import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REPOS_FILE = DATA_DIR / "repositories.json"
_LOCK = Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REPOS_FILE.exists():
        REPOS_FILE.write_text("[]", encoding="utf-8")


def _load_repositories():
    _ensure_storage()
    return json.loads(REPOS_FILE.read_text(encoding="utf-8"))


def _save_repositories(repositories):
    _ensure_storage()
    REPOS_FILE.write_text(json.dumps(repositories, ensure_ascii=False), encoding="utf-8")


def create_repository(repo_url: str) -> Dict:
    with _LOCK:
        repositories = _load_repositories()
        record = {
            "repository_id": str(uuid.uuid4()),
            "repo_url": repo_url,
            "status": "queued",
            "progress": 0,
            "files_found": 0,
            "chunks_indexed": 0,
            "error_message": None,
            "created_at": _now(),
            "updated_at": _now(),
        }
        repositories.append(record)
        _save_repositories(repositories)
        return record


def update_repository(repository_id: str, **updates) -> Optional[Dict]:
    with _LOCK:
        repositories = _load_repositories()
        for repo in repositories:
            if repo["repository_id"] == repository_id:
                repo.update(updates)
                repo["updated_at"] = _now()
                _save_repositories(repositories)
                return repo
    return None


def get_repository(repository_id: str) -> Optional[Dict]:
    with _LOCK:
        repositories = _load_repositories()
        for repo in repositories:
            if repo["repository_id"] == repository_id:
                return repo
    return None
