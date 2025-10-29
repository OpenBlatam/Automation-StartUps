"""
Módulo de Consideraciones de Tráfico y Horarios
==============================================

Este módulo maneja la integración con APIs de tráfico en tiempo real,
análisis de patrones de tráfico y optimización basada en horarios.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

@dataclass
class CondicionTrafico:
    """Representa condiciones de tráfico en un momento específico"""
    timestamp: datetime
    nivel_trafico: int  # 1-5, 5 es máximo tráfico
    tiempo_adicional: int  # minutos adicionales por tráfico
    factor_velocidad: float  # factor de reducción de velocidad (0.1-1.0)

@dataclass
class PatronTrafico:
    """Representa patrones de tráfico por día y hora"""
    dia_semana: int  # 0-6 (lunes-domingo)
    hora: int  # 0-23
    nivel_promedio: float
    desviacion_estandar: float
    factor_congestion: float

class AnalizadorTrafico:
    """Analiza patrones de tráfico y predice condiciones futuras"""
    
    def __init__(self, api_key_google: str = None, api_key_here: str = None):
        self.api_key_google = api_key_google
        self.api_key_here = api_key_here
        self.patrones_trafico = {}
        self.historial_trafico = []
        
    def obtener_trafico_tiempo_real(self, origen: Tuple[float, float], 
                                  destino: Tuple[float, float]) -> CondicionTrafico:
        """Obtiene condiciones de tráfico en tiempo real"""
        
        # Intentar con Google Maps API
        if self.api_key_google:
            try:
                return self._obtener_trafico_google(origen, destino)
            except Exception as e:
                print(f"Error Google Maps API: {e}")
        
        # Intentar con HERE API
        if self.api_key_here:
            try:
                return self._obtener_trafico_here(origen, destino)
            except Exception as e:
                print(f"Error HERE API: {e}")
        
        # Fallback: estimación basada en hora del día
        return self._estimar_trafico_por_hora(origen, destino)
    
    def _obtener_trafico_google(self, origen: Tuple[float, float], 
                              destino: Tuple[float, float]) -> CondicionTrafico:
        """Obtiene tráfico usando Google Maps API"""
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        params = {
            'origins': f"{origen[0]},{origen[1]}",
            'destinations': f"{destino[0]},{destino[1]}",
            'departure_time': int(datetime.now().timestamp()),
            'traffic_model': 'best_guess',
            'key': self.api_key_google
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK':
            elemento = data['rows'][0]['elements'][0]
            
            # Tiempo sin tráfico
            tiempo_normal = elemento['duration']['value'] / 60
            
            # Tiempo con tráfico
            tiempo_trafico = elemento['duration_in_traffic']['value'] / 60
            
            tiempo_adicional = int(tiempo_trafico - tiempo_normal)
            factor_velocidad = tiempo_normal / tiempo_trafico if tiempo_trafico > 0 else 1.0
            
            # Calcular nivel de tráfico (1-5)
            if tiempo_adicional < 5:
                nivel = 1
            elif tiempo_adicional < 15:
                nivel = 2
            elif tiempo_adicional < 30:
                nivel = 3
            elif tiempo_adicional < 60:
                nivel = 4
            else:
                nivel = 5
            
            return CondicionTrafico(
                timestamp=datetime.now(),
                nivel_trafico=nivel,
                tiempo_adicional=tiempo_adicional,
                factor_velocidad=factor_velocidad
            )
        
        raise Exception("Error en respuesta de Google Maps API")
    
    def _obtener_trafico_here(self, origen: Tuple[float, float], 
                            destino: Tuple[float, float]) -> CondicionTrafico:
        """Obtiene tráfico usando HERE API"""
        url = "https://route.ls.hereapi.com/routing/7.2/calculateroute.json"
        
        params = {
            'waypoint0': f"geo!{origen[0]},{origen[1]}",
            'waypoint1': f"geo!{destino[0]},{destino[1]}",
            'mode': 'fastest;car;traffic:enabled',
            'apikey': self.api_key_here
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'response' in data and data['response']['route']:
            route = data['response']['route'][0]
            summary = route['summary']
            
            # Calcular métricas de tráfico
            tiempo_base = summary['baseTime'] / 60  # minutos
            tiempo_trafico = summary['travelTime'] / 60  # minutos
            
            tiempo_adicional = int(tiempo_trafico - tiempo_base)
            factor_velocidad = tiempo_base / tiempo_trafico if tiempo_trafico > 0 else 1.0
            
            # Calcular nivel de tráfico
            nivel = min(5, max(1, int(tiempo_adicional / 10) + 1))
            
            return CondicionTrafico(
                timestamp=datetime.now(),
                nivel_trafico=nivel,
                tiempo_adicional=tiempo_adicional,
                factor_velocidad=factor_velocidad
            )
        
        raise Exception("Error en respuesta de HERE API")
    
    def _estimar_trafico_por_hora(self, origen: Tuple[float, float], 
                                destino: Tuple[float, float]) -> CondicionTrafico:
        """Estimación de tráfico basada en patrones históricos"""
        ahora = datetime.now()
        dia_semana = ahora.weekday()
        hora = ahora.hour
        
        # Patrones típicos de tráfico por hora
        patrones_base = {
            # Hora: (nivel_trafico, tiempo_adicional_minutos)
            6: (2, 5),   # 6 AM - inicio día laboral
            7: (4, 20),  # 7 AM - hora pico mañana
            8: (5, 35),  # 8 AM - máximo tráfico mañana
            9: (3, 15),  # 9 AM - disminuye
            10: (2, 8),  # 10 AM - normal
            11: (2, 5),  # 11 AM - normal
            12: (3, 12), # 12 PM - hora almuerzo
            13: (2, 6),  # 1 PM - normal
            14: (2, 5),  # 2 PM - normal
            15: (2, 7),  # 3 PM - normal
            16: (3, 15), # 4 PM - inicio hora pico tarde
            17: (4, 25), # 5 PM - hora pico tarde
            18: (5, 30), # 6 PM - máximo tráfico tarde
            19: (4, 20), # 7 PM - disminuye
            20: (3, 10), # 8 PM - normal
            21: (2, 5),  # 9 PM - normal
            22: (1, 2),  # 10 PM - poco tráfico
            23: (1, 1),  # 11 PM - poco tráfico
        }
        
        # Ajustar para fines de semana
        if dia_semana >= 5:  # Sábado o domingo
            nivel_base, tiempo_base = patrones_base.get(hora, (1, 2))
            nivel_base = max(1, nivel_base - 1)
            tiempo_base = max(1, tiempo_base // 2)
        else:
            nivel_base, tiempo_base = patrones_base.get(hora, (1, 2))
        
        factor_velocidad = 1.0 - (tiempo_base / 100)  # Estimación
        
        return CondicionTrafico(
            timestamp=ahora,
            nivel_trafico=nivel_base,
            tiempo_adicional=tiempo_base,
            factor_velocidad=max(0.3, factor_velocidad)
        )
    
    def predecir_trafico_futuro(self, origen: Tuple[float, float], 
                              destino: Tuple[float, float],
                              hora_destino: datetime) -> CondicionTrafico:
        """Predice condiciones de tráfico para una hora específica"""
        
        # Usar patrones históricos para predecir
        dia_semana = hora_destino.weekday()
        hora = hora_destino.hour
        
        # Crear clave para el patrón
        clave_patron = f"{dia_semana}_{hora}"
        
        if clave_patron in self.patrones_trafico:
            patron = self.patrones_trafico[clave_patron]
            
            # Generar predicción con variabilidad
            nivel_predicho = int(np.random.normal(patron.nivel_promedio, patron.desviacion_estandar))
            nivel_predicho = max(1, min(5, nivel_predicho))
            
            tiempo_adicional = int(nivel_predicho * 8)  # Estimación
            factor_velocidad = 1.0 - (tiempo_adicional / 100)
            
            return CondicionTrafico(
                timestamp=hora_destino,
                nivel_trafico=nivel_predicho,
                tiempo_adicional=tiempo_adicional,
                factor_velocidad=max(0.3, factor_velocidad)
            )
        
        # Fallback a estimación por hora
        return self._estimar_trafico_por_hora(origen, destino)
    
    def analizar_patrones_historicos(self, datos_historicos: List[Dict]):
        """Analiza patrones históricos de tráfico"""
        
        # Agrupar por día de semana y hora
        patrones = defaultdict(list)
        
        for dato in datos_historicos:
            timestamp = datetime.fromisoformat(dato['timestamp'])
            dia_semana = timestamp.weekday()
            hora = timestamp.hour
            nivel_trafico = dato['nivel_trafico']
            
            clave = f"{dia_semana}_{hora}"
            patrones[clave].append(nivel_trafico)
        
        # Calcular estadísticas para cada patrón
        for clave, niveles in patrones.items():
            if len(niveles) > 1:
                nivel_promedio = np.mean(niveles)
                desviacion = np.std(niveles)
                factor_congestion = nivel_promedio / 5.0  # Normalizar a 0-1
                
                self.patrones_trafico[clave] = PatronTrafico(
                    dia_semana=int(clave.split('_')[0]),
                    hora=int(clave.split('_')[1]),
                    nivel_promedio=nivel_promedio,
                    desviacion_estandar=desviacion,
                    factor_congestion=factor_congestion
                )

class OptimizadorHorarios:
    """Optimiza rutas considerando horarios de entrega y restricciones"""
    
    def __init__(self, analizador_trafico: AnalizadorTrafico):
        self.analizador_trafico = analizador_trafico
        
    def calcular_ventana_tiempo_optima(self, punto_entrega, ubicacion_origen: Tuple[float, float]) -> Tuple[datetime, datetime]:
        """Calcula la ventana de tiempo óptima para llegar a un punto de entrega"""
        
        # Calcular tiempo mínimo de viaje
        distancia = self._calcular_distancia_haversine(ubicacion_origen, (punto_entrega.latitud, punto_entrega.longitud))
        tiempo_minimo = distancia * 2  # Estimación conservadora en minutos
        
        # Calcular hora de apertura
        hora_apertura = datetime.strptime(punto_entrega.horario_apertura, "%H:%M").time()
        hora_cierre = datetime.strptime(punto_entrega.horario_cierre, "%H:%M").time()
        
        # Calcular hora óptima de salida
        hora_salida_optima = datetime.combine(datetime.today(), hora_apertura) - timedelta(minutes=tiempo_minimo)
        
        # Ajustar por tráfico previsto
        condicion_trafico = self.analizador_trafico.predecir_trafico_futuro(
            ubicacion_origen, (punto_entrega.latitud, punto_entrega.longitud), hora_salida_optima
        )
        
        tiempo_adicional = condicion_trafico.tiempo_adicional
        hora_salida_ajustada = hora_salida_optima - timedelta(minutes=tiempo_adicional)
        
        # Calcular hora de llegada estimada
        hora_llegada = hora_salida_ajustada + timedelta(minutes=tiempo_minimo + tiempo_adicional)
        
        return hora_salida_ajustada, hora_llegada
    
    def _calcular_distancia_haversine(self, punto1: Tuple[float, float], punto2: Tuple[float, float]) -> float:
        """Calcula distancia entre dos puntos usando fórmula de Haversine"""
        import math
        
        lat1, lon1 = punto1
        lat2, lon2 = punto2
        
        R = 6371  # Radio de la Tierra en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def optimizar_secuencia_entregas(self, puntos_entrega: List, vehiculo_ubicacion: Tuple[float, float]) -> List:
        """Optimiza la secuencia de entregas considerando horarios y tráfico"""
        
        # Calcular ventanas de tiempo para cada punto
        ventanas_tiempo = []
        for punto in puntos_entrega:
            hora_salida, hora_llegada = self.calcular_ventana_tiempo_optima(punto, vehiculo_ubicacion)
            ventanas_tiempo.append({
                'punto': punto,
                'hora_salida': hora_salida,
                'hora_llegada': hora_llegada,
                'prioridad': punto.prioridad,
                'tipo_entrega': punto.tipo_entrega
            })
        
        # Ordenar por prioridad y factibilidad horaria
        ventanas_tiempo.sort(key=lambda x: (
            -x['prioridad'],  # Mayor prioridad primero
            x['hora_salida']   # Horarios más tempranos primero
        ))
        
        # Filtrar puntos factibles
        puntos_factibles = []
        hora_actual = datetime.now()
        
        for ventana in ventanas_tiempo:
            if ventana['hora_salida'] >= hora_actual:
                puntos_factibles.append(ventana['punto'])
                hora_actual = ventana['hora_llegada'] + timedelta(minutes=ventana['punto'].tiempo_servicio)
        
        return puntos_factibles

def ejemplo_uso_trafico():
    """Ejemplo de uso del sistema de análisis de tráfico"""
    
    print("=== Análisis de Tráfico y Optimización de Horarios ===\n")
    
    # Crear analizador de tráfico
    analizador = AnalizadorTrafico()
    
    # Puntos de ejemplo
    origen = (-12.0464, -77.0428)  # Lima, Perú
    destino = (-12.0564, -77.0328)
    
    # Obtener condiciones actuales de tráfico
    print("1. Condiciones actuales de tráfico:")
    condicion_actual = analizador.obtener_trafico_tiempo_real(origen, destino)
    print(f"   Nivel de tráfico: {condicion_actual.nivel_trafico}/5")
    print(f"   Tiempo adicional: {condicion_actual.tiempo_adicional} minutos")
    print(f"   Factor de velocidad: {condicion_actual.factor_velocidad:.2f}")
    
    # Predecir tráfico futuro
    print("\n2. Predicción de tráfico para mañana 8:00 AM:")
    hora_futura = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    condicion_futura = analizador.predecir_trafico_futuro(origen, destino, hora_futura)
    print(f"   Nivel predicho: {condicion_futura.nivel_trafico}/5")
    print(f"   Tiempo adicional estimado: {condicion_futura.tiempo_adicional} minutos")
    
    # Ejemplo de optimización de horarios
    print("\n3. Optimización de horarios:")
    from logistica_optimizacion_rutas import PuntoEntrega, TipoEntrega
    
    punto_ejemplo = PuntoEntrega(
        id="P001", direccion="Av. Principal 123", latitud=-12.0564, longitud=-77.0328,
        horario_apertura="09:00", horario_cierre="17:00", tiempo_servicio=15,
        tipo_entrega=TipoEntrega.URGENTE, peso=5.0, volumen=0.1, prioridad=5
    )
    
    optimizador_horarios = OptimizadorHorarios(analizador)
    hora_salida, hora_llegada = optimizador_horarios.calcular_ventana_tiempo_optima(punto_ejemplo, origen)
    
    print(f"   Punto: {punto_ejemplo.direccion}")
    print(f"   Hora óptima de salida: {hora_salida.strftime('%H:%M')}")
    print(f"   Hora estimada de llegada: {hora_llegada.strftime('%H:%M')}")
    print(f"   Ventana de entrega: {punto_ejemplo.horario_apertura} - {punto_ejemplo.horario_cierre}")

if __name__ == "__main__":
    ejemplo_uso_trafico()



