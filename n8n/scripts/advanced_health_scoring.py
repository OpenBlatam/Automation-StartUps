#!/usr/bin/env python3
"""
Advanced Customer Health Scoring
Sistema avanzado de scoring de salud del cliente con ML
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Estados de salud del cliente"""
    CRITICAL = "critical"
    AT_RISK = "at_risk"
    STABLE = "stable"
    HEALTHY = "healthy"
    CHAMPION = "champion"


@dataclass
class HealthScore:
    """Score de salud del cliente"""
    customer_id: str
    overall_score: float  # 0-100
    status: HealthStatus
    category_scores: Dict[str, float]
    risk_factors: List[str]
    opportunities: List[str]
    recommendations: List[str]
    trend: str  # "improving", "stable", "declining"
    last_updated: str


class AdvancedHealthScoring:
    """
    Sistema avanzado de scoring de salud del cliente
    """
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def calculate_health_score(
        self,
        customer_id: str,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> HealthScore:
        """
        Calcula el score de salud completo del cliente
        
        Args:
            customer_id: ID del cliente
            customer_data: Datos del cliente (opcional, si no se proporciona se obtienen)
        
        Returns:
            HealthScore con score completo
        """
        if not customer_data:
            customer_data = self._get_customer_data(customer_id)
        
        # Calcular scores por categoría
        engagement_score = self._calculate_engagement_score(customer_data)
        product_usage_score = self._calculate_product_usage_score(customer_data)
        support_score = self._calculate_support_score(customer_data)
        financial_score = self._calculate_financial_score(customer_data)
        relationship_score = self._calculate_relationship_score(customer_data)
        
        category_scores = {
            "engagement": engagement_score,
            "product_usage": product_usage_score,
            "support": support_score,
            "financial": financial_score,
            "relationship": relationship_score
        }
        
        # Calcular score general (promedio ponderado)
        weights = {
            "engagement": 0.25,
            "product_usage": 0.25,
            "support": 0.15,
            "financial": 0.20,
            "relationship": 0.15
        }
        
        overall_score = sum(
            category_scores[cat] * weights[cat]
            for cat in category_scores
        )
        
        # Determinar status
        status = self._determine_status(overall_score, category_scores)
        
        # Identificar factores de riesgo
        risk_factors = self._identify_risk_factors(category_scores, customer_data)
        
        # Identificar oportunidades
        opportunities = self._identify_opportunities(category_scores, customer_data)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            overall_score,
            status,
            category_scores,
            risk_factors,
            opportunities
        )
        
        # Calcular tendencia
        trend = self._calculate_trend(customer_id, overall_score)
        
        return HealthScore(
            customer_id=customer_id,
            overall_score=round(overall_score, 2),
            status=status,
            category_scores={k: round(v, 2) for k, v in category_scores.items()},
            risk_factors=risk_factors,
            opportunities=opportunities,
            recommendations=recommendations,
            trend=trend,
            last_updated=datetime.now().isoformat()
        )
    
    def _calculate_engagement_score(self, customer_data: Dict[str, Any]) -> float:
        """Calcula score de engagement (0-100)"""
        score = 50.0  # Base
        
        # Login frequency
        login_frequency = customer_data.get("login_frequency", 0)
        if login_frequency >= 20:  # Diario
            score += 20
        elif login_frequency >= 10:  # 3-4 veces/semana
            score += 15
        elif login_frequency >= 5:  # Semanal
            score += 10
        elif login_frequency >= 1:  # Mensual
            score += 5
        
        # Email opens
        email_opens = customer_data.get("email_opens_30d", 0)
        if email_opens >= 10:
            score += 15
        elif email_opens >= 5:
            score += 10
        elif email_opens >= 1:
            score += 5
        
        # Feature usage
        features_used = customer_data.get("features_used", 0)
        total_features = customer_data.get("total_features", 10)
        feature_usage_rate = features_used / total_features if total_features > 0 else 0
        score += feature_usage_rate * 15
        
        return min(100, max(0, score))
    
    def _calculate_product_usage_score(self, customer_data: Dict[str, Any]) -> float:
        """Calcula score de uso del producto (0-100)"""
        score = 50.0
        
        # Active days
        active_days_30d = customer_data.get("active_days_30d", 0)
        if active_days_30d >= 20:
            score += 25
        elif active_days_30d >= 10:
            score += 15
        elif active_days_30d >= 5:
            score += 10
        
        # Session duration
        avg_session_duration = customer_data.get("avg_session_duration_minutes", 0)
        if avg_session_duration >= 30:
            score += 15
        elif avg_session_duration >= 15:
            score += 10
        elif avg_session_duration >= 5:
            score += 5
        
        # Adoption rate
        adoption_rate = customer_data.get("adoption_rate", 0)
        score += adoption_rate * 10
        
        return min(100, max(0, score))
    
    def _calculate_support_score(self, customer_data: Dict[str, Any]) -> float:
        """Calcula score de soporte (0-100)"""
        score = 100.0  # Empieza alto
        
        # Support tickets (más tickets = peor)
        support_tickets = customer_data.get("support_tickets_30d", 0)
        if support_tickets >= 5:
            score -= 30
        elif support_tickets >= 3:
            score -= 20
        elif support_tickets >= 1:
            score -= 10
        
        # Ticket resolution time
        avg_resolution_hours = customer_data.get("avg_ticket_resolution_hours", 0)
        if avg_resolution_hours > 48:
            score -= 20
        elif avg_resolution_hours > 24:
            score -= 10
        
        # NPS/CSAT
        nps = customer_data.get("nps_score", 50)
        score += (nps - 50) * 0.3
        
        return min(100, max(0, score))
    
    def _calculate_financial_score(self, customer_data: Dict[str, Any]) -> float:
        """Calcula score financiero (0-100)"""
        score = 50.0
        
        # MRR/ARR
        mrr = customer_data.get("mrr", 0)
        if mrr >= 1000:
            score += 25
        elif mrr >= 500:
            score += 15
        elif mrr >= 100:
            score += 10
        
        # Payment history
        payment_status = customer_data.get("payment_status", "current")
        if payment_status == "overdue":
            score -= 30
        elif payment_status == "pending":
            score -= 10
        elif payment_status == "current":
            score += 10
        
        # Contract value
        contract_value = customer_data.get("contract_value", 0)
        if contract_value >= 10000:
            score += 15
        elif contract_value >= 5000:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_relationship_score(self, customer_data: Dict[str, Any]) -> float:
        """Calcula score de relación (0-100)"""
        score = 50.0
        
        # Tenure
        tenure_months = customer_data.get("tenure_months", 0)
        if tenure_months >= 24:
            score += 20
        elif tenure_months >= 12:
            score += 15
        elif tenure_months >= 6:
            score += 10
        
        # Referrals
        referrals = customer_data.get("referrals", 0)
        score += min(20, referrals * 5)
        
        # Reviews/Testimonials
        reviews = customer_data.get("reviews_submitted", 0)
        score += min(10, reviews * 5)
        
        # Account manager interactions
        am_interactions = customer_data.get("am_interactions_30d", 0)
        if am_interactions >= 3:
            score += 10
        elif am_interactions >= 1:
            score += 5
        
        return min(100, max(0, score))
    
    def _determine_status(
        self,
        overall_score: float,
        category_scores: Dict[str, float]
    ) -> HealthStatus:
        """Determina el status de salud"""
        if overall_score >= 80:
            return HealthStatus.CHAMPION
        elif overall_score >= 60:
            return HealthStatus.HEALTHY
        elif overall_score >= 40:
            # Verificar si hay categorías críticas
            critical_categories = [
                k for k, v in category_scores.items()
                if v < 30
            ]
            if critical_categories:
                return HealthStatus.AT_RISK
            return HealthStatus.STABLE
        elif overall_score >= 20:
            return HealthStatus.AT_RISK
        else:
            return HealthStatus.CRITICAL
    
    def _identify_risk_factors(
        self,
        category_scores: Dict[str, float],
        customer_data: Dict[str, Any]
    ) -> List[str]:
        """Identifica factores de riesgo"""
        risks = []
        
        if category_scores["engagement"] < 40:
            risks.append("Bajo engagement - cliente no está usando el producto activamente")
        
        if category_scores["product_usage"] < 40:
            risks.append("Bajo uso del producto - no está adoptando funcionalidades")
        
        if category_scores["support"] < 50:
            risks.append("Problemas de soporte - múltiples tickets o resolución lenta")
        
        if category_scores["financial"] < 40:
            risks.append("Riesgo financiero - pagos atrasados o bajo valor")
        
        if category_scores["relationship"] < 40:
            risks.append("Relación débil - poco tiempo como cliente o sin referidos")
        
        # Riesgos específicos
        if customer_data.get("days_since_last_login", 0) > 30:
            risks.append("Sin login en más de 30 días")
        
        if customer_data.get("payment_status") == "overdue":
            risks.append("Pago atrasado")
        
        return risks
    
    def _identify_opportunities(
        self,
        category_scores: Dict[str, float],
        customer_data: Dict[str, Any]
    ) -> List[str]:
        """Identifica oportunidades de mejora"""
        opportunities = []
        
        if category_scores["engagement"] >= 70 and category_scores["relationship"] < 60:
            opportunities.append("Alto engagement - oportunidad para solicitar referido")
        
        if category_scores["product_usage"] >= 70 and customer_data.get("mrr", 0) < 500:
            opportunities.append("Alto uso - oportunidad de upsell")
        
        if category_scores["financial"] >= 70 and category_scores["engagement"] < 60:
            opportunities.append("Alto valor - oportunidad de aumentar engagement")
        
        if customer_data.get("features_used", 0) < customer_data.get("total_features", 10) * 0.5:
            opportunities.append("Baja adopción de features - oportunidad de onboarding")
        
        return opportunities
    
    def _generate_recommendations(
        self,
        overall_score: float,
        status: HealthStatus,
        category_scores: Dict[str, float],
        risk_factors: List[str],
        opportunities: List[str]
    ) -> List[str]:
        """Genera recomendaciones basadas en el score"""
        recommendations = []
        
        if status == HealthStatus.CRITICAL:
            recommendations.append("ACCIÓN INMEDIATA: Contactar cliente para entender problemas")
            recommendations.append("Ofrecer soporte prioritario o descuento")
        
        if status == HealthStatus.AT_RISK:
            recommendations.append("Programar llamada de éxito del cliente")
            recommendations.append("Revisar y resolver factores de riesgo identificados")
        
        # Recomendaciones por categoría
        lowest_category = min(category_scores.items(), key=lambda x: x[1])
        if lowest_category[1] < 50:
            recommendations.append(f"Enfocarse en mejorar {lowest_category[0]} (score: {lowest_category[1]:.1f})")
        
        # Recomendaciones de oportunidades
        for opp in opportunities[:2]:  # Top 2
            recommendations.append(f"Oportunidad: {opp}")
        
        return recommendations
    
    def _calculate_trend(self, customer_id: str, current_score: float) -> str:
        """Calcula tendencia del score (simplificado)"""
        # En producción, comparar con scores históricos
        # Por ahora, simulado
        return "stable"
    
    def _get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Obtiene datos del cliente (simulado)"""
        # En producción, obtener de DB/CDP
        return {
            "login_frequency": 15,
            "email_opens_30d": 8,
            "features_used": 5,
            "total_features": 10,
            "active_days_30d": 12,
            "avg_session_duration_minutes": 20,
            "adoption_rate": 0.6,
            "support_tickets_30d": 1,
            "avg_ticket_resolution_hours": 12,
            "nps_score": 70,
            "mrr": 500,
            "payment_status": "current",
            "contract_value": 6000,
            "tenure_months": 18,
            "referrals": 1,
            "reviews_submitted": 1,
            "am_interactions_30d": 2,
            "days_since_last_login": 5
        }
    
    def batch_calculate_scores(
        self,
        customer_ids: List[str]
    ) -> List[HealthScore]:
        """Calcula scores para múltiples clientes"""
        scores = []
        for customer_id in customer_ids:
            score = self.calculate_health_score(customer_id)
            scores.append(score)
        return scores


def main():
    """Ejemplo de uso"""
    scoring = AdvancedHealthScoring(
        api_base_url="https://api.example.com",
        api_key="your_api_key"
    )
    
    # Calcular score para un cliente
    health_score = scoring.calculate_health_score("customer_123")
    
    print(f"Customer: {health_score.customer_id}")
    print(f"Overall Score: {health_score.overall_score}/100")
    print(f"Status: {health_score.status.value}")
    print(f"\nCategory Scores:")
    for category, score in health_score.category_scores.items():
        print(f"  {category}: {score}/100")
    print(f"\nRisk Factors: {health_score.risk_factors}")
    print(f"\nOpportunities: {health_score.opportunities}")
    print(f"\nRecommendations:")
    for rec in health_score.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()










