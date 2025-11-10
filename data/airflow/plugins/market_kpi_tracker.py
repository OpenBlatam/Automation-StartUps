"""
Sistema de Tracking de KPIs de Mercado

Monitorea y trackea KPIs clave de mercado en tiempo real:
- KPIs de tendencias
- KPIs de oportunidades
- KPIs de competencia
- KPIs de sentimiento
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarketKPI:
    """KPI de mercado."""
    kpi_id: str
    kpi_name: str
    category: str
    current_value: float
    previous_value: float
    target_value: float
    change_percentage: float
    status: str  # 'on_track', 'at_risk', 'exceeded'
    trend: str  # 'up', 'down', 'stable'
    last_updated: datetime


class MarketKPITracker:
    """Tracker de KPIs de mercado."""
    
    def __init__(self, postgres_conn_id: Optional[str] = None):
        """
        Inicializa el tracker.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self.logger = logging.getLogger(__name__)
    
    def track_market_kpis(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """
        Trackea KPIs de mercado.
        
        Args:
            market_analysis: Análisis de mercado
            insights: Insights generados
            industry: Industria
            
        Returns:
            KPIs trackeados
        """
        logger.info(f"Tracking market KPIs for {industry}")
        
        kpis = []
        
        # KPI: Tendencias alcistas
        trends = market_analysis.get("trends", [])
        upward_trends = len([t for t in trends if t.get("trend_direction") == "up"])
        total_trends = len(trends)
        upward_ratio = (upward_trends / total_trends * 100) if total_trends > 0 else 0
        
        kpis.append(MarketKPI(
            kpi_id="upward_trends_ratio",
            kpi_name="Upward Trends Ratio",
            category="trends",
            current_value=upward_ratio,
            previous_value=upward_ratio * 0.95,  # Simulado
            target_value=60.0,
            change_percentage=((upward_ratio - upward_ratio * 0.95) / (upward_ratio * 0.95) * 100) if upward_ratio * 0.95 > 0 else 0,
            status="on_track" if upward_ratio >= 50 else "at_risk",
            trend="up" if upward_ratio > 50 else "down",
            last_updated=datetime.utcnow()
        ))
        
        # KPI: Insights de alta prioridad
        high_priority_insights = len([i for i in insights if i.get("priority") == "high"])
        total_insights = len(insights)
        high_priority_ratio = (high_priority_insights / total_insights * 100) if total_insights > 0 else 0
        
        kpis.append(MarketKPI(
            kpi_id="high_priority_insights_ratio",
            kpi_name="High Priority Insights Ratio",
            category="insights",
            current_value=high_priority_ratio,
            previous_value=high_priority_ratio * 0.9,
            target_value=30.0,
            change_percentage=((high_priority_ratio - high_priority_ratio * 0.9) / (high_priority_ratio * 0.9) * 100) if high_priority_ratio * 0.9 > 0 else 0,
            status="exceeded" if high_priority_ratio > 30 else "on_track",
            trend="up" if high_priority_ratio > 20 else "stable",
            last_updated=datetime.utcnow()
        ))
        
        # KPI: Oportunidades identificadas
        opportunities = market_analysis.get("opportunities", [])
        opportunities_count = len(opportunities)
        
        kpis.append(MarketKPI(
            kpi_id="opportunities_count",
            kpi_name="Opportunities Identified",
            category="opportunities",
            current_value=float(opportunities_count),
            previous_value=opportunities_count * 0.8,
            target_value=5.0,
            change_percentage=((opportunities_count - opportunities_count * 0.8) / (opportunities_count * 0.8) * 100) if opportunities_count * 0.8 > 0 else 0,
            status="exceeded" if opportunities_count > 5 else "on_track",
            trend="up" if opportunities_count > 3 else "stable",
            last_updated=datetime.utcnow()
        ))
        
        # KPI: Riesgos identificados
        risks = market_analysis.get("risk_factors", [])
        risks_count = len(risks)
        
        kpis.append(MarketKPI(
            kpi_id="risks_count",
            kpi_name="Risk Factors Identified",
            category="risks",
            current_value=float(risks_count),
            previous_value=risks_count * 1.1,
            target_value=2.0,  # Menos es mejor
            change_percentage=((risks_count - risks_count * 1.1) / (risks_count * 1.1) * 100) if risks_count * 1.1 > 0 else 0,
            status="on_track" if risks_count <= 2 else "at_risk",
            trend="down" if risks_count < 3 else "up",
            last_updated=datetime.utcnow()
        ))
        
        # Convertir a dict para retorno
        kpis_dict = [
            {
                "kpi_id": k.kpi_id,
                "kpi_name": k.kpi_name,
                "category": k.category,
                "current_value": k.current_value,
                "previous_value": k.previous_value,
                "target_value": k.target_value,
                "change_percentage": k.change_percentage,
                "status": k.status,
                "trend": k.trend,
                "last_updated": k.last_updated.isoformat()
            }
            for k in kpis
        ]
        
        # Calcular score general
        overall_score = self._calculate_overall_kpi_score(kpis)
        
        return {
            "industry": industry,
            "tracking_date": datetime.utcnow().isoformat(),
            "kpis": kpis_dict,
            "overall_score": overall_score,
            "kpis_on_track": len([k for k in kpis if k.status == "on_track"]),
            "kpis_at_risk": len([k for k in kpis if k.status == "at_risk"]),
            "kpis_exceeded": len([k for k in kpis if k.status == "exceeded"])
        }
    
    def _calculate_overall_kpi_score(self, kpis: List[MarketKPI]) -> Dict[str, Any]:
        """Calcula score general de KPIs."""
        if not kpis:
            return {"score": 0, "level": "unknown"}
        
        # Calcular score basado en status
        scores = {
            "exceeded": 100,
            "on_track": 75,
            "at_risk": 50
        }
        
        avg_score = sum(scores.get(k.status, 50) for k in kpis) / len(kpis)
        
        if avg_score >= 85:
            level = "excellent"
        elif avg_score >= 70:
            level = "good"
        elif avg_score >= 55:
            level = "fair"
        else:
            level = "poor"
        
        return {
            "score": avg_score,
            "level": level,
            "max_score": 100
        }
    
    def save_kpis_to_db(
        self,
        kpis_data: Dict[str, Any],
        table_name: str = "market_kpis"
    ) -> bool:
        """Guarda KPIs en base de datos."""
        if not self.postgres_conn_id:
            return False
        
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            import json
            
            pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    industry VARCHAR(255),
                    tracking_date TIMESTAMP,
                    kpi_data JSONB,
                    overall_score JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insertar KPIs
            cursor.execute(f"""
                INSERT INTO {table_name} (industry, tracking_date, kpi_data, overall_score)
                VALUES (%s, %s, %s, %s)
            """, (
                kpis_data["industry"],
                kpis_data["tracking_date"],
                json.dumps(kpis_data["kpis"]),
                json.dumps(kpis_data["overall_score"])
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"KPIs saved to database for {kpis_data['industry']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving KPIs to database: {e}")
            return False






