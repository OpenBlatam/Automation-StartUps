#!/usr/bin/env python3
"""
Chatbot de Rastreo de Pedidos para E-commerce
Asistente especializado en ayudar a los clientes a rastrear sus pedidos,
proporcionar actualizaciones en tiempo real, responder preguntas sobre pagos
y escalar a soporte humano cuando sea necesario.

🎯 Uso:
    python3 chatbot_rastreo_pedidos.py
    
    O desde código:
    from chatbot_rastreo_pedidos import OrderTrackingChatbot
    chatbot = OrderTrackingChatbot(
        company_name="Mi Empresa",
        bot_name="Asistente de Pedidos"
    )
    response = chatbot.process_message("¿Dónde está mi pedido ORD-2024-001234?")

✨ Funcionalidades:
- Rastreo de pedidos por ID
- Actualizaciones en tiempo real
- Consultas sobre estado de pago
- Respuestas sobre fechas de entrega
- Escalación automática a soporte humano
- Tono amigable y confiado
- Integración con base de datos
- Logging estructurado
- Métricas y estadísticas
- Persistencia de conversaciones
"""

import re
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import traceback
from functools import lru_cache
import hashlib

# Intentar importar requests para LLM
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Intentar importar utilidades compartidas
try:
    from chatbot_utils import (
        export_metrics_to_json, export_metrics_to_csv,
        analyze_sentiment_basic, extract_keywords,
        calculate_text_similarity, format_response_time,
        generate_conversation_summary, create_metrics_dashboard_data
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Funciones básicas si no están disponibles
    def analyze_sentiment_basic(message):
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
    
    def extract_keywords(text, min_length=3, max_keywords=10):
        return []


class IntentType(Enum):
    """Tipos de intenciones detectadas"""
    TRACK_ORDER = "track_order"
    PAYMENT_STATUS = "payment_status"
    DELIVERY_DATE = "delivery_date"
    CANCEL_ORDER = "cancel_order"
    REFUND = "refund"
    CHANGE_ADDRESS = "change_address"
    CONTACT_SUPPORT = "contact_support"
    ORDER_DETAILS = "order_details"
    SHIPPING_INFO = "shipping_info"
    PROBLEM_DETECTED = "problem_detected"
    OTHER = "other"


@dataclass
class ProblemDetection:
    """Detección de problemas en un pedido"""
    problem_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_action: str
    confidence: float


@dataclass
class ProblemPrediction:
    """Predicción de problemas futuros"""
    problem_type: str
    probability: float  # 0.0 - 1.0
    estimated_time: Optional[str]  # Cuándo podría ocurrir
    risk_factors: List[str]
    preventive_actions: List[str]
    confidence: float


@dataclass
class UserPattern:
    """Patrón de comportamiento del usuario"""
    customer_email: str
    common_intents: List[str]
    average_confidence: float
    escalation_rate: float
    preferred_response_style: str  # 'brief', 'detailed', 'friendly'
    common_problems: List[str]


@dataclass
class TroubleshootingStep:
    """Paso de troubleshooting"""
    step_number: int
    title: str
    description: str
    instructions: List[str]
    verification_question: Optional[str] = None
    expected_result: Optional[str] = None
    next_step_on_success: Optional[int] = None
    next_step_on_failure: Optional[int] = None
    auto_resolvable: bool = False


@dataclass
class TroubleshootingGuide:
    """Guía de troubleshooting para un problema"""
    problem_id: str
    problem_title: str
    problem_description: str
    category: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    steps: List[TroubleshootingStep]
    estimated_time_minutes: int
    auto_resolution_available: bool = False
    auto_resolution_script: Optional[str] = None


@dataclass
class TroubleshootingSession:
    """Sesión de troubleshooting activa"""
    session_id: str
    order_id: Optional[str]
    customer_email: str
    problem_description: str
    detected_problem_id: Optional[str]
    guide: Optional[TroubleshootingGuide]
    current_step: int
    status: str  # 'started', 'in_progress', 'resolved', 'escalated'
    started_at: datetime
    completed_steps: List[Dict]
    notes: List[str]
    ticket_id: Optional[str] = None


@dataclass
class OrderInfo:
    """Información de un pedido"""
    order_id: str
    status: str
    payment_status: str
    tracking_number: Optional[str]
    shipping_carrier: Optional[str]
    estimated_delivery_date: Optional[str]
    actual_delivery_date: Optional[str]
    total_amount: float
    currency: str
    items: List[Dict]
    shipping_address: Dict
    tracking_history: List[Dict]
    payment_history: List[Dict]
    created_at: str
    updated_at: str


@dataclass
class ChatbotResponse:
    """Respuesta del chatbot"""
    message: str
    confidence: float
    intent: str
    requires_escalation: bool
    escalation_reason: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    order_info: Optional[OrderInfo] = None
    processing_time: Optional[float] = None


@dataclass
class ChatbotMetrics:
    """Métricas del chatbot"""
    total_messages: int = 0
    total_escalations: int = 0
    intent_counts: Dict[str, int] = None
    average_confidence: float = 0.0
    average_processing_time: float = 0.0
    orders_tracked: int = 0
    payment_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    sentiment_positive: int = 0
    sentiment_negative: int = 0
    sentiment_neutral: int = 0
    rate_limit_hits: int = 0
    
    def __post_init__(self):
        if self.intent_counts is None:
            self.intent_counts = defaultdict(int)


@dataclass
class RateLimitConfig:
    """Configuración de rate limiting"""
    max_requests: int = 60
    time_window: int = 60  # segundos
    block_duration: int = 300  # segundos


class RateLimiter:
    """Sistema de rate limiting para chatbots"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.requests = defaultdict(deque)  # user_id -> deque de timestamps
        self.blocked_users = {}  # user_id -> unblock_time
    
    def is_allowed(self, user_id: str = "default") -> Tuple[bool, Optional[str]]:
        """Verifica si un usuario puede hacer una request"""
        now = time.time()
        
        # Verificar si está bloqueado
        if user_id in self.blocked_users:
            unblock_time = self.blocked_users[user_id]
            if now < unblock_time:
                remaining = int(unblock_time - now)
                return False, f"Usuario bloqueado. Intenta de nuevo en {remaining} segundos"
            else:
                del self.blocked_users[user_id]
        
        # Limpiar requests antiguos
        user_requests = self.requests[user_id]
        cutoff_time = now - self.config.time_window
        
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()
        
        # Verificar límite
        if len(user_requests) >= self.config.max_requests:
            self.blocked_users[user_id] = now + self.config.block_duration
            return False, f"Límite de requests excedido. Bloqueado por {self.config.block_duration} segundos"
        
        # Registrar request
        user_requests.append(now)
        return True, None


class OrderTrackingChatbot:
    """
    Chatbot especializado en rastreo de pedidos para e-commerce.
    Proporciona actualizaciones en tiempo real y responde consultas sobre pedidos.
    """
    
    def __init__(
        self,
        company_name: str = "[Nombre de la Empresa]",
        bot_name: str = "[Nombre del Bot]",
        db_connection=None,
        enable_logging: bool = True,
        persist_conversations: bool = True,
        conversation_dir: str = "chatbot_conversations",
        enable_rate_limiting: bool = True
    ):
        """
        Inicializa el chatbot de rastreo de pedidos.
        
        Args:
            company_name: Nombre de la empresa
            bot_name: Nombre del bot
            db_connection: Conexión a base de datos (opcional)
            enable_logging: Habilita logging estructurado
            persist_conversations: Guarda conversaciones en archivos JSON
            conversation_dir: Directorio para guardar conversaciones
            enable_rate_limiting: Habilita rate limiting
        """
        self.company_name = company_name
        self.bot_name = bot_name
        self.db_connection = db_connection
        self.metrics = ChatbotMetrics()
        self.enable_logging = enable_logging
        self.persist_conversations = persist_conversations
        self.conversation_dir = Path(conversation_dir)
        
        # Cache de respuestas frecuentes con TTL
        self.response_cache = {}
        self.cache_enabled = True
        self.cache_max_size = 100
        self.cache_ttl = 3600  # 1 hora
        
        # Rate limiting
        self.rate_limiter = RateLimiter(RateLimitConfig(
            max_requests=60,
            time_window=60,
            block_duration=300
        )) if enable_rate_limiting else None
        self.enable_rate_limiting = enable_rate_limiting
        
        # Análisis de sentimiento
        self.sentiment_keywords = {
            'positive': ['gracias', 'excelente', 'perfecto', 'genial', 'bueno', 'bien', 'satisfecho'],
            'negative': ['mal', 'problema', 'error', 'no funciona', 'malo', 'terrible', 'insatisfecho', 'queja']
        }
        
        # Detección de problemas
        self.problem_patterns = {
            'delayed_delivery': {
                'keywords': ['retraso', 'tarde', 'demora', 'lento', 'no llega'],
                'check_function': self._check_delivery_delay
            },
            'payment_issue': {
                'keywords': ['pago', 'cobro', 'factura', 'tarjeta rechazada'],
                'check_function': self._check_payment_issue
            },
            'wrong_address': {
                'keywords': ['dirección', 'direccion', 'envío', 'envio', 'incorrecto'],
                'check_function': self._check_address_issue
            },
            'damaged_package': {
                'keywords': ['dañado', 'roto', 'mal estado', 'defectuoso'],
                'check_function': None
            },
            'missing_item': {
                'keywords': ['falta', 'incompleto', 'no está', 'no viene'],
                'check_function': None
            }
        }
        
        # Aprendizaje de patrones de usuario
        self.user_patterns = {}  # email -> UserPattern
        self.conversation_history = defaultdict(list)  # email -> [conversations]
        
        # Predicción de problemas
        self.enable_predictions = True
        self.prediction_history = []  # Historial de predicciones para aprendizaje
        
        # Integración con LLM (opcional)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.enable_llm = bool(self.openai_api_key) and REQUESTS_AVAILABLE
        
        # Sistema de feedback
        self.feedback_history = defaultdict(list)  # order_id -> [feedback]
        
        # Soporte multi-idioma básico
        self.supported_languages = {
            'es': 'español',
            'en': 'english',
            'pt': 'português',
            'fr': 'français'
        }
        self.current_language = 'es'  # Default español
        self.translations = self._load_translations()
        
        # Análisis de tendencias
        self.trend_analysis = {
            'daily_queries': defaultdict(int),
            'common_problems': defaultdict(int),
            'peak_hours': defaultdict(int)
        }
        
        # Alertas proactivas
        self.proactive_alerts_enabled = True
        self.alert_thresholds = {
            'delayed_orders': 3,  # días
            'pending_payments': 48,  # horas
            'high_escalation_rate': 0.3  # 30%
        }
        
        # A/B Testing
        self.ab_tests = {}  # test_id -> config
        self.ab_results = defaultdict(list)  # test_id -> [results]
        
        # Análisis de satisfacción (NPS)
        self.nps_scores = []  # Lista de scores NPS
        self.satisfaction_surveys = defaultdict(list)  # order_id -> [surveys]
        
        # Plantillas de respuestas
        self.response_templates = self._load_response_templates()
        
        # Sistema de reportes automáticos
        self.auto_reports_enabled = False
        self.report_schedule = {}  # schedule_id -> config
        self.report_history = []  # Historial de reportes generados
        
        # Análisis de ROI
        self.roi_metrics = {
            'cost_per_conversation': 0.05,  # Costo estimado por conversación
            'saved_human_hours': 0,  # Horas humanas ahorradas
            'conversations_handled': 0,
            'escalations_prevented': 0
        }
        
        # Base de conocimiento
        self.knowledge_base = {}  # topic -> [articles]
        self._load_default_knowledge_base()
        
        # Respuestas rápidas (quick replies)
        self.quick_replies = {
            'track_order': ['Rastrear pedido', 'Estado de mi pedido', '¿Dónde está mi pedido?'],
            'payment': ['Estado del pago', 'Problema con el pago', 'Confirmar pago'],
            'delivery': ['Fecha de entrega', 'Cambiar dirección', 'Problema con entrega']
        }
        
        # Análisis de conversaciones
        self.conversation_analytics = {
            'session_duration': [],
            'messages_per_session': [],
            'resolution_time': []
        }
        
        # Mejoras de seguridad
        self.security_config = {
            'max_message_length': 1000,
            'blocked_keywords': ['spam', 'phishing'],  # Palabras bloqueadas
            'suspicious_patterns': []  # Patrones sospechosos detectados
        }
        
        # Sistema de Troubleshooting Guiado
        self.troubleshooting_sessions = {}  # session_id -> TroubleshootingSession
        self.troubleshooting_enabled = True
        self.auto_resolution_enabled = True
        self.troubleshooting_guides = self._load_troubleshooting_guides()
        
        # Configurar logging
        if enable_logging:
            self._setup_logging()
        
        # Crear directorio de conversaciones si no existe
        if persist_conversations:
            self.conversation_dir.mkdir(exist_ok=True)
        
        if enable_logging:
            self.logger.info(f"Chatbot {bot_name} inicializado para {company_name}")
    
    def _load_default_knowledge_base(self):
        """Carga base de conocimiento por defecto"""
        pass
    
    def _load_troubleshooting_guides(self) -> Dict[str, TroubleshootingGuide]:
        """Carga guías de troubleshooting para problemas comunes"""
        guides = {}
        
        # Guía para retraso en entrega
        guides['delayed_delivery'] = TroubleshootingGuide(
            problem_id='delayed_delivery',
            problem_title='Retraso en Entrega',
            problem_description='El pedido tiene retraso en la fecha de entrega estimada',
            category='delivery',
            severity='medium',
            estimated_time_minutes=5,
            auto_resolution_available=False,
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    title='Verificar estado del tracking',
                    description='Verifica el último estado del tracking en el sitio web del carrier',
                    instructions=[
                        '1. Visita el sitio web del carrier con tu número de tracking',
                        '2. Revisa la última actualización de ubicación',
                        '3. Verifica si hay alguna notificación de retraso'
                    ],
                    verification_question='¿Ves alguna actualización reciente en el tracking?',
                    expected_result='Actualización visible en el tracking'
                ),
                TroubleshootingStep(
                    step_number=2,
                    title='Contactar al carrier',
                    description='Si no hay actualizaciones, contacta al carrier directamente',
                    instructions=[
                        '1. Llama al número de atención del carrier',
                        '2. Proporciona tu número de tracking',
                        '3. Pregunta sobre el estado actual del paquete'
                    ],
                    verification_question='¿El carrier pudo darte información sobre el retraso?',
                    expected_result='Información obtenida del carrier'
                )
            ]
        )
        
        # Guía para problema de pago
        guides['payment_failed'] = TroubleshootingGuide(
            problem_id='payment_failed',
            problem_title='Pago Fallido',
            problem_description='El pago del pedido no se procesó correctamente',
            category='payment',
            severity='high',
            estimated_time_minutes=10,
            auto_resolution_available=True,
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    title='Verificar método de pago',
                    description='Verifica que tu método de pago esté activo y tenga fondos',
                    instructions=[
                        '1. Revisa el saldo de tu tarjeta o cuenta',
                        '2. Verifica que la tarjeta no esté vencida',
                        '3. Confirma que no haya restricciones en tu banco'
                    ],
                    verification_question='¿Tu método de pago está activo y tiene fondos?',
                    expected_result='Método de pago válido'
                ),
                TroubleshootingStep(
                    step_number=2,
                    title='Reintentar pago',
                    description='Intenta realizar el pago nuevamente',
                    instructions=[
                        '1. Ve a tu pedido pendiente',
                        '2. Selecciona "Reintentar pago"',
                        '3. Ingresa nuevamente los datos de pago'
                    ],
                    verification_question='¿El pago se procesó correctamente esta vez?',
                    expected_result='Pago procesado exitosamente',
                    auto_resolvable=True
                )
            ]
        )
        
        # Guía para dirección incorrecta
        guides['wrong_address'] = TroubleshootingGuide(
            problem_id='wrong_address',
            problem_title='Dirección de Envío Incorrecta',
            problem_description='La dirección de envío del pedido es incorrecta',
            category='shipping',
            severity='high',
            estimated_time_minutes=15,
            auto_resolution_available=False,
            steps=[
                TroubleshootingStep(
                    step_number=1,
                    title='Verificar estado del envío',
                    description='Verifica si el paquete ya fue enviado',
                    instructions=[
                        '1. Revisa el estado del pedido',
                        '2. Verifica si el estado es "enviado" o "en tránsito"',
                        '3. Si aún no se ha enviado, puedes cambiar la dirección'
                    ],
                    verification_question='¿El pedido ya fue enviado?',
                    expected_result='Estado del envío verificado'
                ),
                TroubleshootingStep(
                    step_number=2,
                    title='Contactar soporte',
                    description='Si el paquete ya fue enviado, contacta a soporte inmediatamente',
                    instructions=[
                        '1. Contacta a nuestro equipo de soporte',
                        '2. Proporciona el número de pedido',
                        '3. Indica la dirección correcta',
                        '4. El equipo intentará redirigir el paquete'
                    ],
                    verification_question='¿Contactaste a soporte?',
                    expected_result='Ticket creado con soporte'
                )
            ]
        )
        
        return guides
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"chatbot_rastreo_pedidos_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("OrderTrackingChatbot")
    
    def _get_cache_key(self, message: str, order_id: Optional[str] = None) -> str:
        """Genera una clave de cache para un mensaje"""
        # Normalizar mensaje
        normalized = re.sub(r'\s+', ' ', message.lower().strip())
        if order_id:
            normalized += f"|{order_id}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_cached_response(self, message: str, order_id: Optional[str] = None) -> Optional[ChatbotResponse]:
        """Obtiene respuesta del cache si existe y no ha expirado"""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(message, order_id)
        cached = self.response_cache.get(cache_key)
        
        if cached:
            # Verificar TTL
            if time.time() - cached.get('timestamp', 0) < self.cache_ttl:
                self.metrics.cache_hits += 1
                return cached.get('response')
            else:
                # Expirar entrada
                del self.response_cache[cache_key]
        
        self.metrics.cache_misses += 1
        return None
    
    def _cache_response(self, message: str, response: ChatbotResponse, order_id: Optional[str] = None):
        """Guarda respuesta en cache con TTL"""
        if not self.cache_enabled or response.confidence < 0.6:
            return
        
        # Limitar tamaño del cache
        if len(self.response_cache) >= self.cache_max_size:
            # Eliminar el más antiguo
            oldest_key = min(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k].get('timestamp', 0)
            )
            del self.response_cache[oldest_key]
        
        cache_key = self._get_cache_key(message, order_id)
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def _extract_order_id(self, message: str) -> Optional[str]:
        """
        Extrae el ID del pedido del mensaje.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            ID del pedido si se encuentra, None en caso contrario
        """
        # Patrones comunes de IDs de pedido
        patterns = [
            r'\bORD[-\s]?(\d{4}[-\s]?\d{6})\b',  # ORD-2024-001234
            r'\b(\d{4}[-\s]?\d{6})\b',  # 2024-001234
            r'\b#?(\d{8,12})\b',  # Números largos
            r'pedido[:\s]+([A-Z0-9-]+)',  # "pedido: ORD-123"
            r'order[:\s]+([A-Z0-9-]+)',  # "order: ORD-123"
        ]
        
        message_upper = message.upper()
        for pattern in patterns:
            match = re.search(pattern, message_upper, re.IGNORECASE)
            if match:
                order_id = match.group(1) if match.lastindex else match.group(0)
                # Normalizar formato
                order_id = re.sub(r'[-\s]', '-', order_id)
                return order_id
        
        return None
    
    def _get_order_from_db(self, order_id: str, customer_email: Optional[str] = None) -> Optional[OrderInfo]:
        """
        Obtiene información del pedido desde la base de datos.
        
        Args:
            order_id: ID del pedido
            customer_email: Email del cliente (opcional, para validación)
            
        Returns:
            Información del pedido o None si no se encuentra
        """
        if not self.db_connection:
            # Modo simulado para pruebas
            return self._get_mock_order(order_id)
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar pedido
            query = """
                SELECT 
                    o.id, o.order_id, o.customer_email, o.customer_name,
                    o.status, o.payment_status, o.tracking_number, o.shipping_carrier,
                    o.estimated_delivery_date, o.actual_delivery_date,
                    o.total_amount, o.currency, o.items, o.shipping_address,
                    o.created_at, o.updated_at
                FROM ecommerce_orders o
                WHERE o.order_id = %s
            """
            
            params = [order_id]
            if customer_email:
                query += " AND o.customer_email = %s"
                params.append(customer_email)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                return None
            
            # Obtener historial de tracking
            tracking_query = """
                SELECT status, location, carrier_status, carrier_message, timestamp, metadata
                FROM ecommerce_order_tracking
                WHERE order_id = %s
                ORDER BY timestamp DESC
            """
            cursor.execute(tracking_query, [row[0]])
            tracking_history = []
            for track_row in cursor.fetchall():
                tracking_history.append({
                    'status': track_row[0],
                    'location': track_row[1],
                    'carrier_status': track_row[2],
                    'carrier_message': track_row[3],
                    'timestamp': track_row[4].isoformat() if track_row[4] else None,
                    'metadata': track_row[5] if track_row[5] else {}
                })
            
            # Obtener historial de pagos
            payment_query = """
                SELECT payment_status, amount, transaction_id, timestamp
                FROM ecommerce_payment_updates
                WHERE order_id = %s
                ORDER BY timestamp DESC
            """
            cursor.execute(payment_query, [row[0]])
            payment_history = []
            for pay_row in cursor.fetchall():
                payment_history.append({
                    'payment_status': pay_row[0],
                    'amount': float(pay_row[1]) if pay_row[1] else None,
                    'transaction_id': pay_row[2],
                    'timestamp': pay_row[3].isoformat() if pay_row[3] else None
                })
            
            cursor.close()
            
            return OrderInfo(
                order_id=row[1],
                status=row[4],
                payment_status=row[5],
                tracking_number=row[6],
                shipping_carrier=row[7],
                estimated_delivery_date=row[8].isoformat() if row[8] else None,
                actual_delivery_date=row[9].isoformat() if row[9] else None,
                total_amount=float(row[10]),
                currency=row[11],
                items=row[12] if row[12] else [],
                shipping_address=row[13] if row[13] else {},
                tracking_history=tracking_history,
                payment_history=payment_history,
                created_at=row[14].isoformat() if row[14] else None,
                updated_at=row[15].isoformat() if row[15] else None
            )
            
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error obteniendo pedido desde BD: {e}", exc_info=True)
            return None
    
    def _get_mock_order(self, order_id: str) -> OrderInfo:
        """Genera un pedido simulado para pruebas"""
        return OrderInfo(
            order_id=order_id,
            status="in_transit",
            payment_status="paid",
            tracking_number="TRACK123456789",
            shipping_carrier="FedEx",
            estimated_delivery_date=(datetime.now() + timedelta(days=2)).isoformat(),
            actual_delivery_date=None,
            total_amount=99.99,
            currency="USD",
            items=[{"name": "Producto Ejemplo", "quantity": 1, "price": 99.99}],
            shipping_address={"city": "Ciudad Ejemplo", "state": "Estado", "zip": "12345"},
            tracking_history=[
                {
                    "status": "shipped",
                    "location": "Centro de distribución",
                    "carrier_status": "In Transit",
                    "carrier_message": "En camino al destino",
                    "timestamp": (datetime.now() - timedelta(hours=12)).isoformat()
                }
            ],
            payment_history=[
                {
                    "payment_status": "paid",
                    "amount": 99.99,
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
                }
            ],
            created_at=(datetime.now() - timedelta(days=1)).isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analiza el sentimiento del mensaje"""
        message_lower = message.lower()
        
        positive_count = sum(1 for kw in self.sentiment_keywords['positive'] if kw in message_lower)
        negative_count = sum(1 for kw in self.sentiment_keywords['negative'] if kw in message_lower)
        
        if positive_count > negative_count:
            self.metrics.sentiment_positive += 1
            return 'positive'
        elif negative_count > positive_count:
            self.metrics.sentiment_negative += 1
            return 'negative'
        else:
            self.metrics.sentiment_neutral += 1
            return 'neutral'
    
    def _detect_intent(self, message: str, order_id: Optional[str] = None) -> Tuple[IntentType, float]:
        """
        Detecta la intención del mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            order_id: ID del pedido si se detectó
            
        Returns:
            Tupla (intención, confianza)
        """
        message_lower = message.lower()
        
        # Patrones de intención
        intent_patterns = {
            IntentType.TRACK_ORDER: [
                r'dónde está', r'donde esta', r'ubicación', r'localización',
                r'rastrear', r'rastreo', r'tracking', r'seguimiento',
                r'estado.*pedido', r'estado.*orden', r'status.*order'
            ],
            IntentType.PAYMENT_STATUS: [
                r'pago', r'pagado', r'factura', r'cobro', r'payment',
                r'tarjeta', r'transacción', r'transaccion', r'facturado'
            ],
            IntentType.DELIVERY_DATE: [
                r'cuándo llega', r'cuando llega', r'fecha.*entrega',
                r'cuándo.*recibo', r'cuando.*recibo', r'delivery.*date',
                r'llegará', r'llegara', r'estimado'
            ],
            IntentType.CANCEL_ORDER: [
                r'cancelar', r'cancelación', r'cancelacion', r'anular',
                r'eliminar.*pedido', r'eliminar.*orden'
            ],
            IntentType.REFUND: [
                r'reembolso', r'refund', r'devolución', r'devolucion',
                r'devolver.*dinero', r'retorno.*pago'
            ],
            IntentType.CHANGE_ADDRESS: [
                r'cambiar.*dirección', r'cambiar.*direccion', r'cambiar.*envío',
                r'cambiar.*envio', r'modificar.*dirección', r'modificar.*direccion'
            ],
            IntentType.CONTACT_SUPPORT: [
                r'hablar.*humano', r'hablar.*agente', r'hablar.*persona',
                r'soporte.*humano', r'agente.*humano', r'escalar',
                r'problema.*complejo', r'no.*entiendo', r'ayuda.*urgente'
            ],
            IntentType.ORDER_DETAILS: [
                r'detalles.*pedido', r'detalles.*orden', r'qué.*pedido',
                r'que.*pedido', r'qué.*compré', r'que.*compre',
                r'items', r'productos.*pedido'
            ],
            IntentType.SHIPPING_INFO: [
                r'envío', r'envio', r'shipping', r'transporte',
                r'carrier', r'empresa.*envío', r'empresa.*envio'
            ]
        }
        
        scores = {}
        for intent, patterns in intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, message_lower))
            if score > 0:
                scores[intent] = min(score / len(patterns) * 2, 1.0)
        
        # Si hay un order_id pero no se detectó intención específica, asumir track_order
        if order_id and not scores:
            return IntentType.TRACK_ORDER, 0.8
        
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        
        return IntentType.OTHER, 0.3
    
    def _format_order_status(self, status: str) -> str:
        """Formatea el estado del pedido en español"""
        status_map = {
            'pending': 'Pendiente',
            'confirmed': 'Confirmado',
            'processing': 'En proceso',
            'shipped': 'Enviado',
            'in_transit': 'En tránsito',
            'out_for_delivery': 'En camino para entrega',
            'delivered': 'Entregado',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado'
        }
        return status_map.get(status, status)
    
    def _format_payment_status(self, status: str) -> str:
        """Formatea el estado del pago en español"""
        status_map = {
            'pending': 'Pendiente',
            'paid': 'Pagado',
            'failed': 'Fallido',
            'refunded': 'Reembolsado',
            'partially_refunded': 'Parcialmente reembolsado'
        }
        return status_map.get(status, status)
    
    def _generate_tracking_response(self, order_info: OrderInfo, include_items: bool = False) -> str:
        """Genera una respuesta amigable sobre el estado del pedido"""
        status_es = self._format_order_status(order_info.status)
        payment_es = self._format_payment_status(order_info.payment_status)
        
        response = f"¡Hola! Te ayudo con tu pedido {order_info.order_id}. 😊\n\n"
        response += f"📦 **Estado actual:** {status_es}\n"
        response += f"💳 **Pago:** {payment_es}\n"
        response += f"💰 **Total:** {order_info.total_amount:.2f} {order_info.currency}\n"
        
        # Agregar items si se solicita
        if include_items and order_info.items:
            response += f"\n📋 **Productos:**\n"
            for item in order_info.items[:5]:  # Máximo 5 items
                item_name = item.get('name', 'Producto')
                quantity = item.get('quantity', 1)
                response += f"  • {item_name} (x{quantity})\n"
        
        response += "\n"
        
        if order_info.tracking_number:
            response += f"📮 **Número de seguimiento:** {order_info.tracking_number}\n"
            if order_info.shipping_carrier:
                response += f"🚚 **Transportista:** {order_info.shipping_carrier}\n"
        
        if order_info.estimated_delivery_date:
            delivery_date = datetime.fromisoformat(order_info.estimated_delivery_date.replace('Z', '+00:00'))
            response += f"📅 **Fecha estimada de entrega:** {delivery_date.strftime('%d/%m/%Y')}\n"
        
        if order_info.tracking_history:
            latest_update = order_info.tracking_history[0]
            if latest_update.get('carrier_message'):
                response += f"\n📍 **Última actualización:** {latest_update['carrier_message']}\n"
            if latest_update.get('location'):
                response += f"🌍 **Ubicación:** {latest_update['location']}\n"
        
        if order_info.status == 'delivered' and order_info.actual_delivery_date:
            delivery_date = datetime.fromisoformat(order_info.actual_delivery_date.replace('Z', '+00:00'))
            response += f"\n✅ **Entregado el:** {delivery_date.strftime('%d/%m/%Y')}\n"
        
        response += f"\n¿Hay algo más en lo que pueda ayudarte sobre tu pedido?"
        
        return response
    
    def _generate_payment_response(self, order_info: OrderInfo) -> str:
        """Genera una respuesta sobre el estado del pago"""
        payment_es = self._format_payment_status(order_info.payment_status)
        
        response = f"💳 **Estado del pago para pedido {order_info.order_id}:**\n\n"
        response += f"Estado: {payment_es}\n"
        response += f"Monto: {order_info.total_amount:.2f} {order_info.currency}\n"
        
        if order_info.payment_history:
            latest_payment = order_info.payment_history[0]
            if latest_payment.get('timestamp'):
                payment_date = datetime.fromisoformat(latest_payment['timestamp'].replace('Z', '+00:00'))
                response += f"Fecha: {payment_date.strftime('%d/%m/%Y %H:%M')}\n"
            if latest_payment.get('transaction_id'):
                response += f"ID de transacción: {latest_payment['transaction_id']}\n"
        
        if order_info.payment_status == 'paid':
            response += "\n✅ Tu pago ha sido procesado correctamente."
        elif order_info.payment_status == 'pending':
            response += "\n⏳ Tu pago está pendiente de procesamiento."
        elif order_info.payment_status == 'failed':
            response += "\n❌ Hubo un problema con el pago. Te recomiendo contactar a nuestro equipo de soporte."
        
        return response
    
    def _detect_problems(self, order_info: OrderInfo, message: str = "") -> List[ProblemDetection]:
        """
        Detecta problemas potenciales en un pedido.
        
        Args:
            order_info: Información del pedido
            message: Mensaje del usuario (opcional)
            
        Returns:
            Lista de problemas detectados
        """
        problems = []
        
        # Verificar retraso en entrega
        delay_problem = self._check_delivery_delay(order_info)
        if delay_problem:
            problems.append(delay_problem)
        
        # Verificar problemas de pago
        payment_problem = self._check_payment_issue(order_info)
        if payment_problem:
            problems.append(payment_problem)
        
        # Verificar problemas de dirección
        if message:
            address_problem = self._check_address_issue(order_info, message)
            if address_problem:
                problems.append(address_problem)
        
        # Verificar pedido cancelado
        if order_info.status == 'cancelled':
            problems.append(ProblemDetection(
                problem_type='cancelled_order',
                severity='high',
                description='El pedido ha sido cancelado',
                suggested_action='Contactar soporte para más información sobre la cancelación',
                confidence=1.0
            ))
        
        return problems
    
    def _check_delivery_delay(self, order_info: OrderInfo) -> Optional[ProblemDetection]:
        """Verifica si hay retraso en la entrega"""
        if not order_info.estimated_delivery_date:
            return None
        
        try:
            estimated = datetime.fromisoformat(order_info.estimated_delivery_date.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Si la fecha estimada pasó y no está entregado
            if estimated < now and order_info.status != 'delivered':
                days_delayed = (now - estimated).days
                
                if days_delayed > 7:
                    severity = 'critical'
                elif days_delayed > 3:
                    severity = 'high'
                elif days_delayed > 1:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                return ProblemDetection(
                    problem_type='delayed_delivery',
                    severity=severity,
                    description=f'El pedido tiene {days_delayed} día(s) de retraso',
                    suggested_action='Contactaremos al carrier para obtener una actualización. Te notificaremos cuando tengamos información.',
                    confidence=0.9
                )
        except Exception:
            pass
        
        return None
    
    def _check_payment_issue(self, order_info: OrderInfo) -> Optional[ProblemDetection]:
        """Verifica problemas de pago"""
        if order_info.payment_status == 'failed':
            return ProblemDetection(
                problem_type='payment_failed',
                severity='high',
                description='El pago del pedido falló',
                suggested_action='Por favor, verifica tu método de pago o contacta a tu banco. Puedes intentar realizar el pago nuevamente.',
                confidence=1.0
            )
        
        if order_info.payment_status == 'pending':
            # Verificar si el pago está pendiente por mucho tiempo
            try:
                created = datetime.fromisoformat(order_info.created_at.replace('Z', '+00:00'))
                now = datetime.now()
                hours_pending = (now - created).total_seconds() / 3600
                
                if hours_pending > 48:
                    return ProblemDetection(
                        problem_type='payment_pending_too_long',
                        severity='medium',
                        description='El pago está pendiente por más de 48 horas',
                        suggested_action='Verifica el estado del pago con tu banco o método de pago utilizado.',
                        confidence=0.7
                    )
            except Exception:
                pass
        
        return None
    
    def _check_address_issue(self, order_info: OrderInfo, message: str) -> Optional[ProblemDetection]:
        """Verifica problemas relacionados con la dirección"""
        message_lower = message.lower()
        
        address_keywords = ['dirección incorrecta', 'direccion incorrecta', 'dirección equivocada', 
                           'cambiar dirección', 'dirección mal', 'envío incorrecto']
        
        if any(kw in message_lower for kw in address_keywords):
            return ProblemDetection(
                problem_type='wrong_address',
                severity='high',
                description='Problema reportado con la dirección de envío',
                suggested_action='Para cambiar la dirección, necesitamos contactarte. Te escalaremos a un agente humano.',
                confidence=0.8
            )
        
        return None
    
    def _predict_future_problems(self, order_info: OrderInfo) -> List[ProblemPrediction]:
        """
        Predice problemas futuros basándose en patrones históricos.
        
        Args:
            order_info: Información del pedido
            
        Returns:
            Lista de predicciones de problemas
        """
        predictions = []
        
        # Predicción de retraso basada en historial del carrier
        if order_info.shipping_carrier and order_info.estimated_delivery_date:
            try:
                estimated = datetime.fromisoformat(order_info.estimated_delivery_date.replace('Z', '+00:00'))
                now = datetime.now()
                days_until = (estimated - now).days
                
                # Si está cerca de la fecha y aún no está en tránsito avanzado
                if days_until <= 2 and order_info.status not in ['out_for_delivery', 'delivered']:
                    # Calcular probabilidad basada en estado actual
                    if order_info.status == 'pending':
                        probability = 0.6
                    elif order_info.status == 'processing':
                        probability = 0.4
                    elif order_info.status == 'shipped':
                        probability = 0.2
                    else:
                        probability = 0.1
                    
                    if probability > 0.3:
                        predictions.append(ProblemPrediction(
                            problem_type='potential_delay',
                            probability=probability,
                            estimated_time=f"En los próximos {days_until} días",
                            risk_factors=[
                                f"Estado actual: {order_info.status}",
                                f"Días hasta entrega: {days_until}"
                            ],
                            preventive_actions=[
                                "Monitorear actualizaciones del carrier",
                                "Contactar al carrier si no hay actualizaciones en 24h"
                            ],
                            confidence=0.7
                        ))
            except Exception:
                pass
        
        # Predicción de problemas de pago si está pendiente
        if order_info.payment_status == 'pending':
            try:
                created = datetime.fromisoformat(order_info.created_at.replace('Z', '+00:00'))
                now = datetime.now()
                hours_pending = (now - created).total_seconds() / 3600
                
                if hours_pending > 24:
                    probability = min(0.3 + (hours_pending - 24) / 100, 0.8)
                    
                    predictions.append(ProblemPrediction(
                        problem_type='payment_may_fail',
                        probability=probability,
                        estimated_time="En las próximas 24 horas",
                        risk_factors=[
                            f"Pago pendiente por {int(hours_pending)} horas",
                            "Sin confirmación del banco"
                        ],
                        preventive_actions=[
                            "Verificar estado del pago con el banco",
                            "Contactar al cliente si persiste"
                        ],
                        confidence=0.6
                    ))
            except Exception:
                pass
        
        return predictions
    
    def _learn_user_pattern(self, customer_email: Optional[str], intent: str, confidence: float, escalated: bool):
        """Aprende patrones del usuario para personalizar respuestas"""
        if not customer_email:
            return
        
        if customer_email not in self.user_patterns:
            self.user_patterns[customer_email] = UserPattern(
                customer_email=customer_email,
                common_intents=[],
                average_confidence=0.0,
                escalation_rate=0.0,
                preferred_response_style='friendly',
                common_problems=[]
            )
        
        pattern = self.user_patterns[customer_email]
        
        # Actualizar intenciones comunes
        if intent not in pattern.common_intents:
            pattern.common_intents.append(intent)
        if len(pattern.common_intents) > 5:
            pattern.common_intents.pop(0)
        
        # Actualizar confianza promedio
        total_conversations = len(self.conversation_history.get(customer_email, []))
        pattern.average_confidence = (
            (pattern.average_confidence * total_conversations + confidence) /
            (total_conversations + 1)
        )
        
        # Actualizar tasa de escalación
        escalations = sum(1 for conv in self.conversation_history.get(customer_email, []) 
                         if conv.get('escalated', False))
        pattern.escalation_rate = escalations / max(total_conversations, 1)
    
    def _get_personalized_response_style(self, customer_email: Optional[str]) -> str:
        """Obtiene el estilo de respuesta preferido del usuario"""
        if not customer_email or customer_email not in self.user_patterns:
            return 'friendly'
        
        pattern = self.user_patterns[customer_email]
        
        # Si tiene alta tasa de escalación, usar estilo más directo
        if pattern.escalation_rate > 0.5:
            return 'direct'
        
        # Si tiene alta confianza promedio, usar estilo breve
        if pattern.average_confidence > 0.8:
            return 'brief'
        
        return pattern.preferred_response_style
    
    def _enhance_response_with_llm(
        self,
        base_response: str,
        order_info: Optional[OrderInfo],
        intent: IntentType,
        problems: List[ProblemDetection],
        customer_email: Optional[str]
    ) -> str:
        """
        Mejora la respuesta usando LLM para hacerla más natural y contextual.
        
        Args:
            base_response: Respuesta base generada
            order_info: Información del pedido
            intent: Intención detectada
            problems: Problemas detectados
            customer_email: Email del cliente
            
        Returns:
            Respuesta mejorada o la original si LLM no está disponible
        """
        if not self.enable_llm:
            return base_response
        
        try:
            # Construir contexto para el LLM
            context = f"Eres {self.bot_name}, asistente de rastreo de pedidos para {self.company_name}.\n\n"
            context += "Tu tono debe ser amigable y confiado, alineado con la voz de la marca.\n\n"
            
            if order_info:
                context += f"Información del pedido:\n"
                context += f"- ID: {order_info.order_id}\n"
                context += f"- Estado: {self._format_order_status(order_info.status)}\n"
                context += f"- Pago: {self._format_payment_status(order_info.payment_status)}\n"
                if order_info.tracking_number:
                    context += f"- Tracking: {order_info.tracking_number}\n"
                if order_info.estimated_delivery_date:
                    context += f"- Entrega estimada: {order_info.estimated_delivery_date}\n"
            
            if problems:
                context += f"\nProblemas detectados:\n"
                for p in problems[:2]:  # Máximo 2 problemas
                    context += f"- {p.description}\n"
            
            context += f"\nIntención del usuario: {intent.value}\n"
            context += f"\nRespuesta base generada:\n{base_response}\n\n"
            context += "Mejora esta respuesta para que sea más natural, amigable y contextual, "
            context += "manteniendo toda la información importante pero haciéndola más conversacional."
            
            # Llamar a OpenAI
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": "Mejora la respuesta manteniendo el tono amigable y confiado."}
            ]
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.openai_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                enhanced = data["choices"][0]["message"]["content"].strip()
                
                # Validar que la respuesta mejorada tiene sentido
                if len(enhanced) > 50 and len(enhanced) < 1000:
                    if self.enable_logging:
                        self.logger.debug("Respuesta mejorada con LLM")
                    return enhanced
            
        except Exception as e:
            if self.enable_logging:
                self.logger.warning(f"Error mejorando respuesta con LLM: {e}")
        
        return base_response
    
    def add_feedback(
        self,
        order_id: str,
        feedback_type: str,  # 'positive', 'negative', 'helpful', 'not_helpful'
        comment: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> bool:
        """
        Agrega feedback sobre una respuesta del chatbot.
        
        Args:
            order_id: ID del pedido relacionado
            feedback_type: Tipo de feedback
            comment: Comentario opcional
            customer_email: Email del cliente
            
        Returns:
            True si se guardó correctamente
        """
        try:
            feedback = {
                'order_id': order_id,
                'feedback_type': feedback_type,
                'comment': comment,
                'customer_email': customer_email,
                'timestamp': datetime.now().isoformat()
            }
            
            self.feedback_history[order_id].append(feedback)
            
            # Mantener solo últimos 10 feedbacks por pedido
            if len(self.feedback_history[order_id]) > 10:
                self.feedback_history[order_id].pop(0)
            
            if self.enable_logging:
                self.logger.info(f"Feedback recibido: {feedback_type} para pedido {order_id}")
            
            return True
            
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error guardando feedback: {e}", exc_info=True)
            return False
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Carga traducciones básicas"""
        return {
            'es': {
                'greeting': '¡Hola! Soy {bot_name}, tu asistente de rastreo de pedidos.',
                'order_not_found': 'No pude encontrar el pedido {order_id}.',
                'order_status': 'Estado: {status}',
                'payment_status': 'Pago: {status}',
                'delivery_date': 'Entrega estimada: {date}',
                'escalating': 'Te conectaré con un agente humano.',
                'thanks': '¡Gracias por contactarnos!'
            },
            'en': {
                'greeting': 'Hello! I\'m {bot_name}, your order tracking assistant.',
                'order_not_found': 'I couldn\'t find order {order_id}.',
                'order_status': 'Status: {status}',
                'payment_status': 'Payment: {status}',
                'delivery_date': 'Estimated delivery: {date}',
                'escalating': 'I\'ll connect you with a human agent.',
                'thanks': 'Thank you for contacting us!'
            },
            'pt': {
                'greeting': 'Olá! Sou {bot_name}, seu assistente de rastreamento de pedidos.',
                'order_not_found': 'Não consegui encontrar o pedido {order_id}.',
                'order_status': 'Status: {status}',
                'payment_status': 'Pagamento: {status}',
                'delivery_date': 'Entrega estimada: {date}',
                'escalating': 'Vou conectá-lo com um agente humano.',
                'thanks': 'Obrigado por entrar em contato!'
            },
            'fr': {
                'greeting': 'Bonjour! Je suis {bot_name}, votre assistant de suivi de commandes.',
                'order_not_found': 'Je n\'ai pas pu trouver la commande {order_id}.',
                'order_status': 'Statut: {status}',
                'payment_status': 'Paiement: {status}',
                'delivery_date': 'Livraison estimée: {date}',
                'escalating': 'Je vais vous connecter avec un agent humain.',
                'thanks': 'Merci de nous avoir contactés!'
            }
        }
    
    def _translate(self, key: str, **kwargs) -> str:
        """Traduce una clave al idioma actual"""
        lang = self.current_language
        if lang not in self.translations:
            lang = 'es'  # Fallback a español
        
        translation = self.translations.get(lang, {}).get(key, key)
        
        # Interpolar variables
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass
        
        return translation
    
    def detect_language(self, message: str) -> str:
        """Detecta el idioma del mensaje"""
        # Detección básica por palabras comunes
        message_lower = message.lower()
        
        # Palabras clave por idioma
        language_indicators = {
            'en': ['hello', 'hi', 'where', 'order', 'track', 'status', 'thank'],
            'pt': ['olá', 'oi', 'onde', 'pedido', 'rastrear', 'status', 'obrigado'],
            'fr': ['bonjour', 'salut', 'où', 'commande', 'suivre', 'statut', 'merci'],
            'es': ['hola', 'dónde', 'pedido', 'rastrear', 'estado', 'gracias']
        }
        
        scores = {}
        for lang, keywords in language_indicators.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            scores[lang] = score
        
        if scores:
            detected = max(scores.items(), key=lambda x: x[1])[0]
            if scores[detected] > 0:
                return detected
        
        return self.current_language  # Default
    
    def set_language(self, language: str):
        """Establece el idioma del chatbot"""
        if language in self.supported_languages:
            self.current_language = language
            if self.enable_logging:
                self.logger.info(f"Idioma cambiado a: {self.supported_languages[language]}")
    
    def analyze_trends(self, days: int = 7) -> Dict:
        """
        Analiza tendencias de consultas.
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con análisis de tendencias
        """
        now = datetime.now()
        
        # Analizar problemas comunes
        problem_counts = defaultdict(int)
        for problems_list in self.trend_analysis['common_problems'].values():
            for problem in problems_list:
                problem_counts[problem] += 1
        
        # Analizar horas pico
        hour_counts = self.trend_analysis['peak_hours']
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else None
        
        return {
            'period_days': days,
            'total_queries': sum(self.trend_analysis['daily_queries'].values()),
            'average_daily_queries': (
                sum(self.trend_analysis['daily_queries'].values()) / days
                if days > 0 else 0
            ),
            'most_common_problems': dict(sorted(
                problem_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            'peak_hour': peak_hour,
            'hourly_distribution': dict(hour_counts)
        }
    
    def check_proactive_alerts(self) -> List[Dict]:
        """
        Verifica condiciones para alertas proactivas.
        
        Returns:
            Lista de alertas que deben enviarse
        """
        alerts = []
        
        if not self.proactive_alerts_enabled:
            return alerts
        
        try:
            # Verificar pedidos retrasados
            if self.db_connection:
                cursor = self.db_connection.cursor()
                
                # Pedidos retrasados
                delayed_query = """
                    SELECT order_id, customer_email, estimated_delivery_date, status
                    FROM ecommerce_orders
                    WHERE status != 'delivered'
                    AND estimated_delivery_date < CURRENT_DATE - INTERVAL '%s days'
                    AND estimated_delivery_date IS NOT NULL
                """
                cursor.execute(delayed_query, (self.alert_thresholds['delayed_orders'],))
                delayed_orders = cursor.fetchall()
                
                for order in delayed_orders:
                    alerts.append({
                        'type': 'delayed_order',
                        'order_id': order[0],
                        'customer_email': order[1],
                        'severity': 'high',
                        'message': f'Pedido {order[0]} tiene más de {self.alert_thresholds["delayed_orders"]} días de retraso'
                    })
                
                # Pagos pendientes
                pending_payment_query = """
                    SELECT order_id, customer_email, created_at
                    FROM ecommerce_orders
                    WHERE payment_status = 'pending'
                    AND created_at < NOW() - INTERVAL '%s hours'
                """
                cursor.execute(pending_payment_query, (self.alert_thresholds['pending_payments'],))
                pending_payments = cursor.fetchall()
                
                for order in pending_payments:
                    alerts.append({
                        'type': 'pending_payment',
                        'order_id': order[0],
                        'customer_email': order[1],
                        'severity': 'medium',
                        'message': f'Pago del pedido {order[0]} está pendiente por más de {self.alert_thresholds["pending_payments"]} horas'
                    })
                
                cursor.close()
        
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error verificando alertas proactivas: {e}", exc_info=True)
        
        return alerts
    
    def export_data(self, format: str = 'json', include_feedback: bool = True) -> str:
        """
        Exporta datos del chatbot.
        
        Args:
            format: Formato de exportación ('json', 'csv')
            include_feedback: Incluir datos de feedback
            
        Returns:
            Ruta del archivo exportado
        """
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        data = {
            'export_date': datetime.now().isoformat(),
            'metrics': self.get_metrics(),
            'trends': self.analyze_trends(),
            'user_patterns': {
                email: self.get_user_pattern(email)
                for email in self.user_patterns.keys()
            }
        }
        
        if include_feedback:
            data['feedback_stats'] = self.get_feedback_stats()
            data['feedback_history'] = dict(self.feedback_history)
        
        if format == 'json':
            file_path = export_dir / f"chatbot_export_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            # CSV básico (solo métricas principales)
            file_path = export_dir / f"chatbot_export_{timestamp}.csv"
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                metrics = self.get_metrics()
                for key, value in metrics.items():
                    if isinstance(value, (int, float, str)):
                        writer.writerow([key, value])
        
        if self.enable_logging:
            self.logger.info(f"Datos exportados a: {file_path}")
        
        return str(file_path)
    
    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Carga plantillas de respuestas personalizables"""
        return {
            'greeting': {
                'default': '¡Hola! Soy {bot_name}, tu asistente de rastreo de pedidos. ¿En qué puedo ayudarte?',
                'friendly': '¡Hola! 😊 Soy {bot_name} y estoy aquí para ayudarte con tu pedido. ¿Qué necesitas?',
                'professional': 'Buenos días. Soy {bot_name}, asistente de rastreo de pedidos. ¿Cómo puedo asistirte?'
            },
            'order_found': {
                'default': 'Encontré tu pedido {order_id}. Estado: {status}',
                'detailed': '¡Perfecto! Encontré tu pedido {order_id}.\n\n📦 Estado: {status}\n💳 Pago: {payment_status}\n📅 Entrega estimada: {delivery_date}',
                'brief': 'Pedido {order_id}: {status}'
            },
            'escalation': {
                'default': 'Te conectaré con un agente humano que podrá ayudarte mejor.',
                'empathetic': 'Entiendo tu situación. Te conectaré con un agente humano que podrá ayudarte de manera más personalizada.',
                'direct': 'Escalando a soporte humano. Un agente se pondrá en contacto contigo.'
            }
        }
    
    def get_response_template(self, template_type: str, style: str = 'default') -> str:
        """Obtiene una plantilla de respuesta"""
        templates = self.response_templates.get(template_type, {})
        return templates.get(style, templates.get('default', ''))
    
    def create_ab_test(
        self,
        test_id: str,
        test_name: str,
        variants: List[Dict[str, Any]],
        traffic_split: Optional[Dict[str, float]] = None
    ) -> bool:
        """
        Crea un test A/B para probar diferentes respuestas.
        
        Args:
            test_id: ID único del test
            test_name: Nombre del test
            variants: Lista de variantes a probar
            traffic_split: Distribución de tráfico (default: 50/50)
            
        Returns:
            True si se creó correctamente
        """
        if not traffic_split:
            # Distribución equitativa por defecto
            split = 1.0 / len(variants)
            traffic_split = {f"variant_{i}": split for i in range(len(variants))}
        
        self.ab_tests[test_id] = {
            'test_name': test_name,
            'variants': variants,
            'traffic_split': traffic_split,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        if self.enable_logging:
            self.logger.info(f"Test A/B creado: {test_id} - {test_name}")
        
        return True
    
    def get_ab_test_variant(self, test_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una variante para un usuario en un test A/B.
        
        Args:
            test_id: ID del test
            user_id: ID del usuario
            
        Returns:
            Variante asignada o None
        """
        if test_id not in self.ab_tests:
            return None
        
        test = self.ab_tests[test_id]
        if test['status'] != 'active':
            return None
        
        # Asignar variante basado en hash del user_id (consistente)
        import hashlib
        hash_value = int(hashlib.md5(f"{test_id}_{user_id}".encode()).hexdigest(), 16)
        variant_index = hash_value % len(test['variants'])
        
        return test['variants'][variant_index]
    
    def record_ab_result(
        self,
        test_id: str,
        variant_id: str,
        metric: str,
        value: float,
        user_id: Optional[str] = None
    ):
        """Registra un resultado de test A/B"""
        self.ab_results[test_id].append({
            'variant_id': variant_id,
            'metric': metric,
            'value': value,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_ab_test_results(self, test_id: str) -> Dict:
        """Obtiene resultados de un test A/B"""
        if test_id not in self.ab_tests:
            return {"error": "Test no encontrado"}
        
        results = self.ab_results.get(test_id, [])
        
        # Agrupar por variante
        variant_stats = defaultdict(lambda: {'count': 0, 'total': 0, 'metrics': defaultdict(list)})
        
        for result in results:
            variant_id = result['variant_id']
            variant_stats[variant_id]['count'] += 1
            variant_stats[variant_id]['total'] += result['value']
            variant_stats[variant_id]['metrics'][result['metric']].append(result['value'])
        
        # Calcular promedios
        summary = {}
        for variant_id, stats in variant_stats.items():
            summary[variant_id] = {
                'count': stats['count'],
                'average': stats['total'] / stats['count'] if stats['count'] > 0 else 0,
                'metrics': {
                    metric: {
                        'count': len(values),
                        'average': sum(values) / len(values) if values else 0,
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0
                    }
                    for metric, values in stats['metrics'].items()
                }
            }
        
        return {
            'test_id': test_id,
            'test_name': self.ab_tests[test_id]['test_name'],
            'status': self.ab_tests[test_id]['status'],
            'variants': summary,
            'total_results': len(results)
        }
    
    def record_nps_score(
        self,
        order_id: str,
        score: int,  # 0-10
        comment: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> bool:
        """
        Registra un score NPS (Net Promoter Score).
        
        Args:
            order_id: ID del pedido
            score: Score de 0 a 10
            comment: Comentario opcional
            customer_email: Email del cliente
            
        Returns:
            True si se guardó correctamente
        """
        if not (0 <= score <= 10):
            return False
        
        nps_entry = {
            'order_id': order_id,
            'score': score,
            'comment': comment,
            'customer_email': customer_email,
            'timestamp': datetime.now().isoformat(),
            'category': 'promoter' if score >= 9 else ('passive' if score >= 7 else 'detractor')
        }
        
        self.nps_scores.append(nps_entry)
        
        if order_id:
            self.satisfaction_surveys[order_id].append(nps_entry)
        
        if self.enable_logging:
            self.logger.info(f"NPS score registrado: {score} para pedido {order_id}")
        
        return True
    
    def get_nps_analysis(self) -> Dict:
        """Calcula análisis NPS"""
        if not self.nps_scores:
            return {
                'nps': 0,
                'total_responses': 0,
                'promoters': 0,
                'passives': 0,
                'detractors': 0
            }
        
        total = len(self.nps_scores)
        promoters = sum(1 for s in self.nps_scores if s['score'] >= 9)
        passives = sum(1 for s in self.nps_scores if 7 <= s['score'] < 9)
        detractors = sum(1 for s in self.nps_scores if s['score'] < 7)
        
        promoter_percentage = (promoters / total) * 100
        detractor_percentage = (detractors / total) * 100
        nps = promoter_percentage - detractor_percentage
        
        return {
            'nps': round(nps, 2),
            'total_responses': total,
            'promoters': promoters,
            'passives': passives,
            'detractors': detractors,
            'promoter_percentage': round(promoter_percentage, 2),
            'passive_percentage': round((passives / total) * 100, 2),
            'detractor_percentage': round(detractor_percentage, 2),
            'average_score': round(sum(s['score'] for s in self.nps_scores) / total, 2)
        }
    
    def get_dashboard_data(self) -> Dict:
        """
        Genera datos completos para dashboard.
        
        Returns:
            Diccionario con todos los datos del dashboard
        """
        metrics = self.get_metrics()
        trends = self.analyze_trends(7)
        feedback_stats = self.get_feedback_stats()
        nps_analysis = self.get_nps_analysis()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'trends': trends,
            'feedback': feedback_stats,
            'nps': nps_analysis,
            'alerts': {
                'count': len(self.check_proactive_alerts()),
                'enabled': self.proactive_alerts_enabled
            },
            'languages': {
                'current': self.current_language,
                'supported': list(self.supported_languages.keys())
            },
            'ab_tests': {
                'active': len([t for t in self.ab_tests.values() if t['status'] == 'active']),
                'total': len(self.ab_tests)
            },
            'users': {
                'tracked': len(self.user_patterns),
                'total_conversations': sum(len(convs) for convs in self.conversation_history.values())
            }
        }
    
    def calculate_roi(self) -> Dict:
        """
        Calcula el ROI (Return on Investment) del chatbot.
        
        Returns:
            Diccionario con métricas de ROI
        """
        metrics = self.get_metrics()
        total_conversations = metrics.get('total_messages', 0)
        escalations = metrics.get('total_escalations', 0)
        conversations_handled = total_conversations - escalations
        
        # Costos
        chatbot_cost = total_conversations * self.roi_metrics['cost_per_conversation']
        
        # Ahorros estimados (asumiendo que cada conversación resuelta ahorra tiempo humano)
        # Estimación: 5 minutos por conversación resuelta = 0.083 horas
        hours_per_conversation = 0.083
        saved_hours = conversations_handled * hours_per_conversation
        cost_per_hour_human = 25.0  # Costo estimado por hora de agente humano
        saved_cost = saved_hours * cost_per_hour_human
        
        # ROI
        roi_percentage = ((saved_cost - chatbot_cost) / chatbot_cost * 100) if chatbot_cost > 0 else 0
        
        return {
            'total_conversations': total_conversations,
            'conversations_handled': conversations_handled,
            'escalations': escalations,
            'automation_rate': (conversations_handled / total_conversations * 100) if total_conversations > 0 else 0,
            'chatbot_cost': round(chatbot_cost, 2),
            'saved_hours': round(saved_hours, 2),
            'saved_cost': round(saved_cost, 2),
            'net_savings': round(saved_cost - chatbot_cost, 2),
            'roi_percentage': round(roi_percentage, 2),
            'cost_per_conversation': self.roi_metrics['cost_per_conversation']
        }
    
    def generate_auto_report(self, report_type: str = 'daily') -> Dict:
        """
        Genera un reporte automático.
        
        Args:
            report_type: Tipo de reporte ('daily', 'weekly', 'monthly')
            
        Returns:
            Diccionario con el reporte
        """
        now = datetime.now()
        
        if report_type == 'daily':
            days = 1
        elif report_type == 'weekly':
            days = 7
        elif report_type == 'monthly':
            days = 30
        else:
            days = 7
        
        metrics = self.get_metrics()
        trends = self.analyze_trends(days)
        feedback_stats = self.get_feedback_stats()
        nps_analysis = self.get_nps_analysis()
        roi = self.calculate_roi()
        alerts = self.check_proactive_alerts()
        
        report = {
            'report_type': report_type,
            'generated_at': now.isoformat(),
            'period_days': days,
            'summary': {
                'total_conversations': metrics.get('total_messages', 0),
                'automation_rate': roi.get('automation_rate', 0),
                'average_confidence': metrics.get('average_confidence', 0),
                'escalation_rate': metrics.get('escalation_rate', 0),
                'nps_score': nps_analysis.get('nps', 0),
                'positive_feedback_rate': feedback_stats.get('positive_rate', 0)
            },
            'metrics': metrics,
            'trends': trends,
            'feedback': feedback_stats,
            'nps': nps_analysis,
            'roi': roi,
            'alerts': {
                'count': len(alerts),
                'high_priority': len([a for a in alerts if a.get('severity') == 'high'])
            },
            'recommendations': self._generate_recommendations(metrics, trends, feedback_stats, nps_analysis)
        }
        
        # Guardar en historial
        self.report_history.append(report)
        if len(self.report_history) > 100:  # Mantener solo últimos 100 reportes
            self.report_history.pop(0)
        
        return report
    
    def _generate_recommendations(
        self,
        metrics: Dict,
        trends: Dict,
        feedback_stats: Dict,
        nps_analysis: Dict
    ) -> List[str]:
        """Genera recomendaciones basadas en los datos"""
        recommendations = []
        
        # Recomendación basada en tasa de escalación
        escalation_rate = metrics.get('escalation_rate', 0)
        if escalation_rate > 0.3:
            recommendations.append(
                f"Tasa de escalación alta ({escalation_rate:.1%}). "
                "Considera mejorar la detección de intenciones o agregar más respuestas predefinidas."
            )
        
        # Recomendación basada en NPS
        nps = nps_analysis.get('nps', 0)
        if nps < 30:
            recommendations.append(
                f"NPS bajo ({nps}). Revisa los comentarios de detractores y mejora la experiencia del cliente."
            )
        
        # Recomendación basada en problemas comunes
        common_problems = trends.get('most_common_problems', {})
        if common_problems:
            top_problem = max(common_problems.items(), key=lambda x: x[1])
            recommendations.append(
                f"Problema más común: {top_problem[0]} ({top_problem[1]} casos). "
                "Considera crear respuestas proactivas para este problema."
            )
        
        # Recomendación basada en feedback negativo
        negative_rate = 1 - feedback_stats.get('positive_rate', 0)
        if negative_rate > 0.2:
            recommendations.append(
                f"Tasa de feedback negativo alta ({negative_rate:.1%}). "
                "Analiza las respuestas que reciben feedback negativo y optimízalas."
            )
        
        if not recommendations:
            recommendations.append("El sistema está funcionando bien. Continúa monitoreando las métricas.")
        
        return recommendations
    
    def get_feedback_stats(self, order_id: Optional[str] = None) -> Dict:
        """
        Obtiene estadísticas de feedback.
        
        Args:
            order_id: ID del pedido (opcional, si no se proporciona retorna global)
            
        Returns:
            Diccionario con estadísticas
        """
        if order_id:
            feedbacks = self.feedback_history.get(order_id, [])
        else:
            feedbacks = [fb for feedbacks_list in self.feedback_history.values() for fb in feedbacks_list]
        
        if not feedbacks:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "helpful": 0,
                "not_helpful": 0
            }
        
        stats = {
            "total": len(feedbacks),
            "positive": sum(1 for fb in feedbacks if fb['feedback_type'] == 'positive'),
            "negative": sum(1 for fb in feedbacks if fb['feedback_type'] == 'negative'),
            "helpful": sum(1 for fb in feedbacks if fb['feedback_type'] == 'helpful'),
            "not_helpful": sum(1 for fb in feedbacks if fb['feedback_type'] == 'not_helpful')
        }
        
        stats["positive_rate"] = stats["positive"] / stats["total"] if stats["total"] > 0 else 0
        stats["helpful_rate"] = stats["helpful"] / stats["total"] if stats["total"] > 0 else 0
        
        return stats
    
    def _should_escalate(self, intent: IntentType, confidence: float, order_info: Optional[OrderInfo] = None, problems: List[ProblemDetection] = None) -> Tuple[bool, Optional[str]]:
        """
        Determina si se debe escalar a soporte humano.
        
        Returns:
            Tupla (debe_escalar, razón)
        """
        # Escalar si la confianza es muy baja
        if confidence < 0.3:
            return True, "Confianza insuficiente en la intención detectada"
        
        # Escalar para ciertas intenciones complejas
        if intent in [IntentType.CANCEL_ORDER, IntentType.REFUND, IntentType.CHANGE_ADDRESS]:
            return True, f"Consulta compleja que requiere intervención humana: {intent.value}"
        
        # Escalar si hay problemas críticos o de alta severidad
        if problems:
            critical_problems = [p for p in problems if p.severity in ['critical', 'high']]
            if critical_problems:
                return True, f"Problema detectado: {critical_problems[0].problem_type}"
        
        # Escalar si hay problemas con el pedido
        if order_info:
            if order_info.status == 'cancelled' and intent != IntentType.CANCEL_ORDER:
                return True, "Pedido cancelado - requiere atención humana"
            if order_info.payment_status == 'failed':
                return True, "Problema con el pago - requiere atención humana"
        
        return False, None
    
    def process_message(
        self,
        message: str,
        customer_email: Optional[str] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ChatbotResponse:
        """
        Procesa un mensaje del usuario y genera una respuesta.
        
        Args:
            message: Mensaje del usuario
            customer_email: Email del cliente (opcional, para validación)
            conversation_id: ID de conversación (opcional)
            
        Returns:
            Respuesta del chatbot
        """
        start_time = datetime.now()
        
        if self.enable_logging:
            self.logger.info(f"Procesando mensaje: {message[:100]}")
        
        # Rate limiting
        user_identifier = user_id or customer_email or "anonymous"
        if self.enable_rate_limiting and self.rate_limiter:
            allowed, reason = self.rate_limiter.is_allowed(user_identifier)
            if not allowed:
                self.metrics.rate_limit_hits += 1
                if self.enable_logging:
                    self.logger.warning(f"Rate limit excedido para {user_identifier}: {reason}")
                return ChatbotResponse(
                    message=f"Has realizado muchas consultas. {reason}. Por favor, espera un momento antes de continuar.",
                    confidence=1.0,
                    intent=IntentType.OTHER.value,
                    requires_escalation=False
                )
        
        # Análisis de sentimiento
        sentiment = self._analyze_sentiment(message)
        if sentiment == 'negative' and self.enable_logging:
            self.logger.info(f"Sentimiento negativo detectado para usuario {user_identifier}")
        
        # Validar entrada
        if not message or len(message.strip()) == 0:
            return ChatbotResponse(
                message="Por favor, escribe tu consulta sobre tu pedido.",
                confidence=0.0,
                intent=IntentType.OTHER.value,
                requires_escalation=False
            )
        
        if len(message) > 2000:
            message = message[:2000]
        
        # Extraer ID del pedido
        order_id = self._extract_order_id(message)
        
        # Verificar cache
        cached_response = self._get_cached_response(message, order_id)
        if cached_response:
            if self.enable_logging:
                self.logger.debug(f"Respuesta obtenida de cache para mensaje: {message[:50]}")
            return cached_response
        
        # Detectar idioma del mensaje
        detected_lang = self.detect_language(message)
        if detected_lang != self.current_language:
            self.set_language(detected_lang)
        
        # Registrar para análisis de tendencias
        now = datetime.now()
        self.trend_analysis['daily_queries'][now.date()] += 1
        self.trend_analysis['peak_hours'][now.hour] += 1
        
        # Detectar intención
        intent, intent_confidence = self._detect_intent(message, order_id)
        
        # Obtener información del pedido si hay order_id
        order_info = None
        problems = []
        if order_id:
            order_info = self._get_order_from_db(order_id, customer_email)
            if not order_info:
                response_message = (
                    f"No pude encontrar el pedido {order_id}. "
                    f"Por favor, verifica que el ID sea correcto. "
                    f"Si el problema persiste, te conectaré con un agente humano."
                )
                return ChatbotResponse(
                    message=response_message,
                    confidence=0.5,
                    intent=intent.value,
                    requires_escalation=True,
                    escalation_reason="Pedido no encontrado"
                )
            self.metrics.orders_tracked += 1
            
            # Detectar problemas automáticamente
            problems = self._detect_problems(order_info, message)
            
            # Predecir problemas futuros
            if self.enable_predictions:
                future_problems = self._predict_future_problems(order_info)
                # Agregar predicciones de alta probabilidad como advertencias
                high_prob_predictions = [p for p in future_problems if p.probability > 0.5]
                if high_prob_predictions and not problems:
                    # Convertir predicciones de alta probabilidad en problemas detectados
                    for pred in high_prob_predictions:
                        problems.append(ProblemDetection(
                            problem_type=pred.problem_type,
                            severity='medium',
                            description=f"Posible {pred.problem_type.replace('_', ' ')}",
                            suggested_action=pred.preventive_actions[0] if pred.preventive_actions else "Monitorear",
                            confidence=pred.confidence
                        ))
        
        # Aprender patrones del usuario
        self._learn_user_pattern(customer_email, intent.value, intent_confidence, False)
        
        # Generar respuesta según la intención
        response_message = ""
        confidence = intent_confidence
        
        if intent == IntentType.TRACK_ORDER:
            if not order_id:
                response_message = (
                    "Para rastrear tu pedido, necesito el ID del pedido. "
                    "Puedes encontrarlo en el email de confirmación o en tu cuenta. "
                    "Por favor, comparte el ID del pedido (ejemplo: ORD-2024-001234)."
                )
                confidence = 0.6
            elif order_info:
                response_message = self._generate_tracking_response(order_info)
                confidence = 0.9
            else:
                response_message = "No pude encontrar información sobre tu pedido."
                confidence = 0.3
        
        elif intent == IntentType.PAYMENT_STATUS:
            if not order_id:
                response_message = (
                    "Para consultar el estado del pago, necesito el ID del pedido. "
                    "Por favor, comparte el ID del pedido."
                )
                confidence = 0.6
            elif order_info:
                response_message = self._generate_payment_response(order_info)
                confidence = 0.9
                self.metrics.payment_queries += 1
            else:
                response_message = "No pude encontrar información sobre el pago de tu pedido."
                confidence = 0.3
        
        elif intent == IntentType.DELIVERY_DATE:
            if not order_id:
                response_message = (
                    "Para consultar la fecha de entrega, necesito el ID del pedido. "
                    "Por favor, comparte el ID del pedido."
                )
                confidence = 0.6
            elif order_info:
                if order_info.estimated_delivery_date:
                    delivery_date = datetime.fromisoformat(order_info.estimated_delivery_date.replace('Z', '+00:00'))
                    response_message = (
                        f"📅 Tu pedido {order_info.order_id} tiene una fecha estimada de entrega: "
                        f"{delivery_date.strftime('%d/%m/%Y')}.\n\n"
                        f"Estado actual: {self._format_order_status(order_info.status)}\n"
                        f"Te mantendré informado de cualquier actualización."
                    )
                else:
                    response_message = (
                        f"Tu pedido {order_info.order_id} está en estado: "
                        f"{self._format_order_status(order_info.status)}. "
                        f"Aún no tenemos una fecha estimada de entrega, pero te notificaremos cuando esté disponible."
                    )
                confidence = 0.85
            else:
                response_message = "No pude encontrar información sobre la fecha de entrega."
                confidence = 0.3
        
        elif intent == IntentType.ORDER_DETAILS:
            if not order_id:
                response_message = (
                    "Para consultar los detalles del pedido, necesito el ID del pedido. "
                    "Por favor, comparte el ID del pedido."
                )
                confidence = 0.6
            elif order_info:
                response_message = self._generate_tracking_response(order_info, include_items=True)
                response_message += f"\n📅 **Fecha de creación:** {datetime.fromisoformat(order_info.created_at.replace('Z', '+00:00')).strftime('%d/%m/%Y')}\n"
                
                if order_info.shipping_address:
                    addr = order_info.shipping_address
                    if addr.get('city'):
                        response_message += f"📍 **Dirección de envío:** {addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}\n"
                
                confidence = 0.9
            else:
                response_message = "No pude encontrar información sobre los detalles del pedido."
                confidence = 0.3
        
        elif intent == IntentType.CONTACT_SUPPORT:
            response_message = (
                "Por supuesto, te conectaré con un agente de nuestro equipo de soporte "
                "que podrá ayudarte mejor con tu consulta. Un momento, por favor."
            )
            confidence = 0.9
        
        else:
            # Intención no manejada directamente
            if order_info:
                response_message = (
                    f"Entiendo tu consulta sobre el pedido {order_info.order_id}. "
                    f"Para darte la mejor asistencia, te conectaré con un agente humano."
                )
            else:
                response_message = (
                    "Puedo ayudarte con el rastreo de pedidos, consultas sobre pagos y fechas de entrega. "
                    "Si tienes el ID de tu pedido, compártelo y te ayudo. "
                    "Si tu consulta es más compleja, puedo conectarte con un agente humano."
                )
            confidence = 0.5
        
        # Agregar información de problemas a la respuesta si existen
        if problems and order_info:
            problem_messages = []
            for problem in problems:
                if problem.severity in ['critical', 'high']:
                    problem_messages.append(f"\n⚠️ **{problem.description}**\n💡 {problem.suggested_action}")
            
            if problem_messages:
                response_message = response_message.rstrip() + "\n\n" + "\n".join(problem_messages)
        
        # Mejorar respuesta con LLM si está habilitado (solo para respuestas con alta confianza)
        if self.enable_llm and confidence >= 0.7 and response_message:
            try:
                enhanced_response = self._enhance_response_with_llm(
                    response_message,
                    order_info,
                    intent,
                    problems,
                    customer_email
                )
                if enhanced_response and len(enhanced_response) > len(response_message) * 0.5:
                    response_message = enhanced_response
            except Exception as e:
                if self.enable_logging:
                    self.logger.warning(f"Error mejorando respuesta con LLM: {e}")
        
        # Determinar si se debe escalar
        should_escalate, escalation_reason = self._should_escalate(intent, confidence, order_info, problems)
        
        if should_escalate:
            if not response_message.endswith("agente humano") and not response_message.endswith("soporte"):
                response_message += " Te conectaré con un agente humano que podrá ayudarte mejor."
        
        # Actualizar métricas
        self.metrics.total_messages += 1
        self.metrics.intent_counts[intent.value] += 1
        if should_escalate:
            self.metrics.total_escalations += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        self.metrics.average_processing_time = (
            (self.metrics.average_processing_time * (self.metrics.total_messages - 1) + processing_time) /
            self.metrics.total_messages
        )
        self.metrics.average_confidence = (
            (self.metrics.average_confidence * (self.metrics.total_messages - 1) + confidence) /
            self.metrics.total_messages
        )
        
        # Crear respuesta
        response = ChatbotResponse(
            message=response_message,
            confidence=confidence,
            intent=intent.value,
            requires_escalation=should_escalate,
            escalation_reason=escalation_reason,
            order_info=order_info,
            processing_time=processing_time
        )
        
        # Guardar en cache si la confianza es alta
        if response.confidence >= 0.6:
            self._cache_response(message, response, order_id)
        
        # Guardar en historial de conversaciones para aprendizaje
        if customer_email:
            self.conversation_history[customer_email].append({
                'timestamp': datetime.now().isoformat(),
                'intent': intent.value,
                'confidence': confidence,
                'escalated': should_escalate,
                'order_id': order_id,
                'sentiment': sentiment
            })
            # Mantener solo últimas 20 conversaciones
            if len(self.conversation_history[customer_email]) > 20:
                self.conversation_history[customer_email].pop(0)
        
        # Guardar conversación si está habilitado
        if self.persist_conversations:
            self._save_conversation(message, response, conversation_id, customer_email, sentiment)
        
        if self.enable_logging:
            self.logger.info(
                f"Respuesta generada - Intent: {intent.value}, "
                f"Confidence: {confidence:.2f}, Escalation: {should_escalate}, "
                f"Sentiment: {sentiment}"
            )
        
        return response
    
    def _save_conversation(
        self,
        user_message: str,
        response: ChatbotResponse,
        conversation_id: Optional[str],
        customer_email: Optional[str],
        sentiment: str = "neutral"
    ):
        """Guarda la conversación en un archivo JSON"""
        try:
            conv_id = conversation_id or f"conv-{datetime.now().timestamp()}"
            conv_file = self.conversation_dir / f"{conv_id}.json"
            
            conversation_data = {
                "conversation_id": conv_id,
                "timestamp": datetime.now().isoformat(),
                "customer_email": customer_email,
                "user_message": user_message,
                "sentiment": sentiment,
                "response": {
                    "message": response.message,
                    "confidence": response.confidence,
                    "intent": response.intent,
                    "requires_escalation": response.requires_escalation,
                    "escalation_reason": response.escalation_reason,
                    "processing_time": response.processing_time
                },
                "order_info": asdict(response.order_info) if response.order_info else None
            }
            
            # Si el archivo existe, agregar a la conversación
            if conv_file.exists():
                with open(conv_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if "messages" not in existing_data:
                        existing_data["messages"] = []
                    existing_data["messages"].append(conversation_data)
                    conversation_data = existing_data
            
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error guardando conversación: {e}", exc_info=True)
    
    def send_proactive_notification(
        self,
        order_id: str,
        notification_type: str = "status_update",
        customer_email: Optional[str] = None
    ) -> bool:
        """
        Envía una notificación proactiva sobre un pedido.
        
        Args:
            order_id: ID del pedido
            notification_type: Tipo de notificación (status_update, delivery, delay)
            customer_email: Email del cliente (opcional)
            
        Returns:
            True si se envió correctamente
        """
        try:
            order_info = self._get_order_from_db(order_id, customer_email)
            if not order_info:
                return False
            
            if notification_type == "status_update":
                message = self._generate_tracking_response(order_info)
            elif notification_type == "delivery":
                message = (
                    f"✅ ¡Excelente noticia!\n\n"
                    f"Tu pedido {order_id} ha sido entregado.\n\n"
                    f"¡Esperamos que disfrutes tu compra!\n"
                    f"Si tienes alguna pregunta, estamos aquí para ti."
                )
            elif notification_type == "delay":
                message = (
                    f"⏰ Actualización sobre tu pedido {order_id}:\n\n"
                    f"Tu pedido está experimentando un pequeño retraso en la entrega.\n\n"
                    f"Estamos trabajando para que llegue lo antes posible.\n"
                    f"Te mantendremos informado de cualquier actualización."
                )
            else:
                message = self._generate_tracking_response(order_info)
            
            # Aquí podrías integrar con webhook, email, etc.
            if self.enable_logging:
                self.logger.info(f"Notificación proactiva enviada: {notification_type} para {order_id}")
            
            return True
            
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error enviando notificación proactiva: {e}", exc_info=True)
            return False
    
    def get_user_pattern(self, customer_email: str) -> Optional[Dict]:
        """
        Obtiene el patrón de comportamiento de un usuario.
        
        Args:
            customer_email: Email del cliente
            
        Returns:
            Diccionario con el patrón del usuario o None
        """
        if customer_email not in self.user_patterns:
            return None
        
        pattern = self.user_patterns[customer_email]
        return {
            "customer_email": pattern.customer_email,
            "common_intents": pattern.common_intents,
            "average_confidence": pattern.average_confidence,
            "escalation_rate": pattern.escalation_rate,
            "preferred_response_style": pattern.preferred_response_style,
            "common_problems": pattern.common_problems,
            "total_conversations": len(self.conversation_history.get(customer_email, []))
        }
    
    def predict_order_problems(self, order_info: OrderInfo) -> List[Dict]:
        """
        Predice problemas futuros para un pedido.
        
        Args:
            order_info: Información del pedido
            
        Returns:
            Lista de predicciones
        """
        predictions = self._predict_future_problems(order_info)
        return [
            {
                "problem_type": p.problem_type,
                "probability": p.probability,
                "estimated_time": p.estimated_time,
                "risk_factors": p.risk_factors,
                "preventive_actions": p.preventive_actions,
                "confidence": p.confidence
            }
            for p in predictions
        ]
    
    def get_metrics(self) -> Dict:
        """Obtiene las métricas actuales del chatbot"""
        total = self.metrics.total_messages
        return {
            "total_messages": total,
            "total_escalations": self.metrics.total_escalations,
            "escalation_rate": (
                self.metrics.total_escalations / total if total > 0 else 0
            ),
            "intent_distribution": dict(self.metrics.intent_counts),
            "average_confidence": self.metrics.average_confidence,
            "average_processing_time": self.metrics.average_processing_time,
            "orders_tracked": self.metrics.orders_tracked,
            "payment_queries": self.metrics.payment_queries,
            "cache_stats": {
                "hits": self.metrics.cache_hits,
                "misses": self.metrics.cache_misses,
                "hit_rate": (
                    self.metrics.cache_hits / (self.metrics.cache_hits + self.metrics.cache_misses)
                    if (self.metrics.cache_hits + self.metrics.cache_misses) > 0 else 0
                )
            },
            "sentiment_distribution": {
                "positive": self.metrics.sentiment_positive,
                "negative": self.metrics.sentiment_negative,
                "neutral": self.metrics.sentiment_neutral
            },
            "rate_limit_hits": self.metrics.rate_limit_hits,
            "users_tracked": len(self.user_patterns),
            "total_conversations": sum(len(convs) for convs in self.conversation_history.values()),
            "llm_enabled": self.enable_llm,
            "feedback_stats": self.get_feedback_stats(),
            "troubleshooting_enabled": self.troubleshooting_enabled,
            "troubleshooting_sessions_active": len(self.troubleshooting_sessions)
        }
    
    def start_troubleshooting_session(
        self,
        problem_description: str,
        order_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> Optional[TroubleshootingSession]:
        """
        Inicia una sesión de troubleshooting guiado.
        
        Args:
            problem_description: Descripción del problema
            order_id: ID del pedido relacionado (opcional)
            customer_email: Email del cliente
            ticket_id: ID del ticket de soporte (opcional)
            
        Returns:
            Sesión de troubleshooting o None si no se puede iniciar
        """
        if not self.troubleshooting_enabled:
            return None
        
        # Detectar problema
        detected_problem = self._detect_troubleshooting_problem(problem_description, order_id)
        
        # Crear sesión
        session_id = f"troubleshoot-{datetime.now().timestamp()}-{hash(problem_description) % 10000}"
        session = TroubleshootingSession(
            session_id=session_id,
            order_id=order_id,
            customer_email=customer_email or "unknown",
            problem_description=problem_description,
            detected_problem_id=detected_problem.problem_id if detected_problem else None,
            guide=detected_problem,
            current_step=0,
            status='started',
            started_at=datetime.now(),
            completed_steps=[],
            notes=[],
            ticket_id=ticket_id
        )
        
        self.troubleshooting_sessions[session_id] = session
        
        # Guardar en base de datos si está disponible
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                query = """
                    INSERT INTO support_troubleshooting_sessions
                    (session_id, ticket_id, customer_email, problem_description,
                     detected_problem_id, detected_problem_title, status, current_step, total_steps)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                total_steps = len(detected_problem.steps) if detected_problem else 0
                cursor.execute(query, (
                    session_id,
                    ticket_id,
                    customer_email,
                    problem_description,
                    detected_problem.problem_id if detected_problem else None,
                    detected_problem.problem_title if detected_problem else None,
                    'started',
                    0,
                    total_steps
                ))
                self.db_connection.commit()
                cursor.close()
            except Exception as e:
                if self.enable_logging:
                    self.logger.error(f"Error guardando sesión de troubleshooting: {e}")
        
        if self.enable_logging:
            self.logger.info(f"Sesión de troubleshooting iniciada: {session_id}")
        
        return session
    
    def _detect_troubleshooting_problem(
        self,
        problem_description: str,
        order_id: Optional[str] = None
    ) -> Optional[TroubleshootingGuide]:
        """
        Detecta qué problema de troubleshooting corresponde a la descripción.
        
        Args:
            problem_description: Descripción del problema
            order_id: ID del pedido (opcional)
            
        Returns:
            Guía de troubleshooting o None
        """
        problem_lower = problem_description.lower()
        
        # Buscar en guías disponibles
        for problem_id, guide in self.troubleshooting_guides.items():
            # Buscar palabras clave del problema
            keywords = [
                guide.problem_title.lower(),
                guide.problem_id.replace('_', ' '),
                *guide.problem_description.lower().split()[:5]
            ]
            
            # Calcular score de coincidencia
            score = sum(1 for kw in keywords if kw in problem_lower)
            if score > 0:
                # Si hay order_id, obtener información del pedido para contexto
                if order_id:
                    order_info = self._get_order_from_db(order_id)
                    if order_info:
                        # Verificar si el problema coincide con el estado del pedido
                        if problem_id == 'delayed_delivery' and order_info.status != 'delivered':
                            return guide
                        elif problem_id == 'payment_failed' and order_info.payment_status == 'failed':
                            return guide
                        elif problem_id == 'wrong_address':
                            return guide
                
                # Si no hay order_id o no coincide, retornar la guía de todos modos
                return guide
        
        return None
    
    def get_troubleshooting_step(
        self,
        session_id: str,
        step_number: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Obtiene el siguiente paso de troubleshooting o un paso específico.
        
        Args:
            session_id: ID de la sesión
            step_number: Número de paso específico (opcional, si no se proporciona retorna el siguiente)
            
        Returns:
            Diccionario con información del paso o None
        """
        if session_id not in self.troubleshooting_sessions:
            return None
        
        session = self.troubleshooting_sessions[session_id]
        
        if not session.guide:
            return None
        
        # Determinar qué paso mostrar
        if step_number is None:
            step_number = session.current_step + 1
        
        if step_number > len(session.guide.steps):
            return {
                'completed': True,
                'message': 'Todos los pasos han sido completados'
            }
        
        step = session.guide.steps[step_number - 1]
        
        return {
            'session_id': session_id,
            'step_number': step.step_number,
            'title': step.title,
            'description': step.description,
            'instructions': step.instructions,
            'verification_question': step.verification_question,
            'expected_result': step.expected_result,
            'total_steps': len(session.guide.steps),
            'current_step': session.current_step,
            'estimated_time_minutes': session.guide.estimated_time_minutes,
            'auto_resolvable': step.auto_resolvable
        }
    
    def complete_troubleshooting_step(
        self,
        session_id: str,
        step_number: int,
        success: bool,
        notes: Optional[str] = None,
        user_response: Optional[str] = None
    ) -> Dict:
        """
        Completa un paso de troubleshooting.
        
        Args:
            session_id: ID de la sesión
            step_number: Número del paso completado
            success: Si el paso fue exitoso
            notes: Notas adicionales
            user_response: Respuesta del usuario a la pregunta de verificación
            
        Returns:
            Diccionario con resultado y siguiente acción
        """
        if session_id not in self.troubleshooting_sessions:
            return {"error": "Sesión no encontrada"}
        
        session = self.troubleshooting_sessions[session_id]
        
        if not session.guide or step_number > len(session.guide.steps):
            return {"error": "Paso inválido"}
        
        step = session.guide.steps[step_number - 1]
        
        # Registrar paso completado
        completed_step = {
            'step_number': step_number,
            'title': step.title,
            'success': success,
            'notes': notes,
            'user_response': user_response,
            'completed_at': datetime.now().isoformat()
        }
        session.completed_steps.append(completed_step)
        
        # Actualizar estado de la sesión
        if success:
            session.current_step = step_number
            session.status = 'in_progress'
            
            # Verificar si hay más pasos
            if step_number >= len(session.guide.steps):
                # Todos los pasos completados
                session.status = 'resolved'
                session.notes.append(f"Problema resuelto: {session.guide.problem_title}")
                
                # Intentar resolución automática si está disponible
                if step.auto_resolvable and self.auto_resolution_enabled:
                    auto_result = self._attempt_auto_resolution(session, step)
                    if auto_result.get('success'):
                        session.notes.append("Resolución automática aplicada")
        else:
            # Paso fallido
            failed_count = sum(1 for s in session.completed_steps if not s.get('success', True))
            if failed_count >= 2:
                session.status = 'needs_escalation'
                session.notes.append("Múltiples pasos fallidos - requiere escalación")
        
        # Guardar en base de datos
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                
                # Insertar intento
                attempt_query = """
                    INSERT INTO support_troubleshooting_attempts
                    (session_id, step_number, step_title, success, notes, step_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(attempt_query, (
                    session_id,
                    step_number,
                    step.title,
                    success,
                    notes,
                    'diagnostic' if step_number == 1 else 'fix'
                ))
                
                # Actualizar sesión
                update_query = """
                    UPDATE support_troubleshooting_sessions
                    SET status = %s, current_step = %s, updated_at = NOW()
                    WHERE session_id = %s
                """
                cursor.execute(update_query, (session.status, session.current_step, session_id))
                
                self.db_connection.commit()
                cursor.close()
            except Exception as e:
                if self.enable_logging:
                    self.logger.error(f"Error guardando paso de troubleshooting: {e}")
        
        # Determinar siguiente acción
        next_action = 'continue'
        message = "Paso completado. Continuando con el siguiente paso." if success else "El paso no se completó exitosamente."
        
        if session.status == 'resolved':
            next_action = 'resolved'
            message = f"¡Excelente! Has completado todos los pasos. El problema '{session.guide.problem_title}' debería estar resuelto."
        elif session.status == 'needs_escalation':
            next_action = 'escalate'
            message = "Múltiples pasos fallaron. Te conectaré con un agente humano que podrá ayudarte mejor."
        
        return {
            'success': True,
            'session_id': session_id,
            'step_completed': completed_step,
            'next_action': next_action,
            'message': message,
            'session_status': session.status,
            'current_step': session.current_step,
            'total_steps': len(session.guide.steps) if session.guide else 0,
            'suggest_escalation': session.status == 'needs_escalation'
        }
    
    def _attempt_auto_resolution(
        self,
        session: TroubleshootingSession,
        step: TroubleshootingStep
    ) -> Dict:
        """
        Intenta resolver automáticamente un problema.
        
        Args:
            session: Sesión de troubleshooting
            step: Paso que permite resolución automática
            
        Returns:
            Diccionario con resultado de la resolución
        """
        if not session.order_id:
            return {'success': False, 'reason': 'No hay order_id asociado'}
        
        order_info = self._get_order_from_db(session.order_id)
        if not order_info:
            return {'success': False, 'reason': 'Pedido no encontrado'}
        
        # Resolución automática para pago fallido
        if session.detected_problem_id == 'payment_failed':
            # Aquí podrías integrar con un sistema de reintento de pago
            # Por ahora solo retornamos éxito simulado
            return {
                'success': True,
                'action': 'payment_retry_initiated',
                'message': 'Se ha iniciado el proceso de reintento de pago'
            }
        
        return {'success': False, 'reason': 'Auto-resolución no disponible para este problema'}
    
    def get_troubleshooting_session(self, session_id: str) -> Optional[Dict]:
        """
        Obtiene información de una sesión de troubleshooting.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con información de la sesión o None
        """
        if session_id not in self.troubleshooting_sessions:
            return None
        
        session = self.troubleshooting_sessions[session_id]
        
        return {
            'session_id': session.session_id,
            'order_id': session.order_id,
            'customer_email': session.customer_email,
            'problem_description': session.problem_description,
            'detected_problem_id': session.detected_problem_id,
            'problem_title': session.guide.problem_title if session.guide else None,
            'current_step': session.current_step,
            'total_steps': len(session.guide.steps) if session.guide else 0,
            'status': session.status,
            'started_at': session.started_at.isoformat(),
            'completed_steps': session.completed_steps,
            'notes': session.notes,
            'ticket_id': session.ticket_id
        }
    
    def find_similar_problems(
        self,
        problem_description: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Encuentra problemas similares basándose en descripciones anteriores.
        
        Args:
            problem_description: Descripción del problema actual
            limit: Número máximo de resultados
            
        Returns:
            Lista de problemas similares
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT 
                    session_id,
                    problem_description,
                    detected_problem_title,
                    status,
                    resolved_at,
                    customer_satisfaction_score
                FROM support_troubleshooting_sessions
                WHERE to_tsvector('english', problem_description) @@ 
                      plainto_tsquery('english', %s)
                AND status = 'resolved'
                ORDER BY resolved_at DESC
                LIMIT %s
            """
            cursor.execute(query, (problem_description, limit))
            results = cursor.fetchall()
            cursor.close()
            
            return [
                {
                    'session_id': row[0],
                    'problem_description': row[1],
                    'problem_title': row[2],
                    'status': row[3],
                    'resolved_at': row[4].isoformat() if row[4] else None,
                    'satisfaction_score': row[5]
                }
                for row in results
            ]
        except Exception as e:
            if self.enable_logging:
                self.logger.error(f"Error buscando problemas similares: {e}")
            return []


def main():
    """Función principal para ejecutar el chatbot en modo interactivo"""
    print("=" * 60)
    print("🤖 Chatbot de Rastreo de Pedidos")
    print("=" * 60)
    print("\nEscribe 'salir' para terminar.\n")
    
    chatbot = OrderTrackingChatbot(
        company_name="Mi Empresa",
        bot_name="Asistente de Pedidos"
    )
    
    while True:
        try:
            user_input = input("Tú: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n¡Hasta luego! 👋")
                break
            
            if not user_input:
                continue
            
            response = chatbot.process_message(user_input)
            print(f"\n{chatbot.bot_name}: {response.message}\n")
            
            if response.requires_escalation:
                print("⚠️  Esta consulta será escalada a soporte humano.\n")
        
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    # Mostrar métricas al finalizar
    print("\n" + "=" * 60)
    print("📊 Métricas de la sesión:")
    print("=" * 60)
    metrics = chatbot.get_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

