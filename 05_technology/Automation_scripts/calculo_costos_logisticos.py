"""
Módulo de Cálculo de Costos Logísticos
=====================================

Este módulo calcula costos detallados por kilómetro considerando:
- Combustible
- Mantenimiento
- Depreciación
- Salarios de conductores
- Seguros
- Peajes
- Costos operativos variables
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import math

@dataclass
class CostosVehiculo:
    """Estructura de costos por tipo de vehículo"""
    tipo_vehiculo: str
    costo_combustible_por_litro: float  # USD/L
    consumo_promedio_litro_por_km: float  # L/km
    costo_mantenimiento_por_km: float  # USD/km
    costo_depreciacion_por_km: float  # USD/km
    costo_seguro_por_dia: float  # USD/día
    costo_peaje_promedio_por_km: float  # USD/km
    costo_conductor_por_hora: float  # USD/hora
    costo_administrativo_por_km: float  # USD/km

@dataclass
class CostosRuta:
    """Costos detallados de una ruta específica"""
    distancia_total_km: float
    tiempo_total_horas: float
    costo_combustible: float
    costo_mantenimiento: float
    costo_depreciacion: float
    costo_seguro: float
    costo_peaje: float
    costo_conductor: float
    costo_administrativo: float
    costo_total: float
    costo_por_km: float
    costo_por_hora: float

class CalculadorCostos:
    """Calcula costos detallados de operación logística"""
    
    def __init__(self):
        self.costos_vehiculos = self._inicializar_costos_vehiculos()
        self.tarifas_peaje = self._inicializar_tarifas_peaje()
        self.precios_combustible = self._inicializar_precios_combustible()
        
    def _inicializar_costos_vehiculos(self) -> Dict[str, CostosVehiculo]:
        """Inicializa costos base por tipo de vehículo"""
        return {
            "motocicleta": CostosVehiculo(
                tipo_vehiculo="motocicleta",
                costo_combustible_por_litro=1.2,
                consumo_promedio_litro_por_km=0.05,
                costo_mantenimiento_por_km=0.15,
                costo_depreciacion_por_km=0.25,
                costo_seguro_por_dia=5.0,
                costo_peaje_promedio_por_km=0.02,
                costo_conductor_por_hora=8.0,
                costo_administrativo_por_km=0.10
            ),
            "furgon": CostosVehiculo(
                tipo_vehiculo="furgon",
                costo_combustible_por_litro=1.2,
                consumo_promedio_litro_por_km=0.12,
                costo_mantenimiento_por_km=0.25,
                costo_depreciacion_por_km=0.40,
                costo_seguro_por_dia=12.0,
                costo_peaje_promedio_por_km=0.05,
                costo_conductor_por_hora=12.0,
                costo_administrativo_por_km=0.15
            ),
            "camion_pequeño": CostosVehiculo(
                tipo_vehiculo="camion_pequeño",
                costo_combustible_por_litro=1.2,
                consumo_promedio_litro_por_km=0.15,
                costo_mantenimiento_por_km=0.35,
                costo_depreciacion_por_km=0.60,
                costo_seguro_por_dia=18.0,
                costo_peaje_promedio_por_km=0.08,
                costo_conductor_por_hora=15.0,
                costo_administrativo_por_km=0.20
            ),
            "camion_grande": CostosVehiculo(
                tipo_vehiculo="camion_grande",
                costo_combustible_por_litro=1.2,
                consumo_promedio_litro_por_km=0.25,
                costo_mantenimiento_por_km=0.50,
                costo_depreciacion_por_km=0.80,
                costo_seguro_por_dia=25.0,
                costo_peaje_promedio_por_km=0.12,
                costo_conductor_por_hora=18.0,
                costo_administrativo_por_km=0.25
            )
        }
    
    def _inicializar_tarifas_peaje(self) -> Dict[str, float]:
        """Inicializa tarifas de peaje por región/ruta"""
        return {
            "panamericana_norte": 0.15,  # USD/km
            "panamericana_sur": 0.12,
            "carretera_central": 0.10,
            "via_expresa": 0.20,
            "carretera_interoceánica": 0.08,
            "urbano": 0.05,
            "rural": 0.02
        }
    
    def _inicializar_precios_combustible(self) -> Dict[str, float]:
        """Inicializa precios de combustible por tipo"""
        return {
            "gasolina_regular": 1.15,  # USD/L
            "gasolina_premium": 1.25,
            "diesel": 1.10,
            "gnv": 0.80,
            "electrico": 0.30  # USD equivalente por km
        }
    
    def calcular_costo_ruta(self, tipo_vehiculo: str, distancia_km: float, 
                          tiempo_horas: float, tipo_ruta: str = "urbano",
                          factor_trafico: float = 1.0) -> CostosRuta:
        """Calcula costos detallados de una ruta"""
        
        if tipo_vehiculo not in self.costos_vehiculos:
            raise ValueError(f"Tipo de vehículo no válido: {tipo_vehiculo}")
        
        costos_vehiculo = self.costos_vehiculos[tipo_vehiculo]
        
        # Ajustar consumo por factor de tráfico
        consumo_ajustado = costos_vehiculo.consumo_promedio_litro_por_km * factor_trafico
        
        # Calcular costos individuales
        costo_combustible = distancia_km * consumo_ajustado * costos_vehiculo.costo_combustible_por_litro
        costo_mantenimiento = distancia_km * costos_vehiculo.costo_mantenimiento_por_km
        costo_depreciacion = distancia_km * costos_vehiculo.costo_depreciacion_por_km
        costo_seguro = (tiempo_horas / 24) * costos_vehiculo.costo_seguro_por_dia
        costo_peaje = distancia_km * self.tarifas_peaje.get(tipo_ruta, 0.05)
        costo_conductor = tiempo_horas * costos_vehiculo.costo_conductor_por_hora
        costo_administrativo = distancia_km * costos_vehiculo.costo_administrativo_por_km
        
        # Calcular totales
        costo_total = (costo_combustible + costo_mantenimiento + costo_depreciacion + 
                      costo_seguro + costo_peaje + costo_conductor + costo_administrativo)
        
        costo_por_km = costo_total / distancia_km if distancia_km > 0 else 0
        costo_por_hora = costo_total / tiempo_horas if tiempo_horas > 0 else 0
        
        return CostosRuta(
            distancia_total_km=distancia_km,
            tiempo_total_horas=tiempo_horas,
            costo_combustible=costo_combustible,
            costo_mantenimiento=costo_mantenimiento,
            costo_depreciacion=costo_depreciacion,
            costo_seguro=costo_seguro,
            costo_peaje=costo_peaje,
            costo_conductor=costo_conductor,
            costo_administrativo=costo_administrativo,
            costo_total=costo_total,
            costo_por_km=costo_por_km,
            costo_por_hora=costo_por_hora
        )
    
    def calcular_costo_flota(self, rutas: List[CostosRuta]) -> Dict[str, float]:
        """Calcula costos totales de una flota de vehículos"""
        
        total_distancia = sum(r.distancia_total_km for r in rutas)
        total_tiempo = sum(r.tiempo_total_horas for r in rutas)
        total_combustible = sum(r.costo_combustible for r in rutas)
        total_mantenimiento = sum(r.costo_mantenimiento for r in rutas)
        total_depreciacion = sum(r.costo_depreciacion for r in rutas)
        total_seguro = sum(r.costo_seguro for r in rutas)
        total_peaje = sum(r.costo_peaje for r in rutas)
        total_conductor = sum(r.costo_conductor for r in rutas)
        total_administrativo = sum(r.costo_administrativo for r in rutas)
        costo_total_flota = sum(r.costo_total for r in rutas)
        
        return {
            "total_distancia_km": total_distancia,
            "total_tiempo_horas": total_tiempo,
            "total_combustible_usd": total_combustible,
            "total_mantenimiento_usd": total_mantenimiento,
            "total_depreciacion_usd": total_depreciacion,
            "total_seguro_usd": total_seguro,
            "total_peaje_usd": total_peaje,
            "total_conductor_usd": total_conductor,
            "total_administrativo_usd": total_administrativo,
            "costo_total_flota_usd": costo_total_flota,
            "costo_promedio_por_km": costo_total_flota / total_distancia if total_distancia > 0 else 0,
            "costo_promedio_por_hora": costo_total_flota / total_tiempo if total_tiempo > 0 else 0,
            "numero_vehiculos": len(rutas)
        }
    
    def optimizar_costo_por_tipo_vehiculo(self, distancia_km: float, tiempo_horas: float,
                                        tipo_ruta: str = "urbano") -> Dict[str, CostosRuta]:
        """Compara costos entre diferentes tipos de vehículos para la misma ruta"""
        
        resultados = {}
        
        for tipo_vehiculo in self.costos_vehiculos.keys():
            costos = self.calcular_costo_ruta(tipo_vehiculo, distancia_km, tiempo_horas, tipo_ruta)
            resultados[tipo_vehiculo] = costos
        
        return resultados
    
    def calcular_break_even(self, costo_ruta: CostosRuta, precio_entrega: float) -> Dict[str, float]:
        """Calcula punto de equilibrio y rentabilidad"""
        
        margen_bruto = precio_entrega - costo_ruta.costo_total
        margen_porcentaje = (margen_bruto / precio_entrega) * 100 if precio_entrega > 0 else 0
        
        # Calcular número mínimo de entregas para cubrir costos fijos diarios
        costo_fijo_diario = 50.0  # Estimación de costos fijos
        entregas_minimas = math.ceil(costo_fijo_diario / margen_bruto) if margen_bruto > 0 else float('inf')
        
        return {
            "precio_entrega": precio_entrega,
            "costo_total": costo_ruta.costo_total,
            "margen_bruto": margen_bruto,
            "margen_porcentaje": margen_porcentaje,
            "entregas_minimas_diarias": entregas_minimas,
            "rentable": margen_bruto > 0
        }

class AnalizadorRentabilidad:
    """Analiza rentabilidad de diferentes estrategias logísticas"""
    
    def __init__(self, calculador_costos: CalculadorCostos):
        self.calculador_costos = calculador_costos
    
    def comparar_estrategias_entrega(self, escenarios: List[Dict]) -> Dict[str, Dict]:
        """Compara diferentes estrategias de entrega"""
        
        resultados = {}
        
        for escenario in escenarios:
            nombre = escenario['nombre']
            tipo_vehiculo = escenario['tipo_vehiculo']
            distancia_total = escenario['distancia_total']
            tiempo_total = escenario['tiempo_total']
            numero_entregas = escenario['numero_entregas']
            precio_por_entrega = escenario['precio_por_entrega']
            
            # Calcular costos
            costos = self.calculador_costos.calcular_costo_ruta(
                tipo_vehiculo, distancia_total, tiempo_total
            )
            
            # Calcular ingresos
            ingresos_totales = numero_entregas * precio_por_entrega
            
            # Calcular rentabilidad
            rentabilidad = ingresos_totales - costos.costo_total
            margen_porcentaje = (rentabilidad / ingresos_totales) * 100 if ingresos_totales > 0 else 0
            
            resultados[nombre] = {
                'costos': costos,
                'ingresos_totales': ingresos_totales,
                'rentabilidad': rentabilidad,
                'margen_porcentaje': margen_porcentaje,
                'rentabilidad_por_entrega': rentabilidad / numero_entregas if numero_entregas > 0 else 0,
                'eficiencia_km': ingresos_totales / distancia_total if distancia_total > 0 else 0
            }
        
        return resultados
    
    def calcular_optimizacion_flota(self, demanda_diaria: int, distancia_promedio: float,
                                  tiempo_promedio: float) -> Dict[str, Dict]:
        """Calcula la configuración óptima de flota para una demanda específica"""
        
        configuraciones = []
        
        # Diferentes configuraciones de flota
        configs = [
            {'motocicleta': 5, 'furgon': 0, 'camion_pequeño': 0},
            {'motocicleta': 3, 'furgon': 2, 'camion_pequeño': 0},
            {'motocicleta': 2, 'furgon': 3, 'camion_pequeño': 1},
            {'motocicleta': 0, 'furgon': 4, 'camion_pequeño': 2},
            {'motocicleta': 0, 'furgon': 2, 'camion_pequeño': 3}
        ]
        
        for i, config in enumerate(configs):
            total_vehiculos = sum(config.values())
            capacidad_estimada = (
                config['motocicleta'] * 20 +  # 20 entregas/día por moto
                config['furgon'] * 40 +       # 40 entregas/día por furgón
                config['camion_pequeño'] * 60  # 60 entregas/día por camión pequeño
            )
            
            if capacidad_estimada >= demanda_diaria:
                # Calcular costos diarios
                costos_diarios = 0
                for tipo_vehiculo, cantidad in config.items():
                    if cantidad > 0:
                        costo_vehiculo = self.calculador_costos.calcular_costo_ruta(
                            tipo_vehiculo, distancia_promedio, tiempo_promedio
                        )
                        costos_diarios += costo_vehiculo.costo_total * cantidad
                
                configuraciones.append({
                    'configuracion': config,
                    'total_vehiculos': total_vehiculos,
                    'capacidad_estimada': capacidad_estimada,
                    'costos_diarios': costos_diarios,
                    'costo_por_entrega': costos_diarios / demanda_diaria,
                    'utilizacion_flota': demanda_diaria / capacidad_estimada
                })
        
        # Ordenar por costo por entrega
        configuraciones.sort(key=lambda x: x['costo_por_entrega'])
        
        return {
            'demanda_diaria': demanda_diaria,
            'distancia_promedio': distancia_promedio,
            'tiempo_promedio': tiempo_promedio,
            'configuracion_optima': configuraciones[0] if configuraciones else None,
            'todas_configuraciones': configuraciones
        }

def ejemplo_calculo_costos():
    """Ejemplo de cálculo de costos logísticos"""
    
    print("=== Cálculo de Costos Logísticos ===\n")
    
    # Crear calculador de costos
    calculador = CalculadorCostos()
    
    # Ejemplo 1: Costo de una ruta específica
    print("1. Costo de ruta específica:")
    costo_ruta = calculador.calcular_costo_ruta(
        tipo_vehiculo="furgon",
        distancia_km=50.0,
        tiempo_horas=2.5,
        tipo_ruta="urbano",
        factor_trafico=1.3
    )
    
    print(f"   Vehículo: Furgón")
    print(f"   Distancia: {costo_ruta.distancia_total_km} km")
    print(f"   Tiempo: {costo_ruta.tiempo_total_horas} horas")
    print(f"   Costo combustible: ${costo_ruta.costo_combustible:.2f}")
    print(f"   Costo mantenimiento: ${costo_ruta.costo_mantenimiento:.2f}")
    print(f"   Costo conductor: ${costo_ruta.costo_conductor:.2f}")
    print(f"   Costo total: ${costo_ruta.costo_total:.2f}")
    print(f"   Costo por km: ${costo_ruta.costo_por_km:.2f}")
    
    # Ejemplo 2: Comparación entre tipos de vehículos
    print("\n2. Comparación entre tipos de vehículos:")
    comparacion = calculador.optimizar_costo_por_tipo_vehiculo(30.0, 1.5, "urbano")
    
    for tipo, costos in comparacion.items():
        print(f"   {tipo.capitalize()}: ${costos.costo_total:.2f} (${costos.costo_por_km:.2f}/km)")
    
    # Ejemplo 3: Análisis de rentabilidad
    print("\n3. Análisis de rentabilidad:")
    break_even = calculador.calcular_break_even(costo_ruta, 25.0)
    print(f"   Precio de entrega: ${break_even['precio_entrega']:.2f}")
    print(f"   Margen bruto: ${break_even['margen_bruto']:.2f}")
    print(f"   Margen porcentaje: {break_even['margen_porcentaje']:.1f}%")
    print(f"   Rentable: {'Sí' if break_even['rentable'] else 'No'}")
    
    # Ejemplo 4: Optimización de flota
    print("\n4. Optimización de flota:")
    analizador = AnalizadorRentabilidad(calculador)
    optimizacion = analizador.calcular_optimizacion_flota(
        demanda_diaria=150,
        distancia_promedio=25.0,
        tiempo_promedio=1.2
    )
    
    if optimizacion['configuracion_optima']:
        config_optima = optimizacion['configuracion_optima']
        print(f"   Configuración óptima: {config_optima['configuracion']}")
        print(f"   Costo por entrega: ${config_optima['costo_por_entrega']:.2f}")
        print(f"   Utilización flota: {config_optima['utilizacion_flota']:.1%}")

if __name__ == "__main__":
    ejemplo_calculo_costos()



