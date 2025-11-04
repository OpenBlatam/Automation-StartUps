import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
	try {
		const client = await pool.connect();
		try {
			const metrics = await client.query(`
				WITH stats AS (
					SELECT 
						COUNT(*) FILTER (WHERE status = 'issued') AS pending_invoices,
						COUNT(*) FILTER (WHERE status = 'paid') AS paid_invoices,
						COUNT(*) FILTER (WHERE status = 'partial') AS partial_invoices,
						SUM(total) FILTER (WHERE status = 'issued') AS pending_amount,
						SUM(total) FILTER (WHERE status = 'paid') AS paid_amount,
						SUM(total) FILTER (WHERE status = 'partial') AS partial_amount,
						AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - due_date)) / 86400) FILTER (WHERE status = 'issued' AND due_date < CURRENT_DATE) AS avg_days_overdue,
						COUNT(*) FILTER (WHERE due_date < CURRENT_DATE - INTERVAL '90 days' AND status = 'issued') AS critical_overdue_count
					FROM invoices
					WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
				),
				revenue_trend AS (
					SELECT 
						DATE_TRUNC('month', created_at) AS month,
						SUM(total) AS revenue,
						COUNT(*) AS invoice_count
					FROM invoices
					WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
					AND status = 'paid'
					GROUP BY month
					ORDER BY month DESC
				),
				payment_stats AS (
					SELECT 
						COUNT(DISTINCT ip.invoice_id) AS invoices_with_payments,
						SUM(p.amount) AS total_paid,
						AVG(p.amount) AS avg_payment
					FROM invoice_payments ip
					JOIN payments p ON ip.payment_id = p.payment_id
					WHERE p.created_at >= CURRENT_DATE - INTERVAL '30 days'
					AND p.status IN ('succeeded', 'paid', 'payment_intent.succeeded')
				)
				SELECT 
					s.*,
					COALESCE(rt.revenue, 0) AS current_month_revenue,
					COALESCE(rt.invoice_count, 0) AS current_month_invoices,
					COALESCE(ps.invoices_with_payments, 0) AS invoices_with_payments,
					COALESCE(ps.total_paid, 0) AS total_paid_30d,
					COALESCE(ps.avg_payment, 0) AS avg_payment
				FROM stats s
				CROSS JOIN LATERAL (
					SELECT revenue, invoice_count 
					FROM revenue_trend 
					ORDER BY month DESC 
					LIMIT 1
				) rt
				CROSS JOIN LATERAL (SELECT * FROM payment_stats) ps
			`);
			return NextResponse.json(metrics.rows[0] || {}, {
				headers: { 'Cache-Control': 'public, max-age=300, stale-while-revalidate=600' },
			});
		} finally {
			client.release();
		}
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}


