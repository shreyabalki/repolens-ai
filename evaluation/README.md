# Evaluation Harness (Phase 2 starter)

This folder contains a lightweight, reproducible evaluation scaffold for RepoLens retrieval quality.

## Goals

Track improvements as retrieval evolves from keyword-only to hybrid retrieval (BM25 + vectors + reranker).

Primary metrics:
- Recall@K
- Precision@K
- MRR
- Average response latency (ms)

## Files

- `golden_queries.json`: benchmark question set with expected relevant files.
- `run_eval.py`: computes retrieval metrics against `/ask` and `/repositories/{id}` workflows.

## Usage

1. Start backend:

```bash
cd backend/app
uvicorn main:app --reload
```

2. Upload a repository and wait until status is `ready`.

3. Run evaluation:

```bash
python evaluation/run_eval.py --base-url http://127.0.0.1:8000 --repository-id <repository_id> --top-k 5
```

## Notes

- This scaffold evaluates retrieval quality from `sources` returned by `/ask`.
- As the system matures, add hallucination scoring and answer-grounding checks.
