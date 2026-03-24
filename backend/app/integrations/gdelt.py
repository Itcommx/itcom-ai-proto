from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging

import requests

from app.services.external_normalize import normalize_external_result, parse_published_at


GDELT_DOC_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
logger = logging.getLogger(__name__)


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
        timespan_hours: int | None = None,
        start_datetime: str | None = None,
        end_datetime: str | None = None,
    ) -> list[dict[str, object]]:
        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("query es requerida")
        effective_max_results = max(1, min(max_results, 10))
        effective_timespan_hours = timespan_hours or self.default_timespan_hours(clean_query)
        effective_timespan_hours = max(1, effective_timespan_hours)

        params = {
            "query": self._build_query(clean_query, language),
            "mode": "ArtList",
            "format": "json",
            "sort": "DateDesc",
            "maxrecords": effective_max_results,
            "timespan": f"{effective_timespan_hours}h",
        }
        if start_datetime:
            params["startdatetime"] = start_datetime
        if end_datetime:
            params["enddatetime"] = end_datetime

        try:
            logger.info("gdelt_request_params=%s", {k: v for k, v in params.items() if k != "query"} | {"query": clean_query})
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
        pre_filter_count = len(articles)

        normalized_results: list[dict[str, object]] = []
        published_dates: list[datetime] = []
        fallback_language = (language or "").strip().lower()
        cutoff = datetime.now(timezone.utc) - timedelta(hours=effective_timespan_hours)
        for article in articles:
            if not isinstance(article, dict):
                continue
            url = str(article.get("url") or article.get("sourceurl") or "").strip()
            title = str(article.get("title") or "").strip()
            if not url and not title:
                continue

            published_at = str(article.get("seendate") or article.get("date") or "") or None
            parsed_published_at = parse_published_at(published_at)
            if parsed_published_at and parsed_published_at < cutoff:
                continue
            if parsed_published_at:
                published_dates.append(parsed_published_at)

            normalized_results.append(
                normalize_external_result(
                    provider="gdelt",
                    source_type="news",
                    query=clean_query,
                    title=title,
                    url=url,
                    published_at=published_at,
                    snippet=str(article.get("snippet") or article.get("socialimage") or ""),
                    language=str(article.get("language") or fallback_language or "unknown"),
                    raw_json=article,
                )
            )
        normalized_results.sort(
            key=lambda item: parse_published_at(str(item.get("published_at") or "")) or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        top_5_dates = [dt.isoformat() for dt in sorted(published_dates, reverse=True)[:5]]
        logger.info(
            "gdelt_filter_stats query=%s before=%s after=%s top5_dates=%s",
            clean_query,
            pre_filter_count,
            len(normalized_results),
            top_5_dates,
        )
        return normalized_results

    @staticmethod
    def _build_query(query: str, language: str | None) -> str:
        if not language:
            return query
        return f"{query} sourceLang:{language.strip().lower()}"

    @staticmethod
    def default_timespan_hours(query: str) -> int:
        lowered = (query or "").lower()
        if "hoy" in lowered:
            return 24
        if "actual" in lowered:
            return 72
        return 72
