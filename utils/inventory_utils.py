"""
Utilidades para gestión de inventario
Funciones helper para operaciones comunes de inventario
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


def reserve_stock(
    product_id: str,
    quantity: int,
    reference_id: str,
    reference_type: str = "order",
    connection=None,
) -> bool:
    """
    Reserva stock para una orden pendiente.
    
    Args:
        product_id: UUID del producto
        quantity: Cantidad a reservar
        reference_id: ID de la orden/referencia
        reference_type: Tipo de referencia (order, quote, etc.)
        connection: Conexión de base de datos (opcional)
    
    Returns:
        True si la reserva fue exitosa, False si no hay stock suficiente
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            # Verificar stock disponible
            cur.execute(
                """
                SELECT available_quantity FROM inventory_stock
                WHERE product_id = %s
                """,
                (product_id,),
            )
            result = cur.fetchone()
            
            if not result:
                logger.warning(f"Product {product_id} has no stock record")
                return False
            
            available = result[0]
            if available < quantity:
                logger.warning(
                    f"Insufficient stock for product {product_id}: "
                    f"requested {quantity}, available {available}"
                )
                return False
            
            # Crear movimiento de reserva
            cur.execute(
                """
                INSERT INTO inventory_movements (
                    product_id, movement_type, direction, quantity,
                    reference_type, reference_id, notes, created_by
                ) VALUES (%s, 'reservation', 'out', %s, %s, %s, 'Reserva automática', 'system')
                """,
                (product_id, quantity, reference_type, reference_id),
            )
            
            # Actualizar stock reservado
            cur.execute(
                """
                UPDATE inventory_stock
                SET reserved_quantity = reserved_quantity + %s,
                    updated_at = NOW()
                WHERE product_id = %s
                """,
                (quantity, product_id),
            )
            
            conn.commit()
            logger.info(f"Reserved {quantity} units of product {product_id} for {reference_type} {reference_id}")
            return True


def release_reservation(
    product_id: str,
    reference_id: str,
    connection=None,
) -> bool:
    """
    Libera una reserva de stock.
    
    Args:
        product_id: UUID del producto
        reference_id: ID de la referencia a liberar
        connection: Conexión de base de datos (opcional)
    
    Returns:
        True si la liberación fue exitosa
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            # Encontrar reserva
            cur.execute(
                """
                SELECT id, quantity FROM inventory_movements
                WHERE product_id = %s
                AND movement_type = 'reservation'
                AND reference_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (product_id, reference_id),
            )
            result = cur.fetchone()
            
            if not result:
                logger.warning(f"No reservation found for product {product_id}, reference {reference_id}")
                return False
            
            movement_id, quantity = result
            
            # Liberar stock reservado
            cur.execute(
                """
                UPDATE inventory_stock
                SET reserved_quantity = GREATEST(0, reserved_quantity - %s),
                    updated_at = NOW()
                WHERE product_id = %s
                """,
                (quantity, product_id),
            )
            
            # Marcar movimiento como cancelado (o eliminarlo)
            cur.execute(
                """
                UPDATE inventory_movements
                SET notes = notes || ' - Liberada automáticamente'
                WHERE id = %s
                """,
                (movement_id,),
            )
            
            conn.commit()
            logger.info(f"Released reservation for product {product_id}, reference {reference_id}")
            return True


def record_sale(
    product_id: str,
    quantity: int,
    reference_id: str,
    reference_type: str = "order",
    unit_price: Optional[Decimal] = None,
    connection=None,
) -> bool:
    """
    Registra una venta de producto.
    
    Args:
        product_id: UUID del producto
        quantity: Cantidad vendida
        reference_id: ID de la orden/venta
        reference_type: Tipo de referencia
        unit_price: Precio unitario (opcional)
        connection: Conexión de base de datos (opcional)
    
    Returns:
        True si la venta fue registrada exitosamente
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            # Liberar reserva si existe
            cur.execute(
                """
                SELECT quantity FROM inventory_movements
                WHERE product_id = %s
                AND movement_type = 'reservation'
                AND reference_id = %s
                AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (product_id, reference_id),
            )
            reservation = cur.fetchone()
            
            if reservation:
                # Liberar reserva
                cur.execute(
                    """
                    UPDATE inventory_stock
                    SET reserved_quantity = GREATEST(0, reserved_quantity - %s),
                        updated_at = NOW()
                    WHERE product_id = %s
                    """,
                    (reservation[0], product_id),
                )
            
            # Crear movimiento de venta
            notes = f"Venta {reference_type} {reference_id}"
            if unit_price:
                notes += f" - Precio unitario: {unit_price}"
            
            cur.execute(
                """
                INSERT INTO inventory_movements (
                    product_id, movement_type, direction, quantity,
                    reference_type, reference_id, notes, created_by
                ) VALUES (%s, 'sale', 'out', %s, %s, %s, %s, 'system')
                """,
                (product_id, quantity, reference_type, reference_id, notes),
            )
            
            conn.commit()
            logger.info(f"Recorded sale of {quantity} units of product {product_id} for {reference_type} {reference_id}")
            return True


def record_purchase(
    product_id: str,
    quantity: int,
    reference_id: str,
    unit_cost: Optional[Decimal] = None,
    supplier_id: Optional[str] = None,
    connection=None,
) -> bool:
    """
    Registra una compra/reposición de producto.
    
    Args:
        product_id: UUID del producto
        quantity: Cantidad comprada
        reference_id: ID de la orden de compra/reorden
        unit_cost: Costo unitario (opcional)
        supplier_id: ID del proveedor (opcional)
        connection: Conexión de base de datos (opcional)
    
    Returns:
        True si la compra fue registrada exitosamente
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            notes = f"Compra {reference_id}"
            if unit_cost:
                notes += f" - Costo unitario: {unit_cost}"
            if supplier_id:
                notes += f" - Proveedor: {supplier_id}"
            
            # Crear movimiento de compra
            cur.execute(
                """
                INSERT INTO inventory_movements (
                    product_id, movement_type, direction, quantity,
                    reference_type, reference_id, notes, created_by
                ) VALUES (%s, 'purchase', 'in', %s, 'purchase_order', %s, %s, 'system')
                """,
                (product_id, quantity, reference_id, notes),
            )
            
            # Actualizar reorden si existe
            cur.execute(
                """
                UPDATE inventory_reorders
                SET status = 'received',
                    received_at = NOW(),
                    updated_at = NOW()
                WHERE product_id = %s
                AND reference_id = %s
                AND status IN ('sent', 'confirmed')
                """,
                (product_id, reference_id),
            )
            
            conn.commit()
            logger.info(f"Recorded purchase of {quantity} units of product {product_id} for {reference_id}")
            return True


def get_product_stock_status(product_id: str, connection=None) -> Dict[str, Any]:
    """
    Obtiene el estado completo de stock de un producto.
    
    Args:
        product_id: UUID del producto
        connection: Conexión de base de datos (opcional)
    
    Returns:
        Diccionario con información de stock
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    p.id,
                    p.sku,
                    p.name,
                    p.reorder_point,
                    p.reorder_quantity,
                    COALESCE(s.quantity, 0) AS total_stock,
                    COALESCE(s.reserved_quantity, 0) AS reserved,
                    COALESCE(s.available_quantity, 0) AS available,
                    CASE 
                        WHEN COALESCE(s.available_quantity, 0) = 0 THEN 'out_of_stock'
                        WHEN COALESCE(s.available_quantity, 0) <= p.reorder_point THEN 'low_stock'
                        ELSE 'normal'
                    END AS status
                FROM inventory_products p
                LEFT JOIN inventory_stock s ON p.id = s.product_id
                WHERE p.id = %s
                """,
                (product_id,),
            )
            
            result = cur.fetchone()
            if not result:
                return {}
            
            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, result))


def calculate_sales_velocity(
    product_id: str,
    days: int = 30,
    connection=None,
) -> float:
    """
    Calcula la velocidad de venta (unidades por día) de un producto.
    
    Args:
        product_id: UUID del producto
        days: Período en días para calcular
        connection: Conexión de base de datos (opcional)
    
    Returns:
        Unidades vendidas por día
    """
    if connection is None:
        from data.airflow.plugins.db import get_conn
        conn_context = get_conn()
    else:
        from contextlib import nullcontext
        conn_context = nullcontext(connection)
    
    with conn_context as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    COALESCE(SUM(quantity)::DECIMAL / NULLIF(GREATEST(1, EXTRACT(EPOCH FROM (NOW() - MIN(created_at))) / 86400.0), 1), 0)
                FROM inventory_movements
                WHERE product_id = %s
                AND movement_type = 'sale'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                (product_id, days),
            )
            
            result = cur.fetchone()
            return float(result[0]) if result and result[0] else 0.0

