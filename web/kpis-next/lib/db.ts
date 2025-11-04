import { Pool } from 'pg';

const pgHost = process.env.KPIS_PG_HOST || 'localhost';
const pgDb = process.env.KPIS_PG_DB || 'analytics';
const pgUser = process.env.KPIS_PG_USER || 'analytics';
const pgPassword = process.env.KPIS_PG_PASSWORD || '';
const pgPort = Number(process.env.KPIS_PG_PORT || 5432);
const poolSize = Number(process.env.KPIS_PG_POOL || 10);
const statementTimeoutMs = Number(process.env.KPIS_PG_STMT_TIMEOUT_MS || 5000);

export const pool = new Pool({
	host: pgHost,
	database: pgDb,
	user: pgUser,
	password: pgPassword,
	port: pgPort,
	max: poolSize,
	statement_timeout: statementTimeoutMs
});
