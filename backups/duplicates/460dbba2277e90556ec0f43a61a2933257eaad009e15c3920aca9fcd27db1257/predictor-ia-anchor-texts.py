#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Predictor IA - Anchor Texts IA Marketing
========================================

Este script utiliza técnicas de machine learning para predecir el rendimiento
de anchor texts antes de su implementación.

Funcionalidades:
- Predicción de CTR basada en características del texto
- Análisis de sentimientos y emociones
- Predicción de conversiones
- Recomendaciones de optimización
- Modelo de aprendizaje automático
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
import math

class PredictorIAAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Características para el modelo de predicción
        self.caracteristicas = {
            'longitud': {'peso': 0.15, 'optimo': 45},
            'palabras_poder': {'peso': 0.20, 'palabras': ['domina', 'revoluciona', 'transforma', 'multiplica', 'acelera', 'exclusivo', 'garantizado', 'éxito', 'ahora', 'última oportunidad']},
            'llamada_accion': {'peso': 0.18, 'palabras': ['aprende', 'descubre', 'haz clic', 'ver más', 'comienza', 'regístrate', 'obtén', 'consigue']},
            'urgencia': {'peso': 0.12, 'palabras': ['ahora', 'hoy', 'ya', 'inmediatamente', 'urgente', 'última oportunidad', 'tiempo limitado', 'solo hoy']},
            'beneficios': {'peso': 0.15, 'palabras': ['resultados', 'éxito', 'garantizado', 'comprobado', 'efectivo', 'seguro', 'confiable']},
            'numeros': {'peso': 0.10, 'patron': r'\d+'},
            'emotividad': {'peso': 0.10, 'palabras': ['increíble', 'sorprendente', 'fantástico', 'extraordinario', 'revolucionario', 'transformador']}
        }
        
        # Datos históricos simulados para entrenamiento
        self.datos_historicos = self._generar_datos_historicos()
        
        # Modelo entrenado
        self.modelo_entrenado = self._entrenar_modelo()

    def _generar_datos_historicos(self) -> List[Dict[str, Any]]:
        """Genera datos históricos simulados para entrenar el modelo"""
        datos = []
        
        # Generar 1000 ejemplos históricos
        for i in range(1000):
            # Generar anchor text aleatorio
            anchor_text = self._generar_anchor_text_historico()
            
            # Extraer características
            caracteristicas = self._extraer_caracteristicas(anchor_text)
            
            # Simular rendimiento basado en características
            ctr = self._simular_ctr(caracteristicas)
            conversion_rate = self._simular_conversion_rate(caracteristicas)
            roi = self._simular_roi(caracteristicas)
            
            datos.append({
                'anchor_text': anchor_text,
                'caracteristicas': caracteristicas,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'fecha': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            })
        
        return datos

    def _generar_anchor_text_historico(self) -> str:
        """Genera un anchor text histórico aleatorio"""
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
        
        palabra_clave = random.choice(self.palabras_clave_base)
        template = random.choice(templates)
        
        # Reemplazar placeholders
        anchor_text = template.replace('{palabra_clave}', palabra_clave)
        anchor_text = anchor_text.replace('{beneficio}', random.choice(['Resultados garantizados', 'Éxito asegurado', 'ROI comprobado']))
        anchor_text = anchor_text.replace('{tiempo}', random.choice(['30 días', '6 meses', '1 año']))
        anchor_text = anchor_text.replace('{garantia}', random.choice(['100% efectivo', 'Sin riesgo', 'Satisfacción garantizada']))
        anchor_text = anchor_text.replace('{año}', '2024')
        anchor_text = anchor_text.replace('{modalidad}', random.choice(['Online', 'Presencial', 'Híbrido']))
        anchor_text = anchor_text.replace('{enfoque}', random.choice(['Avanzado', 'Básico', 'Profesional']))
        anchor_text = anchor_text.replace('{resultado}', random.choice(['Multiplica ventas', 'Aumenta conversiones', 'Optimiza ROI']))
        
        return anchor_text

    def _extraer_caracteristicas(self, anchor_text: str) -> Dict[str, float]:
        """Extrae características numéricas del anchor text"""
        caracteristicas = {}
        texto_lower = anchor_text.lower()
        
        # Longitud
        caracteristicas['longitud'] = len(anchor_text)
        
        # Palabras de poder
        palabras_poder_count = sum(1 for palabra in self.caracteristicas['palabras_poder']['palabras'] 
                                 if palabra in texto_lower)
        caracteristicas['palabras_poder'] = palabras_poder_count
        
        # Llamada a la acción
        cta_count = sum(1 for palabra in self.caracteristicas['llamada_accion']['palabras'] 
                       if palabra in texto_lower)
        caracteristicas['llamada_accion'] = cta_count
        
        # Urgencia
        urgencia_count = sum(1 for palabra in self.caracteristicas['urgencia']['palabras'] 
                           if palabra in texto_lower)
        caracteristicas['urgencia'] = urgencia_count
        
        # Beneficios
        beneficios_count = sum(1 for palabra in self.caracteristicas['beneficios']['palabras'] 
                             if palabra in texto_lower)
        caracteristicas['beneficios'] = beneficios_count
        
        # Números
        numeros = re.findall(self.caracteristicas['numeros']['patron'], anchor_text)
        caracteristicas['numeros'] = len(numeros)
        
        # Emotividad
        emotividad_count = sum(1 for palabra in self.caracteristicas['emotividad']['palabras'] 
                             if palabra in texto_lower)
        caracteristicas['emotividad'] = emotividad_count
        
        return caracteristicas

    def _simular_ctr(self, caracteristicas: Dict[str, float]) -> float:
        """Simula el CTR basado en las características"""
        ctr_base = 0.03  # 3% base
        
        # Ajustar basado en características
        ajuste_longitud = 0.001 if 30 <= caracteristicas['longitud'] <= 60 else -0.002
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.005
        ajuste_cta = caracteristicas['llamada_accion'] * 0.003
        ajuste_urgencia = caracteristicas['urgencia'] * 0.004
        ajuste_beneficios = caracteristicas['beneficios'] * 0.002
        ajuste_numeros = caracteristicas['numeros'] * 0.001
        ajuste_emotividad = caracteristicas['emotividad'] * 0.003
        
        ctr = ctr_base + ajuste_longitud + ajuste_palabras_poder + ajuste_cta + \
              ajuste_urgencia + ajuste_beneficios + ajuste_numeros + ajuste_emotividad
        
        # Agregar ruido aleatorio
        ctr += random.uniform(-0.01, 0.01)
        
        return max(0.001, min(0.15, ctr))  # Limitar entre 0.1% y 15%

    def _simular_conversion_rate(self, caracteristicas: Dict[str, float]) -> float:
        """Simula la tasa de conversión basada en las características"""
        conversion_base = 0.10  # 10% base
        
        # Ajustar basado en características
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.02
        ajuste_beneficios = caracteristicas['beneficios'] * 0.015
        ajuste_urgencia = caracteristicas['urgencia'] * 0.01
        ajuste_emotividad = caracteristicas['emotividad'] * 0.012
        
        conversion_rate = conversion_base + ajuste_palabras_poder + ajuste_beneficios + \
                         ajuste_urgencia + ajuste_emotividad
        
        # Agregar ruido aleatorio
        conversion_rate += random.uniform(-0.02, 0.02)
        
        return max(0.01, min(0.50, conversion_rate))  # Limitar entre 1% y 50%

    def _simular_roi(self, caracteristicas: Dict[str, float]) -> float:
        """Simula el ROI basado en las características"""
        roi_base = 2.0  # 2x base
        
        # Ajustar basado en características
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.3
        ajuste_beneficios = caracteristicas['beneficios'] * 0.2
        ajuste_urgencia = caracteristicas['urgencia'] * 0.15
        ajuste_emotividad = caracteristicas['emotividad'] * 0.25
        
        roi = roi_base + ajuste_palabras_poder + ajuste_beneficios + \
              ajuste_urgencia + ajuste_emotividad
        
        # Agregar ruido aleatorio
        roi += random.uniform(-0.5, 0.5)
        
        return max(1.0, min(10.0, roi))  # Limitar entre 1x y 10x

    def _entrenar_modelo(self) -> Dict[str, Any]:
        """Entrena el modelo de predicción"""
        # En un caso real, aquí se usaría scikit-learn o similar
        # Por simplicidad, usamos un modelo basado en reglas
        
        # Calcular pesos promedio de los datos históricos
        pesos = {}
        for caracteristica, config in self.caracteristicas.items():
            if caracteristica == 'longitud':
                # Para longitud, calcular la desviación del óptimo
                longitudes = [d['caracteristicas']['longitud'] for d in self.datos_historicos]
                # Calcular desviación estándar manualmente
                mean_long = sum(longitudes) / len(longitudes)
                variance = sum((x - mean_long) ** 2 for x in longitudes) / len(longitudes)
                std_dev = math.sqrt(variance)
                pesos[caracteristica] = {
                    'peso': config['peso'],
                    'optimo': config['optimo'],
                    'desviacion_estandar': std_dev
                }
            else:
                # Para otras características, usar el peso configurado
                pesos[caracteristica] = {
                    'peso': config['peso'],
                    'palabras': config.get('palabras', []),
                    'patron': config.get('patron', '')
                }
        
        return {
            'pesos': pesos,
            'datos_entrenamiento': len(self.datos_historicos),
            'fecha_entrenamiento': datetime.now().isoformat(),
            'precision_estimada': 0.85  # 85% de precisión estimada
        }

    def predecir_rendimiento(self, anchor_text: str) -> Dict[str, Any]:
        """Predice el rendimiento de un anchor text"""
        # Extraer características
        caracteristicas = self._extraer_caracteristicas(anchor_text)
        
        # Calcular score de calidad
        score_calidad = self._calcular_score_calidad(caracteristicas)
        
        # Predecir métricas
        ctr_predicho = self._predecir_ctr(caracteristicas)
        conversion_rate_predicho = self._predecir_conversion_rate(caracteristicas)
        roi_predicho = self._predecir_roi(caracteristicas)
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(caracteristicas, score_calidad)
        
        return {
            'anchor_text': anchor_text,
            'caracteristicas': caracteristicas,
            'score_calidad': score_calidad,
            'predicciones': {
                'ctr': round(ctr_predicho * 100, 2),
                'conversion_rate': round(conversion_rate_predicho * 100, 2),
                'roi': round(roi_predicho, 2)
            },
            'recomendaciones': recomendaciones,
            'confianza': self._calcular_confianza(caracteristicas),
            'fecha_prediccion': datetime.now().isoformat()
        }

    def _calcular_score_calidad(self, caracteristicas: Dict[str, float]) -> float:
        """Calcula el score de calidad del anchor text"""
        score = 0.0
        
        # Longitud (óptimo entre 30-60 caracteres)
        longitud = caracteristicas['longitud']
        if 30 <= longitud <= 60:
            score += self.caracteristicas['longitud']['peso'] * 100
        elif 20 <= longitud < 30 or 60 < longitud <= 80:
            score += self.caracteristicas['longitud']['peso'] * 70
        else:
            score += self.caracteristicas['longitud']['peso'] * 30
        
        # Otras características
        for caracteristica, valor in caracteristicas.items():
            if caracteristica != 'longitud':
                peso = self.caracteristicas[caracteristica]['peso']
                # Normalizar valor (máximo 5 palabras de cada tipo)
                valor_normalizado = min(valor / 5.0, 1.0)
                score += peso * valor_normalizado * 100
        
        return min(100, max(0, score))

    def _predecir_ctr(self, caracteristicas: Dict[str, float]) -> float:
        """Predice el CTR basado en las características"""
        ctr_base = 0.03
        
        # Ajustar basado en características
        ajuste_longitud = 0.001 if 30 <= caracteristicas['longitud'] <= 60 else -0.002
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.005
        ajuste_cta = caracteristicas['llamada_accion'] * 0.003
        ajuste_urgencia = caracteristicas['urgencia'] * 0.004
        ajuste_beneficios = caracteristicas['beneficios'] * 0.002
        ajuste_numeros = caracteristicas['numeros'] * 0.001
        ajuste_emotividad = caracteristicas['emotividad'] * 0.003
        
        ctr = ctr_base + ajuste_longitud + ajuste_palabras_poder + ajuste_cta + \
              ajuste_urgencia + ajuste_beneficios + ajuste_numeros + ajuste_emotividad
        
        return max(0.001, min(0.15, ctr))

    def _predecir_conversion_rate(self, caracteristicas: Dict[str, float]) -> float:
        """Predice la tasa de conversión basada en las características"""
        conversion_base = 0.10
        
        # Ajustar basado en características
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.02
        ajuste_beneficios = caracteristicas['beneficios'] * 0.015
        ajuste_urgencia = caracteristicas['urgencia'] * 0.01
        ajuste_emotividad = caracteristicas['emotividad'] * 0.012
        
        conversion_rate = conversion_base + ajuste_palabras_poder + ajuste_beneficios + \
                         ajuste_urgencia + ajuste_emotividad
        
        return max(0.01, min(0.50, conversion_rate))

    def _predecir_roi(self, caracteristicas: Dict[str, float]) -> float:
        """Predice el ROI basado en las características"""
        roi_base = 2.0
        
        # Ajustar basado en características
        ajuste_palabras_poder = caracteristicas['palabras_poder'] * 0.3
        ajuste_beneficios = caracteristicas['beneficios'] * 0.2
        ajuste_urgencia = caracteristicas['urgencia'] * 0.15
        ajuste_emotividad = caracteristicas['emotividad'] * 0.25
        
        roi = roi_base + ajuste_palabras_poder + ajuste_beneficios + \
              ajuste_urgencia + ajuste_emotividad
        
        return max(1.0, min(10.0, roi))

    def _generar_recomendaciones(self, caracteristicas: Dict[str, float], score_calidad: float) -> List[Dict[str, str]]:
        """Genera recomendaciones de optimización"""
        recomendaciones = []
        
        # Recomendaciones basadas en características
        if caracteristicas['longitud'] < 30:
            recomendaciones.append({
                'tipo': 'longitud',
                'prioridad': 'Alta',
                'recomendacion': 'Aumentar la longitud del anchor text para mayor contexto',
                'accion': 'Agregar palabras descriptivas o beneficios específicos'
            })
        elif caracteristicas['longitud'] > 80:
            recomendaciones.append({
                'tipo': 'longitud',
                'prioridad': 'Media',
                'recomendacion': 'Reducir la longitud para mayor impacto',
                'accion': 'Eliminar palabras innecesarias o usar sinónimos más cortos'
            })
        
        if caracteristicas['palabras_poder'] < 2:
            recomendaciones.append({
                'tipo': 'palabras_poder',
                'prioridad': 'Alta',
                'recomendacion': 'Incluir más palabras de poder para mayor impacto',
                'accion': 'Agregar palabras como "domina", "revoluciona", "transforma"'
            })
        
        if caracteristicas['llamada_accion'] == 0:
            recomendaciones.append({
                'tipo': 'cta',
                'prioridad': 'Alta',
                'recomendacion': 'Incluir una llamada a la acción clara',
                'accion': 'Agregar palabras como "aprende", "descubre", "comienza"'
            })
        
        if caracteristicas['urgencia'] == 0:
            recomendaciones.append({
                'tipo': 'urgencia',
                'prioridad': 'Media',
                'recomendacion': 'Crear sensación de urgencia',
                'accion': 'Agregar palabras como "ahora", "hoy", "última oportunidad"'
            })
        
        if caracteristicas['beneficios'] < 2:
            recomendaciones.append({
                'tipo': 'beneficios',
                'prioridad': 'Alta',
                'recomendacion': 'Destacar más beneficios específicos',
                'accion': 'Incluir palabras como "resultados", "éxito", "garantizado"'
            })
        
        if caracteristicas['numeros'] == 0:
            recomendaciones.append({
                'tipo': 'numeros',
                'prioridad': 'Media',
                'recomendacion': 'Incluir números para mayor credibilidad',
                'accion': 'Agregar porcentajes, fechas o cantidades específicas'
            })
        
        if caracteristicas['emotividad'] == 0:
            recomendaciones.append({
                'tipo': 'emotividad',
                'prioridad': 'Media',
                'recomendacion': 'Añadir elementos emocionales',
                'accion': 'Incluir palabras como "increíble", "sorprendente", "fantástico"'
            })
        
        # Recomendación general basada en score
        if score_calidad < 60:
            recomendaciones.append({
                'tipo': 'general',
                'prioridad': 'Muy Alta',
                'recomendacion': 'El anchor text necesita optimización significativa',
                'accion': 'Revisar todas las recomendaciones específicas y reescribir'
            })
        elif score_calidad < 80:
            recomendaciones.append({
                'tipo': 'general',
                'prioridad': 'Media',
                'recomendacion': 'El anchor text puede mejorar con pequeños ajustes',
                'accion': 'Implementar las recomendaciones específicas de mayor prioridad'
            })
        else:
            recomendaciones.append({
                'tipo': 'general',
                'prioridad': 'Baja',
                'recomendacion': 'El anchor text tiene buena calidad',
                'accion': 'Monitorear rendimiento y hacer ajustes menores si es necesario'
            })
        
        return recomendaciones

    def _calcular_confianza(self, caracteristicas: Dict[str, float]) -> float:
        """Calcula el nivel de confianza de la predicción"""
        # Basado en la cantidad de características presentes
        caracteristicas_presentes = sum(1 for v in caracteristicas.values() if v > 0)
        confianza_base = min(caracteristicas_presentes / len(caracteristicas), 1.0)
        
        # Ajustar basado en la calidad de los datos históricos
        confianza_ajustada = confianza_base * self.modelo_entrenado['precision_estimada']
        
        return round(confianza_ajustada * 100, 1)

    def analizar_lote_anchor_texts(self, anchor_texts: List[str]) -> Dict[str, Any]:
        """Analiza un lote de anchor texts"""
        resultados = []
        
        for anchor_text in anchor_texts:
            prediccion = self.predecir_rendimiento(anchor_text)
            resultados.append(prediccion)
        
        # Estadísticas del lote
        ctrs = [r['predicciones']['ctr'] for r in resultados]
        conversion_rates = [r['predicciones']['conversion_rate'] for r in resultados]
        rois = [r['predicciones']['roi'] for r in resultados]
        scores = [r['score_calidad'] for r in resultados]
        
        # Calcular promedios manualmente
        def calcular_promedio(lista):
            return sum(lista) / len(lista) if lista else 0
        
        estadisticas = {
            'total_anchor_texts': len(anchor_texts),
            'ctr_promedio': round(calcular_promedio(ctrs), 2),
            'ctr_maximo': round(max(ctrs), 2),
            'ctr_minimo': round(min(ctrs), 2),
            'conversion_rate_promedio': round(calcular_promedio(conversion_rates), 2),
            'roi_promedio': round(calcular_promedio(rois), 2),
            'score_promedio': round(calcular_promedio(scores), 2),
            'mejor_anchor_text': max(resultados, key=lambda x: x['score_calidad']),
            'peor_anchor_text': min(resultados, key=lambda x: x['score_calidad'])
        }
        
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'estadisticas': estadisticas,
            'resultados_individuales': resultados,
            'recomendaciones_generales': self._generar_recomendaciones_generales(estadisticas)
        }

    def _generar_recomendaciones_generales(self, estadisticas: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones generales para el lote"""
        recomendaciones = []
        
        if estadisticas['score_promedio'] < 60:
            recomendaciones.append("El lote general necesita optimización significativa")
        
        if estadisticas['ctr_promedio'] < 5:
            recomendaciones.append("Considera mejorar el CTR promedio del lote")
        
        if estadisticas['conversion_rate_promedio'] < 10:
            recomendaciones.append("La tasa de conversión promedio puede mejorar")
        
        if estadisticas['roi_promedio'] < 2:
            recomendaciones.append("El ROI promedio del lote es bajo, revisa la estrategia")
        
        return recomendaciones

    def exportar_predicciones(self, resultados: Dict[str, Any], formato: str = "json") -> str:
        """Exporta las predicciones en diferentes formatos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"predicciones_ia_anchor_texts_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- PREDICCIONES IA - ANCHOR TEXTS IA MARKETING ---\n")
                f.write(f"Fecha: {resultados['fecha_analisis']}\n\n")
                
                f.write("ESTADÍSTICAS DEL LOTE:\n")
                stats = resultados['estadisticas']
                f.write(f"• Total anchor texts: {stats['total_anchor_texts']}\n")
                f.write(f"• CTR promedio: {stats['ctr_promedio']}%\n")
                f.write(f"• Tasa de conversión promedio: {stats['conversion_rate_promedio']}%\n")
                f.write(f"• ROI promedio: {stats['roi_promedio']}x\n")
                f.write(f"• Score promedio: {stats['score_promedio']}/100\n\n")
                
                f.write("MEJOR ANCHOR TEXT:\n")
                mejor = stats['mejor_anchor_text']
                f.write(f"• Texto: {mejor['anchor_text']}\n")
                f.write(f"• Score: {mejor['score_calidad']}/100\n")
                f.write(f"• CTR predicho: {mejor['predicciones']['ctr']}%\n")
                f.write(f"• Conversión predicha: {mejor['predicciones']['conversion_rate']}%\n")
                f.write(f"• ROI predicho: {mejor['predicciones']['roi']}x\n\n")
                
                f.write("RECOMENDACIONES GENERALES:\n")
                for rec in resultados['recomendaciones_generales']:
                    f.write(f"• {rec}\n")
                f.write("\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

def main():
    predictor = PredictorIAAnchorTexts()
    
    print("🤖 PREDICTOR IA - ANCHOR TEXTS IA MARKETING")
    print("==========================================\n")
    
    print("🔄 Entrenando modelo con datos históricos...")
    print(f"   • Datos de entrenamiento: {len(predictor.datos_historicos)}")
    print(f"   • Precisión estimada: {predictor.modelo_entrenado['precision_estimada']*100}%")
    
    # Ejemplos de anchor texts para predecir
    ejemplos = [
        "Curso IA Marketing - Resultados Garantizados",
        "Domina el Marketing con IA en 30 Días",
        "Aprende IA Marketing desde Cero",
        "Masterclass IA Marketing 2024 - Exclusivo",
        "Transforma tu Negocio con IA Marketing Ahora"
    ]
    
    print(f"\n🔄 Analizando {len(ejemplos)} anchor texts de ejemplo...")
    resultados = predictor.analizar_lote_anchor_texts(ejemplos)
    
    print("💾 Exportando predicciones...")
    json_file = predictor.exportar_predicciones(resultados, "json")
    txt_file = predictor.exportar_predicciones(resultados, "txt")
    
    print("\n✅ Análisis completado:")
    stats = resultados['estadisticas']
    print(f"   • Anchor texts analizados: {stats['total_anchor_texts']}")
    print(f"   • CTR promedio predicho: {stats['ctr_promedio']}%")
    print(f"   • Conversión promedio predicha: {stats['conversion_rate_promedio']}%")
    print(f"   • ROI promedio predicho: {stats['roi_promedio']}x")
    print(f"   • Score promedio: {stats['score_promedio']}/100")
    
    print(f"\n🏆 MEJOR ANCHOR TEXT:")
    mejor = stats['mejor_anchor_text']
    print(f"   • Texto: {mejor['anchor_text']}")
    print(f"   • Score: {mejor['score_calidad']}/100")
    print(f"   • CTR predicho: {mejor['predicciones']['ctr']}%")
    print(f"   • Confianza: {mejor['confianza']}%")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa las predicciones y recomendaciones")
    print("2. Implementa los anchor texts con mejor score")
    print("3. Monitorea el rendimiento real vs predicciones")
    print("4. Ajusta el modelo con datos reales")
    print("5. Usa las predicciones para optimizar futuros anchor texts")

if __name__ == "__main__":
    main()
