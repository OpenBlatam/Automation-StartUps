# Guía de Troubleshooting - Sistema de Nómina

Guía completa para resolver problemas comunes del sistema de nómina.

## 🔍 Problemas Comunes

### 1. Schema no encontrado

**Síntoma**: Error "table does not exist" o "schema not found"

**Solución**:
```bash
# Verificar que el schema existe
psql $DATABASE_URL -c "\dt payroll_*"

# Si no existe, crear el schema
psql $DATABASE_URL -f data/db/payroll_schema.sql

# O usar el script
python -m payroll.scripts.setup_schema --conn-id postgres_default
```

### 2. Conexión a base de datos falla

**Síntoma**: Error de conexión a PostgreSQL

**Solución**:
```bash
# Verificar conexión
python -m payroll.scripts.health_check --conn-id postgres_default

# Verificar variables de entorno
echo $DATABASE_URL

# Verificar configuración de Airflow
# En Airflow UI: Admin > Connections > postgres_default
```

### 3. OCR falla constantemente

**Síntoma**: OCR siempre retorna error o falla

**Solución**:
```python
# Verificar Tesseract instalado
import pytesseract
print(pytesseract.get_tesseract_version())

# Verificar variables de entorno
echo $TESSERACT_CMD
echo $TESSERACT_LANG

# Probar con diferentes proveedores
from payroll import OCRProcessor

# Tesseract
processor = OCRProcessor(provider="tesseract")
result = processor.process_receipt(image_data)

# AWS Textract (si está configurado)
processor = OCRProcessor(provider="aws_textract")
result = processor.process_receipt(image_data)
```

### 4. Cálculos incorrectos

**Síntoma**: Los montos calculados no coinciden con lo esperado

**Solución**:
```python
from payroll import PayrollValidator

# Validar cálculo
validator = PayrollValidator()
is_valid, error = validator.validate_gross_pay(
    gross_pay, total_hours, hourly_rate
)

# Verificar reglas de deducción
from payroll import PayrollStorage
storage = PayrollStorage()

# Obtener reglas activas
sql = "SELECT * FROM payroll_deduction_rules WHERE active = true"
rules = storage.hook.get_records(sql)
```

### 5. Errores de rate limiting

**Síntoma**: "Rate limit exceeded" o operaciones rechazadas

**Solución**:
```python
from payroll import PayrollRateLimiter

rate_limiter = PayrollRateLimiter()

# Verificar límites
remaining = rate_limiter.payroll_calculations.get_remaining("payroll")
print(f"Remaining: {remaining}")

# Ajustar límites si es necesario
# En config_advanced.py o variables de entorno
```

### 6. Circuit breaker abierto

**Síntoma**: Servicios externos no responden, circuit breaker en estado OPEN

**Solución**:
```python
from payroll import PayrollCircuitBreakers

circuit_breakers = PayrollCircuitBreakers()

# Verificar estados
states = circuit_breakers.get_all_states()
for name, state in states.items():
    print(f"{name}: {state['state']}")

# Si está abierto, esperar timeout o verificar servicio
# El circuit breaker se reseteará automáticamente después del timeout
```

### 7. Aprobaciones pendientes antiguas

**Síntoma**: Muchas aprobaciones pendientes sin procesar

**Solución**:
```python
from payroll import PayrollApprovalSystem

approval_system = PayrollApprovalSystem()

# Obtener pendientes antiguas
pending = approval_system.get_pending_approvals(
    approval_level=ApprovalLevel.MANAGER,
    max_age_days=7
)

# Limpiar con el DAG de mantenimiento
# O manualmente:
from payroll import PayrollMaintenance

maintenance = PayrollMaintenance()
result = maintenance.cleanup_stale_approvals(days=90)
```

### 8. Performance degradado

**Síntoma**: Operaciones lentas, timeouts

**Solución**:
```python
from payroll import PayrollBenchmark

# Benchmark operaciones
benchmark = PayrollBenchmark()
result = benchmark.benchmark_storage_operations(storage, iterations=10)

# Verificar métricas
from payroll import PayrollMonitor

monitor = PayrollMonitor()
performance = monitor.get_performance_metrics(hours=24)
print(f"Throughput: {performance['throughput_per_hour']} ops/hour")

# Optimizar tablas
from payroll import PayrollMaintenance

maintenance = PayrollMaintenance()
maintenance.optimize_tables()
```

### 9. Errores de validación

**Síntoma**: Validaciones fallan constantemente

**Solución**:
```python
from payroll import PayrollValidator

validator = PayrollValidator()

# Validar entradas de tiempo
is_valid, error, warnings = validator.validate_time_entries(
    time_entries, period_start, period_end
)

if not is_valid:
    print(f"Validation error: {error}")
    
if warnings:
    for warning in warnings:
        print(f"Warning: {warning}")

# Verificar reglas de negocio
# Revisar configuración en PayrollValidator
```

### 10. Problemas de sincronización

**Síntoma**: Datos no sincronizados con sistemas externos

**Solución**:
```python
from payroll import PayrollSync

sync = PayrollSync()

# Obtener no sincronizados
unsynced = sync.get_unsynced_records(
    entity_type="pay_period",
    period_start=period_start,
    period_end=period_end
)

# Sincronizar manualmente
for record in unsynced:
    # Tu lógica de sincronización
    sync_handler(record)
    sync.mark_synced("pay_period", record["id"])
```

## 🔧 Comandos de Diagnóstico

### Health Check Completo
```bash
python -m payroll.scripts.health_check --conn-id postgres_default --json
```

### Verificar Operaciones Fallidas
```bash
python -m payroll.scripts.recovery_helper failed --hours 24
```

### Resumen de Recuperación
```bash
python -m payroll.scripts.recovery_helper summary
```

### Verificar Métricas del Sistema
```python
from payroll import PayrollMonitor

monitor = PayrollMonitor()
metrics = monitor.get_system_metrics()
health = monitor.check_system_health()
print(health)
```

## 📊 Logs y Debugging

### Habilitar Logging Detallado
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("payroll")
logger.setLevel(logging.DEBUG)
```

### Verificar Logs de Airflow
```bash
# En Airflow UI: ver logs de tareas
# O en terminal:
airflow tasks logs payroll_processing calculate_payroll 2025-01-01
```

### Tracing de Operaciones
```python
from payroll import observability

with observability.trace("my_operation", employee_id="EMP001"):
    # Tu código
    result = process_payroll()
```

## 🐛 Debugging Avanzado

### Verificar Estado de Circuit Breakers
```python
from payroll import PayrollCircuitBreakers

circuit_breakers = PayrollCircuitBreakers()
states = circuit_breakers.get_all_states()

for name, state in states.items():
    print(f"{name}:")
    print(f"  State: {state['state']}")
    print(f"  Failures: {state['failure_count']}")
    print(f"  Last failure: {state['last_failure_time']}")
```

### Verificar Caché
```python
from payroll import PayrollCache

cache = PayrollCache(enabled=True)
# Verificar hit rate y estadísticas
```

### Verificar Rate Limits
```python
from payroll import PayrollRateLimiter

rate_limiter = PayrollRateLimiter()

# Verificar límites actuales
remaining_calc = rate_limiter.payroll_calculations.get_remaining("payroll")
remaining_ocr = rate_limiter.ocr_requests.get_remaining("ocr")
```

## 🔍 Análisis de Problemas

### Analizar Anomalías
```python
from payroll import PayrollAnalytics

analytics = PayrollAnalytics()
anomalies = analytics.detect_anomalies(period_start, period_end)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.employee_id}")
    print(f"  Type: {anomaly.anomaly_type}")
    print(f"  Severity: {anomaly.severity}")
    print(f"  Description: {anomaly.description}")
```

### Verificar Compliance
```python
from payroll import PayrollCompliance

compliance = PayrollCompliance()
report = compliance.get_compliance_report(period_start, period_end)

if report["total_violations"] > 0:
    print(f"Violations found: {report['total_violations']}")
    for violation in report["violations"]:
        print(f"  {violation['message']}")
```

## 📞 Obtener Ayuda

### Recursos
- [README.md](README.md) - Documentación completa
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Referencia rápida
- [EXAMPLES.md](EXAMPLES.md) - Ejemplos de uso
- [API.md](API.md) - Referencia de API

### Verificar Configuración
```python
from payroll import PayrollAdvancedConfig

config = PayrollAdvancedConfig.from_env()
is_valid, error = config.validate()

if not is_valid:
    print(f"Config error: {error}")
```

### Verificar Feature Flags
```python
from payroll import feature_flags, FeatureFlag

# Verificar estado de feature flags
for flag in FeatureFlag:
    enabled = feature_flags.is_enabled(flag)
    print(f"{flag.value}: {enabled}")
```

## 🎯 Mejores Prácticas

1. **Siempre ejecutar health checks** antes de procesar
2. **Monitorear métricas** regularmente
3. **Revisar logs** para detectar problemas temprano
4. **Usar recovery helper** para operaciones fallidas
5. **Verificar configuración** periódicamente
6. **Mantener backups** actualizados
7. **Ejecutar mantenimiento** regularmente

## ⚠️ Problemas Críticos

### Base de Datos No Accesible
1. Verificar conexión
2. Verificar credenciales
3. Verificar red/firewall
4. Contactar DBA

### Pérdida de Datos
1. Verificar backups
2. Usar sistema de recovery
3. Verificar versionado de datos
4. Contactar soporte

### Sistema Completamente Caído
1. Verificar health checks
2. Verificar circuit breakers
3. Verificar logs de Airflow
4. Escalar al equipo de infraestructura

