# Quick Start - Sistema de Inventario

Guía rápida para empezar a usar el sistema de gestión de inventario.

## 🚀 Instalación Rápida

### 1. Crear esquema de base de datos

```bash
# Aplicar todos los esquemas
psql $KPIS_PG_DSN -f data/db/inventory_schema.sql
psql $KPIS_PG_DSN -f data/db/inventory_indexes.sql
psql $KPIS_PG_DSN -f data/db/inventory_views.sql
psql $KPIS_PG_DSN -f data/db/inventory_orders_schema.sql
```

### 2. Crear producto de ejemplo

```sql
-- Insertar producto
INSERT INTO inventory_products (
    sku, name, category, reorder_point, reorder_quantity,
    supplier_name, supplier_email, unit_cost, lead_time_days
) VALUES (
    'DEMO-001', 'Producto Demo', 'Categoría A', 10, 50,
    'Proveedor Demo', 'proveedor@demo.com', 25.50, 7
) RETURNING id;

-- Inicializar stock
INSERT INTO inventory_stock (product_id, quantity)
SELECT id, 100 FROM inventory_products WHERE sku = 'DEMO-001';
```

### 3. Registrar movimiento de prueba

```sql
-- Simular una venta
INSERT INTO inventory_movements (
    product_id, movement_type, direction, quantity,
    reference_type, reference_id, notes
) 
SELECT 
    id, 'sale', 'out', 5,
    'order', 'ORD-12345', 'Venta de prueba'
FROM inventory_products 
WHERE sku = 'DEMO-001';
```

### 4. Verificar que funciona

```sql
-- Ver stock actual
SELECT * FROM v_inventory_current_stock WHERE sku = 'DEMO-001';

-- Ver alertas (si el stock está bajo)
SELECT * FROM v_inventory_active_alerts;

-- Ver reordenes pendientes
SELECT * FROM v_inventory_pending_reorders;
```

## 📊 DAGs Disponibles

Una vez activados en Airflow, estos DAGs se ejecutarán automáticamente:

| DAG | Frecuencia | Propósito |
|-----|------------|-----------|
| `inventory_monitor` | Cada 30 min | Monitoreo y alertas |
| `inventory_reorder` | Cada 4 horas | Reorden automático |
| `inventory_reports` | Diario 8:00 | Reportes diarios |
| `inventory_demand_forecast` | Diario 2:00 | Predicción de demanda |
| `inventory_abc_analysis` | Semanal | Análisis ABC/XYZ |
| `inventory_reservations` | Cada 15 min | Gestión de reservas |
| `inventory_sync_external` | Cada 6 horas | Sincronización Stripe/QB |

## 🔧 Uso Básico con Python

```python
from utils.inventory_utils import (
    reserve_stock,
    record_sale,
    get_product_stock_status,
)

# Reservar stock para una orden
reserve_stock(
    product_id="uuid-del-producto",
    quantity=5,
    reference_id="ORD-12345",
    reference_type="order"
)

# Registrar una venta
record_sale(
    product_id="uuid-del-producto",
    quantity=3,
    reference_id="ORD-12345",
    reference_type="order"
)

# Ver estado de stock
status = get_product_stock_status("uuid-del-producto")
print(f"Stock disponible: {status['available']}")
print(f"Estado: {status['status']}")
```

## 📈 Consultas Útiles

### Productos críticos
```sql
SELECT * FROM mv_inventory_critical_products
ORDER BY 
    CASE status WHEN 'out_of_stock' THEN 1 ELSE 2 END,
    current_stock;
```

### Top productos por valor
```sql
SELECT 
    p.sku,
    p.name,
    s.available_quantity * p.unit_cost AS total_value
FROM inventory_products p
JOIN inventory_stock s ON p.id = s.product_id
WHERE p.active = TRUE
ORDER BY total_value DESC
LIMIT 10;
```

### Rotación de stock
```sql
SELECT 
    sku,
    product_name,
    turnover_ratio_30d,
    days_of_stock
FROM mv_inventory_performance
WHERE turnover_ratio_30d > 0
ORDER BY turnover_ratio_30d DESC;
```

## 🎯 Próximos Pasos

1. **Configurar notificaciones** (opcional):
   ```bash
   export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
   export SMTP_HOST=smtp.example.com
   ```

2. **Sincronizar con Stripe/QuickBooks** (opcional):
   ```bash
   export STRIPE_API_KEY=sk_...
   export QUICKBOOKS_ACCESS_TOKEN=...
   export QUICKBOOKS_REALM_ID=...
   ```

3. **Revisar DAGs en Airflow UI** y activarlos

4. **Monitorear métricas** en los reportes diarios

## 📚 Documentación Completa

Ver `README_INVENTORY.md` para documentación completa del sistema.

