# ITCOM AI — Master Plan

## 1. Visión
ITCOM AI será una plataforma interna de inteligencia artificial orientada a automatizar consultas, análisis y tareas operativas del corporativo mediante integración con sistemas empresariales existentes, incluyendo Odoo, Contpaqi (SQL Server), sistema de RRHH (MariaDB) y sistema de cotizaciones / órdenes de compra (PostgreSQL).

La plataforma deberá operar de forma segura, auditada, escalable y preparada para evolucionar desde un asistente interno a una capa de automatización corporativa.

---

## 2. Objetivo general
Construir una plataforma de IA empresarial que permita:

- Consultar información operativa y ejecutiva desde una interfaz web interna.
- Automatizar análisis y generación de reportes.
- Integrar datos desde múltiples sistemas corporativos.
- Proveer respuestas con trazabilidad y contexto.
- Reducir tareas manuales, reprocesos y dependencia de Excel.
- Dejar una base técnica lista para despliegue a producción.

---

## 3. Alcance inicial
La primera versión de ITCOM AI incluirá:

1. Backend central en FastAPI.
2. Web UI interna.
3. Módulo de autenticación y roles.
4. Conector a Odoo.
5. Conector a Contpaqi vía SQL Server.
6. Conector a sistema RH en MariaDB.
7. Conector a sistema de compras/cotizaciones en PostgreSQL.
8. Módulo RAG para documentos internos.
9. Bitácora y auditoría de interacciones.
10. Panel administrativo básico.
11. Entorno de staging endurecido.
12. Pipeline CI/CD y documentación operativa.

---

## 4. Fuera de alcance por ahora
No forman parte del release inicial:

- Despliegue multi-tenant externo.
- Automatizaciones transaccionales críticas sin validación humana.
- Integraciones con producción sin capa de sandbox o permisos controlados.
- Flujos financieros o fiscales automáticos no auditados.
- Acciones destructivas sobre bases de datos empresariales.

---

## 5. Arquitectura objetivo
### Capas
- Interfaz Web interna
- API central FastAPI
- Servicios de negocio
- Servicios de IA / RAG
- Conectores empresariales
- Base de datos de aplicación
- Observabilidad y auditoría
- CI/CD y despliegue controlado

### Integraciones previstas
- Odoo
- SQL Server / Contpaqi
- MariaDB / RH
- PostgreSQL / Compras
- Repositorio documental interno

---

## 6. Fases del proyecto

### Fase 0 — Fundaciones
Objetivo:
Dejar listo el repo, la estructura del proyecto, la documentación base, las skills y las reglas operativas.

Entregables:
- Estructura de monorepo
- Docker Compose base
- Makefile
- Documentos maestros
- Skills iniciales
- GitHub Actions base
- Backlog inicial priorizado

Criterio de salida:
El repo permite trabajo multiagente sin improvisación arquitectónica.

---

### Fase 1 — Núcleo de aplicación
Objetivo:
Construir el backend base y las capacidades mínimas del sistema.

Entregables:
- FastAPI base
- Configuración de entorno
- Health endpoints
- Autenticación
- Roles
- Logging estructurado
- Base de datos de aplicación
- Auditoría mínima

Criterio de salida:
La aplicación puede iniciar, autenticar usuarios y registrar actividad.

---

### Fase 2 — UI y administración
Objetivo:
Tener una interfaz usable para pruebas internas.

Entregables:
- Web UI básica
- Login
- Chat UI
- Dashboard admin mínimo
- Historial de consultas
- Vista de estado del sistema

Criterio de salida:
Usuarios internos pueden autenticarse y consumir el sistema.

---

### Fase 3 — Conectores empresariales
Objetivo:
Integrar sistemas de negocio mediante capas seguras y testeables.

Entregables:
- Conector Odoo
- Conector Contpaqi SQL
- Conector RH MariaDB
- Conector Compras PostgreSQL
- Contratos de integración
- Mocks y fixtures
- Tests de integración

Criterio de salida:
Se obtiene información real o simulada de cada sistema bajo interfaz estable.

---

### Fase 4 — IA aplicada y RAG
Objetivo:
Incorporar respuestas asistidas con contexto documental y empresarial.

Entregables:
- Pipeline de ingesta
- Chunking
- Embeddings
- Retrieval
- Prompt orchestration
- Evaluación de respuestas
- Grounding
- Trazabilidad de fuentes

Criterio de salida:
La IA responde con contexto verificable y comportamiento consistente.

---

### Fase 5 — Casos de uso reales
Objetivo:
Implementar casos de uso de alto valor para el corporativo.

Casos iniciales:
- Consulta ejecutiva de ventas
- Resumen financiero
- Consulta RH
- Revisión de órdenes de compra
- Análisis documental interno
- Soporte interno sobre procesos
- Generación de reportes ejecutivos
- Consulta de indicadores
- Resumen de pendientes operativos
- Asistencia a dirección general

Criterio de salida:
Al menos 5 casos de uso funcionando de punta a punta en staging.

---

### Fase 6 — Staging endurecido
Objetivo:
Preparar un entorno casi productivo.

Entregables:
- Pipeline CI/CD
- Monitoreo
- Alertas
- Health checks
- Rollback
- Backups
- Smoke tests
- Seguridad base

Criterio de salida:
Staging estable, monitoreado y recuperable.

---

### Fase 7 — Release readiness
Objetivo:
Preparar salida a producción.

Entregables:
- Checklist de producción
- Runbooks
- Manual operativo
- Plan de soporte
- Release notes
- Criterios de aprobación

Criterio de salida:
Aprobación técnica y operativa para promover a producción.

---

## 7. Definition of Done
Una funcionalidad se considera terminada solo si cumple todo lo siguiente:

- Código implementado
- Pruebas relevantes agregadas o actualizadas
- Lint y validaciones en verde
- Documentación actualizada si aplica
- No introduce secretos ni configuraciones inseguras
- Incluye manejo básico de errores
- Tiene criterios de aceptación cumplidos
- Está registrada en TASKS.md con evidencia
- No rompe módulos existentes
- Es revisable en diff pequeño y claro

---

## 8. Reglas de priorización
Prioridad alta:
- Bloqueadores de arquitectura
- Seguridad
- Autenticación
- Observabilidad
- Integraciones core
- Estabilidad de staging

Prioridad media:
- Mejoras de UX
- Refactors no críticos
- Automatización secundaria

Prioridad baja:
- Embellecimiento visual
- Features opcionales
- Optimización prematura

---

## 9. Riesgos principales
- Ambigüedad en requisitos funcionales
- Drift arquitectónico entre agentes
- Dependencia de sistemas externos inestables
- Accesos inseguros a datos reales
- Automatización sin compuertas de validación
- Exceso de trabajo paralelo sobre módulos acoplados

---

## 10. Mitigaciones
- Mantener ARCHITECTURE.md como fuente oficial
- Dividir tareas en unidades pequeñas
- Usar worktrees / ramas aisladas
- Prohibir cambios directos a producción
- Mockear conectores mientras no exista sandbox
- Revisar seguridad en cada etapa
- Medir cobertura y estabilidad continuamente

---

## 11. Métricas de avance
- Tareas cerradas por semana
- Tiempo promedio por tarea
- Cobertura de pruebas
- Bugs por módulo
- Fallos de CI
- Casos de uso terminados
- Tiempo de recuperación en staging
- Porcentaje de backlog bloqueado

---

## 12. Criterio de éxito del proyecto
ITCOM AI será considerado exitoso en esta etapa si:

- Existe una plataforma funcional en staging
- Se autentican usuarios internos con roles
- Hay conectores funcionales a los sistemas core
- La IA responde con contexto trazable
- Se resuelven casos de uso de negocio reales
- La operación técnica tiene monitoreo, logs y rollback
- El sistema está listo para pasar a piloto controlado
