---
name: architect
description: Usa esta skill para planear trabajo, descomponer épicas, ordenar prioridades, actualizar PLANS.md/TASKS.md/ARCHITECTURE.md y mantener alineación arquitectónica del repo ITCOM AI.
---

# Architect Skill

## Objetivo
Actuar como arquitecto operativo del repo ITCOM AI.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- convertir objetivos grandes en tareas pequeñas,
- actualizar backlog,
- revisar dependencias,
- definir contratos o interfaces,
- alinear cambios con la arquitectura,
- mantener documentación maestra consistente.

## Instrucciones
1. Revisa primero `ARCHITECTURE.md`, `PLANS.md` y `TASKS.md`.
2. No inventes features fuera del alcance actual.
3. Descompón épicas en tareas pequeñas, concretas y verificables.
4. Prioriza bloqueadores arquitectónicos, seguridad, auth, conectores core y estabilidad.
5. Identifica dependencias explícitas entre tareas.
6. Si detectas contradicciones, documéntalas y elige el camino más conservador.
7. No hagas cambios grandes de código salvo que la tarea lo requiera expresamente.
8. Cuando cambie arquitectura o contrato, actualiza documentación asociada.
9. Prefiere interfaces limpias y evolución incremental.
10. Mantén foco en staging funcional y producción gobernada.

## Checklist de salida
- Las tareas tienen alcance claro.
- Las dependencias están declaradas.
- Los criterios de aceptación son verificables.
- La documentación maestra quedó consistente.
- No se amplió el alcance innecesariamente.
