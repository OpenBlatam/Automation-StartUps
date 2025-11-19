"""
Módulo de Procesamiento de Nómina y Gastos
Sistema automatizado para calcular horas, deducciones, pagos y procesar recibos con OCR
"""

from .hour_calculator import HourCalculator, TimeEntry, HoursType
from .deduction_calculator import DeductionCalculator, DeductionRule
from .payment_calculator import PaymentCalculator, PayPeriodCalculation
from .ocr_processor import OCRProcessor, OCRResult
from .storage import PayrollStorage
from .config import PayrollConfig
from .exceptions import (
    PayrollError,
    ConfigurationError,
    ValidationError,
    CalculationError,
    OCRError,
    StorageError,
    EmployeeNotFoundError,
)
from .utils import (
    get_pay_period_dates,
    format_currency,
    format_hours,
    validate_date_range,
    safe_decimal,
    calculate_percentage,
    calculate_yearly_total,
    calculate_pay_period_number,
    format_period_range,
    calculate_deduction_rate,
    is_business_day,
    get_business_days_between,
    calculate_effective_hourly_rate,
    round_to_nearest_cent,
    calculate_overtime_premium,
    log_calculation_summary,
    retry_on_failure,
)
from .notifications import PayrollNotifier
from .reports import PayrollReporter, PayrollReport
from .validators import PayrollValidator
from .audit import PayrollAuditor, AuditEventType
from .exporters import PayrollExporter
from .cache import PayrollCache, cached, make_cache_key
from .approvals import (
    PayrollApprovalSystem,
    ApprovalStatus,
    ApprovalLevel
)
from .integrations import (
    QuickBooksIntegration,
    StripeIntegration,
    AccountingIntegration,
    SlackIntegration
)
from .search import PayrollSearch, SearchFilters
from .metrics import PayrollMetricsCollector, PayrollMetrics
from .security import PayrollSecurity
from .optimizations import BatchProcessor, QueryOptimizer, performance_monitor
from .health_checks import PayrollHealthChecker, HealthStatus
from .maintenance import PayrollMaintenance
from .backup import PayrollBackup
from .analytics import PayrollAnalytics, AnomalyDetection
from .dashboard import PayrollDashboard, DashboardData
from .webhooks import PayrollWebhookHandler, PayrollWebhookReceiver, WebhookEventType
from .sync import PayrollSync, SyncResult
from .testing import PayrollTestData, PayrollTestHelpers
from .predictions import PayrollPredictor, PayrollPrediction
from .alerts import PayrollAlertSystem, Alert, AlertType, AlertSeverity
from .api import PayrollAPI, APIResponse
from .rate_limiting import PayrollRateLimiter, RateLimiter, Throttler
from .circuit_breaker import PayrollCircuitBreakers, CircuitBreaker, CircuitState, CircuitBreakerConfig
from .compliance import PayrollCompliance, ComplianceViolation, ComplianceRule, ComplianceSeverity
from .versioning import PayrollVersioning, DataVersion
from .migrations import PayrollMigrations, Migration
from .feature_flags import PayrollFeatureFlags, FeatureFlag, FeatureFlagConfig, feature_flags
from .observability import PayrollObservability, observe_operation, observability
from .events import PayrollEventBus, PayrollEvent, EventType, event_bus
from .recovery import PayrollRecovery, RecoveryPlan, RecoveryAction
from .config_advanced import PayrollAdvancedConfig
from .workflows import PayrollWorkflow, WorkflowStep, WorkflowExecution, WorkflowStatus, WorkflowStepStatus, create_payroll_workflow
from .benchmarking import PayrollBenchmark, BenchmarkResult
from .monitoring import PayrollMonitor, Metric, MetricType
from .helpers import PayrollHelpers
from .validation_advanced import AdvancedPayrollValidator, ValidationRule
from .debugging import (
    PayrollDebugger,
    PayrollProfiler,
    PayrollDataInspector,
    debug_timing,
    debug_context,
    log_function_call,
    enable_debug_mode,
    validate_data_integrity,
)
from .utilities_advanced import (
    PayrollAdvancedUtilities,
    format_payroll_summary,
    calculate_payroll_metrics_summary,
)
from .data_transformers import (
    PayrollDataTransformer,
    normalize_payroll_data,
)
from .formatters import (
    PayrollFormatter,
    PayrollComparisonFormatter,
)
from .comparators import PayrollComparator

__all__ = [
    "HourCalculator",
    "TimeEntry",
    "HoursType",
    "DeductionCalculator",
    "DeductionRule",
    "PaymentCalculator",
    "PayPeriodCalculation",
    "OCRProcessor",
    "OCRResult",
    "PayrollStorage",
    "PayrollConfig",
    "PayrollError",
    "ConfigurationError",
    "ValidationError",
    "CalculationError",
    "OCRError",
    "StorageError",
    "EmployeeNotFoundError",
    "get_pay_period_dates",
    "format_currency",
    "format_hours",
    "validate_date_range",
    "safe_decimal",
    "calculate_percentage",
    "calculate_yearly_total",
    "calculate_pay_period_number",
    "format_period_range",
    "calculate_deduction_rate",
    "is_business_day",
    "get_business_days_between",
    "calculate_effective_hourly_rate",
    "round_to_nearest_cent",
    "calculate_overtime_premium",
    "log_calculation_summary",
    "retry_on_failure",
    "PayrollNotifier",
    "PayrollReporter",
    "PayrollReport",
    "PayrollValidator",
    "PayrollAuditor",
    "AuditEventType",
    "PayrollExporter",
    "PayrollCache",
    "cached",
    "make_cache_key",
    "PayrollApprovalSystem",
    "ApprovalStatus",
    "ApprovalLevel",
    "QuickBooksIntegration",
    "StripeIntegration",
    "AccountingIntegration",
    "SlackIntegration",
    "PayrollSearch",
    "SearchFilters",
    "PayrollMetricsCollector",
    "PayrollMetrics",
    "PayrollSecurity",
    "BatchProcessor",
    "QueryOptimizer",
    "performance_monitor",
    "PayrollHealthChecker",
    "HealthStatus",
    "PayrollMaintenance",
    "PayrollBackup",
    "PayrollAnalytics",
    "AnomalyDetection",
    "PayrollDashboard",
    "DashboardData",
    "PayrollWebhookHandler",
    "PayrollWebhookReceiver",
    "WebhookEventType",
    "PayrollSync",
    "SyncResult",
    "PayrollTestData",
    "PayrollTestHelpers",
    "PayrollPredictor",
    "PayrollPrediction",
    "PayrollAlertSystem",
    "Alert",
    "AlertType",
    "AlertSeverity",
    "PayrollAPI",
    "APIResponse",
    "PayrollRateLimiter",
    "RateLimiter",
    "Throttler",
    "PayrollCircuitBreakers",
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerConfig",
    "PayrollCompliance",
    "ComplianceViolation",
    "ComplianceRule",
    "ComplianceSeverity",
    "PayrollVersioning",
    "DataVersion",
    "PayrollMigrations",
    "Migration",
    "PayrollFeatureFlags",
    "FeatureFlag",
    "FeatureFlagConfig",
    "feature_flags",
    "PayrollObservability",
    "observe_operation",
    "observability",
    "PayrollEventBus",
    "PayrollEvent",
    "EventType",
    "event_bus",
    "PayrollRecovery",
    "RecoveryPlan",
    "RecoveryAction",
    "PayrollAdvancedConfig",
    "PayrollWorkflow",
    "WorkflowStep",
    "WorkflowExecution",
    "WorkflowStatus",
    "WorkflowStepStatus",
    "create_payroll_workflow",
    "PayrollBenchmark",
    "BenchmarkResult",
    "PayrollMonitor",
    "Metric",
    "MetricType",
    "PayrollHelpers",
    "AdvancedPayrollValidator",
    "ValidationRule",
    # Debugging
    "PayrollDebugger",
    "PayrollProfiler",
    "PayrollDataInspector",
    "debug_timing",
    "debug_context",
    "log_function_call",
    "enable_debug_mode",
    "validate_data_integrity",
    # Advanced Utilities
    "PayrollAdvancedUtilities",
    "format_payroll_summary",
    "calculate_payroll_metrics_summary",
    # Data Transformers
    "PayrollDataTransformer",
    "normalize_payroll_data",
    # Formatters
    "PayrollFormatter",
    "PayrollComparisonFormatter",
    # Comparators
    "PayrollComparator",
]

