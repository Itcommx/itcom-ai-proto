# ITCOM AI Prototype (Docker Compose)

Stack:
- Frontend estático en **nginx**
- Backend **FastAPI**
- LLM local con **Ollama**

## Arquitectura

- El frontend se sirve en `http://localhost:8080`.
- nginx hace reverse proxy de `/api/*` hacia `backend:8000/*`.
- El frontend usa `API_BASE="/api"` (misma origin), evitando CORS y eliminando IP hardcode.
- El backend mantiene los endpoints:
  - `POST /chat`
  - `GET /health`

## Deploy rápido

1. Copia variables de entorno:

```bash
cp .env.example .env
```

2. Levanta servicios:

```bash
docker compose up -d --build
```

3. Verifica estado:

```bash
docker compose ps
```

4. Abre el frontend:

- `http://localhost:8080`

## Variables de entorno principales

- `OLLAMA_URL` (default sugerido en compose: `http://ollama_proto:11434`)
- `OLLAMA_MODEL` (ej. `llama3:latest`)
- `NUM_PREDICT` (default: `80`)
- `OLLAMA_TIMEOUT` segundos (default: `120`)


## Streaming mode

El backend expone un endpoint adicional para streaming por SSE:

- `POST /chat/stream`

Comportamiento:
- Mantiene compatibilidad total con `POST /chat` (JSON, no streaming).
- `POST /chat/stream` reenvía tokens incrementales desde Ollama (`stream:true`) como eventos SSE (`data: ...`).
- El frontend ahora tiene un checkbox **Streaming SSE** (activo por defecto):
  - Activado: usa `/api/chat/stream` y renderiza tokens en tiempo real.
  - Desactivado: usa `/api/chat` con respuesta JSON completa.
- El contenedor de respuesta permite scroll (`overflow-y: auto`, `max-height: 45vh`) y muestra el texto completo al finalizar (`Respuesta completa`).

Prueba rápida de streaming con curl:

```bash
curl -N -X POST http://localhost:8080/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hola","user":"test"}'
```

## Healthchecks y reinicio

- `ollama_proto`: healthcheck con `ollama list`.
- `backend`: healthcheck contra `http://127.0.0.1:8000/health`.
- `frontend` espera a `backend` healthy.
- Política de reinicio para servicios: `unless-stopped`.

## Comandos de verificación para iasever

Ejecuta estos comandos en iasever después del deploy:

```bash
docker compose up -d --build
curl -s http://localhost:8080 | head
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"message":"Hola","user":"test"}'
curl -N -X POST http://localhost:8080/api/chat/stream -H "Content-Type: application/json" -d '{"message":"Hola","user":"test"}'
```

Resultado esperado:
- `GET /api/health` devuelve JSON con `status: ok`.
- `POST /api/chat` devuelve JSON completo con `answer`.
- `POST /api/chat/stream` imprime eventos SSE incrementales (`data: ...`) y evento final con `done: true`.
- En UI, al enviar `resume en 5 bullets el propósito de este prototipo`, se muestran los 5 bullets completos en el contenedor de respuesta (con scroll si excede el alto).

## Troubleshooting

### 1) Frontend carga pero chat falla

Revisa logs del backend:

```bash
docker compose logs -f backend
```

### 2) Backend responde 502

El backend no pudo comunicarse con Ollama dentro de los reintentos/timeout. Verifica:

```bash
docker compose logs -f ollama_proto
```

También confirma que `OLLAMA_URL` en `.env` sea `http://ollama_proto:11434`.

### 3) Ollama sin modelo descargado

Carga el modelo en el contenedor:

```bash
docker exec -it ollama_proto ollama pull llama3:latest
```

Luego prueba health y chat:

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"message":"hola"}'
```


## Auth endpoints (UI login/signup/cambio de contraseña)

El backend ahora expone endpoints de autenticación para la UX del frontend:

- `POST /auth/signup` **y** `POST /api/auth/signup` (alias equivalente)
  - payload: `{ "username": "nuevo", "password": "secreto123", "email": "nuevo@empresa.com" }`
  - respuesta exitosa: crea la cuenta como no verificada, genera un código de 6 dígitos, lo envía por correo y devuelve el cooldown/TTL de verificación.
- `POST /auth/login` **y** `POST /api/auth/login` (alias equivalente)
  - payload: `{ "username": "admin", "password": "change_me", "verification_code": "123456" }`
  - respuesta: `{ "access_token": "...", "token_type": "bearer", "expires_in": 3600, "user": "admin" }`
- `POST /auth/resend-verification` **y** `POST /api/auth/resend-verification` (alias equivalente)
  - payload: `{ "username": "nuevo", "password": "secreto123" }`
  - respuesta: reenvía un nuevo código si la cuenta sigue sin verificar y no está dentro del cooldown.
- `POST /auth/change-password` **y** `POST /api/auth/change-password` (alias equivalente, requiere `Authorization: Bearer <token>`)
  - payload: `{ "current_password": "old", "new_password": "new12345" }`
  - respuesta: `{ "status": "ok", "message": "Contraseña actualizada", "user": "..." }`

Ruta recomendada para frontend (con `API_BASE="/api"`):
- usar `/api/auth/*` para mantener consistencia con el reverse proxy de nginx.

Persistencia demo de usuarios:
- Se usa `AUTH_USERS_PATH` (default `/app/logs/users.json`).
- En startup se asegura el usuario inicial definido por `AUTH_USERNAME`/`AUTH_PASSWORD`.
- Las nuevas cuentas guardan correo, estado de verificación, hash del código y expiración/cooldown de reenvío.
- Configura SMTP con `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_USE_TLS` y `SMTP_USE_SSL`.
- Defaults sugeridos para el flujo actual: `mail.itcom.mx`, `symbiotix@itcom.mx`, puerto `465`, con `SMTP_USE_TLS=true` y `SMTP_USE_SSL=true`.
