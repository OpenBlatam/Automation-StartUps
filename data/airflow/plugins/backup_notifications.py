"""
Sistema de Notificaciones para Backups y Seguridad.

Envía alertas sobre:
- Resultados de backups
- Fallos de backups
- Alertas de seguridad
- Intentos de acceso no autorizados
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from data.airflow.plugins.etl_notifications import notify_slack, notify_email
from data.airflow.plugins.backup_manager import BackupResult, BackupStatus

# Importar integración de ticketing si está disponible
try:
    from data.airflow.plugins.backup_ticketing import TicketingManager, TicketPriority
    TICKETING_AVAILABLE = True
except ImportError:
    TICKETING_AVAILABLE = False
    TicketingManager = None
    TicketPriority = None

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveles de alerta."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BackupNotifier:
    """Notificador de backups."""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        email_config: Optional[Dict[str, Any]] = None,
        enable_notifications: bool = True
    ):
        """
        Inicializa notificador.
        
        Args:
            slack_webhook: Webhook de Slack (opcional)
            email_config: Configuración de email (opcional)
            enable_notifications: Si enviar notificaciones
        """
        self.slack_webhook = slack_webhook or os.getenv("SLACK_WEBHOOK_URL")
        self.email_config = email_config or self._load_email_config()
        self.enable_notifications = enable_notifications
    
    def _load_email_config(self) -> Dict[str, Any]:
        """Carga configuración de email desde variables de entorno."""
        return {
            'smtp_host': os.getenv("SMTP_HOST"),
            'smtp_port': int(os.getenv("SMTP_PORT", "587")),
            'smtp_user': os.getenv("SMTP_USER"),
            'smtp_password': os.getenv("SMTP_PASSWORD"),
            'from_email': os.getenv("FROM_EMAIL", "backups@example.com"),
            'to_emails': os.getenv("BACKUP_ALERT_EMAILS", "").split(",") if os.getenv("BACKUP_ALERT_EMAILS") else []
        }
    
    def notify_backup_result(self, result: BackupResult) -> None:
        """
        Notifica resultado de backup.
        
        Args:
            result: Resultado del backup
        """
        if not self.enable_notifications:
            return
        
        level = AlertLevel.INFO
        if result.status == BackupStatus.FAILED:
            level = AlertLevel.ERROR
        elif result.status == BackupStatus.COMPLETED:
            level = AlertLevel.INFO
        
        message = self._format_backup_message(result)
        
        self._send_notifications(message, level, result)
    
    def _format_backup_message(self, result: BackupResult) -> str:
        """Formatea mensaje de backup con métricas mejoradas."""
        status_emoji = {
            BackupStatus.COMPLETED: "✅",
            BackupStatus.FAILED: "❌",
            BackupStatus.VERIFIED: "✅",
            BackupStatus.IN_PROGRESS: "⏳",
            BackupStatus.PENDING: "⏸️"
        }
        
        emoji = status_emoji.get(result.status, "ℹ️")
        
        size_mb = result.size_bytes / (1024 * 1024) if result.size_bytes else 0
        
        message = f"""
{emoji} *Backup {result.status.value.upper()}*

*ID:* `{result.backup_id}`
*Estado:* {result.status.value}
*Tamaño:* {size_mb:.2f} MB
*Duración:* {result.duration_seconds:.2f}s
*Fecha:* {result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result.created_at else 'N/A'}
"""
        
        # Métricas adicionales
        if result.compression_ratio:
            message += f"*Compresión:* {result.compression_ratio:.2f}x\n"
        
        if result.encryption_time:
            message += f"*Tiempo encriptación:* {result.encryption_time:.2f}s\n"
        
        if result.upload_time:
            message += f"*Tiempo subida nube:* {result.upload_time:.2f}s\n"
        
        if result.disk_usage_before and result.disk_usage_after:
            disk_delta = result.disk_usage_after - result.disk_usage_before
            message += f"*Uso disco:* {result.disk_usage_before:.2f}GB → {result.disk_usage_after:.2f}GB (+{disk_delta:.2f}GB)\n"
        
        if result.file_path:
            message += f"*Archivo local:* `{result.file_path}`\n"
        
        if result.cloud_path:
            message += f"*Nube:* `{result.cloud_path}`\n"
        
        if result.checksum:
            message += f"*Checksum:* `{result.checksum[:16]}...`\n"
        
        if result.error:
            message += f"\n❌ *Error:* {result.error}\n"
        
        return message
    
    def _send_notifications(
        self,
        message: str,
        level: AlertLevel,
        result: Optional[BackupResult] = None
    ) -> None:
        """Envía notificaciones por múltiples canales."""
        # Slack
        if self.slack_webhook:
            try:
                notify_slack(message, webhook_url=self.slack_webhook)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
        
        # Email (solo para errores críticos)
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL] and self.email_config:
            try:
                subject = f"🔴 Backup {level.value.upper()}: {result.backup_id if result else 'Unknown'}"
                notify_email(
                    to=self.email_config.get('to_emails', []),
                    subject=subject,
                    body=message,
                    smtp_host=self.email_config.get('smtp_host'),
                    smtp_port=self.email_config.get('smtp_port', 587),
                    smtp_user=self.email_config.get('smtp_user'),
                    smtp_password=self.email_config.get('smtp_password')
                )
            except Exception as e:
                logger.warning(f"Failed to send email notification: {e}")


class SecurityAlertManager:
    """Gestor de alertas de seguridad."""
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        email_config: Optional[Dict[str, Any]] = None
    ):
        """Inicializa gestor de alertas de seguridad."""
        self.slack_webhook = slack_webhook or os.getenv("SLACK_WEBHOOK_URL")
        self.email_config = email_config
        self.alert_history: List[Dict[str, Any]] = []
        
        # Inicializar ticketing si está disponible
        self.ticketing = None
        if TICKETING_AVAILABLE:
            try:
                self.ticketing = TicketingManager()
            except Exception:
                pass
    
    def send_security_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.WARNING,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envía alerta de seguridad.
        
        Args:
            title: Título de la alerta
            message: Mensaje de la alerta
            level: Nivel de la alerta
            details: Detalles adicionales
        """
        alert = {
            'title': title,
            'message': message,
            'level': level.value,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.alert_history.append(alert)
        
        # Mantener solo últimos 1000 alertas
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        formatted_message = self._format_security_message(alert)
        
        # Enviar notificaciones
        self._send_notifications(formatted_message, level, alert)
        
        logger.warning(f"Security alert [{level.value}]: {title} - {message}")
    
    def _format_security_message(self, alert: Dict[str, Any]) -> str:
        """Formatea mensaje de alerta de seguridad."""
        level_emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        
        emoji = level_emoji.get(AlertLevel(alert['level']), "ℹ️")
        
        message = f"""
{emoji} *{alert['title']}*

{alert['message']}

*Fecha:* {datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
*Nivel:* {alert['level'].upper()}
"""
        
        if alert.get('details'):
            details_str = "\n".join([f"• {k}: {v}" for k, v in alert['details'].items()])
            message += f"\n*Detalles:*\n{details_str}\n"
        
        return message
    
    def _send_notifications(
        self,
        message: str,
        level: AlertLevel,
        alert: Dict[str, Any]
    ) -> None:
        """Envía notificaciones de seguridad."""
        # Slack
        if self.slack_webhook:
            try:
                notify_slack(message, webhook_url=self.slack_webhook)
            except Exception as e:
                logger.warning(f"Failed to send Slack security alert: {e}")
        
        # Email para alertas críticas
        if level in [AlertLevel.ERROR, AlertLevel.CRITICAL] and self.email_config:
            try:
                subject = f"🚨 Security Alert [{level.value.upper()}]: {alert['title']}"
                notify_email(
                    to=self.email_config.get('to_emails', []),
                    subject=subject,
                    body=message,
                    smtp_host=self.email_config.get('smtp_host'),
                    smtp_port=self.email_config.get('smtp_port', 587),
                    smtp_user=self.email_config.get('smtp_user'),
                    smtp_password=self.email_config.get('smtp_password')
                )
            except Exception as e:
                logger.warning(f"Failed to send email security alert: {e}")
        
        # Crear ticket para alertas críticas
        if level == AlertLevel.CRITICAL and self.ticketing:
            try:
                from data.airflow.plugins.backup_ticketing import Ticket
                ticket = Ticket(
                    title=alert['title'],
                    description=alert['message'],
                    priority=TicketPriority.HIGH,
                    labels=['security', 'backup', 'critical']
                )
                ticket_results = self.ticketing.create_backup_failure_ticket(
                    backup_id=alert.get('details', {}).get('backup_id', 'unknown'),
                    error=alert['message'],
                    details=alert.get('details', {})
                )
                if ticket_results:
                    logger.info(f"Created tickets: {ticket_results}")
            except Exception as e:
                logger.warning(f"Failed to create ticket: {e}")
    
    def alert_backup_failure(
        self,
        backup_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Alerta sobre fallo de backup."""
        self.send_security_alert(
            title="Backup Failure",
            message=f"Backup {backup_id} failed: {error}",
            level=AlertLevel.ERROR,
            details=details or {}
        )
    
    def alert_unauthorized_access(
        self,
        resource: str,
        user: Optional[str] = None,
        ip: Optional[str] = None
    ) -> None:
        """Alerta sobre acceso no autorizado."""
        details = {'resource': resource}
        if user:
            details['user'] = user
        if ip:
            details['ip'] = ip
        
        self.send_security_alert(
            title="Unauthorized Access Attempt",
            message=f"Unauthorized access attempt to {resource}",
            level=AlertLevel.CRITICAL,
            details=details
        )
    
    def alert_encryption_error(
        self,
        operation: str,
        error: str
    ) -> None:
        """Alerta sobre error de encriptación."""
        self.send_security_alert(
            title="Encryption Error",
            message=f"Encryption failed during {operation}: {error}",
            level=AlertLevel.ERROR,
            details={'operation': operation, 'error': error}
        )
    
    def alert_cloud_sync_failure(
        self,
        provider: str,
        error: str
    ) -> None:
        """Alerta sobre fallo de sincronización en nube."""
        self.send_security_alert(
            title="Cloud Sync Failure",
            message=f"Failed to sync to {provider}: {error}",
            level=AlertLevel.WARNING,
            details={'provider': provider, 'error': error}
        )
    
    def get_recent_alerts(
        self,
        level: Optional[AlertLevel] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Obtiene alertas recientes.
        
        Args:
            level: Filtrar por nivel (opcional)
            hours: Horas hacia atrás
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        
        alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff
        ]
        
        if level:
            alerts = [a for a in alerts if AlertLevel(a['level']) == level]
        
        return alerts

