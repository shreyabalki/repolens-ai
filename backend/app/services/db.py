import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "data" / "repolens.db"
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH))

Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS repositories (
            repository_id TEXT PRIMARY KEY,
            repo_url TEXT NOT NULL,
            status TEXT NOT NULL,
            progress INTEGER NOT NULL,
            files_found INTEGER NOT NULL,
            chunks_indexed INTEGER NOT NULL,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            language TEXT,
            chunk_index INTEGER,
            start_line INTEGER,
            end_line INTEGER,
            content TEXT NOT NULL,
            embedding_json TEXT,
            embedding_dim INTEGER,
            embedding_model TEXT
        )
        """
    )
    conn.commit()
    conn.close()
