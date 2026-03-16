# ITCOM AI — Task Board

## Convenciones de estado
- TODO
- IN_PROGRESS
- BLOCKED
- REVIEW
- DONE

## Convenciones de prioridad
- P0 = crítico
- P1 = alto
- P2 = medio
- P3 = bajo

## Convenciones de dominio
- ARCH
- BACKEND
- FRONTEND
- AI
- INTEGRATION
- DEVOPS
- QA
- SECURITY
- DOCS

---

## Backlog inicial

| ID | Título | Dominio | Prioridad | Dependencias | Skill sugerida | Estado | Criterio de aceptación |
|----|--------|---------|-----------|--------------|----------------|--------|------------------------|
| T-001 | Crear estructura base del monorepo | ARCH | P0 | Ninguna | architect | DONE | Repo con carpetas base, docs iniciales y estructura consistente |
| T-002 | Crear FastAPI base con endpoint /health | BACKEND | P0 | T-001 | backend-fastapi | DONE | API levanta localmente y responde health check |
| T-003 | Crear archivo .env.example y manejo centralizado de configuración | BACKEND | P0 | T-001 | backend-fastapi | REVIEW | Variables definidas y cargadas desde configuración única |
| T-004 | Crear Docker Compose base para app + db + redis | DEVOPS | P0 | T-001 | devops-release | BLOCKED | Servicios levantan localmente de forma reproducible |
| T-005 | Crear Makefile con comandos estándar | DEVOPS | P1 | T-001 | devops-release | TODO | Existen comandos mínimos para setup, test, lint y run |
| T-006 | Implementar autenticación inicial | BACKEND | P0 | T-002, T-003 | backend-fastapi | BLOCKED | Usuarios pueden autenticarse con flujo básico funcional |
| T-007 | Implementar roles y permisos base | BACKEND | P0 | T-006 | backend-fastapi | TODO | Existen al menos roles admin y user con validación |
| T-008 | Diseñar modelo de auditoría de acciones e interacciones | BACKEND | P1 | T-002 | backend-fastapi | TODO | Existe modelo y persistencia de eventos auditables |
| T-009 | Crear esquema inicial de base de datos de aplicación | BACKEND | P0 | T-002 | backend-fastapi | TODO | Modelos principales y migración inicial definidos |
| T-010 | Crear pipeline CI inicial | DEVOPS | P0 | T-001 | devops-release | TODO | CI corre lint y tests mínimos en cada push/PR |
| T-011 | Agregar linting y formateo estándar | QA | P1 | T-002 | qa-security | TODO | Linters y formateadores configurados y ejecutables |
| T-012 | Crear Web UI mínima con login | FRONTEND | P1 | T-006 | backend-fastapi | TODO | UI funcional con login conectado al backend o mockeado |
| T-013 | Crear vista de chat interna mínima | FRONTEND | P1 | T-012 | backend-fastapi | TODO | Usuario autenticado puede interactuar con interfaz básica |
| T-014 | Crear panel admin básico | FRONTEND | P2 | T-012, T-007 | backend-fastapi | TODO | Admin visualiza estado básico del sistema |
| T-015 | Diseñar contrato del conector Odoo | INTEGRATION | P0 | T-001 | integration-odoo | TODO | Existe interfaz documentada y testeable del conector |
| T-016 | Implementar cliente base Odoo con mocks | INTEGRATION | P1 | T-015 | integration-odoo | TODO | Cliente responde datos simulados y tiene pruebas |
| T-017 | Diseñar contrato del conector Contpaqi SQL | INTEGRATION | P0 | T-001 | integration-contpaqi-sql | TODO | Interfaz documentada para acceso controlado a SQL Server |
| T-018 | Implementar cliente base SQL Server con mocks | INTEGRATION | P1 | T-017 | integration-contpaqi-sql | TODO | Cliente SQL simulado funcional con pruebas |
| T-019 | Diseñar contrato del conector RH MariaDB | INTEGRATION | P1 | T-001 | architect | TODO | Interfaz documentada para consultas RH |
| T-020 | Implementar cliente base RH MariaDB con mocks | INTEGRATION | P1 | T-019 | architect | TODO | Cliente RH funcional con datos simulados |
| T-021 | Diseñar contrato del conector Compras PostgreSQL | INTEGRATION | P1 | T-001 | architect | TODO | Interfaz documentada para consultas de compras |
| T-022 | Implementar cliente base Compras PostgreSQL con mocks | INTEGRATION | P1 | T-021 | architect | TODO | Cliente compras funcional con datos simulados |
| T-023 | Crear módulo base de prompt orchestration | AI | P1 | T-002 | ai-rag | TODO | Existe servicio central de construcción de prompts |
| T-024 | Crear estructura del módulo RAG | AI | P1 | T-023 | ai-rag | TODO | Estructura base, interfaces y servicios definidos |
| T-025 | Implementar pipeline inicial de ingesta documental | AI | P1 | T-024 | ai-rag | TODO | Documentos pueden ser procesados y almacenados |
| T-026 | Implementar retrieval básico | AI | P1 | T-024 | ai-rag | TODO | Existe recuperación de contexto funcional |
| T-027 | Registrar trazabilidad de fuentes en respuestas | AI | P1 | T-026 | ai-rag | TODO | Respuestas guardan referencias a fuentes utilizadas |
| T-028 | Crear pruebas unitarias base del backend | QA | P0 | T-002 | qa-security | TODO | Cobertura mínima inicial del backend |
| T-029 | Crear pruebas de integración para conectores mock | QA | P1 | T-016, T-018, T-020, T-022 | qa-security | TODO | Conectores mock cuentan con pruebas de integración |
| T-030 | Configurar secret scanning y dependabot o equivalente | SECURITY | P1 | T-010 | qa-security | TODO | Pipeline detecta secretos y dependencias vulnerables |
| T-031 | Configurar logging estructurado | DEVOPS | P1 | T-002 | devops-release | TODO | Logs consistentes y útiles para depuración |
| T-032 | Configurar métricas y health checks ampliados | DEVOPS | P1 | T-002 | devops-release | TODO | Existen checks de salud y métricas mínimas |
| T-033 | Crear smoke tests de arranque | QA | P1 | T-004, T-010 | qa-security | TODO | Build y arranque básico validables automáticamente |
| T-034 | Crear runbook inicial de despliegue a staging | DOCS | P2 | T-004, T-010 | devops-release | TODO | Documento describe despliegue, rollback y validación |
| T-035 | Definir primer caso de uso real: consulta ejecutiva de ventas | ARCH | P1 | T-016, T-018, T-022 | architect | TODO | Caso documentado con entradas, salidas y criterios |
| T-036 | Definir primer caso de uso real: resumen financiero | ARCH | P1 | T-018 | architect | TODO | Caso documentado con alcance y dependencias |
| T-037 | Definir primer caso de uso real: consulta RH | ARCH | P1 | T-020 | architect | TODO | Caso documentado con restricciones y privacidad |
| T-038 | Preparar checklist de readiness para staging | DEVOPS | P1 | T-010, T-032, T-033 | devops-release | TODO | Checklist usable por QA y release |
| T-039 | Crear dashboard simple de estado del sistema | FRONTEND | P2 | T-014, T-032 | backend-fastapi | TODO | Panel muestra salud general del sistema |
| T-040 | Actualizar documentación base tras cada bloque completado | DOCS | P1 | Continua | architect | TODO | Docs alineadas al estado real del repo |

---

## Reglas operativas del backlog
1. No iniciar tareas con dependencias abiertas salvo autorización explícita.
2. Cada tarea debe producir cambios pequeños y revisables.
3. Toda tarea debe actualizar su estado real.
4. Si una tarea cambia el comportamiento, debe actualizar pruebas y docs.
5. Si una tarea queda bloqueada, documentar bloqueo y siguiente acción.
6. No cerrar tareas sin validar criterios de aceptación.

---

## Tareas recurrentes
Estas no siempre aparecen como ticket único, pero deben ejecutarse de forma continua:

- Revisar cobertura de pruebas
- Revisar seguridad y secretos
- Limpiar deuda técnica
- Mantener PLANS.md y ARCHITECTURE.md actualizados
- Sincronizar documentación con comportamiento real
- Mantener staging readiness


## Bloqueos activos

- **T-003 (REVIEW):** migración a `settings` validada por compilación/imports y arranque local de FastAPI; falta validación funcional completa del flujo `/api/chat` con Docker+Ollama disponible para cerrar en DONE.
- **T-006 (BLOCKED):** requiere definición mínima de estrategia de identidad (sesión/JWT), almacenamiento de usuarios y criterios de seguridad. Forzar implementación ad-hoc en este punto puede comprometer estabilidad y trazabilidad.
- **T-004 (BLOCKED):** no se puede validar `docker compose up -d --build` en este entorno porque el binario `docker` no está disponible (`command not found`). Se pospone cualquier cambio en `docker-compose.yml` para evitar inestabilidad sin validación reproducible.
