from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="sales_ml_predictions",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Predicciones ML para Ventas
    
    Sistema que predice probabilidad de cierre usando Machine Learning:
    - Predice probabilidad de cierre para cada lead
    - Estima valor esperado del deal
    - Predice tiempo hasta cierre
    - Identifica leads de alto riesgo
    - Recomienda acciones óptimas
    
    **Funcionalidades:**
    - Integración con modelos ML (MLflow, custom endpoints)
    - Actualización de probability_pct basado en ML
    - Cálculo de valor esperado (expected value)
    - Identificación de señales de riesgo
    - Recomendaciones de acciones basadas en predicciones
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "ml_model_endpoint": Param("", type="string"),
        "ml_model_type": Param("probability", type="string", enum=["probability", "value", "time_to_close", "all"]),
        "enable_ml_predictions": Param(True, type="boolean"),
        "update_probability_auto": Param(True, type="boolean"),
        "min_probability_threshold": Param(20, type="integer", minimum=0, maximum=100),
        "max_leads_per_run": Param(200, type="integer", minimum=1, maximum=1000),
        "slack_webhook_url": Param("", type="string"),
    },
    tags=["sales", "ml", "predictions", "ai"],
)
def sales_ml_predictions() -> None:
    """
    DAG para predicciones ML de ventas.
    """
    
    @task(task_id="get_leads_for_prediction")
    def get_leads_for_prediction() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan predicciones."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id AS pipeline_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.score,
                p.priority,
                p.stage,
                p.source,
                p.utm_source,
                p.utm_campaign,
                p.estimated_value,
                p.probability_pct,
                p.assigned_to,
                p.qualified_at,
                p.last_contact_at,
                EXTRACT(EPOCH FROM (NOW() - p.qualified_at) / 86400) AS days_in_pipeline,
                EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
                COUNT(t.id) FILTER (WHERE t.status = 'completed') AS completed_tasks,
                COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks,
                COUNT(e.id) FILTER (WHERE e.event_type LIKE '%email%') AS email_events,
                COUNT(e.id) FILTER (WHERE e.event_type LIKE '%call%') AS call_events
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            LEFT JOIN sales_campaign_executions ce ON p.id = ce.pipeline_id
            LEFT JOIN sales_campaign_events e ON ce.id = e.execution_id
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND p.qualified_at >= NOW() - INTERVAL '90 days'
            GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name,
                     p.score, p.priority, p.stage, p.source, p.utm_source,
                     p.utm_campaign, p.estimated_value, p.probability_pct,
                     p.assigned_to, p.qualified_at, p.last_contact_at
            ORDER BY p.priority DESC, p.score DESC, p.qualified_at DESC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Obtenidos {len(leads)} leads para predicción")
        return leads
    
    @task(task_id="generate_ml_predictions")
    def generate_ml_predictions(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera predicciones ML para cada lead."""
        ctx = get_current_context()
        params = ctx["params"]
        ml_endpoint = str(params["ml_model_endpoint"]).strip()
        model_type = str(params["ml_model_type"])
        enable_ml = bool(params["enable_ml_predictions"])
        
        if not enable_ml or not ml_endpoint:
            logger.warning("ML predictions deshabilitadas o endpoint no configurado")
            return []
        
        predictions = []
        
        for lead in leads:
            try:
                # Preparar features para el modelo
                features = {
                    "lead_score": lead.get("score", 0),
                    "priority": lead.get("priority", "low"),
                    "stage": lead.get("stage", "qualified"),
                    "days_in_pipeline": int(lead.get("days_in_pipeline", 0) or 0),
                    "days_since_contact": int(lead.get("days_since_contact", 0) or 0),
                    "completed_tasks": int(lead.get("completed_tasks", 0) or 0),
                    "pending_tasks": int(lead.get("pending_tasks", 0) or 0),
                    "email_events": int(lead.get("email_events", 0) or 0),
                    "call_events": int(lead.get("call_events", 0) or 0),
                    "estimated_value": float(lead.get("estimated_value", 0) or 0),
                    "current_probability": int(lead.get("probability_pct", 0) or 0),
                    "source": lead.get("source", ""),
                }
                
                # Enviar a modelo ML
                response = requests.post(
                    ml_endpoint,
                    json={"features": features, "model_type": model_type},
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                
                predictions.append({
                    **lead,
                    "ml_probability": result.get("probability", lead.get("probability_pct", 0)),
                    "ml_expected_value": result.get("expected_value", 0),
                    "ml_time_to_close_days": result.get("time_to_close_days", None),
                    "ml_risk_score": result.get("risk_score", 0),
                    "ml_recommendations": result.get("recommendations", []),
                    "ml_confidence": result.get("confidence", 0.5),
                })
                
            except Exception as e:
                logger.warning(f"Error obteniendo predicción ML para lead {lead.get('lead_ext_id')}: {e}")
                # Fallback: usar probabilidad actual
                predictions.append({
                    **lead,
                    "ml_probability": lead.get("probability_pct", 0),
                    "ml_expected_value": 0,
                    "ml_time_to_close_days": None,
                    "ml_risk_score": 0,
                    "ml_recommendations": [],
                    "ml_confidence": 0.0,
                })
                continue
        
        logger.info(f"Predicciones generadas para {len(predictions)} leads")
        return predictions
    
    @task(task_id="update_predictions")
    def update_predictions(predictions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Actualiza predicciones en la base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        update_auto = bool(params["update_probability_auto"])
        min_prob = int(params["min_probability_threshold"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {
            "updated": 0,
            "skipped": 0,
            "high_risk_identified": 0,
            "high_value_identified": 0
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for pred in predictions:
                    try:
                        pipeline_id = pred["pipeline_id"]
                        ml_prob = int(pred.get("ml_probability", 0) or 0)
                        ml_expected_value = float(pred.get("ml_expected_value", 0) or 0)
                        ml_time_to_close = pred.get("ml_time_to_close_days")
                        ml_risk_score = float(pred.get("ml_risk_score", 0) or 0)
                        ml_recommendations = pred.get("ml_recommendations", [])
                        
                        # Solo actualizar si probabilidad ML es mayor que threshold
                        if ml_prob < min_prob:
                            stats["skipped"] += 1
                            continue
                        
                        # Actualizar metadata con predicciones
                        cur.execute("""
                            SELECT metadata FROM sales_pipeline WHERE id = %s
                        """, (pipeline_id,))
                        
                        result = cur.fetchone()
                        metadata = json.loads(result[0]) if result and result[0] else {}
                        
                        metadata["ml_predictions"] = {
                            "probability": ml_prob,
                            "expected_value": ml_expected_value,
                            "time_to_close_days": ml_time_to_close,
                            "risk_score": ml_risk_score,
                            "recommendations": ml_recommendations,
                            "confidence": pred.get("ml_confidence", 0.5),
                            "predicted_at": datetime.utcnow().isoformat()
                        }
                        
                        # Actualizar probability_pct si está habilitado
                        if update_auto and ml_prob > 0:
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET probability_pct = %s,
                                    metadata = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (ml_prob, json.dumps(metadata), pipeline_id))
                        else:
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET metadata = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (json.dumps(metadata), pipeline_id))
                        
                        conn.commit()
                        stats["updated"] += 1
                        
                        # Identificar leads de alto riesgo
                        if ml_risk_score > 0.7:
                            stats["high_risk_identified"] += 1
                        
                        # Identificar deals de alto valor esperado
                        if ml_expected_value > 50000:
                            stats["high_value_identified"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error actualizando predicción para lead {pred.get('lead_ext_id')}: {e}", exc_info=True)
                        continue
        
        logger.info(f"Predicciones actualizadas: {stats['updated']}, "
                   f"Alto riesgo: {stats['high_risk_identified']}, "
                   f"Alto valor: {stats['high_value_identified']}")
        
        try:
            Stats.incr("sales_ml_predictions.updated", stats["updated"])
        except Exception:
            pass
        
        return stats
    
    @task(task_id="notify_insights")
    def notify_insights(stats: Dict[str, int]) -> None:
        """Envía insights de predicciones a Slack."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_url = str(params["slack_webhook_url"]).strip()
        
        if not slack_url or stats["updated"] == 0:
            return
        
        try:
            message = f"""
🤖 *ML Predictions Update*

📊 *Resumen:*
• Predicciones actualizadas: {stats['updated']}
• Leads de alto riesgo identificados: {stats['high_risk_identified']}
• Deals de alto valor esperado: {stats['high_value_identified']}

💡 *Recomendaciones:*
• Revisar leads de alto riesgo para acciones preventivas
• Priorizar deals de alto valor esperado
• Usar predicciones para ajustar estrategia de seguimiento
            """
            
            requests.post(
                slack_url,
                json={"text": message},
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Error enviando notificación: {e}")
    
    # Pipeline
    leads = get_leads_for_prediction()
    predictions = generate_ml_predictions(leads)
    stats = update_predictions(predictions)
    notify_insights(stats)


dag = sales_ml_predictions()



