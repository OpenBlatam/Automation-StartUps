"""
Integración Avanzada con Funciones ML del Schema de Troubleshooting.

Aprovecha todas las funciones avanzadas del schema:
- Predicción de resultados
- Detección de anomalías
- Generación de alertas
- Búsqueda de problemas similares
- Reportes ejecutivos
- Analytics avanzadas
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TroubleshootingMLIntegration:
    """Integración con funciones ML del schema de troubleshooting."""
    
    def __init__(self, db_connection):
        """Inicializa la integración."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def predict_outcome(
        self,
        problem_description: str,
        customer_email: Optional[str] = None,
        detected_problem_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predice el resultado de troubleshooting usando ML.
        
        Usa la función: predict_troubleshooting_outcome()
        
        Args:
            problem_description: Descripción del problema
            customer_email: Email del cliente
            detected_problem_id: ID del problema detectado
            
        Returns:
            Dict con predicción y confianza
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM predict_troubleshooting_outcome(
                        p_problem_description := %s,
                        p_customer_email := %s,
                        p_detected_problem_id := %s
                    )
                """, (problem_description, customer_email, detected_problem_id))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "predicted_outcome": row[0],  # 'resolved', 'escalated', 'abandoned'
                        "confidence": float(row[1]) if row[1] else 0.0,
                        "estimated_duration_minutes": int(row[2]) if row[2] else None,
                        "estimated_steps": int(row[3]) if row[3] else None,
                        "similar_cases_count": int(row[4]) if row[4] else 0,
                        "risk_factors": row[5] if row[5] else []
                    }
        except Exception as e:
            self.logger.error(f"Error predicting outcome: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No prediction available"}
    
    def detect_anomalies(
        self,
        session_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en sesiones de troubleshooting.
        
        Usa la función: detect_troubleshooting_anomalies()
        
        Args:
            session_id: ID de sesión específica (opcional)
            date_from: Fecha desde
            date_to: Fecha hasta
            
        Returns:
            Lista de anomalías detectadas
        """
        if not self.db:
            return []
        
        try:
            with self.db.cursor() as cur:
                if session_id:
                    cur.execute("""
                        SELECT * FROM detect_troubleshooting_anomalies(
                            p_session_id := %s
                        )
                    """, (session_id,))
                else:
                    date_from = date_from or (datetime.now() - timedelta(days=7))
                    date_to = date_to or datetime.now()
                    
                    cur.execute("""
                        SELECT * FROM detect_troubleshooting_anomalies(
                            p_date_from := %s,
                            p_date_to := %s
                        )
                    """, (date_from, date_to))
                
                rows = cur.fetchall()
                
                anomalies = []
                for row in rows:
                    anomalies.append({
                        "session_id": row[0],
                        "anomaly_type": row[1],  # 'duration', 'steps', 'failure_rate', etc.
                        "severity": row[2],  # 'low', 'medium', 'high', 'critical'
                        "description": row[3],
                        "detected_at": row[4],
                        "metadata": row[5] if len(row) > 5 else {}
                    })
                
                return anomalies
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}", exc_info=True)
            return []
    
    def generate_alerts(
        self,
        alert_types: Optional[List[str]] = None,
        severity_threshold: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Genera alertas automáticas basadas en métricas.
        
        Usa la función: generate_troubleshooting_alerts()
        
        Args:
            alert_types: Tipos de alertas a generar (None = todos)
            severity_threshold: Umbral de severidad mínimo
            
        Returns:
            Lista de alertas generadas
        """
        if not self.db:
            return []
        
        try:
            with self.db.cursor() as cur:
                if alert_types:
                    cur.execute("""
                        SELECT * FROM generate_troubleshooting_alerts(
                            p_alert_types := %s,
                            p_severity_threshold := %s
                        )
                    """, (alert_types, severity_threshold))
                else:
                    cur.execute("""
                        SELECT * FROM generate_troubleshooting_alerts(
                            p_severity_threshold := %s
                        )
                    """, (severity_threshold,))
                
                rows = cur.fetchall()
                
                alerts = []
                for row in rows:
                    alerts.append({
                        "alert_id": row[0],
                        "alert_type": row[1],
                        "severity": row[2],
                        "title": row[3],
                        "description": row[4],
                        "affected_sessions": row[5] if len(row) > 5 else [],
                        "recommended_action": row[6] if len(row) > 6 else None,
                        "generated_at": row[7] if len(row) > 7 else datetime.now()
                    })
                
                return alerts
        except Exception as e:
            self.logger.error(f"Error generating alerts: {e}", exc_info=True)
            return []
    
    def find_similar_problems(
        self,
        problem_description: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Encuentra problemas similares usando búsqueda full-text.
        
        Usa la función: find_similar_troubleshooting_problems()
        
        Args:
            problem_description: Descripción del problema
            limit: Número máximo de resultados
            
        Returns:
            Lista de problemas similares
        """
        if not self.db:
            return []
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM find_similar_troubleshooting_problems(
                        p_problem_description := %s,
                        p_limit := %s
                    )
                """, (problem_description, limit))
                
                rows = cur.fetchall()
                
                similar = []
                for row in rows:
                    similar.append({
                        "session_id": row[0],
                        "problem_description": row[1],
                        "detected_problem_title": row[2],
                        "status": row[3],
                        "resolved_at": row[4],
                        "similarity_score": float(row[5]) if row[5] else 0.0
                    })
                
                return similar
        except Exception as e:
            self.logger.error(f"Error finding similar problems: {e}", exc_info=True)
            return []
    
    def get_executive_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        Genera reporte ejecutivo completo.
        
        Usa la función: generate_troubleshooting_executive_report()
        
        Args:
            date_from: Fecha desde
            date_to: Fecha hasta
            include_trends: Incluir análisis de tendencias
            
        Returns:
            Dict con reporte ejecutivo
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                date_from = date_from or (datetime.now() - timedelta(days=30))
                date_to = date_to or datetime.now()
                
                cur.execute("""
                    SELECT * FROM generate_troubleshooting_executive_report(
                        p_date_from := %s,
                        p_date_to := %s,
                        p_include_trends := %s
                    )
                """, (date_from, date_to, include_trends))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "period": {
                            "from": date_from.isoformat(),
                            "to": date_to.isoformat()
                        },
                        "summary": row[0] if isinstance(row[0], dict) else {},
                        "metrics": row[1] if len(row) > 1 and isinstance(row[1], dict) else {},
                        "trends": row[2] if len(row) > 2 and include_trends else None,
                        "top_problems": row[3] if len(row) > 3 else [],
                        "recommendations": row[4] if len(row) > 4 else []
                    }
        except Exception as e:
            self.logger.error(f"Error generating executive report: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No report available"}
    
    def get_problem_performance_report(
        self,
        problem_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de performance para un problema específico.
        
        Usa la función: generate_problem_performance_report()
        
        Args:
            problem_id: ID del problema
            date_from: Fecha desde
            date_to: Fecha hasta
            
        Returns:
            Dict con reporte de performance
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                date_from = date_from or (datetime.now() - timedelta(days=30))
                date_to = date_to or datetime.now()
                
                cur.execute("""
                    SELECT * FROM generate_problem_performance_report(
                        p_problem_id := %s,
                        p_date_from := %s,
                        p_date_to := %s
                    )
                """, (problem_id, date_from, date_to))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "problem_id": problem_id,
                        "period": {
                            "from": date_from.isoformat(),
                            "to": date_to.isoformat()
                        },
                        "performance_metrics": row[0] if isinstance(row[0], dict) else {},
                        "step_analysis": row[1] if len(row) > 1 else [],
                        "common_issues": row[2] if len(row) > 2 else [],
                        "improvement_suggestions": row[3] if len(row) > 3 else []
                    }
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No report available"}
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas en tiempo real.
        
        Usa la vista: vw_troubleshooting_realtime_metrics
        
        Returns:
            Dict con métricas en tiempo real
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("SELECT * FROM vw_troubleshooting_realtime_metrics")
                row = cur.fetchone()
                
                if row:
                    return {
                        "active_sessions": row[0] or 0,
                        "sessions_today": row[1] or 0,
                        "resolved_today": row[2] or 0,
                        "escalated_today": row[3] or 0,
                        "avg_resolution_time_minutes": float(row[4]) if row[4] else 0.0,
                        "resolution_rate": float(row[5]) if row[5] else 0.0,
                        "top_problems": row[6] if len(row) > 6 else [],
                        "last_updated": datetime.now().isoformat()
                    }
        except Exception as e:
            self.logger.error(f"Error getting realtime metrics: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No metrics available"}
    
    def get_daily_stats(
        self,
        days: int = 30,
        refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas diarias desde la vista materializada.
        
        Usa la vista: mv_troubleshooting_daily_stats
        
        Args:
            days: Número de días hacia atrás
            refresh: Si refrescar la vista materializada primero
            
        Returns:
            Lista de estadísticas diarias
        """
        if not self.db:
            return []
        
        try:
            if refresh:
                with self.db.cursor() as cur:
                    cur.execute("SELECT refresh_troubleshooting_daily_stats()")
                    self.db.commit()
            
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM mv_troubleshooting_daily_stats
                    WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                    ORDER BY date DESC
                """, (days,))
                
                rows = cur.fetchall()
                
                stats = []
                for row in rows:
                    stats.append({
                        "date": row[0].isoformat() if row[0] else None,
                        "total_sessions": row[1] or 0,
                        "resolved_sessions": row[2] or 0,
                        "escalated_sessions": row[3] or 0,
                        "in_progress_sessions": row[4] or 0,
                        "avg_duration_seconds": float(row[5]) if row[5] else 0.0,
                        "avg_step_duration_seconds": float(row[6]) if row[6] else 0.0,
                        "unique_customers": row[7] or 0,
                        "unique_problems": row[8] or 0,
                        "problem_distribution": row[9] if len(row) > 9 else {}
                    })
                
                return stats
        except Exception as e:
            self.logger.error(f"Error getting daily stats: {e}", exc_info=True)
            return []
    
    def get_recommendations(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones inteligentes para una sesión.
        
        Usa la función: get_troubleshooting_recommendations()
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Lista de recomendaciones
        """
        if not self.db:
            return []
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM get_troubleshooting_recommendations(
                        p_session_id := %s
                    )
                """, (session_id,))
                
                rows = cur.fetchall()
                
                recommendations = []
                for row in rows:
                    recommendations.append({
                        "recommendation_type": row[0],
                        "priority": row[1],
                        "title": row[2],
                        "description": row[3],
                        "action": row[4] if len(row) > 4 else None,
                        "confidence": float(row[5]) if len(row) > 5 and row[5] else 0.0
                    })
                
                return recommendations
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}", exc_info=True)
            return []
    
    def detect_trends(
        self,
        problem_id: Optional[str] = None,
        weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Detecta tendencias temporales en problemas.
        
        Usa la función: detect_troubleshooting_trends()
        
        Args:
            problem_id: ID del problema (opcional)
            weeks: Número de semanas a analizar
            
        Returns:
            Dict con tendencias detectadas
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                if problem_id:
                    cur.execute("""
                        SELECT * FROM detect_troubleshooting_trends(
                            p_problem_id := %s,
                            p_weeks := %s
                        )
                    """, (problem_id, weeks))
                else:
                    cur.execute("""
                        SELECT * FROM detect_troubleshooting_trends(
                            p_weeks := %s
                        )
                    """, (weeks,))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "trends": row[0] if isinstance(row[0], list) else [],
                        "significant_changes": row[1] if len(row) > 1 else [],
                        "predictions": row[2] if len(row) > 2 else {},
                        "analysis_period_weeks": weeks
                    }
        except Exception as e:
            self.logger.error(f"Error detecting trends: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No trends available"}
    
    def get_cache(
        self,
        cache_key: str
    ) -> Optional[Any]:
        """
        Obtiene valor del cache.
        
        Usa la función: get_troubleshooting_cache()
        
        Args:
            cache_key: Clave del cache
            
        Returns:
            Valor del cache o None
        """
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT get_troubleshooting_cache(p_key := %s)
                """, (cache_key,))
                
                row = cur.fetchone()
                return row[0] if row and row[0] else None
        except Exception as e:
            self.logger.error(f"Error getting cache: {e}", exc_info=True)
            return None
    
    def set_cache(
        self,
        cache_key: str,
        cache_value: Any,
        ttl_seconds: int = 3600
    ) -> bool:
        """
        Guarda valor en cache.
        
        Usa la función: set_troubleshooting_cache()
        
        Args:
            cache_key: Clave del cache
            cache_value: Valor a guardar
            ttl_seconds: Tiempo de vida en segundos
            
        Returns:
            True si se guardó exitosamente
        """
        if not self.db:
            return False
        
        try:
            import json
            
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT set_troubleshooting_cache(
                        p_key := %s,
                        p_value := %s,
                        p_ttl_seconds := %s
                    )
                """, (cache_key, json.dumps(cache_value), ttl_seconds))
                
                self.db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error setting cache: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return False



