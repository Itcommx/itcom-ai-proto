import json
import os
import time
from collections.abc import Generator

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings

app = FastAPI(title=settings.app_name)


class ChatRequest(BaseModel):
    message: str
    user: str | None = "board-demo"


def build_prompt(message: str) -> str:
    return f"Responde en español, claro y breve.\nPregunta: {message}\n"


def append_log_event(user: str | None, took_ms: int, prompt_chars: int):
    log_event = {
        "ts": int(time.time()),
        "user": user,
        "model": settings.ollama_model,
        "took_ms": took_ms,
        "prompt_chars": prompt_chars,
    }

    os.makedirs(os.path.dirname(settings.log_path), exist_ok=True)
    with open(settings.log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_event, ensure_ascii=False) + "\n")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "model": settings.ollama_model,
        "ollama_url": settings.ollama_url,
        "num_predict": settings.num_predict,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    t0 = time.time()

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message vacío")

    payload = {
        "model": settings.ollama_model,
        "prompt": build_prompt(msg),
        "stream": False,
        "options": {"num_predict": settings.num_predict, "temperature": 0.2},
    }

    last_error = None
    data = None
    for attempt in range(1, settings.ollama_retries + 1):
        try:
            response = requests.post(
                f"{settings.ollama_url}/api/generate",
                json=payload,
                timeout=settings.ollama_timeout,
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt < settings.ollama_retries:
                time.sleep(0.5)

    if data is None:
        raise HTTPException(
            status_code=502,
            detail=f"Error llamando a Ollama tras {settings.ollama_retries} intentos: {last_error}",
        )

    took_ms = int((time.time() - t0) * 1000)
    answer = (data.get("response") or "").strip()
    append_log_event(req.user, took_ms, len(msg))

    return {"answer": answer, "took_ms": took_ms, "model": settings.ollama_model}


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    t0 = time.time()

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message vacío")

    payload = {
        "model": settings.ollama_model,
        "prompt": build_prompt(msg),
        "stream": True,
        "options": {"num_predict": settings.num_predict, "temperature": 0.2},
    }

    def event_stream() -> Generator[str, None, None]:
        accumulated = []
        last_error = None

        for attempt in range(1, settings.ollama_retries + 1):
            try:
                with requests.post(
                    f"{settings.ollama_url}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=settings.ollama_timeout,
                ) as response:
                    response.raise_for_status()
                    for raw_line in response.iter_lines(decode_unicode=True):
                        if not raw_line:
                            continue

                        chunk = json.loads(raw_line)
                        token = chunk.get("response") or ""
                        if token:
                            accumulated.append(token)
                            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

                        if chunk.get("done"):
                            took_ms = int((time.time() - t0) * 1000)
                            append_log_event(req.user, took_ms, len(msg))
                            yield (
                                "data: "
                                + json.dumps(
                                    {
                                        "done": True,
                                        "model": settings.ollama_model,
                                        "took_ms": took_ms,
                                        "answer": "".join(accumulated),
                                    },
                                    ensure_ascii=False,
                                )
                                + "\n\n"
                            )
                            return
                return
            except (requests.RequestException, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < settings.ollama_retries:
                    time.sleep(0.5)

        yield (
            "data: "
            + json.dumps(
                {
                    "error": f"Error llamando a Ollama tras {settings.ollama_retries} intentos: {last_error}",
                },
                ensure_ascii=False,
            )
            + "\n\n"
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
