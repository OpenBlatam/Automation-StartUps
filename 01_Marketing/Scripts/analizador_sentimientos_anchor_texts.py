#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de Sentimientos - Anchor Texts IA Marketing
====================================================

Este script analiza los sentimientos y emociones en los anchor texts
para optimizar el impacto emocional y la persuasión.

Funcionalidades:
- Análisis de sentimientos (positivo, negativo, neutral)
- Detección de emociones específicas
- Análisis de persuasión emocional
- Recomendaciones de optimización emocional
- Generación de variantes emocionales
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re
from collections import Counter

class AnalizadorSentimientosAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Diccionario de sentimientos
        self.diccionario_sentimientos = {
            'positivo': {
                'palabras': [
                    'excelente', 'fantástico', 'increíble', 'sorprendente', 'maravilloso',
                    'perfecto', 'genial', 'brillante', 'extraordinario', 'asombroso',
                    'increíble', 'sorprendente', 'fantástico', 'maravilloso', 'excelente',
                    'éxito', 'triunfo', 'victoria', 'logro', 'conquista', 'domina',
                    'revoluciona', 'transforma', 'multiplica', 'acelera', 'optimiza'
                ],
                'intensidad': 0.8
            },
            'negativo': {
                'palabras': [
                    'terrible', 'horrible', 'pésimo', 'malo', 'decepcionante',
                    'frustrante', 'difícil', 'complejo', 'confuso', 'problemático',
                    'fracaso', 'pérdida', 'error', 'fallo', 'decepción'
                ],
                'intensidad': -0.8
            },
            'neutral': {
                'palabras': [
                    'curso', 'aprende', 'descubre', 'conoce', 'información',
                    'guía', 'tutorial', 'método', 'técnica', 'estrategia',
                    'herramienta', 'sistema', 'proceso', 'enfoque', 'método'
                ],
                'intensidad': 0.0
            }
        }
        
        # Diccionario de emociones específicas
        self.diccionario_emociones = {
            'alegria': {
                'palabras': ['feliz', 'alegre', 'contento', 'satisfecho', 'orgulloso'],
                'intensidad': 0.7
            },
            'confianza': {
                'palabras': ['confiable', 'seguro', 'garantizado', 'comprobado', 'verificado'],
                'intensidad': 0.6
            },
            'anticipacion': {
                'palabras': ['espera', 'pronto', 'futuro', 'nuevo', 'innovador'],
                'intensidad': 0.5
            },
            'sorpresa': {
                'palabras': ['sorprendente', 'increíble', 'asombroso', 'increíble', 'extraordinario'],
                'intensidad': 0.8
            },
            'miedo': {
                'palabras': ['urgente', 'crítico', 'vital', 'esencial', 'crucial'],
                'intensidad': -0.6
            },
            'ira': {
                'palabras': ['frustrante', 'difícil', 'complejo', 'problemático', 'confuso'],
                'intensidad': -0.7
            },
            'tristeza': {
                'palabras': ['decepcionante', 'fracaso', 'pérdida', 'error', 'fallo'],
                'intensidad': -0.8
            },
            'asombro': {
                'palabras': ['increíble', 'sorprendente', 'fantástico', 'maravilloso', 'extraordinario'],
                'intensidad': 0.9
            }
        }
        
        # Palabras de persuasión
        self.palabras_persuasion = {
            'urgencia': ['ahora', 'hoy', 'ya', 'inmediatamente', 'urgente', 'pronto'],
            'escasez': ['limitado', 'exclusivo', 'última oportunidad', 'solo hoy', 'tiempo limitado'],
            'autoridad': ['experto', 'profesional', 'certificado', 'avanzado', 'master'],
            'beneficio': ['resultados', 'éxito', 'ganancia', 'beneficio', 'ventaja'],
            'social': ['recomendado', 'popular', 'exitoso', 'comprobado', 'confiable']
        }

    def analizar_sentimiento(self, anchor_text: str) -> Dict[str, Any]:
        """Analiza el sentimiento general del anchor text"""
        texto_lower = anchor_text.lower()
        
        # Contar palabras por sentimiento
        sentimientos_count = {}
        for sentimiento, config in self.diccionario_sentimientos.items():
            count = sum(1 for palabra in config['palabras'] if palabra in texto_lower)
            sentimientos_count[sentimiento] = count
        
        # Calcular score de sentimiento
        score_sentimiento = 0
        total_palabras = len(anchor_text.split())
        
        for sentimiento, count in sentimientos_count.items():
            intensidad = self.diccionario_sentimientos[sentimiento]['intensidad']
            score_sentimiento += (count / total_palabras) * intensidad if total_palabras > 0 else 0
        
        # Normalizar score (-1 a 1)
        score_normalizado = max(-1, min(1, score_sentimiento))
        
        # Determinar sentimiento predominante
        sentimiento_predominante = max(sentimientos_count.items(), key=lambda x: x[1])[0]
        
        # Calcular confianza
        total_palabras_sentimiento = sum(sentimientos_count.values())
        confianza = (total_palabras_sentimiento / total_palabras) * 100 if total_palabras > 0 else 0
        
        return {
            'anchor_text': anchor_text,
            'score_sentimiento': round(score_normalizado, 3),
            'sentimiento_predominante': sentimiento_predominante,
            'confianza': round(confianza, 1),
            'distribucion_sentimientos': sentimientos_count,
            'total_palabras': total_palabras,
            'palabras_sentimiento': total_palabras_sentimiento
        }

    def analizar_emociones(self, anchor_text: str) -> Dict[str, Any]:
        """Analiza las emociones específicas del anchor text"""
        texto_lower = anchor_text.lower()
        
        # Contar emociones
        emociones_count = {}
        for emocion, config in self.diccionario_emociones.items():
            count = sum(1 for palabra in config['palabras'] if palabra in texto_lower)
            emociones_count[emocion] = count
        
        # Calcular intensidad emocional
        intensidad_total = 0
        total_palabras = len(anchor_text.split())
        
        for emocion, count in emociones_count.items():
            intensidad = self.diccionario_emociones[emocion]['intensidad']
            intensidad_total += (count / total_palabras) * intensidad if total_palabras > 0 else 0
        
        # Normalizar intensidad (-1 a 1)
        intensidad_normalizada = max(-1, min(1, intensidad_total))
        
        # Determinar emociones predominantes
        emociones_ordenadas = sorted(emociones_count.items(), key=lambda x: x[1], reverse=True)
        emociones_predominantes = [emotion for emotion, count in emociones_ordenadas if count > 0]
        
        return {
            'anchor_text': anchor_text,
            'intensidad_emocional': round(intensidad_normalizada, 3),
            'emociones_predominantes': emociones_predominantes[:3],
            'distribucion_emociones': emociones_count,
            'emocion_principal': emociones_predominantes[0] if emociones_predominantes else 'neutral'
        }

    def analizar_persuasion(self, anchor_text: str) -> Dict[str, Any]:
        """Analiza los elementos de persuasión del anchor text"""
        texto_lower = anchor_text.lower()
        
        # Contar elementos de persuasión
        persuasion_count = {}
        for elemento, palabras in self.palabras_persuasion.items():
            count = sum(1 for palabra in palabras if palabra in texto_lower)
            persuasion_count[elemento] = count
        
        # Calcular score de persuasión
        total_elementos = sum(persuasion_count.values())
        total_palabras = len(anchor_text.split())
        score_persuasion = (total_elementos / total_palabras) * 100 if total_palabras > 0 else 0
        
        # Determinar elementos predominantes
        elementos_ordenados = sorted(persuasion_count.items(), key=lambda x: x[1], reverse=True)
        elementos_predominantes = [elemento for elemento, count in elementos_ordenados if count > 0]
        
        return {
            'anchor_text': anchor_text,
            'score_persuasion': round(score_persuasion, 2),
            'elementos_predominantes': elementos_predominantes,
            'distribucion_persuasion': persuasion_count,
            'total_elementos': total_elementos
        }

    def analizar_completo(self, anchor_text: str) -> Dict[str, Any]:
        """Realiza un análisis completo de sentimientos, emociones y persuasión"""
        sentimiento = self.analizar_sentimiento(anchor_text)
        emociones = self.analizar_emociones(anchor_text)
        persuasion = self.analizar_persuasion(anchor_text)
        
        # Calcular score general
        score_general = (
            (sentimiento['score_sentimiento'] + 1) * 50 +  # Convertir -1,1 a 0,100
            (emociones['intensidad_emocional'] + 1) * 25 +  # Convertir -1,1 a 0,50
            persuasion['score_persuasion'] * 0.5  # Ya está en 0,100
        ) / 2
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones_emocionales(
            sentimiento, emociones, persuasion
        )
        
        return {
            'anchor_text': anchor_text,
            'fecha_analisis': datetime.now().isoformat(),
            'sentimiento': sentimiento,
            'emociones': emociones,
            'persuasion': persuasion,
            'score_general': round(score_general, 2),
            'recomendaciones': recomendaciones
        }

    def _generar_recomendaciones_emocionales(self, sentimiento: Dict[str, Any], 
                                           emociones: Dict[str, Any], 
                                           persuasion: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en el análisis emocional"""
        recomendaciones = []
        
        # Recomendaciones de sentimiento
        if sentimiento['score_sentimiento'] < 0.2:
            recomendaciones.append({
                'categoria': 'sentimiento',
                'prioridad': 'Alta',
                'recomendacion': 'El anchor text tiene un sentimiento muy neutral o negativo',
                'accion': 'Agrega palabras positivas como "excelente", "fantástico", "increíble"'
            })
        elif sentimiento['score_sentimiento'] > 0.8:
            recomendaciones.append({
                'categoria': 'sentimiento',
                'prioridad': 'Baja',
                'recomendacion': 'El anchor text tiene un sentimiento muy positivo',
                'accion': 'Considera si es apropiado para tu audiencia y objetivo'
            })
        
        # Recomendaciones de emociones
        if not emociones['emociones_predominantes']:
            recomendaciones.append({
                'categoria': 'emociones',
                'prioridad': 'Media',
                'recomendacion': 'El anchor text no evoca emociones específicas',
                'accion': 'Incluye palabras que generen confianza, anticipación o asombro'
            })
        
        # Recomendaciones de persuasión
        if persuasion['score_persuasion'] < 10:
            recomendaciones.append({
                'categoria': 'persuasion',
                'prioridad': 'Alta',
                'recomendacion': 'El anchor text tiene pocos elementos de persuasión',
                'accion': 'Agrega urgencia, escasez o elementos de autoridad'
            })
        
        # Recomendaciones específicas por emoción predominante
        emocion_principal = emociones['emocion_principal']
        if emocion_principal == 'miedo':
            recomendaciones.append({
                'categoria': 'emociones',
                'prioridad': 'Media',
                'recomendacion': 'El anchor text evoca miedo, considera el balance',
                'accion': 'Combina con elementos de confianza y beneficio'
            })
        elif emocion_principal == 'asombro':
            recomendaciones.append({
                'categoria': 'emociones',
                'prioridad': 'Baja',
                'recomendacion': 'Excelente uso del asombro',
                'accion': 'Mantén este enfoque emocional'
            })
        
        return recomendaciones

    def generar_variantes_emocionales(self, anchor_text: str, 
                                    emocion_objetivo: str = None) -> List[Dict[str, Any]]:
        """Genera variantes del anchor text con diferentes emociones"""
        if emocion_objetivo and emocion_objetivo not in self.diccionario_emociones:
            raise ValueError(f"Emoción '{emocion_objetivo}' no encontrada")
        
        variantes = []
        
        # Si no se especifica emoción, generar para todas
        emociones_a_probar = [emocion_objetivo] if emocion_objetivo else list(self.diccionario_emociones.keys())
        
        for emocion in emociones_a_probar:
            palabras_emocion = self.diccionario_emociones[emocion]['palabras']
            palabra_emocion = random.choice(palabras_emocion)
            
            # Generar variante
            variante = f"{palabra_emocion.capitalize()}: {anchor_text}"
            
            # Analizar la variante
            analisis = self.analizar_completo(variante)
            
            variantes.append({
                'variante': variante,
                'emocion_objetivo': emocion,
                'analisis': analisis,
                'mejora_score': analisis['score_general'] - self.analizar_completo(anchor_text)['score_general']
            })
        
        return variantes

    def optimizar_emocionalmente(self, anchor_text: str) -> Dict[str, Any]:
        """Optimiza un anchor text para máximo impacto emocional"""
        analisis_actual = self.analizar_completo(anchor_text)
        
        # Generar variantes emocionales
        variantes = self.generar_variantes_emocionales(anchor_text)
        
        # Seleccionar la mejor variante
        mejor_variante = max(variantes, key=lambda x: x['analisis']['score_general'])
        
        # Generar recomendaciones de optimización
        recomendaciones_optimizacion = self._generar_recomendaciones_optimizacion(
            analisis_actual, mejor_variante['analisis']
        )
        
        return {
            'anchor_text_original': anchor_text,
            'anchor_text_optimizado': mejor_variante['variante'],
            'emocion_aplicada': mejor_variante['emocion_objetivo'],
            'mejora_score': mejor_variante['mejora_score'],
            'analisis_original': analisis_actual,
            'analisis_optimizado': mejor_variante['analisis'],
            'recomendaciones': recomendaciones_optimizacion,
            'variantes_alternativas': variantes[:3],  # Top 3 alternativas
            'fecha_optimizacion': datetime.now().isoformat()
        }

    def _generar_recomendaciones_optimizacion(self, analisis_original: Dict[str, Any], 
                                            analisis_optimizado: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones de optimización emocional"""
        recomendaciones = []
        
        # Comparar scores
        mejora_score = analisis_optimizado['score_general'] - analisis_original['score_general']
        if mejora_score > 0:
            recomendaciones.append({
                'categoria': 'optimizacion',
                'prioridad': 'Alta',
                'recomendacion': f'La optimización mejora el score en {mejora_score:.2f} puntos',
                'accion': 'Implementa la versión optimizada para mayor impacto emocional'
            })
        
        # Comparar sentimientos
        if analisis_optimizado['sentimiento']['score_sentimiento'] > analisis_original['sentimiento']['score_sentimiento']:
            recomendaciones.append({
                'categoria': 'sentimiento',
                'prioridad': 'Media',
                'recomendacion': 'La versión optimizada tiene mejor sentimiento',
                'accion': 'Usa la versión optimizada para mayor positividad'
            })
        
        # Comparar persuasión
        if analisis_optimizado['persuasion']['score_persuasion'] > analisis_original['persuasion']['score_persuasion']:
            recomendaciones.append({
                'categoria': 'persuasion',
                'prioridad': 'Media',
                'recomendacion': 'La versión optimizada es más persuasiva',
                'accion': 'Implementa para mayor conversión'
            })
        
        return recomendaciones

    def exportar_analisis_sentimientos(self, resultados: Dict[str, Any], formato: str = "json") -> str:
        """Exporta el análisis de sentimientos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"analisis_sentimientos_anchor_texts_{timestamp}"
        
        if formato == "json":
            filename = f"{base_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=4)
            return filename
        elif formato == "txt":
            filename = f"{base_filename}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"--- ANÁLISIS DE SENTIMIENTOS - ANCHOR TEXTS IA MARKETING ---\n")
                f.write(f"Fecha: {resultados['fecha_analisis']}\n\n")
                
                f.write("ANÁLISIS COMPLETO:\n")
                f.write(f"• Anchor text: {resultados['anchor_text']}\n")
                f.write(f"• Score general: {resultados['score_general']}/100\n\n")
                
                f.write("SENTIMIENTO:\n")
                sent = resultados['sentimiento']
                f.write(f"• Score: {sent['score_sentimiento']}\n")
                f.write(f"• Predominante: {sent['sentimiento_predominante']}\n")
                f.write(f"• Confianza: {sent['confianza']}%\n\n")
                
                f.write("EMOCIONES:\n")
                emo = resultados['emociones']
                f.write(f"• Intensidad: {emo['intensidad_emocional']}\n")
                f.write(f"• Principal: {emo['emocion_principal']}\n")
                f.write(f"• Predominantes: {', '.join(emo['emociones_predominantes'])}\n\n")
                
                f.write("PERSUASIÓN:\n")
                pers = resultados['persuasion']
                f.write(f"• Score: {pers['score_persuasion']}/100\n")
                f.write(f"• Elementos: {', '.join(pers['elementos_predominantes'])}\n\n")
                
                f.write("RECOMENDACIONES:\n")
                for rec in resultados['recomendaciones']:
                    f.write(f"• {rec['categoria'].title()} ({rec['prioridad']}): {rec['recomendacion']}\n")
                    f.write(f"  Acción: {rec['accion']}\n")
                f.write("\n")
            
            return filename
        else:
            raise ValueError("Formato no soportado. Use 'json' o 'txt'.")

def main():
    analizador = AnalizadorSentimientosAnchorTexts()
    
    print("😊 ANALIZADOR DE SENTIMIENTOS - ANCHOR TEXTS IA MARKETING")
    print("=======================================================\n")
    
    # Ejemplos de anchor texts para analizar
    ejemplos = [
        "Curso IA Marketing - Resultados Garantizados",
        "Aprende IA Marketing desde Cero",
        "Domina el Marketing con IA en 30 Días",
        "Masterclass IA Marketing 2024 - Exclusivo",
        "Transforma tu Negocio con IA Marketing Ahora"
    ]
    
    print("🔄 Analizando sentimientos y emociones...\n")
    
    resultados_completos = []
    for anchor_text in ejemplos:
        print(f"Analizando: {anchor_text}")
        analisis = analizador.analizar_completo(anchor_text)
        resultados_completos.append(analisis)
        
        print(f"  • Sentimiento: {analisis['sentimiento']['sentimiento_predominante']} ({analisis['sentimiento']['score_sentimiento']})")
        print(f"  • Emoción: {analisis['emociones']['emocion_principal']}")
        print(f"  • Persuasión: {analisis['persuasion']['score_persuasion']}/100")
        print(f"  • Score general: {analisis['score_general']}/100\n")
    
    print("🔄 Optimizando anchor text emocionalmente...\n")
    optimizacion = analizador.optimizar_emocionalmente(ejemplos[0])
    
    print("💾 Exportando análisis...\n")
    json_file = analizador.exportar_analisis_sentimientos(resultados_completos[0], "json")
    txt_file = analizador.exportar_analisis_sentimientos(resultados_completos[0], "txt")
    
    print("✅ Análisis completado:")
    print(f"   • Anchor texts analizados: {len(ejemplos)}")
    print(f"   • Score promedio: {sum(r['score_general'] for r in resultados_completos) / len(resultados_completos):.2f}/100")
    
    print(f"\n🏆 MEJOR OPTIMIZACIÓN:")
    print(f"   • Original: {optimizacion['anchor_text_original']}")
    print(f"   • Optimizado: {optimizacion['anchor_text_optimizado']}")
    print(f"   • Emoción aplicada: {optimizacion['emocion_aplicada']}")
    print(f"   • Mejora score: {optimizacion['mejora_score']:.2f} puntos")
    
    print(f"\n📁 Archivos generados:")
    print(f"   • JSON: {json_file}")
    print(f"   • TXT: {txt_file}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisa el análisis de sentimientos y emociones")
    print("2. Implementa las optimizaciones emocionales")
    print("3. A/B testa diferentes enfoques emocionales")
    print("4. Monitorea el impacto en conversiones")
    print("5. Refina la estrategia emocional basada en resultados")

if __name__ == "__main__":
    main()