-- ============================================================================
-- SCHEMA: Sistema de SLA Dinámicos para Tickets de Soporte
-- ============================================================================
-- Permite configurar SLAs personalizados por:
-- - Tipo de cliente (VIP, Enterprise, Standard)
-- - Categoría de ticket
-- - Prioridad
-- - Horario (horario laboral vs. fuera de horario)
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Configuración de SLAs
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_sla_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(256) NOT NULL,
    priority_order INT NOT NULL,
    
    -- Condiciones
    customer_tier VARCHAR(32), -- vip, enterprise, standard, null (todos)
    category VARCHAR(64),
    priority VARCHAR(16),
    tags TEXT[],
    
    -- SLAs
    first_response_minutes INT NOT NULL,
    resolution_minutes INT NOT NULL,
    
    -- Horario
    business_hours_only BOOLEAN DEFAULT false,
    timezone VARCHAR(64) DEFAULT 'UTC',
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Tabla de Tracking de SLA
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_sla_tracking (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(128) NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
    sla_rule_id INT REFERENCES support_sla_rules(id),
    
    -- SLAs aplicados
    first_response_sla_minutes INT,
    resolution_sla_minutes INT,
    
    -- Tiempos reales
    first_response_at TIMESTAMPTZ,
    resolution_at TIMESTAMPTZ,
    
    -- Compliance
    first_response_met BOOLEAN,
    resolution_met BOOLEAN,
    
    -- Breaches
    first_response_breach_minutes INT,
    resolution_breach_minutes INT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- ÍNDICES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_sla_rules_active ON support_sla_rules(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_sla_rules_priority ON support_sla_rules(priority_order);
CREATE INDEX IF NOT EXISTS idx_sla_tracking_ticket ON support_sla_tracking(ticket_id);
CREATE INDEX IF NOT EXISTS idx_sla_tracking_breach ON support_sla_tracking(first_response_met, resolution_met);

-- ============================================================================
-- VISTA: SLA Compliance por Regla
-- ============================================================================
CREATE OR REPLACE VIEW v_support_sla_compliance AS
SELECT 
    r.rule_name,
    r.priority_order,
    COUNT(t.id) as total_tickets,
    COUNT(*) FILTER (WHERE t.first_response_met = true) as first_response_met_count,
    COUNT(*) FILTER (WHERE t.resolution_met = true) as resolution_met_count,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE t.first_response_met = true) / 
        NULLIF(COUNT(t.id), 0),
        2
    ) as first_response_compliance_pct,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE t.resolution_met = true) / 
        NULLIF(COUNT(t.id), 0),
        2
    ) as resolution_compliance_pct,
    AVG(t.first_response_breach_minutes) FILTER (WHERE t.first_response_met = false) as avg_breach_minutes
FROM support_sla_rules r
LEFT JOIN support_sla_tracking t ON r.id = t.sla_rule_id
WHERE r.is_active = true
GROUP BY r.id, r.rule_name, r.priority_order
ORDER BY r.priority_order;

-- ============================================================================
-- FUNCIÓN: Calcular SLA para un ticket
-- ============================================================================
CREATE OR REPLACE FUNCTION calculate_ticket_sla(
    p_ticket_id VARCHAR(128),
    p_customer_tier VARCHAR(32),
    p_category VARCHAR(64),
    p_priority VARCHAR(16),
    p_tags TEXT[]
) RETURNS INT AS $$
DECLARE
    v_sla_rule_id INT;
    v_first_response_minutes INT;
    v_resolution_minutes INT;
BEGIN
    -- Buscar regla de SLA que aplique (en orden de prioridad)
    SELECT id, first_response_minutes, resolution_minutes
    INTO v_sla_rule_id, v_first_response_minutes, v_resolution_minutes
    FROM support_sla_rules
    WHERE is_active = true
    AND (
        customer_tier IS NULL OR customer_tier = p_customer_tier
    )
    AND (
        category IS NULL OR category = p_category
    )
    AND (
        priority IS NULL OR priority = p_priority
    )
    AND (
        tags IS NULL OR tags && p_tags
    )
    ORDER BY priority_order ASC
    LIMIT 1;
    
    -- Si no hay regla específica, usar defaults
    IF v_sla_rule_id IS NULL THEN
        -- Defaults basados en prioridad
        CASE p_priority
            WHEN 'critical' THEN
                v_first_response_minutes := 15;
                v_resolution_minutes := 60;
            WHEN 'urgent' THEN
                v_first_response_minutes := 30;
                v_resolution_minutes := 240;
            WHEN 'high' THEN
                v_first_response_minutes := 120;
                v_resolution_minutes := 480;
            WHEN 'medium' THEN
                v_first_response_minutes := 240;
                v_resolution_minutes := 1440;
            ELSE
                v_first_response_minutes := 480;
                v_resolution_minutes := 2880;
        END CASE;
    END IF;
    
    -- Guardar tracking
    INSERT INTO support_sla_tracking (
        ticket_id,
        sla_rule_id,
        first_response_sla_minutes,
        resolution_sla_minutes
    ) VALUES (
        p_ticket_id,
        v_sla_rule_id,
        v_first_response_minutes,
        v_resolution_minutes
    )
    ON CONFLICT DO NOTHING;
    
    RETURN v_first_response_minutes;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================================================
-- SLAs de Ejemplo
-- ============================================================================
INSERT INTO support_sla_rules (
    rule_name,
    priority_order,
    customer_tier,
    category,
    priority,
    first_response_minutes,
    resolution_minutes,
    business_hours_only,
    is_active
) VALUES
    -- VIP Critical: 5 minutos primera respuesta, 30 minutos resolución
    ('VIP Critical', 1, 'vip', NULL, 'critical', 5, 30, false, true),
    
    -- VIP Urgent: 15 minutos primera respuesta, 2 horas resolución
    ('VIP Urgent', 2, 'vip', NULL, 'urgent', 15, 120, false, true),
    
    -- Enterprise Critical: 15 minutos primera respuesta, 1 hora resolución
    ('Enterprise Critical', 3, 'enterprise', NULL, 'critical', 15, 60, false, true),
    
    -- Critical General: 30 minutos primera respuesta, 2 horas resolución
    ('Critical General', 10, NULL, NULL, 'critical', 30, 120, false, true),
    
    -- Billing Issues: 1 hora primera respuesta, 4 horas resolución
    ('Billing Issues', 20, NULL, 'billing', NULL, 60, 240, false, true),
    
    -- Business Hours Only: Standard tickets en horario laboral
    ('Business Hours Standard', 30, NULL, NULL, 'medium', 240, 1440, true, true)
ON CONFLICT DO NOTHING;

