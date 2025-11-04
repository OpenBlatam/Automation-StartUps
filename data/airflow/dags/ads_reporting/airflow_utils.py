"""
Utilidades específicas para integración con Airflow.

Incluye:
- Helpers para tasks de Airflow
- Funciones de conveniencia para DAGs
- Integración con XComs
- Helpers para contextos de Airflow
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.utils.task_group import TaskGroup
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    logger.warning("Airflow no disponible")


def get_dag_context(**kwargs) -> Dict[str, Any]:
    """
    Extrae contexto de DAG desde kwargs de Airflow.
    
    Args:
        **kwargs: kwargs del contexto de Airflow
        
    Returns:
        Diccionario con información del contexto
    """
    context = {
        "dag_id": kwargs.get("dag").dag_id if kwargs.get("dag") else None,
        "run_id": kwargs.get("run_id"),
        "task_instance": kwargs.get("task_instance"),
        "execution_date": kwargs.get("execution_date"),
        "params": kwargs.get("params", {}),
        "prev_execution_date": kwargs.get("prev_execution_date"),
        "next_execution_date": kwargs.get("next_execution_date"),
    }
    
    # Convertir execution_date a string si es datetime
    if context["execution_date"] and isinstance(context["execution_date"], datetime):
        context["execution_date_str"] = context["execution_date"].strftime("%Y-%m-%d")
    
    return context


def get_task_params(**kwargs) -> Dict[str, Any]:
    """
    Obtiene parámetros de la tarea desde contexto de Airflow.
    
    Args:
        **kwargs: kwargs del contexto de Airflow
        
    Returns:
        Diccionario con parámetros
    """
    params = kwargs.get("params", {})
    
    # También buscar en dag.params si existe
    if kwargs.get("dag") and hasattr(kwargs["dag"], "params"):
        dag_params = kwargs["dag"].params or {}
        params = {**dag_params, **params}
    
    return params


def push_to_xcom(
    key: str,
    value: Any,
    **kwargs
) -> None:
    """
    Pushea valor a XCom de Airflow.
    
    Args:
        key: Clave para XCom
        value: Valor a pushear
        **kwargs: kwargs del contexto de Airflow
    """
    if not AIRFLOW_AVAILABLE:
        logger.warning("Airflow no disponible, no se puede pushear a XCom")
        return
    
    task_instance = kwargs.get("task_instance")
    if task_instance:
        task_instance.xcom_push(key=key, value=value)
        logger.info(f"Pushed to XCom: {key}")
    else:
        logger.warning("No task_instance disponible para XCom")


def pull_from_xcom(
    key: str,
    task_ids: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Pull valor desde XCom de Airflow.
    
    Args:
        key: Clave de XCom
        task_ids: Task ID del cual pull (opcional)
        **kwargs: kwargs del contexto de Airflow
        
    Returns:
        Valor desde XCom o None
    """
    if not AIRFLOW_AVAILABLE:
        logger.warning("Airflow no disponible, no se puede pull de XCom")
        return None
    
    task_instance = kwargs.get("task_instance")
    if task_instance:
        try:
            if task_ids:
                value = task_instance.xcom_pull(key=key, task_ids=task_ids)
            else:
                value = task_instance.xcom_pull(key=key)
            logger.info(f"Pulled from XCom: {key}")
            return value
        except Exception as e:
            logger.warning(f"Error pulling XCom {key}: {str(e)}")
            return None
    else:
        logger.warning("No task_instance disponible para XCom")
        return None


def create_airflow_task(
    task_id: str,
    python_callable: callable,
    dag: Any,
    **task_kwargs
) -> Any:
    """
    Crea task de Airflow con configuración por defecto.
    
    Args:
        task_id: ID de la tarea
        python_callable: Función a ejecutar
        dag: DAG object
        **task_kwargs: Argumentos adicionales para PythonOperator
        
    Returns:
        PythonOperator configurado
    """
    if not AIRFLOW_AVAILABLE:
        raise ImportError("Airflow no disponible")
    
    default_kwargs = {
        "task_id": task_id,
        "python_callable": python_callable,
        "dag": dag,
    }
    
    default_kwargs.update(task_kwargs)
    
    return PythonOperator(**default_kwargs)


def extract_and_store_task(
    platform: str,
    date_start: str,
    date_stop: str,
    table_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Task de Airflow para extraer y almacenar datos.
    
    Args:
        platform: Plataforma (facebook, tiktok, google)
        date_start: Fecha inicio
        date_stop: Fecha fin
        table_name: Nombre de tabla
        **kwargs: kwargs de Airflow
        
    Returns:
        Diccionario con resultados
    """
    from ads_reporting.integration import extract_and_store
    
    # Obtener configuración según plataforma
    if platform == "facebook":
        from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
        import os
        
        config = FacebookAdsConfig(
            access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
            ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
        )
        
        with FacebookAdsClient(config) as client:
            from ads_reporting.extractors import FacebookExtractor
            extractor = FacebookExtractor(client)
            
            from ads_reporting.storage import get_storage
            storage = get_storage("postgres")
            
            result = extract_and_store(
                client, extractor, storage,
                date_start, date_stop,
                table_name=table_name,
                use_cache=True,
                validate=True,
                process=True
            )
            
            # Pushear a XCom
            push_to_xcom("extraction_result", result, **kwargs)
            
            return result
    else:
        raise ValueError(f"Plataforma no soportada: {platform}")


def get_date_range_from_context(
    days_back: int = 7,
    **kwargs
) -> tuple[str, str]:
    """
    Obtiene rango de fechas desde contexto de Airflow.
    
    Args:
        days_back: Días hacia atrás desde execution_date
        **kwargs: kwargs de Airflow
        
    Returns:
        Tuple (date_start, date_stop)
    """
    from ads_reporting.helpers import get_date_range
    from datetime import timedelta
    
    execution_date = kwargs.get("execution_date")
    
    if execution_date and isinstance(execution_date, datetime):
        # Usar execution_date como referencia
        date_stop = execution_date.strftime("%Y-%m-%d")
        date_start = (execution_date - timedelta(days=days_back)).strftime("%Y-%m-%d")
        return (date_start, date_stop)
    else:
        # Usar función helper normal
        return get_date_range(days_back=days_back)


def log_task_start(task_name: str, **kwargs) -> None:
    """
    Log inicio de task de Airflow.
    
    Args:
        task_name: Nombre de la tarea
        **kwargs: kwargs de Airflow
    """
    context = get_dag_context(**kwargs)
    logger.info(
        f"Starting task: {task_name}",
        extra={
            "dag_id": context.get("dag_id"),
            "run_id": context.get("run_id"),
            "execution_date": context.get("execution_date_str")
        }
    )


def log_task_end(task_name: str, result: Any, **kwargs) -> None:
    """
    Log fin de task de Airflow.
    
    Args:
        task_name: Nombre de la tarea
        result: Resultado de la tarea
        **kwargs: kwargs de Airflow
    """
    context = get_dag_context(**kwargs)
    
    result_summary = None
    if isinstance(result, dict):
        result_summary = {
            k: v for k, v in result.items()
            if isinstance(v, (str, int, float, bool, type(None)))
        }
    
    logger.info(
        f"Completed task: {task_name}",
        extra={
            "dag_id": context.get("dag_id"),
            "run_id": context.get("run_id"),
            "result_summary": result_summary
        }
    )


def handle_task_error(
    task_name: str,
    error: Exception,
    **kwargs
) -> None:
    """
    Maneja errores en tasks de Airflow con logging mejorado.
    
    Args:
        task_name: Nombre de la tarea
        error: Excepción capturada
        **kwargs: kwargs de Airflow
    """
    context = get_dag_context(**kwargs)
    
    logger.error(
        f"Error in task: {task_name}",
        exc_info=True,
        extra={
            "dag_id": context.get("dag_id"),
            "run_id": context.get("run_id"),
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
    )
    
    # Pushear error a XCom si es posible
    try:
        push_to_xcom(
            f"{task_name}_error",
            {
                "error_type": type(error).__name__,
                "error_message": str(error)
            },
            **kwargs
        )
    except Exception:
        pass  # Ignorar errores de XCom

