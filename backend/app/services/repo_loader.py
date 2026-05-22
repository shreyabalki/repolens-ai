import os
import tempfile
import subprocess
from pathlib import Path


ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c",
    ".html", ".css", ".md", ".json", ".yml", ".yaml"
}


IGNORE_FOLDERS = {
    ".git", "node_modules", "__pycache__", ".next", "dist", "build", "venv", ".venv"
}


def clone_repository(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    subprocess.run(
        ["git", "clone", repo_url, temp_dir],
        check=True,
        capture_output=True,
        text=True
    )
    return temp_dir


def read_repository_files(repo_path: str):
    files = []

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for filename in filenames:
            file_path = Path(root) / filename

            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                relative_path = str(file_path.relative_to(repo_path))

                files.append({
                    "path": relative_path,
                    "content": content,
                    "language": file_path.suffix.lower()
                })

            except Exception:
                continue

    return files