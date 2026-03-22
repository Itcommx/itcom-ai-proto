import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.integrations.gdelt import GDELTClient, GDELTRequestError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/external", tags=["external-sources"])


class GDELTSearchRequest(BaseModel):
    query: str
    max_results: int | None = None
    language: str | None = None
    start_datetime: str | None = None
    end_datetime: str | None = None


def search_gdelt(payload: GDELTSearchRequest, client: GDELTClient | None = None) -> dict[str, object]:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query es requerida")
    if not settings.external_sources_enabled:
        raise HTTPException(status_code=503, detail="Las fuentes externas están deshabilitadas")
    if not settings.gdelt_enabled:
        raise HTTPException(status_code=503, detail="GDELT está deshabilitado")

    effective_max_results = payload.max_results or settings.external_max_results
    effective_max_results = max(1, min(effective_max_results, settings.external_max_results))
    effective_language = (payload.language or settings.external_default_lang).strip().lower()
    gdelt_client = client or GDELTClient()

    try:
        results = gdelt_client.search(
            query=query,
            max_results=effective_max_results,
            language=effective_language,
            start_datetime=payload.start_datetime,
            end_datetime=payload.end_datetime,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GDELTRequestError as exc:
        logger.warning("gdelt_search_failed query=%s error=%s", query, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    logger.info("gdelt_search_ok query=%s results=%s", query, len(results))
    return {
        "provider": "gdelt",
        "query": query,
        "count": len(results),
        "results": results,
    }


@router.post("/search/gdelt")
def search_gdelt_endpoint(payload: GDELTSearchRequest):
    return search_gdelt(payload)
