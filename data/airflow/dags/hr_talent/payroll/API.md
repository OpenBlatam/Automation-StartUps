# API Documentation - Payroll System

Documentación completa de la API del sistema de nómina.

## Índice

1. [HourCalculator](#hourcalculator)
2. [PaymentCalculator](#paymentcalculator)
3. [PayrollStorage](#payrollstorage)
4. [PayrollNotifier](#payrollnotifier)
5. [PayrollReporter](#payrollreporter)
6. [PayrollValidator](#payrollvalidator)
7. [PayrollApprovalSystem](#payrollapprovalsystem)
8. [PayrollMetricsCollector](#payrollmetricscollector)
9. [PayrollHealthChecker](#payrollhealthchecker)

---

## HourCalculator

Calculadora de horas trabajadas.

### Métodos

#### `calculate_hours_from_timestamps(clock_in, clock_out)`

Calcula horas trabajadas desde timestamps.

**Parámetros:**
- `clock_in` (datetime): Hora de entrada
- `clock_out` (datetime): Hora de salida

**Retorna:** Decimal - Horas trabajadas

**Ejemplo:**
```python
from payroll import HourCalculator
from datetime import datetime

calc = HourCalculator()
hours = calc.calculate_hours_from_timestamps(
    datetime(2025, 1, 1, 9, 0),
    datetime(2025, 1, 1, 17, 30)
)
# Returns: Decimal("8.50")
```

#### `calculate_overtime(time_entries, period_start, period_end)`

Calcula horas regulares y overtime.

**Parámetros:**
- `time_entries` (List[TimeEntry]): Lista de entradas de tiempo
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período

**Retorna:** Dict con 'regular_hours', 'overtime_hours', 'double_time_hours'

---

## PaymentCalculator

Calculadora de pagos completos.

### Métodos

#### `calculate_pay_period(employee_id, hourly_rate, employee_type, period_start, period_end, pay_date, time_entries, expenses_total, employee_context)`

Calcula el pago completo para un período.

**Parámetros:**
- `employee_id` (str): ID del empleado
- `hourly_rate` (Decimal): Tarifa por hora
- `employee_type` (str): Tipo de empleado
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período
- `pay_date` (date): Fecha de pago
- `time_entries` (List[TimeEntry]): Entradas de tiempo
- `expenses_total` (Decimal): Total de gastos
- `employee_context` (Dict, optional): Contexto adicional

**Retorna:** PayPeriodCalculation

---

## PayrollStorage

Almacenamiento en PostgreSQL.

### Métodos

#### `get_employee(employee_id)`

Obtiene un empleado por ID.

**Parámetros:**
- `employee_id` (str): ID del empleado

**Retorna:** Dict con datos del empleado o None

#### `save_time_entry(entry)`

Guarda una entrada de tiempo.

**Parámetros:**
- `entry` (TimeEntry): Entrada de tiempo

**Retorna:** int - ID del registro

#### `save_pay_period(calculation)`

Guarda un período de pago.

**Parámetros:**
- `calculation` (PayPeriodCalculation): Cálculo de período

**Retorna:** int - ID del período

---

## PayrollNotifier

Sistema de notificaciones.

### Métodos

#### `notify_payroll_completed(employee_id, employee_name, period_start, period_end, net_pay, details)`

Notifica que la nómina se completó.

**Parámetros:**
- `employee_id` (str): ID del empleado
- `employee_name` (str): Nombre del empleado
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período
- `net_pay` (Decimal): Pago neto
- `details` (Dict, optional): Detalles adicionales

**Retorna:** bool - True si fue exitoso

---

## PayrollReporter

Generador de reportes.

### Métodos

#### `generate_period_report(period_start, period_end)`

Genera reporte para un período.

**Parámetros:**
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período

**Retorna:** PayrollReport

#### `generate_employee_report(employee_id, start_date, end_date)`

Genera reporte por empleado.

**Parámetros:**
- `employee_id` (str): ID del empleado
- `start_date` (date): Fecha inicio
- `end_date` (date): Fecha fin

**Retorna:** Dict con reporte

---

## PayrollValidator

Validaciones de negocio.

### Métodos

#### `validate_time_entries(entries, period_start, period_end)`

Valida múltiples entradas de tiempo.

**Parámetros:**
- `entries` (List[TimeEntry]): Entradas de tiempo
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período

**Retorna:** Tuple[bool, Optional[str], List[str]] - (is_valid, error, warnings)

---

## PayrollApprovalSystem

Sistema de aprobaciones.

### Métodos

#### `request_approval(entity_type, entity_id, employee_id, approval_level, requested_by, metadata)`

Solicita una aprobación.

**Parámetros:**
- `entity_type` (str): Tipo de entidad
- `entity_id` (int): ID de entidad
- `employee_id` (str): ID del empleado
- `approval_level` (ApprovalLevel): Nivel de aprobación
- `requested_by` (str): Usuario que solicita
- `metadata` (Dict, optional): Metadata adicional

**Retorna:** int - ID de aprobación

#### `approve(approval_id, approved_by, metadata)`

Aprueba una solicitud.

**Parámetros:**
- `approval_id` (int): ID de aprobación
- `approved_by` (str): Usuario que aprueba
- `metadata` (Dict, optional): Metadata adicional

**Retorna:** bool - True si fue exitoso

---

## PayrollMetricsCollector

Recolector de métricas.

### Métodos

#### `collect_period_metrics(period_start, period_end)`

Recolecta métricas para un período.

**Parámetros:**
- `period_start` (date): Inicio del período
- `period_end` (date): Fin del período

**Retorna:** PayrollMetrics

#### `get_trend_analysis(periods, period_type)`

Analiza tendencias.

**Parámetros:**
- `periods` (int): Número de períodos
- `period_type` (str): Tipo de período

**Retorna:** Dict con análisis de tendencias

---

## PayrollHealthChecker

Verificador de salud del sistema.

### Métodos

#### `comprehensive_health_check()`

Realiza verificación completa.

**Retorna:** Dict con estado de salud

**Ejemplo:**
```python
from payroll import PayrollHealthChecker

checker = PayrollHealthChecker()
health = checker.comprehensive_health_check()

print(health['overall_status'])  # 'healthy', 'warning', or 'critical'
```

---

## Códigos de Error

### Excepciones

- `PayrollError`: Excepción base
- `ValidationError`: Error de validación
- `CalculationError`: Error en cálculo
- `StorageError`: Error en almacenamiento
- `OCRError`: Error en OCR
- `ConfigurationError`: Error de configuración

---

## Ejemplos Completos

Ver [README.md](README.md) para ejemplos completos de uso.

