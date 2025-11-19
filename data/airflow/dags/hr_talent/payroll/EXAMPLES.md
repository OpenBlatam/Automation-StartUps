# Ejemplos de Uso - Sistema de Nómina

Ejemplos completos de uso del sistema de nómina.

## Ejemplo 1: Procesamiento Básico de Nómina

```python
from payroll import (
    HourCalculator,
    DeductionCalculator,
    PaymentCalculator,
    PayrollStorage,
    get_pay_period_dates
)
from datetime import date
from decimal import Decimal

# Configurar
storage = PayrollStorage(postgres_conn_id="postgres_default")
period_start, period_end = get_pay_period_dates(period_type="biweekly")

# Obtener empleado
employee = storage.get_employee("EMP001")
if not employee:
    print("Employee not found")
    exit(1)

# Obtener entradas de tiempo
time_entries = storage.get_time_entries("EMP001", period_start, period_end)

# Obtener gastos
expenses = storage.get_expenses_total("EMP001", period_start, period_end)

# Calcular
hour_calc = HourCalculator()
deduction_calc = DeductionCalculator()
payment_calc = PaymentCalculator(hour_calc, deduction_calc)

calculation = payment_calc.calculate_pay_period(
    employee_id=employee["employee_id"],
    hourly_rate=employee["hourly_rate"],
    employee_type=employee["employee_type"],
    period_start=period_start,
    period_end=period_end,
    pay_date=period_end + timedelta(days=7),
    time_entries=time_entries,
    expenses_total=expenses
)

# Guardar
pay_period_id = storage.save_pay_period(calculation)
print(f"Pay period saved: {pay_period_id}")
print(f"Net pay: ${calculation.net_pay}")
```

## Ejemplo 2: Procesamiento OCR de Recibos

```python
from payroll import OCRProcessor, PayrollStorage
import base64

# Inicializar OCR
processor = OCRProcessor(
    provider="tesseract",
    confidence_threshold=0.7
)

storage = PayrollStorage()

# Leer imagen de recibo
with open("receipt.jpg", "rb") as f:
    image_data = f.read()

# Procesar
result = processor.process_receipt(image_data)

if result.success:
    extracted = result.extracted_data
    
    # Guardar recibo
    receipt_id = storage.save_expense_receipt(
        employee_id="EMP001",
        expense_date=date.today(),
        amount=Decimal(str(extracted.get("amount", 0))),
        ocr_result=result,
        receipt_image_base64=base64.b64encode(image_data).decode(),
        vendor=extracted.get("vendor"),
        description=extracted.get("description")
    )
    
    print(f"Receipt processed: {receipt_id}")
    print(f"Amount: ${extracted.get('amount')}")
else:
    print(f"OCR failed: {result.error_message}")
```

## Ejemplo 3: Sistema de Aprobaciones

```python
from payroll import PayrollApprovalSystem, ApprovalLevel

approval_system = PayrollApprovalSystem()
approval_system.ensure_approval_tables()

# Solicitar aprobación
approval_id = approval_system.request_approval(
    entity_type="pay_period",
    entity_id=123,
    employee_id="EMP001",
    approval_level=ApprovalLevel.MANAGER,
    requested_by="system"
)

# Obtener pendientes
pending = approval_system.get_pending_approvals(
    approval_level=ApprovalLevel.MANAGER
)

for approval in pending:
    print(f"Pending: {approval['entity_type']} {approval['entity_id']}")
    
    # Aprobar
    approval_system.approve(
        approval_id=approval["id"],
        approved_by="manager@example.com"
    )
```

## Ejemplo 4: Generación de Reportes

```python
from payroll import PayrollReporter, PayrollExporter
from datetime import date

reporter = PayrollReporter()
exporter = PayrollExporter()

period_start = date(2025, 1, 1)
period_end = date(2025, 1, 14)

# Generar reporte
report = reporter.generate_period_report(period_start, period_end)

print(f"Employees: {report.employee_count}")
print(f"Total Net Pay: ${report.total_net_pay}")

# Exportar a CSV
csv_data = exporter.export_payroll_to_csv(
    period_start, period_end
)

with open("payroll_report.csv", "w") as f:
    f.write(csv_data)

# Exportar a Excel
excel_file = exporter.export_payroll_to_excel(
    period_start, period_end,
    output_path="payroll_report.xlsx"
)
```

## Ejemplo 5: Análisis y Detección de Anomalías

```python
from payroll import PayrollAnalytics
from datetime import date

analytics = PayrollAnalytics()

period_start = date(2025, 1, 1)
period_end = date(2025, 1, 14)

# Detectar anomalías
anomalies = analytics.detect_anomalies(
    period_start, period_end,
    threshold_std=2.0
)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.employee_id}")
    print(f"  Type: {anomaly.anomaly_type}")
    print(f"  Severity: {anomaly.severity}")
    print(f"  Value: ${anomaly.value}")
    print(f"  Description: {anomaly.description}")

# Análisis de costos
cost_analysis = analytics.cost_analysis(period_start, period_end)
print(f"Cost per hour: ${cost_analysis['efficiency_metrics']['cost_per_hour']}")
print(f"Overtime percentage: {cost_analysis['efficiency_metrics']['overtime_percentage']}%")
```

## Ejemplo 6: Dashboard y Métricas

```python
from payroll import PayrollDashboard, PayrollMetricsCollector

dashboard = PayrollDashboard()
metrics = PayrollMetricsCollector()

# Obtener datos del dashboard
dashboard_data = dashboard.get_dashboard_data()

print(f"Total Employees: {dashboard_data.total_employees}")
print(f"Total Net Pay: ${dashboard_data.total_net_pay}")
print(f"Pending Approvals: {dashboard_data.pending_approvals}")

# Obtener KPIs
kpis = dashboard.get_kpi_summary()
print(f"Current Period Net Pay: ${kpis['current_period']['total_net_pay']}")

# Obtener series temporales
time_series = dashboard.get_time_series_data(periods=12)
print(f"Analyzed {time_series['summary']['total_periods']} periods")
```

## Ejemplo 7: Búsqueda Avanzada

```python
from payroll import PayrollSearch, SearchFilters
from decimal import Decimal

search = PayrollSearch()

# Crear filtros
filters = SearchFilters(
    min_net_pay=Decimal("1000.00"),
    department="Engineering",
    period_start_min=date(2025, 1, 1),
    status="approved"
)

# Buscar
results = search.search_pay_periods(
    filters=filters,
    limit=50,
    offset=0
)

print(f"Found {results['total']} records")
for record in results["records"]:
    print(f"{record['employee_name']}: ${record['net_pay']}")

# Obtener estadísticas
stats = search.get_statistics(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

print(f"Average Net Pay: ${stats['average_net_pay']}")
```

## Ejemplo 8: Integración con QuickBooks

```python
from payroll import QuickBooksIntegration
from decimal import Decimal

qb = QuickBooksIntegration(
    access_token="your_token",
    realm_id="your_realm_id",
    base_url="https://sandbox-quickbooks.api.intuit.com"
)

# Crear gasto de nómina
expense_id = qb.create_payroll_expense(
    employee_name="John Doe",
    amount=Decimal("5000.00"),
    expense_date=date(2025, 1, 15),
    description="Biweekly payroll"
)

print(f"QuickBooks expense created: {expense_id}")

# Sincronizar período completo
period_data = {
    "period_start": date(2025, 1, 1),
    "period_end": date(2025, 1, 14),
    "pay_date": date(2025, 1, 21),
    "employees": [
        {
            "name": "John Doe",
            "net_pay": 5000.00
        }
    ]
}

qb.sync_payroll_period(period_data)
```

## Ejemplo 9: Health Checks y Mantenimiento

```python
from payroll import PayrollHealthChecker, PayrollMaintenance

# Health check
health_checker = PayrollHealthChecker()
health = health_checker.comprehensive_health_check()

print(f"System Status: {health['overall_status']}")
for name, check in health['checks'].items():
    print(f"  {name}: {check['status']} - {check['message']}")

# Mantenimiento
maintenance = PayrollMaintenance()

# Archivado
archive_result = maintenance.archive_old_pay_periods(
    retention_days=365,
    dry_run=False
)

print(f"Archived: {archive_result['archived']} records")

# Optimización
optimize_result = maintenance.optimize_tables()
print(f"Optimized: {optimize_result['optimized']} tables")
```

## Ejemplo 10: Procesamiento por Lotes

```python
from payroll import BatchProcessor, PayrollStorage
from payroll.hour_calculator import TimeEntry, HoursType

storage = PayrollStorage()

# Crear múltiples entradas de tiempo
time_entries = [
    TimeEntry(
        employee_id="EMP001",
        work_date=date(2025, 1, i),
        hours_worked=Decimal("8.0"),
        hours_type=HoursType.REGULAR,
        hourly_rate=Decimal("25.00")
    )
    for i in range(1, 15)
]

# Guardar en lote
def save_entry(entry):
    storage.save_time_entry(entry)

batch_processor = BatchProcessor()
results = batch_processor.process_batch(
    items=time_entries,
    processor_func=save_entry,
    batch_size=10,
    max_workers=4
)

print(f"Processed: {results['processed']}")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
```

## Ejemplo 11: Notificaciones

```python
from payroll import PayrollNotifier
from decimal import Decimal

notifier = PayrollNotifier(
    slack_webhook_url="https://hooks.slack.com/...",
    email_api_url="https://api.example.com/email"
)

# Notificar nómina completada
notifier.notify_payroll_completed(
    employee_id="EMP001",
    employee_name="John Doe",
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14),
    net_pay=Decimal("5000.00"),
    details={
        "hours": 80.0,
        "deductions": 1000.0,
        "expenses": 100.0
    }
)

# Notificar error
notifier.notify_payroll_error(
    employee_id="EMP001",
    error_message="Invalid time entries",
    context={"period": "2025-01-01 to 2025-01-14"}
)
```

## Ejemplo 12: Auditoría

```python
from payroll import PayrollAuditor, AuditEventType

auditor = PayrollAuditor()
auditor.ensure_audit_table()

# Registrar evento
auditor.log_event(
    event_type=AuditEventType.PAYROLL_CALCULATED,
    entity_type="pay_period",
    entity_id=123,
    employee_id="EMP001",
    action="calculate",
    new_values={
        "net_pay": 5000.00,
        "gross_pay": 6000.00
    },
    user_id="system"
)

# Obtener historial
trail = auditor.get_audit_trail(
    employee_id="EMP001",
    event_type=AuditEventType.PAYROLL_CALCULATED
)

for event in trail:
    print(f"{event['created_at']}: {event['action']} - {event['event_type']}")
```

## Ejemplo 13: Seguridad y Validación

```python
from payroll import PayrollSecurity, PayrollValidator
from decimal import Decimal

security = PayrollSecurity()
validator = PayrollValidator()

# Sanitizar entrada
user_input = "<script>alert('xss')</script>"
sanitized = security.sanitize_input(user_input)
print(f"Sanitized: {sanitized}")

# Validar email
is_valid = security.validate_email("user@example.com")
print(f"Email valid: {is_valid}")

# Validar entradas de tiempo
from payroll.hour_calculator import TimeEntry, HoursType
from datetime import date

entries = [
    TimeEntry(
        employee_id="EMP001",
        work_date=date(2025, 1, 1),
        hours_worked=Decimal("8.0"),
        hours_type=HoursType.REGULAR,
        hourly_rate=Decimal("25.00")
    )
]

is_valid, error, warnings = validator.validate_time_entries(
    entries, date(2025, 1, 1), date(2025, 1, 14)
)

if not is_valid:
    print(f"Validation failed: {error}")
else:
    print("Validation passed")
    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")
```

## Ejemplo 14: Uso Completo del DAG

El DAG `payroll_processing` puede ejecutarse con diferentes parámetros:

```python
# Desde Airflow UI o CLI
# Procesar todos los empleados
airflow dags trigger payroll_processing \
    --conf '{"process_all_employees": true, "dry_run": false}'

# Procesar empleados específicos
airflow dags trigger payroll_processing \
    --conf '{
        "process_all_employees": false,
        "employee_ids": "EMP001,EMP002,EMP003",
        "period_start": "2025-01-01",
        "period_end": "2025-01-14"
    }'

# Modo dry-run
airflow dags trigger payroll_processing \
    --conf '{"dry_run": true}'

# Con auto-aprobación de gastos
airflow dags trigger payroll_processing \
    --conf '{
        "auto_approve_expenses": true,
        "auto_approve_expenses_threshold": 50.0
    }'
```

## Ejemplo 15: Scripts de Utilidad

```bash
# Setup del schema
python -m payroll.scripts.setup_schema \
    --conn-id postgres_default \
    --schema-file data/db/payroll_schema.sql

# Health check
python -m payroll.scripts.health_check \
    --conn-id postgres_default

# Health check en JSON
python -m payroll.scripts.health_check \
    --conn-id postgres_default \
    --json
```

## Más Información

Para más detalles, consulta:
- [README.md](README.md) - Documentación completa
- [API.md](API.md) - Documentación de API
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios

