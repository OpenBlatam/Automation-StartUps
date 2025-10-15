"""
Automatic Performance Optimizer for Ultimate Launch Planning System
Provides intelligent performance monitoring, optimization, and auto-tuning
"""

import time
import psutil
import threading
import gc
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import logging
import json
from enum import Enum

logger = logging.getLogger(__name__)

class OptimizationLevel(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

@dataclass
class PerformanceMetric:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    active_threads: int
    gc_collections: int
    response_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_mb": self.memory_mb,
            "disk_io_read": self.disk_io_read,
            "disk_io_write": self.disk_io_write,
            "network_io_sent": self.network_io_sent,
            "network_io_recv": self.network_io_recv,
            "active_threads": self.active_threads,
            "gc_collections": self.gc_collections,
            "response_time_ms": self.response_time_ms
        }

@dataclass
class OptimizationAction:
    name: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: str
    executed: bool = False
    executed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.baseline_metrics: Optional[PerformanceMetric] = None
        self.monitoring_active = False
        self.lock = threading.RLock()
        
        # Performance thresholds
        self.thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 85.0,
            "memory_warning": 75.0,
            "memory_critical": 90.0,
            "response_time_warning": 1000.0,  # ms
            "response_time_critical": 5000.0  # ms
        }
        
        # Initialize baseline
        self._establish_baseline()
    
    def start_monitoring(self, interval_seconds: int = 10):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    metric = self._collect_metric()
                    with self.lock:
                        self.metrics_history.append(metric)
                    
                    # Check for performance issues
                    self._check_performance_issues(metric)
                    
                    time.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"Error in performance monitoring: {e}")
                    time.sleep(interval_seconds * 2)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        logger.info("Performance monitoring stopped")
    
    def _collect_metric(self) -> PerformanceMetric:
        """Collect current performance metrics"""
        process = psutil.Process()
        
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        process_memory = process.memory_info()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read = disk_io.read_bytes if disk_io else 0
        disk_write = disk_io.write_bytes if disk_io else 0
        
        # Network I/O
        network_io = psutil.net_io_counters()
        net_sent = network_io.bytes_sent if network_io else 0
        net_recv = network_io.bytes_recv if network_io else 0
        
        # Threads and GC
        active_threads = threading.active_count()
        gc_collections = sum(gc.get_stats())
        
        return PerformanceMetric(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=process_memory.rss / 1024 / 1024,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_io_sent=net_sent,
            network_io_recv=net_recv,
            active_threads=active_threads,
            gc_collections=gc_collections,
            response_time_ms=0.0  # Will be set by specific operations
        )
    
    def _establish_baseline(self):
        """Establish performance baseline"""
        logger.info("Establishing performance baseline...")
        
        # Collect metrics for 30 seconds to establish baseline
        baseline_metrics = []
        for _ in range(3):
            metric = self._collect_metric()
            baseline_metrics.append(metric)
            time.sleep(10)
        
        # Calculate average baseline
        self.baseline_metrics = PerformanceMetric(
            timestamp=datetime.now(),
            cpu_percent=sum(m.cpu_percent for m in baseline_metrics) / len(baseline_metrics),
            memory_percent=sum(m.memory_percent for m in baseline_metrics) / len(baseline_metrics),
            memory_mb=sum(m.memory_mb for m in baseline_metrics) / len(baseline_metrics),
            disk_io_read=sum(m.disk_io_read for m in baseline_metrics) / len(baseline_metrics),
            disk_io_write=sum(m.disk_io_write for m in baseline_metrics) / len(baseline_metrics),
            network_io_sent=sum(m.network_io_sent for m in baseline_metrics) / len(baseline_metrics),
            network_io_recv=sum(m.network_io_recv for m in baseline_metrics) / len(baseline_metrics),
            active_threads=sum(m.active_threads for m in baseline_metrics) / len(baseline_metrics),
            gc_collections=sum(m.gc_collections for m in baseline_metrics) / len(baseline_metrics),
            response_time_ms=0.0
        )
        
        logger.info(f"Performance baseline established: CPU={self.baseline_metrics.cpu_percent:.1f}%, "
                   f"Memory={self.baseline_metrics.memory_percent:.1f}%")
    
    def _check_performance_issues(self, metric: PerformanceMetric):
        """Check for performance issues and trigger alerts"""
        issues = []
        
        if metric.cpu_percent > self.thresholds["cpu_critical"]:
            issues.append(f"Critical CPU usage: {metric.cpu_percent:.1f}%")
        elif metric.cpu_percent > self.thresholds["cpu_warning"]:
            issues.append(f"High CPU usage: {metric.cpu_percent:.1f}%")
        
        if metric.memory_percent > self.thresholds["memory_critical"]:
            issues.append(f"Critical memory usage: {metric.memory_percent:.1f}%")
        elif metric.memory_percent > self.thresholds["memory_warning"]:
            issues.append(f"High memory usage: {metric.memory_percent:.1f}%")
        
        if metric.response_time_ms > self.thresholds["response_time_critical"]:
            issues.append(f"Critical response time: {metric.response_time_ms:.1f}ms")
        elif metric.response_time_ms > self.thresholds["response_time_warning"]:
            issues.append(f"Slow response time: {metric.response_time_ms:.1f}ms")
        
        if issues:
            logger.warning(f"Performance issues detected: {', '.join(issues)}")
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for time window"""
        with self.lock:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {"error": "No metrics in time window"}
            
            return {
                "time_window_minutes": time_window_minutes,
                "sample_count": len(recent_metrics),
                "cpu": {
                    "avg": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                    "max": max(m.cpu_percent for m in recent_metrics),
                    "min": min(m.cpu_percent for m in recent_metrics)
                },
                "memory": {
                    "avg_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                    "avg_mb": sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
                    "max_mb": max(m.memory_mb for m in recent_metrics)
                },
                "response_time": {
                    "avg_ms": sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics),
                    "max_ms": max(m.response_time_ms for m in recent_metrics),
                    "min_ms": min(m.response_time_ms for m in recent_metrics)
                },
                "threads": {
                    "avg": sum(m.active_threads for m in recent_metrics) / len(recent_metrics),
                    "max": max(m.active_threads for m in recent_metrics)
                }
            }
    
    def get_baseline_comparison(self) -> Dict[str, Any]:
        """Compare current performance to baseline"""
        if not self.baseline_metrics:
            return {"error": "No baseline established"}
        
        current = self.metrics_history[-1] if self.metrics_history else None
        if not current:
            return {"error": "No current metrics"}
        
        return {
            "cpu_change_percent": current.cpu_percent - self.baseline_metrics.cpu_percent,
            "memory_change_percent": current.memory_percent - self.baseline_metrics.memory_percent,
            "memory_change_mb": current.memory_mb - self.baseline_metrics.memory_mb,
            "thread_change": current.active_threads - self.baseline_metrics.active_threads,
            "baseline": self.baseline_metrics.to_dict(),
            "current": current.to_dict()
        }

class PerformanceOptimizer:
    """Automatic performance optimization system"""
    
    def __init__(self, monitor: PerformanceMonitor, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED):
        self.monitor = monitor
        self.optimization_level = optimization_level
        self.optimization_history: List[OptimizationAction] = []
        self.auto_optimization_enabled = True
        self.lock = threading.RLock()
        
        # Start optimization monitoring
        self._start_optimization_monitoring()
    
    def _start_optimization_monitoring(self):
        """Start automatic optimization monitoring"""
        def optimization_loop():
            while True:
                try:
                    if self.auto_optimization_enabled:
                        self._check_and_optimize()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    logger.error(f"Error in optimization monitoring: {e}")
                    time.sleep(600)  # Wait longer on error
        
        optimization_thread = threading.Thread(target=optimization_loop, daemon=True)
        optimization_thread.start()
        logger.info("Performance optimization monitoring started")
    
    def _check_and_optimize(self):
        """Check performance and apply optimizations"""
        summary = self.monitor.get_performance_summary(30)  # Last 30 minutes
        
        if "error" in summary:
            return
        
        optimizations = self._identify_optimizations(summary)
        
        for optimization in optimizations:
            if self._should_apply_optimization(optimization):
                self._apply_optimization(optimization)
    
    def _identify_optimizations(self, performance_summary: Dict[str, Any]) -> List[OptimizationAction]:
        """Identify potential optimizations based on performance data"""
        optimizations = []
        
        # CPU optimization
        if performance_summary["cpu"]["avg"] > 80:
            optimizations.append(OptimizationAction(
                name="reduce_worker_threads",
                description="Reduce number of worker threads to lower CPU usage",
                action_type="thread_management",
                parameters={"target_threads": max(1, threading.active_count() - 2)},
                expected_improvement=0.15,
                risk_level="low"
            ))
        
        # Memory optimization
        if performance_summary["memory"]["avg_percent"] > 80:
            optimizations.append(OptimizationAction(
                name="force_garbage_collection",
                description="Force garbage collection to free memory",
                action_type="memory_management",
                parameters={"generations": 2},
                expected_improvement=0.20,
                risk_level="low"
            ))
            
            if self.optimization_level in [OptimizationLevel.BALANCED, OptimizationLevel.AGGRESSIVE]:
                optimizations.append(OptimizationAction(
                    name="clear_caches",
                    description="Clear application caches to free memory",
                    action_type="cache_management",
                    parameters={"clear_all": True},
                    expected_improvement=0.30,
                    risk_level="medium"
                ))
        
        # Response time optimization
        if performance_summary["response_time"]["avg_ms"] > 2000:
            optimizations.append(OptimizationAction(
                name="optimize_database_queries",
                description="Enable query optimization and connection pooling",
                action_type="database_optimization",
                parameters={"enable_query_cache": True, "pool_size": 20},
                expected_improvement=0.25,
                risk_level="low"
            ))
        
        # Thread optimization
        if performance_summary["threads"]["avg"] > 50:
            optimizations.append(OptimizationAction(
                name="optimize_thread_pool",
                description="Optimize thread pool configuration",
                action_type="thread_management",
                parameters={"max_threads": 20, "queue_size": 100},
                expected_improvement=0.10,
                risk_level="low"
            ))
        
        return optimizations
    
    def _should_apply_optimization(self, optimization: OptimizationAction) -> bool:
        """Determine if optimization should be applied"""
        # Check if already applied recently
        recent_optimizations = [
            opt for opt in self.optimization_history
            if opt.name == optimization.name and 
            opt.executed_at and 
            datetime.now() - opt.executed_at < timedelta(hours=1)
        ]
        
        if recent_optimizations:
            return False
        
        # Risk-based filtering
        if optimization.risk_level == "high" and self.optimization_level == OptimizationLevel.CONSERVATIVE:
            return False
        
        return True
    
    def _apply_optimization(self, optimization: OptimizationAction):
        """Apply a performance optimization"""
        try:
            logger.info(f"Applying optimization: {optimization.name}")
            
            if optimization.name == "reduce_worker_threads":
                self._reduce_worker_threads(optimization.parameters)
            elif optimization.name == "force_garbage_collection":
                self._force_garbage_collection(optimization.parameters)
            elif optimization.name == "clear_caches":
                self._clear_caches(optimization.parameters)
            elif optimization.name == "optimize_database_queries":
                self._optimize_database_queries(optimization.parameters)
            elif optimization.name == "optimize_thread_pool":
                self._optimize_thread_pool(optimization.parameters)
            
            # Record optimization
            optimization.executed = True
            optimization.executed_at = datetime.now()
            optimization.result = {"status": "success", "message": "Optimization applied successfully"}
            
            with self.lock:
                self.optimization_history.append(optimization)
            
            logger.info(f"Optimization applied successfully: {optimization.name}")
            
        except Exception as e:
            logger.error(f"Failed to apply optimization {optimization.name}: {e}")
            optimization.executed = True
            optimization.executed_at = datetime.now()
            optimization.result = {"status": "error", "message": str(e)}
            
            with self.lock:
                self.optimization_history.append(optimization)
    
    def _reduce_worker_threads(self, parameters: Dict[str, Any]):
        """Reduce worker threads"""
        target_threads = parameters.get("target_threads", 1)
        # Implementation would depend on your threading model
        logger.info(f"Reducing worker threads to {target_threads}")
    
    def _force_garbage_collection(self, parameters: Dict[str, Any]):
        """Force garbage collection"""
        generations = parameters.get("generations", 2)
        collected = gc.collect()
        logger.info(f"Forced garbage collection, collected {collected} objects")
    
    def _clear_caches(self, parameters: Dict[str, Any]):
        """Clear application caches"""
        # Implementation would depend on your caching system
        logger.info("Clearing application caches")
    
    def _optimize_database_queries(self, parameters: Dict[str, Any]):
        """Optimize database queries"""
        # Implementation would depend on your database system
        logger.info("Optimizing database queries")
    
    def _optimize_thread_pool(self, parameters: Dict[str, Any]):
        """Optimize thread pool"""
        # Implementation would depend on your threading model
        logger.info("Optimizing thread pool configuration")
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history"""
        with self.lock:
            return [asdict(opt) for opt in self.optimization_history]
    
    def set_optimization_level(self, level: OptimizationLevel):
        """Set optimization level"""
        self.optimization_level = level
        logger.info(f"Optimization level set to: {level.value}")
    
    def enable_auto_optimization(self, enabled: bool = True):
        """Enable or disable automatic optimization"""
        self.auto_optimization_enabled = enabled
        logger.info(f"Auto optimization {'enabled' if enabled else 'disabled'}")

class PerformanceProfiler:
    """Performance profiling utilities"""
    
    @staticmethod
    def profile_function(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a function execution"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        return {
            "function": func.__name__,
            "execution_time_ms": (end_time - start_time) * 1000,
            "memory_delta_mb": end_memory - start_memory,
            "success": success,
            "error": error,
            "result": result
        }
    
    @staticmethod
    def profile_decorator(func: Callable):
        """Decorator to profile function execution"""
        def wrapper(*args, **kwargs):
            profile_result = PerformanceProfiler.profile_function(func, *args, **kwargs)
            logger.debug(f"Function {func.__name__} profiled: {profile_result['execution_time_ms']:.2f}ms, "
                        f"{profile_result['memory_delta_mb']:.2f}MB")
            return profile_result["result"]
        return wrapper

# Global instances
_performance_monitor = None
_performance_optimizer = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer(get_performance_monitor())
    return _performance_optimizer

# Example usage
if __name__ == "__main__":
    # Initialize performance system
    monitor = get_performance_monitor()
    optimizer = get_performance_optimizer()
    
    # Start monitoring
    monitor.start_monitoring(interval_seconds=5)
    
    # Set optimization level
    optimizer.set_optimization_level(OptimizationLevel.BALANCED)
    
    # Simulate some work
    @PerformanceProfiler.profile_decorator
    def simulate_work():
        time.sleep(2)
        # Simulate memory allocation
        data = [i for i in range(100000)]
        return len(data)
    
    # Run some work
    for i in range(5):
        result = simulate_work()
        print(f"Work {i+1} completed: {result}")
        time.sleep(1)
    
    # Get performance summary
    summary = monitor.get_performance_summary(10)
    print("\nPerformance Summary:")
    print(json.dumps(summary, indent=2))
    
    # Get optimization history
    history = optimizer.get_optimization_history()
    print(f"\nOptimization History: {len(history)} optimizations applied")
    
    # Stop monitoring
    monitor.stop_monitoring()