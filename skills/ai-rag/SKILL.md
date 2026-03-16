---
name: ai-rag
description: Usa esta skill para construir el módulo de IA y RAG de ITCOM AI, incluyendo ingesta, retrieval, grounding, orchestration, evaluación y trazabilidad.
---

# AI RAG Skill

## Objetivo
Construir una capa de IA útil, trazable y gobernable para ITCOM AI.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- crear pipelines de ingesta,
- procesar documentos,
- construir retrieval,
- orquestar prompts,
- agregar grounding,
- evaluar respuestas,
- registrar fuentes y trazabilidad.

## Instrucciones
1. Revisa `ARCHITECTURE.md`, `TASKS.md` y contratos de datos disponibles.
2. Diseña componentes modulares: ingesta, indexación, retrieval, orchestration, evaluación.
3. Mantén separación entre lógica de recuperación y lógica de respuesta.
4. Toda respuesta relevante debe poder registrar fuentes o contexto usado.
5. Evita prompts monolíticos si puedes modularizar responsabilidades.
6. Implementa evaluaciones simples antes de optimizaciones avanzadas.
7. Registra metadata útil para auditoría.
8. No ocultes fallos silenciosamente: devuelve estados degradados claros cuando falte contexto.
9. Documenta supuestos del pipeline.
10. Prioriza trazabilidad y consistencia sobre sofisticación temprana.

## Checklist de salida
- El flujo de ingesta/retrieval está claro.
- Las respuestas pueden registrar contexto usado.
- Existen evaluaciones mínimas o pruebas funcionales.
- Los componentes son modulares.
- La documentación del módulo quedó actualizada.
