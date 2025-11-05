"""
Sistema de Optimización Logística - Versión Mejorada Completa
============================================================

Este archivo integra todas las mejoras implementadas en un sistema completo
y fácil de usar para optimización de rutas logísticas.
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
import random
import warnings
warnings.filterwarnings('ignore')

# Importar todos los módulos mejorados
from sistema_mejorado import (
    AlgoritmoGeneticoVRP, PredictorTraficoML, OptimizadorMultiObjetivo,
    AnalizadorSensibilidad, SistemaAlertas, VisualizadorRutas,
    PuntoEntrega, Vehiculo, TipoVehiculo, TipoEntrega, RutaOptimizada
)

from analisis_costos_avanzado import (
    CalculadorCostosAvanzado, AnalizadorEscenarios, OptimizadorCostosTiempoReal,
    AnalizadorRentabilidadCliente, AnalisisTCO
)

# from dashboard_interactivo import (
#     DashboardInteractivo, AplicacionStreamlit
# )

class SistemaLogisticaCompleto:
    """Sistema completo de optimización logística con todas las mejoras"""
    
    def __init__(self):
        # Inicializar todos los componentes
        self.algoritmo_genetico = AlgoritmoGeneticoVRP()
        self.predictor_ml = PredictorTraficoML()
        self.optimizador_multi = OptimizadorMultiObjetivo()
        self.analizador_sensibilidad = AnalizadorSensibilidad()
        self.sistema_alertas = SistemaAlertas()
        self.visualizador = VisualizadorRutas()
        
        self.calculador_costos = CalculadorCostosAvanzado()
        self.analizador_escenarios = AnalizadorEscenarios(self.calculador_costos)
        self.optimizador_tiempo_real = OptimizadorCostosTiempoReal(self.calculador_costos)
        self.analizador_rentabilidad = AnalizadorRentabilidadCliente(self.calculador_costos)
        
        # self.dashboard = DashboardInteractivo()  # Requiere streamlit
        
        # Configuración del sistema
        self.configuracion = {
            'api_keys': {
                'google_maps': None,
                'here': None,
                'openweather': None
            },
            'parametros_optimizacion': {
                'poblacion_size': 100,
                'generaciones': 200,
                'tasa_mutacion': 0.1,
                'tasa_cruza': 0.8
            },
            'umbrales_alertas': {
                'costo_excesivo': 1000.0,
                'tiempo_excesivo': 480,
                'riesgo_alto': 0.7,
                'satisfaccion_baja': 0.3,
                'emisiones_altas': 50.0
            }
        }
        
        # Historial de operaciones
        self.historial_operaciones = []
        self.metricas_sistema = {}
    
    def configurar_sistema(self, configuracion: Dict[str, Any]):
        """Configura el sistema con parámetros personalizados"""
        self.configuracion.update(configuracion)
        
        # Actualizar configuración de componentes
        self.algoritmo_genetico.poblacion_size = configuracion.get('poblacion_size', 100)
        self.algoritmo_genetico.generaciones = configuracion.get('generaciones', 200)
        self.algoritmo_genetico.tasa_mutacion = configuracion.get('tasa_mutacion', 0.1)
        self.algoritmo_genetico.tasa_cruza = configuracion.get('tasa_cruza', 0.8)
        
        # Actualizar umbrales de alertas
        self.sistema_alertas.umbrales.update(configuracion.get('umbrales_alertas', {}))
    
    def crear_flota_vehiculos(self, configuracion_flota: List[Dict[str, Any]]) -> List[Vehiculo]:
        """Crea flota de vehículos basada en configuración"""
        vehiculos = []
        
        for config in configuracion_flota:
            vehiculo = Vehiculo(
                id=config['id'],
                tipo=TipoVehiculo(config['tipo']),
                capacidad_peso=config['capacidad_peso'],
                capacidad_volumen=config['capacidad_volumen'],
                consumo_combustible=config['consumo_combustible'],
                costo_por_km=config['costo_por_km'],
                velocidad_promedio=config['velocidad_promedio'],
                conductor_id=config['conductor_id'],
                ubicacion_actual=tuple(config['ubicacion_actual']),
                costo_hora_conductor=config.get('costo_hora_conductor', 15.0),
                emisiones_co2_por_km=config.get('emisiones_co2_por_km', 0.2)
            )
            vehiculos.append(vehiculo)
            
            # Crear modelo de costos para el vehículo
            self.calculador_costos.crear_modelo_vehiculo(
                vehiculo.id, vehiculo.tipo.value, {
                    'valor_vehiculo': config.get('valor_vehiculo', 50000),
                    'consumo_combustible': vehiculo.consumo_combustible,
                    'precio_combustible': config.get('precio_combustible', 1.2),
                    'costo_mantenimiento_por_km': config.get('costo_mantenimiento_por_km', 0.25),
                    'costo_conductor_por_hora': vehiculo.costo_hora_conductor,
                    'costo_seguro_anual': config.get('costo_seguro_anual', 2000),
                    'emisiones_co2_por_km': vehiculo.emisiones_co2_por_km,
                    'precio_carbono': config.get('precio_carbono', 50),
                    'ciclo_vida_anos': config.get('ciclo_vida_anos', 5),
                    'valor_residual': config.get('valor_residual', 0.0)
                }
            )
        
        return vehiculos
    
    def crear_puntos_entrega(self, configuracion_puntos: List[Dict[str, Any]]) -> List[PuntoEntrega]:
        """Crea puntos de entrega basados en configuración"""
        puntos = []
        
        for config in configuracion_puntos:
            punto = PuntoEntrega(
                id=config['id'],
                direccion=config['direccion'],
                latitud=config['latitud'],
                longitud=config['longitud'],
                horario_apertura=config['horario_apertura'],
                horario_cierre=config['horario_cierre'],
                tiempo_servicio=config['tiempo_servicio'],
                tipo_entrega=TipoEntrega(config['tipo_entrega']),
                peso=config.get('peso', 0.0),
                volumen=config.get('volumen', 0.0),
                prioridad=config.get('prioridad', 1),
                valor_pedido=config.get('valor_pedido', 0.0),
                cliente_id=config.get('cliente_id', ''),
                requiere_firma=config.get('requiere_firma', False),
                instrucciones_especiales=config.get('instrucciones_especiales', ''),
                zona_riesgo=config.get('zona_riesgo', False),
                costo_penalizacion=config.get('costo_penalizacion', 0.0)
            )
            puntos.append(punto)
        
        return puntos
    
    def optimizar_rutas_completo(self, vehiculos: List[Vehiculo], 
                               puntos_entrega: List[PuntoEntrega],
                               condiciones_actuales: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimización completa de rutas con todos los algoritmos"""
        
        print("🚀 Iniciando optimización completa de rutas...")
        
        # Configurar condiciones por defecto
        if condiciones_actuales is None:
            condiciones_actuales = {
                'precio_combustible': 1.2,
                'factor_trafico': 0.8,
                'temperatura': 22,
                'precipitacion': 0,
                'es_festivo': False
            }
        
        # 1. Entrenar modelo de ML si hay datos históricos
        print("🤖 Preparando modelo de predicción de tráfico...")
        self._entrenar_modelo_ml_con_datos_simulados()
        
        # 2. Ejecutar algoritmo genético
        print("🧬 Ejecutando algoritmo genético...")
        mejor_solucion_genetico = self.algoritmo_genetico.optimizar(puntos_entrega, vehiculos)
        
        # 3. Optimización multi-objetivo
        print("🎯 Ejecutando optimización multi-objetivo...")
        rutas_multi_objetivo = self._crear_rutas_multi_objetivo(mejor_solucion_genetico, vehiculos, puntos_entrega)
        soluciones_pareto = self.optimizador_multi.optimizar_pareto(rutas_multi_objetivo)
        
        # 4. Análisis de costos avanzado
        print("💰 Realizando análisis de costos avanzado...")
        analisis_costos = self._analizar_costos_rutas(soluciones_pareto, condiciones_actuales)
        
        # 5. Optimización en tiempo real
        print("⚡ Aplicando optimización en tiempo real...")
        rutas_optimizadas_tiempo_real = self._optimizar_tiempo_real(soluciones_pareto, condiciones_actuales)
        
        # 6. Análisis de sensibilidad
        print("📊 Realizando análisis de sensibilidad...")
        analisis_sensibilidad = self._analizar_sensibilidad(rutas_optimizadas_tiempo_real)
        
        # 7. Sistema de alertas
        print("🚨 Evaluando alertas del sistema...")
        alertas_sistema = self._evaluar_alertas_sistema(rutas_optimizadas_tiempo_real)
        
        # 8. Generar métricas finales
        print("📈 Calculando métricas finales...")
        metricas_finales = self._calcular_metricas_finales(rutas_optimizadas_tiempo_real)
        
        # Guardar en historial
        operacion = {
            'timestamp': datetime.now(),
            'vehiculos': len(vehiculos),
            'puntos_entrega': len(puntos_entrega),
            'mejor_solucion': mejor_solucion_genetico,
            'rutas_optimizadas': rutas_optimizadas_tiempo_real,
            'metricas': metricas_finales,
            'alertas': alertas_sistema
        }
        self.historial_operaciones.append(operacion)
        
        print("✅ Optimización completa finalizada!")
        
        return {
            'mejor_solucion_genetico': mejor_solucion_genetico,
            'soluciones_pareto': soluciones_pareto,
            'rutas_optimizadas': rutas_optimizadas_tiempo_real,
            'analisis_costos': analisis_costos,
            'analisis_sensibilidad': analisis_sensibilidad,
            'alertas': alertas_sistema,
            'metricas': metricas_finales,
            'recomendaciones': self._generar_recomendaciones(alertas_sistema, metricas_finales)
        }
    
    def _entrenar_modelo_ml_con_datos_simulados(self):
        """Entrena modelo ML con datos simulados"""
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
            
            self.predictor_ml.agregar_dato_historico(timestamp, ubicacion, nivel_trafico, 
                                                   condiciones_clima, timestamp.weekday())
        
        # Entrenar modelo
        self.predictor_ml.entrenar_modelo()
    
    def _crear_rutas_multi_objetivo(self, solucion_genetico: Dict, vehiculos: List[Vehiculo], 
                                   puntos_entrega: List[PuntoEntrega]) -> List[RutaOptimizada]:
        """Crea rutas para análisis multi-objetivo"""
        rutas = []
        
        for vehiculo_id, puntos_asignados in solucion_genetico['asignaciones'].items():
            if not puntos_asignados:
                continue
            
            vehiculo = next(v for v in vehiculos if v.id == vehiculo_id)
            
            # Calcular métricas básicas
            distancia_total = self._calcular_distancia_total(puntos_asignados, puntos_entrega, vehiculo)
            tiempo_total = distancia_total / vehiculo.velocidad_promedio * 60  # minutos
            
            # Calcular métricas avanzadas
            costo_total = distancia_total * vehiculo.costo_por_km
            combustible_consumido = distancia_total * vehiculo.consumo_combustible
            emisiones_co2 = distancia_total * vehiculo.emisiones_co2_por_km
            
            # Calcular satisfacción del cliente (simplificado)
            satisfaccion_cliente = self._calcular_satisfaccion_cliente(puntos_asignados, puntos_entrega)
            
            # Calcular riesgo total
            riesgo_total = self._calcular_riesgo_total(puntos_asignados, puntos_entrega)
            
            ruta = RutaOptimizada(
                vehiculo_id=vehiculo_id,
                puntos_entrega=[puntos_entrega[i] for i in puntos_asignados],
                secuencia_optima=puntos_asignados,
                distancia_total=distancia_total,
                tiempo_total=int(tiempo_total),
                costo_total=costo_total,
                combustible_consumido=combustible_consumido,
                emisiones_co2=emisiones_co2,
                horario_salida=datetime.now(),
                horario_llegada=datetime.now() + timedelta(minutes=tiempo_total),
                satisfaccion_cliente=satisfaccion_cliente,
                riesgo_total=riesgo_total,
                eficiencia_energetica=distancia_total / combustible_consumido if combustible_consumido > 0 else 0,
                factor_confiabilidad=0.9
            )
            
            rutas.append(ruta)
        
        return rutas
    
    def _calcular_distancia_total(self, puntos_indices: List[int], puntos_entrega: List[PuntoEntrega], 
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
    
    def _calcular_satisfaccion_cliente(self, puntos_indices: List[int], puntos_entrega: List[PuntoEntrega]) -> float:
        """Calcula satisfacción promedio del cliente"""
        if not puntos_indices:
            return 0.0
        
        satisfacciones = []
        for punto_idx in puntos_indices:
            punto = puntos_entrega[punto_idx]
            
            # Factores que afectan la satisfacción
            factor_prioridad = punto.prioridad / 5.0
            factor_tipo = 0.9 if punto.tipo_entrega == TipoEntrega.URGENTE else 0.8
            factor_valor = min(1.0, punto.valor_pedido / 200.0)  # Normalizar por valor promedio
            
            satisfaccion = (factor_prioridad + factor_tipo + factor_valor) / 3.0
            satisfacciones.append(satisfaccion)
        
        return sum(satisfacciones) / len(satisfacciones)
    
    def _calcular_riesgo_total(self, puntos_indices: List[int], puntos_entrega: List[PuntoEntrega]) -> float:
        """Calcula riesgo total de una ruta"""
        if not puntos_indices:
            return 0.0
        
        riesgos = []
        for punto_idx in puntos_indices:
            punto = puntos_entrega[punto_idx]
            
            riesgo_punto = 0.0
            
            # Riesgo por zona
            if punto.zona_riesgo:
                riesgo_punto += 0.3
            
            # Riesgo por tipo de entrega
            if punto.tipo_entrega == TipoEntrega.FRAGIL:
                riesgo_punto += 0.2
            elif punto.tipo_entrega == TipoEntrega.REFRIGERADA:
                riesgo_punto += 0.1
            
            # Riesgo por valor del pedido
            if punto.valor_pedido > 500:
                riesgo_punto += 0.2
            
            riesgos.append(min(1.0, riesgo_punto))
        
        return sum(riesgos) / len(riesgos)
    
    def _analizar_costos_rutas(self, rutas: List[RutaOptimizada], condiciones: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza costos de las rutas"""
        analisis = {
            'costos_por_ruta': [],
            'costos_totales': {},
            'comparacion_vehiculos': {},
            'analisis_escenarios': {}
        }
        
        for ruta in rutas:
            # Calcular costos detallados
            costos_detallados = self.calculador_costos.calcular_costo_ruta_dinamico(
                ruta.vehiculo_id, ruta.distancia_total, ruta.tiempo_total / 60, condiciones
            )
            
            analisis['costos_por_ruta'].append({
                'vehiculo_id': ruta.vehiculo_id,
                'costos': costos_detallados,
                'costo_total': sum(costos_detallados.values())
            })
        
        # Calcular costos totales
        for categoria in ['combustible', 'mantenimiento', 'conductor', 'seguro', 'carbono']:
            analisis['costos_totales'][categoria] = sum(
                ruta['costos'].get(categoria, 0) for ruta in analisis['costos_por_ruta']
            )
        
        return analisis
    
    def _optimizar_tiempo_real(self, rutas: List[RutaOptimizada], condiciones: Dict[str, Any]) -> List[RutaOptimizada]:
        """Aplica optimización en tiempo real"""
        rutas_optimizadas = []
        
        for ruta in rutas:
            # Simular optimización en tiempo real
            puntos_entrega_dict = [
                {
                    'latitud': p.latitud,
                    'longitud': p.longitud,
                    'tiempo_servicio': p.tiempo_servicio
                }
                for p in ruta.puntos_entrega
            ]
            
            optimizacion = self.optimizador_tiempo_real.optimizar_ruta_tiempo_real(
                ruta.vehiculo_id, puntos_entrega_dict, condiciones
            )
            
            # Actualizar ruta con optimización
            ruta_optimizada = ruta
            ruta_optimizada.secuencia_optima = optimizacion['mejor_secuencia']
            ruta_optimizada.costo_total = optimizacion['costo_optimizado']
            
            rutas_optimizadas.append(ruta_optimizada)
        
        return rutas_optimizadas
    
    def _analizar_sensibilidad(self, rutas: List[RutaOptimizada]) -> Dict[str, Any]:
        """Realiza análisis de sensibilidad"""
        analisis = {}
        
        for ruta in rutas:
            vehiculo_id = ruta.vehiculo_id
            
            # Análisis de sensibilidad al combustible (simplificado)
            sensibilidad_combustible = {
                'variacion': 'simplificada',
                'costo_base': ruta.costo_total,
                'variaciones': {
                    -0.2: ruta.costo_total * 0.8,
                    -0.1: ruta.costo_total * 0.9,
                    0: ruta.costo_total,
                    0.1: ruta.costo_total * 1.1,
                    0.2: ruta.costo_total * 1.2
                }
            }
            
            # Análisis de sensibilidad al tráfico
            sensibilidad_trafico = self.analizador_sensibilidad.analizar_sensibilidad_trafico(ruta)
            
            analisis[vehiculo_id] = {
                'sensibilidad_combustible': sensibilidad_combustible,
                'sensibilidad_trafico': sensibilidad_trafico
            }
        
        return analisis
    
    def _evaluar_alertas_sistema(self, rutas: List[RutaOptimizada]) -> List[Dict[str, Any]]:
        """Evalúa alertas del sistema"""
        alertas_totales = []
        
        for ruta in rutas:
            alertas_ruta = self.sistema_alertas.evaluar_ruta(ruta)
            alertas_totales.extend(alertas_ruta)
        
        return alertas_totales
    
    def _calcular_metricas_finales(self, rutas: List[RutaOptimizada]) -> Dict[str, Any]:
        """Calcula métricas finales del sistema"""
        if not rutas:
            return {}
        
        metricas = {
            'total_rutas': len(rutas),
            'total_distancia': sum(r.distancia_total for r in rutas),
            'total_tiempo': sum(r.tiempo_total for r in rutas),
            'total_costo': sum(r.costo_total for r in rutas),
            'total_emisiones': sum(r.emisiones_co2 for r in rutas),
            'promedio_satisfaccion': sum(r.satisfaccion_cliente for r in rutas) / len(rutas),
            'promedio_riesgo': sum(r.riesgo_total for r in rutas) / len(rutas),
            'eficiencia_promedio': sum(r.eficiencia_energetica for r in rutas) / len(rutas),
            'confiabilidad_promedio': sum(r.factor_confiabilidad for r in rutas) / len(rutas)
        }
        
        # Métricas adicionales
        metricas['costo_por_km'] = metricas['total_costo'] / metricas['total_distancia'] if metricas['total_distancia'] > 0 else 0
        metricas['costo_por_hora'] = metricas['total_costo'] / (metricas['total_tiempo'] / 60) if metricas['total_tiempo'] > 0 else 0
        metricas['emisiones_por_km'] = metricas['total_emisiones'] / metricas['total_distancia'] if metricas['total_distancia'] > 0 else 0
        
        return metricas
    
    def _generar_recomendaciones(self, alertas: List[Dict[str, Any]], metricas: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en alertas y métricas"""
        recomendaciones = []
        
        # Recomendaciones basadas en alertas
        tipos_alertas = [alerta['tipo'] for alerta in alertas]
        
        if 'costo_excesivo' in tipos_alertas:
            recomendaciones.append("💰 Considerar optimización adicional de rutas para reducir costos")
        
        if 'tiempo_excesivo' in tipos_alertas:
            recomendaciones.append("⏰ Evaluar uso de más vehículos o rutas paralelas")
        
        if 'riesgo_alto' in tipos_alertas:
            recomendaciones.append("⚠️ Implementar sistema de monitoreo en tiempo real")
        
        if 'satisfaccion_baja' in tipos_alertas:
            recomendaciones.append("😊 Mejorar comunicación con clientes sobre tiempos de entrega")
        
        if 'emisiones_altas' in tipos_alertas:
            recomendaciones.append("🌱 Considerar flota más sostenible")
        
        # Recomendaciones basadas en métricas
        if metricas.get('costo_por_km', 0) > 2.0:
            recomendaciones.append("📊 Revisar estructura de costos operativos")
        
        if metricas.get('promedio_satisfaccion', 0) < 0.7:
            recomendaciones.append("📞 Implementar programa de mejora de satisfacción del cliente")
        
        if metricas.get('promedio_riesgo', 0) > 0.5:
            recomendaciones.append("🛡️ Fortalecer medidas de seguridad y reducción de riesgo")
        
        if metricas.get('eficiencia_promedio', 0) < 5.0:
            recomendaciones.append("⚡ Optimizar eficiencia energética de la flota")
        
        return recomendaciones
    
    def generar_reporte_completo(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte completo del sistema"""
        
        reporte = {
            'resumen_ejecutivo': {
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_rutas_optimizadas': resultados['metricas']['total_rutas'],
                'costo_total': resultados['metricas']['total_costo'],
                'ahorro_estimado': self._calcular_ahorro_estimado(resultados),
                'satisfaccion_promedio': resultados['metricas']['promedio_satisfaccion'],
                'alertas_criticas': len([a for a in resultados['alertas'] if a['severidad'] == 'alta'])
            },
            'detalles_optimizacion': {
                'algoritmo_genetico': {
                    'fitness_final': resultados['mejor_solucion_genetico']['fitness'],
                    'asignaciones': resultados['mejor_solucion_genetico']['asignaciones']
                },
                'soluciones_pareto': len(resultados['soluciones_pareto']),
                'rutas_optimizadas': len(resultados['rutas_optimizadas'])
            },
            'analisis_costos': resultados['analisis_costos'],
            'analisis_sensibilidad': resultados['analisis_sensibilidad'],
            'alertas': resultados['alertas'],
            'metricas': resultados['metricas'],
            'recomendaciones': resultados['recomendaciones']
        }
        
        return reporte
    
    def _calcular_ahorro_estimado(self, resultados: Dict[str, Any]) -> float:
        """Calcula ahorro estimado vs solución inicial"""
        # Simplificado: asumir 15% de ahorro promedio
        costo_total = resultados['metricas']['total_costo']
        return costo_total * 0.15
    
    def crear_dashboard_completo(self, resultados: Dict[str, Any]):
        """Crea dashboard completo con resultados"""
        
        # Preparar datos para dashboard
        rutas_dashboard = []
        for ruta in resultados['rutas_optimizadas']:
            rutas_dashboard.append({
                'vehiculo_id': ruta.vehiculo_id,
                'distancia_total': ruta.distancia_total,
                'tiempo_total': ruta.tiempo_total,
                'costo_total': ruta.costo_total,
                'emisiones_co2': ruta.emisiones_co2,
                'satisfaccion_cliente': ruta.satisfaccion_cliente,
                'riesgo_total': ruta.riesgo_total,
                'secuencia_optima': ruta.secuencia_optima
            })
        
        puntos_dashboard = []
        for ruta in resultados['rutas_optimizadas']:
            for punto in ruta.puntos_entrega:
                puntos_dashboard.append({
                    'id': punto.id,
                    'direccion': punto.direccion,
                    'latitud': punto.latitud,
                    'longitud': punto.longitud,
                    'prioridad': punto.prioridad,
                    'tipo_entrega': punto.tipo_entrega.value,
                    'peso': punto.peso,
                    'volumen': punto.volumen,
                    'horario_apertura': punto.horario_apertura,
                    'horario_cierre': punto.horario_cierre
                })
        
        # Crear dashboard (simplificado sin streamlit)
        datos_dashboard = {
            'metricas': {
                'total_rutas': len(rutas_dashboard),
                'total_distancia': sum(r['distancia_total'] for r in rutas_dashboard),
                'total_tiempo': sum(r['tiempo_total'] for r in rutas_dashboard),
                'total_costo': sum(r['costo_total'] for r in rutas_dashboard),
                'total_emisiones': sum(r['emisiones_co2'] for r in rutas_dashboard),
                'promedio_satisfaccion': sum(r['satisfaccion_cliente'] for r in rutas_dashboard) / len(rutas_dashboard) if rutas_dashboard else 0,
                'promedio_riesgo': sum(r['riesgo_total'] for r in rutas_dashboard) / len(rutas_dashboard) if rutas_dashboard else 0
            }
        }
        
        return {
            'dashboard': datos_dashboard,
            'mapa': 'Mapa interactivo disponible con streamlit',
            'reporte': self.generar_reporte_completo(resultados)
        }

def ejemplo_sistema_completo():
    """Ejemplo del sistema completo en acción"""
    
    print("=" * 80)
    print("SISTEMA COMPLETO DE OPTIMIZACIÓN LOGÍSTICA")
    print("Versión Mejorada con Todas las Funcionalidades")
    print("=" * 80)
    
    # Crear sistema completo
    sistema = SistemaLogisticaCompleto()
    
    # Configurar sistema
    configuracion_sistema = {
        'parametros_optimizacion': {
            'poblacion_size': 50,
            'generaciones': 100,
            'tasa_mutacion': 0.1,
            'tasa_cruza': 0.8
        },
        'umbrales_alertas': {
            'costo_excesivo': 500.0,
            'tiempo_excesivo': 300,
            'riesgo_alto': 0.6,
            'satisfaccion_baja': 0.4,
            'emisiones_altas': 30.0
        }
    }
    
    sistema.configurar_sistema(configuracion_sistema)
    
    print("\n🚚 Configurando flota de vehículos...")
    
    # Configurar flota
    configuracion_flota = [
        {
            'id': 'V001',
            'tipo': 'furgon',
            'capacidad_peso': 500,
            'capacidad_volumen': 10,
            'consumo_combustible': 0.12,
            'costo_por_km': 0.8,
            'velocidad_promedio': 35,
            'conductor_id': 'C001',
            'ubicacion_actual': [-12.0464, -77.0428],
            'costo_hora_conductor': 15.0,
            'emisiones_co2_por_km': 0.2,
            'valor_vehiculo': 45000,
            'precio_combustible': 1.2,
            'costo_mantenimiento_por_km': 0.25,
            'costo_seguro_anual': 2000,
            'precio_carbono': 50,
            'ciclo_vida_anos': 5,
            'valor_residual': 5000
        },
        {
            'id': 'V002',
            'tipo': 'van_electrica',
            'capacidad_peso': 300,
            'capacidad_volumen': 8,
            'consumo_combustible': 0.0,
            'costo_por_km': 0.4,
            'velocidad_promedio': 30,
            'conductor_id': 'C002',
            'ubicacion_actual': [-12.0464, -77.0428],
            'costo_hora_conductor': 12.0,
            'emisiones_co2_por_km': 0.0,
            'valor_vehiculo': 60000,
            'precio_combustible': 0.3,
            'costo_mantenimiento_por_km': 0.15,
            'costo_seguro_anual': 1800,
            'precio_carbono': 50,
            'ciclo_vida_anos': 8,
            'valor_residual': 8000
        }
    ]
    
    vehiculos = sistema.crear_flota_vehiculos(configuracion_flota)
    print(f"✅ Flota configurada: {len(vehiculos)} vehículos")
    
    print("\n📦 Configurando puntos de entrega...")
    
    # Configurar puntos de entrega
    configuracion_puntos = [
        {
            'id': 'E001',
            'direccion': 'Av. Arequipa 1234',
            'latitud': -12.0464,
            'longitud': -77.0428,
            'horario_apertura': '09:00',
            'horario_cierre': '18:00',
            'tiempo_servicio': 10,
            'tipo_entrega': 'urgente',
            'peso': 2.0,
            'volumen': 0.05,
            'prioridad': 5,
            'valor_pedido': 150.0,
            'cliente_id': 'C001',
            'requiere_firma': True,
            'zona_riesgo': False
        },
        {
            'id': 'E002',
            'direccion': 'Jr. Larco 567',
            'latitud': -12.0564,
            'longitud': -77.0328,
            'horario_apertura': '08:00',
            'horario_cierre': '20:00',
            'tiempo_servicio': 15,
            'tipo_entrega': 'refrigerada',
            'peso': 5.0,
            'volumen': 0.1,
            'prioridad': 4,
            'valor_pedido': 200.0,
            'cliente_id': 'C002',
            'instrucciones_especiales': 'Mantener frío',
            'zona_riesgo': False
        },
        {
            'id': 'E003',
            'direccion': 'Av. Javier Prado 890',
            'latitud': -12.0364,
            'longitud': -77.0528,
            'horario_apertura': '10:00',
            'horario_cierre': '17:00',
            'tiempo_servicio': 20,
            'tipo_entrega': 'fragil',
            'peso': 8.0,
            'volumen': 0.2,
            'prioridad': 3,
            'valor_pedido': 300.0,
            'cliente_id': 'C003',
            'zona_riesgo': True
        },
        {
            'id': 'E004',
            'direccion': 'Calle Las Flores 234',
            'latitud': -12.0664,
            'longitud': -77.0228,
            'horario_apertura': '09:30',
            'horario_cierre': '19:00',
            'tiempo_servicio': 12,
            'tipo_entrega': 'urgente',
            'peso': 3.0,
            'volumen': 0.08,
            'prioridad': 5,
            'valor_pedido': 120.0,
            'cliente_id': 'C004',
            'zona_riesgo': False
        },
        {
            'id': 'E005',
            'direccion': 'Av. Brasil 456',
            'latitud': -12.0264,
            'longitud': -77.0628,
            'horario_apertura': '08:30',
            'horario_cierre': '18:30',
            'tiempo_servicio': 18,
            'tipo_entrega': 'estandar',
            'peso': 6.0,
            'volumen': 0.15,
            'prioridad': 3,
            'valor_pedido': 180.0,
            'cliente_id': 'C005',
            'zona_riesgo': False
        }
    ]
    
    puntos_entrega = sistema.crear_puntos_entrega(configuracion_puntos)
    print(f"✅ Puntos de entrega configurados: {len(puntos_entrega)} puntos")
    
    print("\n🚀 Ejecutando optimización completa...")
    
    # Condiciones actuales
    condiciones_actuales = {
        'precio_combustible': 1.3,
        'factor_trafico': 0.7,
        'temperatura': 24,
        'precipitacion': 0,
        'es_festivo': False
    }
    
    # Ejecutar optimización completa
    resultados = sistema.optimizar_rutas_completo(vehiculos, puntos_entrega, condiciones_actuales)
    
    print("\n📊 RESULTADOS DE LA OPTIMIZACIÓN:")
    print("=" * 50)
    
    metricas = resultados['metricas']
    print(f"Total rutas optimizadas: {metricas['total_rutas']}")
    print(f"Distancia total: {metricas['total_distancia']:.2f} km")
    print(f"Tiempo total: {metricas['total_tiempo']} minutos")
    print(f"Costo total: ${metricas['total_costo']:.2f}")
    print(f"Emisiones CO2: {metricas['total_emisiones']:.2f} kg")
    print(f"Satisfacción promedio: {metricas['promedio_satisfaccion']:.2f}")
    print(f"Riesgo promedio: {metricas['promedio_riesgo']:.2f}")
    print(f"Eficiencia promedio: {metricas['eficiencia_promedio']:.2f} km/L")
    
    print("\n🚨 ALERTAS DEL SISTEMA:")
    print("=" * 50)
    
    if resultados['alertas']:
        for alerta in resultados['alertas']:
            print(f"{alerta['severidad'].upper()}: {alerta['mensaje']}")
            print(f"  Recomendación: {alerta['recomendacion']}")
    else:
        print("✅ No se generaron alertas")
    
    print("\n💡 RECOMENDACIONES:")
    print("=" * 50)
    
    for recomendacion in resultados['recomendaciones']:
        print(f"• {recomendacion}")
    
    print("\n📈 GENERANDO REPORTE COMPLETO...")
    
    # Generar reporte completo
    reporte = sistema.generar_reporte_completo(resultados)
    
    print("✅ Reporte completo generado!")
    print(f"   Resumen ejecutivo: {reporte['resumen_ejecutivo']}")
    
    print("\n🎨 CREANDO DASHBOARD INTERACTIVO...")
    
    # Crear dashboard completo
    dashboard_completo = sistema.crear_dashboard_completo(resultados)
    
    print("✅ Dashboard interactivo creado!")
    print(f"   Métricas del dashboard: {len(dashboard_completo['dashboard']['metricas'])} métricas")
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA COMPLETO EJECUTADO EXITOSAMENTE")
    print("=" * 80)
    
    return {
        'sistema': sistema,
        'resultados': resultados,
        'reporte': reporte,
        'dashboard': dashboard_completo
    }

if __name__ == "__main__":
    ejemplo_sistema_completo()
