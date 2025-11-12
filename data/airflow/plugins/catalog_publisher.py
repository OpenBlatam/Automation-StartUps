"""
Módulo de Publicación de Catálogo Actualizado

Aplica ajustes de precios y publica el catálogo actualizado
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import requests
import pandas as pd

from price_config import PriceConfig

logger = logging.getLogger(__name__)


class CatalogPublisher:
    """Publica catálogo actualizado con nuevos precios"""
    
    def __init__(self, config: PriceConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def apply_price_adjustments(self, adjustments: List[Dict]) -> Dict:
        """
        Aplica los ajustes de precios al catálogo
        
        Args:
            adjustments: Lista de ajustes de precios a aplicar
        
        Returns:
            Catálogo actualizado
        """
        catalog_source = self.config.get('catalog_source')
        
        # Obtener catálogo actual
        if catalog_source.get('type') == 'database':
            current_catalog = self._load_catalog_from_db(catalog_source)
        elif catalog_source.get('type') == 'api':
            current_catalog = self._load_catalog_from_api(catalog_source)
        elif catalog_source.get('type') == 'file':
            current_catalog = self._load_catalog_from_file(catalog_source)
        else:
            raise ValueError(f"Tipo de fuente de catálogo no soportado: {catalog_source.get('type')}")
        
        # Aplicar ajustes
        updated_catalog = self._apply_adjustments_to_catalog(current_catalog, adjustments)
        
        logger.info(f"Catálogo actualizado: {len(updated_catalog.get('products', []))} productos")
        return updated_catalog
    
    def _load_catalog_from_db(self, db_config: Dict) -> Dict:
        """Carga catálogo desde base de datos"""
        # Implementar según BD específica
        logger.info("Cargando catálogo desde base de datos")
        return {'products': []}
    
    def _load_catalog_from_api(self, api_config: Dict) -> Dict:
        """Carga catálogo desde API"""
        url = api_config.get('url')
        headers = api_config.get('headers', {})
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error cargando catálogo desde API: {str(e)}")
            raise
    
    def _load_catalog_from_file(self, file_config: Dict) -> Dict:
        """Carga catálogo desde archivo"""
        file_path = file_config.get('path')
        file_type = file_config.get('format', 'json')
        
        try:
            if file_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif file_type == 'csv':
                df = pd.read_csv(file_path)
                return {'products': df.to_dict('records')}
            elif file_type == 'excel':
                df = pd.read_excel(file_path)
                return {'products': df.to_dict('records')}
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_type}")
        except Exception as e:
            logger.error(f"Error cargando catálogo desde archivo: {str(e)}")
            raise
    
    def _apply_adjustments_to_catalog(
        self,
        catalog: Dict,
        adjustments: List[Dict]
    ) -> Dict:
        """Aplica ajustes de precios al catálogo"""
        # Crear diccionario de ajustes para búsqueda rápida
        adjustments_dict = {}
        for adj in adjustments:
            product_id = adj.get('product_id')
            if product_id:
                adjustments_dict[str(product_id)] = adj
        
        # Aplicar ajustes a productos
        updated_products = []
        products = catalog.get('products', [])
        
        for product in products:
            product_id = str(product.get('id', product.get('product_id', '')))
            adjustment = adjustments_dict.get(product_id)
            
            if adjustment:
                # Aplicar nuevo precio
                product['price'] = adjustment.get('new_price')
                product['previous_price'] = adjustment.get('current_price')
                product['price_change'] = adjustment.get('price_change')
                product['price_change_percent'] = adjustment.get('price_change_percent')
                product['price_updated_at'] = datetime.now().isoformat()
                product['price_update_reason'] = adjustment.get('reason')
                
                updated_products.append(product)
            else:
                # Mantener producto sin cambios
                updated_products.append(product)
        
        catalog['products'] = updated_products
        catalog['updated_at'] = datetime.now().isoformat()
        catalog['total_products'] = len(updated_products)
        catalog['products_updated'] = len([p for p in updated_products if 'price_change' in p])
        
        return catalog
    
    def validate_catalog(self, catalog: Dict) -> Dict:
        """
        Valida el catálogo antes de publicarlo
        
        Returns:
            Dict con resultado de validación
        """
        errors = []
        warnings = []
        
        products = catalog.get('products', [])
        
        if not products:
            errors.append("El catálogo no contiene productos")
        
        # Validar cada producto
        for product in products:
            product_id = product.get('id', product.get('product_id'))
            price = product.get('price', 0)
            
            if not product_id:
                warnings.append(f"Producto sin ID: {product.get('name', 'unknown')}")
            
            if price <= 0:
                errors.append(f"Producto {product_id} tiene precio inválido: {price}")
            
            # Validar cambios extremos
            if 'price_change_percent' in product:
                change_percent = abs(product.get('price_change_percent', 0))
                max_change = self.config.get('max_price_change_percent', 20)
                
                if change_percent > max_change:
                    warnings.append(
                        f"Producto {product_id} tiene cambio de precio grande: {change_percent:.2f}%"
                    )
        
        is_valid = len(errors) == 0
        
        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'products_count': len(products),
            'validated_at': datetime.now().isoformat(),
        }
    
    def publish_catalog(self, catalog: Dict) -> Dict:
        """
        Publica el catálogo actualizado
        
        Args:
            catalog: Catálogo actualizado para publicar
        
        Returns:
            Resultado de la publicación
        """
        publish_target = self.config.get('publish_target')
        publish_type = publish_target.get('type', 'api')
        
        try:
            if publish_type == 'api':
                result = self._publish_to_api(catalog, publish_target)
            elif publish_type == 'database':
                result = self._publish_to_database(catalog, publish_target)
            elif publish_type == 'file':
                result = self._publish_to_file(catalog, publish_target)
            elif publish_type == 'multiple':
                result = self._publish_to_multiple(catalog, publish_target)
            else:
                raise ValueError(f"Tipo de publicación no soportado: {publish_type}")
            
            logger.info(f"Catálogo publicado exitosamente: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error publicando catálogo: {str(e)}")
            raise
    
    def _publish_to_api(self, catalog: Dict, api_config: Dict) -> Dict:
        """Publica catálogo a través de API"""
        url = api_config.get('url')
        method = api_config.get('method', 'POST')
        headers = api_config.get('headers', {})
        auth = api_config.get('auth')
        
        # Preparar datos según formato requerido
        data_format = api_config.get('data_format', 'full_catalog')
        
        if data_format == 'full_catalog':
            payload = catalog
        elif data_format == 'products_only':
            payload = {'products': catalog.get('products', [])}
        elif data_format == 'price_updates_only':
            payload = {
                'updates': [
                    {
                        'product_id': p.get('id', p.get('product_id')),
                        'price': p.get('price'),
                        'previous_price': p.get('previous_price'),
                    }
                    for p in catalog.get('products', [])
                    if 'price_change' in p and p.get('price_change', 0) != 0
                ]
            }
        else:
            payload = catalog
        
        try:
            if method.upper() == 'POST':
                if auth:
                    response = self.session.post(url, json=payload, headers=headers, auth=auth, timeout=60)
                else:
                    response = self.session.post(url, json=payload, headers=headers, timeout=60)
            elif method.upper() == 'PUT':
                if auth:
                    response = self.session.put(url, json=payload, headers=headers, auth=auth, timeout=60)
                else:
                    response = self.session.put(url, json=payload, headers=headers, timeout=60)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            
            return {
                'success': True,
                'products_updated': catalog.get('products_updated', 0),
                'total_products': catalog.get('total_products', 0),
                'published_at': datetime.now().isoformat(),
                'response': response.json() if response.content else {},
            }
            
        except Exception as e:
            logger.error(f"Error publicando a API: {str(e)}")
            raise
    
    def _publish_to_database(self, catalog: Dict, db_config: Dict) -> Dict:
        """Publica catálogo a base de datos"""
        # Implementar según BD específica
        logger.info("Publicando catálogo a base de datos")
        
        products_updated = catalog.get('products_updated', 0)
        
        return {
            'success': True,
            'products_updated': products_updated,
            'total_products': catalog.get('total_products', 0),
            'published_at': datetime.now().isoformat(),
            'method': 'database',
        }
    
    def _publish_to_file(self, catalog: Dict, file_config: Dict) -> Dict:
        """Publica catálogo a archivo"""
        file_path = file_config.get('path')
        file_type = file_config.get('format', 'json')
        backup_enabled = file_config.get('backup', True)
        
        try:
            # Hacer backup si está habilitado
            if backup_enabled:
                self._backup_existing_file(file_path)
            
            # Guardar nuevo catálogo
            if file_type == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(catalog, f, indent=2, ensure_ascii=False)
            elif file_type == 'csv':
                df = pd.DataFrame(catalog.get('products', []))
                df.to_csv(file_path, index=False)
            elif file_type == 'excel':
                df = pd.DataFrame(catalog.get('products', []))
                df.to_excel(file_path, index=False)
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_type}")
            
            products_updated = catalog.get('products_updated', 0)
            
            return {
                'success': True,
                'products_updated': products_updated,
                'total_products': catalog.get('total_products', 0),
                'published_at': datetime.now().isoformat(),
                'file_path': file_path,
                'method': 'file',
            }
            
        except Exception as e:
            logger.error(f"Error publicando a archivo: {str(e)}")
            raise
    
    def _publish_to_multiple(self, catalog: Dict, targets_config: Dict) -> Dict:
        """Publica catálogo a múltiples destinos"""
        results = []
        targets = targets_config.get('targets', [])
        
        for target in targets:
            try:
                target_type = target.get('type')
                
                if target_type == 'api':
                    result = self._publish_to_api(catalog, target)
                elif target_type == 'database':
                    result = self._publish_to_database(catalog, target)
                elif target_type == 'file':
                    result = self._publish_to_file(catalog, target)
                else:
                    logger.warning(f"Tipo de destino no soportado: {target_type}")
                    continue
                
                results.append({
                    'target': target.get('name', 'unknown'),
                    'result': result,
                })
                
            except Exception as e:
                logger.error(f"Error publicando a {target.get('name', 'unknown')}: {str(e)}")
                results.append({
                    'target': target.get('name', 'unknown'),
                    'error': str(e),
                })
        
        # Si al menos uno fue exitoso, considerar publicación exitosa
        successful = [r for r in results if r.get('result', {}).get('success', False)]
        
        return {
            'success': len(successful) > 0,
            'products_updated': catalog.get('products_updated', 0),
            'total_products': catalog.get('total_products', 0),
            'published_at': datetime.now().isoformat(),
            'targets': results,
            'method': 'multiple',
        }
    
    def _backup_existing_file(self, file_path: str):
        """Hace backup del archivo existente"""
        import os
        import shutil
        from datetime import datetime
        
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup creado: {backup_path}")
    
    def log_publish_results(self, publish_result: Dict, execution_date):
        """Registra resultados de publicación para auditoría"""
        log_file = self.config.get('audit_log_file', '/tmp/price_automation_audit.log')
        
        log_entry = {
            'execution_date': execution_date.isoformat() if hasattr(execution_date, 'isoformat') else str(execution_date),
            'publish_result': publish_result,
            'logged_at': datetime.now().isoformat(),
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.warning(f"No se pudo escribir en log de auditoría: {str(e)}")



















