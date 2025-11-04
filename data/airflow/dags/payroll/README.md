# Sistema de Procesamiento de Nómina y Gastos

Sistema automatizado completo para procesar nómina, calcular horas trabajadas, deducciones, pagos y manejar recibos de gastos con OCR.

## 📋 Características

### Core
- ✅ **Cálculo de Horas**: Automático de horas regulares, overtime y double time
- ✅ **Cálculo de Deducciones**: Impuestos, beneficios y reglas personalizadas
- ✅ **Cálculo de Pagos**: Integración completa de horas, deducciones y gastos
- ✅ **Procesamiento OCR**: Soporte para Tesseract, AWS Textract y Google Cloud Vision
- ✅ **Almacenamiento**: Persistencia completa en PostgreSQL con caché

### Automatización
- ✅ **Notificaciones**: Multi-canal (Slack, Email, Webhooks)
- ✅ **Sistema de Aprobaciones**: Workflows multi-nivel con auto-aprobación
- ✅ **Validaciones**: Validación robusta de datos y reglas de negocio
- ✅ **Manejo de Errores**: Excepciones personalizadas y retry logic

### Análisis y Reportes
- ✅ **Reportes**: Vistas materializadas para análisis
- ✅ **Métricas y KPIs**: Recolección en tiempo real
- ✅ **Análisis Avanzados**: Detección de anomalías, tendencias, costos
- ✅ **Dashboard**: Datos en tiempo real para visualización
- ✅ **Exportación**: CSV, JSON, Excel

### Seguridad y Compliance
- ✅ **Auditoría**: Trazabilidad completa de cambios
- ✅ **Seguridad**: Hashing, encriptación, validación de inputs
- ✅ **Backup**: Sistema de backup y recuperación
- ✅ **Health Checks**: Verificación automática del sistema

### Optimización
- ✅ **Caché**: Optimización de consultas frecuentes
- ✅ **Batch Processing**: Procesamiento paralelo optimizado
- ✅ **Mantenimiento**: Archivado, limpieza y optimización automática
- ✅ **Búsqueda Avanzada**: Filtrado y búsqueda eficiente

### Integraciones
- ✅ **QuickBooks**: Sincronización de gastos y períodos
- ✅ **Stripe**: Creación de payouts
- ✅ **Sistemas Contables**: Exportación de journal entries
- ✅ **Slack**: Notificaciones avanzadas

## 🏗️ Arquitectura

```
payroll/
├── __init__.py              # Exports principales
├── config.py                # Configuración centralizada
├── hour_calculator.py        # Cálculo de horas trabajadas
├── deduction_calculator.py  # Cálculo de deducciones
├── payment_calculator.py     # Cálculo de pagos completos
├── ocr_processor.py          # Procesamiento OCR de recibos
├── storage.py                # Almacenamiento en PostgreSQL
├── exceptions.py             # Excepciones personalizadas
├── utils.py                  # Funciones de utilidad
├── notifications.py          # Sistema de notificaciones
├── reports.py                # Generador de reportes
├── validators.py             # Validadores de negocio
├── audit.py                  # Sistema de auditoría
├── exporters.py              # Exportadores de datos
├── cache.py                  # Sistema de caché
└── README.md                 # Esta documentación
```

## 📦 Módulos Principales

### 1. HourCalculator

Calcula horas trabajadas, incluyendo overtime y double time.

```python
from payroll import HourCalculator, TimeEntry, HoursType
from datetime import date, datetime
from decimal import Decimal

calculator = HourCalculator(
    regular_hours_per_week=Decimal("40.0"),
    overtime_multiplier=Decimal("1.5"),
    double_time_multiplier=Decimal("2.0")
)

# Calcular horas desde timestamps
hours = calculator.calculate_hours_from_timestamps(
    clock_in=datetime(2025, 1, 1, 9, 0),
    clock_out=datetime(2025, 1, 1, 17, 30)
)
```

### 2. DeductionCalculator

Calcula deducciones basadas en reglas configurables.

```python
from payroll import DeductionCalculator, DeductionRule
from decimal import Decimal

calculator = DeductionCalculator(
    default_tax_rate=Decimal("0.25"),
    default_benefits_rate=Decimal("0.10")
)

# Agregar regla personalizada
rule = DeductionRule(
    rule_name="Impuesto Federal",
    deduction_type="impuestos",
    amount_type="percentage",
    percentage_value=Decimal("0.15"),
    priority=1
)
calculator.add_rule(rule)
```

### 3. PaymentCalculator

Combina horas, deducciones y gastos para calcular el pago neto.

```python
from payroll import PaymentCalculator, HourCalculator, DeductionCalculator

hour_calc = HourCalculator()
deduction_calc = DeductionCalculator()
payment_calc = PaymentCalculator(hour_calc, deduction_calc)

calculation = payment_calc.calculate_pay_period(
    employee_id="EMP001",
    hourly_rate=Decimal("25.00"),
    employee_type="hourly",
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14),
    pay_date=date(2025, 1, 21),
    time_entries=time_entries,
    expenses_total=Decimal("100.00")
)
```

### 4. OCRProcessor

Procesa recibos de gastos con OCR.

```python
from payroll import OCRProcessor

processor = OCRProcessor(
    provider="tesseract",  # o "aws_textract" o "google_vision"
    confidence_threshold=0.7
)

with open("receipt.jpg", "rb") as f:
    image_data = f.read()

result = processor.process_receipt(image_data)
```

### 5. PayrollStorage

Maneja la persistencia en PostgreSQL con caché.

```python
from payroll import PayrollStorage, PayrollCache

cache = PayrollCache(enabled=True, ttl_seconds=3600)
storage = PayrollStorage(postgres_conn_id="postgres_default", cache=cache)

# Operaciones cacheadas automáticamente
employee = storage.get_employee("EMP001")
```

### 6. PayrollNotifier

Sistema de notificaciones multi-canal.

```python
from payroll import PayrollNotifier

notifier = PayrollNotifier(
    slack_webhook_url="https://hooks.slack.com/...",
    email_api_url="https://api.example.com/email",
    webhook_url="https://api.example.com/webhook"
)

notifier.notify_payroll_completed(
    employee_id="EMP001",
    employee_name="John Doe",
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14),
    net_pay=Decimal("5000.00")
)
```

### 7. PayrollReporter

Genera reportes detallados.

```python
from payroll import PayrollReporter

reporter = PayrollReporter(postgres_conn_id="postgres_default")

# Reporte de período
report = reporter.generate_period_report(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

# Reporte por empleado
employee_report = reporter.generate_employee_report(
    employee_id="EMP001",
    start_date=date(2025, 1, 1),
    end_date=date(2025, 12, 31)
)
```

### 8. PayrollValidator

Validaciones de reglas de negocio.

```python
from payroll import PayrollValidator

validator = PayrollValidator(
    max_hours_per_day=Decimal("16.0"),
    max_hours_per_week=Decimal("80.0"),
    min_hourly_rate=Decimal("7.25")
)

is_valid, error, warnings = validator.validate_time_entries(
    time_entries, period_start, period_end
)
```

### 9. PayrollAuditor

Sistema de auditoría y trazabilidad.

```python
from payroll import PayrollAuditor, AuditEventType

auditor = PayrollAuditor(postgres_conn_id="postgres_default")
auditor.ensure_audit_table()

auditor.log_event(
    event_type=AuditEventType.PAYROLL_CALCULATED,
    entity_type="pay_period",
    entity_id="123",
    employee_id="EMP001",
    action="calculate",
    new_values={"net_pay": 5000.00}
)

# Obtener historial
trail = auditor.get_audit_trail(
    employee_id="EMP001",
    event_type=AuditEventType.PAYROLL_CALCULATED
)
```

### 10. PayrollExporter

Exporta datos a diferentes formatos.

```python
from payroll import PayrollExporter

exporter = PayrollExporter(postgres_conn_id="postgres_default")

# Exportar a CSV
csv_data = exporter.export_payroll_to_csv(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

# Exportar a JSON
json_data = exporter.export_payroll_to_json(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

# Exportar a Excel
excel_file = exporter.export_payroll_to_excel(
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14),
    output_path="payroll_report.xlsx"
)
```

## 🔧 Configuración

### Variables de Entorno

```bash
# PostgreSQL
PAYROLL_POSTGRES_CONN_ID=postgres_default

# OCR - Tesseract
TESSERACT_CMD=/usr/bin/tesseract
TESSERACT_LANG=eng

# OCR - AWS Textract
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# OCR - Google Vision
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_PROJECT_ID=your-project-id

# Notificaciones
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
EMAIL_API_URL=https://api.example.com/email
PAYROLL_WEBHOOK_URL=https://api.example.com/webhook

# Configuración de Nómina
PAYROLL_REGULAR_HOURS_PER_WEEK=40.0
PAYROLL_OVERTIME_MULTIPLIER=1.5
PAYROLL_DEFAULT_TAX_RATE=0.25
PAYROLL_DEFAULT_BENEFITS_RATE=0.10
```

### Base de Datos

Ejecutar el schema SQL:

```bash
psql $DATABASE_URL -f data/db/payroll_schema.sql
```

## 📊 DAG de Airflow

El DAG `payroll_processing` se ejecuta cada lunes a las 8 AM y procesa:

1. **Verificación de Schema**: Asegura que las tablas existan
2. **Procesamiento de Recibos**: OCR de recibos pendientes
3. **Cálculo de Nómina**: Para todos los empleados activos con validaciones
4. **Generación de Reportes**: Reportes detallados del período
5. **Actualización de Vistas**: Refresco de vistas materializadas

### Parámetros del DAG

- `period_start`: Fecha inicio del período (YYYY-MM-DD)
- `period_end`: Fecha fin del período (YYYY-MM-DD)
- `pay_date`: Fecha de pago (YYYY-MM-DD)
- `ocr_provider`: Proveedor OCR (tesseract, aws_textract, google_vision)
- `auto_approve_expenses`: Auto-aprobar gastos bajo umbral
- `auto_approve_expenses_threshold`: Umbral para auto-aprobación
- `process_all_employees`: Procesar todos los empleados
- `employee_ids`: Lista de IDs específicos (CSV)
- `dry_run`: Solo simular sin guardar

## 🚀 Uso Avanzado

### Caché Personalizado

```python
from payroll import PayrollStorage, PayrollCache

cache = PayrollCache(enabled=True, max_size=5000, ttl_seconds=7200)
storage = PayrollStorage(postgres_conn_id="postgres_default", cache=cache)

# Invalidar caché después de cambios
cache.invalidate("employee_EMP001")
```

### Decorador de Caché

```python
from payroll import cached, PayrollCache

cache = PayrollCache()

@cached(cache_instance=cache, key_prefix="calc", ttl_seconds=3600)
def expensive_calculation(employee_id: str, period_start: date):
    # Cálculo costoso que se cachea automáticamente
    return result
```

## 📝 Excepciones

El módulo incluye excepciones personalizadas:

- `PayrollError`: Excepción base
- `ConfigurationError`: Error de configuración
- `ValidationError`: Error de validación
- `CalculationError`: Error en cálculo
- `OCRError`: Error en OCR
- `StorageError`: Error en almacenamiento
- `EmployeeNotFoundError`: Empleado no encontrado

## 📚 Referencias

### Documentación
- [API Documentation](API.md) - Referencia completa de API
- [Examples](EXAMPLES.md) - 15 ejemplos de uso
- [Features](FEATURES.md) - Lista de características
- [Changelog](CHANGELOG.md) - Historial de cambios
- [Architecture](ARCHITECTURE.md) - Arquitectura del sistema
- [Summary](SUMMARY.md) - Resumen ejecutivo
- [Deployment](DEPLOYMENT.md) - Guía de despliegue
- [Integration](INTEGRATION.md) - Guía de integraciones
- [Modules](MODULES.md) - Índice de módulos
- [Use Cases](USE_CASES.md) - Casos de uso complejos
- [Quick Reference](QUICK_REFERENCE.md) - Referencia rápida
- [Troubleshooting](TROUBLESHOOTING.md) - Guía de troubleshooting
- [Diagrams](DIAGRAMS.md) - Diagramas y flujos visuales
- [Best Practices](BEST_PRACTICES.md) - Mejores prácticas
- [Code Standards](CODE_STANDARDS.md) - Estándares de código
- [Config Template](CONFIG_TEMPLATE.env) - Template de configuración
- [Testing](TESTING.md) - Guía de testing
- [Development](DEVELOPMENT.md) - Guía de desarrollo y debugging
- [Index](INDEX.md) - Índice completo del sistema

## 🚀 Últimas Mejoras

### Utilidades Avanzadas
- **PayrollAdvancedUtilities**: Clase con funciones avanzadas de cálculo
  - Proyecciones anuales con crecimiento
  - Análisis de impacto de overtime
  - Cálculo de break-even
  - Análisis de varianza
  - Cálculo de eficiencia y utilización
  - Agrupación por departamento
  - Cálculo de percentiles y estadísticas
  - Análisis de tendencias

### Herramientas de Debugging
- **PayrollDebugger**: Logging detallado de cálculos y operaciones
- **PayrollProfiler**: Medición de performance de operaciones
- **PayrollDataInspector**: Inspección de datos para debugging
- **Decoradores**: `@debug_timing`, `debug_context` para profiling
- **Validación de integridad**: Verificación automática de datos

### Transformadores de Datos
- **PayrollDataTransformer**: Normalización y transformación de datos
  - Normalización de employee IDs
  - Conversión de moneda a Decimal
  - Conversión de horas a Decimal
  - Normalización de fechas (múltiples formatos)
  - Limpieza de strings
  - Transformación de time entries y empleados
  - Validación y transformación con schemas
- **Script de validación**: `data_validator.py` para validar datos en batch

### Formateadores Avanzados
- **PayrollFormatter**: Formateo de datos de nómina
  - Formateo de moneda (múltiples formatos y símbolos)
  - Formateo de horas (decimal, horas:minutos, verbose)
  - Formateo de porcentajes
  - Formateo de rangos de período
  - Resúmenes de empleados
  - Desglose de cálculos
  - Tablas formateadas
  - JSON legible
  - Tarjetas de resumen (simple, bordered, fancy)
- **PayrollComparisonFormatter**: Comparación de períodos
  - Comparación lado a lado
  - Cálculo de varianza
  - Formateo de cambios porcentuales

### Archivos del Sistema
- [Schema SQL](../../../db/payroll_schema.sql) - Schema de base de datos
- [DAG Principal](../payroll_processing.py) - DAG de procesamiento
- [DAG de Mantenimiento](../payroll_maintenance.py) - DAG de mantenimiento

### Recursos Externos
- [Documentación de Airflow](https://airflow.apache.org/docs/)

## 🔧 Scripts de Utilidad

### Setup Schema
```bash
python -m payroll.scripts.setup_schema --conn-id postgres_default
```

### Health Check
```bash
python -m payroll.scripts.health_check --conn-id postgres_default
```

### Recovery Helper
```bash
python -m payroll.scripts.recovery_helper failed --hours 24
python -m payroll.scripts.recovery_helper rollback --pay-period-id 123
python -m payroll.scripts.recovery_helper summary
```

### Data Validator
```bash
# Validar todos los datos
python -m payroll.scripts.data_validator --type all --conn-id postgres_default

# Validar solo empleados
python -m payroll.scripts.data_validator --type employees

# Validar solo entradas de tiempo (últimos 30 días)
python -m payroll.scripts.data_validator --type time_entries --days 30

# Output en JSON
python -m payroll.scripts.data_validator --type all --format json
```

## 🎯 Quick Start

```python
from payroll import (
    PayrollStorage,
    HourCalculator,
    DeductionCalculator,
    PaymentCalculator,
    get_pay_period_dates
)
from datetime import date, timedelta

# Setup
storage = PayrollStorage()
period_start, period_end = get_pay_period_dates(period_type="biweekly")

# Obtener datos
employee = storage.get_employee("EMP001")
time_entries = storage.get_time_entries("EMP001", period_start, period_end)
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
storage.save_pay_period(calculation)
print(f"Net Pay: ${calculation.net_pay}")
```

## 📊 DAGs Disponibles

### 1. payroll_processing
**Schedule**: Cada lunes a las 8 AM

Procesamiento completo de nómina:
- Procesamiento OCR de recibos
- Cálculo de nómina para todos los empleados
- Detección de anomalías
- Recolección de métricas
- Generación de reportes
- Datos para dashboard
- Refresco de vistas

### 2. payroll_maintenance
**Schedule**: Domingos a las 2 AM

Mantenimiento del sistema:
- Archivado de períodos antiguos
- Limpieza de datos antiguos
- Optimización de tablas
- Refresco de vistas
- Creación de backups
- Reportes de mantenimiento

## 🏆 Características Destacadas

- **24 módulos** funcionales
- **2 DAGs** de Airflow completamente integrados
- **Procesamiento paralelo** optimizado
- **Detección automática** de anomalías
- **Dashboard en tiempo real**
- **Integraciones** con sistemas externos
- **Seguridad** y compliance
- **Documentación completa**

## 🧪 Dependencias Opcionales

```bash
# Para OCR
pip install pytesseract pillow  # Tesseract
pip install boto3  # AWS Textract
pip install google-cloud-vision  # Google Vision

# Para exportación Excel
pip install pandas openpyxl

# Para caché
pip install cachetools
```
