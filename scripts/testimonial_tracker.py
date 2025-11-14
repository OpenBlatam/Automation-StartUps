#!/usr/bin/env python3
"""
Sistema de Tracking Post-Publicación para Testimonios
Rastrea el rendimiento real de las publicaciones y mejora predicciones
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class PostPerformance:
    """Rendimiento real de una publicación"""
    post_id: str
    platform: str
    published_at: datetime
    predicted_engagement_rate: float
    actual_engagement_rate: float
    predicted_score: float
    actual_score: float
    accuracy: float  # Qué tan cerca estuvo la predicción
    likes: int
    comments: int
    shares: int
    impressions: int
    reach: int
    tracked_at: datetime


class PostTracker:
    """Sistema de tracking de publicaciones post-publicación"""
    
    def __init__(self, tracking_file: Optional[str] = None):
        """
        Inicializa el tracker
        
        Args:
            tracking_file: Archivo JSON para persistir datos de tracking
        """
        self.tracking_file = tracking_file or "data/testimonial_tracking.json"
        self.tracked_posts: Dict[str, PostPerformance] = {}
        self._load_tracking_data()
    
    def _load_tracking_data(self):
        """Carga datos de tracking desde archivo"""
        tracking_path = Path(self.tracking_file)
        if tracking_path.exists():
            try:
                with open(tracking_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for post_id, post_data in data.items():
                        # Convertir fecha de string a datetime
                        if 'published_at' in post_data:
                            post_data['published_at'] = datetime.fromisoformat(post_data['published_at'])
                        if 'tracked_at' in post_data:
                            post_data['tracked_at'] = datetime.fromisoformat(post_data['tracked_at'])
                        self.tracked_posts[post_id] = PostPerformance(**post_data)
                logger.info(f"Datos de tracking cargados: {len(self.tracked_posts)} publicaciones")
            except Exception as e:
                logger.warning(f"Error al cargar datos de tracking: {e}")
    
    def _save_tracking_data(self):
        """Guarda datos de tracking en archivo"""
        try:
            tracking_path = Path(self.tracking_file)
            tracking_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir dataclasses a dict para JSON
            data = {}
            for post_id, post_perf in self.tracked_posts.items():
                post_dict = asdict(post_perf)
                # Convertir datetime a string
                if isinstance(post_dict.get('published_at'), datetime):
                    post_dict['published_at'] = post_dict['published_at'].isoformat()
                if isinstance(post_dict.get('tracked_at'), datetime):
                    post_dict['tracked_at'] = post_dict['tracked_at'].isoformat()
                data[post_id] = post_dict
            
            with open(tracking_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error al guardar datos de tracking: {e}")
    
    def track_post(
        self,
        post_id: str,
        platform: str,
        predicted_data: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> PostPerformance:
        """
        Registra el rendimiento real de una publicación
        
        Args:
            post_id: ID único de la publicación
            platform: Plataforma donde se publicó
            predicted_data: Datos de predicción originales
            actual_data: Datos reales de engagement
        
        Returns:
            PostPerformance con datos de tracking
        """
        predicted_rate = predicted_data.get("predicted_engagement_rate", 0)
        predicted_score = predicted_data.get("predicted_score", 0)
        
        # Calcular engagement rate real
        likes = actual_data.get("likes", 0)
        comments = actual_data.get("comments", 0)
        shares = actual_data.get("shares", 0)
        impressions = actual_data.get("impressions", 0)
        
        if impressions > 0:
            actual_rate = ((likes + comments + shares) / impressions) * 100
        else:
            actual_rate = 0
        
        # Calcular score real (mismo método que predicción)
        actual_score = likes + (comments * 3) + (shares * 5)
        
        # Calcular precisión de la predicción
        if predicted_rate > 0:
            accuracy = 100 - abs((actual_rate - predicted_rate) / predicted_rate * 100)
            accuracy = max(0, min(100, accuracy))
        else:
            accuracy = 0
        
        performance = PostPerformance(
            post_id=post_id,
            platform=platform,
            published_at=datetime.now(),
            predicted_engagement_rate=predicted_rate,
            actual_engagement_rate=actual_rate,
            predicted_score=predicted_score,
            actual_score=actual_score,
            accuracy=round(accuracy, 2),
            likes=likes,
            comments=comments,
            shares=shares,
            impressions=impressions,
            reach=actual_data.get("reach", 0),
            tracked_at=datetime.now()
        )
        
        self.tracked_posts[post_id] = performance
        self._save_tracking_data()
        
        logger.info(f"Publicación {post_id} trackeada. Precisión: {accuracy:.1f}%")
        
        return performance
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tracking
        
        Returns:
            Dict con estadísticas agregadas
        """
        if not self.tracked_posts:
            return {"error": "No hay datos de tracking disponibles"}
        
        performances = list(self.tracked_posts.values())
        
        # Estadísticas generales
        avg_accuracy = sum(p.accuracy for p in performances) / len(performances)
        avg_predicted_rate = sum(p.predicted_engagement_rate for p in performances) / len(performances)
        avg_actual_rate = sum(p.actual_engagement_rate for p in performances) / len(performances)
        
        # Estadísticas por plataforma
        platform_stats = defaultdict(lambda: {
            'count': 0,
            'avg_accuracy': 0,
            'avg_predicted': 0,
            'avg_actual': 0
        })
        
        for perf in performances:
            stats = platform_stats[perf.platform]
            stats['count'] += 1
            stats['avg_accuracy'] += perf.accuracy
            stats['avg_predicted'] += perf.predicted_engagement_rate
            stats['avg_actual'] += perf.actual_engagement_rate
        
        for platform in platform_stats:
            stats = platform_stats[platform]
            if stats['count'] > 0:
                stats['avg_accuracy'] /= stats['count']
                stats['avg_predicted'] /= stats['count']
                stats['avg_actual'] /= stats['count']
        
        # Mejores y peores predicciones
        best_prediction = max(performances, key=lambda x: x.accuracy)
        worst_prediction = min(performances, key=lambda x: x.accuracy)
        
        return {
            "total_tracked": len(performances),
            "average_accuracy": round(avg_accuracy, 2),
            "average_predicted_rate": round(avg_predicted_rate, 2),
            "average_actual_rate": round(avg_actual_rate, 2),
            "prediction_bias": round(avg_predicted_rate - avg_actual_rate, 2),
            "platform_stats": dict(platform_stats),
            "best_prediction": {
                "post_id": best_prediction.post_id,
                "accuracy": best_prediction.accuracy,
                "platform": best_prediction.platform
            },
            "worst_prediction": {
                "post_id": worst_prediction.post_id,
                "accuracy": worst_prediction.accuracy,
                "platform": worst_prediction.platform
            },
            "improvement_suggestions": self._generate_improvement_suggestions(performances)
        }
    
    def _generate_improvement_suggestions(self, performances: List[PostPerformance]) -> List[str]:
        """Genera sugerencias de mejora basadas en tracking"""
        suggestions = []
        
        if not performances:
            return suggestions
        
        # Analizar sesgo de predicción
        avg_predicted = sum(p.predicted_engagement_rate for p in performances) / len(performances)
        avg_actual = sum(p.actual_engagement_rate for p in performances) / len(performances)
        
        bias = avg_predicted - avg_actual
        
        if abs(bias) > 2:
            if bias > 0:
                suggestions.append(f"Las predicciones están sobreestimando en promedio {bias:.2f}%. Considera ajustar el modelo.")
            else:
                suggestions.append(f"Las predicciones están subestimando en promedio {abs(bias):.2f}%. El contenido puede ser mejor de lo esperado.")
        
        # Analizar precisión por plataforma
        platform_accuracy = defaultdict(list)
        for perf in performances:
            platform_accuracy[perf.platform].append(perf.accuracy)
        
        for platform, accuracies in platform_accuracy.items():
            avg_acc = sum(accuracies) / len(accuracies)
            if avg_acc < 70:
                suggestions.append(f"La precisión en {platform} es baja ({avg_acc:.1f}%). Considera recopilar más datos históricos para esta plataforma.")
        
        return suggestions
    
    def export_for_ml_training(self, output_file: str) -> str:
        """
        Exporta datos de tracking en formato para entrenamiento ML
        
        Args:
            output_file: Archivo de salida
        
        Returns:
            Ruta del archivo generado
        """
        training_data = []
        
        for perf in self.tracked_posts.values():
            training_data.append({
                "platform": perf.platform,
                "predicted_engagement_rate": perf.predicted_engagement_rate,
                "predicted_score": perf.predicted_score,
                "actual_engagement_rate": perf.actual_engagement_rate,
                "actual_score": perf.actual_score,
                "accuracy": perf.accuracy,
                "likes": perf.likes,
                "comments": perf.comments,
                "shares": perf.shares,
                "impressions": perf.impressions
            })
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Datos de entrenamiento ML exportados: {output_file}")
        return str(output_path)



