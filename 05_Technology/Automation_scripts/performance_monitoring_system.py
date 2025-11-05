#!/usr/bin/env python3
"""
Performance Monitoring System for Competitive Pricing Analysis
============================================================

Sistema de monitoreo de rendimiento que proporciona:
- Métricas de rendimiento en tiempo real
- Monitoreo de recursos del sistema
- Análisis de latencia y throughput
- Alertas de rendimiento
- Dashboards de métricas
- Análisis de tendencias
- Optimización automática
- Reportes de rendimiento
"""

import psutil
import time
import threading
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
import queue
import multiprocessing as mp
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrica de rendimiento"""
    name: str
    value: float
    timestamp: datetime
    component: str
    metric_type: str  # cpu, memory, disk, network, custom
    unit: str
    tags: Dict[str, str] = None

@dataclass
class PerformanceAlert:
    """Alerta de rendimiento"""
    id: str
    metric_name: str
    threshold: float
    current_value: float
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    component: str
    resolved: bool = False

@dataclass
class PerformanceConfig:
    """Configuración de monitoreo"""
    collection_interval: int = 10  # segundos
    retention_days: int = 30
    alert_thresholds: Dict[str, Dict[str, float]] = None
    enable_cpu_monitoring: bool = True
    enable_memory_monitoring: bool = True
    enable_disk_monitoring: bool = True
    enable_network_monitoring: bool = True
    enable_custom_metrics: bool = True
    auto_optimization: bool = True

class PerformanceMonitoringSystem:
    """Sistema de monitoreo de rendimiento"""
    
    def __init__(self, db_path: str = "performance_monitoring.db", config: PerformanceConfig = None):
        """Inicializar sistema de monitoreo"""
        self.db_path = db_path
        self.config = config or PerformanceConfig()
        
        # Configurar umbrales de alerta por defecto
        if not self.config.alert_thresholds:
            self.config.alert_thresholds = {
                'cpu_percent': {'warning': 70.0, 'critical': 90.0},
                'memory_percent': {'warning': 80.0, 'critical': 95.0},
                'disk_percent': {'warning': 85.0, 'critical': 95.0},
                'response_time': {'warning': 2.0, 'critical': 5.0},
                'error_rate': {'warning': 5.0, 'critical': 10.0}
            }
        
        # Inicializar base de datos
        self._init_database()
        
        # Estado del sistema
        self.running = False
        self.monitoring_thread = None
        self.alert_thread = None
        
        # Cache de métricas
        self.metrics_cache = deque(maxlen=1000)
        self.alerts_cache = deque(maxlen=100)
        
        # Cola de métricas
        self.metrics_queue = queue.Queue()
        
        # Callbacks de alerta
        self.alert_callbacks = []
        
        # Métricas personalizadas
        self.custom_metrics = {}
        
        logger.info("Performance Monitoring System initialized")
    
    def _init_database(self):
        """Inicializar base de datos de monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de métricas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    component TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            # Tabla de alertas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    current_value REAL NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    component TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT 0
                )
            """)
            
            # Tabla de configuración
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            
            # Índices para optimización
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON performance_metrics(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name 
                ON performance_metrics(name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON performance_alerts(timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Performance monitoring database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing performance database: {e}")
            raise
    
    def start_monitoring(self):
        """Iniciar monitoreo"""
        try:
            if self.running:
                logger.warning("Monitoring already running")
                return
            
            self.running = True
            
            # Iniciar hilo de recolección de métricas
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Iniciar hilo de alertas
            self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
            self.alert_thread.start()
            
            logger.info("Performance monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            raise
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        try:
            self.running = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            if self.alert_thread and self.alert_thread.is_alive():
                self.alert_thread.join(timeout=5)
            
            logger.info("Performance monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        while self.running:
            try:
                # Recolectar métricas del sistema
                if self.config.enable_cpu_monitoring:
                    self._collect_cpu_metrics()
                
                if self.config.enable_memory_monitoring:
                    self._collect_memory_metrics()
                
                if self.config.enable_disk_monitoring:
                    self._collect_disk_metrics()
                
                if self.config.enable_network_monitoring:
                    self._collect_network_metrics()
                
                # Recolectar métricas personalizadas
                if self.config.enable_custom_metrics:
                    self._collect_custom_metrics()
                
                # Procesar cola de métricas
                self._process_metrics_queue()
                
                time.sleep(self.config.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.collection_interval)
    
    def _collect_cpu_metrics(self):
        """Recolectar métricas de CPU"""
        try:
            # CPU por proceso
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Métricas por core
            cpu_per_core = psutil.cpu_percent(percpu=True)
            
            # Agregar métricas
            self._add_metric("cpu_percent", cpu_percent, "system", "cpu", "%")
            self._add_metric("cpu_count", cpu_count, "system", "cpu", "cores")
            
            if cpu_freq:
                self._add_metric("cpu_frequency", cpu_freq.current, "system", "cpu", "MHz")
            
            # Métricas por core
            for i, core_percent in enumerate(cpu_per_core):
                self._add_metric(f"cpu_core_{i}_percent", core_percent, "system", "cpu", "%")
            
            # Load average (solo en sistemas Unix)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
                self._add_metric("load_average_1m", load_avg[0], "system", "cpu", "load")
                self._add_metric("load_average_5m", load_avg[1], "system", "cpu", "load")
                self._add_metric("load_average_15m", load_avg[2], "system", "cpu", "load")
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
    
    def _collect_memory_metrics(self):
        """Recolectar métricas de memoria"""
        try:
            # Memoria virtual
            memory = psutil.virtual_memory()
            self._add_metric("memory_total", memory.total, "system", "memory", "bytes")
            self._add_metric("memory_available", memory.available, "system", "memory", "bytes")
            self._add_metric("memory_used", memory.used, "system", "memory", "bytes")
            self._add_metric("memory_percent", memory.percent, "system", "memory", "%")
            
            # Memoria de intercambio
            swap = psutil.swap_memory()
            self._add_metric("swap_total", swap.total, "system", "memory", "bytes")
            self._add_metric("swap_used", swap.used, "system", "memory", "bytes")
            self._add_metric("swap_percent", swap.percent, "system", "memory", "%")
            
            # Memoria por proceso (top 10)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            for i, proc in enumerate(processes[:10]):
                if proc['memory_percent'] > 0:
                    self._add_metric(
                        f"process_memory_{i+1}",
                        proc['memory_percent'],
                        f"process_{proc['name']}",
                        "memory",
                        "%",
                        {"pid": str(proc['pid']), "name": proc['name']}
                    )
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
    
    def _collect_disk_metrics(self):
        """Recolectar métricas de disco"""
        try:
            # Uso de disco por partición
            disk_usage = psutil.disk_usage('/')
            self._add_metric("disk_total", disk_usage.total, "system", "disk", "bytes")
            self._add_metric("disk_used", disk_usage.used, "system", "disk", "bytes")
            self._add_metric("disk_free", disk_usage.free, "system", "disk", "bytes")
            self._add_metric("disk_percent", (disk_usage.used / disk_usage.total) * 100, "system", "disk", "%")
            
            # I/O de disco
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self._add_metric("disk_read_bytes", disk_io.read_bytes, "system", "disk", "bytes")
                self._add_metric("disk_write_bytes", disk_io.write_bytes, "system", "disk", "bytes")
                self._add_metric("disk_read_count", disk_io.read_count, "system", "disk", "operations")
                self._add_metric("disk_write_count", disk_io.write_count, "system", "disk", "operations")
            
            # Métricas por partición
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partition_name = partition.device.replace('/', '_').replace('\\', '_')
                    
                    self._add_metric(
                        f"disk_{partition_name}_total",
                        partition_usage.total,
                        f"partition_{partition_name}",
                        "disk",
                        "bytes"
                    )
                    
                    self._add_metric(
                        f"disk_{partition_name}_used",
                        partition_usage.used,
                        f"partition_{partition_name}",
                        "disk",
                        "bytes"
                    )
                    
                    self._add_metric(
                        f"disk_{partition_name}_percent",
                        (partition_usage.used / partition_usage.total) * 100,
                        f"partition_{partition_name}",
                        "disk",
                        "%"
                    )
                    
                except (PermissionError, OSError):
                    continue
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
    
    def _collect_network_metrics(self):
        """Recolectar métricas de red"""
        try:
            # Estadísticas de red
            net_io = psutil.net_io_counters()
            if net_io:
                self._add_metric("network_bytes_sent", net_io.bytes_sent, "system", "network", "bytes")
                self._add_metric("network_bytes_recv", net_io.bytes_recv, "system", "network", "bytes")
                self._add_metric("network_packets_sent", net_io.packets_sent, "system", "network", "packets")
                self._add_metric("network_packets_recv", net_io.packets_recv, "system", "network", "packets")
                self._add_metric("network_errin", net_io.errin, "system", "network", "errors")
                self._add_metric("network_errout", net_io.errout, "system", "network", "errors")
                self._add_metric("network_dropin", net_io.dropin, "system", "network", "drops")
                self._add_metric("network_dropout", net_io.dropout, "system", "network", "drops")
            
            # Conexiones de red
            connections = psutil.net_connections()
            self._add_metric("network_connections_total", len(connections), "system", "network", "connections")
            
            # Conexiones por estado
            connection_states = defaultdict(int)
            for conn in connections:
                connection_states[conn.status] += 1
            
            for state, count in connection_states.items():
                self._add_metric(
                    f"network_connections_{state.lower()}",
                    count,
                    "system",
                    "network",
                    "connections",
                    {"state": state}
                )
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
    
    def _collect_custom_metrics(self):
        """Recolectar métricas personalizadas"""
        try:
            for metric_name, metric_func in self.custom_metrics.items():
                try:
                    value = metric_func()
                    self._add_metric(metric_name, value, "custom", "custom", "units")
                except Exception as e:
                    logger.error(f"Error collecting custom metric {metric_name}: {e}")
            
        except Exception as e:
            logger.error(f"Error collecting custom metrics: {e}")
    
    def _add_metric(self, name: str, value: float, component: str, metric_type: str, unit: str, tags: Dict[str, str] = None):
        """Agregar métrica"""
        try:
            metric = PerformanceMetric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                component=component,
                metric_type=metric_type,
                unit=unit,
                tags=tags or {}
            )
            
            # Agregar a cola
            self.metrics_queue.put(metric)
            
            # Agregar a cache
            self.metrics_cache.append(metric)
            
        except Exception as e:
            logger.error(f"Error adding metric: {e}")
    
    def _process_metrics_queue(self):
        """Procesar cola de métricas"""
        try:
            while not self.metrics_queue.empty():
                metric = self.metrics_queue.get_nowait()
                self._store_metric(metric)
                self._check_alert_thresholds(metric)
                
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing metrics queue: {e}")
    
    def _store_metric(self, metric: PerformanceMetric):
        """Almacenar métrica en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics 
                (name, value, timestamp, component, metric_type, unit, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.name,
                metric.value,
                metric.timestamp.isoformat(),
                metric.component,
                metric.metric_type,
                metric.unit,
                json.dumps(metric.tags) if metric.tags else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metric: {e}")
    
    def _check_alert_thresholds(self, metric: PerformanceMetric):
        """Verificar umbrales de alerta"""
        try:
            if metric.name not in self.config.alert_thresholds:
                return
            
            thresholds = self.config.alert_thresholds[metric.name]
            current_value = metric.value
            
            # Determinar severidad
            severity = None
            if 'critical' in thresholds and current_value >= thresholds['critical']:
                severity = 'critical'
            elif 'warning' in thresholds and current_value >= thresholds['warning']:
                severity = 'warning'
            
            if severity:
                # Verificar si ya existe una alerta activa
                if self._has_active_alert(metric.name, severity):
                    return
                
                # Crear alerta
                alert = PerformanceAlert(
                    id=f"{metric.name}_{int(time.time())}",
                    metric_name=metric.name,
                    threshold=thresholds.get(severity, 0),
                    current_value=current_value,
                    severity=severity,
                    message=f"{metric.name} is {current_value:.2f} {metric.unit}, exceeding {severity} threshold of {thresholds.get(severity, 0)} {metric.unit}",
                    timestamp=datetime.now(),
                    component=metric.component
                )
                
                self._store_alert(alert)
                self._trigger_alert_callbacks(alert)
                
        except Exception as e:
            logger.error(f"Error checking alert thresholds: {e}")
    
    def _has_active_alert(self, metric_name: str, severity: str) -> bool:
        """Verificar si existe alerta activa"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM performance_alerts
                WHERE metric_name = ? AND severity = ? AND resolved = 0
                AND timestamp > datetime('now', '-5 minutes')
            """, (metric_name, severity))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking active alerts: {e}")
            return False
    
    def _store_alert(self, alert: PerformanceAlert):
        """Almacenar alerta en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_alerts
                (id, metric_name, threshold, current_value, severity, message, timestamp, component)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.metric_name,
                alert.threshold,
                alert.current_value,
                alert.severity,
                alert.message,
                alert.timestamp.isoformat(),
                alert.component
            ))
            
            conn.commit()
            conn.close()
            
            # Agregar a cache
            self.alerts_cache.append(alert)
            
            logger.warning(f"Performance alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
    
    def _trigger_alert_callbacks(self, alert: PerformanceAlert):
        """Ejecutar callbacks de alerta"""
        try:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering alert callbacks: {e}")
    
    def _alert_loop(self):
        """Loop de procesamiento de alertas"""
        while self.running:
            try:
                # Limpiar alertas antiguas
                self._cleanup_old_alerts()
                
                # Verificar alertas resueltas
                self._check_resolved_alerts()
                
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error in alert loop: {e}")
                time.sleep(60)
    
    def _cleanup_old_alerts(self):
        """Limpiar alertas antiguas"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM performance_alerts
                WHERE timestamp < ? AND resolved = 1
            """, (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error cleaning up old alerts: {e}")
    
    def _check_resolved_alerts(self):
        """Verificar alertas resueltas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener alertas activas
            cursor.execute("""
                SELECT id, metric_name, severity FROM performance_alerts
                WHERE resolved = 0
            """)
            
            active_alerts = cursor.fetchall()
            
            for alert_id, metric_name, severity in active_alerts:
                # Verificar si la métrica está por debajo del umbral
                if self._is_metric_below_threshold(metric_name, severity):
                    cursor.execute("""
                        UPDATE performance_alerts SET resolved = 1
                        WHERE id = ?
                    """, (alert_id,))
                    
                    logger.info(f"Alert resolved: {metric_name}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error checking resolved alerts: {e}")
    
    def _is_metric_below_threshold(self, metric_name: str, severity: str) -> bool:
        """Verificar si métrica está por debajo del umbral"""
        try:
            if metric_name not in self.config.alert_thresholds:
                return False
            
            thresholds = self.config.alert_thresholds[metric_name]
            threshold = thresholds.get(severity, 0)
            
            # Obtener valor actual de la métrica
            current_metrics = [m for m in self.metrics_cache if m.name == metric_name]
            if not current_metrics:
                return False
            
            current_value = current_metrics[-1].value
            return current_value < threshold * 0.9  # 10% de margen
            
        except Exception as e:
            logger.error(f"Error checking metric threshold: {e}")
            return False
    
    def add_custom_metric(self, name: str, metric_func: Callable[[], float]):
        """Agregar métrica personalizada"""
        try:
            self.custom_metrics[name] = metric_func
            logger.info(f"Custom metric added: {name}")
            
        except Exception as e:
            logger.error(f"Error adding custom metric: {e}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Agregar callback de alerta"""
        try:
            self.alert_callbacks.append(callback)
            logger.info("Alert callback added")
            
        except Exception as e:
            logger.error(f"Error adding alert callback: {e}")
    
    def get_metrics(self, metric_name: str = None, component: str = None, 
                   start_time: datetime = None, end_time: datetime = None, 
                   limit: int = 1000) -> List[PerformanceMetric]:
        """Obtener métricas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT name, value, timestamp, component, metric_type, unit, tags FROM performance_metrics WHERE 1=1"
            params = []
            
            if metric_name:
                query += " AND name = ?"
                params.append(metric_name)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            metrics = []
            for result in results:
                metrics.append(PerformanceMetric(
                    name=result[0],
                    value=result[1],
                    timestamp=datetime.fromisoformat(result[2]),
                    component=result[3],
                    metric_type=result[4],
                    unit=result[5],
                    tags=json.loads(result[6]) if result[6] else {}
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    def get_alerts(self, severity: str = None, resolved: bool = None, 
                  start_time: datetime = None, end_time: datetime = None,
                  limit: int = 100) -> List[PerformanceAlert]:
        """Obtener alertas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, metric_name, threshold, current_value, severity, message, timestamp, component, resolved FROM performance_alerts WHERE 1=1"
            params = []
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if resolved is not None:
                query += " AND resolved = ?"
                params.append(1 if resolved else 0)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            alerts = []
            for result in results:
                alerts.append(PerformanceAlert(
                    id=result[0],
                    metric_name=result[1],
                    threshold=result[2],
                    current_value=result[3],
                    severity=result[4],
                    message=result[5],
                    timestamp=datetime.fromisoformat(result[6]),
                    component=result[7],
                    resolved=bool(result[8])
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de rendimiento"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Obtener métricas principales
            cpu_metrics = self.get_metrics("cpu_percent", start_time=start_time, end_time=end_time)
            memory_metrics = self.get_metrics("memory_percent", start_time=start_time, end_time=end_time)
            disk_metrics = self.get_metrics("disk_percent", start_time=start_time, end_time=end_time)
            
            # Calcular estadísticas
            summary = {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'hours': hours
                },
                'cpu': self._calculate_metric_stats(cpu_metrics),
                'memory': self._calculate_metric_stats(memory_metrics),
                'disk': self._calculate_metric_stats(disk_metrics),
                'alerts': {
                    'total': len(self.get_alerts(start_time=start_time, end_time=end_time)),
                    'critical': len(self.get_alerts(severity='critical', start_time=start_time, end_time=end_time)),
                    'warning': len(self.get_alerts(severity='warning', start_time=start_time, end_time=end_time)),
                    'active': len(self.get_alerts(resolved=False))
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    def _calculate_metric_stats(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calcular estadísticas de métricas"""
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'latest': values[-1] if values else 0
        }
    
    def create_performance_dashboard(self, hours: int = 24) -> str:
        """Crear dashboard de rendimiento"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Obtener métricas
            cpu_metrics = self.get_metrics("cpu_percent", start_time=start_time, end_time=end_time)
            memory_metrics = self.get_metrics("memory_percent", start_time=start_time, end_time=end_time)
            disk_metrics = self.get_metrics("disk_percent", start_time=start_time, end_time=end_time)
            
            # Crear gráficos
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage'),
                vertical_spacing=0.1
            )
            
            # CPU
            if cpu_metrics:
                cpu_times = [m.timestamp for m in cpu_metrics]
                cpu_values = [m.value for m in cpu_metrics]
                fig.add_trace(
                    go.Scatter(x=cpu_times, y=cpu_values, name='CPU %', line=dict(color='blue')),
                    row=1, col=1
                )
            
            # Memory
            if memory_metrics:
                memory_times = [m.timestamp for m in memory_metrics]
                memory_values = [m.value for m in memory_metrics]
                fig.add_trace(
                    go.Scatter(x=memory_times, y=memory_values, name='Memory %', line=dict(color='green')),
                    row=2, col=1
                )
            
            # Disk
            if disk_metrics:
                disk_times = [m.timestamp for m in disk_metrics]
                disk_values = [m.value for m in disk_metrics]
                fig.add_trace(
                    go.Scatter(x=disk_times, y=disk_values, name='Disk %', line=dict(color='red')),
                    row=3, col=1
                )
            
            fig.update_layout(
                title=f'Performance Dashboard - Last {hours} Hours',
                height=800,
                template='plotly_white'
            )
            
            # Guardar dashboard
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_dashboard_{timestamp}.html"
            filepath = Path("performance_dashboards") / filename
            filepath.parent.mkdir(exist_ok=True)
            
            fig.write_html(str(filepath))
            
            logger.info(f"Performance dashboard created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating performance dashboard: {e}")
            raise

def main():
    """Función principal para demostrar sistema de monitoreo"""
    print("=" * 60)
    print("PERFORMANCE MONITORING SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de monitoreo
    monitoring = PerformanceMonitoringSystem()
    
    # Agregar métrica personalizada de ejemplo
    def custom_response_time():
        import random
        return random.uniform(0.1, 2.0)  # Simular tiempo de respuesta
    
    monitoring.add_custom_metric("response_time", custom_response_time)
    
    # Agregar callback de alerta
    def alert_callback(alert):
        print(f"🚨 ALERT: {alert.message}")
    
    monitoring.add_alert_callback(alert_callback)
    
    # Iniciar monitoreo
    print("Starting performance monitoring...")
    monitoring.start_monitoring()
    
    # Simular funcionamiento
    print("Monitoring system performance for 30 seconds...")
    time.sleep(30)
    
    # Obtener resumen de rendimiento
    print("\nPerformance Summary (last 30 seconds):")
    summary = monitoring.get_performance_summary(hours=1)
    
    if summary:
        print(f"CPU: {summary['cpu'].get('avg', 0):.1f}% (avg)")
        print(f"Memory: {summary['memory'].get('avg', 0):.1f}% (avg)")
        print(f"Disk: {summary['disk'].get('avg', 0):.1f}% (avg)")
        print(f"Alerts: {summary['alerts']['total']} total, {summary['alerts']['active']} active")
    
    # Crear dashboard
    print("\nCreating performance dashboard...")
    dashboard_path = monitoring.create_performance_dashboard(hours=1)
    print(f"✓ Dashboard created: {dashboard_path}")
    
    # Obtener alertas
    print("\nRecent alerts:")
    alerts = monitoring.get_alerts(limit=5)
    for alert in alerts:
        status = "RESOLVED" if alert.resolved else "ACTIVE"
        print(f"  • {alert.severity.upper()}: {alert.message} [{status}]")
    
    # Detener monitoreo
    print("\nStopping monitoring...")
    monitoring.stop_monitoring()
    
    print("\n" + "=" * 60)
    print("PERFORMANCE MONITORING DEMO COMPLETED")
    print("=" * 60)
    print("📊 Performance monitoring features:")
    print("  • Real-time system metrics collection")
    print("  • CPU, memory, disk, and network monitoring")
    print("  • Custom metrics support")
    print("  • Alert threshold monitoring")
    print("  • Performance dashboards")
    print("  • Historical data analysis")
    print("  • Automatic alert resolution")

if __name__ == "__main__":
    main()






