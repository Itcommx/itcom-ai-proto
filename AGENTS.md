# ITCOM AI Prototype - Codex Guidance

## Objetivo
Mantener el demo estable (docker compose up -d --build) y mejorar robustez/performance sin romper la UI.

## Comandos de verificación (obligatorios)
- Build/Up:
  docker compose up -d --build
- Smoke tests:
  curl -s http://localhost:8080 | head
  curl -s http://localhost:8080/api/health
  curl -s http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"message":"Hola","user":"test"}'

## Reglas
- Cambios en commits pequeños y claros.
- No introducir frameworks nuevos en frontend (solo HTML/JS).
- No subir secretos: mantener .env fuera del repo, usar .env.example.
- Mantener endpoints existentes /health y /chat.
- Si cambias docker-compose.yml, debes validar que arranca limpio.
