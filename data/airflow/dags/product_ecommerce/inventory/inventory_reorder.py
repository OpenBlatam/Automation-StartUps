"""
DAG de Reorden Automático de Inventario
Genera reordenes automáticos basados en stock bajo, velocidad de venta y lead time.
"""
from __future__ import annotations

from datetime import timedelta, date
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


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


def calculate_reorder_quantity(
    current_stock: int,
    reorder_point: int,
    reorder_quantity: int,
    sales_velocity: Optional[float] = None,
    lead_time_days: int = 7,
) -> int:
    """
    Calcula la cantidad óptima de reorden basado en múltiples factores.
    
    Args:
        current_stock: Stock actual disponible
        reorder_point: Punto de reorden configurado
        reorder_quantity: Cantidad de reorden por defecto
        sales_velocity: Unidades vendidas por día (opcional)
        lead_time_days: Días de lead time del proveedor
    
    Returns:
        Cantidad recomendada para reorden
    """
    # Si hay velocidad de venta, calcular cantidad basada en cobertura
    if sales_velocity and sales_velocity > 0:
        # Necesitamos cubrir: lead_time + buffer (7 días adicionales)
        days_coverage = lead_time_days + 7
        stock_needed = int(sales_velocity * days_coverage)
        # Stock actual más lo que ya está en camino
        stock_needed = max(stock_needed - current_stock, reorder_quantity)
        return max(stock_needed, reorder_quantity)
    
    # Fallback a cantidad por defecto, pero ajustada si stock está muy bajo
    if current_stock <= reorder_point * 0.3:
        # Si está muy bajo, ordenar más
        return int(reorder_quantity * 1.5)
    
    return reorder_quantity


def determine_priority(
    current_stock: int,
    reorder_point: int,
    days_until_stockout: Optional[int] = None,
) -> str:
    """Determina la prioridad del reorden."""
    if current_stock == 0:
        return "urgent"
    elif days_until_stockout and days_until_stockout <= 3:
        return "urgent"
    elif current_stock <= reorder_point * 0.3:
        return "high"
    elif current_stock <= reorder_point * 0.5:
        return "high"
    else:
        return "normal"


@dag(
    dag_id="inventory_reorder",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */4 * * *",  # Cada 4 horas
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "email_on_failure": False,
        "email_on_retry": False,
    },
    description="Genera reordenes automáticos para productos con stock bajo",
    tags=["inventory", "reorder", "automation"],
)
def inventory_reorder() -> None:
    """DAG principal de reorden automático."""

    @task(task_id="find_products_needing_reorder")
    def find_products_needing_reorder() -> Dict[str, Any]:
        """Encuentra productos que necesitan reorden."""
        logger.info("Finding products needing reorder...")
        
        # Buscar productos con stock bajo que no tengan reordenes pendientes
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                p.category,
                p.reorder_point,
                p.reorder_quantity,
                p.max_stock,
                p.lead_time_days,
                p.unit_cost,
                p.supplier_id,
                p.supplier_name,
                p.supplier_email,
                COALESCE(s.available_quantity, 0) AS current_stock,
                s.id AS stock_id,
                -- Calcular velocidad de venta (unidades/día en últimos 30 días)
                (SELECT COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                 FROM inventory_movements 
                 WHERE product_id = p.id 
                 AND movement_type = 'sale' 
                 AND created_at >= NOW() - INTERVAL '30 days') AS sales_velocity_30d,
                -- Días hasta quiebre estimado
                CASE 
                    WHEN COALESCE(s.available_quantity, 0) = 0 THEN 0
                    WHEN (SELECT COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                          FROM inventory_movements 
                          WHERE product_id = p.id 
                          AND movement_type = 'sale' 
                          AND created_at >= NOW() - INTERVAL '30 days') > 0
                    THEN COALESCE(s.available_quantity, 0)::DECIMAL / 
                         NULLIF((SELECT COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                                 FROM inventory_movements 
                                 WHERE product_id = p.id 
                                 AND movement_type = 'sale' 
                                 AND created_at >= NOW() - INTERVAL '30 days'), 0), 0
                    ELSE NULL
                END AS days_until_stockout
            FROM inventory_products p
            LEFT JOIN inventory_stock s ON p.id = s.product_id
            WHERE p.active = TRUE
            AND COALESCE(s.available_quantity, 0) <= p.reorder_point
            AND NOT EXISTS (
                -- Excluir productos con reordenes pendientes
                SELECT 1 FROM inventory_reorders r
                WHERE r.product_id = p.id
                AND r.status IN ('pending', 'sent', 'confirmed')
            )
            ORDER BY 
                CASE WHEN COALESCE(s.available_quantity, 0) = 0 THEN 1 ELSE 2 END,
                COALESCE(s.available_quantity, 0)
        """
        
        products = _query_dict(sql)
        logger.info(f"Found {len(products)} products needing reorder")
        
        return {"products": products, "count": len(products)}

    @task(task_id="generate_reorders")
    def generate_reorders(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reordenes automáticos para los productos identificados."""
        products = payload.get("products", [])
        if not products:
            logger.info("No products needing reorder")
            return payload
        
        reorders_created = 0
        reorders_skipped = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for product in products:
                    product_id = product["id"]
                    current_stock = product.get("current_stock", 0)
                    reorder_point = product.get("reorder_point", 0)
                    reorder_quantity = product.get("reorder_quantity", 50)
                    sales_velocity = product.get("sales_velocity_30d")
                    lead_time_days = product.get("lead_time_days", 7)
                    unit_cost = product.get("unit_cost")
                    
                    # Calcular cantidad óptima de reorden
                    reorder_qty = calculate_reorder_quantity(
                        current_stock=current_stock,
                        reorder_point=reorder_point,
                        reorder_quantity=reorder_quantity,
                        sales_velocity=float(sales_velocity) if sales_velocity else None,
                        lead_time_days=lead_time_days,
                    )
                    
                    # Aplicar límite de max_stock si existe
                    if product.get("max_stock"):
                        max_stock = product["max_stock"]
                        if current_stock + reorder_qty > max_stock:
                            reorder_qty = max(0, max_stock - current_stock)
                    
                    if reorder_qty <= 0:
                        reorders_skipped += 1
                        logger.debug(f"Skipping reorder for {product['sku']}: calculated quantity is 0")
                        continue
                    
                    # Determinar prioridad
                    days_until_stockout = product.get("days_until_stockout")
                    priority = determine_priority(
                        current_stock=current_stock,
                        reorder_point=reorder_point,
                        days_until_stockout=int(days_until_stockout) if days_until_stockout else None,
                    )
                    
                    # Calcular fecha esperada de entrega
                    expected_delivery = date.today() + timedelta(days=lead_time_days)
                    
                    # Crear reorden
                    insert_sql = """
                        INSERT INTO inventory_reorders (
                            product_id, quantity, unit_cost, status, priority,
                            supplier_id, supplier_name, supplier_email,
                            expected_delivery_date
                        ) VALUES (%s, %s, %s, 'pending', %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    cur.execute(
                        insert_sql,
                        (
                            product_id,
                            reorder_qty,
                            unit_cost,
                            priority,
                            product.get("supplier_id"),
                            product.get("supplier_name"),
                            product.get("supplier_email"),
                            expected_delivery,
                        ),
                    )
                    reorder_id = cur.fetchone()[0]
                    reorders_created += 1
                    
                    logger.info(
                        f"Created reorder {reorder_id} for product {product['sku']}: "
                        f"{reorder_qty} units, priority {priority}, delivery {expected_delivery}"
                    )
            
            conn.commit()
        
        payload["reorders_created"] = reorders_created
        payload["reorders_skipped"] = reorders_skipped
        logger.info(f"Created {reorders_created} reorders, skipped {reorders_skipped}")
        
        return payload

    @task(task_id="send_reorder_notifications")
    def send_reorder_notifications(payload: Dict[str, Any]) -> None:
        """Envía notificaciones sobre reordenes generados."""
        if not NOTIFICATIONS_AVAILABLE:
            return
        
        reorders_created = payload.get("reorders_created", 0)
        products = payload.get("products", [])
        
        if reorders_created == 0:
            logger.info("No reorders created, no notifications needed")
            return
        
        # Preparar mensaje Slack
        slack_msg = f"📦 *Reordenes Automáticos Generados*\n\n"
        slack_msg += f"✅ {reorders_created} reorden(es) creado(s)\n\n"
        
        # Agrupar por proveedor
        by_supplier: Dict[str, List[Dict[str, Any]]] = {}
        for product in products[:10]:  # Top 10
            supplier = product.get("supplier_name") or "Sin proveedor"
            if supplier not in by_supplier:
                by_supplier[supplier] = []
            by_supplier[supplier].append(product)
        
        for supplier, supplier_products in list(by_supplier.items())[:5]:
            slack_msg += f"*{supplier}* ({len(supplier_products)} producto(s)):\n"
            for product in supplier_products[:3]:
                slack_msg += f"• {product['sku']}: {product.get('reorder_quantity', 0)} unidades\n"
            slack_msg += "\n"
        
        try:
            notify_slack(slack_msg)
            logger.info("Slack notification sent")
        except Exception as e:
            logger.warning(f"Failed to send Slack notification: {e}", exc_info=True)
        
        # Enviar email a proveedores si hay configuración
        # Esto se puede expandir para enviar emails directamente a proveedores

    @task(task_id="log_metrics")
    def log_metrics(payload: Dict[str, Any]) -> None:
        """Registra métricas del reorden."""
        reorders_created = payload.get("reorders_created", 0)
        total_products = payload.get("count", 0)
        
        logger.info(
            "Inventory reorder metrics",
            extra={
                "reorders_created": reorders_created,
                "total_products_checked": total_products,
            },
        )
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("inventory.reorder.created", reorders_created)
                Stats.gauge("inventory.reorder.products_checked", total_products)
            except Exception:
                pass

    # Pipeline
    products_data = find_products_needing_reorder()
    reorders_data = generate_reorders(products_data)
    send_reorder_notifications(reorders_data)
    log_metrics(reorders_data)

    return None


dag = inventory_reorder()





