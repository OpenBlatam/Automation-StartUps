"""
Sistema Avanzado de Chatbot para Servicio al Cliente
Autor: Consultoría en Automatización
Versión: 2.0.0 - Mejorado

Funcionalidades:
- Análisis de sentimientos
- Contexto conversacional avanzado
- A/B Testing
- Detección de intención mejorada
- Dashboard de métricas en tiempo real
- Integraciones robustas con CRM y canales
"""

import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
from pathlib import Path
from collections import deque
import uuid

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Niveles de prioridad para tickets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Channel(Enum):
    """Canales de comunicación soportados"""
    WEB = "web"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    TELEGRAM = "telegram"
    INTERCOM = "intercom"
    DIALOGFLOW = "dialogflow"


class Language(Enum):
    """Idiomas soportados"""
    ES = "es"
    EN = "en"
    PT = "pt"
    FR = "fr"


class Sentiment(Enum):
    """Análisis de sentimientos"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"


class Intent(Enum):
    """Intenciones detectadas"""
    QUESTION = "question"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    REQUEST = "request"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    TECHNICAL_ISSUE = "technical_issue"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"


@dataclass
class ChatMessage:
    """Estructura de mensaje del chat"""
    user_id: str
    message: str
    timestamp: datetime
    channel: Channel
    language: Language = Language.ES
    session_id: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChatResponse:
    """Estructura de respuesta del chatbot"""
    message: str
    confidence: float
    action: str  # "answer", "escalate", "request_info"
    ticket_id: Optional[str] = None
    suggested_actions: List[str] = None
    metadata: Dict = None
    sentiment: Optional[Sentiment] = None
    intent: Optional[Intent] = None
    ab_test_variant: Optional[str] = None

    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversationContext:
    """Contexto de conversación para mantener historial"""
    session_id: str
    user_id: str
    messages: deque
    language: Language
    sentiment_history: List[Sentiment]
    intents_history: List[Intent]
    created_at: datetime
    last_activity: datetime
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = deque(maxlen=20)  # Últimos 20 mensajes
        if self.sentiment_history is None:
            self.sentiment_history = []
        if self.intents_history is None:
            self.intents_history = []


class ChatbotEngine:
    """
    Motor principal del chatbot con lógica avanzada
    """
    
    def __init__(self, config_path: str = "chatbot_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.faqs = self._load_faqs()
        self.responses = self._load_responses()
        self.escalation_keywords = self._load_escalation_keywords()
        self.conversations: Dict[str, ConversationContext] = {}  # Contexto de conversaciones
        self.ab_test_variants = {}  # Variantes para A/B testing
        self.metrics = {
            "total_interactions": 0,
            "resolved_first_contact": 0,
            "escalated": 0,
            "avg_response_time": 0.0,
            "satisfaction_scores": [],
            "sentiment_distribution": {
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "frustrated": 0
            },
            "intent_distribution": {},
            "conversation_lengths": [],
            "ab_test_results": {}
        }
        self._initialize_ab_tests()
        
    def _load_config(self) -> Dict:
        """Carga la configuración del chatbot"""
        config_file = Path(__file__).parent / "chatbot_config.json"
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar configuración: {e}")
        
        # Configuración por defecto
        return {
            "company_name": "[Nombre de la Empresa]",
            "product": "[Producto/Servicio]",
            "tone": "profesional pero cálido",
            "use_emojis": True,
            "auto_escalate_critical": True,
            "languages": ["es", "en"],
            "channels": ["web", "whatsapp", "email"],
            "settings": {
                "max_conversation_history": 10,
                "response_timeout": 30,
                "confidence_threshold": 0.7,
                "enable_sentiment_analysis": True,
                "enable_ab_testing": True
            }
        }
    
    def _initialize_ab_tests(self):
        """Inicializa variantes para A/B testing"""
        self.ab_test_variants = {
            "greeting": ["A", "B"],
            "response_tone": ["formal", "casual"],
            "suggested_actions": ["show", "hide"]
        }
    
    def _load_faqs(self) -> Dict:
        """Carga las FAQs desde archivo de configuración"""
        faq_path = Path(__file__).parent / "faqs.json"
        try:
            if faq_path.exists():
                with open(faq_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar FAQs: {e}")
        
        return {}
    
    def _load_responses(self) -> Dict:
        """Carga las respuestas personalizadas"""
        responses_path = Path(__file__).parent / "responses.json"
        try:
            if responses_path.exists():
                with open(responses_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar respuestas: {e}")
        
        return {}
    
    def _load_escalation_keywords(self) -> Dict:
        """Carga palabras clave para escalamiento"""
        escalation_path = Path(__file__).parent / "escalation_keywords.json"
        try:
            if escalation_path.exists():
                with open(escalation_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"No se pudo cargar palabras clave: {e}")
        
        return {
            "critical": ["error crítico", "sistema caído", "no funciona", "urgente", "crítico"],
            "high": ["problema", "error", "bug", "fallo"],
            "medium": ["pregunta", "duda", "consulta", "información"]
        }
    
    def _detect_language(self, text: str) -> Language:
        """Detecta el idioma del mensaje con mejor precisión"""
        # Detección mejorada basada en palabras comunes y patrones
        spanish_words = ["cómo", "qué", "cuál", "dónde", "cuándo", "por qué", "es", "está", "tiene", "puedo"]
        english_words = ["how", "what", "which", "where", "when", "why", "is", "are", "have", "can"]
        portuguese_words = ["como", "o que", "qual", "onde", "quando", "por que", "é", "está", "tem"]
        french_words = ["comment", "quoi", "quel", "où", "quand", "pourquoi", "est", "a"]
        
        text_lower = text.lower()
        es_count = sum(1 for word in spanish_words if word in text_lower)
        en_count = sum(1 for word in english_words if word in text_lower)
        pt_count = sum(1 for word in portuguese_words if word in text_lower)
        fr_count = sum(1 for word in french_words if word in text_lower)
        
        counts = {
            Language.ES: es_count,
            Language.EN: en_count,
            Language.PT: pt_count,
            Language.FR: fr_count
        }
        
        detected = max(counts, key=counts.get)
        return detected if counts[detected] > 0 else Language.ES  # Default
    
    def _analyze_sentiment(self, text: str, language: Language) -> Sentiment:
        """
        Analiza el sentimiento del mensaje
        Versión mejorada con detección de frustración
        """
        text_lower = text.lower()
        lang_code = language.value
        
        # Palabras positivas
        positive_words = {
            "es": ["gracias", "excelente", "genial", "perfecto", "bueno", "me encanta", "fantástico"],
            "en": ["thanks", "excellent", "great", "perfect", "good", "love", "fantastic"],
            "pt": ["obrigado", "excelente", "ótimo", "perfeito", "bom"],
            "fr": ["merci", "excellent", "génial", "parfait", "bon"]
        }
        
        # Palabras negativas
        negative_words = {
            "es": ["mal", "terrible", "horrible", "malo", "problema", "error"],
            "en": ["bad", "terrible", "horrible", "problem", "error", "wrong"],
            "pt": ["ruim", "terrível", "horrível", "problema", "erro"],
            "fr": ["mauvais", "terrible", "horrible", "problème", "erreur"]
        }
        
        # Palabras de frustración
        frustrated_words = {
            "es": ["no funciona", "nunca", "siempre", "odio", "cansado", "frustrado", "molesto"],
            "en": ["doesn't work", "never", "always", "hate", "tired", "frustrated", "annoyed"],
            "pt": ["não funciona", "nunca", "sempre", "odeio", "cansado", "frustrado"],
            "fr": ["ne fonctionne pas", "jamais", "toujours", "déteste", "frustré"]
        }
        
        pos_words = positive_words.get(lang_code, positive_words["es"])
        neg_words = negative_words.get(lang_code, negative_words["es"])
        frus_words = frustrated_words.get(lang_code, frustrated_words["es"])
        
        positive_score = sum(1 for word in pos_words if word in text_lower)
        negative_score = sum(1 for word in neg_words if word in text_lower)
        frustrated_score = sum(1 for word in frus_words if word in text_lower)
        
        # Detectar mayúsculas (indica frustración)
        if any(c.isupper() for c in text if c.isalpha()) and len([c for c in text if c.isupper()]) > len(text) * 0.3:
            frustrated_score += 2
        
        # Detectar signos de exclamación múltiples
        if text.count("!") > 2:
            frustrated_score += 1
        
        if frustrated_score >= 2:
            return Sentiment.FRUSTRATED
        elif negative_score > positive_score:
            return Sentiment.NEGATIVE
        elif positive_score > negative_score:
            return Sentiment.POSITIVE
        else:
            return Sentiment.NEUTRAL
    
    def _detect_intent(self, text: str, language: Language) -> Intent:
        """Detecta la intención del usuario"""
        text_lower = text.lower()
        lang_code = language.value
        
        # Patrones de intención
        intent_patterns = {
            Intent.GREETING: {
                "es": ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"],
                "en": ["hello", "hi", "good morning", "good afternoon", "good evening", "hey"],
                "pt": ["olá", "bom dia", "boa tarde", "boa noite"],
                "fr": ["bonjour", "salut", "bonsoir"]
            },
            Intent.GOODBYE: {
                "es": ["adiós", "hasta luego", "nos vemos", "chao", "hasta pronto"],
                "en": ["bye", "goodbye", "see you", "later", "farewell"],
                "pt": ["tchau", "até logo", "até breve"],
                "fr": ["au revoir", "à bientôt", "salut"]
            },
            Intent.QUESTION: {
                "es": ["cómo", "qué", "cuál", "dónde", "cuándo", "por qué", "pregunta"],
                "en": ["how", "what", "which", "where", "when", "why", "question"],
                "pt": ["como", "o que", "qual", "onde", "quando"],
                "fr": ["comment", "quoi", "quel", "où", "quand"]
            },
            Intent.COMPLAINT: {
                "es": ["queja", "reclamo", "problema", "mal servicio", "insatisfecho"],
                "en": ["complaint", "issue", "problem", "bad service", "unsatisfied"],
                "pt": ["reclamação", "problema", "mau serviço"],
                "fr": ["plainte", "problème", "mauvais service"]
            },
            Intent.TECHNICAL_ISSUE: {
                "es": ["error", "bug", "fallo", "no funciona", "técnico", "sistema"],
                "en": ["error", "bug", "not working", "technical", "system", "crash"],
                "pt": ["erro", "bug", "não funciona", "técnico"],
                "fr": ["erreur", "bug", "ne fonctionne pas", "technique"]
            },
            Intent.BILLING: {
                "es": ["factura", "pago", "cobro", "tarifa", "precio", "billing"],
                "en": ["invoice", "payment", "charge", "fee", "price", "billing"],
                "pt": ["fatura", "pagamento", "cobrança", "preço"],
                "fr": ["facture", "paiement", "frais", "prix"]
            },
            Intent.REQUEST: {
                "es": ["necesito", "quiero", "solicito", "puedo", "me gustaría"],
                "en": ["need", "want", "request", "can", "would like"],
                "pt": ["preciso", "quero", "solicito", "posso"],
                "fr": ["besoin", "veux", "demande", "peux"]
            }
        }
        
        for intent, patterns in intent_patterns.items():
            lang_patterns = patterns.get(lang_code, patterns.get("es", []))
            if any(pattern in text_lower for pattern in lang_patterns):
                return intent
        
        return Intent.QUESTION  # Default
    
    def _check_escalation(self, message: str, language: Language) -> Tuple[bool, Priority]:
        """
        Verifica si el mensaje requiere escalamiento
        Retorna: (necesita_escalamiento, prioridad)
        """
        message_lower = message.lower()
        
        # Verificar palabras clave críticas
        critical_keywords = self.escalation_keywords.get("critical", [])
        if any(keyword in message_lower for keyword in critical_keywords):
            return True, Priority.CRITICAL
        
        # Verificar palabras clave de alta prioridad
        high_keywords = self.escalation_keywords.get("high", [])
        if any(keyword in message_lower for keyword in high_keywords):
            return True, Priority.HIGH
        
        # Verificar si menciona problemas técnicos específicos
        technical_issues = ["no puedo", "no funciona", "error", "problema técnico"]
        if any(issue in message_lower for issue in technical_issues):
            return True, Priority.MEDIUM
        
        return False, Priority.LOW
    
    def _find_best_faq_match(self, message: str, language: Language) -> Optional[Dict]:
        """
        Encuentra la mejor coincidencia de FAQ usando similitud semántica
        """
        message_lower = message.lower()
        lang_code = language.value
        
        if lang_code not in self.faqs:
            return None
        
        best_match = None
        best_score = 0.0
        
        for faq in self.faqs[lang_code]:
            question = faq.get("question", "").lower()
            keywords = faq.get("keywords", [])
            
            # Calcular score de coincidencia
            score = 0.0
            
            # Coincidencia exacta de palabras clave
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += 2.0
            
            # Coincidencia parcial de la pregunta
            question_words = set(question.split())
            message_words = set(message_lower.split())
            common_words = question_words.intersection(message_words)
            if len(question_words) > 0:
                score += len(common_words) / len(question_words) * 1.5
            
            # Coincidencia de sinónimos
            synonyms = faq.get("synonyms", [])
            for synonym in synonyms:
                if synonym.lower() in message_lower:
                    score += 1.0
            
            if score > best_score:
                best_score = score
                best_match = faq
        
        # Solo retornar si el score es suficientemente alto
        if best_score >= 1.0:
            return best_match
        
        return None
    
    def _format_response(self, text: str, language: Language, use_emojis: bool = True) -> str:
        """
        Formatea la respuesta con el tono apropiado y emojis
        """
        if not use_emojis:
            return text
        
        # Agregar emojis contextuales según el contenido
        emoji_map = {
            "gracias": "🙏",
            "bienvenido": "👋",
            "ayuda": "💡",
            "éxito": "✅",
            "error": "⚠️",
            "información": "ℹ️",
            "precio": "💰",
            "plan": "📋",
            "reporte": "📊",
            "exportar": "📤",
            "importar": "📥",
            "configuración": "⚙️",
            "soporte": "🛟",
            "contacto": "📞"
        }
        
        # Buscar y agregar emojis relevantes
        text_lower = text.lower()
        for keyword, emoji in emoji_map.items():
            if keyword in text_lower and emoji not in text:
                # Agregar emoji al inicio si es apropiado
                if text.startswith("Hola") or text.startswith("Hello"):
                    text = f"{emoji} {text}"
                elif keyword in text_lower[:50]:  # Solo en las primeras palabras
                    text = text.replace(keyword, f"{keyword} {emoji}", 1)
        
        return text
    
    def _create_ticket(self, user_id: str, message: str, priority: Priority, 
                      channel: Channel, language: Language) -> str:
        """
        Crea un ticket automático para escalamiento
        """
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id[:6]}"
        
        ticket_data = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "message": message,
            "priority": priority.value,
            "channel": channel.value,
            "language": language.value,
            "created_at": datetime.now().isoformat(),
            "status": "open"
        }
        
        # Guardar ticket (en producción, esto se enviaría a un sistema de tickets)
        tickets_path = Path(__file__).parent / "tickets" / f"{ticket_id}.json"
        tickets_path.parent.mkdir(exist_ok=True)
        
        with open(tickets_path, 'w', encoding='utf-8') as f:
            json.dump(ticket_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ticket creado: {ticket_id} - Prioridad: {priority.value}")
        return ticket_id
    
    def _get_or_create_conversation(self, user_id: str, session_id: str = None) -> ConversationContext:
        """Obtiene o crea un contexto de conversación"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                messages=deque(maxlen=20),
                language=Language.ES,
                sentiment_history=[],
                intents_history=[],
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
        
        self.conversations[session_id].last_activity = datetime.now()
        return self.conversations[session_id]
    
    def _get_ab_test_variant(self, test_name: str, user_id: str) -> str:
        """Obtiene variante para A/B testing basada en user_id"""
        if not self.config.get("settings", {}).get("enable_ab_testing", False):
            return "A"  # Default
        
        variants = self.ab_test_variants.get(test_name, ["A", "B"])
        # Usar hash del user_id para consistencia
        hash_value = hash(user_id) % len(variants)
        return variants[hash_value]
    
    async def process_message(self, chat_message: ChatMessage) -> ChatResponse:
        """
        Procesa un mensaje y genera una respuesta con contexto mejorado
        """
        start_time = datetime.now()
        
        # Obtener o crear contexto de conversación
        if not chat_message.session_id:
            chat_message.session_id = str(uuid.uuid4())
        
        conversation = self._get_or_create_conversation(
            chat_message.user_id,
            chat_message.session_id
        )
        
        # Detectar idioma si no está especificado
        if not chat_message.language:
            chat_message.language = self._detect_language(chat_message.message)
            conversation.language = chat_message.language
        
        # Analizar sentimiento
        sentiment = self._analyze_sentiment(chat_message.message, chat_message.language)
        conversation.sentiment_history.append(sentiment)
        self.metrics["sentiment_distribution"][sentiment.value] = \
            self.metrics["sentiment_distribution"].get(sentiment.value, 0) + 1
        
        # Detectar intención
        intent = self._detect_intent(chat_message.message, chat_message.language)
        conversation.intents_history.append(intent)
        intent_key = intent.value
        self.metrics["intent_distribution"][intent_key] = \
            self.metrics["intent_distribution"].get(intent_key, 0) + 1
        
        # Guardar mensaje en historial
        conversation.messages.append({
            "message": chat_message.message,
            "timestamp": chat_message.timestamp,
            "sentiment": sentiment.value,
            "intent": intent.value
        })
        
        # Verificar escalamiento (mejorado con sentimiento)
        needs_escalation, priority = self._check_escalation(
            chat_message.message, 
            chat_message.language
        )
        
        # Escalar automáticamente si el sentimiento es muy negativo o frustrado
        if sentiment in [Sentiment.FRUSTRATED, Sentiment.NEGATIVE] and \
           len(conversation.sentiment_history) >= 2 and \
           sum(1 for s in conversation.sentiment_history[-3:] if s in [Sentiment.NEGATIVE, Sentiment.FRUSTRATED]) >= 2:
            needs_escalation = True
            priority = Priority.HIGH
        
        if needs_escalation and self.config.get("auto_escalate_critical", True):
            # Crear ticket y escalar
            ticket_id = self._create_ticket(
                chat_message.user_id,
                chat_message.message,
                priority,
                chat_message.channel,
                chat_message.language
            )
            
            self.metrics["escalated"] += 1
            
            # Respuesta de escalamiento
            lang_code = chat_message.language.value
            escalation_responses = self.responses.get("escalation", {})
            escalation_msg = escalation_responses.get(
                lang_code,
                escalation_responses.get("es", "Hemos creado un ticket para tu consulta. Un agente se pondrá en contacto contigo pronto.")
            )
            
            response = ChatResponse(
                message=self._format_response(
                    f"{escalation_msg} Tu número de ticket es: {ticket_id} 🎫",
                    chat_message.language
                ),
                confidence=1.0,
                action="escalate",
                ticket_id=ticket_id,
                suggested_actions=["Ver estado del ticket", "Contactar soporte directo"],
                metadata={"priority": priority.value, "sentiment": sentiment.value},
                sentiment=sentiment,
                intent=intent
            )
            
            # Registrar longitud de conversación antes de escalar
            self.metrics["conversation_lengths"].append(len(conversation.messages))
            
            return response
        
        # Buscar respuesta en FAQs
        faq_match = self._find_best_faq_match(
            chat_message.message,
            chat_message.language
        )
        
        if faq_match:
            answer = faq_match.get("answer", "")
            confidence = faq_match.get("confidence", 0.8)
            
            # A/B Testing: Variar el tono de la respuesta
            ab_variant = self._get_ab_test_variant("response_tone", chat_message.user_id)
            if ab_variant == "casual" and sentiment == Sentiment.POSITIVE:
                # Hacer la respuesta más casual para usuarios positivos
                answer = answer.replace("¡Hola!", "¡Hola! 😊")
            
            # Agregar información adicional si está disponible
            additional_info = faq_match.get("additional_info", "")
            if additional_info:
                answer += f"\n\n{additional_info}"
            
            # Agregar acciones sugeridas (A/B testing)
            suggested_actions = faq_match.get("suggested_actions", [])
            show_actions = self._get_ab_test_variant("suggested_actions", chat_message.user_id) == "show"
            if not show_actions:
                suggested_actions = []
            
            # Personalizar respuesta según sentimiento
            if sentiment == Sentiment.FRUSTRATED:
                answer = f"Entiendo tu frustración. {answer}\n\n¿Hay algo específico que podamos hacer para ayudarte mejor? 🤝"
            elif sentiment == Sentiment.NEGATIVE:
                answer = f"Lamento los inconvenientes. {answer}"
            
            self.metrics["resolved_first_contact"] += 1
            self.metrics["total_interactions"] += 1
            
            # Calcular tiempo de respuesta
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_avg_response_time(response_time)
            
            # Registrar resultado de A/B test
            if "ab_test_results" not in self.metrics:
                self.metrics["ab_test_results"] = {}
            test_key = f"response_tone_{ab_variant}"
            self.metrics["ab_test_results"][test_key] = \
                self.metrics["ab_test_results"].get(test_key, 0) + 1
            
            return ChatResponse(
                message=self._format_response(answer, chat_message.language),
                confidence=confidence,
                action="answer",
                suggested_actions=suggested_actions,
                metadata={"faq_id": faq_match.get("id"), "ab_variant": ab_variant},
                sentiment=sentiment,
                intent=intent,
                ab_test_variant=ab_variant
            )
        
        # Respuesta por defecto si no se encuentra match
        lang_code = chat_message.language.value
        default_responses = self.responses.get("default", {})
        default_msg = default_responses.get(
            lang_code,
            default_responses.get("es", "Lo siento, no entendí tu pregunta. ¿Podrías reformularla?")
        )
        
        # Usar contexto de conversación para mejorar respuesta
        context_hint = ""
        if len(conversation.intents_history) > 0:
            last_intent = conversation.intents_history[-1]
            if last_intent == Intent.BILLING:
                context_hint = "\n\n💡 Si tu pregunta es sobre facturación, puedo ayudarte con eso."
            elif last_intent == Intent.TECHNICAL_ISSUE:
                context_hint = "\n\n💡 Si tienes un problema técnico, puedo crear un ticket para ti."
        
        self.metrics["total_interactions"] += 1
        
        # Detectar si es saludo o despedida
        if intent == Intent.GREETING:
            greeting_responses = self.responses.get("greeting", {})
            greeting_msg = greeting_responses.get(
                lang_code,
                greeting_responses.get("es", "¡Hola! 👋 ¿En qué puedo ayudarte?")
            )
            return ChatResponse(
                message=self._format_response(greeting_msg, chat_message.language),
                confidence=0.9,
                action="answer",
                suggested_actions=["Ver FAQs", "Información de productos"],
                sentiment=sentiment,
                intent=intent
            )
        elif intent == Intent.GOODBYE:
            goodbye_responses = self.responses.get("goodbye", {})
            goodbye_msg = goodbye_responses.get(
                lang_code,
                goodbye_responses.get("es", "¡Fue un placer ayudarte! 😊 ¡Que tengas un excelente día!")
            )
            return ChatResponse(
                message=self._format_response(goodbye_msg, chat_message.language),
                confidence=0.9,
                action="answer",
                sentiment=sentiment,
                intent=intent
            )
        
        return ChatResponse(
            message=self._format_response(
                f"{default_msg}{context_hint} 💬\n\nPuedo ayudarte con:\n- Preguntas frecuentes\n- Información de productos\n- Soporte técnico\n\n¿En qué más puedo ayudarte?",
                chat_message.language
            ),
            confidence=0.3,
            action="request_info",
            suggested_actions=["Ver FAQs", "Contactar soporte", "Hablar con agente"],
            sentiment=sentiment,
            intent=intent
        )
    
    def _update_avg_response_time(self, new_time: float):
        """Actualiza el tiempo promedio de respuesta"""
        total = self.metrics["total_interactions"]
        current_avg = self.metrics["avg_response_time"]
        self.metrics["avg_response_time"] = (
            (current_avg * (total - 1) + new_time) / total
            if total > 0 else new_time
        )
    
    def get_metrics(self) -> Dict:
        """Obtiene las métricas actuales del chatbot con análisis avanzado"""
        total = self.metrics["total_interactions"]
        resolution_rate = (
            (self.metrics["resolved_first_contact"] / total * 100)
            if total > 0 else 0
        )
        
        avg_satisfaction = (
            sum(self.metrics["satisfaction_scores"]) / len(self.metrics["satisfaction_scores"])
            if self.metrics["satisfaction_scores"] else 0
        )
        
        # Calcular promedio de longitud de conversación
        avg_conversation_length = (
            sum(self.metrics["conversation_lengths"]) / len(self.metrics["conversation_lengths"])
            if self.metrics["conversation_lengths"] else 0
        )
        
        # Análisis de sentimientos
        total_sentiments = sum(self.metrics["sentiment_distribution"].values())
        sentiment_percentages = {
            k: round((v / total_sentiments * 100) if total_sentiments > 0 else 0, 2)
            for k, v in self.metrics["sentiment_distribution"].items()
        }
        
        # Verificar si se cumplen objetivos
        targets = self.config.get("metrics", {})
        target_resolution = targets.get("target_resolution_rate", 80)
        target_satisfaction = targets.get("target_satisfaction", 4.5)
        target_response_time = targets.get("target_response_time", 60)
        
        return {
            **self.metrics,
            "resolution_rate": round(resolution_rate, 2),
            "avg_satisfaction": round(avg_satisfaction, 2),
            "escalation_rate": round(
                (self.metrics["escalated"] / total * 100) if total > 0 else 0, 2
            ),
            "avg_conversation_length": round(avg_conversation_length, 2),
            "sentiment_percentages": sentiment_percentages,
            "targets": {
                "resolution_rate": {
                    "target": target_resolution,
                    "current": round(resolution_rate, 2),
                    "met": resolution_rate >= target_resolution
                },
                "satisfaction": {
                    "target": target_satisfaction,
                    "current": round(avg_satisfaction, 2),
                    "met": avg_satisfaction >= target_satisfaction
                },
                "response_time": {
                    "target": target_response_time,
                    "current": round(self.metrics["avg_response_time"], 2),
                    "met": self.metrics["avg_response_time"] <= target_response_time
                }
            },
            "active_conversations": len(self.conversations),
            "total_sessions": len([c for c in self.conversations.values() 
                                 if (datetime.now() - c.last_activity).total_seconds() < 3600])
        }
    
    def record_satisfaction(self, score: int, session_id: str = ""):
        """
        Registra una calificación de satisfacción (1-5)
        """
        if 1 <= score <= 5:
            self.metrics["satisfaction_scores"].append(score)
            logger.info(f"Satisfacción registrada: {score}/5 para sesión {session_id}")


# Integraciones con canales externos
class ChannelAdapter:
    """Adaptador base para diferentes canales"""
    
    def __init__(self, chatbot: ChatbotEngine):
        self.chatbot = chatbot
    
    async def send_message(self, user_id: str, message: str, channel: Channel, 
                          language: Language = Language.ES) -> ChatResponse:
        """Envía un mensaje al chatbot y retorna la respuesta"""
        chat_message = ChatMessage(
            user_id=user_id,
            message=message,
            timestamp=datetime.now(),
            channel=channel,
            language=language
        )
        return await self.chatbot.process_message(chat_message)


class WebAdapter(ChannelAdapter):
    """Adaptador para integración web"""
    pass


class WhatsAppAdapter(ChannelAdapter):
    """Adaptador para WhatsApp Business API"""
    
    async def send_whatsapp_message(self, phone_number: str, message: str, 
                                    language: Language = Language.ES) -> Dict:
        """Envía mensaje a través de WhatsApp"""
        user_id = f"whatsapp_{phone_number}"
        response = await self.send_message(
            user_id, message, Channel.WHATSAPP, language
        )
        
        # Aquí se integraría con la API de WhatsApp Business
        # return await whatsapp_api.send_message(phone_number, response.message)
        
        return {
            "status": "sent",
            "response": response.message,
            "ticket_id": response.ticket_id
        }


class EmailAdapter(ChannelAdapter):
    """Adaptador para respuestas por email"""
    
    async def send_email_response(self, email: str, subject: str, message: str,
                                 language: Language = Language.ES) -> Dict:
        """Procesa email y envía respuesta"""
        user_id = f"email_{email}"
        response = await self.send_message(
            user_id, message, Channel.EMAIL, language
        )
        
        # Aquí se integraría con servicio de email (SendGrid, AWS SES, etc.)
        # return await email_service.send(email, subject, response.message)
        
        return {
            "status": "sent",
            "response": response.message,
            "ticket_id": response.ticket_id
        }


# Integración con CRM
class CRMIntegration:
    """Integración con sistemas CRM (Salesforce, HubSpot, etc.)"""
    
    def __init__(self, crm_type: str = "salesforce", api_key: str = None):
        self.crm_type = crm_type
        self.api_key = api_key
    
    def create_lead(self, user_data: Dict) -> str:
        """Crea un lead en el CRM"""
        # Implementación específica según el CRM
        if self.crm_type == "salesforce":
            return self._create_salesforce_lead(user_data)
        elif self.crm_type == "hubspot":
            return self._create_hubspot_lead(user_data)
        return None
    
    def _create_salesforce_lead(self, user_data: Dict) -> str:
        """Crea lead en Salesforce"""
        # Aquí se integraría con Salesforce API
        logger.info(f"Creando lead en Salesforce: {user_data}")
        return "LEAD-12345"
    
    def _create_hubspot_lead(self, user_data: Dict) -> str:
        """Crea lead en HubSpot"""
        # Aquí se integraría con HubSpot API
        logger.info(f"Creando lead en HubSpot: {user_data}")
        return "LEAD-12345"
    
    def sync_ticket(self, ticket_id: str, ticket_data: Dict) -> bool:
        """Sincroniza ticket con CRM"""
        logger.info(f"Sincronizando ticket {ticket_id} con {self.crm_type}")
        return True


# Función principal de ejemplo
async def main():
    """Ejemplo de uso del chatbot"""
    chatbot = ChatbotEngine()
    
    # Ejemplo de mensaje
    message = ChatMessage(
        user_id="user_123",
        message="¿Cómo exportar reportes?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    print(f"Respuesta: {response.message}")
    print(f"Confianza: {response.confidence}")
    print(f"Acción: {response.action}")
    
    # Mostrar métricas
    metrics = chatbot.get_metrics()
    print(f"\nMétricas: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())


