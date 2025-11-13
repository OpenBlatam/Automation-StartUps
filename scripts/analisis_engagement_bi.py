#!/usr/bin/env python3
"""
Business Intelligence para Engagement - Análisis Avanzado
=========================================================
Funcionalidades de BI avanzadas:
- Análisis de competencia mejorado
- Análisis de audiencia profundo
- Segmentación avanzada de audiencia
- Análisis de cohortes mejorado
- Análisis de funnel de engagement
- Análisis de retención
- Análisis de lifetime value (LTV)
- Análisis de atribución
- Recomendaciones estratégicas de negocio
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
    from analisis_engagement_integraciones import AnalizadorEngagementIntegraciones
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorBIEngagement:
    """Analizador de Business Intelligence para engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        analizador_integraciones: Optional[AnalizadorEngagementIntegraciones] = None
    ):
        """
        Inicializa el analizador de BI
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            analizador_integraciones: Instancia opcional del AnalizadorEngagementIntegraciones
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        self.analizador_integraciones = analizador_integraciones or AnalizadorEngagementIntegraciones(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
    
    def analizar_competencia_avanzado(
        self,
        datos_competencia: List[Dict[str, Any]],
        metricas_propias: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de competencia con múltiples dimensiones
        
        Args:
            datos_competencia: Lista de métricas de competidores
            metricas_propias: Métricas propias
        
        Returns:
            Análisis competitivo completo
        """
        if not datos_competencia:
            return {"error": "No hay datos de competencia"}
        
        # Calcular estadísticas de competencia
        engagement_rates = [c.get('engagement_rate', 0) for c in datos_competencia]
        engagement_scores = [c.get('engagement_score', 0) for c in datos_competencia]
        
        estadisticas_competencia = {
            'promedio': {
                'engagement_rate': statistics.mean(engagement_rates) if engagement_rates else 0,
                'engagement_score': statistics.mean(engagement_scores) if engagement_scores else 0
            },
            'mediana': {
                'engagement_rate': statistics.median(engagement_rates) if engagement_rates else 0,
                'engagement_score': statistics.median(engagement_scores) if engagement_scores else 0
            },
            'percentil_25': {
                'engagement_rate': sorted(engagement_rates)[len(engagement_rates)//4] if engagement_rates else 0,
                'engagement_score': sorted(engagement_scores)[len(engagement_scores)//4] if engagement_scores else 0
            },
            'percentil_75': {
                'engagement_rate': sorted(engagement_rates)[3*len(engagement_rates)//4] if engagement_rates else 0,
                'engagement_score': sorted(engagement_scores)[3*len(engagement_scores)//4] if engagement_scores else 0
            },
            'mejor': {
                'engagement_rate': max(engagement_rates) if engagement_rates else 0,
                'engagement_score': max(engagement_scores) if engagement_scores else 0
            },
            'peor': {
                'engagement_rate': min(engagement_rates) if engagement_rates else 0,
                'engagement_score': min(engagement_scores) if engagement_scores else 0
            }
        }
        
        # Comparar con propias
        engagement_rate_propio = metricas_propias.get('engagement_rate', 0)
        engagement_score_propio = metricas_propias.get('engagement_score', 0)
        
        # Calcular posición relativa
        posicion_rate = self._calcular_posicion_relativa(
            engagement_rate_propio,
            engagement_rates
        )
        posicion_score = self._calcular_posicion_relativa(
            engagement_score_propio,
            engagement_scores
        )
        
        # Análisis de gaps
        gaps = {
            'vs_promedio': {
                'engagement_rate': engagement_rate_propio - estadisticas_competencia['promedio']['engagement_rate'],
                'engagement_score': engagement_score_propio - estadisticas_competencia['promedio']['engagement_score']
            },
            'vs_mejor': {
                'engagement_rate': engagement_rate_propio - estadisticas_competencia['mejor']['engagement_rate'],
                'engagement_score': engagement_score_propio - estadisticas_competencia['mejor']['engagement_score']
            },
            'vs_percentil_75': {
                'engagement_rate': engagement_rate_propio - estadisticas_competencia['percentil_75']['engagement_rate'],
                'engagement_score': engagement_score_propio - estadisticas_competencia['percentil_75']['engagement_score']
            }
        }
        
        # Recomendaciones competitivas
        recomendaciones = self._generar_recomendaciones_competencia(
            gaps,
            posicion_rate,
            posicion_score,
            estadisticas_competencia
        )
        
        return {
            "metricas_propias": metricas_propias,
            "estadisticas_competencia": estadisticas_competencia,
            "posicion_relativa": {
                "engagement_rate": posicion_rate,
                "engagement_score": posicion_score
            },
            "gaps": gaps,
            "recomendaciones": recomendaciones,
            "benchmarking": {
                "vs_promedio": "por_encima" if gaps['vs_promedio']['engagement_rate'] > 0 else "por_debajo",
                "vs_percentil_75": "por_encima" if gaps['vs_percentil_75']['engagement_rate'] > 0 else "por_debajo",
                "vs_mejor": "por_encima" if gaps['vs_mejor']['engagement_rate'] > 0 else "por_debajo"
            }
        }
    
    def _calcular_posicion_relativa(self, valor: float, valores_competencia: List[float]) -> Dict[str, Any]:
        """Calcula posición relativa detallada"""
        if not valores_competencia:
            return {"percentil": 50, "posicion": "medio", "total_competidores": 0}
        
        valores_ordenados = sorted(valores_competencia)
        posicion = sum(1 for v in valores_ordenados if v < valor)
        percentil = int((posicion / len(valores_ordenados)) * 100) if valores_ordenados else 50
        
        if percentil >= 90:
            posicion_label = "top_10"
        elif percentil >= 75:
            posicion_label = "top_25"
        elif percentil >= 50:
            posicion_label = "medio_alto"
        elif percentil >= 25:
            posicion_label = "medio_bajo"
        else:
            posicion_label = "bajo"
        
        return {
            "percentil": percentil,
            "posicion": posicion_label,
            "total_competidores": len(valores_competencia),
            "mejor_que": posicion,
            "peor_que": len(valores_competencia) - posicion
        }
    
    def _generar_recomendaciones_competencia(
        self,
        gaps: Dict[str, Any],
        posicion_rate: Dict[str, Any],
        posicion_score: Dict[str, Any],
        estadisticas: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en análisis competitivo"""
        recomendaciones = []
        
        # Si está por debajo del promedio
        if gaps['vs_promedio']['engagement_rate'] < 0:
            recomendaciones.append({
                "tipo": "mejora_urgente",
                "titulo": "Por debajo del promedio de competencia",
                "descripcion": f"El engagement rate está {abs(gaps['vs_promedio']['engagement_rate']):.2f}% por debajo del promedio",
                "accion": "Revisar estrategia completa y optimizar contenido urgentemente",
                "prioridad": "CRITICA",
                "impacto_esperado": "Alto"
            })
        
        # Si está en percentil bajo
        if posicion_rate['percentil'] < 25:
            recomendaciones.append({
                "tipo": "posicionamiento",
                "titulo": "Posición competitiva baja",
                "descripcion": f"Estás en el percentil {posicion_rate['percentil']} de la competencia",
                "accion": "Analizar estrategias de competidores top y replicar elementos exitosos",
                "prioridad": "ALTA",
                "impacto_esperado": "Alto"
            })
        
        # Si está cerca del top pero no es el mejor
        if posicion_rate['percentil'] >= 75 and gaps['vs_mejor']['engagement_rate'] < 0:
            recomendaciones.append({
                "tipo": "optimizacion_final",
                "titulo": "Cerca del top, optimización final necesaria",
                "descripcion": f"Estás en top 25%, pero {abs(gaps['vs_mejor']['engagement_rate']):.2f}% del líder",
                "accion": "Enfocarse en optimizaciones específicas para alcanzar el liderazgo",
                "prioridad": "MEDIA",
                "impacto_esperado": "Medio"
            })
        
        # Si está en el top
        if posicion_rate['percentil'] >= 90:
            recomendaciones.append({
                "tipo": "mantenimiento",
                "titulo": "Posición de liderazgo",
                "descripcion": "Estás en el top 10% de la competencia",
                "accion": "Mantener estrategia actual y monitorear cambios competitivos",
                "prioridad": "BAJA",
                "impacto_esperado": "Mantenimiento"
            })
        
        return recomendaciones
    
    def analizar_audiencia_profundo(self) -> Dict[str, Any]:
        """
        Análisis profundo de audiencia con múltiples dimensiones
        
        Returns:
            Análisis completo de audiencia
        """
        # Análisis básico de segmentación
        analisis_basico = self.analizador_integraciones.analizar_audiencia_avanzado()
        
        # Análisis adicional de comportamiento
        comportamiento = self._analizar_comportamiento_audiencia()
        
        # Análisis de preferencias
        preferencias = self._analizar_preferencias_audiencia()
        
        # Análisis de engagement por segmento
        engagement_por_segmento = self._analizar_engagement_por_segmento()
        
        # Personas de audiencia
        personas = self._generar_personas_audiencia()
        
        return {
            "segmentacion": analisis_basico,
            "comportamiento": comportamiento,
            "preferencias": preferencias,
            "engagement_por_segmento": engagement_por_segmento,
            "personas": personas,
            "recomendaciones_audiencia": self._generar_recomendaciones_audiencia(
                analisis_basico, comportamiento, preferencias
            )
        }
    
    def _analizar_comportamiento_audiencia(self) -> Dict[str, Any]:
        """Analiza comportamiento de la audiencia"""
        # Análisis de frecuencia de interacción
        interacciones_por_usuario = defaultdict(int)
        for pub in self.analizador.publicaciones:
            # Simular usuarios (en producción vendría de datos reales)
            interacciones_por_usuario[f"user_{hash(pub.id) % 100}"] += pub.engagement_total
        
        frecuencia_interaccion = {
            "alta": sum(1 for v in interacciones_por_usuario.values() if v > 100),
            "media": sum(1 for v in interacciones_por_usuario.values() if 50 <= v <= 100),
            "baja": sum(1 for v in interacciones_por_usuario.values() if v < 50)
        }
        
        return {
            "frecuencia_interaccion": frecuencia_interaccion,
            "usuarios_activos": len(interacciones_por_usuario),
            "promedio_interacciones": statistics.mean(list(interacciones_por_usuario.values())) if interacciones_por_usuario else 0
        }
    
    def _analizar_preferencias_audiencia(self) -> Dict[str, Any]:
        """Analiza preferencias de la audiencia"""
        # Preferencias por tipo de contenido
        preferencias_tipo = defaultdict(lambda: {"total": 0, "engagement": 0})
        for pub in self.analizador.publicaciones:
            preferencias_tipo[pub.tipo_contenido]["total"] += 1
            preferencias_tipo[pub.tipo_contenido]["engagement"] += pub.engagement_total
        
        preferencias_tipo_normalizado = {}
        for tipo, datos in preferencias_tipo.items():
            preferencias_tipo_normalizado[tipo] = {
                "preferencia_score": datos["engagement"] / datos["total"] if datos["total"] > 0 else 0,
                "frecuencia": datos["total"]
            }
        
        # Preferencias por plataforma
        preferencias_plataforma = defaultdict(lambda: {"total": 0, "engagement": 0})
        for pub in self.analizador.publicaciones:
            preferencias_plataforma[pub.plataforma]["total"] += 1
            preferencias_plataforma[pub.plataforma]["engagement"] += pub.engagement_total
        
        preferencias_plataforma_normalizado = {}
        for plataforma, datos in preferencias_plataforma.items():
            preferencias_plataforma_normalizado[plataforma] = {
                "preferencia_score": datos["engagement"] / datos["total"] if datos["total"] > 0 else 0,
                "frecuencia": datos["total"]
            }
        
        return {
            "por_tipo_contenido": preferencias_tipo_normalizado,
            "por_plataforma": preferencias_plataforma_normalizado
        }
    
    def _analizar_engagement_por_segmento(self) -> Dict[str, Any]:
        """Analiza engagement por segmento de audiencia"""
        # Segmentar por nivel de engagement
        segmentos = {
            "alta_interaccion": [],
            "media_interaccion": [],
            "baja_interaccion": []
        }
        
        engagement_scores = [p.engagement_score for p in self.analizador.publicaciones]
        if not engagement_scores:
            return {}
        
        promedio = statistics.mean(engagement_scores)
        desviacion = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
        
        umbral_alto = promedio + desviacion
        umbral_bajo = promedio - desviacion
        
        for pub in self.analizador.publicaciones:
            if pub.engagement_score >= umbral_alto:
                segmentos["alta_interaccion"].append(pub)
            elif pub.engagement_score <= umbral_bajo:
                segmentos["baja_interaccion"].append(pub)
            else:
                segmentos["media_interaccion"].append(pub)
        
        analisis_segmentos = {}
        for segmento_nombre, publicaciones in segmentos.items():
            if publicaciones:
                analisis_segmentos[segmento_nombre] = {
                    "cantidad": len(publicaciones),
                    "engagement_promedio": statistics.mean([p.engagement_score for p in publicaciones]),
                    "engagement_rate_promedio": statistics.mean([p.engagement_rate for p in publicaciones]),
                    "caracteristicas": {
                        "tipos_preferidos": self._contar_tipos(publicaciones),
                        "plataformas_preferidas": self._contar_plataformas(publicaciones),
                        "horarios_optimos": self._analizar_horarios_segmento(publicaciones)
                    }
                }
        
        return analisis_segmentos
    
    def _contar_tipos(self, publicaciones: List[Publicacion]) -> Dict[str, int]:
        """Cuenta tipos de contenido"""
        conteo = defaultdict(int)
        for pub in publicaciones:
            conteo[pub.tipo_contenido] += 1
        return dict(conteo)
    
    def _contar_plataformas(self, publicaciones: List[Publicacion]) -> Dict[str, int]:
        """Cuenta plataformas"""
        conteo = defaultdict(int)
        for pub in publicaciones:
            conteo[pub.plataforma] += 1
        return dict(conteo)
    
    def _analizar_horarios_segmento(self, publicaciones: List[Publicacion]) -> Dict[str, Any]:
        """Analiza horarios óptimos para un segmento"""
        horarios = defaultdict(list)
        for pub in publicaciones:
            hora = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
            horarios[hora].append(pub.engagement_score)
        
        if horarios:
            mejor_horario = max(horarios.items(), key=lambda x: statistics.mean(x[1]))
            return {
                "mejor_hora": mejor_horario[0],
                "score_promedio": statistics.mean(mejor_horario[1])
            }
        return {}
    
    def _generar_personas_audiencia(self) -> List[Dict[str, Any]]:
        """Genera personas de audiencia basadas en segmentos"""
        analisis_segmentos = self._analizar_engagement_por_segmento()
        
        personas = []
        nombres_personas = {
            "alta_interaccion": "Super Engagers",
            "media_interaccion": "Engagers Regulares",
            "baja_interaccion": "Engagers Ocasionales"
        }
        
        for segmento, datos in analisis_segmentos.items():
            caracteristicas = datos.get('caracteristicas', {})
            tipos_preferidos = caracteristicas.get('tipos_preferidos', {})
            plataformas_preferidas = caracteristicas.get('plataformas_preferidas', {})
            
            tipo_preferido = max(tipos_preferidos.items(), key=lambda x: x[1])[0] if tipos_preferidos else 'Y'
            plataforma_preferida = max(plataformas_preferidas.items(), key=lambda x: x[1])[0] if plataformas_preferidas else 'Instagram'
            
            personas.append({
                "nombre": nombres_personas.get(segmento, segmento),
                "segmento": segmento,
                "tamaño": datos['cantidad'],
                "engagement_promedio": datos['engagement_promedio'],
                "caracteristicas": {
                    "tipo_contenido_preferido": tipo_preferido,
                    "plataforma_preferida": plataforma_preferida,
                    "horario_optimo": caracteristicas.get('horarios_optimos', {}).get('mejor_hora', 10)
                },
                "estrategia_recomendada": self._generar_estrategia_persona(segmento, tipo_preferido, plataforma_preferida)
            })
        
        return personas
    
    def _generar_estrategia_persona(
        self,
        segmento: str,
        tipo_preferido: str,
        plataforma_preferida: str
    ) -> str:
        """Genera estrategia recomendada para una persona"""
        estrategias = {
            "alta_interaccion": f"Crear más contenido tipo {tipo_preferido} en {plataforma_preferida} para maximizar engagement",
            "media_interaccion": f"Optimizar contenido tipo {tipo_preferido} en {plataforma_preferida} para aumentar engagement",
            "baja_interaccion": f"Experimentar con diferentes tipos y plataformas para reactivar este segmento"
        }
        return estrategias.get(segmento, "Revisar estrategia para este segmento")
    
    def _generar_recomendaciones_audiencia(
        self,
        segmentacion: Dict[str, Any],
        comportamiento: Dict[str, Any],
        preferencias: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en análisis de audiencia"""
        recomendaciones = []
        
        # Recomendación basada en segmentación
        if segmentacion.get('segmentos'):
            mejor_segmento = max(
                segmentacion['segmentos'].items(),
                key=lambda x: x[1].get('engagement_promedio', 0)
            )
            recomendaciones.append({
                "tipo": "segmentacion",
                "titulo": f"Enfocar en segmento {mejor_segmento[0]}",
                "descripcion": f"Este segmento tiene el mejor engagement promedio",
                "accion": f"Crear más contenido para el segmento {mejor_segmento[0]}",
                "prioridad": "ALTA"
            })
        
        # Recomendación basada en preferencias
        if preferencias.get('por_tipo_contenido'):
            mejor_tipo = max(
                preferencias['por_tipo_contenido'].items(),
                key=lambda x: x[1].get('preferencia_score', 0)
            )
            recomendaciones.append({
                "tipo": "contenido",
                "titulo": f"Incrementar contenido tipo {mejor_tipo[0]}",
                "descripcion": f"La audiencia muestra mayor preferencia por este tipo",
                "accion": f"Aumentar frecuencia de contenido tipo {mejor_tipo[0]}",
                "prioridad": "MEDIA"
            })
        
        return recomendaciones
    
    def analizar_funnel_engagement(self) -> Dict[str, Any]:
        """
        Analiza funnel de engagement (impresiones -> reach -> engagement)
        
        Returns:
            Análisis del funnel completo
        """
        total_impresiones = sum(p.impresiones for p in self.analizador.publicaciones)
        total_reach = sum(p.reach for p in self.analizador.publicaciones)
        total_engagement = sum(p.engagement_total for p in self.analizador.publicaciones)
        
        tasa_reach = (total_reach / total_impresiones * 100) if total_impresiones > 0 else 0
        tasa_engagement = (total_engagement / total_reach * 100) if total_reach > 0 else 0
        tasa_conversion_total = (total_engagement / total_impresiones * 100) if total_impresiones > 0 else 0
        
        # Análisis por etapa del funnel
        etapas = {
            "impresiones": {
                "total": total_impresiones,
                "porcentaje": 100.0
            },
            "reach": {
                "total": total_reach,
                "porcentaje": tasa_reach,
                "perdida": 100 - tasa_reach
            },
            "engagement": {
                "total": total_engagement,
                "porcentaje": tasa_engagement,
                "perdida": 100 - tasa_engagement
            }
        }
        
        # Identificar cuellos de botella
        cuellos_botella = []
        if tasa_reach < 70:
            cuellos_botella.append({
                "etapa": "Reach",
                "problema": f"Solo {tasa_reach:.1f}% de impresiones alcanzan reach",
                "accion": "Mejorar targeting y relevancia del contenido"
            })
        
        if tasa_engagement < 5:
            cuellos_botella.append({
                "etapa": "Engagement",
                "problema": f"Solo {tasa_engagement:.1f}% de reach genera engagement",
                "accion": "Optimizar contenido para mayor interacción"
            })
        
        return {
            "etapas": etapas,
            "tasas": {
                "reach_rate": tasa_reach,
                "engagement_rate": tasa_engagement,
                "conversion_total": tasa_conversion_total
            },
            "cuellos_botella": cuellos_botella,
            "recomendaciones": self._generar_recomendaciones_funnel(cuellos_botella, etapas)
        }
    
    def _generar_recomendaciones_funnel(
        self,
        cuellos_botella: List[Dict[str, Any]],
        etapas: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones para optimizar el funnel"""
        recomendaciones = []
        
        if cuellos_botella:
            for cuello in cuellos_botella:
                recomendaciones.append(f"{cuello['etapa']}: {cuello['accion']}")
        else:
            recomendaciones.append("Funnel optimizado, mantener estrategia actual")
        
        return recomendaciones
    
    def analizar_retencion(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Analiza retención de audiencia
        
        Args:
            periodo_dias: Período para análisis de retención
        
        Returns:
            Análisis de retención
        """
        fecha_limite = datetime.now() - timedelta(days=periodo_dias)
        publicaciones_recientes = [
            p for p in self.analizador.publicaciones
            if p.fecha_publicacion >= fecha_limite
        ]
        
        # Agrupar por semana
        semanas = defaultdict(list)
        for pub in publicaciones_recientes:
            semana = pub.fecha_publicacion.isocalendar()[1]
            año = pub.fecha_publicacion.year
            clave = f"{año}-W{semana}"
            semanas[clave].append(pub)
        
        # Calcular engagement por semana
        engagement_semanal = {}
        for semana_key in sorted(semanas.keys()):
            publicaciones_semana = semanas[semana_key]
            engagement_semanal[semana_key] = {
                "engagement_total": sum(p.engagement_total for p in publicaciones_semana),
                "engagement_promedio": statistics.mean([p.engagement_total for p in publicaciones_semana]) if publicaciones_semana else 0,
                "publicaciones": len(publicaciones_semana)
            }
        
        # Calcular tasa de retención (comparar semana a semana)
        tasas_retencion = []
        semanas_ordenadas = sorted(engagement_semanal.keys())
        for i in range(1, len(semanas_ordenadas)):
            semana_anterior = engagement_semanal[semanas_ordenadas[i-1]]
            semana_actual = engagement_semanal[semanas_ordenadas[i]]
            
            if semana_anterior['engagement_total'] > 0:
                tasa = (semana_actual['engagement_total'] / semana_anterior['engagement_total']) * 100
                tasas_retencion.append({
                    "semana": semanas_ordenadas[i],
                    "tasa_retencion": tasa,
                    "tendencia": "creciente" if tasa >= 100 else "decreciente"
                })
        
        tasa_retencion_promedio = statistics.mean([t['tasa_retencion'] for t in tasas_retencion]) if tasas_retencion else 100
        
        return {
            "periodo_analizado": f"{periodo_dias} días",
            "semanas_analizadas": len(semanas),
            "engagement_semanal": engagement_semanal,
            "tasas_retencion": tasas_retencion,
            "tasa_retencion_promedio": tasa_retencion_promedio,
            "tendencia": "positiva" if tasa_retencion_promedio >= 100 else "negativa"
        }


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de BI para Engagement')
    parser.add_argument('--publicaciones', type=int, default=50, help='Número de publicaciones')
    parser.add_argument('--competencia', action='store_true', help='Analizar competencia')
    parser.add_argument('--audiencia', action='store_true', help='Análisis profundo de audiencia')
    parser.add_argument('--funnel', action='store_true', help='Analizar funnel de engagement')
    parser.add_argument('--retencion', action='store_true', help='Analizar retención')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_bi = AnalizadorBIEngagement(analizador_base)
    
    # Análisis de competencia
    if args.competencia:
        print("\n🏆 Analizando competencia avanzado...")
        datos_competencia = [
            {"engagement_rate": 2.5, "engagement_score": 300},
            {"engagement_rate": 3.1, "engagement_score": 350},
            {"engagement_rate": 2.8, "engagement_score": 320},
            {"engagement_rate": 4.2, "engagement_score": 450}
        ]
        
        reporte = analizador_base.generar_reporte()
        resumen = reporte.get('resumen_ejecutivo', {})
        metricas_propias = {
            "engagement_rate": resumen.get('engagement_rate_promedio', 0),
            "engagement_score": resumen.get('engagement_score_promedio', 0)
        }
        
        analisis_comp = analizador_bi.analizar_competencia_avanzado(datos_competencia, metricas_propias)
        
        print(f"\n📊 Posición Relativa:")
        print(f"   Engagement Rate: Percentil {analisis_comp['posicion_relativa']['engagement_rate']['percentil']}")
        print(f"   Engagement Score: Percentil {analisis_comp['posicion_relativa']['engagement_score']['percentil']}")
        
        print(f"\n💡 Recomendaciones:")
        for rec in analisis_comp['recomendaciones']:
            print(f"   [{rec['prioridad']}] {rec['titulo']}")
    
    # Análisis de audiencia
    if args.audiencia:
        print("\n👥 Analizando audiencia profundo...")
        analisis_audiencia = analizador_bi.analizar_audiencia_profundo()
        
        print(f"\n📊 Personas de Audiencia:")
        for persona in analisis_audiencia.get('personas', []):
            print(f"\n   {persona['nombre']}:")
            print(f"     Tamaño: {persona['tamaño']} publicaciones")
            print(f"     Engagement: {persona['engagement_promedio']:.1f}")
            print(f"     Estrategia: {persona['estrategia_recomendada']}")
    
    # Análisis de funnel
    if args.funnel:
        print("\n� funnel Analizando funnel de engagement...")
        funnel = analizador_bi.analizar_funnel_engagement()
        
        print(f"\n📊 Etapas del Funnel:")
        for etapa, datos in funnel['etapas'].items():
            print(f"   {etapa.capitalize()}: {datos['total']} ({datos['porcentaje']:.1f}%)")
        
        if funnel['cuellos_botella']:
            print(f"\n⚠️  Cuellos de Botella:")
            for cuello in funnel['cuellos_botella']:
                print(f"   {cuello['etapa']}: {cuello['problema']}")
    
    # Análisis de retención
    if args.retencion:
        print("\n📈 Analizando retención...")
        retencion = analizador_bi.analizar_retencion(periodo_dias=30)
        
        print(f"\n📊 Retención:")
        print(f"   Tasa promedio: {retencion['tasa_retencion_promedio']:.1f}%")
        print(f"   Tendencia: {retencion['tendencia']}")


if __name__ == "__main__":
    main()


