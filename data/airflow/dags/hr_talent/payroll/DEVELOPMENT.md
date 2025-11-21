# Guía de Desarrollo - Sistema de Nómina

Guía completa para desarrolladores trabajando en el sistema de nómina.

## 🛠️ Configuración del Entorno

### Prerrequisitos
```bash
# Python 3.9+
python --version

# PostgreSQL 12+
psql --version

# Dependencias
pip install -r requirements.txt
```

### Variables de Entorno
```bash
# Copiar template
cp CONFIG_TEMPLATE.env .env

# Configurar variables
export DATABASE_URL="postgresql://user:pass@localhost/payroll"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export DEBUG_MODE=true
```

## 🐛 Debugging

### Herramientas de Debugging

#### 1. PayrollDebugger
```python
from payroll import PayrollDebugger

debugger = PayrollDebugger()

# Log detallado de cálculo
debugger.log_calculation_details(
    employee_id="EMP001",
    calculation=calculation_result,
    include_breakdown=True
)

# Log de entradas de tiempo
debugger.log_time_entry_details(
    employee_id="EMP001",
    time_entries=entries,
    period_start=date(2025, 1, 1),
    period_end=date(2025, 1, 14)
)

# Comparar cálculos
differences = debugger.compare_calculations(calc1, calc2)
```

#### 2. Debug Timing
```python
from payroll import debug_timing

@debug_timing
def my_function():
    # Tu código aquí
    pass
```

#### 3. Debug Context
```python
from payroll import debug_context

with debug_context("process_payroll"):
    # Tu código aquí
    pass
```

#### 4. Profiler
```python
from payroll import PayrollProfiler

profiler = PayrollProfiler()

# Registrar operaciones
profiler.record_operation("calculation", 1.234)
profiler.record_operation("database_query", 0.567)

# Ver estadísticas
stats = profiler.get_statistics()
profiler.print_statistics()
```

#### 5. Data Inspector
```python
from payroll import PayrollDataInspector

inspector = PayrollDataInspector()

# Inspeccionar datos
employee_info = inspector.inspect_employee(employee_dict)
entry_info = inspector.inspect_time_entry(time_entry)
calc_info = inspector.inspect_calculation(calculation)
```

### Validación de Integridad
```python
from payroll import validate_data_integrity

# Validar datos completos
result = validate_data_integrity(
    employee_id="EMP001",
    calculation=calc,
    time_entries=entries,
    expenses=expenses
)

if not result["valid"]:
    print(f"Issues found: {result['issues']}")
```

### Habilitar Modo Debug
```python
from payroll import enable_debug_mode

# Habilitar
enable_debug_mode(True)

# Deshabilitar
enable_debug_mode(False)
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest data/airflow/dags/payroll/tests/

# Test específico
pytest data/airflow/dags/payroll/tests/test_hour_calculator.py

# Con cobertura
pytest --cov=payroll --cov-report=html
```

### Crear Datos de Prueba
```python
from payroll import PayrollTestData

test_data = PayrollTestData()

# Generar empleado
employee = test_data.generate_employee(
    employee_id="TEST001",
    hourly_rate=Decimal("25.00")
)

# Generar entradas de tiempo
entries = test_data.generate_time_entries(
    employee_id="TEST001",
    start_date=date(2025, 1, 1),
    days=14
)
```

## 📝 Logging

### Configurar Logging
```python
import logging

# Configurar nivel
logging.getLogger("payroll").setLevel(logging.DEBUG)

# Formato personalizado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Logs Útiles
```python
from payroll import PayrollDebugger

# Log de query
PayrollDebugger.log_database_query(
    query="SELECT * FROM employees",
    parameters=("EMP001",),
    execution_time=0.123
)

# Log de función
from payroll import log_function_call

log_function_call(
    func_name="calculate_payroll",
    kwargs={"employee_id": "EMP001"},
    result=calculation,
    execution_time=1.234
)
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```python
# Verificar conexión
from payroll import PayrollStorage

storage = PayrollStorage()
storage.ensure_schema()  # Verifica schema
```

#### 2. Error en Cálculos
```python
# Validar cálculo
from payroll import PaymentCalculator

calc = PaymentCalculator(...)
result = calc.calculate_pay_period(...)
is_valid, error = calc.validate_calculation(result)

if not is_valid:
    print(f"Validation error: {error}")
```

#### 3. Error en OCR
```python
# Probar OCR
from payroll import OCRProcessor

processor = OCRProcessor(provider="tesseract")
result = processor.process_receipt(image_data)

if result.confidence < 0.8:
    print(f"Low confidence: {result.confidence}")
```

## 📊 Performance

### Benchmarking
```python
from payroll import PayrollBenchmark

benchmark = PayrollBenchmark()

# Benchmark de operación
result = benchmark.benchmark_operation(
    operation_name="calculate_payroll",
    operation_func=lambda: calc.calculate_pay_period(...),
    iterations=10
)

print(f"Average time: {result.average_time:.3f}s")
```

### Optimización
```python
# Usar batch processing
from payroll import BatchProcessor

processor = BatchProcessor(batch_size=10, max_workers=4)
results = processor.process_batch(
    items=employees,
    process_func=process_employee
)
```

## 🏗️ Arquitectura

### Estructura de Módulos
```
payroll/
├── Core Modules (6)
│   ├── hour_calculator.py
│   ├── deduction_calculator.py
│   ├── payment_calculator.py
│   ├── ocr_processor.py
│   ├── storage.py
│   └── config.py
├── Automation (4)
├── Analysis (6)
├── Security (4)
└── ...
```

### Flujo de Datos
```
Time Entries → Hour Calculator → Payment Calculator
Expenses → OCR Processor → Storage
Deductions → Deduction Calculator → Payment Calculator
```

## 🔄 Desarrollo Iterativo

### Workflow Recomendado
1. **Escribir tests primero** (TDD)
2. **Implementar funcionalidad**
3. **Ejecutar tests**
4. **Debug si es necesario**
5. **Refactorizar**
6. **Documentar**

### Code Review Checklist
- [ ] Tests pasan
- [ ] Código sigue estándares (ver CODE_STANDARDS.md)
- [ ] Manejo de errores apropiado
- [ ] Logging adecuado
- [ ] Documentación actualizada
- [ ] Performance aceptable

## 📚 Referencias

- [Code Standards](CODE_STANDARDS.md)
- [Best Practices](BEST_PRACTICES.md)
- [Testing Guide](TESTING.md)
- [Architecture](ARCHITECTURE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## 🚀 Quick Start

```python
# 1. Importar módulos
from payroll import (
    PayrollStorage,
    PaymentCalculator,
    HourCalculator,
    PayrollDebugger
)

# 2. Configurar
storage = PayrollStorage()
hour_calc = HourCalculator()
payment_calc = PaymentCalculator(hour_calc, ...)

# 3. Habilitar debug
enable_debug_mode(True)

# 4. Procesar
calculation = payment_calc.calculate_pay_period(...)

# 5. Debug
debugger = PayrollDebugger()
debugger.log_calculation_details("EMP001", calculation)
```

## 💡 Tips

1. **Usa type hints** - Mejora la legibilidad y detección de errores
2. **Logs descriptivos** - Incluye contexto en los logs
3. **Tests unitarios** - Prueba funciones individuales
4. **Tests de integración** - Prueba flujos completos
5. **Profiling** - Identifica cuellos de botella
6. **Validación temprana** - Valida datos lo antes posible
7. **Manejo de errores** - Usa excepciones específicas
8. **Documentación** - Mantén docs actualizados



