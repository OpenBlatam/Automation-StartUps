"""
Sistema de Monitoreo Avanzado para Nómina
Monitoreo en tiempo real y alertas proactivas
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Métrica del sistema"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = None
    unit: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


class PayrollMonitor:
    """Sistema de monitoreo avanzado para nómina"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
        self.metrics: List[Metric] = []
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ) -> None:
        """Registra una métrica"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )
        
        self.metrics.append(metric)
        
        # Mantener solo últimos 1000 métricas
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del sistema"""
        metrics = {}
        
        # Métricas de procesamiento
        sql = """
            SELECT 
                COUNT(*) as total_periods,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_periods,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_periods,
                AVG(net_pay) as avg_net_pay,
                SUM(net_pay) as total_net_pay
            FROM payroll_pay_periods
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        
        result = self.hook.get_first(sql)
        if result:
            metrics["processing"] = {
                "total_periods_24h": result[0] or 0,
                "paid_periods": result[1] or 0,
                "pending_periods": result[2] or 0,
                "avg_net_pay": float(Decimal(str(result[3] or 0))),
                "total_net_pay_24h": float(Decimal(str(result[4] or 0)))
            }
        
        # Métricas de OCR
        ocr_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN ocr_status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN ocr_status = 'failed' THEN 1 END) as failed,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time
            FROM payroll_expense_receipts
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        
        ocr_result = self.hook.get_first(ocr_sql)
        if ocr_result:
            metrics["ocr"] = {
                "total_24h": ocr_result[0] or 0,
                "completed": ocr_result[1] or 0,
                "failed": ocr_result[2] or 0,
                "success_rate": (
                    (ocr_result[1] / ocr_result[0] * 100)
                    if ocr_result[0] > 0 else 0.0
                ),
                "avg_processing_time_seconds": ocr_result[3] or 0.0
            }
        
        # Métricas de aprobaciones
        approval_sql = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                AVG(EXTRACT(EPOCH FROM (COALESCE(approved_at, NOW()) - requested_at))) as avg_approval_time
            FROM payroll_approvals
            WHERE requested_at >= NOW() - INTERVAL '24 hours'
        """
        
        approval_result = self.hook.get_first(approval_sql)
        if approval_result:
            metrics["approvals"] = {
                "total_24h": approval_result[0] or 0,
                "pending": approval_result[1] or 0,
                "approved": approval_result[2] or 0,
                "approval_rate": (
                    (approval_result[2] / approval_result[0] * 100)
                    if approval_result[0] > 0 else 0.0
                ),
                "avg_approval_time_seconds": approval_result[3] or 0.0
            }
        
        return metrics
    
    def check_system_health(self) -> Dict[str, Any]:
        """Verifica salud del sistema"""
        health = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar base de datos
        try:
            self.hook.get_first("SELECT 1")
            health["checks"]["database"] = {"status": "healthy", "message": "Database accessible"}
        except Exception as e:
            health["checks"]["database"] = {"status": "unhealthy", "message": str(e)}
            health["status"] = "unhealthy"
        
        # Verificar procesamiento reciente
        try:
            sql = """
                SELECT COUNT(*)
                FROM payroll_pay_periods
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            """
            recent_count = self.hook.get_first(sql)[0] or 0
            
            if recent_count > 0:
                health["checks"]["processing"] = {"status": "healthy", "message": f"{recent_count} periods processed in last hour"}
            else:
                health["checks"]["processing"] = {"status": "warning", "message": "No processing in last hour"}
        
        except Exception as e:
            health["checks"]["processing"] = {"status": "error", "message": str(e)}
        
        # Verificar errores recientes
        try:
            error_sql = """
                SELECT COUNT(*)
                FROM payroll_pay_periods
                WHERE status = 'failed'
                    AND created_at >= NOW() - INTERVAL '1 hour'
            """
            error_count = self.hook.get_first(error_sql)[0] or 0
            
            if error_count > 10:
                health["checks"]["errors"] = {"status": "warning", "message": f"{error_count} errors in last hour"}
            else:
                health["checks"]["errors"] = {"status": "healthy", "message": f"{error_count} errors in last hour"}
        
        except Exception as e:
            health["checks"]["errors"] = {"status": "error", "message": str(e)}
        
        return health
    
    def get_performance_metrics(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Obtiene métricas de performance"""
        sql = """
            SELECT 
                COUNT(*) as total_operations,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration,
                MIN(EXTRACT(EPOCH FROM (updated_at - created_at))) as min_duration,
                MAX(EXTRACT(EPOCH FROM (updated_at - created_at))) as max_duration
            FROM payroll_pay_periods
            WHERE created_at >= NOW() - INTERVAL '%s hours'
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(sql, parameters=(hours,))
        
        if not result:
            return {}
        
        return {
            "period": f"{hours}h",
            "total_operations": result[0] or 0,
            "avg_duration_seconds": result[1] or 0.0,
            "min_duration_seconds": result[2] or 0.0,
            "max_duration_seconds": result[3] or 0.0,
            "throughput_per_hour": (result[0] / hours) if hours > 0 else 0.0
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de todas las métricas"""
        system_metrics = self.get_system_metrics()
        health = self.check_system_health()
        performance = self.get_performance_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": health,
            "system_metrics": system_metrics,
            "performance": performance,
            "recorded_metrics": len(self.metrics)
        }

