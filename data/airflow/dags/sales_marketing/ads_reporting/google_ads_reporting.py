"""
Módulo para extraer datos de rendimiento de Google Ads.

Funcionalidades:
1. Extracción de datos por palabras clave, grupos de anuncios y campañas
2. Reporte de atribución (primer clic, último clic, asistencias)
3. Análisis comparativo por dispositivo y hora del día

Variables de entorno requeridas:
- GOOGLE_ADS_CUSTOMER_ID: ID del cliente de Google Ads
- GOOGLE_ADS_CLIENT_ID: Client ID de OAuth2
- GOOGLE_ADS_CLIENT_SECRET: Client Secret de OAuth2
- GOOGLE_ADS_REFRESH_TOKEN: Refresh Token de OAuth2
- GOOGLE_ADS_DEVELOPER_TOKEN: Developer Token

Variables de entorno opcionales:
- GOOGLE_ADS_API_VERSION: Versión de la API (default: v14)
- GOOGLE_ADS_REPORT_DESTINATION: Destino para guardar reportes (s3 | postgres | local)
"""

from __future__ import annotations

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Intentar importar librería de Google Ads
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_SDK_AVAILABLE = False
    logger.warning("google-ads SDK no disponible, usando requests directo")


@dataclass
class GoogleAdsConfig:
    """Configuración para Google Ads API."""
    customer_id: str
    client_id: str
    client_secret: str
    refresh_token: str
    developer_token: str
    api_version: str = "v14"
    report_destination: str = "postgres"
    postgres_conn_id: str = "postgres_default"
    yaml_config_path: Optional[str] = None


@dataclass
class GoogleAdsKeywordData:
    """Datos de palabra clave de Google Ads."""
    date_start: str
    date_stop: str
    keyword_id: str
    keyword_text: str
    ad_group_id: str
    ad_group_name: str
    campaign_id: str
    campaign_name: str
    impressions: int
    clicks: int
    ctr: float
    avg_cpc: float
    conversions: float
    cost_per_conversion: float
    conversion_value: float
    network: str  # SEARCH_NETWORK o DISPLAY_NETWORK


def _load_google_ads_config() -> GoogleAdsConfig:
    """Carga configuración desde variables de entorno."""
    return GoogleAdsConfig(
        customer_id=os.environ.get("GOOGLE_ADS_CUSTOMER_ID", ""),
        client_id=os.environ.get("GOOGLE_ADS_CLIENT_ID", ""),
        client_secret=os.environ.get("GOOGLE_ADS_CLIENT_SECRET", ""),
        refresh_token=os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", ""),
        developer_token=os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
        api_version=os.environ.get("GOOGLE_ADS_API_VERSION", "v14"),
        report_destination=os.environ.get("GOOGLE_ADS_REPORT_DESTINATION", "postgres"),
        postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default"),
        yaml_config_path=os.environ.get("GOOGLE_ADS_YAML_CONFIG_PATH")
    )


def _get_google_ads_client(config: GoogleAdsConfig) -> Optional[Any]:
    """
    Crea cliente de Google Ads usando SDK si está disponible.
    
    Args:
        config: Configuración de Google Ads
        
    Returns:
        Cliente de Google Ads o None si no está disponible
    """
    if not GOOGLE_ADS_SDK_AVAILABLE:
        return None
    
    try:
        # Intentar cargar desde archivo YAML si existe
        if config.yaml_config_path and os.path.exists(config.yaml_config_path):
            return GoogleAdsClient.load_from_storage(config.yaml_config_path)
        
        # Crear cliente manualmente
        credentials = {
            "developer_token": config.developer_token,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": config.refresh_token,
            "use_proto_plus": True
        }
        
        return GoogleAdsClient.load_from_dict(credentials)
    except Exception as e:
        logger.error(f"Error creando cliente de Google Ads: {str(e)}")
        return None


def extract_google_ads_keyword_data(
    config: GoogleAdsConfig,
    date_start: str,
    date_stop: str
) -> List[GoogleAdsKeywordData]:
    """
    Extrae datos de palabras clave, grupos de anuncios y campañas.
    
    Args:
        config: Configuración de Google Ads
        date_start: Fecha inicio (YYYY-MM-DD)
        date_stop: Fecha fin (YYYY-MM-DD)
        
    Returns:
        Lista de datos de palabras clave
    """
    results = []
    
    if GOOGLE_ADS_SDK_AVAILABLE:
        client = _get_google_ads_client(config)
        if client:
            try:
                ga_service = client.get_service("GoogleAdsService")
                
                query = f"""
                SELECT
                    keyword_view.resource_name,
                    keyword_view.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversions,
                    metrics.cost_per_conversion,
                    metrics.conversions_value,
                    campaign.advertising_channel_type,
                    segments.date
                FROM keyword_view
                WHERE segments.date >= '{date_start}' AND segments.date <= '{date_stop}'
                    AND campaign.advertising_channel_type = 'SEARCH'
                ORDER BY segments.date, campaign.id, ad_group.id
                """
                
                customer_id = config.customer_id.replace("-", "")
                response = ga_service.search(customer_id=customer_id, query=query)
                
                for row in response:
                    try:
                        keyword_data = GoogleAdsKeywordData(
                            date_start=date_start,
                            date_stop=date_stop,
                            keyword_id=str(row.keyword_view.criterion_id),
                            keyword_text=row.ad_group_criterion.keyword.text,
                            ad_group_id=str(row.ad_group.id),
                            ad_group_name=row.ad_group.name,
                            campaign_id=str(row.campaign.id),
                            campaign_name=row.campaign.name,
                            impressions=int(row.metrics.impressions),
                            clicks=int(row.metrics.clicks),
                            ctr=float(row.metrics.ctr),
                            avg_cpc=float(row.metrics.average_cpc) / 1_000_000,  # Convertir de micros
                            conversions=float(row.metrics.conversions),
                            cost_per_conversion=float(row.metrics.cost_per_conversion) / 1_000_000 if row.metrics.cost_per_conversion else 0,
                            conversion_value=float(row.metrics.conversions_value) / 1_000_000 if row.metrics.conversions_value else 0,
                            network="SEARCH_NETWORK" if "SEARCH" in str(row.campaign.advertising_channel_type) else "DISPLAY_NETWORK"
                        )
                        results.append(keyword_data)
                    except Exception as e:
                        logger.warning(f"Error procesando fila: {str(e)}")
                        continue
                
                logger.info(f"Extraídos {len(results)} registros usando Google Ads SDK")
                return results
                
            except GoogleAdsException as e:
                logger.error(f"Error de Google Ads API: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error extrayendo datos: {str(e)}")
                raise
    
    # Fallback: usar API REST si SDK no está disponible
    logger.warning("Google Ads SDK no disponible, usando método alternativo")
    
    # Nota: La API REST de Google Ads requiere autenticación OAuth2 compleja
    # Por ahora, retornamos lista vacía y el usuario debe usar el SDK
    logger.error("Google Ads SDK es requerido para extraer datos. Por favor instala: pip install google-ads")
    return []


def extract_google_ads_attribution(
    config: GoogleAdsConfig,
    date_start: str,
    date_stop: str
) -> Dict[str, Any]:
    """
    Genera reporte de atribución mostrando caminos de conversión.
    
    Args:
        config: Configuración de Google Ads
        date_start: Fecha inicio
        date_stop: Fecha fin
        
    Returns:
        Diccionario con datos de atribución
    """
    if not GOOGLE_ADS_SDK_AVAILABLE:
        logger.error("Google Ads SDK es requerido para atribución")
        return {}
    
    client = _get_google_ads_client(config)
    if not client:
        return {}
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        customer_id = config.customer_id.replace("-", "")
        
        # Query para datos de atribución
        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros,
            metrics.search_impression_share,
            attribution_metrics.all_conversions,
            attribution_metrics.all_conversions_from_interactions_rate,
            attribution_metrics.all_conversions_value,
            segments.conversion_action_category,
            segments.conversion_action_name,
            customer.descriptive_name
        FROM campaign
        WHERE segments.date >= '{date_start}' AND segments.date <= '{date_stop}'
        ORDER BY metrics.conversions DESC
        """
        
        response = ga_service.search(customer_id=customer_id, query=query)
        
        campaigns = []
        total_first_click_conversions = 0
        total_last_click_conversions = 0
        total_assisted_conversions = 0
        total_cost = 0
        
        for row in response:
            campaign_id = str(row.campaign.id)
            conversions = float(row.metrics.conversions)
            all_conversions = float(row.attribution_metrics.all_conversions) if hasattr(row, 'attribution_metrics') else conversions
            cost = float(row.metrics.cost_micros) / 1_000_000
            
            # En Google Ads, las conversiones son por último clic por defecto
            last_click_conversions = conversions
            assisted_conversions = all_conversions - conversions if all_conversions > conversions else 0
            first_click_conversions = 0  # Se requiere configuración especial para obtener esto
            
            total_last_click_conversions += last_click_conversions
            total_assisted_conversions += assisted_conversions
            total_cost += cost
            
            campaigns.append({
                "campaign_id": campaign_id,
                "campaign_name": row.campaign.name,
                "impressions": int(row.metrics.impressions),
                "clicks": int(row.metrics.clicks),
                "last_click_conversions": last_click_conversions,
                "assisted_conversions": assisted_conversions,
                "first_click_conversions": first_click_conversions,
                "all_conversions": all_conversions,
                "cost": cost,
                "cost_per_acquisition": (cost / all_conversions) if all_conversions > 0 else 0
            })
        
        # Obtener canal de inicio del usuario (primer clic)
        query_first_click = f"""
        SELECT
            campaign.id,
            campaign.name,
            segments.date,
            attribution_metrics.all_conversions_from_interactions_rate
        FROM campaign
        WHERE segments.date >= '{date_start}' AND segments.date <= '{date_stop}'
        """
        
        try:
            first_click_response = ga_service.search(customer_id=customer_id, query=query_first_click)
            for row in first_click_response:
                campaign_id = str(row.campaign.id)
                # Buscar en campaigns y actualizar first_click_conversions
                for camp in campaigns:
                    if camp["campaign_id"] == campaign_id:
                        # Aproximación: usar tasa de conversión desde interacciones
                        if hasattr(row, 'attribution_metrics'):
                            rate = float(row.attribution_metrics.all_conversions_from_interactions_rate)
                            camp["first_click_conversions"] = camp["all_conversions"] * rate
                            total_first_click_conversions += camp["first_click_conversions"]
                        break
        except Exception as e:
            logger.warning(f"Error obteniendo datos de primer clic: {str(e)}")
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "total_campaigns": len(campaigns),
            "total_cost": total_cost,
            "total_last_click_conversions": total_last_click_conversions,
            "total_first_click_conversions": total_first_click_conversions,
            "total_assisted_conversions": total_assisted_conversions,
            "campaigns": campaigns,
            "attribution_summary": {
                "avg_cost_per_last_click": (total_cost / total_last_click_conversions) if total_last_click_conversions > 0 else 0,
                "avg_cost_per_first_click": (total_cost / total_first_click_conversions) if total_first_click_conversions > 0 else 0,
                "assisted_conversions_ratio": (total_assisted_conversions / total_last_click_conversions * 100) if total_last_click_conversions > 0 else 0
            }
        }
        
    except GoogleAdsException as e:
        logger.error(f"Error en atribución de Google Ads: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error extrayendo atribución: {str(e)}")
        raise


def extract_google_ads_device_time_performance(
    config: GoogleAdsConfig,
    date_start: str,
    date_stop: str
) -> Dict[str, Any]:
    """
    Extrae rendimiento por dispositivo y hora del día.
    
    Args:
        config: Configuración de Google Ads
        date_start: Fecha inicio
        date_stop: Fecha fin
        
    Returns:
        Diccionario con análisis por dispositivo y tiempo
    """
    if not GOOGLE_ADS_SDK_AVAILABLE:
        logger.error("Google Ads SDK es requerido")
        return {}
    
    client = _get_google_ads_client(config)
    if not client:
        return {}
    
    try:
        ga_service = client.get_service("GoogleAdsService")
        customer_id = config.customer_id.replace("-", "")
        
        # Query para dispositivo
        query_device = f"""
        SELECT
            campaign.id,
            campaign.name,
            segments.device,
            segments.date,
            segments.day_of_week,
            segments.hour,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date >= '{date_start}' AND segments.date <= '{date_stop}'
        ORDER BY segments.device, segments.hour, segments.day_of_week
        """
        
        response = ga_service.search(customer_id=customer_id, query=query_device)
        
        device_stats = {}
        time_stats = {}
        
        for row in response:
            device = str(row.segments.device)
            hour = int(row.segments.hour) if hasattr(row.segments, 'hour') else None
            day_of_week = str(row.segments.day_of_week) if hasattr(row.segments, 'day_of_week') else None
            
            impressions = int(row.metrics.impressions)
            clicks = int(row.metrics.clicks)
            conversions = float(row.metrics.conversions)
            cost = float(row.metrics.cost_micros) / 1_000_000
            
            # Agrupar por dispositivo
            if device not in device_stats:
                device_stats[device] = {
                    "device": device,
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "cost": 0
                }
            
            device_stats[device]["impressions"] += impressions
            device_stats[device]["clicks"] += clicks
            device_stats[device]["conversions"] += conversions
            device_stats[device]["cost"] += cost
            
            # Agrupar por hora y día
            if hour is not None:
                hour_key = f"hour_{hour}"
                if hour_key not in time_stats:
                    time_stats[hour_key] = {
                        "hour": hour,
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "cost": 0
                    }
                
                time_stats[hour_key]["impressions"] += impressions
                time_stats[hour_key]["clicks"] += clicks
                time_stats[hour_key]["conversions"] += conversions
                time_stats[hour_key]["cost"] += cost
            
            if day_of_week:
                day_key = f"day_{day_of_week}"
                if day_key not in time_stats:
                    time_stats[day_key] = {
                        "day_of_week": day_of_week,
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "cost": 0
                    }
                
                time_stats[day_key]["impressions"] += impressions
                time_stats[day_key]["clicks"] += clicks
                time_stats[day_key]["conversions"] += conversions
                time_stats[day_key]["cost"] += cost
        
        # Calcular métricas por dispositivo
        device_analysis = []
        for device, stats in device_stats.items():
            conversions = stats["conversions"]
            cost = stats["cost"]
            clicks = stats["clicks"]
            
            device_analysis.append({
                "device": device,
                "impressions": stats["impressions"],
                "clicks": stats["clicks"],
                "conversions": conversions,
                "cost": cost,
                "ctr": (clicks / stats["impressions"] * 100) if stats["impressions"] > 0 else 0,
                "cost_per_conversion": (cost / conversions) if conversions > 0 else 0,
                "conversion_rate": (conversions / clicks * 100) if clicks > 0 else 0
            })
        
        # Calcular métricas por hora
        hour_analysis = []
        for key, stats in time_stats.items():
            if key.startswith("hour_"):
                conversions = stats["conversions"]
                cost = stats["cost"]
                
                hour_analysis.append({
                    "hour": stats["hour"],
                    "impressions": stats["impressions"],
                    "clicks": stats["clicks"],
                    "conversions": conversions,
                    "cost": cost,
                    "cost_per_conversion": (cost / conversions) if conversions > 0 else 0,
                    "conversion_rate": (conversions / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
                })
        
        # Calcular métricas por día de semana
        day_analysis = []
        for key, stats in time_stats.items():
            if key.startswith("day_"):
                conversions = stats["conversions"]
                cost = stats["cost"]
                
                day_analysis.append({
                    "day_of_week": stats["day_of_week"],
                    "impressions": stats["impressions"],
                    "clicks": stats["clicks"],
                    "conversions": conversions,
                    "cost": cost,
                    "cost_per_conversion": (cost / conversions) if conversions > 0 else 0,
                    "conversion_rate": (conversions / stats["clicks"] * 100) if stats["clicks"] > 0 else 0
                })
        
        # Identificar mejores horas y dispositivos
        device_analysis.sort(key=lambda x: (x["conversions"], -x["cost_per_conversion"]), reverse=True)
        best_devices = device_analysis[:3]
        worst_devices = sorted(device_analysis[-3:], key=lambda x: x["cost_per_conversion"]) if len(device_analysis) > 3 else []
        
        hour_analysis.sort(key=lambda x: (x["conversions"], -x["cost_per_conversion"]), reverse=True)
        best_hours = hour_analysis[:5]
        
        day_analysis.sort(key=lambda x: (x["conversions"], -x["cost_per_conversion"]), reverse=True)
        best_days = day_analysis[:3]
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "devices": device_analysis,
            "best_devices": best_devices,
            "worst_devices": worst_devices,
            "hours": hour_analysis,
            "best_hours": best_hours,
            "days": day_analysis,
            "best_days": best_days,
            "optimization_suggestions": {
                "increase_bids_devices": [d["device"] for d in best_devices],
                "decrease_bids_devices": [d["device"] for d in worst_devices],
                "increase_bids_hours": [h["hour"] for h in best_hours],
                "best_days_of_week": [d["day_of_week"] for d in best_days]
            }
        }
        
    except GoogleAdsException as e:
        logger.error(f"Error en análisis de dispositivo/hora: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error extrayendo datos de dispositivo/hora: {str(e)}")
        raise


@dag(
    dag_id="google_ads_reporting",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 8 * * *",  # Diario a las 8 AM
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    doc_md="""
    ### Google Ads Reporting
    
    Extrae y analiza datos de rendimiento de campañas de Google Ads.
    
    **Funcionalidades:**
    1. Extracción de datos por palabras clave, grupos de anuncios y campañas
    2. Reporte de atribución (primer clic, último clic, asistencias)
    3. Análisis comparativo por dispositivo y hora del día
    
    **Parámetros:**
    - `date_start`: Fecha inicio (YYYY-MM-DD)
    - `date_stop`: Fecha fin (YYYY-MM-DD)
    - `extract_keywords`: Extraer datos de palabras clave (default: true)
    - `analyze_attribution`: Analizar atribución (default: true)
    - `analyze_device_time`: Analizar por dispositivo/hora (default: true)
    
    **Requisitos:**
    - Instalar Google Ads SDK: `pip install google-ads`
    - Configurar OAuth2 con Google Ads API
    - Tener Developer Token activado
    """,
    params={
        "date_start": Param("", type="string"),
        "date_stop": Param("", type="string"),
        "extract_keywords": Param(True, type="boolean"),
        "analyze_attribution": Param(True, type="boolean"),
        "analyze_device_time": Param(True, type="boolean"),
    },
    tags=["marketing", "google-ads", "reporting"],
)
def google_ads_reporting():
    """DAG principal para reporting de Google Ads."""
    
    config = _load_google_ads_config()
    
    @task(task_id="extract_keyword_data")
    def extract_keyword_data(**context):
        """Extrae datos de palabras clave."""
        params = context.get("params", {})
        
        if not params.get("extract_keywords", True):
            logger.info("Extracción de palabras clave deshabilitada")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Extrayendo datos de palabras clave desde {date_start} hasta {date_stop}")
        
        keyword_data = extract_google_ads_keyword_data(
            config=config,
            date_start=date_start,
            date_stop=date_stop
        )
        
        if not keyword_data:
            logger.warning("No se pudieron extraer datos. Verificar que Google Ads SDK esté instalado.")
            return {"records_extracted": 0, "error": "SDK no disponible"}
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS google_ads_keywords (
                date_start DATE,
                date_stop DATE,
                keyword_id VARCHAR(255),
                keyword_text TEXT,
                ad_group_id VARCHAR(255),
                ad_group_name TEXT,
                campaign_id VARCHAR(255),
                campaign_name TEXT,
                impressions INTEGER,
                clicks INTEGER,
                ctr DECIMAL(10, 4),
                avg_cpc DECIMAL(10, 4),
                conversions DECIMAL(10, 2),
                cost_per_conversion DECIMAL(10, 2),
                conversion_value DECIMAL(10, 2),
                network VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_ga_keyword_date ON google_ads_keywords(date_start, date_stop);
            CREATE INDEX IF NOT EXISTS idx_ga_keyword_campaign ON google_ads_keywords(campaign_id);
            """
            hook.run(create_table_sql)
            
            for kw in keyword_data:
                insert_sql = """
                INSERT INTO google_ads_keywords
                (date_start, date_stop, keyword_id, keyword_text, ad_group_id, ad_group_name,
                 campaign_id, campaign_name, impressions, clicks, ctr, avg_cpc, conversions,
                 cost_per_conversion, conversion_value, network)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    kw.date_start, kw.date_stop, kw.keyword_id, kw.keyword_text,
                    kw.ad_group_id, kw.ad_group_name, kw.campaign_id, kw.campaign_name,
                    kw.impressions, kw.clicks, kw.ctr, kw.avg_cpc, kw.conversions,
                    kw.cost_per_conversion, kw.conversion_value, kw.network
                ))
        
        logger.info(f"Extraídos {len(keyword_data)} registros de palabras clave")
        return {"records_extracted": len(keyword_data)}
    
    @task(task_id="analyze_attribution")
    def analyze_attribution(**context):
        """Analiza atribución de conversiones."""
        params = context.get("params", {})
        
        if not params.get("analyze_attribution", True):
            logger.info("Análisis de atribución deshabilitado")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Analizando atribución desde {date_start} hasta {date_stop}")
        
        attribution_data = extract_google_ads_attribution(
            config=config,
            date_start=date_start,
            date_stop=date_stop
        )
        
        if not attribution_data:
            logger.warning("No se pudieron extraer datos de atribución")
            return {"error": "No data"}
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS google_ads_attribution (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                campaign_id VARCHAR(255),
                campaign_name TEXT,
                impressions INTEGER,
                clicks INTEGER,
                last_click_conversions DECIMAL(10, 2),
                assisted_conversions DECIMAL(10, 2),
                first_click_conversions DECIMAL(10, 2),
                all_conversions DECIMAL(10, 2),
                cost DECIMAL(10, 2),
                cost_per_acquisition DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_ga_attribution_date ON google_ads_attribution(date_start);
            CREATE INDEX IF NOT EXISTS idx_ga_attribution_campaign ON google_ads_attribution(campaign_id);
            """
            hook.run(create_table_sql)
            
            for campaign in attribution_data.get("campaigns", []):
                insert_sql = """
                INSERT INTO google_ads_attribution
                (date_start, date_stop, campaign_id, campaign_name, impressions, clicks,
                 last_click_conversions, assisted_conversions, first_click_conversions,
                 all_conversions, cost, cost_per_acquisition)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    attribution_data["date_start"], attribution_data["date_stop"],
                    campaign["campaign_id"], campaign["campaign_name"],
                    campaign["impressions"], campaign["clicks"],
                    campaign["last_click_conversions"], campaign["assisted_conversions"],
                    campaign["first_click_conversions"], campaign["all_conversions"],
                    campaign["cost"], campaign["cost_per_acquisition"]
                ))
        
        summary = attribution_data.get("attribution_summary", {})
        logger.info(f"Análisis de atribución completado")
        logger.info(f"Conversiones último clic: {attribution_data.get('total_last_click_conversions', 0)}")
        logger.info(f"Conversiones asistidas: {attribution_data.get('total_assisted_conversions', 0)}")
        
        return {
            "total_campaigns": attribution_data.get("total_campaigns", 0),
            "last_click_conversions": attribution_data.get("total_last_click_conversions", 0),
            "assisted_conversions": attribution_data.get("total_assisted_conversions", 0),
            "avg_cpa": summary.get("avg_cost_per_last_click", 0)
        }
    
    @task(task_id="analyze_device_time_performance")
    def analyze_device_time_performance(**context):
        """Analiza rendimiento por dispositivo y hora."""
        params = context.get("params", {})
        
        if not params.get("analyze_device_time", True):
            logger.info("Análisis de dispositivo/hora deshabilitado")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Analizando dispositivo y hora desde {date_start} hasta {date_stop}")
        
        device_time_data = extract_google_ads_device_time_performance(
            config=config,
            date_start=date_start,
            date_stop=date_stop
        )
        
        if not device_time_data:
            logger.warning("No se pudieron extraer datos de dispositivo/hora")
            return {"error": "No data"}
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            # Tabla para dispositivos
            create_device_table_sql = """
            CREATE TABLE IF NOT EXISTS google_ads_device_performance (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                device VARCHAR(50),
                impressions INTEGER,
                clicks INTEGER,
                conversions DECIMAL(10, 2),
                cost DECIMAL(10, 2),
                ctr DECIMAL(10, 4),
                cost_per_conversion DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_ga_device_date ON google_ads_device_performance(date_start);
            """
            hook.run(create_device_table_sql)
            
            for device in device_time_data.get("devices", []):
                insert_sql = """
                INSERT INTO google_ads_device_performance
                (date_start, date_stop, device, impressions, clicks, conversions,
                 cost, ctr, cost_per_conversion, conversion_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    device_time_data["date_start"], device_time_data["date_stop"],
                    device["device"], device["impressions"], device["clicks"],
                    device["conversions"], device["cost"], device["ctr"],
                    device["cost_per_conversion"], device["conversion_rate"]
                ))
            
            # Tabla para horas
            create_hour_table_sql = """
            CREATE TABLE IF NOT EXISTS google_ads_hour_performance (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                hour INTEGER,
                impressions INTEGER,
                clicks INTEGER,
                conversions DECIMAL(10, 2),
                cost DECIMAL(10, 2),
                cost_per_conversion DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_ga_hour_date ON google_ads_hour_performance(date_start);
            """
            hook.run(create_hour_table_sql)
            
            for hour in device_time_data.get("hours", []):
                insert_sql = """
                INSERT INTO google_ads_hour_performance
                (date_start, date_stop, hour, impressions, clicks, conversions,
                 cost, cost_per_conversion, conversion_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    device_time_data["date_start"], device_time_data["date_stop"],
                    hour["hour"], hour["impressions"], hour["clicks"],
                    hour["conversions"], hour["cost"], hour["cost_per_conversion"],
                    hour["conversion_rate"]
                ))
        
        suggestions = device_time_data.get("optimization_suggestions", {})
        logger.info(f"Mejores dispositivos: {suggestions.get('increase_bids_devices', [])}")
        logger.info(f"Mejores horas: {suggestions.get('increase_bids_hours', [])}")
        
        return {
            "devices_analyzed": len(device_time_data.get("devices", [])),
            "hours_analyzed": len(device_time_data.get("hours", [])),
            "best_devices": [d["device"] for d in device_time_data.get("best_devices", [])],
            "best_hours": [h["hour"] for h in device_time_data.get("best_hours", [])]
        }
    
    # Ejecutar tasks
    keywords = extract_keyword_data()
    attribution = analyze_attribution()
    device_time = analyze_device_time_performance()


dag = google_ads_reporting()


