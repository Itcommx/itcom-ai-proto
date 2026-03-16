# ITCOM AI — Architecture Baseline

## Estado actual del repositorio

Este documento fija una línea base mínima y conservadora para mantener el demo estable.

### Estructura base (monorepo)
- `backend/`: API FastAPI y contenedor de backend.
- `frontend/`: UI estática servida por nginx.
- `skills/`: skills operativas del proyecto por dominio.
- `logs/`: salida local de logs (runtime, fuera de control de código).
- `docker-compose.yml`: orquestación local del demo.
- `PLANS.md` y `TASKS.md`: gobierno de roadmap y ejecución.

## Arquitectura runtime del demo

### Componentes
1. **frontend (nginx)**
   - Publica la UI en `http://localhost:8080`.
   - Reenvía `/api/*` al backend.
2. **backend (FastAPI)**
   - Expone `GET /health` y `POST /chat` (más `POST /chat/stream` para SSE).
   - Registra eventos básicos en `logs/requests.jsonl`.
3. **ollama_proto (Ollama)**
   - Proveedor local del modelo para respuestas de chat.

### Contratos que no deben romperse
- Endpoint de salud: `/health` (vía proxy: `/api/health`).
- Endpoint de chat: `/chat` (vía proxy: `/api/chat`).
- Flujo de arranque validable con `docker compose up -d --build`.

## Decisiones conservadoras vigentes
- Sin frameworks adicionales en frontend (HTML/JS).
- Configuración por variables de entorno y `.env.example`.
- Cambios incrementales, reversibles y con smoke tests del proto.

## Próximos pasos de arquitectura (según backlog)
1. Consolidar T-003 (configuración centralizada del backend).
2. Completar T-004 (compose base con servicios de datos requeridos por el plan).
3. Mantener trazabilidad de avances en `TASKS.md` y `PLANS.md`.
