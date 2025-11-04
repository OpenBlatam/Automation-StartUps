"""
Constantes y valores de referencia para ads reporting.

Incluye:
- Umbrales de rendimiento estándar
- Valores de referencia de la industria
- Configuraciones por defecto
"""

from __future__ import annotations

# Umbrales de rendimiento (por industria)
INDUSTRY_BENCHMARKS = {
    "ctr": {
        "excellent": 2.0,
        "good": 1.0,
        "average": 0.5,
        "poor": 0.0
    },
    "cpc": {
        "social_media": {
            "excellent": 1.0,
            "good": 2.0,
            "average": 3.0,
            "poor": 5.0
        },
        "search": {
            "excellent": 2.0,
            "good": 3.0,
            "average": 5.0,
            "poor": 10.0
        }
    },
    "conversion_rate": {
        "excellent": 5.0,
        "good": 3.0,
        "average": 2.0,
        "poor": 1.0
    },
    "roas": {
        "excellent": 4.0,
        "good": 3.0,
        "average": 2.0,
        "poor": 1.0
    },
    "cpa": {
        "social_media": {
            "excellent": 20.0,
            "good": 40.0,
            "average": 60.0,
            "poor": 100.0
        },
        "search": {
            "excellent": 30.0,
            "good": 50.0,
            "average": 80.0,
            "poor": 150.0
        }
    }
}

# Configuraciones por defecto
DEFAULT_CONFIG = {
    "cache": {
        "enabled": True,
        "maxsize": 100,
        "ttl": 300  # 5 minutos
    },
    "retry": {
        "max_attempts": 3,
        "backoff": 1.0,
        "max_wait": 10
    },
    "rate_limit": {
        "delay": 0.5,
        "max_retry_after": 300
    },
    "validation": {
        "strict": False,
        "enable_dq_checks": True
    },
    "batch": {
        "chunk_size": 100,
        "max_workers": 5
    }
}

# Nombres de campos estándar
STANDARD_FIELDS = {
    "campaign": [
        "campaign_id",
        "campaign_name",
        "date_start",
        "date_stop",
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "revenue",
        "ctr",
        "cpc",
        "cpa",
        "roas",
        "conversion_rate"
    ],
    "audience": [
        "audience_type",
        "spend",
        "conversions",
        "revenue",
        "cpa",
        "conversion_value"
    ],
    "geographic": [
        "country",
        "region",
        "impressions",
        "clicks",
        "conversions",
        "spend",
        "cpa"
    ]
}

# Plataformas soportadas
SUPPORTED_PLATFORMS = [
    "facebook",
    "tiktok",
    "google",
    "linkedin",  # Futuro
    "twitter",   # Futuro
    "snapchat"   # Futuro
]

# Formatos de exportación soportados
EXPORT_FORMATS = [
    "csv",
    "json",
    "excel",
    "dataframe",
    "html",
    "markdown"
]

# Niveles de alerta
ALERT_LEVELS = {
    "INFO": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "CRITICAL": "critical"
}

# Códigos de estado comunes
STATUS_CODES = {
    "SUCCESS": "success",
    "PARTIAL": "partial",
    "FAILED": "failed",
    "SKIPPED": "skipped"
}

# Intervalos de tiempo comunes (en días)
TIME_INTERVALS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365
}

# Tipos de desglose soportados
BREAKDOWNS = {
    "facebook": [
        "age",
        "gender",
        "country",
        "region",
        "device_platform",
        "placement",
        "publisher_platform",
        "platform_position",
        "audience_type"
    ],
    "tiktok": [
        "age",
        "gender",
        "country_code",
        "ad_format",
        "device_type"
    ],
    "google": [
        "age",
        "gender",
        "location",
        "device",
        "ad_type",
        "network_type"
    ]
}

# Métricas calculadas comunes
CALCULATED_METRICS = [
    "ctr",           # Click-Through Rate
    "cpc",           # Cost Per Click
    "cpm",           # Cost Per Mille
    "cpa",           # Cost Per Acquisition
    "roas",          # Return on Ad Spend
    "conversion_rate",  # Conversion Rate
    "frequency",     # Frequency
    "reach",         # Reach
    "engagement_rate"  # Engagement Rate
]

# Niveles de agregación
AGGREGATION_LEVELS = [
    "campaign",
    "ad_set",        # Facebook
    "ad_group",      # Google, TikTok
    "ad",
    "creative",
    "audience",
    "device",
    "placement",
    "day",
    "hour"
]

def get_benchmark(
    metric: str,
    value: float,
    platform: str = "social_media",
    benchmark_type: str = "average"
) -> Dict[str, Any]:
    """
    Compara un valor con benchmarks de la industria.
    
    Args:
        metric: Métrica a comparar (ctr, cpc, etc.)
        value: Valor a comparar
        platform: Plataforma (social_media, search)
        benchmark_type: Tipo de benchmark (excellent, good, average, poor)
        
    Returns:
        Diccionario con comparación
    """
    benchmarks = INDUSTRY_BENCHMARKS.get(metric, {})
    
    if isinstance(benchmarks, dict) and platform in benchmarks:
        benchmarks = benchmarks[platform]
    
    if not isinstance(benchmarks, dict):
        return {"error": "Benchmark no disponible"}
    
    threshold = benchmarks.get(benchmark_type, 0)
    
    # Para métricas donde más es mejor (CTR, ROAS, conversion_rate)
    if metric in ["ctr", "roas", "conversion_rate"]:
        above_threshold = value >= threshold
    else:  # Para métricas donde menos es mejor (CPC, CPA)
        above_threshold = value <= threshold
    
    return {
        "metric": metric,
        "value": value,
        "benchmark": threshold,
        "benchmark_type": benchmark_type,
        "above_threshold": above_threshold,
        "performance": "good" if above_threshold else "below"
    }

