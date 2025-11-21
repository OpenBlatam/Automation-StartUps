"""
Sistema de Resumen Automático con IA.

Genera resúmenes inteligentes de tickets, conversaciones y threads.
"""
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class SummaryType(Enum):
    """Tipos de resumen."""
    SHORT = "short"  # 1-2 oraciones
    MEDIUM = "medium"  # Párrafo corto
    LONG = "long"  # Resumen completo
    BULLET = "bullet"  # Puntos clave
    EXECUTIVE = "executive"  # Resumen ejecutivo


@dataclass
class Summary:
    """Resumen generado."""
    summary_type: SummaryType
    content: str
    key_points: List[str]
    sentiment: Optional[str] = None
    urgency: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None


class AISummarizer:
    """Resumidor con IA."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        """
        Inicializa resumidor.
        
        Args:
            provider: 'openai' o 'anthropic'
            model: Modelo a usar
            api_key: API key (opcional, usa env var si no se proporciona)
        """
        self.provider = provider
        self.model = model
        
        if provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if OPENAI_AVAILABLE and self.api_key:
                openai.api_key = self.api_key
        elif provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if ANTHROPIC_AVAILABLE and self.api_key:
                self.client = Anthropic(api_key=self.api_key)
    
    def summarize_ticket(
        self,
        ticket_data: Dict[str, Any],
        summary_type: SummaryType = SummaryType.MEDIUM
    ) -> Summary:
        """
        Resume un ticket completo.
        
        Args:
            ticket_data: Datos del ticket
            summary_type: Tipo de resumen
            
        Returns:
            Resumen generado
        """
        # Construir contexto
        context = self._build_ticket_context(ticket_data)
        
        # Generar resumen
        summary_text = self._generate_summary(context, summary_type)
        
        # Extraer puntos clave
        key_points = self._extract_key_points(ticket_data)
        
        # Analizar sentimiento y urgencia
        sentiment = self._analyze_sentiment(ticket_data.get("description", ""))
        urgency = ticket_data.get("priority", "normal")
        
        return Summary(
            summary_type=summary_type,
            content=summary_text,
            key_points=key_points,
            sentiment=sentiment,
            urgency=urgency,
            confidence=0.85
        )
    
    def summarize_conversation(
        self,
        messages: List[Dict[str, Any]],
        summary_type: SummaryType = SummaryType.MEDIUM
    ) -> Summary:
        """
        Resume una conversación/thread.
        
        Args:
            messages: Lista de mensajes
            summary_type: Tipo de resumen
            
        Returns:
            Resumen generado
        """
        # Construir contexto de conversación
        context = self._build_conversation_context(messages)
        
        # Generar resumen
        summary_text = self._generate_summary(context, summary_type)
        
        # Extraer puntos clave
        key_points = self._extract_key_points_from_messages(messages)
        
        return Summary(
            summary_type=summary_type,
            content=summary_text,
            key_points=key_points,
            confidence=0.80
        )
    
    def _build_ticket_context(self, ticket_data: Dict[str, Any]) -> str:
        """Construye contexto del ticket."""
        context = f"Título: {ticket_data.get('subject', 'N/A')}\n\n"
        context += f"Descripción: {ticket_data.get('description', 'N/A')}\n\n"
        context += f"Prioridad: {ticket_data.get('priority', 'N/A')}\n"
        context += f"Categoría: {ticket_data.get('category', 'N/A')}\n"
        
        if ticket_data.get("customer_email"):
            context += f"Cliente: {ticket_data['customer_email']}\n"
        
        if ticket_data.get("tags"):
            context += f"Tags: {', '.join(ticket_data['tags'])}\n"
        
        return context
    
    def _build_conversation_context(self, messages: List[Dict[str, Any]]) -> str:
        """Construye contexto de conversación."""
        context = "Conversación:\n\n"
        for i, msg in enumerate(messages, 1):
            sender = msg.get("sender", "Usuario")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            context += f"[{timestamp}] {sender}: {content}\n\n"
        return context
    
    def _generate_summary(self, context: str, summary_type: SummaryType) -> str:
        """Genera resumen usando IA."""
        if self.provider == "openai" and OPENAI_AVAILABLE and self.api_key:
            return self._generate_openai_summary(context, summary_type)
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE and self.api_key:
            return self._generate_anthropic_summary(context, summary_type)
        else:
            # Fallback a resumen simple
            return self._generate_simple_summary(context, summary_type)
    
    def _generate_openai_summary(self, context: str, summary_type: SummaryType) -> str:
        """Genera resumen con OpenAI."""
        try:
            length_prompts = {
                SummaryType.SHORT: "en 1-2 oraciones",
                SummaryType.MEDIUM: "en un párrafo corto",
                SummaryType.LONG: "en un resumen completo de varios párrafos",
                SummaryType.BULLET: "en puntos clave",
                SummaryType.EXECUTIVE: "en un resumen ejecutivo conciso"
            }
            
            prompt = f"""Resume el siguiente contenido {length_prompts.get(summary_type, 'en un párrafo')}.

Contenido:
{context}

Resumen:"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en resumir tickets de soporte."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500 if summary_type == SummaryType.SHORT else 1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenAI summary: {e}")
            return self._generate_simple_summary(context, summary_type)
    
    def _generate_anthropic_summary(self, context: str, summary_type: SummaryType) -> str:
        """Genera resumen con Anthropic Claude."""
        try:
            length_prompts = {
                SummaryType.SHORT: "en 1-2 oraciones",
                SummaryType.MEDIUM: "en un párrafo corto",
                SummaryType.LONG: "en un resumen completo",
                SummaryType.BULLET: "en puntos clave",
                SummaryType.EXECUTIVE: "en un resumen ejecutivo"
            }
            
            prompt = f"""Resume el siguiente contenido {length_prompts.get(summary_type, 'en un párrafo')}.

Contenido:
{context}"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating Anthropic summary: {e}")
            return self._generate_simple_summary(context, summary_type)
    
    def _generate_simple_summary(self, context: str, summary_type: SummaryType) -> str:
        """Genera resumen simple sin IA."""
        # Resumen básico: primeras 200 palabras
        words = context.split()
        if len(words) <= 50:
            return context
        
        if summary_type == SummaryType.SHORT:
            return " ".join(words[:30]) + "..."
        elif summary_type == SummaryType.BULLET:
            sentences = context.split(".")
            return "\n".join([f"- {s.strip()}" for s in sentences[:5] if s.strip()])
        else:
            return " ".join(words[:100]) + "..."
    
    def _extract_key_points(self, ticket_data: Dict[str, Any]) -> List[str]:
        """Extrae puntos clave del ticket."""
        points = []
        
        if ticket_data.get("priority") in ["critical", "urgent"]:
            points.append(f"Prioridad: {ticket_data['priority']}")
        
        if ticket_data.get("category"):
            points.append(f"Categoría: {ticket_data['category']}")
        
        # Extraer keywords importantes
        description = ticket_data.get("description", "")
        keywords = ["error", "problema", "no funciona", "urgente", "crítico"]
        for keyword in keywords:
            if keyword.lower() in description.lower():
                points.append(f"Contiene: {keyword}")
        
        return points[:5]  # Máximo 5 puntos
    
    def _extract_key_points_from_messages(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extrae puntos clave de mensajes."""
        points = []
        for msg in messages[:5]:  # Primeros 5 mensajes
            content = msg.get("content", "")
            if len(content) > 50:
                points.append(content[:100] + "...")
        return points
    
    def _analyze_sentiment(self, text: str) -> str:
        """Análisis básico de sentimiento."""
        text_lower = text.lower()
        if any(word in text_lower for word in ["problema", "error", "no funciona", "terrible"]):
            return "negative"
        elif any(word in text_lower for word in ["gracias", "perfecto", "excelente"]):
            return "positive"
        return "neutral"


class ConversationSummarizer:
    """Resumidor especializado en conversaciones."""
    
    def __init__(self, ai_summarizer: AISummarizer):
        """Inicializa resumidor de conversaciones."""
        self.ai_summarizer = ai_summarizer
    
    def summarize_thread(
        self,
        thread_id: str,
        messages: List[Dict[str, Any]],
        include_resolution: bool = True
    ) -> Summary:
        """
        Resume un thread completo.
        
        Args:
            thread_id: ID del thread
            messages: Lista de mensajes
            include_resolution: Incluir información de resolución
            
        Returns:
            Resumen del thread
        """
        # Agrupar mensajes por contexto
        context_messages = self._group_messages_by_context(messages)
        
        # Generar resumen
        summary = self.ai_summarizer.summarize_conversation(
            messages,
            SummaryType.MEDIUM
        )
        
        # Agregar información de resolución si está disponible
        if include_resolution:
            resolution_info = self._extract_resolution_info(messages)
            if resolution_info:
                summary.content += f"\n\nResolución: {resolution_info}"
        
        return summary
    
    def _group_messages_by_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Agrupa mensajes por contexto."""
        # Implementación básica - en producción usar técnicas más avanzadas
        return messages
    
    def _extract_resolution_info(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Extrae información de resolución."""
        # Buscar mensajes que indiquen resolución
        resolution_keywords = ["resuelto", "solucionado", "cerrado", "completado"]
        for msg in reversed(messages):
            content = msg.get("content", "").lower()
            if any(keyword in content for keyword in resolution_keywords):
                return msg.get("content", "")
        return None

