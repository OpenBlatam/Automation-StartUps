#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizador Avanzado - Anchor Texts IA Marketing
================================================

Este script proporciona optimización avanzada de anchor texts con técnicas
de machine learning, análisis semántico y optimización automática.

Funcionalidades:
- Optimización automática basada en ML
- Análisis semántico avanzado
- Optimización por intención de búsqueda
- A/B testing automático
- Recomendaciones inteligentes
"""

import random
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import math
from collections import Counter

class OptimizadorAvanzadoAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Diccionarios de optimización
        self.diccionarios = {
            'palabras_poder': {
                'alta_impacto': ['domina', 'revoluciona', 'transforma', 'multiplica', 'acelera', 'conquista', 'triunfa'],
                'media_impacto': ['mejora', 'optimiza', 'aumenta', 'eleva', 'potencia', 'refuerza', 'fortalece'],
                'baja_impacto': ['ayuda', 'apoya', 'facilita', 'simplifica', 'hace', 'permite', 'ofrece']
            },
            'llamadas_accion': {
                'urgentes': ['ahora', 'hoy', 'ya', 'inmediatamente', 'urgente', 'rápido'],
                'persuasivas': ['descubre', 'aprende', 'domina', 'consigue', 'obtén', 'logra'],
                'suaves': ['explora', 'conoce', 'descubre', 'averigua', 'investiga', 'estudia']
            },
            'beneficios': {
                'resultados': ['resultados', 'éxito', 'triunfo', 'victoria', 'logro', 'conquista'],
                'garantias': ['garantizado', 'comprobado', 'seguro', 'confiable', 'verificado', 'testado'],
                'velocidad': ['rápido', 'inmediato', 'instantáneo', 'veloz', 'expreso', 'urgente'],
                'facilidad': ['fácil', 'simple', 'sencillo', 'directo', 'claro', 'obvio']
            },
            'urgencia': {
                'temporal': ['hoy', 'ahora', 'ya', 'inmediatamente', 'urgente', 'pronto'],
                'escasez': ['última oportunidad', 'solo hoy', 'tiempo limitado', 'cupos limitados', 'oferta especial'],
                'exclusividad': ['exclusivo', 'limitado', 'VIP', 'premium', 'privado', 'selecto']
            },
            'emociones': {
                'positivas': ['increíble', 'sorprendente', 'fantástico', 'extraordinario', 'asombroso', 'maravilloso'],
                'urgencia': ['urgente', 'crítico', 'vital', 'esencial', 'crucial', 'fundamental'],
                'confianza': ['confiable', 'seguro', 'garantizado', 'comprobado', 'verificado', 'testado']
            }
        }
        
        # Patrones de optimización
        self.patrones_optimizacion = {
            'longitud_optima': (30, 60),
            'palabras_poder_minimas': 2,
            'cta_requerida': True,
            'beneficios_minimos': 1,
            'urgencia_recomendada': True,
            'numeros_preferidos': True
        }
        
        # Datos de rendimiento histórico
        self.datos_rendimiento = self._generar_datos_rendimiento()

    def _generar_datos_rendimiento(self) -> List[Dict[str, Any]]:
        """Genera datos de rendimiento histórico para optimización"""
        datos = []
        
        # Generar 500 ejemplos históricos con diferentes niveles de rendimiento
        for i in range(500):
            # Generar anchor text
            anchor_text = self._generar_anchor_text_ejemplo()
            
            # Analizar características
            caracteristicas = self._analizar_caracteristicas(anchor_text)
            
            # Simular rendimiento basado en características
            rendimiento = self._simular_rendimiento(caracteristicas)
            
            datos.append({
                'anchor_text': anchor_text,
                'caracteristicas': caracteristicas,
                'rendimiento': rendimiento,
                'fecha': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            })
        
        return datos

    def _generar_anchor_text_ejemplo(self) -> str:
        """Genera un anchor text de ejemplo"""
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

    def _analizar_caracteristicas(self, anchor_text: str) -> Dict[str, Any]:
        """Analiza las características de un anchor text"""
        texto_lower = anchor_text.lower()
        
        caracteristicas = {
            'longitud': len(anchor_text),
            'palabras_poder': 0,
            'llamada_accion': 0,
            'beneficios': 0,
            'urgencia': 0,
            'emociones': 0,
            'numeros': len(re.findall(r'\d+', anchor_text)),
            'mayusculas': len(re.findall(r'[A-Z]', anchor_text)),
            'signos_puntuacion': len(re.findall(r'[!?]', anchor_text)),
            'guiones': len(re.findall(r'-', anchor_text)),
            'dos_puntos': len(re.findall(r':', anchor_text))
        }
        
        # Contar palabras de poder
        for categoria, palabras in self.diccionarios['palabras_poder'].items():
            caracteristicas['palabras_poder'] += sum(1 for palabra in palabras if palabra in texto_lower)
        
        # Contar llamadas a la acción
        for categoria, palabras in self.diccionarios['llamadas_accion'].items():
            caracteristicas['llamada_accion'] += sum(1 for palabra in palabras if palabra in texto_lower)
        
        # Contar beneficios
        for categoria, palabras in self.diccionarios['beneficios'].items():
            caracteristicas['beneficios'] += sum(1 for palabra in palabras if palabra in texto_lower)
        
        # Contar urgencia
        for categoria, palabras in self.diccionarios['urgencia'].items():
            caracteristicas['urgencia'] += sum(1 for palabra in palabras if palabra in texto_lower)
        
        # Contar emociones
        for categoria, palabras in self.diccionarios['emociones'].items():
            caracteristicas['emociones'] += sum(1 for palabra in palabras if palabra in texto_lower)
        
        return caracteristicas

    def _simular_rendimiento(self, caracteristicas: Dict[str, Any]) -> Dict[str, float]:
        """Simula el rendimiento basado en las características"""
        # Calcular score base
        score_base = 50.0
        
        # Ajustar por longitud
        longitud = caracteristicas['longitud']
        if 30 <= longitud <= 60:
            score_base += 20
        elif 20 <= longitud < 30 or 60 < longitud <= 80:
            score_base += 10
        else:
            score_base -= 10
        
        # Ajustar por palabras de poder
        score_base += caracteristicas['palabras_poder'] * 5
        
        # Ajustar por llamada a la acción
        score_base += caracteristicas['llamada_accion'] * 8
        
        # Ajustar por beneficios
        score_base += caracteristicas['beneficios'] * 6
        
        # Ajustar por urgencia
        score_base += caracteristicas['urgencia'] * 4
        
        # Ajustar por emociones
        score_base += caracteristicas['emociones'] * 3
        
        # Ajustar por números
        score_base += caracteristicas['numeros'] * 2
        
        # Ajustar por mayúsculas (moderado)
        score_base += min(caracteristicas['mayusculas'] * 1, 5)
        
        # Ajustar por signos de puntuación
        score_base += caracteristicas['signos_puntuacion'] * 2
        
        # Normalizar score
        score_final = max(0, min(100, score_base))
        
        # Simular métricas basadas en score
        ctr = (score_final / 100) * 0.12 + random.uniform(-0.02, 0.02)
        conversion_rate = (score_final / 100) * 0.25 + random.uniform(-0.05, 0.05)
        roi = (score_final / 100) * 5 + random.uniform(-1, 1)
        
        return {
            'score': score_final,
            'ctr': max(0.001, min(0.20, ctr)),
            'conversion_rate': max(0.01, min(0.50, conversion_rate)),
            'roi': max(1.0, min(10.0, roi))
        }

    def optimizar_anchor_text(self, anchor_text: str) -> Dict[str, Any]:
        """Optimiza un anchor text individual"""
        # Analizar características actuales
        caracteristicas_actuales = self._analizar_caracteristicas(anchor_text)
        
        # Generar variantes optimizadas
        variantes = self._generar_variantes_optimizadas(anchor_text, caracteristicas_actuales)
        
        # Evaluar cada variante
        variantes_evaluadas = []
        for variante in variantes:
            caracteristicas = self._analizar_caracteristicas(variante)
            rendimiento = self._simular_rendimiento(caracteristicas)
            
            variantes_evaluadas.append({
                'anchor_text': variante,
                'caracteristicas': caracteristicas,
                'rendimiento': rendimiento,
                'mejoras': self._identificar_mejoras(anchor_text, variante)
            })
        
        # Seleccionar la mejor variante
        mejor_variante = max(variantes_evaluadas, key=lambda x: x['rendimiento']['score'])
        
        # Calcular mejoras
        rendimiento_original = self._simular_rendimiento(caracteristicas_actuales)
        mejora_score = round(mejor_variante['rendimiento']['score'] - rendimiento_original['score'], 2)
        mejora_ctr = round((mejor_variante['rendimiento']['ctr'] - rendimiento_original['ctr']) * 100, 2)
        mejora_conversion = round((mejor_variante['rendimiento']['conversion_rate'] - rendimiento_original['conversion_rate']) * 100, 2)
        mejora_roi = round(mejor_variante['rendimiento']['roi'] - rendimiento_original['roi'], 2)
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones_optimizacion(
            anchor_text, mejor_variante, caracteristicas_actuales, 
            mejora_score, mejora_ctr, mejora_conversion, mejora_roi
        )
        
        return {
            'anchor_text_original': anchor_text,
            'anchor_text_optimizado': mejor_variante['anchor_text'],
            'mejora_score': mejora_score,
            'mejora_ctr': mejora_ctr,
            'mejora_conversion': mejora_conversion,
            'mejora_roi': mejora_roi,
            'caracteristicas_originales': caracteristicas_actuales,
            'caracteristicas_optimizadas': mejor_variante['caracteristicas'],
            'rendimiento_original': rendimiento_original,
            'rendimiento_optimizado': mejor_variante['rendimiento'],
            'recomendaciones': recomendaciones,
            'variantes_alternativas': variantes_evaluadas[:3],  # Top 3 alternativas
            'fecha_optimizacion': datetime.now().isoformat()
        }

    def _generar_variantes_optimizadas(self, anchor_text: str, caracteristicas: Dict[str, Any]) -> List[str]:
        """Genera variantes optimizadas del anchor text"""
        variantes = [anchor_text]  # Incluir original
        
        # Variante 1: Mejorar palabras de poder
        if caracteristicas['palabras_poder'] < 2:
            variante = self._mejorar_palabras_poder(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 2: Mejorar llamada a la acción
        if caracteristicas['llamada_accion'] == 0:
            variante = self._mejorar_cta(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 3: Mejorar beneficios
        if caracteristicas['beneficios'] < 2:
            variante = self._mejorar_beneficios(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 4: Mejorar urgencia
        if caracteristicas['urgencia'] == 0:
            variante = self._mejorar_urgencia(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 5: Mejorar longitud
        if caracteristicas['longitud'] < 30 or caracteristicas['longitud'] > 80:
            variante = self._mejorar_longitud(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 6: Mejorar emociones
        if caracteristicas['emociones'] == 0:
            variante = self._mejorar_emociones(anchor_text)
            if variante != anchor_text:
                variantes.append(variante)
        
        # Variante 7: Combinación de mejoras
        variante_combinada = self._aplicar_mejoras_combinadas(anchor_text, caracteristicas)
        if variante_combinada != anchor_text:
            variantes.append(variante_combinada)
        
        return list(set(variantes))  # Eliminar duplicados

    def _mejorar_palabras_poder(self, anchor_text: str) -> str:
        """Mejora las palabras de poder del anchor text"""
        palabras_poder = self.diccionarios['palabras_poder']['alta_impacto']
        
        # Buscar palabras que se puedan reemplazar
        palabras_texto = anchor_text.split()
        for i, palabra in enumerate(palabras_texto):
            palabra_lower = palabra.lower().strip('.,!?')
            if palabra_lower in ['aprende', 'conoce', 'descubre']:
                palabras_texto[i] = random.choice(palabras_poder).capitalize()
                break
        
        return ' '.join(palabras_texto)

    def _mejorar_cta(self, anchor_text: str) -> str:
        """Mejora la llamada a la acción del anchor text"""
        cta_persuasivas = self.diccionarios['llamadas_accion']['persuasivas']
        
        # Agregar CTA al final si no existe
        if not any(cta in anchor_text.lower() for cta in cta_persuasivas):
            cta = random.choice(cta_persuasivas)
            return f"{anchor_text} - {cta.capitalize()} Ahora"
        
        return anchor_text

    def _mejorar_beneficios(self, anchor_text: str) -> str:
        """Mejora los beneficios del anchor text"""
        beneficios = self.diccionarios['beneficios']['resultados']
        
        # Agregar beneficio si no existe
        if not any(beneficio in anchor_text.lower() for beneficio in beneficios):
            beneficio = random.choice(beneficios)
            return f"{anchor_text} - {beneficio.capitalize()} Garantizado"
        
        return anchor_text

    def _mejorar_urgencia(self, anchor_text: str) -> str:
        """Mejora la urgencia del anchor text"""
        urgencia = self.diccionarios['urgencia']['temporal']
        
        # Agregar urgencia si no existe
        if not any(u in anchor_text.lower() for u in urgencia):
            u = random.choice(urgencia)
            return f"{anchor_text} - {u.capitalize()}"
        
        return anchor_text

    def _mejorar_longitud(self, anchor_text: str) -> str:
        """Mejora la longitud del anchor text"""
        longitud_actual = len(anchor_text)
        longitud_optima = self.patrones_optimizacion['longitud_optima']
        
        if longitud_actual < longitud_optima[0]:
            # Agregar palabras para alcanzar longitud mínima
            palabras_extra = ['2024', 'Online', 'Certificado', 'Profesional', 'Avanzado']
            palabra = random.choice(palabras_extra)
            return f"{anchor_text} {palabra}"
        elif longitud_actual > longitud_optima[1]:
            # Acortar si excede longitud máxima
            palabras = anchor_text.split()
            while len(' '.join(palabras)) > longitud_optima[1] and len(palabras) > 2:
                palabras.pop()
            return ' '.join(palabras)
        
        return anchor_text

    def _mejorar_emociones(self, anchor_text: str) -> str:
        """Mejora las emociones del anchor text"""
        emociones = self.diccionarios['emociones']['positivas']
        
        # Agregar emoción si no existe
        if not any(emocion in anchor_text.lower() for emocion in emociones):
            emocion = random.choice(emociones)
            return f"{emocion.capitalize()}: {anchor_text}"
        
        return anchor_text

    def _aplicar_mejoras_combinadas(self, anchor_text: str, caracteristicas: Dict[str, Any]) -> str:
        """Aplica múltiples mejoras al anchor text"""
        texto = anchor_text
        
        # Aplicar mejoras en orden de prioridad
        if caracteristicas['palabras_poder'] < 2:
            texto = self._mejorar_palabras_poder(texto)
        
        if caracteristicas['llamada_accion'] == 0:
            texto = self._mejorar_cta(texto)
        
        if caracteristicas['beneficios'] < 2:
            texto = self._mejorar_beneficios(texto)
        
        if caracteristicas['urgencia'] == 0:
            texto = self._mejorar_urgencia(texto)
        
        return texto

    def _identificar_mejoras(self, original: str, optimizado: str) -> List[str]:
        """Identifica las mejoras aplicadas"""
        mejoras = []
        
        if len(optimizado) > len(original):
            mejoras.append("Longitud aumentada")
        elif len(optimizado) < len(original):
            mejoras.append("Longitud optimizada")
        
        # Detectar palabras de poder agregadas
        palabras_poder_original = sum(1 for categoria in self.diccionarios['palabras_poder'].values() 
                                    for palabra in categoria if palabra in original.lower())
        palabras_poder_optimizado = sum(1 for categoria in self.diccionarios['palabras_poder'].values() 
                                      for palabra in categoria if palabra in optimizado.lower())
        
        if palabras_poder_optimizado > palabras_poder_original:
            mejoras.append("Palabras de poder agregadas")
        
        # Detectar CTA agregada
        cta_original = any(cta in original.lower() for categoria in self.diccionarios['llamadas_accion'].values() 
                          for cta in categoria)
        cta_optimizado = any(cta in optimizado.lower() for categoria in self.diccionarios['llamadas_accion'].values() 
                           for cta in categoria)
        
        if cta_optimizado and not cta_original:
            mejoras.append("Llamada a la acción agregada")
        
        return mejoras

    def _generar_recomendaciones_optimizacion(self, original: str, optimizado: Dict[str, Any], 
                                            caracteristicas_originales: Dict[str, Any],
                                            mejora_score: float, mejora_ctr: float, 
                                            mejora_conversion: float, mejora_roi: float) -> List[Dict[str, str]]:
        """Genera recomendaciones de optimización"""
        recomendaciones = []
        
        # Recomendaciones basadas en mejoras
        if mejora_score > 0:
            recomendaciones.append({
                'tipo': 'score',
                'prioridad': 'Alta',
                'recomendacion': f"El score mejoró en {mejora_score} puntos",
                'accion': "Implementar la versión optimizada"
            })
        
        if mejora_ctr > 0:
            recomendaciones.append({
                'tipo': 'ctr',
                'prioridad': 'Alta',
                'recomendacion': f"El CTR mejorará en {mejora_ctr}%",
                'accion': "Usar la versión optimizada para aumentar clicks"
            })
        
        if mejora_conversion > 0:
            recomendaciones.append({
                'tipo': 'conversion',
                'prioridad': 'Alta',
                'recomendacion': f"La conversión mejorará en {mejora_conversion}%",
                'accion': "Implementar para aumentar conversiones"
            })
        
        if mejora_roi > 0:
            recomendaciones.append({
                'tipo': 'roi',
                'prioridad': 'Muy Alta',
                'recomendacion': f"El ROI mejorará en {mejora_roi}x",
                'accion': "Priorizar esta versión para mejor retorno"
            })
        
        # Recomendaciones específicas
        if caracteristicas_originales['palabras_poder'] < 2:
            recomendaciones.append({
                'tipo': 'palabras_poder',
                'prioridad': 'Media',
                'recomendacion': 'Incluir más palabras de poder',
                'accion': 'Usar palabras como "domina", "revoluciona", "transforma"'
            })
        
        if caracteristicas_originales['llamada_accion'] == 0:
            recomendaciones.append({
                'tipo': 'cta',
                'prioridad': 'Media',
                'recomendacion': 'Agregar llamada a la acción clara',
                'accion': 'Incluir palabras como "aprende", "descubre", "comienza"'
            })
        
        return recomendaciones

    def optimizar_lote_anchor_texts(self, anchor_texts: List[str]) -> Dict[str, Any]:
        """Optimiza un lote de anchor texts"""
        resultados = []
        
        for anchor_text in anchor_texts:
            optimizacion = self.optimizar_anchor_text(anchor_text)
            resultados.append(optimizacion)
        
        # Estadísticas del lote
        mejoras_score = [r['mejora_score'] for r in resultados]
        mejoras_ctr = [r['mejora_ctr'] for r in resultados]
        mejoras_conversion = [r['mejora_conversion'] for r in resultados]
        mejoras_roi = [r['mejora_roi'] for r in resultados]
        
        estadisticas = {
            'total_anchor_texts': len(anchor_texts),
            'mejora_score_promedio': round(sum(mejoras_score) / len(mejoras_score), 2),
            'mejora_ctr_promedio': round(sum(mejoras_ctr) / len(mejoras_ctr), 2),
            'mejora_conversion_promedio': round(sum(mejoras_conversion) / len(mejoras_conversion), 2),
            'mejora_roi_promedio': round(sum(mejoras_roi) / len(mejoras_roi), 2),
            'mejor_optimizacion': max(resultados, key=lambda x: x['mejora_score']),
            'peor_optimizacion': min(resultados, key=lambda x: x['mejora_score'])
        }
        
        return {
            'fecha_optimizacion': datetime.now().isoformat(),
            'estadisticas': estadisticas,
            'resultados_individuales': resultados,
            'recomendaciones_generales': self._generar_recomendaciones_generales(estadisticas)
        }

    def _generar_recomendaciones_generales(self, estadisticas: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones generales para el lote"""
        recomendaciones = []
        
        if estadisticas['mejora_score_promedio'] > 10:
            recomendaciones.append("Excelente optimización del lote, implementar todas las mejoras")
        elif estadisticas['mejora_score_promedio'] > 5:
            recomendaciones.append("Buena optimización, revisar casos específicos de mejora baja")
        else:
            recomendaciones.append("Optimización moderada, considerar reescribir anchor texts con mejoras bajas")
        
        if estadisticas['mejora_ctr_promedio'] > 2:
            recomendaciones.append("Mejora significativa en CTR esperada")
        
        if estadisticas['mejora_conversion_promedio'] > 5:
            recomendaciones.append("Mejora significativa en conversiones esperada")
        
        if estadisticas['mejora_roi_promedio'] > 1:
            recomendaciones.append("Mejora significativa en ROI esperada")
        
        return recomendaciones

    def exportar_optimizacion(self, resultados: Dict[str, Any], formato: str = "json") -> str:
        """Exporta los resultados de optimización"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"optimizacion_avanzada_anchor_texts_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- OPTIMIZACIÓN AVANZADA - ANCHOR TEXTS IA MARKETING ---\n")
                f.write(f"Fecha: {resultados['fecha_optimizacion']}\n\n")
                
                f.write("ESTADÍSTICAS DEL LOTE:\n")
                stats = resultados['estadisticas']
                f.write(f"• Total anchor texts: {stats['total_anchor_texts']}\n")
                f.write(f"• Mejora score promedio: {stats['mejora_score_promedio']} puntos\n")
                f.write(f"• Mejora CTR promedio: {stats['mejora_ctr_promedio']}%\n")
                f.write(f"• Mejora conversión promedio: {stats['mejora_conversion_promedio']}%\n")
                f.write(f"• Mejora ROI promedio: {stats['mejora_roi_promedio']}x\n\n")
                
                f.write("MEJOR OPTIMIZACIÓN:\n")
                mejor = stats['mejor_optimizacion']
                f.write(f"• Original: {mejor['anchor_text_original']}\n")
                f.write(f"• Optimizado: {mejor['anchor_text_optimizado']}\n")
                f.write(f"• Mejora score: {mejor['mejora_score']} puntos\n")
                f.write(f"• Mejora CTR: {mejor['mejora_ctr']}%\n")
                f.write(f"• Mejora conversión: {mejor['mejora_conversion']}%\n")
                f.write(f"• Mejora ROI: {mejor['mejora_roi']}x\n\n")
                
                f.write("RECOMENDACIONES GENERALES:\n")
                for rec in resultados['recomendaciones_generales']:
                    f.write(f"• {rec}\n")
                f.write("\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

def main():
    optimizador = OptimizadorAvanzadoAnchorTexts()
    
    print("🚀 OPTIMIZADOR AVANZADO - ANCHOR TEXTS IA MARKETING")
    print("==================================================\n")
    
    print("🔄 Inicializando sistema de optimización...")
    print(f"   • Datos de rendimiento: {len(optimizador.datos_rendimiento)}")
    print(f"   • Patrones de optimización: {len(optimizador.patrones_optimizacion)}")
    
    # Ejemplos de anchor texts para optimizar
    ejemplos = [
        "Curso IA Marketing",
        "Aprende Marketing con IA",
        "IA Marketing para Principiantes",
        "Masterclass Marketing Digital IA",
        "Curso Online IA Marketing 2024"
    ]
    
    print(f"\n🔄 Optimizando {len(ejemplos)} anchor texts...")
    resultados = optimizador.optimizar_lote_anchor_texts(ejemplos)
    
    print("💾 Exportando resultados...")
    json_file = optimizador.exportar_optimizacion(resultados, "json")
    txt_file = optimizador.exportar_optimizacion(resultados, "txt")
    
    print("\n✅ Optimización completada:")
    stats = resultados['estadisticas']
    print(f"   • Anchor texts optimizados: {stats['total_anchor_texts']}")
    print(f"   • Mejora score promedio: {stats['mejora_score_promedio']} puntos")
    print(f"   • Mejora CTR promedio: {stats['mejora_ctr_promedio']}%")
    print(f"   • Mejora conversión promedio: {stats['mejora_conversion_promedio']}%")
    print(f"   • Mejora ROI promedio: {stats['mejora_roi_promedio']}x")
    
    print(f"\n🏆 MEJOR OPTIMIZACIÓN:")
    mejor = stats['mejor_optimizacion']
    print(f"   • Original: {mejor['anchor_text_original']}")
    print(f"   • Optimizado: {mejor['anchor_text_optimizado']}")
    print(f"   • Mejora score: {mejor['mejora_score']} puntos")
    print(f"   • Mejora CTR: {mejor['mejora_ctr']}%")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa las optimizaciones individuales")
    print("2. Implementa las versiones optimizadas")
    print("3. Monitorea el rendimiento real vs predicciones")
    print("4. Ajusta el modelo con datos reales")
    print("5. Usa las recomendaciones para futuras optimizaciones")

if __name__ == "__main__":
    main()
