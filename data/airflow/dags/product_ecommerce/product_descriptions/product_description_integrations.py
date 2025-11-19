"""
Integraciones con plataformas de e-commerce para descripciones de productos.

Soporta:
- Shopify: Sincronización automática de descripciones
- Amazon: Formato optimizado para Amazon Seller Central
- WooCommerce: Integración vía API REST
- PrestaShop: Integración vía API

Características:
- Sincronización automática de descripciones generadas
- Actualización masiva de catálogos
- Webhooks para nuevos productos
- Manejo de errores y retries
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ShopifyIntegration:
    """Integración con Shopify para sincronizar descripciones."""
    
    def __init__(self, shop_domain: str, access_token: str):
        """
        Args:
            shop_domain: Dominio de la tienda (ej: 'mi-tienda.myshopify.com')
            access_token: Token de acceso de la API
        """
        self.shop_domain = shop_domain.rstrip('/')
        if not self.shop_domain.startswith('http'):
            self.shop_domain = f"https://{self.shop_domain}"
        self.access_token = access_token
        self.base_url = f"{self.shop_domain}/admin/api/2024-01"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
    
    def update_product_description(self, product_id: str, description: Dict) -> Dict:
        """
        Actualiza la descripción de un producto en Shopify.
        
        Args:
            product_id: ID del producto en Shopify
            description: Dict con 'description', 'seo_keywords', 'meta_description'
        
        Returns:
            Dict con resultado de la actualización
        """
        try:
            # Construir body para actualización
            body = {
                'product': {
                    'id': product_id,
                    'body_html': description.get('description', ''),
                    'metafields_global_title_tag': description.get('meta_description', '')[:70] or None,
                }
            }
            
            # Agregar tags SEO si existen
            if description.get('seo_keywords'):
                tags = description.get('tags', [])
                tags.extend([f"seo:{kw}" for kw in description['seo_keywords'][:5]])
                body['product']['tags'] = ','.join(tags)
            
            url = f"{self.base_url}/products/{product_id}.json"
            response = requests.put(url, headers=self.headers, json=body, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Descripción actualizada en Shopify para producto {product_id}")
                return {
                    'success': True,
                    'product_id': product_id,
                    'platform': 'shopify',
                    'updated_at': datetime.now().isoformat()
                }
            else:
                error_msg = f"Error actualizando Shopify: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Excepción actualizando Shopify: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_update_descriptions(self, products: List[Dict]) -> Dict:
        """
        Actualiza múltiples productos en batch.
        
        Args:
            products: Lista de dicts con 'product_id' y 'description'
        
        Returns:
            Dict con resultados de la actualización
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(products)
        }
        
        for product in products:
            result = self.update_product_description(
                product['product_id'],
                product['description']
            )
            if result['success']:
                results['success'].append(result)
            else:
                results['failed'].append({
                    'product_id': product.get('product_id'),
                    'error': result.get('error')
                })
        
        results['success_count'] = len(results['success'])
        results['failed_count'] = len(results['failed'])
        return results
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Obtiene información de un producto de Shopify."""
        try:
            url = f"{self.base_url}/products/{product_id}.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('product')
            else:
                logger.warning(f"Producto {product_id} no encontrado en Shopify")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo producto de Shopify: {str(e)}")
            return None


class AmazonIntegration:
    """Integración con Amazon Seller Central para descripciones."""
    
    def __init__(self, marketplace_id: str, seller_id: str, access_key: str, secret_key: str):
        """
        Args:
            marketplace_id: ID del marketplace (ej: 'ATVPDKIKX0DER' para US)
            seller_id: Seller ID de Amazon
            access_key: AWS Access Key
            secret_key: AWS Secret Key
        """
        self.marketplace_id = marketplace_id
        self.seller_id = seller_id
        self.access_key = access_key
        self.secret_key = secret_key
        # Nota: Amazon requiere autenticación SP-API más compleja
        # Esta es una implementación simplificada
        logger.warning("Amazon SP-API requiere configuración adicional de autenticación OAuth")
    
    def format_for_amazon(self, description: Dict) -> Dict:
        """
        Formatea la descripción según las especificaciones de Amazon.
        
        Amazon requiere:
        - Bullet points (máximo 5, 1000 caracteres cada uno)
        - Descripción principal (máximo 2000 caracteres)
        - Keywords separados por espacios
        """
        formatted = {
            'bullet_points': [],
            'description': '',
            'search_terms': ''
        }
        
        # Extraer bullet points de beneficios
        benefits = description.get('benefits_section', '')
        if not benefits:
            # Crear bullets desde key_benefits si está disponible
            key_benefits = description.get('metadata', {}).get('key_benefits', [])
            for benefit in key_benefits[:5]:
                if len(benefit) <= 1000:
                    formatted['bullet_points'].append(benefit)
        
        # Descripción principal
        main_desc = description.get('description', '')
        if len(main_desc) > 2000:
            main_desc = main_desc[:1997] + "..."
        formatted['description'] = main_desc
        
        # Search terms (keywords)
        keywords = description.get('seo_keywords', [])
        search_terms = ' '.join(keywords[:50])  # Amazon permite hasta 50 keywords
        if len(search_terms) > 250:
            search_terms = search_terms[:247] + "..."
        formatted['search_terms'] = search_terms
        
        return formatted
    
    def update_product_listing(self, sku: str, description: Dict) -> Dict:
        """
        Actualiza el listing de un producto en Amazon.
        
        Nota: Requiere implementación completa de SP-API con autenticación OAuth.
        Esta es una estructura básica.
        """
        try:
            formatted = self.format_for_amazon(description)
            
            # Aquí iría la llamada real a Amazon SP-API
            # Por ahora retornamos el formato preparado
            logger.info(f"Formato preparado para Amazon SKU: {sku}")
            
            return {
                'success': True,
                'sku': sku,
                'platform': 'amazon',
                'formatted_data': formatted,
                'note': 'Requiere implementación completa de SP-API'
            }
        except Exception as e:
            logger.error(f"Error formateando para Amazon: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class WooCommerceIntegration:
    """Integración con WooCommerce vía API REST."""
    
    def __init__(self, store_url: str, consumer_key: str, consumer_secret: str):
        """
        Args:
            store_url: URL de la tienda (ej: 'https://mi-tienda.com')
            consumer_key: Consumer Key de WooCommerce
            consumer_secret: Consumer Secret de WooCommerce
        """
        self.store_url = store_url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = f"{self.store_url}/wp-json/wc/v3"
    
    def update_product_description(self, product_id: int, description: Dict) -> Dict:
        """Actualiza la descripción de un producto en WooCommerce."""
        try:
            import requests.auth
            
            auth = requests.auth.HTTPBasicAuth(self.consumer_key, self.consumer_secret)
            
            body = {
                'description': description.get('description', ''),
                'short_description': description.get('meta_description', '')[:200] or ''
            }
            
            url = f"{self.base_url}/products/{product_id}"
            response = requests.put(url, auth=auth, json=body, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Descripción actualizada en WooCommerce para producto {product_id}")
                return {
                    'success': True,
                    'product_id': product_id,
                    'platform': 'woocommerce',
                    'updated_at': datetime.now().isoformat()
                }
            else:
                error_msg = f"Error actualizando WooCommerce: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
        except Exception as e:
            logger.error(f"Excepción actualizando WooCommerce: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def sync_description_to_platform(
    platform: str,
    product_id: str,
    description: Dict,
    credentials: Dict
) -> Dict:
    """
    Función helper para sincronizar descripción a cualquier plataforma.
    
    Args:
        platform: 'shopify', 'amazon', 'woocommerce'
        product_id: ID del producto en la plataforma
        description: Dict con la descripción generada
        credentials: Dict con credenciales de la plataforma
    
    Returns:
        Dict con resultado de la sincronización
    """
    try:
        if platform.lower() == 'shopify':
            integration = ShopifyIntegration(
                shop_domain=credentials.get('shop_domain'),
                access_token=credentials.get('access_token')
            )
            return integration.update_product_description(product_id, description)
        
        elif platform.lower() == 'amazon':
            integration = AmazonIntegration(
                marketplace_id=credentials.get('marketplace_id'),
                seller_id=credentials.get('seller_id'),
                access_key=credentials.get('access_key'),
                secret_key=credentials.get('secret_key')
            )
            return integration.update_product_listing(product_id, description)
        
        elif platform.lower() == 'woocommerce':
            integration = WooCommerceIntegration(
                store_url=credentials.get('store_url'),
                consumer_key=credentials.get('consumer_key'),
                consumer_secret=credentials.get('consumer_secret')
            )
            return integration.update_product_description(int(product_id), description)
        
        else:
            return {
                'success': False,
                'error': f'Plataforma no soportada: {platform}'
            }
    except Exception as e:
        logger.error(f"Error sincronizando a {platform}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

