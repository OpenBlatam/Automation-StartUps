#!/usr/bin/env python3
"""
🚀 ADVANCED MARKETING BRAIN SYSTEM
Sistema Avanzado de Generación de Conceptos de Marketing con IA
Inspirado en ClickUp Brain - Análisis de Documentos y Sugerencias Accionables
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import random
from dataclasses import dataclass
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CampaignTheme:
    """Estructura para temas de campañas"""
    theme: str
    frequency: int
    success_rate: float
    avg_metrics: Dict[str, float]
    related_technologies: List[str]
    related_channels: List[str]
    related_verticals: List[str]

@dataclass
class MarketingConcept:
    """Estructura para conceptos de marketing generados"""
    concept_id: str
    name: str
    description: str
    category: str
    technology: str
    channel: str
    vertical: str
    objective: str
    inspiration_campaigns: List[int]
    success_probability: float
    complexity: str
    priority: str
    estimated_budget: Dict[str, Any]
    timeline: Dict[str, Any]
    expected_metrics: Dict[str, float]
    tags: List[str]
    created_at: str

class AdvancedMarketingBrain:
    """
    Sistema Avanzado de IA para Generación de Conceptos de Marketing
    Funciona como ClickUp Brain analizando documentos y generando sugerencias accionables
    """
    
    def __init__(self, campaigns_file: str = None, strategies_file: str = None):
        self.campaigns_file = campaigns_file or "1000_ai_marketing_campaigns.json"
        self.strategies_file = strategies_file or "ESTRATEGIAS_CONTENIDO_MASTER_COMPLETO.md"
        
        # Cargar datos
        self.campaigns = self._load_campaigns()
        self.strategies = self._load_strategies()
        
        # Análisis de temas
        self.themes = self._extract_themes()
        self.success_patterns = self._analyze_success_patterns()
        self.trend_analysis = self._analyze_trends()
        
        # Configuración de generación
        self.concept_counter = 0
        
        logger.info("🧠 Advanced Marketing Brain System initialized successfully")
    
    def _load_campaigns(self) -> List[Dict]:
        """Cargar campañas desde archivo JSON"""
        try:
            with open(self.campaigns_file, 'r', encoding='utf-8') as f:
                campaigns = json.load(f)
            logger.info(f"✅ Loaded {len(campaigns)} campaigns from {self.campaigns_file}")
            return campaigns
        except FileNotFoundError:
            logger.warning(f"⚠️ Campaigns file {self.campaigns_file} not found, using sample data")
            return self._get_sample_campaigns()
    
    def _load_strategies(self) -> str:
        """Cargar estrategias desde archivo Markdown"""
        try:
            with open(self.strategies_file, 'r', encoding='utf-8') as f:
                strategies = f.read()
            logger.info(f"✅ Loaded strategies from {self.strategies_file}")
            return strategies
        except FileNotFoundError:
            logger.warning(f"⚠️ Strategies file {self.strategies_file} not found")
            return ""
    
    def _get_sample_campaigns(self) -> List[Dict]:
        """Datos de muestra si no se encuentra el archivo"""
        return [
            {
                "id": 1,
                "name": "Smart Personalization Boost Campaign",
                "category": "Personalización con IA",
                "technology": "Machine Learning",
                "channel": "Redes Sociales",
                "objective": "Aumentar conversiones",
                "vertical": "E-commerce",
                "description": "Implementa algoritmos de Machine Learning para personalizar experiencias únicas en Redes Sociales, adaptando contenido, ofertas y mensajes en tiempo real según el comportamiento y preferencias de cada usuario.",
                "budget": {"amount": 25000, "tier": "Avanzado", "currency": "USD"},
                "timeline": {"start_date": "2024-01-15", "end_date": "2024-03-15", "duration_weeks": 8},
                "metrics": {"conversion_rate": 8.5, "click_through_rate": 4.2, "engagement_rate": 7.8, "cost_per_acquisition": 45.50, "return_on_ad_spend": 5.2, "customer_lifetime_value": 320.75},
                "success_probability": 0.87,
                "complexity": "Media",
                "priority": "Alta",
                "tags": ["Personalización con IA", "Machine Learning", "Redes Sociales", "E-commerce"],
                "created_at": "2024-01-01 10:00:00"
            }
        ]
    
    def _extract_themes(self) -> Dict[str, CampaignTheme]:
        """Extraer temas principales de las campañas exitosas"""
        themes = defaultdict(lambda: {
            'campaigns': [],
            'success_rates': [],
            'metrics': defaultdict(list),
            'technologies': Counter(),
            'channels': Counter(),
            'verticals': Counter()
        })
        
        for campaign in self.campaigns:
            # Extraer tema principal de la categoría
            theme = campaign.get('category', 'General')
            
            themes[theme]['campaigns'].append(campaign['id'])
            themes[theme]['success_rates'].append(campaign.get('success_probability', 0.5))
            
            # Agregar métricas
            metrics = campaign.get('metrics', {})
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    themes[theme]['metrics'][metric].append(value)
            
            # Contar tecnologías, canales y verticales
            themes[theme]['technologies'][campaign.get('technology', 'Unknown')] += 1
            themes[theme]['channels'][campaign.get('channel', 'Unknown')] += 1
            themes[theme]['verticals'][campaign.get('vertical', 'Unknown')] += 1
        
        # Convertir a objetos CampaignTheme
        theme_objects = {}
        for theme_name, theme_data in themes.items():
            avg_success_rate = np.mean(theme_data['success_rates']) if theme_data['success_rates'] else 0.5
            
            avg_metrics = {}
            for metric, values in theme_data['metrics'].items():
                avg_metrics[metric] = np.mean(values) if values else 0
            
            theme_objects[theme_name] = CampaignTheme(
                theme=theme_name,
                frequency=len(theme_data['campaigns']),
                success_rate=avg_success_rate,
                avg_metrics=avg_metrics,
                related_technologies=[tech for tech, _ in theme_data['technologies'].most_common(5)],
                related_channels=[channel for channel, _ in theme_data['channels'].most_common(5)],
                related_verticals=[vertical for vertical, _ in theme_data['verticals'].most_common(5)]
            )
        
        logger.info(f"🎯 Extracted {len(theme_objects)} themes from campaigns")
        return theme_objects
    
    def _analyze_success_patterns(self) -> Dict[str, Any]:
        """Analizar patrones de éxito en las campañas"""
        successful_campaigns = [c for c in self.campaigns if c.get('success_probability', 0) > 0.8]
        
        patterns = {
            'high_success_technologies': Counter(),
            'high_success_channels': Counter(),
            'high_success_verticals': Counter(),
            'high_success_objectives': Counter(),
            'avg_high_success_metrics': defaultdict(list),
            'common_tags': Counter()
        }
        
        for campaign in successful_campaigns:
            patterns['high_success_technologies'][campaign.get('technology', 'Unknown')] += 1
            patterns['high_success_channels'][campaign.get('channel', 'Unknown')] += 1
            patterns['high_success_verticals'][campaign.get('vertical', 'Unknown')] += 1
            patterns['high_success_objectives'][campaign.get('objective', 'Unknown')] += 1
            
            # Métricas de campañas exitosas
            metrics = campaign.get('metrics', {})
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    patterns['avg_high_success_metrics'][metric].append(value)
            
            # Tags comunes
            for tag in campaign.get('tags', []):
                patterns['common_tags'][tag] += 1
        
        # Calcular promedios
        for metric, values in patterns['avg_high_success_metrics'].items():
            patterns['avg_high_success_metrics'][metric] = np.mean(values) if values else 0
        
        logger.info(f"📊 Analyzed success patterns from {len(successful_campaigns)} high-success campaigns")
        return patterns
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analizar tendencias emergentes en el contenido de estrategias"""
        trends = {
            'popular_formats': [],
            'psychological_triggers': [],
            'content_types': [],
            'platform_strategies': [],
            'engagement_tactics': []
        }
        
        if self.strategies:
            # Extraer formatos populares
            format_patterns = re.findall(r'(\*\*.*?\*\*.*?)(?=\n|$)', self.strategies, re.MULTILINE)
            trends['popular_formats'] = [f.strip() for f in format_patterns[:20]]
            
            # Extraer triggers psicológicos
            trigger_patterns = re.findall(r'(Escasez|Prueba Social|Urgencia|Autoridad|Reciprocidad)', self.strategies)
            trends['psychological_triggers'] = list(set(trigger_patterns))
            
            # Extraer tipos de contenido
            content_patterns = re.findall(r'(Tutorial|Storytelling|Comparación|Challenge|Educativo)', self.strategies)
            trends['content_types'] = list(set(content_patterns))
        
        logger.info("📈 Extracted trends from strategy documentation")
        return trends
    
    def generate_fresh_concepts(self, 
                              num_concepts: int = 10,
                              focus_theme: str = None,
                              target_vertical: str = None,
                              min_success_probability: float = 0.7) -> List[MarketingConcept]:
        """
        Generar conceptos frescos de marketing inspirados en campañas exitosas
        """
        concepts = []
        
        # Seleccionar temas para generar conceptos
        if focus_theme and focus_theme in self.themes:
            selected_themes = [focus_theme]
        else:
            # Seleccionar temas con alta frecuencia y éxito
            theme_scores = {
                theme: theme_obj.frequency * theme_obj.success_rate 
                for theme, theme_obj in self.themes.items()
            }
            selected_themes = sorted(theme_scores.keys(), key=lambda x: theme_scores[x], reverse=True)[:5]
        
        for i in range(num_concepts):
            concept = self._generate_single_concept(
                selected_themes[i % len(selected_themes)],
                target_vertical,
                min_success_probability
            )
            concepts.append(concept)
        
        logger.info(f"🎨 Generated {len(concepts)} fresh marketing concepts")
        return concepts
    
    def _generate_single_concept(self, 
                               theme: str, 
                               target_vertical: str = None,
                               min_success_probability: float = 0.7) -> MarketingConcept:
        """Generar un concepto individual de marketing"""
        self.concept_counter += 1
        
        theme_obj = self.themes[theme]
        
        # Seleccionar tecnología basada en patrones de éxito
        technology = self._select_technology(theme_obj)
        
        # Seleccionar canal basado en tendencias
        channel = self._select_channel(theme_obj)
        
        # Seleccionar vertical
        if target_vertical:
            vertical = target_vertical
        else:
            vertical = random.choice(theme_obj.related_verticals) if theme_obj.related_verticals else "Technology"
        
        # Generar nombre y descripción
        name = self._generate_concept_name(theme, technology, channel)
        description = self._generate_concept_description(theme, technology, channel, vertical)
        
        # Calcular probabilidad de éxito
        success_probability = self._calculate_success_probability(theme_obj, technology, channel, vertical)
        
        # Seleccionar campañas de inspiración
        inspiration_campaigns = self._select_inspiration_campaigns(theme, technology, channel)
        
        # Generar métricas esperadas
        expected_metrics = self._generate_expected_metrics(theme_obj, success_probability)
        
        # Generar presupuesto y timeline
        budget = self._generate_budget(technology, channel, vertical)
        timeline = self._generate_timeline(technology, channel)
        
        # Determinar complejidad y prioridad
        complexity = self._determine_complexity(technology, channel)
        priority = self._determine_priority(success_probability, complexity)
        
        # Generar tags
        tags = self._generate_tags(theme, technology, channel, vertical)
        
        concept = MarketingConcept(
            concept_id=f"CONCEPT_{self.concept_counter:04d}",
            name=name,
            description=description,
            category=theme,
            technology=technology,
            channel=channel,
            vertical=vertical,
            objective=self._select_objective(theme),
            inspiration_campaigns=inspiration_campaigns,
            success_probability=success_probability,
            complexity=complexity,
            priority=priority,
            estimated_budget=budget,
            timeline=timeline,
            expected_metrics=expected_metrics,
            tags=tags,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return concept
    
    def _select_technology(self, theme_obj: CampaignTheme) -> str:
        """Seleccionar tecnología basada en patrones de éxito"""
        # Combinar tecnologías del tema con tecnologías de alto éxito
        theme_technologies = theme_obj.related_technologies
        success_technologies = [tech for tech, _ in self.success_patterns['high_success_technologies'].most_common(10)]
        
        # Priorizar tecnologías que aparecen en ambos
        common_technologies = set(theme_technologies) & set(success_technologies)
        if common_technologies:
            return random.choice(list(common_technologies))
        
        # Si no hay coincidencias, usar tecnología del tema
        if theme_technologies:
            return random.choice(theme_technologies)
        
        # Fallback a tecnologías de alto éxito
        return random.choice(success_technologies) if success_technologies else "Machine Learning"
    
    def _select_channel(self, theme_obj: CampaignTheme) -> str:
        """Seleccionar canal basado en tendencias y éxito"""
        theme_channels = theme_obj.related_channels
        success_channels = [channel for channel, _ in self.success_patterns['high_success_channels'].most_common(10)]
        
        # Priorizar canales que aparecen en ambos
        common_channels = set(theme_channels) & set(success_channels)
        if common_channels:
            return random.choice(list(common_channels))
        
        if theme_channels:
            return random.choice(theme_channels)
        
        return random.choice(success_channels) if success_channels else "Redes Sociales"
    
    def _generate_concept_name(self, theme: str, technology: str, channel: str) -> str:
        """Generar nombre creativo para el concepto"""
        name_templates = [
            f"AI-Powered {theme} Strategy",
            f"Intelligent {technology} {theme} Initiative",
            f"Smart {theme} Optimization Program",
            f"Advanced {technology} {theme} Solution",
            f"Next-Gen {theme} with {technology}",
            f"Revolutionary {theme} {channel} Campaign",
            f"Ultimate {technology} {theme} System",
            f"Progressive {theme} Enhancement Program"
        ]
        
        return random.choice(name_templates)
    
    def _generate_concept_description(self, theme: str, technology: str, channel: str, vertical: str) -> str:
        """Generar descripción detallada del concepto"""
        descriptions = {
            "Personalización con IA": f"Implementa {technology} para crear experiencias ultra-personalizadas en {channel}, adaptando cada interacción según el comportamiento único del usuario en {vertical}.",
            "Análisis Predictivo": f"Aplica {technology} para predecir tendencias futuras y comportamientos del consumidor en {channel}, permitiendo decisiones estratégicas proactivas en {vertical}.",
            "Chatbots y Asistentes Virtuales": f"Desarrolla asistentes inteligentes con {technology} para {channel} que proporcionan soporte 24/7 y guían a los usuarios en {vertical}.",
            "Generación de Contenido": f"Utiliza {technology} para generar automáticamente contenido personalizado y relevante para {channel} en {vertical}, incluyendo textos, imágenes y videos.",
            "Optimización de Conversión": f"Aplica {technology} para optimizar continuamente la tasa de conversión en {channel} mediante testing automático y ajustes en tiempo real en {vertical}."
        }
        
        if theme in descriptions:
            return descriptions[theme]
        
        return f"Implementa {technology} para optimizar {theme} en {channel}, proporcionando soluciones innovadoras para {vertical}."
    
    def _calculate_success_probability(self, theme_obj: CampaignTheme, technology: str, channel: str, vertical: str) -> float:
        """Calcular probabilidad de éxito del concepto"""
        base_probability = theme_obj.success_rate
        
        # Ajustar por tecnología
        tech_success = self.success_patterns['high_success_technologies'].get(technology, 0)
        tech_adjustment = min(0.1, tech_success / 10)
        
        # Ajustar por canal
        channel_success = self.success_patterns['high_success_channels'].get(channel, 0)
        channel_adjustment = min(0.1, channel_success / 10)
        
        # Ajustar por vertical
        vertical_success = self.success_patterns['high_success_verticals'].get(vertical, 0)
        vertical_adjustment = min(0.1, vertical_success / 10)
        
        final_probability = base_probability + tech_adjustment + channel_adjustment + vertical_adjustment
        return min(0.98, max(0.1, final_probability))
    
    def _select_inspiration_campaigns(self, theme: str, technology: str, channel: str) -> List[int]:
        """Seleccionar campañas de inspiración"""
        inspiration = []
        
        # Buscar campañas con tema similar
        for campaign in self.campaigns:
            if (campaign.get('category') == theme or 
                campaign.get('technology') == technology or 
                campaign.get('channel') == channel):
                if campaign.get('success_probability', 0) > 0.8:
                    inspiration.append(campaign['id'])
                    if len(inspiration) >= 3:
                        break
        
        return inspiration
    
    def _generate_expected_metrics(self, theme_obj: CampaignTheme, success_probability: float) -> Dict[str, float]:
        """Generar métricas esperadas basadas en el tema y probabilidad de éxito"""
        base_metrics = theme_obj.avg_metrics
        success_multiplier = 1 + (success_probability - 0.5) * 0.5
        
        expected_metrics = {}
        for metric, base_value in base_metrics.items():
            expected_metrics[metric] = round(base_value * success_multiplier, 2)
        
        # Asegurar métricas mínimas
        default_metrics = {
            'conversion_rate': 5.0,
            'click_through_rate': 2.5,
            'engagement_rate': 4.0,
            'cost_per_acquisition': 50.0,
            'return_on_ad_spend': 3.0,
            'customer_lifetime_value': 200.0
        }
        
        for metric, default_value in default_metrics.items():
            if metric not in expected_metrics:
                expected_metrics[metric] = default_value * success_multiplier
        
        return expected_metrics
    
    def _generate_budget(self, technology: str, channel: str, vertical: str) -> Dict[str, Any]:
        """Generar presupuesto estimado"""
        # Presupuestos base por tecnología
        tech_budgets = {
            "Machine Learning": 25000,
            "Deep Learning": 45000,
            "NLP": 18000,
            "Generative AI": 32000,
            "Reinforcement Learning": 55000,
            "Computer Vision": 35000,
            "Neural Networks": 40000
        }
        
        base_amount = tech_budgets.get(technology, 30000)
        
        # Ajustar por canal
        channel_multipliers = {
            "Redes Sociales": 1.0,
            "Email Marketing": 0.8,
            "E-commerce": 1.2,
            "Content Marketing": 0.9,
            "SEM/PPC": 1.5,
            "Mobile Apps": 1.3
        }
        
        multiplier = channel_multipliers.get(channel, 1.0)
        final_amount = int(base_amount * multiplier)
        
        # Determinar tier
        if final_amount < 20000:
            tier = "Intermedio"
        elif final_amount < 40000:
            tier = "Avanzado"
        else:
            tier = "Enterprise"
        
        return {
            "amount": final_amount,
            "tier": tier,
            "currency": "USD"
        }
    
    def _generate_timeline(self, technology: str, channel: str) -> Dict[str, Any]:
        """Generar timeline estimado"""
        # Duración base por tecnología
        tech_durations = {
            "Machine Learning": 8,
            "Deep Learning": 12,
            "NLP": 6,
            "Generative AI": 10,
            "Reinforcement Learning": 14,
            "Computer Vision": 10,
            "Neural Networks": 12
        }
        
        duration_weeks = tech_durations.get(technology, 8)
        
        # Ajustar por canal
        if channel in ["SEM/PPC", "Mobile Apps"]:
            duration_weeks += 2
        elif channel in ["Email Marketing", "Content Marketing"]:
            duration_weeks -= 2
        
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_weeks": duration_weeks
        }
    
    def _determine_complexity(self, technology: str, channel: str) -> str:
        """Determinar complejidad del concepto"""
        complex_technologies = ["Deep Learning", "Reinforcement Learning", "Neural Networks"]
        complex_channels = ["SEM/PPC", "Mobile Apps", "E-commerce"]
        
        if technology in complex_technologies or channel in complex_channels:
            return "Alta"
        elif technology in ["Machine Learning", "Generative AI", "Computer Vision"]:
            return "Media"
        else:
            return "Baja"
    
    def _determine_priority(self, success_probability: float, complexity: str) -> str:
        """Determinar prioridad del concepto"""
        if success_probability > 0.9:
            return "Crítica"
        elif success_probability > 0.8:
            return "Alta"
        elif success_probability > 0.7:
            return "Media"
        else:
            return "Baja"
    
    def _select_objective(self, theme: str) -> str:
        """Seleccionar objetivo basado en el tema"""
        objectives = {
            "Personalización con IA": "Aumentar conversiones",
            "Análisis Predictivo": "Mejorar engagement",
            "Chatbots y Asistentes Virtuales": "Generar leads",
            "Generación de Contenido": "Aumentar ventas",
            "Optimización de Conversión": "Mejorar retención"
        }
        
        return objectives.get(theme, "Aumentar conversiones")
    
    def _generate_tags(self, theme: str, technology: str, channel: str, vertical: str) -> List[str]:
        """Generar tags para el concepto"""
        tags = [theme, technology, channel, vertical]
        
        # Agregar tags adicionales basados en tendencias
        additional_tags = [
            "IA Avanzada", "Automatización", "Optimización", "Personalización",
            "Analytics", "Machine Learning", "Inteligencia Artificial"
        ]
        
        # Agregar 2-3 tags adicionales aleatorios
        tags.extend(random.sample(additional_tags, min(3, len(additional_tags))))
        
        return list(set(tags))  # Remover duplicados
    
    def analyze_document_insights(self, document_content: str) -> Dict[str, Any]:
        """
        Analizar documento y extraer insights accionables (comportamiento ClickUp Brain)
        """
        insights = {
            'key_themes': [],
            'actionable_suggestions': [],
            'trending_topics': [],
            'opportunities': [],
            'recommendations': []
        }
        
        # Extraer temas clave
        themes = re.findall(r'#+\s*(.+?)(?:\n|$)', document_content)
        insights['key_themes'] = [theme.strip() for theme in themes[:10]]
        
        # Extraer sugerencias accionables
        action_patterns = re.findall(r'(?:Implementa|Aplica|Desarrolla|Utiliza|Crea)\s+(.+?)(?:\.|$)', document_content)
        insights['actionable_suggestions'] = [action.strip() for action in action_patterns[:15]]
        
        # Extraer temas trending
        trend_patterns = re.findall(r'(?:Tendencia|Trending|Popular|Emergente).*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', document_content)
        insights['trending_topics'] = list(set(trend_patterns))[:10]
        
        # Generar oportunidades basadas en el contenido
        opportunities = self._generate_opportunities_from_content(document_content)
        insights['opportunities'] = opportunities
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations_from_content(document_content)
        insights['recommendations'] = recommendations
        
        logger.info(f"📋 Extracted insights from document: {len(insights['key_themes'])} themes, {len(insights['actionable_suggestions'])} suggestions")
        return insights
    
    def _generate_opportunities_from_content(self, content: str) -> List[str]:
        """Generar oportunidades basadas en el contenido del documento"""
        opportunities = []
        
        # Buscar palabras clave que indican oportunidades
        opportunity_keywords = ['oportunidad', 'potencial', 'crecimiento', 'expansión', 'nuevo', 'innovación']
        
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in opportunity_keywords):
                if len(sentence.strip()) > 20 and len(sentence.strip()) < 200:
                    opportunities.append(sentence.strip())
                    if len(opportunities) >= 5:
                        break
        
        return opportunities
    
    def _generate_recommendations_from_content(self, content: str) -> List[str]:
        """Generar recomendaciones basadas en el contenido del documento"""
        recommendations = []
        
        # Buscar patrones de recomendación
        rec_patterns = [
            r'Recomendamos\s+(.+?)(?:\.|$)',
            r'Es\s+recomendable\s+(.+?)(?:\.|$)',
            r'Se\s+sugiere\s+(.+?)(?:\.|$)',
            r'Lo\s+ideal\s+es\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            recommendations.extend([match.strip() for match in matches])
            if len(recommendations) >= 5:
                break
        
        return recommendations[:5]
    
    def generate_actionable_marketing_suggestions(self, 
                                                insights: Dict[str, Any],
                                                num_suggestions: int = 10) -> List[Dict[str, Any]]:
        """
        Generar sugerencias de marketing accionables basadas en insights
        """
        suggestions = []
        
        for i in range(num_suggestions):
            suggestion = {
                'id': f"SUGGESTION_{i+1:03d}",
                'title': self._generate_suggestion_title(insights),
                'description': self._generate_suggestion_description(insights),
                'action_type': self._select_action_type(),
                'priority': self._determine_suggestion_priority(),
                'estimated_impact': self._estimate_impact(),
                'implementation_time': self._estimate_implementation_time(),
                'required_resources': self._estimate_required_resources(),
                'success_metrics': self._define_success_metrics(),
                'related_themes': random.sample(insights.get('key_themes', []), min(3, len(insights.get('key_themes', [])))),
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            suggestions.append(suggestion)
        
        logger.info(f"💡 Generated {len(suggestions)} actionable marketing suggestions")
        return suggestions
    
    def _generate_suggestion_title(self, insights: Dict[str, Any]) -> str:
        """Generar título para sugerencia"""
        themes = insights.get('key_themes', ['Marketing'])
        theme = random.choice(themes) if themes else 'Marketing'
        
        titles = [
            f"Optimizar {theme} con IA",
            f"Implementar Estrategia de {theme}",
            f"Mejorar {theme} con Automatización",
            f"Desarrollar Campaña de {theme}",
            f"Escalar {theme} con Tecnología"
        ]
        
        return random.choice(titles)
    
    def _generate_suggestion_description(self, insights: Dict[str, Any]) -> str:
        """Generar descripción para sugerencia"""
        suggestions = insights.get('actionable_suggestions', [])
        if suggestions:
            base_suggestion = random.choice(suggestions)
            return f"Basado en el análisis del documento, se recomienda {base_suggestion.lower()}"
        
        return "Implementar estrategia de marketing basada en los insights extraídos del documento analizado."
    
    def _select_action_type(self) -> str:
        """Seleccionar tipo de acción"""
        action_types = [
            "Implementación", "Optimización", "Desarrollo", "Análisis", 
            "Estrategia", "Automatización", "Personalización", "Escalamiento"
        ]
        return random.choice(action_types)
    
    def _determine_suggestion_priority(self) -> str:
        """Determinar prioridad de la sugerencia"""
        priorities = ["Alta", "Media", "Baja"]
        weights = [0.4, 0.4, 0.2]  # Más probabilidad para Alta y Media
        return random.choices(priorities, weights=weights)[0]
    
    def _estimate_impact(self) -> str:
        """Estimar impacto de la sugerencia"""
        impacts = ["Alto", "Medio", "Bajo"]
        weights = [0.3, 0.5, 0.2]  # Más probabilidad para Medio
        return random.choices(impacts, weights=weights)[0]
    
    def _estimate_implementation_time(self) -> str:
        """Estimar tiempo de implementación"""
        times = ["1-2 semanas", "2-4 semanas", "1-2 meses", "2-3 meses"]
        weights = [0.3, 0.4, 0.2, 0.1]
        return random.choices(times, weights=weights)[0]
    
    def _estimate_required_resources(self) -> List[str]:
        """Estimar recursos requeridos"""
        resources = [
            "Equipo de Marketing", "Desarrollador", "Diseñador", 
            "Analista de Datos", "Especialista en IA", "Gestor de Proyecto"
        ]
        return random.sample(resources, random.randint(2, 4))
    
    def _define_success_metrics(self) -> List[str]:
        """Definir métricas de éxito"""
        metrics = [
            "Aumento en conversiones", "Mejora en engagement", 
            "Reducción de costos", "Incremento en ventas",
            "Mejor ROI", "Mayor alcance", "Mejor retención"
        ]
        return random.sample(metrics, random.randint(2, 3))
    
    def export_concepts_to_json(self, concepts: List[MarketingConcept], filename: str = None) -> str:
        """Exportar conceptos a archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_marketing_concepts_{timestamp}.json"
        
        # Convertir conceptos a diccionarios
        concepts_data = []
        for concept in concepts:
            concept_dict = {
                'id': concept.concept_id,
                'name': concept.name,
                'description': concept.description,
                'category': concept.category,
                'technology': concept.technology,
                'channel': concept.channel,
                'vertical': concept.vertical,
                'objective': concept.objective,
                'inspiration_campaigns': concept.inspiration_campaigns,
                'success_probability': concept.success_probability,
                'complexity': concept.complexity,
                'priority': concept.priority,
                'budget': concept.estimated_budget,
                'timeline': concept.timeline,
                'metrics': concept.expected_metrics,
                'tags': concept.tags,
                'created_at': concept.created_at
            }
            concepts_data.append(concept_dict)
        
        # Guardar archivo
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(concepts_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Exported {len(concepts)} concepts to {filename}")
        return filename
    
    def export_suggestions_to_json(self, suggestions: List[Dict], filename: str = None) -> str:
        """Exportar sugerencias a archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"actionable_marketing_suggestions_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Exported {len(suggestions)} suggestions to {filename}")
        return filename
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Obtener resumen del sistema"""
        return {
            'total_campaigns_analyzed': len(self.campaigns),
            'themes_extracted': len(self.themes),
            'high_success_campaigns': len([c for c in self.campaigns if c.get('success_probability', 0) > 0.8]),
            'concepts_generated': self.concept_counter,
            'top_themes': [theme for theme, _ in sorted(
                [(t, obj.frequency * obj.success_rate) for t, obj in self.themes.items()],
                key=lambda x: x[1], reverse=True
            )[:5]],
            'top_technologies': [tech for tech, _ in self.success_patterns['high_success_technologies'].most_common(5)],
            'top_channels': [channel for channel, _ in self.success_patterns['high_success_channels'].most_common(5)],
            'system_status': 'Active and Ready'
        }


def main():
    """Función principal para demostrar el sistema"""
    print("🚀 ADVANCED MARKETING BRAIN SYSTEM")
    print("=" * 50)
    
    # Inicializar sistema
    brain = AdvancedMarketingBrain()
    
    # Mostrar resumen del sistema
    summary = brain.get_system_summary()
    print(f"\n📊 SISTEMA INICIALIZADO:")
    print(f"   • Campañas analizadas: {summary['total_campaigns_analyzed']}")
    print(f"   • Temas extraídos: {summary['themes_extracted']}")
    print(f"   • Campañas de alto éxito: {summary['high_success_campaigns']}")
    print(f"   • Estado del sistema: {summary['system_status']}")
    
    # Generar conceptos frescos
    print(f"\n🎨 GENERANDO CONCEPTOS FRESCOS...")
    concepts = brain.generate_fresh_concepts(num_concepts=5)
    
    print(f"\n✨ CONCEPTOS GENERADOS:")
    for i, concept in enumerate(concepts, 1):
        print(f"\n{i}. {concept.name}")
        print(f"   📋 Categoría: {concept.category}")
        print(f"   🤖 Tecnología: {concept.technology}")
        print(f"   📱 Canal: {concept.channel}")
        print(f"   🎯 Vertical: {concept.vertical}")
        print(f"   📈 Probabilidad de éxito: {concept.success_probability:.1%}")
        print(f"   💰 Presupuesto estimado: ${concept.estimated_budget['amount']:,} ({concept.estimated_budget['tier']})")
        print(f"   ⏱️ Duración: {concept.timeline['duration_weeks']} semanas")
        print(f"   🏷️ Tags: {', '.join(concept.tags[:3])}...")
    
    # Analizar documento de estrategias
    if brain.strategies:
        print(f"\n📋 ANALIZANDO DOCUMENTO DE ESTRATEGIAS...")
        insights = brain.analyze_document_insights(brain.strategies)
        
        print(f"\n🔍 INSIGHTS EXTRAÍDOS:")
        print(f"   • Temas clave: {len(insights['key_themes'])}")
        print(f"   • Sugerencias accionables: {len(insights['actionable_suggestions'])}")
        print(f"   • Oportunidades: {len(insights['opportunities'])}")
        print(f"   • Recomendaciones: {len(insights['recommendations'])}")
        
        # Generar sugerencias accionables
        print(f"\n💡 GENERANDO SUGERENCIAS ACCIONABLES...")
        suggestions = brain.generate_actionable_marketing_suggestions(insights, num_suggestions=5)
        
        print(f"\n🎯 SUGERENCIAS GENERADAS:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion['title']}")
            print(f"   📝 Descripción: {suggestion['description']}")
            print(f"   🎯 Tipo: {suggestion['action_type']}")
            print(f"   ⚡ Prioridad: {suggestion['priority']}")
            print(f"   📊 Impacto: {suggestion['estimated_impact']}")
            print(f"   ⏱️ Tiempo: {suggestion['implementation_time']}")
            print(f"   👥 Recursos: {', '.join(suggestion['required_resources'])}")
    
    # Exportar resultados
    print(f"\n💾 EXPORTANDO RESULTADOS...")
    concepts_file = brain.export_concepts_to_json(concepts)
    if brain.strategies:
        suggestions_file = brain.export_suggestions_to_json(suggestions)
        print(f"   • Conceptos exportados a: {concepts_file}")
        print(f"   • Sugerencias exportadas a: {suggestions_file}")
    else:
        print(f"   • Conceptos exportados a: {concepts_file}")
    
    print(f"\n✅ SISTEMA COMPLETADO EXITOSAMENTE")
    print(f"🎉 El Advanced Marketing Brain System ha generado conceptos frescos")
    print(f"   inspirados en campañas exitosas y sugerencias accionables basadas")
    print(f"   en el análisis de documentos, similar al comportamiento de ClickUp Brain.")


if __name__ == "__main__":
    main()









