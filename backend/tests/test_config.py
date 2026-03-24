import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class SettingsConfigTests(unittest.TestCase):
    def test_external_sources_defaults_are_safe(self):
        with patch.dict(
            os.environ,
            {
                "AUTH_USERNAME": "admin",
                "AUTH_PASSWORD": "change_me",
                "AUTH_SECRET": "secret",
            },
            clear=True,
        ):
            config = importlib.import_module("app.config")
            config = importlib.reload(config)
            settings = config.build_settings()

        self.assertTrue(settings.external_sources_enabled)
        self.assertEqual(settings.external_max_results, 20)
        self.assertEqual(settings.external_default_lang, "es")
        self.assertEqual(settings.external_default_locale, "mx")
        self.assertTrue(settings.gdelt_enabled)
        self.assertTrue(settings.gdelt_available)
        self.assertTrue(settings.youtube_enabled)
        self.assertFalse(settings.youtube_available)
        self.assertTrue(settings.searchapi_enabled)
        self.assertFalse(settings.searchapi_available)
        self.assertFalse(settings.firecrawl_available)
        self.assertFalse(settings.newsapi_available)

    def test_external_sources_flags_and_keys_control_availability(self):
        with patch.dict(
            os.environ,
            {
                "AUTH_USERNAME": "admin",
                "AUTH_PASSWORD": "change_me",
                "AUTH_SECRET": "secret",
                "EXTERNAL_SOURCES_ENABLED": "true",
                "EXTERNAL_MAX_RESULTS": "0",
                "EXTERNAL_DEFAULT_LANG": "en",
                "EXTERNAL_DEFAULT_LOCALE": "us",
                "GDELT_ENABLED": "false",
                "YOUTUBE_ENABLED": "true",
                "SEARCHAPI_ENABLED": "true",
                "YOUTUBE_API_KEY": "yt-key",
                "SEARCHAPI_API_KEY": "search-key",
                "FIRECRAWL_API_KEY": "firecrawl-key",
                "NEWSAPI_KEY": "news-key",
            },
            clear=True,
        ):
            config = importlib.import_module("app.config")
            config = importlib.reload(config)
            settings = config.build_settings()

        self.assertEqual(settings.external_max_results, 1)
        self.assertEqual(settings.external_default_lang, "en")
        self.assertEqual(settings.external_default_locale, "us")
        self.assertFalse(settings.gdelt_available)
        self.assertTrue(settings.youtube_available)
        self.assertTrue(settings.searchapi_available)
        self.assertTrue(settings.firecrawl_available)
        self.assertTrue(settings.newsapi_available)


if __name__ == "__main__":
    unittest.main()
