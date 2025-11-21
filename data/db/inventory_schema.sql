-- ============================================================================
-- Esquema de Gestión de Inventario
-- ============================================================================
-- Sistema completo para monitoreo de stocks, reordenes automáticos y alertas
-- para reducir quiebre de inventario

-- Tabla de productos/ítems
CREATE TABLE IF NOT EXISTS inventory_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(128) UNIQUE NOT NULL,
    name VARCHAR(512) NOT NULL,
    description TEXT,
    category VARCHAR(128),
    supplier_id UUID,
    supplier_name VARCHAR(256),
    supplier_email VARCHAR(256),
    unit_cost DECIMAL(10, 2),
    unit_price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    active BOOLEAN DEFAULT TRUE,
    
    -- Configuración de reorden
    reorder_point INTEGER NOT NULL DEFAULT 10,
    reorder_quantity INTEGER NOT NULL DEFAULT 50,
    max_stock INTEGER,
    lead_time_days INTEGER DEFAULT 7,  -- Tiempo de entrega del proveedor
    
    -- Integraciones
    stripe_product_id VARCHAR(128),
    quickbooks_item_id VARCHAR(128),
    external_id VARCHAR(256),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_reorder_point CHECK (reorder_point >= 0),
    CONSTRAINT check_reorder_quantity CHECK (reorder_quantity > 0),
    CONSTRAINT check_lead_time CHECK (lead_time_days >= 0)
);

-- Tabla de stock actual por producto
CREATE TABLE IF NOT EXISTS inventory_stock (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL UNIQUE REFERENCES inventory_products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,  -- Stock reservado para órdenes pendientes
    available_quantity INTEGER GENERATED ALWAYS AS (quantity - reserved_quantity) STORED,
    
    -- Ubicaciones (opcional, para multi-almacén)
    location VARCHAR(128),
    warehouse VARCHAR(128),
    
    -- Fechas importantes
    last_restocked_at TIMESTAMPTZ,
    last_sold_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,  -- Para productos perecederos
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_quantity CHECK (quantity >= 0),
    CONSTRAINT check_reserved CHECK (reserved_quantity >= 0 AND reserved_quantity <= quantity)
);

-- Tabla de movimientos de inventario (historial completo)
CREATE TABLE IF NOT EXISTS inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
    stock_id UUID REFERENCES inventory_stock(id) ON DELETE SET NULL,
    
    -- Tipo de movimiento
    movement_type VARCHAR(32) NOT NULL,  -- 'purchase', 'sale', 'adjustment', 'return', 'transfer', 'reservation'
    direction VARCHAR(8) NOT NULL,  -- 'in' o 'out'
    quantity INTEGER NOT NULL,
    quantity_before INTEGER,
    quantity_after INTEGER,
    
    -- Referencias
    reference_id VARCHAR(256),  -- ID de orden, factura, etc.
    reference_type VARCHAR(64),  -- 'order', 'invoice', 'manual', etc.
    notes TEXT,
    
    -- Usuario/sistema que realizó el movimiento
    created_by VARCHAR(128),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_movement_quantity CHECK (quantity > 0),
    CONSTRAINT check_direction CHECK (direction IN ('in', 'out'))
);

-- Tabla de alertas de inventario
CREATE TABLE IF NOT EXISTS inventory_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
    stock_id UUID REFERENCES inventory_stock(id) ON DELETE CASCADE,
    
    -- Tipo de alerta
    alert_type VARCHAR(32) NOT NULL,  -- 'low_stock', 'out_of_stock', 'reorder_time', 'overstock', 'expiring_soon'
    severity VARCHAR(16) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    
    -- Estado
    status VARCHAR(16) DEFAULT 'open',  -- 'open', 'acknowledged', 'resolved', 'ignored'
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(128),
    resolved_at TIMESTAMPTZ,
    
    -- Datos de contexto
    current_stock INTEGER,
    reorder_point INTEGER,
    message TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_alert_type CHECK (alert_type IN ('low_stock', 'out_of_stock', 'reorder_time', 'overstock', 'expiring_soon')),
    CONSTRAINT check_severity CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT check_status CHECK (status IN ('open', 'acknowledged', 'resolved', 'ignored'))
);

-- Tabla de reordenes (pedidos automáticos)
CREATE TABLE IF NOT EXISTS inventory_reorders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
    
    -- Detalles del reorden
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10, 2),
    total_cost DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * COALESCE(unit_cost, 0)) STORED,
    
    -- Estado del reorden
    status VARCHAR(32) DEFAULT 'pending',  -- 'pending', 'sent', 'confirmed', 'received', 'cancelled'
    priority VARCHAR(16) DEFAULT 'normal',  -- 'low', 'normal', 'high', 'urgent'
    
    -- Información del proveedor
    supplier_id UUID,
    supplier_name VARCHAR(256),
    supplier_email VARCHAR(256),
    supplier_po_number VARCHAR(128),  -- Purchase Order Number
    
    -- Fechas
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    expected_delivery_date DATE,
    sent_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    received_at TIMESTAMPTZ,
    
    -- Notas y referencias
    notes TEXT,
    external_reference VARCHAR(256),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_reorder_quantity CHECK (quantity > 0),
    CONSTRAINT check_reorder_status CHECK (status IN ('pending', 'sent', 'confirmed', 'received', 'cancelled')),
    CONSTRAINT check_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

-- Tabla de proveedores (opcional, puede estar en otra tabla)
CREATE TABLE IF NOT EXISTS inventory_suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(256) NOT NULL,
    email VARCHAR(256),
    phone VARCHAR(64),
    contact_person VARCHAR(256),
    address TEXT,
    payment_terms VARCHAR(128),
    default_lead_time_days INTEGER DEFAULT 7,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de predicción de demanda (para análisis avanzado)
CREATE TABLE IF NOT EXISTS inventory_demand_forecast (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
    
    -- Predicción
    forecast_date DATE NOT NULL,
    predicted_demand INTEGER NOT NULL,
    confidence_level DECIMAL(5, 2),  -- 0-100
    
    -- Método de predicción
    forecast_method VARCHAR(64),  -- 'moving_average', 'exponential_smoothing', 'ml_model', etc.
    model_version VARCHAR(64),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(product_id, forecast_date)
);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_inventory_products_updated_at
    BEFORE UPDATE ON inventory_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_stock_updated_at
    BEFORE UPDATE ON inventory_stock
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_alerts_updated_at
    BEFORE UPDATE ON inventory_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_reorders_updated_at
    BEFORE UPDATE ON inventory_reorders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_suppliers_updated_at
    BEFORE UPDATE ON inventory_suppliers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Función para actualizar stock automáticamente al crear un movimiento
CREATE OR REPLACE FUNCTION update_stock_on_movement()
RETURNS TRIGGER AS $$
DECLARE
    qty_before INTEGER;
    qty_after INTEGER;
BEGIN
    -- Obtener o crear registro de stock
    INSERT INTO inventory_stock (product_id, quantity)
    VALUES (NEW.product_id, 0)
    ON CONFLICT (product_id) DO NOTHING;
    
    -- Obtener cantidad antes del movimiento
    SELECT quantity INTO qty_before
    FROM inventory_stock
    WHERE product_id = NEW.product_id;
    
    -- Actualizar cantidad según el movimiento
    IF NEW.direction = 'in' THEN
        qty_after := qty_before + NEW.quantity;
        UPDATE inventory_stock
        SET quantity = qty_after,
            last_restocked_at = CASE WHEN NEW.movement_type = 'purchase' THEN NOW() ELSE last_restocked_at END,
            updated_at = NOW()
        WHERE product_id = NEW.product_id;
    ELSE
        qty_after := GREATEST(0, qty_before - NEW.quantity);
        UPDATE inventory_stock
        SET quantity = qty_after,
            last_sold_at = CASE WHEN NEW.movement_type = 'sale' THEN NOW() ELSE last_sold_at END,
            updated_at = NOW()
        WHERE product_id = NEW.product_id;
    END IF;
    
    -- Guardar cantidad antes y después en el movimiento
    UPDATE inventory_movements
    SET quantity_before = qty_before,
        quantity_after = qty_after
    WHERE id = NEW.id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_stock_on_movement_trigger
    AFTER INSERT ON inventory_movements
    FOR EACH ROW
    EXECUTE FUNCTION update_stock_on_movement();

-- Comentarios para documentación
COMMENT ON TABLE inventory_products IS 'Catálogo de productos con configuración de reorden';
COMMENT ON TABLE inventory_stock IS 'Stock actual de cada producto';
COMMENT ON TABLE inventory_movements IS 'Historial completo de movimientos de inventario';
COMMENT ON TABLE inventory_alerts IS 'Alertas y notificaciones de inventario';
COMMENT ON TABLE inventory_reorders IS 'Reordenes automáticos generados';
COMMENT ON TABLE inventory_suppliers IS 'Proveedores de productos';
COMMENT ON TABLE inventory_demand_forecast IS 'Predicciones de demanda futura';

