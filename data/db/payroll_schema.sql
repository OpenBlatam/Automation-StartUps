-- ============================================================================
-- Schema para Procesamiento de Nómina y Gastos
-- Sistema automatizado para calcular horas, deducciones, pagos y procesar recibos
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla de Empleados
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_employees (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) UNIQUE NOT NULL,
    name VARCHAR(256) NOT NULL,
    email VARCHAR(256),
    position VARCHAR(128),
    hourly_rate DECIMAL(10,2) NOT NULL,
    salary_monthly DECIMAL(10,2), -- Si es salario fijo
    employee_type VARCHAR(32) NOT NULL DEFAULT 'hourly' CHECK (employee_type IN ('hourly', 'salaried', 'contractor')),
    tax_rate DECIMAL(5,4) DEFAULT 0.00, -- Tasa de impuestos (ej: 0.25 = 25%)
    benefits_rate DECIMAL(5,4) DEFAULT 0.00, -- Tasa de beneficios (ej: 0.10 = 10%)
    department VARCHAR(128),
    start_date DATE,
    end_date DATE,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB -- Info adicional: beneficios, deducciones personalizadas, etc.
);

CREATE INDEX IF NOT EXISTS idx_payroll_employees_employee_id ON payroll_employees(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_employees_active ON payroll_employees(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_payroll_employees_type ON payroll_employees(employee_type);

-- ============================================================================
-- 2. Tabla de Registro de Horas Trabajadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_time_entries (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    work_date DATE NOT NULL,
    clock_in TIMESTAMPTZ,
    clock_out TIMESTAMPTZ,
    hours_worked DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    hours_type VARCHAR(32) NOT NULL DEFAULT 'regular' CHECK (hours_type IN ('regular', 'overtime', 'double_time', 'holiday', 'sick', 'vacation', 'other')),
    hourly_rate DECIMAL(10,2) NOT NULL,
    description TEXT,
    project_code VARCHAR(128),
    approved BOOLEAN NOT NULL DEFAULT false,
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    UNIQUE(employee_id, work_date, hours_type)
);

CREATE INDEX IF NOT EXISTS idx_payroll_time_entries_employee_id ON payroll_time_entries(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_time_entries_work_date ON payroll_time_entries(work_date);
CREATE INDEX IF NOT EXISTS idx_payroll_time_entries_approved ON payroll_time_entries(approved) WHERE approved = false;
CREATE INDEX IF NOT EXISTS idx_payroll_time_entries_month ON payroll_time_entries(employee_id, work_date);

-- ============================================================================
-- 3. Tabla de Recibos de Gastos (Expense Receipts)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_expense_receipts (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    receipt_number VARCHAR(128) UNIQUE,
    receipt_date DATE,
    expense_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    category VARCHAR(128), -- transporte, comida, hospedaje, etc.
    vendor VARCHAR(256),
    description TEXT,
    receipt_image_url TEXT, -- URL o path a la imagen del recibo
    receipt_image_base64 TEXT, -- Imagen en base64 para OCR
    ocr_status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (ocr_status IN ('pending', 'processing', 'completed', 'failed', 'manual_review')),
    ocr_confidence DECIMAL(5,4), -- Nivel de confianza del OCR (0-1)
    ocr_extracted_data JSONB, -- Datos extraídos por OCR
    ocr_processed_at TIMESTAMPTZ,
    approved BOOLEAN NOT NULL DEFAULT false,
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    reimbursed BOOLEAN NOT NULL DEFAULT false,
    reimbursed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payroll_expense_receipts_employee_id ON payroll_expense_receipts(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_expense_receipts_expense_date ON payroll_expense_receipts(expense_date);
CREATE INDEX IF NOT EXISTS idx_payroll_expense_receipts_ocr_status ON payroll_expense_receipts(ocr_status) WHERE ocr_status IN ('pending', 'processing', 'failed');
CREATE INDEX IF NOT EXISTS idx_payroll_expense_receipts_approved ON payroll_expense_receipts(approved) WHERE approved = false;
CREATE INDEX IF NOT EXISTS idx_payroll_expense_receipts_reimbursed ON payroll_expense_receipts(reimbursed) WHERE reimbursed = false;

-- ============================================================================
-- 4. Tabla de Deducciones
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_deductions (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    deduction_type VARCHAR(64) NOT NULL, -- impuestos, seguro_social, seguro_salud, retiro, otros
    amount DECIMAL(10,2) NOT NULL,
    amount_type VARCHAR(32) NOT NULL DEFAULT 'fixed' CHECK (amount_type IN ('fixed', 'percentage', 'formula')),
    percentage_of DECIMAL(10,2), -- Si es porcentaje, de qué cantidad
    description TEXT,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    applied BOOLEAN NOT NULL DEFAULT false,
    applied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payroll_deductions_employee_id ON payroll_deductions(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_deductions_period ON payroll_deductions(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_payroll_deductions_applied ON payroll_deductions(applied) WHERE applied = false;
CREATE INDEX IF NOT EXISTS idx_payroll_deductions_type ON payroll_deductions(deduction_type);

-- ============================================================================
-- 5. Tabla de Períodos de Pago (Pay Periods)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_pay_periods (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(128) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    pay_date DATE NOT NULL,
    gross_pay DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    regular_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    overtime_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    total_deductions DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_expenses DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    net_pay DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(32) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'calculated', 'reviewed', 'approved', 'paid', 'cancelled')),
    calculated_at TIMESTAMPTZ,
    reviewed_by VARCHAR(128),
    reviewed_at TIMESTAMPTZ,
    approved_by VARCHAR(128),
    approved_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    payment_method VARCHAR(64), -- transfer, check, cash, etc.
    payment_reference VARCHAR(256), -- Referencia de transferencia, número de cheque, etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE,
    UNIQUE(employee_id, period_start, period_end)
);

CREATE INDEX IF NOT EXISTS idx_payroll_pay_periods_employee_id ON payroll_pay_periods(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_periods_period ON payroll_pay_periods(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_periods_status ON payroll_pay_periods(status);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_periods_pay_date ON payroll_pay_periods(pay_date);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_periods_draft ON payroll_pay_periods(status) WHERE status = 'draft';

-- ============================================================================
-- 6. Tabla de Detalle de Cálculos de Pago
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_pay_calculations (
    id SERIAL PRIMARY KEY,
    pay_period_id INT NOT NULL,
    employee_id VARCHAR(128) NOT NULL,
    calculation_type VARCHAR(64) NOT NULL, -- hours, deductions, expenses, adjustments
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,
    quantity DECIMAL(10,2), -- Para horas, cantidad de items, etc.
    unit_rate DECIMAL(10,2), -- Tasa por unidad
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (pay_period_id) REFERENCES payroll_pay_periods(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES payroll_employees(employee_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payroll_pay_calculations_pay_period_id ON payroll_pay_calculations(pay_period_id);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_calculations_employee_id ON payroll_pay_calculations(employee_id);
CREATE INDEX IF NOT EXISTS idx_payroll_pay_calculations_type ON payroll_pay_calculations(calculation_type);

-- ============================================================================
-- 7. Tabla de Configuración de Deducciones (Deduction Rules)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payroll_deduction_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(128) UNIQUE NOT NULL,
    deduction_type VARCHAR(64) NOT NULL,
    employee_type VARCHAR(32), -- NULL = aplica a todos
    amount_type VARCHAR(32) NOT NULL DEFAULT 'percentage' CHECK (amount_type IN ('fixed', 'percentage', 'formula')),
    amount_value DECIMAL(10,2),
    percentage_value DECIMAL(5,4),
    formula TEXT, -- Expresión para calcular (ej: "gross_pay * 0.25")
    conditions JSONB, -- Condiciones adicionales (ej: min_gross_pay, max_amount)
    enabled BOOLEAN NOT NULL DEFAULT true,
    priority INT NOT NULL DEFAULT 0, -- Para orden de aplicación
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_payroll_deduction_rules_enabled ON payroll_deduction_rules(enabled) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_payroll_deduction_rules_type ON payroll_deduction_rules(deduction_type);
CREATE INDEX IF NOT EXISTS idx_payroll_deduction_rules_priority ON payroll_deduction_rules(priority);

-- ============================================================================
-- 8. Vistas Materializadas para Reportes
-- ============================================================================

-- Vista: Resumen de horas por empleado por mes
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_payroll_hours_summary AS
SELECT 
    employee_id,
    DATE_TRUNC('month', work_date) AS month,
    SUM(CASE WHEN hours_type = 'regular' THEN hours_worked ELSE 0 END) AS regular_hours,
    SUM(CASE WHEN hours_type = 'overtime' THEN hours_worked ELSE 0 END) AS overtime_hours,
    SUM(CASE WHEN hours_type = 'double_time' THEN hours_worked ELSE 0 END) AS double_time_hours,
    SUM(hours_worked) AS total_hours,
    COUNT(*) AS entries_count
FROM payroll_time_entries
WHERE approved = true
GROUP BY employee_id, DATE_TRUNC('month', work_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_payroll_hours_summary_unique ON mv_payroll_hours_summary(employee_id, month);

-- Vista: Resumen de gastos por empleado por mes
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_payroll_expenses_summary AS
SELECT 
    employee_id,
    DATE_TRUNC('month', expense_date) AS month,
    COUNT(*) AS receipt_count,
    SUM(amount) AS total_amount,
    SUM(CASE WHEN approved = true THEN amount ELSE 0 END) AS approved_amount,
    SUM(CASE WHEN reimbursed = true THEN amount ELSE 0 END) AS reimbursed_amount
FROM payroll_expense_receipts
GROUP BY employee_id, DATE_TRUNC('month', expense_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_payroll_expenses_summary_unique ON mv_payroll_expenses_summary(employee_id, month);

-- Vista: Resumen de pagos por empleado
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_payroll_payments_summary AS
SELECT 
    employee_id,
    DATE_TRUNC('month', pay_date) AS month,
    COUNT(*) AS pay_periods_count,
    SUM(gross_pay) AS total_gross_pay,
    SUM(total_deductions) AS total_deductions,
    SUM(total_expenses) AS total_expenses,
    SUM(net_pay) AS total_net_pay,
    SUM(CASE WHEN status = 'paid' THEN net_pay ELSE 0 END) AS paid_amount
FROM payroll_pay_periods
GROUP BY employee_id, DATE_TRUNC('month', pay_date);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_payroll_payments_summary_unique ON mv_payroll_payments_summary(employee_id, month);

-- ============================================================================
-- 9. Funciones de Utilidad
-- ============================================================================

-- Función para calcular horas trabajadas desde clock_in/clock_out
CREATE OR REPLACE FUNCTION calculate_hours_from_timestamps(
    clock_in_time TIMESTAMPTZ,
    clock_out_time TIMESTAMPTZ
) RETURNS DECIMAL(6,2) AS $$
BEGIN
    IF clock_in_time IS NULL OR clock_out_time IS NULL THEN
        RETURN 0.00;
    END IF;
    
    RETURN ROUND(
        EXTRACT(EPOCH FROM (clock_out_time - clock_in_time)) / 3600.0,
        2
    );
END;
$$ LANGUAGE plpgsql;

-- Función para refrescar vistas materializadas
CREATE OR REPLACE FUNCTION refresh_payroll_materialized_views() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_payroll_hours_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_payroll_expenses_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_payroll_payments_summary;
END;
$$ LANGUAGE plpgsql;

COMMIT;





