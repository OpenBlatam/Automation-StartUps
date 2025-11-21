"""
Sistema Enterprise de Troubleshooting - Funcionalidades Avanzadas.

Aprovecha todas las funcionalidades enterprise del schema:
- Sistema de API keys y autenticación
- SLAs (Service Level Agreements) y cumplimiento
- Escalación automática basada en reglas
- Métricas de calidad y performance
- Reporting avanzado
- Mantenimiento automático
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)


class TroubleshootingEnterprise:
    """Sistema enterprise de troubleshooting con funcionalidades avanzadas."""
    
    def __init__(self, db_connection):
        """Inicializa el sistema enterprise."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate_api_key(
        self,
        api_key: str,
        ip_address: Optional[str] = None,
        origin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida una API key.
        
        Usa la función: validate_api_key()
        
        Args:
            api_key: API key a validar
            ip_address: Dirección IP del cliente
            origin: Origen de la petición
            
        Returns:
            Dict con resultado de validación
        """
        if not self.db:
            return {"is_valid": False, "error": "No database connection"}
        
        try:
            # Hash de la API key
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM validate_api_key(
                        p_api_key_hash := %s,
                        p_ip_address := %s::INET,
                        p_origin := %s
                    )
                """, (api_key_hash, ip_address, origin))
                
                row = cur.fetchone()
                
                if row and row[0]:  # is_valid
                    # Actualizar último uso
                    cur.execute("""
                        UPDATE support_troubleshooting_api_keys
                        SET last_used_at = NOW(),
                            usage_count = usage_count + 1
                        WHERE api_key_hash = %s
                    """, (api_key_hash,))
                    self.db.commit()
                    
                    return {
                        "is_valid": True,
                        "key_id": row[1],
                        "permissions": row[2] if row[2] else {},
                        "rate_limit": row[3] or 100
                    }
                else:
                    return {
                        "is_valid": False,
                        "error": "Invalid API key"
                    }
        except Exception as e:
            self.logger.error(f"Error validating API key: {e}", exc_info=True)
            return {"is_valid": False, "error": str(e)}
    
    def check_sla_compliance(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Verifica cumplimiento de SLA para una sesión.
        
        Usa la función: calculate_sla_compliance()
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Dict con información de cumplimiento de SLA
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM calculate_sla_compliance(
                        p_session_id := %s
                    )
                """, (session_id,))
                
                rows = cur.fetchall()
                
                if rows:
                    compliance_data = []
                    for row in rows:
                        compliance_data.append({
                            "sla_id": row[0],
                            "sla_name": row[1],
                            "resolution_met": row[2],
                            "response_met": row[3],
                            "compliance_score": float(row[4]) if row[4] else 0.0,
                            "time_overdue_minutes": int(row[5]) if row[5] else 0
                        })
                    
                    # Calcular cumplimiento general
                    overall_score = sum(c["compliance_score"] for c in compliance_data) / len(compliance_data) if compliance_data else 0.0
                    all_met = all(c["resolution_met"] and c["response_met"] for c in compliance_data)
                    
                    return {
                        "session_id": session_id,
                        "overall_compliance_score": round(overall_score, 2),
                        "all_slas_met": all_met,
                        "sla_details": compliance_data,
                        "at_risk": any(c["time_overdue_minutes"] > 0 for c in compliance_data)
                    }
        except Exception as e:
            self.logger.error(f"Error checking SLA compliance: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "No SLA data available"}
    
    def auto_escalate_if_needed(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verifica y ejecuta escalación automática si es necesaria.
        
        Usa la función: check_auto_escalation_rules()
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Dict con información de escalación o None si no se escaló
        """
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM check_auto_escalation_rules(
                        p_session_id := %s
                    )
                """, (session_id,))
                
                row = cur.fetchone()
                
                if row and row[3]:  # escalated
                    return {
                        "escalated": True,
                        "rule_id": row[0],
                        "escalation_level": row[1],
                        "target_department": row[2],
                        "escalated_at": datetime.now().isoformat()
                    }
        except Exception as e:
            self.logger.error(f"Error checking auto escalation: {e}", exc_info=True)
        
        return None
    
    def get_sla_metrics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sla_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de cumplimiento de SLA.
        
        Args:
            date_from: Fecha desde
            date_to: Fecha hasta
            sla_id: ID del SLA específico (opcional)
            
        Returns:
            Dict con métricas de SLA
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                date_from = date_from or (datetime.now() - timedelta(days=30))
                date_to = date_to or datetime.now()
                
                query = """
                    SELECT 
                        s.id,
                        s.sla_name,
                        COUNT(sc.id) as total_sessions,
                        COUNT(*) FILTER (WHERE sc.resolution_met = true) as resolution_met_count,
                        COUNT(*) FILTER (WHERE sc.response_met = true) as response_met_count,
                        COUNT(*) FILTER (WHERE sc.resolution_met = true AND sc.response_met = true) as both_met_count,
                        AVG(sc.compliance_score) as avg_compliance_score,
                        AVG(CASE 
                            WHEN sc.actual_resolution_time > sc.target_resolution_time THEN
                                EXTRACT(EPOCH FROM (sc.actual_resolution_time - sc.target_resolution_time)) / 60
                            ELSE 0
                        END) as avg_time_overdue_minutes
                    FROM support_troubleshooting_sla_compliance sc
                    JOIN support_troubleshooting_slas s ON sc.sla_id = s.id
                    WHERE sc.calculated_at >= %s AND sc.calculated_at <= %s
                """
                
                params = [date_from, date_to]
                
                if sla_id:
                    query += " AND s.id = %s"
                    params.append(sla_id)
                
                query += " GROUP BY s.id, s.sla_name"
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                metrics = []
                for row in rows:
                    total = row[2] or 0
                    metrics.append({
                        "sla_id": row[0],
                        "sla_name": row[1],
                        "total_sessions": total,
                        "resolution_met_count": row[3] or 0,
                        "response_met_count": row[4] or 0,
                        "both_met_count": row[5] or 0,
                        "resolution_met_rate": round((row[3] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "response_met_rate": round((row[4] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "overall_compliance_rate": round((row[5] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "avg_compliance_score": round(float(row[6] or 0), 2),
                        "avg_time_overdue_minutes": round(float(row[7] or 0), 1)
                    })
                
                return {
                    "period": {
                        "from": date_from.isoformat(),
                        "to": date_to.isoformat()
                    },
                    "metrics": metrics,
                    "summary": {
                        "total_slas": len(metrics),
                        "avg_compliance_rate": round(
                            sum(m["overall_compliance_rate"] for m in metrics) / len(metrics), 2
                        ) if metrics else 0.0
                    }
                }
        except Exception as e:
            self.logger.error(f"Error getting SLA metrics: {e}", exc_info=True)
            return {"error": str(e)}
    
    def create_api_key(
        self,
        key_name: str,
        owner_email: str,
        permissions: Dict[str, Any],
        rate_limit: int = 100,
        allowed_ips: Optional[List[str]] = None,
        allowed_origins: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva API key.
        
        Args:
            key_name: Nombre de la key
            owner_email: Email del propietario
            permissions: Permisos en formato JSON
            rate_limit: Límite de requests por minuto
            allowed_ips: Lista de IPs permitidas
            allowed_origins: Lista de orígenes permitidos
            expires_at: Fecha de expiración
            
        Returns:
            Dict con la API key generada (solo se muestra una vez)
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            import secrets
            import json
            
            # Generar API key
            api_key = f"ts_{secrets.token_urlsafe(32)}"
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            with self.db.cursor() as cur:
                cur.execute("""
                    INSERT INTO support_troubleshooting_api_keys (
                        api_key_hash,
                        key_name,
                        owner_email,
                        permissions,
                        rate_limit_per_minute,
                        allowed_ips,
                        allowed_origins,
                        expires_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (
                    api_key_hash,
                    key_name,
                    owner_email,
                    json.dumps(permissions),
                    rate_limit,
                    allowed_ips,
                    allowed_origins,
                    expires_at
                ))
                
                row = cur.fetchone()
                self.db.commit()
                
                return {
                    "success": True,
                    "key_id": row[0],
                    "api_key": api_key,  # Solo se muestra una vez
                    "key_name": key_name,
                    "created_at": row[1].isoformat() if row[1] else None,
                    "warning": "⚠️ Guarda esta API key ahora, no se mostrará de nuevo"
                }
        except Exception as e:
            self.logger.error(f"Error creating API key: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return {"error": str(e)}
    
    def revoke_api_key(
        self,
        api_key_hash: str
    ) -> bool:
        """
        Revoca una API key.
        
        Args:
            api_key_hash: Hash de la API key a revocar
            
        Returns:
            True si se revocó exitosamente
        """
        if not self.db:
            return False
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    UPDATE support_troubleshooting_api_keys
                    SET is_active = false,
                        revoked_at = NOW()
                    WHERE api_key_hash = %s
                """, (api_key_hash,))
                
                self.db.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error revoking API key: {e}", exc_info=True)
            if self.db:
                self.db.rollback()
            return False
    
    def get_quality_metrics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de calidad del troubleshooting.
        
        Args:
            date_from: Fecha desde
            date_to: Fecha hasta
            
        Returns:
            Dict con métricas de calidad
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                date_from = date_from or (datetime.now() - timedelta(days=30))
                date_to = date_to or datetime.now()
                
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
                        COUNT(*) FILTER (WHERE status = 'escalated') as escalated,
                        AVG(total_duration_seconds) as avg_duration,
                        AVG(customer_satisfaction_score) as avg_satisfaction,
                        COUNT(*) FILTER (WHERE customer_satisfaction_score >= 4) as high_satisfaction_count,
                        COUNT(*) FILTER (WHERE current_step = total_steps AND status = 'resolved') as completed_all_steps
                    FROM support_troubleshooting_sessions
                    WHERE started_at >= %s AND started_at <= %s
                """, (date_from, date_to))
                
                row = cur.fetchone()
                
                total = row[0] or 0
                
                return {
                    "period": {
                        "from": date_from.isoformat(),
                        "to": date_to.isoformat()
                    },
                    "sessions": {
                        "total": total,
                        "resolved": row[1] or 0,
                        "escalated": row[2] or 0,
                        "abandoned": total - (row[1] or 0) - (row[2] or 0)
                    },
                    "quality_metrics": {
                        "resolution_rate": round((row[1] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "escalation_rate": round((row[2] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "avg_duration_minutes": round((row[3] or 0) / 60, 1) if row[3] else 0.0,
                        "avg_satisfaction": round(float(row[4] or 0), 1) if row[4] else None,
                        "high_satisfaction_rate": round((row[5] or 0) / total * 100, 2) if total > 0 else 0.0,
                        "completion_rate": round((row[6] or 0) / total * 100, 2) if total > 0 else 0.0
                    }
                }
        except Exception as e:
            self.logger.error(f"Error getting quality metrics: {e}", exc_info=True)
            return {"error": str(e)}
    
    def perform_maintenance(
        self,
        maintenance_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Ejecuta tareas de mantenimiento automático.
        
        Usa la función: perform_troubleshooting_maintenance()
        
        Args:
            maintenance_type: Tipo de mantenimiento (all, cache, stats, indexes)
            
        Returns:
            Dict con resultados del mantenimiento
        """
        if not self.db:
            return {"error": "No database connection"}
        
        try:
            with self.db.cursor() as cur:
                cur.execute("""
                    SELECT * FROM perform_troubleshooting_maintenance(
                        p_maintenance_type := %s
                    )
                """, (maintenance_type,))
                
                row = cur.fetchone()
                
                if row:
                    return {
                        "maintenance_type": maintenance_type,
                        "tasks_completed": row[0] if isinstance(row[0], list) else [],
                        "cache_cleaned": row[1] if len(row) > 1 else 0,
                        "stats_refreshed": row[2] if len(row) > 2 else False,
                        "indexes_optimized": row[3] if len(row) > 3 else False,
                        "completed_at": datetime.now().isoformat()
                    }
        except Exception as e:
            self.logger.error(f"Error performing maintenance: {e}", exc_info=True)
            return {"error": str(e)}
        
        return {"error": "Maintenance function not available"}



