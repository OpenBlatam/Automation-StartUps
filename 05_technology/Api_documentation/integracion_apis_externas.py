"""
Módulo de Integración con APIs Externas
=======================================

Este módulo integra diversas APIs para obtener datos en tiempo real:
- Google Maps API (rutas, tráfico, lugares)
- HERE API (navegación, tráfico)
- OpenStreetMap (datos geográficos)
- APIs de clima
- APIs de precios de combustible
- APIs de peajes
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import time
import hashlib

@dataclass
class ConfiguracionAPI:
    """Configuración para APIs externas"""
    nombre: str
    base_url: str
    api_key: str
    rate_limit: int  # requests per minute
    timeout: int  # seconds
    activa: bool = True

@dataclass
class RespuestaAPI:
    """Respuesta estandarizada de APIs"""
    exitosa: bool
    datos: Any
    codigo_respuesta: int
    mensaje_error: Optional[str] = None
    timestamp: datetime = None

class GestorAPIs:
    """Gestor centralizado de APIs externas"""
    
    def __init__(self):
        self.apis_configuradas = {}
        self.cache_respuestas = {}
        self.rate_limits = {}
        
    def configurar_api(self, config: ConfiguracionAPI):
        """Configura una nueva API"""
        self.apis_configuradas[config.nombre] = config
        self.rate_limits[config.nombre] = {
            'requests_count': 0,
            'window_start': datetime.now()
        }
    
    def _verificar_rate_limit(self, nombre_api: str) -> bool:
        """Verifica si se puede hacer una request respetando el rate limit"""
        if nombre_api not in self.rate_limits:
            return True
        
        config = self.apis_configuradas.get(nombre_api)
        if not config:
            return True
        
        rate_limit = self.rate_limits[nombre_api]
        ahora = datetime.now()
        
        # Resetear contador si ha pasado un minuto
        if (ahora - rate_limit['window_start']).seconds >= 60:
            rate_limit['requests_count'] = 0
            rate_limit['window_start'] = ahora
        
        return rate_limit['requests_count'] < config.rate_limit
    
    def _incrementar_rate_limit(self, nombre_api: str):
        """Incrementa el contador de requests"""
        if nombre_api in self.rate_limits:
            self.rate_limits[nombre_api]['requests_count'] += 1
    
    def _generar_clave_cache(self, nombre_api: str, parametros: Dict) -> str:
        """Genera clave única para cache"""
        contenido = f"{nombre_api}_{json.dumps(parametros, sort_keys=True)}"
        return hashlib.md5(contenido.encode()).hexdigest()
    
    def _obtener_del_cache(self, clave: str) -> Optional[RespuestaAPI]:
        """Obtiene respuesta del cache si existe y no ha expirado"""
        if clave in self.cache_respuestas:
            respuesta, timestamp = self.cache_respuestas[clave]
            # Cache válido por 5 minutos
            if (datetime.now() - timestamp).seconds < 300:
                return respuesta
            else:
                del self.cache_respuestas[clave]
        return None
    
    def _guardar_en_cache(self, clave: str, respuesta: RespuestaAPI):
        """Guarda respuesta en cache"""
        self.cache_respuestas[clave] = (respuesta, datetime.now())
    
    def hacer_request(self, nombre_api: str, endpoint: str, 
                     parametros: Dict, usar_cache: bool = True) -> RespuestaAPI:
        """Hace request a una API con manejo de errores y cache"""
        
        if nombre_api not in self.apis_configuradas:
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=400,
                mensaje_error=f"API {nombre_api} no configurada"
            )
        
        config = self.apis_configuradas[nombre_api]
        
        if not config.activa:
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=503,
                mensaje_error=f"API {nombre_api} desactivada"
            )
        
        # Verificar rate limit
        if not self._verificar_rate_limit(nombre_api):
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=429,
                mensaje_error=f"Rate limit excedido para {nombre_api}"
            )
        
        # Verificar cache
        if usar_cache:
            clave_cache = self._generar_clave_cache(nombre_api, parametros)
            respuesta_cache = self._obtener_del_cache(clave_cache)
            if respuesta_cache:
                return respuesta_cache
        
        try:
            # Preparar request
            url = f"{config.base_url}{endpoint}"
            headers = {'User-Agent': 'LogisticaOptimizacion/1.0'}
            
            # Agregar API key según el tipo de API
            if 'google' in nombre_api.lower():
                parametros['key'] = config.api_key
            elif 'here' in nombre_api.lower():
                parametros['apikey'] = config.api_key
            else:
                parametros['api_key'] = config.api_key
            
            # Hacer request
            response = requests.get(url, params=parametros, headers=headers, 
                                 timeout=config.timeout)
            
            # Incrementar rate limit
            self._incrementar_rate_limit(nombre_api)
            
            # Procesar respuesta
            if response.status_code == 200:
                datos = response.json()
                respuesta = RespuestaAPI(
                    exitosa=True,
                    datos=datos,
                    codigo_respuesta=200,
                    timestamp=datetime.now()
                )
                
                # Guardar en cache
                if usar_cache:
                    self._guardar_en_cache(clave_cache, respuesta)
                
                return respuesta
            else:
                return RespuestaAPI(
                    exitosa=False,
                    datos=None,
                    codigo_respuesta=response.status_code,
                    mensaje_error=f"Error HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=408,
                mensaje_error=f"Timeout en {nombre_api}"
            )
        except requests.exceptions.RequestException as e:
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=500,
                mensaje_error=f"Error de conexión: {str(e)}"
            )
        except Exception as e:
            return RespuestaAPI(
                exitosa=False,
                datos=None,
                codigo_respuesta=500,
                mensaje_error=f"Error inesperado: {str(e)}"
            )

class IntegradorGoogleMaps:
    """Integración específica con Google Maps API"""
    
    def __init__(self, gestor_apis: GestorAPIs):
        self.gestor = gestor_apis
    
    def obtener_ruta_optimizada(self, origen: Tuple[float, float], 
                              destinos: List[Tuple[float, float]],
                              hora_salida: datetime) -> RespuestaAPI:
        """Obtiene ruta optimizada usando Google Maps"""
        
        # Convertir coordenadas a strings
        origen_str = f"{origen[0]},{origen[1]}"
        destinos_str = "|".join([f"{d[0]},{d[1]}" for d in destinos])
        
        parametros = {
            'origins': origen_str,
            'destinations': destinos_str,
            'departure_time': int(hora_salida.timestamp()),
            'traffic_model': 'best_guess',
            'mode': 'driving',
            'avoid': 'tolls',  # Evitar peajes por defecto
            'units': 'metric'
        }
        
        return self.gestor.hacer_request(
            'google_maps',
            '/maps/api/distancematrix/json',
            parametros
        )
    
    def obtener_direcciones(self, origen: Tuple[float, float], 
                           destino: Tuple[float, float],
                           hora_salida: datetime) -> RespuestaAPI:
        """Obtiene direcciones paso a paso"""
        
        parametros = {
            'origin': f"{origen[0]},{origen[1]}",
            'destination': f"{destino[0]},{destino[1]}",
            'departure_time': int(hora_salida.timestamp()),
            'traffic_model': 'best_guess',
            'mode': 'driving',
            'units': 'metric'
        }
        
        return self.gestor.hacer_request(
            'google_maps',
            '/maps/api/directions/json',
            parametros
        )
    
    def buscar_lugares_cercanos(self, ubicacion: Tuple[float, float], 
                              tipo_lugar: str, radio: int = 1000) -> RespuestaAPI:
        """Busca lugares cercanos (gasolineras, restaurantes, etc.)"""
        
        parametros = {
            'location': f"{ubicacion[0]},{ubicacion[1]}",
            'radius': radius,
            'type': tipo_lugar,
            'key': self.gestor.apis_configuradas['google_maps'].api_key
        }
        
        return self.gestor.hacer_request(
            'google_maps',
            '/maps/api/place/nearbysearch/json',
            parametros
        )

class IntegradorHERE:
    """Integración específica con HERE API"""
    
    def __init__(self, gestor_apis: GestorAPIs):
        self.gestor = gestor_apis
    
    def calcular_ruta(self, origen: Tuple[float, float], 
                     destino: Tuple[float, float]) -> RespuestaAPI:
        """Calcula ruta usando HERE API"""
        
        parametros = {
            'waypoint0': f"geo!{origen[0]},{origen[1]}",
            'waypoint1': f"geo!{destino[0]},{destino[1]}",
            'mode': 'fastest;car;traffic:enabled',
            'legAttributes': 'links,shape',
            'routeAttributes': 'summary,shape'
        }
        
        return self.gestor.hacer_request(
            'here',
            '/routing/7.2/calculateroute.json',
            parametros
        )
    
    def obtener_trafico_tiempo_real(self, ubicacion: Tuple[float, float], 
                                   radio: int = 5000) -> RespuestaAPI:
        """Obtiene información de tráfico en tiempo real"""
        
        parametros = {
            'in': f"circle:{ubicacion[0]},{ubicacion[1]};r={radio}",
            'flow': 'true',
            'incidents': 'true'
        }
        
        return self.gestor.hacer_request(
            'here',
            '/traffic/6.3/flow.json',
            parametros
        )

class IntegradorClima:
    """Integración con APIs de clima"""
    
    def __init__(self, gestor_apis: GestorAPIs):
        self.gestor = gestor_apis
    
    def obtener_clima_actual(self, ubicacion: Tuple[float, float]) -> RespuestaAPI:
        """Obtiene clima actual para una ubicación"""
        
        parametros = {
            'lat': ubicacion[0],
            'lon': ubicacion[1],
            'units': 'metric',
            'appid': self.gestor.apis_configuradas['openweather'].api_key
        }
        
        return self.gestor.hacer_request(
            'openweather',
            '/data/2.5/weather',
            parametros
        )
    
    def obtener_pronostico(self, ubicacion: Tuple[float, float], 
                          dias: int = 5) -> RespuestaAPI:
        """Obtiene pronóstico del clima"""
        
        parametros = {
            'lat': ubicacion[0],
            'lon': ubicacion[1],
            'cnt': dias,
            'units': 'metric',
            'appid': self.gestor.apis_configuradas['openweather'].api_key
        }
        
        return self.gestor.hacer_request(
            'openweather',
            '/data/2.5/forecast',
            parametros
        )

class IntegradorCombustible:
    """Integración con APIs de precios de combustible"""
    
    def __init__(self, gestor_apis: GestorAPIs):
        self.gestor = gestor_apis
    
    def obtener_precios_combustible(self, ubicacion: Tuple[float, float], 
                                  radio: int = 10000) -> RespuestaAPI:
        """Obtiene precios de combustible cercanos"""
        
        parametros = {
            'lat': ubicacion[0],
            'lng': ubicacion[1],
            'radius': radio,
            'type': 'gas_station'
        }
        
        return self.gestor.hacer_request(
            'fuel_prices',
            '/api/v1/stations',
            parametros
        )

def configurar_apis_ejemplo():
    """Configura APIs de ejemplo para demostración"""
    
    gestor = GestorAPIs()
    
    # Configurar Google Maps API
    gestor.configurar_api(ConfiguracionAPI(
        nombre='google_maps',
        base_url='https://maps.googleapis.com',
        api_key='TU_API_KEY_GOOGLE_MAPS',  # Reemplazar con API key real
        rate_limit=1000,
        timeout=10
    ))
    
    # Configurar HERE API
    gestor.configurar_api(ConfiguracionAPI(
        nombre='here',
        base_url='https://route.ls.hereapi.com',
        api_key='TU_API_KEY_HERE',  # Reemplazar con API key real
        rate_limit=1000,
        timeout=10
    ))
    
    # Configurar OpenWeather API
    gestor.configurar_api(ConfiguracionAPI(
        nombre='openweather',
        base_url='https://api.openweathermap.org',
        api_key='TU_API_KEY_OPENWEATHER',  # Reemplazar con API key real
        rate_limit=1000,
        timeout=10
    ))
    
    return gestor

def ejemplo_integracion_apis():
    """Ejemplo de uso de integración con APIs"""
    
    print("=== Integración con APIs Externas ===\n")
    
    # Configurar APIs
    gestor = configurar_apis_ejemplo()
    
    # Crear integradores
    google_maps = IntegradorGoogleMaps(gestor)
    here = IntegradorHERE(gestor)
    clima = IntegradorClima(gestor)
    
    # Ejemplo 1: Obtener ruta optimizada
    print("1. Obteniendo ruta optimizada:")
    origen = (-12.0464, -77.0428)  # Lima, Perú
    destinos = [(-12.0564, -77.0328), (-12.0364, -77.0528)]
    hora_salida = datetime.now()
    
    respuesta_ruta = google_maps.obtener_ruta_optimizada(origen, destinos, hora_salida)
    
    if respuesta_ruta.exitosa:
        print("   ✓ Ruta obtenida exitosamente")
        # Procesar datos de la ruta aquí
    else:
        print(f"   ✗ Error: {respuesta_ruta.mensaje_error}")
    
    # Ejemplo 2: Obtener clima actual
    print("\n2. Obteniendo clima actual:")
    respuesta_clima = clima.obtener_clima_actual(origen)
    
    if respuesta_clima.exitosa:
        print("   ✓ Clima obtenido exitosamente")
        # Procesar datos del clima aquí
    else:
        print(f"   ✗ Error: {respuesta_clima.mensaje_error}")
    
    # Ejemplo 3: Buscar gasolineras cercanas
    print("\n3. Buscando gasolineras cercanas:")
    respuesta_gasolineras = google_maps.buscar_lugares_cercanos(origen, "gas_station", 2000)
    
    if respuesta_gasolineras.exitosa:
        print("   ✓ Gasolineras encontradas")
        # Procesar datos de gasolineras aquí
    else:
        print(f"   ✗ Error: {respuesta_gasolineras.mensaje_error}")
    
    # Ejemplo 4: Información de tráfico
    print("\n4. Obteniendo información de tráfico:")
    respuesta_trafico = here.obtener_trafico_tiempo_real(origen, 5000)
    
    if respuesta_trafico.exitosa:
        print("   ✓ Información de tráfico obtenida")
        # Procesar datos de tráfico aquí
    else:
        print(f"   ✗ Error: {respuesta_trafico.mensaje_error}")

if __name__ == "__main__":
    ejemplo_integracion_apis()



