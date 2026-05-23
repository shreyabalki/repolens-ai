from fastapi import APIRouter, BackgroundTasks, HTTPException
i from pydantic import HttpUrl, ValidationError, TypeAdapter

from app.models.schemas import RepoUploadRequest, RepoUploadResponse, RepositoryStatusResponse
from app.services.ingestion_service import ingest_repository
from app.services.repository_store import create_repository, get_repository

router = APIRouter()


@router.post("/repositories/upload", response_model=RepoUploadResponse)
def upload_repository(request: RepoUploadRequest, background_tasks: BackgroundTasks):
i have mergf    try:
        TypeAdapter(HttpUrl).validate_python(request.repo_url)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Invalid repository URL") from exc

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
