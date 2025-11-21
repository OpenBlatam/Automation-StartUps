"""
Sistema de Aprendizaje y Recomendaciones para Agentes.

Proporciona recomendaciones inteligentes basadas en historial y patrones.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """Recomendación."""
    recommendation_id: str
    type: str  # "solution", "template", "escalation", "knowledge"
    title: str
    description: str
    confidence: float  # 0.0 a 1.0
    priority: str  # "high", "medium", "low"
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class LearningPattern:
    """Patrón de aprendizaje."""
    pattern_id: str
    category: str
    pattern: str
    success_rate: float
    usage_count: int
    last_used: datetime


class LearningEngine:
    """Motor de aprendizaje y recomendaciones."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa motor de aprendizaje.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.patterns: Dict[str, LearningPattern] = {}
        self.agent_preferences: Dict[str, Dict[str, Any]] = {}
        self.solution_history: List[Dict[str, Any]] = []
    
    def get_recommendations(
        self,
        ticket_data: Dict[str, Any],
        agent_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """
        Obtiene recomendaciones para un ticket.
        
        Args:
            ticket_data: Datos del ticket
            agent_id: ID del agente (opcional)
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendación de soluciones similares
        similar_solutions = self._find_similar_solutions(ticket_data)
        for solution in similar_solutions:
            recommendations.append(Recommendation(
                recommendation_id=f"sol-{solution['id']}",
                type="solution",
                title=f"Solución similar: {solution['title']}",
                description=solution.get("description", ""),
                confidence=solution.get("similarity", 0.0),
                priority="high" if solution.get("similarity", 0) > 0.8 else "medium"
            ))
        
        # Recomendación de templates
        templates = self._recommend_templates(ticket_data, agent_id)
        for template in templates:
            recommendations.append(Recommendation(
                recommendation_id=f"template-{template['id']}",
                type="template",
                title=f"Template: {template['name']}",
                description=template.get("description", ""),
                confidence=template.get("match_score", 0.0),
                priority="medium"
            ))
        
        # Recomendación de escalación
        escalation_rec = self._check_escalation_needed(ticket_data)
        if escalation_rec:
            recommendations.append(escalation_rec)
        
        # Recomendación de conocimiento
        knowledge_recs = self._recommend_knowledge(ticket_data)
        recommendations.extend(knowledge_recs)
        
        # Ordenar por prioridad y confianza
        recommendations.sort(
            key=lambda r: (
                0 if r.priority == "high" else 1 if r.priority == "medium" else 2,
                -r.confidence
            )
        )
        
        return recommendations[:10]  # Top 10
    
    def _find_similar_solutions(
        self,
        ticket_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Encuentra soluciones similares."""
        # Implementación básica - en producción usar embeddings o ML
        description = ticket_data.get("description", "").lower()
        category = ticket_data.get("category", "")
        
        similar = []
        
        # Buscar en historial de soluciones
        for solution in self.solution_history:
            sol_desc = solution.get("description", "").lower()
            sol_cat = solution.get("category", "")
            
            # Calcular similitud simple (palabras en común)
            desc_words = set(description.split())
            sol_words = set(sol_desc.split())
            
            if desc_words and sol_words:
                similarity = len(desc_words & sol_words) / len(desc_words | sol_words)
                
                if similarity > 0.3:  # Threshold
                    similar.append({
                        "id": solution.get("id"),
                        "title": solution.get("title"),
                        "description": solution.get("description"),
                        "similarity": similarity,
                        "category": sol_cat
                    })
        
        # Ordenar por similitud
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:5]
    
    def _recommend_templates(
        self,
        ticket_data: Dict[str, Any],
        agent_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Recomienda templates."""
        category = ticket_data.get("category", "")
        tags = ticket_data.get("tags", [])
        
        # Templates por defecto (en producción cargar desde BD)
        templates = [
            {
                "id": "ticket-resolved",
                "name": "Ticket Resuelto",
                "description": "Template para ticket resuelto",
                "category": "general",
                "match_score": 0.5
            },
            {
                "id": "technical-issue",
                "name": "Problema Técnico",
                "description": "Template para problemas técnicos",
                "category": "technical",
                "match_score": 0.8 if category == "technical" else 0.3
            }
        ]
        
        # Filtrar y ordenar
        matched = [t for t in templates if t["match_score"] > 0.4]
        matched.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched[:3]
    
    def _check_escalation_needed(
        self,
        ticket_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """Verifica si se necesita escalación."""
        priority = ticket_data.get("priority", "normal")
        created_at = ticket_data.get("created_at")
        status = ticket_data.get("status")
        
        # Si ya está escalado o resuelto, no recomendar
        if status in ["resolved", "closed", "escalated"]:
            return None
        
        # Verificar si es crítico y no ha sido respondido
        if priority in ["critical", "urgent"]:
            if isinstance(created_at, str):
                from dateutil import parser
                created_at = parser.parse(created_at)
            
            hours_open = (datetime.now() - created_at).total_seconds() / 3600
            
            if hours_open > 2:  # Más de 2 horas sin respuesta
                return Recommendation(
                    recommendation_id="escalate-urgent",
                    type="escalation",
                    title="Escalar Ticket Urgente",
                    description=f"Ticket crítico abierto por {hours_open:.1f} horas sin respuesta",
                    confidence=0.9,
                    priority="high"
                )
        
        return None
    
    def _recommend_knowledge(
        self,
        ticket_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recomienda artículos de conocimiento."""
        description = ticket_data.get("description", "").lower()
        category = ticket_data.get("category", "")
        
        # Artículos de conocimiento (en producción cargar desde BD)
        knowledge_base = [
            {
                "id": "kb-api-connection",
                "title": "Guía de Conexión API",
                "category": "technical",
                "keywords": ["api", "conexión", "error"]
            },
            {
                "id": "kb-billing",
                "title": "Guía de Facturación",
                "category": "billing",
                "keywords": ["factura", "pago", "cobro"]
            }
        ]
        
        recommendations = []
        for kb in knowledge_base:
            # Verificar si coincide con categoría o keywords
            match_score = 0.0
            
            if kb["category"] == category:
                match_score += 0.5
            
            keyword_matches = sum(
                1 for kw in kb["keywords"]
                if kw.lower() in description
            )
            match_score += min(keyword_matches * 0.2, 0.5)
            
            if match_score > 0.4:
                recommendations.append(Recommendation(
                    recommendation_id=f"kb-{kb['id']}",
                    type="knowledge",
                    title=kb["title"],
                    description=f"Artículo de conocimiento relacionado",
                    confidence=match_score,
                    priority="medium"
                ))
        
        return recommendations
    
    def learn_from_resolution(
        self,
        ticket_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ):
        """
        Aprende de una resolución.
        
        Args:
            ticket_data: Datos del ticket
            resolution_data: Datos de la resolución
        """
        # Guardar solución en historial
        solution = {
            "id": f"sol-{ticket_data.get('ticket_id')}",
            "title": ticket_data.get("subject", ""),
            "description": ticket_data.get("description", ""),
            "category": ticket_data.get("category", ""),
            "resolution": resolution_data.get("notes", ""),
            "satisfaction": ticket_data.get("customer_satisfaction_score"),
            "timestamp": datetime.now()
        }
        
        self.solution_history.append(solution)
        
        # Mantener solo últimos 1000
        if len(self.solution_history) > 1000:
            self.solution_history = self.solution_history[-1000:]
        
        # Actualizar patrones
        self._update_patterns(ticket_data, resolution_data)
        
        logger.info(f"Learned from resolution: {ticket_data.get('ticket_id')}")
    
    def _update_patterns(
        self,
        ticket_data: Dict[str, Any],
        resolution_data: Dict[str, Any]
    ):
        """Actualiza patrones de aprendizaje."""
        category = ticket_data.get("category", "general")
        resolution = resolution_data.get("notes", "")
        
        # Crear patrón simple
        pattern_key = f"{category}:{resolution[:50]}"
        
        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = LearningPattern(
                pattern_id=f"pattern-{len(self.patterns)}",
                category=category,
                pattern=resolution[:100],
                success_rate=1.0,
                usage_count=1,
                last_used=datetime.now()
            )
        else:
            pattern = self.patterns[pattern_key]
            pattern.usage_count += 1
            pattern.last_used = datetime.now()
            
            # Actualizar success rate si hay satisfacción
            satisfaction = ticket_data.get("customer_satisfaction_score")
            if satisfaction:
                # Promedio móvil
                pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + satisfaction) / pattern.usage_count
    
    def get_agent_insights(self, agent_id: str) -> Dict[str, Any]:
        """
        Obtiene insights para un agente.
        
        Args:
            agent_id: ID del agente
            
        Returns:
            Insights del agente
        """
        # Filtrar historial del agente
        agent_solutions = [
            s for s in self.solution_history
            if s.get("agent_id") == agent_id
        ]
        
        if not agent_solutions:
            return {"message": "No hay datos suficientes"}
        
        # Calcular métricas
        total_solutions = len(agent_solutions)
        avg_satisfaction = sum(
            s.get("satisfaction", 0) for s in agent_solutions
            if s.get("satisfaction")
        ) / max(1, sum(1 for s in agent_solutions if s.get("satisfaction")))
        
        # Categorías más frecuentes
        categories = defaultdict(int)
        for solution in agent_solutions:
            categories[solution.get("category", "unknown")] += 1
        
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "agent_id": agent_id,
            "total_solutions": total_solutions,
            "average_satisfaction": avg_satisfaction,
            "top_categories": [{"category": cat, "count": count} for cat, count in top_categories],
            "recommendations": self._generate_agent_recommendations(agent_solutions, avg_satisfaction)
        }
    
    def _generate_agent_recommendations(
        self,
        solutions: List[Dict[str, Any]],
        avg_satisfaction: float
    ) -> List[str]:
        """Genera recomendaciones para el agente."""
        recommendations = []
        
        if avg_satisfaction < 3.5:
            recommendations.append("Mejorar satisfacción del cliente. Considerar entrenamiento adicional.")
        
        # Categorías con menos experiencia
        categories = set(s.get("category") for s in solutions)
        if len(categories) < 3:
            recommendations.append("Diversificar experiencia en diferentes categorías.")
        
        return recommendations

