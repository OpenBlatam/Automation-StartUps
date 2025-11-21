"""
Sistema de Machine Learning para Scoring Predictivo de Leads

Predice la probabilidad de conversión de leads usando ML,
permitiendo priorizar y personalizar el nurturing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import pickle
import os

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("Librerías de ML no disponibles. Instala: pip install scikit-learn pandas numpy")


class PredictiveScoringModel:
    """
    Modelo de ML para scoring predictivo de leads.
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Inicializa el modelo de scoring.
        
        Args:
            model_type: Tipo de modelo ('random_forest' o 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.model_path = os.getenv("ML_MODEL_PATH", "/tmp/lead_scoring_model.pkl")
    
    def prepare_features(
        self,
        lead_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[float]:
        """
        Prepara features para el modelo.
        
        Args:
            lead_data: Datos del lead
            historical_data: Datos históricos opcionales
        
        Returns:
            Lista de features numéricas
        """
        features = []
        
        # Features básicas del lead
        features.append(1.0 if lead_data.get("lead_magnet_downloaded") else 0.0)
        features.append(len(lead_data.get("email", "")) / 50.0)  # Normalizado
        features.append(1.0 if lead_data.get("first_name") else 0.0)
        features.append(1.0 if lead_data.get("last_name") else 0.0)
        
        # Features de fuente
        source = lead_data.get("source", "organic")
        source_features = {
            "organic": [1.0, 0.0, 0.0, 0.0],
            "referral": [0.0, 1.0, 0.0, 0.0],
            "social": [0.0, 0.0, 1.0, 0.0],
            "paid": [0.0, 0.0, 0.0, 1.0]
        }
        features.extend(source_features.get(source, [0.0, 0.0, 0.0, 0.0]))
        
        # Features de interés
        interest = lead_data.get("interest_area", "general")
        interest_features = {
            "marketing": [1.0, 0.0, 0.0],
            "sales": [0.0, 1.0, 0.0],
            "general": [0.0, 0.0, 1.0]
        }
        features.extend(interest_features.get(interest, [0.0, 0.0, 1.0]))
        
        # Features de engagement inicial
        engagement_score = lead_data.get("engagement_score", 0)
        features.append(min(engagement_score / 10.0, 1.0))  # Normalizado
        
        # Features temporales
        created_at = lead_data.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            hour = created_at.hour
            day_of_week = created_at.weekday()
            features.append(hour / 24.0)
            features.append(day_of_week / 7.0)
        else:
            features.extend([0.5, 0.5])
        
        # Features históricas (si disponibles)
        if historical_data:
            avg_engagement = sum(d.get("engagement_score", 0) for d in historical_data) / len(historical_data) if historical_data else 0
            conversion_rate = sum(1 for d in historical_data if d.get("status") == "engaged") / len(historical_data) if historical_data else 0
            features.append(min(avg_engagement / 10.0, 1.0))
            features.append(conversion_rate)
        else:
            features.extend([0.0, 0.0])
        
        return features
    
    def train(
        self,
        training_data: List[Dict[str, Any]],
        target_column: str = "converted"
    ) -> Dict[str, Any]:
        """
        Entrena el modelo con datos históricos.
        
        Args:
            training_data: Lista de dicts con datos de entrenamiento
            target_column: Columna objetivo ('converted', 'engaged', etc.)
        
        Returns:
            Dict con métricas de entrenamiento
        """
        if not ML_AVAILABLE:
            return {"error": "Librerías de ML no disponibles"}
        
        try:
            # Preparar datos
            X = []
            y = []
            
            for record in training_data:
                features = self.prepare_features(record)
                X.append(features)
                y.append(1 if record.get(target_column, False) else 0)
            
            if len(X) < 50:
                return {"error": "Datos insuficientes para entrenar (mínimo 50)"}
            
            X = np.array(X)
            y = np.array(y)
            
            # Dividir en train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Crear y entrenar modelo
            if self.model_type == "random_forest":
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            else:
                self.model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluar
            y_pred = self.model.predict(X_test_scaled)
            
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
            self.is_trained = True
            
            # Guardar modelo
            self.save_model()
            
            logger.info(f"Modelo entrenado: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}", exc_info=True)
            return {"error": str(e)}
    
    def predict(
        self,
        lead_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Predice score de conversión para un lead.
        
        Args:
            lead_data: Datos del lead
            historical_data: Datos históricos opcionales
        
        Returns:
            Dict con predicción y score
        """
        if not self.is_trained:
            # Intentar cargar modelo guardado
            if not self.load_model():
                return {
                    "score": 0.5,
                    "probability": 0.5,
                    "prediction": False,
                    "warning": "Modelo no entrenado, usando score por defecto"
                }
        
        try:
            # Preparar features
            features = self.prepare_features(lead_data, historical_data)
            features_array = np.array([features])
            
            # Escalar
            features_scaled = self.scaler.transform(features_array)
            
            # Predecir
            probability = self.model.predict_proba(features_scaled)[0][1]
            prediction = self.model.predict(features_scaled)[0]
            
            # Score de 0-100
            score = int(probability * 100)
            
            return {
                "score": score,
                "probability": float(probability),
                "prediction": bool(prediction),
                "confidence": "high" if probability > 0.7 or probability < 0.3 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo: {e}")
            return {
                "score": 50,
                "probability": 0.5,
                "prediction": False,
                "error": str(e)
            }
    
    def save_model(self) -> bool:
        """Guarda el modelo entrenado."""
        try:
            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "model_type": self.model_type,
                "feature_names": self.feature_names,
                "trained_at": datetime.now().isoformat()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Modelo guardado en {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando modelo: {e}")
            return False
    
    def load_model(self) -> bool:
        """Carga un modelo guardado."""
        try:
            if not os.path.exists(self.model_path):
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.model_type = model_data.get("model_type", "random_forest")
            self.feature_names = model_data.get("feature_names", [])
            self.is_trained = True
            
            logger.info(f"Modelo cargado desde {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False


class LeadScoringService:
    """
    Servicio de scoring de leads que integra con el sistema.
    """
    
    def __init__(self, db_hook=None):
        """
        Inicializa el servicio de scoring.
        
        Args:
            db_hook: Hook de base de datos
        """
        self.db_hook = db_hook
        self.model = PredictiveScoringModel()
        self.model.load_model()  # Intentar cargar modelo existente
    
    def score_lead(
        self,
        lead_id: str
    ) -> Dict[str, Any]:
        """
        Calcula score predictivo para un lead.
        
        Args:
            lead_id: ID del lead
        
        Returns:
            Dict con score y predicción
        """
        if not self.db_hook:
            return {"error": "No hay conexión a base de datos"}
        
        try:
            # Obtener datos del lead
            lead_data = self.db_hook.get_first(
                """
                SELECT 
                    lead_id, email, first_name, last_name,
                    source, interest_area, lead_magnet_downloaded,
                    engagement_score, status, created_at
                FROM organic_leads
                WHERE lead_id = %s
                """,
                parameters=(lead_id,)
            )
            
            if not lead_data:
                return {"error": "Lead no encontrado"}
            
            # Convertir a dict
            lead_dict = {
                "lead_id": lead_data[0],
                "email": lead_data[1],
                "first_name": lead_data[2],
                "last_name": lead_data[3],
                "source": lead_data[4],
                "interest_area": lead_data[5],
                "lead_magnet_downloaded": lead_data[6],
                "engagement_score": lead_data[7] or 0,
                "status": lead_data[8],
                "created_at": lead_data[9]
            }
            
            # Obtener datos históricos similares
            historical = self._get_similar_leads(lead_dict)
            
            # Predecir
            prediction = self.model.predict(lead_dict, historical)
            
            # Actualizar score en BD
            self.db_hook.run(
                """
                UPDATE organic_leads
                SET 
                    ml_score = %s,
                    ml_score_updated_at = NOW(),
                    updated_at = NOW()
                WHERE lead_id = %s
                """,
                parameters=(prediction["score"], lead_id)
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error calculando score: {e}")
            return {"error": str(e)}
    
    def _get_similar_leads(
        self,
        lead_data: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene leads similares para contexto histórico."""
        if not self.db_hook:
            return []
        
        try:
            query = """
                SELECT 
                    source, interest_area, engagement_score, status
                FROM organic_leads
                WHERE source = %s
                AND interest_area = %s
                AND created_at < NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            results = self.db_hook.get_records(
                query,
                parameters=(
                    lead_data.get("source"),
                    lead_data.get("interest_area"),
                    limit
                )
            )
            
            return [
                {
                    "source": r[0],
                    "interest_area": r[1],
                    "engagement_score": r[2] or 0,
                    "converted": r[3] == "engaged"
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo leads similares: {e}")
            return []
    
    def retrain_model(
        self,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Reentrena el modelo con datos recientes.
        
        Args:
            days_back: Días hacia atrás para datos de entrenamiento
        
        Returns:
            Dict con métricas de entrenamiento
        """
        if not self.db_hook:
            return {"error": "No hay conexión a base de datos"}
        
        try:
            # Obtener datos históricos
            query = """
                SELECT 
                    lead_id, email, first_name, last_name,
                    source, interest_area, lead_magnet_downloaded,
                    engagement_score, status, created_at
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '%s days'
                AND status IN ('engaged', 'converted', 'inactive')
            """
            
            results = self.db_hook.get_records(query, parameters=(days_back,))
            
            training_data = [
                {
                    "lead_id": r[0],
                    "email": r[1],
                    "first_name": r[2],
                    "last_name": r[3],
                    "source": r[4],
                    "interest_area": r[5],
                    "lead_magnet_downloaded": r[6],
                    "engagement_score": r[7] or 0,
                    "converted": r[8] == "engaged",
                    "created_at": r[9]
                }
                for r in results
            ]
            
            if len(training_data) < 50:
                return {
                    "error": f"Datos insuficientes: {len(training_data)} (mínimo 50)"
                }
            
            # Entrenar
            metrics = self.model.train(training_data, target_column="converted")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error reentrenando modelo: {e}")
            return {"error": str(e)}


# Schema SQL adicional para ML scoring
ML_SCORING_SCHEMA = """
-- Agregar columna de ML score a organic_leads
ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS ml_score INTEGER CHECK (ml_score BETWEEN 0 AND 100);

ALTER TABLE organic_leads 
ADD COLUMN IF NOT EXISTS ml_score_updated_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_organic_leads_ml_score ON organic_leads(ml_score DESC);
"""

