"""
Análisis Avanzados para Nómina
Análisis predictivo, detección de anomalías, y insights
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from statistics import mean, median, stdev

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class AnomalyDetection:
    """Resultado de detección de anomalías"""
    employee_id: str
    anomaly_type: str
    severity: str  # low, medium, high
    value: Decimal
    expected_range: Dict[str, Decimal]
    description: str
    detected_at: datetime


class PayrollAnalytics:
    """Análisis avanzados para nómina"""
    
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
    
    def detect_anomalies(
        self,
        period_start: date,
        period_end: date,
        threshold_std: float = 2.0
    ) -> List[AnomalyDetection]:
        """Detecta anomalías en pagos"""
        sql = """
            SELECT 
                employee_id,
                net_pay,
                gross_pay,
                total_hours,
                regular_hours,
                overtime_hours
            FROM payroll_pay_periods
            WHERE period_start >= %s AND period_end <= %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not results:
            return []
        
        # Calcular estadísticas
        net_pays = [Decimal(str(row[1])) for row in results if row[1]]
        gross_pays = [Decimal(str(row[2])) for row in results if row[2]]
        hours = [Decimal(str(row[3])) for row in results if row[3]]
        
        if not net_pays:
            return []
        
        net_mean = Decimal(str(mean([float(n) for n in net_pays])))
        net_std = Decimal(str(stdev([float(n) for n in net_pays]))) if len(net_pays) > 1 else Decimal("0.00")
        
        anomalies = []
        
        for row in results:
            employee_id = row[0]
            net_pay = Decimal(str(row[1])) if row[1] else Decimal("0.00")
            gross_pay = Decimal(str(row[2])) if row[2] else Decimal("0.00")
            total_hours = Decimal(str(row[3])) if row[3] else Decimal("0.00")
            
            # Detectar anomalías en pago neto
            if net_pay > 0:
                z_score = float((net_pay - net_mean) / net_std) if net_std > 0 else 0.0
                
                if abs(z_score) > threshold_std:
                    severity = "high" if abs(z_score) > 3.0 else "medium"
                    
                    anomalies.append(AnomalyDetection(
                        employee_id=employee_id,
                        anomaly_type="unusual_net_pay",
                        severity=severity,
                        value=net_pay,
                        expected_range={
                            "min": net_mean - (net_std * Decimal(str(threshold_std))),
                            "max": net_mean + (net_std * Decimal(str(threshold_std)))
                        },
                        description=f"Net pay ${net_pay} is {abs(z_score):.2f} standard deviations from mean",
                        detected_at=datetime.now()
                    ))
            
            # Detectar horas inusuales
            if total_hours > Decimal("80.0"):
                anomalies.append(AnomalyDetection(
                    employee_id=employee_id,
                    anomaly_type="excessive_hours",
                    severity="high",
                    value=total_hours,
                    expected_range={"min": Decimal("0.00"), "max": Decimal("80.00")},
                    description=f"Total hours {total_hours} exceeds 80 hours",
                    detected_at=datetime.now()
                ))
            
            # Detectar horas negativas o cero con pago positivo
            if total_hours <= Decimal("0.00") and net_pay > Decimal("0.00"):
                anomalies.append(AnomalyDetection(
                    employee_id=employee_id,
                    anomaly_type="payment_without_hours",
                    severity="high",
                    value=net_pay,
                    expected_range={"hours": Decimal("0.00")},
                    description=f"Payment ${net_pay} with {total_hours} hours",
                    detected_at=datetime.now()
                ))
        
        return anomalies
    
    def calculate_trends(
        self,
        employee_id: str,
        periods: int = 6
    ) -> Dict[str, Any]:
        """Calcula tendencias para un empleado"""
        sql = """
            SELECT 
                period_start,
                period_end,
                net_pay,
                gross_pay,
                total_hours,
                overtime_hours
            FROM payroll_pay_periods
            WHERE employee_id = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            ORDER BY period_start DESC
            LIMIT %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, periods)
        )
        
        if len(results) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        periods_data = []
        for row in results:
            periods_data.append({
                "period_start": row[0],
                "period_end": row[1],
                "net_pay": Decimal(str(row[2] or 0)),
                "gross_pay": Decimal(str(row[3] or 0)),
                "total_hours": Decimal(str(row[4] or 0)),
                "overtime_hours": Decimal(str(row[5] or 0))
            })
        
        # Calcular cambios
        latest = periods_data[0]
        previous = periods_data[1]
        
        net_change = latest["net_pay"] - previous["net_pay"]
        net_change_pct = (
            (net_change / previous["net_pay"] * 100)
            if previous["net_pay"] > 0 else Decimal("0.00")
        )
        
        hours_change = latest["total_hours"] - previous["total_hours"]
        hours_change_pct = (
            (hours_change / previous["total_hours"] * 100)
            if previous["total_hours"] > 0 else Decimal("0.00")
        )
        
        # Calcular promedio
        avg_net = sum(p["net_pay"] for p in periods_data) / len(periods_data)
        avg_hours = sum(p["total_hours"] for p in periods_data) / len(periods_data)
        
        # Detectar tendencia
        if len(periods_data) >= 3:
            recent_avg = sum(p["net_pay"] for p in periods_data[:3]) / 3
            older_avg = sum(p["net_pay"] for p in periods_data[3:]) / (len(periods_data) - 3) if len(periods_data) > 3 else recent_avg
            
            if recent_avg > older_avg * Decimal("1.1"):
                trend = "increasing"
            elif recent_avg < older_avg * Decimal("0.9"):
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "employee_id": employee_id,
            "periods_analyzed": len(periods_data),
            "latest_period": {
                "net_pay": float(latest["net_pay"]),
                "hours": float(latest["total_hours"])
            },
            "changes": {
                "net_pay_change": float(net_change),
                "net_pay_change_percentage": float(net_change_pct),
                "hours_change": float(hours_change),
                "hours_change_percentage": float(hours_change_pct)
            },
            "averages": {
                "avg_net_pay": float(avg_net),
                "avg_hours": float(avg_hours)
            },
            "trend": trend
        }
    
    def cost_analysis(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Análisis de costos de nómina"""
        sql = """
            SELECT 
                SUM(gross_pay) as total_gross,
                SUM(total_deductions) as total_deductions,
                SUM(total_expenses) as total_expenses,
                SUM(net_pay) as total_net,
                SUM(total_hours) as total_hours,
                SUM(overtime_hours) as total_overtime,
                COUNT(DISTINCT employee_id) as employee_count
            FROM payroll_pay_periods
            WHERE period_start >= %s AND period_end <= %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
        """
        
        result = self.hook.get_first(
            sql,
            parameters=(period_start, period_end)
        )
        
        if not result:
            return {}
        
        total_gross = Decimal(str(result[0] or 0))
        total_deductions = Decimal(str(result[1] or 0))
        total_expenses = Decimal(str(result[2] or 0))
        total_net = Decimal(str(result[3] or 0))
        total_hours = Decimal(str(result[4] or 0))
        total_overtime = Decimal(str(result[5] or 0))
        employee_count = result[6] or 0
        
        # Calcular costos por hora
        cost_per_hour = total_gross / total_hours if total_hours > 0 else Decimal("0.00")
        cost_per_employee = total_gross / employee_count if employee_count > 0 else Decimal("0.00")
        
        # Calcular costo de overtime
        overtime_percentage = (total_overtime / total_hours * 100) if total_hours > 0 else Decimal("0.00")
        
        # Análisis de eficiencia
        avg_hours_per_employee = total_hours / employee_count if employee_count > 0 else Decimal("0.00")
        
        return {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "total_costs": {
                "gross_pay": float(total_gross),
                "deductions": float(total_deductions),
                "expenses": float(total_expenses),
                "net_pay": float(total_net)
            },
            "efficiency_metrics": {
                "cost_per_hour": float(cost_per_hour),
                "cost_per_employee": float(cost_per_employee),
                "avg_hours_per_employee": float(avg_hours_per_employee),
                "overtime_percentage": float(overtime_percentage)
            },
            "summary": {
                "employee_count": employee_count,
                "total_hours": float(total_hours),
                "total_overtime": float(total_overtime),
                "deduction_rate": float((total_deductions / total_gross * 100) if total_gross > 0 else 0)
            }
        }
    
    def department_comparison(
        self,
        period_start: date,
        period_end: date
    ) -> Dict[str, Any]:
        """Compara costos entre departamentos"""
        sql = """
            SELECT 
                e.department,
                COUNT(DISTINCT pp.employee_id) as employee_count,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.net_pay) as total_net,
                SUM(pp.total_hours) as total_hours,
                AVG(pp.net_pay) as avg_net_pay
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE pp.period_start >= %s AND pp.period_end <= %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
                AND e.department IS NOT NULL
            GROUP BY e.department
            ORDER BY total_gross DESC
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(period_start, period_end)
        )
        
        departments = []
        for row in results:
            departments.append({
                "department": row[0],
                "employee_count": row[1],
                "total_gross_pay": float(Decimal(str(row[2] or 0))),
                "total_net_pay": float(Decimal(str(row[3] or 0))),
                "total_hours": float(Decimal(str(row[4] or 0))),
                "avg_net_pay": float(Decimal(str(row[5] or 0)))
            })
        
        # Calcular totales
        total_gross = sum(d["total_gross_pay"] for d in departments)
        
        # Calcular porcentajes
        for dept in departments:
            dept["percentage_of_total"] = (
                (dept["total_gross_pay"] / total_gross * 100) if total_gross > 0 else 0.0
            )
        
        return {
            "period_start": str(period_start),
            "period_end": str(period_end),
            "departments": departments,
            "summary": {
                "total_departments": len(departments),
                "total_gross_pay": total_gross,
                "largest_department": max(departments, key=lambda x: x["total_gross_pay"]) if departments else None
            }
        }

