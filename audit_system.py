"""
Sistema de Auditoría y Logging Avanzado
=======================================

Sistema completo de auditoría con logging estructurado,
trazabilidad de acciones y análisis de seguridad.
"""

import json
import logging
import logging.handlers
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import uuid

class LogLevel(Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ActionType(Enum):
    """Tipos de acciones auditables"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    IMPORT = "import"
    BACKUP = "backup"
    RESTORE = "restore"
    CONFIG_CHANGE = "config_change"
    SYSTEM_EVENT = "system_event"

class SecurityEvent(Enum):
    """Eventos de seguridad"""
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class AuditEntry:
    """Entrada de auditoría"""
    id: str
    timestamp: datetime
    user_id: str
    action: ActionType
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    session_id: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class SecurityAlert:
    """Alerta de seguridad"""
    id: str
    timestamp: datetime
    event_type: SecurityEvent
    severity: str
    user_id: Optional[str]
    ip_address: str
    description: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class AuditLogger:
    """Logger de auditoría avanzado"""
    
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self.init_database()
        self.logger = self._setup_logger()
        self._lock = threading.Lock()
        
    def init_database(self):
        """Inicializar base de datos de auditoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de auditoría
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                details TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
        ''')
        
        # Tabla de alertas de seguridad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_by TEXT,
                resolved_at TEXT
            )
        ''')
        
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Índices para optimizar consultas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_severity ON security_alerts(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
        
        conn.commit()
        conn.close()
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger estructurado"""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        # Evitar duplicación de handlers
        if logger.handlers:
            return logger
        
        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            'audit.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Formato estructurado JSON
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_audit_event(self, 
                       user_id: str,
                       action: ActionType,
                       resource_type: str,
                       resource_id: str,
                       details: Dict[str, Any],
                       ip_address: str = "",
                       user_agent: str = "",
                       session_id: str = "",
                       success: bool = True,
                       error_message: Optional[str] = None):
        """Registrar evento de auditoría"""
        
        with self._lock:
            audit_entry = AuditEntry(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                success=success,
                error_message=error_message
            )
            
            # Guardar en base de datos
            self._save_audit_entry(audit_entry)
            
            # Log estructurado
            log_data = {
                'event': 'audit',
                'audit_id': audit_entry.id,
                'user_id': user_id,
                'action': action.value,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'success': success,
                'ip_address': ip_address,
                'timestamp': audit_entry.timestamp.isoformat()
            }
            
            if success:
                self.logger.info(json.dumps(log_data))
            else:
                self.logger.error(json.dumps(log_data))
    
    def _save_audit_entry(self, entry: AuditEntry):
        """Guardar entrada de auditoría en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_log 
            (id, timestamp, user_id, action, resource_type, resource_id,
             details, ip_address, user_agent, session_id, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id,
            entry.timestamp.isoformat(),
            entry.user_id,
            entry.action.value,
            entry.resource_type,
            entry.resource_id,
            json.dumps(entry.details),
            entry.ip_address,
            entry.user_agent,
            entry.session_id,
            entry.success,
            entry.error_message
        ))
        
        conn.commit()
        conn.close()
    
    def create_security_alert(self,
                            event_type: SecurityEvent,
                            severity: str,
                            user_id: Optional[str],
                            ip_address: str,
                            description: str,
                            details: Dict[str, Any]):
        """Crear alerta de seguridad"""
        
        alert = SecurityAlert(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            description=description,
            details=details
        )
        
        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts 
            (id, timestamp, event_type, severity, user_id, ip_address,
             description, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.id,
            alert.timestamp.isoformat(),
            alert.event_type.value,
            alert.severity,
            alert.user_id,
            alert.ip_address,
            alert.description,
            json.dumps(alert.details)
        ))
        
        conn.commit()
        conn.close()
        
        # Log de seguridad
        security_log = {
            'event': 'security_alert',
            'alert_id': alert.id,
            'event_type': event_type.value,
            'severity': severity,
            'user_id': user_id,
            'ip_address': ip_address,
            'description': description,
            'timestamp': alert.timestamp.isoformat()
        }
        
        self.logger.warning(json.dumps(security_log))
    
    def track_user_session(self,
                          session_id: str,
                          user_id: str,
                          ip_address: str,
                          user_agent: str = "",
                          expires_in_hours: int = 24):
        """Rastrear sesión de usuario"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        expires_at = now + timedelta(hours=expires_in_hours)
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (session_id, user_id, ip_address, user_agent, created_at, 
             last_activity, expires_at, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_id,
            ip_address,
            user_agent,
            now.isoformat(),
            now.isoformat(),
            expires_at.isoformat(),
            True
        ))
        
        conn.commit()
        conn.close()
    
    def update_session_activity(self, session_id: str):
        """Actualizar actividad de sesión"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions 
            SET last_activity = ?
            WHERE session_id = ? AND active = TRUE
        ''', (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_audit_trail(self,
                       user_id: Optional[str] = None,
                       action: Optional[ActionType] = None,
                       resource_type: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: int = 100) -> List[AuditEntry]:
        """Obtener rastro de auditoría"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM audit_log WHERE 1=1'
        params = []
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
        
        if action:
            query += ' AND action = ?'
            params.append(action.value)
        
        if resource_type:
            query += ' AND resource_type = ?'
            params.append(resource_type)
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date.isoformat())
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date.isoformat())
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        entries = []
        for row in rows:
            entry = AuditEntry(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                user_id=row[2],
                action=ActionType(row[3]),
                resource_type=row[4],
                resource_id=row[5],
                details=json.loads(row[6]),
                ip_address=row[7],
                user_agent=row[8],
                session_id=row[9],
                success=bool(row[10]),
                error_message=row[11]
            )
            entries.append(entry)
        
        return entries
    
    def get_security_alerts(self,
                          severity: Optional[str] = None,
                          resolved: Optional[bool] = None,
                          limit: int = 50) -> List[SecurityAlert]:
        """Obtener alertas de seguridad"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM security_alerts WHERE 1=1'
        params = []
        
        if severity:
            query += ' AND severity = ?'
            params.append(severity)
        
        if resolved is not None:
            query += ' AND resolved = ?'
            params.append(resolved)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alert = SecurityAlert(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=SecurityEvent(row[2]),
                severity=row[3],
                user_id=row[4],
                ip_address=row[5],
                description=row[6],
                details=json.loads(row[7]),
                resolved=bool(row[8]),
                resolved_by=row[9],
                resolved_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
            alerts.append(alert)
        
        return alerts
    
    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtener resumen de actividad del usuario"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Actividad por día
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM audit_log
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''', (user_id, start_date.isoformat()))
        
        daily_activity = dict(cursor.fetchall())
        
        # Acciones más frecuentes
        cursor.execute('''
            SELECT action, COUNT(*) as count
            FROM audit_log
            WHERE user_id = ? AND timestamp >= ?
            GROUP BY action
            ORDER BY count DESC
            LIMIT 10
        ''', (user_id, start_date.isoformat()))
        
        top_actions = dict(cursor.fetchall())
        
        # Intentos fallidos
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM audit_log
            WHERE user_id = ? AND timestamp >= ? AND success = FALSE
        ''', (user_id, start_date.isoformat()))
        
        failed_attempts = cursor.fetchone()[0]
        
        # Sesiones activas
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM user_sessions
            WHERE user_id = ? AND active = TRUE AND expires_at > ?
        ''', (user_id, datetime.now().isoformat()))
        
        active_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'user_id': user_id,
            'period_days': days,
            'daily_activity': daily_activity,
            'top_actions': top_actions,
            'failed_attempts': failed_attempts,
            'active_sessions': active_sessions,
            'total_actions': sum(daily_activity.values())
        }
    
    def detect_suspicious_activity(self, user_id: str, hours: int = 24) -> List[SecurityAlert]:
        """Detectar actividad sospechosa"""
        
        alerts = []
        start_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Múltiples intentos fallidos de login
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM audit_log
            WHERE user_id = ? AND action = 'login' AND success = FALSE 
            AND timestamp >= ?
        ''', (user_id, start_time.isoformat()))
        
        failed_logins = cursor.fetchone()[0]
        
        if failed_logins >= 5:
            self.create_security_alert(
                SecurityEvent.FAILED_LOGIN,
                'high',
                user_id,
                '',  # IP no disponible en este contexto
                f'Múltiples intentos fallidos de login: {failed_logins}',
                {'failed_attempts': failed_logins, 'time_window_hours': hours}
            )
        
        # Actividad fuera del horario normal
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM audit_log
            WHERE user_id = ? AND timestamp >= ?
            AND (CAST(strftime('%H', timestamp) AS INTEGER) < 6 
                 OR CAST(strftime('%H', timestamp) AS INTEGER) > 22)
        ''', (user_id, start_time.isoformat()))
        
        off_hours_activity = cursor.fetchone()[0]
        
        if off_hours_activity >= 10:
            self.create_security_alert(
                SecurityEvent.SUSPICIOUS_ACTIVITY,
                'medium',
                user_id,
                '',
                f'Actividad fuera del horario normal: {off_hours_activity} acciones',
                {'off_hours_actions': off_hours_activity, 'time_window_hours': hours}
            )
        
        conn.close()
        return alerts
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Limpiar logs antiguos"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpiar logs de auditoría antiguos
        cursor.execute('DELETE FROM audit_log WHERE timestamp < ?', (cutoff_date.isoformat(),))
        audit_deleted = cursor.rowcount
        
        # Limpiar sesiones expiradas
        cursor.execute('DELETE FROM user_sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
        sessions_deleted = cursor.rowcount
        
        # Limpiar alertas de seguridad resueltas antiguas
        cursor.execute('''
            DELETE FROM security_alerts 
            WHERE resolved = TRUE AND resolved_at < ?
        ''', (cutoff_date.isoformat(),))
        alerts_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Limpieza de logs completada: {audit_deleted} auditorías, "
                        f"{sessions_deleted} sesiones, {alerts_deleted} alertas eliminadas")

# Instancia global del logger de auditoría
audit_logger = AuditLogger()

# Funciones de conveniencia
def log_user_action(user_id: str, action: ActionType, resource_type: str, 
                   resource_id: str, details: Dict[str, Any] = None, 
                   success: bool = True, **kwargs):
    """Log de acción de usuario"""
    audit_logger.log_audit_event(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        success=success,
        **kwargs
    )

def create_security_alert(event_type: SecurityEvent, severity: str, 
                         user_id: str = None, ip_address: str = "",
                         description: str = "", details: Dict[str, Any] = None):
    """Crear alerta de seguridad"""
    audit_logger.create_security_alert(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        description=description,
        details=details or {}
    )

if __name__ == "__main__":
    # Ejemplo de uso
    audit_logger = AuditLogger()
    
    # Log de acciones
    log_user_action(
        user_id="admin",
        action=ActionType.LOGIN,
        resource_type="user",
        resource_id="admin",
        details={"login_method": "password"},
        ip_address="192.168.1.100",
        success=True
    )
    
    # Crear alerta de seguridad
    create_security_alert(
        event_type=SecurityEvent.FAILED_LOGIN,
        severity="high",
        user_id="test_user",
        ip_address="192.168.1.200",
        description="Múltiples intentos fallidos de login",
        details={"attempts": 5}
    )
    
    # Obtener rastro de auditoría
    trail = audit_logger.get_audit_trail(limit=10)
    print(f"Rastro de auditoría: {len(trail)} entradas")
    
    # Obtener alertas de seguridad
    alerts = audit_logger.get_security_alerts(limit=5)
    print(f"Alertas de seguridad: {len(alerts)} alertas")
    
    print("✅ Sistema de auditoría funcionando correctamente")



