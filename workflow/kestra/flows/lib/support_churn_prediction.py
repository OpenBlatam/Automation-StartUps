"""
Sistema de Predicción de Churn para Soporte.

Analiza el comportamiento de clientes para predecir riesgo de churn
y sugerir acciones preventivas.
"""
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ChurnRiskLevel(Enum):
    """Niveles de riesgo de churn."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ChurnPrediction:
    """Predicción de churn."""
    customer_id: str
    risk_level: ChurnRiskLevel
    risk_score: float  # 0.0 a 100.0
    confidence: float  # 0.0 a 1.0
    factors: Dict[str, Any]
    predicted_churn_days: Optional[int]
    recommendations: List[str]
    created_at: datetime


@dataclass
class ChurnFactor:
    """Factor que contribuye al churn."""
    name: str
    weight: float
    value: float
    impact: str  # positive/negative
    description: str


class ChurnPredictor:
    """Sistema de predicción de churn."""
    
    def __init__(self, db_connection):
        """
        Inicializar predictor de churn.
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.db = db_connection
        
    def predict_churn(self, customer_id: str, days_lookback: int = 90) -> ChurnPrediction:
        """
        Predecir riesgo de churn para un cliente.
        
        Args:
            customer_id: ID del cliente
            days_lookback: Días hacia atrás para análisis
            
        Returns:
            Predicción de churn
        """
        try:
            # Obtener datos del cliente
            customer_data = self._get_customer_data(customer_id, days_lookback)
            
            # Calcular factores
            factors = self._calculate_factors(customer_data)
            
            # Calcular score de riesgo
            risk_score = self._calculate_risk_score(factors)
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(risk_score)
            
            # Calcular confianza
            confidence = self._calculate_confidence(customer_data, factors)
            
            # Predecir días hasta churn
            predicted_days = self._predict_churn_days(risk_score, customer_data)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(risk_level, factors)
            
            return ChurnPrediction(
                customer_id=customer_id,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                factors={f.name: f.value for f in factors},
                predicted_churn_days=predicted_days,
                recommendations=recommendations,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error prediciendo churn: {e}")
            raise
    
    def _get_customer_data(self, customer_id: str, days_lookback: int) -> Dict[str, Any]:
        """Obtener datos del cliente."""
        cutoff_date = datetime.now() - timedelta(days=days_lookback)
        
        # Tickets del cliente
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as ticket_count,
                AVG(resolution_time_hours) as avg_resolution_time,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_count,
                AVG(satisfaction_score) as avg_satisfaction,
                COUNT(CASE WHEN priority IN ('urgent', 'critical') THEN 1 END) as urgent_count
            FROM support_tickets
            WHERE customer_email = %s
            AND created_at >= %s
        """, (customer_id, cutoff_date))
        
        ticket_data = cursor.fetchone()
        
        # Último ticket
        cursor.execute("""
            SELECT created_at, status, satisfaction_score
            FROM support_tickets
            WHERE customer_email = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (customer_id,))
        
        last_ticket = cursor.fetchone()
        
        # Días desde último contacto
        days_since_contact = None
        if last_ticket and last_ticket[0]:
            days_since_contact = (datetime.now() - last_ticket[0]).days
        
        return {
            "ticket_count": ticket_data[0] or 0,
            "avg_resolution_time": ticket_data[1] or 0,
            "resolved_count": ticket_data[2] or 0,
            "open_count": ticket_data[3] or 0,
            "avg_satisfaction": ticket_data[4],
            "urgent_count": ticket_data[5] or 0,
            "days_since_contact": days_since_contact,
            "last_ticket_status": last_ticket[1] if last_ticket else None,
            "last_satisfaction": last_ticket[2] if last_ticket else None
        }
    
    def _calculate_factors(self, customer_data: Dict[str, Any]) -> List[ChurnFactor]:
        """Calcular factores de riesgo."""
        factors = []
        
        # Factor: Días desde último contacto
        days_since = customer_data.get("days_since_contact", 0)
        if days_since and days_since > 30:
            risk_value = min(days_since / 90, 1.0) * 100
            factors.append(ChurnFactor(
                name="days_since_contact",
                weight=0.25,
                value=risk_value,
                impact="negative",
                description=f"Sin contacto desde hace {days_since} días"
            ))
        
        # Factor: Satisfacción promedio
        avg_satisfaction = customer_data.get("avg_satisfaction")
        if avg_satisfaction is not None:
            if avg_satisfaction < 3.0:
                risk_value = (3.0 - avg_satisfaction) / 3.0 * 100
                factors.append(ChurnFactor(
                    name="low_satisfaction",
                    weight=0.30,
                    value=risk_value,
                    impact="negative",
                    description=f"Satisfacción baja: {avg_satisfaction:.1f}/5"
                ))
        
        # Factor: Tickets urgentes
        urgent_count = customer_data.get("urgent_count", 0)
        if urgent_count > 3:
            risk_value = min(urgent_count / 10, 1.0) * 100
            factors.append(ChurnFactor(
                name="many_urgent_tickets",
                weight=0.20,
                value=risk_value,
                impact="negative",
                description=f"{urgent_count} tickets urgentes/críticos"
            ))
        
        # Factor: Tiempo de resolución
        avg_resolution = customer_data.get("avg_resolution_time", 0)
        if avg_resolution > 48:
            risk_value = min((avg_resolution - 48) / 72, 1.0) * 100
            factors.append(ChurnFactor(
                name="slow_resolution",
                weight=0.15,
                value=risk_value,
                impact="negative",
                description=f"Resolución lenta: {avg_resolution:.1f}h promedio"
            ))
        
        # Factor: Tickets sin resolver
        open_count = customer_data.get("open_count", 0)
        if open_count > 2:
            risk_value = min(open_count / 5, 1.0) * 100
            factors.append(ChurnFactor(
                name="unresolved_tickets",
                weight=0.10,
                value=risk_value,
                impact="negative",
                description=f"{open_count} tickets sin resolver"
            ))
        
        return factors
    
    def _calculate_risk_score(self, factors: List[ChurnFactor]) -> float:
        """Calcular score de riesgo."""
        if not factors:
            return 0.0
        
        weighted_sum = sum(f.weight * f.value for f in factors)
        total_weight = sum(f.weight for f in factors)
        
        if total_weight == 0:
            return 0.0
        
        return min(weighted_sum / total_weight, 100.0)
    
    def _determine_risk_level(self, risk_score: float) -> ChurnRiskLevel:
        """Determinar nivel de riesgo."""
        if risk_score >= 75:
            return ChurnRiskLevel.CRITICAL
        elif risk_score >= 50:
            return ChurnRiskLevel.HIGH
        elif risk_score >= 25:
            return ChurnRiskLevel.MEDIUM
        else:
            return ChurnRiskLevel.LOW
    
    def _calculate_confidence(self, customer_data: Dict[str, Any], factors: List[ChurnFactor]) -> float:
        """Calcular confianza en la predicción."""
        # Más datos = más confianza
        ticket_count = customer_data.get("ticket_count", 0)
        data_confidence = min(ticket_count / 10, 1.0)
        
        # Más factores = más confianza
        factor_confidence = min(len(factors) / 5, 1.0)
        
        # Confianza combinada
        confidence = (data_confidence * 0.6 + factor_confidence * 0.4)
        
        return min(confidence, 1.0)
    
    def _predict_churn_days(self, risk_score: float, customer_data: Dict[str, Any]) -> Optional[int]:
        """Predecir días hasta posible churn."""
        if risk_score < 25:
            return None
        
        # Modelo simple: mayor score = menos días
        base_days = 180 - (risk_score * 1.5)
        
        # Ajustar por días sin contacto
        days_since = customer_data.get("days_since_contact", 0)
        if days_since > 30:
            base_days -= days_since * 0.5
        
        return max(int(base_days), 7)
    
    def _generate_recommendations(self, risk_level: ChurnRiskLevel, factors: List[ChurnFactor]) -> List[str]:
        """Generar recomendaciones."""
        recommendations = []
        
        if risk_level == ChurnRiskLevel.CRITICAL:
            recommendations.append("Contacto inmediato requerido - cliente en alto riesgo")
            recommendations.append("Asignar agente senior o manager")
            recommendations.append("Ofrecer descuento o compensación")
        
        if risk_level in [ChurnRiskLevel.HIGH, ChurnRiskLevel.CRITICAL]:
            recommendations.append("Programar llamada de seguimiento")
            recommendations.append("Revisar todos los tickets pendientes")
        
        # Recomendaciones basadas en factores
        factor_names = {f.name for f in factors}
        
        if "days_since_contact" in factor_names:
            recommendations.append("Contactar al cliente para verificar satisfacción")
        
        if "low_satisfaction" in factor_names:
            recommendations.append("Investigar causas de insatisfacción")
            recommendations.append("Ofrecer solución proactiva")
        
        if "many_urgent_tickets" in factor_names:
            recommendations.append("Priorizar resolución de tickets urgentes")
            recommendations.append("Revisar proceso de escalamiento")
        
        if "slow_resolution" in factor_names:
            recommendations.append("Optimizar tiempos de respuesta")
            recommendations.append("Asignar más recursos al caso")
        
        if "unresolved_tickets" in factor_names:
            recommendations.append("Resolver todos los tickets pendientes")
            recommendations.append("Comunicar estado actualizado")
        
        return list(set(recommendations))  # Remover duplicados
    
    def get_at_risk_customers(self, risk_level: Optional[ChurnRiskLevel] = None, limit: int = 100) -> List[ChurnPrediction]:
        """
        Obtener clientes en riesgo.
        
        Args:
            risk_level: Nivel de riesgo (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de predicciones
        """
        try:
            # Obtener todos los clientes únicos
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT DISTINCT customer_email
                FROM support_tickets
                WHERE customer_email IS NOT NULL
                ORDER BY customer_email
                LIMIT %s
            """, (limit * 2,))
            
            customers = cursor.fetchall()
            
            predictions = []
            for (customer_id,) in customers:
                prediction = self.predict_churn(customer_id)
                
                if risk_level is None or prediction.risk_level == risk_level:
                    predictions.append(prediction)
                
                if len(predictions) >= limit:
                    break
            
            # Ordenar por score descendente
            predictions.sort(key=lambda x: x.risk_score, reverse=True)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error obteniendo clientes en riesgo: {e}")
            raise
    
    def track_churn_prevention_action(self, customer_id: str, action: str, agent_id: str, notes: Optional[str] = None):
        """
        Registrar acción preventiva de churn.
        
        Args:
            customer_id: ID del cliente
            action: Tipo de acción
            agent_id: ID del agente
            notes: Notas adicionales
        """
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO support_churn_prevention_actions
                (customer_id, action_type, agent_id, notes, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_id, action, agent_id, notes, datetime.now()))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error registrando acción preventiva: {e}")
            self.db.rollback()
            raise
    
    def get_churn_prevention_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de acciones preventivas."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT action_type, agent_id, notes, created_at
                FROM support_churn_prevention_actions
                WHERE customer_id = %s
                ORDER BY created_at DESC
            """, (customer_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "action_type": row[0],
                    "agent_id": row[1],
                    "notes": row[2],
                    "created_at": row[3]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []



