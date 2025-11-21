"""
Sistema de Alertas para Nómina
Alertas inteligentes basadas en reglas y umbrales
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Severidad de alertas"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Tipos de alertas"""
    HIGH_PAYMENT = "high_payment"
    EXCESSIVE_HOURS = "excessive_hours"
    MISSING_TIME_ENTRIES = "missing_time_entries"
    PENDING_APPROVALS = "pending_approvals"
    OCR_FAILURES = "ocr_failures"
    UNUSUAL_DEDUCTIONS = "unusual_deductions"
    ANOMALY_DETECTED = "anomaly_detected"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass
class Alert:
    """Alerta del sistema"""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    employee_id: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class PayrollAlertSystem:
    """Sistema de alertas para nómina"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def check_high_payments(
        self,
        period_start: date,
        period_end: date,
        threshold: Decimal = Decimal("10000.00")
    ) -> List[Alert]:
        """Verifica pagos altos"""
        sql = """
            SELECT 
                employee_id,
                net_pay,
                period_start,
                period_end
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND net_pay > %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end, float(threshold))
        )
        
        alerts = []
        for row in results:
            alerts.append(Alert(
                alert_type=AlertType.HIGH_PAYMENT,
                severity=AlertSeverity.WARNING,
                message=f"High payment detected: ${row[1]:,.2f}",
                employee_id=row[0],
                period_start=row[2],
                period_end=row[3],
                value=Decimal(str(row[1])),
                threshold=threshold
            ))
        
        return alerts
    
    def check_excessive_hours(
        self,
        period_start: date,
        period_end: date,
        max_hours: Decimal = Decimal("80.0")
    ) -> List[Alert]:
        """Verifica horas excesivas"""
        sql = """
            SELECT 
                employee_id,
                total_hours,
                period_start,
                period_end
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND total_hours > %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end, float(max_hours))
        )
        
        alerts = []
        for row in results:
            alerts.append(Alert(
                alert_type=AlertType.EXCESSIVE_HOURS,
                severity=AlertSeverity.WARNING,
                message=f"Excessive hours: {row[1]} hours",
                employee_id=row[0],
                period_start=row[2],
                period_end=row[3],
                value=Decimal(str(row[1])),
                threshold=max_hours
            ))
        
        return alerts
    
    def check_missing_time_entries(
        self,
        period_start: date,
        period_end: date
    ) -> List[Alert]:
        """Verifica empleados sin entradas de tiempo"""
        sql = """
            SELECT DISTINCT e.employee_id, e.name
            FROM payroll_employees e
            WHERE e.active = true
                AND e.employee_type = 'hourly'
                AND NOT EXISTS (
                    SELECT 1
                    FROM payroll_time_entries te
                    WHERE te.employee_id = e.employee_id
                        AND te.work_date >= %s
                        AND te.work_date <= %s
                )
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        alerts = []
        for row in results:
            alerts.append(Alert(
                alert_type=AlertType.MISSING_TIME_ENTRIES,
                severity=AlertSeverity.WARNING,
                message=f"Missing time entries for {row[1]}",
                employee_id=row[0],
                period_start=period_start,
                period_end=period_end
            ))
        
        return alerts
    
    def check_pending_approvals(
        self,
        max_age_days: int = 7
    ) -> List[Alert]:
        """Verifica aprobaciones pendientes antiguas"""
        sql = """
            SELECT 
                id,
                employee_id,
                entity_type,
                entity_id,
                requested_at
            FROM payroll_approvals
            WHERE status = 'pending'
                AND requested_at < NOW() - INTERVAL '%s days'
            ORDER BY requested_at ASC
        """
        
        results = self.hook.get_records(sql, parameters=(max_age_days,))
        
        alerts = []
        for row in results:
            age_days = (datetime.now() - row[4]).days if row[4] else 0
            
            alerts.append(Alert(
                alert_type=AlertType.PENDING_APPROVALS,
                severity=AlertSeverity.CRITICAL if age_days > 14 else AlertSeverity.WARNING,
                message=f"Pending approval {age_days} days old",
                employee_id=row[1],
                metadata={
                    "approval_id": row[0],
                    "entity_type": row[2],
                    "entity_id": row[3],
                    "age_days": age_days
                }
            ))
        
        return alerts
    
    def check_ocr_failures(
        self,
        days: int = 7,
        failure_threshold: int = 10
    ) -> List[Alert]:
        """Verifica fallos de OCR"""
        sql = """
            SELECT COUNT(*)
            FROM payroll_expense_receipts
            WHERE ocr_status = 'failed'
                AND created_at >= NOW() - INTERVAL '%s days'
        """
        
        result = self.hook.get_first(sql, parameters=(days,))
        failure_count = result[0] if result else 0
        
        if failure_count >= failure_threshold:
            return [Alert(
                alert_type=AlertType.OCR_FAILURES,
                severity=AlertSeverity.WARNING,
                message=f"High OCR failure rate: {failure_count} failures in last {days} days",
                metadata={
                    "failure_count": failure_count,
                    "days": days,
                    "threshold": failure_threshold
                }
            )]
        
        return []
    
    def check_budget_exceeded(
        self,
        period_start: date,
        period_end: date,
        budget: Decimal
    ) -> List[Alert]:
        """Verifica si se excedió el presupuesto"""
        sql = """
            SELECT SUM(net_pay)
            FROM payroll_pay_periods
            WHERE period_start = %s AND period_end = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(sql, parameters=(period_start, period_end))
        total = Decimal(str(result[0] or 0)) if result else Decimal("0.00")
        
        if total > budget:
            return [Alert(
                alert_type=AlertType.BUDGET_EXCEEDED,
                severity=AlertSeverity.CRITICAL,
                message=f"Budget exceeded: ${total:,.2f} > ${budget:,.2f}",
                period_start=period_start,
                period_end=period_end,
                value=total,
                threshold=budget,
                metadata={
                    "total_spent": float(total),
                    "budget": float(budget),
                    "over_budget": float(total - budget),
                    "percentage": float((total / budget * 100) if budget > 0 else 0)
                }
            )]
        
        return []
    
    def run_all_checks(
        self,
        period_start: date,
        period_end: date,
        budget: Optional[Decimal] = None
    ) -> List[Alert]:
        """Ejecuta todas las verificaciones"""
        all_alerts = []
        
        # Verificar pagos altos
        all_alerts.extend(self.check_high_payments(period_start, period_end))
        
        # Verificar horas excesivas
        all_alerts.extend(self.check_excessive_hours(period_start, period_end))
        
        # Verificar entradas faltantes
        all_alerts.extend(self.check_missing_time_entries(period_start, period_end))
        
        # Verificar aprobaciones pendientes
        all_alerts.extend(self.check_pending_approvals())
        
        # Verificar OCR fallidos
        all_alerts.extend(self.check_ocr_failures())
        
        # Verificar presupuesto
        if budget:
            all_alerts.extend(self.check_budget_exceeded(period_start, period_end, budget))
        
        return all_alerts
    
    def get_alerts_summary(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Obtiene resumen de alertas"""
        by_severity = {
            "critical": [a for a in alerts if a.severity == AlertSeverity.CRITICAL],
            "warning": [a for a in alerts if a.severity == AlertSeverity.WARNING],
            "info": [a for a in alerts if a.severity == AlertSeverity.INFO]
        }
        
        by_type = {}
        for alert in alerts:
            alert_type = alert.alert_type.value
            if alert_type not in by_type:
                by_type[alert_type] = 0
            by_type[alert_type] += 1
        
        return {
            "total": len(alerts),
            "by_severity": {
                "critical": len(by_severity["critical"]),
                "warning": len(by_severity["warning"]),
                "info": len(by_severity["info"])
            },
            "by_type": by_type,
            "alerts": [
                {
                    "type": a.alert_type.value,
                    "severity": a.severity.value,
                    "message": a.message,
                    "employee_id": a.employee_id,
                    "value": float(a.value) if a.value else None,
                    "threshold": float(a.threshold) if a.threshold else None
                }
                for a in alerts
            ]
        }

