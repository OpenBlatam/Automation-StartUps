# Estándares de Código - Sistema de Nómina

Guía de estándares de código para mantener consistencia en el sistema de nómina.

## 📋 Convenciones Generales

### Nombres
```python
# ✅ Clases: PascalCase
class PayrollCalculator:
    pass

# ✅ Funciones: snake_case
def calculate_pay_period():
    pass

# ✅ Variables: snake_case
employee_id = "EMP001"
hourly_rate = Decimal("25.00")

# ✅ Constantes: UPPER_SNAKE_CASE
MAX_HOURS_PER_WEEK = 80
DEFAULT_TAX_RATE = Decimal("0.25")
```

### Type Hints
```python
# ✅ BUENO: Type hints completos
def calculate_pay_period(
    employee_id: str,
    hourly_rate: Decimal,
    period_start: date,
    period_end: date
) -> PayPeriodCalculation:
    pass

# ❌ MALO: Sin type hints
def calculate_pay_period(employee_id, hourly_rate, period_start, period_end):
    pass
```

### Docstrings
```python
# ✅ BUENO: Docstring completo
def calculate_pay_period(
    employee_id: str,
    hourly_rate: Decimal
) -> PayPeriodCalculation:
    """
    Calcula el pago completo para un período de pago.
    
    Args:
        employee_id: ID único del empleado
        hourly_rate: Tarifa por hora del empleado
    
    Returns:
        PayPeriodCalculation con todos los detalles del cálculo
    
    Raises:
        ValidationError: Si los datos son inválidos
        CalculationError: Si el cálculo falla
    
    Example:
        >>> calc = PaymentCalculator(...)
        >>> result = calc.calculate_pay_period("EMP001", Decimal("25.00"), ...)
        >>> print(result.net_pay)
        5000.00
    """
    pass
```

## 🏗️ Estructura de Clases

### Clases Principales
```python
# ✅ BUENO: Estructura clara
class PaymentCalculator:
    """Descripción de la clase"""
    
    def __init__(self, hour_calc: HourCalculator, deduction_calc: DeductionCalculator):
        """Inicialización con dependencias claras"""
        self.hour_calc = hour_calc
        self.deduction_calc = deduction_calc
    
    def calculate_pay_period(self, ...) -> PayPeriodCalculation:
        """Método principal"""
        pass
    
    def validate_calculation(self, calculation: PayPeriodCalculation) -> tuple[bool, Optional[str]]:
        """Método de validación"""
        pass
```

### Dataclasses
```python
# ✅ BUENO: Usar dataclasses para datos
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class PayPeriodCalculation:
    """Resultado del cálculo de período"""
    employee_id: str
    period_start: date
    period_end: date
    net_pay: Decimal
    gross_pay: Decimal
    # ...
```

## 🔄 Manejo de Errores

### Excepciones Personalizadas
```python
# ✅ BUENO: Excepciones específicas
from payroll.exceptions import ValidationError, CalculationError

def validate_data(data):
    if not data:
        raise ValidationError("Data is required", context={"data": data})
    
    if data["amount"] < 0:
        raise ValidationError("Amount cannot be negative", context={"amount": data["amount"]})

# ❌ MALO: Excepciones genéricas
def validate_data(data):
    if not data:
        raise Exception("Error")  # No específico
```

### Retry Logic
```python
# ✅ BUENO: Usar decorator de retry
from payroll.utils import retry_on_failure

@retry_on_failure(max_attempts=3, delay=1.0)
def save_to_database(data):
    # Operación que puede fallar
    pass

# ❌ MALO: Sin retry
def save_to_database(data):
    # Puede fallar sin reintentar
    pass
```

## 📊 Logging

### Niveles Apropiados
```python
# ✅ BUENO: Niveles apropiados
logger.debug("Detailed debugging info")
logger.info("Normal operation info")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical error")

# ❌ MALO: Todo en error
logger.error("Normal operation")  # Debería ser info
logger.error("Debug info")  # Debería ser debug
```

### Logging Estructurado
```python
# ✅ BUENO: Logging con contexto
logger.info(
    "Payroll calculated",
    extra={
        "employee_id": employee_id,
        "net_pay": float(net_pay),
        "period": f"{period_start} to {period_end}"
    }
)

# ❌ MALO: Logging sin contexto
logger.info("Payroll calculated")
```

## ✅ Validación

### Validación Temprana
```python
# ✅ BUENO: Validar al inicio
def calculate_pay_period(self, employee_id: str, ...):
    # Validar inputs primero
    if not employee_id:
        raise ValidationError("employee_id is required")
    
    if hourly_rate < 0:
        raise ValidationError("hourly_rate cannot be negative")
    
    # Procesar después
    # ...

# ❌ MALO: Validar al final
def calculate_pay_period(self, employee_id: str, ...):
    # Procesar primero
    result = complex_calculation(...)
    
    # Validar después (demasiado tarde)
    if not employee_id:
        raise ValidationError("employee_id is required")
```

## 🔒 Seguridad

### Sanitización
```python
# ✅ BUENO: Sanitizar inputs
from payroll import PayrollSecurity

security = PayrollSecurity()
sanitized = security.sanitize_input(user_input)

# ❌ MALO: Usar input directo
query = f"SELECT * FROM employees WHERE name = '{user_input}'"  # SQL injection risk
```

### Datos Sensibles
```python
# ✅ BUENO: Enmascarar datos sensibles
from payroll import PayrollSecurity

security = PayrollSecurity()
masked = security.mask_sensitive_data(ssn)  # "***-**-1234"

# ❌ MALO: Logear datos sensibles
logger.info(f"SSN: {ssn}")  # Riesgo de seguridad
```

## ⚡ Performance

### Queries Optimizadas
```python
# ✅ BUENO: Query específica
sql = """
    SELECT employee_id, net_pay
    FROM payroll_pay_periods
    WHERE period_start = %s AND period_end = %s
    LIMIT 100
"""

# ❌ MALO: SELECT * sin límites
sql = "SELECT * FROM payroll_pay_periods"
```

### Caché Apropiado
```python
# ✅ BUENO: Caché para datos estáticos
@cached(key_prefix="employee", ttl_seconds=3600)
def get_employee(employee_id):
    return storage.get_employee(employee_id)

# ❌ MALO: Caché para datos dinámicos
@cached(key_prefix="current_period", ttl_seconds=3600)
def get_current_period():
    return get_pay_period_dates()  # Cambia frecuentemente
```

## 📝 Comentarios

### Cuándo Comentar
```python
# ✅ BUENO: Comentar lógica compleja
# Calcular overtime: horas > 40 por semana = overtime
# Overtime = (total_hours - 40) * 1.5
if total_hours > 40:
    overtime = (total_hours - 40) * Decimal("1.5")

# ❌ MALO: Comentar código obvio
# Incrementar contador
counter += 1
```

### TODO Comments
```python
# ✅ BUENO: TODOs específicos y accionables
# TODO: Implementar cálculo de double time para horas > 12/día
# TODO: Agregar soporte para múltiples jurisdicciones fiscales

# ❌ MALO: TODOs vagos
# TODO: Mejorar esto
# TODO: Fix later
```

## 🧪 Testing

### Tests Claros
```python
# ✅ BUENO: Tests con nombres descriptivos
def test_calculate_pay_period_with_overtime():
    """Test que calcula pago con horas overtime"""
    # Arrange
    time_entries = create_overtime_entries()
    
    # Act
    result = calculator.calculate_pay_period(...)
    
    # Assert
    assert result.overtime_hours > 0
    assert result.net_pay > result.gross_pay * Decimal("0.5")

# ❌ MALO: Tests sin contexto
def test_calc():
    result = calc(...)
    assert result
```

## 🔧 Configuración

### Configuración Centralizada
```python
# ✅ BUENO: Configuración desde clase
from payroll import PayrollConfig

config = PayrollConfig.from_env()
config.validate()

# ❌ MALO: Valores hardcodeados
regular_hours = 40  # No es configurable
```

## 📚 Documentación

### README
- ✅ Mantener README actualizado
- ✅ Documentar cambios importantes
- ✅ Incluir ejemplos de uso
- ✅ Listar dependencias

### Código
- ✅ Docstrings en todas las funciones públicas
- ✅ Type hints completos
- ✅ Ejemplos en docstrings
- ✅ Documentar excepciones

## 🎯 Checklist de Revisión

Antes de commitear código:

- [ ] Type hints completos
- [ ] Docstrings en funciones públicas
- [ ] Manejo de errores apropiado
- [ ] Logging con contexto
- [ ] Validación de inputs
- [ ] Tests para nueva funcionalidad
- [ ] Sin valores hardcodeados
- [ ] Código sigue convenciones
- [ ] Sin TODOs vagos
- [ ] Documentación actualizada

## 📖 Recursos

- [Python PEP 8](https://pep8.org/)
- [Type Hints](https://docs.python.org/3/library/typing.html)
- [Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)

