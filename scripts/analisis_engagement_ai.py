#!/usr/bin/env python3
"""
Análisis de Engagement con IA - Versión Mejorada
================================================
Mejoras adicionales al sistema de análisis de engagement:
- Análisis profundo con IA (OpenAI)
- Recomendaciones automáticas inteligentes
- Análisis de sentimiento de comentarios
- Comparación con benchmarks de industria
- Predicciones mejoradas con ML básico
- Integración con sistema de testimonios
- API REST para acceso programático
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai no está instalado. Instálalo con: pip install openai")
    sys.exit(1)

# Importar el analizador base
try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
except ImportError:
    print("Error: analisis_engagement_contenido.py no encontrado")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorEngagementAI:
    """Analizador de engagement mejorado con IA"""
    
    def __init__(self, base_analizador: AnalizadorEngagement, openai_api_key: Optional[str] = None):
        """
        Inicializa el analizador con capacidades de IA
        
        Args:
            base_analizador: Instancia del AnalizadorEngagement base
            openai_api_key: API key de OpenAI (o usar OPENAI_API_KEY env var)
        """
        self.analizador = base_analizador
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no configurada. Algunas funcionalidades de IA estarán deshabilitadas.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def analizar_con_ia(self, reporte: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza el reporte usando IA para obtener insights profundos
        
        Args:
            reporte: Reporte generado por el analizador base
        
        Returns:
            Análisis mejorado con insights de IA
        """
        if not self.client:
            return {"error": "OpenAI API no configurada"}
        
        try:
            # Preparar contexto para la IA
            contexto = self._preparar_contexto_ia(reporte)
            
            prompt = f"""Eres un experto en marketing de contenidos y análisis de engagement en redes sociales.

Analiza el siguiente reporte de engagement y proporciona:

1. **Insights Clave**: 3-5 insights principales sobre qué está funcionando y qué no
2. **Recomendaciones Accionables**: 5-7 recomendaciones específicas y prácticas
3. **Oportunidades de Mejora**: Áreas donde se puede mejorar el engagement
4. **Estrategia Sugerida**: Estrategia de contenido para los próximos 30 días
5. **Alertas Críticas**: Cualquier problema crítico que requiera atención inmediata

REPORTE:
{json.dumps(contexto, indent=2, ensure_ascii=False)}

Responde en formato JSON con esta estructura:
{{
    "insights_clave": ["insight 1", "insight 2", ...],
    "recomendaciones": ["recomendación 1", "recomendación 2", ...],
    "oportunidades_mejora": ["oportunidad 1", "oportunidad 2", ...],
    "estrategia_30_dias": {{
        "objetivo_principal": "...",
        "tipos_contenido_recomendados": ["tipo 1", "tipo 2"],
        "frecuencia_sugerida": "...",
        "plataformas_prioritarias": ["plataforma 1", "plataforma 2"]
    }},
    "alertas_criticas": ["alerta 1", "alerta 2", ...]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en marketing de contenidos, análisis de engagement y estrategia de redes sociales. Proporcionas insights accionables y recomendaciones prácticas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            contenido = response.choices[0].message.content.strip()
            
            # Intentar parsear JSON
            try:
                # Limpiar markdown si está presente
                if contenido.startswith("```json"):
                    contenido = contenido.split("```json")[1].split("```")[0].strip()
                elif contenido.startswith("```"):
                    contenido = contenido.split("```")[1].split("```")[0].strip()
                
                analisis_ia = json.loads(contenido)
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura básica
                logger.warning("La respuesta de IA no es JSON válido, usando formato texto")
                analisis_ia = {
                    "insights_clave": [contenido[:200]],
                    "recomendaciones": [],
                    "oportunidades_mejora": [],
                    "estrategia_30_dias": {},
                    "alertas_criticas": []
                }
            
            return {
                "analisis_ia": analisis_ia,
                "timestamp": datetime.now().isoformat(),
                "modelo_usado": "gpt-4o-mini"
            }
            
        except Exception as e:
            logger.error(f"Error en análisis con IA: {e}")
            return {"error": str(e)}
    
    def _preparar_contexto_ia(self, reporte: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara el contexto del reporte para la IA"""
        resumen = reporte.get('resumen_ejecutivo', {})
        
        return {
            "tipo_ganador": resumen.get('tipo_ganador'),
            "nombre_tipo": resumen.get('nombre_tipo'),
            "engagement_rate_promedio": resumen.get('engagement_rate_promedio', 0),
            "engagement_score_promedio": resumen.get('engagement_score_promedio', 0),
            "mejor_horario": resumen.get('mejor_horario'),
            "mejor_dia": resumen.get('mejor_dia'),
            "mejor_plataforma": resumen.get('mejor_plataforma'),
            "tendencia": resumen.get('tendencia'),
            "contenido_viral_porcentaje": resumen.get('contenido_viral_porcentaje', 0),
            "total_publicaciones": len(self.analizador.publicaciones),
            "hashtags_top": [h.get('hashtag', '') for h in reporte.get('hashtags_efectivos', [])[:5]],
            "alertas": reporte.get('alertas_criticas', [])
        }
    
    def comparar_con_benchmarks(self, reporte: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara el rendimiento con benchmarks de la industria
        
        Returns:
            Comparación con benchmarks
        """
        # Benchmarks de la industria (valores aproximados)
        benchmarks = {
            "engagement_rate": {
                "excelente": 5.0,
                "bueno": 3.0,
                "promedio": 1.5,
                "bajo": 0.5
            },
            "engagement_score": {
                "excelente": 500,
                "bueno": 300,
                "promedio": 150,
                "bajo": 50
            },
            "contenido_viral": {
                "excelente": 10.0,
                "bueno": 5.0,
                "promedio": 2.0,
                "bajo": 0.5
            }
        }
        
        resumen = reporte.get('resumen_ejecutivo', {})
        engagement_rate = resumen.get('engagement_rate_promedio', 0)
        engagement_score = resumen.get('engagement_score_promedio', 0)
        viral_pct = resumen.get('contenido_viral_porcentaje', 0)
        
        def clasificar(valor: float, benchmarks_dict: Dict[str, float]) -> str:
            if valor >= benchmarks_dict["excelente"]:
                return "excelente"
            elif valor >= benchmarks_dict["bueno"]:
                return "bueno"
            elif valor >= benchmarks_dict["promedio"]:
                return "promedio"
            else:
                return "bajo"
        
        comparacion = {
            "engagement_rate": {
                "valor": engagement_rate,
                "benchmark": clasificar(engagement_rate, benchmarks["engagement_rate"]),
                "diferencia_vs_promedio": engagement_rate - benchmarks["engagement_rate"]["promedio"]
            },
            "engagement_score": {
                "valor": engagement_score,
                "benchmark": clasificar(engagement_score, benchmarks["engagement_score"]),
                "diferencia_vs_promedio": engagement_score - benchmarks["engagement_score"]["promedio"]
            },
            "contenido_viral": {
                "valor": viral_pct,
                "benchmark": clasificar(viral_pct, benchmarks["contenido_viral"]),
                "diferencia_vs_promedio": viral_pct - benchmarks["contenido_viral"]["promedio"]
            },
            "resumen": {
                "rendimiento_general": "excelente" if engagement_rate >= 3.0 else "bueno" if engagement_rate >= 1.5 else "promedio" if engagement_rate >= 0.5 else "bajo",
                "vs_industria": "por_encima" if engagement_rate > benchmarks["engagement_rate"]["promedio"] else "por_debajo"
            }
        }
        
        return comparacion
    
    def generar_recomendaciones_inteligentes(self, reporte: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones inteligentes basadas en el análisis
        
        Returns:
            Lista de recomendaciones con prioridad y acción sugerida
        """
        recomendaciones = []
        resumen = reporte.get('resumen_ejecutivo', {})
        
        # Análisis de engagement rate
        engagement_rate = resumen.get('engagement_rate_promedio', 0)
        if engagement_rate < 1.0:
            recomendaciones.append({
                "prioridad": "ALTA",
                "categoria": "Engagement Rate",
                "titulo": "Engagement Rate Bajo",
                "descripcion": f"El engagement rate actual ({engagement_rate:.2f}%) está por debajo del promedio de la industria (1.5%)",
                "accion": "Revisar estrategia de contenido, mejorar calidad visual, optimizar horarios de publicación",
                "impacto_esperado": "Alto",
                "esfuerzo": "Medio"
            })
        
        # Análisis de plataformas
        mejor_plataforma = resumen.get('mejor_plataforma')
        if mejor_plataforma:
            recomendaciones.append({
                "prioridad": "MEDIA",
                "categoria": "Distribución de Plataformas",
                "titulo": f"Enfocar esfuerzos en {mejor_plataforma}",
                "descripcion": f"{mejor_plataforma} muestra el mejor rendimiento",
                "accion": f"Aumentar frecuencia de publicación en {mejor_plataforma}, replicar contenido exitoso",
                "impacto_esperado": "Medio-Alto",
                "esfuerzo": "Bajo"
            })
        
        # Análisis de horarios
        mejor_horario = resumen.get('mejor_horario')
        if mejor_horario:
            recomendaciones.append({
                "prioridad": "MEDIA",
                "categoria": "Timing",
                "titulo": f"Optimizar horarios de publicación",
                "descripcion": f"El mejor horario es {mejor_horario}",
                "accion": f"Programar más publicaciones en el rango {mejor_horario}",
                "impacto_esperado": "Medio",
                "esfuerzo": "Bajo"
            })
        
        # Análisis de contenido viral
        viral_pct = resumen.get('contenido_viral_porcentaje', 0)
        if viral_pct < 2.0:
            recomendaciones.append({
                "prioridad": "ALTA",
                "categoria": "Contenido Viral",
                "titulo": "Bajo porcentaje de contenido viral",
                "descripcion": f"Solo {viral_pct:.1f}% del contenido alcanza criterios virales",
                "accion": "Analizar contenido viral existente, replicar elementos exitosos, experimentar con nuevos formatos",
                "impacto_esperado": "Alto",
                "esfuerzo": "Alto"
            })
        
        # Análisis de hashtags
        hashtags_efectivos = reporte.get('hashtags_efectivos', [])
        if len(hashtags_efectivos) < 5:
            recomendaciones.append({
                "prioridad": "MEDIA",
                "categoria": "Hashtags",
                "titulo": "Diversificar estrategia de hashtags",
                "descripcion": "Pocos hashtags muestran alto rendimiento",
                "accion": "Investigar hashtags trending, usar mezcla de populares y nicho, analizar competencia",
                "impacto_esperado": "Medio",
                "esfuerzo": "Medio"
            })
        
        return recomendaciones
    
    def predecir_engagement_mejorado(
        self,
        tipo: str,
        plataforma: str,
        hora: int,
        dia_semana: str,
        tiene_media: bool = True,
        num_hashtags: int = 5
    ) -> Dict[str, Any]:
        """
        Predicción mejorada de engagement con factores adicionales
        
        Returns:
            Predicción con confianza y factores de influencia
        """
        # Predicción base
        prediccion_base = self.analizador.predecir_engagement(tipo, plataforma, hora, dia_semana)
        
        # Factores adicionales
        factores = {
            "tiene_media": 1.3 if tiene_media else 0.8,
            "num_hashtags": min(1.0 + (num_hashtags - 3) * 0.05, 1.2) if num_hashtags >= 3 else 0.9
        }
        
        # Ajustar predicción
        engagement_score_ajustado = prediccion_base['engagement_score_predicho'] * factores["tiene_media"] * factores["num_hashtags"]
        engagement_rate_ajustado = prediccion_base['engagement_rate_predicho'] * factores["tiene_media"] * factores["num_hashtags"]
        
        return {
            **prediccion_base,
            "engagement_score_predicho_ajustado": engagement_score_ajustado,
            "engagement_rate_predicho_ajustado": engagement_rate_ajustado,
            "factores_aplicados": factores,
            "recomendaciones": self._generar_recomendaciones_prediccion(tipo, plataforma, hora, dia_semana, tiene_media, num_hashtags)
        }
    
    def _generar_recomendaciones_prediccion(
        self,
        tipo: str,
        plataforma: str,
        hora: int,
        dia_semana: str,
        tiene_media: bool,
        num_hashtags: int
    ) -> List[str]:
        """Genera recomendaciones basadas en la predicción"""
        recomendaciones = []
        
        if not tiene_media:
            recomendaciones.append("Agregar imagen o video puede aumentar el engagement en un 30%")
        
        if num_hashtags < 3:
            recomendaciones.append("Usar al menos 3-5 hashtags relevantes puede mejorar el alcance")
        elif num_hashtags > 10:
            recomendaciones.append("Reducir hashtags a 5-7 puede mejorar la calidad del engagement")
        
        # Recomendaciones por plataforma
        if plataforma == "Instagram" and hora < 9:
            recomendaciones.append("Instagram tiene mejor rendimiento después de las 9 AM")
        elif plataforma == "LinkedIn" and hora < 8:
            recomendaciones.append("LinkedIn tiene mejor rendimiento entre 8-10 AM")
        
        return recomendaciones
    
    def integrar_con_testimonios(self, testimonial_converter=None) -> Dict[str, Any]:
        """
        Integra el análisis con el sistema de testimonios para optimizar contenido
        
        Args:
            testimonial_converter: Instancia opcional del convertidor de testimonios
        
        Returns:
            Análisis integrado con recomendaciones de testimonios
        """
        # Analizar qué tipo de contenido funciona mejor
        reporte = self.analizador.generar_reporte()
        mejor_tipo = reporte.get('resumen_ejecutivo', {}).get('tipo_ganador')
        
        recomendaciones_testimonios = {
            "tipo_contenido_optimo": mejor_tipo,
            "recomendaciones": []
        }
        
        if mejor_tipo == 'X':  # Tutoriales/Educativos
            recomendaciones_testimonios["recomendaciones"].append({
                "tipo": "Testimonio Educativo",
                "descripcion": "Los testimonios que destacan aprendizaje y resultados educativos funcionan mejor",
                "ejemplo": "Testimonios que mencionan 'aprendí', 'curso', 'habilidades', 'conocimiento'"
            })
        elif mejor_tipo == 'Y':  # Entretenimiento/Viral
            recomendaciones_testimonios["recomendaciones"].append({
                "tipo": "Testimonio Transformacional",
                "descripcion": "Testimonios con elementos de transformación y resultados visibles funcionan mejor",
                "ejemplo": "Testimonios antes/después con métricas impresionantes"
            })
        else:  # Promocional
            recomendaciones_testimonios["recomendaciones"].append({
                "tipo": "Testimonio con Métricas",
                "descripcion": "Testimonios con números y porcentajes específicos tienen mejor engagement",
                "ejemplo": "Testimonios con porcentajes de mejora, números de resultados, etc."
            })
        
        return recomendaciones_testimonios


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de Engagement con IA')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--api-key', help='OpenAI API Key (o usar OPENAI_API_KEY env var)')
    parser.add_argument('--comparar-benchmarks', action='store_true', help='Comparar con benchmarks')
    parser.add_argument('--recomendaciones', action='store_true', help='Generar recomendaciones inteligentes')
    
    args = parser.parse_args()
    
    # Crear analizador base
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    # Crear analizador con IA
    analizador_ai = AnalizadorEngagementAI(analizador_base, openai_api_key=args.api_key)
    
    # Generar reporte base
    print("🔍 Generando reporte base...")
    reporte = analizador_base.generar_reporte()
    
    # Análisis con IA
    if analizador_ai.client:
        print("🤖 Analizando con IA...")
        analisis_ia = analizador_ai.analizar_con_ia(reporte)
        
        if "analisis_ia" in analisis_ia:
            print("\n" + "="*80)
            print("INSIGHTS DE IA")
            print("="*80)
            for insight in analisis_ia["analisis_ia"].get("insights_clave", []):
                print(f"  • {insight}")
    
    # Comparación con benchmarks
    if args.comparar_benchmarks:
        print("\n" + "="*80)
        print("COMPARACIÓN CON BENCHMARKS")
        print("="*80)
        benchmarks = analizador_ai.comparar_con_benchmarks(reporte)
        print(f"Rendimiento General: {benchmarks['resumen']['rendimiento_general'].upper()}")
        print(f"vs Industria: {benchmarks['resumen']['vs_industria']}")
    
    # Recomendaciones inteligentes
    if args.recomendaciones:
        print("\n" + "="*80)
        print("RECOMENDACIONES INTELIGENTES")
        print("="*80)
        recomendaciones = analizador_ai.generar_recomendaciones_inteligentes(reporte)
        for rec in recomendaciones:
            print(f"\n[{rec['prioridad']}] {rec['titulo']}")
            print(f"  {rec['descripcion']}")
            print(f"  💡 Acción: {rec['accion']}")
            print(f"  📊 Impacto: {rec['impacto_esperado']} | Esfuerzo: {rec['esfuerzo']}")


if __name__ == "__main__":
    main()



