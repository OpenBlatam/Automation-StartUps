# Kestra Flows - Catálogo de Workflows

Esta carpeta contiene todos los workflows de Kestra organizados por categoría. Cada flow está documentado individualmente.

## Estructura

```
flows/
├── README.md                          # Este archivo
├── README_INVOICE_REMINDERS.md        # Documentación de recordatorios de facturas
├── README_MEETING_SCHEDULER.md        # Documentación de agendador de reuniones
├── README_ABANDONED_CART_RECOVERY.md  # Documentación de recuperación de carritos abandonados
├── README_onboarding.md               # Documentación de onboarding
├── IMPROVEMENTS_SUMMARY.md           # Resumen de mejoras (v2.0.0)
├── leads_manychats_to_hubspot.yaml    # Flow: ManyChat → HubSpot + DB
├── hubspot_lead_to_manychat.yaml      # Flow: HubSpot → ManyChat (envío de mensajes)
├── stripe_payments_to_sheets_db_ai.yaml  # Flow: Stripe → Sheets + DB + AI
├── whatsapp_ticket_to_sheet_doc.yaml  # Flow: WhatsApp → Sheets + Docs
├── bpm_rpa_example.yaml              # Flow: BPM + RPA integration
├── lib/                               # 📦 Librerías Python reutilizables (v2.1.0)
│   ├── README.md                      # Documentación de librerías
│   ├── hubspot_client.py              # Cliente HubSpot (CB, cache, metrics, health)
│   ├── manychat_client.py             # Cliente ManyChat (CB, metrics, health)
│   ├── webhook_validator.py           # Validación HMAC para webhooks
│   ├── circuit_breaker.py             # Circuit Breaker pattern
│   ├── cache.py                       # Caché simple con TTL
│   ├── metrics.py                     # Métricas Prometheus
│   ├── health.py                      # Health checks estructurados ⭐
│   ├── batch.py                       # Procesamiento batch paralelo ⭐
│   ├── requirements.txt               # Dependencias Python
│   └── tests/                         # Tests unitarios
│       └── test_hubspot_client.py
└── ...
```

## Categorías de Flows

### 1. Marketing y Growth

#### `leads_manychats_to_hubspot.yaml`

**Función**: Integración ManyChat → HubSpot + Base de datos

**Flujo**:
1. Recibe webhook de ManyChat
2. Calcula score del lead
3. Hace upsert a HubSpot
4. Guarda en base de datos
5. Actualiza lifecycle

**Variables requeridas**:
- `hubspot_token`
- `jdbc_url`, `jdbc_user`, `jdbc_password`

**Documentación**: Ver sección en README principal del proyecto

#### `hubspot_update_estado_interes.yaml`

**Función**: Actualiza la propiedad 'estado_interés' de un contacto en HubSpot

**Flujo**:
1. Recibe parámetros (manual o por webhook)
2. Valida que se proporcionen `hubspot_contact_id` y `nuevo_estado`
3. Actualiza la propiedad en HubSpot vía API
4. Retorna resultado: 'Éxito' o código de error + mensaje

**Variables requeridas**:
- `hubspot_token`: Token de autenticación de HubSpot
- `hubspot_contact_id`: ID del contacto (input o en payload de webhook)
- `nuevo_estado`: Nuevo valor para 'estado_interés' (input o en payload de webhook)
- `hubspot_base`: URL base de la API (opcional, default: https://api.hubapi.com)

**Ejecución manual**:
```bash
curl -X POST http://kestra.example.com/api/v1/executions/trigger \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "namespace": "workflows",
    "flowId": "hubspot_update_estado_interes",
    "inputs": {
      "hubspot_token": "xxx",
      "hubspot_contact_id": "12345678",
      "nuevo_estado": "calificado"
    }
  }'
```

**Ejecución por webhook**:
```bash
curl -X POST http://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_update_estado_interes/webhook_trigger \
  -H "Content-Type: application/json" \
  -d '{
    "hubspot_contact_id": "12345678",
    "nuevo_estado": "calificado"
  }'
```

**Ejemplo de respuesta exitosa**:
```json
{
  "success": true,
  "status_code": 200,
  "contact_id": "12345678",
  "nuevo_estado": "calificado",
  "message": "Éxito"
}
```

**Ejemplo de respuesta con error**:
```json
{
  "success": false,
  "status_code": 404,
  "contact_id": "12345678",
  "nuevo_estado": "calificado",
  "message": "404: Contact not found"
}
```

#### `hubspot_lead_to_manychat.yaml` / `hubspot_lead_to_manychat_improved.yaml` (Recomendado) / `hubspot_to_manychat.yaml`

**Función**: Integración HubSpot → ManyChat para envío de mensajes automáticos cuando se crea un lead con interés en un producto

**Versiones disponibles**:
- `hubspot_lead_to_manychat_improved.yaml` (RECOMENDADO): Versión mejorada con librerías (`lib/hubspot_client.py`, `lib/manychat_client.py`, `lib/webhook_validator.py`). Incluye retry automático, rate limiting, validación robusta y logging estructurado.
- `hubspot_lead_to_manychat.yaml`: Versión estándar con verificación de firma, fetch de propiedades desde API y mejor manejo de eventos
- `hubspot_to_manychat.yaml`: Versión más simple, requiere que todas las propiedades vengan en el webhook

**Librerías disponibles**: Ver `lib/README.md` para documentación completa de las librerías mejoradas.

**Flujo**:
1. Recibe webhook de HubSpot (creación de contacto o cambio de propiedad)
2. Verifica que el contacto tenga la propiedad 'interés_producto' con valor
3. Valida que exista 'manychat_user_id' en el contacto
4. Obtiene nombre del contacto (firstname o lastname)
5. Envía mensaje personalizado a ManyChat: "Hola {nombre}, gracias por tu interés en {producto}. ¿Te gustaría agendar una demo?"
6. Retorna estado de envío (sent/error/skipped)

**Variables requeridas**:
- `manychat_api_key`: API Key de ManyChat para autenticación
- `hubspot_token`: Token de HubSpot (requerido en `hubspot_lead_to_manychat.yaml` para obtener datos del contacto si no vienen en el webhook)
- `hubspot_webhook_secret`: (Opcional, solo `hubspot_lead_to_manychat.yaml`) Secret para verificar firma del webhook

**Configuración en HubSpot**:
1. Configurar webhook en HubSpot para eventos:
   - `contact.creation`: Cuando se crea un nuevo contacto
   - `contact.propertyChange` (filtrado por propiedad `interés_producto`): Cuando cambia la propiedad
2. URL del webhook: `https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_lead_to_manychat/hubspot-lead`
3. Asegurarse de que los contactos tengan las propiedades:
   - `interés_producto`: Valor del producto de interés (ej: "Producto X")
   - `manychat_user_id`: ID del usuario en ManyChat

**Ejemplo de respuesta exitosa**:
```json
{
  "status": "sent",
  "message": "Mensaje enviado exitosamente",
  "contact_id": "12345",
  "contact_name": "Juan Pérez",
  "manychat_user_id": "67890",
  "interes_producto": "Producto X",
  "mensaje_enviado": "Hola Juan Pérez, gracias por tu interés en Producto X. ¿Te gustaría agendar una demo?",
  "manychat_response": {
    "status": "success"
  }
}
```

**Ejemplo de respuesta cuando se omite**:
```json
{
  "status": "skipped",
  "reason": "no_interes_producto",
  "contact_id": "12345"
}
```

#### `stripe_payments_to_sheets_db_ai.yaml`

**Función**: Procesamiento de pagos Stripe con análisis AI

**Flujo**:
1. Recibe webhook de Stripe
2. Registra pago en BD
3. Envía a Google Sheets
4. Llama a OpenAI para análisis

**Variables requeridas**:
- `jdbc_*` (BD connection)
- `sheets_webhook_url`
- `openai_api_key`

**Documentación**: Ver README principal del proyecto

### 2. Customer Support

#### `whatsapp_ticket_to_sheet_doc.yaml`

**Función**: Procesamiento de tickets vía WhatsApp

**Flujo**:
1. Recibe foto de ticket vía WhatsApp
2. Usa OCR para extraer datos
3. Agrega a Google Sheets
4. Genera documento para contabilidad

**Variables requeridas**:
- `openai_api_key` (para OCR)
- `sheets_webhook_url`
- `docs_webhook_url`

**Documentación**: Ver README principal del proyecto

#### `README_ABANDONED_CART_RECOVERY.md`

**Función**: Recuperación de carritos abandonados

Ver documentación específica en el archivo.

### 3. Financial y Facturación

#### `README_INVOICE_REMINDERS.md`

**Función**: Recordatorios automáticos de facturas

Ver documentación específica en el archivo.

### 4. HR y Onboarding

#### `README_onboarding.md`

**Función**: Automatización de onboarding de empleados

Ver documentación específica en el archivo.

### 5. Scheduling

#### `README_MEETING_SCHEDULER.md`

**Función**: Agendador inteligente de reuniones

Ver documentación específica en el archivo.

### 6. Integración BPM + RPA

#### `bpm_rpa_example.yaml`

**Función**: Ejemplo de integración entre BPM y RPA

**Flujo**:
1. Inicia proceso en Flowable
2. Dispara bot de OpenRPA
3. Coordina entre BPM y RPA

**Variables requeridas**:
- `flowable_base_url`, `flowable_token`
- `openrpa_webhook_url`

**Documentación**: Ver `workflow/kestra/README.md`

## Cómo Usar los Flows

### 1. Cargar Flow en Kestra

```bash
# Desde UI de Kestra
# 1. Navegar a Flows → Create
# 2. Paste el contenido YAML del flow
# 3. Guardar

# O vía API
curl -X POST http://kestra.example.com/api/v1/flows \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d @flows/leads_manychats_to_hubspot.yaml
```

### 2. Configurar Variables

Desde la UI de Kestra:
- Namespaces → Variables → Create
- O desde ejecución manual: Inputs/Variables

Desde External Secrets:
- Ver `security/secrets/externalsecrets-*.yaml`

### 3. Configurar Triggers

**Webhooks**:
1. Cargar el flow
2. Copiar la URL del webhook generado
3. Configurar en el sistema externo (ManyChat, Stripe, etc.)

**Schedules**:
1. Editar el flow
2. Configurar cron en la sección `triggers`
3. Guardar

### 4. Ejecutar Manualmente

Desde UI:
- Flows → Seleccionar flow → Execute → Run

Desde CLI:
```bash
curl -X POST http://kestra.example.com/api/v1/executions/trigger \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{
    "namespace": "production",
    "flowId": "leads_manychats_to_hubspot",
    "inputs": {
      "hubspot_token": "xxx",
      "jdbc_url": "jdbc:postgresql://..."
    }
  }'
```

## Monitoreo de Flows

### Desde UI de Kestra

- **Dashboard**: Vista de ejecuciones recientes
- **Executions**: Historial completo de ejecuciones
- **Logs**: Logs de cada task en ejecución
- **Métricas**: Duración, estado, etc.

### Desde Prometheus

Los flows exponen métricas automáticamente:
- `kestra_flows_executions_total`
- `kestra_flows_duration_seconds`
- `kestra_flows_errors_total`

Ver `observability/servicemonitors/kestra.yaml`

### Desde Grafana

Dashboards disponibles:
- ETL workflows
- BPM workflows
- Integration workflows

## Troubleshooting

### Flow no se ejecuta

```bash
# Verificar estado del flow
curl http://kestra.example.com/api/v1/flows/{namespace}/{flowId} \
  -u admin:admin

# Verificar triggers desde UI
# Flows → Flow → Triggers
```

### Error en ejecución

```bash
# Ver logs de ejecución desde UI
# O verificar logs del pod
kubectl logs -n workflows deployment/kestra | grep ERROR
```

### Variables no encontradas

```bash
# Listar variables del namespace
curl http://kestra.example.com/api/v1/variables \
  -u admin:admin \
  -G -d "namespace=production"

# Crear variable faltante
curl -X PUT http://kestra.example.com/api/v1/variables/{key} \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{"value": "xxx"}'
```

## Mejores Prácticas

1. **Versionar flows**: Guardar en Git con commits descriptivos
2. **Separar por namespace**: Usar namespaces por entorno (dev/stg/prod)
3. **Variables secretas**: Marcar como "secret" en UI para ocultarlas
4. **Testing**: Probar flows en dev antes de producción
5. **Idempotencia**: Diseñar flows idempotentes cuando sea posible
6. **Logging**: Usar logging estructurado en tasks personalizados
7. **Error handling**: Implementar retry y manejo de errores

## 📦 Librerías Python Reutilizables

Las librerías en `lib/` proporcionan funcionalidades avanzadas para workflows:

### Características Principales

- **Circuit Breaker**: Protección contra cascading failures
- **Caché**: Reduce llamadas repetidas a APIs
- **Métricas Prometheus**: Observabilidad integrada
- **Health Checks**: Validación de conectividad y dependencias
- **Batch Processing**: Procesamiento paralelo para operaciones masivas
- **Context Managers**: Gestión automática de recursos (cierre de sesiones)
- **Retry Automático**: Exponential backoff con tenacity
- **Rate Limiting**: Manejo automático de 429
- **Logging Estructurado**: Contexto completo en logs

### Módulos Disponibles

1. **`hubspot_client.py`** - Cliente HubSpot con todas las características
2. **`manychat_client.py`** - Cliente ManyChat con Circuit Breaker, métricas y health checks
3. **`webhook_validator.py`** - Validación HMAC para webhooks
4. **`circuit_breaker.py`** - Implementación genérica del patrón
5. **`cache.py`** - Caché con TTL
6. **`metrics.py`** - Colector de métricas Prometheus
7. **`health.py`** ⭐ - Health checks estructurados (v2.1.0)
8. **`batch.py`** ⭐ - Procesamiento batch paralelo (v2.1.0)

### Uso en Flows

Las librerías se pueden usar en Python tasks de Kestra:

```python
# En un task Python de Kestra
import sys
sys.path.insert(0, '/path/to/lib')

from hubspot_client import HubSpotClient
from manychat_client import ManyChatClient

# Usar clientes con context manager (cierre automático)
with HubSpotClient(api_token=os.getenv('HUBSPOT_TOKEN')) as hubspot:
    # Health check antes de usar
    health = hubspot.health_check()
    if health["status"] == "healthy":
        result = hubspot.get_contact("123")  # Con caché, circuit breaker, métricas

# Batch processing para múltiples operaciones
from batch import BatchProcessor
processor = BatchProcessor(max_workers=5)
contacts = [{"id": "1"}, {"id": "2"}]
batch_result = processor.process(
    items=contacts,
    process_func=lambda c: hubspot.get_contact(c["id"])
)
print(f"Success rate: {batch_result.success_rate}%")
```

Ver `lib/README.md` para documentación completa y ejemplos.

## Referencias

- **Kestra General**: `workflow/kestra/README.md`
- **Librerías**: `workflow/kestra/flows/lib/README.md`
- **Mejoras v2.0.0**: `workflow/kestra/flows/IMPROVEMENTS_SUMMARY.md`
- **Kestra Documentation**: [kestra.io/docs](https://kestra.io/docs/)
- **Ejemplos de Integración**: Ver flows individuales en esta carpeta

