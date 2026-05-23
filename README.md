# RepoLens AI

AI-powered codebase intelligence platform for repository understanding and semantic search.

## Backend capabilities (current)

- `POST /repositories/upload`: accepts a Git repository URL and starts background ingestion.
- `GET /repositories/{repository_id}`: returns ingestion status and progress.
- `POST /ask`: answers questions scoped to a specific repository id.

## Ingestion lifecycle

1. `queued`
2. `cloning`
3. `reading`
4. `chunking`
5. `indexing`
6. `ready` (or `failed`)

## Local run

```bash
cd backend/app
pip install -r requirements.txt
uvicorn main:app --reload
```

## Example usage

Upload repository:

```bash
curl -X POST http://127.0.0.1:8000/repositories/upload \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/owner/repo.git"}'
```

Check status:

```bash
curl http://127.0.0.1:8000/repositories/<repository_id>
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"repository_id":"<repository_id>","question":"Where is authentication handled?"}'
```

## Notes

- Hybrid retrieval now combines lexical and embedding-based scoring with repository scoping.
- Data is persisted to local JSON files under `backend/app/data/` for MVP persistence.

### Run backend checks

```bash
python -m compileall backend/app
cd backend && python -m unittest tests/test_services.py tests/test_routes.py tests/test_hybrid_retrieval.py tests/test_embedding_service.py
```


CI runs the same compile + test checks via `.github/workflows/backend-tests.yml`.


## Next milestone: Retrieval evaluation

A starter evaluation harness is available under `evaluation/`.

Run it after uploading and indexing a repository:

```bash
python evaluation/run_eval.py --base-url http://127.0.0.1:8000 --repository-id <repository_id> --top-k 5
```


### Embedding provider configuration

Set provider via environment variables:

```bash
export EMBEDDING_PROVIDER=local_hash  # openai | sentence_transformers | local_hash
export EMBEDDING_MODEL=text-embedding-3-small
export OPENAI_API_KEY=your_key_here
```
