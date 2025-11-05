#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador Avanzado de Campañas de Marketing con IA
==================================================
Herramientas de análisis, filtrado y recomendaciones para las 1000 campañas.
"""

import json
import pandas as pd
from datetime import datetime
import statistics

class AICampaignsAnalyzer:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el analizador con las campañas"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
    
    def get_campaigns_by_budget_range(self, min_budget, max_budget):
        """Filtra campañas por rango de presupuesto"""
        return self.df[
            (self.df['budget'].apply(lambda x: x['amount']) >= min_budget) &
            (self.df['budget'].apply(lambda x: x['amount']) <= max_budget)
        ]
    
    def get_campaigns_by_success_probability(self, min_probability):
        """Filtra campañas por probabilidad de éxito mínima"""
        return self.df[self.df['success_probability'] >= min_probability]
    
    def get_campaigns_by_complexity(self, complexity):
        """Filtra campañas por complejidad"""
        return self.df[self.df['complexity'] == complexity]
    
    def get_campaigns_by_priority(self, priority):
        """Filtra campañas por prioridad"""
        return self.df[self.df['priority'] == priority]
    
    def get_campaigns_by_category(self, category):
        """Filtra campañas por categoría"""
        return self.df[self.df['category'] == category]
    
    def get_campaigns_by_vertical(self, vertical):
        """Filtra campañas por sector vertical"""
        return self.df[self.df['vertical'] == vertical]
    
    def get_campaigns_by_technology(self, technology):
        """Filtra campañas por tecnología"""
        return self.df[self.df['technology'] == technology]
    
    def get_campaigns_by_channel(self, channel):
        """Filtra campañas por canal"""
        return self.df[self.df['channel'] == channel]
    
    def get_high_roi_campaigns(self, min_roi=5.0):
        """Obtiene campañas con ROI alto"""
        return self.df[self.df['metrics'].apply(lambda x: x['return_on_ad_spend']) >= min_roi]
    
    def get_low_risk_campaigns(self, min_success_prob=0.85):
        """Obtiene campañas de bajo riesgo"""
        return self.df[self.df['success_probability'] >= min_success_prob]
    
    def get_quick_win_campaigns(self, max_weeks=8):
        """Obtiene campañas de implementación rápida"""
        return self.df[self.df['timeline'].apply(lambda x: x['duration_weeks']) <= max_weeks]
    
    def get_enterprise_campaigns(self):
        """Obtiene campañas enterprise"""
        return self.df[self.df['budget'].apply(lambda x: x['tier']) == 'Enterprise']
    
    def get_startup_campaigns(self):
        """Obtiene campañas adecuadas para startups"""
        return self.df[
            (self.df['budget'].apply(lambda x: x['amount']) <= 25000) &
            (self.df['complexity'].isin(['Baja', 'Media'])) &
            (self.df['success_probability'] >= 0.80)
        ]
    
    def get_advanced_campaigns(self):
        """Obtiene campañas avanzadas para empresas grandes"""
        return self.df[
            (self.df['budget'].apply(lambda x: x['amount']) >= 50000) &
            (self.df['complexity'] == 'Alta') &
            (self.df['priority'].isin(['Alta', 'Crítica']))
        ]
    
    def analyze_category_performance(self):
        """Analiza el rendimiento por categoría"""
        analysis = {}
        
        for category in self.df['category'].unique():
            cat_campaigns = self.df[self.df['category'] == category]
            
            analysis[category] = {
                'total_campaigns': len(cat_campaigns),
                'avg_budget': cat_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                'avg_success_probability': cat_campaigns['success_probability'].mean(),
                'avg_roi': cat_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                'avg_conversion_rate': cat_campaigns['metrics'].apply(lambda x: x['conversion_rate']).mean(),
                'avg_cpa': cat_campaigns['metrics'].apply(lambda x: x['cost_per_acquisition']).mean(),
                'complexity_distribution': cat_campaigns['complexity'].value_counts().to_dict(),
                'priority_distribution': cat_campaigns['priority'].value_counts().to_dict()
            }
        
        return analysis
    
    def analyze_vertical_performance(self):
        """Analiza el rendimiento por sector vertical"""
        analysis = {}
        
        for vertical in self.df['vertical'].unique():
            vert_campaigns = self.df[self.df['vertical'] == vertical]
            
            analysis[vertical] = {
                'total_campaigns': len(vert_campaigns),
                'avg_budget': vert_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                'avg_success_probability': vert_campaigns['success_probability'].mean(),
                'avg_roi': vert_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                'total_budget': vert_campaigns['budget'].apply(lambda x: x['amount']).sum(),
                'top_categories': vert_campaigns['category'].value_counts().head(3).to_dict()
            }
        
        return analysis
    
    def analyze_technology_trends(self):
        """Analiza tendencias por tecnología"""
        analysis = {}
        
        for tech in self.df['technology'].unique():
            tech_campaigns = self.df[self.df['technology'] == tech]
            
            analysis[tech] = {
                'total_campaigns': len(tech_campaigns),
                'avg_budget': tech_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                'avg_success_probability': tech_campaigns['success_probability'].mean(),
                'avg_roi': tech_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                'most_common_categories': tech_campaigns['category'].value_counts().head(3).to_dict(),
                'most_common_verticals': tech_campaigns['vertical'].value_counts().head(3).to_dict()
            }
        
        return analysis
    
    def get_recommendations(self, budget_range=None, complexity=None, vertical=None, objectives=None):
        """Genera recomendaciones personalizadas"""
        filtered_campaigns = self.df.copy()
        
        # Aplicar filtros
        if budget_range:
            min_budget, max_budget = budget_range
            filtered_campaigns = filtered_campaigns[
                (filtered_campaigns['budget'].apply(lambda x: x['amount']) >= min_budget) &
                (filtered_campaigns['budget'].apply(lambda x: x['amount']) <= max_budget)
            ]
        
        if complexity:
            filtered_campaigns = filtered_campaigns[filtered_campaigns['complexity'] == complexity]
        
        if vertical:
            filtered_campaigns = filtered_campaigns[filtered_campaigns['vertical'] == vertical]
        
        if objectives:
            filtered_campaigns = filtered_campaigns[filtered_campaigns['objective'].isin(objectives)]
        
        # Ordenar por score compuesto
        filtered_campaigns['score'] = (
            filtered_campaigns['success_probability'] * 0.4 +
            (filtered_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) / 10) * 0.3 +
            (1 - filtered_campaigns['timeline'].apply(lambda x: x['duration_weeks']) / 24) * 0.3
        )
        
        return filtered_campaigns.sort_values('score', ascending=False)
    
    def generate_implementation_roadmap(self, total_budget, timeline_months=12):
        """Genera un roadmap de implementación"""
        # Filtrar campañas por presupuesto
        affordable_campaigns = self.df[
            self.df['budget'].apply(lambda x: x['amount']) <= total_budget
        ].copy()
        
        # Ordenar por prioridad y ROI
        affordable_campaigns['priority_score'] = affordable_campaigns['priority'].map({
            'Crítica': 4, 'Alta': 3, 'Media': 2, 'Baja': 1
        })
        
        affordable_campaigns['roi_score'] = affordable_campaigns['metrics'].apply(
            lambda x: x['return_on_ad_spend']
        )
        
        affordable_campaigns['total_score'] = (
            affordable_campaigns['priority_score'] * 0.6 +
            affordable_campaigns['roi_score'] * 0.4
        )
        
        # Seleccionar campañas para el roadmap
        selected_campaigns = affordable_campaigns.sort_values('total_score', ascending=False)
        
        roadmap = {
            'total_budget_allocated': 0,
            'total_campaigns': 0,
            'phases': []
        }
        
        current_budget = 0
        phase = 1
        phase_campaigns = []
        phase_budget = 0
        
        for _, campaign in selected_campaigns.iterrows():
            campaign_budget = campaign['budget']['amount']
            
            if current_budget + campaign_budget <= total_budget:
                phase_campaigns.append(campaign.to_dict())
                phase_budget += campaign_budget
                current_budget += campaign_budget
                
                # Crear nueva fase cada 3 meses o cuando se alcance un límite
                if len(phase_campaigns) >= 10 or phase_budget >= total_budget * 0.25:
                    roadmap['phases'].append({
                        'phase': f'Fase {phase}',
                        'duration_months': 3,
                        'budget': phase_budget,
                        'campaigns': phase_campaigns
                    })
                    phase += 1
                    phase_campaigns = []
                    phase_budget = 0
        
        # Agregar fase final si quedan campañas
        if phase_campaigns:
            roadmap['phases'].append({
                'phase': f'Fase {phase}',
                'duration_months': 3,
                'budget': phase_budget,
                'campaigns': phase_campaigns
            })
        
        roadmap['total_budget_allocated'] = current_budget
        roadmap['total_campaigns'] = len(selected_campaigns)
        
        return roadmap
    
    def generate_risk_analysis(self):
        """Genera análisis de riesgos por campaña"""
        risk_analysis = []
        
        for _, campaign in self.df.iterrows():
            risk_score = 0
            risk_factors = []
            
            # Factores de riesgo
            if campaign['success_probability'] < 0.8:
                risk_score += 2
                risk_factors.append("Baja probabilidad de éxito")
            
            if campaign['complexity'] == 'Alta':
                risk_score += 1
                risk_factors.append("Alta complejidad técnica")
            
            if campaign['budget']['amount'] > 100000:
                risk_score += 1
                risk_factors.append("Alto presupuesto")
            
            if campaign['timeline']['duration_weeks'] > 16:
                risk_score += 1
                risk_factors.append("Larga duración")
            
            if campaign['priority'] == 'Crítica':
                risk_score += 1
                risk_factors.append("Prioridad crítica")
            
            risk_level = "Bajo" if risk_score <= 2 else "Medio" if risk_score <= 4 else "Alto"
            
            risk_analysis.append({
                'campaign_id': campaign['id'],
                'campaign_name': campaign['name'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'mitigation_strategies': self.get_mitigation_strategies(risk_factors)
            })
        
        return risk_analysis
    
    def get_mitigation_strategies(self, risk_factors):
        """Genera estrategias de mitigación de riesgos"""
        strategies = {
            "Baja probabilidad de éxito": [
                "Implementar pruebas piloto antes del lanzamiento completo",
                "Aumentar el tiempo de testing y validación",
                "Asignar equipo más experimentado"
            ],
            "Alta complejidad técnica": [
                "Contratar consultores especializados",
                "Dividir el proyecto en fases más pequeñas",
                "Invertir en capacitación del equipo"
            ],
            "Alto presupuesto": [
                "Implementar controles de gasto estrictos",
                "Dividir el presupuesto en milestones",
                "Negociar contratos con cláusulas de reducción de costos"
            ],
            "Larga duración": [
                "Implementar metodologías ágiles",
                "Establecer hitos intermedios más frecuentes",
                "Asignar más recursos para acelerar el desarrollo"
            ],
            "Prioridad crítica": [
                "Asignar los mejores recursos del equipo",
                "Implementar monitoreo continuo",
                "Preparar planes de contingencia"
            ]
        }
        
        mitigation = []
        for factor in risk_factors:
            mitigation.extend(strategies.get(factor, []))
        
        return list(set(mitigation))  # Eliminar duplicados
    
    def export_analysis_report(self, filename='ai_campaigns_analysis_report.json'):
        """Exporta un reporte completo de análisis"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_campaigns': len(self.df),
                'total_budget': self.df['budget'].apply(lambda x: x['amount']).sum(),
                'avg_success_probability': self.df['success_probability'].mean(),
                'avg_roi': self.df['metrics'].apply(lambda x: x['return_on_ad_spend']).mean()
            },
            'category_analysis': self.analyze_category_performance(),
            'vertical_analysis': self.analyze_vertical_performance(),
            'technology_analysis': self.analyze_technology_trends(),
            'risk_analysis': self.generate_risk_analysis(),
            'top_performers': {
                'by_roi': self.df.nlargest(10, 'metrics').apply(lambda x: x['return_on_ad_spend']).to_dict(),
                'by_success_probability': self.df.nlargest(10, 'success_probability').to_dict(),
                'by_budget_efficiency': self.df.nlargest(10, 'budget').apply(lambda x: x['amount']).to_dict()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Reporte de análisis exportado a: {filename}")
        return report

def main():
    """Función principal de demostración"""
    print("=== ANALIZADOR DE CAMPAÑAS DE MARKETING CON IA ===")
    
    # Inicializar analizador
    analyzer = AICampaignsAnalyzer()
    
    # Análisis básico
    print(f"\nTotal de campañas: {len(analyzer.df)}")
    print(f"Presupuesto total: ${analyzer.df['budget'].apply(lambda x: x['amount']).sum():,}")
    
    # Campañas para startups
    startup_campaigns = analyzer.get_startup_campaigns()
    print(f"\nCampañas recomendadas para startups: {len(startup_campaigns)}")
    
    # Campañas de alto ROI
    high_roi_campaigns = analyzer.get_high_roi_campaigns(7.0)
    print(f"Campañas con ROI > 7x: {len(high_roi_campaigns)}")
    
    # Análisis por categoría
    category_analysis = analyzer.analyze_category_performance()
    print(f"\nAnálisis por categoría:")
    for category, data in category_analysis.items():
        print(f"  {category}: {data['total_campaigns']} campañas, ROI avg: {data['avg_roi']:.1f}x")
    
    # Generar recomendaciones
    recommendations = analyzer.get_recommendations(
        budget_range=(10000, 50000),
        complexity='Media',
        objectives=['Aumentar conversiones', 'Mejorar engagement']
    )
    print(f"\nTop 5 recomendaciones:")
    for i, (_, campaign) in enumerate(recommendations.head().iterrows(), 1):
        print(f"  {i}. {campaign['name']} - ROI: {campaign['metrics']['return_on_ad_spend']:.1f}x")
    
    # Exportar reporte
    analyzer.export_analysis_report()
    
    print("\n¡Análisis completado!")

if __name__ == "__main__":
    main()


