import json
import re
from pathlib import Path
from threading import Lock
from typing import Dict, List

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
        existing.extend(chunks)
        _save_chunks(existing)
    return len(chunks)


def _normalize_tokens(text: str):
    tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def search_chunks(repository_id: str, question: str, top_k: int = 5):
    question_tokens = set(_normalize_tokens(question))
    scored_chunks = []

    with _LOCK:
        chunks = _load_chunks()

    for chunk in chunks:
        if chunk.get("repository_id") != repository_id:
            continue

        content_tokens = set(_normalize_tokens(chunk.get("content", "")))
        file_tokens = set(_normalize_tokens(chunk.get("file_path", "")))

        content_score = len(question_tokens & content_tokens)
        path_score = len(question_tokens & file_tokens) * 2
        score = content_score + path_score

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]
