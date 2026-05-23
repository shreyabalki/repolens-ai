import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes.ask import router as ask_router
from app.routes.repo import router as repo_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("repolens")

app = FastAPI(
    title="RepoLens AI",
    description="AI-powered codebase intelligence platform",
    version="0.2.0"
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s latency_ms=%s", request_id, request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"error": "internal_server_error", "message": "An unexpected server error occurred."})


app.include_router(repo_router)
app.include_router(ask_router)


@app.get("/")
def root():
    return {
        "message": "RepoLens AI backend is running",
        "docs": "/docs"
    }
