import json
import os
import time
from collections.abc import Generator

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "ITCOM AI Prototype")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
LOG_PATH = os.getenv("LOG_PATH", "/app/logs/requests.jsonl")
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "1024"))
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_RETRIES = int(os.getenv("OLLAMA_RETRIES", "2"))

app = FastAPI(title=APP_NAME)


class ChatRequest(BaseModel):
    message: str
    user: str | None = "board-demo"


def build_prompt(message: str) -> str:
    return f"Responde en español, claro y breve.\nPregunta: {message}\n"


def is_truncated(done_reason: str | None) -> bool:
    return (done_reason or "").lower() in {"length", "max_tokens"}


def now_ts() -> int:
    return int(time.time())


def append_log_event(event: dict):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    event_with_ts = {"timestamp": now_ts(), **event}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_with_ts, ensure_ascii=False) + "\n")


def log_chat_event(
    endpoint: str,
    user: str | None,
    prompt_chars: int,
    took_ms: int,
    answer_length: int,
    truncated: bool,
    done_reason: str | None,
    error: str | None = None,
):
    append_log_event(
        {
            "endpoint": endpoint,
            "user": user,
            "model": OLLAMA_MODEL,
            "prompt_chars": prompt_chars,
            "took_ms": took_ms,
            "answer_length": answer_length,
            "truncated": truncated,
            "done_reason": done_reason,
            "error": error,
        }
    )


def ollama_error_message(last_error: Exception | None) -> str:
    return f"Error llamando a Ollama tras {OLLAMA_RETRIES} intentos: {last_error}"


def build_generate_payload(message: str, stream: bool) -> dict:
    return {
        "model": OLLAMA_MODEL,
        "prompt": build_prompt(message),
        "stream": stream,
        "options": {"num_predict": NUM_PREDICT, "temperature": 0.2},
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "app_name": APP_NAME,
        "model": OLLAMA_MODEL,
        "num_predict": NUM_PREDICT,
        "ollama_timeout": OLLAMA_TIMEOUT,
        "ollama_retries": OLLAMA_RETRIES,
        "log_path": LOG_PATH,
        "timestamp": now_ts(),
    }


@app.post("/chat")
def chat(req: ChatRequest):
    t0 = time.time()

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message vacío")

    payload = build_generate_payload(msg, stream=False)

    last_error = None
    data = None
    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            break
        except (requests.RequestException, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < OLLAMA_RETRIES:
                time.sleep(0.5)

    if data is None:
        took_ms = int((time.time() - t0) * 1000)
        error_msg = ollama_error_message(last_error)
        log_chat_event(
            endpoint="/chat",
            user=req.user,
            prompt_chars=len(msg),
            took_ms=took_ms,
            answer_length=0,
            truncated=False,
            done_reason=None,
            error=error_msg,
        )
        raise HTTPException(status_code=502, detail=error_msg)

    took_ms = int((time.time() - t0) * 1000)
    answer = data.get("response") or ""
    done_reason = data.get("done_reason")
    truncated = is_truncated(done_reason)

    log_chat_event(
        endpoint="/chat",
        user=req.user,
        prompt_chars=len(msg),
        took_ms=took_ms,
        answer_length=len(answer),
        truncated=truncated,
        done_reason=done_reason,
        error=None,
    )

    return {
        "answer": answer,
        "took_ms": took_ms,
        "model": OLLAMA_MODEL,
        "truncated": truncated,
        "done_reason": done_reason,
    }


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    t0 = time.time()

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message vacío")

    payload = build_generate_payload(msg, stream=True)

    def event_stream() -> Generator[str, None, None]:
        accumulated = []
        done_reason = None
        last_error = None

        for attempt in range(1, OLLAMA_RETRIES + 1):
            try:
                with requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json=payload,
                    stream=True,
                    timeout=OLLAMA_TIMEOUT,
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
                            done_reason = chunk.get("done_reason")
                            answer = "".join(accumulated)
                            took_ms = int((time.time() - t0) * 1000)
                            truncated = is_truncated(done_reason)
                            log_chat_event(
                                endpoint="/chat/stream",
                                user=req.user,
                                prompt_chars=len(msg),
                                took_ms=took_ms,
                                answer_length=len(answer),
                                truncated=truncated,
                                done_reason=done_reason,
                                error=None,
                            )
                            yield (
                                "data: "
                                + json.dumps(
                                    {
                                        "done": True,
                                        "model": OLLAMA_MODEL,
                                        "took_ms": took_ms,
                                        "answer": answer,
                                        "truncated": truncated,
                                        "done_reason": done_reason,
                                    },
                                    ensure_ascii=False,
                                )
                                + "\n\n"
                            )
                            return
                return
            except (requests.RequestException, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < OLLAMA_RETRIES:
                    time.sleep(0.5)

        took_ms = int((time.time() - t0) * 1000)
        error_msg = ollama_error_message(last_error)
        log_chat_event(
            endpoint="/chat/stream",
            user=req.user,
            prompt_chars=len(msg),
            took_ms=took_ms,
            answer_length=len("".join(accumulated)),
            truncated=False,
            done_reason=done_reason,
            error=error_msg,
        )
        yield (
            "data: "
            + json.dumps(
                {
                    "error": error_msg,
                },
                ensure_ascii=False,
            )
            + "\n\n"
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
