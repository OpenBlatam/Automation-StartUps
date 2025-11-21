"""
Módulo de Extracción de Precios de Competencia

Extrae precios de competidores y mercado desde múltiples fuentes:
- APIs de competidores
- Web scraping
- Bases de datos de mercado
- APIs de agregadores de precios
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from price_config import PriceConfig
from price_cache import PriceCache
from price_circuit_breaker import get_circuit_breaker, CircuitBreakerConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class PriceExtractor:
    """Extrae precios de competencia desde múltiples fuentes"""
    
    def __init__(
        self,
        config: PriceConfig,
        cache: Optional[PriceCache] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    ):
        self.config = config
        self.cache = cache
        self.circuit_breaker_config = circuit_breaker_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.extraction_failures = 0
    
    def extract_all_competitor_prices(self) -> List[Dict]:
        """
        Extrae precios de todas las fuentes configuradas
        
        Returns:
            Lista de diccionarios con información de precios
        """
        all_prices = []
        self.extraction_failures = 0
        
        # Extraer de APIs de competidores
        if self.config.get('competitor_apis'):
            for api_config in self.config.get('competitor_apis', []):
                source_name = api_config.get('name', 'unknown')
                
                # Intentar obtener de caché
                cached_prices = None
                if self.cache:
                    cached_prices = self.cache.get(source_name)
                
                if cached_prices:
                    logger.info(f"Usando precios cacheados de {source_name}: {len(cached_prices)} productos")
                    all_prices.extend(cached_prices)
                else:
                    try:
                        # Usar circuit breaker si está configurado
                        if self.circuit_breaker_config:
                            circuit_breaker = get_circuit_breaker(
                                source_name,
                                self.circuit_breaker_config
                            )
                            prices = circuit_breaker.call(
                                self._extract_from_api_with_retry,
                                api_config
                            )
                        else:
                            prices = self._extract_from_api_with_retry(api_config)
                        
                        all_prices.extend(prices)
                        
                        # Guardar en caché
                        if self.cache and prices:
                            self.cache.set(source_name, prices)
                        
                        logger.info(f"Extraídos {len(prices)} precios de {source_name}")
                    except Exception as e:
                        self.extraction_failures += 1
                        logger.error(f"Error extrayendo de API {source_name}: {str(e)}")
        
        # Extraer mediante web scraping
        if self.config.get('scraping_sources'):
            for source in self.config.get('scraping_sources', []):
                source_name = source.get('name', 'unknown')
                
                # Intentar obtener de caché
                cached_prices = None
                if self.cache:
                    cached_prices = self.cache.get(source_name)
                
                if cached_prices:
                    logger.info(f"Usando precios cacheados de scraping {source_name}: {len(cached_prices)} productos")
                    all_prices.extend(cached_prices)
                else:
                    try:
                        prices = self._extract_from_scraping(source)
                        all_prices.extend(prices)
                        
                        # Guardar en caché
                        if self.cache and prices:
                            self.cache.set(source_name, prices)
                        
                        logger.info(f"Extraídos {len(prices)} precios de scraping {source_name}")
                        time.sleep(self.config.get('scraping_delay', 2))  # Rate limiting
                    except Exception as e:
                        self.extraction_failures += 1
                        logger.error(f"Error en scraping {source_name}: {str(e)}")
        
        # Extraer de bases de datos de mercado
        if self.config.get('market_databases'):
            for db_config in self.config.get('market_databases', []):
                source_name = db_config.get('name', 'unknown')
                try:
                    prices = self._extract_from_database(db_config)
                    all_prices.extend(prices)
                    logger.info(f"Extraídos {len(prices)} precios de BD {source_name}")
                except Exception as e:
                    self.extraction_failures += 1
                    logger.error(f"Error extrayendo de BD {source_name}: {str(e)}")
        
        # Consolidar y normalizar datos
        consolidated_prices = self._consolidate_prices(all_prices)
        
        logger.info(f"Total de precios extraídos y consolidados: {len(consolidated_prices)}")
        return consolidated_prices
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout))
    )
    def _extract_from_api_with_retry(self, api_config: Dict) -> List[Dict]:
        """Extrae desde API con retry automático"""
        return self._extract_from_api(api_config)
    
    def _extract_from_api(self, api_config: Dict) -> List[Dict]:
        """Extrae precios desde una API de competidor"""
        url = api_config.get('url')
        headers = api_config.get('headers', {})
        params = api_config.get('params', {})
        auth = api_config.get('auth')
        
        try:
            if auth:
                response = self.session.get(url, headers=headers, params=params, auth=auth, timeout=30)
            else:
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            # Procesar según el formato de la API
            prices = self._parse_api_response(data, api_config.get('parser_config', {}))
            
            return prices
            
        except Exception as e:
            logger.error(f"Error en extracción API {api_config.get('name')}: {str(e)}")
            return []
    
    def _extract_from_scraping(self, source_config: Dict) -> List[Dict]:
        """Extrae precios mediante web scraping"""
        url = source_config.get('url')
        selectors = source_config.get('selectors', {})
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            prices = []
            products = soup.select(selectors.get('product_container', ''))
            
            for product in products:
                try:
                    name = product.select_one(selectors.get('name', '')).text.strip() if product.select_one(selectors.get('name', '')) else ''
                    price_text = product.select_one(selectors.get('price', '')).text.strip() if product.select_one(selectors.get('price', '')) else ''
                    price = self._parse_price(price_text)
                    
                    if name and price:
                        prices.append({
                            'product_name': name,
                            'competitor_price': price,
                            'source': source_config.get('name'),
                            'extraction_date': datetime.now().isoformat(),
                            'url': url,
                        })
                except Exception as e:
                    logger.warning(f"Error procesando producto: {str(e)}")
                    continue
            
            return prices
            
        except Exception as e:
            logger.error(f"Error en scraping {source_config.get('name')}: {str(e)}")
            return []
    
    def _extract_from_database(self, db_config: Dict) -> List[Dict]:
        """Extrae precios desde una base de datos de mercado"""
        # Implementación específica según el tipo de BD
        # Por ejemplo: PostgreSQL, MySQL, MongoDB, etc.
        connection_string = db_config.get('connection_string')
        query = db_config.get('query')
        
        try:
            # Aquí se implementaría la conexión y consulta específica
            # Por ahora retornamos estructura vacía
            # prices = self._execute_db_query(connection_string, query)
            logger.info(f"Extracción de BD {db_config.get('name')} - implementar según BD específica")
            return []
            
        except Exception as e:
            logger.error(f"Error extrayendo de BD {db_config.get('name')}: {str(e)}")
            return []
    
    def _parse_api_response(self, data: Dict, parser_config: Dict) -> List[Dict]:
        """Parsea la respuesta de una API según configuración"""
        prices = []
        data_path = parser_config.get('data_path', 'data')
        
        # Navegar por la estructura de datos
        items = data
        for key in data_path.split('.'):
            items = items.get(key, [])
        
        for item in items:
            try:
                price = self._parse_price(item.get(parser_config.get('price_field', 'price')))
                prices.append({
                    'product_name': item.get(parser_config.get('name_field', 'name')),
                    'competitor_price': price,
                    'source': parser_config.get('source_name', 'api'),
                    'extraction_date': datetime.now().isoformat(),
                    'product_id': item.get(parser_config.get('id_field', 'id')),
                })
            except Exception as e:
                logger.warning(f"Error parseando item: {str(e)}")
                continue
        
        return prices
    
    def _parse_price(self, price_text: str) -> float:
        """Parsea un texto de precio a float"""
        if not price_text:
            return 0.0
        
        # Remover símbolos y espacios
        price_text = price_text.replace('$', '').replace(',', '').replace('€', '').replace('£', '')
        price_text = price_text.strip()
        
        try:
            return float(price_text)
        except ValueError:
            logger.warning(f"No se pudo parsear precio: {price_text}")
            return 0.0
    
    def _consolidate_prices(self, prices: List[Dict]) -> List[Dict]:
        """Consolida precios duplicados y calcula promedios"""
        # Agrupar por nombre de producto
        product_groups = {}
        
        for price_data in prices:
            product_name = price_data.get('product_name', '').lower().strip()
            
            if product_name not in product_groups:
                product_groups[product_name] = []
            
            product_groups[product_name].append(price_data)
        
        # Calcular precios promedio por producto
        consolidated = []
        for product_name, price_list in product_groups.items():
            valid_prices = [p.get('competitor_price', 0) for p in price_list if p.get('competitor_price', 0) > 0]
            
            if valid_prices:
                consolidated.append({
                    'product_name': product_name,
                    'avg_competitor_price': sum(valid_prices) / len(valid_prices),
                    'min_competitor_price': min(valid_prices),
                    'max_competitor_price': max(valid_prices),
                    'price_count': len(valid_prices),
                    'sources': list(set([p.get('source', 'unknown') for p in price_list])),
                    'extraction_date': datetime.now().isoformat(),
                })
        
        return consolidated
    
    def get_current_catalog_prices(self) -> List[Dict]:
        """
        Obtiene los precios actuales del catálogo propio
        
        Returns:
            Lista de productos con precios actuales
        """
        catalog_source = self.config.get('catalog_source')
        
        if catalog_source.get('type') == 'database':
            # Obtener desde base de datos
            return self._get_prices_from_db(catalog_source)
        elif catalog_source.get('type') == 'api':
            # Obtener desde API interna
            return self._get_prices_from_api(catalog_source)
        elif catalog_source.get('type') == 'file':
            # Obtener desde archivo
            return self._get_prices_from_file(catalog_source)
        else:
            logger.error(f"Tipo de fuente de catálogo no soportado: {catalog_source.get('type')}")
            return []
    
    def _get_prices_from_db(self, db_config: Dict) -> List[Dict]:
        """Obtiene precios desde base de datos"""
        # Implementar según BD específica
        logger.info("Obteniendo precios desde base de datos")
        # Ejemplo de estructura esperada:
        # return [
        #     {'product_id': '123', 'product_name': 'Producto A', 'current_price': 99.99},
        #     ...
        # ]
        return []
    
    def _get_prices_from_api(self, api_config: Dict) -> List[Dict]:
        """Obtiene precios desde API interna"""
        url = api_config.get('url')
        headers = api_config.get('headers', {})
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for item in data.get('products', []):
                prices.append({
                    'product_id': item.get('id'),
                    'product_name': item.get('name'),
                    'current_price': item.get('price'),
                })
            
            return prices
            
        except Exception as e:
            logger.error(f"Error obteniendo precios de API: {str(e)}")
            return []
    
    def _get_prices_from_file(self, file_config: Dict) -> List[Dict]:
        """Obtiene precios desde archivo"""
        file_path = file_config.get('path')
        file_type = file_config.get('format', 'csv')
        
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path)
            elif file_type == 'json':
                df = pd.read_json(file_path)
            elif file_type == 'excel':
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_type}")
            
            prices = df.to_dict('records')
            return prices
            
        except Exception as e:
            logger.error(f"Error leyendo archivo de precios: {str(e)}")
            return []





