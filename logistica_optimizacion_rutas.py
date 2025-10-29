"""
Sistema de Optimización de Rutas Logísticas
==========================================

Este sistema optimiza rutas de entrega considerando:
- Distancias y tiempos de viaje
- Tráfico en tiempo real
- Horarios de entrega
- Costos por kilómetro
- Restricciones de vehículos y conductores

Autor: Sistema de Optimización Logística
Fecha: 2024
"""

import json
import math
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import heapq
from collections import defaultdict

class TipoVehiculo(Enum):
    MOTOCICLETA = "motocicleta"
    FURGON = "furgon"
    CAMION_PEQUEÑO = "camion_pequeño"
    CAMION_GRANDE = "camion_grande"

class TipoEntrega(Enum):
    URGENTE = "urgente"
    ESTANDAR = "estandar"
    PROGRAMADA = "programada"

@dataclass
class PuntoEntrega:
    """Representa un punto de entrega con sus características"""
    id: str
    direccion: str
    latitud: float
    longitud: float
    horario_apertura: str  # "08:00"
    horario_cierre: str    # "18:00"
    tiempo_servicio: int   # minutos
    tipo_entrega: TipoEntrega
    peso: float = 0.0      # kg
    volumen: float = 0.0   # m³
    prioridad: int = 1     # 1-5, 5 es máxima prioridad

@dataclass
class Vehiculo:
    """Representa un vehículo de entrega"""
    id: str
    tipo: TipoVehiculo
    capacidad_peso: float  # kg
    capacidad_volumen: float  # m³
    consumo_combustible: float  # L/km
    costo_por_km: float  # USD/km
    velocidad_promedio: float  # km/h
    conductor_id: str
    ubicacion_actual: Tuple[float, float]  # (lat, lng)

@dataclass
class Ruta:
    """Representa una ruta optimizada"""
    vehiculo_id: str
    puntos_entrega: List[PuntoEntrega]
    distancia_total: float  # km
    tiempo_total: int  # minutos
    costo_total: float  # USD
    combustible_consumido: float  # L
    horario_salida: datetime
    horario_llegada: datetime

class OptimizadorRutas:
    """Clase principal para optimización de rutas logísticas"""
    
    def __init__(self, api_key_maps: str = None):
        self.api_key_maps = api_key_maps
        self.matriz_distancias = {}
        self.matriz_tiempos = {}
        
    def calcular_distancia_haversine(self, punto1: Tuple[float, float], 
                                   punto2: Tuple[float, float]) -> float:
        """Calcula distancia entre dos puntos usando fórmula de Haversine"""
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
    
    def obtener_tiempo_viaje_api(self, origen: Tuple[float, float], 
                                destino: Tuple[float, float], 
                                hora_salida: datetime) -> Tuple[float, int]:
        """
        Obtiene tiempo de viaje real usando APIs externas
        Retorna: (distancia_km, tiempo_minutos)
        """
        if not self.api_key_maps:
            # Fallback a cálculo estimado
            distancia = self.calcular_distancia_haversine(origen, destino)
            tiempo = distancia * 2  # Estimación: 30 km/h promedio
            return distancia, int(tiempo)
        
        try:
            # Google Maps API
            url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': f"{origen[0]},{origen[1]}",
                'destinations': f"{destino[0]},{destino[1]}",
                'departure_time': int(hora_salida.timestamp()),
                'traffic_model': 'best_guess',
                'key': self.api_key_maps
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                elemento = data['rows'][0]['elements'][0]
                distancia_km = elemento['distance']['value'] / 1000
                tiempo_segundos = elemento['duration_in_traffic']['value']
                return distancia_km, int(tiempo_segundos / 60)
            
        except Exception as e:
            print(f"Error en API: {e}")
        
        # Fallback
        distancia = self.calcular_distancia_haversine(origen, destino)
        tiempo = distancia * 2
        return distancia, int(tiempo)
    
    def algoritmo_vrp_basico(self, vehiculos: List[Vehiculo], 
                           puntos_entrega: List[PuntoEntrega],
                           hora_inicio: datetime) -> List[Ruta]:
        """
        Algoritmo básico de Vehicle Routing Problem (VRP)
        """
        rutas = []
        puntos_sin_asignar = puntos_entrega.copy()
        
        for vehiculo in vehiculos:
            if not puntos_sin_asignar:
                break
                
            ruta_puntos = []
            ubicacion_actual = vehiculo.ubicacion_actual
            tiempo_actual = hora_inicio
            distancia_total = 0
            costo_total = 0
            combustible_total = 0
            
            # Algoritmo greedy: seleccionar punto más cercano
            while puntos_sin_asignar:
                mejor_punto = None
                mejor_costo = float('inf')
                
                for punto in puntos_sin_asignar:
                    # Verificar capacidad
                    peso_total = sum(p.peso for p in ruta_puntos) + punto.peso
                    volumen_total = sum(p.volumen for p in ruta_puntos) + punto.volumen
                    
                    if (peso_total > vehiculo.capacidad_peso or 
                        volumen_total > vehiculo.capacidad_volumen):
                        continue
                    
                    # Calcular costo de ir a este punto
                    distancia, tiempo = self.obtener_tiempo_viaje_api(
                        ubicacion_actual, (punto.latitud, punto.longitud), tiempo_actual
                    )
                    
                    costo_viaje = distancia * vehiculo.costo_por_km
                    costo_combustible = distancia * vehiculo.consumo_combustible * 1.5  # USD/L
                    costo_total_punto = costo_viaje + costo_combustible
                    
                    # Penalizar por prioridad baja
                    if punto.prioridad < 3:
                        costo_total_punto *= 1.2
                    
                    if costo_total_punto < mejor_costo:
                        mejor_costo = costo_total_punto
                        mejor_punto = punto
                
                if mejor_punto is None:
                    break
                
                # Agregar punto a la ruta
                distancia, tiempo = self.obtener_tiempo_viaje_api(
                    ubicacion_actual, (mejor_punto.latitud, mejor_punto.longitud), tiempo_actual
                )
                
                ruta_puntos.append(mejor_punto)
                puntos_sin_asignar.remove(mejor_punto)
                
                distancia_total += distancia
                costo_total += distancia * vehiculo.costo_por_km
                combustible_total += distancia * vehiculo.consumo_combustible
                
                tiempo_actual += timedelta(minutes=tiempo + mejor_punto.tiempo_servicio)
                ubicacion_actual = (mejor_punto.latitud, mejor_punto.longitud)
            
            if ruta_puntos:
                tiempo_total = int((tiempo_actual - hora_inicio).total_seconds() / 60)
                ruta = Ruta(
                    vehiculo_id=vehiculo.id,
                    puntos_entrega=ruta_puntos,
                    distancia_total=distancia_total,
                    tiempo_total=tiempo_total,
                    costo_total=costo_total,
                    combustible_consumido=combustible_total,
                    horario_salida=hora_inicio,
                    horario_llegada=tiempo_actual
                )
                rutas.append(ruta)
        
        return rutas
    
    def optimizar_con_restricciones_horario(self, vehiculos: List[Vehiculo],
                                          puntos_entrega: List[PuntoEntrega],
                                          hora_inicio: datetime) -> List[Ruta]:
        """
        Optimización considerando horarios de entrega y restricciones
        """
        # Filtrar puntos por horarios factibles
        puntos_factibles = []
        for punto in puntos_entrega:
            hora_apertura = datetime.strptime(punto.horario_apertura, "%H:%M").time()
            hora_cierre = datetime.strptime(punto.horario_cierre, "%H:%M").time()
            
            # Verificar si es posible llegar en horario
            tiempo_minimo = self.calcular_distancia_haversine(
                vehiculos[0].ubicacion_actual, (punto.latitud, punto.longitud)
            ) * 2  # Estimación conservadora
            
            hora_llegada_estimada = (hora_inicio + timedelta(minutes=tiempo_minimo)).time()
            
            if hora_apertura <= hora_llegada_estimada <= hora_cierre:
                puntos_factibles.append(punto)
        
        return self.algoritmo_vrp_basico(vehiculos, puntos_factibles, hora_inicio)
    
    def calcular_metricas_optimizacion(self, rutas: List[Ruta]) -> Dict:
        """Calcula métricas de optimización"""
        total_distancia = sum(r.distancia_total for r in rutas)
        total_tiempo = sum(r.tiempo_total for r in rutas)
        total_costo = sum(r.costo_total for r in rutas)
        total_combustible = sum(r.combustible_consumido for r in rutas)
        
        return {
            'total_distancia_km': total_distancia,
            'total_tiempo_minutos': total_tiempo,
            'total_costo_usd': total_costo,
            'total_combustible_litros': total_combustible,
            'numero_vehiculos_usados': len(rutas),
            'promedio_costo_por_km': total_costo / total_distancia if total_distancia > 0 else 0,
            'eficiencia_combustible': total_distancia / total_combustible if total_combustible > 0 else 0
        }

def crear_ejemplo_practico():
    """Crea un ejemplo práctico de optimización de rutas"""
    
    # Crear puntos de entrega ejemplo
    puntos_entrega = [
        PuntoEntrega(
            id="P001", direccion="Av. Principal 123", latitud=-12.0464, longitud=-77.0428,
            horario_apertura="09:00", horario_cierre="17:00", tiempo_servicio=15,
            tipo_entrega=TipoEntrega.URGENTE, peso=5.0, volumen=0.1, prioridad=5
        ),
        PuntoEntrega(
            id="P002", direccion="Calle Comercio 456", latitud=-12.0564, longitud=-77.0328,
            horario_apertura="08:00", horario_cierre="18:00", tiempo_servicio=20,
            tipo_entrega=TipoEntrega.ESTANDAR, peso=10.0, volumen=0.2, prioridad=3
        ),
        PuntoEntrega(
            id="P003", direccion="Plaza Central 789", latitud=-12.0364, longitud=-77.0528,
            horario_apertura="10:00", horario_cierre="16:00", tiempo_servicio=25,
            tipo_entrega=TipoEntrega.PROGRAMADA, peso=15.0, volumen=0.3, prioridad=2
        ),
        PuntoEntrega(
            id="P004", direccion="Zona Industrial A", latitud=-12.0664, longitud=-77.0228,
            horario_apertura="07:00", horario_cierre="19:00", tiempo_servicio=30,
            tipo_entrega=TipoEntrega.ESTANDAR, peso=25.0, volumen=0.5, prioridad=4
        ),
        PuntoEntrega(
            id="P005", direccion="Centro Comercial B", latitud=-12.0264, longitud=-77.0628,
            horario_apertura="09:30", horario_cierre="21:00", tiempo_servicio=20,
            tipo_entrega=TipoEntrega.URGENTE, peso=8.0, volumen=0.15, prioridad=5
        )
    ]
    
    # Crear vehículos ejemplo
    vehiculos = [
        Vehiculo(
            id="V001", tipo=TipoVehiculo.FURGON, capacidad_peso=500, capacidad_volumen=10,
            consumo_combustible=0.12, costo_por_km=0.8, velocidad_promedio=35,
            conductor_id="C001", ubicacion_actual=(-12.0464, -77.0428)
        ),
        Vehiculo(
            id="V002", tipo=TipoVehiculo.CAMION_PEQUEÑO, capacidad_peso=1000, capacidad_volumen=20,
            consumo_combustible=0.15, costo_por_km=1.2, velocidad_promedio=30,
            conductor_id="C002", ubicacion_actual=(-12.0464, -77.0428)
        )
    ]
    
    # Crear optimizador
    optimizador = OptimizadorRutas()
    
    # Optimizar rutas
    hora_inicio = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    rutas_optimizadas = optimizador.optimizar_con_restricciones_horario(
        vehiculos, puntos_entrega, hora_inicio
    )
    
    # Calcular métricas
    metricas = optimizador.calcular_metricas_optimizacion(rutas_optimizadas)
    
    return rutas_optimizadas, metricas

if __name__ == "__main__":
    print("=== Sistema de Optimización de Rutas Logísticas ===\n")
    
    # Ejecutar ejemplo práctico
    rutas, metricas = crear_ejemplo_practico()
    
    print("RUTAS OPTIMIZADAS:")
    print("=" * 50)
    
    for i, ruta in enumerate(rutas, 1):
        print(f"\nRuta {i} - Vehículo {ruta.vehiculo_id}:")
        print(f"  Distancia total: {ruta.distancia_total:.2f} km")
        print(f"  Tiempo total: {ruta.tiempo_total} minutos")
        print(f"  Costo total: ${ruta.costo_total:.2f}")
        print(f"  Combustible: {ruta.combustible_consumido:.2f} L")
        print(f"  Horario salida: {ruta.horario_salida.strftime('%H:%M')}")
        print(f"  Horario llegada: {ruta.horario_llegada.strftime('%H:%M')}")
        print("  Puntos de entrega:")
        for punto in ruta.puntos_entrega:
            print(f"    - {punto.id}: {punto.direccion} (Prioridad: {punto.prioridad})")
    
    print("\nMÉTRICAS GENERALES:")
    print("=" * 50)
    for clave, valor in metricas.items():
        if isinstance(valor, float):
            print(f"  {clave}: {valor:.2f}")
        else:
            print(f"  {clave}: {valor}")



