CREATE TABLE IF NOT EXISTS leads (
	ext_id VARCHAR(128) PRIMARY KEY,
	source VARCHAR(32) NOT NULL,
	first_name VARCHAR(128),
	last_name VARCHAR(128),
	email VARCHAR(256),
	phone VARCHAR(64),
	score INT,
	priority VARCHAR(16),
	utm_source VARCHAR(128),
	utm_campaign VARCHAR(128),
	created_at TIMESTAMP DEFAULT NOW(),
	updated_at TIMESTAMP
);


