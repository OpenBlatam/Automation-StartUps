-- Esquema de base de datos para descripciones de productos

-- Tabla principal de descripciones de productos
CREATE TABLE IF NOT EXISTS product_descriptions (
    product_description_id SERIAL PRIMARY KEY,
    product_name VARCHAR(500) NOT NULL,
    product_type VARCHAR(200),
    description TEXT NOT NULL,
    full_description_data JSONB,
    platform VARCHAR(50) DEFAULT 'generic',
    seo_keywords JSONB,
    meta_description TEXT,
    multimedia_suggestions JSONB,
    word_count INTEGER,
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'draft',
    created_by VARCHAR(100),
    
    -- Índices
    CONSTRAINT product_descriptions_platform_check 
        CHECK (platform IN ('amazon', 'shopify', 'generic'))
);

-- Tabla de variaciones para A/B testing
CREATE TABLE IF NOT EXISTS product_description_variations (
    variation_id SERIAL PRIMARY KEY,
    product_description_id INTEGER REFERENCES product_descriptions(product_description_id) ON DELETE CASCADE,
    variation_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    variation_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT variations_type_check 
        CHECK (variation_type IN ('emotional', 'technical', 'benefit_focused', 'seo_optimized', 'custom'))
);

-- Tabla de caché para evitar regeneraciones
CREATE TABLE IF NOT EXISTS product_descriptions_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    description_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de métricas de A/B testing
CREATE TABLE IF NOT EXISTS product_description_ab_metrics (
    metric_id SERIAL PRIMARY KEY,
    product_description_id INTEGER REFERENCES product_descriptions(product_description_id) ON DELETE CASCADE,
    variation_id INTEGER REFERENCES product_description_variations(variation_id) ON DELETE CASCADE,
    platform VARCHAR(50),
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    conversion_rate DECIMAL(5, 4),
    date_recorded DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(product_description_id, variation_id, platform, date_recorded)
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_product_descriptions_product_name ON product_descriptions(product_name);
CREATE INDEX IF NOT EXISTS idx_product_descriptions_platform ON product_descriptions(platform);
CREATE INDEX IF NOT EXISTS idx_product_descriptions_status ON product_descriptions(status);
CREATE INDEX IF NOT EXISTS idx_product_descriptions_created_at ON product_descriptions(created_at);
CREATE INDEX IF NOT EXISTS idx_variations_product_id ON product_description_variations(product_description_id);
CREATE INDEX IF NOT EXISTS idx_variations_type ON product_description_variations(variation_type);
CREATE INDEX IF NOT EXISTS idx_cache_created_at ON product_descriptions_cache(created_at);
CREATE INDEX IF NOT EXISTS idx_ab_metrics_product_id ON product_description_ab_metrics(product_description_id);
CREATE INDEX IF NOT EXISTS idx_ab_metrics_variation_id ON product_description_ab_metrics(variation_id);
CREATE INDEX IF NOT EXISTS idx_ab_metrics_date ON product_description_ab_metrics(date_recorded);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_product_description_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_product_descriptions_updated_at
    BEFORE UPDATE ON product_descriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_product_description_updated_at();

-- Vista para estadísticas de descripciones
CREATE OR REPLACE VIEW product_descriptions_stats AS
SELECT 
    platform,
    status,
    COUNT(*) as total_descriptions,
    AVG(word_count) as avg_word_count,
    SUM(tokens_used) as total_tokens_used,
    MAX(created_at) as last_created
FROM product_descriptions
GROUP BY platform, status;

-- Vista para métricas de A/B testing
CREATE OR REPLACE VIEW product_description_ab_summary AS
SELECT 
    pd.product_name,
    pdv.variation_type,
    pdv.variation_id,
    SUM(pdam.views) as total_views,
    SUM(pdam.clicks) as total_clicks,
    SUM(pdam.conversions) as total_conversions,
    SUM(pdam.revenue) as total_revenue,
    CASE 
        WHEN SUM(pdam.views) > 0 
        THEN SUM(pdam.conversions)::DECIMAL / SUM(pdam.views)::DECIMAL 
        ELSE 0 
    END as overall_conversion_rate
FROM product_descriptions pd
JOIN product_description_variations pdv ON pd.product_description_id = pdv.product_description_id
LEFT JOIN product_description_ab_metrics pdam ON pdv.variation_id = pdam.variation_id
GROUP BY pd.product_name, pdv.variation_type, pdv.variation_id
ORDER BY overall_conversion_rate DESC;

-- Comentarios en tablas
COMMENT ON TABLE product_descriptions IS 'Descripciones de productos generadas con IA';
COMMENT ON TABLE product_description_variations IS 'Variaciones de descripciones para A/B testing';
COMMENT ON TABLE product_descriptions_cache IS 'Caché de descripciones generadas para evitar regeneraciones';
COMMENT ON TABLE product_description_ab_metrics IS 'Métricas de rendimiento de variaciones en A/B testing';




