"""
DAG de Airflow para comparar ingresos de Stripe con QuickBooks automáticamente.

Este DAG ejecuta comparaciones periódicas de ingresos entre Stripe y QuickBooks,
persiste los resultados en la base de datos y envía alertas cuando las diferencias
exceden el umbral configurado.

Schedule: Diario a las 06:00 UTC (para comparar el día anterior)
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

from data.airflow.dags.stripe_quickbooks_revenue_compare import (
    comparar_ingresos_stripe_quickbooks,
    persistir_comparacion,
    enviar_alerta,
    analizar_tendencias,
    obtener_historial_comparaciones
)
from data.airflow.plugins.db import get_conn


logger = logging.getLogger(__name__)


def _get_env_var(name: str, default: str | None = None) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    try:
        return str(Variable.get(name, default_var=default))
    except Exception:
        return default or ""


@dag(
    dag_id="stripe_quickbooks_revenue_compare",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 6 * * *",  # Diario a las 06:00 UTC
    catchup=False,
    default_args={
        "owner": "finance",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "email_on_failure": False,
        "email_on_retry": False,
    },
    description="Compara ingresos netos de Stripe con ingresos registrados en QuickBooks",
    tags=["finance", "reconciliation", "stripe", "quickbooks", "alerts"],
    doc_md="""
    # Comparación de Ingresos Stripe vs QuickBooks
    
    Este DAG compara automáticamente los ingresos netos de Stripe con los ingresos
    registrados en QuickBooks para detectar discrepancias.
    
    ## Funcionalidades
    
    - Comparación diaria automática del día anterior
    - Persistencia de resultados en base de datos
    - Alertas automáticas via Slack y Email cuando hay diferencias
    - Análisis de tendencias históricas
    - Historial de comparaciones
    
    ## Parámetros
    
    - `fecha_inicio`: Fecha de inicio en formato YYYY-MM-DD (default: día anterior)
    - `fecha_fin`: Fecha de fin en formato YYYY-MM-DD (default: día anterior)
    - `umbral`: Umbral de diferencia para alerta en dólares (default: 100.0)
    - `cuenta_quickbooks`: Nombre de la cuenta en QuickBooks (default: "Ventas Stripe")
    - `enable_alerts`: Habilitar alertas (default: true)
    - `enable_persistence`: Persistir resultados en BD (default: true)
    
    ## Variables de Entorno Requeridas
    
    - `STRIPE_API_KEY`: API Key de Stripe
    - `QUICKBOOKS_ACCESS_TOKEN`: Token de acceso OAuth2 de QuickBooks
    - `QUICKBOOKS_REALM_ID`: ID de la compañía en QuickBooks
    - `QUICKBOOKS_BASE`: URL base de la API (default: sandbox)
    - `SLACK_WEBHOOK_URL`: URL del webhook de Slack (opcional, para alertas)
    - `ALERT_EMAILS`: Emails para alertas (opcional, separados por comas)
    
    ## Salidas
    
    - Comparación persistida en tabla `stripe_quickbooks_revenue_comparisons`
    - Alertas enviadas a Slack y Email si la diferencia excede el umbral
    - Logs detallados de la comparación
    """,
    params={
        "fecha_inicio": None,  # Se calcula automáticamente si es None
        "fecha_fin": None,  # Se calcula automáticamente si es None
        "umbral": 100.0,
        "cuenta_quickbooks": "Ventas Stripe",
        "enable_alerts": True,
        "enable_persistence": True,
    },
)
def stripe_quickbooks_revenue_compare_dag() -> None:
    """DAG principal para comparación de ingresos Stripe vs QuickBooks."""
    
    @task(task_id="comparar_ingresos")
    def comparar_ingresos(**context) -> Dict[str, Any]:
        """
        Compara ingresos de Stripe con QuickBooks para el período especificado.
        """
        from airflow.operators.python import get_current_context
        
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        # Calcular fechas si no se proporcionan
        if params.get("fecha_inicio") and params.get("fecha_fin"):
            fecha_inicio = params["fecha_inicio"]
            fecha_fin = params["fecha_fin"]
        else:
            # Por defecto, comparar el día anterior
            data_interval_end = ctx.get("data_interval_end")
            if data_interval_end:
                fecha_fin = (data_interval_end - timedelta(days=1)).date().isoformat()
                fecha_inicio = fecha_fin  # Comparar un solo día
            else:
                # Fallback: usar fecha de ayer
                from datetime import date
                fecha_fin = (date.today() - timedelta(days=1)).isoformat()
                fecha_inicio = fecha_fin
        
        umbral = float(params.get("umbral", 100.0))
        cuenta_quickbooks = params.get("cuenta_quickbooks", "Ventas Stripe")
        
        logger.info(
            f"Iniciando comparación de ingresos",
            extra={
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "umbral": umbral,
                "cuenta_quickbooks": cuenta_quickbooks
            }
        )
        
        resultado = comparar_ingresos_stripe_quickbooks(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            umbral=umbral,
            cuenta_quickbooks=cuenta_quickbooks
        )
        
        # Agregar fechas al resultado para las siguientes tareas
        resultado["fecha_inicio"] = fecha_inicio
        resultado["fecha_fin"] = fecha_fin
        
        return resultado
    
    @task(task_id="persistir_resultado")
    def persistir_resultado(resultado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Persiste el resultado de la comparación en la base de datos.
        """
        from airflow.operators.python import get_current_context
        
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        if not params.get("enable_persistence", True):
            logger.info("Persistencia deshabilitada, saltando")
            return resultado
        
        fecha_inicio = resultado.get("fecha_inicio")
        fecha_fin = resultado.get("fecha_fin")
        
        if not fecha_inicio or not fecha_fin:
            logger.warning("Fechas no disponibles, no se puede persistir")
            return resultado
        
        try:
            with get_conn() as conn:
                record_id = persistir_comparacion(
                    resultado=resultado,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    db_conn=conn
                )
                
                if record_id:
                    logger.info(f"Resultado persistido exitosamente con ID: {record_id}")
                    resultado["persisted_id"] = record_id
                else:
                    logger.warning("No se pudo persistir el resultado")
                    
        except Exception as e:
            logger.error(f"Error persistiendo resultado: {e}", exc_info=True)
            # No fallar el DAG si la persistencia falla
        
        return resultado
    
    @task(task_id="enviar_alertas")
    def enviar_alertas(resultado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía alertas si la diferencia excede el umbral.
        """
        from airflow.operators.python import get_current_context
        
        ctx = get_current_context()
        params = ctx.get("params", {})
        
        if not params.get("enable_alerts", True):
            logger.info("Alertas deshabilitadas, saltando")
            return resultado
        
        fecha_inicio = resultado.get("fecha_inicio")
        fecha_fin = resultado.get("fecha_fin")
        detalles = resultado.get("detalles", {})
        
        if not fecha_inicio or not fecha_fin:
            logger.warning("Fechas no disponibles, no se pueden enviar alertas")
            return resultado
        
        try:
            enviar_alerta(
                resultado=resultado,
                detalles=detalles,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            logger.info("Proceso de alertas completado")
        except Exception as e:
            logger.error(f"Error enviando alertas: {e}", exc_info=True)
            # No fallar el DAG si las alertas fallan
        
        return resultado
    
    @task(task_id="analizar_tendencias")
    def analizar_tendencias_task(**context) -> Dict[str, Any]:
        """
        Analiza tendencias de las comparaciones históricas.
        """
        try:
            with get_conn() as conn:
                tendencias = analizar_tendencias(dias=90, db_conn=conn)
                
                logger.info(
                    "Análisis de tendencias completado",
                    extra=tendencias
                )
                
                # Si hay muchas alertas recientes, enviar notificación
                total_alertas = tendencias.get("total_alertas", 0)
                total_comparaciones = tendencias.get("total_comparaciones", 0)
                
                if total_comparaciones > 0:
                    tasa_alertas = (total_alertas / total_comparaciones) * 100
                    
                    if tasa_alertas > 30 and total_comparaciones >= 7:
                        # Más del 30% de alertas en los últimos 90 días
                        logger.warning(
                            f"Alta tasa de alertas: {tasa_alertas:.1f}% ({total_alertas}/{total_comparaciones})",
                            extra={"tasa_alertas": tasa_alertas, "tendencias": tendencias}
                        )
                
                return tendencias
                
        except Exception as e:
            logger.error(f"Error analizando tendencias: {e}", exc_info=True)
            return {}
    
    @task(task_id="reportar_resultado")
    def reportar_resultado(resultado: Dict[str, Any], tendencias: Dict[str, Any]) -> None:
        """
        Reporta el resultado final de la comparación.
        """
        estado = resultado.get("estado", "Error")
        detalles = resultado.get("detalles", {})
        
        logger.info(
            f"Comparación completada: {estado}",
            extra={
                "estado": estado,
                "ingreso_stripe": detalles.get("ingreso_stripe", 0.0),
                "ingreso_quickbooks": detalles.get("ingreso_quickbooks", 0.0),
                "diferencia": detalles.get("diferencia", 0.0),
                "tendencias": tendencias
            }
        )
        
        # Log detallado para debugging
        if estado == "Alerta":
            logger.warning(
                f"⚠️ ALERTA: Diferencia de ${detalles.get('diferencia', 0):,.2f} "
                f"excede umbral de ${detalles.get('umbral', 0):,.2f}"
            )
        elif estado == "Ok":
            logger.info(
                f"✓ Comparación OK: Diferencia de ${detalles.get('diferencia', 0):,.2f} "
                f"dentro del umbral"
            )
    
    # Construir el flujo del DAG
    resultado_comparacion = comparar_ingresos()
    resultado_persistido = persistir_resultado(resultado_comparacion)
    resultado_con_alertas = enviar_alertas(resultado_persistido)
    tendencias = analizar_tendencias_task()
    
    # Reportar resultado final (usa resultados de ambas ramas)
    reportar_resultado(resultado_con_alertas, tendencias)
    
    return None


# Crear el DAG
dag = stripe_quickbooks_revenue_compare_dag()



