"""
Sistema Avanzado de Optimización Logística - Versión Mejorada
============================================================

Mejoras implementadas:
- Algoritmos genéticos para VRP
- Machine Learning para predicción de tráfico
- Optimización multi-objetivo
- Análisis de sensibilidad
- Sistema de alertas inteligente
- Visualización avanzada
"""

import json
import math
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class TipoVehiculo(Enum):
    MOTOCICLETA = "motocicleta"
    FURGON = "furgon"
    CAMION_PEQUEÑO = "camion_pequeño"
    CAMION_GRANDE = "camion_grande"
    BICICLETA = "bicicleta"
    VAN_ELECTRICA = "van_electrica"

class TipoEntrega(Enum):
    URGENTE = "urgente"
    ESTANDAR = "estandar"
    PROGRAMADA = "programada"
    FRAGIL = "fragil"
    REFRIGERADA = "refrigerada"

class Prioridad(Enum):
    CRITICA = 5
    ALTA = 4
    MEDIA = 3
    BAJA = 2
    MINIMA = 1

@dataclass
class PuntoEntrega:
    """Punto de entrega con características avanzadas"""
    id: str
    direccion: str
    latitud: float
    longitud: float
    horario_apertura: str
    horario_cierre: str
    tiempo_servicio: int
    tipo_entrega: TipoEntrega
    peso: float = 0.0
    volumen: float = 0.0
    prioridad: int = 1
    valor_pedido: float = 0.0
    cliente_id: str = ""
    requiere_firma: bool = False
    instrucciones_especiales: str = ""
    zona_riesgo: bool = False
    costo_penalizacion: float = 0.0

@dataclass
class Vehiculo:
    """Vehículo con características avanzadas"""
    id: str
    tipo: TipoVehiculo
    capacidad_peso: float
    capacidad_volumen: float
    consumo_combustible: float
    costo_por_km: float
    velocidad_promedio: float
    conductor_id: str
    ubicacion_actual: Tuple[float, float]
    costo_hora_conductor: float = 15.0
    costo_mantenimiento_por_km: float = 0.25
    emisiones_co2_por_km: float = 0.2
    autonomia_km: float = 500.0
    requiere_licencia_especial: bool = False
    disponible_24h: bool = False
    equipamiento_especial: List[str] = field(default_factory=list)

@dataclass
class RutaOptimizada:
    """Ruta optimizada con métricas avanzadas"""
    vehiculo_id: str
    puntos_entrega: List[PuntoEntrega]
    secuencia_optima: List[int]
    distancia_total: float
    tiempo_total: int
    costo_total: float
    combustible_consumido: float
    emisiones_co2: float
    horario_salida: datetime
    horario_llegada: datetime
    satisfaccion_cliente: float
    riesgo_total: float
    eficiencia_energetica: float
    factor_confiabilidad: float

class AlgoritmoGeneticoVRP:
    """Algoritmo genético para optimización de VRP"""
    
    def __init__(self, poblacion_size=100, generaciones=200, tasa_mutacion=0.1, tasa_cruza=0.8):
        self.poblacion_size = poblacion_size
        self.generaciones = generaciones
        self.tasa_mutacion = tasa_mutacion
        self.tasa_cruza = tasa_cruza
        self.mejor_solucion = None
        self.historial_fitness = []
        
    def crear_individuo(self, puntos_entrega: List[PuntoEntrega], vehiculos: List[Vehiculo]) -> Dict:
        """Crea un individuo (solución) aleatoria"""
        # Crear secuencia aleatoria de puntos
        secuencia = list(range(len(puntos_entrega)))
        random.shuffle(secuencia)
        
        # Asignar puntos a vehículos de forma aleatoria
        asignaciones = {}
        puntos_por_vehiculo = len(puntos_entrega) // len(vehiculos)
        
        for i, vehiculo in enumerate(vehiculos):
            inicio = i * puntos_por_vehiculo
            fin = inicio + puntos_por_vehiculo
            if i == len(vehiculos) - 1:  # Último vehículo toma los puntos restantes
                fin = len(puntos_entrega)
            
            asignaciones[vehiculo.id] = secuencia[inicio:fin]
        
        return {
            'secuencia': secuencia,
            'asignaciones': asignaciones,
            'fitness': 0.0
        }
    
    def calcular_fitness(self, individuo: Dict, puntos_entrega: List[PuntoEntrega], 
                        vehiculos: List[Vehiculo]) -> float:
        """Calcula el fitness (calidad) de una solución"""
        try:
            costo_total = 0.0
            penalizaciones = 0.0
            
            for vehiculo_id, puntos_asignados in individuo['asignaciones'].items():
                vehiculo = next(v for v in vehiculos if v.id == vehiculo_id)
                
                if not puntos_asignados:
                    continue
                
                # Calcular peso y volumen total
                peso_total = sum(puntos_entrega[i].peso for i in puntos_asignados)
                volumen_total = sum(puntos_entrega[i].volumen for i in puntos_asignados)
                
                # Penalizar si excede capacidad
                if peso_total > vehiculo.capacidad_peso:
                    penalizaciones += (peso_total - vehiculo.capacidad_peso) * 100
                
                if volumen_total > vehiculo.capacidad_volumen:
                    penalizaciones += (volumen_total - vehiculo.capacidad_volumen) * 50
                
                # Calcular distancia y costo
                distancia = self._calcular_distancia_ruta(puntos_asignados, puntos_entrega, vehiculo)
                costo_ruta = distancia * vehiculo.costo_por_km
                costo_total += costo_ruta
            
            # Fitness es inverso del costo total + penalizaciones
            fitness = 1.0 / (costo_total + penalizaciones + 1.0)
            
            return fitness
            
        except Exception as e:
            return 0.001  # Fitness muy bajo para soluciones inválidas
    
    def _calcular_distancia_ruta(self, puntos_indices: List[int], 
                               puntos_entrega: List[PuntoEntrega], 
                               vehiculo: Vehiculo) -> float:
        """Calcula distancia total de una ruta"""
        if not puntos_indices:
            return 0.0
        
        distancia_total = 0.0
        ubicacion_actual = vehiculo.ubicacion_actual
        
        for punto_idx in puntos_indices:
            punto = puntos_entrega[punto_idx]
            distancia = self._distancia_haversine(ubicacion_actual, (punto.latitud, punto.longitud))
            distancia_total += distancia
            ubicacion_actual = (punto.latitud, punto.longitud)
        
        return distancia_total
    
    def _distancia_haversine(self, punto1: Tuple[float, float], punto2: Tuple[float, float]) -> float:
        """Calcula distancia entre dos puntos"""
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
    
    def cruzar(self, padre1: Dict, padre2: Dict) -> Tuple[Dict, Dict]:
        """Cruza dos individuos para crear descendencia"""
        # Cruza de orden (Order Crossover)
        size = len(padre1['secuencia'])
        
        # Seleccionar segmento aleatorio
        inicio = random.randint(0, size - 1)
        fin = random.randint(inicio, size)
        
        # Crear hijo1
        hijo1_secuencia = [-1] * size
        hijo1_secuencia[inicio:fin] = padre1['secuencia'][inicio:fin]
        
        # Completar con elementos del padre2
        idx_hijo = 0
        for elemento in padre2['secuencia']:
            if elemento not in hijo1_secuencia:
                while hijo1_secuencia[idx_hijo] != -1:
                    idx_hijo += 1
                hijo1_secuencia[idx_hijo] = elemento
        
        # Crear hijo2 de forma similar
        hijo2_secuencia = [-1] * size
        hijo2_secuencia[inicio:fin] = padre2['secuencia'][inicio:fin]
        
        idx_hijo = 0
        for elemento in padre1['secuencia']:
            if elemento not in hijo2_secuencia:
                while hijo2_secuencia[idx_hijo] != -1:
                    idx_hijo += 1
                hijo2_secuencia[idx_hijo] = elemento
        
        # Reasignar puntos a vehículos
        hijo1 = self._reasignar_puntos(hijo1_secuencia, padre1['asignaciones'])
        hijo2 = self._reasignar_puntos(hijo2_secuencia, padre2['asignaciones'])
        
        return hijo1, hijo2
    
    def _reasignar_puntos(self, secuencia: List[int], asignaciones_originales: Dict) -> Dict:
        """Reasigna puntos a vehículos manteniendo la estructura"""
        nueva_asignacion = {}
        puntos_por_vehiculo = len(secuencia) // len(asignaciones_originales)
        
        vehiculos = list(asignaciones_originales.keys())
        for i, vehiculo_id in enumerate(vehiculos):
            inicio = i * puntos_por_vehiculo
            fin = inicio + puntos_por_vehiculo
            if i == len(vehiculos) - 1:
                fin = len(secuencia)
            
            nueva_asignacion[vehiculo_id] = secuencia[inicio:fin]
        
        return {
            'secuencia': secuencia,
            'asignaciones': nueva_asignacion,
            'fitness': 0.0
        }
    
    def mutar(self, individuo: Dict) -> Dict:
        """Aplica mutación a un individuo"""
        if random.random() < self.tasa_mutacion:
            # Intercambiar dos elementos aleatorios
            secuencia = individuo['secuencia'].copy()
            i, j = random.sample(range(len(secuencia)), 2)
            secuencia[i], secuencia[j] = secuencia[j], secuencia[i]
            
            # Reasignar puntos
            individuo_mutado = self._reasignar_puntos(secuencia, individuo['asignaciones'])
            return individuo_mutado
        
        return individuo
    
    def seleccionar_padres(self, poblacion: List[Dict]) -> List[Dict]:
        """Selecciona padres usando torneo"""
        padres = []
        
        for _ in range(self.poblacion_size):
            # Torneo de tamaño 3
            candidatos = random.sample(poblacion, min(3, len(poblacion)))
            mejor_candidato = max(candidatos, key=lambda x: x['fitness'])
            padres.append(mejor_candidato)
        
        return padres
    
    def optimizar(self, puntos_entrega: List[PuntoEntrega], vehiculos: List[Vehiculo]) -> Dict:
        """Ejecuta el algoritmo genético"""
        print("🧬 Iniciando algoritmo genético para VRP...")
        
        # Crear población inicial
        poblacion = []
        for _ in range(self.poblacion_size):
            individuo = self.crear_individuo(puntos_entrega, vehiculos)
            individuo['fitness'] = self.calcular_fitness(individuo, puntos_entrega, vehiculos)
            poblacion.append(individuo)
        
        # Evolución
        for generacion in range(self.generaciones):
            # Calcular fitness
            for individuo in poblacion:
                individuo['fitness'] = self.calcular_fitness(individuo, puntos_entrega, vehiculos)
            
            # Encontrar mejor individuo
            mejor_individuo = max(poblacion, key=lambda x: x['fitness'])
            self.historial_fitness.append(mejor_individuo['fitness'])
            
            if generacion % 50 == 0:
                print(f"   Generación {generacion}: Fitness = {mejor_individuo['fitness']:.6f}")
            
            # Seleccionar padres
            padres = self.seleccionar_padres(poblacion)
            
            # Crear nueva población
            nueva_poblacion = []
            
            # Elitismo: mantener el mejor individuo
            nueva_poblacion.append(mejor_individuo)
            
            # Generar descendencia
            while len(nueva_poblacion) < self.poblacion_size:
                padre1, padre2 = random.sample(padres, 2)
                
                if random.random() < self.tasa_cruza:
                    hijo1, hijo2 = self.cruzar(padre1, padre2)
                    hijo1 = self.mutar(hijo1)
                    hijo2 = self.mutar(hijo2)
                    nueva_poblacion.extend([hijo1, hijo2])
                else:
                    nueva_poblacion.extend([padre1, padre2])
            
            poblacion = nueva_poblacion[:self.poblacion_size]
        
        # Encontrar mejor solución final
        for individuo in poblacion:
            individuo['fitness'] = self.calcular_fitness(individuo, puntos_entrega, vehiculos)
        
        self.mejor_solucion = max(poblacion, key=lambda x: x['fitness'])
        
        print(f"✅ Algoritmo genético completado. Fitness final: {self.mejor_solucion['fitness']:.6f}")
        
        return self.mejor_solucion

class PredictorTraficoML:
    """Predictor de tráfico usando Machine Learning"""
    
    def __init__(self):
        self.modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.entrenado = False
        self.datos_historicos = []
        
    def agregar_dato_historico(self, timestamp: datetime, ubicacion: Tuple[float, float], 
                             nivel_trafico: int, condiciones_clima: Dict, dia_semana: int):
        """Agrega datos históricos para entrenamiento"""
        self.datos_historicos.append({
            'timestamp': timestamp,
            'latitud': ubicacion[0],
            'longitud': ubicacion[1],
            'nivel_trafico': nivel_trafico,
            'temperatura': condiciones_clima.get('temperatura', 20),
            'precipitacion': condiciones_clima.get('precipitacion', 0),
            'dia_semana': dia_semana,
            'hora': timestamp.hour,
            'es_festivo': condiciones_clima.get('es_festivo', False)
        })
    
    def preparar_datos_entrenamiento(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara datos para entrenamiento del modelo"""
        if len(self.datos_historicos) < 100:
            return None, None
        
        df = pd.DataFrame(self.datos_historicos)
        
        # Crear características
        X = df[['latitud', 'longitud', 'temperatura', 'precipitacion', 
                'dia_semana', 'hora', 'es_festivo']].values
        
        # Variable objetivo
        y = df['nivel_trafico'].values
        
        return X, y
    
    def entrenar_modelo(self):
        """Entrena el modelo de ML"""
        X, y = self.preparar_datos_entrenamiento()
        
        if X is None:
            print("⚠️ Datos insuficientes para entrenar el modelo")
            return False
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar características
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo
        self.modelo.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        score = self.modelo.score(X_test_scaled, y_test)
        print(f"🎯 Modelo entrenado. Score: {score:.3f}")
        
        self.entrenado = True
        return True
    
    def predecir_trafico(self, ubicacion: Tuple[float, float], timestamp: datetime, 
                        condiciones_clima: Dict) -> Dict:
        """Predice nivel de tráfico para ubicación y tiempo específicos"""
        if not self.entrenado:
            # Fallback a predicción basada en patrones
            return self._prediccion_fallback(timestamp)
        
        # Preparar características
        caracteristicas = np.array([[
            ubicacion[0], ubicacion[1],
            condiciones_clima.get('temperatura', 20),
            condiciones_clima.get('precipitacion', 0),
            timestamp.weekday(),
            timestamp.hour,
            condiciones_clima.get('es_festivo', False)
        ]])
        
        # Escalar características
        caracteristicas_scaled = self.scaler.transform(caracteristicas)
        
        # Predecir
        nivel_predicho = self.modelo.predict(caracteristicas_scaled)[0]
        
        # Calcular métricas adicionales
        tiempo_adicional = max(0, (nivel_predicho - 1) * 8)
        factor_velocidad = max(0.3, 1.0 - (tiempo_adicional / 100))
        
        return {
            'nivel_trafico': max(1, min(5, int(nivel_predicho))),
            'tiempo_adicional': int(tiempo_adicional),
            'factor_velocidad': factor_velocidad,
            'confianza': 0.8 if self.entrenado else 0.3
        }
    
    def _prediccion_fallback(self, timestamp: datetime) -> Dict:
        """Predicción de fallback basada en patrones"""
        hora = timestamp.hour
        dia_semana = timestamp.weekday()
        
        # Patrones típicos
        if 7 <= hora <= 9 or 17 <= hora <= 19:  # Horas pico
            nivel = 4 if dia_semana < 5 else 2
        elif 10 <= hora <= 16:  # Horas normales
            nivel = 2
        else:  # Horas de poco tráfico
            nivel = 1
        
        tiempo_adicional = max(0, (nivel - 1) * 8)
        factor_velocidad = max(0.3, 1.0 - (tiempo_adicional / 100))
        
        return {
            'nivel_trafico': nivel,
            'tiempo_adicional': tiempo_adicional,
            'factor_velocidad': factor_velocidad,
            'confianza': 0.3
        }

class OptimizadorMultiObjetivo:
    """Optimizador multi-objetivo para VRP"""
    
    def __init__(self):
        self.pesos_objetivos = {
            'costo': 0.3,
            'tiempo': 0.25,
            'satisfaccion_cliente': 0.2,
            'emisiones': 0.15,
            'riesgo': 0.1
        }
    
    def calcular_funcion_objetivo(self, ruta: RutaOptimizada) -> float:
        """Calcula función objetivo multi-objetivo"""
        objetivos = {
            'costo': ruta.costo_total,
            'tiempo': ruta.tiempo_total,
            'satisfaccion_cliente': 1.0 - ruta.satisfaccion_cliente,  # Minimizar insatisfacción
            'emisiones': ruta.emisiones_co2,
            'riesgo': ruta.riesgo_total
        }
        
        # Normalizar objetivos (simplificado)
        objetivos_normalizados = {}
        for objetivo, valor in objetivos.items():
            if objetivo == 'satisfaccion_cliente':
                objetivos_normalizados[objetivo] = valor
            else:
                objetivos_normalizados[objetivo] = valor / 100.0  # Normalización simple
        
        # Calcular función objetivo ponderada
        funcion_objetivo = sum(
            self.pesos_objetivos[objetivo] * valor_normalizado
            for objetivo, valor_normalizado in objetivos_normalizados.items()
        )
        
        return funcion_objetivo
    
    def optimizar_pareto(self, soluciones: List[RutaOptimizada]) -> List[RutaOptimizada]:
        """Encuentra frontera de Pareto"""
        # Implementación simplificada de algoritmo NSGA-II
        soluciones_ordenadas = sorted(soluciones, key=self.calcular_funcion_objetivo)
        return soluciones_ordenadas[:10]  # Top 10 soluciones

class AnalizadorSensibilidad:
    """Analizador de sensibilidad para parámetros del sistema"""
    
    def __init__(self):
        self.parametros_base = {}
        self.resultados_sensibilidad = {}
    
    def analizar_sensibilidad_costo_combustible(self, ruta_base: RutaOptimizada, 
                                               vehiculo: Vehiculo) -> Dict:
        """Analiza sensibilidad al costo de combustible"""
        variaciones = [-0.2, -0.1, 0, 0.1, 0.2]  # ±20%, ±10%
        resultados = {}
        
        costo_base = ruta_base.costo_total
        
        for variacion in variaciones:
            nuevo_costo_combustible = vehiculo.consumo_combustible * (1 + variacion)
            nuevo_costo = costo_base + (ruta_base.combustible_consumido * nuevo_costo_combustible * 1.2)
            
            resultados[variacion] = {
                'costo_total': nuevo_costo,
                'variacion_porcentual': ((nuevo_costo - costo_base) / costo_base) * 100
            }
        
        return resultados
    
    def analizar_sensibilidad_trafico(self, ruta_base: RutaOptimizada) -> Dict:
        """Analiza sensibilidad a cambios en tráfico"""
        variaciones_trafico = [0.5, 0.7, 1.0, 1.3, 1.5]  # Factores de velocidad
        resultados = {}
        
        tiempo_base = ruta_base.tiempo_total
        
        for factor in variaciones_trafico:
            nuevo_tiempo = tiempo_base / factor
            nuevo_costo = ruta_base.costo_total * factor  # Asumir costo proporcional
            
            resultados[factor] = {
                'tiempo_total': nuevo_tiempo,
                'costo_total': nuevo_costo,
                'variacion_tiempo': ((nuevo_tiempo - tiempo_base) / tiempo_base) * 100
            }
        
        return resultados

class SistemaAlertas:
    """Sistema de alertas inteligente"""
    
    def __init__(self):
        self.alertas_activas = []
        self.umbrales = {
            'costo_excesivo': 1000.0,  # USD
            'tiempo_excesivo': 480,    # minutos (8 horas)
            'riesgo_alto': 0.7,
            'satisfaccion_baja': 0.3,
            'emisiones_altas': 50.0     # kg CO2
        }
    
    def evaluar_ruta(self, ruta: RutaOptimizada) -> List[Dict]:
        """Evalúa una ruta y genera alertas si es necesario"""
        alertas = []
        
        # Alerta por costo excesivo
        if ruta.costo_total > self.umbrales['costo_excesivo']:
            alertas.append({
                'tipo': 'costo_excesivo',
                'severidad': 'alta',
                'mensaje': f"Costo de ruta excede umbral: ${ruta.costo_total:.2f}",
                'recomendacion': 'Considerar dividir la ruta o usar vehículo más eficiente'
            })
        
        # Alerta por tiempo excesivo
        if ruta.tiempo_total > self.umbrales['tiempo_excesivo']:
            alertas.append({
                'tipo': 'tiempo_excesivo',
                'severidad': 'alta',
                'mensaje': f"Tiempo de ruta excede umbral: {ruta.tiempo_total} minutos",
                'recomendacion': 'Optimizar secuencia o agregar más vehículos'
            })
        
        # Alerta por riesgo alto
        if ruta.riesgo_total > self.umbrales['riesgo_alto']:
            alertas.append({
                'tipo': 'riesgo_alto',
                'severidad': 'media',
                'mensaje': f"Nivel de riesgo alto: {ruta.riesgo_total:.2f}",
                'recomendacion': 'Revisar zonas de riesgo y considerar rutas alternativas'
            })
        
        # Alerta por satisfacción baja
        if ruta.satisfaccion_cliente < self.umbrales['satisfaccion_baja']:
            alertas.append({
                'tipo': 'satisfaccion_baja',
                'severidad': 'media',
                'mensaje': f"Satisfacción del cliente baja: {ruta.satisfaccion_cliente:.2f}",
                'recomendacion': 'Mejorar tiempos de entrega y comunicación'
            })
        
        # Alerta por emisiones altas
        if ruta.emisiones_co2 > self.umbrales['emisiones_altas']:
            alertas.append({
                'tipo': 'emisiones_altas',
                'severidad': 'baja',
                'mensaje': f"Emisiones CO2 altas: {ruta.emisiones_co2:.1f} kg",
                'recomendacion': 'Considerar vehículos eléctricos o rutas más eficientes'
            })
        
        return alertas
    
    def generar_recomendaciones(self, alertas: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en alertas"""
        recomendaciones = []
        
        tipos_alertas = [alerta['tipo'] for alerta in alertas]
        
        if 'costo_excesivo' in tipos_alertas and 'tiempo_excesivo' in tipos_alertas:
            recomendaciones.append("🚨 CRÍTICO: Revisar completamente la estrategia de rutas")
        
        if 'riesgo_alto' in tipos_alertas:
            recomendaciones.append("⚠️ Implementar sistema de monitoreo en tiempo real")
        
        if 'satisfaccion_baja' in tipos_alertas:
            recomendaciones.append("📞 Mejorar comunicación con clientes sobre tiempos de entrega")
        
        if 'emisiones_altas' in tipos_alertas:
            recomendaciones.append("🌱 Considerar flota más sostenible")
        
        return recomendaciones

class VisualizadorRutas:
    """Visualizador avanzado de rutas"""
    
    def __init__(self):
        self.colores_vehiculos = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    def crear_mapa_rutas(self, rutas: List[RutaOptimizada], puntos_entrega: List[PuntoEntrega]):
        """Crea visualización de rutas en mapa"""
        plt.figure(figsize=(15, 10))
        
        # Plotear puntos de entrega
        lats = [p.latitud for p in puntos_entrega]
        lons = [p.longitud for p in puntos_entrega]
        
        plt.scatter(lons, lats, c='red', s=100, alpha=0.7, label='Puntos de Entrega')
        
        # Plotear rutas
        for i, ruta in enumerate(rutas):
            color = self.colores_vehiculos[i % len(self.colores_vehiculos)]
            
            # Coordenadas de la ruta
            ruta_lats = [puntos_entrega[idx].latitud for idx in ruta.secuencia_optima]
            ruta_lons = [puntos_entrega[idx].longitud for idx in ruta.secuencia_optima]
            
            # Dibujar ruta
            plt.plot(ruta_lons, ruta_lats, color=color, linewidth=2, alpha=0.7,
                    label=f'Vehículo {ruta.vehiculo_id}')
            
            # Marcar inicio de ruta
            plt.scatter(ruta_lons[0], ruta_lats[0], color=color, s=150, marker='s')
        
        plt.xlabel('Longitud')
        plt.ylabel('Latitud')
        plt.title('Optimización de Rutas Logísticas')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def crear_dashboard_metricas(self, rutas: List[RutaOptimizada]):
        """Crea dashboard con métricas clave"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Métricas por vehículo
        vehiculos = [r.vehiculo_id for r in rutas]
        costos = [r.costo_total for r in rutas]
        tiempos = [r.tiempo_total for r in rutas]
        distancias = [r.distancia_total for r in rutas]
        emisiones = [r.emisiones_co2 for r in rutas]
        
        # Gráfico de costos
        axes[0, 0].bar(vehiculos, costos, color='skyblue')
        axes[0, 0].set_title('Costo por Vehículo')
        axes[0, 0].set_ylabel('Costo (USD)')
        
        # Gráfico de tiempos
        axes[0, 1].bar(vehiculos, tiempos, color='lightcoral')
        axes[0, 1].set_title('Tiempo por Vehículo')
        axes[0, 1].set_ylabel('Tiempo (min)')
        
        # Gráfico de distancias
        axes[1, 0].bar(vehiculos, distancias, color='lightgreen')
        axes[1, 0].set_title('Distancia por Vehículo')
        axes[1, 0].set_ylabel('Distancia (km)')
        
        # Gráfico de emisiones
        axes[1, 1].bar(vehiculos, emisiones, color='orange')
        axes[1, 1].set_title('Emisiones CO2 por Vehículo')
        axes[1, 1].set_ylabel('CO2 (kg)')
        
        plt.tight_layout()
        plt.show()
    
    def crear_analisis_tendencias(self, historial_fitness: List[float]):
        """Crea gráfico de evolución del algoritmo genético"""
        plt.figure(figsize=(12, 6))
        plt.plot(historial_fitness, linewidth=2, color='blue')
        plt.title('Evolución del Algoritmo Genético')
        plt.xlabel('Generación')
        plt.ylabel('Fitness')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

def ejemplo_sistema_mejorado():
    """Ejemplo del sistema mejorado en acción"""
    
    print("=" * 80)
    print("SISTEMA AVANZADO DE OPTIMIZACIÓN LOGÍSTICA - VERSIÓN MEJORADA")
    print("=" * 80)
    
    # Crear puntos de entrega avanzados
    puntos_entrega = [
        PuntoEntrega(
            id="E001", direccion="Av. Arequipa 1234", latitud=-12.0464, longitud=-77.0428,
            horario_apertura="09:00", horario_cierre="18:00", tiempo_servicio=10,
            tipo_entrega=TipoEntrega.URGENTE, peso=2.0, volumen=0.05, prioridad=5,
            valor_pedido=150.0, cliente_id="C001", requiere_firma=True
        ),
        PuntoEntrega(
            id="E002", direccion="Jr. Larco 567", latitud=-12.0564, longitud=-77.0328,
            horario_apertura="08:00", horario_cierre="20:00", tiempo_servicio=15,
            tipo_entrega=TipoEntrega.REFRIGERADA, peso=5.0, volumen=0.1, prioridad=4,
            valor_pedido=200.0, cliente_id="C002", instrucciones_especiales="Mantener frío"
        ),
        PuntoEntrega(
            id="E003", direccion="Av. Javier Prado 890", latitud=-12.0364, longitud=-77.0528,
            horario_apertura="10:00", horario_cierre="17:00", tiempo_servicio=20,
            tipo_entrega=TipoEntrega.FRAGIL, peso=8.0, volumen=0.2, prioridad=3,
            valor_pedido=300.0, cliente_id="C003", zona_riesgo=True
        ),
        PuntoEntrega(
            id="E004", direccion="Calle Las Flores 234", latitud=-12.0664, longitud=-77.0228,
            horario_apertura="09:30", horario_cierre="19:00", tiempo_servicio=12,
            tipo_entrega=TipoEntrega.URGENTE, peso=3.0, volumen=0.08, prioridad=5,
            valor_pedido=120.0, cliente_id="C004"
        ),
        PuntoEntrega(
            id="E005", direccion="Av. Brasil 456", latitud=-12.0264, longitud=-77.0628,
            horario_apertura="08:30", horario_cierre="18:30", tiempo_servicio=18,
            tipo_entrega=TipoEntrega.ESTANDAR, peso=6.0, volumen=0.15, prioridad=3,
            valor_pedido=180.0, cliente_id="C005"
        )
    ]
    
    # Crear vehículos avanzados
    vehiculos = [
        Vehiculo(
            id="V001", tipo=TipoVehiculo.FURGON, capacidad_peso=500, capacidad_volumen=10,
            consumo_combustible=0.12, costo_por_km=0.8, velocidad_promedio=35,
            conductor_id="C001", ubicacion_actual=(-12.0464, -77.0428),
            costo_hora_conductor=15.0, emisiones_co2_por_km=0.2
        ),
        Vehiculo(
            id="V002", tipo=TipoVehiculo.VAN_ELECTRICA, capacidad_peso=300, capacidad_volumen=8,
            consumo_combustible=0.0, costo_por_km=0.4, velocidad_promedio=30,
            conductor_id="C002", ubicacion_actual=(-12.0464, -77.0428),
            costo_hora_conductor=12.0, emisiones_co2_por_km=0.0,
            equipamiento_especial=["refrigeracion", "seguridad"]
        )
    ]
    
    print("\n🧬 EJECUTANDO ALGORITMO GENÉTICO...")
    
    # Ejecutar algoritmo genético
    algoritmo_genetico = AlgoritmoGeneticoVRP(poblacion_size=50, generaciones=100)
    mejor_solucion = algoritmo_genetico.optimizar(puntos_entrega, vehiculos)
    
    print(f"\n✅ Mejor solución encontrada:")
    print(f"   Fitness: {mejor_solucion['fitness']:.6f}")
    print(f"   Asignaciones: {mejor_solucion['asignaciones']}")
    
    print("\n🤖 ENTRENANDO MODELO DE MACHINE LEARNING...")
    
    # Crear predictor de tráfico ML
    predictor_ml = PredictorTraficoML()
    
    # Simular datos históricos
    for i in range(200):
        timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
        ubicacion = (random.uniform(-12.1, -12.0), random.uniform(-77.1, -77.0))
        nivel_trafico = random.randint(1, 5)
        condiciones_clima = {
            'temperatura': random.uniform(15, 30),
            'precipitacion': random.uniform(0, 10),
            'es_festivo': random.choice([True, False])
        }
        
        predictor_ml.agregar_dato_historico(timestamp, ubicacion, nivel_trafico, 
                                           condiciones_clima, timestamp.weekday())
    
    # Entrenar modelo
    predictor_ml.entrenar_modelo()
    
    print("\n📊 ANÁLISIS DE SENSIBILIDAD...")
    
    # Crear analizador de sensibilidad
    analizador_sensibilidad = AnalizadorSensibilidad()
    
    # Simular ruta para análisis
    ruta_ejemplo = RutaOptimizada(
        vehiculo_id="V001",
        puntos_entrega=puntos_entrega[:3],
        secuencia_optima=[0, 1, 2],
        distancia_total=25.5,
        tiempo_total=120,
        costo_total=85.0,
        combustible_consumido=3.0,
        emisiones_co2=0.6,
        horario_salida=datetime.now(),
        horario_llegada=datetime.now() + timedelta(hours=2),
        satisfaccion_cliente=0.8,
        riesgo_total=0.3,
        eficiencia_energetica=8.5,
        factor_confiabilidad=0.9
    )
    
    # Analizar sensibilidad al costo de combustible
    sensibilidad_combustible = analizador_sensibilidad.analizar_sensibilidad_costo_combustible(
        ruta_ejemplo, vehiculos[0]
    )
    
    print("   Sensibilidad al costo de combustible:")
    for variacion, resultado in sensibilidad_combustible.items():
        print(f"     {variacion:+.0%}: ${resultado['costo_total']:.2f} "
              f"({resultado['variacion_porcentual']:+.1f}%)")
    
    print("\n🚨 SISTEMA DE ALERTAS...")
    
    # Crear sistema de alertas
    sistema_alertas = SistemaAlertas()
    alertas = sistema_alertas.evaluar_ruta(ruta_ejemplo)
    
    if alertas:
        print("   Alertas generadas:")
        for alerta in alertas:
            print(f"     {alerta['severidad'].upper()}: {alerta['mensaje']}")
            print(f"       Recomendación: {alerta['recomendacion']}")
    else:
        print("   ✅ No se generaron alertas")
    
    # Generar recomendaciones
    recomendaciones = sistema_alertas.generar_recomendaciones(alertas)
    if recomendaciones:
        print("\n   Recomendaciones generales:")
        for rec in recomendaciones:
            print(f"     {rec}")
    
    print("\n🎯 OPTIMIZACIÓN MULTI-OBJETIVO...")
    
    # Crear optimizador multi-objetivo
    optimizador_multi = OptimizadorMultiObjetivo()
    
    # Simular múltiples soluciones
    soluciones = []
    for i in range(5):
        solucion = RutaOptimizada(
            vehiculo_id=f"V00{i+1}",
            puntos_entrega=puntos_entrega[:2],
            secuencia_optima=[0, 1],
            distancia_total=20.0 + i * 5,
            tiempo_total=100 + i * 20,
            costo_total=80.0 + i * 15,
            combustible_consumido=2.5 + i * 0.5,
            emisiones_co2=0.5 + i * 0.1,
            horario_salida=datetime.now(),
            horario_llegada=datetime.now() + timedelta(hours=2),
            satisfaccion_cliente=0.9 - i * 0.1,
            riesgo_total=0.2 + i * 0.1,
            eficiencia_energetica=8.0 - i * 0.5,
            factor_confiabilidad=0.95 - i * 0.05
        )
        soluciones.append(solucion)
    
    # Encontrar frontera de Pareto
    soluciones_pareto = optimizador_multi.optimizar_pareto(soluciones)
    
    print(f"   Soluciones en frontera de Pareto: {len(soluciones_pareto)}")
    for i, solucion in enumerate(soluciones_pareto[:3]):
        funcion_objetivo = optimizador_multi.calcular_funcion_objetivo(solucion)
        print(f"     Solución {i+1}: Función objetivo = {funcion_objetivo:.4f}")
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA MEJORADO EJECUTADO EXITOSAMENTE")
    print("=" * 80)
    
    return {
        'mejor_solucion': mejor_solucion,
        'predictor_ml': predictor_ml,
        'alertas': alertas,
        'recomendaciones': recomendaciones,
        'soluciones_pareto': soluciones_pareto
    }

if __name__ == "__main__":
    ejemplo_sistema_mejorado()



