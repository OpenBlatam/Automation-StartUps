"""
Advanced Metrics and Monitoring System for Ultimate Launch Planning System
Provides real-time metrics, performance monitoring, and business intelligence
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"

@dataclass
class MetricData:
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: MetricType
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "type": self.metric_type.value
        }

class MetricsCollector:
    """Advanced metrics collection system"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
        self.start_time = time.time()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_metrics, daemon=True)
        self.cleanup_thread.start()
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.counters[key] += value
            self._record_metric(name, self.counters[key], MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value
            self._record_metric(name, value, MetricType.GAUGE, labels)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.histograms[key].append(value)
            self._record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    def time_function(self, name: str, labels: Dict[str, str] = None):
        """Decorator to time function execution"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.observe_timer(name, duration, labels)
            return wrapper
        return decorator
    
    def observe_timer(self, name: str, duration: float, labels: Dict[str, str] = None):
        """Observe a timer metric"""
        with self.lock:
            key = self._make_key(name, labels)
            self.timers[key].append(duration)
            self._record_metric(name, duration, MetricType.TIMER, labels)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for metric storage"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, labels: Dict[str, str] = None):
        """Record a metric data point"""
        metric_data = MetricData(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            metric_type=metric_type
        )
        self.metrics[name].append(metric_data)
    
    def get_metric_summary(self, name: str, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            recent_metrics = [
                m for m in self.metrics[name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"name": name, "count": 0, "error": "No data in time window"}
            
            values = [m.value for m in recent_metrics]
            
            return {
                "name": name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)],
                "time_window_minutes": time_window_minutes
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        with self.lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histogram_stats": {
                    name: {
                        "count": len(values),
                        "min": min(values) if values else 0,
                        "max": max(values) if values else 0,
                        "mean": sum(values) / len(values) if values else 0
                    }
                    for name, values in self.histograms.items()
                },
                "timer_stats": {
                    name: {
                        "count": len(values),
                        "min": min(values) if values else 0,
                        "max": max(values) if values else 0,
                        "mean": sum(values) / len(values) if values else 0
                    }
                    for name, values in self.timers.items()
                },
                "uptime_seconds": time.time() - self.start_time
            }
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory leaks"""
        while True:
            time.sleep(3600)  # Run every hour
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            
            with self.lock:
                for name, metric_deque in self.metrics.items():
                    while metric_deque and metric_deque[0].timestamp < cutoff_time:
                        metric_deque.popleft()

class LaunchMetrics:
    """Specialized metrics for launch planning"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self._setup_launch_metrics()
    
    def _setup_launch_metrics(self):
        """Initialize launch-specific metrics"""
        # Launch phase metrics
        self.collector.set_gauge("launch_phase_current", 0, {"phase": "none"})
        self.collector.set_gauge("launch_tasks_total", 0)
        self.collector.set_gauge("launch_tasks_completed", 0)
        self.collector.set_gauge("launch_tasks_failed", 0)
        
        # Performance metrics
        self.collector.set_gauge("launch_planning_duration_seconds", 0)
        self.collector.set_gauge("launch_success_probability", 0.0)
        
        # Business metrics
        self.collector.set_gauge("launch_budget_allocated", 0.0)
        self.collector.set_gauge("launch_budget_spent", 0.0)
        self.collector.set_gauge("launch_roi_expected", 0.0)
    
    def track_phase_start(self, phase: str):
        """Track launch phase start"""
        self.collector.set_gauge("launch_phase_current", 1, {"phase": phase})
        self.collector.increment_counter("launch_phase_starts", labels={"phase": phase})
    
    def track_phase_complete(self, phase: str, duration: float):
        """Track launch phase completion"""
        self.collector.set_gauge("launch_phase_current", 0, {"phase": "none"})
        self.collector.increment_counter("launch_phase_completions", labels={"phase": phase})
        self.collector.observe_timer("launch_phase_duration", duration, {"phase": phase})
    
    def track_task_completion(self, task_type: str, success: bool, duration: float):
        """Track task completion"""
        if success:
            self.collector.increment_counter("launch_tasks_completed", labels={"type": task_type})
        else:
            self.collector.increment_counter("launch_tasks_failed", labels={"type": task_type})
        
        self.collector.observe_timer("launch_task_duration", duration, {
            "type": task_type,
            "success": str(success)
        })
    
    def update_budget_metrics(self, allocated: float, spent: float):
        """Update budget-related metrics"""
        self.collector.set_gauge("launch_budget_allocated", allocated)
        self.collector.set_gauge("launch_budget_spent", spent)
        self.collector.set_gauge("launch_budget_utilization", spent / allocated if allocated > 0 else 0)
    
    def update_success_probability(self, probability: float):
        """Update launch success probability"""
        self.collector.set_gauge("launch_success_probability", probability)
    
    def track_ai_prediction(self, model_name: str, accuracy: float, prediction_time: float):
        """Track AI model predictions"""
        self.collector.observe_histogram("ai_prediction_accuracy", accuracy, {"model": model_name})
        self.collector.observe_timer("ai_prediction_time", prediction_time, {"model": model_name})
        self.collector.increment_counter("ai_predictions_total", labels={"model": model_name})

class PerformanceMonitor:
    """System performance monitoring"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background performance monitoring"""
        def monitor_loop():
            while True:
                try:
                    self._collect_system_metrics()
                    time.sleep(30)  # Collect every 30 seconds
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.collector.set_gauge("system_cpu_percent", cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.collector.set_gauge("system_memory_percent", memory.percent)
            self.collector.set_gauge("system_memory_available_mb", memory.available / 1024 / 1024)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.collector.set_gauge("system_disk_percent", disk.percent)
            self.collector.set_gauge("system_disk_free_gb", disk.free / 1024 / 1024 / 1024)
            
            # Process metrics
            process = psutil.Process()
            self.collector.set_gauge("process_memory_mb", process.memory_info().rss / 1024 / 1024)
            self.collector.set_gauge("process_cpu_percent", process.cpu_percent())
            
        except ImportError:
            logger.warning("psutil not available for system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

class MetricsAPI:
    """REST API for metrics access"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def get_metrics_endpoint(self) -> Dict[str, Any]:
        """Get metrics in Prometheus format"""
        metrics = self.collector.get_all_metrics()
        
        # Convert to Prometheus format
        prometheus_metrics = []
        
        # Counters
        for name, value in metrics["counters"].items():
            prometheus_metrics.append(f"# TYPE {name} counter")
            prometheus_metrics.append(f"{name} {value}")
        
        # Gauges
        for name, value in metrics["gauges"].items():
            prometheus_metrics.append(f"# TYPE {name} gauge")
            prometheus_metrics.append(f"{name} {value}")
        
        return {
            "format": "prometheus",
            "metrics": "\n".join(prometheus_metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics_json(self) -> Dict[str, Any]:
        """Get metrics in JSON format"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.collector.get_all_metrics()
        }
    
    def get_metric_summary(self, name: str, time_window: int = 60) -> Dict[str, Any]:
        """Get summary for a specific metric"""
        return self.collector.get_metric_summary(name, time_window)

# Global metrics instance
_metrics_collector = None
_launch_metrics = None
_performance_monitor = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_launch_metrics() -> LaunchMetrics:
    """Get global launch metrics instance"""
    global _launch_metrics
    if _launch_metrics is None:
        _launch_metrics = LaunchMetrics(get_metrics_collector())
    return _launch_metrics

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(get_metrics_collector())
    return _performance_monitor

def get_metrics_api() -> MetricsAPI:
    """Get global metrics API instance"""
    return MetricsAPI(get_metrics_collector())

# Example usage
if __name__ == "__main__":
    # Initialize metrics
    collector = get_metrics_collector()
    launch_metrics = get_launch_metrics()
    performance_monitor = get_performance_monitor()
    metrics_api = get_metrics_api()
    
    # Example metrics collection
    launch_metrics.track_phase_start("pre_launch")
    time.sleep(1)
    launch_metrics.track_phase_complete("pre_launch", 1.0)
    
    launch_metrics.track_task_completion("market_research", True, 0.5)
    launch_metrics.track_task_completion("competitor_analysis", False, 2.0)
    
    launch_metrics.update_budget_metrics(100000.0, 25000.0)
    launch_metrics.update_success_probability(0.85)
    
    # Get metrics
    print("All Metrics:")
    print(json.dumps(metrics_api.get_metrics_json(), indent=2))
    
    print("\nPrometheus Format:")
    print(metrics_api.get_metrics_endpoint()["metrics"])
    
    print("\nTask Duration Summary:")
    print(json.dumps(collector.get_metric_summary("launch_task_duration"), indent=2))







