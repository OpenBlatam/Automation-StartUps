# Plataforma de Automatización Empresarial

Este repositorio define una plataforma modular para automatizar procesos de negocio sobre Kubernetes (AKS/EKS/OpenShift), con data lake (ADLS/S3), analítica (Databricks/Snowflake), orquestación (API Gateway + Kafka + workflows), RPA, MLOps (MLflow/KServe), observabilidad (Prometheus/Grafana, ELK) y gobierno/seguridad (RBAC, OPA Gatekeeper).

## Cómo usar este repo

1) Selecciona el proveedor en `platform.yaml` (cloud, componentes y opciones).
2) Despliega la infraestructura base con Terraform (`infra/terraform`).
3) Aplica los manifiestos de Kubernetes en `kubernetes/` por capas.
4) Despliega integraciones (Kafka, Airflow, Camunda) y capas de IA/MLOps.
5) Activa observabilidad y políticas de seguridad.

Consulta cada carpeta para instrucciones específicas.

## Estructura

- `platform.yaml`: selección de cloud y componentes.
- `infra/terraform`: infraestructura base (Kubernetes, data lake, redes, identidades).
  - AWS: `infra/terraform/` (EKS + S3)
  - Azure: `infra/terraform/azure/` (AKS + ADLS Gen2 + ACR)
- `kubernetes/`: namespaces, ingress/API gateway, componentes core.
- `data/`: pipelines (Airflow), catálogos y lake integration.
- `workflow/`: orquestadores de procesos (Camunda u otros).
- `ml/`: MLOps (MLflow, KServe, ejemplos de despliegue modelo).
- `observability/`: Prometheus/Grafana y ELK.
- `security/`: RBAC, OPA Gatekeeper, guías IAM/auditoría.

## Requisitos locales

- Terraform >= 1.6
- kubectl y/o oc (OpenShift)
- Helm >= 3.13
- Acceso a cloud (Azure/AWS) e identidades configuradas

## Flujo de despliegue (alto nivel)

1. IaC: redes, cluster, storage, identidades.
2. K8s: namespaces, ingress, secrets, policies.
3. Integraciones: Kafka, Airflow, Camunda.
4. Datos/ML: data lake, MLflow, KServe, Databricks/Snowflake.
5. Observabilidad y seguridad.

> Plantillas provistas como ejemplo; adapte valores a su organización.

## Quickstart

AWS (EKS + S3):

```bash
make tf-init TF_DIR=infra/terraform
make tf-apply TF_DIR=infra/terraform
make k8s-namespaces
make k8s-ingress
make k8s-integration
```

Azure (AKS + ADLS + ACR):

```bash
make tf-init TF_DIR=infra/terraform/azure
make tf-apply TF_DIR=infra/terraform/azure
make k8s-namespaces
make k8s-ingress
make k8s-integration
```

Kafka y tópicos (Strimzi ya instalado):

```bash
make k8s-kafka
make k8s-kafka-topics
```

## Avanzado

- Overlays (Kustomize):
  - `kubectl apply -k kubernetes/overlays/dev` (o `stg`/`prod`) para ajustar hosts y parámetros por entorno.
- Helmfile (instalación de charts):
  - `helmfile apply` para instalar ingress-nginx, Airflow, Prometheus/Grafana, Strimzi y Camunda según `helmfile.yaml`.
- External Secrets:
  - AWS: `security/secrets/externalsecrets-aws.yaml` (requiere IRSA/role y ESO instalado).
  - Azure: `security/secrets/externalsecrets-azure.yaml` (requiere Workload Identity/Key Vault y ESO).
- CI/CD:
  - Terraform PR checks: `.github/workflows/infra.yaml` (fmt/validate/plan).
  - Deploy manual a K8s con overlays: `.github/workflows/deploy.yaml` (requiere `KUBECONFIG_B64` en secrets).
- Alertas:
  - Reglas básicas en `observability/prometheus/alertrules.yaml`; improvise severidades y rutas de Alertmanager.

## Certificados y Autenticación

- cert-manager:
  - Instalar con `helmfile apply` y aplicar `security/cert-manager/clusterissuer.yaml`.
  - En el Ingress, use `cert-manager.io/cluster-issuer: letsencrypt-prod` y quite `secretName` manual si usa ACME.
- oauth2-proxy (OIDC):
  - Ajuste `security/oauth2-proxy/values.yaml` con su IdP.
  - Despliegue el chart oauth2-proxy y habilite las anotaciones `auth-url`/`auth-signin` en `api-gateway`.

## Seguridad de red

- NetworkPolicies base en `security/networkpolicies/baseline.yaml` (deny-all ingress + DNS egress). Amplíe según servicios necesarios.
- Gatekeeper: `security/policies/gatekeeper/limits.yaml` para requerir requests/limits.

## Integración de datos

- Kafka Connect: despliegue `kubernetes/kafka/connect/deployment.yaml` y configure plugins/secretos. Ejemplo S3 sink en `kubernetes/kafka/connect/s3-sink.json`.

## Costes

- OpenCost: valores en `observability/opencost/values.yaml` y release en `helmfile.yaml`. Acceda vía servicio en `observability`.

## Comandos útiles

```bash
# instalar charts base
make helmfile-apply
# aplicar overlay por entorno
overlay=dev && make kustomize-$(overlay)
# kafka connect
make k8s-connect
```

## Operación avanzada

- Recursos por espacio: `security/kubernetes/limitranges-quotas.yaml` (LimitRanges y ResourceQuotas por namespace).
- Resiliencia app: `kubernetes/integration/healthz-pdb.yaml` y `healthz-hpa.yaml`.
- Métricas: ServiceMonitor `observability/servicemonitors/healthz.yaml`.
- Backups: Velero (`backup/velero/values.yaml` y release en `helmfile.yaml`).
- Data Lake: lifecycle S3 en Terraform (`infra/terraform/main.tf`).
- Políticas:
  - Requests/Limits obligatorios: `security/policies/gatekeeper/limits.yaml`.
  - Etiqueta `cost-center` obligatoria: `security/policies/gatekeeper/cost-center.yaml`.
- Camunda worker ejemplo: `workflow/camunda/worker/python/worker.py`.
- Databricks/Snowflake: notas en `data/INTEGRATIONS.md`.

## Entornos y validación

- Valores por entorno: `environments/{dev,stg,prod}.yaml` (dominios, issuer OIDC, bucket, issuer ACME).
- Overlays aplican host y `cert-manager.io/cluster-issuer` acorde al entorno.
- Validación sin aplicar cambios:

```bash
make kustomize-validate-dev
make kustomize-validate-stg
make kustomize-validate-prod
```

## Capas de la plataforma (mejorada)

| Capa | Herramienta | Función | Mejora clave |
|---|---|---|---|
| Infraestructura / Plataforma | Kubernetes (EKS/AKS/OpenShift) | Contenedores, orquestación, escalado | Despliegue híbrido (nube + on‑prem) y cumplimiento local |
| Almacenamiento de datos | Data lake + DB (S3/ADLS + SQL/NoSQL) | Históricos, logs, métricas | Gobierno de datos, metadatos, historización |
| Orquestación global de workflows | Kestra | Pipelines declarativos (YAML), triggers, UI | Adopción por equipos mixtos (dev/ops/negocio) |
| Procesos de negocio (BPM) | Flowable | BPMN para procesos formales | Automatizaciones gobernadas y auditables |
| Automatización de tareas (RPA) | OpenRPA | UI/desktop/API bots | Open‑source, evita lock‑in |
| IA/ML/MLOps | Kubeflow + MLflow + KServe | Entrenar/servir, tracking | Evolución hacia automatización “autónoma” |
| Integración / API / eventos | NGINX Ingress + Kafka | APIs, eventos, tiempo real | Escalabilidad y acoplamiento débil |
| Observabilidad y gobernanza | Prometheus/Grafana + ELK + IAM | Métricas, logs, alertas, RBAC | Operación 24/7 y cumplimiento |

## Flujo end‑to‑end

1. Usuarios definen el proceso en Kestra (o programan trigger/evento).
2. Kestra invoca rutas de negocio en Flowable (BPMN) cuando corresponde.
3. Tareas sin API se ejecutan con bots OpenRPA coordinados por OpenFlow.
4. Decisiones y predicciones via Kubeflow/MLflow/KServe.
5. Todo corre en Kubernetes, integrado por API y eventos (Kafka/Ingress).
6. Observabilidad central (Prometheus/ELK) y gobierno (RBAC, OPA, auditoría).

Referencias rápidas:
- Kestra: `workflow/kestra/deployment.yaml`
- Flowable: `workflow/flowable/deployment.yaml`
- OpenRPA: `rpa/OPENRPA.md`
- Kubeflow: `ml/kubeflow/README.md` (KServe/MLflow ya incluidos)

## Workflow: ManyChat → HubSpot + DB + scoring (Kestra)

- Flujo en `workflow/kestra/flows/leads_manychats_to_hubspot.yaml`.
- Secrets (External Secrets, ajustar a su store): `security/secrets/externalsecrets-hubspot-db.yaml`.
- Esquema BD: `data/db/schema.sql`.

Pasos:
1) Exponga Kestra por Ingress y obtenga URL base (ver `workflow/kestra/deployment.yaml` + su Ingress).
2) Cargue el flow en Kestra y copie la URL del webhook generado por el trigger `manychat_webhook`.
3) Configure el Webhook en ManyChat apuntando a esa URL.
4) Defina inputs/variables en la ejecución del flow o namespace:
   - `hubspot_token` (Bearer)
   - `jdbc_url`, `jdbc_user`, `jdbc_password`
5) Ejecute `data/db/schema.sql` en su base de datos de leads.

El flujo: recibe payload de ManyChat → calcula score → upsert a HubSpot → upsert a BD → actualiza lifecycle.

## Automatización: Stripe → Google Sheets + DB + Insight (OpenAI)

- Flujo: `workflow/kestra/flows/stripe_payments_to_sheets_db_ai.yaml`
- Secrets: `security/secrets/externalsecrets-stripe-sheets-openai-db.yaml`
- BD: `data/db/payments.sql`

Pasos:
1) Crea la tabla `payments` ejecutando `data/db/payments.sql`.
2) Importa el flow en Kestra y expón el webhook `stripe_webhook`.
3) Configura un endpoint de webhook en Stripe apuntando a esa URL (evento sugerido: `payment_intent.succeeded`/`charge.succeeded`).
4) Provee inputs/vars:
   - `jdbc_url`, `jdbc_user`, `jdbc_password`
   - `sheets_webhook_url` (Apps Script o servicio que agrega filas)
   - `openai_api_key`
5) Opcional: valida firma Stripe con `STRIPE_SIGNING_SECRET` en un wrapper/gateway o extiende el task de parseo.

Qué hace:
- Registra el pago en la tabla `payments`.
- Envía datos a Google Sheets mediante un webhook externo.
- Llama a OpenAI para una interpretación y pronóstico simple usando los últimos 30 días.

## Automatización: WhatsApp Ticket → Sheets + Documento (Kestra)

- Flujo: `workflow/kestra/flows/whatsapp_ticket_to_sheet_doc.yaml`.
- Secrets: `security/secrets/externalsecrets-whatsapp-ocr.yaml` (WhatsApp token, OpenAI, Sheets, Docs).

Pasos:
1) Exponga Kestra por Ingress y configure el webhook `whatsapp_webhook` como endpoint en su proveedor (WhatsApp Cloud/Twilio). Asegure autenticación/verificación básica.
2) Provea inputs (por ejecución/namespace): `openai_api_key`, `sheets_webhook_url`, `docs_webhook_url` (puede mapearse desde secretos). Opcional: `whatsapp_token`.
3) Envíe una foto de un ticket al WhatsApp configurado. El flujo extrae proveedor, fecha, total, moneda, items, etc., agrega a Google Sheets y genera un documento para contabilidad vía webhook.

## Orquestación BPM + RPA (Kestra)

- Flujo de ejemplo: `workflow/kestra/flows/bpm_rpa_example.yaml`
  - Inicia un proceso en Flowable (`businessApproval`) con variables de negocio.
  - Dispara un bot de OpenRPA vía webhook con el contexto del caso.
- Secrets: `security/secrets/externalsecrets-flowable-openrpa.yaml`.
- Personalice `flowable_base_url`, `flowable_token`, `openrpa_webhook_url` e `inputs.payload` al ejecutar el flow.

## Dashboard de KPIs en tiempo real (Grafana)

- Datasource Postgres: `observability/grafana/datasources/postgres.yaml` (usa variables de entorno)
  - Establezca en el pod de Grafana (o Helm values): `KPIS_PG_HOST`, `KPIS_PG_DB`, `KPIS_PG_USER`, `KPIS_PG_PASSWORD`.
- Dashboard: `observability/grafana/dashboards/kpi.json` (importe via UI o sidecar de dashboards).

KPIs incluidos:
- Ingresos (1h, 24h), ingresos por hora (24h), pagos/leads recientes.
- Leads por prioridad (hoy), conversión 7d (leads→pagos).
- Salud: tasa 5xx de Ingress y reinicios de pods.

## Documentación

- Índice de documentación: `docs/INDEX.md`
- Guías clave: Integraciones (`data/INTEGRATIONS.md`), MLOps (`ml/`), Workflows (`workflow/`), Seguridad (`security/`), Observabilidad (`observability/`).

## Refactor clave aplicado

- commonLabels por entorno en overlays (`kubernetes/overlays/*/kustomization.yaml`) para trazabilidad (`app.kubernetes.io/part-of`, `app.kubernetes.io/environment`).
- Makefile: nuevos targets `tf-fmt` y `tf-validate` para estandarizar validación Terraform.

## Interfaz simple de KPIs (TypeScript)

App ligera en `web/kpis` (Express + TS) que lee `payments` y `leads` y muestra:
- Página HTML en `/` con KPIs y tablas recientes
- API JSON en `/api/kpi/summary`

Ejecutar localmente:
```bash
cd web/kpis
npm install
KPIS_PG_HOST=localhost KPIS_PG_DB=analytics KPIS_PG_USER=analytics KPIS_PG_PASSWORD=xxx npm run dev
# abrir http://localhost:3000
```
Despliegue en contenedor: crear Dockerfile sencillo y exponer `PORT` (por defecto 3000).

## KPIs con Next.js (React)

App en `web/kpis-next` con API Route y página SSR.
- API: `/api/kpi/summary` (usa Postgres `payments` y `leads`).
- UI: `/` (SSR, refresco en cada request).

Ejecutar localmente:
```bash
cd web/kpis-next
npm install
KPIS_PG_HOST=localhost KPIS_PG_DB=analytics KPIS_PG_USER=analytics KPIS_PG_PASSWORD=xxx NEXT_PUBLIC_BASE_URL=http://localhost:3000 npm run dev
```
Despliegue: usar `npm run build && npm start` detrás de Ingress/TLS.

## Airflow: automatizaciones de datos

DAGs añadidos en `data/airflow/dags/`:
- `stripe_reconcile.py`: cada hora reconcilia cargos de Stripe vs tabla `payments` (requiere `STRIPE_API_KEY`, `KPIS_PG_DSN`).
- `kpi_aggregate_daily.py`: consolida métricas diarias en `kpi_daily`.
- `leads_sync_hubspot.py`: sincroniza contactos de HubSpot a `leads` (requiere `HUBSPOT_TOKEN`, `KPIS_PG_DSN`).

Configure conexiones/variables vía External Secrets o env vars del chart de Airflow (`