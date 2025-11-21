-- ============================================================================
-- SCHEMA: Sistema de A/B Testing Automatizado
-- ============================================================================
-- Sistema completo para:
-- - Tests de subject lines en emails
-- - Variaciones de landing pages
-- - Precios dinámicos
-- - CTA buttons
-- - Análisis estadístico automático
-- - Auto-deployment de versión ganadora
-- ============================================================================

BEGIN;

-- ============================================================================
-- Tabla de Tests A/B
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) UNIQUE NOT NULL,
    test_name VARCHAR(256) NOT NULL,
    test_type VARCHAR(64) NOT NULL, -- 'email_subject', 'landing_page', 'pricing', 'cta_button'
    description TEXT,
    
    -- Estado del test
    status VARCHAR(32) NOT NULL DEFAULT 'draft', -- 'draft', 'active', 'paused', 'completed', 'deployed'
    
    -- Configuración del test
    traffic_split JSONB NOT NULL, -- {"variant_a": 0.5, "variant_b": 0.5}
    minimum_sample_size INT DEFAULT 1000, -- Mínimo de muestras para significancia
    significance_level NUMERIC(5,4) DEFAULT 0.95, -- 95% de confianza
    minimum_lift_percentage NUMERIC(5,2) DEFAULT 5.0, -- Mínimo 5% de mejora requerida
    
    -- Auto-deployment
    auto_deploy_enabled BOOLEAN DEFAULT true,
    auto_deploy_when VARCHAR(32) DEFAULT 'significant', -- 'significant', 'significant_and_lift', 'manual'
    
    -- Métricas objetivo
    primary_metric VARCHAR(128) NOT NULL, -- 'open_rate', 'click_rate', 'conversion_rate', 'revenue'
    secondary_metrics JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_by VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    deployed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Tabla de Variantes
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_variants (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    variant_id VARCHAR(128) NOT NULL, -- 'variant_a', 'variant_b', etc.
    variant_name VARCHAR(256) NOT NULL,
    
    -- Configuración específica por tipo de test
    config JSONB NOT NULL, -- Contenido de la variante (subject, landing page config, pricing, CTA)
    
    -- Control de tráfico
    traffic_percentage NUMERIC(5,4) NOT NULL DEFAULT 0.5, -- 0.0 a 1.0
    
    -- Estado
    is_control BOOLEAN DEFAULT false, -- True si es la variante de control
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(test_id, variant_id)
);

-- ============================================================================
-- Tabla de Asignaciones (para consistencia)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_assignments (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    user_id VARCHAR(256), -- ID del usuario/visitante/lead
    session_id VARCHAR(256), -- ID de sesión
    email VARCHAR(256), -- Email para tests de email
    
    variant_id VARCHAR(128) NOT NULL,
    
    -- Contexto
    context JSONB DEFAULT '{}'::jsonb, -- Información adicional (IP, user agent, etc.)
    
    -- Metadata
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(test_id, user_id, email, session_id)
);

-- ============================================================================
-- Tabla de Eventos (tracking de interacciones)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_events (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    assignment_id INT REFERENCES ab_test_assignments(id) ON DELETE CASCADE,
    variant_id VARCHAR(128) NOT NULL,
    
    -- Tipo de evento
    event_type VARCHAR(64) NOT NULL, -- 'email_sent', 'email_opened', 'email_clicked', 'page_view', 'cta_clicked', 'purchase', etc.
    
    -- Métricas del evento
    metrics JSONB DEFAULT '{}'::jsonb, -- {revenue: 100, duration: 5, etc.}
    
    -- Metadata
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Tabla de Resultados Agregados (para análisis rápido)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_results (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    variant_id VARCHAR(128) NOT NULL,
    
    -- Período de análisis
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    analysis_window_hours INT DEFAULT 24, -- Ventana de análisis
    
    -- Métricas primarias
    total_assignments INT DEFAULT 0,
    total_events INT DEFAULT 0,
    
    -- Métricas específicas por tipo de test
    email_sent_count INT DEFAULT 0,
    email_opened_count INT DEFAULT 0,
    email_clicked_count INT DEFAULT 0,
    
    page_views INT DEFAULT 0,
    cta_clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    revenue NUMERIC(12,2) DEFAULT 0,
    
    -- Tasas calculadas
    open_rate NUMERIC(5,4), -- Para emails
    click_rate NUMERIC(5,4), -- Para emails
    conversion_rate NUMERIC(5,4), -- Para todos
    revenue_per_user NUMERIC(12,2),
    
    -- Análisis estadístico
    statistical_significance NUMERIC(5,4), -- p-value
    confidence_interval_lower NUMERIC(5,4),
    confidence_interval_upper NUMERIC(5,4),
    lift_percentage NUMERIC(5,2), -- vs control
    
    -- Metadata
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(test_id, variant_id, analysis_date)
);

-- ============================================================================
-- Tabla de Análisis Estadísticos (historial)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_statistical_analysis (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    
    -- Análisis
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    analysis_type VARCHAR(64) NOT NULL, -- 'daily', 'final', 'checkpoint'
    
    -- Comparación entre variantes
    comparison_data JSONB NOT NULL, -- {"variant_a": {...}, "variant_b": {...}, "winner": "variant_b"}
    
    -- Resultados estadísticos
    is_significant BOOLEAN DEFAULT false,
    p_value NUMERIC(10,8),
    confidence_level NUMERIC(5,4),
    winner_variant_id VARCHAR(128),
    winner_lift_percentage NUMERIC(5,2),
    
    -- Recomendación
    recommendation VARCHAR(64), -- 'deploy', 'continue', 'pause', 'extend'
    recommendation_reason TEXT,
    
    -- Metadata
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Tabla de Deployments (historial de auto-deployments)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ab_test_deployments (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(128) NOT NULL REFERENCES ab_tests(test_id) ON DELETE CASCADE,
    winning_variant_id VARCHAR(128) NOT NULL,
    
    -- Deployment
    deployment_type VARCHAR(32) NOT NULL, -- 'auto', 'manual'
    deployment_status VARCHAR(32) NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'failed'
    
    -- Resultados pre-deployment
    pre_deployment_metrics JSONB NOT NULL,
    
    -- Resultados post-deployment (opcional)
    post_deployment_metrics JSONB,
    
    -- Metadata
    deployed_by VARCHAR(128),
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- ============================================================================
-- Índices
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
CREATE INDEX IF NOT EXISTS idx_ab_tests_type ON ab_tests(test_type);
CREATE INDEX IF NOT EXISTS idx_ab_tests_created_at ON ab_tests(created_at);

CREATE INDEX IF NOT EXISTS idx_ab_variants_test_id ON ab_test_variants(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_variants_variant_id ON ab_test_variants(variant_id);

CREATE INDEX IF NOT EXISTS idx_ab_assignments_test_id ON ab_test_assignments(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_assignments_user_id ON ab_test_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_assignments_email ON ab_test_assignments(email);
CREATE INDEX IF NOT EXISTS idx_ab_assignments_variant_id ON ab_test_assignments(variant_id);

CREATE INDEX IF NOT EXISTS idx_ab_events_test_id ON ab_test_events(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_events_assignment_id ON ab_test_events(assignment_id);
CREATE INDEX IF NOT EXISTS idx_ab_events_variant_id ON ab_test_events(variant_id);
CREATE INDEX IF NOT EXISTS idx_ab_events_type ON ab_test_events(event_type);
CREATE INDEX IF NOT EXISTS idx_ab_events_timestamp ON ab_test_events(event_timestamp);

CREATE INDEX IF NOT EXISTS idx_ab_results_test_id ON ab_test_results(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_results_variant_id ON ab_test_results(variant_id);
CREATE INDEX IF NOT EXISTS idx_ab_results_date ON ab_test_results(analysis_date);

CREATE INDEX IF NOT EXISTS idx_ab_analysis_test_id ON ab_test_statistical_analysis(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_analysis_timestamp ON ab_test_statistical_analysis(analysis_timestamp);

CREATE INDEX IF NOT EXISTS idx_ab_deployments_test_id ON ab_test_deployments(test_id);
CREATE INDEX IF NOT EXISTS idx_ab_deployments_status ON ab_test_deployments(deployment_status);

-- ============================================================================
-- Funciones Helper
-- ============================================================================

-- Función para asignar variante de forma determinística
CREATE OR REPLACE FUNCTION assign_ab_variant(
    p_test_id VARCHAR(128),
    p_user_id VARCHAR(256) DEFAULT NULL,
    p_email VARCHAR(256) DEFAULT NULL,
    p_session_id VARCHAR(256) DEFAULT NULL
)
RETURNS VARCHAR(128) AS $$
DECLARE
    v_variant_id VARCHAR(128);
    v_assignment_id INT;
    v_hash_value BIGINT;
    v_random_value NUMERIC;
    v_cumulative NUMERIC := 0;
    v_traffic_percentage NUMERIC;
    v_test_status VARCHAR(32);
BEGIN
    -- Verificar que el test esté activo
    SELECT status INTO v_test_status
    FROM ab_tests
    WHERE test_id = p_test_id;
    
    IF v_test_status != 'active' THEN
        RAISE EXCEPTION 'Test % is not active (status: %)', p_test_id, v_test_status;
    END IF;
    
    -- Verificar si ya existe una asignación
    SELECT variant_id, id INTO v_variant_id, v_assignment_id
    FROM ab_test_assignments
    WHERE test_id = p_test_id
    AND (
        (p_user_id IS NOT NULL AND user_id = p_user_id) OR
        (p_email IS NOT NULL AND email = p_email) OR
        (p_session_id IS NOT NULL AND session_id = p_session_id)
    )
    LIMIT 1;
    
    -- Si ya existe, retornar la variante asignada
    IF v_variant_id IS NOT NULL THEN
        RETURN v_variant_id;
    END IF;
    
    -- Calcular hash determinístico
    v_hash_value := abs(hashtext(
        COALESCE(p_test_id, '') || ':' ||
        COALESCE(p_user_id, '') || ':' ||
        COALESCE(p_email, '') || ':' ||
        COALESCE(p_session_id, '')
    ));
    
    v_random_value := (v_hash_value % 10000) / 10000.0;
    
    -- Asignar variante basado en porcentaje de tráfico
    FOR v_variant_id, v_traffic_percentage IN
        SELECT variant_id, traffic_percentage
        FROM ab_test_variants
        WHERE test_id = p_test_id
        AND is_active = true
        ORDER BY variant_id
    LOOP
        v_cumulative := v_cumulative + v_traffic_percentage;
        IF v_random_value <= v_cumulative THEN
            -- Crear asignación
            INSERT INTO ab_test_assignments (
                test_id, user_id, email, session_id, variant_id
            ) VALUES (
                p_test_id, p_user_id, p_email, p_session_id, v_variant_id
            )
            RETURNING id INTO v_assignment_id;
            
            RETURN v_variant_id;
        END IF;
    END LOOP;
    
    -- Fallback: retornar primera variante activa
    SELECT variant_id INTO v_variant_id
    FROM ab_test_variants
    WHERE test_id = p_test_id
    AND is_active = true
    ORDER BY variant_id
    LIMIT 1;
    
    RETURN v_variant_id;
END;
$$ LANGUAGE plpgsql;

-- Función para registrar evento
CREATE OR REPLACE FUNCTION record_ab_event(
    p_test_id VARCHAR(128),
    p_user_id VARCHAR(256) DEFAULT NULL,
    p_email VARCHAR(256) DEFAULT NULL,
    p_session_id VARCHAR(256) DEFAULT NULL,
    p_event_type VARCHAR(64),
    p_metrics JSONB DEFAULT '{}'::jsonb
)
RETURNS INT AS $$
DECLARE
    v_assignment_id INT;
    v_variant_id VARCHAR(128);
BEGIN
    -- Obtener o crear asignación
    SELECT id, variant_id INTO v_assignment_id, v_variant_id
    FROM ab_test_assignments
    WHERE test_id = p_test_id
    AND (
        (p_user_id IS NOT NULL AND user_id = p_user_id) OR
        (p_email IS NOT NULL AND email = p_email) OR
        (p_session_id IS NOT NULL AND session_id = p_session_id)
    )
    LIMIT 1;
    
    -- Si no existe asignación, crear una
    IF v_assignment_id IS NULL THEN
        v_variant_id := assign_ab_variant(p_test_id, p_user_id, p_email, p_session_id);
        SELECT id INTO v_assignment_id
        FROM ab_test_assignments
        WHERE test_id = p_test_id
        AND variant_id = v_variant_id
        AND (
            (p_user_id IS NOT NULL AND user_id = p_user_id) OR
            (p_email IS NOT NULL AND email = p_email) OR
            (p_session_id IS NOT NULL AND session_id = p_session_id)
        )
        LIMIT 1;
    END IF;
    
    -- Registrar evento
    INSERT INTO ab_test_events (
        test_id, assignment_id, variant_id, event_type, metrics
    ) VALUES (
        p_test_id, v_assignment_id, v_variant_id, p_event_type, p_metrics
    )
    RETURNING id INTO v_assignment_id;
    
    RETURN v_assignment_id;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular resultados agregados
CREATE OR REPLACE FUNCTION calculate_ab_test_results(
    p_test_id VARCHAR(128),
    p_analysis_date DATE DEFAULT CURRENT_DATE,
    p_window_hours INT DEFAULT 24
)
RETURNS VOID AS $$
DECLARE
    v_test_type VARCHAR(64);
    v_start_timestamp TIMESTAMPTZ;
    v_end_timestamp TIMESTAMPTZ;
BEGIN
    -- Obtener tipo de test
    SELECT test_type INTO v_test_type
    FROM ab_tests
    WHERE test_id = p_test_id;
    
    -- Calcular ventana de tiempo
    v_start_timestamp := (p_analysis_date || ' 00:00:00')::TIMESTAMPTZ;
    v_end_timestamp := v_start_timestamp + (p_window_hours || ' hours')::INTERVAL;
    
    -- Limpiar resultados previos para esta fecha
    DELETE FROM ab_test_results
    WHERE test_id = p_test_id
    AND analysis_date = p_analysis_date;
    
    -- Calcular resultados por variante
    INSERT INTO ab_test_results (
        test_id,
        variant_id,
        analysis_date,
        analysis_window_hours,
        total_assignments,
        total_events,
        email_sent_count,
        email_opened_count,
        email_clicked_count,
        page_views,
        cta_clicks,
        conversions,
        revenue,
        open_rate,
        click_rate,
        conversion_rate,
        revenue_per_user
    )
    SELECT
        a.test_id,
        a.variant_id,
        p_analysis_date,
        p_window_hours,
        COUNT(DISTINCT a.id) as total_assignments,
        COUNT(e.id) as total_events,
        COUNT(e.id) FILTER (WHERE e.event_type = 'email_sent') as email_sent_count,
        COUNT(e.id) FILTER (WHERE e.event_type = 'email_opened') as email_opened_count,
        COUNT(e.id) FILTER (WHERE e.event_type = 'email_clicked') as email_clicked_count,
        COUNT(e.id) FILTER (WHERE e.event_type = 'page_view') as page_views,
        COUNT(e.id) FILTER (WHERE e.event_type = 'cta_clicked') as cta_clicks,
        COUNT(e.id) FILTER (WHERE e.event_type IN ('conversion', 'purchase', 'signup')) as conversions,
        COALESCE(SUM((e.metrics->>'revenue')::NUMERIC), 0) as revenue,
        -- Tasas
        CASE 
            WHEN COUNT(e.id) FILTER (WHERE e.event_type = 'email_sent') > 0 
            THEN COUNT(e.id) FILTER (WHERE e.event_type = 'email_opened')::NUMERIC / 
                 COUNT(e.id) FILTER (WHERE e.event_type = 'email_sent')::NUMERIC
            ELSE NULL
        END as open_rate,
        CASE 
            WHEN COUNT(e.id) FILTER (WHERE e.event_type = 'email_opened') > 0 
            THEN COUNT(e.id) FILTER (WHERE e.event_type = 'email_clicked')::NUMERIC / 
                 COUNT(e.id) FILTER (WHERE e.event_type = 'email_opened')::NUMERIC
            ELSE NULL
        END as click_rate,
        CASE 
            WHEN COUNT(DISTINCT a.id) > 0 
            THEN COUNT(e.id) FILTER (WHERE e.event_type IN ('conversion', 'purchase', 'signup'))::NUMERIC / 
                 COUNT(DISTINCT a.id)::NUMERIC
            ELSE NULL
        END as conversion_rate,
        CASE 
            WHEN COUNT(DISTINCT a.id) > 0 
            THEN COALESCE(SUM((e.metrics->>'revenue')::NUMERIC), 0) / COUNT(DISTINCT a.id)::NUMERIC
            ELSE NULL
        END as revenue_per_user
    FROM ab_test_assignments a
    LEFT JOIN ab_test_events e ON e.assignment_id = a.id
        AND e.event_timestamp >= v_start_timestamp
        AND e.event_timestamp < v_end_timestamp
    WHERE a.test_id = p_test_id
    GROUP BY a.test_id, a.variant_id;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================================================
-- Ejemplos de Tests
-- ============================================================================

-- Ejemplo: Test de Subject Line de Email
INSERT INTO ab_tests (
    test_id, test_name, test_type, description, status,
    traffic_split, minimum_sample_size, significance_level,
    primary_metric, auto_deploy_enabled
) VALUES (
    'email_subject_welcome_v1',
    'Test de Subject Line - Email de Bienvenida',
    'email_subject',
    'Comparar dos subject lines para emails de bienvenida',
    'draft',
    '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
    1000,
    0.95,
    'open_rate',
    true
) ON CONFLICT (test_id) DO NOTHING;

-- Ejemplo: Test de Landing Page
INSERT INTO ab_tests (
    test_id, test_name, test_type, description, status,
    traffic_split, minimum_sample_size, significance_level,
    primary_metric, auto_deploy_enabled
) VALUES (
    'landing_page_homepage_v1',
    'Test de Landing Page - Homepage',
    'landing_page',
    'Comparar dos versiones de la homepage',
    'draft',
    '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
    2000,
    0.95,
    'conversion_rate',
    true
) ON CONFLICT (test_id) DO NOTHING;

-- Ejemplo: Test de Pricing
INSERT INTO ab_tests (
    test_id, test_name, test_type, description, status,
    traffic_split, minimum_sample_size, significance_level,
    primary_metric, auto_deploy_enabled
) VALUES (
    'pricing_strategy_v1',
    'Test de Estrategia de Precios',
    'pricing',
    'Comparar diferentes estrategias de precios',
    'draft',
    '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
    1500,
    0.95,
    'revenue',
    true
) ON CONFLICT (test_id) DO NOTHING;

-- Ejemplo: Test de CTA Button
INSERT INTO ab_tests (
    test_id, test_name, test_type, description, status,
    traffic_split, minimum_sample_size, significance_level,
    primary_metric, auto_deploy_enabled
) VALUES (
    'cta_button_checkout_v1',
    'Test de CTA Button - Checkout',
    'cta_button',
    'Comparar diferentes textos y colores de CTA',
    'draft',
    '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
    800,
    0.95,
    'conversion_rate',
    true
) ON CONFLICT (test_id) DO NOTHING;

