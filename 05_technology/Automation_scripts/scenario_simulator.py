#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Escenarios de Marketing con IA
==========================================
Permite simular diferentes escenarios de mercado y evaluar el impacto en las campañas.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np
import random

class ScenarioSimulator:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el simulador de escenarios"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Escenarios de mercado predefinidos
        self.market_scenarios = {
            'recession': {
                'name': 'Recesión Económica',
                'description': 'Período de contracción económica con reducción en gastos de marketing',
                'budget_multiplier': 0.6,
                'conversion_multiplier': 0.7,
                'competition_multiplier': 1.3,
                'risk_multiplier': 1.5,
                'timeline_multiplier': 1.2,
                'success_probability_penalty': -0.1
            },
            'recovery': {
                'name': 'Recuperación Económica',
                'description': 'Período de recuperación con aumento gradual en inversión',
                'budget_multiplier': 1.1,
                'conversion_multiplier': 1.1,
                'competition_multiplier': 0.9,
                'risk_multiplier': 0.9,
                'timeline_multiplier': 0.95,
                'success_probability_penalty': 0.05
            },
            'growth': {
                'name': 'Crecimiento Económico',
                'description': 'Período de crecimiento sostenido con alta inversión',
                'budget_multiplier': 1.3,
                'conversion_multiplier': 1.2,
                'competition_multiplier': 0.8,
                'risk_multiplier': 0.8,
                'timeline_multiplier': 0.9,
                'success_probability_penalty': 0.08
            },
            'boom': {
                'name': 'Auge Económico',
                'description': 'Período de máximo crecimiento con inversión agresiva',
                'budget_multiplier': 1.6,
                'conversion_multiplier': 1.4,
                'competition_multiplier': 0.7,
                'risk_multiplier': 0.7,
                'timeline_multiplier': 0.85,
                'success_probability_penalty': 0.12
            },
            'crisis': {
                'name': 'Crisis Económica',
                'description': 'Crisis severa con restricciones presupuestarias extremas',
                'budget_multiplier': 0.4,
                'conversion_multiplier': 0.5,
                'competition_multiplier': 1.5,
                'risk_multiplier': 2.0,
                'timeline_multiplier': 1.4,
                'success_probability_penalty': -0.2
            },
            'disruption': {
                'name': 'Disrupción Tecnológica',
                'description': 'Cambios tecnológicos que afectan las estrategias de marketing',
                'budget_multiplier': 1.0,
                'conversion_multiplier': 0.8,
                'competition_multiplier': 1.2,
                'risk_multiplier': 1.3,
                'timeline_multiplier': 1.1,
                'success_probability_penalty': -0.05
            }
        }
        
        # Factores de industria por escenario
        self.industry_scenario_effects = {
            'E-commerce': {
                'recession': {'multiplier': 0.8, 'description': 'Reducción en compras no esenciales'},
                'recovery': {'multiplier': 1.1, 'description': 'Aumento gradual en compras online'},
                'growth': {'multiplier': 1.3, 'description': 'Expansión del comercio electrónico'},
                'boom': {'multiplier': 1.5, 'description': 'Máximo crecimiento del e-commerce'},
                'crisis': {'multiplier': 0.6, 'description': 'Caída drástica en ventas online'},
                'disruption': {'multiplier': 0.9, 'description': 'Adaptación a nuevas tecnologías'}
            },
            'Fintech': {
                'recession': {'multiplier': 1.2, 'description': 'Mayor demanda de servicios financieros digitales'},
                'recovery': {'multiplier': 1.1, 'description': 'Estabilización de servicios financieros'},
                'growth': {'multiplier': 1.4, 'description': 'Adopción masiva de fintech'},
                'boom': {'multiplier': 1.6, 'description': 'Revolución en servicios financieros'},
                'crisis': {'multiplier': 0.7, 'description': 'Reducción en inversión financiera'},
                'disruption': {'multiplier': 1.1, 'description': 'Oportunidades en nuevas tecnologías'}
            },
            'Healthcare': {
                'recession': {'multiplier': 1.1, 'description': 'Demanda estable de servicios de salud'},
                'recovery': {'multiplier': 1.0, 'description': 'Retorno a la normalidad en salud'},
                'growth': {'multiplier': 1.2, 'description': 'Inversión en salud digital'},
                'boom': {'multiplier': 1.4, 'description': 'Innovación en salud digital'},
                'crisis': {'multiplier': 1.3, 'description': 'Aumento en demanda de servicios de salud'},
                'disruption': {'multiplier': 1.0, 'description': 'Adaptación a nuevas tecnologías médicas'}
            }
        }
    
    def simulate_campaign_scenario(self, campaign_id: int, scenario_name: str, 
                                 custom_params: Dict = None) -> Dict[str, Any]:
        """Simula una campaña bajo un escenario específico"""
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        if scenario_name not in self.market_scenarios:
            return {"error": f"Escenario '{scenario_name}' no válido"}
        
        scenario = self.market_scenarios[scenario_name]
        
        # Aplicar parámetros personalizados si se proporcionan
        if custom_params:
            scenario = {**scenario, **custom_params}
        
        # Calcular métricas ajustadas
        adjusted_metrics = self._calculate_adjusted_metrics(campaign, scenario)
        
        # Aplicar efectos de industria
        industry_effect = self._get_industry_effect(campaign['vertical'], scenario_name)
        adjusted_metrics = self._apply_industry_effect(adjusted_metrics, industry_effect)
        
        # Calcular nuevos KPIs
        new_kpis = self._calculate_new_kpis(campaign, adjusted_metrics, scenario)
        
        # Análisis de sensibilidad
        sensitivity_analysis = self._calculate_sensitivity_analysis(campaign, scenario)
        
        # Recomendaciones específicas del escenario
        recommendations = self._generate_scenario_recommendations(campaign, scenario, adjusted_metrics)
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'scenario': scenario_name,
            'scenario_description': scenario['description'],
            'original_metrics': campaign['metrics'],
            'adjusted_metrics': adjusted_metrics,
            'new_kpis': new_kpis,
            'industry_effect': industry_effect,
            'sensitivity_analysis': sensitivity_analysis,
            'recommendations': recommendations,
            'simulation_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_adjusted_metrics(self, campaign: Dict, scenario: Dict) -> Dict[str, float]:
        """Calcula métricas ajustadas según el escenario"""
        original_metrics = campaign['metrics']
        adjusted = {}
        
        # Ajustar métricas de conversión
        conversion_metrics = ['conversion_rate', 'click_through_rate', 'engagement_rate']
        for metric in conversion_metrics:
            if metric in original_metrics:
                adjusted[metric] = original_metrics[metric] * scenario['conversion_multiplier']
        
        # Ajustar métricas de costo
        cost_metrics = ['cost_per_acquisition']
        for metric in cost_metrics:
            if metric in original_metrics:
                adjusted[metric] = original_metrics[metric] / scenario['conversion_multiplier']
        
        # Ajustar ROI
        if 'return_on_ad_spend' in original_metrics:
            adjusted['return_on_ad_spend'] = original_metrics['return_on_ad_spend'] * scenario['conversion_multiplier']
        
        # Ajustar métricas de valor
        value_metrics = ['customer_lifetime_value']
        for metric in value_metrics:
            if metric in original_metrics:
                adjusted[metric] = original_metrics[metric] * scenario['conversion_multiplier']
        
        # Ajustar métricas de alcance
        reach_metrics = ['social_media_reach', 'website_traffic_increase', 'lead_generation_increase']
        for metric in reach_metrics:
            if metric in original_metrics:
                adjusted[metric] = original_metrics[metric] * scenario['conversion_multiplier']
        
        # Mantener métricas que no se ven afectadas
        unaffected_metrics = ['email_open_rate', 'customer_satisfaction_score']
        for metric in unaffected_metrics:
            if metric in original_metrics:
                adjusted[metric] = original_metrics[metric]
        
        return adjusted
    
    def _get_industry_effect(self, industry: str, scenario_name: str) -> Dict[str, Any]:
        """Obtiene el efecto específico del escenario en la industria"""
        if industry in self.industry_scenario_effects:
            if scenario_name in self.industry_scenario_effects[industry]:
                return self.industry_scenario_effects[industry][scenario_name]
        
        # Efecto neutral por defecto
        return {'multiplier': 1.0, 'description': 'Sin efecto específico de industria'}
    
    def _apply_industry_effect(self, metrics: Dict[str, float], industry_effect: Dict[str, Any]) -> Dict[str, float]:
        """Aplica el efecto de la industria a las métricas"""
        multiplier = industry_effect['multiplier']
        
        # Aplicar multiplicador a métricas relevantes
        affected_metrics = ['conversion_rate', 'return_on_ad_spend', 'customer_lifetime_value']
        for metric in affected_metrics:
            if metric in metrics:
                metrics[metric] *= multiplier
        
        return metrics
    
    def _calculate_new_kpis(self, campaign: Dict, adjusted_metrics: Dict, scenario: Dict) -> Dict[str, Any]:
        """Calcula nuevos KPIs basados en el escenario"""
        original_budget = campaign['budget']['amount']
        adjusted_budget = original_budget * scenario['budget_multiplier']
        
        # Calcular ingresos ajustados
        original_roi = campaign['metrics']['return_on_ad_spend']
        adjusted_roi = adjusted_metrics['return_on_ad_spend']
        
        original_revenue = original_budget * original_roi
        adjusted_revenue = adjusted_budget * adjusted_roi
        
        # Calcular ganancia neta
        original_profit = original_revenue - original_budget
        adjusted_profit = adjusted_revenue - adjusted_budget
        
        # Calcular período de recuperación
        original_payback = original_budget / (original_revenue / 12) if original_revenue > 0 else float('inf')
        adjusted_payback = adjusted_budget / (adjusted_revenue / 12) if adjusted_revenue > 0 else float('inf')
        
        # Calcular probabilidad de éxito ajustada
        original_success_prob = campaign['success_probability']
        adjusted_success_prob = max(0, min(1, original_success_prob + scenario['success_probability_penalty']))
        
        # Calcular timeline ajustado
        original_timeline = campaign['timeline']['duration_weeks']
        adjusted_timeline = original_timeline * scenario['timeline_multiplier']
        
        return {
            'budget_analysis': {
                'original_budget': original_budget,
                'adjusted_budget': adjusted_budget,
                'budget_change_percent': ((adjusted_budget - original_budget) / original_budget) * 100
            },
            'revenue_analysis': {
                'original_revenue': original_revenue,
                'adjusted_revenue': adjusted_revenue,
                'revenue_change_percent': ((adjusted_revenue - original_revenue) / original_revenue) * 100
            },
            'profit_analysis': {
                'original_profit': original_profit,
                'adjusted_profit': adjusted_profit,
                'profit_change_percent': ((adjusted_profit - original_profit) / original_profit) * 100 if original_profit != 0 else 0
            },
            'roi_analysis': {
                'original_roi': original_roi,
                'adjusted_roi': adjusted_roi,
                'roi_change_percent': ((adjusted_roi - original_roi) / original_roi) * 100
            },
            'payback_analysis': {
                'original_payback_months': original_payback,
                'adjusted_payback_months': adjusted_payback,
                'payback_change_percent': ((adjusted_payback - original_payback) / original_payback) * 100 if original_payback != float('inf') else 0
            },
            'success_analysis': {
                'original_success_prob': original_success_prob,
                'adjusted_success_prob': adjusted_success_prob,
                'success_change_percent': ((adjusted_success_prob - original_success_prob) / original_success_prob) * 100
            },
            'timeline_analysis': {
                'original_weeks': original_timeline,
                'adjusted_weeks': adjusted_timeline,
                'timeline_change_percent': ((adjusted_timeline - original_timeline) / original_timeline) * 100
            }
        }
    
    def _calculate_sensitivity_analysis(self, campaign: Dict, scenario: Dict) -> Dict[str, Any]:
        """Calcula análisis de sensibilidad para el escenario"""
        # Simular variaciones en los parámetros del escenario
        variations = {
            'optimistic': {k: v * 1.2 if 'multiplier' in k else v for k, v in scenario.items()},
            'realistic': scenario,
            'pessimistic': {k: v * 0.8 if 'multiplier' in k else v for k, v in scenario.items()}
        }
        
        sensitivity_results = {}
        
        for variation_name, variation_params in variations.items():
            adjusted_metrics = self._calculate_adjusted_metrics(campaign, variation_params)
            industry_effect = self._get_industry_effect(campaign['vertical'], 'growth')  # Usar escenario base
            adjusted_metrics = self._apply_industry_effect(adjusted_metrics, industry_effect)
            
            sensitivity_results[variation_name] = {
                'roi': adjusted_metrics.get('return_on_ad_spend', 0),
                'conversion_rate': adjusted_metrics.get('conversion_rate', 0),
                'cost_per_acquisition': adjusted_metrics.get('cost_per_acquisition', 0),
                'customer_lifetime_value': adjusted_metrics.get('customer_lifetime_value', 0)
            }
        
        return sensitivity_results
    
    def _generate_scenario_recommendations(self, campaign: Dict, scenario: Dict, 
                                         adjusted_metrics: Dict) -> List[str]:
        """Genera recomendaciones específicas para el escenario"""
        recommendations = []
        
        scenario_name = scenario['name']
        
        # Recomendaciones generales por escenario
        if 'recession' in scenario_name.lower():
            recommendations.extend([
                "💰 **Reducir presupuesto**: Considerar reducir el presupuesto en un 20-30%",
                "🎯 **Enfocar en ROI**: Priorizar campañas con ROI más alto y recuperación rápida",
                "⏰ **Acelerar implementación**: Implementar más rápido para reducir costos",
                "🛡️ **Reducir riesgo**: Evitar campañas de alta complejidad y riesgo"
            ])
        elif 'growth' in scenario_name.lower() or 'boom' in scenario_name.lower():
            recommendations.extend([
                "🚀 **Aumentar presupuesto**: Considerar aumentar el presupuesto en un 30-50%",
                "📈 **Escalar rápidamente**: Aprovechar las condiciones favorables del mercado",
                "💡 **Innovar**: Invertir en tecnologías emergentes y campañas experimentales",
                "🎯 **Expandir alcance**: Llegar a nuevas audiencias y mercados"
            ])
        elif 'crisis' in scenario_name.lower():
            recommendations.extend([
                "⚠️ **Reconsiderar implementación**: Evaluar si es el momento adecuado",
                "💸 **Presupuesto mínimo**: Usar solo el presupuesto esencial",
                "🛡️ **Campañas de bajo riesgo**: Priorizar campañas con alta probabilidad de éxito",
                "⏸️ **Posponer si es necesario**: Considerar retrasar la implementación"
            ])
        
        # Recomendaciones basadas en métricas ajustadas
        adjusted_roi = adjusted_metrics.get('return_on_ad_spend', 0)
        if adjusted_roi < 3.0:
            recommendations.append("❌ **ROI bajo**: Considerar no implementar en este escenario")
        elif adjusted_roi > 8.0:
            recommendations.append("✅ **ROI excelente**: Implementar inmediatamente")
        
        # Recomendaciones basadas en la industria
        industry = campaign['vertical']
        if industry in ['E-commerce', 'Retail'] and 'recession' in scenario_name.lower():
            recommendations.append("🛒 **E-commerce resiliente**: El e-commerce tiende a ser más resiliente en recesiones")
        elif industry == 'Fintech' and 'growth' in scenario_name.lower():
            recommendations.append("💳 **Fintech en crecimiento**: Aprovechar el auge de los servicios financieros digitales")
        
        return recommendations
    
    def simulate_portfolio_scenario(self, campaign_ids: List[int], scenario_name: str) -> Dict[str, Any]:
        """Simula un portafolio de campañas bajo un escenario específico"""
        if scenario_name not in self.market_scenarios:
            return {"error": f"Escenario '{scenario_name}' no válido"}
        
        portfolio_results = []
        total_original_budget = 0
        total_adjusted_budget = 0
        total_original_revenue = 0
        total_adjusted_revenue = 0
        
        for campaign_id in campaign_ids:
            result = self.simulate_campaign_scenario(campaign_id, scenario_name)
            if 'error' not in result:
                portfolio_results.append(result)
                
                # Acumular totales
                total_original_budget += result['new_kpis']['budget_analysis']['original_budget']
                total_adjusted_budget += result['new_kpis']['budget_analysis']['adjusted_budget']
                total_original_revenue += result['new_kpis']['revenue_analysis']['original_revenue']
                total_adjusted_revenue += result['new_kpis']['revenue_analysis']['adjusted_revenue']
        
        if not portfolio_results:
            return {"error": "No se pudieron simular campañas válidas"}
        
        # Análisis del portafolio
        portfolio_analysis = {
            'total_campaigns': len(portfolio_results),
            'total_budget_change': ((total_adjusted_budget - total_original_budget) / total_original_budget) * 100,
            'total_revenue_change': ((total_adjusted_revenue - total_original_revenue) / total_original_revenue) * 100,
            'average_roi_change': np.mean([r['new_kpis']['roi_analysis']['roi_change_percent'] for r in portfolio_results]),
            'campaigns_improved': len([r for r in portfolio_results if r['new_kpis']['roi_analysis']['roi_change_percent'] > 0]),
            'campaigns_declined': len([r for r in portfolio_results if r['new_kpis']['roi_analysis']['roi_change_percent'] < 0])
        }
        
        return {
            'scenario': scenario_name,
            'portfolio_analysis': portfolio_analysis,
            'campaign_results': portfolio_results,
            'recommendations': self._generate_portfolio_recommendations(portfolio_analysis, scenario_name)
        }
    
    def _generate_portfolio_recommendations(self, portfolio_analysis: Dict, scenario_name: str) -> List[str]:
        """Genera recomendaciones para el portafolio completo"""
        recommendations = []
        
        # Recomendaciones basadas en el análisis del portafolio
        if portfolio_analysis['total_revenue_change'] > 20:
            recommendations.append("🚀 **Portafolio excelente**: El escenario favorece significativamente al portafolio")
        elif portfolio_analysis['total_revenue_change'] > 0:
            recommendations.append("✅ **Portafolio favorable**: El escenario beneficia al portafolio")
        elif portfolio_analysis['total_revenue_change'] > -20:
            recommendations.append("⚠️ **Portafolio neutral**: El escenario tiene impacto moderado")
        else:
            recommendations.append("❌ **Portafolio desfavorable**: Considerar ajustar la estrategia")
        
        # Recomendaciones basadas en campañas individuales
        improved_ratio = portfolio_analysis['campaigns_improved'] / portfolio_analysis['total_campaigns']
        if improved_ratio > 0.7:
            recommendations.append("📈 **Mayoría mejorada**: La mayoría de campañas se benefician del escenario")
        elif improved_ratio < 0.3:
            recommendations.append("📉 **Mayoría afectada**: La mayoría de campañas se ven afectadas negativamente")
        
        # Recomendaciones específicas del escenario
        if 'recession' in scenario_name.lower():
            recommendations.append("💡 **Estrategia de recesión**: Considerar pausar campañas de bajo ROI y enfocar en las de alto rendimiento")
        elif 'growth' in scenario_name.lower():
            recommendations.append("💡 **Estrategia de crecimiento**: Aprovechar para escalar campañas exitosas y experimentar con nuevas")
        
        return recommendations

def main():
    """Función principal de demostración"""
    print("=== SIMULADOR DE ESCENARIOS DE MARKETING ===")
    
    # Inicializar simulador
    simulator = ScenarioSimulator()
    
    # Simular campaña individual
    campaign_id = 1
    scenario = 'growth'
    
    print(f"Simulando campaña {campaign_id} bajo escenario '{scenario}'...")
    result = simulator.simulate_campaign_scenario(campaign_id, scenario)
    
    if 'error' not in result:
        print(f"\n📊 SIMULACIÓN DE CAMPAÑA")
        print(f"Campaña: {result['campaign_name']}")
        print(f"Escenario: {result['scenario_description']}")
        
        print(f"\n💰 ANÁLISIS FINANCIERO")
        budget = result['new_kpis']['budget_analysis']
        print(f"Presupuesto original: ${budget['original_budget']:,.2f}")
        print(f"Presupuesto ajustado: ${budget['adjusted_budget']:,.2f}")
        print(f"Cambio: {budget['budget_change_percent']:+.1f}%")
        
        roi = result['new_kpis']['roi_analysis']
        print(f"ROI original: {roi['original_roi']:.1f}x")
        print(f"ROI ajustado: {roi['adjusted_roi']:.1f}x")
        print(f"Cambio: {roi['roi_change_percent']:+.1f}%")
        
        print(f"\n💡 RECOMENDACIONES")
        for recommendation in result['recommendations']:
            print(f"• {recommendation}")
    
    # Simular portafolio
    print(f"\n🔄 SIMULANDO PORTAFOLIO...")
    portfolio_campaigns = [1, 2, 3, 4, 5]
    portfolio_result = simulator.simulate_portfolio_scenario(portfolio_campaigns, 'recession')
    
    if 'error' not in portfolio_result:
        print(f"\n📊 ANÁLISIS DE PORTAFOLIO")
        analysis = portfolio_result['portfolio_analysis']
        print(f"Total de campañas: {analysis['total_campaigns']}")
        print(f"Cambio en presupuesto: {analysis['total_budget_change']:+.1f}%")
        print(f"Cambio en ingresos: {analysis['total_revenue_change']:+.1f}%")
        print(f"Cambio promedio en ROI: {analysis['average_roi_change']:+.1f}%")
        print(f"Campañas mejoradas: {analysis['campaigns_improved']}")
        print(f"Campañas afectadas: {analysis['campaigns_declined']}")
        
        print(f"\n💡 RECOMENDACIONES DE PORTAFOLIO")
        for recommendation in portfolio_result['recommendations']:
            print(f"• {recommendation}")

if __name__ == "__main__":
    main()


