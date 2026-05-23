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
            vector[idx] += (digest[idx % len(digest)] / 255.0)

    length = math.sqrt(sum(v * v for v in vector))
    if length == 0:
        return vector
    return [v / length for v in vector]


def embed_text(text: str) -> List[float]:
    # Placeholder local embedding for MVP; replace with provider-backed embeddings via env config.
    dim = int(os.getenv("EMBEDDING_DIM", "64"))
    return _hash_embedding(text, dim=dim)


def embed_texts(texts: List[str]) -> List[List[float]]:
    return [embed_text(text) for text in texts]
