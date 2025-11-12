"""
Manejo de Errores Robusto para Troubleshooting
Sistema centralizado de manejo de errores y logging
"""

import logging
import traceback
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severidad de errores"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categorías de errores"""
    VALIDATION = "validation"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    CONFIGURATION = "configuration"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Contexto de un error"""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime
    session_id: Optional[str] = None
    ticket_id: Optional[str] = None
    user_id: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TroubleshootingErrorHandler:
    """Manejo centralizado de errores"""
    
    def __init__(self, log_to_db: bool = False, db_connection=None):
        self.log_to_db = log_to_db
        self.db_connection = db_connection
        self.error_history: List[ErrorContext] = []
    
    def handle_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict] = None,
        session_id: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> ErrorContext:
        """Maneja un error y retorna contexto"""
        error_context = ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            category=category,
            timestamp=datetime.now(),
            session_id=session_id,
            ticket_id=ticket_id,
            stack_trace=traceback.format_exc(),
            metadata=context or {}
        )
        
        # Log según severidad
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"[{category.value}] {error_context.error_message}", exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"[{category.value}] {error_context.error_message}", exc_info=True)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"[{category.value}] {error_context.error_message}")
        else:
            logger.info(f"[{category.value}] {error_context.error_message}")
        
        # Guardar en historial
        self.error_history.append(error_context)
        
        # Guardar en BD si está configurado
        if self.log_to_db and self.db_connection:
            self._save_to_db(error_context)
        
        return error_context
    
    def _save_to_db(self, error_context: ErrorContext):
        """Guarda error en base de datos"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO support_troubleshooting_errors (
                    error_type, error_message, severity, category,
                    session_id, ticket_id, stack_trace, metadata, occurred_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                error_context.error_type,
                error_context.error_message,
                error_context.severity.value,
                error_context.category.value,
                error_context.session_id,
                error_context.ticket_id,
                error_context.stack_trace,
                json.dumps(error_context.metadata),
                error_context.timestamp
            ))
            self.db_connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error guardando error en BD: {e}")
    
    def get_error_stats(self, hours: int = 24) -> Dict:
        """Obtiene estadísticas de errores"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            e for e in self.error_history
            if e.timestamp >= cutoff
        ]
        
        return {
            "total_errors": len(recent_errors),
            "by_severity": {
                severity.value: sum(1 for e in recent_errors if e.severity == severity)
                for severity in ErrorSeverity
            },
            "by_category": {
                category.value: sum(1 for e in recent_errors if e.category == category)
                for category in ErrorCategory
            },
            "most_common": self._get_most_common_errors(recent_errors)
        }
    
    def _get_most_common_errors(self, errors: List[ErrorContext], limit: int = 5) -> List[Dict]:
        """Obtiene errores más comunes"""
        error_counts = {}
        for error in errors:
            key = f"{error.error_type}: {error.error_message[:100]}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        return [
            {"error": error, "count": count}
            for error, count in sorted(
                error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
        ]


def safe_execute(func, *args, error_handler: Optional[TroubleshootingErrorHandler] = None, **kwargs):
    """Wrapper para ejecutar funciones de forma segura"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_handler:
            error_handler.handle_error(
                e,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.BUSINESS_LOGIC,
                context={"function": func.__name__, "args": str(args)[:200]}
            )
        raise



