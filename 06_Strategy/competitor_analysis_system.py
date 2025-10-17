#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análisis de Competencia para Marketing con IA
========================================================
Analiza competidores y genera insights estratégicos para optimizar campañas.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import random
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class CompetitorAnalysisSystem:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el sistema de análisis de competencia"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        
        # Base de datos simulada de competidores
        self.competitors_database = self._initialize_competitors_database()
        
        # Métricas de análisis
        self.analysis_metrics = {
            'market_share': {'weight': 0.25, 'type': 'percentage'},
            'brand_awareness': {'weight': 0.20, 'type': 'percentage'},
            'customer_satisfaction': {'weight': 0.15, 'type': 'rating'},
            'pricing_competitiveness': {'weight': 0.15, 'type': 'rating'},
            'innovation_score': {'weight': 0.10, 'type': 'rating'},
            'social_media_presence': {'weight': 0.10, 'type': 'rating'},
            'content_quality': {'weight': 0.05, 'type': 'rating'}
        }
        
        # Estrategias competitivas
        self.competitive_strategies = {
            'cost_leadership': 'Liderazgo en costos',
            'differentiation': 'Diferenciación',
            'focus': 'Enfoque en nicho',
            'innovation': 'Innovación',
            'customer_intimacy': 'Intimidad con el cliente'
        }
    
    def _initialize_competitors_database(self) -> Dict[str, Any]:
        """Inicializa la base de datos de competidores"""
        competitors = {}
        
        # Competidores principales por industria
        industries = ['tecnología', 'marketing', 'ventas', 'finanzas', 'salud', 'educación']
        
        for industry in industries:
            competitors[industry] = []
            
            # Generar 5-8 competidores por industria
            num_competitors = random.randint(5, 8)
            
            for i in range(num_competitors):
                competitor = {
                    'id': f"{industry}_{i+1}",
                    'name': f"Competidor {i+1} - {industry.title()}",
                    'industry': industry,
                    'market_share': random.uniform(5, 25),
                    'brand_awareness': random.uniform(60, 95),
                    'customer_satisfaction': random.uniform(3.5, 4.8),
                    'pricing_competitiveness': random.uniform(3.0, 5.0),
                    'innovation_score': random.uniform(3.0, 5.0),
                    'social_media_presence': random.uniform(3.0, 5.0),
                    'content_quality': random.uniform(3.0, 5.0),
                    'revenue': random.uniform(1000000, 50000000),
                    'employees': random.randint(50, 2000),
                    'founded_year': random.randint(1990, 2020),
                    'headquarters': random.choice(['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao']),
                    'website': f"https://competidor{i+1}-{industry}.com",
                    'social_media': {
                        'facebook': random.randint(1000, 100000),
                        'twitter': random.randint(500, 50000),
                        'linkedin': random.randint(200, 20000),
                        'instagram': random.randint(1000, 80000)
                    },
                    'strengths': random.sample([
                        'Precios competitivos', 'Innovación tecnológica', 'Servicio al cliente',
                        'Experiencia del usuario', 'Marca reconocida', 'Distribución global',
                        'Calidad del producto', 'Soporte técnico', 'Facilidad de uso'
                    ], random.randint(2, 4)),
                    'weaknesses': random.sample([
                        'Precios altos', 'Limitaciones técnicas', 'Soporte limitado',
                        'Interfaz compleja', 'Funcionalidades limitadas', 'Documentación pobre',
                        'Tiempo de respuesta lento', 'Falta de integraciones'
                    ], random.randint(1, 3)),
                    'opportunities': random.sample([
                        'Expansión internacional', 'Nuevos mercados', 'Innovación de producto',
                        'Partnerships estratégicos', 'Digitalización', 'Sostenibilidad',
                        'Personalización', 'Automatización'
                    ], random.randint(2, 4)),
                    'threats': random.sample([
                        'Competencia intensa', 'Cambios regulatorios', 'Disrupción tecnológica',
                        'Crisis económica', 'Nuevos competidores', 'Cambios en preferencias',
                        'Problemas de suministro', 'Ciberseguridad'
                    ], random.randint(2, 4))
                }
                
                competitors[industry].append(competitor)
        
        return competitors
    
    def analyze_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Analiza un competidor específico"""
        competitor = self._find_competitor(competitor_id)
        if not competitor:
            return {"error": f"Competidor {competitor_id} no encontrado"}
        
        # Calcular score competitivo
        competitive_score = self._calculate_competitive_score(competitor)
        
        # Análisis de fortalezas y debilidades
        swot_analysis = self._perform_swot_analysis(competitor)
        
        # Análisis de posicionamiento
        positioning_analysis = self._analyze_positioning(competitor)
        
        # Recomendaciones estratégicas
        strategic_recommendations = self._generate_strategic_recommendations(
            competitor, competitive_score, swot_analysis
        )
        
        return {
            'competitor_id': competitor_id,
            'competitor_name': competitor['name'],
            'industry': competitor['industry'],
            'competitive_score': competitive_score,
            'swot_analysis': swot_analysis,
            'positioning_analysis': positioning_analysis,
            'strategic_recommendations': strategic_recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _find_competitor(self, competitor_id: str) -> Dict[str, Any]:
        """Encuentra un competidor por ID"""
        for industry, competitors in self.competitors_database.items():
            for competitor in competitors:
                if competitor['id'] == competitor_id:
                    return competitor
        return None
    
    def _calculate_competitive_score(self, competitor: Dict) -> Dict[str, Any]:
        """Calcula el score competitivo de un competidor"""
        total_score = 0
        weighted_scores = {}
        
        for metric, config in self.analysis_metrics.items():
            value = competitor[metric]
            weight = config['weight']
            
            # Normalizar valor según el tipo
            if config['type'] == 'percentage':
                normalized_value = value / 100
            elif config['type'] == 'rating':
                normalized_value = value / 5
            else:
                normalized_value = value
            
            weighted_score = normalized_value * weight
            weighted_scores[metric] = {
                'raw_value': value,
                'normalized_value': normalized_value,
                'weight': weight,
                'weighted_score': weighted_score
            }
            
            total_score += weighted_score
        
        # Clasificar score
        if total_score >= 0.8:
            classification = 'Líder del mercado'
        elif total_score >= 0.6:
            classification = 'Competidor fuerte'
        elif total_score >= 0.4:
            classification = 'Competidor moderado'
        else:
            classification = 'Competidor débil'
        
        return {
            'total_score': total_score,
            'classification': classification,
            'weighted_scores': weighted_scores,
            'max_possible_score': 1.0
        }
    
    def _perform_swot_analysis(self, competitor: Dict) -> Dict[str, Any]:
        """Realiza análisis SWOT del competidor"""
        return {
            'strengths': {
                'items': competitor['strengths'],
                'count': len(competitor['strengths']),
                'analysis': self._analyze_swot_category(competitor['strengths'], 'strengths')
            },
            'weaknesses': {
                'items': competitor['weaknesses'],
                'count': len(competitor['weaknesses']),
                'analysis': self._analyze_swot_category(competitor['weaknesses'], 'weaknesses')
            },
            'opportunities': {
                'items': competitor['opportunities'],
                'count': len(competitor['opportunities']),
                'analysis': self._analyze_swot_category(competitor['opportunities'], 'opportunities')
            },
            'threats': {
                'items': competitor['threats'],
                'count': len(competitor['threats']),
                'analysis': self._analyze_swot_category(competitor['threats'], 'threats')
            }
        }
    
    def _analyze_swot_category(self, items: List[str], category: str) -> str:
        """Analiza una categoría SWOT específica"""
        if category == 'strengths':
            if len(items) >= 4:
                return "Fortalezas sólidas y diversas"
            elif len(items) >= 2:
                return "Fortalezas moderadas"
            else:
                return "Fortalezas limitadas"
        elif category == 'weaknesses':
            if len(items) >= 3:
                return "Múltiples debilidades identificadas"
            elif len(items) >= 1:
                return "Algunas debilidades presentes"
            else:
                return "Pocas debilidades evidentes"
        elif category == 'opportunities':
            if len(items) >= 4:
                return "Abundantes oportunidades de crecimiento"
            elif len(items) >= 2:
                return "Oportunidades moderadas disponibles"
            else:
                return "Oportunidades limitadas"
        else:  # threats
            if len(items) >= 3:
                return "Múltiples amenazas del entorno"
            elif len(items) >= 1:
                return "Algunas amenazas identificadas"
            else:
                return "Pocas amenazas evidentes"
    
    def _analyze_positioning(self, competitor: Dict) -> Dict[str, Any]:
        """Analiza el posicionamiento del competidor"""
        # Determinar estrategia competitiva principal
        strategy_scores = {}
        
        # Liderazgo en costos
        if competitor['pricing_competitiveness'] >= 4.0:
            strategy_scores['cost_leadership'] = 0.8
        else:
            strategy_scores['cost_leadership'] = competitor['pricing_competitiveness'] / 5
        
        # Diferenciación
        if competitor['innovation_score'] >= 4.0 and competitor['content_quality'] >= 4.0:
            strategy_scores['differentiation'] = 0.9
        else:
            strategy_scores['differentiation'] = (competitor['innovation_score'] + competitor['content_quality']) / 10
        
        # Enfoque en nicho
        if competitor['market_share'] < 15 and competitor['customer_satisfaction'] >= 4.0:
            strategy_scores['focus'] = 0.8
        else:
            strategy_scores['focus'] = 0.5
        
        # Innovación
        strategy_scores['innovation'] = competitor['innovation_score'] / 5
        
        # Intimidad con el cliente
        if competitor['customer_satisfaction'] >= 4.5:
            strategy_scores['customer_intimacy'] = 0.9
        else:
            strategy_scores['customer_intimacy'] = competitor['customer_satisfaction'] / 5
        
        # Encontrar estrategia dominante
        dominant_strategy = max(strategy_scores.keys(), key=lambda x: strategy_scores[x])
        
        # Análisis de posicionamiento en el mercado
        market_position = self._determine_market_position(competitor)
        
        return {
            'strategy_scores': strategy_scores,
            'dominant_strategy': dominant_strategy,
            'strategy_description': self.competitive_strategies[dominant_strategy],
            'market_position': market_position,
            'positioning_strength': max(strategy_scores.values())
        }
    
    def _determine_market_position(self, competitor: Dict) -> str:
        """Determina la posición del competidor en el mercado"""
        market_share = competitor['market_share']
        brand_awareness = competitor['brand_awareness']
        
        if market_share >= 20 and brand_awareness >= 80:
            return "Líder del mercado"
        elif market_share >= 10 and brand_awareness >= 60:
            return "Competidor fuerte"
        elif market_share >= 5 and brand_awareness >= 40:
            return "Competidor establecido"
        elif market_share >= 2 and brand_awareness >= 20:
            return "Competidor emergente"
        else:
            return "Competidor nicho"
    
    def _generate_strategic_recommendations(self, competitor: Dict, 
                                          competitive_score: Dict, 
                                          swot_analysis: Dict) -> List[str]:
        """Genera recomendaciones estratégicas basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones basadas en score competitivo
        if competitive_score['total_score'] >= 0.8:
            recommendations.append("🎯 **Competidor líder**: Monitorear de cerca y buscar diferenciación")
        elif competitive_score['total_score'] >= 0.6:
            recommendations.append("⚔️ **Competidor fuerte**: Desarrollar ventajas competitivas específicas")
        elif competitive_score['total_score'] >= 0.4:
            recommendations.append("📈 **Oportunidad de crecimiento**: Aprovechar debilidades identificadas")
        else:
            recommendations.append("🚀 **Ventaja competitiva**: Posicionarse como alternativa superior")
        
        # Recomendaciones basadas en fortalezas
        strengths = swot_analysis['strengths']['items']
        if 'Precios competitivos' in strengths:
            recommendations.append("💰 **Estrategia de precios**: Desarrollar propuesta de valor superior")
        if 'Innovación tecnológica' in strengths:
            recommendations.append("🔬 **Innovación**: Acelerar desarrollo de nuevas funcionalidades")
        if 'Servicio al cliente' in strengths:
            recommendations.append("🤝 **Servicio**: Mejorar experiencia del cliente")
        
        # Recomendaciones basadas en debilidades
        weaknesses = swot_analysis['weaknesses']['items']
        if 'Precios altos' in weaknesses:
            recommendations.append("💸 **Oportunidad de precios**: Ofrecer soluciones más económicas")
        if 'Limitaciones técnicas' in weaknesses:
            recommendations.append("⚙️ **Ventaja técnica**: Desarrollar funcionalidades superiores")
        if 'Soporte limitado' in weaknesses:
            recommendations.append("🆘 **Soporte**: Ofrecer mejor servicio de atención al cliente")
        
        # Recomendaciones basadas en oportunidades
        opportunities = swot_analysis['opportunities']['items']
        if 'Expansión internacional' in opportunities:
            recommendations.append("🌍 **Expansión**: Considerar entrada en mercados internacionales")
        if 'Nuevos mercados' in opportunities:
            recommendations.append("🎯 **Diversificación**: Explorar nuevos segmentos de mercado")
        if 'Innovación de producto' in opportunities:
            recommendations.append("💡 **Innovación**: Invertir en I+D para nuevos productos")
        
        return recommendations
    
    def compare_competitors(self, competitor_ids: List[str]) -> Dict[str, Any]:
        """Compara múltiples competidores"""
        if len(competitor_ids) < 2:
            return {"error": "Se requieren al menos 2 competidores para comparar"}
        
        competitors_data = []
        for competitor_id in competitor_ids:
            competitor = self._find_competitor(competitor_id)
            if competitor:
                competitors_data.append(competitor)
        
        if len(competitors_data) < 2:
            return {"error": "No se encontraron suficientes competidores válidos"}
        
        # Análisis comparativo
        comparison_results = {
            'competitors': [],
            'comparison_matrix': {},
            'rankings': {},
            'insights': [],
            'recommendations': []
        }
        
        # Analizar cada competidor
        for competitor in competitors_data:
            analysis = self.analyze_competitor(competitor['id'])
            if 'error' not in analysis:
                comparison_results['competitors'].append({
                    'id': competitor['id'],
                    'name': competitor['name'],
                    'competitive_score': analysis['competitive_score']['total_score'],
                    'classification': analysis['competitive_score']['classification'],
                    'market_position': analysis['positioning_analysis']['market_position']
                })
        
        # Crear matriz de comparación
        metrics = ['market_share', 'brand_awareness', 'customer_satisfaction', 
                  'pricing_competitiveness', 'innovation_score', 'social_media_presence', 'content_quality']
        
        for metric in metrics:
            comparison_results['comparison_matrix'][metric] = {}
            for competitor in competitors_data:
                comparison_results['comparison_matrix'][metric][competitor['name']] = competitor[metric]
        
        # Rankings
        for metric in metrics:
            sorted_competitors = sorted(competitors_data, key=lambda x: x[metric], reverse=True)
            comparison_results['rankings'][metric] = [
                {'name': comp['name'], 'value': comp[metric]} 
                for comp in sorted_competitors
            ]
        
        # Generar insights
        comparison_results['insights'] = self._generate_comparison_insights(comparison_results)
        
        # Generar recomendaciones
        comparison_results['recommendations'] = self._generate_comparison_recommendations(comparison_results)
        
        return comparison_results
    
    def _generate_comparison_insights(self, comparison_results: Dict) -> List[str]:
        """Genera insights basados en la comparación"""
        insights = []
        
        # Insight sobre líder en market share
        market_share_ranking = comparison_results['rankings']['market_share']
        if market_share_ranking:
            leader = market_share_ranking[0]
            insights.append(f"🏆 **Líder en participación**: {leader['name']} domina con {leader['value']:.1f}% del mercado")
        
        # Insight sobre satisfacción del cliente
        satisfaction_ranking = comparison_results['rankings']['customer_satisfaction']
        if satisfaction_ranking:
            best_satisfaction = satisfaction_ranking[0]
            insights.append(f"😊 **Mejor satisfacción**: {best_satisfaction['name']} lidera con {best_satisfaction['value']:.1f}/5 en satisfacción")
        
        # Insight sobre innovación
        innovation_ranking = comparison_results['rankings']['innovation_score']
        if innovation_ranking:
            most_innovative = innovation_ranking[0]
            insights.append(f"🚀 **Más innovador**: {most_innovative['name']} destaca en innovación con {most_innovative['value']:.1f}/5")
        
        # Insight sobre precios
        pricing_ranking = comparison_results['rankings']['pricing_competitiveness']
        if pricing_ranking:
            most_competitive_pricing = pricing_ranking[0]
            insights.append(f"💰 **Mejor precio**: {most_competitive_pricing['name']} ofrece la mejor relación precio-calidad")
        
        return insights
    
    def _generate_comparison_recommendations(self, comparison_results: Dict) -> List[str]:
        """Genera recomendaciones basadas en la comparación"""
        recommendations = []
        
        # Recomendación basada en posiciones competitivas
        competitors = comparison_results['competitors']
        if len(competitors) >= 2:
            # Encontrar el competidor más fuerte
            strongest = max(competitors, key=lambda x: x['competitive_score'])
            weakest = min(competitors, key=lambda x: x['competitive_score'])
            
            recommendations.append(f"🎯 **Estrategia vs {strongest['name']}**: Desarrollar ventajas específicas para competir con el líder")
            recommendations.append(f"📈 **Oportunidad vs {weakest['name']}**: Aprovechar debilidades para ganar participación")
        
        # Recomendación basada en métricas específicas
        market_share_ranking = comparison_results['rankings']['market_share']
        if market_share_ranking:
            avg_market_share = np.mean([comp['value'] for comp in market_share_ranking])
            if avg_market_share < 10:
                recommendations.append("🌍 **Expansión de mercado**: Oportunidad para aumentar participación en un mercado fragmentado")
        
        # Recomendación basada en innovación
        innovation_ranking = comparison_results['rankings']['innovation_score']
        if innovation_ranking:
            avg_innovation = np.mean([comp['value'] for comp in innovation_ranking])
            if avg_innovation < 3.5:
                recommendations.append("💡 **Innovación disruptiva**: Oportunidad para liderar con innovación en un mercado conservador")
        
        return recommendations
    
    def analyze_industry_landscape(self, industry: str) -> Dict[str, Any]:
        """Analiza el panorama competitivo de una industria"""
        if industry not in self.competitors_database:
            return {"error": f"Industria '{industry}' no encontrada"}
        
        competitors = self.competitors_database[industry]
        
        # Análisis del mercado
        market_analysis = {
            'total_competitors': len(competitors),
            'total_market_share': sum(comp['market_share'] for comp in competitors),
            'average_market_share': np.mean([comp['market_share'] for comp in competitors]),
            'market_concentration': self._calculate_market_concentration(competitors),
            'average_revenue': np.mean([comp['revenue'] for comp in competitors]),
            'total_employees': sum(comp['employees'] for comp in competitors)
        }
        
        # Análisis de competidores por tamaño
        size_analysis = self._analyze_competitor_sizes(competitors)
        
        # Análisis de estrategias competitivas
        strategy_analysis = self._analyze_industry_strategies(competitors)
        
        # Tendencias del mercado
        market_trends = self._identify_market_trends(competitors)
        
        # Oportunidades de mercado
        market_opportunities = self._identify_market_opportunities(competitors, market_analysis)
        
        return {
            'industry': industry,
            'market_analysis': market_analysis,
            'size_analysis': size_analysis,
            'strategy_analysis': strategy_analysis,
            'market_trends': market_trends,
            'market_opportunities': market_opportunities,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_market_concentration(self, competitors: List[Dict]) -> str:
        """Calcula la concentración del mercado"""
        market_shares = [comp['market_share'] for comp in competitors]
        market_shares.sort(reverse=True)
        
        # Calcular índice de concentración (suma de los 4 mayores)
        top4_share = sum(market_shares[:4])
        
        if top4_share >= 75:
            return "Muy concentrado"
        elif top4_share >= 50:
            return "Moderadamente concentrado"
        else:
            return "Fragmentado"
    
    def _analyze_competitor_sizes(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analiza los tamaños de los competidores"""
        revenues = [comp['revenue'] for comp in competitors]
        employees = [comp['employees'] for comp in competitors]
        
        # Clasificar por tamaño
        large_companies = [comp for comp in competitors if comp['revenue'] >= 10000000]
        medium_companies = [comp for comp in competitors if 1000000 <= comp['revenue'] < 10000000]
        small_companies = [comp for comp in competitors if comp['revenue'] < 1000000]
        
        return {
            'large_companies': {
                'count': len(large_companies),
                'percentage': len(large_companies) / len(competitors) * 100,
                'average_revenue': np.mean([comp['revenue'] for comp in large_companies]) if large_companies else 0
            },
            'medium_companies': {
                'count': len(medium_companies),
                'percentage': len(medium_companies) / len(competitors) * 100,
                'average_revenue': np.mean([comp['revenue'] for comp in medium_companies]) if medium_companies else 0
            },
            'small_companies': {
                'count': len(small_companies),
                'percentage': len(small_companies) / len(competitors) * 100,
                'average_revenue': np.mean([comp['revenue'] for comp in small_companies]) if small_companies else 0
            }
        }
    
    def _analyze_industry_strategies(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analiza las estrategias competitivas en la industria"""
        strategies = defaultdict(int)
        
        for competitor in competitors:
            # Determinar estrategia principal basada en métricas
            if competitor['pricing_competitiveness'] >= 4.0:
                strategies['cost_leadership'] += 1
            if competitor['innovation_score'] >= 4.0:
                strategies['innovation'] += 1
            if competitor['customer_satisfaction'] >= 4.5:
                strategies['customer_intimacy'] += 1
            if competitor['market_share'] < 15 and competitor['customer_satisfaction'] >= 4.0:
                strategies['focus'] += 1
            if competitor['innovation_score'] >= 3.5 and competitor['content_quality'] >= 3.5:
                strategies['differentiation'] += 1
        
        total = len(competitors)
        strategy_percentages = {strategy: (count / total) * 100 for strategy, count in strategies.items()}
        
        return {
            'strategy_distribution': strategy_percentages,
            'dominant_strategy': max(strategies.keys(), key=lambda x: strategies[x]) if strategies else None,
            'strategy_diversity': len(strategies)
        }
    
    def _identify_market_trends(self, competitors: List[Dict]) -> List[str]:
        """Identifica tendencias del mercado"""
        trends = []
        
        # Tendencias basadas en métricas promedio
        avg_innovation = np.mean([comp['innovation_score'] for comp in competitors])
        avg_social_presence = np.mean([comp['social_media_presence'] for comp in competitors])
        avg_content_quality = np.mean([comp['content_quality'] for comp in competitors])
        
        if avg_innovation >= 4.0:
            trends.append("🚀 **Alta innovación**: La industria se caracteriza por un fuerte enfoque en innovación")
        
        if avg_social_presence >= 4.0:
            trends.append("📱 **Presencia social fuerte**: Los competidores invierten significativamente en redes sociales")
        
        if avg_content_quality >= 4.0:
            trends.append("📝 **Calidad de contenido**: La industria prioriza la calidad del contenido")
        
        # Tendencias basadas en distribución de empresas
        founded_years = [comp['founded_year'] for comp in competitors]
        recent_companies = [year for year in founded_years if year >= 2015]
        
        if len(recent_companies) / len(competitors) >= 0.3:
            trends.append("🆕 **Mercado dinámico**: Alta proporción de empresas nuevas indica un mercado en crecimiento")
        
        return trends
    
    def _identify_market_opportunities(self, competitors: List[Dict], market_analysis: Dict) -> List[str]:
        """Identifica oportunidades de mercado"""
        opportunities = []
        
        # Oportunidad basada en concentración del mercado
        if market_analysis['market_concentration'] == "Fragmentado":
            opportunities.append("🎯 **Mercado fragmentado**: Oportunidad para consolidar y liderar")
        
        # Oportunidad basada en satisfacción del cliente
        avg_satisfaction = np.mean([comp['customer_satisfaction'] for comp in competitors])
        if avg_satisfaction < 4.0:
            opportunities.append("😊 **Mejora de satisfacción**: Oportunidad para destacar con mejor servicio al cliente")
        
        # Oportunidad basada en innovación
        avg_innovation = np.mean([comp['innovation_score'] for comp in competitors])
        if avg_innovation < 3.5:
            opportunities.append("💡 **Innovación disruptiva**: Oportunidad para liderar con innovación")
        
        # Oportunidad basada en precios
        avg_pricing = np.mean([comp['pricing_competitiveness'] for comp in competitors])
        if avg_pricing < 3.5:
            opportunities.append("💰 **Estrategia de precios**: Oportunidad para ofrecer mejor valor")
        
        return opportunities

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE ANÁLISIS DE COMPETENCIA ===")
    
    # Inicializar sistema
    competitor_analysis = CompetitorAnalysisSystem()
    
    # Analizar competidor individual
    print("Analizando competidor individual...")
    competitor_id = "tecnología_1"
    analysis = competitor_analysis.analyze_competitor(competitor_id)
    
    if 'error' not in analysis:
        print(f"\n📊 ANÁLISIS DE COMPETIDOR")
        print(f"Competidor: {analysis['competitor_name']}")
        print(f"Industria: {analysis['industry']}")
        print(f"Score competitivo: {analysis['competitive_score']['total_score']:.2f}")
        print(f"Clasificación: {analysis['competitive_score']['classification']}")
        print(f"Posición en el mercado: {analysis['positioning_analysis']['market_position']}")
        
        print(f"\n💡 RECOMENDACIONES ESTRATÉGICAS")
        for recommendation in analysis['strategic_recommendations']:
            print(f"• {recommendation}")
    
    # Comparar competidores
    print(f"\n🔄 COMPARANDO COMPETIDORES...")
    competitor_ids = ["tecnología_1", "tecnología_2", "tecnología_3"]
    comparison = competitor_analysis.compare_competitors(competitor_ids)
    
    if 'error' not in comparison:
        print(f"\n📈 COMPARACIÓN DE COMPETIDORES")
        print(f"Competidores analizados: {len(comparison['competitors'])}")
        
        print(f"\n🏆 RANKINGS")
        for metric, ranking in comparison['rankings'].items():
            print(f"\n{metric.replace('_', ' ').title()}:")
            for i, comp in enumerate(ranking, 1):
                print(f"  {i}. {comp['name']}: {comp['value']:.2f}")
        
        print(f"\n💡 INSIGHTS")
        for insight in comparison['insights']:
            print(f"• {insight}")
        
        print(f"\n🎯 RECOMENDACIONES")
        for recommendation in comparison['recommendations']:
            print(f"• {recommendation}")
    
    # Analizar panorama de la industria
    print(f"\n🏭 ANALIZANDO PANORAMA DE LA INDUSTRIA...")
    industry_analysis = competitor_analysis.analyze_industry_landscape("tecnología")
    
    if 'error' not in industry_analysis:
        print(f"\n📊 ANÁLISIS DE LA INDUSTRIA")
        print(f"Industria: {industry_analysis['industry']}")
        print(f"Total de competidores: {industry_analysis['market_analysis']['total_competitors']}")
        print(f"Participación total del mercado: {industry_analysis['market_analysis']['total_market_share']:.1f}%")
        print(f"Concentración del mercado: {industry_analysis['market_analysis']['market_concentration']}")
        
        print(f"\n📈 DISTRIBUCIÓN POR TAMAÑO")
        size_analysis = industry_analysis['size_analysis']
        print(f"Grandes empresas: {size_analysis['large_companies']['count']} ({size_analysis['large_companies']['percentage']:.1f}%)")
        print(f"Medianas empresas: {size_analysis['medium_companies']['count']} ({size_analysis['medium_companies']['percentage']:.1f}%)")
        print(f"Pequeñas empresas: {size_analysis['small_companies']['count']} ({size_analysis['small_companies']['percentage']:.1f}%)")
        
        print(f"\n🚀 TENDENCIAS DEL MERCADO")
        for trend in industry_analysis['market_trends']:
            print(f"• {trend}")
        
        print(f"\n🎯 OPORTUNIDADES DE MERCADO")
        for opportunity in industry_analysis['market_opportunities']:
            print(f"• {opportunity}")
    
    print(f"\n✅ Sistema de análisis de competencia configurado y funcionando")

if __name__ == "__main__":
    main()
