from dataclasses import dataclass

import requests

from app.services.external_normalize import normalize_external_result


GDELT_DOC_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTError(Exception):
    """Base error for GDELT integration."""


class GDELTDisabledError(GDELTError):
    """Raised when the provider is disabled in settings."""


class GDELTRequestError(GDELTError):
    """Raised when the upstream request fails."""


@dataclass
class GDELTClient:
    base_url: str = GDELT_DOC_API_URL
    timeout: int = 10

    def search(
        self,
        *,
        query: str,
        max_results: int,
        language: str | None = None,
        start_datetime: str | None = None,
        end_datetime: str | None = None,
    ) -> list[dict[str, object]]:
        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("query es requerida")

        params = {
            "query": self._build_query(clean_query, language),
            "mode": "ArtList",
            "format": "json",
            "sort": "DateDesc",
            "maxrecords": max_results,
        }
        if start_datetime:
            params["startdatetime"] = start_datetime
        if end_datetime:
            params["enddatetime"] = end_datetime

        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise GDELTRequestError("GDELT no respondió a tiempo") from exc
        except (requests.RequestException, ValueError) as exc:
            raise GDELTRequestError("No se pudo consultar GDELT") from exc

        articles = payload.get("articles")
        if not isinstance(articles, list):
            return []

        normalized_results: list[dict[str, object]] = []
        fallback_language = (language or "").strip().lower()
        for article in articles:
            if not isinstance(article, dict):
                continue
            url = str(article.get("url") or article.get("sourceurl") or "").strip()
            title = str(article.get("title") or "").strip()
            if not url and not title:
                continue

            normalized_results.append(
                normalize_external_result(
                    provider="gdelt",
                    source_type="news",
                    query=clean_query,
                    title=title,
                    url=url,
                    published_at=str(article.get("seendate") or article.get("date") or "") or None,
                    snippet=str(article.get("snippet") or article.get("socialimage") or ""),
                    language=str(article.get("language") or fallback_language or "unknown"),
                    raw_json=article,
                )
            )
        return normalized_results

    @staticmethod
    def _build_query(query: str, language: str | None) -> str:
        if not language:
            return query
        return f"{query} sourceLang:{language.strip().lower()}"
