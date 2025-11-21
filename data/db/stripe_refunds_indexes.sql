-- Índices optimizados para la tabla stripe_refunds
-- Mejora el rendimiento de consultas frecuentes

-- Índice para búsquedas por stripe_refund_id (ya tiene UNIQUE, pero este ayuda en lookups)
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_refund_id ON stripe_refunds(stripe_refund_id);

-- Índice para búsquedas por charge_id (para lookup desde payments)
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_charge_id ON stripe_refunds(stripe_charge_id) WHERE stripe_charge_id IS NOT NULL;

-- Índice para búsquedas por customer_email
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_customer_email ON stripe_refunds(customer_email);

-- Índice para búsquedas por qb_receipt_id
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_qb_receipt_id ON stripe_refunds(qb_receipt_id);

-- Índice para búsquedas por qb_credit_id
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_qb_credit_id ON stripe_refunds(qb_credit_id) WHERE qb_credit_id IS NOT NULL;

-- Índice para filtros por status (muy común en queries)
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_status ON stripe_refunds(status);

-- Índice compuesto para búsquedas por estado y fecha (reportes)
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_status_created_at ON stripe_refunds(status, created_at DESC);

-- Índice para búsquedas por fecha de procesamiento
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_processed_at ON stripe_refunds(processed_at) WHERE processed_at IS NOT NULL;

-- Índice GIN para búsquedas en metadata JSONB
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_metadata_gin ON stripe_refunds USING GIN(metadata) WHERE metadata IS NOT NULL;

-- Índice para búsquedas por rango de fechas (útil para reportes)
CREATE INDEX IF NOT EXISTS idx_stripe_refunds_created_at_date ON stripe_refunds(created_at);



