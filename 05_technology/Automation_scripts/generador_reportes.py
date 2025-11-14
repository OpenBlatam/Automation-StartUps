#!/usr/bin/env python3
"""
Generador de Reportes Ejecutivos
Crea reportes personalizados basados en métricas y progreso
"""

from datetime import datetime, timedelta
from typing import Dict, List
import json

class ReportGenerator:
    def __init__(self):
        self.metrics_template = {
            'daily': ['revenue', 'pipeline', 'leads', 'deals_closed'],
            'weekly': ['mrr', 'cac', 'ltv', 'churn', 'nps'],
            'monthly': ['arr', 'gross_margin', 'ebitda_margin', 'customers', 'team_size']
        }
    
    def generate_daily_report(self, day: int, actual_metrics: Dict) -> str:
        """
        Genera reporte diario
        
        Args:
            day: Día de implementación
            actual_metrics: Métricas actuales
            
        Returns:
            Reporte formateado
        """
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    REPORTE DIARIO - DÍA {day}                                 ║
║                    {datetime.now().strftime('%Y-%m-%d %H:%M')}                                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 MÉTRICAS DEL DÍA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Revenue (MTD):        ${actual_metrics.get('revenue', 0):,.0f}
Pipeline Value:       ${actual_metrics.get('pipeline', 0):,.0f}
Nuevos Leads:         {actual_metrics.get('leads', 0)}
Deals Cerrados:       {actual_metrics.get('deals_closed', 0)}
Active Users:         {actual_metrics.get('active_users', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PROGRESO VS TARGET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Revenue:      {actual_metrics.get('revenue_progress', 0):.1f}% de target
Pipeline:     {actual_metrics.get('pipeline_progress', 0):.1f}% de target
Leads:        {actual_metrics.get('leads_progress', 0):.1f}% de target
Deals:        {actual_metrics.get('deals_progress', 0):.1f}% de target

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 ALERTAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Agregar alertas según métricas
        alerts = []
        if actual_metrics.get('revenue_progress', 100) < 80:
            alerts.append('🔴 REVENUE: Por debajo de target')
        if actual_metrics.get('pipeline_progress', 100) < 70:
            alerts.append('🟡 PIPELINE: Revisar generación de leads')
        if actual_metrics.get('churn', 0) > 10:
            alerts.append('🔴 CHURN: Por encima de threshold (10%)')
        
        if alerts:
            for alert in alerts:
                report += f"{alert}\n"
        else:
            report += "🟢 Todo en track - Sin alertas críticas\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 ACCIONES PRIORITARIAS (MAÑANA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [ ] {"acción_prioritaria_1" if day <= 30 else "Optimizar conversion"}
2. [ ] {"acción_prioritaria_2" if day <= 30 else "Expandir marketing reach"}
3. [ ] {"acción_prioritaria_3" if day <= 30 else "Cerrar deals en pipeline"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        return report
    
    def generate_weekly_report(self, week: int, metrics: Dict) -> str:
        """Genera reporte semanal"""
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     REPORTE SEMANAL - SEMANA {week}                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

📈 RESÚMEN DE LA SEMANA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MRR:                    ${metrics.get('mrr', 0):,.0f}
CAC:                    ${metrics.get('cac', 0):,.0f}
LTV:                    ${metrics.get('ltv', 0):,.0f}
LTV/CAC Ratio:          {metrics.get('ltv_cac_ratio', 0):.1f}:1
Churn Rate:             {metrics.get('churn', 0):.1f}%
NPS Score:              {metrics.get('nps', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 TRENDS DE LA SEMANA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Agregar trends
        trends = []
        if metrics.get('mrr_growth', 0) > 0:
            trends.append(f"✅ MRR: +{metrics.get('mrr_growth', 0):.1f}% vs. semana anterior")
        if metrics.get('churn_change', 0) < 0:
            trends.append(f"✅ Churn: {metrics.get('churn_change', 0):.1f}% improvement")
        if metrics.get('nps_change', 0) > 0:
            trends.append(f"✅ NPS: +{metrics.get('nps_change', 0):.1f} pts improvement")
        
        for trend in trends:
            report += f"{trend}\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 HITOS ALCANZADOS ESTA SEMANA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Agregar milestones alcanzados
        milestones = []
        if week == 4:
            milestones.append("✅ MVP Funcional Completo")
        if metrics.get('deals_closed_week', 0) >= 2:
            milestones.append(f"✅ {metrics.get('deals_closed_week', 0)} Deals Cerrados")
        if metrics.get('pipeline', 0) >= 500_000:
            milestones.append("✅ Pipeline >$500K")
        
        for milestone in milestones:
            report += f"{milestone}\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report
    
    def generate_executive_summary(self, day: int, metrics: Dict) -> str:
        """Genera resumen ejecutivo"""
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     RESUMEN EJECUTIVO - DÍA {day}                              ║
║                         {datetime.now().strftime('%B %Y')}                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

🎯 STATUS GENERAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Progress:              {day} / 90 días ({day/90*100:.1f}% completado)
Phase:                 {"Fundación" if day <= 30 else "Validación" if day <= 60 else "Escalamiento"}
Status:                {"🟢 On Track" if metrics.get('on_track', True) else "🟡 Attention Needed"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 MÉTRICAS FINANCIERAS CLAVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MRR:                   ${metrics.get('mrr', 0):,.0f}
ARR Run Rate:          ${metrics.get('arr_run_rate', 0):,.0f}
Gross Margin:          {metrics.get('gross_margin', 0):.1f}%
EBITDA Margin:         {metrics.get('ebitda_margin', 0):.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 MÉTRICAS DE TRACCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Customers:       {metrics.get('customers', 0)}
New Customers (MTD):   {metrics.get('new_customers', 0)}
Churn Rate:            {metrics.get('churn', 0):.1f}%
NPS:                   {metrics.get('nps', 0)}
CSAT:                  {metrics.get('csat', 0):.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 UNIT ECONOMICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CAC:                   ${metrics.get('cac', 0):,.0f}
LTV:                   ${metrics.get('ltv', 0):,.0f}
LTV/CAC Ratio:         {metrics.get('ltv_cac_ratio', 0):.1f}:1
Payback Period:        {metrics.get('payback_months', 0):.1f} meses

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 RIESGOS Y OPORTUNIDADES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Agregar riesgos y oportunidades
        risks = []
        opportunities = []
        
        if metrics.get('churn', 0) > 8:
            risks.append(f"🔴 Churn alto: {metrics.get('churn', 0):.1f}%")
        if metrics.get('pipeline_coverage', 0) < 3:
            risks.append(f"🟡 Pipeline bajo: {metrics.get('pipeline_coverage', 0):.1f}x")
        
        if metrics.get('mrr_growth', 0) > 15:
            opportunities.append(f"🟢 Crecimiento fuerte: +{metrics.get('mrr_growth', 0):.1f}%")
        if metrics.get('win_rate', 0) > 25:
            opportunities.append(f"🟢 Win rate excelente: {metrics.get('win_rate', 0):.1f}%")
        
        for risk in risks:
            report += f"{risk}\n"
        for opp in opportunities:
            report += f"{opp}\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report


def main():
    """Función principal"""
    generator = ReportGenerator()
    
    # Métricas de ejemplo
    daily_metrics = {
        'revenue': 12500,
        'pipeline': 285000,
        'leads': 8,
        'deals_closed': 1,
        'active_users': 1250,
        'revenue_progress': 85,
        'pipeline_progress': 95,
        'leads_progress': 90,
        'deals_progress': 75,
        'churn': 6.5
    }
    
    weekly_metrics = {
        'mrr': 50000,
        'cac': 2875,
        'ltv': 95000,
        'ltv_cac_ratio': 33,
        'churn': 6.5,
        'nps': 68,
        'mrr_growth': 12.5,
        'churn_change': -0.5,
        'nps_change': 3,
        'deals_closed_week': 3,
        'pipeline': 750000
    }
    
    executive_metrics = {
        'on_track': True,
        'mrr': 50000,
        'arr_run_rate': 600000,
        'gross_margin': 92,
        'ebitda_margin': 65,
        'customers': 156,
        'new_customers': 24,
        'churn': 6.5,
        'nps': 68,
        'csat': 92,
        'cac': 2875,
        'ltv': 95000,
        'ltv_cac_ratio': 33,
        'payback_months': 5.2,
        'churn': 6.5,
        'pipeline_coverage': 3.1,
        'mrr_growth': 12.5,
        'win_rate': 28
    }
    
    # Generar reportes
    print(generator.generate_daily_report(15, daily_metrics))
    print(generator.generate_weekly_report(2, weekly_metrics))
    print(generator.generate_executive_summary(45, executive_metrics))


if __name__ == "__main__":
    main()



