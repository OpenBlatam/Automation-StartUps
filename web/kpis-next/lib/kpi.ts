import { pool } from './db';

export async function fetchSummary() {
	const client = await pool.connect();
	try {
		const [lastHour, last24h, leadsToday, paymentsRecent, leadsRecent] = await Promise.all([
			client.query("SELECT COALESCE(SUM(revenue),0) AS revenue FROM mv_revenue_24h_hourly WHERE hour >= NOW() - interval '1 hour'"),
			client.query("SELECT COALESCE(SUM(revenue),0) AS revenue FROM mv_revenue_24h_hourly"),
			client.query("SELECT priority, COUNT(*)::int AS count FROM leads WHERE created_at::date = CURRENT_DATE GROUP BY 1"),
			client.query("SELECT created_at, payment_id, amount, currency, customer, status, method FROM payments ORDER BY created_at DESC LIMIT 20"),
			client.query("SELECT created_at, ext_id, first_name, last_name, email, score, priority FROM leads ORDER BY created_at DESC LIMIT 20"),
		]);
		return {
			revenue_last_hour: Number(lastHour.rows[0]?.revenue || 0),
			revenue_24h: Number(last24h.rows[0]?.revenue || 0),
			leads_by_priority_today: leadsToday.rows,
			payments_recent: paymentsRecent.rows,
			leads_recent: leadsRecent.rows,
		};
	} finally {
		client.release();
	}
}

export async function fetchRevenue24h() {
	const client = await pool.connect();
	try {
		const q = await client.query(
			"SELECT hour AS time, revenue FROM mv_revenue_24h_hourly ORDER BY hour"
		);
		return q.rows.map(r => ({ time: r.time, revenue: Number(r.revenue) }));
	} finally {
		client.release();
	}
}
