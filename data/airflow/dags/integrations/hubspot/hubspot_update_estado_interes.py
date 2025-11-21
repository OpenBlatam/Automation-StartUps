"""
DAG de Airflow para actualizar la propiedad 'estado_interés' de contactos en HubSpot.
Puede ejecutarse manualmente o programado, y acepta parámetros dinámicos.
"""
from datetime import datetime, timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context

from hubspot_update_contact import actualizar_estado_interes


@dag(
    dag_id="hubspot_update_estado_interes",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger o programado según necesidad
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Actualización de Estado de Interés en HubSpot (Mejorado)
    
    DAG para actualizar la propiedad 'estado_interés' de contactos en HubSpot.
    
    **Funcionalidades mejoradas:**
    - ✅ Retry con exponential backoff automático
    - ✅ Manejo de rate limiting (429) con respeto de Retry-After
    - ✅ Logging estructurado con contexto completo
    - ✅ Validación robusta de inputs
    - ✅ Timeout configurable
    - ✅ Métricas de performance (duración, retries)
    - ✅ Soporte para retorno como objeto estructurado o string (compatibilidad)
    
    **Parámetros requeridos:**
    - `hubspot_contact_id`: ID del contacto en HubSpot
    - `nuevo_estado`: Nuevo valor para 'estado_interés'
    
    **Parámetros opcionales:**
    - `hubspot_token`: Token de autenticación (usa env var HUBSPOT_TOKEN si está vacío)
    - `hubspot_base`: URL base de API (usa env var HUBSPOT_BASE si está vacío, default: https://api.hubapi.com)
    - `max_retries`: Máximo de reintentos (default: 3, range: 0-10)
    - `timeout`: Timeout en segundos (default: 30, range: 5-120)
    - `return_result_object`: Si True, retorna objeto completo con detalles (default: False)
    
    **Ejemplo de uso básico:**
    ```json
    {
        "hubspot_contact_id": "12345678",
        "nuevo_estado": "calificado"
    }
    ```
    
    **Ejemplo de uso avanzado:**
    ```json
    {
        "hubspot_contact_id": "12345678",
        "nuevo_estado": "calificado",
        "max_retries": 5,
        "timeout": 60,
        "return_result_object": true
    }
    ```
    
    **Retorno:**
    - Si `return_result_object=false` (default): 
      - 'Éxito' si la actualización fue exitosa
      - 'CÓDIGO_ERROR: mensaje' si falla
    - Si `return_result_object=true`:
      - Objeto `HubSpotUpdateResult` con campos: success, status_code, message, duration_ms, retries, error_details
    
    **Mejoras de robustez:**
    - Manejo automático de rate limiting (429) respetando headers Retry-After
    - Retry automático en caso de timeouts o errores de conexión
    - Logging estructurado para mejor observabilidad
    - Métricas de performance incluidas en logs
    
    **Requisitos:**
    - Variable de entorno HUBSPOT_TOKEN configurada (o pasar como parámetro)
    """,
    params={
        "hubspot_contact_id": Param(
            "",
            type="string",
            description="ID del contacto en HubSpot",
            minLength=1
        ),
        "nuevo_estado": Param(
            "",
            type="string",
            description="Nuevo valor para la propiedad 'estado_interés'",
            minLength=1
        ),
        "hubspot_token": Param(
            "",
            type="string",
            description="Token de autenticación de HubSpot (opcional, usa HUBSPOT_TOKEN env var si está vacío)",
        ),
        "hubspot_base": Param(
            "",
            type="string",
            description="URL base de la API de HubSpot (opcional, usa HUBSPOT_BASE env var si está vacío)",
        ),
        "max_retries": Param(
            3,
            type="integer",
            description="Máximo de reintentos en caso de error (default: 3)",
            minimum=0,
            maximum=10,
        ),
        "timeout": Param(
            30,
            type="integer",
            description="Timeout en segundos para la petición (default: 30)",
            minimum=5,
            maximum=120,
        ),
        "return_result_object": Param(
            False,
            type="boolean",
            description="Si True, retorna objeto completo con detalles en lugar de string",
        ),
    },
    tags=["hubspot", "crm", "contacts", "api"],
)
def hubspot_update_estado_interes_dag() -> None:
    """
    DAG principal para actualizar estado_interés de contactos HubSpot.
    """
    
    @task(task_id="update_contact_estado_interes")
    def update_contact(**context: Dict[str, Any]) -> str:
        """
        Actualiza la propiedad 'estado_interés' del contacto.
        """
        params = context.get("params", {})
        hubspot_contact_id = params.get("hubspot_contact_id", "").strip()
        nuevo_estado = params.get("nuevo_estado", "").strip()
        hubspot_token = params.get("hubspot_token", "").strip() or None
        hubspot_base = params.get("hubspot_base", "").strip() or None
        max_retries = params.get("max_retries", 3)
        timeout = params.get("timeout", 30)
        return_result_object = params.get("return_result_object", False)
        
        # Validar parámetros requeridos
        if not hubspot_contact_id:
            raise ValueError(
                "El parámetro 'hubspot_contact_id' es requerido. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        if not nuevo_estado:
            raise ValueError(
                "El parámetro 'nuevo_estado' es requerido. "
                "Proporciónalo en los parámetros del DAG."
            )
        
        # Log de inicio
        print(f"🔄 Actualizando contacto {hubspot_contact_id} a estado '{nuevo_estado}'... (max_retries: {max_retries}, timeout: {timeout}s)")
        
        # Llamar a la función de actualización mejorada
        resultado = actualizar_estado_interes(
            hubspot_contact_id=hubspot_contact_id,
            nuevo_estado=nuevo_estado,
            hubspot_token=hubspot_token,
            hubspot_base=hubspot_base,
            max_retries=max_retries,
            timeout=timeout,
            return_result_object=return_result_object
        )
        
        # Manejar resultado (puede ser string o objeto)
        from hubspot_update_contact import HubSpotUpdateResult
        
        if return_result_object and isinstance(resultado, HubSpotUpdateResult):
            if resultado.success:
                print(
                    f"✅ Contacto {hubspot_contact_id} actualizado exitosamente a estado '{nuevo_estado}' "
                    f"(duración: {resultado.duration_ms:.2f}ms, retries: {resultado.retries})"
                )
            else:
                error_msg = f"❌ Error al actualizar contacto {hubspot_contact_id}: {resultado.message} (status: {resultado.status_code})"
                print(error_msg)
                # Si hay error, lanzar excepción para que Airflow marque la tarea como fallida
                raise Exception(f"Error al actualizar contacto: {resultado.message} (status: {resultado.status_code})")
        else:
            # Compatibilidad con código existente (string)
            if resultado == "Éxito":
                print(f"✅ Contacto {hubspot_contact_id} actualizado exitosamente a estado '{nuevo_estado}'")
            else:
                print(f"❌ Error al actualizar contacto {hubspot_contact_id}: {resultado}")
                # Si hay error, lanzar excepción para que Airflow marque la tarea como fallida
                raise Exception(f"Error al actualizar contacto: {resultado}")
        
        return resultado
    
    # Ejecutar la tarea
    update_contact()


# Crear instancia del DAG
hubspot_update_estado_interes_dag()

