import json
import math
import os
import re
from pathlib import Path
from threading import Lock
from typing import Dict, List

from app.services.embedding_service import embed_text

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHUNKS_FILE = DATA_DIR / "chunks.json"
_LOCK = Lock()

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "in", "on", "for", "of", "with", "is", "are", "be", "this", "that"
}


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CHUNKS_FILE.exists():
        CHUNKS_FILE.write_text("[]", encoding="utf-8")


def _load_chunks() -> List[Dict]:
    _ensure_storage()
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def _save_chunks(chunks: List[Dict]):
    _ensure_storage()
    CHUNKS_FILE.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")


def store_chunks(repository_id: str, chunks: List[Dict]):
    with _LOCK:
        existing = _load_chunks()
        existing = [c for c in existing if c.get("repository_id") != repository_id]
        for chunk in chunks:
            chunk["repository_id"] = repository_id
            chunk["embedding"] = embed_text(chunk.get("content", ""))
            chunk["embedding_dim"] = len(chunk["embedding"])
            chunk["embedding_model"] = os.getenv("EMBEDDING_MODEL", "hash-v1")
        existing.extend(chunks)
        _save_chunks(existing)
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
    rows = []

    with _LOCK:
        chunks = _load_chunks()

    for chunk in chunks:
        if chunk.get("repository_id") != repository_id:
            continue

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
