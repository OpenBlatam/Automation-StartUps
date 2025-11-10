#!/usr/bin/env python3
"""
Funcionalidades Avanzadas para Chatbots
Incluye rate limiting, feedback, análisis de tendencias y más
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class FeedbackType(Enum):
    """Tipos de feedback"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


@dataclass
class RateLimitConfig:
    """Configuración de rate limiting"""
    max_requests: int = 60  # Máximo de requests
    time_window: int = 60   # Ventana de tiempo en segundos
    block_duration: int = 300  # Duración del bloqueo en segundos


@dataclass
class FeedbackEntry:
    """Entrada de feedback"""
    conversation_id: str
    message_id: str
    feedback_type: FeedbackType
    comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None


class RateLimiter:
    """Sistema de rate limiting para chatbots"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.requests = defaultdict(deque)  # user_id -> deque de timestamps
        self.blocked_users = {}  # user_id -> unblock_time
    
    def is_allowed(self, user_id: str = "default") -> Tuple[bool, Optional[str]]:
        """
        Verifica si un usuario puede hacer una request.
        
        Returns:
            (allowed, reason)
        """
        now = time.time()
        
        # Verificar si está bloqueado
        if user_id in self.blocked_users:
            unblock_time = self.blocked_users[user_id]
            if now < unblock_time:
                remaining = int(unblock_time - now)
                return False, f"Usuario bloqueado. Intenta de nuevo en {remaining} segundos"
            else:
                # Desbloquear
                del self.blocked_users[user_id]
        
        # Limpiar requests antiguos
        user_requests = self.requests[user_id]
        cutoff_time = now - self.config.time_window
        
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()
        
        # Verificar límite
        if len(user_requests) >= self.config.max_requests:
            # Bloquear usuario
            self.blocked_users[user_id] = now + self.config.block_duration
            return False, f"Límite de requests excedido. Bloqueado por {self.config.block_duration} segundos"
        
        # Registrar request
        user_requests.append(now)
        return True, None
    
    def get_stats(self, user_id: str = "default") -> Dict:
        """Obtiene estadísticas de rate limiting para un usuario"""
        now = time.time()
        user_requests = self.requests[user_id]
        cutoff_time = now - self.config.time_window
        
        # Limpiar requests antiguos
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()
        
        is_blocked = user_id in self.blocked_users and now < self.blocked_users[user_id]
        
        return {
            "user_id": user_id,
            "requests_in_window": len(user_requests),
            "max_requests": self.config.max_requests,
            "remaining_requests": max(0, self.config.max_requests - len(user_requests)),
            "is_blocked": is_blocked,
            "block_until": self.blocked_users.get(user_id) if is_blocked else None
        }


class FeedbackSystem:
    """Sistema de feedback para mejorar el chatbot"""
    
    def __init__(self, feedback_file: str = "chatbot_feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedbacks: List[FeedbackEntry] = []
        self._load_feedback()
    
    def _load_feedback(self):
        """Carga feedback desde archivo"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.feedbacks = [
                        FeedbackEntry(
                            conversation_id=fb['conversation_id'],
                            message_id=fb['message_id'],
                            feedback_type=FeedbackType(fb['feedback_type']),
                            comment=fb.get('comment'),
                            timestamp=datetime.fromisoformat(fb['timestamp']),
                            user_id=fb.get('user_id')
                        )
                        for fb in data.get('feedbacks', [])
                    ]
            except Exception:
                self.feedbacks = []
    
    def _save_feedback(self):
        """Guarda feedback a archivo"""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_feedbacks": len(self.feedbacks),
            "feedbacks": [
                {
                    "conversation_id": fb.conversation_id,
                    "message_id": fb.message_id,
                    "feedback_type": fb.feedback_type.value,
                    "comment": fb.comment,
                    "timestamp": fb.timestamp.isoformat(),
                    "user_id": fb.user_id
                }
                for fb in self.feedbacks
            ]
        }
        
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_feedback(self, feedback: FeedbackEntry):
        """Agrega un feedback"""
        self.feedbacks.append(feedback)
        self._save_feedback()
    
    def get_feedback_stats(self) -> Dict:
        """Obtiene estadísticas de feedback"""
        if not self.feedbacks:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "helpful": 0,
                "not_helpful": 0,
                "positive_rate": 0.0,
                "helpful_rate": 0.0
            }
        
        total = len(self.feedbacks)
        positive = sum(1 for fb in self.feedbacks if fb.feedback_type == FeedbackType.POSITIVE)
        negative = sum(1 for fb in self.feedbacks if fb.feedback_type == FeedbackType.NEGATIVE)
        helpful = sum(1 for fb in self.feedbacks if fb.feedback_type == FeedbackType.HELPFUL)
        not_helpful = sum(1 for fb in self.feedbacks if fb.feedback_type == FeedbackType.NOT_HELPFUL)
        
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "positive_rate": positive / total if total > 0 else 0.0,
            "helpful_rate": helpful / (helpful + not_helpful) if (helpful + not_helpful) > 0 else 0.0
        }
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Obtiene feedback reciente"""
        recent = sorted(self.feedbacks, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [
            {
                "conversation_id": fb.conversation_id,
                "feedback_type": fb.feedback_type.value,
                "comment": fb.comment,
                "timestamp": fb.timestamp.isoformat()
            }
            for fb in recent
        ]


class TrendAnalyzer:
    """Analizador de tendencias en conversaciones"""
    
    def __init__(self, conversation_dir: str = "chatbot_conversations"):
        self.conversation_dir = Path(conversation_dir)
    
    def analyze_intent_trends(self, days: int = 7) -> Dict:
        """Analiza tendencias de intenciones en los últimos días"""
        cutoff_date = datetime.now() - timedelta(days=days)
        intent_counts = defaultdict(int)
        total_conversations = 0
        
        if not self.conversation_dir.exists():
            return {"error": "Directorio de conversaciones no existe"}
        
        for conv_file in self.conversation_dir.glob("*.json"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                created_at = datetime.fromisoformat(data.get('created_at', ''))
                if created_at < cutoff_date:
                    continue
                
                # Extraer intenciones de los mensajes
                for msg in data.get('messages', []):
                    if msg.get('role') == 'assistant':
                        # Buscar intent en metadata si existe
                        intent = msg.get('intent')
                        if intent:
                            intent_counts[intent] += 1
                
                total_conversations += 1
            except Exception:
                continue
        
        # Calcular porcentajes
        total_intents = sum(intent_counts.values())
        intent_percentages = {
            intent: (count / total_intents * 100) if total_intents > 0 else 0
            for intent, count in intent_counts.items()
        }
        
        return {
            "period_days": days,
            "total_conversations": total_conversations,
            "intent_counts": dict(intent_counts),
            "intent_percentages": intent_percentages,
            "most_common_intent": max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        }
    
    def analyze_escalation_trends(self, days: int = 7) -> Dict:
        """Analiza tendencias de escalación"""
        cutoff_date = datetime.now() - timedelta(days=days)
        escalations_by_day = defaultdict(int)
        total_escalations = 0
        
        if not self.conversation_dir.exists():
            return {"error": "Directorio de conversaciones no existe"}
        
        for conv_file in self.conversation_dir.glob("*.json"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                created_at = datetime.fromisoformat(data.get('created_at', ''))
                if created_at < cutoff_date:
                    continue
                
                # Contar escalaciones
                for msg in data.get('messages', []):
                    if msg.get('role') == 'assistant' and msg.get('requires_escalation'):
                        day_key = created_at.strftime('%Y-%m-%d')
                        escalations_by_day[day_key] += 1
                        total_escalations += 1
            except Exception:
                continue
        
        return {
            "period_days": days,
            "total_escalations": total_escalations,
            "escalations_by_day": dict(escalations_by_day),
            "average_per_day": total_escalations / days if days > 0 else 0
        }
    
    def get_peak_hours(self, days: int = 7) -> Dict:
        """Identifica horas pico de uso"""
        cutoff_date = datetime.now() - timedelta(days=days)
        hour_counts = defaultdict(int)
        
        if not self.conversation_dir.exists():
            return {"error": "Directorio de conversaciones no existe"}
        
        for conv_file in self.conversation_dir.glob("*.json"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                created_at = datetime.fromisoformat(data.get('created_at', ''))
                if created_at < cutoff_date:
                    continue
                
                hour = created_at.hour
                hour_counts[hour] += 1
            except Exception:
                continue
        
        if not hour_counts:
            return {"error": "No hay datos suficientes"}
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "period_days": days,
            "hour_distribution": dict(hour_counts),
            "peak_hour": peak_hour,
            "peak_hour_count": hour_counts[peak_hour]
        }


class AISuggestions:
    """Sistema de sugerencias basado en análisis"""
    
    def __init__(self, feedback_system: FeedbackSystem, trend_analyzer: TrendAnalyzer):
        self.feedback_system = feedback_system
        self.trend_analyzer = trend_analyzer
    
    def generate_suggestions(self) -> List[Dict]:
        """Genera sugerencias para mejorar el chatbot"""
        suggestions = []
        
        # Analizar feedback
        feedback_stats = self.feedback_system.get_feedback_stats()
        
        if feedback_stats['total'] > 0:
            if feedback_stats['positive_rate'] < 0.7:
                suggestions.append({
                    "type": "feedback",
                    "priority": "high",
                    "message": f"Tasa de feedback positivo baja ({feedback_stats['positive_rate']:.1%}). "
                              "Considera mejorar las respuestas más comunes.",
                    "action": "Revisar FAQs más consultadas y mejorar respuestas"
                })
            
            if feedback_stats['helpful_rate'] < 0.8:
                suggestions.append({
                    "type": "feedback",
                    "priority": "medium",
                    "message": f"Tasa de utilidad baja ({feedback_stats['helpful_rate']:.1%}). "
                              "Algunas respuestas no están siendo útiles.",
                    "action": "Analizar feedback negativo y ajustar respuestas"
                })
        
        # Analizar tendencias de escalación
        escalation_trends = self.trend_analyzer.analyze_escalation_trends(days=7)
        if 'average_per_day' in escalation_trends:
            avg_escalations = escalation_trends['average_per_day']
            if avg_escalations > 10:
                suggestions.append({
                    "type": "escalation",
                    "priority": "high",
                    "message": f"Alto número de escalaciones diarias ({avg_escalations:.1f}/día). "
                              "El chatbot podría necesitar más información en FAQs.",
                    "action": "Agregar más FAQs basadas en razones de escalación más comunes"
                })
        
        # Analizar intenciones
        intent_trends = self.trend_analyzer.analyze_intent_trends(days=7)
        if 'most_common_intent' in intent_trends and intent_trends['most_common_intent']:
            most_common = intent_trends['most_common_intent']
            if most_common == 'otro':
                suggestions.append({
                    "type": "intent",
                    "priority": "medium",
                    "message": "Muchas consultas no identificadas. "
                              "Considera agregar más patrones de detección de intención.",
                    "action": "Revisar mensajes con intent 'otro' y agregar patrones"
                })
        
        return suggestions


def create_health_check(chatbot_instance) -> Dict:
    """
    Crea un health check del chatbot.
    
    Args:
        chatbot_instance: Instancia del chatbot
    
    Returns:
        Dict con estado de salud del chatbot
    """
    metrics = chatbot_instance.get_metrics()
    
    health_status = "healthy"
    issues = []
    
    # Verificar tasa de escalación
    if metrics.get('escalation_rate', 0) > 0.3:
        health_status = "warning"
        issues.append("Alta tasa de escalación (>30%)")
    
    # Verificar confianza promedio
    if metrics.get('average_confidence', 0) < 0.6:
        health_status = "warning"
        issues.append("Baja confianza promedio (<60%)")
    
    # Verificar tasa de match FAQ
    if metrics.get('faq_match_rate', 0) < 0.5:
        health_status = "warning"
        issues.append("Baja tasa de match de FAQs (<50%)")
    
    # Verificar tiempo de procesamiento
    avg_time = metrics.get('average_processing_time', 0)
    if avg_time > 1.0:
        health_status = "warning"
        issues.append(f"Tiempo de procesamiento alto ({avg_time:.2f}s)")
    
    return {
        "status": health_status,
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "issues": issues,
        "cache_size": len(getattr(chatbot_instance, 'response_cache', {})),
        "total_faqs": len(getattr(chatbot_instance, 'faqs', []))
    }






