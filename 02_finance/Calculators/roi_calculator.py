#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de ROI Personalizada para Campañas de Marketing con IA
================================================================
Permite simular diferentes escenarios y calcular ROI personalizado.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np

class ROICalculator:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa la calculadora de ROI"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Factores de ajuste por industria
        self.industry_multipliers = {
            'E-commerce': {'conversion': 1.2, 'retention': 1.1, 'lifetime_value': 1.3},
            'Fintech': {'conversion': 1.5, 'retention': 1.4, 'lifetime_value': 2.0},
            'Healthcare': {'conversion': 1.1, 'retention': 1.3, 'lifetime_value': 1.8},
            'Education': {'conversion': 0.9, 'retention': 1.2, 'lifetime_value': 1.1},
            'Real Estate': {'conversion': 1.3, 'retention': 1.1, 'lifetime_value': 1.5},
            'Travel & Tourism': {'conversion': 1.0, 'retention': 0.9, 'lifetime_value': 1.2},
            'Food & Beverage': {'conversion': 0.8, 'retention': 0.9, 'lifetime_value': 0.9},
            'Fashion': {'conversion': 1.1, 'retention': 1.0, 'lifetime_value': 1.1},
            'Technology': {'conversion': 1.4, 'retention': 1.2, 'lifetime_value': 1.6},
            'Automotive': {'conversion': 1.2, 'retention': 1.1, 'lifetime_value': 1.4},
            'Entertainment': {'conversion': 0.9, 'retention': 0.8, 'lifetime_value': 1.0},
            'Fitness & Wellness': {'conversion': 1.0, 'retention': 1.1, 'lifetime_value': 1.2}
        }
        
        # Factores de ajuste por tamaño de empresa
        self.company_size_multipliers = {
            'startup': {'budget_efficiency': 1.3, 'implementation_speed': 1.2, 'risk': 1.1},
            'medium': {'budget_efficiency': 1.0, 'implementation_speed': 1.0, 'risk': 1.0},
            'enterprise': {'budget_efficiency': 0.8, 'implementation_speed': 0.9, 'risk': 0.9}
        }
    
    def calculate_base_roi(self, campaign: Dict) -> Dict[str, float]:
        """Calcula el ROI base de una campaña"""
        budget = campaign['budget']['amount']
        base_roi = campaign['metrics']['return_on_ad_spend']
        
        # Calcular ingresos esperados
        expected_revenue = budget * base_roi
        
        # Calcular ganancia neta
        net_profit = expected_revenue - budget
        
        # Calcular ROI porcentual
        roi_percentage = (net_profit / budget) * 100
        
        return {
            'budget': budget,
            'expected_revenue': expected_revenue,
            'net_profit': net_profit,
            'roi_multiplier': base_roi,
            'roi_percentage': roi_percentage,
            'payback_period_months': self.calculate_payback_period(budget, expected_revenue)
        }
    
    def calculate_payback_period(self, budget: float, expected_revenue: float) -> float:
        """Calcula el período de recuperación en meses"""
        if expected_revenue <= budget:
            return float('inf')
        
        monthly_revenue = expected_revenue / 12  # Asumiendo distribución anual
        return budget / monthly_revenue
    
    def apply_industry_adjustments(self, base_roi: Dict, industry: str) -> Dict[str, float]:
        """Aplica ajustes basados en la industria"""
        if industry not in self.industry_multipliers:
            return base_roi
        
        multipliers = self.industry_multipliers[industry]
        
        # Ajustar ingresos esperados
        adjusted_revenue = base_roi['expected_revenue'] * multipliers['lifetime_value']
        adjusted_profit = adjusted_revenue - base_roi['budget']
        adjusted_roi_percentage = (adjusted_profit / base_roi['budget']) * 100
        
        return {
            **base_roi,
            'expected_revenue': adjusted_revenue,
            'net_profit': adjusted_profit,
            'roi_percentage': adjusted_roi_percentage,
            'industry_adjustment': multipliers
        }
    
    def apply_company_size_adjustments(self, roi_data: Dict, company_size: str) -> Dict[str, float]:
        """Aplica ajustes basados en el tamaño de la empresa"""
        if company_size not in self.company_size_multipliers:
            return roi_data
        
        multipliers = self.company_size_multipliers[company_size]
        
        # Ajustar por eficiencia de presupuesto
        budget_efficiency = multipliers['budget_efficiency']
        adjusted_budget = roi_data['budget'] / budget_efficiency
        adjusted_revenue = roi_data['expected_revenue'] * budget_efficiency
        adjusted_profit = adjusted_revenue - adjusted_budget
        adjusted_roi_percentage = (adjusted_profit / adjusted_budget) * 100
        
        return {
            **roi_data,
            'budget': adjusted_budget,
            'expected_revenue': adjusted_revenue,
            'net_profit': adjusted_profit,
            'roi_percentage': adjusted_roi_percentage,
            'company_size_adjustment': multipliers
        }
    
    def simulate_scenario(self, campaign_id: int, scenario_params: Dict) -> Dict[str, Any]:
        """Simula un escenario específico para una campaña"""
        campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return {"error": f"Campaña {campaign_id} no encontrada"}
        
        # Parámetros del escenario
        industry = scenario_params.get('industry', campaign['vertical'])
        company_size = scenario_params.get('company_size', 'medium')
        market_conditions = scenario_params.get('market_conditions', 'normal')
        team_experience = scenario_params.get('team_experience', 'medium')
        budget_adjustment = scenario_params.get('budget_adjustment', 1.0)
        timeline_adjustment = scenario_params.get('timeline_adjustment', 1.0)
        
        # Calcular ROI base
        base_roi = self.calculate_base_roi(campaign)
        
        # Aplicar ajuste de presupuesto
        if budget_adjustment != 1.0:
            base_roi['budget'] *= budget_adjustment
            base_roi['expected_revenue'] *= budget_adjustment
            base_roi['net_profit'] = base_roi['expected_revenue'] - base_roi['budget']
            base_roi['roi_percentage'] = (base_roi['net_profit'] / base_roi['budget']) * 100
        
        # Aplicar ajustes de industria
        industry_adjusted = self.apply_industry_adjustments(base_roi, industry)
        
        # Aplicar ajustes de tamaño de empresa
        size_adjusted = self.apply_company_size_adjustments(industry_adjusted, company_size)
        
        # Aplicar condiciones de mercado
        market_multipliers = {
            'recession': 0.7,
            'normal': 1.0,
            'growth': 1.3,
            'boom': 1.6
        }
        
        market_multiplier = market_multipliers.get(market_conditions, 1.0)
        size_adjusted['expected_revenue'] *= market_multiplier
        size_adjusted['net_profit'] = size_adjusted['expected_revenue'] - size_adjusted['budget']
        size_adjusted['roi_percentage'] = (size_adjusted['net_profit'] / size_adjusted['budget']) * 100
        
        # Aplicar experiencia del equipo
        experience_multipliers = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.2,
            'expert': 1.4
        }
        
        experience_multiplier = experience_multipliers.get(team_experience, 1.0)
        size_adjusted['expected_revenue'] *= experience_multiplier
        size_adjusted['net_profit'] = size_adjusted['expected_revenue'] - size_adjusted['budget']
        size_adjusted['roi_percentage'] = (size_adjusted['net_profit'] / size_adjusted['budget']) * 100
        
        # Calcular métricas adicionales
        size_adjusted['roi_multiplier'] = size_adjusted['expected_revenue'] / size_adjusted['budget']
        size_adjusted['payback_period_months'] = self.calculate_payback_period(
            size_adjusted['budget'], size_adjusted['expected_revenue']
        )
        
        # Ajustar timeline
        original_timeline = campaign['timeline']['duration_weeks']
        adjusted_timeline = original_timeline * timeline_adjustment
        
        # Calcular sensibilidad
        sensitivity_analysis = self.calculate_sensitivity_analysis(size_adjusted, campaign)
        
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'scenario_params': scenario_params,
            'roi_analysis': size_adjusted,
            'timeline_analysis': {
                'original_weeks': original_timeline,
                'adjusted_weeks': adjusted_timeline,
                'timeline_change_percent': ((adjusted_timeline - original_timeline) / original_timeline) * 100
            },
            'sensitivity_analysis': sensitivity_analysis,
            'recommendations': self.generate_roi_recommendations(size_adjusted, scenario_params)
        }
    
    def calculate_sensitivity_analysis(self, roi_data: Dict, campaign: Dict) -> Dict[str, Any]:
        """Calcula análisis de sensibilidad para diferentes escenarios"""
        base_budget = roi_data['budget']
        base_revenue = roi_data['expected_revenue']
        
        # Escenarios de sensibilidad
        scenarios = {
            'optimistic': {'budget_multiplier': 0.8, 'revenue_multiplier': 1.3},
            'realistic': {'budget_multiplier': 1.0, 'revenue_multiplier': 1.0},
            'pessimistic': {'budget_multiplier': 1.2, 'revenue_multiplier': 0.7},
            'worst_case': {'budget_multiplier': 1.5, 'revenue_multiplier': 0.5}
        }
        
        sensitivity_results = {}
        
        for scenario_name, multipliers in scenarios.items():
            adjusted_budget = base_budget * multipliers['budget_multiplier']
            adjusted_revenue = base_revenue * multipliers['revenue_multiplier']
            adjusted_profit = adjusted_revenue - adjusted_budget
            adjusted_roi_percent = (adjusted_profit / adjusted_budget) * 100 if adjusted_budget > 0 else 0
            
            sensitivity_results[scenario_name] = {
                'budget': adjusted_budget,
                'revenue': adjusted_revenue,
                'profit': adjusted_profit,
                'roi_percentage': adjusted_roi_percent,
                'roi_multiplier': adjusted_revenue / adjusted_budget if adjusted_budget > 0 else 0
            }
        
        return sensitivity_results
    
    def generate_roi_recommendations(self, roi_data: Dict, scenario_params: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis de ROI"""
        recommendations = []
        
        roi_percentage = roi_data['roi_percentage']
        payback_period = roi_data['payback_period_months']
        
        # Recomendaciones basadas en ROI
        if roi_percentage >= 200:
            recommendations.append("🎯 **Excelente ROI**: Esta campaña ofrece un retorno excepcional. Priorizar implementación.")
        elif roi_percentage >= 100:
            recommendations.append("✅ **Buen ROI**: La campaña es rentable. Considerar implementación con monitoreo cuidadoso.")
        elif roi_percentage >= 50:
            recommendations.append("⚠️ **ROI moderado**: Evaluar cuidadosamente antes de implementar. Considerar optimizaciones.")
        else:
            recommendations.append("❌ **ROI bajo**: No recomendado para implementación. Buscar alternativas.")
        
        # Recomendaciones basadas en período de recuperación
        if payback_period <= 6:
            recommendations.append("⚡ **Recuperación rápida**: El presupuesto se recuperará en menos de 6 meses.")
        elif payback_period <= 12:
            recommendations.append("📅 **Recuperación moderada**: El presupuesto se recuperará en 6-12 meses.")
        else:
            recommendations.append("⏰ **Recuperación lenta**: Considerar si el período de recuperación es aceptable.")
        
        # Recomendaciones basadas en presupuesto
        budget = roi_data['budget']
        if budget < 25000:
            recommendations.append("💰 **Presupuesto accesible**: Ideal para pruebas piloto o empresas pequeñas.")
        elif budget < 100000:
            recommendations.append("💼 **Presupuesto moderado**: Adecuado para empresas medianas.")
        else:
            recommendations.append("🏢 **Presupuesto alto**: Requiere aprobación ejecutiva y análisis detallado.")
        
        # Recomendaciones basadas en condiciones de mercado
        market_conditions = scenario_params.get('market_conditions', 'normal')
        if market_conditions == 'recession':
            recommendations.append("📉 **Mercado recesivo**: Considerar reducir presupuesto o posponer implementación.")
        elif market_conditions == 'boom':
            recommendations.append("📈 **Mercado en auge**: Oportunidad ideal para implementar y escalar rápidamente.")
        
        return recommendations
    
    def compare_scenarios(self, campaign_id: int, scenarios: List[Dict]) -> Dict[str, Any]:
        """Compara múltiples escenarios para una campaña"""
        results = []
        
        for i, scenario in enumerate(scenarios, 1):
            result = self.simulate_scenario(campaign_id, scenario)
            if 'error' not in result:
                result['scenario_number'] = i
                results.append(result)
        
        if not results:
            return {"error": "No se pudieron simular escenarios válidos"}
        
        # Análisis comparativo
        roi_percentages = [r['roi_analysis']['roi_percentage'] for r in results]
        budgets = [r['roi_analysis']['budget'] for r in results]
        
        best_scenario = max(results, key=lambda x: x['roi_analysis']['roi_percentage'])
        worst_scenario = min(results, key=lambda x: x['roi_analysis']['roi_percentage'])
        
        return {
            'campaign_id': campaign_id,
            'total_scenarios': len(results),
            'best_scenario': best_scenario,
            'worst_scenario': worst_scenario,
            'average_roi': np.mean(roi_percentages),
            'roi_std': np.std(roi_percentages),
            'scenarios': results,
            'recommendations': self.generate_scenario_recommendations(results)
        }
    
    def generate_scenario_recommendations(self, scenarios: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en la comparación de escenarios"""
        recommendations = []
        
        if not scenarios:
            return recommendations
        
        # Encontrar el mejor escenario
        best = max(scenarios, key=lambda x: x['roi_analysis']['roi_percentage'])
        worst = min(scenarios, key=lambda x: x['roi_analysis']['roi_percentage'])
        
        recommendations.append(f"🏆 **Mejor escenario**: {best['scenario_params']} con ROI del {best['roi_analysis']['roi_percentage']:.1f}%")
        
        # Análisis de variabilidad
        roi_values = [s['roi_analysis']['roi_percentage'] for s in scenarios]
        roi_std = np.std(roi_values)
        
        if roi_std < 10:
            recommendations.append("📊 **Baja variabilidad**: Los resultados son consistentes entre escenarios.")
        elif roi_std < 25:
            recommendations.append("📊 **Variabilidad moderada**: Los resultados varían moderadamente entre escenarios.")
        else:
            recommendations.append("📊 **Alta variabilidad**: Los resultados varían significativamente. Revisar parámetros.")
        
        # Recomendación de implementación
        avg_roi = np.mean(roi_values)
        if avg_roi >= 100:
            recommendations.append("✅ **Implementación recomendada**: El ROI promedio es favorable.")
        elif avg_roi >= 50:
            recommendations.append("⚠️ **Implementación condicional**: Evaluar cuidadosamente los riesgos.")
        else:
            recommendations.append("❌ **No recomendado**: El ROI promedio es insuficiente.")
        
        return recommendations
    
    def generate_roi_report(self, campaign_id: int, scenarios: List[Dict], output_file: str = None) -> Dict[str, Any]:
        """Genera un reporte completo de ROI"""
        comparison = self.compare_scenarios(campaign_id, scenarios)
        
        if 'error' in comparison:
            return comparison
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'campaign_id': campaign_id,
            'campaign_name': comparison['scenarios'][0]['campaign_name'],
            'comparison_analysis': comparison,
            'summary': {
                'total_scenarios': comparison['total_scenarios'],
                'best_roi': comparison['best_scenario']['roi_analysis']['roi_percentage'],
                'worst_roi': comparison['worst_scenario']['roi_analysis']['roi_percentage'],
                'average_roi': comparison['average_roi'],
                'roi_volatility': comparison['roi_std']
            }
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report

def main():
    """Función principal de demostración"""
    print("=== CALCULADORA DE ROI PERSONALIZADA ===")
    
    # Inicializar calculadora
    calculator = ROICalculator()
    
    # Ejemplo de simulación de escenario
    campaign_id = 1
    scenario_params = {
        'industry': 'E-commerce',
        'company_size': 'medium',
        'market_conditions': 'growth',
        'team_experience': 'high',
        'budget_adjustment': 1.2,
        'timeline_adjustment': 0.9
    }
    
    print(f"Simulando escenario para campaña {campaign_id}...")
    result = calculator.simulate_scenario(campaign_id, scenario_params)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n📊 ANÁLISIS DE ROI")
    print(f"Campaña: {result['campaign_name']}")
    print(f"Presupuesto: ${result['roi_analysis']['budget']:,.2f}")
    print(f"Ingresos esperados: ${result['roi_analysis']['expected_revenue']:,.2f}")
    print(f"Ganancia neta: ${result['roi_analysis']['net_profit']:,.2f}")
    print(f"ROI: {result['roi_analysis']['roi_percentage']:.1f}%")
    print(f"Multiplicador: {result['roi_analysis']['roi_multiplier']:.1f}x")
    print(f"Período de recuperación: {result['roi_analysis']['payback_period_months']:.1f} meses")
    
    print(f"\n💡 RECOMENDACIONES")
    for recommendation in result['recommendations']:
        print(f"• {recommendation}")
    
    # Ejemplo de comparación de escenarios
    scenarios = [
        {'industry': 'E-commerce', 'company_size': 'startup', 'market_conditions': 'normal'},
        {'industry': 'E-commerce', 'company_size': 'medium', 'market_conditions': 'growth'},
        {'industry': 'E-commerce', 'company_size': 'enterprise', 'market_conditions': 'boom'}
    ]
    
    print(f"\n🔄 COMPARANDO {len(scenarios)} ESCENARIOS...")
    comparison = calculator.compare_scenarios(campaign_id, scenarios)
    
    if 'error' not in comparison:
        print(f"Mejor ROI: {comparison['best_scenario']['roi_analysis']['roi_percentage']:.1f}%")
        print(f"Peor ROI: {comparison['worst_scenario']['roi_analysis']['roi_percentage']:.1f}%")
        print(f"ROI promedio: {comparison['average_roi']:.1f}%")
        
        print(f"\n💡 RECOMENDACIONES DE ESCENARIOS")
        for recommendation in comparison['recommendations']:
            print(f"• {recommendation}")
    
    # Generar reporte
    report = calculator.generate_roi_report(campaign_id, scenarios, 'roi_analysis_report.json')
    print(f"\n📄 Reporte de ROI guardado en: roi_analysis_report.json")

if __name__ == "__main__":
    main()


