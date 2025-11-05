from datetime import datetime, timedelta
from flask import current_app, make_response
from app import db
from models import Product, SalesRecord, InventoryRecord, Alert, ReorderRecommendation
from services.kpi_service import kpi_service
from services.advanced_analytics_service import advanced_analytics_service
import pandas as pd
import io
import json
import logging
from typing import Dict, List
import zipfile

class DataExportService:
    """Servicio de exportación de datos avanzado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_inventory_report(self, format: str = 'excel', filters: Dict = None) -> bytes:
        """Exporta reporte completo de inventario"""
        try:
            filters = filters or {}
            
            # Obtener datos de inventario
            products = Product.query.all()
            inventory_data = []
            
            for product in products:
                current_stock = self._get_current_stock(product.id)
                
                # Aplicar filtros
                if filters.get('category') and product.category != filters['category']:
                    continue
                
                if filters.get('min_stock') and current_stock >= filters['min_stock']:
                    continue
                
                if filters.get('max_stock') and current_stock <= filters['max_stock']:
                    continue
                
                inventory_data.append({
                    'ID': product.id,
                    'Nombre': product.name,
                    'SKU': product.sku,
                    'Categoría': product.category,
                    'Stock Actual': current_stock,
                    'Stock Mínimo': product.min_stock_level,
                    'Stock Máximo': product.max_stock_level,
                    'Punto de Reorden': product.reorder_point,
                    'Precio Unitario': product.unit_price,
                    'Precio de Costo': product.cost_price,
                    'Valor Total': current_stock * product.unit_price,
                    'Proveedor': product.supplier.name if product.supplier else 'No asignado',
                    'Estado': 'Crítico' if current_stock <= product.min_stock_level else 'Normal'
                })
            
            df = pd.DataFrame(inventory_data)
            
            if format.lower() == 'excel':
                return self._export_to_excel(df, 'Reporte_Inventario')
            elif format.lower() == 'csv':
                return self._export_to_csv(df, 'Reporte_Inventario')
            elif format.lower() == 'json':
                return self._export_to_json(df, 'Reporte_Inventario')
            else:
                raise ValueError(f'Formato no soportado: {format}')
                
        except Exception as e:
            self.logger.error(f'Error exportando reporte de inventario: {str(e)}')
            raise
    
    def export_sales_report(self, start_date: datetime, end_date: datetime, format: str = 'excel') -> bytes:
        """Exporta reporte de ventas"""
        try:
            # Obtener datos de ventas
            sales_data = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            sales_list = []
            for sale in sales_data:
                sales_list.append({
                    'ID': sale.id,
                    'Fecha': sale.sale_date.strftime('%Y-%m-%d'),
                    'Producto': sale.product.name,
                    'SKU': sale.product.sku,
                    'Categoría': sale.product.category,
                    'Cantidad': sale.quantity_sold,
                    'Precio Unitario': sale.unit_price,
                    'Total': sale.total_amount,
                    'Cliente': sale.customer.name if sale.customer else 'No especificado'
                })
            
            df = pd.DataFrame(sales_list)
            
            # Agregar resumen
            summary_data = {
                'Total Ventas': len(sales_data),
                'Ingresos Totales': df['Total'].sum(),
                'Cantidad Total': df['Cantidad'].sum(),
                'Ticket Promedio': df['Total'].mean(),
                'Período': f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}"
            }
            
            if format.lower() == 'excel':
                return self._export_sales_to_excel(df, summary_data, 'Reporte_Ventas')
            else:
                return self._export_to_csv(df, 'Reporte_Ventas')
                
        except Exception as e:
            self.logger.error(f'Error exportando reporte de ventas: {str(e)}')
            raise
    
    def export_kpis_report(self, format: str = 'excel') -> bytes:
        """Exporta reporte de KPIs"""
        try:
            kpis = kpi_service.calculate_all_kpis()
            
            # Preparar datos para exportación
            kpi_data = []
            
            for category, metrics in kpis.items():
                for metric_name, value in metrics.items():
                    kpi_data.append({
                        'Categoría': category.title(),
                        'Métrica': metric_name.replace('_', ' ').title(),
                        'Valor': value,
                        'Fecha': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            df = pd.DataFrame(kpi_data)
            
            if format.lower() == 'excel':
                return self._export_to_excel(df, 'Reporte_KPIs')
            else:
                return self._export_to_csv(df, 'Reporte_KPIs')
                
        except Exception as e:
            self.logger.error(f'Error exportando reporte de KPIs: {str(e)}')
            raise
    
    def export_analytics_report(self, format: str = 'excel') -> bytes:
        """Exporta reporte de análisis avanzado"""
        try:
            analytics = advanced_analytics_service.analyze_product_performance()
            
            if 'error' in analytics:
                raise Exception(analytics['error'])
            
            # Crear múltiples hojas para análisis completo
            if format.lower() == 'excel':
                return self._export_analytics_to_excel(analytics)
            else:
                # Para otros formatos, exportar como JSON
                return self._export_to_json(analytics, 'Analisis_Avanzado')
                
        except Exception as e:
            self.logger.error(f'Error exportando reporte de análisis: {str(e)}')
            raise
    
    def export_complete_backup(self) -> bytes:
        """Exporta backup completo del sistema"""
        try:
            # Crear archivo ZIP en memoria
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Exportar inventario
                inventory_data = self.export_inventory_report('csv')
                zip_file.writestr('inventory.csv', inventory_data)
                
                # Exportar ventas (últimos 90 días)
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=90)
                sales_data = self.export_sales_report(start_date, end_date, 'csv')
                zip_file.writestr('sales.csv', sales_data)
                
                # Exportar KPIs
                kpis_data = self.export_kpis_report('csv')
                zip_file.writestr('kpis.csv', kpis_data)
                
                # Exportar alertas
                alerts_data = self._export_alerts_to_csv()
                zip_file.writestr('alerts.csv', alerts_data)
                
                # Exportar recomendaciones
                recommendations_data = self._export_recommendations_to_csv()
                zip_file.writestr('recommendations.csv', recommendations_data)
                
                # Crear archivo de metadatos
                metadata = {
                    'export_date': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'description': 'Backup completo del sistema de inventario',
                    'files': ['inventory.csv', 'sales.csv', 'kpis.csv', 'alerts.csv', 'recommendations.csv']
                }
                zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f'Error creando backup completo: {str(e)}')
            raise
    
    def _export_to_excel(self, df: pd.DataFrame, filename: str) -> bytes:
        """Exporta DataFrame a Excel"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
        output.seek(0)
        return output.getvalue()
    
    def _export_to_csv(self, df: pd.DataFrame, filename: str) -> bytes:
        """Exporta DataFrame a CSV"""
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        return csv_buffer.getvalue().encode('utf-8')
    
    def _export_to_json(self, data: Dict, filename: str) -> bytes:
        """Exporta datos a JSON"""
        return json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
    
    def _export_sales_to_excel(self, df: pd.DataFrame, summary: Dict, filename: str) -> bytes:
        """Exporta ventas a Excel con resumen"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ventas', index=False)
            
            # Crear hoja de resumen
            summary_df = pd.DataFrame(list(summary.items()), columns=['Métrica', 'Valor'])
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def _export_analytics_to_excel(self, analytics: Dict) -> bytes:
        """Exporta análisis avanzado a Excel"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Análisis ABC
            if 'abc_analysis' in analytics and 'products' in analytics['abc_analysis']:
                abc_df = pd.DataFrame(analytics['abc_analysis']['products'])
                abc_df.to_excel(writer, sheet_name='Análisis ABC', index=False)
            
            # Estacionalidad
            if 'seasonality' in analytics:
                if 'monthly' in analytics['seasonality']:
                    monthly_df = pd.DataFrame(analytics['seasonality']['monthly'])
                    monthly_df.to_excel(writer, sheet_name='Estacionalidad Mensual', index=False)
            
            # Clustering
            if 'clusters' in analytics and 'products' in analytics['clusters']:
                clusters_df = pd.DataFrame(analytics['clusters']['products'])
                clusters_df.to_excel(writer, sheet_name='Clustering', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def _export_alerts_to_csv(self) -> bytes:
        """Exporta alertas a CSV"""
        alerts = Alert.query.all()
        alerts_data = []
        
        for alert in alerts:
            alerts_data.append({
                'ID': alert.id,
                'Producto': alert.product.name,
                'SKU': alert.product.sku,
                'Tipo': alert.alert_type,
                'Mensaje': alert.message,
                'Severidad': alert.severity,
                'Resuelto': alert.is_resolved,
                'Fecha Creación': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Fecha Resolución': alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if alert.resolved_at else ''
            })
        
        df = pd.DataFrame(alerts_data)
        return self._export_to_csv(df, 'Alertas')
    
    def _export_recommendations_to_csv(self) -> bytes:
        """Exporta recomendaciones a CSV"""
        recommendations = ReorderRecommendation.query.all()
        rec_data = []
        
        for rec in recommendations:
            rec_data.append({
                'ID': rec.id,
                'Producto': rec.product.name,
                'SKU': rec.product.sku,
                'Cantidad Recomendada': rec.recommended_quantity,
                'Razón': rec.reason,
                'Urgencia': rec.urgency,
                'Costo Estimado': rec.estimated_cost,
                'Procesado': rec.is_processed,
                'Fecha Creación': rec.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(rec_data)
        return self._export_to_csv(df, 'Recomendaciones')
    
    def _get_current_stock(self, product_id: int) -> int:
        """Obtiene stock actual de un producto"""
        try:
            entries = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'in'
            ).scalar() or 0
            
            exits = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'out'
            ).scalar() or 0
            
            adjustments = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'adjustment'
            ).scalar() or 0
            
            return entries - exits + adjustments
            
        except Exception as e:
            self.logger.error(f'Error calculando stock: {str(e)}')
            return 0

# Instancia global del servicio de exportación
data_export_service = DataExportService()



