#!/usr/bin/env python3
"""
Análisis Avanzado V2 de Engagement - Mejoras Premium Extendidas
================================================================
Funcionalidades avanzadas extendidas:
- Sistema de alertas predictivas inteligentes
- Análisis de ROI predictivo avanzado
- Sistema de A/B testing automatizado
- Análisis de sentimiento avanzado con NLP
- Detección automática de oportunidades de contenido
- Análisis cross-platform avanzado
- Sistema de scoring de contenido en tiempo real
- Análisis de tendencias de mercado
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
    from analisis_engagement_inteligente import AnalizadorInteligenteEngagement
    from analisis_engagement_roi import AnalizadorROIEngagement
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorAvanzadoV2Engagement:
    """Analizador avanzado V2 de engagement con funcionalidades extendidas"""
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        analizador_ml: Optional[AnalizadorEngagementML] = None,
        analizador_predictivo: Optional[AnalizadorPredictivoEngagement] = None,
        analizador_inteligente: Optional[AnalizadorInteligenteEngagement] = None,
        analizador_roi: Optional[AnalizadorROIEngagement] = None
    ):
        """
        Inicializa el analizador avanzado V2
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            analizador_ml: Instancia opcional del AnalizadorEngagementML
            analizador_predictivo: Instancia opcional del AnalizadorPredictivoEngagement
            analizador_inteligente: Instancia opcional del AnalizadorInteligenteEngagement
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
        self.analizador_inteligente = analizador_inteligente or AnalizadorInteligenteEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado, self.analizador_ml,
            self.analizador_predictivo
        )
        self.analizador_roi = analizador_roi or AnalizadorROIEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
        # Historial de alertas
        self.historial_alertas = []
    def sistema_alertas_predictivas(
        self,
        umbrales: Optional[Dict[str, float]] = None,
        ventana_dias: int = 7
    ) -> Dict[str, Any]:
        """
        Sistema de alertas predictivas inteligentes
        Args:
            umbrales: Umbrales personalizados para alertas
            ventana_dias: Ventana de días para análisis
        Returns:
            Alertas predictivas generadas
        """
        if umbrales is None:
            umbrales = {
                "engagement_decreciente": -20,  # % de cambio
                "engagement_bajo": 100,  # score mínimo
                "tasa_viral_baja": 5,  # % mínimo
                "roi_decreciente": -15,  # % de cambio
                "competencia_avanzando": 10  # % de diferencia
            }
        alertas = []
        # 1. Alerta: Engagement decreciente
        alerta_engagement = self._detectar_engagement_decreciente(umbrales, ventana_dias)
        if alerta_engagement:
            alertas.append(alerta_engagement)
        # 2. Alerta: Engagement bajo
        alerta_bajo = self._detectar_engagement_bajo(umbrales)
        if alerta_bajo:
            alertas.append(alerta_bajo)
        # 3. Alerta: Tasa viral baja
        alerta_viral = self._detectar_tasa_viral_baja(umbrales)
        if alerta_viral:
            alertas.append(alerta_viral)
        # 4. Alerta: ROI decreciente
        alerta_roi = self._detectar_roi_decreciente(umbrales, ventana_dias)
        if alerta_roi:
            alertas.append(alerta_roi)
        # 5. Alerta: Oportunidades detectadas
        alerta_oportunidades = self._detectar_oportunidades_perdidas()
        if alerta_oportunidades:
            alertas.append(alerta_oportunidades)
        # Priorizar alertas
        alertas_priorizadas = sorted(alertas, key=lambda x: self._prioridad_alerta(x), reverse=True)
        # Guardar en historial
        self.historial_alertas.extend(alertas_priorizadas)
        return {
            "total_alertas": len(alertas_priorizadas),
            "alertas": alertas_priorizadas,
            "alertas_criticas": [a for a in alertas_priorizadas if a.get('severidad') == 'CRITICA'],
            "alertas_altas": [a for a in alertas_priorizadas if a.get('severidad') == 'ALTA'],
            "fecha_analisis": datetime.now().isoformat()
        }
    def _detectar_engagement_decreciente(
        self,
        umbrales: Dict[str, float],
        ventana_dias: int
    ) -> Optional[Dict[str, Any]]:
        """Detecta si el engagement está decreciendo"""
        if len(self.analizador.publicaciones) < 10:
            return None
        # Comparar últimas dos semanas
        fecha_limite = datetime.now() - timedelta(days=ventana_dias)
        publicaciones_recientes = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= fecha_limite
        ]
        if len(publicaciones_recientes) < 5:
            return None
        # Dividir en dos períodos
        mitad = len(publicaciones_recientes) // 2
        periodo_1 = publicaciones_recientes[:mitad]
        periodo_2 = publicaciones_recientes[mitad:]
        promedio_1 = statistics.mean([p.engagement_score for p in periodo_1])
        promedio_2 = statistics.mean([p.engagement_score for p in periodo_2])
        cambio_porcentual = ((promedio_2 - promedio_1) / promedio_1 * 100) if promedio_1 > 0 else 0
        if cambio_porcentual < umbrales.get('engagement_decreciente', -20):
            return {
                "tipo": "ENGAGEMENT_DECRECIENTE",
                "severidad": "ALTA",
                "titulo": "Engagement en tendencia decreciente",
                "descripcion": f"El engagement ha disminuido {abs(cambio_porcentual):.1f}% en los últimos {ventana_dias} días",
                "cambio_porcentual": round(cambio_porcentual, 1),
                "periodo_anterior": round(promedio_1, 1),
                "periodo_actual": round(promedio_2, 1),
                "accion_recomendada": "Revisar estrategia de contenido y timing"
            }
        return None
    def _detectar_engagement_bajo(self, umbrales: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Detecta si el engagement está por debajo del umbral"""
        if not self.analizador.publicaciones:
            return None
        engagement_promedio = statistics.mean([p.engagement_score for p in self.analizador.publicaciones])
        umbral = umbrales.get('engagement_bajo', 100)
        if engagement_promedio < umbral:
            return {
                "tipo": "ENGAGEMENT_BAJO",
                "severidad": "ALTA",
                "titulo": "Engagement por debajo del umbral",
                "descripcion": f"El engagement promedio ({engagement_promedio:.1f}) está por debajo del umbral ({umbral})",
                "engagement_actual": round(engagement_promedio, 1),
                "umbral": umbral,
                "diferencia": round(umbral - engagement_promedio, 1),
                "accion_recomendada": "Optimizar contenido y estrategia de publicación"
            }
        return None
    def _detectar_tasa_viral_baja(self, umbrales: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Detecta si la tasa viral es baja"""
        if not self.analizador.publicaciones:
            return None
        publicaciones_virales = sum(1 for p in self.analizador.publicaciones if p.es_viral)
        tasa_viral = (publicaciones_virales / len(self.analizador.publicaciones)) * 100
        umbral = umbrales.get('tasa_viral_baja', 5)
        if tasa_viral < umbral:
            return {
                "tipo": "TASA_VIRAL_BAJA",
                "severidad": "MEDIA",
                "titulo": "Tasa viral por debajo del objetivo",
                "descripcion": f"La tasa viral ({tasa_viral:.1f}%) está por debajo del objetivo ({umbral}%)",
                "tasa_viral_actual": round(tasa_viral, 1),
                "objetivo": umbral,
                "publicaciones_virales": publicaciones_virales,
                "accion_recomendada": "Mejorar elementos virales en contenido"
            }
        return None
    def _detectar_roi_decreciente(
        self,
        umbrales: Dict[str, float],
        ventana_dias: int
    ) -> Optional[Dict[str, Any]]:
        """Detecta si el ROI está decreciendo"""
        try:
            # Obtener análisis de ROI
            analisis_roi = self.analizador_roi.analizar_roi_detallado()
            if 'error' in analisis_roi:
                return None
            # Comparar ROI por período (simplificado)
            roi_actual = analisis_roi.get('roi_promedio', 0)
            # Si ROI es negativo o muy bajo
            if roi_actual < 0:
                return {
                    "tipo": "ROI_NEGATIVO",
                    "severidad": "CRITICA",
                    "titulo": "ROI negativo detectado",
                    "descripcion": f"El ROI actual ({roi_actual:.1f}%) es negativo",
                    "roi_actual": round(roi_actual, 1),
                    "accion_recomendada": "Revisar urgentemente estrategia de inversión en contenido"
                }
        except:
            pass
        return None
    def _detectar_oportunidades_perdidas(self) -> Optional[Dict[str, Any]]:
        """Detecta oportunidades perdidas"""
        try:
            # Analizar mejor momento vs momento actual
            mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
                tipo_contenido='Y',
                plataforma='Instagram'
            )
            if 'error' not in mejor_momento:
                # Verificar si estamos usando el mejor momento
                publicaciones_recientes = [
                    p for p in self.analizador.publicaciones
                    if p.fecha_publicacion >= datetime.now() - timedelta(days=7)
                ]
                mejor_hora = mejor_momento['mejor_momento'].get('hora', 10)
                mejor_dia = mejor_momento['mejor_momento'].get('dia', 'Wednesday')
                publicaciones_optimas = [
                    p for p in publicaciones_recientes
                    if p.metadata.get('hora_publicacion', p.fecha_publicacion.hour) == mejor_hora and
                    p.metadata.get('dia_semana', p.fecha_publicacion.strftime('%A')) == mejor_dia
                ]
                tasa_optimizacion = (len(publicaciones_optimas) / len(publicaciones_recientes) * 100) if publicaciones_recientes else 0
                if tasa_optimizacion < 50:
                    return {
                        "tipo": "OPORTUNIDAD_TIMING",
                        "severidad": "MEDIA",
                        "titulo": "Oportunidad de optimizar timing",
                        "descripcion": f"Solo {tasa_optimizacion:.1f}% de publicaciones usan el timing óptimo",
                        "tasa_optimizacion": round(tasa_optimizacion, 1),
                        "mejor_hora": mejor_hora,
                        "mejor_dia": mejor_dia,
                        "accion_recomendada": f"Publicar más contenido a las {mejor_hora}:00 los {mejor_dia}"
                    }
        except:
            pass
        return None
    def _prioridad_alerta(self, alerta: Dict[str, Any]) -> int:
        """Calcula prioridad de alerta"""
        severidad_valor = {"CRITICA": 4, "ALTA": 3, "MEDIA": 2, "BAJA": 1}
        return severidad_valor.get(alerta.get('severidad', 'BAJA'), 1)
    def analisis_roi_predictivo_avanzado(
        self,
        escenarios_futuros: List[Dict[str, Any]] = None,
        meses_proyeccion: int = 6
    ) -> Dict[str, Any]:
        """
        Análisis de ROI predictivo avanzado
        Args:
            escenarios_futuros: Escenarios futuros a analizar
            meses_proyeccion: Meses a proyectar
        Returns:
            Análisis de ROI predictivo completo
        """
        # Obtener ROI actual
        roi_actual = self.analizador_roi.analizar_roi_detallado()
        # Proyección de tendencias
        tendencias = self.analizador_predictivo.predecir_tendencias_futuras(
            semanas_futuras=meses_proyeccion * 4
        )
        # Calcular ROI proyectado
        proyecciones_roi = []
        if 'error' not in tendencias and 'predicciones' in tendencias:
            for pred in tendencias['predicciones']:
                # Estimar ROI basado en engagement predicho
                engagement_predicho = pred.get('engagement_score_predicho', 0)
                roi_estimado = self._estimar_roi_desde_engagement(engagement_predicho)
                proyecciones_roi.append({
                    "mes": pred.get('semana', 0) // 4 + 1,
                    "semana": pred.get('semana', 0),
                    "fecha": pred.get('fecha', ''),
                    "engagement_predicho": engagement_predicho,
                    "roi_predicho": roi_estimado
                })
        # Análisis de escenarios
        analisis_escenarios = None
        if escenarios_futuros:
            analisis_escenarios = self.analizador_predictivo.analizar_escenarios_what_if(escenarios_futuros)
        # Recomendaciones de inversión
        recomendaciones_inversion = self._generar_recomendaciones_inversion(roi_actual, proyecciones_roi)
        return {
            "roi_actual": roi_actual,
            "proyecciones_roi": proyecciones_roi,
            "roi_promedio_proyectado": statistics.mean([p['roi_predicho'] for p in proyecciones_roi]) if proyecciones_roi else 0,
            "tendencia_roi": self._calcular_tendencia_roi(proyecciones_roi),
            "escenarios": analisis_escenarios,
            "recomendaciones_inversion": recomendaciones_inversion,
            "break_even_proyectado": self._calcular_break_even_proyectado(proyecciones_roi)
        }
    def _estimar_roi_desde_engagement(self, engagement_score: float) -> float:
        """Estima ROI desde engagement score"""
        # Relación simplificada: ROI = (engagement_score / 10) - 5
        # Ajustar según datos históricos
        roi_estimado = (engagement_score / 10) - 5
        return round(roi_estimado, 1)
    def _calcular_tendencia_roi(self, proyecciones: List[Dict[str, Any]]) -> str:
        """Calcula tendencia de ROI"""
        if len(proyecciones) < 2:
            return "Estable"
        roi_inicial = proyecciones[0]['roi_predicho']
        roi_final = proyecciones[-1]['roi_predicho']
        cambio = roi_final - roi_inicial
        if cambio > 5:
            return "Creciente"
        elif cambio < -5:
            return "Decreciente"
        else:
            return "Estable"
    def _generar_recomendaciones_inversion(
        self,
        roi_actual: Dict[str, Any],
        proyecciones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones de inversión"""
        recomendaciones = []
        roi_promedio_actual = roi_actual.get('roi_promedio', 0) if isinstance(roi_actual, dict) else 0
        roi_promedio_proyectado = statistics.mean([p['roi_predicho'] for p in proyecciones]) if proyecciones else 0
        if roi_promedio_proyectado > roi_promedio_actual:
            recomendaciones.append({
                "tipo": "AUMENTAR_INVERSION",
                "prioridad": "Alta",
                "descripcion": f"ROI proyectado ({roi_promedio_proyectado:.1f}%) es mejor que actual ({roi_promedio_actual:.1f}%)",
                "accion": "Considerar aumentar inversión en contenido"
            })
        elif roi_promedio_proyectado < roi_promedio_actual:
            recomendaciones.append({
                "tipo": "OPTIMIZAR_INVERSION",
                "prioridad": "Media",
                "descripcion": f"ROI proyectado ({roi_promedio_proyectado:.1f}%) es menor que actual",
                "accion": "Optimizar estrategia antes de aumentar inversión"
            })
        return recomendaciones
    def _calcular_break_even_proyectado(
        self,
        proyecciones: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Calcula break-even proyectado"""
        if not proyecciones:
            return None
        # Encontrar primer mes con ROI positivo
        for proy in proyecciones:
            if proy['roi_predicho'] > 0:
                return {
                    "mes": proy['mes'],
                    "semana": proy['semana'],
                    "fecha": proy['fecha'],
                    "roi_en_break_even": proy['roi_predicho']
                }
        return None
    def sistema_ab_testing_automatizado(
        self,
        variantes: List[Dict[str, Any]],
        duracion_dias: int = 7,
        tamano_muestra_minimo: int = 100
    ) -> Dict[str, Any]:
        """
        Sistema de A/B testing automatizado
        Args:
            variantes: Lista de variantes a testear
            duracion_dias: Duración del test en días
            tamano_muestra_minimo: Tamaño mínimo de muestra
        Returns:
            Resultados del A/B test
        """
        if len(variantes) < 2:
            return {"error": "Se necesitan al menos 2 variantes"}
        # Simular resultados del test (en producción, esto vendría de datos reales)
        resultados_variantes = []
        for i, variante in enumerate(variantes):
            # Simular engagement para cada variante
            engagement_simulado = self._simular_engagement_variante(variante)
            resultados_variantes.append({
                "variante": variante.get('nombre', f'Variante {i+1}'),
                "configuracion": variante,
                "engagement_promedio": engagement_simulado,
                "muestra": tamano_muestra_minimo,
                "confianza": 95  # Simulado
            })
        # Encontrar ganador
        ganador = max(resultados_variantes, key=lambda x: x['engagement_promedio'])
        # Calcular significancia estadística (simplificado)
        significancia = self._calcular_significancia_ab_test(resultados_variantes)
        # Recomendación
        recomendacion = self._generar_recomendacion_ab_test(ganador, resultados_variantes, significancia)
        return {
            "test_completado": True,
            "duracion_dias": duracion_dias,
            "variantes_testeadas": len(variantes),
            "resultados": resultados_variantes,
            "ganador": ganador,
            "significancia_estadistica": significancia,
            "recomendacion": recomendacion
        }
    def _simular_engagement_variante(self, variante: Dict[str, Any]) -> float:
        """Simula engagement para una variante"""
        # Usar predicción ML si está disponible
        try:
            prediccion = self.analizador_ml.predecir_engagement_ml(
                tipo_contenido=variante.get('tipo_contenido', 'Y'),
                plataforma=variante.get('plataforma', 'Instagram'),
                hora=variante.get('hora', 10),
                dia_semana=variante.get('dia_semana', 'Wednesday'),
                tiene_media=variante.get('tiene_media', True),
                hashtags=variante.get('hashtags', []),
                titulo=variante.get('titulo', '')
            )
            return prediccion.get('engagement_score_predicho', 0)
        except:
            # Fallback: simulación simple
            return 200 + (hash(str(variante)) % 200)
    def _calcular_significancia_ab_test(
        self,
        resultados: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula significancia estadística del A/B test"""
        if len(resultados) < 2:
            return {"significativo": False, "confianza": 0}
        # Simplificado: comparar diferencias
        engagement_values = [r['engagement_promedio'] for r in resultados]
        max_engagement = max(engagement_values)
        min_engagement = min(engagement_values)
        diferencia = max_engagement - min_engagement
        diferencia_porcentual = (diferencia / min_engagement * 100) if min_engagement > 0 else 0
        # Considerar significativo si diferencia > 10%
        significativo = diferencia_porcentual > 10
        return {
            "significativo": significativo,
            "confianza": 95 if significativo else 50,
            "diferencia_porcentual": round(diferencia_porcentual, 1)
        }
    def _generar_recomendacion_ab_test(
        self,
        ganador: Dict[str, Any],
        resultados: List[Dict[str, Any]],
        significancia: Dict[str, Any]
    ) -> str:
        """Genera recomendación basada en resultados del A/B test"""
        if significancia.get('significativo', False):
            return f"Implementar {ganador['variante']} - Muestra diferencia significativa ({significancia['diferencia_porcentual']:.1f}%)"
        else:
            return f"Considerar {ganador['variante']} pero diferencia no es estadísticamente significativa. Continuar testing."
    def analisis_sentimiento_avanzado(
        self,
        texto: str,
        incluir_aspectos: bool = True
    ) -> Dict[str, Any]:
        """
        Análisis de sentimiento avanzado con NLP
        Args:
            texto: Texto a analizar
            incluir_aspectos: Si incluir análisis por aspectos
        Returns:
            Análisis de sentimiento completo
        """
        # Análisis básico de sentimiento (simplificado)
        palabras_positivas = ['excelente', 'genial', 'bueno', 'mejor', 'increíble', 'fantástico', 'perfecto', 'amor', 'feliz']
        palabras_negativas = ['malo', 'terrible', 'horrible', 'odio', 'triste', 'decepcionado', 'problema', 'error']
        texto_lower = texto.lower()
        # Contar palabras positivas y negativas
        positivas = sum(1 for palabra in palabras_positivas if palabra in texto_lower)
        negativas = sum(1 for palabra in palabras_negativas if palabra in texto_lower)
        # Calcular score de sentimiento
        total_palabras_sentimiento = positivas + negativas
        if total_palabras_sentimiento > 0:
            score_sentimiento = ((positivas - negativas) / total_palabras_sentimiento) * 100
        else:
            score_sentimiento = 0
        # Determinar sentimiento
        if score_sentimiento > 30:
            sentimiento = "POSITIVO"
        elif score_sentimiento < -30:
            sentimiento = "NEGATIVO"
        else:
            sentimiento = "NEUTRAL"
        resultado = {
            "texto_analizado": texto[:100] + "..." if len(texto) > 100 else texto,
            "sentimiento": sentimiento,
            "score_sentimiento": round(score_sentimiento, 1),
            "palabras_positivas": positivas,
            "palabras_negativas": negativas,
            "confianza": min(100, abs(score_sentimiento) + 50)
        }
        if incluir_aspectos:
            resultado['aspectos'] = self._analizar_aspectos_sentimiento(texto)
        return resultado
    def _analizar_aspectos_sentimiento(self, texto: str) -> List[Dict[str, Any]]:
        """Analiza sentimiento por aspectos"""
        aspectos = []
        # Aspectos comunes a buscar
        aspectos_buscar = {
            "calidad": ["calidad", "bueno", "excelente", "malo"],
            "precio": ["precio", "caro", "barato", "costoso"],
            "servicio": ["servicio", "atención", "soporte", "ayuda"]
        }
        texto_lower = texto.lower()
        for aspecto, palabras in aspectos_buscar.items():
            mencionado = any(palabra in texto_lower for palabra in palabras)
            if mencionado:
                # Determinar sentimiento del aspecto
                palabras_positivas_aspecto = ['bueno', 'excelente', 'barato']
                palabras_negativas_aspecto = ['malo', 'caro', 'costoso']
                positivo = any(p in texto_lower for p in palabras_positivas_aspecto)
                negativo = any(p in texto_lower for p in palabras_negativas_aspecto)
                sentimiento_aspecto = "POSITIVO" if positivo and not negativo else "NEGATIVO" if negativo else "NEUTRAL"
                aspectos.append({
                    "aspecto": aspecto,
                    "mencionado": True,
                    "sentimiento": sentimiento_aspecto
                })
        return aspectos
    def deteccion_oportunidades_contenido(
        self,
        plataforma: str = None
    ) -> Dict[str, Any]:
        """
        Detección automática de oportunidades de contenido
        Args:
            plataforma: Plataforma específica (opcional)
        Returns:
            Oportunidades detectadas
        """
        oportunidades = []
        # 1. Oportunidad: Tipo de contenido subutilizado
        analisis_tipos = self._analizar_uso_tipos_contenido()
        tipo_subutilizado = self._identificar_tipo_subutilizado(analisis_tipos)
        if tipo_subutilizado:
            oportunidades.append({
                "tipo": "TIPO_CONTENIDO",
                "prioridad": "Media",
                "descripcion": f"Tipo de contenido '{tipo_subutilizado['tipo']}' está subutilizado",
                "impacto_estimado": "Medio",
                "accion": f"Incrementar contenido tipo {tipo_subutilizado['tipo']}"
            })
        # 2. Oportunidad: Timing no optimizado
        mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
            tipo_contenido='Y',
            plataforma=plataforma or 'Instagram'
        )
        if 'error' not in mejor_momento:
            oportunidades.append({
                "tipo": "TIMING",
                "prioridad": "Alta",
                "descripcion": f"Mejor momento identificado: {temp_dia} a las {temp_hora}:00",
                "impacto_estimado": "Alto",
                "accion": f"Publicar más contenido en este horario"
            })
        # 3. Oportunidad: Hashtags no optimizados
        hashtags_efectivos = self.analizador.analizar_hashtags_efectivos(plataforma=plataforma)
        if 'error' not in hashtags_efectivos:
            top_hashtags = hashtags_efectivos.get('top_hashtags', [])[:5]
            oportunidades.append({
                "tipo": "HASHTAGS",
                "prioridad": "Media",
                "descripcion": f"Usar hashtags más efectivos identificados",
                "impacto_estimado": "Medio",
                "accion": f"Considerar: {', '.join([h['hashtag'] for h in top_hashtags])}"
            })
        return {
            "total_oportunidades": len(oportunidades),
            "oportunidades": oportunidades,
            "oportunidades_alta_prioridad": [o for o in oportunidades if o['prioridad'] == 'Alta'],
            "fecha_deteccion": datetime.now().isoformat()
        }
    def _analizar_uso_tipos_contenido(self) -> Dict[str, Any]:
        """Analiza uso de tipos de contenido"""
        por_tipo = defaultdict(int)
        for pub in self.analizador.publicaciones:
            por_tipo[pub.tipo_contenido] += 1
        total = sum(por_tipo.values())
        porcentajes = {tipo: (count / total * 100) if total > 0 else 0 for tipo, count in por_tipo.items()}
        return {
            "distribucion": porcentajes,
            "total": total
        }
    def _identificar_tipo_subutilizado(self, analisis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Identifica tipo de contenido subutilizado"""
        distribucion = analisis.get('distribucion', {})
        if not distribucion:
            return None
        # Encontrar tipo con menor uso pero mejor rendimiento
        tipos_con_rendimiento = []
        for tipo in distribucion.keys():
            publicaciones_tipo = [p for p in self.analizador.publicaciones if p.tipo_contenido == tipo]
            if publicaciones_tipo:
                rendimiento_promedio = statistics.mean([p.engagement_score for p in publicaciones_tipo])
                porcentaje_uso = distribucion[tipo]
                tipos_con_rendimiento.append({
                    "tipo": tipo,
                    "porcentaje_uso": porcentaje_uso,
                    "rendimiento_promedio": rendimiento_promedio
                })
        if tipos_con_rendimiento:
            # Tipo con buen rendimiento pero bajo uso
            tipos_ordenados = sorted(tipos_con_rendimiento, key=lambda x: x['rendimiento_promedio'], reverse=True)
            for tipo_info in tipos_ordenados:
                if tipo_info['porcentaje_uso'] < 30:  # Menos del 30% de uso
                    return tipo_info
        return None
    def analisis_cross_platform_avanzado(
        self,
        plataformas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Análisis cross-platform avanzado
        Args:
            plataformas: Lista de plataformas a analizar
        Returns:
            Análisis cross-platform completo
        """
        if plataformas is None:
            plataformas = ['Instagram', 'Facebook', 'LinkedIn', 'Twitter']
        analisis_plataformas = []
        for plataforma in plataformas:
            publicaciones_plataforma = [
                p for p in self.analizador.publicaciones
                if p.plataforma == plataforma
            ]
            if publicaciones_plataforma:
                analisis_plataforma = {
                    "plataforma": plataforma,
                    "total_publicaciones": len(publicaciones_plataforma),
                    "engagement_promedio": statistics.mean([p.engagement_score for p in publicaciones_plataforma]),
                    "engagement_rate_promedio": statistics.mean([p.engagement_rate for p in publicaciones_plataforma]),
                    "tasa_viral": sum(1 for p in publicaciones_plataforma if p.es_viral) / len(publicaciones_plataforma) * 100
                }
                analisis_plataformas.append(analisis_plataforma)
        # Comparación entre plataformas
        mejor_plataforma = max(analisis_plataformas, key=lambda x: x['engagement_promedio']) if analisis_plataformas else None
        # Oportunidades cross-platform
        oportunidades = self._identificar_oportunidades_cross_platform(analisis_plataformas)
        return {
            "plataformas_analizadas": len(analisis_plataformas),
            "analisis_por_plataforma": analisis_plataformas,
            "mejor_plataforma": mejor_plataforma,
            "oportunidades_cross_platform": oportunidades,
            "recomendacion_estrategia": self._generar_recomendacion_cross_platform(analisis_plataformas, mejor_plataforma)
        }
    def _identificar_oportunidades_cross_platform(
        self,
        analisis_plataformas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades cross-platform"""
        oportunidades = []
        if len(analisis_plataformas) < 2:
            return oportunidades
        # Encontrar plataforma con mejor rendimiento
        mejor_plataforma = max(analisis_plataformas, key=lambda x: x['engagement_promedio'])
        # Comparar otras plataformas con la mejor
        for plataforma in analisis_plataformas:
            if plataforma['plataforma'] != mejor_plataforma['plataforma']:
                diferencia = mejor_plataforma['engagement_promedio'] - plataforma['engagement_promedio']
                if diferencia > 50:
                    oportunidades.append({
                        "tipo": "MEJORAR_PLATAFORMA",
                        "plataforma": plataforma['plataforma'],
                        "descripcion": f"Plataforma {plataforma['plataforma']} tiene {diferencia:.1f} puntos menos que {mejor_plataforma['plataforma']}",
                        "impacto_estimado": "Alto",
                        "accion": f"Optimizar estrategia en {plataforma['plataforma']}"
                    })
        return oportunidades
    def _generar_recomendacion_cross_platform(
        self,
        analisis_plataformas: List[Dict[str, Any]],
        mejor_plataforma: Optional[Dict[str, Any]]
    ) -> str:
        """Genera recomendación de estrategia cross-platform"""
        if not mejor_plataforma:
            return "No hay suficientes datos para recomendación"
        return f"Enfocarse en {mejor_plataforma['plataforma']} como plataforma principal, replicar estrategia exitosa en otras plataformas"
    def sistema_scoring_contenido_tiempo_real(
        self,
        titulo: str,
        tipo_contenido: str,
        plataforma: str,
        hashtags: List[str] = None,
        horario: int = None,
        dia_semana: str = None
    ) -> Dict[str, Any]:
        """
        Sistema de scoring de contenido en tiempo real
        Args:
            titulo: Título del contenido
            tipo_contenido: Tipo de contenido
            plataforma: Plataforma objetivo
            hashtags: Lista de hashtags
            horario: Hora de publicación
            dia_semana: Día de la semana
        Returns:
            Score completo del contenido
        """
        score_total = 0
        factores = {}
        recomendaciones = []
        # Factor 1: Predicción ML (0-30 puntos)
        try:
            prediccion_ml = self.analizador_ml.predecir_engagement_ml(
                tipo_contenido=tipo_contenido,
                plataforma=plataforma,
                hora=horario or 10,
                dia_semana=dia_semana or 'Wednesday',
                tiene_media=True,
                hashtags=hashtags or [],
                titulo=titulo
            )
            engagement_predicho = prediccion_ml.get('engagement_score_predicho', 0)
            score_ml = min(30, (engagement_predicho / 10))  # Normalizar a 30 puntos
            factores['prediccion_ml'] = round(score_ml, 1)
            score_total += score_ml
        except:
            factores['prediccion_ml'] = 15  # Score neutral si falla
            score_total += 15
        # Factor 2: Análisis de sentimiento (0-20 puntos)
        try:
            sentimiento = self.analisis_sentimiento_avanzado(titulo)
            score_sentimiento = (sentimiento['score_sentimiento'] + 100) / 10  # Normalizar
            factores['sentimiento'] = round(score_sentimiento, 1)
            score_total += score_sentimiento
            if sentimiento['sentimiento'] == 'NEGATIVO':
                recomendaciones.append('Considera ajustar el tono del contenido')
        except:
            factores['sentimiento'] = 10
            score_total += 10
        # Factor 3: Optimización de hashtags (0-15 puntos)
        if hashtags:
            try:
                hashtags_efectivos = self.analizador.analizar_hashtags_efectivos(plataforma=plataforma)
                if 'error' not in hashtags_efectivos:
                    top_hashtags = [h['hashtag'] for h in hashtags_efectivos.get('top_hashtags', [])[:10]]
                    hashtags_usados_efectivos = sum(1 for h in hashtags if h in top_hashtags)
                    score_hashtags = min(15, (hashtags_usados_efectivos / len(hashtags) * 15) if hashtags else 0)
                    factores['hashtags'] = round(score_hashtags, 1)
                    score_total += score_hashtags
                else:
                    factores['hashtags'] = 7
                    score_total += 7
            except:
                factores['hashtags'] = 7
                score_total += 7
        else:
            factores['hashtags'] = 0
            score_total += 0
            recomendaciones.append('Agrega hashtags relevantes')
        # Factor 4: Timing óptimo (0-15 puntos)
        if horario is not None and dia_semana is not None:
            try:
                mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
                    tipo_contenido=tipo_contenido,
                    plataforma=plataforma
                )
                if 'error' not in mejor_momento:
                    mejor_hora = mejor_momento['mejor_momento'].get('hora', 10)
                    mejor_dia = mejor_momento['mejor_momento'].get('dia', 'Wednesday')
                    diferencia_hora = abs(horario - mejor_hora)
                    mismo_dia = dia_semana == mejor_dia
                    if mismo_dia and diferencia_hora <= 1:
                        score_timing = 15
                    elif mismo_dia and diferencia_hora <= 3:
                        score_timing = 12
                    elif mismo_dia:
                        score_timing = 8
                    else:
                        score_timing = 5
                    factores['timing'] = round(score_timing, 1)
                    score_total += score_timing
                    if score_timing < 10:
                        recomendaciones.append(f'Mejor momento: {mejor_dia} a las {mejor_hora}:00')
                else:
                    factores['timing'] = 7
                    score_total += 7
            except:
                factores['timing'] = 7
                score_total += 7
        else:
            factores['timing'] = 7
            score_total += 7
        # Factor 5: Tipo de contenido histórico (0-20 puntos)
        try:
            analisis_tipo = self.analizador.analizar_por_tipo()
            if tipo_contenido in analisis_tipo:
                engagement_promedio = analisis_tipo[tipo_contenido]['engagement_score_promedio']
                mejor_engagement = max([d['engagement_score_promedio'] for d in analisis_tipo.values()])
                if engagement_promedio >= mejor_engagement * 0.9:
                    score_tipo = 20
                elif engagement_promedio >= mejor_engagement * 0.7:
                    score_tipo = 15
                else:
                    score_tipo = 10
            else:
                score_tipo = 10
            factores['tipo_contenido'] = score_tipo
            score_total += score_tipo
        except:
            factores['tipo_contenido'] = 10
            score_total += 10
        # Clasificación final
        if score_total >= 85:
            nivel = 'Excelente'
            probabilidad_viral = 'Muy Alta'
            color = 'verde'
        elif score_total >= 70:
            nivel = 'Muy Bueno'
            probabilidad_viral = 'Alta'
            color = 'verde_claro'
        elif score_total >= 55:
            nivel = 'Bueno'
            probabilidad_viral = 'Media-Alta'
            color = 'amarillo'
        elif score_total >= 40:
            nivel = 'Regular'
            probabilidad_viral = 'Media'
            color = 'naranja'
        else:
            nivel = 'Necesita Mejora'
            probabilidad_viral = 'Baja'
            color = 'rojo'
        return {
            'score_total': round(score_total, 1),
            'score_maximo': 100,
            'porcentaje': round((score_total / 100) * 100, 1),
            'nivel': nivel,
            'probabilidad_viral': probabilidad_viral,
            'color': color,
            'factores': factores,
            'recomendaciones': recomendaciones,
            'mejoras_prioritarias': recomendaciones[:3] if recomendaciones else []
        }
    def analisis_tendencias_mercado_avanzado(
        self,
        palabras_clave: List[str] = None,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de tendencias de mercado
        Args:
            palabras_clave: Palabras clave a analizar
            periodo_dias: Período de análisis en días
        Returns:
            Análisis completo de tendencias
        """
        if palabras_clave is None:
            palabras_clave = [p['palabra'] for p in self.analizador.analizar_palabras_clave_titulos()[:15]]
        tendencias = {
            'palabras_clave_analizadas': palabras_clave,
            'tendencias_por_palabra': [],
            'tendencias_emergentes': [],
            'tendencias_declinantes': [],
            'recomendaciones_estrategicas': []
        }
        fecha_limite = datetime.now() - timedelta(days=periodo_dias)
        publicaciones_recientes = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= fecha_limite
        ]
        for palabra in palabras_clave:
            publicaciones_palabra = [
                p for p in publicaciones_recientes
                if palabra.lower() in p.titulo.lower()
            ]
            if publicaciones_palabra:
                # Dividir en períodos
                publicaciones_ordenadas = sorted(publicaciones_palabra, key=lambda p: p.fecha_publicacion)
                mitad = len(publicaciones_ordenadas) // 2
                primera_mitad = publicaciones_ordenadas[:mitad] if mitad > 0 else []
                segunda_mitad = publicaciones_ordenadas[mitad:] if mitad > 0 else publicaciones_ordenadas
                engagement_primera = statistics.mean([p.engagement_score for p in primera_mitad]) if primera_mitad else 0
                engagement_segunda = statistics.mean([p.engagement_score for p in segunda_mitad]) if segunda_mitad else 0
                cambio = engagement_segunda - engagement_primera
                cambio_porcentual = ((cambio / engagement_primera) * 100) if engagement_primera > 0 else 0
                frecuencia_primera = len(primera_mitad)
                frecuencia_segunda = len(segunda_mitad)
                crecimiento_frecuencia = ((frecuencia_segunda - frecuencia_primera) / frecuencia_primera * 100) if frecuencia_primera > 0 else 0
                # Clasificar tendencia
                if cambio_porcentual > 20 and crecimiento_frecuencia > 10:
                    tipo_tendencia = 'EMERGENTE'
                    tendencias['tendencias_emergentes'].append(palabra)
                elif cambio_porcentual < -20:
                    tipo_tendencia = 'DECLINANTE'
                    tendencias['tendencias_declinantes'].append(palabra)
                elif cambio_porcentual > 0:
                    tipo_tendencia = 'CRECIENTE'
                elif cambio_porcentual < 0:
                    tipo_tendencia = 'DECRECIENTE'
                else:
                    tipo_tendencia = 'ESTABLE'
                tendencias['tendencias_por_palabra'].append({
                    'palabra': palabra,
                    'tipo_tendencia': tipo_tendencia,
                    'engagement_promedio': statistics.mean([p.engagement_score for p in publicaciones_palabra]),
                    'cambio_engagement': round(cambio, 1),
                    'cambio_porcentual': round(cambio_porcentual, 1),
                    'frecuencia_total': len(publicaciones_palabra),
                    'crecimiento_frecuencia': round(crecimiento_frecuencia, 1),
                    'recomendacion': self._generar_recomendacion_tendencia(tipo_tendencia, palabra)
                })
        # Ordenar por engagement promedio
        tendencias['tendencias_por_palabra'].sort(key=lambda x: x['engagement_promedio'], reverse=True)
        # Generar recomendaciones estratégicas
        if tendencias['tendencias_emergentes']:
            mejor_emergente = max(
                [t for t in tendencias['tendencias_por_palabra'] if t['palabra'] in tendencias['tendencias_emergentes']],
                key=lambda x: x['engagement_promedio']
            )
            tendencias['recomendaciones_estrategicas'].append({
                'tipo': 'OPORTUNIDAD',
                'prioridad': 'Alta',
                'descripcion': f"Palabra clave '{mejor_emergente['palabra']}' está emergiendo con alto engagement",
                'accion': f"Incrementar uso de '{mejor_emergente['palabra']}' en próximas publicaciones"
            })
        if tendencias['tendencias_declinantes']:
            tendencias['recomendaciones_estrategicas'].append({
                'tipo': 'ADVERTENCIA',
                'prioridad': 'Media',
                'descripcion': f"Palabras clave en declive: {', '.join(tendencias['tendencias_declinantes'][:3])}",
                'accion': 'Considerar reducir uso o buscar alternativas'
            })
        return tendencias
    def _generar_recomendacion_tendencia(self, tipo_tendencia: str, palabra: str) -> str:
        """Genera recomendación basada en tipo de tendencia"""
        recomendaciones = {
            'EMERGENTE': f"Incrementar uso de '{palabra}' - tendencia emergente con alto potencial",
            'CRECIENTE': f"Mantener o incrementar uso de '{palabra}' - tendencia creciente",
            'ESTABLE': f"Mantener uso moderado de '{palabra}' - tendencia estable",
            'DECRECIENTE': f"Reducir uso de '{palabra}' - tendencia decreciente",
            'DECLINANTE': f"Evitar o reducir significativamente uso de '{palabra}' - en declive"
        }
        return recomendaciones.get(tipo_tendencia, f"Monitorear '{palabra}'")
    def generar_recomendaciones_inteligentes_avanzadas(
        self,
        objetivo: str = "aumentar_engagement"
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones inteligentes avanzadas basadas en múltiples análisis
        Args:
            objetivo: Objetivo principal (aumentar_engagement, mejorar_roi, etc.)
        Returns:
            Recomendaciones completas y priorizadas
        """
        recomendaciones = []
        # 1. Análisis de gaps
        try:
            gaps = self.analizador.analizar_gaps_contenido()
            if gaps and gaps.get('oportunidades'):
                for op in gaps['oportunidades'][:3]:
                    recomendaciones.append({
                        'categoria': 'OPORTUNIDAD',
                        'prioridad': 'Alta' if op['impacto_esperado'] == 'Alto' else 'Media',
                        'titulo': op['descripcion'],
                        'descripcion': f"Impacto esperado: {op['impacto_esperado']}",
                        'accion': op.get('tipo', 'Explorar oportunidad'),
                        'fuente': 'Análisis de gaps'
                    })
        except:
            pass
        # 2. Análisis de ROI
        if objetivo == "mejorar_roi":
            try:
                roi_analisis = self.analizador_roi.analizar_roi_detallado()
                if 'error' not in roi_analisis:
                    mejor_tipo_roi = max(
                        roi_analisis.get('roi_por_tipo', {}).items(),
                        key=lambda x: x[1].get('roi_promedio', 0) if isinstance(x[1], dict) else 0
                    )
                    recomendaciones.append({
                        'categoria': 'ROI',
                        'prioridad': 'Alta',
                        'titulo': f"Incrementar contenido tipo {mejor_tipo_roi[0]}",
                        'descripcion': f"Mejor ROI: {mejor_tipo_roi[1].get('roi_promedio', 0):.1f}%",
                        'accion': f"Crear más contenido de tipo {mejor_tipo_roi[0]}",
                        'fuente': 'Análisis de ROI'
                    })
            except:
                pass
        # 3. Análisis predictivo
        try:
            mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
                tipo_contenido='Y',
                plataforma='Instagram'
            )
            if 'error' not in mejor_momento:
                mejor = mejor_momento['mejor_momento']
                recomendaciones.append({
                    'categoria': 'TIMING',
                    'prioridad': 'Alta',
                    'titulo': 'Optimizar timing de publicaciones',
                    'descripcion': f"Mejor momento: {mejor.get('dia', 'N/A')} a las {mejor.get('hora', 'N/A')}:00",
                    'accion': f"Programar publicaciones para {mejor.get('dia', 'N/A')} a las {mejor.get('hora', 'N/A')}:00",
                    'fuente': 'Análisis predictivo'
                })
        except:
            pass
        # 4. Análisis cross-platform
        try:
            cross_platform = self.analisis_cross_platform_avanzado()
            if cross_platform.get('mejor_plataforma'):
                mejor_plataforma = cross_platform['mejor_plataforma']
                recomendaciones.append({
                    'categoria': 'PLATAFORMA',
                    'prioridad': 'Media',
                    'titulo': f"Enfocarse en {mejor_plataforma['plataforma']}",
                    'descripcion': f"Mejor engagement: {mejor_plataforma['engagement_promedio']:.1f}",
                    'accion': f"Incrementar contenido en {mejor_plataforma['plataforma']}",
                    'fuente': 'Análisis cross-platform'
                })
        except:
            pass
        # Priorizar recomendaciones
        prioridad_valor = {'Alta': 3, 'Media': 2, 'Baja': 1}
        recomendaciones_priorizadas = sorted(
            recomendaciones,
            key=lambda x: prioridad_valor.get(x.get('prioridad', 'Baja'), 1),
            reverse=True
        )
        return {
            'total_recomendaciones': len(recomendaciones_priorizadas),
            'recomendaciones': recomendaciones_priorizadas,
            'recomendaciones_alta_prioridad': [r for r in recomendaciones_priorizadas if r.get('prioridad') == 'Alta'],
            'categorias': list(set([r['categoria'] for r in recomendaciones_priorizadas])),
            'objetivo': objetivo
        }
    def exportar_reporte_completo(
        self,
        output_file: str = None,
        formato: str = 'json'
    ) -> Dict[str, Any]:
        """
        Exporta un reporte completo con todos los análisis
        Args:
            output_file: Archivo de salida
            formato: Formato de exportación (json, html, csv)
        Returns:
            Información del reporte generado
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"reporte_avanzado_v2_{timestamp}.{formato}"
        reporte = {
            'fecha_generacion': datetime.now().isoformat(),
            'resumen_ejecutivo': {},
            'alertas': {},
            'roi_predictivo': {},
            'tendencias': {},
            'recomendaciones': {},
            'analisis_detallados': {}
        }
        # Resumen ejecutivo
        mejor_tipo = self.analizador.identificar_mejor_tipo()
        temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
        reporte['resumen_ejecutivo'] = {
            'mejor_tipo_contenido': temp_nombre,
            'engagement_promedio': mejor_tipo.get('datos', {}).get('engagement_score_promedio', 0) if mejor_tipo and mejor_tipo.get('datos') else 0,
            'total_publicaciones': len(self.analizador.publicaciones)
        }
        # Alertas
        try:
            reporte['alertas'] = self.sistema_alertas_predictivas()
        except:
            reporte['alertas'] = {'error': 'No disponible'}
        # ROI predictivo
        try:
            reporte['roi_predictivo'] = self.analisis_roi_predictivo_avanzado()
        except:
            reporte['roi_predictivo'] = {'error': 'No disponible'}
        # Tendencias
        try:
            reporte['tendencias'] = self.analisis_tendencias_mercado_avanzado()
        except:
            reporte['tendencias'] = {'error': 'No disponible'}
        # Recomendaciones
        try:
            reporte['recomendaciones'] = self.generar_recomendaciones_inteligentes_avanzadas()
        except:
            reporte['recomendaciones'] = {'error': 'No disponible'}
        # Análisis detallados
        reporte['analisis_detallados'] = {
            'por_tipo': self.analizador.analizar_por_tipo(),
            'por_plataforma': self.analizador.analizar_por_plataforma(),
            'horarios_optimos': self.analizador.analizar_horarios_optimos(),
            'hashtags_efectivos': self.analizador.analizar_hashtags_efectivos(top_n=10)
        }
        # Exportar según formato
        if formato == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
        elif formato == 'csv':
            # Exportación CSV simplificada
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Categoría', 'Valor'])
                writer.writerow(['Total Publicaciones', len(self.analizador.publicaciones)])
                writer.writerow(['Mejor Tipo', mejor_tipo['datos']['nombre']])
        return {
            'archivo_generado': output_file,
            'formato': formato,
            'tamano_kb': round(os.path.getsize(output_file) / 1024, 2) if os.path.exists(output_file) else 0,
            'fecha_exportacion': datetime.now().isoformat()
        }
    def analisis_audiencia_profundo(
        self,
        segmentar_por: List[str] = None
    ) -> Dict[str, Any]:
        """
        Análisis profundo de audiencia y comportamiento
        Args:
            segmentar_por: Lista de criterios de segmentación (plataforma, tipo_contenido, etc.)
        Returns:
            Análisis completo de audiencia
        """
        if segmentar_por is None:
            segmentar_por = ['plataforma', 'tipo_contenido']
        analisis = {
            'segmentos': {},
            'comportamiento_por_segmento': {},
            'preferencias_audiencia': {},
            'insights': []
        }
        # Segmentar por diferentes criterios
        for criterio in segmentar_por:
            segmentos = defaultdict(list)
            for pub in self.analizador.publicaciones:
                if criterio == 'plataforma':
                    segmentos[pub.plataforma].append(pub)
                elif criterio == 'tipo_contenido':
                    segmentos[pub.tipo_contenido].append(pub)
                elif criterio == 'horario':
                    hora = pub.fecha_publicacion.hour
                    segmento_hora = f"{hora:02d}-{(hora+1)%24:02d}"
                    segmentos[segmento_hora].append(pub)
            analisis_segmento = {}
            for segmento, publicaciones in segmentos.items():
                if publicaciones:
                    analisis_segmento[segmento] = {
                        'total_publicaciones': len(publicaciones),
                        'engagement_promedio': statistics.mean([p.engagement_score for p in publicaciones]),
                        'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in publicaciones]),
                        'tasa_viral': sum(1 for p in publicaciones if p.es_viral) / len(publicaciones) * 100,
                        'tiempo_respuesta_promedio': self._calcular_tiempo_respuesta_promedio(publicaciones)
                    }
            analisis['segmentos'][criterio] = analisis_segmento
        # Comportamiento por segmento
        mejor_segmento = self._identificar_mejor_segmento(analisis['segmentos'])
        analisis['comportamiento_por_segmento'] = mejor_segmento
        # Preferencias de audiencia
        analisis['preferencias_audiencia'] = {
            'plataforma_preferida': max(
                analisis['segmentos'].get('plataforma', {}).items(),
                key=lambda x: x[1].get('engagement_promedio', 0)
            )[0] if analisis['segmentos'].get('plataforma') else 'N/A',
            'tipo_contenido_preferido': max(
                analisis['segmentos'].get('tipo_contenido', {}).items(),
                key=lambda x: x[1].get('engagement_promedio', 0)
            )[0] if analisis['segmentos'].get('tipo_contenido') else 'N/A',
            'horario_preferido': max(
                analisis['segmentos'].get('horario', {}).items(),
                key=lambda x: x[1].get('engagement_promedio', 0)
            )[0] if analisis['segmentos'].get('horario') else 'N/A'
        }
        # Generar insights
        analisis['insights'] = self._generar_insights_audiencia(analisis)
        return analisis
    def _calcular_tiempo_respuesta_promedio(self, publicaciones: List) -> float:
        """Calcula tiempo promedio de respuesta (simulado)"""
        # Simulación: tiempo de respuesta basado en engagement
        tiempos = []
        for pub in publicaciones:
            # Mayor engagement = menor tiempo de respuesta
            tiempo_estimado = max(1, 60 - (pub.engagement_score / 10))
            tiempos.append(tiempo_estimado)
        return statistics.mean(tiempos) if tiempos else 0
    def _identificar_mejor_segmento(self, segmentos: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica el mejor segmento de audiencia"""
        mejor_segmento = {}
        for criterio, datos in segmentos.items():
            if datos:
                mejor = max(datos.items(), key=lambda x: x[1].get('engagement_promedio', 0))
                mejor_segmento[criterio] = {
                    'segmento': mejor[0],
                    'metricas': mejor[1]
                }
        return mejor_segmento
    def _generar_insights_audiencia(self, analisis: Dict[str, Any]) -> List[str]:
        """Genera insights sobre la audiencia"""
        insights = []
        preferencias = analisis.get('preferencias_audiencia', {})
        if preferencias.get('plataforma_preferida') != 'N/A':
            insights.append(f"La audiencia prefiere contenido en {preferencias['plataforma_preferida']}")
        if preferencias.get('tipo_contenido_preferido') != 'N/A':
            insights.append(f"El tipo de contenido '{preferencias['tipo_contenido_preferido']}' genera más engagement")
        if preferencias.get('horario_preferido') != 'N/A':
            insights.append(f"Mejor momento para publicar: {preferencias['horario_preferido']}")
        return insights
    def optimizacion_contenido_automatica(
        self,
        contenido_original: Dict[str, Any],
        num_variantes: int = 3
    ) -> Dict[str, Any]:
        """
        Optimización automática de contenido generando variantes
        Args:
            contenido_original: Contenido original a optimizar
            num_variantes: Número de variantes a generar
        Returns:
            Variantes optimizadas con scores
        """
        variantes = []
        titulo_original = contenido_original.get('titulo', '')
        tipo_contenido = contenido_original.get('tipo_contenido', 'Y')
        plataforma = contenido_original.get('plataforma', 'Instagram')
        # Variante 1: Optimizar título con hook
        titulo_v1 = self._agregar_hook(titulo_original)
        score_v1 = self.sistema_scoring_contenido_tiempo_real(
            titulo=titulo_v1,
            tipo_contenido=tipo_contenido,
            plataforma=plataforma,
            hashtags=contenido_original.get('hashtags', []),
            horario=contenido_original.get('horario'),
            dia_semana=contenido_original.get('dia_semana')
        )
        variantes.append({
            'variante': 'Con hook mejorado',
            'titulo': titulo_v1,
            'score': score_v1['score_total'],
            'mejoras': ['Hook agregado']
        })
        # Variante 2: Optimizar hashtags
        hashtags_optimizados = self._optimizar_hashtags(
            contenido_original.get('hashtags', []),
            plataforma
        )
        score_v2 = self.sistema_scoring_contenido_tiempo_real(
            titulo=titulo_original,
            tipo_contenido=tipo_contenido,
            plataforma=plataforma,
            hashtags=hashtags_optimizados,
            horario=contenido_original.get('horario'),
            dia_semana=contenido_original.get('dia_semana')
        )
        variantes.append({
            'variante': 'Hashtags optimizados',
            'titulo': titulo_original,
            'hashtags': hashtags_optimizados,
            'score': score_v2['score_total'],
            'mejoras': ['Hashtags optimizados']
        })
        # Variante 3: Optimizar timing
        mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
            tipo_contenido=tipo_contenido,
            plataforma=plataforma
        )
        if 'error' not in mejor_momento:
            mejor = mejor_momento['mejor_momento']
            score_v3 = self.sistema_scoring_contenido_tiempo_real(
                titulo=titulo_original,
                tipo_contenido=tipo_contenido,
                plataforma=plataforma,
                hashtags=contenido_original.get('hashtags', []),
                horario=mejor.get('hora'),
                dia_semana=mejor.get('dia')
            )
            variantes.append({
                'variante': 'Timing optimizado',
                'titulo': titulo_original,
                'horario': mejor.get('hora'),
                'dia_semana': mejor.get('dia'),
                'score': score_v3['score_total'],
                'mejoras': ['Timing optimizado']
            })
        # Ordenar por score
        variantes.sort(key=lambda x: x['score'], reverse=True)
        return {
            'contenido_original': contenido_original,
            'variantes': variantes,
            'mejor_variante': variantes[0] if variantes else None,
            'mejora_score': variantes[0]['score'] - self.sistema_scoring_contenido_tiempo_real(
                titulo=titulo_original,
                tipo_contenido=tipo_contenido,
                plataforma=plataforma,
                hashtags=contenido_original.get('hashtags', []),
                horario=contenido_original.get('horario'),
                dia_semana=contenido_original.get('dia_semana')
            )['score_total'] if variantes else 0
        }
    def _agregar_hook(self, titulo: str) -> str:
        """Agrega un hook efectivo al título"""
        hooks = [
            "¿Sabías que...",
            "Descubre cómo...",
            "La verdad sobre...",
            "3 formas de...",
            "El secreto de..."
        ]
        # Verificar si ya tiene hook
        if any(titulo.startswith(hook.split()[0]) for hook in hooks):
            return titulo
        # Agregar hook al inicio
        import random
        hook = random.choice(hooks)
        return f"{hook} {titulo}"
    def _optimizar_hashtags(self, hashtags: List[str], plataforma: str) -> List[str]:
        """Optimiza hashtags para una plataforma"""
        try:
            hashtags_efectivos = self.analizador.analizar_hashtags_efectivos(plataforma=plataforma)
            if 'error' not in hashtags_efectivos:
                top_hashtags = [h['hashtag'] for h in hashtags_efectivos.get('top_hashtags', [])[:10]]
                # Combinar hashtags originales con los más efectivos
                hashtags_optimizados = list(set(hashtags + top_hashtags[:5]))
                return hashtags_optimizados[:10]  # Limitar a 10
        except:
            pass
        return hashtags
    def dashboard_metricas_tiempo_real(
        self,
        periodo_horas: int = 24
    ) -> Dict[str, Any]:
        """
        Dashboard de métricas en tiempo real
        Args:
            periodo_horas: Período de análisis en horas
        Returns:
            Dashboard completo con métricas en tiempo real
        """
        fecha_limite = datetime.now() - timedelta(hours=periodo_horas)
        publicaciones_recientes = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= fecha_limite
        ]
        dashboard = {
            'periodo_analizado': f'Últimas {periodo_horas} horas',
            'fecha_actualizacion': datetime.now().isoformat(),
            'metricas_generales': {},
            'metricas_por_hora': {},
            'tendencias': {},
            'alertas_activas': []
        }
        if publicaciones_recientes:
            # Métricas generales
            dashboard['metricas_generales'] = {
                'total_publicaciones': len(publicaciones_recientes),
                'engagement_total': sum(p.engagement_total for p in publicaciones_recientes),
                'engagement_promedio': statistics.mean([p.engagement_score for p in publicaciones_recientes]),
                'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in publicaciones_recientes]),
                'publicaciones_virales': sum(1 for p in publicaciones_recientes if p.es_viral),
                'tasa_viral': sum(1 for p in publicaciones_recientes if p.es_viral) / len(publicaciones_recientes) * 100
            }
            # Métricas por hora
            por_hora = defaultdict(list)
            for pub in publicaciones_recientes:
                hora = pub.fecha_publicacion.hour
                por_hora[hora].append(pub)
            for hora, pubs in por_hora.items():
                dashboard['metricas_por_hora'][f"{hora:02d}:00"] = {
                    'publicaciones': len(pubs),
                    'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]),
                    'engagement_total': sum(p.engagement_total for p in pubs)
                }
            # Tendencias
            if len(publicaciones_recientes) >= 4:
                mitad = len(publicaciones_recientes) // 2
                primera_mitad = publicaciones_recientes[:mitad]
                segunda_mitad = publicaciones_recientes[mitad:]
                engagement_primera = statistics.mean([p.engagement_score for p in primera_mitad])
                engagement_segunda = statistics.mean([p.engagement_score for p in segunda_mitad])
                cambio = engagement_segunda - engagement_primera
                cambio_porcentual = ((cambio / engagement_primera) * 100) if engagement_primera > 0 else 0
                dashboard['tendencias'] = {
                    'direccion': 'creciendo' if cambio > 0 else 'decreciendo' if cambio < 0 else 'estable',
                    'cambio_porcentual': round(cambio_porcentual, 1),
                    'velocidad_cambio': 'rapida' if abs(cambio_porcentual) > 20 else 'moderada' if abs(cambio_porcentual) > 10 else 'lenta'
                }
        # Alertas activas
        try:
            alertas = self.sistema_alertas_predictivas()
            dashboard['alertas_activas'] = alertas.get('alertas_criticas', []) + alertas.get('alertas_altas', [])
        except:
            pass
        return dashboard
    def prediccion_engagement_futuro(
        self,
        semanas_futuras: int = 4,
        escenario: str = 'conservador'
    ) -> Dict[str, Any]:
        """
        Predicción de engagement futuro con diferentes escenarios
        Args:
            semanas_futuras: Semanas a proyectar
            escenario: Escenario de proyección (conservador, optimista, pesimista)
        Returns:
            Predicciones de engagement futuro
        """
        predicciones = {
            'escenario': escenario,
            'semanas_proyectadas': semanas_futuras,
            'predicciones_semanales': [],
            'tendencia_general': '',
            'recomendaciones': []
        }
        # Obtener tendencias actuales
        try:
            tendencias = self.analizador_predictivo.predecir_tendencias_futuras(
                semanas_futuras=semanas_futuras
            )
            if 'error' not in tendencias and 'predicciones' in tendencias:
                # Ajustar según escenario
                multiplicador_escenario = {
                    'conservador': 0.9,
                    'optimista': 1.2,
                    'pesimista': 0.7
                }.get(escenario, 1.0)
                for pred in tendencias['predicciones']:
                    engagement_base = pred.get('engagement_score_predicho', 0)
                    engagement_ajustado = engagement_base * multiplicador_escenario
                    predicciones['predicciones_semanales'].append({
                        'semana': pred.get('semana', 0),
                        'fecha': pred.get('fecha', ''),
                        'engagement_predicho': round(engagement_ajustado, 1),
                        'engagement_base': round(engagement_base, 1),
                        'factor_escenario': multiplicador_escenario
                    })
                # Calcular tendencia general
                if len(predicciones['predicciones_semanales']) >= 2:
                    primera = predicciones['predicciones_semanales'][0]['engagement_predicho']
                    ultima = predicciones['predicciones_semanales'][-1]['engagement_predicho']
                    if ultima > primera * 1.1:
                        predicciones['tendencia_general'] = 'Creciente'
                    elif ultima < primera * 0.9:
                        predicciones['tendencia_general'] = 'Decreciente'
                    else:
                        predicciones['tendencia_general'] = 'Estable'
                # Generar recomendaciones
                if predicciones['tendencia_general'] == 'Decreciente':
                    predicciones['recomendaciones'].append('Considerar ajustar estrategia para revertir tendencia decreciente')
                elif predicciones['tendencia_general'] == 'Creciente':
                    predicciones['recomendaciones'].append('Mantener estrategia actual - tendencia positiva')
        except:
            predicciones['error'] = 'No se pudo generar predicción'
        return predicciones
    def analisis_competitivo_avanzado(
        self,
        datos_competidores: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Análisis competitivo avanzado comparando con competidores
        Args:
            datos_competidores: Datos de competidores para comparar
        Returns:
            Análisis competitivo completo
        """
        analisis = {
            'posicion_mercado': {},
            'ventajas_competitivas': [],
            'desventajas_competitivas': [],
            'oportunidades_competitivas': [],
            'benchmarking': {},
            'recomendaciones_estrategicas': []
        }
        # Análisis propio
        analisis_propio = {
            'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 0,
            'engagement_score_promedio': statistics.mean([p.engagement_score for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 0,
            'frecuencia_publicacion': len(self.analizador.publicaciones) / 30 if self.analizador.publicaciones else 0,
            'tasa_viral': sum(1 for p in self.analizador.publicaciones if p.es_viral) / len(self.analizador.publicaciones) * 100 if self.analizador.publicaciones else 0
        }
        if datos_competidores:
            # Comparar con competidores
            engagement_competidores = [c.get('engagement_rate_promedio', 0) for c in datos_competidores]
            engagement_competidores.append(analisis_propio['engagement_rate_promedio'])
            ranking = sorted(enumerate(engagement_competidores), key=lambda x: x[1], reverse=True)
            for pos, (idx, rate) in enumerate(ranking):
                if idx == len(datos_competidores):  # Es nuestro análisis
                    analisis['posicion_mercado'] = {
                        'posicion': pos + 1,
                        'total_competidores': len(datos_competidores) + 1,
                        'percentil': round((1 - (pos / len(ranking))) * 100, 1)
                    }
                    break
            # Identificar ventajas y desventajas
            mejor_competidor = max(datos_competidores, key=lambda x: x.get('engagement_rate_promedio', 0))
            if analisis_propio['engagement_rate_promedio'] > mejor_competidor.get('engagement_rate_promedio', 0):
                diferencia = analisis_propio['engagement_rate_promedio'] - mejor_competidor.get('engagement_rate_promedio', 0)
                analisis['ventajas_competitivas'].append({
                    'tipo': 'ENGAGEMENT_RATE',
                    'descripcion': f"Superas al mejor competidor por {diferencia:.2f}% en engagement rate",
                    'impacto': 'Alto'
                })
            else:
                diferencia = mejor_competidor.get('engagement_rate_promedio', 0) - analisis_propio['engagement_rate_promedio']
                analisis['desventajas_competitivas'].append({
                    'tipo': 'ENGAGEMENT_RATE',
                    'descripcion': f"El mejor competidor te supera por {diferencia:.2f}% en engagement rate",
                    'impacto': 'Alto',
                    'accion': 'Mejorar estrategia de contenido para aumentar engagement'
                })
            # Benchmarking
            analisis['benchmarking'] = {
                'engagement_rate_mercado': statistics.mean([c.get('engagement_rate_promedio', 0) for c in datos_competidores]),
                'engagement_rate_propio': analisis_propio['engagement_rate_promedio'],
                'diferencia_vs_mercado': analisis_propio['engagement_rate_promedio'] - statistics.mean([c.get('engagement_rate_promedio', 0) for c in datos_competidores]),
                'frecuencia_mercado': statistics.mean([c.get('frecuencia_publicacion', 0) for c in datos_competidores]),
                'frecuencia_propia': analisis_propio['frecuencia_publicacion']
            }
        # Oportunidades competitivas
        mejor_tipo = self.analizador.identificar_mejor_tipo()
        temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
        analisis['oportunidades_competitivas'].append({
            'tipo': 'TIPO_CONTENIDO',
            'descripcion': f"Explotar más el tipo de contenido '{temp_nombre}' que tiene mejor rendimiento",
            'impacto': 'Alto'
        })
        # Recomendaciones estratégicas
        if analisis['posicion_mercado'].get('posicion', 0) > len(datos_competidores) / 2 if datos_competidores else 0:
            analisis['recomendaciones_estrategicas'].append({
                'prioridad': 'Alta',
                'descripcion': 'Mejorar posición en el mercado - estás por debajo del promedio',
                'accion': 'Revisar y optimizar estrategia completa de contenido'
            })
        return {
            'analisis_propio': analisis_propio,
            'analisis_competitivo': analisis,
            'competidores': datos_competidores or []
        }
    def generacion_contenido_inteligente(
        self,
        tema: str,
        tipo_contenido: str = None,
        plataforma: str = None
    ) -> Dict[str, Any]:
        """
        Generación inteligente de contenido basada en análisis
        Args:
            tema: Tema del contenido
            tipo_contenido: Tipo de contenido (opcional)
            plataforma: Plataforma objetivo (opcional)
        Returns:
            Contenido generado con optimizaciones
        """
        # Determinar mejor tipo y plataforma si no se proporcionan
        if not tipo_contenido:
            mejor_tipo = self.analizador.identificar_mejor_tipo()
            temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
            tipo_contenido = mejor_tipo.get('tipo', 'N/A') if mejor_tipo else 'N/A'
        if not plataforma:
            analisis_plataformas = self.analizador.analizar_por_plataforma()
            if analisis_plataformas:
                plataforma = max(analisis_plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            else:
                plataforma = 'LinkedIn'
        # Obtener mejores prácticas
        mejor_momento = self.analizador_predictivo.predecir_mejor_momento_publicar(
            tipo_contenido=tipo_contenido,
            plataforma=plataforma
        )
        hashtags_efectivos = self.analizador.analizar_hashtags_efectivos(plataforma=plataforma)
        top_hashtags = [h['hashtag'] for h in hashtags_efectivos.get('top_hashtags', [])[:7]] if 'error' not in hashtags_efectivos else []
        # Generar título optimizado
        titulo_optimizado = self._generar_titulo_optimizado(tema, tipo_contenido, plataforma)
        # Generar estructura de contenido
        estructura = self._generar_estructura_contenido(tipo_contenido, plataforma)
        # Calcular score del contenido generado
        score = self.sistema_scoring_contenido_tiempo_real(
            titulo=titulo_optimizado,
            tipo_contenido=tipo_contenido,
            plataforma=plataforma,
            hashtags=top_hashtags,
            horario=mejor_momento['mejor_momento'].get('hora', 10) if 'error' not in mejor_momento else 10,
            dia_semana=mejor_momento['mejor_momento'].get('dia', 'Wednesday') if 'error' not in mejor_momento else 'Wednesday'
        )
        return {
            'tema': tema,
            'tipo_contenido': tipo_contenido,
            'plataforma': plataforma,
            'titulo_optimizado': titulo_optimizado,
            'estructura_contenido': estructura,
            'hashtags_recomendados': top_hashtags,
            'mejor_momento_publicacion': mejor_momento['mejor_momento'] if 'error' not in mejor_momento else {},
            'score_predicho': score['score_total'],
            'probabilidad_viral': score['probabilidad_viral'],
            'recomendaciones': score.get('recomendaciones', [])
        }
    def _generar_titulo_optimizado(self, tema: str, tipo_contenido: str, plataforma: str) -> str:
        """Genera un título optimizado basado en mejores prácticas"""
        hooks_por_tipo = {
            'X': ['Descubre', 'Aprende', 'Guía completa'],
            'Y': ['¿Sabías que...', 'La verdad sobre', '3 formas de'],
            'Z': ['Caso de éxito', 'Historia real', 'Testimonio']
        }
        hooks = hooks_por_tipo.get(tipo_contenido, ['Descubre', 'Aprende'])
        import random
        hook = random.choice(hooks)
        # Ajustar según plataforma
        if plataforma.lower() == 'linkedin':
            # LinkedIn prefiere títulos más profesionales
            return f"{hook} {tema}: Estrategias que funcionan"
        elif plataforma.lower() == 'twitter':
            # Twitter prefiere títulos más cortos y directos
            return f"{hook} {tema[:50]}"
        else:
            return f"{hook} {tema}"
    def _generar_estructura_contenido(self, tipo_contenido: str, plataforma: str) -> Dict[str, Any]:
        """Genera estructura de contenido optimizada"""
        estructuras = {
            'X': {
                'introduccion': 'Hook + Contexto',
                'desarrollo': '3-5 puntos clave',
                'conclusion': 'CTA + Pregunta',
                'longitud_recomendada': '1000-1500 caracteres' if plataforma.lower() == 'linkedin' else '300-500 caracteres'
            },
            'Y': {
                'introduccion': 'Pregunta provocativa',
                'desarrollo': 'Respuesta + Ejemplos',
                'conclusion': 'Reflexión + CTA',
                'longitud_recomendada': '800-1200 caracteres'
            },
            'Z': {
                'introduccion': 'Contexto de la historia',
                'desarrollo': 'Narrativa + Lecciones',
                'conclusion': 'Aplicación práctica',
                'longitud_recomendada': '1200-2000 caracteres'
            }
        }
        return estructuras.get(tipo_contenido, estructuras['X'])
    def analisis_performance_campanas(
        self,
        campanas: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Análisis de performance de campañas
        Args:
            campanas: Lista de campañas a analizar
        Returns:
            Análisis completo de campañas
        """
        if campanas is None:
            # Generar campañas simuladas basadas en publicaciones
            campanas = []
            publicaciones_por_mes = defaultdict(list)
            for pub in self.analizador.publicaciones:
                mes_key = pub.fecha_publicacion.strftime('%Y-%m')
                publicaciones_por_mes[mes_key].append(pub)
            for mes, pubs in publicaciones_por_mes.items():
                campanas.append({
                    'nombre': f'Campaña {mes}',
                    'fecha_inicio': min(p.fecha_publicacion for p in pubs).isoformat(),
                    'fecha_fin': max(p.fecha_publicacion for p in pubs).isoformat(),
                    'publicaciones': len(pubs),
                    'engagement_total': sum(p.engagement_total for p in pubs),
                    'engagement_promedio': statistics.mean([p.engagement_score for p in pubs])
                })
        analisis = {
            'total_campanas': len(campanas),
            'campanas_analizadas': [],
            'mejor_campana': None,
            'peor_campana': None,
            'tendencias_campanas': {},
            'recomendaciones': []
        }
        for campana in campanas:
            analisis_campana = {
                'nombre': campana.get('nombre', 'Sin nombre'),
                'publicaciones': campana.get('publicaciones', 0),
                'engagement_total': campana.get('engagement_total', 0),
                'engagement_promedio': campana.get('engagement_promedio', 0),
                'roi_estimado': self._calcular_roi_campana(campana),
                'eficiencia': campana.get('engagement_promedio', 0) / campana.get('publicaciones', 1) if campana.get('publicaciones', 0) > 0 else 0
            }
            analisis['campanas_analizadas'].append(analisis_campana)
        # Identificar mejor y peor campaña
        if analisis['campanas_analizadas']:
            analisis['mejor_campana'] = max(analisis['campanas_analizadas'], key=lambda x: x['engagement_promedio'])
            analisis['peor_campana'] = min(analisis['campanas_analizadas'], key=lambda x: x['engagement_promedio'])
            # Análisis de tendencias
            if len(analisis['campanas_analizadas']) >= 2:
                primera = analisis['campanas_analizadas'][0]['engagement_promedio']
                ultima = analisis['campanas_analizadas'][-1]['engagement_promedio']
                cambio = ultima - primera
                analisis['tendencias_campanas'] = {
                    'direccion': 'mejorando' if cambio > 0 else 'empeorando' if cambio < 0 else 'estable',
                    'cambio_porcentual': round((cambio / primera * 100) if primera > 0 else 0, 1),
                    'tendencia': 'positiva' if cambio > 0 else 'negativa' if cambio < 0 else 'neutral'
                }
                if cambio < 0:
                    analisis['recomendaciones'].append({
                        'prioridad': 'Alta',
                        'descripcion': 'Las campañas están mostrando tendencia decreciente',
                        'accion': 'Revisar estrategia y aplicar lecciones de la mejor campaña'
                    })
        return analisis
    def _calcular_roi_campana(self, campana: Dict[str, Any]) -> float:
        """Calcula ROI estimado de una campaña"""
        costo_estimado = campana.get('publicaciones', 0) * 50  # $50 por publicación
        valor_engagement = campana.get('engagement_total', 0) * 0.10  # $0.10 por engagement
        if costo_estimado > 0:
            roi = ((valor_engagement - costo_estimado) / costo_estimado) * 100
            return round(roi, 1)
        return 0
    def sistema_recomendaciones_personalizadas_ai(
        self,
        perfil_usuario: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Sistema de recomendaciones personalizadas con IA
        Args:
            perfil_usuario: Perfil del usuario (objetivos, audiencia, etc.)
        Returns:
            Recomendaciones personalizadas
        """
        recomendaciones = []
        # Analizar perfil del usuario
        if perfil_usuario is None:
            perfil_usuario = {
                'objetivo_principal': 'aumentar_engagement',
                'audiencia_objetivo': 'profesionales',
                'presupuesto': 'medio',
                'frecuencia_deseada': '3-5 veces por semana'
            }
        objetivo = perfil_usuario.get('objetivo_principal', 'aumentar_engagement')
        # Recomendación 1: Basada en objetivo
        if objetivo == 'aumentar_engagement':
            mejor_tipo = self.analizador.identificar_mejor_tipo()
            temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
            temp_engagement_score_promedio = mejor_tipo.get('datos', {}).get('engagement_score_promedio', 0) if mejor_tipo and mejor_tipo.get('datos') else 0
            mejor_tipo_tipo = mejor_tipo.get('tipo', 'N/A') if mejor_tipo else 'N/A'
            recomendaciones.append({
                'tipo': 'TIPO_CONTENIDO',
                'prioridad': 'Alta',
                'titulo': f"Incrementar contenido tipo '{temp_nombre}'",
                'descripcion': f"Este tipo tiene engagement score promedio de {temp_engagement_score_promedio:.1f}",
                'accion': f"Crear 2-3 publicaciones de tipo {mejor_tipo_tipo} esta semana",
                'impacto_esperado': 'Alto',
                'personalizado': True
            })
        # Recomendación 2: Basada en audiencia
        audiencia_objetivo = perfil_usuario.get('audiencia_objetivo', 'general')
        if audiencia_objetivo == 'profesionales':
            recomendaciones.append({
                'tipo': 'PLATAFORMA',
                'prioridad': 'Alta',
                'titulo': 'Enfocarse en LinkedIn',
                'descripcion': 'LinkedIn es ideal para audiencia profesional',
                'accion': 'Aumentar presencia en LinkedIn con contenido profesional',
                'impacto_esperado': 'Alto',
                'personalizado': True
            })
        # Recomendación 3: Basada en presupuesto
        presupuesto = perfil_usuario.get('presupuesto', 'medio')
        if presupuesto == 'bajo':
            recomendaciones.append({
                'tipo': 'ESTRATEGIA',
                'prioridad': 'Media',
                'titulo': 'Optimizar contenido existente',
                'descripcion': 'Reutilizar y optimizar contenido exitoso',
                'accion': 'Repurposing de contenido con mejor engagement',
                'impacto_esperado': 'Medio-Alto',
                'personalizado': True
            })
        # Recomendación 4: Basada en frecuencia
        frecuencia = perfil_usuario.get('frecuencia_deseada', '3-5 veces por semana')
        frecuencia_optima = self.analizador.optimizar_frecuencia_publicacion()
        if frecuencia_optima.get('frecuencia_optima_recomendada'):
            recomendaciones.append({
                'tipo': 'FRECUENCIA',
                'prioridad': 'Media',
                'titulo': 'Optimizar frecuencia de publicación',
                'descripcion': f"Frecuencia óptima: cada {frecuencia_optima['frecuencia_optima_recomendada']} días",
                'accion': f"Ajustar calendario para publicar cada {frecuencia_optima['frecuencia_optima_recomendada']} días",
                'impacto_esperado': 'Medio',
                'personalizado': True
            })
        return {
            'perfil_usuario': perfil_usuario,
            'total_recomendaciones': len(recomendaciones),
            'recomendaciones': recomendaciones,
            'recomendaciones_alta_prioridad': [r for r in recomendaciones if r.get('prioridad') == 'Alta'],
            'fecha_generacion': datetime.now().isoformat()
        }
    def analisis_sentimiento_avanzado_multi_plataforma(
        self,
        incluir_comentarios: bool = False
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de sentimiento multi-plataforma
        Args:
            incluir_comentarios: Si incluir análisis de comentarios (simulado)
        Returns:
            Análisis de sentimiento por plataforma
        """
        analisis = {
            'sentimiento_por_plataforma': {},
            'sentimiento_general': {},
            'tendencias_sentimiento': {},
            'recomendaciones': []
        }
        plataformas = list(set([p.plataforma for p in self.analizador.publicaciones]))
        for plataforma in plataformas:
            publicaciones_plataforma = [p for p in self.analizador.publicaciones if p.plataforma == plataforma]
            if publicaciones_plataforma:
                sentimientos = []
                for pub in publicaciones_plataforma:
                    sentimiento = self.analisis_sentimiento_avanzado(pub.titulo)
                    sentimientos.append(sentimiento)
                # Calcular promedios
                scores = [s['score_sentimiento'] for s in sentimientos]
                positivos = sum(1 for s in sentimientos if s['sentimiento'] == 'POSITIVO')
                negativos = sum(1 for s in sentimientos if s['sentimiento'] == 'NEGATIVO')
                neutrales = sum(1 for s in sentimientos if s['sentimiento'] == 'NEUTRAL')
                analisis['sentimiento_por_plataforma'][plataforma] = {
                    'score_promedio': statistics.mean(scores) if scores else 0,
                    'distribucion': {
                        'positivo': round((positivos / len(sentimientos) * 100), 1),
                        'negativo': round((negativos / len(sentimientos) * 100), 1),
                        'neutral': round((neutrales / len(sentimientos) * 100), 1)
                    },
                    'total_publicaciones': len(publicaciones_plataforma),
                    'sentimiento_dominante': 'POSITIVO' if positivos > negativos and positivos > neutrales else 'NEGATIVO' if negativos > positivos else 'NEUTRAL'
                }
        # Sentimiento general
        todos_scores = []
        for plataforma_data in analisis['sentimiento_por_plataforma'].values():
            todos_scores.append(plataforma_data['score_promedio'])
        if todos_scores:
            analisis['sentimiento_general'] = {
                'score_promedio': statistics.mean(todos_scores),
                'sentimiento_dominante': max(
                    analisis['sentimiento_por_plataforma'].items(),
                    key=lambda x: x[1]['distribucion']['positivo']
                )[1]['sentimiento_dominante'] if analisis['sentimiento_por_plataforma'] else 'NEUTRAL'
            }
        # Recomendaciones
        if analisis['sentimiento_general'].get('score_promedio', 0) < 0:
            analisis['recomendaciones'].append({
                'prioridad': 'Alta',
                'descripcion': 'El sentimiento general es negativo',
                'accion': 'Revisar contenido y ajustar tono hacia mensajes más positivos'
            })
        return analisis
    def deteccion_patrones_ocultos(
        self,
        min_frecuencia: int = 3
    ) -> Dict[str, Any]:
        """
        Detección de patrones ocultos en el contenido
        Args:
            min_frecuencia: Frecuencia mínima para considerar un patrón
        Returns:
            Patrones detectados
        """
        patrones = {
            'patrones_temporales': {},
            'patrones_contenido': {},
            'patrones_hashtags': {},
            'patrones_engagement': {},
            'insights': []
        }
        # Patrón 1: Días consecutivos con alto engagement
        publicaciones_ordenadas = sorted(self.analizador.publicaciones, key=lambda p: p.fecha_publicacion)
        dias_consecutivos = []
        racha_actual = []
        for i, pub in enumerate(publicaciones_ordenadas):
            if i == 0:
                racha_actual.append(pub)
            else:
                dia_anterior = publicaciones_ordenadas[i-1].fecha_publicacion.date()
                dia_actual = pub.fecha_publicacion.date()
                if (dia_actual - dia_anterior).days == 1:
                    racha_actual.append(pub)
                else:
                    if len(racha_actual) >= min_frecuencia:
                        engagement_promedio = statistics.mean([p.engagement_score for p in racha_actual])
                        if engagement_promedio > statistics.mean([p.engagement_score for p in self.analizador.publicaciones]):
                            dias_consecutivos.append({
                                'dias': len(racha_actual),
                                'engagement_promedio': engagement_promedio,
                                'fecha_inicio': racha_actual[0].fecha_publicacion.date().isoformat()
                            })
                    racha_actual = [pub]
        if dias_consecutivos:
            patrones['patrones_temporales']['rachas_exitosas'] = dias_consecutivos
        # Patrón 2: Combinaciones de hashtags efectivas
        combinaciones_hashtags = defaultdict(list)
        for pub in self.analizador.publicaciones:
            if len(pub.hashtags) >= 2:
                # Generar combinaciones de 2 hashtags
                for i, h1 in enumerate(pub.hashtags):
                    for h2 in pub.hashtags[i+1:]:
                        combinacion = tuple(sorted([h1.lower(), h2.lower()]))
                        combinaciones_hashtags[combinacion].append(pub.engagement_score)
        combinaciones_efectivas = []
        for combo, scores in combinaciones_hashtags.items():
            if len(scores) >= min_frecuencia:
                promedio = statistics.mean(scores)
                if promedio > statistics.mean([p.engagement_score for p in self.analizador.publicaciones]):
                    combinaciones_efectivas.append({
                        'hashtags': list(combo),
                        'frecuencia': len(scores),
                        'engagement_promedio': promedio
                    })
        if combinaciones_efectivas:
            combinaciones_efectivas.sort(key=lambda x: x['engagement_promedio'], reverse=True)
            patrones['patrones_hashtags']['combinaciones_efectivas'] = combinaciones_efectivas[:10]
        # Patrón 3: Tipos de contenido que funcionan mejor en ciertos días
        contenido_por_dia = defaultdict(lambda: defaultdict(list))
        for pub in self.analizador.publicaciones:
            dia = pub.fecha_publicacion.strftime('%A')
            contenido_por_dia[dia][pub.tipo_contenido].append(pub.engagement_score)
        mejores_combinaciones = []
        for dia, tipos in contenido_por_dia.items():
            for tipo, scores in tipos.items():
                if len(scores) >= min_frecuencia:
                    promedio = statistics.mean(scores)
                    mejores_combinaciones.append({
                        'dia': dia,
                        'tipo_contenido': tipo,
                        'engagement_promedio': promedio,
                        'frecuencia': len(scores)
                    })
        if mejores_combinaciones:
            mejores_combinaciones.sort(key=lambda x: x['engagement_promedio'], reverse=True)
            patrones['patrones_contenido']['mejores_combinaciones_dia_tipo'] = mejores_combinaciones[:10]
        # Generar insights
        if patrones['patrones_hashtags'].get('combinaciones_efectivas'):
            mejor_combo = patrones['patrones_hashtags']['combinaciones_efectivas'][0]
            patrones['insights'].append(
                f"La combinación de hashtags {', '.join(mejor_combo['hashtags'])} genera {mejor_combo['engagement_promedio']:.1f} de engagement promedio"
            )
        if patrones['patrones_contenido'].get('mejores_combinaciones_dia_tipo'):
            mejor_combinacion = patrones['patrones_contenido']['mejores_combinaciones_dia_tipo'][0]
            patrones['insights'].append(
                f"El tipo '{mejor_combinacion['tipo_contenido']}' funciona mejor los {mejor_combinacion['dia']} con {mejor_combinacion['engagement_promedio']:.1f} de engagement promedio"
            )
        return patrones
    def optimizacion_automatica_estrategia(
        self,
        objetivo: str = 'maximizar_engagement'
    ) -> Dict[str, Any]:
        """
        Optimización automática de estrategia completa
        Args:
            objetivo: Objetivo de optimización
        Returns:
            Estrategia optimizada
        """
        estrategia = {
            'objetivo': objetivo,
            'recomendaciones_estrategicas': [],
            'calendario_optimizado': {},
            'mix_contenido': {},
            'distribucion_plataformas': {},
            'hashtags_estrategicos': {},
            'impacto_esperado': {}
        }
        # 1. Mix de contenido optimizado
        mejor_tipo = self.analizador.identificar_mejor_tipo()
        temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
        analisis_tipos = self.analizador.analizar_por_tipo()
        mix_contenido = {}
        total_engagement = sum([d['engagement_total'] for d in analisis_tipos.values()])
        for tipo, datos in analisis_tipos.items():
            porcentaje_actual = (datos['cantidad_publicaciones'] / len(self.analizador.publicaciones) * 100) if self.analizador.publicaciones else 0
            porcentaje_ideal = (datos['engagement_total'] / total_engagement * 100) if total_engagement > 0 else porcentaje_actual
            mix_contenido[tipo] = {
                'porcentaje_actual': round(porcentaje_actual, 1),
                'porcentaje_ideal': round(porcentaje_ideal, 1),
                'ajuste_necesario': round(porcentaje_ideal - porcentaje_actual, 1)
            }
        estrategia['mix_contenido'] = mix_contenido
        # 2. Distribución de plataformas optimizada
        analisis_plataformas = self.analizador.analizar_por_plataforma()
        total_engagement_plataformas = sum([d['engagement_total'] for d in analisis_plataformas.values()])
        distribucion = {}
        for plataforma, datos in analisis_plataformas.items():
            porcentaje_actual = (datos['cantidad_publicaciones'] / len(self.analizador.publicaciones) * 100) if self.analizador.publicaciones else 0
            porcentaje_ideal = (datos['engagement_total'] / total_engagement_plataformas * 100) if total_engagement_plataformas > 0 else porcentaje_actual
            distribucion[plataforma] = {
                'porcentaje_actual': round(porcentaje_actual, 1),
                'porcentaje_ideal': round(porcentaje_ideal, 1),
                'ajuste_necesario': round(porcentaje_ideal - porcentaje_actual, 1)
            }
        estrategia['distribucion_plataformas'] = distribucion
        # 3. Hashtags estratégicos por plataforma
        hashtags_por_plataforma = self.analizador.analizar_hashtags_por_plataforma()
        estrategia['hashtags_estrategicos'] = {
            plataforma: [h['hashtag'] for h in hashtags[:5]]
            for plataforma, hashtags in hashtags_por_plataforma.items()
        }
        # 4. Calendario optimizado
        frecuencia_optima = self.analizador.optimizar_frecuencia_publicacion()
        horarios_optimos = self.analizador.analizar_horarios_optimos()
        dias_optimos = self.analizador.analizar_dias_semana()
        mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios_optimos else '09-12'
        mejor_dia = max(dias_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if dias_optimos else 'Wednesday'
        estrategia['calendario_optimizado'] = {
            'frecuencia_optima': frecuencia_optima.get('frecuencia_optima_recomendada', 2),
            'mejor_horario': mejor_horario,
            'mejor_dia': mejor_dia,
            'publicaciones_semanales_recomendadas': frecuencia_optima.get('publicaciones_por_semana_optimas', 3)
        }
        # 5. Recomendaciones estratégicas
        if mejor_tipo:
            estrategia['recomendaciones_estrategicas'].append({
                'tipo': 'CONTENIDO',
                'prioridad': 'Alta',
                'descripcion': f"Incrementar contenido tipo '{temp_nombre}' al {mix_contenido[mejor_tipo['tipo']]['porcentaje_ideal']:.1f}%",
                'impacto': 'Alto'
            })
        mejor_plataforma = max(analisis_plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if analisis_plataformas else None
        if mejor_plataforma:
            estrategia['recomendaciones_estrategicas'].append({
                'tipo': 'PLATAFORMA',
                'prioridad': 'Alta',
                'descripcion': f"Enfocarse en {mejor_plataforma} con {temp_porcentaje_ideal:.1f}% del contenido",
                'impacto': 'Alto'
            })
        # 6. Impacto esperado
        engagement_actual = statistics.mean([p.engagement_score for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 0
        engagement_proyectado = engagement_actual * 1.15  # Asumiendo 15% de mejora con optimización
        estrategia['impacto_esperado'] = {
            'engagement_actual': round(engagement_actual, 1),
            'engagement_proyectado': round(engagement_proyectado, 1),
            'mejora_esperada': round(((engagement_proyectado - engagement_actual) / engagement_actual * 100) if engagement_actual > 0 else 0, 1),
            'tiempo_implementacion': '2-4 semanas'
        }
        return estrategia
    def sistema_alertas_proactivas(
        self,
        umbrales_personalizados: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Sistema de alertas proactivas que anticipa problemas
        Args:
            umbrales_personalizados: Umbrales personalizados para alertas
        Returns:
            Alertas proactivas generadas
        """
        if umbrales_personalizados is None:
            umbrales_personalizados = {
                'tendencia_decreciente_dias': 3,
                'engagement_bajo_porcentaje': 20,
                'frecuencia_baja_semanas': 2
            }
        alertas = []
        # Alerta 1: Tendencia decreciente detectada temprano
        if len(self.analizador.publicaciones) >= 5:
            publicaciones_recientes = sorted(
                [p for p in self.analizador.publicaciones if p.fecha_publicacion >= datetime.now() - timedelta(days=7)],
                key=lambda p: p.fecha_publicacion
            )
            if len(publicaciones_recientes) >= 3:
                ultimas_3 = publicaciones_recientes[-3:]
                engagement_ultimas = [p.engagement_score for p in ultimas_3]
                if len(engagement_ultimas) >= 2:
                    tendencia = engagement_ultimas[-1] < engagement_ultimas[0]
                    if tendencia:
                        alertas.append({
                            'tipo': 'TENDENCIA_DECRECIENTE_TEMPRANA',
                            'severidad': 'Media',
                            'titulo': 'Tendencia decreciente detectada en últimos días',
                            'descripcion': 'El engagement ha disminuido en las últimas publicaciones',
                            'accion': 'Revisar contenido reciente y ajustar estrategia',
                            'prevencion': True
                        })
        # Alerta 2: Frecuencia de publicación baja
        publicaciones_ultimas_semanas = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= datetime.now() - timedelta(weeks=2)
        ]
        frecuencia_semanal = len(publicaciones_ultimas_semanas) / 2
        if frecuencia_semanal < umbrales_personalizados.get('frecuencia_baja_semanas', 2):
            alertas.append({
                'tipo': 'FRECUENCIA_BAJA',
                'severidad': 'Media',
                'titulo': 'Frecuencia de publicación por debajo del óptimo',
                'descripcion': f'Publicando {frecuencia_semanal:.1f} veces por semana (óptimo: 3-5)',
                'accion': 'Aumentar frecuencia de publicación para mantener engagement',
                'prevencion': True
            })
        # Alerta 3: Oportunidad de contenido trending
        tendencias = self.analisis_tendencias_mercado_avanzado()
        if tendencias.get('tendencias_emergentes'):
            mejor_emergente = max(
                [t for t in tendencias['tendencias_por_palabra'] if t['palabra'] in tendencias['tendencias_emergentes']],
                key=lambda x: x['engagement_promedio']
            )
            alertas.append({
                'tipo': 'OPORTUNIDAD_TRENDING',
                'severidad': 'Baja',
                'titulo': f"Oportunidad: '{mejor_emergente['palabra']}' está trending",
                'descripcion': f"Palabra clave emergente con {mejor_emergente['engagement_promedio']:.1f} engagement promedio",
                'accion': f"Incrementar uso de '{mejor_emergente['palabra']}' en próximas publicaciones",
                'prevencion': False,
                'oportunidad': True
            })
        return {
            'total_alertas': len(alertas),
            'alertas': alertas,
            'alertas_prevencion': [a for a in alertas if a.get('prevencion', False)],
            'alertas_oportunidades': [a for a in alertas if a.get('oportunidad', False)],
            'fecha_generacion': datetime.now().isoformat()
        }
    def reporte_completo_automatico(
        self,
        incluir_predicciones: bool = True,
        incluir_recomendaciones: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo automático con todos los análisis
        Args:
            incluir_predicciones: Si incluir predicciones futuras
            incluir_recomendaciones: Si incluir recomendaciones
        Returns:
            Reporte completo consolidado
        """
        reporte = {
            'fecha_generacion': datetime.now().isoformat(),
            'resumen_ejecutivo': {},
            'metricas_clave': {},
            'analisis_detallados': {},
            'predicciones': {},
            'recomendaciones': {},
            'acciones_prioritarias': []
        }
        # Resumen ejecutivo
        mejor_tipo = self.analizador.identificar_mejor_tipo()
        temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
        reporte['resumen_ejecutivo'] = {
            'mejor_tipo_contenido': temp_nombre,
            'engagement_promedio': mejor_tipo['datos']['engagement_score_promedio'],
            'total_publicaciones': len(self.analizador.publicaciones),
            'periodo_analizado': 'Últimos 30 días'
        }
        # Métricas clave
        reporte['metricas_clave'] = {
            'engagement_total': sum(p.engagement_total for p in self.analizador.publicaciones),
            'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 0,
            'publicaciones_virales': sum(1 for p in self.analizador.publicaciones if p.es_viral),
            'tasa_viral': sum(1 for p in self.analizador.publicaciones if p.es_viral) / len(self.analizador.publicaciones) * 100 if self.analizador.publicaciones else 0
        }
        # Análisis detallados
        reporte['analisis_detallados'] = {
            'por_tipo': self.analizador.analizar_por_tipo(),
            'por_plataforma': self.analizador.analizar_por_plataforma(),
            'horarios_optimos': self.analizador.analizar_horarios_optimos(),
            'dias_optimos': self.analizador.analizar_dias_semana(),
            'hashtags_efectivos': self.analizador.analizar_hashtags_efectivos(top_n=10),
            'tendencias': self.analizador.analizar_tendencias_temporales(),
            'gaps': self.analizador.analizar_gaps_contenido(),
            'patrones': self.deteccion_patrones_ocultos()
        }
        # Predicciones
        if incluir_predicciones:
            try:
                reporte['predicciones'] = {
                    'engagement_futuro': self.prediccion_engagement_futuro(semanas_futuras=4),
                    'tendencias_mercado': self.analisis_tendencias_mercado_avanzado(),
                    'roi_proyectado': self.analisis_roi_predictivo_avanzado()
                }
            except:
                reporte['predicciones'] = {'error': 'No disponible'}
        # Recomendaciones
        if incluir_recomendaciones:
            try:
                reporte['recomendaciones'] = {
                    'inteligentes': self.generar_recomendaciones_inteligentes_avanzadas(),
                    'personalizadas': self.sistema_recomendaciones_personalizadas_ai(),
                    'estrategia_optimizada': self.optimizacion_automatica_estrategia()
                }
            except:
                reporte['recomendaciones'] = {'error': 'No disponible'}
        # Acciones prioritarias
        if reporte.get('recomendaciones') and isinstance(reporte['recomendaciones'], dict):
            if 'inteligentes' in reporte['recomendaciones']:
                recs = reporte['recomendaciones']['inteligentes']
                if isinstance(recs, dict) and 'recomendaciones_alta_prioridad' in recs:
                    reporte['acciones_prioritarias'] = [
                        {
                            'accion': r.get('titulo', ''),
                            'prioridad': r.get('prioridad', 'Media'),
                            'impacto': r.get('impacto_esperado', 'Medio')
                        }
                        for r in recs['recomendaciones_alta_prioridad'][:5]
                    ]
        return reporte
    def analisis_eficiencia_recursos(
        self,
        costo_por_publicacion: float = 50.0
    ) -> Dict[str, Any]:
        """
        Análisis de eficiencia de recursos y ROI por tipo de contenido
        Args:
            costo_por_publicacion: Costo estimado por publicación
        Returns:
            Análisis de eficiencia y ROI
        """
        analisis = {
            'eficiencia_por_tipo': {},
            'eficiencia_por_plataforma': {},
            'roi_por_tipo': {},
            'roi_por_plataforma': {},
            'recomendaciones_eficiencia': [],
            'ranking_eficiencia': []
        }
        # Eficiencia por tipo de contenido
        analisis_tipos = self.analizador.analizar_por_tipo()
        for tipo, datos in analisis_tipos.items():
            costo_total = datos['cantidad_publicaciones'] * costo_por_publicacion
            valor_generado = datos['engagement_total'] * 0.10  # $0.10 por engagement
            roi = ((valor_generado - costo_total) / costo_total * 100) if costo_total > 0 else 0
            eficiencia = datos['engagement_total'] / datos['cantidad_publicaciones'] if datos['cantidad_publicaciones'] > 0 else 0
            analisis['eficiencia_por_tipo'][tipo] = {
                'costo_total': round(costo_total, 2),
                'valor_generado': round(valor_generado, 2),
                'roi': round(roi, 1),
                'eficiencia': round(eficiencia, 1),
                'engagement_por_dolar': round(eficiencia / costo_por_publicacion, 2) if costo_por_publicacion > 0 else 0
            }
            analisis['roi_por_tipo'][tipo] = round(roi, 1)
        # Eficiencia por plataforma
        analisis_plataformas = self.analizador.analizar_por_plataforma()
        for plataforma, datos in analisis_plataformas.items():
            costo_total = datos['cantidad_publicaciones'] * costo_por_publicacion
            valor_generado = datos['engagement_total'] * 0.10
            roi = ((valor_generado - costo_total) / costo_total * 100) if costo_total > 0 else 0
            eficiencia = datos['engagement_total'] / datos['cantidad_publicaciones'] if datos['cantidad_publicaciones'] > 0 else 0
            analisis['eficiencia_por_plataforma'][plataforma] = {
                'costo_total': round(costo_total, 2),
                'valor_generado': round(valor_generado, 2),
                'roi': round(roi, 1),
                'eficiencia': round(eficiencia, 1),
                'engagement_por_dolar': round(eficiencia / costo_por_publicacion, 2) if costo_por_publicacion > 0 else 0
            }
            analisis['roi_por_plataforma'][plataforma] = round(roi, 1)
        # Ranking de eficiencia
        ranking = []
        for tipo, datos in analisis['eficiencia_por_tipo'].items():
            ranking.append({
                'tipo': tipo,
                'roi': datos['roi'],
                'eficiencia': datos['eficiencia'],
                'engagement_por_dolar': datos['engagement_por_dolar']
            })
        ranking.sort(key=lambda x: x['roi'], reverse=True)
        analisis['ranking_eficiencia'] = ranking
        # Recomendaciones
        mejor_tipo = ranking[0] if ranking else None
        peor_tipo = ranking[-1] if len(ranking) > 1 else None
        if mejor_tipo and mejor_tipo['roi'] > 0:
            analisis['recomendaciones_eficiencia'].append({
                'tipo': 'INCREMENTAR',
                'descripcion': f"Incrementar inversión en tipo '{mejor_tipo['tipo']}' (ROI: {mejor_tipo['roi']:.1f}%)",
                'impacto': 'Alto'
            })
        if peor_tipo and peor_tipo['roi'] < 0:
            analisis['recomendaciones_eficiencia'].append({
                'tipo': 'REDUCIR',
                'descripcion': f"Reducir o optimizar tipo '{peor_tipo['tipo']}' (ROI negativo: {peor_tipo['roi']:.1f}%)",
                'impacto': 'Alto'
            })
        return analisis
    def simulador_escenarios_estrategicos(
        self,
        escenarios: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulador de escenarios estratégicos para planificación
        Args:
            escenarios: Lista de escenarios a simular
        Returns:
            Resultados de simulación por escenario
        """
        if escenarios is None:
            escenarios = [
                {
                    'nombre': 'Escenario Conservador',
                    'aumento_frecuencia': 0.1,  # 10% más
                    'cambio_mix_contenido': {'X': 0.1, 'Y': -0.05, 'Z': -0.05},
                    'optimizacion_hashtags': True
                },
                {
                    'nombre': 'Escenario Agresivo',
                    'aumento_frecuencia': 0.5,  # 50% más
                    'cambio_mix_contenido': {'X': 0.3, 'Y': -0.15, 'Z': -0.15},
                    'optimizacion_hashtags': True
                },
                {
                    'nombre': 'Escenario Balanceado',
                    'aumento_frecuencia': 0.2,  # 20% más
                    'cambio_mix_contenido': {'X': 0.15, 'Y': -0.05, 'Z': -0.1},
                    'optimizacion_hashtags': True
                }
            ]
        resultados = {
            'escenarios_simulados': [],
            'mejor_escenario': None,
            'recomendacion': None
        }
        engagement_actual = statistics.mean([p.engagement_score for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 0
        mejor_tipo = self.analizador.identificar_mejor_tipo()
        temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
        for escenario in escenarios:
            # Calcular engagement proyectado
            factor_frecuencia = 1 + escenario.get('aumento_frecuencia', 0)
            # Ajustar por cambio en mix de contenido
            factor_mix = 1.0
            if escenario.get('cambio_mix_contenido'):
                if temp_nombre in escenario['cambio_mix_contenido']:
                    factor_mix = 1.15
            # Factor de optimización de hashtags
            factor_hashtags = 1.05 if escenario.get('optimizacion_hashtags', False) else 1.0
            engagement_proyectado = engagement_actual * factor_frecuencia * factor_mix * factor_hashtags
            mejora_porcentual = ((engagement_proyectado - engagement_actual) / engagement_actual * 100) if engagement_actual > 0 else 0
            # Calcular inversión necesaria
            publicaciones_actuales = len(self.analizador.publicaciones)
            publicaciones_proyectadas = int(publicaciones_actuales * factor_frecuencia)
            inversión_adicional = (publicaciones_proyectadas - publicaciones_actuales) * 50
            resultado_escenario = {
                'nombre': escenario['nombre'],
                'engagement_actual': round(engagement_actual, 1),
                'engagement_proyectado': round(engagement_proyectado, 1),
                'mejora_porcentual': round(mejora_porcentual, 1),
                'inversion_adicional': round(inversión_adicional, 2),
                'publicaciones_actuales': publicaciones_actuales,
                'publicaciones_proyectadas': publicaciones_proyectadas,
                'roi_estimado': round((engagement_proyectado * 0.10 - inversión_adicional) / inversión_adicional * 100, 1) if inversión_adicional > 0 else 0
            }
            resultados['escenarios_simulados'].append(resultado_escenario)
        # Identificar mejor escenario
        if resultados['escenarios_simulados']:
            mejor = max(resultados['escenarios_simulados'], key=lambda x: x['mejora_porcentual'] / max(x['inversion_adicional'], 1))
            resultados['mejor_escenario'] = mejor
            resultados['recomendacion'] = {
                'escenario_recomendado': mejor['nombre'],
                'razon': f"Mejor balance entre mejora ({mejor['mejora_porcentual']:.1f}%) e inversión (${mejor['inversion_adicional']:.2f})",
                'impacto_esperado': 'Alto' if mejor['mejora_porcentual'] > 15 else 'Medio'
            }
        return resultados
    def analisis_cohortes_avanzado(
        self,
        periodo_cohorte: str = 'mensual'
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de cohortes de contenido
        Args:
            periodo_cohorte: Período para agrupar cohortes (mensual, semanal)
        Returns:
            Análisis de cohortes
        """
        analisis = {
            'cohortes': {},
            'retencion_engagement': {},
            'tendencias_cohortes': {},
            'insights': []
        }
        # Agrupar publicaciones por cohorte
        cohortes = defaultdict(list)
        for pub in self.analizador.publicaciones:
            if periodo_cohorte == 'mensual':
                clave = pub.fecha_publicacion.strftime('%Y-%m')
            else:  # semanal
                clave = pub.fecha_publicacion.strftime('%Y-W%U')
            cohortes[clave].append(pub)
        # Analizar cada cohorte
        for clave, publicaciones in sorted(cohortes.items()):
            analisis_cohorte = {
                'periodo': clave,
                'total_publicaciones': len(publicaciones),
                'engagement_total': sum(p.engagement_total for p in publicaciones),
                'engagement_promedio': statistics.mean([p.engagement_score for p in publicaciones]),
                'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in publicaciones]),
                'publicaciones_virales': sum(1 for p in publicaciones if p.es_viral),
                'tasa_viral': sum(1 for p in publicaciones if p.es_viral) / len(publicaciones) * 100 if publicaciones else 0
            }
            analisis['cohortes'][clave] = analisis_cohorte
        # Análisis de retención
        if len(analisis['cohortes']) >= 2:
            cohortes_ordenados = sorted(analisis['cohortes'].items())
            primera_cohorte = cohortes_ordenados[0][1]
            ultima_cohorte = cohortes_ordenados[-1][1]
            cambio_engagement = ultima_cohorte['engagement_promedio'] - primera_cohorte['engagement_promedio']
            cambio_porcentual = (cambio_engagement / primera_cohorte['engagement_promedio'] * 100) if primera_cohorte['engagement_promedio'] > 0 else 0
            analisis['retencion_engagement'] = {
                'primera_cohorte': primera_cohorte['engagement_promedio'],
                'ultima_cohorte': ultima_cohorte['engagement_promedio'],
                'cambio_absoluto': round(cambio_engagement, 1),
                'cambio_porcentual': round(cambio_porcentual, 1),
                'tendencia': 'mejorando' if cambio_engagement > 0 else 'empeorando' if cambio_engagement < 0 else 'estable'
            }
        # Tendencias entre cohortes
        if len(analisis['cohortes']) >= 3:
            engagement_por_cohorte = [c['engagement_promedio'] for c in analisis['cohortes'].values()]
            # Calcular tendencia
            if len(engagement_por_cohorte) >= 2:
                primera = engagement_por_cohorte[0]
                ultima = engagement_por_cohorte[-1]
                tendencia = 'creciente' if ultima > primera else 'decreciente' if ultima < primera else 'estable'
                analisis['tendencias_cohortes'] = {
                    'direccion': tendencia,
                    'volatilidad': round(statistics.stdev(engagement_por_cohorte) if len(engagement_por_cohorte) > 1 else 0, 1),
                    'consistencia': 'alta' if statistics.stdev(engagement_por_cohorte) < statistics.mean(engagement_por_cohorte) * 0.2 else 'media' if statistics.stdev(engagement_por_cohorte) < statistics.mean(engagement_por_cohorte) * 0.4 else 'baja'
                }
        # Generar insights
        if analisis.get('retencion_engagement'):
            ret = analisis['retencion_engagement']
            if ret['tendencia'] == 'mejorando':
                analisis['insights'].append(
                    f"El engagement ha mejorado {ret['cambio_porcentual']:.1f}% desde la primera cohorte"
                )
            elif ret['tendencia'] == 'empeorando':
                analisis['insights'].append(
                    f"El engagement ha disminuido {abs(ret['cambio_porcentual']):.1f}% - revisar estrategia"
                )
        return analisis
    def sistema_recomendaciones_contextuales(
        self,
        contexto_actual: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Sistema de recomendaciones contextuales basado en situación actual
        Args:
            contexto_actual: Contexto actual (día, hora, plataforma, etc.)
        Returns:
            Recomendaciones contextuales
        """
        if contexto_actual is None:
            ahora = datetime.now()
            contexto_actual = {
                'dia_semana': ahora.strftime('%A'),
                'hora': ahora.hour,
                'plataforma': 'LinkedIn',
                'objetivo': 'aumentar_engagement'
            }
        recomendaciones = []
        # Recomendación basada en día de la semana
        dias_optimos = self.analizador.analizar_dias_semana()
        dia_actual = contexto_actual.get('dia_semana', 'Monday')
        if dias_optimos:
            mejor_dia = max(dias_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            if dia_actual != mejor_dia:
                engagement_dia = dias_optimos[mejor_dia].get('engagement_score_promedio', 0)
                engagement_dia = dias_optimos[mejor_dia].get('engagement_score_promedio', 0)
                recomendaciones.append({
                    'tipo': 'TIMING',
                    'prioridad': 'Media',
                    'titulo': f'Mejor día para publicar: {mejor_dia}',
                    'descripcion': f'El {mejor_dia} tiene {engagement_dia:.1f} de engagement promedio',
                    'accion': f'Programar publicaciones para {mejor_dia}',
                    'contextual': True
                })
        # Recomendación basada en hora
        horarios_optimos = self.analizador.analizar_horarios_optimos()
        hora_actual = contexto_actual.get('hora', 12)
        if horarios_optimos:
            mejor_horario_str = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            mejor_hora = int(mejor_horario_str.split('-')[0])
            if abs(hora_actual - mejor_hora) > 2:
                recomendaciones.append({
                    'tipo': 'TIMING',
                    'prioridad': 'Media',
                    'titulo': f'Mejor horario: {mejor_horario_str}',
                    'descripcion': f'El horario {mejor_horario_str} tiene mejor engagement',
                    'accion': f'Publicar entre las {mejor_horario_str}',
                    'contextual': True
                })
        # Recomendación basada en plataforma
        analisis_plataformas = self.analizador.analizar_por_plataforma()
        plataforma_actual = contexto_actual.get('plataforma', 'LinkedIn')
        if analisis_plataformas:
            mejor_plataforma = max(analisis_plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            engagement_plataforma = analisis_plataformas[mejor_plataforma].get('engagement_score_promedio', 0)
            if plataforma_actual != mejor_plataforma:
                recomendaciones.append({
                    'tipo': 'PLATAFORMA',
                    'prioridad': 'Alta',
                    'titulo': f'Mejor plataforma: {mejor_plataforma}',

                    'descripcion': f'{mejor_plataforma} tiene {engagement_plataforma:.1f} de engagement promedio',
                    'accion': f'Considerar publicar más en {mejor_plataforma}',
                    'contextual': True
                })
        # Recomendación basada en objetivo
        objetivo = contexto_actual.get('objetivo', 'aumentar_engagement')
        if objetivo == 'aumentar_engagement':
            mejor_tipo = self.analizador.identificar_mejor_tipo()
            temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
            if mejor_tipo:
                recomendaciones.append({
                    'tipo': 'CONTENIDO',
                    'prioridad': 'Alta',
                    'titulo': f"Mejor tipo de contenido: '{temp_nombre}'",
                    'descripcion': f"Este tipo tiene {temp_engagement_score_promedio:.1f} de engagement promedio",
                    'accion': f"Incrementar contenido tipo {mejor_tipo['tipo']}",
                    'contextual': True
                })
        return {
            'contexto': contexto_actual,
            'total_recomendaciones': len(recomendaciones),
            'recomendaciones': recomendaciones,
            'recomendaciones_alta_prioridad': [r for r in recomendaciones if r.get('prioridad') == 'Alta'],
            'fecha_generacion': datetime.now().isoformat()
        }
    def dashboard_interactivo_metricas(
        self,
        periodo: str = '30d'
    ) -> Dict[str, Any]:
        """
        Dashboard interactivo con métricas clave
        Args:
            periodo: Período a analizar (7d, 30d, 90d)
        Returns:
            Dashboard con métricas clave
        """
        dias = int(periodo.replace('d', ''))
        fecha_limite = datetime.now() - timedelta(days=dias)
        publicaciones_periodo = [p for p in self.analizador.publicaciones if p.fecha_publicacion >= fecha_limite]
        dashboard = {
            'periodo': periodo,
            'fecha_analisis': datetime.now().isoformat(),
            'metricas_generales': {},
            'metricas_por_plataforma': {},
            'metricas_por_tipo': {},
            'tendencias': {},
            'alertas': [],
            'insights': []
        }
        if not publicaciones_periodo:
            return dashboard
        # Métricas generales
        dashboard['metricas_generales'] = {
            'total_publicaciones': len(publicaciones_periodo),
            'engagement_total': sum(p.engagement_total for p in publicaciones_periodo),
            'engagement_promedio': round(statistics.mean([p.engagement_score for p in publicaciones_periodo]), 1),
            'engagement_rate_promedio': round(statistics.mean([p.engagement_rate for p in publicaciones_periodo]), 2),
            'publicaciones_virales': sum(1 for p in publicaciones_periodo if p.es_viral),
            'tasa_viral': round(sum(1 for p in publicaciones_periodo if p.es_viral) / len(publicaciones_periodo) * 100, 1),
            'frecuencia_semanal': round(len(publicaciones_periodo) / (dias / 7), 1)
        }
        # Métricas por plataforma
        plataformas = list(set([p.plataforma for p in publicaciones_periodo]))
        for plataforma in plataformas:
            pubs_plataforma = [p for p in publicaciones_periodo if p.plataforma == plataforma]
            dashboard['metricas_por_plataforma'][plataforma] = {
                'publicaciones': len(pubs_plataforma),
                'engagement_promedio': round(statistics.mean([p.engagement_score for p in pubs_plataforma]), 1),
                'porcentaje_total': round(len(pubs_plataforma) / len(publicaciones_periodo) * 100, 1)
            }
        # Métricas por tipo
        tipos = list(set([p.tipo_contenido for p in publicaciones_periodo]))
        for tipo in tipos:
            pubs_tipo = [p for p in publicaciones_periodo if p.tipo_contenido == tipo]
            dashboard['metricas_por_tipo'][tipo] = {
                'publicaciones': len(pubs_tipo),
                'engagement_promedio': round(statistics.mean([p.engagement_score for p in pubs_tipo]), 1),
                'porcentaje_total': round(len(pubs_tipo) / len(publicaciones_periodo) * 100, 1)
            }
        # Tendencias
        if len(publicaciones_periodo) >= 2:
            publicaciones_ordenadas = sorted(publicaciones_periodo, key=lambda p: p.fecha_publicacion)
            primera_mitad = publicaciones_ordenadas[:len(publicaciones_ordenadas)//2]
            segunda_mitad = publicaciones_ordenadas[len(publicaciones_ordenadas)//2:]
            engagement_primera = statistics.mean([p.engagement_score for p in primera_mitad])
            engagement_segunda = statistics.mean([p.engagement_score for p in segunda_mitad])
            cambio = engagement_segunda - engagement_primera
            cambio_porcentual = (cambio / engagement_primera * 100) if engagement_primera > 0 else 0
            dashboard['tendencias'] = {
                'direccion': 'creciente' if cambio > 0 else 'decreciente' if cambio < 0 else 'estable',
                'cambio_absoluto': round(cambio, 1),
                'cambio_porcentual': round(cambio_porcentual, 1)
            }
        # Alertas
        if dashboard['tendencias'].get('direccion') == 'decreciente':
            dashboard['alertas'].append({
                'tipo': 'TENDENCIA',
                'severidad': 'Media',
                'mensaje': f"Engagement decreciente: {temp_cambio_porcentual:.1f}%"
            })
        if dashboard['metricas_generales']['frecuencia_semanal'] < 3:
            dashboard['alertas'].append({
                'tipo': 'FRECUENCIA',
                'severidad': 'Baja',
                'mensaje': f"Frecuencia baja: {temp_frecuencia_semanal:.1f} publicaciones/semana"
            })
        # Insights
        mejor_plataforma = max(dashboard['metricas_por_plataforma'].items(), key=lambda x: x[1]['engagement_promedio'])[0] if dashboard['metricas_por_plataforma'] else None
        if mejor_plataforma:
            dashboard['insights'].append(f"{mejor_plataforma} es la plataforma con mejor rendimiento")
        mejor_tipo = max(dashboard['metricas_por_tipo'].items(), key=lambda x: x[1]['engagement_promedio'])[0] if dashboard['metricas_por_tipo'] else None
        if mejor_tipo:
            dashboard['insights'].append(f"El tipo '{mejor_tipo}' tiene mejor engagement promedio")
        return dashboard



    def analisis_competencia_ia(self, competidores=None):
        """Análisis de competencia usando IA"""
        analisis_base = self.analisis_competitivo_avanzado(competidores)
        if self.analizador.ai and self.analizador.ai.enabled and competidores:
            try:
                datos = f"Posición: {analisis_base.get('analisis_competitivo', {}).get('posicion_mercado', {}).get('posicion', 'N/A')}"
                prompt = f"Analiza posición competitiva y genera recomendaciones estratégicas. Datos: {datos}"
                respuesta = self.analizador.ai._call_ai(prompt, system_prompt="Eres un consultor estratégico experto.", temperature=0.7, max_tokens=1000)
                if respuesta and 'error' not in respuesta.lower():
                    import json
                    try:
                        insights = json.loads(respuesta)
                        if isinstance(insights, dict):
                            analisis_base['insights_ia'] = insights
                            analisis_base['generado_con_ia'] = True
                    except: pass
            except Exception as e:
                logger.warning(f"Error IA: {e}")
        return analisis_base
    def generacion_calendario_ia(self, semanas=4, objetivos=None):
        """Genera calendario de contenido usando IA"""
        if objetivos is None:
            objetivos = ['engagement', 'alcance']
        calendario_base = self.analizador.get_optimal_posting_schedule()
        if self.analizador.ai and self.analizador.ai.enabled:
            try:
                mejor_tipo = self.analizador.identificar_mejor_tipo()
                temp_nombre = mejor_tipo.get('datos', {}).get('nombre', 'N/A') if mejor_tipo and mejor_tipo.get('datos') else 'N/A'
                datos = f"Mejor tipo: {temp_nombre}, Semanas: {semanas}"
                prompt = f"Genera calendario de contenido optimizado. Contexto: {datos}"
                respuesta = self.analizador.ai._call_ai(prompt, system_prompt="Eres experto en planificación de contenido.", temperature=0.7, max_tokens=1500)
                if respuesta and 'error' not in respuesta.lower():
                    import json
                    try:
                        calendario = json.loads(respuesta)
                        if isinstance(calendario, dict):
                            return {'semanas': semanas, 'objetivos': objetivos, 'calendario': calendario, 'generado_con_ia': True}
                    except: pass
            except Exception as e:
                logger.warning(f"Error IA: {e}")
        return {'semanas': semanas, 'objetivos': objetivos, 'calendario_base': calendario_base, 'generado_con_ia': False}


    def analisis_competencia_avanzado(
        self,
        datos_competencia: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de competencia con benchmarking
        Args:
            datos_competencia: Datos de competidores (opcional)
        Returns:
            Análisis competitivo completo
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        # Métricas propias
        engagement_promedio = statistics.mean([p.engagement_rate for p in publicaciones])
        engagement_score_promedio = statistics.mean([p.engagement_score for p in publicaciones])
        tasa_viral = sum(1 for p in publicaciones if p.es_viral) / len(publicaciones) * 100
        # Benchmarking (valores estándar de industria si no hay datos de competencia)
        benchmarks = datos_competencia or {
            'engagement_rate_promedio': 2.5,
            'engagement_score_promedio': 200,
            'tasa_viral': 5.0,
            'frecuencia_semanal': 5
        }
        # Comparación
        comparacion = {
            'engagement_rate': {
                'propio': round(engagement_promedio, 2),
                'benchmark': benchmarks.get('engagement_rate_promedio', 2.5),
                'diferencia': round(engagement_promedio - benchmarks.get('engagement_rate_promedio', 2.5), 2),
                'posicion': 'superior' if engagement_promedio > benchmarks.get('engagement_rate_promedio', 2.5) else 'inferior'
            },
            'engagement_score': {
                'propio': round(engagement_score_promedio, 1),
                'benchmark': benchmarks.get('engagement_score_promedio', 200),
                'diferencia': round(engagement_score_promedio - benchmarks.get('engagement_score_promedio', 200), 1),
                'posicion': 'superior' if engagement_score_promedio > benchmarks.get('engagement_score_promedio', 200) else 'inferior'
            },
            'tasa_viral': {
                'propio': round(tasa_viral, 1),
                'benchmark': benchmarks.get('tasa_viral', 5.0),
                'diferencia': round(tasa_viral - benchmarks.get('tasa_viral', 5.0), 1),
                'posicion': 'superior' if tasa_viral > benchmarks.get('tasa_viral', 5.0) else 'inferior'
            }
        }
        # Recomendaciones competitivas
        recomendaciones = []
        if comparacion['engagement_rate']['posicion'] == 'inferior':
            gap = abs(comparacion['engagement_rate']['diferencia'])
            recomendaciones.append({
                'tipo': 'CRITICO',
                'descripcion': f'Engagement rate {gap:.2f}% por debajo del benchmark',
                'accion': 'Optimizar contenido y timing de publicaciones'
            })
        if comparacion['tasa_viral']['posicion'] == 'inferior':
            gap = abs(comparacion['tasa_viral']['diferencia'])
            recomendaciones.append({
                'tipo': 'IMPORTANTE',
                'descripcion': f'Tasa viral {gap:.1f}% por debajo del benchmark',
                'accion': 'Crear más contenido viral y optimizar distribución'
            })
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'comparacion': comparacion,
            'recomendaciones': recomendaciones,
            'posicion_competitiva': 'lider' if sum(1 for c in comparacion.values() if c['posicion'] == 'superior') >= 2 else 'competitivo' if sum(1 for c in comparacion.values() if c['posicion'] == 'superior') >= 1 else 'mejorable'
        }
    def analisis_eficiencia_hashtags_avanzado(
        self,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de eficiencia de hashtags
        Args:
            top_n: Número de hashtags top a analizar
        Returns:
            Análisis de eficiencia de hashtags
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        # Contar hashtags y su engagement
        hashtags_stats = {}
        for pub in publicaciones:
            for hashtag in pub.hashtags:
                if hashtag not in hashtags_stats:
                    hashtags_stats[hashtag] = {
                        'frecuencia': 0,
                        'engagement_total': 0,
                        'engagement_rate_total': 0,
                        'publicaciones': []
                    }
                hashtags_stats[hashtag]['frecuencia'] += 1
                hashtags_stats[hashtag]['engagement_total'] += pub.engagement_score
                hashtags_stats[hashtag]['engagement_rate_total'] += pub.engagement_rate
                hashtags_stats[hashtag]['publicaciones'].append(pub.id)
        # Calcular métricas promedio
        for hashtag, stats in hashtags_stats.items():
            if stats['frecuencia'] > 0:
                stats['engagement_promedio'] = stats['engagement_total'] / stats['frecuencia']
                stats['engagement_rate_promedio'] = stats['engagement_rate_total'] / stats['frecuencia']
                stats['eficiencia'] = stats['engagement_rate_promedio'] * math.log(stats['frecuencia'] + 1)
        # Top hashtags por eficiencia
        top_hashtags = sorted(
            hashtags_stats.items(),
            key=lambda x: x[1]['eficiencia'],
            reverse=True
        )[:top_n]
        print(f"✅ ROI promedio proyectado: {roi_predictivo['roi_promedio_proyectado']:.1f}%")
        combinaciones_efectivas = {}
        for pub in publicaciones:
            if len(pub.hashtags) >= 2:
                # Generar pares de hashtags
                for i, h1 in enumerate(pub.hashtags):
                    for h2 in pub.hashtags[i+1:]:
                        par = tuple(sorted([h1, h2]))
                        if par not in combinaciones_efectivas:
                            combinaciones_efectivas[par] = {
                                'frecuencia': 0,
                                'engagement_promedio': 0,
                                'engagement_scores': []
                            }
                        combinaciones_efectivas[par]['frecuencia'] += 1
                        combinaciones_efectivas[par]['engagement_scores'].append(pub.engagement_score)
        # Calcular engagement promedio de combinaciones
        for par, stats in combinaciones_efectivas.items():
            if stats['engagement_scores']:
                stats['engagement_promedio'] = statistics.mean(stats['engagement_scores'])
        # Top combinaciones
        top_combinaciones = sorted(
            combinaciones_efectivas.items(),
            key=lambda x: x[1]['engagement_promedio'],
            reverse=True
        )[:10]
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'total_hashtags_unicos': len(hashtags_stats),
            'top_hashtags': [
                {
                    'hashtag': h[0],
                    'frecuencia': h[1]['frecuencia'],
                    'engagement_promedio': round(h[1]['engagement_promedio'], 1),
                    'engagement_rate_promedio': round(h[1]['engagement_rate_promedio'], 2),
                    'eficiencia': round(h[1]['eficiencia'], 2)
                }
                for h in top_hashtags
            ],
            'top_combinaciones': [
                {
                    'hashtags': list(par),
                    'frecuencia': stats['frecuencia'],
                    'engagement_promedio': round(stats['engagement_promedio'], 1)
                }
                for par, stats in top_combinaciones
            ],
            'recomendaciones': [
                f"Usar hashtags top: {', '.join([h[0] for h in top_hashtags[:5]])}",
                f"Combinaciones efectivas: {len(top_combinaciones)} pares identificados",
                "Rotar hashtags según eficiencia para mantener engagement"
            ]
        }
    def analisis_rendimiento_temporal_avanzado(
        self,
        ventana_dias: int = 30
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de rendimiento temporal
        Args:
            ventana_dias: Ventana de días para análisis
        Returns:
            Análisis de rendimiento temporal
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        fecha_limite = datetime.now() - timedelta(days=ventana_dias)
        publicaciones_periodo = [p for p in publicaciones if p.fecha_publicacion >= fecha_limite]
        if not publicaciones_periodo:
            return {"error": f"No hay publicaciones en los últimos {ventana_dias} días"}
        # Análisis por día de la semana
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        rendimiento_dias = {dia: {'publicaciones': [], 'engagement_scores': []} for dia in dias_semana}
        for pub in publicaciones_periodo:
            dia_semana = dias_semana[pub.fecha_publicacion.weekday()]
            rendimiento_dias[dia_semana]['publicaciones'].append(pub)
            rendimiento_dias[dia_semana]['engagement_scores'].append(pub.engagement_score)
        # Calcular métricas por día
        metricas_dias = {}
        for dia, datos in rendimiento_dias.items():
            if datos['publicaciones']:
                metricas_dias[dia] = {
                    'cantidad': len(datos['publicaciones']),
                    'engagement_promedio': round(statistics.mean(datos['engagement_scores']), 1),
                    'engagement_rate_promedio': round(statistics.mean([p.engagement_rate for p in datos['publicaciones']]), 2),
                    'tasa_viral': round(sum(1 for p in datos['publicaciones'] if p.es_viral) / len(datos['publicaciones']) * 100, 1)
                }
        # Mejor día
        mejor_dia = max(metricas_dias.items(), key=lambda x: x[1]['engagement_promedio'])[0] if metricas_dias else None
        # Análisis por hora
        rendimiento_horas = {}
        for pub in publicaciones_periodo:
            hora = pub.fecha_publicacion.hour
            if hora not in rendimiento_horas:
                rendimiento_horas[hora] = []
            rendimiento_horas[hora].append(pub.engagement_score)
        metricas_horas = {}
        for hora, scores in rendimiento_horas.items():
            metricas_horas[hora] = {
                'cantidad': len(scores),
                'engagement_promedio': round(statistics.mean(scores), 1)
            }
        mejor_hora = max(metricas_horas.items(), key=lambda x: x[1]['engagement_promedio'])[0] if metricas_horas else None
        # Tendencias semanales
        semanas = {}
        for pub in publicaciones_periodo:
            semana = pub.fecha_publicacion.isocalendar()[1]
            año = pub.fecha_publicacion.year
            key = f"{año}-W{semana:02d}"
            if key not in semanas:
                semanas[key] = []
            semanas[key].append(pub.engagement_score)
        tendencias_semanales = []
        for semana_key in sorted(semanas.keys()):
            scores = semanas[semana_key]
            tendencias_semanales.append({
                'semana': semana_key,
                'engagement_promedio': round(statistics.mean(scores), 1),
                'cantidad': len(scores)
            })
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'ventana_dias': ventana_dias,
            'rendimiento_por_dia': metricas_dias,
            'mejor_dia': mejor_dia,
            'rendimiento_por_hora': metricas_horas,
            'mejor_hora': mejor_hora,
            'tendencias_semanales': tendencias_semanales,
            'recomendaciones': [
                f"Mejor día para publicar: {mejor_dia}" if mejor_dia else "",
                f"Mejor hora para publicar: {mejor_hora}:00" if mejor_hora else "",
                "Ajustar calendario según patrones identificados"
            ]
        }
    def analisis_contenido_viral_profundo(
        self,
        umbral_viral: float = 10.0
    ) -> Dict[str, Any]:
        """
        Análisis profundo de contenido viral
        Args:
            umbral_viral: Umbral de engagement rate para considerar viral
        Returns:
            Análisis profundo de contenido viral
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        # Identificar contenido viral
        contenido_viral = [p for p in publicaciones if p.engagement_rate >= umbral_viral or p.es_viral]
        if not contenido_viral:
            return {
                "mensaje": f"No se encontró contenido viral (umbral: {umbral_viral}%)",
                "total_publicaciones": len(publicaciones),
                "contenido_viral": 0
            }
        # Análisis de características comunes
        hashtags_virales = []
        tipos_virales = {}
        plataformas_virales = {}
        horarios_virales = []
        longitudes_virales = []
        for pub in contenido_viral:
            hashtags_virales.extend(pub.hashtags)
            tipos_virales[pub.tipo_contenido] = tipos_virales.get(pub.tipo_contenido, 0) + 1
            plataformas_virales[pub.plataforma] = plataformas_virales.get(pub.plataforma, 0) + 1
            horarios_virales.append(pub.fecha_publicacion.hour)
            longitudes_virales.append(len(pub.titulo))
        # Hashtags más frecuentes en contenido viral
        hashtags_frecuencia = {}
        for hashtag in hashtags_virales:
            hashtags_frecuencia[hashtag] = hashtags_frecuencia.get(hashtag, 0) + 1
        top_hashtags_virales = sorted(hashtags_frecuencia.items(), key=lambda x: x[1], reverse=True)[:10]
        # Horario óptimo
        horario_optimo = statistics.mode(horarios_virales) if horarios_virales else None
        longitud_optima = round(statistics.mean(longitudes_virales)) if longitudes_virales else 0
        # Comparación con contenido no viral
        contenido_no_viral = [p for p in publicaciones if p not in contenido_viral]
        engagement_viral = statistics.mean([p.engagement_rate for p in contenido_viral])
        engagement_no_viral = statistics.mean([p.engagement_rate for p in contenido_no_viral]) if contenido_no_viral else 0
        diferencia = engagement_viral - engagement_no_viral
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'total_publicaciones': len(publicaciones),
            'contenido_viral': {
                'cantidad': len(contenido_viral),
                'porcentaje': round(len(contenido_viral) / len(publicaciones) * 100, 1),
                'engagement_promedio': round(engagement_viral, 2),
                'engagement_score_promedio': round(statistics.mean([p.engagement_score for p in contenido_viral]), 1)
            },
            'caracteristicas_comunes': {
                'tipos_mas_virales': dict(sorted(tipos_virales.items(), key=lambda x: x[1], reverse=True)[:5]),
                'plataformas_mas_virales': dict(sorted(plataformas_virales.items(), key=lambda x: x[1], reverse=True)[:5]),
                'horario_optimo': horario_optimo,
                'longitud_optima': longitud_optima,
                'top_hashtags': [{'hashtag': h[0], 'frecuencia': h[1]} for h in top_hashtags_virales]
            },
            'comparacion': {
                'diferencia_engagement': round(diferencia, 2),
                'multiplicador': round(engagement_viral / engagement_no_viral, 2) if engagement_no_viral > 0 else 0
            },
            'recomendaciones': [
                f"Contenido viral representa {len(contenido_viral)} publicaciones ({len(contenido_viral)/len(publicaciones)*100:.1f}%)",
                f"Engagement viral: {engagement_viral:.2f}% vs {engagement_no_viral:.2f}% (diferencia: {diferencia:.2f}%)",
                f"Horario óptimo para contenido viral: {horario_optimo}:00" if horario_optimo else "",
                f"Usar hashtags virales: {', '.join([h[0] for h in top_hashtags_virales[:5]])}"
            ]
        }
    def sistema_prediccion_engagement_ia(
        self,
        caracteristicas_contenido: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sistema de predicción de engagement usando IA basado en características
        Args:
            caracteristicas_contenido: Diccionario con características del contenido
        Returns:
            Predicción de engagement
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para entrenar el modelo"}
        # Extraer características del contenido
        tipo_contenido = caracteristicas_contenido.get('tipo_contenido', 'desconocido')
        plataforma = caracteristicas_contenido.get('plataforma', 'instagram')
        num_hashtags = caracteristicas_contenido.get('num_hashtags', 10)
        longitud_titulo = caracteristicas_contenido.get('longitud_titulo', 100)
        tiene_media = caracteristicas_contenido.get('tiene_media', True)
        # Buscar publicaciones similares
        publicaciones_similares = [
            p for p in publicaciones
            if p.tipo_contenido == tipo_contenido
            and p.plataforma == plataforma
            and abs(len(p.hashtags) - num_hashtags) <= 3
            and abs(len(p.titulo) - longitud_titulo) <= 50
            and p.tiene_media == tiene_media
        ]
        if not publicaciones_similares:
            # Buscar con criterios más flexibles
            publicaciones_similares = [
                p for p in publicaciones
                if p.tipo_contenido == tipo_contenido and p.plataforma == plataforma
            ]
        if not publicaciones_similares:
            # Usar todas las publicaciones
            publicaciones_similares = publicaciones
        # Calcular predicción basada en promedio
        engagement_predicho = statistics.mean([p.engagement_rate for p in publicaciones_similares])
        engagement_score_predicho = statistics.mean([p.engagement_score for p in publicaciones_similares])
        # Calcular confianza basada en número de publicaciones similares
        confianza = min(100, len(publicaciones_similares) * 5) if len(publicaciones_similares) < 20 else 95
        # Rango de predicción (intervalo de confianza)
        if len(publicaciones_similares) > 1:
            std_dev = statistics.stdev([p.engagement_rate for p in publicaciones_similares])
            rango_min = max(0, engagement_predicho - std_dev)
            rango_max = engagement_predicho + std_dev
        else:
            rango_min = engagement_predicho * 0.8
            rango_max = engagement_predicho * 1.2
        return {
            'fecha_prediccion': datetime.now().isoformat(),
            'caracteristicas_analizadas': caracteristicas_contenido,
            'prediccion': {
                'engagement_rate': round(engagement_predicho, 2),
                'engagement_score': round(engagement_score_predicho, 1),
                'rango_min': round(rango_min, 2),
                'rango_max': round(rango_max, 2),
                'confianza': round(confianza, 1)
            },
            'basado_en': {
                'publicaciones_similares': len(publicaciones_similares),
                'engagement_promedio_similares': round(statistics.mean([p.engagement_rate for p in publicaciones_similares]), 2)
            },
            'recomendaciones': [
                f"Engagement predicho: {engagement_predicho:.2f}% (confianza: {confianza:.1f}%)",
                f"Rango esperado: {rango_min:.2f}% - {rango_max:.2f}%",
                "Ajustar características para mejorar predicción" if confianza < 70 else "Predicción basada en datos sólidos"
            ]
        }
    def analisis_audiencia_segmentada_avanzado(
        self,
        criterios_segmentacion: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de audiencia segmentada
        Args:
            criterios_segmentacion: Lista de criterios para segmentar (plataforma, tipo, viral, etc.)
        Returns:
            Análisis de audiencia segmentada
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        criterios = criterios_segmentacion or ['plataforma', 'tipo_contenido', 'viral']
        segmentos = {}
        # Segmentación por plataforma
        if 'plataforma' in criterios:
            plataformas = list(set([p.plataforma for p in publicaciones]))
            segmentos['plataforma'] = {}
            for plataforma in plataformas:
                pubs_plataforma = [p for p in publicaciones if p.plataforma == plataforma]
                segmentos['plataforma'][plataforma] = {
                    'cantidad': len(pubs_plataforma),
                    'engagement_promedio': round(statistics.mean([p.engagement_rate for p in pubs_plataforma]), 2),
                    'engagement_score_promedio': round(statistics.mean([p.engagement_score for p in pubs_plataforma]), 1),
                    'tasa_viral': round(sum(1 for p in pubs_plataforma if p.es_viral) / len(pubs_plataforma) * 100, 1)
                }
        # Segmentación por tipo de contenido
        if 'tipo_contenido' in criterios:
            tipos = list(set([p.tipo_contenido for p in publicaciones]))
            segmentos['tipo_contenido'] = {}
            for tipo in tipos:
                pubs_tipo = [p for p in publicaciones if p.tipo_contenido == tipo]
                segmentos['tipo_contenido'][tipo] = {
                    'cantidad': len(pubs_tipo),
                    'engagement_promedio': round(statistics.mean([p.engagement_rate for p in pubs_tipo]), 2),
                    'engagement_score_promedio': round(statistics.mean([p.engagement_score for p in pubs_tipo]), 1),
                    'tasa_viral': round(sum(1 for p in pubs_tipo if p.es_viral) / len(pubs_tipo) * 100, 1)
                }
        # Segmentación por contenido viral
        if 'viral' in criterios:
            contenido_viral = [p for p in publicaciones if p.es_viral]
            contenido_no_viral = [p for p in publicaciones if not p.es_viral]
            segmentos['viral'] = {
                'viral': {
                    'cantidad': len(contenido_viral),
                    'engagement_promedio': round(statistics.mean([p.engagement_rate for p in contenido_viral]), 2) if contenido_viral else 0,
                    'engagement_score_promedio': round(statistics.mean([p.engagement_score for p in contenido_viral]), 1) if contenido_viral else 0
                },
                'no_viral': {
                    'cantidad': len(contenido_no_viral),
                    'engagement_promedio': round(statistics.mean([p.engagement_rate for p in contenido_no_viral]), 2) if contenido_no_viral else 0,
                    'engagement_score_promedio': round(statistics.mean([p.engagement_score for p in contenido_no_viral]), 1) if contenido_no_viral else 0
                }
            }
        # Identificar mejores segmentos
        mejores_segmentos = {}
        for criterio, datos in segmentos.items():
            if isinstance(datos, dict):
                mejor = max(datos.items(), key=lambda x: x[1].get('engagement_promedio', 0) if isinstance(x[1], dict) else 0)
                mejores_segmentos[criterio] = {
                    'segmento': mejor[0],
                    'engagement_promedio': mejor[1].get('engagement_promedio', 0) if isinstance(mejor[1], dict) else 0
                }
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'criterios_utilizados': criterios,
            'segmentos': segmentos,
            'mejores_segmentos': mejores_segmentos,
            'recomendaciones': [
                f"Mejor segmento por {criterio}: {datos['segmento']} ({datos['engagement_promedio']:.2f}% engagement)"
                for criterio, datos in mejores_segmentos.items()
            ]
        }
    def optimizacion_automatica_hashtags_ia(
        self,
        tipo_contenido: str,
        plataforma: str,
        num_hashtags: int = 10
    ) -> Dict[str, Any]:
        """
        Optimización automática de hashtags usando IA
        Args:
            tipo_contenido: Tipo de contenido
            plataforma: Plataforma objetivo
            num_hashtags: Número de hashtags a recomendar
        Returns:
            Hashtags optimizados
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        # Filtrar publicaciones similares
        publicaciones_similares = [
            p for p in publicaciones
            if p.tipo_contenido == tipo_contenido and p.plataforma == plataforma
        ]
        if not publicaciones_similares:
            publicaciones_similares = publicaciones
        # Analizar hashtags más efectivos
        hashtags_stats = {}
        for pub in publicaciones_similares:
            for hashtag in pub.hashtags:
                if hashtag not in hashtags_stats:
                    hashtags_stats[hashtag] = {
                        'frecuencia': 0,
                        'engagement_total': 0,
                        'publicaciones': []
                    }
                hashtags_stats[hashtag]['frecuencia'] += 1
                hashtags_stats[hashtag]['engagement_total'] += pub.engagement_score
                hashtags_stats[hashtag]['publicaciones'].append(pub.id)
        # Calcular score de efectividad
        for hashtag, stats in hashtags_stats.items():
            if stats['frecuencia'] > 0:
                stats['engagement_promedio'] = stats['engagement_total'] / stats['frecuencia']
                # Score combinado: engagement promedio * log(frecuencia) para balancear
                stats['score_efectividad'] = stats['engagement_promedio'] * math.log(stats['frecuencia'] + 1)
        # Top hashtags
        top_hashtags = sorted(
            hashtags_stats.items(),
            key=lambda x: x[1]['score_efectividad'],
            reverse=True
        )[:num_hashtags]
        # Análisis de combinaciones
        combinaciones_efectivas = {}
        for pub in publicaciones_similares:
            if len(pub.hashtags) >= 2 and pub.engagement_rate > statistics.mean([p.engagement_rate for p in publicaciones_similares]):
                # Publicación exitosa con múltiples hashtags
                for i, h1 in enumerate(pub.hashtags):
                    for h2 in pub.hashtags[i+1:]:
                        par = tuple(sorted([h1, h2]))
                        if par not in combinaciones_efectivas:
                            combinaciones_efectivas[par] = []
                        combinaciones_efectivas[par].append(pub.engagement_score)
        # Calcular engagement promedio de combinaciones
        combinaciones_stats = {}
        for par, scores in combinaciones_efectivas.items():
            if len(scores) >= 2:  # Al menos 2 ocurrencias
                combinaciones_stats[par] = {
                    'engagement_promedio': statistics.mean(scores),
                    'frecuencia': len(scores)
                }
        top_combinaciones = sorted(
            combinaciones_stats.items(),
            key=lambda x: x[1]['engagement_promedio'],
            reverse=True
        )[:5]
        return {
            'fecha_optimizacion': datetime.now().isoformat(),
            'tipo_contenido': tipo_contenido,
            'plataforma': plataforma,
            'hashtags_recomendados': [
                {
                    'hashtag': h[0],
                    'score_efectividad': round(h[1]['score_efectividad'], 1),
                    'engagement_promedio': round(h[1]['engagement_promedio'], 1),
                    'frecuencia': h[1]['frecuencia']
                }
                for h in top_hashtags
            ],
            'combinaciones_efectivas': [
                {
                    'hashtags': list(par),
                    'engagement_promedio': round(stats['engagement_promedio'], 1),
                    'frecuencia': stats['frecuencia']
                }
                for par, stats in top_combinaciones
            ],
            'recomendaciones': [
                f"Usar {num_hashtags} hashtags optimizados para {tipo_contenido} en {plataforma}",
                f"Top hashtag: {top_hashtags[0][0]} (score: {round(top_hashtags[0][1]['score_efectividad'], 1)})" if top_hashtags else "",
                f"Combinaciones efectivas identificadas: {len(top_combinaciones)}"
            ]
        }
    def analisis_tendencias_hashtags_temporal(
        self,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """
        Análisis temporal de tendencias de hashtags
        Args:
            periodo_dias: Período en días para analizar tendencias
        Returns:
            Análisis de tendencias de hashtags
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        fecha_limite = datetime.now() - timedelta(days=periodo_dias)
        publicaciones_periodo = [p for p in publicaciones if p.fecha_publicacion >= fecha_limite]
        if not publicaciones_periodo:
            return {"error": f"No hay publicaciones en los últimos {periodo_dias} días"}
        # Dividir en períodos (semanas)
        num_semanas = periodo_dias // 7
        if num_semanas < 2:
            num_semanas = 2
        hashtags_por_semana = {}
        for semana in range(num_semanas):
            inicio_semana = fecha_limite + timedelta(days=semana * 7)
            fin_semana = fecha_limite + timedelta(days=(semana + 1) * 7)
            pubs_semana = [
                p for p in publicaciones_periodo
                if inicio_semana <= p.fecha_publicacion < fin_semana
            ]
            hashtags_semana = {}
            for pub in pubs_semana:
                for hashtag in pub.hashtags:
                    if hashtag not in hashtags_semana:
                        hashtags_semana[hashtag] = {
                            'frecuencia': 0,
                            'engagement_total': 0
                        }
                    hashtags_semana[hashtag]['frecuencia'] += 1
                    hashtags_semana[hashtag]['engagement_total'] += pub.engagement_score
            hashtags_por_semana[f'Semana {semana + 1}'] = hashtags_semana
        # Identificar hashtags en crecimiento
        hashtags_crecimiento = {}
        for semana_key in list(hashtags_por_semana.keys())[:-1]:
            semana_actual = hashtags_por_semana[semana_key]
            semana_siguiente_key = list(hashtags_por_semana.keys())[list(hashtags_por_semana.keys()).index(semana_key) + 1]
            semana_siguiente = hashtags_por_semana[semana_siguiente_key]
            for hashtag in set(list(semana_actual.keys()) + list(semana_siguiente.keys())):
                freq_actual = semana_actual.get(hashtag, {}).get('frecuencia', 0)
                freq_siguiente = semana_siguiente.get(hashtag, {}).get('frecuencia', 0)
                if freq_actual > 0 and freq_siguiente > freq_actual:
                    crecimiento = ((freq_siguiente - freq_actual) / freq_actual) * 100
                    if hashtag not in hashtags_crecimiento:
                        hashtags_crecimiento[hashtag] = []
                    hashtags_crecimiento[hashtag].append(crecimiento)
        # Calcular crecimiento promedio
        hashtags_crecimiento_promedio = {}
        for hashtag, crecimientos in hashtags_crecimiento.items():
            hashtags_crecimiento_promedio[hashtag] = statistics.mean(crecimientos)
        top_crecimiento = sorted(
            hashtags_crecimiento_promedio.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'periodo_dias': periodo_dias,
            'hashtags_por_semana': {
                semana: {
                    hashtag: {
                        'frecuencia': stats['frecuencia'],
                        'engagement_promedio': round(stats['engagement_total'] / stats['frecuencia'], 1) if stats['frecuencia'] > 0 else 0
                    }
                    for hashtag, stats in datos.items()
                }
                for semana, datos in hashtags_por_semana.items()
            },
            'hashtags_en_crecimiento': [
                {
                    'hashtag': h[0],
                    'crecimiento_promedio': round(h[1], 1)
                }
                for h in top_crecimiento
            ],
            'recomendaciones': [
                f"Hashtags en crecimiento: {', '.join([h[0] for h in top_crecimiento[:5]])}",
                "Considerar usar hashtags en tendencia para mayor visibilidad"
            ]
        }
    def sistema_alertas_inteligentes_avanzado(
        self,
        umbrales_personalizados: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Sistema avanzado de alertas inteligentes
        Args:
            umbrales_personalizados: Umbrales personalizados para alertas
        Returns:
            Sistema de alertas inteligentes
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        umbrales = umbrales_personalizados or {
            'engagement_bajo': 1.0,
            'engagement_decreciente': -10.0,
            'frecuencia_baja': 2.0,
            'tasa_viral_baja': 2.0
        }
        alertas = []
        # Análisis de engagement
        engagement_promedio = statistics.mean([p.engagement_rate for p in publicaciones])
        if engagement_promedio < umbrales['engagement_bajo']:
            umbral_engagement_bajo = umbrales.get('engagement_bajo', 1.0)
            alertas.append({
                'tipo': 'CRITICO',
                'categoria': 'Engagement',
                'titulo': 'Engagement por debajo del umbral',
                'descripcion': f'Engagement promedio ({engagement_promedio:.2f}%) está por debajo del umbral ({umbral_engagement_bajo}%)',
                'accion': 'Revisar estrategia de contenido y optimizar publicaciones',
                'prioridad': 1
            })
        # Análisis de tendencia
        if len(publicaciones) >= 10:
            publicaciones_ordenadas = sorted(publicaciones, key=lambda p: p.fecha_publicacion)
            primera_mitad = publicaciones_ordenadas[:len(publicaciones_ordenadas)//2]
            segunda_mitad = publicaciones_ordenadas[len(publicaciones_ordenadas)//2:]
            engagement_primera = statistics.mean([p.engagement_rate for p in primera_mitad])
            engagement_segunda = statistics.mean([p.engagement_rate for p in segunda_mitad])
            cambio_porcentual = ((engagement_segunda - engagement_primera) / engagement_primera * 100) if engagement_primera > 0 else 0
            if cambio_porcentual < umbrales['engagement_decreciente']:
                alertas.append({
                    'tipo': 'ALTA',
                    'categoria': 'Tendencia',
                    'titulo': 'Engagement decreciente',
                    'descripcion': f'Engagement ha disminuido {abs(cambio_porcentual):.1f}% en el período reciente',
                    'accion': 'Analizar causas y ajustar estrategia',
                    'prioridad': 2
                })
        # Análisis de frecuencia
        if publicaciones:
            fecha_mas_antigua = min(p.fecha_publicacion for p in publicaciones)
            dias_totales = (datetime.now() - fecha_mas_antigua).days
            frecuencia_semanal = len(publicaciones) / (dias_totales / 7) if dias_totales > 0 else 0
            if frecuencia_semanal < umbrales['frecuencia_baja']:
                alertas.append({
                    'tipo': 'MEDIA',
                    'categoria': 'Frecuencia',
                    'titulo': 'Frecuencia de publicación baja',
                    'descripcion': f'Frecuencia actual: {frecuencia_semanal:.1f} publicaciones/semana (óptimo: {umbrales.get('frecuencia_baja')}+)',
                    'accion': 'Incrementar frecuencia de publicaciones',
                    'prioridad': 3
                })
        # Análisis de tasa viral
        tasa_viral = sum(1 for p in publicaciones if p.es_viral) / len(publicaciones) * 100
        if tasa_viral < umbrales['tasa_viral_baja']:
            alertas.append({
                'tipo': 'MEDIA',
                'categoria': 'Viralidad',
                'titulo': 'Tasa viral baja',
                'descripcion': f'Tasa viral actual: {tasa_viral:.1f}% (óptimo: {umbrales.get('tasa_viral_baja')}%+)',
                'accion': 'Crear más contenido viral y optimizar distribución',
                'prioridad': 3
            })
        # Ordenar por prioridad
        alertas_ordenadas = sorted(alertas, key=lambda x: x['prioridad'])
        return {
            'fecha_generacion': datetime.now().isoformat(),
            'total_alertas': len(alertas_ordenadas),
            'alertas_criticas': [a for a in alertas_ordenadas if a['tipo'] == 'CRITICO'],
            'alertas_altas': [a for a in alertas_ordenadas if a['tipo'] == 'ALTA'],
            'alertas_medias': [a for a in alertas_ordenadas if a['tipo'] == 'MEDIA'],
            'alertas': alertas_ordenadas,
            'resumen': {
                'engagement_promedio': round(engagement_promedio, 2),
                'frecuencia_semanal': round(frecuencia_semanal, 1) if 'frecuencia_semanal' in locals() else 0,
                'tasa_viral': round(tasa_viral, 1)
            }
        }
    def analisis_roi_contenido_avanzado(
        self,
        costo_por_publicacion: float = 10.0,
        valor_por_engagement: float = 0.1
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de ROI por contenido
        Args:
            costo_por_publicacion: Costo estimado por publicación
            valor_por_engagement: Valor estimado por punto de engagement
        Returns:
            Análisis de ROI por contenido
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        # Calcular ROI por publicación
        roi_publicaciones = []
        for pub in publicaciones:
            valor_generado = pub.engagement_score * valor_por_engagement
            costo = costo_por_publicacion
            roi = ((valor_generado - costo) / costo * 100) if costo > 0 else 0
            roi_publicaciones.append({
                'publicacion_id': pub.id,
                'titulo': pub.titulo[:50],
                'costo': costo,
                'valor_generado': round(valor_generado, 2),
                'roi': round(roi, 2),
                'engagement_score': pub.engagement_score
            })
        # ROI por tipo de contenido
        roi_por_tipo = {}
        for pub in publicaciones:
            tipo = pub.tipo_contenido
            if tipo not in roi_por_tipo:
                roi_por_tipo[tipo] = {
                    'costo_total': 0,
                    'valor_total': 0,
                    'publicaciones': 0
                }
            roi_por_tipo[tipo]['costo_total'] += costo_por_publicacion
            roi_por_tipo[tipo]['valor_total'] += pub.engagement_score * valor_por_engagement
            roi_por_tipo[tipo]['publicaciones'] += 1
        # Calcular ROI promedio por tipo
        roi_tipos = {}
        for tipo, datos in roi_por_tipo.items():
            roi = ((datos['valor_total'] - datos['costo_total']) / datos['costo_total'] * 100) if datos['costo_total'] > 0 else 0
            roi_tipos[tipo] = {
                'roi_promedio': round(roi, 2),
                'publicaciones': datos['publicaciones'],
                'valor_total': round(datos['valor_total'], 2),
                'costo_total': round(datos['costo_total'], 2)
            }
        # Mejor tipo por ROI
        mejor_tipo_roi = max(roi_tipos.items(), key=lambda x: x[1]['roi_promedio'])[0] if roi_tipos else None
        # ROI total
        costo_total = len(publicaciones) * costo_por_publicacion
        valor_total = sum(p.engagement_score for p in publicaciones) * valor_por_engagement
        roi_total = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
        # Top publicaciones por ROI
        top_roi = sorted(roi_publicaciones, key=lambda x: x['roi'], reverse=True)[:10]
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'parametros': {
                'costo_por_publicacion': costo_por_publicacion,
                'valor_por_engagement': valor_por_engagement
            },
            'roi_total': {
                'costo_total': round(costo_total, 2),
                'valor_total': round(valor_total, 2),
                'roi': round(roi_total, 2)
            },
            'roi_por_tipo': roi_tipos,
            'mejor_tipo_roi': mejor_tipo_roi,
            'top_publicaciones_roi': top_roi,
            'recomendaciones': [
                f"ROI total: {roi_total:.2f}%",
                f"Mejor tipo por ROI: {mejor_tipo_roi} ({temp_roi_promedio:.2f}%)" if mejor_tipo_roi else "",
                "Incrementar contenido del tipo con mejor ROI",
                f"Top publicación ROI: {temp_roi:.2f}%" if top_roi else ""
            ]
        }
    def generacion_estrategia_contenido_ia(
        self,
        objetivos: List[str],
        periodo_semanas: int = 4
    ) -> Dict[str, Any]:
        """
        Generación de estrategia de contenido usando IA
        Args:
            objetivos: Lista de objetivos (engagement, viral, roi, crecimiento)
            periodo_semanas: Período en semanas para la estrategia
        Returns:
            Estrategia de contenido generada
        """
        publicaciones = self.analizador.publicaciones
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        estrategia = {
            'fecha_generacion': datetime.now().isoformat(),
            'objetivos': objetivos,
            'periodo_semanas': periodo_semanas,
            'recomendaciones_estrategicas': [],
            'calendario_sugerido': [],
            'metricas_objetivo': {}
        }
        # Análisis según objetivos
        if 'engagement' in objetivos:
            # Identificar mejor tipo de contenido
            tipos = {}
            for pub in publicaciones:
                if pub.tipo_contenido not in tipos:
                    tipos[pub.tipo_contenido] = []
                tipos[pub.tipo_contenido].append(pub.engagement_rate)
            mejor_tipo = max(tipos.items(), key=lambda x: statistics.mean(x[1]))[0] if tipos else None
            if mejor_tipo:
                estrategia['recomendaciones_estrategicas'].append({
                    'objetivo': 'engagement',
                    'prioridad': 'ALTA',
                    'accion': f"Incrementar contenido tipo '{mejor_tipo}'",
                    'razon': f"Tiene {round(statistics.mean(tipos[mejor_tipo]), 2)}% engagement promedio"
                })
        if 'viral' in objetivos:
            publicaciones_virales = [p for p in publicaciones if p.es_viral]
            if publicaciones_virales:
                # Características de contenido viral
                hashtags_virales = []
                for pub in publicaciones_virales:
                    hashtags_virales.extend(pub.hashtags)
                hashtags_frecuencia = {}
                for hashtag in hashtags_virales:
                    hashtags_frecuencia[hashtag] = hashtags_frecuencia.get(hashtag, 0) + 1
                top_hashtags = sorted(hashtags_frecuencia.items(), key=lambda x: x[1], reverse=True)[:5]
                estrategia['recomendaciones_estrategicas'].append({
                    'objetivo': 'viral',
                    'prioridad': 'ALTA',
                    'accion': f"Usar hashtags virales: {', '.join([h[0] for h in top_hashtags])}",
                    'razon': 'Estos hashtags aparecen frecuentemente en contenido viral'
                })
        if 'crecimiento' in objetivos:
            # Análisis de tendencias
            if len(publicaciones) >= 10:
                publicaciones_ordenadas = sorted(publicaciones, key=lambda p: p.fecha_publicacion)
                primera_mitad = publicaciones_ordenadas[:len(publicaciones_ordenadas)//2]
                segunda_mitad = publicaciones_ordenadas[len(publicaciones_ordenadas)//2:]
                engagement_primera = statistics.mean([p.engagement_rate for p in primera_mitad])
                engagement_segunda = statistics.mean([p.engagement_rate for p in segunda_mitad])
                if engagement_segunda > engagement_primera:
                    crecimiento = ((engagement_segunda - engagement_primera) / engagement_primera * 100) if engagement_primera > 0 else 0
                    estrategia['recomendaciones_estrategicas'].append({
                        'objetivo': 'crecimiento',
                        'prioridad': 'MEDIA',
                        'accion': 'Mantener estrategia actual',
                        'razon': f'Crecimiento positivo de {crecimiento:.1f}%'
                    })
                else:
                    estrategia['recomendaciones_estrategicas'].append({
                        'objetivo': 'crecimiento',
                        'prioridad': 'ALTA',
                        'accion': 'Ajustar estrategia para revertir tendencia',
                        'razon': 'Engagement en declive'
                    })
        # Generar calendario sugerido
        frecuencia_semanal = len(publicaciones) / ((datetime.now() - min(p.fecha_publicacion for p in publicaciones)).days / 7) if publicaciones else 0
        frecuencia_objetivo = max(5, round(frecuencia_semanal))
        fecha_inicio = datetime.now()
        for semana in range(periodo_semanas):
            for dia in range(7):
                fecha = fecha_inicio + timedelta(weeks=semana, days=dia)
                if fecha.weekday() < 5:  # Lunes a Viernes
                    estrategia['calendario_sugerido'].append({
                        'fecha': fecha.isoformat(),
                        'tipo_contenido': mejor_tipo if 'mejor_tipo' in locals() else 'variado',
                        'plataforma': 'instagram',
                        'prioridad': 'ALTA' if dia % 2 == 0 else 'MEDIA'
                    })
        # Métricas objetivo
        engagement_actual = statistics.mean([p.engagement_rate for p in publicaciones])
        estrategia['metricas_objetivo'] = {
            'engagement_actual': round(engagement_actual, 2),
            'engagement_objetivo': round(engagement_actual * 1.2, 2),  # 20% de mejora
            'frecuencia_semanal_objetivo': frecuencia_objetivo
        }
        return estrategia

    def analisis_competencia_benchmark_avanzado(
        self,
        benchmarks_industria: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de competencia y benchmarks de industria
        
        Args:
            benchmarks_industria: Benchmarks personalizados de la industria
        
        Returns:
            Análisis comparativo con benchmarks
        """
        publicaciones = self.analizador.publicaciones
        
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Benchmarks por defecto
        benchmarks = benchmarks_industria or {
            'engagement_rate': 3.0,
            'engagement_score': 50.0,
            'tasa_viral': 5.0,
            'frecuencia_semanal': 5.0
        }
        
        # Calcular métricas actuales
        engagement_promedio = statistics.mean([p.engagement_rate for p in publicaciones])
        engagement_score_promedio = statistics.mean([p.engagement_score for p in publicaciones])
        tasa_viral = sum(1 for p in publicaciones if p.es_viral) / len(publicaciones) * 100
        
        fecha_mas_antigua = min(p.fecha_publicacion for p in publicaciones)
        dias_totales = (datetime.now() - fecha_mas_antigua).days
        frecuencia_semanal = len(publicaciones) / (dias_totales / 7) if dias_totales > 0 else 0
        
        # Comparar con benchmarks
        comparacion = {
            'engagement_rate': {
                'actual': round(engagement_promedio, 2),
                'benchmark': benchmarks['engagement_rate'],
                'diferencia': round(engagement_promedio - benchmarks['engagement_rate'], 2),
                'porcentaje_diferencia': round(((engagement_promedio - benchmarks['engagement_rate']) / benchmarks['engagement_rate'] * 100) if benchmarks['engagement_rate'] > 0 else 0, 2),
                'estado': 'ARRIBA' if engagement_promedio >= benchmarks['engagement_rate'] else 'DEBAJO'
            },
            'engagement_score': {
                'actual': round(engagement_score_promedio, 2),
                'benchmark': benchmarks['engagement_score'],
                'diferencia': round(engagement_score_promedio - benchmarks['engagement_score'], 2),
                'porcentaje_diferencia': round(((engagement_score_promedio - benchmarks['engagement_score']) / benchmarks['engagement_score'] * 100) if benchmarks['engagement_score'] > 0 else 0, 2),
                'estado': 'ARRIBA' if engagement_score_promedio >= benchmarks['engagement_score'] else 'DEBAJO'
            },
            'tasa_viral': {
                'actual': round(tasa_viral, 2),
                'benchmark': benchmarks['tasa_viral'],
                'diferencia': round(tasa_viral - benchmarks['tasa_viral'], 2),
                'porcentaje_diferencia': round(((tasa_viral - benchmarks['tasa_viral']) / benchmarks['tasa_viral'] * 100) if benchmarks['tasa_viral'] > 0 else 0, 2),
                'estado': 'ARRIBA' if tasa_viral >= benchmarks['tasa_viral'] else 'DEBAJO'
            },
            'frecuencia_semanal': {
                'actual': round(frecuencia_semanal, 2),
                'benchmark': benchmarks['frecuencia_semanal'],
                'diferencia': round(frecuencia_semanal - benchmarks['frecuencia_semanal'], 2),
                'porcentaje_diferencia': round(((frecuencia_semanal - benchmarks['frecuencia_semanal']) / benchmarks['frecuencia_semanal'] * 100) if benchmarks['frecuencia_semanal'] > 0 else 0, 2),
                'estado': 'ARRIBA' if frecuencia_semanal >= benchmarks['frecuencia_semanal'] else 'DEBAJO'
            }
        }
        
        # Generar recomendaciones
        recomendaciones = []
        for metrica, datos in comparacion.items():
            if datos['estado'] == 'DEBAJO':
                recomendaciones.append({
                    'metrica': metrica,
                    'prioridad': 'ALTA',
                    'accion': f"Incrementar {metrica} en {abs(datos['porcentaje_diferencia']):.1f}% para alcanzar benchmark",
                    'diferencia_actual': datos['diferencia']
                })
        
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'benchmarks': benchmarks,
            'comparacion': comparacion,
            'recomendaciones': recomendaciones,
            'resumen': {
                'metricas_arriba_benchmark': sum(1 for d in comparacion.values() if d['estado'] == 'ARRIBA'),
                'metricas_debajo_benchmark': sum(1 for d in comparacion.values() if d['estado'] == 'DEBAJO'),
                'score_general': round(sum(d['porcentaje_diferencia'] for d in comparacion.values()) / len(comparacion), 2)
            }
        }
    
    def sistema_optimizacion_automatica_contenido(
        self,
        objetivo: str = 'engagement'
    ) -> Dict[str, Any]:
        """
        Sistema de optimización automática de contenido
        
        Args:
            objetivo: Objetivo de optimización (engagement, viral, roi)
        
        Returns:
            Recomendaciones de optimización automática
        """
        publicaciones = self.analizador.publicaciones
        
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        optimizaciones = []
        
        if objetivo == 'engagement':
            # Analizar mejor tipo de contenido
            tipos = {}
            for pub in publicaciones:
                if pub.tipo_contenido not in tipos:
                    tipos[pub.tipo_contenido] = []
                tipos[pub.tipo_contenido].append(pub.engagement_rate)
            
            mejor_tipo = max(tipos.items(), key=lambda x: statistics.mean(x[1]))[0] if tipos else None
            
            # Analizar mejor hora
            horarios = {}
            for pub in publicaciones:
                hora = pub.fecha_publicacion.hour
                if hora not in horarios:
                    horarios[hora] = []
                horarios[hora].append(pub.engagement_rate)
            
            mejor_hora = max(horarios.items(), key=lambda x: statistics.mean(x[1]))[0] if horarios else None
            
            # Analizar mejor día
            dias = {}
            for pub in publicaciones:
                dia = pub.fecha_publicacion.strftime('%A')
                if dia not in dias:
                    dias[dia] = []
                dias[dia].append(pub.engagement_rate)
            
            mejor_dia = max(dias.items(), key=lambda x: statistics.mean(x[1]))[0] if dias else None
            
            optimizaciones.append({
                'tipo': 'CONTENIDO',
                'accion': f'Incrementar contenido tipo "{mejor_tipo}"',
                'impacto_esperado': 'ALTO',
                'razon': f'Engagement promedio: {statistics.mean(tipos[mejor_tipo]):.2f}%'
            })
            
            optimizaciones.append({
                'tipo': 'TIMING',
                'accion': f'Publicar a las {mejor_hora}:00',
                'impacto_esperado': 'MEDIO',
                'razon': f'Engagement promedio: {statistics.mean(horarios[mejor_hora]):.2f}%'
            })
            
            optimizaciones.append({
                'tipo': 'TIMING',
                'accion': f'Publicar los {mejor_dia}',
                'impacto_esperado': 'MEDIO',
                'razon': f'Engagement promedio: {statistics.mean(dias[mejor_dia]):.2f}%'
            })
        
        elif objetivo == 'viral':
            # Analizar contenido viral
            publicaciones_virales = [p for p in publicaciones if p.es_viral]
            if publicaciones_virales:
                hashtags_virales = []
                for pub in publicaciones_virales:
                    hashtags_virales.extend(pub.hashtags)
                
                hashtags_frecuencia = {}
                for hashtag in hashtags_virales:
                    hashtags_frecuencia[hashtag] = hashtags_frecuencia.get(hashtag, 0) + 1
                
                top_hashtags = sorted(hashtags_frecuencia.items(), key=lambda x: x[1], reverse=True)[:5]
                
                optimizaciones.append({
                    'tipo': 'HASHTAGS',
                    'accion': f'Usar hashtags: {", ".join([h[0] for h in top_hashtags])}',
                    'impacto_esperado': 'ALTO',
                    'razon': 'Hashtags más frecuentes en contenido viral'
                })
        
        return {
            'fecha_generacion': datetime.now().isoformat(),
            'objetivo': objetivo,
            'optimizaciones': optimizaciones,
            'total_optimizaciones': len(optimizaciones)
        }
    
    def analisis_predictivo_avanzado_ia(
        self,
        horizonte_dias: int = 30
    ) -> Dict[str, Any]:
        """
        Análisis predictivo avanzado usando IA
        
        Args:
            horizonte_dias: Días hacia el futuro para predecir
        
        Returns:
            Predicciones y proyecciones
        """
        publicaciones = self.analizador.publicaciones
        
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Análisis de tendencias
        publicaciones_ordenadas = sorted(publicaciones, key=lambda p: p.fecha_publicacion)
        
        # Calcular tendencia de engagement
        engagement_por_semana = {}
        for pub in publicaciones_ordenadas:
            semana = pub.fecha_publicacion.isocalendar()[1]
            año = pub.fecha_publicacion.year
            key = f"{año}-W{semana}"
            if key not in engagement_por_semana:
                engagement_por_semana[key] = []
            engagement_por_semana[key].append(pub.engagement_rate)
        
        # Calcular promedio por semana
        engagement_semanal = []
        for key in sorted(engagement_por_semana.keys()):
            engagement_semanal.append(statistics.mean(engagement_por_semana[key]))
        
        # Calcular tendencia (regresión lineal simple)
        if len(engagement_semanal) >= 2:
            n = len(engagement_semanal)
            x = list(range(n))
            y = engagement_semanal
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
            intercepto = (sum_y - pendiente * sum_x) / n
            
            # Proyectar hacia el futuro
            semanas_futuras = horizonte_dias // 7
            predicciones = []
            for i in range(semanas_futuras):
                semana_futura = n + i
                prediccion = pendiente * semana_futura + intercepto
                predicciones.append({
                    'semana': semana_futura,
                    'engagement_predicho': max(0, round(prediccion, 2))
                })
        else:
            predicciones = []
            pendiente = 0
        
        return {
            'fecha_analisis': datetime.now().isoformat(),
            'horizonte_dias': horizonte_dias,
            'tendencia_actual': {
                'pendiente': round(pendiente, 4),
                'direccion': 'CRECIENTE' if pendiente > 0 else 'DECRECIENTE' if pendiente < 0 else 'ESTABLE'
            },
            'predicciones': predicciones,
            'engagement_actual': round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
            'engagement_proyectado': round(predicciones[-1]['engagement_predicho'], 2) if predicciones else 0
        }
    
    def generacion_calendario_estrategico_ia(
        self,
        objetivos: List[str],
        semanas: int = 4
    ) -> Dict[str, Any]:
        """
        Generación de calendario estratégico usando IA
        
        Args:
            objetivos: Lista de objetivos (engagement, viral, crecimiento)
            semanas: Número de semanas para planificar
        
        Returns:
            Calendario estratégico generado
        """
        publicaciones = self.analizador.publicaciones
        
        if not publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        calendario = {
            'fecha_generacion': datetime.now().isoformat(),
            'objetivos': objetivos,
            'semanas': semanas,
            'publicaciones_planificadas': []
        }
        
        # Analizar mejores momentos
        horarios = {}
        dias = {}
        for pub in publicaciones:
            hora = pub.fecha_publicacion.hour
            dia = pub.fecha_publicacion.strftime('%A')
            
            if hora not in horarios:
                horarios[hora] = []
            horarios[hora].append(pub.engagement_rate)
            
            if dia not in dias:
                dias[dia] = []
            dias[dia].append(pub.engagement_rate)
        
        mejor_hora = max(horarios.items(), key=lambda x: statistics.mean(x[1]))[0] if horarios else 12
        mejor_dia = max(dias.items(), key=lambda x: statistics.mean(x[1]))[0] if dias else 'Monday'
        
        # Generar calendario
        fecha_inicio = datetime.now()
        dia_semana_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        mejor_dia_num = dia_semana_map.get(mejor_dia, 0)
        
        for semana in range(semanas):
            for dia in range(7):
                fecha = fecha_inicio + timedelta(weeks=semana, days=dia)
                if fecha.weekday() == mejor_dia_num:
                    calendario['publicaciones_planificadas'].append({
                        'fecha': fecha.isoformat(),
                        'hora': mejor_hora,
                        'tipo_contenido': 'optimizado',
                        'objetivos': objetivos,
                        'prioridad': 'ALTA'
                    })
        
        return calendario

def main():
    """Función principal para demostración"""
    import argparse
    parser = argparse.ArgumentParser(description='Análisis Avanzado V2 de Engagement')
    parser.add_argument('--publicaciones', type=int, default=50, help='Número de publicaciones')
    parser.add_argument('--alertas', action='store_true', help='Sistema de alertas predictivas')
    parser.add_argument('--roi-predictivo', action='store_true', help='Análisis de ROI predictivo')
    parser.add_argument('--ab-testing', action='store_true', help='Sistema de A/B testing')
    parser.add_argument('--sentimiento', action='store_true', help='Análisis de sentimiento')
    parser.add_argument('--oportunidades', action='store_true', help='Detección de oportunidades')
    parser.add_argument('--cross-platform', action='store_true', help='Análisis cross-platform')
    parser.add_argument('--scoring', action='store_true', help='Sistema de scoring en tiempo real')
    parser.add_argument('--tendencias', action='store_true', help='Análisis de tendencias de mercado avanzado')
    parser.add_argument('--recomendaciones', action='store_true', help='Recomendaciones inteligentes avanzadas')
    parser.add_argument('--exportar', type=str, help='Exportar reporte completo (formato: json, csv)')
    parser.add_argument('--audiencia', action='store_true', help='Análisis profundo de audiencia')
    parser.add_argument('--optimizar', action='store_true', help='Optimización automática de contenido')
    parser.add_argument('--dashboard', action='store_true', help='Dashboard de métricas en tiempo real')
    parser.add_argument('--prediccion', type=int, help='Predicción de engagement futuro (semanas)')
    parser.add_argument('--competitivo', action='store_true', help='Análisis competitivo avanzado')
    parser.add_argument('--generar-contenido', type=str, help='Generar contenido inteligente (tema)')
    parser.add_argument('--campanas', action='store_true', help='Análisis de performance de campañas')
    parser.add_argument('--recomendaciones-ai', action='store_true', help='Recomendaciones personalizadas con IA')
    parser.add_argument('--sentimiento-multi', action='store_true', help='Análisis de sentimiento multi-plataforma')
    parser.add_argument('--patrones', action='store_true', help='Detección de patrones ocultos')
    parser.add_argument('--optimizar-estrategia', action='store_true', help='Optimización automática de estrategia')
    parser.add_argument('--alertas-proactivas', action='store_true', help='Sistema de alertas proactivas')
    parser.add_argument('--reporte-completo', action='store_true', help='Generar reporte completo automático')
    parser.add_argument('--competencia-ia', action='store_true', help='Análisis de competencia con IA')
    parser.add_argument('--calendario-ia', type=int, default=4, help='Generar calendario de contenido con IA (semanas)')
    args = parser.parse_args()
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    analizador_avanzado_v2 = AnalizadorAvanzadoV2Engagement(analizador_base)
    # Alertas predictivas
    if args.alertas:
        print("🚨 Sistema de alertas predictivas...")
        print("🚨 Sistema de alertas predictivas...")
        alertas = analizador_avanzado_v2.sistema_alertas_predictivas()
        print(f"✅ {alertas['total_alertas']} alertas generadas")
        print(f"   Críticas: {len(alertas['alertas_criticas'])}")
        print(f"   Altas: {len(alertas['alertas_altas'])}")
        for alerta in alertas['alertas'][:3]:
            print(f"   [{alerta['severidad']}] {alerta['titulo']}")
            print(f"      {alerta['descripcion']}")
    # ROI predictivo
    if args.roi_predictivo:
        print("\n🏆💰Análisis de ROI predictivo avanzado...")
        roi_predictivo = analizador_avanzado_v2.analisis_roi_predictivo_avanzado(meses_proyeccion=6)
        print(f"✅ ROI promedio proyectado: {roi_predictivo['roi_promedio_proyectado']:.1f}%")
        print(f"   Tendencia: {roi_predictivo['tendencia_roi']}")
        if roi_predictivo.get('break_even_proyectado'):
            be = roi_predictivo['break_even_proyectado']
            print(f"   Break-even proyectado: Mes {be['mes']}")
    # A/B testing
    if args.ab_testing:
        print("\n🏆 🧪 Sistema de A/B testing automatizado...")
        variantes = [
            {"nombre": "Variante A", "tipo_contenido": "Y", "hora": 10},
            {"nombre": "Variante B", "tipo_contenido": "Y", "hora": 14}
        ]
        resultado_ab = analizador_avanzado_v2.sistema_ab_testing_automatizado(variantes)
        print(f"✅ Test completado")
        print(f"   Ganador: {temp_variante}")
        print(f"   Engagement: {temp_engagement_promedio:.1f}")
        print(f"   Recomendación: {resultado_ab['recomendacion']}")
    # Sentimiento
    if args.sentimiento:
        print("\n🏆😊Análisis de sentimiento avanzado...")
        texto = "Este producto es excelente, me encanta la calidad. El precio es un poco caro pero vale la pena."
        sentimiento = analizador_avanzado_v2.analisis_sentimiento_avanzado(texto)
        print(f"✅ Sentimiento: {sentimiento['sentimiento']}")
        print(f"   Score: {sentimiento['score_sentimiento']:.1f}")
        print(f"   Confianza: {sentimiento['confianza']:.1f}%")
    # Oportunidades
    if args.oportunidades:
        print("\n🏆 💡 Detección de oportunidades de contenido...")
        oportunidades = analizador_avanzado_v2.deteccion_oportunidades_contenido()
        print(f"✅ {oportunidades['total_oportunidades']} oportunidades detectadas")
        for op in oportunidades['oportunidades'][:3]:
            print(f" [{op['prioridad']}] {op['descripcion']}")
            print(f"      Acción: {op['accion']}")
    # Cross-platform
    if args.cross_platform:
        print("\n🏆 🌐 Análisis cross-platform avanzado...")
        cross_platform = analizador_avanzado_v2.analisis_cross_platform_avanzado()
        plataformas_count = cross_platform.get('plataformas_analizadas', 0)
        print(f"✅ {plataformas_count} plataformas analizadas")
        print(f"✅ {plataformas_count} plataformas analizadas")
        if cross_platform.get('mejor_plataforma"):
            mejor = cross_platform["mejor_plataforma"]
            print(f"   Mejor plataforma: {mejor.get('plataforma\", \"N/A')}")
            print(f"   Engagement: {mejor['engagement_promedio']:.1f}")
    # Scoring en tiempo real
    if args.scoring:
        print("\n🏆📊 Sistema de scoring de contenido en tiempo real...") score = analizador_avanzado_v2.sistema_scoring_contenido_tiempo_real("
            titulo="Cómo mejorar tu engagement en redes sociales",
            tipo_contenido="Y",
            plataforma="LinkedIn",
            hashtags=["#marketing", "#socialmedia", "#engagement"],
            horario=10,
            dia_semana="Wednesday"
        )
        print(f"✅ Score total: {score['score_total']}/100 ({score['porcentaje']}%)")
        print(f"   Nivel: {score['nivel']}")
        print(f"   Probabilidad viral: {score['probabilidad_viral']}")
        print(f"   Factores: {score['factores']}")
        if score['recomendaciones']:
            print(f"   Recomendaciones: {', '.join(score['recomendaciones'][:2])}")
    # Tendencias de mercado
    if args.tendencias:
        print("\n🏆 📈 Análisis de tendencias de mercado avanzado...")
        tendencias = analizador_avanzado_v2.analisis_tendencias_mercado_avanzado()
        print(f"✅ {len(tendencias['tendencias_por_palabra'])} palabras clave analizadas")
        print(f"   Tendencias emergentes: {len(tendencias['tendencias_emergentes'])}")
        print(f"   Tendencias declinantes: {len(tendencias['tendencias_declinantes'])}")
        if tendencias['recomendaciones_estrategicas']:
            for rec in tendencias['recomendaciones_estrategicas'][:2]:
                print(f" [{rec['prioridad']}] {rec['descripcion']}")
                print(f"      Acción: {rec['accion']}")
    # Recomendaciones inteligentes
    if args.recomendaciones:
        print("\n🏆 💡 Recomendaciones inteligentes avanzadas...")
        recomendaciones = analizador_avanzado_v2.generar_recomendaciones_inteligentes_avanzadas()
        print(f"✅ {recomendaciones['total_recomendaciones']} recomendaciones generadas")
        print(f"   Alta prioridad: {len(recomendaciones['recomendaciones_alta_prioridad'])}")
        for rec in recomendaciones['recomendaciones'][:3]:
            print(f" [{rec['prioridad']}] {rec['titulo']}")
            print(f"      {rec['descripcion']}")
            print(f"      Acción: {rec['accion']}")
            print(f"      Fuente: {rec['fuente']}")
    # Exportar reporte
    if args.exportar:
        print(f" 📄 Exportando reporte completo en formato {args.exportar}...")
        resultado = analizador_avanzado_v2.exportar_reporte_completo(formato=args.exportar)
        print(f"✅ Reporte generado: {resultado['archivo_generado']}")
        print(f"   Tamaño: {resultado['tamano_kb']} KB")
        print(f"   Formato: {resultado['formato']}")
    # Análisis de audiencia
    if args.audiencia:
        print("\n🏆 👥 Análisis profundo de audiencia...")
        audiencia = analizador_avanzado_v2.analisis_audiencia_profundo()
        if audiencia.get('preferencias_audiencia'):
            print(f\"✅ Análisis completado\")
            pref = audiencia['preferencias_audiencia']
            print(f"   Plataforma preferida: {pref.get('plataforma_preferida', 'N/A')}")
            print(f"   Tipo de contenido preferido: {pref.get('tipo_contenido_preferido', 'N/A')}")
            print(f"   Horario preferido: {pref.get('horario_preferido', 'N/A')}")
        if audiencia.get('insights'):
            print(f" Insights:")
            for insight in audiencia['insights'][:3]:
                print(f"      • {insight}")
    # Optimización automática
    if args.optimizar:
        print("\n🏆 ⚡ Optimización automática de contenido...")
        contenido_test = {
            'titulo': 'Mejores prácticas de marketing',
            'tipo_contenido': 'Y',
            'plataforma': 'LinkedIn',
            'hashtags': ['#marketing'],
            'horario': 14,
            'dia_semana': 'Monday'
        }
        optimizacion = analizador_avanzado_v2.optimizacion_contenido_automatica(contenido_test)
        if optimizacion.get('mejor_variante'):
            print(f\"✅ {len(optimizacion['variantes'])} variantes generadas\")
            mejor = optimizacion['mejor_variante']
            print(f"   Mejor variante: {mejor['variante']}")
            print(f"   Score: {mejor['score']}/100")
            print(f"   Mejora: +{optimizacion['mejora_score']:.1f} puntos")
    # Dashboard tiempo real
    if args.dashboard:
        print("\n🏆📊 Dashboard de métricas en tiempo real...") dashboard = analizador_avanzado_v2.dashboard_metricas_tiempo_real(periodo_horas=24)"
        if dashboard.get('metricas_generales'):
            print(f\"✅ Dashboard actualizado\")
            mg = dashboard['metricas_generales']
            print(f"   Publicaciones (24h): {mg.get('total_publicaciones', 0)}")
            print(f"   Engagement promedio: {mg.get('engagement_promedio', 0):.1f}")
            print(f"   Tasa viral: {mg.get('tasa_viral', 0):.1f}%")
        if dashboard.get('tendencias'):
            tend = dashboard['tendencias']
            print(f"   Tendencia: {tend.get('direccion', 'N/A')} ({tend.get('cambio_porcentual', 0):+.1f}%)")
        if dashboard.get('alertas_activas'):
            print(f"   Alertas activas: {len(dashboard['alertas_activas'])}")
    # Predicción futuro
    if args.prediccion:
        print(f" 🔮 Predicción de engagement futuro ({args.prediccion} semanas)...")
        prediccion = analizador_avanzado_v2.prediccion_engagement_futuro(
            semanas_futuras=args.prediccion,
            escenario='conservador'
        )
        print(f"✅ Predicción generada (escenario: {prediccion['escenario']})")
        print(f"   Tendencia general: {prediccion.get('tendencia_general', 'N/A')}")
        if prediccion.get('predicciones_semanales'):
            primera = prediccion['predicciones_semanales'][0]
            ultima = prediccion['predicciones_semanales'][-1]
            print(f"   Semana 1: {primera['engagement_predicho']:.1f}")
            print(f"   Semana {args.prediccion}: {ultima['engagement_predicho']:.1f}")
        if prediccion.get('recomendaciones'):
            print(f" Recomendaciones:")
            for rec in prediccion['recomendaciones']:
                print(f"      • {rec}")
    # Análisis competitivo
    if args.competitivo:
        print("\n🏆 datos_competidores = ["
            {'nombre': 'Competidor A', 'engagement_rate_promedio': 4.5, 'frecuencia_publicacion': 5},
            {'nombre': 'Competidor B', 'engagement_rate_promedio': 3.8, 'frecuencia_publicacion': 7},
            {'nombre': 'Competidor C', 'engagement_rate_promedio': 5.2, 'frecuencia_publicacion': 4}
        ]
        competitivo = analizador_avanzado_v2.analisis_competitivo_avanzado(datos_competidores)
        if competitivo.get('analisis_competitivo'):
            print(f\"✅ Análisis completado\")
            ac = competitivo['analisis_competitivo']
            if ac.get('posicion_mercado'):
                pos = ac['posicion_mercado']
                print(f"   Posición en mercado: {pos.get('posicion', 'N/A')}/{pos.get('total_competidores', 'N/A')}")
                print(f"   Percentil: {pos.get('percentil', 0):.1f}%")
            print(f"   Ventajas: {len(ac.get('ventajas_competitivas', []))}")
            print(f"   Desventajas: {len(ac.get('desventajas_competitivas', []))}")
    # Generación de contenido
    if args.generar_contenido:
        print(f" ✨ Generación inteligente de contenido: '{args.generar_contenido}'...")
        contenido = analizador_avanzado_v2.generacion_contenido_inteligente(
            tema=args.generar_contenido
        )
        print(f"✅ Contenido generado")
        print(f"   Título: {contenido.get('titulo_optimizado', 'N/A')}")
        print(f"   Tipo: {contenido.get('tipo_contenido', 'N/A')}")
        print(f"   Plataforma: {contenido.get('plataforma', 'N/A')}")
        print(f"   Score predicho: {contenido.get('score_predicho', 0):.1f}/100")
        print(f"   Probabilidad viral: {contenido.get('probabilidad_viral', 'N/A')}")
        if contenido.get('hashtags_recomendados'):
            print(f"   Hashtags: {', '.join(contenido['hashtags_recomendados'][:5])}")
    # Análisis de campañas
    if args.campanas:
        print("\n🏆📊 Análisis de performance de campañas...") campanas = analizador_avanzado_v2.analisis_performance_campanas()"
        if campanas.get('mejor_campana'):
            print(f\"✅ {campanas.get('total_campanas', 0)} campañas analizadas\")
            mejor = campanas['mejor_campana']
            print(f"   Mejor campaña: {mejor.get('nombre', 'N/A')}")
            print(f"   Engagement promedio: {mejor.get('engagement_promedio', 0):.1f}")
            print(f"   ROI estimado: {mejor.get('roi_estimado', 0):.1f}%")
        if campanas.get('tendencias_campanas'):
            tend = campanas['tendencias_campanas']
            print(f"   Tendencia: {tend.get('direccion', 'N/A')} ({tend.get('cambio_porcentual', 0):+.1f}%)")
    # Recomendaciones personalizadas IA
    if args.recomendaciones_ai:
        print("\n🏆 🤖 Recomendaciones personalizadas con IA...")
        perfil = {
            'objetivo_principal': 'aumentar_engagement',
            'audiencia_objetivo': 'profesionales',
            'presupuesto': 'medio',
            'frecuencia_deseada': '3-5 veces por semana'
        }
        recomendaciones = analizador_avanzado_v2.sistema_recomendaciones_personalizadas_ai(perfil)
        print(f"✅ {recomendaciones.get('total_recomendaciones', 0)} recomendaciones generadas")
        print(f"   Alta prioridad: {len(recomendaciones.get('recomendaciones_alta_prioridad', []))}")
        for rec in recomendaciones.get('recomendaciones', [])[:3]:
            print(f" [{rec.get('prioridad', 'N/A')}] {rec.get('titulo', 'N/A')}")
            print(f"      {rec.get('descripcion', 'N/A')}")
            print(f"      Acción: {rec.get('accion', 'N/A')}")
    # Sentimiento multi-plataforma
    if args.sentimiento_multi:
        print("\n🏆😊Análisis de sentimiento multi-plataforma...")
        sentimiento = analizador_avanzado_v2.analisis_sentimiento_avanzado_multi_plataforma()
        if sentimiento.get('sentimiento_general'):
            print(f\"✅ Análisis completado\")
            sg = sentimiento['sentimiento_general']
            print(f"   Sentimiento general: {sg.get('sentimiento_dominante', 'N/A')}")
            print(f"   Score promedio: {sg.get('score_promedio', 0):.1f}")
        if sentimiento.get('sentimiento_por_plataforma'):
            print(f" Por plataforma:")
            for plataforma, datos in list(sentimiento['sentimiento_por_plataforma'].items())[:3]:
                print(f"      {plataforma}: {datos.get('sentimiento_dominante', 'N/A')} ({datos.get('score_promedio', 0):.1f})")
    # Detección de patrones
    if args.patrones:
        print("\n🏆🔍Detección de patrones ocultos...")
        patrones = analizador_avanzado_v2.deteccion_patrones_ocultos()
        if patrones.get('patrones_hashtags', {}).get('combinaciones_efectivas'):
            print(f\"✅ Patrones detectados\")
            print(f"   Combinaciones de hashtags efectivas: {len(patrones['patrones_hashtags']['combinaciones_efectivas'])}")
            mejor = patrones['patrones_hashtags']['combinaciones_efectivas'][0]
            print(f"   Mejor combinación: {', '.join(mejor['hashtags'])} ({mejor['engagement_promedio']:.1f})")
        if patrones.get('insights'):
            print(f" Insights:")
            for insight in patrones['insights'][:2]:
                print(f"      • {insight}")
    # Optimización de estrategia
    if args.optimizar_estrategia:
        print("\n🏆⚙️ Optimización automática de estrategia...")
        estrategia = analizador_avanzado_v2.optimizacion_automatica_estrategia()
        if estrategia.get('impacto_esperado'):
            print(f"✅ Estrategia optimizada")
            impacto = estrategia['impacto_esperado']
            print(f"   Mejora esperada: {impacto.get('mejora_esperada', 0):.1f}%")
            print(f"   Engagement actual: {impacto.get('engagement_actual', 0):.1f}")
            print(f"   Engagement proyectado: {impacto.get('engagement_proyectado', 0):.1f}")
        if estrategia.get('recomendaciones_estrategicas'):
            print(f" Recomendaciones estratégicas:")
            for rec in estrategia['recomendaciones_estrategicas'][:2]:
                print(f"      [{rec.get('prioridad', 'N/A')}] {rec.get('descripcion', 'N/A')}")
    # Alertas proactivas
    if args.alertas_proactivas:
        print("\n🏆🚨 Sistema de alertas proactivas...")
        alertas = analizador_avanzado_v2.sistema_alertas_proactivas()
        print(f"✅ {alertas.get('total_alertas', 0)} alertas generadas")
        print(f"   Prevención: {len(alertas.get('alertas_prevencion', []))}")
        print(f"   Oportunidades: {len(alertas.get('alertas_oportunidades', []))}")
        for alerta in alertas.get('alertas', [])[:3]:
            print(f" [{alerta.get('severidad', 'N/A')}] {alerta.get('titulo', 'N/A')}")
            print(f"      {alerta.get('descripcion', 'N/A')}")
    # Reporte completo
    if args.reporte_completo:
        print("\n🏆📋Generando reporte completo automático...")
        reporte = analizador_avanzado_v2.reporte_completo_automatico()
        if reporte.get('resumen_ejecutivo'):
            print(f"✅ Reporte generado")
            resumen = reporte['resumen_ejecutivo']
            print(f"   Mejor tipo: {resumen.get('mejor_tipo_contenido', 'N/A')}")
            print(f"   Engagement promedio: {resumen.get('engagement_promedio', 0):.1f}")
            print(f"   Total publicaciones: {resumen.get('total_publicaciones', 0)}")
        if reporte.get('acciones_prioritarias'):
            print(f" Acciones prioritarias:")
            for accion in reporte['acciones_prioritarias'][:3]:
                print(f"      [{accion.get('prioridad', 'N/A')}] {accion.get('accion', 'N/A')}")



    # Análisis de competencia con IA
    if args.competencia_ia:
        print("\n🏆 Análisis de competencia con IA...")
        competidores = [
            {'nombre': 'Competidor A', 'engagement_rate_promedio': 4.5, 'frecuencia_publicacion': 5},
            {'nombre': 'Competidor B', 'engagement_rate_promedio': 3.8, 'frecuencia_publicacion': 7},
            {'nombre': 'Competidor C', 'engagement_rate_promedio': 5.2, 'frecuencia_publicacion': 4}
        ]
        competencia = analizador_avanzado_v2.analisis_competencia_ia(competidores)
        if competencia.get('generado_con_ia'):
            print("✅ Análisis completado")
            print("   ✅ Insights generados con IA")
    # Calendario de contenido con IA
    if args.calendario_ia:
        print(f"\n📅 Generando calendario de contenido con IA ({args.calendario_ia} semanas)...")
        calendario = analizador_avanzado_v2.generacion_calendario_ia(semanas=args.calendario_ia)
        if calendario.get('generado_con_ia'):
            print("✅ Calendario generado")
            print("   ✅ Calendario generado con IA")


if __name__ == "__main__":
    main()


