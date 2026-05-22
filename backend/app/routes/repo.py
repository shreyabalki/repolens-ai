from fastapi import APIRouter
from models.schemas import RepoUploadRequest, RepoUploadResponse
from services.repo_loader import clone_repository, read_repository_files
from services.chunker import chunk_repository_files
from services.retriever import store_chunks

router = APIRouter()


@router.post("/repositories/upload", response_model=RepoUploadResponse)
def upload_repository(request: RepoUploadRequest):
    repo_path = clone_repository(request.repo_url)

    files = read_repository_files(repo_path)
    chunks = chunk_repository_files(files)
    store_chunks(chunks)

    return RepoUploadResponse(
        message="Repository uploaded and indexed successfully",
        repo_url=request.repo_url,
        files_found=len(files)
    )