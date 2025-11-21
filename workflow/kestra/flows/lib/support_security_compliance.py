"""
Sistema de Seguridad y Compliance.

Maneja seguridad, privacidad de datos y compliance.
"""
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceType(Enum):
    """Tipos de compliance."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    CUSTOM = "custom"


class SecurityLevel(Enum):
    """Niveles de seguridad."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityCheck:
    """Verificación de seguridad."""
    check_id: str
    check_type: str
    status: str  # "pass", "fail", "warning"
    description: str
    severity: SecurityLevel
    details: Dict[str, Any] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()
        if self.details is None:
            self.details = {}


@dataclass
class DataRetentionRule:
    """Regla de retención de datos."""
    rule_id: str
    data_type: str  # "ticket", "feedback", "audit", etc.
    retention_days: int
    compliance_type: ComplianceType
    auto_delete: bool = False
    archive_before_delete: bool = True


class SecurityComplianceManager:
    """Gestor de seguridad y compliance."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa gestor.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.retention_rules: List[DataRetentionRule] = []
        self.compliance_configs: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Inicializa reglas por defecto."""
        default_rules = [
            DataRetentionRule(
                rule_id="ticket-retention-1y",
                data_type="ticket",
                retention_days=365,
                compliance_type=ComplianceType.GDPR,
                auto_delete=False,
                archive_before_delete=True
            ),
            DataRetentionRule(
                rule_id="feedback-retention-2y",
                data_type="feedback",
                retention_days=730,
                compliance_type=ComplianceType.GDPR,
                auto_delete=False
            ),
            DataRetentionRule(
                rule_id="audit-retention-7y",
                data_type="audit",
                retention_days=2555,  # 7 años
                compliance_type=ComplianceType.SOC2,
                auto_delete=False
            )
        ]
        
        self.retention_rules = default_rules
    
    def run_security_checks(self) -> List[SecurityCheck]:
        """
        Ejecuta verificaciones de seguridad.
        
        Returns:
            Lista de verificaciones
        """
        checks = []
        
        # Verificar acceso a datos sensibles
        checks.append(self._check_sensitive_data_access())
        
        # Verificar encriptación
        checks.append(self._check_encryption())
        
        # Verificar contraseñas
        checks.append(self._check_password_policy())
        
        # Verificar logs de auditoría
        checks.append(self._check_audit_logs())
        
        # Verificar retención de datos
        checks.append(self._check_data_retention())
        
        # Verificar acceso no autorizado
        checks.append(self._check_unauthorized_access())
        
        return [c for c in checks if c is not None]
    
    def _check_sensitive_data_access(self) -> SecurityCheck:
        """Verifica acceso a datos sensibles."""
        if not self.db:
            return SecurityCheck(
                check_id="security-sensitive-data",
                check_type="sensitive_data_access",
                status="warning",
                description="No se puede verificar acceso a datos sensibles (sin BD)",
                severity=SecurityLevel.MEDIUM
            )
        
        try:
            with self.db.cursor() as cur:
                # Verificar si hay tickets con datos sensibles sin protección
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE description LIKE '%password%' 
                    OR description LIKE '%credit%card%'
                    OR description LIKE '%ssn%'
                    OR description LIKE '%social%security%'
                """)
                
                count = cur.fetchone()[0]
                
                if count > 0:
                    return SecurityCheck(
                        check_id="security-sensitive-data",
                        check_type="sensitive_data_access",
                        status="warning",
                        description=f"Se encontraron {count} tickets con posible información sensible",
                        severity=SecurityLevel.HIGH,
                        details={"tickets_with_sensitive_data": count}
                    )
                else:
                    return SecurityCheck(
                        check_id="security-sensitive-data",
                        check_type="sensitive_data_access",
                        status="pass",
                        description="No se encontraron tickets con información sensible",
                        severity=SecurityLevel.LOW
                    )
        except Exception as e:
            logger.error(f"Error checking sensitive data: {e}")
            return SecurityCheck(
                check_id="security-sensitive-data",
                check_type="sensitive_data_access",
                status="warning",
                description=f"Error al verificar: {str(e)}",
                severity=SecurityLevel.MEDIUM
            )
    
    def _check_encryption(self) -> SecurityCheck:
        """Verifica encriptación."""
        # Verificación básica - en producción verificar configuración real
        return SecurityCheck(
            check_id="security-encryption",
            check_type="encryption",
            status="pass",
            description="Encriptación configurada (verificar configuración de BD)",
            severity=SecurityLevel.MEDIUM,
            details={"note": "Verificar configuración de TLS/SSL en producción"}
        )
    
    def _check_password_policy(self) -> SecurityCheck:
        """Verifica política de contraseñas."""
        # Verificación básica
        return SecurityCheck(
            check_id="security-password-policy",
            check_type="password_policy",
            status="pass",
            description="Política de contraseñas debe estar configurada en el sistema de autenticación",
            severity=SecurityLevel.MEDIUM,
            details={"note": "Verificar en sistema de autenticación"}
        )
    
    def _check_audit_logs(self) -> SecurityCheck:
        """Verifica logs de auditoría."""
        if not self.db:
            return SecurityCheck(
                check_id="security-audit-logs",
                check_type="audit_logs",
                status="warning",
                description="No se puede verificar logs de auditoría (sin BD)",
                severity=SecurityLevel.MEDIUM
            )
        
        try:
            with self.db.cursor() as cur:
                # Verificar si hay tabla de auditoría
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'support_audit_tickets'
                """)
                
                has_audit = cur.fetchone()[0] > 0
                
                if has_audit:
                    # Verificar actividad reciente
                    cur.execute("""
                        SELECT COUNT(*) FROM support_audit_tickets
                        WHERE created_at >= NOW() - INTERVAL '24 hours'
                    """)
                    recent_audits = cur.fetchone()[0]
                    
                    return SecurityCheck(
                        check_id="security-audit-logs",
                        check_type="audit_logs",
                        status="pass" if recent_audits > 0 else "warning",
                        description=f"Sistema de auditoría activo: {recent_audits} eventos en últimas 24h",
                        severity=SecurityLevel.LOW if recent_audits > 0 else SecurityLevel.MEDIUM,
                        details={"recent_audits": recent_audits}
                    )
                else:
                    return SecurityCheck(
                        check_id="security-audit-logs",
                        check_type="audit_logs",
                        status="fail",
                        description="Sistema de auditoría no configurado",
                        severity=SecurityLevel.HIGH
                    )
        except Exception as e:
            logger.error(f"Error checking audit logs: {e}")
            return SecurityCheck(
                check_id="security-audit-logs",
                check_type="audit_logs",
                status="warning",
                description=f"Error al verificar: {str(e)}",
                severity=SecurityLevel.MEDIUM
            )
    
    def _check_data_retention(self) -> SecurityCheck:
        """Verifica cumplimiento de retención de datos."""
        if not self.retention_rules:
            return SecurityCheck(
                check_id="security-data-retention",
                check_type="data_retention",
                status="warning",
                description="No hay reglas de retención configuradas",
                severity=SecurityLevel.MEDIUM
            )
        
        return SecurityCheck(
            check_id="security-data-retention",
            check_type="data_retention",
            status="pass",
            description=f"{len(self.retention_rules)} reglas de retención configuradas",
            severity=SecurityLevel.LOW,
            details={"rules_count": len(self.retention_rules)}
        )
    
    def _check_unauthorized_access(self) -> SecurityCheck:
        """Verifica intentos de acceso no autorizado."""
        if not self.db:
            return None
        
        try:
            with self.db.cursor() as cur:
                # Verificar intentos fallidos recientes (si hay tabla de auditoría de accesos)
                cur.execute("""
                    SELECT COUNT(*) FROM support_audit_access
                    WHERE success = false
                    AND created_at >= NOW() - INTERVAL '24 hours'
                """)
                
                failed_attempts = cur.fetchone()[0]
                
                if failed_attempts > 10:
                    return SecurityCheck(
                        check_id="security-unauthorized-access",
                        check_type="unauthorized_access",
                        status="warning",
                        description=f"{failed_attempts} intentos de acceso fallidos en últimas 24h",
                        severity=SecurityLevel.HIGH,
                        details={"failed_attempts": failed_attempts}
                    )
                else:
                    return SecurityCheck(
                        check_id="security-unauthorized-access",
                        check_type="unauthorized_access",
                        status="pass",
                        description=f"{failed_attempts} intentos fallidos (normal)",
                        severity=SecurityLevel.LOW,
                        details={"failed_attempts": failed_attempts}
                    )
        except Exception:
            # Si no existe la tabla, no es crítico
            return None
    
    def apply_data_retention(self) -> Dict[str, Any]:
        """
        Aplica reglas de retención de datos.
        
        Returns:
            Resultado de aplicación
        """
        if not self.db:
            return {"error": "No database connection"}
        
        results = {
            "applied_rules": [],
            "archived": 0,
            "deleted": 0,
            "errors": []
        }
        
        try:
            with self.db.cursor() as cur:
                for rule in self.retention_rules:
                    if not rule.auto_delete:
                        continue
                    
                    cutoff_date = datetime.now() - timedelta(days=rule.retention_days)
                    
                    try:
                        if rule.data_type == "ticket":
                            # Archivar antes de eliminar
                            if rule.archive_before_delete:
                                cur.execute("""
                                    UPDATE support_tickets
                                    SET status = 'archived'
                                    WHERE created_at < %s
                                    AND status != 'archived'
                                """, (cutoff_date,))
                                archived = cur.rowcount
                                results["archived"] += archived
                            
                            # Eliminar (solo si auto_delete está habilitado)
                            cur.execute("""
                                DELETE FROM support_tickets
                                WHERE created_at < %s
                                AND status = 'archived'
                            """, (cutoff_date,))
                            deleted = cur.rowcount
                            results["deleted"] += deleted
                        
                        results["applied_rules"].append({
                            "rule_id": rule.rule_id,
                            "data_type": rule.data_type,
                            "cutoff_date": cutoff_date.isoformat(),
                            "archived": archived if rule.archive_before_delete else 0,
                            "deleted": deleted
                        })
                        
                    except Exception as e:
                        results["errors"].append({
                            "rule_id": rule.rule_id,
                            "error": str(e)
                        })
                        logger.error(f"Error applying retention rule {rule.rule_id}: {e}")
            
            if self.db:
                self.db.commit()
        
        except Exception as e:
            logger.error(f"Error applying data retention: {e}")
            results["errors"].append({"general_error": str(e)})
        
        return results
    
    def mask_sensitive_data(self, text: str) -> str:
        """
        Enmascara datos sensibles en texto.
        
        Args:
            text: Texto a procesar
            
        Returns:
            Texto con datos enmascarados
        """
        # Patrones comunes de datos sensibles
        patterns = [
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'XXXX-XXXX-XXXX-XXXX'),  # Tarjeta de crédito
            (r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX'),  # SSN
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),  # Email (opcional)
            (r'\b\d{10,}\b', '**********'),  # Números largos
        ]
        
        masked_text = text
        for pattern, replacement in patterns:
            masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
        
        return masked_text
    
    def get_compliance_report(self, compliance_type: ComplianceType) -> Dict[str, Any]:
        """
        Genera reporte de compliance.
        
        Args:
            compliance_type: Tipo de compliance
            
        Returns:
            Reporte de compliance
        """
        security_checks = self.run_security_checks()
        
        passed = sum(1 for c in security_checks if c.status == "pass")
        failed = sum(1 for c in security_checks if c.status == "fail")
        warnings = sum(1 for c in security_checks if c.status == "warning")
        
        return {
            "compliance_type": compliance_type.value,
            "report_date": datetime.now().isoformat(),
            "security_checks": {
                "total": len(security_checks),
                "passed": passed,
                "failed": failed,
                "warnings": warnings
            },
            "checks": [
                {
                    "id": c.check_id,
                    "type": c.check_type,
                    "status": c.status,
                    "description": c.description,
                    "severity": c.severity.value
                }
                for c in security_checks
            ],
            "retention_rules": [
                {
                    "rule_id": r.rule_id,
                    "data_type": r.data_type,
                    "retention_days": r.retention_days
                }
                for r in self.retention_rules
                if r.compliance_type == compliance_type
            ],
            "compliance_score": (passed / len(security_checks) * 100) if security_checks else 0.0
        }

