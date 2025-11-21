"""
Sistema de Machine Learning Básico para Soporte.

Características:
- Predicción de tiempo de resolución
- Predicción de satisfacción del cliente
- Clasificación automática de categorías
- Detección de patrones en tickets
- Recomendación de agentes
"""
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ResolutionPrediction:
    """Predicción de tiempo de resolución."""
    predicted_minutes: float
    confidence: float
    factors: Dict[str, Any]


@dataclass
class SatisfactionPrediction:
    """Predicción de satisfacción."""
    predicted_score: float  # 1-5
    confidence: float
    factors: Dict[str, Any]


class SupportMLPredictor:
    """Predictor básico usando reglas y estadísticas históricas."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el predictor ML.
        
        Args:
            db_connection: Conexión a BD para datos históricos
        """
        self.db_connection = db_connection
        self.historical_stats = {}
    
    def _load_historical_stats(self):
        """Carga estadísticas históricas desde BD."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Tiempo promedio de resolución por categoría y prioridad
            cursor.execute("""
                SELECT 
                    category,
                    priority,
                    AVG(time_to_resolution_minutes) as avg_resolution,
                    COUNT(*) as count
                FROM support_tickets
                WHERE status = 'resolved'
                AND time_to_resolution_minutes IS NOT NULL
                AND created_at >= NOW() - INTERVAL '90 days'
                GROUP BY category, priority
            """)
            
            for row in cursor.fetchall():
                key = f"{row[0]}_{row[1]}"
                self.historical_stats[key] = {
                    "avg_resolution": float(row[2]) if row[2] else None,
                    "count": row[3]
                }
            
            # Satisfacción promedio por agente
            cursor.execute("""
                SELECT 
                    t.assigned_agent_name,
                    AVG(f.satisfaction_score) as avg_satisfaction,
                    COUNT(f.id) as feedback_count
                FROM support_tickets t
                INNER JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
                WHERE t.assigned_agent_name IS NOT NULL
                GROUP BY t.assigned_agent_name
                HAVING COUNT(f.id) >= 5
            """)
            
            self.agent_satisfaction = {
                row[0]: {
                    "avg_satisfaction": float(row[1]) if row[1] else None,
                    "feedback_count": row[2]
                }
                for row in cursor.fetchall()
            }
            
            cursor.close()
            
        except Exception as e:
            logger.warning(f"Error loading historical stats: {e}")
    
    def predict_resolution_time(
        self,
        category: Optional[str],
        priority: str,
        department: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ResolutionPrediction:
        """
        Predice tiempo de resolución basado en datos históricos.
        
        Args:
            category: Categoría del ticket
            priority: Prioridad del ticket
            department: Departamento asignado
            agent_id: ID del agente asignado
            
        Returns:
            ResolutionPrediction con predicción
        """
        # Cargar stats si no están cargadas
        if not self.historical_stats:
            self._load_historical_stats()
        
        # Buscar estadística histórica
        key = f"{category or 'general'}_{priority}"
        historical = self.historical_stats.get(key)
        
        if historical and historical["avg_resolution"]:
            base_prediction = historical["avg_resolution"]
            confidence = min(0.9, 0.5 + (historical["count"] / 100.0))
        else:
            # Predicción basada en prioridad por defecto
            base_predictions = {
                "critical": 60,  # 1 hora
                "urgent": 240,   # 4 horas
                "high": 480,     # 8 horas
                "medium": 1440,  # 24 horas
                "low": 2880      # 48 horas
            }
            base_prediction = base_predictions.get(priority, 1440)
            confidence = 0.5
        
        # Ajustes por departamento
        adjustments = {
            "technical": 1.2,  # Técnico suele tardar más
            "billing": 0.8,     # Facturación suele ser más rápido
            "sales": 0.9,
            "support": 1.0
        }
        if department and department in adjustments:
            base_prediction *= adjustments[department]
        
        factors = {
            "base_prediction": base_prediction,
            "category": category,
            "priority": priority,
            "department": department,
            "historical_data_available": historical is not None
        }
        
        return ResolutionPrediction(
            predicted_minutes=base_prediction,
            confidence=confidence,
            factors=factors
        )
    
    def predict_satisfaction(
        self,
        ticket_id: str,
        agent_id: Optional[str] = None,
        resolution_time_minutes: Optional[float] = None,
        chatbot_resolved: bool = False
    ) -> SatisfactionPrediction:
        """
        Predice satisfacción del cliente.
        
        Args:
            ticket_id: ID del ticket
            agent_id: ID del agente
            resolution_time_minutes: Tiempo de resolución
            chatbot_resolved: Si fue resuelto por chatbot
            
        Returns:
            SatisfactionPrediction
        """
        if not self.agent_satisfaction:
            self._load_historical_stats()
        
        base_score = 3.5  # Score base neutral
        
        # Ajuste por agente
        if agent_id and self.agent_satisfaction:
            agent_name = None
            # Buscar nombre del agente (simplificado)
            # En producción, se buscaría en BD
            for name, stats in self.agent_satisfaction.items():
                if stats.get("avg_satisfaction", 0) > 0:
                    base_score = stats["avg_satisfaction"]
                    break
        
        # Ajuste por tiempo de resolución
        if resolution_time_minutes:
            if resolution_time_minutes < 60:
                base_score += 0.5  # Resolución rápida
            elif resolution_time_minutes < 240:
                base_score += 0.2
            elif resolution_time_minutes > 1440:
                base_score -= 0.3  # Resolución lenta
        
        # Ajuste por chatbot
        if chatbot_resolved:
            base_score += 0.1  # Clientes suelen estar satisfechos con respuestas rápidas
        
        # Normalizar entre 1-5
        predicted_score = max(1.0, min(5.0, base_score))
        
        # Calcular confianza
        confidence = 0.6  # Base
        if agent_id and agent_id in self.agent_satisfaction:
            confidence = min(0.9, 0.6 + (self.agent_satisfaction[agent_id]["feedback_count"] / 50.0))
        
        factors = {
            "base_score": base_score,
            "agent_factor": agent_id is not None,
            "resolution_time_factor": resolution_time_minutes is not None,
            "chatbot_factor": chatbot_resolved
        }
        
        return SatisfactionPrediction(
            predicted_score=predicted_score,
            confidence=confidence,
            factors=factors
        )
    
    def recommend_agent(
        self,
        category: Optional[str],
        priority: str,
        required_specialties: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Recomienda agente basado en historial y especialidades.
        
        Args:
            category: Categoría del ticket
            priority: Prioridad
            required_specialties: Especialidades requeridas
            
        Returns:
            Dict con información del agente recomendado o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar agente con mejor historial para esta categoría/prioridad
            query = """
                SELECT 
                    a.agent_id,
                    a.agent_name,
                    a.department,
                    a.specialties,
                    a.current_active_tickets,
                    a.max_concurrent_tickets,
                    COUNT(t.ticket_id) FILTER (
                        WHERE t.status = 'resolved' 
                        AND t.category = %s
                    ) as resolved_similar,
                    AVG(f.satisfaction_score) FILTER (
                        WHERE f.satisfaction_score IS NOT NULL
                    ) as avg_satisfaction
                FROM support_agents a
                LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id
                LEFT JOIN support_ticket_feedback f ON t.ticket_id = f.ticket_id
                WHERE a.is_available = true
                AND a.current_active_tickets < a.max_concurrent_tickets
            """
            
            params = [category]
            
            if required_specialties:
                query += " AND a.specialties && %s"
                params.append(required_specialties)
            
            query += """
                GROUP BY a.agent_id, a.agent_name, a.department, 
                         a.specialties, a.current_active_tickets, a.max_concurrent_tickets
                ORDER BY 
                    avg_satisfaction DESC NULLS LAST,
                    resolved_similar DESC,
                    a.current_active_tickets ASC
                LIMIT 1
            """
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "department": row[2],
                    "specialties": row[3] if row[3] else [],
                    "current_active_tickets": row[4],
                    "max_concurrent_tickets": row[5],
                    "resolved_similar": row[6] or 0,
                    "avg_satisfaction": float(row[7]) if row[7] else None
                }
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error recommending agent: {e}", exc_info=True)
            return None

