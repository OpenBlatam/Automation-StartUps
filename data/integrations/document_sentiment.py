"""
Análisis de Sentimiento
=======================

Analiza el sentimiento de documentos y comentarios.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Etiquetas de sentimiento"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentAnalysis:
    """Análisis de sentimiento"""
    text: str
    label: SentimentLabel
    score: float  # -1 a 1 (negativo a positivo)
    confidence: float
    analyzed_at: str


class SentimentAnalyzer:
    """Analizador de sentimiento"""
    
    def __init__(self, provider: str = "vader"):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
        self.analyzer = None
        self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Inicializa analizador según proveedor"""
        if self.provider == "vader":
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                self.analyzer = SentimentIntensityAnalyzer()
                self.logger.info("Analizador VADER inicializado")
            except ImportError:
                self.logger.warning(
                    "vaderSentiment no disponible. "
                    "Instala con: pip install vaderSentiment"
                )
        elif self.provider == "textblob":
            try:
                from textblob import TextBlob
                self.analyzer = TextBlob
                self.logger.info("Analizador TextBlob inicializado")
            except ImportError:
                self.logger.warning(
                    "textblob no disponible. "
                    "Instala con: pip install textblob"
                )
        elif self.provider == "transformers":
            try:
                from transformers import pipeline
                self.analyzer = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment"
                )
                self.logger.info("Analizador Transformers inicializado")
            except ImportError:
                self.logger.warning(
                    "transformers no disponible para análisis de sentimiento"
                )
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analiza sentimiento de un texto"""
        if not self.analyzer:
            # Fallback básico
            return self._basic_sentiment(text)
        
        try:
            if self.provider == "vader":
                scores = self.analyzer.polarity_scores(text)
                compound = scores['compound']
                
                if compound >= 0.05:
                    label = SentimentLabel.POSITIVE
                elif compound <= -0.05:
                    label = SentimentLabel.NEGATIVE
                else:
                    label = SentimentLabel.NEUTRAL
                
                return SentimentAnalysis(
                    text=text,
                    label=label,
                    score=compound,
                    confidence=abs(compound),
                    analyzed_at=datetime.now().isoformat()
                )
            
            elif self.provider == "textblob":
                blob = self.analyzer(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    label = SentimentLabel.POSITIVE
                elif polarity < -0.1:
                    label = SentimentLabel.NEGATIVE
                else:
                    label = SentimentLabel.NEUTRAL
                
                return SentimentAnalysis(
                    text=text,
                    label=label,
                    score=polarity,
                    confidence=abs(polarity),
                    analyzed_at=datetime.now().isoformat()
                )
            
            elif self.provider == "transformers":
                result = self.analyzer(text)[0]
                label_str = result['label'].lower()
                
                if 'positive' in label_str or '5' in label_str:
                    label = SentimentLabel.POSITIVE
                    score = 0.5
                elif 'negative' in label_str or '1' in label_str:
                    label = SentimentLabel.NEGATIVE
                    score = -0.5
                else:
                    label = SentimentLabel.NEUTRAL
                    score = 0.0
                
                return SentimentAnalysis(
                    text=text,
                    label=label,
                    score=score,
                    confidence=result['score'],
                    analyzed_at=datetime.now().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"Error analizando sentimiento: {e}")
            return self._basic_sentiment(text)
    
    def _basic_sentiment(self, text: str) -> SentimentAnalysis:
        """Análisis básico de sentimiento (fallback)"""
        positive_words = ['bueno', 'excelente', 'perfecto', 'genial', 'gracias']
        negative_words = ['malo', 'error', 'problema', 'fallo', 'incorrecto']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            label = SentimentLabel.POSITIVE
            score = 0.3
        elif negative_count > positive_count:
            label = SentimentLabel.NEGATIVE
            score = -0.3
        else:
            label = SentimentLabel.NEUTRAL
            score = 0.0
        
        return SentimentAnalysis(
            text=text,
            label=label,
            score=score,
            confidence=0.5,
            analyzed_at=datetime.now().isoformat()
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentAnalysis]:
        """Analiza sentimiento de múltiples textos"""
        return [self.analyze_sentiment(text) for text in texts]
    
    def get_sentiment_summary(self, analyses: List[SentimentAnalysis]) -> Dict[str, Any]:
        """Genera resumen de análisis de sentimiento"""
        total = len(analyses)
        if total == 0:
            return {}
        
        positive = sum(1 for a in analyses if a.label == SentimentLabel.POSITIVE)
        negative = sum(1 for a in analyses if a.label == SentimentLabel.NEGATIVE)
        neutral = sum(1 for a in analyses if a.label == SentimentLabel.NEUTRAL)
        
        avg_score = sum(a.score for a in analyses) / total
        
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_percentage": (positive / total) * 100,
            "negative_percentage": (negative / total) * 100,
            "average_score": avg_score,
            "overall_sentiment": (
                "positive" if avg_score > 0.1
                else "negative" if avg_score < -0.1
                else "neutral"
            )
        }

