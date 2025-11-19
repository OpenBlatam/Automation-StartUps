# Mejoras Últimas - Automatización de Precios

## 🎯 Nuevas Funcionalidades Finales

### 1. Versionado de Precios (`price_versioning.py`)

Sistema completo de versionado con capacidad de rollback.

**Características:**
- Creación de versiones de precios
- Rollback a versiones anteriores
- Comparación de versiones
- Historial completo
- Limpieza automática de versiones antiguas

**Uso:**
```python
from price_versioning import PriceVersioning

versioning = PriceVersioning(config)

# Crear versión
version = versioning.create_version(
    'product_123',
    {'price': 100.0, 'currency': 'USD'},
    {'reason': 'market_adjustment'}
)

# Obtener versiones
versions = versioning.get_product_versions('product_123', limit=10)

# Rollback
rollback = versioning.rollback_to_version('product_123', 'old_version_id')

# Comparar versiones
comparison = versioning.compare_versions('version_1', 'version_2')
```

**Configuración:**
```yaml
enable_versioning: true
versions_dir: /tmp/price_versions
max_versions_per_product: 50
```

### 2. Sistema de Webhooks (`price_webhooks.py`)

Notificaciones automáticas a sistemas externos.

**Eventos Disponibles:**
- `price_extracted` - Precios extraídos
- `price_analyzed` - Precios analizados
- `price_published` - Precios publicados
- `price_changed` - Precio individual cambiado
- `alert_triggered` - Alerta disparada

**Uso:**
```python
from price_webhooks import PriceWebhooks

webhooks = PriceWebhooks(config)

# Notificar cambio de precio
webhooks.notify_price_changed(
    product_id='prod_123',
    product_name='Product A',
    old_price=100.0,
    new_price=120.0,
    change_percent=20.0
)

# Notificar publicación
webhooks.notify_price_published(
    products_updated=50,
    total_products=100,
    success=True
)
```

**Configuración:**
```yaml
enable_webhooks: true
webhooks:
  - url: https://example.com/webhook/prices
    events: [price_changed, price_published]
  - url: https://analytics.com/webhook
    events: [all]
webhook_timeout: 10
webhook_retry_attempts: 3
```

### 3. Reglas de Negocio (`price_business_rules.py`)

Sistema flexible de reglas de negocio personalizables.

**Reglas por Defecto:**
- Precio mínimo basado en costo
- Mantener posición competitiva
- Aumentar si está muy por debajo del mercado

**Uso:**
```python
from price_business_rules import PriceBusinessRules, BusinessRule

rules = PriceBusinessRules(config)

# Agregar regla personalizada
def my_condition(data):
    return data.get('price_change_percent', 0) > 30

def my_action(data):
    return {
        **data,
        'new_price': data['current_price'],
        'reason': 'Cambio muy grande, mantener precio'
    }

rules.add_rule(BusinessRule(
    name='limit_large_changes',
    condition=my_condition,
    action=my_action,
    priority=9
))

# Aplicar reglas
adjusted = rules.apply_rules(price_data, context)

# Aplicar a lote
adjusted_batch = rules.apply_rules_batch(price_adjustments, context)
```

**Configuración:**
```yaml
enable_business_rules: true
```

### 4. Integración con Base de Datos (`price_database.py`)

Integración completa con PostgreSQL y MySQL.

**Características:**
- Lectura de precios actuales
- Actualización de precios
- Historial en base de datos
- Soporte para múltiples productos

**Uso:**
```python
from price_database import PriceDatabase

db = PriceDatabase({
    'enable_database': True,
    'database_type': 'postgres',
    'database_conn_id': 'postgres_default',
    'prices_table': 'product_prices',
    'price_history_table': 'price_history'
})

# Obtener precios actuales
current_prices = db.get_current_prices()

# Obtener precios específicos
product_prices = db.get_current_prices(['prod1', 'prod2'])

# Actualizar precios
updates = [
    {
        'product_id': 'prod1',
        'new_price': 120.0,
        'current_price': 100.0,
        'price_change_percent': 20.0,
        'reason': 'market_adjustment'
    }
]
updated = db.update_prices(updates)

# Obtener historial desde BD
history = db.get_price_history_from_db('prod1', days=30)
```

**Configuración:**
```yaml
enable_database: true
database_type: postgres  # postgres, mysql
database_conn_id: postgres_default
prices_table: product_prices
price_history_table: price_history
```

**Esquema de Tablas Sugerido:**

```sql
-- Tabla de precios actuales
CREATE TABLE product_prices (
    product_id VARCHAR(255) PRIMARY KEY,
    product_name VARCHAR(255),
    price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de historial
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(255),
    product_name VARCHAR(255),
    old_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2),
    change_percent DECIMAL(5, 2),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_history_product ON price_history(product_id);
CREATE INDEX idx_price_history_date ON price_history(created_at);
```

## 🔧 Integración Completa

Todas las mejoras están integradas en el DAG principal:

```python
# Versionado automático después de publicar
if price_versioning:
    for adjustment in validated_adjustments:
        versioning.create_version(
            adjustment['product_id'],
            {'price': adjustment['new_price']},
            {'reason': adjustment['reason']}
        )

# Webhooks automáticos
if price_webhooks:
    webhooks.notify_price_published(
        products_updated=len(validated_adjustments),
        total_products=total,
        success=True
    )

# Aplicar reglas de negocio
if business_rules:
    validated_adjustments = business_rules.apply_rules_batch(
        validated_adjustments,
        context={'competitor_prices': competitor_prices}
    )

# Integración con BD
if price_database:
    current_prices = price_database.get_current_prices()
    price_database.update_prices(validated_adjustments)
```

## 📊 Resumen de Todas las Mejoras

### Total: 19 Módulos

**Ronda 1 (Básicas):** 5 módulos
**Ronda 2 (Avanzadas):** 4 módulos
**Ronda 3 (Finales):** 3 módulos
**Ronda 4 (Adicionales):** 3 módulos
**Ronda 5 (Últimas):** 4 módulos

## 🎉 Sistema Completo

El sistema ahora incluye:
- ✅ 19 módulos especializados
- ✅ Versionado completo con rollback
- ✅ Webhooks para integraciones
- ✅ Reglas de negocio flexibles
- ✅ Integración con bases de datos
- ✅ Y todas las mejoras anteriores

**Sistema de Automatización de Precios - Versión Final Completa**
*19 módulos | 5 rondas de mejoras | Listo para producción enterprise*








