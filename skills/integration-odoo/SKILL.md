---
name: integration-odoo
description: Usa esta skill para construir y mantener el conector de Odoo de ITCOM AI con contratos claros, clientes desacoplados, pruebas y documentación.
---

# Odoo Integration Skill

## Objetivo
Implementar una integración segura, clara y testeable con Odoo.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- definir contratos de integración Odoo,
- crear clientes o adaptadores,
- mapear respuestas,
- mockear la integración,
- agregar pruebas de integración,
- documentar endpoints o flujos.

## Instrucciones
1. Revisa `ARCHITECTURE.md`, `TASKS.md` y cualquier contrato existente del conector.
2. Diseña la integración detrás de interfaces limpias.
3. Evita acoplar el resto del sistema a detalles del cliente Odoo.
4. Usa configuración externa para URL, credenciales y timeouts.
5. Implementa primero contratos, modelos y mocks si no existe entorno seguro.
6. Agrega manejo de errores y timeouts.
7. Documenta qué operaciones están soportadas.
8. Mantén pruebas con fixtures o respuestas simuladas cuando no exista sandbox.
9. No introduzcas credenciales reales.
10. No implementes operaciones destructivas sin validación expresa.

## Checklist de salida
- Existe interfaz clara del conector.
- El cliente está desacoplado del resto de la app.
- Hay pruebas o mocks útiles.
- La documentación del conector quedó actualizada.
- Los errores y casos de timeout están contemplados.
