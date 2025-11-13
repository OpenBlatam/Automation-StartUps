#!/usr/bin/env python3
"""
Script para convertir testimonios de clientes en publicaciones narrativas para redes sociales
Convierte testimonios en contenido atractivo enfocado en resultados, con tono cálido y profesional
"""

import os
import sys
import json
import argparse
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai no está instalado. Instálalo con: pip install openai")
    sys.exit(1)

# Importar funcionalidades avanzadas
try:
    from testimonial_advanced_features import (
        SentimentAnalyzer,
        KeywordAnalyzer,
        TemplateManager,
        SimpleCache,
        FormatGenerator
    )
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Funcionalidades avanzadas no disponibles. Instala dependencias adicionales si las necesitas.")

# Importar optimizador de engagement
try:
    from testimonial_engagement_optimizer import EngagementOptimizer
    ENGAGEMENT_OPTIMIZER_AVAILABLE = True
except ImportError:
    ENGAGEMENT_OPTIMIZER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.debug("Optimizador de engagement no disponible")

# Importar generador de reportes
try:
    from testimonial_analytics_reporter import AnalyticsReporter
    ANALYTICS_REPORTER_AVAILABLE = True
except ImportError:
    ANALYTICS_REPORTER_AVAILABLE = False
    logger.debug("Generador de reportes no disponible")

# Importar comparador de variaciones
try:
    from testimonial_variation_comparator import VariationComparator
    VARIATION_COMPARATOR_AVAILABLE = True
except ImportError:
    VARIATION_COMPARATOR_AVAILABLE = False
    logger.debug("Comparador de variaciones no disponible")

# Importar generador de dashboard
try:
    from testimonial_dashboard_generator import DashboardGenerator
    DASHBOARD_GENERATOR_AVAILABLE = True
except ImportError:
    DASHBOARD_GENERATOR_AVAILABLE = False
    logger.debug("Generador de dashboard no disponible")

# Importar tracker de publicaciones
try:
    from testimonial_tracker import PostTracker
    POST_TRACKER_AVAILABLE = True
except ImportError:
    POST_TRACKER_AVAILABLE = False
    logger.debug("Tracker de publicaciones no disponible")

# Importar predictor ML
try:
    from testimonial_ml_predictor import MLPredictor
    ML_PREDICTOR_AVAILABLE = True
except ImportError:
    ML_PREDICTOR_AVAILABLE = False
    logger.debug("Predictor ML no disponible")

# Importar sistema de alertas
try:
    from testimonial_alert_system import AlertSystem
    ALERT_SYSTEM_AVAILABLE = True
except ImportError:
    ALERT_SYSTEM_AVAILABLE = False
    logger.debug("Sistema de alertas no disponible")

# Importar generador de calendario
try:
    from testimonial_content_calendar import ContentCalendarGenerator
    CALENDAR_GENERATOR_AVAILABLE = True
except ImportError:
    CALENDAR_GENERATOR_AVAILABLE = False
    logger.debug("Generador de calendario no disponible")

# Importar calculadora de ROI
try:
    from testimonial_roi_calculator import ROICalculator
    ROI_CALCULATOR_AVAILABLE = True
except ImportError:
    ROI_CALCULATOR_AVAILABLE = False
    logger.debug("Calculadora de ROI no disponible")

# Importar sistema de versionado
try:
    from testimonial_version_control import VersionControl
    VERSION_CONTROL_AVAILABLE = True
except ImportError:
    VERSION_CONTROL_AVAILABLE = False
    logger.debug("Sistema de versionado no disponible")

# Importar analizador de competidores
try:
    from testimonial_competitor_analyzer import CompetitorAnalyzer
    COMPETITOR_ANALYZER_AVAILABLE = True
except ImportError:
    COMPETITOR_ANALYZER_AVAILABLE = False
    logger.debug("Analizador de competidores no disponible")

# Importar gestor de exportación avanzada
try:
    from testimonial_export_manager import ExportManager
    EXPORT_MANAGER_AVAILABLE = True
except ImportError:
    EXPORT_MANAGER_AVAILABLE = False
    logger.debug("Gestor de exportación avanzada no disponible")

# Importar motor de plantillas
try:
    from testimonial_template_engine import TemplateEngine
    TEMPLATE_ENGINE_AVAILABLE = True
except ImportError:
    TEMPLATE_ENGINE_AVAILABLE = False
    logger.debug("Motor de plantillas no disponible")

# Importar traductor multi-idioma
try:
    from testimonial_translator import MultiLanguageTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.debug("Traductor multi-idioma no disponible")

# Importar integración con BD
try:
    from testimonial_database_integration import DatabaseIntegration
    DATABASE_INTEGRATION_AVAILABLE = True
except ImportError:
    DATABASE_INTEGRATION_AVAILABLE = False
    logger.debug("Integración con BD no disponible")

# Importar programador de publicaciones
try:
    from testimonial_scheduler import PostScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    logger.debug("Programador de publicaciones no disponible")

# Importar integración con APIs sociales
try:
    from testimonial_social_api_integration import SocialMediaAPI
    SOCIAL_API_AVAILABLE = True
except ImportError:
    SOCIAL_API_AVAILABLE = False
    logger.debug("Integración con APIs sociales no disponible")

# Importar sistema de notificaciones
try:
    from testimonial_notification_system import NotificationSystem
    NOTIFICATION_SYSTEM_AVAILABLE = True
except ImportError:
    NOTIFICATION_SYSTEM_AVAILABLE = False
    logger.debug("Sistema de notificaciones no disponible")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestimonialToSocialPostConverter:
    """Clase para convertir testimonios de clientes en publicaciones para redes sociales"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Inicializa el convertidor de testimonios
        
        Args:
            openai_api_key: Clave API de OpenAI. Si es None, intenta obtenerla de OPENAI_API_KEY
            model: Modelo de OpenAI a usar (default: gpt-4o-mini)
        
        Raises:
            ValueError: Si la API key no está configurada
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY no está configurada. "
                "Configúrala como variable de entorno o pásala como parámetro."
            )
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.model = model
            logger.info(f"Convertidor inicializado con modelo: {model}")
            
            # Inicializar funcionalidades avanzadas si están disponibles
            if ADVANCED_FEATURES_AVAILABLE:
                self.sentiment_analyzer = SentimentAnalyzer()
                self.keyword_analyzer = KeywordAnalyzer()
                self.template_manager = TemplateManager()
                self.format_generator = FormatGenerator()
                # Cache opcional (desactivado por defecto)
                self.cache = None
                logger.info("Funcionalidades avanzadas habilitadas")
            else:
                self.sentiment_analyzer = None
                self.keyword_analyzer = None
                self.template_manager = None
                self.format_generator = None
                self.cache = None
            
            # Inicializar optimizador de engagement
            if ENGAGEMENT_OPTIMIZER_AVAILABLE:
                self.engagement_optimizer = EngagementOptimizer()
                logger.info("Optimizador de engagement habilitado")
            else:
                self.engagement_optimizer = None
            
            # Inicializar generador de reportes
            if ANALYTICS_REPORTER_AVAILABLE:
                self.analytics_reporter = AnalyticsReporter()
                logger.info("Generador de reportes habilitado")
            else:
                self.analytics_reporter = None
            
            # Inicializar comparador de variaciones
            if VARIATION_COMPARATOR_AVAILABLE:
                self.variation_comparator = VariationComparator()
                logger.info("Comparador de variaciones habilitado")
            else:
                self.variation_comparator = None
            
            # Inicializar generador de dashboard
            if DASHBOARD_GENERATOR_AVAILABLE:
                self.dashboard_generator = DashboardGenerator()
                logger.info("Generador de dashboard habilitado")
            else:
                self.dashboard_generator = None
            
            # Inicializar tracker (opcional, se puede configurar después)
            self.post_tracker = None
            
            # Inicializar predictor ML (opcional)
            self.ml_predictor = None
            
            # Inicializar sistema de alertas
            if ALERT_SYSTEM_AVAILABLE:
                self.alert_system = AlertSystem()
                logger.info("Sistema de alertas habilitado")
            else:
                self.alert_system = None
            
            # Inicializar generador de calendario
            if CALENDAR_GENERATOR_AVAILABLE:
                self.calendar_generator = ContentCalendarGenerator()
                logger.info("Generador de calendario habilitado")
            else:
                self.calendar_generator = None
            
            # Inicializar calculadora de ROI
            if ROI_CALCULATOR_AVAILABLE:
                self.roi_calculator = ROICalculator()
                logger.info("Calculadora de ROI habilitada")
            else:
                self.roi_calculator = None
            
            # Inicializar sistema de versionado (opcional)
            self.version_control = None
            
            # Inicializar analizador de competidores
            if COMPETITOR_ANALYZER_AVAILABLE:
                self.competitor_analyzer = CompetitorAnalyzer()
                logger.info("Analizador de competidores habilitado")
            else:
                self.competitor_analyzer = None
            
            # Inicializar gestor de exportación avanzada
            if EXPORT_MANAGER_AVAILABLE:
                self.export_manager = ExportManager()
                logger.info("Gestor de exportación avanzada habilitado")
            else:
                self.export_manager = None
            
            # Inicializar motor de plantillas (opcional)
            self.template_engine = None
            
            # Inicializar traductor (opcional, requiere OpenAI)
            if TRANSLATOR_AVAILABLE:
                self.translator = MultiLanguageTranslator(openai_client=self.client)
                logger.info("Traductor multi-idioma habilitado")
            else:
                self.translator = None
            
            # Inicializar integración con BD (opcional)
            self.database = None
            
            # Inicializar programador (opcional)
            if SCHEDULER_AVAILABLE:
                self.scheduler = PostScheduler()
                logger.info("Programador de publicaciones habilitado")
            else:
                self.scheduler = None
            
            # Inicializar integración con APIs sociales (opcional)
            if SOCIAL_API_AVAILABLE:
                self.social_api = SocialMediaAPI()
                logger.info("Integración con APIs sociales habilitada")
            else:
                self.social_api = None
            
            # Inicializar sistema de notificaciones (opcional)
            if NOTIFICATION_SYSTEM_AVAILABLE:
                self.notification_system = NotificationSystem()
                logger.info("Sistema de notificaciones habilitado")
            else:
                self.notification_system = None
        except Exception as e:
            logger.error(f"Error al inicializar cliente de OpenAI: {e}")
            raise
    
    def convert_testimonial(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str = "general",
        tone: str = "cálido y profesional",
        max_length: Optional[int] = None,
        include_hashtags: bool = True,
        include_call_to_action: bool = True,
        enable_cache: bool = False,
        analyze_sentiment: bool = False,
        template_id: Optional[str] = None,
        predict_engagement: bool = False,
        optimize_for_engagement: bool = False
    ) -> Dict[str, Any]:
        """
        Convierte un testimonio en una publicación narrativa para redes sociales
        
        Args:
            testimonial: Texto del testimonio del cliente
            target_audience_problem: Problema o resultado que busca el público objetivo
            platform: Plataforma objetivo (general, instagram, facebook, linkedin, twitter, tiktok)
            tone: Tono deseado (default: "cálido y profesional")
            max_length: Longitud máxima en caracteres (None = sin límite)
            include_hashtags: Si incluir hashtags relevantes
            include_call_to_action: Si incluir llamada a la acción
        
        Returns:
            Dict con la publicación generada y metadatos
        
        Raises:
            ValueError: Si los parámetros requeridos están vacíos o son inválidos
            Exception: Si hay un error al generar la publicación
        """
        # Validar inputs
        if not testimonial or not testimonial.strip():
            raise ValueError("El testimonio no puede estar vacío")
        
        if not target_audience_problem or not target_audience_problem.strip():
            raise ValueError("El problema/resultado del público objetivo no puede estar vacío")
        
        testimonial = testimonial.strip()
        target_audience_problem = target_audience_problem.strip()
        platform = platform.lower().strip()
        
        logger.info(f"Convirtiendo testimonio para plataforma: {platform}, tono: {tone}")
        
        # Verificar cache si está habilitado
        if enable_cache and self.cache:
            cached_result = self.cache.get(testimonial, target_audience_problem, platform)
            if cached_result:
                logger.info("Resultado obtenido del cache")
                return cached_result
        
        # Análisis de sentimiento y keywords si está habilitado
        sentiment_data = None
        keyword_data = None
        if analyze_sentiment and self.sentiment_analyzer:
            logger.debug("Analizando sentimiento y keywords...")
            sentiment_data = self.sentiment_analyzer.analyze(testimonial)
            keyword_data = self.keyword_analyzer.analyze(testimonial)
            logger.debug(f"Sentimiento: {sentiment_data.sentiment} (score: {sentiment_data.score})")
        
        # Configuración específica por plataforma
        platform_configs = {
            "instagram": {
                "max_length": max_length or 2200,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            },
            "facebook": {
                "max_length": max_length or 5000,
                "hashtags_count": 3,
                "emoji": True,
                "line_breaks": True
            },
            "linkedin": {
                "max_length": max_length or 3000,
                "hashtags_count": 5,
                "emoji": False,
                "line_breaks": True,
                "tone": "profesional y empático"
            },
            "twitter": {
                "max_length": max_length or 280,
                "hashtags_count": 2,
                "emoji": True,
                "line_breaks": False
            },
            "tiktok": {
                "max_length": max_length or 300,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            },
            "general": {
                "max_length": max_length or 1000,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            }
        }
        
        config = platform_configs.get(platform, platform_configs["general"])
        
        # Validar longitud del testimonio antes de procesar
        if len(testimonial) > 5000:
            logger.warning(f"Testimonio muy largo ({len(testimonial)} caracteres). Se procesará completo pero puede afectar la calidad.")
        
        # Ajustar prompt según template si se especifica
        template_data = None
        if template_id and self.template_manager:
            template_data = self.template_manager.get_template(template_id)
            if template_data:
                logger.info(f"Usando template: {template_data.get('name', template_id)}")
        
        # Construir el prompt para la IA
        prompt = self._build_prompt(
            testimonial=testimonial,
            target_audience_problem=target_audience_problem,
            platform=platform,
            tone=tone,
            config=config,
            include_hashtags=include_hashtags,
            include_call_to_action=include_call_to_action,
            sentiment_data=sentiment_data,
            keyword_data=keyword_data,
            template_data=template_data
        )
        
        # Generar la publicación usando OpenAI
        try:
            logger.debug("Enviando solicitud a OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un experto en marketing de contenidos y copywriting para redes sociales. "
                            "Especializas en convertir testimonios de clientes en publicaciones narrativas "
                            "que conectan emocionalmente con la audiencia y destacan resultados concretos. "
                            "Tu objetivo es crear contenido auténtico, convincente y orientado a resultados."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            generated_content = response.choices[0].message.content.strip()
            logger.debug(f"Contenido generado ({len(generated_content)} caracteres)")
            
            # Extraer hashtags y CTA si están incluidos
            post_content, hashtags, cta = self._parse_generated_content(
                generated_content,
                include_hashtags=include_hashtags,
                include_call_to_action=include_call_to_action
            )
            
            # Validar longitud
            if config["max_length"] and len(post_content) > config["max_length"]:
                logger.info(f"Publicación excede límite ({len(post_content)} > {config['max_length']}). Acortando...")
                post_content = self._shorten_post(post_content, config["max_length"])
            
            full_post = self._combine_post_parts(post_content, hashtags, cta, config)
            
            result = {
                "post_content": post_content,
                "hashtags": hashtags,
                "call_to_action": cta,
                "full_post": full_post,
                "platform": platform,
                "length": len(post_content),
                "full_length": len(full_post),
                "max_length": config["max_length"],
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "original_testimonial_length": len(testimonial),
                    "tone": tone,
                    "target_audience": target_audience_problem,
                    "model_used": self.model
                }
            }
            
            # Agregar análisis si está disponible
            if sentiment_data:
                result["sentiment_analysis"] = {
                    "sentiment": sentiment_data.sentiment,
                    "score": sentiment_data.score,
                    "confidence": sentiment_data.confidence,
                    "emotional_intensity": sentiment_data.emotional_intensity
                }
            
            if keyword_data:
                result["keyword_analysis"] = {
                    "main_keywords": keyword_data.main_keywords,
                    "topics": keyword_data.topics,
                    "metrics_mentioned": keyword_data.metrics_mentioned,
                    "action_words": keyword_data.action_words
                }
            
            # Predicción y optimización de engagement
            if predict_engagement and self.engagement_optimizer:
                has_numbers = bool(re.search(r'\d+%|\d+\s*(veces|meses|años)', post_content))
                has_emojis = bool(re.findall(r'[😀-🙏🌀-🗿]', post_content))
                
                engagement_prediction = self.engagement_optimizer.predict_engagement(
                    post_content=post_content,
                    hashtags=hashtags,
                    platform=platform,
                    has_cta=bool(cta),
                    has_numbers=has_numbers,
                    has_emojis=has_emojis
                )
                
                base_prediction = {
                    "predicted_score": engagement_prediction.predicted_score,
                    "predicted_engagement_rate": engagement_prediction.predicted_engagement_rate,
                    "confidence": engagement_prediction.confidence,
                    "factors": engagement_prediction.factors,
                    "recommendations": engagement_prediction.recommendations,
                    "optimal_posting_time": engagement_prediction.optimal_posting_time
                }
                
                # Mejorar predicción con ML si está disponible
                if self.ml_predictor:
                    improved_prediction = self.ml_predictor.improve_prediction(
                        base_prediction=base_prediction,
                        factors=engagement_prediction.factors,
                        platform=platform
                    )
                    result["engagement_prediction"] = improved_prediction
                    result["ml_improvement"] = {
                        "improved": True,
                        "improvement_amount": improved_prediction.get("improvement_amount", 0),
                        "base_score": base_prediction["predicted_score"]
                    }
                else:
                    result["engagement_prediction"] = base_prediction
                
                # Optimización adicional si se solicita
                if optimize_for_engagement:
                    optimization = self.engagement_optimizer.optimize_content(
                        post_content=post_content,
                        hashtags=hashtags,
                        platform=platform,
                        current_hashtags=hashtags
                    )
                    
                    result["engagement_optimization"] = {
                        "hashtag_suggestions": optimization.hashtag_suggestions,
                        "length_optimization": optimization.length_optimization,
                        "tone_adjustments": optimization.tone_adjustments,
                        "structure_improvements": optimization.structure_improvements,
                        "engagement_boosters": optimization.engagement_boosters
                    }
                    
                    # Obtener horario óptimo
                    schedule = self.engagement_optimizer.get_optimal_posting_schedule(platform)
                    result["optimal_posting_schedule"] = schedule
                
                # Calcular ROI si está disponible
                if self.roi_calculator and "engagement_prediction" in result:
                    estimated_reach = result.get("estimated_reach", 2000)  # Default reach
                    roi = self.roi_calculator.calculate_roi(
                        predicted_engagement_rate=result["engagement_prediction"].get("predicted_engagement_rate", 0),
                        estimated_reach=estimated_reach,
                        platform=platform
                    )
                    result["roi_calculation"] = {
                        "estimated_reach": roi.estimated_reach,
                        "estimated_engagement": roi.estimated_engagement,
                        "estimated_clicks": roi.estimated_clicks,
                        "estimated_conversions": roi.estimated_conversions,
                        "estimated_revenue": roi.estimated_revenue,
                        "cost_per_post": roi.cost_per_post,
                        "roi_percentage": roi.roi_percentage,
                        "roi_multiplier": roi.roi_multiplier,
                        "payback_period_days": roi.payback_period_days
                    }
            
            # Generar alertas si el sistema está disponible
            if self.alert_system:
                historical_data = []
                if self.engagement_optimizer and hasattr(self.engagement_optimizer, 'historical_data'):
                    historical_data = self.engagement_optimizer.historical_data
                
                alerts = self.alert_system.analyze_and_alert(
                    post_data=result,
                    platform=platform,
                    historical_data=historical_data
                )
                if alerts:
                    result["alerts"] = [
                        {
                            "level": alert.level.value,
                            "title": alert.title,
                            "message": alert.message,
                            "recommendation": alert.recommendation,
                            "action_required": alert.action_required
                        }
                        for alert in alerts
                    ]
                    result["alerts_summary"] = self.alert_system.get_alerts_summary()
            
            # Guardar versión si el versionado está habilitado
            if self.version_control:
                post_id = result.get('metadata', {}).get('post_id', f"post_{datetime.now().timestamp()}")
                self.version_control.create_version(
                    post_id=post_id,
                    post_data=result,
                    changes_summary="Versión inicial generada",
                    tags=["generated"]
                )
            
            # Guardar en cache si está habilitado
            if enable_cache and self.cache:
                self.cache.set(testimonial, target_audience_problem, platform, result)
            
            logger.info(f"Publicación generada exitosamente: {result['length']} caracteres")
            return result
            
        except Exception as e:
            error_msg = f"Error al generar la publicación: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def _build_prompt(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str,
        tone: str,
        config: Dict[str, Any],
        include_hashtags: bool,
        include_call_to_action: bool,
        sentiment_data: Optional[Any] = None,
        keyword_data: Optional[Any] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construye el prompt para la generación de la publicación"""
        
        # Ajustar tono según plataforma si es LinkedIn
        final_tone = config.get("tone", tone) if platform == "linkedin" else tone
        
        # Agregar información de análisis si está disponible
        analysis_context = ""
        if sentiment_data:
            analysis_context += f"\n- Sentimiento detectado: {sentiment_data.sentiment} (intensidad: {sentiment_data.emotional_intensity})\n"
        if keyword_data and keyword_data.metrics_mentioned:
            analysis_context += f"- Métricas mencionadas: {', '.join(keyword_data.metrics_mentioned[:3])}\n"
        if keyword_data and keyword_data.topics:
            analysis_context += f"- Temas principales: {', '.join(keyword_data.topics[:3])}\n"
        
        # Agregar estructura de template si está disponible
        template_instructions = ""
        if template_data:
            structure = template_data.get('structure', [])
            if structure:
                template_instructions = f"\nESTRUCTURA DEL TEMPLATE '{template_data.get('name', 'personalizado')}':\n"
                for i, step in enumerate(structure, 1):
                    template_instructions += f"{i}. {step}\n"
        
        prompt = f"""Convierte el siguiente testimonio de cliente en una publicación narrativa para {platform.upper()}.

TESTIMONIO DEL CLIENTE:
"{testimonial}"
{analysis_context}
CONTEXTO Y OBJETIVO:
- Público objetivo: Personas que buscan {target_audience_problem}
- Tono: {final_tone}
- Plataforma: {platform.upper()}
{template_instructions}

REQUISITOS TÉCNICOS:
- Longitud máxima del contenido principal: {config['max_length']} caracteres
- Formato: {'Con saltos de línea para legibilidad' if config['line_breaks'] else 'Texto continuo'}
- Emojis: {'Sí, usa emojis relevantes (máximo 3-5)' if config['emoji'] else 'No uses emojis'}

ESTRUCTURA NARRATIVA:
1. Hook inicial (1-2 líneas): Captura la atención mencionando el problema o resultado clave
2. Cuerpo narrativo: Relata el testimonio enfocándote en:
   - El RESULTADO CONCRETO obtenido (números, porcentajes, mejoras específicas)
   - La experiencia del cliente (qué sintió, cómo cambió su situación)
   - El valor percibido (por qué fue importante para ellos)
3. Cierre: Conecta con el público objetivo de manera empática

ENFOQUE ESPECIAL:
- Destaca números, porcentajes y resultados medibles si están presentes
- Usa lenguaje emocional pero auténtico
- Evita exageraciones o lenguaje demasiado promocional
- Mantén la autenticidad del testimonio original
"""
        
        if include_hashtags:
            prompt += f"\n- Incluye {config['hashtags_count']} hashtags relevantes al final (en una línea separada)"
        
        if include_call_to_action:
            prompt += "\n- Incluye una llamada a la acción sutil y natural al final (antes de los hashtags si los hay)"
        
        prompt += "\n\nIMPORTANTE: Genera SOLO el contenido de la publicación, sin explicaciones adicionales, sin prefijos como 'Publicación:' o 'Aquí está:'. Empieza directamente con el hook."
        
        return prompt
    
    def _parse_generated_content(
        self,
        content: str,
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> Tuple[str, List[str], Optional[str]]:
        """
        Extrae el contenido principal, hashtags y CTA del texto generado
        
        Returns:
            Tuple con (contenido_principal, lista_hashtags, cta)
        """
        
        hashtags = []
        cta = None
        post_content = content
        
        # Limpiar contenido de prefijos comunes
        prefixes_to_remove = [
            "Publicación:",
            "Aquí está:",
            "Publicación para",
            "Contenido:",
            "Texto:"
        ]
        for prefix in prefixes_to_remove:
            if post_content.strip().startswith(prefix):
                post_content = post_content.replace(prefix, "", 1).strip()
        
        # Extraer hashtags usando regex para mayor precisión
        if include_hashtags:
            # Buscar hashtags en todo el contenido
            hashtag_pattern = r'#\w+'
            found_hashtags = re.findall(hashtag_pattern, content)
            
            if found_hashtags:
                hashtags = list(set(found_hashtags))  # Eliminar duplicados manteniendo orden
                # Remover hashtags del contenido principal
                for hashtag in found_hashtags:
                    post_content = re.sub(re.escape(hashtag), '', post_content)
        
        # Extraer CTA (últimas líneas que contengan verbos de acción)
        if include_call_to_action:
            cta_keywords = [
                'comienza', 'descubre', 'prueba', 'contacta', 'solicita', 'aprende', 
                'conecta', 'consulta', 'visita', 'sigue', 'únete', 'explora', 
                'conoce', 'descubre más', 'empieza', 'obtén', 'accede'
            ]
            lines = [line.strip() for line in post_content.split('\n') if line.strip()]
            
            # Buscar CTA en las últimas 2-3 líneas
            for line in reversed(lines[-3:]):
                line_lower = line.lower()
                # Verificar si contiene palabras clave de CTA
                if any(keyword in line_lower for keyword in cta_keywords):
                    # Verificar que no sea solo un hashtag
                    if not line.strip().startswith('#'):
                        cta = line.strip()
                        # Remover CTA del contenido principal
                        post_content = post_content.replace(line, '').strip()
                        break
        
        # Limpiar espacios múltiples y saltos de línea excesivos
        post_content = re.sub(r'\n{3,}', '\n\n', post_content)
        post_content = re.sub(r' +', ' ', post_content)
        
        return post_content.strip(), hashtags, cta
    
    def _shorten_post(self, content: str, max_length: int) -> str:
        """
        Acorta una publicación si excede la longitud máxima
        
        Args:
            content: Contenido a acortar
            max_length: Longitud máxima deseada
        
        Returns:
            Contenido acortado manteniendo el mensaje principal
        """
        if len(content) <= max_length:
            return content
        
        logger.info(f"Acortando contenido de {len(content)} a {max_length} caracteres")
        
        # Intentar acortar manteniendo el mensaje principal usando IA
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un experto en copywriting. Tu tarea es acortar textos "
                            "manteniendo el mensaje principal, el impacto emocional y los resultados clave. "
                            "Prioriza números, porcentajes y resultados concretos."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Acorta este texto a máximo {max_length} caracteres, "
                            f"manteniendo el mensaje principal, el impacto emocional y los resultados clave:\n\n{content}"
                        )
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            shortened = response.choices[0].message.content.strip()
            logger.debug(f"Contenido acortado con IA: {len(shortened)} caracteres")
            return shortened
        except Exception as e:
            logger.warning(f"Error al acortar con IA: {e}. Usando método de truncamiento inteligente.")
            # Fallback: truncar de forma inteligente
            return self._intelligent_truncate(content, max_length)
    
    def _intelligent_truncate(self, content: str, max_length: int) -> str:
        """
        Trunca contenido de forma inteligente buscando puntos de corte naturales
        
        Args:
            content: Contenido a truncar
            max_length: Longitud máxima
        
        Returns:
            Contenido truncado
        """
        if len(content) <= max_length:
            return content
        
        # Buscar puntos de corte naturales
        truncated = content[:max_length]
        
        # Priorizar puntos de corte: punto seguido de espacio > punto > salto de línea > espacio
        cut_points = [
            truncated.rfind('. '),
            truncated.rfind('.\n'),
            truncated.rfind('.'),
            truncated.rfind('\n'),
            truncated.rfind(' '),
        ]
        
        # Encontrar el mejor punto de corte (el más cercano al límite pero válido)
        best_cut = -1
        for cut in cut_points:
            if cut > max_length * 0.6:  # Al menos 60% del contenido
                best_cut = max(best_cut, cut)
        
        if best_cut > 0:
            result = truncated[:best_cut + 1].strip()
            # Agregar elipsis solo si realmente cortamos contenido significativo
            if len(result) < len(content) * 0.9:
                result += "..."
            return result
        
        # Si no encontramos buen punto, truncar y agregar elipsis
        return truncated.strip() + "..."
    
    def _combine_post_parts(
        self,
        post_content: str,
        hashtags: List[str],
        cta: Optional[str],
        config: Dict[str, Any]
    ) -> str:
        """Combina todas las partes de la publicación en un texto completo"""
        parts = [post_content]
        
        if cta:
            parts.append(f"\n\n{cta}")
        
        if hashtags:
            hashtag_line = " ".join(hashtags)
            parts.append(f"\n\n{hashtag_line}")
        
        return "\n".join(parts)
    
    def generate_multiple_formats(
        self,
        post_content: str,
        platform: str = "general"
    ) -> Dict[str, Any]:
        """
        Genera múltiples formatos del mismo contenido para diferentes usos
        
        Args:
            post_content: Contenido principal de la publicación
            platform: Plataforma objetivo
        
        Returns:
            Dict con diferentes formatos generados
        """
        if not self.format_generator:
            return {"error": "FormatGenerator no disponible"}
        
        formats = {
            "original": post_content,
            "carousel_slides": self.format_generator.generate_carousel_captions(post_content, slide_count=3),
            "story_text": self.format_generator.generate_story_text(post_content),
            "thread_tweets": self.format_generator.generate_thread_tweets(post_content)
        }
        
        return formats
    
    def generate_multiple_variations(
        self,
        testimonial: str,
        target_audience_problem: str,
        platforms: List[str] = None,
        count: int = 3,
        enable_ab_testing: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Genera múltiples variaciones de la publicación para diferentes plataformas o estilos
        
        Args:
            testimonial: Texto del testimonio
            target_audience_problem: Problema o resultado buscado
            platforms: Lista de plataformas (None = generar variaciones generales)
            count: Número de variaciones por plataforma
        
        Returns:
            Lista de publicaciones generadas
        """
        if platforms is None:
            platforms = ["general"]
        
        all_posts = []
        
        for platform in platforms:
            for i in range(count):
                # Variar ligeramente el tono para cada variación
                if enable_ab_testing:
                    # Para A/B testing, usar variaciones más contrastadas
                    tones = [
                        "cálido y emocional",
                        "profesional y técnico",
                        "directo y convincente",
                        "inspirador y motivador"
                    ]
                else:
                    tones = [
                        "cálido y profesional",
                        "inspirador y empático",
                        "directo y convincente"
                    ]
                tone = tones[i % len(tones)]
                
                # Variar template para A/B testing
                template_id = None
                if enable_ab_testing and self.template_manager:
                    available_templates = list(self.template_manager.templates.keys())
                    if available_templates:
                        template_id = available_templates[i % len(available_templates)]
                
                post = self.convert_testimonial(
                    testimonial=testimonial,
                    target_audience_problem=target_audience_problem,
                    platform=platform,
                    tone=tone,
                    template_id=template_id,
                    analyze_sentiment=True
                )
                post["variation_number"] = i + 1
                post["ab_test_variant"] = f"variant_{i + 1}"
                all_posts.append(post)
        
        return all_posts
    
    def enable_cache(self, cache_file: Optional[str] = None, max_size: int = 100):
        """Habilita el sistema de cache"""
        if ADVANCED_FEATURES_AVAILABLE:
            self.cache = SimpleCache(cache_file=cache_file, max_size=max_size)
            logger.info(f"Cache habilitado: {cache_file or 'en memoria'}")
        else:
            logger.warning("Cache no disponible - funcionalidades avanzadas no cargadas")
    
    def disable_cache(self):
        """Deshabilita el sistema de cache"""
        self.cache = None
        logger.info("Cache deshabilitado")
    
    def enable_tracking(self, tracking_file: Optional[str] = None):
        """Habilita el sistema de tracking post-publicación"""
        if POST_TRACKER_AVAILABLE:
            self.post_tracker = PostTracker(tracking_file=tracking_file)
            logger.info(f"Tracking habilitado: {tracking_file or 'default'}")
        else:
            logger.warning("PostTracker no disponible")
    
    def enable_version_control(self, storage_file: Optional[str] = None):
        """Habilita el sistema de versionado"""
        if VERSION_CONTROL_AVAILABLE:
            self.version_control = VersionControl(storage_file=storage_file)
            logger.info(f"Versionado habilitado: {storage_file or 'default'}")
        else:
            logger.warning("VersionControl no disponible")
    
    def generate_dashboard(
        self,
        post_data: Dict[str, Any],
        platform: str,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """
        Genera un dashboard HTML interactivo
        
        Args:
            post_data: Datos de la publicación
            platform: Plataforma objetivo
            output_file: Archivo de salida (opcional)
        
        Returns:
            Contenido HTML del dashboard o None si no está disponible
        """
        if self.dashboard_generator:
            return self.dashboard_generator.generate_dashboard(
                post_data=post_data,
                platform=platform,
                output_file=output_file
            )
        return None


def main():
    """Función principal para ejecución desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Convierte testimonios de clientes en publicaciones para redes sociales"
    )
    parser.add_argument(
        "testimonial",
        help="Texto del testimonio del cliente"
    )
    parser.add_argument(
        "target_audience",
        help="Problema o resultado que busca el público objetivo"
    )
    parser.add_argument(
        "--platform",
        choices=["general", "instagram", "facebook", "linkedin", "twitter", "tiktok"],
        default="general",
        help="Plataforma objetivo (default: general)"
    )
    parser.add_argument(
        "--tone",
        default="cálido y profesional",
        help="Tono deseado (default: cálido y profesional)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        help="Longitud máxima en caracteres"
    )
    parser.add_argument(
        "--no-hashtags",
        action="store_true",
        help="No incluir hashtags"
    )
    parser.add_argument(
        "--no-cta",
        action="store_true",
        help="No incluir llamada a la acción"
    )
    parser.add_argument(
        "--variations",
        type=int,
        metavar="N",
        help="Generar N variaciones de la publicación"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Formato de salida (default: text)"
    )
    parser.add_argument(
        "--api-key",
        help="API Key de OpenAI (o usar variable de entorno OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Archivo JSON con los parámetros (puede incluir testimonial, target_audience, platform, tone, etc.)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Modelo de OpenAI a usar (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Modo verbose con más información de debug"
    )
    parser.add_argument(
        "--analyze-sentiment",
        action="store_true",
        help="Analizar sentimiento y keywords del testimonio"
    )
    parser.add_argument(
        "--template",
        help="ID del template a usar (ver templates disponibles)"
    )
    parser.add_argument(
        "--enable-cache",
        action="store_true",
        help="Habilitar cache de resultados"
    )
    parser.add_argument(
        "--cache-file",
        help="Archivo para persistir el cache"
    )
    parser.add_argument(
        "--generate-formats",
        action="store_true",
        help="Generar múltiples formatos (carousel, stories, threads)"
    )
    parser.add_argument(
        "--ab-testing",
        action="store_true",
        help="Generar variaciones optimizadas para A/B testing"
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Listar templates disponibles y salir"
    )
    parser.add_argument(
        "--predict-engagement",
        action="store_true",
        help="Predecir engagement potencial de la publicación"
    )
    parser.add_argument(
        "--optimize-engagement",
        action="store_true",
        help="Optimizar contenido para máximo engagement"
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generar reporte completo de analytics"
    )
    parser.add_argument(
        "--report-format",
        choices=["json", "csv", "text", "all"],
        default="text",
        help="Formato del reporte (default: text)"
    )
    parser.add_argument(
        "--report-output",
        help="Archivo de salida para el reporte"
    )
    parser.add_argument(
        "--industry",
        default="testimonials",
        choices=["testimonials", "customer_success"],
        help="Industria para benchmarks (default: testimonials)"
    )
    parser.add_argument(
        "--generate-dashboard",
        action="store_true",
        help="Generar dashboard HTML interactivo"
    )
    parser.add_argument(
        "--dashboard-output",
        help="Archivo de salida para el dashboard HTML"
    )
    parser.add_argument(
        "--enable-tracking",
        action="store_true",
        help="Habilitar tracking post-publicación"
    )
    parser.add_argument(
        "--tracking-file",
        help="Archivo para guardar datos de tracking"
    )
    parser.add_argument(
        "--ml-training-data",
        help="Archivo con datos de entrenamiento para ML"
    )
    parser.add_argument(
        "--enable-ml",
        action="store_true",
        help="Habilitar mejoras ML en predicciones"
    )
    parser.add_argument(
        "--generate-calendar",
        action="store_true",
        help="Generar calendario de contenido optimizado"
    )
    parser.add_argument(
        "--calendar-type",
        choices=["weekly", "monthly"],
        default="weekly",
        help="Tipo de calendario a generar"
    )
    parser.add_argument(
        "--calendar-platforms",
        nargs="+",
        help="Plataformas para el calendario (default: todas)"
    )
    parser.add_argument(
        "--calendar-output",
        help="Archivo de salida para el calendario"
    )
    parser.add_argument(
        "--export-formats",
        nargs="+",
        choices=["json", "csv", "txt", "pdf", "excel", "pptx", "all"],
        help="Formatos de exportación adicionales"
    )
    parser.add_argument(
        "--export-all",
        action="store_true",
        help="Exportar a todos los formatos disponibles"
    )
    
    args = parser.parse_args()
    
    # Configurar logging según verbosidad
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Listar templates si se solicita
    if args.list_templates:
        if ADVANCED_FEATURES_AVAILABLE:
            converter = TestimonialToSocialPostConverter(openai_api_key=args.api_key)
            if converter.template_manager:
                templates = converter.template_manager.list_templates()
                print("\nTemplates disponibles:")
                print("=" * 60)
                for template in templates:
                    print(f"\nID: {template['id']}")
                    print(f"Nombre: {template.get('name', 'N/A')}")
                    if 'structure' in template:
                        print("Estructura:")
                        for step in template['structure']:
                            print(f"  - {step}")
                print("\n" + "=" * 60)
            else:
                print("TemplateManager no disponible")
        else:
            print("Funcionalidades avanzadas no disponibles")
        sys.exit(0)
    
    # Si se proporciona un archivo, leer los parámetros desde ahí
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Mapear nombres alternativos
            testimonial = (
                file_data.get("testimonial") or 
                file_data.get("testimonio") or 
                file_data.get("text") or
                args.testimonial
            )
            target_audience = (
                file_data.get("target_audience") or 
                file_data.get("target_audience_problem") or
                file_data.get("problema_resultado") or
                file_data.get("problema") or
                file_data.get("resultado") or
                args.target_audience
            )
            platform = file_data.get("platform") or file_data.get("plataforma") or args.platform
            tone = file_data.get("tone") or file_data.get("tono") or args.tone
            max_length = file_data.get("max_length") or args.max_length
            include_hashtags = file_data.get("include_hashtags", not args.no_hashtags)
            include_cta = file_data.get("include_call_to_action", not args.no_cta)
            model = file_data.get("model") or args.model
            
            # Actualizar args con valores del archivo
            args.testimonial = testimonial
            args.target_audience = target_audience
            args.platform = platform
            args.tone = tone
            args.max_length = max_length
            args.no_hashtags = not include_hashtags
            args.no_cta = not include_cta
            args.model = model
            
            logger.info(f"Parámetros cargados desde archivo: {args.file}")
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {args.file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            sys.exit(1)
    
    try:
        converter = TestimonialToSocialPostConverter(
            openai_api_key=args.api_key,
            model=args.model
        )
        
        # Habilitar cache si se solicita
        if args.enable_cache:
            converter.enable_cache(cache_file=args.cache_file)
        
        # Configurar generador de reportes si está disponible
        if ANALYTICS_REPORTER_AVAILABLE and converter.analytics_reporter:
            converter.analytics_reporter.industry = args.industry
        
        # Habilitar tracking si se solicita
        if args.enable_tracking:
            converter.enable_tracking(tracking_file=args.tracking_file)
        
        # Habilitar ML predictor si se solicita
        if args.enable_ml and ML_PREDICTOR_AVAILABLE:
            converter.ml_predictor = MLPredictor(training_data_file=args.ml_training_data)
            logger.info("Predictor ML habilitado")
        
        if args.variations:
            posts = converter.generate_multiple_variations(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platforms=[args.platform],
                count=args.variations,
                enable_ab_testing=args.ab_testing
            )
            
            # Comparar variaciones si hay múltiples
            if len(posts) > 1 and converter.variation_comparator:
                comparison = converter.variation_comparator.compare_variations(
                    posts,
                    platform=args.platform
                )
                
                if args.output == "json":
                    # Agregar comparación al output JSON
                    for post in posts:
                        if "variation_comparison" not in post:
                            post["variation_comparison"] = comparison
                else:
                    # Mostrar comparación en texto
                    print("\n" + "="*60)
                    print("COMPARACIÓN DE VARIACIONES")
                    print("="*60)
                    print(f"\nMejor variación: #{comparison['best_variation']['variation_number']}")
                    print(f"Score: {comparison['best_variation']['overall_score']}/100")
                    print(f"\n{comparison['summary']}")
                    print("\nRecomendaciones:")
                    for rec in comparison['recommendations'][:5]:
                        print(f"  • {rec}")
                    print("="*60 + "\n")
        else:
            post = converter.convert_testimonial(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platform=args.platform,
                tone=args.tone,
                max_length=args.max_length,
                include_hashtags=not args.no_hashtags,
                include_call_to_action=not args.no_cta,
                enable_cache=args.enable_cache,
                analyze_sentiment=args.analyze_sentiment,
                template_id=args.template,
                predict_engagement=args.predict_engagement,
                optimize_for_engagement=args.optimize_engagement
            )
            posts = [post]
            
            # Generar múltiples formatos si se solicita
            if args.generate_formats:
                formats = converter.generate_multiple_formats(
                    post["post_content"],
                    platform=args.platform
                )
                post["formats"] = formats
            
            # Generar reporte completo si se solicita
            if args.generate_report and converter.analytics_reporter:
                report = converter.analytics_reporter.generate_comprehensive_report(
                    post_data=post,
                    platform=args.platform,
                    include_benchmarks=True,
                    include_competitive=True
                )
                post["analytics_report"] = report
                
                # Exportar reporte según formato solicitado
                if args.report_output:
                    base_path = args.report_output
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_path = f"reports/testimonial_report_{timestamp}"
                
                if args.report_format in ["text", "all"]:
                    text_report = converter.analytics_reporter.generate_summary_text(report)
                    text_file = f"{base_path}.txt"
                    Path(text_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text_report)
                    print(f"\nReporte de texto guardado en: {text_file}")
                
                if args.report_format in ["json", "all"]:
                    json_file = f"{base_path}.json"
                    converter.analytics_reporter.export_report_json(report, json_file)
                    print(f"Reporte JSON guardado en: {json_file}")
                
                if args.report_format in ["csv", "all"]:
                    csv_file = f"{base_path}.csv"
                    converter.analytics_reporter.export_report_csv(report, csv_file)
                    print(f"Reporte CSV guardado en: {csv_file}")
            
            # Generar dashboard si se solicita
            if args.generate_dashboard and converter.dashboard_generator:
                if args.dashboard_output:
                    dashboard_file = args.dashboard_output
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dashboard_file = f"reports/dashboard_{timestamp}.html"
                
                converter.generate_dashboard(
                    post_data=post,
                    platform=args.platform,
                    output_file=dashboard_file
                )
                print(f"\nDashboard HTML generado en: {dashboard_file}")
                print("Abre el archivo en tu navegador para ver las visualizaciones interactivas.")
            
            # Generar calendario si se solicita
            if args.generate_calendar and converter.calendar_generator:
                platforms = args.calendar_platforms or ['linkedin', 'instagram', 'facebook', 'twitter']
                
                if args.calendar_type == "weekly":
                    calendar = converter.calendar_generator.generate_weekly_calendar(
                        platforms=platforms,
                        posts_per_platform=3
                    )
                else:
                    calendar = converter.calendar_generator.generate_monthly_calendar(
                        platforms=platforms,
                        posts_per_week=3
                    )
                
                if args.calendar_output:
                    calendar_file = args.calendar_output
                else:
                    calendar_type = args.calendar_type
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    calendar_file = f"calendars/calendar_{calendar_type}_{timestamp}.json"
                
                converter.calendar_generator.export_to_json(calendar, calendar_file)
                print(f"\n📅 Calendario {args.calendar_type} generado en: {calendar_file}")
                print(f"   Total de eventos: {calendar['summary']['total_events']}")
                print(f"   Por plataforma: {calendar['summary'].get('events_by_platform', {})}")
                
                # También exportar como iCal si es posible
                ical_file = calendar_file.replace('.json', '.ics')
                converter.calendar_generator.export_to_ical(calendar, ical_file)
                print(f"   Calendario iCal exportado en: {ical_file}")
            
            # Exportación avanzada si se solicita
            if (args.export_formats or args.export_all) and converter.export_manager:
                formats_to_export = args.export_formats if args.export_formats else []
                if args.export_all or "all" in formats_to_export:
                    formats_to_export = ['json', 'csv', 'txt', 'pdf', 'excel', 'pptx']
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"exports/testimonial_{timestamp}"
                
                exported_files = converter.export_manager.export_all_formats(
                    post_data=posts[0] if posts else {},
                    base_filename=base_filename,
                    formats=formats_to_export
                )
                
                print(f"\n📤 Archivos exportados:")
                for fmt, file_path in exported_files.items():
                    print(f"   {fmt.upper()}: {file_path}")
        
        if args.output == "json":
            print(json.dumps(posts if args.variations else posts[0], indent=2, ensure_ascii=False))
        else:
            for i, post in enumerate(posts, 1):
                if args.variations:
                    print(f"\n{'='*60}")
                    print(f"VARIACIÓN {i}")
                    print(f"{'='*60}\n")
                
                print("PUBLICACIÓN GENERADA:")
                print("-" * 60)
                print(post["full_post"])
                print("-" * 60)
                print(f"\nLongitud: {post['length']} caracteres")
                print(f"Longitud completa (con hashtags/CTA): {post.get('full_length', post['length'])} caracteres")
                print(f"Plataforma: {post['platform']}")
                print(f"Modelo usado: {post['metadata'].get('model_used', 'N/A')}")
                
                # Mostrar análisis de sentimiento si está disponible
                if "sentiment_analysis" in post:
                    sentiment = post["sentiment_analysis"]
                    print(f"\nAnálisis de Sentimiento:")
                    print(f"  Sentimiento: {sentiment['sentiment']}")
                    print(f"  Score: {sentiment['score']}")
                    print(f"  Confianza: {sentiment['confidence']}")
                    print(f"  Intensidad emocional: {sentiment['emotional_intensity']}")
                
                # Mostrar análisis de keywords si está disponible
                if "keyword_analysis" in post:
                    keywords = post["keyword_analysis"]
                    print(f"\nAnálisis de Keywords:")
                    print(f"  Keywords principales: {', '.join(keywords['main_keywords'][:5])}")
                    if keywords['topics']:
                        print(f"  Temas: {', '.join(keywords['topics'])}")
                    if keywords['metrics_mentioned']:
                        print(f"  Métricas: {', '.join(keywords['metrics_mentioned'][:3])}")
                
                if post["hashtags"]:
                    print(f"\nHashtags ({len(post['hashtags'])}): {', '.join(post['hashtags'])}")
                if post["call_to_action"]:
                    print(f"CTA: {post['call_to_action']}")
                
                # Mostrar predicción de engagement si está disponible
                if "engagement_prediction" in post:
                    pred = post["engagement_prediction"]
                    print(f"\nPredicción de Engagement:")
                    print(f"  Score predicho: {pred['predicted_score']}/100")
                    print(f"  Engagement rate estimado: {pred['predicted_engagement_rate']}%")
                    print(f"  Confianza: {pred['confidence']}")
                    print(f"  Horario óptimo: {pred.get('optimal_posting_time', 'N/A')}")
                    if pred.get('recommendations'):
                        print(f"  Recomendaciones:")
                        for rec in pred['recommendations'][:3]:
                            print(f"    - {rec}")
                
                # Mostrar optimizaciones si están disponibles
                if "engagement_optimization" in post:
                    opt = post["engagement_optimization"]
                    print(f"\nOptimizaciones Sugeridas:")
                    if opt.get('hashtag_suggestions'):
                        print(f"  Hashtags sugeridos: {', '.join(opt['hashtag_suggestions'][:5])}")
                    if opt.get('length_optimization'):
                        print(f"  Longitud: {opt['length_optimization']}")
                    if opt.get('engagement_boosters'):
                        print(f"  Boosters:")
                        for booster in opt['engagement_boosters'][:3]:
                            print(f"    - {booster}")
                
                # Mostrar formatos adicionales si están disponibles
                if "formats" in post:
                    formats = post["formats"]
                    print(f"\nFormatos Adicionales Generados:")
                    if "carousel_slides" in formats:
                        print(f"  Carousel slides: {len(formats['carousel_slides'])} slides")
                    if "story_text" in formats:
                        print(f"  Story text: {len(formats['story_text'])} caracteres")
                    if "thread_tweets" in formats:
                        print(f"  Thread tweets: {len(formats['thread_tweets'])} tweets")
                
                # Mostrar reporte de analytics si está disponible
                if "analytics_report" in post:
                    report = post["analytics_report"]
                    if "overall_score" in report:
                        score = report["overall_score"]
                        print(f"\n{'='*60}")
                        print(f"SCORE GENERAL: {score['score']}/{score['max_score']} ({score['percentage']}%) - {score['grade']}")
                        print(f"{'='*60}")
                    
                    if "benchmark_comparison" in report:
                        bench = report["benchmark_comparison"]
                        print(f"\nComparación con Benchmarks:")
                        print(f"  Percentil: {bench['percentile']}%")
                        print(f"  Nivel: {bench['performance_level'].upper()}")
                        print(f"  Potencial de mejora: +{bench['improvement_potential']}%")
                
                # Mostrar alertas si están disponibles
                if "alerts" in post and converter.alert_system:
                    print(converter.alert_system.format_alerts_for_display())
                
                # Mostrar mejoras ML si están disponibles
                if "ml_improvement" in post:
                    ml_imp = post["ml_improvement"]
                    print(f"\n🤖 Mejora ML:")
                    print(f"  Score mejorado: {post['engagement_prediction']['predicted_score']}/100")
                    print(f"  Mejora: +{ml_imp.get('improvement_amount', 0):.1f} puntos")
                    print(f"  Score base: {ml_imp.get('base_score', 0)}/100")
                
                # Mostrar ROI si está disponible
                if "roi_calculation" in post:
                    roi = post["roi_calculation"]
                    print(f"\n💰 Análisis de ROI:")
                    print(f"  Alcance estimado: {roi['estimated_reach']:,}")
                    print(f"  Engagement estimado: {roi['estimated_engagement']:,}")
                    print(f"  Conversiones estimadas: {roi['estimated_conversions']}")
                    print(f"  Ingresos estimados: ${roi['estimated_revenue']:.2f}")
                    print(f"  Costo por post: ${roi['cost_per_post']:.2f}")
                    print(f"  ROI: {roi['roi_percentage']:.1f}% (x{roi['roi_multiplier']:.2f})")
                    print(f"  Período de recuperación: {roi['payback_period_days']:.1f} días")
                
                print()
    
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
