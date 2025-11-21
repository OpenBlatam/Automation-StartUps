#!/usr/bin/env python3
"""
Generador Avanzado de Posts para Redes Sociales
Basado en la estrategia de campaña de lanzamiento de producto

Genera posts personalizados para diferentes plataformas, audiencias y tipos de campaña
con integración completa con n8n workflows, optimización de engagement y análisis predictivo.
"""

import os
import sys
import json
import argparse
import logging
import re
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from collections import Counter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Intentar importar optimizador de engagement
try:
    from testimonial_engagement_optimizer import EngagementOptimizer, EngagementPrediction, ContentOptimization
    ENGAGEMENT_OPTIMIZER_AVAILABLE = True
except ImportError:
    ENGAGEMENT_OPTIMIZER_AVAILABLE = False
    logger.debug("Optimizador de engagement no disponible, usando funcionalidades básicas")

# Intentar importar analizador de sentimiento
try:
    from testimonial_advanced_features import SentimentAnalyzer
    SENTIMENT_ANALYZER_AVAILABLE = True
except ImportError:
    SENTIMENT_ANALYZER_AVAILABLE = False
    logger.debug("Analizador de sentimiento no disponible")


@dataclass
class PostAnalysis:
    """Análisis completo de un post generado"""
    engagement_score: float  # 0-100
    readability_score: float  # 0-100
    conversion_potential: float  # 0-100
    has_numbers: bool
    has_emojis: bool
    has_questions: bool
    has_cta: bool
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    recommendations: List[str]
    optimal_posting_times: List[str]
    sentiment_score: Optional[float] = None  # -1 a 1
    sentiment_label: Optional[str] = None  # positive, negative, neutral


@dataclass
class VariationComparison:
    """Comparación entre múltiples variaciones de un post"""
    best_engagement: Dict[str, Any]
    best_conversion: Dict[str, Any]
    best_readability: Dict[str, Any]
    recommendations: List[str]
    comparison_table: List[Dict[str, Any]]


@dataclass
class StoryContent:
    """Contenido generado para Stories"""
    slides: List[Dict[str, str]]  # Lista de slides con texto
    total_slides: int
    suggested_images: List[str]
    suggested_videos: List[str]
    interactive_elements: List[str]


@dataclass
class ContentFormat:
    """Formato de contenido para diferentes tipos de posts"""
    format_type: str  # feed, reel, carousel, story, video
    content: str
    suggested_duration: Optional[int] = None  # segundos
    suggested_aspect_ratio: Optional[str] = None
    captions: Optional[List[str]] = None
    suggested_music: Optional[str] = None


@dataclass
class KeywordAnalysis:
    """Análisis de keywords y SEO"""
    keywords: List[str]
    keyword_density: Dict[str, float]
    seo_score: float  # 0-100
    suggested_keywords: List[str]
    trending_keywords: List[str]


@dataclass
class MultiPlatformContent:
    """Contenido generado para múltiples plataformas"""
    platform_contents: Dict[str, Dict[str, Any]]
    cross_platform_consistency: float  # 0-100
    optimal_posting_schedule: Dict[str, str]
    recommendations: List[str]


@dataclass
class CompetitorAnalysis:
    """Análisis de competencia"""
    competitor_posts: List[Dict[str, Any]]
    common_themes: List[str]
    engagement_benchmarks: Dict[str, float]
    content_gaps: List[str]
    opportunities: List[str]
    recommended_strategy: str


@dataclass
class AIContentSuggestion:
    """Sugerencias de contenido generadas por IA"""
    suggested_hooks: List[str]
    suggested_ctas: List[str]
    content_variations: List[str]
    tone_suggestions: List[str]
    improvement_suggestions: List[str]


@dataclass
class TemplateCustomization:
    """Personalización de templates"""
    template_id: str
    custom_fields: Dict[str, Any]
    brand_voice: Dict[str, Any]
    style_guide: Dict[str, Any]
    custom_hashtags: List[str]


@dataclass
class TrendAnalysis:
    """Análisis de tendencias"""
    trending_topics: List[str]
    trending_hashtags: List[str]
    trending_keywords: List[str]
    engagement_trends: Dict[str, float]
    best_posting_times: Dict[str, List[str]]
    content_recommendations: List[str]


@dataclass
class PublishingResult:
    """Resultado de publicación en redes sociales"""
    success: bool
    post_id: Optional[str]
    platform: str
    published_at: Optional[str]
    url: Optional[str]
    error: Optional[str]
    metrics: Optional[Dict[str, Any]]


@dataclass
class PredictiveInsights:
    """Insights predictivos basados en datos"""
    predicted_engagement: float
    predicted_reach: int
    predicted_conversions: int
    confidence_score: float
    risk_factors: List[str]
    success_probability: float
    recommendations: List[str]


@dataclass
class ContentPerformance:
    """Rendimiento de contenido"""
    post_id: str
    platform: str
    impressions: int
    reach: int
    engagement: int
    engagement_rate: float
    clicks: int
    conversions: int
    revenue: float
    performance_score: float
    trends: Dict[str, Any]


@dataclass
class CreativeBrief:
    """Brief creativo para diseño"""
    campaign_objective: str
    target_audience: str
    key_message: str
    visual_style: Dict[str, Any]
    color_palette: List[str]
    typography: Dict[str, Any]
    image_requirements: List[str]
    video_requirements: List[str]
    brand_guidelines: Dict[str, Any]
    content_specs: Dict[str, Any]


@dataclass
class VisualAssetAnalysis:
    """Análisis de assets visuales"""
    asset_type: str  # image, video, graphic
    recommended_dimensions: Dict[str, int]
    color_suggestions: List[str]
    composition_tips: List[str]
    text_overlay_suggestions: List[str]
    style_recommendations: List[str]
    accessibility_score: float
    engagement_potential: float


@dataclass
class CollaborationInvite:
    """Invitación de colaboración"""
    post_id: str
    collaborators: List[str]
    permissions: Dict[str, bool]
    review_status: str
    comments: List[Dict[str, Any]]
    approval_required: bool


class Platform(Enum):
    """Plataformas de redes sociales soportadas"""
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    YOUTUBE = "youtube"


class PostType(Enum):
    """Tipos de posts según la estrategia de campaña"""
    TEASER = "teaser"  # Día 1: Generar expectativa
    DEMO = "demo"  # Día 2: Mostrar producto
    OFFER = "offer"  # Día 3: Oferta especial


class Tone(Enum):
    """Tonos de voz disponibles"""
    PROFESSIONAL = "profesional"
    FRIENDLY = "amigable"
    URGENT = "urgente"
    EMOTIONAL = "emocional"
    CASUAL = "casual"


class CampaignPostGenerator:
    """Generador de posts para campañas de lanzamiento"""
    
    # Templates base por tipo de post y plataforma
    TEMPLATES = {
        PostType.TEASER: {
            Platform.INSTAGRAM: {
                "variation_1": """¿Te has preguntado alguna vez por qué {problem} sigue siendo tan complicado?

Después de {years} años trabajando en esto, finalmente encontramos la solución.

En 48 horas te mostraremos cómo puedes:
✨ Eliminar {pain_point} de tu vida
🚀 Lograr {desired_result} en tiempo récord
💡 Unirte a los {number}+ que ya están transformando su {area}

¿Estás listo para el cambio? 👇
Comenta "SÍ" si quieres ser de los primeros en saberlo 🔔

P.D.: Los primeros 100 en comentar recibirán acceso exclusivo 🎁""",
                "variation_2": """🔮 En 48 horas, tu forma de {verb} cambiará para siempre.

Hemos estado trabajando en algo que:
✅ Resuelve {problem_1} en segundos
✅ Te ahorra {hours} horas cada semana
✅ Te da acceso a {unique_benefit}

¿Qué crees que será? 🤔
Comenta con un emoji lo que esperas:
🔥 = {option_a}
💡 = {option_b}
🚀 = {option_c}

Los más creativos recibirán un premio especial 🎁""",
                "variation_3": """⚡ ÚLTIMAS HORAS para unirte a la lista VIP ⚡

Solo {vip_limit} personas tendrán acceso anticipado a lo que viene.

¿Qué incluye ser VIP?
🎁 Acceso 48 horas antes que todos
💰 Descuento exclusivo del {discount}%
💬 Grupo privado con el equipo
✨ Contenido exclusivo y actualizaciones

¿Quieres ser uno de los {vip_limit}? 👇
Comenta "VIP" y te agregamos a la lista 🔔

(Activa las notificaciones para no perderte el anuncio)"""
            },
            Platform.LINKEDIN: {
                "variation_1": """After {years} years of working on this challenge, we've finally found the solution to {problem}.

In 48 hours, we'll show you how to:
• Eliminate {pain_point} from your workflow
• Achieve {desired_result} in record time
• Join {number}+ professionals already transforming their {area}

Are you ready for the change?

Comment "YES" if you want to be among the first to know.

P.S.: The first 100 to comment will receive exclusive early access.""",
            },
            Platform.TIKTOK: {
                "variation_1": """POV: You're about to discover something that will change how you {verb} forever 🔥

In 48 hours, we're revealing:
✨ How to eliminate {pain_point}
🚀 How to achieve {desired_result} faster
💡 How {number}+ people are already winning

Comment "YES" if you want early access! 👇"""
            }
        },
        PostType.DEMO: {
            Platform.INSTAGRAM: {
                "variation_1": """🎉 ¡El momento ha llegado! Te presentamos {product_name}

Hace {months} meses, {founder_name} estaba frustrado porque {specific_problem}.

Después de {iterations} iteraciones y feedback de {beta_testers} beta testers, finalmente está aquí.

Lo que puedes hacer HOY:

✨ {benefit_1_with_metric}
🚀 {benefit_2_with_result}
💡 {benefit_3_differentiator}

👉 Mira el video para verlo en acción 👆

Ya son {number}+ personas usando {product} para {result}.
¿Quieres ser el siguiente? 

🔗 Link en bio para probarlo GRATIS (sin tarjeta de crédito)

Pregunta lo que quieras abajo 👇 Te respondemos en menos de 5 minutos 💬""",
                "variation_2": """🚀 {product_name} - La solución que estabas buscando

✅ {benefit_1} - {metric_1}
✅ {benefit_2} - {metric_2}
✅ {benefit_3} - {metric_3}

¿Cómo funciona?
1. {step_1}
2. {step_2}
3. {step_3}
4. ¡Listo! Disfruta de {result}

👉 Demo completa en el video 👆

🎁 OFERTA ESPECIAL DE LANZAMIENTO:
• Prueba gratis por {trial_days} días
• Sin tarjeta de crédito requerida
• Cancelación en cualquier momento
• Soporte prioritario incluido

🔗 Link en bio para empezar ahora mismo

¿Tienes dudas? Escríbenos por DM o comenta abajo 💬""",
                "variation_3": """👥 Ya son {number}+ personas usando {product} para {result}

"{powerful_testimonial}" - {testimonial_name}, {testimonial_title}

¿Qué dicen nuestros usuarios?
⭐ "{testimonial_1}" - {name_1}
⭐ "{testimonial_2}" - {name_2}
⭐ "{testimonial_3}" - {name_3}

Lo que hace {product} diferente:
🎯 {differentiator_1}
🎯 {differentiator_2}
🎯 {differentiator_3}

👉 Mira cómo funciona en el video 👆

¿Quieres los mismos resultados?
🔗 Prueba gratis por {trial_days} días - Link en bio

P.D.: Los primeros 50 en registrarse hoy reciben {special_bonus} 🎁"""
            },
            Platform.LINKEDIN: {
                "variation_1": """We're excited to introduce {product_name} - a solution that addresses {specific_problem}.

After {iterations} iterations and feedback from {beta_testers} beta testers, here's what you can achieve:

• {benefit_1_with_metric}
• {benefit_2_with_result}
• {benefit_3_differentiator}

{number}+ professionals are already using {product} to {result}.

Try it free for {trial_days} days (no credit card required).

Link in comments to get started.

Questions? Comment below or send a DM.""",
            }
        },
        PostType.OFFER: {
            Platform.INSTAGRAM: {
                "variation_1": """⚡ ÚLTIMAS {hours} HORAS ⚡

🔥 OFERTA DE LANZAMIENTO - NO SE REPETIRÁ 🔥

Solo quedan {spots_left} cupos disponibles a este precio.

💰 Precio normal: ${regular_price}
🎯 Precio especial: ${discount_price} (Ahorra {discount_percent}%)

✨ Lo que incluye:
• {benefit_1}
• {benefit_2}
• {benefit_3}
• {special_bonus} (Valor: ${bonus_value})

⏰ Esta oferta termina el {end_date} a las {end_time} {timezone}
⏰ O cuando se agoten los {total_spots} cupos disponibles

👉 Ya son {purchased}+ personas que aprovecharon esta oferta
👉 Solo quedan {spots_left} cupos restantes

🔗 Link en bio para asegurar tu cupo AHORA MISMO

💬 ¿Tienes dudas? Escríbenos por DM - Respondemos en menos de 5 minutos

P.D.: Esta es la ÚNICA vez que verás este precio. Después volverá a precio normal.""",
                "variation_2": """💰 ¿Cuánto vale tu tiempo?

Si {product} te ahorra {hours_saved} horas por semana...

Eso son {hours_month} horas al mes = {hours_year} horas al año

A ${discount_price}, estás pagando menos de ${price_per_hour} por hora ahorrada.

🔥 OFERTA ESPECIAL DE LANZAMIENTO:
• Precio normal: ${regular_price}
• Precio especial: ${discount_price} (Ahorra {discount_percent}%)
• Bonus: {special_bonus} (Valor: ${bonus_value})

✨ Garantía de {guarantee_days} días o te devolvemos el 100% del dinero
✨ Sin riesgo - Prueba sin compromiso
✨ Soporte prioritario incluido

⏰ Oferta válida solo hasta {end_date} a las {end_time}

🔗 Link en bio para empezar ahora mismo

💬 ¿Preguntas? Comenta abajo o escríbenos por DM""",
                "variation_3": """👥 Ya son {number}+ personas usando {product} desde el lanzamiento

"{urgency_testimonial}" - {testimonial_name}

🔥 OFERTA DE LANZAMIENTO - SOLO POR 48 HORAS 🔥

💰 Precio normal: ${regular_price}
🎯 Precio especial: ${discount_price} (Ahorra {discount_percent}%)

✨ Incluye:
• {benefit_1}
• {benefit_2}
• {benefit_3}
• {special_bonus} exclusivo para los primeros {first_n}

⏰ Esta oferta termina el {end_date} a las {end_time}

👉 No te quedes fuera - Únete a los {number}+ que ya están transformando su {area}
👉 Link en bio para acceder ahora mismo 🔗

💬 ¿Tienes dudas? Escríbenos por DM

P.D.: Los que esperan siempre pagan más. Los que actúan ahora, ahorran."""
            },
            Platform.LINKEDIN: {
                "variation_1": """Launch Offer - Limited Time Only

Only {spots_left} spots remaining at this price.

Regular Price: ${regular_price}
Special Price: ${discount_price} (Save {discount_percent}%)

What's included:
• {benefit_1}
• {benefit_2}
• {benefit_3}
• {special_bonus} (Value: ${bonus_value})

This offer ends on {end_date} at {end_time} {timezone}, or when {total_spots} spots are filled.

{number}+ professionals have already taken advantage of this offer.

Link in comments to secure your spot.

Questions? Comment below or send a DM.""",
            }
        }
    }
    
    # Hashtags por plataforma y tipo de post
    HASHTAGS = {
        PostType.TEASER: {
            Platform.INSTAGRAM: [
                "#Innovación", "#Tech", "#Productividad", "#NuevoProducto", "#Lanzamiento",
                "#InnovaciónTecnológica", "#ProductividadDigital", "#TechTrends", "#StartupLife",
                "#DigitalTransformation", "#ComingSoon", "#StayTuned", "#Próximamente",
                "#NuevoLanzamiento", "#EsperaLoMejor"
            ],
            Platform.LINKEDIN: [
                "#Innovation", "#Technology", "#Productivity", "#NewProduct", "#Launch",
                "#DigitalTransformation", "#BusinessTools", "#SaaS", "#B2B"
            ],
            Platform.TIKTOK: [
                "#ComingSoon", "#NewProduct", "#TechTok", "#ProductivityHacks", "#Innovation"
            ]
        },
        PostType.DEMO: {
            Platform.INSTAGRAM: [
                "#Demo", "#Demostración", "#ProductoNuevo", "#Innovación", "#Productividad",
                "#Tech", "#HerramientasDigitales", "#Automatización", "#Eficiencia",
                "#NuevoLanzamiento", "#TechTrends", "#ProductividadDigital", "#InnovaciónTecnológica",
                "#DemoProducto", "#Beneficios", "#Solución", "#Herramienta", "#DigitalTools",
                "#SaaS", "#B2B", "#ProductivityHacks", "#TimeSaving", "#BusinessTools"
            ],
            Platform.LINKEDIN: [
                "#ProductDemo", "#NewProduct", "#Innovation", "#Productivity", "#Technology",
                "#BusinessTools", "#SaaS", "#B2B", "#DigitalTransformation"
            ]
        },
        PostType.OFFER: {
            Platform.INSTAGRAM: [
                "#OfertaLimitada", "#Descuento", "#Oportunidad", "#Lanzamiento", "#OfertaEspecial",
                "#NoTeLoPierdas", "#ÚltimaHora", "#Promoción", "#DescuentoEspecial", "#OfertaExclusiva",
                "#LanzamientoProducto", "#OfertaPorTiempoLimitado", "#AprovechaAhora", "#OfertaFlash",
                "#Urgente", "#ActúaAhora", "#OfertaÚnica", "#DescuentoLanzamiento", "#OfertaRelámpago",
                "#ÚltimaChance", "#NoTeLoPierdas", "#AprovechaYa"
            ],
            Platform.LINKEDIN: [
                "#LimitedOffer", "#LaunchOffer", "#SpecialDiscount", "#BusinessOpportunity",
                "#ProfessionalTools", "#B2B", "#SaaS"
            ]
        }
    }
    
    # CTAs por plataforma y tipo
    CTAS = {
        PostType.TEASER: {
            Platform.INSTAGRAM: [
                "Comenta 'SÍ' si quieres ser de los primeros 🔔",
                "Activa las notificaciones para no perderte el anuncio",
                "Comenta 'VIP' para acceso exclusivo 🎁"
            ],
            Platform.LINKEDIN: [
                "Comment 'YES' to be notified first",
                "Follow for updates on the launch"
            ]
        },
        PostType.DEMO: {
            Platform.INSTAGRAM: [
                "🔗 Link en bio para probarlo GRATIS",
                "💬 ¿Tienes dudas? Escríbenos por DM",
                "👉 Prueba gratis por {trial_days} días - Link en bio"
            ],
            Platform.LINKEDIN: [
                "Try it free - Link in comments",
                "Questions? Comment below or send a DM"
            ]
        },
        PostType.OFFER: {
            Platform.INSTAGRAM: [
                "🔗 Link en bio para asegurar tu cupo AHORA MISMO",
                "⏰ Oferta termina en {hours} horas - Actúa ya",
                "💬 Escríbenos por DM si tienes dudas"
            ],
            Platform.LINKEDIN: [
                "Link in comments to secure your spot",
                "Limited time offer - Act now"
            ]
        }
    }
    
    def __init__(self, enable_optimization: bool = True, historical_data: Optional[List[Dict]] = None):
        """
        Inicializar el generador
        
        Args:
            enable_optimization: Habilitar optimización de engagement
            historical_data: Datos históricos de posts para aprendizaje
        """
        self.platform_limits = {
            Platform.INSTAGRAM: {"max_length": 2200, "hashtags": 30, "optimal_length": 200},
            Platform.LINKEDIN: {"max_length": 3000, "hashtags": 5, "optimal_length": 300},
            Platform.TIKTOK: {"max_length": 2200, "hashtags": 10, "optimal_length": 150},
            Platform.FACEBOOK: {"max_length": 5000, "hashtags": 10, "optimal_length": 250},
            Platform.TWITTER: {"max_length": 280, "hashtags": 3, "optimal_length": 200},
            Platform.YOUTUBE: {"max_length": 5000, "hashtags": 10, "optimal_length": 300},
        }
        
        # Inicializar optimizador de engagement si está disponible
        self.enable_optimization = enable_optimization and ENGAGEMENT_OPTIMIZER_AVAILABLE
        self.engagement_optimizer = None
        
        if self.enable_optimization:
            try:
                self.engagement_optimizer = EngagementOptimizer(historical_data=historical_data)
                logger.info("Optimizador de engagement inicializado")
            except Exception as e:
                logger.warning(f"No se pudo inicializar optimizador de engagement: {e}")
                self.enable_optimization = False
        
        # Inicializar analizador de sentimiento
        self.sentiment_analyzer = None
        if SENTIMENT_ANALYZER_AVAILABLE:
            try:
                self.sentiment_analyzer = SentimentAnalyzer()
                logger.info("Analizador de sentimiento inicializado")
            except Exception as e:
                logger.warning(f"No se pudo inicializar analizador de sentimiento: {e}")
        
        # Horarios óptimos por plataforma
        self.optimal_times = {
            Platform.INSTAGRAM: ["09:00-11:00", "13:00-15:00", "18:00-20:00"],
            Platform.LINKEDIN: ["08:00-10:00", "12:00-14:00", "17:00-19:00"],
            Platform.TIKTOK: ["18:00-22:00", "06:00-09:00"],
            Platform.FACEBOOK: ["09:00-11:00", "13:00-15:00", "19:00-21:00"],
            Platform.TWITTER: ["08:00-10:00", "12:00-14:00", "17:00-19:00"],
        }
        
        # Cache de posts generados
        self.post_cache: Dict[str, Dict[str, Any]] = {}
        
        # Keywords trending (puede ser cargado desde archivo o API)
        self.trending_keywords = {
            "tech": ["IA", "automatización", "productividad", "innovación", "digital"],
            "business": ["emprendimiento", "startup", "negocios", "marketing", "ventas"],
            "general": ["lanzamiento", "nuevo", "exclusivo", "oferta", "descuento"]
        }
        
        # Templates personalizables
        self.custom_templates: Dict[str, Dict] = {}
        
        # Historial de posts generados (para aprendizaje)
        self.generation_history: List[Dict[str, Any]] = []
        
        # Configuración de APIs (opcional)
        self.api_configs: Dict[str, Dict[str, str]] = {}
        
        # Performance tracking
        self.performance_tracking: Dict[str, ContentPerformance] = {}
        
        # Predictive models cache
        self.predictive_cache: Dict[str, PredictiveInsights] = {}
    
    def generate_post(
        self,
        platform: str,
        post_type: str,
        product_name: str,
        target_audience: str,
        tone: str = "amigable",
        promotion_details: Optional[Dict] = None,
        custom_data: Optional[Dict] = None,
        variation: int = 1,
        include_hashtags: bool = True,
        include_cta: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un post personalizado para redes sociales
        
        Args:
            platform: Plataforma (instagram, linkedin, tiktok, etc.)
            post_type: Tipo de post (teaser, demo, offer)
            product_name: Nombre del producto/servicio
            target_audience: Audiencia objetivo
            tone: Tono de voz (profesional, amigable, urgente, etc.)
            promotion_details: Detalles de la promoción actual
            custom_data: Datos personalizados para rellenar templates
            variation: Variación del template (1, 2, o 3)
            include_hashtags: Incluir hashtags
            include_cta: Incluir call-to-action
        
        Returns:
            Dict con el post generado y metadata
        """
        try:
            # Validar y convertir enums
            platform_enum = Platform(platform.lower())
            post_type_enum = PostType(post_type.lower())
            
            # Obtener template
            template_key = f"variation_{variation}"
            if platform_enum not in self.TEMPLATES[post_type_enum]:
                # Usar template de Instagram como fallback
                platform_enum = Platform.INSTAGRAM
                logger.warning(f"Template no encontrado para {platform}, usando Instagram como fallback")
            
            if template_key not in self.TEMPLATES[post_type_enum][platform_enum]:
                template_key = "variation_1"
                logger.warning(f"Variación {variation} no encontrada, usando variación 1")
            
            template = self.TEMPLATES[post_type_enum][platform_enum][template_key]
            
            # Preparar datos para el template
            data = self._prepare_template_data(
                product_name=product_name,
                target_audience=target_audience,
                promotion_details=promotion_details or {},
                custom_data=custom_data or {}
            )
            
            # Aplicar template
            post_content = template.format(**data)
            
            # Agregar hashtags si se solicita
            hashtags_text = ""
            if include_hashtags:
                hashtags = self._get_hashtags(post_type_enum, platform_enum, custom_data)
                max_hashtags = self.platform_limits[platform_enum]["hashtags"]
                hashtags = hashtags[:max_hashtags]
                hashtags_text = "\n\n" + " ".join(hashtags)
            
            # Agregar CTA si se solicita
            cta_text = ""
            if include_cta:
                cta = self._get_cta(post_type_enum, platform_enum, data)
                if cta:
                    cta_text = "\n\n" + cta
            
            # Construir post completo
            full_post = post_content + hashtags_text + cta_text
            
            # Validar longitud
            max_length = self.platform_limits[platform_enum]["max_length"]
            if len(full_post) > max_length:
                logger.warning(f"Post excede longitud máxima ({len(full_post)} > {max_length})")
                # Truncar si es necesario (mantener hashtags y CTA)
                available_length = max_length - len(hashtags_text) - len(cta_text) - 10
                post_content = post_content[:available_length] + "..."
                full_post = post_content + hashtags_text + cta_text
            
            # Aplicar ajustes de tono
            full_post = self._apply_tone(full_post, tone)
            
            # Análisis y optimización del post
            analysis = self._analyze_post(full_post, platform_enum, post_type_enum, include_hashtags, include_cta)
            
            # Optimizar hashtags si está habilitado
            optimized_hashtags = hashtags if include_hashtags else []
            if self.enable_optimization and include_hashtags and self.engagement_optimizer:
                try:
                    optimization = self.engagement_optimizer.optimize_hashtags(
                        hashtags=hashtags,
                        platform=platform,
                        post_type=post_type,
                        content=post_content
                    )
                    if optimization and optimization.hashtag_suggestions:
                        # Combinar hashtags originales con optimizados (70% originales, 30% optimizados)
                        optimized_hashtags = hashtags[:int(len(hashtags) * 0.7)]
                        optimized_hashtags.extend(optimization.hashtag_suggestions[:int(len(hashtags) * 0.3)])
                        optimized_hashtags = list(dict.fromkeys(optimized_hashtags))[:max_hashtags]
                except Exception as e:
                    logger.warning(f"Error optimizando hashtags: {e}")
                    optimized_hashtags = hashtags
            
            # Reconstruir post con hashtags optimizados
            if include_hashtags and optimized_hashtags != hashtags:
                hashtags_text = "\n\n" + " ".join(optimized_hashtags)
                full_post = post_content + hashtags_text + cta_text
            
            # Predicción de engagement si está habilitado
            engagement_prediction = None
            if self.enable_optimization and self.engagement_optimizer:
                try:
                    has_numbers = bool(re.search(r'\d+%|\d+\s*(veces|meses|años|horas|días)', full_post))
                    has_emojis = bool(re.findall(r'[😀-🙏🌀-🗿]', full_post))
                    has_questions = bool(re.search(r'[¿?]', full_post))
                    
                    engagement_prediction = self.engagement_optimizer.predict_engagement(
                        post_content=post_content,
                        hashtags=optimized_hashtags if include_hashtags else [],
                        platform=platform,
                        has_cta=include_cta and bool(cta),
                        has_numbers=has_numbers,
                        has_emojis=has_emojis,
                        has_questions=has_questions
                    )
                except Exception as e:
                    logger.warning(f"Error prediciendo engagement: {e}")
            
            # Preparar resultado final
            result = {
                "post_content": post_content,
                "full_post": full_post,
                "hashtags": optimized_hashtags if include_hashtags else [],
                "call_to_action": cta if include_cta else None,
                "platform": platform,
                "post_type": post_type,
                "tone": tone,
                "length": len(full_post),
                "max_length": max_length,
                "metadata": {
                    "product_name": product_name,
                    "target_audience": target_audience,
                    "variation": variation,
                    "generated_at": datetime.now().isoformat(),
                    "promotion_details": promotion_details
                },
                "analysis": asdict(analysis) if analysis else None,
                "engagement_prediction": asdict(engagement_prediction) if engagement_prediction else None,
                "optimal_posting_times": self.optimal_times.get(platform_enum, [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando post: {str(e)}", exc_info=True)
            raise
    
    def _prepare_template_data(
        self,
        product_name: str,
        target_audience: str,
        promotion_details: Dict,
        custom_data: Dict
    ) -> Dict[str, Any]:
        """Prepara los datos para rellenar el template"""
        # Valores por defecto
        data = {
            "product_name": product_name,
            "product": product_name,
            "problem": custom_data.get("problem", "este problema"),
            "years": custom_data.get("years", "3"),
            "pain_point": custom_data.get("pain_point", "las complicaciones"),
            "desired_result": custom_data.get("desired_result", "tus objetivos"),
            "number": custom_data.get("number", "1000"),
            "area": custom_data.get("area", "trabajo"),
            "verb": custom_data.get("verb", "trabajar"),
            "problem_1": custom_data.get("problem_1", "problemas complejos"),
            "hours": custom_data.get("hours", "10"),
            "unique_benefit": custom_data.get("unique_benefit", "beneficios exclusivos"),
            "option_a": custom_data.get("option_a", "Opción A"),
            "option_b": custom_data.get("option_b", "Opción B"),
            "option_c": custom_data.get("option_c", "Opción C"),
            "vip_limit": custom_data.get("vip_limit", "500"),
            "discount": custom_data.get("discount", "20"),
            "founder_name": custom_data.get("founder_name", "nuestro equipo"),
            "specific_problem": custom_data.get("specific_problem", "un problema específico"),
            "months": custom_data.get("months", "6"),
            "iterations": custom_data.get("iterations", "50"),
            "beta_testers": custom_data.get("beta_testers", "100"),
            "benefit_1_with_metric": custom_data.get("benefit_1_with_metric", "Beneficio 1 con métrica"),
            "benefit_2_with_result": custom_data.get("benefit_2_with_result", "Beneficio 2 con resultado"),
            "benefit_3_differentiator": custom_data.get("benefit_3_differentiator", "Beneficio 3 diferenciador"),
            "result": custom_data.get("result", "mejorar su productividad"),
            "trial_days": custom_data.get("trial_days", "14"),
            "step_1": custom_data.get("step_1", "Paso 1"),
            "step_2": custom_data.get("step_2", "Paso 2"),
            "step_3": custom_data.get("step_3", "Paso 3"),
            "benefit_1": custom_data.get("benefit_1", "Beneficio 1"),
            "benefit_2": custom_data.get("benefit_2", "Beneficio 2"),
            "benefit_3": custom_data.get("benefit_3", "Beneficio 3"),
            "metric_1": custom_data.get("metric_1", "Métrica 1"),
            "metric_2": custom_data.get("metric_2", "Métrica 2"),
            "metric_3": custom_data.get("metric_3", "Métrica 3"),
            "powerful_testimonial": custom_data.get("powerful_testimonial", "Testimonial poderoso"),
            "testimonial_name": custom_data.get("testimonial_name", "Nombre"),
            "testimonial_title": custom_data.get("testimonial_title", "Título"),
            "testimonial_1": custom_data.get("testimonial_1", "Testimonial 1"),
            "testimonial_2": custom_data.get("testimonial_2", "Testimonial 2"),
            "testimonial_3": custom_data.get("testimonial_3", "Testimonial 3"),
            "name_1": custom_data.get("name_1", "Nombre 1"),
            "name_2": custom_data.get("name_2", "Nombre 2"),
            "name_3": custom_data.get("name_3", "Nombre 3"),
            "differentiator_1": custom_data.get("differentiator_1", "Diferenciador 1"),
            "differentiator_2": custom_data.get("differentiator_2", "Diferenciador 2"),
            "differentiator_3": custom_data.get("differentiator_3", "Diferenciador 3"),
            "special_bonus": custom_data.get("special_bonus", "Bonus especial"),
            "hours": custom_data.get("hours", "24"),
            "spots_left": custom_data.get("spots_left", "50"),
            "regular_price": custom_data.get("regular_price", promotion_details.get("regular_price", "99")),
            "discount_price": custom_data.get("discount_price", promotion_details.get("discount_price", "79")),
            "discount_percent": custom_data.get("discount_percent", promotion_details.get("discount_percent", "20")),
            "special_bonus": custom_data.get("special_bonus", promotion_details.get("special_bonus", "Bonus especial")),
            "bonus_value": custom_data.get("bonus_value", promotion_details.get("bonus_value", "29")),
            "end_date": custom_data.get("end_date", promotion_details.get("end_date", (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y"))),
            "end_time": custom_data.get("end_time", promotion_details.get("end_time", "23:59")),
            "timezone": custom_data.get("timezone", promotion_details.get("timezone", "GMT")),
            "total_spots": custom_data.get("total_spots", promotion_details.get("total_spots", "100")),
            "purchased": custom_data.get("purchased", promotion_details.get("purchased", "50")),
            "hours_saved": custom_data.get("hours_saved", "5"),
            "hours_month": custom_data.get("hours_month", "20"),
            "hours_year": custom_data.get("hours_year", "240"),
            "price_per_hour": custom_data.get("price_per_hour", "0.33"),
            "guarantee_days": custom_data.get("guarantee_days", "30"),
            "urgency_testimonial": custom_data.get("urgency_testimonial", "Testimonial de urgencia"),
            "first_n": custom_data.get("first_n", "50"),
        }
        
        return data
    
    def _get_hashtags(self, post_type: PostType, platform: Platform, custom_data: Dict) -> List[str]:
        """Obtiene hashtags apropiados para el post"""
        base_hashtags = self.HASHTAGS.get(post_type, {}).get(platform, [])
        
        # Agregar hashtags personalizados si se proporcionan
        custom_hashtags = custom_data.get("custom_hashtags", [])
        if custom_hashtags:
            base_hashtags.extend(custom_hashtags)
        
        # Agregar hashtag de industria si se proporciona
        industry = custom_data.get("industry")
        if industry:
            base_hashtags.append(f"#{industry}")
        
        return base_hashtags
    
    def _get_cta(self, post_type: PostType, platform: Platform, data: Dict) -> str:
        """Obtiene el CTA apropiado para el post"""
        ctas = self.CTAS.get(post_type, {}).get(platform, [])
        if not ctas:
            return ""
        
        # Seleccionar CTA aleatorio o el primero
        import random
        cta = random.choice(ctas)
        
        # Rellenar placeholders en el CTA
        try:
            cta = cta.format(**data)
        except KeyError:
            pass  # Si falta algún dato, usar CTA sin formatear
        
        return cta
    
    def _apply_tone(self, text: str, tone: str) -> str:
        """Aplica ajustes de tono al texto"""
        tone_lower = tone.lower()
        
        if tone_lower == "profesional":
            # Remover emojis excesivos, mantener solo algunos
            text = re.sub(r'([🎉🚀💡✨🎁💰⏰🔥⚡👥⭐🎯👉🔗💬]){2,}', r'\1', text)
            # Usar lenguaje más formal
            text = text.replace("tú", "usted").replace("Tú", "Usted")
        elif tone_lower == "urgente":
            # Agregar más urgencia visual
            if "ÚLTIMAS" not in text and "últimas" not in text:
                text = "⚡ " + text
            # Agregar palabras de urgencia
            if "ahora" not in text.lower() and "inmediato" not in text.lower():
                text = text.replace("Link en bio", "Link en bio AHORA MISMO")
        elif tone_lower == "casual":
            # Hacer más casual y relajado
            text = text.replace("usted", "tú").replace("Usted", "Tú")
            # Agregar más emojis
            if len(re.findall(r'[😀-🙏🌀-🗿]', text)) < 3:
                text = text.replace(".", " 😊")
        elif tone_lower == "emocional":
            # Agregar más emojis y lenguaje emocional
            if "❤️" not in text and "💙" not in text:
                text = text.replace("gracias", "gracias ❤️")
        
        return text
    
    def _analyze_post(
        self,
        post_content: str,
        platform: Platform,
        post_type: PostType,
        has_hashtags: bool,
        has_cta: bool
    ) -> PostAnalysis:
        """Analiza el post generado y calcula métricas"""
        # Detectar características
        has_numbers = bool(re.search(r'\d+%|\d+\s*(veces|meses|años|horas|días|personas)', post_content))
        has_emojis = bool(re.findall(r'[😀-🙏🌀-🗿]', post_content))
        has_questions = bool(re.search(r'[¿?]', post_content))
        
        # Calcular métricas de legibilidad
        sentences = re.split(r'[.!?]+', post_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        word_count = len(post_content.split())
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        # Calcular scores
        engagement_score = 50  # Base
        
        # Factores que aumentan engagement
        if has_numbers:
            engagement_score += 15
        if has_emojis:
            engagement_score += 10
        if has_questions:
            engagement_score += 12
        if has_cta:
            engagement_score += 13
        if has_hashtags:
            engagement_score += 5
        
        # Ajustar por longitud óptima
        optimal_length = self.platform_limits[platform]["optimal_length"]
        current_length = len(post_content)
        if optimal_length * 0.8 <= current_length <= optimal_length * 1.2:
            engagement_score += 10
        elif current_length < optimal_length * 0.5:
            engagement_score -= 5
        elif current_length > optimal_length * 2:
            engagement_score -= 10
        
        engagement_score = max(0, min(100, engagement_score))
        
        # Legibilidad (basado en longitud de oraciones)
        if avg_words_per_sentence <= 20:
            readability_score = 90
        elif avg_words_per_sentence <= 30:
            readability_score = 75
        else:
            readability_score = 60
        
        # Potencial de conversión
        conversion_potential = 50
        if has_cta:
            conversion_potential += 20
        if has_numbers:
            conversion_potential += 15
        if post_type == PostType.OFFER:
            conversion_potential += 15
        conversion_potential = max(0, min(100, conversion_potential))
        
        # Generar recomendaciones
        recommendations = []
        
        if not has_numbers:
            recommendations.append("Agregar números o métricas específicas aumenta engagement en 15%")
        
        if not has_questions:
            recommendations.append("Incluir preguntas retóricas puede aumentar comentarios")
        
        if current_length < optimal_length * 0.8:
            recommendations.append(f"El post es corto. Longitud óptima para {platform.value}: {optimal_length} caracteres")
        elif current_length > optimal_length * 1.5:
            recommendations.append(f"El post es largo. Considera acortarlo para mejor engagement")
        
        if not has_emojis and platform in [Platform.INSTAGRAM, Platform.TIKTOK]:
            recommendations.append("Agregar emojis relevantes puede aumentar engagement en redes visuales")
        
        if avg_words_per_sentence > 25:
            recommendations.append("Oraciones más cortas mejoran la legibilidad")
        
        # Análisis de sentimiento si está disponible
        sentiment_score = None
        sentiment_label = None
        if self.sentiment_analyzer:
            try:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(post_content)
                sentiment_score = sentiment_result.get("score", 0.0)
                sentiment_label = sentiment_result.get("label", "neutral")
                
                # Ajustar engagement score basado en sentimiento
                if sentiment_label == "positive" and sentiment_score > 0.3:
                    engagement_score += 5
                elif sentiment_label == "negative" and sentiment_score < -0.3:
                    engagement_score -= 10
                    recommendations.append("El sentimiento es negativo. Considera ajustar el tono")
            except Exception as e:
                logger.warning(f"Error analizando sentimiento: {e}")
        
        return PostAnalysis(
            engagement_score=engagement_score,
            readability_score=readability_score,
            conversion_potential=conversion_potential,
            has_numbers=has_numbers,
            has_emojis=has_emojis,
            has_questions=has_questions,
            has_cta=has_cta,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_words_per_sentence=avg_words_per_sentence,
            recommendations=recommendations,
            optimal_posting_times=self.optimal_times.get(platform, []),
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label
        )
    
    def generate_multiple_variations(
        self,
        platform: str,
        post_type: str,
        product_name: str,
        target_audience: str,
        tone: str = "amigable",
        promotion_details: Optional[Dict] = None,
        custom_data: Optional[Dict] = None,
        num_variations: int = 3,
        include_hashtags: bool = True,
        include_cta: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Genera múltiples variaciones de un post para A/B testing
        
        Args:
            num_variations: Número de variaciones a generar (1-3)
            ... (otros parámetros iguales a generate_post)
        
        Returns:
            Lista de posts generados
        """
        variations = []
        num_variations = min(max(1, num_variations), 3)  # Entre 1 y 3
        
        for i in range(1, num_variations + 1):
            try:
                post = self.generate_post(
                    platform=platform,
                    post_type=post_type,
                    product_name=product_name,
                    target_audience=target_audience,
                    tone=tone,
                    promotion_details=promotion_details,
                    custom_data=custom_data,
                    variation=i,
                    include_hashtags=include_hashtags,
                    include_cta=include_cta
                )
                post["variation_number"] = i
                variations.append(post)
            except Exception as e:
                logger.error(f"Error generando variación {i}: {e}")
        
        return variations
    
    def compare_variations(
        self,
        variations: List[Dict[str, Any]]
    ) -> VariationComparison:
        """
        Compara múltiples variaciones y recomienda la mejor
        
        Args:
            variations: Lista de posts generados
        
        Returns:
            Comparación con recomendaciones
        """
        if not variations:
            raise ValueError("Se requiere al menos una variación para comparar")
        
        # Encontrar mejores por métrica
        best_engagement = max(variations, key=lambda v: v.get("analysis", {}).get("engagement_score", 0))
        best_conversion = max(variations, key=lambda v: v.get("analysis", {}).get("conversion_potential", 0))
        best_readability = max(variations, key=lambda v: v.get("analysis", {}).get("readability_score", 0))
        
        # Crear tabla de comparación
        comparison_table = []
        for i, var in enumerate(variations, 1):
            analysis = var.get("analysis", {})
            comparison_table.append({
                "variation": i,
                "engagement_score": analysis.get("engagement_score", 0),
                "conversion_potential": analysis.get("conversion_potential", 0),
                "readability_score": analysis.get("readability_score", 0),
                "length": var.get("length", 0),
                "has_numbers": analysis.get("has_numbers", False),
                "has_questions": analysis.get("has_questions", False),
                "sentiment": analysis.get("sentiment_label", "neutral")
            })
        
        # Generar recomendaciones
        recommendations = []
        
        if best_engagement != best_conversion:
            recommendations.append(
                f"Variación {best_engagement.get('variation_number', 1)} tiene mejor engagement, "
                f"pero variación {best_conversion.get('variation_number', 1)} tiene mejor conversión"
            )
        
        # Recomendar la mejor variación general
        overall_scores = []
        for var in variations:
            analysis = var.get("analysis", {})
            overall = (
                analysis.get("engagement_score", 0) * 0.4 +
                analysis.get("conversion_potential", 0) * 0.4 +
                analysis.get("readability_score", 0) * 0.2
            )
            overall_scores.append((overall, var))
        
        best_overall = max(overall_scores, key=lambda x: x[0])[1]
        recommendations.append(
            f"Variación {best_overall.get('variation_number', 1)} es la mejor opción general "
            f"(score combinado: {overall_scores[best_overall.get('variation_number', 1) - 1][0]:.1f})"
        )
        
        return VariationComparison(
            best_engagement=best_engagement,
            best_conversion=best_conversion,
            best_readability=best_readability,
            recommendations=recommendations,
            comparison_table=comparison_table
        )
    
    def generate_story_content(
        self,
        platform: str,
        post_type: str,
        product_name: str,
        target_audience: str,
        base_post: Optional[Dict[str, Any]] = None,
        num_slides: int = 8
    ) -> StoryContent:
        """
        Genera contenido para Stories basado en un post
        
        Args:
            platform: Plataforma
            post_type: Tipo de post
            product_name: Nombre del producto
            target_audience: Audiencia
            base_post: Post base (opcional, se genera si no se proporciona)
            num_slides: Número de slides (8-12 recomendado)
        
        Returns:
            Contenido para Stories
        """
        if not base_post:
            base_post = self.generate_post(
                platform=platform,
                post_type=post_type,
                product_name=product_name,
                target_audience=target_audience
            )
        
        slides = []
        post_content = base_post.get("post_content", "")
        
        # Dividir contenido en slides según tipo de post
        if post_type == "teaser":
            slides = [
                {"text": "🔮 Algo grande viene...", "type": "hook"},
                {"text": f"En 48 horas te mostraremos {product_name}", "type": "announcement"},
                {"text": "¿Qué esperas más?", "type": "question"},
                {"text": "Comenta con un emoji 👇", "type": "cta"},
                {"text": "Los primeros 100 reciben acceso VIP 🎁", "type": "benefit"},
                {"text": "Activa las notificaciones 🔔", "type": "reminder"},
                {"text": "Próximamente...", "type": "teaser"},
                {"text": "Link en bio para más info", "type": "cta_final"}
            ]
        elif post_type == "demo":
            # Dividir beneficios en slides
            benefits = re.findall(r'✨\s*([^\n]+)|✅\s*([^\n]+)', post_content)
            slides = [
                {"text": f"🎉 Presentamos {product_name}", "type": "announcement"},
                {"text": "Lo que puedes hacer HOY:", "type": "intro"}
            ]
            
            for i, benefit in enumerate(benefits[:3], 1):
                benefit_text = benefit[0] or benefit[1]
                slides.append({"text": f"{i}. {benefit_text}", "type": "benefit"})
            
            slides.extend([
                {"text": "👉 Mira el video completo", "type": "cta"},
                {"text": f"Ya son {base_post.get('metadata', {}).get('number', '1000')}+ usuarios", "type": "social_proof"},
                {"text": "🔗 Link en bio para probarlo GRATIS", "type": "cta_final"}
            ])
        elif post_type == "offer":
            slides = [
                {"text": "⚡ ÚLTIMAS HORAS ⚡", "type": "urgency"},
                {"text": f"🔥 OFERTA DE LANZAMIENTO 🔥", "type": "announcement"},
                {"text": f"Precio especial: ${base_post.get('metadata', {}).get('promotion_details', {}).get('discount_price', '79')}", "type": "price"},
                {"text": "✨ Lo que incluye:", "type": "intro"},
                {"text": "• Beneficio 1\n• Beneficio 2\n• Beneficio 3", "type": "benefits"},
                {"text": "⏰ Oferta termina pronto", "type": "urgency"},
                {"text": "👉 Solo quedan X cupos", "type": "scarcity"},
                {"text": "🔗 Link en bio AHORA", "type": "cta_final"}
            ]
        
        # Limitar número de slides
        slides = slides[:num_slides]
        
        # Sugerencias de imágenes/videos
        suggested_images = [
            f"Imagen del producto {product_name}",
            "Gráfico de beneficios",
            "Testimonial visual",
            "Comparación antes/después"
        ]
        
        suggested_videos = [
            "Video demo de 15 segundos",
            "Time-lapse del producto en acción",
            "Testimonial en video"
        ]
        
        # Elementos interactivos
        interactive_elements = []
        if post_type == "teaser":
            interactive_elements = ["Encuesta: ¿Qué esperas?", "Pregunta: ¿Tienes dudas?"]
        elif post_type == "demo":
            interactive_elements = ["Encuesta: ¿Qué beneficio te interesa más?", "Link sticker"]
        elif post_type == "offer":
            interactive_elements = ["Countdown timer", "Link sticker", "Encuesta: ¿Ya aprovechaste la oferta?"]
        
        return StoryContent(
            slides=slides,
            total_slides=len(slides),
            suggested_images=suggested_images,
            suggested_videos=suggested_videos,
            interactive_elements=interactive_elements
        )
    
    def export_to_format(
        self,
        post: Dict[str, Any],
        format_type: str = "json"
    ) -> str:
        """
        Exporta un post a diferentes formatos
        
        Args:
            post: Post generado
            format_type: Formato (json, markdown, csv, html)
        
        Returns:
            String con el contenido exportado
        """
        if format_type == "json":
            return json.dumps(post, indent=2, ensure_ascii=False)
        
        elif format_type == "markdown":
            md = f"""# Post para {post['platform'].upper()}

**Tipo:** {post['post_type']}  
**Tono:** {post['tone']}  
**Longitud:** {post['length']}/{post['max_length']} caracteres

## Contenido

{post['full_post']}

## Análisis

- **Engagement Score:** {post.get('analysis', {}).get('engagement_score', 'N/A')}/100
- **Conversion Potential:** {post.get('analysis', {}).get('conversion_potential', 'N/A')}/100
- **Readability Score:** {post.get('analysis', {}).get('readability_score', 'N/A')}/100

## Hashtags ({len(post.get('hashtags', []))})

{' '.join(post.get('hashtags', []))}

## Recomendaciones

"""
            for rec in post.get('analysis', {}).get('recommendations', []):
                md += f"- {rec}\n"
            
            return md
        
        elif format_type == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(["Campo", "Valor"])
            writer.writerow(["Platform", post['platform']])
            writer.writerow(["Post Type", post['post_type']])
            writer.writerow(["Length", post['length']])
            writer.writerow(["Engagement Score", post.get('analysis', {}).get('engagement_score', '')])
            writer.writerow(["Full Post", post['full_post'].replace('\n', ' ')])
            
            return output.getvalue()
        
        elif format_type == "html":
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Post - {post['platform']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .post {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; flex: 1; }}
        .hashtags {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Post para {post['platform'].upper()}</h1>
    <div class="post">
        <pre style="white-space: pre-wrap;">{post['full_post']}</pre>
    </div>
    <div class="metrics">
        <div class="metric">
            <strong>Engagement</strong><br>
            {post.get('analysis', {}).get('engagement_score', 'N/A')}/100
        </div>
        <div class="metric">
            <strong>Conversión</strong><br>
            {post.get('analysis', {}).get('conversion_potential', 'N/A')}/100
        </div>
        <div class="metric">
            <strong>Legibilidad</strong><br>
            {post.get('analysis', {}).get('readability_score', 'N/A')}/100
        </div>
    </div>
    <div class="hashtags">
        <strong>Hashtags:</strong> {' '.join(post.get('hashtags', []))}
    </div>
</body>
</html>"""
            return html
        
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
    
    def generate_multi_platform(
        self,
        platforms: List[str],
        post_type: str,
        product_name: str,
        target_audience: str,
        tone: str = "amigable",
        promotion_details: Optional[Dict] = None,
        custom_data: Optional[Dict] = None,
        variation: int = 1
    ) -> MultiPlatformContent:
        """
        Genera contenido para múltiples plataformas simultáneamente
        
        Args:
            platforms: Lista de plataformas (ej: ["instagram", "linkedin", "tiktok"])
            ... (otros parámetros iguales a generate_post)
        
        Returns:
            Contenido para múltiples plataformas con análisis de consistencia
        """
        platform_contents = {}
        
        for platform in platforms:
            try:
                post = self.generate_post(
                    platform=platform,
                    post_type=post_type,
                    product_name=product_name,
                    target_audience=target_audience,
                    tone=tone,
                    promotion_details=promotion_details,
                    custom_data=custom_data,
                    variation=variation
                )
                platform_contents[platform] = post
            except Exception as e:
                logger.error(f"Error generando post para {platform}: {e}")
                platform_contents[platform] = {"error": str(e)}
        
        # Calcular consistencia cross-platform
        if len(platform_contents) > 1:
            # Comparar mensajes clave entre plataformas
            key_messages = []
            for platform, content in platform_contents.items():
                if "error" not in content:
                    post_content = content.get("post_content", "")
                    # Extraer mensajes clave (primeras 50 palabras)
                    key_msg = " ".join(post_content.split()[:50])
                    key_messages.append(key_msg.lower())
            
            # Calcular similitud (método simple)
            if key_messages:
                common_words = set(key_messages[0].split())
                for msg in key_messages[1:]:
                    common_words &= set(msg.split())
                
                total_words = set()
                for msg in key_messages:
                    total_words |= set(msg.split())
                
                consistency = (len(common_words) / len(total_words) * 100) if total_words else 0
            else:
                consistency = 0
        else:
            consistency = 100
        
        # Generar horario óptimo para cada plataforma
        optimal_schedule = {}
        for platform in platforms:
            if platform in platform_contents and "error" not in platform_contents[platform]:
                times = self.optimal_times.get(Platform(platform), [])
                if times:
                    optimal_schedule[platform] = times[0]  # Mejor horario
        
        # Recomendaciones
        recommendations = []
        if consistency < 70:
            recommendations.append("Considera mantener mensajes más consistentes entre plataformas")
        
        if len(platform_contents) > 3:
            recommendations.append("Publicar en múltiples plataformas puede aumentar alcance en 40%")
        
        return MultiPlatformContent(
            platform_contents=platform_contents,
            cross_platform_consistency=consistency,
            optimal_posting_schedule=optimal_schedule,
            recommendations=recommendations
        )
    
    def batch_generate(
        self,
        products: List[Dict[str, Any]],
        platforms: Optional[List[str]] = None,
        post_type: str = "demo"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Genera posts para múltiples productos en batch
        
        Args:
            products: Lista de productos con sus datos
                [{"product": "Producto 1", "audience": "audiencia 1", ...}, ...]
            platforms: Lista de plataformas (default: todas)
            post_type: Tipo de post para todos
        
        Returns:
            Dict con posts generados por producto
        """
        if platforms is None:
            platforms = [p.value for p in Platform]
        
        results = {}
        
        for product_data in products:
            product_name = product_data.get("product", "Producto")
            audience = product_data.get("audience", "general")
            tone = product_data.get("tone", "amigable")
            custom_data = product_data.get("custom_data", {})
            promotion_details = product_data.get("promotion_details")
            
            product_results = []
            
            for platform in platforms:
                try:
                    post = self.generate_post(
                        platform=platform,
                        post_type=post_type,
                        product_name=product_name,
                        target_audience=audience,
                        tone=tone,
                        promotion_details=promotion_details,
                        custom_data=custom_data
                    )
                    product_results.append(post)
                except Exception as e:
                    logger.error(f"Error generando post para {product_name} en {platform}: {e}")
            
            results[product_name] = product_results
        
        return results
    
    def analyze_keywords(
        self,
        post_content: str,
        industry: str = "general"
    ) -> KeywordAnalysis:
        """
        Analiza keywords y SEO del contenido
        
        Args:
            post_content: Contenido del post
            industry: Industria para keywords trending
        
        Returns:
            Análisis de keywords y SEO
        """
        # Extraer keywords del contenido
        words = re.findall(r'\b\w+\b', post_content.lower())
        word_freq = Counter(words)
        
        # Filtrar palabras comunes
        stop_words = {
            "el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le",
            "da", "su", "por", "son", "con", "para", "al", "del", "los", "las", "una", "como",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with"
        }
        
        keywords = [word for word, count in word_freq.most_common(20) 
                   if word not in stop_words and len(word) > 3]
        
        # Calcular densidad de keywords
        total_words = len(words)
        keyword_density = {
            kw: (word_freq[kw] / total_words * 100) if total_words > 0 else 0
            for kw in keywords[:10]
        }
        
        # Calcular SEO score
        seo_score = 50  # Base
        
        # Factores positivos
        if len(keywords) >= 5:
            seo_score += 15
        if any(kw in self.trending_keywords.get(industry, []) for kw in keywords):
            seo_score += 20
        if len(post_content) >= 100:
            seo_score += 10
        if re.search(r'\d+', post_content):  # Tiene números
            seo_score += 5
        
        seo_score = min(100, seo_score)
        
        # Keywords sugeridas
        suggested_keywords = []
        industry_keywords = self.trending_keywords.get(industry, [])
        for kw in industry_keywords:
            if kw.lower() not in post_content.lower():
                suggested_keywords.append(kw)
        
        return KeywordAnalysis(
            keywords=keywords[:10],
            keyword_density=keyword_density,
            seo_score=seo_score,
            suggested_keywords=suggested_keywords[:5],
            trending_keywords=industry_keywords[:5]
        )
    
    def generate_content_formats(
        self,
        base_post: Dict[str, Any],
        formats: List[str] = ["feed", "reel", "carousel"]
    ) -> Dict[str, ContentFormat]:
        """
        Genera contenido adaptado para diferentes formatos
        
        Args:
            base_post: Post base generado
            formats: Lista de formatos a generar
        
        Returns:
            Dict con contenido para cada formato
        """
        post_content = base_post.get("post_content", "")
        platform = base_post.get("platform", "instagram")
        post_type = base_post.get("post_type", "demo")
        
        content_formats = {}
        
        for fmt in formats:
            if fmt == "feed":
                # Feed post normal
                content_formats["feed"] = ContentFormat(
                    format_type="feed",
                    content=base_post.get("full_post", ""),
                    suggested_aspect_ratio="1:1"
                )
            
            elif fmt == "reel":
                # Reel: contenido corto y dinámico
                reel_content = self._create_reel_content(post_content, post_type)
                content_formats["reel"] = ContentFormat(
                    format_type="reel",
                    content=reel_content,
                    suggested_duration=30,
                    suggested_aspect_ratio="9:16",
                    captions=self._extract_captions(post_content),
                    suggested_music="Upbeat/energetic"
                )
            
            elif fmt == "carousel":
                # Carousel: dividir en slides
                carousel_slides = self._create_carousel_slides(post_content, post_type)
                content_formats["carousel"] = ContentFormat(
                    format_type="carousel",
                    content="\n---SLIDE---\n".join(carousel_slides),
                    suggested_aspect_ratio="1:1"
                )
            
            elif fmt == "video":
                # Video: script para video
                video_script = self._create_video_script(post_content, post_type)
                content_formats["video"] = ContentFormat(
                    format_type="video",
                    content=video_script,
                    suggested_duration=60,
                    suggested_aspect_ratio="16:9"
                )
        
        return content_formats
    
    def _create_reel_content(self, post_content: str, post_type: str) -> str:
        """Crea contenido optimizado para Reels"""
        # Extraer hook y puntos clave
        sentences = re.split(r'[.!?]+', post_content)
        hook = sentences[0] if sentences else post_content[:50]
        
        # Crear contenido dinámico
        if post_type == "teaser":
            return f"{hook}\n\n🔮 Próximamente...\n\n#Shorts #Reels"
        elif post_type == "demo":
            # Extraer beneficios
            benefits = re.findall(r'✨\s*([^\n]+)|✅\s*([^\n]+)', post_content)
            benefit_text = "\n".join([b[0] or b[1] for b in benefits[:3]])
            return f"{hook}\n\n{benefit_text}\n\n#Demo #Reels"
        else:  # offer
            return f"{hook}\n\n⚡ Oferta limitada\n\n#Oferta #Reels"
    
    def _extract_captions(self, post_content: str) -> List[str]:
        """Extrae captions para video"""
        sentences = re.split(r'[.!?]+', post_content)
        return [s.strip() for s in sentences[:5] if s.strip()]
    
    def _create_carousel_slides(self, post_content: str, post_type: str) -> List[str]:
        """Crea slides para carousel"""
        slides = []
        
        if post_type == "demo":
            # Slide 1: Hook
            slides.append("🎉 ¡Nuevo producto!\n\nDescubre cómo funciona")
            
            # Slides 2-4: Beneficios
            benefits = re.findall(r'✨\s*([^\n]+)|✅\s*([^\n]+)', post_content)
            for i, benefit in enumerate(benefits[:3], 1):
                benefit_text = benefit[0] or benefit[1]
                slides.append(f"Beneficio {i}:\n{benefit_text}")
            
            # Slide final: CTA
            slides.append("🔗 Link en bio para probarlo GRATIS")
        else:
            # Dividir contenido en chunks
            words = post_content.split()
            chunk_size = len(words) // 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                slides.append(chunk)
        
        return slides[:8]  # Máximo 8 slides
    
    def _create_video_script(self, post_content: str, post_type: str) -> str:
        """Crea script para video"""
        hook = post_content.split('\n')[0]
        
        script = f"""VIDEO SCRIPT - {post_type.upper()}

[0-3s] HOOK: {hook}

[3-10s] INTRODUCCIÓN:
Presenta el problema o necesidad

[10-30s] SOLUCIÓN:
Muestra cómo el producto resuelve el problema

[30-50s] BENEFICIOS:
Destaca 2-3 beneficios principales

[50-60s] CTA:
Llamada a la acción clara

MÚSICA: Upbeat, modern
ESTILO: Dinámico, rápido
TEXTO SUPERPUESTO: Sí, con puntos clave
"""
        return script
    
    def generate_content_calendar(
        self,
        start_date: datetime,
        days: int = 7,
        post_type_sequence: List[str] = ["teaser", "demo", "offer"],
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Genera calendario de contenido para múltiples días
        
        Args:
            start_date: Fecha de inicio
            days: Número de días
            post_type_sequence: Secuencia de tipos de posts
            platforms: Plataformas (default: todas)
        
        Returns:
            Lista de posts programados con fechas
        """
        if platforms is None:
            platforms = [p.value for p in Platform]
        
        calendar = []
        current_date = start_date
        
        for day in range(days):
            # Determinar tipo de post según secuencia
            post_type_idx = day % len(post_type_sequence)
            post_type = post_type_sequence[post_type_idx]
            
            # Generar posts para cada plataforma
            for platform in platforms:
                try:
                    # Usar datos de ejemplo (deberían venir como parámetros)
                    post = self.generate_post(
                        platform=platform,
                        post_type=post_type,
                        product_name="Producto",
                        target_audience="audiencia"
                    )
                    
                    # Agregar información de calendario
                    post["scheduled_date"] = current_date.strftime("%Y-%m-%d")
                    post["scheduled_time"] = self.optimal_times.get(
                        Platform(platform), 
                        ["09:00"]
                    )[0].split("-")[0]  # Tomar primera hora
                    post["day_number"] = day + 1
                    
                    calendar.append(post)
                except Exception as e:
                    logger.error(f"Error generando post para calendario: {e}")
            
            current_date += timedelta(days=1)
        
        return calendar
    
    def analyze_competitors(
        self,
        competitor_posts: List[Dict[str, Any]],
        industry: str = "general"
    ) -> CompetitorAnalysis:
        """
        Analiza posts de competidores para identificar oportunidades
        
        Args:
            competitor_posts: Lista de posts de competidores con métricas
            industry: Industria para contexto
        
        Returns:
            Análisis de competencia con recomendaciones
        """
        if not competitor_posts:
            return CompetitorAnalysis(
                competitor_posts=[],
                common_themes=[],
                engagement_benchmarks={},
                content_gaps=[],
                opportunities=["No hay datos de competencia disponibles"],
                recommended_strategy="Enfocarse en contenido único y diferenciado"
            )
        
        # Extraer temas comunes
        all_text = " ".join([p.get("content", "") for p in competitor_posts])
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = Counter(words)
        common_themes = [word for word, count in word_freq.most_common(10) 
                        if len(word) > 4]
        
        # Calcular benchmarks de engagement
        engagement_benchmarks = {
            "avg_likes": sum(p.get("likes", 0) for p in competitor_posts) / len(competitor_posts),
            "avg_comments": sum(p.get("comments", 0) for p in competitor_posts) / len(competitor_posts),
            "avg_shares": sum(p.get("shares", 0) for p in competitor_posts) / len(competitor_posts),
            "avg_engagement_rate": sum(p.get("engagement_rate", 0) for p in competitor_posts) / len(competitor_posts)
        }
        
        # Identificar gaps de contenido
        content_gaps = []
        if not any("video" in p.get("type", "").lower() for p in competitor_posts):
            content_gaps.append("Videos - Competencia no usa mucho video")
        if not any("carousel" in p.get("type", "").lower() for p in competitor_posts):
            content_gaps.append("Carousels - Oportunidad de destacar")
        
        # Oportunidades
        opportunities = []
        top_performer = max(competitor_posts, key=lambda p: p.get("engagement_rate", 0))
        if top_performer:
            opportunities.append(f"Mejorar engagement: Top competidor tiene {top_performer.get('engagement_rate', 0):.1f}%")
        
        if engagement_benchmarks["avg_engagement_rate"] < 5:
            opportunities.append("Mercado con bajo engagement - Oportunidad de destacar")
        
        # Estrategia recomendada
        recommended_strategy = f"""
        Basado en análisis de {len(competitor_posts)} posts de competencia:
        - Enfocarse en: {', '.join(common_themes[:3])}
        - Benchmark de engagement: {engagement_benchmarks['avg_engagement_rate']:.1f}%
        - Oportunidades: {', '.join(opportunities[:2])}
        """
        
        return CompetitorAnalysis(
            competitor_posts=competitor_posts,
            common_themes=common_themes[:5],
            engagement_benchmarks=engagement_benchmarks,
            content_gaps=content_gaps,
            opportunities=opportunities,
            recommended_strategy=recommended_strategy.strip()
        )
    
    def generate_ai_suggestions(
        self,
        base_post: Dict[str, Any],
        num_suggestions: int = 5
    ) -> AIContentSuggestion:
        """
        Genera sugerencias de mejora usando análisis inteligente
        
        Args:
            base_post: Post base para analizar
            num_suggestions: Número de sugerencias por categoría
        
        Returns:
            Sugerencias de contenido generadas por IA
        """
        post_content = base_post.get("post_content", "")
        analysis = base_post.get("analysis", {})
        
        # Generar hooks alternativos
        first_sentence = post_content.split('\n')[0] if post_content else ""
        suggested_hooks = [
            f"¿Sabías que {first_sentence.lower()}?",
            f"🚀 {first_sentence}",
            f"Descubre cómo {first_sentence.lower()}",
            f"Lo que nadie te dice sobre {first_sentence.lower()}",
            f"3 razones por las que {first_sentence.lower()}"
        ][:num_suggestions]
        
        # Generar CTAs alternativos
        suggested_ctas = [
            "🔗 Link en bio para más información",
            "💬 ¿Tienes preguntas? Escríbenos por DM",
            "👉 Prueba gratis - Sin tarjeta de crédito",
            "🎁 Oferta exclusiva - Solo por tiempo limitado",
            "📥 Descarga ahora y comienza hoy mismo"
        ][:num_suggestions]
        
        # Variaciones de contenido
        content_variations = []
        if analysis.get("has_numbers"):
            # Crear variación sin números
            variation = re.sub(r'\d+', '[NÚMERO]', post_content)
            content_variations.append(f"Variación sin números: {variation[:100]}...")
        
        if analysis.get("has_emojis"):
            # Crear variación sin emojis
            variation = re.sub(r'[😀-🙏🌀-🗿]', '', post_content)
            content_variations.append(f"Variación sin emojis: {variation[:100]}...")
        
        # Sugerencias de tono
        tone_suggestions = []
        current_tone = base_post.get("tone", "amigable")
        if current_tone != "urgente":
            tone_suggestions.append("Probar tono más urgente para aumentar conversión")
        if current_tone != "emocional":
            tone_suggestions.append("Agregar más emoción puede aumentar engagement")
        
        # Sugerencias de mejora
        improvement_suggestions = []
        if not analysis.get("has_numbers"):
            improvement_suggestions.append("Agregar números específicos aumenta credibilidad")
        if analysis.get("readability_score", 0) < 80:
            improvement_suggestions.append("Mejorar legibilidad con oraciones más cortas")
        if analysis.get("engagement_score", 0) < 70:
            improvement_suggestions.append("Agregar más elementos interactivos (preguntas, encuestas)")
        
        return AIContentSuggestion(
            suggested_hooks=suggested_hooks,
            suggested_ctas=suggested_ctas,
            content_variations=content_variations[:num_suggestions],
            tone_suggestions=tone_suggestions,
            improvement_suggestions=improvement_suggestions
        )
    
    def create_custom_template(
        self,
        template_id: str,
        template_content: str,
        custom_fields: Dict[str, Any],
        brand_voice: Optional[Dict[str, Any]] = None
    ) -> TemplateCustomization:
        """
        Crea un template personalizado
        
        Args:
            template_id: ID único del template
            template_content: Contenido del template con placeholders
            custom_fields: Campos personalizados disponibles
            brand_voice: Guía de voz de marca
        
        Returns:
            Template personalizado
        """
        self.custom_templates[template_id] = {
            "content": template_content,
            "fields": custom_fields,
            "brand_voice": brand_voice or {},
            "created_at": datetime.now().isoformat()
        }
        
        return TemplateCustomization(
            template_id=template_id,
            custom_fields=custom_fields,
            brand_voice=brand_voice or {},
            style_guide={},
            custom_hashtags=[]
        )
    
    def use_custom_template(
        self,
        template_id: str,
        field_values: Dict[str, str],
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        Usa un template personalizado para generar post
        
        Args:
            template_id: ID del template a usar
            field_values: Valores para rellenar el template
            platform: Plataforma objetivo
        
        Returns:
            Post generado desde template personalizado
        """
        if template_id not in self.custom_templates:
            raise ValueError(f"Template '{template_id}' no encontrado")
        
        template = self.custom_templates[template_id]
        content = template["content"]
        
        # Rellenar placeholders
        for field, value in field_values.items():
            content = content.replace(f"{{{field}}}", str(value))
        
        # Generar post básico
        post = {
            "post_content": content,
            "full_post": content,
            "platform": platform,
            "post_type": "custom",
            "tone": template.get("brand_voice", {}).get("tone", "amigable"),
            "length": len(content),
            "max_length": self.platform_limits[Platform(platform)]["max_length"],
            "hashtags": template.get("custom_hashtags", []),
            "metadata": {
                "template_id": template_id,
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Analizar post generado
        analysis = self._analyze_post(
            content,
            Platform(platform),
            PostType.DEMO,  # Default
            bool(post["hashtags"]),
            True
        )
        post["analysis"] = asdict(analysis)
        
        return post
    
    def analyze_trends(
        self,
        industry: str = "general",
        time_period: str = "7d"
    ) -> TrendAnalysis:
        """
        Analiza tendencias actuales para optimizar contenido
        
        Args:
            industry: Industria objetivo
            time_period: Período de tiempo (7d, 30d, etc.)
        
        Returns:
            Análisis de tendencias con recomendaciones
        """
        # Trending topics basados en keywords
        trending_topics = self.trending_keywords.get(industry, [])[:10]
        
        # Trending hashtags (puede ser cargado desde API)
        trending_hashtags = [
            f"#{topic}" for topic in trending_topics[:5]
        ]
        
        # Trending keywords
        trending_keywords = trending_topics
        
        # Engagement trends (simulado, idealmente desde datos reales)
        engagement_trends = {
            "video": 8.5,
            "carousel": 6.2,
            "image": 4.1,
            "reel": 9.8
        }
        
        # Best posting times (desde optimal_times)
        best_posting_times = {
            platform.value: self.optimal_times.get(platform, [])
            for platform in Platform
        }
        
        # Recomendaciones de contenido
        content_recommendations = []
        if engagement_trends.get("reel", 0) > 8:
            content_recommendations.append("Reels tienen mejor engagement - Priorizar este formato")
        if engagement_trends.get("video", 0) > 7:
            content_recommendations.append("Videos generan alto engagement - Incluir más videos")
        
        # Agregar recomendaciones basadas en trending topics
        if trending_topics:
            content_recommendations.append(
                f"Incluir temas trending: {', '.join(trending_topics[:3])}"
            )
        
        return TrendAnalysis(
            trending_topics=trending_topics,
            trending_hashtags=trending_hashtags,
            trending_keywords=trending_keywords,
            engagement_trends=engagement_trends,
            best_posting_times=best_posting_times,
            content_recommendations=content_recommendations
        )
    
    def optimize_based_on_history(
        self,
        post: Dict[str, Any],
        historical_performance: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Optimiza un post basado en rendimiento histórico
        
        Args:
            post: Post a optimizar
            historical_performance: Datos de rendimiento histórico
        
        Returns:
            Post optimizado con mejoras sugeridas
        """
        if not historical_performance:
            historical_performance = self.generation_history
        
        if not historical_performance:
            return post  # Sin datos históricos, retornar post original
        
        # Analizar posts exitosos
        successful_posts = [
            p for p in historical_performance 
            if p.get("engagement_rate", 0) > 5.0
        ]
        
        if not successful_posts:
            return post
        
        # Extraer características de posts exitosos
        successful_features = {
            "avg_length": sum(len(p.get("content", "")) for p in successful_posts) / len(successful_posts),
            "common_hashtags": [],
            "common_elements": []
        }
        
        # Analizar hashtags comunes
        all_hashtags = []
        for p in successful_posts:
            all_hashtags.extend(p.get("hashtags", []))
        hashtag_freq = Counter(all_hashtags)
        successful_features["common_hashtags"] = [
            tag for tag, count in hashtag_freq.most_common(5)
        ]
        
        # Optimizar post
        optimized_post = post.copy()
        
        # Ajustar longitud si es necesario
        current_length = len(post.get("post_content", ""))
        optimal_length = successful_features["avg_length"]
        if abs(current_length - optimal_length) > 50:
            # Sugerir ajuste de longitud
            optimized_post["optimization_suggestion"] = (
                f"Ajustar longitud a ~{int(optimal_length)} caracteres "
                f"(actual: {current_length})"
            )
        
        # Agregar hashtags exitosos
        current_hashtags = post.get("hashtags", [])
        new_hashtags = [
            tag for tag in successful_features["common_hashtags"]
            if tag not in current_hashtags
        ]
        if new_hashtags:
            optimized_post["suggested_hashtags"] = new_hashtags[:3]
        
        optimized_post["optimized"] = True
        optimized_post["optimization_timestamp"] = datetime.now().isoformat()
        
        return optimized_post
    
    def save_to_history(self, post: Dict[str, Any], performance: Optional[Dict[str, Any]] = None):
        """
        Guarda post en historial para aprendizaje futuro
        
        Args:
            post: Post generado
            performance: Métricas de rendimiento (opcional)
        """
        history_entry = {
            "post_id": post.get("metadata", {}).get("generated_at", datetime.now().isoformat()),
            "platform": post.get("platform"),
            "post_type": post.get("post_type"),
            "content": post.get("post_content", ""),
            "hashtags": post.get("hashtags", []),
            "analysis": post.get("analysis", {}),
            "generated_at": datetime.now().isoformat()
        }
        
        if performance:
            history_entry["performance"] = performance
            history_entry["engagement_rate"] = performance.get("engagement_rate", 0)
        
        self.generation_history.append(history_entry)
        
        # Limitar historial a últimos 1000 posts
        if len(self.generation_history) > 1000:
            self.generation_history = self.generation_history[-1000:]
    
    def generate_multilingual(
        self,
        base_post: Dict[str, Any],
        target_languages: List[str] = ["es", "en"]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Genera versiones del post en múltiples idiomas
        
        Args:
            base_post: Post base en idioma original
            target_languages: Lista de idiomas objetivo
        
        Returns:
            Dict con posts traducidos por idioma
        """
        # Mapeo básico de traducciones (en producción usar API de traducción)
        translations_map = {
            "en": {
                "Comenta": "Comment",
                "Link en bio": "Link in bio",
                "Prueba gratis": "Try free",
                "Oferta": "Offer",
                "Descuento": "Discount"
            }
        }
        
        multilingual_posts = {}
        
        for lang in target_languages:
            if lang == "es":
                # Español es el original
                multilingual_posts[lang] = base_post
            else:
                # Traducción básica (en producción usar API)
                translated_content = base_post.get("post_content", "")
                
                # Aplicar traducciones básicas
                if lang in translations_map:
                    for es_word, en_word in translations_map[lang].items():
                        translated_content = translated_content.replace(es_word, en_word)
                
                translated_post = base_post.copy()
                translated_post["post_content"] = translated_content
                translated_post["full_post"] = translated_content
                translated_post["language"] = lang
                translated_post["metadata"]["original_language"] = "es"
                
                multilingual_posts[lang] = translated_post
        
        return multilingual_posts
    
    def calculate_roi_metrics(
        self,
        post: Dict[str, Any],
        performance: Dict[str, Any],
        campaign_cost: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calcula métricas de ROI y conversión
        
        Args:
            post: Post generado
            performance: Métricas de rendimiento
            campaign_cost: Costo de la campaña
        
        Returns:
            Métricas de ROI y conversión
        """
        impressions = performance.get("impressions", 0)
        reach = performance.get("reach", 0)
        clicks = performance.get("clicks", 0)
        conversions = performance.get("conversions", 0)
        revenue = performance.get("revenue", 0.0)
        
        # Métricas básicas
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        cpm = (campaign_cost / (impressions / 1000)) if impressions > 0 else 0
        cpc = (campaign_cost / clicks) if clicks > 0 else 0
        cpa = (campaign_cost / conversions) if conversions > 0 else 0
        roas = (revenue / campaign_cost) if campaign_cost > 0 else 0
        roi = ((revenue - campaign_cost) / campaign_cost * 100) if campaign_cost > 0 else 0
        
        return {
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "campaign_cost": campaign_cost,
            "ctr": round(ctr, 2),
            "conversion_rate": round(conversion_rate, 2),
            "cpm": round(cpm, 2),
            "cpc": round(cpc, 2),
            "cpa": round(cpa, 2),
            "roas": round(roas, 2),
            "roi": round(roi, 2),
            "profit": round(revenue - campaign_cost, 2)
        }
    
    def version_post(
        self,
        base_post: Dict[str, Any],
        version_name: str,
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea una versión del post con cambios específicos
        
        Args:
            base_post: Post base
            version_name: Nombre de la versión
            changes: Cambios a aplicar
        
        Returns:
            Nueva versión del post
        """
        version = base_post.copy()
        
        # Aplicar cambios
        if "content" in changes:
            version["post_content"] = changes["content"]
            version["full_post"] = changes["content"]
        
        if "hashtags" in changes:
            version["hashtags"] = changes["hashtags"]
        
        if "tone" in changes:
            version["tone"] = changes["tone"]
        
        # Agregar metadata de versión
        version["version"] = version_name
        version["base_version"] = base_post.get("version", "original")
        version["version_history"] = base_post.get("version_history", []) + [{
            "version": version_name,
            "changes": changes,
            "created_at": datetime.now().isoformat()
        }]
        version["metadata"]["versioned"] = True
        version["metadata"]["version_name"] = version_name
        
        # Re-analizar versión
        analysis = self._analyze_post(
            version["post_content"],
            Platform(version["platform"]),
            PostType(version["post_type"]),
            bool(version.get("hashtags")),
            True
        )
        version["analysis"] = asdict(analysis)
        
        return version
    
    def generate_contextual_content(
        self,
        context: str,
        product_name: str,
        target_audience: str,
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        Genera contenido contextual basado en eventos, estaciones, etc.
        
        Args:
            context: Contexto (black_friday, navidad, verano, lanzamiento, etc.)
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            platform: Plataforma
        
        Returns:
            Post contextual generado
        """
        context_templates = {
            "black_friday": {
                "hook": "🔥 BLACK FRIDAY - Oferta única del año",
                "urgency": "Solo 24 horas",
                "discount": "50%",
                "hashtags": ["#BlackFriday", "#Oferta", "#Descuento"]
            },
            "navidad": {
                "hook": "🎄 Regalo perfecto para Navidad",
                "urgency": "Tiempo limitado",
                "discount": "30%",
                "hashtags": ["#Navidad", "#Regalo", "#OfertaNavidad"]
            },
            "verano": {
                "hook": "☀️ Prepárate para el verano",
                "urgency": "Oferta de temporada",
                "discount": "25%",
                "hashtags": ["#Verano", "#Oferta", "#Temporada"]
            },
            "lanzamiento": {
                "hook": "🚀 Lanzamiento oficial",
                "urgency": "Acceso anticipado",
                "discount": "20%",
                "hashtags": ["#Lanzamiento", "#Nuevo", "#Innovación"]
            },
            "año_nuevo": {
                "hook": "🎉 Nuevo año, nuevos objetivos",
                "urgency": "Oferta de año nuevo",
                "discount": "30%",
                "hashtags": ["#AñoNuevo", "#Objetivos", "#Oferta"]
            }
        }
        
        template = context_templates.get(context.lower(), context_templates["lanzamiento"])
        
        # Generar post con contexto
        custom_data = {
            "problem": f"Prepararse para {context}",
            "discount": template["discount"],
            "urgency_text": template["urgency"]
        }
        
        post = self.generate_post(
            platform=platform,
            post_type="offer",
            product_name=product_name,
            target_audience=target_audience,
            custom_data=custom_data
        )
        
        # Agregar contexto
        post["context"] = context
        post["contextual_hook"] = template["hook"]
        post["hashtags"] = template["hashtags"] + post.get("hashtags", [])[:20]
        
        return post
    
    def analyze_audience_segments(
        self,
        posts: List[Dict[str, Any]],
        audience_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analiza segmentos de audiencia basado en posts
        
        Args:
            posts: Lista de posts generados
            audience_data: Datos de audiencia (opcional)
        
        Returns:
            Análisis de segmentos de audiencia
        """
        # Analizar posts por tipo
        posts_by_type = {}
        for post in posts:
            post_type = post.get("post_type", "unknown")
            if post_type not in posts_by_type:
                posts_by_type[post_type] = []
            posts_by_type[post_type].append(post)
        
        # Analizar engagement por segmento
        segment_analysis = {}
        for segment, segment_posts in posts_by_type.items():
            avg_engagement = sum(
                p.get("analysis", {}).get("engagement_score", 0)
                for p in segment_posts
            ) / len(segment_posts) if segment_posts else 0
            
            segment_analysis[segment] = {
                "count": len(segment_posts),
                "avg_engagement": round(avg_engagement, 2),
                "best_performer": max(
                    segment_posts,
                    key=lambda p: p.get("analysis", {}).get("engagement_score", 0)
                ) if segment_posts else None
            }
        
        # Recomendaciones por segmento
        recommendations = []
        best_segment = max(
            segment_analysis.items(),
            key=lambda x: x[1]["avg_engagement"]
        )[0] if segment_analysis else None
        
        if best_segment:
            recommendations.append(
                f"Segmento '{best_segment}' tiene mejor engagement promedio. "
                f"Priorizar este tipo de contenido."
            )
        
        return {
            "segments": segment_analysis,
            "total_posts": len(posts),
            "best_segment": best_segment,
            "recommendations": recommendations,
            "audience_insights": audience_data or {}
        }
    
    def generate_time_based_content(
        self,
        time_of_day: str,
        product_name: str,
        target_audience: str,
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        Genera contenido optimizado para diferentes momentos del día
        
        Args:
            time_of_day: Momento del día (morning, afternoon, evening, night)
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            platform: Plataforma
        
        Returns:
            Post optimizado para el momento del día
        """
        time_templates = {
            "morning": {
                "hook": "☀️ Buenos días!",
                "tone": "energético",
                "message": "Comienza tu día con",
                "hashtags": ["#BuenosDías", "#Motivación", "#Productividad"]
            },
            "afternoon": {
                "hook": "🌤️ Buenas tardes!",
                "tone": "profesional",
                "message": "Aprovecha tu tarde con",
                "hashtags": ["#Productividad", "#Trabajo", "#Eficiencia"]
            },
            "evening": {
                "hook": "🌆 Buenas tardes!",
                "tone": "relajado",
                "message": "Termina tu día con",
                "hashtags": ["#Tarde", "#Descanso", "#Bienestar"]
            },
            "night": {
                "hook": "🌙 Buenas noches!",
                "tone": "reflexivo",
                "message": "Prepárate para mañana con",
                "hashtags": ["#Noche", "#Reflexión", "#Preparación"]
            }
        }
        
        template = time_templates.get(time_of_day.lower(), time_templates["afternoon"])
        
        # Generar post con tono específico
        post = self.generate_post(
            platform=platform,
            post_type="demo",
            product_name=product_name,
            target_audience=target_audience,
            tone=template["tone"]
        )
        
        # Personalizar con contexto temporal
        post["time_context"] = time_of_day
        post["time_hook"] = template["hook"]
        post["hashtags"] = template["hashtags"] + post.get("hashtags", [])[:25]
        
        return post
    
    def setup_ab_test(
        self,
        base_post: Dict[str, Any],
        variations: List[Dict[str, Any]],
        test_name: str,
        duration_days: int = 7
    ) -> Dict[str, Any]:
        """
        Configura un test A/B automatizado
        
        Args:
            base_post: Post base
            variations: Lista de variaciones a testear
            test_name: Nombre del test
            duration_days: Duración del test en días
        
        Returns:
            Configuración del test A/B
        """
        test_config = {
            "test_id": f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_name": test_name,
            "base_post": base_post,
            "variations": variations,
            "total_variations": len(variations) + 1,  # +1 para base
            "duration_days": duration_days,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "status": "active",
            "metrics": {
                "impressions": {},
                "engagement": {},
                "conversions": {}
            },
            "winner": None,
            "created_at": datetime.now().isoformat()
        }
        
        return test_config
    
    def track_ab_test_performance(
        self,
        test_config: Dict[str, Any],
        performance_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Trackea y analiza performance de test A/B
        
        Args:
            test_config: Configuración del test
            performance_data: Datos de performance por variación
        
        Returns:
            Análisis del test con ganador
        """
        # Calcular métricas por variación
        variation_scores = {}
        
        for var_id, perf in performance_data.items():
            engagement_rate = perf.get("engagement_rate", 0)
            conversion_rate = perf.get("conversion_rate", 0)
            ctr = perf.get("ctr", 0)
            
            # Score combinado (engagement 40%, conversión 40%, CTR 20%)
            combined_score = (
                engagement_rate * 0.4 +
                conversion_rate * 0.4 +
                ctr * 0.2
            )
            
            variation_scores[var_id] = {
                "engagement_rate": engagement_rate,
                "conversion_rate": conversion_rate,
                "ctr": ctr,
                "combined_score": combined_score,
                "performance": perf
            }
        
        # Determinar ganador
        winner = max(variation_scores.items(), key=lambda x: x[1]["combined_score"])
        
        # Actualizar test config
        test_config["metrics"] = variation_scores
        test_config["winner"] = winner[0]
        test_config["winner_score"] = winner[1]["combined_score"]
        test_config["status"] = "completed"
        test_config["completed_at"] = datetime.now().isoformat()
        
        # Generar recomendaciones
        recommendations = [
            f"Variación ganadora: {winner[0]} con score de {winner[1]['combined_score']:.2f}",
            f"Engagement rate: {winner[1]['engagement_rate']:.2f}%",
            f"Conversion rate: {winner[1]['conversion_rate']:.2f}%"
        ]
        
        test_config["recommendations"] = recommendations
        
        return test_config
    
    def generate_seasonal_content(
        self,
        season: str,
        product_name: str,
        target_audience: str,
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        Genera contenido estacional
        
        Args:
            season: Estación (primavera, verano, otoño, invierno)
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            platform: Plataforma
        
        Returns:
            Post estacional
        """
        seasonal_themes = {
            "primavera": {
                "emoji": "🌸",
                "theme": "renovación y crecimiento",
                "hashtags": ["#Primavera", "#Renovación", "#Crecimiento"]
            },
            "verano": {
                "emoji": "☀️",
                "theme": "energía y acción",
                "hashtags": ["#Verano", "#Energía", "#Acción"]
            },
            "otoño": {
                "emoji": "🍂",
                "theme": "reflexión y preparación",
                "hashtags": ["#Otoño", "#Reflexión", "#Preparación"]
            },
            "invierno": {
                "emoji": "❄️",
                "theme": "planificación y nuevos comienzos",
                "hashtags": ["#Invierno", "#Planificación", "#NuevosComienzos"]
            }
        }
        
        theme = seasonal_themes.get(season.lower(), seasonal_themes["primavera"])
        
        # Generar post con tema estacional
        custom_data = {
            "season_theme": theme["theme"],
            "season_emoji": theme["emoji"]
        }
        
        post = self.generate_post(
            platform=platform,
            post_type="demo",
            product_name=product_name,
            target_audience=target_audience,
            custom_data=custom_data
        )
        
        post["season"] = season
        post["seasonal_theme"] = theme["theme"]
        post["hashtags"] = theme["hashtags"] + post.get("hashtags", [])[:25]
        
        return post
    
    def create_content_bundle(
        self,
        product_name: str,
        target_audience: str,
        platforms: List[str] = None,
        include_formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Crea un bundle completo de contenido para una campaña
        
        Args:
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            platforms: Plataformas (default: todas)
            include_formats: Formatos a incluir (default: todos)
        
        Returns:
            Bundle completo de contenido
        """
        if platforms is None:
            platforms = [p.value for p in Platform]
        
        if include_formats is None:
            include_formats = ["feed", "reel", "carousel", "story"]
        
        bundle = {
            "product_name": product_name,
            "target_audience": target_audience,
            "created_at": datetime.now().isoformat(),
            "content": {}
        }
        
        # Generar para cada tipo de post
        for post_type in ["teaser", "demo", "offer"]:
            bundle["content"][post_type] = {}
            
            # Generar para cada plataforma
            for platform in platforms:
                try:
                    post = self.generate_post(
                        platform=platform,
                        post_type=post_type,
                        product_name=product_name,
                        target_audience=target_audience
                    )
                    
                    # Generar formatos adicionales
                    formats = self.generate_content_formats(
                        base_post=post,
                        formats=include_formats
                    )
                    
                    # Generar Stories
                    stories = self.generate_story_content(
                        platform=platform,
                        post_type=post_type,
                        product_name=product_name,
                        target_audience=target_audience,
                        base_post=post
                    )
                    
                    bundle["content"][post_type][platform] = {
                        "post": post,
                        "formats": {k: asdict(v) for k, v in formats.items()},
                        "stories": asdict(stories)
                    }
                except Exception as e:
                    logger.error(f"Error generando bundle para {platform}: {e}")
        
        return bundle
    
    def predict_performance(
        self,
        post: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> PredictiveInsights:
        """
        Predice el rendimiento de un post antes de publicarlo
        
        Args:
            post: Post a analizar
            historical_data: Datos históricos (opcional)
        
        Returns:
            Insights predictivos
        """
        if not historical_data:
            historical_data = self.generation_history
        
        analysis = post.get("analysis", {})
        engagement_score = analysis.get("engagement_score", 50)
        conversion_potential = analysis.get("conversion_potential", 50)
        
        # Calcular predicciones basadas en score
        base_reach = 1000  # Base estimada
        predicted_reach = int(base_reach * (engagement_score / 50))
        predicted_engagement = engagement_score * 10  # Estimación
        predicted_conversions = int(predicted_reach * (conversion_potential / 100) * 0.02)
        
        # Ajustar basado en historial si está disponible
        if historical_data:
            successful_posts = [
                p for p in historical_data
                if p.get("performance", {}).get("engagement_rate", 0) > 5.0
            ]
            
            if successful_posts:
                avg_reach = sum(
                    p.get("performance", {}).get("reach", 0)
                    for p in successful_posts
                ) / len(successful_posts)
                
                # Ajustar predicción si el post es similar a exitosos
                if engagement_score > 70:
                    predicted_reach = int(avg_reach * 1.2)
                    predicted_engagement = int(avg_reach * 0.08)
        
        # Calcular confidence score
        confidence_factors = []
        if analysis.get("has_numbers"):
            confidence_factors.append(0.1)
        if analysis.get("has_cta"):
            confidence_factors.append(0.15)
        if analysis.get("has_questions"):
            confidence_factors.append(0.1)
        if engagement_score > 70:
            confidence_factors.append(0.2)
        
        confidence_score = min(1.0, 0.5 + sum(confidence_factors))
        
        # Identificar risk factors
        risk_factors = []
        if engagement_score < 50:
            risk_factors.append("Bajo engagement score predicho")
        if not analysis.get("has_cta"):
            risk_factors.append("Falta call-to-action")
        if not analysis.get("has_numbers"):
            risk_factors.append("Falta métricas específicas")
        
        # Calcular probabilidad de éxito
        success_probability = (
            engagement_score / 100 * 0.5 +
            conversion_potential / 100 * 0.3 +
            confidence_score * 0.2
        )
        
        # Recomendaciones
        recommendations = []
        if engagement_score < 70:
            recommendations.append("Mejorar engagement score antes de publicar")
        if not analysis.get("has_cta"):
            recommendations.append("Agregar call-to-action claro")
        if predicted_reach < 500:
            recommendations.append("Considerar optimizar para mayor alcance")
        
        return PredictiveInsights(
            predicted_engagement=round(predicted_engagement, 2),
            predicted_reach=predicted_reach,
            predicted_conversions=predicted_conversions,
            confidence_score=round(confidence_score, 2),
            risk_factors=risk_factors,
            success_probability=round(success_probability * 100, 2),
            recommendations=recommendations
        )
    
    def publish_to_social_media(
        self,
        post: Dict[str, Any],
        platform: str,
        schedule_time: Optional[datetime] = None,
        auto_publish: bool = False
    ) -> PublishingResult:
        """
        Publica post a redes sociales (requiere configuración de API)
        
        Args:
            post: Post a publicar
            platform: Plataforma objetivo
            schedule_time: Hora programada (opcional)
            auto_publish: Publicar inmediatamente si es True
        
        Returns:
            Resultado de la publicación
        """
        # Verificar configuración de API
        if platform not in self.api_configs:
            return PublishingResult(
                success=False,
                post_id=None,
                platform=platform,
                published_at=None,
                url=None,
                error=f"API no configurada para {platform}",
                metrics=None
            )
        
        try:
            # En producción, aquí se haría la llamada real a la API
            # Por ahora, simulamos la publicación
            
            if schedule_time and not auto_publish:
                # Programar publicación
                status = "scheduled"
                published_at = schedule_time.isoformat()
            else:
                # Publicar inmediatamente
                status = "published"
                published_at = datetime.now().isoformat()
            
            # Simular respuesta de API
            post_id = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            url = f"https://{platform}.com/posts/{post_id}"
            
            # Guardar en historial
            self.save_to_history(post, {
                "status": status,
                "post_id": post_id,
                "published_at": published_at
            })
            
            return PublishingResult(
                success=True,
                post_id=post_id,
                platform=platform,
                published_at=published_at,
                url=url,
                error=None,
                metrics={
                    "status": status,
                    "scheduled": schedule_time is not None
                }
            )
            
        except Exception as e:
            logger.error(f"Error publicando a {platform}: {e}")
            return PublishingResult(
                success=False,
                post_id=None,
                platform=platform,
                published_at=None,
                url=None,
                error=str(e),
                metrics=None
            )
    
    def track_performance(
        self,
        post_id: str,
        platform: str,
        metrics: Dict[str, Any]
    ) -> ContentPerformance:
        """
        Trackea el rendimiento de un post publicado
        
        Args:
            post_id: ID del post
            platform: Plataforma
            metrics: Métricas de rendimiento
        
        Returns:
            Objeto ContentPerformance
        """
        impressions = metrics.get("impressions", 0)
        reach = metrics.get("reach", 0)
        engagement = metrics.get("engagement", 0)
        clicks = metrics.get("clicks", 0)
        conversions = metrics.get("conversions", 0)
        revenue = metrics.get("revenue", 0.0)
        
        engagement_rate = (engagement / reach * 100) if reach > 0 else 0
        
        # Calcular performance score
        performance_score = (
            engagement_rate * 0.4 +
            (clicks / impressions * 100) * 0.3 +
            (conversions / clicks * 100) * 0.3
        ) if impressions > 0 else 0
        
        # Analizar tendencias
        trends = {
            "engagement_trend": "increasing" if engagement_rate > 5 else "stable",
            "reach_trend": "increasing" if reach > impressions * 0.8 else "stable",
            "conversion_trend": "increasing" if conversions > 0 else "stable"
        }
        
        performance = ContentPerformance(
            post_id=post_id,
            platform=platform,
            impressions=impressions,
            reach=reach,
            engagement=engagement,
            engagement_rate=round(engagement_rate, 2),
            clicks=clicks,
            conversions=conversions,
            revenue=revenue,
            performance_score=round(performance_score, 2),
            trends=trends
        )
        
        # Guardar en tracking
        self.performance_tracking[post_id] = performance
        
        return performance
    
    def generate_performance_dashboard(
        self,
        posts: List[Dict[str, Any]],
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """
        Genera dashboard de métricas de rendimiento
        
        Args:
            posts: Lista de posts con métricas
            time_period: Período de tiempo
        
        Returns:
            Dashboard con métricas agregadas
        """
        if not posts:
            return {
                "total_posts": 0,
                "metrics": {},
                "trends": {},
                "recommendations": []
            }
        
        # Métricas agregadas
        total_impressions = sum(p.get("performance", {}).get("impressions", 0) for p in posts)
        total_reach = sum(p.get("performance", {}).get("reach", 0) for p in posts)
        total_engagement = sum(p.get("performance", {}).get("engagement", 0) for p in posts)
        total_clicks = sum(p.get("performance", {}).get("clicks", 0) for p in posts)
        total_conversions = sum(p.get("performance", {}).get("conversions", 0) for p in posts)
        total_revenue = sum(p.get("performance", {}).get("revenue", 0.0) for p in posts)
        
        avg_engagement_rate = (
            sum(p.get("performance", {}).get("engagement_rate", 0) for p in posts) / len(posts)
            if posts else 0
        )
        
        # Análisis por plataforma
        platform_metrics = {}
        for post in posts:
            platform = post.get("platform", "unknown")
            if platform not in platform_metrics:
                platform_metrics[platform] = {
                    "posts": 0,
                    "total_engagement": 0,
                    "avg_engagement_rate": 0
                }
            
            platform_metrics[platform]["posts"] += 1
            platform_metrics[platform]["total_engagement"] += post.get("performance", {}).get("engagement", 0)
        
        # Calcular promedios por plataforma
        for platform, metrics in platform_metrics.items():
            platform_posts = [p for p in posts if p.get("platform") == platform]
            if platform_posts:
                metrics["avg_engagement_rate"] = (
                    sum(p.get("performance", {}).get("engagement_rate", 0) for p in platform_posts) / len(platform_posts)
                )
        
        # Identificar mejor y peor performer
        best_post = max(
            posts,
            key=lambda p: p.get("performance", {}).get("engagement_rate", 0)
        ) if posts else None
        
        worst_post = min(
            posts,
            key=lambda p: p.get("performance", {}).get("engagement_rate", 0)
        ) if posts else None
        
        # Recomendaciones
        recommendations = []
        if avg_engagement_rate < 5:
            recommendations.append("Engagement rate bajo - Revisar estrategia de contenido")
        
        best_platform = max(
            platform_metrics.items(),
            key=lambda x: x[1]["avg_engagement_rate"]
        )[0] if platform_metrics else None
        
        if best_platform:
            recommendations.append(
                f"Plataforma '{best_platform}' tiene mejor rendimiento - Priorizar contenido aquí"
            )
        
        return {
            "total_posts": len(posts),
            "time_period": time_period,
            "metrics": {
                "total_impressions": total_impressions,
                "total_reach": total_reach,
                "total_engagement": total_engagement,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_revenue": round(total_revenue, 2),
                "avg_engagement_rate": round(avg_engagement_rate, 2)
            },
            "platform_breakdown": platform_metrics,
            "best_performer": {
                "post_id": best_post.get("metadata", {}).get("generated_at") if best_post else None,
                "engagement_rate": best_post.get("performance", {}).get("engagement_rate", 0) if best_post else 0,
                "platform": best_post.get("platform") if best_post else None
            },
            "worst_performer": {
                "post_id": worst_post.get("metadata", {}).get("generated_at") if worst_post else None,
                "engagement_rate": worst_post.get("performance", {}).get("engagement_rate", 0) if worst_post else 0,
                "platform": worst_post.get("platform") if worst_post else None
            },
            "trends": {
                "engagement_trend": "increasing" if avg_engagement_rate > 5 else "stable",
                "best_platform": best_platform
            },
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    
    def export_dashboard_html(
        self,
        dashboard: Dict[str, Any],
        output_file: str = "dashboard.html"
    ) -> str:
        """
        Exporta dashboard a HTML interactivo
        
        Args:
            dashboard: Dashboard generado
            output_file: Archivo de salida
        
        Returns:
            Ruta del archivo generado
        """
        metrics = dashboard.get("metrics", {})
        platform_breakdown = dashboard.get("platform_breakdown", {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dashboard de Performance - Posts</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .recommendations {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        }}
        .recommendations h3 {{
            margin-bottom: 15px;
            color: #856404;
        }}
        .recommendations ul {{
            list-style: none;
        }}
        .recommendations li {{
            padding: 8px 0;
            color: #856404;
        }}
        .recommendations li:before {{
            content: "→ ";
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Performance</h1>
            <p>Período: {dashboard.get('time_period', 'N/A')} | Total Posts: {dashboard.get('total_posts', 0)}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_impressions', 0):,}</div>
                <div class="metric-label">Impressions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_reach', 0):,}</div>
                <div class="metric-label">Reach</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_engagement', 0):,}</div>
                <div class="metric-label">Engagement</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('avg_engagement_rate', 0):.2f}%</div>
                <div class="metric-label">Avg Engagement Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_clicks', 0):,}</div>
                <div class="metric-label">Clicks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('total_conversions', 0):,}</div>
                <div class="metric-label">Conversions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${metrics.get('total_revenue', 0):,.2f}</div>
                <div class="metric-label">Revenue</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Performance por Plataforma</h3>
            <canvas id="platformChart" width="400" height="200"></canvas>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendaciones</h3>
            <ul>
"""
        
        for rec in dashboard.get("recommendations", []):
            html += f"                <li>{rec}</li>\n"
        
        html += """            </ul>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('platformChart').getContext('2d');
        const platformData = """ + json.dumps(platform_breakdown) + """;
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(platformData),
                datasets: [{
                    label: 'Avg Engagement Rate %',
                    data: Object.values(platformData).map(p => p.avg_engagement_rate),
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>"""
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
    
    def generate_automated_report(
        self,
        posts: List[Dict[str, Any]],
        report_type: str = "weekly"
    ) -> Dict[str, Any]:
        """
        Genera reporte automatizado de rendimiento
        
        Args:
            posts: Lista de posts con métricas
            report_type: Tipo de reporte (daily, weekly, monthly)
        
        Returns:
            Reporte completo
        """
        dashboard = self.generate_performance_dashboard(posts, time_period=report_type)
        
        # Análisis adicional
        top_performers = sorted(
            posts,
            key=lambda p: p.get("performance", {}).get("engagement_rate", 0),
            reverse=True
        )[:5]
        
        # Insights clave
        insights = []
        if dashboard.get("metrics", {}).get("avg_engagement_rate", 0) > 7:
            insights.append("Engagement rate excelente - Mantener estrategia actual")
        elif dashboard.get("metrics", {}).get("avg_engagement_rate", 0) < 3:
            insights.append("Engagement rate bajo - Revisar contenido y horarios")
        
        best_platform = dashboard.get("trends", {}).get("best_platform")
        if best_platform:
            insights.append(f"Plataforma '{best_platform}' destaca - Aumentar contenido aquí")
        
        return {
            "report_type": report_type,
            "period": datetime.now().strftime("%Y-%m-%d"),
            "summary": dashboard,
            "top_performers": [
                {
                    "post_id": p.get("metadata", {}).get("generated_at"),
                    "platform": p.get("platform"),
                    "engagement_rate": p.get("performance", {}).get("engagement_rate", 0),
                    "reach": p.get("performance", {}).get("reach", 0)
                }
                for p in top_performers
            ],
            "insights": insights,
            "next_steps": dashboard.get("recommendations", []),
            "generated_at": datetime.now().isoformat()
        }
    
    def setup_api_config(
        self,
        platform: str,
        api_key: str,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        """
        Configura credenciales de API para publicación automática
        
        Args:
            platform: Plataforma
            api_key: API key
            api_secret: API secret (opcional)
            access_token: Access token (opcional)
        """
        self.api_configs[platform] = {
            "api_key": api_key,
            "api_secret": api_secret or "",
            "access_token": access_token or "",
            "configured_at": datetime.now().isoformat()
        }
        logger.info(f"API configurada para {platform}")
    
    def batch_publish(
        self,
        posts: List[Dict[str, Any]],
        schedule: bool = False,
        schedule_times: Optional[List[datetime]] = None
    ) -> List[PublishingResult]:
        """
        Publica múltiples posts en batch
        
        Args:
            posts: Lista de posts a publicar
            schedule: Si es True, programa las publicaciones
            schedule_times: Lista de horarios (debe coincidir con posts)
        
        Returns:
            Lista de resultados de publicación
        """
        results = []
        
        for i, post in enumerate(posts):
            platform = post.get("platform", "instagram")
            schedule_time = schedule_times[i] if schedule_times and i < len(schedule_times) else None
            
            result = self.publish_to_social_media(
                post=post,
                platform=platform,
                schedule_time=schedule_time,
                auto_publish=not schedule
            )
            results.append(result)
        
        return results
    
    def generate_creative_brief(
        self,
        post: Dict[str, Any],
        brand_guidelines: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """
        Genera brief creativo para diseñadores
        
        Args:
            post: Post generado
            brand_guidelines: Guías de marca (opcional)
        
        Returns:
            Brief creativo completo
        """
        post_type = post.get("post_type", "demo")
        platform = post.get("platform", "instagram")
        audience = post.get("metadata", {}).get("target_audience", "general")
        
        # Objetivo de campaña
        objectives = {
            "teaser": "Generar expectativa y FOMO",
            "demo": "Demostrar valor y beneficios",
            "offer": "Maximizar conversiones"
        }
        campaign_objective = objectives.get(post_type, "Engagement")
        
        # Mensaje clave
        key_message = post.get("post_content", "")[:100] + "..."
        
        # Estilo visual según plataforma
        visual_styles = {
            "instagram": {
                "style": "Moderno, vibrante, visual",
                "mood": "Energético y atractivo",
                "aesthetic": "Clean, minimalista con toques de color"
            },
            "linkedin": {
                "style": "Profesional, corporativo",
                "mood": "Confiable y autoritario",
                "aesthetic": "Elegante, sobrio, datos visuales"
            },
            "tiktok": {
                "style": "Dinámico, auténtico",
                "mood": "Divertido y relajado",
                "aesthetic": "Casual, real, movimiento"
            }
        }
        visual_style = visual_styles.get(platform, visual_styles["instagram"])
        
        # Paleta de colores
        color_palettes = {
            "instagram": ["#667eea", "#764ba2", "#f093fb", "#4facfe"],
            "linkedin": ["#0077b5", "#000000", "#ffffff", "#e7e7e7"],
            "tiktok": ["#000000", "#ffffff", "#ff0050", "#00f2ea"]
        }
        color_palette = color_palettes.get(platform, ["#667eea", "#764ba2"])
        
        # Tipografía
        typography = {
            "primary_font": "Sans-serif moderno" if platform != "linkedin" else "Serif profesional",
            "heading_size": "Large, bold",
            "body_size": "Medium, readable",
            "style": "Clean, legible"
        }
        
        # Requisitos de imagen
        image_requirements = []
        if post_type == "teaser":
            image_requirements = [
                "Imagen misteriosa con producto parcialmente visible",
                "Efecto de desvelado o sombra",
                "Fondo oscuro con gradiente",
                "Texto superpuesto legible"
            ]
        elif post_type == "demo":
            image_requirements = [
                "Screenshots o fotos del producto en acción",
                "Before/After si aplica",
                "Elementos visuales que muestren beneficios",
                "Personas usando el producto (opcional)"
            ]
        else:  # offer
            image_requirements = [
                "Diseño de urgencia con colores vibrantes",
                "Precio destacado visualmente",
                "Timer o countdown si aplica",
                "Badge de 'OFERTA LIMITADA'"
            ]
        
        # Requisitos de video
        video_requirements = []
        if post_type == "demo":
            video_requirements = [
                "Duración: 30-60 segundos",
                "Hook en primeros 3 segundos",
                "Demostración clara del producto",
                "CTA visual al final",
                "Música upbeat y moderna"
            ]
        
        # Especificaciones de contenido
        content_specs = {
            "platform": platform,
            "format": "Square (1:1)" if platform == "instagram" else "16:9",
            "max_text_length": self.platform_limits[Platform(platform)]["max_length"],
            "hashtags_count": len(post.get("hashtags", [])),
            "cta_required": True
        }
        
        return CreativeBrief(
            campaign_objective=campaign_objective,
            target_audience=audience,
            key_message=key_message,
            visual_style=visual_style,
            color_palette=color_palette,
            typography=typography,
            image_requirements=image_requirements,
            video_requirements=video_requirements,
            brand_guidelines=brand_guidelines or {},
            content_specs=content_specs
        )
    
    def analyze_visual_assets(
        self,
        post: Dict[str, Any],
        asset_type: str = "image"
    ) -> VisualAssetAnalysis:
        """
        Analiza y recomienda assets visuales para un post
        
        Args:
            post: Post generado
            asset_type: Tipo de asset (image, video, graphic)
        
        Returns:
            Análisis y recomendaciones de assets visuales
        """
        platform = post.get("platform", "instagram")
        post_type = post.get("post_type", "demo")
        
        # Dimensiones recomendadas
        dimensions_map = {
            "instagram": {"width": 1080, "height": 1080},
            "linkedin": {"width": 1200, "height": 627},
            "tiktok": {"width": 1080, "height": 1920},
            "facebook": {"width": 1200, "height": 630}
        }
        recommended_dimensions = dimensions_map.get(platform, {"width": 1080, "height": 1080})
        
        # Sugerencias de color
        color_suggestions = []
        if post_type == "offer":
            color_suggestions = ["#FF0000", "#FF6B00", "#FFD700"]  # Rojo, naranja, dorado
        elif post_type == "teaser":
            color_suggestions = ["#667eea", "#764ba2", "#000000"]  # Púrpura, negro
        else:
            color_suggestions = ["#4facfe", "#00f2ea", "#ffffff"]  # Azul, cian, blanco
        
        # Tips de composición
        composition_tips = []
        if asset_type == "image":
            composition_tips = [
                "Usar regla de tercios para elementos principales",
                "Mantener espacio para texto superpuesto",
                "Contraste alto para legibilidad",
                "Enfoque en producto o mensaje clave"
            ]
        elif asset_type == "video":
            composition_tips = [
                "Hook visual en primeros 3 segundos",
                "Transiciones suaves entre escenas",
                "Texto superpuesto para usuarios sin sonido",
                "CTA visual claro al final"
            ]
        
        # Sugerencias de texto superpuesto
        post_content = post.get("post_content", "")
        first_line = post_content.split('\n')[0] if post_content else ""
        text_overlay_suggestions = [
            first_line[:30] + "..." if len(first_line) > 30 else first_line,
            "Hook principal del post",
            "Beneficio clave destacado",
            "Call-to-action"
        ]
        
        # Recomendaciones de estilo
        style_recommendations = []
        if platform == "instagram":
            style_recommendations = [
                "Estilo moderno y minimalista",
                "Colores vibrantes pero no saturados",
                "Tipografía legible y moderna",
                "Espacio en blanco para respiración"
            ]
        elif platform == "linkedin":
            style_recommendations = [
                "Estilo profesional y corporativo",
                "Colores de marca consistentes",
                "Datos visuales y gráficos",
                "Tipografía serif para títulos"
            ]
        
        # Score de accesibilidad
        accessibility_score = 70.0  # Base
        if len(color_suggestions) >= 3:
            accessibility_score += 10
        if asset_type == "image":
            accessibility_score += 10  # Imágenes más accesibles que videos
        
        # Potencial de engagement
        engagement_potential = post.get("analysis", {}).get("engagement_score", 50) * 0.6
        if asset_type == "video":
            engagement_potential += 20  # Videos tienen más engagement
        if post_type == "offer":
            engagement_potential += 10
        
        return VisualAssetAnalysis(
            asset_type=asset_type,
            recommended_dimensions=recommended_dimensions,
            color_suggestions=color_suggestions,
            composition_tips=composition_tips,
            text_overlay_suggestions=text_overlay_suggestions,
            style_recommendations=style_recommendations,
            accessibility_score=min(100, accessibility_score),
            engagement_potential=min(100, engagement_potential)
        )
    
    def generate_collaboration_workflow(
        self,
        post: Dict[str, Any],
        collaborators: List[str],
        approval_required: bool = True
    ) -> CollaborationInvite:
        """
        Crea workflow de colaboración para revisión de posts
        
        Args:
            post: Post a revisar
            collaborators: Lista de colaboradores
            approval_required: Si requiere aprobación
        
        Returns:
            Invitación de colaboración
        """
        post_id = post.get("metadata", {}).get("generated_at", datetime.now().isoformat())
        
        permissions = {
            "can_edit": True,
            "can_comment": True,
            "can_approve": approval_required,
            "can_publish": False
        }
        
        return CollaborationInvite(
            post_id=post_id,
            collaborators=collaborators,
            permissions=permissions,
            review_status="pending",
            comments=[],
            approval_required=approval_required
        )
    
    def calculate_advanced_roi(
        self,
        posts: List[Dict[str, Any]],
        time_period_days: int = 30,
        projection_days: int = 90
    ) -> Dict[str, Any]:
        """
        Calcula ROI avanzado con proyecciones futuras
        
        Args:
            posts: Lista de posts con métricas
            time_period_days: Período de análisis
            projection_days: Días para proyección
        
        Returns:
            Análisis de ROI avanzado con proyecciones
        """
        if not posts:
            return {
                "current_roi": 0,
                "projected_roi": 0,
                "trends": {},
                "recommendations": []
            }
        
        # Calcular métricas actuales
        total_cost = sum(p.get("performance", {}).get("campaign_cost", 0) for p in posts)
        total_revenue = sum(p.get("performance", {}).get("revenue", 0) for p in posts)
        total_impressions = sum(p.get("performance", {}).get("impressions", 0) for p in posts)
        total_conversions = sum(p.get("performance", {}).get("conversions", 0) for p in posts)
        
        current_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        # Calcular tasa de crecimiento
        if len(posts) > 1:
            # Ordenar por fecha
            sorted_posts = sorted(
                posts,
                key=lambda p: p.get("metadata", {}).get("generated_at", "")
            )
            
            first_half = sorted_posts[:len(sorted_posts)//2]
            second_half = sorted_posts[len(sorted_posts)//2:]
            
            first_half_roi = (
                sum(p.get("performance", {}).get("revenue", 0) - p.get("performance", {}).get("campaign_cost", 0)
                    for p in first_half) / sum(p.get("performance", {}).get("campaign_cost", 1) for p in first_half) * 100
                if sum(p.get("performance", {}).get("campaign_cost", 0) for p in first_half) > 0 else 0
            )
            
            second_half_roi = (
                sum(p.get("performance", {}).get("revenue", 0) - p.get("performance", {}).get("campaign_cost", 0)
                    for p in second_half) / sum(p.get("performance", {}).get("campaign_cost", 1) for p in second_half) * 100
                if sum(p.get("performance", {}).get("campaign_cost", 0) for p in second_half) > 0 else 0
            )
            
            growth_rate = ((second_half_roi - first_half_roi) / first_half_roi * 100) if first_half_roi > 0 else 0
        else:
            growth_rate = 0
        
        # Proyección futura
        projection_multiplier = projection_days / time_period_days
        projected_revenue = total_revenue * projection_multiplier * (1 + growth_rate / 100)
        projected_cost = total_cost * projection_multiplier
        projected_roi = ((projected_revenue - projected_cost) / projected_cost * 100) if projected_cost > 0 else 0
        
        # Análisis de tendencias
        trends = {
            "roi_trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable",
            "growth_rate": round(growth_rate, 2),
            "conversion_trend": "improving" if total_conversions > 0 else "needs_optimization"
        }
        
        # Recomendaciones
        recommendations = []
        if current_roi < 100:
            recommendations.append("ROI bajo - Optimizar targeting y contenido")
        if growth_rate < 0:
            recommendations.append("ROI decreciendo - Revisar estrategia urgentemente")
        if total_conversions == 0:
            recommendations.append("Sin conversiones - Mejorar CTAs y landing pages")
        
        return {
            "current_period": {
                "days": time_period_days,
                "total_cost": round(total_cost, 2),
                "total_revenue": round(total_revenue, 2),
                "roi": round(current_roi, 2),
                "total_impressions": total_impressions,
                "total_conversions": total_conversions
            },
            "projection": {
                "days": projection_days,
                "projected_cost": round(projected_cost, 2),
                "projected_revenue": round(projected_revenue, 2),
                "projected_roi": round(projected_roi, 2),
                "confidence": 0.75 if len(posts) >= 5 else 0.5
            },
            "trends": trends,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat()
        }
    
    def generate_live_event_content(
        self,
        event_name: str,
        event_type: str,
        product_name: str,
        target_audience: str,
        live_updates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Genera contenido para eventos en vivo
        
        Args:
            event_name: Nombre del evento
            event_type: Tipo (webinar, launch, demo_live, etc.)
            product_name: Nombre del producto
            target_audience: Audiencia
            live_updates: Actualizaciones en vivo (opcional)
        
        Returns:
            Contenido para evento en vivo
        """
        event_templates = {
            "webinar": {
                "hook": f"🔴 EN VIVO: {event_name}",
                "message": "Únete ahora - Estamos en vivo",
                "hashtags": ["#EnVivo", "#Webinar", "#Live"]
            },
            "launch": {
                "hook": f"🚀 LANZAMIENTO EN VIVO: {event_name}",
                "message": "Sigue el lanzamiento en tiempo real",
                "hashtags": ["#Lanzamiento", "#EnVivo", "#Live"]
            },
            "demo_live": {
                "hook": f"📺 DEMO EN VIVO: {product_name}",
                "message": "Mira cómo funciona en tiempo real",
                "hashtags": ["#Demo", "#EnVivo", "#Live"]
            }
        }
        
        template = event_templates.get(event_type.lower(), event_templates["webinar"])
        
        # Generar post base
        post = self.generate_post(
            platform="instagram",
            post_type="demo",
            product_name=product_name,
            target_audience=target_audience
        )
        
        # Personalizar para evento en vivo
        live_content = f"""{template['hook']}

{template['message']}

📅 {event_name}
⏰ En vivo ahora

{post.get('post_content', '')}

🔴 Únete al stream
💬 Comenta tus preguntas
📱 Comparte con tus amigos

{chr(10).join(template['hashtags'])}"""
        
        post["post_content"] = live_content
        post["full_post"] = live_content
        post["event_type"] = event_type
        post["is_live"] = True
        post["live_updates"] = live_updates or []
        
        return post
    
    def setup_smart_alerts(
        self,
        post: Dict[str, Any],
        alert_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configura alertas inteligentes para posts
        
        Args:
            post: Post a monitorear
            alert_rules: Reglas de alerta
        
        Returns:
            Configuración de alertas
        """
        post_id = post.get("metadata", {}).get("generated_at", datetime.now().isoformat())
        
        default_rules = {
            "engagement_threshold": 5.0,  # %
            "reach_threshold": 1000,
            "conversion_threshold": 10,
            "negative_sentiment_threshold": 0.3,
            "alert_channels": ["email", "slack"]
        }
        
        rules = {**default_rules, **alert_rules}
        
        alert_config = {
            "post_id": post_id,
            "platform": post.get("platform"),
            "rules": rules,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "alerts_triggered": []
        }
        
        return alert_config
    
    def check_alerts(
        self,
        alert_config: Dict[str, Any],
        current_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Verifica si se deben disparar alertas
        
        Args:
            alert_config: Configuración de alertas
            current_metrics: Métricas actuales
        
        Returns:
            Lista de alertas disparadas
        """
        alerts = []
        rules = alert_config.get("rules", {})
        
        engagement_rate = current_metrics.get("engagement_rate", 0)
        reach = current_metrics.get("reach", 0)
        conversions = current_metrics.get("conversions", 0)
        sentiment = current_metrics.get("sentiment_score", 0)
        
        # Verificar cada regla
        if engagement_rate < rules.get("engagement_threshold", 5.0):
            alerts.append({
                "type": "low_engagement",
                "severity": "warning",
                "message": f"Engagement rate bajo: {engagement_rate:.2f}%",
                "threshold": rules.get("engagement_threshold", 5.0),
                "current_value": engagement_rate
            })
        
        if reach < rules.get("reach_threshold", 1000):
            alerts.append({
                "type": "low_reach",
                "severity": "info",
                "message": f"Reach bajo: {reach}",
                "threshold": rules.get("reach_threshold", 1000),
                "current_value": reach
            })
        
        if conversions < rules.get("conversion_threshold", 10):
            alerts.append({
                "type": "low_conversions",
                "severity": "warning",
                "message": f"Conversiones bajas: {conversions}",
                "threshold": rules.get("conversion_threshold", 10),
                "current_value": conversions
            })
        
        if sentiment < -rules.get("negative_sentiment_threshold", 0.3):
            alerts.append({
                "type": "negative_sentiment",
                "severity": "critical",
                "message": f"Sentimiento negativo detectado: {sentiment:.2f}",
                "threshold": -rules.get("negative_sentiment_threshold", 0.3),
                "current_value": sentiment
            })
        
        # Actualizar alertas disparadas
        if alerts:
            alert_config["alerts_triggered"].extend(alerts)
        
        return alerts
    
    def generate_content_from_event(
        self,
        event_data: Dict[str, Any],
        product_name: str,
        target_audience: str
    ) -> Dict[str, Any]:
        """
        Genera contenido basado en eventos del mundo real
        
        Args:
            event_data: Datos del evento (tendencias, noticias, etc.)
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
        
        Returns:
            Post generado desde evento
        """
        event_type = event_data.get("type", "trending")
        event_topic = event_data.get("topic", "")
        event_hashtags = event_data.get("hashtags", [])
        
        # Generar contenido relacionado con el evento
        if event_type == "trending":
            hook = f"🔥 {event_topic} está trending"
            message = f"¿Cómo se relaciona {product_name} con {event_topic}?"
        elif event_type == "news":
            hook = f"📰 {event_topic}"
            message = f"En relación a las últimas noticias sobre {event_topic}..."
        else:
            hook = f"💡 {event_topic}"
            message = f"Descubre cómo {product_name} puede ayudarte con {event_topic}"
        
        # Generar post
        post = self.generate_post(
            platform="instagram",
            post_type="demo",
            product_name=product_name,
            target_audience=target_audience,
            custom_data={
                "event_hook": hook,
                "event_message": message,
                "event_topic": event_topic
            }
        )
        
        # Agregar hashtags del evento
        post["hashtags"] = event_hashtags + post.get("hashtags", [])[:20]
        post["event_related"] = True
        post["event_data"] = event_data
        
        return post
    
    def optimize_for_accessibility(
        self,
        post: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiza post para accesibilidad
        
        Args:
            post: Post a optimizar
        
        Returns:
            Post optimizado con mejoras de accesibilidad
        """
        optimized = post.copy()
        post_content = post.get("post_content", "")
        
        # Mejoras de accesibilidad
        improvements = []
        
        # Verificar contraste de texto (simulado)
        if len(post_content) > 200:
            improvements.append("Contenido largo - Considerar dividir en secciones")
        
        # Agregar alt text sugerido
        optimized["accessibility"] = {
            "alt_text_suggested": f"Post sobre {post.get('metadata', {}).get('product_name', 'producto')}",
            "has_emojis": bool(re.findall(r'[😀-🙏🌀-🗿]', post_content)),
            "readability_score": post.get("analysis", {}).get("readability_score", 0),
            "improvements": improvements,
            "wcag_compliance": "AA" if post.get("analysis", {}).get("readability_score", 0) > 80 else "A"
        }
        
        return optimized
    
    def generate_repurposing_suggestions(
        self,
        post: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Genera sugerencias de repurposing para otras plataformas
        
        Args:
            post: Post original
            target_platforms: Plataformas objetivo
        
        Returns:
            Dict con versiones repurposed por plataforma
        """
        repurposed = {}
        original_content = post.get("post_content", "")
        
        for platform in target_platforms:
            if platform == post.get("platform"):
                continue  # Skip misma plataforma
            
            # Adaptar contenido
            adapted_content = original_content
            
            # Ajustes por plataforma
            if platform == "twitter":
                # Twitter: más corto
                adapted_content = original_content[:200] + "..."
            elif platform == "linkedin":
                # LinkedIn: más profesional
                adapted_content = original_content.replace("🔥", "").replace("⚡", "")
            
            # Generar post adaptado
            try:
                repurposed_post = self.generate_post(
                    platform=platform,
                    post_type=post.get("post_type", "demo"),
                    product_name=post.get("metadata", {}).get("product_name", "Producto"),
                    target_audience=post.get("metadata", {}).get("target_audience", "audiencia"),
                    custom_data={"repurposed_from": post.get("platform")}
                )
                
                # Usar contenido adaptado
                repurposed_post["post_content"] = adapted_content
                repurposed_post["full_post"] = adapted_content
                repurposed_post["repurposed"] = True
                repurposed_post["original_post_id"] = post.get("metadata", {}).get("generated_at")
                
                repurposed[platform] = repurposed_post
            except Exception as e:
                logger.error(f"Error repurposing para {platform}: {e}")
        
        return repurposed
    
    def generate_image_suggestions_with_ai(
        self,
        post: Dict[str, Any],
        style: str = "modern"
    ) -> Dict[str, Any]:
        """
        Genera sugerencias de imágenes usando IA
        
        Args:
            post: Post generado
            style: Estilo de imagen (modern, professional, creative, etc.)
        
        Returns:
            Sugerencias de imágenes con prompts para IA
        """
        post_type = post.get("post_type", "demo")
        product_name = post.get("metadata", {}).get("product_name", "producto")
        platform = post.get("platform", "instagram")
        
        # Prompts para generación de imágenes
        image_prompts = {
            "teaser": f"Mysterious, elegant image of {product_name} partially revealed, dark background with gradient, cinematic lighting, modern minimalist style",
            "demo": f"Professional product photography of {product_name} in action, clean background, bright lighting, showcasing key features, {style} style",
            "offer": f"Vibrant promotional image for {product_name}, bold colors, discount badge, urgent design, eye-catching composition, {style} style"
        }
        
        base_prompt = image_prompts.get(post_type, image_prompts["demo"])
        
        # Variaciones de prompts
        variations = [
            base_prompt,
            f"{base_prompt}, high quality, 4K resolution, professional photography",
            f"{base_prompt}, social media optimized, square format, engaging composition",
            f"{base_prompt}, brand colors, consistent style, marketing material"
        ]
        
        # Especificaciones técnicas
        specs = {
            "platform": platform,
            "dimensions": self.analyze_visual_assets(post, "image").recommended_dimensions,
            "format": "JPG" if platform == "instagram" else "PNG",
            "color_space": "sRGB",
            "resolution": "1080x1080" if platform == "instagram" else "1200x630"
        }
        
        return {
            "prompts": variations,
            "primary_prompt": base_prompt,
            "style": style,
            "specifications": specs,
            "suggested_tools": ["DALL-E", "Midjourney", "Stable Diffusion", "Canva AI"],
            "generated_at": datetime.now().isoformat()
        }
    
    def analyze_competitor_content_realtime(
        self,
        competitor_handles: List[str],
        platform: str,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analiza contenido de competidores en tiempo real
        
        Args:
            competitor_handles: Lista de handles de competidores
            platform: Plataforma a analizar
            keywords: Keywords para filtrar (opcional)
        
        Returns:
            Análisis de competencia en tiempo real
        """
        # En producción, esto se conectaría a APIs de redes sociales
        # Por ahora, simulamos el análisis
        
        analysis = {
            "competitors_analyzed": len(competitor_handles),
            "platform": platform,
            "analysis_date": datetime.now().isoformat(),
            "insights": []
        }
        
        # Simular insights
        for handle in competitor_handles:
            competitor_insights = {
                "handle": handle,
                "avg_engagement_rate": round(random.uniform(3.0, 8.0), 2),
                "posting_frequency": f"{random.randint(3, 7)} posts/week",
                "best_performing_content": {
                    "type": random.choice(["carousel", "video", "single_image"]),
                    "avg_engagement": random.randint(500, 5000)
                },
                "hashtag_strategy": {
                    "avg_hashtags": random.randint(5, 15),
                    "top_hashtags": [f"#{handle}", "#marketing", "#business"]
                },
                "content_themes": ["product_demo", "testimonials", "tips"],
                "posting_times": ["09:00", "13:00", "18:00"]
            }
            analysis["insights"].append(competitor_insights)
        
        # Recomendaciones basadas en análisis
        avg_engagement = sum(
            c["avg_engagement_rate"] for c in analysis["insights"]
        ) / len(analysis["insights"]) if analysis["insights"] else 0
        
        recommendations = []
        if avg_engagement > 6.0:
            recommendations.append("Competidores tienen alto engagement - Analizar su estrategia de contenido")
        
        best_content_type = max(
            (c["best_performing_content"]["type"] for c in analysis["insights"]),
            key=lambda x: sum(
                c["best_performing_content"]["avg_engagement"]
                for c in analysis["insights"]
                if c["best_performing_content"]["type"] == x
            )
        ) if analysis["insights"] else "video"
        
        recommendations.append(f"Tipo de contenido más exitoso: {best_content_type}")
        
        analysis["recommendations"] = recommendations
        analysis["benchmark_engagement"] = round(avg_engagement, 2)
        
        return analysis
    
    def generate_auto_responses(
        self,
        post: Dict[str, Any],
        comment_types: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Genera respuestas automáticas para diferentes tipos de comentarios
        
        Args:
            post: Post generado
            comment_types: Tipos de comentarios (question, positive, negative, etc.)
        
        Returns:
            Respuestas automáticas por tipo de comentario
        """
        if comment_types is None:
            comment_types = ["question", "positive", "negative", "neutral", "pricing"]
        
        product_name = post.get("metadata", {}).get("product_name", "nuestro producto")
        responses = {}
        
        # Respuestas para preguntas
        if "question" in comment_types:
            responses["question"] = [
                f"¡Gracias por tu interés en {product_name}! Te puedo ayudar con eso. ¿Podrías contarme más sobre lo que necesitas?",
                f"Excelente pregunta sobre {product_name}. Déjame darte más detalles...",
                f"Me encanta que preguntes sobre {product_name}. Aquí tienes la información que necesitas..."
            ]
        
        # Respuestas positivas
        if "positive" in comment_types:
            responses["positive"] = [
                f"¡Muchas gracias por tu comentario! Nos alegra saber que {product_name} te está ayudando.",
                f"¡Genial! Nos encanta escuchar experiencias positivas con {product_name}. ¡Gracias por compartir!",
                f"¡Gracias por tu feedback positivo sobre {product_name}! Significa mucho para nosotros."
            ]
        
        # Respuestas negativas
        if "negative" in comment_types:
            responses["negative"] = [
                f"Lamentamos que tu experiencia con {product_name} no haya sido la esperada. ¿Podrías contarnos más detalles para poder ayudarte?",
                f"Gracias por tu feedback. Nos tomamos muy en serio los comentarios y queremos mejorar. ¿Cómo podemos ayudarte?",
                f"Entendemos tu preocupación. Por favor, contáctanos directamente para resolver esto juntos."
            ]
        
        # Respuestas sobre precios
        if "pricing" in comment_types:
            responses["pricing"] = [
                f"Gracias por tu interés en {product_name}. Te envío la información de precios por DM.",
                f"Para información detallada sobre precios de {product_name}, visita nuestro sitio web o contáctanos.",
                f"¡Claro! Te comparto la información de precios. ¿Prefieres que te la envíe por DM?"
            ]
        
        # Respuestas neutrales
        if "neutral" in comment_types:
            responses["neutral"] = [
                f"Gracias por tu comentario sobre {product_name}. ¿Hay algo específico en lo que podamos ayudarte?",
                f"¡Hola! Gracias por interactuar con nuestro contenido sobre {product_name}.",
                f"Apreciamos tu interés en {product_name}. ¿Tienes alguna pregunta?"
            ]
        
        return responses
    
    def categorize_and_tag_posts(
        self,
        posts: List[Dict[str, Any]],
        custom_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Categoriza y etiqueta posts automáticamente
        
        Args:
            posts: Lista de posts a categorizar
            custom_tags: Tags personalizados (opcional)
        
        Returns:
            Posts categorizados y etiquetados
        """
        categorized = {
            "by_type": {},
            "by_platform": {},
            "by_audience": {},
            "by_performance": {},
            "tags": {}
        }
        
        for post in posts:
            post_type = post.get("post_type", "unknown")
            platform = post.get("platform", "unknown")
            audience = post.get("metadata", {}).get("target_audience", "general")
            performance = post.get("performance", {})
            engagement_rate = performance.get("engagement_rate", 0)
            
            # Categorizar por tipo
            if post_type not in categorized["by_type"]:
                categorized["by_type"][post_type] = []
            categorized["by_type"][post_type].append(post)
            
            # Categorizar por plataforma
            if platform not in categorized["by_platform"]:
                categorized["by_platform"][platform] = []
            categorized["by_platform"][platform].append(post)
            
            # Categorizar por audiencia
            if audience not in categorized["by_audience"]:
                categorized["by_audience"][audience] = []
            categorized["by_audience"][audience].append(post)
            
            # Categorizar por performance
            if engagement_rate >= 7.0:
                perf_category = "high_performance"
            elif engagement_rate >= 4.0:
                perf_category = "medium_performance"
            else:
                perf_category = "low_performance"
            
            if perf_category not in categorized["by_performance"]:
                categorized["by_performance"][perf_category] = []
            categorized["by_performance"][perf_category].append(post)
            
            # Generar tags automáticos
            tags = []
            tags.append(post_type)
            tags.append(platform)
            tags.append(audience)
            if post.get("is_live"):
                tags.append("live")
            if post.get("event_related"):
                tags.append("event_related")
            if post.get("repurposed"):
                tags.append("repurposed")
            if custom_tags:
                tags.extend(custom_tags)
            
            post_id = post.get("metadata", {}).get("generated_at", datetime.now().isoformat())
            categorized["tags"][post_id] = tags
        
        return categorized
    
    def semantic_search_posts(
        self,
        query: str,
        posts: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica de posts históricos
        
        Args:
            query: Consulta de búsqueda
            posts: Lista de posts a buscar
            top_k: Número de resultados a retornar
        
        Returns:
            Posts más relevantes según la consulta
        """
        # Búsqueda semántica simple basada en palabras clave
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_posts = []
        
        for post in posts:
            score = 0.0
            content = post.get("post_content", "").lower()
            product_name = post.get("metadata", {}).get("product_name", "").lower()
            audience = post.get("metadata", {}).get("target_audience", "").lower()
            hashtags = " ".join(post.get("hashtags", [])).lower()
            
            # Calcular relevancia
            full_text = f"{content} {product_name} {audience} {hashtags}"
            
            for word in query_words:
                # Contar ocurrencias
                count = full_text.count(word)
                score += count * 1.0
                
                # Bonus por coincidencia exacta en producto o audiencia
                if word in product_name:
                    score += 5.0
                if word in audience:
                    score += 3.0
                if word in hashtags:
                    score += 2.0
            
            # Normalizar por longitud
            score = score / max(len(full_text.split()), 1)
            
            scored_posts.append((score, post))
        
        # Ordenar por score y retornar top_k
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        
        return [post for score, post in scored_posts[:top_k]]
    
    def integrate_with_crm(
        self,
        post: Dict[str, Any],
        crm_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integra post con datos de CRM
        
        Args:
            post: Post generado
            crm_data: Datos del CRM (leads, customers, etc.)
        
        Returns:
            Post enriquecido con datos de CRM
        """
        # Enriquecer post con datos de CRM
        enriched_post = post.copy()
        
        # Agregar segmentación de audiencia desde CRM
        if "audience_segments" in crm_data:
            enriched_post["crm_segments"] = crm_data["audience_segments"]
        
        # Agregar información de leads
        if "leads" in crm_data:
            enriched_post["target_leads"] = crm_data["leads"]
            enriched_post["estimated_reach"] = len(crm_data["leads"])
        
        # Agregar información de clientes
        if "customers" in crm_data:
            enriched_post["target_customers"] = crm_data["customers"]
        
        # Agregar métricas de CRM
        enriched_post["crm_metrics"] = {
            "total_leads": crm_data.get("total_leads", 0),
            "total_customers": crm_data.get("total_customers", 0),
            "conversion_rate": crm_data.get("conversion_rate", 0),
            "last_updated": datetime.now().isoformat()
        }
        
        return enriched_post
    
    def generate_email_campaign_content(
        self,
        post: Dict[str, Any],
        email_type: str = "newsletter"
    ) -> Dict[str, Any]:
        """
        Genera contenido de email marketing basado en post
        
        Args:
            post: Post generado
            email_type: Tipo de email (newsletter, promotion, announcement)
        
        Returns:
            Contenido de email listo para usar
        """
        product_name = post.get("metadata", {}).get("product_name", "producto")
        post_content = post.get("post_content", "")
        
        email_templates = {
            "newsletter": {
                "subject": f"Actualización: {product_name}",
                "preheader": post_content[:100] + "...",
                "greeting": "Hola,",
                "body": f"""
                <p>Esperamos que estés bien.</p>
                <p>{post_content}</p>
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                """,
                "cta_text": "Ver más",
                "closing": "Saludos,<br>El equipo"
            },
            "promotion": {
                "subject": f"Oferta especial: {product_name}",
                "preheader": "No te pierdas esta oportunidad",
                "greeting": "Hola,",
                "body": f"""
                <p>Tenemos una oferta especial para ti.</p>
                <p>{post_content}</p>
                <p>Esta oferta es por tiempo limitado.</p>
                """,
                "cta_text": "Aprovechar oferta",
                "closing": "Gracias,<br>El equipo"
            },
            "announcement": {
                "subject": f"Anuncio importante: {product_name}",
                "preheader": "Tenemos noticias emocionantes",
                "greeting": "Hola,",
                "body": f"""
                <p>Queremos compartir contigo una noticia importante.</p>
                <p>{post_content}</p>
                <p>Estamos emocionados de compartir esto contigo.</p>
                """,
                "cta_text": "Saber más",
                "closing": "Saludos,<br>El equipo"
            }
        }
        
        template = email_templates.get(email_type, email_templates["newsletter"])
        
        return {
            "email_type": email_type,
            "subject": template["subject"],
            "preheader": template["preheader"],
            "html_body": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .cta-button {{ display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <p>{template["greeting"]}</p>
                    {template["body"]}
                    <p><a href="#" class="cta-button">{template["cta_text"]}</a></p>
                    <p>{template["closing"]}</p>
                </div>
            </body>
            </html>
            """,
            "plain_text": f"""
            {template["greeting"]}
            
            {post_content}
            
            {template["cta_text"]}: [URL]
            
            {template["closing"]}
            """,
            "generated_at": datetime.now().isoformat()
        }
    
    def setup_notification_system(
        self,
        notification_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configura sistema de notificaciones
        
        Args:
            notification_config: Configuración de notificaciones
        
        Returns:
            Configuración de sistema de notificaciones
        """
        default_config = {
            "channels": ["email", "slack"],
            "triggers": {
                "post_published": True,
                "high_engagement": True,
                "low_performance": True,
                "negative_sentiment": True
            },
            "recipients": [],
            "frequency": "realtime"  # realtime, daily, weekly
        }
        
        config = {**default_config, **notification_config}
        config["configured_at"] = datetime.now().isoformat()
        config["active"] = True
        
        return config
    
    def generate_analytics_report_advanced(
        self,
        posts: List[Dict[str, Any]],
        report_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera reporte de analytics avanzado
        
        Args:
            posts: Lista de posts con métricas
            report_config: Configuración del reporte
        
        Returns:
            Reporte avanzado de analytics
        """
        # Generar dashboard base
        dashboard = self.generate_performance_dashboard(
            posts,
            time_period=report_config.get("time_period", "30d")
        )
        
        # Análisis avanzado
        advanced_analysis = {
            "engagement_trends": {
                "daily_avg": {},
                "weekly_avg": {},
                "growth_rate": 0.0
            },
            "content_performance": {
                "best_content_type": None,
                "best_platform": None,
                "best_time_to_post": None
            },
            "audience_insights": {
                "top_segments": [],
                "engagement_by_segment": {}
            },
            "roi_analysis": self.calculate_advanced_roi(
                posts,
                time_period_days=report_config.get("time_period_days", 30)
            ),
            "recommendations": []
        }
        
        # Agregar recomendaciones estratégicas
        if dashboard.get("metrics", {}).get("avg_engagement_rate", 0) < 5:
            advanced_analysis["recommendations"].append(
                "Considerar revisar estrategia de contenido - Engagement bajo"
            )
        
        return {
            "dashboard": dashboard,
            "advanced_analysis": advanced_analysis,
            "generated_at": datetime.now().isoformat(),
            "report_config": report_config
        }
    
    def generate_video_script_advanced(
        self,
        post: Dict[str, Any],
        video_length: int = 60,
        style: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Genera script de video avanzado con timing y elementos visuales
        
        Args:
            post: Post generado
            video_length: Duración en segundos
            style: Estilo del video (engaging, educational, promotional)
        
        Returns:
            Script completo de video con timing
        """
        product_name = post.get("metadata", {}).get("product_name", "producto")
        post_type = post.get("post_type", "demo")
        platform = post.get("platform", "instagram")
        
        # Estructura del video
        hook_duration = 3
        intro_duration = 5
        main_content_duration = video_length - hook_duration - intro_duration - 10
        cta_duration = 5
        outro_duration = 2
        
        # Generar script por secciones
        scripts = {
            "hook": {
                "duration": hook_duration,
                "text": f"¿Sabías que {product_name} puede cambiar tu forma de trabajar?",
                "visual": "Close-up del producto con efecto zoom",
                "music": "Upbeat, attention-grabbing",
                "text_overlay": f"Descubre {product_name}"
            },
            "intro": {
                "duration": intro_duration,
                "text": f"Hoy te voy a mostrar cómo {product_name} puede ayudarte a alcanzar tus objetivos.",
                "visual": "Wide shot del producto en contexto",
                "music": "Transition to main theme",
                "text_overlay": None
            },
            "main_content": {
                "duration": main_content_duration,
                "sections": []
            },
            "cta": {
                "duration": cta_duration,
                "text": f"No esperes más. Prueba {product_name} hoy mismo.",
                "visual": "Producto destacado con CTA overlay",
                "music": "Build up to climax",
                "text_overlay": "¡Prueba ahora!"
            },
            "outro": {
                "duration": outro_duration,
                "text": "Gracias por ver. ¡Nos vemos en el próximo video!",
                "visual": "Logo o marca",
                "music": "Fade out",
                "text_overlay": "Síguenos para más"
            }
        }
        
        # Generar secciones del contenido principal
        if post_type == "demo":
            scripts["main_content"]["sections"] = [
                {
                    "time": f"0:00-0:{main_content_duration//3}",
                    "text": "Aquí está el problema que resuelve nuestro producto",
                    "visual": "Problem visualization"
                },
                {
                    "time": f"0:{main_content_duration//3}-0:{(main_content_duration*2)//3}",
                    "text": "Así es como funciona nuestra solución",
                    "visual": "Product demo"
                },
                {
                    "time": f"0:{(main_content_duration*2)//3}-0:{main_content_duration}",
                    "text": "Estos son los resultados que puedes esperar",
                    "visual": "Results showcase"
                }
            ]
        
        return {
            "total_duration": video_length,
            "platform": platform,
            "style": style,
            "script": scripts,
            "production_notes": [
                "Usar iluminación profesional",
                "Audio claro y sin ruido de fondo",
                "Transiciones suaves entre escenas",
                "Texto superpuesto legible",
                "Música sin copyright o con licencia"
            ],
            "equipment_needed": [
                "Cámara o smartphone de alta calidad",
                "Micrófono externo",
                "Iluminación",
                "Trípode",
                "Software de edición"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def analyze_influencer_collaboration(
        self,
        influencer_data: Dict[str, Any],
        product_name: str,
        campaign_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Analiza potencial de colaboración con influencers
        
        Args:
            influencer_data: Datos del influencer
            product_name: Nombre del producto
            campaign_goals: Objetivos de la campaña
        
        Returns:
            Análisis de colaboración con recomendaciones
        """
        follower_count = influencer_data.get("followers", 0)
        avg_engagement_rate = influencer_data.get("avg_engagement_rate", 0)
        audience_match = influencer_data.get("audience_match", 0)  # 0-100
        content_quality = influencer_data.get("content_quality_score", 0)  # 0-100
        
        # Calcular score de colaboración
        collaboration_score = (
            (follower_count / 100000) * 0.2 +  # Normalizado
            avg_engagement_rate * 0.3 +
            (audience_match / 100) * 0.3 +
            (content_quality / 100) * 0.2
        ) * 100
        
        # Recomendaciones
        recommendations = []
        if collaboration_score > 70:
            recommendations.append("Excelente match - Colaboración recomendada")
        elif collaboration_score > 50:
            recommendations.append("Buen match - Considerar colaboración")
        else:
            recommendations.append("Match bajo - Revisar antes de colaborar")
        
        # Tipo de contenido recomendado
        if avg_engagement_rate > 5:
            recommended_content = "Video o Reel"
        elif avg_engagement_rate > 3:
            recommended_content = "Carousel o Post múltiple"
        else:
            recommended_content = "Post simple"
        
        # Estrategia de colaboración
        collaboration_strategy = {
            "content_type": recommended_content,
            "posting_schedule": "1-2 posts durante la campaña",
            "hashtags": ["#sponsored", "#ad", f"#{product_name.lower().replace(' ', '')}"],
            "disclosure": "Requerido por ley",
            "compensation": "Negociar según alcance y engagement"
        }
        
        return {
            "influencer": influencer_data.get("name", "Unknown"),
            "collaboration_score": round(collaboration_score, 2),
            "metrics": {
                "followers": follower_count,
                "avg_engagement_rate": avg_engagement_rate,
                "audience_match": audience_match,
                "content_quality": content_quality
            },
            "recommendations": recommendations,
            "collaboration_strategy": collaboration_strategy,
            "estimated_reach": int(follower_count * (avg_engagement_rate / 100)),
            "estimated_engagement": int(follower_count * (avg_engagement_rate / 100) * 0.1),
            "campaign_fit": "high" if collaboration_score > 70 else "medium" if collaboration_score > 50 else "low",
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_community_content(
        self,
        post: Dict[str, Any],
        community_type: str = "discord"
    ) -> Dict[str, Any]:
        """
        Genera contenido para comunidades (Discord, Slack, etc.)
        
        Args:
            post: Post generado
            community_type: Tipo de comunidad (discord, slack, telegram)
        
        Returns:
            Contenido adaptado para comunidad
        """
        product_name = post.get("metadata", {}).get("product_name", "producto")
        post_content = post.get("post_content", "")
        
        community_templates = {
            "discord": {
                "format": "markdown",
                "header": f"## 🚀 {product_name}",
                "content": post_content,
                "footer": "💬 ¿Qué opinas? ¡Comparte tus pensamientos!",
                "channels": ["#announcements", "#general", "#product-updates"]
            },
            "slack": {
                "format": "slack_markdown",
                "header": f"*{product_name}*",
                "content": post_content,
                "footer": ":speech_balloon: ¿Alguna pregunta?",
                "channels": ["#announcements", "#product"]
            },
            "telegram": {
                "format": "html",
                "header": f"<b>{product_name}</b>",
                "content": post_content,
                "footer": "💬 Comenta abajo",
                "channels": ["@channel"]
            }
        }
        
        template = community_templates.get(community_type.lower(), community_templates["discord"])
        
        return {
            "community_type": community_type,
            "formatted_content": f"""
{template["header"]}

{template["content"]}

{template["footer"]}
            """.strip(),
            "channels": template["channels"],
            "format": template["format"],
            "engagement_tips": [
                "Publicar en horarios de alta actividad",
                "Usar menciones para usuarios clave",
                "Responder rápidamente a comentarios",
                "Crear hilos de discusión"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def analyze_hashtag_trends_realtime(
        self,
        hashtags: List[str],
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        Analiza tendencias de hashtags en tiempo real
        
        Args:
            hashtags: Lista de hashtags a analizar
            platform: Plataforma
        
        Returns:
            Análisis de tendencias de hashtags
        """
        # En producción, esto se conectaría a APIs de redes sociales
        # Por ahora, simulamos el análisis
        
        analysis = {
            "platform": platform,
            "analyzed_at": datetime.now().isoformat(),
            "hashtags": {}
        }
        
        for hashtag in hashtags:
            # Simular datos de tendencia
            trend_data = {
                "current_usage": random.randint(1000, 100000),
                "growth_rate": round(random.uniform(-10, 50), 2),  # %
                "peak_hours": ["09:00", "13:00", "18:00"],
                "competition_level": random.choice(["low", "medium", "high"]),
                "trending": random.choice([True, False]),
                "estimated_reach": random.randint(5000, 50000),
                "best_day_to_use": random.choice(["Monday", "Wednesday", "Friday"])
            }
            
            analysis["hashtags"][hashtag] = trend_data
        
        # Recomendaciones
        trending_hashtags = [
            h for h, data in analysis["hashtags"].items()
            if data.get("trending", False)
        ]
        
        recommendations = []
        if trending_hashtags:
            recommendations.append(f"Hashtags trending: {', '.join(trending_hashtags)}")
        
        low_competition = [
            h for h, data in analysis["hashtags"].items()
            if data.get("competition_level") == "low"
        ]
        if low_competition:
            recommendations.append(f"Hashtags con baja competencia: {', '.join(low_competition)}")
        
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def generate_podcast_script(
        self,
        post: Dict[str, Any],
        episode_length: int = 30
    ) -> Dict[str, Any]:
        """
        Genera script de podcast basado en post
        
        Args:
            post: Post generado
            episode_length: Duración en minutos
        
        Returns:
            Script completo de podcast
        """
        product_name = post.get("metadata", {}).get("product_name", "producto")
        post_content = post.get("post_content", "")
        
        # Estructura del podcast
        intro_duration = 2
        main_content_duration = episode_length - intro_duration - 3
        outro_duration = 1
        
        script = {
            "episode_title": f"Todo sobre {product_name}",
            "duration_minutes": episode_length,
            "sections": {
                "intro": {
                    "duration": intro_duration,
                    "script": f"""
                    Bienvenidos a nuestro podcast. Hoy hablaremos sobre {product_name}.
                    
                    {post_content[:200]}...
                    
                    Si te interesa saber más, quédate hasta el final.
                    """.strip()
                },
                "main_content": {
                    "duration": main_content_duration,
                    "script": f"""
                    {post_content}
                    
                    Déjame profundizar en los puntos clave:
                    
                    1. El problema que resuelve
                    2. Cómo funciona la solución
                    3. Los beneficios principales
                    4. Casos de uso reales
                    """.strip(),
                    "talking_points": [
                        "Problema que resuelve el producto",
                        "Características principales",
                        "Beneficios para el usuario",
                        "Ejemplos de uso",
                        "Testimonios o casos de éxito"
                    ]
                },
                "outro": {
                    "duration": outro_duration,
                    "script": f"""
                    Gracias por escuchar. Si te gustó este episodio sobre {product_name},
                    compártelo con tus amigos y suscríbete para más contenido.
                    
                    Nos vemos en el próximo episodio.
                    """.strip()
                }
            },
            "production_notes": [
                "Grabar en ambiente silencioso",
                "Usar micrófono de calidad",
                "Editar pausas y errores",
                "Agregar música de fondo suave",
                "Incluir intro y outro musical"
            ],
            "promotion": {
                "social_media_posts": [
                    f"Nuevo episodio: Todo sobre {product_name}",
                    f"Escucha nuestro podcast sobre {product_name}"
                ],
                "hashtags": ["#podcast", "#marketing", f"#{product_name.lower().replace(' ', '')}"]
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return script
    
    def integrate_with_scheduling_tools(
        self,
        post: Dict[str, Any],
        tool: str = "buffer",
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Integra post con herramientas de scheduling
        
        Args:
            post: Post generado
            tool: Herramienta (buffer, hootsuite, later, etc.)
            schedule_time: Hora programada
        
        Returns:
            Configuración para herramienta de scheduling
        """
        if schedule_time is None:
            schedule_time = datetime.now() + timedelta(hours=1)
        
        integration_configs = {
            "buffer": {
                "format": "json",
                "payload": {
                    "text": post.get("post_content", ""),
                    "profile_ids": ["default"],
                    "scheduled_at": schedule_time.isoformat(),
                    "media": {
                        "photo": None,  # URL de imagen si está disponible
                        "thumbnail": None
                    }
                },
                "api_endpoint": "https://api.bufferapp.com/1/updates/create.json"
            },
            "hootsuite": {
                "format": "json",
                "payload": {
                    "text": post.get("post_content", ""),
                    "scheduledSendTime": schedule_time.isoformat(),
                    "socialProfileIds": ["default"],
                    "mediaUrls": []
                },
                "api_endpoint": "https://platform.hootsuite.com/v1/messages"
            },
            "later": {
                "format": "json",
                "payload": {
                    "media": [{
                        "text": post.get("post_content", ""),
                        "scheduled_at": schedule_time.isoformat()
                    }]
                },
                "api_endpoint": "https://api.later.com/v1/media"
            }
        }
        
        config = integration_configs.get(tool.lower(), integration_configs["buffer"])
        
        return {
            "tool": tool,
            "post_id": post.get("metadata", {}).get("generated_at"),
            "schedule_time": schedule_time.isoformat(),
            "integration_config": config,
            "status": "ready_to_schedule",
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_content_calendar_advanced(
        self,
        start_date: datetime,
        days: int = 30,
        products: List[str] = None,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Genera calendario de contenido avanzado con optimización
        
        Args:
            start_date: Fecha de inicio
            days: Número de días
            products: Lista de productos
            platforms: Lista de plataformas
        
        Returns:
            Calendario avanzado optimizado
        """
        if products is None:
            products = ["Producto Principal"]
        
        if platforms is None:
            platforms = ["instagram", "linkedin"]
        
        calendar = {
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(days=days)).isoformat(),
            "total_days": days,
            "schedule": [],
            "optimization": {
                "best_posting_times": {},
                "content_mix": {},
                "hashtag_strategy": {}
            }
        }
        
        current_date = start_date
        post_types = ["teaser", "demo", "offer"]
        
        for day in range(days):
            day_schedule = {
                "date": current_date.isoformat(),
                "day_of_week": current_date.strftime("%A"),
                "posts": []
            }
            
            # Generar posts para cada plataforma
            for platform in platforms:
                # Rotar tipos de posts
                post_type = post_types[day % len(post_types)]
                
                # Generar post
                try:
                    post = self.generate_post(
                        platform=platform,
                        post_type=post_type,
                        product_name=products[0],
                        target_audience="general"
                    )
                    
                    # Agregar horario óptimo
                    optimal_time = self.optimal_times.get(platform, {}).get("best", "09:00")
                    post["scheduled_time"] = optimal_time
                    
                    day_schedule["posts"].append({
                        "platform": platform,
                        "post_type": post_type,
                        "scheduled_time": optimal_time,
                        "post": post
                    })
                except Exception as e:
                    logger.error(f"Error generando post para calendario: {e}")
            
            calendar["schedule"].append(day_schedule)
            current_date += timedelta(days=1)
        
        # Agregar optimizaciones
        for platform in platforms:
            calendar["optimization"]["best_posting_times"][platform] = \
                self.optimal_times.get(platform, {}).get("best", "09:00")
        
        return calendar
    
    def generate_ab_test_ml_optimized(
        self,
        base_post: Dict[str, Any],
        variations: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Genera test A/B optimizado con machine learning
        
        Args:
            base_post: Post base
            variations: Variaciones a testear
            historical_data: Datos históricos para ML
        
        Returns:
            Test A/B optimizado con predicciones ML
        """
        test_config = self.setup_ab_test(
            base_post=base_post,
            variations=variations,
            test_name="ML_Optimized_Test",
            duration_days=7
        )
        
        # Predicciones ML basadas en historial
        ml_predictions = {}
        
        if historical_data:
            # Analizar patrones históricos
            successful_patterns = [
                p for p in historical_data
                if p.get("performance", {}).get("engagement_rate", 0) > 6.0
            ]
            
            if successful_patterns:
                # Extraer características de posts exitosos
                avg_hashtags = sum(
                    len(p.get("hashtags", [])) for p in successful_patterns
                ) / len(successful_patterns)
                
                avg_length = sum(
                    len(p.get("post_content", "")) for p in successful_patterns
                ) / len(successful_patterns)
                
                # Predecir performance de variaciones
                for i, variation in enumerate(variations):
                    var_hashtags = len(variation.get("hashtags", []))
                    var_length = len(variation.get("post_content", ""))
                    
                    # Score basado en similitud con posts exitosos
                    hashtag_score = 1.0 - abs(var_hashtags - avg_hashtags) / max(avg_hashtags, 1)
                    length_score = 1.0 - abs(var_length - avg_length) / max(avg_length, 1)
                    
                    ml_score = (hashtag_score + length_score) / 2
                    
                    ml_predictions[f"variation_{i+1}"] = {
                        "predicted_engagement": round(ml_score * 10, 2),
                        "confidence": round(ml_score * 100, 2),
                        "similarity_to_successful": round(ml_score * 100, 2)
                    }
        
        test_config["ml_predictions"] = ml_predictions
        test_config["ml_optimized"] = True
        
        return test_config
    
    def generate_unsplash_image_suggestions(
        self,
        post: Dict[str, Any],
        image_style: str = "professional"
    ) -> Dict[str, Any]:
        """
        Genera sugerencias de búsqueda para Unsplash/Pexels
        
        Args:
            post: Post generado
            image_style: Estilo de imagen
        
        Returns:
            Sugerencias de búsqueda de imágenes
        """
        product_name = post.get("metadata", {}).get("product_name", "producto")
        post_type = post.get("post_type", "demo")
        platform = post.get("platform", "instagram")
        
        # Keywords para búsqueda
        search_keywords = {
            "teaser": [f"{product_name}", "mystery", "dark", "gradient", "abstract"],
            "demo": [f"{product_name}", "professional", "workspace", "modern", "clean"],
            "offer": [f"{product_name}", "sale", "discount", "promotion", "vibrant"]
        }
        
        keywords = search_keywords.get(post_type, search_keywords["demo"])
        
        # Dimensiones según plataforma
        dimensions = {
            "instagram": {"width": 1080, "height": 1080},
            "linkedin": {"width": 1200, "height": 627},
            "tiktok": {"width": 1080, "height": 1920}
        }
        
        return {
            "search_keywords": keywords,
            "primary_keyword": keywords[0],
            "image_style": image_style,
            "dimensions": dimensions.get(platform, {"width": 1080, "height": 1080}),
            "suggested_sources": [
                "Unsplash",
                "Pexels",
                "Pixabay",
                "Freepik"
            ],
            "api_endpoints": {
                "unsplash": f"https://api.unsplash.com/search/photos?query={'+'.join(keywords)}",
                "pexels": f"https://api.pexels.com/v1/search?query={'+'.join(keywords)}"
            },
            "color_suggestions": ["#667eea", "#764ba2", "#f093fb"],
            "orientation": "square" if platform == "instagram" else "landscape",
            "generated_at": datetime.now().isoformat()
        }
    
    def analyze_comments_sentiment_realtime(
        self,
        post_id: str,
        comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza sentimiento de comentarios en tiempo real
        
        Args:
            post_id: ID del post
            comments: Lista de comentarios
        
        Returns:
            Análisis de sentimiento de comentarios
        """
        if not comments:
            return {
                "post_id": post_id,
                "total_comments": 0,
                "sentiment_breakdown": {},
                "recommendations": []
            }
        
        # Analizar sentimiento de cada comentario
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        questions_count = 0
        
        for comment in comments:
            comment_text = comment.get("text", "").lower()
            
            # Análisis simple de sentimiento
            positive_words = ["excelente", "genial", "me encanta", "gracias", "bueno", "perfecto"]
            negative_words = ["malo", "horrible", "no me gusta", "problema", "error", "mal"]
            question_words = ["?", "cómo", "cuándo", "dónde", "qué", "por qué"]
            
            sentiment = "neutral"
            if any(word in comment_text for word in positive_words):
                sentiment = "positive"
                positive_count += 1
            elif any(word in comment_text for word in negative_words):
                sentiment = "negative"
                negative_count += 1
            else:
                neutral_count += 1
            
            if any(word in comment_text for word in question_words):
                questions_count += 1
            
            sentiment_scores.append({
                "comment_id": comment.get("id"),
                "text": comment.get("text"),
                "sentiment": sentiment,
                "is_question": any(word in comment_text for word in question_words)
            })
        
        total = len(comments)
        sentiment_breakdown = {
            "positive": {
                "count": positive_count,
                "percentage": round((positive_count / total * 100), 2) if total > 0 else 0
            },
            "negative": {
                "count": negative_count,
                "percentage": round((negative_count / total * 100), 2) if total > 0 else 0
            },
            "neutral": {
                "count": neutral_count,
                "percentage": round((neutral_count / total * 100), 2) if total > 0 else 0
            },
            "questions": {
                "count": questions_count,
                "percentage": round((questions_count / total * 100), 2) if total > 0 else 0
            }
        }
        
        # Recomendaciones
        recommendations = []
        if negative_count > positive_count:
            recommendations.append("Alto número de comentarios negativos - Revisar y responder urgentemente")
        if questions_count > total * 0.3:
            recommendations.append("Muchas preguntas - Considerar crear FAQ o responder en masa")
        if positive_count > total * 0.7:
            recommendations.append("Excelente feedback positivo - Considerar destacar testimonios")
        
        return {
            "post_id": post_id,
            "total_comments": total,
            "sentiment_breakdown": sentiment_breakdown,
            "comment_analysis": sentiment_scores,
            "recommendations": recommendations,
            "overall_sentiment": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral",
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_newsletter_advanced(
        self,
        posts: List[Dict[str, Any]],
        newsletter_type: str = "weekly"
    ) -> Dict[str, Any]:
        """
        Genera newsletter avanzada con múltiples posts
        
        Args:
            posts: Lista de posts a incluir
            newsletter_type: Tipo de newsletter (weekly, monthly, campaign)
        
        Returns:
            Newsletter completa con HTML y texto plano
        """
        if not posts:
            return {
                "error": "No posts provided",
                "newsletter_type": newsletter_type
            }
        
        # Estructura de newsletter
        newsletter = {
            "type": newsletter_type,
            "subject": f"Newsletter {newsletter_type.capitalize()} - {datetime.now().strftime('%B %Y')}",
            "preheader": f"Resumen de nuestros mejores contenidos",
            "sections": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Agregar cada post como sección
        for i, post in enumerate(posts[:5]):  # Máximo 5 posts
            product_name = post.get("metadata", {}).get("product_name", "Producto")
            post_content = post.get("post_content", "")
            platform = post.get("platform", "instagram")
            
            section = {
                "title": f"{product_name} - {platform.capitalize()}",
                "content": post_content[:300] + "..." if len(post_content) > 300 else post_content,
                "cta": "Ver más",
                "image_placeholder": f"image_{i+1}.jpg"
            }
            newsletter["sections"].append(section)
        
        # Generar HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{newsletter['subject']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .section {{ margin: 30px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
                .cta-button {{ display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{newsletter['subject']}</h1>
                    <p>{newsletter['preheader']}</p>
                </div>
        """
        
        for section in newsletter["sections"]:
            html_content += f"""
                <div class="section">
                    <h2>{section['title']}</h2>
                    <p>{section['content']}</p>
                    <a href="#" class="cta-button">{section['cta']}</a>
                </div>
            """
        
        html_content += """
                <div class="footer">
                    <p>Gracias por suscribirte a nuestro newsletter</p>
                    <p><a href="#">Darse de baja</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Generar texto plano
        plain_text = f"{newsletter['subject']}\n\n{newsletter['preheader']}\n\n"
        for section in newsletter["sections"]:
            plain_text += f"{section['title']}\n{section['content']}\n{section['cta']}: [URL]\n\n"
        plain_text += "Gracias por suscribirte a nuestro newsletter"
        
        newsletter["html_content"] = html_content
        newsletter["plain_text"] = plain_text
        
        return newsletter
    
    def generate_webinar_content(
        self,
        webinar_topic: str,
        product_name: str,
        target_audience: str,
        duration: int = 60
    ) -> Dict[str, Any]:
        """
        Genera contenido completo para webinar
        
        Args:
            webinar_topic: Tema del webinar
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            duration: Duración en minutos
        
        Returns:
            Contenido completo del webinar
        """
        # Estructura del webinar
        intro_duration = 5
        main_content_duration = duration - intro_duration - 10
        qa_duration = 5
        outro_duration = 5
        
        webinar_content = {
            "title": f"Webinar: {webinar_topic}",
            "duration_minutes": duration,
            "target_audience": target_audience,
            "sections": {
                "intro": {
                    "duration": intro_duration,
                    "content": f"""
                    Bienvenidos al webinar sobre {webinar_topic}.
                    
                    Hoy aprenderemos:
                    - Cómo {product_name} puede ayudarte
                    - Casos de uso reales
                    - Mejores prácticas
                    - Q&A al final
                    
                    Empecemos.
                    """.strip()
                },
                "main_content": {
                    "duration": main_content_duration,
                    "slides": [
                        {
                            "title": f"Introducción a {product_name}",
                            "content": f"¿Qué es {product_name} y cómo puede ayudarte?",
                            "duration": main_content_duration // 4
                        },
                        {
                            "title": "Características principales",
                            "content": "Explorando las funcionalidades clave",
                            "duration": main_content_duration // 4
                        },
                        {
                            "title": "Casos de uso",
                            "content": "Ejemplos reales de implementación",
                            "duration": main_content_duration // 4
                        },
                        {
                            "title": "Próximos pasos",
                            "content": "Cómo empezar hoy mismo",
                            "duration": main_content_duration // 4
                        }
                    ]
                },
                "qa": {
                    "duration": qa_duration,
                    "content": "Sesión de preguntas y respuestas",
                    "prepared_questions": [
                        "¿Cuál es el precio?",
                        "¿Hay período de prueba?",
                        "¿Qué soporte ofrecen?",
                        "¿Cómo me registro?"
                    ]
                },
                "outro": {
                    "duration": outro_duration,
                    "content": f"""
                    Gracias por asistir al webinar sobre {webinar_topic}.
                    
                    Próximos pasos:
                    - Registrarse para prueba gratuita
                    - Descargar recursos adicionales
                    - Contactar con nuestro equipo
                    
                    Nos vemos en el próximo webinar.
                    """.strip()
                }
            },
            "promotion": {
                "social_media_posts": [
                    f"Webinar gratuito: {webinar_topic}",
                    f"Únete a nuestro webinar sobre {product_name}"
                ],
                "email_template": "webinar_invitation",
                "hashtags": ["#webinar", "#educación", f"#{product_name.lower().replace(' ', '')}"]
            },
            "resources": {
                "slides_template": "webinar_slides.pptx",
                "handout_template": "webinar_handout.pdf",
                "recording_notes": "Grabar para compartir después"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return webinar_content
    
    def export_to_powerpoint(
        self,
        posts: List[Dict[str, Any]],
        output_file: str = "campaign_presentation.pptx"
    ) -> Dict[str, Any]:
        """
        Exporta posts a formato PowerPoint
        
        Args:
            posts: Lista de posts a exportar
            output_file: Archivo de salida
        
        Returns:
            Información del archivo generado
        """
        # En producción, esto usaría python-pptx
        # Por ahora, generamos estructura
        
        presentation_structure = {
            "title": "Campaña de Marketing - Posts",
            "total_slides": len(posts) + 2,  # +2 para título y cierre
            "slides": []
        }
        
        # Slide de título
        presentation_structure["slides"].append({
            "slide_number": 1,
            "type": "title",
            "title": "Campaña de Marketing",
            "subtitle": f"{len(posts)} posts generados",
            "date": datetime.now().strftime("%B %Y")
        })
        
        # Slides de contenido
        for i, post in enumerate(posts, start=2):
            presentation_structure["slides"].append({
                "slide_number": i,
                "type": "content",
                "title": f"Post {i-1}: {post.get('post_type', 'demo').capitalize()}",
                "platform": post.get("platform", "instagram"),
                "content": post.get("post_content", "")[:200] + "...",
                "hashtags": ", ".join(post.get("hashtags", [])[:5]),
                "metrics": post.get("analysis", {})
            })
        
        # Slide de cierre
        presentation_structure["slides"].append({
            "slide_number": len(posts) + 2,
            "type": "closing",
            "title": "Gracias",
            "content": "¿Preguntas?",
            "contact": "contacto@empresa.com"
        })
        
        return {
            "output_file": output_file,
            "structure": presentation_structure,
            "format": "pptx",
            "note": "En producción, usar python-pptx para generar archivo real",
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_personalized_recommendations(
        self,
        user_profile: Dict[str, Any],
        historical_posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones personalizadas basadas en perfil de usuario
        
        Args:
            user_profile: Perfil del usuario
            historical_posts: Posts históricos del usuario
        
        Returns:
            Recomendaciones personalizadas
        """
        # Analizar preferencias del usuario
        preferred_platforms = user_profile.get("preferred_platforms", [])
        preferred_post_types = user_profile.get("preferred_post_types", [])
        target_audience = user_profile.get("target_audience", "general")
        
        # Analizar posts históricos exitosos
        successful_posts = [
            p for p in historical_posts
            if p.get("performance", {}).get("engagement_rate", 0) > 5.0
        ]
        
        recommendations = {
            "user_profile": user_profile,
            "recommendations": [],
            "insights": {},
            "next_steps": []
        }
        
        # Recomendaciones de plataforma
        if successful_posts:
            best_platform = max(
                set(p.get("platform") for p in successful_posts),
                key=lambda x: sum(
                    p.get("performance", {}).get("engagement_rate", 0)
                    for p in successful_posts
                    if p.get("platform") == x
                )
            )
            recommendations["recommendations"].append(
                f"Plataforma más exitosa: {best_platform} - Priorizar contenido aquí"
            )
        
        # Recomendaciones de tipo de post
        if successful_posts:
            best_type = max(
                set(p.get("post_type") for p in successful_posts),
                key=lambda x: sum(
                    p.get("performance", {}).get("engagement_rate", 0)
                    for p in successful_posts
                    if p.get("post_type") == x
                )
            )
            recommendations["recommendations"].append(
                f"Tipo de post más exitoso: {best_type} - Aumentar frecuencia"
            )
        
        # Insights
        avg_engagement = sum(
            p.get("performance", {}).get("engagement_rate", 0)
            for p in historical_posts
        ) / len(historical_posts) if historical_posts else 0
        
        recommendations["insights"] = {
            "avg_engagement_rate": round(avg_engagement, 2),
            "total_posts": len(historical_posts),
            "successful_posts": len(successful_posts),
            "success_rate": round((len(successful_posts) / len(historical_posts) * 100), 2) if historical_posts else 0
        }
        
        # Próximos pasos
        recommendations["next_steps"] = [
            "Generar más contenido del tipo más exitoso",
            "Optimizar para la plataforma con mejor rendimiento",
            "Experimentar con nuevos formatos",
            "Analizar competencia en plataformas exitosas"
        ]
        
        return recommendations
    
    def backup_posts_data(
        self,
        posts: List[Dict[str, Any]],
        backup_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Crea backup de posts con metadata completa
        
        Args:
            posts: Lista de posts a respaldar
            backup_format: Formato de backup (json, csv, sql)
        
        Returns:
            Información del backup creado
        """
        backup_data = {
            "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "total_posts": len(posts),
            "format": backup_format,
            "data": posts,
            "metadata": {
                "platforms": list(set(p.get("platform") for p in posts)),
                "post_types": list(set(p.get("post_type") for p in posts)),
                "date_range": {
                    "earliest": min(
                        (p.get("metadata", {}).get("generated_at", datetime.now().isoformat()) for p in posts),
                        default=datetime.now().isoformat()
                    ),
                    "latest": max(
                        (p.get("metadata", {}).get("generated_at", datetime.now().isoformat()) for p in posts),
                        default=datetime.now().isoformat()
                    )
                }
            }
        }
        
        return backup_data
    
    def restore_posts_from_backup(
        self,
        backup_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Restaura posts desde backup
        
        Args:
            backup_data: Datos del backup
        
        Returns:
            Información de restauración
        """
        posts = backup_data.get("data", [])
        
        restoration_info = {
            "restored_at": datetime.now().isoformat(),
            "backup_id": backup_data.get("backup_id"),
            "backup_created_at": backup_data.get("created_at"),
            "total_posts_restored": len(posts),
            "platforms_restored": list(set(p.get("platform") for p in posts)),
            "post_types_restored": list(set(p.get("post_type") for p in posts)),
            "status": "success" if posts else "failed",
            "restored_posts": posts
        }
        
        return restoration_info
    
    def generate_tiktok_content(
        self,
        product_name: str,
        target_audience: str,
        video_type: str = "trending"
    ) -> Dict[str, Any]:
        """
        Genera contenido específico para TikTok
        
        Args:
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            video_type: Tipo de video (trending, educational, behind_scenes, challenge)
        
        Returns:
            Contenido completo para TikTok
        """
        tiktok_templates = {
            "trending": {
                "hook": "POV: Descubres el mejor producto para...",
                "style": "Rápido, visual, trending",
                "hashtags": ["#fyp", "#viral", "#trending", "#foryou"]
            },
            "educational": {
                "hook": "3 cosas que no sabías sobre...",
                "style": "Informativo, claro, visual",
                "hashtags": ["#learnontiktok", "#education", "#tips"]
            },
            "behind_scenes": {
                "hook": "Así es como creamos...",
                "style": "Auténtico, casual, real",
                "hashtags": ["#behindthescenes", "#bts", "#reallife"]
            },
            "challenge": {
                "hook": "¿Puedes hacer esto?",
                "style": "Interactivo, divertido, participativo",
                "hashtags": ["#challenge", "#trythis", "#doyou"]
            }
        }
        
        template = tiktok_templates.get(video_type.lower(), tiktok_templates["trending"])
        
        # Generar post base
        post = self.generate_post(
            platform="tiktok",
            post_type="demo",
            product_name=product_name,
            target_audience=target_audience
        )
        
        # Personalizar para TikTok
        tiktok_content = f"""{template['hook']} {product_name}

{post.get('post_content', '')[:200]}

💡 Swipe para más
🎯 Link en bio
📱 Comparte si te gustó

{chr(10).join(template['hashtags'])}"""
        
        post["post_content"] = tiktok_content
        post["full_post"] = tiktok_content
        post["tiktok_type"] = video_type
        post["video_script"] = {
            "hook": template["hook"],
            "main_content": post.get("post_content", ""),
            "cta": "Link en bio",
            "duration": "15-60 segundos",
            "style": template["style"]
        }
        
        return post
    
    def generate_youtube_content(
        self,
        video_topic: str,
        product_name: str,
        video_length: int = 10
    ) -> Dict[str, Any]:
        """
        Genera contenido completo para YouTube
        
        Args:
            video_topic: Tema del video
            product_name: Nombre del producto
            video_length: Duración en minutos
        
        Returns:
            Contenido completo para YouTube
        """
        # Generar título optimizado para SEO
        title_options = [
            f"{video_topic}: Guía Completa {product_name}",
            f"Cómo usar {product_name} - Tutorial {video_topic}",
            f"{product_name} Review: Todo lo que necesitas saber"
        ]
        
        # Descripción optimizada
        description = f"""
        En este video te explico todo sobre {video_topic} usando {product_name}.
        
        📌 Timestamps:
        0:00 - Introducción
        0:30 - ¿Qué es {product_name}?
        2:00 - Características principales
        5:00 - Cómo usarlo
        8:00 - Casos de uso
        10:00 - Conclusión
        
        🔗 Links importantes:
        - Sitio web: [URL]
        - Prueba gratuita: [URL]
        - Documentación: [URL]
        
        💬 Déjame saber en los comentarios qué te pareció.
        
        #YouTube #Tutorial #{product_name.replace(' ', '')}
        """.strip()
        
        # Tags para SEO
        tags = [
            video_topic,
            product_name,
            "tutorial",
            "guía",
            "review",
            "cómo usar",
            "explicación"
        ]
        
        # Thumbnail suggestions
        thumbnail_suggestions = {
            "title_text": f"{video_topic} con {product_name}",
            "colors": ["#FF0000", "#FFFFFF", "#000000"],
            "elements": ["Producto destacado", "Texto grande", "Hook visual"]
        }
        
        return {
            "video_topic": video_topic,
            "product_name": product_name,
            "duration_minutes": video_length,
            "title_options": title_options,
            "recommended_title": title_options[0],
            "description": description,
            "tags": tags,
            "thumbnail_suggestions": thumbnail_suggestions,
            "script": self.generate_video_script_advanced(
                self.generate_post("youtube", "demo", product_name, "general"),
                video_length * 60,
                "educational"
            ),
            "promotion": {
                "community_posts": [
                    f"Nuevo video: {video_topic}",
                    f"¿Quieres aprender sobre {product_name}? Mira nuestro nuevo video"
                ],
                "hashtags": ["#YouTube", "#Tutorial", f"#{product_name.replace(' ', '')}"]
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_linkedin_article(
        self,
        article_topic: str,
        product_name: str,
        target_audience: str,
        word_count: int = 1000
    ) -> Dict[str, Any]:
        """
        Genera estructura completa para artículo de LinkedIn
        
        Args:
            article_topic: Tema del artículo
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            word_count: Número de palabras objetivo
        
        Returns:
            Estructura completa del artículo
        """
        # Estructura del artículo
        article = {
            "title": f"{article_topic}: Cómo {product_name} puede transformar tu negocio",
            "subtitle": f"Una guía completa para {target_audience}",
            "estimated_read_time": f"{word_count // 200} min",
            "sections": [
                {
                    "heading": "Introducción",
                    "content": f"""
                    En el mundo actual, {article_topic} se ha convertido en esencial.
                    {product_name} ofrece una solución innovadora para {target_audience}
                    que puede transformar completamente tu forma de trabajar.
                    """.strip(),
                    "word_count": 50
                },
                {
                    "heading": "El Problema",
                    "content": f"""
                    Muchos {target_audience} enfrentan desafíos significativos cuando se trata de {article_topic}.
                    Estos problemas incluyen falta de eficiencia, costos elevados y procesos complicados.
                    """.strip(),
                    "word_count": 100
                },
                {
                    "heading": f"La Solución: {product_name}",
                    "content": f"""
                    {product_name} aborda estos desafíos de manera innovadora.
                    Con características diseñadas específicamente para {target_audience},
                    ofrece una solución completa y efectiva.
                    """.strip(),
                    "word_count": 150
                },
                {
                    "heading": "Casos de Uso Reales",
                    "content": f"""
                    Veamos cómo {product_name} ha ayudado a empresas reales:
                    
                    1. Caso de éxito 1: [Descripción]
                    2. Caso de éxito 2: [Descripción]
                    3. Caso de éxito 3: [Descripción]
                    """.strip(),
                    "word_count": 200
                },
                {
                    "heading": "Próximos Pasos",
                    "content": f"""
                    Si eres {target_audience} y estás interesado en {product_name},
                    aquí están los próximos pasos:
                    
                    - Explorar las características
                    - Solicitar una demo
                    - Contactar con nuestro equipo
                    """.strip(),
                    "word_count": 100
                },
                {
                    "heading": "Conclusión",
                    "content": f"""
                    {product_name} representa una oportunidad real para {target_audience}
                    que buscan mejorar en {article_topic}. No esperes más para comenzar.
                    """.strip(),
                    "word_count": 50
                }
            ],
            "cta": {
                "text": "¿Quieres saber más sobre cómo podemos ayudarte?",
                "button": "Contactar ahora",
                "link": "[URL]"
            },
            "hashtags": [
                article_topic.replace(" ", ""),
                product_name.replace(" ", ""),
                target_audience,
                "business",
                "innovation"
            ],
            "engagement_tips": [
                "Publicar en horario laboral (9am-5pm)",
                "Incluir pregunta al final para generar comentarios",
                "Responder a todos los comentarios",
                "Compartir en grupos relevantes"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return article
    
    def analyze_optimal_posting_time_ml(
        self,
        historical_posts: List[Dict[str, Any]],
        platform: str
    ) -> Dict[str, Any]:
        """
        Analiza mejor momento para publicar usando ML
        
        Args:
            historical_posts: Posts históricos con métricas
            platform: Plataforma a analizar
        
        Returns:
            Análisis de mejor momento para publicar
        """
        if not historical_posts:
            return {
                "platform": platform,
                "error": "No historical data available",
                "recommendations": ["Usar horarios por defecto de la plataforma"]
            }
        
        # Filtrar posts de la plataforma
        platform_posts = [p for p in historical_posts if p.get("platform") == platform]
        
        if not platform_posts:
            return {
                "platform": platform,
                "error": "No posts for this platform",
                "recommendations": ["Usar horarios por defecto"]
            }
        
        # Analizar por hora del día
        hour_performance = {}
        for post in platform_posts:
            published_at = post.get("metadata", {}).get("published_at")
            if not published_at:
                continue
            
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hour = pub_time.hour
                engagement_rate = post.get("performance", {}).get("engagement_rate", 0)
                
                if hour not in hour_performance:
                    hour_performance[hour] = []
                hour_performance[hour].append(engagement_rate)
            except:
                continue
        
        # Calcular promedio por hora
        avg_by_hour = {
            hour: sum(rates) / len(rates)
            for hour, rates in hour_performance.items()
        }
        
        # Encontrar mejores horas
        best_hours = sorted(
            avg_by_hour.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Analizar por día de la semana
        day_performance = {}
        for post in platform_posts:
            published_at = post.get("metadata", {}).get("published_at")
            if not published_at:
                continue
            
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                day = pub_time.strftime("%A")
                engagement_rate = post.get("performance", {}).get("engagement_rate", 0)
                
                if day not in day_performance:
                    day_performance[day] = []
                day_performance[day].append(engagement_rate)
            except:
                continue
        
        best_days = sorted(
            day_performance.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:3]
        
        return {
            "platform": platform,
            "analysis_based_on": len(platform_posts),
            "best_hours": [
                {"hour": hour, "avg_engagement": round(rate, 2)}
                for hour, rate in best_hours
            ],
            "best_days": [
                {"day": day, "avg_engagement": round(sum(rates) / len(rates), 2)}
                for day, rates in best_days
            ],
            "recommendations": [
                f"Mejor hora: {best_hours[0][0]}:00 (engagement: {best_hours[0][1]:.2f}%)",
                f"Mejor día: {best_days[0][0]} (engagement: {sum(best_days[0][1])/len(best_days[0][1]):.2f}%)",
                f"Combinación óptima: {best_days[0][0]} a las {best_hours[0][0]}:00"
            ],
            "confidence": "high" if len(platform_posts) >= 20 else "medium" if len(platform_posts) >= 10 else "low",
            "analyzed_at": datetime.now().isoformat()
        }
    
    def integrate_with_google_analytics(
        self,
        post: Dict[str, Any],
        ga_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integra post con datos de Google Analytics
        
        Args:
            post: Post generado
            ga_data: Datos de Google Analytics
        
        Returns:
            Post enriquecido con datos de GA
        """
        enriched_post = post.copy()
        
        # Agregar métricas de GA
        enriched_post["ga_metrics"] = {
            "page_views": ga_data.get("page_views", 0),
            "unique_visitors": ga_data.get("unique_visitors", 0),
            "bounce_rate": ga_data.get("bounce_rate", 0),
            "avg_session_duration": ga_data.get("avg_session_duration", 0),
            "conversions": ga_data.get("conversions", 0),
            "conversion_rate": ga_data.get("conversion_rate", 0)
        }
        
        # Agregar datos demográficos
        if "demographics" in ga_data:
            enriched_post["ga_demographics"] = ga_data["demographics"]
        
        # Agregar fuentes de tráfico
        if "traffic_sources" in ga_data:
            enriched_post["ga_traffic_sources"] = ga_data["traffic_sources"]
        
        # Calcular ROI desde GA
        if "revenue" in ga_data and "cost" in ga_data:
            enriched_post["ga_roi"] = {
                "revenue": ga_data["revenue"],
                "cost": ga_data["cost"],
                "roi": ((ga_data["revenue"] - ga_data["cost"]) / ga_data["cost"] * 100) if ga_data["cost"] > 0 else 0
            }
        
        enriched_post["ga_integrated"] = True
        enriched_post["ga_last_updated"] = datetime.now().isoformat()
        
        return enriched_post
    
    def generate_dynamic_template(
        self,
        template_name: str,
        template_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea template dinámico personalizable
        
        Args:
            template_name: Nombre del template
            template_structure: Estructura del template con placeholders
        
        Returns:
            Template creado
        """
        template = {
            "name": template_name,
            "structure": template_structure,
            "placeholders": self._extract_placeholders(template_structure),
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        # Guardar template
        if not hasattr(self, 'dynamic_templates'):
            self.dynamic_templates = {}
        
        self.dynamic_templates[template_name] = template
        
        return template
    
    def _extract_placeholders(self, structure: Any) -> List[str]:
        """Extrae placeholders de una estructura"""
        placeholders = []
        
        if isinstance(structure, dict):
            for value in structure.values():
                placeholders.extend(self._extract_placeholders(value))
        elif isinstance(structure, list):
            for item in structure:
                placeholders.extend(self._extract_placeholders(item))
        elif isinstance(structure, str):
            # Buscar placeholders en formato {placeholder}
            import re
            found = re.findall(r'\{(\w+)\}', structure)
            placeholders.extend(found)
        
        return list(set(placeholders))
    
    def use_dynamic_template(
        self,
        template_name: str,
        values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Usa un template dinámico con valores
        
        Args:
            template_name: Nombre del template
            values: Valores para reemplazar placeholders
        
        Returns:
            Post generado desde template
        """
        if not hasattr(self, 'dynamic_templates') or template_name not in self.dynamic_templates:
            return {
                "error": f"Template '{template_name}' not found",
                "available_templates": list(self.dynamic_templates.keys()) if hasattr(self, 'dynamic_templates') else []
            }
        
        template = self.dynamic_templates[template_name]
        structure = template["structure"]
        
        # Reemplazar placeholders
        result = self._replace_placeholders(structure, values)
        
        # Incrementar uso
        template["usage_count"] += 1
        
        return {
            "template_name": template_name,
            "generated_content": result,
            "used_at": datetime.now().isoformat()
        }
    
    def _replace_placeholders(self, structure: Any, values: Dict[str, Any]) -> Any:
        """Reemplaza placeholders en una estructura"""
        if isinstance(structure, dict):
            return {
                key: self._replace_placeholders(value, values)
                for key, value in structure.items()
            }
        elif isinstance(structure, list):
            return [
                self._replace_placeholders(item, values)
                for item in structure
            ]
        elif isinstance(structure, str):
            import re
            return re.sub(
                r'\{(\w+)\}',
                lambda m: str(values.get(m.group(1), m.group(0))),
                structure
            )
        else:
            return structure
    
    def generate_content_for_notion(
        self,
        post: Dict[str, Any],
        notion_format: str = "page"
    ) -> Dict[str, Any]:
        """
        Genera contenido formateado para Notion
        
        Args:
            post: Post generado
            notion_format: Formato (page, database, template)
        
        Returns:
            Contenido formateado para Notion
        """
        product_name = post.get("metadata", {}).get("product_name", "Producto")
        post_content = post.get("post_content", "")
        platform = post.get("platform", "instagram")
        
        notion_content = {
            "format": notion_format,
            "title": f"{product_name} - {platform.capitalize()} Post",
            "blocks": [
                {
                    "type": "heading_1",
                    "content": f"{product_name} - {platform.capitalize()}"
                },
                {
                    "type": "paragraph",
                    "content": post_content
                },
                {
                    "type": "divider"
                },
                {
                    "type": "heading_2",
                    "content": "Hashtags"
                },
                {
                    "type": "bulleted_list",
                    "items": post.get("hashtags", [])[:10]
                },
                {
                    "type": "heading_2",
                    "content": "Métricas"
                },
                {
                    "type": "table",
                    "columns": ["Métrica", "Valor"],
                    "rows": [
                        ["Engagement Score", str(post.get("analysis", {}).get("engagement_score", 0))],
                        ["Readability", str(post.get("analysis", {}).get("readability_score", 0))],
                        ["Conversion Potential", str(post.get("analysis", {}).get("conversion_potential", 0))]
                    ]
                }
            ],
            "properties": {
                "Platform": platform,
                "Post Type": post.get("post_type", "demo"),
                "Created": datetime.now().isoformat(),
                "Status": "Draft"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return notion_content
    
    def generate_competitor_swot_analysis(
        self,
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera análisis SWOT de competidores
        
        Args:
            competitor_data: Datos de competidores
        
        Returns:
            Análisis SWOT completo
        """
        swot_analysis = {
            "competitors_analyzed": len(competitor_data),
            "analysis_date": datetime.now().isoformat(),
            "competitors": []
        }
        
        for competitor in competitor_data:
            competitor_swot = {
                "name": competitor.get("name", "Unknown"),
                "strengths": competitor.get("strengths", []),
                "weaknesses": competitor.get("weaknesses", []),
                "opportunities": competitor.get("opportunities", []),
                "threats": competitor.get("threats", []),
                "recommendations": []
            }
            
            # Generar recomendaciones basadas en SWOT
            if competitor_swot["weaknesses"]:
                competitor_swot["recommendations"].append(
                    f"Explotar debilidades: {', '.join(competitor_swot['weaknesses'][:2])}"
                )
            
            if competitor_swot["opportunities"]:
                competitor_swot["recommendations"].append(
                    f"Aprovechar oportunidades: {', '.join(competitor_swot['opportunities'][:2])}"
                )
            
            swot_analysis["competitors"].append(competitor_swot)
        
        # Análisis agregado
        swot_analysis["aggregate_insights"] = {
            "common_strengths": [],
            "common_weaknesses": [],
            "market_opportunities": [],
            "market_threats": []
        }
        
        return swot_analysis
    
    def generate_pinterest_content(
        self,
        pin_topic: str,
        product_name: str,
        pin_type: str = "idea"
    ) -> Dict[str, Any]:
        """
        Genera contenido específico para Pinterest
        
        Args:
            pin_topic: Tema del pin
            product_name: Nombre del producto
            pin_type: Tipo de pin (idea, tutorial, product, infographic)
        
        Returns:
            Contenido completo para Pinterest
        """
        pin_templates = {
            "idea": {
                "title": f"{pin_topic}: Ideas con {product_name}",
                "description": f"Descubre ideas creativas usando {product_name} para {pin_topic}",
                "hashtags": ["#ideas", "#diy", "#creative"]
            },
            "tutorial": {
                "title": f"Cómo hacer {pin_topic} con {product_name}",
                "description": f"Tutorial paso a paso para {pin_topic} usando {product_name}",
                "hashtags": ["#tutorial", "#howto", "#stepbystep"]
            },
            "product": {
                "title": f"{product_name} - {pin_topic}",
                "description": f"Conoce {product_name} y cómo puede ayudarte con {pin_topic}",
                "hashtags": ["#product", "#review", "#recommendation"]
            },
            "infographic": {
                "title": f"Infografía: {pin_topic} con {product_name}",
                "description": f"Todo lo que necesitas saber sobre {pin_topic} y {product_name}",
                "hashtags": ["#infographic", "#data", "#visual"]
            }
        }
        
        template = pin_templates.get(pin_type.lower(), pin_templates["idea"])
        
        return {
            "pin_type": pin_type,
            "title": template["title"],
            "description": template["description"],
            "board_suggestions": [
                f"{product_name} Ideas",
                f"{pin_topic} Tips",
                "Product Inspiration"
            ],
            "hashtags": template["hashtags"],
            "image_specs": {
                "ratio": "2:3",
                "min_width": 1000,
                "min_height": 1500,
                "recommended": "1000x1500"
            },
            "seo_keywords": [pin_topic, product_name, "ideas", "tutorial"],
            "rich_pins": {
                "product": True,
                "article": pin_type == "tutorial",
                "recipe": False
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_reddit_content(
        self,
        subreddit: str,
        post_type: str,
        product_name: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Genera contenido para Reddit
        
        Args:
            subreddit: Subreddit objetivo
            post_type: Tipo de post (question, discussion, ama, promotion)
            product_name: Nombre del producto
            content: Contenido del post
        
        Returns:
            Contenido formateado para Reddit
        """
        reddit_templates = {
            "question": {
                "title_format": f"¿Alguien ha usado {product_name}? ¿Qué opinan?",
                "flair": "Question",
                "guidelines": [
                    "Ser genuino y transparente",
                    "No hacer spam",
                    "Participar en la discusión",
                    "Seguir reglas del subreddit"
                ]
            },
            "discussion": {
                "title_format": f"Discusión: {product_name} y su impacto en...",
                "flair": "Discussion",
                "guidelines": [
                    "Iniciar conversación real",
                    "Responder comentarios",
                    "No autopromoción excesiva"
                ]
            },
            "ama": {
                "title_format": f"Soy el creador de {product_name}, AMA!",
                "flair": "AMA",
                "guidelines": [
                    "Verificar identidad",
                    "Responder todas las preguntas",
                    "Ser honesto y transparente"
                ]
            },
            "promotion": {
                "title_format": f"[Producto] {product_name} - Lo que aprendimos",
                "flair": "Promotion",
                "guidelines": [
                    "Seguir reglas de promoción del subreddit",
                    "Ofrecer valor real",
                    "No solo hacer spam"
                ]
            }
        }
        
        template = reddit_templates.get(post_type.lower(), reddit_templates["discussion"])
        
        return {
            "subreddit": subreddit,
            "post_type": post_type,
            "title": template["title_format"],
            "content": content,
            "flair": template["flair"],
            "guidelines": template["guidelines"],
            "formatting_tips": [
                "Usar markdown para formato",
                "Incluir line breaks para legibilidad",
                "Usar listas cuando sea apropiado",
                "Evitar emojis excesivos"
            ],
            "engagement_strategy": [
                "Responder rápidamente a comentarios",
                "Participar genuinamente en discusión",
                "No eliminar posts con feedback negativo",
                "Seguir reddiquette"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def analyze_viral_potential(
        self,
        post: Dict[str, Any],
        historical_viral_posts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analiza potencial viral de un post
        
        Args:
            post: Post a analizar
            historical_viral_posts: Posts virales históricos (opcional)
        
        Returns:
            Análisis de potencial viral
        """
        analysis = post.get("analysis", {})
        engagement_score = analysis.get("engagement_score", 0)
        
        # Factores de viralidad
        viral_factors = {
            "hook_strength": 0.0,
            "emotional_appeal": 0.0,
            "shareability": 0.0,
            "timeliness": 0.0,
            "uniqueness": 0.0
        }
        
        post_content = post.get("post_content", "").lower()
        
        # Analizar hook
        hook_indicators = ["descubre", "sorprende", "nunca", "increíble", "revolucionario"]
        if any(indicator in post_content[:100] for indicator in hook_indicators):
            viral_factors["hook_strength"] = 0.8
        
        # Analizar apelación emocional
        emotional_words = ["amor", "éxito", "felicidad", "inspiración", "motivación"]
        if any(word in post_content for word in emotional_words):
            viral_factors["emotional_appeal"] = 0.7
        
        # Analizar shareability
        if analysis.get("has_questions"):
            viral_factors["shareability"] += 0.2
        if analysis.get("has_numbers"):
            viral_factors["shareability"] += 0.2
        if engagement_score > 70:
            viral_factors["shareability"] += 0.3
        
        # Timeliness (simulado)
        viral_factors["timeliness"] = 0.6  # Base
        
        # Uniqueness
        if len(post_content) > 200:
            viral_factors["uniqueness"] = 0.5
        
        # Calcular score viral
        viral_score = sum(viral_factors.values()) / len(viral_factors) * 100
        
        # Comparar con posts virales históricos
        if historical_viral_posts:
            avg_viral_engagement = sum(
                p.get("performance", {}).get("engagement_rate", 0)
                for p in historical_viral_posts
            ) / len(historical_viral_posts) if historical_viral_posts else 0
            
            if engagement_score >= avg_viral_engagement * 0.8:
                viral_score += 10
        
        # Recomendaciones para aumentar viralidad
        recommendations = []
        if viral_factors["hook_strength"] < 0.5:
            recommendations.append("Mejorar hook inicial - Debe capturar atención en primeros 3 segundos")
        if viral_factors["emotional_appeal"] < 0.5:
            recommendations.append("Aumentar apelación emocional - Conectar con sentimientos del público")
        if viral_factors["shareability"] < 0.5:
            recommendations.append("Aumentar shareability - Agregar elementos que inviten a compartir")
        
        return {
            "viral_score": round(viral_score, 2),
            "viral_factors": {k: round(v, 2) for k, v in viral_factors.items()},
            "viral_probability": round(viral_score / 100 * 100, 2),
            "recommendations": recommendations,
            "estimated_reach": int(1000 * (viral_score / 50)),
            "estimated_shares": int(100 * (viral_score / 50)),
            "viral_threshold": 70.0,
            "is_viral_potential": viral_score >= 70.0,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_email_sequence(
        self,
        sequence_name: str,
        product_name: str,
        sequence_length: int = 5
    ) -> Dict[str, Any]:
        """
        Genera secuencia completa de emails
        
        Args:
            sequence_name: Nombre de la secuencia
            product_name: Nombre del producto
            sequence_length: Número de emails en la secuencia
        
        Returns:
            Secuencia completa de emails
        """
        sequence = {
            "name": sequence_name,
            "product_name": product_name,
            "total_emails": sequence_length,
            "emails": [],
            "timing": {
                "email_1": "Immediately",
                "email_2": "Day 2",
                "email_3": "Day 5",
                "email_4": "Day 10",
                "email_5": "Day 15"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        email_types = [
            "welcome",
            "value_proposition",
            "case_study",
            "social_proof",
            "final_offer"
        ]
        
        for i in range(sequence_length):
            email_type = email_types[i] if i < len(email_types) else "follow_up"
            
            email = {
                "email_number": i + 1,
                "type": email_type,
                "subject": self._generate_email_subject(email_type, product_name, i + 1),
                "preheader": self._generate_email_preheader(email_type, product_name),
                "content": self._generate_email_content(email_type, product_name),
                "cta": self._generate_email_cta(email_type),
                "timing": sequence["timing"].get(f"email_{i+1}", f"Day {i*3}")
            }
            
            sequence["emails"].append(email)
        
        return sequence
    
    def _generate_email_subject(self, email_type: str, product_name: str, number: int) -> str:
        """Genera subject line para email"""
        subjects = {
            "welcome": f"Bienvenido a {product_name}! 🎉",
            "value_proposition": f"Cómo {product_name} puede ayudarte",
            "case_study": f"Historia de éxito con {product_name}",
            "social_proof": f"Lo que dicen nuestros usuarios de {product_name}",
            "final_offer": f"Última oportunidad: {product_name}"
        }
        return subjects.get(email_type, f"Actualización sobre {product_name}")
    
    def _generate_email_preheader(self, email_type: str, product_name: str) -> str:
        """Genera preheader para email"""
        preheaders = {
            "welcome": "Estamos emocionados de tenerte aquí",
            "value_proposition": "Descubre las ventajas",
            "case_study": "Casos reales de éxito",
            "social_proof": "Testimonios de usuarios",
            "final_offer": "No te lo pierdas"
        }
        return preheaders.get(email_type, "Actualización importante")
    
    def _generate_email_content(self, email_type: str, product_name: str) -> str:
        """Genera contenido para email"""
        contents = {
            "welcome": f"¡Hola! Bienvenido a {product_name}. Estamos aquí para ayudarte a alcanzar tus objetivos.",
            "value_proposition": f"{product_name} está diseñado para ayudarte a ser más eficiente y productivo.",
            "case_study": f"Descubre cómo otros han logrado éxito usando {product_name}.",
            "social_proof": f"Miles de usuarios confían en {product_name}. Lee lo que dicen.",
            "final_offer": f"Esta es tu última oportunidad para aprovechar {product_name}."
        }
        return contents.get(email_type, f"Actualización sobre {product_name}")
    
    def _generate_email_cta(self, email_type: str) -> str:
        """Genera CTA para email"""
        ctas = {
            "welcome": "Comenzar ahora",
            "value_proposition": "Ver características",
            "case_study": "Leer más",
            "social_proof": "Unirse ahora",
            "final_offer": "Aprovechar oferta"
        }
        return ctas.get(email_type, "Saber más")
    
    def generate_canva_design_specs(
        self,
        post: Dict[str, Any],
        design_type: str = "social_media"
    ) -> Dict[str, Any]:
        """
        Genera especificaciones de diseño para Canva
        
        Args:
            post: Post generado
            design_type: Tipo de diseño (social_media, story, banner, infographic)
        
        Returns:
            Especificaciones de diseño para Canva
        """
        platform = post.get("platform", "instagram")
        post_type = post.get("post_type", "demo")
        
        # Dimensiones por tipo
        dimensions_map = {
            "social_media": {
                "instagram": {"width": 1080, "height": 1080, "template": "Instagram Post"},
                "linkedin": {"width": 1200, "height": 627, "template": "LinkedIn Post"},
                "facebook": {"width": 1200, "height": 630, "template": "Facebook Post"}
            },
            "story": {
                "instagram": {"width": 1080, "height": 1920, "template": "Instagram Story"},
                "facebook": {"width": 1080, "height": 1920, "template": "Facebook Story"}
            },
            "banner": {
                "default": {"width": 1920, "height": 1080, "template": "Banner"}
            },
            "infographic": {
                "default": {"width": 1080, "height": 1920, "template": "Infographic"}
            }
        }
        
        design_specs = dimensions_map.get(design_type, dimensions_map["social_media"])
        platform_specs = design_specs.get(platform, design_specs.get("default", {"width": 1080, "height": 1080}))
        
        # Elementos de diseño
        visual_elements = {
            "teaser": ["Mystery overlay", "Gradient background", "Product silhouette"],
            "demo": ["Product showcase", "Feature highlights", "Clean background"],
            "offer": ["Discount badge", "Urgency timer", "Bold colors"]
        }
        
        return {
            "design_type": design_type,
            "platform": platform,
            "dimensions": platform_specs,
            "canva_template": platform_specs.get("template", "Custom"),
            "visual_elements": visual_elements.get(post_type, []),
            "color_palette": self.analyze_visual_assets(post, "image").color_suggestions,
            "text_elements": {
                "headline": post.get("post_content", "")[:50],
                "subheadline": post.get("post_content", "")[50:150],
                "cta": post.get("cta", "Ver más")
            },
            "brand_guidelines": {
                "fonts": ["Primary font", "Secondary font"],
                "logo_placement": "Top right or bottom left",
                "brand_colors": ["#667eea", "#764ba2"]
            },
            "canva_api": {
                "endpoint": "https://api.canva.com/v1/designs",
                "template_id": f"template_{platform}_{post_type}",
                "custom_elements": True
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_brand_voice_analysis(
        self,
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza y define voz de marca basado en posts
        
        Args:
            posts: Lista de posts históricos
        
        Returns:
            Análisis de voz de marca
        """
        if not posts:
            return {
                "error": "No posts provided",
                "recommendations": ["Generar más contenido para análisis"]
            }
        
        # Analizar tonos usados
        tones_used = [p.get("tone", "amigable") for p in posts]
        tone_distribution = Counter(tones_used)
        
        # Analizar longitud promedio
        avg_length = sum(len(p.get("post_content", "")) for p in posts) / len(posts)
        
        # Analizar uso de emojis
        emoji_usage = sum(
            1 for p in posts
            if bool(re.findall(r'[😀-🙏🌀-🗿]', p.get("post_content", "")))
        ) / len(posts) * 100
        
        # Analizar uso de preguntas
        question_usage = sum(
            1 for p in posts
            if "?" in p.get("post_content", "")
        ) / len(posts) * 100
        
        # Definir voz de marca
        brand_voice = {
            "primary_tone": tone_distribution.most_common(1)[0][0] if tone_distribution else "amigable",
            "tone_distribution": dict(tone_distribution),
            "writing_style": {
                "avg_length": round(avg_length, 0),
                "style": "conciso" if avg_length < 150 else "detallado" if avg_length > 300 else "moderado",
                "emoji_usage": round(emoji_usage, 2),
                "question_usage": round(question_usage, 2)
            },
            "characteristics": []
        }
        
        # Agregar características
        if emoji_usage > 50:
            brand_voice["characteristics"].append("Uso frecuente de emojis")
        if question_usage > 30:
            brand_voice["characteristics"].append("Comunicación interactiva")
        if avg_length < 150:
            brand_voice["characteristics"].append("Mensajes concisos")
        
        # Recomendaciones
        recommendations = [
            f"Tono principal: {brand_voice['primary_tone']} - Mantener consistencia",
            f"Estilo de escritura: {brand_voice['writing_style']['style']} - Continuar con este estilo"
        ]
        
        return {
            "brand_voice": brand_voice,
            "consistency_score": round(
                (tone_distribution.most_common(1)[0][1] / len(posts) * 100) if tone_distribution else 0,
                2
            ),
            "recommendations": recommendations,
            "analyzed_posts": len(posts),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_content_for_database(
        self,
        posts: List[Dict[str, Any]],
        db_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera estructura de datos para base de datos
        
        Args:
            posts: Lista de posts
            db_schema: Esquema de base de datos
        
        Returns:
            Datos formateados para base de datos
        """
        db_records = []
        
        for post in posts:
            record = {
                "id": post.get("metadata", {}).get("generated_at", datetime.now().isoformat()),
                "platform": post.get("platform"),
                "post_type": post.get("post_type"),
                "content": post.get("post_content", ""),
                "hashtags": ", ".join(post.get("hashtags", [])),
                "engagement_score": post.get("analysis", {}).get("engagement_score", 0),
                "created_at": post.get("metadata", {}).get("generated_at", datetime.now().isoformat()),
                "status": "draft"
            }
            
            # Agregar campos adicionales del schema
            if "custom_fields" in db_schema:
                for field in db_schema["custom_fields"]:
                    record[field] = post.get(field, None)
            
            db_records.append(record)
        
        return {
            "table_name": db_schema.get("table_name", "posts"),
            "total_records": len(db_records),
            "records": db_records,
            "sql_insert": self._generate_sql_inserts(db_records, db_schema.get("table_name", "posts")),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_sql_inserts(self, records: List[Dict[str, Any]], table_name: str) -> str:
        """Genera SQL INSERT statements"""
        if not records:
            return ""
        
        columns = list(records[0].keys())
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
        
        values = []
        for record in records:
            record_values = []
            for col in columns:
                value = record.get(col)
                if isinstance(value, str):
                    record_values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                elif value is None:
                    record_values.append("NULL")
                else:
                    record_values.append(str(value))
            values.append(f"({', '.join(record_values)})")
        
        sql += ",\n".join(values) + ";"
        return sql
    
    def generate_api_response_format(
        self,
        post: Dict[str, Any],
        api_format: str = "rest"
    ) -> Dict[str, Any]:
        """
        Genera respuesta formateada para API
        
        Args:
            post: Post generado
            api_format: Formato de API (rest, graphql, webhook)
        
        Returns:
            Respuesta formateada para API
        """
        if api_format.lower() == "rest":
            return {
                "status": "success",
                "data": {
                    "post": post,
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                },
                "message": "Post generated successfully"
            }
        elif api_format.lower() == "graphql":
            return {
                "data": {
                    "generatePost": {
                        "post": post,
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        elif api_format.lower() == "webhook":
            return {
                "event": "post.generated",
                "timestamp": datetime.now().isoformat(),
                "payload": post
            }
        else:
            return {
                "error": f"Unknown API format: {api_format}",
                "supported_formats": ["rest", "graphql", "webhook"]
            }
    
    def generate_blog_post_structure(
        self,
        blog_topic: str,
        product_name: str,
        target_audience: str,
        word_count: int = 1500
    ) -> Dict[str, Any]:
        """
        Genera estructura completa para blog post
        
        Args:
            blog_topic: Tema del blog
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            word_count: Número de palabras objetivo
        
        Returns:
            Estructura completa del blog post
        """
        blog_structure = {
            "title": f"{blog_topic}: Guía Completa con {product_name}",
            "meta_description": f"Descubre cómo {product_name} puede ayudarte con {blog_topic}. Guía completa para {target_audience}.",
            "slug": f"{blog_topic.lower().replace(' ', '-')}-{product_name.lower().replace(' ', '-')}",
            "estimated_read_time": f"{word_count // 200} min",
            "target_audience": target_audience,
            "sections": [
                {
                    "heading": "Introducción",
                    "content": f"En este artículo exploraremos {blog_topic} y cómo {product_name} puede ser tu aliado perfecto.",
                    "word_count": 100
                },
                {
                    "heading": f"¿Qué es {blog_topic}?",
                    "content": f"{blog_topic} es un concepto clave que todo {target_audience} debe entender...",
                    "word_count": 200
                },
                {
                    "heading": f"Cómo {product_name} resuelve {blog_topic}",
                    "content": f"{product_name} ofrece una solución innovadora para abordar los desafíos de {blog_topic}...",
                    "word_count": 300
                },
                {
                    "heading": "Casos de Uso Reales",
                    "content": "Veamos ejemplos concretos de cómo otros han implementado esta solución...",
                    "word_count": 400
                },
                {
                    "heading": "Mejores Prácticas",
                    "content": "Aquí están las mejores prácticas para maximizar los resultados...",
                    "word_count": 300
                },
                {
                    "heading": "Conclusión",
                    "content": f"{blog_topic} es esencial para {target_audience}, y {product_name} es la herramienta perfecta.",
                    "word_count": 100
                }
            ],
            "seo": {
                "focus_keyword": blog_topic,
                "keywords": [blog_topic, product_name, target_audience, "guía", "tutorial"],
                "meta_keywords": f"{blog_topic}, {product_name}, {target_audience}",
                "internal_links": [],
                "external_links": []
            },
            "cta": {
                "text": f"¿Listo para probar {product_name}?",
                "button": "Comenzar ahora",
                "placement": "end"
            },
            "images": {
                "featured_image": f"{blog_topic.replace(' ', '-')}-featured.jpg",
                "inline_images": 3,
                "alt_texts": []
            },
            "categories": [blog_topic, product_name],
            "tags": [blog_topic, product_name, target_audience, "guía"],
            "generated_at": datetime.now().isoformat()
        }
        
        return blog_structure
    
    def generate_whatsapp_business_content(
        self,
        message_type: str,
        product_name: str,
        customer_name: str = None
    ) -> Dict[str, Any]:
        """
        Genera contenido para WhatsApp Business
        
        Args:
            message_type: Tipo de mensaje (welcome, promotion, support, follow_up)
            product_name: Nombre del producto
            customer_name: Nombre del cliente (opcional)
        
        Returns:
            Contenido formateado para WhatsApp Business
        """
        greeting = f"Hola {customer_name}!" if customer_name else "Hola!"
        
        whatsapp_templates = {
            "welcome": {
                "message": f"""{greeting}

¡Bienvenido a {product_name}! 🎉

Estamos aquí para ayudarte. ¿En qué podemos asistirte hoy?""",
                "quick_replies": ["Ver productos", "Soporte", "Información"]
            },
            "promotion": {
                "message": f"""{greeting}

Tenemos una oferta especial para ti! 🔥

{product_name} con descuento exclusivo.

¿Te interesa saber más?""",
                "quick_replies": ["Sí, quiero saber más", "Ver oferta", "No, gracias"]
            },
            "support": {
                "message": f"""{greeting}

Gracias por contactarnos sobre {product_name}.

Nuestro equipo de soporte está aquí para ayudarte. ¿Cuál es tu consulta?""",
                "quick_replies": ["Problema técnico", "Pregunta general", "Facturación"]
            },
            "follow_up": {
                "message": f"""{greeting}

Solo queríamos seguir sobre {product_name}.

¿Hay algo en lo que podamos ayudarte?""",
                "quick_replies": ["Todo bien", "Tengo una pregunta", "Necesito ayuda"]
            }
        }
        
        template = whatsapp_templates.get(message_type.lower(), whatsapp_templates["welcome"])
        
        return {
            "message_type": message_type,
            "message": template["message"],
            "quick_replies": template["quick_replies"],
            "character_count": len(template["message"]),
            "formatting": {
                "use_emojis": True,
                "use_line_breaks": True,
                "max_length": 4096
            },
            "best_practices": [
                "Responder dentro de 24 horas",
                "Usar lenguaje claro y directo",
                "Incluir quick replies cuando sea posible",
                "Personalizar con nombre del cliente"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_snapchat_content(
        self,
        snap_type: str,
        product_name: str,
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        Genera contenido para Snapchat
        
        Args:
            snap_type: Tipo de snap (story, filter, lens, ad)
            product_name: Nombre del producto
            duration: Duración en segundos
        
        Returns:
            Contenido para Snapchat
        """
        snap_templates = {
            "story": {
                "hook": f"Swip up para {product_name}! 👆",
                "content": f"Descubre {product_name} en nuestra historia",
                "cta": "Swipe up",
                "hashtags": ["#snapchat", "#story"]
            },
            "filter": {
                "hook": f"Prueba nuestro filtro de {product_name}!",
                "content": "Usa nuestro filtro personalizado",
                "cta": "Usar filtro",
                "hashtags": ["#filter", "#ar"]
            },
            "lens": {
                "hook": f"Experimenta {product_name} con AR!",
                "content": "Prueba nuestro lens de realidad aumentada",
                "cta": "Probar lens",
                "hashtags": ["#lens", "#ar", "#snapchat"]
            },
            "ad": {
                "hook": f"Descubre {product_name}",
                "content": f"La solución que necesitas: {product_name}",
                "cta": "Saber más",
                "hashtags": ["#ad", "#sponsored"]
            }
        }
        
        template = snap_templates.get(snap_type.lower(), snap_templates["story"])
        
        return {
            "snap_type": snap_type,
            "duration_seconds": duration,
            "hook": template["hook"],
            "content": template["content"],
            "cta": template["cta"],
            "hashtags": template["hashtags"],
            "specifications": {
                "format": "9:16 (vertical)",
                "resolution": "1080x1920",
                "max_duration": 60,
                "file_size_limit": "32MB"
            },
            "engagement_tips": [
                "Usar elementos visuales llamativos",
                "Incluir texto superpuesto",
                "Mantener contenido auténtico",
                "Usar geofilters cuando sea posible"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def integrate_with_zapier(
        self,
        post: Dict[str, Any],
        zap_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integra post con Zapier
        
        Args:
            post: Post generado
            zap_config: Configuración del Zap
        
        Returns:
            Configuración para Zapier
        """
        zap_webhook = {
            "webhook_url": zap_config.get("webhook_url", ""),
            "trigger": "post_generated",
            "data": {
                "post_id": post.get("metadata", {}).get("generated_at"),
                "platform": post.get("platform"),
                "post_type": post.get("post_type"),
                "content": post.get("post_content", ""),
                "hashtags": post.get("hashtags", []),
                "engagement_score": post.get("analysis", {}).get("engagement_score", 0),
                "generated_at": datetime.now().isoformat()
            },
            "actions": zap_config.get("actions", ["send_to_slack", "save_to_google_sheets"]),
            "filters": zap_config.get("filters", {})
        }
        
        return {
            "zap_name": zap_config.get("zap_name", "Post Generator Integration"),
            "webhook_config": zap_webhook,
            "status": "ready",
            "test_url": zap_config.get("test_url", ""),
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_content_audit(
        self,
        posts: List[Dict[str, Any]],
        audit_period: str = "30d"
    ) -> Dict[str, Any]:
        """
        Genera auditoría completa de contenido
        
        Args:
            posts: Lista de posts a auditar
            audit_period: Período de auditoría
        
        Returns:
            Auditoría completa de contenido
        """
        if not posts:
            return {
                "error": "No posts provided",
                "audit_period": audit_period
            }
        
        # Análisis de contenido
        total_posts = len(posts)
        platforms = Counter(p.get("platform") for p in posts)
        post_types = Counter(p.get("post_type") for p in posts)
        
        # Análisis de performance
        avg_engagement = sum(
            p.get("analysis", {}).get("engagement_score", 0) for p in posts
        ) / total_posts if total_posts > 0 else 0
        
        high_performing = [
            p for p in posts
            if p.get("analysis", {}).get("engagement_score", 0) > 70
        ]
        
        low_performing = [
            p for p in posts
            if p.get("analysis", {}).get("engagement_score", 0) < 50
        ]
        
        # Análisis de consistencia
        tones_used = Counter(p.get("tone", "amigable") for p in posts)
        most_common_tone = tones_used.most_common(1)[0][0] if tones_used else "amigable"
        tone_consistency = (tones_used.most_common(1)[0][1] / total_posts * 100) if tones_used else 0
        
        # Análisis de hashtags
        all_hashtags = []
        for p in posts:
            all_hashtags.extend(p.get("hashtags", []))
        top_hashtags = Counter(all_hashtags).most_common(10)
        
        # Recomendaciones
        recommendations = []
        if avg_engagement < 60:
            recommendations.append("Engagement promedio bajo - Revisar estrategia de contenido")
        if tone_consistency < 70:
            recommendations.append("Inconsistencia en tono - Establecer guía de voz de marca")
        if len(low_performing) > total_posts * 0.3:
            recommendations.append("Alto porcentaje de posts de bajo rendimiento - Analizar causas")
        
        return {
            "audit_period": audit_period,
            "total_posts": total_posts,
            "summary": {
                "platforms_distribution": dict(platforms),
                "post_types_distribution": dict(post_types),
                "avg_engagement_score": round(avg_engagement, 2),
                "high_performing_count": len(high_performing),
                "low_performing_count": len(low_performing)
            },
            "consistency_analysis": {
                "primary_tone": most_common_tone,
                "tone_consistency_score": round(tone_consistency, 2),
                "tone_distribution": dict(tones_used)
            },
            "hashtag_analysis": {
                "total_unique_hashtags": len(set(all_hashtags)),
                "top_hashtags": [{"hashtag": h, "count": c} for h, c in top_hashtags],
                "avg_hashtags_per_post": round(len(all_hashtags) / total_posts, 2) if total_posts > 0 else 0
            },
            "performance_analysis": {
                "high_performers": [
                    {
                        "post_id": p.get("metadata", {}).get("generated_at"),
                        "platform": p.get("platform"),
                        "engagement_score": p.get("analysis", {}).get("engagement_score", 0)
                    }
                    for p in high_performing[:5]
                ],
                "low_performers": [
                    {
                        "post_id": p.get("metadata", {}).get("generated_at"),
                        "platform": p.get("platform"),
                        "engagement_score": p.get("analysis", {}).get("engagement_score", 0)
                    }
                    for p in low_performing[:5]
                ]
            },
            "recommendations": recommendations,
            "next_steps": [
                "Optimizar posts de bajo rendimiento",
                "Aumentar frecuencia de posts exitosos",
                "Mejorar consistencia de tono",
                "Diversificar tipos de contenido"
            ],
            "audited_at": datetime.now().isoformat()
        }
    
    def generate_competitor_content_gaps(
        self,
        your_posts: List[Dict[str, Any]],
        competitor_posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identifica gaps de contenido vs competidores
        
        Args:
            your_posts: Tus posts
            competitor_posts: Posts de competidores
        
        Returns:
            Análisis de gaps de contenido
        """
        # Analizar temas de competidores
        competitor_topics = set()
        for post in competitor_posts:
            content = post.get("content", "").lower()
            # Extraer temas simples (en producción usaría NLP)
            competitor_topics.add(post.get("post_type", ""))
            competitor_topics.add(post.get("platform", ""))
        
        # Analizar tus temas
        your_topics = set()
        for post in your_posts:
            your_topics.add(post.get("post_type", ""))
            your_topics.add(post.get("platform", ""))
        
        # Identificar gaps
        content_gaps = competitor_topics - your_topics
        
        # Analizar engagement de competidores
        competitor_avg_engagement = sum(
            p.get("performance", {}).get("engagement_rate", 0) for p in competitor_posts
        ) / len(competitor_posts) if competitor_posts else 0
        
        your_avg_engagement = sum(
            p.get("analysis", {}).get("engagement_score", 0) for p in your_posts
        ) / len(your_posts) if your_posts else 0
        
        return {
            "content_gaps": list(content_gaps),
            "opportunities": [
                f"Explorar tipo de contenido: {gap}" for gap in content_gaps
            ],
            "engagement_comparison": {
                "your_avg": round(your_avg_engagement, 2),
                "competitor_avg": round(competitor_avg_engagement, 2),
                "gap": round(competitor_avg_engagement - your_avg_engagement, 2)
            },
            "recommendations": [
                "Cubrir gaps de contenido identificados",
                "Analizar por qué competidores tienen mejor engagement",
                "Adaptar estrategias exitosas de competidores"
            ] if content_gaps else ["Tu contenido cubre bien los temas principales"],
            "analyzed_at": datetime.now().isoformat()
        }
    
    def generate_ai_content_enhancement(
        self,
        post: Dict[str, Any],
        enhancement_type: str = "hook"
    ) -> Dict[str, Any]:
        """
        Mejora contenido usando IA
        
        Args:
            post: Post a mejorar
            enhancement_type: Tipo de mejora (hook, cta, hashtags, full)
        
        Returns:
            Post mejorado con sugerencias de IA
        """
        post_content = post.get("post_content", "")
        analysis = post.get("analysis", {})
        
        enhancements = {
            "original": post_content,
            "enhancements": {},
            "suggestions": []
        }
        
        if enhancement_type == "hook" or enhancement_type == "full":
            # Mejorar hook
            current_hook = post_content.split('\n')[0] if post_content else ""
            enhanced_hooks = [
                f"🔥 {current_hook}",
                f"⚡ {current_hook} - No te lo pierdas",
                f"💡 {current_hook.replace('Descubre', 'Revoluciona tu forma de')}"
            ]
            enhancements["enhancements"]["hooks"] = enhanced_hooks
            enhancements["suggestions"].append("Mejorar hook inicial para mayor impacto")
        
        if enhancement_type == "cta" or enhancement_type == "full":
            # Mejorar CTA
            current_cta = post.get("cta", "Ver más")
            enhanced_ctas = [
                f"👉 {current_cta} ahora",
                f"🚀 {current_cta} y transforma tu negocio",
                f"💪 {current_cta} - Empieza hoy"
            ]
            enhancements["enhancements"]["ctas"] = enhanced_ctas
            enhancements["suggestions"].append("Hacer CTA más urgente y específico")
        
        if enhancement_type == "hashtags" or enhancement_type == "full":
            # Mejorar hashtags
            current_hashtags = post.get("hashtags", [])
            enhanced_hashtags = current_hashtags + [
                "#Trending",
                "#Viral",
                "#MustSee"
            ]
            enhancements["enhancements"]["hashtags"] = enhanced_hashtags[:30]
            enhancements["suggestions"].append("Agregar hashtags trending para mayor alcance")
        
        # Generar versión mejorada completa
        if enhancement_type == "full":
            best_hook = enhancements["enhancements"].get("hooks", [post_content.split('\n')[0]])[0]
            best_cta = enhancements["enhancements"].get("ctas", [post.get("cta", "Ver más")])[0]
            
            enhanced_content = f"""{best_hook}

{post_content}

{best_cta}

{chr(10).join(enhancements['enhancements'].get('hashtags', post.get('hashtags', []))[:25])}"""
            
            enhancements["enhanced_post"] = enhanced_content
        
        return enhancements
    
    def generate_content_performance_prediction_advanced(
        self,
        post: Dict[str, Any],
        similar_posts: List[Dict[str, Any]],
        market_trends: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predicción avanzada de performance usando ML y tendencias
        
        Args:
            post: Post a analizar
            similar_posts: Posts similares históricos
            market_trends: Tendencias de mercado (opcional)
        
        Returns:
            Predicción avanzada de performance
        """
        # Predicción base
        base_prediction = self.predict_performance(post, similar_posts)
        
        # Ajustar basado en tendencias de mercado
        trend_multiplier = 1.0
        if market_trends:
            trend_score = market_trends.get("trend_score", 0.5)  # 0-1
            trend_multiplier = 0.8 + (trend_score * 0.4)  # 0.8-1.2
        
        # Ajustar predicciones
        adjusted_engagement = base_prediction.predicted_engagement * trend_multiplier
        adjusted_reach = int(base_prediction.predicted_reach * trend_multiplier)
        adjusted_conversions = int(base_prediction.predicted_conversions * trend_multiplier)
        
        # Análisis de riesgo
        risk_factors = base_prediction.risk_factors.copy()
        if trend_multiplier < 0.9:
            risk_factors.append("Tendencias de mercado desfavorables")
        
        # Escenarios
        scenarios = {
            "optimistic": {
                "engagement": adjusted_engagement * 1.2,
                "reach": int(adjusted_reach * 1.2),
                "conversions": int(adjusted_conversions * 1.2),
                "probability": 0.25
            },
            "realistic": {
                "engagement": adjusted_engagement,
                "reach": adjusted_reach,
                "conversions": adjusted_conversions,
                "probability": 0.50
            },
            "pessimistic": {
                "engagement": adjusted_engagement * 0.8,
                "reach": int(adjusted_reach * 0.8),
                "conversions": int(adjusted_conversions * 0.8),
                "probability": 0.25
            }
        }
        
        return {
            "base_prediction": asdict(base_prediction),
            "trend_adjusted": {
                "engagement": round(adjusted_engagement, 2),
                "reach": adjusted_reach,
                "conversions": adjusted_conversions,
                "trend_multiplier": round(trend_multiplier, 2)
            },
            "scenarios": scenarios,
            "risk_factors": risk_factors,
            "recommendations": base_prediction.recommendations + [
                "Monitorear tendencias de mercado",
                "Ajustar timing según tendencias"
            ],
            "confidence_score": base_prediction.confidence_score * (1.0 if trend_multiplier >= 1.0 else trend_multiplier),
            "predicted_at": datetime.now().isoformat()
        }
    
    def generate_multi_channel_campaign(
        self,
        campaign_name: str,
        product_name: str,
        target_audience: str,
        platforms: List[str] = None,
        campaign_duration: int = 7
    ) -> Dict[str, Any]:
        """
        Genera campaña completa multi-canal
        
        Args:
            campaign_name: Nombre de la campaña
            product_name: Nombre del producto
            target_audience: Audiencia objetivo
            platforms: Plataformas (default: todas principales)
            campaign_duration: Duración en días
        
        Returns:
            Campaña completa multi-canal
        """
        if platforms is None:
            platforms = ["instagram", "linkedin", "tiktok", "facebook", "twitter"]
        
        campaign = {
            "campaign_name": campaign_name,
            "product_name": product_name,
            "target_audience": target_audience,
            "duration_days": campaign_duration,
            "platforms": platforms,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=campaign_duration)).isoformat(),
            "content": {},
            "strategy": {
                "teaser_phase": {"days": [1, 2], "goal": "Awareness"},
                "demo_phase": {"days": [3, 4, 5], "goal": "Education"},
                "offer_phase": {"days": [6, 7], "goal": "Conversion"}
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Generar contenido por fase y plataforma
        for phase, phase_info in campaign["strategy"].items():
            campaign["content"][phase] = {}
            post_type = phase.replace("_phase", "")
            
            for platform in platforms:
                try:
                    post = self.generate_post(
                        platform=platform,
                        post_type=post_type,
                        product_name=product_name,
                        target_audience=target_audience
                    )
                    
                    campaign["content"][phase][platform] = post
                except Exception as e:
                    logger.error(f"Error generando contenido para {platform}: {e}")
        
        # Agregar calendario
        campaign["calendar"] = self.generate_content_calendar(
            start_date=datetime.now(),
            days=campaign_duration,
            platforms=platforms,
            post_type_sequence=["teaser", "teaser", "demo", "demo", "demo", "offer", "offer"]
        )
        
        return campaign


def main():
    """Función principal para ejecución desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Generador Avanzado de Posts para Redes Sociales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Post básico para Instagram
  python campaign_post_generator.py --platform instagram --post-type teaser \\
    --product "Mi Nuevo Producto" --audience "emprendedores"

  # Post con promoción
  python campaign_post_generator.py --platform instagram --post-type offer \\
    --product "Mi Producto" --audience "empresarios" \\
    --promotion '{"regular_price": "99", "discount_price": "79", "discount_percent": "20"}'

  # Post con datos personalizados
  python campaign_post_generator.py --platform linkedin --post-type demo \\
    --product "SaaS Tool" --audience "B2B professionals" \\
    --custom-data '{"benefit_1": "Ahorra 10 horas", "metric_1": "por semana"}'
        """
    )
    
    parser.add_argument(
        "--platform",
        required=True,
        choices=["instagram", "linkedin", "tiktok", "facebook", "twitter", "youtube"],
        help="Plataforma de redes sociales"
    )
    
    parser.add_argument(
        "--post-type",
        required=True,
        choices=["teaser", "demo", "offer"],
        help="Tipo de post (teaser, demo, offer)"
    )
    
    parser.add_argument(
        "--product",
        required=True,
        help="Nombre del producto/servicio"
    )
    
    parser.add_argument(
        "--audience",
        required=True,
        help="Audiencia objetivo"
    )
    
    parser.add_argument(
        "--tone",
        default="amigable",
        choices=["profesional", "amigable", "urgente", "emocional", "casual"],
        help="Tono de voz (default: amigable)"
    )
    
    parser.add_argument(
        "--promotion",
        type=str,
        help="Detalles de promoción en formato JSON"
    )
    
    parser.add_argument(
        "--custom-data",
        type=str,
        help="Datos personalizados en formato JSON"
    )
    
    parser.add_argument(
        "--variation",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="Variación del template (1, 2, o 3)"
    )
    
    parser.add_argument(
        "--no-hashtags",
        action="store_true",
        help="No incluir hashtags"
    )
    
    parser.add_argument(
        "--no-cta",
        action="store_true",
        help="No incluir call-to-action"
    )
    
    parser.add_argument(
        "--output",
        choices=["json", "text", "markdown", "csv", "html"],
        default="json",
        help="Formato de salida (default: json)"
    )
    
    parser.add_argument(
        "--generate-variations",
        type=int,
        metavar="N",
        help="Generar N variaciones (1-3) para A/B testing"
    )
    
    parser.add_argument(
        "--compare-variations",
        action="store_true",
        help="Comparar variaciones generadas y recomendar la mejor"
    )
    
    parser.add_argument(
        "--generate-stories",
        action="store_true",
        help="Generar contenido para Stories basado en el post"
    )
    
    parser.add_argument(
        "--stories-slides",
        type=int,
        default=8,
        help="Número de slides para Stories (default: 8)"
    )
    
    args = parser.parse_args()
    
    # Parsear JSON si se proporciona
    promotion_details = {}
    if args.promotion:
        try:
            promotion_details = json.loads(args.promotion)
        except json.JSONDecodeError:
            logger.error("Error parseando JSON de promoción")
            sys.exit(1)
    
    custom_data = {}
    if args.custom_data:
        try:
            custom_data = json.loads(args.custom_data)
        except json.JSONDecodeError:
            logger.error("Error parseando JSON de datos personalizados")
            sys.exit(1)
    
    # Generar post
    generator = CampaignPostGenerator(enable_optimization=True)
    try:
        # Generar múltiples variaciones si se solicita
        if args.generate_variations:
            variations = generator.generate_multiple_variations(
                platform=args.platform,
                post_type=args.post_type,
                product_name=args.product,
                target_audience=args.audience,
                tone=args.tone,
                promotion_details=promotion_details,
                custom_data=custom_data,
                num_variations=args.generate_variations,
                include_hashtags=not args.no_hashtags,
                include_cta=not args.no_cta
            )
            
            # Comparar variaciones si se solicita
            if args.compare_variations:
                comparison = generator.compare_variations(variations)
                result = {
                    "variations": variations,
                    "comparison": asdict(comparison)
                }
            else:
                result = {"variations": variations}
        else:
            # Generar un solo post
            result = generator.generate_post(
                platform=args.platform,
                post_type=args.post_type,
                product_name=args.product,
                target_audience=args.audience,
                tone=args.tone,
                promotion_details=promotion_details,
                custom_data=custom_data,
                variation=args.variation,
                include_hashtags=not args.no_hashtags,
                include_cta=not args.no_cta
            )
            
            # Generar Stories si se solicita
            if args.generate_stories:
                story_content = generator.generate_story_content(
                    platform=args.platform,
                    post_type=args.post_type,
                    product_name=args.product,
                    target_audience=args.audience,
                    base_post=result,
                    num_slides=args.stories_slides
                )
                result["story_content"] = asdict(story_content)
        
        # Formatear salida
        if args.output == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.output == "text":
            if isinstance(result, dict) and "variations" in result:
                for i, var in enumerate(result["variations"], 1):
                    print(f"\n=== VARIACIÓN {i} ===\n")
                    print(var["full_post"])
            else:
                print(result.get("full_post", json.dumps(result, indent=2)))
        else:
            # Usar método de exportación
            if isinstance(result, dict) and "variations" in result:
                # Exportar primera variación como ejemplo
                export_result = generator.export_to_format(result["variations"][0], args.output)
                print(export_result)
            else:
                export_result = generator.export_to_format(result, args.output)
                print(export_result)
        
    except Exception as e:
        logger.error(f"Error generando post: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

