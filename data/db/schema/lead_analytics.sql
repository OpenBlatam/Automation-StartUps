-- Schema para analytics y mejoras de leads

-- Tabla de analytics de leads
CREATE TABLE IF NOT EXISTS lead_analytics (
    analytics_id SERIAL PRIMARY KEY,
    lead_ext_id VARCHAR(255) UNIQUE NOT NULL,
    analytics_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_analytics_ext_id ON lead_analytics(lead_ext_id);
CREATE INDEX IF NOT EXISTS idx_lead_analytics_created ON lead_analytics(created_at);

-- Tabla de caché de leads (para evitar duplicados)
CREATE TABLE IF NOT EXISTS lead_cache (
    cache_key VARCHAR(32) PRIMARY KEY,
    cache_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lead_cache_created ON lead_cache(created_at);

-- Vista de analytics consolidado
CREATE OR REPLACE VIEW lead_analytics_summary AS
SELECT 
    l.ext_id,
    l.email,
    l.source,
    l.score,
    l.priority,
    (la.analytics_data->>'spam_score')::INTEGER as spam_score,
    (la.analytics_data->>'is_spam')::BOOLEAN as is_spam,
    la.analytics_data->>'scoring_method' as scoring_method,
    la.created_at as analytics_created_at
FROM leads l
LEFT JOIN lead_analytics la ON l.ext_id = la.lead_ext_id
ORDER BY la.created_at DESC;

-- Función para limpiar caché antiguo
CREATE OR REPLACE FUNCTION cleanup_old_lead_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM lead_cache
    WHERE created_at < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;






