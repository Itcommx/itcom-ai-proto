import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ITCOM AI Prototype")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:latest")
    log_path: str = os.getenv("LOG_PATH", "/app/logs/requests.jsonl")
    num_predict: int = int(os.getenv("NUM_PREDICT", "80"))
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    ollama_retries: int = int(os.getenv("OLLAMA_RETRIES", "2"))


settings = Settings()
