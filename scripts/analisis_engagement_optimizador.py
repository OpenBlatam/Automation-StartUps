#!/usr/bin/env python3
"""
Optimizador Automático de Engagement - Mejoras Avanzadas
=========================================================
Funcionalidades de optimización automática:
- Optimización automática de contenido
- Optimización de timing
- Optimización de hashtags
- Optimización de plataformas
- Recomendaciones de mejoras específicas
- A/B testing automático
- Optimización basada en ML
- Análisis de impacto de cambios
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
    from analisis_engagement_ml import AnalizadorEngagementML
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizadorEngagement:
    """Optimizador automático de engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        analizador_ml: Optional[AnalizadorEngagementML] = None
    ):
        """
        Inicializa el optimizador
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            analizador_ml: Instancia opcional del AnalizadorEngagementML
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        self.analizador_ml = analizador_ml or AnalizadorEngagementML(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
    
    def optimizar_contenido(
        self,
        tipo_contenido: str,
        plataforma: str,
        titulo_original: str,
        hashtags_originales: List[str],
        hora_original: int = None,
        dia_original: str = None
    ) -> Dict[str, Any]:
        """
        Optimiza contenido para máximo engagement
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            plataforma: Plataforma objetivo
            titulo_original: Título original
            hashtags_originales: Hashtags originales
            hora_original: Hora original de publicación
            dia_original: Día original de publicación
        
        Returns:
            Recomendaciones de optimización con impacto estimado
        """
        # Analizar contenido actual
        reporte = self.analizador.generar_reporte()
        resumen = reporte.get('resumen_ejecutivo', {})
        
        optimizaciones = {
            "contenido_original": {
                "tipo": tipo_contenido,
                "plataforma": plataforma,
                "titulo": titulo_original,
                "hashtags": hashtags_originales,
                "hora": hora_original,
                "dia": dia_original
            },
            "optimizaciones": [],
            "impacto_total_estimado": 0
        }
        
        # 1. Optimizar título
        optimizacion_titulo = self._optimizar_titulo(titulo_original, tipo_contenido, plataforma)
        if optimizacion_titulo:
            optimizaciones["optimizaciones"].append(optimizacion_titulo)
            optimizaciones["impacto_total_estimado"] += optimizacion_titulo.get("impacto_estimado", 0)
        
        # 2. Optimizar hashtags
        optimizacion_hashtags = self._optimizar_hashtags(
            hashtags_originales,
            tipo_contenido,
            plataforma,
            reporte
        )
        if optimizacion_hashtags:
            optimizaciones["optimizaciones"].append(optimizacion_hashtags)
            optimizaciones["impacto_total_estimado"] += optimizacion_hashtags.get("impacto_estimado", 0)
        
        # 3. Optimizar timing
        if hora_original and dia_original:
            optimizacion_timing = self._optimizar_timing(
                hora_original,
                dia_original,
                plataforma,
                resumen
            )
            if optimizacion_timing:
                optimizaciones["optimizaciones"].append(optimizacion_timing)
                optimizaciones["impacto_total_estimado"] += optimizacion_timing.get("impacto_estimado", 0)
        
        # 4. Optimizar tipo de contenido (si aplica)
        mejor_tipo = resumen.get('tipo_ganador')
        if mejor_tipo and mejor_tipo != tipo_contenido:
            optimizaciones["optimizaciones"].append({
                "tipo": "tipo_contenido",
                "actual": tipo_contenido,
                "recomendado": mejor_tipo,
                "razon": f"El tipo {mejor_tipo} tiene mejor engagement histórico",
                "impacto_estimado": 15,
                "prioridad": "MEDIA"
            })
            optimizaciones["impacto_total_estimado"] += 15
        
        # 5. Optimizar plataforma (si aplica)
        mejor_plataforma = resumen.get('mejor_plataforma')
        if mejor_plataforma and mejor_plataforma != plataforma:
            optimizaciones["optimizaciones"].append({
                "tipo": "plataforma",
                "actual": plataforma,
                "recomendado": mejor_plataforma,
                "razon": f"{mejor_plataforma} muestra mejor rendimiento",
                "impacto_estimado": 20,
                "prioridad": "ALTA"
            })
            optimizaciones["impacto_total_estimado"] += 20
        
        # Calcular predicción mejorada
        optimizaciones["prediccion_mejorada"] = self._calcular_prediccion_optimizada(
            optimizaciones,
            tipo_contenido,
            plataforma
        )
        
        return optimizaciones
    
    def _optimizar_titulo(
        self,
        titulo_original: str,
        tipo_contenido: str,
        plataforma: str
    ) -> Optional[Dict[str, Any]]:
        """Optimiza el título del contenido"""
        optimizaciones = []
        
        # Verificar longitud
        longitud = len(titulo_original)
        longitudes_optimas = {
            'Instagram': (40, 60),
            'Twitter': (50, 70),
            'LinkedIn': (60, 80),
            'Facebook': (50, 80),
            'TikTok': (30, 50)
        }
        
        rango_optimo = longitudes_optimas.get(plataforma, (40, 60))
        
        if longitud < rango_optimo[0]:
            optimizaciones.append({
                "problema": f"Título muy corto ({longitud} caracteres)",
                "solucion": f"Agregar más contexto (óptimo: {rango_optimo[0]}-{rango_optimo[1]} caracteres)",
                "impacto": 5
            })
        elif longitud > rango_optimo[1]:
            optimizaciones.append({
                "problema": f"Título muy largo ({longitud} caracteres)",
                "solucion": f"Acortar a {rango_optimo[0]}-{rango_optimo[1]} caracteres",
                "impacto": 5
            })
        
        # Verificar elementos de engagement
        titulo_lower = titulo_original.lower()
        
        elementos_engagement = {
            "pregunta": ("?", 10),
            "numero": (any(c.isdigit() for c in titulo_original), 8),
            "emocion": (any(palabra in titulo_lower for palabra in ["increíble", "sorprendente", "wow"]), 7),
            "beneficio": (any(palabra in titulo_lower for palabra in ["aprende", "descubre", "mejora"]), 6)
        }
        
        elementos_faltantes = []
        for elemento, (tiene, impacto) in elementos_engagement.items():
            if not tiene:
                elementos_faltantes.append({
                    "elemento": elemento,
                    "impacto": impacto,
                    "sugerencia": self._sugerencia_elemento(elemento, tipo_contenido)
                })
        
        if elementos_faltantes:
            mejor_elemento = max(elementos_faltantes, key=lambda x: x["impacto"])
            optimizaciones.append({
                "problema": f"Falta elemento de engagement: {mejor_elemento['elemento']}",
                "solucion": mejor_elemento["sugerencia"],
                "impacto": mejor_elemento["impacto"]
            })
        
        if optimizaciones:
            mejor_optimizacion = max(optimizaciones, key=lambda x: x["impacto"])
            return {
                "tipo": "titulo",
                "actual": titulo_original,
                "recomendaciones": optimizaciones,
                "mejor_recomendacion": mejor_optimizacion,
                "impacto_estimado": mejor_optimizacion["impacto"],
                "prioridad": "ALTA" if mejor_optimizacion["impacto"] >= 8 else "MEDIA"
            }
        
        return None
    
    def _sugerencia_elemento(self, elemento: str, tipo_contenido: str) -> str:
        """Genera sugerencia para agregar elemento"""
        sugerencias = {
            "pregunta": "Agregar pregunta al inicio: '¿Sabías que...?' o '¿Quieres...?'",
            "numero": "Incluir número específico: '5 formas', '10 tips', '30 días'",
            "emocion": "Agregar palabra emocional: 'increíble', 'sorprendente', 'wow'",
            "beneficio": "Destacar beneficio: 'Aprende a...', 'Descubre cómo...', 'Mejora tu...'"
        }
        return sugerencias.get(elemento, "Mejorar título para mayor engagement")
    
    def _optimizar_hashtags(
        self,
        hashtags_originales: List[str],
        tipo_contenido: str,
        plataforma: str,
        reporte: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimiza hashtags"""
        optimizaciones = []
        
        # Verificar cantidad
        num_hashtags = len(hashtags_originales)
        cantidades_optimas = {
            'Instagram': (5, 10),
            'Twitter': (2, 3),
            'LinkedIn': (3, 5),
            'Facebook': (3, 5),
            'TikTok': (5, 10)
        }
        
        rango_optimo = cantidades_optimas.get(plataforma, (5, 7))
        
        if num_hashtags < rango_optimo[0]:
            optimizaciones.append({
                "problema": f"Muy pocos hashtags ({num_hashtags})",
                "solucion": f"Agregar más hashtags (óptimo: {rango_optimo[0]}-{rango_optimo[1]})",
                "impacto": 8
            })
        elif num_hashtags > rango_optimo[1]:
            optimizaciones.append({
                "problema": f"Demasiados hashtags ({num_hashtags})",
                "solucion": f"Reducir a {rango_optimo[0]}-{rango_optimo[1]} hashtags",
                "impacto": 5
            })
        
        # Verificar hashtags efectivos del reporte
        hashtags_efectivos = reporte.get('hashtags_efectivos', [])
        hashtags_top = [h.get('hashtag', '') for h in hashtags_efectivos[:5]]
        
        hashtags_faltantes = [h for h in hashtags_top if h not in hashtags_originales]
        if hashtags_faltantes:
            optimizaciones.append({
                "problema": "Faltan hashtags probados efectivos",
                "solucion": f"Agregar: {', '.join(hashtags_faltantes[:3])}",
                "impacto": 10
            })
        
        if optimizaciones:
            mejor_optimizacion = max(optimizaciones, key=lambda x: x["impacto"])
            hashtags_recomendados = hashtags_originales.copy()
            
            # Agregar hashtags efectivos faltantes
            if hashtags_faltantes:
                hashtags_recomendados.extend(hashtags_faltantes[:3])
            
            # Ajustar cantidad
            if num_hashtags < rango_optimo[0]:
                # Agregar hashtags genéricos
                hashtags_genericos = self._generar_hashtags_genericos(tipo_contenido, plataforma)
                hashtags_recomendados.extend(hashtags_genericos[:rango_optimo[0] - num_hashtags])
            elif num_hashtags > rango_optimo[1]:
                hashtags_recomendados = hashtags_recomendados[:rango_optimo[1]]
            
            return {
                "tipo": "hashtags",
                "actual": hashtags_originales,
                "recomendado": hashtags_recomendados[:rango_optimo[1]],
                "recomendaciones": optimizaciones,
                "impacto_estimado": mejor_optimizacion["impacto"],
                "prioridad": "ALTA" if mejor_optimizacion["impacto"] >= 8 else "MEDIA"
            }
        
        return None
    
    def _generar_hashtags_genericos(self, tipo_contenido: str, plataforma: str) -> List[str]:
        """Genera hashtags genéricos según tipo y plataforma"""
        hashtags_por_tipo = {
            'X': ['#aprende', '#educacion', '#tutorial', '#tips', '#conocimiento'],
            'Y': ['#viral', '#trending', '#entretenimiento', '#diversion', '#compartir'],
            'Z': ['#producto', '#nuevo', '#oferta', '#promocion', '#descubrir']
        }
        return hashtags_por_tipo.get(tipo_contenido, ['#contenido', '#social', '#marketing'])
    
    def _optimizar_timing(
        self,
        hora_original: int,
        dia_original: str,
        plataforma: str,
        resumen: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimiza timing de publicación"""
        mejor_horario = resumen.get('mejor_horario')
        mejor_dia = resumen.get('mejor_dia')
        
        optimizaciones = []
        
        # Analizar horario
        if mejor_horario:
            # Extraer rango de mejor horario
            if '09:00-12:00' in mejor_horario:
                hora_optima = 10
            elif '12:00-15:00' in mejor_horario:
                hora_optima = 13
            elif '15:00-18:00' in mejor_horario:
                hora_optima = 17
            elif '18:00-21:00' in mejor_horario:
                hora_optima = 19
            else:
                hora_optima = 10
            
            diferencia_horas = abs(hora_original - hora_optima)
            if diferencia_horas > 2:
                optimizaciones.append({
                    "problema": f"Hora no óptima ({hora_original}:00)",
                    "solucion": f"Publicar a las {hora_optima}:00 (mejor horario: {mejor_horario})",
                    "impacto": min(12, diferencia_horas * 2)
                })
        
        # Analizar día
        if mejor_dia:
            dias_map = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            dia_es = dias_map.get(dia_original, dia_original)
            
            if dia_es != mejor_dia:
                optimizaciones.append({
                    "problema": f"Día no óptimo ({dia_es})",
                    "solucion": f"Publicar los {mejor_dia}s",
                    "impacto": 8
                })
        
        if optimizaciones:
            mejor_optimizacion = max(optimizaciones, key=lambda x: x["impacto"])
            return {
                "tipo": "timing",
                "actual": {
                    "hora": hora_original,
                    "dia": dia_original
                },
                "recomendaciones": optimizaciones,
                "impacto_estimado": mejor_optimizacion["impacto"],
                "prioridad": "MEDIA"
            }
        
        return None
    
    def _calcular_prediccion_optimizada(
        self,
        optimizaciones: Dict[str, Any],
        tipo_contenido: str,
        plataforma: str
    ) -> Dict[str, Any]:
        """Calcula predicción de engagement con optimizaciones aplicadas"""
        # Predicción base
        prediccion_base = self.analizador_mejorado.predecir_contenido_viral(
            tipo_contenido=tipo_contenido,
            plataforma=plataforma,
            titulo=optimizaciones["contenido_original"]["titulo"],
            hashtags=optimizaciones["contenido_original"]["hashtags"],
            tiene_media=True,
            hora_publicacion=optimizaciones["contenido_original"].get("hora", 10),
            dia_semana=optimizaciones["contenido_original"].get("dia", "Monday")
        )
        
        # Aplicar mejoras estimadas
        mejora_porcentual = optimizaciones["impacto_total_estimado"] / 100
        
        engagement_score_optimizado = prediccion_base["prediccion_engagement"]["engagement_score_estimado"] * (1 + mejora_porcentual)
        engagement_rate_optimizado = prediccion_base["prediccion_engagement"]["engagement_rate_estimado"] * (1 + mejora_porcentual)
        
        return {
            "engagement_score_original": prediccion_base["prediccion_engagement"]["engagement_score_estimado"],
            "engagement_score_optimizado": round(engagement_score_optimizado, 1),
            "mejora_estimada": round(engagement_score_optimizado - prediccion_base["prediccion_engagement"]["engagement_score_estimado"], 1),
            "mejora_porcentual": round(mejora_porcentual * 100, 1),
            "engagement_rate_optimizado": round(engagement_rate_optimizado, 2)
        }
    
    def generar_plan_optimizacion(self, num_semanas: int = 4) -> Dict[str, Any]:
        """
        Genera plan de optimización para múltiples semanas
        
        Args:
            num_semanas: Número de semanas a planificar
        
        Returns:
            Plan de optimización completo
        """
        reporte = self.analizador.generar_reporte()
        resumen = reporte.get('resumen_ejecutivo', {})
        
        plan = {
            "periodo": f"{num_semanas} semanas",
            "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
            "objetivo": "Maximizar engagement",
            "semanas": []
        }
        
        mejor_tipo = resumen.get('tipo_ganador', 'X')
        mejor_plataforma = resumen.get('mejor_plataforma', 'Instagram')
        mejor_horario = resumen.get('mejor_horario', '09:00-12:00')
        mejor_dia = resumen.get('mejor_dia', 'Wednesday')
        
        for semana in range(1, num_semanas + 1):
            fecha_semana = datetime.now() + timedelta(weeks=semana-1)
            
            semana_plan = {
                "semana": semana,
                "fecha": fecha_semana.strftime('%Y-%m-%d'),
                "recomendaciones": [
                    {
                        "tipo": "contenido",
                        "accion": f"Crear {3 if semana % 2 == 0 else 2} publicaciones tipo {mejor_tipo}",
                        "prioridad": "ALTA"
                    },
                    {
                        "tipo": "plataforma",
                        "accion": f"Enfocar en {mejor_plataforma}",
                        "prioridad": "ALTA"
                    },
                    {
                        "tipo": "timing",
                        "accion": f"Publicar los {mejor_dia}s en horario {mejor_horario}",
                        "prioridad": "MEDIA"
                    }
                ],
                "objetivo_engagement": resumen.get('engagement_score_promedio', 0) * (1 + semana * 0.05)
            }
            
            plan["semanas"].append(semana_plan)
        
        return plan


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimizador de Engagement')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--optimizar', action='store_true', help='Optimizar contenido específico')
    parser.add_argument('--plan', action='store_true', help='Generar plan de optimización')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    optimizador = OptimizadorEngagement(analizador_base)
    
    # Optimizar contenido
    if args.optimizar:
        print("\n🔧 Optimizando contenido...")
        optimizaciones = optimizador.optimizar_contenido(
            tipo_contenido='Y',
            plataforma='Instagram',
            titulo_original='Contenido nuevo',
            hashtags_originales=['#nuevo'],
            hora_original=8,
            dia_original='Monday'
        )
        
        print(f"\n✅ Optimizaciones encontradas: {len(optimizaciones['optimizaciones'])}")
        print(f"📈 Impacto total estimado: {optimizaciones['impacto_total_estimado']}%")
        
        for opt in optimizaciones['optimizaciones']:
            print(f"\n[{opt['prioridad']}] {opt['tipo'].upper()}:")
            if 'recomendaciones' in opt:
                for rec in opt['recomendaciones']:
                    print(f"  • {rec['problema']}")
                    print(f"    → {rec['solucion']}")
        
        if 'prediccion_mejorada' in optimizaciones:
            pred = optimizaciones['prediccion_mejorada']
            print(f"\n📊 Predicción Optimizada:")
            print(f"  Original: {pred['engagement_score_original']}")
            print(f"  Optimizado: {pred['engagement_score_optimizado']}")
            print(f"  Mejora: +{pred['mejora_estimada']} ({pred['mejora_porcentual']}%)")
    
    # Plan de optimización
    if args.plan:
        print("\n📅 Generando plan de optimización...")
        plan = optimizador.generar_plan_optimizacion(num_semanas=4)
        print(f"\n✅ Plan generado para {plan['periodo']}")
        for semana in plan['semanas']:
            print(f"\n  Semana {semana['semana']} ({semana['fecha']}):")
            for rec in semana['recomendaciones']:
                print(f"    [{rec['prioridad']}] {rec['accion']}")


if __name__ == "__main__":
    main()


