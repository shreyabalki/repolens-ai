import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from app.services.db import get_connection


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_dict(row) -> Dict:
    return dict(row)


def create_repository(repo_url: str) -> Dict:
    conn = get_connection()
    repository_id = str(uuid.uuid4())
    now = _now()
    conn.execute(
        """
        INSERT INTO repositories(repository_id, repo_url, status, progress, files_found, chunks_indexed, error_message, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (repository_id, repo_url, "queued", 0, 0, 0, None, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM repositories WHERE repository_id = ?", (repository_id,)).fetchone()
    conn.close()
    return _to_dict(row)


def update_repository(repository_id: str, **updates) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM repositories WHERE repository_id = ?", (repository_id,)).fetchone()
    if not row:
        conn.close()
        return None

    allowed = ["repo_url", "status", "progress", "files_found", "chunks_indexed", "error_message"]
    for key in allowed:
        if key in updates:
            conn.execute(f"UPDATE repositories SET {key} = ? WHERE repository_id = ?", (updates[key], repository_id))
    conn.execute("UPDATE repositories SET updated_at = ? WHERE repository_id = ?", (_now(), repository_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM repositories WHERE repository_id = ?", (repository_id,)).fetchone()
    conn.close()
    return _to_dict(updated)


def get_repository(repository_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM repositories WHERE repository_id = ?", (repository_id,)).fetchone()
    conn.close()
    return _to_dict(row) if row else None
