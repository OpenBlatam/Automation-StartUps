"""
Sistema de Analytics y Dashboard para descripciones de productos.

Incluye:
- Métricas de rendimiento
- Análisis de tendencias
- Comparativas de plataformas
- Reportes automáticos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class DescriptionAnalytics:
    """Sistema de analytics para descripciones."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_metric(self, description_id: str, metric_type: str, value: float, metadata: Dict = None):
        """
        Registra una métrica.
        
        Args:
            description_id: ID de la descripción
            metric_type: Tipo de métrica (view, click, conversion, revenue)
            value: Valor de la métrica
            metadata: Metadata adicional
        """
        self.metrics[description_id].append({
            'type': metric_type,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    def get_description_stats(self, description_id: str, days: int = 30) -> Dict:
        """
        Obtiene estadísticas de una descripción.
        
        Args:
            description_id: ID de la descripción
            days: Días a analizar
        
        Returns:
            Dict con estadísticas
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        description_metrics = [
            m for m in self.metrics.get(description_id, [])
            if datetime.fromisoformat(m['timestamp']) >= cutoff_date
        ]
        
        if not description_metrics:
            return {
                'description_id': description_id,
                'period_days': days,
                'total_views': 0,
                'total_clicks': 0,
                'total_conversions': 0,
                'total_revenue': 0,
                'conversion_rate': 0,
                'ctr': 0,
                'avg_revenue_per_conversion': 0
            }
        
        views = sum(m['value'] for m in description_metrics if m['type'] == 'view')
        clicks = sum(m['value'] for m in description_metrics if m['type'] == 'click')
        conversions = sum(m['value'] for m in description_metrics if m['type'] == 'conversion')
        revenue = sum(m['value'] for m in description_metrics if m['type'] == 'revenue')
        
        conversion_rate = (conversions / views * 100) if views > 0 else 0
        ctr = (clicks / views * 100) if views > 0 else 0
        avg_revenue = (revenue / conversions) if conversions > 0 else 0
        
        return {
            'description_id': description_id,
            'period_days': days,
            'total_views': views,
            'total_clicks': clicks,
            'total_conversions': conversions,
            'total_revenue': revenue,
            'conversion_rate': round(conversion_rate, 2),
            'ctr': round(ctr, 2),
            'avg_revenue_per_conversion': round(avg_revenue, 2)
        }
    
    def get_platform_comparison(self, days: int = 30) -> Dict:
        """
        Compara rendimiento por plataforma.
        
        Args:
            days: Días a analizar
        
        Returns:
            Dict con comparación por plataforma
        """
        platform_stats = defaultdict(lambda: {
            'views': 0,
            'clicks': 0,
            'conversions': 0,
            'revenue': 0
        })
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for desc_id, metrics in self.metrics.items():
            for metric in metrics:
                if datetime.fromisoformat(metric['timestamp']) >= cutoff_date:
                    platform = metric.get('metadata', {}).get('platform', 'unknown')
                    
                    if metric['type'] == 'view':
                        platform_stats[platform]['views'] += metric['value']
                    elif metric['type'] == 'click':
                        platform_stats[platform]['clicks'] += metric['value']
                    elif metric['type'] == 'conversion':
                        platform_stats[platform]['conversions'] += metric['value']
                    elif metric['type'] == 'revenue':
                        platform_stats[platform]['revenue'] += metric['value']
        
        # Calcular tasas
        comparison = {}
        for platform, stats in platform_stats.items():
            views = stats['views']
            clicks = stats['clicks']
            conversions = stats['conversions']
            
            comparison[platform] = {
                **stats,
                'conversion_rate': round((conversions / views * 100) if views > 0 else 0, 2),
                'ctr': round((clicks / views * 100) if views > 0 else 0, 2),
                'avg_revenue_per_conversion': round((stats['revenue'] / conversions) if conversions > 0 else 0, 2)
            }
        
        return comparison
    
    def get_top_performers(self, metric_type: str = 'conversion_rate', limit: int = 10) -> List[Dict]:
        """
        Obtiene las mejores descripciones por métrica.
        
        Args:
            metric_type: Tipo de métrica para ranking
            limit: Número de resultados
        
        Returns:
            Lista de top performers
        """
        performers = []
        
        for desc_id in self.metrics.keys():
            stats = self.get_description_stats(desc_id)
            if stats.get(metric_type, 0) > 0:
                performers.append({
                    'description_id': desc_id,
                    **stats
                })
        
        # Ordenar por métrica
        performers.sort(key=lambda x: x.get(metric_type, 0), reverse=True)
        
        return performers[:limit]
    
    def generate_report(self, days: int = 30) -> Dict:
        """
        Genera un reporte completo de analytics.
        
        Args:
            days: Días a analizar
        
        Returns:
            Dict con reporte completo
        """
        total_descriptions = len(self.metrics)
        
        # Estadísticas generales
        all_stats = []
        for desc_id in self.metrics.keys():
            stats = self.get_description_stats(desc_id, days)
            if stats['total_views'] > 0:
                all_stats.append(stats)
        
        if not all_stats:
            return {
                'period_days': days,
                'total_descriptions': total_descriptions,
                'message': 'No hay datos suficientes para el período'
            }
        
        # Agregar estadísticas
        total_views = sum(s['total_views'] for s in all_stats)
        total_clicks = sum(s['total_clicks'] for s in all_stats)
        total_conversions = sum(s['total_conversions'] for s in all_stats)
        total_revenue = sum(s['total_revenue'] for s in all_stats)
        
        avg_conversion_rate = sum(s['conversion_rate'] for s in all_stats) / len(all_stats) if all_stats else 0
        
        # Top performers
        top_by_conversion = self.get_top_performers('conversion_rate', 5)
        top_by_revenue = self.get_top_performers('total_revenue', 5)
        
        # Comparación por plataforma
        platform_comparison = self.get_platform_comparison(days)
        
        return {
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_descriptions': total_descriptions,
                'active_descriptions': len(all_stats),
                'total_views': total_views,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_revenue': total_revenue,
                'overall_conversion_rate': round((total_conversions / total_views * 100) if total_views > 0 else 0, 2),
                'overall_ctr': round((total_clicks / total_views * 100) if total_views > 0 else 0, 2),
                'avg_conversion_rate': round(avg_conversion_rate, 2)
            },
            'top_performers': {
                'by_conversion_rate': top_by_conversion,
                'by_revenue': top_by_revenue
            },
            'platform_comparison': platform_comparison,
            'insights': DescriptionAnalytics._generate_insights(all_stats, platform_comparison)
        }
    
    @staticmethod
    def _generate_insights(all_stats: List[Dict], platform_comparison: Dict) -> List[str]:
        """Genera insights automáticos del reporte."""
        insights = []
        
        if not all_stats:
            return insights
        
        # Insight sobre conversión promedio
        avg_conv = sum(s['conversion_rate'] for s in all_stats) / len(all_stats)
        if avg_conv < 2:
            insights.append(f"La tasa de conversión promedio ({avg_conv:.2f}%) está por debajo del estándar. Considera optimizar las descripciones.")
        elif avg_conv > 5:
            insights.append(f"Excelente tasa de conversión promedio ({avg_conv:.2f}%). Mantén este nivel.")
        
        # Insight sobre plataforma
        if platform_comparison:
            best_platform = max(platform_comparison.items(), key=lambda x: x[1].get('conversion_rate', 0))
            worst_platform = min(platform_comparison.items(), key=lambda x: x[1].get('conversion_rate', 0))
            
            if best_platform[1].get('conversion_rate', 0) > worst_platform[1].get('conversion_rate', 0) * 1.5:
                insights.append(f"{best_platform[0].upper()} muestra mejor rendimiento que {worst_platform[0].upper()}. Considera replicar estrategias exitosas.")
        
        # Insight sobre variación
        conv_rates = [s['conversion_rate'] for s in all_stats]
        if conv_rates:
            max_conv = max(conv_rates)
            min_conv = min(conv_rates)
            if max_conv > min_conv * 3:
                insights.append(f"Hay alta variación en tasas de conversión ({min_conv:.2f}% - {max_conv:.2f}%). Analiza las mejores prácticas de las descripciones top.")
        
        return insights






