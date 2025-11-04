# 🚀 Plataforma de Automatización Empresarial

> Plataforma modular y escalable para automatización de procesos empresariales sobre Kubernetes, integrando data lake, workflows, RPA, MLOps, observabilidad y seguridad.

[![Terraform](https://img.shields.io/badge/terraform-1.6+-blue.svg)](https://terraform.io)
[![Kubernetes](https://img.shields.io/badge/kubernetes-latest-blue.svg)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/helm-3.13+-blue.svg)](https://helm.sh)

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Inicio Rápido](#-inicio-rápido)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Despliegue](#-despliegue)
- [Componentes Principales](#-componentes-principales)
- [Plataformas de Automatización Empresarial](#-plataformas-de-automatización-empresarial)
  - [Quick Start: Integrar en 15 Minutos](#quick-start-integrar-en-15-minutos)
  - [Decisiones Arquitectónicas Clave](#decisiones-arquitectónicas-clave)
  - [Seguridad en Integraciones](#seguridad-en-integraciones)
  - [Escalamiento y Performance](#escalamiento-y-performance)
  - [Testing de Integraciones](#testing-de-integraciones)
  - [Checklist de Go-Live](#checklist-de-go-live)
- [Casos de Uso](#-casos-de-uso)
- [Operación y Mantenimiento](#-operación-y-mantenimiento)
- [Seguridad](#-seguridad)
- [Guías de Onboarding](#-guías-de-onboarding)
- [Troubleshooting](#-troubleshooting)
- [Métricas y Monitoreo](#-métricas-y-monitoreo)
- [Mejores Prácticas](#-mejores-prácticas)
- [Diagrama de Arquitectura Completo](#-diagrama-de-arquitectura-completo)
- [Checklist de Deployment](#-checklist-de-deployment)
- [FAQ](#-faq-preguntas-frecuentes)
- [Costos Estimados](#-costos-estimados)
- [Ejemplo de Flujo End-to-End Completo](#-ejemplo-de-flujo-end-to-end-completo)
- [Quick Links por Componente](#-quick-links-por-componente)
- [Documentación Adicional](#-documentación-adicional)
- [Changelog](#-changelog)

## 🎯 Descripción General

Esta plataforma proporciona una solución completa para automatizar procesos de negocio, integrando:

### 🚀 Inicio Rápido (TL;DR)

**Para empezar en 5 minutos:**

```bash
# 1. Configurar cloud provider
cp platform.yaml.example platform.yaml
# Editar platform.yaml con tu configuración

# 2. Desplegar infraestructura
make tf-init TF_DIR=infra/terraform
make tf-apply TF_DIR=infra/terraform

# 3. Configurar Kubernetes
make k8s-namespaces
make k8s-ingress

# 4. Desplegar componentes base
make helmfile-apply

# 5. Acceder a dashboards
# Grafana: http://grafana.your-domain.com
# Kestra: http://kestra.your-domain.com
# Airflow: http://airflow.your-domain.com
```

**Componentes principales disponibles:**
- ✅ **Kestra**: Workflows declarativos (YAML) - `workflow/kestra/`
- ✅ **Flowable/Camunda**: BPMN para procesos de negocio - `workflow/`
- ✅ **Airflow**: Pipelines ETL enterprise-grade - `data/airflow/`
- ✅ **OpenRPA**: Automatización RPA open-source - `rpa/`
- ✅ **MLflow**: Tracking y serving de modelos ML - `ml/mlflow/`
- ✅ **Grafana/Prometheus**: Observabilidad completa - `observability/`

**¿Necesitas integrar plataformas comerciales?** Ver sección [Plataformas de Automatización Empresarial](#-plataformas-de-automatización-empresarial) para UiPath, ServiceNow y más.

### 💡 Casos de Uso Principales

| Caso de Uso | Herramienta Recomendada | Documentación |
|-------------|------------------------|---------------|
| **ETL de datos** | Airflow | `data/airflow/dags/INDEX_ETL_IMPROVED.md` |
| **Workflows simples** | Kestra | `workflow/kestra/flows/` |
| **Procesos BPMN formales** | Flowable/Camunda | `workflow/flowable/`, `workflow/camunda/` |
| **Automatización UI/Desktop** | OpenRPA | `rpa/OPENRPA.md` |
| **Machine Learning** | MLflow + KServe | `ml/mlflow/`, `ml/kubeflow/` |
| **Dashboards y KPIs** | Grafana + PostgreSQL | `docs/KPI_SYSTEM.md` |

### 🗺️ Rutas Rápidas por Rol

**👨‍💻 Desarrollador:**
1. [Configurar ambiente local](#-inicio-rápido) → [Crear primer workflow](#-workflows-kestra) → [Ejemplos de código](#ejemplos-de-integración-práctica)

**🔧 DevOps/Platform Engineer:**
1. [Desplegar infraestructura](#-despliegue) → [Configurar observabilidad](#-métricas-y-monitoreo) → [Seguridad](#-seguridad)

**📊 Data Engineer/Analyst:**
1. [ETL con Airflow](#airflow-automatizaciones-de-datos) → [Sistema de KPIs](#-kpis-y-analytics) → [Dashboards Grafana](#dashboard-de-kpis-en-tiempo-real-grafana)

**🏢 Arquitecto/Tomador de Decisiones:**
1. [Comparación de plataformas](#comparación-comerciales-vs-herramientas-integradas) → [Análisis de ROI](#análisis-de-roi-uipath-vs-openrpa) → [Decisiones arquitectónicas](#decisiones-arquitectónicas-clave)

**🔒 Security Engineer:**
1. [Seguridad de integraciones](#seguridad-en-integraciones) → [Network Policies](#network-policies) → [Auditoría](#4-auditoría-y-logging-de-seguridad)

### 📊 Mapa de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                  Plataforma de Automatización                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Workflows   │  │     RPA      │  │    MLOps     │    │
│  │              │  │              │  │              │    │
│  │ • Kestra     │  │ • OpenRPA    │  │ • MLflow     │    │
│  │ • Flowable   │  │ • UiPath*    │  │ • Kubeflow   │    │
│  │ • Camunda    │  │              │  │ • KServe     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     ETL      │  │ Observabilidad│  │  Integración │    │
│  │              │  │              │  │              │    │
│  │ • Airflow    │  │ • Prometheus │  │ • ServiceNow*│    │
│  │ • DAGs       │  │ • Grafana    │  │ • Kafka      │    │
│  │ • Plugins    │  │ • ELK Stack  │  │ • API Gateway│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Infraestructura (Kubernetes)                │  │
│  │  EKS/AKS/OpenShift | Terraform | Helm | Kustomize    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

* = Integración opcional con plataformas comerciales
```

### 🎯 Características Destacadas

- ✅ **Multi-cloud**: AWS, Azure, OpenShift
- ✅ **Enterprise-ready**: Circuit breakers, retry logic, idempotencia
- ✅ **Observabilidad completa**: Métricas, logs, traces, dashboards
- ✅ **Seguridad**: RBAC, OPA, External Secrets, Network Policies
- ✅ **Escalable**: Auto-escalado horizontal, workers distribuidos
- ✅ **Open-source first**: Sin vendor lock-in
- ✅ **Integración comercial**: Soporte para UiPath, ServiceNow (opcional)

Esta plataforma proporciona una solución completa para automatizar procesos de negocio, integrando:

- **Infraestructura**: Kubernetes (EKS/AKS/OpenShift) con gestión multi-cloud
- **Almacenamiento**: Data Lake (S3/ADLS) + bases de datos relacionales/NoSQL
- **Orquestación**: Kestra, Flowable, Camunda para workflows y BPM
- **Automatización**: OpenRPA para tareas repetitivas
- **MLOps**: Kubeflow, MLflow, KServe para machine learning
- **Integración**: API Gateway, Kafka para eventos en tiempo real
- **Observabilidad**: Prometheus, Grafana, ELK para monitoreo completo
- **KPIs y Analytics**: Dashboards automáticos, reportes programados, alertas de KPIs críticos, visualización en tiempo real (ver `docs/KPI_SYSTEM.md`)
- **Seguridad**: RBAC, OPA Gatekeeper, External Secrets, Network Policies

## 🏗️ Arquitectura

### Capas de la Plataforma

| Capa | Herramienta | Función | Características Clave |
|------|------------|---------|----------------------|
| **Infraestructura** | Kubernetes (EKS/AKS/OpenShift) | Contenedores, orquestación, escalado | Despliegue híbrido (nube + on‑prem) y cumplimiento local |
| **Almacenamiento** | Data Lake + DB (S3/ADLS + SQL/NoSQL) | Históricos, logs, métricas | Gobierno de datos, metadatos, historización |
| **Orquestación Global** | Kestra | Pipelines declarativos (YAML), triggers, UI | Adopción por equipos mixtos (dev/ops/negocio) |
| **Procesos de Negocio (BPM)** | Flowable | BPMN para procesos formales | Automatizaciones gobernadas y auditables |
| **Automatización (RPA)** | OpenRPA | UI/desktop/API bots | Open‑source, evita lock‑in |
| **IA/ML/MLOps** | Kubeflow + MLflow + KServe | Entrenar/servir, tracking | Evolución hacia automatización "autónoma" |
| **Integración / API / Eventos** | NGINX Ingress + Kafka | APIs, eventos, tiempo real | Escalabilidad y acoplamiento débil |
| **Observabilidad** | Prometheus/Grafana + ELK + IAM | Métricas, logs, alertas, RBAC | Operación 24/7 y cumplimiento |

### Flujo End-to-End

1. **Definición**: Usuarios definen procesos en Kestra (o programan triggers/eventos)
2. **BPM**: Kestra invoca rutas de negocio en Flowable (BPMN) cuando corresponde
3. **RPA**: Tareas sin API se ejecutan con bots OpenRPA coordinados por OpenFlow
4. **IA/ML**: Decisiones y predicciones via Kubeflow/MLflow/KServe
5. **Ejecución**: Todo corre en Kubernetes, integrado por API y eventos (Kafka/Ingress)
6. **Observabilidad**: Monitoreo central (Prometheus/ELK) y gobierno (RBAC, OPA, auditoría)

## ✅ Requisitos

### Herramientas Locales

- **Terraform** >= 1.6
- **kubectl** y/o **oc** (OpenShift)
- **Helm** >= 3.13
- **Make** (para comandos simplificados)

### Accesos Necesarios

- Acceso a cloud provider (Azure/AWS/GCP)
- Identidades configuradas (IAM roles, service principals)
- Permisos para crear recursos de infraestructura

## 🚀 Inicio Rápido

### 1. Configuración Inicial

Edita `platform.yaml` para seleccionar el proveedor cloud y componentes:

```yaml
cloud:
  provider: aws  # opciones: aws | azure | openshift
  region: us-east-1

kubernetes:
  distribution: eks  # opciones: eks | aks | openshift
  clusterName: biz-automation-dev
```

### 2. Despliegue AWS (EKS + S3)

```bash
# Inicializar Terraform
make tf-init TF_DIR=infra/terraform

# Aplicar infraestructura
make tf-apply TF_DIR=infra/terraform

# Crear namespaces
make k8s-namespaces

# Configurar Ingress
make k8s-ingress

# Desplegar componentes de integración
make k8s-integration
```

### 3. Despliegue Azure (AKS + ADLS + ACR)

```bash
# Inicializar Terraform
make tf-init TF_DIR=infra/terraform/azure

# Aplicar infraestructura
make tf-apply TF_DIR=infra/terraform/azure

# Crear namespaces
make k8s-namespaces

# Configurar Ingress
make k8s-ingress

# Desplegar componentes de integración
make k8s-integration
```

### 4. Desplegar Componentes Adicionales

```bash
# Kafka y tópicos
make k8s-kafka
make k8s-kafka-topics

# Instalar charts base (Airflow, Prometheus, Grafana, etc.)
make helmfile-apply
```

## 📁 Estructura del Proyecto

```
├── platform.yaml                 # Configuración central de cloud y componentes
├── Makefile                      # Comandos simplificados para despliegue
├── helmfile.yaml                 # Definición de releases Helm
│
├── infra/terraform/              # Infraestructura como Código
│   ├── main.tf                   # Terraform AWS (EKS + S3)
│   └── azure/                    # Terraform Azure (AKS + ADLS + ACR)
│
├── kubernetes/                   # Manifiestos Kubernetes
│   ├── namespaces.yaml           # Namespaces por entorno
│   ├── ingress/                  # Configuración de Ingress
│   ├── integration/              # Componentes de integración
│   ├── kafka/                    # Kafka (Strimzi) y tópicos
│   └── overlays/                 # Kustomize overlays (dev/stg/prod)
│
├── data/                         # Pipelines y Datos
│   ├── airflow/                  # DAGs de Airflow
│   │   ├── dags/                 # DAGs de ETL, KPIs, outreach, etc.
│   │   └── plugins/              # Plugins personalizados
│   ├── db/                       # Esquemas y scripts SQL
│   └── INTEGRATIONS.md           # Guía de integraciones de analítica
│
├── workflow/                     # Orquestadores de Procesos
│   ├── kestra/                   # Kestra (pipelines YAML)
│   │   └── flows/                # Flujos de ejemplo
│   ├── flowable/                 # Flowable (BPMN)
│   └── camunda/                  # Camunda (alternativa)
│
├── ml/                           # MLOps
│   ├── kubeflow/                 # Kubeflow pipelines
│   ├── mlflow/                   # MLflow tracking y registry
│   └── kserve/                   # Model serving
│
├── observability/                # Monitoreo y Observabilidad
│   ├── prometheus/               # Reglas de alerta
│   ├── grafana/                  # Dashboards y datasources
│   ├── elastic/                  # ELK stack
│   └── opencost/                 # Análisis de costes
│
├── security/                     # Seguridad y Cumplimiento
│   ├── kubernetes/               # RBAC, LimitRanges, Quotas
│   ├── policies/                 # OPA Gatekeeper policies
│   ├── networkpolicies/          # Network Policies
│   ├── secrets/                  # External Secrets Operator
│   └── cert-manager/             # Gestión de certificados
│
├── web/                          # Aplicaciones Web
│   ├── kpis/                     # Interfaz TypeScript (Express)
│   └── kpis-next/                # Interfaz Next.js (React)
│
├── environments/                 # Configuración por entorno
│   ├── dev.yaml
│   ├── stg.yaml
│   └── prod.yaml
│
└── docs/                         # Documentación Adicional
    └── INDEX.md                  # Índice de documentación
```

## 🔧 Despliegue

### Flujo de Despliegue (Alto Nivel)

1. **IaC**: Desplegar redes, cluster, storage, identidades con Terraform
2. **K8s Base**: Aplicar namespaces, ingress, secrets, policies
3. **Integraciones**: Desplegar Kafka, Airflow, Camunda/Kestra/Flowable
4. **Datos/ML**: Configurar data lake, MLflow, KServe, Databricks/Snowflake
5. **Observabilidad**: Activar Prometheus/Grafana, ELK, alertas
6. **Seguridad**: Aplicar políticas de seguridad, RBAC, auditoría

### Despliegue por Entorno

#### Overlays (Kustomize)

```bash
# Desarrollo
kubectl apply -k kubernetes/overlays/dev

# Staging
kubectl apply -k kubernetes/overlays/stg

# Producción
kubectl apply -k kubernetes/overlays/prod
```

#### Validación sin Aplicar Cambios

```bash
make kustomize-validate-dev
make kustomize-validate-stg
make kustomize-validate-prod
```

### Helmfile

Para instalar charts (Ingress, Airflow, Prometheus/Grafana, Strimzi, Camunda):

```bash
# Aplicar todos los releases
make helmfile-apply

# Ver diferencias
make helmfile-diff
```

## 🧩 Componentes Principales

### Airflow: Automatizaciones de Datos

DAGs incluidos en `data/airflow/dags/`:

- **`etl_example.py`**: Pipeline ETL enterprise-grade con:
  - Circuit breaker con auto-reset y tracking de fallos
  - Detección de anomalías de volumen (20 ejecuciones históricas)
  - Paralelismo adaptativo optimizado
  - Validación de checksum para cambios en datos
  - Idempotencia con TTL configurable
  - Métricas de throughput avanzadas (`rows_per_sec`, `ms_per_1k_rows`)
  - Dry run mode para testing
  - Dataset lineage completo
  - DQ checks expandidos (null_rate, min/max rows)
- **`employee_onboarding.py`**: Automatización de onboarding de empleados con:
  - ✅ Validación robusta de datos (formato de emails, fechas, prevención de auto-asignación)
  - ✅ Idempotencia con TTL configurable por parámetro
  - ✅ Logging estructurado con correlación
  - ✅ Integración opcional con HRIS para enriquecer datos
  - ✅ Creación de cuentas (IdP, email, workspace)
  - ✅ Asignación de tareas en tracker (Jira/Linear/Asana)
  - ✅ Envío de email de bienvenida con documentación
  - ✅ Métricas de performance en Stats
  - ✅ Notificaciones Slack en éxito/fallo
  - ✅ Persistencia de progreso en Airflow Variables
  - ✅ Integración con Camunda BPMN para aprobaciones de manager
- **`kpi_reports_monthly.py`**: Reportes mensuales con idempotencia, detección de anomalías en KPIs y métricas completas
- **`stripe_reconcile.py`**: Reconciliación de cargos Stripe vs tabla `payments`
- **`kpi_aggregate_daily.py`**: Consolidación de métricas diarias
- **`leads_sync_hubspot.py`**: Sincronización de contactos HubSpot
- **`outreach_multichannel.py`**: Automatización de outreach multi-canal
- **`payment_reminders.py`**: Recordatorios de pagos pendientes
- **`invoice_generate.py`**: Generación automática de facturas

Ver `data/airflow/dags/INDEX_ETL_IMPROVED.md` para documentación completa y `data/airflow/README.md` para configuración.

### Workflows: Kestra

Pipelines declarativos en YAML. Ejemplos:

- **`employee_onboarding.yaml`**: Proceso completo automatizado de onboarding con 11 fases:
  - ✅ **Fase 1-2**: Validación robusta, normalización de datos, idempotencia, integración HRIS
  - ✅ **Fase 3**: Acciones en paralelo (crear cuentas IdP/Workspace, notificaciones TI, email bienvenida, tareas manager, calendario)
  - ✅ **Fase 4-5**: Consolidación de resultados, tracking detallado, notificaciones éxito/fallo
  - ✅ **Fase 6**: Persistencia completa en PostgreSQL (4 tablas: empleados, acciones, cuentas, seguimiento)
  - ✅ **Fase 7**: Métricas en tiempo real a Prometheus (tasa de éxito, duración, cuentas creadas)
  - ✅ **Fase 8**: Confirmación automática al HRIS con reporte completo
  - ✅ **Fase 9**: Reporte de auditoría con análisis de compliance y recomendaciones
  - ✅ **Fase 10**: Tareas de seguimiento post-onboarding (día 1, 3, 7, 30)
  - ✅ **Fase 11**: Resumen final consolidado con próximos pasos
  - Ver `workflow/kestra/flows/README_onboarding.md` para documentación completa
- **`leads_manychats_to_hubspot.yaml`**: ManyChat → HubSpot + DB + scoring
- **`stripe_payments_to_sheets_db_ai.yaml`**: Stripe → Sheets + DB + AI insights
- **`whatsapp_ticket_to_sheet_doc.yaml`**: WhatsApp → OCR → Sheets + Docs
- **`bpm_rpa_example.yaml`**: Orquestación BPM + RPA

### Aplicaciones Web

#### KPIs (TypeScript/Express)

```bash
cd web/kpis
npm install
KPIS_PG_HOST=localhost KPIS_PG_DB=analytics \
  KPIS_PG_USER=analytics KPIS_PG_PASSWORD=xxx npm run dev
```

#### KPIs (Next.js/React)

```bash
cd web/kpis-next
npm install
KPIS_PG_HOST=localhost KPIS_PG_DB=analytics \
  KPIS_PG_USER=analytics KPIS_PG_PASSWORD=xxx \
  NEXT_PUBLIC_BASE_URL=http://localhost:3000 npm run dev
```

### Casos de Uso Detallados de Integración

#### Caso 1: Procesamiento Automático de Facturas (UiPath + Kestra)

**Escenario**: Procesar 1000+ facturas PDF diarias, extraer datos estructurados, y cargar a ERP.

```yaml
# workflow/kestra/flows/uipath_invoice_processing.yaml
id: process_invoice_batch
namespace: finance
triggers:
  - id: s3_trigger
    type: io.kestra.plugin.aws.s3.Triggers.File
    bucket: invoices-bucket
    prefix: "incoming/"
    suffix: ".pdf"
tasks:
  - id: trigger_uipath_ocr
    type: io.kestra.plugin.http.HttpRequest
    uri: "https://{{ uipath_orchestrator }}/api/Jobs/Start"
    method: POST
    headers:
      Authorization: "Bearer {{ uipath_api_token }}"
    body:
      ReleaseKey: "invoice-processing-release"
      InputArguments: |
        {
          "pdfPath": "{{ trigger.uri }}",
          "outputFormat": "json"
        }
```

#### Caso 2: Aprobaciones ServiceNow + Camunda

```python
# workflow/camunda/worker/servicenow_approval.py
def create_snow_ticket(task: ExternalTask) -> TaskResult:
    servicenow = os.getenv("SERVICENOW_INSTANCE")
    response = requests.post(
        f"{servicenow}/api/now/table/sc_request",
        auth=(os.getenv("SNOW_USER"), os.getenv("SNOW_PASSWORD")),
        json={
            "short_description": f"Purchase: ${task.get_variable('amount')}",
            "category": "Procurement"
        }
    )
    return task.complete({
        "ticket_sys_id": response.json()["result"]["sys_id"]
    })
```

#### Caso 3: Migración Gradual UiPath → OpenRPA

```yaml
# workflow/kestra/flows/hybrid_rpa_routing.yaml
id: hybrid_rpa_routing
tasks:
  - id: evaluate_complexity
    type: io.kestra.core.tasks.flows.Switch
    value: "{{ inputs.complexity_score }}"
    cases:
      - condition: "${value <= 3}"
        tasks:
          - execute_openrpa  # Gratis
      - condition: "${value > 3}"
        tasks:
          - execute_uipath  # Licenciado
```

### Guías Paso a Paso

#### Integrar UiPath con Kestra

1. **Configurar autenticación**:
```bash
curl -X POST "https://instance.orchestrator.uipath.com/api/account/authenticate" \
  -d '{"tenancyName": "default", "usernameOrEmailAddress": "user", "password": "pass"}'

kubectl create secret generic uipath-credentials \
  --from-literal=token='token' \
  --from-literal=orchestrator-url='https://instance.orchestrator.uipath.com'
```

2. **Crear workflow Kestra** (ver ejemplo Caso 1)

### Troubleshooting

**UiPath**: Jobs fallan
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://instance.orchestrator.uipath.com/api/Robots"
```

**ServiceNow**: Tickets duplicados
```python
# Implementar idempotencia con business_key
def create_ticket_idempotent(business_key, ticket_data):
    existing = snow.get("sc_request", params={
        "sysparm_query": f"u_business_key={business_key}"
    })
    if existing.json()["result"]:
        return existing.json()["result"][0]
    return snow.create("sc_request", {**ticket_data, "u_business_key": business_key})
```

### Métricas y Monitoreo de Integraciones

#### Métricas Clave a Monitorear

| Métrica | Plataforma | Threshold | Acción |
|---------|-----------|-----------|--------|
| Tasa de éxito de jobs | UiPath | < 95% | Alertar y revisar logs |
| Latencia promedio | UiPath API | > 5s | Investigar carga |
| Tiempo de respuesta | ServiceNow API | > 3s | Verificar instancia |
| Tickets duplicados | ServiceNow | > 1% | Revisar idempotencia |
| Tasa de error | Camunda workers | > 2% | Revisar código worker |
| Throughput jobs/hora | UiPath | < baseline | Escalar robots |

#### Dashboard Grafana para Integraciones

```json
{
  "dashboard": {
    "title": "Plataformas de Automatización - Integraciones",
    "panels": [
      {
        "title": "UiPath Jobs Success Rate",
        "targets": [{
          "expr": "rate(uipath_jobs_success_total[5m]) / rate(uipath_jobs_total[5m])"
        }]
      },
      {
        "title": "ServiceNow API Latency",
        "targets": [{
          "expr": "histogram_quantile(0.95, servicenow_api_duration_seconds_bucket)"
        }]
      },
      {
        "title": "Cost Savings (OpenRPA vs UiPath)",
        "targets": [{
          "expr": "sum(rpa_executions{bot_type='openrpa'}) * 150 - sum(rpa_executions{bot_type='uipath'}) * 150"
        }]
      }
    ]
  }
}
```

#### Alertas Prometheus

```yaml
# observability/prometheus/integration_alerts.yaml
groups:
  - name: integration_alerts
    rules:
      - alert: UiPathHighFailureRate
        expr: rate(uipath_jobs_failed_total[5m]) / rate(uipath_jobs_total[5m]) > 0.05
        for: 10m
        annotations:
          summary: "UiPath failure rate above 5%"
          
      - alert: ServiceNowSlowAPI
        expr: histogram_quantile(0.95, servicenow_api_duration_seconds_bucket) > 3
        for: 5m
        annotations:
          summary: "ServiceNow API latency above 3s"
          
      - alert: DuplicateTicketsDetected
        expr: rate(servicenow_tickets_duplicate_total[10m]) > 0.01
        for: 5m
        annotations:
          summary: "ServiceNow duplicate ticket rate above 1%"
```

### Diagramas de Flujo Detallados

#### Flujo Completo: Procesamiento de Facturas

```
┌─────────────────┐
│  Factura PDF    │
│  llega a S3     │
└────────┬────────┘
         │ (Trigger)
         ▼
┌─────────────────┐
│   Kestra Flow   │
│  - Valida PDF   │
│  - Prepara data │
└────────┬────────┘
         │ (HTTP POST)
         ▼
┌─────────────────┐
│ UiPath Bot      │
│ - OCR           │
│ - Extracción    │
│ - Validación    │
└────────┬────────┘
         │ (Polling)
         ▼
┌─────────────────┐
│   PostgreSQL    │
│ - Guarda datos  │
│ - Actualiza BD  │
└────────┬────────┘
         │ (REST API)
         ▼
┌─────────────────┐
│   ERP System    │
│ - Carga factura │
│ - Notifica      │
└─────────────────┘
```

#### Flujo: Aprobación ServiceNow + Camunda

```
┌─────────────────┐
│  Solicitud de   │
│  Compra ($50K)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Camunda Process │
│ (BPMN)          │
└────────┬────────┘
         │ (External Task)
         ▼
┌─────────────────┐
│ ServiceNow API  │
│ - Crea ticket   │
│ - Asigna grupo  │
└────────┬────────┘
         │ (Polling cada 10s)
         ▼
┌─────────────────┐
│  Aprobador      │
│  revisa ticket  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   SÍ        NO
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Aprobado│ │Rechazado│
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘
           │
           ▼
    ┌──────────────┐
    │Camunda recibe│
    │  resultado    │
    └───────┬───────┘
            │
      ┌─────┴─────┐
      │           │
      ▼           ▼
┌──────────┐ ┌──────────┐
│ Procesar │ │Notificar │
│ Compra   │ │Rechazo   │
└──────────┘ └──────────┘
```

### Comparación de Performance y Costos

#### Análisis de ROI: UiPath vs OpenRPA

| Métrica | UiPath | OpenRPA | Diferencia |
|---------|--------|---------|------------|
| **Costo mensual** (10 bots) | $15,000 | $500 (infra) | **$14,500/mes** |
| **Time to market** | 2 semanas | 1 semana | +1 semana |
| **Tasa de éxito** | 98% | 95% | -3% |
| **Soporte** | 24/7 | Comunidad | - |
| **ROI anual** | - | +$174,000 | **Ahorro** |

**Cálculo de ROI**:
```
Ahorro anual = ($15,000 - $500) × 12 meses = $174,000
ROI = (Ahorro - Costo migración) / Costo migración
    = ($174,000 - $20,000) / $20,000 = 770%
```

#### Benchmark de Performance

| Operación | UiPath | ServiceNow | Camunda | OpenRPA |
|-----------|--------|------------|---------|---------|
| **Iniciar job/process** | 2-5s | 1-3s | <1s | <1s |
| **Ejecutar tarea simple** | 30-60s | 5-10s | 1-2s | 20-40s |
| **Procesar batch (100 items)** | 10-15 min | 5-8 min | 2-5 min | 8-12 min |
| **Throughput (items/hora)** | 400-600 | 750-1200 | 1200-3000 | 300-600 |

### Checklist de Integración

#### Pre-integración

- [ ] Documentar casos de uso específicos
- [ ] Evaluar costo-beneficio (ROI)
- [ ] Obtener aprobaciones de negocio
- [ ] Configurar cuentas de prueba
- [ ] Definir SLAs y métricas objetivo
- [ ] Planificar migración gradual (si aplica)

#### Durante la Integración

- [ ] Configurar autenticación/secretos
- [ ] Implementar idempotencia
- [ ] Configurar retry logic y timeouts
- [ ] Crear workflows/tasks de prueba
- [ ] Configurar monitoreo y alertas
- [ ] Documentar procesos y decisiones

#### Post-integración

- [ ] Verificar métricas vs objetivos
- [ ] Revisar logs y errores
- [ ] Optimizar performance
- [ ] Entrenar equipo
- [ ] Documentar troubleshooting
- [ ] Planificar escalamiento

### Ejemplos de Código Completos

#### Worker Camunda Completo para ServiceNow

```python
# workflow/camunda/worker/servicenow_complete.py
"""
Worker completo para integración ServiceNow + Camunda
Incluye: creación de tickets, polling de aprobación, manejo de errores
"""
import os
import time
import requests
from typing import Dict, Any
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceNowClient:
    def __init__(self):
        self.instance = os.getenv("SERVICENOW_INSTANCE")
        self.auth = (os.getenv("SNOW_USER"), os.getenv("SNOW_PASSWORD"))
        self.timeout = 30
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea ticket con retry automático"""
        response = requests.post(
            f"{self.instance}/api/now/table/sc_request",
            auth=self.auth,
            json=ticket_data,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()["result"]
    
    def get_ticket(self, sys_id: str) -> Dict[str, Any]:
        """Obtiene ticket por sys_id"""
        response = requests.get(
            f"{self.instance}/api/now/table/sc_request/{sys_id}",
            auth=self.auth,
            params={"sysparm_fields": "state,approval,work_notes,u_approval_status"},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()["result"]

def create_ticket_handler(task: ExternalTask) -> TaskResult:
    """Crea ticket en ServiceNow"""
    client = ServiceNowClient()
    
    amount = task.get_variable("amount", 0)
    priority = "2" if amount > 10000 else "3"
    
    ticket_data = {
        "short_description": f"Purchase approval: ${amount}",
        "description": task.get_variable("description", ""),
        "category": "Procurement",
        "priority": priority,
        "caller_id": task.get_variable("requester_email"),
        "u_amount": str(amount),
        "u_business_key": task.get_variable("business_key")
    }
    
    try:
        ticket = client.create_ticket(ticket_data)
        return task.complete({
            "ticket_sys_id": ticket["sys_id"],
            "ticket_number": ticket["number"],
            "ticket_url": f"{client.instance}/sc_request.do?sys_id={ticket['sys_id']}"
        })
    except Exception as e:
        return task.failure(
            error_message="Failed to create ServiceNow ticket",
            error_details=str(e),
            retries=task.get_retries() - 1,
            retry_timeout=300  # 5 minutos
        )

def check_approval_handler(task: ExternalTask) -> TaskResult:
    """Verifica estado de aprobación"""
    client = ServiceNowClient()
    ticket_sys_id = task.get_variable("ticket_sys_id")
    
    try:
        ticket = client.get_ticket(ticket_sys_id)
        state = ticket["state"]
        approval_status = ticket.get("u_approval_status", "").lower()
        
        if state == "4" and approval_status == "approved":
            return task.complete({
                "approved": True,
                "approval_date": ticket.get("sys_updated_on", "")
            })
        elif state == "5" or approval_status == "rejected":
            return task.complete({
                "approved": False,
                "rejection_reason": ticket.get("work_notes", "")
            })
        else:
            # Aún pendiente - BPMN error para reintentar
            return task.bpmn_error(
                error_code="APPROVAL_PENDING",
                error_message=f"Ticket still pending. State: {state}"
            )
    except Exception as e:
        return task.failure(
            error_message="Failed to check approval status",
            error_details=str(e)
        )

if __name__ == "__main__":
    worker = ExternalTaskWorker(
        worker_id="servicenow-worker",
        base_url="http://camunda:8080/engine-rest",
        max_tasks=10,
        lock_duration=60000  # 1 minuto
    )
    
    worker.subscribe("servicenow-create-ticket", create_ticket_handler)
    worker.subscribe("servicenow-check-approval", check_approval_handler)
    
    print("ServiceNow worker started...")
    worker.start()
```

### Mejores Prácticas

1. **Idempotencia**: Siempre implementar checks antes de crear recursos externos
   - Usar `business_key` o identificadores únicos
   - Verificar existencia antes de crear
   
2. **Retry Logic**: Backoff exponencial para APIs externas
   - Máximo 3-5 reintentos
   - Espera: 2s, 4s, 8s, 16s
   
3. **Timeouts**: Configurar apropiadamente
   - APIs síncronas: 30-60s
   - Operaciones batch: 5-10 minutos
   
4. **Circuit Breakers**: Para APIs críticas
   - Abrir después de 5 fallos consecutivos
   - Cerrar después de 60s de éxito
   
5. **Secrets Management**: External Secrets Operator
   - Nunca hardcodear credenciales
   - Rotación automática cuando sea posible
   
6. **Monitoreo y Alertas**: Prometheus/Grafana
   - Métricas de latencia, throughput, errores
   - Alertas proactivas antes de problemas

7. **Logging Estructurado**: Para debugging
   - Incluir correlation IDs
   - Log levels apropiados (DEBUG, INFO, WARN, ERROR)

8. **Testing**: Pruebas exhaustivas
   - Unit tests para workers
   - Integration tests con ambientes de prueba
   - Load tests para validar escalabilidad

### Quick Start: Integrar en 15 Minutos

#### Opción 1: UiPath + Kestra (RPA Básico)

```bash
# 1. Configurar credenciales UiPath
export UIPATH_ORCHESTRATOR="https://your-instance.orchestrator.uipath.com"
export UIPATH_TOKEN=$(curl -X POST "${UIPATH_ORCHESTRATOR}/api/account/authenticate" \
  -H "Content-Type: application/json" \
  -d '{"tenancyName":"default","usernameOrEmailAddress":"user","password":"pass"}' \
  | jq -r '.result')

# 2. Crear secret en Kubernetes
kubectl create secret generic uipath-credentials \
  --from-literal=orchestrator-url="${UIPATH_ORCHESTRATOR}" \
  --from-literal=token="${UIPATH_TOKEN}" \
  -n workflows

# 3. Desplegar workflow de ejemplo
kubectl apply -f workflow/kestra/flows/uipath_simple_example.yaml

# 4. Probar workflow
curl -X POST "http://kestra.example.com/api/v1/executions/trigger/uipath_simple_example" \
  -H "Content-Type: application/json" \
  -d '{"inputs":{"process_name":"hello_world"}}'
```

**Workflow mínimo** (`workflow/kestra/flows/uipath_simple_example.yaml`):

```yaml
id: uipath_simple_example
namespace: automation
inputs:
  - id: process_name
    type: STRING
    defaults: "hello_world"
tasks:
  - id: trigger_bot
    type: io.kestra.plugin.http.HttpRequest
    uri: "https://{{ secret('uipath-credentials', 'orchestrator-url') }}/api/Jobs/Start"
    method: POST
    headers:
      Authorization: "Bearer {{ secret('uipath-credentials', 'token') }}"
    body:
      ReleaseKey: "{{ vars[inputs.process_name ~ '_release_key'] }}"
```

#### Opción 2: ServiceNow + Camunda (Aprobaciones)

```bash
# 1. Configurar ServiceNow
export SERVICENOW_INSTANCE="https://your-instance.service-now.com"
export SNOW_USER="api.user"
export SNOW_PASSWORD="api.password"

# 2. Crear secret
kubectl create secret generic servicenow-credentials \
  --from-literal=instance="${SERVICENOW_INSTANCE}" \
  --from-literal=username="${SNOW_USER}" \
  --from-literal=password="${SNOW_PASSWORD}" \
  -n workflows

# 3. Desplegar worker
kubectl apply -f workflow/camunda/worker/servicenow-worker-deployment.yaml

# 4. Iniciar proceso BPMN
curl -X POST "http://camunda.example.com/engine-rest/process-definition/key/purchase_approval/start" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "amount": {"value": 5000, "type": "Double"},
      "description": {"value": "Laptop purchase", "type": "String"},
      "requester_email": {"value": "user@example.com", "type": "String"}
    }
  }'
```

### Configuraciones Completas de Ejemplo

#### Configuración Completa: UiPath Integration

```yaml
# kubernetes/integration/uipath-integration.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: uipath-config
  namespace: workflows
data:
  orchestrator-url: "https://your-instance.orchestrator.uipath.com"
  default-strategy: "ModernJobsCount"
  max-retries: "3"
  timeout-seconds: "300"
  polling-interval-seconds: "5"
---
apiVersion: v1
kind: Secret
metadata:
  name: uipath-credentials
  namespace: workflows
type: Opaque
stringData:
  token: "your-uipath-token"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uipath-bridge
  namespace: workflows
spec:
  replicas: 2
  selector:
    matchLabels:
      app: uipath-bridge
  template:
    metadata:
      labels:
        app: uipath-bridge
    spec:
      containers:
      - name: bridge
        image: python:3.11-slim
        env:
          - name: UIPATH_ORCHESTRATOR_URL
            valueFrom:
              configMapKeyRef:
                name: uipath-config
                key: orchestrator-url
          - name: UIPATH_TOKEN
            valueFrom:
              secretKeyRef:
                name: uipath-credentials
                key: token
        command: ["python", "/app/bridge.py"]
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: uipath-bridge
  namespace: workflows
spec:
  selector:
    app: uipath-bridge
  ports:
    - port: 8080
      targetPort: 8080
```

#### Configuración Completa: ServiceNow Integration

```yaml
# kubernetes/integration/servicenow-integration.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: servicenow-config
  namespace: workflows
data:
  instance-url: "https://your-instance.service-now.com"
  api-version: "v1"
  default-table: "sc_request"
  polling-interval: "10"
  max-polling-attempts: "180"  # 30 minutos
---
apiVersion: v1
kind: Secret
metadata:
  name: servicenow-credentials
  namespace: workflows
type: Opaque
stringData:
  username: "api.user"
  password: "api.password"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: servicenow-worker
  namespace: workflows
spec:
  replicas: 3
  selector:
    matchLabels:
      app: servicenow-worker
  template:
    metadata:
      labels:
        app: servicenow-worker
    spec:
      containers:
      - name: worker
        image: camunda-worker-servicenow:latest
        env:
          - name: SERVICENOW_INSTANCE
            valueFrom:
              configMapKeyRef:
                name: servicenow-config
                key: instance-url
          - name: SNOW_USER
            valueFrom:
              secretKeyRef:
                name: servicenow-credentials
                key: username
          - name: SNOW_PASSWORD
            valueFrom:
              secretKeyRef:
                name: servicenow-credentials
                key: password
          - name: CAMUNDA_REST_URL
            value: "http://camunda:8080/engine-rest"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Troubleshooting Avanzado

#### Problemas Comunes y Soluciones

**Problema 1: UiPath Jobs se quedan "Pending" indefinidamente**

```bash
# Diagnosticar
# 1. Verificar robots disponibles
curl -H "Authorization: Bearer $TOKEN" \
  "https://instance.orchestrator.uipath.com/api/Robots?$filter=State eq 'Available'"

# 2. Verificar queues
curl -H "Authorization: Bearer $TOKEN" \
  "https://instance.orchestrator.uipath.com/api/Queues"

# 3. Ver logs del job específico
curl -H "Authorization: Bearer $TOKEN" \
  "https://instance.orchestrator.uipath.com/api/Jobs/{{job_id}}/OutputArguments"

# Solución: Asegurar robots disponibles y queues configuradas
```

**Problema 2: ServiceNow API rate limiting**

```python
# Implementar rate limiting client-side
from time import sleep
from functools import wraps

def rate_limit(max_per_minute=60):
    """Decorador para limitar llamadas API"""
    min_interval = 60.0 / max_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# Uso
@rate_limit(max_per_minute=60)
def call_servicenow_api(endpoint, data):
    # Tu código aquí
    pass
```

**Problema 3: Camunda workers no procesan tareas**

```bash
# Diagnosticar
# 1. Verificar workers conectados
curl "http://camunda:8080/engine-rest/external-task/count"

# 2. Ver tareas disponibles
curl "http://camunda:8080/engine-rest/external-task?topicName=servicenow-create-ticket&locked=false"

# 3. Ver logs del worker
kubectl logs -n workflows deployment/servicenow-worker -f

# Solución: Verificar conectividad, configuración de topic, y locks
```

**Problema 4: Tickets duplicados en ServiceNow**

```python
# Implementar lock distribuido
import redis
import hashlib
import json

redis_client = redis.Redis(host='redis', port=6379)

def create_ticket_with_lock(business_key, ticket_data, ttl=300):
    """Crea ticket con lock distribuido para evitar duplicados"""
    lock_key = f"servicenow:lock:{business_key}"
    ticket_key = f"servicenow:ticket:{business_key}"
    
    # Intentar adquirir lock
    if redis_client.set(lock_key, "1", nx=True, ex=ttl):
        try:
            # Verificar si ya existe
            existing = redis_client.get(ticket_key)
            if existing:
                return json.loads(existing)
            
            # Crear ticket
            ticket = snow_client.create("sc_request", {
                **ticket_data,
                "u_business_key": business_key
            })
            
            # Guardar en cache
            redis_client.set(
                ticket_key,
                json.dumps(ticket),
                ex=3600  # 1 hora
            )
            
            return ticket
        finally:
            # Liberar lock
            redis_client.delete(lock_key)
    else:
        # Lock adquirido por otro proceso, esperar y reintentar
        time.sleep(1)
        return create_ticket_with_lock(business_key, ticket_data, ttl)
```

### Scripts de Utilidad

#### Script: Monitorear Integraciones

```bash
#!/bin/bash
# scripts/monitor-integrations.sh

echo "=== Monitoring Integration Platforms ==="

# UiPath
echo "--- UiPath Status ---"
UIPATH_JOBS=$(curl -s -H "Authorization: Bearer ${UIPATH_TOKEN}" \
  "${UIPATH_ORCHESTRATOR}/api/Jobs?\$top=1&\$filter=State eq 'Running'" \
  | jq '.value | length')
echo "Running jobs: ${UIPATH_JOBS}"

UIPATH_ROBOTS=$(curl -s -H "Authorization: Bearer ${UIPATH_TOKEN}" \
  "${UIPATH_ORCHESTRATOR}/api/Robots?\$filter=State eq 'Available'" \
  | jq '.value | length')
echo "Available robots: ${UIPATH_ROBOTS}"

# ServiceNow
echo "--- ServiceNow Status ---"
SNOW_INCIDENTS=$(curl -s -u "${SNOW_USER}:${SNOW_PASSWORD}" \
  "${SERVICENOW_INSTANCE}/api/now/table/incident" \
  -G --data-urlencode "sysparm_query=state=1" \
  -G --data-urlencode "sysparm_fields=number" \
  | jq '.result | length')
echo "Open incidents: ${SNOW_INCIDENTS}"

# Camunda
echo "--- Camunda Status ---"
CAMUNDA_PROCESSES=$(curl -s "${CAMUNDA_URL}/engine-rest/process-instance/count" \
  | jq '.count')
echo "Active processes: ${CAMUNDA_PROCESSES}"

CAMUNDA_TASKS=$(curl -s "${CAMUNDA_URL}/engine-rest/external-task/count" \
  | jq '.count')
echo "Pending external tasks: ${CAMUNDA_TASKS}"
```

#### Script: Backup de Configuración de Integraciones

```bash
#!/bin/bash
# scripts/backup-integrations.sh

BACKUP_DIR="/backups/integrations/$(date +%Y%m%d)"
mkdir -p "${BACKUP_DIR}"

echo "Backing up integration configurations..."

# Backup secrets
kubectl get secrets -n workflows \
  -l app=uipath-bridge,app=servicenow-worker \
  -o yaml > "${BACKUP_DIR}/secrets.yaml"

# Backup configmaps
kubectl get configmaps -n workflows \
  uipath-config servicenow-config \
  -o yaml > "${BACKUP_DIR}/configmaps.yaml"

# Backup workflows Kestra
kubectl get flows -n automation -o yaml > "${BACKUP_DIR}/kestra-flows.yaml"

# Backup BPMN processes
kubectl exec -n workflows deployment/camunda -c camunda \
  -- find /camunda/webapps/camunda/WEB-INF/classes/bpmn \
  -name "*.bpmn" -exec tar czf "${BACKUP_DIR}/bpmn-processes.tar.gz" {} +

echo "Backup completed: ${BACKUP_DIR}"
```

### Roadmap de Integración

#### Fase 1: POC (2-4 semanas)
- [ ] Configurar ambiente de prueba
- [ ] Implementar 1-2 casos de uso simples
- [ ] Validar integración básica
- [ ] Medir performance inicial

#### Fase 2: Piloto (1-2 meses)
- [ ] Expandir a 5-10 casos de uso
- [ ] Configurar monitoreo completo
- [ ] Implementar alertas
- [ ] Documentar procesos
- [ ] Entrenar equipo

#### Fase 3: Producción (3-6 meses)
- [ ] Migrar todos los casos de uso
- [ ] Optimizar performance
- [ ] Implementar auto-escalado
- [ ] Establecer SLAs
- [ ] Monitoreo avanzado

#### Fase 4: Optimización (Ongoing)
- [ ] Análisis de costos y optimización
- [ ] Migración gradual de comerciales a open-source
- [ ] Mejora continua basada en métricas
- [ ] Expansión a nuevos casos de uso

### Recursos Adicionales

#### Documentación Oficial
- **UiPath**: https://docs.uipath.com/
- **ServiceNow**: https://docs.servicenow.com/
- **Camunda**: https://docs.camunda.org/

#### Comunidades y Foros
- **UiPath Forum**: https://forum.uipath.com/
- **ServiceNow Community**: https://community.servicenow.com/
- **Camunda Forum**: https://forum.camunda.org/

#### Herramientas Útiles
- **UiPath API Explorer**: Swagger UI en `/swagger` de tu instancia
- **ServiceNow REST API Explorer**: `/api/now/doc`
- **Camunda Cockpit**: Dashboard web en `/camunda/app/cockpit`

### Decisiones Arquitectónicas Clave

#### ¿Cuándo usar cada plataforma?

**Use UiPath cuando:**
- Necesite automatizar interacciones complejas con UI legacy (Windows Forms, SAP GUI, Mainframes)
- Requiera componentes pre-construidos del marketplace
- Necesite soporte empresarial 24/7 para operaciones críticas
- Tenga presupuesto para licencias y ROI positivo documentado

**Use ServiceNow cuando:**
- Automatización deba abarcar múltiples departamentos (IT, HR, Finanzas)
- Requiera gobernanza centralizada y cumplimiento estricto
- Necesite integraciones pre-construidas con herramientas empresariales comunes
- Prefiera modelo SaaS sin gestión de infraestructura

**Use Camunda cuando:**
- Procesos de negocio complejos requieran modelado formal (BPMN)
- Necesite alto control técnico y personalización
- Requiera análisis y optimización de procesos
- Tenga equipos técnicos capaces de mantener open-source

**Use herramientas integradas (Kestra/Flowable/OpenRPA) cuando:**
- Presupuesto limitado o preferencia por open-source
- Necesite control total sobre infraestructura
- Requiera integración nativa con Kubernetes/cloud
- Tenga capacidad técnica interna para mantenimiento

### Seguridad en Integraciones

#### Mejores Prácticas de Seguridad

**1. Gestión de Credenciales**

```yaml
# ✅ CORRECTO: Usar External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: uipath-credentials
  namespace: workflows
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: uipath-credentials
    creationPolicy: Owner
  data:
    - secretKey: token
      remoteRef:
        key: uipath/prod/token
    - secretKey: orchestrator-url
      remoteRef:
        key: uipath/prod/url

# ❌ INCORRECTO: Hardcodear en código
# token = "abc123..."  # NUNCA HACER ESTO
```

**2. Network Policies para Aislamiento**

```yaml
# security/networkpolicies/integration-isolation.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: integration-isolation
  namespace: workflows
spec:
  podSelector:
    matchLabels:
      app: uipath-bridge
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: kestra
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: external-services
      ports:
        - protocol: TCP
          port: 443
    - to:
        - podSelector:
            matchLabels:
              name: kube-dns
      ports:
        - protocol: UDP
          port: 53
```

**3. Rotación de Tokens**

```python
# workflow/camunda/worker/token_rotation.py
import os
import requests
from datetime import datetime, timedelta
from functools import lru_cache

class TokenManager:
    def __init__(self):
        self.token_cache = {}
        self.token_ttl = timedelta(hours=1)
    
    @lru_cache(maxsize=1)
    def get_uipath_token(self, orchestrator_url, username, password):
        """Obtiene token UiPath con cache y rotación automática"""
        cache_key = f"{orchestrator_url}:{username}"
        
        if cache_key in self.token_cache:
            token_data = self.token_cache[cache_key]
            if datetime.now() < token_data['expires_at']:
                return token_data['token']
        
        # Renovar token
        response = requests.post(
            f"{orchestrator_url}/api/account/authenticate",
            json={
                "tenancyName": "default",
                "usernameOrEmailAddress": username,
                "password": password
            },
            timeout=10
        )
        response.raise_for_status()
        
        token = response.json()['result']
        expires_at = datetime.now() + self.token_ttl
        
        self.token_cache[cache_key] = {
            'token': token,
            'expires_at': expires_at
        }
        
        return token
```

**4. Auditoría y Logging de Seguridad**

```python
# security/audit/integration_audit.py
import logging
import json
from datetime import datetime

class SecurityAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('security_audit')
        handler = logging.FileHandler('/var/log/security-audit.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_api_call(self, platform, operation, user, success, details=None):
        """Log todas las llamadas API para auditoría"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'platform': platform,
            'operation': operation,
            'user': user,
            'success': success,
            'details': details or {}
        }
        self.logger.info(json.dumps(event))
    
    def log_token_usage(self, platform, user, token_type):
        """Log uso de tokens"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'token_usage',
            'platform': platform,
            'user': user,
            'token_type': token_type
        }
        self.logger.info(json.dumps(event))

# Uso
audit = SecurityAuditLogger()
audit.log_api_call(
    platform='uipath',
    operation='start_job',
    user='system@example.com',
    success=True,
    details={'job_id': '12345', 'process': 'invoice_processing'}
)
```

### Escalamiento y Performance

#### Optimización de Throughput

**1. Pooling de Conexiones**

```python
# workflow/camunda/worker/connection_pool.py
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests

class PooledAPIClient:
    def __init__(self, base_url, max_connections=100):
        self.session = requests.Session()
        
        # Pool de conexiones
        adapter = HTTPAdapter(
            pool_connections=max_connections,
            pool_maxsize=max_connections,
            max_retries=Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.base_url = base_url
    
    def post(self, endpoint, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
    
    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

# Uso compartido
servicenow_client = PooledAPIClient(
    base_url=os.getenv("SERVICENOW_INSTANCE"),
    max_connections=50
)
```

**2. Batch Processing**

```python
# workflow/camunda/worker/batch_processor.py
from typing import List, Dict
import asyncio

async def process_batch_async(items: List[Dict], batch_size: int = 10):
    """Procesa items en batches paralelos"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_item_async(item) for item in batch],
            return_exceptions=True
        )
        results.extend(batch_results)
    
    return results

async def process_item_async(item: Dict):
    """Procesa un item individual"""
    # Tu lógica aquí
    pass

# Uso
items = [{"id": i, "data": f"item_{i}"} for i in range(100)]
results = asyncio.run(process_batch_async(items, batch_size=10))
```

**3. Caching Inteligente**

```python
# workflow/camunda/worker/smart_cache.py
from functools import lru_cache
import redis
import hashlib
import json
from typing import Callable, Any

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def cached_api_call(cache_ttl: int = 300):
    """Decorador para cachear llamadas API"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Generar clave de cache
            cache_key = hashlib.md5(
                f"{func.__name__}:{str(args)}:{str(kwargs)}".encode()
            ).hexdigest()
            
            # Intentar obtener de cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Uso
@cached_api_call(cache_ttl=600)
def get_servicenow_user(user_id: str) -> Dict:
    """Obtiene usuario de ServiceNow con cache de 10 minutos"""
    response = servicenow_client.get(f"/api/now/table/sys_user/{user_id}")
    return response.json()['result']
```

#### Auto-escalado de Workers

```yaml
# kubernetes/integration/servicenow-worker-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: servicenow-worker-hpa
  namespace: workflows
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: servicenow-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: external_tasks_pending
        target:
          type: AverageValue
          averageValue: "10"  # Escalar si hay más de 10 tareas pendientes
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
        - type: Percent
          value: 100
          periodSeconds: 60
```

### Testing de Integraciones

#### Unit Tests

```python
# tests/integrations/test_servicenow_integration.py
import pytest
from unittest.mock import Mock, patch
from workflow.camunda.worker.servicenow_integration import create_snow_ticket

@pytest.fixture
def mock_task():
    task = Mock()
    task.get_variable.side_effect = lambda key, default=None: {
        'amount': 5000,
        'description': 'Test purchase',
        'requester_email': 'test@example.com',
        'business_key': 'test-key-123'
    }.get(key, default)
    return task

@patch('workflow.camunda.worker.servicenow_integration.requests')
def test_create_ticket_success(mock_requests, mock_task):
    """Test creación exitosa de ticket"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': {
            'sys_id': 'abc123',
            'number': 'REQ001'
        }
    }
    mock_requests.post.return_value = mock_response
    
    result = create_snow_ticket(mock_task)
    
    assert result.is_success()
    assert result.variables['ticket_sys_id'] == 'abc123'
    mock_requests.post.assert_called_once()

@patch('workflow.camunda.worker.servicenow_integration.requests')
def test_create_ticket_failure(mock_requests, mock_task):
    """Test manejo de errores"""
    mock_requests.post.side_effect = Exception("API Error")
    
    result = create_snow_ticket(mock_task)
    
    assert result.is_failure()
    assert "API Error" in result.error_details
```

#### Integration Tests

```python
# tests/integrations/test_uipath_integration.py
import pytest
import requests
from workflow.kestra.flows.uipath_integration import trigger_uipath_bot

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("UIPATH_ORCHESTRATOR"),
    reason="UiPath orchestrator not configured"
)
def test_uipath_job_creation():
    """Test real de creación de job en UiPath"""
    result = trigger_uipath_bot(
        release_key="test-release-key",
        input_arguments={"test": "data"}
    )
    
    assert result['State'] == 'Pending' or result['State'] == 'Running'
    assert 'Id' in result
```

### Checklist de Go-Live

#### Pre-Producción

- [ ] Todas las integraciones probadas en staging
- [ ] Monitoreo y alertas configurados
- [ ] Documentación completa actualizada
- [ ] Equipo entrenado en operación
- [ ] Plan de rollback documentado
- [ ] Backup de configuraciones realizado
- [ ] Secrets rotados y seguros
- [ ] Network policies aplicadas
- [ ] Resource limits configurados
- [ ] Health checks funcionando

#### Go-Live

- [ ] Desplegar a producción durante ventana de mantenimiento
- [ ] Verificar health checks de todos los componentes
- [ ] Monitorear métricas por 1 hora
- [ ] Ejecutar casos de uso de prueba
- [ ] Verificar logs sin errores críticos
- [ ] Confirmar SLAs cumplidos

#### Post-Go-Live

- [ ] Revisar métricas de las primeras 24 horas
- [ ] Optimizar basado en métricas reales
- [ ] Documentar lecciones aprendidas
- [ ] Planificar próximos pasos de optimización

### 📚 Recursos de Aprendizaje y Referencias

#### Documentación por Plataforma

**Plataformas Open-Source Integradas:**
- **Kestra**: [Documentación oficial](https://kestra.io/docs) | [Ejemplos](workflow/kestra/flows/)
- **Flowable**: [Guía BPMN](https://www.flowable.com/open-source/docs/bpmn/) | [Casos de uso](workflow/flowable/)
- **Camunda**: [Documentación](https://docs.camunda.org/) | [BPMN Tutorial](https://camunda.com/bpmn/)
- **OpenRPA**: [Documentación](rpa/OPENRPA.md) | [Guía de inicio](rpa/README.md)
- **Airflow**: [Documentación](data/airflow/README.md) | [ETL avanzado](data/airflow/dags/INDEX_ETL_IMPROVED.md)
- **MLflow**: [Tracking ML](ml/mlflow/) | [Kubeflow](ml/kubeflow/README.md)

**Plataformas Comerciales (Integración Opcional):**
- **UiPath**: [API Documentation](https://docs.uipath.com/orchestrator/reference) | [Forum](https://forum.uipath.com/)
- **ServiceNow**: [REST API](https://docs.servicenow.com/bundle/tokyo-application-development/page/integrate/inbound-rest/concept/c_RESTAPI.html) | [Community](https://community.servicenow.com/)

#### Cursos y Tutoriales Recomendados

**Para Desarrolladores:**
1. **Kubernetes Basics**: [Kubernetes.io Tutorials](https://kubernetes.io/docs/tutorials/)
2. **Airflow**: [Apache Airflow Documentation](https://airflow.apache.org/docs/)
3. **BPMN**: [BPMN 2.0 Specification](https://www.omg.org/spec/BPMN/2.0/)
4. **MLOps**: [MLflow Tutorials](https://mlflow.org/docs/latest/tutorials-and-examples/)

**Para Arquitectos:**
1. **Event-Driven Architecture**: Patrones con Kafka
2. **Microservices on Kubernetes**: Service mesh y patterns
3. **Observability**: Métricas, logs y traces

#### Comunidades y Soporte

- **GitHub Issues**: Reportar bugs o solicitar features
- **Slack/Discord**: Comunidad de la plataforma (si existe)
- **Stack Overflow**: Tag `[nombre-plataforma]` para preguntas técnicas

### 🎓 Guías de Aprendizaje Progresivo

#### Nivel 1: Principiante (Primeras 2 semanas)

**Semana 1: Fundamentos**
- [ ] Configurar ambiente local
- [ ] Desplegar primer workflow en Kestra
- [ ] Crear DAG básico en Airflow
- [ ] Explorar dashboards (Grafana, Kestra UI)

**Semana 2: Integraciones Básicas**
- [ ] Conectar workflow a base de datos PostgreSQL
- [ ] Crear webhook en Kestra
- [ ] Configurar alertas básicas en Prometheus
- [ ] Revisar logs en Grafana Loki

#### Nivel 2: Intermedio (Semanas 3-6)

**Semana 3-4: Workflows Avanzados**
- [ ] Crear proceso BPMN en Flowable/Camunda
- [ ] Implementar workers personalizados
- [ ] Configurar error handling y retry logic
- [ ] Optimizar performance de workflows

**Semana 5-6: Observabilidad y Seguridad**
- [ ] Configurar métricas personalizadas
- [ ] Crear dashboards en Grafana
- [ ] Implementar Network Policies
- [ ] Configurar External Secrets Operator

#### Nivel 3: Avanzado (Mes 2+)

- [ ] Diseñar arquitectura de integraciones complejas
- [ ] Implementar auto-escalado avanzado
- [ ] Optimizar costos y performance
- [ ] Migrar de plataformas comerciales a open-source
- [ ] Contribuir a la documentación/proyecto

### 🛠️ Plantillas y Configuraciones Listas para Usar

#### Plantilla: Workflow Kestra con Error Handling

```yaml
# workflow/kestra/flows/template_with_error_handling.yaml
id: template_with_error_handling
namespace: automation
description: Template con manejo robusto de errores
inputs:
  - id: input_data
    type: STRING
    required: true
tasks:
  - id: validate_input
    type: io.kestra.core.tasks.log.Log
    message: "Validating input: {{ inputs.input_data }}"
  
  - id: main_task
    type: io.kestra.plugin.http.HttpRequest
    uri: "https://api.example.com/process"
    method: POST
    body:
      data: "{{ inputs.input_data }}"
    retry:
      type: constant
      interval: PT5S
      maxAttempt: 3
    timeout: PT30S
  
  - id: handle_success
    type: io.kestra.core.tasks.log.Log
    message: "Task completed successfully"
    conditions:
      - type: execution.flow
        expression: "{{ outputs.main_task.status == 'SUCCESS' }}"
  
  - id: handle_failure
    type: io.kestra.plugin.notifications.slack.SlackExecution
    url: "{{ secret('slack-webhook-url') }}"
    message: "Task failed: {{ outputs.main_task.body }}"
    conditions:
      - type: execution.flow
        expression: "{{ outputs.main_task.status == 'FAILED' }}"
```

#### Plantilla: DAG Airflow con Circuit Breaker

```python
# data/airflow/dags/template_circuit_breaker.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from data.airflow.plugins.etl_circuit_breaker import circuit_breaker

default_args = {
    'owner': 'platform-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'template_circuit_breaker',
    default_args=default_args,
    description='Template con circuit breaker',
    schedule_interval='@daily',
    catchup=False,
    tags=['template', 'circuit-breaker']
)

@circuit_breaker(
    failure_threshold=5,
    reset_timeout=timedelta(minutes=10),
    dag_id='template_circuit_breaker'
)
def process_data(**context):
    """Función que usa circuit breaker automático"""
    # Tu lógica aquí
    pass

task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag
)
```

#### Plantilla: Worker Camunda Completo

```python
# workflow/camunda/worker/template_worker.py
"""
Plantilla completa para worker de Camunda
Incluye: logging, error handling, métricas, retry
"""
import logging
import time
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
from prometheus_client import Counter, Histogram

# Métricas Prometheus
task_counter = Counter('camunda_worker_tasks_total', 'Total tasks processed', ['topic', 'status'])
task_duration = Histogram('camunda_worker_duration_seconds', 'Task duration', ['topic'])

logger = logging.getLogger(__name__)

def template_handler(task: ExternalTask) -> TaskResult:
    """Handler de tarea con métricas y logging"""
    topic = task.get_topic_name()
    start_time = time.time()
    
    logger.info(f"Processing task {task.get_task_id()} for topic {topic}")
    
    try:
        # Obtener variables
        input_data = task.get_variable("input_data")
        business_key = task.get_variable("business_key")
        
        # Procesar
        result = process_business_logic(input_data, business_key)
        
        # Registrar métricas de éxito
        task_counter.labels(topic=topic, status='success').inc()
        task_duration.labels(topic=topic).observe(time.time() - start_time)
        
        logger.info(f"Task {task.get_task_id()} completed successfully")
        
        return task.complete({
            "output": result,
            "status": "success"
        })
        
    except Exception as e:
        # Registrar métricas de error
        task_counter.labels(topic=topic, status='error').inc()
        task_duration.labels(topic=topic).observe(time.time() - start_time)
        
        logger.error(f"Task {task.get_task_id()} failed: {str(e)}", exc_info=True)
        
        return task.failure(
            error_message="Processing failed",
            error_details=str(e),
            retries=task.get_retries() - 1 if task.get_retries() > 0 else 0,
            retry_timeout=300
        )

def process_business_logic(input_data, business_key):
    """Lógica de negocio - reemplazar con tu implementación"""
    # Tu código aquí
    return {"processed": True, "key": business_key}

if __name__ == "__main__":
    worker = ExternalTaskWorker(
        worker_id="template-worker",
        base_url="http://camunda:8080/engine-rest",
        max_tasks=10
    )
    
    worker.subscribe("template-topic", template_handler)
    worker.start()
```

### 📋 Checklist de Migración de Comercial a Open-Source

#### Evaluación Pre-Migración

**Análisis de Casos de Uso:**
- [ ] Inventario completo de procesos automatizados
- [ ] Clasificación por complejidad (simple/complejo/crítico)
- [ ] Identificación de dependencias entre procesos
- [ ] Documentación de requisitos de negocio

**Análisis Técnico:**
- [ ] Mapeo de funcionalidades usadas vs disponibles en open-source
- [ ] Evaluación de gaps técnicos
- [ ] Estimación de esfuerzo de migración
- [ ] Identificación de procesos no migrables (requieren comercial)

**Análisis de Costos:**
- [ ] Costo actual anual de plataforma comercial
- [ ] Costo estimado de infraestructura para open-source
- [ ] Costo de migración (tiempo + recursos)
- [ ] Cálculo de ROI y payback period

#### Plan de Migración

**Fase 1: POC (4-8 semanas)**
- [ ] Seleccionar 2-3 procesos simples para migrar
- [ ] Configurar ambiente de prueba
- [ ] Implementar procesos seleccionados
- [ ] Validar funcionalidad y performance
- [ ] Comparar resultados vs comercial
- [ ] Documentar lecciones aprendidas

**Fase 2: Piloto (3-6 meses)**
- [ ] Migrar 20-30% de procesos (no críticos)
- [ ] Configurar monitoreo y alertas
- [ ] Entrenar equipo de operación
- [ ] Establecer SLAs y métricas de éxito
- [ ] Optimizar basado en feedback

**Fase 3: Escalamiento (6-12 meses)**
- [ ] Migrar procesos críticos con supervisión estrecha
- [ ] Implementar redundancia y alta disponibilidad
- [ ] Optimizar costos y performance
- [ ] Documentar mejores prácticas

**Fase 4: Consolidación (Ongoing)**
- [ ] Retirar plataforma comercial (si aplica)
- [ ] Continuar optimización
- [ ] Expandir a nuevos casos de uso
- [ ] Contribuir a comunidades open-source

### 💰 Análisis de Costos Detallado

#### Comparación Anual de Costos (100 usuarios, 1000 procesos/mes)

| Concepto | UiPath | ServiceNow | Open-Source Stack |
|----------|--------|------------|-------------------|
| **Licencias** | $180,000 | $120,000 | $0 |
| **Infraestructura Cloud** | $36,000 | $0 (SaaS) | $24,000 |
| **Soporte/Mantenimiento** | Incluido | Incluido | $12,000 (opcional) |
| **Costo de Migración** | $0 | $0 | $40,000 (one-time) |
| **TOTAL Año 1** | $216,000 | $120,000 | $76,000 |
| **TOTAL Año 2+** | $216,000 | $120,000 | $36,000 |

**Ahorro potencial:**
- Año 1: $44,000 - $140,000 (considerando migración)
- Año 2+: $84,000 - $180,000 anual
- ROI en 6-12 meses típicamente

#### Costos de Infraestructura Estimados

**Cluster Kubernetes (EKS/AKS):**
- 3 nodos m5.xlarge: $300/mes
- Data Lake (S3/ADLS): $200/mes (varía por uso)
- Bases de datos: $150/mes
- Load balancers: $50/mes
- **Total infraestructura base**: ~$700/mes

**Componentes de plataforma:**
- Airflow workers: $200/mes
- Kestra/Camunda: $100/mes
- Observabilidad stack: $150/mes
- **Total componentes**: ~$450/mes

**TOTAL**: ~$1,150/mes = ~$14,000/año (puede escalar según uso)

### 🔧 Comandos Útiles para Operación Diaria

#### Health Checks Rápidos

```bash
# Ver estado general del cluster
kubectl get pods -A | grep -E "(Running|Pending|Error|CrashLoop)"

# Verificar componentes principales
kubectl get pods -n data -l app=airflow
kubectl get pods -n workflows -l app=kestra
kubectl get pods -n workflows -l app=camunda

# Verificar recursos
kubectl top nodes
kubectl top pods -A --sort-by=memory

# Verificar servicios externos
kubectl get ingress -A
kubectl get services -A | grep LoadBalancer
```

#### Debugging de Workflows

```bash
# Kestra - Ver logs de ejecución
kubectl logs -n workflows deployment/kestra -f | grep "execution_id"

# Airflow - Ver logs de DAG
kubectl exec -n data deployment/airflow-webserver -- \
  airflow tasks logs <dag_id> <task_id> <execution_date>

# Camunda - Ver procesos activos
curl http://camunda.example.com/engine-rest/process-instance?active=true | jq

# Ver tareas pendientes en Camunda
curl http://camunda.example.com/engine-rest/external-task/count | jq
```

#### Monitoreo Rápido

```bash
# Ver métricas de Prometheus
kubectl port-forward -n observability service/prometheus 9090:9090
# Acceder a: http://localhost:9090

# Ver dashboards de Grafana
kubectl port-forward -n observability service/grafana 3000:80
# Acceder a: http://localhost:3000

# Ver logs centralizados
kubectl logs -n observability deployment/loki -f
```

#### Gestión de Secretos

```bash
# Ver secrets sincronizados
kubectl get externalsecrets -A

# Forzar resincronización
kubectl delete externalsecret <name> -n <namespace>

# Ver secretos (valores encriptados)
kubectl get secrets -n <namespace> -o yaml
```

### 📜 Scripts de Automatización

#### Script: Health Check Completo

```bash
#!/bin/bash
# scripts/health-check.sh

echo "=== Platform Health Check ==="
echo "Timestamp: $(date)"

# Verificar pods
echo -e "\n--- Pod Status ---"
kubectl get pods -A -o wide | grep -v Running | head -20

# Verificar servicios críticos
echo -e "\n--- Critical Services ---"
services=("airflow-webserver" "kestra" "camunda" "prometheus" "grafana")
for service in "${services[@]}"; do
    status=$(kubectl get pods -A -l app="$service" -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    echo "$service: $status"
done

# Verificar recursos
echo -e "\n--- Resource Usage ---"
kubectl top nodes --no-headers | awk '{print $1": CPU="$2", Memory="$4}'

# Verificar errores recientes
echo -e "\n--- Recent Errors (last 100 lines) ---"
kubectl logs -n data deployment/airflow-scheduler --tail=100 | grep -i error | tail -5
kubectl logs -n workflows deployment/kestra --tail=100 | grep -i error | tail -5

# Verificar métricas críticas
echo -e "\n--- Critical Metrics ---"
kubectl exec -n observability deployment/prometheus -- \
  wget -qO- http://localhost:9090/api/v1/query?query=up | jq '.data.result[] | select(.value[1]=="0")'
```

#### Script: Backup Automático

```bash
#!/bin/bash
# scripts/auto-backup.sh
# Ejecutar via Cron: 0 2 * * * /path/to/auto-backup.sh

BACKUP_ROOT="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_ROOT"

echo "Starting backup at $(date)"

# Backup de configuraciones Kubernetes
kubectl get all,configmap,secret -A -o yaml > "$BACKUP_ROOT/k8s-resources.yaml"

# Backup de variables Airflow
kubectl exec -n data deployment/airflow-webserver -- \
  airflow variables export - > "$BACKUP_ROOT/airflow-vars.json" 2>/dev/null

# Backup de conexiones Airflow
kubectl exec -n data deployment/airflow-webserver -- \
  airflow connections export - > "$BACKUP_ROOT/airflow-conns.json" 2>/dev/null

# Backup de base de datos (si está en PostgreSQL)
if kubectl get secret -n data postgres-credentials &>/dev/null; then
    PGPASSWORD=$(kubectl get secret -n data postgres-credentials -o jsonpath='{.data.password}' | base64 -d)
    kubectl exec -n data deployment/postgres -- \
      pg_dump -U postgres analytics > "$BACKUP_ROOT/database.sql"
fi

# Comprimir y limpiar backups antiguos (>30 días)
tar czf "$BACKUP_ROOT.tar.gz" "$BACKUP_ROOT"
rm -rf "$BACKUP_ROOT"
find /backups -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed at $(date)"
```

#### Script: Escalar Workers Dinámicamente

```bash
#!/bin/bash
# scripts/scale-workers.sh

NAMESPACE="${1:-data}"
DEPLOYMENT="${2:-airflow-worker}"
TARGET_PODS="${3:-5}"

echo "Scaling $DEPLOYMENT in namespace $NAMESPACE to $TARGET_PODS replicas"

# Obtener pods actuales
CURRENT_PODS=$(kubectl get deployment -n "$NAMESPACE" "$DEPLOYMENT" -o jsonpath='{.spec.replicas}')

if [ "$CURRENT_PODS" != "$TARGET_PODS" ]; then
    kubectl scale deployment -n "$NAMESPACE" "$DEPLOYMENT" --replicas="$TARGET_PODS"
    
    # Esperar a que todos los pods estén listos
    kubectl wait --for=condition=ready pod \
      -l app="$DEPLOYMENT" -n "$NAMESPACE" \
      --timeout=300s
    
    echo "Scaled from $CURRENT_PODS to $TARGET_PODS pods"
else
    echo "Already at target: $TARGET_PODS pods"
fi
```

#### Script: Limpieza de Recursos

```bash
#!/bin/bash
# scripts/cleanup.sh

echo "Cleaning up old resources..."

# Limpiar pods completados
kubectl delete pods --all-namespaces --field-selector=status.phase=Succeeded

# Limpiar jobs completados (más de 1 día)
kubectl delete jobs --all-namespaces --field-selector=status.successful=1

# Limpiar logs antiguos de Airflow (variables)
kubectl exec -n data deployment/airflow-webserver -- \
  airflow db clean --clean-before-timestamp "$(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%S)" \
  --tables log \
  --skip-archive \
  --yes

# Limpiar imágenes no usadas en nodes
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | \
  while read node; do
    kubectl debug node/"$node" -it --image=busybox -- \
      sh -c "crictl rmi --prune"
  done

echo "Cleanup completed"
```

### 🚨 Troubleshooting por Síntoma

#### Síntoma: Workflows no se ejecutan

**Posibles causas y soluciones:**

1. **Scheduler no está corriendo**
```bash
kubectl get pods -n workflows -l app=kestra-scheduler
kubectl logs -n workflows deployment/kestra-scheduler
```

2. **Falta configuración de triggers**
```bash
# Verificar triggers configurados
kubectl exec -n workflows deployment/kestra -- \
  kestra triggers list
```

3. **Variables no configuradas**
```bash
# Verificar variables requeridas
kubectl exec -n workflows deployment/kestra -- \
  kestra variables list
```

#### Síntoma: DAGs de Airflow fallan constantemente

**Diagnóstico:**

```bash
# Ver errores de importación
kubectl exec -n data deployment/airflow-webserver -- \
  airflow dags list-import-errors

# Ver logs de scheduler
kubectl logs -n data deployment/airflow-scheduler --tail=100

# Verificar conexiones de base de datos
kubectl exec -n data deployment/airflow-webserver -- \
  airflow connections list

# Verificar variables requeridas
kubectl exec -n data deployment/airflow-webserver -- \
  airflow variables list | grep -i required
```

#### Síntoma: Alto uso de CPU/Memoria

**Diagnóstico y solución:**

```bash
# Identificar pods consumidores
kubectl top pods -A --sort-by=cpu | head -10
kubectl top pods -A --sort-by=memory | head -10

# Verificar HPA
kubectl get hpa -A

# Escalar manualmente si es necesario
kubectl scale deployment -n <namespace> <deployment> --replicas=<number>

# Verificar límites de recursos
kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Limits"
```

### 📋 Quick Reference Cards

#### Comandos Kubernetes Esenciales

```bash
# Namespaces
kubectl get namespaces
kubectl create namespace <name>
kubectl delete namespace <name>

# Pods
kubectl get pods -A
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> -f
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Deployments
kubectl get deployments -A
kubectl scale deployment <name> -n <namespace> --replicas=<n>
kubectl rollout restart deployment <name> -n <namespace>

# Services
kubectl get services -A
kubectl get ingress -A

# ConfigMaps y Secrets
kubectl get configmaps -A
kubectl get secrets -A
kubectl edit configmap <name> -n <namespace>
```

#### Comandos Airflow

```bash
# Listar DAGs
kubectl exec -n data deployment/airflow-webserver -- airflow dags list

# Pausar/Despausar DAG
kubectl exec -n data deployment/airflow-webserver -- \
  airflow dags pause <dag_id>
kubectl exec -n data deployment/airflow-webserver -- \
  airflow dags unpause <dag_id>

# Trigger DAG manualmente
kubectl exec -n data deployment/airflow-webserver -- \
  airflow dags trigger <dag_id>

# Ver logs de tarea
kubectl exec -n data deployment/airflow-webserver -- \
  airflow tasks logs <dag_id> <task_id> <execution_date>

# Listar variables
kubectl exec -n data deployment/airflow-webserver -- \
  airflow variables list
```

#### Comandos Kestra

```bash
# Listar flows
curl http://kestra.example.com/api/v1/flows

# Ejecutar flow manualmente
curl -X POST http://kestra.example.com/api/v1/executions/trigger/<namespace>/<flow-id> \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"key": "value"}}'

# Ver ejecuciones
curl http://kestra.example.com/api/v1/executions?namespace=<namespace>

# Ver logs de ejecución
curl http://kestra.example.com/api/v1/executions/<execution-id>/logs
```

#### Comandos Camunda

```bash
# Listar procesos
curl http://camunda.example.com/engine-rest/process-definition

# Iniciar proceso
curl -X POST http://camunda.example.com/engine-rest/process-definition/key/<process-key>/start \
  -H "Content-Type: application/json" \
  -d '{"variables": {"key": {"value": "value", "type": "String"}}}'

# Ver instancias activas
curl http://camunda.example.com/engine-rest/process-instance?active=true

# Ver tareas externas
curl http://camunda.example.com/engine-rest/external-task
```

### 🔗 Enlaces Rápidos de Documentación

| Recurso | URL/Comando |
|---------|-------------|
| **Grafana** | `kubectl port-forward -n observability service/grafana 3000:80` |
| **Prometheus** | `kubectl port-forward -n observability service/prometheus 9090:9090` |
| **Kestra UI** | `kubectl port-forward -n workflows service/kestra 8080:8080` |
| **Airflow UI** | `kubectl port-forward -n data service/airflow-webserver 8080:8080` |
| **Camunda Cockpit** | `http://camunda.example.com/camunda/app/cockpit` |
| **Documentación ETL** | `data/airflow/dags/INDEX_ETL_IMPROVED.md` |
| **Sistema de KPIs** | `docs/KPI_SYSTEM.md` |
| **Guía de Workflows** | `workflow/README.md` |

## 📖 Casos de Uso

### Workflow: ManyChat → HubSpot + DB + Scoring

**Archivo**: `workflow/kestra/flows/leads_manychats_to_hubspot.yaml`

**Pasos**:
1. Exponga Kestra por Ingress y obtenga URL base
2. Cargue el flow en Kestra y copie la URL del webhook generado
3. Configure el Webhook en ManyChat apuntando a esa URL
4. Defina variables: `hubspot_token`, `jdbc_url`, `jdbc_user`, `jdbc_password`
5. Ejecute `data/db/schema.sql` en su base de datos

**Flujo**: Recibe payload de ManyChat → calcula score → upsert a HubSpot → upsert a BD → actualiza lifecycle

### Automatización: HubSpot → ManyChat (Envío de Mensajes)

**Archivo**: `workflow/kestra/flows/hubspot_lead_to_manychat.yaml`

**Pasos**:
1. Configurar External Secrets para ManyChat API key:
   ```bash
   kubectl apply -f security/secrets/externalsecrets-manychat.yaml
   ```
2. Aplicar Ingress para Kestra webhooks (ver `kubernetes/ingress/kestra-ingress.yaml`)
3. Cargar flow en Kestra:
   ```bash
   # Desde UI de Kestra: Flows → Create → Paste contenido de hubspot_lead_to_manychat.yaml
   # O vía API
   curl -X POST http://kestra.example.com/api/v1/flows \
     -H "Content-Type: application/json" \
     -u admin:admin \
     -d @workflow/kestra/flows/hubspot_lead_to_manychat.yaml
   ```
4. Configurar variables en Kestra (o usar External Secrets):
   - `manychat_api_key`: Desde secret `manychat-api-key`
   - `hubspot_token`: Desde secret `hubspot-token` (ya configurado)
   - `hubspot_webhook_secret`: (Opcional) Para verificación de webhooks
5. Configurar webhook en HubSpot:
   - URL: `https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_lead_to_manychat/hubspot-lead`
   - Eventos: `contact.creation` y `contact.propertyChange` (filtrado por propiedad `interés_producto`)
6. Asegurar que los contactos tengan propiedades:
   - `interés_producto`: Valor del producto de interés
   - `manychat_user_id`: ID del usuario en ManyChat

**Flujo**: HubSpot crea/actualiza lead con `interés_producto` con valor → Webhook dispara flow → Valida datos → Envía mensaje a ManyChat: "Hola {nombre}, gracias por tu interés en {producto}. ¿Te gustaría agendar una demo?" → Retorna estado (sent/error/skipped)

**Documentación completa**: Ver `workflow/kestra/flows/README.md`

### Automatización: Stripe → Google Sheets + DB + AI

**Archivo**: `workflow/kestra/flows/stripe_payments_to_sheets_db_ai.yaml`

**Pasos**:
1. Cree la tabla `payments` ejecutando `data/db/payments.sql`
2. Importe el flow en Kestra y exponga el webhook `stripe_webhook`
3. Configure un endpoint de webhook en Stripe (evento: `payment_intent.succeeded`)
4. Provea variables: `jdbc_url`, `jdbc_user`, `jdbc_password`, `sheets_webhook_url`, `openai_api_key`

**Funcionalidad**:
- Registra el pago en la tabla `payments`
- Envía datos a Google Sheets mediante webhook
- Llama a OpenAI para interpretación y pronóstico usando últimos 30 días

### Automatización: WhatsApp Ticket → Sheets + Documento

**Archivo**: `workflow/kestra/flows/whatsapp_ticket_to_sheet_doc.yaml`

**Pasos**:
1. Exponga Kestra y configure el webhook `whatsapp_webhook` como endpoint
2. Provea inputs: `openai_api_key`, `sheets_webhook_url`, `docs_webhook_url`
3. Envíe una foto de un ticket al WhatsApp configurado

**Funcionalidad**: Extrae proveedor, fecha, total, moneda, items → agrega a Google Sheets → genera documento para contabilidad

### Automatización: Programación Automática de Reuniones

**Archivo**: `workflow/kestra/flows/meeting_scheduler_automatic.yaml`

**Pasos**:
1. Exponga Kestra y configure el webhook `meeting_scheduler`
2. Configure inputs: `calendar_api_url`, `calendar_api_token`, `email_api_url`, `email_api_key`
3. Opcional: Configure `database_url`, `slack_webhook_url`, `webhook_secret`
4. Envíe solicitud de reunión via POST al webhook

**Payload de ejemplo**:
```json
{
  "organizer_email": "juan@example.com",
  "attendees": ["maria@example.com", "pedro@example.com"],
  "subject": "Reunión de seguimiento Q1",
  "duration_minutes": 30,
  "preferred_date": "2025-02-15",
  "preferred_times": ["14:00", "16:00"]
}
```

**Funcionalidad**:
- ✅ Recibe solicitud de reunión → valida datos → verifica disponibilidad
- ✅ Selecciona mejor horario según preferencias → crea evento en calendario
- ✅ Genera archivo iCal (.ics) → envía invitaciones con adjunto
- ✅ Programa recordatorios automáticos → notifica en Slack (opcional)
- ✅ Persiste reunión en base de datos para tracking

**Características principales**:
- Elimina el "ping-pong" de correos para agendar citas
- Soporte multi-calendario (Google Calendar, Outlook, CalDAV)
- Detección automática de conflictos y duplicados
- Buffer time configurable entre reuniones
- Recordatorios automáticos personalizables

Ver `workflow/kestra/flows/README_MEETING_SCHEDULER.md` para documentación detallada, ejemplos y troubleshooting.

### Dashboard de KPIs en Tiempo Real (Grafana)

**Configuración**:
- Datasource: `observability/grafana/datasources/postgres.yaml`
- Dashboard: `observability/grafana/dashboards/kpi.json`

**KPIs incluidos**:
- Ingresos (1h, 24h), ingresos por hora (24h), pagos/leads recientes
- Leads por prioridad (hoy), conversión 7d (leads→pagos)
- Salud: tasa 5xx de Ingress y reinicios de pods

## 🛠️ Operación y Mantenimiento

### Comandos Útiles

```bash
# Infraestructura
make tf-init TF_DIR=infra/terraform
make tf-plan TF_DIR=infra/terraform
make tf-apply TF_DIR=infra/terraform
make tf-fmt TF_DIR=infra/terraform
make tf-validate TF_DIR=infra/terraform

# Kubernetes
make k8s-namespaces
make k8s-ingress
make k8s-integration
make k8s-kafka
make k8s-kafka-topics
make k8s-connect

# Helmfile
make helmfile-apply
make helmfile-diff

# Kustomize
make kustomize-dev
make kustomize-stg
make kustomize-prod

# Desarrollo local (Airflow)
make airflow-up
make airflow-down
make airflow-init

# Validación de código
make py-lint
make py-format
make js-lint
make js-format
make js-typecheck
make all-checks

# Tests
make py-test
make js-test
```

### Gestión de Recursos

- **LimitRanges y ResourceQuotas**: `security/kubernetes/limitranges-quotas.yaml`
- **Pod Disruption Budgets**: `kubernetes/integration/healthz-pdb.yaml`
- **Horizontal Pod Autoscaler**: `kubernetes/integration/healthz-hpa.yaml`

### Observabilidad

- **Métricas**: ServiceMonitors en `observability/servicemonitors/`
- **Alertas**: Reglas en `observability/prometheus/alertrules.yaml`
- **Costes**: OpenCost en `observability/opencost/values.yaml`

### Backups

- **Velero**: Configuración en `backup/velero/values.yaml`

### Lifecycle de Data Lake

- Configuración S3 lifecycle en Terraform (`infra/terraform/main.tf`)

## 🔐 Seguridad

### External Secrets Operator

Gestión automática de secretos desde:

- **AWS**: `security/secrets/externalsecrets-aws.yaml` (requiere IRSA/role y ESO instalado)
- **Azure**: `security/secrets/externalsecrets-azure.yaml` (requiere Workload Identity/Key Vault y ESO)

### Certificados TLS

**cert-manager**:
1. Instalar con `helmfile apply`
2. Aplicar `security/cert-manager/clusterissuer.yaml`
3. En el Ingress, usar `cert-manager.io/cluster-issuer: letsencrypt-prod`

### Autenticación OIDC

**oauth2-proxy**:
1. Ajustar `security/oauth2-proxy/values.yaml` con su IdP
2. Desplegar el chart oauth2-proxy
3. Habilitar anotaciones `auth-url`/`auth-signin` en `api-gateway`

### Network Policies

Políticas base en `security/networkpolicies/baseline.yaml` (deny-all ingress + DNS egress). Amplíe según servicios necesarios.

### Políticas OPA Gatekeeper

- **Requests/Limits obligatorios**: `security/policies/gatekeeper/limits.yaml`
- **Etiqueta `cost-center` obligatoria**: `security/policies/gatekeeper/cost-center.yaml`
- **Sin imágenes `latest`**: `security/policies/gatekeeper/no-latest.yaml`

### RBAC

Configuración base en `security/kubernetes/rbac-baseline.yaml`.

## 📚 Documentación Adicional

### Documentación por Área

- **Índice General**: `docs/INDEX.md`
- **Sistema de KPIs**: `docs/KPI_SYSTEM.md` (dashboards, reportes, alertas, métricas en tiempo real)
- **Integraciones de Analítica**: `data/INTEGRATIONS.md`
- **MLOps**: `ml/kubeflow/README.md`, `ml/training/README.md`
- **Workflows**: `workflow/kestra/`, `workflow/camunda/README_worker.md`
- **RPA**: `rpa/OPENRPA.md`
- **Airflow**: `data/airflow/README.md`, `data/airflow/dags/INDEX_ETL_IMPROVED.md`
- **Employee Onboarding**: `data/airflow/README_onboarding.md` (guía completa de configuración y uso)
- **Seguridad**: `security/README.md`
- **Grafana**: `observability/grafana/dashboards/README.md`

### Referencias Rápidas

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| Employee Onboarding (Airflow) | `data/airflow/dags/employee_onboarding.py` | DAG de onboarding con validación robusta e integración HRIS |
| Employee Onboarding (Kestra) | `workflow/kestra/flows/employee_onboarding.yaml` | Flow completo con persistencia PostgreSQL |
| Employee Onboarding (Camunda) | `workflow/camunda/onboarding_employee.bpmn` | BPMN con aprobación de manager |
| Camunda Zeebe Worker | `workflow/camunda/worker/zeebe_worker.py` | Worker que conecta Camunda con Airflow |
| Kestra | `workflow/kestra/deployment.yaml` | Orquestación de workflows |
| Flowable | `workflow/flowable/deployment.yaml` | Motor BPM |
| OpenRPA | `rpa/OPENRPA.md` | Automatización RPA |
| Kubeflow | `ml/kubeflow/README.md` | ML pipelines |
| MLflow/KServe | `ml/` | Tracking y serving de modelos |

### CI/CD

- **Terraform PR checks**: `.github/workflows/infra.yaml` (fmt/validate/plan)
- **Deploy manual a K8s**: `.github/workflows/deploy.yaml` (requiere `KUBECONFIG_B64` en secrets)

## 👥 Guías de Onboarding

### Para Desarrolladores Nuevos

1. **Configurar ambiente local**:
```bash
# Clonar repositorio
git clone <repo-url>
cd IA

# Configurar variables de entorno
cp environments/dev.yaml.example environments/dev.yaml
# Editar con tus valores

# Inicializar Terraform
make tf-init TF_DIR=infra/terraform
```

2. **Ejecutar primeros workflows**:
```bash
# Probar DAG básico
airflow dags test etl_example

# Cargar workflow de Kestra
kubectl apply -f workflow/kestra/flows/leads_manychats_to_hubspot.yaml
```

3. **Leer documentación clave**:
- ETL: `data/airflow/dags/INDEX_ETL_IMPROVED.md`
- Workflows: `workflow/kestra/README.md`
- KPIs: `docs/KPI_SYSTEM.md`

### Para Operaciones

1. **Monitoreo básico**:
```bash
# Ver estado de componentes
kubectl get pods -A

# Ver logs de Airflow
kubectl logs -n airflow deployment/airflow-webserver -f

# Ver métricas en Grafana
# Acceder a: http://grafana.your-domain.com
```

2. **Health checks**:
```bash
# Airflow
airflow tasks test etl_example health_check $(date +%Y-%m-%d)

# Kestra
curl http://kestra.your-domain.com/health
```

3. **Gestión de secretos**:
```bash
# Ver secrets sincronizados
kubectl get externalsecrets -A

# Forzar resincronización
kubectl delete externalsecret <name> -n <namespace>
```

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. DAGs de Airflow no se ejecutan

```bash
# Verificar errores de importación
airflow dags list-import-errors

# Verificar variables y conexiones
airflow variables list
airflow connections list

# Verificar estado de scheduler
kubectl logs -n airflow deployment/airflow-scheduler
```

#### 2. Workflows de Kestra fallan

```bash
# Ver logs de ejecuciones
kubectl logs -n workflows deployment/kestra

# Verificar configuración
kubectl get configmap -n workflows

# Verificar webhooks
curl http://kestra.your-domain.com/webhook/<flow-key>
```

#### 2.1. Employee Onboarding falla

```bash
# Verificar logs del DAG de Airflow
kubectl logs -n airflow deployment/airflow-scheduler | grep employee_onboarding

# Verificar progreso guardado en Variables
airflow variables get onboarding_runs:<email>

# Verificar idempotency locks
airflow variables list | grep idemp:employee_onboarding

# Verificar configuración de integraciones
kubectl get configmap -n airflow | grep onboarding
kubectl get secrets -n airflow | grep onboarding

# Probar trigger manual
airflow dags trigger employee_onboarding \
  --conf '{"employee_email":"test@example.com","full_name":"Test User","start_date":"2025-01-01","manager_email":"manager@example.com"}'
```

#### 3. Problemas de conectividad

```bash
# Verificar network policies
kubectl get networkpolicies -A

# Verificar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup <service>

# Verificar conectividad a bases de datos
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql -h <host> -U <user> -d <db>
```

#### 4. Métricas no aparecen en Prometheus

```bash
# Verificar ServiceMonitors
kubectl get servicemonitor -A

# Verificar targets en Prometheus UI
# Navegar a: Status → Targets

# Verificar que el servicio expone /metrics
curl http://airflow-scheduler.data.svc.cluster.local/metrics

# Ver logs del Prometheus operator
kubectl logs -n observability -l app.kubernetes.io/name=prometheus-operator
```

#### 5. Logs no aparecen en Kibana

```bash
# Verificar Fluent Bit
kubectl get pods -n observability -l app=fluent-bit
kubectl logs -n observability -l app=fluent-bit

# Verificar índices en Elasticsearch
curl http://elasticsearch.observability.svc:9200/_cat/indices

# Verificar configuración de Fluent Bit
kubectl get configmap -n observability fluent-bit-config -o yaml
```

#### 6. Dashboard de Grafana vacío

```bash
# Verificar datasources
kubectl get configmap -n observability -l grafana_datasource

# Probar query en Prometheus directamente
# En Prometheus UI: probar la query que usa el dashboard

# Verificar que los dashboards están importados
# En Grafana UI: Configuration → Dashboards
```

#### 7. Alertas no se disparan

```bash
# Verificar reglas de alerta
kubectl get prometheusrules -n observability

# Verificar que las métricas existen
# En Prometheus UI: ejecutar la query de la alerta

# Verificar Alertmanager
kubectl get pods -n observability -l app=alertmanager
kubectl logs -n observability -l app=alertmanager

# Verificar configuración de notificaciones
kubectl get secret -n observability alertmanager-prometheus-kube-prometheus-alertmanager -o yaml
```

#### 8. Problemas de recursos

```bash
# Ver uso de recursos
kubectl top nodes
kubectl top pods -A

# Ver límites y quotas
kubectl describe limitrange -n <namespace>
kubectl describe resourcequota -n <namespace>
```

#### 5. Problemas de secretos

```bash
# Verificar External Secrets
kubectl get externalsecrets -A
kubectl describe externalsecret <name> -n <namespace>

# Verificar sincronización
kubectl get secrets -n <namespace>

# Forzar resincronización
kubectl delete externalsecret <name> -n <namespace>
```

## 📊 Métricas y Monitoreo

### Stack de Observabilidad Completo

La plataforma incluye una pila completa de observabilidad para monitoreo proactivo y detección de problemas:

#### Prometheus - Métricas
- **ServiceMonitors configurados** para:
  - Airflow (scheduler y workers)
  - Kestra workflows
  - Camunda y Flowable procesos BPMN
  - APIs y servicios de integración
- **Métricas recolectadas**:
  - DAG runs (éxitos, fallos, en ejecución)
  - Tareas por estado y duración (percentiles p50, p95, p99)
  - Throughput y latencia
  - Queue lengths y backlog
  - Health checks de componentes

#### Grafana - Visualización
- **Dashboards principales**:
  - Monitoreo de Automatizaciones: Estado de DAGs, tasa de éxito, duración de tareas
  - KPIs de Negocio: Ingresos, leads, conversión
  - APIs HTTP: Requests, latencia, errores
  - ETL Mejorado: Métricas de pipeline, throughput, calidad de datos
- **Datasources**:
  - Prometheus (métricas)
  - PostgreSQL (datos de negocio)
  - Elasticsearch (logs centralizados)
  - Loki (logs recientes)

#### ELK Stack - Logging
- **Elasticsearch**: Almacenamiento de logs con ILM (Index Lifecycle Management)
  - Retención: 30 días en hot tier
  - Búsqueda rápida y analítica avanzada
- **Kibana**: Visualización y búsqueda de logs
  - Búsqueda por namespace, componente, nivel de log
  - Visualizaciones personalizadas
- **Fluent Bit**: Recolector de logs (DaemonSet)
  - Recolección automática de todos los contenedores
  - Enriquecimiento con metadata de Kubernetes
  - Envío a Elasticsearch
- **Logstash**: Procesamiento y transformación de logs (opcional)

#### Alertas Configuradas

Prometheus AlertManager está configurado con alertas críticas y de advertencia:

**Críticas**:
- `AirflowDagRunFailed`: DAG run falló
- `AirflowSchedulerLag`: Scheduler no saludable
- `HighErrorRate`: Más del 5% de respuestas 5xx
- `PodCrashLooping`: Reinicios repetidos

**Advertencias**:
- `AirflowTaskFailed`: Múltiples tareas fallaron
- `HighTaskDuration`: P95 de duración > 30 minutos
- `AutomationQueueBacklog`: >50 DAG runs en cola
- `LowDailyLeads`: Leads diarios bajos
- `LowRevenueVsAvg7d`: Ingresos < 70% del promedio

### Acceso a Observabilidad

```bash
# Prometheus
kubectl port-forward -n observability svc/prometheus-operated 9090:9090
# http://localhost:9090

# Grafana
kubectl port-forward -n observability svc/prometheus-grafana 3000:80
# http://localhost:3000 (admin/admin por defecto)

# Kibana
kubectl port-forward -n observability svc/kibana-kibana 5601:5601
# http://localhost:5601
```

### Búsqueda de Logs

**En Kibana**:
```
# Logs de Airflow con errores
kubernetes.namespace_name:data AND automation_type:airflow AND level:ERROR

# Logs de workflows fallidos
automation_type:workflow AND (state:FAILED OR state:ERROR)

# Logs por componente
kubernetes.labels.app:airflow OR kubernetes.labels.app:kestra
```

**En Grafana (Loki)**:
```logql
# Logs estructurados de Airflow
{namespace="data", container="airflow-worker"} | json | status="failed"

# Errores recientes
{namespace="data"} |= "ERROR" | count_over_time(5m)
```

### Métricas Clave a Monitorear

**Airflow**:
- `airflow_dag_run_status{status="success"}` - DAGs exitosos
- `airflow_dag_run_status{status="failed"}` - DAGs fallidos
- `airflow_task_duration_seconds` - Duración de tareas (histograma)
- `airflow_dag_run_queue_length` - DAGs en cola
- `airflow_scheduler_heartbeat` - Salud del scheduler

**ETL Específico**:
- `etl_example_total_duration_ms` - Duración total del DAG
- `etl_example_throughput_rows_per_sec` - Throughput
- `etl_example_dq_null_rate_exceeded_total` - Fallos de calidad de datos

**Workflows**:
- `kestra_executions_total` - Total de ejecuciones
- `kestra_executions_failed_total` - Ejecuciones fallidas
- `camunda_process_instances_active` - Procesos activos

### Monitoreo Proactivo

1. **Configurar alertas críticas**: Integrar con Slack/PagerDuty/Email
2. **Revisar dashboards diariamente**: Detectar tendencias y anomalías temprano
3. **Análisis de logs**: Buscar patrones de errores recurrentes
4. **Optimización continua**: Ajustar thresholds y métricas según necesidad

## 📊 Métricas y Monitoreo (Legacy)

### Dashboards Disponibles

#### Grafana

- **ETL Dashboard**: Métricas de pipelines ETL (duración, throughput, errores)
- **KPI Dashboard**: KPIs en tiempo real (revenue, leads, conversión)
- **Infrastructure Dashboard**: Uso de recursos, salud de pods, network
- **Cost Dashboard**: Análisis de costes con OpenCost

#### Prometheus

- **Métricas de Airflow**: Exportadas automáticamente
- **Métricas de Kestra**: Via ServiceMonitor
- **Métricas personalizadas**: Vía Stats API de Airflow

### Alertas Configuradas

- **SLA Misses**: DAGs que exceden tiempo objetivo
- **Failures**: DAGs con tasa de fallo > 5%
- **Resource Exhaustion**: CPU/Memory > 80%
- **Circuit Breaker Open**: Servicios externos caídos
- **Rate Limit Hits**: APIs alcanzando límites

### Comandos de Monitoreo

```bash
# Ver métricas de Prometheus
curl http://prometheus.your-domain.com/api/v1/query?query=etl_dag_success_total

# Exportar métricas de Airflow
airflow dags show etl_example | grep metrics

# Ver logs estructurados
kubectl logs -n airflow deployment/airflow-webserver | jq .
```

## 🎯 Mejores Prácticas

### Desarrollo

1. **Nunca commitee secretos**: Use External Secrets Operator
2. **Valide antes de aplicar**: 
   ```bash
   make tf-validate
   make kustomize-validate-dev
   ```
3. **Use overlays por entorno**: Separe configuraciones dev/stg/prod
4. **Testing local primero**: 
   ```bash
   make airflow-up  # Levantar Airflow local
   airflow dags test <dag_id>
   ```
5. **Documenta cambios**: Actualiza documentación con cada feature nueva

### Operaciones

1. **Monitoree costes**: Revise OpenCost regularmente
   ```bash
   # Acceder a OpenCost UI
   kubectl port-forward -n opencost service/opencost 9003:9003
   ```
2. **Aplique políticas de seguridad**: Habilite Gatekeeper y Network Policies
3. **Backups regulares**: Configure Velero para backups automáticos
4. **Mantenga logs estructurados**: Use logging estructurado en todos los componentes
5. **Revise métricas semanalmente**: Identifique tendencias y optimizaciones

### Seguridad

1. **Principio de menor privilegio**: RBAC mínimo necesario
2. **Rotación de secretos**: Automatizar rotación cada 90 días
3. **Escaneo de imágenes**: Integrar en CI/CD pipeline
4. **Network Policies**: Aplicar deny-all por defecto
5. **Auditoría**: Habilitar auditoría de Kubernetes API

### Performance

1. **Chunking adaptativo**: Usar en pipelines ETL grandes
2. **Rate limiting**: Configurar según límites de APIs externas
3. **Circuit breakers**: Para servicios externos críticos
4. **Caching**: Cachear resultados de queries frecuentes
5. **Índices de BD**: Mantener índices optimizados para queries frecuentes

## 💻 Ejemplos Prácticos con Código

### Ejemplo 1: Crear un DAG de Airflow Simple

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def hello_world():
    print("Hello from Airflow!")

with DAG(
    dag_id="mi_primer_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id="hello",
        python_callable=hello_world,
    )
```

**Guardar en**: `data/airflow/dags/mi_primer_dag.py`

### Ejemplo 2: Crear un Workflow de Kestra

```yaml
id: mi_primer_workflow
namespace: workflows

description: Ejemplo básico de workflow

tasks:
  - id: hello
    type: io.kestra.plugin.scripts.shell.Commands
    commands:
      - echo "Hello from Kestra!"

triggers:
  - id: schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 * * *"  # Diario a las 9 AM
```

**Guardar en**: `workflow/kestra/flows/mi_primer_workflow.yaml`

### Ejemplo 3: Health Check Endpoint

```python
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

@app.route('/health')
def health():
    try:
        # Check DB connection
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            connect_timeout=5
        )
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Ejemplo 4: Script de Monitoreo Simple

```bash
#!/bin/bash
# monitoreo.sh - Health check básico

# Verificar pods
echo "=== Estado de Pods ==="
kubectl get pods -A | grep -E "(Error|CrashLoop|Pending)"

# Verificar recursos
echo "=== Uso de Recursos ==="
kubectl top nodes

# Verificar servicios
echo "=== Servicios ==="
kubectl get svc -A | grep -E "(Error|Pending)"

# Verificar logs recientes con errores
echo "=== Errores Recientes ==="
kubectl logs -n airflow deployment/airflow-webserver --tail=100 | grep -i error
```

## 📈 Escalabilidad y Optimización

### Cuándo Escalar

| Métrica | Umbral | Acción |
|---------|--------|--------|
| CPU promedio > 70% | 5 minutos | Aumentar replicas o recursos |
| Memoria > 80% | 5 minutos | Aumentar límites de memoria |
| Latencia p95 > SLA | 10 minutos | Investigar cuello de botella |
| Rate limit hits > 10/hora | Inmediato | Aumentar rate limits o instancias |
| Queue depth > 100 | 15 minutos | Aumentar workers |

### Configurar Auto-Scaling

#### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: airflow-worker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: airflow-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Optimización de Base de Datos

```sql
-- Índices estratégicos para queries frecuentes
CREATE INDEX CONCURRENTLY idx_events_created_at 
ON etl_improved_events(created_at DESC);

CREATE INDEX CONCURRENTLY idx_events_status_created
ON etl_improved_events(status, created_at DESC)
WHERE status IN ('pending', 'processing');

-- Particionamiento por fecha (para grandes volúmenes)
CREATE TABLE etl_events_2025_01 PARTITION OF etl_improved_events
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Vacuum automático (PostgreSQL)
ALTER TABLE etl_improved_events SET (
  autovacuum_vacuum_scale_factor = 0.05,
  autovacuum_analyze_scale_factor = 0.02
);
```

### Optimización de Chunking ETL

```python
# Calcular chunk size óptimo basado en memoria disponible
import os

def calculate_optimal_chunk_size(available_memory_mb: int, row_size_kb: float = 1.0) -> int:
    """
    Calcula chunk size óptimo considerando:
    - Memoria disponible
    - Tamaño promedio de fila
    - Overhead de procesamiento (2x)
    """
    # Dejar 20% de memoria libre
    usable_memory_mb = available_memory_mb * 0.8
    
    # Convertir a KB
    usable_memory_kb = usable_memory_mb * 1024
    
    # Calcular rows posibles (con overhead 2x)
    max_rows = int((usable_memory_kb / row_size_kb) / 2)
    
    # Limitar entre 100 y 10000
    return max(100, min(10000, max_rows))

# Uso
chunk_size = calculate_optimal_chunk_size(
    available_memory_mb=int(os.getenv('MEMORY_LIMIT_MB', '4096'))
)
```

## 🏭 Casos de Uso por Industria

### Fintech / Finanzas

**Use Cases**:
- Reconciliación automática de pagos
- Detección de fraude en tiempo real
- Reportes regulatorios automatizados
- Onboarding de clientes KYC/AML

**Componentes Clave**:
- `stripe_reconcile.py`, `bank_reconcile.py`
- `financial_reports.py`
- Circuit breakers para APIs de pagos
- Audit logs completos

### E-commerce / Retail

**Use Cases**:
- Sincronización de inventario
- Procesamiento de órdenes
- Análisis de comportamiento de clientes
- Optimización de pricing dinámico

**Componentes Clave**:
- ETL pipelines para datos de ventas
- Integraciones con sistemas de inventario
- Análisis con MLflow
- Dashboards de KPIs

### SaaS / B2B

**Use Cases**:
- Onboarding automatizado de clientes
- Nutrición de leads
- Reconciliación de suscripciones
- Reportes de uso y billing

**Componentes Clave**:
- `outreach_multichannel.py`
- `employee_onboarding.py`
- `invoice_generate.py`
- Workflows de Kestra para integraciones

### Healthcare / Salud

**Use Cases**:
- Procesamiento de claims
- Integración con sistemas EHR
- Cumplimiento HIPAA
- Análisis de resultados clínicos

**Componentes Clave**:
- Encriptación end-to-end
- Audit trails completos
- Redundancia y backups
- Network policies estrictas

### Manufacturing / Producción

**Use Cases**:
- Monitoreo de IoT devices
- Mantenimiento predictivo
- Optimización de supply chain
- Control de calidad automatizado

**Componentes Clave**:
- Kafka para streams de IoT
- ML para predicción de fallos
- RPA para procesos repetitivos
- Integración con sistemas MES/ERP

## 🏥 Health Checks Avanzados

### Health Check Completo de Plataforma

```bash
#!/bin/bash
# platform-health-check.sh

echo "=== Platform Health Check ==="
echo "Fecha: $(date)"
echo ""

# 1. Kubernetes Cluster
echo "1. Kubernetes Cluster"
kubectl cluster-info --request-timeout=5s
if [ $? -eq 0 ]; then
    echo "✅ Cluster accesible"
else
    echo "❌ Cluster inaccesible"
    exit 1
fi

# 2. Componentes Principales
echo ""
echo "2. Componentes Principales"
components=("airflow-webserver" "kestra" "prometheus" "grafana")
for comp in "${components[@]}"; do
    if kubectl get deployment -n $(kubectl get namespaces -o name | grep -E "(airflow|workflows|observability)" | cut -d/ -f2) $comp &>/dev/null; then
        replicas=$(kubectl get deployment -n $(kubectl get namespaces -o name | grep -E "(airflow|workflows|observability)" | cut -d/ -f2) $comp -o jsonpath='{.status.readyReplicas}/{.spec.replicas}')
        echo "  ✅ $comp: $replicas replicas listas"
    else
        echo "  ⚠️  $comp: No encontrado"
    fi
done

# 3. Recursos del Sistema
echo ""
echo "3. Recursos del Sistema"
echo "  CPU:"
kubectl top nodes --no-headers | awk '{print "    " $1 ": " $2 "% CPU, " $4 "% Memory"}'

# 4. Pods con Problemas
echo ""
echo "4. Pods con Problemas"
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers | head -5

# 5. Services
echo ""
echo "5. Servicios Críticos"
services=("airflow-webserver" "kestra" "prometheus")
for svc in "${services[@]}"; do
    if kubectl get svc -A | grep -q $svc; then
        echo "  ✅ $svc: Disponible"
    else
        echo "  ❌ $svc: No encontrado"
    fi
done

# 6. Base de Datos
echo ""
echo "6. Conectividad de Base de Datos"
if kubectl run -it --rm db-check --image=postgres:15 --restart=Never -- psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1" &>/dev/null; then
    echo "  ✅ Base de datos accesible"
else
    echo "  ❌ Base de datos inaccesible"
fi

echo ""
echo "=== Health Check Completado ==="
```

### Health Check de Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import requests
import psycopg2
import os

def check_airflow_api():
    """Verifica que Airflow API responda"""
    try:
        resp = requests.get('http://airflow-webserver:8080/health', timeout=5)
        assert resp.status_code == 200
        print("✅ Airflow API OK")
    except Exception as e:
        raise Exception(f"❌ Airflow API error: {e}")

def check_database():
    """Verifica conectividad a base de datos"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN').split('@')[1].split('/')[0],
            database=os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN').split('/')[-1],
            connect_timeout=5
        )
        conn.close()
        print("✅ Database OK")
    except Exception as e:
        raise Exception(f"❌ Database error: {e}")

with DAG(
    'health_check',
    schedule_interval='*/5 * * * *',  # Cada 5 minutos
    start_date=days_ago(1),
    catchup=False,
) as dag:
    check_api = PythonOperator(
        task_id='check_airflow_api',
        python_callable=check_airflow_api,
    )
    
    check_db = PythonOperator(
        task_id='check_database',
        python_callable=check_database,
    )
    
    check_api >> check_db
```

## 💾 Backup y Disaster Recovery

### Estrategia de Backup

#### 1. Backups de Base de Datos

```bash
#!/bin/bash
# backup-database.sh

# Backup PostgreSQL
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    -F c -f /backups/db_$(date +%Y%m%d_%H%M%S).dump

# Backup a S3
aws s3 cp /backups/db_*.dump s3://backup-bucket/database/ --storage-class STANDARD_IA

# Retención: mantener últimos 30 días
find /backups -name "db_*.dump" -mtime +30 -delete
```

#### 2. Backups de Kubernetes con Velero

```bash
# Instalar Velero
velero install \
    --provider aws \
    --bucket velero-backups \
    --secret-file ./credentials-velero

# Backup completo del namespace
velero backup create airflow-backup \
    --include-namespaces airflow \
    --ttl 720h

# Restore
velero restore create --from-backup airflow-backup
```

#### 3. Backup de Configuraciones

```bash
#!/bin/bash
# backup-configs.sh

# Exportar Variables de Airflow
airflow variables export /backups/airflow_vars_$(date +%Y%m%d).json

# Exportar Connections
airflow connections export /backups/airflow_conns_$(date +%Y%m%d).json

# Backup de secrets
kubectl get secrets -A -o yaml > /backups/k8s_secrets_$(date +%Y%m%d).yaml

# Backup a repositorio Git
git add /backups/*
git commit -m "Backup config $(date +%Y%m%d)"
git push
```

### Disaster Recovery Plan

#### RTO/RPO por Componente

| Componente | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|------------|-------------------------------|-------------------------------|
| Airflow DAGs | 1 hora | 24 horas |
| Base de Datos | 30 minutos | 1 hora |
| Configuraciones | 15 minutos | 6 horas |
| Logs y Métricas | 4 horas | 7 días |
| Data Lake | 2 horas | 1 día |

#### Procedimiento de Recuperación

```bash
# 1. Evaluar daño
./platform-health-check.sh > damage-assessment.txt

# 2. Restaurar infraestructura (si necesario)
make tf-apply TF_DIR=infra/terraform

# 3. Restaurar base de datos
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    -c /backups/db_latest.dump

# 4. Restaurar configuraciones
airflow variables import /backups/airflow_vars_latest.json
airflow connections import /backups/airflow_conns_latest.json

# 5. Verificar recuperación
./platform-health-check.sh
```

## 🚀 Quick Wins (Para Empezar Rápido)

### En 15 Minutos: Primer Workflow

```bash
# 1. Levantar Kestra local
kubectl apply -f workflow/kestra/deployment.yaml
kubectl port-forward -n workflows service/kestra 8080:8080

# 2. Crear workflow simple (ver Ejemplos Prácticos)

# 3. Ejecutar y ver resultados
# Acceder a http://localhost:8080
```

### En 30 Minutos: Primer DAG de Airflow

```bash
# 1. Usar Airflow local
make airflow-up

# 2. Crear DAG (ver Ejemplos Prácticos)

# 3. Verificar en UI
# Acceder a http://localhost:8080/admin
```

### En 1 Hora: Pipeline ETL Completo

1. **Configurar base de datos**: Ejecutar `data/db/schema.sql`
2. **Crear DAG**: Copiar `etl_example.py` y adaptar
3. **Configurar variables**: En Airflow UI
4. **Ejecutar**: `airflow dags trigger etl_example`
5. **Ver métricas**: En Grafana dashboard

### Primer Mes: Automatizaciones Clave

- ✅ **Semana 1**: Setup básico y primer workflow
- ✅ **Semana 2**: Integrar fuente de datos principal
- ✅ **Semana 3**: Agregar notificaciones y alertas
- ✅ **Semana 4**: Optimizar y documentar

## 🤝 Contribución

### Proceso de Contribución

1. **Fork el repositorio** y clona tu fork
2. **Crea una rama** para tu feature/fix: `git checkout -b feature/mi-feature`
3. **Desarrolla y prueba** tus cambios
4. **Actualiza documentación** si es necesario
5. **Commitea** con mensajes descriptivos
6. **Push y crea Pull Request**

### Estándares de Código

- **Python**: Seguir PEP 8, usar type hints
- **TypeScript**: Seguir ESLint config, usar strict mode
- **Terraform**: Ejecutar `terraform fmt` antes de commit
- **Kubernetes**: Validar YAML con `kubectl apply --dry-run`

### Testing

```bash
# Tests de Python
pytest data/airflow/tests/

# Tests de TypeScript
cd web/kpis && npm test
cd web/kpis-next && npm test

# Validación de Terraform
make tf-validate

# Validación de Kubernetes
make kustomize-validate-dev
```

### Documentación

- Mantén READMEs actualizados
- Agrega ejemplos de uso
- Documenta breaking changes
- Actualiza `docs/INDEX.md` si agregas nueva documentación

## 📚 Guías de Referencia Rápida

### Comandos Comunes

```bash
# Infraestructura
make tf-init TF_DIR=infra/terraform
make tf-apply TF_DIR=infra/terraform

# Kubernetes
make k8s-namespaces
make k8s-ingress
make k8s-integration

# Airflow
airflow dags list
airflow dags trigger <dag_id>
airflow tasks test <dag_id> <task_id> <execution_date>

# Desarrollo local
make airflow-up  # Levantar Airflow con docker-compose
make airflow-down # Detener
```

### Enlaces Útiles

- **Documentación completa**: `docs/INDEX.md`
- **ETL Mejorado**: `data/airflow/dags/INDEX_ETL_IMPROVED.md`
- **KPIs**: `docs/KPI_SYSTEM.md`
- **Escalabilidad**: `docs/ESCALABILIDAD.md`
- **Integraciones**: `data/INTEGRATIONS.md`

## 🎓 Notas Importantes

> ⚠️ **Importante**: Las plantillas provistas son ejemplos; adapte valores a su organización y requisitos específicos.

### Soporte

- **Documentación completa**: Ver `docs/INDEX.md` para índice general
- **ETL Mejorado**: `data/airflow/dags/INDEX_ETL_IMPROVED.md` (v2.4)
  - ✅ Seguridad avanzada (validación, whitelists, SQL injection prevention)
  - ✅ Escalabilidad detallada (HPA, auto-scaling, optimización DB)
  - ✅ Optimización de costos (ROI, tuning, materialized views)
  - ✅ Ejemplos prácticos completos
- **Financiero**: `data/airflow/dags/INDEX_FINANCIAL.md`
- **KPIs**: `docs/KPI_SYSTEM.md`
- **Integraciones**: `data/INTEGRATIONS.md`
- **Issues**: Crear issue en el repositorio con label apropiado

### Roadmap

- ✅ Infraestructura multi-cloud (AWS/Azure)
- ✅ Orquestación con Kestra, Flowable, Camunda
- ✅ MLOps completo (MLflow, KServe, Kubeflow)
- ✅ Observabilidad completa (Prometheus, Grafana, ELK Stack, ServiceMonitors)
- ✅ Sistema de KPIs automatizado
- 🔄 Integraciones adicionales (Salesforce, Zendesk)
- 🔄 Dashboard de costos mejorado
- 🔄 Multi-tenancy avanzado

---

**Versión**: 0.3.0  
**Última actualización**: 2025-01  
**Mantenido por**: platform-team  
**Licencia**: Ver LICENSE file (si aplica)

### Changelog v0.3.0

- ✅ **Observabilidad mejorada**: 
  - ServiceMonitors para todos los componentes (Airflow, Kestra, Camunda, Flowable)
  - Dashboards de Grafana para monitoreo de automatizaciones
  - Alertas avanzadas de Prometheus para detección proactiva de fallos
  - Recolección centralizada de logs con Fluent Bit y ELK Stack
- ✅ **Documentación mejorada**: 
  - Sección completa de observabilidad en README principal
  - Guías de troubleshooting para métricas y logs
  - Ejemplos de búsqueda de logs en Kibana y Grafana
