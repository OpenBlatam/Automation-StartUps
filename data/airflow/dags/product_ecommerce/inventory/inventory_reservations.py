"""
DAG de Gestión de Reservas de Inventario
Maneja reservas de stock para órdenes pendientes y expira reservas antiguas.
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
    dag_id="inventory_reservations",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="*/15 * * * *",  # Cada 15 minutos
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False,
    },
    description="Gestiona reservas de stock y expira reservas antiguas",
    tags=["inventory", "reservations", "orders"],
)
def inventory_reservations() -> None:
    """DAG de gestión de reservas."""

    @task(task_id="expire_old_reservations")
    def expire_old_reservations() -> Dict[str, Any]:
        """Expira reservas antiguas que no se han completado."""
        logger.info("Expiring old reservations...")
        
        # Buscar movimientos de reserva antiguos (>24 horas) sin completar
        sql = """
            SELECT 
                m.id AS movement_id,
                m.product_id,
                p.sku,
                m.quantity,
                m.reference_id,
                m.created_at
            FROM inventory_movements m
            JOIN inventory_products p ON m.product_id = p.id
            WHERE m.movement_type = 'reservation'
            AND m.created_at < NOW() - INTERVAL '24 hours'
            AND m.reference_id NOT IN (
                -- Excluir si hay una venta asociada
                SELECT DISTINCT reference_id
                FROM inventory_movements
                WHERE movement_type = 'sale'
                AND reference_id IS NOT NULL
            )
        """
        
        expired_reservations = _query_dict(sql)
        
        if not expired_reservations:
            logger.info("No expired reservations found")
            return {"expired_count": 0, "released_stock": 0}
        
        released_stock = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for reservation in expired_reservations:
                    product_id = reservation["product_id"]
                    quantity = reservation["quantity"]
                    
                    # Liberar stock reservado
                    update_sql = """
                        UPDATE inventory_stock
                        SET reserved_quantity = GREATEST(0, reserved_quantity - %s),
                            updated_at = NOW()
                        WHERE product_id = %s
                    """
                    cur.execute(update_sql, (quantity, product_id))
                    
                    # Crear movimiento de ajuste para registrar la liberación
                    adjust_sql = """
                        INSERT INTO inventory_movements (
                            product_id, movement_type, direction, quantity,
                            reference_type, reference_id, notes, created_by
                        ) VALUES (
                            %s, 'adjustment', 'in', %s,
                            'system', 'expired_reservation', 
                            'Reserva expirada automáticamente', 'inventory_reservations_dag'
                        )
                    """
                    cur.execute(adjust_sql, (product_id, quantity))
                    
                    released_stock += quantity
                    
                    logger.info(
                        f"Expired reservation {reservation['movement_id']} for {reservation['sku']}: "
                        f"released {quantity} units"
                    )
                
                conn.commit()
        
        logger.info(f"Expired {len(expired_reservations)} reservations, released {released_stock} units")
        return {
            "expired_count": len(expired_reservations),
            "released_stock": released_stock,
        }

    @task(task_id="check_oversold_products")
    def check_oversold_products() -> Dict[str, Any]:
        """Verifica productos con más reservas que stock disponible."""
        logger.info("Checking for oversold products...")
        
        sql = """
            SELECT 
                p.id,
                p.sku,
                p.name,
                s.quantity AS total_stock,
                s.reserved_quantity,
                s.available_quantity,
                (s.reserved_quantity - s.quantity) AS oversold_quantity
            FROM inventory_products p
            JOIN inventory_stock s ON p.id = s.product_id
            WHERE s.reserved_quantity > s.quantity
            AND p.active = TRUE
        """
        
        oversold = _query_dict(sql)
        
        if oversold:
            logger.warning(f"Found {len(oversold)} oversold products")
            for product in oversold:
                logger.warning(
                    f"Product {product['sku']} is oversold: "
                    f"{product['reserved_quantity']} reserved vs {product['total_stock']} available"
                )
        else:
            logger.info("No oversold products found")
        
        return {"oversold_products": oversold, "count": len(oversold)}

    @task(task_id="update_reserved_quantities")
    def update_reserved_quantities() -> Dict[str, Any]:
        """Actualiza cantidades reservadas basado en reservas activas."""
        logger.info("Updating reserved quantities from active reservations...")
        
        # Calcular reservas activas por producto
        sql = """
            SELECT 
                product_id,
                SUM(quantity) AS total_reserved
            FROM inventory_movements
            WHERE movement_type = 'reservation'
            AND created_at >= NOW() - INTERVAL '24 hours'
            AND reference_id NOT IN (
                SELECT DISTINCT reference_id
                FROM inventory_movements
                WHERE movement_type = 'sale'
                AND reference_id IS NOT NULL
            )
            GROUP BY product_id
        """
        
        active_reservations = _query_dict(sql)
        
        updated_count = 0
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                for reservation in active_reservations:
                    product_id = reservation["product_id"]
                    total_reserved = reservation["total_reserved"]
                    
                    # Actualizar cantidad reservada
                    update_sql = """
                        UPDATE inventory_stock
                        SET reserved_quantity = %s,
                            updated_at = NOW()
                        WHERE product_id = %s
                    """
                    cur.execute(update_sql, (total_reserved, product_id))
                    updated_count += 1
                
                conn.commit()
        
        logger.info(f"Updated reserved quantities for {updated_count} products")
        return {"updated_count": updated_count}

    # Pipeline
    expired = expire_old_reservations()
    oversold = check_oversold_products()
    updated = update_reserved_quantities()

    return None


dag = inventory_reservations()





