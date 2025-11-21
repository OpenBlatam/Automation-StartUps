"""
Sistema de Evaluación de Calidad Automática.

Evalúa automáticamente la calidad de respuestas y tickets resueltos.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class QualityScore(Enum):
    """Niveles de calidad."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 70-89
    FAIR = "fair"  # 50-69
    POOR = "poor"  # 0-49


@dataclass
class QualityCriteria:
    """Criterio de calidad."""
    criterion_id: str
    name: str
    description: str
    weight: float  # 0.0 a 1.0
    check_function: callable


@dataclass
class QualityEvaluation:
    """Evaluación de calidad."""
    evaluation_id: str
    ticket_id: str
    agent_id: str
    
    # Scores
    overall_score: float  # 0-100
    quality_level: QualityScore
    
    # Scores por criterio
    criterion_scores: Dict[str, float]
    
    # Feedback
    strengths: List[str]
    improvements: List[str]
    
    # Metadata
    evaluated_at: datetime = None
    evaluated_by: str = "system"
    
    def __post_init__(self):
        if self.evaluated_at is None:
            self.evaluated_at = datetime.now()


class QualityAssuranceEngine:
    """Motor de evaluación de calidad."""
    
    def __init__(self):
        """Inicializa motor de QA."""
        self.criteria: List[QualityCriteria] = []
        self._initialize_default_criteria()
    
    def _initialize_default_criteria(self):
        """Inicializa criterios por defecto."""
        criteria = [
            QualityCriteria(
                "response_time",
                "Tiempo de Respuesta",
                "Evalúa si se respondió en tiempo razonable",
                0.15,
                self._check_response_time
            ),
            QualityCriteria(
                "response_quality",
                "Calidad de Respuesta",
                "Evalúa la calidad del contenido de la respuesta",
                0.25,
                self._check_response_quality
            ),
            QualityCriteria(
                "professionalism",
                "Profesionalismo",
                "Evalúa el tono y profesionalismo",
                0.15,
                self._check_professionalism
            ),
            QualityCriteria(
                "resolution_completeness",
                "Completitud de Resolución",
                "Evalúa si el problema fue completamente resuelto",
                0.20,
                self._check_resolution_completeness
            ),
            QualityCriteria(
                "documentation",
                "Documentación",
                "Evalúa si se documentó correctamente",
                0.10,
                self._check_documentation
            ),
            QualityCriteria(
                "customer_satisfaction",
                "Satisfacción del Cliente",
                "Evalúa según feedback del cliente",
                0.15,
                self._check_customer_satisfaction
            )
        ]
        
        self.criteria = criteria
    
    def register_criterion(self, criterion: QualityCriteria):
        """Registra un criterio de calidad."""
        self.criteria.append(criterion)
    
    def evaluate_ticket(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]] = None
    ) -> QualityEvaluation:
        """
        Evalúa calidad de un ticket resuelto.
        
        Args:
            ticket_data: Datos del ticket
            response_data: Datos de la respuesta (opcional)
            
        Returns:
            Evaluación de calidad
        """
        ticket_id = ticket_data.get("ticket_id")
        agent_id = ticket_data.get("assigned_agent_id", "unknown")
        
        criterion_scores = {}
        strengths = []
        improvements = []
        
        # Evaluar cada criterio
        for criterion in self.criteria:
            try:
                score = criterion.check_function(ticket_data, response_data)
                criterion_scores[criterion.criterion_id] = score
                
                # Generar feedback
                if score >= 80:
                    strengths.append(f"{criterion.name}: Excelente (score: {score:.1f})")
                elif score < 60:
                    improvements.append(f"{criterion.name}: Necesita mejora (score: {score:.1f})")
            except Exception as e:
                logger.error(f"Error evaluating criterion {criterion.criterion_id}: {e}")
                criterion_scores[criterion.criterion_id] = 0.0
        
        # Calcular score general (promedio ponderado)
        total_weight = sum(c.weight for c in self.criteria)
        overall_score = sum(
            criterion_scores.get(c.criterion_id, 0) * c.weight
            for c in self.criteria
        ) / total_weight if total_weight > 0 else 0.0
        
        # Determinar nivel de calidad
        if overall_score >= 90:
            quality_level = QualityScore.EXCELLENT
        elif overall_score >= 70:
            quality_level = QualityScore.GOOD
        elif overall_score >= 50:
            quality_level = QualityScore.FAIR
        else:
            quality_level = QualityScore.POOR
        
        evaluation = QualityEvaluation(
            evaluation_id=f"qa-{ticket_id}-{datetime.now().timestamp()}",
            ticket_id=ticket_id,
            agent_id=agent_id,
            overall_score=overall_score,
            quality_level=quality_level,
            criterion_scores=criterion_scores,
            strengths=strengths,
            improvements=improvements
        )
        
        logger.info(f"Quality evaluation for ticket {ticket_id}: {overall_score:.1f} ({quality_level.value})")
        return evaluation
    
    def _check_response_time(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa tiempo de respuesta."""
        first_response_at = ticket_data.get("first_response_at")
        created_at = ticket_data.get("created_at")
        
        if not first_response_at or not created_at:
            return 50.0  # Score medio si no hay datos
        
        # Convertir a datetime si son strings
        if isinstance(first_response_at, str):
            from dateutil import parser
            first_response_at = parser.parse(first_response_at)
        if isinstance(created_at, str):
            from dateutil import parser
            created_at = parser.parse(created_at)
        
        response_time_hours = (first_response_at - created_at).total_seconds() / 3600
        
        # Score basado en tiempo (ideal: < 1 hora = 100, > 24 horas = 0)
        if response_time_hours <= 1:
            return 100.0
        elif response_time_hours <= 4:
            return 90.0
        elif response_time_hours <= 8:
            return 75.0
        elif response_time_hours <= 24:
            return 50.0
        else:
            return max(0.0, 50.0 - (response_time_hours - 24) * 2)
    
    def _check_response_quality(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa calidad de respuesta."""
        resolution_notes = ticket_data.get("resolution_notes", "")
        description = ticket_data.get("description", "")
        
        if not resolution_notes:
            return 30.0  # Bajo score si no hay notas
        
        score = 50.0  # Base
        
        # Longitud adecuada (50-500 caracteres)
        length = len(resolution_notes)
        if 50 <= length <= 500:
            score += 20.0
        elif length > 500:
            score += 10.0
        
        # Presencia de palabras clave útiles
        helpful_keywords = ["solución", "resuelto", "pasos", "configuración", "actualizar"]
        keyword_count = sum(1 for kw in helpful_keywords if kw.lower() in resolution_notes.lower())
        score += min(keyword_count * 5, 20.0)
        
        # Estructura (presencia de listas o pasos)
        if any(marker in resolution_notes for marker in ["1.", "2.", "-", "*", "paso"]):
            score += 10.0
        
        return min(score, 100.0)
    
    def _check_professionalism(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa profesionalismo."""
        resolution_notes = ticket_data.get("resolution_notes", "")
        
        if not resolution_notes:
            return 50.0
        
        score = 70.0  # Base
        
        # Palabras no profesionales
        unprofessional_words = ["jaja", "lol", "wtf", "idk", "asap"]
        for word in unprofessional_words:
            if word.lower() in resolution_notes.lower():
                score -= 20.0
        
        # Saludos profesionales
        professional_greetings = ["hola", "buenos días", "buenas tardes", "saludos", "gracias"]
        if any(greeting in resolution_notes.lower() for greeting in professional_greetings):
            score += 15.0
        
        # Cierre profesional
        professional_closings = ["saludos", "atentamente", "quedo a disposición", "cordialmente"]
        if any(closing in resolution_notes.lower() for closing in professional_closings):
            score += 15.0
        
        return max(0.0, min(score, 100.0))
    
    def _check_resolution_completeness(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa completitud de resolución."""
        status = ticket_data.get("status")
        resolution_notes = ticket_data.get("resolution_notes", "")
        
        if status != "resolved":
            return 0.0
        
        score = 60.0  # Base por estar resuelto
        
        if resolution_notes:
            score += 20.0
        
        # Verificar si hay solución clara
        solution_indicators = ["resuelto", "solucionado", "solucion", "funcionando", "correcto"]
        if any(indicator in resolution_notes.lower() for indicator in solution_indicators):
            score += 20.0
        
        return min(score, 100.0)
    
    def _check_documentation(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa documentación."""
        resolution_notes = ticket_data.get("resolution_notes", "")
        tags = ticket_data.get("tags", [])
        
        score = 50.0
        
        if resolution_notes:
            score += 30.0
        
        if tags:
            score += 10.0
        
        # Presencia de información técnica
        technical_indicators = ["código", "error", "log", "configuración", "api", "endpoint"]
        if any(indicator in resolution_notes.lower() for indicator in technical_indicators):
            score += 10.0
        
        return min(score, 100.0)
    
    def _check_customer_satisfaction(
        self,
        ticket_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]]
    ) -> float:
        """Evalúa satisfacción del cliente."""
        satisfaction_score = ticket_data.get("customer_satisfaction_score")
        
        if satisfaction_score is None:
            return 70.0  # Score neutral si no hay feedback
        
        # Convertir a escala 0-100
        if isinstance(satisfaction_score, (int, float)):
            return float(satisfaction_score) * 20  # Asumiendo escala 1-5
        
        return 70.0
    
    def get_agent_quality_report(
        self,
        agent_id: str,
        evaluations: List[QualityEvaluation]
    ) -> Dict[str, Any]:
        """
        Genera reporte de calidad para un agente.
        
        Args:
            agent_id: ID del agente
            evaluations: Lista de evaluaciones
            
        Returns:
            Reporte de calidad
        """
        agent_evals = [e for e in evaluations if e.agent_id == agent_id]
        
        if not agent_evals:
            return {"error": "No evaluations found"}
        
        total_evals = len(agent_evals)
        avg_score = sum(e.overall_score for e in agent_evals) / total_evals
        
        # Distribución por nivel
        distribution = {
            "excellent": sum(1 for e in agent_evals if e.quality_level == QualityScore.EXCELLENT),
            "good": sum(1 for e in agent_evals if e.quality_level == QualityScore.GOOD),
            "fair": sum(1 for e in agent_evals if e.quality_level == QualityScore.FAIR),
            "poor": sum(1 for e in agent_evals if e.quality_level == QualityScore.POOR)
        }
        
        # Promedios por criterio
        criterion_averages = {}
        for criterion in self.criteria:
            criterion_id = criterion.criterion_id
            scores = [e.criterion_scores.get(criterion_id, 0) for e in agent_evals]
            if scores:
                criterion_averages[criterion_id] = sum(scores) / len(scores)
        
        # Fortalezas y mejoras más comunes
        all_strengths = []
        all_improvements = []
        for eval in agent_evals:
            all_strengths.extend(eval.strengths)
            all_improvements.extend(eval.improvements)
        
        from collections import Counter
        common_strengths = [item for item, _ in Counter(all_strengths).most_common(3)]
        common_improvements = [item for item, _ in Counter(all_improvements).most_common(3)]
        
        return {
            "agent_id": agent_id,
            "total_evaluations": total_evals,
            "average_score": avg_score,
            "quality_distribution": distribution,
            "criterion_averages": criterion_averages,
            "common_strengths": common_strengths,
            "common_improvements": common_improvements,
            "recommendations": self._generate_recommendations(avg_score, criterion_averages)
        }
    
    def _generate_recommendations(
        self,
        avg_score: float,
        criterion_averages: Dict[str, float]
    ) -> List[str]:
        """Genera recomendaciones basadas en scores."""
        recommendations = []
        
        if avg_score < 70:
            recommendations.append("Score general bajo. Considerar entrenamiento adicional.")
        
        # Identificar criterios débiles
        for criterion_id, avg in criterion_averages.items():
            if avg < 60:
                criterion = next((c for c in self.criteria if c.criterion_id == criterion_id), None)
                if criterion:
                    recommendations.append(f"Mejorar {criterion.name}: Score actual {avg:.1f}")
        
        if not recommendations:
            recommendations.append("Mantener el buen nivel de calidad.")
        
        return recommendations

