-- ============================================================================
-- Schema para Seguimiento y Automatización de Ventas
-- Sistema automatizado para gestión de leads calificados y seguimiento de ventas
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Historial de Scores de Leads
-- ============================================================================
CREATE TABLE IF NOT EXISTS lead_score_history (
    id SERIAL PRIMARY KEY,
    lead_ext_id VARCHAR(128) NOT NULL,
    score INT NOT NULL,
    previous_score INT,
    priority VARCHAR(16) NOT NULL,
    score_change INT GENERATED ALWAYS AS (score - COALESCE(previous_score, 0)) STORED,
    scoring_factors JSONB, -- Factores que contribuyeron al score
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    calculated_by VARCHAR(64) DEFAULT 'automated_scoring', -- 'automated_scoring', 'manual', 'ml_model'
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_score_history_lead_ext_id ON lead_score_history(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_score_history_calculated_at ON lead_score_history(calculated_at);
CREATE INDEX IF NOT EXISTS idx_score_history_score ON lead_score_history(score);
CREATE INDEX IF NOT EXISTS idx_score_history_priority ON lead_score_history(priority);

-- ============================================================================
-- 2. Tabla de Leads Calificados (Sales Pipeline)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales_pipeline (
    id SERIAL PRIMARY KEY,
    lead_ext_id VARCHAR(128) NOT NULL UNIQUE,
    email VARCHAR(256) NOT NULL,
    first_name VARCHAR(128),
    last_name VARCHAR(128),
    phone VARCHAR(64),
    score INT NOT NULL,
    priority VARCHAR(16) NOT NULL,
    source VARCHAR(32),
    utm_source VARCHAR(128),
    utm_campaign VARCHAR(128),
    stage VARCHAR(32) NOT NULL DEFAULT 'qualified' CHECK (stage IN ('qualified', 'contacted', 'meeting_scheduled', 'proposal_sent', 'negotiating', 'closed_won', 'closed_lost')),
    assigned_to VARCHAR(256), -- Email del vendedor asignado
    qualified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    first_contact_at TIMESTAMPTZ,
    last_contact_at TIMESTAMPTZ,
    next_followup_at TIMESTAMPTZ,
    estimated_value DECIMAL(12,2),
    probability_pct INT DEFAULT 20 CHECK (probability_pct >= 0 AND probability_pct <= 100),
    notes TEXT,
    metadata JSONB, -- Info adicional flexible
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sales_pipeline_stage ON sales_pipeline(stage);
CREATE INDEX IF NOT EXISTS idx_sales_pipeline_assigned_to ON sales_pipeline(assigned_to);
CREATE INDEX IF NOT EXISTS idx_sales_pipeline_next_followup ON sales_pipeline(next_followup_at) 
    WHERE next_followup_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sales_pipeline_priority ON sales_pipeline(priority);
CREATE INDEX IF NOT EXISTS idx_sales_pipeline_qualified_at ON sales_pipeline(qualified_at);

-- ============================================================================
-- 3. Tabla de Tareas de Seguimiento Automatizado
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales_followup_tasks (
    id SERIAL PRIMARY KEY,
    pipeline_id INT NOT NULL,
    lead_ext_id VARCHAR(128) NOT NULL,
    task_type VARCHAR(32) NOT NULL CHECK (task_type IN ('email', 'call', 'meeting', 'proposal', 'custom')),
    task_title VARCHAR(256) NOT NULL,
    task_description TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped', 'cancelled')),
    priority VARCHAR(16) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to VARCHAR(256), -- Email del vendedor
    due_date TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    completed_by VARCHAR(256),
    metadata JSONB, -- Template usado, canal, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (pipeline_id) REFERENCES sales_pipeline(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_followup_tasks_pipeline_id ON sales_followup_tasks(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_followup_tasks_lead_ext_id ON sales_followup_tasks(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_followup_tasks_status ON sales_followup_tasks(status);
CREATE INDEX IF NOT EXISTS idx_followup_tasks_due_date ON sales_followup_tasks(due_date) 
    WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_followup_tasks_assigned_to ON sales_followup_tasks(assigned_to);

-- ============================================================================
-- 4. Tabla de Campañas Automatizadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    campaign_type VARCHAR(32) NOT NULL CHECK (campaign_type IN ('email_sequence', 'call_campaign', 'multichannel', 'nurturing')),
    trigger_criteria JSONB NOT NULL, -- Criterios para activar: {"stage": "qualified", "score_min": 50, ...}
    steps_config JSONB NOT NULL, -- Array de pasos de la campaña
    enabled BOOLEAN NOT NULL DEFAULT true,
    max_leads_per_run INT DEFAULT 50,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sales_campaigns_enabled ON sales_campaigns(enabled) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_sales_campaigns_type ON sales_campaigns(campaign_type);

-- ============================================================================
-- 5. Tabla de Ejecuciones de Campañas
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales_campaign_executions (
    id SERIAL PRIMARY KEY,
    campaign_id INT NOT NULL,
    lead_ext_id VARCHAR(128) NOT NULL,
    pipeline_id INT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'stopped')),
    current_step INT NOT NULL DEFAULT 1,
    total_steps INT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    next_action_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (campaign_id) REFERENCES sales_campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (pipeline_id) REFERENCES sales_pipeline(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE,
    UNIQUE(campaign_id, lead_ext_id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_executions_campaign_id ON sales_campaign_executions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_executions_lead_ext_id ON sales_campaign_executions(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_campaign_executions_status ON sales_campaign_executions(status);
CREATE INDEX IF NOT EXISTS idx_campaign_executions_next_action ON sales_campaign_executions(next_action_at) 
    WHERE status = 'active' AND next_action_at IS NOT NULL;

-- ============================================================================
-- 6. Tabla de Eventos de Campaña (Tracking de acciones)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sales_campaign_events (
    id SERIAL PRIMARY KEY,
    execution_id INT NOT NULL,
    lead_ext_id VARCHAR(128) NOT NULL,
    step_number INT NOT NULL,
    event_type VARCHAR(32) NOT NULL CHECK (event_type IN ('email_sent', 'email_opened', 'email_clicked', 'call_made', 'call_answered', 'meeting_scheduled', 'proposal_sent', 'custom')),
    status VARCHAR(32) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'delivered', 'completed', 'failed', 'skipped')),
    executed_at TIMESTAMPTZ,
    metadata JSONB, -- Detalles del evento: email subject, call duration, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (execution_id) REFERENCES sales_campaign_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_campaign_events_execution_id ON sales_campaign_events(execution_id);
CREATE INDEX IF NOT EXISTS idx_campaign_events_lead_ext_id ON sales_campaign_events(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_campaign_events_event_type ON sales_campaign_events(event_type);
CREATE INDEX IF NOT EXISTS idx_campaign_events_executed_at ON sales_campaign_events(executed_at) 
    WHERE executed_at IS NOT NULL;

-- ============================================================================
-- 7. Vista Materializada de Métricas de Ventas
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_sales_metrics AS
SELECT
    DATE_TRUNC('day', p.qualified_at) AS date,
    COUNT(DISTINCT p.id) AS total_qualified,
    COUNT(DISTINCT CASE WHEN p.stage = 'contacted' THEN p.id END) AS contacted,
    COUNT(DISTINCT CASE WHEN p.stage = 'meeting_scheduled' THEN p.id END) AS meetings_scheduled,
    COUNT(DISTINCT CASE WHEN p.stage = 'proposal_sent' THEN p.id END) AS proposals_sent,
    COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END) AS closed_won,
    COUNT(DISTINCT CASE WHEN p.stage = 'closed_lost' THEN p.id END) AS closed_lost,
    ROUND(
        COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT CASE WHEN p.stage IN ('closed_won', 'closed_lost') THEN p.id END), 0) * 100,
        2
    ) AS win_rate_pct,
    ROUND(AVG(p.estimated_value), 2) AS avg_deal_value,
    SUM(p.estimated_value) AS total_pipeline_value,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'completed') AS tasks_completed,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS tasks_overdue,
    COUNT(DISTINCT ce.id) FILTER (WHERE ce.event_type = 'email_sent') AS emails_sent,
    COUNT(DISTINCT ce.id) FILTER (WHERE ce.event_type = 'call_made') AS calls_made
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
LEFT JOIN sales_campaign_executions ce_exec ON p.id = ce_exec.pipeline_id
LEFT JOIN sales_campaign_events ce ON ce_exec.id = ce.execution_id
WHERE p.qualified_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', p.qualified_at)
ORDER BY date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_sales_metrics_date ON mv_sales_metrics(date);

-- ============================================================================
-- 8. Función para Calcular Score de Lead (Reusable) - Mejorada
-- ============================================================================
CREATE OR REPLACE FUNCTION calculate_lead_score(
    p_lead_ext_id VARCHAR(128),
    p_engagement_replies INT DEFAULT 0,
    p_engagement_clicks INT DEFAULT 0,
    p_engagement_opens INT DEFAULT 0,
    p_has_email BOOLEAN DEFAULT false,
    p_has_phone BOOLEAN DEFAULT false,
    p_has_name BOOLEAN DEFAULT false,
    p_source_score INT DEFAULT 0,
    p_utm_score INT DEFAULT 0,
    p_days_since_created INT DEFAULT 0,
    p_company_domain VARCHAR(256) DEFAULT NULL,
    p_website_visited BOOLEAN DEFAULT false,
    p_demo_requested BOOLEAN DEFAULT false,
    p_pricing_page_viewed BOOLEAN DEFAULT false
)
RETURNS INT AS $$
DECLARE
    v_score INT := 0;
    v_base_score INT := 20;
BEGIN
    -- Base score
    v_score := v_base_score;
    
    -- Contact info (max 20 points)
    IF p_has_email THEN
        v_score := v_score + 10;
    END IF;
    IF p_has_phone THEN
        v_score := v_score + 5;
    END IF;
    IF p_has_name THEN
        v_score := v_score + 5;
    END IF;
    
    -- Engagement (max 40 points)
    IF p_engagement_replies >= 2 THEN
        v_score := v_score + 25;
    ELSIF p_engagement_replies = 1 THEN
        v_score := v_score + 15;
    END IF;
    
    IF p_engagement_clicks >= 2 THEN
        v_score := v_score + 12;
    ELSIF p_engagement_clicks = 1 THEN
        v_score := v_score + 8;
    END IF;
    
    IF p_engagement_opens >= 4 THEN
        v_score := v_score + 15;
    ELSIF p_engagement_opens = 3 THEN
        v_score := v_score + 10;
    ELSIF p_engagement_opens >= 2 THEN
        v_score := v_score + 5;
    END IF;
    
    -- Source and UTM (max 10 points)
    v_score := v_score + LEAST(p_source_score, 5);
    v_score := v_score + LEAST(p_utm_score, 5);
    
    -- Recency bonus (max 10 points) - leads más recientes tienen bonus
    IF p_days_since_created <= 7 THEN
        v_score := v_score + 10;
    ELSIF p_days_since_created <= 30 THEN
        v_score := v_score + 5;
    END IF;
    
    -- Advanced signals (max 20 points)
    -- Company domain quality (Fortune 500, enterprise, etc.)
    IF p_company_domain IS NOT NULL THEN
        -- Bonus por dominio de empresa reconocida
        IF p_company_domain LIKE '%.edu' OR p_company_domain LIKE '%.gov' THEN
            v_score := v_score + 5;
        ELSIF LENGTH(p_company_domain) < 15 THEN
            -- Dominios cortos suelen ser empresas establecidas
            v_score := v_score + 3;
        END IF;
    END IF;
    
    -- Website engagement
    IF p_website_visited THEN
        v_score := v_score + 3;
    END IF;
    
    -- High-intent signals
    IF p_demo_requested THEN
        v_score := v_score + 10;  -- Muy alta intención
    END IF;
    
    IF p_pricing_page_viewed THEN
        v_score := v_score + 5;  -- Interés en compra
    END IF;
    
    -- Cap at 100
    RETURN LEAST(v_score, 100);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 9. Función para Auto-Asignar Leads a Vendedores (Round-robin)
-- ============================================================================
CREATE OR REPLACE FUNCTION auto_assign_sales_rep(p_lead_ext_id VARCHAR(128))
RETURNS VARCHAR(256) AS $$
DECLARE
    v_assigned_email VARCHAR(256);
    v_sales_team TEXT[] := ARRAY[
        'sales1@example.com',
        'sales2@example.com',
        'sales3@example.com'
    ]; -- Configurar con emails reales
    v_current_count INT;
BEGIN
    -- Round-robin: asignar al vendedor con menos leads asignados
    SELECT assigned_to INTO v_assigned_email
    FROM (
        SELECT 
            unnest(v_sales_team) AS email,
            COUNT(*) FILTER (WHERE status != 'closed_lost' AND status != 'closed_won') AS active_count
        FROM sales_pipeline
        WHERE assigned_to = ANY(v_sales_team)
        GROUP BY email
        ORDER BY active_count ASC, email ASC
        LIMIT 1
    ) AS team_load;
    
    -- Si no hay carga, asignar al primero
    IF v_assigned_email IS NULL THEN
        v_assigned_email := v_sales_team[1];
    END IF;
    
    RETURN v_assigned_email;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 10. Trigger para Actualizar updated_at automáticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_sales_pipeline_updated_at
    BEFORE UPDATE ON sales_pipeline
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_followup_tasks_updated_at
    BEFORE UPDATE ON sales_followup_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_campaigns_updated_at
    BEFORE UPDATE ON sales_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_campaign_executions_updated_at
    BEFORE UPDATE ON sales_campaign_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 11. Comentarios para Documentación
-- ============================================================================
COMMENT ON TABLE lead_score_history IS 
    'Historial de cambios de score de leads. Permite análisis de evolución y tendencias.';
COMMENT ON TABLE sales_pipeline IS 
    'Pipeline de ventas. Leads calificados que pasan al proceso de ventas.';
COMMENT ON TABLE sales_followup_tasks IS 
    'Tareas de seguimiento automáticas o manuales para leads en pipeline.';
COMMENT ON TABLE sales_campaigns IS 
    'Plantillas de campañas automatizadas de ventas (email, llamadas, etc.).';
COMMENT ON TABLE sales_campaign_executions IS 
    'Ejecuciones activas de campañas para leads específicos.';
COMMENT ON TABLE sales_campaign_events IS 
    'Eventos individuales dentro de ejecuciones de campañas (emails enviados, llamadas, etc.).';
COMMENT ON MATERIALIZED VIEW mv_sales_metrics IS 
    'Métricas diarias agregadas de pipeline de ventas. Refrescar periódicamente.';
COMMENT ON FUNCTION calculate_lead_score IS 
    'Calcula score de lead basado en múltiples factores (contacto, engagement, fuente, etc.).';
COMMENT ON FUNCTION auto_assign_sales_rep IS 
    'Asigna automáticamente leads a vendedores usando round-robin basado en carga.';

COMMIT;



