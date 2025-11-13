#!/usr/bin/env python3
"""
Análisis de Engagement Mejorado - Funcionalidades Avanzadas
===========================================================
Mejoras adicionales al sistema de análisis de engagement:
- Integración con sistema de testimonios
- Predicción de contenido viral
- Análisis de tendencias temporales avanzado
- Recomendaciones automáticas de contenido
- Exportación a PowerPoint
- Análisis de competencia
- Dashboard interactivo mejorado
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

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorEngagementMejorado:
    """Analizador de engagement con funcionalidades avanzadas"""
    
    def __init__(self, analizador_base: AnalizadorEngagement, analizador_ai: Optional[AnalizadorEngagementAI] = None):
        """
        Inicializa el analizador mejorado
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
    
    def predecir_contenido_viral(
        self,
        tipo_contenido: str,
        plataforma: str,
        titulo: str,
        hashtags: List[str],
        tiene_media: bool = True,
        hora_publicacion: int = 10,
        dia_semana: str = "Monday"
    ) -> Dict[str, Any]:
        """
        Predice si un contenido tiene potencial viral
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            plataforma: Plataforma objetivo
            titulo: Título del contenido
            hashtags: Lista de hashtags
            tiene_media: Si tiene imagen/video
            hora_publicacion: Hora de publicación (0-23)
            dia_semana: Día de la semana
        
        Returns:
            Predicción de potencial viral con score y factores
        """
        # Factores de viralidad
        factores = {
            "tipo_contenido": self._score_tipo_viral(tipo_contenido),
            "plataforma": self._score_plataforma_viral(plataforma),
            "titulo": self._score_titulo_viral(titulo),
            "hashtags": self._score_hashtags_viral(hashtags),
            "media": 1.5 if tiene_media else 0.7,
            "timing": self._score_timing_viral(hora_publicacion, dia_semana, plataforma),
            "longitud_titulo": self._score_longitud_titulo(titulo)
        }
        
        # Calcular score viral (0-100)
        score_viral = (
            factores["tipo_contenido"] * 0.20 +
            factores["plataforma"] * 0.15 +
            factores["titulo"] * 0.25 +
            factores["hashtags"] * 0.15 +
            (factores["media"] - 1) * 50 * 0.10 +
            factores["timing"] * 0.10 +
            factores["longitud_titulo"] * 0.05
        )
        
        # Clasificar potencial
        if score_viral >= 75:
            potencial = "MUY ALTO"
            probabilidad = 0.7
        elif score_viral >= 60:
            potencial = "ALTO"
            probabilidad = 0.5
        elif score_viral >= 45:
            potencial = "MEDIO"
            probabilidad = 0.3
        else:
            potencial = "BAJO"
            probabilidad = 0.1
        
        # Recomendaciones para mejorar
        recomendaciones = self._generar_recomendaciones_viral(factores, score_viral)
        
        return {
            "score_viral": round(score_viral, 1),
            "potencial": potencial,
            "probabilidad_viral": probabilidad,
            "factores": factores,
            "recomendaciones": recomendaciones,
            "prediccion_engagement": self._estimar_engagement_viral(score_viral, tipo_contenido, plataforma)
        }
    
    def _score_tipo_viral(self, tipo: str) -> float:
        """Score de viralidad por tipo de contenido"""
        scores = {
            'X': 70,  # Tutoriales pueden ser virales si son únicos
            'Y': 85,  # Entretenimiento tiene mayor potencial viral
            'Z': 40   # Promocional tiene menor potencial
        }
        return scores.get(tipo, 50)
    
    def _score_plataforma_viral(self, plataforma: str) -> float:
        """Score de viralidad por plataforma"""
        scores = {
            'TikTok': 90,
            'Instagram': 80,
            'Twitter': 70,
            'Facebook': 65,
            'LinkedIn': 50
        }
        return scores.get(plataforma, 60)
    
    def _score_titulo_viral(self, titulo: str) -> float:
        """Analiza el título para potencial viral"""
        titulo_lower = titulo.lower()
        score = 50  # Base
        
        # Palabras que aumentan viralidad
        palabras_virales = [
            'increíble', 'sorprendente', 'no vas a creer', 'esto te va a',
            'viral', 'trending', 'wow', 'impresionante', 'alucinante',
            'antes y después', 'transformación', 'resultado', 'cambio'
        ]
        
        for palabra in palabras_virales:
            if palabra in titulo_lower:
                score += 5
        
        # Preguntas aumentan engagement
        if '?' in titulo:
            score += 10
        
        # Números específicos
        import re
        if re.search(r'\d+', titulo):
            score += 5
        
        # Emojis (si están en el título)
        if any(ord(c) > 127 for c in titulo):
            score += 5
        
        return min(100, score)
    
    def _score_hashtags_viral(self, hashtags: List[str]) -> float:
        """Score de viralidad por hashtags"""
        if not hashtags:
            return 30
        
        score = 50
        
        # Número óptimo de hashtags (5-7)
        num_hashtags = len(hashtags)
        if 5 <= num_hashtags <= 7:
            score += 20
        elif 3 <= num_hashtags < 5 or 7 < num_hashtags <= 10:
            score += 10
        
        # Hashtags trending/virales
        hashtags_virales = ['#viral', '#trending', '#fyp', '#foryou', '#explore']
        for tag in hashtags:
            if tag.lower() in [h.lower() for h in hashtags_virales]:
                score += 10
        
        return min(100, score)
    
    def _score_timing_viral(self, hora: int, dia: str, plataforma: str) -> float:
        """Score de timing para viralidad"""
        # Horarios óptimos por plataforma
        horarios_optimos = {
            'Instagram': [(9, 11), (13, 15), (17, 19), (21, 23)],
            'TikTok': [(9, 11), (12, 14), (19, 21), (21, 23)],
            'Facebook': [(8, 10), (13, 15), (17, 19)],
            'Twitter': [(8, 10), (12, 14), (17, 19), (21, 23)],
            'LinkedIn': [(8, 10), (12, 14), (17, 19)]
        }
        
        rangos = horarios_optimos.get(plataforma, [(9, 17)])
        
        # Verificar si la hora está en un rango óptimo
        en_rango_optimo = any(inicio <= hora <= fin for inicio, fin in rangos)
        
        # Días óptimos (martes-jueves generalmente mejores)
        dias_optimos = ['Tuesday', 'Wednesday', 'Thursday']
        dia_optimo = dia in dias_optimos
        
        score = 50
        if en_rango_optimo:
            score += 30
        if dia_optimo:
            score += 20
        
        return min(100, score)
    
    def _score_longitud_titulo(self, titulo: str) -> float:
        """Score basado en longitud del título"""
        longitud = len(titulo)
        
        # Longitud óptima: 40-60 caracteres
        if 40 <= longitud <= 60:
            return 100
        elif 30 <= longitud < 40 or 60 < longitud <= 80:
            return 80
        elif 20 <= longitud < 30 or 80 < longitud <= 100:
            return 60
        else:
            return 40
    
    def _generar_recomendaciones_viral(self, factores: Dict[str, float], score_actual: float) -> List[str]:
        """Genera recomendaciones para mejorar potencial viral"""
        recomendaciones = []
        
        if factores["tipo_contenido"] < 60:
            recomendaciones.append("Considera cambiar a contenido más entretenido o educativo único")
        
        if factores["titulo"] < 60:
            recomendaciones.append("Mejora el título: agrega palabras emocionales, preguntas o números")
        
        if factores["hashtags"] < 60:
            recomendaciones.append("Optimiza hashtags: usa 5-7 hashtags, incluye algunos trending")
        
        if factores["media"] < 1.0:
            recomendaciones.append("Agrega imagen o video de alta calidad - aumenta viralidad significativamente")
        
        if factores["timing"] < 60:
            recomendaciones.append("Ajusta timing: publica en horarios óptimos para tu plataforma")
        
        if score_actual < 60:
            recomendaciones.append("Combina múltiples mejoras para maximizar potencial viral")
        
        return recomendaciones
    
    def _estimar_engagement_viral(self, score_viral: float, tipo: str, plataforma: str) -> Dict[str, Any]:
        """Estima engagement esperado basado en score viral"""
        # Engagement base por tipo y plataforma
        base_engagement = {
            ('X', 'Instagram'): 500,
            ('X', 'TikTok'): 800,
            ('Y', 'Instagram'): 700,
            ('Y', 'TikTok'): 1200,
            ('Z', 'Instagram'): 300,
            ('Z', 'TikTok'): 500
        }
        
        base = base_engagement.get((tipo, plataforma), 400)
        
        # Multiplicador basado en score viral
        multiplicador = 1 + (score_viral / 100) * 2  # Score 100 = 3x engagement
        
        engagement_estimado = int(base * multiplicador)
        
        return {
            "engagement_score_estimado": engagement_estimado,
            "engagement_rate_estimado": min(15.0, (score_viral / 100) * 10),
            "likes_estimados": int(engagement_estimado * 0.7),
            "comentarios_estimados": int(engagement_estimado * 0.2),
            "shares_estimados": int(engagement_estimado * 0.1)
        }
    
    def analizar_tendencias_temporales(self, dias: int = 30) -> Dict[str, Any]:
        """
        Analiza tendencias temporales de engagement
        
        Args:
            dias: Días hacia atrás para analizar
        
        Returns:
            Análisis de tendencias temporales
        """
        fecha_limite = datetime.now() - timedelta(days=dias)
        publicaciones_recientes = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= fecha_limite
        ]
        
        if len(publicaciones_recientes) < 5:
            return {"error": "No hay suficientes datos para análisis de tendencias"}
        
        # Agrupar por semana
        tendencias_semanales = defaultdict(lambda: {
            'engagement_scores': [],
            'engagement_rates': [],
            'publicaciones': []
        })
        
        for pub in publicaciones_recientes:
            semana = pub.fecha_publicacion.isocalendar()[1]
            año = pub.fecha_publicacion.year
            clave = f"{año}-W{semana}"
            
            tendencias_semanales[clave]['engagement_scores'].append(pub.engagement_score)
            tendencias_semanales[clave]['engagement_rates'].append(pub.engagement_rate)
            tendencias_semanales[clave]['publicaciones'].append(pub)
        
        # Calcular promedios semanales
        semanas_analizadas = []
        for semana_key in sorted(tendencias_semanales.keys()):
            datos = tendencias_semanales[semana_key]
            if datos['engagement_scores']:
                semanas_analizadas.append({
                    'semana': semana_key,
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates']),
                    'num_publicaciones': len(datos['publicaciones'])
                })
        
        # Calcular tendencia
        if len(semanas_analizadas) >= 2:
            primera_semana = semanas_analizadas[0]['engagement_score_promedio']
            ultima_semana = semanas_analizadas[-1]['engagement_score_promedio']
            cambio_porcentual = ((ultima_semana - primera_semana) / primera_semana) * 100 if primera_semana > 0 else 0
            
            direccion = "creciente" if cambio_porcentual > 5 else "decreciente" if cambio_porcentual < -5 else "estable"
        else:
            cambio_porcentual = 0
            direccion = "insuficientes datos"
        
        return {
            "periodo_analizado": f"{dias} días",
            "semanas_analizadas": semanas_analizadas,
            "tendencia": direccion,
            "cambio_porcentual": round(cambio_porcentual, 2),
            "proyeccion": self._proyectar_tendencia(semanas_analizadas)
        }
    
    def _proyectar_tendencia(self, semanas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Proyecta la tendencia hacia el futuro"""
        if len(semanas) < 2:
            return {"error": "Datos insuficientes para proyección"}
        
        # Calcular tasa de cambio promedio
        cambios = []
        for i in range(1, len(semanas)):
            cambio = semanas[i]['engagement_score_promedio'] - semanas[i-1]['engagement_score_promedio']
            cambios.append(cambio)
        
        cambio_promedio = statistics.mean(cambios) if cambios else 0
        ultimo_score = semanas[-1]['engagement_score_promedio']
        
        # Proyectar próximas 4 semanas
        proyecciones = []
        for semana_futura in range(1, 5):
            score_proyectado = ultimo_score + (cambio_promedio * semana_futura)
            proyecciones.append({
                'semana': f"Semana +{semana_futura}",
                'engagement_score_proyectado': max(0, score_proyectado)
            })
        
        return {
            "proyecciones": proyecciones,
            "tendencia_esperada": "creciente" if cambio_promedio > 0 else "decreciente" if cambio_promedio < 0 else "estable",
            "cambio_semanal_promedio": round(cambio_promedio, 2)
        }
    
    def generar_recomendaciones_contenido(self, num_recomendaciones: int = 10) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones automáticas de contenido basadas en análisis
        
        Args:
            num_recomendaciones: Número de recomendaciones a generar
        
        Returns:
            Lista de recomendaciones de contenido
        """
        reporte = self.analizador.generar_reporte()
        resumen = reporte.get('resumen_ejecutivo', {})
        
        recomendaciones = []
        
        # Analizar qué funciona mejor
        mejor_tipo = resumen.get('tipo_ganador', 'X')
        mejor_plataforma = resumen.get('mejor_plataforma', 'Instagram')
        mejor_horario = resumen.get('mejor_horario', '09:00-12:00')
        mejor_dia = resumen.get('mejor_dia', 'Lunes')
        
        # Hashtags efectivos
        hashtags_efectivos = reporte.get('hashtags_efectivos', [])[:5]
        hashtags_top = [h.get('hashtag', '') for h in hashtags_efectivos]
        
        # Generar recomendaciones variadas
        tipos_recomendaciones = [
            {
                "tipo": "Replicar Éxito",
                "descripcion": f"Crear más contenido tipo {mejor_tipo} en {mejor_plataforma}",
                "accion": f"Publicar contenido {resumen.get('nombre_tipo', '')} los {mejor_dia}s en horario {mejor_horario}",
                "prioridad": "ALTA",
                "impacto_esperado": "Alto"
            },
            {
                "tipo": "Optimizar Timing",
                "descripcion": f"Enfocar publicaciones en {mejor_horario} los {mejor_dia}s",
                "accion": f"Programar al menos 3 publicaciones semanales en {mejor_horario}",
                "prioridad": "MEDIA",
                "impacto_esperado": "Medio"
            },
            {
                "tipo": "Hashtags Estratégicos",
                "descripcion": f"Usar hashtags probados: {', '.join(hashtags_top[:3])}",
                "accion": f"Incluir estos hashtags en próximas publicaciones: {', '.join(hashtags_top)}",
                "prioridad": "MEDIA",
                "impacto_esperado": "Medio"
            },
            {
                "tipo": "Diversificar Plataformas",
                "descripcion": f"Explorar otras plataformas además de {mejor_plataforma}",
                "accion": "Crear contenido adaptado para múltiples plataformas",
                "prioridad": "BAJA",
                "impacto_esperado": "Medio"
            },
            {
                "tipo": "Contenido Viral",
                "descripcion": "Crear contenido con alto potencial viral",
                "accion": "Usar elementos probados: títulos emocionales, imágenes impactantes, timing óptimo",
                "prioridad": "ALTA",
                "impacto_esperado": "Alto"
            }
        ]
        
        # Agregar recomendaciones específicas basadas en análisis
        engagement_rate = resumen.get('engagement_rate_promedio', 0)
        if engagement_rate < 2.0:
            tipos_recomendaciones.append({
                "tipo": "Mejorar Calidad",
                "descripcion": "El engagement rate está por debajo del promedio",
                "accion": "Enfocarse en calidad sobre cantidad, mejorar imágenes/videos, optimizar copywriting",
                "prioridad": "ALTA",
                "impacto_esperado": "Alto"
            })
        
        return tipos_recomendaciones[:num_recomendaciones]
    
    def integrar_con_testimonios(self, testimonial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra análisis con sistema de testimonios para optimizar contenido
        
        Args:
            testimonial_data: Datos del testimonio convertido
        
        Returns:
            Análisis integrado con recomendaciones
        """
        # Analizar el testimonio generado
        post_content = testimonial_data.get('post_content', '')
        hashtags = testimonial_data.get('hashtags', [])
        platform = testimonial_data.get('platform', 'general')
        quality_metrics = testimonial_data.get('quality_metrics', {})
        
        # Predecir potencial viral
        tipo_contenido = 'Y' if 'transformación' in post_content.lower() or 'resultado' in post_content.lower() else 'X'
        
        prediccion_viral = self.predecir_contenido_viral(
            tipo_contenido=tipo_contenido,
            plataforma=platform,
            titulo=post_content[:100] if len(post_content) > 100 else post_content,
            hashtags=hashtags,
            tiene_media=True,
            hora_publicacion=10,
            dia_semana="Monday"
        )
        
        # Comparar con contenido exitoso existente
        reporte = self.analizador.generar_reporte()
        mejor_tipo = reporte.get('resumen_ejecutivo', {}).get('tipo_ganador', 'X')
        
        recomendaciones = {
            "testimonio_analizado": {
                "platform": platform,
                "engagement_score_estimado": quality_metrics.get('engagement_score', 0),
                "potencial_viral": prediccion_viral['potencial']
            },
            "comparacion": {
                "tipo_contenido": tipo_contenido,
                "mejor_tipo_historico": mejor_tipo,
                "alineado_con_exito": tipo_contenido == mejor_tipo
            },
            "recomendaciones": []
        }
        
        # Generar recomendaciones específicas
        if prediccion_viral['score_viral'] < 60:
            recomendaciones["recomendaciones"].append({
                "tipo": "Mejorar Potencial Viral",
                "accion": "Optimizar título, agregar más hashtags trending, ajustar timing"
            })
        
        if platform != reporte.get('resumen_ejecutivo', {}).get('mejor_plataforma'):
            recomendaciones["recomendaciones"].append({
                "tipo": "Plataforma Alternativa",
                "accion": f"Considera publicar también en {reporte.get('resumen_ejecutivo', {}).get('mejor_plataforma')}"
            })
        
        return {
            **recomendaciones,
            "prediccion_viral": prediccion_viral
        }


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de Engagement Mejorado')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--predecir-viral', action='store_true', help='Predecir contenido viral')
    parser.add_argument('--tendencias', action='store_true', help='Analizar tendencias temporales')
    parser.add_argument('--recomendaciones', action='store_true', help='Generar recomendaciones')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_mejorado = AnalizadorEngagementMejorado(analizador_base)
    
    # Predicción viral
    if args.predecir_viral:
        print("\n" + "="*80)
        print("PREDICCIÓN DE CONTENIDO VIRAL")
        print("="*80)
        
        prediccion = analizador_mejorado.predecir_contenido_viral(
            tipo_contenido='Y',
            plataforma='Instagram',
            titulo='Antes y después: Transformación increíble en solo 30 días',
            hashtags=['#transformación', '#resultados', '#viral', '#antesydespues'],
            tiene_media=True,
            hora_publicacion=10,
            dia_semana='Wednesday'
        )
        
        print(f"\nScore Viral: {prediccion['score_viral']}/100")
        print(f"Potencial: {prediccion['potencial']}")
        print(f"Probabilidad Viral: {prediccion['probabilidad_viral']*100:.1f}%")
        print(f"\nEngagement Estimado: {prediccion['prediccion_engagement']['engagement_score_estimado']}")
        print(f"\nRecomendaciones:")
        for rec in prediccion['recomendaciones']:
            print(f"  • {rec}")
    
    # Tendencias temporales
    if args.tendencias:
        print("\n" + "="*80)
        print("ANÁLISIS DE TENDENCIAS TEMPORALES")
        print("="*80)
        
        tendencias = analizador_mejorado.analizar_tendencias_temporales(dias=30)
        print(f"\nTendencia: {tendencias.get('tendencia', 'N/A')}")
        print(f"Cambio Porcentual: {tendencias.get('cambio_porcentual', 0):+.2f}%")
        
        if 'proyeccion' in tendencias:
            print(f"\nProyecciones:")
            for proy in tendencias['proyeccion'].get('proyecciones', []):
                print(f"  {proy['semana']}: {proy['engagement_score_proyectado']:.1f}")
    
    # Recomendaciones
    if args.recomendaciones:
        print("\n" + "="*80)
        print("RECOMENDACIONES DE CONTENIDO")
        print("="*80)
        
        recomendaciones = analizador_mejorado.generar_recomendaciones_contenido()
        for i, rec in enumerate(recomendaciones, 1):
            print(f"\n{i}. [{rec['prioridad']}] {rec['tipo']}")
            print(f"   {rec['descripcion']}")
            print(f"   💡 {rec['accion']}")
            print(f"   📊 Impacto: {rec['impacto_esperado']}")


if __name__ == "__main__":
    main()


