---
name: integration-contpaqi-sql
description: Usa esta skill para construir y mantener el conector SQL Server / Contpaqi de ITCOM AI con enfoque en seguridad, lectura controlada, contratos y pruebas.
---

# Contpaqi SQL Integration Skill

## Objetivo
Implementar una capa de acceso segura, controlada y testeable para SQL Server / Contpaqi.

## Cuándo usar esta skill
Usa esta skill cuando necesites:
- definir contrato del conector a SQL Server,
- crear clientes o repositorios de acceso,
- mapear entidades y consultas,
- agregar mocks o fixtures,
- documentar alcance del conector,
- preparar consultas de solo lectura.

## Instrucciones
1. Revisa `TASKS.md`, `ARCHITECTURE.md` y documentación del dominio financiero/contable disponible.
2. Diseña la integración mediante abstracciones claras.
3. Prioriza acceso de solo lectura salvo instrucción expresa.
4. Usa variables de entorno para host, puerto, usuario, base y opciones.
5. Evita acoplar lógica de negocio directamente a SQL crudo.
6. Si no existe sandbox, implementa contratos y mocks primero.
7. Agrega manejo de errores, timeouts y validaciones básicas.
8. Documenta limitaciones y supuestos del conector.
9. Nunca hardcodees credenciales ni queries destructivas.
10. Considera sensibilidad de datos y minimiza exposición.

## Checklist de salida
- Existe interfaz clara para el conector.
- El acceso está abstraído del resto del sistema.
- Se prioriza lectura segura.
- Hay pruebas o simulaciones útiles.
- La documentación refleja alcance y límites.
