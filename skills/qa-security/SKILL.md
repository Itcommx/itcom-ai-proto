---
name: qa-security
description: Usa esta skill para ampliar cobertura, validar comportamiento, revisar errores, detectar riesgos de seguridad y endurecer la calidad general del repo ITCOM AI.
---

# QA Security Skill

## Objetivo
Aumentar la calidad, confiabilidad y seguridad del proyecto ITCOM AI.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- agregar o corregir pruebas,
- revisar regresiones,
- validar edge cases,
- revisar secretos y configuración insegura,
- fortalecer manejo de errores,
- endurecer pipelines de calidad.

## Instrucciones
1. Revisa el alcance del cambio antes de escribir pruebas.
2. Prioriza cobertura sobre módulos críticos y rutas usadas.
3. Busca fallos en validación, manejo de errores, timeouts y permisos.
4. Revisa configuración, secretos y exposición accidental de datos.
5. No generes pruebas frágiles o excesivamente acopladas a implementación interna.
6. Prefiere pruebas útiles y mantenibles.
7. Si un cambio carece de pruebas, agrega al menos una capa razonable de validación.
8. Documenta hallazgos relevantes de seguridad o calidad.
9. No ignores warnings importantes sin justificación.
10. Prioriza estabilidad de CI y preparación para staging.

## Checklist de salida
- Hay nuevas pruebas o mejor validación.
- Se revisaron riesgos básicos de seguridad.
- El manejo de errores mejoró o quedó cubierto.
- El cambio reduce riesgo real y no solo infla cobertura.
