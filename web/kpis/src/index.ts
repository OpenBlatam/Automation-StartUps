import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import client from 'prom-client';
import dotenv from 'dotenv';
import { cleanEnv, str, num, bool } from 'envalid';

dotenv.config();

const env = cleanEnv(process.env, {
	PORT: num({ default: 3001 }),
	DATABASE_URL: str({ default: '' }),
	KPIS_PG_HOST: str({ default: 'localhost' }),
	KPIS_PG_DB: str({ default: 'analytics' }),
	KPIS_PG_USER: str({ default: 'analytics' }),
	KPIS_PG_PASSWORD: str({ default: '' }),
	ENABLE_RATE_LIMIT: bool({ default: true }),
});
import { Pool } from 'pg';

const port = env.PORT;
const pgHost = env.KPIS_PG_HOST;
const pgDb = env.KPIS_PG_DB;
const pgUser = env.KPIS_PG_USER;
const pgPassword = env.KPIS_PG_PASSWORD;

const pool = env.DATABASE_URL
	? new Pool({ connectionString: env.DATABASE_URL })
	: new Pool({ host: pgHost, database: pgDb, user: pgUser, password: pgPassword, port: 5432 });

const app = express();
app.use(helmet());
app.use(cors({ origin: true }));
app.use(morgan('tiny'));
app.use(express.json());

// Rate limiting (simple global limiter)
if (env.ENABLE_RATE_LIMIT) {
	const limiter = rateLimit({ windowMs: 60_000, max: 300 });
	app.use(limiter);
}

// Prometheus metrics
client.collectDefaultMetrics();
const httpHistogram = new client.Histogram({
	name: 'http_request_duration_seconds',
	help: 'HTTP request duration in seconds',
	labelNames: ['method', 'route', 'status'],
	buckets: [0.05, 0.1, 0.2, 0.5, 1, 2, 5]
});

app.use((req, res, next) => {
	const start = process.hrtime.bigint();
	res.on('finish', () => {
		const end = process.hrtime.bigint();
		const duration = Number(end - start) / 1e9;
		const route = req.route?.path || req.path || 'unknown';
		httpHistogram.labels(req.method, route, String(res.statusCode)).observe(duration);
	});
	next();
});

app.get('/metrics', async (_req, res) => {
	res.set('Content-Type', client.register.contentType);
	res.end(await client.register.metrics());
});

app.get('/healthz', async (_req, res) => {
    try {
        await pool.query('SELECT 1');
        res.status(200).json({ status: 'ok' });
    } catch (e: any) {
        res.status(500).json({ status: 'error', message: e.message || 'db error' });
    }
});

app.get('/api/kpi/timeseries', async (_req, res) => {
    try {
        const q = await pool.query(
            "SELECT date_trunc('hour', created_at) AS time, COALESCE(SUM(amount),0) AS revenue FROM payments WHERE created_at >= NOW() - interval '24 hours' GROUP BY 1 ORDER BY 1"
        );
        const data = q.rows.map((r: any) => ({ time: r.time, revenue: Number(r.revenue) }));
        res.json(data);
    } catch (e: any) {
        res.status(500).json({ error: e.message || 'error' });
    }
});

async function getSummary() {
	const client = await pool.connect();
	try {
		const lastHour = await client.query(
			"SELECT COALESCE(SUM(amount),0) AS revenue FROM payments WHERE created_at >= NOW() - interval '1 hour' AND status IN ('succeeded','paid','payment_intent.succeeded')"
		);
		const last24h = await client.query(
			"SELECT COALESCE(SUM(amount),0) AS revenue FROM payments WHERE created_at >= NOW() - interval '24 hours' AND status IN ('succeeded','paid','payment_intent.succeeded')"
		);
		const leadsToday = await client.query(
			"SELECT priority, COUNT(*)::int AS count FROM leads WHERE created_at::date = CURRENT_DATE GROUP BY 1"
		);
		const paymentsRecent = await client.query(
			"SELECT created_at, payment_id, amount, currency, customer, status, method FROM payments ORDER BY created_at DESC LIMIT 20"
		);
		const leadsRecent = await client.query(
			"SELECT created_at, ext_id, first_name, last_name, email, score, priority FROM leads ORDER BY created_at DESC LIMIT 20"
		);
		return {
			revenue_last_hour: Number(lastHour.rows[0]?.revenue || 0),
			revenue_24h: Number(last24h.rows[0]?.revenue || 0),
			leads_by_priority_today: leadsToday.rows,
			payments_recent: paymentsRecent.rows,
			leads_recent: leadsRecent.rows
		};
	} finally {
		client.release();
	}
}

app.get('/api/kpi/summary', async (_req, res) => {
	try {
		const data = await getSummary();
		res.json(data);
	} catch (e: any) {
		res.status(500).json({ error: e.message || 'error' });
	}
});

app.get('/', async (_req, res) => {
	try {
		const data = await getSummary();
		const leadsPie = data.leads_by_priority_today
			.map((r: any) => `${r.priority || 'unknown'}: ${r.count}`)
			.join(' | ');
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(`<!doctype html>
<html><head><meta charset="utf-8"/><title>KPIs</title>
<style>body{font-family:system-ui,Arial;margin:24px} .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:6px;font-size:12px}</style>
</head><body>
<h1>KPIs en tiempo real</h1>
<div class="grid">
	<div><h3>Ingresos (última hora)</h3><div style="font-size:28px">$ ${data.revenue_last_hour.toFixed(2)}</div></div>
	<div><h3>Ingresos (24h)</h3><div style="font-size:28px">$ ${data.revenue_24h.toFixed(2)}</div></div>
	<div><h3>Leads por prioridad (hoy)</h3><div>${leadsPie}</div></div>
</div>
<h3>Pagos recientes</h3>
<table><thead><tr><th>Fecha</th><th>ID</th><th>Monto</th><th>Moneda</th><th>Cliente</th><th>Status</th><th>Método</th></tr></thead>
<tbody>
${data.payments_recent.map((p: any) => `<tr><td>${p.created_at}</td><td>${p.payment_id}</td><td>${p.amount}</td><td>${p.currency}</td><td>${p.customer||''}</td><td>${p.status}</td><td>${p.method||''}</td></tr>`).join('')}
</tbody></table>

<h3>Leads recientes</h3>
<table><thead><tr><th>Fecha</th><th>ID</th><th>Nombre</th><th>Email</th><th>Score</th><th>Prioridad</th></tr></thead>
<tbody>
${data.leads_recent.map((l: any) => `<tr><td>${l.created_at}</td><td>${l.ext_id}</td><td>${(l.first_name||'')+' '+(l.last_name||'')}</td><td>${l.email||''}</td><td>${l.score||0}</td><td>${l.priority||''}</td></tr>`).join('')}
</tbody></table>
</body></html>`);
	} catch (e: any) {
		res.status(500).send(e.message || 'error');
	}
});

const server = app.listen(port, () => {
    console.log(`KPIs server running on http://localhost:${port}`);
});

async function shutdown(signal: string) {
    console.log(`\n${signal} received, shutting down...`);
    server.close(() => {
        pool.end().then(() => {
            console.log('Postgres pool closed. Bye.');
            process.exit(0);
        }).catch((e) => {
            console.error('Error closing pool', e);
            process.exit(1);
        });
    });
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
