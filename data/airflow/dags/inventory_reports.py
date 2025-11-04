"""
DAG de Reportes de Inventario
Genera reportes diarios y semanales de métricas de inventario, rotación, y KPIs.
"""
from __future__ import annotations

from datetime import timedelta, date
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable

from data.airflow.plugins.db import get_conn

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


def _get_env_var(name: str, default: str | None = None) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    value = Variable.get(name, default_var=default)
    if value is None:
        value = os.environ.get(name, default)
    return str(value) if value else ""


def _query_one(sql: str, params: Tuple[Any, ...] | None = None) -> Any:
    """Ejecuta query y retorna un solo valor."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return row[0] if row else None


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


@dag(
    dag_id="inventory_reports",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 8 * * *",  # Diario a las 8:00 UTC
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
        "email_on_retry": False,
    },
    description="Reportes diarios de inventario con métricas y KPIs",
    tags=["inventory", "reports", "kpis"],
)
def inventory_reports() -> None:
    """DAG principal de reportes de inventario."""

    @task(task_id="generate_daily_report")
    def generate_daily_report() -> Dict[str, Any]:
        """Genera reporte diario de inventario."""
        logger.info("Generating daily inventory report...")
        
        # Refrescar vistas materializadas
        with get_conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_daily_stats")
                    conn.commit()
                    logger.info("Refreshed mv_inventory_daily_stats")
                except Exception as e:
                    logger.warning(f"Could not refresh materialized view: {e}")
                
                try:
                    cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_inventory_critical_products")
                    conn.commit()
                    logger.info("Refreshed mv_inventory_critical_products")
                except Exception as e:
                    logger.warning(f"Could not refresh materialized view: {e}")
        
        # Métricas generales
        metrics = {}
        
        # Total de productos activos
        metrics["total_products"] = _query_one(
            "SELECT COUNT(*) FROM inventory_products WHERE active = TRUE"
        ) or 0
        
        # Productos con stock bajo o sin stock
        metrics["critical_products"] = _query_one(
            "SELECT COUNT(*) FROM mv_inventory_critical_products"
        ) or 0
        
        metrics["out_of_stock"] = _query_one(
            "SELECT COUNT(*) FROM mv_inventory_critical_products WHERE status = 'out_of_stock'"
        ) or 0
        
        metrics["low_stock"] = _query_one(
            "SELECT COUNT(*) FROM mv_inventory_critical_products WHERE status = 'low_stock'"
        ) or 0
        
        # Alertas abiertas
        metrics["open_alerts"] = _query_one(
            "SELECT COUNT(*) FROM inventory_alerts WHERE status IN ('open', 'acknowledged')"
        ) or 0
        
        metrics["critical_alerts"] = _query_one(
            "SELECT COUNT(*) FROM inventory_alerts WHERE status IN ('open', 'acknowledged') AND severity = 'critical'"
        ) or 0
        
        # Reordenes pendientes
        metrics["pending_reorders"] = _query_one(
            "SELECT COUNT(*) FROM inventory_reorders WHERE status IN ('pending', 'sent', 'confirmed')"
        ) or 0
        
        # Valor total de inventario
        metrics["total_inventory_value"] = float(
            _query_one(
                """
                SELECT COALESCE(SUM(s.available_quantity * p.unit_cost), 0)
                FROM inventory_stock s
                JOIN inventory_products p ON s.product_id = p.id
                WHERE p.active = TRUE
                """
            ) or 0
        )
        
        # Movimientos del día anterior
        yesterday = date.today() - timedelta(days=1)
        metrics["movements_yesterday"] = _query_one(
            "SELECT COUNT(*) FROM inventory_movements WHERE DATE(created_at) = %s",
            (yesterday,),
        ) or 0
        
        metrics["sales_yesterday"] = _query_one(
            """
            SELECT COALESCE(SUM(quantity), 0)
            FROM inventory_movements 
            WHERE DATE(created_at) = %s AND movement_type = 'sale'
            """,
            (yesterday,),
        ) or 0
        
        # Top productos con más movimiento
        top_movements = _query_dict(
            """
            SELECT 
                p.sku,
                p.name,
                COUNT(m.id) AS movement_count,
                SUM(CASE WHEN m.direction = 'in' THEN m.quantity ELSE 0 END) AS incoming,
                SUM(CASE WHEN m.direction = 'out' THEN m.quantity ELSE 0 END) AS outgoing
            FROM inventory_movements m
            JOIN inventory_products p ON m.product_id = p.id
            WHERE m.created_at >= NOW() - INTERVAL '7 days'
            GROUP BY p.id, p.sku, p.name
            ORDER BY movement_count DESC
            LIMIT 10
            """
        )
        
        # Top productos críticos
        top_critical = _query_dict(
            """
            SELECT sku, product_name, current_stock, reorder_point, status
            FROM mv_inventory_critical_products
            ORDER BY 
                CASE status WHEN 'out_of_stock' THEN 1 ELSE 2 END,
                current_stock
            LIMIT 10
            """
        )
        
        logger.info(f"Daily report generated: {metrics}")
        
        return {
            "metrics": metrics,
            "top_movements": top_movements,
            "top_critical": top_critical,
            "report_date": date.today().isoformat(),
        }

    @task(task_id="send_daily_report")
    def send_daily_report(payload: Dict[str, Any]) -> None:
        """Envía reporte diario por Slack y Email."""
        if not NOTIFICATIONS_AVAILABLE:
            logger.warning("Notifications not available")
            return
        
        metrics = payload.get("metrics", {})
        top_critical = payload.get("top_critical", [])
        report_date = payload.get("report_date", date.today().isoformat())
        
        # Preparar mensaje Slack
        slack_msg = f"📊 *Reporte Diario de Inventario - {report_date}*\n\n"
        
        slack_msg += "*📈 Métricas Generales:*\n"
        slack_msg += f"• Total productos activos: {metrics.get('total_products', 0)}\n"
        slack_msg += f"• Productos críticos: {metrics.get('critical_products', 0)}\n"
        slack_msg += f"  └ Sin stock: {metrics.get('out_of_stock', 0)}\n"
        slack_msg += f"  └ Stock bajo: {metrics.get('low_stock', 0)}\n"
        slack_msg += f"• Alertas abiertas: {metrics.get('open_alerts', 0)} (críticas: {metrics.get('critical_alerts', 0)})\n"
        slack_msg += f"• Reordenes pendientes: {metrics.get('pending_reorders', 0)}\n"
        slack_msg += f"• Valor total inventario: ${metrics.get('total_inventory_value', 0):,.2f}\n"
        slack_msg += f"• Movimientos ayer: {metrics.get('movements_yesterday', 0)} ({metrics.get('sales_yesterday', 0)} ventas)\n\n"
        
        if top_critical:
            slack_msg += "*🚨 Top 5 Productos Críticos:*\n"
            for i, product in enumerate(top_critical[:5], 1):
                status_emoji = "🔴" if product.get("status") == "out_of_stock" else "⚠️"
                slack_msg += f"{i}. {status_emoji} *{product.get('sku')}* - {product.get('product_name', '')[:40]}\n"
                slack_msg += f"   Stock: {product.get('current_stock', 0)}/{product.get('reorder_point', 0)}\n"
        
        try:
            notify_slack(slack_msg)
            logger.info("Slack report sent")
        except Exception as e:
            logger.warning(f"Failed to send Slack report: {e}", exc_info=True)
        
        # Preparar email HTML
        email_subject = f"Reporte Diario de Inventario - {report_date}"
        email_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .critical {{ background-color: #ffcccc; }}
                .warning {{ background-color: #fff4cc; }}
            </style>
        </head>
        <body>
            <h2>Reporte Diario de Inventario - {report_date}</h2>
            
            <h3>Métricas Generales</h3>
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>Total Productos Activos</td>
                    <td>{metrics.get('total_products', 0)}</td>
                </tr>
                <tr>
                    <td>Productos Críticos</td>
                    <td class="critical">{metrics.get('critical_products', 0)}</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;Sin Stock</td>
                    <td class="critical">{metrics.get('out_of_stock', 0)}</td>
                </tr>
                <tr>
                    <td>&nbsp;&nbsp;Stock Bajo</td>
                    <td class="warning">{metrics.get('low_stock', 0)}</td>
                </tr>
                <tr>
                    <td>Alertas Abiertas</td>
                    <td>{metrics.get('open_alerts', 0)}</td>
                </tr>
                <tr>
                    <td>Reordenes Pendientes</td>
                    <td>{metrics.get('pending_reorders', 0)}</td>
                </tr>
                <tr>
                    <td>Valor Total Inventario</td>
                    <td>${metrics.get('total_inventory_value', 0):,.2f}</td>
                </tr>
            </table>
            
            <h3>Top 10 Productos Críticos</h3>
            <table>
                <tr>
                    <th>SKU</th>
                    <th>Nombre</th>
                    <th>Stock Actual</th>
                    <th>Punto de Reorden</th>
                    <th>Estado</th>
                </tr>
        """
        
        for product in top_critical[:10]:
            status = product.get("status", "N/A")
            row_class = "critical" if status == "out_of_stock" else "warning"
            email_html += f"""
                <tr class="{row_class}">
                    <td>{product.get('sku', 'N/A')}</td>
                    <td>{product.get('product_name', 'N/A')}</td>
                    <td>{product.get('current_stock', 0)}</td>
                    <td>{product.get('reorder_point', 0)}</td>
                    <td>{status}</td>
                </tr>
            """
        
        email_html += """
            </table>
        </body>
        </html>
        """
        
        try:
            notify_email(
                subject=email_subject,
                body=f"Reporte diario de inventario del {report_date}. Ver HTML para detalles.",
                html=email_html,
                to=None,
            )
            logger.info("Email report sent")
        except Exception as e:
            logger.warning(f"Failed to send email report: {e}", exc_info=True)

    @task(task_id="log_metrics")
    def log_metrics(payload: Dict[str, Any]) -> None:
        """Registra métricas del reporte."""
        metrics = payload.get("metrics", {})
        logger.info(
            "Inventory report metrics",
            extra=metrics,
        )

    # Pipeline
    report_data = generate_daily_report()
    send_daily_report(report_data)
    log_metrics(report_data)

    return None


dag = inventory_reports()





