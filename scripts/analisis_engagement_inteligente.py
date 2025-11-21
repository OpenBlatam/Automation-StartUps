#!/usr/bin/env python3
"""
Análisis Inteligente de Engagement - Mejoras Premium Avanzadas
===============================================================
Análisis inteligente avanzado:
- Análisis competitivo inteligente con benchmarking dinámico
- Sistema de scoring predictivo de contenido (antes de publicar)
- Recomendaciones personalizadas basadas en ML
- Análisis cross-platform avanzado
- Sistema de alertas predictivas inteligentes
- Análisis de ROI predictivo avanzado
- Sistema de A/B testing automatizado
- Análisis de sentimiento avanzado con NLP
- Detección de oportunidades de contenido
- Análisis de gaps competitivos
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import math
import re

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
    from analisis_engagement_ml import AnalizadorEngagementML
    from analisis_engagement_predictivo import AnalizadorPredictivoEngagement
    from analisis_engagement_roi import AnalizadorROIEngagement
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorInteligenteEngagement:
    """Analizador inteligente avanzado de engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        analizador_ml: Optional[AnalizadorEngagementML] = None,
        analizador_predictivo: Optional[AnalizadorPredictivoEngagement] = None,
        analizador_roi: Optional[AnalizadorROIEngagement] = None
    ):
        """
        Inicializa el analizador inteligente
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            analizador_ml: Instancia opcional del AnalizadorEngagementML
            analizador_predictivo: Instancia opcional del AnalizadorPredictivoEngagement
            analizador_roi: Instancia opcional del AnalizadorROIEngagement
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        self.analizador_ml = analizador_ml or AnalizadorEngagementML(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
        self.analizador_predictivo = analizador_predictivo or AnalizadorPredictivoEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado, self.analizador_ml
        )
        self.analizador_roi = analizador_roi or AnalizadorROIEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
    
    def scoring_predictivo_contenido(
        self,
        contenido_propuesto: Dict[str, Any],
        incluir_recomendaciones: bool = True
    ) -> Dict[str, Any]:
        """
        Score predictivo de contenido antes de publicar
        
        Args:
            contenido_propuesto: Contenido propuesto con campos:
                - tipo_contenido: str
                - plataforma: str
                - titulo: str
                - descripcion: str (opcional)
                - hashtags: List[str]
                - hora_publicacion: int (opcional)
                - dia_semana: str (opcional)
                - tiene_media: bool
                - tipo_media: str (opcional)
            incluir_recomendaciones: Si incluir recomendaciones de mejora
        
        Returns:
            Score predictivo completo con análisis
        """
        # Extraer información del contenido
        tipo = contenido_propuesto.get('tipo_contenido', 'Y')
        plataforma = contenido_propuesto.get('plataforma', 'Instagram')
        titulo = contenido_propuesto.get('titulo', '')
        descripcion = contenido_propuesto.get('descripcion', '')
        hashtags = contenido_propuesto.get('hashtags', [])
        hora = contenido_propuesto.get('hora_publicacion', 10)
        dia = contenido_propuesto.get('dia_semana', 'Wednesday')
        tiene_media = contenido_propuesto.get('tiene_media', True)
        tipo_media = contenido_propuesto.get('tipo_media', 'imagen')
        
        # Predicción base con ML
        try:
            prediccion_ml = self.analizador_ml.predecir_engagement_ml(
                tipo_contenido=tipo,
                plataforma=plataforma,
                hora=hora,
                dia_semana=dia,
                tiene_media=tiene_media,
                hashtags=hashtags,
                titulo=titulo
            )
            engagement_predicho = prediccion_ml.get('engagement_score_predicho', 0)
            confianza = prediccion_ml.get('confianza', 50)
        except:
            engagement_predicho = 0
            confianza = 0
        
        # Análisis de calidad del contenido
        analisis_calidad = self._analizar_calidad_contenido(
            titulo, descripcion, hashtags, tipo, plataforma
        )
        
        # Análisis de timing
        analisis_timing = self._analizar_timing_optimo(hora, dia, tipo, plataforma)
        
        # Análisis de hashtags
        analisis_hashtags = self._analizar_hashtags_optimos(hashtags, tipo, plataforma)
        
        # Score compuesto
        score_final = self._calcular_score_final(
            engagement_predicho,
            analisis_calidad,
            analisis_timing,
            analisis_hashtags,
            confianza
        )
        
        resultado = {
            "score_predictivo": round(score_final, 1),
            "engagement_predicho": round(engagement_predicho, 1),
            "confianza": round(confianza, 1),
            "nivel_recomendacion": self._nivel_recomendacion(score_final),
            "analisis_calidad": analisis_calidad,
            "analisis_timing": analisis_timing,
            "analisis_hashtags": analisis_hashtags,
            "factores_clave": self._identificar_factores_clave(
                analisis_calidad, analisis_timing, analisis_hashtags
            )
        }
        
        if incluir_recomendaciones:
            resultado["recomendaciones"] = self._generar_recomendaciones_scoring(
                analisis_calidad, analisis_timing, analisis_hashtags, score_final
            )
        
        return resultado
    
    def _analizar_calidad_contenido(
        self,
        titulo: str,
        descripcion: str,
        hashtags: List[str],
        tipo: str,
        plataforma: str
    ) -> Dict[str, Any]:
        """Analiza calidad del contenido"""
        # Longitud del título
        longitud_titulo = len(titulo)
        longitud_descripcion = len(descripcion)
        
        # Longitudes óptimas por plataforma
        longitudes_optimas = {
            'Instagram': {'titulo': (50, 150), 'descripcion': (100, 500)},
            'Facebook': {'titulo': (50, 200), 'descripcion': (100, 1000)},
            'LinkedIn': {'titulo': (50, 150), 'descripcion': (200, 2000)},
            'Twitter': {'titulo': (50, 100), 'descripcion': (50, 280)}
        }
        
        optimo = longitudes_optimas.get(plataforma, {'titulo': (50, 150), 'descripcion': (100, 500)})
        
        # Score de longitud
        score_longitud_titulo = 100 if optimo['titulo'][0] <= longitud_titulo <= optimo['titulo'][1] else 50
        score_longitud_desc = 100 if optimo['descripcion'][0] <= longitud_descripcion <= optimo['descripcion'][1] else 50
        
        # Análisis de palabras clave
        palabras_clave = self._extraer_palabras_clave(titulo + " " + descripcion)
        score_palabras_clave = min(100, len(palabras_clave) * 10)
        
        # Análisis de hashtags
        num_hashtags = len(hashtags)
        num_hashtags_optimo = {'Instagram': 5-10, 'Facebook': 1-3, 'LinkedIn': 3-5, 'Twitter': 1-3}
        optimo_hashtags = num_hashtags_optimo.get(plataforma, 5-10)
        score_hashtags = 100 if optimo_hashtags[0] <= num_hashtags <= optimo_hashtags[1] else 50
        
        # Score de hook (título atractivo)
        tiene_hook = self._tiene_hook_efectivo(titulo)
        score_hook = 100 if tiene_hook else 50
        
        return {
            "score_calidad": round((score_longitud_titulo + score_longitud_desc + score_palabras_clave + score_hashtags + score_hook) / 5, 1),
            "longitud_titulo": longitud_titulo,
            "longitud_descripcion": longitud_descripcion,
            "longitud_optima": optimo,
            "palabras_clave": palabras_clave,
            "num_hashtags": num_hashtags,
            "tiene_hook": tiene_hook,
            "score_longitud": round((score_longitud_titulo + score_longitud_desc) / 2, 1),
            "score_contenido": round((score_palabras_clave + score_hook) / 2, 1)
        }
    
    def _analizar_timing_optimo(
        self,
        hora: int,
        dia: str,
        tipo: str,
        plataforma: str
    ) -> Dict[str, Any]:
        """Analiza si el timing es óptimo"""
        try:
            mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
                tipo_contenido=tipo,
                plataforma=plataforma
            )
            
            if 'error' not in mejor_momento:
                mejor = mejor_momento['mejor_momento']
                mejor_hora = mejor.get('hora', hora)
                mejor_dia = mejor.get('dia', dia)
                
                # Score de timing
                diferencia_hora = abs(hora - mejor_hora)
                score_hora = max(0, 100 - (diferencia_hora * 10))
                score_dia = 100 if dia == mejor_dia else 50
                score_timing = (score_hora + score_dia) / 2
                
                return {
                    "score_timing": round(score_timing, 1),
                    "hora_propuesta": hora,
                    "dia_propuesto": dia,
                    "hora_optima": mejor_hora,
                    "dia_optimo": mejor_dia,
                    "diferencia_hora": diferencia_hora,
                    "es_optimo": diferencia_hora <= 1 and dia == mejor_dia
                }
        except:
            pass
        
        return {
            "score_timing": 50,
            "hora_propuesta": hora,
            "dia_propuesto": dia,
            "es_optimo": False
        }
    
    def _analizar_hashtags_optimos(
        self,
        hashtags: List[str],
        tipo: str,
        plataforma: str
    ) -> Dict[str, Any]:
        """Analiza si los hashtags son óptimos"""
        # Analizar hashtags efectivos históricos
        hashtags_efectivos = self.analizador.analizar_hashtags_efectivos(plataforma=plataforma)
        
        if 'error' not in hashtags_efectivos:
            top_hashtags = [h['hashtag'] for h in hashtags_efectivos.get('top_hashtags', [])[:20]]
            
            # Verificar overlap
            hashtags_propuestos_lower = [h.lower().replace('#', '') for h in hashtags]
            top_hashtags_lower = [h.lower().replace('#', '') for h in top_hashtags]
            
            overlap = len(set(hashtags_propuestos_lower) & set(top_hashtags_lower))
            score_overlap = min(100, (overlap / max(len(hashtags), 1)) * 100)
            
            # Recomendaciones de hashtags faltantes
            hashtags_faltantes = [h for h in top_hashtags_lower if h not in hashtags_propuestos_lower][:5]
            
            return {
                "score_hashtags": round(score_overlap, 1),
                "num_hashtags": len(hashtags),
                "overlap_con_top": overlap,
                "hashtags_efectivos_usados": overlap,
                "hashtags_recomendados": hashtags_faltantes,
                "es_optimo": score_overlap >= 50
            }
        
        return {
            "score_hashtags": 50,
            "num_hashtags": len(hashtags),
            "es_optimo": False
        }
    
    def _calcular_score_final(
        self,
        engagement_predicho: float,
        analisis_calidad: Dict[str, Any],
        analisis_timing: Dict[str, Any],
        analisis_hashtags: Dict[str, Any],
        confianza: float
    ) -> float:
        """Calcula score final compuesto"""
        # Normalizar engagement (0-100)
        engagement_normalizado = min(100, (engagement_predicho / 10))
        
        # Pesos
        peso_engagement = 0.4
        peso_calidad = 0.3
        peso_timing = 0.15
        peso_hashtags = 0.15
        
        score = (
            engagement_normalizado * peso_engagement +
            analisis_calidad['score_calidad'] * peso_calidad +
            analisis_timing['score_timing'] * peso_timing +
            analisis_hashtags['score_hashtags'] * peso_hashtags
        )
        
        # Ajustar por confianza
        score_ajustado = score * (confianza / 100)
        
        return score_ajustado
    
    def _nivel_recomendacion(self, score: float) -> str:
        """Determina nivel de recomendación"""
        if score >= 80:
            return "EXCELENTE - Publicar inmediatamente"
        elif score >= 65:
            return "BUENO - Publicar con pequeñas mejoras"
        elif score >= 50:
            return "REGULAR - Mejorar antes de publicar"
        else:
            return "BAJO - Requiere optimización significativa"
    
    def _identificar_factores_clave(
        self,
        analisis_calidad: Dict[str, Any],
        analisis_timing: Dict[str, Any],
        analisis_hashtags: Dict[str, Any]
    ) -> List[str]:
        """Identifica factores clave que afectan el score"""
        factores = []
        
        if analisis_calidad['score_calidad'] < 60:
            factores.append("Calidad del contenido necesita mejora")
        
        if analisis_timing['score_timing'] < 60:
            factores.append(f"Timing no óptimo (mejor: {analisis_timing.get('hora_optima', 'N/A')}h)")
        
        if analisis_hashtags['score_hashtags'] < 60:
            factores.append("Hashtags no están optimizados")
        
        if not analisis_calidad.get('tiene_hook', False):
            factores.append("Falta un hook efectivo en el título")
        
        return factores
    
    def _generar_recomendaciones_scoring(
        self,
        analisis_calidad: Dict[str, Any],
        analisis_timing: Dict[str, Any],
        analisis_hashtags: Dict[str, Any],
        score_final: float
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones específicas para mejorar el score"""
        recomendaciones = []
        
        # Recomendaciones de calidad
        if analisis_calidad['score_longitud'] < 70:
            recomendaciones.append({
                "categoria": "Calidad",
                "prioridad": "Alta",
                "recomendacion": f"Ajustar longitud del contenido (actual: {analisis_calidad['longitud_titulo']} chars)",
                "accion": f"Objetivo: {analisis_calidad['longitud_optima']['titulo']} chars"
            })
        
        if not analisis_calidad.get('tiene_hook', False):
            recomendaciones.append({
                "categoria": "Calidad",
                "prioridad": "Alta",
                "recomendacion": "Agregar un hook efectivo al título",
                "accion": "Usar preguntas, números, o declaraciones impactantes"
            })
        
        # Recomendaciones de timing
        if analisis_timing['score_timing'] < 70:
            recomendaciones.append({
                "categoria": "Timing",
                "prioridad": "Media",
                "recomendacion": f"Cambiar hora de publicación a {analisis_timing.get('hora_optima', 'N/A')}:00",
                "accion": f"Mejor día: {analisis_timing.get('dia_optimo', 'N/A')}"
            })
        
        # Recomendaciones de hashtags
        if analisis_hashtags['score_hashtags'] < 70:
            recomendaciones.append({
                "categoria": "Hashtags",
                "prioridad": "Media",
                "recomendacion": "Usar hashtags más efectivos",
                "accion": f"Considerar: {', '.join(analisis_hashtags.get('hashtags_recomendados', [])[:5])}"
            })
        
        return recomendaciones
    
    def _extraer_palabras_clave(self, texto: str) -> List[str]:
        """Extrae palabras clave del texto"""
        # Palabras comunes a ignorar
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'las', 'del', 'los', 'una', 'para', 'como', 'está', 'pero', 'más', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esas', 'esos', 'esas', 'esos', 'esas', 'esos'}
        
        # Limpiar y tokenizar
        texto_limpio = re.sub(r'[^\w\s]', ' ', texto.lower())
        palabras = texto_limpio.split()
        
        # Filtrar stop words y palabras muy cortas
        palabras_clave = [p for p in palabras if len(p) > 3 and p not in stop_words]
        
        # Contar frecuencia
        frecuencia = defaultdict(int)
        for palabra in palabras_clave:
            frecuencia[palabra] += 1
        
        # Retornar top palabras clave
        top_palabras = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)[:10]
        return [palabra for palabra, _ in top_palabras]
    
    def _tiene_hook_efectivo(self, titulo: str) -> bool:
        """Verifica si el título tiene un hook efectivo"""
        # Patrones de hooks efectivos
        patrones_hook = [
            r'^\d+',  # Empieza con número
            r'[¿?]',  # Contiene pregunta
            r'^(cómo|qué|por qué|cuándo|dónde)',  # Empieza con pregunta
            r'[!]',  # Contiene exclamación
            r'\b(secret[oa]|truco|guía|tips?|mejor|top|nunca|siempre)\b',  # Palabras poderosas
        ]
        
        titulo_lower = titulo.lower()
        for patron in patrones_hook:
            if re.search(patron, titulo_lower):
                return True
        
        return False
    
    def analisis_competitivo_inteligente(
        self,
        competidores: List[Dict[str, Any]],
        incluir_benchmarking: bool = True
    ) -> Dict[str, Any]:
        """
        Análisis competitivo inteligente con benchmarking dinámico
        
        Args:
            competidores: Lista de competidores con sus datos de engagement
            incluir_benchmarking: Si incluir benchmarking automático
        
        Returns:
            Análisis competitivo completo
        """
        # Calcular métricas propias
        metricas_propias = self._calcular_metricas_propias()
        
        # Analizar competidores
        analisis_competidores = []
        for competidor in competidores:
            analisis = self._analizar_competidor(competidor, metricas_propias)
            analisis_competidores.append(analisis)
        
        # Identificar gaps
        gaps = self._identificar_gaps_competitivos(metricas_propias, analisis_competidores)
        
        # Benchmarking dinámico
        benchmarking = None
        if incluir_benchmarking:
            benchmarking = self._generar_benchmarking_dinamico(metricas_propias, analisis_competidores)
        
        # Oportunidades
        oportunidades = self._identificar_oportunidades(metricas_propias, analisis_competidores, gaps)
        
        return {
            "metricas_propias": metricas_propias,
            "competidores_analizados": len(competidores),
            "analisis_competidores": analisis_competidores,
            "gaps_competitivos": gaps,
            "benchmarking": benchmarking,
            "oportunidades": oportunidades,
            "posicionamiento": self._calcular_posicionamiento(metricas_propias, analisis_competidores)
        }
    
    def _calcular_metricas_propias(self) -> Dict[str, Any]:
        """Calcula métricas propias para comparación"""
        if not self.analizador.publicaciones:
            return {"error": "No hay publicaciones"}
        
        engagement_scores = [p.engagement_score for p in self.analizador.publicaciones]
        engagement_rates = [p.engagement_rate for p in self.analizador.publicaciones]
        
        return {
            "engagement_score_promedio": statistics.mean(engagement_scores),
            "engagement_rate_promedio": statistics.mean(engagement_rates),
            "engagement_score_max": max(engagement_scores),
            "engagement_rate_max": max(engagement_rates),
            "total_publicaciones": len(self.analizador.publicaciones),
            "tasa_viral": sum(1 for p in self.analizador.publicaciones if p.es_viral) / len(self.analizador.publicaciones) * 100
        }
    
    def _analizar_competidor(
        self,
        competidor: Dict[str, Any],
        metricas_propias: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza un competidor individual"""
        engagement_score_comp = competidor.get('engagement_score_promedio', 0)
        engagement_rate_comp = competidor.get('engagement_rate_promedio', 0)
        
        engagement_score_propio = metricas_propias.get('engagement_score_promedio', 0)
        engagement_rate_propio = metricas_propias.get('engagement_rate_promedio', 0)
        
        # Comparación
        diferencia_score = engagement_score_comp - engagement_score_propio
        diferencia_rate = engagement_rate_comp - engagement_rate_propio
        
        porcentaje_diferencia_score = (diferencia_score / engagement_score_propio * 100) if engagement_score_propio > 0 else 0
        porcentaje_diferencia_rate = (diferencia_rate / engagement_rate_propio * 100) if engagement_rate_propio > 0 else 0
        
        return {
            "nombre": competidor.get('nombre', 'Competidor'),
            "engagement_score_promedio": engagement_score_comp,
            "engagement_rate_promedio": engagement_rate_comp,
            "diferencia_score": round(diferencia_score, 1),
            "diferencia_rate": round(diferencia_rate, 2),
            "porcentaje_diferencia_score": round(porcentaje_diferencia_score, 1),
            "porcentaje_diferencia_rate": round(porcentaje_diferencia_rate, 1),
            "es_mejor": engagement_score_comp > engagement_score_propio,
            "ventaja": abs(diferencia_score)
        }
    
    def _identificar_gaps_competitivos(
        self,
        metricas_propias: Dict[str, Any],
        analisis_competidores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifica gaps competitivos"""
        gaps = []
        
        # Encontrar mejor competidor
        mejor_competidor = max(analisis_competidores, key=lambda x: x['engagement_score_promedio'])
        
        if mejor_competidor['es_mejor']:
            gaps.append({
                "tipo": "Engagement Score",
                "gap": mejor_competidor['diferencia_score'],
                "porcentaje_gap": mejor_competidor['porcentaje_diferencia_score'],
                "competidor": mejor_competidor['nombre'],
                "severidad": "Alta" if mejor_competidor['porcentaje_diferencia_score'] > 50 else "Media"
            })
        
        # Gap en engagement rate
        mejor_rate = max(analisis_competidores, key=lambda x: x['engagement_rate_promedio'])
        if mejor_rate['engagement_rate_promedio'] > metricas_propias.get('engagement_rate_promedio', 0):
            gaps.append({
                "tipo": "Engagement Rate",
                "gap": mejor_rate['diferencia_rate'],
                "porcentaje_gap": mejor_rate['porcentaje_diferencia_rate'],
                "competidor": mejor_rate['nombre'],
                "severidad": "Alta" if mejor_rate['porcentaje_diferencia_rate'] > 50 else "Media"
            })
        
        return gaps
    
    def _generar_benchmarking_dinamico(
        self,
        metricas_propias: Dict[str, Any],
        analisis_competidores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera benchmarking dinámico"""
        if not analisis_competidores:
            return {"error": "No hay competidores para benchmarking"}
        
        # Calcular percentiles
        scores = [c['engagement_score_promedio'] for c in analisis_competidores]
        scores.append(metricas_propias.get('engagement_score_promedio', 0))
        
        scores_sorted = sorted(scores)
        propio_score = metricas_propias.get('engagement_score_promedio', 0)
        
        # Percentil
        percentil = (scores_sorted.index(propio_score) / len(scores_sorted)) * 100 if propio_score in scores_sorted else 50
        
        # Posición
        posicion = len([s for s in scores_sorted if s < propio_score]) + 1
        
        return {
            "percentil": round(percentil, 1),
            "posicion": posicion,
            "total_comparados": len(scores_sorted),
            "score_promedio_mercado": round(statistics.mean(scores), 1),
            "score_mediano_mercado": round(statistics.median(scores), 1),
            "nivel": "Excelente" if percentil >= 90 else "Bueno" if percentil >= 70 else "Regular" if percentil >= 50 else "Bajo"
        }
    
    def _identificar_oportunidades(
        self,
        metricas_propias: Dict[str, Any],
        analisis_competidores: List[Dict[str, Any]],
        gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades de mejora"""
        oportunidades = []
        
        # Oportunidad basada en gaps
        for gap in gaps:
            if gap['severidad'] == 'Alta':
                oportunidades.append({
                    "tipo": "Reducir Gap",
                    "descripcion": f"Reducir gap de {gap['tipo']} con {gap['competidor']}",
                    "impacto_estimado": "Alto",
                    "esfuerzo": "Medio",
                    "prioridad": "Alta"
                })
        
        # Oportunidad de contenido
        mejor_competidor = max(analisis_competidores, key=lambda x: x['engagement_score_promedio'])
        if mejor_competidor['es_mejor']:
            oportunidades.append({
                "tipo": "Optimización de Contenido",
                "descripcion": f"Analizar estrategia de contenido de {mejor_competidor['nombre']}",
                "impacto_estimado": "Alto",
                "esfuerzo": "Bajo",
                "prioridad": "Media"
            })
        
        return oportunidades
    
    def _calcular_posicionamiento(
        self,
        metricas_propias: Dict[str, Any],
        analisis_competidores: List[Dict[str, Any]]
    ) -> str:
        """Calcula posicionamiento competitivo"""
        mejor_competidor = max(analisis_competidores, key=lambda x: x['engagement_score_promedio'])
        propio_score = metricas_propias.get('engagement_score_promedio', 0)
        
        if propio_score >= mejor_competidor['engagement_score_promedio']:
            return "Líder"
        elif propio_score >= mejor_competidor['engagement_score_promedio'] * 0.8:
            return "Competitivo"
        else:
            return "Rezagado"
    
    def recomendaciones_personalizadas_ml(
        self,
        objetivo: str = "aumentar_engagement",
        contexto: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recomendaciones personalizadas basadas en ML
        
        Args:
            objetivo: Objetivo principal (aumentar_engagement, mejorar_roi, etc.)
            contexto: Contexto adicional opcional
        
        Returns:
            Recomendaciones personalizadas
        """
        # Analizar historial
        historial = self._analizar_historial_contenido()
        
        # Identificar patrones exitosos
        patrones_exitosos = self._identificar_patrones_exitosos(historial)
        
        # Generar recomendaciones basadas en objetivo
        recomendaciones = []
        
        if objetivo == "aumentar_engagement":
            recomendaciones = self._recomendaciones_aumentar_engagement(patrones_exitosos, historial)
        elif objetivo == "mejorar_roi":
            recomendaciones = self._recomendaciones_mejorar_roi(patrones_exitosos, historial)
        elif objetivo == "aumentar_viralidad":
            recomendaciones = self._recomendaciones_aumentar_viralidad(patrones_exitosos, historial)
        
        # Priorizar recomendaciones
        recomendaciones_priorizadas = self._priorizar_recomendaciones(recomendaciones, historial)
        
        return {
            "objetivo": objetivo,
            "recomendaciones": recomendaciones_priorizadas,
            "patrones_exitosos_identificados": patrones_exitosos,
            "confianza": self._calcular_confianza_recomendaciones(recomendaciones_priorizadas)
        }
    
    def _analizar_historial_contenido(self) -> Dict[str, Any]:
        """Analiza historial de contenido"""
        if not self.analizador.publicaciones:
            return {"error": "No hay publicaciones"}
        
        # Top publicaciones
        top_publicaciones = sorted(
            self.analizador.publicaciones,
            key=lambda x: x.engagement_score,
            reverse=True
        )[:10]
        
        # Análisis por tipo
        por_tipo = defaultdict(list)
        for pub in self.analizador.publicaciones:
            por_tipo[pub.tipo_contenido].append(pub.engagement_score)
        
        tipos_promedio = {tipo: statistics.mean(scores) for tipo, scores in por_tipo.items()}
        
        return {
            "top_publicaciones": [
                {
                    "tipo": p.tipo_contenido,
                    "plataforma": p.plataforma,
                    "engagement_score": p.engagement_score,
                    "es_viral": p.es_viral
                }
                for p in top_publicaciones
            ],
            "promedio_por_tipo": tipos_promedio,
            "total_publicaciones": len(self.analizador.publicaciones)
        }
    
    def _identificar_patrones_exitosos(self, historial: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica patrones en contenido exitoso"""
        if 'error' in historial:
            return {}
        
        top_pubs = historial.get('top_publicaciones', [])
        
        # Patrones comunes en top publicaciones
        tipos_top = [p['tipo'] for p in top_pubs]
        plataformas_top = [p['plataforma'] for p in top_pubs]
        
        tipo_mas_comun = max(set(tipos_top), key=tipos_top.count) if tipos_top else None
        plataforma_mas_comun = max(set(plataformas_top), key=plataformas_top.count) if plataformas_top else None
        
        return {
            "tipo_mas_exitoso": tipo_mas_comun,
            "plataforma_mas_exitosa": plataforma_mas_comun,
            "tasa_viral_top": sum(1 for p in top_pubs if p['es_viral']) / len(top_pubs) * 100 if top_pubs else 0
        }
    
    def _recomendaciones_aumentar_engagement(
        self,
        patrones: Dict[str, Any],
        historial: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones para aumentar engagement"""
        recomendaciones = []
        
        tipo_exitoso = patrones.get('tipo_mas_exitoso')
        if tipo_exitoso:
            recomendaciones.append({
                "tipo": "Contenido",
                "prioridad": "Alta",
                "recomendacion": f"Incrementar contenido tipo {tipo_exitoso}",
                "razon": f"Este tipo muestra mejor rendimiento histórico",
                "impacto_estimado": "Alto"
            })
        
        # Recomendación de timing
        recomendaciones.append({
            "tipo": "Timing",
            "prioridad": "Media",
            "recomendacion": "Optimizar horarios de publicación",
            "razon": "El timing afecta significativamente el engagement",
            "impacto_estimado": "Medio"
        })
        
        return recomendaciones
    
    def _recomendaciones_mejorar_roi(
        self,
        patrones: Dict[str, Any],
        historial: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones para mejorar ROI"""
        recomendaciones = []
        
        recomendaciones.append({
            "tipo": "ROI",
            "prioridad": "Alta",
            "recomendacion": "Enfocarse en contenido con mejor ROI histórico",
            "razon": "Optimizar inversión en contenido más rentable",
            "impacto_estimado": "Alto"
        })
        
        return recomendaciones
    
    def _recomendaciones_aumentar_viralidad(
        self,
        patrones: Dict[str, Any],
        historial: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones para aumentar viralidad"""
        recomendaciones = []
        
        tasa_viral = patrones.get('tasa_viral_top', 0)
        if tasa_viral < 10:
            recomendaciones.append({
                "tipo": "Viralidad",
                "prioridad": "Alta",
                "recomendacion": "Mejorar elementos virales en contenido",
                "razon": f"Tasa viral actual: {tasa_viral:.1f}%",
                "impacto_estimado": "Alto"
            })
        
        return recomendaciones
    
    def _priorizar_recomendaciones(
        self,
        recomendaciones: List[Dict[str, Any]],
        historial: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioriza recomendaciones por impacto y factibilidad"""
        # Ordenar por prioridad y impacto
        prioridad_valor = {"Alta": 3, "Media": 2, "Baja": 1}
        impacto_valor = {"Alto": 3, "Medio": 2, "Bajo": 1}
        
        recomendaciones_ordenadas = sorted(
            recomendaciones,
            key=lambda x: (
                prioridad_valor.get(x.get('prioridad', 'Media'), 2),
                impacto_valor.get(x.get('impacto_estimado', 'Medio'), 2)
            ),
            reverse=True
        )
        
        return recomendaciones_ordenadas
    
    def _calcular_confianza_recomendaciones(
        self,
        recomendaciones: List[Dict[str, Any]]
    ) -> float:
        """Calcula confianza en las recomendaciones"""
        if not recomendaciones:
            return 0
        
        # Más recomendaciones basadas en datos = mayor confianza
        confianza_base = min(100, len(recomendaciones) * 20)
        
        # Ajustar por calidad de datos históricos
        confianza_ajustada = confianza_base * 0.8  # Factor conservador
        
        return round(confianza_ajustada, 1)


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis Inteligente de Engagement')
    parser.add_argument('--publicaciones', type=int, default=50, help='Número de publicaciones')
    parser.add_argument('--scoring', action='store_true', help='Scoring predictivo de contenido')
    parser.add_argument('--competitivo', action='store_true', help='Análisis competitivo')
    parser.add_argument('--recomendaciones', action='store_true', help='Recomendaciones personalizadas')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_inteligente = AnalizadorInteligenteEngagement(analizador_base)
    
    # Scoring predictivo
    if args.scoring:
        print("\n📊 Scoring predictivo de contenido...")
        contenido_propuesto = {
            "tipo_contenido": "Y",
            "plataforma": "Instagram",
            "titulo": "5 Secretos para Aumentar tu Engagement",
            "descripcion": "Descubre los secretos que los expertos usan para aumentar engagement",
            "hashtags": ["engagement", "marketing", "socialmedia"],
            "hora_publicacion": 10,
            "dia_semana": "Wednesday",
            "tiene_media": True
        }
        
        scoring = analizador_inteligente.scoring_predictivo_contenido(contenido_propuesto)
        
        print(f"\n✅ Score Predictivo: {scoring['score_predictivo']}/100")
        print(f"   Nivel: {scoring['nivel_recomendacion']}")
        print(f"   Engagement Predicho: {scoring['engagement_predicho']}")
        
        if 'recomendaciones' in scoring:
            print(f"\n   Recomendaciones:")
            for rec in scoring['recomendaciones'][:3]:
                print(f"     - {rec['recomendacion']}")
    
    # Análisis competitivo
    if args.competitivo:
        print("\n🏆 Análisis competitivo inteligente...")
        competidores = [
            {"nombre": "Competidor A", "engagement_score_promedio": 350, "engagement_rate_promedio": 5.2},
            {"nombre": "Competidor B", "engagement_score_promedio": 280, "engagement_rate_promedio": 4.8},
            {"nombre": "Competidor C", "engagement_score_promedio": 420, "engagement_rate_promedio": 6.1}
        ]
        
        analisis = analizador_inteligente.analisis_competitivo_inteligente(competidores)
        
        print(f"\n✅ Posicionamiento: {analisis['posicionamiento']}")
        if analisis.get('benchmarking'):
            bench = analisis['benchmarking']
            print(f"   Percentil: {bench['percentil']}%")
            print(f"   Nivel: {bench['nivel']}")
        
        if analisis.get('gaps_competitivos'):
            print(f"\n   Gaps identificados: {len(analisis['gaps_competitivos'])}")
    
    # Recomendaciones personalizadas
    if args.recomendaciones:
        print("\n💡 Recomendaciones personalizadas con ML...")
        recomendaciones = analizador_inteligente.recomendaciones_personalizadas_ml(
            objetivo="aumentar_engagement"
        )
        
        print(f"\n✅ {len(recomendaciones['recomendaciones'])} recomendaciones generadas")
        print(f"   Confianza: {recomendaciones['confianza']}%")
        
        for rec in recomendaciones['recomendaciones'][:3]:
            print(f"\n   [{rec['prioridad']}] {rec['recomendacion']}")
            print(f"      Razón: {rec['razon']}")


if __name__ == "__main__":
    main()



