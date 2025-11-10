"""
Dashboard de Métricas para Chatbot
Sistema de análisis y reportes en tiempo real
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot de métricas en un momento dado"""
    timestamp: datetime
    total_interactions: int
    resolved_first_contact: int
    escalated: int
    avg_response_time: float
    resolution_rate: float
    escalation_rate: float
    avg_satisfaction: float
    interactions_by_channel: Dict[str, int]
    interactions_by_language: Dict[str, int]
    top_faqs: List[Dict]
    common_escalation_reasons: List[Dict]


class MetricsDashboard:
    """
    Dashboard de métricas avanzado para el chatbot
    """
    
    def __init__(self, data_dir: str = "metrics_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.snapshots: List[MetricSnapshot] = []
        self.load_historical_data()
    
    def load_historical_data(self):
        """Carga datos históricos desde archivos"""
        snapshot_files = sorted(self.data_dir.glob("snapshot_*.json"))
        for file in snapshot_files[-100:]:  # Últimas 100 snapshots
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    snapshot = MetricSnapshot(**data)
                    self.snapshots.append(snapshot)
            except Exception as e:
                logger.warning(f"Error cargando snapshot {file}: {e}")
    
    def save_snapshot(self, metrics: Dict):
        """Guarda un snapshot de métricas"""
        timestamp = datetime.now()
        
        snapshot = MetricSnapshot(
            timestamp=timestamp,
            total_interactions=metrics.get("total_interactions", 0),
            resolved_first_contact=metrics.get("resolved_first_contact", 0),
            escalated=metrics.get("escalated", 0),
            avg_response_time=metrics.get("avg_response_time", 0.0),
            resolution_rate=metrics.get("resolution_rate", 0.0),
            escalation_rate=metrics.get("escalation_rate", 0.0),
            avg_satisfaction=metrics.get("avg_satisfaction", 0.0),
            interactions_by_channel=metrics.get("interactions_by_channel", {}),
            interactions_by_language=metrics.get("interactions_by_language", {}),
            top_faqs=metrics.get("top_faqs", []),
            common_escalation_reasons=metrics.get("common_escalation_reasons", [])
        )
        
        self.snapshots.append(snapshot)
        
        # Guardar en archivo
        filename = f"snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.data_dir / filename
        
        snapshot_dict = asdict(snapshot)
        snapshot_dict['timestamp'] = snapshot.timestamp.isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Snapshot guardado: {filename}")
    
    def get_current_metrics(self, chatbot_metrics: Dict) -> Dict:
        """Obtiene métricas actuales con análisis"""
        return {
            "summary": {
                "total_interactions": chatbot_metrics.get("total_interactions", 0),
                "resolution_rate": chatbot_metrics.get("resolution_rate", 0.0),
                "escalation_rate": chatbot_metrics.get("escalation_rate", 0.0),
                "avg_response_time_seconds": round(chatbot_metrics.get("avg_response_time", 0.0), 2),
                "avg_satisfaction": chatbot_metrics.get("avg_satisfaction", 0.0),
                "targets": {
                    "resolution_rate_target": 80.0,
                    "satisfaction_target": 4.5,
                    "response_time_target": 60.0
                },
                "performance_vs_targets": {
                    "resolution_rate_met": chatbot_metrics.get("resolution_rate", 0) >= 80.0,
                    "satisfaction_met": chatbot_metrics.get("avg_satisfaction", 0) >= 4.5,
                    "response_time_met": chatbot_metrics.get("avg_response_time", 0) <= 60.0
                }
            },
            "trends": self._calculate_trends(),
            "breakdown": {
                "by_channel": chatbot_metrics.get("interactions_by_channel", {}),
                "by_language": chatbot_metrics.get("interactions_by_language", {}),
                "by_hour": self._get_hourly_distribution(),
                "by_day": self._get_daily_distribution()
            },
            "insights": self._generate_insights(chatbot_metrics)
        }
    
    def _calculate_trends(self) -> Dict:
        """Calcula tendencias basadas en snapshots históricos"""
        if len(self.snapshots) < 2:
            return {"resolution_rate": "insufficient_data", "satisfaction": "insufficient_data"}
        
        recent = self.snapshots[-7:]  # Últimos 7 días
        previous = self.snapshots[-14:-7] if len(self.snapshots) >= 14 else []
        
        trends = {}
        
        if recent:
            recent_avg_resolution = statistics.mean([s.resolution_rate for s in recent])
            recent_avg_satisfaction = statistics.mean([s.avg_satisfaction for s in recent])
            
            if previous:
                prev_avg_resolution = statistics.mean([s.resolution_rate for s in previous])
                prev_avg_satisfaction = statistics.mean([s.avg_satisfaction for s in previous])
                
                trends["resolution_rate"] = {
                    "current": round(recent_avg_resolution, 2),
                    "previous": round(prev_avg_resolution, 2),
                    "change": round(recent_avg_resolution - prev_avg_resolution, 2),
                    "trend": "up" if recent_avg_resolution > prev_avg_resolution else "down"
                }
                
                trends["satisfaction"] = {
                    "current": round(recent_avg_satisfaction, 2),
                    "previous": round(prev_avg_satisfaction, 2),
                    "change": round(recent_avg_satisfaction - prev_avg_satisfaction, 2),
                    "trend": "up" if recent_avg_satisfaction > prev_avg_satisfaction else "down"
                }
            else:
                trends["resolution_rate"] = {"current": round(recent_avg_resolution, 2)}
                trends["satisfaction"] = {"current": round(recent_avg_satisfaction, 2)}
        
        return trends
    
    def _get_hourly_distribution(self) -> Dict:
        """Distribución de interacciones por hora"""
        # En producción, esto vendría de los datos reales
        return {f"{h:02d}:00": 0 for h in range(24)}
    
    def _get_daily_distribution(self) -> Dict:
        """Distribución de interacciones por día"""
        if not self.snapshots:
            return {}
        
        daily = defaultdict(int)
        for snapshot in self.snapshots[-30:]:  # Últimos 30 días
            day = snapshot.timestamp.strftime("%Y-%m-%d")
            daily[day] += snapshot.total_interactions
        
        return dict(daily)
    
    def _generate_insights(self, metrics: Dict) -> List[str]:
        """Genera insights automáticos basados en métricas"""
        insights = []
        
        resolution_rate = metrics.get("resolution_rate", 0)
        if resolution_rate >= 80:
            insights.append("✅ Excelente tasa de resolución en primera interacción (>80%)")
        elif resolution_rate < 60:
            insights.append("⚠️ Tasa de resolución baja. Considera revisar las FAQs y mejorar las respuestas.")
        
        satisfaction = metrics.get("avg_satisfaction", 0)
        if satisfaction >= 4.5:
            insights.append("✅ Alta satisfacción del cliente (>4.5/5)")
        elif satisfaction < 3.5:
            insights.append("⚠️ Satisfacción del cliente por debajo del objetivo. Revisa las respuestas más comunes.")
        
        response_time = metrics.get("avg_response_time", 0)
        if response_time <= 60:
            insights.append("✅ Tiempo de respuesta excelente (<1 min)")
        elif response_time > 120:
            insights.append("⚠️ Tiempo de respuesta alto. Considera optimizar el procesamiento.")
        
        escalation_rate = metrics.get("escalation_rate", 0)
        if escalation_rate > 30:
            insights.append("⚠️ Alta tasa de escalamiento. Revisa las razones comunes de escalamiento.")
        
        return insights
    
    def generate_report(self, chatbot_metrics: Dict, period: str = "daily") -> str:
        """Genera un reporte en texto legible"""
        current = self.get_current_metrics(chatbot_metrics)
        summary = current["summary"]
        
        report = f"""
╔═══════════════════════════════════════════════════════════╗
║        REPORTE DE MÉTRICAS DEL CHATBOT - {period.upper()}        ║
╚═══════════════════════════════════════════════════════════╝

📊 RESUMEN GENERAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total de Interacciones: {summary['total_interactions']:,}
Tasa de Resolución: {summary['resolution_rate']:.2f}% {'✅' if summary['performance_vs_targets']['resolution_rate_met'] else '⚠️'}
Tasa de Escalamiento: {summary.get('escalation_rate', 0):.2f}%
Tiempo Promedio de Respuesta: {summary['avg_response_time_seconds']:.2f}s {'✅' if summary['performance_vs_targets']['response_time_met'] else '⚠️'}
Satisfacción Promedio: {summary['avg_satisfaction']:.2f}/5.0 {'✅' if summary['performance_vs_targets']['satisfaction_met'] else '⚠️'}

🎯 OBJETIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasa de Resolución: {summary['targets']['resolution_rate_target']}% (Actual: {summary['resolution_rate']:.2f}%)
Satisfacción: {summary['targets']['satisfaction_target']}/5 (Actual: {summary['avg_satisfaction']:.2f}/5)
Tiempo de Respuesta: <{summary['targets']['response_time_target']}s (Actual: {summary['avg_response_time_seconds']:.2f}s)

💡 INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for insight in current["insights"]:
            report += f"{insight}\n"
        
        if current["trends"]:
            report += "\n📈 TENDENCIAS\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            if "resolution_rate" in current["trends"] and isinstance(current["trends"]["resolution_rate"], dict):
                rr_trend = current["trends"]["resolution_rate"]
                if "change" in rr_trend:
                    trend_arrow = "📈" if rr_trend["trend"] == "up" else "📉"
                    report += f"Tasa de Resolución: {trend_arrow} {rr_trend['change']:+.2f}% vs período anterior\n"
        
        report += "\n" + "="*60 + "\n"
        report += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def export_to_json(self, chatbot_metrics: Dict) -> Dict:
        """Exporta métricas a formato JSON"""
        return self.get_current_metrics(chatbot_metrics)


# Función de utilidad para generar dashboard HTML
def generate_html_dashboard(metrics: Dict) -> str:
    """Genera un dashboard HTML visual"""
    summary = metrics.get("summary", {})
    
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Chatbot - Métricas</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .metric-card h3 {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard de Métricas del Chatbot</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Interacciones</h3>
                <div class="value">{summary.get('total_interactions', 0):,}</div>
            </div>
            <div class="metric-card">
                <h3>Tasa de Resolución</h3>
                <div class="value">{summary.get('resolution_rate', 0):.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Satisfacción Promedio</h3>
                <div class="value">{summary.get('avg_satisfaction', 0):.1f}/5</div>
            </div>
            <div class="metric-card">
                <h3>Tiempo Respuesta</h3>
                <div class="value">{summary.get('avg_response_time_seconds', 0):.1f}s</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="satisfactionChart"></canvas>
        </div>
    </div>
    
    <script>
        // Gráfico de satisfacción (ejemplo)
        const ctx = document.getElementById('satisfactionChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                datasets: [{{
                    label: 'Satisfacción',
                    data: [4.5, 4.6, 4.7, 4.5, 4.8, 4.6, 4.7],
                    borderColor: 'rgb(102, 126, 234)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Satisfacción del Cliente (Últimos 7 días)'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html

