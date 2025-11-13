#!/usr/bin/env python3
"""
Análisis Predictivo Avanzado de Engagement - Mejoras Premium
=============================================================
Análisis predictivo avanzado:
- Predicción de tendencias futuras
- Predicción de contenido viral con ML
- Predicción de ROI futuro
- Predicción de retención
- Análisis de escenarios (what-if)
- Predicción de mejor momento para publicar
- Predicción de mejor tipo de contenido
- Análisis de sensibilidad
- Modelos predictivos avanzados
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
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
    from analisis_engagement_ml import AnalizadorEngagementML
    from analisis_engagement_roi import AnalizadorROIEngagement
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorPredictivoEngagement:
    """Analizador predictivo avanzado de engagement"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None,
        analizador_ml: Optional[AnalizadorEngagementML] = None,
        analizador_roi: Optional[AnalizadorROIEngagement] = None
    ):
        """
        Inicializa el analizador predictivo
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
            analizador_ml: Instancia opcional del AnalizadorEngagementML
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
        self.analizador_roi = analizador_roi or AnalizadorROIEngagement(
            analizador_base, self.analizador_ai, self.analizador_mejorado
        )
    
    def predecir_tendencias_futuras(
        self,
        semanas_futuras: int = 4,
        incluir_intervalos_confianza: bool = True
    ) -> Dict[str, Any]:
        """
        Predice tendencias futuras de engagement
        
        Args:
            semanas_futuras: Número de semanas a predecir
            incluir_intervalos_confianza: Si incluir intervalos de confianza
        
        Returns:
            Predicción de tendencias futuras
        """
        # Analizar tendencias históricas
        tendencias = self.analizador_mejorado.analizar_tendencias_temporales(dias=60)
        
        if 'error' in tendencias:
            return {"error": "Datos insuficientes para predicción"}
        
        semanas_analizadas = tendencias.get('semanas_analizadas', [])
        if len(semanas_analizadas) < 2:
            return {"error": "Se necesitan al menos 2 semanas de datos"}
        
        # Calcular tasa de cambio promedio
        cambios_semanales = []
        for i in range(1, len(semanas_analizadas)):
            cambio = semanas_analizadas[i]['engagement_score_promedio'] - semanas_analizadas[i-1]['engagement_score_promedio']
            cambios_semanales.append(cambio)
        
        cambio_promedio = statistics.mean(cambios_semanales) if cambios_semanales else 0
        ultimo_score = semanas_analizadas[-1]['engagement_score_promedio']
        
        # Calcular desviación estándar para intervalos de confianza
        desviacion = statistics.stdev(cambios_semanales) if len(cambios_semanales) > 1 else abs(cambio_promedio) * 0.3
        
        # Generar predicciones
        predicciones = []
        fecha_base = datetime.now()
        
        for semana in range(1, semanas_futuras + 1):
            score_predicho = ultimo_score + (cambio_promedio * semana)
            
            prediccion = {
                "semana": semana,
                "fecha": (fecha_base + timedelta(weeks=semana)).strftime('%Y-%m-%d'),
                "engagement_score_predicho": max(0, round(score_predicho, 1)),
                "tendencia": "creciente" if cambio_promedio > 0 else "decreciente" if cambio_promedio < 0 else "estable"
            }
            
            if incluir_intervalos_confianza:
                # Intervalo de confianza del 95%
                margen_error = 1.96 * desviacion * math.sqrt(semana)
                prediccion["intervalo_confianza"] = {
                    "minimo": max(0, round(score_predicho - margen_error, 1)),
                    "maximo": round(score_predicho + margen_error, 1),
                    "nivel_confianza": 95
                }
            
            predicciones.append(prediccion)
        
        return {
            "periodo_prediccion": f"{semanas_futuras} semanas",
            "tendencia_actual": tendencias.get('tendencia', 'estable'),
            "cambio_semanal_promedio": round(cambio_promedio, 2),
            "predicciones": predicciones,
            "confianza_general": self._calcular_confianza_prediccion(semanas_analizadas, cambios_semanales)
        }
    
    def _calcular_confianza_prediccion(
        self,
        semanas_analizadas: List[Dict[str, Any]],
        cambios_semanales: List[float]
    ) -> float:
        """Calcula confianza general de la predicción"""
        if len(semanas_analizadas) < 3:
            return 50.0
        
        # Más datos = mayor confianza
        confianza_por_datos = min(100, len(semanas_analizadas) * 10)
        
        # Menor variabilidad = mayor confianza
        if cambios_semanales:
            variabilidad = statistics.stdev(cambios_semanales) if len(cambios_semanales) > 1 else 0
            promedio_absoluto = abs(statistics.mean(cambios_semanales))
            confianza_por_estabilidad = max(0, 100 - (variabilidad / max(promedio_absoluto, 1)) * 50) if promedio_absoluto > 0 else 50
        else:
            confianza_por_estabilidad = 50
        
        # Confianza combinada
        confianza = (confianza_por_datos * 0.4 + confianza_por_estabilidad * 0.6)
        return round(confianza, 1)
    
    def predecir_mejor_momento_publicar(
        self,
        tipo_contenido: str,
        plataforma: str,
        rango_horas: Tuple[int, int] = (6, 22),
        dias_semana: List[str] = None
    ) -> Dict[str, Any]:
        """
        Predice el mejor momento para publicar
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            plataforma: Plataforma objetivo
            rango_horas: Rango de horas a analizar (inicio, fin)
            dias_semana: Días de la semana a considerar
        
        Returns:
            Mejor momento predicho con predicciones por opción
        """
        if dias_semana is None:
            dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Analizar rendimiento histórico por hora y día
        rendimiento_opciones = []
        
        for dia in dias_semana:
            for hora in range(rango_horas[0], rango_horas[1] + 1):
                # Filtrar publicaciones similares
                publicaciones_similares = [
                    p for p in self.analizador.publicaciones
                    if p.tipo_contenido == tipo_contenido and
                    p.plataforma == plataforma and
                    p.metadata.get('dia_semana', p.fecha_publicacion.strftime('%A')) == dia and
                    p.metadata.get('hora_publicacion', p.fecha_publicacion.hour) == hora
                ]
                
                if publicaciones_similares:
                    engagement_promedio = statistics.mean([p.engagement_score for p in publicaciones_similares])
                    rendimiento_opciones.append({
                        "dia": dia,
                        "hora": hora,
                        "engagement_promedio": engagement_promedio,
                        "muestra": len(publicaciones_similares)
                    })
        
        # Si no hay datos históricos suficientes, usar predicción ML
        if not rendimiento_opciones:
            # Usar predicción ML para cada opción
            for dia in dias_semana:
                for hora in range(rango_horas[0], rango_horas[1] + 1):
                    try:
                        prediccion_ml = self.analizador_ml.predecir_engagement_ml(
                            tipo_contenido=tipo_contenido,
                            plataforma=plataforma,
                            hora=hora,
                            dia_semana=dia,
                            tiene_media=True,
                            hashtags=[],
                            titulo=""
                        )
                        rendimiento_opciones.append({
                            "dia": dia,
                            "hora": hora,
                            "engagement_promedio": prediccion_ml.get('engagement_score_predicho', 0),
                            "muestra": 0,
                            "prediccion_ml": True,
                            "confianza": prediccion_ml.get('confianza', 0)
                        })
                    except:
                        pass
        
        if not rendimiento_opciones:
            return {"error": "No se pueden generar predicciones con los datos disponibles"}
        
        # Encontrar mejor opción
        mejor_opcion = max(rendimiento_opciones, key=lambda x: x['engagement_promedio'])
        
        # Top 5 opciones
        top_opciones = sorted(rendimiento_opciones, key=lambda x: x['engagement_promedio'], reverse=True)[:5]
        
        return {
            "mejor_momento": {
                "dia": mejor_opcion['dia'],
                "hora": mejor_opcion['hora'],
                "engagement_predicho": round(mejor_opcion['engagement_promedio'], 1),
                "confianza": mejor_opcion.get('confianza', 100 if mejor_opcion['muestra'] > 0 else 50)
            },
            "top_opciones": [
                {
                    "dia": opt['dia'],
                    "hora": opt['hora'],
                    "engagement_predicho": round(opt['engagement_promedio'], 1),
                    "confianza": opt.get('confianza', 100 if opt['muestra'] > 0 else 50)
                }
                for opt in top_opciones
            ],
            "total_opciones_analizadas": len(rendimiento_opciones)
        }
    
    def predecir_mejor_tipo_contenido(
        self,
        plataforma: str,
        contexto: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Predice el mejor tipo de contenido para una plataforma
        
        Args:
            plataforma: Plataforma objetivo
            contexto: Contexto adicional (opcional)
        
        Returns:
            Predicción del mejor tipo de contenido
        """
        # Analizar rendimiento histórico por tipo en la plataforma
        rendimiento_por_tipo = {}
        
        for tipo in ['X', 'Y', 'Z']:
            publicaciones_tipo = [
                p for p in self.analizador.publicaciones
                if p.tipo_contenido == tipo and p.plataforma == plataforma
            ]
            
            if publicaciones_tipo:
                rendimiento_por_tipo[tipo] = {
                    "engagement_promedio": statistics.mean([p.engagement_score for p in publicaciones_tipo]),
                    "engagement_rate_promedio": statistics.mean([p.engagement_rate for p in publicaciones_tipo]),
                    "muestra": len(publicaciones_tipo),
                    "viral_promedio": sum(1 for p in publicaciones_tipo if p.es_viral) / len(publicaciones_tipo) * 100
                }
            else:
                # Usar predicción ML si no hay datos históricos
                try:
                    prediccion_ml = self.analizador_ml.predecir_engagement_ml(
                        tipo_contenido=tipo,
                        plataforma=plataforma,
                        hora=10,
                        dia_semana='Wednesday',
                        tiene_media=True
                    )
                    rendimiento_por_tipo[tipo] = {
                        "engagement_promedio": prediccion_ml.get('engagement_score_predicho', 0),
                        "engagement_rate_promedio": 0,
                        "muestra": 0,
                        "viral_promedio": 0,
                        "prediccion_ml": True
                    }
                except:
                    rendimiento_por_tipo[tipo] = {
                        "engagement_promedio": 0,
                        "engagement_rate_promedio": 0,
                        "muestra": 0,
                        "viral_promedio": 0
                    }
        
        if not rendimiento_por_tipo:
            return {"error": "No hay datos para predicción"}
        
        # Encontrar mejor tipo
        mejor_tipo = max(rendimiento_por_tipo.items(), key=lambda x: x[1]['engagement_promedio'])
        
        # Ranking de tipos
        ranking = sorted(rendimiento_por_tipo.items(), key=lambda x: x[1]['engagement_promedio'], reverse=True)
        
        return {
            "mejor_tipo": {
                "tipo": mejor_tipo[0],
                "engagement_predicho": round(mejor_tipo[1]['engagement_promedio'], 1),
                "engagement_rate_predicho": round(mejor_tipo[1]['engagement_rate_promedio'], 2),
                "viral_promedio": round(mejor_tipo[1]['viral_promedio'], 1)
            },
            "ranking_tipos": [
                {
                    "tipo": tipo,
                    "engagement_predicho": round(datos['engagement_promedio'], 1),
                    "engagement_rate_predicho": round(datos['engagement_rate_promedio'], 2),
                    "muestra": datos['muestra']
                }
                for tipo, datos in ranking
            ],
            "recomendacion": self._generar_recomendacion_tipo(mejor_tipo[0], mejor_tipo[1], contexto)
        }
    
    def _generar_recomendacion_tipo(
        self,
        mejor_tipo: str,
        datos: Dict[str, Any],
        contexto: Optional[Dict[str, Any]]
    ) -> str:
        """Genera recomendación para tipo de contenido"""
        nombres_tipos = {
            'X': 'Tutoriales/Educativos',
            'Y': 'Entretenimiento/Viral',
            'Z': 'Promocional/Producto'
        }
        
        recomendacion = f"El tipo de contenido {nombres_tipos.get(mejor_tipo, mejor_tipo)} muestra mejor rendimiento"
        
        if datos.get('muestra', 0) > 0:
            recomendacion += f" con {datos['muestra']} publicaciones históricas"
        
        if datos.get('viral_promedio', 0) > 5:
            recomendacion += f" y alto potencial viral ({datos['viral_promedio']:.1f}%)"
        
        return recomendacion
    
    def analizar_escenarios_what_if(
        self,
        escenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza escenarios what-if (qué pasaría si...)
        
        Args:
            escenarios: Lista de escenarios a analizar
        
        Returns:
            Análisis de escenarios con predicciones
        """
        analisis_escenarios = []
        
        for i, escenario in enumerate(escenarios, 1):
            # Simular escenario
            prediccion = self._simular_escenario(escenario)
            
            analisis_escenarios.append({
                "escenario_numero": i,
                "nombre": escenario.get('nombre', f'Escenario {i}'),
                "descripcion": escenario.get('descripcion', ''),
                "cambios": escenario.get('cambios', {}),
                "prediccion": prediccion,
                "impacto_estimado": self._calcular_impacto_escenario(prediccion)
            })
        
        # Comparar escenarios
        mejor_escenario = max(analisis_escenarios, key=lambda x: x['prediccion'].get('engagement_score_predicho', 0))
        
        return {
            "escenarios_analizados": len(escenarios),
            "escenarios": analisis_escenarios,
            "mejor_escenario": mejor_escenario,
            "recomendacion": f"Escenario recomendado: {mejor_escenario['nombre']}"
        }
    
    def _simular_escenario(self, escenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simula un escenario y predice resultados"""
        cambios = escenario.get('cambios', {})
        
        # Obtener predicción base
        tipo = cambios.get('tipo_contenido', 'Y')
        plataforma = cambios.get('plataforma', 'Instagram')
        hora = cambios.get('hora', 10)
        dia = cambios.get('dia_semana', 'Wednesday')
        
        # Predicción base
        try:
            prediccion_base = self.analizador_ml.predecir_engagement_ml(
                tipo_contenido=tipo,
                plataforma=plataforma,
                hora=hora,
                dia_semana=dia,
                tiene_media=cambios.get('tiene_media', True),
                hashtags=cambios.get('hashtags', []),
                titulo=cambios.get('titulo', '')
            )
            
            engagement_base = prediccion_base.get('engagement_score_predicho', 0)
            
            # Aplicar modificadores del escenario
            modificadores = cambios.get('modificadores', {})
            engagement_ajustado = engagement_base
            
            if 'aumentar_engagement' in modificadores:
                engagement_ajustado *= (1 + modificadores['aumentar_engagement'] / 100)
            
            if 'cambiar_frecuencia' in modificadores:
                # Ajustar por frecuencia (más publicaciones = más engagement total)
                engagement_ajustado *= modificadores['cambiar_frecuencia']
            
            return {
                "engagement_score_predicho": round(engagement_ajustado, 1),
                "engagement_rate_predicho": round(prediccion_base.get('engagement_rate_predicho_ajustado', 0), 2),
                "confianza": prediccion_base.get('confianza', 50),
                "factores_aplicados": modificadores
            }
        except:
            return {
                "engagement_score_predicho": 0,
                "engagement_rate_predicho": 0,
                "confianza": 0,
                "error": "No se pudo simular el escenario"
            }
    
    def _calcular_impacto_escenario(self, prediccion: Dict[str, Any]) -> str:
        """Calcula impacto estimado de un escenario"""
        engagement = prediccion.get('engagement_score_predicho', 0)
        
        if engagement > 500:
            return "Muy Alto"
        elif engagement > 300:
            return "Alto"
        elif engagement > 150:
            return "Medio"
        else:
            return "Bajo"
    
    def analizar_sensibilidad(
        self,
        variable: str,
        valores: List[Any],
        contexto_base: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Análisis de sensibilidad (cómo cambia el resultado al variar una variable)
        
        Args:
            variable: Variable a analizar (tipo_contenido, plataforma, hora, etc.)
            valores: Valores a probar
            contexto_base: Contexto base para la predicción
        
        Returns:
            Análisis de sensibilidad
        """
        resultados = []
        
        for valor in valores:
            contexto_test = contexto_base.copy()
            contexto_test[variable] = valor
            
            try:
                prediccion = self.analizador_ml.predecir_engagement_ml(
                    tipo_contenido=contexto_test.get('tipo_contenido', 'Y'),
                    plataforma=contexto_test.get('plataforma', 'Instagram'),
                    hora=contexto_test.get('hora', 10),
                    dia_semana=contexto_test.get('dia_semana', 'Wednesday'),
                    tiene_media=contexto_test.get('tiene_media', True),
                    hashtags=contexto_test.get('hashtags', []),
                    titulo=contexto_test.get('titulo', '')
                )
                
                resultados.append({
                    "valor": valor,
                    "engagement_predicho": prediccion.get('engagement_score_predicho', 0),
                    "confianza": prediccion.get('confianza', 0)
                })
            except:
                resultados.append({
                    "valor": valor,
                    "engagement_predicho": 0,
                    "confianza": 0,
                    "error": "No se pudo calcular"
                })
        
        if not resultados:
            return {"error": "No se pudieron calcular resultados"}
        
        # Encontrar mejor y peor valor
        mejor_resultado = max(resultados, key=lambda x: x['engagement_predicho'])
        peor_resultado = min(resultados, key=lambda x: x['engagement_predicho'])
        
        # Calcular sensibilidad (variación)
        engagement_values = [r['engagement_predicho'] for r in resultados if r['engagement_predicho'] > 0]
        if engagement_values:
            variacion = max(engagement_values) - min(engagement_values)
            sensibilidad_relativa = (variacion / statistics.mean(engagement_values) * 100) if statistics.mean(engagement_values) > 0 else 0
        else:
            variacion = 0
            sensibilidad_relativa = 0
        
        return {
            "variable_analizada": variable,
            "valores_probados": valores,
            "resultados": resultados,
            "mejor_valor": mejor_resultado['valor'],
            "peor_valor": peor_resultado['valor'],
            "variacion_absoluta": round(variacion, 1),
            "sensibilidad_relativa": round(sensibilidad_relativa, 1),
            "sensibilidad": "Alta" if sensibilidad_relativa > 30 else "Media" if sensibilidad_relativa > 10 else "Baja"
        }


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis Predictivo de Engagement')
    parser.add_argument('--publicaciones', type=int, default=50, help='Número de publicaciones')
    parser.add_argument('--tendencias', action='store_true', help='Predecir tendencias futuras')
    parser.add_argument('--mejor-momento', action='store_true', help='Predecir mejor momento')
    parser.add_argument('--mejor-tipo', action='store_true', help='Predecir mejor tipo')
    parser.add_argument('--escenarios', action='store_true', help='Analizar escenarios what-if')
    parser.add_argument('--sensibilidad', action='store_true', help='Análisis de sensibilidad')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_predictivo = AnalizadorPredictivoEngagement(analizador_base)
    
    # Predicción de tendencias
    if args.tendencias:
        print("\n📈 Prediciendo tendencias futuras...")
        tendencias = analizador_predictivo.predecir_tendencias_futuras(semanas_futuras=4)
        
        if 'error' not in tendencias:
            print(f"\n✅ Predicción para {tendencias['periodo_prediccion']}:")
            print(f"   Confianza: {tendencias['confianza_general']}%")
            print(f"   Tendencia: {tendencias['tendencia_actual']}")
            
            for pred in tendencias['predicciones']:
                print(f"\n   Semana {pred['semana']} ({pred['fecha']}):")
                print(f"     Engagement Score: {pred['engagement_score_predicho']}")
                if 'intervalo_confianza' in pred:
                    intervalo = pred['intervalo_confianza']
                    print(f"     Intervalo 95%: {intervalo['minimo']} - {intervalo['maximo']}")
    
    # Mejor momento
    if args.mejor_momento:
        print("\n⏰ Prediciendo mejor momento para publicar...")
        mejor_momento = analizador_predictivo.predecir_mejor_momento_publicar(
            tipo_contenido='Y',
            plataforma='Instagram'
        )
        
        if 'error' not in mejor_momento:
            mejor = mejor_momento['mejor_momento']
            print(f"\n✅ Mejor momento:")
            print(f"   Día: {mejor['dia']}")
            print(f"   Hora: {mejor['hora']}:00")
            print(f"   Engagement Predicho: {mejor['engagement_predicho']}")
            print(f"   Confianza: {mejor['confianza']}%")
    
    # Mejor tipo
    if args.mejor_tipo:
        print("\n📝 Prediciendo mejor tipo de contenido...")
        mejor_tipo = analizador_predictivo.predecir_mejor_tipo_contenido(
            plataforma='Instagram'
        )
        
        if 'error' not in mejor_tipo:
            mejor = mejor_tipo['mejor_tipo']
            print(f"\n✅ Mejor tipo: {mejor['tipo']}")
            print(f"   Engagement Predicho: {mejor['engagement_predicho']}")
            print(f"   Recomendación: {mejor_tipo['recomendacion']}")
    
    # Escenarios
    if args.escenarios:
        print("\n🔮 Analizando escenarios what-if...")
        escenarios = [
            {
                "nombre": "Aumentar frecuencia",
                "descripcion": "Publicar 2x más contenido",
                "cambios": {
                    "tipo_contenido": "Y",
                    "plataforma": "Instagram",
                    "modificadores": {"cambiar_frecuencia": 2.0}
                }
            },
            {
                "nombre": "Optimizar timing",
                "descripcion": "Publicar en mejor horario",
                "cambios": {
                    "tipo_contenido": "Y",
                    "plataforma": "Instagram",
                    "hora": 10,
                    "modificadores": {"aumentar_engagement": 20}
                }
            }
        ]
        
        analisis = analizador_predictivo.analizar_escenarios_what_if(escenarios)
        print(f"\n✅ {analisis['recomendacion']}")
        print(f"   Mejor escenario: {analisis['mejor_escenario']['nombre']}")
        print(f"   Engagement predicho: {analisis['mejor_escenario']['prediccion']['engagement_score_predicho']}")
    
    # Sensibilidad
    if args.sensibilidad:
        print("\n📊 Análisis de sensibilidad...")
        sensibilidad = analizador_predictivo.analizar_sensibilidad(
            variable="hora",
            valores=[6, 9, 12, 15, 18, 21],
            contexto_base={
                "tipo_contenido": "Y",
                "plataforma": "Instagram",
                "dia_semana": "Wednesday"
            }
        )
        
        if 'error' not in sensibilidad:
            print(f"\n✅ Sensibilidad: {sensibilidad['sensibilidad']}")
            print(f"   Mejor hora: {sensibilidad['mejor_valor']}")
            print(f"   Variación: {sensibilidad['variacion_absoluta']} puntos")


if __name__ == "__main__":
    main()


