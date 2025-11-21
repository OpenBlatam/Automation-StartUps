"""
Sistema de Gestión de Tiempo y Asistencia
Registro automático de entradas/salidas, cálculo de horas, gestión de vacaciones y permisos
"""

from .storage import (
    TimeTrackingStorage,
    ClockEvent,
    EventType,
    WorkSession,
    SessionStatus,
    VacationRequest,
    VacationType,
    TimeDispute,
    DisputeType,
)
from .clock_manager import ClockManager
from .session_manager import SessionManager
from .vacation_manager import VacationManager
from .dispute_manager import DisputeManager
from .hour_calculator import TimeTrackingHourCalculator
from .validators import TimeTrackingValidator
from .notifications import TimeTrackingNotifier
from .geofencing import GeofencingValidator
from .timezone_manager import TimezoneManager
from .anomaly_detector import AnomalyDetector
from .api import TimeTrackingAPI
from .reports import TimeTrackingReporter
from .analytics import TimeTrackingAnalytics
from .notifications_advanced import AdvancedNotifier
from .integrations import (
    IntegrationManager,
    HRISIntegration,
    PayrollSystemIntegration,
    CalendarIntegration,
    SlackIntegration,
)
from .optimizations import (
    CacheManager,
    QueryOptimizer,
    PerformanceMonitor,
    DatabaseMaintenance,
    cached,
)
from .audit import AuditLogger

__all__ = [
    "ClockManager",
    "ClockEvent",
    "EventType",
    "SessionManager",
    "WorkSession",
    "SessionStatus",
    "VacationManager",
    "VacationRequest",
    "VacationType",
    "DisputeManager",
    "TimeDispute",
    "DisputeType",
    "TimeTrackingHourCalculator",
    "TimeTrackingStorage",
    "TimeTrackingValidator",
    "TimeTrackingNotifier",
    "GeofencingValidator",
    "TimezoneManager",
    "AnomalyDetector",
    "TimeTrackingAPI",
    "TimeTrackingReporter",
    "TimeTrackingAnalytics",
    "AdvancedNotifier",
    "IntegrationManager",
    "HRISIntegration",
    "PayrollSystemIntegration",
    "CalendarIntegration",
    "SlackIntegration",
    "CacheManager",
    "QueryOptimizer",
    "PerformanceMonitor",
    "DatabaseMaintenance",
    "cached",
    "AuditLogger",
]

