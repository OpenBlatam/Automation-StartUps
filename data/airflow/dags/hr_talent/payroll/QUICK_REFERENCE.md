# Referencia Rápida - Sistema de Nómina

Guía de referencia rápida para uso común del sistema.

## 🚀 Inicio Rápido

### Setup Básico

```python
from payroll import PayrollStorage, HourCalculator, DeductionCalculator, PaymentCalculator

# Inicializar
storage = PayrollStorage()
hour_calc = HourCalculator()
deduction_calc = DeductionCalculator()
payment_calc = PaymentCalculator(hour_calc, deduction_calc)
```

### Procesamiento Básico

```python
# Obtener empleado
employee = storage.get_employee("EMP001")

# Obtener entradas de tiempo
time_entries = storage.get_time_entries("EMP001", period_start, period_end)

# Calcular
calculation = payment_calc.calculate_pay_period(...)

# Guardar
storage.save_pay_period(calculation)
```

## 📋 Comandos Comunes

### Health Check
```bash
python -m payroll.scripts.health_check --conn-id postgres_default
```

### Recovery
```bash
python -m payroll.scripts.recovery_helper failed --hours 24
python -m payroll.scripts.recovery_helper summary
```

### Setup Schema
```bash
python -m payroll.scripts.setup_schema --conn-id postgres_default
```

## 🔧 Funciones Más Usadas

### Cálculos
- `HourCalculator.calculate_overtime()` - Calcula horas
- `DeductionCalculator.calculate_deductions()` - Calcula deducciones
- `PaymentCalculator.calculate_pay_period()` - Calcula pago completo

### Storage
- `PayrollStorage.get_employee()` - Obtiene empleado
- `PayrollStorage.get_time_entries()` - Obtiene entradas de tiempo
- `PayrollStorage.save_pay_period()` - Guarda período
- `PayrollStorage.get_expenses_total()` - Obtiene gastos

### OCR
- `OCRProcessor.process_receipt()` - Procesa recibo

### Reportes
- `PayrollReporter.generate_period_report()` - Genera reporte
- `PayrollExporter.export_payroll_to_csv()` - Exporta CSV

### Notificaciones
- `PayrollNotifier.notify_payroll_completed()` - Notifica nómina
- `PayrollNotifier.notify_payroll_error()` - Notifica error

### Aprobaciones
- `PayrollApprovalSystem.request_approval()` - Solicita aprobación
- `PayrollApprovalSystem.approve()` - Aprueba

## 📊 Métricas y Análisis

### Métricas
```python
from payroll import PayrollMetricsCollector

metrics = PayrollMetricsCollector()
period_metrics = metrics.collect_period_metrics(period_start, period_end)
```

### Análisis
```python
from payroll import PayrollAnalytics

analytics = PayrollAnalytics()
anomalies = analytics.detect_anomalies(period_start, period_end)
cost_analysis = analytics.cost_analysis(period_start, period_end)
```

### Dashboard
```python
from payroll import PayrollDashboard

dashboard = PayrollDashboard()
dashboard_data = dashboard.get_dashboard_data()
kpis = dashboard.get_kpi_summary()
```

## 🔔 Alertas y Notificaciones

### Alertas
```python
from payroll import PayrollAlertSystem

alerts = PayrollAlertSystem()
alerts_list = alerts.run_all_checks(period_start, period_end)
```

### Eventos
```python
from payroll import event_bus, EventType, PayrollEvent

# Publicar evento
event = PayrollEvent(
    event_type=EventType.PAYROLL_CALCULATED,
    payload={"employee_id": "EMP001", "net_pay": 5000.00}
)
event_bus.publish(event)
```

## 🔐 Seguridad y Compliance

### Compliance
```python
from payroll import PayrollCompliance

compliance = PayrollCompliance()
violations = compliance.run_all_checks(...)
```

### Auditoría
```python
from payroll import PayrollAuditor, AuditEventType

auditor = PayrollAuditor()
auditor.log_event(
    event_type=AuditEventType.PAYROLL_CALCULATED,
    entity_type="pay_period",
    entity_id=123,
    employee_id="EMP001",
    action="calculate"
)
```

## ⚡ Optimización

### Caché
```python
from payroll import PayrollCache

cache = PayrollCache(enabled=True, ttl_seconds=1800)
```

### Batch Processing
```python
from payroll import BatchProcessor

batch_processor = BatchProcessor()
results = batch_processor.process_batch(items, processor_func, batch_size=50)
```

### Rate Limiting
```python
from payroll import PayrollRateLimiter

rate_limiter = PayrollRateLimiter()
if rate_limiter.check_payroll_calculation():
    # Procesar
    pass
```

## 🔗 Integraciones

### QuickBooks
```python
from payroll import QuickBooksIntegration

qb = QuickBooksIntegration(access_token="...", realm_id="...")
qb.sync_payroll_period(period_data)
```

### Stripe
```python
from payroll import StripeIntegration

stripe = StripeIntegration(api_key="...")
stripe.create_payout(employee_id, amount, currency="usd")
```

### Webhooks
```python
from payroll import PayrollWebhookHandler

webhook = PayrollWebhookHandler(webhook_url="...", secret_key="...")
webhook.send_webhook(WebhookEventType.PAYROLL_CALCULATED, data)
```

## 🛠️ Mantenimiento

### Mantenimiento
```python
from payroll import PayrollMaintenance

maintenance = PayrollMaintenance()
maintenance.archive_old_pay_periods(retention_days=365)
maintenance.optimize_tables()
```

### Backup
```python
from payroll import PayrollBackup

backup = PayrollBackup()
backup.backup_pay_periods(period_start, period_end)
```

### Health Checks
```python
from payroll import PayrollHealthChecker

health_checker = PayrollHealthChecker()
health = health_checker.comprehensive_health_check()
```

## 📈 Monitoreo

### Monitoreo
```python
from payroll import PayrollMonitor

monitor = PayrollMonitor()
metrics = monitor.get_system_metrics()
health = monitor.check_system_health()
```

### Observabilidad
```python
from payroll import observability, observe_operation

@observe_operation("process_payroll")
def process_payroll():
    # Tu código
    pass
```

## 🔄 Recovery

### Recovery
```python
from payroll import PayrollRecovery

recovery = PayrollRecovery()
plan = recovery.recover_failed_calculation(employee_id, period_start, period_end)
failed_ops = recovery.get_failed_operations(hours=24)
```

## 🎯 Workflows

### Workflows
```python
from payroll import create_payroll_workflow

workflow = create_payroll_workflow("my_workflow")
workflow.add_step("step1", func1)
workflow.add_step("step2", func2, depends_on=["step1"])
execution = workflow.execute(context)
```

## 📊 Benchmarking

### Benchmarking
```python
from payroll import PayrollBenchmark

benchmark = PayrollBenchmark()
result = benchmark.benchmark_function("my_function", my_function, iterations=10)
summary = benchmark.get_summary()
```

## 🎛️ Configuración

### Configuración
```python
from payroll import PayrollAdvancedConfig

config = PayrollAdvancedConfig.from_env()
config.apply_overrides({"regular_hours_per_week": 35.0})
is_valid, error = config.validate()
```

### Feature Flags
```python
from payroll import feature_flags, FeatureFlag

if feature_flags.is_enabled(FeatureFlag.ANOMALY_DETECTION):
    # Usar detección de anomalías
    pass
```

## 📚 Referencias Rápidas

- **Módulos**: Ver [MODULES.md](MODULES.md)
- **API**: Ver [API.md](API.md)
- **Ejemplos**: Ver [EXAMPLES.md](EXAMPLES.md)
- **Casos de Uso**: Ver [USE_CASES.md](USE_CASES.md)
- **Integraciones**: Ver [INTEGRATION.md](INTEGRATION.md)

## 🆘 Troubleshooting

### Problemas Comunes

**Schema no encontrado**
```bash
python -m payroll.scripts.setup_schema --conn-id postgres_default
```

**Health check falla**
```bash
python -m payroll.scripts.health_check --conn-id postgres_default
```

**Operaciones fallidas**
```bash
python -m payroll.scripts.recovery_helper failed --hours 24
```

## 💡 Tips

1. Usa batch processing para grandes volúmenes
2. Habilita caché para consultas frecuentes
3. Configura rate limiting para protección
4. Usa circuit breakers para servicios externos
5. Monitorea métricas regularmente
6. Revisa alertas diariamente
7. Ejecuta health checks periódicamente

