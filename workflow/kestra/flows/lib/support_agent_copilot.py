"""
Sistema de Copilot para Agentes.

Asistente inteligente que ayuda a los agentes en tiempo real.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CopilotSuggestion:
    """Sugerencia del copilot."""
    suggestion_id: str
    type: str  # "response", "action", "escalation", "knowledge"
    title: str
    content: str
    confidence: float
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = None


class AgentCopilot:
    """Copilot para agentes."""
    
    def __init__(
        self,
        learning_engine=None,
        quality_engine=None,
        api_key: Optional[str] = None
    ):
        """
        Inicializa copilot.
        
        Args:
            learning_engine: Motor de aprendizaje (opcional)
            quality_engine: Motor de calidad (opcional)
            api_key: API key de OpenAI (opcional)
        """
        self.learning_engine = learning_engine
        self.quality_engine = quality_engine
        self.api_key = api_key or None
        
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
    
    def get_suggestions(
        self,
        ticket_data: Dict[str, Any],
        agent_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[CopilotSuggestion]:
        """
        Obtiene sugerencias para el agente.
        
        Args:
            ticket_data: Datos del ticket
            agent_context: Contexto del agente
            conversation_history: Historial de conversación (opcional)
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        # Sugerencia de respuesta
        response_suggestion = self._suggest_response(ticket_data, conversation_history)
        if response_suggestion:
            suggestions.append(response_suggestion)
        
        # Sugerencia de acción
        action_suggestion = self._suggest_action(ticket_data, agent_context)
        if action_suggestion:
            suggestions.append(action_suggestion)
        
        # Sugerencia de escalación
        escalation_suggestion = self._suggest_escalation(ticket_data)
        if escalation_suggestion:
            suggestions.append(escalation_suggestion)
        
        # Sugerencias de conocimiento
        knowledge_suggestions = self._suggest_knowledge(ticket_data)
        suggestions.extend(knowledge_suggestions)
        
        # Ordenar por confianza
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        
        return suggestions[:5]  # Top 5
    
    def _suggest_response(
        self,
        ticket_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> Optional[CopilotSuggestion]:
        """Sugiere respuesta."""
        description = ticket_data.get("description", "")
        category = ticket_data.get("category", "")
        
        # Si hay contexto de aprendizaje, usar recomendaciones
        if self.learning_engine:
            recommendations = self.learning_engine.get_recommendations(ticket_data)
            if recommendations:
                rec = recommendations[0]
                return CopilotSuggestion(
                    suggestion_id=f"copilot-response-{rec.recommendation_id}",
                    type="response",
                    title="Respuesta Sugerida",
                    content=self._generate_response_content(ticket_data, rec),
                    confidence=rec.confidence,
                    reasoning="Basado en soluciones similares anteriores"
                )
        
        # Generar respuesta con IA si está disponible
        if OPENAI_AVAILABLE and self.api_key:
            try:
                response_text = self._generate_ai_response(ticket_data, conversation_history)
                if response_text:
                    return CopilotSuggestion(
                        suggestion_id=f"copilot-ai-response-{datetime.now().timestamp()}",
                        type="response",
                        title="Respuesta Generada por IA",
                        content=response_text,
                        confidence=0.75,
                        reasoning="Generada por IA basada en el contexto del ticket"
                    )
            except Exception as e:
                logger.error(f"Error generating AI response: {e}")
        
        return None
    
    def _generate_response_content(
        self,
        ticket_data: Dict[str, Any],
        recommendation
    ) -> str:
        """Genera contenido de respuesta desde recomendación."""
        # Template básico
        customer_name = ticket_data.get("customer_name", "Cliente")
        
        content = f"Hola {customer_name},\n\n"
        content += f"Gracias por contactarnos sobre: {ticket_data.get('subject', '')}\n\n"
        
        if recommendation.type == "solution":
            content += f"Basado en casos similares, te sugerimos:\n\n{recommendation.description}\n\n"
        elif recommendation.type == "template":
            content += "Te proporcionamos la siguiente respuesta:\n\n"
            content += recommendation.description
        
        content += "\nPor favor, confirma si esto resuelve tu problema.\n\n"
        content += "Saludos,\n"
        content += "[Tu nombre]"
        
        return content
    
    def _generate_ai_response(
        self,
        ticket_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> Optional[str]:
        """Genera respuesta usando IA."""
        try:
            prompt = f"""Eres un agente de soporte experto. Genera una respuesta profesional y útil para el siguiente ticket:

Título: {ticket_data.get('subject', '')}
Descripción: {ticket_data.get('description', '')}
Categoría: {ticket_data.get('category', '')}
Prioridad: {ticket_data.get('priority', 'normal')}

Genera una respuesta que:
1. Sea profesional y empática
2. Reconozca el problema del cliente
3. Proporcione pasos claros para resolver
4. Sea concisa pero completa

Respuesta:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un agente de soporte profesional y experto."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    def _suggest_action(
        self,
        ticket_data: Dict[str, Any],
        agent_context: Dict[str, Any]
    ) -> Optional[CopilotSuggestion]:
        """Sugiere acción."""
        priority = ticket_data.get("priority", "normal")
        status = ticket_data.get("status", "open")
        
        # Si es crítico y no asignado
        if priority in ["critical", "urgent"] and status == "open":
            return CopilotSuggestion(
                suggestion_id="copilot-action-assign",
                type="action",
                title="Asignar Ticket Urgente",
                content="Este ticket es crítico. Considera asignarlo inmediatamente a un agente disponible.",
                confidence=0.9,
                reasoning="Ticket crítico sin asignar"
            )
        
        # Si lleva mucho tiempo abierto
        created_at = ticket_data.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                from dateutil import parser
                created_at = parser.parse(created_at)
            
            hours_open = (datetime.now() - created_at).total_seconds() / 3600
            if hours_open > 24 and status != "resolved":
                return CopilotSuggestion(
                    suggestion_id="copilot-action-followup",
                    type="action",
                    title="Seguimiento Necesario",
                    content=f"Este ticket lleva {hours_open:.1f} horas abierto. Considera hacer seguimiento o escalar.",
                    confidence=0.7,
                    reasoning=f"Ticket abierto por {hours_open:.1f} horas"
                )
        
        return None
    
    def _suggest_escalation(
        self,
        ticket_data: Dict[str, Any]
    ) -> Optional[CopilotSuggestion]:
        """Sugiere escalación."""
        priority = ticket_data.get("priority", "normal")
        created_at = ticket_data.get("created_at")
        first_response_at = ticket_data.get("first_response_at")
        
        # Si es crítico y no hay respuesta
        if priority in ["critical", "urgent"] and not first_response_at:
            if isinstance(created_at, str):
                from dateutil import parser
                created_at = parser.parse(created_at)
            
            hours_open = (datetime.now() - created_at).total_seconds() / 3600
            if hours_open > 2:
                return CopilotSuggestion(
                    suggestion_id="copilot-escalate",
                    type="escalation",
                    title="Escalar Ticket",
                    content=f"Ticket crítico sin respuesta por {hours_open:.1f} horas. Considera escalar.",
                    confidence=0.95,
                    reasoning="Ticket crítico sin respuesta"
                )
        
        return None
    
    def _suggest_knowledge(
        self,
        ticket_data: Dict[str, Any]
    ) -> List[CopilotSuggestion]:
        """Sugiere artículos de conocimiento."""
        suggestions = []
        
        if self.learning_engine:
            recommendations = self.learning_engine.get_recommendations(ticket_data)
            knowledge_recs = [r for r in recommendations if r.type == "knowledge"]
            
            for rec in knowledge_recs[:3]:
                suggestions.append(CopilotSuggestion(
                    suggestion_id=f"copilot-knowledge-{rec.recommendation_id}",
                    type="knowledge",
                    title=rec.title,
                    content=rec.description,
                    confidence=rec.confidence,
                    reasoning="Artículo de conocimiento relacionado"
                ))
        
        return suggestions
    
    def get_quality_feedback(
        self,
        response_text: str,
        ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Proporciona feedback de calidad sobre una respuesta.
        
        Args:
            response_text: Texto de la respuesta
            response_data: Datos de la respuesta
            
        Returns:
            Feedback de calidad
        """
        feedback = {
            "score": 75.0,
            "strengths": [],
            "improvements": [],
            "suggestions": []
        }
        
        # Análisis básico
        if len(response_text) < 50:
            feedback["improvements"].append("La respuesta es muy corta. Considera agregar más detalles.")
            feedback["score"] -= 10
        elif len(response_text) > 1000:
            feedback["improvements"].append("La respuesta es muy larga. Considera hacerla más concisa.")
            feedback["score"] -= 5
        
        # Verificar profesionalismo
        if any(word in response_text.lower() for word in ["jaja", "lol", "wtf"]):
            feedback["improvements"].append("Evita palabras informales en respuestas profesionales.")
            feedback["score"] -= 15
        
        # Verificar saludo
        if any(greeting in response_text.lower() for greeting in ["hola", "buenos días", "saludos"]):
            feedback["strengths"].append("Incluye saludo profesional")
        
        # Verificar cierre
        if any(closing in response_text.lower() for closing in ["saludos", "atentamente", "gracias"]):
            feedback["strengths"].append("Incluye cierre profesional")
        
        # Sugerencias
        if feedback["score"] < 70:
            feedback["suggestions"].append("Revisa la respuesta antes de enviar para mejorar la calidad.")
        
        return feedback

