"""
DAG de Optimización de Costos de Inventario
Analiza y optimiza costos de almacenamiento, rotación y sobrestock.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, List, Tuple

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.db import get_conn

try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


@dag(
    dag_id="inventory_cost_optimization",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 4 * * 1",  # Semanal los lunes a las 4:00 AM
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Optimización de costos de inventario y análisis de sobrestock",
    tags=["inventory", "optimization", "costs"],
)
def inventory_cost_optimization() -> None:
    """DAG de optimización de costos."""

    @task(task_id="analyze_overstock")
    def analyze_overstock() -> Dict[str, Any]:
        """Analiza productos con sobrestock."""
        logger.info("Analyzing overstock products...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                p.category,
                s.available_quantity AS current_stock,
                p.max_stock,
                p.reorder_point,
                p.unit_cost,
                s.available_quantity * p.unit_cost AS inventory_value,
                -- Calcular días de stock basado en velocidad de venta
                CASE 
                    WHEN (SELECT COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                          FROM inventory_movements 
                          WHERE product_id = p.id 
                          AND movement_type = 'sale' 
                          AND created_at >= NOW() - INTERVAL '30 days') > 0
                    THEN s.available_quantity::DECIMAL / 
                         NULLIF((SELECT COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                                 FROM inventory_movements 
                                 WHERE product_id = p.id 
                                 AND movement_type = 'sale' 
                                 AND created_at >= NOW() - INTERVAL '30 days'), 0)
                    ELSE NULL
                END AS days_of_stock,
                -- Calcular costo de almacenamiento (asumiendo 1% mensual del valor)
                s.available_quantity * p.unit_cost * 0.01 / 30 AS daily_storage_cost
            FROM inventory_products p
            JOIN inventory_stock s ON p.id = s.product_id
            WHERE p.active = TRUE
            AND (
                (p.max_stock IS NOT NULL AND s.available_quantity > p.max_stock)
                OR (s.available_quantity > p.reorder_point * 3)
            )
            AND s.available_quantity > 0
            ORDER BY s.available_quantity * p.unit_cost DESC
        """
        
        overstock = _query_dict(sql)
        
        total_overstock_value = sum(p.get("inventory_value", 0) for p in overstock)
        total_storage_cost = sum(p.get("daily_storage_cost", 0) for p in overstock)
        
        logger.info(
            f"Found {len(overstock)} overstock products, "
            f"total value: ${total_overstock_value:,.2f}, "
            f"daily storage cost: ${total_storage_cost:,.2f}"
        )
        
        return {
            "overstock_products": overstock,
            "count": len(overstock),
            "total_value": total_overstock_value,
            "total_daily_storage_cost": total_storage_cost,
        }

    @task(task_id="analyze_slow_moving")
    def analyze_slow_moving() -> Dict[str, Any]:
        """Analiza productos de movimiento lento."""
        logger.info("Analyzing slow-moving products...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                p.category,
                s.available_quantity,
                s.available_quantity * p.unit_cost AS inventory_value,
                COALESCE(
                    (SELECT SUM(quantity)
                     FROM inventory_movements 
                     WHERE product_id = p.id 
                     AND movement_type = 'sale' 
                     AND created_at >= NOW() - INTERVAL '90 days'), 0
                ) AS sales_90d,
                COALESCE(
                    (SELECT SUM(quantity)
                     FROM inventory_movements 
                     WHERE product_id = p.id 
                     AND movement_type = 'sale' 
                     AND created_at >= NOW() - INTERVAL '30 days'), 0
                ) AS sales_30d,
                s.last_sold_at,
                EXTRACT(EPOCH FROM (NOW() - COALESCE(s.last_sold_at, p.created_at))) / 86400 AS days_since_last_sale
            FROM inventory_products p
            JOIN inventory_stock s ON p.id = s.product_id
            WHERE p.active = TRUE
            AND s.available_quantity > 0
            AND (
                -- Sin ventas en últimos 90 días
                (SELECT COUNT(*) FROM inventory_movements 
                 WHERE product_id = p.id AND movement_type = 'sale' 
                 AND created_at >= NOW() - INTERVAL '90 days') = 0
                OR
                -- Más de 180 días sin venta
                (s.last_sold_at IS NOT NULL AND s.last_sold_at < NOW() - INTERVAL '180 days')
            )
            ORDER BY s.available_quantity * p.unit_cost DESC
        """
        
        slow_moving = _query_dict(sql)
        
        total_value = sum(p.get("inventory_value", 0) for p in slow_moving)
        
        logger.info(f"Found {len(slow_moving)} slow-moving products, total value: ${total_value:,.2f}")
        
        return {
            "slow_moving_products": slow_moving,
            "count": len(slow_moving),
            "total_value": total_value,
        }

    @task(task_id="calculate_optimization_recommendations")
    def calculate_optimization_recommendations(
        overstock_data: Dict[str, Any],
        slow_moving_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calcula recomendaciones de optimización."""
        logger.info("Calculating optimization recommendations...")
        
        recommendations = []
        total_savings_potential = 0.0
        
        # Recomendaciones para sobrestock
        for product in overstock_data.get("overstock_products", [])[:10]:
            current_stock = product.get("current_stock", 0)
            max_stock = product.get("max_stock") or (product.get("reorder_point", 0) * 2)
            excess = current_stock - max_stock
            
            if excess > 0:
                excess_value = excess * product.get("unit_cost", 0)
                recommendation = {
                    "type": "reduce_stock",
                    "product_sku": product.get("sku"),
                    "product_name": product.get("name"),
                    "current_stock": current_stock,
                    "recommended_stock": max_stock,
                    "excess_units": excess,
                    "excess_value": excess_value,
                    "action": f"Reducir stock de {current_stock} a {max_stock} unidades",
                    "savings": excess_value * 0.01 * 30,  # Ahorro mensual estimado
                }
                recommendations.append(recommendation)
                total_savings_potential += recommendation["savings"]
        
        # Recomendaciones para productos de movimiento lento
        for product in slow_moving_data.get("slow_moving_products", [])[:10]:
            current_value = product.get("inventory_value", 0)
            days_since_sale = product.get("days_since_last_sale", 0)
            
            if days_since_sale > 180:
                recommendation = {
                    "type": "liquidate",
                    "product_sku": product.get("sku"),
                    "product_name": product.get("name"),
                    "inventory_value": current_value,
                    "days_since_last_sale": int(days_since_last_sale),
                    "action": "Considerar liquidación o descuento",
                    "savings": current_value * 0.5,  # Recuperar 50% del valor
                }
                recommendations.append(recommendation)
                total_savings_potential += recommendation["savings"]
        
        logger.info(f"Generated {len(recommendations)} optimization recommendations")
        
        return {
            "recommendations": recommendations,
            "total_savings_potential": total_savings_potential,
            "count": len(recommendations),
        }

    @task(task_id="send_optimization_report")
    def send_optimization_report(
        overstock_data: Dict[str, Any],
        slow_moving_data: Dict[str, Any],
        recommendations: Dict[str, Any],
    ) -> None:
        """Envía reporte de optimización."""
        if not NOTIFICATIONS_AVAILABLE:
            return
        
        overstock_count = overstock_data.get("count", 0)
        slow_moving_count = slow_moving_data.get("slow_moving_products", [])
        recs = recommendations.get("recommendations", [])
        total_savings = recommendations.get("total_savings_potential", 0)
        
        slack_msg = f"💰 *Reporte de Optimización de Costos de Inventario*\n\n"
        slack_msg += f"📊 *Resumen:*\n"
        slack_msg += f"• Productos con sobrestock: {overstock_data.get('count', 0)}\n"
        slack_msg += f"  └ Valor total: ${overstock_data.get('total_value', 0):,.2f}\n"
        slack_msg += f"  └ Costo diario almacenamiento: ${overstock_data.get('total_daily_storage_cost', 0):,.2f}\n"
        slack_msg += f"• Productos de movimiento lento: {slow_moving_data.get('count', 0)}\n"
        slack_msg += f"  └ Valor total: ${slow_moving_data.get('total_value', 0):,.2f}\n"
        slack_msg += f"• Recomendaciones generadas: {len(recs)}\n"
        slack_msg += f"• Ahorro potencial estimado: ${total_savings:,.2f}/mes\n\n"
        
        if recs:
            slack_msg += f"*Top 5 Recomendaciones:*\n"
            for i, rec in enumerate(recs[:5], 1):
                slack_msg += f"{i}. {rec['type']}: {rec['product_sku']}\n"
                slack_msg += f"   {rec['action']}\n"
                slack_msg += f"   Ahorro: ${rec.get('savings', 0):,.2f}/mes\n"
        
        try:
            notify_slack(slack_msg)
            logger.info("Optimization report sent")
        except Exception as e:
            logger.warning(f"Failed to send optimization report: {e}", exc_info=True)

    # Pipeline
    overstock = analyze_overstock()
    slow_moving = analyze_slow_moving()
    recommendations = calculate_optimization_recommendations(overstock, slow_moving)
    send_optimization_report(overstock, slow_moving, recommendations)

    return None


dag = inventory_cost_optimization()

