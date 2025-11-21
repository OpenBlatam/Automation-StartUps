"""
MLflow Training DAG - Entrenamiento automatizado de modelos con MLflow

Pipeline completo de ML que incluye:
- Carga de datos desde DB/S3
- Preprocesamiento y feature engineering
- Entrenamiento con tracking en MLflow
- Evaluación y métricas
- Registro automático de modelos
- Promoción a producción si cumple criterios

Uso:
    - Ejecutar manualmente con parámetros
    - O configurar schedule para re-entrenamiento periódico
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.utils.context import get_current_context
import pendulum

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    from mlflow.sklearn import log_model as sklearn_log_model
    import mlflow.sklearn
    _MLFLOW_AVAILABLE = True
except ImportError:
    _MLFLOW_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    from sklearn.preprocessing import StandardScaler
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

from data.airflow.plugins.db import get_conn
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


def _get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    value = os.getenv(key) or Variable.get(key, default_var=default or "")
    if required and not value:
        raise AirflowFailException(f"Required variable {key} not set")
    return value


@dag(
    dag_id="mlflow_train",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger o configurar schedule
    catchup=False,
    default_args={
        "owner": "ml-team",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### MLflow Training Pipeline
    
    Pipeline automatizado completo para entrenamiento de modelos ML con tracking en MLflow.
    
    **Funcionalidades:**
    - Carga de datos desde PostgreSQL o S3
    - Preprocesamiento y feature engineering
    - Entrenamiento con múltiples algoritmos
    - Tracking completo en MLflow (parámetros, métricas, artefactos)
    - Evaluación con cross-validation
    - Registro automático de modelos
    - Promoción a producción si cumple criterios
    
    **Parámetros:**
    - `model_type`: Tipo de modelo (random_forest | gradient_boosting | custom)
    - `experiment_name`: Nombre del experimento en MLflow
    - `data_source`: Origen de datos (db | s3 | synthetic)
    - `table_name`: Nombre de tabla en DB (si data_source=db)
    - `target_column`: Columna objetivo para predicción
    - `min_accuracy_threshold`: Accuracy mínimo para registrar modelo (default: 0.7)
    - `register_model`: Registrar modelo en registry (default: true)
    - `promote_to_production`: Promover automáticamente a producción (default: false)
    - `dry_run`: Solo simular sin entrenar (default: false)
    
    **Requisitos:**
    - MLflow server configurado y accesible
    - Variables de Airflow: MLFLOW_TRACKING_URI
    - PostgreSQL accesible (si usa data_source=db)
    - S3 accesible (si usa data_source=s3)
    """,
    params={
        "model_type": "random_forest",  # random_forest | gradient_boosting
        "experiment_name": "mlflow-training",
        "data_source": "synthetic",  # db | s3 | synthetic
        "table_name": "",
        "target_column": "target",
        "min_accuracy_threshold": 0.7,
        "register_model": True,
        "promote_to_production": False,
        "dry_run": False,
        "max_runs": 1,  # Máximo de runs del experimento a considerar
    },
    tags=["ml", "mlflow", "training", "model-registry"],
)
def mlflow_train() -> None:
    """
    DAG principal de entrenamiento con MLflow.
    """
    
    @task(task_id="load_data")
    def load_data(**kwargs) -> Dict[str, Any]:
        """Carga datos desde la fuente especificada."""
        ctx = get_current_context()
        params = ctx["params"]
        data_source = str(params.get("data_source", "synthetic"))
        
        logger.info(f"Loading data from source: {data_source}")
        
        if data_source == "synthetic":
            # Generar datos sintéticos para ejemplo
            logger.info("Generating synthetic data")
            np.random.seed(42)
            n_samples = 1000
            n_features = 10
            
            X = np.random.randn(n_samples, n_features)
            y = (X.sum(axis=1) > 0).astype(int)
            
            df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
            df["target"] = y
            
            logger.info(f"Generated {len(df)} samples with {n_features} features")
            
            return {
                "data": df.to_dict("records"),
                "target_column": "target",
                "n_samples": len(df),
                "n_features": n_features,
            }
        
        elif data_source == "db":
            table_name = str(params.get("table_name", ""))
            if not table_name:
                raise AirflowFailException("table_name required when data_source=db")
            
            logger.info(f"Loading data from table: {table_name}")
            
            with get_conn() as conn:
                query = f"SELECT * FROM {table_name} LIMIT 10000"
                df = pd.read_sql(query, conn)
            
            target_column = str(params.get("target_column", "target"))
            if target_column not in df.columns:
                raise AirflowFailException(f"Target column '{target_column}' not found in data")
            
            logger.info(f"Loaded {len(df)} samples from {table_name}")
            
            return {
                "data": df.to_dict("records"),
                "target_column": target_column,
                "n_samples": len(df),
                "n_features": len(df.columns) - 1,
            }
        
        elif data_source == "s3":
            # TODO: Implementar carga desde S3
            raise AirflowFailException("S3 data source not yet implemented")
        
        else:
            raise AirflowFailException(f"Unknown data_source: {data_source}")
    
    @task(task_id="preprocess_data")
    def preprocess_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocesa datos para entrenamiento."""
        logger.info("Preprocessing data")
        
        df = pd.DataFrame(data["data"])
        target_column = data["target_column"]
        
        # Separar features y target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Normalización (opcional, según modelo)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(
            f"Preprocessed data: train={len(X_train)}, test={len(X_test)}",
            extra={"train_size": len(X_train), "test_size": len(X_test)},
        )
        
        return {
            **data,
            "X_train": X_train.tolist(),
            "X_test": X_test.tolist(),
            "y_train": y_train.tolist(),
            "y_test": y_test.tolist(),
            "feature_names": list(X.columns),
        }
    
    @task(task_id="train_model")
    def train_model(preprocessed: Dict[str, Any]) -> Dict[str, Any]:
        """Entrena modelo y registra en MLflow."""
        if not _MLFLOW_AVAILABLE:
            raise AirflowFailException("MLflow not available. Install: pip install mlflow")
        
        if not _SKLEARN_AVAILABLE:
            raise AirflowFailException("scikit-learn not available")
        
        ctx = get_current_context()
        params = ctx["params"]
        
        tracking_uri = _get_env_var("MLFLOW_TRACKING_URI", "http://mlflow.ml.svc.cluster.local")
        experiment_name = str(params.get("experiment_name", "mlflow-training"))
        model_type = str(params.get("model_type", "random_forest"))
        dry_run = bool(params.get("dry_run", False))
        
        logger.info(
            f"Training model",
            extra={
                "tracking_uri": tracking_uri,
                "experiment": experiment_name,
                "model_type": model_type,
                "dry_run": dry_run,
            },
        )
        
        if dry_run:
            logger.info("DRY RUN: Skipping actual training")
            return {
                **preprocessed,
                "run_id": "dry-run",
                "accuracy": 0.95,
                "model_uri": "dry-run",
            }
        
        # Configurar MLflow
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        
        # Preparar datos
        X_train = np.array(preprocessed["X_train"])
        X_test = np.array(preprocessed["X_test"])
        y_train = np.array(preprocessed["y_train"])
        y_test = np.array(preprocessed["y_test"])
        
        # Configurar modelo
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
            )
            hyperparams = {"n_estimators": 100, "max_depth": 10}
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
            )
            hyperparams = {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5}
        else:
            raise AirflowFailException(f"Unknown model_type: {model_type}")
        
        # Iniciar run de MLflow
        run_name = f"{model_type}_{ctx['dag_run'].run_id}"
        
        with mlflow.start_run(run_name=run_name):
            # Log parámetros
            mlflow.log_params(hyperparams)
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("train_size", len(X_train))
            mlflow.log_param("test_size", len(X_test))
            mlflow.log_param("dag_run_id", ctx["dag_run"].run_id)
            
            # Entrenar modelo
            logger.info("Training model...")
            model.fit(X_train, y_train)
            
            # Predicciones
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            y_test_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
            
            # Calcular métricas
            train_accuracy = accuracy_score(y_train, y_train_pred)
            test_accuracy = accuracy_score(y_test, y_test_pred)
            precision = precision_score(y_test, y_test_pred, average="weighted")
            recall = recall_score(y_test, y_test_pred, average="weighted")
            f1 = f1_score(y_test, y_test_pred, average="weighted")
            
            metrics = {
                "train_accuracy": train_accuracy,
                "test_accuracy": test_accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }
            
            if y_test_proba is not None:
                try:
                    auc = roc_auc_score(y_test, y_test_proba)
                    metrics["roc_auc"] = auc
                except Exception as e:
                    logger.warning(f"Could not calculate AUC: {e}")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
            metrics["cv_accuracy_mean"] = cv_scores.mean()
            metrics["cv_accuracy_std"] = cv_scores.std()
            
            # Log métricas
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            
            # Log modelo
            sklearn_log_model(model, "model")
            
            # Tags
            mlflow.set_tag("dag_id", "mlflow_train")
            mlflow.set_tag("model_type", model_type)
            mlflow.set_tag("environment", os.getenv("ENV", "dev"))
            
            run_id = mlflow.active_run().info.run_id
            model_uri = f"runs:/{run_id}/model"
            
            logger.info(
                f"Model trained successfully",
                extra={
                    "run_id": run_id,
                    "test_accuracy": test_accuracy,
                    "metrics": metrics,
                },
            )
            
            return {
                **preprocessed,
                "run_id": run_id,
                "model_uri": model_uri,
                "metrics": metrics,
                "accuracy": test_accuracy,
            }
    
    @task(task_id="register_model")
    def register_model(training_result: Dict[str, Any]) -> Dict[str, Any]:
        """Registra modelo en MLflow Model Registry."""
        ctx = get_current_context()
        params = ctx["params"]
        
        register = bool(params.get("register_model", True))
        min_accuracy = float(params.get("min_accuracy_threshold", 0.7))
        accuracy = float(training_result.get("accuracy", 0.0))
        
        if not register:
            logger.info("Model registration skipped (register_model=false)")
            return {**training_result, "registered": False}
        
        if accuracy < min_accuracy:
            raise AirflowFailException(
                f"Model accuracy {accuracy:.3f} below threshold {min_accuracy:.3f}"
            )
        
        tracking_uri = _get_env_var("MLFLOW_TRACKING_URI", "http://mlflow.ml.svc.cluster.local")
        mlflow.set_tracking_uri(tracking_uri)
        
        model_uri = training_result["model_uri"]
        run_id = training_result["run_id"]
        
        # Nombre del modelo (configurable)
        model_name = f"mlflow-{ctx['params'].get('experiment_name', 'training')}"
        
        try:
            client = MlflowClient(tracking_uri=tracking_uri)
            
            # Registrar modelo
            registered_model = mlflow.register_model(model_uri, model_name)
            
            logger.info(
                f"Model registered successfully",
                extra={
                    "model_name": model_name,
                    "version": registered_model.version,
                    "run_id": run_id,
                },
            )
            
            # Promover a producción si se solicita
            promote = bool(params.get("promote_to_production", False))
            if promote:
                client.transition_model_version_stage(
                    name=model_name,
                    version=registered_model.version,
                    stage="Production",
                )
                logger.info(f"Model {model_name} v{registered_model.version} promoted to Production")
            
            return {
                **training_result,
                "registered": True,
                "model_name": model_name,
                "version": registered_model.version,
                "stage": "Production" if promote else "None",
            }
        
        except Exception as e:
            logger.error(f"Error registering model: {e}")
            raise AirflowFailException(f"Failed to register model: {e}")
    
    @task(task_id="notify_results")
    def notify_results(registration_result: Dict[str, Any]) -> None:
        """Envía notificación con resultados del entrenamiento."""
        ctx = get_current_context()
        
        registered = registration_result.get("registered", False)
        accuracy = registration_result.get("accuracy", 0.0)
        model_name = registration_result.get("model_name", "unknown")
        version = registration_result.get("version", "unknown")
        
        if registered:
            message = (
                f"✅ Modelo entrenado exitosamente\n"
                f"Modelo: {model_name} v{version}\n"
                f"Accuracy: {accuracy:.3f}\n"
                f"Run ID: {registration_result.get('run_id', 'unknown')}"
            )
        else:
            message = (
                f"⚠️ Entrenamiento completado pero modelo no registrado\n"
                f"Accuracy: {accuracy:.3f}\n"
                f"Run ID: {registration_result.get('run_id', 'unknown')}"
            )
        
        try:
            notify_slack(message, dag_id="mlflow_train")
        except Exception as e:
            logger.warning(f"Could not send Slack notification: {e}")
    
    # Pipeline
    data = load_data()
    preprocessed = preprocess_data(data)
    trained = train_model(preprocessed)
    registered = register_model(trained)
    notify_results(registered)
    
    return None


# Ejecutar DAG
mlflow_train()

