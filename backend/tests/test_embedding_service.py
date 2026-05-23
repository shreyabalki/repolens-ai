import os
import unittest
from unittest import mock

from app.services import embedding_service


class EmbeddingServiceTests(unittest.TestCase):
    def setUp(self):
        self.original_provider = os.getenv("EMBEDDING_PROVIDER")
        self.original_model = os.getenv("EMBEDDING_MODEL")

    def tearDown(self):
        if self.original_provider is None:
            os.environ.pop("EMBEDDING_PROVIDER", None)
        else:
            os.environ["EMBEDDING_PROVIDER"] = self.original_provider

        if self.original_model is None:
            os.environ.pop("EMBEDDING_MODEL", None)
        else:
            os.environ["EMBEDDING_MODEL"] = self.original_model

    @mock.patch("app.services.embedding_service._openai_embedding", return_value=[0.1, 0.2, 0.3])
    def test_openai_provider_path(self, mocked_embed):
        os.environ["EMBEDDING_PROVIDER"] = "openai"
        vec = embedding_service.embed_text("authenticate request")
        self.assertEqual(vec, [0.1, 0.2, 0.3])
        mocked_embed.assert_called_once()

    @mock.patch("app.services.embedding_service._openai_embedding", side_effect=RuntimeError("provider error"))
    def test_provider_failure_falls_back_to_hash(self, mocked_embed):
        os.environ["EMBEDDING_PROVIDER"] = "openai"
        vec = embedding_service.embed_text("fallback check")
        self.assertIsInstance(vec, list)
        self.assertGreater(len(vec), 0)
        self.assertTrue(all(isinstance(v, float) for v in vec))
        mocked_embed.assert_called_once()

    def test_empty_text_returns_deterministic_shape(self):
        os.environ["EMBEDDING_PROVIDER"] = "local_hash"
        os.environ["EMBEDDING_DIM"] = "32"
        vec = embedding_service.embed_text("")
        self.assertEqual(len(vec), 32)
        self.assertTrue(all(v == 0.0 for v in vec))


if __name__ == "__main__":
    unittest.main()
