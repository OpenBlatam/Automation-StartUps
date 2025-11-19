"""
Módulo de Ads Reporting - Arquitectura Modular Completa

Sistema completo para extracción, procesamiento, validación y análisis de datos
de plataformas de publicidad (Facebook, TikTok, Google Ads).

📦 28 módulos implementados con 330+ funciones disponibles

🚀 Inicio Rápido:
    from ads_reporting import quick_extract_facebook
    
    result = quick_extract_facebook(days_back=7)
    print(f"Extraídos: {result['extracted']}, Guardados: {result['saved']}")

📚 Para ejemplos completos, ver: ads_reporting.examples

Módulos principales:
- Clientes: facebook_client, tiktok_client, google_client
- Procesamiento: extractors, processors, validators, storage
- Avanzado: integration, monitoring, batch_processor, analytics, optimization
- Utilidades: helpers, formatters, debugging, airflow_utils, quick_start
- Soporte: constants, examples, async_support
"""

from ads_reporting.base_client import (
    BaseAdsClient,
    APIConfig,
    AdsAPIError,
    AdsAuthError,
    AdsRateLimitError,
)
from ads_reporting.exceptions import (
    AdsReportingError,
    ConfigurationError,
    AuthenticationError,
    APIError,
    RateLimitError,
    ValidationError,
    DataQualityError,
    ExtractionError,
    StorageError,
    ProcessingError,
    create_error_summary,
)
from ads_reporting.facebook_client import (
    FacebookAdsClient,
    FacebookAdsConfig,
)
from ads_reporting.tiktok_client import (
    TikTokAdsClient,
    TikTokAdsConfig,
)
from ads_reporting.google_client import (
    GoogleAdsClient,
    GoogleAdsConfig,
)
from ads_reporting.extractors import (
    BaseExtractor,
    FacebookExtractor,
    TikTokExtractor,
)
from ads_reporting.storage import (
    BaseStorage,
    PostgreSQLStorage,
    S3Storage,
    get_storage,
)
from ads_reporting.processors import (
    BaseProcessor,
    CampaignProcessor,
    AudienceProcessor,
    GeographicProcessor,
    PerformanceMetrics,
    get_processor,
)
from ads_reporting.validators import (
    BaseValidator,
    SchemaValidator,
    ValueValidator,
    ConsistencyValidator,
    CompletenessValidator,
    ValidationResult,
    validate_campaign_data,
)
from ads_reporting.cache import (
    AdsCache,
    get_cache,
    set_cache,
)
from ads_reporting.config import (
    AdsReportingConfig,
    get_config,
    set_config,
)
from ads_reporting.helpers import (
    normalize_date,
    get_date_range,
    calculate_ctr,
    calculate_cpc,
    calculate_cpa,
    calculate_roas,
    normalize_platform_data,
    merge_campaign_data,
)
from ads_reporting.integration import (
    extract_and_store,
    compare_platforms,
    generate_performance_report,
)
from ads_reporting.monitoring import (
    PerformanceMonitor,
    DataQualityMonitor,
    AlertManager,
    AlertLevel,
    Alert,
    get_alert_manager,
    monitor_extraction,
)
from ads_reporting.batch_processor import (
    BatchProcessor,
    BatchResult,
    process_campaign_batch,
)
from ads_reporting.analytics import (
    analyze_trends,
    compare_periods,
    detect_significant_changes,
    segment_analysis,
    calculate_lift,
    find_top_performers,
    find_bottom_performers,
    TrendAnalysis,
    ComparisonResult,
)
from ads_reporting.reporting import (
    format_report_summary,
    export_to_csv,
    export_to_json,
    export_to_dataframe,
    generate_daily_summary,
    create_comparison_table,
    format_alert_summary,
)
from ads_reporting.utils_extended import (
    clean_campaign_name,
    normalize_currency,
    normalize_percentage,
    sanitize_id,
    truncate_text,
    flatten_dict,
    safe_get,
    chunk_list,
    remove_duplicates,
)
from ads_reporting.debugging import (
    timing_context,
    debug_function,
    inspect_data,
    diagnose_extraction_issues,
    log_data_sample,
    error_handler_context,
    profile_function,
)
from ads_reporting.optimization import (
    analyze_campaign_efficiency,
    suggest_budget_reallocation,
    detect_waste,
    optimize_ad_schedule,
    OptimizationRecommendation,
)
from ads_reporting.quick_start import (
    quick_extract_facebook,
    quick_report_facebook,
    quick_export_facebook,
    quick_compare_periods,
    quick_optimize_campaigns,
)
from ads_reporting.constants import (
    INDUSTRY_BENCHMARKS,
    DEFAULT_CONFIG,
    STANDARD_FIELDS,
    SUPPORTED_PLATFORMS,
    EXPORT_FORMATS,
    ALERT_LEVELS,
    get_benchmark,
)
from ads_reporting.formatters import (
    format_number,
    format_currency,
    format_percentage,
    format_duration,
    format_table,
    format_metric_change,
    format_summary_stats,
    format_list_summary,
    format_boolean,
    format_date_range,
)
from ads_reporting.airflow_utils import (
    get_dag_context,
    get_task_params,
    push_to_xcom,
    pull_from_xcom,
    create_airflow_task,
    extract_and_store_task,
    get_date_range_from_context,
    log_task_start,
    log_task_end,
    handle_task_error,
)

__all__ = [
    # Base
    "BaseAdsClient",
    "APIConfig",
    "AdsAPIError",
    "AdsAuthError",
    "AdsRateLimitError",
    # Exceptions (enhanced)
    "AdsReportingError",
    "ConfigurationError",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "ValidationError",
    "DataQualityError",
    "ExtractionError",
    "StorageError",
    "ProcessingError",
    "create_error_summary",
    # Clients
    "FacebookAdsClient",
    "FacebookAdsConfig",
    "TikTokAdsClient",
    "TikTokAdsConfig",
    "GoogleAdsClient",
    "GoogleAdsConfig",
    # Extractors
    "BaseExtractor",
    "FacebookExtractor",
    "TikTokExtractor",
    # Storage
    "BaseStorage",
    "PostgreSQLStorage",
    "S3Storage",
    "get_storage",
    # Processors
    "BaseProcessor",
    "CampaignProcessor",
    "AudienceProcessor",
    "GeographicProcessor",
    "PerformanceMetrics",
    "get_processor",
    # Validators
    "BaseValidator",
    "SchemaValidator",
    "ValueValidator",
    "ConsistencyValidator",
    "CompletenessValidator",
    "ValidationResult",
    "validate_campaign_data",
    # Cache
    "AdsCache",
    "get_cache",
    "set_cache",
    # Config
    "AdsReportingConfig",
    "get_config",
    "set_config",
    # Helpers
    "normalize_date",
    "get_date_range",
    "calculate_ctr",
    "calculate_cpc",
    "calculate_cpa",
    "calculate_roas",
    "normalize_platform_data",
    "merge_campaign_data",
    "validate_campaign_performance",
    "enrich_with_calculations",
    "create_summary_dict",
    # Integration
    "extract_and_store",
    "compare_platforms",
    "generate_performance_report",
    "optimize_campaign_budget",
    # Monitoring
    "PerformanceMonitor",
    "DataQualityMonitor",
    "AlertManager",
    "AlertLevel",
    "Alert",
    "get_alert_manager",
    "monitor_extraction",
    # Batch Processing
    "BatchProcessor",
    "BatchResult",
    "process_campaign_batch",
    # Analytics
    "analyze_trends",
    "compare_periods",
    "detect_significant_changes",
    "segment_analysis",
    "calculate_lift",
    "find_top_performers",
    "find_bottom_performers",
    "TrendAnalysis",
    "ComparisonResult",
    # Reporting
    "format_report_summary",
    "export_to_csv",
    "export_to_json",
    "export_to_dataframe",
    "export_to_excel",
    "generate_daily_summary",
    "create_comparison_table",
    "format_alert_summary",
    # Utils Extended
    "clean_campaign_name",
    "normalize_currency",
    "normalize_percentage",
    "sanitize_id",
    "truncate_text",
    "flatten_dict",
    "safe_get",
    "chunk_list",
    "remove_duplicates",
    # Debugging
    "timing_context",
    "debug_function",
    "inspect_data",
    "diagnose_extraction_issues",
    "log_data_sample",
    "error_handler_context",
    "profile_function",
    # Optimization
    "analyze_campaign_efficiency",
    "suggest_budget_reallocation",
    "detect_waste",
    "optimize_ad_schedule",
    "OptimizationRecommendation",
    # Quick Start
    "quick_extract_facebook",
    "quick_report_facebook",
    "quick_export_facebook",
    "quick_compare_periods",
    "quick_optimize_campaigns",
    # Constants
    "INDUSTRY_BENCHMARKS",
    "DEFAULT_CONFIG",
    "STANDARD_FIELDS",
    "SUPPORTED_PLATFORMS",
    "EXPORT_FORMATS",
    "ALERT_LEVELS",
    "get_benchmark",
    # Formatters
    "format_number",
    "format_currency",
    "format_percentage",
    "format_duration",
    "format_table",
    "format_metric_change",
    "format_summary_stats",
    "format_list_summary",
    "format_boolean",
    "format_date_range",
    # Airflow Utils
    "get_dag_context",
    "get_task_params",
    "push_to_xcom",
    "pull_from_xcom",
    "create_airflow_task",
    "extract_and_store_task",
    "get_date_range_from_context",
    "log_task_start",
    "log_task_end",
    "handle_task_error",
]

    GoogleAdsConfig,
)
from ads_reporting.extractors import (
    BaseExtractor,
    FacebookExtractor,
    TikTokExtractor,
)
from ads_reporting.storage import (
    BaseStorage,
    PostgreSQLStorage,
    S3Storage,
    get_storage,
)
from ads_reporting.processors import (
    BaseProcessor,
    CampaignProcessor,
    AudienceProcessor,
    GeographicProcessor,
    PerformanceMetrics,
    get_processor,
)
from ads_reporting.validators import (
    BaseValidator,
    SchemaValidator,
    ValueValidator,
    ConsistencyValidator,
    CompletenessValidator,
    ValidationResult,
    validate_campaign_data,
)
from ads_reporting.cache import (
    AdsCache,
    get_cache,
    set_cache,
)
from ads_reporting.config import (
    AdsReportingConfig,
    get_config,
    set_config,
)
from ads_reporting.helpers import (
    normalize_date,
    get_date_range,
    calculate_ctr,
    calculate_cpc,
    calculate_cpa,
    calculate_roas,
    normalize_platform_data,
    merge_campaign_data,
)
from ads_reporting.integration import (
    extract_and_store,
    compare_platforms,
    generate_performance_report,
)
from ads_reporting.monitoring import (
    PerformanceMonitor,
    DataQualityMonitor,
    AlertManager,
    AlertLevel,
    Alert,
    get_alert_manager,
    monitor_extraction,
)
from ads_reporting.batch_processor import (
    BatchProcessor,
    BatchResult,
    process_campaign_batch,
)
from ads_reporting.analytics import (
    analyze_trends,
    compare_periods,
    detect_significant_changes,
    segment_analysis,
    calculate_lift,
    find_top_performers,
    find_bottom_performers,
    TrendAnalysis,
    ComparisonResult,
)
from ads_reporting.reporting import (
    format_report_summary,
    export_to_csv,
    export_to_json,
    export_to_dataframe,
    generate_daily_summary,
    create_comparison_table,
    format_alert_summary,
)
from ads_reporting.utils_extended import (
    clean_campaign_name,
    normalize_currency,
    normalize_percentage,
    sanitize_id,
    truncate_text,
    flatten_dict,
    safe_get,
    chunk_list,
    remove_duplicates,
)
from ads_reporting.debugging import (
    timing_context,
    debug_function,
    inspect_data,
    diagnose_extraction_issues,
    log_data_sample,
    error_handler_context,
    profile_function,
)
from ads_reporting.optimization import (
    analyze_campaign_efficiency,
    suggest_budget_reallocation,
    detect_waste,
    optimize_ad_schedule,
    OptimizationRecommendation,
)
from ads_reporting.quick_start import (
    quick_extract_facebook,
    quick_report_facebook,
    quick_export_facebook,
    quick_compare_periods,
    quick_optimize_campaigns,
)
from ads_reporting.constants import (
    INDUSTRY_BENCHMARKS,
    DEFAULT_CONFIG,
    STANDARD_FIELDS,
    SUPPORTED_PLATFORMS,
    EXPORT_FORMATS,
    ALERT_LEVELS,
    get_benchmark,
)
from ads_reporting.formatters import (
    format_number,
    format_currency,
    format_percentage,
    format_duration,
    format_table,
    format_metric_change,
    format_summary_stats,
    format_list_summary,
    format_boolean,
    format_date_range,
)
from ads_reporting.airflow_utils import (
    get_dag_context,
    get_task_params,
    push_to_xcom,
    pull_from_xcom,
    create_airflow_task,
    extract_and_store_task,
    get_date_range_from_context,
    log_task_start,
    log_task_end,
    handle_task_error,
)
from ads_reporting.errors import (
    AdsReportingError,
    ConfigurationError,
    AuthenticationError,
    APIError,
    ValidationError,
    DataQualityError,
    RateLimitError,
    format_error_message,
    safe_execute,
    get_error_summary,
)

__all__ = [
    # Base
    "BaseAdsClient",
    "APIConfig",
    "AdsAPIError",
    "AdsAuthError",
    "AdsRateLimitError",
    # Clients
    "FacebookAdsClient",
    "FacebookAdsConfig",
    "TikTokAdsClient",
    "TikTokAdsConfig",
    "GoogleAdsClient",
    "GoogleAdsConfig",
    # Extractors
    "BaseExtractor",
    "FacebookExtractor",
    "TikTokExtractor",
    # Storage
    "BaseStorage",
    "PostgreSQLStorage",
    "S3Storage",
    "get_storage",
    # Processors
    "BaseProcessor",
    "CampaignProcessor",
    "AudienceProcessor",
    "GeographicProcessor",
    "PerformanceMetrics",
    "get_processor",
    # Validators
    "BaseValidator",
    "SchemaValidator",
    "ValueValidator",
    "ConsistencyValidator",
    "CompletenessValidator",
    "ValidationResult",
    "validate_campaign_data",
    # Cache
    "AdsCache",
    "get_cache",
    "set_cache",
    # Config
    "AdsReportingConfig",
    "get_config",
    "set_config",
    # Helpers
    "normalize_date",
    "get_date_range",
    "calculate_ctr",
    "calculate_cpc",
    "calculate_cpa",
    "calculate_roas",
    "normalize_platform_data",
    "merge_campaign_data",
    "validate_campaign_performance",
    "enrich_with_calculations",
    "create_summary_dict",
    # Integration
    "extract_and_store",
    "compare_platforms",
    "generate_performance_report",
    "optimize_campaign_budget",
    # Monitoring
    "PerformanceMonitor",
    "DataQualityMonitor",
    "AlertManager",
    "AlertLevel",
    "Alert",
    "get_alert_manager",
    "monitor_extraction",
    # Batch Processing
    "BatchProcessor",
    "BatchResult",
    "process_campaign_batch",
    # Analytics
    "analyze_trends",
    "compare_periods",
    "detect_significant_changes",
    "segment_analysis",
    "calculate_lift",
    "find_top_performers",
    "find_bottom_performers",
    "TrendAnalysis",
    "ComparisonResult",
    # Reporting
    "format_report_summary",
    "export_to_csv",
    "export_to_json",
    "export_to_dataframe",
    "export_to_excel",
    "generate_daily_summary",
    "create_comparison_table",
    "format_alert_summary",
    # Utils Extended
    "clean_campaign_name",
    "normalize_currency",
    "normalize_percentage",
    "sanitize_id",
    "truncate_text",
    "flatten_dict",
    "safe_get",
    "chunk_list",
    "remove_duplicates",
    # Debugging
    "timing_context",
    "debug_function",
    "inspect_data",
    "diagnose_extraction_issues",
    "log_data_sample",
    "error_handler_context",
    "profile_function",
    # Optimization
    "analyze_campaign_efficiency",
    "suggest_budget_reallocation",
    "detect_waste",
    "optimize_ad_schedule",
    "OptimizationRecommendation",
    # Quick Start
    "quick_extract_facebook",
    "quick_report_facebook",
    "quick_export_facebook",
    "quick_compare_periods",
    "quick_optimize_campaigns",
    # Constants
    "INDUSTRY_BENCHMARKS",
    "DEFAULT_CONFIG",
    "STANDARD_FIELDS",
    "SUPPORTED_PLATFORMS",
    "EXPORT_FORMATS",
    "ALERT_LEVELS",
    "get_benchmark",
    # Formatters
    "format_number",
    "format_currency",
    "format_percentage",
    "format_duration",
    "format_table",
    "format_metric_change",
    "format_summary_stats",
    "format_list_summary",
    "format_boolean",
    "format_date_range",
    # Airflow Utils
    "get_dag_context",
    "get_task_params",
    "push_to_xcom",
    "pull_from_xcom",
    "create_airflow_task",
    "extract_and_store_task",
    "get_date_range_from_context",
    "log_task_start",
    "log_task_end",
    "handle_task_error",
]
