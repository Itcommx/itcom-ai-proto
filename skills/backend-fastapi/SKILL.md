---
name: backend-fastapi
description: Usa esta skill para implementar servicios backend de ITCOM AI con FastAPI, incluyendo endpoints, auth, modelos, validaciones, configuración, auditoría y pruebas.
---

# Backend FastAPI Skill

## Objetivo
Implementar backend mantenible, modular y seguro para ITCOM AI.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- crear o modificar endpoints FastAPI,
- implementar auth y roles,
- modelar entidades,
- agregar servicios,
- manejar configuración,
- registrar auditoría,
- agregar pruebas backend.

## Instrucciones
1. Revisa `TASKS.md`, `ARCHITECTURE.md` y el módulo afectado antes de modificar código.
2. Implementa cambios pequeños y con responsabilidad clara.
3. Separa routers, schemas, services, repositories y config cuando aplique.
4. No mezcles lógica de infraestructura con lógica de negocio si puedes abstraerla.
5. Usa variables de entorno y configuración centralizada.
6. Agrega manejo básico de errores.
7. Agrega o actualiza pruebas unitarias o de integración relevantes.
8. Mantén nombres descriptivos y consistencia de módulos.
9. Si cambias contratos o rutas, actualiza documentación.
10. No hardcodees secretos ni endpoints sensibles.

## Preferencias de implementación
- Código explícito sobre magia innecesaria
- Validación clara de entradas
- Logs útiles en fallos
- Dependencias mínimas
- Tipado consistente
- Estructura preparada para escalar

## Checklist de salida
- El endpoint o servicio funciona.
- Existen validaciones mínimas.
- La configuración es externa.
- Hay pruebas relevantes.
- No se rompió compatibilidad accidentalmente.
- El cambio es pequeño y revisable.
