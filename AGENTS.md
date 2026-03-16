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

---

## Alcance de gobierno ampliado
Estas reglas complementan las reglas operativas actuales del proto. En caso de conflicto, debe prevalecer el criterio más conservador que mantenga estable el demo y no rompa los endpoints existentes ni el flujo de `docker compose up -d --build`.

## Fuente de verdad documental
Las fuentes oficiales del proyecto son, en este orden:

1. AGENTS.md
2. PLANS.md
3. TASKS.md
4. README.md
5. .env.example

Si hay contradicción entre documentos, no asumir. Documentar el conflicto y elegir la ruta más segura y reversible.

## Principios de trabajo
1. Trabajar en cambios pequeños, concretos y revisables.
2. No romper la UI actual ni los endpoints existentes.
3. Priorizar estabilidad, seguridad, trazabilidad y mantenibilidad.
4. Evitar cambios amplios no justificados.
5. Toda modificación debe poder validarse localmente con los comandos de verificación del proto.

## Dominios de trabajo sugeridos
### Architect Agent
Responsable de:
- descomponer trabajo,
- mantener backlog,
- alinear tareas con arquitectura,
- definir dependencias,
- actualizar documentación maestra.

### Backend Agent
Responsable de:
- FastAPI,
- servicios,
- auth,
- modelos,
- validaciones,
- endpoints,
- auditoría.

### Integration Agent
Responsable de:
- conectores a Odoo,
- SQL Server,
- MariaDB,
- PostgreSQL,
- contratos de integración,
- mocks,
- fixtures,
- pruebas relacionadas.

### AI/RAG Agent
Responsable de:
- ingesta documental,
- retrieval,
- orchestration,
- grounding,
- evaluación,
- trazabilidad de respuestas.

### Frontend Agent
Responsable de:
- login UI,
- chat UI,
- panel admin,
- dashboard del sistema.

### QA/Security Agent
Responsable de:
- pruebas unitarias,
- pruebas de integración,
- hardening,
- revisión de errores,
- scanning de secretos,
- revisión de dependencias.

### DevOps/Release Agent
Responsable de:
- Docker,
- Compose,
- staging,
- monitoreo,
- health checks,
- rollback,
- release readiness.

## Reglas de ejecución
1. Antes de modificar código, revisar `TASKS.md`.
2. Mantener el alcance estrictamente dentro de la tarea.
3. No mezclar múltiples refactors grandes con una tarea funcional.
4. Si cambias comportamiento, actualiza documentación y validación correspondiente.
5. Preferir mocks y stubs cuando una integración real no sea segura o no esté lista.
6. Si cambias `docker-compose.yml`, validar arranque limpio obligatoriamente.

## Reglas de seguridad ampliadas
Está prohibido:
- introducir secretos reales en el repo,
- usar credenciales hardcodeadas,
- conectarse a producción sin instrucción explícita,
- ejecutar cambios destructivos en bases de datos,
- abrir puertos o accesos externos sin justificación,
- subir dumps reales de datos sensibles.

Toda integración debe usar variables de entorno y configuración externa.

## Política de cambios
Los cambios deben ser:
- pequeños,
- coherentes,
- testeados,
- documentados si aplica,
- reversibles.

Evitar:
- cambios masivos no relacionados,
- renombrados amplios innecesarios,
- refactors especulativos,
- optimización prematura,
- acoplamiento circular.

## Política de pruebas
Cada cambio relevante debe dejar al menos una de estas mejoras:
- nueva prueba unitaria,
- nueva prueba de integración,
- ampliación de cobertura,
- smoke test adicional,
- validación de error o edge case.

No cerrar tareas funcionales sin evidencia básica de validación.

## Criterio de “listo para staging”
Para declarar una funcionalidad lista para staging debe cumplir:
- `docker compose up -d --build` exitoso,
- `/api/health` responde correctamente,
- `/api/chat` responde correctamente,
- la UI sigue cargando,
- no se introdujeron secretos,
- logs útiles disponibles,
- rollback razonable.

## Criterio de escalamiento
Escalar o marcar como bloqueado cuando ocurra cualquiera de estos casos:
- contradicción entre docs,
- dependencia externa no disponible,
- falta de contrato de integración,
- requisito ambiguo que cambia arquitectura,
- riesgo de seguridad,
- necesidad de datos reales sensibles,
- impacto transversal sobre varios módulos.

## Estilo esperado de entrega
Toda tarea debe dejar:
- código claro,
- diff pequeño,
- comentarios solo donde aporten valor,
- nombres descriptivos,
- manejo básico de errores,
- evidencia de validación,
- estado actualizado en `TASKS.md` si aplica.

## Regla final
No optimizar para velocidad a costa de estabilidad, seguridad o mantenibilidad.
La prioridad del proyecto es conservar un demo funcional mientras se evoluciona hacia una plataforma gobernable y lista para pilotaje real.
