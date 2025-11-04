"""
Ejemplos de uso prácticos del sistema ads_reporting.

Proporciona ejemplos completos y funcionales para casos de uso comunes.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Ejemplos comentados para documentación


def example_basic_extraction():
    """
    Ejemplo básico de extracción de datos.
    
    Usage:
        from ads_reporting.examples import example_basic_extraction
        example_basic_extraction()
    """
    from ads_reporting import (
        FacebookAdsClient, FacebookAdsConfig,
        FacebookExtractor,
        get_storage
    )
    
    # Configuración
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID"),
    )
    
    # Extracción
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(
            date_start="2024-01-01",
            date_stop="2024-01-31"
        )
    
    # Almacenamiento
    storage = get_storage("postgres")
    result = storage.save_campaign_performance(data, "facebook_ads_performance")
    
    print(f"Extraídos: {len(data)} registros")
    print(f"Guardados: {result['saved']} registros")
    
    return result


def example_with_validation():
    """
    Ejemplo con validación completa.
    """
    from ads_reporting import (
        FacebookAdsClient, FacebookAdsConfig,
        FacebookExtractor,
        validate_campaign_data,
        get_storage
    )
    
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID"),
    )
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(
            date_start="2024-01-01",
            date_stop="2024-01-31"
        )
    
    # Validación
    validation = validate_campaign_data(data, strict=False)
    
    if not validation.valid:
        print(f"Errores de validación: {validation.errors[:5]}")
    
    if validation.warnings:
        print(f"Advertencias: {validation.warnings[:5]}")
    
    # Solo guardar si validación pasa
    if validation.valid:
        storage = get_storage("postgres")
        storage.save_campaign_performance(data, "facebook_ads_performance")
    
    return {"valid": validation.valid, "data": data}


def example_with_processing():
    """
    Ejemplo con procesamiento y análisis.
    """
    from ads_reporting import (
        FacebookAdsClient, FacebookAdsConfig,
        FacebookExtractor,
        CampaignProcessor,
        find_top_performers
    )
    
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID"),
    )
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(
            date_start="2024-01-01",
            date_stop="2024-01-31"
        )
    
    # Procesamiento
    processor = CampaignProcessor()
    normalized = processor.normalize(data)
    metrics = processor.calculate_metrics(normalized)
    
    # Top performers
    top = find_top_performers(normalized, metric="roas", top_n=10)
    
    print(f"ROAS promedio: {metrics.roas:.2f}")
    print(f"Top 10 campañas por ROAS:")
    for campaign in top:
        print(f"  {campaign.get('campaign_name')}: ROAS {campaign.get('roas'):.2f}")
    
    return {
        "metrics": metrics,
        "top_performers": top
    }


def example_with_optimization():
    """
    Ejemplo con análisis de optimización.
    """
    from ads_reporting import (
        quick_optimize_campaigns,
        analyze_campaign_efficiency,
        suggest_budget_reallocation
    )
    
    # Análisis rápido
    optimization = quick_optimize_campaigns(days_back=30)
    
    print("Recomendaciones:")
    for rec in optimization["recommendations"]:
        print(f"[{rec['priority']}] {rec['title']}")
        print(f"  Acción: {rec['action']}")
    
    print(f"\nDesperdicio potencial: ${optimization['waste_analysis']['total_waste_potential']:.2f}")
    
    return optimization


def example_comparison_report():
    """
    Ejemplo de reporte comparativo.
    """
    from ads_reporting import (
        quick_compare_periods,
        format_report_summary,
        create_comparison_table
    )
    
    # Comparar períodos
    comparison = quick_compare_periods(
        period1_days=7,      # Esta semana
        period2_days=7,       # Semana pasada
        period2_offset=7
    )
    
    # Crear tabla de comparación
    table = create_comparison_table(comparison["comparison"])
    print(table)
    
    return comparison


def example_complete_pipeline():
    """
    Ejemplo de pipeline completo con todas las funcionalidades.
    """
    from ads_reporting import (
        extract_and_store,
        generate_performance_report,
        format_report_summary,
        analyze_campaign_efficiency,
        export_to_csv
    )
    from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
    from ads_reporting.extractors import FacebookExtractor
    from ads_reporting.storage import get_storage
    
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID"),
    )
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        storage = get_storage("postgres")
        
        # 1. Extraer y almacenar
        result = extract_and_store(
            client, extractor, storage,
            date_start="2024-01-01",
            date_stop="2024-01-31",
            use_cache=True,
            validate=True,
            process=True
        )
        
        print(f"✓ Extraídos: {result['extracted']}")
        print(f"✓ Guardados: {result['saved']}")
        
        # 2. Generar reporte
        report = generate_performance_report(
            result.get("data", []),
            date_start="2024-01-01",
            date_stop="2024-01-31"
        )
        
        # 3. Formatear y mostrar
        summary_text = format_report_summary(report["summary"], format_type="text")
        print("\n" + summary_text)
        
        # 4. Análisis de optimización
        recommendations = analyze_campaign_efficiency(result.get("data", []))
        print(f"\n✓ Recomendaciones: {len(recommendations)}")
        
        # 5. Exportar
        csv_file = export_to_csv(result.get("data", []), filepath="report.csv")
        print(f"✓ Exportado a: {csv_file}")
        
        return {
            "extraction": result,
            "report": report,
            "recommendations": recommendations
        }


def example_airflow_integration():
    """
    Ejemplo de integración con Airflow.
    """
    from airflow.decorators import dag, task
    import pendulum
    
    from ads_reporting import (
        extract_and_store_task,
        get_date_range_from_context,
        log_task_start,
        log_task_end,
        push_to_xcom,
        pull_from_xcom
    )
    
    @dag(
        dag_id="facebook_ads_example",
        start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
        schedule="@daily",
        catchup=False
    )
    def facebook_ads_dag():
        @task
        def extract_task(**kwargs):
            log_task_start("extract_facebook_ads", **kwargs)
            
            date_start, date_stop = get_date_range_from_context(days_back=7, **kwargs)
            
            result = extract_and_store_task(
                platform="facebook",
                date_start=date_start,
                date_stop=date_stop,
                table_name="facebook_ads_performance",
                **kwargs
            )
            
            log_task_end("extract_facebook_ads", result, **kwargs)
            return result
        
        @task
        def report_task(**kwargs):
            # Pull datos de task anterior
            extraction_result = pull_from_xcom("extraction_result", **kwargs)
            
            from ads_reporting import generate_performance_report
            
            if extraction_result:
                report = generate_performance_report(
                    extraction_result.get("data", []),
                    extraction_result.get("date_start", ""),
                    extraction_result.get("date_stop", "")
                )
                
                push_to_xcom("performance_report", report, **kwargs)
                return report
            
            return None
        
        extract = extract_task()
        report = report_task()
        report.set_upstream(extract)
    
    return facebook_ads_dag


def example_with_monitoring():
    """
    Ejemplo con monitoreo y alertas.
    """
    import time
    from ads_reporting import (
        FacebookAdsClient, FacebookAdsConfig,
        FacebookExtractor,
        monitor_extraction,
        DataQualityMonitor,
        get_alert_manager
    )
    
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID"),
    )
    
    start_time = time.time()
    
    with FacebookAdsClient(config) as client:
        extractor = FacebookExtractor(client)
        data = extractor.extract_campaign_performance(
            date_start="2024-01-01",
            date_stop="2024-01-31"
        )
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Monitoreo
    alerts = monitor_extraction(
        platform="facebook",
        records_extracted=len(data),
        duration_ms=duration_ms,
        errors=0
    )
    
    # Data quality monitoring
    dq_monitor = DataQualityMonitor("facebook")
    dq_alerts = dq_monitor.check_data_quality(data, expected_min_records=10)
    
    # Enviar alertas
    if alerts or dq_alerts:
        alert_manager = get_alert_manager()
        alert_manager.send_batch_alerts(alerts + dq_alerts)
    
    return {
        "data": data,
        "alerts": alerts,
        "dq_alerts": dq_alerts
    }

