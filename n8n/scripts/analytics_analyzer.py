#!/usr/bin/env python3
"""
Analytics Analyzer - Script avanzado para análisis de métricas
Proporciona análisis profundo de performance y recomendaciones
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

class AnalyticsAnalyzer:
    """Analizador avanzado de métricas de automatización"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def get_performance_data(self, period: str = '7d') -> Dict:
        """Obtiene datos de performance"""
        url = f"{self.api_base_url}/analytics/performance"
        params = {"period": period}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def calculate_health_score(self, metrics: Dict) -> Dict:
        """Calcula health score general del sistema"""
        score = 100
        issues = []
        
        # Cart abandonment
        if metrics.get('cartAbandonmentRate', 0) > 80:
            score -= 20
            issues.append('High cart abandonment rate')
        elif metrics.get('cartAbandonmentRate', 0) > 70:
            score -= 10
            issues.append('Moderate cart abandonment rate')
        
        # Email open rate
        if metrics.get('emailOpenRate', 0) < 20:
            score -= 15
            issues.append('Low email open rate')
        elif metrics.get('emailOpenRate', 0) < 25:
            score -= 8
            issues.append('Moderate email open rate')
        
        # Email click rate
        if metrics.get('emailClickRate', 0) < 5:
            score -= 15
            issues.append('Low email click rate')
        elif metrics.get('emailClickRate', 0) < 8:
            score -= 8
            issues.append('Moderate email click rate')
        
        # Conversion rate
        if metrics.get('conversionRate', 0) < 10:
            score -= 20
            issues.append('Low conversion rate')
        elif metrics.get('conversionRate', 0) < 15:
            score -= 10
            issues.append('Moderate conversion rate')
        
        # Recovery rate
        if metrics.get('recoveryRate', 0) < 25:
            score -= 15
            issues.append('Low recovery rate')
        elif metrics.get('recoveryRate', 0) < 35:
            score -= 8
            issues.append('Moderate recovery rate')
        
        score = max(0, min(100, score))
        
        # Determinar status
        if score >= 80:
            status = 'excellent'
        elif score >= 60:
            status = 'good'
        elif score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'score': score,
            'status': status,
            'issues': issues
        }
    
    def analyze_trends(self, current: Dict, previous: Dict) -> Dict:
        """Analiza tendencias comparando períodos"""
        trends = {}
        
        metrics_to_compare = [
            'cartAbandonmentRate',
            'emailOpenRate',
            'emailClickRate',
            'conversionRate',
            'recoveryRate',
            'revenue'
        ]
        
        for metric in metrics_to_compare:
            current_val = current.get(metric, 0)
            previous_val = previous.get(metric, 0)
            change = current_val - previous_val
            change_percent = (change / previous_val * 100) if previous_val > 0 else 0
            
            trends[metric] = {
                'current': current_val,
                'previous': previous_val,
                'change': change,
                'changePercent': change_percent,
                'direction': 'up' if change > 0 else 'down' if change < 0 else 'stable'
            }
        
        return trends
    
    def generate_recommendations(self, metrics: Dict, trends: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en métricas y tendencias"""
        recommendations = []
        
        # Recomendación: Mejorar timing si open rate bajo
        if metrics.get('emailOpenRate', 0) < 25:
            recommendations.append({
                'priority': 'high',
                'category': 'timing',
                'title': 'Optimizar horarios de envío',
                'description': 'La tasa de apertura es baja. Considera ajustar los horarios de envío basado en datos históricos.',
                'action': 'analyze_best_send_times'
            })
        
        # Recomendación: Mejorar contenido si click rate bajo
        if metrics.get('emailClickRate', 0) < 8:
            recommendations.append({
                'priority': 'high',
                'category': 'content',
                'title': 'Mejorar CTAs y contenido',
                'description': 'La tasa de clic es baja. Prueba diferentes CTAs, mensajes y diseño.',
                'action': 'test_new_content'
            })
        
        # Recomendación: Ajustar descuentos si recovery bajo
        if metrics.get('recoveryRate', 0) < 30:
            recommendations.append({
                'priority': 'medium',
                'category': 'discount',
                'title': 'Revisar estrategia de descuentos',
                'description': 'La tasa de recuperación es baja. Considera ajustar niveles de descuento o timing.',
                'action': 'review_discount_strategy'
            })
        
        # Recomendación: Revisar checkout si abandono alto
        if metrics.get('cartAbandonmentRate', 0) > 75:
            recommendations.append({
                'priority': 'critical',
                'category': 'checkout',
                'title': 'Revisar proceso de checkout',
                'description': 'La tasa de abandono es muy alta. Revisa el proceso de checkout para identificar problemas.',
                'action': 'audit_checkout_process'
            })
        
        # Recomendación: Optimizar si tendencia negativa
        for metric, trend in trends.items():
            if trend['direction'] == 'down' and abs(trend['changePercent']) > 10:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'optimization',
                    'title': f'Revisar {metric}',
                    'description': f'{metric} ha disminuido {abs(trend["changePercent"]):.1f}%. Investiga la causa.',
                    'action': f'investigate_{metric}'
                })
        
        return recommendations
    
    def calculate_roi(self, metrics: Dict) -> Dict:
        """Calcula ROI del sistema de automatización"""
        revenue = metrics.get('revenue', 0)
        recovered_value = metrics.get('recoveredValue', 0)
        total_value = metrics.get('totalValue', 0)
        
        # Estimación de costos (ajustar según tu caso)
        estimated_costs = {
            'api_costs': 400,  # Costos de APIs mensuales
            'infrastructure': 100,  # Infraestructura
            'maintenance': 200  # Mantenimiento
        }
        total_costs = sum(estimated_costs.values())
        
        total_revenue = revenue + recovered_value
        roi = ((total_revenue - total_costs) / total_costs * 100) if total_costs > 0 else 0
        
        return {
            'totalRevenue': total_revenue,
            'totalCosts': total_costs,
            'netProfit': total_revenue - total_costs,
            'roi': roi,
            'breakdown': {
                'revenue': revenue,
                'recoveredValue': recovered_value,
                'costs': estimated_costs
            }
        }
    
    def generate_report(self, period: str = '7d') -> Dict:
        """Genera reporte completo de análisis"""
        current_data = self.get_performance_data(period)
        previous_data = self.get_performance_data('14d')  # Para comparar
        
        metrics = current_data.get('metrics', {})
        previous_metrics = previous_data.get('metrics', {})
        
        health = self.calculate_health_score(metrics)
        trends = self.analyze_trends(metrics, previous_metrics)
        recommendations = self.generate_recommendations(metrics, trends)
        roi = self.calculate_roi(metrics)
        
        return {
            'period': period,
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'metrics': metrics,
            'trends': trends,
            'recommendations': recommendations,
            'roi': roi,
            'summary': {
                'status': health['status'],
                'score': health['score'],
                'totalRecommendations': len(recommendations),
                'criticalRecommendations': len([r for r in recommendations if r['priority'] == 'critical']),
                'roi': roi['roi']
            }
        }


def main():
    """Ejemplo de uso"""
    api_url = os.getenv("API_BASE_URL", "https://api.yourdomain.com")
    api_key = os.getenv("API_KEY", "your_api_key_here")
    
    analyzer = AnalyticsAnalyzer(api_url, api_key)
    
    # Generar reporte
    report = analyzer.generate_report('7d')
    
    print("=" * 50)
    print("REPORTE DE ANÁLISIS")
    print("=" * 50)
    print(f"\nHealth Score: {report['health']['score']} ({report['health']['status']})")
    print(f"\nROI: {report['roi']['roi']:.2f}%")
    print(f"\nRecomendaciones: {report['summary']['totalRecommendations']}")
    print(f"Críticas: {report['summary']['criticalRecommendations']}")
    
    print("\n" + "=" * 50)
    print("RECOMENDACIONES")
    print("=" * 50)
    for rec in report['recommendations']:
        print(f"\n[{rec['priority'].upper()}] {rec['title']}")
        print(f"  {rec['description']}")
    
    # Guardar reporte
    with open(f"report_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n\nReporte guardado en: report_{datetime.now().strftime('%Y%m%d')}.json")


if __name__ == "__main__":
    main()










