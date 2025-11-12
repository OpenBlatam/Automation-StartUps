"""
Sistema Avanzado de Troubleshooting - Versión Mejorada.

Incluye:
- Detección inteligente de problemas con ML
- Personalización según historial del cliente
- Optimización de pasos según éxito previo
- Analytics y métricas avanzadas
- Integración completa con schema de BD
- Sistema de aprendizaje automático
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ProblemDetectionMethod(Enum):
    """Métodos de detección de problemas."""
    KEYWORD_MATCHING = "keyword_matching"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    ML_CLASSIFICATION = "ml_classification"
    LLM_ANALYSIS = "llm_analysis"
    HYBRID = "hybrid"  # Combinación de métodos


class StepOptimizationStrategy(Enum):
    """Estrategias de optimización de pasos."""
    SUCCESS_RATE = "success_rate"  # Ordenar por tasa de éxito
    DURATION = "duration"  # Ordenar por duración promedio
    CUSTOMER_SATISFACTION = "customer_satisfaction"  # Ordenar por satisfacción
    HYBRID = "hybrid"  # Combinación de factores


class TroubleshootingAdvanced:
    """Sistema avanzado de troubleshooting con ML y optimización."""
    
    def __init__(self, db_connection=None):
        """Inicializa el sistema avanzado."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def detect_problem_advanced(
        self,
        problem_description: str,
        customer_email: Optional[str] = None,
        customer_history: Optional[Dict[str, Any]] = None,
        method: ProblemDetectionMethod = ProblemDetectionMethod.HYBRID
    ) -> Dict[str, Any]:
        """
        Detecta problemas usando métodos avanzados.
        
        Args:
            problem_description: Descripción del problema
            customer_email: Email del cliente (para historial)
            customer_history: Historial del cliente
            method: Método de detección
            
        Returns:
            Dict con problema detectado, confianza, y metadata
        """
        # Obtener historial si no se proporciona
        if not customer_history and customer_email and self.db:
            customer_history = self._get_customer_history(customer_email)
        
        # Aplicar método de detección
        if method == ProblemDetectionMethod.HYBRID:
            results = self._hybrid_detection(problem_description, customer_history)
        elif method == ProblemDetectionMethod.KEYWORD_MATCHING:
            results = self._keyword_detection(problem_description)
        elif method == ProblemDetectionMethod.SEMANTIC_SIMILARITY:
            results = self._semantic_detection(problem_description)
        elif method == ProblemDetectionMethod.ML_CLASSIFICATION:
            results = self._ml_detection(problem_description, customer_history)
        elif method == ProblemDetectionMethod.LLM_ANALYSIS:
            results = self._llm_detection(problem_description)
        else:
            results = self._hybrid_detection(problem_description, customer_history)
        
        # Ajustar confianza según historial
        if customer_history:
            results = self._adjust_confidence_by_history(results, customer_history)
        
        return results
    
    def optimize_steps(
        self,
        problem_id: str,
        customer_email: Optional[str] = None,
        strategy: StepOptimizationStrategy = StepOptimizationStrategy.HYBRID
    ) -> List[Dict[str, Any]]:
        """
        Optimiza los pasos de troubleshooting según datos históricos.
        
        Args:
            problem_id: ID del problema
            customer_email: Email del cliente
            strategy: Estrategia de optimización
            
        Returns:
            Lista de pasos optimizados
        """
        # Obtener pasos base del problema
        base_steps = self._get_problem_steps(problem_id)
        
        if not base_steps:
            return []
        
        # Obtener estadísticas de pasos
        step_stats = self._get_step_statistics(problem_id, customer_email)
        
        # Aplicar estrategia de optimización
        if strategy == StepOptimizationStrategy.SUCCESS_RATE:
            optimized = self._optimize_by_success_rate(base_steps, step_stats)
        elif strategy == StepOptimizationStrategy.DURATION:
            optimized = self._optimize_by_duration(base_steps, step_stats)
        elif strategy == StepOptimizationStrategy.CUSTOMER_SATISFACTION:
            optimized = self._optimize_by_satisfaction(base_steps, step_stats)
        else:  # HYBRID
            optimized = self._optimize_hybrid(base_steps, step_stats)
        
        return optimized
    
    def predict_resolution_time(
        self,
        problem_id: str,
        customer_email: Optional[str] = None,
        technical_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predice el tiempo de resolución basado en datos históricos.
        
        Args:
            problem_id: ID del problema
            customer_email: Email del cliente
            technical_level: Nivel técnico del cliente
            
        Returns:
            Dict con predicción y confianza
        """
        # Obtener estadísticas históricas
        stats = self._get_resolution_statistics(problem_id, customer_email, technical_level)
        
        if not stats:
            return {
                "estimated_minutes": 15,
                "confidence": 0.5,
                "min_minutes": 5,
                "max_minutes": 30
            }
        
        # Calcular predicción
        avg_duration = stats.get("avg_duration_minutes", 15)
        median_duration = stats.get("median_duration_minutes", 15)
        
        # Ajustar según nivel técnico
        if technical_level:
            level_multipliers = {
                "beginner": 1.5,
                "intermediate": 1.0,
                "advanced": 0.7,
                "expert": 0.5
            }
            multiplier = level_multipliers.get(technical_level.lower(), 1.0)
            avg_duration = avg_duration * multiplier
        
        # Calcular confianza basada en cantidad de datos
        sample_size = stats.get("sample_size", 0)
        confidence = min(0.95, 0.5 + (sample_size / 100) * 0.45)
        
        return {
            "estimated_minutes": int(avg_duration),
            "confidence": round(confidence, 2),
            "min_minutes": int(stats.get("min_duration_minutes", avg_duration * 0.5)),
            "max_minutes": int(stats.get("max_duration_minutes", avg_duration * 1.5)),
            "sample_size": sample_size,
            "median_minutes": int(median_duration)
        }
    
    def get_personalized_guidance(
        self,
        problem_id: str,
        customer_email: str,
        step_number: int
    ) -> Dict[str, Any]:
        """
        Obtiene guía personalizada basada en historial del cliente.
        
        Args:
            problem_id: ID del problema
            customer_email: Email del cliente
            step_number: Número del paso
            
        Returns:
            Dict con guía personalizada
        """
        # Obtener historial del cliente
        history = self._get_customer_troubleshooting_history(customer_email, problem_id)
        
        # Obtener paso base
        step = self._get_step_details(problem_id, step_number)
        
        if not step:
            return {}
        
        # Personalizar según historial
        personalized = {
            "step_number": step_number,
            "title": step.get("title"),
            "instructions": step.get("instructions"),
            "warnings": step.get("warnings", []),
            "resources": step.get("resources", []),
            "personalization": {}
        }
        
        # Agregar personalizaciones
        if history:
            # Si el cliente ha tenido problemas con este paso antes
            failed_attempts = history.get("failed_attempts", {}).get(str(step_number), 0)
            if failed_attempts > 0:
                personalized["personalization"]["additional_help"] = True
                personalized["personalization"]["common_issues"] = history.get(
                    "common_issues", {}
                ).get(str(step_number), [])
            
            # Si el cliente completó este paso rápidamente antes
            avg_duration = history.get("step_durations", {}).get(str(step_number))
            if avg_duration and avg_duration < 60:  # Menos de 1 minuto
                personalized["personalization"]["can_skip_verification"] = True
        
        return personalized
    
    def track_step_completion(
        self,
        session_id: str,
        step_number: int,
        success: bool,
        duration_seconds: int,
        notes: Optional[str] = None
    ) -> None:
        """
        Registra la finalización de un paso para aprendizaje.
        
        Args:
            session_id: ID de la sesión
            step_number: Número del paso
            success: Si el paso fue exitoso
            duration_seconds: Duración en segundos
            notes: Notas adicionales
        """
        if not self.db:
            self.logger.warning("No database connection, skipping tracking")
            return
        
        try:
            with self.db.cursor() as cur:
                # Insertar o actualizar intento
                cur.execute("""
                    INSERT INTO support_troubleshooting_attempts (
                        session_id, step_number, success, duration_seconds, notes, attempted_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                """, (session_id, step_number, success, duration_seconds, notes))
                
                # Actualizar estadísticas del paso
                cur.execute("""
                    UPDATE support_troubleshooting_step_statistics
                    SET 
                        total_attempts = total_attempts + 1,
                        successful_attempts = successful_attempts + CASE WHEN %s THEN 1 ELSE 0 END,
                        total_duration_seconds = total_duration_seconds + %s,
                        avg_duration_seconds = (total_duration_seconds + %s) / (total_attempts + 1),
                        success_rate = (successful_attempts + CASE WHEN %s THEN 1 ELSE 0 END)::float / (total_attempts + 1),
                        updated_at = NOW()
                    WHERE problem_id = (
                        SELECT detected_problem_id 
                        FROM support_troubleshooting_sessions 
                        WHERE session_id = %s
                    ) AND step_number = %s
                """, (success, duration_seconds, duration_seconds, success, session_id, step_number))
                
                self.db.commit()
                self.logger.info(f"Tracked step completion: session={session_id}, step={step_number}, success={success}")
        except Exception as e:
            self.logger.error(f"Error tracking step completion: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
    
    def get_analytics(
        self,
        problem_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene analytics del sistema de troubleshooting.
        
        Args:
            problem_id: ID del problema (opcional, para filtrar)
            date_from: Fecha desde
            date_to: Fecha hasta
            
        Returns:
            Dict con analytics
        """
        if not self.db:
            return {"error": "No database connection"}
        
        date_from = date_from or (datetime.now() - timedelta(days=30))
        date_to = date_to or datetime.now()
        
        try:
            with self.db.cursor() as cur:
                # Estadísticas generales
                query = """
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved_sessions,
                        COUNT(*) FILTER (WHERE status = 'escalated') as escalated_sessions,
                        AVG(total_duration_seconds) as avg_duration_seconds,
                        AVG(current_step) as avg_steps_completed,
                        AVG(customer_satisfaction_score) as avg_satisfaction
                    FROM support_troubleshooting_sessions
                    WHERE started_at >= %s AND started_at <= %s
                """
                params = [date_from, date_to]
                
                if problem_id:
                    query += " AND detected_problem_id = %s"
                    params.append(problem_id)
                
                cur.execute(query, params)
                row = cur.fetchone()
                
                total = row[0] or 0
                resolved = row[1] or 0
                escalated = row[2] or 0
                
                return {
                    "period": {
                        "from": date_from.isoformat(),
                        "to": date_to.isoformat()
                    },
                    "sessions": {
                        "total": total,
                        "resolved": resolved,
                        "escalated": escalated,
                        "abandoned": total - resolved - escalated
                    },
                    "metrics": {
                        "resolution_rate": round((resolved / total * 100) if total > 0 else 0, 2),
                        "escalation_rate": round((escalated / total * 100) if total > 0 else 0, 2),
                        "avg_duration_minutes": round((row[3] or 0) / 60, 1),
                        "avg_steps_completed": round(row[4] or 0, 1),
                        "avg_satisfaction": round(row[5] or 0, 1) if row[5] else None
                    },
                    "problem_id": problem_id
                }
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}", exc_info=True)
            return {"error": str(e)}
    
    # Métodos privados de ayuda
    
    def _get_customer_history(self, customer_email: str) -> Dict[str, Any]:
        """Obtiene historial del cliente."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_tickets,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved_tickets,
                        AVG(time_to_resolution_minutes) as avg_resolution_time
                    FROM support_tickets
                    WHERE customer_email = %s
                    AND created_at >= NOW() - INTERVAL '90 days'
                """, (customer_email,))
                
                row = cur.fetchone()
                return {
                    "total_tickets": row[0] or 0,
                    "resolved_tickets": row[1] or 0,
                    "avg_resolution_time_minutes": row[2] or 0
                }
        except Exception as e:
            self.logger.error(f"Error getting customer history: {e}")
            return {}
    
    def _hybrid_detection(
        self,
        description: str,
        customer_history: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detección híbrida combinando múltiples métodos."""
        # Implementación simplificada
        # En producción, combinaría keyword matching, semantic similarity, y ML
        return {
            "problem_id": "unknown",
            "confidence": 0.5,
            "method": "hybrid",
            "alternatives": []
        }
    
    def _keyword_detection(self, description: str) -> Dict[str, Any]:
        """Detección por palabras clave."""
        # Implementación simplificada
        return {"problem_id": "unknown", "confidence": 0.3, "method": "keyword"}
    
    def _semantic_detection(self, description: str) -> Dict[str, Any]:
        """Detección por similitud semántica."""
        # Implementación simplificada
        return {"problem_id": "unknown", "confidence": 0.4, "method": "semantic"}
    
    def _ml_detection(
        self,
        description: str,
        customer_history: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detección usando machine learning."""
        # Implementación simplificada
        return {"problem_id": "unknown", "confidence": 0.6, "method": "ml"}
    
    def _llm_detection(self, description: str) -> Dict[str, Any]:
        """Detección usando LLM."""
        # Implementación simplificada
        return {"problem_id": "unknown", "confidence": 0.7, "method": "llm"}
    
    def _adjust_confidence_by_history(
        self,
        results: Dict[str, Any],
        customer_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ajusta la confianza según el historial del cliente."""
        # Si el cliente ha tenido problemas similares antes, aumentar confianza
        if customer_history.get("total_tickets", 0) > 0:
            results["confidence"] = min(0.95, results["confidence"] * 1.1)
        
        return results
    
    def _get_problem_steps(self, problem_id: str) -> List[Dict[str, Any]]:
        """Obtiene pasos base del problema."""
        # Implementación simplificada
        # En producción, vendría de la base de conocimiento
        return []
    
    def _get_step_statistics(
        self,
        problem_id: str,
        customer_email: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Obtiene estadísticas de pasos."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                query = """
                    SELECT 
                        step_number,
                        COUNT(*) as total_attempts,
                        COUNT(*) FILTER (WHERE success = true) as successful_attempts,
                        AVG(duration_seconds) as avg_duration,
                        AVG(CASE WHEN success THEN 1 ELSE 0 END) as success_rate
                    FROM support_troubleshooting_attempts
                    WHERE session_id IN (
                        SELECT session_id 
                        FROM support_troubleshooting_sessions 
                        WHERE detected_problem_id = %s
                    )
                    GROUP BY step_number
                """
                
                cur.execute(query, (problem_id,))
                rows = cur.fetchall()
                
                stats = {}
                for row in rows:
                    stats[str(row[0])] = {
                        "total_attempts": row[1] or 0,
                        "successful_attempts": row[2] or 0,
                        "avg_duration_seconds": row[3] or 0,
                        "success_rate": float(row[4] or 0)
                    }
                
                return stats
        except Exception as e:
            self.logger.error(f"Error getting step statistics: {e}")
            return {}
    
    def _optimize_by_success_rate(
        self,
        steps: List[Dict[str, Any]],
        stats: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimiza pasos por tasa de éxito."""
        # Ordenar pasos por tasa de éxito descendente
        def get_success_rate(step):
            step_num = str(step.get("step_number", 0))
            return stats.get(step_num, {}).get("success_rate", 0.5)
        
        return sorted(steps, key=get_success_rate, reverse=True)
    
    def _optimize_by_duration(
        self,
        steps: List[Dict[str, Any]],
        stats: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimiza pasos por duración."""
        # Ordenar pasos por duración ascendente (más rápidos primero)
        def get_duration(step):
            step_num = str(step.get("step_number", 0))
            return stats.get(step_num, {}).get("avg_duration_seconds", 300)
        
        return sorted(steps, key=get_duration)
    
    def _optimize_by_satisfaction(
        self,
        steps: List[Dict[str, Any]],
        stats: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimiza pasos por satisfacción del cliente."""
        # Similar a success rate pero con métricas de satisfacción
        return self._optimize_by_success_rate(steps, stats)
    
    def _optimize_hybrid(
        self,
        steps: List[Dict[str, Any]],
        stats: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimización híbrida combinando múltiples factores."""
        # Calcular score combinado para cada paso
        def get_hybrid_score(step):
            step_num = str(step.get("step_number", 0))
            step_stats = stats.get(step_num, {})
            
            success_rate = step_stats.get("success_rate", 0.5)
            avg_duration = step_stats.get("avg_duration_seconds", 300)
            
            # Score = éxito * (1 - normalización de duración)
            # Pasos con alta tasa de éxito y baja duración tienen mejor score
            duration_score = 1.0 - min(1.0, avg_duration / 600)  # Normalizar a 10 minutos
            hybrid_score = success_rate * 0.7 + duration_score * 0.3
            
            return hybrid_score
        
        return sorted(steps, key=get_hybrid_score, reverse=True)
    
    def _get_resolution_statistics(
        self,
        problem_id: str,
        customer_email: Optional[str],
        technical_level: Optional[str]
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de resolución."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                query = """
                    SELECT 
                        COUNT(*) as sample_size,
                        AVG(total_duration_seconds / 60.0) as avg_duration_minutes,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_duration_seconds / 60.0) as median_duration_minutes,
                        MIN(total_duration_seconds / 60.0) as min_duration_minutes,
                        MAX(total_duration_seconds / 60.0) as max_duration_minutes
                    FROM support_troubleshooting_sessions
                    WHERE detected_problem_id = %s
                    AND status = 'resolved'
                """
                
                params = [problem_id]
                
                if customer_email:
                    query += " AND customer_email = %s"
                    params.append(customer_email)
                
                cur.execute(query, params)
                row = cur.fetchone()
                
                if row and row[0] > 0:
                    return {
                        "sample_size": row[0] or 0,
                        "avg_duration_minutes": float(row[1] or 15),
                        "median_duration_minutes": float(row[2] or 15),
                        "min_duration_minutes": float(row[3] or 5),
                        "max_duration_minutes": float(row[4] or 30)
                    }
        except Exception as e:
            self.logger.error(f"Error getting resolution statistics: {e}")
        
        return {}
    
    def _get_customer_troubleshooting_history(
        self,
        customer_email: str,
        problem_id: str
    ) -> Dict[str, Any]:
        """Obtiene historial de troubleshooting del cliente."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT 
                        session_id,
                        current_step,
                        status,
                        total_duration_seconds
                    FROM support_troubleshooting_sessions
                    WHERE customer_email = %s
                    AND detected_problem_id = %s
                    ORDER BY started_at DESC
                    LIMIT 10
                """, (customer_email, problem_id))
                
                sessions = cur.fetchall()
                
                # Procesar sesiones para obtener estadísticas
                failed_attempts = {}
                step_durations = {}
                common_issues = {}
                
                for session in sessions:
                    session_id, current_step, status, duration = session
                    # Procesar intentos de pasos
                    cur.execute("""
                        SELECT step_number, success, duration_seconds, notes
                        FROM support_troubleshooting_attempts
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    attempts = cur.fetchall()
                    for attempt in attempts:
                        step_num, success, step_duration, notes = attempt
                        step_key = str(step_num)
                        
                        if not success:
                            failed_attempts[step_key] = failed_attempts.get(step_key, 0) + 1
                            if notes:
                                if step_key not in common_issues:
                                    common_issues[step_key] = []
                                common_issues[step_key].append(notes)
                        
                        if step_duration:
                            if step_key not in step_durations:
                                step_durations[step_key] = []
                            step_durations[step_key].append(step_duration)
                
                # Calcular promedios
                avg_durations = {}
                for step_key, durations in step_durations.items():
                    avg_durations[step_key] = sum(durations) / len(durations) if durations else 0
                
                return {
                    "total_sessions": len(sessions),
                    "failed_attempts": failed_attempts,
                    "step_durations": avg_durations,
                    "common_issues": common_issues
                }
        except Exception as e:
            self.logger.error(f"Error getting customer troubleshooting history: {e}")
            return {}
    
    def _get_step_details(self, problem_id: str, step_number: int) -> Optional[Dict[str, Any]]:
        """Obtiene detalles de un paso específico."""
        # Implementación simplificada
        # En producción, vendría de la base de conocimiento
        return None



