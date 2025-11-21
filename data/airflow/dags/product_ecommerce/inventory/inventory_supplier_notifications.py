"""
DAG de Notificaciones a Proveedores
Envía automáticamente reordenes a proveedores por email.
"""
from __future__ import annotations

from datetime import timedelta, date
import logging
import os
from typing import Any, Dict, List, Tuple

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

from data.airflow.plugins.db import get_conn

try:
    from data.airflow.plugins.etl_notifications import notify_email
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_env_var(name: str, default: str | None = None) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    from airflow.models import Variable
    value = Variable.get(name, default_var=default)
    if value is None:
        value = os.environ.get(name, default)
    return str(value) if value else ""


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


@dag(
    dag_id="inventory_supplier_notifications",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Envía reordenes a proveedores automáticamente",
    tags=["inventory", "suppliers", "notifications"],
)
def inventory_supplier_notifications() -> None:
    """DAG de notificaciones a proveedores."""

    @task(task_id="find_pending_reorders")
    def find_pending_reorders() -> Dict[str, Any]:
        """Encuentra reordenes pendientes de enviar."""
        logger.info("Finding pending reorders to send...")
        
        sql = """
            SELECT 
                r.id,
                r.product_id,
                p.sku,
                p.name AS product_name,
                r.quantity,
                r.unit_cost,
                r.total_cost,
                r.priority,
                r.supplier_name,
                r.supplier_email,
                r.requested_at,
                r.expected_delivery_date,
                s.available_quantity AS current_stock
            FROM inventory_reorders r
            JOIN inventory_products p ON r.product_id = p.id
            LEFT JOIN inventory_stock s ON r.product_id = s.product_id
            WHERE r.status = 'pending'
            AND r.supplier_email IS NOT NULL
            AND r.supplier_email != ''
            ORDER BY 
                CASE r.priority 
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'normal' THEN 3
                    ELSE 4
                END,
                r.requested_at
        """
        
        reorders = _query_dict(sql)
        logger.info(f"Found {len(reorders)} pending reorders to send")
        
        return {"reorders": reorders, "count": len(reorders)}

    @task(task_id="send_reorder_emails")
    def send_reorder_emails(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envía emails de reorden a proveedores."""
        if not NOTIFICATIONS_AVAILABLE:
            logger.warning("Email notifications not available")
            return {"sent": 0, "failed": 0}
        
        reorders = payload.get("reorders", [])
        if not reorders:
            logger.info("No reorders to send")
            return {"sent": 0, "failed": 0}
        
        # Agrupar por proveedor
        by_supplier: Dict[str, List[Dict[str, Any]]] = {}
        for reorder in reorders:
            supplier_email = reorder.get("supplier_email")
            if supplier_email:
                if supplier_email not in by_supplier:
                    by_supplier[supplier_email] = {
                        "supplier_name": reorder.get("supplier_name", "Proveedor"),
                        "reorders": [],
                    }
                by_supplier[supplier_email]["reorders"].append(reorder)
        
        sent_count = 0
        failed_count = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for supplier_email, supplier_data in by_supplier.items():
                    supplier_name = supplier_data["supplier_name"]
                    supplier_reorders = supplier_data["reorders"]
                    
                    # Preparar email
                    subject = f"Orden de Compra - {len(supplier_reorders)} producto(s)"
                    
                    # Calcular total
                    total_amount = sum(r.get("total_cost", 0) for r in supplier_reorders)
                    
                    html_body = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                            th {{ background-color: #f2f2f2; }}
                            .total {{ font-weight: bold; background-color: #e8f4f8; }}
                        </style>
                    </head>
                    <body>
                        <h2>Orden de Compra</h2>
                        <p>Estimado/a {supplier_name},</p>
                        <p>Por favor, procese la siguiente orden de compra:</p>
                        
                        <table>
                            <tr>
                                <th>SKU</th>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Costo Unitario</th>
                                <th>Total</th>
                                <th>Prioridad</th>
                            </tr>
                    """
                    
                    for reorder in supplier_reorders:
                        priority_emoji = {
                            "urgent": "🔴",
                            "high": "🟠",
                            "normal": "🟡",
                            "low": "🟢",
                        }.get(reorder.get("priority", "normal"), "")
                        
                        html_body += f"""
                            <tr>
                                <td>{reorder.get('sku', 'N/A')}</td>
                                <td>{reorder.get('product_name', 'N/A')}</td>
                                <td>{reorder.get('quantity', 0)}</td>
                                <td>${reorder.get('unit_cost', 0):,.2f}</td>
                                <td>${reorder.get('total_cost', 0):,.2f}</td>
                                <td>{priority_emoji} {reorder.get('priority', 'normal')}</td>
                            </tr>
                        """
                        
                        # Marcar como enviado
                        cur.execute(
                            """
                            UPDATE inventory_reorders
                            SET status = 'sent',
                                sent_at = NOW(),
                                updated_at = NOW()
                            WHERE id = %s
                            """,
                            (reorder["id"],),
                        )
                    
                    html_body += f"""
                            <tr class="total">
                                <td colspan="4" style="text-align: right;">Total:</td>
                                <td>${total_amount:,.2f}</td>
                                <td></td>
                            </tr>
                        </table>
                        
                        <p>Fecha esperada de entrega: {supplier_reorders[0].get('expected_delivery_date', 'A coordinar')}</p>
                        <p>Por favor, confirme la recepción de esta orden.</p>
                        <p>Saludos cordiales,<br>Sistema de Inventario</p>
                    </body>
                    </html>
                    """
                    
                    try:
                        notify_email(
                            subject=subject,
                            body=f"Orden de compra con {len(supplier_reorders)} producto(s). Total: ${total_amount:,.2f}",
                            html=html_body,
                            to=supplier_email,
                        )
                        sent_count += len(supplier_reorders)
                        logger.info(f"Sent reorder email to {supplier_email} ({len(supplier_reorders)} items)")
                    except Exception as e:
                        failed_count += len(supplier_reorders)
                        logger.error(f"Failed to send email to {supplier_email}: {e}", exc_info=True)
                        # Revertir status
                        for reorder in supplier_reorders:
                            cur.execute(
                                "UPDATE inventory_reorders SET status = 'pending', sent_at = NULL WHERE id = %s",
                                (reorder["id"],),
                            )
                
                conn.commit()
        
        logger.info(f"Sent {sent_count} reorders, failed {failed_count}")
        return {"sent": sent_count, "failed": failed_count}

    # Pipeline
    reorders_data = find_pending_reorders()
    result = send_reorder_emails(reorders_data)

    return None


dag = inventory_supplier_notifications()

