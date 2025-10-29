"""
Sistema Avanzado de Análisis de Costos Logísticos
================================================

Mejoras implementadas:
- Análisis de costos totales de propiedad (TCO)
- Modelado de costos dinámicos
- Análisis de escenarios
- Optimización de costos en tiempo real
- Análisis de rentabilidad por cliente
- Modelado de costos de carbono
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
import seaborn as sns

class TipoCosto(Enum):
    DIRECTO = "directo"
    INDIRECTO = "indirecto"
    FIJO = "fijo"
    VARIABLE = "variable"
    OPORTUNIDAD = "oportunidad"
    CARBONO = "carbono"

class CategoriaCosto(Enum):
    COMBUSTIBLE = "combustible"
    MANTENIMIENTO = "mantenimiento"
    DEPRECIACION = "depreciacion"
    SEGURO = "seguro"
    CONDUCTOR = "conductor"
    PEAJE = "peaje"
    ADMINISTRATIVO = "administrativo"
    CARBONO = "carbono"
    PENALIZACIONES = "penalizaciones"
    INVENTARIO = "inventario"

@dataclass
class CostoDetallado:
    """Estructura detallada de costos"""
    categoria: CategoriaCosto
    tipo: TipoCosto
    valor_base: float
    factor_escalamiento: float = 1.0
    variabilidad: float = 0.0  # Desviación estándar
    dependencias: List[str] = field(default_factory=list)
    formula_calculo: str = ""
    unidad: str = "USD"
    frecuencia: str = "por_km"  # por_km, por_hora, por_dia, por_entrega

@dataclass
class ModeloCostoVehiculo:
    """Modelo completo de costos por vehículo"""
    vehiculo_id: str
    tipo_vehiculo: str
    costos: Dict[CategoriaCosto, CostoDetallado]
    parametros_operativos: Dict[str, float]
    ciclo_vida_anos: int = 5
    valor_residual: float = 0.0
    tasa_descuento: float = 0.1

@dataclass
class AnalisisTCO:
    """Análisis de Costo Total de Propiedad"""
    costo_adquisicion: float
    costos_operativos_anuales: float
    costos_mantenimiento_anuales: float
    costos_combustible_anuales: float
    costos_seguro_anuales: float
    valor_residual: float
    ciclo_vida_anos: int
    tco_total: float
    tco_anual: float
    tco_por_km: float

class CalculadorCostosAvanzado:
    """Calculador avanzado de costos logísticos"""
    
    def __init__(self):
        self.modelos_vehiculos = {}
        self.factores_externos = {}
        self.escenarios = {}
        self.historial_costos = []
        
    def crear_modelo_vehiculo(self, vehiculo_id: str, tipo_vehiculo: str, 
                            parametros: Dict[str, float]) -> ModeloCostoVehiculo:
        """Crea modelo de costos para un vehículo"""
        
        costos = {}
        
        # Costos de combustible
        costos[CategoriaCosto.COMBUSTIBLE] = CostoDetallado(
            categoria=CategoriaCosto.COMBUSTIBLE,
            tipo=TipoCosto.VARIABLE,
            valor_base=parametros.get('consumo_combustible', 0.12) * parametros.get('precio_combustible', 1.2),
            factor_escalamiento=1.0,
            variabilidad=0.1,
            dependencias=['precio_combustible', 'eficiencia_conduccion'],
            formula_calculo="consumo_km * precio_litro * distancia",
            unidad="USD",
            frecuencia="por_km"
        )
        
        # Costos de mantenimiento
        costos[CategoriaCosto.MANTENIMIENTO] = CostoDetallado(
            categoria=CategoriaCosto.MANTENIMIENTO,
            tipo=TipoCosto.VARIABLE,
            valor_base=parametros.get('costo_mantenimiento_por_km', 0.25),
            factor_escalamiento=1.05,  # Incremento anual del 5%
            variabilidad=0.15,
            dependencias=['kilometraje', 'edad_vehiculo', 'condiciones_carretera'],
            formula_calculo="costo_base * kilometraje * factor_edad",
            unidad="USD",
            frecuencia="por_km"
        )
        
        # Costos de depreciación
        costos[CategoriaCosto.DEPRECIACION] = CostoDetallado(
            categoria=CategoriaCosto.DEPRECIACION,
            tipo=TipoCosto.FIJO,
            valor_base=parametros.get('valor_vehiculo', 50000) / parametros.get('vida_util_km', 300000),
            factor_escalamiento=1.0,
            variabilidad=0.0,
            dependencias=['valor_vehiculo', 'vida_util'],
            formula_calculo="valor_vehiculo / vida_util_km",
            unidad="USD",
            frecuencia="por_km"
        )
        
        # Costos de conductor
        costos[CategoriaCosto.CONDUCTOR] = CostoDetallado(
            categoria=CategoriaCosto.CONDUCTOR,
            tipo=TipoCosto.VARIABLE,
            valor_base=parametros.get('costo_conductor_por_hora', 15.0),
            factor_escalamiento=1.03,  # Incremento anual del 3%
            variabilidad=0.05,
            dependencias=['tiempo_conduccion', 'salario_conductor'],
            formula_calculo="salario_hora * tiempo_conduccion",
            unidad="USD",
            frecuencia="por_hora"
        )
        
        # Costos de seguro
        costos[CategoriaCosto.SEGURO] = CostoDetallado(
            categoria=CategoriaCosto.SEGURO,
            tipo=TipoCosto.FIJO,
            valor_base=parametros.get('costo_seguro_anual', 2000) / 365,
            factor_escalamiento=1.02,  # Incremento anual del 2%
            variabilidad=0.0,
            dependencias=['valor_vehiculo', 'historial_accidentes'],
            formula_calculo="prima_anual / dias_año",
            unidad="USD",
            frecuencia="por_dia"
        )
        
        # Costos de carbono
        costos[CategoriaCosto.CARBONO] = CostoDetallado(
            categoria=CategoriaCosto.CARBONO,
            tipo=TipoCosto.VARIABLE,
            valor_base=parametros.get('emisiones_co2_por_km', 0.2) * parametros.get('precio_carbono', 50),
            factor_escalamiento=1.1,  # Incremento anual del 10%
            variabilidad=0.2,
            dependencias=['emisiones_co2', 'precio_carbono'],
            formula_calculo="emisiones_km * precio_carbono * distancia",
            unidad="USD",
            frecuencia="por_km"
        )
        
        modelo = ModeloCostoVehiculo(
            vehiculo_id=vehiculo_id,
            tipo_vehiculo=tipo_vehiculo,
            costos=costos,
            parametros_operativos=parametros,
            ciclo_vida_anos=parametros.get('ciclo_vida_anos', 5),
            valor_residual=parametros.get('valor_residual', 0.0),
            tasa_descuento=parametros.get('tasa_descuento', 0.1)
        )
        
        self.modelos_vehiculos[vehiculo_id] = modelo
        return modelo
    
    def calcular_costo_ruta_dinamico(self, vehiculo_id: str, distancia_km: float, 
                                    tiempo_horas: float, condiciones: Dict[str, Any]) -> Dict[str, float]:
        """Calcula costos dinámicos de una ruta"""
        
        if vehiculo_id not in self.modelos_vehiculos:
            raise ValueError(f"Modelo de vehículo {vehiculo_id} no encontrado")
        
        modelo = self.modelos_vehiculos[vehiculo_id]
        costos_calculados = {}
        
        for categoria, costo_detallado in modelo.costos.items():
            # Aplicar factores externos
            factor_externo = self._calcular_factor_externo(costo_detallado, condiciones)
            
            # Calcular costo base
            if costo_detallado.frecuencia == "por_km":
                costo_base = costo_detallado.valor_base * distancia_km
            elif costo_detallado.frecuencia == "por_hora":
                costo_base = costo_detallado.valor_base * tiempo_horas
            elif costo_detallado.frecuencia == "por_dia":
                costo_base = costo_detallado.valor_base * (tiempo_horas / 24)
            else:
                costo_base = costo_detallado.valor_base
            
            # Aplicar escalamiento temporal
            factor_temporal = self._calcular_factor_temporal(costo_detallado)
            
            # Aplicar variabilidad
            factor_variabilidad = np.random.normal(1.0, costo_detallado.variabilidad)
            
            # Calcular costo final
            costo_final = costo_base * factor_externo * factor_temporal * factor_variabilidad
            
            costos_calculados[categoria.value] = max(0, costo_final)
        
        return costos_calculados
    
    def _calcular_factor_externo(self, costo_detallado: CostoDetallado, condiciones: Dict[str, Any]) -> float:
        """Calcula factor externo basado en condiciones"""
        factor = 1.0
        
        for dependencia in costo_detallado.dependencias:
            if dependencia in condiciones:
                valor = condiciones[dependencia]
                
                if dependencia == 'precio_combustible':
                    factor *= valor / 1.2  # Precio base de referencia
                elif dependencia == 'eficiencia_conduccion':
                    factor *= (2.0 - valor)  # Inversamente proporcional
                elif dependencia == 'condiciones_carretera':
                    factor *= valor  # Factor directo
                elif dependencia == 'precio_carbono':
                    factor *= valor / 50  # Precio base de referencia
        
        return factor
    
    def _calcular_factor_temporal(self, costo_detallado: CostoDetallado) -> float:
        """Calcula factor temporal de escalamiento"""
        # Simular escalamiento anual
        anos_transcurridos = 1.0  # Simplificado
        return costo_detallado.factor_escalamiento ** anos_transcurridos
    
    def calcular_tco(self, vehiculo_id: str, kilometraje_anual: float) -> AnalisisTCO:
        """Calcula Costo Total de Propiedad (TCO)"""
        
        modelo = self.modelos_vehiculos[vehiculo_id]
        
        # Costos de adquisición
        costo_adquisicion = modelo.parametros_operativos.get('valor_vehiculo', 50000)
        
        # Costos operativos anuales
        costos_operativos = {}
        for categoria, costo_detallado in modelo.costos.items():
            if costo_detallado.frecuencia == "por_km":
                costos_operativos[categoria] = costo_detallado.valor_base * kilometraje_anual
            elif costo_detallado.frecuencia == "por_dia":
                costos_operativos[categoria] = costo_detallado.valor_base * 365
            else:
                costos_operativos[categoria] = costo_detallado.valor_base * 2000  # Estimación
        
        costo_operativo_total = sum(costos_operativos.values())
        
        # Calcular TCO con valor presente neto
        flujos_caja = []
        for año in range(modelo.ciclo_vida_anos):
            flujo_año = costo_operativo_total * (modelo.costos[CategoriaCosto.MANTENIMIENTO].factor_escalamiento ** año)
            flujos_caja.append(flujo_año)
        
        # Valor presente neto
        vpn_costos_operativos = sum(
            flujo / ((1 + modelo.tasa_descuento) ** (año + 1))
            for año, flujo in enumerate(flujos_caja)
        )
        
        # Valor residual presente
        valor_residual_presente = modelo.valor_residual / ((1 + modelo.tasa_descuento) ** modelo.ciclo_vida_anos)
        
        # TCO total
        tco_total = costo_adquisicion + vpn_costos_operativos - valor_residual_presente
        tco_anual = tco_total / modelo.ciclo_vida_anos
        tco_por_km = tco_total / (kilometraje_anual * modelo.ciclo_vida_anos)
        
        return AnalisisTCO(
            costo_adquisicion=costo_adquisicion,
            costos_operativos_anuales=costo_operativo_total,
            costos_mantenimiento_anuales=costos_operativos.get(CategoriaCosto.MANTENIMIENTO, 0),
            costos_combustible_anuales=costos_operativos.get(CategoriaCosto.COMBUSTIBLE, 0),
            costos_seguro_anuales=costos_operativos.get(CategoriaCosto.SEGURO, 0),
            valor_residual=modelo.valor_residual,
            ciclo_vida_anos=modelo.ciclo_vida_anos,
            tco_total=tco_total,
            tco_anual=tco_anual,
            tco_por_km=tco_por_km
        )

class AnalizadorEscenarios:
    """Analizador de escenarios de costos"""
    
    def __init__(self, calculador_costos: CalculadorCostosAvanzado):
        self.calculador = calculador_costos
        self.escenarios = {}
    
    def crear_escenario(self, nombre: str, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un escenario de análisis"""
        
        escenario = {
            'nombre': nombre,
            'parametros': parametros,
            'resultados': {},
            'probabilidad': parametros.get('probabilidad', 0.5),
            'impacto': parametros.get('impacto', 'medio')
        }
        
        self.escenarios[nombre] = escenario
        return escenario
    
    def analizar_escenario_combustible(self, vehiculo_id: str, distancia_km: float, 
                                     tiempo_horas: float) -> Dict[str, Dict]:
        """Analiza escenarios de variación de precio de combustible"""
        
        escenarios_combustible = {
            'optimista': {'precio_combustible': 0.8, 'probabilidad': 0.2},
            'base': {'precio_combustible': 1.2, 'probabilidad': 0.5},
            'pesimista': {'precio_combustible': 1.8, 'probabilidad': 0.3}
        }
        
        resultados = {}
        
        for nombre, parametros in escenarios_combustible.items():
            condiciones = {'precio_combustible': parametros['precio_combustible']}
            costos = self.calculador.calcular_costo_ruta_dinamico(vehiculo_id, distancia_km, tiempo_horas, condiciones)
            
            resultados[nombre] = {
                'costos': costos,
                'costo_total': sum(costos.values()),
                'probabilidad': parametros['probabilidad'],
                'variacion_vs_base': 0  # Se calculará después
            }
        
        # Calcular variaciones vs escenario base
        costo_base = resultados['base']['costo_total']
        for escenario in resultados.values():
            escenario['variacion_vs_base'] = ((escenario['costo_total'] - costo_base) / costo_base) * 100
        
        return resultados
    
    def analizar_escenario_trafico(self, vehiculo_id: str, distancia_km: float) -> Dict[str, Dict]:
        """Analiza escenarios de variación de tráfico"""
        
        escenarios_trafico = {
            'sin_trafico': {'factor_velocidad': 1.0, 'probabilidad': 0.1},
            'trafico_normal': {'factor_velocidad': 0.8, 'probabilidad': 0.6},
            'trafico_intenso': {'factor_velocidad': 0.5, 'probabilidad': 0.3}
        }
        
        resultados = {}
        
        for nombre, parametros in escenarios_trafico.items():
            factor_velocidad = parametros['factor_velocidad']
            tiempo_horas = (distancia_km / 35) / factor_velocidad  # Velocidad base 35 km/h
            
            condiciones = {'eficiencia_conduccion': factor_velocidad}
            costos = self.calculador.calcular_costo_ruta_dinamico(vehiculo_id, distancia_km, tiempo_horas, condiciones)
            
            resultados[nombre] = {
                'costos': costos,
                'costo_total': sum(costos.values()),
                'tiempo_horas': tiempo_horas,
                'probabilidad': parametros['probabilidad']
            }
        
        return resultados
    
    def calcular_valor_esperado(self, escenarios: Dict[str, Dict]) -> Dict[str, float]:
        """Calcula valor esperado de costos"""
        
        valor_esperado = {}
        
        # Obtener todas las categorías de costo
        categorias = set()
        for escenario in escenarios.values():
            categorias.update(escenario['costos'].keys())
        
        # Calcular valor esperado por categoría
        for categoria in categorias:
            valor_esperado[categoria] = sum(
                escenario['costos'].get(categoria, 0) * escenario['probabilidad']
                for escenario in escenarios.values()
            )
        
        # Calcular valor esperado total
        valor_esperado['total'] = sum(
            escenario['costo_total'] * escenario['probabilidad']
            for escenario in escenarios.values()
        )
        
        return valor_esperado

class OptimizadorCostosTiempoReal:
    """Optimizador de costos en tiempo real"""
    
    def __init__(self, calculador_costos: CalculadorCostosAvanzado):
        self.calculador = calculador_costos
        self.modelo_prediccion = None
        self.historial_optimizaciones = []
    
    def entrenar_modelo_prediccion(self, datos_historicos: List[Dict]):
        """Entrena modelo para predecir costos"""
        
        if len(datos_historicos) < 50:
            return False
        
        df = pd.DataFrame(datos_historicos)
        
        # Preparar características
        X = df[['distancia_km', 'tiempo_horas', 'precio_combustible', 'factor_trafico']].values
        y = df['costo_total'].values
        
        # Entrenar modelo
        self.modelo_prediccion = LinearRegression()
        self.modelo_prediccion.fit(X, y)
        
        return True
    
    def optimizar_ruta_tiempo_real(self, vehiculo_id: str, puntos_entrega: List[Dict], 
                                  condiciones_actuales: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza ruta en tiempo real considerando costos"""
        
        # Calcular costos para diferentes secuencias
        secuencias_posibles = self._generar_secuencias_posibles(puntos_entrega)
        
        mejor_secuencia = None
        menor_costo = float('inf')
        resultados_detallados = []
        
        for secuencia in secuencias_posibles:
            # Calcular distancia y tiempo de la secuencia
            distancia, tiempo = self._calcular_distancia_tiempo_secuencia(secuencia, puntos_entrega)
            
            # Calcular costos
            costos = self.calculador.calcular_costo_ruta_dinamico(
                vehiculo_id, distancia, tiempo, condiciones_actuales
            )
            
            costo_total = sum(costos.values())
            
            resultados_detallados.append({
                'secuencia': secuencia,
                'distancia': distancia,
                'tiempo': tiempo,
                'costos': costos,
                'costo_total': costo_total
            })
            
            if costo_total < menor_costo:
                menor_costo = costo_total
                mejor_secuencia = secuencia
        
        # Encontrar mejor resultado
        mejor_resultado = next(r for r in resultados_detallados if r['secuencia'] == mejor_secuencia)
        
        # Guardar en historial
        self.historial_optimizaciones.append({
            'timestamp': datetime.now(),
            'vehiculo_id': vehiculo_id,
            'mejor_secuencia': mejor_secuencia,
            'costo_optimizado': menor_costo,
            'condiciones': condiciones_actuales
        })
        
        return {
            'mejor_secuencia': mejor_secuencia,
            'costo_optimizado': menor_costo,
            'resultados_todos': resultados_detallados,
            'ahorro_vs_original': self._calcular_ahorro(mejor_resultado, resultados_detallados)
        }
    
    def _generar_secuencias_posibles(self, puntos_entrega: List[Dict]) -> List[List[int]]:
        """Genera secuencias posibles de entrega"""
        import itertools
        
        indices = list(range(len(puntos_entrega)))
        
        # Para más de 5 puntos, usar heurística
        if len(indices) > 5:
            # Generar solo algunas secuencias representativas
            secuencias = [indices]  # Secuencia original
            secuencias.append(list(reversed(indices)))  # Secuencia inversa
            
            # Algunas permutaciones aleatorias
            for _ in range(min(10, len(indices) * 2)):
                secuencia = indices.copy()
                np.random.shuffle(secuencia)
                secuencias.append(secuencia)
            
            return secuencias
        else:
            # Generar todas las permutaciones
            return list(itertools.permutations(indices))
    
    def _calcular_distancia_tiempo_secuencia(self, secuencia: List[int], 
                                           puntos_entrega: List[Dict]) -> Tuple[float, float]:
        """Calcula distancia y tiempo total de una secuencia"""
        
        distancia_total = 0.0
        tiempo_total = 0.0
        
        # Ubicación inicial (simplificada)
        ubicacion_actual = (-12.0464, -77.0428)
        
        for punto_idx in secuencia:
            punto = puntos_entrega[punto_idx]
            
            # Calcular distancia (simplificada)
            distancia = np.sqrt(
                (punto['latitud'] - ubicacion_actual[0])**2 + 
                (punto['longitud'] - ubicacion_actual[1])**2
            ) * 111  # Aproximación km
            
            distancia_total += distancia
            tiempo_total += distancia / 35  # Velocidad promedio 35 km/h
            tiempo_total += punto.get('tiempo_servicio', 15) / 60  # Tiempo de servicio
            
            ubicacion_actual = (punto['latitud'], punto['longitud'])
        
        return distancia_total, tiempo_total
    
    def _calcular_ahorro(self, mejor_resultado: Dict, todos_resultados: List[Dict]) -> float:
        """Calcula ahorro vs secuencia original"""
        
        if len(todos_resultados) < 2:
            return 0.0
        
        # Asumir que la primera secuencia es la original
        costo_original = todos_resultados[0]['costo_total']
        costo_optimizado = mejor_resultado['costo_total']
        
        return ((costo_original - costo_optimizado) / costo_original) * 100

class AnalizadorRentabilidadCliente:
    """Analizador de rentabilidad por cliente"""
    
    def __init__(self, calculador_costos: CalculadorCostosAvanzado):
        self.calculador = calculador_costos
        self.datos_clientes = {}
    
    def agregar_datos_cliente(self, cliente_id: str, datos: Dict[str, Any]):
        """Agrega datos de un cliente"""
        
        self.datos_clientes[cliente_id] = {
            'id': cliente_id,
            'nombre': datos.get('nombre', ''),
            'ubicacion': datos.get('ubicacion', (0, 0)),
            'frecuencia_entregas': datos.get('frecuencia_entregas', 1),
            'valor_promedio_pedido': datos.get('valor_promedio_pedido', 0),
            'tipo_cliente': datos.get('tipo_cliente', 'estandar'),
            'descuentos_aplicados': datos.get('descuentos_aplicados', 0),
            'costo_servicio_personalizado': datos.get('costo_servicio_personalizado', 0),
            'historial_pagos': datos.get('historial_pagos', []),
            'satisfaccion_promedio': datos.get('satisfaccion_promedio', 0.8)
        }
    
    def calcular_rentabilidad_cliente(self, cliente_id: str, vehiculo_id: str, 
                                    distancia_km: float, tiempo_horas: float) -> Dict[str, Any]:
        """Calcula rentabilidad de un cliente específico"""
        
        if cliente_id not in self.datos_clientes:
            raise ValueError(f"Cliente {cliente_id} no encontrado")
        
        cliente = self.datos_clientes[cliente_id]
        
        # Calcular costos de entrega
        condiciones = {'precio_combustible': 1.2, 'factor_trafico': 0.8}
        costos_entrega = self.calculador.calcular_costo_ruta_dinamico(
            vehiculo_id, distancia_km, tiempo_horas, condiciones
        )
        
        costo_total_entrega = sum(costos_entrega.values())
        
        # Calcular ingresos
        ingresos_por_entrega = cliente['valor_promedio_pedido']
        ingresos_mensuales = ingresos_por_entrega * cliente['frecuencia_entregas'] * 4.33  # Promedio semanas/mes
        
        # Calcular costos mensuales
        costos_mensuales = costo_total_entrega * cliente['frecuencia_entregas'] * 4.33
        
        # Aplicar descuentos
        ingresos_netos = ingresos_mensuales * (1 - cliente['descuentos_aplicados'] / 100)
        
        # Calcular métricas de rentabilidad
        margen_bruto = ingresos_netos - costos_mensuales
        margen_porcentaje = (margen_bruto / ingresos_netos) * 100 if ingresos_netos > 0 else 0
        
        # Calcular valor de vida del cliente (CLV simplificado)
        meses_promedio_cliente = 24  # Estimación
        clv = margen_bruto * meses_promedio_cliente
        
        # Calcular ROI
        roi = (margen_bruto / costos_mensuales) * 100 if costos_mensuales > 0 else 0
        
        return {
            'cliente_id': cliente_id,
            'ingresos_mensuales': ingresos_mensuales,
            'costos_mensuales': costos_mensuales,
            'margen_bruto': margen_bruto,
            'margen_porcentaje': margen_porcentaje,
            'clv': clv,
            'roi': roi,
            'costo_por_entrega': costo_total_entrega,
            'valor_por_entrega': ingresos_por_entrega,
            'frecuencia_entregas': cliente['frecuencia_entregas'],
            'satisfaccion': cliente['satisfaccion_promedio'],
            'tipo_cliente': cliente['tipo_cliente']
        }
    
    def analizar_portfolio_clientes(self) -> Dict[str, Any]:
        """Analiza portfolio completo de clientes"""
        
        analisis_portfolio = {
            'clientes_rentables': [],
            'clientes_marginales': [],
            'clientes_no_rentables': [],
            'metricas_generales': {}
        }
        
        ingresos_totales = 0
        costos_totales = 0
        clv_total = 0
        
        for cliente_id in self.datos_clientes.keys():
            # Usar valores promedio para el análisis
            rentabilidad = self.calcular_rentabilidad_cliente(
                cliente_id, 'V001', 25.0, 1.5  # Valores promedio
            )
            
            if rentabilidad['margen_porcentaje'] > 20:
                analisis_portfolio['clientes_rentables'].append(rentabilidad)
            elif rentabilidad['margen_porcentaje'] > 5:
                analisis_portfolio['clientes_marginales'].append(rentabilidad)
            else:
                analisis_portfolio['clientes_no_rentables'].append(rentabilidad)
            
            ingresos_totales += rentabilidad['ingresos_mensuales']
            costos_totales += rentabilidad['costos_mensuales']
            clv_total += rentabilidad['clv']
        
        # Calcular métricas generales
        analisis_portfolio['metricas_generales'] = {
            'total_clientes': len(self.datos_clientes),
            'ingresos_totales_mensuales': ingresos_totales,
            'costos_totales_mensuales': costos_totales,
            'margen_total': ingresos_totales - costos_totales,
            'margen_promedio': ((ingresos_totales - costos_totales) / ingresos_totales) * 100 if ingresos_totales > 0 else 0,
            'clv_promedio': clv_total / len(self.datos_clientes) if self.datos_clientes else 0,
            'clientes_rentables_pct': len(analisis_portfolio['clientes_rentables']) / len(self.datos_clientes) * 100 if self.datos_clientes else 0
        }
        
        return analisis_portfolio

def ejemplo_analisis_costos_avanzado():
    """Ejemplo del sistema avanzado de análisis de costos"""
    
    print("=" * 80)
    print("SISTEMA AVANZADO DE ANÁLISIS DE COSTOS LOGÍSTICOS")
    print("=" * 80)
    
    # Crear calculador avanzado
    calculador = CalculadorCostosAvanzado()
    
    print("\n🚚 Creando modelos de vehículos...")
    
    # Crear modelo para furgón
    modelo_furgon = calculador.crear_modelo_vehiculo(
        'V001', 'furgon', {
            'valor_vehiculo': 45000,
            'consumo_combustible': 0.12,
            'precio_combustible': 1.2,
            'costo_mantenimiento_por_km': 0.25,
            'costo_conductor_por_hora': 15.0,
            'costo_seguro_anual': 2000,
            'emisiones_co2_por_km': 0.2,
            'precio_carbono': 50,
            'ciclo_vida_anos': 5,
            'valor_residual': 5000
        }
    )
    
    # Crear modelo para van eléctrica
    modelo_electrica = calculador.crear_modelo_vehiculo(
        'V002', 'van_electrica', {
            'valor_vehiculo': 60000,
            'consumo_combustible': 0.0,  # Eléctrico
            'precio_combustible': 0.3,  # Costo electricidad
            'costo_mantenimiento_por_km': 0.15,
            'costo_conductor_por_hora': 12.0,
            'costo_seguro_anual': 1800,
            'emisiones_co2_por_km': 0.0,
            'precio_carbono': 50,
            'ciclo_vida_anos': 8,
            'valor_residual': 8000
        }
    )
    
    print("✅ Modelos de vehículos creados!")
    
    print("\n💰 Calculando TCO (Costo Total de Propiedad)...")
    
    # Calcular TCO para ambos vehículos
    tco_furgon = calculador.calcular_tco('V001', 50000)  # 50,000 km/año
    tco_electrica = calculador.calcular_tco('V002', 50000)
    
    print(f"   Furgón:")
    print(f"     TCO Total: ${tco_furgon.tco_total:,.2f}")
    print(f"     TCO Anual: ${tco_furgon.tco_anual:,.2f}")
    print(f"     TCO por km: ${tco_furgon.tco_por_km:.3f}")
    
    print(f"   Van Eléctrica:")
    print(f"     TCO Total: ${tco_electrica.tco_total:,.2f}")
    print(f"     TCO Anual: ${tco_electrica.tco_anual:,.2f}")
    print(f"     TCO por km: ${tco_electrica.tco_por_km:.3f}")
    
    print("\n📊 Análisis de escenarios...")
    
    # Crear analizador de escenarios
    analizador_escenarios = AnalizadorEscenarios(calculador)
    
    # Analizar escenarios de combustible
    escenarios_combustible = analizador_escenarios.analizar_escenario_combustible(
        'V001', 50.0, 2.0
    )
    
    print("   Escenarios de precio de combustible:")
    for escenario, datos in escenarios_combustible.items():
        print(f"     {escenario.capitalize()}: ${datos['costo_total']:.2f} "
              f"({datos['variacion_vs_base']:+.1f}%)")
    
    # Calcular valor esperado
    valor_esperado = analizador_escenarios.calcular_valor_esperado(escenarios_combustible)
    print(f"   Valor esperado: ${valor_esperado['total']:.2f}")
    
    print("\n⚡ Optimización en tiempo real...")
    
    # Crear optimizador en tiempo real
    optimizador_tiempo_real = OptimizadorCostosTiempoReal(calculador)
    
    # Simular datos históricos para entrenar modelo
    datos_historicos = []
    for i in range(100):
        datos_historicos.append({
            'distancia_km': np.random.uniform(10, 100),
            'tiempo_horas': np.random.uniform(0.5, 4),
            'precio_combustible': np.random.uniform(1.0, 1.5),
            'factor_trafico': np.random.uniform(0.5, 1.0),
            'costo_total': np.random.uniform(50, 200)
        })
    
    # Entrenar modelo
    modelo_entrenado = optimizador_tiempo_real.entrenar_modelo_prediccion(datos_historicos)
    
    if modelo_entrenado:
        print("   ✅ Modelo de predicción entrenado!")
        
        # Optimizar ruta
        puntos_entrega = [
            {'latitud': -12.0464, 'longitud': -77.0428, 'tiempo_servicio': 15},
            {'latitud': -12.0564, 'longitud': -77.0328, 'tiempo_servicio': 20},
            {'latitud': -12.0364, 'longitud': -77.0528, 'tiempo_servicio': 25}
        ]
        
        condiciones_actuales = {'precio_combustible': 1.3, 'factor_trafico': 0.7}
        
        optimizacion = optimizador_tiempo_real.optimizar_ruta_tiempo_real(
            'V001', puntos_entrega, condiciones_actuales
        )
        
        print(f"   Mejor secuencia: {optimizacion['mejor_secuencia']}")
        print(f"   Costo optimizado: ${optimizacion['costo_optimizado']:.2f}")
        print(f"   Ahorro: {optimizacion['ahorro_vs_original']:.1f}%")
    
    print("\n👥 Análisis de rentabilidad por cliente...")
    
    # Crear analizador de rentabilidad
    analizador_rentabilidad = AnalizadorRentabilidadCliente(calculador)
    
    # Agregar datos de clientes
    clientes_ejemplo = [
        {
            'id': 'C001',
            'nombre': 'Cliente Premium',
            'ubicacion': (-12.0464, -77.0428),
            'frecuencia_entregas': 20,
            'valor_promedio_pedido': 150,
            'tipo_cliente': 'premium',
            'descuentos_aplicados': 5,
            'satisfaccion_promedio': 0.95
        },
        {
            'id': 'C002',
            'nombre': 'Cliente Estándar',
            'ubicacion': (-12.0564, -77.0328),
            'frecuencia_entregas': 8,
            'valor_promedio_pedido': 80,
            'tipo_cliente': 'estandar',
            'descuentos_aplicados': 0,
            'satisfaccion_promedio': 0.85
        },
        {
            'id': 'C003',
            'nombre': 'Cliente Marginal',
            'ubicacion': (-12.0364, -77.0528),
            'frecuencia_entregas': 3,
            'valor_promedio_pedido': 40,
            'tipo_cliente': 'marginal',
            'descuentos_aplicados': 10,
            'satisfaccion_promedio': 0.70
        }
    ]
    
    for cliente_data in clientes_ejemplo:
        analizador_rentabilidad.agregar_datos_cliente(cliente_data['id'], cliente_data)
    
    # Analizar portfolio de clientes
    portfolio = analizador_rentabilidad.analizar_portfolio_clientes()
    
    print("   Análisis de portfolio:")
    print(f"     Total clientes: {portfolio['metricas_generales']['total_clientes']}")
    print(f"     Ingresos mensuales: ${portfolio['metricas_generales']['ingresos_totales_mensuales']:,.2f}")
    print(f"     Margen promedio: {portfolio['metricas_generales']['margen_promedio']:.1f}%")
    print(f"     CLV promedio: ${portfolio['metricas_generales']['clv_promedio']:,.2f}")
    print(f"     Clientes rentables: {portfolio['metricas_generales']['clientes_rentables_pct']:.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS AVANZADO DE COSTOS COMPLETADO")
    print("=" * 80)
    
    return {
        'calculador': calculador,
        'tco_furgon': tco_furgon,
        'tco_electrica': tco_electrica,
        'escenarios_combustible': escenarios_combustible,
        'optimizador_tiempo_real': optimizador_tiempo_real,
        'portfolio_clientes': portfolio
    }

if __name__ == "__main__":
    ejemplo_analisis_costos_avanzado()



