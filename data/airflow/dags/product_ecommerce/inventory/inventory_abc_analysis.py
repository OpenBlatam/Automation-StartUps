"""
DAG de Análisis ABC/XYZ
Clasifica productos según valor (ABC) y variabilidad de demanda (XYZ)
para estrategias de gestión diferenciadas.
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
    dag_id="inventory_abc_analysis",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 3 * * 0",  # Semanal los domingos a las 3:00 AM
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Análisis ABC/XYZ de productos para gestión diferenciada",
    tags=["inventory", "analysis", "abc"],
)
def inventory_abc_analysis() -> None:
    """DAG de análisis ABC/XYZ."""

    @task(task_id="calculate_abc_classification")
    def calculate_abc_classification() -> Dict[str, Any]:
        """Calcula clasificación ABC basada en valor de inventario."""
        logger.info("Calculating ABC classification...")
        
        # Calcular valor total por producto (stock * costo unitario)
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                COALESCE(s.available_quantity, 0) * COALESCE(p.unit_cost, 0) AS total_value,
                COALESCE(s.available_quantity, 0) AS stock_quantity,
                COALESCE(p.unit_cost, 0) AS unit_cost
            FROM inventory_products p
            LEFT JOIN inventory_stock s ON p.id = s.product_id
            WHERE p.active = TRUE
            AND COALESCE(s.available_quantity, 0) > 0
            ORDER BY total_value DESC
        """
        
        products = _query_dict(sql)
        
        if not products:
            return {"products": [], "classifications": {}}
        
        # Calcular valor total
        total_value = sum(p["total_value"] for p in products)
        
        # Clasificar ABC
        cumulative_value = 0
        classifications = {}
        
        for product in products:
            cumulative_value += product["total_value"]
            cumulative_percent = (cumulative_value / total_value * 100) if total_value > 0 else 0
            
            if cumulative_percent <= 80:
                abc_class = "A"  # Top 80% del valor
            elif cumulative_percent <= 95:
                abc_class = "B"  # Siguiente 15% del valor
            else:
                abc_class = "C"  # Último 5% del valor
            
            classifications[product["id"]] = {
                "abc_class": abc_class,
                "cumulative_percent": cumulative_percent,
                "total_value": product["total_value"],
            }
        
        logger.info(f"Classified {len(products)} products: A={sum(1 for c in classifications.values() if c['abc_class']=='A')}, "
                   f"B={sum(1 for c in classifications.values() if c['abc_class']=='B')}, "
                   f"C={sum(1 for c in classifications.values() if c['abc_class']=='C')}")
        
        return {"products": products, "classifications": classifications}

    @task(task_id="calculate_xyz_classification")
    def calculate_xyz_classification() -> Dict[str, Any]:
        """Calcula clasificación XYZ basada en variabilidad de demanda."""
        logger.info("Calculating XYZ classification...")
        
        # Calcular variabilidad de ventas (últimos 90 días)
        sql = """
            SELECT 
                p.id,
                p.sku,
                COUNT(m.id) AS sale_count,
                SUM(m.quantity) AS total_sold,
                AVG(m.quantity) AS avg_quantity,
                STDDEV(m.quantity) AS stddev_quantity,
                CASE 
                    WHEN COUNT(m.id) > 0 THEN STDDEV(m.quantity) / NULLIF(AVG(m.quantity), 0)
                    ELSE 0
                END AS coefficient_variation
            FROM inventory_products p
            LEFT JOIN inventory_movements m ON p.id = m.product_id
            AND m.movement_type = 'sale'
            AND m.created_at >= NOW() - INTERVAL '90 days'
            WHERE p.active = TRUE
            GROUP BY p.id, p.sku
            HAVING COUNT(m.id) > 0
        """
        
        products = _query_dict(sql)
        
        if not products:
            return {"products": [], "classifications": {}}
        
        # Calcular percentiles de coeficiente de variación
        cv_values = [p["coefficient_variation"] for p in products if p["coefficient_variation"] is not None]
        cv_values.sort()
        
        if not cv_values:
            return {"products": [], "classifications": {}}
        
        p33 = cv_values[int(len(cv_values) * 0.33)] if len(cv_values) > 0 else 0
        p66 = cv_values[int(len(cv_values) * 0.66)] if len(cv_values) > 0 else 0
        
        # Clasificar XYZ
        classifications = {}
        for product in products:
            cv = product["coefficient_variation"] or 0
            
            if cv <= p33:
                xyz_class = "X"  # Baja variabilidad (predecible)
            elif cv <= p66:
                xyz_class = "Y"  # Variabilidad media
            else:
                xyz_class = "Z"  # Alta variabilidad (impredecible)
            
            classifications[product["id"]] = {
                "xyz_class": xyz_class,
                "coefficient_variation": cv,
                "sale_count": product["sale_count"],
            }
        
        logger.info(f"Classified {len(products)} products: X={sum(1 for c in classifications.values() if c['xyz_class']=='X')}, "
                   f"Y={sum(1 for c in classifications.values() if c['xyz_class']=='Y')}, "
                   f"Z={sum(1 for c in classifications.values() if c['xyz_class']=='Z')}")
        
        return {"products": products, "classifications": classifications}

    @task(task_id="store_classifications")
    def store_classifications(
        abc_data: Dict[str, Any],
        xyz_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Almacena clasificaciones en la base de datos."""
        abc_classifications = abc_data.get("classifications", {})
        xyz_classifications = xyz_data.get("classifications", {})
        
        # Agregar columna de clasificación si no existe (en producción usar migración)
        # Por ahora, almacenamos en una tabla separada o en metadata JSONB
        
        stored_count = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de clasificaciones si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_classifications (
                        product_id UUID PRIMARY KEY REFERENCES inventory_products(id) ON DELETE CASCADE,
                        abc_class VARCHAR(1),
                        xyz_class VARCHAR(1),
                        abc_value DECIMAL(12, 2),
                        abc_cumulative_percent DECIMAL(5, 2),
                        xyz_coefficient_variation DECIMAL(10, 4),
                        updated_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Insertar/actualizar clasificaciones
                all_product_ids = set(abc_classifications.keys()) | set(xyz_classifications.keys())
                
                for product_id in all_product_ids:
                    abc = abc_classifications.get(product_id, {})
                    xyz = xyz_classifications.get(product_id, {})
                    
                    upsert_sql = """
                        INSERT INTO inventory_classifications (
                            product_id, abc_class, xyz_class,
                            abc_value, abc_cumulative_percent, xyz_coefficient_variation
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (product_id)
                        DO UPDATE SET
                            abc_class = EXCLUDED.abc_class,
                            xyz_class = EXCLUDED.xyz_class,
                            abc_value = EXCLUDED.abc_value,
                            abc_cumulative_percent = EXCLUDED.abc_cumulative_percent,
                            xyz_coefficient_variation = EXCLUDED.xyz_coefficient_variation,
                            updated_at = NOW()
                    """
                    
                    cur.execute(
                        upsert_sql,
                        (
                            product_id,
                            abc.get("abc_class"),
                            xyz.get("xyz_class"),
                            abc.get("total_value"),
                            abc.get("cumulative_percent"),
                            xyz.get("coefficient_variation"),
                        ),
                    )
                    stored_count += 1
                
                conn.commit()
        
        logger.info(f"Stored classifications for {stored_count} products")
        
        # Generar resumen por combinación ABC/XYZ
        summary = {}
        for product_id in all_product_ids:
            abc_class = abc_classifications.get(product_id, {}).get("abc_class", "?")
            xyz_class = xyz_classifications.get(product_id, {}).get("xyz_class", "?")
            combo = f"{abc_class}{xyz_class}"
            summary[combo] = summary.get(combo, 0) + 1
        
        return {
            "stored_count": stored_count,
            "summary": summary,
        }

    # Pipeline
    abc_data = calculate_abc_classification()
    xyz_data = calculate_xyz_classification()
    store_classifications(abc_data, xyz_data)

    return None


dag = inventory_abc_analysis()





