-- Esquema de base de datos para sincronización de datos
-- ======================================================
-- 
-- Tablas para tracking, auditoría y reconciliación de sincronizaciones
-- entre CRM, ERP y hojas de cálculo

-- Tabla de historial de sincronizaciones
CREATE TABLE IF NOT EXISTS sync_history (
    id SERIAL PRIMARY KEY,
    sync_id VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    direction VARCHAR(32) NOT NULL DEFAULT 'bidirectional',
    total_records INTEGER DEFAULT 0,
    successful INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    conflicted INTEGER DEFAULT 0,
    skipped INTEGER DEFAULT 0,
    duration_seconds FLOAT,
    errors JSONB,
    metadata JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_sync_id UNIQUE(sync_id)
);

-- Tabla de registros sincronizados individuales
CREATE TABLE IF NOT EXISTS sync_records (
    id SERIAL PRIMARY KEY,
    sync_history_id INTEGER REFERENCES sync_history(id) ON DELETE CASCADE,
    source_id VARCHAR(256) NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    target_id VARCHAR(256),
    target_type VARCHAR(64),
    checksum VARCHAR(64),
    status VARCHAR(32) NOT NULL,
    error_message TEXT,
    data JSONB,
    metadata JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_sync_record UNIQUE(source_id, source_type, target_type)
);

-- Tabla de mapeo de campos entre sistemas
CREATE TABLE IF NOT EXISTS field_mappings (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(64) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    source_field VARCHAR(128) NOT NULL,
    target_field VARCHAR(128) NOT NULL,
    transformation_function VARCHAR(256),
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    validation_rules JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_field_mapping UNIQUE(source_type, target_type, source_field, target_field)
);

-- Tabla de configuración de sincronizaciones recurrentes
CREATE TABLE IF NOT EXISTS sync_schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    source_type VARCHAR(64) NOT NULL,
    target_type VARCHAR(64) NOT NULL,
    direction VARCHAR(32) NOT NULL DEFAULT 'bidirectional',
    schedule_cron VARCHAR(64),
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de conflictos pendientes de resolución
CREATE TABLE IF NOT EXISTS sync_conflicts (
    id SERIAL PRIMARY KEY,
    sync_record_id INTEGER REFERENCES sync_records(id) ON DELETE CASCADE,
    source_data JSONB NOT NULL,
    target_data JSONB NOT NULL,
    conflict_type VARCHAR(64) NOT NULL,
    conflict_fields JSONB,
    resolution_strategy VARCHAR(64),
    resolved_by VARCHAR(128),
    resolved_at TIMESTAMPTZ,
    resolution_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de métricas de performance
CREATE TABLE IF NOT EXISTS sync_metrics (
    id SERIAL PRIMARY KEY,
    sync_history_id INTEGER REFERENCES sync_history(id) ON DELETE CASCADE,
    metric_name VARCHAR(128) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(32),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_sync_metric UNIQUE(sync_history_id, metric_name, recorded_at)
);

-- Índices para optimización de consultas
CREATE INDEX IF NOT EXISTS idx_sync_history_sync_id ON sync_history(sync_id);
CREATE INDEX IF NOT EXISTS idx_sync_history_status ON sync_history(status);
CREATE INDEX IF NOT EXISTS idx_sync_history_started_at ON sync_history(started_at);
CREATE INDEX IF NOT EXISTS idx_sync_history_source_target ON sync_history(source_type, target_type);

CREATE INDEX IF NOT EXISTS idx_sync_records_source ON sync_records(source_id, source_type);
CREATE INDEX IF NOT EXISTS idx_sync_records_target ON sync_records(target_id, target_type);
CREATE INDEX IF NOT EXISTS idx_sync_records_checksum ON sync_records(checksum);
CREATE INDEX IF NOT EXISTS idx_sync_records_status ON sync_records(status);
CREATE INDEX IF NOT EXISTS idx_sync_records_synced_at ON sync_records(synced_at);
CREATE INDEX IF NOT EXISTS idx_sync_records_history_id ON sync_records(sync_history_id);

CREATE INDEX IF NOT EXISTS idx_field_mappings_source_target ON field_mappings(source_type, target_type);

CREATE INDEX IF NOT EXISTS idx_sync_schedules_enabled ON sync_schedules(enabled);
CREATE INDEX IF NOT EXISTS idx_sync_schedules_next_run ON sync_schedules(next_run_at);

CREATE INDEX IF NOT EXISTS idx_sync_conflicts_resolved ON sync_conflicts(resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_sync_conflicts_sync_record ON sync_conflicts(sync_record_id);

CREATE INDEX IF NOT EXISTS idx_sync_metrics_history ON sync_metrics(sync_history_id);
CREATE INDEX IF NOT EXISTS idx_sync_metrics_recorded_at ON sync_metrics(recorded_at);

-- Vistas útiles

-- Vista de resumen de sincronizaciones
CREATE OR REPLACE VIEW sync_summary AS
SELECT 
    DATE_TRUNC('day', started_at) as sync_date,
    source_type,
    target_type,
    status,
    COUNT(*) as sync_count,
    SUM(total_records) as total_records,
    SUM(successful) as total_successful,
    SUM(failed) as total_failed,
    SUM(conflicted) as total_conflicted,
    AVG(duration_seconds) as avg_duration_seconds,
    MAX(duration_seconds) as max_duration_seconds
FROM sync_history
GROUP BY DATE_TRUNC('day', started_at), source_type, target_type, status;

-- Vista de registros con conflictos
CREATE OR REPLACE VIEW sync_conflicts_view AS
SELECT 
    sc.id as conflict_id,
    sr.source_id,
    sr.source_type,
    sr.target_id,
    sr.target_type,
    sc.conflict_type,
    sc.conflict_fields,
    sc.resolution_strategy,
    sc.resolved_at,
    sc.created_at as conflict_created_at,
    sh.sync_id,
    sh.started_at as sync_started_at
FROM sync_conflicts sc
JOIN sync_records sr ON sc.sync_record_id = sr.id
JOIN sync_history sh ON sr.sync_history_id = sh.id
WHERE sc.resolved_at IS NULL;

-- Vista de performance por tipo de sincronización
CREATE OR REPLACE VIEW sync_performance_view AS
SELECT 
    source_type,
    target_type,
    DATE_TRUNC('hour', started_at) as hour_bucket,
    COUNT(*) as sync_count,
    AVG(duration_seconds) as avg_duration,
    AVG(successful::float / NULLIF(total_records, 0)) * 100 as success_rate,
    AVG(failed::float / NULLIF(total_records, 0)) * 100 as failure_rate
FROM sync_history
WHERE completed_at IS NOT NULL
GROUP BY source_type, target_type, DATE_TRUNC('hour', started_at);

-- Comentarios en tablas
COMMENT ON TABLE sync_history IS 'Historial completo de todas las sincronizaciones ejecutadas';
COMMENT ON TABLE sync_records IS 'Registros individuales sincronizados entre sistemas';
COMMENT ON TABLE field_mappings IS 'Mapeo de campos entre diferentes sistemas';
COMMENT ON TABLE sync_schedules IS 'Configuración de sincronizaciones programadas';
COMMENT ON TABLE sync_conflicts IS 'Conflictos detectados durante sincronización que requieren resolución manual';
COMMENT ON TABLE sync_metrics IS 'Métricas de performance de sincronizaciones';


