"""
Sistema de Predicción y Recomendaciones Inteligentes
Predice problemas antes de que ocurran y recomienda soluciones proactivas
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ProblemPrediction:
    """Predicción de un problema potencial"""
    problem_id: str
    problem_title: str
    probability: float
    confidence: float
    reasons: List[str]
    recommended_actions: List[str]
    estimated_impact: str  # low, medium, high


@dataclass
class UserPattern:
    """Patrón de comportamiento del usuario"""
    customer_email: str
    common_problems: List[Tuple[str, int]]  # (problem_id, count)
    avg_resolution_time: float
    preferred_time: Optional[str]  # hora del día preferida
    success_rate: float
    escalation_rate: float


class TroubleshootingPredictor:
    """Sistema de predicción de problemas"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.patterns_cache = {}
        self.prediction_threshold = 0.6
    
    def analyze_user_history(self, customer_email: str, days: int = 90) -> UserPattern:
        """Analiza el historial del usuario para identificar patrones"""
        if customer_email in self.patterns_cache:
            return self.patterns_cache[customer_email]
        
        if not self.db:
            return None
        
        try:
            cursor = self.db.cursor()
            
            # Obtener sesiones del usuario
            cursor.execute("""
                SELECT 
                    detected_problem_id,
                    detected_problem_title,
                    status,
                    started_at,
                    resolved_at,
                    escalated_at
                FROM support_troubleshooting_sessions
                WHERE customer_email = %s
                  AND started_at >= %s
                ORDER BY started_at DESC
            """, (customer_email, datetime.now() - timedelta(days=days)))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                return None
            
            # Analizar patrones
            problem_counts = defaultdict(int)
            resolution_times = []
            escalations = 0
            resolutions = 0
            
            for session in sessions:
                problem_id = session[0]
                status = session[2]
                started_at = session[3]
                resolved_at = session[4]
                escalated_at = session[5]
                
                if problem_id:
                    problem_counts[problem_id] += 1
                
                if status == 'resolved' and resolved_at:
                    resolution_times.append(
                        (resolved_at - started_at).total_seconds() / 60
                    )
                    resolutions += 1
                elif status == 'escalated' or escalated_at:
                    escalations += 1
            
            # Calcular métricas
            common_problems = sorted(
                problem_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            avg_resolution_time = (
                statistics.mean(resolution_times) if resolution_times else 0
            )
            
            total_sessions = len(sessions)
            success_rate = (resolutions / total_sessions * 100) if total_sessions > 0 else 0
            escalation_rate = (escalations / total_sessions * 100) if total_sessions > 0 else 0
            
            pattern = UserPattern(
                customer_email=customer_email,
                common_problems=common_problems,
                avg_resolution_time=avg_resolution_time,
                preferred_time=None,  # Se puede calcular analizando horas
                success_rate=success_rate,
                escalation_rate=escalation_rate
            )
            
            self.patterns_cache[customer_email] = pattern
            cursor.close()
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analizando historial de usuario: {e}")
            return None
    
    def predict_next_problem(
        self,
        customer_email: str,
        current_context: Optional[Dict[str, Any]] = None
    ) -> Optional[ProblemPrediction]:
        """Predice el siguiente problema probable del usuario"""
        pattern = self.analyze_user_history(customer_email)
        
        if not pattern or not pattern.common_problems:
            return None
        
        # El problema más común tiene mayor probabilidad
        most_common = pattern.common_problems[0]
        problem_id, count = most_common
        
        # Calcular probabilidad basada en frecuencia y tiempo desde última ocurrencia
        total_problems = sum(c for _, c in pattern.common_problems)
        base_probability = count / total_problems if total_problems > 0 else 0
        
        # Ajustar por tiempo (más reciente = mayor probabilidad)
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT started_at
                    FROM support_troubleshooting_sessions
                    WHERE customer_email = %s
                      AND detected_problem_id = %s
                    ORDER BY started_at DESC
                    LIMIT 1
                """, (customer_email, problem_id))
                
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    last_occurrence = result[0]
                    days_since = (datetime.now() - last_occurrence).days
                    
                    # Si fue hace menos de 7 días, aumentar probabilidad
                    if days_since < 7:
                        base_probability *= 1.2
                    elif days_since > 30:
                        base_probability *= 0.8
                        
            except Exception as e:
                logger.error(f"Error calculando probabilidad: {e}")
        
        if base_probability < self.prediction_threshold:
            return None
        
        # Obtener título del problema
        problem_title = problem_id
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT detected_problem_title
                    FROM support_troubleshooting_sessions
                    WHERE detected_problem_id = %s
                    LIMIT 1
                """, (problem_id,))
                
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    problem_title = result[0] or problem_id
            except Exception:
                pass
        
        # Generar razones y acciones recomendadas
        reasons = [
            f"Este problema ha ocurrido {count} veces en tu historial",
            f"Tasa de éxito previa: {pattern.success_rate:.1f}%"
        ]
        
        recommended_actions = [
            "Revisar la guía de troubleshooting para este problema",
            "Verificar si hay actualizaciones pendientes",
            "Contactar soporte preventivamente si el problema persiste"
        ]
        
        # Determinar impacto estimado
        if pattern.escalation_rate > 50:
            estimated_impact = "high"
        elif pattern.escalation_rate > 30:
            estimated_impact = "medium"
        else:
            estimated_impact = "low"
        
        return ProblemPrediction(
            problem_id=problem_id,
            problem_title=problem_title,
            probability=min(base_probability * 100, 100),
            confidence=min(len(pattern.common_problems) * 20, 100),
            reasons=reasons,
            recommended_actions=recommended_actions,
            estimated_impact=estimated_impact
        )
    
    def get_proactive_recommendations(
        self,
        customer_email: str
    ) -> List[Dict[str, Any]]:
        """Obtiene recomendaciones proactivas para el usuario"""
        pattern = self.analyze_user_history(customer_email)
        
        if not pattern:
            return []
        
        recommendations = []
        
        # Recomendación basada en problemas frecuentes
        if pattern.common_problems:
            most_common = pattern.common_problems[0]
            recommendations.append({
                "type": "preventive",
                "title": f"Problema frecuente: {most_common[0]}",
                "description": f"Este problema ha ocurrido {most_common[1]} veces. Considera revisar la guía preventiva.",
                "priority": "high" if most_common[1] >= 3 else "medium",
                "action": "view_preventive_guide"
            })
        
        # Recomendación basada en tasa de éxito
        if pattern.success_rate < 50:
            recommendations.append({
                "type": "improvement",
                "title": "Mejora tu tasa de resolución",
                "description": f"Tu tasa de éxito actual es {pattern.success_rate:.1f}%. Te recomendamos seguir las guías paso a paso.",
                "priority": "medium",
                "action": "view_tips"
            })
        
        # Recomendación basada en tiempo de resolución
        if pattern.avg_resolution_time > 30:
            recommendations.append({
                "type": "efficiency",
                "title": "Optimiza tu tiempo de resolución",
                "description": f"El tiempo promedio de resolución es {pattern.avg_resolution_time:.1f} minutos. Revisa nuestras guías rápidas.",
                "priority": "low",
                "action": "view_quick_guides"
            })
        
        return recommendations


class TroubleshootingRecommender:
    """Sistema de recomendaciones inteligentes"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.predictor = TroubleshootingPredictor(db_connection)
    
    def recommend_solutions(
        self,
        problem_description: str,
        customer_email: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recomienda soluciones basadas en descripción y contexto"""
        recommendations = []
        
        # Si hay historial del usuario, usar predicción
        if customer_email:
            prediction = self.predictor.predict_next_problem(
                customer_email,
                context
            )
            
            if prediction:
                recommendations.append({
                    "type": "predicted",
                    "problem_id": prediction.problem_id,
                    "problem_title": prediction.problem_title,
                    "confidence": prediction.confidence,
                    "reasons": prediction.reasons,
                    "actions": prediction.recommended_actions
                })
        
        # Buscar problemas similares en la base de datos
        if self.db:
            try:
                cursor = self.db.cursor()
                
                # Búsqueda simple por palabras clave
                keywords = problem_description.lower().split()[:5]
                
                cursor.execute("""
                    SELECT DISTINCT
                        detected_problem_id,
                        detected_problem_title,
                        COUNT(*) as frequency,
                        AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_at, escalated_at, NOW()) - started_at)) / 60) as avg_time
                    FROM support_troubleshooting_sessions
                    WHERE LOWER(description) LIKE ANY(ARRAY[%s])
                       OR LOWER(detected_problem_title) LIKE ANY(ARRAY[%s])
                    GROUP BY detected_problem_id, detected_problem_title
                    ORDER BY frequency DESC
                    LIMIT 3
                """, (
                    [f'%{kw}%' for kw in keywords],
                    [f'%{kw}%' for kw in keywords]
                ))
                
                similar = cursor.fetchall()
                cursor.close()
                
                for prob_id, prob_title, freq, avg_time in similar:
                    recommendations.append({
                        "type": "similar",
                        "problem_id": prob_id,
                        "problem_title": prob_title,
                        "frequency": freq,
                        "avg_resolution_time": round(avg_time, 1) if avg_time else None,
                        "confidence": min(freq * 10, 100)
                    })
                    
            except Exception as e:
                logger.error(f"Error buscando problemas similares: {e}")
        
        return recommendations
    
    def get_personalized_guide(
        self,
        problem_id: str,
        customer_email: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene una guía personalizada basada en el historial del usuario"""
        pattern = self.predictor.analyze_user_history(customer_email)
        
        if not pattern:
            return None
        
        # Buscar intentos previos de este problema
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT 
                        a.step_number,
                        a.success,
                        COUNT(*) as attempts
                    FROM support_troubleshooting_sessions s
                    JOIN support_troubleshooting_attempts a ON s.session_id = a.session_id
                    WHERE s.customer_email = %s
                      AND s.detected_problem_id = %s
                    GROUP BY a.step_number, a.success
                    ORDER BY a.step_number
                """, (customer_email, problem_id))
                
                attempts = cursor.fetchall()
                cursor.close()
                
                # Identificar pasos problemáticos
                problematic_steps = []
                for step_num, success, count in attempts:
                    if not success and count >= 2:
                        problematic_steps.append({
                            "step_number": step_num,
                            "failure_count": count
                        })
                
                if problematic_steps:
                    return {
                        "personalized": True,
                        "problematic_steps": problematic_steps,
                        "recommendations": [
                            f"El paso {ps['step_number']} ha fallado {ps['failure_count']} veces. Revisa cuidadosamente las instrucciones.",
                            "Considera contactar soporte antes de intentar estos pasos nuevamente."
                        ]
                    }
                    
            except Exception as e:
                logger.error(f"Error obteniendo guía personalizada: {e}")
        
        return None


class TroubleshootingLearningEngine:
    """Motor de aprendizaje para mejorar las guías automáticamente"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
    
    def analyze_step_effectiveness(self, problem_id: str) -> Dict[str, Any]:
        """Analiza la efectividad de cada paso de una guía"""
        if not self.db:
            return {}
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT 
                    a.step_number,
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN a.success = true THEN 1 END) as successful,
                    COUNT(CASE WHEN a.success = false THEN 1 END) as failed,
                    AVG(EXTRACT(EPOCH FROM (a.completed_at - a.started_at))) as avg_duration_seconds
                FROM support_troubleshooting_sessions s
                JOIN support_troubleshooting_attempts a ON s.session_id = a.session_id
                WHERE s.detected_problem_id = %s
                GROUP BY a.step_number
                ORDER BY a.step_number
            """, (problem_id,))
            
            steps = cursor.fetchall()
            cursor.close()
            
            analysis = {
                "problem_id": problem_id,
                "steps": [],
                "overall_success_rate": 0,
                "recommendations": []
            }
            
            total_success = 0
            total_attempts = 0
            
            for step_num, total, successful, failed, avg_duration in steps:
                success_rate = (successful / total * 100) if total > 0 else 0
                total_success += successful
                total_attempts += total
                
                step_analysis = {
                    "step_number": step_num,
                    "total_attempts": total,
                    "success_rate": round(success_rate, 2),
                    "avg_duration_seconds": round(avg_duration, 2) if avg_duration else None,
                    "needs_improvement": success_rate < 70
                }
                
                analysis["steps"].append(step_analysis)
                
                if success_rate < 70:
                    analysis["recommendations"].append(
                        f"El paso {step_num} tiene una tasa de éxito del {success_rate:.1f}%. "
                        f"Considera revisar las instrucciones o agregar más detalles."
                    )
            
            if total_attempts > 0:
                analysis["overall_success_rate"] = round(
                    (total_success / total_attempts) * 100, 2
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando efectividad de pasos: {e}")
            return {}
    
    def suggest_guide_improvements(self, problem_id: str) -> List[str]:
        """Sugiere mejoras para una guía basándose en datos"""
        analysis = self.analyze_step_effectiveness(problem_id)
        
        if not analysis:
            return []
        
        suggestions = []
        
        # Sugerencias basadas en tasa de éxito
        if analysis["overall_success_rate"] < 70:
            suggestions.append(
                f"La guía tiene una tasa de éxito del {analysis['overall_success_rate']:.1f}%. "
                "Considera simplificar los pasos o agregar más contexto."
            )
        
        # Sugerencias por paso problemático
        for step in analysis["steps"]:
            if step["needs_improvement"]:
                suggestions.append(
                    f"Paso {step['step_number']}: Tasa de éxito {step['success_rate']:.1f}%. "
                    "Revisar claridad de instrucciones."
                )
        
        return suggestions



