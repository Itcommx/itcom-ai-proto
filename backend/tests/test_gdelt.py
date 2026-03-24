import importlib
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self):
        return self._payload


class GDELTIntegrationTests(unittest.TestCase):
    def test_gdelt_client_normalizes_results(self):
        gdelt = importlib.import_module("app.integrations.gdelt")
        gdelt = importlib.reload(gdelt)
        client = gdelt.GDELTClient(timeout=3)
        recent_date = (datetime.utcnow() + timedelta(hours=2)).strftime("%Y%m%d%H%M%S")

        with patch.object(
            gdelt.requests,
            "get",
            return_value=DummyResponse(
                {
                    "articles": [
                        {
                            "title": "Mexico nearshoring expands",
                            "url": "https://example.com/news/nearshoring",
                            "seendate": recent_date,
                            "snippet": "Industrial investment keeps growing.",
                            "language": "Spanish",
                        }
                    ]
                }
            ),
        ) as mocked_get:
            results = client.search(query="nearshoring mexico", max_results=5, language="es")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["provider"], "gdelt")
        self.assertEqual(results[0]["source_type"], "news")
        self.assertEqual(results[0]["query"], "nearshoring mexico")
        self.assertEqual(results[0]["domain"], "example.com")
        self.assertEqual(results[0]["language"], "spanish")
        mocked_get.assert_called_once()

    def test_gdelt_client_returns_empty_list_on_empty_articles(self):
        gdelt = importlib.import_module("app.integrations.gdelt")
        gdelt = importlib.reload(gdelt)
        client = gdelt.GDELTClient()

        with patch.object(gdelt.requests, "get", return_value=DummyResponse({"articles": []})):
            results = client.search(query="macro", max_results=3, language="es")

        self.assertEqual(results, [])

    def test_gdelt_client_limits_maxrecords_and_sets_timespan(self):
        gdelt = importlib.import_module("app.integrations.gdelt")
        gdelt = importlib.reload(gdelt)
        client = gdelt.GDELTClient()

        with patch.object(gdelt.requests, "get", return_value=DummyResponse({"articles": []})) as mocked_get:
            client.search(query="dame noticias de hoy", max_results=50, language="es")

        params = mocked_get.call_args.kwargs["params"]
        self.assertEqual(params["maxrecords"], 10)
        self.assertEqual(params["timespan"], "24h")

    def test_gdelt_client_filters_old_articles(self):
        gdelt = importlib.import_module("app.integrations.gdelt")
        gdelt = importlib.reload(gdelt)
        client = gdelt.GDELTClient()

        with patch.object(
            gdelt.requests,
            "get",
            return_value=DummyResponse(
                {
                    "articles": [
                        {
                            "title": "Very old",
                            "url": "https://old.example.com/a",
                            "seendate": "20200101000000",
                            "snippet": "Old snippet",
                            "language": "Spanish",
                        },
                        {
                            "title": "Recent",
                            "url": "https://new.example.com/b",
                            "seendate": "20990101000000",
                            "snippet": "Recent snippet",
                            "language": "Spanish",
                        },
                    ]
                }
            ),
        ):
            results = client.search(query="actual economia", max_results=10, language="es")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Recent")

    def test_search_gdelt_rejects_empty_query(self):
        router_module = importlib.import_module("app.routers.external_sources")
        router_module = importlib.reload(router_module)
        payload = router_module.GDELTSearchRequest(query="   ")

        with self.assertRaises(HTTPException) as exc:
            router_module.search_gdelt(payload)

        self.assertEqual(exc.exception.status_code, 400)

    def test_search_gdelt_blocks_when_disabled(self):
        router_module = importlib.import_module("app.routers.external_sources")
        router_module = importlib.reload(router_module)
        payload = router_module.GDELTSearchRequest(query="economia")

        fake_settings = SimpleNamespace(
            external_sources_enabled=False,
            gdelt_enabled=True,
            external_max_results=20,
            external_default_lang="es",
        )
        with patch.object(router_module, "settings", fake_settings):
            with self.assertRaises(HTTPException) as exc:
                router_module.search_gdelt(payload)

        self.assertEqual(exc.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
