-- Schema para recuperación automática de carritos abandonados
-- Este schema se crea automáticamente por el DAG, pero se incluye aquí para referencia

-- Tabla principal de carritos abandonados
CREATE TABLE IF NOT EXISTS abandoned_carts (
    id SERIAL PRIMARY KEY,
    cart_id VARCHAR(255) NOT NULL UNIQUE,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    items JSONB NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    abandoned_at TIMESTAMP WITH TIME ZONE,
    recovered_at TIMESTAMP WITH TIME ZONE,
    reminder_sent_at TIMESTAMP WITH TIME ZONE,
    discount_sent_at TIMESTAMP WITH TIME ZONE,
    discount_code VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    conversion_status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_date DATE GENERATED ALWAYS AS (created_at::DATE) STORED
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_abandoned_carts_email 
ON abandoned_carts(customer_email);

CREATE INDEX IF NOT EXISTS idx_abandoned_carts_created_at 
ON abandoned_carts(created_at);

CREATE INDEX IF NOT EXISTS idx_abandoned_carts_status 
ON abandoned_carts(status);

CREATE INDEX IF NOT EXISTS idx_abandoned_carts_abandoned_at 
ON abandoned_carts(abandoned_at) WHERE abandoned_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_abandoned_carts_reminder_sent_at 
ON abandoned_carts(reminder_sent_at) WHERE reminder_sent_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_abandoned_carts_discount_sent_at 
ON abandoned_carts(discount_sent_at) WHERE discount_sent_at IS NOT NULL;

-- Tabla de tracking de emails enviados
CREATE TABLE IF NOT EXISTS abandoned_cart_emails (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES abandoned_carts(id) ON DELETE CASCADE,
    email_type VARCHAR(50) NOT NULL, -- 'reminder' o 'discount'
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    converted BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_cart_emails_cart_id 
ON abandoned_cart_emails(cart_id);

CREATE INDEX IF NOT EXISTS idx_cart_emails_type 
ON abandoned_cart_emails(email_type);

CREATE INDEX IF NOT EXISTS idx_cart_emails_sent_at 
ON abandoned_cart_emails(sent_at);

-- Tabla de códigos de descuento generados
CREATE TABLE IF NOT EXISTS cart_discount_codes (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES abandoned_carts(id) ON DELETE CASCADE,
    discount_code VARCHAR(50) NOT NULL UNIQUE,
    discount_percentage INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_discount_codes_code 
ON cart_discount_codes(discount_code);

CREATE INDEX IF NOT EXISTS idx_discount_codes_cart_id 
ON cart_discount_codes(cart_id);

CREATE INDEX IF NOT EXISTS idx_discount_codes_active 
ON cart_discount_codes(is_active) WHERE is_active = TRUE;

-- Vista para análisis de conversión
CREATE OR REPLACE VIEW abandoned_cart_analytics AS
SELECT 
    DATE_TRUNC('day', c.created_at) as date,
    COUNT(*) as total_carts,
    COUNT(CASE WHEN c.reminder_sent_at IS NOT NULL THEN 1 END) as reminders_sent,
    COUNT(CASE WHEN c.discount_sent_at IS NOT NULL THEN 1 END) as discounts_sent,
    COUNT(CASE WHEN c.recovered_at IS NOT NULL THEN 1 END) as recovered_carts,
    SUM(c.total_amount) as total_value,
    SUM(CASE WHEN c.recovered_at IS NOT NULL THEN c.total_amount ELSE 0 END) as recovered_value,
    ROUND(
        COUNT(CASE WHEN c.recovered_at IS NOT NULL THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as recovery_rate
FROM abandoned_carts c
GROUP BY DATE_TRUNC('day', c.created_at)
ORDER BY date DESC;

-- Función para registrar un carrito abandonado
CREATE OR REPLACE FUNCTION register_abandoned_cart(
    p_cart_id VARCHAR(255),
    p_customer_email VARCHAR(255),
    p_customer_name VARCHAR(255),
    p_items JSONB,
    p_total_amount DECIMAL(10, 2),
    p_currency VARCHAR(10) DEFAULT 'USD',
    p_metadata JSONB DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_cart_id INTEGER;
BEGIN
    INSERT INTO abandoned_carts (
        cart_id,
        customer_email,
        customer_name,
        items,
        total_amount,
        currency,
        created_at,
        updated_at,
        abandoned_at,
        status,
        metadata
    ) VALUES (
        p_cart_id,
        p_customer_email,
        p_customer_name,
        p_items,
        p_total_amount,
        p_currency,
        NOW(),
        NOW(),
        NOW(),
        'pending',
        p_metadata
    )
    ON CONFLICT (cart_id) 
    DO UPDATE SET
        items = EXCLUDED.items,
        total_amount = EXCLUDED.total_amount,
        updated_at = NOW(),
        metadata = EXCLUDED.metadata
    RETURNING id INTO v_cart_id;
    
    RETURN v_cart_id;
END;
$$ LANGUAGE plpgsql;

-- Función para marcar un carrito como recuperado
CREATE OR REPLACE FUNCTION mark_cart_recovered(
    p_cart_id VARCHAR(255)
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE abandoned_carts
    SET recovered_at = NOW(),
        status = 'recovered',
        conversion_status = 'converted',
        updated_at = NOW()
    WHERE cart_id = p_cart_id
        AND recovered_at IS NULL;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar si un código de descuento es válido
CREATE OR REPLACE FUNCTION validate_discount_code(
    p_code VARCHAR(50)
) RETURNS TABLE (
    is_valid BOOLEAN,
    discount_percentage INTEGER,
    cart_id VARCHAR(255),
    expires_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (cdc.is_active = TRUE 
         AND cdc.used_at IS NULL 
         AND (cdc.expires_at IS NULL OR cdc.expires_at > NOW())) as is_valid,
        cdc.discount_percentage,
        ac.cart_id,
        cdc.expires_at
    FROM cart_discount_codes cdc
    JOIN abandoned_carts ac ON cdc.cart_id = ac.id
    WHERE cdc.discount_code = p_code;
END;
$$ LANGUAGE plpgsql;

-- Función para marcar un código de descuento como usado
CREATE OR REPLACE FUNCTION mark_discount_code_used(
    p_code VARCHAR(50)
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE cart_discount_codes
    SET used_at = NOW(),
        is_active = FALSE
    WHERE discount_code = p_code
        AND used_at IS NULL
        AND is_active = TRUE
        AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Comentarios
COMMENT ON TABLE abandoned_carts IS 'Carritos abandonados detectados en el sistema';
COMMENT ON TABLE abandoned_cart_emails IS 'Tracking de emails enviados para recuperación de carritos';
COMMENT ON TABLE cart_discount_codes IS 'Códigos de descuento generados automáticamente para carritos abandonados';
COMMENT ON VIEW abandoned_cart_analytics IS 'Vista analítica para métricas de recuperación de carritos';














