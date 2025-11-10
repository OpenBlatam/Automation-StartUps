-- ============================================================================
-- Schema para Sistema de Gestión de Tiempo y Asistencia
-- Registro automático de entradas/salidas, cálculo de horas, gestión de vacaciones y permisos
-- Reduce errores y disputas de tiempo trabajado
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Registros de Entrada/Salida (Clock In/Out)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_clock_events (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    event_type VARCHAR(32) NOT NULL CHECK (event_type IN ('clock_in', 'clock_out', 'break_start', 'break_end')),
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    location VARCHAR(256), -- GPS, dirección IP, nombre de oficina, etc.
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    device_type VARCHAR(64), -- 'mobile', 'web', 'kiosk', 'api', 'biometric'
    device_id VARCHAR(256),
    ip_address VARCHAR(45), -- IPv4 o IPv6
    notes TEXT,
    auto_detected BOOLEAN DEFAULT false, -- Si fue detectado automáticamente (geofencing, etc.)
    verified BOOLEAN DEFAULT false, -- Si fue verificado por supervisor
    verified_by VARCHAR(128),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB, -- Info adicional: fotos, huellas, etc.
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_clock_events_employee_id ON time_tracking_clock_events(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_clock_events_event_time ON time_tracking_clock_events(event_time);
CREATE INDEX IF NOT EXISTS idx_time_tracking_clock_events_event_type ON time_tracking_clock_events(event_type);
CREATE INDEX IF NOT EXISTS idx_time_tracking_clock_events_date ON time_tracking_clock_events(employee_id, DATE(event_time));
CREATE INDEX IF NOT EXISTS idx_time_tracking_clock_events_unverified ON time_tracking_clock_events(verified) WHERE verified = false;

-- ============================================================================
-- 2. Tabla de Sesiones de Trabajo (Work Sessions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_work_sessions (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    work_date DATE NOT NULL,
    clock_in_event_id INT NOT NULL,
    clock_out_event_id INT,
    clock_in_time TIMESTAMPTZ NOT NULL,
    clock_out_time TIMESTAMPTZ,
    break_duration_minutes INT DEFAULT 0, -- Duración total de breaks en minutos
    total_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    regular_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    overtime_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    double_time_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    hours_type VARCHAR(32) NOT NULL DEFAULT 'regular' CHECK (hours_type IN ('regular', 'overtime', 'double_time', 'holiday', 'sick', 'vacation', 'other')),
    status VARCHAR(32) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'disputed', 'approved', 'rejected')),
    auto_closed BOOLEAN DEFAULT false, -- Si se cerró automáticamente (por ejemplo, al día siguiente)
    notes TEXT,
    approved BOOLEAN NOT NULL DEFAULT false,
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    disputed BOOLEAN NOT NULL DEFAULT false,
    dispute_reason TEXT,
    dispute_resolved BOOLEAN DEFAULT false,
    dispute_resolved_by VARCHAR(128),
    dispute_resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (clock_in_event_id) REFERENCES time_tracking_clock_events(id) ON DELETE CASCADE,
    FOREIGN KEY (clock_out_event_id) REFERENCES time_tracking_clock_events(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_employee_id ON time_tracking_work_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_work_date ON time_tracking_work_sessions(work_date);
CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_status ON time_tracking_work_sessions(status);
CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_open ON time_tracking_work_sessions(status) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_disputed ON time_tracking_work_sessions(disputed) WHERE disputed = true;
CREATE INDEX IF NOT EXISTS idx_time_tracking_work_sessions_unapproved ON time_tracking_work_sessions(approved) WHERE approved = false;

-- ============================================================================
-- 3. Tabla de Breaks (Descansos)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_breaks (
    id SERIAL PRIMARY KEY,
    work_session_id INT NOT NULL,
    employee_id VARCHAR(128) NOT NULL,
    break_type VARCHAR(32) NOT NULL CHECK (break_type IN ('lunch', 'coffee', 'rest', 'other')),
    break_start_event_id INT NOT NULL,
    break_end_event_id INT,
    break_start_time TIMESTAMPTZ NOT NULL,
    break_end_time TIMESTAMPTZ,
    duration_minutes INT,
    paid BOOLEAN DEFAULT false, -- Si el break es pagado
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (work_session_id) REFERENCES time_tracking_work_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (break_start_event_id) REFERENCES time_tracking_clock_events(id) ON DELETE CASCADE,
    FOREIGN KEY (break_end_event_id) REFERENCES time_tracking_clock_events(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_breaks_work_session_id ON time_tracking_breaks(work_session_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_breaks_employee_id ON time_tracking_breaks(employee_id);

-- ============================================================================
-- 4. Tabla de Vacaciones (Vacations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_vacations (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    vacation_type VARCHAR(32) NOT NULL CHECK (vacation_type IN ('vacation', 'sick', 'personal', 'bereavement', 'jury_duty', 'military', 'other')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested DECIMAL(5,2) NOT NULL, -- Días solicitados (puede ser medio día)
    days_approved DECIMAL(5,2), -- Días aprobados
    status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled', 'taken')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    requested_by VARCHAR(128), -- Puede ser diferente al employee_id si es por HR
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    rejected_by VARCHAR(128),
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_vacations_employee_id ON time_tracking_vacations(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_vacations_dates ON time_tracking_vacations(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_time_tracking_vacations_status ON time_tracking_vacations(status);
CREATE INDEX IF NOT EXISTS idx_time_tracking_vacations_pending ON time_tracking_vacations(status) WHERE status = 'pending';

-- ============================================================================
-- 5. Tabla de Permisos (Leave Requests)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    leave_type VARCHAR(32) NOT NULL CHECK (leave_type IN ('medical', 'family', 'educational', 'unpaid', 'other')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME, -- Si es medio día o horas específicas
    end_time TIME,
    hours_requested DECIMAL(6,2),
    status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    requested_by VARCHAR(128),
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    rejected_by VARCHAR(128),
    rejected_at TIMESTAMPTZ,
    rejection_reason TEXT,
    notes TEXT,
    documentation_url TEXT, -- URL a documentación médica, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    CHECK (end_date >= start_date)
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_leave_requests_employee_id ON time_tracking_leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_leave_requests_dates ON time_tracking_leave_requests(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_time_tracking_leave_requests_status ON time_tracking_leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_time_tracking_leave_requests_pending ON time_tracking_leave_requests(status) WHERE status = 'pending';

-- ============================================================================
-- 6. Tabla de Saldo de Vacaciones (Vacation Balance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_vacation_balances (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL UNIQUE,
    vacation_days_accrued DECIMAL(6,2) NOT NULL DEFAULT 0.00, -- Días acumulados
    vacation_days_used DECIMAL(6,2) NOT NULL DEFAULT 0.00, -- Días usados
    vacation_days_available DECIMAL(6,2) NOT NULL DEFAULT 0.00, -- Días disponibles
    sick_days_accrued DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    sick_days_used DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    sick_days_available DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    personal_days_accrued DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    personal_days_used DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    personal_days_available DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    last_accrual_date DATE, -- Última fecha de acumulación
    accrual_rate DECIMAL(5,2), -- Días por período (ej: 1.25 días/mes)
    accrual_period VARCHAR(32), -- 'monthly', 'biweekly', 'weekly', 'yearly'
    year INT NOT NULL, -- Año del saldo
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_vacation_balances_employee_id ON time_tracking_vacation_balances(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_vacation_balances_year ON time_tracking_vacation_balances(year);

-- ============================================================================
-- 7. Tabla de Disputas de Tiempo (Time Disputes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_disputes (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    work_session_id INT,
    time_entry_id INT, -- Referencia a payroll_time_entries si aplica
    dispute_type VARCHAR(32) NOT NULL CHECK (dispute_type IN ('missing_clock', 'incorrect_time', 'missing_break', 'overtime_calculation', 'other')),
    dispute_date DATE NOT NULL,
    description TEXT NOT NULL,
    requested_hours DECIMAL(6,2),
    current_hours DECIMAL(6,2),
    status VARCHAR(32) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'under_review', 'resolved', 'rejected', 'cancelled')),
    priority VARCHAR(32) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_by VARCHAR(128),
    reviewed_by VARCHAR(128),
    reviewed_at TIMESTAMPTZ,
    resolved_by VARCHAR(128),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    resolution_action VARCHAR(32), -- 'approved', 'adjusted', 'rejected', 'forwarded'
    evidence_urls JSONB, -- Array de URLs a evidencia (screenshots, logs, etc.)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (work_session_id) REFERENCES time_tracking_work_sessions(id) ON DELETE SET NULL,
    FOREIGN KEY (time_entry_id) REFERENCES payroll_time_entries(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_disputes_employee_id ON time_tracking_disputes(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_disputes_status ON time_tracking_disputes(status);
CREATE INDEX IF NOT EXISTS idx_time_tracking_disputes_open ON time_tracking_disputes(status) WHERE status IN ('open', 'under_review');
CREATE INDEX IF NOT EXISTS idx_time_tracking_disputes_date ON time_tracking_disputes(dispute_date);

-- ============================================================================
-- 8. Tabla de Configuración de Horarios (Schedule Configuration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_schedules (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128),
    schedule_name VARCHAR(128) NOT NULL,
    schedule_type VARCHAR(32) NOT NULL CHECK (schedule_type IN ('fixed', 'flexible', 'shift', 'remote')),
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Monday, 6=Sunday, NULL = todos los días
    start_time TIME,
    end_time TIME,
    break_duration_minutes INT DEFAULT 30,
    required_hours DECIMAL(5,2), -- Horas requeridas por día
    timezone VARCHAR(64) DEFAULT 'UTC',
    is_active BOOLEAN NOT NULL DEFAULT true,
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_schedules_employee_id ON time_tracking_schedules(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_schedules_active ON time_tracking_schedules(is_active) WHERE is_active = true;

-- ============================================================================
-- 9. Tabla de Alertas y Notificaciones de Tiempo
-- ============================================================================
CREATE TABLE IF NOT EXISTS time_tracking_alerts (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128),
    alert_type VARCHAR(64) NOT NULL CHECK (alert_type IN (
        'missing_clock_in', 'missing_clock_out', 'late_clock_in', 'early_clock_out',
        'missing_break', 'long_break', 'overtime_warning', 'discrepancy_detected',
        'vacation_balance_low', 'leave_pending_approval', 'dispute_submitted'
    )),
    alert_severity VARCHAR(32) NOT NULL DEFAULT 'info' CHECK (alert_severity IN ('info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    related_entity_type VARCHAR(32), -- 'work_session', 'vacation', 'dispute', etc.
    related_entity_id INT,
    status VARCHAR(32) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved', 'dismissed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(128),
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(128),
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_alerts_employee_id ON time_tracking_alerts(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_alerts_status ON time_tracking_alerts(status);
CREATE INDEX IF NOT EXISTS idx_time_tracking_alerts_active ON time_tracking_alerts(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_time_tracking_alerts_type ON time_tracking_alerts(alert_type);

-- ============================================================================
-- 10. Funciones de Utilidad
-- ============================================================================

-- Función para calcular horas trabajadas desde clock in/out
CREATE OR REPLACE FUNCTION calculate_session_hours(
    clock_in_time TIMESTAMPTZ,
    clock_out_time TIMESTAMPTZ,
    break_minutes INT DEFAULT 0
) RETURNS DECIMAL(6,2) AS $$
BEGIN
    IF clock_in_time IS NULL OR clock_out_time IS NULL THEN
        RETURN 0.00;
    END IF;
    
    RETURN GREATEST(0, ROUND(
        (EXTRACT(EPOCH FROM (clock_out_time - clock_in_time)) / 3600.0) - (break_minutes / 60.0),
        2
    ));
END;
$$ LANGUAGE plpgsql;

-- Función para detectar sesiones abiertas (sin clock out)
CREATE OR REPLACE FUNCTION detect_open_sessions(
    p_employee_id VARCHAR(128),
    p_max_hours_ago INT DEFAULT 24
) RETURNS TABLE (
    session_id INT,
    employee_id VARCHAR(128),
    clock_in_time TIMESTAMPTZ,
    hours_open DECIMAL(6,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ws.id,
        ws.employee_id,
        ws.clock_in_time,
        calculate_session_hours(ws.clock_in_time, NOW(), COALESCE(ws.break_duration_minutes, 0)) as hours_open
    FROM time_tracking_work_sessions ws
    WHERE ws.employee_id = p_employee_id
        AND ws.status = 'open'
        AND ws.clock_out_time IS NULL
        AND ws.clock_in_time >= NOW() - (p_max_hours_ago || ' hours')::INTERVAL
    ORDER BY ws.clock_in_time DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para cerrar automáticamente sesiones abiertas
CREATE OR REPLACE FUNCTION auto_close_stale_sessions(
    p_max_hours_open INT DEFAULT 24
) RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    UPDATE time_tracking_work_sessions
    SET 
        status = 'closed',
        clock_out_time = clock_in_time + (p_max_hours_open || ' hours')::INTERVAL,
        auto_closed = true,
        updated_at = NOW()
    WHERE status = 'open'
        AND clock_out_time IS NULL
        AND clock_in_time < NOW() - (p_max_hours_open || ' hours')::INTERVAL;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular saldo de vacaciones
CREATE OR REPLACE FUNCTION calculate_vacation_balance(
    p_employee_id VARCHAR(128),
    p_year INT DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)
) RETURNS TABLE (
    vacation_days_available DECIMAL(6,2),
    sick_days_available DECIMAL(6,2),
    personal_days_available DECIMAL(6,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(vb.vacation_days_available, 0) as vacation_days_available,
        COALESCE(vb.sick_days_available, 0) as sick_days_available,
        COALESCE(vb.personal_days_available, 0) as personal_days_available
    FROM time_tracking_vacation_balances vb
    WHERE vb.employee_id = p_employee_id
        AND vb.year = p_year;
    
    -- Si no existe registro, retornar ceros
    IF NOT FOUND THEN
        RETURN QUERY SELECT 0.00, 0.00, 0.00;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 11. Vistas Materializadas para Reportes
-- ============================================================================

-- Vista: Resumen diario de asistencia por empleado
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_time_tracking_daily_summary AS
SELECT 
    ws.employee_id,
    ws.work_date,
    COUNT(DISTINCT ws.id) as sessions_count,
    SUM(ws.total_hours) as total_hours,
    SUM(ws.regular_hours) as regular_hours,
    SUM(ws.overtime_hours) as overtime_hours,
    SUM(ws.break_duration_minutes) / 60.0 as break_hours,
    MIN(ws.clock_in_time) as first_clock_in,
    MAX(ws.clock_out_time) as last_clock_out,
    COUNT(DISTINCT CASE WHEN ws.status = 'disputed' THEN ws.id END) as disputed_sessions,
    COUNT(DISTINCT CASE WHEN ws.approved = false THEN ws.id END) as unapproved_sessions
FROM time_tracking_work_sessions ws
GROUP BY ws.employee_id, ws.work_date;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_time_tracking_daily_summary_unique ON mv_time_tracking_daily_summary(employee_id, work_date);

-- Vista: Resumen mensual de asistencia
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_time_tracking_monthly_summary AS
SELECT 
    employee_id,
    DATE_TRUNC('month', work_date)::DATE as month,
    COUNT(DISTINCT work_date) as days_worked,
    SUM(total_hours) as total_hours,
    SUM(regular_hours) as regular_hours,
    SUM(overtime_hours) as overtime_hours,
    AVG(total_hours) as avg_daily_hours,
    COUNT(DISTINCT disputed_sessions) as disputed_days
FROM mv_time_tracking_daily_summary
GROUP BY employee_id, DATE_TRUNC('month', work_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_time_tracking_monthly_summary_unique ON mv_time_tracking_monthly_summary(employee_id, month);

-- Función para refrescar vistas materializadas
CREATE OR REPLACE FUNCTION refresh_time_tracking_materialized_views() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_time_tracking_daily_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_time_tracking_monthly_summary;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 12. Triggers para Actualización Automática
-- ============================================================================

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_time_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_time_tracking_clock_events_updated_at
    BEFORE UPDATE ON time_tracking_clock_events
    FOR EACH ROW
    EXECUTE FUNCTION update_time_tracking_updated_at();

CREATE TRIGGER trigger_time_tracking_work_sessions_updated_at
    BEFORE UPDATE ON time_tracking_work_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_time_tracking_updated_at();

CREATE TRIGGER trigger_time_tracking_vacations_updated_at
    BEFORE UPDATE ON time_tracking_vacations
    FOR EACH ROW
    EXECUTE FUNCTION update_time_tracking_updated_at();

CREATE TRIGGER trigger_time_tracking_leave_requests_updated_at
    BEFORE UPDATE ON time_tracking_leave_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_time_tracking_updated_at();

-- ============================================================================
-- 13. Tablas Adicionales para Mejoras
-- ============================================================================

-- Tabla de Ubicaciones Autorizadas (Geofencing)
CREATE TABLE IF NOT EXISTS time_tracking_authorized_locations (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128), -- NULL = aplica a todos los empleados
    location_name VARCHAR(256) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    allowed_radius_km DECIMAL(6,2) DEFAULT 0.5, -- Radio permitido en kilómetros
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_authorized_locations_employee_id 
    ON time_tracking_authorized_locations(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_authorized_locations_active 
    ON time_tracking_authorized_locations(is_active) WHERE is_active = true;

-- Tabla de Días Festivos
CREATE TABLE IF NOT EXISTS time_tracking_holidays (
    id SERIAL PRIMARY KEY,
    holiday_date DATE NOT NULL,
    holiday_name VARCHAR(256) NOT NULL,
    employee_id VARCHAR(128), -- NULL = aplica a todos los empleados
    is_paid BOOLEAN DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    UNIQUE(holiday_date, employee_id)
);

CREATE INDEX IF NOT EXISTS idx_time_tracking_holidays_date 
    ON time_tracking_holidays(holiday_date);
CREATE INDEX IF NOT EXISTS idx_time_tracking_holidays_employee_id 
    ON time_tracking_holidays(employee_id);
CREATE INDEX IF NOT EXISTS idx_time_tracking_holidays_active 
    ON time_tracking_holidays(is_active) WHERE is_active = true;

COMMIT;

