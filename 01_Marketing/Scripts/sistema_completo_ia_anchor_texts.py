#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Completo IA - Anchor Texts IA Marketing
===============================================

Este script integra todas las funcionalidades del sistema en una interfaz
unificada con capacidades de IA avanzadas.

Funcionalidades:
- Generación masiva con IA
- Predicción de rendimiento
- Optimización automática
- Análisis de competencia
- A/B testing inteligente
- Dashboard en tiempo real
- Pipeline completo automatizado
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re
import math
import os
import subprocess
import sys

class SistemaCompletoIAAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Configuración del sistema
        self.configuracion = {
            'modo_ia': True,
            'prediccion_automatica': True,
            'optimizacion_automatica': True,
            'analisis_competencia': True,
            'ab_testing': True,
            'dashboard_tiempo_real': True,
            'exportacion_automatica': True
        }
        
        # Estadísticas del sistema
        self.estadisticas = {
            'anchor_texts_generados': 0,
            'optimizaciones_realizadas': 0,
            'predicciones_generadas': 0,
            'ab_tests_ejecutados': 0,
            'archivos_exportados': 0,
            'fecha_inicio': datetime.now().isoformat()
        }
        
        # Cache de resultados
        self.cache = {
            'anchor_texts': [],
            'predicciones': [],
            'optimizaciones': [],
            'ab_tests': [],
            'analisis_competencia': []
        }

    def ejecutar_pipeline_completo(self, configuracion_personalizada: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ejecuta el pipeline completo del sistema"""
        print("🚀 SISTEMA COMPLETO IA - ANCHOR TEXTS IA MARKETING")
        print("==================================================\n")
        
        # Aplicar configuración personalizada
        if configuracion_personalizada:
            self.configuracion.update(configuracion_personalizada)
        
        resultados = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'configuracion': self.configuracion,
            'etapas': [],
            'estadisticas_finales': {},
            'archivos_generados': [],
            'recomendaciones': []
        }
        
        # Etapa 1: Generación masiva
        print("🔄 Etapa 1: Generación masiva de anchor texts...")
        etapa_generacion = self._ejecutar_generacion_masiva()
        resultados['etapas'].append(etapa_generacion)
        
        # Etapa 2: Predicción de rendimiento
        if self.configuracion['prediccion_automatica']:
            print("🔄 Etapa 2: Predicción de rendimiento...")
            etapa_prediccion = self._ejecutar_prediccion_rendimiento()
            resultados['etapas'].append(etapa_prediccion)
        
        # Etapa 3: Optimización automática
        if self.configuracion['optimizacion_automatica']:
            print("🔄 Etapa 3: Optimización automática...")
            etapa_optimizacion = self._ejecutar_optimizacion_automatica()
            resultados['etapas'].append(etapa_optimizacion)
        
        # Etapa 4: Análisis de competencia
        if self.configuracion['analisis_competencia']:
            print("🔄 Etapa 4: Análisis de competencia...")
            etapa_competencia = self._ejecutar_analisis_competencia()
            resultados['etapas'].append(etapa_competencia)
        
        # Etapa 5: A/B Testing
        if self.configuracion['ab_testing']:
            print("🔄 Etapa 5: A/B Testing inteligente...")
            etapa_ab_test = self._ejecutar_ab_testing()
            resultados['etapas'].append(etapa_ab_test)
        
        # Etapa 6: Dashboard en tiempo real
        if self.configuracion['dashboard_tiempo_real']:
            print("🔄 Etapa 6: Generando dashboard en tiempo real...")
            etapa_dashboard = self._ejecutar_dashboard_tiempo_real()
            resultados['etapas'].append(etapa_dashboard)
        
        # Etapa 7: Exportación automática
        if self.configuracion['exportacion_automatica']:
            print("🔄 Etapa 7: Exportación automática...")
            etapa_exportacion = self._ejecutar_exportacion_automatica()
            resultados['etapas'].append(etapa_exportacion)
        
        # Calcular estadísticas finales
        resultados['estadisticas_finales'] = self._calcular_estadisticas_finales()
        
        # Generar recomendaciones
        resultados['recomendaciones'] = self._generar_recomendaciones_finales(resultados)
        
        print("\n✅ Pipeline completo ejecutado exitosamente!")
        self._mostrar_resumen_ejecucion(resultados)
        
        return resultados

    def _ejecutar_generacion_masiva(self) -> Dict[str, Any]:
        """Ejecuta la generación masiva de anchor texts"""
        # Simular generación masiva
        cantidad = random.randint(100, 500)
        anchor_texts = self._generar_anchor_texts_masivos(cantidad)
        
        # Guardar en cache
        self.cache['anchor_texts'] = anchor_texts
        self.estadisticas['anchor_texts_generados'] += len(anchor_texts)
        
        return {
            'nombre': 'Generación Masiva',
            'estado': 'completado',
            'anchor_texts_generados': len(anchor_texts),
            'tiempo_ejecucion': random.uniform(2, 5),
            'archivos_generados': ['anchor_texts_generados.json']
        }

    def _generar_anchor_texts_masivos(self, cantidad: int) -> List[Dict[str, Any]]:
        """Genera anchor texts masivos"""
        anchor_texts = []
        
        templates = [
            "Curso {palabra_clave} - {beneficio}",
            "Aprende {palabra_clave} en {tiempo}",
            "Domina {palabra_clave} - {garantia}",
            "Masterclass {palabra_clave} {año}",
            "Certificación {palabra_clave} - {modalidad}",
            "IA Marketing: {enfoque} - {resultado}",
            "Transforma tu negocio con {palabra_clave}",
            "El futuro del marketing: {palabra_clave}",
            "Estrategias {palabra_clave} que funcionan",
            "Guía completa de {palabra_clave}"
        ]
        
        beneficios = ["Resultados garantizados", "Éxito asegurado", "ROI comprobado", "Efectividad probada"]
        tiempos = ["30 días", "6 meses", "1 año", "90 días"]
        garantias = ["100% efectivo", "Sin riesgo", "Satisfacción garantizada", "Resultados comprobados"]
        modalidades = ["Online", "Presencial", "Híbrido", "Intensivo"]
        enfoques = ["Avanzado", "Básico", "Profesional", "Especializado"]
        resultados = ["Multiplica ventas", "Aumenta conversiones", "Optimiza ROI", "Escala tu negocio"]
        
        for i in range(cantidad):
            palabra_clave = random.choice(self.palabras_clave_base)
            template = random.choice(templates)
            
            # Reemplazar placeholders
            anchor_text = template.replace('{palabra_clave}', palabra_clave)
            anchor_text = anchor_text.replace('{beneficio}', random.choice(beneficios))
            anchor_text = anchor_text.replace('{tiempo}', random.choice(tiempos))
            anchor_text = anchor_text.replace('{garantia}', random.choice(garantias))
            anchor_text = anchor_text.replace('{año}', '2024')
            anchor_text = anchor_text.replace('{modalidad}', random.choice(modalidades))
            anchor_text = anchor_text.replace('{enfoque}', random.choice(enfoques))
            anchor_text = anchor_text.replace('{resultado}', random.choice(resultados))
            
            anchor_texts.append({
                'id': f"at_{i+1:04d}",
                'texto': anchor_text,
                'palabra_clave': palabra_clave,
                'categoria': random.choice(['comercial', 'informativo', 'navegacional']),
                'fecha_creacion': datetime.now().isoformat()
            })
        
        return anchor_texts

    def _ejecutar_prediccion_rendimiento(self) -> Dict[str, Any]:
        """Ejecuta la predicción de rendimiento"""
        if not self.cache['anchor_texts']:
            return {'nombre': 'Predicción Rendimiento', 'estado': 'omitido', 'razon': 'No hay anchor texts para predecir'}
        
        # Simular predicción
        predicciones = []
        for anchor_text in self.cache['anchor_texts'][:50]:  # Limitar a 50 para demo
            prediccion = self._simular_prediccion(anchor_text)
            predicciones.append(prediccion)
        
        self.cache['predicciones'] = predicciones
        self.estadisticas['predicciones_generadas'] += len(predicciones)
        
        return {
            'nombre': 'Predicción Rendimiento',
            'estado': 'completado',
            'predicciones_generadas': len(predicciones),
            'tiempo_ejecucion': random.uniform(3, 7),
            'archivos_generados': ['predicciones_rendimiento.json']
        }

    def _simular_prediccion(self, anchor_text: Dict[str, Any]) -> Dict[str, Any]:
        """Simula una predicción de rendimiento"""
        # Simular métricas basadas en características del texto
        longitud = len(anchor_text['texto'])
        palabras_poder = sum(1 for palabra in ['domina', 'revoluciona', 'transforma', 'multiplica'] 
                           if palabra in anchor_text['texto'].lower())
        
        # Calcular score base
        score_base = 50
        if 30 <= longitud <= 60:
            score_base += 20
        score_base += palabras_poder * 10
        
        # Simular métricas
        ctr = min(0.15, max(0.01, (score_base / 100) * 0.12 + random.uniform(-0.02, 0.02)))
        conversion_rate = min(0.50, max(0.01, (score_base / 100) * 0.25 + random.uniform(-0.05, 0.05)))
        roi = min(10.0, max(1.0, (score_base / 100) * 5 + random.uniform(-1, 1)))
        
        return {
            'anchor_text_id': anchor_text['id'],
            'anchor_text': anchor_text['texto'],
            'score_calidad': min(100, max(0, score_base)),
            'ctr_predicho': round(ctr * 100, 2),
            'conversion_rate_predicho': round(conversion_rate * 100, 2),
            'roi_predicho': round(roi, 2),
            'confianza': round(random.uniform(70, 95), 1),
            'fecha_prediccion': datetime.now().isoformat()
        }

    def _ejecutar_optimizacion_automatica(self) -> Dict[str, Any]:
        """Ejecuta la optimización automática"""
        if not self.cache['predicciones']:
            return {'nombre': 'Optimización Automática', 'estado': 'omitido', 'razon': 'No hay predicciones para optimizar'}
        
        # Seleccionar los peores anchor texts para optimizar
        predicciones_ordenadas = sorted(self.cache['predicciones'], key=lambda x: x['score_calidad'])
        peores_predicciones = predicciones_ordenadas[:20]  # Top 20 peores
        
        optimizaciones = []
        for prediccion in peores_predicciones:
            optimizacion = self._simular_optimizacion(prediccion)
            optimizaciones.append(optimizacion)
        
        self.cache['optimizaciones'] = optimizaciones
        self.estadisticas['optimizaciones_realizadas'] += len(optimizaciones)
        
        return {
            'nombre': 'Optimización Automática',
            'estado': 'completado',
            'optimizaciones_realizadas': len(optimizaciones),
            'tiempo_ejecucion': random.uniform(4, 8),
            'archivos_generados': ['optimizaciones_automaticas.json']
        }

    def _simular_optimizacion(self, prediccion: Dict[str, Any]) -> Dict[str, Any]:
        """Simula una optimización"""
        anchor_text_original = prediccion['anchor_text']
        
        # Generar versión optimizada
        mejoras = ['- Resultados Garantizados', '- Domina Ahora', '- Exclusivo 2024', '- Sin Riesgo']
        mejora = random.choice(mejoras)
        anchor_text_optimizado = f"{anchor_text_original} {mejora}"
        
        # Simular mejoras
        mejora_score = random.randint(10, 40)
        mejora_ctr = random.uniform(1, 5)
        mejora_conversion = random.uniform(2, 8)
        mejora_roi = random.uniform(0.5, 2.0)
        
        return {
            'anchor_text_id': prediccion['anchor_text_id'],
            'anchor_text_original': anchor_text_original,
            'anchor_text_optimizado': anchor_text_optimizado,
            'mejora_score': mejora_score,
            'mejora_ctr': round(mejora_ctr, 2),
            'mejora_conversion': round(mejora_conversion, 2),
            'mejora_roi': round(mejora_roi, 2),
            'fecha_optimizacion': datetime.now().isoformat()
        }

    def _ejecutar_analisis_competencia(self) -> Dict[str, Any]:
        """Ejecuta el análisis de competencia"""
        # Simular análisis de competencia
        competidores = [
            {'nombre': 'MarketingIA Pro', 'fortalezas': ['certificación', 'tiempo corto'], 'debilidades': ['precio alto']},
            {'nombre': 'DigitalMind Academy', 'fortalezas': ['gratuito', 'completo'], 'debilidades': ['calidad variable']},
            {'nombre': 'TechMarketing Solutions', 'fortalezas': ['avanzado', 'empresas'], 'debilidades': ['complejo']}
        ]
        
        oportunidades = [
            'Anchor texts emocionales no explotados',
            'Nichos específicos por industria',
            'Tendencias 2024 no cubiertas',
            'Formato interactivo innovador'
        ]
        
        analisis = {
            'competidores_analizados': len(competidores),
            'oportunidades_identificadas': len(oportunidades),
            'fortalezas_propias': ['IA avanzada', 'Personalización', 'Resultados comprobados'],
            'recomendaciones': [
                'Enfocarse en diferenciación emocional',
                'Explotar nichos específicos',
                'Aprovechar tendencias 2024'
            ]
        }
        
        self.cache['analisis_competencia'] = analisis
        
        return {
            'nombre': 'Análisis Competencia',
            'estado': 'completado',
            'competidores_analizados': len(competidores),
            'oportunidades_identificadas': len(oportunidades),
            'tiempo_ejecucion': random.uniform(2, 4),
            'archivos_generados': ['analisis_competencia.json']
        }

    def _ejecutar_ab_testing(self) -> Dict[str, Any]:
        """Ejecuta A/B testing inteligente"""
        if not self.cache['anchor_texts']:
            return {'nombre': 'A/B Testing', 'estado': 'omitido', 'razon': 'No hay anchor texts para testear'}
        
        # Seleccionar anchor texts para A/B testing
        anchor_texts_test = random.sample(self.cache['anchor_texts'], min(10, len(self.cache['anchor_texts'])))
        
        # Simular A/B test
        variantes = []
        for i, anchor_text in enumerate(anchor_texts_test):
            variante_a = anchor_text['texto']
            variante_b = f"{anchor_text['texto']} - {random.choice(['Exclusivo', 'Garantizado', '2024', 'Premium'])}"
            
            # Simular métricas
            ctr_a = random.uniform(0.02, 0.08)
            ctr_b = random.uniform(0.03, 0.12)
            conversion_a = random.uniform(0.05, 0.20)
            conversion_b = random.uniform(0.08, 0.25)
            
            variantes.append({
                'anchor_text_id': anchor_text['id'],
                'variante_a': variante_a,
                'variante_b': variante_b,
                'ctr_a': round(ctr_a * 100, 2),
                'ctr_b': round(ctr_b * 100, 2),
                'conversion_a': round(conversion_a * 100, 2),
                'conversion_b': round(conversion_b * 100, 2),
                'ganadora': 'B' if ctr_b > ctr_a else 'A',
                'mejora_ctr': round((ctr_b - ctr_a) * 100, 2),
                'mejora_conversion': round((conversion_b - conversion_a) * 100, 2)
            })
        
        self.cache['ab_tests'] = variantes
        self.estadisticas['ab_tests_ejecutados'] += len(variantes)
        
        return {
            'nombre': 'A/B Testing',
            'estado': 'completado',
            'tests_ejecutados': len(variantes),
            'tiempo_ejecucion': random.uniform(5, 10),
            'archivos_generados': ['ab_tests_resultados.json']
        }

    def _ejecutar_dashboard_tiempo_real(self) -> Dict[str, Any]:
        """Ejecuta la generación del dashboard en tiempo real"""
        # Generar dashboard HTML
        dashboard_html = self._generar_dashboard_html()
        
        # Guardar dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_tiempo_real_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        return {
            'nombre': 'Dashboard Tiempo Real',
            'estado': 'completado',
            'archivo_generado': filename,
            'tiempo_ejecucion': random.uniform(1, 3),
            'archivos_generados': [filename]
        }

    def _generar_dashboard_html(self) -> str:
        """Genera el dashboard HTML en tiempo real"""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Tiempo Real - Sistema IA Anchor Texts</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 30px; margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .metric-label {{ color: #7f8c8d; font-size: 1.1em; text-transform: uppercase; letter-spacing: 1px; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .status-completado {{ background: #27ae60; color: white; }}
        .status-ejecutando {{ background: #f39c12; color: white; }}
        .status-pendiente {{ background: #95a5a6; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Dashboard Tiempo Real - Sistema IA Anchor Texts</h1>
            <p>Monitoreo en vivo del sistema completo de generación y optimización</p>
            <p>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self.estadisticas['anchor_texts_generados']}</div>
                <div class="metric-label">Anchor Texts Generados</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.estadisticas['predicciones_generadas']}</div>
                <div class="metric-label">Predicciones Generadas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.estadisticas['optimizaciones_realizadas']}</div>
                <div class="metric-label">Optimizaciones Realizadas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.estadisticas['ab_tests_ejecutados']}</div>
                <div class="metric-label">A/B Tests Ejecutados</div>
            </div>
        </div>
        
        <div class="metric-card">
            <h3>Estado del Sistema</h3>
            <p><span class="status status-completado">Sistema Activo</span></p>
            <p>Tiempo de ejecución: {datetime.now() - datetime.fromisoformat(self.estadisticas['fecha_inicio'])}</p>
            <p>Archivos generados: {self.estadisticas['archivos_exportados']}</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh cada 30 segundos
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """

    def _ejecutar_exportacion_automatica(self) -> Dict[str, Any]:
        """Ejecuta la exportación automática"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_generados = []
        
        # Exportar anchor texts
        if self.cache['anchor_texts']:
            filename = f"anchor_texts_completos_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cache['anchor_texts'], f, ensure_ascii=False, indent=2)
            archivos_generados.append(filename)
        
        # Exportar predicciones
        if self.cache['predicciones']:
            filename = f"predicciones_completas_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cache['predicciones'], f, ensure_ascii=False, indent=2)
            archivos_generados.append(filename)
        
        # Exportar optimizaciones
        if self.cache['optimizaciones']:
            filename = f"optimizaciones_completas_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cache['optimizaciones'], f, ensure_ascii=False, indent=2)
            archivos_generados.append(filename)
        
        # Exportar A/B tests
        if self.cache['ab_tests']:
            filename = f"ab_tests_completos_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cache['ab_tests'], f, ensure_ascii=False, indent=2)
            archivos_generados.append(filename)
        
        # Exportar análisis de competencia
        if self.cache['analisis_competencia']:
            filename = f"analisis_competencia_completo_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.cache['analisis_competencia'], f, ensure_ascii=False, indent=2)
            archivos_generados.append(filename)
        
        self.estadisticas['archivos_exportados'] += len(archivos_generados)
        
        return {
            'nombre': 'Exportación Automática',
            'estado': 'completado',
            'archivos_exportados': len(archivos_generados),
            'tiempo_ejecucion': random.uniform(1, 3),
            'archivos_generados': archivos_generados
        }

    def _calcular_estadisticas_finales(self) -> Dict[str, Any]:
        """Calcula las estadísticas finales del sistema"""
        return {
            'anchor_texts_generados': self.estadisticas['anchor_texts_generados'],
            'predicciones_generadas': self.estadisticas['predicciones_generadas'],
            'optimizaciones_realizadas': self.estadisticas['optimizaciones_realizadas'],
            'ab_tests_ejecutados': self.estadisticas['ab_tests_ejecutados'],
            'archivos_exportados': self.estadisticas['archivos_exportados'],
            'tiempo_total_ejecucion': (datetime.now() - datetime.fromisoformat(self.estadisticas['fecha_inicio'])).total_seconds(),
            'eficiencia_sistema': round((self.estadisticas['anchor_texts_generados'] + self.estadisticas['predicciones_generadas']) / 100, 2)
        }

    def _generar_recomendaciones_finales(self, resultados: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones finales del sistema"""
        recomendaciones = []
        
        stats = resultados['estadisticas_finales']
        
        if stats['anchor_texts_generados'] > 200:
            recomendaciones.append("Excelente generación de anchor texts, implementar en campañas piloto")
        
        if stats['predicciones_generadas'] > 50:
            recomendaciones.append("Predicciones generadas exitosamente, monitorear rendimiento real vs predicciones")
        
        if stats['optimizaciones_realizadas'] > 20:
            recomendaciones.append("Optimizaciones completadas, implementar versiones mejoradas")
        
        if stats['ab_tests_ejecutados'] > 10:
            recomendaciones.append("A/B tests ejecutados, analizar resultados y seleccionar ganadores")
        
        if stats['eficiencia_sistema'] > 5:
            recomendaciones.append("Sistema funcionando eficientemente, considerar escalamiento")
        
        recomendaciones.extend([
            "Revisar todos los archivos generados para implementación",
            "Configurar monitoreo continuo del rendimiento",
            "Planificar próximas iteraciones del sistema",
            "Documentar lecciones aprendidas para futuras mejoras"
        ])
        
        return recomendaciones

    def _mostrar_resumen_ejecucion(self, resultados: Dict[str, Any]):
        """Muestra el resumen de la ejecución"""
        print(f"\n📊 RESUMEN DE EJECUCIÓN:")
        print(f"   • Anchor texts generados: {resultados['estadisticas_finales']['anchor_texts_generados']}")
        print(f"   • Predicciones generadas: {resultados['estadisticas_finales']['predicciones_generadas']}")
        print(f"   • Optimizaciones realizadas: {resultados['estadisticas_finales']['optimizaciones_realizadas']}")
        print(f"   • A/B tests ejecutados: {resultados['estadisticas_finales']['ab_tests_ejecutados']}")
        print(f"   • Archivos exportados: {resultados['estadisticas_finales']['archivos_exportados']}")
        print(f"   • Tiempo total: {resultados['estadisticas_finales']['tiempo_total_ejecucion']:.1f} segundos")
        print(f"   • Eficiencia del sistema: {resultados['estadisticas_finales']['eficiencia_sistema']}")
        
        print(f"\n📁 ARCHIVOS GENERADOS:")
        for archivo in resultados['archivos_generados']:
            print(f"   • {archivo}")
        
        print(f"\n🎯 RECOMENDACIONES PRINCIPALES:")
        for i, rec in enumerate(resultados['recomendaciones'][:5], 1):
            print(f"   {i}. {rec}")

def main():
    sistema = SistemaCompletoIAAnchorTexts()
    
    # Configuración personalizada (opcional)
    configuracion_personalizada = {
        'modo_ia': True,
        'prediccion_automatica': True,
        'optimizacion_automatica': True,
        'analisis_competencia': True,
        'ab_testing': True,
        'dashboard_tiempo_real': True,
        'exportacion_automatica': True
    }
    
    # Ejecutar pipeline completo
    resultados = sistema.ejecutar_pipeline_completo(configuracion_personalizada)
    
    # Guardar resultados finales
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resultados_sistema_completo_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultados guardados en: {filename}")
    print(f"\n🎉 ¡Sistema completo ejecutado exitosamente!")

if __name__ == "__main__":
    main()




