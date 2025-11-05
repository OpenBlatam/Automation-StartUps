#!/usr/bin/env python3
"""
ClickUp Brain Performance Monitoring
===================================

Performance metrics, monitoring, and optimization tools.
"""

import time
import psutil
import threading
import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging
from pathlib import Path
from contextlib import contextmanager
import functools

ROOT = Path(__file__).parent

@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    timestamp: datetime
    unit: str = "ms"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: List[float] = field(default_factory=list)

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime
    active_connections: int
    requests_per_second: float
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    cache_hit_rate: float
    queue_size: int
    processing_time_avg: float

class PerformanceCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.system_metrics: deque = deque(maxlen=max_history)
        self.app_metrics: deque = deque(maxlen=max_history)
        self._lock = threading.Lock()
        self._running = False
        self._collector_thread: Optional[threading.Thread] = None
    
    def start_collection(self, interval: float = 1.0) -> None:
        """Start automatic metric collection."""
        if self._running:
            return
        
        self._running = True
        self._collector_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval,),
            daemon=True
        )
        self._collector_thread.start()
        logging.info("Performance collection started")
    
    def stop_collection(self) -> None:
        """Stop automatic metric collection."""
        self._running = False
        if self._collector_thread:
            self._collector_thread.join(timeout=5)
        logging.info("Performance collection stopped")
    
    def _collection_loop(self, interval: float) -> None:
        """Main collection loop."""
        while self._running:
            try:
                self.collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"Error in performance collection: {e}")
                time.sleep(interval)
    
    def collect_system_metrics(self) -> None:
        """Collect system resource metrics."""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = []
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                network_sent_mb=network.bytes_sent / (1024 * 1024),
                network_recv_mb=network.bytes_recv / (1024 * 1024),
                process_count=process_count,
                load_average=load_avg
            )
            
            with self._lock:
                self.system_metrics.append(metrics)
                
        except Exception as e:
            logging.error(f"Failed to collect system metrics: {e}")
    
    def add_metric(self, name: str, value: float, unit: str = "ms", tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a custom performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            unit=unit,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        with self._lock:
            self.metrics[name].append(metric)
    
    def add_app_metrics(self, metrics: ApplicationMetrics) -> None:
        """Add application metrics."""
        with self._lock:
            self.app_metrics.append(metrics)
    
    def get_metrics_summary(self, time_window: timedelta = timedelta(minutes=5)) -> Dict[str, Any]:
        """Get metrics summary for the specified time window."""
        cutoff_time = datetime.now() - time_window
        
        with self._lock:
            summary = {
                'system_metrics': self._get_system_summary(cutoff_time),
                'custom_metrics': self._get_custom_metrics_summary(cutoff_time),
                'app_metrics': self._get_app_metrics_summary(cutoff_time)
            }
        
        return summary
    
    def _get_system_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Get system metrics summary."""
        recent_metrics = [m for m in self.system_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        return {
            'cpu_avg': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'cpu_max': max(m.cpu_percent for m in recent_metrics),
            'memory_avg': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'memory_max': max(m.memory_percent for m in recent_metrics),
            'disk_usage_avg': sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics),
            'network_sent_total': sum(m.network_sent_mb for m in recent_metrics),
            'network_recv_total': sum(m.network_recv_mb for m in recent_metrics),
            'process_count_avg': sum(m.process_count for m in recent_metrics) / len(recent_metrics)
        }
    
    def _get_custom_metrics_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Get custom metrics summary."""
        summary = {}
        
        for metric_name, metrics_deque in self.metrics.items():
            recent_metrics = [m for m in metrics_deque if m.timestamp >= cutoff_time]
            
            if recent_metrics:
                values = [m.value for m in recent_metrics]
                summary[metric_name] = {
                    'count': len(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'unit': recent_metrics[0].unit
                }
        
        return summary
    
    def _get_app_metrics_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Get application metrics summary."""
        recent_metrics = [m for m in self.app_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        return {
            'requests_per_second_avg': sum(m.requests_per_second for m in recent_metrics) / len(recent_metrics),
            'response_time_avg': sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics),
            'response_time_p95_avg': sum(m.response_time_p95 for m in recent_metrics) / len(recent_metrics),
            'error_rate_avg': sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            'cache_hit_rate_avg': sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics)
        }

class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self):
        self.collector = PerformanceCollector()
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds: Dict[str, Dict[str, float]] = {
            'cpu_percent': {'warning': 80, 'critical': 95},
            'memory_percent': {'warning': 85, 'critical': 95},
            'disk_usage_percent': {'warning': 80, 'critical': 90},
            'response_time_avg': {'warning': 1000, 'critical': 5000},
            'error_rate': {'warning': 0.05, 'critical': 0.1}
        }
        self._lock = threading.Lock()
    
    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start performance monitoring."""
        self.collector.start_collection(interval)
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.collector.stop_collection()
        logging.info("Performance monitoring stopped")
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts."""
        summary = self.collector.get_metrics_summary(timedelta(minutes=1))
        new_alerts = []
        
        # Check system metrics
        system_metrics = summary.get('system_metrics', {})
        for metric, thresholds in self.thresholds.items():
            if metric in system_metrics:
                value = system_metrics[metric]
                if value >= thresholds['critical']:
                    alert = {
                        'level': 'critical',
                        'metric': metric,
                        'value': value,
                        'threshold': thresholds['critical'],
                        'timestamp': datetime.now()
                    }
                    new_alerts.append(alert)
                elif value >= thresholds['warning']:
                    alert = {
                        'level': 'warning',
                        'metric': metric,
                        'value': value,
                        'threshold': thresholds['warning'],
                        'timestamp': datetime.now()
                    }
                    new_alerts.append(alert)
        
        # Store alerts
        with self._lock:
            self.alerts.extend(new_alerts)
            # Keep only recent alerts
            cutoff = datetime.now() - timedelta(hours=24)
            self.alerts = [a for a in self.alerts if a['timestamp'] >= cutoff]
        
        return new_alerts
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        summary = self.collector.get_metrics_summary(timedelta(hours=1))
        
        with self._lock:
            recent_alerts = [a for a in self.alerts if a['timestamp'] >= datetime.now() - timedelta(hours=1)]
        
        return {
            'timestamp': datetime.now(),
            'summary': summary,
            'alerts': recent_alerts,
            'health_score': self._calculate_health_score(summary, recent_alerts)
        }
    
    def _calculate_health_score(self, summary: Dict[str, Any], alerts: List[Dict[str, Any]]) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        # Deduct points for alerts
        for alert in alerts:
            if alert['level'] == 'critical':
                score -= 20
            elif alert['level'] == 'warning':
                score -= 10
        
        # Deduct points for high resource usage
        system_metrics = summary.get('system_metrics', {})
        if system_metrics.get('cpu_avg', 0) > 80:
            score -= 15
        if system_metrics.get('memory_avg', 0) > 85:
            score -= 15
        
        return max(0, score)

@contextmanager
def performance_timer(metric_name: str, collector: Optional[PerformanceCollector] = None):
    """Context manager for timing operations."""
    if collector is None:
        collector = PerformanceCollector()
    
    start_time = time.time()
    try:
        yield
    finally:
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        collector.add_metric(metric_name, duration, "ms")

def performance_monitor(metric_name: str, collector: Optional[PerformanceCollector] = None):
    """Decorator for monitoring function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with performance_timer(f"{metric_name}_{func.__name__}", collector):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def async_performance_monitor(metric_name: str, collector: Optional[PerformanceCollector] = None):
    """Decorator for monitoring async function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = (time.time() - start_time) * 1000
                if collector is None:
                    collector = PerformanceCollector()
                collector.add_metric(f"{metric_name}_{func.__name__}", duration, "ms")
        return wrapper
    return decorator

# Global performance monitor instance
performance_monitor_instance = PerformanceMonitor()

def start_performance_monitoring(interval: float = 1.0) -> None:
    """Start global performance monitoring."""
    performance_monitor_instance.start_monitoring(interval)

def stop_performance_monitoring() -> None:
    """Stop global performance monitoring."""
    performance_monitor_instance.stop_monitoring()

def get_performance_report() -> Dict[str, Any]:
    """Get global performance report."""
    return performance_monitor_instance.get_performance_report()

def add_performance_metric(name: str, value: float, unit: str = "ms", tags: Optional[Dict[str, str]] = None) -> None:
    """Add a performance metric to the global collector."""
    performance_monitor_instance.collector.add_metric(name, value, unit, tags)

if __name__ == "__main__":
    # Demo performance monitoring system
    print("ClickUp Brain Performance Monitoring Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Start monitoring
    start_performance_monitoring(interval=0.5)
    
    # Test performance monitoring decorator
    @performance_monitor("demo")
    def slow_operation():
        time.sleep(0.1)
        return "Operation completed"
    
    @async_performance_monitor("demo")
    async def async_slow_operation():
        await asyncio.sleep(0.1)
        return "Async operation completed"
    
    # Run some operations
    for i in range(5):
        result = slow_operation()
        print(f"Operation {i+1}: {result}")
        
        # Add custom metrics
        add_performance_metric("custom_metric", i * 10, "count", {"iteration": str(i)})
    
    # Test async operation
    async def run_async_demo():
        result = await async_slow_operation()
        print(f"Async operation: {result}")
    
    asyncio.run(run_async_demo())
    
    # Wait a bit for metrics collection
    time.sleep(2)
    
    # Get performance report
    report = get_performance_report()
    print(f"\nPerformance Report:")
    print(f"Health Score: {report['health_score']:.1f}")
    print(f"System Metrics: {json.dumps(report['summary']['system_metrics'], indent=2)}")
    print(f"Custom Metrics: {json.dumps(report['summary']['custom_metrics'], indent=2)}")
    
    # Check for alerts
    alerts = performance_monitor_instance.check_alerts()
    if alerts:
        print(f"\nAlerts: {json.dumps(alerts, indent=2, default=str)}")
    else:
        print("\nNo alerts detected")
    
    # Stop monitoring
    stop_performance_monitoring()
    
    print("\nPerformance monitoring demo completed!")









