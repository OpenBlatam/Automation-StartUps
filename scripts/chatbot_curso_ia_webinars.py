#!/usr/bin/env python3
"""
Chatbot para Curso de IA y Webinars
Proporciona respuestas automáticas sobre el curso de IA y los webinars disponibles.
Escala consultas complejas a agentes humanos cuando es necesario.

🎯 Uso:
    python3 chatbot_curso_ia_webinars.py
    
    O desde código:
    from chatbot_curso_ia_webinars import CursoIAWebinarChatbot
    chatbot = CursoIAWebinarChatbot()
    response = chatbot.process_message("¿Cuánto cuesta el curso?")

✨ Funcionalidades:
- Logging estructurado
- Persistencia de conversaciones
- Métricas y estadísticas
- Manejo avanzado de errores
- Contexto de historial de conversación
- Validación mejorada de entrada
- Cache de respuestas
- Exportación de métricas
- Análisis de sentimiento
- Búsqueda mejorada de FAQs
- Rate limiting
- Sistema de feedback
- Análisis de tendencias
- Health checks
"""

import re
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import traceback
from functools import lru_cache
import hashlib

# Importar utilidades compartidas
try:
    from chatbot_utils import (
        export_metrics_to_json, export_metrics_to_csv,
        analyze_sentiment_basic, extract_keywords,
        calculate_text_similarity, format_response_time,
        generate_conversation_summary, create_metrics_dashboard_data
    )
    from chatbot_advanced_features import (
        RateLimiter, RateLimitConfig, FeedbackSystem, FeedbackType,
        TrendAnalyzer, AISuggestions, create_health_check
    )
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    # Si no están disponibles, definir funciones básicas
    def export_metrics_to_json(metrics, output_file="chatbot_metrics.json"):
        with open(output_file, 'w') as f:
            json.dump({"exported_at": datetime.now().isoformat(), "metrics": metrics}, f, indent=2)
        return output_file
    
    def export_metrics_to_csv(metrics, output_file="chatbot_metrics.csv"):
        return output_file
    
    def analyze_sentiment_basic(message):
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    
    def extract_keywords(text, min_length=3, max_keywords=10):
        return []
    
    def calculate_text_similarity(text1, text2):
        return 0.0
    
    def format_response_time(seconds):
        return f"{seconds:.3f}s"
    
    def generate_conversation_summary(conversation_history):
        return {"total_messages": len(conversation_history)}
    
    def create_metrics_dashboard_data(metrics):
        return metrics


class IntentType(Enum):
    """Tipos de intenciones detectadas"""
    INFO_CURSO = "info_curso"
    PRECIO_CURSO = "precio_curso"
    CONTENIDO_CURSO = "contenido_curso"
    INSCRIPCION = "inscripcion"
    WEBINAR_INFO = "webinar_info"
    WEBINAR_PROXIMOS = "webinar_proximos"
    WEBINAR_INSCRIPCION = "webinar_inscripcion"
    REQUISITOS = "requisitos"
    CERTIFICACION = "certificacion"
    HORARIOS = "horarios"
    PLATAFORMA = "plataforma"
    SOPORTE = "soporte"
    OTRO = "otro"


@dataclass
class ChatbotResponse:
    """Respuesta del chatbot"""
    message: str
    confidence: float
    intent: str
    requires_escalation: bool
    escalation_reason: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    faq_matched: Optional[str] = None
    processing_time: Optional[float] = None


@dataclass
class ChatbotMetrics:
    """Métricas del chatbot"""
    total_messages: int = 0
    total_escalations: int = 0
    intent_counts: Dict[str, int] = None
    average_confidence: float = 0.0
    average_processing_time: float = 0.0
    faq_matches: int = 0
    
    def __post_init__(self):
        if self.intent_counts is None:
            self.intent_counts = defaultdict(int)


class CursoIAWebinarChatbot:
    """
    Chatbot especializado en responder preguntas sobre el Curso de IA y Webinars.
    """
    
    def __init__(self, enable_logging: bool = True, persist_conversations: bool = True, 
                 conversation_dir: str = "chatbot_conversations", enable_rate_limiting: bool = True,
                 enable_feedback: bool = True):
        """
        Inicializa el chatbot con base de conocimiento.
        
        Args:
            enable_logging: Habilita logging estructurado
            persist_conversations: Guarda conversaciones en archivos JSON
            conversation_dir: Directorio para guardar conversaciones
            enable_rate_limiting: Habilita rate limiting
            enable_feedback: Habilita sistema de feedback
        """
        self.faqs = self._load_faqs()
        self.webinars = self._load_webinars()
        self.escalation_keywords = [
            "complejo", "problema", "error", "no funciona", "no entiendo",
            "ayuda urgente", "emergencia", "reembolso", "cancelar", "queja"
        ]
        self.metrics = ChatbotMetrics()
        self.enable_logging = enable_logging
        self.persist_conversations = persist_conversations
        self.conversation_dir = Path(conversation_dir)
        
        # Cache de respuestas frecuentes
        self.response_cache = {}
        self.cache_enabled = True
        self.cache_max_size = 100
        
        # Rate limiting
        if ADVANCED_FEATURES_AVAILABLE and enable_rate_limiting:
            self.rate_limiter = RateLimiter(RateLimitConfig(max_requests=60, time_window=60))
            self.enable_rate_limiting = True
        else:
            self.rate_limiter = None
            self.enable_rate_limiting = False
        
        # Sistema de feedback
        if ADVANCED_FEATURES_AVAILABLE and enable_feedback:
            self.feedback_system = FeedbackSystem("chatbot_feedback.json")
            self.trend_analyzer = TrendAnalyzer(str(self.conversation_dir))
            self.ai_suggestions = AISuggestions(self.feedback_system, self.trend_analyzer)
            self.enable_feedback = True
        else:
            self.feedback_system = None
            self.trend_analyzer = None
            self.ai_suggestions = None
            self.enable_feedback = False
        
        # Configurar logging
        if enable_logging:
            self._setup_logging()
        
        # Crear directorio de conversaciones si no existe
        if persist_conversations:
            self.conversation_dir.mkdir(exist_ok=True)
        
        if enable_logging:
            self.logger.info("Chatbot inicializado correctamente")
        
    def _load_faqs(self) -> List[Dict]:
        """Carga las preguntas frecuentes sobre el curso"""
        return [
            {
                "id": "faq_001",
                "category": "informacion_general",
                "question": "¿Qué es el curso de IA?",
                "answer": "Nuestro curso de Inteligencia Artificial es un programa completo diseñado para enseñarte los fundamentos y aplicaciones prácticas de la IA. Incluye módulos sobre machine learning, deep learning, procesamiento de lenguaje natural, visión por computadora y aplicaciones empresariales. El curso está diseñado tanto para principiantes como para profesionales que buscan actualizar sus conocimientos.",
                "keywords": ["curso", "ia", "inteligencia artificial", "qué es", "información"]
            },
            {
                "id": "faq_002",
                "category": "precio",
                "question": "¿Cuánto cuesta el curso?",
                "answer": "El curso de IA tiene diferentes modalidades de pago:\n• Plan Mensual: $99 USD/mes\n• Plan Trimestral: $249 USD (ahorro de $48)\n• Plan Anual: $899 USD (ahorro de $289)\n\nTambién ofrecemos descuentos para estudiantes (20% de descuento) y grupos empresariales (descuentos personalizados). Todos los planes incluyen acceso completo al contenido, certificado al finalizar y soporte durante 6 meses.",
                "keywords": ["precio", "costo", "cuánto", "tarifa", "pago", "plan"]
            },
            {
                "id": "faq_003",
                "category": "contenido",
                "question": "¿Qué contenido incluye el curso?",
                "answer": "El curso incluye:\n\n📚 Módulos principales:\n• Fundamentos de IA y Machine Learning\n• Deep Learning y Redes Neuronales\n• Procesamiento de Lenguaje Natural (NLP)\n• Visión por Computadora\n• Aplicaciones Empresariales de IA\n• Ética en IA\n\n🎯 Recursos adicionales:\n• Más de 50 horas de video\n• Proyectos prácticos con código\n• Casos de estudio reales\n• Acceso a comunidad exclusiva\n• Material descargable\n• Certificado de finalización",
                "keywords": ["contenido", "módulos", "temas", "qué incluye", "material"]
            },
            {
                "id": "faq_004",
                "category": "inscripcion",
                "question": "¿Cómo me inscribo al curso?",
                "answer": "Para inscribirte al curso, puedes:\n\n1. Visitar nuestra página web: www.ejemplo.com/curso-ia\n2. Seleccionar el plan que mejor se adapte a ti\n3. Completar el formulario de inscripción\n4. Realizar el pago de forma segura\n\nUna vez completado, recibirás un email con tus credenciales de acceso en menos de 24 horas. Si necesitas ayuda con el proceso, puedes contactarnos en inscripciones@ejemplo.com",
                "keywords": ["inscripción", "inscribir", "registro", "cómo", "proceso"]
            },
            {
                "id": "faq_005",
                "category": "requisitos",
                "question": "¿Qué requisitos necesito para tomar el curso?",
                "answer": "Los requisitos son:\n\n📋 Conocimientos previos:\n• Conocimientos básicos de programación (Python recomendado)\n• Comprensión básica de matemáticas (álgebra, estadística)\n• No se requiere experiencia previa en IA\n\n💻 Requisitos técnicos:\n• Computadora con conexión a internet estable\n• Navegador web actualizado (Chrome, Firefox, Safari)\n• 4GB de RAM mínimo (8GB recomendado)\n• Espacio en disco: 5GB para proyectos\n\nEl curso está diseñado para ser accesible, comenzando desde lo básico.",
                "keywords": ["requisitos", "necesito", "requiere", "conocimientos", "técnico"]
            },
            {
                "id": "faq_006",
                "category": "certificacion",
                "question": "¿Recibo un certificado al finalizar?",
                "answer": "Sí, al completar todos los módulos y proyectos del curso recibirás un certificado digital verificable. El certificado:\n\n✅ Es reconocido internacionalmente\n✅ Incluye tu nombre y fecha de finalización\n✅ Puede ser compartido en LinkedIn\n✅ Tiene un código de verificación único\n✅ Es descargable en formato PDF\n\nPara obtener el certificado, debes completar al menos el 80% del contenido y aprobar los proyectos prácticos con una calificación mínima de 70%.",
                "keywords": ["certificado", "certificación", "diploma", "reconocimiento"]
            },
            {
                "id": "faq_007",
                "category": "webinar",
                "question": "¿Qué son los webinars?",
                "answer": "Nuestros webinars son sesiones en vivo donde expertos en IA comparten conocimientos actualizados, tendencias del mercado y casos prácticos. Los webinars son:\n\n🎥 Sesiones en vivo de 60-90 minutos\n📅 Programados regularmente (2-3 veces al mes)\n💡 Temas variados y actualizados\n🎯 Incluyen Q&A con los expertos\n📹 Grabaciones disponibles para inscritos\n\nLos webinars son gratuitos para estudiantes del curso y están disponibles con descuento para el público general.",
                "keywords": ["webinar", "webinars", "sesiones", "en vivo", "qué son"]
            },
            {
                "id": "faq_008",
                "category": "webinar",
                "question": "¿Cuándo son los próximos webinars?",
                "answer": "Nuestros próximos webinars programados son:\n\n📅 Próximos eventos:\n• 'IA Generativa en 2024' - 15 de marzo, 19:00 GMT\n• 'Machine Learning para Marketing' - 22 de marzo, 19:00 GMT\n• 'ChatGPT y Automatización Empresarial' - 5 de abril, 19:00 GMT\n\nPuedes ver el calendario completo y registrarte en: www.ejemplo.com/webinars\n\nRecibirás recordatorios por email 24 horas antes de cada evento.",
                "keywords": ["próximos", "cuándo", "fecha", "calendario", "eventos"]
            },
            {
                "id": "faq_009",
                "category": "webinar",
                "question": "¿Cómo me inscribo a un webinar?",
                "answer": "Para inscribirte a un webinar:\n\n1. Visita nuestra página de webinars: www.ejemplo.com/webinars\n2. Selecciona el webinar que te interese\n3. Haz clic en 'Registrarse' (es gratuito para estudiantes del curso)\n4. Completa el formulario con tu email\n5. Recibirás un email de confirmación con el link de acceso\n\nLos estudiantes del curso tienen acceso automático a todos los webinars. Si eres estudiante, solo necesitas iniciar sesión en la plataforma.",
                "keywords": ["inscribir", "registrar", "webinar", "cómo", "acceso"]
            },
            {
                "id": "faq_010",
                "category": "plataforma",
                "question": "¿Cómo accedo a la plataforma del curso?",
                "answer": "Para acceder a la plataforma:\n\n1. Visita: www.ejemplo.com/login\n2. Ingresa con el email que usaste para inscribirte\n3. Usa la contraseña que recibiste por email\n\nSi olvidaste tu contraseña, puedes restablecerla desde la página de login. Si tienes problemas de acceso, contacta a soporte@ejemplo.com y te ayudaremos en menos de 24 horas.",
                "keywords": ["acceso", "plataforma", "login", "iniciar sesión", "contraseña"]
            },
            {
                "id": "faq_011",
                "category": "horarios",
                "question": "¿El curso tiene horarios fijos?",
                "answer": "No, el curso es completamente asíncrono y flexible:\n\n⏰ Puedes estudiar a tu ritmo\n📅 Sin horarios fijos ni clases obligatorias\n🌍 Acceso 24/7 desde cualquier lugar\n⏸️ Pausa y reanuda cuando quieras\n\nSin embargo, ofrecemos sesiones opcionales en vivo cada semana para resolver dudas y networking. Estas sesiones son grabadas y están disponibles después.",
                "keywords": ["horarios", "horario", "cuándo", "flexible", "asíncrono"]
            },
            {
                "id": "faq_012",
                "category": "soporte",
                "question": "¿Qué tipo de soporte ofrecen?",
                "answer": "Ofrecemos múltiples canales de soporte:\n\n💬 Chat en vivo (Lun-Vie, 9:00-18:00 GMT)\n📧 Email: soporte@ejemplo.com (respuesta en 24h)\n📚 Base de conocimiento con guías\n🎥 Videos tutoriales\n👥 Comunidad de estudiantes en Discord\n🎓 Sesiones de Q&A semanales\n\nPara temas técnicos complejos o consultas personalizadas, puedes solicitar una sesión 1-on-1 con un instructor (disponible en planes premium).",
                "keywords": ["soporte", "ayuda", "contacto", "asistencia", "problema"]
            }
        ]
    
    def _setup_logging(self):
        """Configura logging estructurado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chatbot_curso_ia.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CursoIAWebinarChatbot')
    
    def _save_conversation(self, conversation_id: str, messages: List[Dict]):
        """Guarda una conversación en un archivo JSON"""
        if not self.persist_conversations:
            return
        
        try:
            conversation_file = self.conversation_dir / f"{conversation_id}.json"
            conversation_data = {
                "conversation_id": conversation_id,
                "created_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "messages": messages
            }
            
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Conversación guardada: {conversation_id}")
        except Exception as e:
            self.logger.error(f"Error guardando conversación: {e}")
    
    def get_metrics(self) -> Dict:
        """Retorna métricas del chatbot"""
        return {
            "total_messages": self.metrics.total_messages,
            "total_escalations": self.metrics.total_escalations,
            "escalation_rate": (
                self.metrics.total_escalations / self.metrics.total_messages 
                if self.metrics.total_messages > 0 else 0
            ),
            "intent_distribution": dict(self.metrics.intent_counts),
            "average_confidence": self.metrics.average_confidence,
            "average_processing_time": self.metrics.average_processing_time,
            "faq_match_rate": (
                self.metrics.faq_matches / self.metrics.total_messages 
                if self.metrics.total_messages > 0 else 0
            )
        }
    
    def reset_metrics(self):
        """Reinicia las métricas"""
        self.metrics = ChatbotMetrics()
        if self.enable_logging:
            self.logger.info("Métricas reiniciadas")
    
    def export_metrics(self, format: str = "json", output_file: Optional[str] = None) -> str:
        """
        Exporta métricas a archivo.
        
        Args:
            format: Formato de exportación ('json' o 'csv')
            output_file: Nombre del archivo (opcional)
        
        Returns:
            Ruta del archivo generado
        """
        metrics = self.get_metrics()
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if format == "json":
                output_file = f"chatbot_curso_ia_metrics_{timestamp}.json"
            else:
                output_file = f"chatbot_curso_ia_metrics_{timestamp}.csv"
        
        if format == "json":
            return export_metrics_to_json(metrics, output_file)
        else:
            return export_metrics_to_csv(metrics, output_file)
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict]:
        """
        Obtiene un resumen de una conversación guardada.
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            Dict con resumen o None si no existe
        """
        if not self.persist_conversations:
            return None
        
        conversation_file = self.conversation_dir / f"{conversation_id}.json"
        
        if not conversation_file.exists():
            return None
        
        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return generate_conversation_summary(data.get('messages', []))
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error leyendo conversación: {e}")
            return None
    
    def _get_cache_key(self, message: str) -> str:
        """Genera una clave de cache para un mensaje"""
        # Normalizar mensaje
        normalized = re.sub(r'\s+', ' ', message.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_cached_response(self, message: str) -> Optional[ChatbotResponse]:
        """Obtiene respuesta del cache si existe"""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(message)
        return self.response_cache.get(cache_key)
    
    def _cache_response(self, message: str, response: ChatbotResponse):
        """Guarda respuesta en cache"""
        if not self.cache_enabled:
            return
        
        # Limitar tamaño del cache
        if len(self.response_cache) >= self.cache_max_size:
            # Eliminar el más antiguo (FIFO simple)
            first_key = next(iter(self.response_cache))
            del self.response_cache[first_key]
        
        cache_key = self._get_cache_key(message)
        self.response_cache[cache_key] = response
    
    def _load_webinars(self) -> List[Dict]:
        """Carga información de webinars programados"""
        return [
            {
                "id": "web_001",
                "title": "IA Generativa en 2024: Tendencias y Aplicaciones",
                "date": "2024-03-15",
                "time": "19:00 GMT",
                "duration": "90 minutos",
                "speaker": "Dr. María González",
                "topics": ["GPT-4", "DALL-E", "Aplicaciones empresariales", "Ética"],
                "price": "Gratis para estudiantes / $29 público general"
            },
            {
                "id": "web_002",
                "title": "Machine Learning para Marketing Digital",
                "date": "2024-03-22",
                "time": "19:00 GMT",
                "duration": "75 minutos",
                "speaker": "Ing. Carlos Martínez",
                "topics": ["Segmentación", "Predicción de conversión", "Personalización", "ROI"],
                "price": "Gratis para estudiantes / $29 público general"
            },
            {
                "id": "web_003",
                "title": "ChatGPT y Automatización Empresarial",
                "date": "2024-04-05",
                "time": "19:00 GMT",
                "duration": "60 minutos",
                "speaker": "Dra. Ana Rodríguez",
                "topics": ["Automatización", "Integraciones", "Casos de uso", "Mejores prácticas"],
                "price": "Gratis para estudiantes / $29 público general"
            }
        ]
    
    def detect_intent(self, message: str, conversation_history: Optional[List[Dict]] = None) -> IntentType:
        """
        Detecta la intención del mensaje del usuario.
        Usa el historial de conversación para mejorar la detección.
        """
        message_lower = message.lower()
        
        # Si hay historial, considerar el contexto
        context = ""
        if conversation_history:
            # Tomar los últimos 3 mensajes del usuario para contexto
            user_messages = [
                msg.get('content', '') for msg in conversation_history[-6:] 
                if msg.get('role') == 'user'
            ]
            context = " ".join(user_messages).lower()
        
        combined_text = f"{context} {message_lower}"
        
        # Patrones de intención
        patterns = {
            IntentType.INFO_CURSO: [
                r"qué es.*curso", r"información.*curso", r"curso.*ia", r"sobre.*curso"
            ],
            IntentType.PRECIO_CURSO: [
                r"precio", r"costo", r"cuánto.*cuesta", r"tarifa", r"pago", r"plan"
            ],
            IntentType.CONTENIDO_CURSO: [
                r"contenido", r"módulos", r"temas", r"qué incluye", r"material"
            ],
            IntentType.INSCRIPCION: [
                r"inscribir", r"inscripción", r"registrar", r"cómo.*inscribir", r"matricular"
            ],
            IntentType.WEBINAR_INFO: [
                r"qué.*webinar", r"webinar.*es", r"información.*webinar"
            ],
            IntentType.WEBINAR_PROXIMOS: [
                r"próximos.*webinar", r"cuándo.*webinar", r"fecha.*webinar", r"calendario"
            ],
            IntentType.WEBINAR_INSCRIPCION: [
                r"inscribir.*webinar", r"registrar.*webinar", r"acceso.*webinar"
            ],
            IntentType.REQUISITOS: [
                r"requisitos", r"necesito", r"requiere", r"conocimientos.*previos"
            ],
            IntentType.CERTIFICACION: [
                r"certificado", r"certificación", r"diploma", r"reconocimiento"
            ],
            IntentType.HORARIOS: [
                r"horario", r"cuándo.*clase", r"fecha.*clase", r"flexible"
            ],
            IntentType.PLATAFORMA: [
                r"acceso", r"plataforma", r"login", r"iniciar.*sesión", r"contraseña"
            ],
            IntentType.SOPORTE: [
                r"soporte", r"ayuda", r"contacto", r"problema", r"error"
            ]
        }
        
        # Buscar coincidencias (priorizar mensaje actual, luego contexto)
        intent_scores = defaultdict(float)
        
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                # Coincidencias en mensaje actual tienen mayor peso
                if re.search(pattern, message_lower):
                    intent_scores[intent] += 2.0
                # Coincidencias en contexto tienen menor peso
                elif context and re.search(pattern, context):
                    intent_scores[intent] += 0.5
        
        # Retornar el intent con mayor score
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return IntentType.OTRO
    
    def search_faq(self, message: str) -> Optional[Dict]:
        """Busca la FAQ más relevante para el mensaje usando similitud mejorada"""
        message_lower = message.lower()
        message_words = set(re.findall(r'\b\w+\b', message_lower))
        
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            score = 0
            faq_text = f"{faq['question']} {faq['answer']}".lower()
            faq_keywords = [kw.lower() for kw in faq.get('keywords', [])]
            
            # Puntuar por palabras clave (mayor peso)
            for keyword in faq_keywords:
                if keyword in message_lower:
                    score += 2
            
            # Puntuar por palabras comunes
            faq_words = set(re.findall(r'\b\w+\b', faq_text))
            common_words = message_words.intersection(faq_words)
            score += len(common_words) * 0.5
            
            # Puntuar por coincidencia exacta de pregunta (muy alto)
            if faq['question'].lower() in message_lower:
                score += 5
            
            # Usar similitud de texto como factor adicional
            similarity = calculate_text_similarity(message_lower, faq_text)
            score += similarity * 3
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        # Solo retornar si el score es suficientemente alto
        if best_score >= 2:
            return best_match
        
        return None
    
    def check_escalation_needed(self, message: str, intent: IntentType) -> Tuple[bool, Optional[str]]:
        """Verifica si la consulta necesita escalación a un agente humano"""
        message_lower = message.lower()
        
        # Palabras clave que requieren escalación
        escalation_patterns = [
            r"reembolso", r"devolución", r"cancelar", r"cancelación",
            r"queja", r"reclamo", r"problema.*pago", r"error.*pago",
            r"no.*funciona", r"no.*puedo", r"no.*entra", r"acceso.*denegado",
            r"urgente", r"emergencia", r"inmediato"
        ]
        
        for pattern in escalation_patterns:
            if re.search(pattern, message_lower):
                return True, "Consulta requiere atención personalizada de un agente"
        
        # Si el intent es OTRO y no hay FAQ relevante, escalar
        if intent == IntentType.OTRO:
            return True, "Consulta no identificada, requiere revisión humana"
        
        # Feedback negativo
        negative_patterns = [
            r"no.*ayuda", r"no.*sirve", r"no.*entiendo", r"confuso", r"complejo"
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, message_lower):
                return True, "Usuario indica dificultad, mejor atención personalizada"
        
        return False, None
    
    def generate_response(self, message: str, conversation_history: Optional[List[Dict]] = None) -> ChatbotResponse:
        """
        Genera una respuesta para el mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            conversation_history: Historial de conversación para contexto
        
        Returns:
            ChatbotResponse con la respuesta generada
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not message or not message.strip():
                raise ValueError("El mensaje no puede estar vacío")
            
            if len(message) > 2000:
                raise ValueError("El mensaje es demasiado largo (máximo 2000 caracteres)")
            
            # Verificar cache primero
            cached_response = self._get_cached_response(message)
            if cached_response:
                processing_time = (datetime.now() - start_time).total_seconds()
                # Actualizar tiempo de procesamiento (será muy bajo por cache)
                cached_response.processing_time = processing_time
                if self.enable_logging:
                    self.logger.debug(f"Respuesta obtenida del cache")
                return cached_response
            
            # Detectar intención (con contexto)
            intent = self.detect_intent(message, conversation_history)
            
            # Buscar FAQ relevante
            faq_match = self.search_faq(message)
            
            # Verificar si necesita escalación
            needs_escalation, escalation_reason = self.check_escalation_needed(message, intent)
            
            # Análisis de sentimiento (opcional, para logging)
            sentiment = analyze_sentiment_basic(message)
            if self.enable_logging and sentiment['negative'] > 0.3:
                self.logger.warning(f"Sentimiento negativo detectado: {sentiment}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if needs_escalation:
                self.metrics.total_escalations += 1
                self.logger.info(f"Escalación requerida: {escalation_reason}")
                
                return ChatbotResponse(
                    message=(
                        "Entiendo tu consulta. Para brindarte la mejor asistencia y resolver tu "
                        "situación de manera personalizada, voy a conectarte con uno de nuestros "
                        "agentes especializados. Un miembro de nuestro equipo se pondrá en contacto "
                        "contigo en breve.\n\n"
                        "Mientras tanto, puedes contactarnos directamente en:\n"
                        "📧 Email: soporte@ejemplo.com\n"
                        "💬 Chat en vivo: disponible en nuestra página web\n"
                        "📞 Teléfono: +1 (555) 123-4567 (Lun-Vie, 9:00-18:00 GMT)"
                    ),
                    confidence=0.9,
                    intent=intent.value,
                    requires_escalation=True,
                    escalation_reason=escalation_reason,
                    suggested_actions=[
                        "Contactar por email",
                        "Ver base de conocimiento",
                        "Programar llamada"
                    ],
                    processing_time=processing_time
                )
        
            # Si hay FAQ relevante, usarla
            if faq_match:
                self.metrics.faq_matches += 1
                # Agregar información adicional según el intent
                response_message = faq_match['answer']
                
                # Agregar información de webinars si es relevante
                if intent in [IntentType.WEBINAR_PROXIMOS, IntentType.WEBINAR_INFO]:
                    webinars_info = "\n\n📅 Próximos webinars:\n"
                    for webinar in self.webinars[:3]:
                        webinars_info += (
                            f"• {webinar['title']}\n"
                            f"  📅 {webinar['date']} a las {webinar['time']}\n"
                            f"  👤 {webinar['speaker']}\n"
                            f"  💰 {webinar['price']}\n\n"
                        )
                    response_message += webinars_info
                
                response = ChatbotResponse(
                    message=response_message,
                    confidence=0.85,
                    intent=intent.value,
                    requires_escalation=False,
                    suggested_actions=[
                        "¿Te ayudó esta respuesta?",
                        "¿Tienes otra pregunta?",
                        "Contactar con agente humano"
                    ],
                    faq_matched=faq_match.get('id'),
                    processing_time=processing_time
                )
                
                # Guardar en cache
                self._cache_response(message, response)
                return response
            
            # Respuesta genérica si no hay FAQ pero no requiere escalación
            response = ChatbotResponse(
                message=(
                    "Gracias por tu consulta. Aunque no tengo información específica sobre ese tema "
                    "en este momento, puedo ayudarte con:\n\n"
                    "• Información sobre el curso de IA\n"
                    "• Detalles sobre nuestros webinars\n"
                    "• Proceso de inscripción\n"
                    "• Precios y planes\n"
                    "• Requisitos y certificación\n\n"
                    "Si tu consulta es más específica o compleja, puedo conectarte con un agente "
                    "humano que podrá ayudarte mejor. ¿Te gustaría que te conecte con nuestro equipo?"
                ),
                confidence=0.5,
                intent=intent.value,
                requires_escalation=False,
                suggested_actions=[
                    "Ver información del curso",
                    "Ver próximos webinars",
                    "Contactar con agente humano"
                ],
                processing_time=processing_time
            )
            
            # No cachear respuestas genéricas de baja confianza
            if response.confidence >= 0.6:
                self._cache_response(message, response)
            
            return response
        
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error procesando mensaje: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return ChatbotResponse(
                message=(
                    "Lo siento, ocurrió un error al procesar tu mensaje. "
                    "Por favor, intenta reformular tu pregunta o contacta directamente "
                    "con nuestro equipo de soporte en soporte@ejemplo.com"
                ),
                confidence=0.0,
                intent="error",
                requires_escalation=True,
                escalation_reason=error_msg,
                processing_time=processing_time
            )
    
    def process_message(self, user_message: str, conversation_history: Optional[List[Dict]] = None,
                       conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> Dict:
        """
        Procesa un mensaje del usuario y retorna la respuesta del chatbot.
        
        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de conversación (opcional)
            conversation_id: ID único de la conversación (opcional)
            user_id: ID del usuario para rate limiting (opcional)
        
        Returns:
            Dict con la respuesta del chatbot
        """
        # Generar ID de conversación si no existe
        if not conversation_id:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_message) % 10000}"
        
        # Rate limiting
        if self.enable_rate_limiting and self.rate_limiter:
            user_id = user_id or "default"
            allowed, reason = self.rate_limiter.is_allowed(user_id)
            if not allowed:
                return {
                    "error": reason,
                    "conversation_id": conversation_id,
                    "rate_limited": True
                }
        
        # Validación básica
        if not user_message or not user_message.strip():
            return {
                "error": "El mensaje no puede estar vacío",
                "conversation_id": conversation_id
            }
        
        # Procesar mensaje
        response = self.generate_response(user_message, conversation_history)
        
        # Actualizar métricas
        self.metrics.total_messages += 1
        self.metrics.intent_counts[response.intent] += 1
        
        # Actualizar promedio de confianza
        total_conf = self.metrics.average_confidence * (self.metrics.total_messages - 1)
        self.metrics.average_confidence = (total_conf + response.confidence) / self.metrics.total_messages
        
        # Actualizar promedio de tiempo de procesamiento
        if response.processing_time:
            total_time = self.metrics.average_processing_time * (self.metrics.total_messages - 1)
            self.metrics.average_processing_time = (total_time + response.processing_time) / self.metrics.total_messages
        
        # Logging
        if self.enable_logging:
            self.logger.info(
                f"Mensaje procesado - Intent: {response.intent}, "
                f"Confidence: {response.confidence:.2f}, "
                f"Escalation: {response.requires_escalation}"
            )
        
        # Preparar respuesta
        result = {
            "response": response.message,
            "confidence": response.confidence,
            "intent": response.intent,
            "requires_escalation": response.requires_escalation,
            "escalation_reason": response.escalation_reason,
            "suggested_actions": response.suggested_actions,
            "faq_matched": response.faq_matched,
            "processing_time": response.processing_time,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        }
        
        # Guardar conversación si está habilitado
        if self.persist_conversations and conversation_history is not None:
            updated_history = conversation_history + [
                {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
                {
                    "role": "assistant", 
                    "content": response.message, 
                    "timestamp": datetime.now().isoformat(),
                    "intent": response.intent,
                    "confidence": response.confidence,
                    "requires_escalation": response.requires_escalation
                }
            ]
            self._save_conversation(conversation_id, updated_history)
        
        return result
    
    def add_feedback(self, conversation_id: str, message_id: str, feedback_type: str, 
                    comment: Optional[str] = None, user_id: Optional[str] = None) -> bool:
        """
        Agrega feedback sobre una respuesta.
        
        Args:
            conversation_id: ID de la conversación
            message_id: ID del mensaje
            feedback_type: Tipo de feedback ('positive', 'negative', 'helpful', 'not_helpful')
            comment: Comentario opcional
            user_id: ID del usuario
        
        Returns:
            True si se agregó exitosamente
        """
        if not self.enable_feedback or not self.feedback_system:
            return False
        
        try:
            feedback_entry = FeedbackEntry(
                conversation_id=conversation_id,
                message_id=message_id,
                feedback_type=FeedbackType(feedback_type),
                comment=comment,
                user_id=user_id
            )
            self.feedback_system.add_feedback(feedback_entry)
            return True
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error agregando feedback: {e}")
            return False
    
    def get_feedback_stats(self) -> Optional[Dict]:
        """Obtiene estadísticas de feedback"""
        if not self.enable_feedback or not self.feedback_system:
            return None
        return self.feedback_system.get_feedback_stats()
    
    def get_trends(self, days: int = 7) -> Dict:
        """Obtiene análisis de tendencias"""
        if not self.enable_feedback or not self.trend_analyzer:
            return {"error": "Sistema de tendencias no disponible"}
        
        return {
            "intent_trends": self.trend_analyzer.analyze_intent_trends(days),
            "escalation_trends": self.trend_analyzer.analyze_escalation_trends(days),
            "peak_hours": self.trend_analyzer.get_peak_hours(days)
        }
    
    def get_ai_suggestions(self) -> List[Dict]:
        """Obtiene sugerencias de IA para mejorar el chatbot"""
        if not self.enable_feedback or not self.ai_suggestions:
            return []
        return self.ai_suggestions.generate_suggestions()
    
    def health_check(self) -> Dict:
        """Realiza un health check del chatbot"""
        if ADVANCED_FEATURES_AVAILABLE:
            return create_health_check(self)
        else:
            # Health check básico
            metrics = self.get_metrics()
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "issues": [],
                "cache_size": len(self.response_cache),
                "total_faqs": len(self.faqs)
            }


def main():
    """Función principal para pruebas interactivas"""
    chatbot = CursoIAWebinarChatbot(enable_logging=True, persist_conversations=True)
    
    print("=" * 60)
    print("🤖 Chatbot - Curso de IA y Webinars")
    print("=" * 60)
    print("\n¡Hola! Soy tu asistente virtual. Puedo ayudarte con:")
    print("• Información sobre el curso de IA")
    print("• Próximos webinars y cómo inscribirte")
    print("• Precios, requisitos y certificación")
    print("• Cualquier otra pregunta relacionada")
    print("\nComandos especiales:")
    print("• 'salir' - Terminar conversación")
    print("• 'métricas' - Ver estadísticas del chatbot")
    print("• 'reset métricas' - Reiniciar estadísticas")
    print("• 'exportar métricas json/csv' - Exportar métricas")
    print("• 'resumen conversación <id>' - Ver resumen de conversación")
    print("• 'tendencias' - Ver análisis de tendencias")
    print("• 'sugerencias' - Ver sugerencias de IA")
    print("• 'health check' o 'salud' - Verificar estado del chatbot")
    print("• 'feedback <tipo> [comentario]' - Dar feedback (positive/negative/helpful/not_helpful)")
    print("\nEscribe 'salir' para terminar la conversación.\n")
    
    conversation_history = []
    conversation_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        user_input = input("Tú: ").strip()
        
        if user_input.lower() in ['salir', 'exit', 'quit', 'adiós']:
            print("\n¡Gracias por usar nuestro chatbot! Que tengas un excelente día. 👋")
            # Mostrar métricas finales
            metrics = chatbot.get_metrics()
            print(f"\n📊 Resumen de la sesión:")
            print(f"   • Mensajes procesados: {metrics['total_messages']}")
            print(f"   • Escalaciones: {metrics['total_escalations']}")
            print(f"   • Tasa de escalación: {metrics['escalation_rate']:.1%}")
            print(f"   • Confianza promedio: {metrics['average_confidence']:.2f}")
            break
        
        if not user_input:
            continue
        
        # Comandos especiales
        if user_input.lower() == 'métricas':
            metrics = chatbot.get_metrics()
            print("\n📊 Métricas del Chatbot:")
            print(f"   • Total mensajes: {metrics['total_messages']}")
            print(f"   • Total escalaciones: {metrics['total_escalations']}")
            print(f"   • Tasa de escalación: {metrics['escalation_rate']:.1%}")
            print(f"   • Confianza promedio: {metrics['average_confidence']:.2f}")
            print(f"   • Tiempo promedio: {format_response_time(metrics['average_processing_time'])}")
            print(f"   • Tasa de match FAQ: {metrics['faq_match_rate']:.1%}")
            print(f"   • Tamaño del cache: {len(chatbot.response_cache)}")
            print(f"   • Distribución de intenciones:")
            for intent, count in metrics['intent_distribution'].items():
                print(f"     - {intent}: {count}")
            print()
            continue
        
        if user_input.lower() == 'reset métricas':
            chatbot.reset_metrics()
            print("✅ Métricas reiniciadas\n")
            continue
        
        if user_input.lower().startswith('exportar métricas'):
            parts = user_input.lower().split()
            format_type = 'json'
            if len(parts) > 2 and parts[2] in ['json', 'csv']:
                format_type = parts[2]
            
            output_file = chatbot.export_metrics(format=format_type)
            print(f"✅ Métricas exportadas a: {output_file}\n")
            continue
        
        if user_input.lower().startswith('resumen conversación'):
            parts = user_input.split()
            if len(parts) > 2:
                conv_id = parts[2]
                summary = chatbot.get_conversation_summary(conv_id)
                if summary:
                    print(f"\n📋 Resumen de conversación {conv_id}:")
                    print(f"   • Total mensajes: {summary['total_messages']}")
                    print(f"   • Mensajes usuario: {summary['user_messages']}")
                    print(f"   • Mensajes bot: {summary['bot_messages']}")
                    print(f"   • Temas principales: {', '.join(summary.get('topics', []))}")
                    print(f"   • Sentimiento: Positivo {summary['sentiment']['positive']:.1%}, "
                          f"Negativo {summary['sentiment']['negative']:.1%}, "
                          f"Neutro {summary['sentiment']['neutral']:.1%}")
                    print()
                else:
                    print(f"❌ Conversación {conv_id} no encontrada\n")
            else:
                print("❌ Uso: resumen conversación <conversation_id>\n")
            continue
        
        if user_input.lower() == 'tendencias':
            trends = chatbot.get_trends(days=7)
            if 'error' not in trends:
                print("\n📈 Tendencias (últimos 7 días):")
                print(f"   • Intención más común: {trends['intent_trends'].get('most_common_intent', 'N/A')}")
                print(f"   • Escalaciones promedio/día: {trends['escalation_trends'].get('average_per_day', 0):.1f}")
                print(f"   • Hora pico: {trends['peak_hours'].get('peak_hour', 'N/A')}:00")
                print()
            else:
                print(f"❌ {trends.get('error', 'Error desconocido')}\n")
            continue
        
        if user_input.lower() == 'sugerencias':
            suggestions = chatbot.get_ai_suggestions()
            if suggestions:
                print("\n💡 Sugerencias de IA:")
                for i, suggestion in enumerate(suggestions, 1):
                    priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡"
                    print(f"   {i}. {priority_icon} [{suggestion['priority']}] {suggestion['message']}")
                    print(f"      Acción: {suggestion['action']}")
                print()
            else:
                print("✅ No hay sugerencias en este momento. El chatbot está funcionando bien.\n")
            continue
        
        if user_input.lower() == 'health check' or user_input.lower() == 'salud':
            health = chatbot.health_check()
            status_icon = "✅" if health['status'] == 'healthy' else "⚠️"
            print(f"\n{status_icon} Health Check del Chatbot:")
            print(f"   • Estado: {health['status']}")
            print(f"   • Cache: {health.get('cache_size', 0)} respuestas")
            print(f"   • FAQs: {health.get('total_faqs', 0)} disponibles")
            if health.get('issues'):
                print(f"   • Problemas detectados:")
                for issue in health['issues']:
                    print(f"     - {issue}")
            print()
            continue
        
        if user_input.lower().startswith('feedback'):
            parts = user_input.split()
            if len(parts) >= 3:
                feedback_type = parts[1].lower()
                if feedback_type in ['positive', 'negative', 'helpful', 'not_helpful']:
                    comment = " ".join(parts[2:]) if len(parts) > 2 else None
                    # Usar el último conversation_id
                    success = chatbot.add_feedback(
                        conversation_id=conversation_id,
                        message_id=f"msg_{len(conversation_history)}",
                        feedback_type=feedback_type,
                        comment=comment
                    )
                    if success:
                        print(f"✅ Feedback '{feedback_type}' registrado. ¡Gracias!\n")
                    else:
                        print("❌ Error registrando feedback\n")
                else:
                    print("❌ Tipo de feedback inválido. Usa: positive, negative, helpful, not_helpful\n")
            else:
                # Mostrar estadísticas de feedback
                stats = chatbot.get_feedback_stats()
                if stats:
                    print("\n📊 Estadísticas de Feedback:")
                    print(f"   • Total: {stats['total']}")
                    print(f"   • Positivo: {stats['positive']} ({stats['positive_rate']:.1%})")
                    print(f"   • Negativo: {stats['negative']}")
                    print(f"   • Útil: {stats['helpful']} ({stats['helpful_rate']:.1%})")
                    print()
                else:
                    print("ℹ️  Sistema de feedback no disponible\n")
            continue
        
        response = chatbot.process_message(user_input, conversation_history, conversation_id)
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            continue
        
        print(f"\n🤖 Chatbot: {response['response']}")
        
        if response.get('suggested_actions'):
            print("\n💡 Acciones sugeridas:")
            for i, action in enumerate(response['suggested_actions'], 1):
                print(f"   {i}. {action}")
        
        if response.get('requires_escalation'):
            print(f"\n⚠️  Escalación: {response.get('escalation_reason', 'N/A')}")
        
        print(f"\n[Confianza: {response['confidence']:.2f} | Intención: {response['intent']} | "
              f"Tiempo: {response.get('processing_time', 0):.3f}s]\n")
        
        # Guardar en historial
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        conversation_history.append({
            "role": "assistant",
            "content": response['response'],
            "timestamp": response['timestamp']
        })


if __name__ == "__main__":
    main()

