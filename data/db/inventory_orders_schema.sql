-- ============================================================================
-- Esquema Adicional: Órdenes de Compra y Aprobaciones
-- ============================================================================
-- Extensión del sistema de inventario para gestión de órdenes de compra

-- Tabla de órdenes de compra (purchase orders)
CREATE TABLE IF NOT EXISTS inventory_purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_number VARCHAR(128) UNIQUE NOT NULL,
    
    -- Estado y prioridad
    status VARCHAR(32) DEFAULT 'draft',  -- 'draft', 'pending_approval', 'approved', 'sent', 'received', 'cancelled'
    priority VARCHAR(16) DEFAULT 'normal',
    
    -- Información del proveedor
    supplier_id UUID REFERENCES inventory_suppliers(id),
    supplier_name VARCHAR(256) NOT NULL,
    supplier_email VARCHAR(256),
    supplier_contact VARCHAR(256),
    
    -- Totales
    subtotal DECIMAL(12, 2) DEFAULT 0,
    tax DECIMAL(12, 2) DEFAULT 0,
    shipping DECIMAL(12, 2) DEFAULT 0,
    total DECIMAL(12, 2) GENERATED ALWAYS AS (subtotal + tax + shipping) STORED,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Fechas
    requested_date DATE,
    expected_delivery_date DATE,
    sent_date DATE,
    received_date DATE,
    
    -- Aprobación
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    approval_notes TEXT,
    
    -- Notas y referencias
    notes TEXT,
    external_reference VARCHAR(256),
    
    -- Metadata
    created_by VARCHAR(128),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_po_status CHECK (status IN ('draft', 'pending_approval', 'approved', 'sent', 'received', 'cancelled')),
    CONSTRAINT check_po_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

-- Tabla de líneas de orden de compra
CREATE TABLE IF NOT EXISTS inventory_po_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_id UUID NOT NULL REFERENCES inventory_purchase_orders(id) ON DELETE CASCADE,
    reorder_id UUID REFERENCES inventory_reorders(id),
    
    -- Producto
    product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
    sku VARCHAR(128),
    product_name VARCHAR(512),
    
    -- Cantidad y precio
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    
    -- Estado de recepción
    quantity_received INTEGER DEFAULT 0,
    received_at TIMESTAMPTZ,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_po_line_quantity CHECK (quantity > 0),
    CONSTRAINT check_po_line_received CHECK (quantity_received <= quantity)
);

-- Tabla de aprobaciones de reordenes
CREATE TABLE IF NOT EXISTS inventory_reorder_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reorder_id UUID NOT NULL REFERENCES inventory_reorders(id) ON DELETE CASCADE,
    
    -- Estado de aprobación
    status VARCHAR(32) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'cancelled'
    
    -- Aprobador
    approver_id VARCHAR(128),
    approver_name VARCHAR(256),
    approver_email VARCHAR(256),
    
    -- Fechas
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    
    -- Notas
    approval_notes TEXT,
    rejection_reason TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT check_approval_status CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled'))
);

-- Trigger para actualizar updated_at
CREATE TRIGGER update_inventory_po_updated_at
    BEFORE UPDATE ON inventory_purchase_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_po_lines_updated_at
    BEFORE UPDATE ON inventory_po_lines
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_reorder_approvals_updated_at
    BEFORE UPDATE ON inventory_reorder_approvals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Función para generar número de PO automáticamente
CREATE OR REPLACE FUNCTION generate_po_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.po_number IS NULL OR NEW.po_number = '' THEN
        NEW.po_number := 'PO-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || 
                         LPAD(NEXTVAL('po_sequence')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear secuencia para números de PO
CREATE SEQUENCE IF NOT EXISTS po_sequence START 1;

CREATE TRIGGER generate_po_number_trigger
    BEFORE INSERT ON inventory_purchase_orders
    FOR EACH ROW
    EXECUTE FUNCTION generate_po_number();

-- Índices
CREATE INDEX IF NOT EXISTS idx_inventory_po_status ON inventory_purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_inventory_po_supplier ON inventory_purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_inventory_po_created ON inventory_purchase_orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_po_approval ON inventory_purchase_orders(requires_approval, status) WHERE requires_approval = TRUE;
CREATE INDEX IF NOT EXISTS idx_inventory_po_lines_po ON inventory_po_lines(po_id);
CREATE INDEX IF NOT EXISTS idx_inventory_po_lines_product ON inventory_po_lines(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_reorder_approvals_reorder ON inventory_reorder_approvals(reorder_id);
CREATE INDEX IF NOT EXISTS idx_inventory_reorder_approvals_status ON inventory_reorder_approvals(status);

-- Comentarios
COMMENT ON TABLE inventory_purchase_orders IS 'Órdenes de compra a proveedores';
COMMENT ON TABLE inventory_po_lines IS 'Líneas de productos en órdenes de compra';
COMMENT ON TABLE inventory_reorder_approvals IS 'Aprobaciones de reordenes automáticos';

