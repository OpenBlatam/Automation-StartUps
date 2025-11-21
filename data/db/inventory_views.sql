-- ============================================================================
-- Vistas Materializadas para KPIs de Inventario
-- ============================================================================

-- Vista: Stock actual con información de productos
CREATE OR REPLACE VIEW v_inventory_current_stock AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    p.category,
    p.reorder_point,
    p.reorder_quantity,
    p.lead_time_days,
    p.supplier_name,
    p.active,
    COALESCE(s.quantity, 0) AS current_quantity,
    COALESCE(s.reserved_quantity, 0) AS reserved_quantity,
    COALESCE(s.available_quantity, 0) AS available_quantity,
    s.location,
    s.warehouse,
    s.last_restocked_at,
    s.last_sold_at,
    -- Estado del stock
    CASE 
        WHEN COALESCE(s.available_quantity, 0) = 0 THEN 'out_of_stock'
        WHEN COALESCE(s.available_quantity, 0) <= p.reorder_point THEN 'low_stock'
        WHEN p.max_stock IS NOT NULL AND COALESCE(s.available_quantity, 0) >= p.max_stock THEN 'overstock'
        ELSE 'normal'
    END AS stock_status,
    -- Días hasta quiebre estimado (simplificado)
    CASE 
        WHEN COALESCE(s.available_quantity, 0) = 0 THEN 0
        WHEN s.last_sold_at IS NULL THEN NULL
        ELSE GREATEST(1, 
            EXTRACT(EPOCH FROM (NOW() - s.last_sold_at)) / 86400.0 / 
            NULLIF(COALESCE(s.available_quantity, 0), 0) * 
            (SELECT COUNT(*)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1)
             FROM inventory_movements 
             WHERE product_id = p.id 
             AND movement_type = 'sale' 
             AND created_at >= NOW() - INTERVAL '30 days')
        )::INTEGER
    END AS days_until_stockout,
    p.updated_at AS product_updated_at,
    s.updated_at AS stock_updated_at
FROM inventory_products p
LEFT JOIN inventory_stock s ON p.id = s.product_id
WHERE p.active = TRUE;

-- Vista: Alertas activas con información completa
CREATE OR REPLACE VIEW v_inventory_active_alerts AS
SELECT 
    a.id AS alert_id,
    a.alert_type,
    a.severity,
    a.status,
    a.message,
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    p.category,
    s.available_quantity AS current_stock,
    p.reorder_point,
    a.created_at,
    a.acknowledged_at,
    a.resolved_at,
    EXTRACT(EPOCH FROM (NOW() - a.created_at)) / 3600 AS hours_open
FROM inventory_alerts a
JOIN inventory_products p ON a.product_id = p.id
LEFT JOIN inventory_stock s ON a.stock_id = s.id
WHERE a.status IN ('open', 'acknowledged')
ORDER BY 
    CASE a.severity 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    a.created_at DESC;

-- Vista: Reordenes pendientes
CREATE OR REPLACE VIEW v_inventory_pending_reorders AS
SELECT 
    r.id AS reorder_id,
    r.product_id,
    p.sku,
    p.name AS product_name,
    p.category,
    r.quantity AS reorder_quantity,
    r.unit_cost,
    r.total_cost,
    r.status,
    r.priority,
    r.supplier_name,
    r.supplier_email,
    r.requested_at,
    r.expected_delivery_date,
    s.available_quantity AS current_stock,
    p.reorder_point,
    EXTRACT(EPOCH FROM (r.expected_delivery_date::TIMESTAMP - NOW())) / 86400 AS days_until_delivery
FROM inventory_reorders r
JOIN inventory_products p ON r.product_id = p.id
LEFT JOIN inventory_stock s ON r.product_id = s.product_id
WHERE r.status IN ('pending', 'sent', 'confirmed')
ORDER BY 
    CASE r.priority 
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        ELSE 4
    END,
    r.requested_at;

-- Vista: Movimientos recientes por producto
CREATE OR REPLACE VIEW v_inventory_recent_movements AS
SELECT 
    m.id AS movement_id,
    m.product_id,
    p.sku,
    p.name AS product_name,
    m.movement_type,
    m.direction,
    m.quantity,
    m.quantity_before,
    m.quantity_after,
    m.reference_type,
    m.reference_id,
    m.notes,
    m.created_by,
    m.created_at
FROM inventory_movements m
JOIN inventory_products p ON m.product_id = p.id
WHERE m.created_at >= NOW() - INTERVAL '30 days'
ORDER BY m.created_at DESC;

-- Vista Materializada: Estadísticas diarias de inventario
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_daily_stats AS
SELECT 
    DATE(created_at) AS stat_date,
    COUNT(DISTINCT product_id) AS total_products,
    COUNT(DISTINCT CASE WHEN movement_type = 'purchase' THEN product_id END) AS products_restocked,
    COUNT(DISTINCT CASE WHEN movement_type = 'sale' THEN product_id END) AS products_sold,
    SUM(CASE WHEN direction = 'in' THEN quantity ELSE 0 END) AS total_incoming,
    SUM(CASE WHEN direction = 'out' THEN quantity ELSE 0 END) AS total_outgoing,
    COUNT(DISTINCT reference_id) AS unique_transactions
FROM inventory_movements
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at)
ORDER BY stat_date DESC;

-- Vista Materializada: Productos críticos (stock bajo o sin stock)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_critical_products AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    p.category,
    p.reorder_point,
    p.reorder_quantity,
    COALESCE(s.available_quantity, 0) AS current_stock,
    CASE 
        WHEN COALESCE(s.available_quantity, 0) = 0 THEN 'out_of_stock'
        WHEN COALESCE(s.available_quantity, 0) <= p.reorder_point THEN 'low_stock'
        ELSE 'normal'
    END AS status,
    p.supplier_name,
    p.supplier_email,
    p.lead_time_days,
    s.last_sold_at,
    (SELECT COUNT(*) FROM inventory_alerts WHERE product_id = p.id AND status = 'open') AS open_alerts,
    (SELECT COUNT(*) FROM inventory_reorders WHERE product_id = p.id AND status IN ('pending', 'sent', 'confirmed')) AS pending_reorders,
    p.updated_at
FROM inventory_products p
LEFT JOIN inventory_stock s ON p.id = s.product_id
WHERE p.active = TRUE 
AND (COALESCE(s.available_quantity, 0) <= p.reorder_point OR s.available_quantity IS NULL)
ORDER BY 
    CASE 
        WHEN COALESCE(s.available_quantity, 0) = 0 THEN 1
        ELSE 2
    END,
    COALESCE(s.available_quantity, 0);

-- Vista Materializada: Métricas de rendimiento de inventario
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_inventory_performance AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    -- Rotación de stock (ventas últimos 30 días / stock promedio)
    COALESCE(
        (SELECT SUM(quantity) 
         FROM inventory_movements 
         WHERE product_id = p.id 
         AND movement_type = 'sale' 
         AND created_at >= NOW() - INTERVAL '30 days')::DECIMAL / 
        NULLIF(
            (SELECT AVG(quantity_after) 
             FROM inventory_movements 
             WHERE product_id = p.id 
             AND created_at >= NOW() - INTERVAL '30 days'), 0
        ), 0
    ) AS turnover_ratio_30d,
    -- Días de stock disponible
    CASE 
        WHEN (SELECT SUM(quantity) FROM inventory_movements 
              WHERE product_id = p.id AND movement_type = 'sale' 
              AND created_at >= NOW() - INTERVAL '30 days') > 0
        THEN COALESCE(s.available_quantity, 0)::DECIMAL / 
             NULLIF(
                 (SELECT AVG(daily_sales) FROM (
                     SELECT DATE(created_at), SUM(quantity) AS daily_sales
                     FROM inventory_movements 
                     WHERE product_id = p.id 
                     AND movement_type = 'sale' 
                     AND created_at >= NOW() - INTERVAL '30 days'
                     GROUP BY DATE(created_at)
                 ) daily), 0
             ), 0
        ELSE NULL
    END AS days_of_stock,
    -- Precisión de predicción (si hay forecast)
    NULL AS forecast_accuracy,
    -- Tasa de quiebre de stock
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM inventory_alerts 
            WHERE product_id = p.id 
            AND alert_type = 'out_of_stock' 
            AND created_at >= NOW() - INTERVAL '90 days'
        ) THEN TRUE 
        ELSE FALSE 
    END AS has_stockout_90d,
    p.updated_at
FROM inventory_products p
LEFT JOIN inventory_stock s ON p.id = s.product_id
WHERE p.active = TRUE;

-- Índices para vistas materializadas
CREATE INDEX IF NOT EXISTS idx_mv_inventory_daily_stats_date ON mv_inventory_daily_stats(stat_date DESC);
CREATE INDEX IF NOT EXISTS idx_mv_inventory_critical_products_status ON mv_inventory_critical_products(status);
CREATE INDEX IF NOT EXISTS idx_mv_inventory_critical_products_product ON mv_inventory_critical_products(product_id);
CREATE INDEX IF NOT EXISTS idx_mv_inventory_performance_product ON mv_inventory_performance(product_id);

-- Comentarios
COMMENT ON VIEW v_inventory_current_stock IS 'Vista de stock actual con estados y cálculos';
COMMENT ON VIEW v_inventory_active_alerts IS 'Alertas activas ordenadas por severidad';
COMMENT ON VIEW v_inventory_pending_reorders IS 'Reordenes pendientes ordenados por prioridad';
COMMENT ON VIEW v_inventory_recent_movements IS 'Movimientos recientes de inventario';
COMMENT ON MATERIALIZED VIEW mv_inventory_daily_stats IS 'Estadísticas diarias agregadas de movimientos';
COMMENT ON MATERIALIZED VIEW mv_inventory_critical_products IS 'Productos con stock bajo o sin stock';
COMMENT ON MATERIALIZED VIEW mv_inventory_performance IS 'Métricas de rendimiento de inventario por producto';





