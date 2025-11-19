"""
DAG de Airflow para actualización batch de propiedades de contactos en HubSpot.

Permite actualizar múltiples contactos en una sola ejecución, útil para:
- Migraciones masivas
- Actualizaciones programadas desde bases de datos
- Procesamiento de archivos CSV/JSON
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

from hubspot_update_contact import actualizar_contactos_batch, BatchUpdateResult


@dag(
    dag_id="hubspot_batch_update_estado_interes",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Actualización Batch de Estado de Interés en HubSpot
    
    DAG para actualizar la propiedad 'estado_interés' de múltiples contactos en HubSpot.
    
    **Funcionalidades:**
    - ✅ Actualización batch eficiente con rate limiting automático
    - ✅ Pausas entre batches para evitar rate limits
    - ✅ Continuación en caso de error (opcional)
    - ✅ Estadísticas completas de éxito/fallo
    - ✅ Logging detallado de cada contacto
    
    **Parámetros requeridos:**
    - `updates`: Lista JSON de actualizaciones en formato:
      ```json
      [
        {"contact_id": "123", "valor": "calificado"},
        {"contact_id": "456", "valor": "interesado"}
      ]
      ```
    
    **Parámetros opcionales:**
    - `propiedad`: Nombre de la propiedad a actualizar (default: "estado_interés")
    - `hubspot_token`: Token de autenticación (usa env var si está vacío)
    - `hubspot_base`: URL base de API (usa env var si está vacío)
    - `max_retries`: Máximo de reintentos por contacto (default: 3)
    - `timeout`: Timeout en segundos por petición (default: 30)
    - `batch_size`: Contactos por batch antes de pausar (default: 10)
    - `batch_delay`: Segundos de espera entre batches (default: 0.1)
    - `continue_on_error`: Continuar con otros si uno falla (default: true)
    
    **Ejemplo de uso:**
    ```json
    {
        "updates": [
            {"contact_id": "12345678", "valor": "calificado"},
            {"contact_id": "87654321", "valor": "interesado"}
        ],
        "batch_size": 5,
        "continue_on_error": true
    }
    ```
    
    **Retorno:**
    - Objeto BatchUpdateResult con estadísticas agregadas:
      - total: Total de contactos procesados
      - successful: Contactos actualizados exitosamente
      - failed: Contactos que fallaron
      - success_rate: Porcentaje de éxito
      - duration_ms: Duración total en milisegundos
      - results: Lista detallada de cada resultado
    """,
    params={
        "updates": Param(
            [],
            type="array",
            description="Lista de actualizaciones: [{\"contact_id\": \"...\", \"valor\": \"...\"}, ...]",
        ),
        "propiedad": Param(
            "estado_interés",
            type="string",
            description="Nombre de la propiedad a actualizar",
        ),
        "hubspot_token": Param(
            "",
            type="string",
            description="Token de autenticación (opcional)",
        ),
        "hubspot_base": Param(
            "",
            type="string",
            description="URL base de API (opcional)",
        ),
        "max_retries": Param(
            3,
            type="integer",
            minimum=0,
            maximum=10,
            description="Máximo de reintentos por contacto",
        ),
        "timeout": Param(
            30,
            type="integer",
            minimum=5,
            maximum=120,
            description="Timeout por petición en segundos",
        ),
        "batch_size": Param(
            10,
            type="integer",
            minimum=1,
            maximum=100,
            description="Contactos por batch",
        ),
        "batch_delay": Param(
            0.1,
            type="number",
            minimum=0,
            maximum=10,
            description="Segundos de espera entre batches",
        ),
        "continue_on_error": Param(
            True,
            type="boolean",
            description="Continuar con otros contactos si uno falla",
        ),
    },
    tags=["hubspot", "crm", "contacts", "api", "batch"],
)
def hubspot_batch_update_dag() -> None:
    """
    DAG principal para actualización batch de estado_interés.
    """
    
    @task(task_id="batch_update_contacts")
    def batch_update(**context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza múltiples contactos en batch.
        """
        params = context.get("params", {})
        updates = params.get("updates", [])
        
        if not updates or not isinstance(updates, list):
            raise ValueError(
                "El parámetro 'updates' es requerido y debe ser una lista. "
                "Formato: [{\"contact_id\": \"...\", \"valor\": \"...\"}, ...]"
            )
        
        if len(updates) == 0:
            raise ValueError("La lista 'updates' no puede estar vacía")
        
        # Validar formato de updates
        for i, update in enumerate(updates):
            if not isinstance(update, dict):
                raise ValueError(f"Update #{i+1} debe ser un diccionario, recibido: {type(update)}")
            if not update.get("contact_id") and not update.get("hubspot_contact_id"):
                raise ValueError(f"Update #{i+1} debe tener 'contact_id' o 'hubspot_contact_id'")
            if not update.get("valor") and not update.get("value") and not update.get("nuevo_estado"):
                raise ValueError(f"Update #{i+1} debe tener 'valor', 'value' o 'nuevo_estado'")
        
        propiedad = params.get("propiedad", "estado_interés")
        hubspot_token = params.get("hubspot_token", "").strip() or None
        hubspot_base = params.get("hubspot_base", "").strip() or None
        max_retries = params.get("max_retries", 3)
        timeout = params.get("timeout", 30)
        batch_size = params.get("batch_size", 10)
        batch_delay = float(params.get("batch_delay", 0.1))
        continue_on_error = params.get("continue_on_error", True)
        
        print(f"🔄 Iniciando actualización batch de {len(updates)} contactos...")
        print(f"   Propiedad: {propiedad}")
        print(f"   Batch size: {batch_size}, Delay: {batch_delay}s")
        print(f"   Continue on error: {continue_on_error}")
        
        # Ejecutar actualización batch
        resultado: BatchUpdateResult = actualizar_contactos_batch(
            updates=updates,
            propiedad=propiedad,
            hubspot_token=hubspot_token,
            hubspot_base=hubspot_base,
            max_retries=max_retries,
            timeout=timeout,
            batch_size=batch_size,
            batch_delay=batch_delay,
            continue_on_error=continue_on_error
        )
        
        # Log de resultados
        print(f"\n✅ Actualización batch completada:")
        print(f"   Total: {resultado.total}")
        print(f"   Exitosos: {resultado.successful}")
        print(f"   Fallidos: {resultado.failed}")
        print(f"   Tasa de éxito: {resultado.success_rate:.2f}%")
        print(f"   Duración: {resultado.duration_ms:.2f}ms")
        
        # Mostrar errores si los hay
        if resultado.failed > 0:
            print(f"\n❌ Errores encontrados:")
            for i, result in enumerate(resultado.results):
                if not result.success:
                    print(f"   - Contacto {result.contact_id}: {result.message}")
        
        # Si hay fallos y continue_on_error es False, lanzar excepción
        if resultado.failed > 0 and not continue_on_error:
            raise Exception(
                f"Actualización batch falló: {resultado.failed}/{resultado.total} contactos fallaron"
            )
        
        return resultado.to_dict()
    
    # Ejecutar la tarea
    batch_update()


# Crear instancia del DAG
hubspot_batch_update_dag()



