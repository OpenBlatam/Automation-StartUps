# Índice de Módulos - Sistema de Nómina

Índice completo de todos los módulos del sistema de nómina con descripción y uso.

## 📦 Módulos Core

### hour_calculator.py
**Descripción**: Calcula horas trabajadas (regulares, overtime, double time)

**Clases principales**:
- `HourCalculator`: Calculadora principal
- `TimeEntry`: Entrada de tiempo
- `HoursType`: Enum de tipos de horas

**Uso**:
```python
from payroll import HourCalculator, TimeEntry

calc = HourCalculator()
hours = calc.calculate_overtime(time_entries, period_start, period_end)
```

### deduction_calculator.py
**Descripción**: Calcula deducciones (impuestos, beneficios, personalizadas)

**Clases principales**:
- `DeductionCalculator`: Calculadora de deducciones
- `Deduction`: Dataclass de deducción
- `DeductionRule`: Regla de deducción

**Uso**:
```python
from payroll import DeductionCalculator

calc = DeductionCalculator()
deductions = calc.calculate_deductions(employee_id, gross_pay, context)
```

### payment_calculator.py
**Descripción**: Calcula pago completo (bruto y neto)

**Clases principales**:
- `PaymentCalculator`: Calculadora de pagos
- `PayPeriodCalculation`: Resultado del cálculo

**Uso**:
```python
from payroll import PaymentCalculator

calc = PaymentCalculator(hour_calc, deduction_calc)
result = calc.calculate_pay_period(...)
```

### ocr_processor.py
**Descripción**: Procesa recibos con OCR

**Clases principales**:
- `OCRProcessor`: Procesador OCR
- `OCRResult`: Resultado del OCR

**Uso**:
```python
from payroll import OCRProcessor

processor = OCRProcessor(provider="tesseract")
result = processor.process_receipt(image_data)
```

### storage.py
**Descripción**: Persistencia de datos en PostgreSQL

**Clases principales**:
- `PayrollStorage`: Almacenador principal

**Uso**:
```python
from payroll import PayrollStorage

storage = PayrollStorage()
employee = storage.get_employee("EMP001")
```

### config.py
**Descripción**: Configuración básica del sistema

**Clases principales**:
- `PayrollConfig`: Configuración

## 🔔 Módulos de Automatización

### notifications.py
**Descripción**: Sistema de notificaciones multi-canal

**Clases principales**:
- `PayrollNotifier`: Notificador principal

**Canales**: Slack, Email, Webhooks

### approvals.py
**Descripción**: Sistema de aprobaciones multi-nivel

**Clases principales**:
- `PayrollApprovalSystem`: Sistema de aprobaciones
- `ApprovalStatus`: Enum de estados
- `ApprovalLevel`: Enum de niveles

### validators.py
**Descripción**: Validaciones de reglas de negocio

**Clases principales**:
- `PayrollValidator`: Validador principal

### exceptions.py
**Descripción**: Excepciones personalizadas

**Excepciones**:
- `PayrollError`: Base
- `ValidationError`: Validación
- `CalculationError`: Cálculo
- `OCRError`: OCR
- `StorageError`: Storage

## 📊 Módulos de Análisis

### reports.py
**Descripción**: Generación de reportes

**Clases principales**:
- `PayrollReporter`: Generador de reportes
- `PayrollReport`: Reporte

### metrics.py
**Descripción**: Recolección de métricas y KPIs

**Clases principales**:
- `PayrollMetricsCollector`: Recolector de métricas
- `PayrollMetrics`: Métricas

### analytics.py
**Descripción**: Análisis avanzados

**Clases principales**:
- `PayrollAnalytics`: Analizador
- `AnomalyDetection`: Detección de anomalías

### dashboard.py
**Descripción**: Datos para dashboard

**Clases principales**:
- `PayrollDashboard`: Generador de dashboard
- `DashboardData`: Datos del dashboard

### exporters.py
**Descripción**: Exportación de datos

**Clases principales**:
- `PayrollExporter`: Exportador

**Formatos**: CSV, JSON, Excel

### search.py
**Descripción**: Búsqueda avanzada

**Clases principales**:
- `PayrollSearch`: Búsqueda
- `SearchFilters`: Filtros

## 🔐 Módulos de Seguridad

### security.py
**Descripción**: Funciones de seguridad

**Clases principales**:
- `PayrollSecurity`: Seguridad

### audit.py
**Descripción**: Auditoría y trazabilidad

**Clases principales**:
- `PayrollAuditor`: Auditor
- `AuditEventType`: Tipos de eventos

### compliance.py
**Descripción**: Verificación de compliance legal

**Clases principales**:
- `PayrollCompliance`: Compliance
- `ComplianceViolation`: Violación
- `ComplianceRule`: Reglas

### versioning.py
**Descripción**: Versionado de datos

**Clases principales**:
- `PayrollVersioning`: Versionado
- `DataVersion`: Versión

## ⚡ Módulos de Optimización

### cache.py
**Descripción**: Sistema de caché

**Clases principales**:
- `PayrollCache`: Caché
- Decorator `@cached`

### optimizations.py
**Descripción**: Optimizaciones de rendimiento

**Clases principales**:
- `BatchProcessor`: Procesamiento por lotes
- `QueryOptimizer`: Optimizador de queries
- Decorator `@performance_monitor`

### rate_limiting.py
**Descripción**: Rate limiting y throttling

**Clases principales**:
- `PayrollRateLimiter`: Rate limiter
- `RateLimiter`: Limiter genérico
- `Throttler`: Throttler

### circuit_breaker.py
**Descripción**: Circuit breakers para servicios

**Clases principales**:
- `PayrollCircuitBreakers`: Circuit breakers
- `CircuitBreaker`: Breaker genérico
- `CircuitState`: Estados

## 🔗 Módulos de Integración

### integrations.py
**Descripción**: Integraciones externas

**Clases principales**:
- `QuickBooksIntegration`: QuickBooks
- `StripeIntegration`: Stripe
- `AccountingIntegration`: Genérico
- `SlackIntegration`: Slack

### webhooks.py
**Descripción**: Sistema de webhooks

**Clases principales**:
- `PayrollWebhookHandler`: Handler
- `PayrollWebhookReceiver`: Receptor

### sync.py
**Descripción**: Sincronización con sistemas externos

**Clases principales**:
- `PayrollSync`: Sincronización
- `SyncResult`: Resultado

## 🛠️ Módulos de Mantenimiento

### maintenance.py
**Descripción**: Mantenimiento y limpieza

**Clases principales**:
- `PayrollMaintenance`: Mantenimiento

### backup.py
**Descripción**: Sistema de backup

**Clases principales**:
- `PayrollBackup`: Backup

### health_checks.py
**Descripción**: Health checks del sistema

**Clases principales**:
- `PayrollHealthChecker`: Health checker
- `HealthStatus`: Estados

### migrations.py
**Descripción**: Migraciones de esquema

**Clases principales**:
- `PayrollMigrations`: Migraciones
- `Migration`: Migración

### observability.py
**Descripción**: Observabilidad y tracing

**Clases principales**:
- `PayrollObservability`: Observabilidad
- Decorator `@observe_operation`

## 🚀 Módulos Avanzados

### predictions.py
**Descripción**: Predicciones basadas en historial

**Clases principales**:
- `PayrollPredictor`: Predictor
- `PayrollPrediction`: Predicción

### alerts.py
**Descripción**: Sistema de alertas

**Clases principales**:
- `PayrollAlertSystem`: Sistema de alertas
- `Alert`: Alerta
- `AlertType`: Tipos
- `AlertSeverity`: Severidad

### feature_flags.py
**Descripción**: Feature flags

**Clases principales**:
- `PayrollFeatureFlags`: Feature flags
- `FeatureFlag`: Enum de flags

### api.py
**Descripción**: API REST (estructura)

**Clases principales**:
- `PayrollAPI`: API
- `APIResponse`: Respuesta

### events.py
**Descripción**: Sistema de eventos

**Clases principales**:
- `PayrollEventBus`: Event bus
- `PayrollEvent`: Evento
- `EventType`: Tipos

### recovery.py
**Descripción**: Sistema de recovery

**Clases principales**:
- `PayrollRecovery`: Recovery
- `RecoveryPlan`: Plan
- `RecoveryAction`: Acciones

### config_advanced.py
**Descripción**: Configuración avanzada

**Clases principales**:
- `PayrollAdvancedConfig`: Configuración

## 🧰 Módulos de Utilidades

### utils.py
**Descripción**: Funciones utilitarias

**Funciones principales**:
- `get_pay_period_dates`: Fechas de período
- `format_currency`: Formato de moneda
- `format_hours`: Formato de horas
- `validate_date_range`: Validación de fechas
- `retry_on_failure`: Decorator de retry
- `log_calculation_summary`: Logging

### testing.py
**Descripción**: Utilidades de testing

**Clases principales**:
- `PayrollTestData`: Datos de prueba
- `PayrollTestHelpers`: Helpers

### helpers.py
**Descripción**: Helpers adicionales

**Clases principales**:
- `PayrollHelpers`: Helpers adicionales

**Funciones principales**:
- `parse_employee_id`: Parse de ID
- `calculate_pay_period_number`: Número de período
- `format_employee_name`: Formato de nombre

### debugging.py
**Descripción**: Utilidades de debugging y profiling

**Clases principales**:
- `PayrollDebugger`: Debugger
- `PayrollProfiler`: Profiler
- `PayrollDataInspector`: Inspector de datos

**Funciones principales**:
- `debug_timing`: Decorador de timing
- `debug_context`: Context manager
- `enable_debug_mode`: Habilitar debug
- `validate_data_integrity`: Validar integridad

### utilities_advanced.py
**Descripción**: Utilidades avanzadas de cálculo y análisis

**Clases principales**:
- `PayrollAdvancedUtilities`: Utilidades avanzadas

**Funciones principales**:
- `calculate_projected_annual_cost`: Proyección anual
- `calculate_overtime_cost_impact`: Impacto de overtime
- `calculate_break_even_hours`: Break-even
- `calculate_variance`: Varianza
- `calculate_statistics`: Estadísticas
- `calculate_trend`: Tendencias
- `format_payroll_summary`: Resumen formateado

### data_transformers.py
**Descripción**: Transformadores y normalizadores de datos

**Clases principales**:
- `PayrollDataTransformer`: Transformador de datos

**Funciones principales**:
- `normalize_employee_id`: Normalizar ID
- `normalize_currency`: Normalizar moneda
- `normalize_hours`: Normalizar horas
- `normalize_date`: Normalizar fecha
- `transform_time_entry`: Transformar entrada
- `transform_employee`: Transformar empleado
- `normalize_payroll_data`: Función de conveniencia

## 📚 Organización por Categoría

### Por Responsabilidad

**Cálculo**: hour_calculator, deduction_calculator, payment_calculator

**Procesamiento**: ocr_processor, storage

**Validación**: validators, exceptions

**Notificación**: notifications, approvals

**Análisis**: reports, metrics, analytics, dashboard, exporters, search

**Seguridad**: security, audit, compliance, versioning

**Optimización**: cache, optimizations, rate_limiting, circuit_breaker

**Integración**: integrations, webhooks, sync

**Mantenimiento**: maintenance, backup, health_checks, migrations, observability

**Avanzado**: predictions, alerts, feature_flags, api, events, recovery, config_advanced

**Utilidades**: utils, testing, helpers, debugging, utilities_advanced, data_transformers

### Por Prioridad de Uso

**Críticos**: hour_calculator, deduction_calculator, payment_calculator, storage, config

**Importantes**: ocr_processor, notifications, approvals, validators

**Esenciales**: reports, metrics, analytics, security, audit

**Opcionales**: predictions, alerts, feature_flags, events, recovery

## 🔍 Búsqueda Rápida

### Por Funcionalidad

- **Cálculo de horas**: `hour_calculator.py`
- **Cálculo de deducciones**: `deduction_calculator.py`
- **Cálculo de pagos**: `payment_calculator.py`
- **OCR de recibos**: `ocr_processor.py`
- **Almacenamiento**: `storage.py`
- **Notificaciones**: `notifications.py`
- **Aprobaciones**: `approvals.py`
- **Reportes**: `reports.py`
- **Métricas**: `metrics.py`
- **Análisis**: `analytics.py`
- **Dashboard**: `dashboard.py`
- **Exportación**: `exporters.py`
- **Búsqueda**: `search.py`
- **Seguridad**: `security.py`
- **Auditoría**: `audit.py`
- **Compliance**: `compliance.py`
- **Caché**: `cache.py`
- **Optimización**: `optimizations.py`
- **Rate Limiting**: `rate_limiting.py`
- **Circuit Breaker**: `circuit_breaker.py`
- **Integraciones**: `integrations.py`
- **Webhooks**: `webhooks.py`
- **Sincronización**: `sync.py`
- **Mantenimiento**: `maintenance.py`
- **Backup**: `backup.py`
- **Health Checks**: `health_checks.py`
- **Migraciones**: `migrations.py`
- **Observabilidad**: `observability.py`
- **Predicciones**: `predictions.py`
- **Alertas**: `alerts.py`
- **Feature Flags**: `feature_flags.py`
- **API**: `api.py`
- **Eventos**: `events.py`
- **Recovery**: `recovery.py`
- **Configuración**: `config.py`, `config_advanced.py`
- **Utilidades**: `utils.py`, `testing.py`, `helpers.py`, `debugging.py`, `utilities_advanced.py`, `data_transformers.py`

## 📖 Más Información

- [README.md](README.md) - Documentación completa
- [API.md](API.md) - Referencia de API
- [EXAMPLES.md](EXAMPLES.md) - Ejemplos de uso
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del sistema

