#!/usr/bin/env python3
"""
Predictor ML Básico para Mejorar Predicciones de Engagement
Usa datos históricos para mejorar predicciones con el tiempo
"""

import json
import logging
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class MLPredictor:
    """Predictor básico de ML para mejorar predicciones"""
    
    def __init__(self, training_data_file: Optional[str] = None):
        """
        Inicializa el predictor ML
        
        Args:
            training_data_file: Archivo con datos de entrenamiento
        """
        self.training_data = []
        self.model_weights = {}
        self._load_training_data(training_data_file)
        self._train_model()
    
    def _load_training_data(self, file_path: Optional[str]):
        """Carga datos de entrenamiento"""
        if not file_path:
            return
        
        try:
            data_path = Path(file_path)
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.training_data = json.load(f)
                logger.info(f"Datos de entrenamiento cargados: {len(self.training_data)} registros")
        except Exception as e:
            logger.warning(f"Error al cargar datos de entrenamiento: {e}")
    
    def _train_model(self):
        """Entrena un modelo básico con los datos disponibles"""
        if not self.training_data or len(self.training_data) < 10:
            # Usar pesos por defecto si no hay suficientes datos
            self.model_weights = {
                'length': 0.15,
                'hashtags': 0.20,
                'has_numbers': 0.15,
                'has_emojis': 0.10,
                'has_cta': 0.15,
                'has_storytelling': 0.15,
                'platform_factor': 0.10
            }
            return
        
        # Análisis básico de correlaciones
        # Calcular promedios de engagement por factor
        factor_engagement = defaultdict(list)
        
        for record in self.training_data:
            actual_rate = record.get('actual_engagement_rate', 0)
            predicted_rate = record.get('predicted_engagement_rate', 0)
            
            # Normalizar factores (asumir estructura similar)
            if actual_rate > 0:
                factor_engagement['overall'].append(actual_rate)
        
        # Calcular pesos basados en variabilidad
        if factor_engagement.get('overall'):
            avg_engagement = statistics.mean(factor_engagement['overall'])
            std_engagement = statistics.stdev(factor_engagement['overall']) if len(factor_engagement['overall']) > 1 else 0
            
            # Ajustar pesos basados en precisión de predicciones
            prediction_errors = []
            for record in self.training_data:
                pred = record.get('predicted_engagement_rate', 0)
                actual = record.get('actual_engagement_rate', 0)
                if pred > 0 and actual > 0:
                    error = abs((actual - pred) / pred)
                    prediction_errors.append(error)
            
            avg_error = statistics.mean(prediction_errors) if prediction_errors else 0.2
            
            # Ajustar pesos para reducir error
            adjustment_factor = 1.0 - min(0.3, avg_error)
            
            self.model_weights = {
                'length': 0.15 * adjustment_factor,
                'hashtags': 0.20 * adjustment_factor,
                'has_numbers': 0.15 * adjustment_factor,
                'has_emojis': 0.10 * adjustment_factor,
                'has_cta': 0.15 * adjustment_factor,
                'has_storytelling': 0.15 * adjustment_factor,
                'platform_factor': 0.10 * adjustment_factor
            }
        
        logger.debug(f"Modelo entrenado con {len(self.training_data)} registros")
    
    def improve_prediction(
        self,
        base_prediction: Dict[str, Any],
        factors: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Mejora una predicción usando el modelo ML
        
        Args:
            base_prediction: Predicción base del sistema
            factors: Factores de la publicación
            platform: Plataforma objetivo
        
        Returns:
            Predicción mejorada
        """
        if not self.training_data or len(self.training_data) < 5:
            # No hay suficientes datos para mejorar
            return base_prediction
        
        base_score = base_prediction.get('predicted_score', 50)
        base_rate = base_prediction.get('predicted_engagement_rate', 2.0)
        
        # Ajustar basado en factores y pesos del modelo
        adjustments = []
        
        # Factor de longitud
        length_factor = factors.get('length_factor', 1.0)
        length_adjustment = (length_factor - 1.0) * self.model_weights['length'] * 100
        adjustments.append(length_adjustment)
        
        # Factor de hashtags
        hashtag_factor = factors.get('hashtag_factor', 1.0)
        hashtag_adjustment = (hashtag_factor - 1.0) * self.model_weights['hashtags'] * 100
        adjustments.append(hashtag_adjustment)
        
        # Otros factores
        if factors.get('has_numbers'):
            adjustments.append(self.model_weights['has_numbers'] * 15)
        if factors.get('has_emojis'):
            adjustments.append(self.model_weights['has_emojis'] * 10)
        if factors.get('has_cta'):
            adjustments.append(self.model_weights['has_cta'] * 15)
        if factors.get('has_storytelling'):
            adjustments.append(self.model_weights['has_storytelling'] * 15)
        
        # Ajuste por plataforma basado en datos históricos
        platform_adjustment = self._get_platform_adjustment(platform)
        adjustments.append(platform_adjustment)
        
        # Aplicar ajustes
        total_adjustment = sum(adjustments)
        improved_score = base_score + total_adjustment
        improved_score = max(0, min(100, improved_score))
        
        # Ajustar engagement rate proporcionalmente
        score_ratio = improved_score / base_score if base_score > 0 else 1.0
        improved_rate = base_rate * score_ratio
        improved_rate = max(0, min(20, improved_rate))
        
        # Calcular nueva confianza (aumenta con más datos)
        confidence = base_prediction.get('confidence', 0.6)
        if len(self.training_data) >= 20:
            confidence = min(0.95, confidence + 0.1)
        elif len(self.training_data) >= 10:
            confidence = min(0.9, confidence + 0.05)
        
        return {
            'predicted_score': round(improved_score, 1),
            'predicted_engagement_rate': round(improved_rate, 2),
            'confidence': round(confidence, 2),
            'ml_improved': True,
            'improvement_amount': round(total_adjustment, 1),
            'base_score': base_score,
            'factors': factors
        }
    
    def _get_platform_adjustment(self, platform: str) -> float:
        """Obtiene ajuste específico por plataforma basado en datos históricos"""
        if not self.training_data:
            return 0.0
        
        # Filtrar datos por plataforma
        platform_data = [
            r for r in self.training_data
            if r.get('platform', '').lower() == platform.lower()
        ]
        
        if len(platform_data) < 3:
            return 0.0
        
        # Calcular promedio de engagement para esta plataforma
        platform_rates = [r.get('actual_engagement_rate', 0) for r in platform_data]
        avg_platform_rate = statistics.mean(platform_rates)
        
        # Calcular promedio general
        all_rates = [r.get('actual_engagement_rate', 0) for r in self.training_data]
        avg_general_rate = statistics.mean(all_rates)
        
        # Ajuste basado en diferencia
        if avg_general_rate > 0:
            adjustment = ((avg_platform_rate - avg_general_rate) / avg_general_rate) * 10
            return adjustment * self.model_weights['platform_factor']
        
        return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtiene información sobre el modelo"""
        return {
            'training_samples': len(self.training_data),
            'model_weights': self.model_weights,
            'is_trained': len(self.training_data) >= 10,
            'confidence_level': 'high' if len(self.training_data) >= 20 else 'medium' if len(self.training_data) >= 10 else 'low'
        }



