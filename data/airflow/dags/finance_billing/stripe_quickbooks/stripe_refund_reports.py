"""
DAG para generar reportes y métricas de reembolsos de Stripe.
Proporciona insights sobre reembolsos procesados, tasas de éxito, y tendencias.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, List

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.db import get_conn

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from data.airflow.plugins.etl_notifications import notify_slack, notify_email
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack, notify_email
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dag(
	dag_id="stripe_refund_reports",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 9 * * *",  # Diario a las 9 AM
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=5),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Genera reportes y métricas de reembolsos de Stripe procesados",
	tags=["finance", "stripe", "reports", "analytics"],
)
def stripe_refund_reports() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="generate_daily_report")
	def generate_daily_report() -> Dict[str, Any]:
		"""
		Genera reporte diario de reembolsos procesados.
		"""
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Estadísticas del día
					cur.execute("""
						SELECT 
							COUNT(*) as total,
							COUNT(*) FILTER (WHERE status = 'completed') as completed,
							COUNT(*) FILTER (WHERE status = 'failed') as failed,
							COUNT(*) FILTER (WHERE status = 'pending') as pending,
							COUNT(*) FILTER (WHERE status = 'triggered') as triggered,
							COALESCE(SUM(amount) FILTER (WHERE status = 'completed'), 0) as total_amount_completed,
							COALESCE(SUM(amount), 0) as total_amount,
							AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) FILTER (WHERE processed_at IS NOT NULL) as avg_processing_seconds
						FROM stripe_refunds
						WHERE created_at >= CURRENT_DATE
					""")
					
					today_stats = cur.fetchone()
					
					# Estadísticas de la última semana
					cur.execute("""
						SELECT 
							COUNT(*) as total,
							COUNT(*) FILTER (WHERE status = 'completed') as completed,
							COUNT(*) FILTER (WHERE status = 'failed') as failed,
							COALESCE(SUM(amount) FILTER (WHERE status = 'completed'), 0) as total_amount_completed,
							COALESCE(SUM(amount), 0) as total_amount
						FROM stripe_refunds
						WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
					""")
					
					week_stats = cur.fetchone()
					
					# Reembolsos fallidos recientes
					cur.execute("""
						SELECT 
							stripe_refund_id,
							customer_email,
							amount,
							error_message,
							created_at
						FROM stripe_refunds
						WHERE status = 'failed'
							AND created_at >= CURRENT_DATE - INTERVAL '24 hours'
						ORDER BY created_at DESC
						LIMIT 10
					""")
					
					failed_refunds = cur.fetchall()
					
					# Tasa de éxito por día (últimos 7 días)
					cur.execute("""
						SELECT 
							DATE(created_at) as date,
							COUNT(*) as total,
							COUNT(*) FILTER (WHERE status = 'completed') as completed,
							ROUND(
								COUNT(*) FILTER (WHERE status = 'completed')::numeric / 
								NULLIF(COUNT(*), 0) * 100, 
								2
							) as success_rate_pct
						FROM stripe_refunds
						WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
						GROUP BY DATE(created_at)
						ORDER BY date DESC
					""")
					
					daily_trends = cur.fetchall()
					
					report = {
						"today": {
							"total": today_stats[0] or 0,
							"completed": today_stats[1] or 0,
							"failed": today_stats[2] or 0,
							"pending": today_stats[3] or 0,
							"triggered": today_stats[4] or 0,
							"total_amount_completed": float(today_stats[5] or 0),
							"total_amount": float(today_stats[6] or 0),
							"avg_processing_seconds": float(today_stats[7] or 0),
							"success_rate": (
								(today_stats[1] / today_stats[0] * 100) 
								if today_stats[0] and today_stats[0] > 0 
								else 0
							)
						},
						"week": {
							"total": week_stats[0] or 0,
							"completed": week_stats[1] or 0,
							"failed": week_stats[2] or 0,
							"total_amount_completed": float(week_stats[3] or 0),
							"total_amount": float(week_stats[4] or 0),
							"success_rate": (
								(week_stats[1] / week_stats[0] * 100) 
								if week_stats[0] and week_stats[0] > 0 
								else 0
							)
						},
						"failed_refunds_recent": [
							{
								"stripe_refund_id": row[0],
								"customer_email": row[1],
								"amount": float(row[2]),
								"error_message": row[3],
								"created_at": str(row[4])
							}
							for row in failed_refunds
						],
						"daily_trends": [
							{
								"date": str(row[0]),
								"total": row[1],
								"completed": row[2],
								"success_rate_pct": float(row[3] or 0)
							}
							for row in daily_trends
						]
					}
					
					logger.info(
						"Reporte diario generado",
						extra={
							"today_total": report["today"]["total"],
							"today_success_rate": report["today"]["success_rate"],
							"week_total": report["week"]["total"]
						}
					)
					
					# Registrar métricas
					if STATS_AVAILABLE:
						try:
							Stats.gauge("stripe_refund.reports.today_total", report["today"]["total"])
							Stats.gauge("stripe_refund.reports.today_success_rate", report["today"]["success_rate"])
							Stats.gauge("stripe_refund.reports.week_total", report["week"]["total"])
							Stats.gauge("stripe_refund.reports.week_success_rate", report["week"]["success_rate"])
						except Exception:
							pass
					
					return report
		except Exception as e:
			logger.error(f"Error generando reporte: {e}", exc_info=True)
			raise AirflowFailException(f"Error generando reporte: {e}")

	@task(task_id="send_daily_notification")
	def send_daily_notification(report: Dict[str, Any]) -> None:
		"""
		Envía notificación diaria con el resumen de reembolsos.
		"""
		today = report.get("today", {})
		week = report.get("week", {})
		
		# Preparar mensaje
		success_rate_today = today.get("success_rate", 0)
		emoji = "✅" if success_rate_today >= 95 else "⚠️" if success_rate_today >= 80 else "❌"
		
		message = f"""
{emoji} *Reporte Diario de Reembolsos Stripe*

*📊 Hoy:*
• Total: {today.get('total', 0)}
• Completados: {today.get('completed', 0)} ✅
• Fallidos: {today.get('failed', 0)} ❌
• Pendientes: {today.get('pending', 0)} ⏳
• Tasa de éxito: {success_rate_today:.1f}%
• Monto procesado: ${today.get('total_amount_completed', 0):,.2f}

*📈 Última semana:*
• Total: {week.get('total', 0)}
• Completados: {week.get('completed', 0)}
• Tasa de éxito: {week.get('success_rate', 0):.1f}%
• Monto total: ${week.get('total_amount_completed', 0):,.2f}

*⚠️ Reembolsos fallidos recientes: {len(report.get('failed_refunds_recent', []))}*
"""
		
		# Agregar detalles de fallidos si hay
		failed = report.get("failed_refunds_recent", [])
		if failed:
			message += "\n*Detalles de fallos:*\n"
			for refund in failed[:5]:  # Solo primeros 5
				message += f"• {refund['stripe_refund_id'][:20]}... - ${refund['amount']:.2f} - {refund['error_message'][:50]}\n"
		
		if NOTIFICATIONS_AVAILABLE:
			try:
				notify_slack(
					message,
					extra_context=report,
					username="Stripe Refund Reports",
					icon_emoji=":credit_card:"
				)
				logger.info("Notificación enviada a Slack")
			except Exception as e:
				logger.warning(f"Error enviando notificación a Slack: {e}")
		
		# También enviar email si hay fallos significativos
		if today.get("failed", 0) > 0 or success_rate_today < 90:
			try:
				html_body = f"""
				<h2>Reporte Diario de Reembolsos Stripe</h2>
				<h3>Resumen del día</h3>
				<ul>
					<li><strong>Total:</strong> {today.get('total', 0)}</li>
					<li><strong>Completados:</strong> {today.get('completed', 0)}</li>
					<li><strong>Fallidos:</strong> {today.get('failed', 0)}</li>
					<li><strong>Tasa de éxito:</strong> {success_rate_today:.1f}%</li>
				</ul>
				"""
				if failed:
					html_body += "<h3>Reembolsos fallidos</h3><ul>"
					for refund in failed:
						html_body += f"<li>{refund['stripe_refund_id']} - ${refund['amount']:.2f} - {refund['error_message']}</li>"
					html_body += "</ul>"
				
				notify_email(
					subject=f"Reporte Diario Reembolsos - {success_rate_today:.1f}% éxito",
					html_content=html_body
				)
			except Exception as e:
				logger.warning(f"Error enviando email: {e}")

	@task(task_id="check_failed_refunds")
	def check_failed_refunds() -> Dict[str, Any]:
		"""
		Verifica reembolsos fallidos que necesitan atención.
		"""
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Reembolsos fallidos sin reprocesar
					cur.execute("""
						SELECT 
							stripe_refund_id,
							customer_email,
							amount,
							error_message,
							created_at,
							processed_at
						FROM stripe_refunds
						WHERE status = 'failed'
							AND processed_at IS NOT NULL
							AND processed_at >= CURRENT_DATE - INTERVAL '7 days'
						ORDER BY created_at DESC
					""")
					
					failed = cur.fetchall()
					
					# Reembolsos pendientes por más de 24 horas
					cur.execute("""
						SELECT 
							stripe_refund_id,
							customer_email,
							amount,
							created_at
						FROM stripe_refunds
						WHERE status IN ('pending', 'triggered')
							AND created_at < NOW() - INTERVAL '24 hours'
						ORDER BY created_at ASC
					""")
					
					stuck = cur.fetchall()
					
					result = {
						"failed_count": len(failed),
						"stuck_count": len(stuck),
						"failed_refunds": [
							{
								"stripe_refund_id": row[0],
								"customer_email": row[1],
								"amount": float(row[2]),
								"error_message": row[3],
								"created_at": str(row[4]),
								"processed_at": str(row[5])
							}
							for row in failed
						],
						"stuck_refunds": [
							{
								"stripe_refund_id": row[0],
								"customer_email": row[1],
								"amount": float(row[2]),
								"created_at": str(row[3])
							}
							for row in stuck
						]
					}
					
					# Alertar si hay problemas
					if result["stuck_count"] > 0:
						logger.warning(f"{result['stuck_count']} reembolsos atascados")
						if NOTIFICATIONS_AVAILABLE:
							try:
								notify_slack(
									f"⚠️ {result['stuck_count']} reembolsos atascados por más de 24 horas",
									extra_context=result,
									username="Stripe Refund Monitor"
								)
							except Exception:
								pass
					
					return result
		except Exception as e:
			logger.error(f"Error verificando reembolsos fallidos: {e}", exc_info=True)
			return {"failed_count": 0, "stuck_count": 0, "failed_refunds": [], "stuck_refunds": []}

	# Pipeline de reportes
	report = generate_daily_report()
	send_daily_notification(report)
	check_failed_refunds()
	return None


dag = stripe_refund_reports()



