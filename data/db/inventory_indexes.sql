-- ============================================================================
-- Índices para Gestión de Inventario
-- ============================================================================
-- Optimización de consultas frecuentes

-- Índices para inventory_products
CREATE INDEX IF NOT EXISTS idx_inventory_products_sku ON inventory_products(sku);
CREATE INDEX IF NOT EXISTS idx_inventory_products_active ON inventory_products(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_inventory_products_category ON inventory_products(category);
CREATE INDEX IF NOT EXISTS idx_inventory_products_supplier ON inventory_products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_inventory_products_stripe ON inventory_products(stripe_product_id) WHERE stripe_product_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_products_quickbooks ON inventory_products(quickbooks_item_id) WHERE quickbooks_item_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_products_updated ON inventory_products(updated_at DESC);

-- Índices para inventory_stock
CREATE INDEX IF NOT EXISTS idx_inventory_stock_product ON inventory_stock(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_quantity ON inventory_stock(quantity);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_available ON inventory_stock(available_quantity);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_location ON inventory_stock(location) WHERE location IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_stock_warehouse ON inventory_stock(warehouse) WHERE warehouse IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_stock_expires ON inventory_stock(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_stock_low_stock ON inventory_stock(product_id, available_quantity) WHERE available_quantity < 10;

-- Índices compuestos para consultas comunes
CREATE INDEX IF NOT EXISTS idx_inventory_stock_product_quantity ON inventory_stock(product_id, available_quantity);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_product_updated ON inventory_stock(product_id, updated_at DESC);

-- Índices para inventory_movements
CREATE INDEX IF NOT EXISTS idx_inventory_movements_product ON inventory_movements(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_stock ON inventory_movements(stock_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_type ON inventory_movements(movement_type);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_direction ON inventory_movements(direction);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_created ON inventory_movements(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_reference ON inventory_movements(reference_type, reference_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_product_created ON inventory_movements(product_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_product_type ON inventory_movements(product_id, movement_type, created_at DESC);

-- Índices para inventory_alerts
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_product ON inventory_alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_stock ON inventory_alerts(stock_id);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_type ON inventory_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_status ON inventory_alerts(status);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_severity ON inventory_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_open ON inventory_alerts(status, severity, created_at DESC) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_product_status ON inventory_alerts(product_id, status);
CREATE INDEX IF NOT EXISTS idx_inventory_alerts_created ON inventory_alerts(created_at DESC);

-- Índices para inventory_reorders
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_product ON inventory_reorders(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_status ON inventory_reorders(status);
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_priority ON inventory_reorders(priority);
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_supplier ON inventory_reorders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_pending ON inventory_reorders(status, priority, requested_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_requested ON inventory_reorders(requested_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_expected ON inventory_reorders(expected_delivery_date) WHERE expected_delivery_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_inventory_reorders_product_status ON inventory_reorders(product_id, status);

-- Índices para inventory_suppliers
CREATE INDEX IF NOT EXISTS idx_inventory_suppliers_name ON inventory_suppliers(name);
CREATE INDEX IF NOT EXISTS idx_inventory_suppliers_active ON inventory_suppliers(active) WHERE active = TRUE;

-- Índices para inventory_demand_forecast
CREATE INDEX IF NOT EXISTS idx_inventory_forecast_product ON inventory_demand_forecast(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_forecast_date ON inventory_demand_forecast(forecast_date);
CREATE INDEX IF NOT EXISTS idx_inventory_forecast_product_date ON inventory_demand_forecast(product_id, forecast_date DESC);

-- Índices para consultas de monitoreo (productos con stock bajo)
CREATE INDEX IF NOT EXISTS idx_inventory_monitoring_low_stock 
ON inventory_stock(product_id, available_quantity) 
WHERE available_quantity <= (
    SELECT reorder_point FROM inventory_products WHERE id = inventory_stock.product_id
);

-- Índice para productos activos con información de stock
CREATE INDEX IF NOT EXISTS idx_inventory_active_with_stock
ON inventory_products(id)
INCLUDE (sku, name, reorder_point)
WHERE active = TRUE;

COMMENT ON INDEX idx_inventory_stock_low_stock IS 'Índice para búsquedas rápidas de stock bajo';
COMMENT ON INDEX idx_inventory_alerts_open IS 'Índice para alertas abiertas ordenadas por severidad';
COMMENT ON INDEX idx_inventory_reorders_pending IS 'Índice para reordenes pendientes ordenados por prioridad';





