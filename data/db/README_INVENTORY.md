# Sistema de Gestión de Inventario

Sistema completo de automatización para gestión de inventario, monitoreo de stocks, generación de reordenes automáticos y alertas para reducir quiebre de inventario.

## 📋 Estructura

```
data/db/
├── inventory_schema.sql      # Esquema de tablas de inventario
├── inventory_indexes.sql     # Índices optimizados
├── inventory_views.sql       # Vistas y vistas materializadas
└── README_INVENTORY.md       # Esta documentación

data/airflow/dags/
├── inventory_monitor.py      # DAG de monitoreo y alertas
├── inventory_reorder.py      # DAG de reorden automático
└── inventory_reports.py      # DAG de reportes diarios
```

## 🗄️ Esquema de Base de Datos

### Tablas Principales

#### `inventory_products`
Catálogo de productos con configuración de reorden:
- Información básica: SKU, nombre, descripción, categoría
- Proveedor: ID, nombre, email
- Precios: costo unitario, precio de venta
- Configuración de reorden: punto de reorden, cantidad de reorden, stock máximo, lead time
- Integraciones: Stripe, QuickBooks, IDs externos

#### `inventory_stock`
Stock actual por producto:
- Cantidad disponible y reservada
- Ubicación/almacén (soporte multi-almacén)
- Fechas importantes: última reposición, última venta, fecha de expiración

#### `inventory_movements`
Historial completo de movimientos:
- Tipos: compra, venta, ajuste, devolución, transferencia, reserva
- Tracking: cantidad antes/después, referencias a órdenes/facturas
- Auditoría: usuario/sistema que realizó el movimiento

#### `inventory_alerts`
Sistema de alertas:
- Tipos: stock bajo, sin stock, tiempo de reorden, sobrestock, próximos a vencer
- Severidad: baja, media, alta, crítica
- Estado: abierta, reconocida, resuelta, ignorada

#### `inventory_reorders`
Reordenes automáticos generados:
- Estado: pendiente, enviado, confirmado, recibido, cancelado
- Prioridad: baja, normal, alta, urgente
- Información de proveedor y fechas de entrega esperadas

#### `inventory_suppliers`
Catálogo de proveedores:
- Información de contacto
- Términos de pago
- Lead time por defecto

#### `inventory_demand_forecast`
Predicciones de demanda futura:
- Predicciones por fecha
- Método usado (promedio móvil, suavizado exponencial, ML, etc.)
- Nivel de confianza

### Vistas y Vistas Materializadas

#### `v_inventory_current_stock`
Vista de stock actual con estados y cálculos:
- Stock disponible vs. punto de reorden
- Estado del stock (normal, bajo, sin stock, sobrestock)
- Días estimados hasta quiebre

#### `v_inventory_active_alerts`
Alertas activas ordenadas por severidad:
- Información completa del producto
- Horas que lleva abierta la alerta

#### `v_inventory_pending_reorders`
Reordenes pendientes ordenados por prioridad:
- Información de producto y proveedor
- Días hasta entrega esperada

#### `mv_inventory_daily_stats`
Estadísticas diarias agregadas de movimientos:
- Productos restockeados/vendidos
- Totales de entrada/salida
- Últimos 90 días

#### `mv_inventory_critical_products`
Productos con stock bajo o sin stock:
- Estado actual
- Alertas y reordenes pendientes
- Información de proveedor

#### `mv_inventory_performance`
Métricas de rendimiento:
- Rotación de stock (turnover ratio)
- Días de stock disponible
- Tasa de quiebre de stock

## 🔄 DAGs de Airflow

### `inventory_monitor`
**Frecuencia**: Cada 30 minutos  
**Propósito**: Monitoreo continuo de inventario

**Tareas**:
1. `check_stock_levels`: Verifica niveles de stock y detecta productos críticos
2. `create_alerts`: Crea alertas en BD para productos críticos
3. `check_expiring_products`: Verifica productos próximos a vencer
4. `send_notifications`: Envía notificaciones Slack/Email para alertas críticas
5. `log_metrics`: Registra métricas

**Alertas generadas**:
- `out_of_stock`: Stock = 0 (severidad: crítica)
- `low_stock`: Stock ≤ punto de reorden (severidad: media/alta)
- `expiring_soon`: Productos que expiran en ≤30 días

### `inventory_reorder`
**Frecuencia**: Cada 4 horas  
**Propósito**: Generación automática de reordenes

**Tareas**:
1. `find_products_needing_reorder`: Encuentra productos que necesitan reorden
2. `generate_reorders`: Calcula cantidad óptima y crea reordenes
3. `send_reorder_notifications`: Notifica sobre reordenes generados
4. `log_metrics`: Registra métricas

**Lógica de reorden**:
- Calcula cantidad óptima basada en:
  - Velocidad de venta (últimos 30 días)
  - Lead time del proveedor
  - Punto de reorden configurado
  - Stock máximo (si aplica)
- Determina prioridad:
  - `urgent`: Stock = 0 o días hasta quiebre ≤ 3
  - `high`: Stock ≤ 30% del punto de reorden
  - `normal`: Stock entre 30-100% del punto de reorden

### `inventory_reports`
**Frecuencia**: Diario a las 8:00 UTC  
**Propósito**: Reportes diarios de métricas

**Tareas**:
1. `generate_daily_report`: Genera métricas y refresca vistas materializadas
2. `send_daily_report`: Envía reporte por Slack y Email
3. `log_metrics`: Registra métricas

**Métricas incluidas**:
- Total productos activos
- Productos críticos (sin stock / stock bajo)
- Alertas abiertas
- Reordenes pendientes
- Valor total de inventario
- Movimientos del día anterior
- Top productos críticos
- Top productos con más movimiento

## 🚀 Instalación

### 1. Crear esquema de base de datos

```bash
# Aplicar esquema completo
psql $KPIS_PG_DSN -f data/db/inventory_schema.sql
psql $KPIS_PG_DSN -f data/db/inventory_indexes.sql
psql $KPIS_PG_DSN -f data/db/inventory_views.sql
```

### 2. Configurar variables de entorno (opcional)

```bash
# Airflow Variables
airflow variables set INVENTORY_ENABLE_NOTIFICATIONS true
airflow variables set INVENTORY_ALERT_EMAIL inventory@example.com
```

### 3. Activar DAGs en Airflow

Los DAGs se activarán automáticamente. Verificar en la UI de Airflow:
- `inventory_monitor`
- `inventory_reorder`
- `inventory_reports`

## 📊 Uso

### Insertar productos

```sql
INSERT INTO inventory_products (
    sku, name, category, reorder_point, reorder_quantity,
    supplier_name, supplier_email, unit_cost, lead_time_days
) VALUES (
    'PROD-001', 'Producto Ejemplo', 'Categoría A', 10, 50,
    'Proveedor XYZ', 'proveedor@example.com', 25.50, 7
);
```

### Inicializar stock

```sql
INSERT INTO inventory_stock (product_id, quantity)
SELECT id, 100 FROM inventory_products WHERE sku = 'PROD-001';
```

### Registrar movimiento de inventario

```sql
-- Venta
INSERT INTO inventory_movements (
    product_id, movement_type, direction, quantity,
    reference_type, reference_id, notes
) VALUES (
    (SELECT id FROM inventory_products WHERE sku = 'PROD-001'),
    'sale', 'out', 5,
    'order', 'ORD-12345', 'Venta online'
);

-- Compra/Reposición
INSERT INTO inventory_movements (
    product_id, movement_type, direction, quantity,
    reference_type, reference_id, notes
) VALUES (
    (SELECT id FROM inventory_products WHERE sku = 'PROD-001'),
    'purchase', 'in', 50,
    'reorder', (SELECT id FROM inventory_reorders WHERE product_id = (SELECT id FROM inventory_products WHERE sku = 'PROD-001') LIMIT 1),
    'Reorden recibido'
);
```

### Consultar productos críticos

```sql
SELECT * FROM mv_inventory_critical_products
ORDER BY 
    CASE status WHEN 'out_of_stock' THEN 1 ELSE 2 END,
    current_stock;
```

### Consultar alertas abiertas

```sql
SELECT * FROM v_inventory_active_alerts
ORDER BY severity, created_at DESC;
```

### Consultar reordenes pendientes

```sql
SELECT * FROM v_inventory_pending_reorders
ORDER BY priority, requested_at;
```

## 🔔 Notificaciones

### Slack
Se envían automáticamente cuando:
- Hay productos sin stock (crítico)
- Se generan nuevos reordenes
- Reporte diario

Configurar webhook:
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Email
Se envían automáticamente cuando:
- Hay productos sin stock (crítico)
- Reporte diario

Configurar SMTP:
```bash
export SMTP_HOST=smtp.example.com
export SMTP_USER=inventory@example.com
export SMTP_PASSWORD=...
```

## 📈 Métricas y KPIs

### Métricas clave

1. **Tasa de quiebre de stock**: % de productos sin stock
2. **Rotación de stock**: Ventas / Stock promedio
3. **Días de stock disponible**: Stock actual / Ventas diarias promedio
4. **Precisión de reorden**: % de veces que se evita quiebre
5. **Tiempo de respuesta**: Tiempo desde alerta hasta reorden

### Consultar métricas

```sql
-- Rotación de stock por producto
SELECT * FROM mv_inventory_performance
WHERE turnover_ratio_30d > 0
ORDER BY turnover_ratio_30d DESC;

-- Días de stock disponible
SELECT 
    sku, 
    product_name,
    days_of_stock,
    CASE 
        WHEN days_of_stock < 7 THEN 'Crítico'
        WHEN days_of_stock < 14 THEN 'Bajo'
        WHEN days_of_stock < 30 THEN 'Normal'
        ELSE 'Alto'
    END AS stock_status
FROM mv_inventory_performance
WHERE days_of_stock IS NOT NULL
ORDER BY days_of_stock;
```

## 🔧 Mantenimiento

### Refrescar vistas materializadas

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_daily_stats;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_critical_products;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_performance;
```

Esto se hace automáticamente por el DAG `inventory_reports`.

### Limpiar alertas resueltas antiguas

```sql
-- Eliminar alertas resueltas de hace más de 90 días
DELETE FROM inventory_alerts
WHERE status = 'resolved'
AND resolved_at < NOW() - INTERVAL '90 days';
```

### Archivar movimientos antiguos

```sql
-- Crear tabla de archivo (si es necesario)
CREATE TABLE IF NOT EXISTS inventory_movements_archive 
AS TABLE inventory_movements WITH NO DATA;

-- Mover movimientos de hace más de 1 año
INSERT INTO inventory_movements_archive
SELECT * FROM inventory_movements
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM inventory_movements
WHERE created_at < NOW() - INTERVAL '1 year';
```

## 🔗 Integraciones

### Stripe
Los productos pueden tener un `stripe_product_id` para sincronización con Stripe.

### QuickBooks
Los productos pueden tener un `quickbooks_item_id` para sincronización con QuickBooks.

### APIs
Los DAGs pueden ser extendidos para:
- Enviar reordenes directamente a proveedores vía API
- Sincronizar stock con sistemas externos
- Actualizar dashboards en tiempo real

## 🆕 Funcionalidades Avanzadas

### Predicción de Demanda (`inventory_demand_forecast`)
- **Frecuencia**: Diario a las 2:00 AM
- Calcula predicciones usando promedio móvil y suavizado exponencial
- Optimiza automáticamente puntos de reorden basado en predicciones
- Almacena forecasts para los próximos 30 días

### Análisis ABC/XYZ (`inventory_abc_analysis`)
- **Frecuencia**: Semanal los domingos
- Clasificación ABC por valor (A: 80% valor, B: 15%, C: 5%)
- Clasificación XYZ por variabilidad de demanda (X: predecible, Y: media, Z: impredecible)
- Almacena clasificaciones para estrategias diferenciadas

### Gestión de Reservas (`inventory_reservations`)
- **Frecuencia**: Cada 15 minutos
- Expira reservas antiguas (>24 horas) automáticamente
- Detecta productos oversold (más reservas que stock)
- Actualiza cantidades reservadas desde reservas activas

### Sincronización Externa (`inventory_sync_external`)
- **Frecuencia**: Cada 6 horas
- Sincroniza productos desde Stripe
- Sincroniza ítems desde QuickBooks
- Mantiene productos actualizados automáticamente

### Órdenes de Compra
- Gestión completa de purchase orders
- Aprobaciones de reordenes
- Tracking de recepciones
- Integración con reordenes automáticos

### Utilidades (`utils/inventory_utils.py`)
Funciones helper para:
- `reserve_stock()`: Reservar stock para órdenes
- `release_reservation()`: Liberar reservas
- `record_sale()`: Registrar ventas
- `record_purchase()`: Registrar compras
- `get_product_stock_status()`: Estado de stock
- `calculate_sales_velocity()`: Velocidad de venta

## 📝 Mejoras Futuras

- [ ] Predicción de demanda con ML avanzado
- [ ] Integración con APIs de proveedores para envío automático de POs
- [ ] Dashboard en tiempo real con WebSockets
- [ ] Optimización de costos de almacenamiento
- [ ] Gestión avanzada de múltiples ubicaciones/almacenes
- [ ] Tracking de lotes y expiración avanzado
- [ ] Integración con sistemas de envío/logística

## 🐛 Troubleshooting

### Alertas no se están generando
- Verificar que el DAG `inventory_monitor` esté activo
- Revisar logs del DAG
- Verificar que existan productos con stock bajo

### Reordenes no se generan
- Verificar que el DAG `inventory_reorder` esté activo
- Verificar que no existan reordenes pendientes previos
- Revisar logs para productos específicos

### Notificaciones no se envían
- Verificar variables de entorno (SLACK_WEBHOOK_URL, SMTP_*)
- Revisar logs de notificaciones
- Verificar que NOTIFICATIONS_AVAILABLE = True

