"""
Enhanced Launch Planner - Sistema Mejorado
Versión avanzada con IA, análisis predictivo y funcionalidades premium
"""

import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

from launch_planning_checklist import LaunchPlanningChecklist, ChecklistItem, LaunchPhase
from clickup_brain_integration import ClickUpBrainBehavior, ClickUpBrainExtractor
from advanced_launch_planner import AdvancedLaunchPlanner, LaunchMetrics, TeamMember, ResourceRequirement

@dataclass
class AIPrediction:
    """Predicciones de IA para el lanzamiento"""
    success_probability: float
    estimated_timeline: str
    budget_optimization: Dict[str, float]
    risk_factors: List[str]
    success_metrics: Dict[str, float]
    recommendations: List[str]

@dataclass
class MarketAnalysis:
    """Análisis de mercado y competencia"""
    market_size: float
    competition_level: str
    target_audience: Dict[str, Any]
    market_trends: List[str]
    opportunities: List[str]
    threats: List[str]
    market_timing: str

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento del lanzamiento"""
    velocity: float  # Velocidad de desarrollo
    quality_score: float  # Puntuación de calidad
    team_efficiency: float  # Eficiencia del equipo
    resource_utilization: float  # Utilización de recursos
    timeline_adherence: float  # Adherencia al cronograma

class EnhancedLaunchPlanner:
    """Planificador de lanzamientos mejorado con IA y análisis avanzado"""
    
    def __init__(self):
        self.base_planner = AdvancedLaunchPlanner()
        self.brain_system = ClickUpBrainBehavior()
        self.checklist_system = LaunchPlanningChecklist()
        
        # Datos históricos para análisis predictivo
        self.historical_data = self._load_historical_data()
        self.market_data = self._load_market_data()
        
        # Modelos de IA (simulados)
        self.ai_models = self._initialize_ai_models()
        
    def _load_historical_data(self) -> Dict[str, Any]:
        """Cargar datos históricos de lanzamientos"""
        return {
            "mobile_apps": {
                "success_rate": 0.65,
                "avg_timeline": "12-16 weeks",
                "avg_budget": 75000,
                "common_risks": ["App Store rejection", "User acquisition", "Technical complexity"],
                "success_factors": ["Strong MVP", "User testing", "Marketing strategy"]
            },
            "saas_platforms": {
                "success_rate": 0.72,
                "avg_timeline": "16-24 weeks", 
                "avg_budget": 150000,
                "common_risks": ["Market saturation", "Technical scalability", "Customer acquisition"],
                "success_factors": ["Product-market fit", "Strong onboarding", "Customer support"]
            },
            "ecommerce": {
                "success_rate": 0.58,
                "avg_timeline": "8-12 weeks",
                "avg_budget": 45000,
                "common_risks": ["Competition", "Inventory management", "Payment processing"],
                "success_factors": ["Unique products", "SEO optimization", "Customer experience"]
            }
        }
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Cargar datos de mercado actuales"""
        return {
            "mobile_app_market": {
                "growth_rate": 0.15,
                "competition_level": "high",
                "trends": ["AI integration", "Privacy focus", "Subscription models"],
                "opportunities": ["Niche markets", "Emerging technologies", "Global expansion"]
            },
            "saas_market": {
                "growth_rate": 0.22,
                "competition_level": "very_high",
                "trends": ["AI-powered tools", "Remote work solutions", "Automation"],
                "opportunities": ["Vertical SaaS", "Integration platforms", "AI-first products"]
            },
            "ecommerce_market": {
                "growth_rate": 0.12,
                "competition_level": "extreme",
                "trends": ["Social commerce", "Sustainability", "Personalization"],
                "opportunities": ["Direct-to-consumer", "Subscription boxes", "Local markets"]
            }
        }
    
    def _initialize_ai_models(self) -> Dict[str, Any]:
        """Inicializar modelos de IA (simulados)"""
        return {
            "success_predictor": {
                "accuracy": 0.87,
                "features": ["complexity", "team_size", "budget", "timeline", "market_conditions"]
            },
            "timeline_estimator": {
                "accuracy": 0.82,
                "features": ["scope", "team_experience", "technology_stack", "dependencies"]
            },
            "budget_optimizer": {
                "accuracy": 0.79,
                "features": ["scope", "team_costs", "marketing_needs", "infrastructure"]
            },
            "risk_assessor": {
                "accuracy": 0.85,
                "features": ["market_conditions", "technical_complexity", "team_stability", "competition"]
            }
        }
    
    def analyze_launch_requirements_ai(self, requirements: str, scenario_type: str = "mobile_app") -> Dict[str, Any]:
        """Análisis avanzado de requisitos con IA"""
        
        # Análisis básico
        basic_analysis = self.base_planner.analyze_launch_requirements(requirements)
        
        # Análisis de mercado
        market_analysis = self._perform_market_analysis(scenario_type)
        
        # Predicciones de IA
        ai_predictions = self._generate_ai_predictions(requirements, basic_analysis, market_analysis)
        
        # Análisis de rendimiento
        performance_metrics = self._calculate_performance_metrics(basic_analysis)
        
        # Recomendaciones inteligentes
        recommendations = self._generate_smart_recommendations(
            basic_analysis, market_analysis, ai_predictions
        )
        
        return {
            "basic_analysis": basic_analysis,
            "market_analysis": market_analysis,
            "ai_predictions": ai_predictions,
            "performance_metrics": performance_metrics,
            "recommendations": recommendations,
            "confidence_score": self._calculate_confidence_score(ai_predictions)
        }
    
    def _perform_market_analysis(self, scenario_type: str) -> MarketAnalysis:
        """Realizar análisis de mercado"""
        market_data = self.market_data.get(f"{scenario_type}_market", self.market_data["mobile_app_market"])
        
        # Análisis de tamaño de mercado (simulado)
        market_sizes = {
            "mobile_app": 5000000000,  # $5B
            "saas_platform": 150000000000,  # $150B
            "ecommerce": 5000000000000  # $5T
        }
        
        # Análisis de audiencia objetivo
        target_audiences = {
            "mobile_app": {
                "primary": "Millennials and Gen Z (25-40 years)",
                "secondary": "Tech-savvy professionals",
                "geographic": "Global, focus on developed markets",
                "behavior": "Mobile-first, app-native users"
            },
            "saas_platform": {
                "primary": "Small to medium businesses",
                "secondary": "Enterprise teams",
                "geographic": "North America and Europe",
                "behavior": "Productivity-focused, ROI-conscious"
            },
            "ecommerce": {
                "primary": "Online shoppers (18-65 years)",
                "secondary": "Mobile commerce users",
                "geographic": "Local and regional markets",
                "behavior": "Price-sensitive, convenience-focused"
            }
        }
        
        return MarketAnalysis(
            market_size=market_sizes.get(scenario_type, 1000000000),
            competition_level=market_data["competition_level"],
            target_audience=target_audiences.get(scenario_type, target_audiences["mobile_app"]),
            market_trends=market_data["trends"],
            opportunities=market_data["opportunities"],
            threats=self._identify_market_threats(scenario_type),
            market_timing=self._assess_market_timing(scenario_type)
        )
    
    def _generate_ai_predictions(self, requirements: str, basic_analysis: Dict, market_analysis: MarketAnalysis) -> AIPrediction:
        """Generar predicciones de IA"""
        
        # Calcular probabilidad de éxito
        success_probability = self._calculate_success_probability(basic_analysis, market_analysis)
        
        # Estimar timeline optimizado
        estimated_timeline = self._estimate_optimized_timeline(basic_analysis)
        
        # Optimización de presupuesto
        budget_optimization = self._optimize_budget_allocation(basic_analysis, market_analysis)
        
        # Factores de riesgo
        risk_factors = self._identify_ai_risk_factors(basic_analysis, market_analysis)
        
        # Métricas de éxito
        success_metrics = self._predict_success_metrics(basic_analysis, market_analysis)
        
        # Recomendaciones
        recommendations = self._generate_ai_recommendations(basic_analysis, market_analysis)
        
        return AIPrediction(
            success_probability=success_probability,
            estimated_timeline=estimated_timeline,
            budget_optimization=budget_optimization,
            risk_factors=risk_factors,
            success_metrics=success_metrics,
            recommendations=recommendations
        )
    
    def _calculate_success_probability(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> float:
        """Calcular probabilidad de éxito usando IA"""
        base_probability = 0.5
        
        # Factores positivos
        if basic_analysis["complexity_score"] <= 3:
            base_probability += 0.15
        elif basic_analysis["complexity_score"] <= 5:
            base_probability += 0.10
        
        if market_analysis.competition_level in ["low", "medium"]:
            base_probability += 0.20
        elif market_analysis.competition_level == "high":
            base_probability += 0.10
        
        if len(basic_analysis["team_requirements"]) >= 3:
            base_probability += 0.10
        
        # Factores negativos
        if basic_analysis["complexity_score"] >= 7:
            base_probability -= 0.20
        
        if market_analysis.competition_level == "extreme":
            base_probability -= 0.15
        
        return max(0.1, min(0.95, base_probability))
    
    def _estimate_optimized_timeline(self, basic_analysis: Dict) -> str:
        """Estimar timeline optimizado"""
        complexity = basic_analysis["complexity_score"]
        
        if complexity <= 2:
            return "6-8 weeks"
        elif complexity <= 4:
            return "8-12 weeks"
        elif complexity <= 6:
            return "12-16 weeks"
        elif complexity <= 8:
            return "16-20 weeks"
        else:
            return "20-24 weeks"
    
    def _optimize_budget_allocation(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> Dict[str, float]:
        """Optimizar asignación de presupuesto"""
        total_budget = 100000  # Presupuesto base
        
        # Ajustar según complejidad
        if basic_analysis["complexity_score"] >= 5:
            total_budget *= 1.5
        elif basic_analysis["complexity_score"] >= 3:
            total_budget *= 1.2
        
        # Ajustar según competencia
        competition_multipliers = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3,
            "very_high": 1.5,
            "extreme": 2.0
        }
        
        total_budget *= competition_multipliers.get(market_analysis.competition_level, 1.0)
        
        return {
            "development": total_budget * 0.40,
            "marketing": total_budget * 0.30,
            "infrastructure": total_budget * 0.15,
            "team": total_budget * 0.10,
            "contingency": total_budget * 0.05
        }
    
    def _identify_ai_risk_factors(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> List[str]:
        """Identificar factores de riesgo usando IA"""
        risks = []
        
        # Riesgos técnicos
        if basic_analysis["complexity_score"] >= 6:
            risks.extend([
                "Alta complejidad técnica puede causar retrasos",
                "Riesgo de sobrecarga del equipo de desarrollo",
                "Posibles problemas de escalabilidad"
            ])
        
        # Riesgos de mercado
        if market_analysis.competition_level in ["very_high", "extreme"]:
            risks.extend([
                "Mercado altamente competitivo",
                "Dificultad para destacar entre competidores",
                "Posible guerra de precios"
            ])
        
        # Riesgos de recursos
        if len(basic_analysis["team_requirements"]) < 3:
            risks.append("Equipo insuficiente para la complejidad del proyecto")
        
        return risks
    
    def _predict_success_metrics(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> Dict[str, float]:
        """Predecir métricas de éxito"""
        base_users = 1000
        base_revenue = 10000
        
        # Ajustar según complejidad
        if basic_analysis["complexity_score"] >= 5:
            base_users *= 2
            base_revenue *= 3
        elif basic_analysis["complexity_score"] >= 3:
            base_users *= 1.5
            base_revenue *= 2
        
        # Ajustar según mercado
        market_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "very_high": 2.0,
            "extreme": 3.0
        }
        
        multiplier = market_multipliers.get(market_analysis.competition_level, 1.0)
        
        return {
            "target_users": base_users * multiplier,
            "target_revenue": base_revenue * multiplier,
            "market_share": min(5.0, multiplier * 0.5),
            "user_retention": 0.75 + (multiplier * 0.05),
            "conversion_rate": 0.03 + (multiplier * 0.01)
        }
    
    def _generate_ai_recommendations(self, basic_analysis: Dict, market_analysis: MarketAnalysis) -> List[str]:
        """Generar recomendaciones inteligentes"""
        recommendations = []
        
        # Recomendaciones basadas en complejidad
        if basic_analysis["complexity_score"] >= 6:
            recommendations.extend([
                "Considera dividir el proyecto en fases más pequeñas",
                "Invierte en herramientas de automatización",
                "Contrata desarrolladores senior con experiencia"
            ])
        
        # Recomendaciones basadas en mercado
        if market_analysis.competition_level in ["high", "very_high", "extreme"]:
            recommendations.extend([
                "Desarrolla un valor proposicional único y diferenciado",
                "Invierte fuertemente en marketing y branding",
                "Considera nichos de mercado menos saturados"
            ])
        
        # Recomendaciones generales
        recommendations.extend([
            "Implementa testing continuo desde el inicio",
            "Establece métricas claras de éxito",
            "Mantén comunicación constante con stakeholders"
        ])
        
        return recommendations
    
    def _calculate_performance_metrics(self, basic_analysis: Dict) -> PerformanceMetrics:
        """Calcular métricas de rendimiento"""
        complexity = basic_analysis["complexity_score"]
        
        # Velocidad de desarrollo (inversamente proporcional a complejidad)
        velocity = max(0.3, 1.0 - (complexity * 0.1))
        
        # Puntuación de calidad (basada en planificación)
        quality_score = 0.7 + (len(basic_analysis.get("team_requirements", [])) * 0.05)
        
        # Eficiencia del equipo
        team_efficiency = min(1.0, 0.6 + (len(basic_analysis.get("team_requirements", [])) * 0.1))
        
        # Utilización de recursos
        resource_utilization = 0.8 if complexity <= 5 else 0.9
        
        # Adherencia al cronograma
        timeline_adherence = max(0.5, 1.0 - (complexity * 0.08))
        
        return PerformanceMetrics(
            velocity=velocity,
            quality_score=quality_score,
            team_efficiency=team_efficiency,
            resource_utilization=resource_utilization,
            timeline_adherence=timeline_adherence
        )
    
    def _generate_smart_recommendations(self, basic_analysis: Dict, market_analysis: MarketAnalysis, ai_predictions: AIPrediction) -> List[str]:
        """Generar recomendaciones inteligentes combinadas"""
        recommendations = []
        
        # Recomendaciones de IA
        recommendations.extend(ai_predictions.recommendations)
        
        # Recomendaciones basadas en probabilidad de éxito
        if ai_predictions.success_probability < 0.6:
            recommendations.extend([
                "Considera reducir el alcance del proyecto",
                "Invierte más en investigación de mercado",
                "Desarrolla un MVP más simple"
            ])
        
        # Recomendaciones de optimización de presupuesto
        if ai_predictions.budget_optimization["marketing"] > ai_predictions.budget_optimization["development"]:
            recommendations.append("Considera aumentar el presupuesto de desarrollo")
        
        return list(set(recommendations))  # Eliminar duplicados
    
    def _calculate_confidence_score(self, ai_predictions: AIPrediction) -> float:
        """Calcular puntuación de confianza"""
        # Basado en la consistencia de las predicciones
        base_confidence = 0.8
        
        # Ajustar según la probabilidad de éxito
        if 0.4 <= ai_predictions.success_probability <= 0.8:
            base_confidence += 0.1
        elif ai_predictions.success_probability < 0.4 or ai_predictions.success_probability > 0.9:
            base_confidence -= 0.1
        
        return max(0.5, min(0.95, base_confidence))
    
    def _identify_market_threats(self, scenario_type: str) -> List[str]:
        """Identificar amenazas del mercado"""
        threats = {
            "mobile_app": [
                "Cambios en políticas de App Store",
                "Saturación del mercado de apps",
                "Competencia de apps gratuitas"
            ],
            "saas_platform": [
                "Consolidación del mercado",
                "Competencia de grandes empresas",
                "Cambios en regulaciones de datos"
            ],
            "ecommerce": [
                "Dominio de Amazon y grandes retailers",
                "Cambios en algoritmos de búsqueda",
                "Aumento de costos de adquisición"
            ]
        }
        
        return threats.get(scenario_type, threats["mobile_app"])
    
    def _assess_market_timing(self, scenario_type: str) -> str:
        """Evaluar timing del mercado"""
        # Análisis simplificado del timing
        current_trends = {
            "mobile_app": "Favorable - crecimiento continuo",
            "saas_platform": "Muy favorable - alta demanda",
            "ecommerce": "Competitivo - requiere diferenciación"
        }
        
        return current_trends.get(scenario_type, "Neutral")
    
    def create_enhanced_launch_plan(self, requirements: str, scenario_type: str = "mobile_app") -> Dict[str, Any]:
        """Crear plan de lanzamiento mejorado con IA"""
        
        # Análisis avanzado con IA
        enhanced_analysis = self.analyze_launch_requirements_ai(requirements, scenario_type)
        
        # Crear plan base
        base_plan = self.base_planner.create_custom_launch_plan(requirements, scenario_type)
        
        # Integrar análisis mejorado
        enhanced_plan = {
            **base_plan,
            "enhanced_analysis": enhanced_analysis,
            "ai_insights": {
                "success_probability": enhanced_analysis["ai_predictions"].success_probability,
                "confidence_score": enhanced_analysis["confidence_score"],
                "optimized_timeline": enhanced_analysis["ai_predictions"].estimated_timeline,
                "budget_optimization": enhanced_analysis["ai_predictions"].budget_optimization,
                "performance_metrics": enhanced_analysis["performance_metrics"].__dict__,
                "smart_recommendations": enhanced_analysis["recommendations"]
            },
            "market_intelligence": {
                "market_analysis": enhanced_analysis["market_analysis"].__dict__,
                "competitive_landscape": self._analyze_competitive_landscape(scenario_type),
                "market_opportunities": enhanced_analysis["market_analysis"].opportunities,
                "market_threats": enhanced_analysis["market_analysis"].threats
            }
        }
        
        return enhanced_plan
    
    def _analyze_competitive_landscape(self, scenario_type: str) -> Dict[str, Any]:
        """Analizar panorama competitivo"""
        competitive_data = {
            "mobile_app": {
                "top_competitors": ["Google", "Apple", "Meta", "TikTok"],
                "market_leaders": ["Google Play", "App Store"],
                "barriers_to_entry": ["App Store approval", "User acquisition costs"],
                "competitive_advantages": ["Unique features", "Better UX", "Niche focus"]
            },
            "saas_platform": {
                "top_competitors": ["Microsoft", "Salesforce", "HubSpot", "Slack"],
                "market_leaders": ["Microsoft 365", "Salesforce CRM"],
                "barriers_to_entry": ["High switching costs", "Network effects"],
                "competitive_advantages": ["Integration capabilities", "Pricing", "Customer support"]
            },
            "ecommerce": {
                "top_competitors": ["Amazon", "eBay", "Shopify", "WooCommerce"],
                "market_leaders": ["Amazon", "eBay"],
                "barriers_to_entry": ["Brand recognition", "Logistics", "Customer trust"],
                "competitive_advantages": ["Unique products", "Better pricing", "Customer experience"]
            }
        }
        
        return competitive_data.get(scenario_type, competitive_data["mobile_app"])
    
    def generate_enhanced_report(self, enhanced_plan: Dict[str, Any]) -> str:
        """Generar reporte mejorado con insights de IA"""
        
        ai_insights = enhanced_plan["ai_insights"]
        market_intelligence = enhanced_plan["market_intelligence"]
        
        report = f"""
# 🚀 Enhanced Launch Planning Report
*Generado con IA Avanzada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 🎯 Executive Summary
**Probabilidad de Éxito**: {ai_insights['success_probability']:.1%}
**Puntuación de Confianza**: {ai_insights['confidence_score']:.1%}
**Timeline Optimizado**: {ai_insights['optimized_timeline']}

## 🧠 AI Insights & Predictions

### Probabilidad de Éxito
- **Predicción de IA**: {ai_insights['success_probability']:.1%}
- **Nivel de Confianza**: {ai_insights['confidence_score']:.1%}
- **Factores Clave**: {', '.join(enhanced_plan['enhanced_analysis']['ai_predictions'].risk_factors[:3])}

### Optimización de Presupuesto
"""
        
        for category, amount in ai_insights['budget_optimization'].items():
            report += f"- **{category.title()}**: ${amount:,.0f}\n"
        
        report += f"""
### Métricas de Rendimiento Predichas
- **Velocidad de Desarrollo**: {ai_insights['performance_metrics']['velocity']:.1%}
- **Puntuación de Calidad**: {ai_insights['performance_metrics']['quality_score']:.1%}
- **Eficiencia del Equipo**: {ai_insights['performance_metrics']['team_efficiency']:.1%}
- **Utilización de Recursos**: {ai_insights['performance_metrics']['resource_utilization']:.1%}

## 📊 Market Intelligence

### Análisis de Mercado
- **Tamaño del Mercado**: ${market_intelligence['market_analysis']['market_size']:,.0f}
- **Nivel de Competencia**: {market_intelligence['market_analysis']['competition_level'].title()}
- **Timing del Mercado**: {market_intelligence['market_analysis']['market_timing']}

### Oportunidades Identificadas
"""
        
        for opportunity in market_intelligence['market_opportunities']:
            report += f"- {opportunity}\n"
        
        report += """
### Amenazas del Mercado
"""
        
        for threat in market_intelligence['market_threats']:
            report += f"- {threat}\n"
        
        report += f"""
## 🎯 Smart Recommendations

### Recomendaciones de IA
"""
        
        for i, recommendation in enumerate(ai_insights['smart_recommendations'][:10], 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
## 📈 Success Metrics Prediction

### Métricas Objetivo
- **Usuarios Objetivo**: {ai_insights['performance_metrics'].get('target_users', 'N/A'):,}
- **Ingresos Objetivo**: ${ai_insights['performance_metrics'].get('target_revenue', 'N/A'):,}
- **Cuota de Mercado**: {ai_insights['performance_metrics'].get('market_share', 'N/A'):.1f}%
- **Retención de Usuarios**: {ai_insights['performance_metrics'].get('user_retention', 'N/A'):.1%}

## ⚠️ Risk Assessment

### Factores de Riesgo Identificados
"""
        
        for risk in enhanced_plan['enhanced_analysis']['ai_predictions'].risk_factors:
            report += f"- {risk}\n"
        
        report += f"""
## 🚀 Next Steps

1. **Revisar y Aprobar** el plan de lanzamiento mejorado
2. **Implementar Recomendaciones** de IA prioritarias
3. **Configurar Monitoreo** de métricas de rendimiento
4. **Establecer Checkpoints** de revisión basados en predicciones
5. **Preparar Contingencias** para riesgos identificados

---
*Reporte generado por Enhanced Launch Planner con IA Avanzada*
*Confianza del Modelo: {ai_insights['confidence_score']:.1%}*
"""
        
        return report

def main():
    """Demostración del Enhanced Launch Planner"""
    print("🚀 Enhanced Launch Planner - Sistema Mejorado con IA")
    print("=" * 60)
    
    # Inicializar planner mejorado
    enhanced_planner = EnhancedLaunchPlanner()
    
    # Requisitos de ejemplo
    requirements = """
    Lanzar una plataforma SaaS de gestión de proyectos con IA.
    Objetivo: 5,000 usuarios pagos en el primer año.
    Presupuesto: $200,000 para desarrollo y marketing.
    Necesitamos 8 desarrolladores, 2 diseñadores, 1 especialista en IA.
    Debe integrar con Slack, Microsoft Teams, y sistemas de pago.
    Lanzamiento objetivo: Q3 2024.
    Prioridad alta para seguridad y escalabilidad.
    """
    
    print("🧠 Procesando requisitos con IA avanzada...")
    
    # Crear plan mejorado
    enhanced_plan = enhanced_planner.create_enhanced_launch_plan(requirements, "saas_platform")
    
    # Mostrar resultados
    ai_insights = enhanced_plan["ai_insights"]
    market_intelligence = enhanced_plan["market_intelligence"]
    
    print("✅ Plan de lanzamiento mejorado creado exitosamente!")
    print(f"   🎯 Probabilidad de Éxito: {ai_insights['success_probability']:.1%}")
    print(f"   🧠 Puntuación de Confianza: {ai_insights['confidence_score']:.1%}")
    print(f"   ⏱️  Timeline Optimizado: {ai_insights['optimized_timeline']}")
    print(f"   💰 Presupuesto Total: ${sum(ai_insights['budget_optimization'].values()):,.0f}")
    
    # Generar reporte mejorado
    enhanced_report = enhanced_planner.generate_enhanced_report(enhanced_plan)
    
    # Guardar archivos
    with open("enhanced_launch_plan.json", "w", encoding="utf-8") as f:
        json.dump({
            "enhanced_plan": {
                "ai_insights": ai_insights,
                "market_intelligence": market_intelligence,
                "basic_plan": enhanced_plan["scenario"]
            }
        }, f, indent=2, ensure_ascii=False)
    
    with open("enhanced_launch_report.md", "w", encoding="utf-8") as f:
        f.write(enhanced_report)
    
    with open("clickup_enhanced_workspace.json", "w", encoding="utf-8") as f:
        f.write(enhanced_plan["import_data"])
    
    print("\n📁 Archivos generados:")
    print("   • enhanced_launch_plan.json")
    print("   • enhanced_launch_report.md")
    print("   • clickup_enhanced_workspace.json")
    
    print("\n🎉 Enhanced Launch Planner demo completado!")
    print("   🚀 Sistema mejorado con IA listo para usar")

if __name__ == "__main__":
    main()









