#!/usr/bin/env python3
"""
🔗 MARKETING BRAIN INTEGRATION
Sistema de Integración Unificado para el Advanced Marketing Brain System
Conecta todos los componentes y proporciona una interfaz unificada
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept
from marketing_brain_analytics import MarketingBrainAnalytics
from marketing_brain_automation import MarketingBrainAutomation

logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuración de integración"""
    api_endpoints: Dict[str, str]
    external_services: Dict[str, Dict[str, Any]]
    sync_intervals: Dict[str, int]  # en segundos
    data_sources: List[str]
    output_formats: List[str]

@dataclass
class IntegrationStatus:
    """Estado de integración"""
    component: str
    status: str  # connected, disconnected, error
    last_sync: Optional[str]
    error_message: Optional[str] = None

@dataclass
class UnifiedResponse:
    """Respuesta unificada del sistema"""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    timestamp: str
    execution_time_ms: float

class MarketingBrainIntegration:
    """
    Sistema de Integración Unificado para el Advanced Marketing Brain System
    Conecta todos los componentes y proporciona una interfaz unificada
    """
    
    def __init__(self, config_file: str = None):
        # Inicializar componentes principales
        self.brain = AdvancedMarketingBrain()
        self.analytics = MarketingBrainAnalytics(self.brain)
        self.automation = MarketingBrainAutomation(self.brain, self.analytics)
        
        # Configuración de integración
        self.config = self._load_integration_config(config_file)
        
        # Estado de integración
        self.integration_status = {}
        self.sync_threads = {}
        self.is_running = False
        
        # Cache de datos
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Pool de threads para operaciones concurrentes
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        # Métricas de integración
        self.integration_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'cache_hit_rate': 0
        }
        
        logger.info("🔗 Marketing Brain Integration initialized successfully")
    
    def _load_integration_config(self, config_file: str = None) -> IntegrationConfig:
        """Cargar configuración de integración"""
        default_config = {
            'api_endpoints': {
                'concepts': '/api/concepts',
                'analytics': '/api/analytics',
                'automation': '/api/automation',
                'trends': '/api/trends',
                'reports': '/api/reports'
            },
            'external_services': {
                'google_analytics': {
                    'enabled': False,
                    'api_key': '',
                    'view_id': ''
                },
                'social_media': {
                    'enabled': False,
                    'platforms': ['facebook', 'twitter', 'linkedin'],
                    'api_keys': {}
                },
                'email_marketing': {
                    'enabled': False,
                    'service': 'mailchimp',
                    'api_key': ''
                },
                'crm': {
                    'enabled': False,
                    'service': 'hubspot',
                    'api_key': ''
                }
            },
            'sync_intervals': {
                'trends': 3600,  # 1 hora
                'analytics': 1800,  # 30 minutos
                'automation': 300,  # 5 minutos
                'external_data': 7200  # 2 horas
            },
            'data_sources': [
                'internal_campaigns',
                'external_trends',
                'social_media_data',
                'analytics_data'
            ],
            'output_formats': ['json', 'csv', 'excel', 'pdf']
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    # Merge con configuración por defecto
                    for key, value in custom_config.items():
                        if key in default_config:
                            if isinstance(value, dict) and isinstance(default_config[key], dict):
                                default_config[key].update(value)
                            else:
                                default_config[key] = value
            except Exception as e:
                logger.warning(f"Error cargando configuración personalizada: {e}")
        
        return IntegrationConfig(**default_config)
    
    def start_integration(self):
        """Iniciar sistema de integración"""
        if self.is_running:
            logger.warning("Sistema de integración ya está ejecutándose")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Iniciar componentes
        self.automation.start_automation()
        
        # Iniciar sincronización de datos
        self._start_data_sync()
        
        # Iniciar monitoreo de integración
        self._start_integration_monitoring()
        
        logger.info("🔗 Sistema de integración iniciado")
        self._update_integration_status('system', 'connected')
    
    def stop_integration(self):
        """Detener sistema de integración"""
        if not self.is_running:
            logger.warning("Sistema de integración no está ejecutándose")
            return
        
        self.is_running = False
        
        # Detener componentes
        self.automation.stop_automation()
        
        # Detener threads de sincronización
        for thread in self.sync_threads.values():
            if thread.is_alive():
                thread.join(timeout=5)
        
        # Cerrar pool de threads
        self.thread_pool.shutdown(wait=True)
        
        logger.info("🔗 Sistema de integración detenido")
        self._update_integration_status('system', 'disconnected')
    
    def _start_data_sync(self):
        """Iniciar sincronización de datos"""
        for component, interval in self.config.sync_intervals.items():
            thread = threading.Thread(
                target=self._sync_worker,
                args=(component, interval),
                daemon=True
            )
            thread.start()
            self.sync_threads[component] = thread
        
        logger.info(f"📡 Iniciada sincronización para {len(self.config.sync_intervals)} componentes")
    
    def _sync_worker(self, component: str, interval: int):
        """Worker para sincronización de datos"""
        while self.is_running:
            try:
                self._sync_component_data(component)
                self._update_integration_status(component, 'connected')
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error sincronizando {component}: {e}")
                self._update_integration_status(component, 'error', str(e))
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _sync_component_data(self, component: str):
        """Sincronizar datos de un componente específico"""
        if component == 'trends':
            self._sync_trends_data()
        elif component == 'analytics':
            self._sync_analytics_data()
        elif component == 'automation':
            self._sync_automation_data()
        elif component == 'external_data':
            self._sync_external_data()
    
    def _sync_trends_data(self):
        """Sincronizar datos de tendencias"""
        trends = self.analytics.analyze_market_trends()
        self.data_cache['trends'] = {
            'data': [self.analytics._trend_to_dict(trend) for trend in trends],
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("📈 Datos de tendencias sincronizados")
    
    def _sync_analytics_data(self):
        """Sincronizar datos de análisis"""
        report = self.analytics.generate_market_opportunity_report()
        self.data_cache['analytics'] = {
            'data': report,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("📊 Datos de análisis sincronizados")
    
    def _sync_automation_data(self):
        """Sincronizar datos de automatización"""
        status = self.automation.get_system_status()
        self.data_cache['automation'] = {
            'data': status,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("🤖 Datos de automatización sincronizados")
    
    def _sync_external_data(self):
        """Sincronizar datos externos"""
        # Implementar sincronización con servicios externos
        for service_name, service_config in self.config.external_services.items():
            if service_config.get('enabled', False):
                try:
                    self._sync_external_service(service_name, service_config)
                except Exception as e:
                    logger.error(f"Error sincronizando {service_name}: {e}")
    
    def _sync_external_service(self, service_name: str, service_config: Dict[str, Any]):
        """Sincronizar servicio externo específico"""
        if service_name == 'google_analytics':
            self._sync_google_analytics(service_config)
        elif service_name == 'social_media':
            self._sync_social_media(service_config)
        elif service_name == 'email_marketing':
            self._sync_email_marketing(service_config)
        elif service_name == 'crm':
            self._sync_crm(service_config)
    
    def _sync_google_analytics(self, config: Dict[str, Any]):
        """Sincronizar Google Analytics"""
        # Implementación simplificada - en producción usaría la API real
        mock_data = {
            'sessions': 15000,
            'users': 12000,
            'pageviews': 45000,
            'bounce_rate': 0.35,
            'conversion_rate': 0.025
        }
        
        self.data_cache['google_analytics'] = {
            'data': mock_data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("📊 Google Analytics sincronizado")
    
    def _sync_social_media(self, config: Dict[str, Any]):
        """Sincronizar redes sociales"""
        mock_data = {
            'facebook': {'followers': 5000, 'engagement_rate': 0.045},
            'twitter': {'followers': 3200, 'engagement_rate': 0.038},
            'linkedin': {'followers': 1800, 'engagement_rate': 0.052}
        }
        
        self.data_cache['social_media'] = {
            'data': mock_data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("📱 Redes sociales sincronizadas")
    
    def _sync_email_marketing(self, config: Dict[str, Any]):
        """Sincronizar email marketing"""
        mock_data = {
            'subscribers': 25000,
            'open_rate': 0.22,
            'click_rate': 0.035,
            'unsubscribe_rate': 0.008
        }
        
        self.data_cache['email_marketing'] = {
            'data': mock_data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("📧 Email marketing sincronizado")
    
    def _sync_crm(self, config: Dict[str, Any]):
        """Sincronizar CRM"""
        mock_data = {
            'total_contacts': 15000,
            'active_leads': 2500,
            'conversion_rate': 0.15,
            'average_deal_size': 2500
        }
        
        self.data_cache['crm'] = {
            'data': mock_data,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug("👥 CRM sincronizado")
    
    def _start_integration_monitoring(self):
        """Iniciar monitoreo de integración"""
        def monitor_loop():
            while self.is_running:
                try:
                    self._monitor_integration_health()
                    time.sleep(60)  # Monitorear cada minuto
                except Exception as e:
                    logger.error(f"Error en monitoreo de integración: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("📊 Monitoreo de integración iniciado")
    
    def _monitor_integration_health(self):
        """Monitorear salud de la integración"""
        # Verificar estado de componentes
        components_status = {
            'brain': 'connected' if self.brain else 'disconnected',
            'analytics': 'connected' if self.analytics else 'disconnected',
            'automation': 'connected' if self.automation.is_running else 'disconnected'
        }
        
        # Verificar cache
        cache_health = self._check_cache_health()
        
        # Verificar métricas
        self._update_integration_metrics()
        
        # Generar alertas si es necesario
        self._check_integration_alerts(components_status, cache_health)
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Verificar salud del cache"""
        current_time = datetime.now()
        cache_health = {
            'total_entries': len(self.data_cache),
            'stale_entries': 0,
            'hit_rate': self.integration_metrics['cache_hit_rate']
        }
        
        for key, entry in self.data_cache.items():
            entry_time = datetime.fromisoformat(entry['timestamp'])
            if (current_time - entry_time).total_seconds() > self.cache_ttl:
                cache_health['stale_entries'] += 1
        
        return cache_health
    
    def _update_integration_metrics(self):
        """Actualizar métricas de integración"""
        if hasattr(self, 'start_time'):
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.integration_metrics['uptime_seconds'] = uptime
    
    def _check_integration_alerts(self, components_status: Dict[str, str], cache_health: Dict[str, Any]):
        """Verificar alertas de integración"""
        # Alertas por componentes desconectados
        for component, status in components_status.items():
            if status == 'disconnected':
                self.automation._add_alert(
                    "warning", 
                    f"Componente Desconectado", 
                    f"El componente {component} está desconectado"
                )
        
        # Alertas por cache
        if cache_health['stale_entries'] > 0:
            self.automation._add_alert(
                "warning",
                "Cache Desactualizado",
                f"{cache_health['stale_entries']} entradas del cache están desactualizadas"
            )
    
    def _update_integration_status(self, component: str, status: str, error_message: str = None):
        """Actualizar estado de integración"""
        self.integration_status[component] = IntegrationStatus(
            component=component,
            status=status,
            last_sync=datetime.now().isoformat(),
            error_message=error_message
        )
    
    def get_unified_dashboard_data(self) -> UnifiedResponse:
        """Obtener datos unificados para dashboard"""
        start_time = time.time()
        
        try:
            # Obtener datos de todos los componentes
            dashboard_data = {
                'system_overview': self._get_system_overview(),
                'concepts': self._get_recent_concepts(),
                'trends': self._get_cached_trends(),
                'analytics': self._get_cached_analytics(),
                'automation': self._get_cached_automation(),
                'external_data': self._get_external_data_summary(),
                'integration_status': self._get_integration_status_summary()
            }
            
            execution_time = (time.time() - start_time) * 1000
            
            response = UnifiedResponse(
                success=True,
                data=dashboard_data,
                metadata={
                    'components_queried': len(dashboard_data),
                    'cache_hits': self._count_cache_hits(),
                    'data_freshness': self._calculate_data_freshness()
                },
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(True, execution_time)
            return response
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error obteniendo datos unificados: {e}")
            
            response = UnifiedResponse(
                success=False,
                data=None,
                metadata={'error': str(e)},
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(False, execution_time)
            return response
    
    def _get_system_overview(self) -> Dict[str, Any]:
        """Obtener resumen del sistema"""
        return {
            'total_campaigns': len(self.brain.campaigns),
            'themes_extracted': len(self.brain.themes),
            'automation_rules': len([r for r in self.automation.automation_rules if r.enabled]),
            'active_executions': len(self.automation.active_executions),
            'integration_uptime': self.integration_metrics.get('uptime_seconds', 0),
            'system_status': 'running' if self.is_running else 'stopped'
        }
    
    def _get_recent_concepts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener conceptos recientes"""
        concepts = self.brain.generate_fresh_concepts(num_concepts=limit)
        return [self._concept_to_dict(concept) for concept in concepts]
    
    def _get_cached_trends(self) -> Dict[str, Any]:
        """Obtener tendencias del cache"""
        if 'trends' in self.data_cache:
            return self.data_cache['trends']
        return {'data': [], 'timestamp': None}
    
    def _get_cached_analytics(self) -> Dict[str, Any]:
        """Obtener análisis del cache"""
        if 'analytics' in self.data_cache:
            return self.data_cache['analytics']
        return {'data': {}, 'timestamp': None}
    
    def _get_cached_automation(self) -> Dict[str, Any]:
        """Obtener datos de automatización del cache"""
        if 'automation' in self.data_cache:
            return self.data_cache['automation']
        return {'data': {}, 'timestamp': None}
    
    def _get_external_data_summary(self) -> Dict[str, Any]:
        """Obtener resumen de datos externos"""
        summary = {}
        for service_name in ['google_analytics', 'social_media', 'email_marketing', 'crm']:
            if service_name in self.data_cache:
                summary[service_name] = {
                    'available': True,
                    'last_sync': self.data_cache[service_name]['timestamp']
                }
            else:
                summary[service_name] = {'available': False}
        return summary
    
    def _get_integration_status_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado de integración"""
        return {
            component: {
                'status': status.status,
                'last_sync': status.last_sync,
                'error': status.error_message
            }
            for component, status in self.integration_status.items()
        }
    
    def _count_cache_hits(self) -> int:
        """Contar hits del cache"""
        return len(self.data_cache)
    
    def _calculate_data_freshness(self) -> Dict[str, str]:
        """Calcular frescura de los datos"""
        freshness = {}
        current_time = datetime.now()
        
        for key, entry in self.data_cache.items():
            entry_time = datetime.fromisoformat(entry['timestamp'])
            age_seconds = (current_time - entry_time).total_seconds()
            
            if age_seconds < 300:  # 5 minutos
                freshness[key] = 'fresh'
            elif age_seconds < 1800:  # 30 minutos
                freshness[key] = 'recent'
            else:
                freshness[key] = 'stale'
        
        return freshness
    
    def _update_request_metrics(self, success: bool, execution_time: float):
        """Actualizar métricas de requests"""
        self.integration_metrics['total_requests'] += 1
        
        if success:
            self.integration_metrics['successful_requests'] += 1
        else:
            self.integration_metrics['failed_requests'] += 1
        
        # Actualizar tiempo promedio de respuesta
        total_requests = self.integration_metrics['total_requests']
        current_avg = self.integration_metrics['average_response_time']
        self.integration_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
    
    def _concept_to_dict(self, concept: MarketingConcept) -> Dict[str, Any]:
        """Convertir MarketingConcept a diccionario"""
        return {
            'id': concept.concept_id,
            'name': concept.name,
            'description': concept.description,
            'category': concept.category,
            'technology': concept.technology,
            'channel': concept.channel,
            'vertical': concept.vertical,
            'success_probability': concept.success_probability,
            'complexity': concept.complexity,
            'priority': concept.priority,
            'budget': concept.estimated_budget,
            'timeline': concept.timeline,
            'tags': concept.tags,
            'created_at': concept.created_at
        }
    
    def generate_comprehensive_report(self, 
                                    include_external_data: bool = True,
                                    format: str = 'json') -> UnifiedResponse:
        """Generar reporte comprensivo del sistema"""
        start_time = time.time()
        
        try:
            # Generar reporte base
            base_report = self.analytics.generate_market_opportunity_report()
            
            # Agregar datos de automatización
            automation_status = self.automation.get_system_status()
            base_report['automation_status'] = automation_status
            
            # Agregar datos de integración
            integration_metrics = self.integration_metrics.copy()
            base_report['integration_metrics'] = integration_metrics
            
            # Agregar datos externos si se solicita
            if include_external_data:
                external_data = {}
                for service_name in ['google_analytics', 'social_media', 'email_marketing', 'crm']:
                    if service_name in self.data_cache:
                        external_data[service_name] = self.data_cache[service_name]['data']
                base_report['external_data'] = external_data
            
            # Agregar conceptos recientes
            recent_concepts = self._get_recent_concepts(20)
            base_report['recent_concepts'] = recent_concepts
            
            execution_time = (time.time() - start_time) * 1000
            
            # Exportar en formato solicitado
            if format == 'json':
                filename = self._export_report_json(base_report)
            elif format == 'csv':
                filename = self._export_report_csv(base_report)
            else:
                filename = self._export_report_json(base_report)
            
            response = UnifiedResponse(
                success=True,
                data=base_report,
                metadata={
                    'format': format,
                    'filename': filename,
                    'include_external_data': include_external_data,
                    'concepts_included': len(recent_concepts)
                },
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(True, execution_time)
            return response
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error generando reporte comprensivo: {e}")
            
            response = UnifiedResponse(
                success=False,
                data=None,
                metadata={'error': str(e)},
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(False, execution_time)
            return response
    
    def _export_report_json(self, report: Dict[str, Any]) -> str:
        """Exportar reporte a JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def _export_report_csv(self, report: Dict[str, Any]) -> str:
        """Exportar reporte a CSV"""
        import pandas as pd
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_report_{timestamp}.csv"
        
        # Convertir datos a DataFrame
        data = []
        
        # Agregar conceptos
        for concept in report.get('recent_concepts', []):
            data.append({
                'type': 'concept',
                'id': concept['id'],
                'name': concept['name'],
                'category': concept['category'],
                'technology': concept['technology'],
                'success_probability': concept['success_probability']
            })
        
        # Agregar tendencias
        for trend in report.get('market_trends', []):
            data.append({
                'type': 'trend',
                'id': trend['name'],
                'name': trend['name'],
                'category': trend['category'],
                'growth_rate': trend['growth_rate'],
                'popularity_score': trend['popularity_score']
            })
        
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
        
        return filename
    
    def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any] = None) -> UnifiedResponse:
        """Ejecutar workflow específico"""
        start_time = time.time()
        
        try:
            if workflow_name == 'daily_analysis':
                result = self._execute_daily_analysis_workflow(parameters or {})
            elif workflow_name == 'trend_monitoring':
                result = self._execute_trend_monitoring_workflow(parameters or {})
            elif workflow_name == 'concept_optimization':
                result = self._execute_concept_optimization_workflow(parameters or {})
            elif workflow_name == 'automation_setup':
                result = self._execute_automation_setup_workflow(parameters or {})
            else:
                raise ValueError(f"Workflow '{workflow_name}' no reconocido")
            
            execution_time = (time.time() - start_time) * 1000
            
            response = UnifiedResponse(
                success=True,
                data=result,
                metadata={
                    'workflow': workflow_name,
                    'parameters': parameters or {}
                },
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(True, execution_time)
            return response
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error ejecutando workflow {workflow_name}: {e}")
            
            response = UnifiedResponse(
                success=False,
                data=None,
                metadata={'error': str(e), 'workflow': workflow_name},
                timestamp=datetime.now().isoformat(),
                execution_time_ms=execution_time
            )
            
            self._update_request_metrics(False, execution_time)
            return response
    
    def _execute_daily_analysis_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar workflow de análisis diario"""
        # Generar conceptos frescos
        concepts = self.brain.generate_fresh_concepts(
            num_concepts=parameters.get('num_concepts', 10),
            min_success_probability=parameters.get('min_success_probability', 0.8)
        )
        
        # Analizar tendencias
        trends = self.analytics.analyze_market_trends()
        
        # Generar reporte
        report = self.analytics.generate_market_opportunity_report()
        
        return {
            'concepts_generated': len(concepts),
            'trends_analyzed': len(trends),
            'report_generated': True,
            'concepts': [self._concept_to_dict(c) for c in concepts[:5]],
            'top_trends': [self.analytics._trend_to_dict(t) for t in trends[:5]]
        }
    
    def _execute_trend_monitoring_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar workflow de monitoreo de tendencias"""
        # Analizar tendencias específicas
        category = parameters.get('category')
        trends = self.analytics.analyze_market_trends(category=category)
        
        # Generar alertas si es necesario
        alerts = []
        for trend in trends:
            if trend.growth_rate > 0.4:  # Tendencia emergente
                alerts.append({
                    'type': 'emerging_trend',
                    'trend': trend.trend_name,
                    'growth_rate': trend.growth_rate,
                    'message': f"Tendencia emergente detectada: {trend.trend_name}"
                })
        
        return {
            'trends_monitored': len(trends),
            'alerts_generated': len(alerts),
            'trends': [self.analytics._trend_to_dict(t) for t in trends],
            'alerts': alerts
        }
    
    def _execute_concept_optimization_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar workflow de optimización de conceptos"""
        # Generar conceptos base
        concepts = self.brain.generate_fresh_concepts(
            num_concepts=parameters.get('num_concepts', 20)
        )
        
        # Optimizar conceptos
        optimized_concepts = []
        for concept in concepts:
            prediction = self.analytics.predict_concept_performance(concept)
            if prediction.success_probability > 0.8:
                optimized_concepts.append(concept)
        
        # Ejecutar conceptos optimizados automáticamente
        executions = []
        for concept in optimized_concepts[:5]:  # Limitar a 5 ejecuciones
            execution_id = self.automation.execute_concept_automatically(concept)
            executions.append(execution_id)
        
        return {
            'concepts_analyzed': len(concepts),
            'concepts_optimized': len(optimized_concepts),
            'executions_started': len(executions),
            'execution_ids': executions
        }
    
    def _execute_automation_setup_workflow(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar workflow de configuración de automatización"""
        # Configurar reglas de automatización
        rules_configured = 0
        
        if parameters.get('enable_daily_concepts', True):
            # La regla ya existe por defecto
            rules_configured += 1
        
        if parameters.get('enable_trend_monitoring', True):
            # La regla ya existe por defecto
            rules_configured += 1
        
        if parameters.get('enable_performance_alerts', True):
            # La regla ya existe por defecto
            rules_configured += 1
        
        # Configurar servicios externos
        external_services = parameters.get('external_services', {})
        services_configured = 0
        
        for service_name, service_config in external_services.items():
            if service_name in self.config.external_services:
                self.config.external_services[service_name].update(service_config)
                services_configured += 1
        
        return {
            'automation_rules_configured': rules_configured,
            'external_services_configured': services_configured,
            'automation_status': self.automation.is_running,
            'integration_status': self.is_running
        }
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de integración"""
        return {
            'integration_metrics': self.integration_metrics,
            'integration_status': {
                component: {
                    'status': status.status,
                    'last_sync': status.last_sync,
                    'error': status.error_message
                }
                for component, status in self.integration_status.items()
            },
            'cache_status': {
                'total_entries': len(self.data_cache),
                'services_cached': list(self.data_cache.keys()),
                'cache_ttl': self.cache_ttl
            },
            'system_uptime': self.integration_metrics.get('uptime_seconds', 0)
        }
    
    def export_integration_config(self, filename: str = None) -> str:
        """Exportar configuración de integración"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_config_{timestamp}.json"
        
        config_data = {
            'integration_config': asdict(self.config),
            'automation_config': self.automation.export_automation_config(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Configuración de integración exportada a {filename}")
        return filename


def main():
    """Función principal para demostrar el sistema de integración"""
    print("🔗 MARKETING BRAIN INTEGRATION")
    print("=" * 50)
    
    # Inicializar sistema de integración
    integration = MarketingBrainIntegration()
    
    # Mostrar configuración
    print(f"\n⚙️ CONFIGURACIÓN DEL SISTEMA:")
    print(f"   • Endpoints API: {len(integration.config.api_endpoints)}")
    print(f"   • Servicios externos: {len(integration.config.external_services)}")
    print(f"   • Intervalos de sincronización: {len(integration.config.sync_intervals)}")
    print(f"   • Formatos de salida: {', '.join(integration.config.output_formats)}")
    
    # Iniciar integración
    print(f"\n🚀 INICIANDO SISTEMA DE INTEGRACIÓN...")
    integration.start_integration()
    
    # Esperar un poco para que se sincronicen los datos
    print(f"\n⏳ Esperando sincronización inicial...")
    time.sleep(10)
    
    # Obtener datos unificados del dashboard
    print(f"\n📊 OBTENIENDO DATOS UNIFICADOS...")
    dashboard_response = integration.get_unified_dashboard_data()
    
    if dashboard_response.success:
        print(f"   ✅ Datos obtenidos exitosamente")
        print(f"   ⏱️ Tiempo de ejecución: {dashboard_response.execution_time_ms:.1f}ms")
        print(f"   📈 Componentes consultados: {dashboard_response.metadata['components_queried']}")
        print(f"   💾 Cache hits: {dashboard_response.metadata['cache_hits']}")
        
        # Mostrar resumen del sistema
        system_overview = dashboard_response.data['system_overview']
        print(f"\n📋 RESUMEN DEL SISTEMA:")
        print(f"   • Campañas totales: {system_overview['total_campaigns']}")
        print(f"   • Temas extraídos: {system_overview['themes_extracted']}")
        print(f"   • Reglas de automatización: {system_overview['automation_rules']}")
        print(f"   • Ejecuciones activas: {system_overview['active_executions']}")
        print(f"   • Estado del sistema: {system_overview['system_status']}")
    else:
        print(f"   ❌ Error obteniendo datos: {dashboard_response.metadata.get('error')}")
    
    # Ejecutar workflow de análisis diario
    print(f"\n🔄 EJECUTANDO WORKFLOW DE ANÁLISIS DIARIO...")
    workflow_response = integration.execute_workflow('daily_analysis', {
        'num_concepts': 5,
        'min_success_probability': 0.8
    })
    
    if workflow_response.success:
        workflow_data = workflow_response.data
        print(f"   ✅ Workflow ejecutado exitosamente")
        print(f"   🎨 Conceptos generados: {workflow_data['concepts_generated']}")
        print(f"   📈 Tendencias analizadas: {workflow_data['trends_analyzed']}")
        print(f"   📊 Reporte generado: {workflow_data['report_generated']}")
    else:
        print(f"   ❌ Error ejecutando workflow: {workflow_response.metadata.get('error')}")
    
    # Generar reporte comprensivo
    print(f"\n📊 GENERANDO REPORTE COMPRENSIVO...")
    report_response = integration.generate_comprehensive_report(
        include_external_data=True,
        format='json'
    )
    
    if report_response.success:
        print(f"   ✅ Reporte generado exitosamente")
        print(f"   📄 Archivo: {report_response.metadata['filename']}")
        print(f"   📊 Conceptos incluidos: {report_response.metadata['concepts_included']}")
        print(f"   🌐 Datos externos: {report_response.metadata['include_external_data']}")
    else:
        print(f"   ❌ Error generando reporte: {report_response.metadata.get('error')}")
    
    # Mostrar métricas de integración
    print(f"\n📈 MÉTRICAS DE INTEGRACIÓN:")
    metrics = integration.get_integration_metrics()
    integration_metrics = metrics['integration_metrics']
    print(f"   • Requests totales: {integration_metrics['total_requests']}")
    print(f"   • Requests exitosos: {integration_metrics['successful_requests']}")
    print(f"   • Requests fallidos: {integration_metrics['failed_requests']}")
    print(f"   • Tiempo promedio de respuesta: {integration_metrics['average_response_time']:.1f}ms")
    print(f"   • Entradas en cache: {metrics['cache_status']['total_entries']}")
    print(f"   • Servicios en cache: {', '.join(metrics['cache_status']['services_cached'])}")
    
    # Exportar configuración
    print(f"\n💾 EXPORTANDO CONFIGURACIÓN...")
    config_file = integration.export_integration_config()
    print(f"   • Configuración exportada a: {config_file}")
    
    # Detener integración
    print(f"\n🛑 DETENIENDO SISTEMA DE INTEGRACIÓN...")
    integration.stop_integration()
    
    print(f"\n✅ DEMOSTRACIÓN COMPLETADA")
    print(f"🎉 El sistema de integración ha demostrado exitosamente")
    print(f"   la conexión unificada de todos los componentes del")
    print(f"   Advanced Marketing Brain System.")


if __name__ == "__main__":
    main()










