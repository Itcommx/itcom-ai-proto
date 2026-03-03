import os, time, json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "ITCOM AI Prototype")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
LOG_PATH = os.getenv("LOG_PATH", "/app/logs/requests.jsonl")

app = FastAPI(title=APP_NAME)

# CORS para que el frontend (8080) pueda llamar al backend (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user: str | None = "board-demo"

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "model": OLLAMA_MODEL, "ollama_url": OLLAMA_URL}

@app.post("/chat")
def chat(req: ChatRequest):
    t0 = time.time()

    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message vacío")

    # Prompt corto para demo (menos tokens = más rápido)
    prompt = f"Responde en español, claro y breve.\nPregunta: {msg}\n"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 80,
            "temperature": 0.2
        }
    }

    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error llamando a Ollama: {str(e)}")

    took_ms = int((time.time() - t0) * 1000)
    answer = (data.get("response") or "").strip()

    log_event = {
        "ts": int(time.time()),
        "user": req.user,
        "model": OLLAMA_MODEL,
        "took_ms": took_ms,
        "prompt_chars": len(msg),
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_event, ensure_ascii=False) + "\n")

    return {"answer": answer, "took_ms": took_ms, "model": OLLAMA_MODEL}
