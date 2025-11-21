-- ============================================================================
-- SCHEMA: Sistema de Automatización de Marketing de Contenido
-- ============================================================================
-- Este esquema soporta:
-- - Gestión de artículos/blogs
-- - Conversión a múltiples formatos (tweets, LinkedIn, newsletters)
-- - Programación de publicaciones en redes sociales
-- - Tracking de engagement por canal
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Artículos/Blogs
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(128) UNIQUE NOT NULL,
    title VARCHAR(512) NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author VARCHAR(256),
    author_email VARCHAR(256),
    
    -- URLs y metadatos
    source_url TEXT, -- URL del artículo original
    featured_image_url TEXT,
    tags TEXT[], -- Array de tags
    
    -- Estado y categorización
    status VARCHAR(32) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    category VARCHAR(128),
    language VARCHAR(8) DEFAULT 'es',
    
    -- Fechas
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadatos adicionales
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT unique_article_id UNIQUE(article_id)
);

CREATE INDEX IF NOT EXISTS idx_content_articles_status ON content_articles(status);
CREATE INDEX IF NOT EXISTS idx_content_articles_created_at ON content_articles(created_at);
CREATE INDEX IF NOT EXISTS idx_content_articles_category ON content_articles(category);

-- ============================================================================
-- 2. Tabla de Versiones de Contenido (conversiones)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_versions (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(128) NOT NULL REFERENCES content_articles(article_id) ON DELETE CASCADE,
    version_type VARCHAR(32) NOT NULL CHECK (version_type IN ('twitter', 'linkedin', 'newsletter', 'facebook', 'instagram', 'thread')),
    platform VARCHAR(32) NOT NULL,
    
    -- Contenido convertido
    content TEXT NOT NULL,
    media_urls TEXT[], -- URLs de imágenes/videos
    hashtags TEXT[], -- Hashtags extraídos/generados
    
    -- Características del formato
    character_count INTEGER,
    word_count INTEGER,
    estimated_read_time INTEGER, -- minutos
    
    -- Estado
    status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'scheduled', 'published', 'failed')),
    approved_by VARCHAR(256),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_article_version UNIQUE(article_id, version_type, platform)
);

CREATE INDEX IF NOT EXISTS idx_content_versions_article_id ON content_versions(article_id);
CREATE INDEX IF NOT EXISTS idx_content_versions_status ON content_versions(status);
CREATE INDEX IF NOT EXISTS idx_content_versions_platform ON content_versions(platform);

-- ============================================================================
-- 3. Tabla de Publicaciones Programadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_scheduled_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(128) UNIQUE NOT NULL,
    article_id VARCHAR(128) REFERENCES content_articles(article_id) ON DELETE SET NULL,
    version_id INTEGER REFERENCES content_versions(id) ON DELETE SET NULL,
    
    -- Plataforma y canal
    platform VARCHAR(32) NOT NULL CHECK (platform IN ('twitter', 'linkedin', 'facebook', 'instagram', 'threads')),
    account_id VARCHAR(128), -- ID de la cuenta en la plataforma
    account_name VARCHAR(256),
    
    -- Contenido a publicar
    content TEXT NOT NULL,
    media_urls TEXT[],
    hashtags TEXT[],
    
    -- Programación
    scheduled_at TIMESTAMPTZ NOT NULL,
    timezone VARCHAR(64) DEFAULT 'UTC',
    status VARCHAR(32) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'publishing', 'published', 'failed', 'cancelled')),
    
    -- Resultados de publicación
    published_post_id VARCHAR(256), -- ID del post publicado en la plataforma
    published_url TEXT,
    published_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON content_scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_at ON content_scheduled_posts(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_platform ON content_scheduled_posts(platform);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_article_id ON content_scheduled_posts(article_id);

-- ============================================================================
-- 4. Tabla de Engagement/Métricas
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_engagement (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(128) NOT NULL REFERENCES content_scheduled_posts(post_id) ON DELETE CASCADE,
    platform_post_id VARCHAR(256) NOT NULL, -- ID del post en la plataforma
    
    -- Métricas básicas
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0, -- Para Twitter
    saves INTEGER DEFAULT 0, -- Para Instagram
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    
    -- Métricas calculadas
    engagement_rate NUMERIC(5,2), -- Porcentaje de engagement
    click_through_rate NUMERIC(5,2), -- CTR
    
    -- Desglose por tipo de engagement
    engagement_breakdown JSONB DEFAULT '{}'::jsonb,
    
    -- Fechas de tracking
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    tracked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_post_engagement UNIQUE(post_id, platform_post_id)
);

CREATE INDEX IF NOT EXISTS idx_engagement_post_id ON content_engagement(post_id);
CREATE INDEX IF NOT EXISTS idx_engagement_tracked_at ON content_engagement(tracked_at);
CREATE INDEX IF NOT EXISTS idx_engagement_platform_post_id ON content_engagement(platform_post_id);

-- ============================================================================
-- 5. Tabla de Historial de Engagement (snapshots)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_engagement_history (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(128) NOT NULL REFERENCES content_scheduled_posts(post_id) ON DELETE CASCADE,
    platform_post_id VARCHAR(256) NOT NULL,
    
    -- Métricas en el momento del snapshot
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    engagement_rate NUMERIC(5,2),
    
    -- Snapshot metadata
    snapshot_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_engagement_history_post_id ON content_engagement_history(post_id);
CREATE INDEX IF NOT EXISTS idx_engagement_history_snapshot_at ON content_engagement_history(snapshot_at);

-- ============================================================================
-- 6. Tabla de Configuración de Plataformas
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_platform_config (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(32) NOT NULL UNIQUE CHECK (platform IN ('twitter', 'linkedin', 'facebook', 'instagram', 'threads')),
    account_id VARCHAR(128) NOT NULL,
    account_name VARCHAR(256),
    
    -- Credenciales (encriptadas)
    api_key VARCHAR(512),
    api_secret VARCHAR(512),
    access_token VARCHAR(512),
    access_token_secret VARCHAR(512),
    refresh_token VARCHAR(512),
    
    -- Configuración
    is_active BOOLEAN DEFAULT TRUE,
    default_hashtags TEXT[],
    default_mentions TEXT[],
    posting_schedule JSONB, -- Horarios preferidos para publicar
    
    -- Límites y rate limits
    daily_post_limit INTEGER DEFAULT 10,
    hourly_post_limit INTEGER DEFAULT 2,
    last_post_at TIMESTAMPTZ,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_platform_config_platform ON content_platform_config(platform);
CREATE INDEX IF NOT EXISTS idx_platform_config_is_active ON content_platform_config(is_active);

-- ============================================================================
-- 7. Tabla de Templates de Conversión
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_conversion_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(128) NOT NULL UNIQUE,
    platform VARCHAR(32) NOT NULL,
    version_type VARCHAR(32) NOT NULL,
    
    -- Template configuration
    template_content TEXT NOT NULL, -- Template con placeholders
    max_length INTEGER,
    min_length INTEGER,
    required_fields TEXT[],
    
    -- Reglas de conversión
    extraction_rules JSONB, -- Reglas para extraer contenido del artículo
    formatting_rules JSONB, -- Reglas de formateo
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Metadatos
    description TEXT,
    created_by VARCHAR(256),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversion_templates_platform ON content_conversion_templates(platform);
CREATE INDEX IF NOT EXISTS idx_conversion_templates_is_active ON content_conversion_templates(is_active);

-- ============================================================================
-- 8. Tabla de Análisis de Performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_performance_analysis (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(128) REFERENCES content_articles(article_id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    
    -- Métricas agregadas por artículo
    total_posts INTEGER DEFAULT 0,
    total_platforms INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    total_impressions INTEGER DEFAULT 0,
    total_reach INTEGER DEFAULT 0,
    avg_engagement_rate NUMERIC(5,2),
    
    -- Mejor performing post
    best_post_id VARCHAR(128),
    best_platform VARCHAR(32),
    
    -- Desglose por plataforma
    platform_breakdown JSONB DEFAULT '{}'::jsonb,
    
    -- Insights
    insights TEXT[],
    recommendations TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_article_analysis_date UNIQUE(article_id, analysis_date)
);

CREATE INDEX IF NOT EXISTS idx_performance_analysis_article_id ON content_performance_analysis(article_id);
CREATE INDEX IF NOT EXISTS idx_performance_analysis_date ON content_performance_analysis(analysis_date);

COMMIT;

-- ============================================================================
-- Comentarios de documentación
-- ============================================================================
COMMENT ON TABLE content_articles IS 'Artículos/blogs que serán convertidos y distribuidos';
COMMENT ON TABLE content_versions IS 'Versiones convertidas del artículo para diferentes plataformas';
COMMENT ON TABLE content_scheduled_posts IS 'Publicaciones programadas en redes sociales';
COMMENT ON TABLE content_engagement IS 'Métricas de engagement actuales por post';
COMMENT ON TABLE content_engagement_history IS 'Historial de snapshots de engagement para análisis temporal';
COMMENT ON TABLE content_platform_config IS 'Configuración de cuentas de redes sociales';
COMMENT ON TABLE content_conversion_templates IS 'Templates para convertir artículos a diferentes formatos';
COMMENT ON TABLE content_performance_analysis IS 'Análisis agregado de performance por artículo';

