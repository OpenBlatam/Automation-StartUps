"""
Sistema de monitoreo y alertas para ads reporting.

Incluye:
- Detección de anomalías
- Alertas automáticas
- Métricas de rendimiento
- Health monitoring
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from ads_reporting_utils import notify_slack
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    def notify_slack(message: str, **kwargs):
        logger.info(f"[Slack] {message}")


class AlertLevel(Enum):
    """Niveles de alerta."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alerta del sistema."""
    level: AlertLevel
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    platform: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte alerta a diccionario."""
        return {
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "platform": self.platform
        }


class PerformanceMonitor:
    """Monitor de rendimiento de extracciones."""
    
    def __init__(self, platform: str):
        """
        Inicializa el monitor.
        
        Args:
            platform: Plataforma a monitorear
        """
        self.platform = platform
        self.extraction_history: List[Dict[str, Any]] = []
    
    def record_extraction(
        self,
        records_extracted: int,
        duration_ms: float,
        errors: int = 0
    ) -> None:
        """
        Registra una extracción.
        
        Args:
            records_extracted: Número de registros extraídos
            duration_ms: Duración en milisegundos
            errors: Número de errores
        """
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "records_extracted": records_extracted,
            "duration_ms": duration_ms,
            "errors": errors,
            "records_per_second": (records_extracted / (duration_ms / 1000)) if duration_ms > 0 else 0
        }
        
        self.extraction_history.append(record)
        
        # Mantener solo últimos 100 registros
        if len(self.extraction_history) > 100:
            self.extraction_history = self.extraction_history[-100:]
        
        # Trackear métricas
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr(
                    f"ads_reporting.{self.platform}.extraction.records",
                    records_extracted
                )
                stats.timing(
                    f"ads_reporting.{self.platform}.extraction.duration_ms",
                    int(duration_ms)
                )
                if errors > 0:
                    stats.incr(
                        f"ads_reporting.{self.platform}.extraction.errors",
                        errors
                    )
            except Exception:
                pass
    
    def detect_performance_issues(self) -> List[Alert]:
        """
        Detecta problemas de rendimiento.
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        if len(self.extraction_history) < 5:
            return alerts
        
        recent = self.extraction_history[-10:]
        
        # Detectar disminución significativa en registros
        avg_recent = sum(r["records_extracted"] for r in recent) / len(recent)
        avg_older = sum(r["records_extracted"] for r in self.extraction_history[:-10]) / max(1, len(self.extraction_history) - 10)
        
        if avg_older > 0 and (avg_recent / avg_older) < 0.5:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Disminución significativa en registros extraídos",
                message=f"Promedio reciente: {avg_recent:.0f}, promedio anterior: {avg_older:.0f}",
                platform=self.platform,
                details={"avg_recent": avg_recent, "avg_older": avg_older}
            ))
        
        # Detectar aumento en tiempo de ejecución
        avg_duration_recent = sum(r["duration_ms"] for r in recent) / len(recent)
        avg_duration_older = sum(r["duration_ms"] for r in self.extraction_history[:-10]) / max(1, len(self.extraction_history) - 10)
        
        if avg_duration_older > 0 and (avg_duration_recent / avg_duration_older) > 2.0:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Aumento significativo en tiempo de ejecución",
                message=f"Tiempo reciente: {avg_duration_recent:.0f}ms, tiempo anterior: {avg_duration_older:.0f}ms",
                platform=self.platform,
                details={"avg_duration_recent": avg_duration_recent, "avg_duration_older": avg_duration_older}
            ))
        
        # Detectar errores frecuentes
        recent_errors = sum(r["errors"] for r in recent)
        if recent_errors > 5:
            alerts.append(Alert(
                level=AlertLevel.ERROR,
                title="Errores frecuentes en extracción",
                message=f"{recent_errors} errores en las últimas 10 extracciones",
                platform=self.platform,
                details={"recent_errors": recent_errors}
            ))
        
        return alerts


class DataQualityMonitor:
    """Monitor de calidad de datos."""
    
    def __init__(self, platform: str):
        """
        Inicializa el monitor de calidad.
        
        Args:
            platform: Plataforma a monitorear
        """
        self.platform = platform
    
    def check_data_quality(
        self,
        data: List[Dict[str, Any]],
        expected_min_records: int = 1
    ) -> List[Alert]:
        """
        Verifica calidad de datos y genera alertas.
        
        Args:
            data: Lista de datos a verificar
            expected_min_records: Mínimo de registros esperados
            
        Returns:
            Lista de alertas
        """
        alerts = []
        
        # Verificar número de registros
        if len(data) < expected_min_records:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Pocos registros extraídos",
                message=f"Se extrajeron {len(data)} registros, se esperaban al menos {expected_min_records}",
                platform=self.platform,
                details={"extracted": len(data), "expected": expected_min_records}
            ))
        
        # Verificar valores negativos
        negative_values = []
        for i, record in enumerate(data):
            if record.get("spend", 0) < 0 or record.get("impressions", 0) < 0:
                negative_values.append(i)
        
        if negative_values:
            alerts.append(Alert(
                level=AlertLevel.ERROR,
                title="Valores negativos detectados",
                message=f"Se encontraron valores negativos en {len(negative_values)} registros",
                platform=self.platform,
                details={"records_with_negatives": negative_values[:10]}
            ))
        
        # Verificar CTR anormalmente alto
        high_ctr_count = sum(1 for r in data if r.get("ctr", 0) > 50)
        if high_ctr_count > len(data) * 0.1:  # Más del 10%
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="CTR anormalmente alto detectado",
                message=f"{high_ctr_count} registros con CTR > 50%",
                platform=self.platform,
                details={"high_ctr_count": high_ctr_count}
            ))
        
        # Verificar falta de conversiones
        no_conversions = sum(1 for r in data if r.get("conversions", 0) == 0 and r.get("clicks", 0) > 100)
        if no_conversions > len(data) * 0.3:  # Más del 30%
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                title="Falta de conversiones",
                message=f"{no_conversions} registros con clics pero sin conversiones",
                platform=self.platform,
                details={"no_conversions_count": no_conversions}
            ))
        
        return alerts


class AlertManager:
    """Gestor de alertas del sistema."""
    
    def __init__(self, enable_notifications: bool = True):
        """
        Inicializa el gestor de alertas.
        
        Args:
            enable_notifications: Si enviar notificaciones (Slack, etc.)
        """
        self.enable_notifications = enable_notifications
        self.alerts_history: List[Alert] = []
    
    def send_alert(self, alert: Alert) -> None:
        """
        Envía una alerta.
        
        Args:
            alert: Alerta a enviar
        """
        self.alerts_history.append(alert)
        
        # Mantener solo últimos 1000 alertas
        if len(self.alerts_history) > 1000:
            self.alerts_history = self.alerts_history[-1000:]
        
        # Determinar emoji según nivel
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        emoji = emoji_map.get(alert.level, "ℹ️")
        
        # Formatear mensaje
        message = f"{emoji} **{alert.title}**\n{alert.message}"
        if alert.platform:
            message += f"\nPlataforma: {alert.platform}"
        if alert.details:
            details_str = ", ".join(f"{k}={v}" for k, v in list(alert.details.items())[:5])
            message += f"\nDetalles: {details_str}"
        
        # Logging
        log_level_map = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }
        logger.log(log_level_map.get(alert.level, logging.INFO), message)
        
        # Notificación externa
        if self.enable_notifications and alert.level in [AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL]:
            try:
                notify_slack(message, level=alert.level.value)
            except Exception as e:
                logger.warning(f"Error enviando notificación: {str(e)}")
    
    def send_batch_alerts(self, alerts: List[Alert]) -> None:
        """
        Envía múltiples alertas en batch.
        
        Args:
            alerts: Lista de alertas
        """
        for alert in alerts:
            self.send_alert(alert)
        
        # Si hay muchas alertas, enviar resumen
        if len(alerts) > 5:
            critical_count = sum(1 for a in alerts if a.level == AlertLevel.CRITICAL)
            error_count = sum(1 for a in alerts if a.level == AlertLevel.ERROR)
            warning_count = sum(1 for a in alerts if a.level == AlertLevel.WARNING)
            
            summary = (
                f"📊 Resumen de alertas ({len(alerts)} total):\n"
                f"🚨 Críticas: {critical_count}\n"
                f"❌ Errores: {error_count}\n"
                f"⚠️ Advertencias: {warning_count}"
            )
            
            if critical_count > 0 or error_count > 0:
                try:
                    notify_slack(summary)
                except Exception:
                    pass
    
    def get_recent_alerts(
        self,
        level: Optional[AlertLevel] = None,
        hours: int = 24
    ) -> List[Alert]:
        """
        Obtiene alertas recientes.
        
        Args:
            level: Nivel de alerta a filtrar (opcional)
            hours: Horas hacia atrás
            
        Returns:
            Lista de alertas
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        filtered = [
            alert for alert in self.alerts_history
            if datetime.fromisoformat(alert.timestamp) >= cutoff
        ]
        
        if level:
            filtered = [a for a in filtered if a.level == level]
        
        return filtered


# Instancia global del gestor de alertas
_global_alert_manager: Optional[AlertManager] = None


def get_alert_manager(enable_notifications: bool = True) -> AlertManager:
    """Obtiene o crea el gestor de alertas global."""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager(enable_notifications=enable_notifications)
    return _global_alert_manager


def monitor_extraction(
    platform: str,
    records_extracted: int,
    duration_ms: float,
    errors: int = 0
) -> List[Alert]:
    """
    Monitorea una extracción y retorna alertas si las hay.
    
    Args:
        platform: Plataforma
        records_extracted: Registros extraídos
        duration_ms: Duración en ms
        errors: Errores
        
    Returns:
        Lista de alertas generadas
    """
    monitor = PerformanceMonitor(platform)
    monitor.record_extraction(records_extracted, duration_ms, errors)
    alerts = monitor.detect_performance_issues()
    
    if alerts:
        alert_manager = get_alert_manager()
        alert_manager.send_batch_alerts(alerts)
    
    return alerts

