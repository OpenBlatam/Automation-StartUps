# Workflow Orchestration

Esta carpeta contiene las configuraciones y definiciones de los orquestadores de workflows y procesos de negocio (BPM) de la plataforma.

## Componentes

La plataforma soporta múltiples herramientas de orquestación según el caso de uso:

### Kestra

**Ubicación**: `workflow/kestra/`

Orquestador de workflows declarativo en YAML, ideal para pipelines de datos y automatizaciones complejas.

- **Características**: Flujos declarativos, triggers, UI web, fácil adopción
- **Uso**: Pipelines de datos, integraciones (ManyChat, Stripe, WhatsApp), workflows end-to-end
- **Documentación**: Ver `workflow/kestra/README.md`

### Flowable

**Ubicación**: `workflow/flowable/`

Motor BPM (Business Process Management) para procesos de negocio formales y gobernados.

- **Características**: BPMN 2.0, gestión de casos, workflows humanos, auditoría
- **Uso**: Procesos de aprobación, onboarding, workflows con intervención humana
- **Documentación**: Ver `workflow/flowable/README.md`

### Camunda

**Ubicación**: `workflow/camunda/`

Plataforma BPM alternativa con workers para tareas asíncronas.

- **Características**: BPMN, DMN (decisiones), workers en Python/Java
- **Uso**: Procesos de negocio, workers personalizados
- **Documentación**: Ver `workflow/camunda/README_worker.md`

## Arquitectura

```
┌─────────────────┐
│   Triggers      │  (Webhooks, Cron, Events)
│  (Kestra)       │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Kestra  │  ──> Pipeline de datos
    │ Flows   │  ──> Integraciones
    └────┬────┘
         │
    ┌────┴────┐
    │Flowable │  ──> Procesos BPMN
    │ (BPMN)  │  ──> Aprobaciones
    └────┬────┘
         │
    ┌────┴────┐
    │ Camunda │  ──> Workers
    │ Workers │  ──> Tareas asíncronas
    └─────────┘
```

## Flujos de Trabajo Comunes

### 1. Integración ManyChat → HubSpot + DB

**Archivo**: `workflow/kestra/flows/leads_manychats_to_hubspot.yaml`

Flujo que:
1. Recibe webhook de ManyChat
2. Calcula score del lead
3. Hace upsert a HubSpot
4. Guarda en base de datos
5. Actualiza lifecycle

Ver documentación en README principal del proyecto.

### 2. Integración HubSpot → ManyChat (Envío de Mensajes)

**Archivo**: `workflow/kestra/flows/hubspot_lead_to_manychat.yaml`

Flujo que:
1. Recibe webhook de HubSpot (creación de contacto o cambio de propiedad)
2. Verifica que el contacto tenga la propiedad 'interés_producto' con valor
3. Valida que exista 'manychat_user_id' en el contacto
4. Obtiene nombre del contacto
5. Envía mensaje personalizado a ManyChat
6. Retorna estado de envío

**Configuración**:
- External Secrets: `security/secrets/externalsecrets-manychat.yaml`
- Webhook URL: `https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_lead_to_manychat/hubspot-lead`
- Variables requeridas: `manychat_api_key`, `hubspot_token` (opcional: `hubspot_webhook_secret`)

Ver documentación detallada en `workflow/kestra/flows/README.md`.

### 3. Pagos Stripe → Sheets + DB + AI

**Archivo**: `workflow/kestra/flows/stripe_payments_to_sheets_db_ai.yaml`

Flujo que:
1. Recibe webhook de Stripe
2. Registra pago en BD
3. Envía a Google Sheets
4. Llama a OpenAI para análisis

### 4. Tickets WhatsApp → Sheets + Docs

**Archivo**: `workflow/kestra/flows/whatsapp_ticket_to_sheet_doc.yaml`

Flujo que:
1. Recibe foto de ticket vía WhatsApp
2. Usa OCR para extraer datos
3. Agrega a Google Sheets
4. Genera documento para contabilidad

### 5. BPM + RPA

**Archivo**: `workflow/kestra/flows/bpm_rpa_example.yaml`

Flujo que:
1. Inicia proceso en Flowable
2. Dispara bot de OpenRPA
3. Coordina entre BPM y RPA

## Despliegue

### Kestra

```bash
# Aplicar Deployment
kubectl apply -f workflow/kestra/deployment.yaml

# Exponer por Ingress
# Configurar Ingress para kestra.workflows.svc.cluster.local

# Acceder a UI
kubectl port-forward -n workflows service/kestra 8080:8080
```

### Flowable

```bash
# Aplicar Deployment
kubectl apply -f workflow/flowable/deployment.yaml

# Acceder a UI (puerto 8080)
kubectl port-forward -n workflows service/flowable 8080:8080
```

### Camunda

Camunda se despliega mediante Helm (ver `helmfile.yaml`):

```bash
helmfile apply
```

## Integración entre Componentes

### Kestra → Flowable

```yaml
# En un flow de Kestra
type: io.kestra.core.tasks.flows.Http
uri: http://flowable.workflows.svc.cluster.local/runtime/process-instances
method: POST
headers:
  Authorization: "Bearer ${flowable_token}"
body:
  processDefinitionKey: businessApproval
  variables:
    amount: 5000
```

### Flowable → OpenRPA

Flows de Flowable pueden invocar webhooks que disparan bots de OpenRPA (ver `rpa/OPENRPA.md`).

### Camunda Workers

Workers de Camunda pueden:
- Leer de Kafka
- Procesar tareas asíncronas
- Integrar con servicios externos

Ver `workflow/camunda/worker/` para ejemplos en Python.

## Variables y Secrets

Los workflows necesitan acceso a:

- **Tokens de API**: HubSpot, Stripe, OpenAI
- **Credenciales de BD**: JDBC URLs, usuarios, passwords
- **Webhooks**: URLs de servicios externos

Estos se gestionan mediante External Secrets Operator:

- `security/secrets/externalsecrets-hubspot-db.yaml`
- `security/secrets/externalsecrets-stripe-sheets-openai-db.yaml`
- `security/secrets/externalsecrets-whatsapp-ocr.yaml`
- `security/secrets/externalsecrets-flowable-openrpa.yaml`

## Monitoreo

### Kestra

- **UI**: Dashboard de ejecuciones y logs
- **Métricas**: Expone métricas en `/metrics`
- **ServiceMonitor**: Ver `observability/servicemonitors/`

### Flowable

- **UI**: Modeler y Admin UI
- **Auditoría**: Logs de procesos y casos
- **Métricas**: Actuator endpoints (Spring Boot)

### Camunda

- **Cockpit**: UI de monitoreo de procesos
- **Métricas**: Integración con Prometheus

## Troubleshooting

### Ver Logs

```bash
# Kestra
kubectl logs -n workflows deployment/kestra

# Flowable
kubectl logs -n workflows deployment/flowable

# Camunda
kubectl logs -n workflows deployment/camunda-platform-zeebe-gateway
```

### Verificar Estado

```bash
# Ver pods
kubectl get pods -n workflows

# Ver servicios
kubectl get svc -n workflows

# Ver eventos
kubectl get events -n workflows --sort-by='.lastTimestamp'
```

### Debugging de Flows

1. **Kestra**: Usa el UI para ver ejecuciones paso a paso
2. **Flowable**: Revisa logs de Spring Boot y traces de procesos
3. **Camunda**: Usa Cockpit para inspeccionar instancias de proceso

## Mejores Prácticas

1. **Idempotencia**: Diseña flows idempotentes cuando sea posible
2. **Error Handling**: Implementa retry y manejo de errores
3. **Secrets**: Nunca hardcodees secrets en flows
4. **Versionado**: Versiona flows en Git
5. **Testing**: Prueba flows en desarrollo antes de producción
6. **Monitoreo**: Instrumenta métricas y alertas críticas

## Referencias

- [Kestra Documentation](https://kestra.io/docs/)
- [Flowable Documentation](https://www.flowable.com/open-source/docs/)
- [Camunda Documentation](https://docs.camunda.org/)
- [BPMN 2.0 Specification](https://www.omg.org/spec/BPMN/2.0/)


