"""
DAG Webhook Handler para Actualizaciones de Inventario
Recibe actualizaciones de stock desde sistemas externos vía webhook.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import json
from typing import Any, Dict, List, Optional

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

from data.airflow.plugins.db import get_conn

logger = logging.getLogger(__name__)


@dag(
    dag_id="inventory_webhook_handler",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Triggered manually or via API
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False,
    },
    description="Webhook handler para actualizaciones de inventario desde sistemas externos",
    tags=["inventory", "webhook", "api"],
)
def inventory_webhook_handler() -> None:
    """DAG handler para webhooks de inventario."""

    @task(task_id="process_webhook_payload")
    def process_webhook_payload(**context) -> Dict[str, Any]:
        """Procesa payload del webhook."""
        # Obtener datos del contexto (pueden venir de conf o de un trigger externo)
        conf = context.get("dag_run", {}).conf or {}
        
        # Formato esperado:
        # {
        #   "event_type": "stock_update" | "purchase_received" | "sale_processed",
        #   "product_sku": "SKU-001",
        #   "quantity": 100,
        #   "reference_id": "REF-123",
        #   "reference_type": "order",
        #   "metadata": {...}
        # }
        
        event_type = conf.get("event_type")
        product_sku = conf.get("product_sku")
        quantity = conf.get("quantity", 0)
        
        if not event_type or not product_sku:
            raise ValueError("Missing required fields: event_type, product_sku")
        
        logger.info(f"Processing webhook: {event_type} for product {product_sku}")
        
        return {
            "event_type": event_type,
            "product_sku": product_sku,
            "quantity": quantity,
            "reference_id": conf.get("reference_id"),
            "reference_type": conf.get("reference_type", "webhook"),
            "metadata": conf.get("metadata", {}),
        }

    @task(task_id="update_stock_from_webhook")
    def update_stock_from_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza stock basado en el webhook."""
        event_type = payload["event_type"]
        product_sku = payload["product_sku"]
        quantity = payload["quantity"]
        reference_id = payload.get("reference_id")
        reference_type = payload.get("reference_type", "webhook")
        
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar producto por SKU
                cur.execute("SELECT id FROM inventory_products WHERE sku = %s", (product_sku,))
                result = cur.fetchone()
                
                if not result:
                    raise ValueError(f"Product with SKU {product_sku} not found")
                
                product_id = result[0]
                
                # Determinar tipo de movimiento según event_type
                if event_type == "stock_update":
                    # Actualización directa de stock
                    movement_type = "adjustment"
                    direction = "in" if quantity > 0 else "out"
                    quantity_abs = abs(quantity)
                    
                elif event_type == "purchase_received":
                    movement_type = "purchase"
                    direction = "in"
                    quantity_abs = quantity
                    
                elif event_type == "sale_processed":
                    movement_type = "sale"
                    direction = "out"
                    quantity_abs = quantity
                    
                else:
                    raise ValueError(f"Unknown event_type: {event_type}")
                
                # Crear movimiento
                cur.execute(
                    """
                    INSERT INTO inventory_movements (
                        product_id, movement_type, direction, quantity,
                        reference_type, reference_id, notes, created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'webhook')
                    RETURNING id
                    """,
                    (
                        product_id,
                        movement_type,
                        direction,
                        quantity_abs,
                        reference_type,
                        reference_id or f"WEBHOOK-{event_type}",
                        f"Actualizado desde webhook: {event_type}",
                    ),
                )
                
                movement_id = cur.fetchone()[0]
                conn.commit()
                
                logger.info(
                    f"Updated stock for {product_sku}: {movement_type} {direction} {quantity_abs} "
                    f"(movement_id: {movement_id})"
                )
                
                return {
                    "success": True,
                    "movement_id": str(movement_id),
                    "product_id": str(product_id),
                    "event_type": event_type,
                }

    # Pipeline
    payload = process_webhook_payload()
    result = update_stock_from_webhook(payload)

    return None


dag = inventory_webhook_handler()

