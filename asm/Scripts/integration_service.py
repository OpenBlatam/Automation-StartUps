from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Supplier
import requests
import json
import logging
from typing import Dict, List, Optional
import schedule
import time
import threading
from dataclasses import dataclass
import os
import zipfile
import shutil

@dataclass
class APIIntegration:
    """Configuración de integración con API externa"""
    name: str
    base_url: str
    api_key: str
    endpoints: Dict[str, str]
    headers: Dict[str, str]
    rate_limit: int = 100  # requests per hour
    last_sync: Optional[datetime] = None

class ExternalIntegrationService:
    """Servicio de integración con APIs externas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integrations = {}
        self.sync_jobs = {}
        self.is_running = False
        
        # Configurar integraciones por defecto
        self._setup_default_integrations()
    
    def _setup_default_integrations(self):
        """Configura integraciones por defecto"""
        # Integración con API de precios de mercado
        self.integrations['market_prices'] = APIIntegration(
            name='Market Prices API',
            base_url='https://api.marketdata.com',
            api_key='demo_key',
            endpoints={
                'prices': '/v1/prices',
                'trends': '/v1/trends',
                'forecasts': '/v1/forecasts'
            },
            headers={
                'Authorization': 'Bearer demo_key',
                'Content-Type': 'application/json'
            }
        )
        
        # Integración con API de proveedores
        self.integrations['supplier_api'] = APIIntegration(
            name='Supplier Management API',
            base_url='https://api.suppliers.com',
            api_key='demo_key',
            endpoints={
                'products': '/v1/products',
                'prices': '/v1/prices',
                'availability': '/v1/availability',
                'orders': '/v1/orders'
            },
            headers={
                'Authorization': 'Bearer demo_key',
                'Content-Type': 'application/json'
            }
        )
        
        # Integración con API de análisis de mercado
        self.integrations['market_analytics'] = APIIntegration(
            name='Market Analytics API',
            base_url='https://api.analytics.com',
            api_key='demo_key',
            endpoints={
                'demand_forecast': '/v1/demand-forecast',
                'competitor_analysis': '/v1/competitor-analysis',
                'trend_analysis': '/v1/trend-analysis'
            },
            headers={
                'Authorization': 'Bearer demo_key',
                'Content-Type': 'application/json'
            }
        )
    
    def sync_market_prices(self) -> Dict:
        """Sincroniza precios de mercado"""
        try:
            integration = self.integrations['market_prices']
            
            # Simular datos de precios de mercado
            market_data = {
                'products': [
                    {
                        'sku': 'PROD001',
                        'market_price': 25.99,
                        'trend': 'up',
                        'change_percent': 2.5,
                        'last_updated': datetime.utcnow().isoformat()
                    },
                    {
                        'sku': 'PROD002',
                        'market_price': 45.50,
                        'trend': 'down',
                        'change_percent': -1.2,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                ]
            }
            
            # Actualizar productos con precios de mercado
            updated_count = 0
            for product_data in market_data['products']:
                product = Product.query.filter_by(sku=product_data['sku']).first()
                if product:
                    # Guardar precio de mercado como atributo adicional
                    if not hasattr(product, 'market_price'):
                        # En un sistema real, esto sería una columna en la BD
                        pass
                    updated_count += 1
            
            integration.last_sync = datetime.utcnow()
            
            return {
                'success': True,
                'updated_products': updated_count,
                'sync_time': integration.last_sync.isoformat(),
                'data': market_data
            }
            
        except Exception as e:
            self.logger.error(f'Error sincronizando precios de mercado: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def sync_supplier_data(self) -> Dict:
        """Sincroniza datos de proveedores"""
        try:
            integration = self.integrations['supplier_api']
            
            # Simular datos de proveedores
            supplier_data = {
                'products': [
                    {
                        'sku': 'PROD001',
                        'supplier_price': 18.50,
                        'availability': 'in_stock',
                        'lead_time_days': 5,
                        'minimum_order': 100,
                        'supplier_id': 'SUP001'
                    },
                    {
                        'sku': 'PROD002',
                        'supplier_price': 32.75,
                        'availability': 'limited',
                        'lead_time_days': 7,
                        'minimum_order': 50,
                        'supplier_id': 'SUP002'
                    }
                ]
            }
            
            # Actualizar productos con datos de proveedores
            updated_count = 0
            for product_data in supplier_data['products']:
                product = Product.query.filter_by(sku=product_data['sku']).first()
                if product:
                    # Actualizar precio de costo si es mejor
                    if product_data['supplier_price'] < product.cost_price:
                        product.cost_price = product_data['supplier_price']
                        updated_count += 1
            
            db.session.commit()
            integration.last_sync = datetime.utcnow()
            
            return {
                'success': True,
                'updated_products': updated_count,
                'sync_time': integration.last_sync.isoformat(),
                'data': supplier_data
            }
            
        except Exception as e:
            self.logger.error(f'Error sincronizando datos de proveedores: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_market_forecast(self, product_sku: str) -> Dict:
        """Obtiene pronóstico de mercado para un producto"""
        try:
            integration = self.integrations['market_analytics']
            
            # Simular pronóstico de mercado
            forecast_data = {
                'product_sku': product_sku,
                'forecast_period': '30_days',
                'demand_forecast': {
                    'high': 150,
                    'medium': 120,
                    'low': 90
                },
                'price_forecast': {
                    'trend': 'stable',
                    'expected_change': 0.5,
                    'confidence': 0.85
                },
                'market_conditions': {
                    'competition_level': 'medium',
                    'seasonality': 'normal',
                    'external_factors': ['economic_stability', 'supply_chain_normal']
                },
                'recommendations': [
                    'Maintain current pricing strategy',
                    'Monitor competitor pricing weekly',
                    'Consider promotional pricing for slow-moving items'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'forecast': forecast_data
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo pronóstico de mercado: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_competitor_analysis(self, product_category: str) -> Dict:
        """Obtiene análisis de competidores"""
        try:
            integration = self.integrations['market_analytics']
            
            # Simular análisis de competidores
            competitor_data = {
                'category': product_category,
                'competitors': [
                    {
                        'name': 'Competitor A',
                        'market_share': 0.35,
                        'avg_price': 28.50,
                        'strengths': ['Brand recognition', 'Distribution network'],
                        'weaknesses': ['Higher prices', 'Limited innovation']
                    },
                    {
                        'name': 'Competitor B',
                        'market_share': 0.25,
                        'avg_price': 24.75,
                        'strengths': ['Price competitiveness', 'Product variety'],
                        'weaknesses': ['Quality issues', 'Customer service']
                    }
                ],
                'market_insights': {
                    'total_market_size': 1000000,
                    'growth_rate': 0.08,
                    'price_sensitivity': 'high',
                    'key_drivers': ['Price', 'Quality', 'Availability']
                },
                'recommendations': [
                    'Focus on price competitiveness',
                    'Improve product quality',
                    'Enhance customer service',
                    'Develop unique value propositions'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'analysis': competitor_data
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo análisis de competidores: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def start_auto_sync(self):
        """Inicia sincronización automática"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Programar trabajos de sincronización
        schedule.every(1).hours.do(self.sync_market_prices)
        schedule.every(2).hours.do(self.sync_supplier_data)
        schedule.every(6).hours.do(self._cleanup_old_data)
        
        # Ejecutar en hilo separado
        sync_thread = threading.Thread(target=self._sync_worker)
        sync_thread.daemon = True
        sync_thread.start()
        
        self.logger.info('Sincronización automática iniciada')
    
    def stop_auto_sync(self):
        """Detiene sincronización automática"""
        self.is_running = False
        schedule.clear()
        self.logger.info('Sincronización automática detenida')
    
    def _sync_worker(self):
        """Worker para sincronización automática"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                self.logger.error(f'Error en worker de sincronización: {str(e)}')
                time.sleep(300)  # Esperar 5 minutos en caso de error
    
    def _cleanup_old_data(self):
        """Limpia datos antiguos"""
        try:
            # Limpiar registros de ventas antiguos (más de 2 años)
            cutoff_date = datetime.utcnow() - timedelta(days=730)
            old_sales = SalesRecord.query.filter(SalesRecord.sale_date < cutoff_date).all()
            
            for sale in old_sales:
                db.session.delete(sale)
            
            db.session.commit()
            self.logger.info(f'Limpiados {len(old_sales)} registros de ventas antiguos')
            
        except Exception as e:
            self.logger.error(f'Error limpiando datos antiguos: {str(e)}')
    
    def get_integration_status(self) -> Dict:
        """Obtiene estado de las integraciones"""
        status = {}
        
        for name, integration in self.integrations.items():
            status[name] = {
                'name': integration.name,
                'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
                'status': 'active' if integration.last_sync else 'inactive',
                'rate_limit': integration.rate_limit
            }
        
        return {
            'integrations': status,
            'auto_sync_running': self.is_running,
            'total_integrations': len(self.integrations)
        }

class BackupService:
    """Servicio de respaldos automáticos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = 'backups'
        self.retention_days = 30
        
        # Crear directorio de respaldos si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_full_backup(self) -> Dict:
        """Crea respaldo completo del sistema"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_full_{timestamp}.zip'
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Respaldar archivos de configuración
                config_files = ['app.py', 'models.py', 'requirements.txt']
                for file in config_files:
                    if os.path.exists(file):
                        zipf.write(file, f'config/{file}')
                
                # Respaldar servicios
                if os.path.exists('services'):
                    for root, dirs, files in os.walk('services'):
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path, file_path)
                
                # Respaldar rutas
                if os.path.exists('routes'):
                    for root, dirs, files in os.walk('routes'):
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path, file_path)
                
                # Respaldar templates
                if os.path.exists('templates'):
                    for root, dirs, files in os.walk('templates'):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                
                # Respaldar archivos estáticos
                if os.path.exists('static'):
                    for root, dirs, files in os.walk('static'):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file_path)
                
                # Crear archivo de metadatos
                metadata = {
                    'backup_type': 'full',
                    'created_at': datetime.utcnow().isoformat(),
                    'version': '3.0',
                    'description': 'Respaldo completo del sistema de inventario',
                    'files_included': len(zipf.namelist())
                }
                
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(backup_path)
            
            return {
                'success': True,
                'backup_file': backup_filename,
                'backup_path': backup_path,
                'file_size': file_size,
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f'Error creando respaldo completo: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def create_data_backup(self) -> Dict:
        """Crea respaldo solo de datos"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_data_{timestamp}.json'
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Exportar datos de la base de datos
            data = {
                'products': [],
                'sales': [],
                'inventory': [],
                'alerts': [],
                'suppliers': [],
                'backup_info': {
                    'created_at': datetime.utcnow().isoformat(),
                    'backup_type': 'data_only',
                    'version': '3.0'
                }
            }
            
            # Exportar productos
            products = Product.query.all()
            for product in products:
                data['products'].append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'description': product.description,
                    'category': product.category,
                    'unit_price': float(product.unit_price),
                    'cost_price': float(product.cost_price),
                    'min_stock_level': product.min_stock_level,
                    'max_stock_level': product.max_stock_level,
                    'reorder_point': product.reorder_point,
                    'supplier_id': product.supplier_id,
                    'created_at': product.created_at.isoformat() if product.created_at else None
                })
            
            # Exportar ventas (últimos 90 días)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
            sales = SalesRecord.query.filter(
                SalesRecord.sale_date >= start_date,
                SalesRecord.sale_date <= end_date
            ).all()
            
            for sale in sales:
                data['sales'].append({
                    'id': sale.id,
                    'product_id': sale.product_id,
                    'quantity_sold': sale.quantity_sold,
                    'unit_price': float(sale.unit_price),
                    'total_amount': float(sale.total_amount),
                    'sale_date': sale.sale_date.isoformat(),
                    'customer_id': sale.customer_id
                })
            
            # Guardar datos
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Obtener tamaño del archivo
            file_size = os.path.getsize(backup_path)
            
            return {
                'success': True,
                'backup_file': backup_filename,
                'backup_path': backup_path,
                'file_size': file_size,
                'records_backed_up': {
                    'products': len(data['products']),
                    'sales': len(data['sales'])
                },
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f'Error creando respaldo de datos: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def restore_from_backup(self, backup_file: str) -> Dict:
        """Restaura sistema desde respaldo"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            if not os.path.exists(backup_path):
                return {'success': False, 'error': 'Archivo de respaldo no encontrado'}
            
            if backup_file.endswith('.json'):
                # Restaurar desde respaldo de datos
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restaurar productos
                restored_products = 0
                for product_data in data['products']:
                    existing_product = Product.query.filter_by(sku=product_data['sku']).first()
                    if not existing_product:
                        product = Product(
                            name=product_data['name'],
                            sku=product_data['sku'],
                            description=product_data['description'],
                            category=product_data['category'],
                            unit_price=product_data['unit_price'],
                            cost_price=product_data['cost_price'],
                            min_stock_level=product_data['min_stock_level'],
                            max_stock_level=product_data['max_stock_level'],
                            reorder_point=product_data['reorder_point'],
                            supplier_id=product_data['supplier_id']
                        )
                        db.session.add(product)
                        restored_products += 1
                
                db.session.commit()
                
                return {
                    'success': True,
                    'restored_products': restored_products,
                    'restored_at': datetime.utcnow().isoformat()
                }
            
            else:
                return {'success': False, 'error': 'Tipo de respaldo no soportado para restauración'}
            
        except Exception as e:
            self.logger.error(f'Error restaurando desde respaldo: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_backups(self):
        """Limpia respaldos antiguos"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
            
            self.logger.info(f'Limpiados {deleted_count} respaldos antiguos')
            return {'success': True, 'deleted_count': deleted_count}
            
        except Exception as e:
            self.logger.error(f'Error limpiando respaldos antiguos: {str(e)}')
            return {'success': False, 'error': str(e)}
    
    def get_backup_status(self) -> Dict:
        """Obtiene estado de los respaldos"""
        try:
            backups = []
            total_size = 0
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    backups.append({
                        'filename': filename,
                        'size': file_size,
                        'created_at': file_time.isoformat(),
                        'type': 'full' if 'full' in filename else 'data'
                    })
                    
                    total_size += file_size
            
            # Ordenar por fecha de creación
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'backups': backups,
                'total_backups': len(backups),
                'total_size': total_size,
                'retention_days': self.retention_days,
                'backup_dir': self.backup_dir
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo estado de respaldos: {str(e)}')
            return {'success': False, 'error': str(e)}

# Instancias globales de los servicios
external_integration_service = ExternalIntegrationService()
backup_service = BackupService()



