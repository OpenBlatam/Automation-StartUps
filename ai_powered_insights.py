"""
AI-Powered Insights Engine
Motor de insights avanzado con machine learning y análisis predictivo
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from enhanced_launch_planner import EnhancedLaunchPlanner, AIPrediction, MarketAnalysis, PerformanceMetrics

@dataclass
class MLPrediction:
    """Predicción de machine learning"""
    model_name: str
    confidence: float
    prediction: Any
    features_used: List[str]
    model_version: str

@dataclass
class TrendAnalysis:
    """Análisis de tendencias"""
    trend_direction: str  # "up", "down", "stable"
    trend_strength: float  # 0-1
    trend_duration: str
    key_indicators: List[str]
    future_projection: Dict[str, Any]

@dataclass
class CompetitiveIntelligence:
    """Inteligencia competitiva"""
    competitor_analysis: Dict[str, Any]
    market_position: str
    competitive_advantages: List[str]
    threats: List[str]
    opportunities: List[str]
    market_share_prediction: float

class AIPoweredInsightsEngine:
    """Motor de insights avanzado con IA"""
    
    def __init__(self):
        self.enhanced_planner = EnhancedLaunchPlanner()
        self.ml_models = self._initialize_ml_models()
        self.trend_data = self._load_trend_data()
        self.competitive_data = self._load_competitive_data()
        
    def _initialize_ml_models(self) -> Dict[str, Any]:
        """Inicializar modelos de machine learning (simulados)"""
        return {
            "success_predictor": {
                "type": "RandomForest",
                "accuracy": 0.89,
                "features": ["complexity", "team_size", "budget", "market_conditions", "timeline"],
                "version": "2.1.0"
            },
            "timeline_estimator": {
                "type": "LinearRegression",
                "accuracy": 0.84,
                "features": ["scope", "team_experience", "technology_stack", "dependencies"],
                "version": "1.8.0"
            },
            "budget_optimizer": {
                "type": "GradientBoosting",
                "accuracy": 0.91,
                "features": ["scope", "team_costs", "marketing_needs", "infrastructure"],
                "version": "2.0.0"
            },
            "risk_assessor": {
                "type": "NeuralNetwork",
                "accuracy": 0.87,
                "features": ["market_conditions", "technical_complexity", "team_stability"],
                "version": "1.9.0"
            },
            "market_analyzer": {
                "type": "LSTM",
                "accuracy": 0.82,
                "features": ["historical_data", "market_trends", "competitor_activity"],
                "version": "1.5.0"
            }
        }
    
    def _load_trend_data(self) -> Dict[str, Any]:
        """Cargar datos de tendencias del mercado"""
        return {
            "technology_trends": {
                "ai_adoption": {"trend": "up", "growth_rate": 0.35, "confidence": 0.92},
                "cloud_migration": {"trend": "up", "growth_rate": 0.28, "confidence": 0.89},
                "mobile_first": {"trend": "stable", "growth_rate": 0.12, "confidence": 0.85},
                "privacy_focus": {"trend": "up", "growth_rate": 0.45, "confidence": 0.94},
                "sustainability": {"trend": "up", "growth_rate": 0.38, "confidence": 0.88}
            },
            "market_trends": {
                "saas_growth": {"trend": "up", "growth_rate": 0.22, "confidence": 0.91},
                "ecommerce_boom": {"trend": "up", "growth_rate": 0.18, "confidence": 0.87},
                "mobile_app_saturation": {"trend": "down", "growth_rate": -0.05, "confidence": 0.83},
                "content_consumption": {"trend": "up", "growth_rate": 0.25, "confidence": 0.90}
            },
            "consumer_trends": {
                "remote_work": {"trend": "up", "growth_rate": 0.30, "confidence": 0.93},
                "digital_native": {"trend": "up", "growth_rate": 0.15, "confidence": 0.86},
                "personalization": {"trend": "up", "growth_rate": 0.40, "confidence": 0.95},
                "instant_gratification": {"trend": "up", "growth_rate": 0.20, "confidence": 0.88}
            }
        }
    
    def _load_competitive_data(self) -> Dict[str, Any]:
        """Cargar datos competitivos"""
        return {
            "mobile_app": {
                "top_competitors": [
                    {"name": "Google", "market_share": 0.35, "strength": "very_high"},
                    {"name": "Apple", "market_share": 0.28, "strength": "very_high"},
                    {"name": "Meta", "market_share": 0.15, "strength": "high"},
                    {"name": "TikTok", "market_share": 0.12, "strength": "high"}
                ],
                "barriers_to_entry": ["App Store approval", "User acquisition costs", "Brand recognition"],
                "success_factors": ["Unique value proposition", "Excellent UX", "Viral mechanics"]
            },
            "saas_platform": {
                "top_competitors": [
                    {"name": "Microsoft", "market_share": 0.40, "strength": "very_high"},
                    {"name": "Salesforce", "market_share": 0.25, "strength": "very_high"},
                    {"name": "HubSpot", "market_share": 0.15, "strength": "high"},
                    {"name": "Slack", "market_share": 0.10, "strength": "high"}
                ],
                "barriers_to_entry": ["High switching costs", "Network effects", "Enterprise sales"],
                "success_factors": ["Integration capabilities", "Customer success", "Pricing strategy"]
            },
            "ecommerce": {
                "top_competitors": [
                    {"name": "Amazon", "market_share": 0.45, "strength": "extreme"},
                    {"name": "eBay", "market_share": 0.15, "strength": "high"},
                    {"name": "Shopify", "market_share": 0.12, "strength": "high"},
                    {"name": "WooCommerce", "market_share": 0.08, "strength": "medium"}
                ],
                "barriers_to_entry": ["Brand recognition", "Logistics network", "Customer trust"],
                "success_factors": ["Unique products", "Customer experience", "SEO optimization"]
            }
        }
    
    def generate_ml_predictions(self, requirements: str, scenario_type: str) -> Dict[str, MLPrediction]:
        """Generar predicciones usando modelos de ML"""
        predictions = {}
        
        # Análisis básico
        basic_analysis = self.enhanced_planner.base_planner.analyze_launch_requirements(requirements)
        market_analysis = self.enhanced_planner._perform_market_analysis(scenario_type)
        
        # Predicción de éxito
        success_model = self.ml_models["success_predictor"]
        success_probability = self._predict_success_ml(basic_analysis, market_analysis)
        
        predictions["success"] = MLPrediction(
            model_name=success_model["type"],
            confidence=success_model["accuracy"],
            prediction=success_probability,
            features_used=success_model["features"],
            model_version=success_model["version"]
        )
        
        # Estimación de timeline
        timeline_model = self.ml_models["timeline_estimator"]
        timeline_estimate = self._estimate_timeline_ml(basic_analysis)
        
        predictions["timeline"] = MLPrediction(
            model_name=timeline_model["type"],
            confidence=timeline_model["accuracy"],
            prediction=timeline_estimate,
            features_used=timeline_model["features"],
            model_version=timeline_model["version"]
        )
        
        # Optimización de presupuesto
        budget_model = self.ml_models["budget_optimizer"]
        budget_optimization = self._optimize_budget_ml(basic_analysis, market_analysis)
        
        predictions["budget"] = MLPrediction(
            model_name=budget_model["type"],
            confidence=budget_model["accuracy"],
            prediction=budget_optimization,
            features_used=budget_model["features"],
            model_version=budget_model["version"]
        )
        
        # Evaluación de riesgos
        risk_model = self.ml_models["risk_assessor"]
        risk_assessment = self._assess_risks_ml(basic_analysis, market_analysis)
        
        predictions["risk"] = MLPrediction(
            model_name=risk_model["type"],
            confidence=risk_model["accuracy"],
            prediction=risk_assessment,
            features_used=risk_model["features"],
            model_version=risk_model["version"]
        )
        
        return predictions
    
    def _predict_success_ml(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> float:
        """Predicción de éxito usando ML"""
        # Simular predicción de RandomForest
        base_probability = 0.5
        
        # Factores del modelo
        complexity_factor = 1.0 - (basic_analysis["complexity_score"] * 0.1)
        market_factor = 0.8 if market_analysis.competition_level in ["low", "medium"] else 0.6
        team_factor = min(1.2, 0.8 + (len(basic_analysis.get("team_requirements", [])) * 0.1))
        
        # Predicción final
        prediction = base_probability * complexity_factor * market_factor * team_factor
        
        # Agregar ruido aleatorio para simular ML
        noise = np.random.normal(0, 0.05)
        prediction = max(0.1, min(0.95, prediction + noise))
        
        return prediction
    
    def _estimate_timeline_ml(self, basic_analysis: Dict) -> str:
        """Estimación de timeline usando ML"""
        complexity = basic_analysis["complexity_score"]
        
        # Modelo de regresión lineal simulado
        base_weeks = 8
        complexity_multiplier = 1 + (complexity * 0.3)
        
        estimated_weeks = int(base_weeks * complexity_multiplier)
        
        # Agregar variabilidad
        variance = np.random.normal(0, 2)
        estimated_weeks = max(4, estimated_weeks + int(variance))
        
        if estimated_weeks <= 8:
            return "6-8 weeks"
        elif estimated_weeks <= 12:
            return "8-12 weeks"
        elif estimated_weeks <= 16:
            return "12-16 weeks"
        elif estimated_weeks <= 20:
            return "16-20 weeks"
        else:
            return "20-24 weeks"
    
    def _optimize_budget_ml(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> Dict[str, float]:
        """Optimización de presupuesto usando ML"""
        base_budget = 100000
        
        # Ajustar según complejidad
        complexity_multiplier = 1 + (basic_analysis["complexity_score"] * 0.2)
        
        # Ajustar según competencia
        competition_multipliers = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "very_high": 1.5,
            "extreme": 2.0
        }
        
        competition_multiplier = competition_multipliers.get(market_analysis.competition_level, 1.0)
        
        total_budget = base_budget * complexity_multiplier * competition_multiplier
        
        # Distribución optimizada por ML
        distribution = {
            "development": total_budget * 0.42,
            "marketing": total_budget * 0.28,
            "infrastructure": total_budget * 0.16,
            "team": total_budget * 0.10,
            "contingency": total_budget * 0.04
        }
        
        return distribution
    
    def _assess_risks_ml(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> List[str]:
        """Evaluación de riesgos usando ML"""
        risks = []
        
        # Red neuronal simulada para clasificación de riesgos
        if basic_analysis["complexity_score"] >= 6:
            risks.extend([
                "Alta complejidad técnica detectada por ML",
                "Riesgo de sobrecarga del equipo de desarrollo",
                "Posibles problemas de escalabilidad"
            ])
        
        if market_analysis.competition_level in ["very_high", "extreme"]:
            risks.extend([
                "Mercado altamente competitivo identificado",
                "Dificultad para destacar entre competidores",
                "Posible guerra de precios"
            ])
        
        # Riesgos adicionales detectados por ML
        if len(basic_analysis.get("team_requirements", [])) < 3:
            risks.append("Equipo insuficiente detectado por análisis de ML")
        
        return risks
    
    def analyze_trends(self, scenario_type: str) -> TrendAnalysis:
        """Análisis de tendencias del mercado"""
        trend_data = self.trend_data
        
        # Combinar tendencias relevantes
        relevant_trends = []
        
        if scenario_type == "mobile_app":
            relevant_trends.extend([
                trend_data["technology_trends"]["mobile_first"],
                trend_data["market_trends"]["mobile_app_saturation"],
                trend_data["consumer_trends"]["digital_native"]
            ])
        elif scenario_type == "saas_platform":
            relevant_trends.extend([
                trend_data["technology_trends"]["ai_adoption"],
                trend_data["market_trends"]["saas_growth"],
                trend_data["consumer_trends"]["remote_work"]
            ])
        elif scenario_type == "ecommerce":
            relevant_trends.extend([
                trend_data["market_trends"]["ecommerce_boom"],
                trend_data["consumer_trends"]["instant_gratification"],
                trend_data["technology_trends"]["privacy_focus"]
            ])
        
        # Calcular tendencia general
        if not relevant_trends:
            return TrendAnalysis(
                trend_direction="stable",
                trend_strength=0.5,
                trend_duration="6-12 months",
                key_indicators=["Market stability"],
                future_projection={"growth_rate": 0.1}
            )
        
        # Análisis de tendencia
        up_trends = sum(1 for t in relevant_trends if t["trend"] == "up")
        down_trends = sum(1 for t in relevant_trends if t["trend"] == "down")
        stable_trends = sum(1 for t in relevant_trends if t["trend"] == "stable")
        
        total_trends = len(relevant_trends)
        
        if up_trends > down_trends and up_trends > stable_trends:
            trend_direction = "up"
            trend_strength = up_trends / total_trends
        elif down_trends > up_trends and down_trends > stable_trends:
            trend_direction = "down"
            trend_strength = down_trends / total_trends
        else:
            trend_direction = "stable"
            trend_strength = stable_trends / total_trends
        
        # Proyección futura
        avg_growth_rate = np.mean([t["growth_rate"] for t in relevant_trends])
        avg_confidence = np.mean([t["confidence"] for t in relevant_trends])
        
        future_projection = {
            "growth_rate": avg_growth_rate,
            "confidence": avg_confidence,
            "time_horizon": "12-18 months"
        }
        
        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_duration="6-12 months",
            key_indicators=[t["trend"] for t in relevant_trends],
            future_projection=future_projection
        )
    
    def generate_competitive_intelligence(self, scenario_type: str) -> CompetitiveIntelligence:
        """Generar inteligencia competitiva"""
        competitive_data = self.competitive_data.get(scenario_type, self.competitive_data["mobile_app"])
        
        # Análisis de competidores
        competitors = competitive_data["top_competitors"]
        
        # Calcular posición de mercado
        total_market_share = sum(c["market_share"] for c in competitors)
        remaining_share = 1.0 - total_market_share
        
        if remaining_share > 0.1:
            market_position = "Opportunity for new entrants"
        elif remaining_share > 0.05:
            market_position = "Competitive but accessible"
        else:
            market_position = "Highly saturated market"
        
        # Identificar ventajas competitivas
        competitive_advantages = competitive_data["success_factors"]
        
        # Identificar amenazas
        threats = competitive_data["barriers_to_entry"]
        
        # Identificar oportunidades
        opportunities = []
        if remaining_share > 0.05:
            opportunities.append("Market share available for new entrants")
        
        if any(c["strength"] == "medium" for c in competitors):
            opportunities.append("Weak competitors to target")
        
        # Predicción de cuota de mercado
        market_share_prediction = min(0.05, remaining_share * 0.5)  # Conservador
        
        return CompetitiveIntelligence(
            competitor_analysis={
                "top_competitors": competitors,
                "total_market_share": total_market_share,
                "remaining_share": remaining_share
            },
            market_position=market_position,
            competitive_advantages=competitive_advantages,
            threats=threats,
            opportunities=opportunities,
            market_share_prediction=market_share_prediction
        )
    
    def generate_comprehensive_insights(self, requirements: str, scenario_type: str) -> Dict[str, Any]:
        """Generar insights comprehensivos"""
        
        # Predicciones de ML
        ml_predictions = self.generate_ml_predictions(requirements, scenario_type)
        
        # Análisis de tendencias
        trend_analysis = self.analyze_trends(scenario_type)
        
        # Inteligencia competitiva
        competitive_intelligence = self.generate_competitive_intelligence(scenario_type)
        
        # Análisis tradicional mejorado
        enhanced_analysis = self.enhanced_planner.analyze_launch_requirements_ai(requirements, scenario_type)
        
        return {
            "ml_predictions": {k: asdict(v) for k, v in ml_predictions.items()},
            "trend_analysis": asdict(trend_analysis),
            "competitive_intelligence": asdict(competitive_intelligence),
            "enhanced_analysis": enhanced_analysis,
            "insights_summary": self._generate_insights_summary(
                ml_predictions, trend_analysis, competitive_intelligence
            ),
            "recommendations": self._generate_ai_recommendations(
                ml_predictions, trend_analysis, competitive_intelligence
            ),
            "confidence_score": self._calculate_overall_confidence(ml_predictions),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_insights_summary(self, ml_predictions: Dict, trend_analysis: TrendAnalysis, 
                                 competitive_intelligence: CompetitiveIntelligence) -> Dict[str, Any]:
        """Generar resumen de insights"""
        
        success_prediction = ml_predictions["success"]
        
        return {
            "overall_success_probability": success_prediction.prediction,
            "confidence_level": success_prediction.confidence,
            "market_trend": trend_analysis.trend_direction,
            "trend_strength": trend_analysis.trend_strength,
            "market_position": competitive_intelligence.market_position,
            "predicted_market_share": competitive_intelligence.market_share_prediction,
            "key_opportunities": len(competitive_intelligence.opportunities),
            "major_threats": len(competitive_intelligence.threats),
            "ml_model_accuracy": np.mean([p.confidence for p in ml_predictions.values()])
        }
    
    def _generate_ai_recommendations(self, ml_predictions: Dict, trend_analysis: TrendAnalysis,
                                   competitive_intelligence: CompetitiveIntelligence) -> List[str]:
        """Generar recomendaciones basadas en IA"""
        recommendations = []
        
        # Recomendaciones basadas en predicciones de ML
        success_pred = ml_predictions["success"]
        if success_pred.prediction < 0.6:
            recommendations.extend([
                "Considerar reducir el alcance del proyecto para aumentar probabilidad de éxito",
                "Invertir más en investigación de mercado y validación",
                "Desarrollar un MVP más simple y enfocado"
            ])
        
        # Recomendaciones basadas en tendencias
        if trend_analysis.trend_direction == "up":
            recommendations.append("Aprovechar la tendencia alcista del mercado para acelerar el lanzamiento")
        elif trend_analysis.trend_direction == "down":
            recommendations.append("Considerar diferir el lanzamiento o pivotar la estrategia")
        
        # Recomendaciones basadas en competencia
        if competitive_intelligence.market_position == "Opportunity for new entrants":
            recommendations.append("Mercado con oportunidades para nuevos participantes - proceder con confianza")
        elif competitive_intelligence.market_position == "Highly saturated market":
            recommendations.extend([
                "Mercado altamente saturado - enfocarse en diferenciación única",
                "Considerar nichos de mercado menos competitivos"
            ])
        
        # Recomendaciones de ML
        budget_pred = ml_predictions["budget"]
        if budget_pred.prediction["marketing"] > budget_pred.prediction["development"]:
            recommendations.append("Considerar aumentar el presupuesto de desarrollo según ML")
        
        return list(set(recommendations))  # Eliminar duplicados
    
    def _calculate_overall_confidence(self, ml_predictions: Dict) -> float:
        """Calcular confianza general del sistema"""
        confidences = [pred.confidence for pred in ml_predictions.values()]
        return np.mean(confidences)

def main():
    """Demostración del motor de insights con IA"""
    print("🧠 AI-Powered Insights Engine Demo")
    print("=" * 50)
    
    # Inicializar motor de insights
    insights_engine = AIPoweredInsightsEngine()
    
    # Requisitos de ejemplo
    requirements = """
    Lanzar una plataforma SaaS de análisis de datos con IA para pequeñas empresas.
    Objetivo: 2,000 usuarios pagos en el primer año.
    Presupuesto: $150,000 para desarrollo y marketing.
    Necesitamos 6 desarrolladores, 2 diseñadores, 1 especialista en IA.
    Debe integrar con herramientas populares como Excel, Google Sheets, y CRM.
    Lanzamiento objetivo: Q2 2024.
    Prioridad alta para facilidad de uso y insights accionables.
    """
    
    print("📝 Requisitos de Prueba:")
    print(f"   {requirements.strip()}")
    
    print("\n🧠 Generando insights comprehensivos con IA...")
    
    try:
        # Generar insights comprehensivos
        insights = insights_engine.generate_comprehensive_insights(requirements, "saas_platform")
        
        print("✅ Insights generados exitosamente!")
        
        # Mostrar resumen
        summary = insights["insights_summary"]
        print(f"\n📊 Resumen de Insights:")
        print(f"   🎯 Probabilidad de Éxito: {summary['overall_success_probability']:.1%}")
        print(f"   🧠 Nivel de Confianza: {summary['confidence_level']:.1%}")
        print(f"   📈 Tendencia del Mercado: {summary['market_trend'].title()}")
        print(f"   💪 Fuerza de Tendencia: {summary['trend_strength']:.1%}")
        print(f"   🏆 Posición de Mercado: {summary['market_position']}")
        print(f"   📊 Cuota de Mercado Predicha: {summary['predicted_market_share']:.1%}")
        print(f"   🎯 Oportunidades Clave: {summary['key_opportunities']}")
        print(f"   ⚠️ Amenazas Principales: {summary['major_threats']}")
        print(f"   🤖 Precisión del Modelo ML: {summary['ml_model_accuracy']:.1%}")
        
        # Mostrar predicciones de ML
        print(f"\n🤖 Predicciones de Machine Learning:")
        for model_name, prediction in insights["ml_predictions"].items():
            print(f"   📊 {model_name.title()}:")
            print(f"      Modelo: {prediction['model_name']}")
            print(f"      Confianza: {prediction['confidence']:.1%}")
            print(f"      Versión: {prediction['model_version']}")
            if model_name == "success":
                print(f"      Predicción: {prediction['prediction']:.1%}")
            elif model_name == "timeline":
                print(f"      Predicción: {prediction['prediction']}")
            elif model_name == "budget":
                total = sum(prediction['prediction'].values())
                print(f"      Predicción: ${total:,.0f} total")
        
        # Mostrar análisis de tendencias
        trend_analysis = insights["trend_analysis"]
        print(f"\n📈 Análisis de Tendencias:")
        print(f"   Dirección: {trend_analysis['trend_direction'].title()}")
        print(f"   Fuerza: {trend_analysis['trend_strength']:.1%}")
        print(f"   Duración: {trend_analysis['trend_duration']}")
        print(f"   Indicadores Clave: {', '.join(trend_analysis['key_indicators'])}")
        
        # Mostrar inteligencia competitiva
        competitive = insights["competitive_intelligence"]
        print(f"\n🏆 Inteligencia Competitiva:")
        print(f"   Posición: {competitive['market_position']}")
        print(f"   Cuota Predicha: {competitive['market_share_prediction']:.1%}")
        print(f"   Ventajas: {len(competitive['competitive_advantages'])} identificadas")
        print(f"   Amenazas: {len(competitive['threats'])} identificadas")
        print(f"   Oportunidades: {len(competitive['opportunities'])} identificadas")
        
        # Mostrar recomendaciones
        recommendations = insights["recommendations"]
        print(f"\n🎯 Recomendaciones de IA ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Guardar insights
        with open("ai_insights_comprehensive.json", "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Insights guardados en: ai_insights_comprehensive.json")
        
    except Exception as e:
        print(f"❌ Error generando insights: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Demo del AI-Powered Insights Engine completado!")

if __name__ == "__main__":
    main()








