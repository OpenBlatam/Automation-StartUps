"""
DAG de Monitoreo de Inventario
Monitorea stocks, genera alertas y detecta productos con stock bajo o quiebre de inventario.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.db import get_conn

# Librerías mejoradas
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        RetryError,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from data.airflow.plugins.etl_notifications import notify_slack, notify_email
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack, notify_email
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

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


def _query_rows(sql: str, params: Tuple[Any, ...] | None = None) -> List[Tuple[Any, ...]]:
    """Ejecuta query y retorna todas las filas."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


@dag(
    dag_id="inventory_monitor",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="*/30 * * * *",  # Cada 30 minutos
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
        "email_on_failure": False,
        "email_on_retry": False,
    },
    description="Monitoreo continuo de inventario con alertas de stock bajo y quiebre",
    tags=["inventory", "monitoring", "alerts"],
)
def inventory_monitor() -> None:
    """DAG principal de monitoreo de inventario."""

    @task(task_id="check_stock_levels")
    def check_stock_levels() -> Dict[str, Any]:
        """Verifica niveles de stock y detecta productos críticos."""
        logger.info("Checking stock levels...")
        
        # Buscar productos con stock bajo o sin stock
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                p.category,
                p.reorder_point,
                p.reorder_quantity,
                p.supplier_name,
                p.supplier_email,
                p.lead_time_days,
                COALESCE(s.available_quantity, 0) AS current_stock,
                s.id AS stock_id,
                s.last_sold_at,
                -- Calcular días hasta quiebre estimado
                CASE 
                    WHEN COALESCE(s.available_quantity, 0) = 0 THEN 0
                    WHEN s.last_sold_at IS NULL THEN NULL
                    ELSE GREATEST(1, 
                        EXTRACT(EPOCH FROM (NOW() - s.last_sold_at)) / 86400.0 / 
                        NULLIF(COALESCE(s.available_quantity, 0), 0) * 
                        (SELECT COUNT(*)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1)
                         FROM inventory_movements 
                         WHERE product_id = p.id 
                         AND movement_type = 'sale' 
                         AND created_at >= NOW() - INTERVAL '30 days')
                    )::INTEGER
                END AS days_until_stockout
            FROM inventory_products p
            LEFT JOIN inventory_stock s ON p.id = s.product_id
            WHERE p.active = TRUE
            AND (
                COALESCE(s.available_quantity, 0) = 0
                OR COALESCE(s.available_quantity, 0) <= p.reorder_point
            )
            ORDER BY 
                CASE WHEN COALESCE(s.available_quantity, 0) = 0 THEN 1 ELSE 2 END,
                COALESCE(s.available_quantity, 0)
        """
        
        critical_products = _query_dict(sql)
        logger.info(f"Found {len(critical_products)} products with low/out of stock")
        
        return {
            "critical_products": critical_products,
            "total_critical": len(critical_products),
            "out_of_stock": len([p for p in critical_products if p.get("current_stock", 0) == 0]),
            "low_stock": len([p for p in critical_products if p.get("current_stock", 0) > 0]),
        }

    @task(task_id="create_alerts")
    def create_alerts(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Crea alertas en la base de datos para productos críticos."""
        critical_products = payload.get("critical_products", [])
        if not critical_products:
            logger.info("No critical products to alert")
            return payload
        
        alerts_created = 0
        alerts_skipped = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for product in critical_products:
                    product_id = product["id"]
                    stock_id = product.get("stock_id")
                    current_stock = product.get("current_stock", 0)
                    reorder_point = product.get("reorder_point", 0)
                    
                    # Determinar tipo y severidad de alerta
                    if current_stock == 0:
                        alert_type = "out_of_stock"
                        severity = "critical"
                        message = f"Producto {product['sku']} ({product['name']}) está sin stock"
                    elif current_stock <= reorder_point * 0.5:
                        alert_type = "low_stock"
                        severity = "high"
                        message = f"Producto {product['sku']} ({product['name']}) tiene stock crítico: {current_stock} unidades (punto de reorden: {reorder_point})"
                    else:
                        alert_type = "low_stock"
                        severity = "medium"
                        message = f"Producto {product['sku']} ({product['name']}) está bajo el punto de reorden: {current_stock}/{reorder_point}"
                    
                    # Verificar si ya existe una alerta abierta del mismo tipo
                    check_sql = """
                        SELECT id FROM inventory_alerts
                        WHERE product_id = %s
                        AND alert_type = %s
                        AND status IN ('open', 'acknowledged')
                        LIMIT 1
                    """
                    cur.execute(check_sql, (product_id, alert_type))
                    existing = cur.fetchone()
                    
                    if existing:
                        alerts_skipped += 1
                        logger.debug(f"Alert already exists for product {product['sku']}, type {alert_type}")
                        continue
                    
                    # Crear nueva alerta
                    insert_sql = """
                        INSERT INTO inventory_alerts (
                            product_id, stock_id, alert_type, severity, status,
                            current_stock, reorder_point, message
                        ) VALUES (%s, %s, %s, %s, 'open', %s, %s, %s)
                        RETURNING id
                    """
                    cur.execute(
                        insert_sql,
                        (
                            product_id,
                            stock_id,
                            alert_type,
                            severity,
                            current_stock,
                            reorder_point,
                            message,
                        ),
                    )
                    alert_id = cur.fetchone()[0]
                    alerts_created += 1
                    logger.info(f"Created alert {alert_id} for product {product['sku']}")
            
            conn.commit()
        
        payload["alerts_created"] = alerts_created
        payload["alerts_skipped"] = alerts_skipped
        logger.info(f"Created {alerts_created} new alerts, skipped {alerts_skipped} duplicates")
        
        return payload

    @task(task_id="check_expiring_products")
    def check_expiring_products() -> Dict[str, Any]:
        """Verifica productos próximos a vencer (si aplica)."""
        logger.info("Checking for expiring products...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                s.available_quantity,
                s.expires_at,
                EXTRACT(EPOCH FROM (s.expires_at - NOW())) / 86400 AS days_until_expiry
            FROM inventory_products p
            JOIN inventory_stock s ON p.id = s.product_id
            WHERE s.expires_at IS NOT NULL
            AND s.expires_at > NOW()
            AND s.expires_at <= NOW() + INTERVAL '30 days'
            AND s.available_quantity > 0
            ORDER BY s.expires_at
        """
        
        expiring = _query_dict(sql)
        logger.info(f"Found {len(expiring)} products expiring soon")
        
        # Crear alertas para productos que expiran pronto
        if expiring:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for product in expiring:
                        days = int(product.get("days_until_expiry", 0))
                        severity = "high" if days <= 7 else "medium"
                        
                        # Verificar si ya existe alerta
                        check_sql = """
                            SELECT id FROM inventory_alerts
                            WHERE product_id = %s
                            AND alert_type = 'expiring_soon'
                            AND status IN ('open', 'acknowledged')
                            LIMIT 1
                        """
                        cur.execute(check_sql, (product["id"],))
                        if cur.fetchone():
                            continue
                        
                        # Crear alerta
                        insert_sql = """
                            INSERT INTO inventory_alerts (
                                product_id, stock_id, alert_type, severity, status, message
                            ) VALUES (
                                %s, 
                                (SELECT id FROM inventory_stock WHERE product_id = %s LIMIT 1),
                                'expiring_soon',
                                %s,
                                'open',
                                %s
                            )
                        """
                        message = f"Producto {product['sku']} expira en {days} días"
                        cur.execute(
                            insert_sql,
                            (
                                product["id"],
                                product["id"],
                                severity,
                                message,
                            ),
                        )
                
                conn.commit()
        
        return {"expiring_products": expiring, "count": len(expiring)}

    @task(task_id="send_notifications")
    def send_notifications(payload: Dict[str, Any]) -> None:
        """Envía notificaciones para alertas críticas."""
        if not NOTIFICATIONS_AVAILABLE:
            logger.warning("Notifications not available, skipping")
            return
        
        critical_products = payload.get("critical_products", [])
        total_critical = payload.get("total_critical", 0)
        out_of_stock = payload.get("out_of_stock", 0)
        alerts_created = payload.get("alerts_created", 0)
        
        if total_critical == 0:
            logger.info("No critical products, no notifications needed")
            return
        
        # Preparar mensaje Slack
        slack_msg = f"📦 *Alerta de Inventario*\n\n"
        slack_msg += f"🚨 {total_critical} producto(s) requieren atención:\n"
        slack_msg += f"• Sin stock: {out_of_stock}\n"
        slack_msg += f"• Stock bajo: {total_critical - out_of_stock}\n"
        slack_msg += f"• Nuevas alertas creadas: {alerts_created}\n\n"
        
        if critical_products:
            slack_msg += "*Top 5 productos críticos:*\n"
            for i, product in enumerate(critical_products[:5], 1):
                stock = product.get("current_stock", 0)
                reorder = product.get("reorder_point", 0)
                status = "🔴 Sin stock" if stock == 0 else f"⚠️ Stock bajo ({stock}/{reorder})"
                slack_msg += f"{i}. *{product['sku']}* - {product['name'][:50]}\n"
                slack_msg += f"   {status}\n"
        
        try:
            notify_slack(slack_msg)
            logger.info("Slack notification sent")
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}", exc_info=True)
        
        # Enviar email si hay productos sin stock
        if out_of_stock > 0:
            email_subject = f"ALERTA: {out_of_stock} productos sin stock"
            email_body = f"""
            <h2>Alerta de Inventario - Productos Sin Stock</h2>
            <p>Se detectaron <strong>{out_of_stock}</strong> productos sin stock.</p>
            
            <h3>Productos sin stock:</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr>
                    <th>SKU</th>
                    <th>Nombre</th>
                    <th>Categoría</th>
                    <th>Proveedor</th>
                    <th>Punto de Reorden</th>
                </tr>
            """
            
            for product in critical_products:
                if product.get("current_stock", 0) == 0:
                    email_body += f"""
                    <tr>
                        <td>{product['sku']}</td>
                        <td>{product['name']}</td>
                        <td>{product.get('category', 'N/A')}</td>
                        <td>{product.get('supplier_name', 'N/A')}</td>
                        <td>{product.get('reorder_point', 0)}</td>
                    </tr>
                    """
            
            email_body += "</table>"
            
            try:
                notify_email(
                    subject=email_subject,
                    body=email_body,
                    html=email_body,
                    to=None,  # Usa configuración por defecto
                )
                logger.info("Email notification sent")
            except Exception as e:
                logger.warning(f"Failed to send email notification: {e}", exc_info=True)

    @task(task_id="log_metrics")
    def log_metrics(payload: Dict[str, Any]) -> None:
        """Registra métricas del monitoreo."""
        total_critical = payload.get("total_critical", 0)
        out_of_stock = payload.get("out_of_stock", 0)
        alerts_created = payload.get("alerts_created", 0)
        
        logger.info(
            "Inventory monitoring metrics",
            extra={
                "total_critical": total_critical,
                "out_of_stock": out_of_stock,
                "low_stock": total_critical - out_of_stock,
                "alerts_created": alerts_created,
            },
        )
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("inventory.monitor.critical_products", total_critical)
                Stats.incr("inventory.monitor.out_of_stock", out_of_stock)
                Stats.incr("inventory.monitor.alerts_created", alerts_created)
            except Exception:
                pass

    # Pipeline
    stock_data = check_stock_levels()
    alerts_data = create_alerts(stock_data)
    expiring_data = check_expiring_products()
    send_notifications(alerts_data)
    log_metrics(alerts_data)

    return None


dag = inventory_monitor()





