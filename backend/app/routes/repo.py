from fastapi import APIRouter, BackgroundTasks, HTTPException
from models.schemas import RepoUploadRequest, RepoUploadResponse, RepositoryStatusResponse
from services.ingestion_service import ingest_repository
from services.repository_store import create_repository, get_repository

router = APIRouter()


@router.post("/repositories/upload", response_model=RepoUploadResponse)
def upload_repository(request: RepoUploadRequest, background_tasks: BackgroundTasks):
    repository = create_repository(request.repo_url)
    background_tasks.add_task(
        ingest_repository,
        repository["repository_id"],
        request.repo_url,
    )

    return RepoUploadResponse(
        message="Repository upload accepted for background indexing",
        repo_url=request.repo_url,
        repository_id=repository["repository_id"],
        status=repository["status"],
    )


@router.get("/repositories/{repository_id}", response_model=RepositoryStatusResponse)
def repository_status(repository_id: str):
    repository = get_repository(repository_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryStatusResponse(**repository)
