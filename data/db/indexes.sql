-- Payments indexes
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments (created_at);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments (status);
CREATE INDEX IF NOT EXISTS idx_payments_created_status ON payments (created_at, status);

-- Leads indexes
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads (created_at);
CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads (priority);

-- KPI daily primary key already set on day; ensure btree
CREATE INDEX IF NOT EXISTS idx_kpi_daily_day ON kpi_daily (day);


