#!/usr/bin/env python3
"""
🎨 MARKETING BRAIN CONTENT GENERATOR
Sistema Avanzado de Generación de Contenido con IA
Incluye generación automática de copy, hooks, hashtags y contenido multimedia
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import asyncio
import aiohttp
from collections import defaultdict, Counter
import re
import random
import string
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept
from marketing_brain_ai_enhancer import MarketingBrainAIEnhancer

logger = logging.getLogger(__name__)

@dataclass
class GeneratedContent:
    """Contenido generado por IA"""
    content_id: str
    content_type: str
    title: str
    content: str
    target_audience: str
    platform: str
    engagement_score: float
    virality_potential: float
    keywords: List[str]
    hashtags: List[str]
    call_to_action: str
    created_at: str
    ai_model_used: str
    generation_parameters: Dict[str, Any]

@dataclass
class ContentTemplate:
    """Template de contenido"""
    template_id: str
    template_name: str
    content_type: str
    structure: Dict[str, Any]
    variables: List[str]
    success_rate: float
    usage_count: int
    last_used: str

@dataclass
class ContentPerformance:
    """Rendimiento del contenido"""
    content_id: str
    views: int
    engagement: int
    shares: int
    conversions: int
    click_through_rate: float
    conversion_rate: float
    cost_per_acquisition: float
    return_on_ad_spend: float
    performance_score: float
    measurement_date: str

class MarketingBrainContentGenerator:
    """
    Sistema Avanzado de Generación de Contenido con IA
    Incluye generación automática de copy, hooks, hashtags y contenido multimedia
    """
    
    def __init__(self, brain_system: AdvancedMarketingBrain = None, 
                 ai_enhancer: MarketingBrainAIEnhancer = None):
        self.brain = brain_system or AdvancedMarketingBrain()
        self.ai_enhancer = ai_enhancer or MarketingBrainAIEnhancer(self.brain)
        
        # Templates de contenido
        self.content_templates = self._load_content_templates()
        
        # Base de datos de contenido generado
        self.generated_content = []
        self.content_performance = {}
        
        # Configuración de generación
        self.generation_config = self._load_generation_config()
        
        # Modelos de IA para generación
        self.generation_models = {
            'copy_generator': self._initialize_copy_generator(),
            'hook_generator': self._initialize_hook_generator(),
            'hashtag_generator': self._initialize_hashtag_generator(),
            'cta_generator': self._initialize_cta_generator()
        }
        
        # Métricas de generación
        self.generation_metrics = {
            'total_content_generated': 0,
            'high_performing_content': 0,
            'average_engagement_score': 0.0,
            'templates_used': 0,
            'ai_models_used': 0
        }
        
        # Cache de contenido
        self.content_cache = {}
        self.performance_cache = {}
        
        logger.info("🎨 Marketing Brain Content Generator initialized successfully")
    
    def _load_content_templates(self) -> Dict[str, ContentTemplate]:
        """Cargar templates de contenido"""
        templates = {}
        
        # Template para posts de redes sociales
        templates['social_media_post'] = ContentTemplate(
            template_id="social_media_post",
            template_name="Social Media Post Template",
            content_type="social_media",
            structure={
                'hook': '{hook}',
                'main_content': '{main_content}',
                'value_proposition': '{value_proposition}',
                'social_proof': '{social_proof}',
                'call_to_action': '{call_to_action}',
                'hashtags': '{hashtags}'
            },
            variables=['hook', 'main_content', 'value_proposition', 'social_proof', 'call_to_action', 'hashtags'],
            success_rate=0.75,
            usage_count=0,
            last_used=""
        )
        
        # Template para email marketing
        templates['email_campaign'] = ContentTemplate(
            template_id="email_campaign",
            template_name="Email Campaign Template",
            content_type="email",
            structure={
                'subject_line': '{subject_line}',
                'preheader': '{preheader}',
                'greeting': '{greeting}',
                'opening': '{opening}',
                'main_content': '{main_content}',
                'benefits': '{benefits}',
                'social_proof': '{social_proof}',
                'call_to_action': '{call_to_action}',
                'closing': '{closing}'
            },
            variables=['subject_line', 'preheader', 'greeting', 'opening', 'main_content', 'benefits', 'social_proof', 'call_to_action', 'closing'],
            success_rate=0.68,
            usage_count=0,
            last_used=""
        )
        
        # Template para anuncios SEM/PPC
        templates['sem_ad'] = ContentTemplate(
            template_id="sem_ad",
            template_name="SEM/PPC Ad Template",
            content_type="sem_ppc",
            structure={
                'headline_1': '{headline_1}',
                'headline_2': '{headline_2}',
                'headline_3': '{headline_3}',
                'description_1': '{description_1}',
                'description_2': '{description_2}',
                'call_to_action': '{call_to_action}',
                'keywords': '{keywords}'
            },
            variables=['headline_1', 'headline_2', 'headline_3', 'description_1', 'description_2', 'call_to_action', 'keywords'],
            success_rate=0.72,
            usage_count=0,
            last_used=""
        )
        
        # Template para contenido de blog
        templates['blog_post'] = ContentTemplate(
            template_id="blog_post",
            template_name="Blog Post Template",
            content_type="blog",
            structure={
                'title': '{title}',
                'meta_description': '{meta_description}',
                'introduction': '{introduction}',
                'main_sections': '{main_sections}',
                'conclusion': '{conclusion}',
                'call_to_action': '{call_to_action}',
                'tags': '{tags}'
            },
            variables=['title', 'meta_description', 'introduction', 'main_sections', 'conclusion', 'call_to_action', 'tags'],
            success_rate=0.65,
            usage_count=0,
            last_used=""
        )
        
        # Template para video scripts
        templates['video_script'] = ContentTemplate(
            template_id="video_script",
            template_name="Video Script Template",
            content_type="video",
            structure={
                'hook': '{hook}',
                'introduction': '{introduction}',
                'main_content': '{main_content}',
                'demonstration': '{demonstration}',
                'social_proof': '{social_proof}',
                'call_to_action': '{call_to_action}',
                'outro': '{outro}'
            },
            variables=['hook', 'introduction', 'main_content', 'demonstration', 'social_proof', 'call_to_action', 'outro'],
            success_rate=0.78,
            usage_count=0,
            last_used=""
        )
        
        logger.info(f"📋 Loaded {len(templates)} content templates")
        return templates
    
    def _load_generation_config(self) -> Dict[str, Any]:
        """Cargar configuración de generación"""
        return {
            'content_lengths': {
                'social_media': {'min': 50, 'max': 280},
                'email': {'min': 200, 'max': 800},
                'sem_ppc': {'min': 30, 'max': 90},
                'blog': {'min': 800, 'max': 2000},
                'video': {'min': 100, 'max': 500}
            },
            'engagement_optimization': {
                'hook_variations': 5,
                'cta_variations': 3,
                'hashtag_count': {'min': 3, 'max': 10},
                'keyword_density': 0.02
            },
            'platform_specific': {
                'instagram': {'max_hashtags': 30, 'max_caption_length': 2200},
                'twitter': {'max_hashtags': 2, 'max_tweet_length': 280},
                'facebook': {'max_hashtags': 5, 'max_post_length': 63206},
                'linkedin': {'max_hashtags': 5, 'max_post_length': 3000},
                'youtube': {'max_description_length': 5000, 'max_tags': 15}
            },
            'ai_generation': {
                'creativity_level': 0.7,
                'consistency_threshold': 0.8,
                'uniqueness_threshold': 0.6,
                'relevance_threshold': 0.75
            }
        }
    
    def _initialize_copy_generator(self) -> Dict[str, Any]:
        """Inicializar generador de copy"""
        return {
            'model_type': 'advanced_copy_generator',
            'templates': {
                'problem_solution': "¿Tienes {problem}? Descubre cómo {solution} puede transformar tu {outcome}",
                'benefit_focused': "Obtén {benefit} en solo {timeframe} con {product_service}",
                'social_proof': "Más de {number} {audience} ya han {achievement} con {product_service}",
                'urgency_scarcity': "Solo quedan {quantity} {product_service} disponibles. ¡{action} ahora!",
                'storytelling': "Cuando {persona} descubrió {product_service}, su {situation} cambió completamente"
            },
            'power_words': [
                'revolucionario', 'exclusivo', 'limitado', 'gratis', 'instantáneo',
                'comprobado', 'garantizado', 'secreto', 'poderoso', 'transformador',
                'innovador', 'avanzado', 'superior', 'eficiente', 'optimizado'
            ],
            'emotional_triggers': [
                'miedo', 'codicia', 'orgullo', 'envidia', 'ira', 'alegría',
                'sorpresa', 'tristeza', 'anticipación', 'confianza', 'sorpresa'
            ]
        }
    
    def _initialize_hook_generator(self) -> Dict[str, Any]:
        """Inicializar generador de hooks"""
        return {
            'model_type': 'hook_generator',
            'hook_types': {
                'question': [
                    "¿Sabías que {statistic}?",
                    "¿Qué pasaría si {scenario}?",
                    "¿Por qué {audience} está {action}?",
                    "¿Te has preguntado {question}?"
                ],
                'statement': [
                    "{number} {audience} ya han {achievement}",
                    "El {percentage}% de {audience} no sabe {fact}",
                    "Descubre el secreto que {persona} no quiere que sepas",
                    "La verdad sobre {topic} que {authority} no te cuenta"
                ],
                'story': [
                    "Cuando {persona} hizo {action}, todo cambió",
                    "La historia de cómo {persona} {achievement}",
                    "Hace {timeframe}, {persona} descubrió {secret}",
                    "El momento en que {persona} se dio cuenta de {realization}"
                ],
                'controversy': [
                    "Lo que {authority} no quiere que sepas sobre {topic}",
                    "La mentira más grande sobre {topic}",
                    "Por qué {common_belief} está completamente equivocado",
                    "El lado oscuro de {topic} que nadie habla"
                ],
                'urgency': [
                    "Solo por {timeframe}: {offer}",
                    "Últimas {quantity} disponibles",
                    "Antes de que {event}, {action}",
                    "No pierdas esta oportunidad única"
                ]
            },
            'hook_enhancers': [
                'números específicos', 'estadísticas impactantes', 'nombres de autoridad',
                'tiempos específicos', 'cantidades limitadas', 'resultados medibles'
            ]
        }
    
    def _initialize_hashtag_generator(self) -> Dict[str, Any]:
        """Inicializar generador de hashtags"""
        return {
            'model_type': 'hashtag_generator',
            'hashtag_categories': {
                'industry': ['#marketing', '#digital', '#tecnologia', '#innovacion', '#negocios'],
                'trending': ['#viral', '#tendencia', '#actualidad', '#breaking', '#hot'],
                'engagement': ['#comenta', '#comparte', '#like', '#follow', '#dm'],
                'niche': ['#startup', '#emprendimiento', '#fintech', '#ecommerce', '#saas'],
                'location': ['#mexico', '#latam', '#global', '#local', '#internacional'],
                'emotion': ['#inspiracion', '#motivacion', '#exito', '#cambio', '#futuro']
            },
            'hashtag_strategies': {
                'high_volume': 'hashtags con más de 1M posts',
                'medium_volume': 'hashtags con 100K-1M posts',
                'low_volume': 'hashtags con menos de 100K posts',
                'niche_specific': 'hashtags específicos del nicho',
                'branded': 'hashtags únicos de la marca'
            },
            'hashtag_optimization': {
                'mix_ratio': {'high': 0.2, 'medium': 0.3, 'low': 0.5},
                'max_hashtags': 30,
                'min_hashtags': 5,
                'brand_hashtags': 2
            }
        }
    
    def _initialize_cta_generator(self) -> Dict[str, Any]:
        """Inicializar generador de CTAs"""
        return {
            'model_type': 'cta_generator',
            'cta_types': {
                'action_oriented': [
                    'Descarga ahora', 'Regístrate gratis', 'Comienza hoy',
                    'Obtén acceso', 'Únete ahora', 'Activa tu cuenta'
                ],
                'benefit_focused': [
                    'Transforma tu negocio', 'Aumenta tus ventas',
                    'Optimiza tu marketing', 'Mejora tu ROI',
                    'Escala tu empresa', 'Domina tu industria'
                ],
                'urgency_driven': [
                    'No esperes más', 'Oferta limitada',
                    'Solo por tiempo limitado', 'Últimas horas',
                    'Antes de que se agote', 'No pierdas esta oportunidad'
                ],
                'social_proof': [
                    'Únete a miles de usuarios', 'Como otros 10,000+',
                    'Sé parte del cambio', 'Conviértete en un experto',
                    'Sigue el ejemplo de los líderes', 'Forma parte de la comunidad'
                ],
                'curiosity': [
                    'Descubre el secreto', 'Averigua cómo',
                    'Conoce la verdad', 'Explora las posibilidades',
                    'Desvela el misterio', 'Revela la estrategia'
                ]
            },
            'cta_enhancers': [
                'gratis', 'ahora', 'hoy', 'instantáneo', 'sin compromiso',
                'garantizado', 'comprobado', 'exclusivo', 'limitado'
            ]
        }
    
    def generate_content_for_concept(self, concept: MarketingConcept, 
                                   content_type: str, 
                                   platform: str = None,
                                   target_audience: str = None) -> GeneratedContent:
        """Generar contenido para un concepto específico"""
        logger.info(f"🎨 Generating {content_type} content for concept: {concept.name}")
        
        # Generar ID único
        content_id = self._generate_content_id(concept.concept_id, content_type)
        
        # Obtener template
        template = self._get_template_for_type(content_type)
        if not template:
            raise ValueError(f"No template found for content type: {content_type}")
        
        # Generar variables del contenido
        content_variables = self._generate_content_variables(concept, content_type, platform, target_audience)
        
        # Aplicar template
        generated_content = self._apply_template(template, content_variables)
        
        # Optimizar para plataforma
        if platform:
            generated_content = self._optimize_for_platform(generated_content, platform)
        
        # Calcular métricas de engagement
        engagement_score = self._calculate_engagement_score(generated_content, content_type)
        virality_potential = self._calculate_virality_potential(generated_content, content_type)
        
        # Crear objeto de contenido generado
        content = GeneratedContent(
            content_id=content_id,
            content_type=content_type,
            title=content_variables.get('title', concept.name),
            content=generated_content,
            target_audience=target_audience or concept.vertical,
            platform=platform or 'multi_platform',
            engagement_score=engagement_score,
            virality_potential=virality_potential,
            keywords=self._extract_keywords(generated_content),
            hashtags=self._generate_hashtags(concept, content_type, platform),
            call_to_action=content_variables.get('call_to_action', ''),
            created_at=datetime.now().isoformat(),
            ai_model_used='marketing_brain_content_generator',
            generation_parameters={
                'concept_id': concept.concept_id,
                'template_used': template.template_id,
                'platform': platform,
                'target_audience': target_audience,
                'generation_config': self.generation_config
            }
        )
        
        # Guardar contenido generado
        self.generated_content.append(content)
        self.generation_metrics['total_content_generated'] += 1
        
        # Actualizar template usage
        template.usage_count += 1
        template.last_used = datetime.now().isoformat()
        
        logger.info(f"✅ Generated content {content_id} with engagement score: {engagement_score:.2f}")
        return content
    
    def _generate_content_id(self, concept_id: str, content_type: str) -> str:
        """Generar ID único para el contenido"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_input = f"{concept_id}_{content_type}_{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"content_{content_type}_{timestamp}_{hash_suffix}"
    
    def _get_template_for_type(self, content_type: str) -> Optional[ContentTemplate]:
        """Obtener template para tipo de contenido"""
        template_mapping = {
            'social_media': 'social_media_post',
            'email': 'email_campaign',
            'sem_ppc': 'sem_ad',
            'blog': 'blog_post',
            'video': 'video_script'
        }
        
        template_key = template_mapping.get(content_type)
        if template_key and template_key in self.content_templates:
            return self.content_templates[template_key]
        
        return None
    
    def _generate_content_variables(self, concept: MarketingConcept, 
                                  content_type: str, 
                                  platform: str = None,
                                  target_audience: str = None) -> Dict[str, str]:
        """Generar variables para el contenido"""
        variables = {}
        
        # Variables básicas del concepto
        variables.update({
            'product_service': concept.name,
            'category': concept.category,
            'technology': concept.technology,
            'vertical': concept.vertical,
            'objective': concept.objective,
            'target_audience': target_audience or concept.vertical
        })
        
        # Generar hook
        variables['hook'] = self._generate_hook(concept, content_type)
        
        # Generar contenido principal
        variables['main_content'] = self._generate_main_content(concept, content_type)
        
        # Generar propuesta de valor
        variables['value_proposition'] = self._generate_value_proposition(concept)
        
        # Generar prueba social
        variables['social_proof'] = self._generate_social_proof(concept)
        
        # Generar call to action
        variables['call_to_action'] = self._generate_call_to_action(concept, content_type)
        
        # Variables específicas por tipo de contenido
        if content_type == 'email':
            variables.update(self._generate_email_variables(concept))
        elif content_type == 'sem_ppc':
            variables.update(self._generate_sem_variables(concept))
        elif content_type == 'blog':
            variables.update(self._generate_blog_variables(concept))
        elif content_type == 'video':
            variables.update(self._generate_video_variables(concept))
        
        return variables
    
    def _generate_hook(self, concept: MarketingConcept, content_type: str) -> str:
        """Generar hook atractivo"""
        hook_generator = self.generation_models['hook_generator']
        hook_types = hook_generator['hook_types']
        
        # Seleccionar tipo de hook basado en el concepto
        if concept.objective == 'Awareness':
            hook_type = 'question'
        elif concept.objective == 'Conversion':
            hook_type = 'urgency'
        elif concept.objective == 'Engagement':
            hook_type = 'story'
        else:
            hook_type = 'statement'
        
        # Obtener templates del tipo seleccionado
        templates = hook_types.get(hook_type, hook_types['statement'])
        
        # Seleccionar template aleatorio
        template = random.choice(templates)
        
        # Rellenar variables
        hook = template.format(
            statistic=f"el 85% de las empresas en {concept.vertical}",
            scenario=f"pudieras {concept.objective.lower()} tu {concept.vertical}",
            audience=concept.vertical,
            action="transformando",
            question=f"cómo {concept.technology} puede revolucionar tu {concept.vertical}",
            number="10,000+",
            achievement="transformado su negocio",
            percentage="90",
            fact=f"cómo {concept.technology} puede optimizar su {concept.vertical}",
            persona="los líderes de {concept.vertical}",
            topic=concept.technology,
            authority="los expertos",
            action="descubrir",
            timeframe="24 horas",
            offer=f"acceso exclusivo a {concept.name}",
            quantity="50",
            event="se agote la oferta",
            common_belief=f"que {concept.vertical} es complicado",
            realization=f"que {concept.technology} era la solución"
        )
        
        return hook
    
    def _generate_main_content(self, concept: MarketingConcept, content_type: str) -> str:
        """Generar contenido principal"""
        copy_generator = self.generation_models['copy_generator']
        templates = copy_generator['templates']
        
        # Seleccionar template basado en el objetivo
        if concept.objective == 'Awareness':
            template_key = 'problem_solution'
        elif concept.objective == 'Conversion':
            template_key = 'benefit_focused'
        elif concept.objective == 'Engagement':
            template_key = 'social_proof'
        else:
            template_key = 'benefit_focused'
        
        template = templates[template_key]
        
        # Rellenar variables
        content = template.format(
            problem=f"problemas de {concept.vertical}",
            solution=concept.name,
            outcome=concept.vertical,
            benefit=f"resultados excepcionales en {concept.vertical}",
            timeframe="30 días",
            product_service=concept.name,
            number="5,000+",
            audience=f"empresas de {concept.vertical}",
            achievement="revolucionado su estrategia",
            quantity="100",
            action="reserva tu lugar"
        )
        
        # Agregar detalles específicos
        content += f"\n\nCon {concept.technology}, {concept.name} ofrece una solución innovadora que combina lo mejor de la tecnología moderna con estrategias probadas para {concept.vertical}."
        
        return content
    
    def _generate_value_proposition(self, concept: MarketingConcept) -> str:
        """Generar propuesta de valor"""
        value_props = [
            f"Optimiza tu {concept.vertical} con tecnología de vanguardia",
            f"Incrementa tu ROI en {concept.vertical} hasta un 300%",
            f"Automatiza procesos complejos de {concept.vertical}",
            f"Escala tu {concept.vertical} sin límites",
            f"Transforma tu {concept.vertical} en 30 días"
        ]
        
        return random.choice(value_props)
    
    def _generate_social_proof(self, concept: MarketingConcept) -> str:
        """Generar prueba social"""
        social_proofs = [
            f"Únete a más de 10,000 empresas que ya usan {concept.technology}",
            f"Recomendado por el 95% de los expertos en {concept.vertical}",
            f"Calificado con 4.9/5 estrellas por usuarios de {concept.vertical}",
            f"Utilizado por las 500 empresas más exitosas de {concept.vertical}",
            f"Testimonial: 'Cambió completamente mi {concept.vertical}' - CEO, Empresa Fortune 500"
        ]
        
        return random.choice(social_proofs)
    
    def _generate_call_to_action(self, concept: MarketingConcept, content_type: str) -> str:
        """Generar call to action"""
        cta_generator = self.generation_models['cta_generator']
        cta_types = cta_generator['cta_types']
        
        # Seleccionar tipo de CTA basado en el objetivo
        if concept.objective == 'Awareness':
            cta_type = 'curiosity'
        elif concept.objective == 'Conversion':
            cta_type = 'action_oriented'
        elif concept.objective == 'Engagement':
            cta_type = 'social_proof'
        else:
            cta_type = 'benefit_focused'
        
        templates = cta_types.get(cta_type, cta_types['action_oriented'])
        template = random.choice(templates)
        
        # Rellenar variables
        cta = template.format(
            product_service=concept.name,
            audience=f"empresas de {concept.vertical}",
            action="descubre",
            benefit=f"resultados en {concept.vertical}",
            timeframe="hoy",
            number="10,000+"
        )
        
        return cta
    
    def _generate_email_variables(self, concept: MarketingConcept) -> Dict[str, str]:
        """Generar variables específicas para email"""
        return {
            'subject_line': f"🚀 Revoluciona tu {concept.vertical} con {concept.name}",
            'preheader': f"Descubre cómo {concept.technology} puede transformar tu negocio",
            'greeting': "Hola [Nombre],",
            'opening': f"¿Sabías que el 90% de las empresas en {concept.vertical} no están aprovechando todo su potencial?",
            'benefits': f"• Optimización automática de procesos\n• Incremento del ROI hasta 300%\n• Escalabilidad sin límites\n• Soporte 24/7",
            'closing': "Saludos cordiales,\nEl equipo de Marketing Brain"
        }
    
    def _generate_sem_variables(self, concept: MarketingConcept) -> Dict[str, str]:
        """Generar variables específicas para SEM/PPC"""
        return {
            'headline_1': f"{concept.name} - {concept.vertical}",
            'headline_2': f"Optimiza tu {concept.vertical}",
            'headline_3': f"Con {concept.technology}",
            'description_1': f"Revoluciona tu {concept.vertical} con tecnología avanzada. Resultados garantizados.",
            'description_2': f"Incrementa tu ROI hasta 300%. Únete a 10,000+ empresas exitosas.",
            'keywords': f"{concept.vertical}, {concept.technology}, optimización, ROI, automatización"
        }
    
    def _generate_blog_variables(self, concept: MarketingConcept) -> Dict[str, str]:
        """Generar variables específicas para blog"""
        return {
            'title': f"Cómo {concept.name} está Revolucionando {concept.vertical} en 2024",
            'meta_description': f"Descubre cómo {concept.technology} puede transformar tu {concept.vertical}. Guía completa con casos de éxito y estrategias probadas.",
            'introduction': f"En el mundo actual de {concept.vertical}, la tecnología juega un papel fundamental. {concept.name} representa una revolución en cómo las empresas abordan {concept.vertical}.",
            'main_sections': f"1. El estado actual de {concept.vertical}\n2. Cómo {concept.technology} cambia el juego\n3. Casos de éxito reales\n4. Implementación paso a paso\n5. Resultados esperados",
            'conclusion': f"{concept.name} no es solo una herramienta, es una transformación completa de tu {concept.vertical}. El futuro es ahora.",
            'tags': f"{concept.vertical}, {concept.technology}, optimización, estrategia, innovación"
        }
    
    def _generate_video_variables(self, concept: MarketingConcept) -> Dict[str, str]:
        """Generar variables específicas para video"""
        return {
            'introduction': f"Hola, soy [Tu Nombre] y hoy te voy a mostrar cómo {concept.name} está cambiando completamente {concept.vertical}.",
            'demonstration': f"Vamos a ver en acción cómo {concept.technology} puede optimizar tu {concept.vertical} en tiempo real.",
            'outro': f"Si este video te ayudó, dale like, suscríbete y comparte. Nos vemos en el próximo video sobre {concept.vertical}."
        }
    
    def _apply_template(self, template: ContentTemplate, variables: Dict[str, str]) -> str:
        """Aplicar template con variables"""
        content = ""
        
        for key, value in template.structure.items():
            if key in variables:
                content += f"{variables[key]}\n\n"
            else:
                content += f"{value}\n\n"
        
        return content.strip()
    
    def _optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimizar contenido para plataforma específica"""
        platform_config = self.generation_config['platform_specific'].get(platform, {})
        
        if not platform_config:
            return content
        
        # Optimizar longitud
        max_length = platform_config.get('max_post_length', len(content))
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # Optimizar hashtags
        max_hashtags = platform_config.get('max_hashtags', 10)
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > max_hashtags:
            # Mantener solo los primeros hashtags
            content = re.sub(r'#\w+', '', content)
            content += ' ' + ' '.join(hashtags[:max_hashtags])
        
        return content
    
    def _calculate_engagement_score(self, content: str, content_type: str) -> float:
        """Calcular score de engagement"""
        score = 0.5  # Base score
        
        # Bonificaciones por elementos de engagement
        if '?' in content:
            score += 0.1  # Preguntas
        if '!' in content:
            score += 0.05  # Exclamaciones
        if any(word in content.lower() for word in ['gratis', 'free', 'sin costo']):
            score += 0.1  # Palabras de valor
        if any(word in content.lower() for word in ['ahora', 'hoy', 'inmediato']):
            score += 0.08  # Urgencia
        if any(word in content.lower() for word in ['tú', 'tu', 'usted']):
            score += 0.05  # Personalización
        
        # Bonificaciones por hashtags
        hashtag_count = len(re.findall(r'#\w+', content))
        score += min(0.1, hashtag_count * 0.02)
        
        # Bonificaciones por longitud óptima
        length_config = self.generation_config['content_lengths'].get(content_type, {'min': 100, 'max': 500})
        content_length = len(content)
        if length_config['min'] <= content_length <= length_config['max']:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_virality_potential(self, content: str, content_type: str) -> float:
        """Calcular potencial de viralidad"""
        potential = 0.3  # Base potential
        
        # Elementos que aumentan viralidad
        viral_indicators = [
            'viral', 'tendencia', 'breaking', 'exclusivo', 'secreto',
            'revelación', 'sorprendente', 'increíble', 'imposible'
        ]
        
        for indicator in viral_indicators:
            if indicator in content.lower():
                potential += 0.1
        
        # Bonificaciones por emociones
        emotional_words = [
            'sorprendente', 'increíble', 'asombroso', 'revolucionario',
            'transformador', 'impactante', 'espectacular'
        ]
        
        for word in emotional_words:
            if word in content.lower():
                potential += 0.05
        
        # Bonificaciones por números específicos
        if re.search(r'\d+%', content):
            potential += 0.05
        if re.search(r'\d+[KMB]', content):
            potential += 0.05
        
        return min(1.0, potential)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extraer palabras clave del contenido"""
        # Palabras comunes a excluir
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
            'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con',
            'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más',
            'pero', 'sus', 'todo', 'esta', 'entre', 'cuando', 'muy',
            'sin', 'sobre', 'también', 'me', 'hasta', 'desde', 'está',
            'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez',
            'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene',
            'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese',
            'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te',
            'otros', 'aunque', 'esa', 'esos', 'estas', 'le', 'ha',
            'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando',
            'todo', 'esta', 'ser', 'son', 'con', 'su', 'para', 'al',
            'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus',
            'todo', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre'
        }
        
        # Extraer palabras
        words = re.findall(r'\b[a-zA-Záéíóúñü]+\b', content.lower())
        
        # Filtrar palabras comunes y palabras cortas
        keywords = [
            word for word in words 
            if word not in stop_words and len(word) > 3
        ]
        
        # Contar frecuencia
        word_counts = Counter(keywords)
        
        # Retornar las más frecuentes
        return [word for word, count in word_counts.most_common(10)]
    
    def _generate_hashtags(self, concept: MarketingConcept, content_type: str, platform: str = None) -> List[str]:
        """Generar hashtags optimizados"""
        hashtag_generator = self.generation_models['hashtag_generator']
        categories = hashtag_generator['hashtag_categories']
        
        hashtags = []
        
        # Hashtags de industria
        hashtags.extend(categories['industry'][:2])
        
        # Hashtags de nicho específico
        niche_hashtags = {
            'E-commerce': ['#ecommerce', '#online', '#ventas', '#tienda'],
            'Fintech': ['#fintech', '#finanzas', '#digital', '#innovacion'],
            'SaaS': ['#saas', '#software', '#cloud', '#tecnologia'],
            'Healthcare': ['#healthcare', '#salud', '#medicina', '#bienestar'],
            'Education': ['#educacion', '#aprendizaje', '#formacion', '#conocimiento']
        }
        
        if concept.vertical in niche_hashtags:
            hashtags.extend(niche_hashtags[concept.vertical][:2])
        
        # Hashtags de tecnología
        tech_hashtags = {
            'Machine Learning': ['#machinelearning', '#ai', '#datascience'],
            'Deep Learning': ['#deeplearning', '#neuralnetworks', '#ai'],
            'NLP': ['#nlp', '#languagemodel', '#textanalysis'],
            'Computer Vision': ['#computervision', '#imageprocessing', '#ai'],
            'Reinforcement Learning': ['#reinforcementlearning', '#rl', '#ai']
        }
        
        if concept.technology in tech_hashtags:
            hashtags.extend(tech_hashtags[concept.technology][:2])
        
        # Hashtags de engagement
        hashtags.extend(categories['engagement'][:2])
        
        # Hashtags de tendencia (aleatorios)
        trending_hashtags = categories['trending']
        hashtags.extend(random.sample(trending_hashtags, 2))
        
        # Optimizar para plataforma
        if platform:
            platform_config = self.generation_config['platform_specific'].get(platform, {})
            max_hashtags = platform_config.get('max_hashtags', 10)
            hashtags = hashtags[:max_hashtags]
        
        return hashtags
    
    def generate_content_campaign(self, concept: MarketingConcept, 
                                platforms: List[str] = None,
                                content_types: List[str] = None) -> List[GeneratedContent]:
        """Generar campaña completa de contenido"""
        logger.info(f"🎨 Generating content campaign for concept: {concept.name}")
        
        if not platforms:
            platforms = ['instagram', 'facebook', 'twitter', 'linkedin']
        
        if not content_types:
            content_types = ['social_media', 'email', 'sem_ppc']
        
        campaign_content = []
        
        for platform in platforms:
            for content_type in content_types:
                try:
                    content = self.generate_content_for_concept(
                        concept=concept,
                        content_type=content_type,
                        platform=platform,
                        target_audience=concept.vertical
                    )
                    campaign_content.append(content)
                    
                except Exception as e:
                    logger.error(f"Error generating {content_type} for {platform}: {e}")
                    continue
        
        logger.info(f"✅ Generated {len(campaign_content)} content pieces for campaign")
        return campaign_content
    
    def optimize_content_performance(self, content_id: str, 
                                   performance_data: ContentPerformance) -> GeneratedContent:
        """Optimizar contenido basado en rendimiento"""
        logger.info(f"🔧 Optimizing content performance for: {content_id}")
        
        # Encontrar contenido
        content = None
        for c in self.generated_content:
            if c.content_id == content_id:
                content = c
                break
        
        if not content:
            raise ValueError(f"Content not found: {content_id}")
        
        # Guardar datos de rendimiento
        self.content_performance[content_id] = performance_data
        
        # Analizar rendimiento
        performance_score = performance_data.performance_score
        
        if performance_score < 0.6:  # Contenido de bajo rendimiento
            # Generar versión optimizada
            optimized_content = self._create_optimized_version(content, performance_data)
            
            # Actualizar métricas
            if performance_score > 0.8:
                self.generation_metrics['high_performing_content'] += 1
            
            return optimized_content
        
        return content
    
    def _create_optimized_version(self, original_content: GeneratedContent, 
                                performance_data: ContentPerformance) -> GeneratedContent:
        """Crear versión optimizada del contenido"""
        # Crear nueva versión con mejoras
        optimized_content = GeneratedContent(
            content_id=f"{original_content.content_id}_optimized",
            content_type=original_content.content_type,
            title=original_content.title,
            content=self._optimize_content_text(original_content.content, performance_data),
            target_audience=original_content.target_audience,
            platform=original_content.platform,
            engagement_score=original_content.engagement_score,
            virality_potential=original_content.virality_potential,
            keywords=original_content.keywords,
            hashtags=self._optimize_hashtags(original_content.hashtags, performance_data),
            call_to_action=self._optimize_cta(original_content.call_to_action, performance_data),
            created_at=datetime.now().isoformat(),
            ai_model_used='marketing_brain_content_optimizer',
            generation_parameters={
                'original_content_id': original_content.content_id,
                'optimization_reason': 'performance_improvement',
                'original_performance_score': performance_data.performance_score
            }
        )
        
        return optimized_content
    
    def _optimize_content_text(self, content: str, performance_data: ContentPerformance) -> str:
        """Optimizar texto del contenido"""
        # Si el engagement es bajo, agregar más elementos de engagement
        if performance_data.engagement < 100:
            # Agregar pregunta al final
            if '?' not in content:
                content += "\n\n¿Qué opinas? ¡Comenta abajo!"
        
        # Si el CTR es bajo, mejorar el hook
        if performance_data.click_through_rate < 0.02:
            # Agregar urgencia
            if 'ahora' not in content.lower():
                content = f"🚨 {content}"
        
        return content
    
    def _optimize_hashtags(self, hashtags: List[str], performance_data: ContentPerformance) -> List[str]:
        """Optimizar hashtags"""
        # Si el engagement es bajo, agregar hashtags de engagement
        if performance_data.engagement < 100:
            engagement_hashtags = ['#comenta', '#comparte', '#like', '#follow']
            hashtags.extend(engagement_hashtags[:2])
        
        return hashtags[:10]  # Limitar a 10 hashtags
    
    def _optimize_cta(self, cta: str, performance_data: ContentPerformance) -> str:
        """Optimizar call to action"""
        # Si la conversión es baja, hacer CTA más directo
        if performance_data.conversion_rate < 0.05:
            if 'gratis' not in cta.lower():
                cta = f"{cta} ¡GRATIS!"
        
        return cta
    
    def get_content_analytics(self) -> Dict[str, Any]:
        """Obtener analytics de contenido generado"""
        if not self.generated_content:
            return {'message': 'No content generated yet'}
        
        # Analytics básicos
        total_content = len(self.generated_content)
        content_by_type = Counter([c.content_type for c in self.generated_content])
        content_by_platform = Counter([c.platform for c in self.generated_content])
        
        # Analytics de rendimiento
        avg_engagement = np.mean([c.engagement_score for c in self.generated_content])
        avg_virality = np.mean([c.virality_potential for c in self.generated_content])
        
        # Top performing content
        top_content = sorted(
            self.generated_content, 
            key=lambda x: x.engagement_score, 
            reverse=True
        )[:5]
        
        # Analytics de templates
        template_usage = {}
        for template in self.content_templates.values():
            template_usage[template.template_name] = template.usage_count
        
        return {
            'total_content_generated': total_content,
            'content_by_type': dict(content_by_type),
            'content_by_platform': dict(content_by_platform),
            'average_engagement_score': round(avg_engagement, 3),
            'average_virality_potential': round(avg_virality, 3),
            'top_performing_content': [
                {
                    'content_id': c.content_id,
                    'title': c.title,
                    'engagement_score': c.engagement_score,
                    'virality_potential': c.virality_potential,
                    'content_type': c.content_type,
                    'platform': c.platform
                }
                for c in top_content
            ],
            'template_usage': template_usage,
            'generation_metrics': self.generation_metrics,
            'performance_data_available': len(self.content_performance)
        }
    
    def export_content_library(self, export_dir: str = "content_library") -> Dict[str, str]:
        """Exportar biblioteca de contenido"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar contenido generado
        content_data = [asdict(content) for content in self.generated_content]
        content_path = Path(export_dir) / f"generated_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        exported_files['generated_content'] = str(content_path)
        
        # Exportar templates
        templates_data = {k: asdict(v) for k, v in self.content_templates.items()}
        templates_path = Path(export_dir) / f"content_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)
        exported_files['content_templates'] = str(templates_path)
        
        # Exportar analytics
        analytics = self.get_content_analytics()
        analytics_path = Path(export_dir) / f"content_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analytics_path, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)
        exported_files['content_analytics'] = str(analytics_path)
        
        logger.info(f"📦 Exported content library to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Content Generator"""
    print("🎨 MARKETING BRAIN CONTENT GENERATOR")
    print("=" * 50)
    
    # Inicializar sistemas
    brain = AdvancedMarketingBrain()
    ai_enhancer = MarketingBrainAIEnhancer(brain)
    content_generator = MarketingBrainContentGenerator(brain, ai_enhancer)
    
    # Generar conceptos de prueba
    print(f"\n🎨 GENERANDO CONCEPTOS DE PRUEBA...")
    test_concepts = brain.generate_fresh_concepts(num_concepts=2, min_success_probability=0.7)
    
    # Generar contenido para cada concepto
    print(f"\n📝 GENERANDO CONTENIDO...")
    all_generated_content = []
    
    for concept in test_concepts:
        print(f"\n   🎯 Concepto: {concept.name}")
        print(f"      • Categoría: {concept.category}")
        print(f"      • Tecnología: {concept.technology}")
        print(f"      • Vertical: {concept.vertical}")
        
        # Generar campaña de contenido
        campaign_content = content_generator.generate_content_campaign(
            concept=concept,
            platforms=['instagram', 'facebook', 'twitter'],
            content_types=['social_media', 'email']
        )
        
        all_generated_content.extend(campaign_content)
        
        print(f"      • Contenido generado: {len(campaign_content)} piezas")
        
        # Mostrar ejemplo de contenido
        if campaign_content:
            example_content = campaign_content[0]
            print(f"      • Ejemplo ({example_content.content_type}):")
            print(f"        Título: {example_content.title}")
            print(f"        Contenido: {example_content.content[:100]}...")
            print(f"        Engagement Score: {example_content.engagement_score:.2f}")
            print(f"        Hashtags: {', '.join(example_content.hashtags[:5])}")
    
    # Mostrar analytics
    print(f"\n📊 ANALYTICS DE CONTENIDO:")
    analytics = content_generator.get_content_analytics()
    
    print(f"   • Total de contenido generado: {analytics['total_content_generated']}")
    print(f"   • Score de engagement promedio: {analytics['average_engagement_score']:.3f}")
    print(f"   • Potencial de viralidad promedio: {analytics['average_virality_potential']:.3f}")
    
    print(f"\n   📈 Contenido por tipo:")
    for content_type, count in analytics['content_by_type'].items():
        print(f"      - {content_type}: {count}")
    
    print(f"\n   📱 Contenido por plataforma:")
    for platform, count in analytics['content_by_platform'].items():
        print(f"      - {platform}: {count}")
    
    # Mostrar top content
    print(f"\n   🏆 Top 3 contenido con mejor engagement:")
    for i, content in enumerate(analytics['top_performing_content'][:3], 1):
        print(f"      {i}. {content['title'][:50]}...")
        print(f"         Engagement: {content['engagement_score']:.3f} | Plataforma: {content['platform']}")
    
    # Exportar biblioteca de contenido
    print(f"\n💾 EXPORTANDO BIBLIOTECA DE CONTENIDO...")
    exported_files = content_generator.export_content_library()
    print(f"   • Archivos exportados: {len(exported_files)}")
    for file_type, path in exported_files.items():
        print(f"     - {file_type}: {Path(path).name}")
    
    print(f"\n✅ CONTENT GENERATOR COMPLETADO EXITOSAMENTE")
    print(f"🎉 Se ha generado contenido optimizado para múltiples plataformas")
    print(f"   y canales de marketing con IA avanzada.")


if __name__ == "__main__":
    main()







