import json
import math
import os
import re
from typing import Dict, List

from app.services.db import get_connection
from app.services.embedding_service import embed_text

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "in", "on", "for", "of", "with", "is", "are", "be", "this", "that"
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "in", "on", "for", "of", "with", "is", "are", "be", "this", "that"
}

def store_chunks(repository_id: str, chunks: List[Dict]):
    conn = get_connection()
    conn.execute("DELETE FROM chunks WHERE repository_id = ?", (repository_id,))
    for chunk in chunks:
        embedding = embed_text(chunk.get("content", ""))
        conn.execute(
            """
            INSERT INTO chunks(repository_id, file_path, language, chunk_index, start_line, end_line, content, embedding_json, embedding_dim, embedding_model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                repository_id,
                chunk.get("file_path", ""),
                chunk.get("language"),
                chunk.get("chunk_index"),
                chunk.get("start_line"),
                chunk.get("end_line"),
                chunk.get("content", ""),
                json.dumps(embedding),
                len(embedding),
                os.getenv("EMBEDDING_MODEL", "hash-v1"),
            ),
        )
    conn.commit()
    conn.close()
    return len(chunks)


def _normalize_tokens(text: str):
    tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _min_max_normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    low, high = min(values), max(values)
    if low == high:
        return [1.0 if v > 0 else 0.0 for v in values]
    return [(v - low) / (high - low) for v in values]


def search_chunks(repository_id: str, question: str, top_k: int = 5):
    question_tokens = set(_normalize_tokens(question))
    question_embedding = embed_text(question)
    alpha = float(os.getenv("HYBRID_ALPHA", "0.5"))
    alpha = max(0.0, min(alpha, 1.0))

    conn = get_connection()
    rows_db = conn.execute("SELECT * FROM chunks WHERE repository_id = ?", (repository_id,)).fetchall()
    conn.close()

    rows = []
    for row in rows_db:
        chunk = {
            "repository_id": row["repository_id"],
            "file_path": row["file_path"],
            "language": row["language"],
            "chunk_index": row["chunk_index"],
            "start_line": row["start_line"],
            "end_line": row["end_line"],
            "content": row["content"],
            "embedding": json.loads(row["embedding_json"]) if row["embedding_json"] else [],
            "embedding_dim": row["embedding_dim"],
            "embedding_model": row["embedding_model"],
        }
        content_tokens = set(_normalize_tokens(chunk.get("content", "")))
        file_tokens = set(_normalize_tokens(chunk.get("file_path", "")))
        lexical = len(question_tokens & content_tokens) + (len(question_tokens & file_tokens) * 2)
        vector = _cosine_similarity(question_embedding, chunk.get("embedding", []))
        rows.append({"chunk": chunk, "lexical": float(lexical), "vector": float(vector)})

    if not rows:
        return []

    lexical_norm = _min_max_normalize([r["lexical"] for r in rows])
    vector_norm = _min_max_normalize([r["vector"] for r in rows])

    scored = []
    for idx, row in enumerate(rows):
        score = alpha * lexical_norm[idx] + (1.0 - alpha) * vector_norm[idx]
        if score > 0:
            scored.append((score, row["chunk"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k]]
