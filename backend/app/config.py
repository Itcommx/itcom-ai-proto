import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int, *, minimum: int | None = None) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        return max(minimum, value)
    return value


def _get_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    app_name: str
    ollama_url: str
    ollama_model: str
    log_path: str
    num_predict: int
    ollama_timeout: int
    ollama_retries: int
    auth_username: str
    auth_password: str
    auth_secret: str
    auth_token_ttl: int
    auth_users_path: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str
    smtp_use_tls: bool
    smtp_use_ssl: bool
    external_sources_enabled: bool
    external_max_results: int
    external_default_lang: str
    external_default_locale: str
    gdelt_enabled: bool
    youtube_enabled: bool
    searchapi_enabled: bool
    youtube_api_key: str
    searchapi_api_key: str
    firecrawl_api_key: str
    newsapi_key: str

    @property
    def gdelt_available(self) -> bool:
        return self.external_sources_enabled and self.gdelt_enabled

    @property
    def youtube_available(self) -> bool:
        return (
            self.external_sources_enabled
            and self.youtube_enabled
            and bool(self.youtube_api_key)
        )

    @property
    def searchapi_available(self) -> bool:
        return (
            self.external_sources_enabled
            and self.searchapi_enabled
            and bool(self.searchapi_api_key)
        )

    @property
    def firecrawl_available(self) -> bool:
        return self.external_sources_enabled and bool(self.firecrawl_api_key)

    @property
    def newsapi_available(self) -> bool:
        return self.external_sources_enabled and bool(self.newsapi_key)


def build_settings() -> Settings:
    return Settings(
        app_name=_get_str("APP_NAME", "ITCOM AI Prototype"),
        ollama_url=_get_str("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=_get_str("OLLAMA_MODEL", "llama3:latest"),
        log_path=_get_str("LOG_PATH", "/app/logs/requests.jsonl"),
        num_predict=_get_int("NUM_PREDICT", 1024, minimum=1),
        ollama_timeout=_get_int("OLLAMA_TIMEOUT", 120, minimum=1),
        ollama_retries=_get_int("OLLAMA_RETRIES", 2, minimum=1),
        auth_username=_get_str("AUTH_USERNAME"),
        auth_password=_get_str("AUTH_PASSWORD"),
        auth_secret=_get_str("AUTH_SECRET"),
        auth_token_ttl=_get_int("AUTH_TOKEN_TTL", 3600, minimum=1),
        auth_users_path=_get_str("AUTH_USERS_PATH", "/app/logs/users.json"),
        smtp_host=_get_str("SMTP_HOST"),
        smtp_port=_get_int("SMTP_PORT", 587, minimum=1),
        smtp_username=_get_str("SMTP_USERNAME"),
        smtp_password=_get_str("SMTP_PASSWORD"),
        smtp_from_email=_get_str("SMTP_FROM_EMAIL"),
        smtp_from_name=_get_str("SMTP_FROM_NAME", "Symbiotix"),
        smtp_use_tls=_get_bool("SMTP_USE_TLS", True),
        smtp_use_ssl=_get_bool("SMTP_USE_SSL", False),
        external_sources_enabled=_get_bool("EXTERNAL_SOURCES_ENABLED", True),
        external_max_results=_get_int("EXTERNAL_MAX_RESULTS", 20, minimum=1),
        external_default_lang=_get_str("EXTERNAL_DEFAULT_LANG", "es"),
        external_default_locale=_get_str("EXTERNAL_DEFAULT_LOCALE", "mx"),
        gdelt_enabled=_get_bool("GDELT_ENABLED", True),
        youtube_enabled=_get_bool("YOUTUBE_ENABLED", True),
        searchapi_enabled=_get_bool("SEARCHAPI_ENABLED", True),
        youtube_api_key=_get_str("YOUTUBE_API_KEY"),
        searchapi_api_key=_get_str("SEARCHAPI_API_KEY"),
        firecrawl_api_key=_get_str("FIRECRAWL_API_KEY"),
        newsapi_key=_get_str("NEWSAPI_KEY"),
    )


settings = build_settings()
