"""
Sistema de Observabilidad para Nómina
Métricas, tracing y logging estructurado
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)


class PayrollObservability:
    """Sistema de observabilidad para nómina"""
    
    def __init__(self):
        """Inicializa sistema de observabilidad"""
        self.metrics: Dict[str, Any] = {}
        self.traces: list = []
    
    @contextmanager
    def trace(self, operation_name: str, **context):
        """Context manager para tracing"""
        trace_id = f"{operation_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        trace_data = {
            "trace_id": trace_id,
            "operation": operation_name,
            "start_time": datetime.now().isoformat(),
            "context": context,
            "success": False,
            "duration_ms": 0,
            "error": None
        }
        
        try:
            yield trace_data
            trace_data["success"] = True
        except Exception as e:
            trace_data["error"] = str(e)
            raise
        finally:
            trace_data["duration_ms"] = int((time.time() - start_time) * 1000)
            trace_data["end_time"] = datetime.now().isoformat()
            self.traces.append(trace_data)
            
            if trace_data["duration_ms"] > 5000:  # Log slow operations
                logger.warning(
                    f"Slow operation detected: {operation_name} "
                    f"took {trace_data['duration_ms']}ms"
                )
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Registra una métrica"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        metric_data = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        }
        
        self.metrics[metric_name].append(metric_data)
        
        # Mantener solo últimos 1000 valores
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def increment_counter(
        self,
        counter_name: str,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Incrementa un contador"""
        if counter_name not in self.metrics:
            self.metrics[counter_name] = []
        
        self.metrics[counter_name].append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de métricas"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                numeric_values = [v["value"] for v in values if isinstance(v["value"], (int, float))]
                
                if numeric_values:
                    summary[metric_name] = {
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "latest": values[-1]["value"]
                    }
        
        return summary
    
    def get_recent_traces(self, limit: int = 100) -> list:
        """Obtiene trazas recientes"""
        return self.traces[-limit:] if len(self.traces) > limit else self.traces
    
    def log_structured(
        self,
        level: str,
        message: str,
        **context
    ) -> None:
        """Logging estructurado"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **context
        }
        
        log_message = json.dumps(log_data)
        
        if level == "ERROR":
            logger.error(log_message)
        elif level == "WARNING":
            logger.warning(log_message)
        elif level == "INFO":
            logger.info(log_message)
        else:
            logger.debug(log_message)


def observe_operation(operation_name: str):
    """Decorator para observar operaciones"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            observability = PayrollObservability()
            
            with observability.trace(operation_name, function=func.__name__):
                try:
                    result = func(*args, **kwargs)
                    observability.increment_counter(f"{operation_name}.success")
                    return result
                except Exception as e:
                    observability.increment_counter(f"{operation_name}.error")
                    observability.log_structured(
                        "ERROR",
                        f"Operation {operation_name} failed",
                        error=str(e),
                        function=func.__name__
                    )
                    raise
        
        return wrapper
    return decorator


# Instancia global
observability = PayrollObservability()

