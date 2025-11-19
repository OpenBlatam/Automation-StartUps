"""
Sistema de Compliance para Nómina
Verificaciones de cumplimiento legal y regulatorio
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class ComplianceRule(str, Enum):
    """Reglas de compliance"""
    MINIMUM_WAGE = "minimum_wage"
    OVERTIME_RATE = "overtime_rate"
    MAX_HOURS_PER_WEEK = "max_hours_per_week"
    MAX_HOURS_PER_DAY = "max_hours_per_day"
    PAYMENT_FREQUENCY = "payment_frequency"
    TAX_WITHHOLDING = "tax_withholding"
    BENEFITS_REQUIREMENTS = "benefits_requirements"


class ComplianceSeverity(str, Enum):
    """Severidad de violaciones de compliance"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    LEGAL = "legal"  # Violación legal que requiere acción inmediata


@dataclass
class ComplianceViolation:
    """Violación de compliance"""
    rule: ComplianceRule
    severity: ComplianceSeverity
    message: str
    employee_id: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    actual_value: Optional[Decimal] = None
    required_value: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None
    detected_at: datetime = None
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()


class PayrollCompliance:
    """Sistema de compliance para nómina"""
    
    def __init__(
        self,
        postgres_conn_id: str = "postgres_default",
        minimum_wage: Decimal = Decimal("7.25"),  # Federal minimum wage
        max_hours_per_week: Decimal = Decimal("60.0"),
        max_hours_per_day: Decimal = Decimal("16.0"),
        overtime_multiplier: Decimal = Decimal("1.5")
    ):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
            minimum_wage: Salario mínimo por hora
            max_hours_per_week: Máximo de horas por semana
            max_hours_per_day: Máximo de horas por día
            overtime_multiplier: Multiplicador de overtime requerido
        """
        self.postgres_conn_id = postgres_conn_id
        self.minimum_wage = minimum_wage
        self.max_hours_per_week = max_hours_per_week
        self.max_hours_per_day = max_hours_per_day
        self.overtime_multiplier = overtime_multiplier
        self._hook: Optional[PostgresHook] = None
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def check_minimum_wage(
        self,
        employee_id: str,
        hourly_rate: Decimal
    ) -> List[ComplianceViolation]:
        """Verifica cumplimiento de salario mínimo"""
        violations = []
        
        if hourly_rate < self.minimum_wage:
            violations.append(ComplianceViolation(
                rule=ComplianceRule.MINIMUM_WAGE,
                severity=ComplianceSeverity.LEGAL,
                message=f"Hourly rate ${hourly_rate} below minimum wage ${self.minimum_wage}",
                employee_id=employee_id,
                actual_value=hourly_rate,
                required_value=self.minimum_wage
            ))
        
        return violations
    
    def check_overtime_rate(
        self,
        employee_id: str,
        overtime_rate: Decimal,
        base_rate: Decimal
    ) -> List[ComplianceViolation]:
        """Verifica que el rate de overtime sea correcto"""
        violations = []
        required_overtime = base_rate * self.overtime_multiplier
        
        if overtime_rate < required_overtime:
            violations.append(ComplianceViolation(
                rule=ComplianceRule.OVERTIME_RATE,
                severity=ComplianceSeverity.LEGAL,
                message=f"Overtime rate ${overtime_rate} below required ${required_overtime}",
                employee_id=employee_id,
                actual_value=overtime_rate,
                required_value=required_overtime
            ))
        
        return violations
    
    def check_max_hours(
        self,
        employee_id: str,
        period_start: date,
        period_end: date
    ) -> List[ComplianceViolation]:
        """Verifica límites de horas"""
        violations = []
        
        # Verificar horas por semana
        sql = """
            SELECT 
                DATE_TRUNC('week', work_date) as week,
                SUM(EXTRACT(EPOCH FROM (clock_out - clock_in)) / 3600) as total_hours
            FROM payroll_time_entries
            WHERE employee_id = %s
                AND work_date >= %s
                AND work_date <= %s
            GROUP BY DATE_TRUNC('week', work_date)
            HAVING SUM(EXTRACT(EPOCH FROM (clock_out - clock_in)) / 3600) > %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, period_start, period_end, float(self.max_hours_per_week))
        )
        
        for row in results:
            violations.append(ComplianceViolation(
                rule=ComplianceRule.MAX_HOURS_PER_WEEK,
                severity=ComplianceSeverity.WARNING,
                message=f"Weekly hours {row[1]:.1f} exceed maximum {self.max_hours_per_week}",
                employee_id=employee_id,
                period_start=period_start,
                period_end=period_end,
                actual_value=Decimal(str(row[1])),
                required_value=self.max_hours_per_week
            ))
        
        # Verificar horas por día
        sql = """
            SELECT 
                work_date,
                SUM(EXTRACT(EPOCH FROM (clock_out - clock_in)) / 3600) as total_hours
            FROM payroll_time_entries
            WHERE employee_id = %s
                AND work_date >= %s
                AND work_date <= %s
            GROUP BY work_date
            HAVING SUM(EXTRACT(EPOCH FROM (clock_out - clock_in)) / 3600) > %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, period_start, period_end, float(self.max_hours_per_day))
        )
        
        for row in results:
            violations.append(ComplianceViolation(
                rule=ComplianceRule.MAX_HOURS_PER_DAY,
                severity=ComplianceSeverity.WARNING,
                message=f"Daily hours {row[1]:.1f} exceed maximum {self.max_hours_per_day}",
                employee_id=employee_id,
                period_start=period_start,
                period_end=period_end,
                actual_value=Decimal(str(row[1])),
                required_value=self.max_hours_per_day
            ))
        
        return violations
    
    def check_payment_period(
        self,
        employee_id: str,
        period_start: date,
        period_end: date,
        pay_date: date,
        max_days_after_period: int = 7
    ) -> List[ComplianceViolation]:
        """Verifica que el pago se haga dentro del tiempo requerido"""
        violations = []
        
        days_after = (pay_date - period_end).days
        
        if days_after > max_days_after_period:
            violations.append(ComplianceViolation(
                rule=ComplianceRule.PAYMENT_FREQUENCY,
                severity=ComplianceSeverity.WARNING,
                message=f"Payment {days_after} days after period end (max {max_days_after_period})",
                employee_id=employee_id,
                period_start=period_start,
                period_end=period_end,
                metadata={"days_after": days_after, "pay_date": str(pay_date)}
            ))
        
        return violations
    
    def check_tax_withholding(
        self,
        employee_id: str,
        gross_pay: Decimal,
        tax_withheld: Decimal,
        min_withholding_rate: Decimal = Decimal("0.10")
    ) -> List[ComplianceViolation]:
        """Verifica que el withholding de impuestos sea adecuado"""
        violations = []
        
        if gross_pay > 0:
            withholding_rate = tax_withheld / gross_pay
            
            if withholding_rate < min_withholding_rate:
                violations.append(ComplianceViolation(
                    rule=ComplianceRule.TAX_WITHHOLDING,
                    severity=ComplianceSeverity.WARNING,
                    message=f"Tax withholding rate {withholding_rate:.2%} below minimum {min_withholding_rate:.2%}",
                    employee_id=employee_id,
                    actual_value=withholding_rate,
                    required_value=min_withholding_rate
                ))
        
        return violations
    
    def run_all_checks(
        self,
        employee_id: str,
        period_start: date,
        period_end: date,
        hourly_rate: Decimal,
        pay_date: date,
        gross_pay: Decimal,
        tax_withheld: Decimal
    ) -> List[ComplianceViolation]:
        """Ejecuta todas las verificaciones de compliance"""
        all_violations = []
        
        # Salario mínimo
        all_violations.extend(self.check_minimum_wage(employee_id, hourly_rate))
        
        # Horas máximas
        all_violations.extend(self.check_max_hours(employee_id, period_start, period_end))
        
        # Frecuencia de pago
        all_violations.extend(self.check_payment_period(employee_id, period_start, period_end, pay_date))
        
        # Withholding de impuestos
        all_violations.extend(self.check_tax_withholding(employee_id, gross_pay, tax_withheld))
        
        return all_violations
    
    def get_compliance_report(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Genera reporte de compliance para un período"""
        sql = """
            SELECT DISTINCT pp.employee_id, e.hourly_rate
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start = %s AND pp.period_end = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        results = self.hook.get_records(sql, parameters=(period_start, period_end))
        
        all_violations = []
        
        for row in results:
            employee_id = row[0]
            hourly_rate = Decimal(str(row[1] or 0))
            
            # Obtener datos del período
            period_sql = """
                SELECT gross_pay, total_deductions, pay_date
                FROM payroll_pay_periods
                WHERE employee_id = %s
                    AND period_start = %s
                    AND period_end = %s
                LIMIT 1
            """
            
            period_result = self.hook.get_first(
                period_sql,
                parameters=(employee_id, period_start, period_end)
            )
            
            if period_result:
                gross_pay = Decimal(str(period_result[0] or 0))
                total_deductions = Decimal(str(period_result[1] or 0))
                pay_date = period_result[2]
                
                violations = self.run_all_checks(
                    employee_id=employee_id,
                    period_start=period_start,
                    period_end=period_end,
                    hourly_rate=hourly_rate,
                    pay_date=pay_date,
                    gross_pay=gross_pay,
                    tax_withheld=total_deductions
                )
                
                all_violations.extend(violations)
        
        # Agrupar por severidad
        by_severity = {
            "legal": [v for v in all_violations if v.severity == ComplianceSeverity.LEGAL],
            "critical": [v for v in all_violations if v.severity == ComplianceSeverity.CRITICAL],
            "warning": [v for v in all_violations if v.severity == ComplianceSeverity.WARNING],
            "info": [v for v in all_violations if v.severity == ComplianceSeverity.INFO]
        }
        
        return {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "total_violations": len(all_violations),
            "by_severity": {
                "legal": len(by_severity["legal"]),
                "critical": len(by_severity["critical"]),
                "warning": len(by_severity["warning"]),
                "info": len(by_severity["info"])
            },
            "violations": [
                {
                    "rule": v.rule.value,
                    "severity": v.severity.value,
                    "message": v.message,
                    "employee_id": v.employee_id,
                    "actual_value": float(v.actual_value) if v.actual_value else None,
                    "required_value": float(v.required_value) if v.required_value else None
                }
                for v in all_violations
            ]
        }

