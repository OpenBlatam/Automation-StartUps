"""
Sistema de Métricas para Automatización de Precios

Recopila y expone métricas de rendimiento y operación
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False


@dataclass
class OperationMetrics:
    """Métricas de una operación"""
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = False
    items_processed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PriceMetrics:
    """Sistema de métricas para automatización de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics: List[OperationMetrics] = []
        self.enabled = config.get('metrics_enabled', True)
    
    def start_operation(self, operation: str, metadata: Optional[Dict] = None) -> str:
        """
        Inicia medición de una operación
        
        Args:
            operation: Nombre de la operación
            metadata: Metadatos adicionales
        
        Returns:
            ID de la operación
        """
        if not self.enabled:
            return ""
        
        metric = OperationMetrics(
            operation=operation,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        operation_id = str(len(self.metrics) - 1)
        
        logger.debug(f"Métrica iniciada: {operation} (ID: {operation_id})")
        return operation_id
    
    def end_operation(
        self,
        operation_id: str,
        success: bool = True,
        items_processed: int = 0,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Finaliza medición de una operación
        
        Args:
            operation_id: ID de la operación
            success: Si la operación fue exitosa
            items_processed: Número de items procesados
            errors: Lista de errores (si los hay)
            metadata: Metadatos adicionales
        """
        if not self.enabled or not operation_id:
            return
        
        try:
            idx = int(operation_id)
            if 0 <= idx < len(self.metrics):
                metric = self.metrics[idx]
                metric.end_time = datetime.now()
                metric.duration_seconds = (
                    metric.end_time - metric.start_time
                ).total_seconds()
                metric.success = success
                metric.items_processed = items_processed
                metric.errors = errors or []
                
                if metadata:
                    metric.metadata.update(metadata)
                
                # Registrar en Airflow Stats si está disponible
                if STATS_AVAILABLE:
                    try:
                        Stats.timing(
                            f"price_automation.{metric.operation}.duration",
                            metric.duration_seconds
                        )
                        Stats.incr(
                            f"price_automation.{metric.operation}.{'success' if success else 'failure'}"
                        )
                        if items_processed > 0:
                            Stats.incr(
                                f"price_automation.{metric.operation}.items",
                                items_processed
                            )
                    except Exception as e:
                        logger.warning(f"Error registrando stats: {e}")
                
                logger.debug(
                    f"Métrica finalizada: {metric.operation} - "
                    f"{metric.duration_seconds:.2f}s, "
                    f"success={success}, items={items_processed}"
                )
        except (ValueError, IndexError) as e:
            logger.warning(f"Error finalizando métrica {operation_id}: {e}")
    
    def get_operation_summary(self, operation: Optional[str] = None) -> Dict:
        """
        Obtiene resumen de operaciones
        
        Args:
            operation: Nombre de operación específica (None = todas)
        
        Returns:
            Diccionario con resumen
        """
        if not self.metrics:
            return {"total": 0}
        
        filtered_metrics = [
            m for m in self.metrics
            if operation is None or m.operation == operation
        ]
        
        if not filtered_metrics:
            return {"total": 0, "operation": operation}
        
        completed = [m for m in filtered_metrics if m.end_time is not None]
        successful = [m for m in completed if m.success]
        
        total_duration = sum(m.duration_seconds or 0 for m in completed)
        avg_duration = total_duration / len(completed) if completed else 0
        
        total_items = sum(m.items_processed for m in completed)
        
        return {
            "operation": operation or "all",
            "total": len(filtered_metrics),
            "completed": len(completed),
            "in_progress": len(filtered_metrics) - len(completed),
            "successful": len(successful),
            "failed": len(completed) - len(successful),
            "success_rate": len(successful) / len(completed) * 100 if completed else 0,
            "avg_duration_seconds": round(avg_duration, 2),
            "total_duration_seconds": round(total_duration, 2),
            "total_items_processed": total_items,
            "avg_items_per_operation": round(total_items / len(completed), 2) if completed else 0,
        }
    
    def get_performance_report(self) -> Dict:
        """Genera reporte de rendimiento completo"""
        if not self.metrics:
            return {"message": "No hay métricas disponibles"}
        
        # Resumen por operación
        operations = set(m.operation for m in self.metrics)
        operation_summaries = {
            op: self.get_operation_summary(op)
            for op in operations
        }
        
        # Métricas generales
        all_completed = [m for m in self.metrics if m.end_time is not None]
        total_errors = sum(len(m.errors) for m in all_completed)
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "total_operations": len(self.metrics),
            "completed_operations": len(all_completed),
            "total_errors": total_errors,
            "operation_summaries": operation_summaries,
            "overall_success_rate": (
                len([m for m in all_completed if m.success]) / len(all_completed) * 100
                if all_completed else 0
            ),
        }
    
    def clear_old_metrics(self, days: int = 7):
        """Elimina métricas más antiguas que X días"""
        cutoff = datetime.now() - timedelta(days=days)
        self.metrics = [
            m for m in self.metrics
            if m.start_time >= cutoff
        ]
        logger.info(f"Métricas antiguas eliminadas (manteniendo últimos {days} días)")








