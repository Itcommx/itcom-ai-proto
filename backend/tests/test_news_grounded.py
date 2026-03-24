import importlib
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class NewsGroundedTests(unittest.TestCase):
    def setUp(self):
        os.environ["AUTH_USERNAME"] = "admin"
        os.environ["AUTH_PASSWORD"] = "change_me"
        os.environ["AUTH_SECRET"] = "secret"

    def test_prompt_contains_grounding_instructions(self):
        main = importlib.import_module("app.main")
        main = importlib.reload(main)
        prompt = main.build_news_grounded_prompt(
            "dame noticias de hoy",
            [
                {
                    "title": "Demo title",
                    "published_at": "20250315000000",
                    "domain": "example.com",
                    "snippet": "Snippet",
                    "url": "https://example.com/news",
                }
            ],
        )
        self.assertIn("Responde únicamente con la información de los artículos proporcionados.", prompt)
        self.assertIn("No inventes noticias.", prompt)
        self.assertIn("No uses conocimiento previo.", prompt)
        self.assertIn("Incluye fecha y fuente por cada nota.", prompt)

    def test_fetch_recent_news_articles_blocked_when_external_disabled(self):
        main = importlib.import_module("app.main")
        main = importlib.reload(main)
        fake_settings = SimpleNamespace(
            external_sources_enabled=False,
            gdelt_enabled=True,
            external_max_results=10,
            external_default_lang="es",
            ollama_timeout=5,
        )
        with patch.object(main, "settings", fake_settings):
            with self.assertRaises(HTTPException) as exc:
                main.fetch_recent_news_articles("dame noticias de hoy")
        self.assertEqual(exc.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
