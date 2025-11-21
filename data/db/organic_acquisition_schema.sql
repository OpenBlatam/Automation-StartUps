-- ============================================================================
-- SCHEMA PARA AUTOMATIZACIÓN DE ADQUISICIÓN ORGÁNICA CON NURTURING Y REFERIDOS
-- ============================================================================

-- Tabla principal de leads orgánicos
CREATE TABLE IF NOT EXISTS organic_leads (
    lead_id VARCHAR(128) PRIMARY KEY,
    email VARCHAR(256) NOT NULL,
    first_name VARCHAR(128),
    last_name VARCHAR(128),
    source VARCHAR(64) DEFAULT 'organic',
    utm_source VARCHAR(128),
    utm_campaign VARCHAR(128),
    utm_medium VARCHAR(64),
    interest_area VARCHAR(128),
    lead_magnet_downloaded BOOLEAN DEFAULT false,
    referral_code VARCHAR(64),
    referrer_lead_id VARCHAR(128),
    status VARCHAR(32) DEFAULT 'new' CHECK (status IN ('new', 'nurturing', 'engaged', 'converted', 'inactive')),
    engagement_score INTEGER DEFAULT 0,
    content_consumed INTEGER DEFAULT 0,
    crm_synced BOOLEAN DEFAULT false,
    crm_synced_at TIMESTAMP,
    crm_contact_id VARCHAR(128),
    engaged_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organic_leads_email ON organic_leads(email);
CREATE INDEX IF NOT EXISTS idx_organic_leads_status ON organic_leads(status);
CREATE INDEX IF NOT EXISTS idx_organic_leads_source ON organic_leads(source);
CREATE INDEX IF NOT EXISTS idx_organic_leads_referral_code ON organic_leads(referral_code);
CREATE INDEX IF NOT EXISTS idx_organic_leads_created_at ON organic_leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_organic_leads_engagement ON organic_leads(engagement_score DESC);

-- Tabla de templates de nurturing
CREATE TABLE IF NOT EXISTS nurturing_templates (
    template_id VARCHAR(128) PRIMARY KEY,
    template_name VARCHAR(256) NOT NULL,
    interest_area VARCHAR(128),
    sequence_name VARCHAR(256) NOT NULL,
    content_items JSONB NOT NULL DEFAULT '[]'::jsonb,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nurturing_templates_interest ON nurturing_templates(interest_area);
CREATE INDEX IF NOT EXISTS idx_nurturing_templates_active ON nurturing_templates(active) WHERE active = true;

-- Tabla de secuencias de nurturing activas
CREATE TABLE IF NOT EXISTS nurturing_sequences (
    sequence_id VARCHAR(128) PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    template_id VARCHAR(128) REFERENCES nurturing_templates(template_id),
    sequence_name VARCHAR(256) NOT NULL,
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER DEFAULT 5,
    status VARCHAR(32) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled')),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    paused_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_lead ON nurturing_sequences(lead_id);
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_status ON nurturing_sequences(status);
CREATE INDEX IF NOT EXISTS idx_nurturing_sequences_started ON nurturing_sequences(started_at DESC);

-- Tabla de engagement con contenido
CREATE TABLE IF NOT EXISTS content_engagement (
    engagement_id SERIAL PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    sequence_id VARCHAR(128) REFERENCES nurturing_sequences(sequence_id) ON DELETE CASCADE,
    content_type VARCHAR(64) NOT NULL CHECK (content_type IN ('blog', 'guide', 'video', 'webinar', 'ebook')),
    content_id VARCHAR(128),
    content_title VARCHAR(512),
    content_url TEXT,
    status VARCHAR(32) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'sent', 'opened', 'clicked', 'completed', 'failed')),
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_engagement_lead ON content_engagement(lead_id);
CREATE INDEX IF NOT EXISTS idx_content_engagement_sequence ON content_engagement(sequence_id);
CREATE INDEX IF NOT EXISTS idx_content_engagement_status ON content_engagement(status);
CREATE INDEX IF NOT EXISTS idx_content_engagement_scheduled ON content_engagement(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX IF NOT EXISTS idx_content_engagement_type ON content_engagement(content_type);

-- Tabla de programas de referidos
CREATE TABLE IF NOT EXISTS referral_programs (
    program_id SERIAL PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    referral_code VARCHAR(64) UNIQUE NOT NULL,
    referral_link TEXT NOT NULL,
    incentive_amount DECIMAL(10, 2) NOT NULL DEFAULT 10.00,
    status VARCHAR(32) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'cancelled')),
    invited_at TIMESTAMP,
    joined_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_referral_programs_lead ON referral_programs(lead_id);
CREATE INDEX IF NOT EXISTS idx_referral_programs_code ON referral_programs(referral_code);
CREATE INDEX IF NOT EXISTS idx_referral_programs_status ON referral_programs(status);

-- Tabla de referidos
CREATE TABLE IF NOT EXISTS referrals (
    referral_id VARCHAR(128) PRIMARY KEY,
    referrer_lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    referral_code VARCHAR(64) NOT NULL REFERENCES referral_programs(referral_code),
    referred_email VARCHAR(256) NOT NULL,
    referred_first_name VARCHAR(128),
    referred_last_name VARCHAR(128),
    referred_phone VARCHAR(32),
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'validated', 'fraud', 'rejected')),
    fraud_reasons JSONB,
    validated_at TIMESTAMP,
    validated_by VARCHAR(128),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_lead_id);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);
CREATE INDEX IF NOT EXISTS idx_referrals_email ON referrals(referred_email);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_created ON referrals(created_at DESC);

-- Tabla de recompensas por referidos
CREATE TABLE IF NOT EXISTS referral_rewards (
    reward_id VARCHAR(128) PRIMARY KEY,
    referral_id VARCHAR(128) NOT NULL REFERENCES referrals(referral_id) ON DELETE CASCADE,
    referrer_lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    reward_amount DECIMAL(10, 2) NOT NULL,
    reward_type VARCHAR(32) DEFAULT 'cash' CHECK (reward_type IN ('cash', 'credit', 'points', 'discount')),
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled')),
    paid_at TIMESTAMP,
    payment_method VARCHAR(64),
    payment_reference VARCHAR(128),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_referral_rewards_referrer ON referral_rewards(referrer_lead_id);
CREATE INDEX IF NOT EXISTS idx_referral_rewards_referral ON referral_rewards(referral_id);
CREATE INDEX IF NOT EXISTS idx_referral_rewards_status ON referral_rewards(status);
CREATE INDEX IF NOT EXISTS idx_referral_rewards_created ON referral_rewards(created_at DESC);

-- Tabla de log de recordatorios
CREATE TABLE IF NOT EXISTS reminder_log (
    reminder_id SERIAL PRIMARY KEY,
    lead_id VARCHAR(128) NOT NULL REFERENCES organic_leads(lead_id) ON DELETE CASCADE,
    reminder_type VARCHAR(64) NOT NULL CHECK (reminder_type IN ('first', 'second_incentive', 'engagement', 'referral')),
    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_reminder_log_lead ON reminder_log(lead_id);
CREATE INDEX IF NOT EXISTS idx_reminder_log_type ON reminder_log(reminder_type);
CREATE INDEX IF NOT EXISTS idx_reminder_log_sent ON reminder_log(sent_at DESC);

-- Tabla de métricas de adquisición
CREATE TABLE IF NOT EXISTS acquisition_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id VARCHAR(128) UNIQUE NOT NULL,
    report_type VARCHAR(32) NOT NULL CHECK (report_type IN ('daily', 'weekly', 'monthly')),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    metrics_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_acquisition_metrics_type ON acquisition_metrics(report_type);
CREATE INDEX IF NOT EXISTS idx_acquisition_metrics_period ON acquisition_metrics(period_start DESC, period_end DESC);

-- ============================================================================
-- FUNCIONES Y TRIGGERS
-- ============================================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER update_organic_leads_updated_at
    BEFORE UPDATE ON organic_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nurturing_templates_updated_at
    BEFORE UPDATE ON nurturing_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_nurturing_sequences_updated_at
    BEFORE UPDATE ON nurturing_sequences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_engagement_updated_at
    BEFORE UPDATE ON content_engagement
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referral_programs_updated_at
    BEFORE UPDATE ON referral_programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referrals_updated_at
    BEFORE UPDATE ON referrals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referral_rewards_updated_at
    BEFORE UPDATE ON referral_rewards
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular engagement score
CREATE OR REPLACE FUNCTION calculate_engagement_score(p_lead_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_score INTEGER;
BEGIN
    SELECT COALESCE(SUM(
        CASE 
            WHEN status = 'completed' THEN 3
            WHEN status = 'clicked' THEN 2
            WHEN status = 'opened' THEN 1
            ELSE 0
        END
    ), 0) INTO v_score
    FROM content_engagement
    WHERE lead_id = p_lead_id;
    
    RETURN v_score;
END;
$$ LANGUAGE plpgsql;

-- Función para validar referido
CREATE OR REPLACE FUNCTION validate_referral(p_referral_id VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_referral RECORD;
    v_referrer_email VARCHAR;
    v_is_valid BOOLEAN := true;
BEGIN
    -- Obtener datos del referido
    SELECT * INTO v_referral
    FROM referrals
    WHERE referral_id = p_referral_id;
    
    IF NOT FOUND THEN
        RETURN false;
    END IF;
    
    -- Obtener email del referidor
    SELECT email INTO v_referrer_email
    FROM organic_leads
    WHERE lead_id = v_referral.referrer_lead_id;
    
    -- Validación 1: No auto-referido
    IF LOWER(v_referral.referred_email) = LOWER(v_referrer_email) THEN
        RETURN false;
    END IF;
    
    -- Validación 2: No existe ya como lead antes del referido
    IF EXISTS (
        SELECT 1 FROM organic_leads
        WHERE email = v_referral.referred_email
        AND created_at < v_referral.created_at
    ) THEN
        RETURN false;
    END IF;
    
    RETURN v_is_valid;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DATOS INICIALES (Templates de nurturing)
-- ============================================================================

-- Insertar templates por defecto
INSERT INTO nurturing_templates (template_id, template_name, interest_area, sequence_name, content_items, active)
VALUES 
    (
        'template_general',
        'Template General',
        'general',
        'Secuencia de Nurturing General',
        '[
            {"type": "blog", "id": "blog_1", "title": "Guía de Inicio Rápido", "url": "https://tu-dominio.com/blog/guia-inicio"},
            {"type": "guide", "id": "guide_1", "title": "Guía Completa de Mejores Prácticas", "url": "https://tu-dominio.com/guides/mejores-practicas"},
            {"type": "video", "id": "video_1", "title": "Video Tutorial: Primeros Pasos", "url": "https://tu-dominio.com/videos/tutorial"},
            {"type": "blog", "id": "blog_2", "title": "Casos de Éxito", "url": "https://tu-dominio.com/blog/casos-exito"},
            {"type": "ebook", "id": "ebook_1", "title": "Ebook Completo", "url": "https://tu-dominio.com/ebooks/completo"}
        ]'::jsonb,
        true
    ),
    (
        'template_marketing',
        'Template Marketing',
        'marketing',
        'Secuencia de Nurturing Marketing',
        '[
            {"type": "blog", "id": "blog_mkt_1", "title": "Estrategias de Marketing Digital", "url": "https://tu-dominio.com/blog/marketing-digital"},
            {"type": "guide", "id": "guide_mkt_1", "title": "Guía de Automatización de Marketing", "url": "https://tu-dominio.com/guides/automatizacion-marketing"},
            {"type": "video", "id": "video_mkt_1", "title": "Webinar: Marketing Avanzado", "url": "https://tu-dominio.com/videos/marketing-avanzado"}
        ]'::jsonb,
        true
    ),
    (
        'template_sales',
        'Template Ventas',
        'sales',
        'Secuencia de Nurturing Ventas',
        '[
            {"type": "blog", "id": "blog_sales_1", "title": "Técnicas de Cierre de Ventas", "url": "https://tu-dominio.com/blog/cierre-ventas"},
            {"type": "guide", "id": "guide_sales_1", "title": "Guía de Prospección", "url": "https://tu-dominio.com/guides/prospeccion"},
            {"type": "video", "id": "video_sales_1", "title": "Video: Pipeline de Ventas", "url": "https://tu-dominio.com/videos/pipeline-ventas"}
        ]'::jsonb,
        true
    )
ON CONFLICT (template_id) DO NOTHING;

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista de leads con métricas de engagement
CREATE OR REPLACE VIEW v_leads_with_engagement AS
SELECT 
    ol.*,
    COUNT(ce.engagement_id) as total_content_items,
    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_items,
    COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as opened_items,
    MAX(ce.sent_at) as last_content_sent_at
FROM organic_leads ol
LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
GROUP BY ol.lead_id;

-- Vista de referidos con estadísticas
CREATE OR REPLACE VIEW v_referrals_stats AS
SELECT 
    rp.lead_id as referrer_lead_id,
    ol.email as referrer_email,
    rp.referral_code,
    rp.incentive_amount,
    COUNT(r.referral_id) as total_referrals,
    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated_referrals,
    COUNT(CASE WHEN r.status = 'fraud' THEN 1 END) as fraud_referrals,
    COALESCE(SUM(rr.reward_amount), 0) as total_rewards_earned,
    rp.invited_at,
    rp.joined_at
FROM referral_programs rp
JOIN organic_leads ol ON rp.lead_id = ol.lead_id
LEFT JOIN referrals r ON rp.referral_code = r.referral_code
LEFT JOIN referral_rewards rr ON r.referral_id = rr.referral_id AND rr.status = 'paid'
GROUP BY rp.lead_id, ol.email, rp.referral_code, rp.incentive_amount, rp.invited_at, rp.joined_at;

-- Vista de métricas de conversión
CREATE OR REPLACE VIEW v_conversion_metrics AS
SELECT 
    DATE_TRUNC('day', ol.created_at) as date,
    COUNT(*) as total_leads,
    COUNT(CASE WHEN ol.status = 'engaged' THEN 1 END) as engaged_leads,
    COUNT(DISTINCT rp.lead_id) as invited_to_referrals,
    COUNT(DISTINCT r.referral_id) as total_referrals,
    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated_referrals,
    ROUND(
        COUNT(CASE WHEN ol.status = 'engaged' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as engagement_rate,
    ROUND(
        COUNT(DISTINCT r.referral_id)::NUMERIC / 
        NULLIF(COUNT(DISTINCT rp.lead_id), 0) * 100, 
        2
    ) as referral_rate
FROM organic_leads ol
LEFT JOIN referral_programs rp ON ol.lead_id = rp.lead_id
LEFT JOIN referrals r ON rp.referral_code = r.referral_code
WHERE ol.created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', ol.created_at)
ORDER BY date DESC;

