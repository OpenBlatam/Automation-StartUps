# 📚 Documentación de Plataforma - Índice Centralizado

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Índice centralizado de toda la documentación de la plataforma de automatización empresarial.

## 📋 Tabla de Contenidos

- [Inicio Rápido](#-inicio-rápido)
- [Documentación por Categoría](#-documentación-por-categoría)
  - [Infraestructura e IaC](#infraestructura-e-iac)
  - [Kubernetes y Orquestación](#kubernetes-y-orquestación)
  - [Datos y ETL](#datos-y-etl)
  - [Machine Learning y MLOps](#machine-learning-y-mlops)
  - [Workflows y BPM](#workflows-y-bpm)
  - [Automatización (RPA)](#automatización-rpa)
  - [Observabilidad](#observabilidad)
  - [KPIs y Analytics](#kpis-y-analytics)
  - [Seguridad](#seguridad)
  - [Entornos y Configuración](#entornos-y-configuración)
  - [Backup y Recuperación](#backup-y-recuperación)
- [Documentos Especializados](#-documentos-especializados)
- [Guías de Referencia Rápida](#-guías-de-referencia-rápida)

## 🚀 Inicio Rápido

### Para Nuevos Usuarios

1. **[README de Documentación](./README.md)** ⭐ **Lee esto primero** - Introducción a la documentación
2. **[Quick Start Guide](./QUICK_START.md)** ⭐ **Empieza aquí** - Guía rápida de 15 minutos
3. **Leer el README Principal**: `README.md` - Visión general completa de la plataforma
4. **Configuración Inicial**: Ver sección de [Inicio Rápido en README](../README.md#-inicio-rápido)

### Por Rol

#### 🛠️ Desarrollador
- **ETL y Datos**: [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) - Guía completa del sistema ETL
- **Workflows**: [`workflow/README.md`](../workflow/README.md) - Orquestación con Kestra, Flowable, Camunda
- **MLOps**: [`ml/kubeflow/README.md`](../ml/kubeflow/README.md) - Pipelines de ML

#### 🔧 DevOps/Platform Engineer
- **Infraestructura**: [`infra/README.md`](../infra/README.md) - Terraform, Kubernetes
- **Observabilidad**: [`observability/README.md`](../observability/README.md) - Prometheus, Grafana, Loki
- **Seguridad**: [`security/README.md`](../security/README.md) - RBAC, OPA, External Secrets

#### 📊 Data Analyst/Scientist
- **Sistema de KPIs**: [`docs/KPI_SYSTEM.md`](./KPI_SYSTEM.md) - Dashboards, reportes, alertas
- **ETL**: [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md)
- **Integraciones**: [`data/INTEGRATIONS.md`](../data/INTEGRATIONS.md) - Databricks, Snowflake

## 📚 Documentación por Categoría

### Infraestructura e IaC

**Terraform**
- **AWS**: `infra/terraform/` - Provisionamiento de VPC, EKS, S3
- **Azure**: `infra/terraform/azure/` - Provisionamiento de AKS, ADLS, ACR
- **Documentación completa**: [`infra/README.md`](../infra/README.md)

**Config Management**
- **Ansible**: `infra/ansible/` - Configuración de servidores
- **Salt**: `infra/salt/` - Gestión de configuración
- **Puppet**: `infra/puppet/` - Automatización de infraestructura

### Kubernetes y Orquestación

**Kubernetes Base**
- **Manifiestos**: `kubernetes/` - Namespaces, Ingress, Integrations
- **Documentación**: [`kubernetes/README.md`](../kubernetes/README.md)
- **Overlays**: `kubernetes/overlays/` - Configuración por entorno (dev/stg/prod)

**Workers y Auto-escalado**
- **HPA**: `kubernetes/workers/` - Horizontal Pod Autoscaler para workers
- **Documentación**: [`kubernetes/workers/README.md`](../kubernetes/workers/README.md)

**Escalabilidad**
- **Arquitectura**: [`docs/ESCALABILIDAD.md`](./ESCALABILIDAD.md) - Workers, infraestructura, observabilidad

### Datos y ETL ⭐

**Airflow** - Pipelines de datos enterprise-grade

- **README General**: [`data/airflow/README.md`](../data/airflow/README.md) - Configuración y operación
- **Índice ETL Completo**: [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) ⭐ **Referencia Principal**
  - DAGs principales (etl_example, employee_onboarding, kpi_reports_monthly)
  - Utilidades y helpers (etl_config_constants.py, etl_utils.py)
  - Patrones de diseño, optimizaciones, troubleshooting
- **Mejoras Aplicadas**: [`data/airflow/dags/ETL_IMPROVEMENTS.md`](../data/airflow/dags/ETL_IMPROVEMENTS.md) - Historial de mejoras
- **Onboarding**: [`data/airflow/README_onboarding.md`](../data/airflow/README_onboarding.md) - Guía de onboarding

**Base de Datos**
- **Esquemas**: `data/db/` - SQL schemas, índices, vistas materializadas
- **Documentación**: [`data/db/README.md`](../data/db/README.md)

**Integraciones de Analítica**
- **Documentación**: [`data/INTEGRATIONS.md`](../data/INTEGRATIONS.md) - Databricks, Snowflake, sistemas externos

### Machine Learning y MLOps

**MLflow**
- **Tracking y Registry**: `ml/mlflow/`
- **Documentación**: [`ml/mlflow/README.md`](../ml/mlflow/README.md)

**KServe**
- **Model Serving**: `ml/kserve/`
- **Documentación**: [`ml/kserve/README.md`](../ml/kserve/README.md)

**Kubeflow**
- **Plataforma ML**: `ml/kubeflow/`
- **Documentación**: [`ml/kubeflow/README.md`](../ml/kubeflow/README.md)

**Training**
- **Scripts y Pipelines**: `ml/training/`
- **Documentación**: [`ml/training/README.md`](../ml/training/README.md)

### Workflows y BPM

**Kestra** - Orquestador declarativo en YAML
- **Flujos**: `workflow/kestra/flows/`
- **Documentación**: [`workflow/kestra/README.md`](../workflow/kestra/README.md)
- **Ejemplos**: Leads ManyChat→HubSpot, Stripe→Sheets+DB, WhatsApp OCR

**Flowable** - Motor BPM (BPMN 2.0)
- **Deployment**: `workflow/flowable/`
- **Documentación**: [`workflow/flowable/README.md`](../workflow/flowable/README.md)

**Camunda** - Plataforma BPM con workers
- **BPMN**: `workflow/camunda/`
- **Workers**: [`workflow/camunda/README_worker.md`](../workflow/camunda/README_worker.md)
- **Ejemplo**: `onboarding_employee.bpmn` con aprobación de manager

**Overview General**
- **Documentación**: [`workflow/README.md`](../workflow/README.md) - Visión general de orquestación

### Automatización (RPA)

**OpenRPA**
- **Documentación**: [`rpa/OPENRPA.md`](../rpa/OPENRPA.md) - Automatización de tareas UI/desktop
- **README**: [`rpa/README.md`](../rpa/README.md)

### Observabilidad

**Stack Completa**
- **Componentes**: Prometheus, Grafana, Loki, OpenCost
- **Ubicación**: `observability/`
- **Documentación**: [`observability/README.md`](../observability/README.md) - Guía completa

**Dashboards**
- **Grafana**: `observability/grafana/dashboards/`
- **Documentación**: [`observability/grafana/dashboards/README.md`](../observability/grafana/dashboards/README.md)

**Alertas**
- **Prometheus**: `observability/prometheus/alertrules.yaml` - Reglas de alerta

**ServiceMonitors**
- **Prometheus**: `observability/servicemonitors/` - Auto-descubrimiento de métricas

### KPIs y Analytics

**Sistema de KPIs**
- **Documentación**: [`docs/KPI_SYSTEM.md`](./KPI_SYSTEM.md) ⭐
  - Dashboards automáticos (Grafana)
  - Reportes programados (diario, semanal, mensual)
  - Alertas de KPIs críticos
  - Visualización en tiempo real

**API KPIs**
- **Express + TypeScript**: `web/kpis/`
- **Documentación**: [`web/kpis/README.md`](../web/kpis/README.md)

**Dashboard Next.js**
- **React/Next.js**: `web/kpis-next/`
- **Documentación**: [`web/kpis-next/README.md`](../web/kpis-next/README.md)

### Seguridad

**Seguridad General**
- **Documentación**: [`security/README.md`](../security/README.md)
  - RBAC, OPA Gatekeeper, External Secrets
  - Network Policies, Certificados TLS
  - Autenticación OIDC

**Vault**
- **HashiCorp Vault**: `security/vault/`
- **Documentación**: [`security/vault/README.md`](../security/vault/README.md)

**Network Policies**
- **Políticas de Red**: `security/networkpolicies/`
- **Baseline**: `security/networkpolicies/baseline.yaml`

**RBAC**
- **Roles y Permisos**: `security/kubernetes/rbac-baseline.yaml`

### Entornos y Configuración

**Environments**
- **Configuración por Entorno**: `environments/` (dev/stg/prod)
- **Documentación**: [`environments/README.md`](../environments/README.md)
- **Archivos**: `dev.yaml`, `stg.yaml`, `prod.yaml`

### Backup y Recuperación

**Velero**
- **Backups de Kubernetes**: `backup/`
- **Documentación**: [`backup/README.md`](../backup/README.md)
- **Configuración**: `backup/velero/values.yaml`

### Utilidades

**Scripts**
- **Scripts y Utilidades**: `scripts/`
- **Documentación**: [`scripts/README.md`](../scripts/README.md)
- **Ejemplos**: Health checks, onboarding CLI

## 📖 Documentos Especializados

### 📚 Documentación Técnica Completa

**Guías Principales** (Nuevas):
- **[Arquitectura](./ARQUITECTURA.md)** ⭐ - Arquitectura completa del sistema
  - Componentes principales
  - Patrones arquitectónicos
  - Flujos de datos
  - Decisiones arquitectónicas
- **[Guía de Desarrollo](./DESARROLLO.md)** ⭐ - Guía para desarrolladores
  - Configuración del entorno
  - Crear DAGs, workflows, workers
  - Testing y code review
  - Mejores prácticas
- **[Operación y Mantenimiento](./OPERACION.md)** ⭐ - Guía para operaciones
  - Monitoreo y alertas
  - Mantenimiento rutinario
  - Backup y recuperación
  - Performance tuning
- **[Troubleshooting](./TROUBLESHOOTING.md)** ⭐ - Resolución de problemas
  - Problemas comunes
  - Comandos útiles
  - Escalación
- **[Deployment](./DEPLOYMENT.md)** ⭐ - Guía de despliegue
  - Despliegue en dev/staging/prod
  - Post-deployment
  - Rollback procedures
- **[Sistema de Aprobaciones](./APPROVAL_SYSTEM.md)** - Documentación técnica
  - Arquitectura modular
  - Plugins y componentes
  - Configuración y uso
- **[Mejoras del Sistema de Aprobaciones](./APPROVAL_SYSTEM_MEJORAS.md)** ⭐ Nuevo - Guía de mejoras
  - Problemas identificados
  - Plan de refactorización
  - Optimizaciones de performance
  - Mejoras de código
- **[Ejemplos Prácticos](./EJEMPLOS_PRACTICOS.md)** ⭐ Nuevo - Ejemplos y casos de uso
  - Ejemplos de Airflow
  - Ejemplos de Kestra
  - Integraciones
  - Casos de uso completos
- **[Guía de Migración](./GUIA_MIGRACION.md)** ⭐ Nuevo - Migración paso a paso
  - Migración de approval_cleanup.py
  - Migración de DAGs legacy
  - Checklist completo
- **[Quick Start Guide](./QUICK_START.md)** ⭐ Nuevo - Guía rápida de 15 minutos
  - Setup inicial
  - Primer DAG
  - Ejecución y monitoreo
- **[Mejores Prácticas](./BEST_PRACTICES.md)** ⭐ Nuevo - Patrones y recomendaciones
  - Principios generales
  - Prácticas de Airflow
  - Prácticas de código
  - Anti-patrones
- **[FAQ](./FAQ.md)** ⭐ Nuevo - Preguntas frecuentes
  - Preguntas generales
  - Airflow, Kubernetes, Base de datos
  - Sistema de aprobaciones
  - Performance y troubleshooting
- **[Mejoras de Arquitectura con Librerías](./MEJORAS_LIBRERIAS.md)** ⭐ Nuevo - Análisis y mejoras
  - Análisis completo de arquitectura actual
  - Librerías recomendadas por categoría
  - Plan de implementación
  - Guía de migración
- **[Guía de Implementación de Mejoras](./GUIA_IMPLEMENTACION_MEJORAS.md)** ⭐ Nuevo - Guía práctica
  - Ejemplos por categoría
  - Patrones de migración
  - Best practices
  - Checklist de implementación
- **[Resumen Ejecutivo: Mejoras](./RESUMEN_MEJORAS_LIBRERIAS.md)** ⭐ Nuevo - Resumen rápido
  - Quick wins
  - Impacto esperado
  - Próximos pasos

### Escalabilidad

**Arquitectura de Escalabilidad**
- **Documento**: [`docs/ESCALABILIDAD.md`](./ESCALABILIDAD.md)
- **Contenido**:
  - Workers (Celery, Camunda)
  - Infraestructura de orquestación
  - Observabilidad de escalabilidad
  - Auto-scaling y optimización

### Sistema de KPIs

**KPIs Automatizado**
- **Documento**: [`docs/KPI_SYSTEM.md`](./KPI_SYSTEM.md)
- **Contenido**:
  - Vistas materializadas
  - DAGs de reportes (diario, semanal, mensual)
  - Dashboards de Grafana
  - Alertas y monitoreo en tiempo real

### Growth / Outreach

**DAGs de Airflow para Outreach**

#### `outreach_multichannel`
- **Ubicación**: `data/airflow/dags/outreach_multichannel.py`
- **Función**: Automatización multi-canal (email + LinkedIn) con A/B testing
- **Características principales**:
  - Segmentación VIP con templates dedicados
  - A/B testing determinístico
  - Engagement tracking y branching inteligente
  - Rate limiting y cooldown por dominio
  - Analytics avanzado con métricas de performance
  - Exportación múltiples formatos (CSV, JSON, Excel, HTML dashboard)
  - Multi-idioma y personalización por industria
  - Integración CRM (HubSpot, Salesforce)
  - Health checks de webhooks
  - Scheduler inteligente (excluye fines de semana)

**Documentación completa**: Ver [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) sección "Growth / Outreach"

#### DAGs Relacionados

- **`outreach_unsubscribe_sync`**: Sincronización de bajas desde CSV/API
- **`outreach_dlq_retry`**: Reintentos automáticos desde DLQ

**Ejemplo de uso**:

```bash
airflow dags trigger outreach_multichannel \
  --conf '{
    "leads_csv_url": "https://bucket/leads.csv",
    "email_webhook_url": "https://hooks.zapier.com/xxx",
    "linkedin_webhook_url": "https://hook.integromat.com/yyy",
    "email_from": "growth@domain.com",
    "email_subject_template": "{{first_name}}, idea para {{company}}",
    "max_parallel_leads": 16
  }'
```

## 🔍 Guías de Referencia Rápida

### Referencias Rápidas

- **[Referencia Rápida](./REFERENCIA_RAPIDA.md)** ⭐ **Nuevo** - Comandos y APIs de referencia
  - Comandos de Airflow, Kubernetes, PostgreSQL
  - Variables de entorno
  - APIs y endpoints
  - Plugins disponibles

- **[Diagramas](./DIAGRAMAS.md)** ⭐ **Nuevo** - Diagramas de arquitectura
  - Arquitectura de alto nivel
  - Flujos de datos
  - Arquitectura de aprobaciones
  - Arquitectura de Kubernetes

### Por Tarea Común

#### Configurar Observabilidad
1. Ver [`observability/README.md`](../observability/README.md)
2. Instalar Prometheus: `helmfile apply`
3. Configurar dashboards: `kubectl apply -f observability/grafana/dashboards/`
4. Configurar alertas: Ver `observability/prometheus/alertrules.yaml`

#### Crear un Nuevo DAG de Airflow
1. Ver [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) - Sección "Patrones de Diseño"
2. Usar `etl_config_constants.py` para configuración centralizada
3. Usar `etl_utils.py` para funciones reutilizables
4. Seguir mejores prácticas documentadas

#### Configurar un Nuevo Workflow en Kestra
1. Ver [`workflow/kestra/README.md`](../workflow/kestra/README.md)
2. Ver ejemplos en `workflow/kestra/flows/`
3. Configurar webhooks y variables según necesidad

#### Monitorear KPIs
1. Ver [`docs/KPI_SYSTEM.md`](./KPI_SYSTEM.md)
2. Acceder a Grafana: `kubectl port-forward -n observability service/prometheus-grafana 3000:80`
3. Ver dashboard de KPIs en tiempo real

#### Troubleshooting
- **Guía Completa**: [`docs/TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) ⭐ - Guía completa de troubleshooting
- **Airflow**: [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) - Sección "Troubleshooting"
- **Observabilidad**: [`observability/README.md`](../observability/README.md) - Sección "Troubleshooting"
- **General**: [`README.md`](../README.md) - Sección "Troubleshooting"

### Archivos Clave por Área

| Área | Archivos Clave |
|------|----------------|
| **Arquitectura** | [`docs/ARQUITECTURA.md`](./ARQUITECTURA.md), [`docs/ESCALABILIDAD.md`](./ESCALABILIDAD.md) |
| **Desarrollo** | [`docs/DESARROLLO.md`](./DESARROLLO.md), [`data/airflow/dags/INDEX_ETL_IMPROVED.md`](../data/airflow/dags/INDEX_ETL_IMPROVED.md) |
| **Operación** | [`docs/OPERACION.md`](./OPERACION.md), [`docs/DEPLOYMENT.md`](./DEPLOYMENT.md) |
| **Troubleshooting** | [`docs/TROUBLESHOOTING.md`](./TROUBLESHOOTING.md), [`docs/APPROVAL_SYSTEM.md`](./APPROVAL_SYSTEM.md) |
| **Mejoras y Librerías** | [`docs/MEJORAS_LIBRERIAS.md`](./MEJORAS_LIBRERIAS.md), [`docs/GUIA_IMPLEMENTACION_MEJORAS.md`](./GUIA_IMPLEMENTACION_MEJORAS.md) |
| **ETL** | `data/airflow/dags/INDEX_ETL_IMPROVED.md`, `data/airflow/dags/etl_example.py` |
| **KPIs** | [`docs/KPI_SYSTEM.md`](./KPI_SYSTEM.md), `web/kpis-next/README.md` |
| **Infraestructura** | `infra/README.md`, `platform.yaml` |
| **Observabilidad** | `observability/README.md`, `observability/prometheus/alertrules.yaml` |
| **Seguridad** | `security/README.md`, `security/secrets/externalsecrets-*.yaml` |
| **Workflows** | `workflow/README.md`, `workflow/kestra/flows/` |

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024
