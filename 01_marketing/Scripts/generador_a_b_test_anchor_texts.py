#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de A/B Tests - Anchor Texts IA Marketing
=================================================

Este script genera variantes de anchor texts para pruebas A/B, incluyendo
métricas de seguimiento y análisis estadístico.

Funcionalidades:
- Generación de variantes para A/B testing
- Métricas de seguimiento automáticas
- Análisis estadístico de resultados
- Recomendaciones basadas en datos
- Reportes de rendimiento
"""

import random
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import statistics

class GeneradorABTestAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Variables para A/B testing
        self.variables_testing = {
            'longitud': {
                'corta': (10, 30),
                'media': (31, 60),
                'larga': (61, 100)
            },
            'tono': {
                'formal': ['Curso', 'Programa', 'Certificación', 'Masterclass'],
                'informal': ['Aprende', 'Descubre', 'Domina', 'Conquista'],
                'urgente': ['¡Última oportunidad!', 'Solo hoy', 'No te pierdas', 'Actúa ya'],
                'emocional': ['Transforma', 'Revoluciona', 'Cambia', 'Libera']
            },
            'cta': {
                'directa': ['Ver curso', 'Inscríbete', 'Comienza', 'Accede'],
                'indirecta': ['Descubre más', 'Conoce cómo', 'Explora', 'Aprende'],
                'urgente': ['¡Reserva ya!', '¡Solo hoy!', '¡Últimas plazas!', '¡No esperes!'],
                'emocional': ['Cambia tu vida', 'Realiza tu sueño', 'Alcanza el éxito', 'Libera tu potencial']
            },
            'beneficios': {
                'resultados': ['Resultados garantizados', 'Éxito asegurado', 'ROI comprobado', 'Efectividad probada'],
                'tiempo': ['En 30 días', 'Rápido y efectivo', 'Acelera tu crecimiento', 'Inmediato'],
                'facilidad': ['Fácil de implementar', 'Sin complicaciones', 'Paso a paso', 'Desde cero'],
                'exclusividad': ['Exclusivo', 'Limitado', 'VIP', 'Premium']
            },
            'social_proof': {
                'numeros': ['10,000+ estudiantes', '500+ empresas', '98% satisfacción', '5 estrellas'],
                'autoridad': ['Expertos certificados', 'Profesionales reconocidos', 'Líderes de la industria', 'Especialistas'],
                'testimonios': ['Casos de éxito', 'Testimonios reales', 'Historias de transformación', 'Resultados comprobados']
            }
        }
        
        # Métricas de seguimiento
        self.metricas_base = {
            'impresiones': 0,
            'clicks': 0,
            'conversiones': 0,
            'ctr': 0.0,
            'conversion_rate': 0.0,
            'costo_click': 0.0,
            'costo_conversion': 0.0,
            'roi': 0.0
        }

    def generar_variantes_ab_test(self, cantidad_variantes: int = 10) -> List[Dict[str, Any]]:
        """Genera variantes para A/B testing"""
        variantes = []
        
        for i in range(cantidad_variantes):
            # Seleccionar variables aleatorias
            longitud = random.choice(list(self.variables_testing['longitud'].keys()))
            tono = random.choice(list(self.variables_testing['tono'].keys()))
            cta = random.choice(list(self.variables_testing['cta'].keys()))
            beneficio = random.choice(list(self.variables_testing['beneficios'].keys()))
            social_proof = random.choice(list(self.variables_testing['social_proof'].keys()))
            
            # Generar anchor text
            anchor_text = self._generar_anchor_text_ab_test(
                longitud, tono, cta, beneficio, social_proof
            )
            
            # Generar métricas simuladas
            metricas = self._generar_metricas_simuladas()
            
            variante = {
                'id': f"variante_{i+1:03d}",
                'nombre': f"Variante {i+1} - {tono.title()} + {cta.title()}",
                'anchor_text': anchor_text,
                'variables': {
                    'longitud': longitud,
                    'tono': tono,
                    'cta': cta,
                    'beneficio': beneficio,
                    'social_proof': social_proof
                },
                'metricas': metricas,
                'fecha_creacion': datetime.now().isoformat(),
                'estado': 'activo'
            }
            
            variantes.append(variante)
        
        return variantes

    def _generar_anchor_text_ab_test(self, longitud: str, tono: str, cta: str, 
                                    beneficio: str, social_proof: str) -> str:
        """Genera un anchor text específico para A/B testing"""
        # Seleccionar palabra clave base
        palabra_clave = random.choice(self.palabras_clave_base)
        
        # Seleccionar elementos según las variables
        elemento_tono = random.choice(self.variables_testing['tono'][tono])
        elemento_cta = random.choice(self.variables_testing['cta'][cta])
        elemento_beneficio = random.choice(self.variables_testing['beneficios'][beneficio])
        elemento_social = random.choice(self.variables_testing['social_proof'][social_proof])
        
        # Generar diferentes estructuras según la longitud
        if longitud == 'corta':
            estructuras = [
                f"{elemento_tono} {palabra_clave}",
                f"{palabra_clave} - {elemento_cta}",
                f"{elemento_social} {palabra_clave}"
            ]
        elif longitud == 'media':
            estructuras = [
                f"{elemento_tono} {palabra_clave} - {elemento_beneficio}",
                f"{palabra_clave}: {elemento_beneficio} - {elemento_cta}",
                f"{elemento_social} {palabra_clave} - {elemento_cta}",
                f"{elemento_tono} {palabra_clave} {elemento_beneficio}"
            ]
        else:  # larga
            estructuras = [
                f"{elemento_tono} {palabra_clave} - {elemento_beneficio} - {elemento_cta}",
                f"{elemento_social} {palabra_clave}: {elemento_beneficio} - {elemento_cta}",
                f"{elemento_tono} {palabra_clave} {elemento_beneficio} - {elemento_social}",
                f"{palabra_clave} - {elemento_beneficio} - {elemento_social} - {elemento_cta}"
            ]
        
        # Seleccionar estructura aleatoria
        estructura = random.choice(estructuras)
        
        # Ajustar longitud si es necesario
        longitud_actual = len(estructura)
        longitud_objetivo = self.variables_testing['longitud'][longitud]
        
        if longitud_actual < longitud_objetivo[0]:
            # Agregar elementos para alcanzar longitud mínima
            elementos_extra = [
                "2024", "Online", "Certificado", "Profesional", "Avanzado",
                "Completo", "Actualizado", "Exclusivo", "Premium", "VIP"
            ]
            while longitud_actual < longitud_objetivo[0] and elementos_extra:
                elemento = random.choice(elementos_extra)
                elementos_extra.remove(elemento)
                estructura += f" {elemento}"
                longitud_actual = len(estructura)
        
        elif longitud_actual > longitud_objetivo[1]:
            # Acortar si excede longitud máxima
            palabras = estructura.split()
            while len(' '.join(palabras)) > longitud_objetivo[1] and len(palabras) > 2:
                palabras.pop()
            estructura = ' '.join(palabras)
        
        return estructura

    def _generar_metricas_simuladas(self) -> Dict[str, Any]:
        """Genera métricas simuladas para testing"""
        # Simular datos realistas
        impresiones = random.randint(1000, 10000)
        ctr_base = random.uniform(0.02, 0.08)  # 2-8% CTR
        clicks = int(impresiones * ctr_base)
        conversion_rate = random.uniform(0.05, 0.25)  # 5-25% conversión
        conversiones = int(clicks * conversion_rate)
        
        costo_click = random.uniform(0.50, 3.00)
        costo_conversion = costo_click / conversion_rate if conversion_rate > 0 else 0
        roi = random.uniform(1.5, 5.0)  # ROI 150-500%
        
        return {
            'impresiones': impresiones,
            'clicks': clicks,
            'conversiones': conversiones,
            'ctr': round(ctr_base * 100, 2),
            'conversion_rate': round(conversion_rate * 100, 2),
            'costo_click': round(costo_click, 2),
            'costo_conversion': round(costo_conversion, 2),
            'roi': round(roi, 2)
        }

    def ejecutar_ab_test(self, variantes: List[Dict[str, Any]], 
                        duracion_dias: int = 30) -> Dict[str, Any]:
        """Ejecuta un A/B test con las variantes proporcionadas"""
        fecha_inicio = datetime.now()
        fecha_fin = fecha_inicio + timedelta(days=duracion_dias)
        
        # Simular evolución de métricas durante el test
        resultados_test = {
            'test_id': f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'duracion_dias': duracion_dias,
            'variantes': [],
            'analisis_estadistico': {},
            'recomendaciones': []
        }
        
        for variante in variantes:
            # Simular evolución de métricas
            metricas_evolucion = self._simular_evolucion_metricas(
                variante['metricas'], duracion_dias
            )
            
            variante_resultado = {
                'id': variante['id'],
                'nombre': variante['nombre'],
                'anchor_text': variante['anchor_text'],
                'variables': variante['variables'],
                'metricas_iniciales': variante['metricas'],
                'metricas_finales': metricas_evolucion['finales'],
                'evolucion_diaria': metricas_evolucion['diaria'],
                'tendencia': metricas_evolucion['tendencia']
            }
            
            resultados_test['variantes'].append(variante_resultado)
        
        # Análisis estadístico
        resultados_test['analisis_estadistico'] = self._analizar_resultados_estadisticos(
            resultados_test['variantes']
        )
        
        # Generar recomendaciones
        resultados_test['recomendaciones'] = self._generar_recomendaciones_ab_test(
            resultados_test['variantes'], resultados_test['analisis_estadistico']
        )
        
        return resultados_test

    def _simular_evolucion_metricas(self, metricas_iniciales: Dict[str, Any], 
                                   duracion_dias: int) -> Dict[str, Any]:
        """Simula la evolución de métricas durante el test"""
        evolucion_diaria = []
        metricas_actuales = metricas_iniciales.copy()
        
        for dia in range(duracion_dias):
            # Simular variaciones diarias
            factor_crecimiento = random.uniform(0.95, 1.15)  # ±15% variación
            factor_conversion = random.uniform(0.90, 1.10)  # ±10% variación conversión
            
            # Actualizar métricas
            metricas_actuales['impresiones'] = int(metricas_actuales['impresiones'] * factor_crecimiento)
            metricas_actuales['clicks'] = int(metricas_actuales['clicks'] * factor_crecimiento)
            metricas_actuales['conversiones'] = int(metricas_actuales['conversiones'] * factor_conversion)
            
            # Recalcular ratios
            if metricas_actuales['impresiones'] > 0:
                metricas_actuales['ctr'] = round(
                    (metricas_actuales['clicks'] / metricas_actuales['impresiones']) * 100, 2
                )
            
            if metricas_actuales['clicks'] > 0:
                metricas_actuales['conversion_rate'] = round(
                    (metricas_actuales['conversiones'] / metricas_actuales['clicks']) * 100, 2
                )
            
            # Calcular tendencia
            if dia > 0:
                ctr_anterior = evolucion_diaria[-1]['ctr']
                tendencia_ctr = "creciente" if metricas_actuales['ctr'] > ctr_anterior else "decreciente"
            else:
                tendencia_ctr = "estable"
            
            evolucion_diaria.append({
                'dia': dia + 1,
                'impresiones': metricas_actuales['impresiones'],
                'clicks': metricas_actuales['clicks'],
                'conversiones': metricas_actuales['conversiones'],
                'ctr': metricas_actuales['ctr'],
                'conversion_rate': metricas_actuales['conversion_rate'],
                'tendencia_ctr': tendencia_ctr
            })
        
        # Calcular tendencia general
        ctrs = [dia['ctr'] for dia in evolucion_diaria]
        tendencia_general = self._calcular_tendencia(ctrs)
        
        return {
            'diaria': evolucion_diaria,
            'finales': metricas_actuales,
            'tendencia': tendencia_general
        }

    def _calcular_tendencia(self, valores: List[float]) -> str:
        """Calcula la tendencia general de una serie de valores"""
        if len(valores) < 2:
            return "insuficiente_datos"
        
        # Calcular pendiente usando regresión lineal simple
        n = len(valores)
        x = list(range(n))
        y = valores
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if pendiente > 0.1:
            return "creciente"
        elif pendiente < -0.1:
            return "decreciente"
        else:
            return "estable"

    def _analizar_resultados_estadisticos(self, variantes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realiza análisis estadístico de los resultados del A/B test"""
        # Recopilar métricas de todas las variantes
        ctrs = [v['metricas_finales']['ctr'] for v in variantes]
        conversion_rates = [v['metricas_finales']['conversion_rate'] for v in variantes]
        rois = [v['metricas_finales']['roi'] for v in variantes]
        
        # Estadísticas descriptivas
        analisis = {
            'ctr': {
                'promedio': round(statistics.mean(ctrs), 2),
                'mediana': round(statistics.median(ctrs), 2),
                'desviacion_estandar': round(statistics.stdev(ctrs) if len(ctrs) > 1 else 0, 2),
                'minimo': round(min(ctrs), 2),
                'maximo': round(max(ctrs), 2)
            },
            'conversion_rate': {
                'promedio': round(statistics.mean(conversion_rates), 2),
                'mediana': round(statistics.median(conversion_rates), 2),
                'desviacion_estandar': round(statistics.stdev(conversion_rates) if len(conversion_rates) > 1 else 0, 2),
                'minimo': round(min(conversion_rates), 2),
                'maximo': round(max(conversion_rates), 2)
            },
            'roi': {
                'promedio': round(statistics.mean(rois), 2),
                'mediana': round(statistics.median(rois), 2),
                'desviacion_estandar': round(statistics.stdev(rois) if len(rois) > 1 else 0, 2),
                'minimo': round(min(rois), 2),
                'maximo': round(max(rois), 2)
            }
        }
        
        # Identificar variante ganadora
        mejor_ctr = max(variantes, key=lambda v: v['metricas_finales']['ctr'])
        mejor_conversion = max(variantes, key=lambda v: v['metricas_finales']['conversion_rate'])
        mejor_roi = max(variantes, key=lambda v: v['metricas_finales']['roi'])
        
        analisis['ganadores'] = {
            'mejor_ctr': {
                'id': mejor_ctr['id'],
                'nombre': mejor_ctr['nombre'],
                'ctr': mejor_ctr['metricas_finales']['ctr']
            },
            'mejor_conversion': {
                'id': mejor_conversion['id'],
                'nombre': mejor_conversion['nombre'],
                'conversion_rate': mejor_conversion['metricas_finales']['conversion_rate']
            },
            'mejor_roi': {
                'id': mejor_roi['id'],
                'nombre': mejor_roi['nombre'],
                'roi': mejor_roi['metricas_finales']['roi']
            }
        }
        
        # Calcular significancia estadística (simplificado)
        analisis['significancia'] = self._calcular_significancia_estadistica(variantes)
        
        return analisis

    def _calcular_significancia_estadistica(self, variantes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula la significancia estadística entre variantes (simplificado)"""
        # En un caso real, aquí se implementaría una prueba t o chi-cuadrado
        # Por simplicidad, simulamos resultados
        
        mejor_variante = max(variantes, key=lambda v: v['metricas_finales']['ctr'])
        peor_variante = min(variantes, key=lambda v: v['metricas_finales']['ctr'])
        
        diferencia_ctr = mejor_variante['metricas_finales']['ctr'] - peor_variante['metricas_finales']['ctr']
        
        # Simular p-value basado en la diferencia
        if diferencia_ctr > 2.0:
            p_value = random.uniform(0.01, 0.05)  # Significativo
            significativo = True
        elif diferencia_ctr > 1.0:
            p_value = random.uniform(0.05, 0.10)  # Marginalmente significativo
            significativo = False
        else:
            p_value = random.uniform(0.10, 0.50)  # No significativo
            significativo = False
        
        return {
            'diferencia_ctr': round(diferencia_ctr, 2),
            'p_value': round(p_value, 3),
            'significativo': significativo,
            'nivel_confianza': 95 if significativo else 90
        }

    def _generar_recomendaciones_ab_test(self, variantes: List[Dict[str, Any]], 
                                       analisis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en los resultados del A/B test"""
        recomendaciones = []
        
        # Recomendación basada en CTR
        mejor_ctr = analisis['ganadores']['mejor_ctr']
        recomendaciones.append({
            'categoria': 'CTR',
            'prioridad': 'Alta',
            'recomendacion': f"Usar la variante '{mejor_ctr['nombre']}' para maximizar CTR",
            'justificacion': f"CTR de {mejor_ctr['ctr']}% vs promedio de {analisis['ctr']['promedio']}%"
        })
        
        # Recomendación basada en conversión
        mejor_conversion = analisis['ganadores']['mejor_conversion']
        recomendaciones.append({
            'categoria': 'Conversión',
            'prioridad': 'Alta',
            'recomendacion': f"Implementar la variante '{mejor_conversion['nombre']}' para maximizar conversiones",
            'justificacion': f"Tasa de conversión de {mejor_conversion['conversion_rate']}% vs promedio de {analisis['conversion_rate']['promedio']}%"
        })
        
        # Recomendación basada en ROI
        mejor_roi = analisis['ganadores']['mejor_roi']
        recomendaciones.append({
            'categoria': 'ROI',
            'prioridad': 'Muy Alta',
            'recomendacion': f"Priorizar la variante '{mejor_roi['nombre']}' para mejor retorno de inversión",
            'justificacion': f"ROI de {mejor_roi['roi']}x vs promedio de {analisis['roi']['promedio']}x"
        })
        
        # Recomendación sobre significancia estadística
        if analisis['significancia']['significativo']:
            recomendaciones.append({
                'categoria': 'Significancia',
                'prioridad': 'Media',
                'recomendacion': 'Los resultados son estadísticamente significativos',
                'justificacion': f"P-value de {analisis['significancia']['p_value']} < 0.05"
            })
        else:
            recomendaciones.append({
                'categoria': 'Significancia',
                'prioridad': 'Media',
                'recomendacion': 'Extender el test para obtener significancia estadística',
                'justificacion': f"P-value de {analisis['significancia']['p_value']} > 0.05"
            })
        
        # Recomendaciones sobre variables específicas
        variables_ganadoras = self._analizar_variables_ganadoras(variantes, analisis)
        for variable, info in variables_ganadoras.items():
            recomendaciones.append({
                'categoria': f'Variable: {variable}',
                'prioridad': 'Media',
                'recomendacion': f"Usar {info['valor']} en futuros anchor texts",
                'justificacion': f"Presente en {info['frecuencia']} de las mejores variantes"
            })
        
        return recomendaciones

    def _analizar_variables_ganadoras(self, variantes: List[Dict[str, Any]], 
                                    analisis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Analiza qué variables aparecen más en las mejores variantes"""
        # Ordenar variantes por CTR
        variantes_ordenadas = sorted(variantes, key=lambda v: v['metricas_finales']['ctr'], reverse=True)
        
        # Tomar las top 3 variantes
        top_variantes = variantes_ordenadas[:3]
        
        # Contar variables
        conteo_variables = {}
        for variante in top_variantes:
            for variable, valor in variante['variables'].items():
                if variable not in conteo_variables:
                    conteo_variables[variable] = {}
                if valor not in conteo_variables[variable]:
                    conteo_variables[variable][valor] = 0
                conteo_variables[variable][valor] += 1
        
        # Encontrar la variable más frecuente en cada categoría
        variables_ganadoras = {}
        for variable, valores in conteo_variables.items():
            valor_mas_frecuente = max(valores.items(), key=lambda x: x[1])
            variables_ganadoras[variable] = {
                'valor': valor_mas_frecuente[0],
                'frecuencia': valor_mas_frecuente[1]
            }
        
        return variables_ganadoras

    def exportar_resultados_ab_test(self, resultados: Dict[str, Any], formato: str = "json") -> str:
        """Exporta los resultados del A/B test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"ab_test_anchor_texts_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- RESULTADOS A/B TEST - ANCHOR TEXTS IA MARKETING ---\n")
                f.write(f"Test ID: {resultados['test_id']}\n")
                f.write(f"Período: {resultados['fecha_inicio']} - {resultados['fecha_fin']}\n")
                f.write(f"Duración: {resultados['duracion_dias']} días\n\n")
                
                f.write("RESUMEN EJECUTIVO:\n")
                analisis = resultados['analisis_estadistico']
                f.write(f"• CTR promedio: {analisis['ctr']['promedio']}%\n")
                f.write(f"• Tasa de conversión promedio: {analisis['conversion_rate']['promedio']}%\n")
                f.write(f"• ROI promedio: {analisis['roi']['promedio']}x\n\n")
                
                f.write("GANADORES:\n")
                f.write(f"• Mejor CTR: {analisis['ganadores']['mejor_ctr']['nombre']} ({analisis['ganadores']['mejor_ctr']['ctr']}%)\n")
                f.write(f"• Mejor Conversión: {analisis['ganadores']['mejor_conversion']['nombre']} ({analisis['ganadores']['mejor_conversion']['conversion_rate']}%)\n")
                f.write(f"• Mejor ROI: {analisis['ganadores']['mejor_roi']['nombre']} ({analisis['ganadores']['mejor_roi']['roi']}x)\n\n")
                
                f.write("RECOMENDACIONES:\n")
                for rec in resultados['recomendaciones']:
                    f.write(f"• {rec['categoria']} ({rec['prioridad']}): {rec['recomendacion']}\n")
                    f.write(f"  Justificación: {rec['justificacion']}\n")
                f.write("\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

def main():
    generador = GeneradorABTestAnchorTexts()
    
    print("🧪 GENERADOR DE A/B TESTS - ANCHOR TEXTS IA MARKETING")
    print("====================================================\n")
    
    print("🔄 Generando variantes para A/B testing...")
    variantes = generador.generar_variantes_ab_test(cantidad_variantes=15)
    
    print("🔄 Ejecutando A/B test simulado...")
    resultados = generador.ejecutar_ab_test(variantes, duracion_dias=30)
    
    print("💾 Exportando resultados...")
    json_file = generador.exportar_resultados_ab_test(resultados, "json")
    txt_file = generador.exportar_resultados_ab_test(resultados, "txt")
    
    print("\n✅ A/B Test completado:")
    print(f"   • Variantes generadas: {len(variantes)}")
    print(f"   • Duración del test: {resultados['duracion_dias']} días")
    print(f"   • Mejor CTR: {resultados['analisis_estadistico']['ganadores']['mejor_ctr']['ctr']}%")
    print(f"   • Mejor conversión: {resultados['analisis_estadistico']['ganadores']['mejor_conversion']['conversion_rate']}%")
    print(f"   • Mejor ROI: {resultados['analisis_estadistico']['ganadores']['mejor_roi']['roi']}x")
    print(f"   • Significancia estadística: {'Sí' if resultados['analisis_estadistico']['significancia']['significativo'] else 'No'}")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa los resultados del A/B test")
    print("2. Implementa las variantes ganadoras")
    print("3. Monitorea el rendimiento a largo plazo")
    print("4. Planifica nuevos tests con insights obtenidos")
    print("5. Documenta las lecciones aprendidas")

if __name__ == "__main__":
    main()




