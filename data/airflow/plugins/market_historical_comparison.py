"""
Comparación Histórica de Tendencias de Mercado

Compara análisis actuales con históricos para identificar:
- Cambios en tendencias
- Evolución de oportunidades
- Patrones temporales
- Análisis de tendencias a largo plazo
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TrendComparison:
    """Comparación de tendencia entre períodos."""
    trend_name: str
    current_value: float
    previous_value: float
    change_absolute: float
    change_percentage: float
    trend_acceleration: float  # Cambio en la velocidad de cambio
    period_comparison: str  # "week", "month", "quarter"


class MarketHistoricalComparator:
    """Comparador histórico de análisis de mercado."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el comparador histórico.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.logger = logging.getLogger(__name__)
    
    def compare_with_historical(
        self,
        current_analysis: Dict[str, Any],
        comparison_periods: List[str] = ["1 week", "1 month", "3 months"]
    ) -> Dict[str, Any]:
        """
        Compara análisis actual con históricos.
        
        Args:
            current_analysis: Análisis actual
            comparison_periods: Períodos para comparar
            
        Returns:
            Comparación completa con históricos
        """
        logger.info("Comparing with historical data")
        
        if not self.postgres_conn_id:
            logger.warning("PostgreSQL connection not configured, skipping historical comparison")
            return {"comparison_available": False}
        
        industry = current_analysis.get("industry", "")
        current_trends = current_analysis.get("trends", [])
        
        comparisons = {}
        
        for period in comparison_periods:
            historical_analysis = self._get_historical_analysis(industry, period)
            if historical_analysis:
                comparison = self._compare_analyses(current_analysis, historical_analysis, period)
                comparisons[period] = comparison
        
        return {
            "comparison_available": True,
            "industry": industry,
            "current_analysis_date": current_analysis.get("analysis_date"),
            "comparisons": comparisons,
            "summary": self._generate_comparison_summary(comparisons)
        }
    
    def _get_historical_analysis(
        self,
        industry: str,
        period: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene análisis histórico desde base de datos."""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            import json
            
            pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            # Parsear período
            if "week" in period:
                days = 7
            elif "month" in period:
                days = 30
            elif "quarter" in period:
                days = 90
            else:
                days = 30
            
            # Obtener análisis más cercano al período
            cursor.execute("""
                SELECT analysis_data, analysis_date
                FROM market_trends_analysis
                WHERE industry = %s
                AND analysis_date >= CURRENT_DATE - INTERVAL '%s days'
                AND analysis_date < CURRENT_DATE - INTERVAL '%s days'
                ORDER BY ABS(EXTRACT(EPOCH FROM (analysis_date - (CURRENT_DATE - INTERVAL '%s days'))))
                LIMIT 1
            """, (industry, days + 7, days - 7, days))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    "analysis": row[0],
                    "date": row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical analysis: {e}")
            return None
    
    def _compare_analyses(
        self,
        current: Dict[str, Any],
        historical: Dict[str, Any],
        period: str
    ) -> Dict[str, Any]:
        """Compara dos análisis."""
        current_trends = current.get("trends", [])
        historical_trends = historical["analysis"].get("trends", [])
        
        # Crear mapas por nombre de tendencia
        current_map = {t.get("trend_name"): t for t in current_trends}
        historical_map = {t.get("trend_name"): t for t in historical_trends}
        
        comparisons = []
        trends_improved = 0
        trends_declined = 0
        trends_stable = 0
        
        # Comparar tendencias comunes
        common_trends = set(current_map.keys()) & set(historical_map.keys())
        
        for trend_name in common_trends:
            current_trend = current_map[trend_name]
            historical_trend = historical_map[trend_name]
            
            current_value = current_trend.get("current_value", 0)
            historical_value = historical_trend.get("current_value", 0)
            
            change_absolute = current_value - historical_value
            change_percentage = ((current_value - historical_value) / historical_value * 100) if historical_value != 0 else 0
            
            # Calcular aceleración (cambio en la velocidad de cambio)
            current_change = current_trend.get("change_percentage", 0)
            historical_change = historical_trend.get("change_percentage", 0)
            acceleration = current_change - historical_change
            
            comparison = TrendComparison(
                trend_name=trend_name,
                current_value=current_value,
                previous_value=historical_value,
                change_absolute=change_absolute,
                change_percentage=change_percentage,
                trend_acceleration=acceleration,
                period_comparison=period
            )
            
            comparisons.append({
                "trend_name": trend_name,
                "current_value": current_value,
                "historical_value": historical_value,
                "change_absolute": change_absolute,
                "change_percentage": change_percentage,
                "acceleration": acceleration,
                "status": "improved" if change_percentage > 5 else "declined" if change_percentage < -5 else "stable"
            })
            
            if change_percentage > 5:
                trends_improved += 1
            elif change_percentage < -5:
                trends_declined += 1
            else:
                trends_stable += 1
        
        return {
            "period": period,
            "historical_date": historical["date"],
            "comparisons": comparisons,
            "summary": {
                "trends_improved": trends_improved,
                "trends_declined": trends_declined,
                "trends_stable": trends_stable,
                "total_comparable": len(comparisons)
            }
        }
    
    def _generate_comparison_summary(
        self,
        comparisons: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera resumen de comparaciones."""
        total_improved = sum(
            c.get("summary", {}).get("trends_improved", 0)
            for c in comparisons.values()
        )
        total_declined = sum(
            c.get("summary", {}).get("trends_declined", 0)
            for c in comparisons.values()
        )
        total_stable = sum(
            c.get("summary", {}).get("trends_stable", 0)
            for c in comparisons.values()
        )
        
        overall_sentiment = "positive" if total_improved > total_declined else "negative" if total_declined > total_improved else "neutral"
        
        return {
            "total_improved": total_improved,
            "total_declined": total_declined,
            "total_stable": total_stable,
            "overall_sentiment": overall_sentiment,
            "improvement_rate": (total_improved / max(total_improved + total_declined + total_stable, 1)) * 100
        }
    
    def identify_trend_patterns(
        self,
        industry: str,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Identifica patrones en tendencias históricas.
        
        Args:
            industry: Industria
            lookback_days: Días hacia atrás
            
        Returns:
            Patrones identificados
        """
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            import json
            
            pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT analysis_data, analysis_date
                FROM market_trends_analysis
                WHERE industry = %s
                AND analysis_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY analysis_date ASC
            """, (industry, lookback_days))
            
            historical_analyses = []
            for row in cursor.fetchall():
                historical_analyses.append({
                    "data": row[0],
                    "date": row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1])
                })
            
            cursor.close()
            conn.close()
            
            if len(historical_analyses) < 3:
                return {"patterns_available": False, "reason": "Insufficient historical data"}
            
            # Analizar patrones
            patterns = self._analyze_patterns(historical_analyses)
            
            return {
                "patterns_available": True,
                "industry": industry,
                "lookback_days": lookback_days,
                "analyses_count": len(historical_analyses),
                "patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
            return {"patterns_available": False, "error": str(e)}
    
    def _analyze_patterns(
        self,
        historical_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza patrones en datos históricos."""
        # Agrupar tendencias por nombre
        trends_by_name = {}
        
        for analysis in historical_analyses:
            trends = analysis["data"].get("trends", [])
            date = analysis["date"]
            
            for trend in trends:
                name = trend.get("trend_name", "unknown")
                if name not in trends_by_name:
                    trends_by_name[name] = []
                
                trends_by_name[name].append({
                    "date": date,
                    "value": trend.get("current_value", 0),
                    "change": trend.get("change_percentage", 0)
                })
        
        # Identificar patrones
        patterns = {
            "increasing_trends": [],
            "decreasing_trends": [],
            "volatile_trends": [],
            "stable_trends": []
        }
        
        for trend_name, values in trends_by_name.items():
            if len(values) < 3:
                continue
            
            # Calcular tendencia general
            changes = [v["change"] for v in values]
            avg_change = sum(changes) / len(changes)
            volatility = sum(abs(c - avg_change) for c in changes) / len(changes)
            
            if avg_change > 5 and volatility < 10:
                patterns["increasing_trends"].append({
                    "name": trend_name,
                    "average_change": avg_change,
                    "volatility": volatility
                })
            elif avg_change < -5 and volatility < 10:
                patterns["decreasing_trends"].append({
                    "name": trend_name,
                    "average_change": avg_change,
                    "volatility": volatility
                })
            elif volatility > 15:
                patterns["volatile_trends"].append({
                    "name": trend_name,
                    "average_change": avg_change,
                    "volatility": volatility
                })
            else:
                patterns["stable_trends"].append({
                    "name": trend_name,
                    "average_change": avg_change,
                    "volatility": volatility
                })
        
        return patterns






