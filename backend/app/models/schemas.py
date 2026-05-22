from pydantic import BaseModel
from typing import List, Optional


class SourceCitation(BaseModel):
    file_path: str
    start_line: int
    end_line: int


class AskRequest(BaseModel):
    question: str
    repository_id: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation] = []


class RepoUploadRequest(BaseModel):
    repo_url: str


class RepoUploadResponse(BaseModel):
    message: str
    repo_url: str
    repository_id: str
    status: str


class RepositoryStatusResponse(BaseModel):
    repository_id: str
    repo_url: str
    status: str
    progress: int
    files_found: int
    chunks_indexed: int
    error_message: Optional[str] = None
