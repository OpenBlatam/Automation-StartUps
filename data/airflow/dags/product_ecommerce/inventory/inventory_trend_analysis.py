"""
DAG de Análisis de Tendencias de Inventario
Analiza tendencias de ventas, estacionalidad y patrones de demanda.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, List, Tuple

import pendulum
from airflow.decorators import dag, task

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


@dag(
    dag_id="inventory_trend_analysis",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 5 * * 1",  # Semanal los lunes a las 5:00 AM
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Análisis de tendencias y patrones de demanda",
    tags=["inventory", "analysis", "trends"],
)
def inventory_trend_analysis() -> None:
    """DAG de análisis de tendencias."""

    @task(task_id="analyze_sales_trends")
    def analyze_sales_trends() -> Dict[str, Any]:
        """Analiza tendencias de ventas por producto."""
        logger.info("Analyzing sales trends...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                DATE_TRUNC('week', m.created_at) AS week,
                SUM(m.quantity) AS weekly_sales
            FROM inventory_products p
            JOIN inventory_movements m ON p.id = m.product_id
            WHERE m.movement_type = 'sale'
            AND m.created_at >= NOW() - INTERVAL '12 weeks'
            AND p.active = TRUE
            GROUP BY p.id, p.sku, p.name, DATE_TRUNC('week', m.created_at)
            ORDER BY p.id, week
        """
        
        trends = _query_dict(sql)
        
        # Agrupar por producto y calcular tendencia
        product_trends = {}
        for trend in trends:
            product_id = trend["id"]
            if product_id not in product_trends:
                product_trends[product_id] = {
                    "sku": trend["sku"],
                    "name": trend["name"],
                    "weekly_sales": [],
                }
            product_trends[product_id]["weekly_sales"].append(trend["weekly_sales"])
        
        # Calcular tendencia (incremento/decremento)
        trend_analysis = []
        for product_id, data in product_trends.items():
            sales = data["weekly_sales"]
            if len(sales) >= 4:
                # Comparar últimas 4 semanas vs anteriores 4 semanas
                recent_avg = sum(sales[-4:]) / len(sales[-4:])
                previous_avg = sum(sales[-8:-4]) / len(sales[-8:-4]) if len(sales) >= 8 else recent_avg
                
                if previous_avg > 0:
                    change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
                    trend_direction = "increasing" if change_pct > 10 else "decreasing" if change_pct < -10 else "stable"
                else:
                    change_pct = 0
                    trend_direction = "stable"
                
                trend_analysis.append({
                    "product_id": product_id,
                    "sku": data["sku"],
                    "name": data["name"],
                    "trend_direction": trend_direction,
                    "change_percent": change_pct,
                    "recent_avg": recent_avg,
                    "previous_avg": previous_avg,
                })
        
        logger.info(f"Analyzed trends for {len(trend_analysis)} products")
        return {"trends": trend_analysis}

    @task(task_id="detect_seasonality")
    def detect_seasonality() -> Dict[str, Any]:
        """Detecta patrones estacionales."""
        logger.info("Detecting seasonality patterns...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                EXTRACT(MONTH FROM m.created_at) AS month,
                EXTRACT(DAY FROM m.created_at) AS day_of_month,
                EXTRACT(DOW FROM m.created_at) AS day_of_week,
                SUM(m.quantity) AS sales
            FROM inventory_products p
            JOIN inventory_movements m ON p.id = m.product_id
            WHERE m.movement_type = 'sale'
            AND m.created_at >= NOW() - INTERVAL '12 months'
            AND p.active = TRUE
            GROUP BY p.id, p.sku, p.name, 
                     EXTRACT(MONTH FROM m.created_at),
                     EXTRACT(DAY FROM m.created_at),
                     EXTRACT(DOW FROM m.created_at)
        """
        
        seasonal_data = _query_dict(sql)
        
        # Agrupar por producto y mes
        product_seasonality = {}
        for data in seasonal_data:
            product_id = data["id"]
            if product_id not in product_seasonality:
                product_seasonality[product_id] = {
                    "sku": data["sku"],
                    "name": data["name"],
                    "monthly_sales": {},
                }
            month = int(data["month"])
            product_seasonality[product_id]["monthly_sales"][month] = \
                product_seasonality[product_id]["monthly_sales"].get(month, 0) + data["sales"]
        
        # Identificar productos con estacionalidad fuerte
        seasonal_products = []
        for product_id, data in product_seasonality.items():
            monthly_sales = data["monthly_sales"]
            if len(monthly_sales) >= 6:
                sales_values = list(monthly_sales.values())
                avg_sales = sum(sales_values) / len(sales_values)
                max_sales = max(sales_values)
                min_sales = min(sales_values)
                
                # Variabilidad > 50% indica estacionalidad
                if avg_sales > 0:
                    variability = ((max_sales - min_sales) / avg_sales) * 100
                    if variability > 50:
                        seasonal_products.append({
                            "product_id": product_id,
                            "sku": data["sku"],
                            "name": data["name"],
                            "variability": variability,
                            "peak_month": max(monthly_sales, key=monthly_sales.get),
                            "low_month": min(monthly_sales, key=monthly_sales.get),
                        })
        
        logger.info(f"Detected {len(seasonal_products)} products with seasonality")
        return {"seasonal_products": seasonal_products}

    @task(task_id="store_trend_data")
    def store_trend_data(
        trends_data: Dict[str, Any],
        seasonality_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Almacena datos de tendencias."""
        logger.info("Storing trend analysis data...")
        
        # Crear tabla de tendencias si no existe
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_trends (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        product_id UUID NOT NULL REFERENCES inventory_products(id) ON DELETE CASCADE,
                        trend_direction VARCHAR(32),
                        change_percent DECIMAL(5, 2),
                        recent_avg DECIMAL(10, 2),
                        previous_avg DECIMAL(10, 2),
                        is_seasonal BOOLEAN DEFAULT FALSE,
                        seasonality_variability DECIMAL(5, 2),
                        peak_month INTEGER,
                        analyzed_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(product_id, analyzed_at)
                    )
                """)
                
                # Insertar tendencias
                trends = trends_data.get("trends", [])
                seasonal_products = {p["product_id"]: p for p in seasonality_data.get("seasonal_products", [])}
                
                for trend in trends:
                    product_id = trend["product_id"]
                    seasonal = seasonal_products.get(product_id, {})
                    
                    cur.execute("""
                        INSERT INTO inventory_trends (
                            product_id, trend_direction, change_percent,
                            recent_avg, previous_avg, is_seasonal,
                            seasonality_variability, peak_month
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id, analyzed_at)
                        DO UPDATE SET
                            trend_direction = EXCLUDED.trend_direction,
                            change_percent = EXCLUDED.change_percent,
                            recent_avg = EXCLUDED.recent_avg,
                            previous_avg = EXCLUDED.previous_avg,
                            is_seasonal = EXCLUDED.is_seasonal,
                            seasonality_variability = EXCLUDED.seasonality_variability,
                            peak_month = EXCLUDED.peak_month
                    """, (
                        product_id,
                        trend["trend_direction"],
                        trend["change_percent"],
                        trend["recent_avg"],
                        trend["previous_avg"],
                        bool(seasonal),
                        seasonal.get("variability"),
                        seasonal.get("peak_month"),
                    ))
                
                conn.commit()
        
        logger.info(f"Stored trend data for {len(trends_data.get('trends', []))} products")
        return {"stored_count": len(trends_data.get("trends", []))}

    # Pipeline
    trends = analyze_sales_trends()
    seasonality = detect_seasonality()
    store_trend_data(trends, seasonality)

    return None


dag = inventory_trend_analysis()

