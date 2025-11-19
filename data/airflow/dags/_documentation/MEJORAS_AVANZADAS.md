# Mejoras Avanzadas - Automatización de Precios

## 🎯 Nuevas Funcionalidades Avanzadas

### 1. Circuit Breaker para APIs

Protege contra fallos en cascada cuando las APIs externas fallan.

**Configuración:**
```yaml
circuit_breaker_failures: 5      # Fallos antes de abrir
circuit_breaker_timeout: 60      # Segundos antes de intentar recuperación
```

**Estados:**
- **CLOSED**: Normal, permite requests
- **OPEN**: Bloquea requests después de fallos
- **HALF_OPEN**: Probando si el servicio se recuperó

**Uso:**
```python
from price_circuit_breaker import get_circuit_breaker, CircuitBreakerConfig

config = CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60)
breaker = get_circuit_breaker('Competitor API', config)

# Proteger llamada
result = breaker.call(api_function, *args)
```

### 2. Sistema Multi-Moneda

Convierte precios entre diferentes monedas automáticamente.

**Configuración:**
```yaml
enable_currency_conversion: true
base_currency: USD
target_currency: EUR
exchange_rate_api_url: https://api.exchangerate-api.com/v4/latest/
exchange_rate_cache_ttl: 3600
```

**Uso:**
```python
from price_currency import CurrencyConverter

converter = CurrencyConverter(config)

# Convertir precio
price_eur = converter.convert_price(100.0, 'USD', 'EUR')

# Normalizar lista de precios
normalized = converter.normalize_prices(prices, target_currency='USD')
```

**Características:**
- Conversión automática
- Caché de tasas de cambio
- Soporte para múltiples APIs
- Normalización de precios a moneda base

### 3. Optimizador de Precios

Optimiza precios usando análisis predictivo y múltiples estrategias.

**Configuración:**
```yaml
enable_price_optimization: true
optimization_strategy: balanced  # balanced, revenue_maximization, profit_maximization, market_share
price_elasticity: -1.5
min_margin: 0.20
max_margin: 0.50
```

**Estrategias Disponibles:**

#### Revenue Maximization
Maximiza ingresos totales considerando elasticidad de precio.

#### Profit Maximization
Maximiza ganancias considerando costos y márgenes.

#### Market Share
Optimiza para ganar participación de mercado (precios competitivos).

#### Balanced
Estrategia balanceada que considera:
- 40% precio de mercado
- 30% precio actual
- 30% costo + margen

**Uso:**
```python
from price_optimizer import PriceOptimizer

optimizer = PriceOptimizer(config)

result = optimizer.optimize_price(
    current_price=100.0,
    competitor_prices=[95.0, 105.0, 100.0],
    cost=70.0,
    demand_forecast=1000
)

print(f"Precio optimizado: {result['optimized_price']}")
print(f"Impacto estimado: {result['impact_estimate']}")
```

**Resultado incluye:**
- Precio optimizado
- Análisis de posición en mercado
- Estimación de impacto (demanda, ingresos)
- Nivel de confianza

### 4. Sistema de Reportes Avanzados

Genera reportes detallados y análisis de rendimiento.

**Configuración:**
```yaml
reports_dir: /tmp/price_reports
```

**Tipos de Reportes:**

#### Reporte de Ejecución
Reporte completo de cada ejecución del DAG.

```python
from price_reports import PriceReportGenerator

generator = PriceReportGenerator(config)

report = generator.generate_execution_report(
    execution_date=datetime.now(),
    extraction_result={...},
    analysis_result={...},
    publish_result={...},
    alerts=[...],
    metrics={...}
)
```

**Incluye:**
- Resumen ejecutivo
- Resultados de extracción
- Análisis de precios
- Resultados de publicación
- Alertas generadas
- Métricas de rendimiento
- Recomendaciones automáticas

#### Reporte de Tendencias
Análisis de tendencias históricas de precios.

```python
trend_report = generator.generate_trend_report(days=30)
```

**Incluye:**
- Total de cambios
- Promedio de cambios
- Volatilidad
- Tendencia general (increasing/decreasing/stable)

#### Reporte de Comparación
Comparación detallada con competencia.

```python
comparison = generator.generate_comparison_report(
    current_prices=[...],
    competitor_prices=[...]
)
```

**Incluye:**
- Productos por encima/dentro/debajo del mercado
- Diferencias porcentuales
- Análisis de posición

## 📊 Ejemplos de Uso

### Ejemplo 1: Optimización con Circuit Breaker

```python
from price_circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
from price_optimizer import PriceOptimizer

# Configurar circuit breaker
cb_config = CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60)
breaker = get_circuit_breaker('Competitor API', cb_config)

# Optimizar precio
optimizer = PriceOptimizer(config)
result = optimizer.optimize_price(
    current_price=100.0,
    competitor_prices=[95.0, 105.0],
    cost=70.0
)

# Proteger publicación con circuit breaker
def publish_price(price):
    # Lógica de publicación
    pass

breaker.call(publish_price, result['optimized_price'])
```

### Ejemplo 2: Análisis Multi-Moneda

```python
from price_currency import CurrencyConverter

converter = CurrencyConverter({
    'base_currency': 'USD',
    'target_currency': 'EUR',
    'enable_currency_conversion': True
})

# Precios en diferentes monedas
prices = [
    {'product': 'A', 'price': 100, 'currency': 'USD'},
    {'product': 'B', 'price': 90, 'currency': 'EUR'},
    {'product': 'C', 'price': 80, 'currency': 'GBP'},
]

# Normalizar a USD
normalized = converter.normalize_prices(prices, target_currency='USD')
```

### Ejemplo 3: Reporte Completo

```python
from price_reports import PriceReportGenerator
from datetime import datetime

generator = PriceReportGenerator(config)

# Generar reporte de ejecución
report = generator.generate_execution_report(
    execution_date=datetime.now(),
    extraction_result={
        'competitor_prices_count': 500,
        'failures': 0
    },
    analysis_result={
        'adjustments_count': 300
    },
    publish_result={
        'success': True,
        'products_updated': 300,
        'total_products': 500
    },
    alerts=[],
    metrics={...}
)

# Ver recomendaciones
for rec in report['recommendations']:
    print(f"- {rec}")
```

## 🔧 Integración en el DAG

Las mejoras avanzadas están integradas automáticamente en el DAG principal:

1. **Circuit Breaker**: Protege automáticamente las llamadas a APIs
2. **Conversión de Moneda**: Se activa si `enable_currency_conversion: true`
3. **Optimización**: Se activa si `enable_price_optimization: true`
4. **Reportes**: Se generan automáticamente después de cada ejecución

## 📈 Beneficios

### Circuit Breaker
- ✅ Previene fallos en cascada
- ✅ Mejora resiliencia del sistema
- ✅ Recuperación automática

### Multi-Moneda
- ✅ Soporte global
- ✅ Comparación precisa entre mercados
- ✅ Normalización automática

### Optimización
- ✅ Precios más inteligentes
- ✅ Maximización de ingresos/ganancias
- ✅ Análisis de impacto

### Reportes
- ✅ Visibilidad completa
- ✅ Análisis histórico
- ✅ Recomendaciones automáticas

## 🚀 Activar Mejoras

Editar `price_automation_config.yaml`:

```yaml
# Activar todas las mejoras
enable_currency_conversion: true
enable_price_optimization: true

# Configurar circuit breaker
circuit_breaker_failures: 5
circuit_breaker_timeout: 60

# Configurar optimización
optimization_strategy: balanced
price_elasticity: -1.5
```

### 5. **Validación Avanzada** (`price_validation.py`)
- ✅ Validación robusta con múltiples reglas
- ✅ Detección de anomalías estadísticas
- ✅ Validación de ajustes de precio
- ✅ Validación por lotes
- ✅ Análisis de cambios extremos

### 6. **Machine Learning Básico** (`price_ml.py`)
- ✅ Predicción de precios óptimos
- ✅ Múltiples modelos: regresión lineal, media móvil, promedio ponderado
- ✅ Predicción de demanda basada en elasticidad
- ✅ Cálculo de confianza en predicciones

### 7. **A/B Testing** (`price_ab_testing.py`)
- ✅ Testing de estrategias de precios
- ✅ División automática en grupos A y B
- ✅ Análisis estadístico de resultados
- ✅ Determinación de estrategia ganadora

## 📚 Documentación Relacionada

- `README_PRICE_AUTOMATION.md`: Documentación completa
- `MEJORAS_IMPLEMENTADAS.md`: Mejoras básicas
- `QUICK_START_PRICE_AUTOMATION.md`: Inicio rápido

