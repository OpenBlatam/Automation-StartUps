"""
Análisis de Sentimiento Avanzado con NLP

Análisis profundo de sentimiento usando técnicas de NLP para:
- Análisis de sentimiento granular
- Detección de emociones
- Análisis de aspectos
- Extracción de temas
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """Análisis de sentimiento."""
    text: str
    overall_sentiment: str  # 'positive', 'negative', 'neutral'
    sentiment_score: float  # -1 a 1
    confidence: float  # 0-1
    emotions: Dict[str, float]  # 'joy', 'anger', 'fear', 'sadness', etc.
    key_phrases: List[str]
    topics: List[str]


class AdvancedSentimentAnalyzer:
    """Analizador avanzado de sentimiento con NLP."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        self.logger = logging.getLogger(__name__)
    
    def analyze_sentiment(
        self,
        text: str,
        language: str = "en"
    ) -> SentimentAnalysis:
        """
        Analiza sentimiento de un texto.
        
        Args:
            text: Texto a analizar
            language: Idioma del texto
            
        Returns:
            Análisis de sentimiento
        """
        if not text or not text.strip():
            return SentimentAnalysis(
                text=text,
                overall_sentiment="neutral",
                sentiment_score=0.0,
                confidence=0.0,
                emotions={},
                key_phrases=[],
                topics=[]
            )
        
        # Análisis con VADER
        vader_scores = None
        if self.vader_analyzer:
            vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # Análisis con TextBlob
        textblob_sentiment = None
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                textblob_sentiment = blob.sentiment
            except Exception as e:
                logger.warning(f"TextBlob analysis failed: {e}")
        
        # Combinar resultados
        if vader_scores:
            sentiment_score = vader_scores.get("compound", 0.0)
        elif textblob_sentiment:
            sentiment_score = textblob_sentiment.polarity
        else:
            sentiment_score = 0.0
        
        # Determinar sentimiento general
        if sentiment_score > 0.1:
            overall_sentiment = "positive"
        elif sentiment_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        # Calcular confianza
        if vader_scores:
            confidence = max(
                abs(vader_scores.get("pos", 0)),
                abs(vader_scores.get("neg", 0)),
                abs(vader_scores.get("neu", 0))
            )
        else:
            confidence = abs(sentiment_score)
        
        # Detectar emociones (simplificado)
        emotions = self._detect_emotions(text, sentiment_score)
        
        # Extraer frases clave
        key_phrases = self._extract_key_phrases(text)
        
        # Extraer temas
        topics = self._extract_topics(text)
        
        return SentimentAnalysis(
            text=text,
            overall_sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            confidence=confidence,
            emotions=emotions,
            key_phrases=key_phrases,
            topics=topics
        )
    
    def analyze_batch_sentiment(
        self,
        texts: List[str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analiza sentimiento de múltiples textos.
        
        Args:
            texts: Lista de textos
            language: Idioma
            
        Returns:
            Análisis agregado
        """
        analyses = [self.analyze_sentiment(text, language) for text in texts]
        
        # Agregar resultados
        total = len(analyses)
        positive_count = sum(1 for a in analyses if a.overall_sentiment == "positive")
        negative_count = sum(1 for a in analyses if a.overall_sentiment == "negative")
        neutral_count = sum(1 for a in analyses if a.overall_sentiment == "neutral")
        
        avg_sentiment = sum(a.sentiment_score for a in analyses) / total if total > 0 else 0.0
        avg_confidence = sum(a.confidence for a in analyses) / total if total > 0 else 0.0
        
        # Agregar emociones
        all_emotions = {}
        for analysis in analyses:
            for emotion, value in analysis.emotions.items():
                if emotion not in all_emotions:
                    all_emotions[emotion] = []
                all_emotions[emotion].append(value)
        
        avg_emotions = {
            emotion: sum(values) / len(values)
            for emotion, values in all_emotions.items()
        }
        
        # Agregar temas
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis.topics)
        
        # Contar temas más frecuentes
        from collections import Counter
        topic_counts = Counter(all_topics)
        top_topics = [topic for topic, count in topic_counts.most_common(10)]
        
        return {
            "total_texts": total,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_percentage": (positive_count / total * 100) if total > 0 else 0,
            "negative_percentage": (negative_count / total * 100) if total > 0 else 0,
            "average_sentiment_score": avg_sentiment,
            "average_confidence": avg_confidence,
            "overall_sentiment": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
            "average_emotions": avg_emotions,
            "top_topics": top_topics,
            "individual_analyses": [
                {
                    "text": a.text[:100] + "..." if len(a.text) > 100 else a.text,
                    "sentiment": a.overall_sentiment,
                    "score": a.sentiment_score
                }
                for a in analyses
            ]
        }
    
    def _detect_emotions(self, text: str, sentiment_score: float) -> Dict[str, float]:
        """Detecta emociones en el texto (simplificado)."""
        text_lower = text.lower()
        emotions = {
            "joy": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "sadness": 0.0,
            "surprise": 0.0
        }
        
        # Palabras clave de emociones (simplificado)
        joy_words = ["happy", "excited", "great", "wonderful", "amazing", "excellent"]
        anger_words = ["angry", "furious", "outraged", "frustrated", "annoyed"]
        fear_words = ["worried", "afraid", "scared", "concerned", "anxious"]
        sadness_words = ["sad", "disappointed", "depressed", "unhappy", "gloomy"]
        surprise_words = ["surprised", "shocked", "amazed", "astonished", "unexpected"]
        
        # Contar palabras de emoción
        for word in joy_words:
            if word in text_lower:
                emotions["joy"] += 0.2
        
        for word in anger_words:
            if word in text_lower:
                emotions["anger"] += 0.2
        
        for word in fear_words:
            if word in text_lower:
                emotions["fear"] += 0.2
        
        for word in sadness_words:
            if word in text_lower:
                emotions["sadness"] += 0.2
        
        for word in surprise_words:
            if word in text_lower:
                emotions["surprise"] += 0.2
        
        # Normalizar
        max_emotion = max(emotions.values()) if emotions.values() else 1.0
        if max_emotion > 0:
            emotions = {k: min(1.0, v / max_emotion) for k, v in emotions.items()}
        
        # Ajustar por sentimiento general
        if sentiment_score > 0:
            emotions["joy"] = max(emotions["joy"], abs(sentiment_score))
        elif sentiment_score < 0:
            emotions["sadness"] = max(emotions["sadness"], abs(sentiment_score))
        
        return emotions
    
    def _extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extrae frases clave del texto."""
        # Simplificado - en producción usarías técnicas más avanzadas
        # Por ahora, extraemos palabras importantes
        
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                # Obtener sustantivos y adjetivos
                phrases = []
                for word, pos in blob.tags:
                    if pos.startswith('NN') or pos.startswith('JJ'):
                        phrases.append(word)
                return phrases[:max_phrases]
            except Exception:
                pass
        
        # Fallback: palabras más comunes
        words = text.lower().split()
        # Filtrar palabras comunes
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        important_words = [w for w in words if w not in common_words and len(w) > 3]
        return list(set(important_words))[:max_phrases]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrae temas del texto."""
        # Simplificado - en producción usarías topic modeling
        key_phrases = self._extract_key_phrases(text, max_phrases=10)
        return key_phrases






