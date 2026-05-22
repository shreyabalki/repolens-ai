from fastapi import APIRouter
from models.schemas import AskRequest, AskResponse
from services.retriever import search_chunks
from services.llm_service import generate_answer

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    chunks = search_chunks(request.question)
    answer = generate_answer(request.question, chunks)

    sources = list(set(chunk["file_path"] for chunk in chunks))

    return AskResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )