"""
Ejemplos Prácticos de Optimización Logística
===========================================

Este archivo contiene ejemplos prácticos y casos de uso comunes
para la optimización de rutas logísticas.
"""

from datetime import datetime, timedelta
from typing import List, Dict
import json

# Importar módulos del sistema
from logistica_optimizacion_rutas import (
    OptimizadorRutas, PuntoEntrega, Vehiculo, TipoVehiculo, TipoEntrega
)
from analisis_trafico_horarios import AnalizadorTrafico, OptimizadorHorarios
from calculo_costos_logisticos import CalculadorCostos, AnalizadorRentabilidad
from integracion_apis_externas import configurar_apis_ejemplo

class EjemplosPracticos:
    """Clase con ejemplos prácticos de optimización logística"""
    
    def __init__(self):
        self.optimizador = OptimizadorRutas()
        self.analizador_trafico = AnalizadorTrafico()
        self.calculador_costos = CalculadorCostos()
        
    def ejemplo_entrega_ultima_milla(self):
        """Ejemplo: Optimización de entregas de última milla en ciudad"""
        
        print("=== EJEMPLO 1: ENTREGAS DE ÚLTIMA MILLA ===\n")
        
        # Crear puntos de entrega urbanos
        puntos_entrega = [
            PuntoEntrega(
                id="E001", direccion="Av. Arequipa 1234", latitud=-12.0464, longitud=-77.0428,
                horario_apertura="09:00", horario_cierre="18:00", tiempo_servicio=10,
                tipo_entrega=TipoEntrega.URGENTE, peso=2.0, volumen=0.05, prioridad=5
            ),
            PuntoEntrega(
                id="E002", direccion="Jr. Larco 567", latitud=-12.0564, longitud=-77.0328,
                horario_apertura="08:00", horario_cierre="20:00", tiempo_servicio=15,
                tipo_entrega=TipoEntrega.ESTANDAR, peso=5.0, volumen=0.1, prioridad=3
            ),
            PuntoEntrega(
                id="E003", direccion="Av. Javier Prado 890", latitud=-12.0364, longitud=-77.0528,
                horario_apertura="10:00", horario_cierre="17:00", tiempo_servicio=20,
                tipo_entrega=TipoEntrega.PROGRAMADA, peso=8.0, volumen=0.2, prioridad=2
            ),
            PuntoEntrega(
                id="E004", direccion="Calle Las Flores 234", latitud=-12.0664, longitud=-77.0228,
                horario_apertura="09:30", horario_cierre="19:00", tiempo_servicio=12,
                tipo_entrega=TipoEntrega.URGENTE, peso=3.0, volumen=0.08, prioridad=4
            ),
            PuntoEntrega(
                id="E005", direccion="Av. Brasil 456", latitud=-12.0264, longitud=-77.0628,
                horario_apertura="08:30", horario_cierre="18:30", tiempo_servicio=18,
                tipo_entrega=TipoEntrega.ESTANDAR, peso=6.0, volumen=0.15, prioridad=3
            )
        ]
        
        # Crear flota de motocicletas para última milla
        vehiculos = [
            Vehiculo(
                id="M001", tipo=TipoVehiculo.MOTOCICLETA, capacidad_peso=50, capacidad_volumen=1,
                consumo_combustible=0.05, costo_por_km=0.3, velocidad_promedio=25,
                conductor_id="C001", ubicacion_actual=(-12.0464, -77.0428)
            ),
            Vehiculo(
                id="M002", tipo=TipoVehiculo.MOTOCICLETA, capacidad_peso=50, capacidad_volumen=1,
                consumo_combustible=0.05, costo_por_km=0.3, velocidad_promedio=25,
                conductor_id="C002", ubicacion_actual=(-12.0464, -77.0428)
            ),
            Vehiculo(
                id="M003", tipo=TipoVehiculo.MOTOCICLETA, capacidad_peso=50, capacidad_volumen=1,
                consumo_combustible=0.05, costo_por_km=0.3, velocidad_promedio=25,
                conductor_id="C003", ubicacion_actual=(-12.0464, -77.0428)
            )
        ]
        
        # Optimizar rutas
        hora_inicio = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        rutas_optimizadas = self.optimizador.optimizar_con_restricciones_horario(
            vehiculos, puntos_entrega, hora_inicio
        )
        
        # Calcular métricas
        metricas = self.optimizador.calcular_metricas_optimizacion(rutas_optimizadas)
        
        print("RESULTADOS:")
        print(f"  Total entregas: {len(puntos_entrega)}")
        print(f"  Vehículos utilizados: {metricas['numero_vehiculos_usados']}")
        print(f"  Distancia total: {metricas['total_distancia_km']:.2f} km")
        print(f"  Tiempo total: {metricas['total_tiempo_minutos']} minutos")
        print(f"  Costo total: ${metricas['total_costo_usd']:.2f}")
        print(f"  Eficiencia: {metricas['eficiencia_combustible']:.2f} km/L")
        
        print("\nRUTAS DETALLADAS:")
        for i, ruta in enumerate(rutas_optimizadas, 1):
            print(f"\n  Ruta {i} - Motocicleta {ruta.vehiculo_id}:")
            print(f"    Entregas: {len(ruta.puntos_entrega)}")
            print(f"    Distancia: {ruta.distancia_total:.2f} km")
            print(f"    Tiempo: {ruta.tiempo_total} min")
            print(f"    Costo: ${ruta.costo_total:.2f}")
            for punto in ruta.puntos_entrega:
                print(f"      - {punto.id}: {punto.direccion}")
        
        return rutas_optimizadas, metricas
    
    def ejemplo_distribucion_empresarial(self):
        """Ejemplo: Distribución empresarial con múltiples tipos de vehículos"""
        
        print("\n=== EJEMPLO 2: DISTRIBUCIÓN EMPRESARIAL ===\n")
        
        # Crear puntos de entrega empresariales
        puntos_entrega = [
            PuntoEntrega(
                id="B001", direccion="Centro Comercial Megaplaza", latitud=-12.0464, longitud=-77.0428,
                horario_apertura="10:00", horario_cierre="22:00", tiempo_servicio=30,
                tipo_entrega=TipoEntrega.ESTANDAR, peso=100.0, volumen=2.0, prioridad=4
            ),
            PuntoEntrega(
                id="B002", direccion="Supermercado Wong", latitud=-12.0564, longitud=-77.0328,
                horario_apertura="08:00", horario_cierre="23:00", tiempo_servicio=25,
                tipo_entrega=TipoEntrega.URGENTE, peso=80.0, volumen=1.5, prioridad=5
            ),
            PuntoEntrega(
                id="B003", direccion="Tienda por Departamentos", latitud=-12.0364, longitud=-77.0528,
                horario_apertura="09:00", horario_cierre="21:00", tiempo_servicio=35,
                tipo_entrega=TipoEntrega.PROGRAMADA, peso=150.0, volumen=3.0, prioridad=3
            ),
            PuntoEntrega(
                id="B004", direccion="Farmacia InkaFarma", latitud=-12.0664, longitud=-77.0228,
                horario_apertura="07:00", horario_cierre="23:59", tiempo_servicio=20,
                tipo_entrega=TipoEntrega.URGENTE, peso=60.0, volumen=1.0, prioridad=5
            ),
            PuntoEntrega(
                id="B005", direccion="Restaurante Chain", latitud=-12.0264, longitud=-77.0628,
                horario_apertura="11:00", horario_cierre="15:00", tiempo_servicio=40,
                tipo_entrega=TipoEntrega.PROGRAMADA, peso=200.0, volumen=4.0, prioridad=2
            )
        ]
        
        # Crear flota mixta
        vehiculos = [
            Vehiculo(
                id="F001", tipo=TipoVehiculo.FURGON, capacidad_peso=500, capacidad_volumen=10,
                consumo_combustible=0.12, costo_por_km=0.8, velocidad_promedio=35,
                conductor_id="C001", ubicacion_actual=(-12.0464, -77.0428)
            ),
            Vehiculo(
                id="C001", tipo=TipoVehiculo.CAMION_PEQUEÑO, capacidad_peso=1000, capacidad_volumen=20,
                consumo_combustible=0.15, costo_por_km=1.2, velocidad_promedio=30,
                conductor_id="C002", ubicacion_actual=(-12.0464, -77.0428)
            ),
            Vehiculo(
                id="C002", tipo=TipoVehiculo.CAMION_GRANDE, capacidad_peso=2000, capacidad_volumen=40,
                consumo_combustible=0.25, costo_por_km=1.8, velocidad_promedio=25,
                conductor_id="C003", ubicacion_actual=(-12.0464, -77.0428)
            )
        ]
        
        # Optimizar rutas
        hora_inicio = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        rutas_optimizadas = self.optimizador.optimizar_con_restricciones_horario(
            vehiculos, puntos_entrega, hora_inicio
        )
        
        # Calcular métricas
        metricas = self.optimizador.calcular_metricas_optimizacion(rutas_optimizadas)
        
        print("RESULTADOS:")
        print(f"  Total entregas: {len(puntos_entrega)}")
        print(f"  Vehículos utilizados: {metricas['numero_vehiculos_usados']}")
        print(f"  Distancia total: {metricas['total_distancia_km']:.2f} km")
        print(f"  Tiempo total: {metricas['total_tiempo_minutos']} minutos")
        print(f"  Costo total: ${metricas['total_costo_usd']:.2f}")
        print(f"  Costo por km: ${metricas['promedio_costo_por_km']:.2f}")
        
        print("\nRUTAS DETALLADAS:")
        for i, ruta in enumerate(rutas_optimizadas, 1):
            print(f"\n  Ruta {i} - {ruta.vehiculo_id}:")
            print(f"    Entregas: {len(ruta.puntos_entrega)}")
            print(f"    Distancia: {ruta.distancia_total:.2f} km")
            print(f"    Tiempo: {ruta.tiempo_total} min")
            print(f"    Costo: ${ruta.costo_total:.2f}")
            peso_total = sum(p.peso for p in ruta.puntos_entrega)
            volumen_total = sum(p.volumen for p in ruta.puntos_entrega)
            print(f"    Carga: {peso_total:.1f} kg, {volumen_total:.1f} m³")
        
        return rutas_optimizadas, metricas
    
    def ejemplo_analisis_costos(self):
        """Ejemplo: Análisis detallado de costos"""
        
        print("\n=== EJEMPLO 3: ANÁLISIS DE COSTOS ===\n")
        
        # Escenarios de comparación
        escenarios = [
            {
                'nombre': 'Motocicletas',
                'tipo_vehiculo': 'motocicleta',
                'distancia_total': 80.0,
                'tiempo_total': 4.0,
                'numero_entregas': 20,
                'precio_por_entrega': 8.0
            },
            {
                'nombre': 'Furgones',
                'tipo_vehiculo': 'furgon',
                'distancia_total': 60.0,
                'tiempo_total': 3.5,
                'numero_entregas': 15,
                'precio_por_entrega': 12.0
            },
            {
                'nombre': 'Camiones Pequeños',
                'tipo_vehiculo': 'camion_pequeño',
                'distancia_total': 40.0,
                'tiempo_total': 3.0,
                'numero_entregas': 10,
                'precio_por_entrega': 20.0
            }
        ]
        
        # Analizar rentabilidad
        analizador = AnalizadorRentabilidad(self.calculador_costos)
        resultados = analizador.comparar_estrategias_entrega(escenarios)
        
        print("COMPARACIÓN DE ESTRATEGIAS:")
        print("-" * 80)
        print(f"{'Estrategia':<15} {'Ingresos':<10} {'Costos':<10} {'Rentabilidad':<12} {'Margen %':<10}")
        print("-" * 80)
        
        for nombre, resultado in resultados.items():
            print(f"{nombre:<15} ${resultado['ingresos_totales']:<9.2f} "
                  f"${resultado['costos'].costo_total:<9.2f} "
                  f"${resultado['rentabilidad']:<11.2f} "
                  f"{resultado['margen_porcentaje']:<9.1f}%")
        
        # Encontrar estrategia más rentable
        mejor_estrategia = max(resultados.items(), key=lambda x: x[1]['rentabilidad'])
        print(f"\n✓ Estrategia más rentable: {mejor_estrategia[0]}")
        print(f"  Rentabilidad: ${mejor_estrategia[1]['rentabilidad']:.2f}")
        print(f"  Margen: {mejor_estrategia[1]['margen_porcentaje']:.1f}%")
        
        return resultados
    
    def ejemplo_optimizacion_flota(self):
        """Ejemplo: Optimización de configuración de flota"""
        
        print("\n=== EJEMPLO 4: OPTIMIZACIÓN DE FLOTA ===\n")
        
        # Parámetros de demanda
        demanda_diaria = 200
        distancia_promedio = 15.0
        tiempo_promedio = 0.8
        
        # Analizar configuraciones óptimas
        analizador = AnalizadorRentabilidad(self.calculador_costos)
        optimizacion = analizador.calcular_optimizacion_flota(
            demanda_diaria, distancia_promedio, tiempo_promedio
        )
        
        print("ANÁLISIS DE CONFIGURACIÓN DE FLOTA:")
        print(f"  Demanda diaria: {demanda_diaria} entregas")
        print(f"  Distancia promedio: {distancia_promedio} km")
        print(f"  Tiempo promedio: {tiempo_promedio} horas")
        
        if optimizacion['configuracion_optima']:
            config = optimizacion['configuracion_optima']
            print(f"\n✓ CONFIGURACIÓN ÓPTIMA:")
            print(f"  Configuración: {config['configuracion']}")
            print(f"  Total vehículos: {config['total_vehiculos']}")
            print(f"  Capacidad estimada: {config['capacidad_estimada']} entregas/día")
            print(f"  Costos diarios: ${config['costos_diarios']:.2f}")
            print(f"  Costo por entrega: ${config['costo_por_entrega']:.2f}")
            print(f"  Utilización flota: {config['utilizacion_flota']:.1%}")
        
        print("\nTODAS LAS CONFIGURACIONES:")
        print("-" * 70)
        print(f"{'Configuración':<25} {'Vehículos':<10} {'Costo/Entrega':<15} {'Utilización':<12}")
        print("-" * 70)
        
        for config in optimizacion['todas_configuraciones']:
            config_str = str(config['configuracion']).replace("'", "")[:20]
            print(f"{config_str:<25} {config['total_vehiculos']:<10} "
                  f"${config['costo_por_entrega']:<14.2f} {config['utilizacion_flota']:<11.1%}")
        
        return optimizacion
    
    def ejemplo_integracion_apis(self):
        """Ejemplo: Integración con APIs externas"""
        
        print("\n=== EJEMPLO 5: INTEGRACIÓN CON APIs ===\n")
        
        # Configurar APIs
        gestor_apis = configurar_apis_ejemplo()
        
        # Simular obtención de datos en tiempo real
        print("OBTENIENDO DATOS EN TIEMPO REAL:")
        
        # Datos de ejemplo (en producción vendrían de APIs reales)
        datos_trafico = {
            'nivel_trafico': 3,
            'tiempo_adicional': 15,
            'factor_velocidad': 0.7
        }
        
        datos_clima = {
            'temperatura': 22,
            'condiciones': 'Parcialmente nublado',
            'precipitacion': 0
        }
        
        datos_combustible = {
            'precio_gasolina': 1.15,
            'precio_diesel': 1.10,
            'gasolineras_cercanas': 5
        }
        
        print(f"  Tráfico: Nivel {datos_trafico['nivel_trafico']}/5 "
              f"(+{datos_trafico['tiempo_adicional']} min)")
        print(f"  Clima: {datos_clima['temperatura']}°C, {datos_clima['condiciones']}")
        print(f"  Combustible: Gasolina ${datos_combustible['precio_gasolina']}/L")
        
        # Ajustar cálculos basados en datos en tiempo real
        factor_ajuste_trafico = datos_trafico['factor_velocidad']
        factor_ajuste_clima = 1.0 if datos_clima['precipitacion'] == 0 else 1.2
        
        print(f"\nFACTORES DE AJUSTE:")
        print(f"  Factor tráfico: {factor_ajuste_trafico:.2f}")
        print(f"  Factor clima: {factor_ajuste_clima:.2f}")
        
        return {
            'trafico': datos_trafico,
            'clima': datos_clima,
            'combustible': datos_combustible,
            'factores_ajuste': {
                'trafico': factor_ajuste_trafico,
                'clima': factor_ajuste_clima
            }
        }

def ejecutar_todos_los_ejemplos():
    """Ejecuta todos los ejemplos prácticos"""
    
    print("=" * 80)
    print("SISTEMA DE OPTIMIZACIÓN DE RUTAS LOGÍSTICAS")
    print("Ejemplos Prácticos y Casos de Uso Comunes")
    print("=" * 80)
    
    ejemplos = EjemplosPracticos()
    
    try:
        # Ejecutar todos los ejemplos
        ejemplos.ejemplo_entrega_ultima_milla()
        ejemplos.ejemplo_distribucion_empresarial()
        ejemplos.ejemplo_analisis_costos()
        ejemplos.ejemplo_optimizacion_flota()
        ejemplos.ejemplo_integracion_apis()
        
        print("\n" + "=" * 80)
        print("✓ TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error ejecutando ejemplos: {e}")
        print("Verifique la configuración y dependencias del sistema.")

if __name__ == "__main__":
    ejecutar_todos_los_ejemplos()
