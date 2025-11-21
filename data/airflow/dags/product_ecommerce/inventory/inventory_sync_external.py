"""
DAG de Sincronización con Sistemas Externos
Sincroniza productos y stock con Stripe y QuickBooks.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

from data.airflow.plugins.db import get_conn

try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


def _get_env_var(name: str, default: str | None = None) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
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
    dag_id="inventory_sync_external",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "inventory",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    description="Sincroniza productos y stock con sistemas externos (Stripe, QuickBooks)",
    tags=["inventory", "sync", "stripe", "quickbooks"],
)
def inventory_sync_external() -> None:
    """DAG de sincronización con sistemas externos."""

    @task(task_id="sync_stripe_products")
    def sync_stripe_products() -> Dict[str, Any]:
        """Sincroniza productos desde Stripe."""
        logger.info("Syncing products from Stripe...")
        
        stripe_key = _get_env_var("STRIPE_API_KEY")
        if not stripe_key:
            logger.warning("STRIPE_API_KEY not configured, skipping Stripe sync")
            return {"synced": 0, "errors": []}
        
        try:
            import requests
            
            # Obtener productos de Stripe
            headers = {"Authorization": f"Bearer {stripe_key}"}
            response = requests.get(
                "https://api.stripe.com/v1/products",
                params={"limit": 100, "active": "true"},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            stripe_products = response.json().get("data", [])
            
            synced = 0
            errors = []
            
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for stripe_product in stripe_products:
                        stripe_id = stripe_product.get("id")
                        name = stripe_product.get("name", "")
                        description = stripe_product.get("description", "")
                        
                        # Buscar o crear producto en inventario
                        # Usar SKU como identificador (puede venir del metadata)
                        sku = stripe_product.get("metadata", {}).get("sku") or stripe_id
                        
                        upsert_sql = """
                            INSERT INTO inventory_products (
                                sku, name, description, stripe_product_id, active
                            ) VALUES (%s, %s, %s, %s, TRUE)
                            ON CONFLICT (sku)
                            DO UPDATE SET
                                name = EXCLUDED.name,
                                description = EXCLUDED.description,
                                stripe_product_id = EXCLUDED.stripe_product_id,
                                updated_at = NOW()
                            RETURNING id
                        """
                        
                        try:
                            cur.execute(upsert_sql, (sku, name, description, stripe_id))
                            product_id = cur.fetchone()[0]
                            synced += 1
                            logger.debug(f"Synced Stripe product {stripe_id} -> {sku}")
                        except Exception as e:
                            errors.append(f"Error syncing {stripe_id}: {str(e)}")
                            logger.warning(f"Error syncing Stripe product {stripe_id}: {e}")
                    
                    conn.commit()
            
            logger.info(f"Synced {synced} products from Stripe")
            return {"synced": synced, "errors": errors, "source": "stripe"}
            
        except Exception as e:
            logger.error(f"Failed to sync from Stripe: {e}", exc_info=True)
            return {"synced": 0, "errors": [str(e)], "source": "stripe"}

    @task(task_id="sync_quickbooks_items")
    def sync_quickbooks_items() -> Dict[str, Any]:
        """Sincroniza ítems desde QuickBooks."""
        logger.info("Syncing items from QuickBooks...")
        
        qb_access_token = _get_env_var("QUICKBOOKS_ACCESS_TOKEN")
        qb_realm_id = _get_env_var("QUICKBOOKS_REALM_ID")
        
        if not qb_access_token or not qb_realm_id:
            logger.warning("QuickBooks credentials not configured, skipping QuickBooks sync")
            return {"synced": 0, "errors": []}
        
        try:
            import requests
            
            # Obtener ítems de QuickBooks
            qb_base = _get_env_var("QUICKBOOKS_BASE", "https://sandbox-quickbooks.api.intuit.com")
            url = f"{qb_base}/v3/company/{qb_realm_id}/items"
            
            headers = {
                "Authorization": f"Bearer {qb_access_token}",
                "Accept": "application/json",
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            qb_items = response.json().get("QueryResponse", {}).get("Item", [])
            if not isinstance(qb_items, list):
                qb_items = [qb_items]
            
            synced = 0
            errors = []
            
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for qb_item in qb_items:
                        qb_id = qb_item.get("Id")
                        name = qb_item.get("Name", "")
                        sku = qb_item.get("Sku") or qb_id
                        unit_price = float(qb_item.get("UnitPrice", 0) or 0)
                        
                        # Buscar o crear producto
                        upsert_sql = """
                            INSERT INTO inventory_products (
                                sku, name, unit_price, quickbooks_item_id, active
                            ) VALUES (%s, %s, %s, %s, TRUE)
                            ON CONFLICT (sku)
                            DO UPDATE SET
                                name = EXCLUDED.name,
                                unit_price = EXCLUDED.unit_price,
                                quickbooks_item_id = EXCLUDED.quickbooks_item_id,
                                updated_at = NOW()
                            RETURNING id
                        """
                        
                        try:
                            cur.execute(upsert_sql, (sku, name, unit_price, qb_id))
                            product_id = cur.fetchone()[0]
                            synced += 1
                            logger.debug(f"Synced QuickBooks item {qb_id} -> {sku}")
                        except Exception as e:
                            errors.append(f"Error syncing {qb_id}: {str(e)}")
                            logger.warning(f"Error syncing QuickBooks item {qb_id}: {e}")
                    
                    conn.commit()
            
            logger.info(f"Synced {synced} items from QuickBooks")
            return {"synced": synced, "errors": errors, "source": "quickbooks"}
            
        except Exception as e:
            logger.error(f"Failed to sync from QuickBooks: {e}", exc_info=True)
            return {"synced": 0, "errors": [str(e)], "source": "quickbooks"}

    @task(task_id="log_sync_results")
    def log_sync_results(
        stripe_result: Dict[str, Any],
        qb_result: Dict[str, Any],
    ) -> None:
        """Registra resultados de sincronización."""
        total_synced = stripe_result.get("synced", 0) + qb_result.get("synced", 0)
        total_errors = len(stripe_result.get("errors", [])) + len(qb_result.get("errors", []))
        
        logger.info(
            "External sync completed",
            extra={
                "stripe_synced": stripe_result.get("synced", 0),
                "quickbooks_synced": qb_result.get("synced", 0),
                "total_synced": total_synced,
                "total_errors": total_errors,
            },
        )
        
        if total_errors > 0 and NOTIFICATIONS_AVAILABLE:
            try:
                notify_slack(
                    f"⚠️ *Sincronización Externa de Inventario*\n\n"
                    f"✅ Sincronizados: {total_synced}\n"
                    f"❌ Errores: {total_errors}\n\n"
                    f"Stripe: {stripe_result.get('synced', 0)}\n"
                    f"QuickBooks: {qb_result.get('synced', 0)}"
                )
            except Exception:
                pass

    # Pipeline
    stripe_result = sync_stripe_products()
    qb_result = sync_quickbooks_items()
    log_sync_results(stripe_result, qb_result)

    return None


dag = inventory_sync_external()





