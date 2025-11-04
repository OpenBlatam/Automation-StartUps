"""
DAG de Predicción de Demanda
Calcula predicciones de demanda futura usando métodos estadísticos simples
y actualiza la tabla de forecast para optimizar reordenes.
"""
from __future__ import annotations

from datetime import timedelta, date
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

from data.airflow.plugins.db import get_conn

logger = logging.getLogger(__name__)


def _query_dict(sql: str, params: Tuple[Any, ...] | None = None) -> List[Dict[str, Any]]:
    """Ejecuta query y retorna filas como diccionarios."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]


def calculate_moving_average(sales_data: List[int], window: int = 7) -> float:
    """Calcula promedio móvil simple."""
    if not sales_data or len(sales_data) < window:
        return 0.0
    return sum(sales_data[-window:]) / window


def calculate_exponential_smoothing(sales_data: List[int], alpha: float = 0.3) -> float:
    """Calcula suavizado exponencial simple."""
    if not sales_data:
        return 0.0
    
    forecast = float(sales_data[0])
    for value in sales_data[1:]:
        forecast = alpha * float(value) + (1 - alpha) * forecast
    
    return forecast


@dag(
    dag_id="inventory_demand_forecast",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 2 * * *",  # Diario a las 2:00 AM
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Predicción de demanda para optimización de inventario",
    tags=["inventory", "forecast", "ml"],
)
def inventory_demand_forecast() -> None:
    """DAG de predicción de demanda."""

    @task(task_id="collect_sales_history")
    def collect_sales_history() -> Dict[str, Any]:
        """Recopila historial de ventas por producto."""
        logger.info("Collecting sales history...")
        
        # Obtener ventas de últimos 90 días por producto
        sql = """
            SELECT 
                p.id AS product_id,
                p.sku,
                DATE(m.created_at) AS sale_date,
                SUM(m.quantity) AS daily_sales
            FROM inventory_products p
            JOIN inventory_movements m ON p.id = m.product_id
            WHERE m.movement_type = 'sale'
            AND m.created_at >= NOW() - INTERVAL '90 days'
            AND p.active = TRUE
            GROUP BY p.id, p.sku, DATE(m.created_at)
            ORDER BY p.id, sale_date
        """
        
        sales_data = _query_dict(sql)
        
        # Agrupar por producto
        products_sales: Dict[str, List[Dict[str, Any]]] = {}
        for sale in sales_data:
            product_id = sale["product_id"]
            if product_id not in products_sales:
                products_sales[product_id] = []
            products_sales[product_id].append(sale)
        
        logger.info(f"Collected sales history for {len(products_sales)} products")
        return {"products_sales": products_sales}

    @task(task_id="calculate_forecasts")
    def calculate_forecasts(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula predicciones de demanda para los próximos 30 días."""
        products_sales = payload.get("products_sales", {})
        
        forecasts_created = 0
        forecasts_updated = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for product_id, sales_list in products_sales.items():
                    if not sales_list:
                        continue
                    
                    # Extraer cantidades diarias ordenadas
                    daily_sales = [s["daily_sales"] for s in sorted(sales_list, key=lambda x: x["sale_date"])]
                    
                    # Calcular diferentes métodos de predicción
                    ma_7 = calculate_moving_average(daily_sales, window=7)
                    ma_14 = calculate_moving_average(daily_sales, window=14)
                    ma_30 = calculate_moving_average(daily_sales, window=30)
                    es_forecast = calculate_exponential_smoothing(daily_sales, alpha=0.3)
                    
                    # Usar el promedio de los métodos como predicción final
                    methods = [m for m in [ma_7, ma_14, ma_30, es_forecast] if m > 0]
                    if not methods:
                        continue
                    
                    predicted_demand = int(sum(methods) / len(methods))
                    
                    # Calcular confianza basada en variabilidad
                    if len(daily_sales) >= 7:
                        variance = sum((x - predicted_demand) ** 2 for x in daily_sales[-7:]) / len(daily_sales[-7:])
                        std_dev = variance ** 0.5
                        avg_sales = sum(daily_sales[-7:]) / len(daily_sales[-7:])
                        if avg_sales > 0:
                            coefficient_variation = std_dev / avg_sales
                            confidence = max(50, min(100, 100 - (coefficient_variation * 100)))
                        else:
                            confidence = 50
                    else:
                        confidence = 50
                    
                    # Insertar o actualizar forecast para los próximos 30 días
                    for days_ahead in range(1, 31):
                        forecast_date = date.today() + timedelta(days=days_ahead)
                        
                        # Usar método de suavizado exponencial como método principal
                        upsert_sql = """
                            INSERT INTO inventory_demand_forecast (
                                product_id, forecast_date, predicted_demand,
                                confidence_level, forecast_method, model_version
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (product_id, forecast_date)
                            DO UPDATE SET
                                predicted_demand = EXCLUDED.predicted_demand,
                                confidence_level = EXCLUDED.confidence_level,
                                forecast_method = EXCLUDED.forecast_method,
                                model_version = EXCLUDED.model_version
                        """
                        
                        cur.execute(
                            upsert_sql,
                            (
                                product_id,
                                forecast_date,
                                predicted_demand,
                                confidence,
                                "exponential_smoothing",
                                "v1.0",
                            ),
                        )
                        
                        if days_ahead == 1:
                            forecasts_created += 1
                        forecasts_updated += 1
                
                conn.commit()
        
        logger.info(f"Created/updated {forecasts_updated} forecast entries for {forecasts_created} products")
        return {"forecasts_updated": forecasts_updated, "products_forecasted": forecasts_created}

    @task(task_id="optimize_reorder_points")
    def optimize_reorder_points(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza puntos de reorden basado en predicciones de demanda."""
        logger.info("Optimizing reorder points based on forecasts...")
        
        # Obtener productos con forecast y calcular reorden óptimo
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.reorder_point AS current_reorder_point,
                p.lead_time_days,
                AVG(df.predicted_demand) AS avg_predicted_demand,
                MAX(df.confidence_level) AS avg_confidence
            FROM inventory_products p
            JOIN inventory_demand_forecast df ON p.id = df.product_id
            WHERE df.forecast_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
            AND p.active = TRUE
            GROUP BY p.id, p.sku, p.reorder_point, p.lead_time_days
            HAVING AVG(df.predicted_demand) > 0
        """
        
        products = _query_dict(sql)
        
        optimized_count = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for product in products:
                    product_id = product["id"]
                    current_rp = product["current_reorder_point"]
                    avg_demand = float(product["avg_predicted_demand"])
                    lead_time = product["lead_time_days"] or 7
                    confidence = float(product["avg_confidence"])
                    
                    # Calcular nuevo punto de reorden: demanda diaria * (lead_time + buffer)
                    # Buffer = 7 días adicionales
                    buffer_days = 7
                    safety_stock = avg_demand * (lead_time + buffer_days) * 1.2  # 20% de seguridad
                    new_reorder_point = int(safety_stock)
                    
                    # Solo actualizar si la diferencia es significativa (>20%)
                    if abs(new_reorder_point - current_rp) / max(current_rp, 1) > 0.2:
                        # Solo actualizar si la confianza es razonable
                        if confidence >= 60:
                            update_sql = """
                                UPDATE inventory_products
                                SET reorder_point = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """
                            cur.execute(update_sql, (new_reorder_point, product_id))
                            optimized_count += 1
                            
                            logger.info(
                                f"Optimized reorder point for {product['sku']}: "
                                f"{current_rp} -> {new_reorder_point} (confidence: {confidence:.1f}%)"
                            )
                
                conn.commit()
        
        logger.info(f"Optimized reorder points for {optimized_count} products")
        return {"optimized_count": optimized_count}

    # Pipeline
    sales_data = collect_sales_history()
    forecasts_data = calculate_forecasts(sales_data)
    optimize_reorder_points(forecasts_data)

    return None


dag = inventory_demand_forecast()





