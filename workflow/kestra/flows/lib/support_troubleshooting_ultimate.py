"""
Sistema Ultimate de Troubleshooting - Todas las Funcionalidades Avanzadas.

Aprovecha TODAS las funcionalidades del schema completo (8783 líneas):
- Tests automatizados
- Monitoreo avanzado
- Alertas inteligentes
- Documentación automática
- Versionado de schema
- Métricas de SLA avanzadas
- Y mucho más...
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class TroubleshootingUltimate:
    """Sistema ultimate que integra todas las funcionalidades avanzadas."""
    
    def __init__(self, db_connection):
        """Inicializa el sistema ultimate."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def run_test_suite(
        self,
        suite_name: Optional[str] = None,
        test_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una suite de tests automatizados.
        
        Usa la función: run_test_suite()
        
        Args:
            suite_name: Nombre de la suite (opcional)
            test_names: Lista de nombres de tests específicos (opcional)
            
        Returns:
            Dict con resultados de los tests
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                if suite_name:
                    cur.execute("""
                        SELECT * FROM run_test_suite(
                            p_suite_name := %s
                        )
                    """, (suite_name,))
                elif test_names:
                    cur.execute("""
                        SELECT * FROM run_test_suite(
                            p_test_names := %s
                        )
                    """, (test_names,))
                else:
                    cur.execute("SELECT * FROM run_test_suite()")
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "suite_name": suite_name or "all",
                        "total_tests": row[0] or 0,
                        "passed_tests": row[1] or 0,
                        "failed_tests": row[2] or 0,
                        "test_results": row[3] if len(row) > 3 and isinstance(row[3], list) else [],
                        "execution_time_seconds": float(row[4]) if len(row) > 4 and row[4] else 0.0,
                        "success_rate": round((row[1] or 0) / (row[0] or 1) * 100, 2) if row[0] else 0.0
                    }
        except Exception as e:
            self.logger.error(f"Error running test suite: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "Test suite not available"}
    
    def evaluate_smart_alerts(
        self,
        alert_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evalúa y dispara alertas inteligentes.
        
        Usa la función: evaluate_smart_alerts()
        
        Args:
            alert_names: Lista de nombres de alertas específicas (opcional)
            
        Returns:
            Lista de alertas disparadas
        """
        if not self.db:
            return []
        
        try:
            with self.db.cursor() as cur:
                cur.execute("SELECT * FROM evaluate_smart_alerts()")
                rows = cur.fetchall()
                
                alerts = []
                for row in rows:
                    # Filtrar por nombres si se especifican
                    if alert_names and row[0] not in alert_names:
                        continue
                    
                    if row[2]:  # triggered
                        alerts.append({
                            "alert_name": row[0],
                            "severity": row[1],
                            "triggered": True,
                            "current_value": float(row[3]) if row[3] else None,
                            "threshold_value": float(row[4]) if row[4] else None,
                            "triggered_at": datetime.now().isoformat()
                        })
                        
                        # Actualizar última vez que se disparó
                        cur.execute("""
                            UPDATE support_troubleshooting_smart_alerts
                            SET last_triggered_at = NOW(),
                                trigger_count = trigger_count + 1
                            WHERE alert_name = %s
                        """, (row[0],))
                
                self.db.commit()
                return alerts
        except Exception as e:
            self.logger.error(f"Error evaluating smart alerts: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return []
    
    def get_monitoring_metrics(
        self,
        metric_names: Optional[List[str]] = None,
        hours: int = 24
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene métricas de monitoreo avanzado.
        
        Args:
            metric_names: Lista de nombres de métricas (opcional)
            hours: Número de horas hacia atrás
            
        Returns:
            Dict con métricas agrupadas por nombre
        """
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                query = """
                    SELECT 
                        metric_name,
                        metric_type,
                        metric_value,
                        labels,
                        timestamp
                    FROM support_troubleshooting_monitoring
                    WHERE timestamp >= NOW() - INTERVAL '%s hours'
                """
                
                params = [hours]
                
                if metric_names:
                    query += " AND metric_name = ANY(%s)"
                    params.append(metric_names)
                
                query += " ORDER BY timestamp DESC"
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                metrics = {}
                for row in rows:
                    metric_name = row[0]
                    if metric_name not in metrics:
                        metrics[metric_name] = []
                    
                    metrics[metric_name].append({
                        "type": row[1],
                        "value": float(row[2]) if row[2] else 0.0,
                        "labels": row[3] if row[3] else {},
                        "timestamp": row[4].isoformat() if row[4] else None
                    })
                
                return metrics
        except Exception as e:
            self.logger.error(f"Error getting monitoring metrics: {e}", exc_info=True)
            return {}
    
    def calculate_sla_metrics_advanced(
        self,
        sla_id: int,
        metric_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas avanzadas de SLA.
        
        Usa la función: calculate_sla_metrics()
        
        Args:
            sla_id: ID del SLA
            metric_date: Fecha para calcular métricas (default: hoy)
            
        Returns:
            Dict con métricas avanzadas de SLA
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                metric_date = metric_date or datetime.now().date()
                
                cur.execute("""
                    SELECT * FROM calculate_sla_metrics(
                        p_sla_id := %s,
                        p_metric_date := %s
                    )
                """, (sla_id, metric_date))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "sla_name": row[0],
                        "metric_date": row[1].isoformat() if row[1] else None,
                        "target_resolution_time_minutes": int(row[2]) if row[2] else None,
                        "actual_resolution_time_minutes": float(row[3]) if row[3] else None,
                        "target_success_rate": float(row[4]) if row[4] else None,
                        "actual_success_rate": float(row[5]) if row[5] else None,
                        "target_availability": float(row[6]) if row[6] else None,
                        "actual_availability": float(row[7]) if row[7] else None,
                        "sla_compliant": row[8] if len(row) > 8 else None,
                        "performance": {
                            "resolution_time_vs_target": round(
                                (float(row[3]) or 0) / (int(row[2]) or 1) * 100, 2
                            ) if row[2] and row[3] else None,
                            "success_rate_vs_target": round(
                                (float(row[5]) or 0) / (float(row[4]) or 1) * 100, 2
                            ) if row[4] and row[5] else None,
                            "availability_vs_target": round(
                                (float(row[7]) or 0) / (float(row[6]) or 1) * 100, 2
                            ) if row[6] and row[7] else None
                        }
                    }
        except Exception as e:
            self.logger.error(f"Error calculating SLA metrics: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "SLA metrics not available"}
    
    def generate_schema_documentation(
        self,
        include_examples: bool = True,
        format_type: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Genera documentación automática del schema.
        
        Usa la función: generate_schema_documentation()
        
        Args:
            include_examples: Incluir ejemplos en la documentación
            format_type: Formato (markdown, html, json)
            
        Returns:
            Dict con documentación generada
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM generate_schema_documentation(
                        p_include_examples := %s,
                        p_format := %s
                    )
                """, (include_examples, format_type))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "format": format_type,
                        "generated_at": datetime.now().isoformat(),
                        "documentation": row[0] if isinstance(row[0], str) else str(row[0]),
                        "tables_documented": row[1] if len(row) > 1 else 0,
                        "functions_documented": row[2] if len(row) > 2 else 0,
                        "views_documented": row[3] if len(row) > 3 else 0
                    }
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "Documentation generation not available"}
    
    def register_schema_version(
        self,
        version_number: str,
        description: str,
        migration_script: Optional[str] = None,
        rollback_script: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra una nueva versión del schema.
        
        Usa la función: register_schema_version()
        
        Args:
            version_number: Número de versión (ej: "3.1.0")
            description: Descripción de la versión
            migration_script: Script de migración (opcional)
            rollback_script: Script de rollback (opcional)
            
        Returns:
            Dict con información de la versión registrada
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT register_schema_version(
                        p_version_number := %s,
                        p_description := %s,
                        p_migration_script := %s,
                        p_rollback_script := %s
                    )
                """, (version_number, description, migration_script, rollback_script))
                
                version_id = cur.fetchone()[0]
                self.db.commit()
                
                return {
                    "success": True,
                    "version_id": version_id,
                    "version_number": version_number,
                    "description": description,
                    "registered_at": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error registering schema version: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return {"error": str(e)}
    
    def get_system_health(
        self
    ) -> Dict[str, Any]:
        """
        Obtiene el estado de salud completo del sistema.
        
        Returns:
            Dict con estado de salud de todos los componentes
        """
        if not self.db:
            return {"error": "No database connection", "status": "unhealthy"}
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {}
        }
        
        try:
            # Verificar base de datos
            with self.db.cursor() as cur:
                cur.execute("SELECT 1")
                health["components"]["database"] = {
                    "status": "healthy",
                    "response_time_ms": 0  # Simplificado
                }
        except Exception as e:
            health["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"
        
        # Verificar tests
        try:
            test_results = self.run_test_suite()
            if test_results.get("success_rate", 0) >= 95:
                health["components"]["tests"] = {
                    "status": "healthy",
                    "success_rate": test_results.get("success_rate", 0)
                }
            else:
                health["components"]["tests"] = {
                    "status": "degraded",
                    "success_rate": test_results.get("success_rate", 0)
                }
                health["status"] = "degraded"
        except Exception as e:
            health["components"]["tests"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        # Verificar alertas activas
        try:
            alerts = self.evaluate_smart_alerts()
            critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
            
            if critical_alerts:
                health["components"]["alerts"] = {
                    "status": "unhealthy",
                    "critical_alerts": len(critical_alerts)
                }
                health["status"] = "unhealthy"
            else:
                health["components"]["alerts"] = {
                    "status": "healthy",
                    "active_alerts": len(alerts)
                }
        except Exception as e:
            health["components"]["alerts"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        # Verificar métricas de monitoreo
        try:
            metrics = self.get_monitoring_metrics(hours=1)
            health["components"]["monitoring"] = {
                "status": "healthy",
                "metrics_count": sum(len(v) for v in metrics.values())
            }
        except Exception as e:
            health["components"]["monitoring"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        return health
    
    def create_smart_alert(
        self,
        alert_name: str,
        alert_condition: str,
        severity: str = "warning",
        threshold_value: Optional[float] = None,
        evaluation_interval_seconds: int = 60,
        cooldown_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Crea una nueva alerta inteligente.
        
        Args:
            alert_name: Nombre de la alerta
            alert_condition: Condición SQL que debe evaluarse
            severity: Severidad (info, warning, critical)
            threshold_value: Valor umbral (opcional)
            evaluation_interval_seconds: Intervalo de evaluación
            cooldown_seconds: Tiempo de cooldown entre disparos
            
        Returns:
            Dict con información de la alerta creada
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_troubleshooting_smart_alerts (
                        alert_name,
                        alert_condition,
                        severity,
                        threshold_value,
                        evaluation_interval_seconds,
                        cooldown_seconds
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (
                    alert_name,
                    alert_condition,
                    severity,
                    threshold_value,
                    evaluation_interval_seconds,
                    cooldown_seconds
                ))
                
                row = cur.fetchone()
                self.db.commit()
                
                return {
                    "success": True,
                    "alert_id": row[0],
                    "alert_name": alert_name,
                    "created_at": row[1].isoformat() if row[1] else None
                }
        except Exception as e:
            self.logger.error(f"Error creating smart alert: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return {"error": str(e)}
    
    def record_monitoring_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_type: str = "gauge",
        labels: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 3600
    ) -> bool:
        """
        Registra una métrica de monitoreo.
        
        Args:
            metric_name: Nombre de la métrica
            metric_value: Valor de la métrica
            metric_type: Tipo (counter, gauge, histogram, summary)
            labels: Etiquetas adicionales
            ttl_seconds: Tiempo de vida en segundos
            
        Returns:
            True si se registró exitosamente
        """
        if not self.db:
            return False
        
        try:
            import json
            
            with self.db.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_troubleshooting_monitoring (
                        metric_name,
                        metric_type,
                        metric_value,
                        labels,
                        ttl_seconds
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    metric_name,
                    metric_type,
                    metric_value,
                    json.dumps(labels) if labels else "{}",
                    ttl_seconds
                ))
                
                self.db.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error recording monitoring metric: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return False



