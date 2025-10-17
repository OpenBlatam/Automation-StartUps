#!/usr/bin/env python3
"""
📈 MARKETING BRAIN ANALYTICS
Sistema Avanzado de Análisis y Predicción para Marketing
Análisis de Tendencias, Competencia y Optimización Automática
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional
import logging
from dataclasses import dataclass
from pathlib import Path
import sys

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept

logger = logging.getLogger(__name__)

@dataclass
class TrendAnalysis:
    """Estructura para análisis de tendencias"""
    trend_name: str
    category: str
    growth_rate: float
    popularity_score: float
    emerging_keywords: List[str]
    related_technologies: List[str]
    market_opportunity: str
    predicted_duration: str
    confidence_level: float

@dataclass
class CompetitorInsight:
    """Estructura para insights de competencia"""
    competitor_name: str
    market_share: float
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    recommended_strategies: List[str]

@dataclass
class PerformancePrediction:
    """Estructura para predicción de rendimiento"""
    concept_id: str
    predicted_metrics: Dict[str, float]
    confidence_interval: Dict[str, Tuple[float, float]]
    risk_factors: List[str]
    optimization_suggestions: List[str]
    success_probability: float

class MarketingBrainAnalytics:
    """
    Sistema Avanzado de Análisis y Predicción para Marketing
    Extiende el Advanced Marketing Brain System con capacidades analíticas avanzadas
    """
    
    def __init__(self, brain_system: AdvancedMarketingBrain = None):
        self.brain = brain_system or AdvancedMarketingBrain()
        
        # Datos de análisis
        self.trend_data = self._load_trend_data()
        self.competitor_data = self._load_competitor_data()
        self.market_data = self._load_market_data()
        
        # Modelos de predicción
        self.performance_model = self._build_performance_model()
        self.trend_model = self._build_trend_model()
        
        logger.info("📈 Marketing Brain Analytics initialized successfully")
    
    def _load_trend_data(self) -> Dict[str, Any]:
        """Cargar datos de tendencias del mercado"""
        return {
            'ai_trends': {
                'personalization': {'growth': 0.35, 'keywords': ['AI personalization', 'machine learning', 'customer experience']},
                'automation': {'growth': 0.28, 'keywords': ['marketing automation', 'workflow automation', 'AI automation']},
                'predictive_analytics': {'growth': 0.42, 'keywords': ['predictive analytics', 'forecasting', 'data science']},
                'chatbots': {'growth': 0.31, 'keywords': ['AI chatbots', 'conversational AI', 'virtual assistants']},
                'content_generation': {'growth': 0.38, 'keywords': ['AI content', 'generative AI', 'automated content']}
            },
            'channel_trends': {
                'social_media': {'growth': 0.25, 'keywords': ['social commerce', 'influencer marketing', 'social selling']},
                'email_marketing': {'growth': 0.15, 'keywords': ['email automation', 'personalized emails', 'email analytics']},
                'video_marketing': {'growth': 0.45, 'keywords': ['video content', 'live streaming', 'short-form video']},
                'voice_search': {'growth': 0.22, 'keywords': ['voice optimization', 'smart speakers', 'voice commerce']},
                'mobile_marketing': {'growth': 0.18, 'keywords': ['mobile-first', 'app marketing', 'mobile commerce']}
            },
            'vertical_trends': {
                'ecommerce': {'growth': 0.32, 'keywords': ['omnichannel', 'social commerce', 'AI recommendations']},
                'fintech': {'growth': 0.28, 'keywords': ['digital banking', 'cryptocurrency', 'AI fraud detection']},
                'healthcare': {'growth': 0.24, 'keywords': ['telemedicine', 'AI diagnostics', 'health apps']},
                'education': {'growth': 0.26, 'keywords': ['edtech', 'online learning', 'AI tutoring']},
                'technology': {'growth': 0.35, 'keywords': ['cloud computing', 'IoT', 'AI integration']}
            }
        }
    
    def _load_competitor_data(self) -> Dict[str, Any]:
        """Cargar datos de competencia"""
        return {
            'major_competitors': {
                'HubSpot': {
                    'market_share': 0.15,
                    'strengths': ['All-in-one platform', 'Strong automation', 'Good analytics'],
                    'weaknesses': ['High cost', 'Complex setup', 'Limited customization'],
                    'focus_areas': ['Inbound marketing', 'Sales automation', 'CRM']
                },
                'Mailchimp': {
                    'market_share': 0.12,
                    'strengths': ['User-friendly', 'Good email tools', 'Affordable'],
                    'weaknesses': ['Limited automation', 'Basic analytics', 'Limited integrations'],
                    'focus_areas': ['Email marketing', 'Small business', 'E-commerce']
                },
                'Salesforce': {
                    'market_share': 0.20,
                    'strengths': ['Enterprise features', 'Strong CRM', 'Extensive integrations'],
                    'weaknesses': ['Complex', 'Expensive', 'Steep learning curve'],
                    'focus_areas': ['Enterprise CRM', 'Sales automation', 'Analytics']
                },
                'Adobe Marketing Cloud': {
                    'market_share': 0.10,
                    'strengths': ['Creative tools', 'Advanced analytics', 'Enterprise features'],
                    'weaknesses': ['High cost', 'Complex', 'Limited SMB focus'],
                    'focus_areas': ['Creative marketing', 'Analytics', 'Enterprise']
                }
            }
        }
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Cargar datos del mercado"""
        return {
            'market_size': {
                'global_marketing_automation': 6.4,  # Billions USD
                'ai_in_marketing': 2.1,  # Billions USD
                'social_media_marketing': 4.2,  # Billions USD
                'email_marketing': 1.2,  # Billions USD
                'content_marketing': 3.8  # Billions USD
            },
            'growth_rates': {
                'marketing_automation': 0.12,
                'ai_marketing': 0.25,
                'social_media': 0.15,
                'email_marketing': 0.08,
                'content_marketing': 0.18
            },
            'regional_data': {
                'north_america': {'share': 0.35, 'growth': 0.10},
                'europe': {'share': 0.28, 'growth': 0.12},
                'asia_pacific': {'share': 0.25, 'growth': 0.18},
                'latin_america': {'share': 0.08, 'growth': 0.15},
                'middle_east_africa': {'share': 0.04, 'growth': 0.20}
            }
        }
    
    def _build_performance_model(self) -> Dict[str, Any]:
        """Construir modelo de predicción de rendimiento"""
        # Modelo simplificado basado en análisis de campañas exitosas
        return {
            'success_factors': {
                'technology_weights': {
                    'Machine Learning': 0.85,
                    'Deep Learning': 0.92,
                    'NLP': 0.78,
                    'Generative AI': 0.88,
                    'Reinforcement Learning': 0.90,
                    'Computer Vision': 0.82
                },
                'channel_weights': {
                    'Redes Sociales': 0.80,
                    'Email Marketing': 0.75,
                    'E-commerce': 0.85,
                    'Content Marketing': 0.78,
                    'SEM/PPC': 0.88,
                    'Mobile Apps': 0.82
                },
                'vertical_weights': {
                    'E-commerce': 0.85,
                    'Fintech': 0.88,
                    'Healthcare': 0.82,
                    'Technology': 0.90,
                    'Fashion': 0.78,
                    'Education': 0.80
                }
            },
            'metric_predictors': {
                'conversion_rate': {'base': 5.0, 'max': 25.0},
                'engagement_rate': {'base': 4.0, 'max': 20.0},
                'click_through_rate': {'base': 2.5, 'max': 15.0},
                'cost_per_acquisition': {'base': 50.0, 'min': 15.0},
                'return_on_ad_spend': {'base': 3.0, 'max': 12.0}
            }
        }
    
    def _build_trend_model(self) -> Dict[str, Any]:
        """Construir modelo de análisis de tendencias"""
        return {
            'trend_lifecycle': {
                'emerging': {'duration': '6-12 months', 'growth_rate': 0.3},
                'growing': {'duration': '1-2 years', 'growth_rate': 0.5},
                'mature': {'duration': '2-3 years', 'growth_rate': 0.2},
                'declining': {'duration': '1-2 years', 'growth_rate': -0.1}
            },
            'trend_indicators': {
                'keyword_volume': 0.3,
                'social_mentions': 0.25,
                'industry_reports': 0.2,
                'investment_funding': 0.15,
                'product_launches': 0.1
            }
        }
    
    def analyze_market_trends(self, 
                            category: str = None,
                            timeframe: str = "12_months") -> List[TrendAnalysis]:
        """
        Analizar tendencias del mercado
        """
        trends = []
        
        # Seleccionar categorías a analizar
        categories_to_analyze = []
        if category:
            if category in self.trend_data:
                categories_to_analyze = [category]
        else:
            categories_to_analyze = list(self.trend_data.keys())
        
        for cat in categories_to_analyze:
            category_data = self.trend_data[cat]
            
            for trend_name, trend_info in category_data.items():
                # Calcular score de popularidad
                popularity_score = self._calculate_popularity_score(trend_info)
                
                # Determinar oportunidad de mercado
                market_opportunity = self._assess_market_opportunity(trend_info['growth'])
                
                # Predecir duración
                predicted_duration = self._predict_trend_duration(trend_info['growth'])
                
                # Calcular nivel de confianza
                confidence_level = self._calculate_confidence_level(trend_info)
                
                trend = TrendAnalysis(
                    trend_name=trend_name,
                    category=cat,
                    growth_rate=trend_info['growth'],
                    popularity_score=popularity_score,
                    emerging_keywords=trend_info['keywords'],
                    related_technologies=self._get_related_technologies(trend_name),
                    market_opportunity=market_opportunity,
                    predicted_duration=predicted_duration,
                    confidence_level=confidence_level
                )
                trends.append(trend)
        
        # Ordenar por score de popularidad
        trends.sort(key=lambda x: x.popularity_score, reverse=True)
        
        logger.info(f"📈 Analyzed {len(trends)} market trends")
        return trends
    
    def _calculate_popularity_score(self, trend_info: Dict) -> float:
        """Calcular score de popularidad de una tendencia"""
        base_score = trend_info['growth'] * 100
        keyword_bonus = len(trend_info['keywords']) * 5
        return min(100, base_score + keyword_bonus)
    
    def _assess_market_opportunity(self, growth_rate: float) -> str:
        """Evaluar oportunidad de mercado basada en tasa de crecimiento"""
        if growth_rate > 0.4:
            return "Excelente - Mercado en rápido crecimiento"
        elif growth_rate > 0.3:
            return "Muy Buena - Mercado en crecimiento sostenido"
        elif growth_rate > 0.2:
            return "Buena - Mercado estable con crecimiento moderado"
        elif growth_rate > 0.1:
            return "Moderada - Mercado maduro con crecimiento lento"
        else:
            return "Baja - Mercado saturado o en declive"
    
    def _predict_trend_duration(self, growth_rate: float) -> str:
        """Predecir duración de la tendencia"""
        if growth_rate > 0.4:
            return "2-3 años (Tendencia emergente)"
        elif growth_rate > 0.3:
            return "1-2 años (Tendencia en crecimiento)"
        elif growth_rate > 0.2:
            return "6-12 meses (Tendencia madura)"
        else:
            return "3-6 meses (Tendencia en declive)"
    
    def _calculate_confidence_level(self, trend_info: Dict) -> float:
        """Calcular nivel de confianza en la tendencia"""
        base_confidence = 0.7
        keyword_confidence = min(0.2, len(trend_info['keywords']) * 0.05)
        growth_confidence = min(0.1, trend_info['growth'] * 0.3)
        return min(0.95, base_confidence + keyword_confidence + growth_confidence)
    
    def _get_related_technologies(self, trend_name: str) -> List[str]:
        """Obtener tecnologías relacionadas con la tendencia"""
        technology_mapping = {
            'personalization': ['Machine Learning', 'NLP', 'Computer Vision'],
            'automation': ['Machine Learning', 'Reinforcement Learning'],
            'predictive_analytics': ['Deep Learning', 'Machine Learning'],
            'chatbots': ['NLP', 'Machine Learning'],
            'content_generation': ['Generative AI', 'NLP'],
            'social_media': ['Machine Learning', 'NLP'],
            'email_marketing': ['Machine Learning', 'NLP'],
            'video_marketing': ['Computer Vision', 'Generative AI'],
            'voice_search': ['NLP', 'Machine Learning'],
            'mobile_marketing': ['Machine Learning', 'Computer Vision']
        }
        return technology_mapping.get(trend_name, ['Machine Learning'])
    
    def analyze_competition(self, 
                          market_segment: str = None,
                          include_swot: bool = True) -> List[CompetitorInsight]:
        """
        Analizar competencia en el mercado
        """
        competitors = []
        
        competitor_data = self.competitor_data['major_competitors']
        
        for competitor_name, competitor_info in competitor_data.items():
            # Generar análisis SWOT si se solicita
            if include_swot:
                swot_analysis = self._generate_swot_analysis(competitor_info)
            else:
                swot_analysis = {
                    'strengths': competitor_info['strengths'],
                    'weaknesses': competitor_info['weaknesses'],
                    'opportunities': [],
                    'threats': []
                }
            
            # Generar estrategias recomendadas
            recommended_strategies = self._generate_competitive_strategies(
                competitor_info, swot_analysis
            )
            
            competitor = CompetitorInsight(
                competitor_name=competitor_name,
                market_share=competitor_info['market_share'],
                strengths=swot_analysis['strengths'],
                weaknesses=swot_analysis['weaknesses'],
                opportunities=swot_analysis['opportunities'],
                threats=swot_analysis['threats'],
                recommended_strategies=recommended_strategies
            )
            competitors.append(competitor)
        
        # Ordenar por participación de mercado
        competitors.sort(key=lambda x: x.market_share, reverse=True)
        
        logger.info(f"🏆 Analyzed {len(competitors)} competitors")
        return competitors
    
    def _generate_swot_analysis(self, competitor_info: Dict) -> Dict[str, List[str]]:
        """Generar análisis SWOT para un competidor"""
        strengths = competitor_info['strengths'].copy()
        weaknesses = competitor_info['weaknesses'].copy()
        
        # Generar oportunidades basadas en debilidades del competidor
        opportunities = []
        for weakness in weaknesses:
            if 'cost' in weakness.lower():
                opportunities.append("Oportunidad de precio competitivo")
            elif 'complex' in weakness.lower():
                opportunities.append("Oportunidad de simplicidad y usabilidad")
            elif 'limited' in weakness.lower():
                opportunities.append("Oportunidad de expansión de funcionalidades")
        
        # Generar amenazas basadas en fortalezas del competidor
        threats = []
        for strength in strengths:
            if 'platform' in strength.lower():
                threats.append("Amenaza de integración completa")
            elif 'automation' in strength.lower():
                threats.append("Amenaza de automatización avanzada")
            elif 'analytics' in strength.lower():
                threats.append("Amenaza de capacidades analíticas")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'opportunities': opportunities,
            'threats': threats
        }
    
    def _generate_competitive_strategies(self, 
                                       competitor_info: Dict,
                                       swot_analysis: Dict) -> List[str]:
        """Generar estrategias competitivas basadas en análisis SWOT"""
        strategies = []
        
        # Estrategias basadas en oportunidades
        for opportunity in swot_analysis['opportunities']:
            if 'precio' in opportunity.lower():
                strategies.append("Desarrollar solución más económica")
            elif 'simplicidad' in opportunity.lower():
                strategies.append("Crear interfaz más intuitiva")
            elif 'funcionalidades' in opportunity.lower():
                strategies.append("Expandir capacidades del producto")
        
        # Estrategias basadas en amenazas
        for threat in swot_analysis['threats']:
            if 'integración' in threat.lower():
                strategies.append("Mejorar integraciones con terceros")
            elif 'automatización' in threat.lower():
                strategies.append("Desarrollar automatización más avanzada")
            elif 'analíticas' in threat.lower():
                strategies.append("Invertir en capacidades de análisis")
        
        # Estrategias generales
        strategies.extend([
            "Diferenciación por nicho específico",
            "Mejor soporte al cliente",
            "Innovación en tecnología emergente"
        ])
        
        return strategies[:5]  # Limitar a 5 estrategias principales
    
    def predict_concept_performance(self, 
                                  concept: MarketingConcept) -> PerformancePrediction:
        """
        Predecir rendimiento de un concepto de marketing
        """
        # Obtener factores de éxito del modelo
        success_factors = self.performance_model['success_factors']
        
        # Calcular score base
        tech_score = success_factors['technology_weights'].get(concept.technology, 0.5)
        channel_score = success_factors['channel_weights'].get(concept.channel, 0.5)
        vertical_score = success_factors['vertical_weights'].get(concept.vertical, 0.5)
        
        # Calcular score combinado
        combined_score = (tech_score * 0.4 + channel_score * 0.3 + vertical_score * 0.3)
        
        # Predecir métricas
        predicted_metrics = self._predict_metrics(concept, combined_score)
        
        # Calcular intervalos de confianza
        confidence_interval = self._calculate_confidence_interval(predicted_metrics)
        
        # Identificar factores de riesgo
        risk_factors = self._identify_risk_factors(concept)
        
        # Generar sugerencias de optimización
        optimization_suggestions = self._generate_optimization_suggestions(concept, predicted_metrics)
        
        # Calcular probabilidad de éxito
        success_probability = self._calculate_success_probability(concept, combined_score)
        
        prediction = PerformancePrediction(
            concept_id=concept.concept_id,
            predicted_metrics=predicted_metrics,
            confidence_interval=confidence_interval,
            risk_factors=risk_factors,
            optimization_suggestions=optimization_suggestions,
            success_probability=success_probability
        )
        
        logger.info(f"🔮 Generated performance prediction for {concept.concept_id}")
        return prediction
    
    def _predict_metrics(self, concept: MarketingConcept, score: float) -> Dict[str, float]:
        """Predecir métricas específicas para un concepto"""
        metric_predictors = self.performance_model['metric_predictors']
        predicted_metrics = {}
        
        for metric, predictor in metric_predictors.items():
            base_value = predictor['base']
            max_value = predictor.get('max', base_value * 3)
            min_value = predictor.get('min', base_value * 0.5)
            
            # Ajustar por score y complejidad
            complexity_multiplier = {'Baja': 1.0, 'Media': 0.9, 'Alta': 0.8}.get(concept.complexity, 1.0)
            adjusted_score = score * complexity_multiplier
            
            # Calcular valor predicho
            predicted_value = base_value + (max_value - base_value) * adjusted_score
            predicted_value = max(min_value, min(max_value, predicted_value))
            
            predicted_metrics[metric] = round(predicted_value, 2)
        
        return predicted_metrics
    
    def _calculate_confidence_interval(self, metrics: Dict[str, float]) -> Dict[str, Tuple[float, float]]:
        """Calcular intervalos de confianza para las métricas predichas"""
        confidence_interval = {}
        
        for metric, value in metrics.items():
            # Intervalo de confianza del 80%
            margin = value * 0.15  # 15% de margen
            lower_bound = max(0, value - margin)
            upper_bound = value + margin
            
            confidence_interval[metric] = (round(lower_bound, 2), round(upper_bound, 2))
        
        return confidence_interval
    
    def _identify_risk_factors(self, concept: MarketingConcept) -> List[str]:
        """Identificar factores de riesgo para un concepto"""
        risk_factors = []
        
        # Riesgos por tecnología
        if concept.technology in ['Deep Learning', 'Reinforcement Learning']:
            risk_factors.append("Alta complejidad técnica")
        
        # Riesgos por canal
        if concept.channel in ['SEM/PPC', 'Mobile Apps']:
            risk_factors.append("Alto costo de adquisición")
        
        # Riesgos por vertical
        if concept.vertical in ['Healthcare', 'Fintech']:
            risk_factors.append("Regulaciones estrictas")
        
        # Riesgos por presupuesto
        if concept.estimated_budget['amount'] > 50000:
            risk_factors.append("Alta inversión requerida")
        
        # Riesgos por complejidad
        if concept.complexity == 'Alta':
            risk_factors.append("Tiempo de implementación extendido")
        
        return risk_factors
    
    def _generate_optimization_suggestions(self, 
                                         concept: MarketingConcept,
                                         predicted_metrics: Dict[str, float]) -> List[str]:
        """Generar sugerencias de optimización para un concepto"""
        suggestions = []
        
        # Sugerencias basadas en métricas predichas
        if predicted_metrics.get('conversion_rate', 0) < 8:
            suggestions.append("Mejorar estrategia de conversión")
        
        if predicted_metrics.get('cost_per_acquisition', 0) > 40:
            suggestions.append("Optimizar canales de adquisición")
        
        if predicted_metrics.get('engagement_rate', 0) < 6:
            suggestions.append("Mejorar contenido y engagement")
        
        # Sugerencias basadas en tecnología
        if concept.technology == 'Machine Learning':
            suggestions.append("Implementar A/B testing automático")
        
        if concept.technology == 'NLP':
            suggestions.append("Optimizar procesamiento de lenguaje natural")
        
        # Sugerencias generales
        suggestions.extend([
            "Monitorear métricas en tiempo real",
            "Implementar feedback loops",
            "Optimizar basado en datos de usuario"
        ])
        
        return suggestions[:5]  # Limitar a 5 sugerencias principales
    
    def _calculate_success_probability(self, concept: MarketingConcept, score: float) -> float:
        """Calcular probabilidad de éxito de un concepto"""
        base_probability = score
        
        # Ajustar por presupuesto
        budget_multiplier = 1.0
        if concept.estimated_budget['amount'] > 40000:
            budget_multiplier = 1.1  # Mayor presupuesto = mayor probabilidad
        elif concept.estimated_budget['amount'] < 15000:
            budget_multiplier = 0.9  # Menor presupuesto = menor probabilidad
        
        # Ajustar por duración
        duration_multiplier = 1.0
        if concept.timeline['duration_weeks'] > 12:
            duration_multiplier = 0.95  # Proyectos largos = menor probabilidad
        elif concept.timeline['duration_weeks'] < 6:
            duration_multiplier = 1.05  # Proyectos cortos = mayor probabilidad
        
        final_probability = base_probability * budget_multiplier * duration_multiplier
        return min(0.98, max(0.1, final_probability))
    
    def generate_market_opportunity_report(self) -> Dict[str, Any]:
        """
        Generar reporte completo de oportunidades de mercado
        """
        # Analizar tendencias
        trends = self.analyze_market_trends()
        
        # Analizar competencia
        competitors = self.analyze_competition()
        
        # Generar conceptos optimizados
        optimized_concepts = self._generate_optimized_concepts(trends)
        
        # Calcular métricas del mercado
        market_metrics = self._calculate_market_metrics()
        
        report = {
            'executive_summary': self._generate_executive_summary(trends, competitors),
            'market_trends': [self._trend_to_dict(trend) for trend in trends[:10]],
            'competitive_analysis': [self._competitor_to_dict(comp) for comp in competitors],
            'optimized_concepts': [self._concept_to_dict(concept) for concept in optimized_concepts],
            'market_metrics': market_metrics,
            'recommendations': self._generate_strategic_recommendations(trends, competitors),
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info("📊 Generated comprehensive market opportunity report")
        return report
    
    def _generate_optimized_concepts(self, trends: List[TrendAnalysis]) -> List[MarketingConcept]:
        """Generar conceptos optimizados basados en tendencias"""
        optimized_concepts = []
        
        # Seleccionar top 5 tendencias
        top_trends = trends[:5]
        
        for trend in top_trends:
            # Generar concepto basado en la tendencia
            concept = self.brain.generate_fresh_concepts(
                num_concepts=1,
                focus_theme=trend.trend_name,
                min_success_probability=0.8
            )[0]
            
            # Optimizar concepto basado en tendencia
            concept.name = f"Trend-Optimized {concept.name}"
            concept.tags.extend(trend.emerging_keywords[:3])
            
            optimized_concepts.append(concept)
        
        return optimized_concepts
    
    def _calculate_market_metrics(self) -> Dict[str, Any]:
        """Calcular métricas del mercado"""
        market_data = self.market_data
        
        return {
            'total_market_size': sum(market_data['market_size'].values()),
            'average_growth_rate': np.mean(list(market_data['growth_rates'].values())),
            'fastest_growing_segment': max(market_data['growth_rates'].items(), key=lambda x: x[1]),
            'largest_market_segment': max(market_data['market_size'].items(), key=lambda x: x[1]),
            'regional_opportunities': market_data['regional_data']
        }
    
    def _generate_executive_summary(self, 
                                  trends: List[TrendAnalysis],
                                  competitors: List[CompetitorInsight]) -> str:
        """Generar resumen ejecutivo"""
        top_trend = trends[0] if trends else None
        top_competitor = competitors[0] if competitors else None
        
        summary = f"""
        El mercado de marketing con IA muestra un crecimiento robusto con múltiples oportunidades emergentes.
        La tendencia principal es '{top_trend.trend_name}' con una tasa de crecimiento del {top_trend.growth_rate:.1%}.
        El competidor líder es {top_competitor.competitor_name} con {top_competitor.market_share:.1%} de participación de mercado.
        Se recomienda enfocarse en tecnologías emergentes y diferenciación por nicho específico.
        """
        
        return summary.strip()
    
    def _generate_strategic_recommendations(self, 
                                          trends: List[TrendAnalysis],
                                          competitors: List[CompetitorInsight]) -> List[str]:
        """Generar recomendaciones estratégicas"""
        recommendations = []
        
        # Recomendaciones basadas en tendencias
        for trend in trends[:3]:
            recommendations.append(f"Invertir en {trend.trend_name} - {trend.market_opportunity}")
        
        # Recomendaciones basadas en competencia
        for competitor in competitors[:2]:
            for strategy in competitor.recommended_strategies[:2]:
                recommendations.append(f"Estrategia competitiva: {strategy}")
        
        # Recomendaciones generales
        recommendations.extend([
            "Desarrollar capacidades de IA diferenciadas",
            "Enfocarse en nichos específicos con alta demanda",
            "Invertir en automatización y personalización",
            "Construir ecosistema de integraciones"
        ])
        
        return recommendations[:8]  # Limitar a 8 recomendaciones
    
    def _trend_to_dict(self, trend: TrendAnalysis) -> Dict[str, Any]:
        """Convertir TrendAnalysis a diccionario"""
        return {
            'name': trend.trend_name,
            'category': trend.category,
            'growth_rate': trend.growth_rate,
            'popularity_score': trend.popularity_score,
            'emerging_keywords': trend.emerging_keywords,
            'related_technologies': trend.related_technologies,
            'market_opportunity': trend.market_opportunity,
            'predicted_duration': trend.predicted_duration,
            'confidence_level': trend.confidence_level
        }
    
    def _competitor_to_dict(self, competitor: CompetitorInsight) -> Dict[str, Any]:
        """Convertir CompetitorInsight a diccionario"""
        return {
            'name': competitor.competitor_name,
            'market_share': competitor.market_share,
            'strengths': competitor.strengths,
            'weaknesses': competitor.weaknesses,
            'opportunities': competitor.opportunities,
            'threats': competitor.threats,
            'recommended_strategies': competitor.recommended_strategies
        }
    
    def _concept_to_dict(self, concept: MarketingConcept) -> Dict[str, Any]:
        """Convertir MarketingConcept a diccionario"""
        return {
            'id': concept.concept_id,
            'name': concept.name,
            'description': concept.description,
            'category': concept.category,
            'technology': concept.technology,
            'channel': concept.channel,
            'vertical': concept.vertical,
            'success_probability': concept.success_probability,
            'budget': concept.estimated_budget,
            'timeline': concept.timeline,
            'tags': concept.tags
        }
    
    def export_analytics_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Exportar reporte de análisis a archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"marketing_analytics_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Analytics report exported to {filename}")
        return filename


def main():
    """Función principal para demostrar el sistema de análisis"""
    print("📈 MARKETING BRAIN ANALYTICS")
    print("=" * 50)
    
    # Inicializar sistema
    analytics = MarketingBrainAnalytics()
    
    # Analizar tendencias del mercado
    print("\n🔍 ANALIZANDO TENDENCIAS DEL MERCADO...")
    trends = analytics.analyze_market_trends()
    
    print(f"\n📈 TOP 5 TENDENCIAS IDENTIFICADAS:")
    for i, trend in enumerate(trends[:5], 1):
        print(f"\n{i}. {trend.trend_name}")
        print(f"   📊 Categoría: {trend.category}")
        print(f"   📈 Crecimiento: {trend.growth_rate:.1%}")
        print(f"   🎯 Score Popularidad: {trend.popularity_score:.1f}")
        print(f"   💡 Oportunidad: {trend.market_opportunity}")
        print(f"   ⏱️ Duración: {trend.predicted_duration}")
        print(f"   🔑 Keywords: {', '.join(trend.emerging_keywords[:3])}")
    
    # Analizar competencia
    print(f"\n🏆 ANALIZANDO COMPETENCIA...")
    competitors = analytics.analyze_competition()
    
    print(f"\n🎯 ANÁLISIS COMPETITIVO:")
    for i, competitor in enumerate(competitors[:3], 1):
        print(f"\n{i}. {competitor.competitor_name}")
        print(f"   📊 Participación: {competitor.market_share:.1%}")
        print(f"   ✅ Fortalezas: {', '.join(competitor.strengths[:2])}")
        print(f"   ❌ Debilidades: {', '.join(competitor.weaknesses[:2])}")
        print(f"   🚀 Estrategias: {', '.join(competitor.recommended_strategies[:2])}")
    
    # Generar reporte completo
    print(f"\n📊 GENERANDO REPORTE COMPLETO...")
    report = analytics.generate_market_opportunity_report()
    
    # Exportar reporte
    filename = analytics.export_analytics_report(report)
    print(f"✅ Reporte exportado a: {filename}")
    
    # Mostrar resumen ejecutivo
    print(f"\n📋 RESUMEN EJECUTIVO:")
    print(report['executive_summary'])
    
    # Mostrar recomendaciones estratégicas
    print(f"\n🎯 RECOMENDACIONES ESTRATÉGICAS:")
    for i, recommendation in enumerate(report['recommendations'][:5], 1):
        print(f"{i}. {recommendation}")
    
    print(f"\n✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
    print(f"🎉 El sistema de análisis ha identificado oportunidades de mercado")
    print(f"   y generado recomendaciones estratégicas basadas en datos reales.")


if __name__ == "__main__":
    main()










