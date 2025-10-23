#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Reportes Automáticos por Industria
==============================================
Genera reportes especializados para cada sector vertical con insights específicos.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

class IndustryReportGenerator:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el generador de reportes por industria"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Configuración específica por industria
        self.industry_configs = {
            'E-commerce': {
                'key_metrics': ['conversion_rate', 'customer_lifetime_value', 'cost_per_acquisition'],
                'priority_categories': ['Personalización con IA', 'Optimización de Conversión', 'Recomendaciones Inteligentes'],
                'budget_ranges': {'low': 10000, 'medium': 50000, 'high': 150000},
                'success_thresholds': {'roi': 5.0, 'conversion': 8.0, 'success_prob': 0.85}
            },
            'Fintech': {
                'key_metrics': ['return_on_ad_spend', 'customer_lifetime_value', 'retention_rate'],
                'priority_categories': ['Análisis Predictivo', 'Automatización de Marketing', 'Análisis de Sentimientos'],
                'budget_ranges': {'low': 25000, 'medium': 100000, 'high': 500000},
                'success_thresholds': {'roi': 7.0, 'conversion': 12.0, 'success_prob': 0.90}
            },
            'Healthcare': {
                'key_metrics': ['engagement_rate', 'customer_satisfaction_score', 'retention_rate'],
                'priority_categories': ['Chatbots y Asistentes Virtuales', 'Personalización con IA', 'Análisis de Sentimientos'],
                'budget_ranges': {'low': 20000, 'medium': 75000, 'high': 200000},
                'success_thresholds': {'roi': 6.0, 'conversion': 10.0, 'success_prob': 0.88}
            },
            'Education': {
                'key_metrics': ['engagement_rate', 'retention_rate', 'website_traffic_increase'],
                'priority_categories': ['Generación de Contenido', 'Personalización con IA', 'Chatbots y Asistentes Virtuales'],
                'budget_ranges': {'low': 5000, 'medium': 25000, 'high': 100000},
                'success_thresholds': {'roi': 4.0, 'conversion': 6.0, 'success_prob': 0.80}
            },
            'Real Estate': {
                'key_metrics': ['lead_generation_increase', 'conversion_rate', 'customer_lifetime_value'],
                'priority_categories': ['Segmentación Avanzada', 'Análisis Predictivo', 'Marketing Visual con IA'],
                'budget_ranges': {'low': 15000, 'medium': 60000, 'high': 180000},
                'success_thresholds': {'roi': 5.5, 'conversion': 9.0, 'success_prob': 0.85}
            },
            'Technology': {
                'key_metrics': ['return_on_ad_spend', 'brand_awareness_lift', 'lead_generation_increase'],
                'priority_categories': ['Optimización de Conversión', 'Análisis Predictivo', 'Automatización de Marketing'],
                'budget_ranges': {'low': 30000, 'medium': 100000, 'high': 300000},
                'success_thresholds': {'roi': 8.0, 'conversion': 15.0, 'success_prob': 0.92}
            }
        }
    
    def generate_industry_report(self, industry: str) -> Dict[str, Any]:
        """Genera un reporte completo para una industria específica"""
        if industry not in self.industry_configs:
            return {"error": f"Industria '{industry}' no soportada"}
        
        # Filtrar campañas por industria
        industry_campaigns = self.df[self.df['vertical'] == industry].copy()
        
        if industry_campaigns.empty:
            return {"error": f"No se encontraron campañas para la industria '{industry}'"}
        
        config = self.industry_configs[industry]
        
        # Análisis general
        general_analysis = self._analyze_general_metrics(industry_campaigns, config)
        
        # Análisis por categorías
        category_analysis = self._analyze_by_categories(industry_campaigns, config)
        
        # Análisis por presupuesto
        budget_analysis = self._analyze_by_budget(industry_campaigns, config)
        
        # Análisis por complejidad
        complexity_analysis = self._analyze_by_complexity(industry_campaigns)
        
        # Análisis de tecnologías
        technology_analysis = self._analyze_by_technology(industry_campaigns)
        
        # Campañas recomendadas
        recommended_campaigns = self._get_recommended_campaigns(industry_campaigns, config)
        
        # Tendencias y insights
        trends_insights = self._generate_trends_insights(industry_campaigns, config)
        
        # Roadmap de implementación
        implementation_roadmap = self._generate_implementation_roadmap(industry_campaigns, config)
        
        return {
            'industry': industry,
            'generated_at': datetime.now().isoformat(),
            'summary': general_analysis,
            'category_analysis': category_analysis,
            'budget_analysis': budget_analysis,
            'complexity_analysis': complexity_analysis,
            'technology_analysis': technology_analysis,
            'recommended_campaigns': recommended_campaigns,
            'trends_insights': trends_insights,
            'implementation_roadmap': implementation_roadmap
        }
    
    def _analyze_general_metrics(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Analiza métricas generales para la industria"""
        total_campaigns = len(campaigns)
        total_budget = campaigns['budget'].apply(lambda x: x['amount']).sum()
        avg_budget = campaigns['budget'].apply(lambda x: x['amount']).mean()
        
        # Calcular métricas clave
        key_metrics = {}
        for metric in config['key_metrics']:
            if metric in ['conversion_rate', 'customer_lifetime_value', 'cost_per_acquisition', 
                         'return_on_ad_spend', 'engagement_rate', 'retention_rate', 
                         'customer_satisfaction_score', 'website_traffic_increase', 
                         'lead_generation_increase', 'brand_awareness_lift']:
                values = campaigns['metrics'].apply(lambda x: x.get(metric, 0))
                key_metrics[metric] = {
                    'average': values.mean(),
                    'median': values.median(),
                    'min': values.min(),
                    'max': values.max(),
                    'std': values.std()
                }
        
        # Análisis de ROI
        roi_values = campaigns['metrics'].apply(lambda x: x['return_on_ad_spend'])
        success_prob_values = campaigns['success_probability']
        
        # Campañas que superan umbrales
        high_performers = campaigns[
            (roi_values >= config['success_thresholds']['roi']) &
            (success_prob_values >= config['success_thresholds']['success_prob'])
        ]
        
        return {
            'total_campaigns': total_campaigns,
            'total_budget': total_budget,
            'average_budget': avg_budget,
            'key_metrics': key_metrics,
            'roi_analysis': {
                'average': roi_values.mean(),
                'median': roi_values.median(),
                'high_performers_count': len(high_performers),
                'high_performers_percentage': (len(high_performers) / total_campaigns) * 100
            },
            'success_probability_analysis': {
                'average': success_prob_values.mean(),
                'median': success_prob_values.median(),
                'above_threshold': (success_prob_values >= config['success_thresholds']['success_prob']).sum()
            }
        }
    
    def _analyze_by_categories(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Analiza campañas por categorías prioritarias"""
        category_analysis = {}
        priority_categories = config['priority_categories']
        
        for category in priority_categories:
            cat_campaigns = campaigns[campaigns['category'] == category]
            
            if not cat_campaigns.empty:
                category_analysis[category] = {
                    'count': len(cat_campaigns),
                    'percentage': (len(cat_campaigns) / len(campaigns)) * 100,
                    'average_budget': cat_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                    'average_roi': cat_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                    'average_success_prob': cat_campaigns['success_probability'].mean(),
                    'complexity_distribution': cat_campaigns['complexity'].value_counts().to_dict(),
                    'priority_distribution': cat_campaigns['priority'].value_counts().to_dict()
                }
        
        return category_analysis
    
    def _analyze_by_budget(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Analiza campañas por rangos de presupuesto"""
        budget_ranges = config['budget_ranges']
        budget_analysis = {}
        
        for range_name, threshold in budget_ranges.items():
            if range_name == 'low':
                range_campaigns = campaigns[campaigns['budget'].apply(lambda x: x['amount']) <= threshold]
            elif range_name == 'medium':
                range_campaigns = campaigns[
                    (campaigns['budget'].apply(lambda x: x['amount']) > budget_ranges['low']) &
                    (campaigns['budget'].apply(lambda x: x['amount']) <= threshold)
                ]
            else:  # high
                range_campaigns = campaigns[campaigns['budget'].apply(lambda x: x['amount']) > threshold]
            
            if not range_campaigns.empty:
                budget_analysis[range_name] = {
                    'count': len(range_campaigns),
                    'percentage': (len(range_campaigns) / len(campaigns)) * 100,
                    'average_budget': range_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                    'average_roi': range_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                    'average_success_prob': range_campaigns['success_probability'].mean(),
                    'top_categories': range_campaigns['category'].value_counts().head(3).to_dict()
                }
        
        return budget_analysis
    
    def _analyze_by_complexity(self, campaigns: pd.DataFrame) -> Dict[str, Any]:
        """Analiza campañas por nivel de complejidad"""
        complexity_analysis = {}
        
        for complexity in ['Baja', 'Media', 'Alta']:
            comp_campaigns = campaigns[campaigns['complexity'] == complexity]
            
            if not comp_campaigns.empty:
                complexity_analysis[complexity] = {
                    'count': len(comp_campaigns),
                    'percentage': (len(comp_campaigns) / len(campaigns)) * 100,
                    'average_budget': comp_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                    'average_roi': comp_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                    'average_success_prob': comp_campaigns['success_probability'].mean(),
                    'average_timeline_weeks': comp_campaigns['timeline'].apply(lambda x: x['duration_weeks']).mean(),
                    'top_categories': comp_campaigns['category'].value_counts().head(3).to_dict()
                }
        
        return complexity_analysis
    
    def _analyze_by_technology(self, campaigns: pd.DataFrame) -> Dict[str, Any]:
        """Analiza campañas por tecnología utilizada"""
        technology_analysis = {}
        
        for tech in campaigns['technology'].unique():
            tech_campaigns = campaigns[campaigns['technology'] == tech]
            
            technology_analysis[tech] = {
                'count': len(tech_campaigns),
                'percentage': (len(tech_campaigns) / len(campaigns)) * 100,
                'average_budget': tech_campaigns['budget'].apply(lambda x: x['amount']).mean(),
                'average_roi': tech_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
                'average_success_prob': tech_campaigns['success_probability'].mean(),
                'top_categories': tech_campaigns['category'].value_counts().head(3).to_dict(),
                'complexity_distribution': tech_campaigns['complexity'].value_counts().to_dict()
            }
        
        return technology_analysis
    
    def _get_recommended_campaigns(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, List[Dict]]:
        """Obtiene campañas recomendadas para la industria"""
        recommendations = {
            'high_roi': [],
            'low_risk': [],
            'quick_wins': [],
            'budget_efficient': []
        }
        
        # Campañas de alto ROI
        high_roi_threshold = config['success_thresholds']['roi']
        high_roi_campaigns = campaigns[
            campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) >= high_roi_threshold
        ].nlargest(5, 'metrics')
        
        recommendations['high_roi'] = high_roi_campaigns[['id', 'name', 'category', 'budget', 'success_probability', 'metrics']].to_dict('records')
        
        # Campañas de bajo riesgo
        low_risk_campaigns = campaigns[
            (campaigns['success_probability'] >= 0.9) &
            (campaigns['complexity'].isin(['Baja', 'Media']))
        ].nlargest(5, 'success_probability')
        
        recommendations['low_risk'] = low_risk_campaigns[['id', 'name', 'category', 'budget', 'success_probability', 'complexity']].to_dict('records')
        
        # Campañas de implementación rápida
        quick_wins = campaigns[
            campaigns['timeline'].apply(lambda x: x['duration_weeks']) <= 8
        ].nlargest(5, 'metrics')
        
        recommendations['quick_wins'] = quick_wins[['id', 'name', 'category', 'budget', 'timeline', 'metrics']].to_dict('records')
        
        # Campañas eficientes en presupuesto
        campaigns['budget_efficiency'] = campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) / (campaigns['budget'].apply(lambda x: x['amount']) / 10000)
        budget_efficient = campaigns.nlargest(5, 'budget_efficiency')
        
        recommendations['budget_efficient'] = budget_efficient[['id', 'name', 'category', 'budget', 'budget_efficiency', 'metrics']].to_dict('records')
        
        return recommendations
    
    def _generate_trends_insights(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Genera insights sobre tendencias en la industria"""
        insights = {
            'top_performing_categories': campaigns.groupby('category')['metrics'].apply(
                lambda x: x.apply(lambda y: y['return_on_ad_spend']).mean()
            ).sort_values(ascending=False).head(5).to_dict(),
            'most_used_technologies': campaigns['technology'].value_counts().head(5).to_dict(),
            'budget_distribution': {
                'under_25k': (campaigns['budget'].apply(lambda x: x['amount']) < 25000).sum(),
                '25k_to_100k': ((campaigns['budget'].apply(lambda x: x['amount']) >= 25000) & 
                               (campaigns['budget'].apply(lambda x: x['amount']) < 100000)).sum(),
                'over_100k': (campaigns['budget'].apply(lambda x: x['amount']) >= 100000).sum()
            },
            'complexity_trends': campaigns['complexity'].value_counts().to_dict(),
            'priority_distribution': campaigns['priority'].value_counts().to_dict(),
            'success_rate_by_complexity': campaigns.groupby('complexity')['success_probability'].mean().to_dict()
        }
        
        return insights
    
    def _generate_implementation_roadmap(self, campaigns: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Genera un roadmap de implementación para la industria"""
        # Fase 1: Campañas de bajo riesgo y alto ROI
        phase1_campaigns = campaigns[
            (campaigns['success_probability'] >= 0.85) &
            (campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) >= config['success_thresholds']['roi']) &
            (campaigns['complexity'].isin(['Baja', 'Media']))
        ].nlargest(10, 'metrics')
        
        # Fase 2: Campañas de categorías prioritarias
        priority_categories = config['priority_categories']
        phase2_campaigns = campaigns[
            campaigns['category'].isin(priority_categories)
        ].nlargest(15, 'success_probability')
        
        # Fase 3: Campañas de alta complejidad pero alto potencial
        phase3_campaigns = campaigns[
            (campaigns['complexity'] == 'Alta') &
            (campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) >= config['success_thresholds']['roi'] * 1.2)
        ].nlargest(10, 'metrics')
        
        roadmap = {
            'phase_1': {
                'name': 'Fundación y Quick Wins',
                'duration_months': 3,
                'campaigns': phase1_campaigns[['id', 'name', 'category', 'budget', 'success_probability']].to_dict('records'),
                'total_budget': phase1_campaigns['budget'].apply(lambda x: x['amount']).sum(),
                'expected_roi': phase1_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean()
            },
            'phase_2': {
                'name': 'Escalamiento por Categorías Prioritarias',
                'duration_months': 6,
                'campaigns': phase2_campaigns[['id', 'name', 'category', 'budget', 'success_probability']].to_dict('records'),
                'total_budget': phase2_campaigns['budget'].apply(lambda x: x['amount']).sum(),
                'expected_roi': phase2_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean()
            },
            'phase_3': {
                'name': 'Innovación y Diferenciación',
                'duration_months': 9,
                'campaigns': phase3_campaigns[['id', 'name', 'category', 'budget', 'success_probability']].to_dict('records'),
                'total_budget': phase3_campaigns['budget'].apply(lambda x: x['amount']).sum(),
                'expected_roi': phase3_campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']).mean()
            }
        }
        
        return roadmap
    
    def generate_all_industry_reports(self, output_dir: str = 'industry_reports') -> Dict[str, str]:
        """Genera reportes para todas las industrias soportadas"""
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        generated_reports = {}
        
        for industry in self.industry_configs.keys():
            print(f"Generando reporte para {industry}...")
            report = self.generate_industry_report(industry)
            
            if 'error' not in report:
                filename = f"{industry.lower().replace(' ', '_')}_report.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
                
                generated_reports[industry] = filepath
                print(f"✅ Reporte de {industry} guardado en: {filepath}")
            else:
                print(f"❌ Error generando reporte de {industry}: {report['error']}")
        
        return generated_reports

def main():
    """Función principal de demostración"""
    print("=== GENERADOR DE REPORTES POR INDUSTRIA ===")
    
    # Inicializar generador
    generator = IndustryReportGenerator()
    
    # Generar reporte para E-commerce
    print("Generando reporte para E-commerce...")
    ecommerce_report = generator.generate_industry_report('E-commerce')
    
    if 'error' not in ecommerce_report:
        print(f"\n📊 REPORTE DE E-COMMERCE")
        print(f"Total de campañas: {ecommerce_report['summary']['total_campaigns']}")
        print(f"Presupuesto total: ${ecommerce_report['summary']['total_budget']:,.2f}")
        print(f"ROI promedio: {ecommerce_report['summary']['roi_analysis']['average']:.1f}x")
        print(f"Campañas de alto rendimiento: {ecommerce_report['summary']['roi_analysis']['high_performers_count']}")
        
        print(f"\n🏆 CATEGORÍAS TOP")
        for category, data in ecommerce_report['category_analysis'].items():
            print(f"• {category}: {data['count']} campañas, ROI avg: {data['average_roi']:.1f}x")
        
        print(f"\n💡 RECOMENDACIONES")
        print("Campañas de Alto ROI:")
        for campaign in ecommerce_report['recommended_campaigns']['high_roi'][:3]:
            print(f"• {campaign['name']} - ROI: {campaign['metrics']['return_on_ad_spend']:.1f}x")
    
    # Generar todos los reportes
    print(f"\n🔄 GENERANDO TODOS LOS REPORTES...")
    all_reports = generator.generate_all_industry_reports()
    
    print(f"\n✅ Reportes generados:")
    for industry, filepath in all_reports.items():
        print(f"• {industry}: {filepath}")

if __name__ == "__main__":
    main()


