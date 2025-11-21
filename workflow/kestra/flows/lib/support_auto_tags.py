"""
Sistema de Tags Automáticos para Tickets.

Características:
- Generación automática de tags basada en contenido
- Tags por categoría, prioridad, keywords
- Tags de urgencia y sentimiento
- Tags personalizados configurables
"""
import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

try:
    from .support_sentiment import SupportSentimentAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TagResult:
    """Resultado de generación de tags."""
    tags: List[str]
    confidence: float
    sources: Dict[str, List[str]]  # De dónde vienen los tags


class SupportAutoTagger:
    """Generador automático de tags para tickets."""
    
    # Keywords para tags comunes
    TAG_KEYWORDS = {
        "urgent": ["urgente", "inmediato", "asap", "crítico", "emergencia"],
        "payment": ["pago", "payment", "factura", "invoice", "cobro", "tarjeta"],
        "technical": ["error", "bug", "no funciona", "caído", "lento", "problema técnico"],
        "billing": ["factura", "invoice", "billing", "cobro", "refund", "reembolso"],
        "account": ["cuenta", "account", "login", "contraseña", "password", "acceso"],
        "feature": ["característica", "feature", "funcionalidad", "cómo hacer", "tutorial"],
        "vip": ["vip", "premium", "enterprise"],
        "recurring": ["nuevamente", "otra vez", "siempre", "repetido", "múltiples veces"],
        "positive": ["gracias", "excelente", "perfecto", "bien", "funciona"],
        "negative": ["problema", "mal", "terrible", "frustrado", "enojado"]
    }
    
    # Tags por categoría
    CATEGORY_TAGS = {
        "billing": ["billing", "payment", "finance"],
        "technical": ["technical", "bug", "error"],
        "sales": ["sales", "demo", "pricing"],
        "account": ["account", "access", "security"],
        "security": ["security", "critical", "urgent"]
    }
    
    # Tags por prioridad
    PRIORITY_TAGS = {
        "critical": ["critical", "urgent", "escalate"],
        "urgent": ["urgent", "high-priority"],
        "high": ["high-priority"],
        "medium": ["normal"],
        "low": ["low-priority"]
    }
    
    def __init__(self, enable_sentiment_tags: bool = True):
        """
        Inicializa el auto-tagger.
        
        Args:
            enable_sentiment_tags: Habilitar tags de sentimiento
        """
        self.enable_sentiment_tags = enable_sentiment_tags and SENTIMENT_AVAILABLE
        if self.enable_sentiment_tags:
            self.sentiment_analyzer = SupportSentimentAnalyzer()
    
    def extract_keywords(self, text: str) -> Set[str]:
        """Extrae keywords relevantes del texto."""
        if not text:
            return set()
        
        text_lower = text.lower()
        found_keywords = set()
        
        for tag, keywords in self.TAG_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.add(tag)
                    break
        
        return found_keywords
    
    def generate_tags(
        self,
        subject: Optional[str],
        description: str,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        customer_email: Optional[str] = None,
        existing_tags: Optional[List[str]] = None
    ) -> TagResult:
        """
        Genera tags automáticos para un ticket.
        
        Args:
            subject: Asunto del ticket
            description: Descripción
            category: Categoría del ticket
            priority: Prioridad del ticket
            customer_email: Email del cliente
            existing_tags: Tags existentes (se preservan)
            
        Returns:
            TagResult con tags generados
        """
        tags = set(existing_tags or [])
        sources = {
            "keywords": [],
            "category": [],
            "priority": [],
            "sentiment": [],
            "custom": []
        }
        
        # Combinar texto
        full_text = f"{subject or ''} {description}".lower()
        
        # Tags por keywords
        keyword_tags = self.extract_keywords(full_text)
        tags.update(keyword_tags)
        sources["keywords"] = list(keyword_tags)
        
        # Tags por categoría
        if category and category in self.CATEGORY_TAGS:
            category_tags = self.CATEGORY_TAGS[category]
            tags.update(category_tags)
            sources["category"] = category_tags
        
        # Tags por prioridad
        if priority and priority in self.PRIORITY_TAGS:
            priority_tags = self.PRIORITY_TAGS[priority]
            tags.update(priority_tags)
            sources["priority"] = priority_tags
        
        # Tags de sentimiento
        if self.enable_sentiment_tags:
            try:
                sentiment_result = self.sentiment_analyzer.analyze_text(full_text)
                if sentiment_result.sentiment == "negative":
                    tags.add("negative-sentiment")
                    sources["sentiment"].append("negative-sentiment")
                elif sentiment_result.sentiment == "positive":
                    tags.add("positive-sentiment")
                    sources["sentiment"].append("positive-sentiment")
                
                if sentiment_result.frustration_indicators > 0:
                    tags.add("frustrated")
                    sources["sentiment"].append("frustrated")
                
                if sentiment_result.urgency_score > 0.7:
                    tags.add("emotionally-urgent")
                    sources["sentiment"].append("emotionally-urgent")
            except Exception as e:
                logger.warning(f"Error in sentiment tagging: {e}")
        
        # Tags personalizados
        # VIP/Enterprise
        if customer_email:
            # En producción, se verificaría en BD
            if "vip" in customer_email.lower() or "enterprise" in customer_email.lower():
                tags.add("vip")
                sources["custom"].append("vip")
        
        # Tags de fuente (si está en metadata)
        # Se pueden agregar más tags personalizados aquí
        
        # Calcular confianza
        confidence = 0.5  # Base
        if keyword_tags:
            confidence += 0.2
        if category:
            confidence += 0.15
        if priority:
            confidence += 0.15
        
        confidence = min(1.0, confidence)
        
        return TagResult(
            tags=sorted(list(tags)),
            confidence=confidence,
            sources=sources
        )

