import tempfile
import unittest
from pathlib import Path

from app.services import chunker, repository_store, retriever


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        data_path = Path(self.temp_dir.name)

        repository_store.DATA_DIR = data_path
        repository_store.REPOS_FILE = data_path / "repositories.json"

        retriever.DATA_DIR = data_path
        retriever.CHUNKS_FILE = data_path / "chunks.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_repository_create_and_get(self):
        created = repository_store.create_repository("https://github.com/example/repo.git")
        found = repository_store.get_repository(created["repository_id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["repo_url"], "https://github.com/example/repo.git")
        self.assertEqual(found["status"], "queued")

    def test_retriever_store_and_scope(self):
        retriever.store_chunks("repo-a", [{"file_path": "a.py", "content": "auth token"}])
        retriever.store_chunks("repo-b", [{"file_path": "b.py", "content": "database session"}])

        a_results = retriever.search_chunks("repo-a", "auth")
        b_results = retriever.search_chunks("repo-b", "database")

        self.assertEqual(len(a_results), 1)
        self.assertEqual(a_results[0]["repository_id"], "repo-a")
        self.assertEqual(len(b_results), 1)
        self.assertEqual(b_results[0]["repository_id"], "repo-b")

    def test_chunker_line_ranges(self):
        files = [{"path": "main.py", "language": ".py", "content": "line1\nline2\nline3\n"}]
        chunks = chunker.chunk_repository_files(files)

        self.assertGreaterEqual(len(chunks), 1)
        self.assertIn("start_line", chunks[0])
        self.assertIn("end_line", chunks[0])
        self.assertGreaterEqual(chunks[0]["start_line"], 1)


if __name__ == "__main__":
    unittest.main()
