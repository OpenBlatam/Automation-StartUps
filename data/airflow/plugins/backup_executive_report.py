"""
Módulo de Reportes Ejecutivos de Backups.

Genera reportes de alto nivel para ejecutivos:
- Resumen ejecutivo
- Métricas clave (KPIs)
- Tendencias
- Riesgos y recomendaciones
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from data.airflow.plugins.backup_analytics import BackupAnalyticsEngine
from data.airflow.plugins.backup_compliance import BackupComplianceValidator
from data.airflow.plugins.backup_health import BackupHealthChecker

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummary:
    """Resumen ejecutivo."""
    period_start: datetime
    period_end: datetime
    total_backups: int
    success_rate: float
    total_size_gb: float
    compliance_status: str
    health_status: str
    key_risks: List[str]
    recommendations: List[str]
    cost_estimate: Optional[float] = None


class ExecutiveReportGenerator:
    """Generador de reportes ejecutivos."""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        """
        Inicializa generador de reportes.
        
        Args:
            backup_dir: Directorio de backups
        """
        self.backup_dir = backup_dir
        self.analytics = BackupAnalyticsEngine(backup_dir=backup_dir)
        self.compliance = BackupComplianceValidator(backup_dir=backup_dir)
        self.health = BackupHealthChecker(backup_dir=backup_dir)
    
    def generate_monthly_executive_report(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte ejecutivo mensual.
        
        Args:
            month: Mes (1-12, None = mes actual)
            year: Año (None = año actual)
        """
        # Obtener analytics mensual
        analytics_report = self.analytics.generate_monthly_report(month=month, year=year)
        
        # Obtener compliance
        compliance_results = self.compliance.validate_all()
        
        # Obtener health check
        health_results = self.health.check_all()
        
        # Calcular KPIs
        analytics = analytics_report['analytics']
        kpis = {
            'success_rate': analytics['success_rate'],
            'total_backups': analytics['total_backups'],
            'total_size_gb': analytics['total_size_gb'],
            'avg_backups_per_day': analytics['total_backups'] / 30 if analytics['total_backups'] > 0 else 0,
            'compliance_score': self._calculate_compliance_score(compliance_results),
            'health_score': self._calculate_health_score(health_results)
        }
        
        # Identificar riesgos
        risks = self._identify_risks(analytics_report, compliance_results, health_results)
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(kpis, risks)
        
        # Estimar costos
        cost_estimate = self._estimate_costs(analytics['total_size_gb'])
        
        return {
            'period': {
                'month': analytics_report['month'],
                'year': analytics_report['year'],
                'start': analytics['period_start'],
                'end': analytics['period_end']
            },
            'kpis': kpis,
            'compliance': {
                'status': compliance_results['overall_status'],
                'summary': compliance_results['summary']
            },
            'health': {
                'status': health_results['overall_status'],
                'summary': health_results['summary']
            },
            'risks': risks,
            'recommendations': recommendations,
            'cost_estimate': cost_estimate,
            'trends': analytics_report.get('trends', {}),
            'space_prediction': analytics_report.get('space_prediction', {})
        }
    
    def _calculate_compliance_score(self, compliance_results: Dict[str, Any]) -> float:
        """Calcula score de compliance (0-100)."""
        summary = compliance_results['summary']
        total = summary['total_checks']
        
        if total == 0:
            return 0.0
        
        compliant = summary['compliant']
        return (compliant / total) * 100
    
    def _calculate_health_score(self, health_results: Dict[str, Any]) -> float:
        """Calcula score de salud (0-100)."""
        summary = health_results['summary']
        total = summary['total']
        
        if total == 0:
            return 0.0
        
        healthy = summary['healthy']
        return (healthy / total) * 100
    
    def _identify_risks(
        self,
        analytics: Dict[str, Any],
        compliance: Dict[str, Any],
        health: Dict[str, Any]
    ) -> List[str]:
        """Identifica riesgos basados en datos."""
        risks = []
        
        # Riesgo de tasa de éxito baja
        if analytics['analytics']['success_rate'] < 0.95:
            risks.append(
                f"Backup success rate below 95% ({analytics['analytics']['success_rate']:.1%})"
            )
        
        # Riesgo de compliance
        if compliance['overall_status'] == 'non_compliant':
            risks.append("System is non-compliant with backup policies")
        
        # Riesgo de salud
        if health['overall_status'] == 'critical':
            risks.append("System health is critical")
        
        # Riesgo de espacio
        if 'space_prediction' in analytics:
            prediction = analytics['space_prediction']
            if prediction.get('predicted_size_gb', 0) > 100:
                risks.append(
                    f"Predicted space needs high: {prediction['predicted_size_gb']:.2f}GB"
                )
        
        # Riesgo de frecuencia
        if analytics['analytics']['total_backups'] < 20:  # Menos de 20 backups en el mes
            risks.append("Backup frequency may be insufficient")
        
        return risks
    
    def _generate_recommendations(
        self,
        kpis: Dict[str, Any],
        risks: List[str]
    ) -> List[str]:
        """Genera recomendaciones basadas en KPIs y riesgos."""
        recommendations = []
        
        # Recomendaciones basadas en tasa de éxito
        if kpis['success_rate'] < 0.95:
            recommendations.append(
                "Investigate and fix backup failures to improve success rate above 95%"
            )
        
        # Recomendaciones basadas en compliance
        if kpis['compliance_score'] < 80:
            recommendations.append(
                "Address compliance issues to meet policy requirements"
            )
        
        # Recomendaciones basadas en salud
        if kpis['health_score'] < 80:
            recommendations.append(
                "Address system health issues to ensure reliable backups"
            )
        
        # Recomendaciones basadas en espacio
        if len([r for r in risks if 'space' in r.lower()]) > 0:
            recommendations.append(
                "Plan for additional storage capacity or implement more aggressive retention policies"
            )
        
        # Recomendaciones generales
        if not recommendations:
            recommendations.append(
                "System is operating well. Continue monitoring and maintain current practices."
            )
        
        return recommendations
    
    def _estimate_costs(self, total_size_gb: float) -> Dict[str, Any]:
        """
        Estima costos de almacenamiento.
        
        Args:
            total_size_gb: Tamaño total en GB
        
        Returns:
            Dict con estimaciones de costo
        """
        # Precios aproximados (USD por GB/mes)
        storage_prices = {
            'aws_s3_standard': 0.023,
            'aws_s3_glacier': 0.004,
            'azure_blob_hot': 0.018,
            'azure_blob_cool': 0.01,
            'gcp_standard': 0.02,
            'gcp_nearline': 0.01
        }
        
        estimates = {}
        
        for provider, price_per_gb in storage_prices.items():
            monthly_cost = total_size_gb * price_per_gb
            annual_cost = monthly_cost * 12
            estimates[provider] = {
                'monthly_usd': round(monthly_cost, 2),
                'annual_usd': round(annual_cost, 2)
            }
        
        return {
            'total_size_gb': total_size_gb,
            'estimates': estimates,
            'note': 'Estimates based on standard pricing. Actual costs may vary.'
        }
    
    def format_executive_summary(self, report: Dict[str, Any]) -> str:
        """Formatea reporte como resumen ejecutivo legible."""
        period = report['period']
        kpis = report['kpis']
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║        BACKUP SYSTEM EXECUTIVE REPORT                       ║
║        {period['year']}/{str(period['month']).zfill(2)}                                    ║
╚══════════════════════════════════════════════════════════════╝

📊 KEY PERFORMANCE INDICATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Success Rate:        {kpis['success_rate']:.1%}
• Total Backups:       {kpis['total_backups']}
• Total Size:          {kpis['total_size_gb']:.2f} GB
• Avg Backups/Day:     {kpis['avg_backups_per_day']:.1f}
• Compliance Score:    {kpis['compliance_score']:.1f}/100
• Health Score:        {kpis['health_score']:.1f}/100

🔒 COMPLIANCE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {report['compliance']['status'].upper()}
• Compliant:     {report['compliance']['summary']['compliant']}
• Non-compliant: {report['compliance']['summary']['non_compliant']}
• Warnings:      {report['compliance']['summary']['warnings']}

🏥 HEALTH STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: {report['health']['status'].upper()}
• Healthy:  {report['health']['summary']['healthy']}
• Warnings: {report['health']['summary']['warnings']}
• Critical: {report['health']['summary']['critical']}
"""
        
        if report['risks']:
            summary += f"""
⚠️  IDENTIFIED RISKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for i, risk in enumerate(report['risks'], 1):
                summary += f"{i}. {risk}\n"
        
        if report['recommendations']:
            summary += f"""
💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for i, rec in enumerate(report['recommendations'], 1):
                summary += f"{i}. {rec}\n"
        
        if report.get('cost_estimate'):
            cost = report['cost_estimate']
            summary += f"""
💰 COST ESTIMATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Size: {cost['total_size_gb']:.2f} GB

Estimated Monthly Costs (USD):
"""
            for provider, costs in cost['estimates'].items():
                summary += f"• {provider}: ${costs['monthly_usd']:.2f}/month\n"
        
        return summary

