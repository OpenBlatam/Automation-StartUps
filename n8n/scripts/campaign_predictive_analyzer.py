#!/usr/bin/env python3
"""
Campaign Predictive Analyzer
Análisis predictivo avanzado para campañas de lanzamiento
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics
from collections import defaultdict


class CampaignPredictiveAnalyzer:
    """
    Analizador predictivo para campañas de lanzamiento
    Predice engagement, conversiones y ROI antes y durante la campaña
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def predict_pre_campaign(
        self,
        product_config: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Predice resultados ANTES de lanzar la campaña
        
        Args:
            product_config: Configuración del producto
            historical_data: Datos históricos de campañas anteriores
        
        Returns:
            Dict con predicciones y recomendaciones
        """
        # Análisis de factores clave
        factors = self._analyze_campaign_factors(product_config, historical_data)
        
        # Predicción de engagement
        engagement_prediction = self._predict_engagement(factors, historical_data)
        
        # Predicción de conversiones
        conversion_prediction = self._predict_conversions(factors, engagement_prediction)
        
        # Predicción de ROI
        roi_prediction = self._predict_roi(factors, conversion_prediction)
        
        # Recomendaciones de optimización
        recommendations = self._generate_recommendations(factors, engagement_prediction)
        
        return {
            "prediction": {
                "engagement": engagement_prediction,
                "conversions": conversion_prediction,
                "roi": roi_prediction,
                "confidence": self._calculate_confidence(historical_data)
            },
            "factors": factors,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def predict_during_campaign(
        self,
        campaign_id: str,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Predice resultados DURANTE la campaña basado en métricas actuales
        
        Args:
            campaign_id: ID de la campaña
            current_metrics: Métricas actuales de la campaña
            historical_data: Datos históricos
        
        Returns:
            Dict con predicciones actualizadas y ajustes recomendados
        """
        # Análisis de tendencias actuales
        trends = self._analyze_current_trends(current_metrics)
        
        # Predicción de resultados finales
        final_prediction = self._extrapolate_final_results(current_metrics, trends, historical_data)
        
        # Detección de anomalías
        anomalies = self._detect_anomalies(current_metrics, historical_data)
        
        # Recomendaciones de ajuste
        adjustments = self._recommend_adjustments(current_metrics, trends, final_prediction)
        
        return {
            "campaignId": campaign_id,
            "currentMetrics": current_metrics,
            "trends": trends,
            "finalPrediction": final_prediction,
            "anomalies": anomalies,
            "adjustments": adjustments,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_campaign_factors(
        self,
        product_config: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Analiza factores clave de la campaña"""
        factors = {
            "product": {
                "name": product_config.get("name", ""),
                "benefitsCount": len(product_config.get("benefits", [])),
                "discountPercentage": product_config.get("discount_percentage", 0),
                "urgencyLevel": "high" if product_config.get("discount_percentage", 0) > 20 else "medium"
            },
            "platforms": {
                "count": len(product_config.get("platforms", [])),
                "platforms": product_config.get("platforms", []),
                "diversity": self._calculate_platform_diversity(product_config.get("platforms", []))
            },
            "content": {
                "hashtagsCount": len(product_config.get("hashtags", [])),
                "hashtagQuality": self._assess_hashtag_quality(product_config.get("hashtags", [])),
                "ctaStrength": self._assess_cta_strength(product_config.get("cta_link", ""))
            },
            "timing": {
                "dayOfWeek": datetime.now().weekday(),
                "hour": datetime.now().hour,
                "optimalTiming": self._calculate_optimal_timing(historical_data)
            }
        }
        
        # Score general
        factors["overallScore"] = self._calculate_overall_score(factors)
        
        return factors
    
    def _predict_engagement(
        self,
        factors: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Predice engagement esperado"""
        base_engagement_rate = 0.05  # 5% base
        
        # Ajustes basados en factores
        adjustments = {
            "platform_diversity": factors["platforms"]["diversity"] * 0.02,
            "hashtag_quality": factors["content"]["hashtagQuality"] * 0.015,
            "discount": min(factors["product"]["discountPercentage"] / 100 * 0.03, 0.05),
            "benefits": min(factors["product"]["benefitsCount"] / 10 * 0.01, 0.02)
        }
        
        predicted_rate = base_engagement_rate + sum(adjustments.values())
        predicted_rate = min(predicted_rate, 0.15)  # Cap at 15%
        
        # Predicción por plataforma
        platform_predictions = {}
        for platform in factors["platforms"]["platforms"]:
            platform_base = {
                "instagram": 0.06,
                "facebook": 0.04,
                "linkedin": 0.03,
                "tiktok": 0.08,
                "twitter": 0.02
            }.get(platform.lower(), 0.04)
            
            platform_predictions[platform] = {
                "engagementRate": platform_base * (1 + predicted_rate / base_engagement_rate - 1),
                "expectedReach": self._estimate_reach(platform, historical_data),
                "expectedLikes": 0,  # Calculado después
                "expectedComments": 0,
                "expectedShares": 0
            }
        
        return {
            "overallEngagementRate": predicted_rate,
            "byPlatform": platform_predictions,
            "confidence": self._calculate_confidence(historical_data)
        }
    
    def _predict_conversions(
        self,
        factors: Dict[str, Any],
        engagement_prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predice conversiones esperadas"""
        # Tasa de conversión base (engagement → lead)
        base_conversion_rate = 0.10  # 10% de engagement se convierte en lead
        
        # Ajustes
        discount_boost = min(factors["product"]["discountPercentage"] / 100 * 0.05, 0.10)
        urgency_boost = 0.05 if factors["product"]["urgencyLevel"] == "high" else 0.02
        
        conversion_rate = base_conversion_rate + discount_boost + urgency_boost
        conversion_rate = min(conversion_rate, 0.30)  # Cap at 30%
        
        # Calcular leads esperados
        total_expected_reach = sum(
            p["expectedReach"] for p in engagement_prediction["byPlatform"].values()
        )
        
        expected_leads = int(total_expected_reach * engagement_prediction["overallEngagementRate"] * conversion_rate)
        
        # Tasa de conversión lead → venta
        lead_to_sale_rate = 0.15  # 15% de leads se convierten en ventas
        
        expected_sales = int(expected_leads * lead_to_sale_rate)
        
        return {
            "expectedLeads": expected_leads,
            "expectedSales": expected_sales,
            "conversionRate": conversion_rate,
            "leadToSaleRate": lead_to_sale_rate,
            "confidence": engagement_prediction["confidence"] * 0.9  # Menor confianza
        }
    
    def _predict_roi(
        self,
        factors: Dict[str, Any],
        conversion_prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predice ROI esperado"""
        # Asumir precio promedio (debería venir de product_config)
        avg_price = 100  # $100 promedio
        discount = factors["product"]["discountPercentage"] / 100
        discounted_price = avg_price * (1 - discount)
        
        # Revenue esperado
        expected_revenue = conversion_prediction["expectedSales"] * discounted_price
        
        # Costos estimados (debería venir de configuración)
        estimated_costs = {
            "content_creation": 500,
            "advertising": 200,
            "platform_fees": 100,
            "automation": 50
        }
        total_costs = sum(estimated_costs.values())
        
        # ROI
        profit = expected_revenue - total_costs
        roi_percentage = (profit / total_costs * 100) if total_costs > 0 else 0
        
        return {
            "expectedRevenue": expected_revenue,
            "estimatedCosts": total_costs,
            "expectedProfit": profit,
            "roiPercentage": roi_percentage,
            "breakEvenSales": int(total_costs / discounted_price) if discounted_price > 0 else 0,
            "confidence": conversion_prediction["confidence"] * 0.85
        }
    
    def _generate_recommendations(
        self,
        factors: Dict[str, Any],
        engagement_prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Recomendación de plataformas
        if factors["platforms"]["count"] < 3:
            recommendations.append({
                "type": "platform",
                "priority": "high",
                "message": "Agregar más plataformas puede aumentar el alcance en 30-50%",
                "action": "Considerar agregar TikTok o Twitter"
            })
        
        # Recomendación de hashtags
        if factors["content"]["hashtagQuality"] < 0.7:
            recommendations.append({
                "type": "hashtags",
                "priority": "medium",
                "message": "Mejorar calidad de hashtags puede aumentar engagement en 15-25%",
                "action": "Usar hashtags más específicos y relevantes"
            })
        
        # Recomendación de descuento
        if factors["product"]["discountPercentage"] < 15:
            recommendations.append({
                "type": "discount",
                "priority": "medium",
                "message": "Aumentar descuento a 20%+ puede aumentar conversiones en 20-30%",
                "action": "Considerar aumentar descuento si es viable"
            })
        
        # Recomendación de timing
        optimal_timing = factors["timing"]["optimalTiming"]
        current_hour = datetime.now().hour
        if abs(current_hour - optimal_timing["hour"]) > 2:
            recommendations.append({
                "type": "timing",
                "priority": "low",
                "message": f"Publicar a las {optimal_timing['hour']}:00 puede aumentar engagement en 10-15%",
                "action": f"Programar publicación para las {optimal_timing['hour']}:00"
            })
        
        return recommendations
    
    def _analyze_current_trends(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza tendencias actuales de la campaña"""
        # Esto sería más complejo con datos reales
        return {
            "engagementTrend": "increasing" if current_metrics.get("engagementRate", 0) > 0.05 else "stable",
            "conversionTrend": "increasing" if current_metrics.get("conversionRate", 0) > 0.10 else "stable",
            "velocity": "high" if current_metrics.get("leadsPerHour", 0) > 5 else "normal"
        }
    
    def _extrapolate_final_results(
        self,
        current_metrics: Dict[str, Any],
        trends: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Extrapola resultados finales basado en métricas actuales"""
        # Cálculo simplificado
        days_elapsed = current_metrics.get("daysElapsed", 1)
        total_days = 3  # Campaña de 3 días
        
        if days_elapsed == 0:
            return {"error": "No hay datos suficientes"}
        
        # Proyección lineal (mejoraría con ML)
        projection_factor = total_days / days_elapsed
        
        return {
            "projectedReach": int(current_metrics.get("totalReach", 0) * projection_factor),
            "projectedEngagements": int(current_metrics.get("totalEngagements", 0) * projection_factor),
            "projectedLeads": int(current_metrics.get("totalLeads", 0) * projection_factor),
            "projectedSales": int(current_metrics.get("totalSales", 0) * projection_factor),
            "projectedRevenue": current_metrics.get("totalRevenue", 0) * projection_factor,
            "confidence": 0.7 if days_elapsed >= 2 else 0.5
        }
    
    def _detect_anomalies(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> List[Dict[str, Any]]:
        """Detecta anomalías en las métricas"""
        anomalies = []
        
        # Anomalía: Engagement muy bajo
        if current_metrics.get("engagementRate", 0) < 0.02:
            anomalies.append({
                "type": "low_engagement",
                "severity": "high",
                "message": "Engagement rate está muy por debajo del esperado",
                "suggestedAction": "Revisar contenido y hashtags"
            })
        
        # Anomalía: Conversión muy baja
        if current_metrics.get("conversionRate", 0) < 0.05:
            anomalies.append({
                "type": "low_conversion",
                "severity": "medium",
                "message": "Tasa de conversión está baja",
                "suggestedAction": "Revisar CTA y oferta"
            })
        
        return anomalies
    
    def _recommend_adjustments(
        self,
        current_metrics: Dict[str, Any],
        trends: Dict[str, Any],
        final_prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recomienda ajustes durante la campaña"""
        adjustments = []
        
        # Si engagement está bajo
        if current_metrics.get("engagementRate", 0) < 0.03:
            adjustments.append({
                "type": "content",
                "action": "Publicar contenido adicional de apoyo",
                "priority": "high"
            })
        
        # Si conversión está baja
        if current_metrics.get("conversionRate", 0) < 0.08:
            adjustments.append({
                "type": "offer",
                "action": "Considerar aumentar descuento o agregar bonus",
                "priority": "medium"
            })
        
        return adjustments
    
    # Helper methods
    def _calculate_platform_diversity(self, platforms: List[str]) -> float:
        """Calcula diversidad de plataformas (0-1)"""
        unique_platforms = len(set(platforms))
        max_platforms = 5  # Instagram, Facebook, LinkedIn, TikTok, Twitter
        return min(unique_platforms / max_platforms, 1.0)
    
    def _assess_hashtag_quality(self, hashtags: List[str]) -> float:
        """Evalúa calidad de hashtags (0-1)"""
        if not hashtags:
            return 0.0
        
        # Factores: cantidad, especificidad, relevancia
        count_score = min(len(hashtags) / 20, 1.0)  # Óptimo: 15-20 hashtags
        specificity_score = 0.7  # Simplificado
        relevance_score = 0.8  # Simplificado
        
        return (count_score + specificity_score + relevance_score) / 3
    
    def _assess_cta_strength(self, cta_link: str) -> float:
        """Evalúa fuerza del CTA (0-1)"""
        if not cta_link or cta_link == "":
            return 0.0
        
        # Factores: link válido, dominio confiable, etc.
        return 0.8 if cta_link.startswith("http") else 0.5
    
    def _calculate_optimal_timing(self, historical_data: Optional[List[Dict]]) -> Dict[str, Any]:
        """Calcula timing óptimo basado en datos históricos"""
        # Default: 9 AM en día laboral
        return {
            "hour": 9,
            "dayOfWeek": 0,  # Lunes
            "confidence": 0.6
        }
    
    def _calculate_overall_score(self, factors: Dict[str, Any]) -> float:
        """Calcula score general de la campaña (0-100)"""
        scores = {
            "platforms": factors["platforms"]["diversity"] * 30,
            "content": factors["content"]["hashtagQuality"] * 30,
            "product": min(factors["product"]["discountPercentage"] / 30 * 20, 20),
            "timing": 0.7 * 20  # Simplificado
        }
        
        return sum(scores.values())
    
    def _estimate_reach(self, platform: str, historical_data: Optional[List[Dict]]) -> int:
        """Estima alcance por plataforma"""
        # Defaults basados en promedios de la industria
        defaults = {
            "instagram": 5000,
            "facebook": 3000,
            "linkedin": 2000,
            "tiktok": 8000,
            "twitter": 1500
        }
        
        return defaults.get(platform.lower(), 2000)
    
    def _calculate_confidence(self, historical_data: Optional[List[Dict]]) -> float:
        """Calcula nivel de confianza de las predicciones"""
        if not historical_data or len(historical_data) < 5:
            return 0.5  # Baja confianza sin datos
        
        if len(historical_data) >= 20:
            return 0.9  # Alta confianza con muchos datos
        
        return 0.5 + (len(historical_data) / 20 * 0.4)  # Escala lineal


def main():
    """Ejemplo de uso"""
    analyzer = CampaignPredictiveAnalyzer(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Configuración del producto
    product_config = {
        "name": "Mi Nuevo Producto",
        "benefits": ["Beneficio 1", "Beneficio 2", "Beneficio 3"],
        "discount_percentage": 25,
        "platforms": ["instagram", "facebook", "linkedin"],
        "hashtags": ["#Lanzamiento", "#NuevoProducto", "#Oferta"],
        "cta_link": "https://yoursite.com/launch"
    }
    
    # Predicción pre-campaña
    print("=== Predicción Pre-Campaña ===")
    prediction = analyzer.predict_pre_campaign(product_config)
    print(json.dumps(prediction, indent=2))
    
    # Predicción durante campaña
    print("\n=== Predicción Durante Campaña ===")
    current_metrics = {
        "totalReach": 5000,
        "totalEngagements": 250,
        "totalLeads": 30,
        "totalSales": 5,
        "totalRevenue": 500,
        "engagementRate": 0.05,
        "conversionRate": 0.10,
        "daysElapsed": 1,
        "leadsPerHour": 3
    }
    
    during_prediction = analyzer.predict_during_campaign(
        campaign_id="campaign_123",
        current_metrics=current_metrics
    )
    print(json.dumps(during_prediction, indent=2))


if __name__ == "__main__":
    main()



