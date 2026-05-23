import os
import tempfile
import unittest
from pathlib import Path

os.environ["DATABASE_PATH"] = f"str(Path(tempfile.mkdtemp()) / 'test_hybrid.db')"

from app.services.db import init_db
from app.services import retriever


class HybridRetrieverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_store_adds_embeddings(self):
        retriever.store_chunks("repo-1", [{"file_path": "a.py", "content": "authentication middleware"}])
        found = retriever.search_chunks("repo-1", "authentication")
        self.assertGreaterEqual(len(found), 1)
        self.assertIn("embedding", found[0])
        self.assertGreater(found[0].get("embedding_dim", 0), 0)

    def test_repo_scoped_hybrid_search(self):
        retriever.store_chunks("repo-a", [{"file_path": "auth.py", "content": "login auth token"}])
        retriever.store_chunks("repo-b", [{"file_path": "db.py", "content": "postgres query index"}])

        res_a = retriever.search_chunks("repo-a", "login")
        res_b = retriever.search_chunks("repo-b", "postgres")
        self.assertEqual(res_a[0]["repository_id"], "repo-a")
        self.assertEqual(res_b[0]["repository_id"], "repo-b")


if __name__ == "__main__":
    unittest.main()
