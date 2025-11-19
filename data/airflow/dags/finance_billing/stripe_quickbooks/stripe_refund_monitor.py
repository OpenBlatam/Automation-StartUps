"""
DAG de monitoreo y alertas para reembolsos de Stripe.
Detecta problemas y envía alertas automáticas.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.db import get_conn

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dag(
	dag_id="stripe_refund_monitor",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="*/30 * * * *",  # Cada 30 minutos
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=5),
		"email_on_failure": False,
	},
	description="Monitorea reembolsos de Stripe y envía alertas por problemas",
	tags=["finance", "stripe", "monitoring", "alerts"],
)
def stripe_refund_monitor() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="check_stuck_refunds")
	def check_stuck_refunds() -> Dict[str, Any]:
		"""
		Verifica reembolsos atascados (pending/triggered por más de 1 hora).
		"""
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute("""
						SELECT 
							stripe_refund_id,
							status,
							customer_email,
							amount,
							created_at,
							EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600 as hours_stuck
						FROM stripe_refunds
						WHERE status IN ('pending', 'triggered')
							AND created_at < NOW() - INTERVAL '1 hour'
						ORDER BY created_at ASC
					""")
					
					stuck = cur.fetchall()
					
					if stuck:
						logger.warning(f"Encontrados {len(stuck)} reembolsos atascados")
						
						# Alertar si hay más de 3 atascados
						if len(stuck) >= 3:
							message = f"⚠️ *ALERTA: {len(stuck)} reembolsos atascados*\n\n"
							for row in stuck[:5]:  # Primeros 5
								message += f"• {row[0][:20]}... - {row[2]} - ${float(row[3]):.2f} - {float(row[5]):.1f}h atascado\n"
							
							if NOTIFICATIONS_AVAILABLE:
								try:
									notify_slack(
										message,
										extra_context={"count": len(stuck), "refunds": stuck[:5]},
										username="Stripe Refund Monitor"
									)
								except Exception:
									pass
					
					return {
						"stuck_count": len(stuck),
						"stuck_refunds": [
							{
								"stripe_refund_id": row[0],
								"status": row[1],
								"customer_email": row[2],
								"amount": float(row[3]),
								"hours_stuck": float(row[5])
							}
							for row in stuck
						]
					}
		except Exception as e:
			logger.error(f"Error verificando reembolsos atascados: {e}", exc_info=True)
			return {"stuck_count": 0, "stuck_refunds": []}

	@task(task_id="check_failure_rate")
	def check_failure_rate() -> Dict[str, Any]:
		"""
		Verifica si la tasa de fallos es inusualmente alta.
		"""
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					# Últimas 24 horas
					cur.execute("""
						SELECT 
							COUNT(*) as total,
							COUNT(*) FILTER (WHERE status = 'failed') as failed,
							COUNT(*) FILTER (WHERE status = 'completed') as completed
						FROM stripe_refunds
						WHERE created_at >= NOW() - INTERVAL '24 hours'
					""")
					
					stats = cur.fetchone()
					total = stats[0] or 0
					failed = stats[1] or 0
					completed = stats[2] or 0
					
					failure_rate = (failed / total * 100) if total > 0 else 0
					
					# Alertar si tasa de fallo > 20% y hay al menos 5 reembolsos
					if failure_rate > 20.0 and total >= 5:
						logger.warning(f"Tasa de fallo alta: {failure_rate:.1f}% ({failed}/{total})")
						
						# Obtener errores más comunes
						cur.execute("""
							SELECT 
								error_message,
								COUNT(*) as count
							FROM stripe_refunds
							WHERE status = 'failed'
								AND created_at >= NOW() - INTERVAL '24 hours'
								AND error_message IS NOT NULL
							GROUP BY error_message
							ORDER BY count DESC
							LIMIT 3
						""")
						
						common_errors = cur.fetchall()
						
						message = f"🚨 *ALERTA: Tasa de fallo alta ({failure_rate:.1f}%)\n"
						message += f"• Total: {total}\n"
						message += f"• Fallidos: {failed}\n"
						message += f"• Completados: {completed}\n\n"
						message += "*Errores más comunes:*\n"
						for error, count in common_errors:
							message += f"• {error[:60]}... ({count} veces)\n"
						
						if NOTIFICATIONS_AVAILABLE:
							try:
								notify_slack(
									message,
									extra_context={
										"failure_rate": failure_rate,
										"total": total,
										"failed": failed
									},
									username="Stripe Refund Monitor"
								)
							except Exception:
								pass
					
					return {
						"failure_rate": failure_rate,
						"total": total,
						"failed": failed,
						"completed": completed,
						"alert_triggered": failure_rate > 20.0 and total >= 5
					}
		except Exception as e:
			logger.error(f"Error verificando tasa de fallos: {e}", exc_info=True)
			return {"failure_rate": 0, "total": 0, "failed": 0, "completed": 0, "alert_triggered": False}

	@task(task_id="refresh_materialized_views")
	def refresh_materialized_views() -> None:
		"""
		Refresca vistas materializadas de reembolsos.
		"""
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute("SELECT refresh_stripe_refunds_mv();")
					logger.info("Vista materializada refrescada")
		except Exception as e:
			logger.warning(f"No se pudo refrescar vista materializada (puede no existir): {e}")

	# Pipeline de monitoreo
	check_stuck_refunds()
	check_failure_rate()
	refresh_materialized_views()
	return None


dag = stripe_refund_monitor()



