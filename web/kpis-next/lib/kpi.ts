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

export async function fetchAging() {
	const client = await pool.connect();
	try {
		const q = await client.query(`
			SELECT 
				CASE 
					WHEN due_date >= CURRENT_DATE THEN 'current'
					WHEN due_date >= CURRENT_DATE - INTERVAL '30 days' THEN '1-30'
					WHEN due_date >= CURRENT_DATE - INTERVAL '60 days' THEN '31-60'
					WHEN due_date >= CURRENT_DATE - INTERVAL '90 days' THEN '61-90'
					ELSE '90+'
				END AS bucket,
				COUNT(*)::int AS invoice_count,
				COALESCE(SUM(total), 0)::numeric AS total_amount
			FROM invoices
			WHERE status = 'issued'
			AND due_date IS NOT NULL
			GROUP BY bucket
			ORDER BY 
				CASE bucket
					WHEN 'current' THEN 1
					WHEN '1-30' THEN 2
					WHEN '31-60' THEN 3
					WHEN '61-90' THEN 4
					WHEN '90+' THEN 5
				END
		`);
		return q.rows.map(r => ({
			bucket: r.bucket,
			invoice_count: Number(r.invoice_count),
			total_amount: Number(r.total_amount),
		}));
	} finally {
		client.release();
	}
}

export async function fetchRevenue(period: string = 'daily') {
	const client = await pool.connect();
	try {
		if (period === 'monthly') {
			const q = await client.query(`
				SELECT 
					DATE_TRUNC('month', created_at)::date AS period,
					COUNT(*)::int AS invoice_count,
					COALESCE(SUM(total), 0)::numeric AS revenue,
					COALESCE(SUM(taxes), 0)::numeric AS taxes,
					COALESCE(SUM(subtotal), 0)::numeric AS subtotal
				FROM invoices
				WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
				GROUP BY period
				ORDER BY period DESC
			`);
			return q.rows.map(r => ({
				period: r.period,
				invoice_count: Number(r.invoice_count),
				revenue: Number(r.revenue),
				taxes: Number(r.taxes),
				subtotal: Number(r.subtotal),
			}));
		} else {
			const q = await client.query(`
				SELECT 
					created_at::date AS period,
					COUNT(*)::int AS invoice_count,
					COALESCE(SUM(total), 0)::numeric AS revenue,
					COALESCE(SUM(taxes), 0)::numeric AS taxes,
					COALESCE(SUM(subtotal), 0)::numeric AS subtotal
				FROM invoices
				WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
				GROUP BY period
				ORDER BY period DESC
			`);
			return q.rows.map(r => ({
				period: r.period,
				invoice_count: Number(r.invoice_count),
				revenue: Number(r.revenue),
				taxes: Number(r.taxes),
				subtotal: Number(r.subtotal),
			}));
		}
	} finally {
		client.release();
	}
}
