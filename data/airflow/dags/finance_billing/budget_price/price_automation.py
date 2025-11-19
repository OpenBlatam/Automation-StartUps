"""
DAG de Automatización de Actualización de Precios en Catálogos

Este DAG ejecuta diariamente:
1. Extracción de precios de competencia/mercado
2. Análisis y ajuste de precios propios
3. Publicación de catálogo actualizado

Autor: Sistema de Automatización
Fecha: 2024
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
import os

# Agregar el directorio de plugins al path
plugins_dir = os.path.join(os.path.dirname(__file__), '../plugins')
if plugins_dir not in sys.path:
    sys.path.insert(0, plugins_dir)

from price_extraction import PriceExtractor
from price_analyzer import PriceAnalyzer
from catalog_publisher import CatalogPublisher
from price_config import PriceConfig
from price_cache import PriceCache
from price_history import PriceHistory
from price_alerting import PriceAlerting
from price_metrics import PriceMetrics
from price_circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
from price_currency import CurrencyConverter
from price_optimizer import PriceOptimizer
from price_reports import PriceReportGenerator
from price_validation import PriceValidator
from price_ml import PriceMLPredictor
from price_ab_testing import PriceABTesting
from price_api import PriceAPI
from price_competitor_analysis import CompetitorAnalyzer
from price_export import PriceExporter
from price_versioning import PriceVersioning
from price_webhooks import PriceWebhooks
from price_business_rules import PriceBusinessRules
from price_database import PriceDatabase
from price_sentiment import PriceSentimentAnalyzer
from price_demand_forecast import DemandForecaster
from price_recommendations import PriceRecommendationEngine
from price_multi_objective import MultiObjectiveOptimizer

# Intentar cargar configuración desde archivo o usar defaults
config_path = os.getenv('PRICE_AUTOMATION_CONFIG')
if not config_path:
    # Buscar en ubicación estándar
    default_config_path = os.path.join(os.path.dirname(__file__), '../config/price_automation_config.yaml')
    if os.path.exists(default_config_path):
        config_path = default_config_path

try:
    config = PriceConfig(config_path) if config_path else PriceConfig()
except Exception as e:
    print(f"Advertencia: No se pudo cargar configuración desde archivo: {e}")
    print("Usando configuración por defecto")
    config = PriceConfig()

# Inicializar sistemas de soporte
cache_config = config.to_dict()
cache = PriceCache(cache_config)
history = PriceHistory(cache_config)
alerting = PriceAlerting(cache_config)
metrics = PriceMetrics(cache_config)

# Inicializar sistemas avanzados
currency_converter = CurrencyConverter(cache_config) if cache_config.get('enable_currency_conversion', False) else None
price_optimizer = PriceOptimizer(cache_config) if cache_config.get('enable_price_optimization', False) else None
report_generator = PriceReportGenerator(cache_config)
price_validator = PriceValidator(cache_config)
ml_predictor = PriceMLPredictor(cache_config) if cache_config.get('enable_ml_predictions', False) else None
ab_testing = PriceABTesting(cache_config) if cache_config.get('enable_ab_testing', False) else None
competitor_analyzer = CompetitorAnalyzer(cache_config)
price_exporter = PriceExporter(cache_config)
price_api = PriceAPI(cache_config) if cache_config.get('enable_api', False) else None
price_versioning = PriceVersioning(cache_config) if cache_config.get('enable_versioning', False) else None
price_webhooks = PriceWebhooks(cache_config) if cache_config.get('enable_webhooks', False) else None
business_rules = PriceBusinessRules(cache_config) if cache_config.get('enable_business_rules', False) else None
price_database = PriceDatabase(cache_config) if cache_config.get('enable_database', False) else None
sentiment_analyzer = PriceSentimentAnalyzer(cache_config) if cache_config.get('enable_sentiment_analysis', False) else None
demand_forecaster = DemandForecaster(cache_config) if cache_config.get('enable_demand_forecast', False) else None
recommendation_engine = PriceRecommendationEngine(cache_config) if cache_config.get('enable_recommendations', False) else None
multi_objective_optimizer = MultiObjectiveOptimizer(cache_config) if cache_config.get('enable_multi_objective', False) else None

# Configurar dependencias de API si está habilitada
if price_api:
    price_api.set_dependencies(
        history=history,
        metrics=metrics,
        alerting=alerting,
        report_generator=report_generator
    )

# Circuit breakers para APIs
circuit_breaker_config = CircuitBreakerConfig(
    failure_threshold=cache_config.get('circuit_breaker_failures', 5),
    timeout_seconds=cache_config.get('circuit_breaker_timeout', 60)
)

# Configuración por defecto
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# Configuración del DAG
dag = DAG(
    'price_automation_daily',
    default_args=default_args,
    description='Automatización diaria de actualización de precios en catálogos (Mejorado)',
    schedule_interval='0 2 * * *',  # Ejecuta diariamente a las 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['pricing', 'automation', 'catalog', 'daily', 'improved'],
)

# Instancias de los módulos con mejoras integradas
extractor = PriceExtractor(
    config,
    cache=cache,
    circuit_breaker_config=circuit_breaker_config
)
analyzer = PriceAnalyzer(config, history=history)
publisher = CatalogPublisher(config)


def extract_competitor_prices(**context):
    """
    Extrae precios de competencia y mercado
    """
    execution_date = context['execution_date']
    op_id = metrics.start_operation('extract_competitor_prices')
    
    print(f"Iniciando extracción de precios de competencia - {execution_date}")
    
    try:
        # Extraer precios de múltiples fuentes
        competitor_prices = extractor.extract_all_competitor_prices()
        
        # Evaluar alertas
        alert_data = {
            'competitor_prices_count': len(competitor_prices),
            'extraction_failures': extractor.extraction_failures,
        }
        alerts = alerting.evaluate(alert_data)
        
        # Guardar resultados para siguiente paso
        context['ti'].xcom_push(key='competitor_prices', value=competitor_prices)
        context['ti'].xcom_push(key='extraction_alerts', value=alerts)
        
        # Finalizar métricas
        metrics.end_operation(
            op_id,
            success=True,
            items_processed=len(competitor_prices),
            metadata={'failures': extractor.extraction_failures}
        )
        
        print(f"Extracción completada: {len(competitor_prices)} productos encontrados")
        if alerts:
            print(f"Alertas generadas: {len(alerts)}")
        
        return competitor_prices
        
    except Exception as e:
        metrics.end_operation(op_id, success=False, errors=[str(e)])
        alerting.evaluate({'extraction_failures': extractor.extraction_failures + 1})
        print(f"Error en extracción de precios: {str(e)}")
        raise


def analyze_and_adjust_prices(**context):
    """
    Analiza precios actuales vs mercado y calcula ajustes
    """
    execution_date = context['execution_date']
    op_id = metrics.start_operation('analyze_and_adjust_prices')
    
    print(f"Iniciando análisis y ajuste de precios - {execution_date}")
    
    try:
        # Obtener precios de competencia del paso anterior
        ti = context['ti']
        competitor_prices = ti.xcom_pull(key='competitor_prices', task_ids='extract_competitor_prices')
        
        if not competitor_prices:
            raise ValueError("No se obtuvieron precios de competencia")
        
        # Obtener precios actuales del catálogo
        current_prices = extractor.get_current_catalog_prices()
        
        # Analizar y calcular ajustes
        price_adjustments = analyzer.calculate_price_adjustments(
            current_prices=current_prices,
            competitor_prices=competitor_prices
        )
        
        # Validar ajustes antes de aplicarlos
        validated_adjustments = analyzer.validate_adjustments(price_adjustments)
        
        # Validación avanzada adicional
        for adjustment in validated_adjustments:
            validation_context = {
                'current_price': adjustment.get('current_price', 0),
                'price_change_percent': adjustment.get('price_change_percent', 0),
                'max_price_change_percent': config.get('max_price_change_percent', 20),
                'cost': adjustment.get('cost'),  # Si está disponible
                'min_margin': config.get('min_margin', 0.20),
            }
            
            is_valid, errors, analysis = price_validator.validate_price_adjustment(
                adjustment.get('current_price', 0),
                adjustment.get('new_price', 0),
                validation_context
            )
            
            if not is_valid:
                logger.warning(
                    f"Validación fallida para {adjustment.get('product_name')}: {errors}"
                )
                # Marcar para revisión manual
                adjustment['validation_status'] = 'failed'
                adjustment['validation_errors'] = errors
            else:
                adjustment['validation_status'] = 'passed'
                if analysis.get('warnings'):
                    adjustment['validation_warnings'] = analysis['warnings']
        
        # Calcular métricas de cambios
        extreme_changes = [
            adj for adj in validated_adjustments
            if abs(adj.get('price_change_percent', 0)) > config.get('extreme_change_threshold', 30)
        ]
        
        # Evaluar alertas
        if extreme_changes:
            for change in extreme_changes:
                alert_data = {
                    'product_name': change.get('product_name', 'Unknown'),
                    'price_change_percent': change.get('price_change_percent', 0),
                }
                alerting.evaluate(alert_data)
        
        # Guardar ajustes para siguiente paso
        ti.xcom_push(key='price_adjustments', value=validated_adjustments)
        
        # Finalizar métricas
        metrics.end_operation(
            op_id,
            success=True,
            items_processed=len(validated_adjustments),
            metadata={
                'extreme_changes': len(extreme_changes),
                'total_changes': len([a for a in validated_adjustments if a.get('price_change', 0) != 0])
            }
        )
        
        print(f"Análisis completado: {len(validated_adjustments)} productos con ajustes")
        if extreme_changes:
            print(f"⚠️ {len(extreme_changes)} cambios extremos detectados")
        
        return validated_adjustments
        
    except Exception as e:
        metrics.end_operation(op_id, success=False, errors=[str(e)])
        print(f"Error en análisis de precios: {str(e)}")
        raise


def publish_catalog_update(**context):
    """
    Publica el catálogo actualizado con los nuevos precios
    """
    execution_date = context['execution_date']
    op_id = metrics.start_operation('publish_catalog')
    
    print(f"Iniciando publicación de catálogo actualizado - {execution_date}")
    
    try:
        # Obtener ajustes de precios del paso anterior
        ti = context['ti']
        price_adjustments = ti.xcom_pull(key='price_adjustments', task_ids='analyze_and_adjust_prices')
        
        if not price_adjustments:
            raise ValueError("No se obtuvieron ajustes de precios para publicar")
        
        # Aplicar ajustes al catálogo
        updated_catalog = publisher.apply_price_adjustments(price_adjustments)
        
        # Validar catálogo actualizado
        validation_result = publisher.validate_catalog(updated_catalog)
        
        # Evaluar alertas de validación
        if not validation_result['valid']:
            alert_data = {
                'validation_passed': False,
                'validation_errors': validation_result.get('errors', [])
            }
            alerting.evaluate(alert_data)
            raise ValueError(f"Validación fallida: {validation_result['errors']}")
        
        # Publicar catálogo
        publish_result = publisher.publish_catalog(updated_catalog)
        
        # Evaluar alertas de publicación
        if not publish_result.get('success', False):
            alert_data = {
                'publish_success': False,
                'publish_error': 'Publicación falló'
            }
            alerting.evaluate(alert_data)
        
        # Registrar resultados
        publisher.log_publish_results(publish_result, execution_date)
        
        # Finalizar métricas
        metrics.end_operation(
            op_id,
            success=publish_result.get('success', False),
            items_processed=publish_result.get('products_updated', 0),
            metadata={
                'total_products': publish_result.get('total_products', 0),
                'publish_method': publish_result.get('method', 'unknown')
            }
        )
        
        print(f"Publicación completada: {publish_result['products_updated']} productos actualizados")
        return publish_result
        
    except Exception as e:
        metrics.end_operation(op_id, success=False, errors=[str(e)])
        alert_data = {
            'publish_success': False,
            'publish_error': str(e)
        }
        alerting.evaluate(alert_data)
        print(f"Error en publicación de catálogo: {str(e)}")
        raise


def send_notification(**context):
    """
    Envía notificación con resumen de la ejecución
    """
    try:
        ti = context['ti']
        # Obtener resultado directamente del return de la tarea anterior
        publish_result = ti.xcom_pull(task_ids='publish_catalog_update')
        
        # Obtener resumen de alertas
        alerts_summary = alerting.get_alerts_summary()
        
        # Obtener reporte de métricas
        metrics_report = metrics.get_performance_report()
        
        if publish_result:
            products_updated = publish_result.get('products_updated', 0)
            total_products = publish_result.get('total_products', 0)
            
            message = f"""
            ============================================
            Actualización de Precios Completada
            ============================================
            
            Productos actualizados: {products_updated}
            Total de productos: {total_products}
            Fecha de ejecución: {context['execution_date']}
            Estado: {'Éxito' if publish_result.get('success', False) else 'Con advertencias'}
            
            Alertas: {alerts_summary.get('total', 0)}
            Métricas: {metrics_report.get('completed_operations', 0)} operaciones completadas
            
            ============================================
            """
            print(message)
            
            # Enviar notificación a Slack si está configurado
            slack_webhook = config.get('slack_webhook_url') or os.getenv('SLACK_WEBHOOK_URL')
            if slack_webhook:
                from price_alerting import notify_slack
                notify_slack(message, slack_webhook)
        else:
            print("No se obtuvo resultado de publicación para notificar")
        
        # Limpiar historial antiguo
        history.cleanup_old_history()
        
        # Limpiar métricas antiguas
        metrics.clear_old_metrics(days=7)
        
        # Generar reporte de ejecución
        try:
            extraction_result = {
                'competitor_prices_count': len(ti.xcom_pull(key='competitor_prices', task_ids='extract_competitor_prices') or []),
                'failures': extractor.extraction_failures,
            }
            analysis_result = {
                'adjustments_count': len(ti.xcom_pull(key='price_adjustments', task_ids='analyze_and_adjust_prices') or []),
            }
            alerts_data = alerting.get_alerts_summary()
            metrics_data = metrics.get_performance_report()
            
            execution_report = report_generator.generate_execution_report(
                execution_date=context['execution_date'],
                extraction_result=extraction_result,
                analysis_result=analysis_result,
                publish_result=publish_result or {},
                alerts=alerting.alerts,
                metrics=metrics_data
            )
            
            print(f"Reporte de ejecución generado: {execution_report.get('summary', {}).get('status', 'unknown')}")
        except Exception as e:
            logger.warning(f"Error generando reporte: {e}")
        
    except Exception as e:
        print(f"Error al enviar notificación: {str(e)}")


# Definición de tareas
extract_task = PythonOperator(
    task_id='extract_competitor_prices',
    python_callable=extract_competitor_prices,
    dag=dag,
)

analyze_task = PythonOperator(
    task_id='analyze_and_adjust_prices',
    python_callable=analyze_and_adjust_prices,
    dag=dag,
)

publish_task = PythonOperator(
    task_id='publish_catalog_update',
    python_callable=publish_catalog_update,
    dag=dag,
)

notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    dag=dag,
)

# Definir flujo de ejecución
extract_task >> analyze_task >> publish_task >> notification_task

