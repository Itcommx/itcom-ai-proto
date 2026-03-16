---
name: devops-release
description: Usa esta skill para mantener la operación técnica de ITCOM AI, incluyendo Docker, CI/CD, staging, observabilidad, health checks, rollback y readiness de release.
---

# DevOps Release Skill

## Objetivo
Preparar ITCOM AI para ejecutarse, validarse y liberarse de forma controlada.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- crear o mantener Docker/Compose,
- configurar CI/CD,
- preparar staging,
- agregar health checks,
- definir rollback,
- mejorar observabilidad,
- construir checklist de release.

## Instrucciones
1. Revisa `TASKS.md`, `ARCHITECTURE.md` y la estructura de despliegue actual.
2. Mantén configuración reproducible y simple.
3. No acoples despliegue a entornos locales irrepetibles.
4. Toda variable sensible debe salir de configuración externa.
5. Agrega health checks y smoke tests cuando aplique.
6. Piensa siempre en recuperación: logs, rollback, monitoreo, validación post-deploy.
7. Mantén pipelines entendibles y pequeños.
8. No despliegues a producción sin compuertas explícitas.
9. Documenta pasos operativos y supuestos.
10. Prioriza staging estable antes de sofisticación avanzada.

## Checklist de salida
- El entorno se puede levantar o validar de forma consistente.
- Existe visibilidad básica del estado del sistema.
- El pipeline es entendible y útil.
- Hay base razonable para rollback o recuperación.
- La documentación operativa quedó alineada.
