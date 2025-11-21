from __future__ import annotations

from datetime import timedelta, date
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_email


def _get_env_var(name: str, default: str | None = None) -> str:
	return str(Variable.get(name, default_var=default))


@dag(
	dag_id="financial_summary",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 9 * * MON",  # weekly on Monday at 09:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Weekly financial executive summary",
	tags=["finance", "summary", "reports"],
)
def financial_summary() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="generate_summary")
	def generate_summary() -> Dict[str, Any]:
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Revenue metrics
					cur.execute(
						"""
						SELECT 
							SUM(total) FILTER (WHERE status = 'paid' AND created_at >= CURRENT_DATE - INTERVAL '7 days') AS revenue_7d,
							SUM(total) FILTER (WHERE status = 'paid' AND created_at >= CURRENT_DATE - INTERVAL '30 days') AS revenue_30d,
							COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') AS invoices_7d,
							COUNT(*) FILTER (WHERE status = 'issued' AND due_date < CURRENT_DATE) AS overdue_count,
							SUM(total) FILTER (WHERE status = 'issued' AND due_date < CURRENT_DATE) AS overdue_amount,
							AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - due_date)) / 86400) 
								FILTER (WHERE status = 'issued' AND due_date < CURRENT_DATE) AS avg_days_overdue,
							COUNT(*) FILTER (WHERE status = 'partial') AS partial_count,
							SUM(total) FILTER (WHERE status = 'partial') AS partial_amount
						FROM invoices
						"""
					)
					row = cur.fetchone()
					revenue_7d, revenue_30d, invoices_7d, overdue_count, overdue_amount, avg_overdue, partial_count, partial_amount = row
					# Payment metrics
					cur.execute(
						"""
						SELECT 
							COUNT(DISTINCT p.payment_id) AS payments_7d,
							SUM(p.amount) AS payments_7d_total,
							COUNT(DISTINCT ip.invoice_id) AS invoices_paid_7d
						FROM payments p
						LEFT JOIN invoice_payments ip ON p.payment_id = ip.payment_id
						WHERE p.created_at >= CURRENT_DATE - INTERVAL '7 days'
						AND p.status IN ('succeeded', 'paid', 'payment_intent.succeeded')
						"""
					)
					pay_row = cur.fetchone()
					payments_7d, payments_7d_total, invoices_paid_7d = pay_row if pay_row else (0, 0, 0)
					# Credit notes
					cur.execute(
						"SELECT COUNT(*), SUM(amount) FROM credit_notes WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
					)
					cn_row = cur.fetchone()
					credit_notes_7d, credit_amount_7d = cn_row if cn_row else (0, 0)
					return {
						"revenue_7d": float(revenue_7d or 0),
						"revenue_30d": float(revenue_30d or 0),
						"invoices_7d": int(invoices_7d or 0),
						"overdue_count": int(overdue_count or 0),
						"overdue_amount": float(overdue_amount or 0),
						"avg_days_overdue": float(avg_overdue or 0) if avg_overdue else 0,
						"partial_count": int(partial_count or 0),
						"partial_amount": float(partial_amount or 0),
						"payments_7d": int(payments_7d or 0),
						"payments_7d_total": float(payments_7d_total or 0),
						"invoices_paid_7d": int(invoices_paid_7d or 0),
						"credit_notes_7d": int(credit_notes_7d or 0),
						"credit_amount_7d": float(credit_amount_7d or 0),
					}
		except Exception:
			logger.warning("summary generation failed", exc_info=True)
			return {}
		return {}

	@task(task_id="send_summary_email")
	def send_summary_email(payload: Dict[str, Any]) -> None:
		if not payload:
			logger.warning("empty summary, skipping email")
			return
		subject = f"Resumen Financiero Semanal - {date.today().strftime('%Y-%m-%d')}"
		html = f"""
		<html>
		<head><style>
			body {{ font-family: Arial, sans-serif; }}
			.metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
			.metric-label {{ font-weight: bold; color: #333; }}
			.metric-value {{ font-size: 18px; color: #2563eb; margin-top: 5px; }}
			.alert {{ background: #fee2e2; border-left: 4px solid #dc2626; }}
			.section {{ margin: 20px 0; }}
			h2 {{ color: #1f2937; border-bottom: 2px solid #2563eb; padding-bottom: 5px; }}
		</style></head>
		<body>
			<h1>Resumen Financiero Semanal</h1>
			<p>Período: Últimos 7 días</p>
			
			<div class="section">
				<h2>📈 Ingresos</h2>
				<div class="metric">
					<div class="metric-label">Revenue (7 días)</div>
					<div class="metric-value">${payload.get('revenue_7d', 0):,.2f}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Revenue (30 días)</div>
					<div class="metric-value">${payload.get('revenue_30d', 0):,.2f}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Facturas Emitidas (7 días)</div>
					<div class="metric-value">{payload.get('invoices_7d', 0)}</div>
				</div>
			</div>

			<div class="section">
				<h2>💰 Pagos</h2>
				<div class="metric">
					<div class="metric-label">Pagos Recibidos (7 días)</div>
					<div class="metric-value">{payload.get('payments_7d', 0)}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Monto Total Pagado (7 días)</div>
					<div class="metric-value">${payload.get('payments_7d_total', 0):,.2f}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Facturas Pagadas (7 días)</div>
					<div class="metric-value">{payload.get('invoices_paid_7d', 0)}</div>
				</div>
			</div>

			<div class="section">
				<h2>⚠️ Cuentas por Cobrar</h2>
				<div class="metric {'alert' if payload.get('overdue_count', 0) > 0 else ''}">
					<div class="metric-label">Facturas Vencidas</div>
					<div class="metric-value">{payload.get('overdue_count', 0)}</div>
				</div>
				<div class="metric {'alert' if payload.get('overdue_amount', 0) > 0 else ''}">
					<div class="metric-label">Monto Vencido</div>
					<div class="metric-value">${payload.get('overdue_amount', 0):,.2f}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Promedio Días de Mora</div>
					<div class="metric-value">{payload.get('avg_days_overdue', 0):.1f} días</div>
				</div>
			</div>

			<div class="section">
				<h2>📊 Estado de Facturas</h2>
				<div class="metric">
					<div class="metric-label">Facturas Parcialmente Pagadas</div>
					<div class="metric-value">{payload.get('partial_count', 0)}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Monto Pendiente (Parciales)</div>
					<div class="metric-value">${payload.get('partial_amount', 0):,.2f}</div>
				</div>
			</div>

			<div class="section">
				<h2>🔄 Devoluciones</h2>
				<div class="metric">
					<div class="metric-label">Notas de Crédito (7 días)</div>
					<div class="metric-value">{payload.get('credit_notes_7d', 0)}</div>
				</div>
				<div class="metric">
					<div class="metric-label">Monto de Devoluciones</div>
					<div class="metric-value">${payload.get('credit_amount_7d', 0):,.2f}</div>
				</div>
			</div>

			<p style="margin-top: 30px; color: #6b7280; font-size: 12px;">
				Reporte generado automáticamente. Para más detalles, consulta el dashboard financiero.
			</p>
		</body>
		</html>
		"""
		try:
			notify_email(subject=subject, html_content=html, to=None)
			logger.info("summary email sent")
		except Exception:
			logger.warning("summary email failed", exc_info=True)

	send_summary_email(generate_summary())
	return None


dag = financial_summary()


