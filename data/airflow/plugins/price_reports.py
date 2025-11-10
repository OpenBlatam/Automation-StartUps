"""
Sistema de Reportes Avanzados para Automatización de Precios

Genera reportes detallados y análisis de rendimiento
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class PriceReportGenerator:
    """Genera reportes avanzados de automatización de precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.reports_dir = Path(config.get('reports_dir', '/tmp/price_reports'))
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_execution_report(
        self,
        execution_date: datetime,
        extraction_result: Dict,
        analysis_result: Dict,
        publish_result: Dict,
        alerts: List[Dict],
        metrics: Dict
    ) -> Dict:
        """
        Genera reporte completo de ejecución
        
        Args:
            execution_date: Fecha de ejecución
            extraction_result: Resultado de extracción
            analysis_result: Resultado de análisis
            publish_result: Resultado de publicación
            alerts: Lista de alertas
            metrics: Métricas de rendimiento
        
        Returns:
            Reporte completo
        """
        report = {
            'execution_date': execution_date.isoformat(),
            'summary': self._generate_summary(
                extraction_result,
                analysis_result,
                publish_result,
                alerts
            ),
            'extraction': extraction_result,
            'analysis': analysis_result,
            'publication': publish_result,
            'alerts': alerts,
            'metrics': metrics,
            'recommendations': self._generate_recommendations(
                extraction_result,
                analysis_result,
                publish_result,
                alerts
            ),
            'generated_at': datetime.now().isoformat(),
        }
        
        # Guardar reporte
        self._save_report(report, execution_date)
        
        return report
    
    def _generate_summary(
        self,
        extraction_result: Dict,
        analysis_result: Dict,
        publish_result: Dict,
        alerts: List[Dict]
    ) -> Dict:
        """Genera resumen ejecutivo"""
        total_products = publish_result.get('total_products', 0)
        products_updated = publish_result.get('products_updated', 0)
        extraction_failures = extraction_result.get('failures', 0)
        critical_alerts = len([a for a in alerts if a.get('severity') == 'critical'])
        
        # Calcular estado general
        if critical_alerts > 0 or not publish_result.get('success', False):
            status = 'error'
        elif extraction_failures > 0 or len(alerts) > 0:
            status = 'warning'
        else:
            status = 'success'
        
        return {
            'status': status,
            'total_products': total_products,
            'products_updated': products_updated,
            'update_rate': (
                (products_updated / total_products * 100)
                if total_products > 0 else 0
            ),
            'extraction_failures': extraction_failures,
            'total_alerts': len(alerts),
            'critical_alerts': critical_alerts,
            'success': publish_result.get('success', False),
        }
    
    def _generate_recommendations(
        self,
        extraction_result: Dict,
        analysis_result: Dict,
        publish_result: Dict,
        alerts: List[Dict]
    ) -> List[str]:
        """Genera recomendaciones basadas en resultados"""
        recommendations = []
        
        # Recomendaciones por fallos de extracción
        failures = extraction_result.get('failures', 0)
        if failures > 0:
            recommendations.append(
                f"Revisar {failures} fuente(s) de extracción que fallaron. "
                "Considerar agregar circuit breakers o aumentar timeouts."
            )
        
        # Recomendaciones por alertas críticas
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        if critical_alerts:
            recommendations.append(
                f"Revisar {len(critical_alerts)} alerta(s) crítica(s). "
                "Algunos cambios de precio pueden ser demasiado extremos."
            )
        
        # Recomendaciones por tasa de actualización baja
        total_products = publish_result.get('total_products', 0)
        products_updated = publish_result.get('products_updated', 0)
        if total_products > 0:
            update_rate = products_updated / total_products
            if update_rate < 0.1:
                recommendations.append(
                    "Tasa de actualización muy baja. "
                    "Revisar estrategia de precios o fuentes de datos."
                )
        
        # Recomendaciones por éxito de publicación
        if not publish_result.get('success', False):
            recommendations.append(
                "La publicación falló. Revisar conectividad y configuración."
            )
        
        if not recommendations:
            recommendations.append(
                "Ejecución exitosa. No se requieren acciones inmediatas."
            )
        
        return recommendations
    
    def generate_trend_report(
        self,
        days: int = 30,
        history_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Genera reporte de tendencias
        
        Args:
            days: Días a analizar
            history_data: Datos históricos (opcional)
        
        Returns:
            Reporte de tendencias
        """
        # Si no hay datos, intentar leer del historial
        if not history_data:
            history_data = self._load_history_data(days)
        
        if not history_data:
            return {'message': 'No hay datos históricos disponibles'}
        
        # Análisis de tendencias
        price_changes = [
            d.get('price_change_percent', 0) for d in history_data
            if 'price_change_percent' in d
        ]
        
        increases = [p for p in price_changes if p > 0]
        decreases = [p for p in price_changes if p < 0]
        
        report = {
            'period_days': days,
            'total_changes': len(price_changes),
            'increases': len(increases),
            'decreases': len(decreases),
            'avg_change': (
                statistics.mean(price_changes) if price_changes else 0
            ),
            'avg_increase': (
                statistics.mean(increases) if increases else 0
            ),
            'avg_decrease': (
                statistics.mean(decreases) if decreases else 0
            ),
            'volatility': (
                statistics.stdev(price_changes) if len(price_changes) > 1 else 0
            ),
            'trend': self._calculate_trend(price_changes),
            'generated_at': datetime.now().isoformat(),
        }
        
        return report
    
    def _calculate_trend(self, changes: List[float]) -> str:
        """Calcula tendencia general"""
        if not changes:
            return 'unknown'
        
        avg = statistics.mean(changes)
        
        if avg > 2:
            return 'increasing'
        elif avg < -2:
            return 'decreasing'
        else:
            return 'stable'
    
    def _load_history_data(self, days: int) -> List[Dict]:
        """Carga datos históricos"""
        history_dir = Path(self.config.get('history_dir', '/tmp/price_history'))
        if not history_dir.exists():
            return []
        
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            history_file = history_dir / f"prices_{current_date.strftime('%Y-%m-%d')}.json"
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    data.extend(history.get('changes', []))
                except Exception as e:
                    logger.warning(f"Error leyendo {history_file}: {e}")
            
            current_date += timedelta(days=1)
        
        return data
    
    def _save_report(self, report: Dict, execution_date: datetime):
        """Guarda reporte en archivo"""
        try:
            date_str = execution_date.strftime('%Y-%m-%d')
            report_file = self.reports_dir / f"execution_report_{date_str}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte guardado: {report_file}")
        except Exception as e:
            logger.error(f"Error guardando reporte: {e}")
    
    def generate_comparison_report(
        self,
        current_prices: List[Dict],
        competitor_prices: List[Dict]
    ) -> Dict:
        """
        Genera reporte de comparación con competencia
        
        Args:
            current_prices: Precios actuales
            competitor_prices: Precios de competencia
        
        Returns:
            Reporte de comparación
        """
        # Crear diccionario de precios de competencia
        comp_dict = {
            p.get('product_name', '').lower(): p
            for p in competitor_prices
        }
        
        comparisons = []
        total_products = 0
        above_market = 0
        below_market = 0
        in_market = 0
        
        for current in current_prices:
            product_name = current.get('product_name', '').lower()
            current_price = current.get('current_price', 0)
            
            if not product_name or current_price <= 0:
                continue
            
            total_products += 1
            competitor = comp_dict.get(product_name)
            
            if competitor:
                comp_price = competitor.get('avg_competitor_price', 0)
                if comp_price > 0:
                    diff_percent = (
                        (current_price - comp_price) / comp_price * 100
                    )
                    
                    if diff_percent > 5:
                        position = 'above_market'
                        above_market += 1
                    elif diff_percent < -5:
                        position = 'below_market'
                        below_market += 1
                    else:
                        position = 'in_market'
                        in_market += 1
                    
                    comparisons.append({
                        'product_name': current.get('product_name'),
                        'current_price': current_price,
                        'competitor_price': comp_price,
                        'difference_percent': round(diff_percent, 2),
                        'position': position,
                    })
        
        return {
            'total_products': total_products,
            'products_with_competition': len(comparisons),
            'above_market': above_market,
            'below_market': below_market,
            'in_market': in_market,
            'comparisons': comparisons,
            'generated_at': datetime.now().isoformat(),
        }








