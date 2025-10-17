"""
Sistema de Plantillas Inteligentes para Respuestas en Redes Sociales
Versión Ultra Avanzada con Machine Learning y Personalización Automática
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd

logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    ENGAGEMENT = "engagement"
    SUPPORT = "support"
    SALES = "sales"
    CRISIS = "crisis"
    INFORMATION = "information"
    THANK_YOU = "thank_you"
    FOLLOW_UP = "follow_up"

class TemplateLanguage(Enum):
    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    FRENCH = "fr"

@dataclass
class TemplateVariable:
    """Variable de plantilla con validación y sugerencias"""
    name: str
    type: str  # text, number, date, url, email, phone
    required: bool = True
    default_value: str = ""
    validation_pattern: str = ""
    suggestions: List[str] = None
    description: str = ""

@dataclass
class ResponseTemplate:
    """Plantilla de respuesta ultra avanzada"""
    template_id: str
    name: str
    category: TemplateCategory
    language: TemplateLanguage
    content: str
    variables: List[TemplateVariable]
    sentiment_target: str
    intent_target: str
    urgency_level: str
    confidence_threshold: float
    usage_count: int = 0
    success_rate: float = 0.0
    engagement_score: float = 0.0
    conversion_rate: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    is_active: bool = True
    tags: List[str] = None
    brand_voice: Dict[str, Any] = None
    a_b_test_variants: List[str] = None

class AdvancedTemplateEngine:
    """Motor de plantillas ultra avanzado"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        self.templates: Dict[str, ResponseTemplate] = {}
        self.template_vectors = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.similarity_cache = {}
        
        # Métricas de rendimiento
        self.performance_metrics = {}
        self.learning_data = []
        
        # Cargar plantillas existentes
        self._load_templates()
        self._build_similarity_index()
    
    def create_template(self, 
                       name: str,
                       category: TemplateCategory,
                       language: TemplateLanguage,
                       content: str,
                       variables: List[TemplateVariable],
                       sentiment_target: str = "neutral",
                       intent_target: str = "general",
                       urgency_level: str = "medium",
                       confidence_threshold: float = 0.5,
                       tags: List[str] = None,
                       brand_voice: Dict[str, Any] = None) -> ResponseTemplate:
        """Crear nueva plantilla con validación avanzada"""
        
        template_id = self._generate_template_id(name, category)
        
        # Validar contenido de la plantilla
        self._validate_template_content(content, variables)
        
        # Optimizar plantilla con IA
        optimized_content = self._optimize_template_content(content, variables, brand_voice)
        
        template = ResponseTemplate(
            template_id=template_id,
            name=name,
            category=category,
            language=language,
            content=optimized_content,
            variables=variables,
            sentiment_target=sentiment_target,
            intent_target=intent_target,
            urgency_level=urgency_level,
            confidence_threshold=confidence_threshold,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=tags or [],
            brand_voice=brand_voice or {}
        )
        
        # Guardar plantilla
        self._save_template(template)
        self.templates[template_id] = template
        
        # Reconstruir índice de similitud
        self._build_similarity_index()
        
        logger.info(f"Plantilla creada: {template_id}")
        return template
    
    def select_best_template(self, 
                           comment_analysis: Dict,
                           context: Dict = None) -> Tuple[ResponseTemplate, float]:
        """Seleccionar la mejor plantilla basada en análisis avanzado"""
        
        try:
            # Filtrar plantillas por criterios básicos
            candidate_templates = self._filter_candidate_templates(comment_analysis, context)
            
            if not candidate_templates:
                # Fallback a plantilla genérica
                return self._get_fallback_template(), 0.5
            
            # Calcular scores de compatibilidad
            template_scores = []
            for template in candidate_templates:
                score = self._calculate_template_score(template, comment_analysis, context)
                template_scores.append((template, score))
            
            # Ordenar por score y seleccionar el mejor
            template_scores.sort(key=lambda x: x[1], reverse=True)
            best_template, best_score = template_scores[0]
            
            # Actualizar métricas de uso
            self._update_template_usage(best_template.template_id)
            
            return best_template, best_score
            
        except Exception as e:
            logger.error(f"Error en selección de plantilla: {e}")
            return self._get_fallback_template(), 0.3
    
    def personalize_template(self, 
                           template: ResponseTemplate,
                           comment_analysis: Dict,
                           context: Dict = None) -> str:
        """Personalizar plantilla con datos específicos del comentario"""
        
        try:
            personalized_content = template.content
            
            # Reemplazar variables básicas
            personalized_content = self._replace_basic_variables(
                personalized_content, comment_analysis, context
            )
            
            # Aplicar personalización avanzada
            personalized_content = self._apply_advanced_personalization(
                personalized_content, comment_analysis, context
            )
            
            # Optimizar para la plataforma
            personalized_content = self._optimize_for_platform(
                personalized_content, context.get('platform', 'general')
            )
            
            # Aplicar voz de marca
            personalized_content = self._apply_brand_voice(
                personalized_content, template.brand_voice, context
            )
            
            # Validar resultado final
            self._validate_personalized_content(personalized_content, template)
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error en personalización: {e}")
            return template.content
    
    def optimize_template_performance(self, template_id: str) -> ResponseTemplate:
        """Optimizar plantilla basada en métricas de rendimiento"""
        
        if template_id not in self.templates:
            raise ValueError(f"Plantilla {template_id} no encontrada")
        
        template = self.templates[template_id]
        metrics = self.performance_metrics.get(template_id, {})
        
        # Analizar métricas de rendimiento
        if metrics.get('usage_count', 0) < 10:
            logger.warning(f"Plantilla {template_id} tiene pocos usos para optimización")
            return template
        
        # Generar variantes optimizadas
        optimized_variants = self._generate_optimized_variants(template, metrics)
        
        # Seleccionar la mejor variante
        best_variant = self._select_best_variant(optimized_variants, metrics)
        
        # Actualizar plantilla
        template.content = best_variant['content']
        template.updated_at = datetime.now()
        
        # Guardar cambios
        self._save_template(template)
        
        logger.info(f"Plantilla {template_id} optimizada")
        return template
    
    def create_ab_test(self, 
                      template_id: str,
                      variants: List[str],
                      test_duration_days: int = 7) -> str:
        """Crear test A/B para plantilla"""
        
        if template_id not in self.templates:
            raise ValueError(f"Plantilla {template_id} no encontrada")
        
        test_id = self._generate_test_id(template_id)
        
        # Crear variantes de test
        test_variants = []
        for i, variant_content in enumerate(variants):
            variant_id = f"{template_id}_variant_{i+1}"
            variant_template = ResponseTemplate(
                template_id=variant_id,
                name=f"{self.templates[template_id].name} - Variante {i+1}",
                category=self.templates[template_id].category,
                language=self.templates[template_id].language,
                content=variant_content,
                variables=self.templates[template_id].variables,
                sentiment_target=self.templates[template_id].sentiment_target,
                intent_target=self.templates[template_id].intent_target,
                urgency_level=self.templates[template_id].urgency_level,
                confidence_threshold=self.templates[template_id].confidence_threshold,
                created_at=datetime.now(),
                is_active=True,
                tags=self.templates[template_id].tags + [f"ab_test_{test_id}"]
            )
            
            self._save_template(variant_template)
            test_variants.append(variant_template)
        
        # Configurar test
        test_config = {
            'test_id': test_id,
            'original_template_id': template_id,
            'variants': [v.template_id for v in test_variants],
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=test_duration_days),
            'traffic_split': [1.0 / len(variants)] * len(variants),
            'status': 'active'
        }
        
        # Guardar configuración de test
        self._save_ab_test_config(test_config)
        
        logger.info(f"Test A/B creado: {test_id}")
        return test_id
    
    def get_template_analytics(self, template_id: str) -> Dict[str, Any]:
        """Obtener analytics detallados de plantilla"""
        
        if template_id not in self.templates:
            raise ValueError(f"Plantilla {template_id} no encontrada")
        
        template = self.templates[template_id]
        metrics = self.performance_metrics.get(template_id, {})
        
        # Calcular métricas avanzadas
        analytics = {
            'template_info': {
                'id': template.template_id,
                'name': template.name,
                'category': template.category.value,
                'language': template.language.value,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                'is_active': template.is_active
            },
            'performance_metrics': {
                'usage_count': metrics.get('usage_count', 0),
                'success_rate': metrics.get('success_rate', 0.0),
                'engagement_score': metrics.get('engagement_score', 0.0),
                'conversion_rate': metrics.get('conversion_rate', 0.0),
                'avg_response_time': metrics.get('avg_response_time', 0.0),
                'sentiment_improvement': metrics.get('sentiment_improvement', 0.0)
            },
            'usage_trends': self._get_usage_trends(template_id),
            'top_contexts': self._get_top_contexts(template_id),
            'performance_by_platform': self._get_performance_by_platform(template_id),
            'recommendations': self._get_optimization_recommendations(template_id, metrics)
        }
        
        return analytics
    
    def _load_templates(self):
        """Cargar plantillas desde archivos"""
        try:
            templates_file = self.templates_dir / "templates.json"
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                
                for template_data in templates_data:
                    template = self._dict_to_template(template_data)
                    self.templates[template.template_id] = template
                
                logger.info(f"Cargadas {len(self.templates)} plantillas")
        except Exception as e:
            logger.error(f"Error cargando plantillas: {e}")
    
    def _save_template(self, template: ResponseTemplate):
        """Guardar plantilla en archivo"""
        try:
            templates_file = self.templates_dir / "templates.json"
            
            # Cargar plantillas existentes
            templates_data = []
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
            
            # Actualizar o agregar plantilla
            template_dict = self._template_to_dict(template)
            existing_index = None
            for i, existing in enumerate(templates_data):
                if existing['template_id'] == template.template_id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                templates_data[existing_index] = template_dict
            else:
                templates_data.append(template_dict)
            
            # Guardar archivo
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Error guardando plantilla: {e}")
    
    def _build_similarity_index(self):
        """Construir índice de similitud para búsqueda rápida"""
        try:
            if not self.templates:
                return
            
            # Extraer textos de plantillas
            template_texts = []
            template_ids = []
            
            for template in self.templates.values():
                if template.is_active:
                    # Combinar contenido y metadatos para búsqueda
                    search_text = f"{template.content} {template.name} {' '.join(template.tags or [])}"
                    template_texts.append(search_text)
                    template_ids.append(template.template_id)
            
            if template_texts:
                # Vectorizar textos
                self.template_vectors = self.vectorizer.fit_transform(template_texts)
                self.template_ids = template_ids
                
                logger.info(f"Índice de similitud construido para {len(template_texts)} plantillas")
                
        except Exception as e:
            logger.error(f"Error construyendo índice de similitud: {e}")
    
    def _filter_candidate_templates(self, comment_analysis: Dict, context: Dict = None) -> List[ResponseTemplate]:
        """Filtrar plantillas candidatas basadas en criterios básicos"""
        
        candidates = []
        
        for template in self.templates.values():
            if not template.is_active:
                continue
            
            # Filtrar por sentimiento
            if (template.sentiment_target != "neutral" and 
                template.sentiment_target != comment_analysis.get('sentiment', 'neutral')):
                continue
            
            # Filtrar por intención
            if (template.intent_target != "general" and 
                template.intent_target != comment_analysis.get('intent', 'general')):
                continue
            
            # Filtrar por urgencia
            if (template.urgency_level != "medium" and 
                template.urgency_level != comment_analysis.get('urgency', 'medium')):
                continue
            
            # Filtrar por confianza mínima
            if (template.confidence_threshold > 
                comment_analysis.get('confidence', 0.5)):
                continue
            
            # Filtrar por idioma si está disponible
            if context and context.get('language'):
                if template.language.value != context['language']:
                    continue
            
            candidates.append(template)
        
        return candidates
    
    def _calculate_template_score(self, 
                                template: ResponseTemplate,
                                comment_analysis: Dict,
                                context: Dict = None) -> float:
        """Calcular score de compatibilidad de plantilla"""
        
        score = 0.0
        
        # Score base por rendimiento histórico
        score += template.success_rate * 0.3
        
        # Score por engagement histórico
        score += template.engagement_score * 0.2
        
        # Score por similitud semántica
        semantic_score = self._calculate_semantic_similarity(
            template, comment_analysis.get('content', '')
        )
        score += semantic_score * 0.2
        
        # Score por contexto específico
        context_score = self._calculate_context_score(template, context)
        score += context_score * 0.15
        
        # Score por personalización
        personalization_score = self._calculate_personalization_potential(
            template, comment_analysis
        )
        score += personalization_score * 0.15
        
        return min(score, 1.0)
    
    def _calculate_semantic_similarity(self, template: ResponseTemplate, comment_content: str) -> float:
        """Calcular similitud semántica entre plantilla y comentario"""
        
        try:
            if self.template_vectors is None:
                return 0.5
            
            # Vectorizar comentario
            comment_vector = self.vectorizer.transform([comment_content])
            
            # Encontrar índice de la plantilla
            template_index = None
            for i, template_id in enumerate(self.template_ids):
                if template_id == template.template_id:
                    template_index = i
                    break
            
            if template_index is None:
                return 0.5
            
            # Calcular similitud coseno
            template_vector = self.template_vectors[template_index]
            similarity = cosine_similarity(comment_vector, template_vector)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculando similitud semántica: {e}")
            return 0.5
    
    def _calculate_context_score(self, template: ResponseTemplate, context: Dict = None) -> float:
        """Calcular score basado en contexto"""
        
        if not context:
            return 0.5
        
        score = 0.5
        
        # Bonus por plataforma específica
        if context.get('platform') in template.tags:
            score += 0.2
        
        # Bonus por hora del día
        if context.get('is_business_hours') and 'business' in template.tags:
            score += 0.1
        
        # Bonus por tipo de usuario
        if context.get('user_type') == 'vip' and 'vip' in template.tags:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_personalization_potential(self, 
                                           template: ResponseTemplate,
                                           comment_analysis: Dict) -> float:
        """Calcular potencial de personalización"""
        
        # Contar variables disponibles
        variable_count = len(template.variables)
        
        # Contar datos disponibles del comentario
        available_data = 0
        if comment_analysis.get('entities'):
            available_data += len(comment_analysis['entities'])
        if comment_analysis.get('keywords'):
            available_data += len(comment_analysis['keywords'])
        if comment_analysis.get('author_info'):
            available_data += 1
        
        # Calcular ratio de personalización
        if variable_count == 0:
            return 0.5
        
        personalization_ratio = min(available_data / variable_count, 1.0)
        return personalization_ratio
    
    def _replace_basic_variables(self, 
                               content: str,
                               comment_analysis: Dict,
                               context: Dict = None) -> str:
        """Reemplazar variables básicas en la plantilla"""
        
        # Variables del comentario
        if comment_analysis.get('author'):
            content = content.replace('{author}', comment_analysis['author'])
        
        if comment_analysis.get('content'):
            content = content.replace('{comment_content}', comment_analysis['content'])
        
        # Variables de contexto
        if context:
            if context.get('company_name'):
                content = content.replace('{company_name}', context['company_name'])
            
            if context.get('platform'):
                content = content.replace('{platform}', context['platform'])
            
            if context.get('timestamp'):
                content = content.replace('{timestamp}', context['timestamp'])
        
        # Variables de fecha/hora
        now = datetime.now()
        content = content.replace('{current_date}', now.strftime('%Y-%m-%d'))
        content = content.replace('{current_time}', now.strftime('%H:%M'))
        
        return content
    
    def _apply_advanced_personalization(self, 
                                      content: str,
                                      comment_analysis: Dict,
                                      context: Dict = None) -> str:
        """Aplicar personalización avanzada"""
        
        # Personalización basada en entidades
        if comment_analysis.get('entities'):
            for entity in comment_analysis['entities']:
                if entity.get('type') == 'PERSON' and '{person_name}' in content:
                    content = content.replace('{person_name}', entity['text'])
                elif entity.get('type') == 'ORG' and '{organization}' in content:
                    content = content.replace('{organization}', entity['text'])
                elif entity.get('type') == 'PRODUCT' and '{product_name}' in content:
                    content = content.replace('{product_name}', entity['text'])
        
        # Personalización basada en keywords
        if comment_analysis.get('keywords') and '{relevant_topic}' in content:
            # Seleccionar keyword más relevante
            top_keyword = comment_analysis['keywords'][0] if comment_analysis['keywords'] else 'el tema'
            content = content.replace('{relevant_topic}', top_keyword)
        
        # Personalización basada en sentimiento
        sentiment = comment_analysis.get('sentiment', 'neutral')
        if sentiment == 'positive' and '{sentiment_response}' in content:
            content = content.replace('{sentiment_response}', '¡Nos alegra mucho saberlo!')
        elif sentiment == 'negative' and '{sentiment_response}' in content:
            content = content.replace('{sentiment_response}', 'Entendemos tu preocupación')
        else:
            content = content.replace('{sentiment_response}', 'Gracias por tu comentario')
        
        return content
    
    def _optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimizar contenido para plataforma específica"""
        
        if platform == 'twitter':
            # Limitar a 280 caracteres
            if len(content) > 280:
                content = content[:277] + "..."
        elif platform == 'instagram':
            # Añadir hashtags relevantes
            if len(content) < 200:
                content += " #servicio #atencion #calidad"
        elif platform == 'linkedin':
            # Hacer más profesional
            content = content.replace('¡', '').replace('!', '.')
        
        return content
    
    def _apply_brand_voice(self, 
                         content: str,
                         brand_voice: Dict[str, Any],
                         context: Dict = None) -> str:
        """Aplicar voz de marca"""
        
        if not brand_voice:
            return content
        
        # Aplicar tono
        tone = brand_voice.get('tone', 'professional')
        if tone == 'casual':
            content = content.replace('usted', 'tú').replace('Usted', 'Tú')
        elif tone == 'formal':
            content = content.replace('tú', 'usted').replace('Tú', 'Usted')
        
        # Aplicar palabras clave de marca
        if brand_voice.get('keywords'):
            for keyword in brand_voice['keywords']:
                if keyword.lower() not in content.lower():
                    content += f" {keyword}"
        
        return content
    
    def _validate_personalized_content(self, content: str, template: ResponseTemplate):
        """Validar contenido personalizado"""
        
        # Verificar que no queden variables sin reemplazar
        remaining_vars = re.findall(r'\{[^}]+\}', content)
        if remaining_vars:
            logger.warning(f"Variables sin reemplazar en plantilla {template.template_id}: {remaining_vars}")
        
        # Verificar longitud mínima
        if len(content.strip()) < 10:
            raise ValueError("Contenido personalizado demasiado corto")
        
        # Verificar caracteres especiales problemáticos
        if any(char in content for char in ['<', '>', '&']):
            logger.warning(f"Caracteres especiales detectados en plantilla {template.template_id}")
    
    def _generate_template_id(self, name: str, category: TemplateCategory) -> str:
        """Generar ID único para plantilla"""
        base_id = f"{category.value}_{name.lower().replace(' ', '_')}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_id}_{timestamp}"
    
    def _generate_test_id(self, template_id: str) -> str:
        """Generar ID único para test A/B"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ab_test_{template_id}_{timestamp}"
    
    def _get_fallback_template(self) -> ResponseTemplate:
        """Obtener plantilla de respaldo"""
        return ResponseTemplate(
            template_id="fallback",
            name="Plantilla Genérica",
            category=TemplateCategory.INFORMATION,
            language=TemplateLanguage.SPANISH,
            content="Gracias por tu comentario. Te responderemos pronto.",
            variables=[],
            sentiment_target="neutral",
            intent_target="general",
            urgency_level="low",
            confidence_threshold=0.0
        )
    
    def _template_to_dict(self, template: ResponseTemplate) -> Dict:
        """Convertir plantilla a diccionario"""
        return {
            'template_id': template.template_id,
            'name': template.name,
            'category': template.category.value,
            'language': template.language.value,
            'content': template.content,
            'variables': [asdict(var) for var in template.variables],
            'sentiment_target': template.sentiment_target,
            'intent_target': template.intent_target,
            'urgency_level': template.urgency_level,
            'confidence_threshold': template.confidence_threshold,
            'usage_count': template.usage_count,
            'success_rate': template.success_rate,
            'engagement_score': template.engagement_score,
            'conversion_rate': template.conversion_rate,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None,
            'is_active': template.is_active,
            'tags': template.tags or [],
            'brand_voice': template.brand_voice or {}
        }
    
    def _dict_to_template(self, data: Dict) -> ResponseTemplate:
        """Convertir diccionario a plantilla"""
        return ResponseTemplate(
            template_id=data['template_id'],
            name=data['name'],
            category=TemplateCategory(data['category']),
            language=TemplateLanguage(data['language']),
            content=data['content'],
            variables=[TemplateVariable(**var) for var in data.get('variables', [])],
            sentiment_target=data.get('sentiment_target', 'neutral'),
            intent_target=data.get('intent_target', 'general'),
            urgency_level=data.get('urgency_level', 'medium'),
            confidence_threshold=data.get('confidence_threshold', 0.5),
            usage_count=data.get('usage_count', 0),
            success_rate=data.get('success_rate', 0.0),
            engagement_score=data.get('engagement_score', 0.0),
            conversion_rate=data.get('conversion_rate', 0.0),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            is_active=data.get('is_active', True),
            tags=data.get('tags', []),
            brand_voice=data.get('brand_voice', {})
        )

# Plantillas predefinidas
PREDEFINED_TEMPLATES = [
    {
        'name': 'Respuesta Positiva Genérica',
        'category': TemplateCategory.ENGAGEMENT,
        'language': TemplateLanguage.SPANISH,
        'content': '¡Muchas gracias por tu comentario, {author}! {sentiment_response} Nos alegra saber que {relevant_topic} te ha resultado útil. {call_to_action}',
        'variables': [
            TemplateVariable('author', 'text', True, '', '', ['usuario', 'cliente'], 'Nombre del autor del comentario'),
            TemplateVariable('sentiment_response', 'text', False, '¡Nos alegra saberlo!', '', ['¡Nos alegra saberlo!', '¡Excelente!', '¡Fantástico!'], 'Respuesta al sentimiento'),
            TemplateVariable('relevant_topic', 'text', True, 'nuestro servicio', '', [], 'Tema relevante del comentario'),
            TemplateVariable('call_to_action', 'text', False, '¡Sigue compartiendo tu experiencia!', '', ['¡Sigue compartiendo!', '¡Gracias por la recomendación!'], 'Llamada a la acción')
        ],
        'sentiment_target': 'positive',
        'intent_target': 'compliment',
        'tags': ['engagement', 'positive', 'generic']
    },
    {
        'name': 'Respuesta a Queja',
        'category': TemplateCategory.SUPPORT,
        'language': TemplateLanguage.SPANISH,
        'content': 'Hola {author}, lamentamos mucho {specific_issue}. Entendemos tu preocupación y queremos ayudarte a resolverlo. {solution_offer} {contact_info}',
        'variables': [
            TemplateVariable('author', 'text', True, '', '', [], 'Nombre del autor'),
            TemplateVariable('specific_issue', 'text', True, 'la situación', '', [], 'Problema específico mencionado'),
            TemplateVariable('solution_offer', 'text', True, 'Te contactaremos directamente', '', ['Te contactaremos', 'Resolveremos esto', 'Te ayudaremos'], 'Oferta de solución'),
            TemplateVariable('contact_info', 'text', False, 'Puedes contactarnos en {company_email}', '', [], 'Información de contacto')
        ],
        'sentiment_target': 'negative',
        'intent_target': 'complaint',
        'urgency_level': 'high',
        'tags': ['support', 'complaint', 'urgent']
    },
    {
        'name': 'Respuesta a Pregunta',
        'category': TemplateCategory.INFORMATION,
        'language': TemplateLanguage.SPANISH,
        'content': 'Hola {author}, excelente pregunta sobre {topic}. {detailed_answer} {additional_resources}',
        'variables': [
            TemplateVariable('author', 'text', True, '', '', [], 'Nombre del autor'),
            TemplateVariable('topic', 'text', True, 'nuestro servicio', '', [], 'Tema de la pregunta'),
            TemplateVariable('detailed_answer', 'text', True, 'Te explicamos:', '', [], 'Respuesta detallada'),
            TemplateVariable('additional_resources', 'text', False, 'Para más información, visita nuestro sitio web', '', [], 'Recursos adicionales')
        ],
        'sentiment_target': 'neutral',
        'intent_target': 'question',
        'tags': ['information', 'question', 'helpful']
    }
]

# Función para inicializar plantillas predefinidas
def initialize_predefined_templates(engine: AdvancedTemplateEngine):
    """Inicializar plantillas predefinidas"""
    for template_data in PREDEFINED_TEMPLATES:
        try:
            engine.create_template(**template_data)
        except Exception as e:
            logger.error(f"Error creando plantilla predefinida {template_data['name']}: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar motor de plantillas
    engine = AdvancedTemplateEngine()
    
    # Inicializar plantillas predefinidas
    initialize_predefined_templates(engine)
    
    # Ejemplo de uso
    comment_analysis = {
        'content': '¡Me encanta este producto! ¿Tienen más colores disponibles?',
        'sentiment': 'positive',
        'intent': 'question',
        'author': 'María García',
        'confidence': 0.9,
        'entities': [{'text': 'producto', 'type': 'PRODUCT'}],
        'keywords': ['producto', 'colores', 'disponibles']
    }
    
    context = {
        'platform': 'instagram',
        'company_name': 'Mi Empresa',
        'language': 'es'
    }
    
    # Seleccionar mejor plantilla
    template, score = engine.select_best_template(comment_analysis, context)
    print(f"Plantilla seleccionada: {template.name} (score: {score:.2f})")
    
    # Personalizar plantilla
    personalized_response = engine.personalize_template(template, comment_analysis, context)
    print(f"Respuesta personalizada: {personalized_response}")
