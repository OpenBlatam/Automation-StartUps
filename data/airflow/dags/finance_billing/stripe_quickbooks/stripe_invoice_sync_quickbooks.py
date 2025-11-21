"""
DAG de Airflow para sincronizar facturas de Stripe a QuickBooks.
Cuando se emite una factura en Stripe, crea automáticamente la factura correspondiente en QuickBooks
y la marca como pagada si se detecta un pago inmediato.
"""
from datetime import timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

from stripe_invoice_to_quickbooks import crear_factura_quickbooks


@dag(
    dag_id="stripe_invoice_sync_quickbooks",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger cuando se emite una factura en Stripe
    catchup=False,
    default_args={
        "owner": "finance",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Sincronización de Facturas Stripe → QuickBooks
    
    DAG para crear facturas en QuickBooks cuando se emite una factura en Stripe.
    
    **Funcionalidades:**
    - ✅ Crea factura en QuickBooks con mismo monto y fecha de vencimiento
    - ✅ Detecta pagos inmediatos en Stripe y marca factura como pagada automáticamente
    - ✅ Busca cliente en QuickBooks por correo electrónico
    - ✅ Manejo robusto de errores y retries
    
    **Parámetros requeridos:**
    - `stripe_invoice_id`: ID de la factura en Stripe (ej: "in_1234567890")
    - `correo_cliente`: Correo electrónico del cliente
    - `monto_factura`: Monto total de la factura (número)
    - `fecha_vencimiento`: Fecha de vencimiento en formato YYYY-MM-DD o ISO (ej: "2025-02-15")
    
    **Parámetros opcionales:**
    - `cuenta_ingresos`: Nombre de la cuenta de ingresos en QuickBooks (default: "Services")
    - `qb_access_token`: Token de acceso de QuickBooks (usa env var QUICKBOOKS_ACCESS_TOKEN si está vacío)
    - `qb_realm_id`: ID de la compañía en QuickBooks (usa env var QUICKBOOKS_REALM_ID si está vacío)
    - `stripe_api_key`: API key de Stripe para verificar estado de pago (usa env var STRIPE_API_KEY si está vacío)
    
    **Ejemplo de uso:**
    ```json
    {
        "stripe_invoice_id": "in_1234567890",
        "correo_cliente": "cliente@example.com",
        "monto_factura": 1000.00,
        "fecha_vencimiento": "2025-02-15",
        "cuenta_ingresos": "Services"
    }
    ```
    
    **Retorno:**
    - Dict con:
        - `qb_invoice_id`: ID de la factura creada en QuickBooks (None si falla)
        - `estado`: Estado de la operación ('Éxito' o descripción del error)
        - `pagada`: bool indicando si la factura fue marcada como pagada
    
    **Requisitos:**
    - Variable de entorno QUICKBOOKS_ACCESS_TOKEN configurada
    - Variable de entorno QUICKBOOKS_REALM_ID configurada
    - Variable de entorno STRIPE_API_KEY configurada (opcional, solo si se quiere verificar pagos)
    - El cliente debe existir en QuickBooks (usar stripe_quickbooks_sync.py para sincronizar clientes primero)
    
    **Notas:**
    - Si la factura de Stripe tiene un pago inmediato detectado, se crea automáticamente un Payment en QuickBooks
    - Si el cliente no existe en QuickBooks, el DAG fallará con un mensaje claro
    """,
    params={
        "stripe_invoice_id": Param(
            "",
            type="string",
            description="ID de la factura en Stripe (ej: in_1234567890)",
            minLength=1
        ),
        "correo_cliente": Param(
            "",
            type="string",
            description="Correo electrónico del cliente",
            minLength=1
        ),
        "monto_factura": Param(
            0.0,
            type="number",
            description="Monto total de la factura",
            minimum=0.01
        ),
        "fecha_vencimiento": Param(
            "",
            type="string",
            description="Fecha de vencimiento en formato YYYY-MM-DD o ISO (ej: 2025-02-15)",
            minLength=1
        ),
        "cuenta_ingresos": Param(
            "Services",
            type="string",
            description="Nombre de la cuenta de ingresos en QuickBooks (default: Services)",
        ),
        "qb_access_token": Param(
            "",
            type="string",
            description="Token de acceso de QuickBooks (opcional, usa QUICKBOOKS_ACCESS_TOKEN env var si está vacío)",
        ),
        "qb_realm_id": Param(
            "",
            type="string",
            description="ID de la compañía en QuickBooks (opcional, usa QUICKBOOKS_REALM_ID env var si está vacío)",
        ),
        "stripe_api_key": Param(
            "",
            type="string",
            description="API key de Stripe (opcional, usa STRIPE_API_KEY env var si está vacío)",
        ),
    },
    tags=["stripe", "quickbooks", "invoice", "finance", "sync"],
)
def stripe_invoice_sync_quickbooks_dag() -> None:
    """
    DAG principal para sincronizar facturas de Stripe a QuickBooks.
    """
    
    @task(task_id="create_quickbooks_invoice")
    def create_invoice(**context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea la factura en QuickBooks basada en la factura de Stripe.
        """
        params = context.get("params", {})
        stripe_invoice_id = params.get("stripe_invoice_id", "").strip()
        correo_cliente = params.get("correo_cliente", "").strip()
        monto_factura = params.get("monto_factura", 0.0)
        fecha_vencimiento = params.get("fecha_vencimiento", "").strip()
        cuenta_ingresos = params.get("cuenta_ingresos", "Services").strip()
        qb_access_token = params.get("qb_access_token", "").strip() or None
        qb_realm_id = params.get("qb_realm_id", "").strip() or None
        stripe_api_key = params.get("stripe_api_key", "").strip() or None
        
        # Validar parámetros requeridos
        if not stripe_invoice_id:
            raise ValueError(
                "El parámetro 'stripe_invoice_id' es requerido. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        if not correo_cliente:
            raise ValueError(
                "El parámetro 'correo_cliente' es requerido. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        if not monto_factura or monto_factura <= 0:
            raise ValueError(
                "El parámetro 'monto_factura' es requerido y debe ser mayor que cero. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        if not fecha_vencimiento:
            raise ValueError(
                "El parámetro 'fecha_vencimiento' es requerido. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        # Log de inicio
        print(f"🔄 Sincronizando factura Stripe {stripe_invoice_id} a QuickBooks...")
        print(f"  - Cliente: {correo_cliente}")
        print(f"  - Monto: ${monto_factura:.2f}")
        print(f"  - Fecha vencimiento: {fecha_vencimiento}")
        print(f"  - Cuenta ingresos: {cuenta_ingresos}")
        
        # Llamar a la función de creación de factura
        resultado = crear_factura_quickbooks(
            stripe_invoice_id=stripe_invoice_id,
            correo_cliente=correo_cliente,
            monto_factura=float(monto_factura),
            fecha_vencimiento=fecha_vencimiento,
            cuenta_ingresos=cuenta_ingresos,
            qb_access_token=qb_access_token,
            qb_realm_id=qb_realm_id,
            stripe_api_key=stripe_api_key
        )
        
        # Manejar resultado
        if resultado.get("estado") == "Éxito":
            qb_invoice_id = resultado.get("qb_invoice_id")
            pagada = resultado.get("pagada", False)
            
            print(f"✅ Factura creada exitosamente en QuickBooks")
            print(f"  - ID QuickBooks: {qb_invoice_id}")
            print(f"  - ID Stripe: {stripe_invoice_id}")
            
            if pagada:
                print(f"  - Estado: Pagada automáticamente (pago inmediato detectado)")
                if resultado.get("qb_payment_id"):
                    print(f"  - ID Pago QuickBooks: {resultado.get('qb_payment_id')}")
            else:
                print(f"  - Estado: Pendiente de pago")
            
            # Retornar resultado incluyendo el ID de QuickBooks
            return {
                "qb_invoice_id": qb_invoice_id,
                "stripe_invoice_id": stripe_invoice_id,
                "estado": "Éxito",
                "pagada": pagada
            }
        else:
            error_msg = resultado.get("estado", "Error desconocido")
            print(f"❌ Error al crear factura en QuickBooks: {error_msg}")
            # Si hay error, lanzar excepción para que Airflow marque la tarea como fallida
            raise Exception(f"Error al crear factura en QuickBooks: {error_msg}")
    
    # Ejecutar la tarea
    create_invoice()


# Crear instancia del DAG
stripe_invoice_sync_quickbooks_dag()



