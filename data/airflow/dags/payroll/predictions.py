"""
Sistema de Predicciones para Nómina
Predicciones básicas usando análisis estadístico
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from statistics import mean, median

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class PayrollPrediction:
    """Predicción de nómina"""
    employee_id: str
    predicted_net_pay: Decimal
    predicted_hours: Decimal
    confidence: float
    based_on_periods: int
    predicted_date: date
    factors: Dict[str, Any]


class PayrollPredictor:
    """Sistema de predicciones para nómina"""
    
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
    
    def predict_next_period(
        self,
        employee_id: str,
        lookback_periods: int = 6
    ) -> PayrollPrediction:
        """Predice el próximo período de pago"""
        sql = """
            SELECT 
                net_pay,
                gross_pay,
                total_hours,
                regular_hours,
                overtime_hours
            FROM payroll_pay_periods
            WHERE employee_id = %s
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            ORDER BY period_start DESC
            LIMIT %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, lookback_periods)
        )
        
        if len(results) < 2:
            # No hay suficiente historial
            return PayrollPrediction(
                employee_id=employee_id,
                predicted_net_pay=Decimal("0.00"),
                predicted_hours=Decimal("0.00"),
                confidence=0.0,
                based_on_periods=len(results),
                predicted_date=date.today(),
                factors={"error": "Insufficient historical data"}
            )
        
        # Calcular promedios
        net_pays = [Decimal(str(row[0] or 0)) for row in results]
        hours = [Decimal(str(row[2] or 0)) for row in results]
        overtime_hours = [Decimal(str(row[4] or 0)) for row in results]
        
        avg_net_pay = Decimal(str(mean([float(n) for n in net_pays])))
        avg_hours = Decimal(str(mean([float(h) for h in hours])))
        avg_overtime = Decimal(str(mean([float(o) for o in overtime_hours])))
        
        # Calcular tendencia
        recent_avg = mean([float(n) for n in net_pays[:3]])
        older_avg = mean([float(n) for n in net_pays[3:]]) if len(net_pays) > 3 else recent_avg
        
        trend_factor = 1.0
        if recent_avg > older_avg * 1.1:
            trend_factor = 1.05  # Tendencia creciente
        elif recent_avg < older_avg * 0.9:
            trend_factor = 0.95  # Tendencia decreciente
        
        # Predicción
        predicted_net_pay = avg_net_pay * Decimal(str(trend_factor))
        predicted_hours = avg_hours
        
        # Calcular confianza (más períodos = mayor confianza)
        confidence = min(0.95, 0.5 + (len(results) * 0.1))
        
        # Si hay mucha variabilidad, reducir confianza
        if len(net_pays) > 1:
            import statistics
            std_dev = statistics.stdev([float(n) for n in net_pays])
            avg_value = float(avg_net_pay)
            if std_dev > 0:
                coefficient_of_variation = std_dev / avg_value if avg_value > 0 else 0
                if coefficient_of_variation > 0.2:  # Alta variabilidad
                    confidence *= 0.8
        
        return PayrollPrediction(
            employee_id=employee_id,
            predicted_net_pay=predicted_net_pay.quantize(Decimal("0.01")),
            predicted_hours=predicted_hours.quantize(Decimal("0.01")),
            confidence=confidence,
            based_on_periods=len(results),
            predicted_date=date.today(),
            factors={
                "average_net_pay": float(avg_net_pay),
                "average_hours": float(avg_hours),
                "average_overtime": float(avg_overtime),
                "trend_factor": trend_factor,
                "variability": float(std_dev) if len(net_pays) > 1 else 0.0
            }
        )
    
    def predict_department_costs(
        self,
        department: str,
        periods_ahead: int = 4
    ) -> Dict[str, Any]:
        """Predice costos futuros por departamento"""
        sql = """
            SELECT 
                pp.period_start,
                pp.period_end,
                SUM(pp.gross_pay) as total_gross,
                SUM(pp.net_pay) as total_net
            FROM payroll_pay_periods pp
            JOIN payroll_employees e ON pp.employee_id = e.employee_id
            WHERE e.department = %s
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
            GROUP BY pp.period_start, pp.period_end
            ORDER BY pp.period_start DESC
            LIMIT 6
        """
        
        results = self.hook.get_records(sql, parameters=(department,))
        
        if len(results) < 2:
            return {
                "department": department,
                "predictions": [],
                "error": "Insufficient historical data"
            }
        
        # Calcular promedio y tendencia
        gross_pays = [float(Decimal(str(row[2] or 0))) for row in results]
        net_pays = [float(Decimal(str(row[3] or 0))) for row in results]
        
        avg_gross = mean(gross_pays)
        avg_net = mean(net_pays)
        
        # Calcular tendencia
        recent_avg = mean(gross_pays[:3])
        trend_factor = recent_avg / mean(gross_pays[3:]) if len(gross_pays) > 3 else 1.0
        
        # Generar predicciones
        predictions = []
        base_date = date.today()
        
        for i in range(periods_ahead):
            period_start = base_date + timedelta(days=i * 14)
            period_end = period_start + timedelta(days=13)
            
            # Aplicar tendencia
            predicted_gross = avg_gross * (trend_factor ** i)
            predicted_net = avg_net * (trend_factor ** i)
            
            predictions.append({
                "period_start": str(period_start),
                "period_end": str(period_end),
                "predicted_gross_pay": predicted_gross,
                "predicted_net_pay": predicted_net,
                "confidence": max(0.5, 0.9 - (i * 0.1))  # Disminuye con más períodos
            })
        
        return {
            "department": department,
            "predictions": predictions,
            "based_on_periods": len(results),
            "trend_factor": trend_factor,
            "average_gross_pay": avg_gross,
            "average_net_pay": avg_net
        }
    
    def detect_seasonal_patterns(
        self,
        employee_id: str,
        years: int = 2
    ) -> Dict[str, Any]:
        """Detecta patrones estacionales en pagos"""
        sql = """
            SELECT 
                EXTRACT(MONTH FROM period_start) as month,
                EXTRACT(QUARTER FROM period_start) as quarter,
                AVG(net_pay) as avg_net_pay,
                AVG(total_hours) as avg_hours
            FROM payroll_pay_periods
            WHERE employee_id = %s
                AND period_start >= CURRENT_DATE - INTERVAL '%s years'
                AND status IN ('calculated', 'reviewed', 'approved', 'paid')
            GROUP BY EXTRACT(MONTH FROM period_start), EXTRACT(QUARTER FROM period_start)
            ORDER BY month
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(employee_id, years)
        )
        
        if len(results) < 6:
            return {
                "employee_id": employee_id,
                "patterns": [],
                "error": "Insufficient data for seasonal analysis"
            }
        
        monthly_patterns = {}
        for row in results:
            month = int(row[0])
            monthly_patterns[month] = {
                "avg_net_pay": float(Decimal(str(row[2] or 0))),
                "avg_hours": float(Decimal(str(row[3] or 0)))
            }
        
        # Identificar meses con mayor/menor actividad
        if monthly_patterns:
            max_month = max(monthly_patterns.items(), key=lambda x: x[1]["avg_net_pay"])
            min_month = min(monthly_patterns.items(), key=lambda x: x[1]["avg_net_pay"])
        else:
            max_month = None
            min_month = None
        
        return {
            "employee_id": employee_id,
            "monthly_patterns": monthly_patterns,
            "peak_month": max_month[0] if max_month else None,
            "low_month": min_month[0] if min_month else None,
            "years_analyzed": years
        }

