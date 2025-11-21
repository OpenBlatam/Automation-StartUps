"""
Sistema de Análisis y Reportes Avanzados
Versión: 2.0.0
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
from collections import defaultdict
import csv


class AnalyticsReport:
    """
    Genera reportes avanzados de análisis del chatbot
    """
    
    def __init__(self, chatbot_engine, learning_system):
        self.chatbot = chatbot_engine
        self.learning = learning_system
        self.reports_path = Path("reports")
        self.reports_path.mkdir(exist_ok=True)
    
    def generate_daily_report(self) -> Dict:
        """Genera reporte diario"""
        metrics = self.chatbot.get_metrics()
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "daily",
            "summary": {
                "total_interactions": metrics["total_interactions"],
                "resolved_first_contact": metrics["resolved_first_contact"],
                "resolution_rate": metrics["resolution_rate"],
                "avg_satisfaction": metrics["avg_satisfaction"],
                "avg_response_time": metrics["avg_response_time"],
                "escalations": metrics["escalated"],
                "escalation_rate": metrics["escalation_rate"]
            },
            "sentiment_analysis": metrics["sentiment_percentages"],
            "intent_distribution": metrics["intent_distribution"],
            "targets_status": metrics["targets"],
            "recommendations": self._generate_recommendations(metrics)
        }
        
        return report
    
    def generate_weekly_report(self) -> Dict:
        """Genera reporte semanal"""
        weekly_analysis = self.learning.analyze_weekly_performance()
        metrics = self.chatbot.get_metrics()
        
        report = {
            "period": "weekly",
            "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": {
                "total_interactions": metrics["total_interactions"],
                "resolution_rate": metrics["resolution_rate"],
                "avg_satisfaction": metrics["avg_satisfaction"],
                "avg_response_time": metrics["avg_response_time"],
                "escalation_rate": metrics["escalation_rate"]
            },
            "trends": {
                "sentiment_trend": metrics["sentiment_percentages"],
                "intent_trend": metrics["intent_distribution"]
            },
            "top_unresolved_questions": weekly_analysis["top_unresolved"],
            "improvement_suggestions": weekly_analysis["improvement_suggestions"],
            "recommendations": weekly_analysis["recommendations"],
            "faq_suggestions": self.learning.generate_faq_suggestions()
        }
        
        return report
    
    def generate_monthly_report(self) -> Dict:
        """Genera reporte mensual"""
        metrics = self.chatbot.get_metrics()
        unresolved = self.learning.get_unresolved_questions(limit=20)
        suggestions = self.learning.get_improvement_suggestions()
        
        # Calcular ROI estimado
        estimated_savings = self._calculate_estimated_savings(metrics)
        
        report = {
            "period": "monthly",
            "month": datetime.now().strftime("%Y-%m"),
            "executive_summary": {
                "total_interactions": metrics["total_interactions"],
                "automation_rate": metrics["resolution_rate"],
                "customer_satisfaction": metrics["avg_satisfaction"],
                "estimated_savings": estimated_savings,
                "key_achievements": self._identify_achievements(metrics)
            },
            "detailed_metrics": {
                "performance": {
                    "resolution_rate": metrics["resolution_rate"],
                    "satisfaction": metrics["avg_satisfaction"],
                    "response_time": metrics["avg_response_time"],
                    "escalation_rate": metrics["escalation_rate"]
                },
                "sentiment_analysis": metrics["sentiment_percentages"],
                "intent_analysis": metrics["intent_distribution"],
                "conversation_analysis": {
                    "avg_length": metrics.get("avg_conversation_length", 0),
                    "active_sessions": metrics.get("active_conversations", 0)
                }
            },
            "improvement_areas": {
                "top_unresolved": unresolved,
                "suggestions": suggestions[:10],
                "faq_recommendations": self.learning.generate_faq_suggestions()
            },
            "next_steps": self._generate_next_steps(metrics, unresolved)
        }
        
        return report
    
    def _calculate_estimated_savings(self, metrics: Dict) -> Dict:
        """Calcula ahorros estimados"""
        # Asumiendo costo promedio de $25 por interacción humana
        # y tiempo promedio de 15 minutos por interacción
        cost_per_human_interaction = 25
        total_interactions = metrics["total_interactions"]
        resolved_by_bot = metrics["resolved_first_contact"]
        
        # Interacciones que el bot resolvió (no requirieron humano)
        bot_resolved = resolved_by_bot
        human_interactions_avoided = bot_resolved
        
        # Calcular ahorro
        estimated_savings = human_interactions_avoided * cost_per_human_interaction
        
        # Calcular horas ahorradas
        hours_per_interaction = 0.25  # 15 minutos
        hours_saved = human_interactions_avoided * hours_per_interaction
        
        return {
            "interactions_automated": bot_resolved,
            "estimated_cost_savings": estimated_savings,
            "hours_saved": hours_saved,
            "automation_percentage": metrics["resolution_rate"],
            "roi_estimate": f"{(estimated_savings / 1000):.1f}x" if estimated_savings > 0 else "0x"
        }
    
    def _identify_achievements(self, metrics: Dict) -> List[str]:
        """Identifica logros alcanzados"""
        achievements = []
        
        if metrics["resolution_rate"] >= 80:
            achievements.append(f"✅ Tasa de resolución del {metrics['resolution_rate']}% (objetivo: 80%)")
        
        if metrics["avg_satisfaction"] >= 4.5:
            achievements.append(f"✅ Satisfacción de {metrics['avg_satisfaction']}/5 (objetivo: 4.5/5)")
        
        if metrics["avg_response_time"] <= 60:
            achievements.append(f"✅ Tiempo de respuesta de {metrics['avg_response_time']:.1f}s (objetivo: <60s)")
        
        if metrics["escalation_rate"] < 20:
            achievements.append(f"✅ Tasa de escalamiento del {metrics['escalation_rate']}% (objetivo: <20%)")
        
        return achievements
    
    def _generate_recommendations(self, metrics: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en métricas"""
        recommendations = []
        
        if metrics["resolution_rate"] < 80:
            recommendations.append({
                "priority": "high",
                "category": "resolution_rate",
                "message": f"La tasa de resolución ({metrics['resolution_rate']}%) está por debajo del objetivo. Considera:",
                "actions": [
                    "Agregar más FAQs basadas en preguntas no resueltas",
                    "Mejorar la detección de intención",
                    "Refinar palabras clave y sinónimos"
                ]
            })
        
        if metrics["avg_satisfaction"] < 4.5:
            recommendations.append({
                "priority": "high",
                "category": "satisfaction",
                "message": f"La satisfacción ({metrics['avg_satisfaction']}/5) puede mejorar. Considera:",
                "actions": [
                    "Revisar respuestas con menor satisfacción",
                    "Personalizar respuestas según sentimiento",
                    "Mejorar el tono y claridad de las respuestas"
                ]
            })
        
        if metrics["avg_response_time"] > 60:
            recommendations.append({
                "priority": "medium",
                "category": "response_time",
                "message": f"El tiempo de respuesta ({metrics['avg_response_time']:.1f}s) puede optimizarse.",
                "actions": [
                    "Optimizar algoritmos de matching",
                    "Cachear respuestas frecuentes",
                    "Revisar integraciones que puedan estar causando demoras"
                ]
            })
        
        sentiment_dist = metrics["sentiment_percentages"]
        if sentiment_dist.get("negative", 0) + sentiment_dist.get("frustrated", 0) > 30:
            recommendations.append({
                "priority": "high",
                "category": "sentiment",
                "message": "Alto porcentaje de sentimientos negativos detectados.",
                "actions": [
                    "Revisar casos de escalamiento recientes",
                    "Mejorar respuestas para casos negativos",
                    "Considerar escalamiento proactivo"
                ]
            })
        
        return recommendations
    
    def _generate_next_steps(self, metrics: Dict, unresolved: List[Dict]) -> List[str]:
        """Genera próximos pasos recomendados"""
        next_steps = []
        
        # Basado en preguntas no resueltas
        if unresolved:
            top_unresolved = unresolved[0] if unresolved else None
            if top_unresolved and top_unresolved.get("frequency", 0) >= 5:
                next_steps.append(
                    f"Agregar FAQ para: '{top_unresolved['question']}' "
                    f"(aparece {top_unresolved['frequency']} veces)"
                )
        
        # Basado en métricas
        if metrics["resolution_rate"] < 80:
            next_steps.append("Incrementar base de conocimiento con nuevas FAQs")
        
        if metrics["avg_satisfaction"] < 4.5:
            next_steps.append("Revisar y mejorar respuestas existentes")
        
        # Basado en sentimientos
        sentiment_dist = metrics["sentiment_percentages"]
        if sentiment_dist.get("frustrated", 0) > 10:
            next_steps.append("Implementar detección proactiva de frustración")
        
        return next_steps
    
    def export_report_to_json(self, report: Dict, filename: str = None):
        """Exporta reporte a JSON"""
        if not filename:
            filename = f"report_{report.get('type', 'custom')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.reports_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reporte exportado a: {filepath}")
        return filepath
    
    def export_report_to_csv(self, report: Dict, filename: str = None):
        """Exporta métricas principales a CSV"""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.reports_path / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir encabezados
            writer.writerow(['Métrica', 'Valor', 'Objetivo', 'Estado'])
            
            # Escribir datos
            if 'summary' in report:
                summary = report['summary']
                writer.writerow(['Interacciones Totales', summary.get('total_interactions', 0), '-', '-'])
                writer.writerow(['Tasa de Resolución', f"{summary.get('resolution_rate', 0)}%", '80%', 
                               '✅' if summary.get('resolution_rate', 0) >= 80 else '❌'])
                writer.writerow(['Satisfacción', f"{summary.get('avg_satisfaction', 0)}/5", '4.5/5',
                               '✅' if summary.get('avg_satisfaction', 0) >= 4.5 else '❌'])
                writer.writerow(['Tiempo de Respuesta', f"{summary.get('avg_response_time', 0)}s", '<60s',
                               '✅' if summary.get('avg_response_time', 0) <= 60 else '❌'])
        
        print(f"✅ Métricas exportadas a CSV: {filepath}")
        return filepath
    
    def generate_executive_summary(self) -> str:
        """Genera resumen ejecutivo en texto"""
        metrics = self.chatbot.get_metrics()
        savings = self._calculate_estimated_savings(metrics)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           RESUMEN EJECUTIVO - CHATBOT                       ║
║           Período: {datetime.now().strftime('%Y-%m-%d')}                    ║
╚══════════════════════════════════════════════════════════════╝

📊 MÉTRICAS PRINCIPALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Interacciones Totales: {metrics['total_interactions']}
  • Tasa de Resolución: {metrics['resolution_rate']}% {'✅' if metrics['resolution_rate'] >= 80 else '❌'}
  • Satisfacción del Cliente: {metrics['avg_satisfaction']}/5 {'✅' if metrics['avg_satisfaction'] >= 4.5 else '❌'}
  • Tiempo Promedio de Respuesta: {metrics['avg_response_time']:.1f}s {'✅' if metrics['avg_response_time'] <= 60 else '❌'}
  • Tasa de Escalamiento: {metrics['escalation_rate']}%

💰 IMPACTO FINANCIERO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Interacciones Automatizadas: {savings['interactions_automated']}
  • Ahorro Estimado: ${savings['estimated_cost_savings']:,.2f}
  • Horas Ahorradas: {savings['hours_saved']:.1f} horas
  • ROI Estimado: {savings['roi_estimate']}

😊 ANÁLISIS DE SENTIMIENTOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for sentiment, percentage in metrics['sentiment_percentages'].items():
            summary += f"  • {sentiment.capitalize()}: {percentage}%\n"
        
        summary += f"""
🎯 RECOMENDACIONES PRINCIPALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        recommendations = self._generate_recommendations(metrics)
        for i, rec in enumerate(recommendations[:3], 1):
            summary += f"  {i}. {rec['message']}\n"
            for action in rec['actions'][:2]:
                summary += f"     - {action}\n"
        
        return summary


# Función de ejemplo
def main():
    """Ejemplo de uso del sistema de reportes"""
    from chatbot_engine import ChatbotEngine
    from learning_system import LearningSystem
    
    chatbot = ChatbotEngine()
    learning = LearningSystem(chatbot)
    analytics = AnalyticsReport(chatbot, learning)
    
    # Generar reporte diario
    daily_report = analytics.generate_daily_report()
    analytics.export_report_to_json(daily_report, "daily_report.json")
    
    # Generar resumen ejecutivo
    summary = analytics.generate_executive_summary()
    print(summary)
    
    # Exportar a CSV
    analytics.export_report_to_csv(daily_report)


if __name__ == "__main__":
    main()






