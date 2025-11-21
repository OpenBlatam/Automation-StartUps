# Guía de Integración - Sistema de Nómina

Guía completa para integrar el sistema de nómina con otros sistemas y servicios.

## 🔌 Integraciones Disponibles

### 1. QuickBooks

#### Configuración

```python
from payroll import QuickBooksIntegration

qb = QuickBooksIntegration(
    access_token="your_access_token",
    realm_id="your_realm_id",
    base_url="https://sandbox-quickbooks.api.intuit.com"  # o producción
)
```

#### Uso

```python
# Crear gasto
expense_id = qb.create_payroll_expense(
    employee_name="John Doe",
    amount=Decimal("5000.00"),
    expense_date=date(2025, 1, 15),
    description="Biweekly payroll"
)

# Sincronizar período
period_data = {
    "period_start": date(2025, 1, 1),
    "period_end": date(2025, 1, 14),
    "pay_date": date(2025, 1, 21),
    "employees": [...]
}

qb.sync_payroll_period(period_data)
```

### 2. Stripe

#### Configuración

```python
from payroll import StripeIntegration

stripe = StripeIntegration(
    api_key="sk_test_...",
    test_mode=True
)
```

#### Uso

```python
# Crear payout
payout = stripe.create_payout(
    employee_id="EMP001",
    amount=Decimal("5000.00"),
    currency="usd",
    description="Biweekly payroll"
)
```

### 3. Slack

#### Configuración

```python
from payroll import SlackIntegration

slack = SlackIntegration(
    webhook_url="https://hooks.slack.com/services/...",
    channel="#payroll"
)
```

#### Uso

```python
# Enviar notificación
slack.send_notification(
    message="Payroll processing completed",
    attachments=[...]
)
```

### 4. Webhooks

#### Configuración

```python
from payroll import PayrollWebhookHandler

webhook = PayrollWebhookHandler(
    webhook_url="https://api.example.com/webhook",
    secret_key="your_secret_key"
)
```

#### Uso

```python
# Enviar webhook
webhook.send_webhook(
    event_type=WebhookEventType.PAYROLL_CALCULATED,
    data={
        "employee_id": "EMP001",
        "net_pay": 5000.00
    }
)
```

### 5. Sistema de Eventos

#### Subscripción a Eventos

```python
from payroll import event_bus, EventType, PayrollEvent

def handle_payroll_calculated(event: PayrollEvent):
    print(f"Payroll calculated: {event.payload}")

# Suscribirse
event_bus.subscribe(
    EventType.PAYROLL_CALCULATED,
    handle_payroll_calculated
)

# Publicar evento
event = PayrollEvent(
    event_type=EventType.PAYROLL_CALCULATED,
    payload={"employee_id": "EMP001", "net_pay": 5000.00}
)

event_bus.publish(event)
```

## 🔄 Sincronización

### Sincronización con Sistemas Externos

```python
from payroll import PayrollSync

sync = PayrollSync()

# Definir handler de sincronización
def sync_handler(period_data):
    # Enviar a sistema externo
    external_api.create_payroll(period_data)
    return True

# Sincronizar
result = sync.sync_payroll_periods_to_external(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14),
    sync_handler=sync_handler
)

# Marcar como sincronizado
sync.mark_synced(
    entity_type="pay_period",
    entity_id=123,
    external_id="EXT-123"
)
```

## 📊 API REST

### Estructura de Endpoints

```python
from payroll import PayrollAPI

api = PayrollAPI(base_url="http://localhost:8000")

# Obtener empleado
response = api.get_employee("EMP001")

# Calcular nómina
response = api.calculate_payroll(
    employee_id="EMP001",
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

# Obtener métricas
response = api.get_metrics(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)
```

## 🔐 Autenticación

### Configuración de Autenticación

```python
from payroll import PayrollSecurity

security = PayrollSecurity()

# Generar token
token = security.generate_audit_token(
    entity_id="123",
    action="calculate"
)

# Verificar token
is_valid = security.verify_audit_token(token)
```

## 📡 Webhooks Outbound

### Configurar Webhooks Salientes

```python
from payroll import PayrollWebhookHandler, WebhookEventType

webhook = PayrollWebhookHandler(
    webhook_url="https://api.example.com/webhook",
    secret_key="secret_key"
)

# Enviar webhook
webhook.send_webhook(
    event_type=WebhookEventType.PAYROLL_CALCULATED,
    data={
        "employee_id": "EMP001",
        "net_pay": 5000.00,
        "period_start": "2025-01-01",
        "period_end": "2025-01-14"
    }
)
```

## 📥 Webhooks Inbound

### Recibir Webhooks

```python
from payroll import PayrollWebhookReceiver, WebhookEventType

receiver = PayrollWebhookReceiver(secret_key="secret_key")

# Registrar handler
def handle_webhook(data):
    print(f"Received webhook: {data}")

receiver.register_handler(
    WebhookEventType.PAYROLL_PAID,
    handle_webhook
)

# Procesar webhook recibido
receiver.process_webhook(
    payload={
        "event_type": "payroll.paid",
        "data": {...}
    },
    signature="signature_from_header"
)
```

## 🔄 Integración con Airflow

### Uso en DAGs

```python
from airflow.decorators import dag, task
from payroll import PayrollStorage, PaymentCalculator

@dag(...)
def my_payroll_dag():
    @task
    def process_payroll(**context):
        storage = PayrollStorage()
        # ... procesamiento
        return result
    
    process_payroll()
```

## 🧪 Testing de Integraciones

### Testing de Integraciones

```python
from payroll.testing import PayrollTestData

# Crear datos de prueba
test_data = PayrollTestData.create_test_dataset(
    num_employees=5,
    num_periods=2
)

# Usar en tests
for employee in test_data["employees"]:
    # Probar integración
    result = integration.process(employee)
    assert result.success
```

## 🔧 Configuración Avanzada

### Configuración Personalizada

```python
from payroll import PayrollAdvancedConfig

config = PayrollAdvancedConfig.from_env()

# Aplicar overrides
config.apply_overrides({
    "regular_hours_per_week": 35.0,
    "overtime_multiplier": 1.75
})

# Validar
is_valid, error = config.validate()
if not is_valid:
    print(f"Config error: {error}")
```

## 📝 Mejores Prácticas

### 1. Manejo de Errores

```python
try:
    result = integration.process(data)
except Exception as e:
    logger.error(f"Integration error: {e}")
    # Fallback o retry
```

### 2. Rate Limiting

```python
from payroll import PayrollRateLimiter

rate_limiter = PayrollRateLimiter()

if rate_limiter.check_payroll_calculation():
    # Procesar
    pass
else:
    # Esperar o rechazar
    pass
```

### 3. Circuit Breakers

```python
from payroll import PayrollCircuitBreakers

circuit_breakers = PayrollCircuitBreakers()

try:
    result = circuit_breakers.call_ocr(ocr_function, image_data)
except Exception as e:
    # Circuit breaker abierto
    logger.error(f"OCR service unavailable: {e}")
```

## 🎯 Casos de Uso Comunes

### 1. Sincronización Automática

```python
# En DAG de Airflow
@task
def sync_to_quickbooks(**context):
    sync = PayrollSync()
    # Sincronizar períodos no sincronizados
    unsynced = sync.get_unsynced_records("pay_period")
    for record in unsynced:
        # Sincronizar
        sync_handler(record)
        sync.mark_synced("pay_period", record["id"])
```

### 2. Notificaciones Automáticas

```python
# En event handler
def on_payroll_calculated(event):
    # Enviar a Slack
    slack.send_notification(f"Payroll calculated: {event.payload}")
    
    # Enviar webhook
    webhook.send_webhook(WebhookEventType.PAYROLL_CALCULATED, event.payload)
```

### 3. Monitoreo de Integraciones

```python
# Verificar estado de circuit breakers
states = circuit_breakers.get_all_states()
for name, state in states.items():
    if state["state"] == "open":
        logger.warning(f"Circuit breaker {name} is OPEN")
```

## 📚 Recursos Adicionales

- [API Documentation](API.md)
- [Examples](EXAMPLES.md)
- [Architecture](ARCHITECTURE.md)
- [Deployment](DEPLOYMENT.md)

