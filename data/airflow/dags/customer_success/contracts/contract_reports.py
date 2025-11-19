"""
DAG de Reportes de Contratos
Genera reportes periódicos de métricas y analytics de contratos
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_integrations import get_contract_analytics

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_reports",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(days=7),  # Ejecutar semanalmente
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract Reports - Reportes Semanales de Contratos
    
    DAG que se ejecuta semanalmente para:
    - ✅ Generar reportes de métricas y analytics
    - ✅ Identificar contratos que requieren atención
    - ✅ Calcular KPIs de firma y renovación
    - ✅ Enviar resumen a stakeholders
    
    **Funcionalidad:**
    - Calcula métricas agregadas de contratos
    - Identifica contratos pendientes de firma por más de X días
    - Calcula tasa de firma y tiempo promedio
    - Genera reporte consolidado
    """,
    description="Generación de reportes semanales de contratos",
    tags=["contracts", "legal", "reports", "analytics"],
    dagrun_timeout=timedelta(minutes=15),
    max_active_runs=1,
)
def contract_reports() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="generate_weekly_report", pool=CONTRACT_POOL)
    def generate_weekly_report() -> Dict[str, Any]:
        """Genera reporte semanal de contratos."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.reports.generate.start", 1)
            except Exception:
                pass
        
        # Obtener analytics del último mes
        end_date = pendulum.now().date()
        start_date = end_date - timedelta(days=30)
        
        analytics = get_contract_analytics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Contratos pendientes de firma por más de 7 días
        pending_query = """
            SELECT COUNT(*)
            FROM contracts
            WHERE status IN ('pending_signature', 'partially_signed')
              AND created_at < NOW() - INTERVAL '7 days'
        """
        pending_old = hook.get_first(pending_query)[0] or 0
        
        # Contratos próximos a expirar
        expiring_query = """
            SELECT COUNT(*)
            FROM contracts
            WHERE status = 'fully_signed'
              AND expiration_date IS NOT NULL
              AND expiration_date <= CURRENT_DATE + INTERVAL '30 days'
              AND expiration_date > CURRENT_DATE
        """
        expiring_count = hook.get_first(expiring_query)[0] or 0
        
        # Contratos sin auto-renovación próximos a expirar
        expiring_no_auto_query = """
            SELECT COUNT(*)
            FROM contracts
            WHERE status = 'fully_signed'
              AND auto_renew = false
              AND expiration_date IS NOT NULL
              AND expiration_date <= CURRENT_DATE + INTERVAL '30 days'
              AND expiration_date > CURRENT_DATE
        """
        expiring_no_auto = hook.get_first(expiring_no_auto_query)[0] or 0
        
        # Tiempo promedio de firma por tipo
        avg_time_query = """
            SELECT 
                contract_type,
                AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days
            FROM contracts
            WHERE status = 'fully_signed'
              AND signed_date IS NOT NULL
              AND created_at >= %s
            GROUP BY contract_type
        """
        avg_time_by_type = {}
        for row in hook.get_records(avg_time_query, parameters=(start_date,)):
            avg_time_by_type[row[0]] = round(float(row[1]), 2) if row[1] else 0.0
        
        report = {
            "report_date": end_date.isoformat(),
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "analytics": analytics,
            "pending_old_count": pending_old,
            "expiring_count": expiring_count,
            "expiring_no_auto_count": expiring_no_auto,
            "avg_days_to_sign_by_type": avg_time_by_type,
            "alerts": []
        }
        
        # Generar alertas
        if pending_old > 0:
            report["alerts"].append({
                "type": "warning",
                "message": f"{pending_old} contratos pendientes de firma por más de 7 días",
                "action": "Revisar y enviar recordatorios"
            })
        
        if expiring_no_auto > 0:
            report["alerts"].append({
                "type": "info",
                "message": f"{expiring_no_auto} contratos próximos a expirar sin auto-renovación",
                "action": "Evaluar renovación manual"
            })
        
        if analytics.get("signing_rate", 0) < 70:
            report["alerts"].append({
                "type": "warning",
                "message": f"Tasa de firma baja: {analytics.get('signing_rate', 0):.1f}%",
                "action": "Revisar proceso de firma"
            })
        
        logger.info(
            f"Reporte semanal generado",
            extra={
                "total_contracts": analytics.get("total_contracts", 0),
                "signing_rate": analytics.get("signing_rate", 0),
                "alerts_count": len(report["alerts"])
            },
        )
        
        if Stats:
            try:
                Stats.incr("contracts.reports.generate.success", 1)
                Stats.gauge("contracts.reports.signing_rate", analytics.get("signing_rate", 0))
                Stats.gauge("contracts.reports.pending_old", pending_old)
            except Exception:
                pass
        
        return report

    @task(task_id="send_report", pool=CONTRACT_POOL)
    def send_report(report: Dict[str, Any]) -> Dict[str, Any]:
        """Envía el reporte por Slack/Email."""
        if Stats:
            try:
                Stats.incr("contracts.reports.send.start", 1)
            except Exception:
                pass
        
        try:
            from data.airflow.plugins.contract_notifications import ContractNotificationManager
            
            manager = ContractNotificationManager()
            
            # Formatear reporte para Slack
            message = f"📊 *Reporte Semanal de Contratos*\n"
            message += f"Período: {report['period']}\n\n"
            message += f"*Métricas:*\n"
            message += f"• Total de contratos: {report['analytics'].get('total_contracts', 0)}\n"
            message += f"• Firmados: {report['analytics'].get('signed_count', 0)}\n"
            message += f"• Pendientes: {report['analytics'].get('pending_count', 0)}\n"
            message += f"• Tasa de firma: {report['analytics'].get('signing_rate', 0):.1f}%\n"
            message += f"• Días promedio para firmar: {report['analytics'].get('avg_days_to_sign', 0):.1f}\n"
            message += f"• Próximos a expirar (30 días): {report['analytics'].get('expiring_30_days', 0)}\n\n"
            
            if report['pending_old_count'] > 0:
                message += f"⚠️ *Atención:* {report['pending_old_count']} contratos pendientes por más de 7 días\n\n"
            
            if report['alerts']:
                message += f"*Alertas:*\n"
                for alert in report['alerts']:
                    emoji = "⚠️" if alert['type'] == 'warning' else "ℹ️"
                    message += f"{emoji} {alert['message']}\n"
            
            manager._send_slack_notification(message, color="#36a64f")
            
            logger.info("Reporte enviado exitosamente")
            
            if Stats:
                try:
                    Stats.incr("contracts.reports.send.success", 1)
                except Exception:
                    pass
            
            return {"sent": True, "report": report}
        except Exception as e:
            logger.error(f"Error enviando reporte: {e}")
            if Stats:
                try:
                    Stats.incr("contracts.reports.send.failed", 1)
                except Exception:
                    pass
            return {"sent": False, "error": str(e)}

    # Define task flow
    report = generate_weekly_report()
    result = send_report(report)
    
    return None


dag = contract_reports()

