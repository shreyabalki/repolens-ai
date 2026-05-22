from pydantic import BaseModel
from typing import List, Optional


class AskRequest(BaseModel):
    question: str
    repo_id: Optional[str] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str] = []


class RepoUploadRequest(BaseModel):
    repo_url: str


class RepoUploadResponse(BaseModel):
    message: str
    repo_url: str
    files_found: int