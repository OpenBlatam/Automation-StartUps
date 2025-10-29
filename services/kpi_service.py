from datetime import datetime, timedelta
from app import db
from models import Product, InventoryRecord, SalesRecord, Alert, ReorderRecommendation, KPIMetric
from services.alert_service import alert_system
from services.replenishment_service import replenishment_service
import logging
from typing import Dict, List, Tuple
import pandas as pd

class KPIService:
    """Servicio para calcular y gestionar KPIs del sistema de inventario"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_kpis(self) -> Dict:
        """Calcula todos los KPIs principales del sistema"""
        try:
            kpis = {}
            
            # KPIs de Inventario
            kpis['inventory'] = self._calculate_inventory_kpis()
            
            # KPIs de Ventas
            kpis['sales'] = self._calculate_sales_kpis()
            
            # KPIs Financieros
            kpis['financial'] = self._calculate_financial_kpis()
            
            # KPIs Operacionales
            kpis['operational'] = self._calculate_operational_kpis()
            
            # KPIs de Alertas
            kpis['alerts'] = self._calculate_alert_kpis()
            
            # KPIs de Reposición
            kpis['replenishment'] = self._calculate_replenishment_kpis()
            
            # Guardar KPIs en la base de datos
            self._save_kpis(kpis)
            
            return kpis
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs: {str(e)}')
            return {}
    
    def _calculate_inventory_kpis(self) -> Dict:
        """Calcula KPIs relacionados con inventario"""
        try:
            products = Product.query.all()
            total_products = len(products)
            
            if total_products == 0:
                return self._empty_kpi_dict('inventory')
            
            # Stock total valorizado
            total_inventory_value = 0
            total_inventory_cost = 0
            low_stock_products = 0
            out_of_stock_products = 0
            
            for product in products:
                current_stock = alert_system.get_current_stock(product.id)
                inventory_value = current_stock * product.unit_price
                inventory_cost = current_stock * product.cost_price
                
                total_inventory_value += inventory_value
                total_inventory_cost += inventory_cost
                
                if current_stock <= product.min_stock_level:
                    low_stock_products += 1
                
                if current_stock <= 0:
                    out_of_stock_products += 1
            
            # Rotación de inventario (simplificada)
            inventory_turnover = self._calculate_inventory_turnover()
            
            # Precisión de inventario (basada en ajustes)
            inventory_accuracy = self._calculate_inventory_accuracy()
            
            return {
                'total_products': total_products,
                'total_inventory_value': round(total_inventory_value, 2),
                'total_inventory_cost': round(total_inventory_cost, 2),
                'low_stock_products': low_stock_products,
                'out_of_stock_products': out_of_stock_products,
                'inventory_turnover': round(inventory_turnover, 2),
                'inventory_accuracy': round(inventory_accuracy, 2),
                'low_stock_percentage': round((low_stock_products / total_products) * 100, 2),
                'out_of_stock_percentage': round((out_of_stock_products / total_products) * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs de inventario: {str(e)}')
            return self._empty_kpi_dict('inventory')
    
    def _calculate_sales_kpis(self) -> Dict:
        """Calcula KPIs relacionados con ventas"""
        try:
            # Ventas de los últimos 30 días
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sales_records = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            if not sales_records:
                return self._empty_kpi_dict('sales')
            
            # Métricas básicas
            total_sales_volume = sum(record.quantity_sold for record in sales_records)
            total_sales_revenue = sum(record.total_amount for record in sales_records)
            avg_order_value = total_sales_revenue / len(sales_records) if sales_records else 0
            
            # Productos más vendidos
            product_sales = {}
            for record in sales_records:
                product_id = record.product_id
                if product_id not in product_sales:
                    product_sales[product_id] = {'quantity': 0, 'revenue': 0, 'name': record.product.name}
                product_sales[product_id]['quantity'] += record.quantity_sold
                product_sales[product_id]['revenue'] += record.total_amount
            
            # Top 5 productos por volumen
            top_products_volume = sorted(
                product_sales.items(), 
                key=lambda x: x[1]['quantity'], 
                reverse=True
            )[:5]
            
            # Top 5 productos por ingresos
            top_products_revenue = sorted(
                product_sales.items(), 
                key=lambda x: x[1]['revenue'], 
                reverse=True
            )[:5]
            
            # Crecimiento de ventas (comparar con período anterior)
            previous_period_start = start_date - timedelta(days=30)
            previous_sales = SalesRecord.query.filter(
                SalesRecord.sale_date >= previous_period_start,
                SalesRecord.sale_date < start_date
            ).all()
            
            previous_revenue = sum(record.total_amount for record in previous_sales)
            sales_growth = ((total_sales_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            return {
                'total_sales_volume': total_sales_volume,
                'total_sales_revenue': round(total_sales_revenue, 2),
                'avg_order_value': round(avg_order_value, 2),
                'total_orders': len(sales_records),
                'sales_growth_percentage': round(sales_growth, 2),
                'top_products_volume': [
                    {'product_name': data['name'], 'quantity': data['quantity']} 
                    for _, data in top_products_volume
                ],
                'top_products_revenue': [
                    {'product_name': data['name'], 'revenue': round(data['revenue'], 2)} 
                    for _, data in top_products_revenue
                ]
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs de ventas: {str(e)}')
            return self._empty_kpi_dict('sales')
    
    def _calculate_financial_kpis(self) -> Dict:
        """Calcula KPIs financieros"""
        try:
            # Margen de beneficio
            products = Product.query.all()
            total_cost = 0
            total_value = 0
            
            for product in products:
                current_stock = alert_system.get_current_stock(product.id)
                total_cost += current_stock * product.cost_price
                total_value += current_stock * product.unit_price
            
            gross_margin = ((total_value - total_cost) / total_value * 100) if total_value > 0 else 0
            
            # ROI del inventario (simplificado)
            inventory_roi = self._calculate_inventory_roi()
            
            # Costo de almacenamiento (estimado)
            storage_cost = total_value * 0.02  # 2% del valor del inventario
            
            return {
                'gross_margin_percentage': round(gross_margin, 2),
                'inventory_roi': round(inventory_roi, 2),
                'total_inventory_value': round(total_value, 2),
                'total_inventory_cost': round(total_cost, 2),
                'estimated_storage_cost': round(storage_cost, 2),
                'profit_potential': round(total_value - total_cost, 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs financieros: {str(e)}')
            return self._empty_kpi_dict('financial')
    
    def _calculate_operational_kpis(self) -> Dict:
        """Calcula KPIs operacionales"""
        try:
            # Tiempo promedio de respuesta a alertas
            resolved_alerts = Alert.query.filter(Alert.is_resolved == True).all()
            
            if resolved_alerts:
                response_times = []
                for alert in resolved_alerts:
                    if alert.resolved_at:
                        response_time = (alert.resolved_at - alert.created_at).total_seconds() / 3600  # horas
                        response_times.append(response_time)
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            else:
                avg_response_time = 0
            
            # Eficiencia de reposición
            total_recommendations = ReorderRecommendation.query.count()
            processed_recommendations = ReorderRecommendation.query.filter(
                ReorderRecommendation.is_processed == True
            ).count()
            
            replenishment_efficiency = (processed_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
            
            # Precisión de predicciones
            forecast_accuracy = self._calculate_forecast_accuracy()
            
            return {
                'avg_alert_response_time_hours': round(avg_response_time, 2),
                'replenishment_efficiency_percentage': round(replenishment_efficiency, 2),
                'forecast_accuracy_percentage': round(forecast_accuracy, 2),
                'total_recommendations': total_recommendations,
                'processed_recommendations': processed_recommendations
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs operacionales: {str(e)}')
            return self._empty_kpi_dict('operational')
    
    def _calculate_alert_kpis(self) -> Dict:
        """Calcula KPIs relacionados con alertas"""
        try:
            alert_stats = alert_system.get_alert_statistics()
            
            # Tiempo promedio de resolución por tipo
            alert_types = ['low_stock', 'out_of_stock', 'reorder']
            avg_resolution_times = {}
            
            for alert_type in alert_types:
                alerts = Alert.query.filter(
                    Alert.alert_type == alert_type,
                    Alert.is_resolved == True
                ).all()
                
                if alerts:
                    resolution_times = [
                        (alert.resolved_at - alert.created_at).total_seconds() / 3600
                        for alert in alerts if alert.resolved_at
                    ]
                    avg_resolution_times[alert_type] = round(sum(resolution_times) / len(resolution_times), 2)
                else:
                    avg_resolution_times[alert_type] = 0
            
            return {
                **alert_stats,
                'avg_resolution_times': avg_resolution_times
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs de alertas: {str(e)}')
            return self._empty_kpi_dict('alerts')
    
    def _calculate_replenishment_kpis(self) -> Dict:
        """Calcula KPIs relacionados con reposición"""
        try:
            replenishment_summary = replenishment_service.get_reorder_summary()
            
            # Efectividad de las recomendaciones
            recommendations = ReorderRecommendation.query.all()
            
            if recommendations:
                avg_recommended_quantity = sum(r.recommended_quantity for r in recommendations) / len(recommendations)
                avg_estimated_cost = sum(r.estimated_cost for r in recommendations) / len(recommendations)
            else:
                avg_recommended_quantity = 0
                avg_estimated_cost = 0
            
            return {
                **replenishment_summary,
                'avg_recommended_quantity': round(avg_recommended_quantity, 2),
                'avg_estimated_cost': round(avg_estimated_cost, 2)
            }
            
        except Exception as e:
            self.logger.error(f'Error calculando KPIs de reposición: {str(e)}')
            return self._empty_kpi_dict('replenishment')
    
    def _calculate_inventory_turnover(self) -> float:
        """Calcula rotación de inventario"""
        try:
            # Ventas de los últimos 30 días
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sales_records = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            if not sales_records:
                return 0
            
            # Calcular costo de ventas
            cost_of_sales = sum(record.quantity_sold * record.product.cost_price for record in sales_records)
            
            # Calcular inventario promedio
            products = Product.query.all()
            avg_inventory_cost = sum(
                alert_system.get_current_stock(p.id) * p.cost_price for p in products
            ) / len(products) if products else 0
            
            # Rotación = Costo de ventas / Inventario promedio
            turnover = cost_of_sales / avg_inventory_cost if avg_inventory_cost > 0 else 0
            
            return turnover
            
        except Exception as e:
            self.logger.error(f'Error calculando rotación de inventario: {str(e)}')
            return 0
    
    def _calculate_inventory_accuracy(self) -> float:
        """Calcula precisión del inventario basada en ajustes"""
        try:
            # Contar ajustes de inventario
            adjustments = InventoryRecord.query.filter(
                InventoryRecord.movement_type == 'adjustment'
            ).count()
            
            # Contar total de movimientos
            total_movements = InventoryRecord.query.count()
            
            # Precisión = (Total movimientos - Ajustes) / Total movimientos
            accuracy = ((total_movements - adjustments) / total_movements * 100) if total_movements > 0 else 100
            
            return accuracy
            
        except Exception as e:
            self.logger.error(f'Error calculando precisión de inventario: {str(e)}')
            return 100
    
    def _calculate_inventory_roi(self) -> float:
        """Calcula ROI del inventario"""
        try:
            # Ingresos de los últimos 30 días
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sales_records = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            if not sales_records:
                return 0
            
            total_revenue = sum(record.total_amount for record in sales_records)
            total_cost = sum(record.quantity_sold * record.product.cost_price for record in sales_records)
            
            # Calcular valor del inventario
            products = Product.query.all()
            inventory_value = sum(
                alert_system.get_current_stock(p.id) * p.cost_price for p in products
            )
            
            # ROI = (Ingresos - Costos) / Valor del inventario
            roi = ((total_revenue - total_cost) / inventory_value * 100) if inventory_value > 0 else 0
            
            return roi
            
        except Exception as e:
            self.logger.error(f'Error calculando ROI: {str(e)}')
            return 0
    
    def _calculate_forecast_accuracy(self) -> float:
        """Calcula precisión de las predicciones"""
        try:
            # Esta es una implementación simplificada
            # En un sistema real, se compararían predicciones con ventas reales
            
            # Por ahora, retornamos un valor estimado basado en la cantidad de predicciones
            forecasts_count = db.session.query(db.func.count()).select_from(
                db.text("demand_forecasts")
            ).scalar() or 0
            
            if forecasts_count > 10:
                return 85.0  # Alta precisión estimada
            elif forecasts_count > 5:
                return 75.0  # Precisión media
            else:
                return 65.0  # Precisión baja por falta de datos
                
        except Exception as e:
            self.logger.error(f'Error calculando precisión de predicciones: {str(e)}')
            return 0
    
    def _save_kpis(self, kpis: Dict):
        """Guarda KPIs en la base de datos"""
        try:
            # Eliminar KPIs anteriores del día actual
            today = datetime.utcnow().date()
            KPIMetric.query.filter(
                db.func.date(KPIMetric.created_at) == today
            ).delete()
            
            # Guardar nuevos KPIs
            for category, metrics in kpis.items():
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        kpi = KPIMetric(
                            metric_name=f"{category}_{metric_name}",
                            metric_value=metric_value,
                            category=category,
                            period_start=today,
                            period_end=today
                        )
                        db.session.add(kpi)
            
            db.session.commit()
            self.logger.info('KPIs guardados exitosamente')
            
        except Exception as e:
            self.logger.error(f'Error guardando KPIs: {str(e)}')
            db.session.rollback()
    
    def _empty_kpi_dict(self, category: str) -> Dict:
        """Retorna diccionario vacío para una categoría de KPI"""
        return {
            f'{category}_error': 'No hay datos suficientes para calcular KPIs'
        }
    
    def get_kpi_trends(self, days: int = 30) -> Dict:
        """Obtiene tendencias de KPIs en el tiempo"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            kpis = KPIMetric.query.filter(
                KPIMetric.period_start >= start_date,
                KPIMetric.period_start <= end_date
            ).order_by(KPIMetric.created_at).all()
            
            trends = {}
            for kpi in kpis:
                if kpi.metric_name not in trends:
                    trends[kpi.metric_name] = []
                trends[kpi.metric_name].append({
                    'date': kpi.period_start.isoformat(),
                    'value': kpi.metric_value
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f'Error obteniendo tendencias de KPIs: {str(e)}')
            return {}

# Instancia global del servicio de KPIs
kpi_service = KPIService()



