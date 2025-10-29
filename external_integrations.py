"""
Sistema de Integración con APIs Externas
========================================

Integración con servicios externos para enriquecer el sistema
de gestión de inventario con datos de mercado, precios y logística.
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import base64
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Tipos de integración"""
    MARKET_DATA = "market_data"
    PRICING = "pricing"
    LOGISTICS = "logistics"
    WEATHER = "weather"
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"

class DataSource(Enum):
    """Fuentes de datos"""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    FEDEX = "fedex"
    UPS = "ups"
    DHL = "dhl"
    OPENWEATHER = "openweather"
    NEWS_API = "news_api"
    TWITTER = "twitter"

@dataclass
class MarketData:
    """Datos de mercado"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    source: str

@dataclass
class PricingData:
    """Datos de precios"""
    product_category: str
    current_price: float
    price_trend: str  # "up", "down", "stable"
    price_forecast: float
    confidence: float
    timestamp: datetime
    source: str

@dataclass
class LogisticsData:
    """Datos de logística"""
    carrier: str
    service_type: str
    estimated_days: int
    cost: float
    tracking_available: bool
    timestamp: datetime

@dataclass
class WeatherData:
    """Datos meteorológicos"""
    location: str
    temperature: float
    humidity: float
    conditions: str
    wind_speed: float
    timestamp: datetime

class APIIntegration:
    """Clase base para integraciones de API"""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'InventoryManagementSystem/1.0',
            'Accept': 'application/json'
        })
        self.rate_limit_delay = 1  # segundos entre requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Aplicar límite de tasa"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Realizar petición HTTP"""
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a {url}: {e}")
            raise
    
    def _make_post_request(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Realizar petición POST"""
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición POST a {url}: {e}")
            raise

class AlphaVantageIntegration(APIIntegration):
    """Integración con Alpha Vantage para datos de mercado"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://www.alphavantage.co/query")
        self.rate_limit_delay = 12  # Alpha Vantage tiene límite de 5 requests/minuto
    
    def get_stock_quote(self, symbol: str) -> MarketData:
        """Obtener cotización de acción"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        data = self._make_request('', params)
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return MarketData(
                symbol=symbol,
                price=float(quote['05. price']),
                change=float(quote['09. change']),
                change_percent=float(quote['10. change percent'].rstrip('%')),
                volume=int(quote['06. volume']),
                timestamp=datetime.now(),
                source='alpha_vantage'
            )
        else:
            raise ValueError(f"No se encontraron datos para {symbol}")
    
    def get_currency_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Obtener tasa de cambio de divisas"""
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.api_key
        }
        
        data = self._make_request('', params)
        
        if 'Realtime Currency Exchange Rate' in data:
            rate = data['Realtime Currency Exchange Rate']
            return float(rate['5. Exchange Rate'])
        else:
            raise ValueError(f"No se encontró tasa de cambio para {from_currency}/{to_currency}")

class FedExIntegration(APIIntegration):
    """Integración con FedEx para servicios de logística"""
    
    def __init__(self, api_key: str, secret_key: str, account_number: str):
        super().__init__(api_key, "https://apis-sandbox.fedex.com")
        self.secret_key = secret_key
        self.account_number = account_number
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Obtener token de acceso"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret_key
        }
        
        response = self.session.post(
            f"{self.base_url}/oauth/token",
            data=auth_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            # Actualizar headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            
            return self.access_token
        else:
            raise ValueError("Error obteniendo token de acceso de FedEx")
    
    def get_shipping_rates(self, origin: Dict[str, str], destination: Dict[str, str], 
                          weight: float, dimensions: Dict[str, float]) -> List[LogisticsData]:
        """Obtener tarifas de envío"""
        self._get_access_token()
        
        data = {
            'accountNumber': {
                'value': self.account_number
            },
            'requestedShipment': {
                'shipper': {
                    'address': origin
                },
                'recipients': [{
                    'address': destination
                }],
                'shipDatestamp': datetime.now().strftime('%Y-%m-%d'),
                'rateRequestType': ['ACCOUNT'],
                'requestedPackageLineItems': [{
                    'weight': {
                        'value': weight,
                        'units': 'KG'
                    },
                    'dimensions': {
                        'length': dimensions.get('length', 0),
                        'width': dimensions.get('width', 0),
                        'height': dimensions.get('height', 0),
                        'units': 'CM'
                    }
                }]
            }
        }
        
        response_data = self._make_post_request('/rate/v1/rates/quotes', data)
        
        logistics_data = []
        if 'output' in response_data and 'rateReplyDetails' in response_data['output']:
            for rate_detail in response_data['output']['rateReplyDetails']:
                logistics_data.append(LogisticsData(
                    carrier='FedEx',
                    service_type=rate_detail.get('serviceType', 'Unknown'),
                    estimated_days=rate_detail.get('commit', {}).get('daysInTransit', 0),
                    cost=rate_detail.get('ratedShipmentDetails', [{}])[0].get('totalNetCharge', {}).get('amount', 0),
                    tracking_available=True,
                    timestamp=datetime.now()
                ))
        
        return logistics_data

class OpenWeatherIntegration(APIIntegration):
    """Integración con OpenWeather para datos meteorológicos"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.openweathermap.org/data/2.5")
        self.rate_limit_delay = 1
    
    def get_current_weather(self, city: str, country_code: str = None) -> WeatherData:
        """Obtener clima actual"""
        params = {
            'q': f"{city},{country_code}" if country_code else city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        data = self._make_request('/weather', params)
        
        return WeatherData(
            location=f"{city}, {country_code}" if country_code else city,
            temperature=data['main']['temp'],
            humidity=data['main']['humidity'],
            conditions=data['weather'][0]['description'],
            wind_speed=data['wind']['speed'],
            timestamp=datetime.now()
        )
    
    def get_weather_forecast(self, city: str, days: int = 5) -> List[WeatherData]:
        """Obtener pronóstico del clima"""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': days * 8  # 8 mediciones por día (cada 3 horas)
        }
        
        data = self._make_request('/forecast', params)
        
        forecast = []
        for item in data['list'][:days]:
            forecast.append(WeatherData(
                location=city,
                temperature=item['main']['temp'],
                humidity=item['main']['humidity'],
                conditions=item['weather'][0]['description'],
                wind_speed=item['wind']['speed'],
                timestamp=datetime.fromtimestamp(item['dt'])
            ))
        
        return forecast

class NewsAPIIntegration(APIIntegration):
    """Integración con News API para noticias del sector"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://newsapi.org/v2")
        self.rate_limit_delay = 1
    
    def get_industry_news(self, industry: str, language: str = 'en', 
                         page_size: int = 20) -> List[Dict[str, Any]]:
        """Obtener noticias de la industria"""
        params = {
            'q': industry,
            'language': language,
            'pageSize': page_size,
            'sortBy': 'publishedAt',
            'apiKey': self.api_key
        }
        
        data = self._make_request('/everything', params)
        
        return data.get('articles', [])
    
    def get_headlines(self, category: str = 'business', country: str = 'us') -> List[Dict[str, Any]]:
        """Obtener titulares por categoría"""
        params = {
            'category': category,
            'country': country,
            'apiKey': self.api_key
        }
        
        data = self._make_request('/top-headlines', params)
        
        return data.get('articles', [])

class IntegrationManager:
    """Gestor de integraciones externas"""
    
    def __init__(self):
        self.integrations = {}
        self.cache = {}
        self.cache_ttl = {}
    
    def register_integration(self, name: str, integration: APIIntegration):
        """Registrar integración"""
        self.integrations[name] = integration
        logger.info(f"Integración {name} registrada")
    
    def get_cached_data(self, key: str, ttl_seconds: int = 300) -> Optional[Any]:
        """Obtener datos del caché"""
        if key in self.cache:
            if key in self.cache_ttl:
                if datetime.now() < self.cache_ttl[key]:
                    return self.cache[key]
                else:
                    # Expirar caché
                    del self.cache[key]
                    del self.cache_ttl[key]
        
        return None
    
    def set_cached_data(self, key: str, data: Any, ttl_seconds: int = 300):
        """Establecer datos en caché"""
        self.cache[key] = data
        self.cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Obtener datos de mercado"""
        cache_key = f"market_data_{symbol}"
        cached_data = self.get_cached_data(cache_key, 300)  # 5 minutos
        
        if cached_data:
            return cached_data
        
        if 'alpha_vantage' in self.integrations:
            try:
                data = self.integrations['alpha_vantage'].get_stock_quote(symbol)
                self.set_cached_data(cache_key, data, 300)
                return data
            except Exception as e:
                logger.error(f"Error obteniendo datos de mercado para {symbol}: {e}")
        
        return None
    
    def get_shipping_rates(self, origin: Dict[str, str], destination: Dict[str, str],
                          weight: float, dimensions: Dict[str, float]) -> List[LogisticsData]:
        """Obtener tarifas de envío"""
        cache_key = f"shipping_{hash(str(origin) + str(destination) + str(weight))}"
        cached_data = self.get_cached_data(cache_key, 1800)  # 30 minutos
        
        if cached_data:
            return cached_data
        
        all_rates = []
        
        # FedEx
        if 'fedex' in self.integrations:
            try:
                fedex_rates = self.integrations['fedex'].get_shipping_rates(
                    origin, destination, weight, dimensions
                )
                all_rates.extend(fedex_rates)
            except Exception as e:
                logger.error(f"Error obteniendo tarifas de FedEx: {e}")
        
        # Aquí se pueden agregar más carriers (UPS, DHL, etc.)
        
        if all_rates:
            self.set_cached_data(cache_key, all_rates, 1800)
        
        return all_rates
    
    def get_weather_data(self, city: str) -> Optional[WeatherData]:
        """Obtener datos meteorológicos"""
        cache_key = f"weather_{city}"
        cached_data = self.get_cached_data(cache_key, 1800)  # 30 minutos
        
        if cached_data:
            return cached_data
        
        if 'openweather' in self.integrations:
            try:
                data = self.integrations['openweather'].get_current_weather(city)
                self.set_cached_data(cache_key, data, 1800)
                return data
            except Exception as e:
                logger.error(f"Error obteniendo datos meteorológicos para {city}: {e}")
        
        return None
    
    def get_industry_news(self, industry: str) -> List[Dict[str, Any]]:
        """Obtener noticias de la industria"""
        cache_key = f"news_{industry}"
        cached_data = self.get_cached_data(cache_key, 3600)  # 1 hora
        
        if cached_data:
            return cached_data
        
        if 'news_api' in self.integrations:
            try:
                data = self.integrations['news_api'].get_industry_news(industry)
                self.set_cached_data(cache_key, data, 3600)
                return data
            except Exception as e:
                logger.error(f"Error obteniendo noticias para {industry}: {e}")
        
        return []
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtener estado de las integraciones"""
        status = {}
        
        for name, integration in self.integrations.items():
            try:
                # Probar conectividad básica
                if hasattr(integration, '_make_request'):
                    # Hacer una petición de prueba simple
                    integration._make_request('/')
                status[name] = {
                    'status': 'connected',
                    'last_check': datetime.now().isoformat()
                }
            except Exception as e:
                status[name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        return status

# Instancia global del gestor de integraciones
integration_manager = IntegrationManager()

# Funciones de conveniencia
def setup_integrations(config: Dict[str, str]):
    """Configurar integraciones desde configuración"""
    
    # Alpha Vantage
    if 'alpha_vantage_api_key' in config:
        integration_manager.register_integration(
            'alpha_vantage',
            AlphaVantageIntegration(config['alpha_vantage_api_key'])
        )
    
    # FedEx
    if all(key in config for key in ['fedex_api_key', 'fedex_secret_key', 'fedex_account_number']):
        integration_manager.register_integration(
            'fedex',
            FedExIntegration(
                config['fedex_api_key'],
                config['fedex_secret_key'],
                config['fedex_account_number']
            )
        )
    
    # OpenWeather
    if 'openweather_api_key' in config:
        integration_manager.register_integration(
            'openweather',
            OpenWeatherIntegration(config['openweather_api_key'])
        )
    
    # News API
    if 'news_api_key' in config:
        integration_manager.register_integration(
            'news_api',
            NewsAPIIntegration(config['news_api_key'])
        )

def get_market_trends(symbols: List[str]) -> Dict[str, MarketData]:
    """Obtener tendencias de mercado para múltiples símbolos"""
    trends = {}
    
    for symbol in symbols:
        data = integration_manager.get_market_data(symbol)
        if data:
            trends[symbol] = data
    
    return trends

def get_optimal_shipping(origin: Dict[str, str], destination: Dict[str, str],
                        weight: float, dimensions: Dict[str, float]) -> Optional[LogisticsData]:
    """Obtener opción de envío óptima (más rápida y económica)"""
    rates = integration_manager.get_shipping_rates(origin, destination, weight, dimensions)
    
    if not rates:
        return None
    
    # Encontrar la mejor opción (balance entre costo y tiempo)
    best_option = min(rates, key=lambda x: (x.cost * 0.7) + (x.estimated_days * 10))
    
    return best_option

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando integraciones externas...")
    
    # Configurar integraciones (usar claves reales en producción)
    config = {
        'alpha_vantage_api_key': 'demo',  # Clave de demostración
        'openweather_api_key': 'demo',   # Clave de demostración
        'news_api_key': 'demo'           # Clave de demostración
    }
    
    setup_integrations(config)
    
    # Probar integraciones
    try:
        # Datos de mercado
        market_data = integration_manager.get_market_data('AAPL')
        if market_data:
            print(f"Datos de mercado AAPL: ${market_data.price}")
        
        # Datos meteorológicos
        weather = integration_manager.get_weather_data('New York')
        if weather:
            print(f"Clima en {weather.location}: {weather.temperature}°C")
        
        # Noticias
        news = integration_manager.get_industry_news('technology')
        if news:
            print(f"Noticias de tecnología: {len(news)} artículos")
        
        # Estado de integraciones
        status = integration_manager.get_integration_status()
        print(f"Estado de integraciones: {status}")
        
    except Exception as e:
        logger.error(f"Error probando integraciones: {e}")
    
    print("✅ Sistema de integraciones funcionando")



