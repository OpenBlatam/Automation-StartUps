CREATE TABLE IF NOT EXISTS payments (
	payment_id VARCHAR(128) PRIMARY KEY,
	amount NUMERIC(12,2) NOT NULL,
	currency VARCHAR(8) NOT NULL,
	customer VARCHAR(256),
	status VARCHAR(64),
	method VARCHAR(64),
	metadata JSONB,
	created_at TIMESTAMP NOT NULL,
	updated_at TIMESTAMP
);
