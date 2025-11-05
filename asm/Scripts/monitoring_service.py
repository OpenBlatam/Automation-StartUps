from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Alert
import logging
from typing import Dict, List, Optional, Tuple
import threading
import time
import json
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    """Niveles de severidad de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alertas"""
    STOCK_LOW = "stock_low"
    STOCK_OUT = "stock_out"
    DEMAND_SPIKE = "demand_spike"
    PRICE_ANOMALY = "price_anomaly"
    SUPPLIER_ISSUE = "supplier_issue"
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_THREAT = "security_threat"

@dataclass
class MonitoringMetric:
    """Métrica de monitoreo"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    unit: str
    timestamp: datetime
    trend: str = "stable"  # up, down, stable

@dataclass
class SystemHealth:
    """Estado de salud del sistema"""
    overall_status: str  # healthy, warning, critical
    metrics: List[MonitoringMetric]
    alerts_count: int
    last_check: datetime
    uptime: float
    performance_score: float

class AdvancedMonitoringService:
    """Servicio avanzado de monitoreo y alertas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.alert_rules = {}
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Configurar reglas de alertas por defecto
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Configura reglas de alertas por defecto"""
        self.alert_rules = {
            AlertType.STOCK_LOW: {
                'enabled': True,
                'severity': AlertSeverity.MEDIUM,
                'threshold': 0.1,  # 10% del stock mínimo
                'cooldown_minutes': 60
            },
            AlertType.STOCK_OUT: {
                'enabled': True,
                'severity': AlertSeverity.CRITICAL,
                'threshold': 0,
                'cooldown_minutes': 0
            },
            AlertType.DEMAND_SPIKE: {
                'enabled': True,
                'severity': AlertSeverity.HIGH,
                'threshold': 2.0,  # 200% del promedio
                'cooldown_minutes': 30
            },
            AlertType.PRICE_ANOMALY: {
                'enabled': True,
                'severity': AlertSeverity.MEDIUM,
                'threshold': 0.2,  # 20% de cambio
                'cooldown_minutes': 120
            },
            AlertType.SYSTEM_ERROR: {
                'enabled': True,
                'severity': AlertSeverity.HIGH,
                'threshold': 5,  # 5 errores por hora
                'cooldown_minutes': 15
            },
            AlertType.PERFORMANCE_DEGRADATION: {
                'enabled': True,
                'severity': AlertSeverity.MEDIUM,
                'threshold': 0.8,  # 80% del rendimiento normal
                'cooldown_minutes': 30
            }
        }
    
    def start_monitoring(self):
        """Inicia el monitoreo del sistema"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info('Monitoreo avanzado iniciado')
    
    def stop_monitoring(self):
        """Detiene el monitoreo del sistema"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info('Monitoreo avanzado detenido')
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.is_monitoring:
            try:
                # Recolectar métricas
                metrics = self._collect_system_metrics()
                
                # Evaluar reglas de alertas
                self._evaluate_alert_rules(metrics)
                
                # Actualizar historial de métricas
                self._update_metrics_history(metrics)
                
                # Limpiar historial antiguo
                self._cleanup_old_metrics()
                
                # Esperar antes de la siguiente verificación
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                self.logger.error(f'Error en loop de monitoreo: {str(e)}')
                time.sleep(300)  # Esperar 5 minutos en caso de error
    
    def _collect_system_metrics(self) -> List[MonitoringMetric]:
        """Recolecta métricas del sistema"""
        metrics = []
        
        try:
            # Métricas de inventario
            total_products = Product.query.count()
            low_stock_products = self._count_low_stock_products()
            out_of_stock_products = self._count_out_of_stock_products()
            
            metrics.extend([
                MonitoringMetric(
                    name='total_products',
                    value=total_products,
                    threshold_warning=0,
                    threshold_critical=0,
                    unit='products',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='low_stock_ratio',
                    value=low_stock_products / total_products if total_products > 0 else 0,
                    threshold_warning=0.1,
                    threshold_critical=0.2,
                    unit='ratio',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='out_of_stock_ratio',
                    value=out_of_stock_products / total_products if total_products > 0 else 0,
                    threshold_warning=0.05,
                    threshold_critical=0.1,
                    unit='ratio',
                    timestamp=datetime.utcnow()
                )
            ])
            
            # Métricas de ventas
            sales_metrics = self._collect_sales_metrics()
            metrics.extend(sales_metrics)
            
            # Métricas de rendimiento
            performance_metrics = self._collect_performance_metrics()
            metrics.extend(performance_metrics)
            
            # Métricas de errores
            error_metrics = self._collect_error_metrics()
            metrics.extend(error_metrics)
            
        except Exception as e:
            self.logger.error(f'Error recolectando métricas: {str(e)}')
        
        return metrics
    
    def _count_low_stock_products(self) -> int:
        """Cuenta productos con stock bajo"""
        try:
            count = 0
            products = Product.query.all()
            
            for product in products:
                current_stock = self._get_current_stock(product.id)
                if current_stock <= product.min_stock_level:
                    count += 1
            
            return count
        except Exception as e:
            self.logger.error(f'Error contando productos con stock bajo: {str(e)}')
            return 0
    
    def _count_out_of_stock_products(self) -> int:
        """Cuenta productos sin stock"""
        try:
            count = 0
            products = Product.query.all()
            
            for product in products:
                current_stock = self._get_current_stock(product.id)
                if current_stock <= 0:
                    count += 1
            
            return count
        except Exception as e:
            self.logger.error(f'Error contando productos sin stock: {str(e)}')
            return 0
    
    def _get_current_stock(self, product_id: int) -> int:
        """Obtiene stock actual de un producto"""
        try:
            entries = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'in'
            ).scalar() or 0
            
            exits = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'out'
            ).scalar() or 0
            
            adjustments = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'adjustment'
            ).scalar() or 0
            
            return max(0, entries - exits + adjustments)
            
        except Exception as e:
            self.logger.error(f'Error obteniendo stock actual: {str(e)}')
            return 0
    
    def _collect_sales_metrics(self) -> List[MonitoringMetric]:
        """Recolecta métricas de ventas"""
        metrics = []
        
        try:
            # Ventas de las últimas 24 horas
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)
            
            recent_sales = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            total_revenue = sum(sale.total_amount for sale in recent_sales)
            total_quantity = sum(sale.quantity_sold for sale in recent_sales)
            
            # Calcular promedio histórico para comparación
            historical_sales = SalesRecord.query.filter(
                SalesRecord.sale_date >= end_date - timedelta(days=7),
                SalesRecord.sale_date < start_date
            ).all()
            
            historical_revenue = sum(sale.total_amount for sale in historical_sales) / 7
            historical_quantity = sum(sale.quantity_sold for sale in historical_sales) / 7
            
            metrics.extend([
                MonitoringMetric(
                    name='daily_revenue',
                    value=total_revenue,
                    threshold_warning=historical_revenue * 0.8,
                    threshold_critical=historical_revenue * 0.5,
                    unit='currency',
                    timestamp=datetime.utcnow(),
                    trend='up' if total_revenue > historical_revenue else 'down'
                ),
                MonitoringMetric(
                    name='daily_quantity_sold',
                    value=total_quantity,
                    threshold_warning=historical_quantity * 0.8,
                    threshold_critical=historical_quantity * 0.5,
                    unit='units',
                    timestamp=datetime.utcnow(),
                    trend='up' if total_quantity > historical_quantity else 'down'
                )
            ])
            
        except Exception as e:
            self.logger.error(f'Error recolectando métricas de ventas: {str(e)}')
        
        return metrics
    
    def _collect_performance_metrics(self) -> List[MonitoringMetric]:
        """Recolecta métricas de rendimiento"""
        metrics = []
        
        try:
            # Simular métricas de rendimiento
            import psutil
            import os
            
            # Uso de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Uso de memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Espacio en disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            metrics.extend([
                MonitoringMetric(
                    name='cpu_usage',
                    value=cpu_percent,
                    threshold_warning=70.0,
                    threshold_critical=90.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='memory_usage',
                    value=memory_percent,
                    threshold_warning=80.0,
                    threshold_critical=95.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='disk_usage',
                    value=disk_percent,
                    threshold_warning=85.0,
                    threshold_critical=95.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                )
            ])
            
        except ImportError:
            # psutil no disponible, usar métricas simuladas
            metrics.extend([
                MonitoringMetric(
                    name='cpu_usage',
                    value=45.0,
                    threshold_warning=70.0,
                    threshold_critical=90.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='memory_usage',
                    value=60.0,
                    threshold_warning=80.0,
                    threshold_critical=95.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                ),
                MonitoringMetric(
                    name='disk_usage',
                    value=75.0,
                    threshold_warning=85.0,
                    threshold_critical=95.0,
                    unit='percent',
                    timestamp=datetime.utcnow()
                )
            ])
        except Exception as e:
            self.logger.error(f'Error recolectando métricas de rendimiento: {str(e)}')
        
        return metrics
    
    def _collect_error_metrics(self) -> List[MonitoringMetric]:
        """Recolecta métricas de errores"""
        metrics = []
        
        try:
            # Contar errores de las últimas 24 horas
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)
            
            # Simular conteo de errores (en un sistema real, esto vendría de logs)
            error_count = 0
            
            metrics.append(MonitoringMetric(
                name='error_count_24h',
                value=error_count,
                threshold_warning=5.0,
                threshold_critical=10.0,
                unit='errors',
                timestamp=datetime.utcnow()
            ))
            
        except Exception as e:
            self.logger.error(f'Error recolectando métricas de errores: {str(e)}')
        
        return metrics
    
    def _evaluate_alert_rules(self, metrics: List[MonitoringMetric]):
        """Evalúa reglas de alertas"""
        try:
            for metric in metrics:
                # Evaluar reglas específicas por métrica
                if metric.name == 'out_of_stock_ratio' and metric.value > 0:
                    self._create_alert_if_needed(
                        AlertType.STOCK_OUT,
                        f"Productos sin stock detectados: {metric.value:.1%}",
                        AlertSeverity.CRITICAL
                    )
                
                elif metric.name == 'low_stock_ratio' and metric.value > 0.1:
                    self._create_alert_if_needed(
                        AlertType.STOCK_LOW,
                        f"Alto porcentaje de productos con stock bajo: {metric.value:.1%}",
                        AlertSeverity.MEDIUM
                    )
                
                elif metric.name == 'daily_revenue' and metric.value < metric.threshold_warning:
                    self._create_alert_if_needed(
                        AlertType.DEMAND_SPIKE,
                        f"Ventas por debajo del promedio: ${metric.value:.2f}",
                        AlertSeverity.HIGH
                    )
                
                elif metric.name == 'cpu_usage' and metric.value > metric.threshold_critical:
                    self._create_alert_if_needed(
                        AlertType.PERFORMANCE_DEGRADATION,
                        f"Alto uso de CPU: {metric.value:.1f}%",
                        AlertSeverity.HIGH
                    )
                
                elif metric.name == 'memory_usage' and metric.value > metric.threshold_critical:
                    self._create_alert_if_needed(
                        AlertType.PERFORMANCE_DEGRADATION,
                        f"Alto uso de memoria: {metric.value:.1f}%",
                        AlertSeverity.HIGH
                    )
                
                elif metric.name == 'error_count_24h' and metric.value > metric.threshold_critical:
                    self._create_alert_if_needed(
                        AlertType.SYSTEM_ERROR,
                        f"Alto número de errores: {metric.value} en 24h",
                        AlertSeverity.HIGH
                    )
        
        except Exception as e:
            self.logger.error(f'Error evaluando reglas de alertas: {str(e)}')
    
    def _create_alert_if_needed(self, alert_type: AlertType, message: str, severity: AlertSeverity):
        """Crea alerta si es necesario (considerando cooldown)"""
        try:
            rule = self.alert_rules.get(alert_type)
            if not rule or not rule['enabled']:
                return
            
            # Verificar cooldown
            last_alert = Alert.query.filter(
                Alert.alert_type == alert_type.value,
                Alert.is_resolved == False
            ).order_by(Alert.created_at.desc()).first()
            
            if last_alert:
                time_since_last = datetime.utcnow() - last_alert.created_at
                cooldown_minutes = rule['cooldown_minutes']
                
                if time_since_last.total_seconds() < cooldown_minutes * 60:
                    return  # Aún en período de cooldown
            
            # Crear nueva alerta
            alert = Alert(
                alert_type=alert_type.value,
                message=message,
                severity=severity.value,
                is_resolved=False,
                created_at=datetime.utcnow()
            )
            
            db.session.add(alert)
            db.session.commit()
            
            self.logger.info(f'Alerta creada: {alert_type.value} - {message}')
            
        except Exception as e:
            self.logger.error(f'Error creando alerta: {str(e)}')
    
    def _update_metrics_history(self, metrics: List[MonitoringMetric]):
        """Actualiza historial de métricas"""
        try:
            timestamp = datetime.utcnow()
            
            for metric in metrics:
                self.metrics_history.append({
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': timestamp,
                    'trend': metric.trend
                })
            
            # Mantener solo las últimas 1000 entradas por métrica
            metric_names = set(m['name'] for m in self.metrics_history)
            for name in metric_names:
                entries = [m for m in self.metrics_history if m['name'] == name]
                if len(entries) > 1000:
                    # Mantener solo las más recientes
                    entries.sort(key=lambda x: x['timestamp'], reverse=True)
                    self.metrics_history = [m for m in self.metrics_history if m['name'] != name]
                    self.metrics_history.extend(entries[:1000])
        
        except Exception as e:
            self.logger.error(f'Error actualizando historial de métricas: {str(e)}')
    
    def _cleanup_old_metrics(self):
        """Limpia métricas antiguas"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            self.metrics_history = [
                m for m in self.metrics_history 
                if m['timestamp'] > cutoff_date
            ]
        except Exception as e:
            self.logger.error(f'Error limpiando métricas antiguas: {str(e)}')
    
    def get_system_health(self) -> SystemHealth:
        """Obtiene estado de salud del sistema"""
        try:
            # Obtener métricas más recientes
            recent_metrics = []
            metric_names = set(m['name'] for m in self.metrics_history)
            
            for name in metric_names:
                entries = [m for m in self.metrics_history if m['name'] == name]
                if entries:
                    latest = max(entries, key=lambda x: x['timestamp'])
                    recent_metrics.append(MonitoringMetric(
                        name=latest['name'],
                        value=latest['value'],
                        threshold_warning=0,
                        threshold_critical=0,
                        unit='',
                        timestamp=latest['timestamp'],
                        trend=latest.get('trend', 'stable')
                    ))
            
            # Calcular estado general
            critical_count = 0
            warning_count = 0
            
            for metric in recent_metrics:
                if hasattr(metric, 'threshold_critical') and metric.value > metric.threshold_critical:
                    critical_count += 1
                elif hasattr(metric, 'threshold_warning') and metric.value > metric.threshold_warning:
                    warning_count += 1
            
            if critical_count > 0:
                overall_status = 'critical'
            elif warning_count > 0:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            # Contar alertas activas
            active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
            
            # Calcular puntuación de rendimiento
            performance_score = self._calculate_performance_score(recent_metrics)
            
            return SystemHealth(
                overall_status=overall_status,
                metrics=recent_metrics,
                alerts_count=active_alerts,
                last_check=datetime.utcnow(),
                uptime=99.9,  # Simulado
                performance_score=performance_score
            )
            
        except Exception as e:
            self.logger.error(f'Error obteniendo estado de salud: {str(e)}')
            return SystemHealth(
                overall_status='unknown',
                metrics=[],
                alerts_count=0,
                last_check=datetime.utcnow(),
                uptime=0,
                performance_score=0
            )
    
    def _calculate_performance_score(self, metrics: List[MonitoringMetric]) -> float:
        """Calcula puntuación de rendimiento"""
        try:
            if not metrics:
                return 0.0
            
            total_score = 0.0
            count = 0
            
            for metric in metrics:
                if metric.name in ['cpu_usage', 'memory_usage', 'disk_usage']:
                    # Para métricas de uso, menor es mejor
                    if metric.value < 50:
                        score = 100
                    elif metric.value < 80:
                        score = 80 - (metric.value - 50) * 2
                    else:
                        score = max(0, 40 - (metric.value - 80) * 2)
                    
                    total_score += score
                    count += 1
            
            return total_score / count if count > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f'Error calculando puntuación de rendimiento: {str(e)}')
            return 0.0
    
    def get_metrics_history(self, metric_name: str = None, hours: int = 24) -> List[Dict]:
        """Obtiene historial de métricas"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(hours=hours)
            
            if metric_name:
                history = [
                    m for m in self.metrics_history 
                    if m['name'] == metric_name and m['timestamp'] > cutoff_date
                ]
            else:
                history = [
                    m for m in self.metrics_history 
                    if m['timestamp'] > cutoff_date
                ]
            
            # Ordenar por timestamp
            history.sort(key=lambda x: x['timestamp'])
            
            return history
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial de métricas: {str(e)}')
            return []
    
    def update_alert_rule(self, alert_type: AlertType, rule_config: Dict):
        """Actualiza regla de alerta"""
        try:
            self.alert_rules[alert_type] = rule_config
            self.logger.info(f'Regla de alerta actualizada: {alert_type.value}')
            
        except Exception as e:
            self.logger.error(f'Error actualizando regla de alerta: {str(e)}')
    
    def get_alert_rules(self) -> Dict:
        """Obtiene reglas de alertas"""
        return self.alert_rules

# Instancia global del servicio de monitoreo
advanced_monitoring_service = AdvancedMonitoringService()



