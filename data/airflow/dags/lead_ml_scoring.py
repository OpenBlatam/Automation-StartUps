from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_ml_scoring",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */12 * * *",  # Cada 12 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Machine Learning Scoring Avanzado
    
    Calcula score predictivo usando modelos ML basados en:
    - Historial de conversión
    - Patrones de comportamiento
    - Características del lead
    - Tiempo de respuesta
    - Engagement histórico
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `max_leads_per_run`: Máximo de leads a procesar (default: 200)
    - `ml_model_type`: Tipo de modelo ('gradient_boosting', 'random_forest', 'neural_network')
    - `retrain_model`: Reentrenar modelo (default: false)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(200, type="integer", minimum=1, maximum=1000),
        "ml_model_type": Param("gradient_boosting", type="string", enum=["gradient_boosting", "random_forest", "neural_network"]),
        "retrain_model": Param(False, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "ml", "scoring", "automation"],
)
def lead_ml_scoring() -> None:
    """
    DAG para scoring ML avanzado de leads.
    """
    
    @task(task_id="collect_training_data")
    def collect_training_data() -> Dict[str, Any]:
        """Recolecta datos históricos para entrenamiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        retrain = bool(params["retrain_model"])
        
        if not retrain:
            return {"training_data": None, "skip": True}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener leads históricos con outcomes
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.email,
                        p.first_name,
                        p.last_name,
                        p.company,
                        p.score as initial_score,
                        p.priority,
                        p.source,
                        p.utm_source,
                        p.utm_campaign,
                        p.stage,
                        p.estimated_value,
                        p.probability_pct,
                        p.qualified_at,
                        p.first_contact_at,
                        p.last_contact_at,
                        CASE 
                            WHEN p.stage = 'closed_won' THEN 1
                            ELSE 0
                        END as converted,
                        EXTRACT(EPOCH FROM (COALESCE(p.first_contact_at, p.qualified_at) - p.qualified_at))/86400 as days_to_contact,
                        p.metadata
                    FROM sales_pipeline p
                    WHERE p.qualified_at >= NOW() - INTERVAL '90 days'
                    ORDER BY p.qualified_at DESC
                    LIMIT 5000
                """)
                
                columns = [desc[0] for desc in cur.description]
                training_data = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Recolectados {len(training_data)} registros para entrenamiento")
        return {"training_data": training_data, "skip": False}
    
    @task(task_id="train_ml_model")
    def train_ml_model(training_data_result: Dict[str, Any]) -> Dict[str, Any]:
        """Entrena modelo ML."""
        if training_data_result.get("skip"):
            return {"model_trained": False, "skip": True}
        
        try:
            import numpy as np
            import pandas as pd
            from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import LabelEncoder
            from sklearn.metrics import accuracy_score, precision_score, recall_score
            ML_AVAILABLE = True
        except ImportError:
            logger.warning("Scikit-learn no disponible, usando scoring básico")
            ML_AVAILABLE = False
            return {"model_trained": False, "skip": True}
        
        if not ML_AVAILABLE:
            return {"model_trained": False, "skip": True}
        
        training_data = training_data_result.get("training_data", [])
        if not training_data:
            return {"model_trained": False, "skip": True}
        
        # Preparar datos
        df = pd.DataFrame(training_data)
        
        # Features
        feature_columns = [
            'initial_score', 'estimated_value', 'probability_pct',
            'days_to_contact'
        ]
        
        # Codificar variables categóricas
        le_priority = LabelEncoder()
        le_source = LabelEncoder()
        le_stage = LabelEncoder()
        
        df['priority_encoded'] = le_priority.fit_transform(df['priority'].fillna('low'))
        df['source_encoded'] = le_source.fit_transform(df['source'].fillna('unknown'))
        df['stage_encoded'] = le_stage.fit_transform(df['stage'].fillna('qualified'))
        
        feature_columns.extend(['priority_encoded', 'source_encoded', 'stage_encoded'])
        
        # Target
        y = df['converted'].values
        
        # Features
        X = df[feature_columns].fillna(0).values
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        ctx = get_current_context()
        model_type = ctx["params"]["ml_model_type"]
        
        if model_type == "gradient_boosting":
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        elif model_type == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
        model.fit(X_train, y_train)
        
        # Evaluar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        
        logger.info(f"Modelo entrenado - Accuracy: {accuracy:.2f}, Precision: {precision:.2f}, Recall: {recall:.2f}")
        
        # Guardar modelo (en producción usar MLflow o similar)
        import pickle
        import os
        model_dir = "/tmp/ml_models"
        os.makedirs(model_dir, exist_ok=True)
        model_path = f"{model_dir}/lead_scoring_model.pkl"
        
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'feature_columns': feature_columns,
                'label_encoders': {
                    'priority': le_priority,
                    'source': le_source,
                    'stage': le_stage
                },
                'accuracy': accuracy,
                'trained_at': datetime.utcnow().isoformat()
            }, f)
        
        return {
            "model_trained": True,
            "model_path": model_path,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "skip": False
        }
    
    @task(task_id="predict_lead_scores")
    def predict_lead_scores(model_result: Dict[str, Any]) -> Dict[str, Any]:
        """Predice scores usando modelo ML."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        dry_run = bool(params["dry_run"])
        
        if model_result.get("skip"):
            logger.info("Saltando predicción - modelo no disponible")
            return {"predicted": 0, "errors": 0}
        
        try:
            import pickle
            import numpy as np
            import pandas as pd
            ML_AVAILABLE = True
        except ImportError:
            logger.warning("Librerías ML no disponibles")
            return {"predicted": 0, "errors": 0}
        
        # Cargar modelo
        model_path = model_result.get("model_path")
        if not model_path:
            return {"predicted": 0, "errors": 0}
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            model = model_data['model']
            feature_columns = model_data['feature_columns']
            label_encoders = model_data['label_encoders']
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return {"predicted": 0, "errors": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener leads para predecir
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.id,
                        p.lead_ext_id,
                        p.score as initial_score,
                        p.priority,
                        p.source,
                        p.stage,
                        p.estimated_value,
                        p.probability_pct,
                        EXTRACT(EPOCH FROM (COALESCE(p.first_contact_at, NOW()) - p.qualified_at))/86400 as days_to_contact
                    FROM sales_pipeline p
                    WHERE p.stage NOT IN ('closed_won', 'closed_lost')
                        AND (p.metadata->>'ml_score') IS NULL
                    ORDER BY p.priority DESC, p.score DESC
                    LIMIT %s
                """, (max_leads,))
                
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        stats = {"predicted": 0, "errors": 0}
        
        for lead in leads:
            try:
                # Preparar features
                features = []
                
                # Numéricas
                features.append(lead.get('initial_score', 0))
                features.append(float(lead.get('estimated_value', 0)) or 0)
                features.append(lead.get('probability_pct', 0))
                features.append(float(lead.get('days_to_contact', 0)) or 0)
                
                # Categóricas
                priority = lead.get('priority', 'low')
                source = lead.get('source', 'unknown')
                stage = lead.get('stage', 'qualified')
                
                features.append(label_encoders['priority'].transform([priority])[0])
                features.append(label_encoders['source'].transform([source])[0])
                features.append(label_encoders['stage'].transform([stage])[0])
                
                # Predecir
                X = np.array([features])
                conversion_probability = model.predict_proba(X)[0][1]  # Probabilidad de conversión
                ml_score = int(conversion_probability * 100)
                
                # Actualizar lead
                if not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            existing_metadata = {}
                            cur.execute("""
                                SELECT metadata FROM sales_pipeline WHERE id = %s
                            """, (lead['id'],))
                            result = cur.fetchone()
                            if result and result[0]:
                                existing_metadata = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                            
                            updated_metadata = {
                                **existing_metadata,
                                "ml_score": ml_score,
                                "ml_conversion_probability": float(conversion_probability),
                                "ml_scored_at": datetime.utcnow().isoformat()
                            }
                            
                            # Actualizar score si ML score es mayor
                            new_score = max(lead.get('initial_score', 0), ml_score)
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    score = %s,
                                    metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (new_score, json.dumps(updated_metadata), lead['id']))
                            
                            conn.commit()
                            stats["predicted"] += 1
                            logger.info(f"Lead {lead['lead_ext_id']} - ML Score: {ml_score}, Prob: {conversion_probability:.2%}")
                else:
                    logger.info(f"[DRY RUN] Lead {lead['lead_ext_id']} - ML Score: {ml_score}")
                    stats["predicted"] += 1
            
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error prediciendo lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Predicción completada: {stats}")
        return stats
    
    # Pipeline
    training_data = collect_training_data()
    model_result = train_ml_model(training_data)
    prediction_stats = predict_lead_scores(model_result)


dag = lead_ml_scoring()

