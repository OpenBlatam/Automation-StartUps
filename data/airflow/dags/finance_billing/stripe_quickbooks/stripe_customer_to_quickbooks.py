"""
DAG para sincronizar clientes de Stripe con QuickBooks.
Cuando se crea un nuevo cliente en Stripe, este DAG verifica en QuickBooks si existe por correo.
Si no existe, crea uno; si existe, actualiza los datos de dirección/país.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
import logging
import os
import time
from datetime import timedelta

from data.airflow.dags.stripe_quickbooks_sync import sincronizar_cliente_stripe_quickbooks

logger = logging.getLogger(__name__)

# Importar Stats para métricas
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    logger.debug("Stats not available for metrics")

# Importar utilidades de notificaciones del stack
try:
    from data.airflow.plugins.etl_notifications import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    try:
        from plugins.etl_notifications import notify_slack
        NOTIFICATIONS_AVAILABLE = True
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False
        logger.warning("Notifications plugin not available")


@dag(
    dag_id="stripe_customer_to_quickbooks",
    start_date=None,  # Manual trigger only
    schedule=None,
    catchup=False,
    default_args={
        "owner": "finance",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "depends_on_past": False,
    },
    doc_md="""
    ### Sincronización de Clientes Stripe → QuickBooks
    
    DAG que sincroniza clientes de Stripe con QuickBooks.
    
    **Funcionalidad:**
    1. Recibe un evento de nuevo cliente en Stripe (nombre, correo, país)
    2. Verifica en QuickBooks si existe un cliente con ese correo
    3. Si no existe, crea uno nuevo en QuickBooks
    4. Si existe, actualiza los datos de dirección/país con los nuevos datos
    5. Retorna 'creado' o 'actualizado' + ID cliente QuickBooks
    
    **Parámetros (via API trigger):**
    - `nombre_cliente`: Nombre completo del cliente (requerido)
    - `correo_cliente`: Correo electrónico del cliente (requerido)
    - `pais`: País del cliente (requerido)
    
    **Configuración requerida (variables de entorno):**
    - `QUICKBOOKS_REALM_ID` o `QUICKBOOKS_COMPANY_ID`: ID de la compañía en QuickBooks
    - `QUICKBOOKS_ACCESS_TOKEN`: Token de acceso directo (opcional, si no se usa OAuth2)
    - O bien, para OAuth2:
      - `QUICKBOOKS_CLIENT_ID`
      - `QUICKBOOKS_CLIENT_SECRET`
      - `QUICKBOOKS_REFRESH_TOKEN`
    
    **Ejemplo de uso via API:**
    ```bash
    curl -X POST http://airflow/api/v1/dags/stripe_customer_to_quickbooks/dagRuns \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "conf": {
          "nombre_cliente": "Juan Pérez",
          "correo_cliente": "juan@example.com",
          "pais": "MX"
        }
      }'
    ```
    
    **Respuesta esperada:**
    - `creado {qb_customer_id}`: Cliente creado exitosamente
    - `actualizado {qb_customer_id}`: Cliente actualizado exitosamente
    - `ERROR_*`: Descripción del error
    """,
    params={
        "nombre_cliente": Param("", type="string", minLength=1),
        "correo_cliente": Param("", type="string", minLength=1),
        "pais": Param("", type="string", minLength=1),
    },
    tags=["stripe", "quickbooks", "customer", "sync", "finance", "webhook"],
)
def stripe_customer_to_quickbooks() -> None:
    """
    DAG para sincronizar clientes de Stripe con QuickBooks.
    """
    
    @task(
        task_id="sincronizar_cliente",
        execution_timeout=timedelta(minutes=5),  # Timeout de 5 minutos
        retries=2,
        retry_delay=timedelta(minutes=1),
        retry_exponential_backoff=True,
    )
    def sincronizar_cliente() -> Dict[str, Any]:
        """
        Sincroniza un cliente de Stripe con QuickBooks.
        """
        ctx = get_current_context()
        params = ctx["params"]
        
        nombre_cliente = str(params.get("nombre_cliente", "")).strip()
        correo_cliente = str(params.get("correo_cliente", "")).strip()
        pais = str(params.get("pais", "")).strip()
        
        # Validar parámetros requeridos
        if not nombre_cliente:
            raise AirflowFailException("nombre_cliente es requerido")
        if not correo_cliente:
            raise AirflowFailException("correo_cliente es requerido")
        if not pais:
            raise AirflowFailException("pais es requerido")
        
        logger.info(
            "Iniciando sincronización de cliente Stripe → QuickBooks",
            extra={
                "nombre_cliente": nombre_cliente,
                "correo_cliente": correo_cliente,
                "pais": pais,
            },
        )
        
        # Tracking de métricas y performance
        start_time = time.time()
        
        # Registrar inicio en métricas
        if STATS_AVAILABLE:
            try:
                Stats.incr("stripe_quickbooks_sync.attempt", 1, tags={"action": "sync"})
            except Exception:
                pass
        
        try:
            # Llamar a la función de sincronización
            resultado = sincronizar_cliente_stripe_quickbooks(
                nombre_cliente=nombre_cliente,
                correo_cliente=correo_cliente,
                pais=pais
            )
        except Exception as e:
            # Registrar error en métricas
            if STATS_AVAILABLE:
                try:
                    Stats.incr("stripe_quickbooks_sync.error", 1, tags={"error_type": type(e).__name__})
                except Exception:
                    pass
            raise
        
        # Calcular duración
        duration_ms = (time.time() - start_time) * 1000
        
        # Parsear resultado
        if resultado.startswith("creado "):
            qb_customer_id = resultado.replace("creado ", "").strip()
            
            # Registrar éxito en métricas
            if STATS_AVAILABLE:
                try:
                    Stats.incr("stripe_quickbooks_sync.success", 1, tags={"action": "create"})
                    Stats.incr("stripe_quickbooks_sync.duration_ms", int(duration_ms), tags={"action": "create"})
                except Exception:
                    pass
            
            logger.info(
                "Cliente creado exitosamente en QuickBooks",
                extra={
                    "correo_cliente": correo_cliente,
                    "qb_customer_id": qb_customer_id,
                    "nombre_cliente": nombre_cliente,
                    "pais": pais,
                    "duration_ms": duration_ms,
                },
            )
            
            # Notificación a Slack si está disponible
            if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                try:
                    notify_slack(
                        f"✅ *Cliente creado en QuickBooks*\n"
                        f"• Nombre: {nombre_cliente}\n"
                        f"• Email: {correo_cliente}\n"
                        f"• País: {pais}\n"
                        f"• ID QuickBooks: {qb_customer_id}",
                        extra_context={
                            "dag_id": "stripe_customer_to_quickbooks",
                            "status": "creado",
                            "qb_customer_id": qb_customer_id,
                            "correo_cliente": correo_cliente,
                        },
                        username="Stripe-QuickBooks Sync",
                        icon_emoji=":money_with_wings:"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack notification: {e}")
            
            return {
                "status": "creado",
                "qb_customer_id": qb_customer_id,
                "mensaje": resultado,
                "correo_cliente": correo_cliente,
                "nombre_cliente": nombre_cliente,
                "duration_ms": duration_ms,
            }
        elif resultado.startswith("actualizado "):
            qb_customer_id = resultado.replace("actualizado ", "").strip()
            
            # Registrar éxito en métricas
            if STATS_AVAILABLE:
                try:
                    Stats.incr("stripe_quickbooks_sync.success", 1, tags={"action": "update"})
                    Stats.incr("stripe_quickbooks_sync.duration_ms", int(duration_ms), tags={"action": "update"})
                except Exception:
                    pass
            
            logger.info(
                "Cliente actualizado exitosamente en QuickBooks",
                extra={
                    "correo_cliente": correo_cliente,
                    "qb_customer_id": qb_customer_id,
                    "nombre_cliente": nombre_cliente,
                    "pais": pais,
                    "duration_ms": duration_ms,
                },
            )
            
            # Notificación a Slack si está disponible
            if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                try:
                    notify_slack(
                        f"🔄 *Cliente actualizado en QuickBooks*\n"
                        f"• Nombre: {nombre_cliente}\n"
                        f"• Email: {correo_cliente}\n"
                        f"• País: {pais}\n"
                        f"• ID QuickBooks: {qb_customer_id}",
                        extra_context={
                            "dag_id": "stripe_customer_to_quickbooks",
                            "status": "actualizado",
                            "qb_customer_id": qb_customer_id,
                            "correo_cliente": correo_cliente,
                        },
                        username="Stripe-QuickBooks Sync",
                        icon_emoji=":money_with_wings:"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack notification: {e}")
            
            return {
                "status": "actualizado",
                "qb_customer_id": qb_customer_id,
                "mensaje": resultado,
                "correo_cliente": correo_cliente,
                "nombre_cliente": nombre_cliente,
                "duration_ms": duration_ms,
            }
        else:
            # Error
            # Registrar error en métricas
            if STATS_AVAILABLE:
                try:
                    Stats.incr("stripe_quickbooks_sync.error", 1, tags={"action": "sync"})
                    Stats.incr("stripe_quickbooks_sync.duration_ms", int(duration_ms), tags={"action": "error"})
                except Exception:
                    pass
            
            logger.error(
                "Error al sincronizar cliente con QuickBooks",
                extra={
                    "correo_cliente": correo_cliente,
                    "nombre_cliente": nombre_cliente,
                    "pais": pais,
                    "error": resultado,
                    "duration_ms": duration_ms,
                },
            )
            
            # Notificación de error a Slack
            if NOTIFICATIONS_AVAILABLE and os.getenv("ENABLE_SLACK", "false").lower() == "true":
                try:
                    notify_slack(
                        f"❌ *Error al sincronizar cliente*\n"
                        f"• Nombre: {nombre_cliente}\n"
                        f"• Email: {correo_cliente}\n"
                        f"• Error: {resultado[:200]}",
                        extra_context={
                            "dag_id": "stripe_customer_to_quickbooks",
                            "status": "error",
                            "correo_cliente": correo_cliente,
                            "error": resultado,
                        },
                        username="Stripe-QuickBooks Sync",
                        icon_emoji=":warning:"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack error notification: {e}")
            
            raise AirflowFailException(f"Error al sincronizar cliente: {resultado}")
    
    # Ejecutar tarea
    sincronizar_cliente()


# Generar DAG
dag_instance = stripe_customer_to_quickbooks()

