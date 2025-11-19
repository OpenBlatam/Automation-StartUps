"""
DAG de Insights de Machine Learning para Contratos
Genera predicciones y análisis ML periódicos
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from data.airflow.plugins.contract_ml import (
    predict_contract_renewal_probability,
    detect_contract_anomalies,
    get_contract_health_score
)

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


@dag(
    dag_id="contract_ml_insights",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(hours=24),  # Ejecutar diariamente
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract ML Insights - Análisis de Machine Learning
    
    DAG que se ejecuta diariamente para:
    - ✅ Calcular health scores de contratos
    - ✅ Detectar anomalías
    - ✅ Predecir probabilidades de renovación
    - ✅ Generar insights para dashboard
    
    **Funcionalidad:**
    - Analiza contratos activos y pendientes
    - Identifica contratos con problemas
    - Genera predicciones para toma de decisiones
    """,
    description="Análisis de ML para contratos",
    tags=["contracts", "legal", "ml", "analytics", "insights"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_ml_insights() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="analyze_contracts", pool=CONTRACT_POOL)
    def analyze_contracts() -> dict:
        """Analiza contratos con ML"""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.ml.analyze.start", 1)
            except Exception:
                pass
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Obtener contratos activos para analizar
        query = """
            SELECT contract_id, contract_type, status
            FROM contracts
            WHERE status IN ('pending_signature', 'partially_signed', 'fully_signed')
              AND created_at >= NOW() - INTERVAL '90 days'
            ORDER BY created_at DESC
            LIMIT 100
        """
        
        contracts = hook.get_records(query)
        
        results = {
            "analyzed": 0,
            "health_scores": [],
            "anomalies_found": 0,
            "renewal_predictions": [],
            "errors": []
        }
        
        for row in contracts:
            contract_id = row[0]
            results["analyzed"] += 1
            
            try:
                # Health score
                health = get_contract_health_score(contract_id)
                results["health_scores"].append({
                    "contract_id": contract_id,
                    "score": health.get("health_score", 0),
                    "level": health.get("health_level", "unknown")
                })
                
                # Anomalies
                anomalies = detect_contract_anomalies(contract_id)
                if anomalies.get("has_anomalies"):
                    results["anomalies_found"] += 1
                    results["anomalies"] = results.get("anomalies", [])
                    results["anomalies"].append({
                        "contract_id": contract_id,
                        "anomalies": anomalies.get("anomalies", [])
                    })
                
                # Renewal prediction (solo para firmados)
                if row[2] == "fully_signed":
                    renewal = predict_contract_renewal_probability(contract_id)
                    results["renewal_predictions"].append({
                        "contract_id": contract_id,
                        "probability": renewal.get("renewal_probability", 0),
                        "recommendation": renewal.get("recommendation", "unknown")
                    })
                
            except Exception as e:
                error_msg = f"Error analizando {contract_id}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Calcular promedios
        if results["health_scores"]:
            avg_health = sum(h["score"] for h in results["health_scores"]) / len(results["health_scores"])
            results["avg_health_score"] = round(avg_health, 1)
        
        if results["renewal_predictions"]:
            avg_renewal = sum(r["probability"] for r in results["renewal_predictions"]) / len(results["renewal_predictions"])
            results["avg_renewal_probability"] = round(avg_renewal, 2)
        
        logger.info(
            f"Análisis ML completado",
            extra={
                "analyzed": results["analyzed"],
                "anomalies": results["anomalies_found"]
            }
        )
        
        if Stats:
            try:
                Stats.incr("contracts.ml.analyze.completed", 1)
                Stats.gauge("contracts.ml.avg_health_score", results.get("avg_health_score", 0))
            except Exception:
                pass
        
        return results

    # Define task flow
    results = analyze_contracts()
    
    return None


dag = contract_ml_insights()

