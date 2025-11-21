"""
Módulo de Chatbot para Soporte - Manejo de FAQs y respuestas automáticas.

Características:
- Búsqueda de FAQs en base de datos
- Integración con LLM (OpenAI) para respuestas contextuales
- Detección de intenciones
- Escalación inteligente cuando no puede resolver
"""
import os
import logging
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
    )
    from requests.exceptions import RequestException, HTTPError
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from .circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
    from .cache import get_cache
    from .metrics import get_metrics_collector
    CIRCUIT_BREAKER_AVAILABLE = True
    CACHE_AVAILABLE = True
    METRICS_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    CACHE_AVAILABLE = False
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constantes
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"


@dataclass
class ChatbotResponse:
    """Respuesta del chatbot."""
    response_text: str
    confidence: float
    faq_matched: bool
    faq_article_id: Optional[str] = None
    intent_detected: Optional[str] = None
    resolved: bool = False
    escalation_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FAQArticle:
    """Artículo de FAQ."""
    article_id: str
    title: str
    content: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class SupportChatbot:
    """Chatbot para manejo de FAQs y soporte automático."""
    
    def __init__(
        self,
        db_connection: Any = None,
        openai_api_key: Optional[str] = None,
        openai_model: str = OPENAI_DEFAULT_MODEL,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        enable_llm: bool = True,
        enable_cache: bool = True,
    ):
        """
        Inicializa el chatbot de soporte.
        
        Args:
            db_connection: Conexión a base de datos para buscar FAQs
            openai_api_key: API key de OpenAI para respuestas con LLM
            openai_model: Modelo de OpenAI a usar
            confidence_threshold: Umbral de confianza para considerar respuesta válida
            enable_llm: Habilitar uso de LLM para respuestas contextuales
            enable_cache: Habilitar cache de respuestas
        """
        self.db_connection = db_connection
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = openai_model
        self.confidence_threshold = confidence_threshold
        self.enable_llm = enable_llm and self.openai_api_key
        self.enable_cache = enable_cache
        
        # Configurar HTTP session
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=DEFAULT_MAX_RETRIES,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST", "GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        
        # Cache si está disponible
        self.cache = None
        if enable_cache and CACHE_AVAILABLE:
            try:
                self.cache = get_cache(ttl=3600)  # 1 hora
            except Exception as e:
                logger.warning(f"No se pudo inicializar cache: {e}")
        
        # Circuit breaker si está disponible
        self.circuit_breaker = None
        if CIRCUIT_BREAKER_AVAILABLE:
            try:
                self.circuit_breaker = get_circuit_breaker(
                    "openai_chatbot",
                    CircuitBreakerConfig(
                        failure_threshold=5,
                        timeout=60,
                        expected_exception=Exception
                    )
                )
            except Exception as e:
                logger.warning(f"No se pudo inicializar circuit breaker: {e}")
        
        # Métricas
        self.metrics = None
        if METRICS_AVAILABLE:
            try:
                self.metrics = get_metrics_collector()
            except Exception as e:
                logger.warning(f"No se pudo inicializar métricas: {e}")
    
    def search_faq(self, query: str, limit: int = 5) -> List[FAQArticle]:
        """
        Busca artículos de FAQ relevantes para la consulta.
        
        Args:
            query: Texto de la consulta del usuario
            limit: Número máximo de resultados
            
        Returns:
            Lista de artículos de FAQ ordenados por relevancia
        """
        if not self.db_connection:
            logger.warning("No hay conexión a BD para buscar FAQs")
            return []
        
        try:
            # Normalizar query
            query_lower = query.lower().strip()
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            
            # Buscar en base de datos
            cursor = self.db_connection.cursor()
            
            # Buscar por keywords y contenido
            sql = """
                SELECT 
                    article_id,
                    title,
                    content,
                    summary,
                    category,
                    tags,
                    keywords
                FROM support_faq_articles
                WHERE is_active = true
                AND (
                    LOWER(content) LIKE %s
                    OR LOWER(title) LIKE %s
                    OR EXISTS (
                        SELECT 1 FROM unnest(keywords) AS kw
                        WHERE LOWER(kw) = ANY(%s)
                    )
                    OR tags && %s
                )
                ORDER BY 
                    CASE 
                        WHEN LOWER(title) LIKE %s THEN 1
                        WHEN EXISTS (
                            SELECT 1 FROM unnest(keywords) AS kw
                            WHERE LOWER(kw) = ANY(%s)
                        ) THEN 2
                        ELSE 3
                    END,
                    view_count DESC
                LIMIT %s
            """
            
            query_pattern = f"%{query_lower}%"
            keywords_array = list(query_words)
            tags_array = keywords_array
            
            cursor.execute(sql, (
                query_pattern,
                query_pattern,
                keywords_array,
                tags_array,
                query_pattern,
                keywords_array,
                limit
            ))
            
            results = []
            for row in cursor.fetchall():
                results.append(FAQArticle(
                    article_id=row[0],
                    title=row[1],
                    content=row[2],
                    summary=row[3],
                    category=row[4],
                    tags=row[5] if row[5] else [],
                    keywords=row[6] if row[6] else []
                ))
            
            cursor.close()
            
            if self.metrics:
                self.metrics.increment(
                    "support_chatbot_faq_search",
                    tags={"results_count": len(results)}
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando FAQs: {e}", exc_info=True)
            if self.metrics:
                self.metrics.increment("support_chatbot_faq_search_error")
            return []
    
    def _call_llm(
        self,
        user_message: str,
        faq_context: Optional[List[FAQArticle]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, float]:
        """
        Llama a OpenAI para generar respuesta contextual.
        
        Args:
            user_message: Mensaje del usuario
            faq_context: Artículos de FAQ relevantes
            conversation_history: Historial de conversación
            
        Returns:
            Tupla (respuesta, confianza)
        """
        if not self.enable_llm:
            return "", 0.0
        
        # Verificar circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.is_open():
            try:
                with self.circuit_breaker:
                    return self._execute_llm_call(user_message, faq_context, conversation_history)
            except Exception as e:
                logger.error(f"Error en llamada LLM (circuit breaker): {e}")
                return "", 0.0
        elif self.circuit_breaker and self.circuit_breaker.is_open():
            logger.warning("Circuit breaker abierto para LLM")
            return "", 0.0
        else:
            return self._execute_llm_call(user_message, faq_context, conversation_history)
    
    def _execute_llm_call(
        self,
        user_message: str,
        faq_context: Optional[List[FAQArticle]],
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> Tuple[str, float]:
        """Ejecuta la llamada a LLM."""
        try:
            # Construir contexto de FAQs
            faq_text = ""
            if faq_context:
                faq_text = "\n\nArtículos de ayuda relevantes:\n"
                for i, faq in enumerate(faq_context[:3], 1):  # Max 3 FAQs como contexto
                    faq_text += f"\n{i}. {faq.title}\n{faq.summary or faq.content[:200]}\n"
            
            # Construir historial
            messages = []
            
            # System prompt
            system_prompt = """Eres un asistente de soporte al cliente experto y útil. 
Tu objetivo es resolver las consultas de los clientes de manera clara, concisa y amigable.
Si tienes información relevante en los artículos de ayuda, úsala para responder.
Si no puedes resolver la consulta con certeza, indica que escalarás a un agente humano.
Responde en el mismo idioma que el usuario."""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Agregar historial
            if conversation_history:
                for msg in conversation_history[-5:]:  # Últimas 5 interacciones
                    messages.append(msg)
            
            # Agregar contexto de FAQs
            if faq_text:
                messages.append({
                    "role": "system",
                    "content": f"Contexto adicional:{faq_text}"
                })
            
            # Mensaje del usuario
            messages.append({"role": "user", "content": user_message})
            
            # Llamar a OpenAI
            url = f"{OPENAI_BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.openai_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 1.0,
            }
            
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]
            
            # Calcular confianza (simplificado: basado en si hay respuesta)
            confidence = 0.8 if assistant_message and len(assistant_message) > 20 else 0.5
            
            if self.metrics:
                self.metrics.increment(
                    "support_chatbot_llm_calls",
                    tags={"model": self.openai_model}
                )
                self.metrics.histogram(
                    "support_chatbot_llm_tokens",
                    data.get("usage", {}).get("total_tokens", 0)
                )
            
            return assistant_message, confidence
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}", exc_info=True)
            if self.metrics:
                self.metrics.increment("support_chatbot_llm_error")
            return "", 0.0
    
    def detect_intent(self, message: str) -> Tuple[Optional[str], float]:
        """
        Detecta la intención del mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Tupla (intención, confianza)
        """
        message_lower = message.lower()
        
        # Intenciones comunes
        intents = {
            "billing": ["pago", "factura", "cobro", "tarjeta", "refund", "reembolso", "precio", "costo"],
            "technical": ["error", "no funciona", "bug", "problema", "falla", "no carga", "lento"],
            "account": ["cuenta", "login", "contraseña", "password", "acceso", "registro"],
            "feature": ["cómo", "funciona", "característica", "feature", "capacidad"],
            "cancellation": ["cancelar", "dar de baja", "eliminar cuenta", "cerrar"],
            "general": ["información", "ayuda", "soporte", "duda"]
        }
        
        scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score / len(keywords)
        
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1] * 0.8, 1.0)
        
        return "general", 0.5
    
    def process_message(
        self,
        user_message: str,
        ticket_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> ChatbotResponse:
        """
        Procesa un mensaje del usuario y genera una respuesta.
        
        Args:
            user_message: Mensaje del usuario
            ticket_id: ID del ticket (opcional)
            conversation_history: Historial de conversación
            
        Returns:
            Respuesta del chatbot
        """
        start_time = datetime.now()
        
        # Verificar cache
        cache_key = None
        if self.cache and ticket_id:
            cache_key = f"chatbot_response:{ticket_id}:{hash(user_message)}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Respuesta obtenida de cache para ticket {ticket_id}")
                if self.metrics:
                    self.metrics.increment("support_chatbot_cache_hit")
                return ChatbotResponse(**cached)
        
        # Detectar intención
        intent, intent_confidence = self.detect_intent(user_message)
        
        # Buscar FAQs relevantes
        faq_results = self.search_faq(user_message, limit=5)
        faq_matched = len(faq_results) > 0
        
        # Determinar respuesta
        response_text = ""
        confidence = 0.0
        faq_article_id = None
        resolved = False
        escalation_reason = None
        
        if faq_results and len(faq_results) > 0:
            # Si hay FAQ muy relevante, usarla directamente
            best_faq = faq_results[0]
            faq_article_id = best_faq.article_id
            
            # Si el LLM está habilitado, usar para formatear mejor la respuesta
            if self.enable_llm:
                llm_response, llm_confidence = self._call_llm(
                    user_message,
                    faq_context=[best_faq],
                    conversation_history=conversation_history
                )
                if llm_confidence >= self.confidence_threshold:
                    response_text = llm_response
                    confidence = llm_confidence
                else:
                    # Fallback a FAQ directo
                    response_text = best_faq.summary or best_faq.content[:500]
                    confidence = 0.75
            else:
                # Usar FAQ directamente
                response_text = best_faq.summary or best_faq.content[:500]
                confidence = 0.75
            
            resolved = confidence >= self.confidence_threshold
        elif self.enable_llm:
            # Intentar con LLM sin FAQs
            llm_response, llm_confidence = self._call_llm(
                user_message,
                faq_context=None,
                conversation_history=conversation_history
            )
            
            if llm_confidence >= self.confidence_threshold:
                response_text = llm_response
                confidence = llm_confidence
                resolved = True
            else:
                # No se puede resolver, escalar
                escalation_reason = "No se encontró respuesta adecuada en FAQs ni con LLM"
                response_text = "Entiendo tu consulta. Para darte la mejor asistencia, voy a conectarte con un agente de nuestro equipo que podrá ayudarte mejor."
                confidence = 0.3
                resolved = False
        else:
            # Sin LLM ni FAQs, escalar
            escalation_reason = "No se encontraron FAQs relevantes y LLM no está disponible"
            response_text = "Gracias por tu consulta. Te voy a conectar con un agente de nuestro equipo que podrá ayudarte."
            confidence = 0.2
            resolved = False
        
        # Si la confianza es muy baja, escalar
        if confidence < self.confidence_threshold and not escalation_reason:
            escalation_reason = f"Confianza insuficiente ({confidence:.2f})"
        
        # Crear respuesta
        response = ChatbotResponse(
            response_text=response_text,
            confidence=confidence,
            faq_matched=faq_matched,
            faq_article_id=faq_article_id,
            intent_detected=intent,
            resolved=resolved,
            escalation_reason=escalation_reason,
            metadata={
                "intent_confidence": intent_confidence,
                "faq_results_count": len(faq_results),
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        )
        
        # Guardar en cache
        if self.cache and cache_key:
            try:
                self.cache.set(cache_key, {
                    "response_text": response.response_text,
                    "confidence": response.confidence,
                    "faq_matched": response.faq_matched,
                    "faq_article_id": response.faq_article_id,
                    "intent_detected": response.intent_detected,
                    "resolved": response.resolved,
                    "escalation_reason": response.escalation_reason,
                    "metadata": response.metadata
                }, ttl=1800)  # 30 minutos
            except Exception as e:
                logger.warning(f"No se pudo guardar en cache: {e}")
        
        # Métricas
        if self.metrics:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.increment(
                "support_chatbot_requests",
                tags={
                    "resolved": str(resolved).lower(),
                    "faq_matched": str(faq_matched).lower(),
                    "intent": intent
                }
            )
            self.metrics.histogram("support_chatbot_response_time_ms", duration_ms)
            self.metrics.histogram("support_chatbot_confidence", confidence)
        
        return response





