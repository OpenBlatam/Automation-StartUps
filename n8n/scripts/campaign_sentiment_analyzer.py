#!/usr/bin/env python3
"""
Campaign Sentiment Analyzer
Analiza sentimiento de comentarios y engagement en tiempo real
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import re


class CampaignSentimentAnalyzer:
    """
    Analizador de sentimiento para campañas
    Analiza comentarios, menciones y engagement para detectar sentimiento
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Diccionarios de sentimiento (simplificado)
        self.positive_words = {
            'excelente', 'genial', 'perfecto', 'increíble', 'fantástico',
            'me encanta', 'quiero', 'sí', 'interesante', 'bueno', 'genial',
            'amazing', 'great', 'love', 'perfect', 'awesome', 'wow'
        }
        
        self.negative_words = {
            'malo', 'horrible', 'terrible', 'no me gusta', 'caro', 'mal',
            'bad', 'terrible', 'hate', 'expensive', 'worst', 'disappointed'
        }
    
    def analyze_comment_sentiment(
        self,
        comment: str,
        language: str = "es"
    ) -> Dict[str, Any]:
        """
        Analiza sentimiento de un comentario
        
        Args:
            comment: Texto del comentario
            language: Idioma (es, en)
        
        Returns:
            Dict con análisis de sentimiento
        """
        comment_lower = comment.lower()
        
        # Contar palabras positivas y negativas
        positive_count = sum(1 for word in self.positive_words if word in comment_lower)
        negative_count = sum(1 for word in self.negative_words if word in comment_lower)
        
        # Detectar emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        emojis = emoji_pattern.findall(comment)
        emoji_sentiment = self._analyze_emoji_sentiment(emojis)
        
        # Calcular score de sentimiento (-1 a 1)
        base_score = (positive_count - negative_count) / max(len(comment.split()), 1)
        emoji_score = emoji_sentiment.get("score", 0)
        sentiment_score = (base_score * 0.7 + emoji_score * 0.3)
        sentiment_score = max(-1, min(1, sentiment_score))
        
        # Determinar categoría
        if sentiment_score > 0.3:
            category = "positive"
        elif sentiment_score < -0.3:
            category = "negative"
        else:
            category = "neutral"
        
        # Detectar intención
        intention = self._detect_intention(comment)
        
        return {
            "comment": comment,
            "sentimentScore": sentiment_score,
            "category": category,
            "positiveWords": positive_count,
            "negativeWords": negative_count,
            "emojis": emojis,
            "emojiSentiment": emoji_sentiment,
            "intention": intention,
            "confidence": min(abs(sentiment_score) * 1.5, 1.0),
            "analyzedAt": datetime.now().isoformat()
        }
    
    def analyze_batch_sentiment(
        self,
        comments: List[str],
        language: str = "es"
    ) -> Dict[str, Any]:
        """
        Analiza sentimiento de múltiples comentarios
        
        Args:
            comments: Lista de comentarios
            language: Idioma
        
        Returns:
            Dict con análisis agregado
        """
        analyses = [self.analyze_comment_sentiment(c, language) for c in comments]
        
        # Estadísticas agregadas
        total = len(analyses)
        positive = sum(1 for a in analyses if a["category"] == "positive")
        negative = sum(1 for a in analyses if a["category"] == "negative")
        neutral = sum(1 for a in analyses if a["category"] == "neutral")
        
        avg_sentiment = sum(a["sentimentScore"] for a in analyses) / total if total > 0 else 0
        
        # Detectar intenciones
        intentions = defaultdict(int)
        for a in analyses:
            intentions[a["intention"]] += 1
        
        # Comentarios más positivos y negativos
        most_positive = max(analyses, key=lambda x: x["sentimentScore"]) if analyses else None
        most_negative = min(analyses, key=lambda x: x["sentimentScore"]) if analyses else None
        
        return {
            "totalComments": total,
            "positiveCount": positive,
            "negativeCount": negative,
            "neutralCount": neutral,
            "positivePercentage": (positive / total * 100) if total > 0 else 0,
            "negativePercentage": (negative / total * 100) if total > 0 else 0,
            "averageSentiment": avg_sentiment,
            "overallSentiment": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
            "intentions": dict(intentions),
            "mostPositive": most_positive,
            "mostNegative": most_negative,
            "individualAnalyses": analyses,
            "analyzedAt": datetime.now().isoformat()
        }
    
    def detect_crisis(
        self,
        sentiment_analysis: Dict[str, Any],
        threshold: float = -0.3
    ) -> Optional[Dict[str, Any]]:
        """
        Detecta posibles crisis de reputación
        
        Args:
            sentiment_analysis: Análisis de sentimiento
            threshold: Umbral para detectar crisis
        
        Returns:
            Dict con alerta de crisis o None
        """
        if sentiment_analysis["averageSentiment"] < threshold:
            negative_percentage = sentiment_analysis["negativePercentage"]
            
            severity = "high" if negative_percentage > 30 else "medium" if negative_percentage > 15 else "low"
            
            return {
                "crisisDetected": True,
                "severity": severity,
                "averageSentiment": sentiment_analysis["averageSentiment"],
                "negativePercentage": negative_percentage,
                "recommendedActions": self._get_crisis_actions(severity),
                "detectedAt": datetime.now().isoformat()
            }
        
        return None
    
    def _analyze_emoji_sentiment(self, emojis: List[str]) -> Dict[str, Any]:
        """Analiza sentimiento de emojis"""
        if not emojis:
            return {"score": 0, "count": 0}
        
        # Emojis positivos comunes
        positive_emojis = ['😊', '😍', '❤️', '👍', '🔥', '✨', '🎉', '💯', '🚀']
        negative_emojis = ['😞', '😢', '👎', '💔', '😡', '❌']
        
        positive_count = sum(1 for e in emojis if any(pe in e for pe in positive_emojis))
        negative_count = sum(1 for e in emojis if any(ne in e for ne in negative_emojis))
        
        score = (positive_count - negative_count) / len(emojis) if emojis else 0
        
        return {
            "score": score,
            "count": len(emojis),
            "positiveCount": positive_count,
            "negativeCount": negative_count
        }
    
    def _detect_intention(self, comment: str) -> str:
        """Detecta intención del comentario"""
        comment_lower = comment.lower()
        
        # Intenciones comunes
        if any(word in comment_lower for word in ['quiero', 'comprar', 'quiero ser', 'sí', 'me interesa']):
            return "purchase_intent"
        elif any(word in comment_lower for word in ['pregunta', 'cuánto', 'cómo', 'dónde', 'cuándo']):
            return "question"
        elif any(word in comment_lower for word in ['gracias', 'excelente', 'genial']):
            return "appreciation"
        elif any(word in comment_lower for word in ['no', 'no me gusta', 'malo']):
            return "complaint"
        else:
            return "general"
    
    def _get_crisis_actions(self, severity: str) -> List[str]:
        """Obtiene acciones recomendadas según severidad"""
        actions = {
            "high": [
                "Responder inmediatamente a comentarios negativos",
                "Publicar comunicado oficial si es necesario",
                "Contactar a usuarios más afectados directamente",
                "Revisar y ajustar estrategia de campaña",
                "Monitorear continuamente el sentimiento"
            ],
            "medium": [
                "Responder a comentarios negativos prioritarios",
                "Ajustar mensajes de campaña si es necesario",
                "Aumentar engagement positivo",
                "Monitorear tendencias"
            ],
            "low": [
                "Monitorear situación",
                "Responder selectivamente",
                "Continuar con estrategia normal"
            ]
        }
        
        return actions.get(severity, [])


def main():
    """Ejemplo de uso"""
    analyzer = CampaignSentimentAnalyzer(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Comentarios de ejemplo
    comments = [
        "¡Excelente producto! Quiero ser de los primeros 🚀",
        "Me encanta, cómo puedo comprarlo?",
        "No me gusta, es muy caro",
        "Genial, estoy interesado",
        "Perfecto, justo lo que necesitaba ❤️",
        "No funciona bien",
        "Increíble, quiero más información"
    ]
    
    # Analizar batch
    analysis = analyzer.analyze_batch_sentiment(comments)
    print("=== Análisis de Sentimiento ===")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    # Detectar crisis
    crisis = analyzer.detect_crisis(analysis)
    if crisis:
        print("\n=== ⚠️ Crisis Detectada ===")
        print(json.dumps(crisis, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

