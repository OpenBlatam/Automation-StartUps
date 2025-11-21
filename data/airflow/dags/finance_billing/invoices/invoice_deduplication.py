from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_email


@dag(
	dag_id="invoice_deduplication",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 4 * * *",  # daily at 04:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Detect and report potential duplicate invoices",
	tags=["finance", "validation", "deduplication"],
)
def invoice_deduplication() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="detect_duplicates")
	def detect_duplicates() -> Dict[str, Any]:
		tolerance = 0.01  # 1 cent tolerance
		duplicates: list[Dict[str, Any]] = []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Find potential duplicates: same total, same day, within tolerance
					cur.execute(
						"""
						SELECT 
							i1.id AS id1,
							i1.serie AS serie1,
							i2.id AS id2,
							i2.serie AS serie2,
							i1.total,
							i1.created_at::date AS invoice_date,
							ABS(i1.total - i2.total) AS amount_diff
						FROM invoices i1
						JOIN invoices i2 ON 
							i1.id < i2.id
							AND i1.created_at::date = i2.created_at::date
							AND ABS(i1.total - i2.total) <= %s
							AND i1.status = i2.status
						WHERE i1.created_at >= CURRENT_DATE - INTERVAL '30 days'
						ORDER BY i1.created_at DESC
						LIMIT 50
						"""
					)
					for row in cur.fetchall():
						id1, serie1, id2, serie2, total, inv_date, diff = row
						duplicates.append({
							"invoice1_id": id1,
							"invoice1_serie": serie1,
							"invoice2_id": id2,
							"invoice2_serie": serie2,
							"amount": float(total),
							"date": inv_date.isoformat() if hasattr(inv_date, "isoformat") else str(inv_date),
							"difference": float(diff),
						})
		except Exception:
			logger.warning("duplicate detection failed", exc_info=True)
		logger.info("duplicate detection completed", extra={"count": len(duplicates)})
		return {"duplicates": duplicates, "count": len(duplicates)}

	@task(task_id="report_duplicates")
	def report_duplicates(payload: Dict[str, Any]) -> None:
		duplicates = payload.get("duplicates", []) or []
		count = payload.get("count", 0)
		if count == 0:
			logger.info("no duplicates found")
			return
		subject = f"ALERTA: {count} posibles facturas duplicadas detectadas"
		html = f"""
		<html>
		<body>
			<h2>Facturas Potencialmente Duplicadas</h2>
			<p>Se detectaron <strong>{count}</strong> pares de facturas que podrían ser duplicados.</p>
			<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
				<tr style="background: #f5f5f5;">
					<th>Factura 1</th>
					<th>Factura 2</th>
					<th>Monto</th>
					<th>Fecha</th>
					<th>Diferencia</th>
				</tr>
		"""
		for dup in duplicates[:20]:  # Limit to 20 in email
			html += f"""
				<tr>
					<td>{dup.get('invoice1_serie')} (ID: {dup.get('invoice1_id')})</td>
					<td>{dup.get('invoice2_serie')} (ID: {dup.get('invoice2_id')})</td>
					<td>${dup.get('amount', 0):,.2f}</td>
					<td>{dup.get('date')}</td>
					<td>${dup.get('difference', 0):,.2f}</td>
				</tr>
			"""
		html += """
			</table>
			<p style="margin-top: 20px; color: #666; font-size: 12px;">
				Nota: Estas son posibles duplicados basados en monto y fecha similares. 
				Por favor, revisa manualmente para confirmar.
			</p>
		</body>
		</html>
		"""
		try:
			notify_email(subject=subject, html_content=html, to=None)
			logger.info("duplicate report sent", extra={"count": count})
		except Exception:
			logger.warning("duplicate report failed", exc_info=True)

	report_duplicates(detect_duplicates())
	return None


dag = invoice_deduplication()


