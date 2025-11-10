"""
Módulo de Machine Learning para Predicción de Fallos de Backups.

Proporciona:
- Predicción de fallos de backups
- Detección de anomalías
- Predicción de necesidades de espacio
- Análisis predictivo de tendencias
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Intentar importar bibliotecas de ML
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    pd = None

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    RandomForestClassifier = None
    StandardScaler = None


@dataclass
class FailurePrediction:
    """Predicción de fallo."""
    backup_id: str
    failure_probability: float
    risk_factors: List[str]
    recommended_actions: List[str]
    confidence: float


@dataclass
class AnomalyDetection:
    """Detección de anomalía."""
    metric_name: str
    value: float
    expected_value: float
    anomaly_score: float
    is_anomaly: bool
    severity: str


class BackupMLPredictor:
    """Predictor ML para backups."""
    
    def __init__(self, model_dir: str = "/tmp/backup-ml-models"):
        """
        Inicializa predictor ML.
        
        Args:
            model_dir: Directorio para almacenar modelos
        """
        self.model_dir = model_dir
        self.failure_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
    
    def train_failure_prediction_model(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Entrena modelo para predecir fallos.
        
        Args:
            historical_data: Datos históricos de backups
        
        Returns:
            True si el entrenamiento fue exitoso
        """
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("ML libraries not available")
            return False
        
        try:
            # Preparar datos
            df = pd.DataFrame(historical_data)
            
            # Features para predicción
            features = [
                'duration_seconds',
                'size_bytes',
                'hour_of_day',
                'day_of_week',
                'previous_success_rate'
            ]
            
            # Target: 1 si falló, 0 si no
            df['failed'] = (df['status'] == 'failed').astype(int)
            
            # Preparar features
            X = df[features].fillna(0)
            y = df['failed']
            
            # Entrenar modelo
            self.failure_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.failure_model.fit(X, y)
            
            logger.info("Failure prediction model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train model: {e}", exc_info=True)
            return False
    
    def predict_backup_failure(
        self,
        backup_config: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> FailurePrediction:
        """
        Predice probabilidad de fallo de un backup.
        
        Args:
            backup_config: Configuración del backup
            historical_context: Contexto histórico
        
        Returns:
            Predicción de fallo
        """
        if not self.failure_model:
            # Modelo simple basado en reglas si ML no está disponible
            return self._rule_based_prediction(backup_config, historical_context)
        
        try:
            # Preparar features
            features = np.array([[
                backup_config.get('estimated_duration', 300),
                backup_config.get('estimated_size', 1024*1024*100),
                datetime.now().hour,
                datetime.now().weekday(),
                historical_context.get('success_rate', 0.95)
            ]])
            
            # Predecir
            failure_prob = self.failure_model.predict_proba(features)[0][1]
            
            # Identificar factores de riesgo
            risk_factors = self._identify_risk_factors(backup_config, historical_context)
            
            # Recomendaciones
            recommendations = self._generate_recommendations(failure_prob, risk_factors)
            
            return FailurePrediction(
                backup_id=backup_config.get('backup_id', 'unknown'),
                failure_probability=failure_prob,
                risk_factors=risk_factors,
                recommended_actions=recommendations,
                confidence=0.8 if failure_prob > 0.5 else 0.9
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._rule_based_prediction(backup_config, historical_context)
    
    def _rule_based_prediction(
        self,
        backup_config: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> FailurePrediction:
        """Predicción basada en reglas (fallback)."""
        risk_factors = []
        failure_prob = 0.0
        
        # Analizar factores de riesgo
        if historical_context.get('success_rate', 1.0) < 0.9:
            risk_factors.append("Low historical success rate")
            failure_prob += 0.2
        
        if backup_config.get('estimated_size', 0) > 10 * 1024 * 1024 * 1024:  # > 10GB
            risk_factors.append("Large backup size")
            failure_prob += 0.1
        
        current_hour = datetime.now().hour
        if current_hour >= 8 and current_hour <= 18:
            risk_factors.append("Backup during business hours")
            failure_prob += 0.05
        
        recommendations = []
        if failure_prob > 0.3:
            recommendations.append("Consider scheduling during off-peak hours")
        if backup_config.get('estimated_size', 0) > 5 * 1024 * 1024 * 1024:
            recommendations.append("Consider incremental backup for large datasets")
        
        return FailurePrediction(
            backup_id=backup_config.get('backup_id', 'unknown'),
            failure_probability=min(failure_prob, 0.95),
            risk_factors=risk_factors,
            recommended_actions=recommendations,
            confidence=0.7
        )
    
    def detect_anomalies(
        self,
        metrics: Dict[str, float],
        historical_baseline: Dict[str, Tuple[float, float]]  # mean, std
    ) -> List[AnomalyDetection]:
        """
        Detecta anomalías en métricas.
        
        Args:
            metrics: Métricas actuales
            historical_baseline: Baseline histórico (mean, std)
        
        Returns:
            Lista de anomalías detectadas
        """
        anomalies = []
        
        for metric_name, value in metrics.items():
            if metric_name not in historical_baseline:
                continue
            
            mean, std = historical_baseline[metric_name]
            
            if std == 0:
                continue
            
            # Calcular z-score
            z_score = abs((value - mean) / std)
            
            # Detectar anomalía (z-score > 2)
            is_anomaly = z_score > 2.0
            
            severity = "critical" if z_score > 3 else ("high" if z_score > 2.5 else "medium")
            
            anomalies.append(AnomalyDetection(
                metric_name=metric_name,
                value=value,
                expected_value=mean,
                anomaly_score=z_score,
                is_anomaly=is_anomaly,
                severity=severity
            ))
        
        return anomalies
    
    def _identify_risk_factors(
        self,
        backup_config: Dict[str, Any],
        historical_context: Dict[str, Any]
    ) -> List[str]:
        """Identifica factores de riesgo."""
        factors = []
        
        if historical_context.get('recent_failures', 0) > 2:
            factors.append("Multiple recent failures")
        
        if backup_config.get('estimated_duration', 0) > 3600:
            factors.append("Long estimated duration")
        
        if backup_config.get('database_size_gb', 0) > 100:
            factors.append("Very large database")
        
        return factors
    
    def _generate_recommendations(
        self,
        failure_prob: float,
        risk_factors: List[str]
    ) -> List[str]:
        """Genera recomendaciones basadas en predicción."""
        recommendations = []
        
        if failure_prob > 0.5:
            recommendations.append("High failure risk - consider manual backup")
        
        if "Multiple recent failures" in risk_factors:
            recommendations.append("Investigate root cause of recent failures")
        
        if "Very large database" in risk_factors:
            recommendations.append("Consider splitting into smaller backups")
        
        if not recommendations:
            recommendations.append("Backup appears low-risk")
        
        return recommendations
    
    def predict_space_needs_ml(
        self,
        historical_sizes: List[float],
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Predice necesidades de espacio usando ML.
        
        Args:
            historical_sizes: Tamaños históricos de backups
            days_ahead: Días a predecir
        
        Returns:
            Predicción con intervalos de confianza
        """
        if not NUMPY_AVAILABLE or len(historical_sizes) < 7:
            # Fallback simple
            avg_size = sum(historical_sizes) / len(historical_sizes) if historical_sizes else 0
            return {
                'predicted_size_gb': avg_size * days_ahead,
                'confidence': 'low',
                'method': 'simple_average'
            }
        
        try:
            # Calcular tendencia
            sizes = np.array(historical_sizes)
            
            # Regresión lineal simple
            x = np.arange(len(sizes))
            coeffs = np.polyfit(x, sizes, 1)
            
            # Predecir
            future_x = len(sizes) + days_ahead
            predicted_size = np.polyval(coeffs, future_x)
            
            # Calcular intervalo de confianza
            residuals = sizes - np.polyval(coeffs, x)
            std_error = np.std(residuals)
            confidence_interval = 1.96 * std_error  # 95% CI
            
            return {
                'predicted_size_gb': predicted_size,
                'confidence_lower': predicted_size - confidence_interval,
                'confidence_upper': predicted_size + confidence_interval,
                'confidence': 'high' if len(historical_sizes) >= 30 else 'medium',
                'method': 'linear_regression',
                'trend': 'increasing' if coeffs[0] > 0 else 'decreasing'
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            avg_size = sum(historical_sizes) / len(historical_sizes)
            return {
                'predicted_size_gb': avg_size * days_ahead,
                'confidence': 'low',
                'method': 'fallback'
            }

