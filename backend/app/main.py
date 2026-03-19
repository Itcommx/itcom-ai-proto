import base64
import hashlib
import hmac
import json
import os
import secrets
import smtplib
import time
from collections.abc import Generator
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


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


def build_settings() -> Settings:
    env = os.environ
    return Settings(
        app_name=env.get("APP_NAME", "ITCOM AI Prototype"),
        ollama_url=env.get("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=env.get("OLLAMA_MODEL", "llama3:latest"),
        log_path=env.get("LOG_PATH", "/app/logs/requests.jsonl"),
        num_predict=int(env.get("NUM_PREDICT", "1024")),
        ollama_timeout=int(env.get("OLLAMA_TIMEOUT", "120")),
        ollama_retries=int(env.get("OLLAMA_RETRIES", "2")),
        auth_username=env.get("AUTH_USERNAME", ""),
        auth_password=env.get("AUTH_PASSWORD", ""),
        auth_secret=env.get("AUTH_SECRET", ""),
        auth_token_ttl=int(env.get("AUTH_TOKEN_TTL", "3600")),
        auth_users_path=env.get("AUTH_USERS_PATH", "/app/logs/users.json"),
        smtp_host=env.get("SMTP_HOST", ""),
        smtp_port=int(env.get("SMTP_PORT", "587")),
        smtp_username=env.get("SMTP_USERNAME", ""),
        smtp_password=env.get("SMTP_PASSWORD", ""),
        smtp_from_email=env.get("SMTP_FROM_EMAIL", ""),
        smtp_from_name=env.get("SMTP_FROM_NAME", "Symbiotix"),
        smtp_use_tls=env.get("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes", "on"},
        smtp_use_ssl=env.get("SMTP_USE_SSL", "false").strip().lower() in {"1", "true", "yes", "on"},


settings = build_settings()
app = FastAPI(title=settings.app_name)


class ChatRequest(BaseModel):
    message: str
    user: str | None = "board-demo"


class LoginRequest(BaseModel):
    username: str
    password: str
    verification_code: str | None = None


class SignupRequest(BaseModel):
    username: str
    password: str
    email: str


class ResendVerificationRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


VERIFICATION_CODE_TTL_SECONDS = 600
VERIFICATION_RESEND_COOLDOWN_SECONDS = 60


def build_prompt(message: str) -> str:
    return f"Responde en español, claro y breve.\nPregunta: {message}\n"


def is_truncated(done_reason: str | None) -> bool:
    return (done_reason or "").lower() in {"length", "max_tokens"}


def now_ts() -> int:
    return int(time.time())


def append_log_event(event: dict):
    os.makedirs(os.path.dirname(settings.log_path), exist_ok=True)
    event_with_ts = {"timestamp": now_ts(), **event}
    with open(settings.log_path, "a", encoding="utf-8") as f:
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
            "model": settings.ollama_model,
            "prompt_chars": prompt_chars,
            "took_ms": took_ms,
            "answer_length": answer_length,
            "truncated": truncated,
            "done_reason": done_reason,
            "error": error,
        }
    )


def ollama_error_message(last_error: Exception | None) -> str:
    return f"Error llamando a Ollama tras {settings.ollama_retries} intentos: {last_error}"


def build_generate_payload(message: str, stream: bool) -> dict:
    return {
        "model": settings.ollama_model,
        "prompt": build_prompt(message),
        "stream": stream,
        "options": {"num_predict": settings.num_predict, "temperature": 0.2},
    }


def sign_payload(payload: str) -> str:
    return hmac.new(
        settings.auth_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def issue_token(username: str) -> str:
    expires_at = now_ts() + settings.auth_token_ttl
    payload = f"{username}:{expires_at}"
    signature = sign_payload(payload)
    raw = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def parse_token(token: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, expires_at, signature = raw.rsplit(":", 2)
        payload = f"{username}:{expires_at}"
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=f"Token inválido: {exc}")

    expected = sign_payload(payload)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Firma de token inválida")

    if now_ts() > int(expires_at):
        raise HTTPException(status_code=401, detail="Token expirado")

    return username


def validate_auth_config():
    if (
        not settings.auth_username
        or not settings.auth_password
        or not settings.auth_secret
    ):
        raise HTTPException(
            status_code=503,
            detail="Auth no configurada: define AUTH_USERNAME, AUTH_PASSWORD y AUTH_SECRET",
        )


def hash_password(username: str, password: str) -> str:
    salted = f"{username}:{password}:{settings.auth_secret}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def hash_verification_code(username: str, code: str) -> str:
    salted = f"{username}:{code}:{settings.auth_secret}:verification"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def users_path() -> Path:
    return Path(settings.auth_users_path)


def normalize_user_record(username: str, raw: object) -> dict[str, object] | None:
    if isinstance(raw, str):
        return {
            "password_hash": raw,
            "email": username if "@" in username else "",
            "verified": True,
            "verification_code_hash": None,
            "verification_expires_at": None,
            "verification_last_sent_at": None,
            "created_at": now_ts(),
            "verified_at": now_ts(),
        }

    if not isinstance(raw, dict):
        return None

    password_hash = str(raw.get("password_hash") or raw.get("password") or "").strip()
    if not password_hash:
        return None

    return {
        "password_hash": password_hash,
        "email": str(raw.get("email") or "").strip().lower(),
        "verified": bool(raw.get("verified", False)),
        "verification_code_hash": raw.get("verification_code_hash"),
        "verification_expires_at": raw.get("verification_expires_at"),
        "verification_last_sent_at": raw.get("verification_last_sent_at"),
        "created_at": int(raw.get("created_at") or now_ts()),
        "verified_at": raw.get("verified_at"),
    }


def load_users() -> dict[str, dict[str, object]]:
    path = users_path()
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    users: dict[str, dict[str, object]] = {}
    for key, value in data.items():
        username = str(key)
        record = normalize_user_record(username, value)
        if record:
            users[username] = record
    return users


def save_users(users: dict[str, dict[str, object]]):
    path = users_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def validate_email(email: str) -> str:
    clean = require_non_empty(email, "email").lower()
    if "@" not in clean or "." not in clean.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=400, detail="email inválido")
    return clean


def make_user_record(username: str, password: str, email: str, *, verified: bool) -> dict[str, object]:
    now = now_ts()
    return {
        "password_hash": hash_password(username, password),
        "email": email,
        "verified": verified,
        "verification_code_hash": None,
        "verification_expires_at": None,
        "verification_last_sent_at": None,
        "created_at": now,
        "verified_at": now if verified else None,
    }


def ensure_default_user():
    users = load_users()
    if settings.auth_username and settings.auth_username not in users:
        users[settings.auth_username] = make_user_record(
            settings.auth_username,
            settings.auth_password,
            settings.auth_username if "@" in settings.auth_username else "",
            verified=True,
        )
        save_users(users)


def get_user_record(username: str) -> dict[str, object] | None:
    return load_users().get(username)


def verify_user_password(username: str, password: str) -> bool:
    record = get_user_record(username)
    if not record:
        return False
    stored = str(record.get("password_hash") or "")
    return hmac.compare_digest(stored, hash_password(username, password))


def validate_smtp_config():
    required = {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_PORT": settings.smtp_port,
        "SMTP_USERNAME": settings.smtp_username,
        "SMTP_PASSWORD": settings.smtp_password,
        "SMTP_FROM_EMAIL": settings.smtp_from_email,
        "SMTP_FROM_NAME": settings.smtp_from_name,
    }
    missing = [key for key, value in required.items() if value in {"", 0, None}]
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"SMTP no configurado: define {', '.join(missing)}",
        )


def generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def apply_new_verification_code(username: str, record: dict[str, object]) -> str:
    code = generate_verification_code()
    record["verification_code_hash"] = hash_verification_code(username, code)
    record["verification_expires_at"] = now_ts() + VERIFICATION_CODE_TTL_SECONDS
    record["verification_last_sent_at"] = now_ts()
    record["verified"] = False
    record["verified_at"] = None
    return code


def send_verification_email(username: str, email: str, code: str):
    validate_smtp_config()
    message = EmailMessage()
    sender_name = settings.smtp_from_name.strip() or settings.app_name
    message["Subject"] = "Código de verificación de Symbiotix"
    message["From"] = f"{sender_name} <{settings.smtp_from_email}>"
    message["To"] = email
    message.set_content(
        "\n".join(
            [
                "Symbiotix",
                "",
                f"Hola {username},",
                "",
                "Recibimos una solicitud para verificar tu cuenta.",
                f"Tu código de verificación es: {code}",
                "",
                "El código expira en aproximadamente 10 minutos.",
                "Si necesitas uno nuevo, puedes solicitar un reenvío desde la pantalla de acceso.",
                "Si no solicitaste esta cuenta, ignora este correo.",
            ]
        )
    )
    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
                smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
                smtp.ehlo()
                if settings.smtp_use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        append_log_event(
            {
                "event": "smtp_verification_failed",
                "smtp_host": settings.smtp_host,
                "smtp_port": settings.smtp_port,
                "smtp_use_tls": settings.smtp_use_tls,
                "smtp_use_ssl": settings.smtp_use_ssl,
                "to": email,
                "error": str(exc),
            }
        )
        raise HTTPException(
            status_code=502,
            detail="No se pudo enviar el correo de verificación. Verifica la configuración SMTP e intenta nuevamente.",
        )


def assert_verification_code(username: str, record: dict[str, object], code: str):
    stored_hash = str(record.get("verification_code_hash") or "")
    expires_at = int(record.get("verification_expires_at") or 0)
    if not stored_hash or not expires_at:
        raise HTTPException(status_code=400, detail="Solicita un nuevo código de verificación")
    if now_ts() > expires_at:
        raise HTTPException(status_code=401, detail="El código de verificación expiró")
    candidate = hash_verification_code(username, code)
    if not hmac.compare_digest(stored_hash, candidate):
        raise HTTPException(status_code=401, detail="Código de verificación inválido")


def mark_user_verified(record: dict[str, object]):
    record["verified"] = True
    record["verified_at"] = now_ts()
    record["verification_code_hash"] = None
    record["verification_expires_at"] = None


def verification_cooldown_remaining(record: dict[str, object]) -> int:
    last_sent_at = int(record.get("verification_last_sent_at") or 0)
    remaining = (last_sent_at + VERIFICATION_RESEND_COOLDOWN_SECONDS) - now_ts()
    return max(0, remaining)


def require_non_empty(value: str, field_name: str) -> str:
    clean = (value or "").strip()
    if not clean:
        raise HTTPException(status_code=400, detail=f"{field_name} es requerido")
    return clean


def get_current_user(authorization: str | None = Header(default=None)) -> str:
    validate_auth_config()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token vacío")
    return parse_token(token)


@app.on_event("startup")
def startup_seed_users():
    validate_auth_config()
    ensure_default_user()


@app.post("/auth/signup")
@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    validate_auth_config()
    validate_smtp_config()
    username = require_non_empty(req.username, "username")
    password = require_non_empty(req.password, "password")
    email = validate_email(req.email)

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="password debe tener al menos 6 caracteres")

    users = load_users()
    if username in users:
        raise HTTPException(status_code=409, detail="El usuario ya existe")

    users[username] = make_user_record(username, password, email, verified=False)
    code = apply_new_verification_code(username, users[username])
    send_verification_email(username, email, code)
    save_users(users)

    return {
        "status": "ok",
        "message": "Cuenta creada. Revisa tu correo para validar el código.",
        "user": username,
        "email": email,
        "verified": False,
        "verification_required": True,
        "verification_expires_in": VERIFICATION_CODE_TTL_SECONDS,
        "resend_cooldown_seconds": VERIFICATION_RESEND_COOLDOWN_SECONDS,
    }


@app.post("/auth/login")
@app.post("/api/auth/login")
def login(req: LoginRequest):
    validate_auth_config()
    username = require_non_empty(req.username, "username")
    password = require_non_empty(req.password, "password")

    if not verify_user_password(username, password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    users = load_users()
    record = users.get(username)
    if not record:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not bool(record.get("verified")):
        code = (req.verification_code or "").strip()
        if not code:
            raise HTTPException(
                status_code=403,
                detail="Cuenta no verificada. Ingresa el código de verificación enviado por correo.",
            )
        assert_verification_code(username, record, code)
        mark_user_verified(record)
        save_users(users)

    token = issue_token(username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.auth_token_ttl,
        "user": username,
        "verified": bool(record.get("verified")),
    }


@app.post("/auth/resend-verification")
@app.post("/api/auth/resend-verification")
def resend_verification(req: ResendVerificationRequest):
    validate_auth_config()
    validate_smtp_config()
    username = require_non_empty(req.username, "username")
    password = require_non_empty(req.password, "password")

    if not verify_user_password(username, password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    users = load_users()
    record = users.get(username)
    if not record:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if bool(record.get("verified")):
        return {"status": "ok", "message": "La cuenta ya está verificada", "verified": True}

    cooldown_remaining = verification_cooldown_remaining(record)
    if cooldown_remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Espera {cooldown_remaining} segundos antes de reenviar el código",
        )

    email = str(record.get("email") or "")
    if not email:
        raise HTTPException(status_code=400, detail="La cuenta no tiene correo registrado")

    code = apply_new_verification_code(username, record)
    send_verification_email(username, email, code)
    save_users(users)
    return {
        "status": "ok",
        "message": "Código reenviado",
        "user": username,
        "verified": False,
        "verification_required": True,
        "verification_expires_in": VERIFICATION_CODE_TTL_SECONDS,
        "resend_cooldown_seconds": VERIFICATION_RESEND_COOLDOWN_SECONDS,
    }


@app.post("/auth/change-password")
@app.post("/api/auth/change-password")
def change_password(req: ChangePasswordRequest, user: str = Depends(get_current_user)):
    validate_auth_config()
    current_password = require_non_empty(req.current_password, "current_password")
    new_password = require_non_empty(req.new_password, "new_password")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="new_password debe tener al menos 6 caracteres")

    if not verify_user_password(user, current_password):
        raise HTTPException(status_code=401, detail="Contraseña actual inválida")

    users = load_users()
    record = users.get(user)
    if not record:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    record["password_hash"] = hash_password(user, new_password)
    save_users(users)
    return {"status": "ok", "message": "Contraseña actualizada", "user": user}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "app_name": settings.app_name,
        "model": settings.ollama_model,
        "ollama_url": settings.ollama_url,
        "num_predict": settings.num_predict,
        "ollama_timeout": settings.ollama_timeout,
        "ollama_retries": settings.ollama_retries,
        "log_path": settings.log_path,
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
        except (requests.RequestException, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < settings.ollama_retries:
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
    answer = (data.get("response") or "").strip()
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
        "model": settings.ollama_model,
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
                                        "model": settings.ollama_model,
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
                if attempt < settings.ollama_retries:
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
