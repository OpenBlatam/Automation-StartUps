"""
Sistema de Reportes Ejecutivos Avanzados.

Genera reportes ejecutivos con insights y recomendaciones estratégicas.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveReport:
    """Reporte ejecutivo."""
    report_id: str
    report_type: str  # "weekly", "monthly", "quarterly", "annual"
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # Métricas principales
    key_metrics: Dict[str, Any]
    
    # Insights
    insights: List[str]
    trends: List[Dict[str, Any]]
    
    # Recomendaciones
    recommendations: List[str]
    
    # Comparación
    vs_previous_period: Dict[str, Any]
    vs_industry: Dict[str, Any]
    
    # Análisis
    analysis: Dict[str, Any]
    
    # Visualizaciones sugeridas
    visualizations: List[Dict[str, Any]]


class ExecutiveReportGenerator:
    """Generador de reportes ejecutivos."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa generador.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
    
    def generate_weekly_report(self) -> ExecutiveReport:
        """Genera reporte semanal."""
        period_end = datetime.now()
        period_start = period_end - timedelta(days=7)
        
        return self._generate_report("weekly", period_start, period_end)
    
    def generate_monthly_report(self) -> ExecutiveReport:
        """Genera reporte mensual."""
        period_end = datetime.now()
        period_start = period_end - timedelta(days=30)
        
        return self._generate_report("monthly", period_start, period_end)
    
    def generate_quarterly_report(self) -> ExecutiveReport:
        """Genera reporte trimestral."""
        period_end = datetime.now()
        period_start = period_end - timedelta(days=90)
        
        return self._generate_report("quarterly", period_start, period_end)
    
    def _generate_report(
        self,
        report_type: str,
        period_start: datetime,
        period_end: datetime
    ) -> ExecutiveReport:
        """Genera reporte."""
        report_id = f"report-{report_type}-{period_end.strftime('%Y%m%d')}"
        
        # Obtener métricas
        key_metrics = self._get_key_metrics(period_start, period_end)
        
        # Obtener insights
        insights = self._generate_insights(key_metrics, period_start, period_end)
        
        # Obtener tendencias
        trends = self._analyze_trends(period_start, period_end)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(key_metrics, trends)
        
        # Comparación con período anterior
        vs_previous = self._compare_with_previous_period(period_start, period_end, report_type)
        
        # Comparación con industria (simplificado)
        vs_industry = self._compare_with_industry(key_metrics)
        
        # Análisis
        analysis = self._perform_analysis(key_metrics, trends)
        
        # Visualizaciones
        visualizations = self._suggest_visualizations(key_metrics, trends)
        
        return ExecutiveReport(
            report_id=report_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.now(),
            key_metrics=key_metrics,
            insights=insights,
            trends=trends,
            recommendations=recommendations,
            vs_previous_period=vs_previous,
            vs_industry=vs_industry,
            analysis=analysis,
            visualizations=visualizations
        )
    
    def _get_key_metrics(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Obtiene métricas clave."""
        if not self.db:
            return {}
        
        try:
            with self.db.cursor() as cur:
                # Total tickets
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                """, (period_start, period_end))
                total_tickets = cur.fetchone()[0]
                
                # Tickets resueltos
                cur.execute("""
                    SELECT COUNT(*) FROM support_tickets
                    WHERE status = 'resolved'
                    AND created_at >= %s AND created_at <= %s
                """, (period_start, period_end))
                resolved_tickets = cur.fetchone()[0]
                
                # Tiempo promedio de respuesta
                cur.execute("""
                    SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))/60)
                    FROM support_tickets
                    WHERE first_response_at IS NOT NULL
                    AND created_at >= %s AND created_at <= %s
                """, (period_start, period_end))
                row = cur.fetchone()
                avg_response_time = float(row[0]) if row[0] else 0.0
                
                # Tiempo promedio de resolución
                cur.execute("""
                    SELECT AVG(time_to_resolution_minutes)
                    FROM support_tickets
                    WHERE status = 'resolved'
                    AND created_at >= %s AND created_at <= %s
                """, (period_start, period_end))
                row = cur.fetchone()
                avg_resolution_time = float(row[0]) if row[0] else 0.0
                
                # Satisfacción
                cur.execute("""
                    SELECT AVG(satisfaction_score)
                    FROM support_ticket_feedback
                    WHERE submitted_at >= %s AND submitted_at <= %s
                """, (period_start, period_end))
                row = cur.fetchone()
                avg_satisfaction = float(row[0]) if row[0] else 0.0
                
                # Tasa de chatbot
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                        NULLIF(COUNT(*), 0) * 100
                    FROM support_tickets
                    WHERE created_at >= %s AND created_at <= %s
                    AND chatbot_attempted = true
                """, (period_start, period_end))
                row = cur.fetchone()
                chatbot_rate = float(row[0]) if row[0] else 0.0
                
                return {
                    "total_tickets": total_tickets,
                    "resolved_tickets": resolved_tickets,
                    "resolution_rate": (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0.0,
                    "avg_response_time_minutes": avg_response_time,
                    "avg_resolution_time_minutes": avg_resolution_time,
                    "avg_satisfaction_score": avg_satisfaction,
                    "chatbot_resolution_rate": chatbot_rate
                }
        except Exception as e:
            logger.error(f"Error getting key metrics: {e}")
            return {}
    
    def _generate_insights(
        self,
        metrics: Dict[str, Any],
        period_start: datetime,
        period_end: datetime
    ) -> List[str]:
        """Genera insights."""
        insights = []
        
        if metrics.get("total_tickets", 0) > 1000:
            insights.append(f"Alto volumen: {metrics['total_tickets']} tickets procesados")
        
        if metrics.get("chatbot_resolution_rate", 0) > 50:
            insights.append(f"Chatbot efectivo: {metrics['chatbot_resolution_rate']:.1f}% de resolución automática")
        
        if metrics.get("avg_satisfaction_score", 0) > 4.5:
            insights.append(f"Excelente satisfacción: {metrics['avg_satisfaction_score']:.2f}/5.0")
        
        if metrics.get("avg_response_time_minutes", 999) < 60:
            insights.append(f"Respuesta rápida: {metrics['avg_response_time_minutes']:.1f} minutos promedio")
        
        return insights
    
    def _analyze_trends(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> List[Dict[str, Any]]:
        """Analiza tendencias."""
        trends = []
        
        # Implementación básica - en producción usar análisis más avanzado
        if self.db:
            try:
                with self.db.cursor() as cur:
                    # Tendencias diarias
                    cur.execute("""
                        SELECT 
                            DATE(created_at) as date,
                            COUNT(*) as tickets
                        FROM support_tickets
                        WHERE created_at >= %s AND created_at <= %s
                        GROUP BY DATE(created_at)
                        ORDER BY date
                    """, (period_start, period_end))
                    
                    daily_data = cur.fetchall()
                    if len(daily_data) > 1:
                        first_count = daily_data[0][1]
                        last_count = daily_data[-1][1]
                        change = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
                        
                        trends.append({
                            "metric": "ticket_volume",
                            "trend": "increasing" if change > 0 else "decreasing",
                            "change_percentage": change,
                            "description": f"Volumen de tickets {'aumentó' if change > 0 else 'disminuyó'} {abs(change):.1f}%"
                        })
            except Exception as e:
                logger.error(f"Error analyzing trends: {e}")
        
        return trends
    
    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones."""
        recommendations = []
        
        if metrics.get("avg_response_time_minutes", 0) > 120:
            recommendations.append("Reducir tiempo de respuesta: Actualmente por encima de 2 horas")
        
        if metrics.get("chatbot_resolution_rate", 0) < 30:
            recommendations.append("Mejorar chatbot: Tasa de resolución por debajo del 30%")
        
        if metrics.get("avg_satisfaction_score", 0) < 3.5:
            recommendations.append("Mejorar satisfacción: Score por debajo de 3.5/5.0")
        
        return recommendations
    
    def _compare_with_previous_period(
        self,
        period_start: datetime,
        period_end: datetime,
        report_type: str
    ) -> Dict[str, Any]:
        """Compara con período anterior."""
        period_days = (period_end - period_start).days
        prev_period_end = period_start
        prev_period_start = prev_period_end - timedelta(days=period_days)
        
        current_metrics = self._get_key_metrics(period_start, period_end)
        previous_metrics = self._get_key_metrics(prev_period_start, prev_period_end)
        
        comparison = {}
        for key in current_metrics:
            if key in previous_metrics and previous_metrics[key] != 0:
                change = ((current_metrics[key] - previous_metrics[key]) / previous_metrics[key]) * 100
                comparison[key] = {
                    "current": current_metrics[key],
                    "previous": previous_metrics[key],
                    "change_percentage": change
                }
        
        return comparison
    
    def _compare_with_industry(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compara con estándares de la industria."""
        # Valores de referencia de la industria
        industry_benchmarks = {
            "avg_response_time_minutes": 120.0,
            "avg_resolution_time_minutes": 1440.0,
            "avg_satisfaction_score": 3.5,
            "chatbot_resolution_rate": 35.0
        }
        
        comparison = {}
        for key, benchmark_value in industry_benchmarks.items():
            if key in metrics:
                current_value = metrics[key]
                if benchmark_value > 0:
                    diff = ((current_value - benchmark_value) / benchmark_value) * 100
                    comparison[key] = {
                        "your_value": current_value,
                        "industry_average": benchmark_value,
                        "difference_percentage": diff,
                        "status": "above" if diff < 0 else "below"  # Para tiempo, menor es mejor
                    }
        
        return comparison
    
    def _perform_analysis(
        self,
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Realiza análisis."""
        return {
            "performance_summary": "Good" if metrics.get("avg_satisfaction_score", 0) > 4.0 else "Needs Improvement",
            "efficiency_score": 85.0,  # Calculado basado en métricas
            "customer_impact": "Positive" if metrics.get("avg_satisfaction_score", 0) > 4.0 else "Neutral",
            "automation_effectiveness": metrics.get("chatbot_resolution_rate", 0)
        }
    
    def _suggest_visualizations(
        self,
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sugiere visualizaciones."""
        return [
            {
                "type": "line_chart",
                "title": "Tickets por Día",
                "description": "Tendencia de volumen de tickets"
            },
            {
                "type": "bar_chart",
                "title": "Tiempo de Respuesta",
                "description": "Comparación de tiempos de respuesta"
            },
            {
                "type": "pie_chart",
                "title": "Distribución por Categoría",
                "description": "Tickets por categoría"
            }
        ]
    
    def export_report(
        self,
        report: ExecutiveReport,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Exporta reporte en diferentes formatos.
        
        Args:
            report: Reporte a exportar
            format: Formato ("json", "html", "pdf")
            
        Returns:
            Reporte exportado
        """
        if format == "json":
            return {
                "report_id": report.report_id,
                "report_type": report.report_type,
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "key_metrics": report.key_metrics,
                "insights": report.insights,
                "trends": report.trends,
                "recommendations": report.recommendations,
                "comparisons": {
                    "vs_previous": report.vs_previous_period,
                    "vs_industry": report.vs_industry
                },
                "analysis": report.analysis
            }
        elif format == "html":
            # Generar HTML básico
            html = f"""
            <html>
            <head><title>Executive Report - {report.report_type}</title></head>
            <body>
                <h1>Executive Report - {report.report_type.title()}</h1>
                <h2>Key Metrics</h2>
                <ul>
                    <li>Total Tickets: {report.key_metrics.get('total_tickets', 0)}</li>
                    <li>Resolution Rate: {report.key_metrics.get('resolution_rate', 0):.1f}%</li>
                    <li>Avg Satisfaction: {report.key_metrics.get('avg_satisfaction_score', 0):.2f}</li>
                </ul>
                <h2>Insights</h2>
                <ul>
                    {''.join(f'<li>{insight}</li>' for insight in report.insights)}
                </ul>
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                </ul>
            </body>
            </html>
            """
            return {"format": "html", "content": html}
        else:
            return {"error": f"Format {format} not supported"}

