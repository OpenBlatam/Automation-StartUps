"""
Módulo de Validación de Compliance para Backups.

Proporciona:
- Validación de políticas de backup
- Verificación de retención
- Validación de encriptación
- Verificación de acceso
- Reportes de compliance
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Estados de compliance."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class ComplianceRule:
    """Regla de compliance."""
    rule_id: str
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    enabled: bool = True


@dataclass
class ComplianceCheck:
    """Resultado de verificación de compliance."""
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()


class BackupComplianceValidator:
    """Validador de compliance de backups."""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        """
        Inicializa validador de compliance.
        
        Args:
            backup_dir: Directorio de backups
        """
        self.backup_dir = Path(backup_dir)
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[ComplianceRule]:
        """Inicializa reglas de compliance."""
        return [
            ComplianceRule(
                rule_id="encryption_required",
                name="Encryption Required",
                description="All backups must be encrypted",
                severity="critical"
            ),
            ComplianceRule(
                rule_id="retention_policy",
                name="Retention Policy",
                description="Backups must comply with retention policy",
                severity="high"
            ),
            ComplianceRule(
                rule_id="backup_frequency",
                name="Backup Frequency",
                description="Backups must meet minimum frequency requirements",
                severity="high"
            ),
            ComplianceRule(
                rule_id="offsite_backup",
                name="Offsite Backup",
                description="Backups must be stored offsite (cloud)",
                severity="critical"
            ),
            ComplianceRule(
                rule_id="access_control",
                name="Access Control",
                description="Backups must have proper access controls",
                severity="medium"
            ),
            ComplianceRule(
                rule_id="verification_required",
                name="Verification Required",
                description="Backups must be verified regularly",
                severity="high"
            )
        ]
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones de compliance.
        
        Returns:
            Dict con resultados de todas las validaciones
        """
        checks = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if rule.rule_id == "encryption_required":
                checks.append(self._check_encryption(rule))
            elif rule.rule_id == "retention_policy":
                checks.append(self._check_retention(rule))
            elif rule.rule_id == "backup_frequency":
                checks.append(self._check_frequency(rule))
            elif rule.rule_id == "offsite_backup":
                checks.append(self._check_offsite(rule))
            elif rule.rule_id == "access_control":
                checks.append(self._check_access_control(rule))
            elif rule.rule_id == "verification_required":
                checks.append(self._check_verification(rule))
        
        # Determinar estado general
        critical_failures = [
            c for c in checks
            if c.status == ComplianceStatus.NON_COMPLIANT
            and any(r.severity == 'critical' for r in self.rules if r.rule_id == c.rule_id)
        ]
        
        if critical_failures:
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(c.status == ComplianceStatus.NON_COMPLIANT for c in checks):
            overall_status = ComplianceStatus.WARNING
        elif all(c.status == ComplianceStatus.COMPLIANT for c in checks):
            overall_status = ComplianceStatus.COMPLIANT
        else:
            overall_status = ComplianceStatus.UNKNOWN
        
        return {
            'overall_status': overall_status.value,
            'checks': [
                {
                    'rule_id': c.rule_id,
                    'rule_name': c.rule_name,
                    'status': c.status.value,
                    'message': c.message,
                    'details': c.details,
                    'checked_at': c.checked_at.isoformat()
                }
                for c in checks
            ],
            'summary': {
                'total_checks': len(checks),
                'compliant': sum(1 for c in checks if c.status == ComplianceStatus.COMPLIANT),
                'non_compliant': sum(1 for c in checks if c.status == ComplianceStatus.NON_COMPLIANT),
                'warnings': sum(1 for c in checks if c.status == ComplianceStatus.WARNING)
            }
        }
    
    def _check_encryption(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica que los backups estén encriptados."""
        import os
        
        encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
        
        if not encryption_key:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.NON_COMPLIANT,
                message="Encryption key not configured",
                details={'severity': rule.severity}
            )
        
        # Verificar que hay backups encriptados
        encrypted_backups = list(self.backup_dir.glob("*.encrypted"))
        
        if not encrypted_backups:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                message="No encrypted backups found",
                details={'severity': rule.severity}
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.COMPLIANT,
            message=f"Found {len(encrypted_backups)} encrypted backups",
            details={
                'encrypted_count': len(encrypted_backups),
                'severity': rule.severity
            }
        )
    
    def _check_retention(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica política de retención."""
        retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        recent_backups = [
            f for f in self.backup_dir.glob("*")
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) >= cutoff_date
        ]
        
        if len(recent_backups) < 7:  # Mínimo 7 backups en período de retención
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                message=f"Only {len(recent_backups)} backups found in retention period",
                details={
                    'retention_days': retention_days,
                    'backups_found': len(recent_backups),
                    'severity': rule.severity
                }
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.COMPLIANT,
            message=f"Retention policy compliant: {len(recent_backups)} backups",
            details={
                'retention_days': retention_days,
                'backups_found': len(recent_backups),
                'severity': rule.severity
            }
        )
    
    def _check_frequency(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica frecuencia de backups."""
        # Verificar que hay backups recientes (últimas 48 horas)
        cutoff_date = datetime.now() - timedelta(hours=48)
        
        recent_backups = [
            f for f in self.backup_dir.glob("*")
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) >= cutoff_date
        ]
        
        if not recent_backups:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.NON_COMPLIANT,
                message="No backups found in last 48 hours",
                details={'severity': rule.severity}
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.COMPLIANT,
            message=f"Backup frequency compliant: {len(recent_backups)} backups in last 48h",
            details={
                'backups_found': len(recent_backups),
                'severity': rule.severity
            }
        )
    
    def _check_offsite(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica que haya backups en la nube."""
        import os
        
        cloud_provider = os.getenv("CLOUD_PROVIDER")
        cloud_configured = bool(
            cloud_provider and
            (
                (cloud_provider == "aws" and os.getenv("AWS_BACKUP_BUCKET")) or
                (cloud_provider == "azure" and os.getenv("AZURE_STORAGE_CONNECTION_STRING")) or
                (cloud_provider == "gcp" and os.getenv("GCP_BACKUP_BUCKET"))
            )
        )
        
        if not cloud_configured:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.NON_COMPLIANT,
                message="Offsite backup (cloud) not configured",
                details={'severity': rule.severity}
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.COMPLIANT,
            message=f"Offsite backup configured: {cloud_provider}",
            details={
                'cloud_provider': cloud_provider,
                'severity': rule.severity
            }
        )
    
    def _check_access_control(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica controles de acceso."""
        # Verificar permisos del directorio
        backup_dir_stat = self.backup_dir.stat()
        mode = backup_dir_stat.st_mode
        
        # Verificar que no sea accesible públicamente (permisos 755 o más restrictivos)
        if mode & 0o077 == 0:  # No hay permisos para otros
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.COMPLIANT,
                message="Access controls properly configured",
                details={'severity': rule.severity}
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.WARNING,
            message="Backup directory may have overly permissive access",
            details={
                'mode': oct(mode),
                'severity': rule.severity
            }
        )
    
    def _check_verification(self, rule: ComplianceRule) -> ComplianceCheck:
        """Verifica que los backups se verifiquen regularmente."""
        # Buscar archivos de verificación recientes
        verification_files = list(self.backup_dir.glob("*verification*.json"))
        
        if not verification_files:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                message="No verification records found",
                details={'severity': rule.severity}
            )
        
        # Verificar que haya verificaciones recientes (últimos 7 días)
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_verifications = [
            f for f in verification_files
            if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff_date
        ]
        
        if not recent_verifications:
            return ComplianceCheck(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                status=ComplianceStatus.WARNING,
                message="No recent verification records found",
                details={'severity': rule.severity}
            )
        
        return ComplianceCheck(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            status=ComplianceStatus.COMPLIANT,
            message=f"Verification compliant: {len(recent_verifications)} recent verifications",
            details={
                'verifications_found': len(recent_verifications),
                'severity': rule.severity
            }
        )

