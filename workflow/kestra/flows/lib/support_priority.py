"""
Módulo de Priorización Automática de Tickets de Soporte.

Características:
- Cálculo de score de prioridad basado en múltiples factores
- Análisis de urgencia del contenido
- Consideración del tipo de cliente
- Historial de tickets del cliente
"""
import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from .support_sentiment import SupportSentimentAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PriorityScore:
    """Score de prioridad calculado."""
    score: float  # 0.0 a 100.0
    priority: str  # low, medium, high, urgent, critical
    factors: Dict[str, Any]  # Factores que influyeron
    reasoning: str  # Explicación del score


class SupportPriorityCalculator:
    """Calculadora de prioridad para tickets de soporte."""
    
    # Palabras clave de urgencia
    CRITICAL_KEYWORDS = [
        "critico", "criticial", "crash", "down", "caído", "no funciona nada",
        "emergencia", "emergency", "urgente inmediato", "bloqueado", "blocked"
    ]
    
    URGENT_KEYWORDS = [
        "urgente", "urgent", "asap", "rápido", "inmediato", "hoy",
        "importante", "importante", "prioridad", "priority"
    ]
    
    HIGH_KEYWORDS = [
        "problema", "error", "bug", "falla", "issue", "no puedo",
        "no funciona", "broken", "no carga", "lento"
    ]
    
    # Factores de puntuación
    BASE_SCORE = 30.0
    CONTENT_URGENCY_MAX = 40.0
    CUSTOMER_TIER_MAX = 15.0
    HISTORY_IMPACT_MAX = 10.0
    TIME_SENSITIVITY_MAX = 5.0
    
    def __init__(
        self,
        db_connection: Any = None,
        vip_customers: Optional[List[str]] = None,
        enterprise_customers: Optional[List[str]] = None,
        enable_sentiment_analysis: bool = True
    ):
        """
        Inicializa el calculador de prioridad.
        
        Args:
            db_connection: Conexión a BD para consultar historial
            vip_customers: Lista de emails de clientes VIP
            enterprise_customers: Lista de emails de clientes enterprise
            enable_sentiment_analysis: Habilitar análisis de sentimiento
        """
        self.db_connection = db_connection
        self.vip_customers = set(vip_customers or [])
        self.enterprise_customers = set(enterprise_customers or [])
        self.enable_sentiment = enable_sentiment_analysis and SENTIMENT_AVAILABLE
        if self.enable_sentiment:
            self.sentiment_analyzer = SupportSentimentAnalyzer()
    
    def calculate_urgency_from_content(self, subject: str, description: str) -> Dict[str, Any]:
        """
        Calcula la urgencia basada en el contenido del ticket.
        
        Args:
            subject: Asunto del ticket
            description: Descripción del ticket
            
        Returns:
            Dict con score y factores
        """
        text = f"{subject or ''} {description or ''}".lower()
        score = 0.0
        factors = []
        
        # Buscar palabras clave críticas
        critical_matches = sum(1 for kw in self.CRITICAL_KEYWORDS if kw in text)
        if critical_matches > 0:
            score = min(self.CONTENT_URGENCY_MAX, critical_matches * 15.0)
            factors.append(f"Palabras críticas detectadas: {critical_matches}")
        
        # Buscar palabras urgentes
        if score < self.CONTENT_URGENCY_MAX:
            urgent_matches = sum(1 for kw in self.URGENT_KEYWORDS if kw in text)
            if urgent_matches > 0:
                score = max(score, min(30.0, urgent_matches * 10.0))
                factors.append(f"Palabras urgentes: {urgent_matches}")
        
        # Buscar palabras de alta prioridad
        if score < 20.0:
            high_matches = sum(1 for kw in self.HIGH_KEYWORDS if kw in text)
            if high_matches > 0:
                score = max(score, min(15.0, high_matches * 3.0))
                factors.append(f"Problemas detectados: {high_matches}")
        
        # Longitud del mensaje (mensajes muy cortos pueden ser urgentes)
        if len(text) < 50 and score < 10.0:
            score += 5.0
            factors.append("Mensaje muy corto (posible urgencia)")
        
        # Exclamaciones y mayúsculas (indican urgencia emocional)
        exclamation_count = text.count('!')
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', f"{subject or ''}"))
        if exclamation_count > 2 or caps_words > 2:
            score += min(10.0, (exclamation_count + caps_words) * 2.0)
            factors.append(f"Indicadores emocionales de urgencia")
        
        return {
            "score": min(score, self.CONTENT_URGENCY_MAX),
            "factors": factors,
            "matches": {
                "critical": critical_matches,
                "urgent": urgent_matches if 'urgent_matches' in locals() else 0,
                "high": high_matches if 'high_matches' in locals() else 0
            }
        }
    
    def calculate_customer_tier_score(self, customer_email: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcula score basado en el tipo/tier del cliente.
        
        Args:
            customer_email: Email del cliente
            customer_id: ID del cliente en CRM
            
        Returns:
            Dict con score y tier
        """
        email_lower = customer_email.lower()
        score = 0.0
        tier = "standard"
        factors = []
        
        # Cliente VIP
        if email_lower in self.vip_customers:
            score = CUSTOMER_TIER_MAX
            tier = "vip"
            factors.append("Cliente VIP")
        
        # Cliente Enterprise
        elif email_lower in self.enterprise_customers:
            score = CUSTOMER_TIER_MAX * 0.8
            tier = "enterprise"
            factors.append("Cliente Enterprise")
        
        # Verificar en BD si hay información adicional
        if self.db_connection and customer_id:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_tickets,
                        COUNT(*) FILTER (WHERE priority IN ('urgent', 'critical')) as urgent_tickets,
                        MAX(created_at) as last_ticket_date
                    FROM support_tickets
                    WHERE customer_id = %s
                    GROUP BY customer_id
                """, (customer_id,))
                
                row = cursor.fetchone()
                if row:
                    total_tickets, urgent_tickets, last_ticket_date = row
                    
                    # Si es cliente frecuente con tickets urgentes, aumentar score
                    if total_tickets > 10 and urgent_tickets > 3:
                        score += min(5.0, urgent_tickets * 1.0)
                        factors.append(f"Cliente frecuente con {urgent_tickets} tickets urgentes")
                    
                    # Si último ticket fue hace menos de 24h, puede ser problema recurrente
                    if last_ticket_date:
                        hours_ago = (datetime.now() - last_ticket_date).total_seconds() / 3600
                        if hours_ago < 24:
                            score += 3.0
                            factors.append("Ticket reciente (posible problema recurrente)")
                
                cursor.close()
            except Exception as e:
                logger.warning(f"Error consultando historial de cliente: {e}")
        
        return {
            "score": min(score, self.CUSTOMER_TIER_MAX),
            "tier": tier,
            "factors": factors
        }
    
    def calculate_time_sensitivity(self, subject: str, description: str) -> Dict[str, Any]:
        """
        Calcula sensibilidad temporal (deadlines, fechas importantes).
        
        Args:
            subject: Asunto
            description: Descripción
            
        Returns:
            Dict con score
        """
        text = f"{subject or ''} {description or ''}".lower()
        score = 0.0
        factors = []
        
        # Buscar fechas y deadlines
        date_patterns = [
            r'\b(hoy|today|now|ahora)\b',
            r'\b(mañana|tomorrow)\b',
            r'\b(esta semana|this week)\b',
            r'\bdeadline\b',
            r'\b(fecha límite|fecha limite)\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'  # Fechas
        ]
        
        for pattern in date_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                score += min(5.0, matches * 2.0)
                factors.append(f"Referencias temporales encontradas: {matches}")
                break
        
        return {
            "score": min(score, self.TIME_SENSITIVITY_MAX),
            "factors": factors
        }
    
    def calculate_priority(
        self,
        subject: str,
        description: str,
        customer_email: str,
        customer_id: Optional[str] = None,
        source: str = "web",
        category: Optional[str] = None
    ) -> PriorityScore:
        """
        Calcula el score de prioridad completo del ticket.
        
        Args:
            subject: Asunto del ticket
            description: Descripción
            customer_email: Email del cliente
            customer_id: ID del cliente
            source: Origen del ticket
            category: Categoría del ticket
            
        Returns:
            PriorityScore con score, prioridad y factores
        """
        # Score base
        total_score = self.BASE_SCORE
        
        # Urgencia del contenido
        content_urgency = self.calculate_urgency_from_content(subject, description)
        total_score += content_urgency["score"]
        
        # Tier del cliente
        customer_tier = self.calculate_customer_tier_score(customer_email, customer_id)
        total_score += customer_tier["score"]
        
        # Sensibilidad temporal
        time_sensitivity = self.calculate_time_sensitivity(subject, description)
        total_score += time_sensitivity["score"]
        
        # Ajustes por categoría
        category_boost = {
            "billing": 5.0,  # Problemas de facturación son importantes
            "technical": 3.0,  # Problemas técnicos
            "security": 15.0,  # Seguridad es crítica
        }
        if category and category in category_boost:
            total_score += category_boost[category]
        
        # Ajustes por fuente
        source_boost = {
            "phone": 5.0,  # Llamadas telefónicas suelen ser más urgentes
            "chat": 2.0,
            "email": 0.0,
        }
        if source in source_boost:
            total_score += source_boost[source]
        
        # Análisis de sentimiento (boost adicional)
        if self.enable_sentiment:
            try:
                sentiment_result = self.sentiment_analyzer.analyze_ticket(subject, description)
                sentiment_boost = self.sentiment_analyzer.get_sentiment_boost(sentiment_result)
                total_score += sentiment_boost
                
                # Agregar a factores
                all_factors["sentiment"] = {
                    "sentiment": sentiment_result.sentiment,
                    "score": sentiment_result.score,
                    "urgency_score": sentiment_result.urgency_score,
                    "frustration_indicators": sentiment_result.frustration_indicators,
                    "boost": sentiment_boost
                }
            except Exception as e:
                logger.warning(f"Error en análisis de sentimiento: {e}")
        
        # Normalizar score (0-100)
        total_score = min(100.0, max(0.0, total_score))
        
        # Determinar prioridad
        if total_score >= 85:
            priority = "critical"
        elif total_score >= 70:
            priority = "urgent"
        elif total_score >= 55:
            priority = "high"
        elif total_score >= 40:
            priority = "medium"
        else:
            priority = "low"
        
        # Construir reasoning
        reasoning_parts = []
        if content_urgency["score"] > 0:
            reasoning_parts.append(f"Urgencia en contenido: {content_urgency['score']:.1f} puntos")
        if customer_tier["score"] > 0:
            reasoning_parts.append(f"Tier de cliente ({customer_tier['tier']}): {customer_tier['score']:.1f} puntos")
        if time_sensitivity["score"] > 0:
            reasoning_parts.append(f"Sensibilidad temporal: {time_sensitivity['score']:.1f} puntos")
        
        reasoning = f"Score total: {total_score:.1f}/100. " + "; ".join(reasoning_parts) if reasoning_parts else f"Score base: {total_score:.1f}/100"
        
        # Consolidar factores
        all_factors = {
            "content_urgency": content_urgency,
            "customer_tier": customer_tier,
            "time_sensitivity": time_sensitivity,
            "category_boost": category if category in category_boost else None,
            "source_boost": source,
            "base_score": self.BASE_SCORE,
            "final_score": total_score
        }
        
        return PriorityScore(
            score=total_score,
            priority=priority,
            factors=all_factors,
            reasoning=reasoning
        )

