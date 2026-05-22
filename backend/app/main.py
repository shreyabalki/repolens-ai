from fastapi import FastAPI
from routes.ask import router as ask_router
from routes.repo import router as repo_router

app = FastAPI(
    title="RepoLens AI",
    description="AI-powered codebase intelligence platform",
    version="0.1.0"
)

app.include_router(repo_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {
        "message": "RepoLens AI backend is running",
        "docs": "/docs"
    }