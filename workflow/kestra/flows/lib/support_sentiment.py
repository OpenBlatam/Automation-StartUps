"""
Módulo de Análisis de Sentimiento para Tickets de Soporte.

Características:
- Análisis básico de sentimiento (positivo/negativo/neutral)
- Detección de urgencia emocional
- Scoring de frustración
- Integración opcional con servicios externos (AWS Comprehend, Google NLP)
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Resultado del análisis de sentimiento."""
    sentiment: str  # positive, negative, neutral
    score: float  # 0.0 a 1.0
    urgency_score: float  # 0.0 a 1.0
    frustration_indicators: int
    keywords: list[str]


class SupportSentimentAnalyzer:
    """Analizador de sentimiento para tickets de soporte."""
    
    # Palabras indicadoras de sentimiento negativo
    NEGATIVE_KEYWORDS = [
        "problema", "error", "falla", "no funciona", "roto", "mal",
        "terrible", "horrible", "frustrado", "molesto", "enojado",
        "desesperado", "urgente", "crítico", "grave", "importante",
        "bloqueado", "atascado", "no puedo", "imposible"
    ]
    
    # Palabras indicadoras de sentimiento positivo
    POSITIVE_KEYWORDS = [
        "gracias", "excelente", "perfecto", "genial", "bueno",
        "bien", "funciona", "satisfecho", "contento", "feliz",
        "ayuda", "apoyo", "resolver", "solucionar"
    ]
    
    # Indicadores de frustración
    FRUSTRATION_KEYWORDS = [
        "nuevamente", "otra vez", "siempre", "nunca", "todavía",
        "aún", "sigue", "persiste", "repetido", "múltiples veces",
        "varias veces", "muchas veces", "demasiadas veces"
    ]
    
    # Indicadores de urgencia emocional
    URGENCY_EMOTIONAL_KEYWORDS = [
        "urgente", "inmediato", "ahora", "ya", "rápido", "asap",
        "crítico", "emergencia", "importante", "prioridad",
        "necesito", "debo", "tengo que"
    ]
    
    def __init__(self, enable_external_api: bool = False, api_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el analizador de sentimiento.
        
        Args:
            enable_external_api: Habilitar APIs externas (AWS Comprehend, etc.)
            api_config: Configuración de API externa
        """
        self.enable_external_api = enable_external_api
        self.api_config = api_config or {}
    
    def analyze_text(self, text: str) -> SentimentResult:
        """
        Analiza el sentimiento de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            SentimentResult con análisis completo
        """
        if not text:
            return SentimentResult(
                sentiment="neutral",
                score=0.5,
                urgency_score=0.0,
                frustration_indicators=0,
                keywords=[]
            )
        
        text_lower = text.lower()
        
        # Contar palabras clave
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        frustration_count = sum(1 for kw in self.FRUSTRATION_KEYWORDS if kw in text_lower)
        urgency_count = sum(1 for kw in self.URGENCY_EMOTIONAL_KEYWORDS if kw in text_lower)
        
        # Detectar mayúsculas (indicador de urgencia emocional)
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if caps_words > 2:
            urgency_count += 2
        
        # Detectar exclamaciones
        exclamation_count = text.count('!')
        if exclamation_count > 2:
            urgency_count += 2
            negative_count += 1
        
        # Calcular score de sentimiento
        total_keywords = negative_count + positive_count
        if total_keywords == 0:
            sentiment_score = 0.5
            sentiment = "neutral"
        elif negative_count > positive_count:
            sentiment_score = max(0.0, 0.5 - (negative_count / max(total_keywords, 1)) * 0.5)
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment_score = min(1.0, 0.5 + (positive_count / max(total_keywords, 1)) * 0.5)
            sentiment = "positive"
        else:
            sentiment_score = 0.5
            sentiment = "neutral"
        
        # Calcular score de urgencia (0.0 a 1.0)
        urgency_score = min(1.0, urgency_count / 10.0)
        
        # Keywords encontradas
        found_keywords = []
        for kw in self.NEGATIVE_KEYWORDS + self.POSITIVE_KEYWORDS:
            if kw in text_lower:
                found_keywords.append(kw)
        
        return SentimentResult(
            sentiment=sentiment,
            score=sentiment_score,
            urgency_score=urgency_score,
            frustration_indicators=frustration_count,
            keywords=found_keywords[:10]  # Limitar a 10
        )
    
    def analyze_ticket(self, subject: str, description: str) -> SentimentResult:
        """
        Analiza el sentimiento de un ticket completo.
        
        Args:
            subject: Asunto del ticket
            description: Descripción del ticket
            
        Returns:
            SentimentResult combinado
        """
        # Combinar texto (el asunto tiene más peso)
        combined_text = f"{subject} {subject} {description}"  # Asunto duplicado para más peso
        
        result = self.analyze_text(combined_text)
        
        # Ajustar score de urgencia si hay frustración
        if result.frustration_indicators > 0:
            result.urgency_score = min(1.0, result.urgency_score + (result.frustration_indicators * 0.1))
            if result.sentiment == "neutral":
                result.sentiment = "negative"
                result.score = max(0.0, result.score - 0.2)
        
        return result
    
    def should_escalate_by_sentiment(self, sentiment_result: SentimentResult) -> bool:
        """
        Determina si un ticket debería escalarse basado en sentimiento.
        
        Args:
            sentiment_result: Resultado del análisis de sentimiento
            
        Returns:
            True si debería escalarse
        """
        # Escalar si:
        # - Sentimiento muy negativo (score < 0.3)
        # - Urgencia emocional alta (urgency_score > 0.7)
        # - Múltiples indicadores de frustración (> 2)
        
        if sentiment_result.sentiment == "negative" and sentiment_result.score < 0.3:
            return True
        
        if sentiment_result.urgency_score > 0.7:
            return True
        
        if sentiment_result.frustration_indicators > 2:
            return True
        
        return False
    
    def get_sentiment_boost(self, sentiment_result: SentimentResult) -> float:
        """
        Calcula boost de prioridad basado en sentimiento.
        
        Args:
            sentiment_result: Resultado del análisis
            
        Returns:
            Boost de puntos (0-15)
        """
        boost = 0.0
        
        # Boost por sentimiento negativo
        if sentiment_result.sentiment == "negative":
            boost += (1.0 - sentiment_result.score) * 10.0  # Máximo 10 puntos
        
        # Boost por urgencia emocional
        boost += sentiment_result.urgency_score * 5.0  # Máximo 5 puntos
        
        return min(15.0, boost)

