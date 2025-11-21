# Guía de Testing - Sistema de Nómina

Guía completa para testing del sistema de nómina.

## 🧪 Estrategia de Testing

### Pirámide de Testing
```
        /\
       /  \
      / E2E \          Pocos tests end-to-end
     /______\
    /        \
   /Integration\      Algunos tests de integración
  /____________\
 /              \
/  Unit Tests    \    Muchos tests unitarios
/________________\
```

## 📋 Tipos de Tests

### 1. Tests Unitarios

**Objetivo**: Probar componentes individuales aislados

**Ubicación**: `payroll/tests/test_*.py`

**Ejemplo**:
```python
from payroll import HourCalculator
from payroll.testing import PayrollTestData

def test_calculate_overtime():
    calc = HourCalculator()
    entries = PayrollTestData.create_test_time_entries(...)
    result = calc.calculate_overtime(entries, start, end)
    assert result["total_hours"] > 0
```

### 2. Tests de Integración

**Objetivo**: Probar interacción entre componentes

**Ubicación**: `payroll/tests/test_integration.py`

**Ejemplo**:
```python
def test_complete_payroll_flow():
    storage = PayrollStorage()
    calculator = PaymentCalculator(...)
    
    # Flujo completo
    employee = storage.get_employee("EMP001")
    calculation = calculator.calculate_pay_period(...)
    storage.save_pay_period(calculation)
```

### 3. Tests de Performance

**Objetivo**: Verificar que el sistema cumple con requisitos de performance

**Ejemplo**:
```python
from payroll import PayrollBenchmark

benchmark = PayrollBenchmark()
result = benchmark.benchmark_function(
    "calculate_payroll",
    calculate_payroll,
    iterations=100
)

assert result.average_time < 1.0  # Debe ser < 1 segundo
```

## 🔧 Herramientas de Testing

### Datos de Prueba

```python
from payroll.testing import PayrollTestData

# Crear empleado de prueba
employee = PayrollTestData.create_test_employee(
    "TEST001",
    "Test Employee",
    Decimal("25.00")
)

# Crear entradas de tiempo
entries = PayrollTestData.create_test_time_entries(
    "TEST001",
    date(2025, 1, 1),
    date(2025, 1, 14)
)

# Crear cálculo de prueba
calculation = PayrollTestData.create_test_calculation(
    "TEST001",
    date(2025, 1, 1),
    date(2025, 1, 14)
)
```

### Helpers de Testing

```python
from payroll.testing import PayrollTestHelpers

# Validar cálculo
PayrollTestHelpers.assert_calculation_valid(calculation)

# Crear dataset completo
dataset = PayrollTestData.create_test_dataset(
    num_employees=10,
    num_periods=4
)
```

## 📝 Escribir Tests

### Estructura de Test

```python
import unittest
from payroll import PaymentCalculator

class TestPaymentCalculator(unittest.TestCase):
    def setUp(self):
        """Setup para cada test"""
        self.calculator = PaymentCalculator(...)
    
    def test_something(self):
        """Test específico"""
        # Arrange
        data = create_test_data()
        
        # Act
        result = self.calculator.calculate(...)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertGreater(result.net_pay, Decimal("0.00"))
    
    def tearDown(self):
        """Cleanup después de cada test"""
        pass
```

### Patrones de Testing

#### 1. Test de Casos Felices
```python
def test_calculate_pay_period_success(self):
    """Test cálculo exitoso"""
    calculation = self.calculator.calculate_pay_period(...)
    self.assertIsNotNone(calculation)
    self.assertGreater(calculation.net_pay, Decimal("0.00"))
```

#### 2. Test de Validación
```python
def test_validation_failure(self):
    """Test que validación falla con datos inválidos"""
    with self.assertRaises(ValidationError):
        self.calculator.calculate_pay_period(
            employee_id="",  # Inválido
            ...
        )
```

#### 3. Test de Edge Cases
```python
def test_zero_hours(self):
    """Test con cero horas trabajadas"""
    time_entries = []  # Sin entradas
    calculation = self.calculator.calculate_pay_period(
        time_entries=time_entries,
        ...
    )
    self.assertEqual(calculation.total_hours, Decimal("0.00"))
```

#### 4. Test de Performance
```python
def test_calculation_performance(self):
    """Test que cálculo es rápido"""
    import time
    
    start = time.time()
    calculation = self.calculator.calculate_pay_period(...)
    elapsed = time.time() - start
    
    self.assertLess(elapsed, 1.0)  # < 1 segundo
```

## 🎯 Cobertura de Tests

### Áreas a Cubrir

1. **Calculadores**
   - ✅ HourCalculator
   - ✅ DeductionCalculator
   - ✅ PaymentCalculator

2. **Procesadores**
   - ✅ OCRProcessor
   - ✅ PayrollStorage

3. **Validadores**
   - ✅ PayrollValidator
   - ✅ AdvancedPayrollValidator

4. **Servicios**
   - ✅ PayrollAnalytics
   - ✅ PayrollAlertSystem
   - ✅ PayrollCompliance

### Métricas de Cobertura

```bash
# Ejecutar con coverage
pytest --cov=payroll --cov-report=html

# Ver reporte
open htmlcov/index.html
```

## 🚀 Ejecutar Tests

### Todos los Tests
```bash
pytest payroll/tests/
```

### Tests Específicos
```bash
pytest payroll/tests/test_hour_calculator.py
pytest payroll/tests/test_integration.py::TestPayrollIntegration
```

### Con Verbose
```bash
pytest payroll/tests/ -v
```

### Con Coverage
```bash
pytest --cov=payroll --cov-report=term-missing
```

## 🔍 Debugging Tests

### Ver Output Detallado
```bash
pytest -v -s payroll/tests/
```

### Ejecutar Test Específico
```bash
pytest payroll/tests/test_payment_calculator.py::TestPaymentCalculator::test_calculate_pay_period_hourly
```

### Con PDB
```bash
pytest --pdb payroll/tests/
```

## 📊 Tests de Integración con Base de Datos

### Setup de Base de Datos de Test

```python
import pytest
from payroll import PayrollStorage

@pytest.fixture
def test_storage():
    """Fixture para storage de test"""
    storage = PayrollStorage(postgres_conn_id="test_postgres")
    # Setup: crear datos de prueba
    yield storage
    # Teardown: limpiar datos de prueba
```

### Test con Base de Datos

```python
def test_save_and_retrieve(test_storage):
    """Test guardar y recuperar"""
    # Guardar
    calculation = create_test_calculation()
    pay_period_id = test_storage.save_pay_period(calculation)
    
    # Recuperar
    # (implementar método de recuperación si no existe)
    assert pay_period_id is not None
```

## 🎭 Mocking

### Mock de Servicios Externos

```python
from unittest.mock import Mock, patch

@patch('payroll.integrations.QuickBooksIntegration.sync_payroll_period')
def test_integration_with_mock(mock_sync):
    """Test integración con mock"""
    mock_sync.return_value = {"success": True}
    
    # Tu código que usa la integración
    result = sync_to_quickbooks(...)
    
    mock_sync.assert_called_once()
```

## 📈 Métricas de Testing

### Tracking de Cobertura
- **Objetivo**: > 80% cobertura
- **Monitorear**: Cobertura por módulo
- **Alertar**: Si cobertura baja

### Performance Tests
```python
from payroll import PayrollBenchmark

benchmark = PayrollBenchmark()

# Benchmark función
result = benchmark.benchmark_function(
    "calculate_payroll",
    calculate_payroll,
    iterations=100
)

# Verificar que cumple requisitos
assert result.average_time < 1.0
assert result.success_rate > 0.95
```

## 🔄 CI/CD Integration

### Ejecutar en CI

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pytest payroll/tests/ --cov=payroll --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v2
```

## 📚 Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Testing Best Practices](BEST_PRACTICES.md)

