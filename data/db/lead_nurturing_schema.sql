-- ============================================================================
-- Schema para Secuencias de Nutrición de Leads (Lead Nurturing)
-- Sistema automatizado para aumentar conversión de leads fríos a calificados
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Templates de Secuencias
-- ============================================================================
CREATE TABLE IF NOT EXISTS nurturing_sequence_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    priority_filter VARCHAR(16) DEFAULT 'low', -- low, medium, high, all
    min_score INT DEFAULT 0,
    max_score INT DEFAULT 49,
    total_steps INT NOT NULL CHECK (total_steps > 0),
    steps_config JSONB NOT NULL, -- Array de pasos: [{step, delay_days, subject, body, ...}]
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_nurturing_templates_priority ON nurturing_sequence_templates(priority_filter);
CREATE INDEX IF NOT EXISTS idx_nurturing_templates_enabled ON nurturing_sequence_templates(enabled) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_nurturing_templates_score_range ON nurturing_sequence_templates(min_score, max_score);

-- ============================================================================
-- 2. Tabla de Secuencias Activas
-- ============================================================================
CREATE TABLE IF NOT EXISTS lead_nurturing_sequences (
    id SERIAL PRIMARY KEY,
    lead_ext_id VARCHAR(128) NOT NULL,
    email VARCHAR(256) NOT NULL,
    sequence_name VARCHAR(128) NOT NULL,
    current_step INT NOT NULL DEFAULT 1 CHECK (current_step > 0),
    total_steps INT NOT NULL CHECK (total_steps > 0),
    status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'stopped', 'qualified')),
    lead_score INT NOT NULL DEFAULT 0,
    lead_priority VARCHAR(16) NOT NULL DEFAULT 'low',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ,
    next_send_at TIMESTAMPTZ,
    qualified_at TIMESTAMPTZ,
    paused_at TIMESTAMPTZ,
    paused_reason TEXT,
    completion_rate NUMERIC(5,2), -- % de pasos completados
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE,
    UNIQUE(lead_ext_id, sequence_name)
);

CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_lead_ext_id ON lead_nurturing_sequences(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_status ON lead_nurturing_sequences(status);
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_next_send_at ON lead_nurturing_sequences(next_send_at) 
    WHERE status = 'active' AND next_send_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_qualified_at ON lead_nurturing_sequences(qualified_at) 
    WHERE qualified_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_active ON lead_nurturing_sequences(status, next_send_at) 
    WHERE status = 'active';

-- ============================================================================
-- 3. Tabla de Eventos de Secuencia (Emails, SMS, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS lead_nurturing_events (
    id SERIAL PRIMARY KEY,
    sequence_id INT NOT NULL,
    lead_ext_id VARCHAR(128) NOT NULL,
    email VARCHAR(256) NOT NULL,
    step_number INT NOT NULL CHECK (step_number > 0),
    step_type VARCHAR(32) NOT NULL DEFAULT 'email', -- email, sms, linkedin, etc.
    subject VARCHAR(512),
    body_preview TEXT, -- Primeros 500 chars del body
    status VARCHAR(32) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'delivered', 'opened', 'clicked', 'replied', 'bounced', 'failed', 'skipped')),
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    bounced_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    metadata JSONB, -- Info adicional: webhook_response, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (sequence_id) REFERENCES lead_nurturing_sequences(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_ext_id) REFERENCES leads(ext_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_nurturing_events_sequence_id ON lead_nurturing_events(sequence_id);
CREATE INDEX IF NOT EXISTS idx_nurturing_events_lead_ext_id ON lead_nurturing_events(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_nurturing_events_status ON lead_nurturing_events(status);
CREATE INDEX IF NOT EXISTS idx_nurturing_events_sent_at ON lead_nurturing_events(sent_at) 
    WHERE sent_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nurturing_events_engagement ON lead_nurturing_events(opened_at, clicked_at, replied_at) 
    WHERE opened_at IS NOT NULL OR clicked_at IS NOT NULL OR replied_at IS NOT NULL;

-- ============================================================================
-- 4. Tabla de Engagement Agregado (para análisis rápido)
-- ============================================================================
CREATE TABLE IF NOT EXISTS lead_nurturing_engagement_summary (
    sequence_id INT PRIMARY KEY,
    lead_ext_id VARCHAR(128) NOT NULL,
    total_emails_sent INT DEFAULT 0,
    total_emails_opened INT DEFAULT 0,
    total_emails_clicked INT DEFAULT 0,
    total_emails_replied INT DEFAULT 0,
    first_open_at TIMESTAMPTZ,
    last_open_at TIMESTAMPTZ,
    first_reply_at TIMESTAMPTZ,
    open_rate NUMERIC(5,2), -- %
    click_rate NUMERIC(5,2), -- %
    reply_rate NUMERIC(5,2), -- %
    engagement_score INT DEFAULT 0, -- Score calculado basado en engagement
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (sequence_id) REFERENCES lead_nurturing_sequences(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_nurturing_engagement_summary_lead ON lead_nurturing_engagement_summary(lead_ext_id);

-- ============================================================================
-- 5. Vista Materializada de Métricas de Conversión
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_nurturing_conversion_metrics AS
SELECT
    DATE_TRUNC('day', s.started_at) AS date,
    COUNT(DISTINCT s.id) AS total_sequences_started,
    COUNT(DISTINCT CASE WHEN s.status = 'completed' THEN s.id END) AS sequences_completed,
    COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) AS leads_qualified,
    COUNT(DISTINCT CASE WHEN s.status = 'active' THEN s.id END) AS sequences_active,
    COUNT(DISTINCT e.id) AS total_emails_sent,
    COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) AS emails_opened,
    COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) AS emails_clicked,
    COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) AS emails_replied,
    ROUND(
        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT s.id), 0) * 100, 
        2
    ) AS conversion_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
        2
    ) AS open_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
        2
    ) AS click_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
        2
    ) AS reply_rate_pct,
    AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) AS avg_days_to_qualify
FROM lead_nurturing_sequences s
LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
WHERE s.started_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', s.started_at)
ORDER BY date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_nurturing_conversion_date ON mv_nurturing_conversion_metrics(date);

-- ============================================================================
-- 6. Función para Actualizar Engagement Summary
-- ============================================================================
CREATE OR REPLACE FUNCTION update_nurturing_engagement_summary(seq_id INT)
RETURNS void AS $$
BEGIN
    INSERT INTO lead_nurturing_engagement_summary (
        sequence_id, lead_ext_id,
        total_emails_sent, total_emails_opened, total_emails_clicked, total_emails_replied,
        first_open_at, last_open_at, first_reply_at,
        open_rate, click_rate, reply_rate, engagement_score, updated_at
    )
    SELECT 
        s.id AS sequence_id,
        s.lead_ext_id,
        COUNT(*) FILTER (WHERE e.status IN ('sent', 'delivered', 'opened', 'clicked', 'replied')) AS total_emails_sent,
        COUNT(*) FILTER (WHERE e.opened_at IS NOT NULL) AS total_emails_opened,
        COUNT(*) FILTER (WHERE e.clicked_at IS NOT NULL) AS total_emails_clicked,
        COUNT(*) FILTER (WHERE e.replied_at IS NOT NULL) AS total_emails_replied,
        MIN(e.opened_at) AS first_open_at,
        MAX(e.opened_at) AS last_open_at,
        MIN(e.replied_at) AS first_reply_at,
        ROUND(
            COUNT(*) FILTER (WHERE e.opened_at IS NOT NULL)::NUMERIC / 
            NULLIF(COUNT(*) FILTER (WHERE e.status IN ('sent', 'delivered', 'opened', 'clicked', 'replied')), 0) * 100,
            2
        ) AS open_rate,
        ROUND(
            COUNT(*) FILTER (WHERE e.clicked_at IS NOT NULL)::NUMERIC / 
            NULLIF(COUNT(*) FILTER (WHERE e.status IN ('sent', 'delivered', 'opened', 'clicked', 'replied')), 0) * 100,
            2
        ) AS click_rate,
        ROUND(
            COUNT(*) FILTER (WHERE e.replied_at IS NOT NULL)::NUMERIC / 
            NULLIF(COUNT(*) FILTER (WHERE e.status IN ('sent', 'delivered', 'opened', 'clicked', 'replied')), 0) * 100,
            2
        ) AS reply_rate,
        -- Engagement score: replies (15pts) + clicks (8pts) + opens (5pts), cap at 100
        LEAST(
            (COUNT(*) FILTER (WHERE e.replied_at IS NOT NULL) * 15) +
            (COUNT(*) FILTER (WHERE e.clicked_at IS NOT NULL) * 8) +
            (COUNT(*) FILTER (WHERE e.opened_at IS NOT NULL) * 5),
            100
        ) AS engagement_score,
        NOW() AS updated_at
    FROM lead_nurturing_sequences s
    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
    WHERE s.id = seq_id
    GROUP BY s.id, s.lead_ext_id
    ON CONFLICT (sequence_id) DO UPDATE SET
        total_emails_sent = EXCLUDED.total_emails_sent,
        total_emails_opened = EXCLUDED.total_emails_opened,
        total_emails_clicked = EXCLUDED.total_emails_clicked,
        total_emails_replied = EXCLUDED.total_emails_replied,
        first_open_at = EXCLUDED.first_open_at,
        last_open_at = EXCLUDED.last_open_at,
        first_reply_at = EXCLUDED.first_reply_at,
        open_rate = EXCLUDED.open_rate,
        click_rate = EXCLUDED.click_rate,
        reply_rate = EXCLUDED.reply_rate,
        engagement_score = EXCLUDED.engagement_score,
        updated_at = EXCLUDED.updated_at;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 7. Comentarios para Documentación
-- ============================================================================
COMMENT ON TABLE nurturing_sequence_templates IS 
    'Templates reutilizables de secuencias de nutrición. Define pasos, timing y contenido.';
COMMENT ON TABLE lead_nurturing_sequences IS 
    'Secuencias activas de nutrición. Rastrea progreso de cada lead a través de su secuencia.';
COMMENT ON TABLE lead_nurturing_events IS 
    'Eventos individuales (emails, SMS, etc.) enviados dentro de cada secuencia. Tracking completo de engagement.';
COMMENT ON TABLE lead_nurturing_engagement_summary IS 
    'Resumen agregado de engagement por secuencia. Optimizado para queries rápidas.';
COMMENT ON MATERIALIZED VIEW mv_nurturing_conversion_metrics IS 
    'Métricas diarias agregadas de conversión de leads fríos a calificados. Refrescar periódicamente.';
COMMENT ON FUNCTION update_nurturing_engagement_summary IS 
    'Actualiza el resumen de engagement para una secuencia. Ejecutar después de actualizar eventos.';

COMMIT;
