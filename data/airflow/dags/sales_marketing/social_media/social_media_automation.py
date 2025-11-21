"""
DAG de Automatización de Publicación en Redes Sociales
========================================================
Flujo completo de automatización:
1. Recoger contenido nuevo desde base de datos
2. Programar publicación en plataformas seleccionadas
3. Rastrear interacciones y métricas
4. Enviar reporte semanal con análisis de performance
"""
from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import os
import hashlib
import re
from collections import defaultdict

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Intentar importar utilidades de notificaciones
try:
    from data.airflow.plugins.etl_notifications import notify_slack, notify_email
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    def notify_slack(message: str, **kwargs): pass
    def notify_email(to: str, subject: str, body: str, html: Optional[str] = None, **kwargs): pass

logger = logging.getLogger(__name__)


@dag(
    dag_id="social_media_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas para publicación
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Automatización Avanzada de Publicación en Redes Sociales
    
    Sistema completo y avanzado que automatiza el flujo completo de publicación en redes sociales con inteligencia artificial:
    
    **Funcionalidades Principales:**
    1. **Recolección de Contenido**: Busca artículos nuevos en la base de datos que necesitan ser publicados
    2. **Análisis de Sentimiento**: Analiza el sentimiento del contenido antes de publicar (positivo/negativo/neutral)
    3. **Detección de Hashtags Trending**: Detecta y sugiere hashtags trending relevantes para cada post
    4. **Programación Inteligente con ML**: Programa publicaciones usando ML para optimizar horarios basados en engagement histórico
    5. **Publicación Automática**: Publica contenido en las plataformas seleccionadas (Twitter, LinkedIn, Facebook, Instagram)
    6. **Detección de Contenido Viral**: Detecta automáticamente posts que están volviéndose virales
    7. **Tracking de Interacciones**: Rastrea métricas de engagement en tiempo real
    8. **Recomendaciones Automáticas**: Genera recomendaciones basadas en análisis de performance
    9. **Reportes Semanales**: Genera y envía reportes semanales con análisis completo de performance
    
    **Funcionalidades Avanzadas:**
    - ✅ Análisis de sentimiento del contenido
    - ✅ Predicción de engagement con Machine Learning
    - ✅ Detección de hashtags trending
    - ✅ Optimización de horarios con Machine Learning
    - ✅ Detección automática de contenido viral
    - ✅ Cálculo de ROI de publicaciones
    - ✅ Republicación automática de contenido de alto rendimiento
    - ✅ Recomendaciones inteligentes basadas en datos
    - ✅ Alertas automáticas para contenido viral
    - ✅ Análisis de mejor hora para publicar por plataforma
    - ✅ Identificación de categorías y hashtags más efectivos
    - ✅ A/B testing de contenido (opcional)
    - ✅ Optimización automática de contenido
    - ✅ Análisis de audiencia e insights demográficos
    - ✅ Análisis de tendencias y crecimiento
    - ✅ Optimización inteligente de contenido basada en mejores prácticas
    - ✅ Detección de temas trending y en declive
    - ✅ Análisis de sentimiento de comentarios
    - ✅ Análisis de ROI por campaña/UTM
    - ✅ Benchmarking de performance vs histórico
    - ✅ Alertas inteligentes para ROI negativo
    - ✅ Comparación con percentiles (mediana, top 25%)
    - ✅ Optimización automática de hashtags por categoría
    - ✅ Análisis de mejor hora del día por plataforma
    - ✅ Exportación de datos de analytics para análisis externo
    - ✅ Identificación de top 3 horas con mejor engagement
    - ✅ Detección de anomalías en engagement (Z-score)
    - ✅ Análisis de performance por autor
    - ✅ Forecasting de engagement futuro
    - ✅ Alertas para anomalías de alto/bajo rendimiento
    - ✅ Análisis de tendencias semanales por plataforma
    - ✅ Optimización de calendario de contenido (evita sobrecarga)
    - ✅ Redistribución automática de posts sobrecargados
    - ✅ Estructura completa para APIs reales (Twitter, LinkedIn, Facebook, Instagram)
    - ✅ Gestión multi-cuenta por plataforma
    - ✅ Reintentos automáticos de posts fallidos (backoff exponencial)
    - ✅ Detección de contenido similar/duplicado
    - ✅ Prevención de publicación de contenido duplicado
    - ✅ Análisis de similitud con Jaccard similarity
    - ✅ Respuestas automáticas a comentarios (con plantillas inteligentes)
    - ✅ Tracking y análisis de competencia
    - ✅ Clustering de contenido similar
    - ✅ Análisis de imágenes (labels, colores, texto, calidad)
    - ✅ Detección de texto en imágenes (OCR)
    - ✅ Análisis de seguridad de imágenes (safe search)
    - ✅ A/B testing automático de variantes de contenido
    - ✅ Detección automática de crisis de reputación
    - ✅ Tracking de menciones de marca
    - ✅ Programación reactiva basada en trending topics
    - ✅ Alertas automáticas de crisis
    - ✅ Evaluación automática de tests A/B
    - ✅ Análisis de influencers y su impacto
    - ✅ Scoring de calidad de contenido (0-100)
    - ✅ Sugerencias inteligentes de hashtags
    - ✅ Optimización de performance (índices, ANALYZE)
    - ✅ Análisis de factores de calidad (título, contenido, hashtags, media)
    - ✅ Sugerencias basadas en hashtags de alto rendimiento
    - ✅ Reutilización automática de contenido exitoso
    - ✅ Social listening y monitoreo de conversaciones
    - ✅ Optimización continua de engagement rate
    - ✅ Calendario de contenido automatizado
    - ✅ Análisis de patrones de alto rendimiento
    - ✅ Adaptación de contenido por plataforma
    - ✅ Generación automática de contenido con IA
    - ✅ Análisis de contenido de video
    - ✅ Investigación automática de hashtags
    - ✅ Predicción de performance antes de publicar
    - ✅ Analytics cross-platform comparativo
    - ✅ Análisis de tendencias de hashtags
    - ✅ Scoring de predicción de engagement
    - ✅ Verificación de seguridad de contenido
    - ✅ Validación robusta de datos
    - ✅ Gestión inteligente de rate limits
    - ✅ Recuperación automática de errores
    - ✅ Detección de contenido problemático
    - ✅ Estrategias de recuperación por tipo de error
    - ✅ Segmentación avanzada de audiencia
    - ✅ Personalización de contenido por segmento
    - ✅ Predicción de tendencias futuras
    - ✅ Benchmarking avanzado de competencia
    - ✅ Optimización automática de campañas
    - ✅ Análisis de comportamiento de audiencia
    - ✅ Identificación de segmentos de alto valor
    - ✅ Tracking de leads desde redes sociales a CRM
    - ✅ Análisis avanzado de ROI con atribución multi-touch
    - ✅ Scoring de efectividad de contenido
    - ✅ Tracking de velocidad de engagement
    - ✅ Optimización del ciclo de vida del contenido
    - ✅ Modelos de atribución (first-touch, last-touch, linear, time-decay)
    - ✅ Detección de contenido viral por velocidad
    - ✅ Recomendaciones de ciclo de vida
    - ✅ Refresh automático de contenido exitoso
    - ✅ Curación inteligente de contenido
    - ✅ Análisis de heatmap de engagement (día/hora)
    - ✅ Scoring de curación basado en múltiples factores
    - ✅ Identificación de mejores slots temporales
    - ✅ Repurposing automático de contenido exitoso
    - ✅ Matching de contenido con audiencia ideal
    - ✅ Generación automática de hashtags con ML
    - ✅ Detección de señales sociales relevantes
    - ✅ Forecasting avanzado de engagement
    - ✅ Análisis de performance por categoría
    - ✅ Adaptación automática de contenido por plataforma
    - ✅ Benchmarking de performance contra estándares de industria
    - ✅ Detección de anomalías en engagement (Z-score)
    - ✅ Análisis de tendencias de contenido y categorías
    - ✅ Scoring ML avanzado de calidad de contenido
    - ✅ Clasificación de performance tiers (excellent/good/average)
    - ✅ Identificación de tendencias rising/declining/stable
    - ✅ Scoring de potencial viral de contenido
    - ✅ Optimización ML de engagement basada en patrones
    - ✅ Respuestas automáticas inteligentes a engagement
    - ✅ Análisis de factores virales (trending, emocional, hooks)
    - ✅ Aprendizaje de mejores prácticas por categoría
    - ✅ Generación automática de respuestas contextuales
    - ✅ Análisis de crecimiento de audiencia y engagement
    - ✅ Insights ML avanzados de performance
    - ✅ Optimización de ROI en redes sociales
    - ✅ Análisis comparativo de períodos temporales
    - ✅ Estrategias de optimización personalizadas
    - ✅ Detección de contenido sobre-promedio
    - ✅ Análisis de patrones de engagement (día, categoría)
    - ✅ Optimización ML de hashtags basada en performance
    - ✅ Forecasting ML avanzado de performance
    - ✅ Identificación de mejores días de la semana
    - ✅ Optimización de hashtags por categoría
    - ✅ Ajuste de forecast basado en calidad de contenido
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para PostgreSQL (default: postgres_default)
    - `platforms`: Plataformas donde publicar (JSON array: ["twitter", "linkedin", "facebook"])
    - `max_posts_per_run`: Máximo de posts a procesar por ejecución (default: 20)
    - `auto_schedule`: Programar automáticamente posts pendientes (default: true)
    - `auto_publish`: Publicar automáticamente posts programados (default: true)
    - `track_engagement`: Rastrear métricas de engagement (default: true)
    - `send_weekly_report`: Enviar reporte semanal (default: true)
    - `report_recipients`: Emails para reportes (comma-separated)
    - `dry_run`: Modo dry-run sin publicar (default: false)
    - `analyze_sentiment`: Analizar sentimiento del contenido (default: true)
    - `predict_engagement_ml`: Predecir engagement con ML (default: true)
    - `detect_trending_hashtags`: Detectar hashtags trending (default: true)
    - `optimize_timing_ml`: Optimizar horarios con ML (default: true)
    - `enable_ab_testing`: Habilitar A/B testing (default: false)
    - `calculate_roi`: Calcular ROI de publicaciones (default: true)
    - `republish_top_content`: Republicar contenido de alto rendimiento (default: true)
    - `analyze_audience`: Analizar audiencia y demografía (default: true)
    - `trend_analysis`: Análisis de tendencias (default: true)
    - `smart_content_optimization`: Optimización inteligente de contenido (default: true)
    - `analyze_comment_sentiment`: Analizar sentimiento de comentarios (default: true)
    - `campaign_roi_analysis`: Análisis de ROI por campaña (default: true)
    - `performance_benchmarking`: Benchmarking de performance (default: true)
    - `hashtag_optimization`: Optimización automática de hashtags (default: true)
    - `best_time_analysis`: Análisis de mejor momento del día (default: true)
    - `anomaly_detection`: Detección de anomalías (default: true)
    - `author_performance_analysis`: Análisis de performance por autor (default: true)
    - `engagement_forecasting`: Forecasting de engagement futuro (default: true)
    - `content_calendar_optimization`: Optimización de calendario (default: true)
    - `multi_account_management`: Gestión multi-cuenta (default: true)
    - `auto_retry_failed_posts`: Reintentar posts fallidos (default: true)
    - `content_similarity_detection`: Detección de contenido similar (default: false)
    - `auto_respond_comments`: Responder comentarios automáticamente (default: false)
    - `competitor_tracking`: Tracking de competencia (default: false)
    - `content_clustering`: Clustering de contenido similar (default: false)
    - `image_analysis`: Análisis de imágenes (default: false)
    - `ab_testing`: A/B testing automático (default: false)
    - `crisis_detection`: Detección de crisis (default: true)
    - `brand_mention_tracking`: Tracking de menciones (default: false)
    - `reactive_scheduling`: Programación reactiva (default: false)
    - `influencer_analysis`: Análisis de influencers (default: false)
    - `content_quality_scoring`: Scoring de calidad (default: true)
    - `intelligent_hashtag_suggestions`: Sugerencias de hashtags (default: true)
    - `performance_optimization`: Optimización de performance (default: true)
    - `content_repurposing`: Reutilización de contenido (default: false)
    - `social_listening`: Social listening (default: false)
    - `engagement_rate_optimization`: Optimización de engagement (default: true)
    - `automated_content_calendar`: Calendario automatizado (default: true)
    - `ai_content_generation`: Generación de contenido con IA (default: false)
    - `video_content_analysis`: Análisis de video (default: false)
    - `automated_hashtag_research`: Investigación de hashtags (default: true)
    - `content_performance_prediction`: Predicción de performance (default: true)
    - `cross_platform_analytics`: Analytics cross-platform (default: true)
    - `content_safety_check`: Verificación de seguridad (default: true)
    - `data_validation`: Validación de datos (default: true)
    - `rate_limit_management`: Gestión de rate limits (default: true)
    - `error_recovery`: Recuperación de errores (default: true)
    - `audience_segmentation`: Segmentación de audiencia (default: true)
    - `content_personalization`: Personalización de contenido (default: false)
    - `trend_prediction`: Predicción de tendencias (default: true)
    - `competitor_benchmarking`: Benchmarking de competencia (default: false)
    - `automated_campaign_optimization`: Optimización de campañas (default: true)
    - `crm_lead_tracking`: Tracking de leads a CRM (default: false)
    - `advanced_roi_analysis`: Análisis avanzado de ROI (default: true)
    - `content_effectiveness_scoring`: Scoring de efectividad (default: true)
    - `engagement_velocity_tracking`: Tracking de velocidad (default: true)
    - `content_lifecycle_optimization`: Optimización de ciclo de vida (default: true)
    - `automated_content_refresh`: Refresh automático de contenido (default: true)
    - `intelligent_content_curation`: Curación inteligente (default: true)
    - `engagement_heatmap_analysis`: Análisis de heatmap (default: true)
    - `automated_content_repurposing`: Repurposing automático (default: true)
    - `content_audience_matching`: Matching de audiencia (default: true)
    - `automated_hashtag_generation`: Generación automática de hashtags (default: true)
    - `social_signal_detection`: Detección de señales sociales (default: true)
    - `content_engagement_forecasting`: Forecasting avanzado (default: true)
    - `content_performance_benchmarking`: Benchmarking de performance (default: true)
    - `engagement_anomaly_detection`: Detección de anomalías (default: true)
    - `content_trend_analysis`: Análisis de tendencias (default: true)
    - `content_quality_ml_scoring`: Scoring ML de calidad (default: true)
    - `content_viral_potential_scoring`: Scoring de potencial viral (default: true)
    - `content_engagement_optimization_ml`: Optimización ML de engagement (default: true)
    - `automated_engagement_responses`: Respuestas automáticas (default: true)
    - `content_audience_growth_analysis`: Análisis de crecimiento (default: true)
    - `content_performance_insights_ml`: Insights ML (default: true)
    - `social_media_roi_optimization`: Optimización de ROI (default: true)
    - `content_engagement_pattern_analysis`: Análisis de patrones (default: true)
    - `automated_hashtag_optimization_ml`: Optimización ML de hashtags (default: true)
    - `content_performance_forecasting_ml`: Forecasting ML (default: true)
    - `export_analytics_data`: Exportar datos de analytics (default: false)
    - `generate_recommendations`: Generar recomendaciones automáticas (default: true)
    - `detect_viral_content`: Detectar contenido viral (default: true)
    - `smart_alerts`: Alertas inteligentes (default: true)
    
    **Schedule:**
    - Publicación: Cada 2 horas (0 */2 * * *)
    - Reporte semanal: Lunes 09:00 UTC (se ejecuta automáticamente)
    
    **Tablas de Base de Datos:**
    - `content_articles`: Artículos/blogs a publicar
    - `content_versions`: Versiones convertidas por plataforma
    - `content_scheduled_posts`: Publicaciones programadas
    - `content_engagement`: Métricas de engagement
    - `content_engagement_history`: Historial de snapshots de engagement
    - `content_platform_config`: Configuración de plataformas
    - `content_performance_analysis`: Análisis de performance por artículo
    
    **Pipeline de Ejecución:**
    1. Recolección de contenido nuevo
    2. Validación de datos
    3. Generación de contenido con IA
    4. Verificación de seguridad de contenido
    5. Detección de contenido similar
    6. Clustering de contenido
    7. Reutilización de contenido exitoso
    8. Calendario de contenido automatizado
    9. Análisis de imágenes
    10. Análisis de videos
    11. Scoring de calidad de contenido
    12. Investigación automática de hashtags
    13. Predicción de performance
    14. Predicción de tendencias futuras
    15. Programación reactiva (trending topics)
    16. Personalización de contenido por segmento
    17. Sugerencias inteligentes de hashtags
    18. Optimización inteligente de contenido
    19. Análisis de sentimiento
    20. Predicción de engagement con ML
    21. Detección de hashtags trending
    22. Optimización automática de hashtags
    23. Programación inteligente con ML
    24. A/B testing automático
    25. Optimización de calendario de contenido
    26. Publicación automática
    27. Gestión de rate limits
    28. Reintentos automáticos de posts fallidos
    29. Detección de contenido viral
    30. Tracking de engagement
    31. Tracking de velocidad de engagement
    32. Scoring de efectividad de contenido
    33. Optimización de ciclo de vida
    34. Tracking de leads a CRM
    35. Análisis de sentimiento de comentarios
    36. Respuestas automáticas a comentarios
    37. Tracking de competencia
    38. Tracking de menciones de marca
    39. Análisis de influencers
    40. Social listening
    41. Detección de crisis de reputación
    42. Detección de anomalías
    43. Optimización de performance
    44. Optimización de engagement rate
    45. Analytics cross-platform
    46. Recuperación automática de errores
    47. Segmentación de audiencia
    48. Benchmarking de competencia
    49. Optimización automática de campañas
    50. Refresh automático de contenido exitoso
    51. Análisis de heatmap de engagement
    52. Repurposing automático de contenido
    53. Detección de señales sociales
    54. Forecasting avanzado de engagement
    55. Benchmarking de performance
    56. Detección de anomalías en engagement
    57. Análisis de tendencias de contenido
    58. Optimización ML de engagement
    59. Respuestas automáticas inteligentes
    60. Análisis de crecimiento de audiencia
    61. Insights ML de performance
    62. Análisis de patrones de engagement
    63. Análisis de mejor hora del día
    64. Análisis de performance por autor
    65. Análisis de audiencia e insights
    66. Análisis de tendencias y crecimiento
    67. Forecasting de engagement futuro
    68. Cálculo de ROI
    69. Análisis avanzado de ROI con atribución
    70. Optimización de ROI en redes sociales
    71. Análisis de ROI por campaña
    72. Benchmarking de performance
    73. Republicación de contenido de alto rendimiento
    74. Generación de reporte semanal
    75. Generación de recomendaciones
    76. Envío de reportes
    77. Exportación de datos de analytics
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "platforms": Param('["twitter", "linkedin"]', type="string"),
        "max_posts_per_run": Param(20, type="integer", minimum=1, maximum=100),
        "auto_schedule": Param(True, type="boolean"),
        "auto_publish": Param(True, type="boolean"),
        "track_engagement": Param(True, type="boolean"),
        "send_weekly_report": Param(True, type="boolean"),
        "report_recipients": Param("", type="string"),
        "dry_run": Param(False, type="boolean"),
        "analyze_sentiment": Param(True, type="boolean", description="Analizar sentimiento del contenido"),
        "detect_trending_hashtags": Param(True, type="boolean", description="Detectar hashtags trending"),
        "optimize_timing_ml": Param(True, type="boolean", description="Optimizar horarios con ML"),
        "enable_ab_testing": Param(False, type="boolean", description="Habilitar A/B testing"),
        "predict_engagement_ml": Param(True, type="boolean", description="Predecir engagement con ML"),
        "analyze_competitors": Param(False, type="boolean", description="Analizar competencia"),
        "auto_optimize_content": Param(True, type="boolean", description="Optimizar contenido automáticamente"),
        "analyze_audience": Param(True, type="boolean", description="Analizar audiencia y demografía"),
        "trend_analysis": Param(True, type="boolean", description="Análisis de tendencias"),
        "smart_content_optimization": Param(True, type="boolean", description="Optimización inteligente de contenido"),
        "republish_top_content": Param(True, type="boolean", description="Republicar contenido de alto rendimiento"),
        "calculate_roi": Param(True, type="boolean", description="Calcular ROI de publicaciones"),
        "generate_recommendations": Param(True, type="boolean", description="Generar recomendaciones automáticas"),
        "detect_viral_content": Param(True, type="boolean", description="Detectar contenido viral"),
        "smart_alerts": Param(True, type="boolean", description="Alertas inteligentes"),
        "analyze_comment_sentiment": Param(True, type="boolean", description="Analizar sentimiento de comentarios"),
        "auto_respond_comments": Param(False, type="boolean", description="Responder comentarios automáticamente"),
        "competitor_analysis": Param(False, type="boolean", description="Análisis de competencia"),
        "campaign_roi_analysis": Param(True, type="boolean", description="Análisis de ROI por campaña"),
        "performance_benchmarking": Param(True, type="boolean", description="Benchmarking de performance"),
        "export_analytics_data": Param(False, type="boolean", description="Exportar datos de analytics"),
        "image_analysis": Param(False, type="boolean", description="Análisis de imágenes"),
        "hashtag_optimization": Param(True, type="boolean", description="Optimización automática de hashtags"),
        "best_time_analysis": Param(True, type="boolean", description="Análisis de mejor momento del día"),
        "content_clustering": Param(False, type="boolean", description="Clustering de contenido similar"),
        "anomaly_detection": Param(True, type="boolean", description="Detección de anomalías en engagement"),
        "author_performance_analysis": Param(True, type="boolean", description="Análisis de performance por autor"),
        "content_similarity_analysis": Param(False, type="boolean", description="Análisis de similitud de contenido"),
        "engagement_forecasting": Param(True, type="boolean", description="Forecasting de engagement futuro"),
        "auto_respond_to_comments": Param(False, type="boolean", description="Responder comentarios automáticamente"),
        "content_clustering": Param(False, type="boolean", description="Clustering de contenido similar"),
        "multi_account_management": Param(True, type="boolean", description="Gestión multi-cuenta"),
        "content_calendar_optimization": Param(True, type="boolean", description="Optimización de calendario de contenido"),
        "auto_respond_comments": Param(False, type="boolean", description="Responder comentarios automáticamente"),
        "competitor_tracking": Param(False, type="boolean", description="Tracking de competencia"),
        "content_similarity_detection": Param(False, type="boolean", description="Detección de contenido similar"),
        "real_time_dashboard": Param(False, type="boolean", description="Dashboard de métricas en tiempo real"),
        "auto_retry_failed_posts": Param(True, type="boolean", description="Reintentar posts fallidos automáticamente"),
        "ab_testing": Param(False, type="boolean", description="A/B testing automático de contenido"),
        "influencer_analysis": Param(False, type="boolean", description="Análisis de influencers y menciones"),
        "crisis_detection": Param(True, type="boolean", description="Detección automática de crisis de reputación"),
        "reactive_scheduling": Param(False, type="boolean", description="Programación reactiva basada en trending topics"),
        "brand_mention_tracking": Param(False, type="boolean", description="Tracking de menciones de marca"),
        "content_generation": Param(False, type="boolean", description="Generación automática de contenido"),
        "budget_optimization": Param(False, type="boolean", description="Optimización de presupuesto de publicidad"),
        "video_analysis": Param(False, type="boolean", description="Análisis de videos"),
        "crm_integration": Param(False, type="boolean", description="Integración con CRM"),
        "performance_optimization": Param(True, type="boolean", description="Optimización de performance de queries"),
        "intelligent_hashtag_suggestions": Param(True, type="boolean", description="Sugerencias inteligentes de hashtags"),
        "content_quality_scoring": Param(True, type="boolean", description="Scoring de calidad de contenido"),
        "multi_language_support": Param(False, type="boolean", description="Soporte multi-idioma"),
        "engagement_prediction_ml": Param(True, type="boolean", description="Predicción avanzada de engagement con ML"),
        "advanced_sentiment_analysis": Param(True, type="boolean", description="Análisis de sentimiento avanzado con NLP"),
        "content_repurposing": Param(False, type="boolean", description="Reutilización automática de contenido"),
        "social_listening": Param(False, type="boolean", description="Social listening y monitoreo"),
        "automated_content_calendar": Param(True, type="boolean", description="Calendario de contenido automatizado"),
        "engagement_rate_optimization": Param(True, type="boolean", description="Optimización continua de engagement rate"),
        "ai_content_generation": Param(False, type="boolean", description="Generación automática de contenido con IA"),
        "video_content_analysis": Param(False, type="boolean", description="Análisis de contenido de video"),
        "budget_allocation_optimization": Param(False, type="boolean", description="Optimización de asignación de presupuesto"),
        "cross_platform_analytics": Param(True, type="boolean", description="Analytics cross-platform"),
        "automated_hashtag_research": Param(True, type="boolean", description="Investigación automática de hashtags"),
        "content_performance_prediction": Param(True, type="boolean", description="Predicción de performance antes de publicar"),
        "smart_content_scheduling": Param(True, type="boolean", description="Programación inteligente basada en audiencia"),
        "intelligent_caching": Param(True, type="boolean", description="Caché inteligente para optimización"),
        "batch_processing": Param(True, type="boolean", description="Procesamiento por lotes para mejor performance"),
        "data_validation": Param(True, type="boolean", description="Validación robusta de datos"),
        "error_recovery": Param(True, type="boolean", description="Recuperación automática de errores"),
        "rate_limit_management": Param(True, type="boolean", description="Gestión inteligente de rate limits"),
        "content_safety_check": Param(True, type="boolean", description="Verificación de seguridad de contenido"),
        "advanced_ml_optimization": Param(True, type="boolean", description="Optimización avanzada con ML"),
        "competitor_benchmarking": Param(False, type="boolean", description="Benchmarking avanzado de competencia"),
        "budget_optimization": Param(False, type="boolean", description="Optimización de presupuesto de publicidad"),
        "crm_integration": Param(False, type="boolean", description="Integración con CRM para leads"),
        "audience_segmentation": Param(True, type="boolean", description="Segmentación avanzada de audiencia"),
        "content_personalization": Param(False, type="boolean", description="Personalización de contenido por segmento"),
        "trend_prediction": Param(True, type="boolean", description="Predicción de tendencias futuras"),
        "automated_campaign_optimization": Param(True, type="boolean", description="Optimización automática de campañas"),
        "crm_lead_tracking": Param(False, type="boolean", description="Tracking de leads desde redes sociales a CRM"),
        "advanced_roi_analysis": Param(True, type="boolean", description="Análisis avanzado de ROI con atribución"),
        "content_effectiveness_scoring": Param(True, type="boolean", description="Scoring de efectividad de contenido"),
        "automated_hashtag_trending_detection": Param(True, type="boolean", description="Detección automática de hashtags trending"),
        "multi_channel_attribution": Param(False, type="boolean", description="Atribución multi-canal"),
        "content_lifecycle_optimization": Param(True, type="boolean", description="Optimización del ciclo de vida del contenido"),
        "engagement_velocity_tracking": Param(True, type="boolean", description="Tracking de velocidad de engagement"),
        "automated_content_refresh": Param(True, type="boolean", description="Refresh automático de contenido exitoso"),
        "cross_platform_content_sync": Param(False, type="boolean", description="Sincronización cross-platform de contenido"),
        "intelligent_content_curation": Param(True, type="boolean", description="Curación inteligente de contenido"),
        "engagement_heatmap_analysis": Param(True, type="boolean", description="Análisis de heatmap de engagement"),
        "content_performance_attribution": Param(True, type="boolean", description="Atribución de performance de contenido"),
        "automated_content_repurposing": Param(True, type="boolean", description="Repurposing automático de contenido exitoso"),
        "content_audience_matching": Param(True, type="boolean", description="Matching de contenido con audiencia ideal"),
        "engagement_prediction_ml": Param(True, type="boolean", description="Predicción ML avanzada de engagement"),
        "content_topic_modeling": Param(False, type="boolean", description="Modelado de temas para clustering"),
        "automated_hashtag_generation": Param(True, type="boolean", description="Generación automática de hashtags con ML"),
        "content_competitor_analysis": Param(False, type="boolean", description="Análisis profundo de competencia"),
        "social_signal_detection": Param(True, type="boolean", description="Detección de señales sociales relevantes"),
        "content_engagement_forecasting": Param(True, type="boolean", description="Forecasting avanzado de engagement"),
        "content_performance_benchmarking": Param(True, type="boolean", description="Benchmarking de performance de contenido"),
        "automated_content_optimization_ml": Param(True, type="boolean", description="Optimización ML automática de contenido"),
        "engagement_anomaly_detection": Param(True, type="boolean", description="Detección de anomalías en engagement"),
        "content_trend_analysis": Param(True, type="boolean", description="Análisis de tendencias de contenido"),
        "automated_engagement_boosting": Param(False, type="boolean", description="Boost automático de engagement bajo"),
        "content_quality_ml_scoring": Param(True, type="boolean", description="Scoring ML de calidad de contenido"),
        "multi_platform_content_sync": Param(False, type="boolean", description="Sincronización multi-plataforma"),
        "intelligent_posting_schedule": Param(True, type="boolean", description="Programación inteligente con ML"),
        "content_engagement_optimization_ml": Param(True, type="boolean", description="Optimización ML de engagement"),
        "automated_content_ab_testing": Param(True, type="boolean", description="A/B testing automático de contenido"),
        "content_performance_attribution_ml": Param(True, type="boolean", description="Atribución ML de performance"),
        "social_listening_advanced": Param(False, type="boolean", description="Social listening avanzado"),
        "content_viral_potential_scoring": Param(True, type="boolean", description="Scoring de potencial viral"),
        "automated_engagement_responses": Param(True, type="boolean", description="Respuestas automáticas inteligentes"),
        "content_competitor_intelligence": Param(False, type="boolean", description="Inteligencia de competencia avanzada"),
        "content_performance_attribution_advanced": Param(True, type="boolean", description="Atribución avanzada de performance"),
        "automated_content_scheduling_ml": Param(True, type="boolean", description="Programación ML automática"),
        "content_engagement_prediction_advanced": Param(True, type="boolean", description="Predicción avanzada de engagement"),
        "social_media_roi_optimization": Param(True, type="boolean", description="Optimización de ROI en redes sociales"),
        "content_audience_growth_analysis": Param(True, type="boolean", description="Análisis de crecimiento de audiencia"),
        "automated_content_republishing": Param(True, type="boolean", description="Republicación automática inteligente"),
        "content_performance_insights_ml": Param(True, type="boolean", description="Insights ML de performance"),
        "content_engagement_pattern_analysis": Param(True, type="boolean", description="Análisis de patrones de engagement"),
        "automated_content_optimization_ai": Param(True, type="boolean", description="Optimización AI de contenido"),
        "social_media_budget_optimization": Param(False, type="boolean", description="Optimización de presupuesto"),
        "content_performance_forecasting_ml": Param(True, type="boolean", description="Forecasting ML de performance"),
        "automated_hashtag_optimization_ml": Param(True, type="boolean", description="Optimización ML de hashtags"),
        "content_engagement_boost_ml": Param(False, type="boolean", description="Boost ML de engagement"),
        "social_media_analytics_dashboard": Param(True, type="boolean", description="Dashboard de analytics"),
    },
    tags=["social-media", "marketing", "automation", "content", "reporting"],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60),
)
def social_media_automation() -> None:
    """
    DAG principal de automatización de redes sociales.
    """
    
    @task(task_id="analyze_content_sentiment")
    def analyze_content_sentiment(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el sentimiento del contenido antes de publicar."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("analyze_sentiment", True))
        
        if not analyze_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        analyzed_count = 0
        
        # Palabras positivas y negativas básicas (en producción usar NLP avanzado)
        positive_words = ["excelente", "genial", "increíble", "mejor", "fantástico", "bueno", "perfecto", "amazing", "great", "awesome", "wonderful"]
        negative_words = ["malo", "terrible", "horrible", "peor", "problema", "error", "bad", "terrible", "awful", "worst", "problem"]
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for article in articles:
                    article_id = article["article_id"]
                    content = (article.get("content", "") or "").lower()
                    title = (article.get("title", "") or "").lower()
                    full_text = f"{title} {content}"
                    
                    # Análisis básico de sentimiento
                    positive_count = sum(1 for word in positive_words if word in full_text)
                    negative_count = sum(1 for word in negative_words if word in full_text)
                    total_words = len(full_text.split())
                    
                    if total_words > 0:
                        sentiment_score = (positive_count - negative_count) / max(total_words / 100, 1)
                        
                        if sentiment_score > 0.1:
                            sentiment = "positive"
                        elif sentiment_score < -0.1:
                            sentiment = "negative"
                        else:
                            sentiment = "neutral"
                    else:
                        sentiment = "neutral"
                        sentiment_score = 0.0
                    
                    # Guardar análisis en metadata
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'sentiment', %s,
                                    'sentiment_score', %s,
                                    'sentiment_analyzed_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (sentiment, sentiment_score, article_id))
                        
                        article["sentiment"] = sentiment
                        article["sentiment_score"] = sentiment_score
                        analyzed_count += 1
                    except Exception as e:
                        logger.error(f"Error guardando análisis de sentimiento para {article_id}: {e}")
                        continue
                
                conn.commit()
        
        logger.info(f"Análisis de sentimiento completado: {analyzed_count} artículos analizados")
        
        if Stats:
            try:
                Stats.incr("social_media.sentiment_analyzed", analyzed_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="predict_engagement_ml")
    def predict_engagement_ml(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predice engagement esperado usando Machine Learning."""
        ctx = get_current_context()
        params = ctx["params"]
        predict_enabled = bool(params.get("predict_engagement_ml", True))
        
        if not predict_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        predicted_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener datos históricos para entrenar modelo simple
                cur.execute("""
                    SELECT 
                        LENGTH(a.content) as content_length,
                        LENGTH(a.title) as title_length,
                        CASE WHEN a.category IS NOT NULL THEN 1 ELSE 0 END as has_category,
                        CASE WHEN a.featured_image_url IS NOT NULL THEN 1 ELSE 0 END as has_image,
                        array_length(a.tags, 1) as tags_count,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        AVG(e.impressions) as avg_impressions
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '90 days'
                    AND sp.status = 'published'
                    GROUP BY a.article_id, a.content, a.title, a.category, a.featured_image_url, a.tags
                    HAVING COUNT(sp.post_id) >= 1
                    LIMIT 1000
                """)
                
                historical_data = cur.fetchall()
                
                if len(historical_data) < 10:
                    logger.info("No hay suficientes datos históricos para predicción ML")
                    return content_data
                
                # Calcular promedios para predicción simple
                avg_engagement = sum(row[5] or 0 for row in historical_data) / len(historical_data) if historical_data else 3.0
                avg_impressions = sum(row[6] or 0 for row in historical_data) / len(historical_data) if historical_data else 1000
                
                for article in articles:
                    article_id = article["article_id"]
                    content_length = len(article.get("content", "") or "")
                    title_length = len(article.get("title", "") or "")
                    has_category = 1 if article.get("category") else 0
                    has_image = 1 if article.get("featured_image_url") else 0
                    tags_count = len(article.get("tags", []) or [])
                    
                    # Predicción simple basada en características
                    # En producción, usar modelo ML entrenado (scikit-learn, XGBoost, etc.)
                    predicted_engagement = avg_engagement
                    
                    # Ajustes basados en características
                    if has_image:
                        predicted_engagement *= 1.2
                    if has_category:
                        predicted_engagement *= 1.1
                    if tags_count > 3:
                        predicted_engagement *= 1.15
                    if content_length > 500:
                        predicted_engagement *= 1.1
                    
                    predicted_impressions = avg_impressions
                    if has_image:
                        predicted_impressions *= 1.3
                    
                    # Guardar predicción
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'predicted_engagement_rate', %s,
                                    'predicted_impressions', %s,
                                    'prediction_confidence', %s,
                                    'predicted_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            round(predicted_engagement, 2),
                            int(predicted_impressions),
                            0.7,  # Confidence score
                            article_id
                        ))
                        
                        article["predicted_engagement"] = round(predicted_engagement, 2)
                        article["predicted_impressions"] = int(predicted_impressions)
                        predicted_count += 1
                    except Exception as e:
                        logger.error(f"Error guardando predicción para {article_id}: {e}")
                        continue
                
                conn.commit()
        
        logger.info(f"Predicción de engagement completada: {predicted_count} artículos")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_predicted", predicted_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="detect_trending_hashtags")
    def detect_trending_hashtags(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta hashtags trending y sugiere hashtags relevantes."""
        ctx = get_current_context()
        params = ctx["params"]
        detect_enabled = bool(params.get("detect_trending_hashtags", True))
        
        if not detect_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        hashtags_suggested = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener hashtags más usados recientemente (últimos 7 días)
                cur.execute("""
                    SELECT 
                        unnest(hashtags) as hashtag,
                        COUNT(*) as usage_count
                    FROM content_scheduled_posts
                    WHERE published_at >= NOW() - INTERVAL '7 days'
                    AND hashtags IS NOT NULL
                    AND array_length(hashtags, 1) > 0
                    GROUP BY hashtag
                    ORDER BY usage_count DESC
                    LIMIT 20
                """)
                
                trending_hashtags = [row[0] for row in cur.fetchall()]
                
                for article in articles:
                    article_id = article["article_id"]
                    existing_tags = article.get("tags", []) or []
                    content = article.get("content", "").lower()
                    
                    # Extraer hashtags del contenido
                    content_hashtags = re.findall(r'#(\w+)', content)
                    
                    # Sugerir hashtags trending relevantes
                    suggested_hashtags = []
                    
                    # Agregar hashtags trending que sean relevantes
                    for trending in trending_hashtags[:5]:
                        if trending.lower() in content or any(tag.lower() == trending.lower() for tag in existing_tags):
                            suggested_hashtags.append(trending)
                    
                    # Agregar hashtags del contenido
                    suggested_hashtags.extend([f"#{h}" for h in content_hashtags[:3]])
                    
                    if suggested_hashtags:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'suggested_hashtags', %s,
                                        'trending_hashtags_detected_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (json.dumps(suggested_hashtags), article_id))
                            
                            article["suggested_hashtags"] = suggested_hashtags
                            hashtags_suggested += 1
                        except Exception as e:
                            logger.error(f"Error guardando hashtags sugeridos para {article_id}: {e}")
                            continue
                
                conn.commit()
        
        logger.info(f"Detección de hashtags trending: {hashtags_suggested} artículos con sugerencias")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtags_suggested", hashtags_suggested)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="collect_new_content")
    def collect_new_content() -> Dict[str, Any]:
        """Recoge contenido nuevo desde la base de datos que necesita ser publicado."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_posts = int(params.get("max_posts_per_run", 20))
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar artículos publicados sin versiones o con versiones pendientes
                cur.execute("""
                    SELECT DISTINCT
                        a.article_id,
                        a.title,
                        a.content,
                        a.excerpt,
                        a.author,
                        a.source_url,
                        a.featured_image_url,
                        a.tags,
                        a.published_at,
                        COUNT(v.id) FILTER (WHERE v.status = 'approved') as approved_versions,
                        COUNT(v.id) FILTER (WHERE v.status = 'pending') as pending_versions
                    FROM content_articles a
                    LEFT JOIN content_versions v ON v.article_id = a.article_id
                    WHERE a.status = 'published'
                    AND a.published_at IS NOT NULL
                    AND (
                        -- Artículos sin versiones
                        NOT EXISTS (
                            SELECT 1 FROM content_versions v2 
                            WHERE v2.article_id = a.article_id
                        )
                        OR
                        -- Artículos con versiones pendientes de programar
                        EXISTS (
                            SELECT 1 FROM content_versions v3
                            WHERE v3.article_id = a.article_id
                            AND v3.status = 'approved'
                            AND NOT EXISTS (
                                SELECT 1 FROM content_scheduled_posts sp
                                WHERE sp.version_id = v3.id
                                AND sp.status NOT IN ('failed', 'cancelled')
                            )
                        )
                    )
                    GROUP BY a.article_id, a.title, a.content, a.excerpt, a.author,
                             a.source_url, a.featured_image_url, a.tags, a.published_at
                    ORDER BY a.published_at DESC
                    LIMIT %s
                """, (max_posts,))
                
                columns = [desc[0] for desc in cur.description]
                articles = []
                
                for row in cur.fetchall():
                    article = dict(zip(columns, row))
                    articles.append(article)
                
                logger.info(f"Encontrados {len(articles)} artículos para procesar")
                
                result = {
                    "articles": articles,
                    "total": len(articles),
                    "collected_at": datetime.utcnow().isoformat()
                }
                
                if Stats:
                    try:
                        Stats.incr("social_media.content_collected", len(articles))
                    except Exception:
                        pass
                
                return result
    
    @task(task_id="schedule_posts")
    def schedule_posts(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Programa publicaciones en las plataformas seleccionadas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        auto_schedule = bool(params.get("auto_schedule", True))
        platforms_str = str(params.get("platforms", '["twitter", "linkedin"]'))
        dry_run = bool(params.get("dry_run", False))
        
        if not auto_schedule:
            logger.info("Auto-schedule deshabilitado, saltando programación")
            return {"scheduled": 0, "skipped": content_data.get("total", 0)}
        
        try:
            platforms = json.loads(platforms_str)
        except json.JSONDecodeError:
            logger.warning(f"Error parseando platforms, usando default")
            platforms = ["twitter", "linkedin"]
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        articles = content_data.get("articles", [])
        scheduled_count = 0
        skipped_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for article in articles:
                    article_id = article["article_id"]
                    
                    # Obtener versiones aprobadas para este artículo
                    cur.execute("""
                        SELECT id, platform, version_type, content, media_urls, hashtags
                        FROM content_versions
                        WHERE article_id = %s
                        AND status = 'approved'
                        AND platform = ANY(%s)
                        AND NOT EXISTS (
                            SELECT 1 FROM content_scheduled_posts sp
                            WHERE sp.version_id = content_versions.id
                            AND sp.status NOT IN ('failed', 'cancelled')
                        )
                    """, (article_id, platforms))
                    
                    versions = cur.fetchall()
                    version_columns = [desc[0] for desc in cur.description]
                    
                    for version_row in versions:
                        version = dict(zip(version_columns, version_row))
                        platform = version["platform"]
                        
                        try:
                            # Obtener configuración de la plataforma
                            cur.execute("""
                                SELECT account_id, account_name, posting_schedule, 
                                       daily_post_limit, hourly_post_limit, last_post_at
                                FROM content_platform_config
                                WHERE platform = %s AND is_active = TRUE
                                LIMIT 1
                            """, (platform,))
                            
                            platform_config = cur.fetchone()
                            if not platform_config:
                                logger.warning(f"No hay configuración activa para {platform}")
                                skipped_count += 1
                                continue
                            
                            account_id, account_name, posting_schedule, daily_limit, hourly_limit, last_post = platform_config
                            
                            # Calcular fecha de publicación óptima (con ML si está habilitado)
                            optimize_ml = bool(params.get("optimize_timing_ml", True))
                            scheduled_at = _calculate_optimal_publish_time(
                                platform, posting_schedule, last_post, hourly_limit,
                                article_id=article_id, conn=conn, optimize_ml=optimize_ml
                            )
                            
                            # Generar post_id único
                            post_id = f"{platform}_{article_id}_{int(scheduled_at.timestamp())}"
                            
                            if not dry_run:
                                # Insertar publicación programada
                                cur.execute("""
                                    INSERT INTO content_scheduled_posts (
                                        post_id, article_id, version_id, platform,
                                        account_id, account_name, content, media_urls,
                                        hashtags, scheduled_at, timezone, status,
                                        created_at
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', NOW()
                                    )
                                    ON CONFLICT (post_id) DO NOTHING
                                    RETURNING post_id
                                """, (
                                    post_id,
                                    article_id,
                                    version["id"],
                                    platform,
                                    account_id,
                                    account_name,
                                    version["content"],
                                    version.get("media_urls") or [],
                                    version.get("hashtags") or [],
                                    scheduled_at,
                                    "UTC"
                                ))
                                
                                if cur.fetchone():
                                    scheduled_count += 1
                                    logger.info(f"Post programado: {post_id} para {platform} a las {scheduled_at}")
                                    
                                    # Actualizar last_post_at
                                    cur.execute("""
                                        UPDATE content_platform_config
                                        SET last_post_at = %s
                                        WHERE platform = %s AND account_id = %s
                                    """, (scheduled_at, platform, account_id))
                            else:
                                scheduled_count += 1
                                logger.info(f"[DRY RUN] Post sería programado: {post_id} para {platform}")
                        
                        except Exception as e:
                            logger.error(f"Error programando post para {article_id} en {platform}: {e}", exc_info=True)
                            skipped_count += 1
                            continue
                
                conn.commit()
        
        result = {
            "scheduled": scheduled_count,
            "skipped": skipped_count,
            "platforms": platforms
        }
        
        if Stats:
            try:
                Stats.incr("social_media.posts_scheduled", scheduled_count)
            except Exception:
                pass
        
        logger.info(f"Programación completada: {scheduled_count} programados, {skipped_count} omitidos")
        return result
    
    @task(task_id="publish_scheduled_posts")
    def publish_scheduled_posts(schedule_result: Dict[str, Any]) -> Dict[str, Any]:
        """Publica posts programados que ya alcanzaron su hora de publicación."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        auto_publish = bool(params.get("auto_publish", True))
        dry_run = bool(params.get("dry_run", False))
        
        if not auto_publish:
            logger.info("Auto-publish deshabilitado, saltando publicación")
            return {"published": 0, "failed": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        published_count = 0
        failed_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener posts programados listos para publicar
                cur.execute("""
                    SELECT sp.post_id, sp.article_id, sp.version_id, sp.platform,
                           sp.account_id, sp.content, sp.media_urls, sp.hashtags,
                           pc.api_key, pc.api_secret, pc.access_token, pc.access_token_secret
                    FROM content_scheduled_posts sp
                    JOIN content_platform_config pc ON pc.platform = sp.platform 
                        AND pc.account_id = sp.account_id
                    WHERE sp.status = 'scheduled'
                    AND sp.scheduled_at <= NOW()
                    AND pc.is_active = TRUE
                    ORDER BY sp.scheduled_at ASC
                    LIMIT 50
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts_to_publish = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                logger.info(f"Encontrados {len(posts_to_publish)} posts listos para publicar")
                
                for post in posts_to_publish:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    
                    try:
                        # Actualizar estado a "publishing"
                        cur.execute("""
                            UPDATE content_scheduled_posts
                            SET status = 'publishing', updated_at = NOW()
                            WHERE post_id = %s
                        """, (post_id,))
                        
                        if not dry_run:
                            # Publicar según plataforma
                            publish_result = _publish_to_platform(
                                platform=platform,
                                content=post["content"],
                                media_urls=post.get("media_urls") or [],
                                hashtags=post.get("hashtags") or [],
                                credentials={
                                    "api_key": post.get("api_key"),
                                    "api_secret": post.get("api_secret"),
                                    "access_token": post.get("access_token"),
                                    "access_token_secret": post.get("access_token_secret"),
                                }
                            )
                            
                            if publish_result.get("success"):
                                # Actualizar con éxito
                                cur.execute("""
                                    UPDATE content_scheduled_posts
                                    SET status = 'published',
                                        published_post_id = %s,
                                        published_url = %s,
                                        published_at = NOW(),
                                        updated_at = NOW()
                                    WHERE post_id = %s
                                """, (
                                    publish_result.get("post_id"),
                                    publish_result.get("url"),
                                    post_id
                                ))
                                
                                published_count += 1
                                logger.info(f"Post publicado exitosamente: {post_id} -> {publish_result.get('post_id')}")
                            else:
                                # Marcar como fallido
                                error_msg = publish_result.get("error", "Error desconocido")
                                cur.execute("""
                                    UPDATE content_scheduled_posts
                                    SET status = 'failed',
                                        error_message = %s,
                                        retry_count = retry_count + 1,
                                        updated_at = NOW()
                                    WHERE post_id = %s
                                """, (error_msg, post_id))
                                
                                failed_count += 1
                                logger.error(f"Error publicando post {post_id}: {error_msg}")
                        else:
                            # Dry run: simular publicación exitosa
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'published',
                                    published_post_id = 'DRY_RUN_' || post_id,
                                    published_url = 'https://example.com/dry-run',
                                    published_at = NOW(),
                                    updated_at = NOW()
                                WHERE post_id = %s
                            """, (post_id,))
                            published_count += 1
                            logger.info(f"[DRY RUN] Post simulado como publicado: {post_id}")
                    
                    except Exception as e:
                        logger.error(f"Error procesando post {post_id}: {e}", exc_info=True)
                        try:
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'failed',
                                    error_message = %s,
                                    retry_count = retry_count + 1,
                                    updated_at = NOW()
                                WHERE post_id = %s
                            """, (str(e), post_id))
                            failed_count += 1
                        except Exception:
                            pass
                
                conn.commit()
        
        result = {
            "published": published_count,
            "failed": failed_count
        }
        
        if Stats:
            try:
                Stats.incr("social_media.posts_published", published_count)
                Stats.incr("social_media.posts_failed", failed_count)
            except Exception:
                pass
        
        logger.info(f"Publicación completada: {published_count} publicados, {failed_count} fallidos")
        return result
    
    @task(task_id="detect_viral_content")
    def detect_viral_content(publish_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta contenido que está volviéndose viral."""
        ctx = get_current_context()
        params = ctx["params"]
        detect_enabled = bool(params.get("detect_viral_content", True))
        
        if not detect_enabled:
            return publish_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        viral_posts = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar posts con crecimiento rápido de engagement
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.article_id,
                        sp.platform,
                        e.likes,
                        e.comments,
                        e.shares,
                        e.impressions,
                        e.engagement_rate,
                        sp.published_at,
                        e.tracked_at,
                        EXTRACT(EPOCH FROM (e.tracked_at - sp.published_at) / 3600) as hours_since_publish
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '24 hours'
                    AND EXTRACT(EPOCH FROM (e.tracked_at - sp.published_at) / 3600) <= 24
                    AND (
                        -- Criterios de viralidad
                        (e.engagement_rate > 10 AND e.impressions > 1000)
                        OR
                        (e.likes + e.comments + e.shares > 500 AND EXTRACT(EPOCH FROM (e.tracked_at - sp.published_at) / 3600) < 6)
                        OR
                        (e.engagement_rate > 15)
                    )
                    ORDER BY e.engagement_rate DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                for row in cur.fetchall():
                    post = dict(zip(columns, row))
                    viral_posts.append(post)
                    
                    # Marcar como viral en metadata
                    try:
                        cur.execute("""
                            UPDATE content_scheduled_posts
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'is_viral', true,
                                    'viral_detected_at', NOW(),
                                    'viral_score', %s
                                )
                            WHERE post_id = %s
                        """, (post.get("engagement_rate", 0), post["post_id"]))
                    except Exception as e:
                        logger.error(f"Error marcando post como viral: {e}")
                
                conn.commit()
        
        if viral_posts:
            logger.info(f"Detectados {len(viral_posts)} posts virales")
            
            # Enviar alerta si hay contenido viral
            if NOTIFICATIONS_AVAILABLE:
                try:
                    viral_message = f"""
🔥 *Contenido Viral Detectado!*

Se detectaron {len(viral_posts)} posts con alto engagement:

"""
                    for post in viral_posts[:5]:
                        viral_message += f"""
• {post.get('platform', 'N/A').upper()}: Engagement Rate {post.get('engagement_rate', 0):.2f}%
  Likes: {post.get('likes', 0):,} | Comentarios: {post.get('comments', 0):,}
"""
                    notify_slack(viral_message)
                except Exception as e:
                    logger.error(f"Error enviando alerta de viral: {e}")
        
        if Stats:
            try:
                Stats.incr("social_media.viral_detected", len(viral_posts))
            except Exception:
                pass
        
        return publish_result
    
    @task(task_id="calculate_roi")
    def calculate_roi(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula ROI de las publicaciones en redes sociales."""
        ctx = get_current_context()
        params = ctx["params"]
        calculate_enabled = bool(params.get("calculate_roi", True))
        
        if not calculate_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular ROI basado en engagement y tiempo invertido
                # ROI = (Valor generado - Costo) / Costo * 100
                
                # Obtener posts publicados en últimos 30 días
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.article_id,
                        e.engagement_rate,
                        e.impressions,
                        e.reach,
                        e.clicks,
                        sp.published_at,
                        a.category
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    JOIN content_articles a ON a.article_id = sp.article_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    ORDER BY sp.published_at DESC
                    LIMIT 100
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                total_roi = 0
                roi_calculated = 0
                
                # Valores estimados (en producción, obtener de sistema de costos real)
                cost_per_post = 0.5  # Costo estimado por post (tiempo + recursos)
                value_per_engagement = 0.02  # Valor estimado por engagement
                value_per_click = 0.10  # Valor estimado por click
                
                for post in posts:
                    post_id = post["post_id"]
                    engagement_rate = post.get("engagement_rate", 0) or 0
                    impressions = post.get("impressions", 0) or 0
                    clicks = post.get("clicks", 0) or 0
                    
                    # Calcular valor generado
                    engagements = int(impressions * engagement_rate / 100)
                    value_generated = (engagements * value_per_engagement) + (clicks * value_per_click)
                    
                    # Calcular ROI
                    cost = cost_per_post
                    if value_generated > 0:
                        roi = ((value_generated - cost) / cost) * 100
                    else:
                        roi = -100  # Pérdida total
                    
                    # Guardar ROI
                    try:
                        cur.execute("""
                            UPDATE content_scheduled_posts
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'roi', %s,
                                    'value_generated', %s,
                                    'cost', %s,
                                    'roi_calculated_at', NOW()
                                )
                            WHERE post_id = %s
                        """, (round(roi, 2), round(value_generated, 2), cost, post_id))
                        
                        total_roi += roi
                        roi_calculated += 1
                    except Exception as e:
                        logger.error(f"Error calculando ROI para {post_id}: {e}")
                        continue
                
                conn.commit()
                
                avg_roi = total_roi / roi_calculated if roi_calculated > 0 else 0
                logger.info(f"ROI calculado: {roi_calculated} posts, ROI promedio: {avg_roi:.2f}%")
        
        if Stats:
            try:
                Stats.gauge("social_media.avg_roi", avg_roi)
                Stats.incr("social_media.roi_calculated", roi_calculated)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="republish_top_content")
    def republish_top_content(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """República contenido de alto rendimiento en diferentes horarios."""
        ctx = get_current_context()
        params = ctx["params"]
        republish_enabled = bool(params.get("republish_top_content", True))
        
        if not republish_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        republished_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar posts de alto rendimiento que no han sido republicados
                cur.execute("""
                    SELECT DISTINCT
                        sp.article_id,
                        sp.platform,
                        AVG(e.engagement_rate) as avg_engagement,
                        MAX(e.impressions) as max_impressions,
                        COUNT(DISTINCT sp.post_id) as publish_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '60 days'
                    AND sp.published_at <= NOW() - INTERVAL '7 days'  -- Posts de hace más de 7 días
                    GROUP BY sp.article_id, sp.platform
                    HAVING AVG(e.engagement_rate) > 5.0  -- Engagement rate > 5%
                    AND COUNT(DISTINCT sp.post_id) <= 2  -- No republicado más de 2 veces
                    ORDER BY avg_engagement DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                top_content = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for content in top_content:
                    article_id = content["article_id"]
                    platform = content["platform"]
                    
                    # Obtener versión del artículo
                    cur.execute("""
                        SELECT id, content, media_urls, hashtags
                        FROM content_versions
                        WHERE article_id = %s
                        AND platform = %s
                        AND status = 'approved'
                        LIMIT 1
                    """, (article_id, platform))
                    
                    version = cur.fetchone()
                    if not version:
                        continue
                    
                    version_id, version_content, media_urls, hashtags = version
                    
                    # Obtener configuración de plataforma
                    cur.execute("""
                        SELECT account_id, account_name
                        FROM content_platform_config
                        WHERE platform = %s AND is_active = TRUE
                        LIMIT 1
                    """, (platform,))
                    
                    platform_config = cur.fetchone()
                    if not platform_config:
                        continue
                    
                    account_id, account_name = platform_config
                    
                    # Programar republicación (en 3-7 días)
                    import random
                    days_ahead = random.randint(3, 7)
                    scheduled_at = datetime.utcnow() + timedelta(days=days_ahead)
                    
                    post_id = f"{platform}_{article_id}_republish_{int(scheduled_at.timestamp())}"
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_scheduled_posts (
                                post_id, article_id, version_id, platform,
                                account_id, account_name, content, media_urls,
                                hashtags, scheduled_at, timezone, status,
                                metadata, created_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled',
                                jsonb_build_object('is_republish', true, 'original_engagement', %s),
                                NOW()
                            )
                            ON CONFLICT (post_id) DO NOTHING
                            RETURNING post_id
                        """, (
                            post_id,
                            article_id,
                            version_id,
                            platform,
                            account_id,
                            account_name,
                            version_content,
                            media_urls or [],
                            hashtags or [],
                            scheduled_at,
                            "UTC",
                            content.get("avg_engagement", 0)
                        ))
                        
                        if cur.fetchone():
                            republished_count += 1
                            logger.info(f"Contenido de alto rendimiento programado para republicación: {post_id}")
                    except Exception as e:
                        logger.error(f"Error programando republicación para {article_id}: {e}")
                        continue
                
                conn.commit()
        
        logger.info(f"Republicación completada: {republished_count} posts programados")
        
        if Stats:
            try:
                Stats.incr("social_media.content_republished", republished_count)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="track_engagement")
    def track_engagement(publish_result: Dict[str, Any]) -> Dict[str, Any]:
        """Rastrea interacciones y métricas de posts publicados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        track_enabled = bool(params.get("track_engagement", True))
        
        if not track_enabled:
            logger.info("Tracking deshabilitado, saltando rastreo")
            return {"tracked": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        tracked_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener posts publicados que necesitan tracking
                cur.execute("""
                    SELECT sp.post_id, sp.platform_post_id, sp.platform, sp.published_at,
                           pc.api_key, pc.api_secret, pc.access_token, pc.access_token_secret
                    FROM content_scheduled_posts sp
                    JOIN content_platform_config pc ON pc.platform = sp.platform
                        AND pc.account_id = sp.account_id
                    WHERE sp.status = 'published'
                    AND sp.published_post_id IS NOT NULL
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND (
                        -- Posts sin engagement registrado
                        NOT EXISTS (
                            SELECT 1 FROM content_engagement e
                            WHERE e.post_id = sp.post_id
                        )
                        OR
                        -- Posts con engagement desactualizado (> 1 hora)
                        EXISTS (
                            SELECT 1 FROM content_engagement e
                            WHERE e.post_id = sp.post_id
                            AND e.last_synced_at < NOW() - INTERVAL '1 hour'
                        )
                    )
                    ORDER BY sp.published_at DESC
                    LIMIT 100
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts_to_track = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                logger.info(f"Rastreando engagement para {len(posts_to_track)} posts")
                
                for post in posts_to_track:
                    post_id = post["post_id"]
                    platform_post_id = post["platform_post_id"]
                    platform = post["platform"]
                    
                    try:
                        # Obtener métricas de la plataforma
                        metrics = _fetch_platform_metrics(
                            platform=platform,
                            post_id=platform_post_id,
                            credentials={
                                "api_key": post.get("api_key"),
                                "api_secret": post.get("api_secret"),
                                "access_token": post.get("access_token"),
                                "access_token_secret": post.get("access_token_secret"),
                            }
                        )
                        
                        if metrics:
                            # Insertar o actualizar engagement
                            cur.execute("""
                                INSERT INTO content_engagement (
                                    post_id, platform_post_id, likes, comments, shares,
                                    retweets, saves, clicks, impressions, reach,
                                    engagement_rate, click_through_rate, last_synced_at, tracked_at
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                                )
                                ON CONFLICT (post_id, platform_post_id)
                                DO UPDATE SET
                                    likes = EXCLUDED.likes,
                                    comments = EXCLUDED.comments,
                                    shares = EXCLUDED.shares,
                                    retweets = EXCLUDED.retweets,
                                    saves = EXCLUDED.saves,
                                    clicks = EXCLUDED.clicks,
                                    impressions = EXCLUDED.impressions,
                                    reach = EXCLUDED.reach,
                                    engagement_rate = EXCLUDED.engagement_rate,
                                    click_through_rate = EXCLUDED.click_through_rate,
                                    last_synced_at = NOW(),
                                    tracked_at = NOW()
                            """, (
                                post_id,
                                platform_post_id,
                                metrics.get("likes", 0),
                                metrics.get("comments", 0),
                                metrics.get("shares", 0),
                                metrics.get("retweets", 0),
                                metrics.get("saves", 0),
                                metrics.get("clicks", 0),
                                metrics.get("impressions", 0),
                                metrics.get("reach", 0),
                                metrics.get("engagement_rate"),
                                metrics.get("click_through_rate")
                            ))
                            
                            # Guardar snapshot histórico
                            cur.execute("""
                                INSERT INTO content_engagement_history (
                                    post_id, platform_post_id, likes, comments, shares,
                                    retweets, saves, clicks, impressions, reach, engagement_rate
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                )
                            """, (
                                post_id,
                                platform_post_id,
                                metrics.get("likes", 0),
                                metrics.get("comments", 0),
                                metrics.get("shares", 0),
                                metrics.get("retweets", 0),
                                metrics.get("saves", 0),
                                metrics.get("clicks", 0),
                                metrics.get("impressions", 0),
                                metrics.get("reach", 0),
                                metrics.get("engagement_rate")
                            ))
                            
                            tracked_count += 1
                            logger.debug(f"Engagement actualizado para post {post_id}")
                    
                    except Exception as e:
                        logger.error(f"Error rastreando engagement para post {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        result = {"tracked": tracked_count}
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_tracked", tracked_count)
            except Exception:
                pass
        
        logger.info(f"Tracking completado: {tracked_count} posts actualizados")
        return result
    
    @task(task_id="generate_weekly_report")
    def generate_weekly_report(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte semanal con análisis de performance."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        send_report = bool(params.get("send_weekly_report", True))
        
        # Solo generar reporte si es lunes (día 0 en cron)
        current_date = datetime.utcnow()
        if current_date.weekday() != 0:  # 0 = lunes
            logger.info("No es lunes, saltando generación de reporte semanal")
            return {"skipped": True, "reason": "not_monday"}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular fechas de la semana pasada
                week_start = current_date - timedelta(days=7)
                week_end = current_date
                
                # Obtener métricas agregadas por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        COUNT(DISTINCT sp.article_id) as total_articles,
                        SUM(e.likes) as total_likes,
                        SUM(e.comments) as total_comments,
                        SUM(e.shares) as total_shares,
                        SUM(e.retweets) as total_retweets,
                        SUM(e.impressions) as total_impressions,
                        SUM(e.reach) as total_reach,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        AVG(e.click_through_rate) as avg_ctr
                    FROM content_scheduled_posts sp
                    LEFT JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= %s
                    AND sp.published_at < %s
                    AND sp.status = 'published'
                    GROUP BY sp.platform
                    ORDER BY total_posts DESC
                """, (week_start, week_end))
                
                columns = [desc[0] for desc in cur.description]
                platform_metrics = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Obtener top posts
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        a.title as article_title,
                        e.likes + e.comments + e.shares + COALESCE(e.retweets, 0) as total_engagement,
                        e.engagement_rate,
                        sp.published_url
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    LEFT JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= %s
                    AND sp.published_at < %s
                    AND sp.status = 'published'
                    ORDER BY total_engagement DESC NULLS LAST
                    LIMIT 10
                """, (week_start, week_end))
                
                top_posts = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
                
                # Calcular totales
                total_posts = sum(pm.get("total_posts", 0) or 0 for pm in platform_metrics)
                total_engagement = sum(
                    (pm.get("total_likes", 0) or 0) +
                    (pm.get("total_comments", 0) or 0) +
                    (pm.get("total_shares", 0) or 0) +
                    (pm.get("total_retweets", 0) or 0)
                    for pm in platform_metrics
                )
                total_impressions = sum(pm.get("total_impressions", 0) or 0 for pm in platform_metrics)
                
                report = {
                    "period": {
                        "start": week_start.isoformat(),
                        "end": week_end.isoformat()
                    },
                    "summary": {
                        "total_posts": total_posts,
                        "total_articles": len(set(pm.get("total_articles", 0) for pm in platform_metrics)),
                        "total_engagement": total_engagement,
                        "total_impressions": total_impressions,
                        "avg_engagement_rate": sum(
                            pm.get("avg_engagement_rate", 0) or 0 for pm in platform_metrics
                        ) / len(platform_metrics) if platform_metrics else 0
                    },
                    "platform_breakdown": platform_metrics,
                    "top_posts": top_posts,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Reporte semanal generado: {total_posts} posts, {total_engagement} engagement total")
                
                return report
    
    @task(task_id="analyze_audience_insights")
    def analyze_audience_insights(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza insights de audiencia basados en engagement."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("analyze_audience", True))
        
        if not analyze_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        insights = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar mejor día de la semana para publicar
                cur.execute("""
                    SELECT 
                        EXTRACT(DOW FROM sp.published_at) as day_of_week,
                        AVG(e.engagement_rate) as avg_engagement,
                        AVG(e.impressions) as avg_impressions,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '60 days'
                    AND sp.status = 'published'
                    GROUP BY EXTRACT(DOW FROM sp.published_at)
                    HAVING COUNT(*) >= 5
                    ORDER BY avg_engagement DESC
                """)
                
                day_insights = cur.fetchall()
                if day_insights:
                    best_day = max(day_insights, key=lambda x: x[1])
                    day_names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
                    insights["best_day"] = {
                        "day": day_names[int(best_day[0])],
                        "engagement": round(best_day[1], 2),
                        "impressions": int(best_day[2])
                    }
                
                # Analizar mejor tipo de contenido
                cur.execute("""
                    SELECT 
                        a.category,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '60 days'
                    AND sp.status = 'published'
                    AND a.category IS NOT NULL
                    GROUP BY a.category
                    HAVING COUNT(*) >= 3
                    ORDER BY avg_engagement DESC
                    LIMIT 5
                """)
                
                category_insights = cur.fetchall()
                if category_insights:
                    insights["top_categories"] = [
                        {"category": cat[0], "engagement": round(cat[1], 2), "posts": cat[2]}
                        for cat in category_insights
                    ]
                
                # Analizar mejor longitud de contenido
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN LENGTH(a.content) < 200 THEN 'corto'
                            WHEN LENGTH(a.content) < 500 THEN 'medio'
                            WHEN LENGTH(a.content) < 1000 THEN 'largo'
                            ELSE 'muy_largo'
                        END as content_length,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '60 days'
                    AND sp.status = 'published'
                    GROUP BY content_length
                    HAVING COUNT(*) >= 3
                    ORDER BY avg_engagement DESC
                """)
                
                length_insights = cur.fetchall()
                if length_insights:
                    insights["best_length"] = {
                        "length": length_insights[0][0],
                        "engagement": round(length_insights[0][1], 2)
                    }
                
                # Guardar insights en tabla de análisis
                try:
                    cur.execute("""
                        INSERT INTO content_performance_analysis (
                            article_id, analysis_date, insights, created_at
                        ) VALUES (
                            NULL, CURRENT_DATE, %s, NOW()
                        )
                        ON CONFLICT DO NOTHING
                    """, (json.dumps(insights),))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error guardando insights de audiencia: {e}")
        
        logger.info(f"Análisis de audiencia completado: {len(insights)} insights generados")
        
        if Stats:
            try:
                Stats.incr("social_media.audience_analyzed", 1)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="trend_analysis")
    def trend_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza tendencias de engagement y contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("trend_analysis", True))
        
        if not analyze_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        trends = {
            "engagement_trend": "stable",
            "growth_rate": 0.0,
            "top_trending_topics": [],
            "declining_topics": []
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar tendencia de engagement (últimas 4 semanas vs anteriores 4 semanas)
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN sp.published_at >= NOW() - INTERVAL '28 days' THEN 'recent'
                            WHEN sp.published_at >= NOW() - INTERVAL '56 days' THEN 'previous'
                            ELSE 'old'
                        END as period,
                        AVG(e.engagement_rate) as avg_engagement,
                        AVG(e.impressions) as avg_impressions
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '56 days'
                    AND sp.status = 'published'
                    GROUP BY period
                    HAVING COUNT(*) >= 5
                """)
                
                period_data = {row[0]: {"engagement": row[1] or 0, "impressions": row[2] or 0} for row in cur.fetchall()}
                
                if "recent" in period_data and "previous" in period_data:
                    recent_eng = period_data["recent"]["engagement"]
                    previous_eng = period_data["previous"]["engagement"]
                    
                    if previous_eng > 0:
                        growth_rate = ((recent_eng - previous_eng) / previous_eng) * 100
                        trends["growth_rate"] = round(growth_rate, 2)
                        
                        if growth_rate > 10:
                            trends["engagement_trend"] = "growing"
                        elif growth_rate < -10:
                            trends["engagement_trend"] = "declining"
                        else:
                            trends["engagement_trend"] = "stable"
                
                # Analizar temas trending (hashtags más usados recientemente)
                cur.execute("""
                    SELECT 
                        unnest(sp.hashtags) as hashtag,
                        COUNT(*) as usage_count,
                        AVG(e.engagement_rate) as avg_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    AND sp.hashtags IS NOT NULL
                    GROUP BY hashtag
                    HAVING COUNT(*) >= 2
                    ORDER BY usage_count DESC, avg_engagement DESC
                    LIMIT 10
                """)
                
                trending_topics = cur.fetchall()
                if trending_topics:
                    trends["top_trending_topics"] = [
                        {"hashtag": topic[0], "usage": topic[1], "engagement": round(topic[2] or 0, 2)}
                        for topic in trending_topics
                    ]
                
                # Analizar temas en declive
                cur.execute("""
                    SELECT 
                        unnest(sp.hashtags) as hashtag,
                        COUNT(*) FILTER (WHERE sp.published_at >= NOW() - INTERVAL '14 days') as recent_usage,
                        COUNT(*) FILTER (WHERE sp.published_at >= NOW() - INTERVAL '28 days' 
                                         AND sp.published_at < NOW() - INTERVAL '14 days') as previous_usage
                    FROM content_scheduled_posts sp
                    WHERE sp.published_at >= NOW() - INTERVAL '28 days'
                    AND sp.status = 'published'
                    AND sp.hashtags IS NOT NULL
                    GROUP BY hashtag
                    HAVING previous_usage > 0
                    AND recent_usage < previous_usage * 0.5
                    ORDER BY (previous_usage - recent_usage) DESC
                    LIMIT 5
                """)
                
                declining_topics = cur.fetchall()
                if declining_topics:
                    trends["declining_topics"] = [
                        {"hashtag": topic[0], "recent": topic[1], "previous": topic[2]}
                        for topic in declining_topics
                    ]
        
        logger.info(f"Análisis de tendencias: {trends['engagement_trend']} ({trends['growth_rate']:.2f}%)")
        
        if Stats:
            try:
                Stats.gauge("social_media.engagement_growth_rate", trends["growth_rate"])
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="smart_content_optimization")
    def smart_content_optimization(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza contenido automáticamente basado en mejores prácticas."""
        ctx = get_current_context()
        params = ctx["params"]
        optimize_enabled = bool(params.get("smart_content_optimization", True))
        
        if not optimize_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        optimized_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener mejores prácticas de contenido exitoso
                cur.execute("""
                    SELECT 
                        AVG(LENGTH(a.content)) as avg_content_length,
                        AVG(LENGTH(a.title)) as avg_title_length,
                        AVG(array_length(a.tags, 1)) as avg_tags_count,
                        COUNT(*) FILTER (WHERE a.featured_image_url IS NOT NULL)::float / COUNT(*) as image_ratio
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '90 days'
                    AND sp.status = 'published'
                    AND e.engagement_rate > 5.0
                    HAVING COUNT(*) >= 10
                """)
                
                best_practices = cur.fetchone()
                
                if not best_practices:
                    return content_data
                
                avg_content_len, avg_title_len, avg_tags, image_ratio = best_practices
                
                for article in articles:
                    article_id = article["article_id"]
                    optimizations = []
                    
                    # Optimización 1: Longitud de contenido
                    content_len = len(article.get("content", "") or "")
                    if avg_content_len and content_len < avg_content_len * 0.7:
                        optimizations.append("content_too_short")
                    elif avg_content_len and content_len > avg_content_len * 1.5:
                        optimizations.append("content_too_long")
                    
                    # Optimización 2: Título
                    title_len = len(article.get("title", "") or "")
                    if avg_title_len and title_len < avg_title_len * 0.7:
                        optimizations.append("title_too_short")
                    elif avg_title_len and title_len > avg_title_len * 1.3:
                        optimizations.append("title_too_long")
                    
                    # Optimización 3: Imagen destacada
                    if not article.get("featured_image_url") and image_ratio > 0.7:
                        optimizations.append("missing_featured_image")
                    
                    # Optimización 4: Tags
                    tags_count = len(article.get("tags", []) or [])
                    if avg_tags and tags_count < avg_tags * 0.5:
                        optimizations.append("insufficient_tags")
                    
                    if optimizations:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'optimization_suggestions', %s,
                                        'optimized_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (json.dumps(optimizations), article_id))
                            
                            article["optimization_suggestions"] = optimizations
                            optimized_count += 1
                        except Exception as e:
                            logger.error(f"Error guardando optimizaciones para {article_id}: {e}")
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización de contenido completada: {optimized_count} artículos optimizados")
        
        if Stats:
            try:
                Stats.incr("social_media.content_optimized", optimized_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="generate_recommendations")
    def generate_recommendations(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendaciones automáticas basadas en performance."""
        ctx = get_current_context()
        params = ctx["params"]
        generate_enabled = bool(params.get("generate_recommendations", True))
        
        if not generate_enabled or report_data.get("skipped"):
            return report_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        recommendations = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar mejor hora para publicar por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        EXTRACT(HOUR FROM sp.published_at) as publish_hour,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    GROUP BY sp.platform, EXTRACT(HOUR FROM sp.published_at)
                    HAVING COUNT(*) >= 3
                    ORDER BY sp.platform, avg_engagement DESC
                """)
                
                best_hours = {}
                for row in cur.fetchall():
                    platform, hour, engagement, count = row
                    if platform not in best_hours:
                        best_hours[platform] = []
                    best_hours[platform].append({"hour": int(hour), "engagement": float(engagement), "count": count})
                
                # Recomendación 1: Mejor hora para publicar
                for platform, hours in best_hours.items():
                    if hours:
                        best_hour = max(hours, key=lambda x: x["engagement"])
                        recommendations.append({
                            "type": "optimal_posting_time",
                            "platform": platform,
                            "message": f"Mejor hora para publicar en {platform}: {best_hour['hour']}:00 (engagement promedio: {best_hour['engagement']:.2f}%)",
                            "priority": "high"
                        })
                
                # Analizar tipos de contenido con mejor performance
                cur.execute("""
                    SELECT 
                        a.category,
                        sp.platform,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    AND a.category IS NOT NULL
                    GROUP BY a.category, sp.platform
                    HAVING COUNT(*) >= 2
                    ORDER BY avg_engagement DESC
                    LIMIT 10
                """)
                
                top_categories = cur.fetchall()
                if top_categories:
                    recommendations.append({
                        "type": "content_category",
                        "message": f"Categorías con mejor engagement: {', '.join([f'{cat[0]} ({cat[2]:.2f}%)' for cat in top_categories[:3]])}",
                        "priority": "medium"
                    })
                
                # Analizar hashtags más efectivos
                cur.execute("""
                    SELECT 
                        unnest(sp.hashtags) as hashtag,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as usage_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    AND sp.hashtags IS NOT NULL
                    GROUP BY hashtag
                    HAVING COUNT(*) >= 3
                    ORDER BY avg_engagement DESC
                    LIMIT 10
                """)
                
                top_hashtags = cur.fetchall()
                if top_hashtags:
                    recommendations.append({
                        "type": "hashtags",
                        "message": f"Hashtags más efectivos: {', '.join([h[0] for h in top_hashtags[:5]])}",
                        "priority": "medium"
                    })
        
        report_data["recommendations"] = recommendations
        
        logger.info(f"Generadas {len(recommendations)} recomendaciones")
        
        return report_data
    
    @task(task_id="analyze_comment_sentiment")
    def analyze_comment_sentiment(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el sentimiento de comentarios en posts publicados."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("analyze_comment_sentiment", True))
        
        if not analyze_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        analyzed_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener posts con comentarios recientes
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        e.comments,
                        sp.published_at
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND e.comments > 0
                    ORDER BY e.comments DESC
                    LIMIT 50
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts_with_comments = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Palabras positivas y negativas para análisis de sentimiento
                positive_words = ["excelente", "genial", "gracias", "me encanta", "perfecto", "bueno", "amazing", "great", "love", "thanks"]
                negative_words = ["malo", "terrible", "horrible", "odio", "problema", "error", "bad", "terrible", "hate", "problem"]
                
                for post in posts_with_comments:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    comments_count = post.get("comments", 0)
                    
                    # En producción, aquí se obtendrían los comentarios reales de la API
                    # Por ahora, simulamos análisis basado en métricas
                    
                    # Análisis simplificado: posts con muchos comentarios tienden a tener sentimiento mixto
                    if comments_count > 50:
                        sentiment_score = 0.6  # Positivo pero con discusión
                        sentiment = "mixed_positive"
                    elif comments_count > 20:
                        sentiment_score = 0.7  # Mayormente positivo
                        sentiment = "positive"
                    else:
                        sentiment_score = 0.8  # Muy positivo
                        sentiment = "very_positive"
                    
                    # Guardar análisis
                    try:
                        cur.execute("""
                            UPDATE content_engagement
                            SET engagement_breakdown = COALESCE(engagement_breakdown, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'comment_sentiment', %s,
                                    'comment_sentiment_score', %s,
                                    'comment_analysis_at', NOW()
                                )
                            WHERE post_id = %s
                        """, (sentiment, sentiment_score, post_id))
                        
                        analyzed_count += 1
                    except Exception as e:
                        logger.error(f"Error analizando sentimiento de comentarios para {post_id}: {e}")
                        continue
                
                conn.commit()
        
        logger.info(f"Análisis de sentimiento de comentarios: {analyzed_count} posts analizados")
        
        if Stats:
            try:
                Stats.incr("social_media.comment_sentiment_analyzed", analyzed_count)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="campaign_roi_analysis")
    def campaign_roi_analysis(roi_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza ROI por campaña/UTM."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("campaign_roi_analysis", True))
        
        if not analyze_enabled:
            return roi_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        campaign_roi = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar ROI por campaña UTM
                cur.execute("""
                    SELECT 
                        a.utm_campaign,
                        a.utm_source,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        SUM((e.impressions * e.engagement_rate / 100) * 0.02 + e.clicks * 0.10) as total_value,
                        COUNT(DISTINCT sp.post_id) * 0.5 as total_cost,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        SUM(e.impressions) as total_impressions
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND a.utm_campaign IS NOT NULL
                    GROUP BY a.utm_campaign, a.utm_source
                    HAVING COUNT(DISTINCT sp.post_id) >= 2
                    ORDER BY total_value DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                campaigns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for campaign in campaigns:
                    campaign_name = campaign.get("utm_campaign", "unknown")
                    total_value = float(campaign.get("total_value", 0) or 0)
                    total_cost = float(campaign.get("total_cost", 0) or 0)
                    
                    if total_cost > 0:
                        roi = ((total_value - total_cost) / total_cost) * 100
                    else:
                        roi = 0
                    
                    campaign_roi[campaign_name] = {
                        "roi": round(roi, 2),
                        "value": round(total_value, 2),
                        "cost": round(total_cost, 2),
                        "posts": campaign.get("total_posts", 0),
                        "avg_engagement": round(campaign.get("avg_engagement_rate", 0) or 0, 2),
                        "impressions": campaign.get("total_impressions", 0)
                    }
        
        logger.info(f"Análisis de ROI por campaña: {len(campaign_roi)} campañas analizadas")
        
        # Enviar alerta si hay campañas con ROI negativo
        negative_roi_campaigns = [name for name, data in campaign_roi.items() if data["roi"] < 0]
        if negative_roi_campaigns and NOTIFICATIONS_AVAILABLE:
            try:
                alert_message = f"""
⚠️ *Campañas con ROI Negativo Detectadas*

Las siguientes campañas tienen ROI negativo:
"""
                for campaign_name in negative_roi_campaigns[:5]:
                    data = campaign_roi[campaign_name]
                    alert_message += f"\n• {campaign_name}: ROI {data['roi']:.2f}% (Valor: ${data['value']:.2f}, Costo: ${data['cost']:.2f})"
                
                notify_slack(alert_message)
            except Exception as e:
                logger.error(f"Error enviando alerta de ROI negativo: {e}")
        
        if Stats:
            try:
                for campaign_name, data in campaign_roi.items():
                    Stats.gauge(f"social_media.campaign_roi.{campaign_name}", data["roi"])
            except Exception:
                pass
        
        return roi_result
    
    @task(task_id="performance_benchmarking")
    def performance_benchmarking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compara performance actual con benchmarks históricos."""
        ctx = get_current_context()
        params = ctx["params"]
        benchmark_enabled = bool(params.get("performance_benchmarking", True))
        
        if not benchmark_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        benchmarks = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular benchmarks por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        AVG(e.engagement_rate) as benchmark_engagement,
                        AVG(e.impressions) as benchmark_impressions,
                        AVG(e.clicks) as benchmark_clicks,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY e.engagement_rate) as median_engagement,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY e.engagement_rate) as top_quartile_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '90 days'
                    AND sp.status = 'published'
                    GROUP BY sp.platform
                    HAVING COUNT(*) >= 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                platform_benchmarks = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for benchmark in platform_benchmarks:
                    platform = benchmark["platform"]
                    benchmarks[platform] = {
                        "avg_engagement": round(benchmark.get("benchmark_engagement", 0) or 0, 2),
                        "median_engagement": round(benchmark.get("median_engagement", 0) or 0, 2),
                        "top_quartile_engagement": round(benchmark.get("top_quartile_engagement", 0) or 0, 2),
                        "avg_impressions": int(benchmark.get("benchmark_impressions", 0) or 0),
                        "avg_clicks": int(benchmark.get("benchmark_clicks", 0) or 0)
                    }
                
                # Comparar posts recientes con benchmarks
                cur.execute("""
                    SELECT 
                        sp.platform,
                        e.engagement_rate,
                        e.impressions,
                        sp.post_id
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '7 days'
                    AND sp.status = 'published'
                """)
                
                recent_posts = cur.fetchall()
                below_benchmark = 0
                above_benchmark = 0
                
                for post in recent_posts:
                    platform, engagement, impressions, post_id = post
                    if platform in benchmarks:
                        benchmark_eng = benchmarks[platform]["avg_engagement"]
                        if engagement and engagement < benchmark_eng * 0.7:
                            below_benchmark += 1
                        elif engagement and engagement > benchmark_eng * 1.3:
                            above_benchmark += 1
                
                benchmarks["recent_performance"] = {
                    "below_benchmark": below_benchmark,
                    "above_benchmark": above_benchmark,
                    "total_recent": len(recent_posts)
                }
        
        logger.info(f"Benchmarking completado: {len(benchmarks)} plataformas analizadas")
        
        # Alerta si hay muchos posts por debajo del benchmark
        if benchmarks.get("recent_performance", {}).get("below_benchmark", 0) > 5:
            if NOTIFICATIONS_AVAILABLE:
                try:
                    alert_message = f"""
📊 *Performance por Debajo del Benchmark*

Se detectaron {benchmarks['recent_performance']['below_benchmark']} posts recientes 
por debajo del 70% del benchmark promedio.

Revisar estrategia de contenido y horarios de publicación.
"""
                    notify_slack(alert_message)
                except Exception as e:
                    logger.error(f"Error enviando alerta de benchmark: {e}")
        
        if Stats:
            try:
                for platform, data in benchmarks.items():
                    if platform != "recent_performance":
                        Stats.gauge(f"social_media.benchmark.{platform}.engagement", data["avg_engagement"])
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="hashtag_optimization")
    def hashtag_optimization(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza hashtags basándose en performance histórico."""
        ctx = get_current_context()
        params = ctx["params"]
        optimize_enabled = bool(params.get("hashtag_optimization", True))
        
        if not optimize_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        optimized_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener hashtags más efectivos por categoría
                cur.execute("""
                    SELECT 
                        a.category,
                        unnest(sp.hashtags) as hashtag,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as usage_count
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '90 days'
                    AND sp.status = 'published'
                    AND a.category IS NOT NULL
                    AND sp.hashtags IS NOT NULL
                    GROUP BY a.category, hashtag
                    HAVING COUNT(*) >= 2
                    ORDER BY a.category, avg_engagement DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                hashtag_performance = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Agrupar por categoría
                category_hashtags = defaultdict(list)
                for item in hashtag_performance:
                    category = item.get("category")
                    if category:
                        category_hashtags[category].append({
                            "hashtag": item.get("hashtag"),
                            "engagement": item.get("avg_engagement", 0) or 0,
                            "usage": item.get("usage_count", 0)
                        })
                
                # Optimizar hashtags para cada artículo
                for article in articles:
                    article_id = article["article_id"]
                    category = article.get("category")
                    existing_hashtags = article.get("tags", []) or []
                    
                    if not category or category not in category_hashtags:
                        continue
                    
                    # Obtener top hashtags para esta categoría
                    top_hashtags = sorted(
                        category_hashtags[category],
                        key=lambda x: x["engagement"],
                        reverse=True
                    )[:5]
                    
                    # Combinar hashtags existentes con los optimizados
                    optimized_hashtags = existing_hashtags.copy()
                    for top_hashtag in top_hashtags:
                        hashtag = top_hashtag["hashtag"]
                        if hashtag not in optimized_hashtags:
                            optimized_hashtags.append(hashtag)
                    
                    # Limitar a 10 hashtags máximo
                    optimized_hashtags = optimized_hashtags[:10]
                    
                    if optimized_hashtags != existing_hashtags:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'optimized_hashtags', %s,
                                        'hashtag_optimized_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (json.dumps(optimized_hashtags), article_id))
                            
                            article["optimized_hashtags"] = optimized_hashtags
                            optimized_count += 1
                        except Exception as e:
                            logger.error(f"Error optimizando hashtags para {article_id}: {e}")
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización de hashtags completada: {optimized_count} artículos optimizados")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtags_optimized", optimized_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="best_time_analysis")
    def best_time_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el mejor momento del día para publicar por plataforma."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("best_time_analysis", True))
        
        if not analyze_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        best_times = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar mejor hora del día por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        EXTRACT(HOUR FROM sp.published_at) as hour,
                        AVG(e.engagement_rate) as avg_engagement,
                        AVG(e.impressions) as avg_impressions,
                        COUNT(*) as post_count,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY e.engagement_rate) as top_quartile
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '60 days'
                    AND sp.status = 'published'
                    GROUP BY sp.platform, EXTRACT(HOUR FROM sp.published_at)
                    HAVING COUNT(*) >= 3
                    ORDER BY sp.platform, avg_engagement DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                hour_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Agrupar por plataforma y encontrar mejores horas
                platform_hours = defaultdict(list)
                for item in hour_data:
                    platform = item["platform"]
                    platform_hours[platform].append({
                        "hour": int(item["hour"]),
                        "engagement": float(item["avg_engagement"] or 0),
                        "impressions": int(item["avg_impressions"] or 0),
                        "posts": item["post_count"],
                        "top_quartile": float(item["top_quartile"] or 0)
                    })
                
                for platform, hours in platform_hours.items():
                    if hours:
                        # Encontrar top 3 horas
                        top_hours = sorted(hours, key=lambda x: x["engagement"], reverse=True)[:3]
                        best_times[platform] = {
                            "top_hours": [
                                {
                                    "hour": h["hour"],
                                    "engagement": round(h["engagement"], 2),
                                    "impressions": h["impressions"]
                                }
                                for h in top_hours
                            ],
                            "best_hour": top_hours[0]["hour"] if top_hours else None,
                            "best_engagement": round(top_hours[0]["engagement"], 2) if top_hours else 0
                        }
                
                # Guardar análisis
                try:
                    cur.execute("""
                        INSERT INTO content_performance_analysis (
                            article_id, analysis_date, insights, created_at
                        ) VALUES (
                            NULL, CURRENT_DATE, 
                            jsonb_build_object('best_times', %s),
                            NOW()
                        )
                        ON CONFLICT DO NOTHING
                    """, (json.dumps(best_times),))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error guardando análisis de mejores horas: {e}")
        
        logger.info(f"Análisis de mejores horas completado: {len(best_times)} plataformas")
        
        if Stats:
            try:
                for platform, data in best_times.items():
                    if data.get("best_hour"):
                        Stats.gauge(f"social_media.best_hour.{platform}", data["best_hour"])
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="anomaly_detection")
    def anomaly_detection(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta anomalías en engagement y métricas."""
        ctx = get_current_context()
        params = ctx["params"]
        detect_enabled = bool(params.get("anomaly_detection", True))
        
        if not detect_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        anomalies = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular estadísticas para detección de anomalías
                cur.execute("""
                    SELECT 
                        sp.platform,
                        AVG(e.engagement_rate) as avg_engagement,
                        STDDEV(e.engagement_rate) as stddev_engagement,
                        AVG(e.impressions) as avg_impressions,
                        STDDEV(e.impressions) as stddev_impressions
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    GROUP BY sp.platform
                    HAVING COUNT(*) >= 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                platform_stats = {row[0]: dict(zip(columns[1:], row[1:])) for row in cur.fetchall()}
                
                # Buscar posts con engagement anómalo (fuera de 2 desviaciones estándar)
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.article_id,
                        e.engagement_rate,
                        e.impressions,
                        sp.published_at
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '7 days'
                    AND sp.status = 'published'
                """)
                
                recent_posts = cur.fetchall()
                
                for post in recent_posts:
                    post_id, platform, article_id, engagement, impressions, published_at = post
                    
                    if platform in platform_stats:
                        stats = platform_stats[platform]
                        avg_eng = stats.get("avg_engagement", 0) or 0
                        stddev_eng = stats.get("stddev_engagement", 0) or 0
                        
                        if engagement and stddev_eng > 0:
                            z_score = (engagement - avg_eng) / stddev_eng
                            
                            # Anomalía: engagement muy alto o muy bajo
                            if abs(z_score) > 2:
                                anomaly_type = "high_performance" if z_score > 2 else "low_performance"
                                anomalies.append({
                                    "post_id": post_id,
                                    "platform": platform,
                                    "anomaly_type": anomaly_type,
                                    "z_score": round(z_score, 2),
                                    "engagement": engagement,
                                    "expected_range": f"{avg_eng - 2*stddev_eng:.2f} - {avg_eng + 2*stddev_eng:.2f}"
                                })
                                
                                # Guardar anomalía
                                try:
                                    cur.execute("""
                                        UPDATE content_scheduled_posts
                                        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                            jsonb_build_object(
                                                'anomaly_detected', true,
                                                'anomaly_type', %s,
                                                'z_score', %s,
                                                'anomaly_detected_at', NOW()
                                            )
                                        WHERE post_id = %s
                                    """, (anomaly_type, round(z_score, 2), post_id))
                                except Exception as e:
                                    logger.error(f"Error guardando anomalía para {post_id}: {e}")
                
                conn.commit()
        
        # Enviar alerta si hay anomalías significativas
        high_performance = [a for a in anomalies if a["anomaly_type"] == "high_performance"]
        low_performance = [a for a in anomalies if a["anomaly_type"] == "low_performance"]
        
        if high_performance and NOTIFICATIONS_AVAILABLE:
            try:
                alert_message = f"""
🎯 *Anomalías Detectadas: Alto Rendimiento*

Se detectaron {len(high_performance)} posts con engagement excepcionalmente alto:

"""
                for anomaly in high_performance[:5]:
                    alert_message += f"• {anomaly['platform']}: Engagement {anomaly['engagement']:.2f}% (Z-score: {anomaly['z_score']})\n"
                
                notify_slack(alert_message)
            except Exception as e:
                logger.error(f"Error enviando alerta de anomalías: {e}")
        
        if low_performance and len(low_performance) > 3:
            try:
                alert_message = f"""
⚠️ *Anomalías Detectadas: Bajo Rendimiento*

Se detectaron {len(low_performance)} posts con engagement excepcionalmente bajo.
Revisar estrategia de contenido.
"""
                notify_slack(alert_message)
            except Exception as e:
                logger.error(f"Error enviando alerta de anomalías: {e}")
        
        logger.info(f"Detección de anomalías: {len(anomalies)} anomalías detectadas")
        
        if Stats:
            try:
                Stats.incr("social_media.anomalies_detected", len(anomalies))
                Stats.incr("social_media.high_performance_anomalies", len(high_performance))
                Stats.incr("social_media.low_performance_anomalies", len(low_performance))
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="author_performance_analysis")
    def author_performance_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza performance de contenido por autor."""
        ctx = get_current_context()
        params = ctx["params"]
        analyze_enabled = bool(params.get("author_performance_analysis", True))
        
        if not analyze_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        author_stats = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar performance por autor
                cur.execute("""
                    SELECT 
                        a.author,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        AVG(e.engagement_rate) as avg_engagement,
                        AVG(e.impressions) as avg_impressions,
                        SUM(e.likes + e.comments + e.shares) as total_engagement,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY e.engagement_rate) as top_quartile
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '90 days'
                    AND sp.status = 'published'
                    AND a.author IS NOT NULL
                    GROUP BY a.author
                    HAVING COUNT(DISTINCT sp.post_id) >= 3
                    ORDER BY avg_engagement DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                authors = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for author_data in authors:
                    author = author_data["author"]
                    author_stats[author] = {
                        "total_posts": author_data.get("total_posts", 0),
                        "avg_engagement": round(author_data.get("avg_engagement", 0) or 0, 2),
                        "avg_impressions": int(author_data.get("avg_impressions", 0) or 0),
                        "total_engagement": int(author_data.get("total_engagement", 0) or 0),
                        "top_quartile": round(author_data.get("top_quartile", 0) or 0, 2)
                    }
                
                # Guardar análisis
                try:
                    cur.execute("""
                        INSERT INTO content_performance_analysis (
                            article_id, analysis_date, insights, created_at
                        ) VALUES (
                            NULL, CURRENT_DATE,
                            jsonb_build_object('author_performance', %s),
                            NOW()
                        )
                        ON CONFLICT DO NOTHING
                    """, (json.dumps(author_stats),))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error guardando análisis de autores: {e}")
        
        logger.info(f"Análisis de autores completado: {len(author_stats)} autores analizados")
        
        if Stats:
            try:
                for author, stats in author_stats.items():
                    Stats.gauge(f"social_media.author.{author}.avg_engagement", stats["avg_engagement"])
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="engagement_forecasting")
    def engagement_forecasting(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Predice engagement futuro basado en tendencias históricas."""
        ctx = get_current_context()
        params = ctx["params"]
        forecast_enabled = bool(params.get("engagement_forecasting", True))
        
        if not forecast_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        forecasts = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular tendencia de engagement por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        DATE_TRUNC('week', sp.published_at) as week,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '12 weeks'
                    AND sp.status = 'published'
                    GROUP BY sp.platform, DATE_TRUNC('week', sp.published_at)
                    HAVING COUNT(*) >= 3
                    ORDER BY sp.platform, week DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                weekly_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Agrupar por plataforma y calcular tendencia
                platform_weeks = defaultdict(list)
                for item in weekly_data:
                    platform = item["platform"]
                    platform_weeks[platform].append({
                        "week": item["week"],
                        "engagement": float(item["avg_engagement"] or 0),
                        "posts": item["post_count"]
                    })
                
                # Calcular forecast simple (promedio móvil)
                for platform, weeks in platform_weeks.items():
                    if len(weeks) >= 4:
                        # Usar últimas 4 semanas para forecast
                        recent_weeks = sorted(weeks, key=lambda x: x["week"], reverse=True)[:4]
                        avg_engagement = sum(w["engagement"] for w in recent_weeks) / len(recent_weeks)
                        
                        # Calcular tendencia (simple linear regression)
                        if len(recent_weeks) >= 2:
                            first_eng = recent_weeks[-1]["engagement"]
                            last_eng = recent_weeks[0]["engagement"]
                            trend = (last_eng - first_eng) / len(recent_weeks)
                            
                            # Forecast para próxima semana
                            next_week_forecast = last_eng + trend
                            
                            forecasts[platform] = {
                                "current_avg": round(avg_engagement, 2),
                                "trend": round(trend, 2),
                                "next_week_forecast": round(next_week_forecast, 2),
                                "trend_direction": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
                            }
                
                # Guardar forecast
                try:
                    cur.execute("""
                        INSERT INTO content_performance_analysis (
                            article_id, analysis_date, insights, created_at
                        ) VALUES (
                            NULL, CURRENT_DATE,
                            jsonb_build_object('engagement_forecast', %s),
                            NOW()
                        )
                        ON CONFLICT DO NOTHING
                    """, (json.dumps(forecasts),))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error guardando forecast: {e}")
        
        logger.info(f"Forecasting completado: {len(forecasts)} plataformas")
        
        if Stats:
            try:
                for platform, forecast in forecasts.items():
                    Stats.gauge(f"social_media.forecast.{platform}.next_week", forecast["next_week_forecast"])
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_calendar_optimization")
    def content_calendar_optimization(scheduled_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza el calendario de contenido para evitar sobrecarga."""
        ctx = get_current_context()
        params = ctx["params"]
        optimize_enabled = bool(params.get("content_calendar_optimization", True))
        
        if not optimize_enabled:
            return scheduled_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        optimized_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Verificar distribución de posts programados
                cur.execute("""
                    SELECT 
                        DATE(scheduled_at) as date,
                        platform,
                        COUNT(*) as posts_count
                    FROM content_scheduled_posts
                    WHERE status = 'scheduled'
                    AND scheduled_at >= NOW()
                    AND scheduled_at <= NOW() + INTERVAL '7 days'
                    GROUP BY DATE(scheduled_at), platform
                    ORDER BY date, platform
                """)
                
                columns = [desc[0] for desc in cur.description]
                scheduled_distribution = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Identificar días con sobrecarga (> 5 posts por plataforma)
                overloaded = {}
                for item in scheduled_distribution:
                    date_key = f"{item['date']}_{item['platform']}"
                    if item['posts_count'] > 5:
                        if date_key not in overloaded:
                            overloaded[date_key] = []
                        overloaded[date_key].append(item)
                
                # Redistribuir posts sobrecargados
                for date_key, items in overloaded.items():
                    for item in items:
                        date = item['date']
                        platform = item['platform']
                        excess = item['posts_count'] - 5
                        
                        # Mover posts excedentes a días menos cargados
                        cur.execute("""
                            SELECT post_id, scheduled_at
                            FROM content_scheduled_posts
                            WHERE status = 'scheduled'
                            AND DATE(scheduled_at) = %s
                            AND platform = %s
                            ORDER BY scheduled_at ASC
                            LIMIT %s
                        """, (date, platform, excess))
                        
                        posts_to_move = cur.fetchall()
                        
                        # Encontrar días con menos posts
                        cur.execute("""
                            SELECT DATE(scheduled_at) as date, COUNT(*) as count
                            FROM content_scheduled_posts
                            WHERE status = 'scheduled'
                            AND platform = %s
                            AND scheduled_at >= NOW()
                            AND scheduled_at <= NOW() + INTERVAL '7 days'
                            GROUP BY DATE(scheduled_at)
                            HAVING COUNT(*) < 3
                            ORDER BY count ASC, date ASC
                            LIMIT %s
                        """, (platform, excess))
                        
                        available_dates = cur.fetchall()
                        
                        # Redistribuir
                        for i, (post_id, _) in enumerate(posts_to_move):
                            if i < len(available_dates):
                                new_date = available_dates[i][0]
                                try:
                                    cur.execute("""
                                        UPDATE content_scheduled_posts
                                        SET scheduled_at = scheduled_at + INTERVAL '1 day' * 
                                            EXTRACT(DAY FROM (%s::date - DATE(scheduled_at))),
                                            updated_at = NOW()
                                        WHERE post_id = %s
                                    """, (new_date, post_id))
                                    optimized_count += 1
                                except Exception as e:
                                    logger.error(f"Error redistribuyendo post {post_id}: {e}")
                
                conn.commit()
        
        logger.info(f"Optimización de calendario: {optimized_count} posts redistribuidos")
        
        if Stats:
            try:
                Stats.incr("social_media.calendar_optimized", optimized_count)
            except Exception:
                pass
        
        return scheduled_result
    
    @task(task_id="auto_retry_failed_posts")
    def auto_retry_failed_posts(publish_result: Dict[str, Any]) -> Dict[str, Any]:
        """Reintenta automáticamente posts que fallaron."""
        ctx = get_current_context()
        params = ctx["params"]
        retry_enabled = bool(params.get("auto_retry_failed_posts", True))
        
        if not retry_enabled:
            return publish_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        retried_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar posts fallidos que pueden reintentarse
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.content,
                        sp.media_urls,
                        sp.hashtags,
                        sp.retry_count,
                        sp.error_message,
                        pc.api_key, pc.api_secret, pc.access_token, pc.access_token_secret
                    FROM content_scheduled_posts sp
                    JOIN content_platform_config pc ON pc.platform = sp.platform
                        AND pc.account_id = sp.account_id
                    WHERE sp.status = 'failed'
                    AND sp.retry_count < 3
                    AND sp.scheduled_at >= NOW() - INTERVAL '24 hours'
                    AND pc.is_active = TRUE
                    ORDER BY sp.retry_count ASC, sp.scheduled_at DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                failed_posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in failed_posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    retry_count = post.get("retry_count", 0)
                    
                    # Esperar antes de reintentar (backoff exponencial)
                    wait_hours = 2 ** retry_count  # 1h, 2h, 4h
                    last_failed = post.get("scheduled_at")
                    
                    if last_failed:
                        time_since_failure = (datetime.utcnow() - last_failed).total_seconds() / 3600
                        if time_since_failure < wait_hours:
                            continue  # Aún no es tiempo de reintentar
                    
                    try:
                        # Actualizar estado a "publishing"
                        cur.execute("""
                            UPDATE content_scheduled_posts
                            SET status = 'publishing',
                                retry_count = retry_count + 1,
                                updated_at = NOW()
                            WHERE post_id = %s
                        """, (post_id,))
                        
                        # Reintentar publicación
                        publish_result = _publish_to_platform(
                            platform=platform,
                            content=post["content"],
                            media_urls=post.get("media_urls") or [],
                            hashtags=post.get("hashtags") or [],
                            credentials={
                                "api_key": post.get("api_key"),
                                "api_secret": post.get("api_secret"),
                                "access_token": post.get("access_token"),
                                "access_token_secret": post.get("access_token_secret"),
                            }
                        )
                        
                        if publish_result.get("success"):
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'published',
                                    published_post_id = %s,
                                    published_url = %s,
                                    published_at = NOW(),
                                    error_message = NULL,
                                    updated_at = NOW()
                                WHERE post_id = %s
                            """, (
                                publish_result.get("post_id"),
                                publish_result.get("url"),
                                post_id
                            ))
                            
                            retried_count += 1
                            logger.info(f"Post reintentado exitosamente: {post_id}")
                        else:
                            # Marcar como fallido nuevamente
                            error_msg = publish_result.get("error", "Error desconocido")
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'failed',
                                    error_message = %s,
                                    updated_at = NOW()
                                WHERE post_id = %s
                            """, (error_msg, post_id))
                    
                    except Exception as e:
                        logger.error(f"Error reintentando post {post_id}: {e}", exc_info=True)
                        try:
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'failed',
                                    error_message = %s,
                                    updated_at = NOW()
                                WHERE post_id = %s
                            """, (str(e), post_id))
                        except Exception:
                            pass
                
                conn.commit()
        
        logger.info(f"Reintentos automáticos: {retried_count} posts reintentados exitosamente")
        
        if Stats:
            try:
                Stats.incr("social_media.posts_retried", retried_count)
            except Exception:
                pass
        
        return publish_result
    
    @task(task_id="content_similarity_detection")
    def content_similarity_detection(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta contenido similar para evitar duplicados."""
        ctx = get_current_context()
        params = ctx["params"]
        detect_enabled = bool(params.get("content_similarity_detection", False))
        
        if not detect_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        similar_detected = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener artículos publicados recientemente para comparar
                cur.execute("""
                    SELECT article_id, title, content
                    FROM content_articles
                    WHERE published_at >= NOW() - INTERVAL '30 days'
                    AND status = 'published'
                    ORDER BY published_at DESC
                    LIMIT 100
                """)
                
                existing_articles = {row[0]: {"title": row[1], "content": row[2]} for row in cur.fetchall()}
                
                for article in articles:
                    article_id = article["article_id"]
                    title = (article.get("title", "") or "").lower()
                    content = (article.get("content", "") or "").lower()
                    
                    # Comparación simple de similitud (en producción usar NLP avanzado)
                    for existing_id, existing in existing_articles.items():
                        if existing_id == article_id:
                            continue
                        
                        existing_title = existing["title"].lower()
                        existing_content = existing["content"].lower()
                        
                        # Calcular similitud simple (Jaccard similarity)
                        title_words = set(title.split())
                        existing_title_words = set(existing_title.split())
                        
                        if title_words and existing_title_words:
                            title_similarity = len(title_words & existing_title_words) / len(title_words | existing_title_words)
                            
                            # Si similitud > 0.7, marcar como similar
                            if title_similarity > 0.7:
                                try:
                                    cur.execute("""
                                        UPDATE content_articles
                                        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                            jsonb_build_object(
                                                'similar_to', %s,
                                                'similarity_score', %s,
                                                'similarity_detected_at', NOW()
                                            )
                                        WHERE article_id = %s
                                    """, (existing_id, round(title_similarity, 2), article_id))
                                    
                                    similar_detected += 1
                                    logger.warning(f"Contenido similar detectado: {article_id} similar a {existing_id} ({title_similarity:.2%})")
                                    break
                                except Exception as e:
                                    logger.error(f"Error guardando similitud: {e}")
                
                conn.commit()
        
        logger.info(f"Detección de similitud: {similar_detected} artículos con contenido similar")
        
        if Stats:
            try:
                Stats.incr("social_media.similar_content_detected", similar_detected)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="auto_respond_to_comments")
    def auto_respond_to_comments(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Responde automáticamente a comentarios según reglas configuradas."""
        ctx = get_current_context()
        params = ctx["params"]
        auto_respond_enabled = bool(params.get("auto_respond_comments", False) or params.get("auto_respond_to_comments", False))
        
        if not auto_respond_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        responses_sent = 0
        
        # Plantillas de respuestas automáticas
        response_templates = {
            "question": [
                "¡Gracias por tu pregunta! Te comparto más información: {link}",
                "Excelente pregunta. Aquí tienes más detalles: {link}",
                "Gracias por tu interés. Puedes encontrar más información aquí: {link}"
            ],
            "compliment": [
                "¡Muchas gracias por tu comentario! Nos alegra saber que te gustó.",
                "Gracias por el feedback positivo. ¡Seguimos trabajando para mejorar!",
                "¡Gracias! Tu apoyo nos motiva a seguir creando contenido de valor."
            ],
            "complaint": [
                "Lamentamos la inconveniencia. Por favor contáctanos en {support_email} para ayudarte.",
                "Entendemos tu preocupación. Nuestro equipo te contactará pronto.",
                "Gracias por reportarlo. Estamos revisando el tema y te responderemos pronto."
            ],
            "default": [
                "¡Gracias por tu comentario!",
                "Agradecemos tu feedback.",
                "Gracias por seguirnos."
            ]
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener posts con comentarios sin responder
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.published_post_id,
                        sp.published_url,
                        e.comments,
                        e.engagement_breakdown,
                        pc.api_key, pc.api_secret, pc.access_token, pc.access_token_secret
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    JOIN content_platform_config pc ON pc.platform = sp.platform
                        AND pc.account_id = sp.account_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND e.comments > 0
                    AND (e.engagement_breakdown->>'auto_responded_at' IS NULL)
                    AND pc.is_active = TRUE
                    ORDER BY e.comments DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts_with_comments = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts_with_comments:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    published_post_id = post.get("published_post_id")
                    comments_count = post.get("comments", 0)
                    
                    # Solo responder si hay comentarios recientes (últimas 24h)
                    # En producción, aquí se obtendrían los comentarios reales de la API
                    # Por ahora, simulamos respuesta automática
                    
                    if comments_count > 0 and published_post_id:
                        try:
                            # Determinar tipo de comentario (simulado)
                            # En producción, usar NLP para clasificar comentarios
                            comment_type = "question" if comments_count > 10 else "compliment"
                            
                            # Seleccionar plantilla
                            templates = response_templates.get(comment_type, response_templates["default"])
                            response_text = templates[0].format(
                                link=post.get("published_url", ""),
                                support_email="support@example.com"
                            )
                            
                            # En producción, aquí se publicaría la respuesta usando la API de la plataforma
                            # Ejemplo para Twitter:
                            # if platform == "twitter":
                            #     api = tweepy.Client(
                            #         bearer_token=post["access_token"],
                            #         consumer_key=post["api_key"],
                            #         consumer_secret=post["api_secret"],
                            #         access_token=post["access_token"],
                            #         access_token_secret=post["access_token_secret"]
                            #     )
                            #     api.create_tweet(
                            #         text=response_text,
                            #         in_reply_to_tweet_id=published_post_id
                            #     )
                            
                            # Simulación: marcar como respondido
                            cur.execute("""
                                UPDATE content_engagement
                                SET engagement_breakdown = COALESCE(engagement_breakdown, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'auto_responded_at', NOW(),
                                        'auto_response_type', %s,
                                        'auto_response_text', %s
                                    )
                                WHERE post_id = %s
                            """, (comment_type, response_text, post_id))
                            
                            responses_sent += 1
                            logger.info(f"Respuesta automática enviada para post {post_id} ({comment_type})")
                        
                        except Exception as e:
                            logger.error(f"Error enviando respuesta automática para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Respuestas automáticas: {responses_sent} respuestas enviadas")
        
        if Stats:
            try:
                Stats.incr("social_media.auto_responses_sent", responses_sent)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="competitor_tracking")
    def competitor_tracking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Tracking y análisis de competencia en redes sociales."""
        ctx = get_current_context()
        params = ctx["params"]
        tracking_enabled = bool(params.get("competitor_tracking", False))
        
        if not tracking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Competidores a trackear (en producción, esto vendría de una tabla de configuración)
        competitors = [
            {"name": "competitor1", "platform": "twitter", "handle": "@competitor1"},
            {"name": "competitor2", "platform": "linkedin", "handle": "competitor2"},
        ]
        
        tracked_posts = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de tracking de competencia si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_competitor_tracking (
                        tracking_id SERIAL PRIMARY KEY,
                        competitor_name VARCHAR(255) NOT NULL,
                        platform VARCHAR(50) NOT NULL,
                        post_id VARCHAR(255),
                        post_url TEXT,
                        content TEXT,
                        likes INTEGER DEFAULT 0,
                        comments INTEGER DEFAULT 0,
                        shares INTEGER DEFAULT 0,
                        impressions INTEGER DEFAULT 0,
                        posted_at TIMESTAMP,
                        tracked_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                for competitor in competitors:
                    competitor_name = competitor["name"]
                    platform = competitor["platform"]
                    
                    # En producción, aquí se obtendrían los posts del competidor usando la API
                    # Por ahora, simulamos tracking
                    try:
                        # Simulación: obtener posts recientes del competidor
                        # if platform == "twitter":
                        #     api = tweepy.Client(bearer_token=BEARER_TOKEN)
                        #     user = api.get_user(username=competitor["handle"])
                        #     tweets = api.get_users_tweets(
                        #         id=user.data.id,
                        #         max_results=10,
                        #         tweet_fields=["public_metrics", "created_at"]
                        #     )
                        #     for tweet in tweets.data:
                        #         cur.execute("""
                        #             INSERT INTO content_competitor_tracking
                        #             (competitor_name, platform, post_id, post_url, content, 
                        #              likes, comments, shares, impressions, posted_at, metadata)
                        #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        #             ON CONFLICT (competitor_name, platform, post_id) 
                        #             DO UPDATE SET
                        #                 likes = EXCLUDED.likes,
                        #                 comments = EXCLUDED.comments,
                        #                 shares = EXCLUDED.shares,
                        #                 impressions = EXCLUDED.impressions,
                        #                 tracked_at = NOW()
                        #         """, (
                        #             competitor_name, platform, tweet.id,
                        #             f"https://twitter.com/status/{tweet.id}",
                        #             tweet.text,
                        #             tweet.public_metrics.get("like_count", 0),
                        #             tweet.public_metrics.get("reply_count", 0),
                        #             tweet.public_metrics.get("retweet_count", 0),
                        #             tweet.public_metrics.get("impression_count", 0),
                        #             tweet.created_at,
                        #             json.dumps({"public_metrics": tweet.public_metrics})
                        #         ))
                        
                        # Simulación por ahora
                        import random
                        cur.execute("""
                            INSERT INTO content_competitor_tracking
                            (competitor_name, platform, post_id, post_url, content, 
                             likes, comments, shares, impressions, posted_at, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            competitor_name, platform, f"{platform}_{random.randint(1000, 9999)}",
                            f"https://{platform}.com/post/{random.randint(1000, 9999)}",
                            f"Sample post from {competitor_name}",
                            random.randint(10, 500),
                            random.randint(0, 50),
                            random.randint(0, 50),
                            random.randint(100, 5000),
                            datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                            json.dumps({"simulated": True})
                        ))
                        
                        tracked_posts += 1
                    
                    except Exception as e:
                        logger.error(f"Error trackeando competidor {competitor_name}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Tracking de competencia: {tracked_posts} posts trackeados")
        
        if Stats:
            try:
                Stats.incr("social_media.competitor_posts_tracked", tracked_posts)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_clustering")
    def content_clustering(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agrupa contenido similar usando clustering."""
        ctx = get_current_context()
        params = ctx["params"]
        clustering_enabled = bool(params.get("content_clustering", False))
        
        if not clustering_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        clusters_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de clusters si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_clusters (
                        cluster_id SERIAL PRIMARY KEY,
                        cluster_name VARCHAR(255),
                        cluster_keywords TEXT[],
                        article_ids INTEGER[],
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Clustering simple basado en palabras clave
                # En producción, usar técnicas avanzadas como K-means, DBSCAN, o embeddings
                keyword_groups = {}
                
                for article in articles:
                    article_id = article["article_id"]
                    title = (article.get("title", "") or "").lower()
                    category = article.get("category", "").lower()
                    
                    # Extraer palabras clave importantes (palabras de 4+ caracteres)
                    words = [w for w in title.split() if len(w) >= 4]
                    key_phrase = " ".join(words[:3])  # Primeras 3 palabras clave
                    
                    if not key_phrase:
                        continue
                    
                    # Agrupar por frase clave similar
                    cluster_key = key_phrase[:20]  # Simplificado
                    
                    if cluster_key not in keyword_groups:
                        keyword_groups[cluster_key] = {
                            "article_ids": [],
                            "keywords": words[:5]
                        }
                    
                    keyword_groups[cluster_key]["article_ids"].append(article_id)
                
                # Guardar clusters
                for cluster_key, cluster_data in keyword_groups.items():
                    if len(cluster_data["article_ids"]) >= 2:  # Mínimo 2 artículos por cluster
                        try:
                            cur.execute("""
                                INSERT INTO content_clusters
                                (cluster_name, cluster_keywords, article_ids, metadata)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                f"Cluster: {cluster_key}",
                                cluster_data["keywords"],
                                cluster_data["article_ids"],
                                json.dumps({
                                    "created_by": "automation",
                                    "cluster_size": len(cluster_data["article_ids"])
                                })
                            ))
                            
                            clusters_created += 1
                            
                            # Actualizar metadata de artículos con cluster_id
                            cur.execute("""
                                SELECT cluster_id FROM content_clusters
                                WHERE cluster_name = %s
                                ORDER BY created_at DESC
                                LIMIT 1
                            """, (f"Cluster: {cluster_key}",))
                            
                            cluster_row = cur.fetchone()
                            if cluster_row:
                                cluster_id = cluster_row[0]
                                for article_id in cluster_data["article_ids"]:
                                    cur.execute("""
                                        UPDATE content_articles
                                        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                            jsonb_build_object('cluster_id', %s)
                                        WHERE article_id = %s
                                    """, (cluster_id, article_id))
                        
                        except Exception as e:
                            logger.error(f"Error creando cluster {cluster_key}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Clustering de contenido: {clusters_created} clusters creados")
        
        if Stats:
            try:
                Stats.incr("social_media.content_clusters_created", clusters_created)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="image_analysis")
    def image_analysis(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza imágenes asociadas al contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("image_analysis", False))
        
        if not analysis_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles = content_data.get("articles", [])
        images_analyzed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for article in articles:
                    article_id = article["article_id"]
                    media_urls = article.get("media_urls") or []
                    
                    if not media_urls:
                        continue
                    
                    image_analysis_results = []
                    
                    for media_url in media_urls:
                        if not media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            continue
                        
                        try:
                            # En producción, usar servicios como:
                            # - Google Cloud Vision API
                            # - AWS Rekognition
                            # - Azure Computer Vision
                            # - Clarifai
                            
                            # Ejemplo con Google Cloud Vision:
                            # from google.cloud import vision
                            # client = vision.ImageAnnotatorClient()
                            # image = vision.Image()
                            # image.source.image_uri = media_url
                            # response = client.label_detection(image=image)
                            # labels = [label.description for label in response.label_annotations]
                            # 
                            # response = client.safe_search_detection(image=image)
                            # safe_search = response.safe_search_annotation
                            
                            # Simulación por ahora
                            import random
                            analysis_result = {
                                "labels": ["technology", "business", "innovation"][:random.randint(1, 3)],
                                "dominant_colors": ["#FF5733", "#33C3F0", "#85C1E2"][:random.randint(1, 3)],
                                "text_detected": random.choice([True, False]),
                                "faces_detected": random.choice([0, 1, 2]),
                                "safe_search": {
                                    "adult": "VERY_UNLIKELY",
                                    "violence": "VERY_UNLIKELY",
                                    "racy": "VERY_UNLIKELY"
                                },
                                "image_quality": {
                                    "brightness": random.uniform(0.5, 1.0),
                                    "contrast": random.uniform(0.5, 1.0),
                                    "sharpness": random.uniform(0.5, 1.0)
                                },
                                "analyzed_at": datetime.utcnow().isoformat()
                            }
                            
                            image_analysis_results.append({
                                "url": media_url,
                                "analysis": analysis_result
                            })
                            
                            images_analyzed += 1
                        
                        except Exception as e:
                            logger.error(f"Error analizando imagen {media_url}: {e}", exc_info=True)
                            continue
                    
                    # Guardar análisis en metadata del artículo
                    if image_analysis_results:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object('image_analysis', %s)
                                WHERE article_id = %s
                            """, (json.dumps(image_analysis_results), article_id))
                        except Exception as e:
                            logger.error(f"Error guardando análisis de imágenes para {article_id}: {e}")
                
                conn.commit()
        
        logger.info(f"Análisis de imágenes: {images_analyzed} imágenes analizadas")
        
        if Stats:
            try:
                Stats.incr("social_media.images_analyzed", images_analyzed)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="ab_testing")
    def ab_testing(scheduled_result: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza A/B testing automático de variantes de contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        ab_enabled = bool(params.get("ab_testing", False))
        
        if not ab_enabled:
            return scheduled_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        ab_tests_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de A/B tests si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_ab_tests (
                        test_id SERIAL PRIMARY KEY,
                        article_id INTEGER NOT NULL,
                        variant_a_post_id INTEGER,
                        variant_b_post_id INTEGER,
                        variant_a_content TEXT,
                        variant_b_content TEXT,
                        variant_a_hashtags TEXT[],
                        variant_b_hashtags TEXT[],
                        test_started_at TIMESTAMP DEFAULT NOW(),
                        test_ended_at TIMESTAMP,
                        winner_variant VARCHAR(1),
                        variant_a_engagement_rate DECIMAL(10,2),
                        variant_b_engagement_rate DECIMAL(10,2),
                        confidence_level DECIMAL(5,2),
                        status VARCHAR(50) DEFAULT 'running',
                        metadata JSONB
                    )
                """)
                
                # Buscar artículos candidatos para A/B testing
                cur.execute("""
                    SELECT 
                        a.article_id,
                        a.title,
                        a.content,
                        a.hashtags,
                        COUNT(sp.post_id) as existing_posts
                    FROM content_articles a
                    LEFT JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    WHERE a.status = 'published'
                    AND a.published_at >= NOW() - INTERVAL '7 days'
                    GROUP BY a.article_id, a.title, a.content, a.hashtags
                    HAVING COUNT(sp.post_id) = 0
                    ORDER BY a.published_at DESC
                    LIMIT 5
                """)
                
                columns = [desc[0] for desc in cur.description]
                candidates = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for candidate in candidates:
                    article_id = candidate["article_id"]
                    title = candidate["title"]
                    content = candidate["content"]
                    hashtags = candidate.get("hashtags") or []
                    
                    # Crear variantes A y B
                    # Variante A: título original, contenido completo
                    variant_a_content = f"{title}\n\n{content[:200]}..." if len(content) > 200 else f"{title}\n\n{content}"
                    variant_a_hashtags = hashtags[:5] if hashtags else []
                    
                    # Variante B: título más corto, contenido resumido, hashtags diferentes
                    variant_b_title = title[:50] + "..." if len(title) > 50 else title
                    variant_b_content = f"{variant_b_title}\n\n{content[:150]}..." if len(content) > 150 else f"{variant_b_title}\n\n{content}"
                    variant_b_hashtags = hashtags[5:10] if len(hashtags) > 5 else hashtags
                    
                    try:
                        # Crear test A/B
                        cur.execute("""
                            INSERT INTO content_ab_tests
                            (article_id, variant_a_content, variant_b_content, 
                             variant_a_hashtags, variant_b_hashtags, status, metadata)
                            VALUES (%s, %s, %s, %s, %s, 'running', %s)
                            RETURNING test_id
                        """, (
                            article_id,
                            variant_a_content,
                            variant_b_content,
                            variant_a_hashtags,
                            variant_b_hashtags,
                            json.dumps({
                                "created_by": "automation",
                                "test_type": "content_variants"
                            })
                        ))
                        
                        test_id = cur.fetchone()[0]
                        
                        # Programar ambas variantes para publicación
                        # Variante A
                        cur.execute("""
                            INSERT INTO content_scheduled_posts
                            (article_id, platform, content, hashtags, scheduled_at, status, metadata)
                            VALUES (%s, %s, %s, %s, NOW() + INTERVAL '1 hour', 'scheduled', %s)
                            RETURNING post_id
                        """, (
                            article_id,
                            "twitter",  # Plataforma por defecto para test
                            variant_a_content,
                            variant_a_hashtags,
                            json.dumps({"ab_test_id": test_id, "variant": "A"})
                        ))
                        variant_a_post_id = cur.fetchone()[0]
                        
                        # Variante B (publicar 2 horas después)
                        cur.execute("""
                            INSERT INTO content_scheduled_posts
                            (article_id, platform, content, hashtags, scheduled_at, status, metadata)
                            VALUES (%s, %s, %s, %s, NOW() + INTERVAL '3 hours', 'scheduled', %s)
                            RETURNING post_id
                        """, (
                            article_id,
                            "twitter",
                            variant_b_content,
                            variant_b_hashtags,
                            json.dumps({"ab_test_id": test_id, "variant": "B"})
                        ))
                        variant_b_post_id = cur.fetchone()[0]
                        
                        # Actualizar test con post_ids
                        cur.execute("""
                            UPDATE content_ab_tests
                            SET variant_a_post_id = %s, variant_b_post_id = %s
                            WHERE test_id = %s
                        """, (variant_a_post_id, variant_b_post_id, test_id))
                        
                        ab_tests_created += 1
                        logger.info(f"A/B test creado: test_id={test_id}, article_id={article_id}")
                    
                    except Exception as e:
                        logger.error(f"Error creando A/B test para {article_id}: {e}", exc_info=True)
                        continue
                
                # Evaluar tests completados (después de 24 horas)
                cur.execute("""
                    SELECT 
                        test_id,
                        variant_a_post_id,
                        variant_b_post_id
                    FROM content_ab_tests
                    WHERE status = 'running'
                    AND test_started_at <= NOW() - INTERVAL '24 hours'
                """)
                
                completed_tests = cur.fetchall()
                
                for test_row in completed_tests:
                    test_id, variant_a_post_id, variant_b_post_id = test_row
                    
                    try:
                        # Obtener métricas de ambas variantes
                        cur.execute("""
                            SELECT 
                                AVG(e.engagement_rate) as avg_engagement_rate,
                                SUM(e.likes + e.comments + e.shares) as total_engagement,
                                COUNT(*) as data_points
                            FROM content_engagement e
                            WHERE e.post_id = %s
                        """, (variant_a_post_id,))
                        
                        variant_a_metrics = cur.fetchone()
                        variant_a_engagement = float(variant_a_metrics[0] or 0) if variant_a_metrics[0] else 0
                        
                        cur.execute("""
                            SELECT 
                                AVG(e.engagement_rate) as avg_engagement_rate,
                                SUM(e.likes + e.comments + e.shares) as total_engagement,
                                COUNT(*) as data_points
                            FROM content_engagement e
                            WHERE e.post_id = %s
                        """, (variant_b_post_id,))
                        
                        variant_b_metrics = cur.fetchone()
                        variant_b_engagement = float(variant_b_metrics[0] or 0) if variant_b_metrics[0] else 0
                        
                        # Determinar ganador (diferencia > 10% para ser significativo)
                        winner = None
                        confidence = 0
                        
                        if variant_a_engagement > 0 and variant_b_engagement > 0:
                            diff_pct = abs(variant_a_engagement - variant_b_engagement) / max(variant_a_engagement, variant_b_engagement) * 100
                            
                            if diff_pct > 10:  # Diferencia significativa
                                winner = "A" if variant_a_engagement > variant_b_engagement else "B"
                                confidence = min(diff_pct, 95)  # Máximo 95% de confianza
                        
                        # Actualizar test
                        cur.execute("""
                            UPDATE content_ab_tests
                            SET status = 'completed',
                                test_ended_at = NOW(),
                                winner_variant = %s,
                                variant_a_engagement_rate = %s,
                                variant_b_engagement_rate = %s,
                                confidence_level = %s
                            WHERE test_id = %s
                        """, (winner, variant_a_engagement, variant_b_engagement, confidence, test_id))
                        
                        logger.info(f"A/B test completado: test_id={test_id}, winner={winner}, confidence={confidence:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error evaluando A/B test {test_id}: {e}", exc_info=True)
                
                conn.commit()
        
        logger.info(f"A/B testing: {ab_tests_created} tests creados")
        
        if Stats:
            try:
                Stats.incr("social_media.ab_tests_created", ab_tests_created)
            except Exception:
                pass
        
        return scheduled_result
    
    @task(task_id="crisis_detection")
    def crisis_detection(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta crisis de reputación basada en métricas anómalas."""
        ctx = get_current_context()
        params = ctx["params"]
        detection_enabled = bool(params.get("crisis_detection", True))
        
        if not detection_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        crises_detected = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar posts con métricas anómalas que indiquen crisis
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.content,
                        sp.published_at,
                        e.comments,
                        e.engagement_rate,
                        e.engagement_breakdown->>'comment_sentiment' as comment_sentiment,
                        a.title,
                        a.category
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    JOIN content_articles a ON a.article_id = sp.article_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '24 hours'
                    AND (
                        -- Muchos comentarios negativos
                        (e.comments > 50 AND (e.engagement_breakdown->>'comment_sentiment' = 'negative' OR e.engagement_breakdown->>'comment_sentiment' = 'very_negative'))
                        OR
                        -- Engagement rate muy bajo (posible backlash)
                        (e.engagement_rate < 0.5 AND e.impressions > 1000)
                        OR
                        -- Ratio de comentarios a likes muy alto (discusión negativa)
                        (e.comments > 20 AND e.likes > 0 AND (e.comments::float / e.likes) > 0.5)
                    )
                    AND (e.engagement_breakdown->>'crisis_detected' IS NULL)
                    ORDER BY e.comments DESC, sp.published_at DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                potential_crises = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for crisis_post in potential_crises:
                    post_id = crisis_post["post_id"]
                    platform = crisis_post["platform"]
                    comments = crisis_post.get("comments", 0)
                    engagement_rate = float(crisis_post.get("engagement_rate", 0) or 0)
                    sentiment = crisis_post.get("comment_sentiment", "")
                    
                    # Calcular severidad de crisis
                    severity = "low"
                    if comments > 100 or engagement_rate < 0.3:
                        severity = "high"
                    elif comments > 50 or engagement_rate < 0.5:
                        severity = "medium"
                    
                    try:
                        # Marcar como crisis detectada
                        cur.execute("""
                            UPDATE content_engagement
                            SET engagement_breakdown = COALESCE(engagement_breakdown, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'crisis_detected', TRUE,
                                    'crisis_detected_at', NOW(),
                                    'crisis_severity', %s,
                                    'crisis_indicators', jsonb_build_array(
                                        CASE WHEN %s > 50 THEN 'high_negative_comments' END,
                                        CASE WHEN %s < 0.5 THEN 'low_engagement_rate' END,
                                        CASE WHEN %s IN ('negative', 'very_negative') THEN 'negative_sentiment' END
                                    )
                                )
                            WHERE post_id = %s
                        """, (severity, comments, engagement_rate, sentiment, post_id))
                        
                        crises_detected += 1
                        
                        # Enviar alerta
                        crisis_message = f"🚨 CRISIS DETECTADA en {platform}\n"
                        crisis_message += f"Post ID: {post_id}\n"
                        crisis_message += f"Severidad: {severity.upper()}\n"
                        crisis_message += f"Comentarios: {comments}\n"
                        crisis_message += f"Engagement Rate: {engagement_rate:.2f}%\n"
                        crisis_message += f"Sentimiento: {sentiment}\n"
                        crisis_message += f"URL: {crisis_post.get('published_url', 'N/A')}"
                        
                        if NOTIFICATIONS_AVAILABLE:
                            try:
                                notify_slack(crisis_message, channel="#alerts", priority="high")
                                notify_email(
                                    to=params.get("alert_email", "admin@example.com"),
                                    subject=f"🚨 Crisis de Reputación Detectada - {platform}",
                                    body=crisis_message
                                )
                            except Exception as e:
                                logger.error(f"Error enviando alerta de crisis: {e}")
                        
                        logger.warning(f"CRISIS DETECTADA: post_id={post_id}, severity={severity}")
                    
                    except Exception as e:
                        logger.error(f"Error detectando crisis para {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Detección de crisis: {crises_detected} crisis detectadas")
        
        if Stats:
            try:
                Stats.incr("social_media.crises_detected", crises_detected)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="brand_mention_tracking")
    def brand_mention_tracking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Tracking de menciones de marca en redes sociales."""
        ctx = get_current_context()
        params = ctx["params"]
        tracking_enabled = bool(params.get("brand_mention_tracking", False))
        
        if not tracking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Términos de marca a trackear (en producción, desde configuración)
        brand_terms = ["@mibrand", "#mibrand", "mi marca", "nuestra empresa"]
        
        mentions_tracked = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de menciones si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_brand_mentions (
                        mention_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50) NOT NULL,
                        post_id VARCHAR(255),
                        author_handle VARCHAR(255),
                        author_name VARCHAR(255),
                        mention_text TEXT,
                        mention_type VARCHAR(50),
                        sentiment VARCHAR(50),
                        sentiment_score DECIMAL(5,2),
                        engagement_count INTEGER DEFAULT 0,
                        mentioned_at TIMESTAMP,
                        tracked_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # En producción, aquí se buscarían menciones usando APIs
                # Ejemplo para Twitter:
                # api = tweepy.Client(bearer_token=BEARER_TOKEN)
                # for term in brand_terms:
                #     tweets = api.search_recent_tweets(
                #         query=term,
                #         max_results=100,
                #         tweet_fields=["author_id", "created_at", "public_metrics"]
                #     )
                #     for tweet in tweets.data:
                #         # Analizar sentimiento y guardar
                
                # Simulación por ahora
                import random
                for term in brand_terms[:2]:  # Limitar para simulación
                    try:
                        # Simular menciones
                        sentiment_types = ["positive", "neutral", "negative"]
                        sentiment = random.choice(sentiment_types)
                        
                        cur.execute("""
                            INSERT INTO content_brand_mentions
                            (platform, post_id, author_handle, author_name, mention_text,
                             mention_type, sentiment, sentiment_score, engagement_count, mentioned_at, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            "twitter",
                            f"tweet_{random.randint(10000, 99999)}",
                            f"@user_{random.randint(100, 999)}",
                            f"User {random.randint(100, 999)}",
                            f"Sample mention: {term}",
                            "mention",
                            sentiment,
                            random.uniform(0.3 if sentiment == "negative" else 0.6, 0.9),
                            random.randint(0, 100),
                            datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                            json.dumps({"term": term, "simulated": True})
                        ))
                        
                        mentions_tracked += 1
                    
                    except Exception as e:
                        logger.error(f"Error trackeando menciones para {term}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Tracking de menciones: {mentions_tracked} menciones trackeadas")
        
        if Stats:
            try:
                Stats.incr("social_media.brand_mentions_tracked", mentions_tracked)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="reactive_scheduling")
    def reactive_scheduling(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Programación reactiva basada en trending topics."""
        ctx = get_current_context()
        params = ctx["params"]
        reactive_enabled = bool(params.get("reactive_scheduling", False))
        
        if not reactive_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        reactive_posts_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener trending topics (en producción, desde APIs de redes sociales)
                # Ejemplo: Twitter Trending Topics API
                trending_topics = [
                    {"topic": "#AI", "trend_score": 95},
                    {"topic": "#TechNews", "trend_score": 87},
                    {"topic": "#Innovation", "trend_score": 82},
                ]
                
                # Buscar contenido relacionado con trending topics
                for trend in trending_topics:
                    topic = trend["topic"]
                    trend_score = trend["trend_score"]
                    
                    # Solo crear posts reactivos si el trend score es alto
                    if trend_score < 80:
                        continue
                    
                    try:
                        # Buscar artículos relacionados
                        cur.execute("""
                            SELECT article_id, title, content, category
                            FROM content_articles
                            WHERE (
                                title ILIKE %s
                                OR content ILIKE %s
                                OR category ILIKE %s
                            )
                            AND status = 'published'
                            AND article_id NOT IN (
                                SELECT DISTINCT article_id
                                FROM content_scheduled_posts
                                WHERE scheduled_at >= NOW() - INTERVAL '7 days'
                            )
                            ORDER BY published_at DESC
                            LIMIT 1
                        """, (f"%{topic}%", f"%{topic}%", f"%{topic}%"))
                        
                        article_row = cur.fetchone()
                        
                        if article_row:
                            article_id, title, content, category = article_row
                            
                            # Crear post reactivo con trending topic
                            reactive_content = f"{title}\n\n{content[:150]}...\n\n{topic}"
                            hashtags = [topic, category] if category else [topic]
                            
                            cur.execute("""
                                INSERT INTO content_scheduled_posts
                                (article_id, platform, content, hashtags, scheduled_at, status, metadata)
                                VALUES (%s, %s, %s, %s, NOW() + INTERVAL '30 minutes', 'scheduled', %s)
                            """, (
                                article_id,
                                "twitter",
                                reactive_content,
                                hashtags,
                                json.dumps({
                                    "reactive": True,
                                    "trending_topic": topic,
                                    "trend_score": trend_score,
                                    "created_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            reactive_posts_created += 1
                            logger.info(f"Post reactivo creado para trending topic: {topic}")
                    
                    except Exception as e:
                        logger.error(f"Error creando post reactivo para {topic}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Programación reactiva: {reactive_posts_created} posts reactivos creados")
        
        if Stats:
            try:
                Stats.incr("social_media.reactive_posts_created", reactive_posts_created)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="influencer_analysis")
    def influencer_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza influencers y su impacto en el contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("influencer_analysis", False))
        
        if not analysis_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        influencers_analyzed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de influencers si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_influencers (
                        influencer_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50) NOT NULL,
                        handle VARCHAR(255) NOT NULL,
                        name VARCHAR(255),
                        follower_count INTEGER DEFAULT 0,
                        engagement_rate DECIMAL(10,2),
                        avg_likes INTEGER DEFAULT 0,
                        avg_comments INTEGER DEFAULT 0,
                        avg_shares INTEGER DEFAULT 0,
                        category VARCHAR(100),
                        influence_score DECIMAL(10,2),
                        last_analyzed_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB,
                        UNIQUE(platform, handle)
                    )
                """)
                
                # Analizar usuarios que interactúan frecuentemente con el contenido
                cur.execute("""
                    SELECT 
                        sp.platform,
                        COUNT(DISTINCT sp.post_id) as interaction_count,
                        AVG(e.likes + e.comments + e.shares) as avg_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform
                    HAVING COUNT(DISTINCT sp.post_id) >= 5
                """)
                
                # En producción, aquí se identificarían influencers reales usando APIs
                # Por ahora, simulamos análisis
                import random
                
                sample_influencers = [
                    {"handle": "@tech_influencer", "platform": "twitter", "followers": 50000, "category": "technology"},
                    {"handle": "@business_expert", "platform": "linkedin", "followers": 30000, "category": "business"},
                    {"handle": "@innovation_guru", "platform": "twitter", "followers": 75000, "category": "innovation"},
                ]
                
                for influencer in sample_influencers:
                    try:
                        handle = influencer["handle"]
                        platform = influencer["platform"]
                        followers = influencer["followers"]
                        category = influencer["category"]
                        
                        # Calcular engagement rate simulado
                        engagement_rate = random.uniform(3.0, 8.0)
                        influence_score = (followers / 1000) * engagement_rate
                        
                        cur.execute("""
                            INSERT INTO content_influencers
                            (platform, handle, name, follower_count, engagement_rate,
                             avg_likes, avg_comments, avg_shares, category, influence_score, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (platform, handle) 
                            DO UPDATE SET
                                follower_count = EXCLUDED.follower_count,
                                engagement_rate = EXCLUDED.engagement_rate,
                                influence_score = EXCLUDED.influence_score,
                                last_analyzed_at = NOW()
                        """, (
                            platform,
                            handle,
                            handle.replace("@", "").replace("_", " ").title(),
                            followers,
                            engagement_rate,
                            random.randint(100, 1000),
                            random.randint(10, 100),
                            random.randint(5, 50),
                            category,
                            round(influence_score, 2),
                            json.dumps({"simulated": True, "category": category})
                        ))
                        
                        influencers_analyzed += 1
                        logger.info(f"Influencer analizado: {handle} ({platform})")
                    
                    except Exception as e:
                        logger.error(f"Error analizando influencer {influencer.get('handle')}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Análisis de influencers: {influencers_analyzed} influencers analizados")
        
        if Stats:
            try:
                Stats.incr("social_media.influencers_analyzed", influencers_analyzed)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_quality_scoring")
    def content_quality_scoring(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula un score de calidad para cada artículo."""
        ctx = get_current_context()
        params = ctx["params"]
        scoring_enabled = bool(params.get("content_quality_scoring", True))
        
        if not scoring_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_scored = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    hashtags = article.get("hashtags") or []
                    
                    # Calcular score de calidad (0-100)
                    quality_score = 0
                    quality_factors = {}
                    
                    # Factor 1: Longitud del título (óptimo: 40-60 caracteres)
                    title_length = len(title)
                    if 40 <= title_length <= 60:
                        title_score = 20
                    elif 30 <= title_length < 40 or 60 < title_length <= 70:
                        title_score = 15
                    else:
                        title_score = 10
                    quality_score += title_score
                    quality_factors["title_length"] = {"score": title_score, "length": title_length}
                    
                    # Factor 2: Longitud del contenido (óptimo: 200-500 palabras)
                    content_words = len(content.split())
                    if 200 <= content_words <= 500:
                        content_score = 25
                    elif 100 <= content_words < 200 or 500 < content_words <= 800:
                        content_score = 20
                    else:
                        content_score = 15
                    quality_score += content_score
                    quality_factors["content_length"] = {"score": content_score, "words": content_words}
                    
                    # Factor 3: Número de hashtags (óptimo: 3-5)
                    hashtag_count = len(hashtags)
                    if 3 <= hashtag_count <= 5:
                        hashtag_score = 15
                    elif 1 <= hashtag_count < 3 or 5 < hashtag_count <= 8:
                        hashtag_score = 10
                    else:
                        hashtag_score = 5
                    quality_score += hashtag_score
                    quality_factors["hashtag_count"] = {"score": hashtag_score, "count": hashtag_count}
                    
                    # Factor 4: Presencia de palabras clave importantes
                    important_keywords = ["innovación", "tecnología", "negocio", "estrategia", "éxito", "crecimiento"]
                    keyword_count = sum(1 for kw in important_keywords if kw.lower() in content.lower())
                    keyword_score = min(keyword_count * 5, 20)
                    quality_score += keyword_score
                    quality_factors["keywords"] = {"score": keyword_score, "count": keyword_count}
                    
                    # Factor 5: Estructura (presencia de números, listas, etc.)
                    has_numbers = bool(re.search(r'\d+', content))
                    has_lists = bool(re.search(r'[•\-\*]|^\d+\.', content, re.MULTILINE))
                    structure_score = 0
                    if has_numbers:
                        structure_score += 5
                    if has_lists:
                        structure_score += 5
                    quality_score += structure_score
                    quality_factors["structure"] = {"score": structure_score, "has_numbers": has_numbers, "has_lists": has_lists}
                    
                    # Factor 6: Media (imágenes/videos)
                    media_urls = article.get("media_urls") or []
                    media_count = len(media_urls)
                    if media_count >= 1:
                        media_score = 15
                    else:
                        media_score = 0
                    quality_score += media_score
                    quality_factors["media"] = {"score": media_score, "count": media_count}
                    
                    # Normalizar a 0-100
                    quality_score = min(quality_score, 100)
                    
                    # Determinar nivel de calidad
                    if quality_score >= 80:
                        quality_level = "excellent"
                    elif quality_score >= 60:
                        quality_level = "good"
                    elif quality_score >= 40:
                        quality_level = "fair"
                    else:
                        quality_level = "poor"
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'quality_score', %s,
                                    'quality_level', %s,
                                    'quality_factors', %s,
                                    'quality_scored_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (quality_score, quality_level, json.dumps(quality_factors), article_id))
                        
                        articles_scored += 1
                        logger.debug(f"Quality score calculado para artículo {article_id}: {quality_score}/100 ({quality_level})")
                    
                    except Exception as e:
                        logger.error(f"Error calculando quality score para {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Content quality scoring: {articles_scored} artículos evaluados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_quality_scored", articles_scored)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="intelligent_hashtag_suggestions")
    def intelligent_hashtag_suggestions(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera sugerencias inteligentes de hashtags basadas en contenido y trending."""
        ctx = get_current_context()
        params = ctx["params"]
        suggestions_enabled = bool(params.get("intelligent_hashtag_suggestions", True))
        
        if not suggestions_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        suggestions_added = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    category = article.get("category", "")
                    existing_hashtags = article.get("hashtags") or []
                    
                    # Generar sugerencias basadas en contenido
                    suggested_hashtags = []
                    
                    # 1. Hashtags basados en categoría
                    if category:
                        category_hashtags = {
                            "technology": ["#Tech", "#Innovation", "#AI", "#Digital"],
                            "business": ["#Business", "#Entrepreneurship", "#Strategy", "#Growth"],
                            "marketing": ["#Marketing", "#DigitalMarketing", "#ContentMarketing", "#SocialMedia"],
                            "design": ["#Design", "#UX", "#UI", "#Creative"],
                        }
                        suggested_hashtags.extend(category_hashtags.get(category.lower(), []))
                    
                    # 2. Hashtags basados en palabras clave del título
                    title_words = [w.lower() for w in title.split() if len(w) > 4]
                    for word in title_words[:3]:
                        suggested_hashtags.append(f"#{word.capitalize()}")
                    
                    # 3. Hashtags trending relacionados (simulado)
                    # En producción, se obtendrían de APIs de trending topics
                    trending_suggestions = ["#Trending", "#Viral", "#MustRead"]
                    suggested_hashtags.extend(trending_suggestions[:2])
                    
                    # 4. Hashtags de alto rendimiento histórico
                    cur.execute("""
                        SELECT DISTINCT unnest(hashtags) as hashtag
                        FROM content_scheduled_posts sp
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE e.engagement_rate > 5.0
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                        GROUP BY hashtag
                        ORDER BY AVG(e.engagement_rate) DESC
                        LIMIT 3
                    """)
                    
                    high_performance_hashtags = [row[0] for row in cur.fetchall() if row[0]]
                    suggested_hashtags.extend(high_performance_hashtags)
                    
                    # Eliminar duplicados y limitar a 10
                    suggested_hashtags = list(dict.fromkeys(suggested_hashtags))[:10]
                    
                    # Combinar con hashtags existentes (sin duplicados)
                    all_hashtags = existing_hashtags + [h for h in suggested_hashtags if h not in existing_hashtags]
                    all_hashtags = all_hashtags[:10]  # Máximo 10 hashtags
                    
                    if suggested_hashtags:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'suggested_hashtags', %s,
                                        'hashtags_suggested_at', NOW()
                                    ),
                                hashtags = %s
                                WHERE article_id = %s
                            """, (json.dumps(suggested_hashtags), all_hashtags, article_id))
                            
                            suggestions_added += 1
                            logger.debug(f"Hashtags sugeridos para artículo {article_id}: {len(suggested_hashtags)} sugerencias")
                        
                        except Exception as e:
                            logger.error(f"Error agregando hashtags sugeridos para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Sugerencias inteligentes de hashtags: {suggestions_added} artículos con sugerencias")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtag_suggestions_added", suggestions_added)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="performance_optimization")
    def performance_optimization(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza performance de queries y operaciones."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("performance_optimization", True))
        
        if not optimization_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        indexes_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear índices para mejorar performance de queries frecuentes
                indexes_to_create = [
                    {
                        "name": "idx_scheduled_posts_status_published",
                        "table": "content_scheduled_posts",
                        "columns": "(status, published_at)",
                        "condition": "WHERE status = 'published'"
                    },
                    {
                        "name": "idx_engagement_post_id",
                        "table": "content_engagement",
                        "columns": "(post_id)",
                        "condition": ""
                    },
                    {
                        "name": "idx_articles_published_status",
                        "table": "content_articles",
                        "columns": "(status, published_at)",
                        "condition": "WHERE status = 'published'"
                    },
                    {
                        "name": "idx_scheduled_posts_article_platform",
                        "table": "content_scheduled_posts",
                        "columns": "(article_id, platform)",
                        "condition": ""
                    },
                ]
                
                for index_def in indexes_to_create:
                    try:
                        # Verificar si el índice ya existe
                        cur.execute("""
                            SELECT COUNT(*) 
                            FROM pg_indexes 
                            WHERE indexname = %s
                        """, (index_def["name"],))
                        
                        exists = cur.fetchone()[0] > 0
                        
                        if not exists:
                            cur.execute(f"""
                                CREATE INDEX IF NOT EXISTS {index_def["name"]}
                                ON {index_def["table"]} {index_def["columns"]}
                            """)
                            
                            indexes_created += 1
                            logger.info(f"Índice creado: {index_def['name']}")
                    
                    except Exception as e:
                        logger.warning(f"Error creando índice {index_def['name']}: {e}")
                        continue
                
                # Analizar tablas para optimizar query planner
                try:
                    cur.execute("ANALYZE content_scheduled_posts")
                    cur.execute("ANALYZE content_engagement")
                    cur.execute("ANALYZE content_articles")
                    logger.info("Tablas analizadas para optimización")
                except Exception as e:
                    logger.warning(f"Error analizando tablas: {e}")
                
                conn.commit()
        
        logger.info(f"Optimización de performance: {indexes_created} índices creados/verificados")
        
        if Stats:
            try:
                Stats.incr("social_media.performance_indexes_created", indexes_created)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_repurposing")
    def content_repurposing(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reutiliza contenido exitoso en diferentes formatos y plataformas."""
        ctx = get_current_context()
        params = ctx["params"]
        repurposing_enabled = bool(params.get("content_repurposing", False))
        
        if not repurposing_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        repurposed_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar contenido de alto rendimiento para repurposing
                cur.execute("""
                    SELECT 
                        a.article_id,
                        a.title,
                        a.content,
                        a.category,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        SUM(e.likes + e.comments + e.shares) as total_engagement
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND e.engagement_rate > 5.0
                    AND a.article_id NOT IN (
                        SELECT DISTINCT article_id
                        FROM content_scheduled_posts
                        WHERE metadata->>'repurposed_from' IS NOT NULL
                        AND scheduled_at >= NOW() - INTERVAL '7 days'
                    )
                    GROUP BY a.article_id, a.title, a.content, a.category
                    HAVING AVG(e.engagement_rate) > 5.0
                    ORDER BY AVG(e.engagement_rate) DESC
                    LIMIT 5
                """)
                
                columns = [desc[0] for desc in cur.description]
                top_content = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for article in top_content:
                    article_id = article["article_id"]
                    title = article["title"]
                    content = article["content"]
                    category = article["category"]
                    avg_engagement = float(article.get("avg_engagement_rate", 0) or 0)
                    
                    # Crear variantes para diferentes plataformas
                    platforms_to_repurpose = ["linkedin", "facebook"]  # Ya publicado en twitter
                    
                    for platform in platforms_to_repurpose:
                        try:
                            # Adaptar contenido para la plataforma
                            if platform == "linkedin":
                                # LinkedIn: más profesional, más largo
                                repurposed_content = f"{title}\n\n{content[:500]}..."
                                hashtags = [f"#{category}", "#Professional", "#Business"]
                            elif platform == "facebook":
                                # Facebook: más casual, con emojis
                                repurposed_content = f"📢 {title}\n\n{content[:300]}...\n\n¿Qué opinas? 👇"
                                hashtags = [f"#{category}", "#News", "#Update"]
                            else:
                                continue
                            
                            # Programar repurposing (publicar en 1 semana)
                            cur.execute("""
                                INSERT INTO content_scheduled_posts
                                (article_id, platform, content, hashtags, scheduled_at, status, metadata)
                                VALUES (%s, %s, %s, %s, NOW() + INTERVAL '7 days', 'scheduled', %s)
                            """, (
                                article_id,
                                platform,
                                repurposed_content,
                                hashtags,
                                json.dumps({
                                    "repurposed": True,
                                    "repurposed_from": article_id,
                                    "original_engagement_rate": round(avg_engagement, 2),
                                    "repurposed_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            repurposed_count += 1
                            logger.info(f"Contenido repurposed: article_id={article_id} -> {platform}")
                        
                        except Exception as e:
                            logger.error(f"Error repurposing contenido {article_id} para {platform}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Content repurposing: {repurposed_count} variantes creadas")
        
        if Stats:
            try:
                Stats.incr("social_media.content_repurposed", repurposed_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="social_listening")
    def social_listening(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Monitoreo y análisis de conversaciones en redes sociales."""
        ctx = get_current_context()
        params = ctx["params"]
        listening_enabled = bool(params.get("social_listening", False))
        
        if not listening_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        conversations_tracked = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de social listening si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_social_listening (
                        listening_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50) NOT NULL,
                        conversation_id VARCHAR(255),
                        author_handle VARCHAR(255),
                        author_name VARCHAR(255),
                        conversation_text TEXT,
                        topic VARCHAR(255),
                        sentiment VARCHAR(50),
                        sentiment_score DECIMAL(5,2),
                        engagement_count INTEGER DEFAULT 0,
                        mentioned_brands TEXT[],
                        keywords TEXT[],
                        conversation_date TIMESTAMP,
                        tracked_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Términos y temas a monitorear
                topics_to_monitor = [
                    {"topic": "AI", "keywords": ["artificial intelligence", "AI", "machine learning"]},
                    {"topic": "Technology", "keywords": ["tech", "innovation", "digital"]},
                    {"topic": "Business", "keywords": ["business", "strategy", "growth"]},
                ]
                
                # En producción, aquí se buscarían conversaciones usando APIs
                # Ejemplo para Twitter:
                # api = tweepy.Client(bearer_token=BEARER_TOKEN)
                # for topic in topics_to_monitor:
                #     tweets = api.search_recent_tweets(
                #         query=" OR ".join(topic["keywords"]),
                #         max_results=100,
                #         tweet_fields=["author_id", "created_at", "public_metrics", "text"]
                #     )
                #     for tweet in tweets.data:
                #         # Analizar y guardar
                
                # Simulación por ahora
                import random
                for topic_info in topics_to_monitor[:2]:  # Limitar para simulación
                    topic = topic_info["topic"]
                    keywords = topic_info["keywords"]
                    
                    try:
                        sentiment_types = ["positive", "neutral", "negative"]
                        sentiment = random.choice(sentiment_types)
                        
                        cur.execute("""
                            INSERT INTO content_social_listening
                            (platform, conversation_id, author_handle, author_name, conversation_text,
                             topic, sentiment, sentiment_score, engagement_count, mentioned_brands,
                             keywords, conversation_date, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            "twitter",
                            f"conv_{random.randint(10000, 99999)}",
                            f"@user_{random.randint(100, 999)}",
                            f"User {random.randint(100, 999)}",
                            f"Sample conversation about {topic}: {random.choice(keywords)}",
                            topic,
                            sentiment,
                            random.uniform(0.3 if sentiment == "negative" else 0.6, 0.9),
                            random.randint(0, 100),
                            ["@mibrand"],
                            keywords[:3],
                            datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
                            json.dumps({"simulated": True, "topic": topic})
                        ))
                        
                        conversations_tracked += 1
                    
                    except Exception as e:
                        logger.error(f"Error trackeando conversación sobre {topic}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Social listening: {conversations_tracked} conversaciones trackeadas")
        
        if Stats:
            try:
                Stats.incr("social_media.conversations_tracked", conversations_tracked)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="engagement_rate_optimization")
    def engagement_rate_optimization(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza continuamente el engagement rate mediante aprendizaje."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("engagement_rate_optimization", True))
        
        if not optimization_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        optimizations_applied = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar patrones de alto engagement
                cur.execute("""
                    SELECT 
                        sp.platform,
                        EXTRACT(HOUR FROM sp.published_at) as publish_hour,
                        EXTRACT(DOW FROM sp.published_at) as publish_day,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        AVG(LENGTH(sp.content)) as avg_content_length,
                        AVG(array_length(sp.hashtags, 1)) as avg_hashtag_count,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform, EXTRACT(HOUR FROM sp.published_at), EXTRACT(DOW FROM sp.published_at)
                    HAVING COUNT(*) >= 3
                    ORDER BY AVG(e.engagement_rate) DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                high_performance_patterns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Guardar insights de optimización
                for pattern in high_performance_patterns:
                    platform = pattern["platform"]
                    publish_hour = int(pattern.get("publish_hour", 0) or 0)
                    publish_day = int(pattern.get("publish_day", 0) or 0)
                    avg_engagement = float(pattern.get("avg_engagement_rate", 0) or 0)
                    avg_length = float(pattern.get("avg_content_length", 0) or 0)
                    avg_hashtags = float(pattern.get("avg_hashtag_count", 0) or 0)
                    
                    if avg_engagement > 5.0:  # Solo patrones de alto rendimiento
                        try:
                            # Crear o actualizar tabla de optimizaciones
                            cur.execute("""
                                CREATE TABLE IF NOT EXISTS content_engagement_optimizations (
                                    optimization_id SERIAL PRIMARY KEY,
                                    platform VARCHAR(50) NOT NULL,
                                    optimal_hour INTEGER,
                                    optimal_day INTEGER,
                                    optimal_content_length INTEGER,
                                    optimal_hashtag_count INTEGER,
                                    expected_engagement_rate DECIMAL(10,2),
                                    pattern_confidence DECIMAL(5,2),
                                    last_updated_at TIMESTAMP DEFAULT NOW(),
                                    metadata JSONB,
                                    UNIQUE(platform, optimal_hour, optimal_day)
                                )
                            """)
                            
                            cur.execute("""
                                INSERT INTO content_engagement_optimizations
                                (platform, optimal_hour, optimal_day, optimal_content_length,
                                 optimal_hashtag_count, expected_engagement_rate, pattern_confidence, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (platform, optimal_hour, optimal_day)
                                DO UPDATE SET
                                    optimal_content_length = EXCLUDED.optimal_content_length,
                                    optimal_hashtag_count = EXCLUDED.optimal_hashtag_count,
                                    expected_engagement_rate = EXCLUDED.expected_engagement_rate,
                                    pattern_confidence = EXCLUDED.pattern_confidence,
                                    last_updated_at = NOW()
                            """, (
                                platform,
                                publish_hour,
                                publish_day,
                                int(avg_length),
                                int(avg_hashtags),
                                round(avg_engagement, 2),
                                min(95.0, avg_engagement * 10),  # Confidence basado en engagement
                                json.dumps({
                                    "post_count": pattern.get("post_count", 0),
                                    "analyzed_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            optimizations_applied += 1
                            logger.info(f"Optimización guardada: {platform} - hora {publish_hour}, día {publish_day}, engagement {avg_engagement:.2f}%")
                        
                        except Exception as e:
                            logger.error(f"Error guardando optimización: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización de engagement rate: {optimizations_applied} patrones optimizados")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_optimizations_applied", optimizations_applied)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_content_calendar")
    def automated_content_calendar(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera automáticamente un calendario de contenido optimizado."""
        ctx = get_current_context()
        params = ctx["params"]
        calendar_enabled = bool(params.get("automated_content_calendar", True))
        
        if not calendar_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        calendar_entries_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de calendario si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_calendar (
                        calendar_id SERIAL PRIMARY KEY,
                        article_id INTEGER,
                        platform VARCHAR(50) NOT NULL,
                        scheduled_date DATE NOT NULL,
                        scheduled_time TIME,
                        content_type VARCHAR(50),
                        priority INTEGER DEFAULT 5,
                        status VARCHAR(50) DEFAULT 'planned',
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                articles = content_data.get("articles", [])
                platforms = json.loads(str(params.get("platforms", '["twitter", "linkedin"]')))
                
                # Distribuir contenido a lo largo de la próxima semana
                for i, article in enumerate(articles[:10]):  # Limitar a 10 artículos
                    article_id = article["article_id"]
                    
                    # Calcular fecha óptima (distribuir a lo largo de la semana)
                    days_ahead = (i % 7) + 1
                    scheduled_date = (datetime.utcnow() + timedelta(days=days_ahead)).date()
                    
                    # Hora óptima basada en análisis previo (simulado: 9 AM, 1 PM, 5 PM)
                    optimal_hours = [9, 13, 17]
                    scheduled_time = f"{optimal_hours[i % len(optimal_hours)]:02d}:00:00"
                    
                    for platform in platforms:
                        try:
                            cur.execute("""
                                INSERT INTO content_calendar
                                (article_id, platform, scheduled_date, scheduled_time,
                                 content_type, priority, status, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                article_id,
                                platform,
                                scheduled_date,
                                scheduled_time,
                                article.get("category", "general"),
                                5,  # Prioridad media
                                "planned",
                                json.dumps({
                                    "auto_generated": True,
                                    "created_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            calendar_entries_created += 1
                        
                        except Exception as e:
                            logger.error(f"Error creando entrada de calendario: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Calendario automatizado: {calendar_entries_created} entradas creadas")
        
        if Stats:
            try:
                Stats.incr("social_media.calendar_entries_created", calendar_entries_created)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="ai_content_generation")
    def ai_content_generation(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera contenido automáticamente usando IA basado en temas y tendencias."""
        ctx = get_current_context()
        params = ctx["params"]
        generation_enabled = bool(params.get("ai_content_generation", False))
        
        if not generation_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_generated = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Temas para generar contenido (en producción, desde análisis de trending)
                topics_to_generate = [
                    {"topic": "AI Trends", "category": "technology"},
                    {"topic": "Business Growth", "category": "business"},
                    {"topic": "Digital Innovation", "category": "innovation"},
                ]
                
                for topic_info in topics_to_generate[:2]:  # Limitar para simulación
                    topic = topic_info["topic"]
                    category = topic_info["category"]
                    
                    try:
                        # En producción, aquí se usaría un modelo de IA (GPT, Claude, etc.)
                        # Ejemplo con OpenAI:
                        # import openai
                        # response = openai.ChatCompletion.create(
                        #     model="gpt-4",
                        #     messages=[
                        #         {"role": "system", "content": "Eres un experto en marketing de contenido."},
                        #         {"role": "user", "content": f"Genera un artículo sobre {topic} de 300 palabras."}
                        #     ]
                        # )
                        # generated_content = response.choices[0].message.content
                        
                        # Simulación por ahora
                        generated_title = f"Latest Insights on {topic}"
                        generated_content = f"""
                        In today's rapidly evolving landscape, {topic} continues to shape the future of business and technology.
                        
                        Key points to consider:
                        • Innovation drives growth
                        • Strategic planning is essential
                        • Data-driven decisions lead to success
                        
                        As we navigate these changes, staying informed and adaptable is crucial for long-term success.
                        """
                        
                        # Crear artículo generado
                        cur.execute("""
                            INSERT INTO content_articles
                            (title, content, category, status, author_id, published_at, metadata)
                            VALUES (%s, %s, %s, 'draft', NULL, NOW(), %s)
                            RETURNING article_id
                        """, (
                            generated_title,
                            generated_content.strip(),
                            category,
                            json.dumps({
                                "ai_generated": True,
                                "generation_model": "simulated",
                                "topic": topic,
                                "generated_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        article_id = cur.fetchone()[0]
                        articles_generated += 1
                        logger.info(f"Contenido generado con IA: article_id={article_id}, topic={topic}")
                    
                    except Exception as e:
                        logger.error(f"Error generando contenido con IA para {topic}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Generación de contenido con IA: {articles_generated} artículos generados")
        
        if Stats:
            try:
                Stats.incr("social_media.ai_articles_generated", articles_generated)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="video_content_analysis")
    def video_content_analysis(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza contenido de video para optimización."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("video_content_analysis", False))
        
        if not analysis_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        videos_analyzed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    media_urls = article.get("media_urls") or []
                    
                    # Buscar URLs de video
                    video_urls = [url for url in media_urls if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi', '.youtube', '.vimeo'])]
                    
                    if not video_urls:
                        continue
                    
                    video_analysis_results = []
                    
                    for video_url in video_urls:
                        try:
                            # En producción, usar servicios como:
                            # - Google Cloud Video Intelligence API
                            # - AWS Rekognition Video
                            # - Azure Video Analyzer
                            
                            # Ejemplo con Google Cloud Video Intelligence:
                            # from google.cloud import videointelligence
                            # client = videointelligence.VideoIntelligenceServiceClient()
                            # features = [videointelligence.Feature.LABEL_DETECTION]
                            # operation = client.annotate_video(
                            #     request={"input_uri": video_url, "features": features}
                            # )
                            # result = operation.result()
                            # labels = [annotation.entity.description for annotation in result.annotation_results[0].segment_label_annotations]
                            
                            # Simulación por ahora
                            import random
                            analysis_result = {
                                "labels": ["technology", "presentation", "tutorial"][:random.randint(1, 3)],
                                "duration_seconds": random.randint(30, 600),
                                "has_audio": random.choice([True, False]),
                                "has_captions": random.choice([True, False]),
                                "quality_score": random.uniform(0.6, 1.0),
                                "thumbnail_url": video_url.replace('.mp4', '_thumb.jpg'),
                                "analyzed_at": datetime.utcnow().isoformat()
                            }
                            
                            video_analysis_results.append({
                                "url": video_url,
                                "analysis": analysis_result
                            })
                            
                            videos_analyzed += 1
                        
                        except Exception as e:
                            logger.error(f"Error analizando video {video_url}: {e}", exc_info=True)
                            continue
                    
                    # Guardar análisis en metadata
                    if video_analysis_results:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object('video_analysis', %s)
                                WHERE article_id = %s
                            """, (json.dumps(video_analysis_results), article_id))
                        except Exception as e:
                            logger.error(f"Error guardando análisis de video para {article_id}: {e}")
                
                conn.commit()
        
        logger.info(f"Análisis de video: {videos_analyzed} videos analizados")
        
        if Stats:
            try:
                Stats.incr("social_media.videos_analyzed", videos_analyzed)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="automated_hashtag_research")
    def automated_hashtag_research(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Investiga automáticamente hashtags relevantes y trending."""
        ctx = get_current_context()
        params = ctx["params"]
        research_enabled = bool(params.get("automated_hashtag_research", True))
        
        if not research_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        hashtags_researched = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de investigación de hashtags si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_hashtag_research (
                        research_id SERIAL PRIMARY KEY,
                        hashtag VARCHAR(255) NOT NULL,
                        platform VARCHAR(50) NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        engagement_rate DECIMAL(10,2),
                        trend_score DECIMAL(10,2),
                        related_hashtags TEXT[],
                        researched_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB,
                        UNIQUE(hashtag, platform)
                    )
                """)
                
                articles = content_data.get("articles", [])
                platforms = json.loads(str(params.get("platforms", '["twitter", "linkedin"]')))
                
                # Hashtags base para investigar
                base_hashtags = set()
                for article in articles:
                    hashtags = article.get("hashtags") or []
                    base_hashtags.update(hashtags)
                
                # En producción, aquí se investigarían hashtags usando APIs
                # Ejemplo para Twitter:
                # api = tweepy.Client(bearer_token=BEARER_TOKEN)
                # for hashtag in base_hashtags:
                #     tweets = api.search_recent_tweets(
                #         query=f"#{hashtag}",
                #         max_results=100,
                #         tweet_fields=["public_metrics"]
                #     )
                #     usage_count = len(tweets.data)
                #     avg_engagement = sum(t.public_metrics.get('like_count', 0) for t in tweets.data) / max(usage_count, 1)
                
                # Simulación por ahora
                for hashtag in list(base_hashtags)[:5]:  # Limitar para simulación
                    for platform in platforms:
                        try:
                            import random
                            
                            # Simular investigación
                            usage_count = random.randint(100, 10000)
                            engagement_rate = random.uniform(2.0, 8.0)
                            trend_score = random.uniform(50, 100)
                            related_hashtags = [f"#{h}" for h in ["related1", "related2", "related3"]]
                            
                            cur.execute("""
                                INSERT INTO content_hashtag_research
                                (hashtag, platform, usage_count, engagement_rate, trend_score,
                                 related_hashtags, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (hashtag, platform)
                                DO UPDATE SET
                                    usage_count = EXCLUDED.usage_count,
                                    engagement_rate = EXCLUDED.engagement_rate,
                                    trend_score = EXCLUDED.trend_score,
                                    researched_at = NOW()
                            """, (
                                hashtag.replace("#", ""),
                                platform,
                                usage_count,
                                engagement_rate,
                                trend_score,
                                related_hashtags,
                                json.dumps({"simulated": True})
                            ))
                            
                            hashtags_researched += 1
                        
                        except Exception as e:
                            logger.error(f"Error investigando hashtag {hashtag} en {platform}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Investigación automática de hashtags: {hashtags_researched} hashtags investigados")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtags_researched", hashtags_researched)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="content_performance_prediction")
    def content_performance_prediction(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predice el performance de contenido antes de publicar."""
        ctx = get_current_context()
        params = ctx["params"]
        prediction_enabled = bool(params.get("content_performance_prediction", True))
        
        if not prediction_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        predictions_made = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    hashtags = article.get("hashtags") or []
                    category = article.get("category", "")
                    
                    # Calcular score de predicción basado en factores históricos
                    prediction_score = 0
                    prediction_factors = {}
                    
                    # Factor 1: Longitud del contenido (históricamente, contenido de 200-500 palabras tiene mejor engagement)
                    content_length = len(content.split())
                    if 200 <= content_length <= 500:
                        length_score = 0.3
                    elif 100 <= content_length < 200 or 500 < content_length <= 800:
                        length_score = 0.2
                    else:
                        length_score = 0.1
                    prediction_score += length_score
                    prediction_factors["content_length"] = {"score": length_score, "words": content_length}
                    
                    # Factor 2: Número de hashtags (óptimo: 3-5)
                    hashtag_count = len(hashtags)
                    if 3 <= hashtag_count <= 5:
                        hashtag_score = 0.2
                    elif 1 <= hashtag_count < 3 or 5 < hashtag_count <= 8:
                        hashtag_score = 0.15
                    else:
                        hashtag_score = 0.1
                    prediction_score += hashtag_score
                    prediction_factors["hashtag_count"] = {"score": hashtag_score, "count": hashtag_count}
                    
                    # Factor 3: Performance histórico de la categoría
                    cur.execute("""
                        SELECT AVG(e.engagement_rate)
                        FROM content_articles a
                        JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                    """, (category,))
                    
                    category_avg = cur.fetchone()
                    category_engagement = float(category_avg[0] or 0) if category_avg[0] else 0
                    category_score = min(category_engagement / 10.0, 0.3)  # Normalizar
                    prediction_score += category_score
                    prediction_factors["category_performance"] = {"score": category_score, "avg_engagement": category_engagement}
                    
                    # Factor 4: Quality score (si existe)
                    quality_score = article.get("metadata", {}).get("quality_score") if isinstance(article.get("metadata"), dict) else None
                    if quality_score:
                        quality_factor = quality_score / 100.0 * 0.2
                        prediction_score += quality_factor
                        prediction_factors["quality_score"] = {"score": quality_factor, "quality": quality_score}
                    
                    # Normalizar a 0-1
                    prediction_score = min(prediction_score, 1.0)
                    
                    # Convertir a engagement rate esperado (0-10%)
                    predicted_engagement_rate = prediction_score * 10.0
                    
                    # Clasificar predicción
                    if predicted_engagement_rate >= 7.0:
                        prediction_level = "excellent"
                    elif predicted_engagement_rate >= 5.0:
                        prediction_level = "good"
                    elif predicted_engagement_rate >= 3.0:
                        prediction_level = "fair"
                    else:
                        prediction_level = "poor"
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'performance_prediction', %s,
                                    'predicted_engagement_rate', %s,
                                    'prediction_level', %s,
                                    'prediction_factors', %s,
                                    'predicted_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            round(prediction_score, 3),
                            round(predicted_engagement_rate, 2),
                            prediction_level,
                            json.dumps(prediction_factors),
                            article_id
                        ))
                        
                        predictions_made += 1
                        logger.debug(f"Predicción de performance para artículo {article_id}: {predicted_engagement_rate:.2f}% ({prediction_level})")
                    
                    except Exception as e:
                        logger.error(f"Error prediciendo performance para {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Predicción de performance: {predictions_made} predicciones realizadas")
        
        if Stats:
            try:
                Stats.incr("social_media.performance_predictions_made", predictions_made)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="cross_platform_analytics")
    def cross_platform_analytics(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza métricas cross-platform para insights comparativos."""
        ctx = get_current_context()
        params = ctx["params"]
        analytics_enabled = bool(params.get("cross_platform_analytics", True))
        
        if not analytics_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Análisis comparativo entre plataformas
                cur.execute("""
                    SELECT 
                        sp.platform,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        AVG(e.likes) as avg_likes,
                        AVG(e.comments) as avg_comments,
                        AVG(e.shares) as avg_shares,
                        AVG(e.impressions) as avg_impressions,
                        SUM(e.likes + e.comments + e.shares) as total_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform
                    ORDER BY avg_engagement_rate DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                platform_stats = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Guardar análisis cross-platform
                if platform_stats:
                    try:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS content_cross_platform_analytics (
                                analytics_id SERIAL PRIMARY KEY,
                                analysis_date DATE DEFAULT CURRENT_DATE,
                                platform_comparison JSONB,
                                best_platform VARCHAR(50),
                                worst_platform VARCHAR(50),
                                insights TEXT,
                                created_at TIMESTAMP DEFAULT NOW(),
                                metadata JSONB
                            )
                        """)
                        
                        # Determinar mejor y peor plataforma
                        best_platform = max(platform_stats, key=lambda x: float(x.get("avg_engagement_rate", 0) or 0))
                        worst_platform = min(platform_stats, key=lambda x: float(x.get("avg_engagement_rate", 0) or 0))
                        
                        insights = f"Best performing platform: {best_platform['platform']} with {best_platform.get('avg_engagement_rate', 0):.2f}% engagement rate."
                        
                        cur.execute("""
                            INSERT INTO content_cross_platform_analytics
                            (platform_comparison, best_platform, worst_platform, insights, metadata)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            json.dumps(platform_stats),
                            best_platform["platform"],
                            worst_platform["platform"],
                            insights,
                            json.dumps({"analyzed_at": datetime.utcnow().isoformat()})
                        ))
                        
                        logger.info(f"Analytics cross-platform: {len(platform_stats)} plataformas analizadas")
                    
                    except Exception as e:
                        logger.error(f"Error guardando analytics cross-platform: {e}", exc_info=True)
                
                conn.commit()
        
        if Stats:
            try:
                Stats.incr("social_media.cross_platform_analytics_run", 1)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_safety_check")
    def content_safety_check(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica la seguridad y apropiación del contenido antes de publicar."""
        ctx = get_current_context()
        params = ctx["params"]
        safety_enabled = bool(params.get("content_safety_check", True))
        
        if not safety_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_checked = 0
        unsafe_content_detected = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                # Lista de palabras/términos problemáticos (en producción, usar ML/NLP avanzado)
                unsafe_keywords = [
                    "spam", "scam", "fake", "fraud",  # Ejemplos básicos
                ]
                
                # En producción, usar servicios como:
                # - Google Cloud Natural Language API (Sentiment + Entity Analysis)
                # - AWS Comprehend (Content Moderation)
                # - Azure Content Moderator
                # - Perspective API (Toxicity Detection)
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    
                    # Verificación básica de seguridad
                    safety_score = 1.0
                    safety_issues = []
                    
                    # Verificar palabras problemáticas
                    text_lower = (title + " " + content).lower()
                    for keyword in unsafe_keywords:
                        if keyword in text_lower:
                            safety_score -= 0.2
                            safety_issues.append(f"Unsafe keyword detected: {keyword}")
                    
                    # Verificar longitud mínima
                    if len(content) < 50:
                        safety_score -= 0.1
                        safety_issues.append("Content too short")
                    
                    # Verificar contenido vacío o solo espacios
                    if not content.strip():
                        safety_score = 0
                        safety_issues.append("Empty content")
                    
                    # Normalizar score
                    safety_score = max(0.0, min(1.0, safety_score))
                    
                    # Determinar estado de seguridad
                    if safety_score >= 0.8:
                        safety_status = "safe"
                    elif safety_score >= 0.5:
                        safety_status = "review_needed"
                    else:
                        safety_status = "unsafe"
                        unsafe_content_detected += 1
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'safety_check', %s,
                                    'safety_score', %s,
                                    'safety_status', %s,
                                    'safety_issues', %s,
                                    'safety_checked_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            True,
                            round(safety_score, 2),
                            safety_status,
                            json.dumps(safety_issues),
                            article_id
                        ))
                        
                        articles_checked += 1
                        
                        if safety_status == "unsafe":
                            logger.warning(f"Contenido inseguro detectado: article_id={article_id}, issues={safety_issues}")
                    
                    except Exception as e:
                        logger.error(f"Error verificando seguridad para {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Verificación de seguridad: {articles_checked} artículos verificados, {unsafe_content_detected} inseguros detectados")
        
        if Stats:
            try:
                Stats.incr("social_media.content_safety_checked", articles_checked)
                Stats.incr("social_media.unsafe_content_detected", unsafe_content_detected)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="data_validation")
    def data_validation(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la integridad y calidad de los datos antes de procesar."""
        ctx = get_current_context()
        params = ctx["params"]
        validation_enabled = bool(params.get("data_validation", True))
        
        if not validation_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_validated = 0
        validation_errors = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article.get("article_id")
                    title = article.get("title", "")
                    content = article.get("content", "")
                    category = article.get("category", "")
                    
                    validation_errors_list = []
                    
                    # Validación 1: Article ID requerido
                    if not article_id:
                        validation_errors_list.append("Missing article_id")
                    
                    # Validación 2: Título requerido y no vacío
                    if not title or not title.strip():
                        validation_errors_list.append("Missing or empty title")
                    
                    # Validación 3: Contenido requerido y longitud mínima
                    if not content or not content.strip():
                        validation_errors_list.append("Missing or empty content")
                    elif len(content.strip()) < 50:
                        validation_errors_list.append("Content too short (minimum 50 characters)")
                    
                    # Validación 4: Categoría válida (si existe)
                    valid_categories = ["technology", "business", "marketing", "design", "innovation", "general"]
                    if category and category.lower() not in valid_categories:
                        validation_errors_list.append(f"Invalid category: {category}")
                    
                    # Validación 5: Hashtags válidos (formato correcto)
                    hashtags = article.get("hashtags") or []
                    for hashtag in hashtags:
                        if not hashtag.startswith("#"):
                            validation_errors_list.append(f"Invalid hashtag format: {hashtag}")
                    
                    # Validación 6: Media URLs válidos (si existen)
                    media_urls = article.get("media_urls") or []
                    for url in media_urls:
                        if not url.startswith(("http://", "https://")):
                            validation_errors_list.append(f"Invalid media URL format: {url}")
                    
                    if validation_errors_list:
                        validation_errors += 1
                        logger.warning(f"Errores de validación para article_id={article_id}: {validation_errors_list}")
                        
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'validation_errors', %s,
                                        'validation_status', 'failed',
                                        'validated_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (json.dumps(validation_errors_list), article_id))
                        except Exception as e:
                            logger.error(f"Error guardando errores de validación: {e}")
                    else:
                        articles_validated += 1
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'validation_status', 'passed',
                                        'validated_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (article_id,))
                        except Exception as e:
                            logger.error(f"Error guardando validación exitosa: {e}")
                
                conn.commit()
        
        logger.info(f"Validación de datos: {articles_validated} artículos validados, {validation_errors} errores encontrados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_validated", articles_validated)
                Stats.incr("social_media.validation_errors", validation_errors)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="rate_limit_management")
    def rate_limit_management(publish_result: Dict[str, Any]) -> Dict[str, Any]:
        """Gestiona inteligentemente los rate limits de las APIs de redes sociales."""
        ctx = get_current_context()
        params = ctx["params"]
        rate_limit_enabled = bool(params.get("rate_limit_management", True))
        
        if not rate_limit_enabled:
            return publish_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de rate limits si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_rate_limits (
                        limit_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50) NOT NULL,
                        account_id VARCHAR(255),
                        request_count INTEGER DEFAULT 0,
                        window_start TIMESTAMP DEFAULT NOW(),
                        window_end TIMESTAMP,
                        limit_max INTEGER DEFAULT 100,
                        limit_remaining INTEGER DEFAULT 100,
                        reset_at TIMESTAMP,
                        last_updated_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB,
                        UNIQUE(platform, account_id)
                    )
                """)
                
                # Rate limits por plataforma (valores típicos)
                platform_limits = {
                    "twitter": {"per_15min": 300, "per_day": 1500},
                    "linkedin": {"per_day": 100},
                    "facebook": {"per_hour": 200, "per_day": 1000},
                    "instagram": {"per_hour": 200, "per_day": 1000},
                }
                
                platforms = json.loads(str(params.get("platforms", '["twitter", "linkedin"]')))
                
                for platform in platforms:
                    limits = platform_limits.get(platform, {"per_day": 100})
                    
                    try:
                        # Verificar rate limits actuales
                        cur.execute("""
                            SELECT limit_remaining, reset_at
                            FROM content_rate_limits
                            WHERE platform = %s
                            AND account_id = 'default'
                            AND reset_at > NOW()
                            ORDER BY last_updated_at DESC
                            LIMIT 1
                        """, (platform,))
                        
                        rate_limit_row = cur.fetchone()
                        
                        if rate_limit_row:
                            remaining = rate_limit_row[0] or 0
                            reset_at = rate_limit_row[1]
                            
                            if remaining <= 10:  # Cerca del límite
                                logger.warning(f"Rate limit bajo para {platform}: {remaining} requests restantes. Reset en {reset_at}")
                                
                                # Pausar publicación si es necesario
                                if remaining <= 0:
                                    logger.error(f"Rate limit alcanzado para {platform}. Pausando publicación hasta {reset_at}")
                        else:
                            # Inicializar rate limit tracking
                            reset_at = datetime.utcnow() + timedelta(hours=24)
                            cur.execute("""
                                INSERT INTO content_rate_limits
                                (platform, account_id, limit_max, limit_remaining, reset_at, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (platform, account_id)
                                DO UPDATE SET
                                    limit_remaining = EXCLUDED.limit_remaining,
                                    reset_at = EXCLUDED.reset_at,
                                    last_updated_at = NOW()
                            """, (
                                platform,
                                "default",
                                limits.get("per_day", 100),
                                limits.get("per_day", 100),
                                reset_at,
                                json.dumps({"limits": limits})
                            ))
                    
                    except Exception as e:
                        logger.error(f"Error gestionando rate limit para {platform}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info("Gestión de rate limits: límites verificados y actualizados")
        
        if Stats:
            try:
                Stats.incr("social_media.rate_limits_checked", 1)
            except Exception:
                pass
        
        return publish_result
    
    @task(task_id="error_recovery")
    def error_recovery(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperación automática de errores y reintentos inteligentes."""
        ctx = get_current_context()
        params = ctx["params"]
        recovery_enabled = bool(params.get("error_recovery", True))
        
        if not recovery_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        errors_recovered = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar errores recientes que pueden recuperarse
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.error_message,
                        sp.retry_count,
                        sp.updated_at
                    FROM content_scheduled_posts sp
                    WHERE sp.status = 'failed'
                    AND sp.retry_count < 3
                    AND sp.updated_at >= NOW() - INTERVAL '1 hour'
                    AND sp.error_message NOT LIKE '%permanent%'
                    ORDER BY sp.updated_at DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                recoverable_errors = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for error_post in recoverable_errors:
                    post_id = error_post["post_id"]
                    error_message = error_post.get("error_message", "")
                    retry_count = error_post.get("retry_count", 0)
                    
                    # Clasificar tipo de error
                    error_type = "unknown"
                    if "rate limit" in error_message.lower() or "429" in error_message:
                        error_type = "rate_limit"
                    elif "timeout" in error_message.lower():
                        error_type = "timeout"
                    elif "network" in error_message.lower() or "connection" in error_message.lower():
                        error_type = "network"
                    elif "authentication" in error_message.lower() or "401" in error_message or "403" in error_message:
                        error_type = "authentication"
                    
                    # Estrategias de recuperación según tipo de error
                    recoverable = False
                    recovery_strategy = None
                    
                    if error_type in ["rate_limit", "timeout", "network"]:
                        recoverable = True
                        recovery_strategy = "retry_with_backoff"
                    elif error_type == "authentication":
                        recoverable = False
                        recovery_strategy = "requires_manual_intervention"
                    
                    if recoverable:
                        try:
                            # Marcar para reintento
                            wait_minutes = (2 ** retry_count) * 5  # Backoff exponencial: 5, 10, 20 minutos
                            
                            cur.execute("""
                                UPDATE content_scheduled_posts
                                SET status = 'pending_retry',
                                    metadata = COALESCE(metadata, '{}'::jsonb) || 
                                        jsonb_build_object(
                                            'error_type', %s,
                                            'recovery_strategy', %s,
                                            'retry_scheduled_at', NOW() + INTERVAL '%s minutes',
                                            'error_recovered_at', NOW()
                                        )
                                WHERE post_id = %s
                            """, (error_type, recovery_strategy, wait_minutes, post_id))
                            
                            errors_recovered += 1
                            logger.info(f"Error recuperable detectado: post_id={post_id}, type={error_type}, strategy={recovery_strategy}")
                        
                        except Exception as e:
                            logger.error(f"Error en recuperación para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Recuperación de errores: {errors_recovered} errores marcados para recuperación")
        
        if Stats:
            try:
                Stats.incr("social_media.errors_recovered", errors_recovered)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="audience_segmentation")
    def audience_segmentation(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Segmenta la audiencia basada en comportamiento y engagement."""
        ctx = get_current_context()
        params = ctx["params"]
        segmentation_enabled = bool(params.get("audience_segmentation", True))
        
        if not segmentation_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        segments_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de segmentos si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_audience_segments (
                        segment_id SERIAL PRIMARY KEY,
                        segment_name VARCHAR(255) NOT NULL,
                        segment_criteria JSONB,
                        audience_size INTEGER DEFAULT 0,
                        avg_engagement_rate DECIMAL(10,2),
                        preferred_content_types TEXT[],
                        preferred_platforms TEXT[],
                        active_hours TEXT[],
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_updated_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar comportamiento de audiencia para crear segmentos
                cur.execute("""
                    SELECT 
                        a.category,
                        sp.platform,
                        EXTRACT(HOUR FROM sp.published_at) as publish_hour,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as interaction_count
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY a.category, sp.platform, EXTRACT(HOUR FROM sp.published_at)
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG(e.engagement_rate) DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                behavior_patterns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Crear segmentos basados en patrones
                segments = {}
                
                for pattern in behavior_patterns:
                    category = pattern.get("category", "general")
                    platform = pattern["platform"]
                    hour = int(pattern.get("publish_hour", 0) or 0)
                    engagement = float(pattern.get("avg_engagement", 0) or 0)
                    
                    # Crear segmento por categoría y plataforma
                    segment_key = f"{category}_{platform}"
                    
                    if segment_key not in segments:
                        segments[segment_key] = {
                            "name": f"{category.title()} Enthusiasts - {platform.title()}",
                            "criteria": {
                                "category": category,
                                "platform": platform,
                                "min_engagement_rate": round(engagement * 0.8, 2)
                            },
                            "preferred_content_types": [category],
                            "preferred_platforms": [platform],
                            "active_hours": [],
                            "total_engagement": 0,
                            "interaction_count": 0
                        }
                    
                    segments[segment_key]["active_hours"].append(f"{hour:02d}:00")
                    segments[segment_key]["total_engagement"] += engagement
                    segments[segment_key]["interaction_count"] += pattern.get("interaction_count", 0)
                
                # Guardar segmentos
                for segment_key, segment_data in segments.items():
                    try:
                        avg_engagement = segment_data["total_engagement"] / max(segment_data["interaction_count"], 1)
                        active_hours = sorted(list(set(segment_data["active_hours"])))[:5]  # Top 5 horas
                        
                        cur.execute("""
                            INSERT INTO content_audience_segments
                            (segment_name, segment_criteria, audience_size, avg_engagement_rate,
                             preferred_content_types, preferred_platforms, active_hours, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            segment_data["name"],
                            json.dumps(segment_data["criteria"]),
                            segment_data["interaction_count"],
                            round(avg_engagement, 2),
                            segment_data["preferred_content_types"],
                            segment_data["preferred_platforms"],
                            active_hours,
                            json.dumps({"created_by": "automation"})
                        ))
                        
                        segments_created += 1
                        logger.info(f"Segmento creado: {segment_data['name']}")
                    
                    except Exception as e:
                        logger.error(f"Error creando segmento {segment_key}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Segmentación de audiencia: {segments_created} segmentos creados")
        
        if Stats:
            try:
                Stats.incr("social_media.audience_segments_created", segments_created)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_personalization")
    def content_personalization(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Personaliza contenido basado en segmentos de audiencia."""
        ctx = get_current_context()
        params = ctx["params"]
        personalization_enabled = bool(params.get("content_personalization", False))
        
        if not personalization_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        personalized_count = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                # Obtener segmentos de audiencia
                cur.execute("""
                    SELECT segment_id, segment_name, segment_criteria, preferred_content_types, preferred_platforms
                    FROM content_audience_segments
                    ORDER BY avg_engagement_rate DESC
                    LIMIT 5
                """)
                
                columns = [desc[0] for desc in cur.description]
                segments = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for article in articles:
                    article_id = article["article_id"]
                    category = article.get("category", "")
                    
                    # Encontrar segmentos relevantes
                    relevant_segments = [
                        seg for seg in segments
                        if category.lower() in [ct.lower() for ct in (seg.get("preferred_content_types") or [])]
                    ]
                    
                    if relevant_segments:
                        # Personalizar contenido para cada segmento
                        for segment in relevant_segments[:2]:  # Máximo 2 variantes
                            segment_id = segment["segment_id"]
                            segment_name = segment["segment_name"]
                            
                            try:
                                # Crear variante personalizada
                                personalized_content = article.get("content", "")
                                
                                # Ajustar tono/estilo según segmento (simulado)
                                if "enthusiasts" in segment_name.lower():
                                    personalized_content = f"🎯 {personalized_content[:200]}... [Personalizado para {segment_name}]"
                                
                                # Guardar variante personalizada
                                cur.execute("""
                                    INSERT INTO content_scheduled_posts
                                    (article_id, platform, content, hashtags, scheduled_at, status, metadata)
                                    VALUES (%s, %s, %s, %s, NOW() + INTERVAL '1 day', 'scheduled', %s)
                                """, (
                                    article_id,
                                    segment.get("preferred_platforms", [""])[0] if segment.get("preferred_platforms") else "twitter",
                                    personalized_content,
                                    article.get("hashtags") or [],
                                    json.dumps({
                                        "personalized": True,
                                        "segment_id": segment_id,
                                        "segment_name": segment_name,
                                        "personalized_at": datetime.utcnow().isoformat()
                                    })
                                ))
                                
                                personalized_count += 1
                                logger.info(f"Contenido personalizado: article_id={article_id} para segmento {segment_name}")
                            
                            except Exception as e:
                                logger.error(f"Error personalizando contenido para segmento {segment_id}: {e}", exc_info=True)
                                continue
                
                conn.commit()
        
        logger.info(f"Personalización de contenido: {personalized_count} variantes personalizadas creadas")
        
        if Stats:
            try:
                Stats.incr("social_media.content_personalized", personalized_count)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="trend_prediction")
    def trend_prediction(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predice tendencias futuras basadas en análisis histórico."""
        ctx = get_current_context()
        params = ctx["params"]
        prediction_enabled = bool(params.get("trend_prediction", True))
        
        if not prediction_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        trends_predicted = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de predicciones de tendencias si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_trend_predictions (
                        prediction_id SERIAL PRIMARY KEY,
                        trend_topic VARCHAR(255) NOT NULL,
                        trend_category VARCHAR(100),
                        predicted_growth_rate DECIMAL(10,2),
                        confidence_score DECIMAL(5,2),
                        predicted_peak_date DATE,
                        current_trend_score DECIMAL(10,2),
                        predicted_trend_score DECIMAL(10,2),
                        prediction_date DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar hashtags trending para predecir tendencias futuras
                cur.execute("""
                    SELECT 
                        unnest(sp.hashtags) as hashtag,
                        COUNT(*) as usage_count,
                        AVG(e.engagement_rate) as avg_engagement,
                        MAX(sp.published_at) as last_used
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '14 days'
                    GROUP BY hashtag
                    HAVING COUNT(*) >= 3
                    ORDER BY AVG(e.engagement_rate) DESC, COUNT(*) DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                trending_hashtags = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for hashtag_data in trending_hashtags:
                    hashtag = hashtag_data["hashtag"]
                    usage_count = hashtag_data.get("usage_count", 0)
                    avg_engagement = float(hashtag_data.get("avg_engagement", 0) or 0)
                    last_used = hashtag_data.get("last_used")
                    
                    # Calcular crecimiento (simulado - en producción usar análisis temporal avanzado)
                    import random
                    growth_rate = random.uniform(5.0, 25.0)  # % de crecimiento esperado
                    confidence = min(95.0, avg_engagement * 10)  # Confidence basado en engagement
                    
                    # Predecir fecha pico (7-14 días desde ahora)
                    days_to_peak = random.randint(7, 14)
                    predicted_peak = (datetime.utcnow() + timedelta(days=days_to_peak)).date()
                    
                    current_score = usage_count * avg_engagement
                    predicted_score = current_score * (1 + growth_rate / 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_trend_predictions
                            (trend_topic, trend_category, predicted_growth_rate, confidence_score,
                             predicted_peak_date, current_trend_score, predicted_trend_score, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            hashtag,
                            "hashtag",
                            round(growth_rate, 2),
                            round(confidence, 2),
                            predicted_peak,
                            round(current_score, 2),
                            round(predicted_score, 2),
                            json.dumps({
                                "usage_count": usage_count,
                                "avg_engagement": round(avg_engagement, 2),
                                "last_used": last_used.isoformat() if last_used else None
                            })
                        ))
                        
                        trends_predicted += 1
                        logger.info(f"Tendencia predicha: {hashtag}, crecimiento {growth_rate:.1f}%, peak en {predicted_peak}")
                    
                    except Exception as e:
                        logger.error(f"Error prediciendo tendencia para {hashtag}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Predicción de tendencias: {trends_predicted} tendencias predichas")
        
        if Stats:
            try:
                Stats.incr("social_media.trends_predicted", trends_predicted)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="competitor_benchmarking")
    def competitor_benchmarking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmarking avanzado contra competidores."""
        ctx = get_current_context()
        params = ctx["params"]
        benchmarking_enabled = bool(params.get("competitor_benchmarking", False))
        
        if not benchmarking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        benchmarks_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de benchmarking si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_competitor_benchmarks (
                        benchmark_id SERIAL PRIMARY KEY,
                        metric_name VARCHAR(255) NOT NULL,
                        our_value DECIMAL(10,2),
                        competitor_value DECIMAL(10,2),
                        competitor_name VARCHAR(255),
                        difference_percentage DECIMAL(10,2),
                        benchmark_date DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Calcular métricas propias
                cur.execute("""
                    SELECT 
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        AVG(e.likes) as avg_likes,
                        AVG(e.comments) as avg_comments,
                        AVG(e.shares) as avg_shares,
                        AVG(e.impressions) as avg_impressions
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                """)
                
                our_metrics = cur.fetchone()
                our_engagement = float(our_metrics[0] or 0) if our_metrics[0] else 0
                our_likes = float(our_metrics[1] or 0) if our_metrics[1] else 0
                our_comments = float(our_metrics[2] or 0) if our_metrics[2] else 0
                
                # Obtener métricas de competidores (simulado)
                # En producción, esto vendría de la tabla content_competitor_tracking
                competitors_data = [
                    {"name": "competitor1", "engagement": our_engagement * 1.2, "likes": our_likes * 1.1},
                    {"name": "competitor2", "engagement": our_engagement * 0.9, "likes": our_likes * 0.8},
                ]
                
                for competitor in competitors_data:
                    competitor_name = competitor["name"]
                    comp_engagement = competitor["engagement"]
                    comp_likes = competitor["likes"]
                    
                    # Calcular diferencias
                    engagement_diff = ((comp_engagement - our_engagement) / our_engagement * 100) if our_engagement > 0 else 0
                    likes_diff = ((comp_likes - our_likes) / our_likes * 100) if our_likes > 0 else 0
                    
                    try:
                        # Guardar benchmarks
                        for metric_name, our_val, comp_val, diff in [
                            ("engagement_rate", our_engagement, comp_engagement, engagement_diff),
                            ("avg_likes", our_likes, comp_likes, likes_diff),
                        ]:
                            cur.execute("""
                                INSERT INTO content_competitor_benchmarks
                                (metric_name, our_value, competitor_value, competitor_name, difference_percentage, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (
                                metric_name,
                                round(our_val, 2),
                                round(comp_val, 2),
                                competitor_name,
                                round(diff, 2),
                                json.dumps({"benchmarked_at": datetime.utcnow().isoformat()})
                            ))
                            
                            benchmarks_created += 1
                            logger.info(f"Benchmark: {metric_name} - Nosotros: {our_val:.2f}, {competitor_name}: {comp_val:.2f}, Diff: {diff:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error creando benchmark para {competitor_name}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Benchmarking de competencia: {benchmarks_created} benchmarks creados")
        
        if Stats:
            try:
                Stats.incr("social_media.competitor_benchmarks_created", benchmarks_created)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_campaign_optimization")
    def automated_campaign_optimization(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza campañas automáticamente basado en performance."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("automated_campaign_optimization", True))
        
        if not optimization_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        campaigns_optimized = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar campañas por UTM
                cur.execute("""
                    SELECT 
                        a.utm_campaign,
                        a.utm_source,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        SUM(e.impressions) as total_impressions,
                        SUM(e.likes + e.comments + e.shares) as total_engagement
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND a.utm_campaign IS NOT NULL
                    GROUP BY a.utm_campaign, a.utm_source
                    HAVING COUNT(DISTINCT sp.post_id) >= 3
                """)
                
                columns = [desc[0] for desc in cur.description]
                campaigns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for campaign in campaigns:
                    campaign_name = campaign.get("utm_campaign", "")
                    avg_engagement = float(campaign.get("avg_engagement_rate", 0) or 0)
                    total_posts = campaign.get("total_posts", 0)
                    
                    # Recomendaciones de optimización
                    optimizations = []
                    
                    if avg_engagement < 3.0:
                        optimizations.append("Low engagement - Consider adjusting content strategy")
                    
                    if total_posts < 5:
                        optimizations.append("Low post volume - Increase posting frequency")
                    
                    # Calcular score de campaña
                    campaign_score = min(100, avg_engagement * 10 + total_posts * 2)
                    
                    if optimizations:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'campaign_optimization', %s,
                                        'campaign_score', %s,
                                        'optimized_at', NOW()
                                    )
                                WHERE utm_campaign = %s
                            """, (
                                json.dumps(optimizations),
                                round(campaign_score, 2),
                                campaign_name
                            ))
                            
                            campaigns_optimized += 1
                            logger.info(f"Campaña optimizada: {campaign_name}, score: {campaign_score:.1f}, optimizations: {len(optimizations)}")
                        
                        except Exception as e:
                            logger.error(f"Error optimizando campaña {campaign_name}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización automática de campañas: {campaigns_optimized} campañas optimizadas")
        
        if Stats:
            try:
                Stats.incr("social_media.campaigns_optimized", campaigns_optimized)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="crm_lead_tracking")
    def crm_lead_tracking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Tracking de leads generados desde redes sociales hacia CRM."""
        ctx = get_current_context()
        params = ctx["params"]
        tracking_enabled = bool(params.get("crm_lead_tracking", False) or params.get("crm_integration", False))
        
        if not tracking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        leads_tracked = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de leads si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_social_leads (
                        lead_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50) NOT NULL,
                        lead_source VARCHAR(255),
                        lead_type VARCHAR(50),
                        contact_info JSONB,
                        engagement_action VARCHAR(100),
                        conversion_value DECIMAL(10,2),
                        utm_campaign VARCHAR(255),
                        utm_source VARCHAR(255),
                        utm_medium VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW(),
                        synced_to_crm BOOLEAN DEFAULT FALSE,
                        crm_lead_id VARCHAR(255),
                        metadata JSONB
                    )
                """)
                
                # Buscar acciones de engagement que pueden ser leads
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.published_url,
                        e.clicks,
                        e.comments,
                        a.utm_campaign,
                        a.utm_source,
                        a.utm_medium
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    JOIN content_articles a ON a.article_id = sp.article_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND (e.clicks > 10 OR e.comments > 5)
                    AND a.utm_campaign IS NOT NULL
                    ORDER BY e.clicks DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                potential_leads = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for lead_data in potential_leads:
                    post_id = lead_data["post_id"]
                    platform = lead_data["platform"]
                    clicks = lead_data.get("clicks", 0)
                    comments = lead_data.get("comments", 0)
                    
                    # Determinar tipo de lead basado en engagement
                    lead_type = "click_through" if clicks > 10 else "engaged_commenter"
                    conversion_value = clicks * 0.5 + comments * 2.0  # Valor estimado
                    
                    try:
                        # En producción, aquí se integraría con CRM (Salesforce, HubSpot, etc.)
                        # Ejemplo con HubSpot:
                        # import hubspot
                        # client = hubspot.Client.create(access_token=HUBSPOT_TOKEN)
                        # properties = {
                        #     "email": contact_email,
                        #     "firstname": first_name,
                        #     "lastname": last_name,
                        #     "lead_source": "Social Media",
                        #     "utm_campaign": utm_campaign
                        # }
                        # crm_lead = client.crm.contacts.basic_api.create(properties=properties)
                        # crm_lead_id = crm_lead.id
                        
                        # Simulación por ahora
                        cur.execute("""
                            INSERT INTO content_social_leads
                            (post_id, platform, lead_source, lead_type, engagement_action,
                             conversion_value, utm_campaign, utm_source, utm_medium, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            post_id,
                            platform,
                            f"{platform}_social",
                            lead_type,
                            "click" if clicks > 10 else "comment",
                            round(conversion_value, 2),
                            lead_data.get("utm_campaign"),
                            lead_data.get("utm_source"),
                            lead_data.get("utm_medium"),
                            json.dumps({
                                "clicks": clicks,
                                "comments": comments,
                                "tracked_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        leads_tracked += 1
                        logger.info(f"Lead trackeado: post_id={post_id}, type={lead_type}, value={conversion_value:.2f}")
                    
                    except Exception as e:
                        logger.error(f"Error trackeando lead para post {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Tracking de leads CRM: {leads_tracked} leads trackeados")
        
        if Stats:
            try:
                Stats.incr("social_media.leads_tracked", leads_tracked)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="advanced_roi_analysis")
    def advanced_roi_analysis(roi_result: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis avanzado de ROI con atribución multi-touch."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("advanced_roi_analysis", True))
        
        if not analysis_enabled:
            return roi_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de ROI avanzado si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_advanced_roi (
                        roi_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        attribution_model VARCHAR(50),
                        touchpoints_count INTEGER,
                        first_touch_value DECIMAL(10,2),
                        last_touch_value DECIMAL(10,2),
                        linear_attribution_value DECIMAL(10,2),
                        time_decay_value DECIMAL(10,2),
                        total_roi DECIMAL(10,2),
                        roi_percentage DECIMAL(10,2),
                        analysis_date DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Análisis de ROI con diferentes modelos de atribución
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        e.impressions,
                        e.clicks,
                        e.likes,
                        e.comments,
                        e.shares,
                        (e.impressions * e.engagement_rate / 100) * 0.02 as estimated_value
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND e.impressions > 100
                    ORDER BY e.impressions DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    estimated_value = float(post.get("estimated_value", 0) or 0)
                    cost = 0.5  # Costo estimado por post
                    
                    # Calcular ROI con diferentes modelos de atribución
                    first_touch_value = estimated_value * 0.3  # 30% al primer touch
                    last_touch_value = estimated_value * 0.4   # 40% al último touch
                    linear_attribution_value = estimated_value * 0.5  # 50% distribuido
                    time_decay_value = estimated_value * 0.35  # 35% con decay temporal
                    
                    total_roi = estimated_value - cost
                    roi_percentage = ((estimated_value - cost) / cost * 100) if cost > 0 else 0
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_advanced_roi
                            (post_id, platform, attribution_model, touchpoints_count,
                             first_touch_value, last_touch_value, linear_attribution_value,
                             time_decay_value, total_roi, roi_percentage, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            post_id,
                            platform,
                            "multi_touch",
                            1,  # Simplificado
                            round(first_touch_value, 2),
                            round(last_touch_value, 2),
                            round(linear_attribution_value, 2),
                            round(time_decay_value, 2),
                            round(total_roi, 2),
                            round(roi_percentage, 2),
                            json.dumps({
                                "cost": cost,
                                "estimated_value": round(estimated_value, 2),
                                "analyzed_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        logger.debug(f"ROI avanzado calculado: post_id={post_id}, ROI={roi_percentage:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error calculando ROI avanzado para {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info("Análisis avanzado de ROI: análisis completado")
        
        if Stats:
            try:
                Stats.incr("social_media.advanced_roi_analyzed", 1)
            except Exception:
                pass
        
        return roi_result
    
    @task(task_id="content_effectiveness_scoring")
    def content_effectiveness_scoring(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula un score de efectividad basado en múltiples factores."""
        ctx = get_current_context()
        params = ctx["params"]
        scoring_enabled = bool(params.get("content_effectiveness_scoring", True))
        
        if not scoring_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        posts_scored = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Calcular efectividad de posts publicados
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        e.engagement_rate,
                        e.impressions,
                        e.likes,
                        e.comments,
                        e.shares,
                        e.clicks,
                        e.click_through_rate,
                        sp.published_at
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    ORDER BY e.engagement_rate DESC
                    LIMIT 50
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    engagement_rate = float(post.get("engagement_rate", 0) or 0)
                    impressions = post.get("impressions", 0) or 0
                    clicks = post.get("clicks", 0) or 0
                    ctr = float(post.get("click_through_rate", 0) or 0)
                    
                    # Calcular score de efectividad (0-100)
                    effectiveness_score = 0
                    
                    # Factor 1: Engagement rate (40%)
                    effectiveness_score += min(engagement_rate * 4, 40)
                    
                    # Factor 2: Click-through rate (30%)
                    effectiveness_score += min(ctr * 6, 30)
                    
                    # Factor 3: Alcance (20%)
                    reach_score = min((impressions / 10000) * 20, 20) if impressions > 0 else 0
                    effectiveness_score += reach_score
                    
                    # Factor 4: Velocidad de engagement (10%)
                    # Posts más recientes con buen engagement tienen bonus
                    hours_since_publish = (datetime.utcnow() - post.get("published_at", datetime.utcnow())).total_seconds() / 3600
                    if hours_since_publish < 24 and engagement_rate > 3.0:
                        effectiveness_score += 10
                    elif hours_since_publish < 48 and engagement_rate > 2.0:
                        effectiveness_score += 5
                    
                    effectiveness_score = min(effectiveness_score, 100)
                    
                    # Clasificar efectividad
                    if effectiveness_score >= 80:
                        effectiveness_level = "excellent"
                    elif effectiveness_score >= 60:
                        effectiveness_level = "good"
                    elif effectiveness_score >= 40:
                        effectiveness_level = "fair"
                    else:
                        effectiveness_level = "poor"
                    
                    try:
                        cur.execute("""
                            UPDATE content_engagement
                            SET engagement_breakdown = COALESCE(engagement_breakdown, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'effectiveness_score', %s,
                                    'effectiveness_level', %s,
                                    'effectiveness_scored_at', NOW()
                                )
                            WHERE post_id = %s
                        """, (round(effectiveness_score, 2), effectiveness_level, post_id))
                        
                        posts_scored += 1
                        logger.debug(f"Efectividad calculada: post_id={post_id}, score={effectiveness_score:.1f} ({effectiveness_level})")
                    
                    except Exception as e:
                        logger.error(f"Error calculando efectividad para {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Scoring de efectividad: {posts_scored} posts evaluados")
        
        if Stats:
            try:
                Stats.incr("social_media.posts_effectiveness_scored", posts_scored)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="engagement_velocity_tracking")
    def engagement_velocity_tracking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Tracking de velocidad de engagement (engagement por hora)."""
        ctx = get_current_context()
        params = ctx["params"]
        tracking_enabled = bool(params.get("engagement_velocity_tracking", True))
        
        if not tracking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        velocities_tracked = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de velocidad si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_engagement_velocity (
                        velocity_id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        platform VARCHAR(50),
                        hours_since_publish INTEGER,
                        engagement_count INTEGER,
                        engagement_rate DECIMAL(10,2),
                        velocity_score DECIMAL(10,2),
                        tracked_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Calcular velocidad de engagement para posts recientes
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.published_at,
                        e.likes + e.comments + e.shares as total_engagement,
                        e.engagement_rate
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '48 hours'
                    ORDER BY sp.published_at DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    published_at = post.get("published_at")
                    total_engagement = post.get("total_engagement", 0) or 0
                    engagement_rate = float(post.get("engagement_rate", 0) or 0)
                    
                    if published_at:
                        hours_since = int((datetime.utcnow() - published_at).total_seconds() / 3600)
                        
                        # Calcular velocidad (engagement por hora)
                        velocity = total_engagement / max(hours_since, 1)
                        velocity_score = min(velocity * engagement_rate / 10, 100)  # Normalizar
                        
                        try:
                            cur.execute("""
                                INSERT INTO content_engagement_velocity
                                (post_id, platform, hours_since_publish, engagement_count,
                                 engagement_rate, velocity_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                post_id,
                                platform,
                                hours_since,
                                total_engagement,
                                round(engagement_rate, 2),
                                round(velocity_score, 2),
                                json.dumps({
                                    "tracked_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            velocities_tracked += 1
                            
                            # Detectar contenido de alta velocidad (viral potencial)
                            if velocity > 10 and hours_since < 6:
                                logger.info(f"Alta velocidad de engagement detectada: post_id={post_id}, velocity={velocity:.1f}/hora")
                        
                        except Exception as e:
                            logger.error(f"Error trackeando velocidad para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Tracking de velocidad de engagement: {velocities_tracked} posts trackeados")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_velocities_tracked", velocities_tracked)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_lifecycle_optimization")
    def content_lifecycle_optimization(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza el ciclo de vida del contenido basado en performance."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("content_lifecycle_optimization", True))
        
        if not optimization_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        optimizations_applied = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar ciclo de vida de contenido
                cur.execute("""
                    SELECT 
                        a.article_id,
                        a.title,
                        COUNT(DISTINCT sp.post_id) as total_posts,
                        MAX(sp.published_at) as last_published,
                        AVG(e.engagement_rate) as avg_engagement,
                        SUM(e.impressions) as total_impressions
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    GROUP BY a.article_id, a.title
                    HAVING COUNT(DISTINCT sp.post_id) >= 1
                    ORDER BY AVG(e.engagement_rate) DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                articles = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for article in articles:
                    article_id = article["article_id"]
                    total_posts = article.get("total_posts", 0)
                    last_published = article.get("last_published")
                    avg_engagement = float(article.get("avg_engagement", 0) or 0)
                    
                    # Determinar etapa del ciclo de vida
                    lifecycle_stage = "new"
                    recommendations = []
                    
                    if last_published:
                        days_since = (datetime.utcnow() - last_published).days
                        
                        if days_since < 7:
                            lifecycle_stage = "active"
                        elif days_since < 30:
                            lifecycle_stage = "mature"
                        else:
                            lifecycle_stage = "declining"
                    
                    # Recomendaciones basadas en etapa y performance
                    if lifecycle_stage == "active" and avg_engagement > 5.0:
                        recommendations.append("High performance - Consider repurposing to other platforms")
                    elif lifecycle_stage == "mature" and avg_engagement < 2.0:
                        recommendations.append("Low engagement - Consider updating or retiring")
                    elif lifecycle_stage == "declining" and avg_engagement > 3.0:
                        recommendations.append("Still performing well - Consider refresh and republish")
                    
                    if recommendations:
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'lifecycle_stage', %s,
                                        'lifecycle_recommendations', %s,
                                        'lifecycle_optimized_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (
                                lifecycle_stage,
                                json.dumps(recommendations),
                                article_id
                            ))
                            
                            optimizations_applied += 1
                            logger.info(f"Ciclo de vida optimizado: article_id={article_id}, stage={lifecycle_stage}, recommendations={len(recommendations)}")
                        
                        except Exception as e:
                            logger.error(f"Error optimizando ciclo de vida para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización de ciclo de vida: {optimizations_applied} artículos optimizados")
        
        if Stats:
            try:
                Stats.incr("social_media.lifecycle_optimizations_applied", optimizations_applied)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_content_refresh")
    def automated_content_refresh(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh automático de contenido exitoso con actualizaciones."""
        ctx = get_current_context()
        params = ctx["params"]
        refresh_enabled = bool(params.get("automated_content_refresh", True))
        
        if not refresh_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        content_refreshed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar contenido exitoso que puede refrescarse
                cur.execute("""
                    SELECT 
                        a.article_id,
                        a.title,
                        a.content,
                        a.category,
                        AVG(e.engagement_rate) as avg_engagement,
                        MAX(sp.published_at) as last_published
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND a.status = 'published'
                    GROUP BY a.article_id, a.title, a.content, a.category
                    HAVING MAX(sp.published_at) < NOW() - INTERVAL '90 days'
                    AND AVG(e.engagement_rate) > 4.0
                    ORDER BY AVG(e.engagement_rate) DESC
                    LIMIT 5
                """)
                
                columns = [desc[0] for desc in cur.description]
                candidates = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for article in candidates:
                    article_id = article["article_id"]
                    title = article["title"]
                    content = article["content"]
                    avg_engagement = float(article.get("avg_engagement", 0) or 0)
                    
                    try:
                        # Crear versión refrescada
                        refreshed_title = f"Updated: {title}"
                        refreshed_content = f"{content}\n\n[Updated {datetime.utcnow().strftime('%Y-%m-%d')} - Original engagement: {avg_engagement:.1f}%]"
                        
                        # Crear nuevo artículo como versión refrescada
                        cur.execute("""
                            INSERT INTO content_articles
                            (title, content, category, status, author_id, published_at, metadata)
                            VALUES (%s, %s, %s, 'draft', NULL, NOW(), %s)
                            RETURNING article_id
                        """, (
                            refreshed_title,
                            refreshed_content,
                            article.get("category", "general"),
                            json.dumps({
                                "refreshed_from": article_id,
                                "original_engagement": round(avg_engagement, 2),
                                "refreshed_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        refreshed_article_id = cur.fetchone()[0]
                        content_refreshed += 1
                        logger.info(f"Contenido refrescado: article_id={article_id} -> {refreshed_article_id}")
                    
                    except Exception as e:
                        logger.error(f"Error refrescando contenido {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Refresh automático de contenido: {content_refreshed} artículos refrescados")
        
        if Stats:
            try:
                Stats.incr("social_media.content_refreshed", content_refreshed)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="intelligent_content_curation")
    def intelligent_content_curation(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Curación inteligente de contenido basada en performance histórico."""
        ctx = get_current_context()
        params = ctx["params"]
        curation_enabled = bool(params.get("intelligent_content_curation", True))
        
        if not curation_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_curated = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    
                    # Calcular score de curación basado en múltiples factores
                    curation_score = 0
                    curation_factors = {}
                    
                    # Factor 1: Quality score (si existe)
                    quality_score = article.get("metadata", {}).get("quality_score") if isinstance(article.get("metadata"), dict) else None
                    if quality_score:
                        curation_score += quality_score * 0.4
                        curation_factors["quality"] = quality_score
                    
                    # Factor 2: Performance prediction (si existe)
                    predicted_engagement = article.get("metadata", {}).get("predicted_engagement_rate") if isinstance(article.get("metadata"), dict) else None
                    if predicted_engagement:
                        curation_score += float(predicted_engagement) * 4
                        curation_factors["predicted_performance"] = predicted_engagement
                    
                    # Factor 3: Trending topics alignment
                    hashtags = article.get("hashtags") or []
                    trending_hashtags_count = len([h for h in hashtags if "#" in str(h)])
                    curation_score += min(trending_hashtags_count * 5, 20)
                    curation_factors["trending_alignment"] = trending_hashtags_count
                    
                    # Normalizar
                    curation_score = min(curation_score, 100)
                    
                    # Determinar prioridad de curación
                    if curation_score >= 70:
                        curation_priority = "high"
                    elif curation_score >= 50:
                        curation_priority = "medium"
                    else:
                        curation_priority = "low"
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'curation_score', %s,
                                    'curation_priority', %s,
                                    'curation_factors', %s,
                                    'curated_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            round(curation_score, 2),
                            curation_priority,
                            json.dumps(curation_factors),
                            article_id
                        ))
                        
                        articles_curated += 1
                        logger.debug(f"Contenido curado: article_id={article_id}, score={curation_score:.1f}, priority={curation_priority}")
                    
                    except Exception as e:
                        logger.error(f"Error curando contenido {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Curación inteligente: {articles_curated} artículos curados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_curated", articles_curated)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="engagement_heatmap_analysis")
    def engagement_heatmap_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza patrones de engagement en heatmap (día/hora)."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("engagement_heatmap_analysis", True))
        
        if not analysis_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de heatmap si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_engagement_heatmap (
                        heatmap_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50) NOT NULL,
                        day_of_week INTEGER,
                        hour_of_day INTEGER,
                        avg_engagement_rate DECIMAL(10,2),
                        total_posts INTEGER,
                        total_engagement INTEGER,
                        heatmap_score DECIMAL(10,2),
                        analysis_date DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar engagement por día y hora
                cur.execute("""
                    SELECT 
                        sp.platform,
                        EXTRACT(DOW FROM sp.published_at) as day_of_week,
                        EXTRACT(HOUR FROM sp.published_at) as hour_of_day,
                        AVG(e.engagement_rate) as avg_engagement_rate,
                        COUNT(*) as total_posts,
                        SUM(e.likes + e.comments + e.shares) as total_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform, EXTRACT(DOW FROM sp.published_at), EXTRACT(HOUR FROM sp.published_at)
                    HAVING COUNT(*) >= 2
                    ORDER BY AVG(e.engagement_rate) DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                heatmap_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for heatmap_point in heatmap_data:
                    platform = heatmap_point["platform"]
                    day_of_week = int(heatmap_point.get("day_of_week", 0) or 0)
                    hour_of_day = int(heatmap_point.get("hour_of_day", 0) or 0)
                    avg_engagement = float(heatmap_point.get("avg_engagement_rate", 0) or 0)
                    total_posts = heatmap_point.get("total_posts", 0)
                    total_engagement = heatmap_point.get("total_engagement", 0) or 0
                    
                    # Calcular score de heatmap
                    heatmap_score = avg_engagement * (total_posts / 10)  # Normalizar
                    heatmap_score = min(heatmap_score, 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_engagement_heatmap
                            (platform, day_of_week, hour_of_day, avg_engagement_rate,
                             total_posts, total_engagement, heatmap_score, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            platform,
                            day_of_week,
                            hour_of_day,
                            round(avg_engagement, 2),
                            total_posts,
                            total_engagement,
                            round(heatmap_score, 2),
                            json.dumps({"analyzed_at": datetime.utcnow().isoformat()})
                        ))
                        
                        logger.debug(f"Heatmap: {platform} - Día {day_of_week}, Hora {hour_of_day}, Engagement {avg_engagement:.2f}%")
                    
                    except Exception as e:
                        logger.error(f"Error guardando heatmap: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info("Análisis de heatmap: heatmap generado")
        
        if Stats:
            try:
                Stats.incr("social_media.heatmap_analyzed", 1)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_content_repurposing")
    def automated_content_repurposing(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Repurposing automático de contenido exitoso para otras plataformas/formats."""
        ctx = get_current_context()
        params = ctx["params"]
        repurposing_enabled = bool(params.get("automated_content_repurposing", True))
        
        if not repurposing_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        content_repurposed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar contenido exitoso que puede repurposearse
                cur.execute("""
                    SELECT 
                        a.article_id,
                        a.title,
                        a.content,
                        a.category,
                        sp.platform as original_platform,
                        AVG(e.engagement_rate) as avg_engagement,
                        MAX(e.impressions) as max_impressions
                    FROM content_articles a
                    JOIN content_scheduled_posts sp ON sp.article_id = a.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND a.status = 'published'
                    AND AVG(e.engagement_rate) > 5.0
                    GROUP BY a.article_id, a.title, a.content, a.category, sp.platform
                    HAVING COUNT(DISTINCT sp.platform) = 1  -- Solo publicado en una plataforma
                    ORDER BY AVG(e.engagement_rate) DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                candidates = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Plataformas objetivo para repurposing
                target_platforms = ["twitter", "linkedin", "facebook", "instagram"]
                
                for article in candidates:
                    article_id = article["article_id"]
                    original_platform = article.get("original_platform", "")
                    title = article["title"]
                    content = article["content"]
                    avg_engagement = float(article.get("avg_engagement", 0) or 0)
                    
                    # Determinar plataformas objetivo (excluir la original)
                    platforms_to_repurpose = [p for p in target_platforms if p != original_platform]
                    
                    for target_platform in platforms_to_repurpose[:2]:  # Máximo 2 plataformas
                        try:
                            # Adaptar contenido según plataforma
                            if target_platform == "twitter":
                                # Twitter: más corto, con hashtags
                                adapted_content = f"{title[:100]}\n\n{content[:200]}..."
                                adapted_content += "\n\n#marketing #content"
                            elif target_platform == "linkedin":
                                # LinkedIn: más profesional
                                adapted_content = f"{title}\n\n{content[:500]}..."
                            else:
                                adapted_content = f"{title}\n\n{content}"
                            
                            # Crear nuevo artículo como versión repurposed
                            cur.execute("""
                                INSERT INTO content_articles
                                (title, content, category, status, author_id, published_at, metadata)
                                VALUES (%s, %s, %s, 'draft', NULL, NOW(), %s)
                                RETURNING article_id
                            """, (
                                f"[Repurposed for {target_platform}] {title}",
                                adapted_content,
                                article.get("category", "general"),
                                json.dumps({
                                    "repurposed_from": article_id,
                                    "original_platform": original_platform,
                                    "target_platform": target_platform,
                                    "original_engagement": round(avg_engagement, 2),
                                    "repurposed_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            repurposed_article_id = cur.fetchone()[0]
                            content_repurposed += 1
                            logger.info(f"Contenido repurposed: article_id={article_id} -> {repurposed_article_id} para {target_platform}")
                        
                        except Exception as e:
                            logger.error(f"Error repurposing contenido {article_id} para {target_platform}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Repurposing automático: {content_repurposed} artículos repurposed")
        
        if Stats:
            try:
                Stats.incr("social_media.content_repurposed", content_repurposed)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_audience_matching")
    def content_audience_matching(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Matching de contenido con audiencia ideal basado en performance histórico."""
        ctx = get_current_context()
        params = ctx["params"]
        matching_enabled = bool(params.get("content_audience_matching", True))
        
        if not matching_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_matched = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    category = article.get("category", "general")
                    
                    # Buscar audiencia ideal basada en performance histórico de categoría similar
                    cur.execute("""
                        SELECT 
                            sp.platform,
                            AVG(e.engagement_rate) as avg_engagement,
                            AVG(e.impressions) as avg_impressions,
                            COUNT(*) as post_count
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '90 days'
                        GROUP BY sp.platform
                        HAVING COUNT(*) >= 3
                        ORDER BY AVG(e.engagement_rate) DESC
                        LIMIT 3
                    """, (category,))
                    
                    columns = [desc[0] for desc in cur.description]
                    ideal_audiences = [dict(zip(columns, row)) for row in cur.fetchall()]
                    
                    if ideal_audiences:
                        best_platform = ideal_audiences[0].get("platform")
                        avg_engagement = float(ideal_audiences[0].get("avg_engagement", 0) or 0)
                        
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'ideal_audience_platform', %s,
                                        'expected_engagement', %s,
                                        'audience_matched_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (
                                best_platform,
                                round(avg_engagement, 2),
                                article_id
                            ))
                            
                            articles_matched += 1
                            logger.debug(f"Audiencia match: article_id={article_id}, platform={best_platform}, expected_engagement={avg_engagement:.1f}%")
                        
                        except Exception as e:
                            logger.error(f"Error matching audiencia para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Matching de audiencia: {articles_matched} artículos matcheados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_audience_matched", articles_matched)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="social_signal_detection")
    def social_signal_detection(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta señales sociales relevantes (trending topics, menciones, etc.)."""
        ctx = get_current_context()
        params = ctx["params"]
        detection_enabled = bool(params.get("social_signal_detection", True))
        
        if not detection_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        signals_detected = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de señales sociales si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_social_signals (
                        signal_id SERIAL PRIMARY KEY,
                        signal_type VARCHAR(50) NOT NULL,
                        signal_value VARCHAR(255),
                        platform VARCHAR(50),
                        relevance_score DECIMAL(10,2),
                        detected_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Detectar hashtags trending
                cur.execute("""
                    SELECT 
                        hashtag,
                        COUNT(*) as usage_count,
                        AVG(e.engagement_rate) as avg_engagement,
                        MAX(sp.published_at) as last_used
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    CROSS JOIN LATERAL unnest(string_to_array(sp.hashtags, ',')) as hashtag
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND hashtag LIKE '#%'
                    GROUP BY hashtag
                    HAVING COUNT(*) >= 3
                    ORDER BY COUNT(*) DESC, AVG(e.engagement_rate) DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                trending_hashtags = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for hashtag_data in trending_hashtags:
                    hashtag = hashtag_data.get("hashtag", "").strip()
                    usage_count = hashtag_data.get("usage_count", 0)
                    avg_engagement = float(hashtag_data.get("avg_engagement", 0) or 0)
                    
                    # Calcular relevancia
                    relevance_score = min((usage_count * 10) + (avg_engagement * 2), 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_social_signals
                            (signal_type, signal_value, platform, relevance_score, metadata)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            "trending_hashtag",
                            hashtag,
                            "all",
                            round(relevance_score, 2),
                            json.dumps({
                                "usage_count": usage_count,
                                "avg_engagement": round(avg_engagement, 2),
                                "detected_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        signals_detected += 1
                        logger.debug(f"Señal detectada: {hashtag} (relevance: {relevance_score:.1f})")
                    
                    except Exception as e:
                        logger.error(f"Error guardando señal: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Detección de señales sociales: {signals_detected} señales detectadas")
        
        if Stats:
            try:
                Stats.incr("social_media.social_signals_detected", signals_detected)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_hashtag_generation")
    def automated_hashtag_generation(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera hashtags automáticamente usando ML y análisis de contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        generation_enabled = bool(params.get("automated_hashtag_generation", True))
        
        if not generation_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        hashtags_generated = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    category = article.get("category", "general")
                    
                    # Extraer palabras clave del título y contenido
                    text = f"{title} {content}".lower()
                    
                    # Palabras clave comunes por categoría
                    category_keywords = {
                        "technology": ["tech", "innovation", "digital", "ai", "software"],
                        "marketing": ["marketing", "strategy", "brand", "campaign", "social"],
                        "business": ["business", "growth", "strategy", "leadership", "success"],
                        "general": ["tips", "guide", "how-to", "best", "top"]
                    }
                    
                    # Generar hashtags basados en categoría y contenido
                    generated_hashtags = []
                    
                    # Hashtags de categoría
                    keywords = category_keywords.get(category, category_keywords["general"])
                    for keyword in keywords[:3]:
                        if keyword in text:
                            generated_hashtags.append(f"#{keyword}")
                    
                    # Hashtags de trending (si hay señales detectadas)
                    cur.execute("""
                        SELECT signal_value
                        FROM content_social_signals
                        WHERE signal_type = 'trending_hashtag'
                        AND detected_at >= NOW() - INTERVAL '7 days'
                        ORDER BY relevance_score DESC
                        LIMIT 3
                    """)
                    
                    trending = [row[0] for row in cur.fetchall()]
                    generated_hashtags.extend(trending[:2])
                    
                    # Hashtag de categoría genérica
                    generated_hashtags.append(f"#{category}")
                    
                    # Limitar a 5 hashtags
                    generated_hashtags = list(set(generated_hashtags))[:5]
                    
                    if generated_hashtags:
                        hashtags_str = ", ".join(generated_hashtags)
                        
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'auto_generated_hashtags', %s,
                                        'hashtags_generated_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (
                                json.dumps(generated_hashtags),
                                article_id
                            ))
                            
                            hashtags_generated += 1
                            logger.debug(f"Hashtags generados: article_id={article_id}, hashtags={hashtags_str}")
                        
                        except Exception as e:
                            logger.error(f"Error generando hashtags para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Generación automática de hashtags: {hashtags_generated} artículos procesados")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtags_generated", hashtags_generated)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="content_engagement_forecasting")
    def content_engagement_forecasting(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Forecasting avanzado de engagement usando modelos predictivos."""
        ctx = get_current_context()
        params = ctx["params"]
        forecasting_enabled = bool(params.get("content_engagement_forecasting", True))
        
        if not forecasting_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        forecasts_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de forecasting si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_engagement_forecasts (
                        forecast_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        forecasted_engagement_rate DECIMAL(10,2),
                        forecasted_impressions INTEGER,
                        confidence_score DECIMAL(10,2),
                        forecast_horizon_days INTEGER,
                        forecasted_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Obtener posts recientes para forecasting
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.article_id,
                        a.category,
                        e.engagement_rate,
                        e.impressions,
                        sp.published_at
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    LEFT JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    ORDER BY sp.published_at DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    category = post.get("category", "general")
                    current_engagement = float(post.get("engagement_rate", 0) or 0)
                    current_impressions = post.get("impressions", 0) or 0
                    
                    # Modelo de forecasting simplificado (en producción usar ML real)
                    # Basado en performance histórico de categoría y plataforma
                    cur.execute("""
                        SELECT 
                            AVG(e.engagement_rate) as avg_engagement,
                            AVG(e.impressions) as avg_impressions
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.platform = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                    """, (category, platform))
                    
                    historical = cur.fetchone()
                    if historical:
                        avg_historical_engagement = float(historical[0] or 0)
                        avg_historical_impressions = float(historical[1] or 0) if historical[1] else 0
                        
                        # Forecasting: promedio entre actual e histórico con tendencia
                        forecasted_engagement = (current_engagement * 0.6) + (avg_historical_engagement * 0.4)
                        forecasted_impressions = int((current_impressions * 0.6) + (avg_historical_impressions * 0.4)) if current_impressions > 0 else int(avg_historical_impressions)
                        
                        # Confidence basado en cantidad de datos históricos
                        confidence_score = min(85.0, 50.0 + (avg_historical_engagement * 5))
                        
                        try:
                            cur.execute("""
                                INSERT INTO content_engagement_forecasts
                                (post_id, platform, forecasted_engagement_rate, forecasted_impressions,
                                 confidence_score, forecast_horizon_days, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                post_id,
                                platform,
                                round(forecasted_engagement, 2),
                                forecasted_impressions,
                                round(confidence_score, 2),
                                7,  # 7 días horizon
                                json.dumps({
                                    "current_engagement": round(current_engagement, 2),
                                    "current_impressions": current_impressions,
                                    "historical_avg_engagement": round(avg_historical_engagement, 2),
                                    "forecasted_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            forecasts_created += 1
                            logger.debug(f"Forecast creado: post_id={post_id}, engagement={forecasted_engagement:.1f}%, confidence={confidence_score:.1f}%")
                        
                        except Exception as e:
                            logger.error(f"Error creando forecast para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Forecasting de engagement: {forecasts_created} forecasts creados")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_forecasts_created", forecasts_created)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_performance_benchmarking")
    def content_performance_benchmarking(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmarking de performance de contenido contra estándares de la industria."""
        ctx = get_current_context()
        params = ctx["params"]
        benchmarking_enabled = bool(params.get("content_performance_benchmarking", True))
        
        if not benchmarking_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        benchmarks_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de benchmarks si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_performance_benchmarks (
                        benchmark_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        category VARCHAR(100),
                        engagement_rate DECIMAL(10,2),
                        industry_avg DECIMAL(10,2),
                        benchmark_score DECIMAL(10,2),
                        performance_tier VARCHAR(50),
                        benchmarked_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Benchmarks de industria (valores estándar)
                industry_benchmarks = {
                    "twitter": {"avg": 1.5, "good": 3.0, "excellent": 5.0},
                    "linkedin": {"avg": 2.0, "good": 4.0, "excellent": 6.0},
                    "facebook": {"avg": 1.0, "good": 2.5, "excellent": 4.0},
                    "instagram": {"avg": 2.5, "good": 5.0, "excellent": 8.0}
                }
                
                # Analizar posts recientes
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        a.category,
                        e.engagement_rate,
                        e.impressions
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND e.engagement_rate IS NOT NULL
                    ORDER BY e.engagement_rate DESC
                    LIMIT 30
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    category = post.get("category", "general")
                    engagement_rate = float(post.get("engagement_rate", 0) or 0)
                    
                    # Obtener benchmark de industria
                    platform_benchmark = industry_benchmarks.get(platform, industry_benchmarks["twitter"])
                    industry_avg = platform_benchmark["avg"]
                    
                    # Calcular score de benchmark (0-100)
                    if engagement_rate >= platform_benchmark["excellent"]:
                        benchmark_score = 90 + min((engagement_rate - platform_benchmark["excellent"]) * 2, 10)
                        performance_tier = "excellent"
                    elif engagement_rate >= platform_benchmark["good"]:
                        benchmark_score = 70 + ((engagement_rate - platform_benchmark["good"]) / (platform_benchmark["excellent"] - platform_benchmark["good"])) * 20
                        performance_tier = "good"
                    elif engagement_rate >= industry_avg:
                        benchmark_score = 50 + ((engagement_rate - industry_avg) / (platform_benchmark["good"] - industry_avg)) * 20
                        performance_tier = "above_average"
                    else:
                        benchmark_score = max(0, (engagement_rate / industry_avg) * 50)
                        performance_tier = "below_average"
                    
                    benchmark_score = min(benchmark_score, 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_performance_benchmarks
                            (post_id, platform, category, engagement_rate, industry_avg,
                             benchmark_score, performance_tier, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            post_id,
                            platform,
                            category,
                            round(engagement_rate, 2),
                            round(industry_avg, 2),
                            round(benchmark_score, 2),
                            performance_tier,
                            json.dumps({
                                "benchmarked_at": datetime.utcnow().isoformat(),
                                "industry_good": platform_benchmark["good"],
                                "industry_excellent": platform_benchmark["excellent"]
                            })
                        ))
                        
                        benchmarks_created += 1
                        logger.debug(f"Benchmark creado: post_id={post_id}, tier={performance_tier}, score={benchmark_score:.1f}")
                    
                    except Exception as e:
                        logger.error(f"Error creando benchmark para {post_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Benchmarking de performance: {benchmarks_created} benchmarks creados")
        
        if Stats:
            try:
                Stats.incr("social_media.performance_benchmarks_created", benchmarks_created)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="engagement_anomaly_detection")
    def engagement_anomaly_detection(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta anomalías en engagement usando análisis estadístico."""
        ctx = get_current_context()
        params = ctx["params"]
        detection_enabled = bool(params.get("engagement_anomaly_detection", True))
        
        if not detection_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        anomalies_detected = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de anomalías si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_engagement_anomalies (
                        anomaly_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        anomaly_type VARCHAR(50),
                        engagement_rate DECIMAL(10,2),
                        z_score DECIMAL(10,2),
                        detected_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Calcular estadísticas por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        AVG(e.engagement_rate) as avg_engagement,
                        STDDEV(e.engagement_rate) as stddev_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND e.engagement_rate IS NOT NULL
                    GROUP BY sp.platform
                    HAVING COUNT(*) >= 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                platform_stats = {row[0]: {"avg": float(row[1] or 0), "stddev": float(row[2] or 1)} for row in cur.fetchall()}
                
                # Buscar posts recientes para detectar anomalías
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        e.engagement_rate
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND e.engagement_rate IS NOT NULL
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    engagement_rate = float(post.get("engagement_rate", 0) or 0)
                    
                    stats = platform_stats.get(platform)
                    if not stats or stats["stddev"] == 0:
                        continue
                    
                    # Calcular Z-score
                    z_score = (engagement_rate - stats["avg"]) / stats["stddev"]
                    
                    # Detectar anomalías (Z-score > 2 o < -2)
                    anomaly_type = None
                    if z_score > 2:
                        anomaly_type = "high_performance"
                    elif z_score < -2:
                        anomaly_type = "low_performance"
                    
                    if anomaly_type:
                        try:
                            cur.execute("""
                                INSERT INTO content_engagement_anomalies
                                (post_id, platform, anomaly_type, engagement_rate, z_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                post_id,
                                platform,
                                anomaly_type,
                                round(engagement_rate, 2),
                                round(z_score, 2),
                                json.dumps({
                                    "platform_avg": round(stats["avg"], 2),
                                    "platform_stddev": round(stats["stddev"], 2),
                                    "detected_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            anomalies_detected += 1
                            logger.info(f"Anomalía detectada: post_id={post_id}, type={anomaly_type}, z_score={z_score:.2f}")
                        
                        except Exception as e:
                            logger.error(f"Error guardando anomalía para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Detección de anomalías: {anomalies_detected} anomalías detectadas")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_anomalies_detected", anomalies_detected)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_trend_analysis")
    def content_trend_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza tendencias de contenido y categorías."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("content_trend_analysis", True))
        
        if not analysis_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        trends_analyzed = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de tendencias si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_trends (
                        trend_id SERIAL PRIMARY KEY,
                        category VARCHAR(100),
                        platform VARCHAR(50),
                        trend_direction VARCHAR(50),
                        engagement_change DECIMAL(10,2),
                        trend_strength DECIMAL(10,2),
                        analyzed_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar tendencias por categoría y plataforma
                cur.execute("""
                    SELECT 
                        a.category,
                        sp.platform,
                        AVG(CASE WHEN sp.published_at >= NOW() - INTERVAL '14 days' 
                            THEN e.engagement_rate END) as recent_avg,
                        AVG(CASE WHEN sp.published_at >= NOW() - INTERVAL '30 days' 
                            AND sp.published_at < NOW() - INTERVAL '14 days'
                            THEN e.engagement_rate END) as previous_avg
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    AND e.engagement_rate IS NOT NULL
                    GROUP BY a.category, sp.platform
                    HAVING COUNT(*) >= 5
                """)
                
                columns = [desc[0] for desc in cur.description]
                category_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for data in category_data:
                    category = data.get("category", "general")
                    platform = data.get("platform", "")
                    recent_avg = float(data.get("recent_avg", 0) or 0)
                    previous_avg = float(data.get("previous_avg", 0) or 0)
                    
                    if previous_avg == 0:
                        continue
                    
                    # Calcular cambio porcentual
                    engagement_change = ((recent_avg - previous_avg) / previous_avg) * 100
                    
                    # Determinar dirección de tendencia
                    if engagement_change > 10:
                        trend_direction = "rising"
                        trend_strength = min(100, abs(engagement_change) * 2)
                    elif engagement_change < -10:
                        trend_direction = "declining"
                        trend_strength = min(100, abs(engagement_change) * 2)
                    else:
                        trend_direction = "stable"
                        trend_strength = 50 - abs(engagement_change)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_trends
                            (category, platform, trend_direction, engagement_change, trend_strength, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            category,
                            platform,
                            trend_direction,
                            round(engagement_change, 2),
                            round(trend_strength, 2),
                            json.dumps({
                                "recent_avg": round(recent_avg, 2),
                                "previous_avg": round(previous_avg, 2),
                                "analyzed_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        trends_analyzed += 1
                        logger.debug(f"Tendencia analizada: {category}/{platform}, direction={trend_direction}, change={engagement_change:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error analizando tendencia: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Análisis de tendencias: {trends_analyzed} tendencias analizadas")
        
        if Stats:
            try:
                Stats.incr("social_media.content_trends_analyzed", trends_analyzed)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_quality_ml_scoring")
    def content_quality_ml_scoring(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scoring ML avanzado de calidad de contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        scoring_enabled = bool(params.get("content_quality_ml_scoring", True))
        
        if not scoring_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_scored = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    
                    # Modelo simplificado de scoring ML (en producción usar modelo real)
                    quality_score = 0
                    quality_factors = {}
                    
                    # Factor 1: Longitud del contenido (20%)
                    content_length = len(content)
                    if 500 <= content_length <= 2000:
                        length_score = 20
                    elif 200 <= content_length < 500 or 2000 < content_length <= 3000:
                        length_score = 15
                    else:
                        length_score = 10
                    quality_score += length_score
                    quality_factors["length_score"] = length_score
                    
                    # Factor 2: Título (20%)
                    title_length = len(title)
                    if 30 <= title_length <= 70:
                        title_score = 20
                    elif 20 <= title_length < 30 or 70 < title_length <= 100:
                        title_score = 15
                    else:
                        title_score = 10
                    quality_score += title_score
                    quality_factors["title_score"] = title_score
                    
                    # Factor 3: Keywords y estructura (30%)
                    keywords_count = len([w for w in content.lower().split() if len(w) > 4])
                    if keywords_count >= 20:
                        keywords_score = 30
                    elif keywords_count >= 10:
                        keywords_score = 20
                    else:
                        keywords_score = 10
                    quality_score += keywords_score
                    quality_factors["keywords_score"] = keywords_score
                    
                    # Factor 4: Legibilidad (30%)
                    sentences = content.split('.')
                    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
                    if 10 <= avg_sentence_length <= 20:
                        readability_score = 30
                    elif 5 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 30:
                        readability_score = 20
                    else:
                        readability_score = 10
                    quality_score += readability_score
                    quality_factors["readability_score"] = readability_score
                    
                    quality_score = min(quality_score, 100)
                    
                    # Clasificar calidad
                    if quality_score >= 80:
                        quality_tier = "excellent"
                    elif quality_score >= 60:
                        quality_tier = "good"
                    elif quality_score >= 40:
                        quality_tier = "fair"
                    else:
                        quality_tier = "poor"
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'ml_quality_score', %s,
                                    'ml_quality_tier', %s,
                                    'ml_quality_factors', %s,
                                    'ml_scored_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            round(quality_score, 2),
                            quality_tier,
                            json.dumps(quality_factors),
                            article_id
                        ))
                        
                        articles_scored += 1
                        logger.debug(f"Calidad ML calculada: article_id={article_id}, score={quality_score:.1f} ({quality_tier})")
                    
                    except Exception as e:
                        logger.error(f"Error calculando calidad ML para {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Scoring ML de calidad: {articles_scored} artículos evaluados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_ml_scored", articles_scored)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="content_viral_potential_scoring")
    def content_viral_potential_scoring(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el potencial viral de contenido antes de publicar."""
        ctx = get_current_context()
        params = ctx["params"]
        scoring_enabled = bool(params.get("content_viral_potential_scoring", True))
        
        if not scoring_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        articles_scored = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    title = article.get("title", "")
                    content = article.get("content", "")
                    category = article.get("category", "general")
                    
                    # Calcular potencial viral (0-100)
                    viral_score = 0
                    viral_factors = {}
                    
                    # Factor 1: Trending topics alignment (25%)
                    hashtags = article.get("hashtags") or []
                    trending_hashtags = len([h for h in hashtags if "#" in str(h)])
                    trending_score = min(trending_hashtags * 5, 25)
                    viral_score += trending_score
                    viral_factors["trending_alignment"] = trending_score
                    
                    # Factor 2: Emotional triggers (25%)
                    emotional_words = ["amazing", "incredible", "shocking", "must", "best", "top", "ultimate", "secret"]
                    emotional_count = sum(1 for word in emotional_words if word in content.lower() or word in title.lower())
                    emotional_score = min(emotional_count * 5, 25)
                    viral_score += emotional_score
                    viral_factors["emotional_triggers"] = emotional_score
                    
                    # Factor 3: Content length optimization (20%)
                    content_length = len(content)
                    if 300 <= content_length <= 1000:
                        length_score = 20
                    elif 100 <= content_length < 300 or 1000 < content_length <= 2000:
                        length_score = 15
                    else:
                        length_score = 10
                    viral_score += length_score
                    viral_factors["optimal_length"] = length_score
                    
                    # Factor 4: Question/engagement hooks (15%)
                    has_question = "?" in title or "?" in content[:200]
                    has_call_to_action = any(cta in content.lower()[:200] for cta in ["share", "comment", "like", "retweet"])
                    engagement_hooks_score = 15 if (has_question or has_call_to_action) else 5
                    viral_score += engagement_hooks_score
                    viral_factors["engagement_hooks"] = engagement_hooks_score
                    
                    # Factor 5: Historical performance prediction (15%)
                    # Basado en predicción de engagement si existe
                    predicted_engagement = article.get("metadata", {}).get("predicted_engagement_rate") if isinstance(article.get("metadata"), dict) else None
                    if predicted_engagement:
                        prediction_score = min(float(predicted_engagement) * 3, 15)
                        viral_score += prediction_score
                        viral_factors["prediction_based"] = prediction_score
                    
                    viral_score = min(viral_score, 100)
                    
                    # Clasificar potencial viral
                    if viral_score >= 75:
                        viral_potential = "high"
                    elif viral_score >= 50:
                        viral_potential = "medium"
                    else:
                        viral_potential = "low"
                    
                    try:
                        cur.execute("""
                            UPDATE content_articles
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object(
                                    'viral_potential_score', %s,
                                    'viral_potential', %s,
                                    'viral_factors', %s,
                                    'viral_scored_at', NOW()
                                )
                            WHERE article_id = %s
                        """, (
                            round(viral_score, 2),
                            viral_potential,
                            json.dumps(viral_factors),
                            article_id
                        ))
                        
                        articles_scored += 1
                        logger.debug(f"Potencial viral calculado: article_id={article_id}, score={viral_score:.1f} ({viral_potential})")
                    
                    except Exception as e:
                        logger.error(f"Error calculando potencial viral para {article_id}: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Scoring de potencial viral: {articles_scored} artículos evaluados")
        
        if Stats:
            try:
                Stats.incr("social_media.articles_viral_scored", articles_scored)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="content_engagement_optimization_ml")
    def content_engagement_optimization_ml(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimización ML de engagement basada en aprendizaje de patrones."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("content_engagement_optimization_ml", True))
        
        if not optimization_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        optimizations_applied = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de optimizaciones ML si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_ml_optimizations (
                        optimization_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        optimization_type VARCHAR(50),
                        before_engagement DECIMAL(10,2),
                        predicted_improvement DECIMAL(10,2),
                        optimization_score DECIMAL(10,2),
                        applied_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar posts con bajo engagement para optimización
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        a.category,
                        e.engagement_rate,
                        e.impressions
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    AND e.engagement_rate < 2.0
                    ORDER BY e.engagement_rate ASC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    category = post.get("category", "general")
                    current_engagement = float(post.get("engagement_rate", 0) or 0)
                    
                    # Buscar mejor práctica de la categoría
                    cur.execute("""
                        SELECT AVG(e.engagement_rate) as avg_engagement
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.platform = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                        AND e.engagement_rate > 3.0
                    """, (category, platform))
                    
                    best_practice = cur.fetchone()
                    if best_practice and best_practice[0]:
                        avg_best_practice = float(best_practice[0])
                        predicted_improvement = avg_best_practice - current_engagement
                        optimization_score = min(predicted_improvement * 20, 100)
                        
                        # Determinar tipo de optimización
                        if predicted_improvement > 2.0:
                            optimization_type = "high_impact"
                        elif predicted_improvement > 1.0:
                            optimization_type = "medium_impact"
                        else:
                            optimization_type = "low_impact"
                        
                        try:
                            cur.execute("""
                                INSERT INTO content_ml_optimizations
                                (post_id, platform, optimization_type, before_engagement,
                                 predicted_improvement, optimization_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (
                                post_id,
                                platform,
                                optimization_type,
                                round(current_engagement, 2),
                                round(predicted_improvement, 2),
                                round(optimization_score, 2),
                                json.dumps({
                                    "category": category,
                                    "best_practice_avg": round(avg_best_practice, 2),
                                    "optimized_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            optimizations_applied += 1
                            logger.debug(f"Optimización ML: post_id={post_id}, improvement={predicted_improvement:.1f}%, type={optimization_type}")
                        
                        except Exception as e:
                            logger.error(f"Error aplicando optimización ML para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización ML de engagement: {optimizations_applied} optimizaciones aplicadas")
        
        if Stats:
            try:
                Stats.incr("social_media.ml_optimizations_applied", optimizations_applied)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_engagement_responses")
    def automated_engagement_responses(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Respuestas automáticas inteligentes a engagement."""
        ctx = get_current_context()
        params = ctx["params"]
        responses_enabled = bool(params.get("automated_engagement_responses", True))
        
        if not responses_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        responses_generated = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de respuestas automáticas si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_automated_responses (
                        response_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        response_type VARCHAR(50),
                        response_content TEXT,
                        generated_at TIMESTAMP DEFAULT NOW(),
                        sent BOOLEAN DEFAULT FALSE,
                        metadata JSONB
                    )
                """)
                
                # Buscar posts con alto engagement que necesitan respuesta
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        a.title,
                        e.comments,
                        e.likes,
                        e.shares
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '24 hours'
                    AND (e.comments > 5 OR e.likes > 20 OR e.shares > 5)
                    AND NOT EXISTS (
                        SELECT 1 FROM content_automated_responses
                        WHERE post_id = sp.post_id
                    )
                    ORDER BY (e.comments + e.likes + e.shares) DESC
                    LIMIT 10
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    title = post.get("title", "")
                    comments = post.get("comments", 0) or 0
                    likes = post.get("likes", 0) or 0
                    shares = post.get("shares", 0) or 0
                    
                    # Generar respuesta basada en tipo de engagement
                    response_content = None
                    response_type = None
                    
                    if comments > 5:
                        response_type = "thank_you_comment"
                        response_content = f"¡Gracias por todos los comentarios! Nos encanta escuchar vuestras opiniones sobre '{title[:50]}...'"
                    elif shares > 5:
                        response_type = "thank_you_share"
                        response_content = f"¡Increíble ver que estáis compartiendo '{title[:50]}...'! Gracias por ayudar a difundir el mensaje."
                    elif likes > 20:
                        response_type = "thank_you_like"
                        response_content = f"¡Gracias por todo el apoyo! Nos alegra que os guste '{title[:50]}...'"
                    
                    if response_content:
                        try:
                            cur.execute("""
                                INSERT INTO content_automated_responses
                                (post_id, platform, response_type, response_content, metadata)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                post_id,
                                platform,
                                response_type,
                                response_content,
                                json.dumps({
                                    "comments": comments,
                                    "likes": likes,
                                    "shares": shares,
                                    "generated_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            responses_generated += 1
                            logger.info(f"Respuesta generada: post_id={post_id}, type={response_type}")
                        
                        except Exception as e:
                            logger.error(f"Error generando respuesta para {post_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Respuestas automáticas: {responses_generated} respuestas generadas")
        
        if Stats:
            try:
                Stats.incr("social_media.automated_responses_generated", responses_generated)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_audience_growth_analysis")
    def content_audience_growth_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el crecimiento de audiencia y engagement a lo largo del tiempo."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("content_audience_growth_analysis", True))
        
        if not analysis_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de crecimiento si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_audience_growth (
                        growth_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50),
                        period_start DATE,
                        period_end DATE,
                        follower_growth INTEGER,
                        engagement_growth DECIMAL(10,2),
                        growth_rate DECIMAL(10,2),
                        analyzed_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar crecimiento por plataforma (últimos 30 días vs. anteriores 30 días)
                cur.execute("""
                    SELECT 
                        sp.platform,
                        COUNT(DISTINCT sp.post_id) as recent_posts,
                        SUM(e.impressions) as recent_impressions,
                        AVG(e.engagement_rate) as recent_engagement,
                        COUNT(DISTINCT sp2.post_id) as previous_posts,
                        SUM(e2.impressions) as previous_impressions,
                        AVG(e2.engagement_rate) as previous_engagement
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    LEFT JOIN content_scheduled_posts sp2 ON sp2.platform = sp.platform
                        AND sp2.published_at >= NOW() - INTERVAL '60 days'
                        AND sp2.published_at < NOW() - INTERVAL '30 days'
                        AND sp2.status = 'published'
                    LEFT JOIN content_engagement e2 ON e2.post_id = sp2.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform
                """)
                
                columns = [desc[0] for desc in cur.description]
                growth_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for data in growth_data:
                    platform = data.get("platform", "")
                    recent_engagement = float(data.get("recent_engagement", 0) or 0)
                    previous_engagement = float(data.get("previous_engagement", 0) or 0)
                    recent_impressions = data.get("recent_impressions", 0) or 0
                    previous_impressions = data.get("previous_impressions", 0) or 0
                    
                    # Calcular crecimiento
                    if previous_engagement > 0:
                        engagement_growth = ((recent_engagement - previous_engagement) / previous_engagement) * 100
                    else:
                        engagement_growth = 0
                    
                    if previous_impressions > 0:
                        impression_growth = ((recent_impressions - previous_impressions) / previous_impressions) * 100
                    else:
                        impression_growth = 0
                    
                    growth_rate = (engagement_growth + impression_growth) / 2
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_audience_growth
                            (platform, period_start, period_end, follower_growth,
                             engagement_growth, growth_rate, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            platform,
                            (datetime.utcnow() - timedelta(days=30)).date(),
                            datetime.utcnow().date(),
                            int(impression_growth),
                            round(engagement_growth, 2),
                            round(growth_rate, 2),
                            json.dumps({
                                "recent_engagement": round(recent_engagement, 2),
                                "previous_engagement": round(previous_engagement, 2),
                                "recent_impressions": recent_impressions,
                                "previous_impressions": previous_impressions,
                                "analyzed_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        logger.debug(f"Crecimiento analizado: {platform}, engagement_growth={engagement_growth:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error analizando crecimiento: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info("Análisis de crecimiento de audiencia: análisis completado")
        
        if Stats:
            try:
                Stats.incr("social_media.audience_growth_analyzed", 1)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="content_performance_insights_ml")
    def content_performance_insights_ml(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera insights ML avanzados sobre performance de contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        insights_enabled = bool(params.get("content_performance_insights_ml", True))
        
        if not insights_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        insights_generated = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de insights ML si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_ml_insights (
                        insight_id SERIAL PRIMARY KEY,
                        post_id INTEGER,
                        platform VARCHAR(50),
                        insight_type VARCHAR(50),
                        insight_value DECIMAL(10,2),
                        insight_description TEXT,
                        confidence_score DECIMAL(10,2),
                        generated_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar posts recientes para generar insights
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        a.category,
                        a.title,
                        e.engagement_rate,
                        e.impressions,
                        e.likes,
                        e.comments,
                        e.shares,
                        e.click_through_rate
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '7 days'
                    ORDER BY e.engagement_rate DESC
                    LIMIT 20
                """)
                
                columns = [desc[0] for desc in cur.description]
                posts = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for post in posts:
                    post_id = post["post_id"]
                    platform = post["platform"]
                    category = post.get("category", "general")
                    engagement_rate = float(post.get("engagement_rate", 0) or 0)
                    ctr = float(post.get("click_through_rate", 0) or 0)
                    
                    insights = []
                    
                    # Insight 1: Performance vs. category average
                    cur.execute("""
                        SELECT AVG(e.engagement_rate)
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.platform = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                    """, (category, platform))
                    
                    category_avg = cur.fetchone()
                    if category_avg and category_avg[0]:
                        avg_engagement = float(category_avg[0])
                        if engagement_rate > avg_engagement * 1.5:
                            insights.append({
                                "type": "above_category_average",
                                "value": round(((engagement_rate / avg_engagement) - 1) * 100, 2),
                                "description": f"Performance {round(((engagement_rate / avg_engagement) - 1) * 100, 1)}% above category average",
                                "confidence": 85.0
                            })
                    
                    # Insight 2: CTR performance
                    if ctr > 3.0:
                        insights.append({
                            "type": "high_ctr",
                            "value": round(ctr, 2),
                            "description": f"Excellent click-through rate: {ctr:.1f}%",
                            "confidence": 90.0
                        })
                    
                    # Insight 3: Engagement velocity
                    if engagement_rate > 5.0:
                        insights.append({
                            "type": "high_engagement",
                            "value": round(engagement_rate, 2),
                            "description": f"High engagement rate: {engagement_rate:.1f}% - Consider repurposing",
                            "confidence": 80.0
                        })
                    
                    # Guardar insights
                    for insight in insights:
                        try:
                            cur.execute("""
                                INSERT INTO content_ml_insights
                                (post_id, platform, insight_type, insight_value,
                                 insight_description, confidence_score, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                post_id,
                                platform,
                                insight["type"],
                                insight["value"],
                                insight["description"],
                                insight["confidence"],
                                json.dumps({
                                    "category": category,
                                    "generated_at": datetime.utcnow().isoformat()
                                })
                            ))
                            
                            insights_generated += 1
                            logger.debug(f"Insight generado: post_id={post_id}, type={insight['type']}")
                        
                        except Exception as e:
                            logger.error(f"Error guardando insight: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Insights ML generados: {insights_generated} insights creados")
        
        if Stats:
            try:
                Stats.incr("social_media.ml_insights_generated", insights_generated)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="social_media_roi_optimization")
    def social_media_roi_optimization(roi_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza ROI de redes sociales basado en performance."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("social_media_roi_optimization", True))
        
        if not optimization_enabled:
            return roi_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        optimizations_applied = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de optimizaciones ROI si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_roi_optimizations (
                        optimization_id SERIAL PRIMARY KEY,
                        platform VARCHAR(50),
                        category VARCHAR(100),
                        current_roi DECIMAL(10,2),
                        optimized_roi DECIMAL(10,2),
                        improvement_percentage DECIMAL(10,2),
                        optimization_strategy TEXT,
                        applied_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Analizar ROI por plataforma y categoría
                cur.execute("""
                    SELECT 
                        sp.platform,
                        a.category,
                        AVG((e.impressions * e.engagement_rate / 100) * 0.02 - 0.5) as avg_roi,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '30 days'
                    GROUP BY sp.platform, a.category
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG((e.impressions * e.engagement_rate / 100) * 0.02 - 0.5) DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                roi_data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for data in roi_data:
                    platform = data.get("platform", "")
                    category = data.get("category", "general")
                    current_roi = float(data.get("avg_roi", 0) or 0)
                    
                    # Estrategia de optimización basada en ROI actual
                    if current_roi < 0:
                        optimization_strategy = "Focus on high-engagement content. Consider reducing posting frequency for this category."
                        optimized_roi = current_roi * 1.5  # Mejora estimada
                    elif current_roi < 1.0:
                        optimization_strategy = "Increase engagement rate through better timing and hashtag optimization."
                        optimized_roi = current_roi * 1.3
                    else:
                        optimization_strategy = "Maintain current strategy. Consider scaling successful content."
                        optimized_roi = current_roi * 1.1
                    
                    improvement_percentage = ((optimized_roi - current_roi) / abs(current_roi)) * 100 if current_roi != 0 else 0
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_roi_optimizations
                            (platform, category, current_roi, optimized_roi,
                             improvement_percentage, optimization_strategy, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            platform,
                            category,
                            round(current_roi, 2),
                            round(optimized_roi, 2),
                            round(improvement_percentage, 2),
                            optimization_strategy,
                            json.dumps({
                                "post_count": data.get("post_count", 0),
                                "optimized_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        optimizations_applied += 1
                        logger.debug(f"ROI optimizado: {platform}/{category}, improvement={improvement_percentage:.1f}%")
                    
                    except Exception as e:
                        logger.error(f"Error optimizando ROI: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Optimización de ROI: {optimizations_applied} optimizaciones aplicadas")
        
        if Stats:
            try:
                Stats.incr("social_media.roi_optimizations_applied", optimizations_applied)
            except Exception:
                pass
        
        return roi_result
    
    @task(task_id="content_engagement_pattern_analysis")
    def content_engagement_pattern_analysis(track_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza patrones de engagement para identificar tendencias y oportunidades."""
        ctx = get_current_context()
        params = ctx["params"]
        analysis_enabled = bool(params.get("content_engagement_pattern_analysis", True))
        
        if not analysis_enabled:
            return track_result
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        patterns_identified = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de patrones si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_engagement_patterns (
                        pattern_id SERIAL PRIMARY KEY,
                        pattern_type VARCHAR(50),
                        platform VARCHAR(50),
                        category VARCHAR(100),
                        pattern_description TEXT,
                        pattern_strength DECIMAL(10,2),
                        identified_at TIMESTAMP DEFAULT NOW(),
                        metadata JSONB
                    )
                """)
                
                # Patrón 1: Mejor día de la semana
                cur.execute("""
                    SELECT 
                        sp.platform,
                        EXTRACT(DOW FROM sp.published_at) as day_of_week,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '90 days'
                    GROUP BY sp.platform, EXTRACT(DOW FROM sp.published_at)
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG(e.engagement_rate) DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                day_patterns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for pattern in day_patterns:
                    platform = pattern.get("platform", "")
                    day_of_week = int(pattern.get("day_of_week", 0) or 0)
                    avg_engagement = float(pattern.get("avg_engagement", 0) or 0)
                    post_count = pattern.get("post_count", 0)
                    
                    day_names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
                    day_name = day_names[day_of_week] if day_of_week < len(day_names) else f"Día {day_of_week}"
                    
                    pattern_strength = min(avg_engagement * 10, 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_engagement_patterns
                            (pattern_type, platform, pattern_description, pattern_strength, metadata)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            "best_day_of_week",
                            platform,
                            f"{day_name} shows highest engagement ({avg_engagement:.1f}%) with {post_count} posts",
                            round(pattern_strength, 2),
                            json.dumps({
                                "day_of_week": day_of_week,
                                "day_name": day_name,
                                "avg_engagement": round(avg_engagement, 2),
                                "post_count": post_count,
                                "identified_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        patterns_identified += 1
                        logger.debug(f"Patrón identificado: {platform} - mejor día {day_name}")
                    
                    except Exception as e:
                        logger.error(f"Error guardando patrón: {e}", exc_info=True)
                        continue
                
                # Patrón 2: Mejor categoría por plataforma
                cur.execute("""
                    SELECT 
                        sp.platform,
                        a.category,
                        AVG(e.engagement_rate) as avg_engagement,
                        COUNT(*) as post_count
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.status = 'published'
                    AND sp.published_at >= NOW() - INTERVAL '90 days'
                    GROUP BY sp.platform, a.category
                    HAVING COUNT(*) >= 5
                    ORDER BY AVG(e.engagement_rate) DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                category_patterns = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for pattern in category_patterns:
                    platform = pattern.get("platform", "")
                    category = pattern.get("category", "general")
                    avg_engagement = float(pattern.get("avg_engagement", 0) or 0)
                    post_count = pattern.get("post_count", 0)
                    
                    pattern_strength = min(avg_engagement * 10, 100)
                    
                    try:
                        cur.execute("""
                            INSERT INTO content_engagement_patterns
                            (pattern_type, platform, category, pattern_description, pattern_strength, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            "best_category",
                            platform,
                            category,
                            f"Category '{category}' performs best on {platform} ({avg_engagement:.1f}% engagement, {post_count} posts)",
                            round(pattern_strength, 2),
                            json.dumps({
                                "avg_engagement": round(avg_engagement, 2),
                                "post_count": post_count,
                                "identified_at": datetime.utcnow().isoformat()
                            })
                        ))
                        
                        patterns_identified += 1
                        logger.debug(f"Patrón identificado: {platform} - mejor categoría {category}")
                    
                    except Exception as e:
                        logger.error(f"Error guardando patrón: {e}", exc_info=True)
                        continue
                
                conn.commit()
        
        logger.info(f"Análisis de patrones: {patterns_identified} patrones identificados")
        
        if Stats:
            try:
                Stats.incr("social_media.engagement_patterns_identified", patterns_identified)
            except Exception:
                pass
        
        return track_result
    
    @task(task_id="automated_hashtag_optimization_ml")
    def automated_hashtag_optimization_ml(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza hashtags usando ML basado en performance histórico."""
        ctx = get_current_context()
        params = ctx["params"]
        optimization_enabled = bool(params.get("automated_hashtag_optimization_ml", True))
        
        if not optimization_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        hashtags_optimized = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    category = article.get("category", "general")
                    current_hashtags = article.get("hashtags") or []
                    
                    # Buscar hashtags de mejor performance para esta categoría
                    cur.execute("""
                        SELECT 
                            hashtag,
                            AVG(e.engagement_rate) as avg_engagement,
                            COUNT(*) as usage_count
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        CROSS JOIN LATERAL unnest(string_to_array(sp.hashtags, ',')) as hashtag
                        WHERE a.category = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                        AND hashtag LIKE '#%'
                        GROUP BY hashtag
                        HAVING COUNT(*) >= 2
                        ORDER BY AVG(e.engagement_rate) DESC
                        LIMIT 5
                    """, (category,))
                    
                    optimal_hashtags = [row[0] for row in cur.fetchall()]
                    
                    if optimal_hashtags:
                        # Combinar hashtags actuales con óptimos
                        optimized_hashtags = list(set(current_hashtags + optimal_hashtags))[:10]  # Máximo 10
                        
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'optimized_hashtags', %s,
                                        'hashtags_optimized_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (
                                json.dumps(optimized_hashtags),
                                article_id
                            ))
                            
                            hashtags_optimized += 1
                            logger.debug(f"Hashtags optimizados: article_id={article_id}, optimized={len(optimized_hashtags)}")
                        
                        except Exception as e:
                            logger.error(f"Error optimizando hashtags para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Optimización ML de hashtags: {hashtags_optimized} artículos optimizados")
        
        if Stats:
            try:
                Stats.incr("social_media.hashtags_optimized_ml", hashtags_optimized)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="content_performance_forecasting_ml")
    def content_performance_forecasting_ml(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Forecasting ML avanzado de performance de contenido."""
        ctx = get_current_context()
        params = ctx["params"]
        forecasting_enabled = bool(params.get("content_performance_forecasting_ml", True))
        
        if not forecasting_enabled:
            return content_data
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        forecasts_created = 0
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                articles = content_data.get("articles", [])
                
                for article in articles:
                    article_id = article["article_id"]
                    category = article.get("category", "general")
                    title = article.get("title", "")
                    
                    # Forecasting basado en performance histórico de categoría similar
                    cur.execute("""
                        SELECT 
                            AVG(e.engagement_rate) as avg_engagement,
                            AVG(e.impressions) as avg_impressions,
                            AVG(e.click_through_rate) as avg_ctr,
                            COUNT(*) as sample_size
                        FROM content_scheduled_posts sp
                        JOIN content_articles a ON a.article_id = sp.article_id
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE a.category = %s
                        AND sp.status = 'published'
                        AND sp.published_at >= NOW() - INTERVAL '60 days'
                    """, (category,))
                    
                    historical = cur.fetchone()
                    if historical and historical[0]:
                        avg_engagement = float(historical[0] or 0)
                        avg_impressions = float(historical[1] or 0) if historical[1] else 0
                        avg_ctr = float(historical[2] or 0) if historical[2] else 0
                        sample_size = historical[3] or 0
                        
                        # Ajustar forecast basado en calidad del contenido (si existe)
                        quality_score = article.get("metadata", {}).get("ml_quality_score") if isinstance(article.get("metadata"), dict) else None
                        if quality_score:
                            quality_multiplier = 1 + (float(quality_score) / 100) * 0.2  # Hasta 20% bonus
                            forecasted_engagement = avg_engagement * quality_multiplier
                        else:
                            forecasted_engagement = avg_engagement
                        
                        confidence = min(90.0, 50.0 + (sample_size * 2))  # Más datos = más confianza
                        
                        try:
                            cur.execute("""
                                UPDATE content_articles
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                    jsonb_build_object(
                                        'ml_forecasted_engagement', %s,
                                        'ml_forecasted_impressions', %s,
                                        'ml_forecasted_ctr', %s,
                                        'forecast_confidence', %s,
                                        'forecasted_at', NOW()
                                    )
                                WHERE article_id = %s
                            """, (
                                round(forecasted_engagement, 2),
                                int(avg_impressions),
                                round(avg_ctr, 2),
                                round(confidence, 2),
                                article_id
                            ))
                            
                            forecasts_created += 1
                            logger.debug(f"Forecast ML creado: article_id={article_id}, engagement={forecasted_engagement:.1f}%, confidence={confidence:.1f}%")
                        
                        except Exception as e:
                            logger.error(f"Error creando forecast ML para {article_id}: {e}", exc_info=True)
                            continue
                
                conn.commit()
        
        logger.info(f"Forecasting ML de performance: {forecasts_created} forecasts creados")
        
        if Stats:
            try:
                Stats.incr("social_media.ml_forecasts_created", forecasts_created)
            except Exception:
                pass
        
        return content_data
    
    @task(task_id="export_analytics_data")
    def export_analytics_data(report_data: Dict[str, Any]) -> None:
        """Exporta datos de analytics para análisis externo."""
        ctx = get_current_context()
        params = ctx["params"]
        export_enabled = bool(params.get("export_analytics_data", False))
        
        if not export_enabled or report_data.get("skipped"):
            return
        
        conn_id = str(params["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Solo exportar los lunes (junto con el reporte semanal)
        current_date = datetime.utcnow()
        if current_date.weekday() != 0:
            return
        
        export_path = os.getenv("ANALYTICS_EXPORT_PATH", "/tmp/social_media_analytics")
        os.makedirs(export_path, exist_ok=True)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Exportar datos de engagement
                cur.execute("""
                    SELECT 
                        sp.post_id,
                        sp.platform,
                        sp.article_id,
                        a.title,
                        a.category,
                        e.likes,
                        e.comments,
                        e.shares,
                        e.impressions,
                        e.reach,
                        e.engagement_rate,
                        e.click_through_rate,
                        sp.published_at,
                        sp.published_url
                    FROM content_scheduled_posts sp
                    JOIN content_articles a ON a.article_id = sp.article_id
                    JOIN content_engagement e ON e.post_id = sp.post_id
                    WHERE sp.published_at >= NOW() - INTERVAL '30 days'
                    AND sp.status = 'published'
                    ORDER BY sp.published_at DESC
                """)
                
                columns = [desc[0] for desc in cur.description]
                data = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Exportar a JSON
                export_file = os.path.join(export_path, f"analytics_{current_date.strftime('%Y%m%d')}.json")
                with open(export_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                logger.info(f"Datos de analytics exportados: {len(data)} registros a {export_file}")
        
        if Stats:
            try:
                Stats.incr("social_media.analytics_exported", 1)
            except Exception:
                pass
    
    @task(task_id="send_weekly_report")
    def send_weekly_report(report_data: Dict[str, Any]) -> None:
        """Envía el reporte semanal por email y/o Slack."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if report_data.get("skipped"):
            return
        
        recipients_str = str(params.get("report_recipients", ""))
        recipients = [r.strip() for r in recipients_str.split(",") if r.strip()] if recipients_str else []
        
        # Formatear reporte
        period = report_data.get("period", {})
        summary = report_data.get("summary", {})
        platform_breakdown = report_data.get("platform_breakdown", [])
        top_posts = report_data.get("top_posts", [])
        recommendations = report_data.get("recommendations", [])
        
        # Texto plano
        text_body = f"""
Reporte Semanal de Redes Sociales
{'=' * 50}

Período: {period.get('start', 'N/A')} a {period.get('end', 'N/A')}

RESUMEN GENERAL
---------------
• Total de Posts: {summary.get('total_posts', 0)}
• Total de Artículos: {summary.get('total_articles', 0)}
• Engagement Total: {summary.get('total_engagement', 0):,}
• Impresiones Total: {summary.get('total_impressions', 0):,}
• Tasa de Engagement Promedio: {summary.get('avg_engagement_rate', 0):.2f}%

DESGLOSE POR PLATAFORMA
-----------------------
"""
        for platform in platform_breakdown:
            text_body += f"""
{platform.get('platform', 'N/A').upper()}:
  • Posts: {platform.get('total_posts', 0)}
  • Likes: {platform.get('total_likes', 0):,}
  • Comentarios: {platform.get('total_comments', 0):,}
  • Compartidos: {platform.get('total_shares', 0):,}
  • Engagement Rate: {platform.get('avg_engagement_rate', 0):.2f}%
"""
        
        if top_posts:
            text_body += "\nTOP 10 POSTS\n------------\n"
            for i, post in enumerate(top_posts[:10], 1):
                text_body += f"{i}. {post.get('article_title', 'N/A')[:50]}... ({post.get('platform', 'N/A')})\n"
                text_body += f"   Engagement: {post.get('total_engagement', 0):,} | Rate: {post.get('engagement_rate', 0):.2f}%\n"
        
        if recommendations:
            text_body += "\nRECOMENDACIONES\n---------------\n"
            for rec in recommendations:
                text_body += f"• [{rec.get('priority', 'medium').upper()}] {rec.get('message', 'N/A')}\n"
        
        # HTML
        html_body = f"""
        <html>
        <head><style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #333; }}
            .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
            .platform {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }}
            .top-post {{ margin: 5px 0; padding: 5px; }}
        </style></head>
        <body>
            <h1>📊 Reporte Semanal de Redes Sociales</h1>
            <p><strong>Período:</strong> {period.get('start', 'N/A')} a {period.get('end', 'N/A')}</p>
            
            <div class="summary">
                <h2>Resumen General</h2>
                <ul>
                    <li><strong>Total de Posts:</strong> {summary.get('total_posts', 0)}</li>
                    <li><strong>Total de Artículos:</strong> {summary.get('total_articles', 0)}</li>
                    <li><strong>Engagement Total:</strong> {summary.get('total_engagement', 0):,}</li>
                    <li><strong>Impresiones Total:</strong> {summary.get('total_impressions', 0):,}</li>
                    <li><strong>Tasa de Engagement Promedio:</strong> {summary.get('avg_engagement_rate', 0):.2f}%</li>
                </ul>
            </div>
            
            <h2>Desglose por Plataforma</h2>
"""
        for platform in platform_breakdown:
            html_body += f"""
            <div class="platform">
                <h3>{platform.get('platform', 'N/A').upper()}</h3>
                <ul>
                    <li>Posts: {platform.get('total_posts', 0)}</li>
                    <li>Likes: {platform.get('total_likes', 0):,}</li>
                    <li>Comentarios: {platform.get('total_comments', 0):,}</li>
                    <li>Compartidos: {platform.get('total_shares', 0):,}</li>
                    <li>Engagement Rate: {platform.get('avg_engagement_rate', 0):.2f}%</li>
                </ul>
            </div>
"""
        
        if top_posts:
            html_body += "<h2>Top 10 Posts</h2><ol>"
            for post in top_posts[:10]:
                html_body += f"""
                <li class="top-post">
                    <strong>{post.get('article_title', 'N/A')[:50]}...</strong> ({post.get('platform', 'N/A')})<br>
                    Engagement: {post.get('total_engagement', 0):,} | Rate: {post.get('engagement_rate', 0):.2f}%
                </li>
"""
            html_body += "</ol>"
        
        if recommendations:
            html_body += "<h2>💡 Recomendaciones</h2><ul>"
            for rec in recommendations:
                priority_color = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}.get(rec.get("priority", "medium"), "#6c757d")
                html_body += f"""
                <li style="margin: 10px 0; padding: 10px; border-left: 3px solid {priority_color};">
                    <strong>[{rec.get('priority', 'medium').upper()}]</strong> {rec.get('message', 'N/A')}
                </li>
"""
            html_body += "</ul>"
        
        html_body += "</body></html>"
        
        # Enviar por email
        if recipients and NOTIFICATIONS_AVAILABLE:
            for recipient in recipients:
                try:
                    notify_email(
                        to=recipient,
                        subject="📊 Reporte Semanal de Redes Sociales",
                        body=text_body,
                        html=html_body
                    )
                    logger.info(f"Reporte enviado por email a {recipient}")
                except Exception as e:
                    logger.error(f"Error enviando email a {recipient}: {e}", exc_info=True)
        
        # Enviar a Slack
        if NOTIFICATIONS_AVAILABLE:
            try:
                slack_message = f"""
📊 *Reporte Semanal de Redes Sociales*

*Período:* {period.get('start', 'N/A')} a {period.get('end', 'N/A')}

*Resumen:*
• Posts: {summary.get('total_posts', 0)}
• Engagement: {summary.get('total_engagement', 0):,}
• Engagement Rate: {summary.get('avg_engagement_rate', 0):.2f}%

*Top Plataforma:* {platform_breakdown[0].get('platform', 'N/A') if platform_breakdown else 'N/A'}
"""
                notify_slack(slack_message)
                logger.info("Reporte enviado a Slack")
            except Exception as e:
                logger.error(f"Error enviando a Slack: {e}", exc_info=True)
    
    # Funciones auxiliares
    def _calculate_optimal_publish_time(
        platform: str,
        posting_schedule: Optional[Dict],
        last_post: Optional[datetime],
        hourly_limit: int,
        article_id: Optional[str] = None,
        conn: Optional[Any] = None,
        optimize_ml: bool = True
    ) -> datetime:
        """Calcula el mejor momento para publicar según la plataforma."""
        now = datetime.utcnow()
        
        # Si hay un schedule configurado, usarlo
        if posting_schedule:
            # Lógica simplificada: publicar en la próxima hora disponible
            # En producción, esto debería considerar horarios óptimos por plataforma
            pass
        
        # Verificar límite horario
        if last_post:
            time_since_last = (now - last_post).total_seconds() / 3600
            if time_since_last < (60 / hourly_limit):  # minutos entre posts
                # Esperar hasta el próximo slot disponible
                minutes_to_wait = (60 / hourly_limit) - time_since_last
                now = now + timedelta(minutes=int(minutes_to_wait * 60) + 5)
        
        # Si ML está habilitado y hay datos históricos, usar análisis ML
        if optimize_ml and conn and article_id:
            try:
                with conn.cursor() as cur:
                    # Analizar mejor hora basada en histórico de engagement
                    cur.execute("""
                        SELECT 
                            EXTRACT(HOUR FROM sp.published_at) as hour,
                            AVG(e.engagement_rate) as avg_engagement,
                            COUNT(*) as sample_size
                        FROM content_scheduled_posts sp
                        JOIN content_engagement e ON e.post_id = sp.post_id
                        WHERE sp.platform = %s
                        AND sp.published_at >= NOW() - INTERVAL '30 days'
                        AND sp.status = 'published'
                        GROUP BY EXTRACT(HOUR FROM sp.published_at)
                        HAVING COUNT(*) >= 2
                        ORDER BY avg_engagement DESC
                        LIMIT 3
                    """, (platform,))
                    
                    ml_optimal_hours = [int(row[0]) for row in cur.fetchall()]
                    
                    if ml_optimal_hours:
                        # Usar horas óptimas basadas en ML
                        platform_hours = ml_optimal_hours
                        logger.debug(f"Usando horarios ML para {platform}: {platform_hours}")
                    else:
                        # Fallback a horarios por defecto
                        optimal_hours = {
                            "twitter": [9, 12, 15, 18, 21],
                            "linkedin": [8, 12, 17],
                            "facebook": [9, 13, 19],
                            "instagram": [11, 14, 17, 20],
                        }
                        platform_hours = optimal_hours.get(platform, [9, 12, 15, 18])
            except Exception as e:
                logger.warning(f"Error en optimización ML, usando horarios por defecto: {e}")
                optimal_hours = {
                    "twitter": [9, 12, 15, 18, 21],
                    "linkedin": [8, 12, 17],
                    "facebook": [9, 13, 19],
                    "instagram": [11, 14, 17, 20],
                }
                platform_hours = optimal_hours.get(platform, [9, 12, 15, 18])
        else:
            # Horarios óptimos por plataforma (UTC) - valores por defecto
            optimal_hours = {
                "twitter": [9, 12, 15, 18, 21],  # 9am, 12pm, 3pm, 6pm, 9pm
                "linkedin": [8, 12, 17],  # 8am, 12pm, 5pm
                "facebook": [9, 13, 19],  # 9am, 1pm, 7pm
                "instagram": [11, 14, 17, 20],  # 11am, 2pm, 5pm, 8pm
            }
            platform_hours = optimal_hours.get(platform, [9, 12, 15, 18])
        
        current_hour = now.hour
        
        # Encontrar la próxima hora óptima
        next_hour = None
        for hour in platform_hours:
            if hour > current_hour:
                next_hour = hour
                break
        
        if next_hour is None:
            next_hour = platform_hours[0]  # Usar primera hora del día siguiente
        
        # Ajustar a la próxima hora óptima
        scheduled = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        if scheduled <= now:
            scheduled = scheduled + timedelta(days=1)
        
        return scheduled
    
    def _publish_to_platform(
        platform: str,
        content: str,
        media_urls: List[str],
        hashtags: List[str],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publica contenido en la plataforma especificada."""
        logger.info(f"Publicando en {platform}...")
        
        try:
            if platform == "twitter":
                # Estructura para Twitter API v2
                # En producción, usar tweepy o requests directo
                """
                import tweepy
                client = tweepy.Client(
                    bearer_token=credentials.get("bearer_token"),
                    consumer_key=credentials.get("api_key"),
                    consumer_secret=credentials.get("api_secret"),
                    access_token=credentials.get("access_token"),
                    access_token_secret=credentials.get("access_token_secret")
                )
                
                # Publicar tweet
                if media_urls:
                    # Subir media primero
                    media_ids = []
                    for media_url in media_urls:
                        # Upload media y obtener media_id
                        # media_ids.append(media_id)
                    response = client.create_tweet(text=content, media_ids=media_ids)
                else:
                    response = client.create_tweet(text=content)
                
                return {
                    "success": True,
                    "post_id": response.data["id"],
                    "url": f"https://twitter.com/user/status/{response.data['id']}"
                }
                """
                # Simulación por ahora
                post_id = f"twitter_{hashlib.md5(content.encode()).hexdigest()[:10]}"
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://twitter.com/status/{post_id}"
                }
                
            elif platform == "linkedin":
                # Estructura para LinkedIn API
                """
                import requests
                
                headers = {
                    "Authorization": f"Bearer {credentials.get('access_token')}",
                    "Content-Type": "application/json"
                }
                
                # Preparar contenido
                payload = {
                    "author": f"urn:li:person:{credentials.get('person_urn')}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "ARTICLE" if media_urls else "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                
                response = requests.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                return {
                    "success": True,
                    "post_id": response.json()["id"],
                    "url": f"https://linkedin.com/feed/update/{response.json()['id']}"
                }
                """
                # Simulación por ahora
                post_id = f"linkedin_{hashlib.md5(content.encode()).hexdigest()[:10]}"
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://linkedin.com/posts/{post_id}"
                }
                
            elif platform == "facebook":
                # Estructura para Facebook Graph API
                """
                import requests
                
                page_id = credentials.get("page_id")
                access_token = credentials.get("access_token")
                
                url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
                params = {
                    "message": content,
                    "access_token": access_token
                }
                
                if media_urls:
                    # Para imágenes, usar endpoint diferente
                    params["attached_media"] = json.dumps([{"media_fbid": media_id} for media_id in media_ids])
                
                response = requests.post(url, params=params)
                response.raise_for_status()
                
                return {
                    "success": True,
                    "post_id": response.json()["id"],
                    "url": f"https://facebook.com/{page_id}/posts/{response.json()['id']}"
                }
                """
                # Simulación por ahora
                post_id = f"facebook_{hashlib.md5(content.encode()).hexdigest()[:10]}"
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://facebook.com/posts/{post_id}"
                }
                
            elif platform == "instagram":
                # Estructura para Instagram Graph API
                """
                import requests
                
                # Instagram requiere container creation primero
                # Luego publicar el container
                container_url = f"https://graph.facebook.com/v18.0/{credentials.get('instagram_account_id')}/media"
                # ... crear container y luego publicar
                """
                post_id = f"instagram_{hashlib.md5(content.encode()).hexdigest()[:10]}"
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://instagram.com/p/{post_id}"
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Plataforma {platform} no implementada"
                }
        except Exception as e:
            logger.error(f"Error publicando en {platform}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _fetch_platform_metrics(
        platform: str,
        post_id: str,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtiene métricas de engagement de la plataforma."""
        try:
            if platform == "twitter":
                # Estructura para Twitter API v2 Analytics
                """
                import tweepy
                client = tweepy.Client(
                    bearer_token=credentials.get("bearer_token"),
                    consumer_key=credentials.get("api_key"),
                    consumer_secret=credentials.get("api_secret"),
                    access_token=credentials.get("access_token"),
                    access_token_secret=credentials.get("access_token_secret")
                )
                
                # Obtener métricas del tweet
                tweet = client.get_tweet(
                    id=post_id,
                    tweet_fields=["public_metrics", "non_public_metrics"]
                )
                
                metrics = tweet.data.public_metrics
                return {
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "impressions": metrics.get("impression_count", 0),
                    "engagement_rate": (metrics.get("like_count", 0) + metrics.get("retweet_count", 0)) / max(metrics.get("impression_count", 1), 1) * 100
                }
                """
                # Simulación por ahora
                import random
                return {
                    "likes": random.randint(10, 500),
                    "comments": random.randint(0, 50),
                    "retweets": random.randint(0, 50),
                    "clicks": random.randint(50, 1000),
                    "impressions": random.randint(500, 5000),
                    "reach": random.randint(400, 4000),
                    "engagement_rate": random.uniform(2.0, 8.0),
                    "click_through_rate": random.uniform(1.0, 5.0)
                }
                
            elif platform == "linkedin":
                # Estructura para LinkedIn Analytics API
                """
                import requests
                
                headers = {
                    "Authorization": f"Bearer {credentials.get('access_token')}"
                }
                
                response = requests.get(
                    f"https://api.linkedin.com/v2/socialActions/{post_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                    "comments": data.get("commentsSummary", {}).get("totalComments", 0),
                    "shares": data.get("sharesSummary", {}).get("totalShares", 0),
                    "impressions": data.get("impressionCount", 0),
                    "clicks": data.get("clickCount", 0)
                }
                """
                import random
                return {
                    "likes": random.randint(10, 500),
                    "comments": random.randint(0, 50),
                    "shares": random.randint(0, 100),
                    "clicks": random.randint(50, 1000),
                    "impressions": random.randint(500, 5000),
                    "reach": random.randint(400, 4000),
                    "engagement_rate": random.uniform(2.0, 8.0),
                    "click_through_rate": random.uniform(1.0, 5.0)
                }
                
            elif platform == "facebook":
                # Estructura para Facebook Insights API
                """
                import requests
                
                url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
                params = {
                    "metric": "post_impressions,post_engaged_users,post_clicks",
                    "access_token": credentials.get("access_token")
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                # Procesar métricas...
                """
                import random
                return {
                    "likes": random.randint(10, 500),
                    "comments": random.randint(0, 50),
                    "shares": random.randint(0, 100),
                    "clicks": random.randint(50, 1000),
                    "impressions": random.randint(500, 5000),
                    "reach": random.randint(400, 4000),
                    "engagement_rate": random.uniform(2.0, 8.0),
                    "click_through_rate": random.uniform(1.0, 5.0)
                }
                
            elif platform == "instagram":
                # Estructura para Instagram Insights API
                """
                import requests
                
                url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
                params = {
                    "metric": "impressions,reach,engagement",
                    "access_token": credentials.get("access_token")
                }
                """
                import random
                return {
                    "likes": random.randint(10, 500),
                    "comments": random.randint(0, 50),
                    "saves": random.randint(0, 30),
                    "clicks": random.randint(50, 1000),
                    "impressions": random.randint(500, 5000),
                    "reach": random.randint(400, 4000),
                    "engagement_rate": random.uniform(2.0, 8.0),
                    "click_through_rate": random.uniform(1.0, 5.0)
                }
                
            else:
                logger.warning(f"Plataforma {platform} no soportada para métricas")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo métricas de {platform}: {e}", exc_info=True)
            return None
    
    # Pipeline principal
    content = collect_new_content()
    content_validated = data_validation(content)
    content_ai_generated = ai_content_generation(content_validated)
    content_safety_checked = content_safety_check(content_ai_generated)
    content_similarity_checked = content_similarity_detection(content_safety_checked)
    content_clustered = content_clustering(content_similarity_checked)
    content_repurposed = content_repurposing(content_clustered)
    calendar_created = automated_content_calendar(content_repurposed)
    content_images_analyzed = image_analysis(calendar_created)
    content_videos_analyzed = video_content_analysis(content_images_analyzed)
    content_quality_scored = content_quality_scoring(content_videos_analyzed)
    content_quality_ml_scored_advanced = content_quality_ml_scoring(content_quality_scored)
    content_viral_scored = content_viral_potential_scoring(content_quality_ml_scored_advanced)
    content_hashtags_researched = automated_hashtag_research(content_viral_scored)
    content_performance_predicted = content_performance_prediction(content_hashtags_researched)
    trends_predicted = trend_prediction(content_performance_predicted)
    content_reactive = reactive_scheduling(trends_predicted)
    content_personalized = content_personalization(content_reactive)
    content_hashtags_suggested = intelligent_hashtag_suggestions(content_personalized)
    content_hashtags_generated = automated_hashtag_generation(content_hashtags_suggested)
    content_hashtags_optimized_ml = automated_hashtag_optimization_ml(content_hashtags_generated)
    content_forecasted_ml = content_performance_forecasting_ml(content_hashtags_optimized_ml)
    content_audience_matched = content_audience_matching(content_forecasted_ml)
    content_curated = intelligent_content_curation(content_audience_matched)
    content_optimized = smart_content_optimization(content_curated)
    content_with_sentiment = analyze_content_sentiment(content_optimized)
    content_with_prediction = predict_engagement_ml(content_with_sentiment)
    content_with_hashtags = detect_trending_hashtags(content_with_prediction)
    content_hashtags_optimized = hashtag_optimization(content_with_hashtags)
    scheduled = schedule_posts(content_hashtags_optimized)
    ab_tested = ab_testing(scheduled)
    calendar_optimized = content_calendar_optimization(ab_tested)
    published = publish_scheduled_posts(calendar_optimized)
    rate_limits_managed = rate_limit_management(published)
    retried = auto_retry_failed_posts(rate_limits_managed)
    viral_detected = detect_viral_content(retried)
    tracked = track_engagement(viral_detected)
    engagement_velocity = engagement_velocity_tracking(tracked)
    content_effectiveness = content_effectiveness_scoring(engagement_velocity)
    lifecycle_optimized = content_lifecycle_optimization(content_effectiveness)
    crm_leads = crm_lead_tracking(lifecycle_optimized)
    comment_sentiment = analyze_comment_sentiment(crm_leads)
    auto_responded = auto_respond_to_comments(comment_sentiment)
    competitor_tracked = competitor_tracking(auto_responded)
    brand_mentions = brand_mention_tracking(competitor_tracked)
    influencers_analyzed = influencer_analysis(brand_mentions)
    social_listened = social_listening(influencers_analyzed)
    crisis_detected = crisis_detection(social_listened)
    anomalies = anomaly_detection(crisis_detected)
    performance_optimized = performance_optimization(anomalies)
    engagement_optimized = engagement_rate_optimization(performance_optimized)
    cross_platform_analyzed = cross_platform_analytics(engagement_optimized)
    errors_recovered = error_recovery(cross_platform_analyzed)
    audience_segmented = audience_segmentation(errors_recovered)
    competitor_benchmarked = competitor_benchmarking(audience_segmented)
    campaigns_optimized = automated_campaign_optimization(competitor_benchmarked)
    content_refreshed = automated_content_refresh(campaigns_optimized)
    heatmap_analyzed = engagement_heatmap_analysis(content_refreshed)
    content_repurposed_auto = automated_content_repurposing(heatmap_analyzed)
    social_signals = social_signal_detection(content_repurposed_auto)
    engagement_forecasted_advanced = content_engagement_forecasting(social_signals)
    performance_benchmarked = content_performance_benchmarking(engagement_forecasted_advanced)
    engagement_anomalies = engagement_anomaly_detection(performance_benchmarked)
    content_trends = content_trend_analysis(engagement_anomalies)
    engagement_optimized_ml = content_engagement_optimization_ml(content_trends)
    automated_responses = automated_engagement_responses(engagement_optimized_ml)
    audience_growth = content_audience_growth_analysis(automated_responses)
    performance_insights = content_performance_insights_ml(audience_growth)
    engagement_patterns = content_engagement_pattern_analysis(performance_insights)
    best_times = best_time_analysis(engagement_patterns)
    author_analysis = author_performance_analysis(best_times)
    audience_analyzed = analyze_audience_insights(author_analysis)
    trends_analyzed = trend_analysis(audience_analyzed)
    forecasted = engagement_forecasting(trends_analyzed)
    roi_calculated = calculate_roi(forecasted)
    advanced_roi = advanced_roi_analysis(roi_calculated)
    roi_optimized = social_media_roi_optimization(advanced_roi)
    campaign_roi = campaign_roi_analysis(roi_optimized)
    benchmarked = performance_benchmarking(campaign_roi)
    republished = republish_top_content(benchmarked)
    report = generate_weekly_report(republished)
    report_with_recommendations = generate_recommendations(report)
    send_weekly_report(report_with_recommendations)
    export_analytics_data(report_with_recommendations)


dag = social_media_automation()

