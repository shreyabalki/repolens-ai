from fastapi import APIRouter, HTTPException
from app.models.schemas import AskRequest, AskResponse, SourceCitation
from app.services.retriever import search_chunks
from app.services.llm_service import generate_answer
from app.services.repository_store import get_repository

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    repository = get_repository(request.repository_id)
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repository["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"Repository is not ready. Current status: {repository['status']}")

    chunks = search_chunks(request.repository_id, request.question)
    answer = generate_answer(request.question, chunks)

    seen = set()
    sources = []
    for chunk in chunks:
        key = (chunk["file_path"], chunk.get("start_line", 1), chunk.get("end_line", 1))
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceCitation(
                file_path=chunk["file_path"],
                start_line=chunk.get("start_line", 1),
                end_line=chunk.get("end_line", 1),
            )
        )

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=sources,
    )
