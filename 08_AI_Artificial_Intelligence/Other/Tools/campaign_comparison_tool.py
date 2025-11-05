#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramienta de Comparación de Campañas de Marketing con IA
=========================================================
Permite comparar múltiples campañas y generar recomendaciones basadas en criterios específicos.
"""

import json
import pandas as pd
from datetime import datetime
import numpy as np
from typing import List, Dict, Any, Tuple

class CampaignComparisonTool:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa la herramienta de comparación"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        self.comparison_criteria = {
            'roi': {'weight': 0.25, 'higher_better': True},
            'success_probability': {'weight': 0.20, 'higher_better': True},
            'budget_efficiency': {'weight': 0.15, 'higher_better': True},
            'implementation_speed': {'weight': 0.15, 'higher_better': True},
            'complexity': {'weight': 0.10, 'higher_better': False},
            'risk_level': {'weight': 0.10, 'higher_better': False},
            'innovation_level': {'weight': 0.05, 'higher_better': True}
        }
    
    def calculate_budget_efficiency(self, campaign):
        """Calcula la eficiencia del presupuesto (ROI / Presupuesto)"""
        roi = campaign['metrics']['return_on_ad_spend']
        budget = campaign['budget']['amount']
        return roi / (budget / 10000)  # Normalizar por cada $10K
    
    def calculate_implementation_speed(self, campaign):
        """Calcula la velocidad de implementación (inverso del tiempo)"""
        weeks = campaign['timeline']['duration_weeks']
        return 1 / (weeks / 24)  # Normalizar por 24 semanas máximo
    
    def calculate_risk_level(self, campaign):
        """Calcula el nivel de riesgo basado en múltiples factores"""
        risk_score = 0
        
        # Factores de riesgo
        if campaign['success_probability'] < 0.8:
            risk_score += 3
        elif campaign['success_probability'] < 0.85:
            risk_score += 2
        elif campaign['success_probability'] < 0.9:
            risk_score += 1
        
        if campaign['complexity'] == 'Alta':
            risk_score += 2
        elif campaign['complexity'] == 'Media':
            risk_score += 1
        
        if campaign['budget']['amount'] > 100000:
            risk_score += 2
        elif campaign['budget']['amount'] > 50000:
            risk_score += 1
        
        if campaign['timeline']['duration_weeks'] > 16:
            risk_score += 1
        
        return min(risk_score, 10)  # Normalizar a 0-10
    
    def calculate_innovation_level(self, campaign):
        """Calcula el nivel de innovación basado en tecnología y categoría"""
        innovation_scores = {
            'Generative AI': 9,
            'Deep Learning': 8,
            'Reinforcement Learning': 8,
            'Computer Vision': 7,
            'Neural Networks': 7,
            'Machine Learning': 6,
            'NLP': 6,
            'Predictive Analytics': 5,
            'Recommendation Engines': 5,
            'Sentiment Analysis': 4
        }
        
        tech_score = innovation_scores.get(campaign['technology'], 5)
        
        # Ajustar por categoría
        category_boost = {
            'Marketing Visual con IA': 2,
            'Generación de Contenido': 1,
            'Optimización de Conversión': 1,
            'Análisis Predictivo': 0,
            'Personalización con IA': 0,
            'Chatbots y Asistentes Virtuales': -1,
            'Automatización de Marketing': -1,
            'Segmentación Avanzada': -1,
            'Análisis de Sentimientos': -1,
            'Recomendaciones Inteligentes': -1
        }
        
        return min(tech_score + category_boost.get(campaign['category'], 0), 10)
    
    def normalize_score(self, value, min_val, max_val, higher_better=True):
        """Normaliza un valor a escala 0-10"""
        if max_val == min_val:
            return 5  # Valor neutral si no hay variación
        
        normalized = (value - min_val) / (max_val - min_val) * 10
        
        if not higher_better:
            normalized = 10 - normalized
        
        return max(0, min(10, normalized))
    
    def calculate_composite_score(self, campaign):
        """Calcula el score compuesto de una campaña"""
        scores = {}
        
        # ROI
        roi = campaign['metrics']['return_on_ad_spend']
        scores['roi'] = self.normalize_score(roi, 2, 15, True)
        
        # Probabilidad de éxito
        success_prob = campaign['success_probability']
        scores['success_probability'] = self.normalize_score(success_prob, 0.65, 0.98, True)
        
        # Eficiencia de presupuesto
        budget_eff = self.calculate_budget_efficiency(campaign)
        scores['budget_efficiency'] = self.normalize_score(budget_eff, 0.5, 5.0, True)
        
        # Velocidad de implementación
        impl_speed = self.calculate_implementation_speed(campaign)
        scores['implementation_speed'] = self.normalize_score(impl_speed, 0.2, 2.0, True)
        
        # Complejidad (inversa)
        complexity_map = {'Baja': 1, 'Media': 2, 'Alta': 3}
        complexity = complexity_map[campaign['complexity']]
        scores['complexity'] = self.normalize_score(complexity, 1, 3, False)
        
        # Nivel de riesgo (inverso)
        risk = self.calculate_risk_level(campaign)
        scores['risk_level'] = self.normalize_score(risk, 0, 10, False)
        
        # Nivel de innovación
        innovation = self.calculate_innovation_level(campaign)
        scores['innovation_level'] = self.normalize_score(innovation, 0, 10, True)
        
        # Calcular score compuesto ponderado
        composite_score = sum(
            scores[criterion] * self.comparison_criteria[criterion]['weight']
            for criterion in scores
        )
        
        return {
            'composite_score': round(composite_score, 2),
            'individual_scores': scores,
            'campaign_id': campaign['id'],
            'campaign_name': campaign['name']
        }
    
    def compare_campaigns(self, campaign_ids: List[int]) -> Dict[str, Any]:
        """Compara un conjunto de campañas"""
        if not campaign_ids:
            return {"error": "No se proporcionaron IDs de campañas"}
        
        # Filtrar campañas válidas
        valid_campaigns = []
        for campaign_id in campaign_ids:
            campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
            if campaign:
                valid_campaigns.append(campaign)
        
        if not valid_campaigns:
            return {"error": "No se encontraron campañas válidas"}
        
        # Calcular scores para cada campaña
        comparison_results = []
        for campaign in valid_campaigns:
            score_data = self.calculate_composite_score(campaign)
            comparison_results.append({
                **score_data,
                'category': campaign['category'],
                'technology': campaign['technology'],
                'budget': campaign['budget']['amount'],
                'success_probability': campaign['success_probability'],
                'roi': campaign['metrics']['return_on_ad_spend'],
                'complexity': campaign['complexity'],
                'priority': campaign['priority']
            })
        
        # Ordenar por score compuesto
        comparison_results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Generar análisis comparativo
        analysis = {
            'total_campaigns': len(comparison_results),
            'best_campaign': comparison_results[0],
            'worst_campaign': comparison_results[-1],
            'average_score': np.mean([r['composite_score'] for r in comparison_results]),
            'score_std': np.std([r['composite_score'] for r in comparison_results]),
            'rankings': comparison_results,
            'recommendations': self.generate_recommendations(comparison_results)
        }
        
        return analysis
    
    def generate_recommendations(self, comparison_results: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en la comparación"""
        recommendations = []
        
        if not comparison_results:
            return recommendations
        
        best = comparison_results[0]
        worst = comparison_results[-1]
        
        # Recomendación principal
        recommendations.append(f"🏆 **Campaña recomendada**: {best['campaign_name']} (Score: {best['composite_score']}/10)")
        
        # Análisis de fortalezas
        best_scores = best['individual_scores']
        top_criteria = sorted(best_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        strengths = []
        for criterion, score in top_criteria:
            if score >= 8:
                strengths.append(f"{criterion.replace('_', ' ').title()}")
        
        if strengths:
            recommendations.append(f"✅ **Fortalezas**: Excelente en {', '.join(strengths)}")
        
        # Análisis de debilidades
        worst_scores = worst['individual_scores']
        bottom_criteria = sorted(worst_scores.items(), key=lambda x: x[1])[:3]
        
        weaknesses = []
        for criterion, score in bottom_criteria:
            if score <= 4:
                weaknesses.append(f"{criterion.replace('_', ' ').title()}")
        
        if weaknesses:
            recommendations.append(f"⚠️ **Áreas de mejora**: Considerar {', '.join(weaknesses)}")
        
        # Análisis de presupuesto
        budgets = [r['budget'] for r in comparison_results]
        avg_budget = np.mean(budgets)
        
        if best['budget'] < avg_budget * 0.8:
            recommendations.append(f"💰 **Eficiencia de presupuesto**: {best['campaign_name']} ofrece excelente ROI con presupuesto reducido")
        
        # Análisis de riesgo
        if best['individual_scores']['risk_level'] >= 7:
            recommendations.append("🛡️ **Bajo riesgo**: La campaña recomendada presenta un perfil de riesgo favorable")
        
        # Análisis de implementación
        if best['individual_scores']['implementation_speed'] >= 7:
            recommendations.append("⚡ **Implementación rápida**: La campaña se puede implementar en tiempo reducido")
        
        return recommendations
    
    def find_similar_campaigns(self, campaign_id: int, limit: int = 5) -> List[Dict]:
        """Encuentra campañas similares a una dada"""
        target_campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
        if not target_campaign:
            return []
        
        # Calcular similitud basada en múltiples factores
        similarities = []
        for campaign in self.campaigns:
            if campaign['id'] == campaign_id:
                continue
            
            similarity_score = 0
            
            # Misma categoría
            if campaign['category'] == target_campaign['category']:
                similarity_score += 3
            
            # Misma tecnología
            if campaign['technology'] == target_campaign['technology']:
                similarity_score += 2
            
            # Mismo vertical
            if campaign['vertical'] == target_campaign['vertical']:
                similarity_score += 2
            
            # Misma complejidad
            if campaign['complexity'] == target_campaign['complexity']:
                similarity_score += 1
            
            # Presupuesto similar (±25%)
            target_budget = target_campaign['budget']['amount']
            campaign_budget = campaign['budget']['amount']
            if abs(campaign_budget - target_budget) / target_budget <= 0.25:
                similarity_score += 1
            
            similarities.append({
                'campaign': campaign,
                'similarity_score': similarity_score
            })
        
        # Ordenar por similitud y retornar top N
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:limit]
    
    def generate_comparison_report(self, campaign_ids: List[int], output_file: str = None):
        """Genera un reporte detallado de comparación"""
        analysis = self.compare_campaigns(campaign_ids)
        
        if 'error' in analysis:
            return analysis
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'campaigns_compared': len(campaign_ids),
            'analysis': analysis,
            'detailed_breakdown': self.generate_detailed_breakdown(analysis['rankings'])
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report
    
    def generate_detailed_breakdown(self, rankings: List[Dict]) -> Dict[str, Any]:
        """Genera un desglose detallado de las comparaciones"""
        breakdown = {
            'by_category': {},
            'by_technology': {},
            'by_complexity': {},
            'by_budget_range': {},
            'score_distribution': {
                'excellent': 0,  # 8-10
                'good': 0,       # 6-8
                'average': 0,    # 4-6
                'poor': 0        # 0-4
            }
        }
        
        for campaign in rankings:
            score = campaign['composite_score']
            
            # Distribución de scores
            if score >= 8:
                breakdown['score_distribution']['excellent'] += 1
            elif score >= 6:
                breakdown['score_distribution']['good'] += 1
            elif score >= 4:
                breakdown['score_distribution']['average'] += 1
            else:
                breakdown['score_distribution']['poor'] += 1
            
            # Por categoría
            category = campaign['category']
            if category not in breakdown['by_category']:
                breakdown['by_category'][category] = {'count': 0, 'avg_score': 0, 'scores': []}
            breakdown['by_category'][category]['count'] += 1
            breakdown['by_category'][category]['scores'].append(score)
            
            # Por tecnología
            technology = campaign['technology']
            if technology not in breakdown['by_technology']:
                breakdown['by_technology'][technology] = {'count': 0, 'avg_score': 0, 'scores': []}
            breakdown['by_technology'][technology]['count'] += 1
            breakdown['by_technology'][technology]['scores'].append(score)
            
            # Por complejidad
            complexity = campaign['complexity']
            if complexity not in breakdown['by_complexity']:
                breakdown['by_complexity'][complexity] = {'count': 0, 'avg_score': 0, 'scores': []}
            breakdown['by_complexity'][complexity]['count'] += 1
            breakdown['by_complexity'][complexity]['scores'].append(score)
            
            # Por rango de presupuesto
            budget = campaign['budget']
            if budget < 25000:
                budget_range = 'Básico'
            elif budget < 75000:
                budget_range = 'Intermedio'
            elif budget < 150000:
                budget_range = 'Avanzado'
            else:
                budget_range = 'Enterprise'
            
            if budget_range not in breakdown['by_budget_range']:
                breakdown['by_budget_range'][budget_range] = {'count': 0, 'avg_score': 0, 'scores': []}
            breakdown['by_budget_range'][budget_range]['count'] += 1
            breakdown['by_budget_range'][budget_range]['scores'].append(score)
        
        # Calcular promedios
        for category_data in breakdown['by_category'].values():
            category_data['avg_score'] = round(np.mean(category_data['scores']), 2)
        
        for tech_data in breakdown['by_technology'].values():
            tech_data['avg_score'] = round(np.mean(tech_data['scores']), 2)
        
        for comp_data in breakdown['by_complexity'].values():
            comp_data['avg_score'] = round(np.mean(comp_data['scores']), 2)
        
        for budget_data in breakdown['by_budget_range'].values():
            budget_data['avg_score'] = round(np.mean(budget_data['scores']), 2)
        
        return breakdown

def main():
    """Función principal de demostración"""
    print("=== HERRAMIENTA DE COMPARACIÓN DE CAMPAÑAS ===")
    
    # Inicializar herramienta
    comparator = CampaignComparisonTool()
    
    # Ejemplo de comparación
    sample_campaign_ids = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30]
    
    print(f"Comparando {len(sample_campaign_ids)} campañas...")
    
    # Realizar comparación
    analysis = comparator.compare_campaigns(sample_campaign_ids)
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DE COMPARACIÓN")
    print(f"Total de campañas: {analysis['total_campaigns']}")
    print(f"Score promedio: {analysis['average_score']:.2f}/10")
    print(f"Desviación estándar: {analysis['score_std']:.2f}")
    
    print(f"\n🏆 MEJOR CAMPAÑA")
    best = analysis['best_campaign']
    print(f"Nombre: {best['campaign_name']}")
    print(f"Score: {best['composite_score']}/10")
    print(f"Categoría: {best['category']}")
    print(f"Tecnología: {best['technology']}")
    print(f"Presupuesto: ${best['budget']:,}")
    print(f"ROI: {best['roi']:.1f}x")
    
    print(f"\n📈 TOP 5 CAMPAÑAS")
    for i, campaign in enumerate(analysis['rankings'][:5], 1):
        print(f"{i}. {campaign['campaign_name']} - Score: {campaign['composite_score']}/10 - ROI: {campaign['roi']:.1f}x")
    
    print(f"\n💡 RECOMENDACIONES")
    for recommendation in analysis['recommendations']:
        print(f"• {recommendation}")
    
    # Generar reporte
    report = comparator.generate_comparison_report(sample_campaign_ids, 'campaign_comparison_report.json')
    print(f"\n📄 Reporte detallado guardado en: campaign_comparison_report.json")
    
    # Buscar campañas similares
    print(f"\n🔍 CAMPAÑAS SIMILARES A LA #1")
    similar = comparator.find_similar_campaigns(1, 3)
    for sim in similar:
        print(f"• {sim['campaign']['name']} - Similitud: {sim['similarity_score']}/10")

if __name__ == "__main__":
    main()


