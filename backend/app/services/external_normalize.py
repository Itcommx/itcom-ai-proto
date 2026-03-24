from datetime import datetime, timezone
from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    parsed = urlparse((url or "").strip())
    return parsed.netloc.lower()


def parse_published_at(value: str | None) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d%H%M%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            parsed = datetime.strptime(raw, fmt)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def normalize_external_result(
    *,
    provider: str,
    source_type: str,
    query: str,
    title: str,
    url: str,
    published_at: str | None,
    snippet: str,
    language: str,
    raw_json: dict,
) -> dict[str, object]:
    return {
        "provider": provider,
        "source_type": source_type,
        "query": query,
        "title": title.strip(),
        "url": url.strip(),
        "domain": extract_domain(url),
        "published_at": published_at,
        "snippet": snippet.strip(),
        "language": language.strip().lower(),
        "raw_json": raw_json,
    }
