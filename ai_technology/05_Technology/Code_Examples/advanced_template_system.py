"""
Sistema de Templates Ultra Avanzado para Respuestas en Redes Sociales
Versión Mejorada con Machine Learning y Personalización Inteligente
"""

import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import logging

logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    ENGAGEMENT = "engagement"
    SUPPORT = "support"
    SALES = "sales"
    CRISIS = "crisis"
    INFORMATION = "information"
    THANK_YOU = "thank_you"
    FOLLOW_UP = "follow_up"

class TemplateComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class TemplateVariable:
    """Variable de template con validación y sugerencias"""
    name: str
    type: str  # text, number, date, url, email, etc.
    required: bool
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None
    suggestions: List[str] = None
    description: str = ""

@dataclass
class AdvancedTemplate:
    """Template ultra avanzado con IA integrada"""
    template_id: str
    name: str
    category: TemplateCategory
    complexity: TemplateComplexity
    content: str
    variables: List[TemplateVariable]
    
    # Configuración de IA
    sentiment_target: str
    intent_target: str
    confidence_threshold: float
    personalization_level: int  # 1-5
    
    # Métricas de rendimiento
    usage_count: int = 0
    success_rate: float = 0.0
    engagement_score: float = 0.0
    conversion_rate: float = 0.0
    
    # Configuración avanzada
    max_length: int = 280
    min_length: int = 20
    emoji_usage: bool = True
    hashtag_usage: bool = True
    mention_usage: bool = True
    
    # Contexto y condiciones
    platform_restrictions: List[str] = None
    time_restrictions: Dict[str, Any] = None
    user_type_restrictions: List[str] = None
    
    # A/B Testing
    variants: List[str] = None
    current_variant: int = 0
    
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class TemplatePerformance:
    """Métricas de rendimiento de templates"""
    template_id: str
    total_uses: int
    successful_responses: int
    average_engagement: float
    average_response_time: float
    sentiment_improvement: float
    conversion_events: int
    last_updated: datetime

class AdvancedTemplateEngine:
    """Motor de templates ultra avanzado"""
    
    def __init__(self, openai_api_key: str):
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.templates = {}
        self.performance_data = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.template_vectors = None
        
        # Cargar templates predefinidos
        self._load_predefined_templates()
        
    def _load_predefined_templates(self):
        """Cargar templates predefinidos ultra avanzados"""
        
        # Template para comentarios positivos
        positive_template = AdvancedTemplate(
            template_id="positive_engagement_v2",
            name="Engagement Positivo Avanzado",
            category=TemplateCategory.ENGAGEMENT,
            complexity=TemplateComplexity.ADVANCED,
            content="""¡{greeting}! {personalization} Nos encanta saber que {specific_detail}. {value_add} {call_to_action} {hashtags}""",
            variables=[
                TemplateVariable("greeting", "text", True, "¡Hola!", None, ["¡Hola!", "¡Hola {username}!", "¡Buenos días!", "¡Buenas tardes!"], "Saludo personalizado"),
                TemplateVariable("personalization", "text", True, "Gracias por compartir tu experiencia", None, 
                               ["Gracias por compartir tu experiencia", "Es genial ver tu feedback", "Apreciamos mucho tu comentario"], "Personalización del mensaje"),
                TemplateVariable("specific_detail", "text", True, "te gusta nuestro producto", None, [], "Detalle específico del comentario"),
                TemplateVariable("value_add", "text", False, "", None, 
                               ["¿Sabías que también tenemos {related_product}?", "Te recomendamos echar un vistazo a {feature}"], "Valor adicional"),
                TemplateVariable("call_to_action", "text", False, "", None, 
                               ["¡Síguenos para más contenido!", "¡Comparte tu experiencia con otros!", "¡Visita nuestro perfil!"], "Llamada a la acción"),
                TemplateVariable("hashtags", "text", False, "", None, [], "Hashtags relevantes")
            ],
            sentiment_target="positive",
            intent_target="compliment",
            confidence_threshold=0.7,
            personalization_level=4,
            emoji_usage=True,
            hashtag_usage=True,
            platform_restrictions=["instagram", "facebook", "twitter"],
            variants=[
                "¡{greeting}! {personalization} Nos encanta saber que {specific_detail}. {value_add} {call_to_action} {hashtags}",
                "¡{greeting}! {personalization} {specific_detail} es exactamente lo que buscamos. {value_add} {call_to_action} {hashtags}",
                "¡{greeting}! {personalization} {specific_detail} nos motiva a seguir mejorando. {value_add} {call_to_action} {hashtags}"
            ]
        )
        
        # Template para comentarios negativos
        negative_template = AdvancedTemplate(
            template_id="crisis_management_v2",
            name="Gestión de Crisis Avanzada",
            category=TemplateCategory.CRISIS,
            complexity=TemplateComplexity.EXPERT,
            content="""{acknowledgment} {empathy} {solution_offer} {next_steps} {contact_info}""",
            variables=[
                TemplateVariable("acknowledgment", "text", True, "Entendemos tu preocupación", None, 
                               ["Entendemos tu preocupación", "Lamentamos mucho esta situación", "Agradecemos que nos hayas contactado"], "Reconocimiento del problema"),
                TemplateVariable("empathy", "text", True, "y sabemos lo frustrante que puede ser", None, 
                               ["y sabemos lo frustrante que puede ser", "y comprendemos tu frustración", "y valoramos tu paciencia"], "Empatía"),
                TemplateVariable("solution_offer", "text", True, "Vamos a resolver esto inmediatamente", None, 
                               ["Vamos a resolver esto inmediatamente", "Te ayudaremos a solucionarlo", "Trabajaremos contigo para solucionarlo"], "Oferta de solución"),
                TemplateVariable("next_steps", "text", True, "Por favor, envíanos un DM con más detalles", None, 
                               ["Por favor, envíanos un DM con más detalles", "Contáctanos por privado para más información", "Escríbenos para ayudarte mejor"], "Próximos pasos"),
                TemplateVariable("contact_info", "text", False, "", None, 
                               ["o llámanos al {phone}", "o escríbenos a {email}", "o visita {website}"], "Información de contacto")
            ],
            sentiment_target="negative",
            intent_target="complaint",
            confidence_threshold=0.6,
            personalization_level=5,
            emoji_usage=False,
            hashtag_usage=False,
            platform_restrictions=["facebook", "instagram", "twitter", "linkedin"],
            variants=[
                "{acknowledgment} {empathy} {solution_offer} {next_steps} {contact_info}",
                "{acknowledgment} {empathy} {solution_offer} {next_steps} {contact_info}",
                "{acknowledgment} {empathy} {solution_offer} {next_steps} {contact_info}"
            ]
        )
        
        # Template para preguntas
        question_template = AdvancedTemplate(
            template_id="information_response_v2",
            name="Respuesta Informativa Avanzada",
            category=TemplateCategory.INFORMATION,
            complexity=TemplateComplexity.ADVANCED,
            content="""{greeting} {answer} {additional_info} {resources} {follow_up}""",
            variables=[
                TemplateVariable("greeting", "text", True, "¡Excelente pregunta!", None, 
                               ["¡Excelente pregunta!", "¡Buena pregunta!", "¡Gracias por preguntar!"], "Saludo para pregunta"),
                TemplateVariable("answer", "text", True, "La respuesta es {specific_answer}", None, [], "Respuesta específica"),
                TemplateVariable("additional_info", "text", False, "", None, 
                               ["Además, {extra_info}", "También te puede interesar que {bonus_info}"], "Información adicional"),
                TemplateVariable("resources", "text", False, "", None, 
                               ["Puedes encontrar más información en {link}", "Te recomendamos leer {resource}"], "Recursos adicionales"),
                TemplateVariable("follow_up", "text", False, "", None, 
                               ["¿Te gustaría saber más sobre {related_topic}?", "¿Hay algo más en lo que te pueda ayudar?"], "Seguimiento")
            ],
            sentiment_target="neutral",
            intent_target="question",
            confidence_threshold=0.5,
            personalization_level=3,
            emoji_usage=True,
            hashtag_usage=True,
            platform_restrictions=["facebook", "instagram", "twitter", "linkedin"]
        )
        
        # Template para ventas
        sales_template = AdvancedTemplate(
            template_id="sales_conversion_v2",
            name="Conversión de Ventas Avanzada",
            category=TemplateCategory.SALES,
            complexity=TemplateComplexity.EXPERT,
            content="""{acknowledgment} {value_proposition} {urgency} {offer} {call_to_action}""",
            variables=[
                TemplateVariable("acknowledgment", "text", True, "¡Gracias por tu interés!", None, 
                               ["¡Gracias por tu interés!", "¡Perfecto timing!", "¡Excelente elección!"], "Reconocimiento del interés"),
                TemplateVariable("value_proposition", "text", True, "{product} es perfecto para {benefit}", None, [], "Propuesta de valor"),
                TemplateVariable("urgency", "text", False, "", None, 
                               ["Solo quedan {stock} unidades", "Oferta válida hasta {date}", "¡No te lo pierdas!"], "Urgencia"),
                TemplateVariable("offer", "text", False, "", None, 
                               ["Te ofrecemos {discount}% de descuento", "Incluye {bonus} gratis", "Envío gratis"], "Oferta especial"),
                TemplateVariable("call_to_action", "text", True, "¡Compra ahora!", None, 
                               ["¡Compra ahora!", "¡Reserva el tuyo!", "¡Contáctanos para más info!"], "Llamada a la acción")
            ],
            sentiment_target="positive",
            intent_target="purchase_inquiry",
            confidence_threshold=0.8,
            personalization_level=5,
            emoji_usage=True,
            hashtag_usage=True,
            platform_restrictions=["facebook", "instagram", "twitter"]
        )
        
        # Almacenar templates
        self.templates = {
            positive_template.template_id: positive_template,
            negative_template.template_id: negative_template,
            question_template.template_id: question_template,
            sales_template.template_id: sales_template
        }
        
        # Inicializar vectores para similitud
        self._initialize_template_vectors()
    
    def _initialize_template_vectors(self):
        """Inicializar vectores para búsqueda de similitud"""
        template_texts = []
        for template in self.templates.values():
            template_texts.append(f"{template.name} {template.content} {template.category.value}")
        
        if template_texts:
            self.template_vectors = self.vectorizer.fit_transform(template_texts)
    
    async def select_best_template(self, 
                                 comment_analysis: Dict,
                                 context: Dict = None) -> AdvancedTemplate:
        """Selección inteligente del mejor template"""
        try:
            # Filtrar templates por criterios básicos
            suitable_templates = self._filter_templates_by_criteria(comment_analysis, context)
            
            if not suitable_templates:
                # Fallback a template neutral
                suitable_templates = [t for t in self.templates.values() 
                                    if t.sentiment_target == "neutral"]
            
            # Calcular scores de compatibilidad
            template_scores = {}
            for template in suitable_templates:
                score = await self._calculate_template_score(template, comment_analysis, context)
                template_scores[template.template_id] = score
            
            # Seleccionar el mejor template
            best_template_id = max(template_scores, key=template_scores.get)
            best_template = self.templates[best_template_id]
            
            # Actualizar métricas de uso
            best_template.usage_count += 1
            
            return best_template
            
        except Exception as e:
            logger.error(f"Error en selección de template: {e}")
            # Template de emergencia
            return self._get_emergency_template()
    
    def _filter_templates_by_criteria(self, 
                                    comment_analysis: Dict,
                                    context: Dict = None) -> List[AdvancedTemplate]:
        """Filtrar templates por criterios básicos"""
        suitable_templates = []
        
        for template in self.templates.values():
            # Verificar sentimiento
            if template.sentiment_target != comment_analysis.get('sentiment', 'neutral'):
                continue
            
            # Verificar intención
            if template.intent_target != comment_analysis.get('intent', 'question'):
                continue
            
            # Verificar confianza
            if template.confidence_threshold > comment_analysis.get('sentiment_confidence', 0.5):
                continue
            
            # Verificar plataforma
            if context and context.get('platform'):
                if template.platform_restrictions and context['platform'] not in template.platform_restrictions:
                    continue
            
            # Verificar restricciones de tiempo
            if template.time_restrictions:
                if not self._check_time_restrictions(template.time_restrictions):
                    continue
            
            suitable_templates.append(template)
        
        return suitable_templates
    
    async def _calculate_template_score(self, 
                                      template: AdvancedTemplate,
                                      comment_analysis: Dict,
                                      context: Dict = None) -> float:
        """Calcular score de compatibilidad del template"""
        score = 0.0
        
        # Score base por rendimiento histórico
        score += template.success_rate * 0.3
        
        # Score por engagement histórico
        score += template.engagement_score * 0.2
        
        # Score por personalización
        score += (template.personalization_level / 5) * 0.2
        
        # Score por complejidad vs análisis
        complexity_score = self._calculate_complexity_match(template, comment_analysis)
        score += complexity_score * 0.15
        
        # Score por contexto
        context_score = self._calculate_context_match(template, context)
        score += context_score * 0.15
        
        return score
    
    def _calculate_complexity_match(self, 
                                  template: AdvancedTemplate,
                                  comment_analysis: Dict) -> float:
        """Calcular match de complejidad"""
        comment_complexity = self._assess_comment_complexity(comment_analysis)
        
        complexity_map = {
            TemplateComplexity.SIMPLE: 1,
            TemplateComplexity.MEDIUM: 2,
            TemplateComplexity.ADVANCED: 3,
            TemplateComplexity.EXPERT: 4
        }
        
        template_complexity = complexity_map[template.complexity]
        
        # Penalizar si hay mucha diferencia
        difference = abs(comment_complexity - template_complexity)
        return max(0, 1 - (difference / 4))
    
    def _assess_comment_complexity(self, comment_analysis: Dict) -> int:
        """Evaluar complejidad del comentario"""
        complexity = 1  # Base
        
        # Aumentar complejidad por factores
        if comment_analysis.get('toxicity_score', 0) > 0.5:
            complexity += 1
        
        if comment_analysis.get('intent') in ['complaint', 'support']:
            complexity += 1
        
        if len(comment_analysis.get('entities', [])) > 3:
            complexity += 1
        
        if comment_analysis.get('urgency') in ['high', 'critical']:
            complexity += 1
        
        return min(complexity, 4)
    
    def _calculate_context_match(self, 
                               template: AdvancedTemplate,
                               context: Dict = None) -> float:
        """Calcular match de contexto"""
        if not context:
            return 0.5
        
        score = 0.5  # Base
        
        # Verificar tipo de usuario
        if template.user_type_restrictions:
            user_type = context.get('user_type', '')
            if user_type in template.user_type_restrictions:
                score += 0.3
        
        # Verificar hora del día
        if template.time_restrictions:
            if self._check_time_restrictions(template.time_restrictions):
                score += 0.2
        
        return min(score, 1.0)
    
    def _check_time_restrictions(self, time_restrictions: Dict) -> bool:
        """Verificar restricciones de tiempo"""
        now = datetime.now()
        
        # Verificar día de la semana
        if 'weekdays_only' in time_restrictions and now.weekday() >= 5:
            return False
        
        # Verificar horario
        if 'business_hours_only' in time_restrictions:
            hour = now.hour
            if hour < 9 or hour > 17:
                return False
        
        return True
    
    async def generate_personalized_response(self, 
                                           template: AdvancedTemplate,
                                           comment_analysis: Dict,
                                           context: Dict = None) -> str:
        """Generar respuesta personalizada usando IA"""
        try:
            # Seleccionar variante del template
            selected_variant = self._select_template_variant(template)
            
            # Generar valores para variables
            variable_values = await self._generate_variable_values(
                template, comment_analysis, context
            )
            
            # Aplicar variables al template
            response = self._apply_variables_to_template(selected_variant, variable_values)
            
            # Optimizar respuesta
            optimized_response = await self._optimize_response(response, template, context)
            
            return optimized_response
            
        except Exception as e:
            logger.error(f"Error en generación de respuesta: {e}")
            return "Gracias por tu comentario. Te responderemos pronto."
    
    def _select_template_variant(self, template: AdvancedTemplate) -> str:
        """Seleccionar variante del template para A/B testing"""
        if not template.variants:
            return template.content
        
        # Rotar variantes o usar la actual
        variant_index = template.current_variant % len(template.variants)
        return template.variants[variant_index]
    
    async def _generate_variable_values(self, 
                                      template: AdvancedTemplate,
                                      comment_analysis: Dict,
                                      context: Dict = None) -> Dict[str, str]:
        """Generar valores para variables del template usando IA"""
        variable_values = {}
        
        for variable in template.variables:
            if variable.name in variable_values:
                continue
            
            # Generar valor usando IA
            value = await self._generate_variable_value(
                variable, comment_analysis, context
            )
            
            variable_values[variable.name] = value
        
        return variable_values
    
    async def _generate_variable_value(self, 
                                     variable: TemplateVariable,
                                     comment_analysis: Dict,
                                     context: Dict = None) -> str:
        """Generar valor específico para una variable"""
        try:
            # Si hay sugerencias, usar IA para seleccionar/adaptar
            if variable.suggestions:
                prompt = f"""
                Basándote en este comentario: "{comment_analysis.get('content', '')}"
                Y este contexto: {context or {}}
                
                Selecciona o adapta la mejor opción para la variable "{variable.name}":
                {variable.suggestions}
                
                Responde solo con el texto seleccionado/adaptado, sin explicaciones.
                """
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            
            # Si no hay sugerencias, usar valor por defecto
            return variable.default_value or ""
            
        except Exception as e:
            logger.error(f"Error generando variable {variable.name}: {e}")
            return variable.default_value or ""
    
    def _apply_variables_to_template(self, 
                                   template_content: str,
                                   variable_values: Dict[str, str]) -> str:
        """Aplicar variables al contenido del template"""
        response = template_content
        
        for variable_name, value in variable_values.items():
            placeholder = f"{{{variable_name}}}"
            response = response.replace(placeholder, value)
        
        return response
    
    async def _optimize_response(self, 
                               response: str,
                               template: AdvancedTemplate,
                               context: Dict = None) -> str:
        """Optimizar respuesta final"""
        try:
            # Verificar longitud
            if len(response) > template.max_length:
                response = response[:template.max_length-3] + "..."
            
            # Añadir emojis si está habilitado
            if template.emoji_usage:
                response = self._add_appropriate_emojis(response, template.sentiment_target)
            
            # Añadir hashtags si está habilitado
            if template.hashtag_usage and context:
                response = self._add_hashtags(response, context)
            
            # Verificar menciones
            if template.mention_usage and context:
                response = self._add_mentions(response, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error optimizando respuesta: {e}")
            return response
    
    def _add_appropriate_emojis(self, response: str, sentiment: str) -> str:
        """Añadir emojis apropiados"""
        emoji_map = {
            'positive': ['😊', '👍', '🎉', '✨', '💙'],
            'negative': ['😔', '💙', '🤝', '🙏'],
            'neutral': ['💭', '📝', '🔍', '💡', '📌']
        }
        
        if sentiment in emoji_map and not any(emoji in response for emoji in emoji_map[sentiment]):
            import random
            emoji = random.choice(emoji_map[sentiment])
            response += f" {emoji}"
        
        return response
    
    def _add_hashtags(self, response: str, context: Dict) -> str:
        """Añadir hashtags relevantes"""
        if len(response) < 200:  # Solo si hay espacio
            hashtags = context.get('suggested_hashtags', [])
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags[:2]])
                response += f" {hashtag_text}"
        
        return response
    
    def _add_mentions(self, response: str, context: Dict) -> str:
        """Añadir menciones apropiadas"""
        if context.get('should_mention_user'):
            username = context.get('username', '')
            if username and f"@{username}" not in response:
                response = f"@{username} {response}"
        
        return response
    
    def _get_emergency_template(self) -> AdvancedTemplate:
        """Template de emergencia"""
        return AdvancedTemplate(
            template_id="emergency",
            name="Template de Emergencia",
            category=TemplateCategory.INFORMATION,
            complexity=TemplateComplexity.SIMPLE,
            content="Gracias por tu comentario. Te responderemos pronto.",
            variables=[],
            sentiment_target="neutral",
            intent_target="question",
            confidence_threshold=0.0,
            personalization_level=1
        )
    
    async def update_template_performance(self, 
                                        template_id: str,
                                        success: bool,
                                        engagement_score: float,
                                        response_time: float):
        """Actualizar métricas de rendimiento del template"""
        if template_id not in self.templates:
            return
        
        template = self.templates[template_id]
        
        # Actualizar métricas
        if success:
            template.success_rate = (template.success_rate * template.usage_count + 1) / (template.usage_count + 1)
        
        template.engagement_score = (template.engagement_score * template.usage_count + engagement_score) / (template.usage_count + 1)
        
        # Actualizar timestamp
        template.updated_at = datetime.now()
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de templates"""
        total_templates = len(self.templates)
        total_uses = sum(t.usage_count for t in self.templates.values())
        avg_success_rate = sum(t.success_rate for t in self.templates.values()) / total_templates if total_templates > 0 else 0
        avg_engagement = sum(t.engagement_score for t in self.templates.values()) / total_templates if total_templates > 0 else 0
        
        return {
            'total_templates': total_templates,
            'total_uses': total_uses,
            'average_success_rate': avg_success_rate,
            'average_engagement': avg_engagement,
            'templates_by_category': self._get_templates_by_category(),
            'top_performing_templates': self._get_top_performing_templates()
        }
    
    def _get_templates_by_category(self) -> Dict[str, int]:
        """Obtener templates por categoría"""
        categories = {}
        for template in self.templates.values():
            category = template.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _get_top_performing_templates(self, limit: int = 5) -> List[Dict]:
        """Obtener templates con mejor rendimiento"""
        sorted_templates = sorted(
            self.templates.values(),
            key=lambda t: (t.success_rate + t.engagement_score) / 2,
            reverse=True
        )
        
        return [
            {
                'template_id': t.template_id,
                'name': t.name,
                'success_rate': t.success_rate,
                'engagement_score': t.engagement_score,
                'usage_count': t.usage_count
            }
            for t in sorted_templates[:limit]
        ]

# Ejemplo de uso
async def main():
    """Ejemplo de uso del sistema de templates"""
    
    engine = AdvancedTemplateEngine("your-openai-api-key")
    
    # Simular análisis de comentario
    comment_analysis = {
        'content': '¡Me encanta este producto! ¿Tienen más colores disponibles?',
        'sentiment': 'positive',
        'sentiment_confidence': 0.9,
        'intent': 'purchase_inquiry',
        'intent_confidence': 0.8,
        'toxicity_score': 0.0,
        'entities': [{'text': 'producto', 'type': 'PRODUCT'}],
        'urgency': 'low'
    }
    
    context = {
        'platform': 'instagram',
        'username': 'usuario123',
        'user_type': 'customer',
        'should_mention_user': True
    }
    
    # Seleccionar mejor template
    best_template = await engine.select_best_template(comment_analysis, context)
    print(f"Template seleccionado: {best_template.name}")
    
    # Generar respuesta personalizada
    response = await engine.generate_personalized_response(best_template, comment_analysis, context)
    print(f"Respuesta generada: {response}")
    
    # Obtener estadísticas
    stats = engine.get_template_statistics()
    print(f"Estadísticas: {stats}")

if __name__ == "__main__":
    asyncio.run(main())









