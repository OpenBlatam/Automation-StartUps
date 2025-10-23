#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizador Automático de Presupuestos para Campañas de Marketing con IA
=======================================================================
Utiliza algoritmos de optimización para distribuir presupuestos de manera óptima.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
from scipy.optimize import minimize, differential_evolution
import warnings
warnings.filterwarnings('ignore')

class BudgetOptimizer:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el optimizador de presupuestos"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Parámetros de optimización
        self.optimization_methods = {
            'maximize_roi': self._maximize_roi,
            'maximize_conversions': self._maximize_conversions,
            'minimize_risk': self._minimize_risk,
            'balanced_approach': self._balanced_approach
        }
    
    def optimize_portfolio_budget(self, total_budget: float, 
                                campaign_ids: List[int] = None,
                                optimization_method: str = 'balanced_approach',
                                constraints: Dict = None) -> Dict[str, Any]:
        """Optimiza la distribución de presupuesto en un portafolio de campañas"""
        
        if campaign_ids is None:
            # Usar todas las campañas si no se especifican
            campaign_ids = list(range(1, len(self.campaigns) + 1))
        
        # Filtrar campañas válidas
        valid_campaigns = []
        for campaign_id in campaign_ids:
            campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
            if campaign:
                valid_campaigns.append(campaign)
        
        if not valid_campaigns:
            return {"error": "No se encontraron campañas válidas"}
        
        # Preparar datos para optimización
        campaign_data = self._prepare_campaign_data(valid_campaigns)
        
        # Aplicar restricciones
        if constraints:
            campaign_data = self._apply_constraints(campaign_data, constraints)
        
        # Ejecutar optimización
        optimization_func = self.optimization_methods.get(optimization_method, self._balanced_approach)
        result = optimization_func(campaign_data, total_budget)
        
        # Generar reporte de optimización
        optimization_report = self._generate_optimization_report(
            campaign_data, result, total_budget, optimization_method
        )
        
        return optimization_report
    
    def _prepare_campaign_data(self, campaigns: List[Dict]) -> pd.DataFrame:
        """Prepara los datos de campañas para optimización"""
        data = []
        
        for campaign in campaigns:
            metrics = campaign['metrics']
            
            # Calcular métricas de eficiencia
            roi = metrics.get('return_on_ad_spend', 0)
            conversion_rate = metrics.get('conversion_rate', 0)
            cost_per_acquisition = metrics.get('cost_per_acquisition', 0)
            success_probability = campaign['success_probability']
            
            # Calcular score de eficiencia
            efficiency_score = (roi * success_probability) / 10
            
            # Calcular riesgo (inverso de probabilidad de éxito)
            risk_score = 1 - success_probability
            
            data.append({
                'id': campaign['id'],
                'name': campaign['name'],
                'category': campaign['category'],
                'vertical': campaign['vertical'],
                'current_budget': campaign['budget']['amount'],
                'min_budget': campaign['budget']['amount'] * 0.5,  # Mínimo 50% del presupuesto actual
                'max_budget': campaign['budget']['amount'] * 2.0,  # Máximo 200% del presupuesto actual
                'roi': roi,
                'conversion_rate': conversion_rate,
                'cost_per_acquisition': cost_per_acquisition,
                'success_probability': success_probability,
                'efficiency_score': efficiency_score,
                'risk_score': risk_score,
                'complexity': campaign['complexity'],
                'priority': campaign['priority']
            })
        
        return pd.DataFrame(data)
    
    def _apply_constraints(self, campaign_data: pd.DataFrame, constraints: Dict) -> pd.DataFrame:
        """Aplica restricciones a los datos de campañas"""
        # Filtrar por categoría
        if 'categories' in constraints:
            campaign_data = campaign_data[campaign_data['category'].isin(constraints['categories'])]
        
        # Filtrar por vertical
        if 'verticals' in constraints:
            campaign_data = campaign_data[campaign_data['vertical'].isin(constraints['verticals'])]
        
        # Filtrar por complejidad
        if 'complexities' in constraints:
            campaign_data = campaign_data[campaign_data['complexity'].isin(constraints['complexities'])]
        
        # Filtrar por prioridad
        if 'priorities' in constraints:
            campaign_data = campaign_data[campaign_data['priority'].isin(constraints['priorities'])]
        
        # Filtrar por ROI mínimo
        if 'min_roi' in constraints:
            campaign_data = campaign_data[campaign_data['roi'] >= constraints['min_roi']]
        
        # Filtrar por probabilidad de éxito mínima
        if 'min_success_probability' in constraints:
            campaign_data = campaign_data[campaign_data['success_probability'] >= constraints['min_success_probability']]
        
        return campaign_data
    
    def _maximize_roi(self, campaign_data: pd.DataFrame, total_budget: float) -> Dict[str, Any]:
        """Optimiza para maximizar ROI total"""
        n_campaigns = len(campaign_data)
        
        # Función objetivo: maximizar ROI total
        def objective(budgets):
            total_roi = 0
            for i, budget in enumerate(budgets):
                if i < n_campaigns:
                    roi = campaign_data.iloc[i]['roi']
                    success_prob = campaign_data.iloc[i]['success_probability']
                    # ROI esperado = ROI * Probabilidad de éxito
                    expected_roi = roi * success_prob
                    total_roi += budget * expected_roi
            return -total_roi  # Minimizar el negativo para maximizar
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - total_budget}  # Presupuesto total
        ]
        
        # Límites de presupuesto por campaña
        bounds = []
        for i in range(n_campaigns):
            min_budget = campaign_data.iloc[i]['min_budget']
            max_budget = campaign_data.iloc[i]['max_budget']
            bounds.append((min_budget, max_budget))
        
        # Punto inicial (distribución uniforme)
        x0 = [total_budget / n_campaigns] * n_campaigns
        
        # Optimizar
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return {
            'method': 'maximize_roi',
            'success': result.success,
            'optimized_budgets': result.x.tolist(),
            'total_roi': -result.fun,
            'optimization_details': result
        }
    
    def _maximize_conversions(self, campaign_data: pd.DataFrame, total_budget: float) -> Dict[str, Any]:
        """Optimiza para maximizar conversiones totales"""
        n_campaigns = len(campaign_data)
        
        # Función objetivo: maximizar conversiones totales
        def objective(budgets):
            total_conversions = 0
            for i, budget in enumerate(budgets):
                if i < n_campaigns:
                    conversion_rate = campaign_data.iloc[i]['conversion_rate']
                    success_prob = campaign_data.iloc[i]['success_probability']
                    # Conversiones esperadas = (Presupuesto / CPA) * Tasa de conversión * Probabilidad de éxito
                    cpa = campaign_data.iloc[i]['cost_per_acquisition']
                    if cpa > 0:
                        expected_conversions = (budget / cpa) * (conversion_rate / 100) * success_prob
                        total_conversions += expected_conversions
            return -total_conversions  # Minimizar el negativo para maximizar
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - total_budget}  # Presupuesto total
        ]
        
        # Límites de presupuesto por campaña
        bounds = []
        for i in range(n_campaigns):
            min_budget = campaign_data.iloc[i]['min_budget']
            max_budget = campaign_data.iloc[i]['max_budget']
            bounds.append((min_budget, max_budget))
        
        # Punto inicial (distribución uniforme)
        x0 = [total_budget / n_campaigns] * n_campaigns
        
        # Optimizar
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return {
            'method': 'maximize_conversions',
            'success': result.success,
            'optimized_budgets': result.x.tolist(),
            'total_conversions': -result.fun,
            'optimization_details': result
        }
    
    def _minimize_risk(self, campaign_data: pd.DataFrame, total_budget: float) -> Dict[str, Any]:
        """Optimiza para minimizar riesgo total"""
        n_campaigns = len(campaign_data)
        
        # Función objetivo: minimizar riesgo total (maximizar probabilidad de éxito)
        def objective(budgets):
            total_risk = 0
            for i, budget in enumerate(budgets):
                if i < n_campaigns:
                    risk_score = campaign_data.iloc[i]['risk_score']
                    # Riesgo ponderado por presupuesto
                    weighted_risk = budget * risk_score
                    total_risk += weighted_risk
            return total_risk
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - total_budget}  # Presupuesto total
        ]
        
        # Límites de presupuesto por campaña
        bounds = []
        for i in range(n_campaigns):
            min_budget = campaign_data.iloc[i]['min_budget']
            max_budget = campaign_data.iloc[i]['max_budget']
            bounds.append((min_budget, max_budget))
        
        # Punto inicial (distribución uniforme)
        x0 = [total_budget / n_campaigns] * n_campaigns
        
        # Optimizar
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return {
            'method': 'minimize_risk',
            'success': result.success,
            'optimized_budgets': result.x.tolist(),
            'total_risk': result.fun,
            'optimization_details': result
        }
    
    def _balanced_approach(self, campaign_data: pd.DataFrame, total_budget: float) -> Dict[str, Any]:
        """Optimiza usando un enfoque balanceado (ROI, conversiones y riesgo)"""
        n_campaigns = len(campaign_data)
        
        # Función objetivo: balancear ROI, conversiones y riesgo
        def objective(budgets):
            total_score = 0
            for i, budget in enumerate(budgets):
                if i < n_campaigns:
                    roi = campaign_data.iloc[i]['roi']
                    conversion_rate = campaign_data.iloc[i]['conversion_rate']
                    success_prob = campaign_data.iloc[i]['success_probability']
                    risk_score = campaign_data.iloc[i]['risk_score']
                    
                    # Score balanceado: ROI * Conversiones * Probabilidad de éxito - Riesgo
                    roi_score = roi * success_prob
                    conversion_score = (conversion_rate / 100) * success_prob
                    risk_penalty = risk_score * 0.5  # Penalización por riesgo
                    
                    balanced_score = (roi_score + conversion_score - risk_penalty) * budget
                    total_score += balanced_score
            return -total_score  # Minimizar el negativo para maximizar
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - total_budget}  # Presupuesto total
        ]
        
        # Límites de presupuesto por campaña
        bounds = []
        for i in range(n_campaigns):
            min_budget = campaign_data.iloc[i]['min_budget']
            max_budget = campaign_data.iloc[i]['max_budget']
            bounds.append((min_budget, max_budget))
        
        # Punto inicial (distribución uniforme)
        x0 = [total_budget / n_campaigns] * n_campaigns
        
        # Optimizar
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        return {
            'method': 'balanced_approach',
            'success': result.success,
            'optimized_budgets': result.x.tolist(),
            'total_score': -result.fun,
            'optimization_details': result
        }
    
    def _generate_optimization_report(self, campaign_data: pd.DataFrame, 
                                    result: Dict, total_budget: float, 
                                    method: str) -> Dict[str, Any]:
        """Genera un reporte detallado de la optimización"""
        
        if not result['success']:
            return {
                'error': 'La optimización no convergió exitosamente',
                'method': method,
                'total_budget': total_budget
            }
        
        optimized_budgets = result['optimized_budgets']
        
        # Calcular métricas de la optimización
        total_allocated = sum(optimized_budgets)
        budget_utilization = (total_allocated / total_budget) * 100
        
        # Calcular ROI total esperado
        total_expected_roi = 0
        total_expected_conversions = 0
        total_expected_revenue = 0
        
        campaign_results = []
        
        for i, budget in enumerate(optimized_budgets):
            if i < len(campaign_data):
                campaign = campaign_data.iloc[i]
                
                # Métricas esperadas
                roi = campaign['roi']
                success_prob = campaign['success_probability']
                conversion_rate = campaign['conversion_rate']
                cpa = campaign['cost_per_acquisition']
                
                expected_roi = roi * success_prob
                expected_revenue = budget * expected_roi
                expected_conversions = (budget / cpa) * (conversion_rate / 100) * success_prob if cpa > 0 else 0
                
                total_expected_roi += expected_roi
                total_expected_conversions += expected_conversions
                total_expected_revenue += expected_revenue
                
                # Cambio en presupuesto
                budget_change = ((budget - campaign['current_budget']) / campaign['current_budget']) * 100
                
                campaign_results.append({
                    'campaign_id': campaign['id'],
                    'campaign_name': campaign['name'],
                    'category': campaign['category'],
                    'vertical': campaign['vertical'],
                    'current_budget': campaign['current_budget'],
                    'optimized_budget': budget,
                    'budget_change_percent': budget_change,
                    'expected_roi': expected_roi,
                    'expected_revenue': expected_revenue,
                    'expected_conversions': expected_conversions,
                    'efficiency_score': campaign['efficiency_score'],
                    'risk_score': campaign['risk_score']
                })
        
        # Ordenar por presupuesto optimizado
        campaign_results.sort(key=lambda x: x['optimized_budget'], reverse=True)
        
        # Generar recomendaciones
        recommendations = self._generate_optimization_recommendations(campaign_results, method)
        
        return {
            'optimization_method': method,
            'total_budget': total_budget,
            'total_allocated': total_allocated,
            'budget_utilization_percent': budget_utilization,
            'total_expected_roi': total_expected_roi,
            'total_expected_conversions': total_expected_conversions,
            'total_expected_revenue': total_expected_revenue,
            'campaign_results': campaign_results,
            'recommendations': recommendations,
            'optimization_timestamp': datetime.now().isoformat()
        }
    
    def _generate_optimization_recommendations(self, campaign_results: List[Dict], method: str) -> List[str]:
        """Genera recomendaciones basadas en los resultados de optimización"""
        recommendations = []
        
        # Análisis de distribución de presupuesto
        high_budget_campaigns = [c for c in campaign_results if c['optimized_budget'] > 50000]
        low_budget_campaigns = [c for c in campaign_results if c['optimized_budget'] < 10000]
        
        if high_budget_campaigns:
            recommendations.append(f"💰 **{len(high_budget_campaigns)} campañas de alto presupuesto**: Priorizar implementación y monitoreo")
        
        if low_budget_campaigns:
            recommendations.append(f"🔍 **{len(low_budget_campaigns)} campañas de bajo presupuesto**: Considerar si el presupuesto es suficiente")
        
        # Análisis de cambios de presupuesto
        increased_budget = [c for c in campaign_results if c['budget_change_percent'] > 20]
        decreased_budget = [c for c in campaign_results if c['budget_change_percent'] < -20]
        
        if increased_budget:
            recommendations.append(f"📈 **{len(increased_budget)} campañas con aumento significativo**: Aprovechar el potencial identificado")
        
        if decreased_budget:
            recommendations.append(f"📉 **{len(decreased_budget)} campañas con reducción significativa**: Revisar viabilidad con presupuesto reducido")
        
        # Recomendaciones específicas por método
        if method == 'maximize_roi':
            recommendations.append("🎯 **Enfoque en ROI**: La optimización prioriza el retorno de inversión")
        elif method == 'maximize_conversions':
            recommendations.append("🔄 **Enfoque en conversiones**: La optimización prioriza el volumen de conversiones")
        elif method == 'minimize_risk':
            recommendations.append("🛡️ **Enfoque en riesgo**: La optimización prioriza campañas de bajo riesgo")
        else:
            recommendations.append("⚖️ **Enfoque balanceado**: La optimización considera múltiples factores")
        
        # Recomendaciones de implementación
        total_expected_revenue = sum(c['expected_revenue'] for c in campaign_results)
        total_budget = sum(c['optimized_budget'] for c in campaign_results)
        overall_roi = total_expected_revenue / total_budget if total_budget > 0 else 0
        
        if overall_roi > 5:
            recommendations.append("✅ **ROI excelente**: El portafolio optimizado ofrece un retorno excepcional")
        elif overall_roi > 3:
            recommendations.append("👍 **ROI bueno**: El portafolio optimizado es rentable")
        else:
            recommendations.append("⚠️ **ROI moderado**: Considerar revisar la selección de campañas")
        
        return recommendations
    
    def compare_optimization_methods(self, total_budget: float, 
                                   campaign_ids: List[int] = None) -> Dict[str, Any]:
        """Compara diferentes métodos de optimización"""
        
        if campaign_ids is None:
            campaign_ids = list(range(1, min(51, len(self.campaigns) + 1)))  # Límite a 50 campañas para comparación
        
        comparison_results = {}
        
        for method_name in self.optimization_methods.keys():
            result = self.optimize_portfolio_budget(
                total_budget=total_budget,
                campaign_ids=campaign_ids,
                optimization_method=method_name
            )
            
            if 'error' not in result:
                comparison_results[method_name] = {
                    'total_expected_roi': result['total_expected_roi'],
                    'total_expected_conversions': result['total_expected_conversions'],
                    'total_expected_revenue': result['total_expected_revenue'],
                    'budget_utilization_percent': result['budget_utilization_percent'],
                    'campaign_count': len(result['campaign_results'])
                }
        
        # Encontrar mejor método para cada métrica
        best_methods = {}
        if comparison_results:
            best_methods['highest_roi'] = max(comparison_results.keys(), 
                                            key=lambda x: comparison_results[x]['total_expected_roi'])
            best_methods['highest_conversions'] = max(comparison_results.keys(), 
                                                    key=lambda x: comparison_results[x]['total_expected_conversions'])
            best_methods['highest_revenue'] = max(comparison_results.keys(), 
                                                key=lambda x: comparison_results[x]['total_expected_revenue'])
        
        return {
            'comparison_results': comparison_results,
            'best_methods': best_methods,
            'total_budget': total_budget,
            'campaign_count': len(campaign_ids),
            'comparison_timestamp': datetime.now().isoformat()
        }

def main():
    """Función principal de demostración"""
    print("=== OPTIMIZADOR AUTOMÁTICO DE PRESUPUESTOS ===")
    
    # Inicializar optimizador
    optimizer = BudgetOptimizer()
    
    # Ejemplo de optimización
    total_budget = 500000
    campaign_ids = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30]
    
    print(f"Optimizando presupuesto de ${total_budget:,} para {len(campaign_ids)} campañas...")
    
    # Optimización balanceada
    result = optimizer.optimize_portfolio_budget(
        total_budget=total_budget,
        campaign_ids=campaign_ids,
        optimization_method='balanced_approach'
    )
    
    if 'error' not in result:
        print(f"\n📊 RESULTADOS DE OPTIMIZACIÓN")
        print(f"Método: {result['optimization_method']}")
        print(f"Presupuesto total: ${result['total_budget']:,}")
        print(f"Presupuesto asignado: ${result['total_allocated']:,.2f}")
        print(f"Utilización: {result['budget_utilization_percent']:.1f}%")
        print(f"ROI total esperado: {result['total_expected_roi']:.2f}")
        print(f"Conversiones esperadas: {result['total_expected_conversions']:.0f}")
        print(f"Ingresos esperados: ${result['total_expected_revenue']:,.2f}")
        
        print(f"\n💰 TOP 5 CAMPAÑAS POR PRESUPUESTO")
        for i, campaign in enumerate(result['campaign_results'][:5], 1):
            print(f"{i}. {campaign['campaign_name']}")
            print(f"   Presupuesto: ${campaign['optimized_budget']:,.2f} ({campaign['budget_change_percent']:+.1f}%)")
            print(f"   ROI esperado: {campaign['expected_roi']:.2f}")
            print(f"   Conversiones: {campaign['expected_conversions']:.0f}")
        
        print(f"\n💡 RECOMENDACIONES")
        for recommendation in result['recommendations']:
            print(f"• {recommendation}")
    
    # Comparar métodos de optimización
    print(f"\n🔄 COMPARANDO MÉTODOS DE OPTIMIZACIÓN...")
    comparison = optimizer.compare_optimization_methods(total_budget, campaign_ids)
    
    print(f"\n📈 COMPARACIÓN DE MÉTODOS")
    for method, metrics in comparison['comparison_results'].items():
        print(f"{method}:")
        print(f"  ROI: {metrics['total_expected_roi']:.2f}")
        print(f"  Conversiones: {metrics['total_expected_conversions']:.0f}")
        print(f"  Ingresos: ${metrics['total_expected_revenue']:,.2f}")
    
    print(f"\n🏆 MEJORES MÉTODOS")
    for metric, method in comparison['best_methods'].items():
        print(f"• {metric}: {method}")

if __name__ == "__main__":
    main()

