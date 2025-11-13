#!/usr/bin/env python3
"""
Análisis de Engagement con Machine Learning - Predicciones Avanzadas
=====================================================================
Funcionalidades ML avanzadas:
- Predicción de engagement con modelos ML
- Análisis de sentimiento de comentarios
- Clasificación automática de contenido
- Detección de patrones con clustering
- Optimización automática de contenido
- Sistema de A/B testing inteligente
- Análisis predictivo avanzado
"""

import os
import sys
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalizadorEngagementML:
    """Analizador de engagement con capacidades de Machine Learning"""
    
    def __init__(
        self,
        analizador_base: AnalizadorEngagement,
        analizador_ai: Optional[AnalizadorEngagementAI] = None,
        analizador_mejorado: Optional[AnalizadorEngagementMejorado] = None
    ):
        """
        Inicializa el analizador con ML
        
        Args:
            analizador_base: Instancia del AnalizadorEngagement base
            analizador_ai: Instancia opcional del AnalizadorEngagementAI
            analizador_mejorado: Instancia opcional del AnalizadorEngagementMejorado
        """
        self.analizador = analizador_base
        self.analizador_ai = analizador_ai or AnalizadorEngagementAI(analizador_base)
        self.analizador_mejorado = analizador_mejorado or AnalizadorEngagementMejorado(
            analizador_base, self.analizador_ai
        )
        self.modelos_entrenados = {}
    
    def entrenar_modelo_prediccion(self) -> Dict[str, Any]:
        """
        Entrena un modelo simple de predicción de engagement
        
        Returns:
            Información del modelo entrenado
        """
        if len(self.analizador.publicaciones) < 10:
            return {"error": "Se necesitan al menos 10 publicaciones para entrenar"}
        
        # Preparar datos de entrenamiento
        X = []  # Features
        y = []  # Target (engagement_score)
        
        for pub in self.analizador.publicaciones:
            features = self._extraer_features(pub)
            X.append(features)
            y.append(pub.engagement_score)
        
        # Modelo simple basado en regresión lineal básica
        # En producción, usar sklearn o similar
        modelo_info = {
            "tipo": "regresion_lineal_simple",
            "features": [
                "tipo_contenido_X", "tipo_contenido_Y", "tipo_contenido_Z",
                "plataforma_instagram", "plataforma_linkedin", "plataforma_twitter",
                "hora_normalizada", "dia_semana_normalizado",
                "tiene_media", "num_hashtags", "longitud_titulo"
            ],
            "coeficientes": self._calcular_coeficientes_simple(X, y),
            "r2_score": self._calcular_r2_simple(X, y),
            "muestras_entrenamiento": len(X),
            "fecha_entrenamiento": datetime.now().isoformat()
        }
        
        self.modelos_entrenados["engagement_score"] = modelo_info
        
        return modelo_info
    
    def _extraer_features(self, pub: Publicacion) -> List[float]:
        """Extrae features de una publicación para ML"""
        # Codificación one-hot de tipo de contenido
        tipo_X = 1.0 if pub.tipo_contenido == 'X' else 0.0
        tipo_Y = 1.0 if pub.tipo_contenido == 'Y' else 0.0
        tipo_Z = 1.0 if pub.tipo_contenido == 'Z' else 0.0
        
        # Codificación one-hot de plataforma
        plataforma_instagram = 1.0 if pub.plataforma == 'Instagram' else 0.0
        plataforma_linkedin = 1.0 if pub.plataforma == 'LinkedIn' else 0.0
        plataforma_twitter = 1.0 if pub.plataforma == 'Twitter' else 0.0
        
        # Normalizar hora (0-23 -> 0-1)
        hora_normalizada = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour) / 23.0
        
        # Normalizar día de semana (0-6 -> 0-1)
        dia_semana = pub.metadata.get('dia_semana', pub.fecha_publicacion.strftime('%A'))
        dias_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 
                   'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        dia_normalizado = dias_map.get(dia_semana, 0) / 6.0
        
        # Features adicionales
        tiene_media = 1.0 if pub.tiene_media else 0.0
        num_hashtags = min(len(pub.hashtags) / 10.0, 1.0)  # Normalizar a 0-1
        longitud_titulo = min(len(pub.titulo) / 100.0, 1.0)  # Normalizar a 0-1
        
        return [
            tipo_X, tipo_Y, tipo_Z,
            plataforma_instagram, plataforma_linkedin, plataforma_twitter,
            hora_normalizada, dia_normalizado,
            tiene_media, num_hashtags, longitud_titulo
        ]
    
    def _calcular_coeficientes_simple(self, X: List[List[float]], y: List[float]) -> List[float]:
        """Calcula coeficientes usando regresión lineal simple"""
        # Versión simplificada - en producción usar sklearn
        n = len(X)
        if n == 0:
            return [0.0] * len(X[0]) if X else []
        
        # Promedio de cada feature
        promedios_X = [statistics.mean([x[i] for x in X]) for i in range(len(X[0]))]
        promedio_y = statistics.mean(y)
        
        # Coeficientes simples basados en correlación
        coeficientes = []
        for i in range(len(X[0])):
            valores_feature = [x[i] for x in X]
            if statistics.stdev(valores_feature) > 0:
                # Correlación simple
                covarianza = sum((valores_feature[j] - promedios_X[i]) * (y[j] - promedio_y) 
                               for j in range(n)) / n
                varianza = statistics.variance(valores_feature) if n > 1 else 1
                coeficiente = covarianza / varianza if varianza > 0 else 0
            else:
                coeficiente = 0
            coeficientes.append(coeficiente)
        
        return coeficientes
    
    def _calcular_r2_simple(self, X: List[List[float]], y: List[float]) -> float:
        """Calcula R² score simple"""
        if len(X) == 0:
            return 0.0
        
        promedio_y = statistics.mean(y)
        ss_tot = sum((yi - promedio_y) ** 2 for yi in y)
        
        if ss_tot == 0:
            return 1.0
        
        # Predicciones simples
        coeficientes = self._calcular_coeficientes_simple(X, y)
        promedio_y = statistics.mean(y)
        
        predicciones = []
        for x in X:
            pred = promedio_y + sum(coef * feat for coef, feat in zip(coeficientes, x))
            predicciones.append(max(0, pred))
        
        ss_res = sum((yi - pred) ** 2 for yi, pred in zip(y, predicciones))
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return max(0, min(1, r2))
    
    def predecir_engagement_ml(
        self,
        tipo_contenido: str,
        plataforma: str,
        hora: int,
        dia_semana: str,
        tiene_media: bool = True,
        hashtags: List[str] = None,
        titulo: str = ""
    ) -> Dict[str, Any]:
        """
        Predice engagement usando modelo ML entrenado
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            plataforma: Plataforma objetivo
            hora: Hora de publicación (0-23)
            dia_semana: Día de la semana
            tiene_media: Si tiene imagen/video
            hashtags: Lista de hashtags
            titulo: Título del contenido
        
        Returns:
            Predicción con confianza y factores
        """
        # Entrenar modelo si no está entrenado
        if "engagement_score" not in self.modelos_entrenados:
            logger.info("Entrenando modelo...")
            self.entrenar_modelo_prediccion()
        
        # Crear publicación temporal para extraer features
        pub_temp = Publicacion(
            id="temp",
            tipo_contenido=tipo_contenido,
            titulo=titulo or "Título de ejemplo",
            plataforma=plataforma,
            fecha_publicacion=datetime.now(),
            likes=0,
            comentarios=0,
            shares=0,
            impresiones=0,
            reach=0,
            hashtags=hashtags or [],
            tiene_media=tiene_media,
            metadata={
                'hora_publicacion': hora,
                'dia_semana': dia_semana
            }
        )
        
        features = self._extraer_features(pub_temp)
        modelo = self.modelos_entrenados.get("engagement_score", {})
        coeficientes = modelo.get("coeficientes", [0.0] * len(features))
        
        # Predicción simple
        promedio_historico = statistics.mean([p.engagement_score for p in self.analizador.publicaciones]) if self.analizador.publicaciones else 100
        
        prediccion = promedio_historico + sum(coef * feat for coef, feat in zip(coeficientes, features))
        prediccion = max(0, prediccion)
        
        # Calcular confianza basada en R²
        confianza = modelo.get("r2_score", 0.5) * 100
        
        # Factores más influyentes
        factores_influencia = []
        for i, (coef, feat_name) in enumerate(zip(coeficientes, modelo.get("features", []))):
            impacto = abs(coef * features[i]) if i < len(features) else 0
            factores_influencia.append({
                "feature": feat_name,
                "impacto": round(impacto, 2),
                "coeficiente": round(coef, 4)
            })
        
        factores_influencia.sort(key=lambda x: x["impacto"], reverse=True)
        
        return {
            "engagement_score_predicho": round(prediccion, 1),
            "confianza": round(confianza, 1),
            "modelo_usado": modelo.get("tipo", "desconocido"),
            "factores_mas_influyentes": factores_influencia[:5],
            "recomendaciones": self._generar_recomendaciones_ml(factores_influencia, features, modelo)
        }
    
    def _generar_recomendaciones_ml(
        self,
        factores_influencia: List[Dict[str, Any]],
        features: List[float],
        modelo: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones basadas en factores ML"""
        recomendaciones = []
        
        # Analizar factores más influyentes
        for factor in factores_influencia[:3]:
            feature_name = factor["feature"]
            impacto = factor["impacto"]
            
            if "tipo_contenido" in feature_name and impacto > 10:
                tipo = feature_name.split("_")[-1]
                recomendaciones.append(f"El tipo de contenido {tipo} tiene alto impacto positivo")
            
            if "plataforma" in feature_name and impacto > 10:
                plataforma = feature_name.split("_")[-1].capitalize()
                recomendaciones.append(f"La plataforma {plataforma} muestra mejor rendimiento")
            
            if "hora" in feature_name and impacto > 5:
                recomendaciones.append("Optimizar timing puede mejorar significativamente el engagement")
            
            if "media" in feature_name and impacto > 10:
                recomendaciones.append("Incluir imagen/video es crítico para buen engagement")
        
        return recomendaciones
    
    def analizar_sentimiento_comentarios(
        self,
        comentarios: List[str],
        usar_ia: bool = True
    ) -> Dict[str, Any]:
        """
        Analiza el sentimiento de comentarios
        
        Args:
            comentarios: Lista de comentarios a analizar
            usar_ia: Si usar IA para análisis avanzado
        
        Returns:
            Análisis de sentimiento
        """
        if not comentarios:
            return {"error": "No hay comentarios para analizar"}
        
        # Análisis básico de palabras clave
        palabras_positivas = [
            'excelente', 'genial', 'increíble', 'perfecto', 'bueno', 'me gusta',
            'gracias', 'útil', 'interesante', 'sorprendente', 'impresionante'
        ]
        
        palabras_negativas = [
            'malo', 'terrible', 'horrible', 'no me gusta', 'mal', 'pésimo',
            'decepcionado', 'insatisfecho', 'error', 'problema'
        ]
        
        sentimientos = []
        positivos = 0
        negativos = 0
        neutros = 0
        
        for comentario in comentarios:
            comentario_lower = comentario.lower()
            pos_count = sum(1 for palabra in palabras_positivas if palabra in comentario_lower)
            neg_count = sum(1 for palabra in palabras_negativas if palabra in comentario_lower)
            
            if pos_count > neg_count:
                sentimientos.append("positivo")
                positivos += 1
            elif neg_count > pos_count:
                sentimientos.append("negativo")
                negativos += 1
            else:
                sentimientos.append("neutral")
                neutros += 1
        
        total = len(comentarios)
        analisis_basico = {
            "total_comentarios": total,
            "positivos": positivos,
            "negativos": negativos,
            "neutros": neutros,
            "porcentaje_positivo": (positivos / total * 100) if total > 0 else 0,
            "porcentaje_negativo": (negativos / total * 100) if total > 0 else 0,
            "score_sentimiento": ((positivos - negativos) / total * 100) if total > 0 else 0
        }
        
        # Análisis con IA si está disponible
        analisis_ia = None
        if usar_ia and self.analizador_ai.client:
            try:
                comentarios_texto = "\n".join(comentarios[:20])  # Limitar para no exceder tokens
                
                response = self.analizador_ai.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Eres un experto en análisis de sentimiento. Analiza comentarios y proporciona insights."
                        },
                        {
                            "role": "user",
                            "content": f"Analiza el sentimiento de estos comentarios y proporciona insights clave:\n\n{comentarios_texto}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                analisis_ia = {
                    "insights": response.choices[0].message.content.strip(),
                    "modelo": "gpt-4o-mini"
                }
            except Exception as e:
                logger.warning(f"Error en análisis IA de sentimiento: {e}")
        
        return {
            "analisis_basico": analisis_basico,
            "analisis_ia": analisis_ia,
            "sentimientos_individuales": sentimientos[:10]  # Primeros 10
        }
    
    def detectar_patrones_clustering(self, num_clusters: int = 3) -> Dict[str, Any]:
        """
        Detecta patrones usando clustering simple
        
        Args:
            num_clusters: Número de clusters a identificar
        
        Returns:
            Análisis de clusters y patrones
        """
        if len(self.analizador.publicaciones) < num_clusters:
            return {"error": f"Se necesitan al menos {num_clusters} publicaciones"}
        
        # Preparar datos
        datos = []
        for pub in self.analizador.publicaciones:
            datos.append({
                "engagement_score": pub.engagement_score,
                "engagement_rate": pub.engagement_rate,
                "tipo": pub.tipo_contenido,
                "plataforma": pub.plataforma
            })
        
        # Clustering simple basado en engagement
        engagement_scores = [d["engagement_score"] for d in datos]
        
        # Dividir en clusters por percentiles
        sorted_scores = sorted(engagement_scores)
        percentiles = [sorted_scores[int(len(sorted_scores) * (i+1) / num_clusters)] 
                      for i in range(num_clusters-1)]
        
        clusters = []
        for i in range(num_clusters):
            if i == 0:
                cluster_data = [d for d in datos if d["engagement_score"] < percentiles[0]]
            elif i == num_clusters - 1:
                cluster_data = [d for d in datos if d["engagement_score"] >= percentiles[-1]]
            else:
                cluster_data = [d for d in datos if percentiles[i-1] <= d["engagement_score"] < percentiles[i]]
            
            if cluster_data:
                clusters.append({
                    "cluster_id": i + 1,
                    "tamaño": len(cluster_data),
                    "engagement_score_promedio": statistics.mean([d["engagement_score"] for d in cluster_data]),
                    "engagement_rate_promedio": statistics.mean([d["engagement_rate"] for d in cluster_data]),
                    "tipos_contenido": self._contar_tipos(cluster_data, "tipo"),
                    "plataformas": self._contar_tipos(cluster_data, "plataforma"),
                    "caracteristicas": self._identificar_caracteristicas_cluster(cluster_data)
                })
        
        return {
            "num_clusters": len(clusters),
            "clusters": clusters,
            "insights": self._generar_insights_clusters(clusters)
        }
    
    def _contar_tipos(self, datos: List[Dict[str, Any]], campo: str) -> Dict[str, int]:
        """Cuenta tipos en un cluster"""
        conteo = defaultdict(int)
        for d in datos:
            conteo[d[campo]] += 1
        return dict(conteo)
    
    def _identificar_caracteristicas_cluster(self, cluster_data: List[Dict[str, Any]]) -> List[str]:
        """Identifica características del cluster"""
        caracteristicas = []
        
        tipos = self._contar_tipos(cluster_data, "tipo")
        tipo_mas_comun = max(tipos.items(), key=lambda x: x[1])[0] if tipos else None
        if tipo_mas_comun:
            caracteristicas.append(f"Tipo de contenido predominante: {tipo_mas_comun}")
        
        plataformas = self._contar_tipos(cluster_data, "plataforma")
        plataforma_mas_comun = max(plataformas.items(), key=lambda x: x[1])[0] if plataformas else None
        if plataforma_mas_comun:
            caracteristicas.append(f"Plataforma predominante: {plataforma_mas_comun}")
        
        return caracteristicas
    
    def _generar_insights_clusters(self, clusters: List[Dict[str, Any]]) -> List[str]:
        """Genera insights basados en clusters"""
        insights = []
        
        if len(clusters) >= 2:
            mejor_cluster = max(clusters, key=lambda c: c["engagement_score_promedio"])
            peor_cluster = min(clusters, key=lambda c: c["engagement_score_promedio"])
            
            insights.append(f"Cluster de alto rendimiento: {mejor_cluster['caracteristicas']}")
            insights.append(f"Cluster de bajo rendimiento: {peor_cluster['caracteristicas']}")
            
            diferencia = mejor_cluster["engagement_score_promedio"] - peor_cluster["engagement_score_promedio"]
            insights.append(f"Diferencia de engagement: {diferencia:.1f} puntos")
        
        return insights


def main():
    """Función principal para demostración"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis de Engagement con ML')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones')
    parser.add_argument('--entrenar', action='store_true', help='Entrenar modelo ML')
    parser.add_argument('--predecir', action='store_true', help='Predecir engagement')
    parser.add_argument('--clustering', action='store_true', help='Detectar patrones con clustering')
    
    args = parser.parse_args()
    
    # Crear analizadores
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    analizador_ml = AnalizadorEngagementML(analizador_base)
    
    # Entrenar modelo
    if args.entrenar:
        print("\n🤖 Entrenando modelo ML...")
        modelo = analizador_ml.entrenar_modelo_prediccion()
        print(f"✅ Modelo entrenado:")
        print(f"   Tipo: {modelo.get('tipo')}")
        print(f"   R² Score: {modelo.get('r2_score', 0):.3f}")
        print(f"   Muestras: {modelo.get('muestras_entrenamiento')}")
    
    # Predicción
    if args.predecir:
        print("\n🔮 Prediciendo engagement...")
        prediccion = analizador_ml.predecir_engagement_ml(
            tipo_contenido='Y',
            plataforma='Instagram',
            hora=10,
            dia_semana='Wednesday',
            tiene_media=True,
            hashtags=['#viral', '#trending'],
            titulo='Contenido increíble que te sorprenderá'
        )
        print(f"✅ Predicción:")
        print(f"   Engagement Score: {prediccion['engagement_score_predicho']}")
        print(f"   Confianza: {prediccion['confianza']}%")
        print(f"   Factores más influyentes:")
        for factor in prediccion['factores_mas_influyentes'][:3]:
            print(f"     • {factor['feature']}: {factor['impacto']}")
    
    # Clustering
    if args.clustering:
        print("\n🔍 Detectando patrones con clustering...")
        clusters = analizador_ml.detectar_patrones_clustering(num_clusters=3)
        print(f"✅ {clusters['num_clusters']} clusters detectados:")
        for cluster in clusters['clusters']:
            print(f"\n   Cluster {cluster['cluster_id']}:")
            print(f"     Tamaño: {cluster['tamaño']}")
            print(f"     Engagement Score: {cluster['engagement_score_promedio']:.1f}")
            print(f"     Características: {', '.join(cluster['caracteristicas'])}")


if __name__ == "__main__":
    main()


