# RPA - Robotic Process Automation

Esta carpeta contiene la documentación y configuración para automatización de procesos robóticos (RPA) usando OpenRPA y OpenFlow.

## Descripción

OpenRPA y OpenFlow proporcionan una solución open-source para automatización de tareas repetitivas que requieren interacción con interfaces de usuario (UI), aplicaciones de escritorio y APIs.

## Componentes

### OpenFlow (Server)

OpenFlow es el servidor/broker que coordina y gestiona la ejecución de bots OpenRPA.

**Características**:
- API REST y WebSocket para comunicación
- Base de datos MongoDB para persistencia
- Coordinación centralizada de bots
- UI web para monitoreo

**Despliegue**: Ver `OPENRPA.md` para detalles de despliegue en Kubernetes.

### OpenRPA (Bots)

OpenRPA son los bots que ejecutan las tareas automatizadas en estaciones/VMs.

**Características**:
- Automatización de UI (clic, escribir, capturar)
- Integración con APIs
- Scripts Python/C# para lógica compleja
- Comunicación con OpenFlow vía WebSocket/API

## Arquitectura

```
┌─────────────────┐
│   Kestra/       │  Triggers workflow
│   Flowable      │
└────────┬────────┘
         │ HTTP/Webhook
    ┌────┴────┐
    │ OpenFlow│  Coordina bots
    │ Server  │
    └────┬────┘
         │ WebSocket/API
    ┌────┴────┐
    │ OpenRPA │  Ejecuta tareas
    │  Bots   │
    └─────────┘
```

## Integración con la Plataforma

### Desde Kestra

Los flows de Kestra pueden disparar bots OpenRPA:

```yaml
# workflow/kestra/flows/bpm_rpa_example.yaml
- id: trigger_openrpa_bot
  type: io.kestra.core.tasks.http.Request
  uri: http://openflow.workflows.svc:8080/api/v1/bots/execute
  method: POST
  headers:
    Authorization: "Bearer ${vars.openrpa_token}"
  body:
    bot_name: "invoice_processing"
    parameters:
      invoice_path: "{{ inputs.invoice_path }}"
```

### Desde Flowable

Flows de Flowable pueden invocar bots mediante Service Tasks HTTP:

```yaml
# Service Task HTTP que llama a OpenFlow API
url: http://openflow.workflows.svc:8080/api/v1/bots/execute
method: POST
variables:
  bot_name: invoice_processing
  parameters: ${execution.getVariable('invoice_data')}
```

### Desde Kafka

Integración mediante eventos:

```yaml
# Consumir evento de Kafka y disparar bot
topic: rpa-tasks
consumer:
  - on_message:
      trigger_bot:
        bot: document_processing
        data: ${message.value}
```

## Despliegue

### OpenFlow en Kubernetes

```bash
# Despliegue básico (ver OPENRPA.md para detalles)
kubectl apply -f kubernetes/openflow-deployment.yaml

# Exponer servicio
kubectl expose deployment openflow \
  --namespace workflows \
  --port 8080 \
  --type ClusterIP
```

**Requisitos**:
- MongoDB para persistencia
- Service Account con permisos necesarios
- ConfigMap con configuración

### OpenRPA Bots

Los bots OpenRPA se despliegan en:
- **VMs dedicadas**: Para tareas que requieren escritorio completo
- **Contenedores**: Para tareas headless o con virtual display
- **Workstations**: Para desarrollo y pruebas

**Configuración del Bot**:

```json
{
  "openflow_url": "ws://openflow.workflows.svc:8080/ws",
  "bot_id": "invoice-bot-001",
  "credentials": {
    "username": "bot-user",
    "password": "${OPENRPA_PASSWORD}"
  }
}
```

## Seguridad

### Autenticación

1. **OIDC en Gateway**: Configurar OAuth2-proxy o similar para acceso externo
2. **mTLS**: Para comunicación entre OpenFlow y bots (producción)
3. **API Keys**: Para autenticación de aplicaciones que llaman a OpenFlow

### Red

- **Network Policies**: Aislar tráfico de OpenFlow
- **VPN/Private Network**: Para bots en VMs on-premise

## Observabilidad

### Métricas

OpenFlow expone métricas en `/metrics`:

- `openrpa_bot_executions_total`: Total de ejecuciones
- `openrpa_bot_duration_seconds`: Duración de ejecuciones
- `openrpa_bot_errors_total`: Errores

Configurar ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: openflow
  namespace: workflows
spec:
  selector:
    matchLabels:
      app: openflow
  endpoints:
    - port: http
      path: /metrics
```

### Logging

Los logs de OpenFlow y bots se estructuran:

```json
{
  "timestamp": "2025-01-15T10:00:00Z",
  "level": "INFO",
  "bot_id": "invoice-bot-001",
  "execution_id": "exec-123",
  "message": "Bot execution completed",
  "duration_ms": 4500
}
```

### Tracing

Integración opcional con OpenTelemetry para tracing distribuido.

## Casos de Uso

### Procesamiento de Facturas

1. Flowable inicia proceso de aprobación
2. Service Task llama a OpenRPA bot
3. Bot extrae datos de factura (OCR)
4. Bot valida y procesa
5. Resultado se envía de vuelta a Flowable

### Automatización de Formularios Web

1. Kestra flow recibe datos
2. Dispara OpenRPA bot
3. Bot navega a formulario web
4. Bot completa campos automáticamente
5. Bot envía formulario y captura confirmación

### Sincronización de Sistemas Legacy

1. Kafka recibe evento de nuevo registro
2. OpenRPA bot consume evento
3. Bot accede a sistema legacy vía UI
4. Bot ingresa datos y sincroniza
5. Bot reporta resultado a OpenFlow

## Troubleshooting

### Bot no se conecta a OpenFlow

```bash
# Verificar conectividad
kubectl exec -n workflows deployment/openflow -- \
  nc -zv openflow.workflows.svc.cluster.local 8080

# Verificar logs de OpenFlow
kubectl logs -n workflows deployment/openflow | grep websocket
```

### Bot falla en ejecución

```bash
# Ver logs del bot
# Si está en VM, verificar logs locales
# Si está en pod, verificar logs del pod

# Verificar métricas
curl http://openflow.workflows.svc:8080/metrics | grep openrpa_bot_errors
```

### Error de autenticación

```bash
# Verificar credenciales
kubectl get secret -n workflows openrpa-credentials

# Verificar configuración OIDC
kubectl get ingress -n workflows openflow -o yaml
```

## Mejores Prácticas

1. **Idempotencia**: Diseña bots idempotentes
2. **Error Handling**: Implementa retry y manejo de errores robusto
3. **Logging**: Usa logging estructurado con contexto
4. **Timeouts**: Configura timeouts apropiados para tareas
5. **Monitoreo**: Instrumenta métricas clave (duración, tasa de error)
6. **Security**: No hardcodees credenciales, usa secretos
7. **Testing**: Prueba bots en staging antes de producción

## Referencias

- **OpenRPA**: Ver `OPENRPA.md` para detalles técnicos
- **OpenFlow Documentation**: [OpenFlow Docs](https://openrpa.docs.openflow.io/)
- **Ejemplos de Integración**: `workflow/kestra/flows/bpm_rpa_example.yaml`

