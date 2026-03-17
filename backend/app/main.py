import base64
import hashlib
import hmac
import json
import os
import time
from collections.abc import Generator

import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "ITCOM AI Prototype")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
LOG_PATH = os.getenv("LOG_PATH", "/app/logs/requests.jsonl")
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "1024"))
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_RETRIES = int(os.getenv("OLLAMA_RETRIES", "2"))
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")
AUTH_SECRET = os.getenv("AUTH_SECRET", "")
AUTH_TOKEN_TTL = int(os.getenv("AUTH_TOKEN_TTL", "3600"))

app = FastAPI(title=APP_NAME)


class ChatRequest(BaseModel):
    message: str
    user: str | None = "board-demo"


class LoginRequest(BaseModel):
    username: str
    password: str


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


def sign_payload(payload: str) -> str:
    return hmac.new(AUTH_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def issue_token(username: str) -> str:
    expires_at = now_ts() + AUTH_TOKEN_TTL
    payload = f"{username}:{expires_at}"
    signature = sign_payload(payload)
    raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def parse_token(token: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, expires_at, signature = raw.rsplit(":", 2)
        payload = f"{username}:{expires_at}"
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Token inválido: {exc}")

    expected = sign_payload(payload)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Firma de token inválida")

    if now_ts() > int(expires_at):
        raise HTTPException(status_code=401, detail="Token expirado")

    return username




def validate_auth_config():
    if not AUTH_USERNAME or not AUTH_PASSWORD or not AUTH_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Auth no configurada: define AUTH_USERNAME, AUTH_PASSWORD y AUTH_SECRET",
        )

def get_current_user(authorization: str | None = Header(default=None)) -> str:
    validate_auth_config()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token vacío")
    return parse_token(token)


@app.post("/auth/login")
def login(req: LoginRequest):
    validate_auth_config()
    if req.username != AUTH_USERNAME or req.password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = issue_token(req.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": AUTH_TOKEN_TTL,
        "user": req.username,
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
def chat(req: ChatRequest, user: str = Depends(get_current_user)):
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
            user=user,
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
        user=user,
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
        "user": user,
    }


@app.post("/chat/stream")
def chat_stream(req: ChatRequest, user: str = Depends(get_current_user)):
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
                                user=user,
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
                                        "user": user,
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
            user=user,
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
