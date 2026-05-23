import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = f"str(Path(tempfile.mkdtemp()) / 'test_routes.db')"

from app.main import app
from app.services import ingestion_service
from app.services.db import init_db


class RouteTests(unittest.TestCase):
    def setUp(self):
        init_db()
        self.original_clone = ingestion_service.clone_repository
        self.original_read = ingestion_service.read_repository_files

        ingestion_service.clone_repository = lambda repo_url: "/tmp/mock_repo"
        ingestion_service.read_repository_files = lambda repo_path: [
            {"path": "auth.py", "language": ".py", "content": "def authenticate(user):\n    return True\n"}
        ]

        self.client = TestClient(app)

    def tearDown(self):
        ingestion_service.clone_repository = self.original_clone
        ingestion_service.read_repository_files = self.original_read

    def test_upload_and_status_flow(self):
        response = self.client.post("/repositories/upload", json={"repo_url": "https://github.com/example/repo.git"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("repository_id", payload)

        status_response = self.client.get(f"/repositories/{payload['repository_id']}")
        self.assertEqual(status_response.status_code, 200)
        status_payload = status_response.json()
        self.assertEqual(status_payload["status"], "ready")
        self.assertGreaterEqual(status_payload["chunks_indexed"], 1)

    def test_upload_invalid_url(self):
        response = self.client.post("/repositories/upload", json={"repo_url": "not-a-url"})
        self.assertEqual(response.status_code, 422)

    def test_ask_not_found_repository(self):
        response = self.client.post("/ask", json={"repository_id": "missing", "question": "where is auth"})
        self.assertEqual(response.status_code, 404)

    def test_ask_happy_path(self):
        upload = self.client.post("/repositories/upload", json={"repo_url": "https://github.com/example/repo.git"}).json()
        repo_id = upload["repository_id"]

        response = self.client.post("/ask", json={"repository_id": repo_id, "question": "authenticate"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["question"], "authenticate")
        self.assertGreaterEqual(len(payload["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
