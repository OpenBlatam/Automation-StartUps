-- ============================================================================
-- Esquema de E-commerce: Pedidos y Rastreo
-- ============================================================================
-- Sistema completo para gestión de pedidos de e-commerce con tracking en tiempo real
-- Ideal para automatizar el 70% de consultas de entrega

-- Tabla principal de pedidos
CREATE TABLE IF NOT EXISTS ecommerce_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(128) UNIQUE NOT NULL,  -- ID público del pedido (ej: ORD-2024-001234)
    customer_id UUID,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(64),
    
    -- Estado del pedido
    status VARCHAR(32) DEFAULT 'pending',  -- 'pending', 'confirmed', 'processing', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled', 'refunded'
    payment_status VARCHAR(32) DEFAULT 'pending',  -- 'pending', 'paid', 'failed', 'refunded', 'partially_refunded'
    
    -- Información de pago
    payment_method VARCHAR(64),  -- 'credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash_on_delivery'
    payment_transaction_id VARCHAR(255),
    payment_date TIMESTAMPTZ,
    total_amount DECIMAL(12, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(12, 2) DEFAULT 0,
    shipping_amount DECIMAL(12, 2) DEFAULT 0,
    discount_amount DECIMAL(12, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Información de envío
    shipping_method VARCHAR(64),  -- 'standard', 'express', 'overnight', 'pickup'
    shipping_carrier VARCHAR(64),  -- 'fedex', 'ups', 'dhl', 'usps', 'custom'
    tracking_number VARCHAR(128),
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- Direcciones
    shipping_address JSONB NOT NULL,  -- {street, city, state, zip, country}
    billing_address JSONB,
    
    -- Items del pedido
    items JSONB NOT NULL,  -- [{product_id, name, sku, quantity, price, total}]
    
    -- Notas y referencias
    notes TEXT,
    internal_notes TEXT,  -- Notas internas no visibles al cliente
    external_reference VARCHAR(256),  -- Referencia externa (ej: Shopify order ID)
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    cancelled_at TIMESTAMPTZ,
    cancelled_reason TEXT,
    
    CONSTRAINT check_order_status CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled', 'refunded')),
    CONSTRAINT check_payment_status CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_refunded'))
);

-- Tabla de tracking de eventos del pedido
CREATE TABLE IF NOT EXISTS ecommerce_order_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES ecommerce_orders(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL,
    location VARCHAR(255),  -- Ubicación actual del paquete
    carrier_status VARCHAR(128),  -- Estado del carrier (ej: "In Transit", "Out for Delivery")
    carrier_message TEXT,  -- Mensaje del carrier
    estimated_delivery_date DATE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,  -- Información adicional del carrier
    
    CONSTRAINT check_tracking_status CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled', 'refunded'))
);

-- Tabla de actualizaciones de pago
CREATE TABLE IF NOT EXISTS ecommerce_payment_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES ecommerce_orders(id) ON DELETE CASCADE,
    payment_status VARCHAR(32) NOT NULL,
    amount DECIMAL(12, 2),
    transaction_id VARCHAR(255),
    payment_method VARCHAR(64),
    notes TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    
    CONSTRAINT check_payment_update_status CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_refunded'))
);

-- Tabla de consultas del chatbot
CREATE TABLE IF NOT EXISTS ecommerce_chatbot_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES ecommerce_orders(id) ON DELETE SET NULL,
    customer_email VARCHAR(255),
    query_text TEXT NOT NULL,
    intent VARCHAR(64),  -- 'track_order', 'payment_status', 'delivery_date', 'cancel_order', 'refund', 'other'
    response_text TEXT,
    confidence FLOAT,
    resolved BOOLEAN DEFAULT FALSE,
    escalated BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Tabla de conversaciones del chatbot
CREATE TABLE IF NOT EXISTS ecommerce_chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(128) UNIQUE NOT NULL,
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    order_id UUID REFERENCES ecommerce_orders(id) ON DELETE SET NULL,
    status VARCHAR(32) DEFAULT 'active',  -- 'active', 'resolved', 'escalated', 'closed'
    started_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    escalated_at TIMESTAMPTZ,
    escalated_to VARCHAR(255),  -- ID del agente humano
    metadata JSONB
);

-- Tabla de mensajes de conversación
CREATE TABLE IF NOT EXISTS ecommerce_chatbot_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ecommerce_chatbot_conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(16) NOT NULL,  -- 'user', 'bot', 'agent'
    message_text TEXT NOT NULL,
    intent VARCHAR(64),
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    
    CONSTRAINT check_message_type CHECK (message_type IN ('user', 'bot', 'agent'))
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_order_id ON ecommerce_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_customer_email ON ecommerce_orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_status ON ecommerce_orders(status);
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_payment_status ON ecommerce_orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_tracking_number ON ecommerce_orders(tracking_number) WHERE tracking_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_created_at ON ecommerce_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_ecommerce_orders_estimated_delivery ON ecommerce_orders(estimated_delivery_date) WHERE estimated_delivery_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ecommerce_order_tracking_order_id ON ecommerce_order_tracking(order_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_order_tracking_timestamp ON ecommerce_order_tracking(timestamp);
CREATE INDEX IF NOT EXISTS idx_ecommerce_order_tracking_status ON ecommerce_order_tracking(status);

CREATE INDEX IF NOT EXISTS idx_ecommerce_payment_updates_order_id ON ecommerce_payment_updates(order_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_payment_updates_timestamp ON ecommerce_payment_updates(timestamp);

CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_queries_order_id ON ecommerce_chatbot_queries(order_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_queries_customer_email ON ecommerce_chatbot_queries(customer_email);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_queries_intent ON ecommerce_chatbot_queries(intent);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_queries_created_at ON ecommerce_chatbot_queries(created_at);

CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_conversations_conversation_id ON ecommerce_chatbot_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_conversations_customer_email ON ecommerce_chatbot_conversations(customer_email);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_conversations_order_id ON ecommerce_chatbot_conversations(order_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_conversations_status ON ecommerce_chatbot_conversations(status);

CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_messages_conversation_id ON ecommerce_chatbot_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ecommerce_chatbot_messages_created_at ON ecommerce_chatbot_messages(created_at);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_ecommerce_orders_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ecommerce_orders_updated_at
    BEFORE UPDATE ON ecommerce_orders
    FOR EACH ROW
    EXECUTE FUNCTION update_ecommerce_orders_updated_at();

-- Vista para tracking completo del pedido
CREATE OR REPLACE VIEW ecommerce_order_tracking_view AS
SELECT 
    o.id,
    o.order_id,
    o.customer_email,
    o.customer_name,
    o.status,
    o.payment_status,
    o.tracking_number,
    o.shipping_carrier,
    o.shipping_method,
    o.estimated_delivery_date,
    o.actual_delivery_date,
    o.total_amount,
    o.currency,
    o.created_at,
    o.updated_at,
    (
        SELECT json_agg(
            json_build_object(
                'status', t.status,
                'location', t.location,
                'carrier_status', t.carrier_status,
                'carrier_message', t.carrier_message,
                'timestamp', t.timestamp,
                'metadata', t.metadata
            ) ORDER BY t.timestamp DESC
        )
        FROM ecommerce_order_tracking t
        WHERE t.order_id = o.id
    ) as tracking_history,
    (
        SELECT json_agg(
            json_build_object(
                'payment_status', p.payment_status,
                'amount', p.amount,
                'transaction_id', p.transaction_id,
                'timestamp', p.timestamp
            ) ORDER BY p.timestamp DESC
        )
        FROM ecommerce_payment_updates p
        WHERE p.order_id = o.id
    ) as payment_history
FROM ecommerce_orders o;

-- Función para obtener el estado actual del pedido
CREATE OR REPLACE FUNCTION get_order_status(order_id_param VARCHAR)
RETURNS TABLE (
    order_id VARCHAR,
    status VARCHAR,
    payment_status VARCHAR,
    tracking_number VARCHAR,
    estimated_delivery_date DATE,
    last_update TIMESTAMPTZ,
    tracking_history JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.order_id,
        o.status,
        o.payment_status,
        o.tracking_number,
        o.estimated_delivery_date,
        o.updated_at,
        (
            SELECT json_agg(
                json_build_object(
                    'status', t.status,
                    'location', t.location,
                    'carrier_status', t.carrier_status,
                    'carrier_message', t.carrier_message,
                    'timestamp', t.timestamp
                ) ORDER BY t.timestamp DESC
            )
            FROM ecommerce_order_tracking t
            WHERE t.order_id = o.id
        ) as tracking_history
    FROM ecommerce_orders o
    WHERE o.order_id = order_id_param;
END;
$$ LANGUAGE plpgsql;

-- Comentarios
COMMENT ON TABLE ecommerce_orders IS 'Pedidos de e-commerce con información completa de tracking';
COMMENT ON TABLE ecommerce_order_tracking IS 'Historial de eventos de tracking de pedidos';
COMMENT ON TABLE ecommerce_payment_updates IS 'Historial de actualizaciones de pago';
COMMENT ON TABLE ecommerce_chatbot_queries IS 'Consultas realizadas al chatbot de rastreo';
COMMENT ON TABLE ecommerce_chatbot_conversations IS 'Conversaciones del chatbot de rastreo';
COMMENT ON TABLE ecommerce_chatbot_messages IS 'Mensajes individuales de las conversaciones';



