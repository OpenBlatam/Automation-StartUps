"""
Sistema de Benchmarking y Comparación.

Compara rendimiento del sistema con benchmarks y estándares de la industria.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class BenchmarkCategory(Enum):
    """Categorías de benchmark."""
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    SATISFACTION = "satisfaction"
    CHATBOT_EFFECTIVENESS = "chatbot_effectiveness"
    AGENT_PRODUCTIVITY = "agent_productivity"
    FIRST_CONTACT_RESOLUTION = "first_contact_resolution"


@dataclass
class Benchmark:
    """Benchmark de la industria."""
    category: BenchmarkCategory
    metric_name: str
    industry_average: float
    industry_top_10: float
    industry_top_1: float
    your_value: Optional[float] = None
    unit: str = ""


@dataclass
class BenchmarkComparison:
    """Comparación con benchmarks."""
    comparison_id: str
    benchmark: Benchmark
    your_value: float
    percentile: float  # 0-100, qué percentil representa
    vs_average: float  # Diferencia vs promedio
    vs_top_10: float  # Diferencia vs top 10%
    vs_top_1: float  # Diferencia vs top 1%
    rating: str  # "excellent", "good", "average", "below_average"
    recommendations: List[str]


class BenchmarkingEngine:
    """Motor de benchmarking."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa motor de benchmarking.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.industry_benchmarks = self._load_industry_benchmarks()
    
    def _load_industry_benchmarks(self) -> Dict[BenchmarkCategory, Benchmark]:
        """Carga benchmarks de la industria."""
        benchmarks = {
            BenchmarkCategory.RESPONSE_TIME: Benchmark(
                category=BenchmarkCategory.RESPONSE_TIME,
                metric_name="First Response Time",
                industry_average=120.0,  # minutos
                industry_top_10=60.0,
                industry_top_1=30.0,
                unit="minutes"
            ),
            BenchmarkCategory.RESOLUTION_TIME: Benchmark(
                category=BenchmarkCategory.RESOLUTION_TIME,
                metric_name="Resolution Time",
                industry_average=1440.0,  # 24 horas en minutos
                industry_top_10=720.0,  # 12 horas
                industry_top_1=360.0,  # 6 horas
                unit="minutes"
            ),
            BenchmarkCategory.SATISFACTION: Benchmark(
                category=BenchmarkCategory.SATISFACTION,
                metric_name="Customer Satisfaction",
                industry_average=3.5,  # en escala 1-5
                industry_top_10=4.2,
                industry_top_1=4.7,
                unit="score (1-5)"
            ),
            BenchmarkCategory.CHATBOT_EFFECTIVENESS: Benchmark(
                category=BenchmarkCategory.CHATBOT_EFFECTIVENESS,
                metric_name="Chatbot Resolution Rate",
                industry_average=35.0,  # porcentaje
                industry_top_10=55.0,
                industry_top_1=75.0,
                unit="percentage"
            ),
            BenchmarkCategory.AGENT_PRODUCTIVITY: Benchmark(
                category=BenchmarkCategory.AGENT_PRODUCTIVITY,
                metric_name="Tickets per Agent per Day",
                industry_average=15.0,
                industry_top_10=25.0,
                industry_top_1=35.0,
                unit="tickets/day"
            ),
            BenchmarkCategory.FIRST_CONTACT_RESOLUTION: Benchmark(
                category=BenchmarkCategory.FIRST_CONTACT_RESOLUTION,
                metric_name="First Contact Resolution Rate",
                industry_average=70.0,  # porcentaje
                industry_top_10=85.0,
                industry_top_1=95.0,
                unit="percentage"
            )
        }
        
        return benchmarks
    
    def compare_with_benchmarks(self, days: int = 30) -> List[BenchmarkComparison]:
        """
        Compara métricas actuales con benchmarks.
        
        Args:
            days: Días a analizar
            
        Returns:
            Lista de comparaciones
        """
        comparisons = []
        
        if not self.db:
            return comparisons
        
        try:
            with self.db.cursor() as cur:
                # Response Time
                cur.execute("""
                    SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                    FROM support_tickets
                    WHERE first_response_at IS NOT NULL
                    AND created_at >= NOW() - INTERVAL %s days
                """, (days,))
                row = cur.fetchone()
                response_time = float(row[0]) if row[0] else None
                
                if response_time:
                    comp = self._compare_metric(
                        BenchmarkCategory.RESPONSE_TIME,
                        response_time,
                        lower_is_better=True
                    )
                    comparisons.append(comp)
                
                # Resolution Time
                cur.execute("""
                    SELECT AVG(time_to_resolution_minutes)
                    FROM support_tickets
                    WHERE status = 'resolved'
                    AND created_at >= NOW() - INTERVAL %s days
                """, (days,))
                row = cur.fetchone()
                resolution_time = float(row[0]) if row[0] else None
                
                if resolution_time:
                    comp = self._compare_metric(
                        BenchmarkCategory.RESOLUTION_TIME,
                        resolution_time,
                        lower_is_better=True
                    )
                    comparisons.append(comp)
                
                # Satisfaction
                cur.execute("""
                    SELECT AVG(satisfaction_score)
                    FROM support_ticket_feedback
                    WHERE submitted_at >= NOW() - INTERVAL %s days
                """, (days,))
                row = cur.fetchone()
                satisfaction = float(row[0]) if row[0] else None
                
                if satisfaction:
                    comp = self._compare_metric(
                        BenchmarkCategory.SATISFACTION,
                        satisfaction,
                        lower_is_better=False
                    )
                    comparisons.append(comp)
                
                # Chatbot Effectiveness
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                        NULLIF(COUNT(*), 0) * 100
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL %s days
                    AND chatbot_attempted = true
                """, (days,))
                row = cur.fetchone()
                chatbot_rate = float(row[0]) if row[0] else None
                
                if chatbot_rate:
                    comp = self._compare_metric(
                        BenchmarkCategory.CHATBOT_EFFECTIVENESS,
                        chatbot_rate,
                        lower_is_better=False
                    )
                    comparisons.append(comp)
                
                # Agent Productivity
                cur.execute("""
                    SELECT 
                        COUNT(*)::float / NULLIF(COUNT(DISTINCT assigned_agent_id), 0) / %s
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL %s days
                    AND assigned_agent_id IS NOT NULL
                    AND status = 'resolved'
                """, (days, days))
                row = cur.fetchone()
                productivity = float(row[0]) if row[0] else None
                
                if productivity:
                    comp = self._compare_metric(
                        BenchmarkCategory.AGENT_PRODUCTIVITY,
                        productivity,
                        lower_is_better=False
                    )
                    comparisons.append(comp)
        
        except Exception as e:
            logger.error(f"Error comparing benchmarks: {e}")
        
        return comparisons
    
    def _compare_metric(
        self,
        category: BenchmarkCategory,
        your_value: float,
        lower_is_better: bool = False
    ) -> BenchmarkComparison:
        """Compara una métrica con benchmarks."""
        benchmark = self.industry_benchmarks[category]
        
        # Calcular diferencias
        vs_avg = your_value - benchmark.industry_average
        vs_top10 = your_value - benchmark.industry_top_10
        vs_top1 = your_value - benchmark.industry_top_1
        
        # Ajustar según si menor es mejor
        if lower_is_better:
            vs_avg = -vs_avg
            vs_top10 = -vs_top10
            vs_top1 = -vs_top1
        
        # Calcular percentil aproximado
        if lower_is_better:
            # Para métricas donde menor es mejor
            if your_value <= benchmark.industry_top_1:
                percentile = 99.0
            elif your_value <= benchmark.industry_top_10:
                percentile = 90.0 + ((benchmark.industry_top_10 - your_value) / (benchmark.industry_top_10 - benchmark.industry_top_1)) * 9.0
            elif your_value <= benchmark.industry_average:
                percentile = 50.0 + ((benchmark.industry_average - your_value) / (benchmark.industry_average - benchmark.industry_top_10)) * 40.0
            else:
                percentile = 50.0 - ((your_value - benchmark.industry_average) / benchmark.industry_average) * 50.0
        else:
            # Para métricas donde mayor es mejor
            if your_value >= benchmark.industry_top_1:
                percentile = 99.0
            elif your_value >= benchmark.industry_top_10:
                percentile = 90.0 + ((your_value - benchmark.industry_top_10) / (benchmark.industry_top_1 - benchmark.industry_top_10)) * 9.0
            elif your_value >= benchmark.industry_average:
                percentile = 50.0 + ((your_value - benchmark.industry_average) / (benchmark.industry_top_10 - benchmark.industry_average)) * 40.0
            else:
                percentile = 50.0 - ((benchmark.industry_average - your_value) / benchmark.industry_average) * 50.0
        
        percentile = max(0.0, min(100.0, percentile))
        
        # Determinar rating
        if percentile >= 90:
            rating = "excellent"
        elif percentile >= 75:
            rating = "good"
        elif percentile >= 50:
            rating = "average"
        else:
            rating = "below_average"
        
        # Generar recomendaciones
        recommendations = []
        if percentile < 50:
            recommendations.append(f"Mejorar {benchmark.metric_name}: Actualmente en percentil {percentile:.1f}")
        if vs_avg < 0 and not lower_is_better:
            recommendations.append(f"Estás {(abs(vs_avg)/benchmark.industry_average)*100:.1f}% por debajo del promedio de la industria")
        if vs_top10 < 0:
            recommendations.append("Objetivo: alcanzar top 10% de la industria")
        
        return BenchmarkComparison(
            comparison_id=f"benchmark-{category.value}-{datetime.now().timestamp()}",
            benchmark=benchmark,
            your_value=your_value,
            percentile=percentile,
            vs_average=vs_avg,
            vs_top_10=vs_top10,
            vs_top_1=vs_top1,
            rating=rating,
            recommendations=recommendations
        )
    
    def get_benchmark_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Genera reporte completo de benchmarking.
        
        Args:
            days: Días a analizar
            
        Returns:
            Reporte de benchmarking
        """
        comparisons = self.compare_with_benchmarks(days)
        
        if not comparisons:
            return {"error": "No data available for comparison"}
        
        # Calcular scores promedio
        avg_percentile = sum(c.percentile for c in comparisons) / len(comparisons)
        excellent_count = sum(1 for c in comparisons if c.rating == "excellent")
        good_count = sum(1 for c in comparisons if c.rating == "good")
        average_count = sum(1 for c in comparisons if c.rating == "average")
        below_avg_count = sum(1 for c in comparisons if c.rating == "below_average")
        
        # Prioridades de mejora
        improvement_priorities = sorted(
            comparisons,
            key=lambda c: c.percentile
        )[:3]  # Top 3 áreas de mejora
        
        return {
            "period_days": days,
            "total_metrics": len(comparisons),
            "average_percentile": avg_percentile,
            "rating_distribution": {
                "excellent": excellent_count,
                "good": good_count,
                "average": average_count,
                "below_average": below_avg_count
            },
            "comparisons": [
                {
                    "category": c.benchmark.category.value,
                    "metric": c.benchmark.metric_name,
                    "your_value": c.your_value,
                    "industry_average": c.benchmark.industry_average,
                    "percentile": c.percentile,
                    "rating": c.rating,
                    "vs_average_pct": (c.vs_average / c.benchmark.industry_average * 100) if c.benchmark.industry_average != 0 else 0
                }
                for c in comparisons
            ],
            "improvement_priorities": [
                {
                    "metric": c.benchmark.metric_name,
                    "current_percentile": c.percentile,
                    "recommendations": c.recommendations
                }
                for c in improvement_priorities
            ],
            "overall_assessment": self._generate_overall_assessment(avg_percentile, comparisons)
        }
    
    def _generate_overall_assessment(
        self,
        avg_percentile: float,
        comparisons: List[BenchmarkComparison]
    ) -> str:
        """Genera evaluación general."""
        if avg_percentile >= 90:
            return "Excelente rendimiento. Estás en el top 10% de la industria."
        elif avg_percentile >= 75:
            return "Buen rendimiento. Estás por encima del promedio de la industria."
        elif avg_percentile >= 50:
            return "Rendimiento promedio. Hay oportunidades de mejora."
        else:
            return "Rendimiento por debajo del promedio. Se recomienda implementar mejoras urgentes."

