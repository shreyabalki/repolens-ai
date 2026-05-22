from app.services.chunker import chunk_repository_files
from app.services.repo_loader import clone_repository, read_repository_files
from app.services.repository_store import update_repository
from app.services.retriever import store_chunks


def ingest_repository(repository_id: str, repo_url: str):
    try:
        update_repository(repository_id, status="cloning", progress=10)
        repo_path = clone_repository(repo_url)

        update_repository(repository_id, status="reading", progress=35)
        files = read_repository_files(repo_path)

        update_repository(repository_id, status="chunking", progress=60, files_found=len(files))
        chunks = chunk_repository_files(files)

        update_repository(repository_id, status="indexing", progress=85)
        indexed = store_chunks(repository_id, chunks)

        update_repository(
            repository_id,
            status="ready",
            progress=100,
            files_found=len(files),
            chunks_indexed=indexed,
            error_message=None,
        )
    except Exception as exc:
        update_repository(repository_id, status="failed", error_message=str(exc))
