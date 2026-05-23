import hashlib
import math
import os
from typing import List


def _hash_embedding(text: str, dim: int = 64) -> List[float]:
    tokens = text.lower().split()
    vector = [0.0] * dim
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for idx in range(dim):
            vector[idx] += digest[idx % len(digest)] / 255.0

    length = math.sqrt(sum(v * v for v in vector))
    if length == 0:
        return vector
    return [v / length for v in vector]


def _openai_embedding(text: str) -> List[float]:
    from openai import OpenAI

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding


def _sentence_transformers_embedding(text: str) -> List[float]:
    from sentence_transformers import SentenceTransformer

    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    vec = model.encode(text)
    return vec.tolist() if hasattr(vec, "tolist") else list(vec)


def embed_text(text: str) -> List[float]:
    provider = os.getenv("EMBEDDING_PROVIDER", "local_hash").lower()

    try:
        if provider == "openai":
            return _openai_embedding(text)
        if provider in {"sentence_transformers", "st"}:
            return _sentence_transformers_embedding(text)
    except Exception:
        # Fallback to deterministic local embedding for resilience in MVP mode.
        pass

    dim = int(os.getenv("EMBEDDING_DIM", "64"))
    return _hash_embedding(text, dim=dim)


def embed_texts(texts: List[str]) -> List[List[float]]:
    return [embed_text(text) for text in texts]
