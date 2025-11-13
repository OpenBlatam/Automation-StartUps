#!/usr/bin/env python3
"""
Análisis de Engagement de Contenido - Versión Mejorada v4.0
========================================================
Analiza publicaciones del último mes y sugiere qué tipo de contenido
obtuvo más engagement y por qué, además de recomendar nuevas ideas.

Mejoras incluidas:
- Análisis de horarios óptimos
- Análisis por día de la semana
- Análisis por plataforma
- Análisis de hashtags más efectivos
- Exportación a HTML con visualizaciones
- Exportación a CSV y PDF
- Conexión opcional a base de datos real
- Análisis de tendencias temporales
- Calendario de contenido optimizado
- Análisis de ROI potencial
- Generación de estrategia de contenido
- Alertas y recomendaciones críticas
- Exportación a Excel con múltiples hojas
- Análisis de benchmarking/competencia
- Detección de contenido mejorable
- Dashboard HTML interactivo con gráficos
- API REST para acceso programático
- Integración con script de reciclaje
- Análisis predictivo con ML
- Comparación de versiones recicladas
- Exportación mejorada con más formatos

NUEVAS FUNCIONALIDADES v4.0:
- ✅ Análisis específico optimizado para LinkedIn
- ✅ Validación de posts de LinkedIn antes de publicar
- ✅ Detección automática de hooks, CTAs y preguntas
- ✅ Análisis de estructura de posts (Hook + CTA + Pregunta)
- ✅ Recomendaciones específicas para LinkedIn basadas en mejores prácticas
- ✅ Análisis de longitud óptima para LinkedIn (1000-1500 caracteres)
- ✅ Análisis de horarios B2B específicos (8-10 AM, 12-1 PM, 5-6 PM)
- ✅ Análisis de uso estratégico de emojis
- ✅ Análisis de formato de contenido (texto, imagen, video, carousel)
- ✅ Sistema de cache para análisis repetidos
- ✅ Integración mejorada con IA para recomendaciones
- ✅ Detección de contenido duplicado
- ✅ Análisis de frecuencia óptima de publicación
"""

import json
import csv
import random
import os
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import statistics
import argparse
import math

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ML imports (opcionales)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Integración de IA
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        OPENAI_AVAILABLE = False
    print("⚠️  OpenAI no está instalado. Instala con: pip install openai")


@dataclass
class Publicacion:
    """Estructura de una publicación."""
    id: str
    tipo_contenido: str  # X, Y, Z u otros tipos
    titulo: str
    plataforma: str
    fecha_publicacion: datetime
    likes: int
    comentarios: int
    shares: int
    impresiones: int
    reach: int
    hashtags: List[str]
    tiene_media: bool
    duracion_video: int = 0  # segundos, 0 si no es video
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def engagement_total(self) -> int:
        """Calcula el engagement total."""
        return self.likes + self.comentarios + self.shares
    
    @property
    def engagement_rate(self) -> float:
        """Calcula la tasa de engagement."""
        if self.impresiones == 0:
            return 0.0
        return (self.engagement_total / self.impresiones) * 100
    
    @property
    def engagement_score(self) -> float:
        """Score ponderado de engagement."""
        # Ponderación: likes (1x), comentarios (3x), shares (5x)
        return self.likes + (self.comentarios * 3) + (self.shares * 5)
    
    @property
    def es_viral(self) -> bool:
        """Determina si una publicación es viral."""
        # Criterio: engagement rate > 10% y engagement total > 500
        return self.engagement_rate > 10.0 and self.engagement_total > 500
    
    @property
    def ratio_compartidos(self) -> float:
        """Ratio de compartidos sobre likes."""
        if self.likes == 0:
            return 0.0
        return (self.shares / self.likes) * 100


class AIIntegration:
    """Clase para integración con servicios de IA (OpenAI) - Versión mejorada."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", 
                 enable_cache: bool = True, max_retries: int = 3, timeout: int = 30):
        """
        Inicializa la integración de IA.
        
        Args:
            api_key: API key de OpenAI (si no se proporciona, se busca en env vars)
            model: Modelo de OpenAI a usar
            enable_cache: Habilitar cache para respuestas de IA
            max_retries: Número máximo de reintentos en caso de error
            timeout: Timeout en segundos para las llamadas a la API
        """
        self.enabled = OPENAI_AVAILABLE
        self.model = model
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.timeout = timeout
        self._cache: Dict[str, str] = {}  # Cache simple para respuestas
        
        if not OPENAI_AVAILABLE:
            self.client = None
            logger.warning("OpenAI no está disponible. Instala con: pip install openai")
            return
        
        # Configurar cliente de OpenAI
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if self.api_key:
            try:
                # Usar la API moderna de OpenAI
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
                self.enabled = True
                logger.info(f"Cliente de OpenAI inicializado con modelo {model}")
            except Exception as e:
                self.client = None
                self.enabled = False
                logger.error(f"Error al inicializar cliente de OpenAI: {e}")
        else:
            self.client = None
            self.enabled = False
            logger.warning("OPENAI_API_KEY no configurada. La funcionalidad de IA estará deshabilitada.")
    
    def clear_cache(self):
        """Limpia el cache de respuestas de IA."""
        self._cache.clear()
        logger.info("Cache de IA limpiado")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        return {
            "cache_size": len(self._cache),
            "cache_enabled": self.enable_cache
        }
    
    def _call_ai(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, 
                 max_tokens: int = 2000, use_cache: bool = True) -> Optional[str]:
        """
        Llama a la API de OpenAI con retry logic y cache.
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura para la generación (0-1)
            max_tokens: Máximo de tokens a generar
            use_cache: Usar cache si está disponible
            
        Returns:
            Respuesta de la IA o None si hay error
        """
        if not self.enabled or not self.client:
            return None
        
        # Verificar cache
        cache_key = f"{prompt}_{system_prompt}_{temperature}_{max_tokens}"
        if use_cache and self.enable_cache and cache_key in self._cache:
            logger.debug("Respuesta obtenida del cache")
            return self._cache[cache_key]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Retry logic con exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content.strip()
                
                # Guardar en cache
                if use_cache and self.enable_cache:
                    # Limitar tamaño del cache (mantener solo las últimas 100 respuestas)
                    if len(self._cache) > 100:
                        # Eliminar la entrada más antigua (simple LRU)
                        oldest_key = next(iter(self._cache))
                        del self._cache[oldest_key]
                    self._cache[cache_key] = content
                
                logger.debug(f"Respuesta de IA obtenida exitosamente (intento {attempt + 1})")
                return content
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Error al llamar a la IA (intento {attempt + 1}/{self.max_retries}): {e}. Reintentando en {wait_time}s...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error al llamar a la IA después de {self.max_retries} intentos: {e}")
                    return None
        
        return None
    
    def generar_recomendaciones_contenido(self, reporte: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera recomendaciones inteligentes de contenido usando IA.
        
        Args:
            reporte: Reporte de análisis de engagement
            
        Returns:
            Diccionario con recomendaciones generadas por IA
        """
        if not self.enabled:
            return {"error": "IA no disponible"}
        
        sistema_prompt = """Eres un experto en marketing de contenidos y análisis de engagement en redes sociales. 
Analiza los datos proporcionados y genera recomendaciones específicas, accionables y basadas en datos."""
        
        prompt = f"""Analiza el siguiente reporte de engagement de contenido y genera recomendaciones específicas:

RESUMEN EJECUTIVO:
- Tipo de contenido con mayor engagement: {reporte.get('resumen_ejecutivo', {}).get('nombre_tipo', 'N/A')}
- Engagement Rate Promedio: {reporte.get('resumen_ejecutivo', {}).get('engagement_rate_promedio', 0):.2f}%
- Engagement Score Promedio: {reporte.get('resumen_ejecutivo', {}).get('engagement_score_promedio', 0):.1f}
- Mejor Horario: {reporte.get('resumen_ejecutivo', {}).get('mejor_horario', 'N/A')}
- Mejor Día: {reporte.get('resumen_ejecutivo', {}).get('mejor_dia', 'N/A')}
- Mejor Plataforma: {reporte.get('resumen_ejecutivo', {}).get('mejor_plataforma', 'N/A')}

ANÁLISIS POR TIPO DE CONTENIDO:
{json.dumps(reporte.get('analisis_por_tipo', {}), indent=2, ensure_ascii=False, default=str)}

Genera recomendaciones específicas en formato JSON con la siguiente estructura:
{{
    "recomendaciones_estrategicas": [
        "Recomendación 1 específica y accionable",
        "Recomendación 2 específica y accionable",
        ...
    ],
    "ideas_contenido": [
        {{
            "tipo": "Tipo de contenido recomendado",
            "titulo": "Idea de título",
            "descripcion": "Descripción de la idea",
            "plataforma": "Plataforma recomendada",
            "horario": "Horario recomendado",
            "hashtags_sugeridos": ["#hashtag1", "#hashtag2"]
        }},
        ...
    ],
    "mejoras_prioritarias": [
        "Mejora prioritaria 1",
        "Mejora prioritaria 2",
        ...
    ],
    "insights_clave": [
        "Insight clave 1",
        "Insight clave 2",
        ...
    ]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.7, max_tokens=2000)
        
        if respuesta:
            try:
                # Intentar parsear JSON
                recomendaciones = json.loads(respuesta)
                return recomendaciones
            except json.JSONDecodeError:
                # Si no es JSON válido, devolver como texto
                return {
                    "recomendaciones_texto": respuesta,
                    "recomendaciones_estrategicas": [respuesta]
                }
        
        return {"error": "No se pudo generar recomendaciones"}
    
    def analizar_sentimiento_contenido(self, publicaciones: List[Publicacion]) -> Dict[str, Any]:
        """
        Analiza el sentimiento y calidad del contenido usando IA.
        
        Args:
            publicaciones: Lista de publicaciones a analizar
            
        Returns:
            Diccionario con análisis de sentimiento
        """
        if not self.enabled or not publicaciones:
            return {"error": "IA no disponible o sin publicaciones"}
        
        # Seleccionar las top 10 publicaciones por engagement
        top_publicaciones = sorted(publicaciones, key=lambda p: p.engagement_score, reverse=True)[:10]
        
        sistema_prompt = """Eres un experto en análisis de contenido y sentimiento en redes sociales. 
Analiza el contenido y proporciona insights sobre sentimiento, calidad y efectividad."""
        
        contenido_analizar = "\n".join([
            f"- {p.titulo} ({p.plataforma}): Engagement Score {p.engagement_score:.1f}, "
            f"Rate {p.engagement_rate:.2f}%, Hashtags: {', '.join(p.hashtags[:5])}"
            for p in top_publicaciones
        ])
        
        prompt = f"""Analiza el sentimiento y calidad de estas publicaciones con mejor engagement:

{contenido_analizar}

Genera un análisis en formato JSON con:
{{
    "sentimiento_general": "positivo/neutral/negativo",
    "temas_recurrentes": ["tema1", "tema2", ...],
    "tono_contenido": "Descripción del tono general",
    "calidad_contenido": "Descripción de la calidad",
    "elementos_exitosos": ["elemento1", "elemento2", ...],
    "patrones_virales": ["patrón1", "patrón2", ...],
    "sugerencias_mejora": ["sugerencia1", "sugerencia2", ...]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.5, max_tokens=1500)
        
        if respuesta:
            try:
                return json.loads(respuesta)
            except json.JSONDecodeError:
                return {
                    "analisis_texto": respuesta,
                    "sentimiento_general": "neutral"
                }
        
        return {"error": "No se pudo analizar el contenido"}
    
    def generar_sugerencias_mejora(self, publicacion: Publicacion, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera sugerencias específicas de mejora para una publicación usando IA.
        
        Args:
            publicacion: Publicación a analizar
            contexto: Contexto adicional (opcional)
            
        Returns:
            Diccionario con sugerencias de mejora
        """
        if not self.enabled:
            return {"error": "IA no disponible"}
        
        sistema_prompt = """Eres un experto en optimización de contenido para redes sociales. 
Proporciona sugerencias específicas y accionables para mejorar el engagement."""
        
        contexto_str = ""
        if contexto:
            contexto_str = f"\nContexto adicional:\n{json.dumps(contexto, indent=2, ensure_ascii=False, default=str)}"
        
        prompt = f"""Analiza esta publicación y genera sugerencias específicas de mejora:

PUBLICACIÓN:
- Título: {publicacion.titulo}
- Plataforma: {publicacion.plataforma}
- Tipo: {publicacion.tipo_contenido}
- Engagement Score: {publicacion.engagement_score:.1f}
- Engagement Rate: {publicacion.engagement_rate:.2f}%
- Likes: {publicacion.likes}
- Comentarios: {publicacion.comentarios}
- Shares: {publicacion.shares}
- Hashtags: {', '.join(publicacion.hashtags)}
- Tiene Media: {publicacion.tiene_media}
- Fecha: {publicacion.fecha_publicacion.strftime('%Y-%m-%d %H:%M')}
{contexto_str}

Genera sugerencias en formato JSON:
{{
    "titulo_mejorado": "Sugerencia de título mejorado",
    "hashtags_sugeridos": ["#hashtag1", "#hashtag2", ...],
    "mejoras_contenido": [
        "Mejora específica 1",
        "Mejora específica 2",
        ...
    ],
    "optimizacion_plataforma": "Sugerencias específicas para {publicacion.plataforma}",
    "horario_recomendado": "Horario recomendado",
    "mejoras_media": "Sugerencias para mejorar el contenido multimedia",
    "razones_bajo_engagement": ["Razón 1", "Razón 2", ...]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.7, max_tokens=1500)
        
        if respuesta:
            try:
                return json.loads(respuesta)
            except json.JSONDecodeError:
                return {
                    "sugerencias_texto": respuesta,
                    "mejoras_contenido": [respuesta]
                }
        
        return {"error": "No se pudieron generar sugerencias"}
    
    def generar_descripcion_insights(self, datos: Dict[str, Any]) -> str:
        """
        Genera una descripción narrativa de los insights usando IA.
        
        Args:
            datos: Datos del análisis
            
        Returns:
            Descripción narrativa generada por IA
        """
        if not self.enabled:
            return "IA no disponible para generar descripción."
        
        sistema_prompt = """Eres un experto en análisis de datos de marketing de contenidos. 
Escribe descripciones claras, profesionales y accionables basadas en datos."""
        
        prompt = f"""Genera una descripción narrativa profesional (2-3 párrafos) de estos insights de engagement:

{json.dumps(datos, indent=2, ensure_ascii=False, default=str)}

La descripción debe ser:
- Clara y profesional
- Basada en datos concretos
- Accionable
- En español

Escribe solo la descripción, sin formato adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.6, max_tokens=500)
        return respuesta or "No se pudo generar la descripción."
    
    def generar_titulos_optimizados(self, tipo_contenido: str, tema: str, plataforma: str, contexto: Dict[str, Any] = None) -> List[str]:
        """
        Genera títulos optimizados para contenido usando IA.
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            tema: Tema del contenido
            plataforma: Plataforma objetivo
            contexto: Contexto adicional (opcional)
            
        Returns:
            Lista de títulos sugeridos
        """
        if not self.enabled:
            return []
        
        sistema_prompt = """Eres un experto en creación de títulos virales y optimizados para redes sociales. 
Genera títulos que maximicen el engagement y clicks."""
        
        contexto_str = ""
        if contexto:
            contexto_str = f"\nContexto: {json.dumps(contexto, indent=2, ensure_ascii=False, default=str)}"
        
        prompt = f"""Genera 5 títulos optimizados para:
- Tipo de contenido: {tipo_contenido}
- Tema: {tema}
- Plataforma: {plataforma}
{contexto_str}

Los títulos deben ser:
- Atractivos y llamativos
- Optimizados para la plataforma {plataforma}
- Que generen curiosidad o valor
- Entre 40-80 caracteres aproximadamente

Responde SOLO con un JSON array de strings:
["Título 1", "Título 2", "Título 3", "Título 4", "Título 5"]"""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.8, max_tokens=500)
        
        if respuesta:
            try:
                titulos = json.loads(respuesta)
                if isinstance(titulos, list):
                    return titulos[:5]
            except json.JSONDecodeError:
                # Intentar extraer títulos del texto
                lines = [l.strip() for l in respuesta.split('\n') if l.strip() and not l.strip().startswith('#')]
                return lines[:5]
        
        return []
    
    def generar_hashtags_inteligentes(self, titulo: str, plataforma: str, contexto: Dict[str, Any] = None) -> List[str]:
        """
        Genera hashtags inteligentes usando IA basados en el título y contexto.
        
        Args:
            titulo: Título del contenido
            plataforma: Plataforma objetivo
            contexto: Contexto adicional (opcional)
            
        Returns:
            Lista de hashtags sugeridos
        """
        if not self.enabled:
            return []
        
        sistema_prompt = """Eres un experto en hashtags para redes sociales. 
Genera hashtags relevantes, populares y optimizados para cada plataforma."""
        
        contexto_str = ""
        if contexto:
            contexto_str = f"\nContexto: {json.dumps(contexto, indent=2, ensure_ascii=False, default=str)}"
        
        prompt = f"""Genera 10 hashtags optimizados para:
- Título: {titulo}
- Plataforma: {plataforma}
{contexto_str}

Los hashtags deben ser:
- Relevantes al contenido
- Populares en {plataforma}
- Mezcla de específicos y generales
- Sin espacios ni caracteres especiales

Responde SOLO con un JSON array de strings (sin el símbolo #):
["hashtag1", "hashtag2", "hashtag3", ...]"""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.7, max_tokens=300)
        
        if respuesta:
            try:
                hashtags = json.loads(respuesta)
                if isinstance(hashtags, list):
                    return [h.replace('#', '') for h in hashtags[:10]]
            except json.JSONDecodeError:
                # Intentar extraer hashtags del texto
                hashtags = re.findall(r'#?(\w+)', respuesta)
                return hashtags[:10]
        
        return []
    
    def analizar_competencia_contenido(self, publicaciones_propias: List[Publicacion], publicaciones_competencia: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analiza contenido de competencia y compara con el propio usando IA.
        
        Args:
            publicaciones_propias: Lista de publicaciones propias
            publicaciones_competencia: Lista de publicaciones de competencia (opcional)
            
        Returns:
            Diccionario con análisis comparativo
        """
        if not self.enabled:
            return {"error": "IA no disponible"}
        
        sistema_prompt = """Eres un experto en análisis competitivo de contenido en redes sociales. 
Analiza y compara estrategias de contenido para identificar oportunidades."""
        
        # Analizar publicaciones propias
        top_propias = sorted(publicaciones_propias, key=lambda p: p.engagement_score, reverse=True)[:5]
        analisis_propias = "\n".join([
            f"- {p.titulo} ({p.plataforma}): Score {p.engagement_score:.1f}, Rate {p.engagement_rate:.2f}%"
            for p in top_propias
        ])
        
        prompt = f"""Analiza estas publicaciones propias con mejor rendimiento:

{analisis_propias}

Genera un análisis en formato JSON con:
{{
    "fortalezas": ["fortaleza1", "fortaleza2", ...],
    "debilidades": ["debilidad1", "debilidad2", ...],
    "oportunidades": ["oportunidad1", "oportunidad2", ...],
    "amenazas": ["amenaza1", "amenaza2", ...],
    "recomendaciones_competitivas": ["recomendación1", "recomendación2", ...],
    "nichos_no_explorados": ["nicho1", "nicho2", ...]
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.6, max_tokens=1500)
        
        if respuesta:
            try:
                return json.loads(respuesta)
            except json.JSONDecodeError:
                return {
                    "analisis_texto": respuesta,
                    "fortalezas": [],
                    "debilidades": []
                }
        
        return {"error": "No se pudo analizar"}
    
    def generar_estrategia_contenido(self, reporte: Dict[str, Any], objetivo: str = "aumentar engagement") -> Dict[str, Any]:
        """
        Genera una estrategia completa de contenido usando IA.
        
        Args:
            reporte: Reporte de análisis completo
            objetivo: Objetivo de la estrategia
            
        Returns:
            Diccionario con estrategia generada
        """
        if not self.enabled:
            return {"error": "IA no disponible"}
        
        sistema_prompt = """Eres un estratega experto en marketing de contenidos. 
Crea estrategias completas, accionables y basadas en datos."""
        
        resumen = reporte.get('resumen_ejecutivo', {})
        benchmarking = reporte.get('benchmarking', {})
        
        prompt = f"""Crea una estrategia completa de contenido para: {objetivo}

DATOS ACTUALES:
- Tipo ganador: {resumen.get('nombre_tipo', 'N/A')}
- Engagement Rate: {resumen.get('engagement_rate_promedio', 0):.2f}%
- Mejor Plataforma: {resumen.get('mejor_plataforma', 'N/A')}
- Mejor Horario: {resumen.get('mejor_horario', 'N/A')}
- Benchmark Score: {benchmarking.get('score_general', 0):.1f}% del excelente

Genera una estrategia en formato JSON:
{{
    "objetivo": "{objetivo}",
    "metas_cuantitativas": {{
        "engagement_rate_objetivo": 0.0,
        "engagement_score_objetivo": 0,
        "contenido_viral_objetivo": 0.0
    }},
    "estrategia_por_plataforma": {{
        "plataforma1": {{
            "frecuencia": "X veces por semana",
            "tipos_contenido": ["tipo1", "tipo2"],
            "horarios_optimos": ["horario1", "horario2"],
            "hashtags_estrategicos": ["#hashtag1", "#hashtag2"]
        }}
    }},
    "calendario_sugerido": {{
        "lunes": ["tipo_contenido1", "tipo_contenido2"],
        "martes": [...],
        ...
    }},
    "temas_contenido": ["tema1", "tema2", ...],
    "acciones_inmediatas": ["acción1", "acción2", ...],
    "metricas_seguimiento": ["métrica1", "métrica2", ...],
    "cronograma_implementacion": {{
        "semana_1": ["tarea1", "tarea2"],
        "semana_2": [...],
        ...
    }}
}}

Responde SOLO con el JSON, sin texto adicional."""
        
        respuesta = self._call_ai(prompt, system_prompt, temperature=0.7, max_tokens=2500)
        
        if respuesta:
            try:
                return json.loads(respuesta)
            except json.JSONDecodeError:
                return {
                    "estrategia_texto": respuesta,
                    "objetivo": objetivo
                }
        
        return {"error": "No se pudo generar la estrategia"}


class AnalizadorEngagement:
    """Analizador de engagement de contenido."""
    
    def __init__(self, db_connection=None, enable_tiktok_hashtags: bool = True, enable_cache: bool = True):
        """
        Inicializa el analizador.
        
        Args:
            db_connection: Conexión opcional a base de datos PostgreSQL
            enable_tiktok_hashtags: Habilitar integración con generador de hashtags TikTok
            enable_cache: Habilitar cache para análisis repetidos
        """
        self.publicaciones: List[Publicacion] = []
        self.db = db_connection
        self.enable_tiktok_hashtags = enable_tiktok_hashtags
        self.enable_cache = enable_cache
        self._cache: Dict[str, Any] = {}
        self.hashtag_generator_path = os.path.join(
            os.path.dirname(__file__), 
            'tiktok_hashtag_generator.py'
        )
        # Inicializar integración de IA si está disponible
        try:
            self.ai = AIIntegration(enable_cache=enable_cache)
            if self.ai.enabled:
                logger.info("Integración de IA habilitada")
            else:
                logger.warning("Integración de IA solicitada pero no disponible")
        except Exception as e:
            logger.error(f"Error al inicializar IA: {e}")
            self.ai = None
        
        # Cache para análisis con TTL
        self._cache_analisis: Dict[str, Any] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
    
    def clear_cache(self):
        """Limpia el cache de análisis."""
        self._cache.clear()
        self._cache_analisis.clear()
        self._cache_timestamp.clear()
        if self.ai:
            self.ai.clear_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        stats = {
            "cache_size": len(self._cache),
            "analisis_cache_size": len(self._cache_analisis),
            "ai_cache_size": self.ai.get_cache_stats()["cache_size"] if self.ai else 0
        }
        return stats
    
    def _get_cached_or_compute(self, cache_key: str, compute_func, ttl_seconds: int = 3600):
        """
        Obtiene un valor del cache o lo calcula si no existe o expiró.
        
        Args:
            cache_key: Clave única para el cache
            compute_func: Función que calcula el valor si no está en cache
            ttl_seconds: Tiempo de vida del cache en segundos (default: 1 hora)
            
        Returns:
            Valor del cache o resultado de compute_func
        """
        if not self.enable_cache:
            return compute_func()
        
        now = datetime.now()
        
        # Verificar si existe y no ha expirado
        if cache_key in self._cache_analisis:
            timestamp = self._cache_timestamp.get(cache_key)
            if timestamp and (now - timestamp).total_seconds() < ttl_seconds:
                return self._cache_analisis[cache_key]
        
        # Calcular y guardar en cache
        result = compute_func()
        self._cache_analisis[cache_key] = result
        self._cache_timestamp[cache_key] = now
        
        return result
    
    def validar_datos(self) -> Dict[str, Any]:
        """
        Valida la calidad de los datos de todas las publicaciones.
        
        Returns:
            Diccionario con resultados de validación
        """
        problemas = []
        warnings = []
        total_publicaciones = len(self.publicaciones)
        
        if total_publicaciones == 0:
            return {
                "valido": False,
                "problemas": ["No hay publicaciones para validar"],
                "warnings": [],
                "score_calidad": 0
            }
        
        # Validar cada publicación
        publicaciones_invalidas = 0
        publicaciones_sin_impresiones = 0
        publicaciones_sin_hashtags = 0
        publicaciones_con_reach_inconsistente = 0
        
        for pub in self.publicaciones:
            calidad = pub.calidad_datos
            
            if not calidad["es_valida"]:
                publicaciones_invalidas += 1
                problemas.extend(calidad["problemas"])
            
            warnings.extend(calidad["warnings"])
            
            if pub.impresiones == 0:
                publicaciones_sin_impresiones += 1
            
            if len(pub.hashtags) == 0:
                publicaciones_sin_hashtags += 1
            
            if pub.reach > pub.impresiones * 1.1 and pub.impresiones > 0:
                publicaciones_con_reach_inconsistente += 1
        
        # Resumen de problemas
        if publicaciones_invalidas > 0:
            problemas.append(f"{publicaciones_invalidas} publicación(es) con datos inválidos")
        
        if publicaciones_sin_impresiones > total_publicaciones * 0.1:
            warnings.append(f"{publicaciones_sin_impresiones} publicación(es) sin impresiones ({publicaciones_sin_impresiones/total_publicaciones*100:.1f}%)")
        
        if publicaciones_sin_hashtags > total_publicaciones * 0.2:
            warnings.append(f"{publicaciones_sin_hashtags} publicación(es) sin hashtags ({publicaciones_sin_hashtags/total_publicaciones*100:.1f}%)")
        
        if publicaciones_con_reach_inconsistente > 0:
            warnings.append(f"{publicaciones_con_reach_inconsistente} publicación(es) con reach inconsistente")
        
        # Calcular score de calidad
        score_base = 100
        score_base -= len(problemas) * 20
        score_base -= len(warnings) * 5
        score_calidad = max(0, score_base)
        
        return {
            "valido": len(problemas) == 0,
            "problemas": list(set(problemas)),  # Eliminar duplicados
            "warnings": list(set(warnings)),  # Eliminar duplicados
            "score_calidad": score_calidad,
            "total_publicaciones": total_publicaciones,
            "publicaciones_invalidas": publicaciones_invalidas,
            "publicaciones_sin_impresiones": publicaciones_sin_impresiones,
            "publicaciones_sin_hashtags": publicaciones_sin_hashtags
        }
    
    def generar_datos_ejemplo(self, num_publicaciones: int = 30):
        """
        Genera datos de ejemplo simulando publicaciones del último mes.
        Tipos de contenido:
        - X: Tutoriales/Educativos (alto engagement esperado)
        - Y: Entretenimiento/Viral (engagement medio-alto)
        - Z: Promocional/Producto (engagement bajo-medio)
        """
        tipos_contenido = {
            'X': {
                'nombre': 'Tutoriales/Educativos',
                'prob_alto_engagement': 0.7,
                'hashtags_tipicos': ['#tutorial', '#aprende', '#educacion', '#tips'],
                'tiene_media_prob': 0.9,
                'duracion_promedio': 180
            },
            'Y': {
                'nombre': 'Entretenimiento/Viral',
                'prob_alto_engagement': 0.5,
                'hashtags_tipicos': ['#viral', '#entretenimiento', '#diversion', '#trending'],
                'tiene_media_prob': 0.95,
                'duracion_promedio': 60
            },
            'Z': {
                'nombre': 'Promocional/Producto',
                'prob_alto_engagement': 0.3,
                'hashtags_tipicos': ['#producto', '#oferta', '#nuevo', '#promocion'],
                'tiene_media_prob': 0.8,
                'duracion_promedio': 30
            }
        }
        
        plataformas = ['Instagram', 'LinkedIn', 'Twitter', 'Facebook', 'TikTok']
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        for i in range(num_publicaciones):
            # Distribución: 40% X, 35% Y, 25% Z
            tipo_key = random.choices(
                ['X', 'Y', 'Z'],
                weights=[40, 35, 25]
            )[0]
            
            tipo_info = tipos_contenido[tipo_key]
            
            # Generar fecha aleatoria en el último mes
            dias_aleatorios = random.randint(0, 30)
            fecha = fecha_inicio + timedelta(days=dias_aleatorios)
            
            # Generar métricas según el tipo de contenido
            base_impresiones = random.randint(500, 5000)
            base_reach = int(base_impresiones * random.uniform(0.6, 0.9))
            
            # Engagement varía según tipo
            if tipo_key == 'X':  # Tutoriales tienen mejor engagement
                factor_engagement = random.uniform(0.08, 0.15)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.7, 1.3))
                comentarios_base = int(likes_base * random.uniform(0.15, 0.25))
                shares_base = int(likes_base * random.uniform(0.10, 0.20))
            elif tipo_key == 'Y':  # Entretenimiento tiene engagement medio-alto
                factor_engagement = random.uniform(0.05, 0.12)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.6, 1.2))
                comentarios_base = int(likes_base * random.uniform(0.10, 0.18))
                shares_base = int(likes_base * random.uniform(0.08, 0.15))
            else:  # Z: Promocional tiene engagement más bajo
                factor_engagement = random.uniform(0.02, 0.08)
                likes_base = int(base_impresiones * factor_engagement * random.uniform(0.5, 1.0))
                comentarios_base = int(likes_base * random.uniform(0.05, 0.12))
                shares_base = int(likes_base * random.uniform(0.03, 0.10))
            
            # Añadir variabilidad
            likes = max(0, int(likes_base + random.randint(-50, 50)))
            comentarios = max(0, int(comentarios_base + random.randint(-10, 10)))
            shares = max(0, int(shares_base + random.randint(-5, 5)))
            
            # Generar hashtags
            num_hashtags = random.randint(3, 7)
            hashtags = random.sample(tipo_info['hashtags_tipicos'], 
                                    min(num_hashtags, len(tipo_info['hashtags_tipicos'])))
            
            # Generar título según tipo
            titulos = {
                'X': [
                    f"Cómo hacer {random.choice(['X', 'Y', 'Z'])} en 5 pasos",
                    f"Tutorial completo: {random.choice(['Guía', 'Método', 'Técnica'])}",
                    f"5 tips para mejorar tu {random.choice(['productividad', 'habilidad', 'resultado'])}",
                    f"Aprende {random.choice(['esto', 'aquello'])} en minutos"
                ],
                'Y': [
                    f"Esto te va a {random.choice(['sorprender', 'encantar', 'divertir'])}",
                    f"Viral: {random.choice(['Momento', 'Situación', 'Historia'])} increíble",
                    f"No vas a creer lo que pasó",
                    f"Trending: {random.choice(['Lo último', 'Lo nuevo', 'Lo mejor'])}"
                ],
                'Z': [
                    f"Nuevo producto disponible",
                    f"Oferta especial: {random.randint(10, 50)}% descuento",
                    f"Descubre nuestra {random.choice(['novedad', 'oferta', 'promoción'])}",
                    f"Lanzamiento: {random.choice(['Producto', 'Servicio', 'Solución'])}"
                ]
            }
            
            publicacion = Publicacion(
                id=f"post_{i+1:03d}",
                tipo_contenido=tipo_key,
                titulo=random.choice(titulos[tipo_key]),
                plataforma=random.choice(plataformas),
                fecha_publicacion=fecha,
                likes=likes,
                comentarios=comentarios,
                shares=shares,
                impresiones=base_impresiones,
                reach=base_reach,
                hashtags=hashtags,
                tiene_media=random.random() < tipo_info['tiene_media_prob'],
                duracion_video=random.randint(15, tipo_info['duracion_promedio']) if tipo_info['tiene_media_prob'] > 0.5 else 0,
                metadata={
                    'tipo_nombre': tipo_info['nombre'],
                    'hora_publicacion': fecha.hour,
                    'dia_semana': fecha.strftime('%A')
                }
            )
            
            self.publicaciones.append(publicacion)
    
    def cargar_desde_bd(self, dias_atras: int = 30):
        """
        Carga publicaciones desde la base de datos real.
        
        Args:
            dias_atras: Número de días hacia atrás para analizar
        """
        if not self.db:
            raise ValueError("No hay conexión a base de datos configurada")
        
        cursor = self.db.cursor()
        fecha_limite = datetime.now() - timedelta(days=dias_atras)
        
        # Consulta para obtener publicaciones con engagement
        cursor.execute("""
            SELECT 
                sp.post_id,
                sp.platform,
                sp.content,
                sp.hashtags,
                sp.published_at,
                sp.metadata,
                ce.likes,
                ce.comments,
                ce.shares,
                ce.retweets,
                ce.impressions,
                ce.reach,
                ce.engagement_rate,
                cv.version_type as tipo_contenido,
                ca.category
            FROM content_scheduled_posts sp
            LEFT JOIN content_engagement ce ON sp.post_id = ce.post_id
            LEFT JOIN content_versions cv ON sp.version_id = cv.id
            LEFT JOIN content_articles ca ON sp.article_id = ca.article_id
            WHERE sp.status = 'published'
            AND sp.published_at >= %s
            ORDER BY sp.published_at DESC
        """, (fecha_limite,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        for row in rows:
            data = dict(zip(columns, row))
            
            # Determinar tipo de contenido
            tipo = data.get('tipo_contenido', 'Z')
            if tipo in ['twitter', 'linkedin', 'newsletter']:
                tipo = 'X' if 'tutorial' in (data.get('content', '') + ' ' + data.get('category', '')).lower() else 'Y'
            else:
                tipo = 'Z'
            
            # Parsear hashtags
            hashtags = data.get('hashtags', [])
            if isinstance(hashtags, str):
                hashtags = [h.strip() for h in hashtags.split(',') if h.strip()]
            
            publicacion = Publicacion(
                id=data['post_id'],
                tipo_contenido=tipo,
                titulo=data.get('content', '')[:100] or f"Post {data['post_id']}",
                plataforma=data.get('platform', 'Unknown'),
                fecha_publicacion=data.get('published_at', datetime.now()),
                likes=data.get('likes', 0) or 0,
                comentarios=data.get('comments', 0) or 0,
                shares=(data.get('shares', 0) or 0) + (data.get('retweets', 0) or 0),
                impresiones=data.get('impressions', 0) or 0,
                reach=data.get('reach', 0) or 0,
                hashtags=hashtags,
                tiene_media=bool(data.get('metadata', {}).get('has_media', False)),
                metadata=data.get('metadata', {}) or {}
            )
            
            self.publicaciones.append(publicacion)
        
        cursor.close()
    
    def analizar_horarios_optimos(self) -> Dict[str, Any]:
        """Analiza los horarios con mejor engagement."""
        analisis_horarios = defaultdict(lambda: {
            'publicaciones': [],
            'engagement_scores': [],
            'engagement_rates': []
        })
        
        for pub in self.publicaciones:
            hora = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
            # Agrupar por rangos horarios
            if 6 <= hora < 9:
                rango = '06:00-09:00 (Mañana Temprano)'
            elif 9 <= hora < 12:
                rango = '09:00-12:00 (Mañana)'
            elif 12 <= hora < 15:
                rango = '12:00-15:00 (Mediodía)'
            elif 15 <= hora < 18:
                rango = '15:00-18:00 (Tarde)'
            elif 18 <= hora < 21:
                rango = '18:00-21:00 (Noche)'
            else:
                rango = '21:00-06:00 (Noche Tardía)'
            
            analisis_horarios[rango]['publicaciones'].append(pub)
            analisis_horarios[rango]['engagement_scores'].append(pub.engagement_score)
            analisis_horarios[rango]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = {}
        for rango, datos in analisis_horarios.items():
            if len(datos['publicaciones']) > 0:
                resultado[rango] = {
                    'cantidad': len(datos['publicaciones']),
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates'])
                }
        
        return resultado
    
    def analizar_dias_semana(self) -> Dict[str, Any]:
        """Analiza el engagement por día de la semana."""
        analisis_dias = defaultdict(lambda: {
            'publicaciones': [],
            'engagement_scores': [],
            'engagement_rates': []
        })
        
        dias_es = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        for pub in self.publicaciones:
            dia_semana = pub.metadata.get('dia_semana', pub.fecha_publicacion.strftime('%A'))
            dia_es = dias_es.get(dia_semana, dia_semana)
            
            analisis_dias[dia_es]['publicaciones'].append(pub)
            analisis_dias[dia_es]['engagement_scores'].append(pub.engagement_score)
            analisis_dias[dia_es]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = {}
        for dia, datos in analisis_dias.items():
            if len(datos['publicaciones']) > 0:
                resultado[dia] = {
                    'cantidad': len(datos['publicaciones']),
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates'])
                }
        
        return resultado
    
    def analizar_hashtags_efectivos(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Analiza los hashtags más efectivos."""
        hashtag_stats = defaultdict(lambda: {
            'publicaciones': [],
            'engagement_scores': [],
            'engagement_rates': []
        })
        
        for pub in self.publicaciones:
            for hashtag in pub.hashtags:
                hashtag_lower = hashtag.lower().strip()
                hashtag_stats[hashtag_lower]['publicaciones'].append(pub)
                hashtag_stats[hashtag_lower]['engagement_scores'].append(pub.engagement_score)
                hashtag_stats[hashtag_lower]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = []
        for hashtag, datos in hashtag_stats.items():
            if len(datos['publicaciones']) >= 2:  # Solo hashtags usados al menos 2 veces
                resultado.append({
                    'hashtag': hashtag,
                    'veces_usado': len(datos['publicaciones']),
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates'])
                })
        
        # Ordenar por engagement score promedio
        resultado.sort(key=lambda x: x['engagement_score_promedio'], reverse=True)
        return resultado[:top_n]
    
    def analizar_por_plataforma(self) -> Dict[str, Any]:
        """Analiza el engagement por plataforma."""
        analisis_plataformas = defaultdict(lambda: {
            'publicaciones': [],
            'total_likes': 0,
            'total_comentarios': 0,
            'total_shares': 0,
            'total_impresiones': 0,
            'engagement_scores': [],
            'engagement_rates': []
        })
        
        for pub in self.publicaciones:
            plataforma = pub.plataforma
            analisis_plataformas[plataforma]['publicaciones'].append(pub)
            analisis_plataformas[plataforma]['total_likes'] += pub.likes
            analisis_plataformas[plataforma]['total_comentarios'] += pub.comentarios
            analisis_plataformas[plataforma]['total_shares'] += pub.shares
            analisis_plataformas[plataforma]['total_impresiones'] += pub.impresiones
            analisis_plataformas[plataforma]['engagement_scores'].append(pub.engagement_score)
            analisis_plataformas[plataforma]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = {}
        for plataforma, datos in analisis_plataformas.items():
            num_pubs = len(datos['publicaciones'])
            if num_pubs > 0:
                resultado[plataforma] = {
                    'cantidad_publicaciones': num_pubs,
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates']),
                    'likes_promedio': datos['total_likes'] / num_pubs,
                    'comentarios_promedio': datos['total_comentarios'] / num_pubs,
                    'shares_promedio': datos['total_shares'] / num_pubs,
                    'impresiones_promedio': datos['total_impresiones'] / num_pubs
                }
        
        return resultado
    
    def analizar_tendencias_temporales(self) -> Dict[str, Any]:
        """Analiza las tendencias de engagement a lo largo del tiempo."""
        # Agrupar por semana
        publicaciones_por_semana = defaultdict(list)
        
        for pub in self.publicaciones:
            # Calcular número de semana
            fecha = pub.fecha_publicacion
            semana = fecha.isocalendar()[1]  # Número de semana
            año_semana = f"{fecha.year}-W{semana:02d}"
            
            publicaciones_por_semana[año_semana].append(pub)
        
        tendencias = {}
        semanas_ordenadas = sorted(publicaciones_por_semana.keys())
        
        for semana in semanas_ordenadas:
            pubs = publicaciones_por_semana[semana]
            if len(pubs) > 0:
                tendencias[semana] = {
                    'cantidad': len(pubs),
                    'engagement_promedio': statistics.mean([p.engagement_total for p in pubs]),
                    'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]),
                    'engagement_score_promedio': statistics.mean([p.engagement_score for p in pubs]),
                    'publicaciones_virales': sum(1 for p in pubs if p.es_viral)
                }
        
        # Calcular tendencia (creciente/decreciente)
        if len(tendencias) >= 2:
            valores = [tendencias[s]['engagement_score_promedio'] for s in semanas_ordenadas]
            tendencia_direccion = 'creciente' if valores[-1] > valores[0] else 'decreciente'
            tendencia_porcentaje = ((valores[-1] - valores[0]) / valores[0] * 100) if valores[0] > 0 else 0
        else:
            tendencia_direccion = 'estable'
            tendencia_porcentaje = 0
        
        return {
            'tendencias_semanales': tendencias,
            'direccion': tendencia_direccion,
            'cambio_porcentual': tendencia_porcentaje,
            'semanas_analizadas': len(tendencias)
        }
    
    def analizar_palabras_clave_titulos(self, top_n: int = 15) -> List[Dict[str, Any]]:
        """Analiza las palabras clave más efectivas en los títulos."""
        palabras_stats = defaultdict(lambda: {
            'publicaciones': [],
            'engagement_scores': [],
            'engagement_rates': []
        })
        
        # Palabras comunes a excluir
        stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'y', 'o', 'a', 'que', 'es', 'se', 'por', 'con', 'para', 'como', 'más', 'muy', 'este', 'esta', 'estos', 'estas', 'te', 'tu', 'su', 'sus', 'le', 'les'}
        
        for pub in self.publicaciones:
            # Extraer palabras del título
            palabras = re.findall(r'\b\w+\b', pub.titulo.lower())
            
            for palabra in palabras:
                if len(palabra) > 3 and palabra not in stop_words:  # Solo palabras > 3 caracteres
                    palabras_stats[palabra]['publicaciones'].append(pub)
                    palabras_stats[palabra]['engagement_scores'].append(pub.engagement_score)
                    palabras_stats[palabra]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = []
        for palabra, datos in palabras_stats.items():
            if len(datos['publicaciones']) >= 2:  # Solo palabras usadas al menos 2 veces
                resultado.append({
                    'palabra': palabra,
                    'veces_usada': len(datos['publicaciones']),
                    'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                    'engagement_rate_promedio': statistics.mean(datos['engagement_rates']),
                    'impacto': statistics.mean(datos['engagement_scores']) * len(datos['publicaciones'])  # Score total
                })
        
        # Ordenar por impacto total
        resultado.sort(key=lambda x: x['impacto'], reverse=True)
        return resultado[:top_n]
    
    def detectar_contenido_viral(self) -> Dict[str, Any]:
        """Detecta y analiza contenido viral."""
        publicaciones_virales = [p for p in self.publicaciones if p.es_viral]
        
        if len(publicaciones_virales) == 0:
            return {
                'cantidad': 0,
                'porcentaje': 0.0,
                'caracteristicas_comunes': {}
            }
        
        # Analizar características comunes
        tipos_virales = Counter([p.tipo_contenido for p in publicaciones_virales])
        plataformas_virales = Counter([p.plataforma for p in publicaciones_virales])
        hashtags_virales = Counter()
        
        for pub in publicaciones_virales:
            for hashtag in pub.hashtags:
                hashtags_virales[hashtag.lower()] += 1
        
        return {
            'cantidad': len(publicaciones_virales),
            'porcentaje': (len(publicaciones_virales) / len(self.publicaciones)) * 100,
            'engagement_promedio': statistics.mean([p.engagement_total for p in publicaciones_virales]),
            'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in publicaciones_virales]),
            'tipos_mas_virales': dict(tipos_virales.most_common(3)),
            'plataformas_mas_virales': dict(plataformas_virales.most_common(3)),
            'hashtags_mas_virales': dict(hashtags_virales.most_common(5)),
            'publicaciones': [
                {
                    'id': p.id,
                    'titulo': p.titulo[:50],
                    'tipo': p.tipo_contenido,
                    'plataforma': p.plataforma,
                    'engagement_score': p.engagement_score,
                    'engagement_rate': p.engagement_rate
                }
                for p in sorted(publicaciones_virales, key=lambda x: x.engagement_score, reverse=True)[:5]
            ]
        }
    
    def predecir_engagement(self, tipo: str, plataforma: str, hora: int, dia_semana: str) -> Dict[str, Any]:
        """Predice el engagement potencial basado en patrones históricos."""
        # Filtrar publicaciones similares
        publicaciones_similares = [
            p for p in self.publicaciones
            if p.tipo_contenido == tipo and p.plataforma == plataforma
        ]
        
        if len(publicaciones_similares) == 0:
            return {
                'engagement_score_predicho': 0,
                'engagement_rate_predicho': 0.0,
                'confianza': 0.0,
                'muestra': 0
            }
        
        # Calcular promedios
        engagement_score_promedio = statistics.mean([p.engagement_score for p in publicaciones_similares])
        engagement_rate_promedio = statistics.mean([p.engagement_rate for p in publicaciones_similares])
        
        # Ajustar según horario y día
        horarios_optimos = self.analizar_horarios_optimos()
        dias_optimos = self.analizar_dias_semana()
        
        factor_horario = 1.0
        factor_dia = 1.0
        
        # Determinar rango horario
        if 6 <= hora < 9:
            rango = '06:00-09:00 (Mañana Temprano)'
        elif 9 <= hora < 12:
            rango = '09:00-12:00 (Mañana)'
        elif 12 <= hora < 15:
            rango = '12:00-15:00 (Mediodía)'
        elif 15 <= hora < 18:
            rango = '15:00-18:00 (Tarde)'
        elif 18 <= hora < 21:
            rango = '18:00-21:00 (Noche)'
        else:
            rango = '21:00-06:00 (Noche Tardía)'
        
        mejor_horario_score = max([h['engagement_score_promedio'] for h in horarios_optimos.values()]) if horarios_optimos else engagement_score_promedio
        if rango in horarios_optimos:
            factor_horario = horarios_optimos[rango]['engagement_score_promedio'] / mejor_horario_score if mejor_horario_score > 0 else 1.0
        
        mejor_dia_score = max([d['engagement_score_promedio'] for d in dias_optimos.values()]) if dias_optimos else engagement_score_promedio
        dias_es = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
                  'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        dia_es = dias_es.get(dia_semana, dia_semana)
        if dia_es in dias_optimos:
            factor_dia = dias_optimos[dia_es]['engagement_score_promedio'] / mejor_dia_score if mejor_dia_score > 0 else 1.0
        
        # Calcular predicción ajustada
        engagement_score_predicho = engagement_score_promedio * factor_horario * factor_dia
        engagement_rate_predicho = engagement_rate_promedio * factor_horario * factor_dia
        
        # Calcular confianza basada en tamaño de muestra
        confianza = min(100, (len(publicaciones_similares) / 10) * 100)
        
        return {
            'engagement_score_predicho': engagement_score_predicho,
            'engagement_rate_predicho': engagement_rate_predicho,
            'confianza': confianza,
            'muestra': len(publicaciones_similares),
            'factores': {
                'horario': factor_horario,
                'dia': factor_dia
            }
        }
    
    def analizar_correlaciones(self) -> Dict[str, Any]:
        """Analiza correlaciones entre diferentes variables."""
        correlaciones = {}
        
        # Correlación: Media vs Sin Media
        con_media = [p.engagement_score for p in self.publicaciones if p.tiene_media]
        sin_media = [p.engagement_score for p in self.publicaciones if not p.tiene_media]
        
        if len(con_media) > 0 and len(sin_media) > 0:
            correlaciones['media'] = {
                'con_media_promedio': statistics.mean(con_media),
                'sin_media_promedio': statistics.mean(sin_media),
                'diferencia_porcentual': ((statistics.mean(con_media) - statistics.mean(sin_media)) / statistics.mean(sin_media) * 100) if statistics.mean(sin_media) > 0 else 0
            }
        
        # Correlación: Número de hashtags vs Engagement
        hashtags_engagement = []
        for pub in self.publicaciones:
            hashtags_engagement.append({
                'num_hashtags': len(pub.hashtags),
                'engagement_score': pub.engagement_score
            })
        
        if len(hashtags_engagement) > 1:
            num_hashtags_promedio = statistics.mean([h['num_hashtags'] for h in hashtags_engagement])
            correlaciones['hashtags'] = {
                'hashtags_promedio': num_hashtags_promedio,
                'engagement_con_hashtags': statistics.mean([h['engagement_score'] for h in hashtags_engagement if h['num_hashtags'] > num_hashtags_promedio]),
                'engagement_sin_hashtags': statistics.mean([h['engagement_score'] for h in hashtags_engagement if h['num_hashtags'] <= num_hashtags_promedio])
            }
        
        # Correlación: Longitud del título vs Engagement
        titulos_engagement = []
        for pub in self.publicaciones:
            titulos_engagement.append({
                'longitud': len(pub.titulo),
                'engagement_score': pub.engagement_score
            })
        
        if len(titulos_engagement) > 1:
            longitud_promedio = statistics.mean([t['longitud'] for t in titulos_engagement])
            correlaciones['longitud_titulo'] = {
                'longitud_promedio': longitud_promedio,
                'engagement_titulos_largos': statistics.mean([t['engagement_score'] for t in titulos_engagement if t['longitud'] > longitud_promedio]),
                'engagement_titulos_cortos': statistics.mean([t['engagement_score'] for t in titulos_engagement if t['longitud'] <= longitud_promedio])
            }
        
        return correlaciones
    
    def generar_recomendaciones_avanzadas(self, mejor_tipo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones avanzadas basadas en análisis profundo."""
        recomendaciones = self.generar_recomendaciones(mejor_tipo)
        
        # Agregar recomendaciones basadas en análisis adicionales
        contenido_viral = self.detectar_contenido_viral()
        palabras_clave = self.analizar_palabras_clave_titulos()
        correlaciones = self.analizar_correlaciones()
        horarios_optimos = self.analizar_horarios_optimos()
        
        recomendaciones_avanzadas = []
        
        # Recomendación basada en contenido viral
        if contenido_viral['cantidad'] > 0:
            mejor_tipo_viral = max(contenido_viral['tipos_mas_virales'].items(), key=lambda x: x[1])[0] if contenido_viral['tipos_mas_virales'] else None
            if mejor_tipo_viral:
                recomendaciones_avanzadas.append({
                    'titulo': f'Replicar Patrón de Contenido Viral (Tipo {mejor_tipo_viral})',
                    'descripcion': f'El {contenido_viral["porcentaje"]:.1f}% de tu contenido viral es de tipo {mejor_tipo_viral}. Replica estos patrones.',
                    'razon': f'Tu contenido viral tiene un engagement rate promedio de {contenido_viral["engagement_rate_promedio"]:.2f}%',
                    'accion': 'Analiza las publicaciones virales y replica su estructura, formato y timing',
                    'prioridad': 'Alta'
                })
        
        # Recomendación basada en palabras clave
        if palabras_clave:
            top_palabras = ', '.join([p['palabra'] for p in palabras_clave[:3]])
            recomendaciones_avanzadas.append({
                'titulo': 'Usar Palabras Clave de Alto Impacto',
                'descripcion': f'Incluye estas palabras en tus títulos: {top_palabras}',
                'razon': f'Estas palabras generan un engagement score promedio de {palabras_clave[0]["engagement_score_promedio"]:.1f}',
                'accion': f'Incorpora las palabras: {top_palabras} en tus próximos títulos',
                'prioridad': 'Media'
            })
        
        # Recomendación basada en media
        if correlaciones.get('media'):
            diff = correlaciones['media']['diferencia_porcentual']
            if diff > 20:
                recomendaciones_avanzadas.append({
                    'titulo': 'Incluir Contenido Multimedia',
                    'descripcion': 'Las publicaciones con media tienen un engagement significativamente mayor',
                    'razon': f'El contenido con media tiene {diff:.1f}% más engagement',
                    'accion': 'Asegúrate de incluir imágenes o videos en al menos el 80% de tus publicaciones',
                    'prioridad': 'Alta'
                })
        
        # Recomendación basada en horarios
        if horarios_optimos:
            mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            recomendaciones_avanzadas.append({
                'titulo': 'Optimizar Horarios de Publicación',
                'descripcion': f'Publica más contenido en el horario: {mejor_horario}',
                'razon': f'Este horario genera un engagement score promedio de {horarios_optimos[mejor_horario]["engagement_score_promedio"]:.1f}',
                'accion': f'Programa el 40% de tus publicaciones en el horario {mejor_horario}',
                'prioridad': 'Media'
            })
        
        return recomendaciones + recomendaciones_avanzadas
    
    def generar_calendario_optimizado(self, semanas: int = 4) -> Dict[str, Any]:
        """Genera un calendario de contenido optimizado basado en análisis."""
        horarios_optimos = self.analizar_horarios_optimos()
        dias_optimos = self.analizar_dias_semana()
        mejor_tipo = self.identificar_mejor_tipo()
        analisis_plataformas = self.analizar_por_plataforma()
        
        # Determinar mejor horario y día
        mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios_optimos else None
        mejor_dia = max(dias_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if dias_optimos else None
        mejor_plataforma = max(analisis_plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if analisis_plataformas else None
        
        # Mapeo de días
        dias_map = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3,
            'Viernes': 4, 'Sábado': 5, 'Domingo': 6
        }
        
        # Extraer hora del mejor horario
        hora_optima = 10  # Default
        if mejor_horario:
            match = re.search(r'(\d{2}):\d{2}', mejor_horario)
            if match:
                hora_optima = int(match.group(1))
        
        calendario = []
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Generar calendario para las próximas semanas
        for semana in range(semanas):
            semana_calendario = {
                'semana': semana + 1,
                'fecha_inicio': (fecha_inicio + timedelta(weeks=semana)).strftime('%Y-%m-%d'),
                'publicaciones': []
            }
            
            # Distribuir publicaciones según análisis
            # 40% en mejor día, 30% en segundo mejor día, 30% distribuido
            dias_ordenados = sorted(dias_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'], reverse=True)
            
            for dia_idx, (dia_nombre, datos) in enumerate(dias_ordenados[:3]):
                if dia_nombre in dias_map:
                    dia_num = dias_map[dia_nombre]
                    fecha = fecha_inicio + timedelta(weeks=semana, days=dia_num)
                    
                    # Determinar cantidad de publicaciones según ranking del día
                    if dia_idx == 0:  # Mejor día
                        num_pubs = 2
                    elif dia_idx == 1:  # Segundo mejor
                        num_pubs = 1
                    else:
                        num_pubs = 1
                    
                    for pub_num in range(num_pubs):
                        hora = hora_optima + (pub_num * 2)  # Espaciar 2 horas
                        if hora > 21:
                            hora = hora_optima
                        
                        publicacion_calendario = {
                            'fecha': fecha.strftime('%Y-%m-%d'),
                            'dia': dia_nombre,
                            'hora': f"{hora:02d}:00",
                            'tipo_contenido': mejor_tipo['tipo'],
                            'plataforma': mejor_plataforma or 'Instagram',
                            'titulo_sugerido': f"{mejor_tipo['datos']['nombre']} - Semana {semana + 1}",
                            'hashtags_sugeridos': self.analizar_hashtags_efectivos(5),
                            'engagement_predicho': self.predecir_engagement(
                                mejor_tipo['tipo'],
                                mejor_plataforma or 'Instagram',
                                hora,
                                fecha.strftime('%A')
                            )
                        }
                        
                        semana_calendario['publicaciones'].append(publicacion_calendario)
            
            calendario.append(semana_calendario)
        
        return {
            'semanas': semanas,
            'calendario': calendario,
            'recomendaciones': {
                'mejor_horario': mejor_horario,
                'mejor_dia': mejor_dia,
                'mejor_plataforma': mejor_plataforma,
                'tipo_recomendado': mejor_tipo['tipo']
            }
        }
    
    def analizar_roi_potencial(self) -> Dict[str, Any]:
        """Analiza el ROI potencial basado en engagement."""
        mejor_tipo = self.identificar_mejor_tipo()
        analisis_plataformas = self.analizar_por_plataforma()
        
        # Costos estimados por tipo de contenido (en horas)
        costos_contenido = {
            'X': {'horas': 3, 'descripcion': 'Tutoriales requieren más tiempo de producción'},
            'Y': {'horas': 1, 'descripcion': 'Contenido viral es más rápido de producir'},
            'Z': {'horas': 2, 'descripcion': 'Contenido promocional requiere diseño'}
        }
        
        # Valor estimado por engagement (en dólares)
        valor_por_engagement = {
            'likes': 0.01,
            'comentarios': 0.10,
            'shares': 0.50
        }
        
        # Calcular ROI por tipo
        roi_por_tipo = {}
        for tipo_key, datos in mejor_tipo.get('comparacion_con_otros', {}).items():
            datos_tipo = mejor_tipo['datos'] if tipo_key == mejor_tipo['tipo'] else datos
            costo = costos_contenido.get(tipo_key, {'horas': 2})['horas']
            
            # Calcular valor generado
            valor_likes = datos_tipo['likes_promedio'] * valor_por_engagement['likes']
            valor_comentarios = datos_tipo['comentarios_promedio'] * valor_por_engagement['comentarios']
            valor_shares = datos_tipo['shares_promedio'] * valor_por_engagement['shares']
            valor_total = valor_likes + valor_comentarios + valor_shares
            
            # ROI = (Valor - Costo) / Costo * 100
            # Asumiendo costo de $50/hora
            costo_total = costo * 50
            roi = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
            
            roi_por_tipo[tipo_key] = {
                'tipo': tipo_key,
                'nombre': datos_tipo.get('nombre', tipo_key),
                'costo_horas': costo,
                'costo_estimado': costo_total,
                'valor_generado': valor_total,
                'roi_porcentaje': roi,
                'publicaciones_necesarias_para_roi_positivo': math.ceil(costo_total / valor_total) if valor_total > 0 else 0
            }
        
        # ROI por plataforma
        roi_por_plataforma = {}
        for plataforma, datos in analisis_plataformas.items():
            valor_likes = datos['likes_promedio'] * valor_por_engagement['likes']
            valor_comentarios = datos['comentarios_promedio'] * valor_por_engagement['comentarios']
            valor_shares = datos['shares_promedio'] * valor_por_engagement['shares']
            valor_total = valor_likes + valor_comentarios + valor_shares
            
            # Costo promedio por plataforma
            costo_promedio = 100  # $100 por publicación promedio
            roi = ((valor_total - costo_promedio) / costo_promedio * 100) if costo_promedio > 0 else 0
            
            roi_por_plataforma[plataforma] = {
                'plataforma': plataforma,
                'valor_generado': valor_total,
                'costo_estimado': costo_promedio,
                'roi_porcentaje': roi
            }
        
        return {
            'roi_por_tipo': roi_por_tipo,
            'roi_por_plataforma': roi_por_plataforma,
            'mejor_roi_tipo': max(roi_por_tipo.items(), key=lambda x: x[1]['roi_porcentaje'])[0] if roi_por_tipo else None,
            'mejor_roi_plataforma': max(roi_por_plataforma.items(), key=lambda x: x[1]['roi_porcentaje'])[0] if roi_por_plataforma else None,
            'metricas_valor': valor_por_engagement
        }
    
    def generar_alertas_criticas(self, reporte: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera alertas críticas basadas en el análisis."""
        alertas = []
        
        # Alerta: Tendencia decreciente
        if reporte['resumen_ejecutivo'].get('cambio_tendencia', 0) < -20:
            alertas.append({
                'nivel': 'CRÍTICO',
                'titulo': 'Tendencia Decreciente Detectada',
                'mensaje': f"El engagement ha disminuido un {abs(reporte['resumen_ejecutivo']['cambio_tendencia']):.1f}%",
                'accion': 'Revisar estrategia de contenido inmediatamente',
                'prioridad': 1
            })
        
        # Alerta: Bajo contenido viral
        if reporte['resumen_ejecutivo'].get('contenido_viral_porcentaje', 0) < 5:
            alertas.append({
                'nivel': 'ALTA',
                'titulo': 'Bajo Porcentaje de Contenido Viral',
                'mensaje': f"Solo el {reporte['resumen_ejecutivo']['contenido_viral_porcentaje']:.1f}% del contenido es viral",
                'accion': 'Aumentar producción de contenido de alto engagement',
                'prioridad': 2
            })
        
        # Alerta: Plataforma subóptima
        mejor_plataforma = reporte['resumen_ejecutivo'].get('mejor_plataforma')
        if mejor_plataforma:
            analisis_plataformas = reporte.get('analisis_por_plataforma', {})
            if len(analisis_plataformas) > 1:
                plataformas_ordenadas = sorted(
                    analisis_plataformas.items(),
                    key=lambda x: x[1]['engagement_score_promedio'],
                    reverse=True
                )
                peor_plataforma = plataformas_ordenadas[-1]
                diferencia = plataformas_ordenadas[0][1]['engagement_score_promedio'] - peor_plataforma[1]['engagement_score_promedio']
                
                if diferencia > 200:
                    alertas.append({
                        'nivel': 'MEDIA',
                        'titulo': f'Plataforma {peor_plataforma[0]} con Bajo Rendimiento',
                        'mensaje': f"{peor_plataforma[0]} tiene {diferencia:.1f} puntos menos que {mejor_plataforma}",
                        'accion': f'Considerar reducir contenido en {peor_plataforma[0]} o mejorar estrategia',
                        'prioridad': 3
                    })
        
        # Alerta: Engagement rate bajo
        engagement_rate = reporte['resumen_ejecutivo'].get('engagement_rate_promedio', 0)
        if engagement_rate < 3.0:
            alertas.append({
                'nivel': 'ALTA',
                'titulo': 'Engagement Rate Bajo',
                'mensaje': f"El engagement rate promedio es {engagement_rate:.2f}%, por debajo del estándar (3-5%)",
                'accion': 'Revisar calidad del contenido y timing de publicaciones',
                'prioridad': 2
            })
        
        return sorted(alertas, key=lambda x: x['prioridad'])
    
    def analizar_benchmarking(self) -> Dict[str, Any]:
        """Analiza benchmarking contra estándares de la industria."""
        # Benchmarks estándar de la industria
        benchmarks = {
            'engagement_rate': {
                'excelente': 5.0,
                'bueno': 3.0,
                'promedio': 1.5,
                'bajo': 0.5
            },
            'engagement_score': {
                'excelente': 500,
                'bueno': 300,
                'promedio': 150,
                'bajo': 50
            },
            'contenido_viral': {
                'excelente': 10.0,
                'bueno': 5.0,
                'promedio': 2.0,
                'bajo': 0.0
            }
        }
        
        mejor_tipo = self.identificar_mejor_tipo()
        contenido_viral = self.detectar_contenido_viral()
        
        engagement_rate = mejor_tipo['datos']['engagement_rate_promedio']
        engagement_score = mejor_tipo['datos']['engagement_score_promedio']
        viral_porcentaje = contenido_viral.get('porcentaje', 0)
        
        # Clasificar performance
        def clasificar(valor, benchmarks_dict):
            if valor >= benchmarks_dict['excelente']:
                return 'excelente', '🟢'
            elif valor >= benchmarks_dict['bueno']:
                return 'bueno', '🟡'
            elif valor >= benchmarks_dict['promedio']:
                return 'promedio', '🟠'
            else:
                return 'bajo', '🔴'
        
        clasificacion_rate, emoji_rate = clasificar(engagement_rate, benchmarks['engagement_rate'])
        clasificacion_score, emoji_score = clasificar(engagement_score, benchmarks['engagement_score'])
        clasificacion_viral, emoji_viral = clasificar(viral_porcentaje, benchmarks['contenido_viral'])
        
        # Calcular diferencia con benchmarks
        diferencia_excelente_rate = engagement_rate - benchmarks['engagement_rate']['excelente']
        diferencia_excelente_score = engagement_score - benchmarks['engagement_score']['excelente']
        
        return {
            'engagement_rate': {
                'valor': engagement_rate,
                'benchmark_excelente': benchmarks['engagement_rate']['excelente'],
                'clasificacion': clasificacion_rate,
                'emoji': emoji_rate,
                'diferencia_excelente': diferencia_excelente_rate,
                'porcentaje_del_excelente': (engagement_rate / benchmarks['engagement_rate']['excelente'] * 100) if benchmarks['engagement_rate']['excelente'] > 0 else 0
            },
            'engagement_score': {
                'valor': engagement_score,
                'benchmark_excelente': benchmarks['engagement_score']['excelente'],
                'clasificacion': clasificacion_score,
                'emoji': emoji_score,
                'diferencia_excelente': diferencia_excelente_score,
                'porcentaje_del_excelente': (engagement_score / benchmarks['engagement_score']['excelente'] * 100) if benchmarks['engagement_score']['excelente'] > 0 else 0
            },
            'contenido_viral': {
                'valor': viral_porcentaje,
                'benchmark_excelente': benchmarks['contenido_viral']['excelente'],
                'clasificacion': clasificacion_viral,
                'emoji': emoji_viral,
                'diferencia_excelente': viral_porcentaje - benchmarks['contenido_viral']['excelente'],
                'porcentaje_del_excelente': (viral_porcentaje / benchmarks['contenido_viral']['excelente'] * 100) if benchmarks['contenido_viral']['excelente'] > 0 else 0
            },
            'score_general': statistics.mean([
                (engagement_rate / benchmarks['engagement_rate']['excelente'] * 100),
                (engagement_score / benchmarks['engagement_score']['excelente'] * 100),
                (viral_porcentaje / benchmarks['contenido_viral']['excelente'] * 100) if benchmarks['contenido_viral']['excelente'] > 0 else 0
            ])
        }
    
    def detectar_contenido_mejorable(self) -> List[Dict[str, Any]]:
        """Detecta publicaciones que necesitan mejoras."""
        mejor_tipo = self.identificar_mejor_tipo()
        mejor_score = mejor_tipo['datos']['engagement_score_promedio']
        mejor_rate = mejor_tipo['datos']['engagement_rate_promedio']
        
        contenido_mejorable = []
        
        for pub in self.publicaciones:
            # Criterios para contenido mejorable
            razones = []
            
            # Score muy bajo comparado con el mejor
            if pub.engagement_score < mejor_score * 0.3:
                razones.append(f"Engagement score muy bajo ({pub.engagement_score:.1f} vs {mejor_score:.1f})")
            
            # Engagement rate bajo
            if pub.engagement_rate < mejor_rate * 0.5:
                razones.append(f"Engagement rate bajo ({pub.engagement_rate:.2f}% vs {mejor_rate:.2f}%)")
            
            # Sin media cuando debería tenerla
            if not pub.tiene_media and pub.tipo_contenido == mejor_tipo['tipo']:
                razones.append("Falta contenido multimedia")
            
            # Muy pocos hashtags
            if len(pub.hashtags) < 3:
                razones.append(f"Muy pocos hashtags ({len(pub.hashtags)})")
            
            # Ratio de compartidos muy bajo
            if pub.ratio_compartidos < 5:
                razones.append(f"Bajo ratio de compartidos ({pub.ratio_compartidos:.1f}%)")
            
            if razones:
                contenido_mejorable.append({
                    'id': pub.id,
                    'titulo': pub.titulo[:60],
                    'tipo': pub.tipo_contenido,
                    'plataforma': pub.plataforma,
                    'fecha': pub.fecha_publicacion.strftime('%Y-%m-%d'),
                    'engagement_score': pub.engagement_score,
                    'engagement_rate': pub.engagement_rate,
                    'razones': razones,
                    'prioridad': 'ALTA' if len(razones) >= 3 else 'MEDIA',
                    'mejoras_sugeridas': self._generar_mejoras_sugeridas(pub, mejor_tipo)
                })
        
        # Ordenar por prioridad y score
        contenido_mejorable.sort(key=lambda x: (x['prioridad'] == 'ALTA', -x['engagement_score']))
        
        return contenido_mejorable[:10]  # Top 10
    
    def _generar_mejoras_sugeridas(self, pub: Publicacion, mejor_tipo: Dict[str, Any]) -> List[str]:
        """Genera sugerencias de mejora para una publicación."""
        mejoras = []
        
        if not pub.tiene_media:
            mejoras.append("Agregar imagen o video")
        
        if len(pub.hashtags) < 5:
            mejoras.append(f"Agregar más hashtags (actualmente {len(pub.hashtags)})")
        
        if pub.tipo_contenido != mejor_tipo['tipo']:
            mejoras.append(f"Considerar cambiar a tipo {mejor_tipo['tipo']} ({mejor_tipo['datos']['nombre']})")
        
        horarios_optimos = self.analizar_horarios_optimos()
        if horarios_optimos:
            mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0]
            hora_actual = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
            mejoras.append(f"Publicar en horario óptimo: {mejor_horario}")
        
        return mejoras
    
    def analizar_por_tipo(self) -> Dict[str, Any]:
        """Analiza el engagement por tipo de contenido."""
        analisis = defaultdict(lambda: {
            'publicaciones': [],
            'total_likes': 0,
            'total_comentarios': 0,
            'total_shares': 0,
            'total_impresiones': 0,
            'total_reach': 0,
            'engagement_scores': [],
            'engagement_rates': [],
            'plataformas': defaultdict(int),
            'con_media': 0,
            'sin_media': 0
        })
        
        for pub in self.publicaciones:
            tipo = pub.tipo_contenido
            analisis[tipo]['publicaciones'].append(pub)
            analisis[tipo]['total_likes'] += pub.likes
            analisis[tipo]['total_comentarios'] += pub.comentarios
            analisis[tipo]['total_shares'] += pub.shares
            analisis[tipo]['total_impresiones'] += pub.impresiones
            analisis[tipo]['total_reach'] += pub.reach
            analisis[tipo]['engagement_scores'].append(pub.engagement_score)
            analisis[tipo]['engagement_rates'].append(pub.engagement_rate)
            analisis[tipo]['plataformas'][pub.plataforma] += 1
            
            if pub.tiene_media:
                analisis[tipo]['con_media'] += 1
            else:
                analisis[tipo]['sin_media'] += 1
        
        # Calcular promedios y estadísticas
        resultado = {}
        for tipo, datos in analisis.items():
            num_pubs = len(datos['publicaciones'])
            if num_pubs == 0:
                continue
            
            total_engagement = datos['total_likes'] + datos['total_comentarios'] + datos['total_shares']
            
            resultado[tipo] = {
                'nombre': datos['publicaciones'][0].metadata.get('tipo_nombre', tipo),
                'cantidad_publicaciones': num_pubs,
                'engagement_total': total_engagement,
                'engagement_promedio': total_engagement / num_pubs,
                'engagement_score_promedio': statistics.mean(datos['engagement_scores']),
                'engagement_rate_promedio': statistics.mean(datos['engagement_rates']),
                'likes_promedio': datos['total_likes'] / num_pubs,
                'comentarios_promedio': datos['total_comentarios'] / num_pubs,
                'shares_promedio': datos['total_shares'] / num_pubs,
                'impresiones_promedio': datos['total_impresiones'] / num_pubs,
                'reach_promedio': datos['total_reach'] / num_pubs,
                'porcentaje_con_media': (datos['con_media'] / num_pubs) * 100,
                'plataformas_mas_usadas': dict(sorted(
                    datos['plataformas'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )),
                'mejor_publicacion': max(
                    datos['publicaciones'],
                    key=lambda p: p.engagement_score
                )
            }
        
        return resultado
    
    def identificar_mejor_tipo(self) -> Dict[str, Any]:
        """Identifica el tipo de contenido con mejor engagement."""
        analisis = self.analizar_por_tipo()
        
        if not analisis:
            return {}
        
        # Ordenar por engagement_score_promedio
        tipos_ordenados = sorted(
            analisis.items(),
            key=lambda x: x[1]['engagement_score_promedio'],
            reverse=True
        )
        
        mejor_tipo_key, mejor_tipo_data = tipos_ordenados[0]
        
        # Analizar por qué es mejor
        razones = []
        
        # Comparar con otros tipos
        otros_tipos = {k: v for k, v in analisis.items() if k != mejor_tipo_key}
        
        for otro_tipo_key, otro_tipo_data in otros_tipos.items():
            diferencia_score = mejor_tipo_data['engagement_score_promedio'] - otro_tipo_data['engagement_score_promedio']
            diferencia_rate = mejor_tipo_data['engagement_rate_promedio'] - otro_tipo_data['engagement_rate_promedio']
            
            if diferencia_score > 0:
                razones.append(
                    f"Supera a {otro_tipo_data['nombre']} por {diferencia_score:.1f} puntos "
                    f"en engagement score ({diferencia_rate:.2f}% más en engagement rate)"
                )
        
        # Analizar características específicas
        caracteristicas = []
        if mejor_tipo_data['comentarios_promedio'] > mejor_tipo_data['likes_promedio'] * 0.2:
            caracteristicas.append("Genera alta participación en comentarios (más del 20% de likes)")
        if mejor_tipo_data['shares_promedio'] > mejor_tipo_data['likes_promedio'] * 0.15:
            caracteristicas.append("Alto índice de compartidos (más del 15% de likes)")
        if mejor_tipo_data['porcentaje_con_media'] > 85:
            caracteristicas.append("Mayoría de publicaciones incluyen contenido multimedia")
        
        return {
            'tipo': mejor_tipo_key,
            'datos': mejor_tipo_data,
            'razones_superioridad': razones,
            'caracteristicas_clave': caracteristicas,
            'comparacion_con_otros': otros_tipos
        }
    
    def generar_recomendaciones(self, mejor_tipo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera 5 recomendaciones basadas en el patrón del mejor tipo."""
        tipo_key = mejor_tipo['tipo']
        datos = mejor_tipo['datos']
        
        recomendaciones = []
        
        # Basadas en las características del mejor tipo
        if tipo_key == 'X':  # Tutoriales/Educativos
            recomendaciones = [
                {
                    'titulo': 'Serie de Tutoriales Paso a Paso',
                    'descripcion': 'Crear una serie semanal de tutoriales cortos (5-10 min) sobre temas específicos',
                    'razon': 'Los tutoriales generan alto engagement porque proporcionan valor inmediato',
                    'formato_sugerido': 'Video corto con capturas de pantalla y narración',
                    'hashtags_sugeridos': ['#tutorial', '#aprende', '#pasoapaso', '#tips'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Tips Rápidos en Formato Carousel',
                    'descripcion': 'Publicaciones tipo carousel con 5-7 tips visuales y concisos',
                    'razon': 'El formato carousel mantiene a la audiencia comprometida y genera más tiempo de visualización',
                    'formato_sugerido': 'Carousel de Instagram/LinkedIn con imágenes/texto',
                    'hashtags_sugeridos': ['#tips', '#consejos', '#productividad', '#aprende'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Casos de Estudio con Resultados',
                    'descripcion': 'Mostrar casos reales de cómo aplicar conocimientos con resultados medibles',
                    'razon': 'Los casos de estudio generan credibilidad y comentarios de personas que quieren replicar',
                    'formato_sugerido': 'Post largo con imágenes antes/después o métricas',
                    'hashtags_sugeridos': ['#casoestudio', '#resultados', '#exito', '#aprende'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Preguntas y Respuestas en Vivo',
                    'descripcion': 'Sesiones de Q&A donde respondes preguntas frecuentes de tu audiencia',
                    'razon': 'El formato interactivo genera alta participación en comentarios y shares',
                    'formato_sugerido': 'Video en vivo o Stories con preguntas',
                    'hashtags_sugeridos': ['#preguntas', '#respuestas', '#live', '#comunidad'],
                    'frecuencia': '1 vez cada 2 semanas'
                },
                {
                    'titulo': 'Guías Descargables Gratuitas',
                    'descripcion': 'Crear PDFs o recursos descargables que complementen tus publicaciones',
                    'razon': 'Los recursos descargables generan saves y shares, aumentando el engagement',
                    'formato_sugerido': 'Post con link a descarga + preview del contenido',
                    'hashtags_sugeridos': ['#descarga', '#gratis', '#recurso', '#guia'],
                    'frecuencia': '1 vez por semana'
                }
            ]
        
        elif tipo_key == 'Y':  # Entretenimiento/Viral
            recomendaciones = [
                {
                    'titulo': 'Contenido Behind-the-Scenes',
                    'descripcion': 'Mostrar el proceso detrás de tus proyectos o trabajo diario',
                    'razon': 'El contenido auténtico y personal genera conexión emocional',
                    'formato_sugerido': 'Stories o posts cortos con videos casuales',
                    'hashtags_sugeridos': ['#behindthescenes', '#proceso', '#real', '#autentico'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Desafíos o Trends Populares',
                    'descripcion': 'Adaptar trends virales del momento a tu nicho o industria',
                    'razon': 'Los trends tienen alto potencial de alcance orgánico',
                    'formato_sugerido': 'Video corto siguiendo el formato del trend',
                    'hashtags_sugeridos': ['#trending', '#viral', '#challenge', '#moda'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Memes Relacionados con tu Industria',
                    'descripcion': 'Crear memes divertidos pero relevantes para tu audiencia',
                    'razon': 'Los memes generan shares rápidos y engagement emocional',
                    'formato_sugerido': 'Imagen con texto o formato meme estándar',
                    'hashtags_sugeridos': ['#meme', '#humor', '#divertido', '#relatable'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Historias Inspiradoras o Motivacionales',
                    'descripcion': 'Compartir historias personales o de clientes que inspiren',
                    'razon': 'El contenido emocional genera comentarios y conexión profunda',
                    'formato_sugerido': 'Post largo con texto o video narrado',
                    'hashtags_sugeridos': ['#inspiracion', '#motivacion', '#historia', '#exito'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Contenido Interactivo (Polls, Quizzes)',
                    'descripcion': 'Usar features interactivas de las plataformas (encuestas, preguntas)',
                    'razon': 'La interacción directa aumenta el engagement y tiempo en plataforma',
                    'formato_sugerido': 'Stories con polls o posts con preguntas',
                    'hashtags_sugeridos': ['#interactivo', '#encuesta', '#comunidad', '#participa'],
                    'frecuencia': '2-3 veces por semana'
                }
            ]
        
        else:  # Z: Promocional/Producto
            recomendaciones = [
                {
                    'titulo': 'Educación sobre el Producto',
                    'descripcion': 'Convertir promociones en contenido educativo sobre beneficios y uso',
                    'razon': 'El contenido educativo genera más engagement que promociones directas',
                    'formato_sugerido': 'Video tutorial mostrando el producto en uso',
                    'hashtags_sugeridos': ['#tutorial', '#producto', '#beneficios', '#como'],
                    'frecuencia': '1-2 veces por semana'
                },
                {
                    'titulo': 'Testimonios y Reviews de Clientes',
                    'descripcion': 'Mostrar resultados reales de clientes usando tu producto/servicio',
                    'razon': 'La prueba social genera credibilidad y engagement orgánico',
                    'formato_sugerido': 'Video testimonial o post con imágenes de resultados',
                    'hashtags_sugeridos': ['#testimonial', '#review', '#cliente', '#resultados'],
                    'frecuencia': '1 vez por semana'
                },
                {
                    'titulo': 'Comparativas y Demostraciones',
                    'descripcion': 'Mostrar comparaciones antes/después o vs competencia',
                    'razon': 'Las comparativas ayudan a la decisión y generan comentarios',
                    'formato_sugerido': 'Carousel o video con comparación visual',
                    'hashtags_sugeridos': ['#comparacion', '#demo', '#antesydespues', '#mejor'],
                    'frecuencia': '1 vez cada 2 semanas'
                },
                {
                    'titulo': 'Contenido de Valor Gratuito',
                    'descripcion': 'Ofrecer valor primero (consejos, herramientas) antes de promocionar',
                    'razon': 'El contenido de valor genera confianza y aumenta el engagement',
                    'formato_sugerido': 'Post educativo con call-to-action suave al final',
                    'hashtags_sugeridos': ['#gratis', '#valor', '#consejo', '#herramienta'],
                    'frecuencia': '2-3 veces por semana'
                },
                {
                    'titulo': 'Lanzamientos con Anticipación',
                    'descripcion': 'Crear expectativa con contenido de "próximamente" y detrás de escena',
                    'razon': 'La anticipación genera engagement antes del lanzamiento',
                    'formato_sugerido': 'Serie de posts contando la historia del desarrollo',
                    'hashtags_sugeridos': ['#proximamente', '#lanzamiento', '#nuevo', '#exclusivo'],
                    'frecuencia': 'Durante campañas de lanzamiento'
                }
            ]
        
        return recomendaciones
    
    def generar_reporte(self) -> Dict[str, Any]:
        """Genera un reporte completo del análisis."""
        mejor_tipo = self.identificar_mejor_tipo()
        recomendaciones = self.generar_recomendaciones_avanzadas(mejor_tipo)
        analisis_completo = self.analizar_por_tipo()
        horarios_optimos = self.analizar_horarios_optimos()
        dias_semana = self.analizar_dias_semana()
        hashtags_efectivos = self.analizar_hashtags_efectivos()
        analisis_plataformas = self.analizar_por_plataforma()
        tendencias = self.analizar_tendencias_temporales()
        palabras_clave = self.analizar_palabras_clave_titulos()
        contenido_viral = self.detectar_contenido_viral()
        correlaciones = self.analizar_correlaciones()
        benchmarking = self.analizar_benchmarking()
        contenido_mejorable = self.detectar_contenido_mejorable()
        
        # Generar reporte base
        reporte_base = {
            'fecha_analisis': datetime.now().isoformat(),
            'periodo_analizado': 'Últimos 30 días',
            'total_publicaciones': len(self.publicaciones),
            'mejor_tipo_contenido': mejor_tipo,
            'analisis_por_tipo': analisis_completo,
            'analisis_por_plataforma': analisis_plataformas,
            'horarios_optimos': horarios_optimos,
            'dias_semana_optimos': dias_semana,
            'hashtags_mas_efectivos': hashtags_efectivos,
            'tendencias_temporales': tendencias,
            'palabras_clave_efectivas': palabras_clave,
            'contenido_viral': contenido_viral,
            'correlaciones': correlaciones,
            'recomendaciones': recomendaciones,
            'resumen_ejecutivo': {
                'tipo_ganador': mejor_tipo['tipo'],
                'nombre_tipo': mejor_tipo['datos']['nombre'],
                'engagement_rate_promedio': mejor_tipo['datos']['engagement_rate_promedio'],
                'engagement_score_promedio': mejor_tipo['datos']['engagement_score_promedio'],
                'razones_principales': mejor_tipo['razones_superioridad'][:3],
                'caracteristicas_clave': mejor_tipo['caracteristicas_clave'],
                'mejor_horario': max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios_optimos else None,
                'mejor_dia': max(dias_semana.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if dias_semana else None,
                'mejor_plataforma': max(analisis_plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if analisis_plataformas else None,
                'tendencia': tendencias.get('direccion', 'estable'),
                'cambio_tendencia': tendencias.get('cambio_porcentual', 0),
                'contenido_viral_porcentaje': contenido_viral.get('porcentaje', 0)
            }
        }
        
        # Agregar análisis de IA si está disponible
        if self.ai and self.ai.enabled:
            print("🤖 Generando análisis con IA...")
            try:
                # Generar recomendaciones inteligentes con IA
                recomendaciones_ai = self.ai.generar_recomendaciones_contenido(reporte_base)
                if 'error' not in recomendaciones_ai:
                    reporte_base['recomendaciones_ai'] = recomendaciones_ai
                
                # Analizar sentimiento y calidad del contenido
                analisis_sentimiento = self.ai.analizar_sentimiento_contenido(self.publicaciones)
                if 'error' not in analisis_sentimiento:
                    reporte_base['analisis_sentimiento_ai'] = analisis_sentimiento
                
                # Generar descripción narrativa de insights
                insights_data = {
                    'mejor_tipo': mejor_tipo['datos']['nombre'],
                    'engagement_rate': mejor_tipo['datos']['engagement_rate_promedio'],
                    'mejor_plataforma': reporte_base['resumen_ejecutivo']['mejor_plataforma'],
                    'mejor_horario': reporte_base['resumen_ejecutivo']['mejor_horario']
                }
                descripcion_insights = self.ai.generar_descripcion_insights(insights_data)
                reporte_base['descripcion_insights_ai'] = descripcion_insights
                
                print("✅ Análisis con IA completado")
            except Exception as e:
                print(f"⚠️  Error en análisis de IA: {e}")
                reporte_base['ai_error'] = str(e)
        
        # Agregar alertas críticas
        reporte_base['alertas_criticas'] = self.generar_alertas_criticas(reporte_base)
        
        # Agregar análisis avanzado de hashtags
        if self.enable_tiktok_hashtags:
            try:
                reporte_base['hashtags_optimizados'] = self.recomendar_hashtags_por_tipo_contenido()
                reporte_base['hashtags_por_plataforma'] = self.analizar_hashtags_por_plataforma()
            except Exception as e:
                reporte_base['hashtags_error'] = str(e)
        
        # Agregar análisis ML avanzado
        try:
            # Detección de anomalías
            anomalias = self.detectar_anomalias_engagement()
            if anomalias:
                reporte_base['anomalias_engagement'] = anomalias[:10]  # Top 10
            
            # Clustering de contenido
            if HAS_SKLEARN and len(self.publicaciones) >= 5:
                clusters = self.clusterizar_contenido(n_clusters=3)
                if 'error' not in clusters:
                    reporte_base['clustering_contenido'] = clusters
            
            # Estrategia optimizada
            estrategia = self.generar_estrategia_optimizada()
            reporte_base['estrategia_optimizada'] = estrategia
            
            # Análisis de tendencias futuras
            if HAS_SKLEARN and len(self.publicaciones) >= 7:
                tendencias_futuras = self.analizar_tendencias_futuras(dias_proyeccion=30)
                if 'error' not in tendencias_futuras:
                    reporte_base['tendencias_futuras'] = tendencias_futuras
            
            # Calendario optimizado
            calendario = self.optimizar_calendario_contenido(num_semanas=4)
            reporte_base['calendario_optimizado'] = calendario
            
            # Ideas de contenido basadas en tendencias
            ideas_contenido = self.generar_ideas_contenido_tendencias(num_ideas=5)
            reporte_base['ideas_contenido_tendencias'] = ideas_contenido
            
            # Sistema de alertas inteligentes
            alertas_sistema = self.crear_sistema_alertas()
            reporte_base['alertas_sistema'] = alertas_sistema
            
            # Plan de acción para mejora
            plan_accion = self.generar_plan_accion_mejora()
            if 'error' not in plan_accion:
                reporte_base['plan_accion_mejora'] = plan_accion
            
        except Exception as e:
            reporte_base['ml_error'] = str(e)
        
        # Agregar análisis específico de LinkedIn si hay posts de LinkedIn
        try:
            linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
            if linkedin_posts:
                print("📊 Generando análisis específico de LinkedIn...")
                analisis_linkedin = self.analizar_linkedin_especifico()
                if 'error' not in analisis_linkedin:
                    reporte_base['analisis_linkedin'] = analisis_linkedin
                    # Agregar recomendaciones específicas de LinkedIn
                    recomendaciones_linkedin = self.generar_recomendaciones_linkedin()
                    if recomendaciones_linkedin:
                        reporte_base['recomendaciones_linkedin'] = recomendaciones_linkedin
                print("✅ Análisis de LinkedIn completado")
        except Exception as e:
            reporte_base['linkedin_error'] = str(e)
        
        return reporte_base
    
    def exportar_csv(self, reporte: Dict[str, Any], output_file: str):
        """Exporta el reporte a CSV."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir publicaciones
            writer.writerow(['=== PUBLICACIONES ==='])
            writer.writerow([
                'ID', 'Tipo', 'Título', 'Plataforma', 'Fecha', 'Likes', 
                'Comentarios', 'Shares', 'Impresiones', 'Reach', 
                'Engagement Rate', 'Engagement Score', 'Hashtags'
            ])
            
            for pub in self.publicaciones:
                writer.writerow([
                    pub.id, pub.tipo_contenido, pub.titulo[:50], pub.plataforma,
                    pub.fecha_publicacion.strftime('%Y-%m-%d %H:%M'),
                    pub.likes, pub.comentarios, pub.shares, pub.impresiones,
                    pub.reach, f"{pub.engagement_rate:.2f}%", 
                    f"{pub.engagement_score:.1f}", ', '.join(pub.hashtags[:5])
                ])
            
            # Escribir análisis por tipo
            writer.writerow([])
            writer.writerow(['=== ANÁLISIS POR TIPO ==='])
            writer.writerow([
                'Tipo', 'Nombre', 'Cantidad', 'Engagement Total', 
                'Engagement Promedio', 'Engagement Rate', 'Likes Promedio',
                'Comentarios Promedio', 'Shares Promedio'
            ])
            
            for tipo, datos in reporte['analisis_por_tipo'].items():
                writer.writerow([
                    tipo, datos['nombre'], datos['cantidad_publicaciones'],
                    datos['engagement_total'], datos['engagement_promedio'],
                    f"{datos['engagement_rate_promedio']:.2f}%",
                    datos['likes_promedio'], datos['comentarios_promedio'],
                    datos['shares_promedio']
                ])
    
    def exportar_html(self, reporte: Dict[str, Any], output_file: str):
        """Exporta el reporte a HTML con visualizaciones."""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Engagement - {datetime.now().strftime('%d/%m/%Y')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            min-width: 200px;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .recommendation {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .recommendation h4 {{
            color: #667eea;
            margin-bottom: 8px;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 2px;
            background: #667eea;
            color: white;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Engagement de Contenido</h1>
        <p><strong>Fecha de análisis:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p><strong>Período analizado:</strong> {reporte['periodo_analizado']}</p>
        <p><strong>Total de publicaciones:</strong> {reporte['total_publicaciones']}</p>
        
        <div class="summary-box">
            <h2>🏆 Resumen Ejecutivo</h2>
            <div class="metric">
                <div class="metric-label">Tipo Ganador</div>
                <div class="metric-value">{reporte['resumen_ejecutivo']['nombre_tipo']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Engagement Rate</div>
                <div class="metric-value">{reporte['resumen_ejecutivo']['engagement_rate_promedio']:.2f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Engagement Score</div>
                <div class="metric-value">{reporte['resumen_ejecutivo']['engagement_score_promedio']:.1f}</div>
            </div>
        </div>
        
        <h2>📈 Análisis por Tipo de Contenido</h2>
        <table>
            <tr>
                <th>Tipo</th>
                <th>Nombre</th>
                <th>Cantidad</th>
                <th>Engagement Rate</th>
                <th>Engagement Score</th>
                <th>Likes Promedio</th>
                <th>Comentarios Promedio</th>
                <th>Shares Promedio</th>
            </tr>
"""
        
        for tipo, datos in reporte['analisis_por_tipo'].items():
            html += f"""
            <tr>
                <td><strong>{tipo}</strong></td>
                <td>{datos['nombre']}</td>
                <td>{datos['cantidad_publicaciones']}</td>
                <td>{datos['engagement_rate_promedio']:.2f}%</td>
                <td>{datos['engagement_score_promedio']:.1f}</td>
                <td>{datos['likes_promedio']:.1f}</td>
                <td>{datos['comentarios_promedio']:.1f}</td>
                <td>{datos['shares_promedio']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>🌐 Análisis por Plataforma</h2>
        <table>
            <tr>
                <th>Plataforma</th>
                <th>Cantidad</th>
                <th>Engagement Rate</th>
                <th>Engagement Score</th>
                <th>Likes Promedio</th>
            </tr>
"""
        
        for plataforma, datos in reporte['analisis_por_plataforma'].items():
            html += f"""
            <tr>
                <td><strong>{plataforma}</strong></td>
                <td>{datos['cantidad_publicaciones']}</td>
                <td>{datos['engagement_rate_promedio']:.2f}%</td>
                <td>{datos['engagement_score_promedio']:.1f}</td>
                <td>{datos['likes_promedio']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>⏰ Horarios Óptimos</h2>
        <table>
            <tr>
                <th>Horario</th>
                <th>Cantidad</th>
                <th>Engagement Rate</th>
                <th>Engagement Score</th>
            </tr>
"""
        
        for horario, datos in sorted(reporte['horarios_optimos'].items(), 
                                     key=lambda x: x[1]['engagement_score_promedio'], 
                                     reverse=True):
            html += f"""
            <tr>
                <td><strong>{horario}</strong></td>
                <td>{datos['cantidad']}</td>
                <td>{datos['engagement_rate_promedio']:.2f}%</td>
                <td>{datos['engagement_score_promedio']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>📅 Días de la Semana</h2>
        <table>
            <tr>
                <th>Día</th>
                <th>Cantidad</th>
                <th>Engagement Rate</th>
                <th>Engagement Score</th>
            </tr>
"""
        
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for dia in orden_dias:
            if dia in reporte['dias_semana_optimos']:
                datos = reporte['dias_semana_optimos'][dia]
                html += f"""
            <tr>
                <td><strong>{dia}</strong></td>
                <td>{datos['cantidad']}</td>
                <td>{datos['engagement_rate_promedio']:.2f}%</td>
                <td>{datos['engagement_score_promedio']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>#️⃣ Hashtags Más Efectivos</h2>
        <table>
            <tr>
                <th>Hashtag</th>
                <th>Veces Usado</th>
                <th>Engagement Rate</th>
                <th>Engagement Score</th>
            </tr>
"""
        
        for hashtag_data in reporte['hashtags_mas_efectivos'][:10]:
            html += f"""
            <tr>
                <td><span class="badge">#{hashtag_data['hashtag']}</span></td>
                <td>{hashtag_data['veces_usado']}</td>
                <td>{hashtag_data['engagement_rate_promedio']:.2f}%</td>
                <td>{hashtag_data['engagement_score_promedio']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>📊 Tendencias Temporales</h2>
        <table>
            <tr>
                <th>Semana</th>
                <th>Publicaciones</th>
                <th>Engagement Promedio</th>
                <th>Engagement Rate</th>
                <th>Contenido Viral</th>
            </tr>
"""
        
        for semana, datos in sorted(reporte['tendencias_temporales']['tendencias_semanales'].items()):
            html += f"""
            <tr>
                <td><strong>{semana}</strong></td>
                <td>{datos['cantidad']}</td>
                <td>{datos['engagement_promedio']:.1f}</td>
                <td>{datos['engagement_rate_promedio']:.2f}%</td>
                <td>{datos['publicaciones_virales']}</td>
            </tr>
"""
        
        html += f"""
        </table>
        <p><strong>Tendencia:</strong> {reporte['tendencias_temporales']['direccion'].capitalize()} 
        ({reporte['tendencias_temporales']['cambio_porcentual']:+.1f}%)</p>
        
        <h2>🔤 Palabras Clave Más Efectivas</h2>
        <table>
            <tr>
                <th>Palabra</th>
                <th>Veces Usada</th>
                <th>Engagement Score</th>
                <th>Impacto Total</th>
            </tr>
"""
        
        for palabra_data in reporte['palabras_clave_efectivas'][:10]:
            html += f"""
            <tr>
                <td><strong>{palabra_data['palabra']}</strong></td>
                <td>{palabra_data['veces_usada']}</td>
                <td>{palabra_data['engagement_score_promedio']:.1f}</td>
                <td>{palabra_data['impacto']:.1f}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <h2>🔥 Análisis de Contenido Viral</h2>
"""
        
        viral = reporte['contenido_viral']
        if viral['cantidad'] > 0:
            html += f"""
        <div class="summary-box">
            <p><strong>Publicaciones Virales:</strong> {viral['cantidad']} ({viral['porcentaje']:.1f}%)</p>
            <p><strong>Engagement Rate Promedio:</strong> {viral['engagement_rate_promedio']:.2f}%</p>
            <p><strong>Tipo Más Viral:</strong> {', '.join([f'{k} ({v})' for k, v in viral['tipos_mas_virales'].items()])}</p>
            <p><strong>Plataforma Más Viral:</strong> {', '.join([f'{k} ({v})' for k, v in viral['plataformas_mas_virales'].items()])}</p>
        </div>
        <h3>Top 5 Publicaciones Virales:</h3>
        <table>
            <tr>
                <th>Título</th>
                <th>Tipo</th>
                <th>Plataforma</th>
                <th>Engagement Score</th>
                <th>Engagement Rate</th>
            </tr>
"""
            for pub in viral['publicaciones']:
                html += f"""
            <tr>
                <td>{pub['titulo']}</td>
                <td>{pub['tipo']}</td>
                <td>{pub['plataforma']}</td>
                <td>{pub['engagement_score']:.1f}</td>
                <td>{pub['engagement_rate']:.2f}%</td>
            </tr>
"""
            html += """
        </table>
"""
        else:
            html += "<p>No se detectó contenido viral en este período.</p>"
        
        html += """
        <h2>📊 Benchmarking</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Tu Valor</th>
                <th>Benchmark Excelente</th>
                <th>Clasificación</th>
                <th>% del Excelente</th>
            </tr>
"""
        
        bench = reporte.get('benchmarking', {})
        if bench:
            html += f"""
            <tr>
                <td><strong>Engagement Rate</strong></td>
                <td>{bench['engagement_rate']['valor']:.2f}%</td>
                <td>{bench['engagement_rate']['benchmark_excelente']:.2f}%</td>
                <td>{bench['engagement_rate']['emoji']} {bench['engagement_rate']['clasificacion'].upper()}</td>
                <td>{bench['engagement_rate']['porcentaje_del_excelente']:.1f}%</td>
            </tr>
            <tr>
                <td><strong>Engagement Score</strong></td>
                <td>{bench['engagement_score']['valor']:.1f}</td>
                <td>{bench['engagement_score']['benchmark_excelente']:.1f}</td>
                <td>{bench['engagement_score']['emoji']} {bench['engagement_score']['clasificacion'].upper()}</td>
                <td>{bench['engagement_score']['porcentaje_del_excelente']:.1f}%</td>
            </tr>
            <tr>
                <td><strong>Contenido Viral</strong></td>
                <td>{bench['contenido_viral']['valor']:.1f}%</td>
                <td>{bench['contenido_viral']['benchmark_excelente']:.1f}%</td>
                <td>{bench['contenido_viral']['emoji']} {bench['contenido_viral']['clasificacion'].upper()}</td>
                <td>{bench['contenido_viral']['porcentaje_del_excelente']:.1f}%</td>
            </tr>
"""
        
        html += f"""
        </table>
        {f"<p><strong>Score General:</strong> {bench.get('score_general', 0):.1f}% del nivel excelente</p>" if bench else ""}
        
        <h2>🔧 Contenido que Necesita Mejoras</h2>
"""
        
        if reporte.get('contenido_mejorable'):
            html += """
        <table>
            <tr>
                <th>Título</th>
                <th>Plataforma</th>
                <th>Engagement Score</th>
                <th>Prioridad</th>
                <th>Razones</th>
            </tr>
"""
            for item in reporte['contenido_mejorable'][:10]:
                prioridad_color = '#e74c3c' if item['prioridad'] == 'ALTA' else '#f39c12'
                html += f"""
            <tr>
                <td>{item['titulo']}</td>
                <td>{item['plataforma']}</td>
                <td>{item['engagement_score']:.1f}</td>
                <td style="color: {prioridad_color};"><strong>{item['prioridad']}</strong></td>
                <td>{'; '.join(item['razones'][:2])}</td>
            </tr>
"""
            html += """
        </table>
"""
        else:
            html += "<p>¡Excelente! No se detectó contenido que necesite mejoras urgentes.</p>"
        
        html += """
        <h2>🔗 Correlaciones</h2>
"""
        
        corr = reporte.get('correlaciones', {})
        if corr.get('media'):
            html += f"""
        <div class="recommendation">
            <h4>Contenido con Media vs Sin Media</h4>
            <p><strong>Con Media:</strong> {corr['media']['con_media_promedio']:.1f} puntos</p>
            <p><strong>Sin Media:</strong> {corr['media']['sin_media_promedio']:.1f} puntos</p>
            <p><strong>Diferencia:</strong> {corr['media']['diferencia_porcentual']:+.1f}%</p>
        </div>
"""
        
        html += """
        <h2>💡 Recomendaciones</h2>
"""
        
        for i, rec in enumerate(reporte['recomendaciones'], 1):
            prioridad_class = 'high' if rec.get('prioridad') == 'Alta' else 'medium' if rec.get('prioridad') == 'Media' else 'low'
            html += f"""
        <div class="recommendation">
            <h4>{i}. {rec['titulo']} <span style="color: {'#e74c3c' if rec.get('prioridad') == 'Alta' else '#f39c12' if rec.get('prioridad') == 'Media' else '#95a5a6'}; font-size: 0.8em;">[{rec.get('prioridad', 'Normal')}]</span></h4>
            <p><strong>Descripción:</strong> {rec['descripcion']}</p>
            <p><strong>Razón:</strong> {rec['razon']}</p>
"""
            if 'formato_sugerido' in rec:
                html += f"<p><strong>Formato:</strong> {rec['formato_sugerido']}</p>"
            if 'frecuencia' in rec:
                html += f"<p><strong>Frecuencia:</strong> {rec['frecuencia']}</p>"
            if 'hashtags_sugeridos' in rec:
                html += f"<p><strong>Hashtags sugeridos:</strong> {', '.join([f'#{h}' for h in rec['hashtags_sugeridos']])}</p>"
            if 'accion' in rec:
                html += f"<p><strong>Acción:</strong> {rec['accion']}</p>"
            html += """
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def exportar_pdf(self, reporte: Dict[str, Any], output_file: str):
        """Exporta el reporte a PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib import colors
            REPORTLAB_AVAILABLE = True
        except ImportError:
            raise ImportError("reportlab es requerido para exportar a PDF. Instala con: pip install reportlab")
        
        doc = SimpleDocTemplate(output_file, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Título
        story.append(Paragraph("Reporte de Engagement de Contenido", title_style))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Resumen Ejecutivo
        story.append(Paragraph("Resumen Ejecutivo", heading_style))
        resumen = reporte['resumen_ejecutivo']
        
        resumen_data = [
            ['Métrica', 'Valor'],
            ['Tipo Ganador', resumen['nombre_tipo']],
            ['Engagement Rate', f"{resumen['engagement_rate_promedio']:.2f}%"],
            ['Engagement Score', f"{resumen['engagement_score_promedio']:.1f}"],
            ['Mejor Horario', resumen.get('mejor_horario', 'N/A')],
            ['Mejor Día', resumen.get('mejor_dia', 'N/A')],
            ['Mejor Plataforma', resumen.get('mejor_plataforma', 'N/A')],
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 3*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(resumen_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Alertas Críticas
        if reporte.get('alertas_criticas'):
            story.append(Paragraph("Alertas Críticas", heading_style))
            for alerta in reporte['alertas_criticas'][:3]:
                nivel_color = colors.red if alerta['nivel'] == 'CRÍTICO' else colors.orange if alerta['nivel'] == 'ALTA' else colors.yellow
                alerta_text = f"<b>{alerta['nivel']}:</b> {alerta['titulo']}<br/>{alerta['mensaje']}<br/><i>Acción: {alerta['accion']}</i>"
                story.append(Paragraph(alerta_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Análisis por Tipo
        story.append(Paragraph("Análisis por Tipo de Contenido", heading_style))
        tipo_data = [['Tipo', 'Nombre', 'Cantidad', 'Engagement Rate', 'Engagement Score']]
        for tipo, datos in reporte['analisis_por_tipo'].items():
            tipo_data.append([
                tipo,
                datos['nombre'],
                str(datos['cantidad_publicaciones']),
                f"{datos['engagement_rate_promedio']:.2f}%",
                f"{datos['engagement_score_promedio']:.1f}"
            ])
        
        tipo_table = Table(tipo_data, colWidths=[0.8*inch, 2*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        tipo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(tipo_table)
        story.append(PageBreak())
        
        # Recomendaciones
        story.append(Paragraph("Recomendaciones", heading_style))
        for i, rec in enumerate(reporte['recomendaciones'][:10], 1):
            rec_text = f"<b>{i}. {rec['titulo']}</b><br/>{rec['descripcion']}<br/><i>{rec['razon']}</i>"
            story.append(Paragraph(rec_text, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        # Generar PDF
        doc.build(story)
    
    def exportar_excel(self, reporte: Dict[str, Any], output_file: str):
        """Exporta el reporte a Excel con múltiples hojas."""
        try:
            import pandas as pd
            PANDAS_AVAILABLE = True
        except ImportError:
            raise ImportError("pandas es requerido para exportar a Excel. Instala con: pip install pandas openpyxl")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Hoja 1: Resumen Ejecutivo
            resumen_data = {
                'Métrica': [
                    'Tipo Ganador', 'Engagement Rate', 'Engagement Score',
                    'Mejor Horario', 'Mejor Día', 'Mejor Plataforma',
                    'Tendencia', 'Contenido Viral %'
                ],
                'Valor': [
                    reporte['resumen_ejecutivo']['nombre_tipo'],
                    f"{reporte['resumen_ejecutivo']['engagement_rate_promedio']:.2f}%",
                    f"{reporte['resumen_ejecutivo']['engagement_score_promedio']:.1f}",
                    reporte['resumen_ejecutivo'].get('mejor_horario', 'N/A'),
                    reporte['resumen_ejecutivo'].get('mejor_dia', 'N/A'),
                    reporte['resumen_ejecutivo'].get('mejor_plataforma', 'N/A'),
                    reporte['resumen_ejecutivo'].get('tendencia', 'N/A'),
                    f"{reporte['resumen_ejecutivo'].get('contenido_viral_porcentaje', 0):.1f}%"
                ]
            }
            pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja 2: Publicaciones
            publicaciones_data = []
            for pub in self.publicaciones:
                publicaciones_data.append({
                    'ID': pub.id,
                    'Tipo': pub.tipo_contenido,
                    'Título': pub.titulo[:50],
                    'Plataforma': pub.plataforma,
                    'Fecha': pub.fecha_publicacion.strftime('%Y-%m-%d %H:%M'),
                    'Likes': pub.likes,
                    'Comentarios': pub.comentarios,
                    'Shares': pub.shares,
                    'Impresiones': pub.impresiones,
                    'Reach': pub.reach,
                    'Engagement Rate': f"{pub.engagement_rate:.2f}%",
                    'Engagement Score': f"{pub.engagement_score:.1f}",
                    'Hashtags': ', '.join(pub.hashtags[:5]),
                    'Tiene Media': 'Sí' if pub.tiene_media else 'No',
                    'Es Viral': 'Sí' if pub.es_viral else 'No'
                })
            pd.DataFrame(publicaciones_data).to_excel(writer, sheet_name='Publicaciones', index=False)
            
            # Hoja 3: Análisis por Tipo
            tipo_data = []
            for tipo, datos in reporte['analisis_por_tipo'].items():
                tipo_data.append({
                    'Tipo': tipo,
                    'Nombre': datos['nombre'],
                    'Cantidad': datos['cantidad_publicaciones'],
                    'Engagement Total': datos['engagement_total'],
                    'Engagement Promedio': datos['engagement_promedio'],
                    'Engagement Rate': f"{datos['engagement_rate_promedio']:.2f}%",
                    'Engagement Score': datos['engagement_score_promedio'],
                    'Likes Promedio': datos['likes_promedio'],
                    'Comentarios Promedio': datos['comentarios_promedio'],
                    'Shares Promedio': datos['shares_promedio']
                })
            pd.DataFrame(tipo_data).to_excel(writer, sheet_name='Por Tipo', index=False)
            
            # Hoja 4: Por Plataforma
            plataforma_data = []
            for plataforma, datos in reporte['analisis_por_plataforma'].items():
                plataforma_data.append({
                    'Plataforma': plataforma,
                    'Cantidad': datos['cantidad_publicaciones'],
                    'Engagement Rate': f"{datos['engagement_rate_promedio']:.2f}%",
                    'Engagement Score': datos['engagement_score_promedio'],
                    'Likes Promedio': datos['likes_promedio'],
                    'Comentarios Promedio': datos['comentarios_promedio'],
                    'Shares Promedio': datos['shares_promedio'],
                    'Impresiones Promedio': datos['impresiones_promedio']
                })
            pd.DataFrame(plataforma_data).to_excel(writer, sheet_name='Por Plataforma', index=False)
            
            # Hoja 5: Benchmarking
            if 'benchmarking' in reporte and reporte['benchmarking']:
                bench = reporte['benchmarking']
                benchmarking_data = {
                'Métrica': ['Engagement Rate', 'Engagement Score', 'Contenido Viral'],
                'Tu Valor': [
                    f"{bench['engagement_rate']['valor']:.2f}%",
                    f"{bench['engagement_score']['valor']:.1f}",
                    f"{bench['contenido_viral']['valor']:.1f}%"
                ],
                'Benchmark Excelente': [
                    f"{bench['engagement_rate']['benchmark_excelente']:.2f}%",
                    f"{bench['engagement_score']['benchmark_excelente']:.1f}",
                    f"{bench['contenido_viral']['benchmark_excelente']:.1f}%"
                ],
                'Clasificación': [
                    bench['engagement_rate']['clasificacion'],
                    bench['engagement_score']['clasificacion'],
                    bench['contenido_viral']['clasificacion']
                ],
                '% del Excelente': [
                    f"{bench['engagement_rate']['porcentaje_del_excelente']:.1f}%",
                    f"{bench['engagement_score']['porcentaje_del_excelente']:.1f}%",
                    f"{bench['contenido_viral']['porcentaje_del_excelente']:.1f}%"
                ]
                }
                pd.DataFrame(benchmarking_data).to_excel(writer, sheet_name='Benchmarking', index=False)
            
            # Hoja 6: Contenido Mejorable
            if 'contenido_mejorable' in reporte and reporte['contenido_mejorable']:
                mejorable_data = []
                for item in reporte['contenido_mejorable']:
                    mejorable_data.append({
                        'ID': item['id'],
                        'Título': item['titulo'],
                        'Tipo': item['tipo'],
                        'Plataforma': item['plataforma'],
                        'Fecha': item['fecha'],
                        'Engagement Score': item['engagement_score'],
                        'Engagement Rate': f"{item['engagement_rate']:.2f}%",
                        'Prioridad': item['prioridad'],
                        'Razones': '; '.join(item['razones']),
                        'Mejoras Sugeridas': '; '.join(item['mejoras_sugeridas'])
                    })
                pd.DataFrame(mejorable_data).to_excel(writer, sheet_name='Mejorable', index=False)
            
            # Hoja 7: Hashtags Efectivos
            hashtags_data = []
            for hashtag in reporte['hashtags_mas_efectivos']:
                hashtags_data.append({
                    'Hashtag': hashtag['hashtag'],
                    'Veces Usado': hashtag['veces_usado'],
                    'Engagement Rate': f"{hashtag['engagement_rate_promedio']:.2f}%",
                    'Engagement Score': hashtag['engagement_score_promedio']
                })
            pd.DataFrame(hashtags_data).to_excel(writer, sheet_name='Hashtags', index=False)
            
            # Hoja 8: Palabras Clave
            palabras_data = []
            for palabra in reporte['palabras_clave_efectivas']:
                palabras_data.append({
                    'Palabra': palabra['palabra'],
                    'Veces Usada': palabra['veces_usada'],
                    'Engagement Score': palabra['engagement_score_promedio'],
                    'Impacto Total': palabra['impacto']
                })
            pd.DataFrame(palabras_data).to_excel(writer, sheet_name='Palabras Clave', index=False)
    
    def get_historical_data_for_recycling(self, topic: str, hashtags: List[str], platform: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene datos históricos de engagement para usar en el script de reciclaje.
        
        Args:
            topic: Tema principal del contenido
            hashtags: Lista de hashtags del contenido
            platform: Plataforma específica (opcional)
            
        Returns:
            Diccionario con datos históricos o None si no hay datos
        """
        # Filtrar publicaciones similares
        similar_posts = []
        
        for pub in self.publicaciones:
            # Verificar si tiene hashtags similares o tema similar
            pub_hashtags_lower = [h.lower().replace('#', '') for h in pub.hashtags]
            hashtags_lower = [h.lower().replace('#', '') for h in hashtags]
            matching_hashtags = [h for h in hashtags_lower if h in pub_hashtags_lower]
            
            # Verificar plataforma si se especifica
            platform_match = True
            if platform:
                platform_match = pub.plataforma.lower() == platform.lower()
            
            # Considerar similar si tiene hashtags coincidentes o tema relacionado
            if (matching_hashtags or topic.lower() in pub.titulo.lower()) and platform_match:
                similar_posts.append(pub)
        
        if not similar_posts:
            return None
        
        # Calcular promedios de engagement
        avg_engagement_scores = [p.engagement_score for p in similar_posts]
        avg_likes = [p.likes for p in similar_posts]
        avg_comments = [p.comentarios for p in similar_posts]
        avg_shares = [p.shares for p in similar_posts]
        avg_reach = [p.reach for p in similar_posts]
        avg_impressions = [p.impresiones for p in similar_posts]
        
        # Calcular promedios
        avg_score = sum(avg_engagement_scores) / len(avg_engagement_scores) if avg_engagement_scores else 0
        avg_likes_val = sum(avg_likes) / len(avg_likes) if avg_likes else 0
        avg_comments_val = sum(avg_comments) / len(avg_comments) if avg_comments else 0
        avg_shares_val = sum(avg_shares) / len(avg_shares) if avg_shares else 0
        avg_reach_val = sum(avg_reach) / len(avg_reach) if avg_reach else 0
        
        # Calcular ratios por score
        avg_likes_per_score = avg_likes_val / max(avg_score, 1) if avg_score > 0 else 12
        avg_comments_per_score = avg_comments_val / max(avg_score, 1) if avg_score > 0 else 1.8
        avg_shares_per_score = avg_shares_val / max(avg_score, 1) if avg_score > 0 else 0.6
        avg_reach_multiplier = avg_reach_val / max(avg_likes_val, 1) if avg_likes_val > 0 else 3.5
        
        # Obtener hashtags más efectivos
        effective_hashtags = self.analizar_hashtags_efectivos(top_n=10)
        top_hashtags = [h['hashtag'] for h in effective_hashtags[:5]]
        
        return {
            'topic_avg_engagement': avg_score,
            'avg_likes_per_score': avg_likes_per_score,
            'avg_comments_per_score': avg_comments_per_score,
            'avg_shares_per_score': avg_shares_per_score,
            'avg_reach_multiplier': avg_reach_multiplier,
            'effective_hashtags': top_hashtags,
            'data_points': len(similar_posts),
            'similar_posts_count': len(similar_posts),
            'avg_impressions': sum(avg_impressions) / len(avg_impressions) if avg_impressions else 0,
            'avg_engagement_rate': sum([p.engagement_rate for p in similar_posts]) / len(similar_posts) if similar_posts else 0
        }
    
    def compare_recycled_versions(self, versions_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Compara diferentes versiones recicladas de una publicación.
        
        Args:
            versions_data: Diccionario con datos de versiones recicladas
                Ejemplo: {
                    'static_post': {'engagement_metrics': {...}, ...},
                    'short_video': {'engagement_metrics': {...}, ...},
                    'story': {'engagement_metrics': {...}, ...}
                }
        
        Returns:
            Análisis comparativo de las versiones
        """
        comparison = {
            'versions': {},
            'best_version': None,
            'recommendations': []
        }
        
        best_score = 0
        best_version_name = None
        
        for version_name, version_data in versions_data.items():
            metrics = version_data.get('engagement_metrics', {})
            score = metrics.get('engagement_score', 0)
            
            comparison['versions'][version_name] = {
                'engagement_score': score,
                'estimated_likes': metrics.get('estimated_likes', 0),
                'estimated_comments': metrics.get('estimated_comments', 0),
                'estimated_shares': metrics.get('estimated_shares', 0),
                'estimated_reach': metrics.get('estimated_reach', 0),
                'confidence': metrics.get('confidence', 'medium')
            }
            
            if score > best_score:
                best_score = score
                best_version_name = version_name
        
        comparison['best_version'] = best_version_name
        
        # Generar recomendaciones
        if best_version_name:
            version_titles = {
                'static_post': 'Post Estático',
                'short_video': 'Video Corto',
                'story': 'Historia'
            }
            comparison['recommendations'].append(
                f"La mejor versión es {version_titles.get(best_version_name, best_version_name)} "
                f"con un score de engagement de {best_score}/100"
            )
        
        # Comparar diferencias
        if len(comparison['versions']) > 1:
            scores = [v['engagement_score'] for v in comparison['versions'].values()]
            max_score = max(scores)
            min_score = min(scores)
            difference = max_score - min_score
            
            if difference > 20:
                comparison['recommendations'].append(
                    f"Hay una diferencia significativa ({difference} puntos) entre versiones. "
                    f"Considera publicar múltiples versiones en diferentes momentos."
                )
        
        return comparison
    
    def predict_engagement(self, content_type: str, platform: str, hashtags: List[str], 
                          has_media: bool = True, hour: Optional[int] = None) -> Dict[str, Any]:
        """
        Predice el engagement potencial de una publicación basado en datos históricos.
        
        Args:
            content_type: Tipo de contenido (tutorial, tip, fact, etc.)
            platform: Plataforma donde se publicará
            hashtags: Lista de hashtags a usar
            has_media: Si la publicación incluye media
            hour: Hora de publicación (0-23)
        
        Returns:
            Predicción de engagement
        """
        # Filtrar publicaciones similares
        similar = []
        for pub in self.publicaciones:
            # Verificar tipo de contenido (aproximado)
            tipo_match = False
            if content_type == 'tutorial' and pub.tipo_contenido == 'X':
                tipo_match = True
            elif content_type == 'tip' and pub.tipo_contenido == 'X':
                tipo_match = True
            elif content_type in ['fact', 'opinion'] and pub.tipo_contenido == 'Y':
                tipo_match = True
            
            # Verificar plataforma
            platform_match = pub.plataforma.lower() == platform.lower()
            
            # Verificar hashtags
            pub_hashtags_lower = [h.lower().replace('#', '') for h in pub.hashtags]
            hashtags_lower = [h.lower().replace('#', '') for h in hashtags]
            matching_hashtags = len([h for h in hashtags_lower if h in pub_hashtags_lower])
            
            # Verificar hora si se especifica
            hour_match = True
            if hour is not None:
                pub_hour = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
                hour_match = abs(pub_hour - hour) <= 2  # Ventana de 2 horas
            
            if (tipo_match or matching_hashtags > 0) and platform_match and hour_match:
                similar.append(pub)
        
        if not similar:
            # Si no hay similares, usar promedios generales
            avg_score = statistics.mean([p.engagement_score for p in self.publicaciones]) if self.publicaciones else 50
            confidence = 'low'
        else:
            # Calcular promedio de engagement de publicaciones similares
            avg_score = statistics.mean([p.engagement_score for p in similar])
            confidence = 'high' if len(similar) > 10 else 'medium' if len(similar) > 5 else 'low'
        
        # Ajustar según factores
        adjustments = {
            'has_media': 1.15 if has_media else 1.0,
            'hashtags_count': min(1.2, 1.0 + (len(hashtags) / 10) * 0.2)
        }
        
        predicted_score = avg_score * adjustments['has_media'] * adjustments['hashtags_count']
        predicted_score = min(100, max(0, predicted_score))
        
        # Estimar métricas
        estimated_likes = int(predicted_score * 12)
        estimated_comments = int(predicted_score * 1.8)
        estimated_shares = int(predicted_score * 0.6)
        estimated_reach = int(estimated_likes * 3.5)
        
        return {
            'predicted_engagement_score': round(predicted_score, 1),
            'estimated_likes': estimated_likes,
            'estimated_comments': estimated_comments,
            'estimated_shares': estimated_shares,
            'estimated_reach': estimated_reach,
            'confidence': confidence,
            'similar_posts_analyzed': len(similar),
            'factors_considered': {
                'content_type': content_type,
                'platform': platform,
                'has_media': has_media,
                'hashtags_count': len(hashtags),
                'hour': hour
            }
        }
    
    def get_optimal_posting_schedule(self, content_type: str, platform: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Genera un calendario optimizado de publicación basado en datos históricos.
        
        Args:
            content_type: Tipo de contenido
            platform: Plataforma objetivo
            days_ahead: Días hacia adelante para planificar
        
        Returns:
            Lista de slots de tiempo optimizados
        """
        # Analizar horarios y días óptimos
        horarios = self.analizar_horarios_optimos()
        dias = self.analizar_dias_semana()
        
        # Obtener mejores horarios y días
        best_hours = sorted(horarios.items(), key=lambda x: x[1]['engagement_score_promedio'], reverse=True)[:3]
        best_days = sorted(dias.items(), key=lambda x: x[1]['engagement_score_promedio'], reverse=True)[:3]
        
        schedule = []
        today = datetime.now()
        
        # Mapeo de días de la semana
        day_map = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        for day_offset in range(days_ahead):
            target_date = today + timedelta(days=day_offset)
            day_name = day_map.get(target_date.strftime('%A'), target_date.strftime('%A'))
            
            # Buscar si este día está en los mejores días
            day_score = 0
            for best_day, data in best_days:
                if best_day.lower() in day_name.lower():
                    day_score = data['engagement_score_promedio']
                    break
            
            # Para cada mejor horario
            for hour_str, hour_data in best_hours:
                hour = int(hour_str.split('-')[0].split(':')[0])
                target_datetime = target_date.replace(hour=hour, minute=0, second=0)
                
                # Predecir engagement para este slot
                prediction = self.predict_engagement(
                    content_type=content_type,
                    platform=platform,
                    hashtags=[],
                    has_media=True,
                    hour=hour
                )
                
                schedule.append({
                    'date': target_datetime.strftime('%Y-%m-%d'),
                    'day': day_name,
                    'time': f"{hour:02d}:00",
                    'datetime': target_datetime.isoformat(),
                    'predicted_score': prediction['predicted_engagement_score'],
                    'day_score': day_score,
                    'hour_score': hour_data['engagement_score_promedio'],
                    'recommendation': 'Alta' if prediction['predicted_engagement_score'] > 70 else 'Media' if prediction['predicted_engagement_score'] > 50 else 'Baja'
                })
        
        # Ordenar por score predicho
        schedule.sort(key=lambda x: x['predicted_score'], reverse=True)
        
        return schedule[:10]  # Retornar top 10 slots

    def recomendar_hashtags_por_tipo_contenido(self) -> Dict[str, Any]:
        """Recomienda hashtags optimizados por tipo de contenido basado en datos históricos"""
        recomendaciones = {}
        
        analisis_por_tipo = self.analizar_por_tipo()
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=20)
        
        for tipo, datos in analisis_por_tipo.items():
            # Filtrar hashtags usados en este tipo de contenido
            hashtags_tipo = []
            for pub in self.publicaciones:
                if pub.tipo_contenido == tipo:
                    hashtags_tipo.extend(pub.hashtags)
            
            # Contar frecuencia y engagement
            hashtag_stats = defaultdict(lambda: {'veces_usado': 0, 'engagement_scores': []})
            for pub in self.publicaciones:
                if pub.tipo_contenido == tipo:
                    for hashtag in pub.hashtags:
                        hashtag_stats[hashtag.lower()]['veces_usado'] += 1
                        hashtag_stats[hashtag.lower()]['engagement_scores'].append(pub.engagement_score)
            
            # Calcular promedios
            hashtags_historicos = []
            for hashtag, stats in hashtag_stats.items():
                if stats['veces_usado'] > 0:
                    hashtags_historicos.append({
                        'hashtag': hashtag,
                        'veces_usado': stats['veces_usado'],
                        'engagement_score_promedio': statistics.mean(stats['engagement_scores']) if stats['engagement_scores'] else 0
                    })
            
            hashtags_historicos.sort(key=lambda x: x['engagement_score_promedio'], reverse=True)
            
            # Generar hashtags nuevos basados en los efectivos
            hashtags_nuevos = []
            for h in hashtags_efectivos[:10]:
                if h['hashtag'].lower() not in [x['hashtag'].lower() for x in hashtags_historicos]:
                    hashtags_nuevos.append({
                        'hashtag': h['hashtag'],
                        'recomendado': True,
                        'uso_historico': h['veces_usado'],
                        'engagement_score_promedio': h['engagement_score_promedio']
                    })
            
            recomendaciones[tipo] = {
                'total_publicaciones': datos['cantidad_publicaciones'],
                'engagement_promedio': datos['engagement_score_promedio'],
                'hashtags_historicos_efectivos': hashtags_historicos[:5],
                'hashtags_optimizados_nuevos': hashtags_nuevos[:5]
            }
        
        return recomendaciones
    
    def analizar_hashtags_por_plataforma(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analiza hashtags más efectivos por plataforma"""
        hashtags_por_plataforma = defaultdict(lambda: defaultdict(lambda: {'veces_usado': 0, 'engagement_scores': [], 'engagement_rates': []}))
        
        for pub in self.publicaciones:
            plataforma = pub.plataforma
            for hashtag in pub.hashtags:
                hashtag_lower = hashtag.lower()
                hashtags_por_plataforma[plataforma][hashtag_lower]['veces_usado'] += 1
                hashtags_por_plataforma[plataforma][hashtag_lower]['engagement_scores'].append(pub.engagement_score)
                hashtags_por_plataforma[plataforma][hashtag_lower]['engagement_rates'].append(pub.engagement_rate)
        
        resultado = {}
        for plataforma, hashtags in hashtags_por_plataforma.items():
            hashtags_list = []
            for hashtag, stats in hashtags.items():
                if stats['veces_usado'] > 0:
                    hashtags_list.append({
                        'hashtag': hashtag,
                        'veces_usado': stats['veces_usado'],
                        'engagement_score_promedio': statistics.mean(stats['engagement_scores']) if stats['engagement_scores'] else 0,
                        'engagement_rate_promedio': statistics.mean(stats['engagement_rates']) if stats['engagement_rates'] else 0
                    })
            
            hashtags_list.sort(key=lambda x: x['engagement_score_promedio'], reverse=True)
            resultado[plataforma] = hashtags_list[:10]
        
        return resultado
    
    def detectar_anomalias_engagement(self) -> List[Dict[str, Any]]:
        """Detecta publicaciones con engagement anómalo (muy alto o muy bajo)"""
        if len(self.publicaciones) < 5:
            return []
        
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        mean_score = statistics.mean(engagement_scores)
        stdev_score = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
        
        anomalias = []
        threshold = 2 * stdev_score  # 2 desviaciones estándar
        
        for pub in self.publicaciones:
            deviation = abs(pub.engagement_score - mean_score)
            if deviation > threshold:
                anomalias.append({
                    'id': pub.id,
                    'titulo': pub.titulo,
                    'plataforma': pub.plataforma,
                    'tipo': pub.tipo_contenido,
                    'engagement_score': pub.engagement_score,
                    'deviation': deviation,
                    'tipo_anomalia': 'alto' if pub.engagement_score > mean_score else 'bajo',
                    'fecha': pub.fecha_publicacion.isoformat()
                })
        
        anomalias.sort(key=lambda x: x['deviation'], reverse=True)
        return anomalias
    
    def clusterizar_contenido(self, n_clusters: int = 3) -> Dict[str, Any]:
        """Agrupa contenido similar usando clustering"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            import numpy as np
        except ImportError:
            return {'error': 'scikit-learn no está instalado. Instala con: pip install scikit-learn'}
        
        if len(self.publicaciones) < n_clusters:
            return {'error': f'Se necesitan al menos {n_clusters} publicaciones para clustering'}
        
        # Preparar características
        features = []
        for pub in self.publicaciones:
            features.append([
                pub.engagement_score,
                pub.engagement_rate,
                pub.likes,
                pub.comentarios,
                pub.shares,
                len(pub.hashtags),
                1 if pub.tiene_media else 0
            ])
        
        # Normalizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Aplicar KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Agrupar publicaciones por cluster
        clusters_data = defaultdict(list)
        for i, pub in enumerate(self.publicaciones):
            clusters_data[int(clusters[i])].append({
                'id': pub.id,
                'titulo': pub.titulo,
                'engagement_score': pub.engagement_score,
                'tipo': pub.tipo_contenido
            })
        
        # Analizar cada cluster
        resultado = {}
        for cluster_id, publicaciones in clusters_data.items():
            engagement_scores = [p['engagement_score'] for p in publicaciones]
            tipos = [p['tipo'] for p in publicaciones]
            
            resultado[f'cluster_{cluster_id}'] = {
                'cantidad': len(publicaciones),
                'engagement_promedio': statistics.mean(engagement_scores),
                'tipos_comunes': dict(Counter(tipos)),
                'publicaciones': publicaciones[:5]  # Top 5
            }
        
        return resultado
    
    def generar_estrategia_optimizada(self) -> Dict[str, Any]:
        """Genera una estrategia de contenido optimizada basada en análisis"""
        mejor_tipo = self.identificar_mejor_tipo()
        horarios = self.analizar_horarios_optimos()
        dias = self.analizar_dias_semana()
        plataformas = self.analizar_por_plataforma()
        
        mejor_horario = max(horarios.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios else None
        mejor_dia = max(dias.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if dias else None
        mejor_plataforma = max(plataformas.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if plataformas else None
        
        return {
            'tipo_contenido_recomendado': mejor_tipo.get('tipo', 'X'),
            'mejor_horario': mejor_horario,
            'mejor_dia': mejor_dia,
            'mejor_plataforma': mejor_plataforma,
            'frecuencia_sugerida': '3-5 veces por semana',
            'formato_prioritario': 'Video corto' if mejor_tipo.get('datos', {}).get('porcentaje_con_media', 0) > 80 else 'Post estático',
            'hashtags_sugeridos': [h['hashtag'] for h in self.analizar_hashtags_efectivos(top_n=10)[:5]]
        }
    
    def detectar_anomalias(self, threshold_zscore: float = 2.0) -> Dict[str, Any]:
        """
        Detecta publicaciones con métricas anómalas usando análisis estadístico.
        
        Args:
            threshold_zscore: Umbral de Z-score para detectar anomalías (default: 2.0)
            
        Returns:
            Diccionario con anomalías detectadas
        """
        if len(self.publicaciones) < 3:
            return {"error": "Se necesitan al menos 3 publicaciones para detectar anomalías"}
        
        anomalias = {
            "engagement_score_alto": [],
            "engagement_score_bajo": [],
            "engagement_rate_alto": [],
            "engagement_rate_bajo": [],
            "impresiones_anomalas": [],
            "hashtags_anomalos": []
        }
        
        # Calcular estadísticas
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        impresiones = [p.impresiones for p in self.publicaciones]
        num_hashtags = [len(p.hashtags) for p in self.publicaciones]
        
        def calcular_zscore(valor, media, desv_std):
            if desv_std == 0:
                return 0
            return (valor - media) / desv_std
        
        # Detectar anomalías en engagement score
        if len(engagement_scores) > 1:
            media_score = statistics.mean(engagement_scores)
            desv_score = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
            
            for pub in self.publicaciones:
                zscore = calcular_zscore(pub.engagement_score, media_score, desv_score)
                if zscore > threshold_zscore:
                    anomalias["engagement_score_alto"].append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "score": pub.engagement_score,
                        "zscore": zscore,
                        "tipo": "Alto engagement inesperado"
                    })
                elif zscore < -threshold_zscore:
                    anomalias["engagement_score_bajo"].append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "score": pub.engagement_score,
                        "zscore": zscore,
                        "tipo": "Bajo engagement inesperado"
                    })
        
        # Detectar anomalías en engagement rate
        if len(engagement_rates) > 1:
            media_rate = statistics.mean(engagement_rates)
            desv_rate = statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0
            
            for pub in self.publicaciones:
                zscore = calcular_zscore(pub.engagement_rate, media_rate, desv_rate)
                if zscore > threshold_zscore:
                    anomalias["engagement_rate_alto"].append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "rate": pub.engagement_rate,
                        "zscore": zscore
                    })
                elif zscore < -threshold_zscore:
                    anomalias["engagement_rate_bajo"].append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "rate": pub.engagement_rate,
                        "zscore": zscore
                    })
        
        # Detectar impresiones anómalas
        if len(impresiones) > 1:
            media_imp = statistics.mean(impresiones)
            desv_imp = statistics.stdev(impresiones) if len(impresiones) > 1 else 0
            
            for pub in self.publicaciones:
                zscore = calcular_zscore(pub.impresiones, media_imp, desv_imp)
                if abs(zscore) > threshold_zscore:
                    anomalias["impresiones_anomalas"].append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "impresiones": pub.impresiones,
                        "zscore": zscore
                    })
        
        # Resumen
        total_anomalias = sum(len(v) for v in anomalias.values() if isinstance(v, list))
        
        return {
            "total_anomalias": total_anomalias,
            "anomalias": anomalias,
            "threshold_usado": threshold_zscore,
            "recomendacion": "Revisar anomalías para identificar oportunidades o problemas" if total_anomalias > 0 else "No se detectaron anomalías significativas"
        }
    
    def comparar_periodos(self, fecha_corte: datetime = None) -> Dict[str, Any]:
        """
        Compara el engagement entre dos períodos de tiempo.
        
        Args:
            fecha_corte: Fecha que divide los dos períodos (default: mitad del rango)
            
        Returns:
            Diccionario con comparación de períodos
        """
        if len(self.publicaciones) < 4:
            return {"error": "Se necesitan al menos 4 publicaciones para comparar períodos"}
        
        # Determinar fecha de corte si no se proporciona
        if fecha_corte is None:
            fechas = sorted([p.fecha_publicacion for p in self.publicaciones])
            fecha_corte = fechas[len(fechas) // 2]
        
        periodo1 = [p for p in self.publicaciones if p.fecha_publicacion < fecha_corte]
        periodo2 = [p for p in self.publicaciones if p.fecha_publicacion >= fecha_corte]
        
        if len(periodo1) == 0 or len(periodo2) == 0:
            return {"error": "No hay suficientes datos en ambos períodos"}
        
        def calcular_metricas(publicaciones):
            return {
                "cantidad": len(publicaciones),
                "engagement_score_promedio": statistics.mean([p.engagement_score for p in publicaciones]),
                "engagement_rate_promedio": statistics.mean([p.engagement_rate for p in publicaciones]),
                "engagement_total_promedio": statistics.mean([p.engagement_total for p in publicaciones]),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                "porcentaje_viral": (sum(1 for p in publicaciones if p.es_viral) / len(publicaciones)) * 100
            }
        
        metricas_p1 = calcular_metricas(periodo1)
        metricas_p2 = calcular_metricas(periodo2)
        
        # Calcular cambios porcentuales
        def cambio_porcentual(val1, val2):
            if val1 == 0:
                return 0 if val2 == 0 else float('inf')
            return ((val2 - val1) / val1) * 100
        
        cambios = {
            "engagement_score": cambio_porcentual(metricas_p1["engagement_score_promedio"], metricas_p2["engagement_score_promedio"]),
            "engagement_rate": cambio_porcentual(metricas_p1["engagement_rate_promedio"], metricas_p2["engagement_rate_promedio"]),
            "engagement_total": cambio_porcentual(metricas_p1["engagement_total_promedio"], metricas_p2["engagement_total_promedio"]),
            "porcentaje_viral": cambio_porcentual(metricas_p1["porcentaje_viral"], metricas_p2["porcentaje_viral"])
        }
        
        # Determinar tendencia general
        cambios_positivos = sum(1 for v in cambios.values() if v > 0)
        tendencia = "mejorando" if cambios_positivos >= 2 else "empeorando" if cambios_positivos == 0 else "mixta"
        
        return {
            "periodo1": {
                "fecha_inicio": min(p.fecha_publicacion for p in periodo1).isoformat(),
                "fecha_fin": max(p.fecha_publicacion for p in periodo1).isoformat(),
                "metricas": metricas_p1
            },
            "periodo2": {
                "fecha_inicio": min(p.fecha_publicacion for p in periodo2).isoformat(),
                "fecha_fin": max(p.fecha_publicacion for p in periodo2).isoformat(),
                "metricas": metricas_p2
            },
            "cambios_porcentuales": cambios,
            "tendencia": tendencia,
            "fecha_corte": fecha_corte.isoformat(),
            "insight": f"El engagement está {tendencia}. Los cambios más significativos son en engagement_score ({cambios['engagement_score']:+.1f}%)"
        }
    
    def analizar_patrones_temporales(self) -> Dict[str, Any]:
        """
        Analiza patrones temporales avanzados en el engagement.
        
        Returns:
            Diccionario con patrones temporales detectados
        """
        if len(self.publicaciones) < 7:
            return {"error": "Se necesitan al menos 7 publicaciones para analizar patrones temporales"}
        
        patrones = {
            "tendencia_semanal": {},
            "tendencia_mensual": {},
            "ciclos_detectados": [],
            "picos_y_valles": {}
        }
        
        # Análisis por día de la semana
        dias_analisis = self.analizar_dias_semana()
        mejor_dia = max(dias_analisis.items(), key=lambda x: x[1]['engagement_score_promedio']) if dias_analisis else None
        peor_dia = min(dias_analisis.items(), key=lambda x: x[1]['engagement_score_promedio']) if dias_analisis else None
        
        patrones["tendencia_semanal"] = {
            "mejor_dia": {"dia": mejor_dia[0], "score": mejor_dia[1]['engagement_score_promedio']} if mejor_dia else None,
            "peor_dia": {"dia": peor_dia[0], "score": peor_dia[1]['engagement_score_promedio']} if peor_dia else None,
            "variacion_semanal": abs(mejor_dia[1]['engagement_score_promedio'] - peor_dia[1]['engagement_score_promedio']) if mejor_dia and peor_dia else 0
        }
        
        # Análisis por hora del día
        horarios_analisis = self.analizar_horarios_optimos()
        mejor_horario = max(horarios_analisis.items(), key=lambda x: x[1]['engagement_score_promedio']) if horarios_analisis else None
        peor_horario = min(horarios_analisis.items(), key=lambda x: x[1]['engagement_score_promedio']) if horarios_analisis else None
        
        patrones["tendencia_mensual"] = {
            "mejor_horario": {"horario": mejor_horario[0], "score": mejor_horario[1]['engagement_score_promedio']} if mejor_horario else None,
            "peor_horario": {"horario": peor_horario[0], "score": peor_horario[1]['engagement_score_promedio']} if peor_horario else None
        }
        
        # Detectar picos y valles
        publicaciones_ordenadas = sorted(self.publicaciones, key=lambda p: p.fecha_publicacion)
        engagement_scores = [p.engagement_score for p in publicaciones_ordenadas]
        
        if len(engagement_scores) >= 5:
            media_score = statistics.mean(engagement_scores)
            desv_score = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
            
            picos = []
            valles = []
            
            for i in range(1, len(engagement_scores) - 1):
                if engagement_scores[i] > engagement_scores[i-1] and engagement_scores[i] > engagement_scores[i+1]:
                    if engagement_scores[i] > media_score + desv_score:
                        picos.append({
                            "fecha": publicaciones_ordenadas[i].fecha_publicacion.isoformat(),
                            "score": engagement_scores[i],
                            "titulo": publicaciones_ordenadas[i].titulo[:50]
                        })
                elif engagement_scores[i] < engagement_scores[i-1] and engagement_scores[i] < engagement_scores[i+1]:
                    if engagement_scores[i] < media_score - desv_score:
                        valles.append({
                            "fecha": publicaciones_ordenadas[i].fecha_publicacion.isoformat(),
                            "score": engagement_scores[i],
                            "titulo": publicaciones_ordenadas[i].titulo[:50]
                        })
            
            patrones["picos_y_valles"] = {
                "picos": picos[:5],  # Top 5 picos
                "valles": valles[:5],  # Top 5 valles
                "total_picos": len(picos),
                "total_valles": len(valles)
            }
        
        return patrones
    
    def generar_recomendaciones_inteligentes(self) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones inteligentes usando análisis combinado y IA.
        
        Returns:
            Lista de recomendaciones priorizadas
        """
        recomendaciones = []
        
        # Validar datos primero
        validacion = self.validar_datos()
        if not validacion["valido"]:
            recomendaciones.append({
                "prioridad": "CRÍTICA",
                "categoria": "Calidad de Datos",
                "titulo": "Corregir problemas de calidad de datos",
                "descripcion": f"Se encontraron {len(validacion['problemas'])} problemas en los datos",
                "accion": "Revisar y corregir los datos antes de continuar",
                "impacto_esperado": "Alto"
            })
        
        # Analizar anomalías
        anomalias = self.detectar_anomalias()
        if anomalias.get("total_anomalias", 0) > 0:
            if len(anomalias["anomalias"]["engagement_score_alto"]) > 0:
                mejor_anomalia = max(anomalias["anomalias"]["engagement_score_alto"], key=lambda x: x["score"])
                recomendaciones.append({
                    "prioridad": "ALTA",
                    "categoria": "Oportunidad",
                    "titulo": f"Replicar patrón de publicación exitosa: {mejor_anomalia['titulo']}",
                    "descripcion": f"Esta publicación tuvo un engagement score excepcional ({mejor_anomalia['score']:.1f})",
                    "accion": f"Analizar y replicar características de la publicación {mejor_anomalia['id']}",
                    "impacto_esperado": "Alto"
                })
        
        # Comparar períodos
        comparacion = self.comparar_periodos()
        if comparacion.get("tendencia") == "empeorando":
            recomendaciones.append({
                "prioridad": "ALTA",
                "categoria": "Tendencia",
                "titulo": "El engagement está disminuyendo",
                "descripcion": f"El engagement ha disminuido en {abs(comparacion['cambios_porcentuales']['engagement_score']):.1f}%",
                "accion": "Revisar estrategia de contenido y timing de publicaciones",
                "impacto_esperado": "Alto"
            })
        
        # Analizar patrones temporales
        patrones = self.analizar_patrones_temporales()
        if patrones.get("tendencia_semanal", {}).get("mejor_dia"):
            mejor_dia = patrones["tendencia_semanal"]["mejor_dia"]
            recomendaciones.append({
                "prioridad": "MEDIA",
                "categoria": "Optimización",
                "titulo": f"Publicar más contenido los {mejor_dia['dia']}s",
                "descripcion": f"Los {mejor_dia['dia']}s tienen el mejor engagement promedio ({mejor_dia['score']:.1f})",
                "accion": f"Programar más publicaciones para los {mejor_dia['dia']}s",
                "impacto_esperado": "Medio"
            })
        
        # Usar IA si está disponible
        if self.ai and self.ai.enabled:
            try:
                reporte_temp = self.generar_reporte()
                recomendaciones_ai = self.ai.generar_recomendaciones_contenido(reporte_temp)
                
                if recomendaciones_ai and not recomendaciones_ai.get("error"):
                    for rec in recomendaciones_ai.get("recomendaciones_estrategicas", [])[:3]:
                        recomendaciones.append({
                            "prioridad": "MEDIA",
                            "categoria": "IA",
                            "titulo": rec[:100],
                            "descripcion": rec,
                            "accion": rec,
                            "impacto_esperado": "Medio"
                        })
            except Exception as e:
                pass  # Ignorar errores de IA
        
        # Ordenar por prioridad
        prioridad_order = {"CRÍTICA": 0, "ALTA": 1, "MEDIA": 2, "BAJA": 3}
        recomendaciones.sort(key=lambda x: prioridad_order.get(x["prioridad"], 99))
        
        return recomendaciones[:10]  # Top 10 recomendaciones
    
    def obtener_estadisticas_resumidas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas resumidas rápidas del análisis.
        
        Returns:
            Diccionario con estadísticas clave
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        
        return {
            "total_publicaciones": len(self.publicaciones),
            "engagement_rate_promedio": statistics.mean(engagement_rates) if engagement_rates else 0,
            "engagement_score_promedio": statistics.mean(engagement_scores) if engagement_scores else 0,
            "mejor_publicacion": {
                "id": max(self.publicaciones, key=lambda x: x.engagement_score).id,
                "titulo": max(self.publicaciones, key=lambda x: x.engagement_score).titulo[:50],
                "engagement_score": max(engagement_scores) if engagement_scores else 0
            },
            "publicaciones_virales": sum(1 for p in self.publicaciones if p.es_viral),
            "mejor_tipo": max(
                Counter(p.tipo_contenido for p in self.publicaciones).items(),
                key=lambda x: x[1]
            )[0] if self.publicaciones else None,
            "mejor_plataforma": max(
                Counter(p.plataforma for p in self.publicaciones).items(),
                key=lambda x: x[1]
            )[0] if self.publicaciones else None
        }
    
    def filtrar_publicaciones(self, 
                             tipo_contenido: Optional[str] = None,
                             plataforma: Optional[str] = None,
                             fecha_inicio: Optional[datetime] = None,
                             fecha_fin: Optional[datetime] = None,
                             min_engagement_rate: Optional[float] = None) -> List[Publicacion]:
        """
        Filtra publicaciones según criterios especificados.
        
        Args:
            tipo_contenido: Filtrar por tipo (X, Y, Z)
            plataforma: Filtrar por plataforma
            fecha_inicio: Fecha mínima de publicación
            fecha_fin: Fecha máxima de publicación
            min_engagement_rate: Engagement rate mínimo
            
        Returns:
            Lista de publicaciones filtradas
        """
        resultado = self.publicaciones.copy()
        
        if tipo_contenido:
            resultado = [p for p in resultado if p.tipo_contenido == tipo_contenido]
        
        if plataforma:
            resultado = [p for p in resultado if p.plataforma == plataforma]
        
        if fecha_inicio:
            resultado = [p for p in resultado if p.fecha_publicacion >= fecha_inicio]
        
        if fecha_fin:
            resultado = [p for p in resultado if p.fecha_publicacion <= fecha_fin]
        
        if min_engagement_rate is not None:
            resultado = [p for p in resultado if p.engagement_rate >= min_engagement_rate]
        
        return resultado
    
    def comparar_tipos_contenido(self) -> Dict[str, Any]:
        """
        Compara el rendimiento de diferentes tipos de contenido.
            
        Returns:
            Diccionario con comparación detallada
        """
        tipos = {}
        
        for tipo in ['X', 'Y', 'Z']:
            publicaciones_tipo = [p for p in self.publicaciones if p.tipo_contenido == tipo]
            
            if publicaciones_tipo:
                engagement_rates = [p.engagement_rate for p in publicaciones_tipo]
                engagement_scores = [p.engagement_score for p in publicaciones_tipo]
                
                tipos[tipo] = {
                    "cantidad": len(publicaciones_tipo),
                    "engagement_rate_promedio": statistics.mean(engagement_rates),
                    "engagement_score_promedio": statistics.mean(engagement_scores),
                    "engagement_rate_max": max(engagement_rates) if engagement_rates else 0,
                    "engagement_score_max": max(engagement_scores) if engagement_scores else 0,
                    "publicaciones_virales": sum(1 for p in publicaciones_tipo if p.es_viral),
                    "porcentaje_viral": (sum(1 for p in publicaciones_tipo if p.es_viral) / len(publicaciones_tipo)) * 100
                }
        
        # Determinar mejor tipo
        mejor_tipo = max(
            tipos.items(),
            key=lambda x: x[1]['engagement_score_promedio']
        ) if tipos else None
        
        return {
            "tipos": tipos,
            "mejor_tipo": mejor_tipo[0] if mejor_tipo else None,
            "mejor_tipo_datos": mejor_tipo[1] if mejor_tipo else None
        }
    
    def exportar_analisis_completo(self, output_dir: str = ".", formato: str = "json") -> Dict[str, Any]:
        """
        Exporta un análisis completo con todas las métricas y análisis avanzados.
        
        Args:
            output_dir: Directorio de salida
            formato: Formato de exportación (json, html, todos)
            
        Returns:
            Diccionario con rutas de archivos generados
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"analisis_completo_{timestamp}"
        archivos_generados = {}
        
        # Generar todos los análisis
        analisis_completo = {
            "metadata": {
                "fecha_analisis": datetime.now().isoformat(),
                "total_publicaciones": len(self.publicaciones),
                "rango_fechas": {
                    "inicio": min(p.fecha_publicacion for p in self.publicaciones).isoformat() if self.publicaciones else None,
                    "fin": max(p.fecha_publicacion for p in self.publicaciones).isoformat() if self.publicaciones else None
                }
            },
            "validacion_datos": self.validar_datos(),
            "resumen_ejecutivo": self.generar_reporte().get("resumen_ejecutivo", {}),
            "analisis_por_tipo": self.generar_reporte().get("analisis_por_tipo", {}),
            "analisis_por_plataforma": self.analizar_por_plataforma(),
            "horarios_optimos": self.analizar_horarios_optimos(),
            "dias_semana": self.analizar_dias_semana(),
            "hashtags_efectivos": self.analizar_hashtags_efectivos(),
            "palabras_clave": self.analizar_palabras_clave_titulos(),
            "contenido_viral": self.detectar_contenido_viral(),
            "tendencias_temporales": self.analizar_tendencias_temporales(),
            "anomalias": self.detectar_anomalias(),
            "comparacion_periodos": self.comparar_periodos(),
            "patrones_temporales": self.analizar_patrones_temporales(),
            "correlaciones": self.analizar_correlaciones(),
            "recomendaciones_inteligentes": self.generar_recomendaciones_inteligentes()
        }
        
        # Exportar según formato
        if formato in ["json", "todos"]:
            json_file = os.path.join(output_dir, f"{base_name}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(analisis_completo, f, indent=2, ensure_ascii=False, default=str)
            archivos_generados["json"] = json_file
        
        if formato in ["html", "todos"]:
            html_file = os.path.join(output_dir, f"{base_name}.html")
            self.exportar_html(analisis_completo, html_file)
            archivos_generados["html"] = html_file
        
        return {
            "archivos": archivos_generados,
            "resumen": {
                "total_analisis": len(analisis_completo) - 1,  # Excluir metadata
                "recomendaciones": len(analisis_completo.get("recomendaciones_inteligentes", [])),
                "anomalias_detectadas": analisis_completo.get("anomalias", {}).get("total_anomalias", 0)
            }
        }
    
    def calcular_metricas_avanzadas(self) -> Dict[str, Any]:
        """
        Calcula métricas avanzadas de engagement.
        
        Returns:
            Diccionario con métricas avanzadas
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        
        # Calcular percentiles
        def calcular_percentil(valores, percentil):
            if not valores:
                return 0
            sorted_vals = sorted(valores)
            index = int(len(sorted_vals) * percentil / 100)
            return sorted_vals[min(index, len(sorted_vals) - 1)]
        
        return {
            "engagement_rate": {
                "promedio": statistics.mean(engagement_rates) if engagement_rates else 0,
                "mediana": statistics.median(engagement_rates) if engagement_rates else 0,
                "desviacion_estandar": statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0,
                "minimo": min(engagement_rates) if engagement_rates else 0,
                "maximo": max(engagement_rates) if engagement_rates else 0,
                "percentil_25": calcular_percentil(engagement_rates, 25),
                "percentil_75": calcular_percentil(engagement_rates, 75),
                "percentil_90": calcular_percentil(engagement_rates, 90)
            },
            "engagement_score": {
                "promedio": statistics.mean(engagement_scores) if engagement_scores else 0,
                "mediana": statistics.median(engagement_scores) if engagement_scores else 0,
                "desviacion_estandar": statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0,
                "minimo": min(engagement_scores) if engagement_scores else 0,
                "maximo": max(engagement_scores) if engagement_scores else 0,
                "percentil_25": calcular_percentil(engagement_scores, 25),
                "percentil_75": calcular_percentil(engagement_scores, 75),
                "percentil_90": calcular_percentil(engagement_scores, 90)
            },
            "distribucion_viral": {
                "total_virales": sum(1 for p in self.publicaciones if p.es_viral),
                "porcentaje_viral": (sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones)) * 100,
                "engagement_rate_promedio_virales": statistics.mean([p.engagement_rate for p in self.publicaciones if p.es_viral]) if any(p.es_viral for p in self.publicaciones) else 0
            },
            "coeficiente_variacion": {
                "engagement_rate": (statistics.stdev(engagement_rates) / statistics.mean(engagement_rates) * 100) if engagement_rates and statistics.mean(engagement_rates) > 0 else 0,
                "engagement_score": (statistics.stdev(engagement_scores) / statistics.mean(engagement_scores) * 100) if engagement_scores and statistics.mean(engagement_scores) > 0 else 0
            }
        }
    
    def identificar_patrones_ocultos(self) -> Dict[str, Any]:
        """
        Identifica patrones ocultos en los datos usando análisis estadístico.
            
        Returns:
            Diccionario con patrones identificados
        """
        if len(self.publicaciones) < 10:
            return {"error": "Se necesitan al menos 10 publicaciones para identificar patrones"}
        
        patrones = {
            "correlaciones_fuertes": [],
            "factores_exito": [],
            "factores_fracaso": []
        }
        
        # Analizar correlación entre número de hashtags y engagement
        hashtags_vs_engagement = [(len(p.hashtags), p.engagement_rate) for p in self.publicaciones]
        if len(hashtags_vs_engagement) > 1:
            hashtags_list = [h[0] for h in hashtags_vs_engagement]
            engagement_list = [h[1] for h in hashtags_vs_engagement]
            if statistics.stdev(hashtags_list) > 0 and statistics.stdev(engagement_list) > 0:
                try:
                    correlacion = statistics.correlation(hashtags_list, engagement_list) if hasattr(statistics, 'correlation') else 0
                    if abs(correlacion) > 0.5:
                        patrones["correlaciones_fuertes"].append({
                            "factor1": "Número de hashtags",
                            "factor2": "Engagement rate",
                            "correlacion": correlacion,
                            "interpretacion": "Positiva" if correlacion > 0 else "Negativa"
                        })
                except:
                    pass
        
        # Función auxiliar para calcular percentiles
        def calcular_percentil(valores, percentil):
            if not valores:
                return 0
            sorted_vals = sorted(valores)
            index = int(len(sorted_vals) * percentil / 100)
            return sorted_vals[min(index, len(sorted_vals) - 1)]
        
        # Identificar factores de éxito (top 20% de publicaciones)
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        threshold_exito = calcular_percentil(engagement_scores, 80)
        publicaciones_exito = [p for p in self.publicaciones if p.engagement_score >= threshold_exito]
        
        if publicaciones_exito:
            # Analizar características comunes
            hashtags_promedio_exito = statistics.mean([len(p.hashtags) for p in publicaciones_exito])
            porcentaje_con_media_exito = (sum(1 for p in publicaciones_exito if p.tiene_media) / len(publicaciones_exito)) * 100
            
            patrones["factores_exito"] = {
                "hashtags_promedio": hashtags_promedio_exito,
                "porcentaje_con_media": porcentaje_con_media_exito,
                "tipos_comunes": dict(Counter(p.tipo_contenido for p in publicaciones_exito)),
                "plataformas_comunes": dict(Counter(p.plataforma for p in publicaciones_exito))
            }
        
        # Identificar factores de fracaso (bottom 20% de publicaciones)
        threshold_fracaso = calcular_percentil(engagement_scores, 20)
        publicaciones_fracaso = [p for p in self.publicaciones if p.engagement_score <= threshold_fracaso]
        
        if publicaciones_fracaso:
            hashtags_promedio_fracaso = statistics.mean([len(p.hashtags) for p in publicaciones_fracaso])
            porcentaje_con_media_fracaso = (sum(1 for p in publicaciones_fracaso if p.tiene_media) / len(publicaciones_fracaso)) * 100
            
            patrones["factores_fracaso"] = {
                "hashtags_promedio": hashtags_promedio_fracaso,
                "porcentaje_con_media": porcentaje_con_media_fracaso,
                "tipos_comunes": dict(Counter(p.tipo_contenido for p in publicaciones_fracaso)),
                "plataformas_comunes": dict(Counter(p.plataforma for p in publicaciones_fracaso))
            }
        
        return patrones
    
    def analizar_crecimiento_engagement(self, periodo_semanas: int = 4) -> Dict[str, Any]:
        """
        Analiza el crecimiento del engagement en el tiempo.
        
        Args:
            periodo_semanas: Número de semanas hacia atrás para analizar
            
        Returns:
            Diccionario con análisis de crecimiento
        """
        if len(self.publicaciones) < periodo_semanas:
            return {"error": f"Se necesitan al menos {periodo_semanas} publicaciones para analizar crecimiento"}
        
        # Agrupar por semana
        publicaciones_por_semana = defaultdict(list)
        fecha_limite = datetime.now() - timedelta(weeks=periodo_semanas)
        
        for pub in self.publicaciones:
            if pub.fecha_publicacion >= fecha_limite:
                semana_key = pub.fecha_publicacion.isoformat()[:10]  # YYYY-MM-DD
                semana_num = (pub.fecha_publicacion - fecha_limite).days // 7
                publicaciones_por_semana[semana_num].append(pub)
        
        crecimiento_semanal = []
        engagement_anterior = None
        
        for semana in sorted(publicaciones_por_semana.keys()):
            pubs_semana = publicaciones_por_semana[semana]
            engagement_promedio = statistics.mean([p.engagement_rate for p in pubs_semana])
            engagement_score_promedio = statistics.mean([p.engagement_score for p in pubs_semana])
            
            crecimiento = None
            if engagement_anterior is not None:
                crecimiento = ((engagement_promedio - engagement_anterior) / engagement_anterior) * 100 if engagement_anterior > 0 else 0
            
            crecimiento_semanal.append({
                "semana": semana + 1,
                "engagement_rate": engagement_promedio,
                "engagement_score": engagement_score_promedio,
                "cantidad_publicaciones": len(pubs_semana),
                "crecimiento_porcentual": crecimiento
            })
            
            engagement_anterior = engagement_promedio
        
        # Calcular tendencia general
        if len(crecimiento_semanal) >= 2:
            primer_valor = crecimiento_semanal[0]['engagement_rate']
            ultimo_valor = crecimiento_semanal[-1]['engagement_rate']
            crecimiento_total = ((ultimo_valor - primer_valor) / primer_valor * 100) if primer_valor > 0 else 0
            tendencia = "creciente" if crecimiento_total > 0 else "decreciente" if crecimiento_total < 0 else "estable"
        else:
            crecimiento_total = 0
            tendencia = "insuficientes_datos"
        
        return {
            "periodo_analizado_semanas": periodo_semanas,
            "crecimiento_semanal": crecimiento_semanal,
            "crecimiento_total_porcentual": crecimiento_total,
            "tendencia": tendencia,
            "engagement_promedio_inicial": crecimiento_semanal[0]['engagement_rate'] if crecimiento_semanal else 0,
            "engagement_promedio_final": crecimiento_semanal[-1]['engagement_rate'] if crecimiento_semanal else 0
        }
    
    def predecir_engagement_futuro(self, dias_proyeccion: int = 7) -> Dict[str, Any]:
        """
        Predice el engagement esperado para los próximos días usando análisis de tendencias.
        
        Args:
            dias_proyeccion: Número de días hacia el futuro para proyectar
            
        Returns:
            Diccionario con predicciones
        """
        if len(self.publicaciones) < 7:
            return {"error": "Se necesitan al menos 7 publicaciones para hacer predicciones"}
        
        # Agrupar por día
        publicaciones_por_dia = defaultdict(list)
        for pub in sorted(self.publicaciones, key=lambda x: x.fecha_publicacion):
            dia_key = pub.fecha_publicacion.date()
            publicaciones_por_dia[dia_key].append(pub)
        
        # Calcular engagement promedio por día
        dias_ordenados = sorted(publicaciones_por_dia.keys())
        engagement_diario = []
        
        for dia in dias_ordenados[-14:]:  # Últimas 2 semanas
            pubs_dia = publicaciones_por_dia[dia]
            if pubs_dia:
                engagement_diario.append(statistics.mean([p.engagement_rate for p in pubs_dia]))
        
        if len(engagement_diario) < 3:
            return {"error": "No hay suficientes datos históricos para hacer predicciones"}
        
        # Calcular tendencia simple (promedio móvil)
        promedio_reciente = statistics.mean(engagement_diario[-7:]) if len(engagement_diario) >= 7 else statistics.mean(engagement_diario)
        promedio_anterior = statistics.mean(engagement_diario[:-7]) if len(engagement_diario) >= 14 else promedio_reciente
        
        tendencia_diaria = (promedio_reciente - promedio_anterior) / 7 if len(engagement_diario) >= 14 else 0
        
        # Proyecciones
        proyecciones = []
        engagement_base = engagement_diario[-1] if engagement_diario else promedio_reciente
        
        for dia in range(1, dias_proyeccion + 1):
            engagement_proyectado = engagement_base + (tendencia_diaria * dia)
            engagement_proyectado = max(0, engagement_proyectado)  # No puede ser negativo
            
            proyecciones.append({
                "dia": dia,
                "fecha": (datetime.now() + timedelta(days=dia)).date().isoformat(),
                "engagement_rate_proyectado": round(engagement_proyectado, 2),
                "confianza": max(50, 100 - (dia * 5))  # Confianza decrece con el tiempo
            })
        
        return {
            "engagement_actual_promedio": round(promedio_reciente, 2),
            "tendencia_diaria": round(tendencia_diaria, 4),
            "proyecciones": proyecciones,
            "metodo": "Promedio móvil con tendencia",
            "confianza_promedio": round(statistics.mean([p['confianza'] for p in proyecciones]), 1)
        }
    
    def generar_benchmark_personalizado(self) -> Dict[str, Any]:
        """
        Genera un benchmark personalizado basado en el rendimiento histórico.
        
        Returns:
            Diccionario con benchmarks personalizados
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar benchmark"}
        
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        engagement_scores = [p.engagement_score for p in self.publicaciones]
        
        # Calcular percentiles para establecer niveles
        def calcular_percentil(valores, percentil):
            if not valores:
                return 0
            sorted_vals = sorted(valores)
            index = int(len(sorted_vals) * percentil / 100)
            return sorted_vals[min(index, len(sorted_vals) - 1)]
        
        return {
            "engagement_rate": {
                "excelente": calcular_percentil(engagement_rates, 90),
                "bueno": calcular_percentil(engagement_rates, 75),
                "promedio": statistics.mean(engagement_rates) if engagement_rates else 0,
                "mejorable": calcular_percentil(engagement_rates, 25),
                "bajo": calcular_percentil(engagement_rates, 10)
            },
            "engagement_score": {
                "excelente": calcular_percentil(engagement_scores, 90),
                "bueno": calcular_percentil(engagement_scores, 75),
                "promedio": statistics.mean(engagement_scores) if engagement_scores else 0,
                "mejorable": calcular_percentil(engagement_scores, 25),
                "bajo": calcular_percentil(engagement_scores, 10)
            },
            "por_tipo_contenido": {
                tipo: {
                    "promedio": statistics.mean([p.engagement_rate for p in self.publicaciones if p.tipo_contenido == tipo]),
                    "mejor": max([p.engagement_rate for p in self.publicaciones if p.tipo_contenido == tipo], default=0),
                    "peor": min([p.engagement_rate for p in self.publicaciones if p.tipo_contenido == tipo], default=0)
                }
                for tipo in ['X', 'Y', 'Z']
                if any(p.tipo_contenido == tipo for p in self.publicaciones)
            },
            "por_plataforma": {
                plataforma: {
                    "promedio": statistics.mean([p.engagement_rate for p in self.publicaciones if p.plataforma == plataforma]),
                    "mejor": max([p.engagement_rate for p in self.publicaciones if p.plataforma == plataforma], default=0),
                    "peor": min([p.engagement_rate for p in self.publicaciones if p.plataforma == plataforma], default=0)
                }
                for plataforma in set(p.plataforma for p in self.publicaciones)
            }
        }
    
    def generar_reporte_ejecutivo(self) -> Dict[str, Any]:
        """
        Genera un reporte ejecutivo resumido con insights clave.
        
        Returns:
            Diccionario con reporte ejecutivo
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar reporte"}
        
        # Obtener métricas clave
        estadisticas = self.obtener_estadisticas_resumidas()
        comparacion_tipos = self.comparar_tipos_contenido()
        metricas_avanzadas = self.calcular_metricas_avanzadas()
        crecimiento = self.analizar_crecimiento_engagement()
        benchmark = self.generar_benchmark_personalizado()
        recomendaciones = self.generar_recomendaciones_inteligentes()[:5]  # Top 5
        
        # Generar insights clave
        insights = []
        
        if comparacion_tipos.get("mejor_tipo"):
            insights.append({
                "tipo": "Mejor Tipo de Contenido",
                "valor": comparacion_tipos["mejor_tipo"],
                "impacto": "Alto",
                "accion": f"Incrementar producción de contenido tipo {comparacion_tipos['mejor_tipo']}"
            })
        
        if crecimiento.get("tendencia") == "decreciente":
            insights.append({
                "tipo": "Tendencia de Engagement",
                "valor": f"Decreciente ({crecimiento.get('crecimiento_total_porcentual', 0):.1f}%)",
                "impacto": "Alto",
                "accion": "Revisar estrategia de contenido y timing"
            })
        
        if metricas_avanzadas.get("distribucion_viral", {}).get("porcentaje_viral", 0) < 5:
            insights.append({
                "tipo": "Contenido Viral",
                "valor": f"Solo {metricas_avanzadas['distribucion_viral']['porcentaje_viral']:.1f}% de contenido viral",
                "impacto": "Medio",
                "accion": "Analizar contenido exitoso y replicar patrones"
            })
        
        return {
            "fecha_reporte": datetime.now().isoformat(),
            "periodo_analizado": {
                "total_publicaciones": estadisticas.get("total_publicaciones", 0),
                "fecha_inicio": min(p.fecha_publicacion for p in self.publicaciones).isoformat() if self.publicaciones else None,
                "fecha_fin": max(p.fecha_publicacion for p in self.publicaciones).isoformat() if self.publicaciones else None
            },
            "metricas_clave": {
                "engagement_rate_promedio": estadisticas.get("engagement_rate_promedio", 0),
                "engagement_score_promedio": estadisticas.get("engagement_score_promedio", 0),
                "publicaciones_virales": estadisticas.get("publicaciones_virales", 0),
                "mejor_tipo": estadisticas.get("mejor_tipo"),
                "mejor_plataforma": estadisticas.get("mejor_plataforma")
            },
            "benchmark": benchmark,
            "crecimiento": crecimiento,
            "insights_clave": insights,
            "recomendaciones_prioritarias": recomendaciones,
            "resumen_ejecutivo": f"El engagement promedio es {estadisticas.get('engagement_rate_promedio', 0):.2f}%. "
                                f"El mejor tipo de contenido es {comparacion_tipos.get('mejor_tipo', 'N/A')}. "
                                f"Tendencia: {crecimiento.get('tendencia', 'N/A')}."
        }
    
    def optimizar_contenido_futuro(self, num_recomendaciones: int = 5) -> Dict[str, Any]:
        """
        Genera recomendaciones específicas para optimizar contenido futuro.
        
        Args:
            num_recomendaciones: Número de recomendaciones a generar
            
        Returns:
            Diccionario con recomendaciones de optimización
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        recomendaciones = []
        
        # Analizar mejor tipo de contenido
        comparacion_tipos = self.comparar_tipos_contenido()
        if comparacion_tipos.get("mejor_tipo"):
            mejor_tipo = comparacion_tipos["mejor_tipo"]
            mejor_tipo_datos = comparacion_tipos["mejor_tipo_datos"]
            recomendaciones.append({
                "categoria": "Tipo de Contenido",
                "recomendacion": f"Priorizar contenido tipo {mejor_tipo}",
                "razon": f"Tiene {mejor_tipo_datos.get('engagement_score_promedio', 0):.1f} de engagement score promedio",
                "impacto_esperado": "Alto",
                "accion": f"Crear más contenido tipo {mejor_tipo}"
            })
        
        # Analizar mejor plataforma
        analisis_plataforma = self.analizar_por_plataforma()
        if analisis_plataforma:
            mejor_plataforma = max(
                analisis_plataforma.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            recomendaciones.append({
                "categoria": "Plataforma",
                "recomendacion": f"Enfocarse en {mejor_plataforma[0]}",
                "razon": f"Tiene {mejor_plataforma[1].get('engagement_score_promedio', 0):.1f} de engagement score promedio",
                "impacto_esperado": "Alto",
                "accion": f"Publicar más contenido en {mejor_plataforma[0]}"
            })
        
        # Analizar mejor horario
        horarios = self.analizar_horarios_optimos()
        if horarios:
            mejor_horario = max(
                horarios.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            recomendaciones.append({
                "categoria": "Timing",
                "recomendacion": f"Publicar en horario {mejor_horario[0]}",
                "razon": f"Tiene {mejor_horario[1].get('engagement_score_promedio', 0):.1f} de engagement score promedio",
                "impacto_esperado": "Medio",
                "accion": f"Programar publicaciones para {mejor_horario[0]}"
            })
        
        # Analizar hashtags efectivos
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=5)
        if hashtags_efectivos:
            top_hashtags = [h['hashtag'] for h in hashtags_efectivos[:5]]
            recomendaciones.append({
                "categoria": "Hashtags",
                "recomendacion": f"Usar hashtags: {', '.join(top_hashtags)}",
                "razon": "Estos hashtags tienen el mejor engagement histórico",
                "impacto_esperado": "Medio",
                "accion": f"Incluir estos hashtags en futuras publicaciones"
            })
        
        # Analizar mejor día de la semana
        dias = self.analizar_dias_semana()
        if dias:
            mejor_dia = max(
                dias.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            recomendaciones.append({
                "categoria": "Día de la Semana",
                "recomendacion": f"Publicar más los {mejor_dia[0]}s",
                "razon": f"Los {mejor_dia[0]}s tienen {mejor_dia[1].get('engagement_score_promedio', 0):.1f} de engagement score promedio",
                "impacto_esperado": "Medio",
                "accion": f"Programar más publicaciones para los {mejor_dia[0]}s"
            })
        
        return {
            "total_recomendaciones": len(recomendaciones),
            "recomendaciones": recomendaciones[:num_recomendaciones],
            "fecha_generacion": datetime.now().isoformat()
        }
    
    def analizar_segmentacion_audiencia(self) -> Dict[str, Any]:
        """
        Analiza la segmentación de audiencia basada en el engagement por plataforma y tipo.
        
        Returns:
            Diccionario con análisis de segmentación
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        segmentos = {}
        
        # Segmentar por plataforma
        for plataforma in set(p.plataforma for p in self.publicaciones):
            pubs_plataforma = [p for p in self.publicaciones if p.plataforma == plataforma]
            engagement_rates = [p.engagement_rate for p in pubs_plataforma]
            
            segmentos[plataforma] = {
                "cantidad_publicaciones": len(pubs_plataforma),
                "engagement_rate_promedio": statistics.mean(engagement_rates) if engagement_rates else 0,
                "engagement_rate_max": max(engagement_rates) if engagement_rates else 0,
                "engagement_rate_min": min(engagement_rates) if engagement_rates else 0,
                "tipos_contenido": dict(Counter(p.tipo_contenido for p in pubs_plataforma)),
                "publicaciones_virales": sum(1 for p in pubs_plataforma if p.es_viral),
                "porcentaje_viral": (sum(1 for p in pubs_plataforma if p.es_viral) / len(pubs_plataforma)) * 100 if pubs_plataforma else 0
            }
        
        # Identificar mejor segmento
        mejor_segmento = max(
            segmentos.items(),
            key=lambda x: x[1]['engagement_rate_promedio']
        ) if segmentos else None
        
        return {
            "segmentos": segmentos,
            "mejor_segmento": mejor_segmento[0] if mejor_segmento else None,
            "mejor_segmento_datos": mejor_segmento[1] if mejor_segmento else None,
            "total_segmentos": len(segmentos)
        }
    
    def generar_calendario_optimizado_avanzado(self, semanas: int = 4, objetivo: str = "maximizar_engagement") -> Dict[str, Any]:
        """
        Genera un calendario optimizado avanzado basado en múltiples factores.
        
        Args:
            semanas: Número de semanas a planificar
            objetivo: Objetivo del calendario (maximizar_engagement, balancear_tipos, maximizar_viralidad)
            
        Returns:
            Diccionario con calendario optimizado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar calendario"}
        
        # Obtener mejores prácticas
        comparacion_tipos = self.comparar_tipos_contenido()
        mejor_tipo = comparacion_tipos.get("mejor_tipo")
        
        analisis_plataforma = self.analizar_por_plataforma()
        mejor_plataforma = max(
            analisis_plataforma.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if analisis_plataforma else None
        
        horarios = self.analizar_horarios_optimos()
        mejor_horario = max(
            horarios.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if horarios else None
        
        dias = self.analizar_dias_semana()
        mejor_dia = max(
            dias.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if dias else None
        
        # Generar calendario
        calendario = []
        fecha_inicio = datetime.now()
        
        # Mapeo de días
        dias_map = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3,
            'Viernes': 4, 'Sábado': 5, 'Domingo': 6
        }
        
        # Extraer hora del mejor horario
        hora_publicacion = 10  # Default
        if mejor_horario:
            hora_match = re.search(r'(\d{2}):', mejor_horario)
            if hora_match:
                hora_publicacion = int(hora_match.group(1))
        
        dia_numero = dias_map.get(mejor_dia, 0) if mejor_dia else 0
        
        for semana in range(semanas):
            # Calcular fecha del mejor día de la semana
            dias_hasta_dia = (dia_numero - fecha_inicio.weekday()) % 7
            fecha_publicacion = fecha_inicio + timedelta(days=semana * 7 + dias_hasta_dia)
            
            # Determinar tipo de contenido según objetivo
            if objetivo == "balancear_tipos":
                tipo_contenido = ['X', 'Y', 'Z'][semana % 3]
            elif objetivo == "maximizar_viralidad":
                # Analizar qué tipo tiene más contenido viral
                tipos_virales = {}
                for tipo in ['X', 'Y', 'Z']:
                    pubs_tipo = [p for p in self.publicaciones if p.tipo_contenido == tipo]
                    tipos_virales[tipo] = sum(1 for p in pubs_tipo if p.es_viral) / len(pubs_tipo) if pubs_tipo else 0
                tipo_contenido = max(tipos_virales.items(), key=lambda x: x[1])[0] if tipos_virales else mejor_tipo
            else:
                tipo_contenido = mejor_tipo or 'X'
            
            # Predecir engagement
            prediccion = self.predecir_engagement_futuro(dias_proyeccion=1)
            engagement_esperado = prediccion.get("engagement_actual_promedio", 0) if prediccion else 0
            
            calendario.append({
                "semana": semana + 1,
                "fecha": fecha_publicacion.date().isoformat(),
                "dia": mejor_dia or "Lunes",
                "hora": f"{hora_publicacion:02d}:00",
                "tipo_contenido": tipo_contenido,
                "plataforma": mejor_plataforma or "Instagram",
                "engagement_esperado": round(engagement_esperado, 2),
                "objetivo": objetivo,
                "recomendaciones": {
                    "hashtags": [h['hashtag'] for h in self.analizar_hashtags_efectivos(top_n=5)],
                    "incluir_media": True,
                    "duracion_video": 60 if tipo_contenido == 'Y' else 180
                }
            })
        
        return {
            "calendario": calendario,
            "resumen": {
                "semanas_planificadas": semanas,
                "objetivo": objetivo,
                "mejor_tipo": mejor_tipo,
                "mejor_plataforma": mejor_plataforma,
                "mejor_dia": mejor_dia,
                "mejor_horario": mejor_horario,
                "engagement_promedio_esperado": round(statistics.mean([c['engagement_esperado'] for c in calendario]), 2)
            }
        }
    
    def generar_alertas_inteligentes(self, umbrales: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Genera alertas inteligentes basadas en umbrales configurables.
        
        Args:
            umbrales: Diccionario con umbrales personalizados (opcional)
            
        Returns:
            Lista de alertas generadas
        """
        if not self.publicaciones:
            return []
        
        # Umbrales por defecto
        umbrales_default = {
            "engagement_rate_minimo": 2.0,
            "engagement_rate_excelente": 5.0,
            "decrecimiento_maximo": -10.0,
            "consistencia_minima": 70.0
        }
        
        umbrales_finales = {**umbrales_default, **(umbrales or {})}
        
        alertas = []
        
        # Alerta: Engagement rate bajo
        engagement_promedio = statistics.mean([p.engagement_rate for p in self.publicaciones])
        if engagement_promedio < umbrales_finales["engagement_rate_minimo"]:
            alertas.append({
                "tipo": "Alerta",
                "nivel": "Alta",
                "titulo": "Engagement Rate Bajo",
                "mensaje": f"El engagement rate promedio ({engagement_promedio:.2f}%) está por debajo del umbral mínimo ({umbrales_finales['engagement_rate_minimo']}%)",
                "accion": "Revisar estrategia de contenido y timing de publicaciones",
                "impacto": "Alto"
            })
        
        # Alerta: Tendencia decreciente
        crecimiento = self.analizar_crecimiento_engagement()
        if crecimiento.get("crecimiento_total_porcentual", 0) < umbrales_finales["decrecimiento_maximo"]:
            alertas.append({
                "tipo": "Alerta",
                "nivel": "Crítica",
                "titulo": "Tendencia Decreciente Significativa",
                "mensaje": f"El engagement ha disminuido {abs(crecimiento.get('crecimiento_total_porcentual', 0)):.1f}% en el período analizado",
                "accion": "Revisar urgentemente la estrategia de contenido y considerar cambios inmediatos",
                "impacto": "Crítico"
            })
        
        # Alerta: Falta de consistencia
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        if len(engagement_rates) > 1:
            desviacion = statistics.stdev(engagement_rates)
            promedio = statistics.mean(engagement_rates)
            coeficiente_variacion = (desviacion / promedio * 100) if promedio > 0 else 100
            consistencia = 100 - coeficiente_variacion
            
            if consistencia < umbrales_finales["consistencia_minima"]:
                alertas.append({
                    "tipo": "Advertencia",
                    "nivel": "Media",
                    "titulo": "Falta de Consistencia en el Contenido",
                    "mensaje": f"La consistencia del engagement es {consistencia:.1f}%, por debajo del umbral ({umbrales_finales['consistencia_minima']}%)",
                    "accion": "Estandarizar formatos y estrategias de contenido",
                    "impacto": "Medio"
                })
        
        # Alerta positiva: Excelente rendimiento
        if engagement_promedio > umbrales_finales["engagement_rate_excelente"]:
            alertas.append({
                "tipo": "Oportunidad",
                "nivel": "Baja",
                "titulo": "Excelente Rendimiento",
                "mensaje": f"El engagement rate promedio ({engagement_promedio:.2f}%) está por encima del umbral excelente ({umbrales_finales['engagement_rate_excelente']}%)",
                "accion": "Mantener la estrategia actual y considerar escalar",
                "impacto": "Bajo"
            })
        
        return alertas
    
    def exportar_resumen_ejecutivo_json(self, output_file: str = "resumen_ejecutivo.json") -> Dict[str, Any]:
        """
        Exporta un resumen ejecutivo completo en formato JSON.
        
        Args:
            output_file: Nombre del archivo de salida
            
        Returns:
            Diccionario con información del archivo generado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para exportar"}
        
        # Generar todos los análisis necesarios
        resumen = self.generar_resumen_performance()
        reporte_ejecutivo = self.generar_reporte_ejecutivo()
        optimizacion = self.optimizar_contenido_futuro()
        alertas = self.generar_alertas_inteligentes()
        
        # Consolidar todo
        resumen_completo = {
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "version": "4.0",
                "total_publicaciones": len(self.publicaciones)
            },
            "resumen_ejecutivo": reporte_ejecutivo,
            "performance": resumen,
            "optimizacion": optimizacion,
            "alertas": alertas,
            "recomendaciones_prioritarias": reporte_ejecutivo.get("recomendaciones_prioritarias", [])
        }
        
        # Exportar a JSON
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resumen_completo, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Resumen ejecutivo exportado a {output_file}")
            
            return {
                "archivo": output_file,
                "tamaño_kb": round(os.path.getsize(output_file) / 1024, 2),
                "fecha_exportacion": datetime.now().isoformat(),
                "resumen": {
                    "total_secciones": len(resumen_completo),
                    "total_alertas": len(alertas),
                    "total_recomendaciones": len(optimizacion.get("recomendaciones", []))
                }
            }
        except Exception as e:
            logger.error(f"Error al exportar resumen ejecutivo: {e}")
            return {"error": str(e)}
    
    def analizar_roi_detallado(self, costo_por_publicacion: float = 50.0, valor_por_engagement: float = 0.10) -> Dict[str, Any]:
        """
        Analiza el ROI detallado del contenido.
        
        Args:
            costo_por_publicacion: Costo estimado por publicación en USD
            valor_por_engagement: Valor estimado por punto de engagement en USD
            
        Returns:
            Diccionario con análisis de ROI detallado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar ROI"}
        
        # Calcular ROI por publicación
        roi_por_publicacion = []
        for pub in self.publicaciones:
            costo = costo_por_publicacion
            valor_generado = pub.engagement_total * valor_por_engagement
            roi = ((valor_generado - costo) / costo * 100) if costo > 0 else 0
            roi_por_publicacion.append({
                "id": pub.id,
                "titulo": pub.titulo[:50],
                "costo": costo,
                "valor_generado": round(valor_generado, 2),
                "roi_porcentual": round(roi, 2),
                "engagement_total": pub.engagement_total
            })
        
        # Calcular ROI por tipo de contenido
        roi_por_tipo = {}
        for tipo in ['X', 'Y', 'Z']:
            pubs_tipo = [p for p in self.publicaciones if p.tipo_contenido == tipo]
            if pubs_tipo:
                costo_total = len(pubs_tipo) * costo_por_publicacion
                valor_total = sum(p.engagement_total for p in pubs_tipo) * valor_por_engagement
                roi_total = ((valor_total - costo_total) / costo_total * 100) if costo_total > 0 else 0
                
                roi_por_tipo[tipo] = {
                    "cantidad_publicaciones": len(pubs_tipo),
                    "costo_total": costo_total,
                    "valor_total": round(valor_total, 2),
                    "roi_porcentual": round(roi_total, 2),
                    "roi_por_publicacion": round(roi_total / len(pubs_tipo), 2) if pubs_tipo else 0
                }
        
        # Calcular ROI total
        costo_total_general = len(self.publicaciones) * costo_por_publicacion
        valor_total_general = sum(p.engagement_total for p in self.publicaciones) * valor_por_engagement
        roi_total_general = ((valor_total_general - costo_total_general) / costo_total_general * 100) if costo_total_general > 0 else 0
        
        # Identificar mejor ROI
        mejor_roi = max(roi_por_publicacion, key=lambda x: x['roi_porcentual']) if roi_por_publicacion else None
        
        return {
            "roi_total": {
                "costo_total": costo_total_general,
                "valor_total": round(valor_total_general, 2),
                "roi_porcentual": round(roi_total_general, 2),
                "total_publicaciones": len(self.publicaciones)
            },
            "roi_por_tipo": roi_por_tipo,
            "mejor_roi_publicacion": mejor_roi,
            "roi_promedio": round(statistics.mean([r['roi_porcentual'] for r in roi_por_publicacion]), 2) if roi_por_publicacion else 0,
            "parametros": {
                "costo_por_publicacion": costo_por_publicacion,
                "valor_por_engagement": valor_por_engagement
            }
        }
    
    def analizar_tendencias_hashtags(self, dias_recientes: int = 30) -> Dict[str, Any]:
        """
        Analiza tendencias de hashtags en el tiempo.
        
        Args:
            dias_recientes: Número de días hacia atrás para analizar
            
        Returns:
            Diccionario con análisis de tendencias de hashtags
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        fecha_limite = datetime.now() - timedelta(days=dias_recientes)
        publicaciones_recientes = [p for p in self.publicaciones if p.fecha_publicacion >= fecha_limite]
        
        if not publicaciones_recientes:
            return {"error": f"No hay publicaciones en los últimos {dias_recientes} días"}
        
        # Agrupar por semana
        hashtags_por_semana = defaultdict(lambda: defaultdict(int))
        
        for pub in publicaciones_recientes:
            semana = (pub.fecha_publicacion - fecha_limite).days // 7
            for hashtag in pub.hashtags:
                hashtags_por_semana[semana][hashtag.lower()] += 1
        
        # Analizar tendencias
        tendencias = {}
        hashtags_unicos = set()
        for semana_data in hashtags_por_semana.values():
            hashtags_unicos.update(semana_data.keys())
        
        for hashtag in hashtags_unicos:
            uso_por_semana = []
            for semana in sorted(hashtags_por_semana.keys()):
                uso_por_semana.append(hashtags_por_semana[semana].get(hashtag.lower(), 0))
            
            if len(uso_por_semana) >= 2:
                # Calcular tendencia
                primer_valor = uso_por_semana[0]
                ultimo_valor = uso_por_semana[-1]
                cambio = ((ultimo_valor - primer_valor) / primer_valor * 100) if primer_valor > 0 else (100 if ultimo_valor > 0 else 0)
                
                tendencias[hashtag] = {
                    "uso_total": sum(uso_por_semana),
                    "uso_promedio": statistics.mean(uso_por_semana),
                    "tendencia": "creciente" if cambio > 10 else "decreciente" if cambio < -10 else "estable",
                    "cambio_porcentual": round(cambio, 1),
                    "uso_por_semana": uso_por_semana
                }
        
        # Identificar hashtags trending
        hashtags_crecientes = [h for h, datos in tendencias.items() if datos["tendencia"] == "creciente"]
        hashtags_decrecientes = [h for h, datos in tendencias.items() if datos["tendencia"] == "decreciente"]
        
        return {
            "periodo_analizado_dias": dias_recientes,
            "total_hashtags_unicos": len(hashtags_unicos),
            "tendencias": tendencias,
            "hashtags_crecientes": sorted(hashtags_crecientes, key=lambda x: tendencias[x]["cambio_porcentual"], reverse=True)[:10],
            "hashtags_decrecientes": sorted(hashtags_decrecientes, key=lambda x: tendencias[x]["cambio_porcentual"])[:10],
            "hashtags_mas_usados": sorted(tendencias.items(), key=lambda x: x[1]["uso_total"], reverse=True)[:10]
        }
    
    def comparar_publicaciones_similares(self, publicacion_id: str) -> Dict[str, Any]:
        """
        Compara una publicación con otras similares para identificar diferencias.
        
        Args:
            publicacion_id: ID de la publicación a comparar
            
        Returns:
            Diccionario con comparación de publicaciones similares
        """
        # Buscar publicación
        publicacion_objetivo = next((p for p in self.publicaciones if p.id == publicacion_id), None)
        
        if not publicacion_objetivo:
            return {"error": f"Publicación {publicacion_id} no encontrada"}
        
        # Buscar publicaciones similares (mismo tipo y plataforma)
        publicaciones_similares = [
            p for p in self.publicaciones
            if p.id != publicacion_id
            and p.tipo_contenido == publicacion_objetivo.tipo_contenido
            and p.plataforma == publicacion_objetivo.plataforma
        ]
        
        if not publicaciones_similares:
            return {"error": "No se encontraron publicaciones similares"}
        
        # Calcular estadísticas de publicaciones similares
        engagement_rates_similares = [p.engagement_rate for p in publicaciones_similares]
        engagement_scores_similares = [p.engagement_score for p in publicaciones_similares]
        
        # Comparar
        comparacion = {
            "publicacion_objetivo": {
                "id": publicacion_objetivo.id,
                "titulo": publicacion_objetivo.titulo,
                "engagement_rate": publicacion_objetivo.engagement_rate,
                "engagement_score": publicacion_objetivo.engagement_score,
                "hashtags": publicacion_objetivo.hashtags,
                "tiene_media": publicacion_objetivo.tiene_media
            },
            "publicaciones_similares": {
                "cantidad": len(publicaciones_similares),
                "engagement_rate_promedio": statistics.mean(engagement_rates_similares),
                "engagement_score_promedio": statistics.mean(engagement_scores_similares),
                "engagement_rate_max": max(engagement_rates_similares),
                "engagement_score_max": max(engagement_scores_similares)
            },
            "comparacion": {
                "diferencia_engagement_rate": round(publicacion_objetivo.engagement_rate - statistics.mean(engagement_rates_similares), 2),
                "diferencia_engagement_score": round(publicacion_objetivo.engagement_score - statistics.mean(engagement_scores_similares), 2),
                "percentil_engagement_rate": self._calcular_percentil_valor(publicacion_objetivo.engagement_rate, engagement_rates_similares),
                "percentil_engagement_score": self._calcular_percentil_valor(publicacion_objetivo.engagement_score, engagement_scores_similares)
            },
            "recomendaciones": []
        }
        
        # Generar recomendaciones
        if comparacion["comparacion"]["diferencia_engagement_rate"] < -1:
            comparacion["recomendaciones"].append({
                "tipo": "Mejora",
                "mensaje": "El engagement rate está por debajo del promedio de publicaciones similares",
                "accion": "Revisar hashtags, timing y formato de la publicación"
            })
        
        # Analizar hashtags comunes en publicaciones exitosas
        publicaciones_exitosas = [p for p in publicaciones_similares if p.engagement_rate > statistics.mean(engagement_rates_similares)]
        if publicaciones_exitosas:
            hashtags_exitosos = Counter()
            for p in publicaciones_exitosas:
                hashtags_exitosos.update([h.lower() for h in p.hashtags])
            
            hashtags_faltantes = [h for h, count in hashtags_exitosos.most_common(5) if h.lower() not in [ht.lower() for ht in publicacion_objetivo.hashtags]]
            
            if hashtags_faltantes:
                comparacion["recomendaciones"].append({
                    "tipo": "Optimización",
                    "mensaje": f"Hashtags exitosos que podrías usar: {', '.join(hashtags_faltantes[:3])}",
                    "accion": "Considerar incluir estos hashtags en futuras publicaciones similares"
                })
        
        return comparacion
    
    def _calcular_percentil_valor(self, valor: float, valores: List[float]) -> float:
        """Calcula el percentil de un valor en una lista de valores."""
        if not valores:
            return 0
        valores_ordenados = sorted(valores)
        posicion = sum(1 for v in valores_ordenados if v <= valor)
        return round((posicion / len(valores_ordenados)) * 100, 1)
    
    def generar_estrategia_personalizada(self, objetivos: List[str] = None) -> Dict[str, Any]:
        """
        Genera una estrategia personalizada basada en objetivos específicos.
        
        Args:
            objetivos: Lista de objetivos (ej: ["aumentar_engagement", "aumentar_viralidad", "optimizar_roi"])
            
        Returns:
            Diccionario con estrategia personalizada
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar estrategia"}
        
        objetivos_default = ["aumentar_engagement"]
        objetivos_finales = objetivos or objetivos_default
        
        estrategia = {
            "objetivos": objetivos_finales,
            "fecha_generacion": datetime.now().isoformat(),
            "recomendaciones_por_objetivo": {},
            "acciones_prioritarias": []
        }
        
        # Analizar cada objetivo
        for objetivo in objetivos_finales:
            recomendaciones = []
            
            if objetivo == "aumentar_engagement":
                mejor_tipo = self.comparar_tipos_contenido().get("mejor_tipo")
                analisis_plataforma = self.analizar_por_plataforma()
                mejor_plataforma = max(
                    analisis_plataforma.items(),
                    key=lambda x: x[1].get('engagement_score_promedio', 0)
                )[0] if analisis_plataforma else None
                
                recomendaciones.append({
                    "accion": f"Incrementar producción de contenido tipo {mejor_tipo}",
                    "razon": f"El tipo {mejor_tipo} tiene el mejor engagement promedio",
                    "impacto_esperado": "Alto"
                })
                
                if mejor_plataforma:
                    recomendaciones.append({
                        "accion": f"Enfocarse en {mejor_plataforma}",
                        "razon": f"{mejor_plataforma} tiene el mejor engagement promedio",
                        "impacto_esperado": "Alto"
                    })
            
            elif objetivo == "aumentar_viralidad":
                publicaciones_virales = [p for p in self.publicaciones if p.es_viral]
                if publicaciones_virales:
                    tipos_virales = Counter(p.tipo_contenido for p in publicaciones_virales)
                    mejor_tipo_viral = tipos_virales.most_common(1)[0][0] if tipos_virales else None
                    
            if mejor_tipo_viral:
                        recomendaciones.append({
                            "accion": f"Crear más contenido tipo {mejor_tipo_viral}",
                            "razon": f"El tipo {mejor_tipo_viral} tiene más probabilidad de volverse viral",
                            "impacto_esperado": "Alto"
                        })
            
            elif objetivo == "optimizar_roi":
                roi_analisis = self.analizar_roi_detallado()
                mejor_tipo_roi = max(
                    roi_analisis.get("roi_por_tipo", {}).items(),
                    key=lambda x: x[1].get('roi_porcentual', 0)
                )[0] if roi_analisis.get("roi_por_tipo") else None
                
                if mejor_tipo_roi:
                    recomendaciones.append({
                        "accion": f"Priorizar contenido tipo {mejor_tipo_roi}",
                        "razon": f"El tipo {mejor_tipo_roi} tiene el mejor ROI",
                        "impacto_esperado": "Alto"
                    })
            
            elif objetivo == "mejorar_consistencia":
                engagement_rates = [p.engagement_rate for p in self.publicaciones]
                if len(engagement_rates) > 1:
                    desviacion = statistics.stdev(engagement_rates)
                    recomendaciones.append({
                        "accion": "Estandarizar formatos y estrategias de contenido",
                        "razon": f"La desviación estándar del engagement es {desviacion:.2f}%",
                        "impacto_esperado": "Medio"
                    })
            
            estrategia["recomendaciones_por_objetivo"][objetivo] = recomendaciones
            estrategia["acciones_prioritarias"].extend(recomendaciones[:2])  # Top 2 por objetivo
        
        # Priorizar acciones
        estrategia["acciones_prioritarias"] = estrategia["acciones_prioritarias"][:5]  # Top 5 acciones
        
        return estrategia
    
    def analizar_correlacion_factores(self) -> Dict[str, Any]:
        """
        Analiza correlaciones entre diferentes factores y el engagement.
        
        Returns:
            Diccionario con análisis de correlaciones
        """
        if len(self.publicaciones) < 10:
            return {"error": "Se necesitan al menos 10 publicaciones para analizar correlaciones"}
        
        correlaciones = {}
        
        # Correlación: Número de hashtags vs Engagement
        hashtags_vs_engagement = [(len(p.hashtags), p.engagement_rate) for p in self.publicaciones]
        if len(hashtags_vs_engagement) > 1:
            hashtags_list = [h[0] for h in hashtags_vs_engagement]
            engagement_list = [h[1] for h in hashtags_vs_engagement]
            
            if statistics.stdev(hashtags_list) > 0 and statistics.stdev(engagement_list) > 0:
                try:
                    # Calcular correlación de Pearson simplificada
                    media_hashtags = statistics.mean(hashtags_list)
                    media_engagement = statistics.mean(engagement_list)
                    
                    numerador = sum((hashtags_list[i] - media_hashtags) * (engagement_list[i] - media_engagement) for i in range(len(hashtags_list)))
                    denom_hashtags = math.sqrt(sum((h - media_hashtags) ** 2 for h in hashtags_list))
                    denom_engagement = math.sqrt(sum((e - media_engagement) ** 2 for e in engagement_list))
                    
                    correlacion = numerador / (denom_hashtags * denom_engagement) if (denom_hashtags * denom_engagement) > 0 else 0
                    
                    correlaciones["hashtags_vs_engagement"] = {
                        "correlacion": round(correlacion, 3),
                        "interpretacion": "Fuerte positiva" if correlacion > 0.7 else "Moderada positiva" if correlacion > 0.3 else "Débil positiva" if correlacion > 0 else "Débil negativa" if correlacion > -0.3 else "Moderada negativa" if correlacion > -0.7 else "Fuerte negativa",
                        "significancia": "Alta" if abs(correlacion) > 0.5 else "Media" if abs(correlacion) > 0.3 else "Baja"
                    }
                except:
                    pass
        
        # Correlación: Tiene media vs Engagement
        con_media = [p.engagement_rate for p in self.publicaciones if p.tiene_media]
        sin_media = [p.engagement_rate for p in self.publicaciones if not p.tiene_media]
        
        if con_media and sin_media:
            diferencia = statistics.mean(con_media) - statistics.mean(sin_media)
            correlaciones["media_vs_engagement"] = {
                "engagement_con_media": round(statistics.mean(con_media), 2),
                "engagement_sin_media": round(statistics.mean(sin_media), 2),
                "diferencia": round(diferencia, 2),
                "impacto": "Positivo" if diferencia > 0 else "Negativo",
                "recomendacion": "Incluir media visual" if diferencia > 1 else "Evaluar necesidad de media"
            }
        
        # Correlación: Longitud de título vs Engagement
        titulos_vs_engagement = [(len(p.titulo), p.engagement_rate) for p in self.publicaciones]
        if len(titulos_vs_engagement) > 1:
            # Agrupar por rangos de longitud
            rangos = {
                "corto (<100)": [t[1] for t in titulos_vs_engagement if t[0] < 100],
                "medio (100-200)": [t[1] for t in titulos_vs_engagement if 100 <= t[0] < 200],
                "largo (>200)": [t[1] for t in titulos_vs_engagement if t[0] >= 200]
            }
            
            mejor_rango = max(
                [(rango, statistics.mean(valores)) for rango, valores in rangos.items() if valores],
                key=lambda x: x[1]
            ) if any(rangos.values()) else None
            
            correlaciones["longitud_titulo_vs_engagement"] = {
                "rangos": {rango: round(statistics.mean(valores), 2) if valores else 0 for rango, valores in rangos.items()},
                "mejor_rango": mejor_rango[0] if mejor_rango else None,
                "engagement_mejor_rango": mejor_rango[1] if mejor_rango else 0
            }
        
        return {
            "total_correlaciones": len(correlaciones),
            "correlaciones": correlaciones,
            "recomendaciones": self._generar_recomendaciones_correlaciones(correlaciones)
        }
    
    def _generar_recomendaciones_correlaciones(self, correlaciones: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en correlaciones encontradas."""
        recomendaciones = []
        
        if "hashtags_vs_engagement" in correlaciones:
            corr = correlaciones["hashtags_vs_engagement"]["correlacion"]
            if corr > 0.5:
                recomendaciones.append("Aumentar el número de hashtags puede mejorar el engagement")
            elif corr < -0.3:
                recomendaciones.append("Considerar reducir el número de hashtags")
        
        if "media_vs_engagement" in correlaciones:
            impacto = correlaciones["media_vs_engagement"]["impacto"]
            if impacto == "Positivo":
                recomendaciones.append("Incluir media visual en todas las publicaciones")
        
        if "longitud_titulo_vs_engagement" in correlaciones:
            mejor_rango = correlaciones["longitud_titulo_vs_engagement"]["mejor_rango"]
            if mejor_rango:
                recomendaciones.append(f"Optimizar títulos al rango {mejor_rango} caracteres")
        
        return recomendaciones
    
    def analizar_contenido_por_palabras_clave(self, palabras_clave: List[str]) -> Dict[str, Any]:
        """
        Analiza el rendimiento de contenido que contiene palabras clave específicas.
        
        Args:
            palabras_clave: Lista de palabras clave a buscar en títulos y contenido
            
        Returns:
            Diccionario con análisis de contenido por palabras clave
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        if not palabras_clave:
            return {"error": "Debe proporcionar al menos una palabra clave"}
        
        resultados = {}
        
        for palabra_clave in palabras_clave:
            palabra_lower = palabra_clave.lower()
            
            # Buscar publicaciones que contengan la palabra clave
            publicaciones_con_palabra = [
                p for p in self.publicaciones
                if palabra_lower in p.titulo.lower() or any(palabra_lower in str(v).lower() for v in p.metadata.values() if isinstance(v, str))
            ]
            
            if publicaciones_con_palabra:
                engagement_rates = [p.engagement_rate for p in publicaciones_con_palabra]
                engagement_scores = [p.engagement_score for p in publicaciones_con_palabra]
                
                resultados[palabra_clave] = {
                    "cantidad_publicaciones": len(publicaciones_con_palabra),
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_score_promedio": round(statistics.mean(engagement_scores), 2),
                    "engagement_rate_max": round(max(engagement_rates), 2),
                    "engagement_score_max": round(max(engagement_scores), 2),
                    "publicaciones_virales": sum(1 for p in publicaciones_con_palabra if p.es_viral),
                    "porcentaje_viral": round((sum(1 for p in publicaciones_con_palabra if p.es_viral) / len(publicaciones_con_palabra)) * 100, 2),
                    "mejores_publicaciones": sorted(
                        [{"id": p.id, "titulo": p.titulo[:50], "engagement_rate": p.engagement_rate} for p in publicaciones_con_palabra],
                        key=lambda x: x["engagement_rate"],
                        reverse=True
                    )[:5]
                }
            else:
                resultados[palabra_clave] = {
                    "cantidad_publicaciones": 0,
                    "mensaje": f"No se encontraron publicaciones con la palabra clave '{palabra_clave}'"
                }
        
        # Comparar con promedio general
        engagement_rate_general = statistics.mean([p.engagement_rate for p in self.publicaciones])
        
        return {
            "palabras_clave_analizadas": palabras_clave,
            "resultados": resultados,
            "comparacion_con_promedio": {
                "engagement_rate_promedio_general": round(engagement_rate_general, 2),
                "palabras_clave_sobre_promedio": [
                    palabra for palabra, datos in resultados.items()
                    if isinstance(datos, dict) and datos.get("engagement_rate_promedio", 0) > engagement_rate_general
                ]
            }
        }
    
    def exportar_a_csv(self, output_file: str = "analisis_engagement.csv") -> Dict[str, Any]:
        """
        Exporta los datos de análisis a formato CSV.
        
        Args:
            output_file: Nombre del archivo CSV de salida
            
        Returns:
            Diccionario con información del archivo generado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para exportar"}
        
        try:
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Encabezados
                headers = [
                    "ID", "Título", "Tipo Contenido", "Plataforma", "Fecha Publicación",
                    "Likes", "Comentarios", "Shares", "Impresiones", "Reach",
                    "Engagement Total", "Engagement Rate", "Engagement Score",
                    "Es Viral", "Tiene Media", "Hashtags", "Duración Video"
                ]
                writer.writerow(headers)
                
                # Datos
                for pub in self.publicaciones:
                    row = [
                        pub.id,
                        pub.titulo,
                        pub.tipo_contenido,
                        pub.plataforma,
                        pub.fecha_publicacion.isoformat(),
                        pub.likes,
                        pub.comentarios,
                        pub.shares,
                        pub.impresiones,
                        pub.reach,
                        pub.engagement_total,
                        round(pub.engagement_rate, 2),
                        round(pub.engagement_score, 2),
                        "Sí" if pub.es_viral else "No",
                        "Sí" if pub.tiene_media else "No",
                        ", ".join(pub.hashtags),
                        pub.duracion_video
                    ]
                    writer.writerow(row)
            
            logger.info(f"Datos exportados a CSV: {output_file}")
            
            return {
                "archivo": output_file,
                "tamaño_kb": round(os.path.getsize(output_file) / 1024, 2),
                "total_filas": len(self.publicaciones) + 1,  # +1 por encabezado
                "fecha_exportacion": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error al exportar a CSV: {e}")
            return {"error": str(e)}
    
    def analizar_series_temporales_avanzado(self, metrica: str = "engagement_rate", ventana: int = 7) -> Dict[str, Any]:
        """
        Análisis avanzado de series temporales con promedios móviles y tendencias.
        
        Args:
            metrica: Métrica a analizar (engagement_rate, engagement_score, engagement_total)
            ventana: Ventana de días para promedio móvil
            
        Returns:
            Diccionario con análisis de series temporales
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Ordenar por fecha
        publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
        
        # Extraer valores de la métrica
        valores_metricos = []
        fechas = []
        
        for pub in publicaciones_ordenadas:
            fechas.append(pub.fecha_publicacion)
            if metrica == "engagement_rate":
                valores_metricos.append(pub.engagement_rate)
            elif metrica == "engagement_score":
                valores_metricos.append(pub.engagement_score)
            elif metrica == "engagement_total":
                valores_metricos.append(pub.engagement_total)
            else:
                return {"error": f"Métrica '{metrica}' no válida"}
        
        # Calcular promedio móvil
        promedios_moviles = []
        for i in range(len(valores_metricos)):
            inicio = max(0, i - ventana + 1)
            ventana_valores = valores_metricos[inicio:i+1]
            promedios_moviles.append(statistics.mean(ventana_valores))
        
        # Calcular tendencia general
        if len(valores_metricos) >= 2:
            primer_tercio = statistics.mean(valores_metricos[:len(valores_metricos)//3])
            ultimo_tercio = statistics.mean(valores_metricos[-len(valores_metricos)//3:])
            cambio_tendencia = ((ultimo_tercio - primer_tercio) / primer_tercio * 100) if primer_tercio > 0 else 0
            
            tendencia = "creciente" if cambio_tendencia > 5 else "decreciente" if cambio_tendencia < -5 else "estable"
        else:
            tendencia = "insuficiente_datos"
            cambio_tendencia = 0
        
        # Identificar puntos de cambio significativos
        puntos_cambio = []
        for i in range(1, len(promedios_moviles)):
            cambio = promedios_moviles[i] - promedios_moviles[i-1]
            cambio_porcentual = (cambio / promedios_moviles[i-1] * 100) if promedios_moviles[i-1] > 0 else 0
            
            if abs(cambio_porcentual) > 10:  # Cambio significativo > 10%
                puntos_cambio.append({
                    "fecha": fechas[i].isoformat(),
                    "cambio_porcentual": round(cambio_porcentual, 2),
                    "valor_anterior": round(promedios_moviles[i-1], 2),
                    "valor_nuevo": round(promedios_moviles[i], 2),
                    "tipo": "aumento" if cambio_porcentual > 0 else "disminución"
                })
        
        return {
            "metrica_analizada": metrica,
            "ventana_promedio_movil": ventana,
            "total_puntos_datos": len(valores_metricos),
            "valores": valores_metricos,
            "promedios_moviles": [round(v, 2) for v in promedios_moviles],
            "fechas": [f.isoformat() for f in fechas],
            "tendencia_general": {
                "direccion": tendencia,
                "cambio_porcentual": round(cambio_tendencia, 2),
                "valor_inicial": round(valores_metricos[0], 2) if valores_metricos else 0,
                "valor_final": round(valores_metricos[-1], 2) if valores_metricos else 0
            },
            "puntos_cambio_significativos": puntos_cambio[:10],  # Top 10
            "estadisticas": {
                "promedio": round(statistics.mean(valores_metricos), 2),
                "mediana": round(statistics.median(valores_metricos), 2),
                "desviacion_estandar": round(statistics.stdev(valores_metricos), 2) if len(valores_metricos) > 1 else 0,
                "minimo": round(min(valores_metricos), 2),
                "maximo": round(max(valores_metricos), 2)
            }
        }
    
    def identificar_patrones_estacionales(self) -> Dict[str, Any]:
        """
        Identifica patrones estacionales en el engagement.
        
        Returns:
            Diccionario con análisis de patrones estacionales
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Agrupar por mes
        engagement_por_mes = defaultdict(list)
        engagement_por_dia_semana = defaultdict(list)
        engagement_por_hora = defaultdict(list)
        
        for pub in self.publicaciones:
            mes = pub.fecha_publicacion.month
            dia_semana = pub.fecha_publicacion.strftime('%A')
            hora = pub.fecha_publicacion.hour
            
            engagement_por_mes[mes].append(pub.engagement_rate)
            engagement_por_dia_semana[dia_semana].append(pub.engagement_rate)
            engagement_por_hora[hora].append(pub.engagement_rate)
        
        # Analizar por mes
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        patrones_mes = {}
        for mes, valores in engagement_por_mes.items():
            patrones_mes[meses_nombres[mes]] = {
                "promedio": round(statistics.mean(valores), 2),
                "cantidad_publicaciones": len(valores)
            }
        
        mejor_mes = max(patrones_mes.items(), key=lambda x: x[1]["promedio"]) if patrones_mes else None
        
        # Analizar por día de semana
        patrones_dia = {}
        for dia, valores in engagement_por_dia_semana.items():
            patrones_dia[dia] = {
                "promedio": round(statistics.mean(valores), 2),
                "cantidad_publicaciones": len(valores)
            }
        
        mejor_dia = max(patrones_dia.items(), key=lambda x: x[1]["promedio"]) if patrones_dia else None
        
        # Analizar por hora
        patrones_hora = {}
        for hora, valores in engagement_por_hora.items():
            patrones_hora[hora] = {
                "promedio": round(statistics.mean(valores), 2),
                "cantidad_publicaciones": len(valores)
            }
        
        mejor_hora = max(patrones_hora.items(), key=lambda x: x[1]["promedio"]) if patrones_hora else None
        
        return {
            "patrones_por_mes": patrones_mes,
            "mejor_mes": {
                "mes": mejor_mes[0] if mejor_mes else None,
                "engagement_promedio": mejor_mes[1]["promedio"] if mejor_mes else 0
            },
            "patrones_por_dia_semana": patrones_dia,
            "mejor_dia_semana": {
                "dia": mejor_dia[0] if mejor_dia else None,
                "engagement_promedio": mejor_dia[1]["promedio"] if mejor_dia else 0
            },
            "patrones_por_hora": patrones_hora,
            "mejor_hora": {
                "hora": mejor_hora[0] if mejor_hora else None,
                "engagement_promedio": mejor_hora[1]["promedio"] if mejor_hora else 0
            },
            "recomendaciones": [
                f"Publicar más contenido en {mejor_mes[0]}" if mejor_mes else "No hay suficiente datos para recomendar mes",
                f"Priorizar publicaciones los {mejor_dia[0]}s" if mejor_dia else "No hay suficiente datos para recomendar día",
                f"Publicar alrededor de las {mejor_hora[0]}:00 horas" if mejor_hora else "No hay suficiente datos para recomendar hora"
            ]
        }
    
    def generar_dashboard_resumen(self) -> Dict[str, Any]:
        """
        Genera un dashboard resumen con todas las métricas clave.
        
        Returns:
            Diccionario con dashboard completo
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar dashboard"}
        
        # Obtener todos los análisis necesarios
        estadisticas = self.obtener_estadisticas_resumidas()
        score = self.calcular_score_rendimiento()
        crecimiento = self.analizar_crecimiento_engagement()
        mejor_tipo = self.comparar_tipos_contenido().get("mejor_tipo")
        mejor_plataforma = max(
            self.analizar_por_plataforma().items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if self.analizar_por_plataforma() else None
        
        # Obtener top publicaciones
        top_publicaciones = sorted(
            self.publicaciones,
            key=lambda x: x.engagement_rate,
            reverse=True
        )[:5]
        
        dashboard = {
            "fecha_generacion": datetime.now().isoformat(),
            "resumen_ejecutivo": {
                "total_publicaciones": len(self.publicaciones),
                "score_general": score.get("score_total", 0),
                "engagement_rate_promedio": estadisticas.get("engagement_rate_promedio", 0),
                "tendencia": crecimiento.get("tendencia", "estable"),
                "crecimiento_porcentual": crecimiento.get("crecimiento_total_porcentual", 0)
            },
            "mejores_practicas": {
                "mejor_tipo_contenido": mejor_tipo,
                "mejor_plataforma": mejor_plataforma,
                "top_publicaciones": [
                    {
                        "id": p.id,
                        "titulo": p.titulo[:50],
                        "engagement_rate": round(p.engagement_rate, 2),
                        "plataforma": p.plataforma
                    }
                    for p in top_publicaciones
                ]
            },
            "metricas_clave": {
                "engagement_rate": {
                    "promedio": estadisticas.get("engagement_rate_promedio", 0),
                    "maximo": estadisticas.get("engagement_rate_maximo", 0),
                    "minimo": estadisticas.get("engagement_rate_minimo", 0)
                },
                "engagement_score": {
                    "promedio": estadisticas.get("engagement_score_promedio", 0),
                    "maximo": estadisticas.get("engagement_score_maximo", 0),
                    "minimo": estadisticas.get("engagement_score_minimo", 0)
                },
                "publicaciones_virales": sum(1 for p in self.publicaciones if p.es_viral),
                "porcentaje_viral": round((sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones)) * 100, 2)
            },
            "score_desglosado": score.get("desglose", {}),
            "alertas": self.generar_alertas_inteligentes()[:5],  # Top 5 alertas
            "recomendaciones_prioritarias": self.optimizar_contenido_futuro().get("recomendaciones", [])[:5]
        }
        
        return dashboard
    
    def analizar_contenido_viral_detallado(self) -> Dict[str, Any]:
        """
        Análisis detallado de contenido viral para identificar factores de éxito.
        
        Returns:
            Diccionario con análisis detallado de contenido viral
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        publicaciones_virales = [p for p in self.publicaciones if p.es_viral]
        
        if not publicaciones_virales:
            return {
                "mensaje": "No se encontraron publicaciones virales",
                "total_publicaciones": len(self.publicaciones),
                "publicaciones_virales": 0
            }
        
        # Analizar características comunes
        tipos_virales = Counter(p.tipo_contenido for p in publicaciones_virales)
        plataformas_virales = Counter(p.plataforma for p in publicaciones_virales)
        
        # Analizar hashtags en contenido viral
        hashtags_virales = Counter()
        for p in publicaciones_virales:
            hashtags_virales.update([h.lower() for h in p.hashtags])
        
        # Analizar timing de contenido viral
        horas_virales = [p.fecha_publicacion.hour for p in publicaciones_virales]
        dias_virales = [p.fecha_publicacion.strftime('%A') for p in publicaciones_virales]
        
        # Calcular métricas promedio de contenido viral
        engagement_rates_virales = [p.engagement_rate for p in publicaciones_virales]
        engagement_scores_virales = [p.engagement_score for p in publicaciones_virales]
        
        # Comparar con contenido no viral
        publicaciones_no_virales = [p for p in self.publicaciones if not p.es_viral]
        engagement_rates_no_virales = [p.engagement_rate for p in publicaciones_no_virales] if publicaciones_no_virales else []
        
        return {
            "resumen": {
                "total_publicaciones": len(self.publicaciones),
                "publicaciones_virales": len(publicaciones_virales),
                "porcentaje_viral": round((len(publicaciones_virales) / len(self.publicaciones)) * 100, 2)
            },
            "caracteristicas_comunes": {
                "tipo_contenido_mas_viral": tipos_virales.most_common(1)[0] if tipos_virales else None,
                "plataforma_mas_viral": plataformas_virales.most_common(1)[0] if plataformas_virales else None,
                "distribucion_por_tipo": dict(tipos_virales),
                "distribucion_por_plataforma": dict(plataformas_virales)
            },
            "hashtags_virales": {
                "top_hashtags": [{"hashtag": h, "frecuencia": c} for h, c in hashtags_virales.most_common(10)],
                "total_hashtags_unicos": len(hashtags_virales)
            },
            "timing_optimo": {
                "hora_promedio": round(statistics.mean(horas_virales), 1) if horas_virales else None,
                "hora_mas_comun": Counter(horas_virales).most_common(1)[0] if horas_virales else None,
                "dia_mas_comun": Counter(dias_virales).most_common(1)[0] if dias_virales else None,
                "distribucion_por_dia": dict(Counter(dias_virales))
            },
            "metricas_promedio": {
                "engagement_rate_promedio": round(statistics.mean(engagement_rates_virales), 2),
                "engagement_score_promedio": round(statistics.mean(engagement_scores_virales), 2),
                "engagement_rate_max": round(max(engagement_rates_virales), 2),
                "engagement_rate_min": round(min(engagement_rates_virales), 2)
            },
            "comparacion_con_no_viral": {
                "diferencia_engagement_rate": round(
                    statistics.mean(engagement_rates_virales) - statistics.mean(engagement_rates_no_virales),
                    2
                ) if engagement_rates_no_virales else 0,
                "multiplicador": round(
                    statistics.mean(engagement_rates_virales) / statistics.mean(engagement_rates_no_virales),
                    2
                ) if engagement_rates_no_virales and statistics.mean(engagement_rates_no_virales) > 0 else 0
            },
            "top_publicaciones_virales": sorted(
                [{"id": p.id, "titulo": p.titulo[:50], "engagement_rate": p.engagement_rate, "plataforma": p.plataforma} for p in publicaciones_virales],
                key=lambda x: x["engagement_rate"],
                reverse=True
            )[:5],
            "recomendaciones": [
                f"Crear más contenido tipo {tipos_virales.most_common(1)[0][0]}" if tipos_virales else "No hay suficiente datos",
                f"Enfocarse en {plataformas_virales.most_common(1)[0][0]}" if plataformas_virales else "No hay suficiente datos",
                f"Publicar alrededor de las {round(statistics.mean(horas_virales), 0):.0f}:00 horas" if horas_virales else "No hay suficiente datos",
                f"Usar hashtags: {', '.join([h for h, _ in hashtags_virales.most_common(3)])}" if hashtags_virales else "No hay suficiente datos"
            ]
        }
    
    def generar_recomendaciones_automaticas(self, num_recomendaciones: int = 10) -> Dict[str, Any]:
        """
        Genera recomendaciones automáticas basadas en todos los análisis disponibles.
        
        Args:
            num_recomendaciones: Número de recomendaciones a generar
            
        Returns:
            Diccionario con recomendaciones automáticas priorizadas
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar recomendaciones"}
        
        recomendaciones = []
        
        # Analizar mejor tipo de contenido
        comparacion_tipos = self.comparar_tipos_contenido()
        mejor_tipo = comparacion_tipos.get("mejor_tipo")
        if mejor_tipo:
            tipos_datos = comparacion_tipos.get("tipos", {}).get(mejor_tipo, {})
            recomendaciones.append({
                "prioridad": "Alta",
                "categoria": "Tipo de Contenido",
                "recomendacion": f"Incrementar producción de contenido tipo {mejor_tipo}",
                "razon": f"Tiene un engagement score promedio de {tipos_datos.get('engagement_score_promedio', 0):.1f}",
                "impacto_esperado": "Alto",
                "accion": f"Crear {int(len(self.publicaciones) * 0.4)} publicaciones tipo {mejor_tipo} en el próximo mes"
            })
        
        # Analizar mejor plataforma
        analisis_plataforma = self.analizar_por_plataforma()
        if analisis_plataforma:
            mejor_plataforma = max(
                analisis_plataforma.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            recomendaciones.append({
                "prioridad": "Alta",
                "categoria": "Plataforma",
                "recomendacion": f"Enfocarse en {mejor_plataforma[0]}",
                "razon": f"Tiene un engagement score promedio de {mejor_plataforma[1].get('engagement_score_promedio', 0):.1f}",
                "impacto_esperado": "Alto",
                "accion": f"Incrementar publicaciones en {mejor_plataforma[0]} en un 30%"
            })
        
        # Analizar mejor horario
        horarios = self.analizar_horarios_optimos()
        if horarios:
            mejor_horario = max(
                horarios.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            recomendaciones.append({
                "prioridad": "Media",
                "categoria": "Timing",
                "recomendacion": f"Publicar en horario {mejor_horario[0]}",
                "razon": f"Tiene un engagement score promedio de {mejor_horario[1].get('engagement_score_promedio', 0):.1f}",
                "impacto_esperado": "Medio",
                "accion": f"Programar el 60% de las publicaciones en horario {mejor_horario[0]}"
            })
        
        # Analizar hashtags efectivos
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=5)
        if hashtags_efectivos:
            top_hashtags = [h['hashtag'] for h in hashtags_efectivos[:3]]
            recomendaciones.append({
                "prioridad": "Media",
                "categoria": "Hashtags",
                "recomendacion": f"Usar hashtags: {', '.join(top_hashtags)}",
                "razon": f"Estos hashtags tienen engagement promedio superior",
                "impacto_esperado": "Medio",
                "accion": f"Incluir estos hashtags en todas las publicaciones futuras"
            })
        
        # Analizar contenido viral
        analisis_viral = self.analizar_contenido_viral_detallado()
        if analisis_viral.get("publicaciones_virales", 0) > 0:
            caracteristicas = analisis_viral.get("caracteristicas_comunes", {})
            tipo_viral = caracteristicas.get("tipo_contenido_mas_viral")
            if tipo_viral:
                recomendaciones.append({
                    "prioridad": "Alta",
                    "categoria": "Contenido Viral",
                    "recomendacion": f"Replicar estrategia de contenido tipo {tipo_viral[0]}",
                    "razon": f"Este tipo representa el {tipo_viral[1]}% del contenido viral",
                    "impacto_esperado": "Alto",
                    "accion": f"Analizar y replicar elementos exitosos del tipo {tipo_viral[0]}"
                })
        
        # Analizar consistencia
        engagement_rates = [p.engagement_rate for p in self.publicaciones]
        if len(engagement_rates) > 1:
            desviacion = statistics.stdev(engagement_rates)
            if desviacion > statistics.mean(engagement_rates) * 0.5:
                recomendaciones.append({
                    "prioridad": "Media",
                    "categoria": "Consistencia",
                    "recomendacion": "Mejorar consistencia del contenido",
                    "razon": f"Desviación estándar alta ({desviacion:.2f}%) indica inconsistencia",
                    "impacto_esperado": "Medio",
                    "accion": "Estandarizar formatos y estrategias de contenido"
                })
        
        # Analizar crecimiento
        crecimiento = self.analizar_crecimiento_engagement()
        if crecimiento.get("crecimiento_total_porcentual", 0) < -5:
            recomendaciones.append({
                "prioridad": "Alta",
                "categoria": "Tendencia",
                "recomendacion": "Revisar estrategia de contenido urgentemente",
                "razon": f"El engagement ha disminuido {abs(crecimiento.get('crecimiento_total_porcentual', 0)):.1f}%",
                "impacto_esperado": "Crítico",
                "accion": "Implementar cambios inmediatos en la estrategia de contenido"
            })
        
        # Ordenar por prioridad
        orden_prioridad = {"Alta": 3, "Media": 2, "Baja": 1}
        recomendaciones_ordenadas = sorted(
            recomendaciones,
            key=lambda x: (orden_prioridad.get(x["prioridad"], 0), x.get("impacto_esperado", "")),
            reverse=True
        )[:num_recomendaciones]
        
        return {
            "total_recomendaciones": len(recomendaciones_ordenadas),
            "recomendaciones": recomendaciones_ordenadas,
            "resumen_por_categoria": {
                categoria: len([r for r in recomendaciones_ordenadas if r["categoria"] == categoria])
                for categoria in set(r["categoria"] for r in recomendaciones_ordenadas)
            },
            "fecha_generacion": datetime.now().isoformat()
        }
    
    def analizar_benchmark_competencia(self, benchmarks: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Compara el rendimiento con benchmarks de la industria/competencia.
        
        Args:
            benchmarks: Diccionario con benchmarks personalizados (opcional)
            
        Returns:
            Diccionario con análisis de benchmark
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Benchmarks por defecto (valores típicos de la industria)
        benchmarks_default = {
            "engagement_rate_promedio": 3.0,
            "engagement_rate_excelente": 5.0,
            "engagement_rate_bueno": 4.0,
            "engagement_rate_promedio_instagram": 2.5,
            "engagement_rate_promedio_linkedin": 2.0,
            "engagement_rate_promedio_facebook": 1.5,
            "tasa_viralidad": 1.0  # Porcentaje de contenido viral
        }
        
        benchmarks_finales = {**benchmarks_default, **(benchmarks or {})}
        
        # Calcular métricas actuales
        engagement_rate_actual = statistics.mean([p.engagement_rate for p in self.publicaciones])
        tasa_viralidad_actual = (sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones)) * 100
        
        # Comparar por plataforma
        comparacion_plataformas = {}
        analisis_plataforma = self.analizar_por_plataforma()
        
        benchmarks_plataforma = {
            "Instagram": benchmarks_finales.get("engagement_rate_promedio_instagram", 2.5),
            "LinkedIn": benchmarks_finales.get("engagement_rate_promedio_linkedin", 2.0),
            "Facebook": benchmarks_finales.get("engagement_rate_promedio_facebook", 1.5),
            "Twitter": 1.0,
            "TikTok": 5.0,
            "YouTube": 2.0
        }
        
        for plataforma, datos in analisis_plataforma.items():
            engagement_plataforma = datos.get("engagement_rate_promedio", 0)
            benchmark_plataforma = benchmarks_plataforma.get(plataforma, benchmarks_finales["engagement_rate_promedio"])
            
            diferencia = engagement_plataforma - benchmark_plataforma
            porcentaje_diferencia = (diferencia / benchmark_plataforma * 100) if benchmark_plataforma > 0 else 0
            
            comparacion_plataformas[plataforma] = {
                "engagement_actual": round(engagement_plataforma, 2),
                "benchmark_industria": round(benchmark_plataforma, 2),
                "diferencia": round(diferencia, 2),
                "porcentaje_diferencia": round(porcentaje_diferencia, 2),
                "estado": "Sobre benchmark" if diferencia > 0 else "Bajo benchmark" if diferencia < -0.5 else "En benchmark",
                "gap": round(abs(diferencia), 2)
            }
        
        # Clasificar rendimiento general
        if engagement_rate_actual >= benchmarks_finales["engagement_rate_excelente"]:
            clasificacion = "Excelente"
        elif engagement_rate_actual >= benchmarks_finales["engagement_rate_bueno"]:
            clasificacion = "Bueno"
        elif engagement_rate_actual >= benchmarks_finales["engagement_rate_promedio"]:
            clasificacion = "Promedio"
        else:
            clasificacion = "Bajo promedio"
        
        return {
            "benchmarks_aplicados": benchmarks_finales,
            "rendimiento_general": {
                "engagement_rate_actual": round(engagement_rate_actual, 2),
                "benchmark_industria": benchmarks_finales["engagement_rate_promedio"],
                "diferencia": round(engagement_rate_actual - benchmarks_finales["engagement_rate_promedio"], 2),
                "porcentaje_diferencia": round(
                    ((engagement_rate_actual - benchmarks_finales["engagement_rate_promedio"]) / benchmarks_finales["engagement_rate_promedio"] * 100),
                    2
                ),
                "clasificacion": clasificacion,
                "gap_para_excelente": round(benchmarks_finales["engagement_rate_excelente"] - engagement_rate_actual, 2)
            },
            "comparacion_por_plataforma": comparacion_plataformas,
            "viralidad": {
                "tasa_actual": round(tasa_viralidad_actual, 2),
                "benchmark_industria": benchmarks_finales["tasa_viralidad"],
                "diferencia": round(tasa_viralidad_actual - benchmarks_finales["tasa_viralidad"], 2),
                "estado": "Sobre benchmark" if tasa_viralidad_actual > benchmarks_finales["tasa_viralidad"] else "Bajo benchmark"
            },
            "recomendaciones": self._generar_recomendaciones_benchmark(engagement_rate_actual, benchmarks_finales, comparacion_plataformas)
        }
    
    def _generar_recomendaciones_benchmark(self, engagement_actual: float, benchmarks: Dict[str, float], comparacion_plataformas: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en comparación con benchmarks."""
        recomendaciones = []
        
        gap_excelente = benchmarks["engagement_rate_excelente"] - engagement_actual
        
        if gap_excelente > 1:
            recomendaciones.append(f"Necesitas mejorar {gap_excelente:.1f}% para alcanzar nivel excelente")
        
        plataformas_bajo_benchmark = [
            p for p, datos in comparacion_plataformas.items()
            if datos["estado"] == "Bajo benchmark"
        ]
        
        if plataformas_bajo_benchmark:
            recomendaciones.append(f"Enfocarse en mejorar rendimiento en: {', '.join(plataformas_bajo_benchmark)}")
        
        plataformas_sobre_benchmark = [
            p for p, datos in comparacion_plataformas.items()
            if datos["estado"] == "Sobre benchmark"
        ]
        
        if plataformas_sobre_benchmark:
            recomendaciones.append(f"Mantener estrategia exitosa en: {', '.join(plataformas_sobre_benchmark)}")
        
        return recomendaciones
    
    def generar_reporte_completo_html(self, output_file: str = "reporte_completo.html") -> Dict[str, Any]:
        """
        Genera un reporte completo en formato HTML con visualizaciones.
        
        Args:
            output_file: Nombre del archivo HTML de salida
            
        Returns:
            Diccionario con información del archivo generado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar reporte"}
        
        try:
            # Obtener todos los análisis
            dashboard = self.generar_dashboard_resumen()
            recomendaciones = self.generar_recomendaciones_automaticas()
            benchmark = self.analizar_benchmark_competencia()
            
            # Generar HTML
            html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Completo de Engagement</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            display: inline-block;
            min-width: 200px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .recommendation {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .alert {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .badge-high {{
            background-color: #28a745;
            color: white;
        }}
        .badge-medium {{
            background-color: #ffc107;
            color: black;
        }}
        .badge-low {{
            background-color: #dc3545;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte Completo de Engagement</h1>
        <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📈 Resumen Ejecutivo</h2>
        <div class="metric-card">
            <div>Total Publicaciones</div>
            <div class="metric-value">{dashboard['resumen_ejecutivo']['total_publicaciones']}</div>
            </div>
        <div class="metric-card">
            <div>Score General</div>
            <div class="metric-value">{dashboard['resumen_ejecutivo']['score_general']:.1f}</div>
            </div>
        <div class="metric-card">
            <div>Engagement Rate Promedio</div>
            <div class="metric-value">{dashboard['resumen_ejecutivo']['engagement_rate_promedio']:.2f}%</div>
        </div>
        
        <h2>🎯 Mejores Prácticas</h2>
        <ul>
            <li><strong>Mejor Tipo de Contenido:</strong> {dashboard['mejores_practicas']['mejor_tipo_contenido']}</li>
            <li><strong>Mejor Plataforma:</strong> {dashboard['mejores_practicas']['mejor_plataforma']}</li>
        </ul>
        
        <h2>💡 Recomendaciones Prioritarias</h2>
        {''.join([f'<div class="recommendation"><strong>{r["categoria"]}:</strong> {r["recomendacion"]}<br><small>{r["razon"]}</small></div>' for r in recomendaciones['recomendaciones'][:5]])}
        
        <h2>📊 Comparación con Benchmark</h2>
        <p><strong>Clasificación:</strong> <span class="badge badge-{'high' if benchmark['rendimiento_general']['clasificacion'] == 'Excelente' else 'medium' if benchmark['rendimiento_general']['clasificacion'] == 'Bueno' else 'low'}">{benchmark['rendimiento_general']['clasificacion']}</span></p>
        <p>Engagement Rate Actual: {benchmark['rendimiento_general']['engagement_rate_actual']:.2f}%</p>
        <p>Benchmark Industria: {benchmark['rendimiento_general']['benchmark_industria']:.2f}%</p>
        
        <h2>⚠️ Alertas</h2>
        {''.join([f'<div class="alert"><strong>{a["titulo"]}:</strong> {a["mensaje"]}</div>' for a in dashboard.get('alertas', [])[:3]])}
        
        <h2>📋 Top Publicaciones</h2>
        <table>
            <tr>
                <th>Título</th>
                <th>Plataforma</th>
                <th>Engagement Rate</th>
            </tr>
            {''.join([f'<tr><td>{p["titulo"]}</td><td>{p["plataforma"]}</td><td>{p["engagement_rate"]:.2f}%</td></tr>' for p in dashboard['mejores_practicas']['top_publicaciones']])}
        </table>
    </div>
</body>
</html>
"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Reporte HTML generado: {output_file}")
            
            return {
                "archivo": output_file,
                "tamaño_kb": round(os.path.getsize(output_file) / 1024, 2),
                "fecha_exportacion": datetime.now().isoformat(),
                "secciones_incluidas": [
                    "Resumen Ejecutivo",
                    "Mejores Prácticas",
                    "Recomendaciones",
                    "Benchmark",
                    "Alertas",
                    "Top Publicaciones"
                ]
            }
        except Exception as e:
            logger.error(f"Error al generar reporte HTML: {e}")
            return {"error": str(e)}
    
    def analizar_formato_contenido(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento por formato de contenido (video, imagen, texto, carousel).
        
        Returns:
            Diccionario con análisis de formatos de contenido
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Clasificar por formato basado en duración de video y tipo
        formatos = {
            "video": [],
            "imagen": [],
            "carousel": [],
            "texto": []
        }
        
        for pub in self.publicaciones:
            if pub.duracion_video > 0:
                formatos["video"].append(pub)
            elif pub.tiene_media:
                # Intentar detectar carousel basado en metadata
                if pub.metadata.get("tipo_media") == "carousel" or len(pub.metadata.get("imagenes", [])) > 1:
                    formatos["carousel"].append(pub)
                else:
                    formatos["imagen"].append(pub)
            else:
                formatos["texto"].append(pub)
        
        analisis_formatos = {}
        
        for formato, publicaciones in formatos.items():
            if publicaciones:
                engagement_rates = [p.engagement_rate for p in publicaciones]
                engagement_scores = [p.engagement_score for p in publicaciones]
                
                analisis_formatos[formato] = {
                    "cantidad": len(publicaciones),
                    "porcentaje_total": round((len(publicaciones) / len(self.publicaciones)) * 100, 2),
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_score_promedio": round(statistics.mean(engagement_scores), 2),
                    "engagement_rate_max": round(max(engagement_rates), 2),
                    "engagement_rate_min": round(min(engagement_rates), 2),
                    "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                    "porcentaje_viral": round((sum(1 for p in publicaciones if p.es_viral) / len(publicaciones)) * 100, 2),
                    "duracion_promedio_video": round(statistics.mean([p.duracion_video for p in publicaciones if p.duracion_video > 0]), 0) if formato == "video" else 0
                }
        
        # Identificar mejor formato
        mejor_formato = max(
            [(f, datos["engagement_rate_promedio"]) for f, datos in analisis_formatos.items()],
            key=lambda x: x[1]
        ) if analisis_formatos else None
        
        return {
            "formatos": analisis_formatos,
            "mejor_formato": mejor_formato[0] if mejor_formato else None,
            "mejor_formato_engagement": mejor_formato[1] if mejor_formato else 0,
            "recomendaciones": [
                f"Incrementar producción de contenido formato {mejor_formato[0]}" if mejor_formato else "No hay suficiente datos",
                f"El formato {mejor_formato[0]} tiene {mejor_formato[1]:.2f}% de engagement rate promedio" if mejor_formato else ""
            ]
        }
    
    def optimizar_hashtags_automaticamente(self, publicacion_id: str = None) -> Dict[str, Any]:
        """
        Optimiza hashtags automáticamente basándose en análisis histórico.
        
        Args:
            publicacion_id: ID de publicación específica (opcional)
            
        Returns:
            Diccionario con recomendaciones de hashtags optimizados
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Analizar hashtags más efectivos
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=20)
        
        # Analizar hashtags por tipo de contenido
        hashtags_por_tipo = defaultdict(Counter)
        hashtags_por_plataforma = defaultdict(Counter)
        
        for pub in self.publicaciones:
            for hashtag in pub.hashtags:
                hashtags_por_tipo[pub.tipo_contenido][hashtag.lower()] += 1
                hashtags_por_plataforma[pub.plataforma][hashtag.lower()] += 1
        
        # Si se especifica una publicación, analizar específicamente
        recomendaciones_especificas = {}
        if publicacion_id:
            pub_objetivo = next((p for p in self.publicaciones if p.id == publicacion_id), None)
            if pub_objetivo:
                # Recomendar hashtags basados en tipo y plataforma
                hashtags_tipo = hashtags_por_tipo.get(pub_objetivo.tipo_contenido, Counter())
                hashtags_plataforma = hashtags_por_plataforma.get(pub_objetivo.plataforma, Counter())
                
                # Combinar y priorizar
                hashtags_combinados = Counter()
                for h, c in hashtags_tipo.items():
                    hashtags_combinados[h] += c * 2  # Peso mayor para tipo
                for h, c in hashtags_plataforma.items():
                    hashtags_combinados[h] += c
                
                # Excluir hashtags ya usados
                hashtags_usados = [h.lower() for h in pub_objetivo.hashtags]
                hashtags_recomendados = [
                    h for h, c in hashtags_combinados.most_common(15)
                    if h.lower() not in hashtags_usados
                ]
                
                recomendaciones_especificas = {
                    "publicacion_id": publicacion_id,
                    "hashtags_actuales": pub_objetivo.hashtags,
                    "hashtags_recomendados": hashtags_recomendados[:10],
                    "razon": f"Basados en éxito de contenido tipo {pub_objetivo.tipo_contenido} en {pub_objetivo.plataforma}"
                }
        
        # Generar recomendaciones generales
        hashtags_generales = [h['hashtag'] for h in hashtags_efectivos[:10]]
        
        return {
            "hashtags_mas_efectivos": hashtags_generales,
            "hashtags_por_tipo": {
                tipo: [h for h, _ in hashtags.most_common(5)]
                for tipo, hashtags in hashtags_por_tipo.items()
            },
            "hashtags_por_plataforma": {
                plataforma: [h for h, _ in hashtags.most_common(5)]
                for plataforma, hashtags in hashtags_por_plataforma.items()
            },
            "recomendaciones_especificas": recomendaciones_especificas if recomendaciones_especificas else None,
            "estrategia": {
                "numero_optimo_hashtags": 10,
                "mezcla_recomendada": "5 hashtags específicos + 3 hashtags populares + 2 hashtags de nicho",
                "rotacion": "Rotar hashtags cada 2-3 publicaciones para evitar shadowban"
            }
        }
    
    def predecir_engagement_contenido_nuevo(self, tipo_contenido: str, plataforma: str, 
                                             hora_publicacion: int = None, dia_semana: str = None,
                                             numero_hashtags: int = 10, tiene_media: bool = True) -> Dict[str, Any]:
        """
        Predice el engagement esperado para contenido nuevo antes de publicar.
        
        Args:
            tipo_contenido: Tipo de contenido (X, Y, Z)
            plataforma: Plataforma (Instagram, LinkedIn, etc.)
            hora_publicacion: Hora de publicación (0-23)
            dia_semana: Día de la semana
            numero_hashtags: Número de hashtags a usar
            tiene_media: Si incluye media visual
            
        Returns:
            Diccionario con predicción de engagement
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones históricas para predecir"}
        
        # Buscar publicaciones similares
        publicaciones_similares = [
            p for p in self.publicaciones
            if p.tipo_contenido == tipo_contenido
            and p.plataforma == plataforma
        ]
        
        if not publicaciones_similares:
            return {"error": f"No hay publicaciones históricas de tipo {tipo_contenido} en {plataforma}"}
        
        # Filtrar por hora si se proporciona
        if hora_publicacion is not None:
            publicaciones_similares = [
                p for p in publicaciones_similares
                if abs(p.fecha_publicacion.hour - hora_publicacion) <= 2
            ]
        
        # Filtrar por día si se proporciona
        if dia_semana:
            publicaciones_similares = [
                p for p in publicaciones_similares
                if p.fecha_publicacion.strftime('%A') == dia_semana
            ]
        
        if not publicaciones_similares:
            # Usar todas las similares si no hay coincidencias exactas
            publicaciones_similares = [
                p for p in self.publicaciones
                if p.tipo_contenido == tipo_contenido and p.plataforma == plataforma
            ]
        
        # Calcular predicción base
        engagement_rates = [p.engagement_rate for p in publicaciones_similares]
        engagement_base = statistics.mean(engagement_rates)
        
        # Ajustar por factores
        ajustes = {}
        
        # Ajuste por número de hashtags
        hashtags_vs_engagement = self.analizar_correlacion_factores()
        if "hashtags_vs_engagement" in hashtags_vs_engagement.get("correlaciones", {}):
            corr = hashtags_vs_engagement["correlaciones"]["hashtags_vs_engagement"]["correlacion"]
            hashtags_promedio = statistics.mean([len(p.hashtags) for p in publicaciones_similares])
            if hashtags_promedio > 0:
                ajuste_hashtags = ((numero_hashtags - hashtags_promedio) / hashtags_promedio) * corr * 0.1
                ajustes["hashtags"] = round(ajuste_hashtags, 3)
        
        # Ajuste por media
        if "media_vs_engagement" in hashtags_vs_engagement.get("correlaciones", {}):
            media_data = hashtags_vs_engagement["correlaciones"]["media_vs_engagement"]
            if tiene_media and media_data.get("impacto") == "Positivo":
                ajustes["media"] = media_data.get("diferencia", 0) * 0.01
        
        # Calcular predicción final
        prediccion_final = engagement_base + sum(ajustes.values())
        
        # Calcular confianza
        muestra = len(publicaciones_similares)
        confianza = min(95, 50 + (muestra * 2)) if muestra < 25 else 95
        
        return {
            "prediccion": {
                "engagement_rate_esperado": round(prediccion_final, 2),
                "engagement_score_esperado": round(prediccion_final * 10, 1),
                "confianza": round(confianza, 1),
                "muestra_utilizada": muestra
            },
            "factores_considerados": {
                "tipo_contenido": tipo_contenido,
                "plataforma": plataforma,
                "hora_publicacion": hora_publicacion,
                "dia_semana": dia_semana,
                "numero_hashtags": numero_hashtags,
                "tiene_media": tiene_media
            },
            "ajustes_aplicados": ajustes,
            "basado_en": {
                "engagement_rate_promedio_historico": round(engagement_base, 2),
                "publicaciones_similares": muestra
            },
            "recomendaciones": [
                f"Engagement esperado: {prediccion_final:.2f}% (confianza: {confianza:.1f}%)",
                f"Basado en {muestra} publicaciones similares",
                "Considerar ajustar hora o día si la confianza es baja"
            ]
        }
    
    def generar_resumen_mensual(self, mes: int = None, año: int = None) -> Dict[str, Any]:
        """
        Genera un resumen mensual completo de rendimiento.
        
        Args:
            mes: Mes a analizar (1-12), None para mes actual
            año: Año a analizar, None para año actual
            
        Returns:
            Diccionario con resumen mensual
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Determinar período
        ahora = datetime.now()
        mes_analizar = mes if mes else ahora.month
        año_analizar = año if año else ahora.year
        
        # Filtrar publicaciones del mes
        publicaciones_mes = [
            p for p in self.publicaciones
            if p.fecha_publicacion.month == mes_analizar
            and p.fecha_publicacion.year == año_analizar
        ]
        
        if not publicaciones_mes:
            return {
                "error": f"No hay publicaciones para {mes_analizar}/{año_analizar}",
                "periodo": f"{mes_analizar}/{año_analizar}"
            }
        
        # Calcular métricas del mes
        engagement_rates = [p.engagement_rate for p in publicaciones_mes]
        engagement_scores = [p.engagement_score for p in publicaciones_mes]
        
        # Comparar con mes anterior
        mes_anterior = mes_analizar - 1 if mes_analizar > 1 else 12
        año_anterior = año_analizar if mes_analizar > 1 else año_analizar - 1
        
        publicaciones_mes_anterior = [
            p for p in self.publicaciones
            if p.fecha_publicacion.month == mes_anterior
            and p.fecha_publicacion.year == año_anterior
        ]
        
        comparacion_mes_anterior = {}
        if publicaciones_mes_anterior:
            engagement_rate_anterior = statistics.mean([p.engagement_rate for p in publicaciones_mes_anterior])
            cambio = statistics.mean(engagement_rates) - engagement_rate_anterior
            cambio_porcentual = (cambio / engagement_rate_anterior * 100) if engagement_rate_anterior > 0 else 0
            
            comparacion_mes_anterior = {
                "engagement_rate_mes_anterior": round(engagement_rate_anterior, 2),
                "cambio": round(cambio, 2),
                "cambio_porcentual": round(cambio_porcentual, 2),
                "tendencia": "mejora" if cambio > 0 else "disminucion" if cambio < 0 else "estable"
            }
        
        # Top publicaciones del mes
        top_publicaciones = sorted(
            publicaciones_mes,
            key=lambda x: x.engagement_rate,
            reverse=True
        )[:5]
        
        meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        return {
            "periodo": {
                "mes": mes_analizar,
                "año": año_analizar,
                "nombre_mes": meses_nombres[mes_analizar - 1]
            },
            "metricas": {
                "total_publicaciones": len(publicaciones_mes),
                "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                "engagement_score_promedio": round(statistics.mean(engagement_scores), 2),
                "engagement_rate_max": round(max(engagement_rates), 2),
                "engagement_rate_min": round(min(engagement_rates), 2),
                "publicaciones_virales": sum(1 for p in publicaciones_mes if p.es_viral),
                "porcentaje_viral": round((sum(1 for p in publicaciones_mes if p.es_viral) / len(publicaciones_mes)) * 100, 2)
            },
            "distribucion": {
                "por_tipo": dict(Counter(p.tipo_contenido for p in publicaciones_mes)),
                "por_plataforma": dict(Counter(p.plataforma for p in publicaciones_mes))
            },
            "comparacion_mes_anterior": comparacion_mes_anterior,
            "top_publicaciones": [
                {
                    "id": p.id,
                    "titulo": p.titulo[:50],
                    "engagement_rate": round(p.engagement_rate, 2),
                    "plataforma": p.plataforma,
                    "fecha": p.fecha_publicacion.isoformat()
                }
                for p in top_publicaciones
            ],
            "insights": [
                f"Se publicaron {len(publicaciones_mes)} publicaciones en {meses_nombres[mes_analizar - 1]}",
                f"Engagement rate promedio: {statistics.mean(engagement_rates):.2f}%",
                f"Top plataforma: {max(Counter(p.plataforma for p in publicaciones_mes).items(), key=lambda x: x[1])[0]}" if publicaciones_mes else ""
            ]
        }
    
    def analizar_longitud_contenido(self) -> Dict[str, Any]:
        """
        Analiza el impacto de la longitud del contenido en el engagement.
            
        Returns:
            Diccionario con análisis de longitud de contenido
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Clasificar por rangos de longitud
        rangos_longitud = {
            "muy_corto": [],  # < 50 caracteres
            "corto": [],       # 50-100
            "medio": [],       # 100-200
            "largo": [],       # 200-300
            "muy_largo": []    # > 300
        }
        
        for pub in self.publicaciones:
            longitud = len(pub.titulo)
            if longitud < 50:
                rangos_longitud["muy_corto"].append(pub)
            elif longitud < 100:
                rangos_longitud["corto"].append(pub)
            elif longitud < 200:
                rangos_longitud["medio"].append(pub)
            elif longitud < 300:
                rangos_longitud["largo"].append(pub)
            else:
                rangos_longitud["muy_largo"].append(pub)
        
        analisis_rangos = {}
        
        for rango, publicaciones in rangos_longitud.items():
            if publicaciones:
                engagement_rates = [p.engagement_rate for p in publicaciones]
                engagement_scores = [p.engagement_score for p in publicaciones]
                longitudes = [len(p.titulo) for p in publicaciones]
                
                analisis_rangos[rango] = {
                    "cantidad": len(publicaciones),
                    "longitud_promedio": round(statistics.mean(longitudes), 0),
                    "longitud_min": min(longitudes),
                    "longitud_max": max(longitudes),
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_score_promedio": round(statistics.mean(engagement_scores), 2),
                    "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                    "porcentaje_viral": round((sum(1 for p in publicaciones if p.es_viral) / len(publicaciones)) * 100, 2)
                }
        
        # Identificar mejor rango
        mejor_rango = max(
            [(r, datos["engagement_rate_promedio"]) for r, datos in analisis_rangos.items()],
            key=lambda x: x[1]
        ) if analisis_rangos else None
        
        # Calcular correlación longitud vs engagement
        longitudes_vs_engagement = [(len(p.titulo), p.engagement_rate) for p in self.publicaciones]
        if len(longitudes_vs_engagement) > 1:
            longitudes_list = [l[0] for l in longitudes_vs_engagement]
            engagement_list = [l[1] for l in longitudes_vs_engagement]
            
            if statistics.stdev(longitudes_list) > 0 and statistics.stdev(engagement_list) > 0:
                try:
                    media_longitud = statistics.mean(longitudes_list)
                    media_engagement = statistics.mean(engagement_list)
                    
                    numerador = sum((longitudes_list[i] - media_longitud) * (engagement_list[i] - media_engagement) for i in range(len(longitudes_list)))
                    denom_longitud = math.sqrt(sum((l - media_longitud) ** 2 for l in longitudes_list))
                    denom_engagement = math.sqrt(sum((e - media_engagement) ** 2 for e in engagement_list))
                    
                    correlacion = numerador / (denom_longitud * denom_engagement) if (denom_longitud * denom_engagement) > 0 else 0
                except:
                    correlacion = 0
            else:
                correlacion = 0
        else:
            correlacion = 0
        
        return {
            "rangos_longitud": analisis_rangos,
            "mejor_rango": mejor_rango[0] if mejor_rango else None,
            "mejor_rango_engagement": mejor_rango[1] if mejor_rango else 0,
            "correlacion_longitud_engagement": round(correlacion, 3),
            "interpretacion_correlacion": "Positiva" if correlacion > 0.3 else "Negativa" if correlacion < -0.3 else "Neutra",
            "recomendaciones": [
                f"Optimizar longitud de contenido al rango '{mejor_rango[0]}'" if mejor_rango else "No hay suficiente datos",
                f"Longitud promedio recomendada: {analisis_rangos[mejor_rango[0]]['longitud_promedio']:.0f} caracteres" if mejor_rango and mejor_rango[0] in analisis_rangos else ""
            ]
        }
    
    def analizar_frecuencia_publicacion(self) -> Dict[str, Any]:
        """
        Analiza el impacto de la frecuencia de publicación en el engagement.
        
        Returns:
            Diccionario con análisis de frecuencia de publicación
        """
        if not self.publicaciones or len(self.publicaciones) < 2:
            return {"error": "Se necesitan al menos 2 publicaciones para analizar frecuencia"}
        
        # Ordenar por fecha
        publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
        
        # Calcular intervalos entre publicaciones
        intervalos = []
        for i in range(1, len(publicaciones_ordenadas)):
            intervalo = (publicaciones_ordenadas[i].fecha_publicacion - publicaciones_ordenadas[i-1].fecha_publicacion).total_seconds() / 3600  # En horas
            intervalos.append({
                "horas": intervalo,
                "dias": intervalo / 24,
                "engagement_rate": publicaciones_ordenadas[i].engagement_rate
            })
        
        # Clasificar por frecuencia
        frecuencia_categorias = {
            "muy_alta": [],  # < 6 horas
            "alta": [],       # 6-24 horas
            "media": [],      # 1-3 días
            "baja": [],       # 3-7 días
            "muy_baja": []    # > 7 días
        }
        
        for intervalo in intervalos:
            horas = intervalo["horas"]
            if horas < 6:
                frecuencia_categorias["muy_alta"].append(intervalo)
            elif horas < 24:
                frecuencia_categorias["alta"].append(intervalo)
            elif horas < 72:
                frecuencia_categorias["media"].append(intervalo)
            elif horas < 168:
                frecuencia_categorias["baja"].append(intervalo)
            else:
                frecuencia_categorias["muy_baja"].append(intervalo)
        
        analisis_frecuencia = {}
        
        for categoria, datos in frecuencia_categorias.items():
            if datos:
                engagement_rates = [d["engagement_rate"] for d in datos]
                intervalos_horas = [d["horas"] for d in datos]
                
                analisis_frecuencia[categoria] = {
                    "cantidad_intervalos": len(datos),
                    "intervalo_promedio_horas": round(statistics.mean(intervalos_horas), 1),
                    "intervalo_promedio_dias": round(statistics.mean(intervalos_horas) / 24, 1),
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_rate_max": round(max(engagement_rates), 2),
                    "engagement_rate_min": round(min(engagement_rates), 2)
                }
        
        # Identificar mejor frecuencia
        mejor_frecuencia = max(
            [(c, datos["engagement_rate_promedio"]) for c, datos in analisis_frecuencia.items()],
            key=lambda x: x[1]
        ) if analisis_frecuencia else None
        
        # Calcular frecuencia promedio general
        frecuencia_promedio_horas = statistics.mean([i["horas"] for i in intervalos]) if intervalos else 0
        frecuencia_promedio_dias = frecuencia_promedio_horas / 24
        
        return {
            "frecuencia_promedio": {
                "horas": round(frecuencia_promedio_horas, 1),
                "dias": round(frecuencia_promedio_dias, 1),
                "publicaciones_por_semana": round(168 / frecuencia_promedio_horas, 1) if frecuencia_promedio_horas > 0 else 0
            },
            "analisis_por_categoria": analisis_frecuencia,
            "mejor_frecuencia": mejor_frecuencia[0] if mejor_frecuencia else None,
            "mejor_frecuencia_engagement": mejor_frecuencia[1] if mejor_frecuencia else 0,
            "recomendaciones": [
                f"Frecuencia óptima: {mejor_frecuencia[0]}" if mejor_frecuencia else "No hay suficiente datos",
                f"Publicar cada {analisis_frecuencia[mejor_frecuencia[0]]['intervalo_promedio_horas']:.1f} horas" if mejor_frecuencia and mejor_frecuencia[0] in analisis_frecuencia else "",
                f"Frecuencia promedio actual: cada {frecuencia_promedio_dias:.1f} días"
            ]
        }
    
    def comparar_estrategias_contenido(self, estrategia_a: Dict[str, Any], estrategia_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara dos estrategias de contenido diferentes.
        
        Args:
            estrategia_a: Primera estrategia (debe incluir tipo_contenido, plataforma, etc.)
            estrategia_b: Segunda estrategia
        
        Returns:
            Diccionario con comparación de estrategias
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para comparar estrategias"}
        
        # Filtrar publicaciones según estrategia A
        pubs_a = self.publicaciones
        if estrategia_a.get("tipo_contenido"):
            pubs_a = [p for p in pubs_a if p.tipo_contenido == estrategia_a["tipo_contenido"]]
        if estrategia_a.get("plataforma"):
            pubs_a = [p for p in pubs_a if p.plataforma == estrategia_a["plataforma"]]
        if estrategia_a.get("tiene_media") is not None:
            pubs_a = [p for p in pubs_a if p.tiene_media == estrategia_a["tiene_media"]]
        
        # Filtrar publicaciones según estrategia B
        pubs_b = self.publicaciones
        if estrategia_b.get("tipo_contenido"):
            pubs_b = [p for p in pubs_b if p.tipo_contenido == estrategia_b["tipo_contenido"]]
        if estrategia_b.get("plataforma"):
            pubs_b = [p for p in pubs_b if p.plataforma == estrategia_b["plataforma"]]
        if estrategia_b.get("tiene_media") is not None:
            pubs_b = [p for p in pubs_b if p.tiene_media == estrategia_b["tiene_media"]]
        
        if not pubs_a or not pubs_b:
            return {"error": "No hay suficientes publicaciones para comparar las estrategias"}
        
        # Calcular métricas
        engagement_rate_a = statistics.mean([p.engagement_rate for p in pubs_a])
        engagement_rate_b = statistics.mean([p.engagement_rate for p in pubs_b])
        engagement_score_a = statistics.mean([p.engagement_score for p in pubs_a])
        engagement_score_b = statistics.mean([p.engagement_score for p in pubs_b])
        
        diferencia = engagement_rate_a - engagement_rate_b
        porcentaje_diferencia = (diferencia / engagement_rate_b * 100) if engagement_rate_b > 0 else 0
        
        return {
            "estrategia_a": {
                "parametros": estrategia_a,
                "cantidad_publicaciones": len(pubs_a),
                "engagement_rate_promedio": round(engagement_rate_a, 2),
                "engagement_score_promedio": round(engagement_score_a, 2),
                "publicaciones_virales": sum(1 for p in pubs_a if p.es_viral),
                "porcentaje_viral": round((sum(1 for p in pubs_a if p.es_viral) / len(pubs_a)) * 100, 2)
            },
            "estrategia_b": {
                "parametros": estrategia_b,
                "cantidad_publicaciones": len(pubs_b),
                "engagement_rate_promedio": round(engagement_rate_b, 2),
                "engagement_score_promedio": round(engagement_score_b, 2),
                "publicaciones_virales": sum(1 for p in pubs_b if p.es_viral),
                "porcentaje_viral": round((sum(1 for p in pubs_b if p.es_viral) / len(pubs_b)) * 100, 2)
            },
            "comparacion": {
                "diferencia_engagement_rate": round(diferencia, 2),
                "porcentaje_diferencia": round(porcentaje_diferencia, 2),
                "mejor_estrategia": "A" if diferencia > 0 else "B" if diferencia < 0 else "Empate",
                "ventaja_absoluta": round(abs(diferencia), 2),
                "ventaja_relativa": round(abs(porcentaje_diferencia), 2)
            },
            "recomendacion": f"La estrategia {'A' if diferencia > 0 else 'B'} tiene mejor rendimiento con {abs(porcentaje_diferencia):.1f}% de diferencia" if diferencia != 0 else "Ambas estrategias tienen rendimiento similar"
        }
    
    def generar_plan_contenido_optimizado(self, semanas: int = 4, publicaciones_por_semana: int = 5) -> Dict[str, Any]:
        """
        Genera un plan de contenido optimizado basado en todos los análisis.
        
        Args:
            semanas: Número de semanas a planificar
            publicaciones_por_semana: Número de publicaciones por semana
        
        Returns:
            Diccionario con plan de contenido optimizado
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar plan"}
        
        # Obtener mejores prácticas
        mejor_tipo = self.comparar_tipos_contenido().get("mejor_tipo")
        analisis_plataforma = self.analizar_por_plataforma()
        mejor_plataforma = max(
            analisis_plataforma.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if analisis_plataforma else None
        
        horarios = self.analizar_horarios_optimos()
        mejor_horario = max(
            horarios.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if horarios else None
        
        dias = self.analizar_dias_semana()
        mejor_dia = max(
            dias.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if dias else None
        
        # Analizar formato
        analisis_formato = self.analizar_formato_contenido()
        mejor_formato = analisis_formato.get("mejor_formato")
        
        # Analizar hashtags
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=20)
        hashtags_recomendados = [h['hashtag'] for h in hashtags_efectivos[:10]]
        
        # Generar plan
        plan = {
            "periodo": {
                "semanas": semanas,
                "publicaciones_totales": semanas * publicaciones_por_semana,
                "publicaciones_por_semana": publicaciones_por_semana
            },
            "estrategia_base": {
                "tipo_contenido_principal": mejor_tipo,
                "plataforma_principal": mejor_plataforma,
                "formato_principal": mejor_formato,
                "mejor_dia": mejor_dia,
                "mejor_horario": mejor_horario
            },
            "semanas": [],
            "hashtags_recomendados": hashtags_recomendados,
            "objetivos": {
                "engagement_rate_objetivo": statistics.mean([p.engagement_rate for p in self.publicaciones]) * 1.15,
                "publicaciones_virales_objetivo": int((semanas * publicaciones_por_semana) * 0.1)
            }
        }
        
        fecha_inicio = datetime.now()
        dias_map = {
            'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3,
            'Viernes': 4, 'Sábado': 5, 'Domingo': 6
        }
        
        dia_numero = dias_map.get(mejor_dia, 0) if mejor_dia else 0
        
        # Extraer hora del mejor horario
        hora_publicacion = 10
        if mejor_horario:
            hora_match = re.search(r'(\d{2}):', mejor_horario)
            if hora_match:
                hora_publicacion = int(hora_match.group(1))
        
        for semana in range(semanas):
            semana_data = {
                "semana": semana + 1,
                "publicaciones": []
            }
            
            for i in range(publicaciones_por_semana):
                # Calcular fecha
                dias_hasta_dia = (dia_numero - fecha_inicio.weekday()) % 7
                fecha_publicacion = fecha_inicio + timedelta(days=semana * 7 + dias_hasta_dia + (i % 7))
                
                # Variar tipo de contenido para diversidad
                tipos_variados = ['X', 'Y', 'Z']
                tipo_contenido = tipos_variados[i % len(tipos_variados)] if mejor_tipo else mejor_tipo
                
                # Predecir engagement
                prediccion = self.predecir_engagement_contenido_nuevo(
                    tipo_contenido=tipo_contenido or 'X',
                    plataforma=mejor_plataforma or 'Instagram',
                    hora_publicacion=hora_publicacion,
                    dia_semana=mejor_dia,
                    numero_hashtags=10,
                    tiene_media=True
                )
                
                semana_data["publicaciones"].append({
                    "fecha": fecha_publicacion.date().isoformat(),
                    "dia": fecha_publicacion.strftime('%A'),
                    "hora": f"{hora_publicacion:02d}:00",
                    "tipo_contenido": tipo_contenido,
                    "plataforma": mejor_plataforma or "Instagram",
                    "formato": mejor_formato or "imagen",
                    "hashtags_sugeridos": hashtags_recomendados[:10],
                    "engagement_esperado": prediccion.get("prediccion", {}).get("engagement_rate_esperado", 0),
                    "confianza": prediccion.get("prediccion", {}).get("confianza", 0)
                })
            
            plan["semanas"].append(semana_data)
        
        return plan
    
    def exportar_plan_contenido_json(self, plan: Dict[str, Any], output_file: str = "plan_contenido.json") -> Dict[str, Any]:
        """
        Exporta el plan de contenido a formato JSON.
        
        Args:
            plan: Plan de contenido generado
            output_file: Nombre del archivo de salida
            
        Returns:
            Diccionario con información del archivo generado
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Plan de contenido exportado a {output_file}")
            
            return {
                "archivo": output_file,
                "tamaño_kb": round(os.path.getsize(output_file) / 1024, 2),
                "fecha_exportacion": datetime.now().isoformat(),
                "resumen": {
                    "semanas_planificadas": plan.get("periodo", {}).get("semanas", 0),
                    "publicaciones_totales": plan.get("periodo", {}).get("publicaciones_totales", 0)
                }
            }
        except Exception as e:
            logger.error(f"Error al exportar plan de contenido: {e}")
            return {"error": str(e)}
    
    def analizar_engagement_por_interaccion(self) -> Dict[str, Any]:
        """
        Analiza el engagement desglosado por tipo de interacción (likes, comentarios, shares).
        
        Returns:
            Diccionario con análisis de engagement por tipo de interacción
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Calcular métricas por tipo de interacción
        total_likes = sum(p.likes for p in self.publicaciones)
        total_comentarios = sum(p.comentarios for p in self.publicaciones)
        total_shares = sum(p.shares for p in self.publicaciones)
        total_engagement = sum(p.engagement_total for p in self.publicaciones)
        
        # Calcular porcentajes
        porcentaje_likes = (total_likes / total_engagement * 100) if total_engagement > 0 else 0
        porcentaje_comentarios = (total_comentarios / total_engagement * 100) if total_engagement > 0 else 0
        porcentaje_shares = (total_shares / total_engagement * 100) if total_engagement > 0 else 0
        
        # Analizar por plataforma
        interacciones_por_plataforma = {}
        for plataforma in set(p.plataforma for p in self.publicaciones):
            pubs_plataforma = [p for p in self.publicaciones if p.plataforma == plataforma]
            likes_plataforma = sum(p.likes for p in pubs_plataforma)
            comentarios_plataforma = sum(p.comentarios for p in pubs_plataforma)
            shares_plataforma = sum(p.shares for p in pubs_plataforma)
            engagement_plataforma = sum(p.engagement_total for p in pubs_plataforma)
            
            interacciones_por_plataforma[plataforma] = {
                "likes": likes_plataforma,
                "comentarios": comentarios_plataforma,
                "shares": shares_plataforma,
                "engagement_total": engagement_plataforma,
                "porcentaje_likes": (likes_plataforma / engagement_plataforma * 100) if engagement_plataforma > 0 else 0,
                "porcentaje_comentarios": (comentarios_plataforma / engagement_plataforma * 100) if engagement_plataforma > 0 else 0,
                "porcentaje_shares": (shares_plataforma / engagement_plataforma * 100) if engagement_plataforma > 0 else 0
            }
        
        # Identificar tipo de interacción dominante
        tipo_dominante = max(
            [("likes", porcentaje_likes), ("comentarios", porcentaje_comentarios), ("shares", porcentaje_shares)],
            key=lambda x: x[1]
        )
        
        return {
            "resumen_general": {
                "total_likes": total_likes,
                "total_comentarios": total_comentarios,
                "total_shares": total_shares,
                "total_engagement": total_engagement,
                "porcentaje_likes": round(porcentaje_likes, 2),
                "porcentaje_comentarios": round(porcentaje_comentarios, 2),
                "porcentaje_shares": round(porcentaje_shares, 2)
            },
            "tipo_interaccion_dominante": {
                "tipo": tipo_dominante[0],
                "porcentaje": round(tipo_dominante[1], 2)
            },
            "interacciones_por_plataforma": {
                plataforma: {
                    k: round(v, 2) if isinstance(v, float) else v
                    for k, v in datos.items()
                }
                for plataforma, datos in interacciones_por_plataforma.items()
            },
            "insights": [
                f"El {tipo_dominante[0]} representa el {tipo_dominante[1]:.1f}% del engagement total",
                f"Promedio de likes por publicación: {round(total_likes / len(self.publicaciones), 1)}",
                f"Promedio de comentarios por publicación: {round(total_comentarios / len(self.publicaciones), 1)}",
                f"Promedio de shares por publicación: {round(total_shares / len(self.publicaciones), 1)}"
            ]
        }
    
    def analizar_contenido_por_temas(self, temas: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Analiza el rendimiento de contenido por temas/categorías específicas.
        
        Args:
            temas: Diccionario con temas y palabras clave asociadas (opcional)
            
        Returns:
            Diccionario con análisis de contenido por temas
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Temas por defecto si no se proporcionan
        if not temas:
            temas = {
                "educativo": ["tutorial", "aprende", "guía", "cómo", "tips", "consejos"],
                "entretenimiento": ["divertido", "gracioso", "meme", "chiste", "humor"],
                "inspiracional": ["motivación", "inspiración", "éxito", "superación", "logro"],
                "noticias": ["noticia", "actualidad", "nuevo", "actualización", "último"],
                "promocional": ["oferta", "descuento", "promoción", "venta", "producto"]
            }
        
        resultados_temas = {}
        
        for tema, palabras_clave in temas.items():
            # Buscar publicaciones que contengan las palabras clave
            publicaciones_tema = []
            for pub in self.publicaciones:
                titulo_lower = pub.titulo.lower()
                if any(palabra.lower() in titulo_lower for palabra in palabras_clave):
                    publicaciones_tema.append(pub)
            
            if publicaciones_tema:
                engagement_rates = [p.engagement_rate for p in publicaciones_tema]
                engagement_scores = [p.engagement_score for p in publicaciones_tema]
                
                resultados_temas[tema] = {
                    "cantidad_publicaciones": len(publicaciones_tema),
                    "palabras_clave": palabras_clave,
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_score_promedio": round(statistics.mean(engagement_scores), 2),
                    "engagement_rate_max": round(max(engagement_rates), 2),
                    "engagement_rate_min": round(min(engagement_rates), 2),
                    "publicaciones_virales": sum(1 for p in publicaciones_tema if p.es_viral),
                    "porcentaje_viral": round((sum(1 for p in publicaciones_tema if p.es_viral) / len(publicaciones_tema)) * 100, 2),
                    "top_publicaciones": sorted(
                        [{"id": p.id, "titulo": p.titulo[:50], "engagement_rate": p.engagement_rate} for p in publicaciones_tema],
                        key=lambda x: x["engagement_rate"],
                        reverse=True
                    )[:3]
                }
            else:
                resultados_temas[tema] = {
                    "cantidad_publicaciones": 0,
                    "palabras_clave": palabras_clave,
                    "mensaje": f"No se encontraron publicaciones con tema '{tema}'"
                }
        
        # Identificar mejor tema
        temas_con_datos = {t: d for t, d in resultados_temas.items() if d.get("cantidad_publicaciones", 0) > 0}
        mejor_tema = max(
            temas_con_datos.items(),
            key=lambda x: x[1].get("engagement_rate_promedio", 0)
        ) if temas_con_datos else None
        
        return {
            "temas_analizados": list(temas.keys()),
            "resultados": resultados_temas,
            "mejor_tema": mejor_tema[0] if mejor_tema else None,
            "mejor_tema_engagement": mejor_tema[1].get("engagement_rate_promedio", 0) if mejor_tema else 0,
            "recomendaciones": [
                f"Incrementar contenido del tema '{mejor_tema[0]}'" if mejor_tema else "No hay suficiente datos",
                f"El tema '{mejor_tema[0]}' tiene {mejor_tema[1].get('engagement_rate_promedio', 0):.2f}% de engagement rate promedio" if mejor_tema else ""
            ]
        }
    
    def generar_insights_automaticos(self) -> Dict[str, Any]:
        """
        Genera insights automáticos basados en todos los análisis disponibles.
        
        Returns:
            Diccionario con insights automáticos consolidados
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar insights"}
        
        insights = {
            "fecha_generacion": datetime.now().isoformat(),
            "insights_principales": [],
            "oportunidades": [],
            "alertas": [],
            "recomendaciones_accion": []
        }
        
        # Obtener análisis clave
        estadisticas = self.obtener_estadisticas_resumidas()
        crecimiento = self.analizar_crecimiento_engagement()
        comparacion_tipos = self.comparar_tipos_contenido()
        analisis_plataforma = self.analizar_por_plataforma()
        analisis_viral = self.analizar_contenido_viral_detallado()
        
        # Insight 1: Tendencia general
        if crecimiento.get("tendencia") == "creciente":
            insights["insights_principales"].append({
                "tipo": "Positivo",
                "titulo": "Tendencia Creciente",
                "mensaje": f"El engagement está creciendo {crecimiento.get('crecimiento_total_porcentual', 0):.1f}%",
                "impacto": "Alto"
            })
        elif crecimiento.get("tendencia") == "decreciente":
            insights["alertas"].append({
                "tipo": "Crítica",
                "titulo": "Tendencia Decreciente",
                "mensaje": f"El engagement ha disminuido {abs(crecimiento.get('crecimiento_total_porcentual', 0)):.1f}%",
                "accion": "Revisar estrategia urgentemente"
            })
        
        # Insight 2: Mejor tipo de contenido
        mejor_tipo = comparacion_tipos.get("mejor_tipo")
        if mejor_tipo:
            tipos_datos = comparacion_tipos.get("tipos", {}).get(mejor_tipo, {})
            insights["oportunidades"].append({
                "tipo": "Optimización",
                "titulo": f"Tipo de Contenido '{mejor_tipo}' Destaca",
                "mensaje": f"Tiene un engagement score promedio de {tipos_datos.get('engagement_score_promedio', 0):.1f}",
                "accion": f"Incrementar producción de contenido tipo {mejor_tipo}"
            })
        
        # Insight 3: Contenido viral
        if analisis_viral.get("publicaciones_virales", 0) > 0:
            caracteristicas = analisis_viral.get("caracteristicas_comunes", {})
            tipo_viral = caracteristicas.get("tipo_contenido_mas_viral")
            if tipo_viral:
                insights["insights_principales"].append({
                    "tipo": "Éxito",
                    "titulo": "Contenido Viral Identificado",
                    "mensaje": f"El tipo '{tipo_viral[0]}' representa el {tipo_viral[1]}% del contenido viral",
                    "impacto": "Alto"
                })
        
        # Insight 4: Mejor plataforma
        if analisis_plataforma:
            mejor_plataforma = max(
                analisis_plataforma.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            insights["oportunidades"].append({
                "tipo": "Optimización",
                "titulo": f"Plataforma '{mejor_plataforma[0]}' Destaca",
                "mensaje": f"Tiene un engagement score promedio de {mejor_plataforma[1].get('engagement_score_promedio', 0):.1f}",
                "accion": f"Incrementar presencia en {mejor_plataforma[0]}"
            })
        
        # Insight 5: Engagement rate vs benchmark
        engagement_promedio = estadisticas.get("engagement_rate_promedio", 0)
        if engagement_promedio < 2.0:
            insights["alertas"].append({
                "tipo": "Media",
                "titulo": "Engagement Rate Bajo",
                "mensaje": f"El engagement rate promedio ({engagement_promedio:.2f}%) está por debajo del estándar de la industria (2-3%)",
                "accion": "Revisar estrategia de contenido y timing"
            })
        elif engagement_promedio > 5.0:
            insights["insights_principales"].append({
                "tipo": "Excelente",
                "titulo": "Engagement Rate Excelente",
                "mensaje": f"El engagement rate promedio ({engagement_promedio:.2f}%) está por encima del estándar excelente (5%)",
                "impacto": "Muy Alto"
            })
        
        # Generar recomendaciones de acción
        if mejor_tipo:
            insights["recomendaciones_accion"].append({
                "prioridad": "Alta",
                "accion": f"Crear más contenido tipo {mejor_tipo}",
                "razon": "Tiene el mejor rendimiento promedio"
            })
        
        if analisis_plataforma:
            mejor_plataforma = max(
                analisis_plataforma.items(),
                key=lambda x: x[1].get('engagement_score_promedio', 0)
            )
            insights["recomendaciones_accion"].append({
                "prioridad": "Alta",
                "accion": f"Incrementar publicaciones en {mejor_plataforma[0]}",
                "razon": "Plataforma con mejor engagement"
            })
        
        return insights
    
    def analizar_eficiencia_temporal(self) -> Dict[str, Any]:
        """
        Analiza la eficiencia del contenido en diferentes momentos temporales.
        
        Returns:
            Diccionario con análisis de eficiencia temporal
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Agrupar por diferentes períodos temporales
        eficiencia_por_hora = defaultdict(list)
        eficiencia_por_dia = defaultdict(list)
        eficiencia_por_mes = defaultdict(list)
        
        for pub in self.publicaciones:
            hora = pub.fecha_publicacion.hour
            dia = pub.fecha_publicacion.strftime('%A')
            mes = pub.fecha_publicacion.strftime('%B')
            
            eficiencia_por_hora[hora].append(pub.engagement_rate)
            eficiencia_por_dia[dia].append(pub.engagement_rate)
            eficiencia_por_mes[mes].append(pub.engagement_rate)
        
        # Calcular eficiencia promedio
        eficiencia_hora = {
            hora: {
                "engagement_promedio": round(statistics.mean(rates), 2),
                "cantidad_publicaciones": len(rates),
                "eficiencia_score": round(statistics.mean(rates) * len(rates), 1)  # Engagement * frecuencia
            }
            for hora, rates in eficiencia_por_hora.items()
        }
        
        eficiencia_dia = {
            dia: {
                "engagement_promedio": round(statistics.mean(rates), 2),
                "cantidad_publicaciones": len(rates),
                "eficiencia_score": round(statistics.mean(rates) * len(rates), 1)
            }
            for dia, rates in eficiencia_por_dia.items()
        }
        
        eficiencia_mes = {
            mes: {
                "engagement_promedio": round(statistics.mean(rates), 2),
                "cantidad_publicaciones": len(rates),
                "eficiencia_score": round(statistics.mean(rates) * len(rates), 1)
            }
            for mes, rates in eficiencia_por_mes.items()
        }
        
        # Identificar momentos más eficientes
        mejor_hora = max(eficiencia_hora.items(), key=lambda x: x[1]["eficiencia_score"]) if eficiencia_hora else None
        mejor_dia = max(eficiencia_dia.items(), key=lambda x: x[1]["eficiencia_score"]) if eficiencia_dia else None
        mejor_mes = max(eficiencia_mes.items(), key=lambda x: x[1]["eficiencia_score"]) if eficiencia_mes else None
        
        return {
            "eficiencia_por_hora": eficiencia_hora,
            "eficiencia_por_dia": eficiencia_dia,
            "eficiencia_por_mes": eficiencia_mes,
            "momentos_optimos": {
                "mejor_hora": {
                    "hora": mejor_hora[0] if mejor_hora else None,
                    "datos": mejor_hora[1] if mejor_hora else {}
                },
                "mejor_dia": {
                    "dia": mejor_dia[0] if mejor_dia else None,
                    "datos": mejor_dia[1] if mejor_dia else {}
                },
                "mejor_mes": {
                    "mes": mejor_mes[0] if mejor_mes else None,
                    "datos": mejor_mes[1] if mejor_mes else {}
                }
            },
            "recomendaciones": [
                f"Publicar más contenido a las {mejor_hora[0]}:00 horas" if mejor_hora else "No hay suficiente datos para hora",
                f"Priorizar publicaciones los {mejor_dia[0]}s" if mejor_dia else "No hay suficiente datos para día",
                f"Incrementar producción en {mejor_mes[0]}" if mejor_mes else "No hay suficiente datos para mes"
            ]
        }
    
    def generar_reporte_comparativo_periodos(self, periodo_a: Dict[str, Any], periodo_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un reporte comparativo entre dos períodos de tiempo.
        
        Args:
            periodo_a: Diccionario con fecha_inicio y fecha_fin del primer período
            periodo_b: Diccionario con fecha_inicio y fecha_fin del segundo período
            
        Returns:
            Diccionario con reporte comparativo
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para comparar"}
        
        # Convertir fechas si son strings
        if isinstance(periodo_a.get("fecha_inicio"), str):
            periodo_a["fecha_inicio"] = datetime.fromisoformat(periodo_a["fecha_inicio"])
        if isinstance(periodo_a.get("fecha_fin"), str):
            periodo_a["fecha_fin"] = datetime.fromisoformat(periodo_a["fecha_fin"])
        if isinstance(periodo_b.get("fecha_inicio"), str):
            periodo_b["fecha_inicio"] = datetime.fromisoformat(periodo_b["fecha_inicio"])
        if isinstance(periodo_b.get("fecha_fin"), str):
            periodo_b["fecha_fin"] = datetime.fromisoformat(periodo_b["fecha_fin"])
        
        # Filtrar publicaciones por período
        pubs_periodo_a = [
            p for p in self.publicaciones
            if periodo_a["fecha_inicio"] <= p.fecha_publicacion <= periodo_a["fecha_fin"]
        ]
        
        pubs_periodo_b = [
            p for p in self.publicaciones
            if periodo_b["fecha_inicio"] <= p.fecha_publicacion <= periodo_b["fecha_fin"]
        ]
        
        if not pubs_periodo_a or not pubs_periodo_b:
            return {"error": "Uno o ambos períodos no tienen publicaciones"}
        
        # Calcular métricas para cada período
        def calcular_metricas_periodo(publicaciones):
            return {
                "total_publicaciones": len(publicaciones),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in publicaciones]), 2),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                "porcentaje_viral": round((sum(1 for p in publicaciones if p.es_viral) / len(publicaciones)) * 100, 2),
                "total_likes": sum(p.likes for p in publicaciones),
                "total_comentarios": sum(p.comentarios for p in publicaciones),
                "total_shares": sum(p.shares for p in publicaciones)
            }
        
        metricas_a = calcular_metricas_periodo(pubs_periodo_a)
        metricas_b = calcular_metricas_periodo(pubs_periodo_b)
        
        # Calcular cambios
        cambios = {
            "engagement_rate": {
                "periodo_a": metricas_a["engagement_rate_promedio"],
                "periodo_b": metricas_b["engagement_rate_promedio"],
                "diferencia": round(metricas_b["engagement_rate_promedio"] - metricas_a["engagement_rate_promedio"], 2),
                "cambio_porcentual": round(
                    ((metricas_b["engagement_rate_promedio"] - metricas_a["engagement_rate_promedio"]) / metricas_a["engagement_rate_promedio"] * 100) if metricas_a["engagement_rate_promedio"] > 0 else 0,
                    2
                )
            },
            "publicaciones_virales": {
                "periodo_a": metricas_a["publicaciones_virales"],
                "periodo_b": metricas_b["publicaciones_virales"],
                "diferencia": metricas_b["publicaciones_virales"] - metricas_a["publicaciones_virales"]
            }
        }
        
        return {
            "periodo_a": {
                "fecha_inicio": periodo_a["fecha_inicio"].isoformat(),
                "fecha_fin": periodo_a["fecha_fin"].isoformat(),
                "metricas": metricas_a
            },
            "periodo_b": {
                "fecha_inicio": periodo_b["fecha_inicio"].isoformat(),
                "fecha_fin": periodo_b["fecha_fin"].isoformat(),
                "metricas": metricas_b
            },
            "comparacion": cambios,
            "conclusion": {
                "tendencia": "mejora" if cambios["engagement_rate"]["cambio_porcentual"] > 0 else "disminucion" if cambios["engagement_rate"]["cambio_porcentual"] < 0 else "estable",
                "magnitud": abs(cambios["engagement_rate"]["cambio_porcentual"]),
                "interpretacion": f"El engagement {'mejoró' if cambios['engagement_rate']['cambio_porcentual'] > 0 else 'disminuyó' if cambios['engagement_rate']['cambio_porcentual'] < 0 else 'se mantuvo'} en un {abs(cambios['engagement_rate']['cambio_porcentual']):.1f}%"
            }
        }
    
    def analizar_rendimiento_hashtags_combinados(self, min_coocurrencias: int = 2) -> Dict[str, Any]:
        """
        Analiza el rendimiento de combinaciones de hashtags que aparecen juntos frecuentemente.
        
        Args:
            min_coocurrencias: Número mínimo de veces que deben aparecer juntos
            
        Returns:
            Diccionario con análisis de combinaciones de hashtags
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Contar co-ocurrencias de hashtags
        coocurrencias = defaultdict(int)
        combinaciones_engagement = defaultdict(list)
        
        for pub in self.publicaciones:
            hashtags = [h.lower() for h in pub.hashtags]
            # Generar todas las combinaciones de 2 hashtags
            for i in range(len(hashtags)):
                for j in range(i + 1, len(hashtags)):
                    combinacion = tuple(sorted([hashtags[i], hashtags[j]]))
                    coocurrencias[combinacion] += 1
                    combinaciones_engagement[combinacion].append(pub.engagement_rate)
        
        # Filtrar combinaciones frecuentes
        combinaciones_frecuentes = {
            combo: {
                "frecuencia": count,
                "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                "engagement_rate_max": round(max(engagement_rates), 2),
                "cantidad_publicaciones": len(engagement_rates)
            }
            for combo, count in coocurrencias.items()
            if count >= min_coocurrencias
            for engagement_rates in [combinaciones_engagement[combo]]
        }
        
        # Ordenar por engagement promedio
        combinaciones_ordenadas = sorted(
            combinaciones_frecuentes.items(),
            key=lambda x: x[1]["engagement_rate_promedio"],
            reverse=True
        )
        
        return {
            "total_combinaciones_analizadas": len(combinaciones_frecuentes),
            "min_coocurrencias": min_coocurrencias,
            "mejores_combinaciones": [
                {
                    "hashtags": list(combo),
                    "frecuencia": datos["frecuencia"],
                    "engagement_rate_promedio": datos["engagement_rate_promedio"],
                    "engagement_rate_max": datos["engagement_rate_max"]
                }
                for combo, datos in combinaciones_ordenadas[:10]
            ],
            "recomendaciones": [
                f"Usar combinación: {' + '.join(combinaciones_ordenadas[0][0])}" if combinaciones_ordenadas else "No hay combinaciones frecuentes",
                f"Esta combinación tiene {combinaciones_ordenadas[0][1]['engagement_rate_promedio']:.2f}% de engagement promedio" if combinaciones_ordenadas else ""
            ]
        }
    
    def analizar_evolucion_engagement(self, ventana_dias: int = 7) -> Dict[str, Any]:
        """
        Analiza la evolución del engagement en ventanas de tiempo específicas.
        
        Args:
            ventana_dias: Tamaño de la ventana en días
            
        Returns:
            Diccionario con análisis de evolución
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Ordenar por fecha
        publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
        
        fecha_inicio = publicaciones_ordenadas[0].fecha_publicacion
        fecha_fin = publicaciones_ordenadas[-1].fecha_publicacion
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        # Dividir en ventanas
        ventanas = []
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            fecha_ventana_fin = fecha_actual + timedelta(days=ventana_dias - 1)
            
            pubs_ventana = [
                p for p in publicaciones_ordenadas
                if fecha_actual <= p.fecha_publicacion <= fecha_ventana_fin
            ]
            
            if pubs_ventana:
                engagement_rates = [p.engagement_rate for p in pubs_ventana]
                ventanas.append({
                    "ventana": len(ventanas) + 1,
                    "fecha_inicio": fecha_actual.date().isoformat(),
                    "fecha_fin": fecha_ventana_fin.date().isoformat(),
                    "cantidad_publicaciones": len(pubs_ventana),
                    "engagement_rate_promedio": round(statistics.mean(engagement_rates), 2),
                    "engagement_rate_max": round(max(engagement_rates), 2),
                    "engagement_rate_min": round(min(engagement_rates), 2),
                    "publicaciones_virales": sum(1 for p in pubs_ventana if p.es_viral)
                })
            
            fecha_actual = fecha_ventana_fin + timedelta(days=1)
        
        # Calcular tendencia entre ventanas
        if len(ventanas) >= 2:
            primera_ventana = ventanas[0]["engagement_rate_promedio"]
            ultima_ventana = ventanas[-1]["engagement_rate_promedio"]
            cambio_total = ultima_ventana - primera_ventana
            cambio_porcentual = (cambio_total / primera_ventana * 100) if primera_ventana > 0 else 0
            
            # Calcular cambios entre ventanas consecutivas
            cambios_ventanas = []
            for i in range(1, len(ventanas)):
                cambio = ventanas[i]["engagement_rate_promedio"] - ventanas[i-1]["engagement_rate_promedio"]
                cambios_ventanas.append({
                    "de_ventana": i,
                    "a_ventana": i + 1,
                    "cambio": round(cambio, 2),
                    "cambio_porcentual": round((cambio / ventanas[i-1]["engagement_rate_promedio"] * 100) if ventanas[i-1]["engagement_rate_promedio"] > 0 else 0, 2)
                })
        else:
            cambio_total = 0
            cambio_porcentual = 0
            cambios_ventanas = []
        
        return {
            "periodo_analizado": {
                "fecha_inicio": fecha_inicio.date().isoformat(),
                "fecha_fin": fecha_fin.date().isoformat(),
                "dias_totales": dias_totales,
                "ventana_dias": ventana_dias,
                "total_ventanas": len(ventanas)
            },
            "ventanas": ventanas,
            "evolucion": {
                "engagement_inicial": ventanas[0]["engagement_rate_promedio"] if ventanas else 0,
                "engagement_final": ventanas[-1]["engagement_rate_promedio"] if ventanas else 0,
                "cambio_total": round(cambio_total, 2),
                "cambio_porcentual": round(cambio_porcentual, 2),
                "tendencia": "creciente" if cambio_porcentual > 5 else "decreciente" if cambio_porcentual < -5 else "estable"
            },
            "cambios_entre_ventanas": cambios_ventanas,
            "insights": [
                f"El engagement {'aumentó' if cambio_porcentual > 0 else 'disminuyó' if cambio_porcentual < 0 else 'se mantuvo'} {abs(cambio_porcentual):.1f}% durante el período analizado",
                f"Promedio de publicaciones por ventana: {round(statistics.mean([v['cantidad_publicaciones'] for v in ventanas]), 1)}" if ventanas else ""
            ]
        }
    
    def identificar_contenido_mejorable(self, umbral_engagement: float = None) -> Dict[str, Any]:
        """
        Identifica contenido que tiene potencial de mejora basándose en análisis comparativo.
        
        Args:
            umbral_engagement: Umbral de engagement rate para considerar contenido mejorable (opcional)
            
        Returns:
            Diccionario con contenido identificado como mejorable
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Calcular umbral si no se proporciona
        if umbral_engagement is None:
            engagement_rates = [p.engagement_rate for p in self.publicaciones]
            umbral_engagement = statistics.mean(engagement_rates) * 0.7  # 70% del promedio
        
        # Identificar contenido bajo el umbral
        contenido_mejorable = []
        
        for pub in self.publicaciones:
            if pub.engagement_rate < umbral_engagement:
                # Buscar publicaciones similares exitosas
                pubs_similares = [
                    p for p in self.publicaciones
                    if p.id != pub.id
                    and p.tipo_contenido == pub.tipo_contenido
                    and p.plataforma == pub.plataforma
                ]
                
                if pubs_similares:
                    engagement_similares = [p.engagement_rate for p in pubs_similares]
                    engagement_promedio_similares = statistics.mean(engagement_similares)
                    
                    gap = engagement_promedio_similares - pub.engagement_rate
                    
                    # Analizar diferencias
                    diferencias = []
                    
                    # Analizar hashtags
                    hashtags_exitosos = Counter()
                    for p in [p for p in pubs_similares if p.engagement_rate > engagement_promedio_similares]:
                        hashtags_exitosos.update([h.lower() for h in p.hashtags])
                    
                    hashtags_faltantes = [
                        h for h, count in hashtags_exitosos.most_common(5)
                        if h.lower() not in [ht.lower() for ht in pub.hashtags]
                    ]
                    
                    if hashtags_faltantes:
                        diferencias.append(f"Faltan hashtags exitosos: {', '.join(hashtags_faltantes[:3])}")
                    
                    # Analizar timing
                    horarios_exitosos = [p.fecha_publicacion.hour for p in pubs_similares if p.engagement_rate > engagement_promedio_similares]
                    if horarios_exitosos:
                        hora_optima = Counter(horarios_exitosos).most_common(1)[0][0]
                        if abs(pub.fecha_publicacion.hour - hora_optima) > 3:
                            diferencias.append(f"Timing subóptimo: publicó a las {pub.fecha_publicacion.hour}:00, óptimo sería {hora_optima}:00")
                    
                    contenido_mejorable.append({
                        "id": pub.id,
                        "titulo": pub.titulo[:50],
                        "engagement_rate_actual": round(pub.engagement_rate, 2),
                        "engagement_rate_promedio_similares": round(engagement_promedio_similares, 2),
                        "gap": round(gap, 2),
                        "potencial_mejora": round((gap / pub.engagement_rate * 100) if pub.engagement_rate > 0 else 0, 1),
                        "plataforma": pub.plataforma,
                        "tipo_contenido": pub.tipo_contenido,
                        "diferencias_identificadas": diferencias,
                        "prioridad": "Alta" if gap > 2 else "Media" if gap > 1 else "Baja"
                    })
        
        # Ordenar por potencial de mejora
        contenido_mejorable_ordenado = sorted(
            contenido_mejorable,
            key=lambda x: (x["potencial_mejora"], x["gap"]),
            reverse=True
        )
        
        return {
            "umbral_engagement": round(umbral_engagement, 2),
            "total_contenido_mejorable": len(contenido_mejorable_ordenado),
            "porcentaje_mejorable": round((len(contenido_mejorable_ordenado) / len(self.publicaciones)) * 100, 2),
            "contenido_mejorable": contenido_mejorable_ordenado[:20],  # Top 20
            "resumen_por_prioridad": {
                "alta": len([c for c in contenido_mejorable_ordenado if c["prioridad"] == "Alta"]),
                "media": len([c for c in contenido_mejorable_ordenado if c["prioridad"] == "Media"]),
                "baja": len([c for c in contenido_mejorable_ordenado if c["prioridad"] == "Baja"])
            },
            "recomendaciones": [
                f"Se identificaron {len(contenido_mejorable_ordenado)} publicaciones con potencial de mejora",
                f"Priorizar mejoras en {len([c for c in contenido_mejorable_ordenado if c['prioridad'] == 'Alta'])} publicaciones de alta prioridad"
            ]
        }
    
    def generar_estrategia_hashtags_avanzada(self) -> Dict[str, Any]:
        """
        Genera una estrategia avanzada de hashtags basada en análisis completo.
        
        Returns:
            Diccionario con estrategia avanzada de hashtags
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Analizar hashtags efectivos
        hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=30)
        
        # Analizar combinaciones
        combinaciones = self.analizar_rendimiento_hashtags_combinados()
        
        # Analizar por tipo de contenido
        hashtags_por_tipo = defaultdict(Counter)
        hashtags_por_plataforma = defaultdict(Counter)
        
        for pub in self.publicaciones:
            for hashtag in pub.hashtags:
                hashtags_por_tipo[pub.tipo_contenido][hashtag.lower()] += 1
                hashtags_por_plataforma[pub.plataforma][hashtag.lower()] += 1
        
        # Clasificar hashtags por volumen (estimado)
        hashtags_populares = []  # Alto volumen
        hashtags_medios = []     # Volumen medio
        hashtags_nicho = []      # Bajo volumen, específicos
        
        for h in hashtags_efectivos[:20]:
            frecuencia = sum(1 for p in self.publicaciones if h['hashtag'].lower() in [ht.lower() for ht in p.hashtags])
            if frecuencia > len(self.publicaciones) * 0.3:
                hashtags_populares.append(h['hashtag'])
            elif frecuencia > len(self.publicaciones) * 0.1:
                hashtags_medios.append(h['hashtag'])
            else:
                hashtags_nicho.append(h['hashtag'])
        
        return {
            "estrategia_general": {
                "numero_total_hashtags": 10,
                "distribucion_recomendada": {
                    "hashtags_populares": 3,
                    "hashtags_medios": 4,
                    "hashtags_nicho": 3
                },
                "rotacion": "Cambiar 30% de hashtags cada publicación"
            },
            "hashtags_recomendados": {
                "populares": hashtags_populares[:10],
                "medios": hashtags_medios[:10],
                "nicho": hashtags_nicho[:10]
            },
            "combinaciones_efectivas": combinaciones.get("mejores_combinaciones", [])[:5],
            "hashtags_por_tipo_contenido": {
                tipo: [h for h, _ in hashtags.most_common(5)]
                for tipo, hashtags in hashtags_por_tipo.items()
            },
            "hashtags_por_plataforma": {
                plataforma: [h for h, _ in hashtags.most_common(5)]
                for plataforma, hashtags in hashtags_por_plataforma.items()
            },
            "mejores_practicas": [
                "Usar 5-10 hashtags por publicación",
                "Mezclar hashtags populares con hashtags de nicho",
                "Incluir hashtags específicos del tipo de contenido",
                "Rotar hashtags regularmente para evitar shadowban",
                "Usar combinaciones probadas de hashtags"
            ]
        }
    
    def calcular_impacto_mejoras(self, mejoras_propuestas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula el impacto esperado de mejoras propuestas al contenido.
        
        Args:
            mejoras_propuestas: Lista de mejoras propuestas con tipo y descripción
            
        Returns:
            Diccionario con impacto calculado de las mejoras
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para calcular impacto"}
        
        impacto_total = {
            "mejoras_analizadas": len(mejoras_propuestas),
            "impacto_esperado": {},
            "mejoras_por_impacto": {
                "alto": [],
                "medio": [],
                "bajo": []
            }
        }
        
        for mejora in mejoras_propuestas:
            tipo_mejora = mejora.get("tipo", "general")
            impacto_estimado = mejora.get("impacto_estimado", "medio")
            
            # Calcular impacto basado en análisis histórico
            impacto_calculado = 0
            
            if tipo_mejora == "hashtags":
                # Analizar impacto de hashtags
                analisis_hashtags = self.analizar_correlacion_factores()
                if "hashtags_vs_engagement" in analisis_hashtags.get("correlaciones", {}):
                    corr = analisis_hashtags["correlaciones"]["hashtags_vs_engagement"]["correlacion"]
                    impacto_calculado = abs(corr) * 2  # Escalar correlación
            
            elif tipo_mejora == "timing":
                # Analizar impacto de timing
                horarios = self.analizar_horarios_optimos()
                if horarios:
                    mejor_horario = max(horarios.items(), key=lambda x: x[1].get('engagement_score_promedio', 0))
                    impacto_calculado = mejor_horario[1].get('engagement_score_promedio', 0) / 10
            
            elif tipo_mejora == "formato":
                # Analizar impacto de formato
                analisis_formato = self.analizar_formato_contenido()
                mejor_formato = analisis_formato.get("mejor_formato_engagement", 0)
                if mejor_formato > 0:
                    engagement_promedio = statistics.mean([p.engagement_rate for p in self.publicaciones])
                    impacto_calculado = (mejor_formato - engagement_promedio) / engagement_promedio * 100
            
            elif tipo_mejora == "tipo_contenido":
                # Analizar impacto de tipo de contenido
                comparacion = self.comparar_tipos_contenido()
                mejor_tipo = comparacion.get("mejor_tipo")
                if mejor_tipo:
                    tipos_datos = comparacion.get("tipos", {}).get(mejor_tipo, {})
                    engagement_promedio = statistics.mean([p.engagement_rate for p in self.publicaciones])
                    mejor_engagement = tipos_datos.get("engagement_rate_promedio", 0)
                    if mejor_engagement > 0:
                        impacto_calculado = (mejor_engagement - engagement_promedio) / engagement_promedio * 100
            
            # Clasificar por impacto
            if impacto_calculado > 15:
                impacto_total["mejoras_por_impacto"]["alto"].append({
                    "mejora": mejora,
                    "impacto_calculado": round(impacto_calculado, 2)
                })
            elif impacto_calculado > 5:
                impacto_total["mejoras_por_impacto"]["medio"].append({
                    "mejora": mejora,
                    "impacto_calculado": round(impacto_calculado, 2)
                })
            else:
                impacto_total["mejoras_por_impacto"]["bajo"].append({
                    "mejora": mejora,
                    "impacto_calculado": round(impacto_calculado, 2)
                })
            
            impacto_total["impacto_esperado"][mejora.get("descripcion", tipo_mejora)] = round(impacto_calculado, 2)
        
        # Calcular impacto total estimado
        impacto_promedio = statistics.mean(list(impacto_total["impacto_esperado"].values())) if impacto_total["impacto_esperado"] else 0
        
        return {
            **impacto_total,
            "resumen": {
                "impacto_promedio": round(impacto_promedio, 2),
                "mejoras_alto_impacto": len(impacto_total["mejoras_por_impacto"]["alto"]),
                "mejoras_medio_impacto": len(impacto_total["mejoras_por_impacto"]["medio"]),
                "mejoras_bajo_impacto": len(impacto_total["mejoras_por_impacto"]["bajo"])
            },
            "recomendaciones": [
                f"Priorizar {len(impacto_total['mejoras_por_impacto']['alto'])} mejoras de alto impacto",
                f"Impacto promedio esperado: {impacto_promedio:.1f}% de mejora en engagement"
            ]
        }
    
    def analizar_contenido_por_sentimiento(self, umbral_positivo: float = 0.6, umbral_negativo: float = 0.4) -> Dict[str, Any]:
        """
        Analiza el contenido por sentimiento basado en comentarios y engagement.
        
        Args:
            umbral_positivo: Umbral para considerar sentimiento positivo
            umbral_negativo: Umbral para considerar sentimiento negativo
            
        Returns:
            Diccionario con análisis de sentimiento
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Clasificar por sentimiento basado en ratio de comentarios/likes
        contenido_positivo = []
        contenido_neutro = []
        contenido_negativo = []
        
        for pub in self.publicaciones:
            if pub.likes > 0:
                ratio_comentarios_likes = pub.comentarios / pub.likes
                
                # Ratio alto puede indicar controversia (negativo) o alto engagement (positivo)
                # Usar engagement rate como indicador adicional
                if pub.engagement_rate > statistics.mean([p.engagement_rate for p in self.publicaciones]) * 1.2:
                    contenido_positivo.append(pub)
                elif ratio_comentarios_likes > 0.1:  # Muchos comentarios relativos a likes
                    contenido_negativo.append(pub)
                else:
                    contenido_neutro.append(pub)
            else:
                contenido_neutro.append(pub)
        
        # Calcular métricas por sentimiento
        def calcular_metricas_sentimiento(publicaciones):
            if not publicaciones:
                return {}
            return {
                "cantidad": len(publicaciones),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in publicaciones]), 2),
                "ratio_comentarios_likes": round(statistics.mean([p.comentarios / p.likes if p.likes > 0 else 0 for p in publicaciones]), 3),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral)
            }
        
        metricas_positivo = calcular_metricas_sentimiento(contenido_positivo)
        metricas_neutro = calcular_metricas_sentimiento(contenido_neutro)
        metricas_negativo = calcular_metricas_sentimiento(contenido_negativo)
        
        return {
            "distribucion": {
                "positivo": {
                    "cantidad": len(contenido_positivo),
                    "porcentaje": round((len(contenido_positivo) / len(self.publicaciones)) * 100, 2),
                    "metricas": metricas_positivo
                },
                "neutro": {
                    "cantidad": len(contenido_neutro),
                    "porcentaje": round((len(contenido_neutro) / len(self.publicaciones)) * 100, 2),
                    "metricas": metricas_neutro
                },
                "negativo": {
                    "cantidad": len(contenido_negativo),
                    "porcentaje": round((len(contenido_negativo) / len(self.publicaciones)) * 100, 2),
                    "metricas": metricas_negativo
                }
            },
            "insights": [
                f"Contenido positivo: {len(contenido_positivo)} publicaciones ({metricas_positivo.get('engagement_rate_promedio', 0):.2f}% engagement promedio)" if contenido_positivo else "",
                f"Contenido neutro: {len(contenido_neutro)} publicaciones ({metricas_neutro.get('engagement_rate_promedio', 0):.2f}% engagement promedio)" if contenido_neutro else "",
                f"Contenido negativo: {len(contenido_negativo)} publicaciones ({metricas_negativo.get('engagement_rate_promedio', 0):.2f}% engagement promedio)" if contenido_negativo else ""
            ]
        }
    
    def generar_recomendaciones_personalizadas_por_publicacion(self, publicacion_id: str) -> Dict[str, Any]:
        """
        Genera recomendaciones personalizadas para una publicación específica.
        
        Args:
            publicacion_id: ID de la publicación
            
        Returns:
            Diccionario con recomendaciones personalizadas
        """
        # Buscar publicación
        publicacion = next((p for p in self.publicaciones if p.id == publicacion_id), None)
        
        if not publicacion:
            return {"error": f"Publicación {publicacion_id} no encontrada"}
        
        recomendaciones = []
        prioridades = []
        
        # Comparar con publicaciones similares exitosas
        pubs_similares = [
            p for p in self.publicaciones
            if p.id != publicacion_id
            and p.tipo_contenido == publicacion.tipo_contenido
            and p.plataforma == publicacion.plataforma
        ]
        
        if pubs_similares:
            engagement_similares = [p.engagement_rate for p in pubs_similares]
            engagement_promedio = statistics.mean(engagement_similares)
            
            if publicacion.engagement_rate < engagement_promedio:
                gap = engagement_promedio - publicacion.engagement_rate
                recomendaciones.append({
                    "tipo": "Optimización",
                    "prioridad": "Alta" if gap > 2 else "Media",
                    "titulo": "Engagement por debajo del promedio",
                    "mensaje": f"El engagement ({publicacion.engagement_rate:.2f}%) está {gap:.2f}% por debajo del promedio de publicaciones similares ({engagement_promedio:.2f}%)",
                    "acciones": [
                        "Revisar hashtags y considerar usar hashtags más efectivos",
                        "Evaluar timing de publicación",
                        "Analizar formato y calidad del contenido"
                    ]
                })
                prioridades.append(("Alta" if gap > 2 else "Media", gap))
        
        # Analizar hashtags
        hashtags_optimizacion = self.optimizar_hashtags_automaticamente(publicacion_id)
        if hashtags_optimizacion.get("recomendaciones_especificas"):
            recs_hashtags = hashtags_optimizacion["recomendaciones_especificas"]
            recomendaciones.append({
                "tipo": "Hashtags",
                "prioridad": "Media",
                "titulo": "Optimización de Hashtags",
                "mensaje": recs_hashtags.get("razon", ""),
                "acciones": [
                    f"Considerar usar estos hashtags: {', '.join(recs_hashtags.get('hashtags_recomendados', [])[:5])}"
                ]
            })
            prioridades.append(("Media", 1))
        
        # Analizar timing
        horarios = self.analizar_horarios_optimos()
        if horarios:
            mejor_horario = max(horarios.items(), key=lambda x: x[1].get('engagement_score_promedio', 0))
            hora_actual = publicacion.fecha_publicacion.hour
            
            # Extraer hora del mejor horario
            hora_match = re.search(r'(\d{2}):', mejor_horario[0])
            hora_optima = int(hora_match.group(1)) if hora_match else hora_actual
            
            if abs(hora_actual - hora_optima) > 3:
                recomendaciones.append({
                    "tipo": "Timing",
                    "prioridad": "Media",
                    "titulo": "Timing Subóptimo",
                    "mensaje": f"Publicaste a las {hora_actual}:00, pero el mejor horario es {hora_optima}:00",
                    "acciones": [
                        f"Programar futuras publicaciones similares para las {hora_optima}:00 horas"
                    ]
                })
                prioridades.append(("Media", 0.5))
        
        # Analizar formato
        analisis_formato = self.analizar_formato_contenido()
        mejor_formato = analisis_formato.get("mejor_formato")
        
        # Determinar formato actual
        formato_actual = "video" if publicacion.duracion_video > 0 else "imagen" if publicacion.tiene_media else "texto"
        
        if mejor_formato and formato_actual != mejor_formato:
            recomendaciones.append({
                "tipo": "Formato",
                "prioridad": "Baja",
                "titulo": "Formato Alternativo",
                "mensaje": f"El formato '{mejor_formato}' tiene mejor rendimiento que '{formato_actual}'",
                "acciones": [
                    f"Considerar usar formato '{mejor_formato}' para futuras publicaciones similares"
                ]
            })
            prioridades.append(("Baja", 0.3))
        
        # Ordenar por prioridad
        orden_prioridad = {"Alta": 3, "Media": 2, "Baja": 1}
        recomendaciones_ordenadas = sorted(
            recomendaciones,
            key=lambda x: (orden_prioridad.get(x["prioridad"], 0), x.get("impacto", 0)),
            reverse=True
        )
        
        return {
            "publicacion": {
                "id": publicacion.id,
                "titulo": publicacion.titulo[:50],
                "engagement_rate": round(publicacion.engagement_rate, 2),
                "plataforma": publicacion.plataforma,
                "tipo_contenido": publicacion.tipo_contenido
            },
            "total_recomendaciones": len(recomendaciones_ordenadas),
            "recomendaciones": recomendaciones_ordenadas,
            "resumen": {
                "recomendaciones_alta_prioridad": len([r for r in recomendaciones_ordenadas if r["prioridad"] == "Alta"]),
                "recomendaciones_media_prioridad": len([r for r in recomendaciones_ordenadas if r["prioridad"] == "Media"]),
                "recomendaciones_baja_prioridad": len([r for r in recomendaciones_ordenadas if r["prioridad"] == "Baja"])
            }
        }
    
    def analizar_rendimiento_por_calidad_contenido(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento basado en calidad del contenido (basado en métricas disponibles).
        
        Returns:
            Diccionario con análisis de rendimiento por calidad
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Calcular score de calidad para cada publicación
        calidad_publicaciones = []
        
        for pub in self.publicaciones:
            score_calidad = 0
            
            # Factor 1: Tiene media visual
            if pub.tiene_media:
                score_calidad += 20
            
            # Factor 2: Número de hashtags (óptimo entre 5-15)
            num_hashtags = len(pub.hashtags)
            if 5 <= num_hashtags <= 15:
                score_calidad += 20
            elif num_hashtags > 0:
                score_calidad += 10
            
            # Factor 3: Longitud de título (óptimo entre 50-200 caracteres)
            longitud_titulo = len(pub.titulo)
            if 50 <= longitud_titulo <= 200:
                score_calidad += 20
            elif longitud_titulo > 0:
                score_calidad += 10
            
            # Factor 4: Engagement rate (normalizado)
            engagement_normalizado = min(pub.engagement_rate / 10 * 20, 20)  # Máximo 20 puntos
            score_calidad += engagement_normalizado
            
            # Factor 5: Consistencia (basado en ratio reach/impresiones)
            if pub.impresiones > 0:
                ratio_reach = pub.reach / pub.impresiones
                if 0.7 <= ratio_reach <= 1.0:
                    score_calidad += 20
                elif ratio_reach > 0:
                    score_calidad += 10
            
            calidad_publicaciones.append({
                "publicacion": pub,
                "score_calidad": round(score_calidad, 1),
                "desglose": {
                    "tiene_media": pub.tiene_media,
                    "hashtags_optimos": 5 <= num_hashtags <= 15,
                    "longitud_optima": 50 <= longitud_titulo <= 200,
                    "engagement_normalizado": round(engagement_normalizado, 1)
                }
            })
        
        # Clasificar por calidad
        calidad_alta = [c for c in calidad_publicaciones if c["score_calidad"] >= 70]
        calidad_media = [c for c in calidad_publicaciones if 50 <= c["score_calidad"] < 70]
        calidad_baja = [c for c in calidad_publicaciones if c["score_calidad"] < 50]
        
        def calcular_metricas_calidad(publicaciones_calidad):
            if not publicaciones_calidad:
                return {}
            pubs = [c["publicacion"] for c in publicaciones_calidad]
            return {
                "cantidad": len(pubs),
                "score_calidad_promedio": round(statistics.mean([c["score_calidad"] for c in publicaciones_calidad]), 1),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in pubs]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in pubs]), 2),
                "publicaciones_virales": sum(1 for p in pubs if p.es_viral)
            }
        
        return {
            "distribucion_calidad": {
                "alta": {
                    "rango": "70-100",
                    **calcular_metricas_calidad(calidad_alta)
                },
                "media": {
                    "rango": "50-69",
                    **calcular_metricas_calidad(calidad_media)
                },
                "baja": {
                    "rango": "0-49",
                    **calcular_metricas_calidad(calidad_baja)
                }
            },
            "score_calidad_promedio_general": round(statistics.mean([c["score_calidad"] for c in calidad_publicaciones]), 1),
            "top_publicaciones_calidad": sorted(
                calidad_publicaciones,
                key=lambda x: x["score_calidad"],
                reverse=True
            )[:5],
            "recomendaciones": [
                f"Score de calidad promedio: {round(statistics.mean([c['score_calidad'] for c in calidad_publicaciones]), 1)}/100",
                f"Publicaciones de alta calidad: {len(calidad_alta)} ({len(calidad_alta)/len(self.publicaciones)*100:.1f}%)",
                "Mejorar factores de calidad puede incrementar engagement significativamente"
            ]
        }
    
    def generar_dashboard_completo_interactivo(self) -> Dict[str, Any]:
        """
        Genera un dashboard completo e interactivo con todas las métricas clave.
        
        Returns:
            Diccionario con dashboard completo interactivo
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para generar dashboard"}
        
        # Obtener todos los análisis necesarios
        dashboard_resumen = self.generar_dashboard_resumen()
        insights = self.generar_insights_automaticos()
        recomendaciones = self.generar_recomendaciones_automaticas()
        benchmark = self.analizar_benchmark_competencia()
        score = self.calcular_score_rendimiento()
        crecimiento = self.analizar_crecimiento_engagement()
        eficiencia = self.analizar_eficiencia_contenido()
        analisis_viral = self.analizar_contenido_viral_detallado()
        
        # Obtener mejores prácticas
        mejor_tipo = self.comparar_tipos_contenido().get("mejor_tipo")
        analisis_plataforma = self.analizar_por_plataforma()
        mejor_plataforma = max(
            analisis_plataforma.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if analisis_plataforma else None
        
        horarios = self.analizar_horarios_optimos()
        mejor_horario = max(
            horarios.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if horarios else None
        
        dias = self.analizar_dias_semana()
        mejor_dia = max(
            dias.items(),
            key=lambda x: x[1].get('engagement_score_promedio', 0)
        )[0] if dias else None
        
        dashboard = {
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "version": "5.0",
                "total_publicaciones": len(self.publicaciones),
                "periodo_analizado": {
                    "fecha_inicio": min(p.fecha_publicacion for p in self.publicaciones).isoformat(),
                    "fecha_fin": max(p.fecha_publicacion for p in self.publicaciones).isoformat()
                }
            },
            "metricas_principales": {
                "engagement_rate_promedio": dashboard_resumen["resumen_ejecutivo"]["engagement_rate_promedio"],
                "score_general": dashboard_resumen["resumen_ejecutivo"]["score_general"],
                "tendencia": crecimiento.get("tendencia", "estable"),
                "crecimiento_porcentual": crecimiento.get("crecimiento_total_porcentual", 0),
                "publicaciones_virales": dashboard_resumen["metricas_clave"]["publicaciones_virales"],
                "porcentaje_viral": dashboard_resumen["metricas_clave"]["porcentaje_viral"]
            },
            "mejores_practicas": {
                "mejor_tipo_contenido": mejor_tipo,
                "mejor_plataforma": mejor_plataforma,
                "mejor_dia": mejor_dia,
                "mejor_horario": mejor_horario,
                "top_publicaciones": dashboard_resumen["mejores_practicas"]["top_publicaciones"]
            },
            "insights": {
                "principales": insights.get("insights_principales", [])[:5],
                "oportunidades": insights.get("oportunidades", [])[:5],
                "alertas": insights.get("alertas", [])[:5]
            },
            "recomendaciones": {
                "prioritarias": recomendaciones.get("recomendaciones", [])[:10],
                "por_categoria": recomendaciones.get("resumen_por_categoria", {})
            },
            "benchmark": {
                "clasificacion": benchmark["rendimiento_general"]["clasificacion"],
                "engagement_actual": benchmark["rendimiento_general"]["engagement_rate_actual"],
                "benchmark_industria": benchmark["rendimiento_general"]["benchmark_industria"],
                "gap_para_excelente": benchmark["rendimiento_general"]["gap_para_excelente"]
            },
            "score_desglosado": score.get("desglose", {}),
            "eficiencia": eficiencia.get("resumen", {}),
            "contenido_viral": {
                "total_virales": analisis_viral.get("resumen", {}).get("publicaciones_virales", 0),
                "porcentaje_viral": analisis_viral.get("resumen", {}).get("porcentaje_viral", 0),
                "caracteristicas_comunes": analisis_viral.get("caracteristicas_comunes", {})
            },
            "secciones_disponibles": [
                "Métricas Principales",
                "Mejores Prácticas",
                "Insights Automáticos",
                "Recomendaciones",
                "Benchmark",
                "Score de Rendimiento",
                "Eficiencia",
                "Contenido Viral"
            ]
        }
        
        return dashboard
    
    def exportar_dashboard_completo_json(self, output_file: str = "dashboard_completo.json") -> Dict[str, Any]:
        """
        Exporta el dashboard completo a formato JSON.
        
        Args:
            output_file: Nombre del archivo de salida
            
        Returns:
            Diccionario con información del archivo generado
        """
        try:
            dashboard = self.generar_dashboard_completo_interactivo()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Dashboard completo exportado a {output_file}")
            
            return {
                "archivo": output_file,
                "tamaño_kb": round(os.path.getsize(output_file) / 1024, 2),
                "fecha_exportacion": datetime.now().isoformat(),
                "secciones_incluidas": dashboard.get("secciones_disponibles", []),
                "total_secciones": len(dashboard.get("secciones_disponibles", []))
            }
        except Exception as e:
            logger.error(f"Error al exportar dashboard completo: {e}")
            return {"error": str(e)}
    
    def analizar_contenido_por_tipo_narrativo(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento del contenido basado en el tipo de narrativa o storytelling.
        
        Returns:
            Diccionario con análisis de rendimiento por tipo narrativo
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Patrones de tipos narrativos
        tipos_narrativos = {
            "caso_estudio": [r"caso de estudio", r"caso real", r"historia real", r"experiencia real"],
            "testimonial": [r"testimonio", r"cliente", r"usuario", r"experiencia de"],
            "tutorial": [r"cómo", r"tutorial", r"paso a paso", r"guía", r"aprende a"],
            "lista": [r"^\d+", r"top \d+", r"\d+ formas", r"\d+ tips", r"\d+ razones", r"\d+ cosas"],
            "comparacion": [r"vs", r"versus", r"comparación", r"diferencia entre", r"mejor que"],
            "mito_realidad": [r"mito", r"realidad", r"verdad", r"mentira", r"mito vs"],
            "prediccion": [r"será", r"será el", r"tendencia", r"futuro", r"próximo"],
            "noticia": [r"nuevo", r"lanzamiento", r"anuncio", r"actualización", r"último"],
            "entretenimiento": [r"divertido", r"gracioso", r"chiste", r"meme", r"viral"],
            "educativo": [r"explica", r"qué es", r"definición", r"concepto", r"aprende sobre"]
        }
        
        contenido_por_tipo = {tipo: [] for tipo in tipos_narrativos.keys()}
        contenido_sin_tipo_detectado = []
        
        for pub in self.publicaciones:
            titulo_lower = pub.titulo.lower()
            tipo_encontrado = False
            
            for tipo_narrativo, patrones in tipos_narrativos.items():
                for patron in patrones:
                    if re.search(patron, titulo_lower):
                        contenido_por_tipo[tipo_narrativo].append(pub)
                        tipo_encontrado = True
                        break
                if tipo_encontrado:
                    break
            
            if not tipo_encontrado:
                contenido_sin_tipo_detectado.append(pub)
        
        def calcular_metricas_narrativo(publicaciones):
            if not publicaciones:
                return {}
            return {
                "cantidad": len(publicaciones),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in publicaciones]), 2),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                "ratio_comentarios": round(statistics.mean([p.comentarios / p.likes if p.likes > 0 else 0 for p in publicaciones]), 3)
            }
        
        metricas_por_tipo = {tipo: calcular_metricas_narrativo(pubs) for tipo, pubs in contenido_por_tipo.items()}
        metricas_sin_tipo = calcular_metricas_narrativo(contenido_sin_tipo_detectado)
        
        # Mejor tipo narrativo
        mejor_tipo_narrativo = max(
            [(tipo, m) for tipo, m in metricas_por_tipo.items() if m.get("cantidad", 0) > 0],
            key=lambda x: x[1].get("engagement_rate_promedio", 0),
            default=(None, {})
        )
        
        # Construir distribución de tipos narrativos
        distribucion_tipos = []
        for tipo, pubs in contenido_por_tipo.items():
            if len(pubs) > 0:
                tipo_formateado = tipo.replace("_", " ").title()
                distribucion_tipos.append(f"{tipo_formateado}: {len(pubs)}")
        distribucion_texto = ", ".join(distribucion_tipos) if distribucion_tipos else "N/A"
        
        return {
            "distribucion": {
                **{f"tipo_{tipo}": {
                    "tipo": tipo.replace("_", " ").title(),
                    **metricas
                } for tipo, metricas in metricas_por_tipo.items()},
                "sin_tipo_detectado": {
                    "tipo": "Sin tipo detectado",
                    **metricas_sin_tipo
                }
            },
            "mejor_tipo_narrativo": {
                "tipo": mejor_tipo_narrativo[0].replace("_", " ").title() if mejor_tipo_narrativo[0] else None,
                "metricas": mejor_tipo_narrativo[1]
            },
            "recomendaciones": [
                f"Mejor tipo narrativo: '{mejor_tipo_narrativo[0].replace('_', ' ').title()}' con {mejor_tipo_narrativo[1].get('engagement_rate_promedio', 0):.2f}% engagement promedio" if mejor_tipo_narrativo[0] else "",
                f"Distribución de tipos narrativos: {distribucion_texto}",
                "Tipos narrativos como caso de estudio y testimoniales generan alta confianza",
                "Listas y tutoriales son muy efectivos para engagement"
            ]
        }
    
    def analizar_contenido_por_palabras_poderosas(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento del contenido basado en el uso de palabras poderosas.
        
        Returns:
            Diccionario con análisis de rendimiento por palabras poderosas
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Palabras poderosas categorizadas
        palabras_poderosas = {
            "urgencia": ["ahora", "urgente", "inmediato", "rápido", "ya", "hoy", "limitado", "última oportunidad"],
            "exclusividad": ["exclusivo", "solo", "único", "especial", "privado", "VIP", "premium"],
            "beneficio": ["gratis", "descuento", "ahorra", "gana", "obtén", "consigue", "logra", "mejora"],
            "curiosidad": ["secreto", "oculto", "nadie te", "descubre", "revela", "sorprendente", "inesperado"],
            "autoridad": ["experto", "profesional", "certificado", "verificado", "comprobado", "probado"],
            "social": ["viral", "trending", "popular", "más visto", "más compartido", "top"],
            "emocional": ["increíble", "asombroso", "sorprendente", "impactante", "emocionante", "inspirador"]
        }
        
        contenido_por_categoria = {categoria: [] for categoria in palabras_poderosas.keys()}
        contenido_sin_palabras_poderosas = []
        
        for pub in self.publicaciones:
            titulo_lower = pub.titulo.lower()
            categorias_encontradas = []
            
            for categoria, palabras in palabras_poderosas.items():
                for palabra in palabras:
                    if palabra in titulo_lower:
                        categorias_encontradas.append(categoria)
                        break
            
            if categorias_encontradas:
                for categoria in categorias_encontradas:
                    contenido_por_categoria[categoria].append(pub)
            else:
                contenido_sin_palabras_poderosas.append(pub)
        
        def calcular_metricas_palabras(publicaciones):
            if not publicaciones:
                return {}
            return {
                "cantidad": len(publicaciones),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in publicaciones]), 2),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral)
            }
        
        metricas_por_categoria = {cat: calcular_metricas_palabras(pubs) for cat, pubs in contenido_por_categoria.items()}
        metricas_sin_palabras = calcular_metricas_palabras(contenido_sin_palabras_poderosas)
        
        # Mejor categoría de palabras poderosas
        mejor_categoria = max(
            [(cat, m) for cat, m in metricas_por_categoria.items() if m.get("cantidad", 0) > 0],
            key=lambda x: x[1].get("engagement_rate_promedio", 0),
            default=(None, {})
        )
        
        return {
            "distribucion": {
                **{f"categoria_{cat}": {
                    "categoria": cat.replace("_", " ").title(),
                    **metricas
                } for cat, metricas in metricas_por_categoria.items()},
                "sin_palabras_poderosas": {
                    "categoria": "Sin palabras poderosas",
                    **metricas_sin_palabras
                }
            },
            "mejor_categoria": {
                "categoria": mejor_categoria[0].replace("_", " ").title() if mejor_categoria[0] else None,
                "metricas": mejor_categoria[1]
            },
            "recomendaciones": [
                f"Mejor categoría de palabras poderosas: '{mejor_categoria[0].replace('_', ' ').title()}' con {mejor_categoria[1].get('engagement_rate_promedio', 0):.2f}% engagement promedio" if mejor_categoria[0] else "",
                f"Publicaciones con palabras poderosas: {sum(len(pubs) for pubs in contenido_por_categoria.values())} ({sum(len(pubs) for pubs in contenido_por_categoria.values())/len(self.publicaciones)*100:.1f}%)",
                "Palabras de urgencia y curiosidad generan más clicks",
                "Palabras de autoridad y beneficio aumentan confianza"
            ]
        }
    
    def analizar_contenido_por_complejidad(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento del contenido basado en la complejidad del texto.
        
        Returns:
            Diccionario con análisis de rendimiento por complejidad
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        contenido_simple = []
        contenido_intermedio = []
        contenido_complejo = []
        
        for pub in self.publicaciones:
            titulo = pub.titulo
            
            # Métricas de complejidad
            longitud = len(titulo)
            num_palabras = len(titulo.split())
            num_oraciones = titulo.count('.') + titulo.count('!') + titulo.count('?')
            palabras_complejas = len([w for w in titulo.split() if len(w) > 8])
            
            # Score de complejidad (0-100)
            score_complejidad = (
                (longitud / 500 * 30) +  # Longitud (máx 30 puntos)
                (num_palabras / 50 * 20) +  # Número de palabras (máx 20 puntos)
                (num_oraciones * 5) +  # Número de oraciones (máx 20 puntos)
                (palabras_complejas / num_palabras * 100 * 30 if num_palabras > 0 else 0)  # Palabras complejas (máx 30 puntos)
            )
            
            score_complejidad = min(score_complejidad, 100)
            
            if score_complejidad < 30:
                contenido_simple.append({"publicacion": pub, "score": score_complejidad})
            elif score_complejidad < 60:
                contenido_intermedio.append({"publicacion": pub, "score": score_complejidad})
            else:
                contenido_complejo.append({"publicacion": pub, "score": score_complejidad})
        
        def calcular_metricas_complejidad(lista_contenido):
            if not lista_contenido:
                return {}
            pubs = [c["publicacion"] for c in lista_contenido]
            return {
                "cantidad": len(pubs),
                "score_complejidad_promedio": round(statistics.mean([c["score"] for c in lista_contenido]), 1),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in pubs]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in pubs]), 2),
                "publicaciones_virales": sum(1 for p in pubs if p.es_viral)
            }
        
        metricas_simple = calcular_metricas_complejidad(contenido_simple)
        metricas_intermedio = calcular_metricas_complejidad(contenido_intermedio)
        metricas_complejo = calcular_metricas_complejidad(contenido_complejo)
        
        return {
            "distribucion": {
                "simple": {
                    "rango": "0-30 (Simple)",
                    **metricas_simple
                },
                "intermedio": {
                    "rango": "31-60 (Intermedio)",
                    **metricas_intermedio
                },
                "complejo": {
                    "rango": "61-100 (Complejo)",
                    **metricas_complejo
                }
            },
            "recomendaciones": [
                f"Contenido simple: {len(contenido_simple)} publicaciones ({metricas_simple.get('engagement_rate_promedio', 0):.2f}% engagement promedio)",
                f"Contenido intermedio: {len(contenido_intermedio)} publicaciones ({metricas_intermedio.get('engagement_rate_promedio', 0):.2f}% engagement promedio)",
                f"Contenido complejo: {len(contenido_complejo)} publicaciones ({metricas_complejo.get('engagement_rate_promedio', 0):.2f}% engagement promedio)",
                "Contenido simple suele tener mejor engagement en redes sociales",
                "Balancear complejidad según audiencia objetivo"
            ]
        }
    
    def analizar_contenido_por_interactividad(self) -> Dict[str, Any]:
        """
        Analiza el rendimiento del contenido basado en elementos interactivos.
        
        Returns:
            Diccionario con análisis de rendimiento por interactividad
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        contenido_interactivo = {
            "con_pregunta": [],
            "con_encuesta": [],
            "con_desafio": [],
            "con_llamado_accion": [],
            "con_historia": [],
            "sin_interactividad": []
        }
        
        for pub in self.publicaciones:
            titulo_lower = pub.titulo.lower()
            interactivo = False
            
            # Detectar preguntas
            if '?' in pub.titulo or '¿' in pub.titulo:
                contenido_interactivo["con_pregunta"].append(pub)
                interactivo = True
            
            # Detectar encuestas (palabras clave)
            if any(palabra in titulo_lower for palabra in ["encuesta", "vota", "elige", "prefiere", "cuál prefieres"]):
                contenido_interactivo["con_encuesta"].append(pub)
                interactivo = True
            
            # Detectar desafíos
            if any(palabra in titulo_lower for palabra in ["desafío", "challenge", "reto", "prueba"]):
                contenido_interactivo["con_desafio"].append(pub)
                interactivo = True
            
            # Detectar llamados a acción
            if any(palabra in titulo_lower for palabra in ["comenta", "comparte", "dale like", "guarda", "sígueme"]):
                contenido_interactivo["con_llamado_accion"].append(pub)
                interactivo = True
            
            # Detectar historias
            if any(palabra in titulo_lower for palabra in ["historia", "cuando", "hace", "experiencia", "caso"]):
                contenido_interactivo["con_historia"].append(pub)
                interactivo = True
            
            if not interactivo:
                contenido_interactivo["sin_interactividad"].append(pub)
        
        def calcular_metricas_interactividad(publicaciones):
            if not publicaciones:
                return {}
            return {
                "cantidad": len(publicaciones),
                "engagement_rate_promedio": round(statistics.mean([p.engagement_rate for p in publicaciones]), 2),
                "engagement_score_promedio": round(statistics.mean([p.engagement_score for p in publicaciones]), 2),
                "publicaciones_virales": sum(1 for p in publicaciones if p.es_viral),
                "ratio_comentarios": round(statistics.mean([p.comentarios / p.likes if p.likes > 0 else 0 for p in publicaciones]), 3)
            }
        
        metricas_interactividad = {tipo: calcular_metricas_interactividad(pubs) for tipo, pubs in contenido_interactivo.items()}
        
        # Mejor tipo de interactividad
        mejor_interactividad = max(
            [(tipo, m) for tipo, m in metricas_interactividad.items() if m.get("cantidad", 0) > 0 and tipo != "sin_interactividad"],
            key=lambda x: x[1].get("engagement_rate_promedio", 0),
            default=(None, {})
        )
        
        return {
            "distribucion": {
                **{f"interactividad_{tipo}": {
                    "tipo": tipo.replace("_", " ").title(),
                    **metricas
                } for tipo, metricas in metricas_interactividad.items()}
            },
            "mejor_interactividad": {
                "tipo": mejor_interactividad[0].replace("_", " ").title() if mejor_interactividad[0] else None,
                "metricas": mejor_interactividad[1]
            },
            "recomendaciones": [
                f"Mejor tipo de interactividad: '{mejor_interactividad[0].replace('_', ' ').title()}' con {mejor_interactividad[1].get('engagement_rate_promedio', 0):.2f}% engagement promedio" if mejor_interactividad[0] else "",
                f"Contenido interactivo: {sum(len(pubs) for tipo, pubs in contenido_interactivo.items() if tipo != 'sin_interactividad')} publicaciones",
                "Contenido interactivo genera 2-3x más engagement que contenido pasivo",
                "Preguntas y llamados a acción son los más efectivos"
            ]
        }
    
    def generar_reporte_optimizacion_completo(self) -> Dict[str, Any]:
        """
        Genera un reporte completo de optimización consolidando todos los análisis de contenido.
        
        Returns:
            Diccionario con reporte completo de optimización
        """
        if not self.publicaciones:
            return {"error": "No hay publicaciones para analizar"}
        
        # Ejecutar todos los análisis de contenido
        analisis_completo = self.generar_analisis_completo_contenido()
        analisis_narrativo = self.analizar_contenido_por_tipo_narrativo()
        analisis_palabras = self.analizar_contenido_por_palabras_poderosas()
        analisis_complejidad = self.analizar_contenido_por_complejidad()
        analisis_interactividad = self.analizar_contenido_por_interactividad()
        
        # Consolidar recomendaciones prioritarias
        recomendaciones_prioritarias = []
        
        # Duración de video
        if analisis_completo.get("analisis_detallados", {}).get("duracion_video", {}).get("duracion_optima"):
            duracion_optima = analisis_completo["analisis_detallados"]["duracion_video"]["duracion_optima"]["rango"]
            recomendaciones_prioritarias.append({
                "categoria": "Duración de Video",
                "recomendacion": f"Optimizar duración de video a {duracion_optima}",
                "impacto_esperado": "Alto",
                "prioridad": 1
            })
        
        # CTA
        if analisis_completo.get("analisis_detallados", {}).get("cta", {}).get("mejor_cta"):
            mejor_cta = analisis_completo["analisis_detallados"]["cta"]["mejor_cta"]["tipo"]
            recomendaciones_prioritarias.append({
                "categoria": "CTA",
                "recomendacion": f"Incrementar uso de CTA tipo '{mejor_cta}'",
                "impacto_esperado": "Alto",
                "prioridad": 1
            })
        
        # Hook
        if analisis_completo.get("analisis_detallados", {}).get("hook", {}).get("mejor_hook"):
            mejor_hook = analisis_completo["analisis_detallados"]["hook"]["mejor_hook"]["tipo"]
            recomendaciones_prioritarias.append({
                "categoria": "Hook",
                "recomendacion": f"Implementar hooks tipo '{mejor_hook}' más frecuentemente",
                "impacto_esperado": "Alto",
                "prioridad": 1
            })
        
        # Tipo narrativo
        if analisis_narrativo.get("mejor_tipo_narrativo", {}).get("tipo"):
            mejor_narrativo = analisis_narrativo["mejor_tipo_narrativo"]["tipo"]
            recomendaciones_prioritarias.append({
                "categoria": "Tipo Narrativo",
                "recomendacion": f"Crear más contenido tipo '{mejor_narrativo}'",
                "impacto_esperado": "Medio",
                "prioridad": 2
            })
        
        # Palabras poderosas
        if analisis_palabras.get("mejor_categoria", {}).get("categoria"):
            mejor_categoria = analisis_palabras["mejor_categoria"]["categoria"]
            recomendaciones_prioritarias.append({
                "categoria": "Palabras Poderosas",
                "recomendacion": f"Incrementar uso de palabras de categoría '{mejor_categoria}'",
                "impacto_esperado": "Medio",
                "prioridad": 2
            })
        
        # Interactividad
        if analisis_interactividad.get("mejor_interactividad", {}).get("tipo"):
            mejor_interactividad = analisis_interactividad["mejor_interactividad"]["tipo"]
            recomendaciones_prioritarias.append({
                "categoria": "Interactividad",
                "recomendacion": f"Incrementar contenido con '{mejor_interactividad}'",
                "impacto_esperado": "Alto",
                "prioridad": 1
            })
        
        # Ordenar por prioridad
        recomendaciones_prioritarias.sort(key=lambda x: x["prioridad"])
        
        return {
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "version": "6.0",
                "total_publicaciones": len(self.publicaciones),
                "analisis_incluidos": [
                    "Análisis Completo de Contenido",
                    "Tipo Narrativo",
                    "Palabras Poderosas",
                    "Complejidad",
                    "Interactividad"
                ]
            },
            "analisis_detallados": {
                "contenido_completo": analisis_completo,
                "tipo_narrativo": analisis_narrativo,
                "palabras_poderosas": analisis_palabras,
                "complejidad": analisis_complejidad,
                "interactividad": analisis_interactividad
            },
            "recomendaciones_prioritarias": recomendaciones_prioritarias,
            "resumen_ejecutivo": {
                "total_recomendaciones": len(recomendaciones_prioritarias),
                "recomendaciones_alta_prioridad": len([r for r in recomendaciones_prioritarias if r["prioridad"] == 1]),
                "recomendaciones_media_prioridad": len([r for r in recomendaciones_prioritarias if r["prioridad"] == 2]),
                "impacto_esperado_total": "Alto" if len([r for r in recomendaciones_prioritarias if r["impacto_esperado"] == "Alto"]) > 3 else "Medio"
            }
        }


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Análisis de Engagement de Contenido')
    parser.add_argument('--dias', type=int, default=30, help='Días hacia atrás para analizar')
    parser.add_argument('--db', action='store_true', help='Usar base de datos real en lugar de datos de ejemplo')
    parser.add_argument('--publicaciones', type=int, default=30, help='Número de publicaciones de ejemplo a generar')
    parser.add_argument('--formato', choices=['json', 'html', 'csv', 'pdf', 'excel', 'todos'], default='todos', 
                       help='Formato de salida del reporte')
    parser.add_argument('--output-dir', type=str, default='.', help='Directorio para guardar los reportes')
    parser.add_argument('--predecir', action='store_true', help='Mostrar herramienta de predicción')
    parser.add_argument('--calendario', action='store_true', help='Generar calendario de contenido optimizado')
    parser.add_argument('--roi', action='store_true', help='Incluir análisis de ROI potencial')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ANÁLISIS DE ENGAGEMENT DE CONTENIDO - VERSIÓN MEJORADA")
    print("=" * 80)
    print()
    
    # Crear analizador
    analizador = AnalizadorEngagement()
    
    # Cargar datos
    if args.db:
        try:
            import psycopg2
            # Intentar conectar a la BD (ajustar según tu configuración)
            db_conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'content_marketing'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            analizador.db = db_conn
            print(f"📊 Cargando datos desde base de datos (últimos {args.dias} días)...")
            analizador.cargar_desde_bd(dias_atras=args.dias)
            print(f"✅ {len(analizador.publicaciones)} publicaciones cargadas")
        except Exception as e:
            print(f"⚠️  Error conectando a BD: {e}")
            print("📊 Generando datos de ejemplo...")
            analizador.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
            print(f"✅ {len(analizador.publicaciones)} publicaciones generadas")
    else:
        print("📊 Generando datos de ejemplo del último mes...")
        analizador.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
        print(f"✅ {len(analizador.publicaciones)} publicaciones generadas")
    
    print()
    
    # Generar reporte
    print("🔍 Analizando engagement...")
    reporte = analizador.generar_reporte()
    print()
    
    # Mostrar resultados
    print("=" * 80)
    print("RESUMEN EJECUTIVO")
    print("=" * 80)
    print()
    
    resumen = reporte['resumen_ejecutivo']
    print(f"🏆 TIPO DE CONTENIDO CON MAYOR ENGAGEMENT: {resumen['nombre_tipo']} (Tipo {resumen['tipo_ganador']})")
    print()
    print(f"📈 Métricas Clave:")
    print(f"   • Engagement Rate Promedio: {resumen['engagement_rate_promedio']:.2f}%")
    print(f"   • Engagement Score Promedio: {resumen['engagement_score_promedio']:.1f} puntos")
    if resumen.get('mejor_horario'):
        print(f"   • Mejor Horario: {resumen['mejor_horario']}")
    if resumen.get('mejor_dia'):
        print(f"   • Mejor Día: {resumen['mejor_dia']}")
    if resumen.get('mejor_plataforma'):
        print(f"   • Mejor Plataforma: {resumen['mejor_plataforma']}")
    if resumen.get('tendencia'):
        print(f"   • Tendencia: {resumen['tendencia'].capitalize()} ({resumen.get('cambio_tendencia', 0):+.1f}%)")
    if resumen.get('contenido_viral_porcentaje', 0) > 0:
        print(f"   • Contenido Viral: {resumen['contenido_viral_porcentaje']:.1f}%")
    print()
    
    print("💡 ¿Por qué este tipo obtuvo más engagement?")
    for i, razon in enumerate(resumen['razones_principales'], 1):
        print(f"   {i}. {razon}")
    print()
    
    print("✨ Características Clave:")
    for i, caracteristica in enumerate(resumen['caracteristicas_clave'], 1):
        print(f"   {i}. {caracteristica}")
    print()
    
    # Guardar reportes
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = f"reporte_engagement_{timestamp}"
    
    if args.formato in ['json', 'todos']:
        json_file = os.path.join(args.output_dir, f"{base_name}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Reporte JSON guardado en: {json_file}")
    
    if args.formato in ['html', 'todos']:
        html_file = os.path.join(args.output_dir, f"{base_name}.html")
        analizador.exportar_html(reporte, html_file)
        print(f"✅ Reporte HTML guardado en: {html_file}")
    
    if args.formato in ['csv', 'todos']:
        csv_file = os.path.join(args.output_dir, f"{base_name}.csv")
        analizador.exportar_csv(reporte, csv_file)
        print(f"✅ Reporte CSV guardado en: {csv_file}")
    
    if args.formato in ['pdf', 'todos']:
        try:
            pdf_file = os.path.join(args.output_dir, f"{base_name}.pdf")
            analizador.exportar_pdf(reporte, pdf_file)
            print(f"✅ Reporte PDF guardado en: {pdf_file}")
        except ImportError as e:
            print(f"⚠️  No se pudo generar PDF: {e}")
            print("   Instala reportlab con: pip install reportlab")
    
    if args.formato in ['excel', 'todos']:
        try:
            excel_file = os.path.join(args.output_dir, f"{base_name}.xlsx")
            analizador.exportar_excel(reporte, excel_file)
            print(f"✅ Reporte Excel guardado en: {excel_file}")
        except ImportError as e:
            print(f"⚠️  No se pudo generar Excel: {e}")
            print("   Instala pandas y openpyxl con: pip install pandas openpyxl")
    
    # Generar calendario si se solicita
    if args.calendario:
        print()
        print("=" * 80)
        print("📅 CALENDARIO DE CONTENIDO OPTIMIZADO")
        print("=" * 80)
        calendario = analizador.generar_calendario_optimizado(semanas=4)
        print(f"\n📌 Recomendaciones:")
        print(f"   • Mejor Horario: {calendario['recomendaciones']['mejor_horario']}")
        print(f"   • Mejor Día: {calendario['recomendaciones']['mejor_dia']}")
        print(f"   • Mejor Plataforma: {calendario['recomendaciones']['mejor_plataforma']}")
        print(f"\n📆 Calendario para las próximas {calendario['semanas']} semanas:")
        
        for semana in calendario['calendario']:
            print(f"\n   Semana {semana['semana']} ({semana['fecha_inicio']}):")
            for pub in semana['publicaciones']:
                pred = pub['engagement_predicho']
                print(f"     • {pub['fecha']} {pub['hora']} - {pub['plataforma']}")
                print(f"       Tipo: {pub['tipo_contenido']} | Score Predicho: {pred['engagement_score_predicho']:.1f}")
        
        # Guardar calendario en JSON
        calendario_file = os.path.join(args.output_dir, f"{base_name}_calendario.json")
        with open(calendario_file, 'w', encoding='utf-8') as f:
            json.dump(calendario, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✅ Calendario guardado en: {calendario_file}")
    
    # Análisis de ROI si se solicita
    if args.roi:
        print()
        print("=" * 80)
        print("💰 ANÁLISIS DE ROI POTENCIAL")
        print("=" * 80)
        roi_analisis = analizador.analizar_roi_potencial()
        
        print("\n📊 ROI por Tipo de Contenido:")
        for tipo_key, datos in roi_analisis['roi_por_tipo'].items():
            print(f"\n   {datos['nombre']} (Tipo {tipo_key}):")
            print(f"     • Costo Estimado: ${datos['costo_estimado']:.2f} ({datos['costo_horas']} horas)")
            print(f"     • Valor Generado: ${datos['valor_generado']:.2f}")
            print(f"     • ROI: {datos['roi_porcentaje']:+.1f}%")
            if datos['roi_porcentaje'] < 0:
                print(f"     • Publicaciones necesarias para ROI positivo: {datos['publicaciones_necesarias_para_roi_positivo']}")
        
        print("\n📊 ROI por Plataforma:")
        for plataforma, datos in roi_analisis['roi_por_plataforma'].items():
            print(f"   • {plataforma}: ROI {datos['roi_porcentaje']:+.1f}% (Valor: ${datos['valor_generado']:.2f})")
        
        mejor_roi_tipo = roi_analisis.get('mejor_roi_tipo')
        if mejor_roi_tipo:
            mejor_datos = roi_analisis['roi_por_tipo'][mejor_roi_tipo]
            print(f"\n🏆 Mejor ROI: {mejor_datos['nombre']} con {mejor_datos['roi_porcentaje']:+.1f}%")
        
        # Guardar análisis ROI
        roi_file = os.path.join(args.output_dir, f"{base_name}_roi.json")
        with open(roi_file, 'w', encoding='utf-8') as f:
            json.dump(roi_analisis, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✅ Análisis de ROI guardado en: {roi_file}")
    
    # Mostrar herramienta de predicción si se solicita
    if args.predecir:
        print()
        print("=" * 80)
        print("🔮 HERRAMIENTA DE PREDICCIÓN")
        print("=" * 80)
        print()
        print("Ejemplos de predicción:")
        
        # Ejemplo 1: Tipo X en Facebook, mañana
        pred1 = analizador.predecir_engagement('X', 'Facebook', 10, 'Friday')
        print(f"\n📌 Tipo X en Facebook, Viernes 10:00 AM:")
        print(f"   • Engagement Score Predicho: {pred1['engagement_score_predicho']:.1f}")
        print(f"   • Engagement Rate Predicho: {pred1['engagement_rate_predicho']:.2f}%")
        print(f"   • Confianza: {pred1['confianza']:.1f}% (basado en {pred1['muestra']} publicaciones similares)")
        
        # Ejemplo 2: Tipo Y en Instagram, tarde
        pred2 = analizador.predecir_engagement('Y', 'Instagram', 16, 'Wednesday')
        print(f"\n📌 Tipo Y en Instagram, Miércoles 4:00 PM:")
        print(f"   • Engagement Score Predicho: {pred2['engagement_score_predicho']:.1f}")
        print(f"   • Engagement Rate Predicho: {pred2['engagement_rate_predicho']:.2f}%")
        print(f"   • Confianza: {pred2['confianza']:.1f}% (basado en {pred2['muestra']} publicaciones similares)")
    
    # Mostrar benchmarking
    if reporte.get('benchmarking'):
        print()
        print("=" * 80)
        print("📊 BENCHMARKING VS ESTÁNDARES DE LA INDUSTRIA")
        print("=" * 80)
        bench = reporte['benchmarking']
        print(f"\n{bench['engagement_rate']['emoji']} Engagement Rate: {bench['engagement_rate']['valor']:.2f}%")
        print(f"   Clasificación: {bench['engagement_rate']['clasificacion'].upper()}")
        print(f"   Benchmark Excelente: {bench['engagement_rate']['benchmark_excelente']:.2f}%")
        print(f"   Estás al {bench['engagement_rate']['porcentaje_del_excelente']:.1f}% del nivel excelente")
        
        print(f"\n{bench['engagement_score']['emoji']} Engagement Score: {bench['engagement_score']['valor']:.1f}")
        print(f"   Clasificación: {bench['engagement_score']['clasificacion'].upper()}")
        print(f"   Benchmark Excelente: {bench['engagement_score']['benchmark_excelente']:.1f}")
        print(f"   Estás al {bench['engagement_score']['porcentaje_del_excelente']:.1f}% del nivel excelente")
        
        print(f"\n{bench['contenido_viral']['emoji']} Contenido Viral: {bench['contenido_viral']['valor']:.1f}%")
        print(f"   Clasificación: {bench['contenido_viral']['clasificacion'].upper()}")
        print(f"   Benchmark Excelente: {bench['contenido_viral']['benchmark_excelente']:.1f}%")
        
        print(f"\n🎯 Score General: {bench['score_general']:.1f}% del nivel excelente")
    
    # Mostrar contenido mejorable
    if reporte.get('contenido_mejorable'):
        print()
        print("=" * 80)
        print("🔧 CONTENIDO QUE NECESITA MEJORAS")
        print("=" * 80)
        for i, item in enumerate(reporte['contenido_mejorable'][:5], 1):
            prioridad_emoji = '🔴' if item['prioridad'] == 'ALTA' else '🟡'
            print(f"\n{prioridad_emoji} {i}. {item['titulo']} ({item['plataforma']})")
            print(f"   • Engagement Score: {item['engagement_score']:.1f}")
            print(f"   • Razones: {', '.join(item['razones'][:2])}")
            print(f"   • Mejoras: {', '.join(item['mejoras_sugeridas'][:2])}")
    
    # Mostrar alertas críticas
    if reporte.get('alertas_criticas'):
        print()
        print("=" * 80)
        print("⚠️  ALERTAS CRÍTICAS")
        print("=" * 80)
        for alerta in reporte['alertas_criticas']:
            nivel_emoji = '🔴' if alerta['nivel'] == 'CRÍTICO' else '🟠' if alerta['nivel'] == 'ALTA' else '🟡'
            print(f"\n{nivel_emoji} {alerta['nivel']}: {alerta['titulo']}")
            print(f"   {alerta['mensaje']}")
            print(f"   💡 Acción: {alerta['accion']}")
    
    # Mostrar análisis de IA
    if reporte.get('recomendaciones_ai'):
        print()
        print("=" * 80)
        print("🤖 RECOMENDACIONES INTELIGENTES CON IA")
        print("=" * 80)
        ai_recs = reporte['recomendaciones_ai']
        
        if 'recomendaciones_estrategicas' in ai_recs:
            print("\n📋 Recomendaciones Estratégicas:")
            for i, rec in enumerate(ai_recs['recomendaciones_estrategicas'][:5], 1):
                print(f"   {i}. {rec}")
        
        if 'ideas_contenido' in ai_recs:
            print("\n💡 Ideas de Contenido Generadas por IA:")
            for i, idea in enumerate(ai_recs['ideas_contenido'][:3], 1):
                print(f"\n   {i}. {idea.get('titulo', 'Sin título')}")
                print(f"      • Tipo: {idea.get('tipo', 'N/A')}")
                print(f"      • Plataforma: {idea.get('plataforma', 'N/A')}")
                print(f"      • Horario: {idea.get('horario', 'N/A')}")
                print(f"      • Descripción: {idea.get('descripcion', 'N/A')}")
                if idea.get('hashtags_sugeridos'):
                    print(f"      • Hashtags: {', '.join(idea['hashtags_sugeridos'][:5])}")
        
        if 'insights_clave' in ai_recs:
            print("\n🔍 Insights Clave:")
            for i, insight in enumerate(ai_recs['insights_clave'][:5], 1):
                print(f"   {i}. {insight}")
    
    if reporte.get('analisis_sentimiento_ai'):
        print()
        print("=" * 80)
        print("🎭 ANÁLISIS DE SENTIMIENTO Y CALIDAD (IA)")
        print("=" * 80)
        sentimiento = reporte['analisis_sentimiento_ai']
        
        if 'sentimiento_general' in sentimiento:
            sent_emoji = '😊' if sentimiento['sentimiento_general'] == 'positivo' else '😐' if sentimiento['sentimiento_general'] == 'neutral' else '😟'
            print(f"\n{sent_emoji} Sentimiento General: {sentimiento['sentimiento_general'].upper()}")
        
        if 'temas_recurrentes' in sentimiento:
            print(f"\n📌 Temas Recurrentes: {', '.join(sentimiento['temas_recurrentes'][:5])}")
        
        if 'elementos_exitosos' in sentimiento:
            print(f"\n✅ Elementos Exitosos:")
            for i, elemento in enumerate(sentimiento['elementos_exitosos'][:5], 1):
                print(f"   {i}. {elemento}")
        
        if 'patrones_virales' in sentimiento:
            print(f"\n🔥 Patrones Virales Detectados:")
            for i, patron in enumerate(sentimiento['patrones_virales'][:5], 1):
                print(f"   {i}. {patron}")
    
    if reporte.get('descripcion_insights_ai'):
        print()
        print("=" * 80)
        print("📝 DESCRIPCIÓN NARRATIVA DE INSIGHTS (IA)")
        print("=" * 80)
        print(f"\n{reporte['descripcion_insights_ai']}")
    
    # Mostrar análisis adicional
    if reporte.get('contenido_viral', {}).get('cantidad', 0) > 0:
        print()
        print("=" * 80)
        print("🔥 CONTENIDO VIRAL DETECTADO")
        print("=" * 80)
        viral = reporte['contenido_viral']
        print(f"   • Publicaciones Virales: {viral['cantidad']} ({viral['porcentaje']:.1f}%)")
        print(f"   • Engagement Rate Promedio: {viral['engagement_rate_promedio']:.2f}%")
        if viral.get('tipos_mas_virales'):
            print(f"   • Tipos Más Virales: {', '.join([f'{k} ({v})' for k, v in viral['tipos_mas_virales'].items()])}")
    
    if reporte.get('palabras_clave_efectivas'):
        print()
        print("=" * 80)
        print("🔤 TOP 5 PALABRAS CLAVE MÁS EFECTIVAS")
        print("=" * 80)
        for i, palabra in enumerate(reporte['palabras_clave_efectivas'][:5], 1):
            print(f"   {i}. '{palabra['palabra']}' - Score: {palabra['engagement_score_promedio']:.1f} (usada {palabra['veces_usada']} veces)")
    
    # Mostrar recomendaciones de hashtags optimizados
    if reporte.get('hashtags_optimizados'):
        print()
        print("=" * 80)
        print("🎯 HASHTAGS OPTIMIZADOS POR TIPO DE CONTENIDO")
        print("=" * 80)
        
        tipo_nombres = {
            'X': 'Tutoriales/Educativos',
            'Y': 'Entretenimiento/Viral',
            'Z': 'Promocional/Producto'
        }
        
        for tipo, recomendacion in reporte['hashtags_optimizados'].items():
            print(f"\n📌 Tipo {tipo} ({tipo_nombres.get(tipo, tipo)}):")
            print(f"   • Publicaciones analizadas: {recomendacion['total_publicaciones']}")
            print(f"   • Engagement promedio: {recomendacion['engagement_promedio']:.1f}")
            
            if recomendacion.get('hashtags_historicos_efectivos'):
                print(f"\n   ✅ Hashtags Históricos Más Efectivos:")
                for i, h in enumerate(recomendacion['hashtags_historicos_efectivos'][:3], 1):
                    print(f"      {i}. {h['hashtag']} - Score: {h['engagement_score_promedio']:.1f} (usado {h['veces_usado']} veces)")
            
            if recomendacion.get('hashtags_optimizados_nuevos'):
                print(f"\n   🚀 Hashtags Optimizados Nuevos (Generados con IA):")
                hashtags_nuevos = [h for h in recomendacion['hashtags_optimizados_nuevos'] if h.get('recomendado')]
                for i, h in enumerate(hashtags_nuevos[:5], 1):
                    uso_info = f" (usado {h['uso_historico']} veces)" if h.get('uso_historico', 0) > 0 else " (nuevo)"
                    score_info = f" - Score histórico: {h['engagement_score_promedio']:.1f}" if h.get('engagement_score_promedio') else ""
                    print(f"      {i}. {h['hashtag']}{uso_info}{score_info}")
    
    # Mostrar hashtags por plataforma
    if reporte.get('hashtags_por_plataforma'):
        print()
        print("=" * 80)
        print("📱 HASHTAGS MÁS EFECTIVOS POR PLATAFORMA")
        print("=" * 80)
        for plataforma, hashtags in reporte['hashtags_por_plataforma'].items():
            if hashtags:
                print(f"\n📌 {plataforma}:")
                for i, h in enumerate(hashtags[:5], 1):
                    print(f"   {i}. {h['hashtag']} - Score: {h['engagement_score_promedio']:.1f} (Rate: {h['engagement_rate_promedio']:.2f}%)")
    
    # Mostrar anomalías detectadas
    if reporte.get('anomalias_engagement'):
        print()
        print("=" * 80)
        print("🔍 ANOMALÍAS DE ENGAGEMENT DETECTADAS")
        print("=" * 80)
        anomalias = reporte['anomalias_engagement']
        print(f"\n   Total de anomalías: {len(anomalias)}")
        
        anomalias_altas = [a for a in anomalias if a['tipo'] == 'alto']
        anomalias_bajas = [a for a in anomalias if a['tipo'] == 'bajo']
        
        if anomalias_altas:
            print(f"\n   🔥 Anomalías Altas (Engagement Excepcional): {len(anomalias_altas)}")
            for i, a in enumerate(anomalias_altas[:3], 1):
                print(f"      {i}. {a['titulo']} - Score: {a['engagement_score']:.1f} (z-score: {a['z_score']:.2f})")
        
        if anomalias_bajas:
            print(f"\n   ⚠️  Anomalías Bajas (Necesitan Mejora): {len(anomalias_bajas)}")
            for i, a in enumerate(anomalias_bajas[:3], 1):
                print(f"      {i}. {a['titulo']} - Score: {a['engagement_score']:.1f} (z-score: {a['z_score']:.2f})")
    
    # Mostrar clustering de contenido
    if reporte.get('clustering_contenido') and 'error' not in reporte['clustering_contenido']:
        print()
        print("=" * 80)
        print("🎯 CLUSTERING DE CONTENIDO (ML)")
        print("=" * 80)
        clusters = reporte['clustering_contenido']
        print(f"\n   Clusters identificados: {clusters['n_clusters']}")
        
        for cluster_name, datos in clusters['clusters'].items():
            print(f"\n   📊 {cluster_name.upper()}:")
            print(f"      • Tamaño: {datos['tamaño']} publicaciones")
            print(f"      • Engagement Score Promedio: {datos['engagement_score_promedio']:.1f}")
            print(f"      • Engagement Rate Promedio: {datos['engagement_rate_promedio']:.2f}%")
            print(f"      • Tipo más común: {datos['tipos_contenido'].most_common(1)[0][0] if datos['tipos_contenido'] else 'N/A'}")
            print(f"      • Plataforma más común: {datos['plataformas'].most_common(1)[0][0] if datos['plataformas'] else 'N/A'}")
    
    # Mostrar estrategia optimizada
    if reporte.get('estrategia_optimizada'):
        print()
        print("=" * 80)
        print("🚀 ESTRATEGIA DE CONTENIDO OPTIMIZADA")
        print("=" * 80)
        estrategia = reporte['estrategia_optimizada']
        print(f"\n   Basado en análisis de {estrategia['basado_en']} publicaciones")
        
        for i, rec in enumerate(estrategia['recomendaciones'], 1):
            prioridad_emoji = '🔴' if rec['prioridad'] == 'Alta' else '🟡' if rec['prioridad'] == 'Media' else '🟢'
            impacto_emoji = '🔥' if rec['impacto_esperado'] == 'Alto' else '📈' if rec['impacto_esperado'] == 'Medio' else '📊'
            
            print(f"\n   {prioridad_emoji} {i}. {rec['categoria']} ({impacto_emoji} {rec['impacto_esperado']}):")
            print(f"      Recomendación: {rec['recomendacion']}")
            print(f"      Razón: {rec['razon']}")
            print(f"      Acción: {rec['accion']}")
        
        if estrategia.get('prediccion_ml'):
            pred = estrategia['prediccion_ml']
            print(f"\n   🤖 Predicción ML:")
            print(f"      • Engagement Esperado: {pred['engagement_esperado']:.1f}")
            print(f"      • Confianza: {pred['confianza']:.1f}%")
            if pred.get('factores_clave'):
                print(f"      • Factores Clave:")
                for factor in pred['factores_clave']:
                    print(f"        - {factor['factor']}: {factor['importancia']:.2%}")
        
        if estrategia.get('roi_esperado'):
            roi = estrategia['roi_esperado']
            print(f"\n   💰 ROI Esperado:")
            print(f"      • Mejora de Engagement: {roi['mejora_engagement']}")
            print(f"      • Publicaciones Necesarias: {roi['publicaciones_necesarias']}")
            print(f"      • Tiempo Estimado: {roi['tiempo_estimado']}")
    
    # Mostrar análisis específico de LinkedIn
    if reporte.get('analisis_linkedin'):
        print()
        print("=" * 80)
        print("💼 ANÁLISIS ESPECÍFICO DE LINKEDIN")
        print("=" * 80)
        linkedin = reporte['analisis_linkedin']
        
        print(f"\n📊 Resumen:")
        print(f"   • Total posts LinkedIn: {linkedin.get('total_posts_linkedin', 0)}")
        print(f"   • Engagement promedio: {linkedin.get('engagement_promedio_linkedin', 0):.2f}%")
        
        if linkedin.get('mejor_post_linkedin'):
            mejor = linkedin['mejor_post_linkedin']
            print(f"\n🏆 Mejor Post LinkedIn:")
            print(f"   • Engagement Rate: {mejor['engagement_rate']:.2f}%")
            print(f"   • Título: {mejor['titulo'][:100]}...")
            print(f"   • Hashtags: {', '.join(mejor['hashtags'][:5])}")
        
        if linkedin.get('longitud_optima'):
            print(f"\n📏 Longitud Óptima:")
            mejor_long = max(linkedin['longitud_optima'].items(), 
                           key=lambda x: x[1]['engagement_promedio'])
            print(f"   • {mejor_long[0]}: {mejor_long[1]['engagement_promedio']:.2f}% engagement")
        
        if linkedin.get('estructura_posts'):
            estructura = linkedin['estructura_posts']
            if estructura.get('completo', {}).get('engagement_promedio', 0) > 0:
                print(f"\n✅ Estructura Completa (Hook + CTA + Pregunta):")
                print(f"   • Engagement: {estructura['completo']['engagement_promedio']:.2f}%")
                print(f"   • Posts con estructura completa: {estructura['completo'].get('cantidad', 0)}")
        
        if linkedin.get('hashtags_optimo'):
            mejor_hashtags = max(linkedin['hashtags_optimo'].items(),
                               key=lambda x: x[1]['engagement_promedio'])
            print(f"\n#️⃣ Hashtags Óptimos:")
            print(f"   • {mejor_hashtags[0]} hashtags: {mejor_hashtags[1]['engagement_promedio']:.2f}% engagement")
        
        if linkedin.get('horarios_linkedin'):
            horarios = linkedin['horarios_linkedin']
            if 'optimo' in horarios and 'suboptimo' in horarios:
                diff = horarios['optimo']['engagement_promedio'] - horarios['suboptimo']['engagement_promedio']
                print(f"\n⏰ Horarios:")
                print(f"   • Óptimos (8-10 AM, 12-1 PM, 5-6 PM): {horarios['optimo']['engagement_promedio']:.2f}%")
                print(f"   • Subóptimos: {horarios['suboptimo']['engagement_promedio']:.2f}%")
                print(f"   • Diferencia: +{diff:.2f}%")
        
        if linkedin.get('formato_analisis'):
            mejor_formato = max(linkedin['formato_analisis'].items(),
                              key=lambda x: x[1]['engagement_promedio'])
            print(f"\n🎨 Formato Más Efectivo:")
            print(f"   • {mejor_formato[0].capitalize()}: {mejor_formato[1]['engagement_promedio']:.2f}% engagement")
    
    # Mostrar recomendaciones específicas de LinkedIn
    if reporte.get('recomendaciones_linkedin'):
        print()
        print("=" * 80)
        print("💡 RECOMENDACIONES ESPECÍFICAS PARA LINKEDIN")
        print("=" * 80)
        for i, rec in enumerate(reporte['recomendaciones_linkedin'], 1):
            prioridad_emoji = '🔴' if rec['prioridad'] == 'Alta' else '🟡'
            print(f"\n{prioridad_emoji} {i}. {rec['categoria']}:")
            print(f"   • Recomendación: {rec['recomendacion']}")
            print(f"   • Razón: {rec['razon']}")
            print(f"   • Acción: {rec['accion']}")
    
    # Mostrar ideas de contenido basadas en tendencias
    if reporte.get('ideas_contenido_tendencias'):
        print()
        print("=" * 80)
        print("💡 IDEAS DE CONTENIDO BASADAS EN TENDENCIAS")
        print("=" * 80)
        ideas = reporte['ideas_contenido_tendencias']
        print(f"\n   Total de ideas generadas: {len(ideas)}")
        for i, idea in enumerate(ideas[:5], 1):
            print(f"\n   {i}. {idea.get('titulo_sugerido', 'Sin título')}")
            print(f"      • Tipo: {idea.get('nombre_tipo', idea.get('tipo_contenido', 'N/A'))}")
            print(f"      • Plataforma: {idea.get('plataforma', 'N/A')}")
            print(f"      • Engagement Esperado: {idea.get('engagement_esperado', 0):.1f} (Confianza: {idea.get('confianza', 0):.1f}%)")
            if idea.get('hashtags_sugeridos'):
                print(f"      • Hashtags: {', '.join(idea.get('hashtags_sugeridos', [])[:3])}")
            print(f"      • Horario Óptimo: {idea.get('horario_optimo', 'N/A')}")
    
    # Mostrar sistema de alertas
    if reporte.get('alertas_sistema'):
        print()
        print("=" * 80)
        print("🚨 SISTEMA DE ALERTAS INTELIGENTES")
        print("=" * 80)
        alertas = reporte['alertas_sistema']
        print(f"\n   Total de alertas: {alertas.get('total_alertas', 0)}")
        print(f"   Alertas críticas: {alertas.get('alertas_criticas', 0)}")
        
        for alerta in alertas.get('alertas', [])[:5]:
            tipo_emoji = '🔴' if alerta['tipo'] == 'CRÍTICA' else '🟠' if alerta['tipo'] == 'ALTA' else '🟡'
            print(f"\n   {tipo_emoji} {alerta['titulo']}")
            print(f"      {alerta['mensaje']}")
            print(f"      💡 Acción: {alerta['accion']}")
    
    # Mostrar plan de acción para mejora
    if reporte.get('plan_accion_mejora') and 'error' not in reporte['plan_accion_mejora']:
        print()
        print("=" * 80)
        print("📋 PLAN DE ACCIÓN PARA MEJORA")
        print("=" * 80)
        plan = reporte['plan_accion_mejora']
        
        if plan.get('acciones_prioritarias'):
            print(f"\n   🔴 ACCIONES PRIORITARIAS ({len(plan['acciones_prioritarias'])}):")
            for i, accion in enumerate(plan['acciones_prioritarias'], 1):
                impacto_emoji = '🔥' if accion['impacto_esperado'] == 'Alto' else '📈'
                print(f"\n   {i}. {impacto_emoji} {accion['accion']}")
                print(f"      • Impacto: {accion['impacto_esperado']}")
                print(f"      • Tiempo: {accion['tiempo_estimado']}")
                print(f"      • Dificultad: {accion['dificultad']}")
                print(f"      • Razón: {accion['razon']}")
        
        if plan.get('acciones_secundarias'):
            print(f"\n   🟡 ACCIONES SECUNDARIAS ({len(plan['acciones_secundarias'])}):")
            for i, accion in enumerate(plan['acciones_secundarias'], 1):
                print(f"\n   {i}. {accion['accion']}")
                print(f"      • Impacto: {accion['impacto_esperado']}")
                print(f"      • Tiempo: {accion['tiempo_estimado']}")
        
        if plan.get('metricas_objetivo'):
            metricas = plan['metricas_objetivo']
            print(f"\n   🎯 MÉTRICAS OBJETIVO:")
            print(f"      • Engagement Rate: {metricas.get('engagement_rate_actual', 0):.2f}% → {metricas.get('engagement_rate_objetivo', 0):.2f}%")
            print(f"      • Engagement Score: {metricas.get('engagement_score_actual', 0):.1f} → {metricas.get('engagement_score_objetivo', 0):.1f}")
            print(f"      • Mejora Esperada: {metricas.get('mejora_esperada_porcentual', 0):.0f}%")
    
    print()
    print("=" * 80)
    print("✅ Análisis completado")
    print("=" * 80)


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.0
# ============================================================================

def generar_contenido_optimizado(self, tema: str, tipo_contenido: str = 'X', plataforma: str = 'LinkedIn') -> Dict[str, Any]:
    """
    Genera contenido optimizado basado en análisis de posts exitosos.
    
    Args:
        tema: Tema principal del contenido
        tipo_contenido: Tipo de contenido (X, Y, Z)
        plataforma: Plataforma objetivo
        
    Returns:
        Contenido optimizado con estructura completa
    """
    # Analizar posts exitosos del mismo tipo
    posts_exitosos = [p for p in self.publicaciones 
                     if p.tipo_contenido == tipo_contenido and p.plataforma.lower() == plataforma.lower()]
    
    if not posts_exitosos:
        posts_exitosos = [p for p in self.publicaciones if p.tipo_contenido == tipo_contenido]
    
    # Extraer patrones de posts exitosos
    patrones = {
        'longitud_promedio': statistics.mean([len(p.titulo) for p in posts_exitosos]) if posts_exitosos else 1200,
        'hashtags_promedio': statistics.mean([len(p.hashtags) for p in posts_exitosos]) if posts_exitosos else 6,
        'hashtags_comunes': Counter([h for p in posts_exitosos for h in p.hashtags]).most_common(10),
        'palabras_clave': Counter([palabra for p in posts_exitosos 
                                  for palabra in p.titulo.lower().split() 
                                  if len(palabra) > 4]).most_common(15)
    }
    
    # Generar estructura optimizada
    longitud_objetivo = int(patrones['longitud_promedio'])
    if plataforma.lower() == 'linkedin':
        longitud_objetivo = max(1000, min(1500, longitud_objetivo))
    
    # Generar hook basado en posts exitosos
    hooks_exitosos = [p.titulo[:125] for p in posts_exitosos if hasattr(self, '_tiene_hook_efectivo') and self._tiene_hook_efectivo(p.titulo)]
    hook_template = hooks_exitosos[0] if hooks_exitosos else f"El problema que enfrentan profesionales en {tema}"
    
    # Generar hashtags optimizados
    hashtags_sugeridos = [h[0] for h in patrones['hashtags_comunes'][:7]]
    if len(hashtags_sugeridos) < 5:
        hashtags_sugeridos.extend([f"#{tema.lower()}", "#Innovación", "#Estrategia", "#Liderazgo"])
    
    return {
        'tema': tema,
        'tipo_contenido': tipo_contenido,
        'plataforma': plataforma,
        'estructura_sugerida': {
            'hook': hook_template,
            'longitud_objetivo': longitud_objetivo,
            'hashtags_sugeridos': hashtags_sugeridos[:7],
            'palabras_clave': [p[0] for p in patrones['palabras_clave'][:10]]
        },
        'patrones_extraidos': patrones,
        'recomendaciones': [
            f"Usa longitud de {longitud_objetivo} caracteres",
            f"Incluye {len(hashtags_sugeridos)} hashtags relevantes",
            "Agrega hook en primeras 125 caracteres",
            "Incluye CTA claro",
            "Termina con pregunta para engagement"
        ]
    }


def analizar_ab_test(self, variacion_a: Dict[str, Any], variacion_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza resultados de A/B testing entre dos variaciones de contenido.
    
    Args:
        variacion_a: Métricas de variación A {'titulo', 'hashtags', 'engagement_rate', 'impresiones'}
        variacion_b: Métricas de variación B
        
    Returns:
        Análisis estadístico del A/B test
    """
    # Calcular métricas básicas
    engagement_a = variacion_a.get('engagement_rate', 0)
    engagement_b = variacion_b.get('engagement_rate', 0)
    impresiones_a = variacion_a.get('impresiones', 0)
    impresiones_b = variacion_b.get('impresiones', 0)
    
    # Calcular diferencia
    diferencia = engagement_b - engagement_a
    diferencia_porcentual = ((engagement_b - engagement_a) / engagement_a * 100) if engagement_a > 0 else 0
    
    # Determinar ganador
    if engagement_b > engagement_a:
        ganador = 'B'
        mejora = diferencia_porcentual
    elif engagement_a > engagement_b:
        ganador = 'A'
        mejora = -diferencia_porcentual
    else:
        ganador = 'Empate'
        mejora = 0
    
    # Calcular significancia estadística
    total_impresiones = impresiones_a + impresiones_b
    significativo = total_impresiones > 1000 and abs(diferencia) > 0.5
    
    # Calcular scores si están disponibles
    score_a = None
    score_b = None
    if hasattr(self, 'calcular_score_optimizacion') and variacion_a.get('titulo'):
        try:
            score_a = self.calcular_score_optimizacion(variacion_a.get('titulo', ''), variacion_a.get('hashtags', []))
        except:
            pass
    if hasattr(self, 'calcular_score_optimizacion') and variacion_b.get('titulo'):
        try:
            score_b = self.calcular_score_optimizacion(variacion_b.get('titulo', ''), variacion_b.get('hashtags', []))
        except:
            pass
    
    return {
        'variacion_a': {
            'engagement_rate': engagement_a,
            'impresiones': impresiones_a,
            'score': score_a
        },
        'variacion_b': {
            'engagement_rate': engagement_b,
            'impresiones': impresiones_b,
            'score': score_b
        },
        'resultado': {
            'ganador': ganador,
            'diferencia_absoluta': abs(diferencia),
            'diferencia_porcentual': abs(diferencia_porcentual),
            'mejora': mejora,
            'significativo': significativo
        },
        'recomendacion': f"Usa variación {ganador} - {'Mejora significativa' if significativo else 'Diferencia no significativa'}"
    }


def generar_calendario_linkedin(self, semanas: int = 4) -> Dict[str, Any]:
    """
    Genera calendario optimizado específico para LinkedIn.
    
    Args:
        semanas: Número de semanas a planificar
        
    Returns:
        Calendario con posts optimizados para LinkedIn
    """
    # Analizar mejores prácticas de LinkedIn
    analisis_linkedin = {}
    try:
        if hasattr(self, 'analizar_linkedin_especifico'):
            analisis_linkedin = self.analizar_linkedin_especifico()
    except:
        pass
    
    # Horarios óptimos LinkedIn
    horarios_optimos = {
        'Lunes': ['8:00', '12:00'],
        'Martes': ['8:00', '12:00', '17:00'],
        'Miércoles': ['8:00', '12:00', '17:00'],
        'Jueves': ['8:00', '12:00', '17:00'],
        'Viernes': ['8:00', '12:00']
    }
    
    # Tipos de contenido por día
    tipos_por_dia = {
        'Lunes': 'Educativo/Informativo',
        'Martes': 'Caso de Éxito',
        'Miércoles': 'Pregunta/Engagement',
        'Jueves': 'Insights/Estadísticas',
        'Viernes': 'Inspiracional/Ligero'
    }
    
    calendario = []
    fecha_inicio = datetime.now()
    
    for semana in range(semanas):
        semana_calendario = {
            'semana': semana + 1,
            'fecha_inicio': (fecha_inicio + timedelta(weeks=semana)).strftime('%Y-%m-%d'),
            'posts': []
        }
        
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for dia in dias_semana:
            fecha = fecha_inicio + timedelta(weeks=semana, days=dias_semana.index(dia))
            
            # Seleccionar mejor horario
            horarios_dia = horarios_optimos.get(dia, ['8:00'])
            mejor_horario = horarios_dia[0] if horarios_dia else '8:00'
            
            semana_calendario['posts'].append({
                'dia': dia,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'horario': mejor_horario,
                'tipo_contenido': tipos_por_dia.get(dia, 'General'),
                'recomendaciones': [
                    f"Publicar a las {mejor_horario}",
                    f"Tipo: {tipos_por_dia.get(dia, 'General')}",
                    "Incluir Hook + CTA + Pregunta",
                    "Usar 5-7 hashtags relevantes"
                ]
            })
        
        calendario.append(semana_calendario)
    
    return {
        'calendario': calendario,
        'total_posts': semanas * 5,
        'recomendaciones_generales': [
            'Publica 3-5 veces por semana para máximo engagement',
            'Mejores días: Martes, Miércoles, Jueves',
            'Mejores horarios: 8-10 AM, 12-1 PM, 5-6 PM',
            'Varía tipos de contenido para mantener interés',
            'Responde a comentarios en primeras 2 horas'
        ],
        'analisis_base': analisis_linkedin
    }


def generar_plan_accion_mejora(self) -> Dict[str, Any]:
    """Genera un plan de acción específico para mejorar el engagement."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    plan_accion = {'fecha_generacion': datetime.now().isoformat(), 'acciones_prioritarias': [], 'acciones_secundarias': [], 'metricas_objetivo': {}}
    engagement_actual = statistics.mean([p.engagement_rate for p in self.publicaciones])
    engagement_score_actual = statistics.mean([p.engagement_score for p in self.publicaciones])
    mejor_tipo = self.identificar_mejor_tipo()
    mejor_plataforma = max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else None
    tipo_actual_distribucion = Counter([p.tipo_contenido for p in self.publicaciones])
    tipo_mas_usado = tipo_actual_distribucion.most_common(1)[0][0] if tipo_actual_distribucion else None
    if tipo_mas_usado != mejor_tipo['tipo']:
        plan_accion['acciones_prioritarias'].append({'accion': f"Cambiar enfoque de tipo {tipo_mas_usado} a tipo {mejor_tipo['tipo']}", 'impacto_esperado': 'Alto', 'tiempo_estimado': '2 semanas', 'dificultad': 'Media', 'razon': f"El tipo {mejor_tipo['tipo']} tiene {mejor_tipo['datos']['engagement_score_promedio']:.1f} vs {statistics.mean([p.engagement_score for p in self.publicaciones if p.tipo_contenido == tipo_mas_usado]):.1f}"})
    horarios_optimos = self.analizar_horarios_optimos()
    mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios_optimos else None
    horarios_actuales = Counter([p.metadata.get('hora_publicacion', p.fecha_publicacion.hour) for p in self.publicaciones])
    hora_mas_usada = horarios_actuales.most_common(1)[0][0] if horarios_actuales else None
    if mejor_horario and hora_mas_usada:
        hora_match = re.search(r'(\d{2}):\d{2}', mejor_horario)
        hora_optima = int(hora_match.group(1)) if hora_match else None
        if hora_optima and abs(hora_mas_usada - hora_optima) > 2:
            plan_accion['acciones_prioritarias'].append({'accion': f"Ajustar horario de publicación de {hora_mas_usada}:00 a {hora_optima}:00", 'impacto_esperado': 'Medio', 'tiempo_estimado': '1 semana', 'dificultad': 'Baja', 'razon': f"El horario {mejor_horario} tiene mejor engagement"})
    hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=5)
    hashtags_actuales = Counter([h.lower() for p in self.publicaciones for h in p.hashtags])
    hashtags_mas_usados = [h[0] for h in hashtags_actuales.most_common(5)]
    hashtags_recomendados = [h['hashtag'].lower() for h in hashtags_efectivos[:5]]
    hashtags_faltantes = [h for h in hashtags_recomendados if h not in hashtags_mas_usados]
    if hashtags_faltantes:
        plan_accion['acciones_secundarias'].append({'accion': f"Incorporar hashtags efectivos: {', '.join(hashtags_faltantes[:3])}", 'impacto_esperado': 'Medio', 'tiempo_estimado': 'Inmediato', 'dificultad': 'Baja', 'razon': 'Estos hashtags tienen mejor engagement histórico'})
    contenido_viral = self.detectar_contenido_viral()
    if contenido_viral.get('porcentaje', 0) < 10:
        plan_accion['acciones_secundarias'].append({'accion': 'Aumentar contenido viral analizando características de contenido exitoso', 'impacto_esperado': 'Alto', 'tiempo_estimado': '1 mes', 'dificultad': 'Media', 'razon': f"Solo {contenido_viral.get('porcentaje', 0):.1f}% del contenido es viral"})
    objetivo_engagement_rate = engagement_actual * 1.2
    objetivo_engagement_score = engagement_score_actual * 1.15
    plan_accion['metricas_objetivo'] = {'engagement_rate_actual': engagement_actual, 'engagement_rate_objetivo': objetivo_engagement_rate, 'engagement_score_actual': engagement_score_actual, 'engagement_score_objetivo': objetivo_engagement_score, 'mejora_esperada_porcentual': 20}
    return plan_accion


def analizar_retencion_audiencia(self) -> Dict[str, Any]:
    """Analiza la retención de audiencia basada en engagement repetido."""
    if len(self.publicaciones) < 15:
        return {'error': 'Se necesitan al menos 15 publicaciones'}
    publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
    engagement_por_periodo = defaultdict(list)
    periodo_actual = 0
    fecha_inicio_periodo = publicaciones_ordenadas[0].fecha_publicacion
    for pub in publicaciones_ordenadas:
        dias_desde_inicio = (pub.fecha_publicacion - fecha_inicio_periodo).days
        periodo = dias_desde_inicio // 7
        engagement_por_periodo[periodo].append(pub.engagement_score)
    retencion_analisis = []
    periodo_anterior = None
    for periodo in sorted(engagement_por_periodo.keys()):
        engagement_promedio = statistics.mean(engagement_por_periodo[periodo])
        if periodo_anterior is not None:
            engagement_anterior = statistics.mean(engagement_por_periodo[periodo_anterior])
            retencion = (engagement_promedio / engagement_anterior * 100) if engagement_anterior > 0 else 100
            retencion_analisis.append({'periodo': periodo, 'engagement_promedio': engagement_promedio, 'retencion_porcentual': retencion, 'tendencia': 'mejorando' if retencion > 100 else 'decreciendo' if retencion < 90 else 'estable'})
        periodo_anterior = periodo
    retencion_promedio = statistics.mean([r['retencion_porcentual'] for r in retencion_analisis]) if retencion_analisis else 100
    return {'retencion_por_periodo': retencion_analisis, 'retencion_promedio': retencion_promedio, 'tendencia_general': 'mejorando' if retencion_promedio > 100 else 'decreciendo' if retencion_promedio < 90 else 'estable', 'recomendacion': 'Mantener estrategia actual' if retencion_promedio > 100 else 'Revisar cambios recientes en contenido'}


def optimizar_distribucion_tipos(self, objetivo_engagement: float = None) -> Dict[str, Any]:
    """Optimiza la distribución de tipos de contenido para alcanzar un objetivo."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    analisis_tipos = self.analizar_por_tipo()
    if objetivo_engagement is None:
        objetivo_engagement = statistics.mean([p.engagement_score for p in self.publicaciones]) * 1.2
    distribucion_actual = {tipo: datos['cantidad_publicaciones'] for tipo, datos in analisis_tipos.items()}
    total_actual = sum(distribucion_actual.values())
    distribucion_optima = {}
    mejor_tipo = self.identificar_mejor_tipo()
    engagement_por_tipo = {tipo: datos['engagement_score_promedio'] for tipo, datos in analisis_tipos.items()}
    mejor_tipo_key = mejor_tipo['tipo']
    mejor_engagement = engagement_por_tipo.get(mejor_tipo_key, 0)
    otros_tipos = {k: v for k, v in engagement_por_tipo.items() if k != mejor_tipo_key}
    segundo_mejor = max(otros_tipos.items(), key=lambda x: x[1]) if otros_tipos else None
    if segundo_mejor:
        distribucion_optima[mejor_tipo_key] = {'porcentaje': 50, 'publicaciones': int(total_actual * 0.5), 'engagement_esperado': mejor_engagement}
        distribucion_optima[segundo_mejor[0]] = {'porcentaje': 30, 'publicaciones': int(total_actual * 0.3), 'engagement_esperado': segundo_mejor[1]}
        tercer_tipo = [k for k in engagement_por_tipo.keys() if k != mejor_tipo_key and k != segundo_mejor[0]]
        if tercer_tipo:
            tercer_engagement = engagement_por_tipo.get(tercer_tipo[0], 0)
            distribucion_optima[tercer_tipo[0]] = {'porcentaje': 20, 'publicaciones': int(total_actual * 0.2), 'engagement_esperado': tercer_engagement}
    else:
        distribucion_optima[mejor_tipo_key] = {'porcentaje': 100, 'publicaciones': total_actual, 'engagement_esperado': mejor_engagement}
    engagement_esperado_total = sum(d['publicaciones'] * d['engagement_esperado'] for d in distribucion_optima.values()) / total_actual if total_actual > 0 else 0
    return {'distribucion_actual': distribucion_actual, 'distribucion_optima': distribucion_optima, 'objetivo_engagement': objetivo_engagement, 'engagement_esperado': engagement_esperado_total, 'mejora_esperada': ((engagement_esperado_total - statistics.mean([p.engagement_score for p in self.publicaciones])) / statistics.mean([p.engagement_score for p in self.publicaciones]) * 100) if self.publicaciones else 0, 'recomendacion': f"Redistribuir contenido: {mejor_tipo_key} 50%, otros tipos 50%"}


def analizar_eficacia_cta(self) -> Dict[str, Any]:
    """Analiza la eficacia de CTAs (Call to Actions) en títulos."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    ctas_comunes = ['comenta', 'comparte', 'like', 'sigue', 'descubre', 'aprende', 'mira', 'prueba', 'descarga', 'suscríbete', 'envía', 'contacta']
    cta_engagement = defaultdict(list)
    for pub in self.publicaciones:
        titulo_lower = pub.titulo.lower()
        for cta in ctas_comunes:
            if cta in titulo_lower:
                cta_engagement[cta].append(pub.engagement_score)
    cta_analisis = []
    for cta, scores in cta_engagement.items():
        if len(scores) >= 2:
            cta_analisis.append({'cta': cta, 'veces_usado': len(scores), 'engagement_promedio': statistics.mean(scores), 'engagement_mediana': statistics.median(scores)})
    cta_analisis.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_cta = cta_analisis[0] if cta_analisis else None
    return {'ctas_analizados': cta_analisis, 'mejor_cta': mejor_cta, 'recomendacion': f"Usar CTA '{mejor_cta['cta']}' más frecuentemente" if mejor_cta else "No se detectaron CTAs significativos"}


def generar_benchmark_personalizado(self, metricas_objetivo: Dict[str, float] = None) -> Dict[str, Any]:
    """Genera un benchmark personalizado basado en objetivos específicos."""
    if metricas_objetivo is None:
        metricas_objetivo = {'engagement_rate': 5.0, 'engagement_score': 150.0, 'contenido_viral_porcentaje': 15.0}
    engagement_rate_actual = statistics.mean([p.engagement_rate for p in self.publicaciones])
    engagement_score_actual = statistics.mean([p.engagement_score for p in self.publicaciones])
    contenido_viral_actual = (sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones) * 100) if self.publicaciones else 0
    gaps = {'engagement_rate': metricas_objetivo['engagement_rate'] - engagement_rate_actual, 'engagement_score': metricas_objetivo['engagement_score'] - engagement_score_actual, 'contenido_viral': metricas_objetivo['contenido_viral_porcentaje'] - contenido_viral_actual}
    porcentajes_objetivo = {'engagement_rate': (engagement_rate_actual / metricas_objetivo['engagement_rate'] * 100) if metricas_objetivo['engagement_rate'] > 0 else 0, 'engagement_score': (engagement_score_actual / metricas_objetivo['engagement_score'] * 100) if metricas_objetivo['engagement_score'] > 0 else 0, 'contenido_viral': (contenido_viral_actual / metricas_objetivo['contenido_viral_porcentaje'] * 100) if metricas_objetivo['contenido_viral_porcentaje'] > 0 else 0}
    return {'metricas_actuales': {'engagement_rate': engagement_rate_actual, 'engagement_score': engagement_score_actual, 'contenido_viral_porcentaje': contenido_viral_actual}, 'metricas_objetivo': metricas_objetivo, 'gaps': gaps, 'porcentaje_objetivo': porcentajes_objetivo, 'score_general': statistics.mean(list(porcentajes_objetivo.values())), 'recomendaciones': [f"Aumentar engagement rate en {gaps['engagement_rate']:.2f}%" if gaps['engagement_rate'] > 0 else 'Engagement rate objetivo alcanzado', f"Aumentar engagement score en {gaps['engagement_score']:.1f}" if gaps['engagement_score'] > 0 else 'Engagement score objetivo alcanzado', f"Aumentar contenido viral en {gaps['contenido_viral']:.1f}%" if gaps['contenido_viral'] > 0 else 'Contenido viral objetivo alcanzado']}


def analizar_contenido_evergreen_vs_trending(self) -> Dict[str, Any]:
    """Analiza la diferencia entre contenido evergreen y trending."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_evergreen = []
    contenido_trending = []
    fecha_actual = datetime.now()
    for pub in self.publicaciones:
        dias_desde_publicacion = (fecha_actual - pub.fecha_publicacion).days
        engagement_reciente = pub.engagement_score if dias_desde_publicacion <= 7 else 0
        engagement_total = pub.engagement_score
        ratio_reciente = engagement_reciente / engagement_total if engagement_total > 0 else 0
        if ratio_reciente > 0.7:
            contenido_trending.append({'publicacion': pub, 'ratio_reciente': ratio_reciente, 'dias_desde_publicacion': dias_desde_publicacion})
        elif dias_desde_publicacion > 30 and engagement_total > statistics.mean([p.engagement_score for p in self.publicaciones]):
            contenido_evergreen.append({'publicacion': pub, 'engagement_total': engagement_total, 'dias_desde_publicacion': dias_desde_publicacion})
    engagement_promedio_evergreen = statistics.mean([c['engagement_total'] for c in contenido_evergreen]) if contenido_evergreen else 0
    engagement_promedio_trending = statistics.mean([c['publicacion'].engagement_score for c in contenido_trending]) if contenido_trending else 0
    return {'contenido_evergreen': {'cantidad': len(contenido_evergreen), 'engagement_promedio': engagement_promedio_evergreen, 'ejemplos': [{'titulo': c['publicacion'].titulo[:50], 'engagement': c['engagement_total'], 'dias': c['dias_desde_publicacion']} for c in contenido_evergreen[:5]]}, 'contenido_trending': {'cantidad': len(contenido_trending), 'engagement_promedio': engagement_promedio_trending, 'ejemplos': [{'titulo': c['publicacion'].titulo[:50], 'engagement': c['publicacion'].engagement_score, 'ratio_reciente': c['ratio_reciente']} for c in contenido_trending[:5]]}, 'recomendacion': 'Balancear contenido evergreen (60%) y trending (40%)' if contenido_evergreen and contenido_trending else 'Generar más contenido evergreen para engagement sostenido' if not contenido_evergreen else 'Aumentar contenido trending para engagement inmediato'}


def analizar_patrones_cross_platform(self) -> Dict[str, Any]:
    """Analiza patrones de contenido que funcionan bien en múltiples plataformas."""
    if len(self.publicaciones) < 15:
        return {'error': 'Se necesitan al menos 15 publicaciones'}
    contenido_por_plataforma = defaultdict(list)
    for pub in self.publicaciones:
        contenido_por_plataforma[pub.plataforma].append(pub)
    patrones_comunes = defaultdict(list)
    tipos_exitosos = defaultdict(int)
    hashtags_exitosos = defaultdict(int)
    horarios_exitosos = defaultdict(int)
    for plataforma, pubs in contenido_por_plataforma.items():
        if len(pubs) >= 3:
            mejor_tipo = Counter([p.tipo_contenido for p in pubs]).most_common(1)[0][0] if pubs else None
            mejor_hashtag = Counter([h.lower() for p in pubs for h in p.hashtags]).most_common(1)[0][0] if pubs else None
            mejor_horario = Counter([p.metadata.get('hora_publicacion', p.fecha_publicacion.hour) for p in pubs]).most_common(1)[0][0] if pubs else None
            if mejor_tipo:
                tipos_exitosos[mejor_tipo] += 1
            if mejor_hashtag:
                hashtags_exitosos[mejor_hashtag] += 1
            if mejor_horario:
                horarios_exitosos[mejor_horario] += 1
    tipos_cross_platform = [tipo for tipo, count in tipos_exitosos.items() if count >= 2]
    hashtags_cross_platform = [h for h, count in hashtags_exitosos.items() if count >= 2]
    horarios_cross_platform = [h for h, count in horarios_exitosos.items() if count >= 2]
    return {'tipos_cross_platform': tipos_cross_platform, 'hashtags_cross_platform': hashtags_cross_platform[:10], 'horarios_cross_platform': horarios_cross_platform, 'recomendacion': f"Usar tipos {', '.join(tipos_cross_platform[:2])} y hashtags {', '.join(hashtags_cross_platform[:3])} para máximo alcance cross-platform" if tipos_cross_platform and hashtags_cross_platform else "No se detectaron patrones cross-platform significativos"}


def predecir_potencial_viralidad(self, tipo_contenido: str, plataforma: str, titulo: str, hashtags: List[str], tiene_media: bool = True) -> Dict[str, Any]:
    """Predice el potencial de viralidad de un contenido antes de publicarlo."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    factores_viralidad = {}
    contenido_viral_historico = [p for p in self.publicaciones if p.es_viral]
    if contenido_viral_historico:
        tipos_virales = Counter([p.tipo_contenido for p in contenido_viral_historico])
        plataformas_virales = Counter([p.plataforma for p in contenido_viral_historico])
        hashtags_virales = Counter([h.lower() for p in contenido_viral_historico for h in p.hashtags])
        factores_viralidad['tipo_contenido'] = tipos_virales.get(tipo_contenido, 0) / len(contenido_viral_historico) * 100 if contenido_viral_historico else 0
        factores_viralidad['plataforma'] = plataformas_virales.get(plataforma, 0) / len(contenido_viral_historico) * 100 if contenido_viral_historico else 0
        hashtags_match = sum(1 for h in hashtags if h.lower() in hashtags_virales)
        factores_viralidad['hashtags_match'] = (hashtags_match / len(hashtags) * 100) if hashtags else 0
        factores_viralidad['tiene_media'] = (sum(1 for p in contenido_viral_historico if p.tiene_media) / len(contenido_viral_historico) * 100) if contenido_viral_historico else 0
    score_viralidad = (factores_viralidad.get('tipo_contenido', 0) * 0.3 + factores_viralidad.get('plataforma', 0) * 0.2 + factores_viralidad.get('hashtags_match', 0) * 0.3 + (100 if tiene_media and factores_viralidad.get('tiene_media', 0) > 50 else 0) * 0.2)
    probabilidad_viral = min(100, score_viralidad)
    return {'probabilidad_viral': probabilidad_viral, 'factores_analizados': factores_viralidad, 'recomendaciones': ['Ajustar tipo de contenido' if factores_viralidad.get('tipo_contenido', 0) < 20 else 'Tipo de contenido óptimo', 'Cambiar plataforma' if factores_viralidad.get('plataforma', 0) < 20 else 'Plataforma óptima', 'Optimizar hashtags' if factores_viralidad.get('hashtags_match', 0) < 30 else 'Hashtags optimizados', 'Agregar media visual' if not tiene_media else 'Media incluida'], 'clasificacion': 'Alto potencial viral' if probabilidad_viral > 70 else 'Potencial viral medio' if probabilidad_viral > 40 else 'Bajo potencial viral'}


def analizar_engagement_por_longitud_contenido(self) -> Dict[str, Any]:
    """Analiza cómo la longitud del contenido afecta el engagement."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_longitud = defaultdict(list)
    for pub in self.publicaciones:
        longitud = len(pub.titulo)
        if longitud < 50:
            categoria = 'Corto (<50)'
        elif longitud < 150:
            categoria = 'Medio (50-150)'
        elif longitud < 300:
            categoria = 'Largo (150-300)'
        else:
            categoria = 'Muy Largo (>300)'
        contenido_por_longitud[categoria].append(pub)
    analisis_longitud = []
    for categoria, pubs in contenido_por_longitud.items():
        if len(pubs) >= 2:
            analisis_longitud.append({'categoria': categoria, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_longitud.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_longitud = analisis_longitud[0] if analisis_longitud else None
    return {'analisis_por_longitud': analisis_longitud, 'mejor_longitud': mejor_longitud, 'recomendacion': f"Usar contenido de longitud {mejor_longitud['categoria']} para máximo engagement" if mejor_longitud else "No hay datos suficientes para determinar longitud óptima"}


def generar_roadmap_contenido(self, semanas: int = 8) -> Dict[str, Any]:
    """Genera un roadmap estratégico de contenido para las próximas semanas."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    mejor_tipo = self.identificar_mejor_tipo()
    mejor_plataforma = max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else None
    horarios_optimos = self.analizar_horarios_optimos()
    hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=10)
    roadmap = {'semanas': [], 'objetivos': {}, 'estrategia_general': []}
    fecha_inicio = datetime.now()
    tipos_distribucion = self.optimizar_distribucion_tipos()
    distribucion_optima = tipos_distribucion.get('distribucion_optima', {})
    tipos_prioritarios = sorted(distribucion_optima.items(), key=lambda x: x[1].get('porcentaje', 0), reverse=True)[:3]
    for semana in range(semanas):
        semana_data = {'semana': semana + 1, 'fecha_inicio': (fecha_inicio + timedelta(weeks=semana)).strftime('%Y-%m-%d'), 'contenido_planificado': [], 'objetivos_semana': {}}
        posts_por_semana = 5
        for i in range(posts_por_semana):
            tipo_asignado = tipos_prioritarios[i % len(tipos_prioritarios)][0] if tipos_prioritarios else mejor_tipo['tipo']
            mejor_horario = max(horarios_optimos.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios_optimos else '10:00'
            hashtags_sugeridos = [h['hashtag'] for h in hashtags_efectivos[:5]]
            semana_data['contenido_planificado'].append({'dia': (i % 5) + 1, 'tipo': tipo_asignado, 'plataforma': mejor_plataforma, 'horario': mejor_horario, 'hashtags_sugeridos': hashtags_sugeridos})
        semana_data['objetivos_semana'] = {'engagement_rate_objetivo': statistics.mean([p.engagement_rate for p in self.publicaciones]) * 1.1, 'publicaciones_objetivo': posts_por_semana, 'contenido_viral_objetivo': 1}
        roadmap['semanas'].append(semana_data)
    roadmap['objetivos'] = {'engagement_rate_objetivo': statistics.mean([p.engagement_rate for p in self.publicaciones]) * 1.15, 'contenido_viral_objetivo': semanas * 0.2, 'crecimiento_audiencia_objetivo': 20}
    # Construir estrategia general evitando f-strings anidados con backslashes
    distribucion_texto = ', '.join([f"{t[0]} {t[1].get('porcentaje', 0)}%" for t in tipos_prioritarios[:3]])
    roadmap['estrategia_general'] = [
        f"Enfocarse en tipo {mejor_tipo['tipo']} ({mejor_tipo['datos']['nombre']})",
        f"Priorizar plataforma {mejor_plataforma}",
        f"Usar horarios {mejor_horario}",
        f"Distribuir contenido: {distribucion_texto}"
    ]
    return roadmap


def analizar_competidores_especificos(self, datos_competidores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analiza métricas específicas de competidores y compara con propias."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    if not datos_competidores:
        return {'error': 'Se necesitan datos de competidores'}
    metricas_propias = {'engagement_rate': statistics.mean([p.engagement_rate for p in self.publicaciones]), 'engagement_score': statistics.mean([p.engagement_score for p in self.publicaciones]), 'contenido_viral': (sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones) * 100), 'frecuencia_publicacion': len(self.publicaciones) / max(1, (datetime.now() - min(p.fecha_publicacion for p in self.publicaciones)).days)}
    metricas_competidores = []
    for competidor in datos_competidores:
        metricas_comp = {'nombre': competidor.get('nombre', 'Competidor'), 'engagement_rate': competidor.get('engagement_rate', 0), 'engagement_score': competidor.get('engagement_score', 0), 'contenido_viral': competidor.get('contenido_viral_porcentaje', 0), 'frecuencia_publicacion': competidor.get('frecuencia_publicacion', 0)}
        metricas_competidores.append(metricas_comp)
    comparacion = []
    for comp in metricas_competidores:
        gaps = {'engagement_rate': comp['engagement_rate'] - metricas_propias['engagement_rate'], 'engagement_score': comp['engagement_score'] - metricas_propias['engagement_score'], 'contenido_viral': comp['contenido_viral'] - metricas_propias['contenido_viral']}
        ventajas = [k for k, v in gaps.items() if v < 0]
        desventajas = [k for k, v in gaps.items() if v > 0]
        comparacion.append({'competidor': comp['nombre'], 'gaps': gaps, 'ventajas_propias': ventajas, 'desventajas_propias': desventajas, 'score_comparativo': (len(ventajas) / len(gaps) * 100) if gaps else 0})
    mejor_competidor = max(comparacion, key=lambda x: x['score_comparativo']) if comparacion else None
    return {'metricas_propias': metricas_propias, 'metricas_competidores': metricas_competidores, 'comparacion': comparacion, 'mejor_competidor': mejor_competidor, 'recomendaciones': [f"Mejorar {', '.join(mejor_competidor['desventajas_propias'])} para competir con {mejor_competidor['competidor']}" if mejor_competidor and mejor_competidor['desventajas_propias'] else "Mantener ventajas competitivas actuales"]}


def analizar_palabras_clave_trending(self, ventana_dias: int = 7) -> Dict[str, Any]:
    """Identifica palabras clave que están trending en los últimos días."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    fecha_limite = datetime.now() - timedelta(days=ventana_dias)
    publicaciones_recientes = [p for p in self.publicaciones if p.fecha_publicacion >= fecha_limite]
    publicaciones_anteriores = [p for p in self.publicaciones if p.fecha_publicacion < fecha_limite]
    if len(publicaciones_recientes) < 3:
        return {'error': 'No hay suficientes publicaciones recientes'}
    palabras_recientes = Counter()
    palabras_anteriores = Counter()
    for pub in publicaciones_recientes:
        palabras = re.findall(r'\b\w+\b', pub.titulo.lower())
        palabras_recientes.update(palabras)
    for pub in publicaciones_anteriores:
        palabras = re.findall(r'\b\w+\b', pub.titulo.lower())
        palabras_anteriores.update(palabras)
    palabras_trending = []
    stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'año', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esas', 'esos', 'estas', 'estos', 'las', 'los', 'les', 'nos', 'me', 'te', 'se', 'le', 'lo', 'la', 'el', 'un', 'una', 'unos', 'unas', 'de', 'del', 'al', 'a', 'en', 'por', 'para', 'con', 'sin', 'sobre', 'bajo', 'entre', 'hasta', 'desde', 'durante', 'mediante', 'según', 'contra', 'hacia', 'tras', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'sobre', 'tras'}
    for palabra, count_reciente in palabras_recientes.items():
        if len(palabra) > 3 and palabra not in stop_words:
            count_anterior = palabras_anteriores.get(palabra, 0)
            crecimiento = ((count_reciente - count_anterior) / count_anterior * 100) if count_anterior > 0 else 100
            if crecimiento > 50 or count_reciente >= 3:
                palabras_trending.append({'palabra': palabra, 'frecuencia_reciente': count_reciente, 'crecimiento': crecimiento, 'engagement_promedio': statistics.mean([p.engagement_score for p in publicaciones_recientes if palabra in p.titulo.lower()])})
    palabras_trending.sort(key=lambda x: x['crecimiento'], reverse=True)
    return {'ventana_dias': ventana_dias, 'palabras_trending': palabras_trending[:20], 'recomendacion': f"Incorporar palabras clave trending: {', '.join([p['palabra'] for p in palabras_trending[:5]])}" if palabras_trending else "No se detectaron palabras clave trending significativas"}


def analizar_engagement_por_formato(self) -> Dict[str, Any]:
    """Analiza el engagement por formato de contenido (video, imagen, texto, carousel)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_formato = defaultdict(list)
    for pub in self.publicaciones:
        formato = pub.metadata.get('formato', 'texto')
        contenido_por_formato[formato].append(pub)
    analisis_formato = []
    for formato, pubs in contenido_por_formato.items():
        if len(pubs) >= 2:
            analisis_formato.append({'formato': formato, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'contenido_viral_porcentaje': (sum(1 for p in pubs if p.es_viral) / len(pubs) * 100)})
    analisis_formato.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_formato = analisis_formato[0] if analisis_formato else None
    return {'analisis_por_formato': analisis_formato, 'mejor_formato': mejor_formato, 'recomendacion': f"Priorizar formato {mejor_formato['formato']} para máximo engagement" if mejor_formato else "No hay datos suficientes para determinar formato óptimo"}


def generar_ideas_contenido_inteligentes(self, num_ideas: int = 10, tipo_preferido: str = None) -> Dict[str, Any]:
    """Genera ideas de contenido inteligentes basadas en análisis de datos históricos."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    mejor_tipo = self.identificar_mejor_tipo()
    mejor_plataforma = max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else None
    hashtags_efectivos = self.analizar_hashtags_efectivos(top_n=10)
    palabras_clave_trending = self.analizar_palabras_clave_trending()
    contenido_exitoso = sorted(self.publicaciones, key=lambda x: x.engagement_score, reverse=True)[:5]
    ideas = []
    tipo_usar = tipo_preferido or mejor_tipo['tipo']
    for i in range(num_ideas):
        palabras_trending = [p['palabra'] for p in palabras_clave_trending.get('palabras_trending', [])[:3]]
        hashtags_sugeridos = [h['hashtag'] for h in hashtags_efectivos[:5]]
        contenido_base = contenido_exitoso[i % len(contenido_exitoso)] if contenido_exitoso else None
        titulo_base = contenido_base.titulo[:50] if contenido_base else "Contenido sobre"
        idea = {'id': i + 1, 'tipo': tipo_usar, 'plataforma': mejor_plataforma, 'titulo_sugerido': f"{titulo_base} {' '.join(palabras_trending[:2])}", 'hashtags_sugeridos': hashtags_sugeridos, 'palabras_clave': palabras_trending, 'engagement_esperado': mejor_tipo['datos']['engagement_score_promedio'], 'razon': f"Basado en contenido exitoso tipo {tipo_usar} con engagement promedio de {mejor_tipo['datos']['engagement_score_promedio']:.1f}"}
        ideas.append(idea)
    return {'ideas_generadas': ideas, 'total_ideas': len(ideas), 'tipo_recomendado': tipo_usar, 'plataforma_recomendada': mejor_plataforma, 'recomendacion': f"Generar {num_ideas} piezas de contenido tipo {tipo_usar} en {mejor_plataforma} usando palabras trending y hashtags efectivos"}


def analizar_eficiencia_por_recurso(self, costo_por_tipo: Dict[str, float] = None) -> Dict[str, Any]:
    """Analiza la eficiencia de contenido considerando recursos/costos necesarios."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    if costo_por_tipo is None:
        costo_por_tipo = {'X': 50.0, 'Y': 75.0, 'Z': 100.0}
    analisis_tipos = self.analizar_por_tipo()
    eficiencia_por_tipo = []
    for tipo, datos in analisis_tipos.items():
        costo = costo_por_tipo.get(tipo, 50.0)
        engagement_promedio = datos['engagement_score_promedio']
        eficiencia = engagement_promedio / costo if costo > 0 else 0
        eficiencia_por_tipo.append({'tipo': tipo, 'costo_promedio': costo, 'engagement_promedio': engagement_promedio, 'eficiencia': eficiencia, 'roi_estimado': (engagement_promedio - costo) / costo * 100 if costo > 0 else 0})
    eficiencia_por_tipo.sort(key=lambda x: x['eficiencia'], reverse=True)
    mejor_eficiencia = eficiencia_por_tipo[0] if eficiencia_por_tipo else None
    return {'eficiencia_por_tipo': eficiencia_por_tipo, 'mejor_eficiencia': mejor_eficiencia, 'recomendacion': f"Priorizar tipo {mejor_eficiencia['tipo']} para máxima eficiencia (ROI: {mejor_eficiencia['roi_estimado']:.1f}%)" if mejor_eficiencia else "No hay datos suficientes"}


def analizar_engagement_por_temporada(self) -> Dict[str, Any]:
    """Analiza el engagement por temporada/estación del año."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_temporada = defaultdict(list)
    temporadas = {'Primavera': [3, 4, 5], 'Verano': [6, 7, 8], 'Otoño': [9, 10, 11], 'Invierno': [12, 1, 2]}
    for pub in self.publicaciones:
        mes = pub.fecha_publicacion.month
        for temporada, meses in temporadas.items():
            if mes in meses:
                contenido_por_temporada[temporada].append(pub)
                break
    analisis_temporada = []
    for temporada, pubs in contenido_por_temporada.items():
        if len(pubs) >= 2:
            analisis_temporada.append({'temporada': temporada, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'contenido_viral_porcentaje': (sum(1 for p in pubs if p.es_viral) / len(pubs) * 100)})
    analisis_temporada.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_temporada = analisis_temporada[0] if analisis_temporada else None
    return {'analisis_por_temporada': analisis_temporada, 'mejor_temporada': mejor_temporada, 'recomendacion': f"Planificar más contenido durante {mejor_temporada['temporada']} para máximo engagement" if mejor_temporada else "No hay datos suficientes para determinar temporada óptima"}


def analizar_engagement_por_evento_especial(self, eventos: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analiza el engagement durante eventos especiales (festividades, lanzamientos, etc.)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    if eventos is None:
        eventos = [{'nombre': 'Navidad', 'fecha_inicio': '2024-12-20', 'fecha_fin': '2024-12-26'}, {'nombre': 'Año Nuevo', 'fecha_inicio': '2024-12-30', 'fecha_fin': '2025-01-02'}]
    contenido_por_evento = defaultdict(list)
    contenido_normal = []
    for pub in self.publicaciones:
        fecha_pub = pub.fecha_publicacion.date()
        en_evento = False
        for evento in eventos:
            fecha_inicio = datetime.strptime(evento['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(evento['fecha_fin'], '%Y-%m-%d').date()
            if fecha_inicio <= fecha_pub <= fecha_fin:
                contenido_por_evento[evento['nombre']].append(pub)
                en_evento = True
                break
        if not en_evento:
            contenido_normal.append(pub)
    analisis_eventos = []
    for evento_nombre, pubs in contenido_por_evento.items():
        if len(pubs) >= 2:
            analisis_eventos.append({'evento': evento_nombre, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    engagement_normal = statistics.mean([p.engagement_score for p in contenido_normal]) if contenido_normal else 0
    mejor_evento = max(analisis_eventos, key=lambda x: x['engagement_promedio']) if analisis_eventos else None
    return {'analisis_por_evento': analisis_eventos, 'engagement_normal': engagement_normal, 'mejor_evento': mejor_evento, 'recomendacion': f"Planificar contenido especial durante {mejor_evento['evento']} (+{((mejor_evento['engagement_promedio'] - engagement_normal) / engagement_normal * 100) if engagement_normal > 0 else 0:.1f}% engagement)" if mejor_evento and engagement_normal > 0 else "No hay datos suficientes"}


def analizar_engagement_por_dispositivo(self) -> Dict[str, Any]:
    """Analiza el engagement por dispositivo (móvil, desktop, tablet)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_dispositivo = defaultdict(list)
    for pub in self.publicaciones:
        dispositivo = pub.metadata.get('dispositivo', 'desconocido')
        contenido_por_dispositivo[dispositivo].append(pub)
    analisis_dispositivo = []
    for dispositivo, pubs in contenido_por_dispositivo.items():
        if len(pubs) >= 2:
            analisis_dispositivo.append({'dispositivo': dispositivo, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_dispositivo.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_dispositivo = analisis_dispositivo[0] if analisis_dispositivo else None
    return {'analisis_por_dispositivo': analisis_dispositivo, 'mejor_dispositivo': mejor_dispositivo, 'recomendacion': f"Optimizar contenido para {mejor_dispositivo['dispositivo']} para máximo engagement" if mejor_dispositivo else "No hay datos suficientes para determinar dispositivo óptimo"}


def analizar_engagement_por_fuente_trafico(self) -> Dict[str, Any]:
    """Analiza el engagement por fuente de tráfico (orgánico, pagado, referido, etc.)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_fuente = defaultdict(list)
    for pub in self.publicaciones:
        fuente = pub.metadata.get('fuente_trafico', 'organico')
        contenido_por_fuente[fuente].append(pub)
    analisis_fuente = []
    for fuente, pubs in contenido_por_fuente.items():
        if len(pubs) >= 2:
            analisis_fuente.append({'fuente': fuente, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'alcance_promedio': statistics.mean([p.reach for p in pubs])})
    analisis_fuente.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_fuente = analisis_fuente[0] if analisis_fuente else None
    return {'analisis_por_fuente': analisis_fuente, 'mejor_fuente': mejor_fuente, 'recomendacion': f"Priorizar estrategia de {mejor_fuente['fuente']} para máximo engagement" if mejor_fuente else "No hay datos suficientes para determinar fuente óptima"}


def analizar_engagement_por_colaboracion(self) -> Dict[str, Any]:
    """Analiza el engagement de contenido con colaboraciones/influencers."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_colaboracion = []
    contenido_sin_colaboracion = []
    for pub in self.publicaciones:
        tiene_colaboracion = pub.metadata.get('tiene_colaboracion', False) or any('colab' in h.lower() or 'collab' in h.lower() for h in pub.hashtags)
        if tiene_colaboracion:
            contenido_colaboracion.append(pub)
        else:
            contenido_sin_colaboracion.append(pub)
    engagement_colaboracion = statistics.mean([p.engagement_score for p in contenido_colaboracion]) if contenido_colaboracion else 0
    engagement_sin_colaboracion = statistics.mean([p.engagement_score for p in contenido_sin_colaboracion]) if contenido_sin_colaboracion else 0
    diferencia = engagement_colaboracion - engagement_sin_colaboracion
    diferencia_porcentual = (diferencia / engagement_sin_colaboracion * 100) if engagement_sin_colaboracion > 0 else 0
    return {'contenido_con_colaboracion': {'cantidad': len(contenido_colaboracion), 'engagement_promedio': engagement_colaboracion}, 'contenido_sin_colaboracion': {'cantidad': len(contenido_sin_colaboracion), 'engagement_promedio': engagement_sin_colaboracion}, 'diferencia': diferencia, 'diferencia_porcentual': diferencia_porcentual, 'recomendacion': f"Aumentar colaboraciones (+{diferencia_porcentual:.1f}% engagement)" if diferencia_porcentual > 0 else "Colaboraciones no muestran mejora significativa" if diferencia_porcentual > -10 else "Revisar estrategia de colaboraciones"}


def analizar_engagement_por_campana(self, campanas: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analiza el engagement de contenido asociado a campañas específicas."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    if campanas is None:
        campanas = [{'nombre': 'Campaña Q1', 'hashtags': ['#campanaq1']}, {'nombre': 'Campaña Q2', 'hashtags': ['#campanaq2']}]
    contenido_por_campana = defaultdict(list)
    contenido_sin_campana = []
    for pub in self.publicaciones:
        en_campana = False
        for campana in campanas:
            hashtags_campana = [h.lower() for h in campana.get('hashtags', [])]
            if any(h.lower() in hashtags_campana for h in pub.hashtags):
                contenido_por_campana[campana['nombre']].append(pub)
                en_campana = True
                break
        if not en_campana:
            contenido_sin_campana.append(pub)
    analisis_campanas = []
    for campana_nombre, pubs in contenido_por_campana.items():
        if len(pubs) >= 2:
            analisis_campanas.append({'campana': campana_nombre, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'alcance_total': sum([p.reach for p in pubs])})
    analisis_campanas.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_campana = analisis_campanas[0] if analisis_campanas else None
    return {'analisis_por_campana': analisis_campanas, 'contenido_sin_campana': {'cantidad': len(contenido_sin_campana)}, 'mejor_campana': mejor_campana, 'recomendacion': f"Replicar estrategia de {mejor_campana['campana']} para máximo engagement" if mejor_campana else "No hay datos suficientes de campañas"}


def analizar_engagement_por_tipo_interaccion(self) -> Dict[str, Any]:
    """Analiza el engagement desglosado por tipo de interacción (likes, comentarios, shares)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    interacciones_por_tipo = {'likes': [], 'comentarios': [], 'shares': []}
    for pub in self.publicaciones:
        interacciones_por_tipo['likes'].append(pub.likes)
        interacciones_por_tipo['comentarios'].append(pub.comentarios)
        interacciones_por_tipo['shares'].append(pub.shares)
    analisis_interacciones = {}
    for tipo, valores in interacciones_por_tipo.items():
        if valores:
            analisis_interacciones[tipo] = {'promedio': statistics.mean(valores), 'mediana': statistics.median(valores), 'total': sum(valores), 'porcentaje_del_total': (sum(valores) / sum([p.likes + p.comentarios + p.shares for p in self.publicaciones]) * 100) if self.publicaciones else 0}
    mejor_interaccion = max(analisis_interacciones.items(), key=lambda x: x[1]['promedio']) if analisis_interacciones else None
    return {'analisis_por_tipo': analisis_interacciones, 'mejor_interaccion': mejor_interaccion, 'recomendacion': f"Enfocarse en generar más {mejor_interaccion[0]} para máximo engagement" if mejor_interaccion else "No hay datos suficientes"}


def analizar_engagement_por_duracion_video(self) -> Dict[str, Any]:
    """Analiza cómo la duración del video afecta el engagement."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_duracion = defaultdict(list)
    for pub in self.publicaciones:
        if pub.duracion_video > 0:
            duracion_segundos = pub.duracion_video / 1000
            if duracion_segundos < 15:
                categoria = 'Muy Corto (<15s)'
            elif duracion_segundos < 30:
                categoria = 'Corto (15-30s)'
            elif duracion_segundos < 60:
                categoria = 'Medio (30-60s)'
            elif duracion_segundos < 180:
                categoria = 'Largo (1-3min)'
            else:
                categoria = 'Muy Largo (>3min)'
            contenido_por_duracion[categoria].append(pub)
    analisis_duracion = []
    for categoria, pubs in contenido_por_duracion.items():
        if len(pubs) >= 2:
            analisis_duracion.append({'categoria': categoria, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'duracion_promedio_segundos': statistics.mean([p.duracion_video / 1000 for p in pubs])})
    analisis_duracion.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_duracion = analisis_duracion[0] if analisis_duracion else None
    return {'analisis_por_duracion': analisis_duracion, 'mejor_duracion': mejor_duracion, 'recomendacion': f"Priorizar videos de duración {mejor_duracion['categoria']} para máximo engagement" if mejor_duracion else "No hay datos suficientes de videos"}


def analizar_engagement_por_frecuencia_publicacion_detallado(self) -> Dict[str, Any]:
    """Analiza cómo la frecuencia de publicación afecta el engagement."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
    intervalos = []
    for i in range(1, len(publicaciones_ordenadas)):
        dias_diferencia = (publicaciones_ordenadas[i].fecha_publicacion - publicaciones_ordenadas[i-1].fecha_publicacion).days
        intervalos.append({'dias': dias_diferencia, 'engagement': publicaciones_ordenadas[i].engagement_score})
    frecuencia_por_categoria = defaultdict(list)
    for intervalo in intervalos:
        dias = intervalo['dias']
        if dias == 0:
            categoria = 'Múltiples por día'
        elif dias == 1:
            categoria = 'Diario'
        elif dias <= 3:
            categoria = 'Cada 2-3 días'
        elif dias <= 7:
            categoria = 'Semanal'
        elif dias <= 14:
            categoria = 'Cada 2 semanas'
        else:
            categoria = 'Esporádico (>2 semanas)'
        frecuencia_por_categoria[categoria].append(intervalo['engagement'])
    analisis_frecuencia = []
    for categoria, engagement_scores in frecuencia_por_categoria.items():
        if len(engagement_scores) >= 2:
            analisis_frecuencia.append({'categoria': categoria, 'cantidad': len(engagement_scores), 'engagement_promedio': statistics.mean(engagement_scores)})
    analisis_frecuencia.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_frecuencia = analisis_frecuencia[0] if analisis_frecuencia else None
    return {'analisis_por_frecuencia': analisis_frecuencia, 'mejor_frecuencia': mejor_frecuencia, 'recomendacion': f"Publicar con frecuencia {mejor_frecuencia['categoria']} para máximo engagement" if mejor_frecuencia else "No hay datos suficientes"}


def analizar_engagement_por_hora_detallado(self) -> Dict[str, Any]:
    """Analiza el engagement por hora del día con mayor detalle (24 horas)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_hora = defaultdict(list)
    for pub in self.publicaciones:
        hora = pub.metadata.get('hora_publicacion', pub.fecha_publicacion.hour)
        contenido_por_hora[hora].append(pub)
    analisis_horas = []
    for hora in range(24):
        if hora in contenido_por_hora and len(contenido_por_hora[hora]) >= 1:
            pubs_hora = contenido_por_hora[hora]
            analisis_horas.append({'hora': hora, 'cantidad': len(pubs_hora), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs_hora]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs_hora])})
    analisis_horas.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejores_horas = analisis_horas[:5] if analisis_horas else []
    return {'analisis_por_hora': analisis_horas, 'mejores_horas': mejores_horas, 'recomendacion': f"Publicar entre las {mejores_horas[0]['hora']:02d}:00 y {mejores_horas[-1]['hora']:02d}:00 para máximo engagement" if mejores_horas else "No hay datos suficientes"}


def analizar_engagement_por_dia_mes(self) -> Dict[str, Any]:
    """Analiza el engagement por día del mes (1-31)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_dia = defaultdict(list)
    for pub in self.publicaciones:
        dia_mes = pub.fecha_publicacion.day
        contenido_por_dia[dia_mes].append(pub)
    analisis_dias = []
    for dia in range(1, 32):
        if dia in contenido_por_dia and len(contenido_por_dia[dia]) >= 1:
            pubs_dia = contenido_por_dia[dia]
            analisis_dias.append({'dia': dia, 'cantidad': len(pubs_dia), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs_dia]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs_dia])})
    analisis_dias.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejores_dias = analisis_dias[:5] if analisis_dias else []
    return {'analisis_por_dia': analisis_dias, 'mejores_dias': mejores_dias, 'recomendacion': f"Publicar en los días {', '.join([str(d['dia']) for d in mejores_dias[:3]])} del mes para máximo engagement" if mejores_dias else "No hay datos suficientes"}


def analizar_engagement_por_mes_ano(self) -> Dict[str, Any]:
    """Analiza el engagement por mes del año."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_mes = defaultdict(list)
    meses_nombres = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    for pub in self.publicaciones:
        mes = pub.fecha_publicacion.month
        contenido_por_mes[mes].append(pub)
    analisis_meses = []
    for mes in range(1, 13):
        if mes in contenido_por_mes and len(contenido_por_mes[mes]) >= 1:
            pubs_mes = contenido_por_mes[mes]
            analisis_meses.append({'mes': mes, 'mes_nombre': meses_nombres[mes], 'cantidad': len(pubs_mes), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs_mes]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs_mes])})
    analisis_meses.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_mes = analisis_meses[0] if analisis_meses else None
    return {'analisis_por_mes': analisis_meses, 'mejor_mes': mejor_mes, 'recomendacion': f"Planificar más contenido en {mejor_mes['mes_nombre']} para máximo engagement" if mejor_mes else "No hay datos suficientes"}


def analizar_engagement_por_ubicacion(self) -> Dict[str, Any]:
    """Analiza el engagement por ubicación geográfica."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_ubicacion = defaultdict(list)
    for pub in self.publicaciones:
        ubicacion = pub.metadata.get('ubicacion', 'desconocida')
        contenido_por_ubicacion[ubicacion].append(pub)
    analisis_ubicacion = []
    for ubicacion, pubs in contenido_por_ubicacion.items():
        if len(pubs) >= 2:
            analisis_ubicacion.append({'ubicacion': ubicacion, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'alcance_promedio': statistics.mean([p.reach for p in pubs])})
    analisis_ubicacion.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_ubicacion = analisis_ubicacion[0] if analisis_ubicacion else None
    return {'analisis_por_ubicacion': analisis_ubicacion, 'mejor_ubicacion': mejor_ubicacion, 'recomendacion': f"Optimizar contenido para audiencia de {mejor_ubicacion['ubicacion']} para máximo engagement" if mejor_ubicacion else "No hay datos suficientes de ubicación"}


def analizar_engagement_por_demografia(self) -> Dict[str, Any]:
    """Analiza el engagement por demografía de audiencia (edad, género, intereses)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_demografia = defaultdict(list)
    for pub in self.publicaciones:
        demografia = pub.metadata.get('demografia', 'general')
        contenido_por_demografia[demografia].append(pub)
    analisis_demografia = []
    for demografia, pubs in contenido_por_demografia.items():
        if len(pubs) >= 2:
            analisis_demografia.append({'demografia': demografia, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_demografia.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_demografia = analisis_demografia[0] if analisis_demografia else None
    return {'analisis_por_demografia': analisis_demografia, 'mejor_demografia': mejor_demografia, 'recomendacion': f"Enfocar contenido en demografía {mejor_demografia['demografia']} para máximo engagement" if mejor_demografia else "No hay datos suficientes de demografía"}


def analizar_engagement_por_calidad_contenido(self) -> Dict[str, Any]:
    """Analiza el engagement según la calidad percibida del contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_calidad = defaultdict(list)
    for pub in self.publicaciones:
        calidad = pub.metadata.get('calidad_contenido', 'media')
        contenido_por_calidad[calidad].append(pub)
    analisis_calidad = []
    for calidad, pubs in contenido_por_calidad.items():
        if len(pubs) >= 2:
            analisis_calidad.append({'calidad': calidad, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_calidad.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_calidad = analisis_calidad[0] if analisis_calidad else None
    return {'analisis_por_calidad': analisis_calidad, 'mejor_calidad': mejor_calidad, 'recomendacion': f"Mantener estándar de calidad {mejor_calidad['calidad']} para máximo engagement" if mejor_calidad else "No hay datos suficientes de calidad"}


def analizar_engagement_por_tipo_media(self) -> Dict[str, Any]:
    """Analiza el engagement por tipo de media (imagen estática, video, GIF, carousel)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_tipo_media = defaultdict(list)
    for pub in self.publicaciones:
        tipo_media = pub.metadata.get('tipo_media', 'imagen' if pub.tiene_media else 'texto')
        contenido_por_tipo_media[tipo_media].append(pub)
    analisis_tipo_media = []
    for tipo, pubs in contenido_por_tipo_media.items():
        if len(pubs) >= 2:
            analisis_tipo_media.append({'tipo_media': tipo, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'contenido_viral_porcentaje': (sum(1 for p in pubs if p.es_viral) / len(pubs) * 100)})
    analisis_tipo_media.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_tipo_media = analisis_tipo_media[0] if analisis_tipo_media else None
    return {'analisis_por_tipo_media': analisis_tipo_media, 'mejor_tipo_media': mejor_tipo_media, 'recomendacion': f"Priorizar tipo de media {mejor_tipo_media['tipo_media']} para máximo engagement" if mejor_tipo_media else "No hay datos suficientes"}


def generar_analisis_completo_temporal(self) -> Dict[str, Any]:
    """Genera un análisis completo temporal combinando todos los análisis temporales."""
    if len(self.publicaciones) < 20:
        return {'error': 'Se necesitan al menos 20 publicaciones'}
    analisis_hora = self.analizar_engagement_por_hora_detallado()
    analisis_dia_mes = self.analizar_engagement_por_dia_mes()
    analisis_mes = self.analizar_engagement_por_mes_ano()
    analisis_temporada = self.analizar_engagement_por_temporada()
    mejor_hora = analisis_hora.get('mejores_horas', [{}])[0] if analisis_hora.get('mejores_horas') else {}
    mejor_dia = analisis_dia_mes.get('mejores_dias', [{}])[0] if analisis_dia_mes.get('mejores_dias') else {}
    mejor_mes = analisis_mes.get('mejor_mes', {})
    mejor_temporada = analisis_temporada.get('mejor_temporada', {})
    return {'analisis_hora': analisis_hora, 'analisis_dia_mes': analisis_dia_mes, 'analisis_mes': analisis_mes, 'analisis_temporada': analisis_temporada, 'configuracion_optima_temporal': {'mejor_hora': mejor_hora.get('hora'), 'mejor_dia_mes': mejor_dia.get('dia'), 'mejor_mes': mejor_mes.get('mes_nombre'), 'mejor_temporada': mejor_temporada.get('temporada')}, 'recomendacion': f"Publicar en {mejor_temporada.get('temporada', 'N/A')}, mes {mejor_mes.get('mes_nombre', 'N/A')}, día {mejor_dia.get('dia', 'N/A')}, hora {mejor_hora.get('hora', 'N/A')}:00 para máximo engagement"}


def analizar_engagement_por_emocion(self) -> Dict[str, Any]:
    """Analiza el engagement según la emoción que transmite el contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    emociones_comunes = ['alegría', 'inspiración', 'curiosidad', 'sorpresa', 'motivación', 'educación', 'entretenimiento', 'empatía']
    contenido_por_emocion = defaultdict(list)
    for pub in self.publicaciones:
        emocion = pub.metadata.get('emocion', 'general')
        if emocion not in emociones_comunes:
            emocion = 'general'
        contenido_por_emocion[emocion].append(pub)
    analisis_emocion = []
    for emocion, pubs in contenido_por_emocion.items():
        if len(pubs) >= 2:
            analisis_emocion.append({'emocion': emocion, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_emocion.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_emocion = analisis_emocion[0] if analisis_emocion else None
    return {'analisis_por_emocion': analisis_emocion, 'mejor_emocion': mejor_emocion, 'recomendacion': f"Crear contenido que transmita {mejor_emocion['emocion']} para máximo engagement" if mejor_emocion else "No hay datos suficientes de emociones"}


def analizar_engagement_por_tema(self) -> Dict[str, Any]:
    """Analiza el engagement por tema o categoría de contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_tema = defaultdict(list)
    for pub in self.publicaciones:
        tema = pub.metadata.get('tema', 'general')
        contenido_por_tema[tema].append(pub)
    analisis_tema = []
    for tema, pubs in contenido_por_tema.items():
        if len(pubs) >= 2:
            analisis_tema.append({'tema': tema, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'contenido_viral_porcentaje': (sum(1 for p in pubs if p.es_viral) / len(pubs) * 100)})
    analisis_tema.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_tema = analisis_tema[0] if analisis_tema else None
    return {'analisis_por_tema': analisis_tema, 'mejor_tema': mejor_tema, 'recomendacion': f"Crear más contenido sobre tema {mejor_tema['tema']} para máximo engagement" if mejor_tema else "No hay datos suficientes de temas"}


def analizar_engagement_por_autor(self) -> Dict[str, Any]:
    """Analiza el engagement por autor o creador del contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_autor = defaultdict(list)
    for pub in self.publicaciones:
        autor = pub.metadata.get('autor', 'desconocido')
        contenido_por_autor[autor].append(pub)
    analisis_autor = []
    for autor, pubs in contenido_por_autor.items():
        if len(pubs) >= 2:
            analisis_autor.append({'autor': autor, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs]), 'contenido_viral_porcentaje': (sum(1 for p in pubs if p.es_viral) / len(pubs) * 100)})
    analisis_autor.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_autor = analisis_autor[0] if analisis_autor else None
    return {'analisis_por_autor': analisis_autor, 'mejor_autor': mejor_autor, 'recomendacion': f"Colaborar más con {mejor_autor['autor']} para máximo engagement" if mejor_autor else "No hay datos suficientes de autores"}


def analizar_engagement_por_idioma(self) -> Dict[str, Any]:
    """Analiza el engagement por idioma del contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_idioma = defaultdict(list)
    for pub in self.publicaciones:
        idioma = pub.metadata.get('idioma', 'español')
        contenido_por_idioma[idioma].append(pub)
    analisis_idioma = []
    for idioma, pubs in contenido_por_idioma.items():
        if len(pubs) >= 2:
            analisis_idioma.append({'idioma': idioma, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_idioma.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_idioma = analisis_idioma[0] if analisis_idioma else None
    return {'analisis_por_idioma': analisis_idioma, 'mejor_idioma': mejor_idioma, 'recomendacion': f"Crear más contenido en {mejor_idioma['idioma']} para máximo engagement" if mejor_idioma else "No hay datos suficientes de idiomas"}


def analizar_engagement_por_estilo_contenido(self) -> Dict[str, Any]:
    """Analiza el engagement por estilo de contenido (formal, casual, humorístico, etc.)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_estilo = defaultdict(list)
    for pub in self.publicaciones:
        estilo = pub.metadata.get('estilo_contenido', 'general')
        contenido_por_estilo[estilo].append(pub)
    analisis_estilo = []
    for estilo, pubs in contenido_por_estilo.items():
        if len(pubs) >= 2:
            analisis_estilo.append({'estilo': estilo, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_estilo.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_estilo = analisis_estilo[0] if analisis_estilo else None
    return {'analisis_por_estilo': analisis_estilo, 'mejor_estilo': mejor_estilo, 'recomendacion': f"Usar estilo {mejor_estilo['estilo']} para máximo engagement" if mejor_estilo else "No hay datos suficientes de estilos"}


def generar_dashboard_completo(self) -> Dict[str, Any]:
    """Genera un dashboard completo con todos los análisis principales."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    dashboard = {'fecha_generacion': datetime.now().isoformat(), 'metricas_generales': {}, 'analisis_detallados': {}, 'recomendaciones_consolidadas': []}
    dashboard['metricas_generales'] = {'total_publicaciones': len(self.publicaciones), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in self.publicaciones]), 'engagement_score_promedio': statistics.mean([p.engagement_score for p in self.publicaciones]), 'contenido_viral_porcentaje': (sum(1 for p in self.publicaciones if p.es_viral) / len(self.publicaciones) * 100)}
    mejor_tipo = self.identificar_mejor_tipo()
    mejor_plataforma = max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else None
    dashboard['analisis_detallados'] = {'mejor_tipo': mejor_tipo, 'mejor_plataforma': mejor_plataforma, 'horarios_optimos': self.analizar_horarios_optimos(), 'hashtags_efectivos': self.analizar_hashtags_efectivos(top_n=10), 'temporal_completo': self.generar_analisis_completo_temporal() if len(self.publicaciones) >= 20 else {}}
    dashboard['recomendaciones_consolidadas'] = [f"Enfocarse en tipo {mejor_tipo['tipo']} ({mejor_tipo['datos']['nombre']})", f"Priorizar plataforma {mejor_plataforma}", "Usar hashtags más efectivos identificados", "Seguir configuración temporal óptima"]
    return dashboard


def analizar_engagement_por_longitud_texto(self) -> Dict[str, Any]:
    """Analiza el engagement por longitud del texto del contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_longitud = defaultdict(list)
    for pub in self.publicaciones:
        longitud_texto = len(pub.titulo) if pub.titulo else 0
        categoria = 'corto' if longitud_texto < 50 else ('medio' if longitud_texto < 150 else 'largo')
        contenido_por_longitud[categoria].append(pub)
    analisis_longitud = []
    for categoria, pubs in contenido_por_longitud.items():
        if len(pubs) >= 2:
            analisis_longitud.append({'categoria': categoria, 'cantidad': len(pubs), 'longitud_promedio': statistics.mean([len(p.titulo) if p.titulo else 0 for p in pubs]), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_longitud.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_longitud = analisis_longitud[0] if analisis_longitud else None
    return {'analisis_por_longitud': analisis_longitud, 'mejor_longitud': mejor_longitud, 'recomendacion': f"Usar textos de longitud {mejor_longitud['categoria']} ({mejor_longitud['longitud_promedio']:.0f} caracteres promedio) para máximo engagement" if mejor_longitud else "No hay datos suficientes"}


def analizar_engagement_por_palabras_clave(self) -> Dict[str, Any]:
    """Analiza el engagement por palabras clave presentes en el contenido."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    palabras_clave_engagement = defaultdict(list)
    palabras_comunes = ['tutorial', 'tips', 'hack', 'review', 'comparison', 'vs', 'how', 'why', 'best', 'top', 'new', 'free', 'guide', 'trick', 'secret']
    for pub in self.publicaciones:
        titulo_lower = (pub.titulo or '').lower()
        for palabra in palabras_comunes:
            if palabra in titulo_lower:
                palabras_clave_engagement[palabra].append(pub)
    analisis_palabras = []
    for palabra, pubs in palabras_clave_engagement.items():
        if len(pubs) >= 2:
            analisis_palabras.append({'palabra_clave': palabra, 'cantidad': len(pubs), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_palabras.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejores_palabras = analisis_palabras[:5] if analisis_palabras else []
    return {'analisis_por_palabras_clave': analisis_palabras, 'mejores_palabras_clave': mejores_palabras, 'recomendacion': f"Incorporar palabras clave: {', '.join([p['palabra_clave'] for p in mejores_palabras[:3]])} para máximo engagement" if mejores_palabras else "No hay datos suficientes"}


def analizar_engagement_por_hashtag_count(self) -> Dict[str, Any]:
    """Analiza el engagement según el número de hashtags utilizados."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_por_hashtag_count = defaultdict(list)
    for pub in self.publicaciones:
        num_hashtags = len(pub.hashtags)
        categoria = 'pocos' if num_hashtags < 3 else ('medio' if num_hashtags < 7 else 'muchos')
        contenido_por_hashtag_count[categoria].append(pub)
    analisis_count = []
    for categoria, pubs in contenido_por_hashtag_count.items():
        if len(pubs) >= 2:
            analisis_count.append({'categoria': categoria, 'cantidad': len(pubs), 'hashtags_promedio': statistics.mean([len(p.hashtags) for p in pubs]), 'engagement_promedio': statistics.mean([p.engagement_score for p in pubs]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in pubs])})
    analisis_count.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_count = analisis_count[0] if analisis_count else None
    return {'analisis_por_hashtag_count': analisis_count, 'mejor_count': mejor_count, 'recomendacion': f"Usar {mejor_count['categoria']} hashtags ({mejor_count['hashtags_promedio']:.1f} promedio) para máximo engagement" if mejor_count else "No hay datos suficientes"}


def analizar_engagement_por_mentions(self) -> Dict[str, Any]:
    """Analiza el engagement según si el contenido incluye menciones a otros usuarios."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_con_mentions = []
    contenido_sin_mentions = []
    for pub in self.publicaciones:
        tiene_mentions = pub.metadata.get('tiene_mentions', False) or any('@' in (pub.titulo or ''))
        if tiene_mentions:
            contenido_con_mentions.append(pub)
        else:
            contenido_sin_mentions.append(pub)
    analisis_mentions = []
    if len(contenido_con_mentions) >= 2:
        analisis_mentions.append({'tipo': 'con_mentions', 'cantidad': len(contenido_con_mentions), 'engagement_promedio': statistics.mean([p.engagement_score for p in contenido_con_mentions]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in contenido_con_mentions])})
    if len(contenido_sin_mentions) >= 2:
        analisis_mentions.append({'tipo': 'sin_mentions', 'cantidad': len(contenido_sin_mentions), 'engagement_promedio': statistics.mean([p.engagement_score for p in contenido_sin_mentions]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in contenido_sin_mentions])})
    analisis_mentions.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_tipo = analisis_mentions[0] if analisis_mentions else None
    return {'analisis_por_mentions': analisis_mentions, 'mejor_tipo': mejor_tipo, 'recomendacion': f"{'Incluir' if mejor_tipo and mejor_tipo['tipo'] == 'con_mentions' else 'No incluir'} menciones en el contenido para máximo engagement" if mejor_tipo else "No hay datos suficientes"}


def analizar_engagement_por_cta(self) -> Dict[str, Any]:
    """Analiza el engagement según si el contenido incluye llamadas a la acción (CTA)."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    contenido_con_cta = []
    contenido_sin_cta = []
    ctas_comunes = ['comenta', 'like', 'sigue', 'comparte', 'guarda', 'visita', 'descubre', 'aprende', 'suscríbete', 'descarga']
    for pub in self.publicaciones:
        titulo_lower = (pub.titulo or '').lower()
        tiene_cta = any(cta in titulo_lower for cta in ctas_comunes) or pub.metadata.get('tiene_cta', False)
        if tiene_cta:
            contenido_con_cta.append(pub)
        else:
            contenido_sin_cta.append(pub)
    analisis_cta = []
    if len(contenido_con_cta) >= 2:
        analisis_cta.append({'tipo': 'con_cta', 'cantidad': len(contenido_con_cta), 'engagement_promedio': statistics.mean([p.engagement_score for p in contenido_con_cta]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in contenido_con_cta])})
    if len(contenido_sin_cta) >= 2:
        analisis_cta.append({'tipo': 'sin_cta', 'cantidad': len(contenido_sin_cta), 'engagement_promedio': statistics.mean([p.engagement_score for p in contenido_sin_cta]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in contenido_sin_cta])})
    analisis_cta.sort(key=lambda x: x['engagement_promedio'], reverse=True)
    mejor_tipo = analisis_cta[0] if analisis_cta else None
    return {'analisis_por_cta': analisis_cta, 'mejor_tipo': mejor_tipo, 'recomendacion': f"{'Incluir' if mejor_tipo and mejor_tipo['tipo'] == 'con_cta' else 'No incluir'} CTAs en el contenido para máximo engagement" if mejor_tipo else "No hay datos suficientes"}


def generar_analisis_completo_contenido(self) -> Dict[str, Any]:
    """Genera un análisis completo del contenido combinando múltiples factores."""
    if len(self.publicaciones) < 20:
        return {'error': 'Se necesitan al menos 20 publicaciones'}
    analisis_longitud = self.analizar_engagement_por_longitud_texto()
    analisis_palabras = self.analizar_engagement_por_palabras_clave()
    analisis_hashtags = self.analizar_engagement_por_hashtag_count()
    analisis_mentions = self.analizar_engagement_por_mentions()
    analisis_cta = self.analizar_engagement_por_cta()
    mejor_longitud = analisis_longitud.get('mejor_longitud', {})
    mejores_palabras = analisis_palabras.get('mejores_palabras_clave', [])
    mejor_hashtag_count = analisis_hashtags.get('mejor_count', {})
    mejor_mentions = analisis_mentions.get('mejor_tipo', {})
    mejor_cta = analisis_cta.get('mejor_tipo', {})
    return {'analisis_longitud': analisis_longitud, 'analisis_palabras': analisis_palabras, 'analisis_hashtags': analisis_hashtags, 'analisis_mentions': analisis_mentions, 'analisis_cta': analisis_cta, 'configuracion_optima_contenido': {'longitud_optima': mejor_longitud.get('categoria'), 'palabras_clave_optimas': [p['palabra_clave'] for p in mejores_palabras[:3]], 'hashtags_optimos': mejor_hashtag_count.get('categoria'), 'mentions': mejor_mentions.get('tipo') == 'con_mentions', 'cta': mejor_cta.get('tipo') == 'con_cta'}, 'recomendacion': f"Contenido óptimo: longitud {mejor_longitud.get('categoria', 'N/A')}, palabras clave {', '.join([p['palabra_clave'] for p in mejores_palabras[:2]]) if mejores_palabras else 'N/A'}, {mejor_hashtag_count.get('categoria', 'N/A')} hashtags, {'con' if mejor_mentions.get('tipo') == 'con_mentions' else 'sin'} menciones, {'con' if mejor_cta.get('tipo') == 'con_cta' else 'sin'} CTA"}


def analizar_engagement_por_velocidad_crecimiento(self) -> Dict[str, Any]:
    """Analiza la velocidad de crecimiento del engagement a lo largo del tiempo."""
    if len(self.publicaciones) < 20:
        return {'error': 'Se necesitan al menos 20 publicaciones'}
    publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
    ventanas = []
    ventana_size = max(5, len(publicaciones_ordenadas) // 4)
    for i in range(0, len(publicaciones_ordenadas) - ventana_size + 1, ventana_size):
        ventana = publicaciones_ordenadas[i:i + ventana_size]
        if len(ventana) >= 3:
            ventanas.append({'inicio': ventana[0].fecha_publicacion.isoformat(), 'fin': ventana[-1].fecha_publicacion.isoformat(), 'engagement_promedio': statistics.mean([p.engagement_score for p in ventana]), 'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in ventana])})
    crecimiento = []
    for i in range(1, len(ventanas)):
        crecimiento_porcentaje = ((ventanas[i]['engagement_promedio'] - ventanas[i-1]['engagement_promedio']) / ventanas[i-1]['engagement_promedio'] * 100) if ventanas[i-1]['engagement_promedio'] > 0 else 0
        crecimiento.append({'periodo': f"{ventanas[i-1]['inicio']} a {ventanas[i]['fin']}", 'crecimiento_porcentaje': crecimiento_porcentaje})
    crecimiento_promedio = statistics.mean([c['crecimiento_porcentaje'] for c in crecimiento]) if crecimiento else 0
    tendencia = 'creciente' if crecimiento_promedio > 5 else ('decreciente' if crecimiento_promedio < -5 else 'estable')
    return {'ventanas_analisis': ventanas, 'crecimiento_por_periodo': crecimiento, 'crecimiento_promedio': crecimiento_promedio, 'tendencia': tendencia, 'recomendacion': f"Tendencia {tendencia} ({crecimiento_promedio:.1f}%). {'Mantener estrategia actual' if tendencia == 'creciente' else 'Revisar estrategia de contenido' if tendencia == 'decreciente' else 'Optimizar para acelerar crecimiento'}"}


def analizar_engagement_por_consistencia(self) -> Dict[str, Any]:
    """Analiza la consistencia del engagement a lo largo del tiempo."""
    if len(self.publicaciones) < 15:
        return {'error': 'Se necesitan al menos 15 publicaciones'}
    engagement_scores = [p.engagement_score for p in self.publicaciones]
    engagement_rates = [p.engagement_rate for p in self.publicaciones]
    desviacion_estandar_score = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
    desviacion_estandar_rate = statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0
    promedio_score = statistics.mean(engagement_scores)
    promedio_rate = statistics.mean(engagement_rates)
    coeficiente_variacion_score = (desviacion_estandar_score / promedio_score * 100) if promedio_score > 0 else 0
    coeficiente_variacion_rate = (desviacion_estandar_rate / promedio_rate * 100) if promedio_rate > 0 else 0
    consistencia_score = 'alta' if coeficiente_variacion_score < 20 else ('media' if coeficiente_variacion_score < 40 else 'baja')
    consistencia_rate = 'alta' if coeficiente_variacion_rate < 20 else ('media' if coeficiente_variacion_rate < 40 else 'baja')
    return {'coeficiente_variacion_score': coeficiente_variacion_score, 'coeficiente_variacion_rate': coeficiente_variacion_rate, 'consistencia_score': consistencia_score, 'consistencia_rate': consistencia_rate, 'desviacion_estandar_score': desviacion_estandar_score, 'desviacion_estandar_rate': desviacion_estandar_rate, 'recomendacion': f"Consistencia {consistencia_score} en engagement score y {consistencia_rate} en engagement rate. {'Mantener calidad consistente' if consistencia_score == 'alta' else 'Mejorar consistencia del contenido'}"}


def analizar_engagement_por_momentum(self) -> Dict[str, Any]:
    """Analiza el momentum del engagement (tendencia reciente vs histórica)."""
    if len(self.publicaciones) < 20:
        return {'error': 'Se necesitan al menos 20 publicaciones'}
    publicaciones_ordenadas = sorted(self.publicaciones, key=lambda x: x.fecha_publicacion)
    mitad = len(publicaciones_ordenadas) // 2
    historico = publicaciones_ordenadas[:mitad]
    reciente = publicaciones_ordenadas[mitad:]
    engagement_historico = statistics.mean([p.engagement_score for p in historico])
    engagement_reciente = statistics.mean([p.engagement_score for p in reciente])
    engagement_rate_historico = statistics.mean([p.engagement_rate for p in historico])
    engagement_rate_reciente = statistics.mean([p.engagement_rate for p in reciente])
    cambio_score = ((engagement_reciente - engagement_historico) / engagement_historico * 100) if engagement_historico > 0 else 0
    cambio_rate = ((engagement_rate_reciente - engagement_rate_historico) / engagement_rate_historico * 100) if engagement_rate_historico > 0 else 0
    momentum = 'positivo' if cambio_score > 10 else ('negativo' if cambio_score < -10 else 'neutral')
    return {'engagement_historico': engagement_historico, 'engagement_reciente': engagement_reciente, 'engagement_rate_historico': engagement_rate_historico, 'engagement_rate_reciente': engagement_rate_reciente, 'cambio_score_porcentaje': cambio_score, 'cambio_rate_porcentaje': cambio_rate, 'momentum': momentum, 'recomendacion': f"Momentum {momentum} ({cambio_score:.1f}% cambio). {'Acelerar estrategia actual' if momentum == 'positivo' else 'Revisar y ajustar estrategia' if momentum == 'negativo' else 'Optimizar para generar momentum positivo'}"}


def analizar_engagement_por_competencia_relativa(self) -> Dict[str, Any]:
    """Analiza el engagement relativo comparado con benchmarks de la industria."""
    if len(self.publicaciones) < 10:
        return {'error': 'Se necesitan al menos 10 publicaciones'}
    engagement_promedio = statistics.mean([p.engagement_score for p in self.publicaciones])
    engagement_rate_promedio = statistics.mean([p.engagement_rate for p in self.publicaciones])
    benchmarks_industria = {'alto': 1000, 'medio': 500, 'bajo': 200}
    benchmarks_rate = {'alto': 5.0, 'medio': 2.5, 'bajo': 1.0}
    nivel_score = 'alto' if engagement_promedio >= benchmarks_industria['alto'] else ('medio' if engagement_promedio >= benchmarks_industria['medio'] else 'bajo')
    nivel_rate = 'alto' if engagement_rate_promedio >= benchmarks_rate['alto'] else ('medio' if engagement_rate_promedio >= benchmarks_rate['medio'] else 'bajo')
    diferencia_score = engagement_promedio - benchmarks_industria['medio']
    diferencia_rate = engagement_rate_promedio - benchmarks_rate['medio']
    return {'engagement_promedio': engagement_promedio, 'engagement_rate_promedio': engagement_rate_promedio, 'nivel_score': nivel_score, 'nivel_rate': nivel_rate, 'diferencia_score': diferencia_score, 'diferencia_rate': diferencia_rate, 'benchmarks': {'score': benchmarks_industria, 'rate': benchmarks_rate}, 'recomendacion': f"Nivel {nivel_score} en engagement score y {nivel_rate} en engagement rate. {'Mantener excelente rendimiento' if nivel_score == 'alto' and nivel_rate == 'alto' else 'Mejorar estrategia para alcanzar benchmarks altos'}"}


def generar_reporte_performance_completo(self) -> Dict[str, Any]:
    """Genera un reporte completo de performance consolidando múltiples análisis."""
    if len(self.publicaciones) < 20:
        return {'error': 'Se necesitan al menos 20 publicaciones'}
    reporte = {'fecha_generacion': datetime.now().isoformat(), 'resumen_ejecutivo': {}, 'analisis_detallados': {}, 'recomendaciones_prioritarias': []}
    analisis_crecimiento = self.analizar_engagement_por_velocidad_crecimiento()
    analisis_consistencia = self.analizar_engagement_por_consistencia()
    analisis_momentum = self.analizar_engagement_por_momentum()
    analisis_competencia = self.analizar_engagement_por_competencia_relativa()
    reporte['resumen_ejecutivo'] = {'tendencia': analisis_crecimiento.get('tendencia'), 'momentum': analisis_momentum.get('momentum'), 'nivel_competencia': analisis_competencia.get('nivel_score'), 'consistencia': analisis_consistencia.get('consistencia_score')}
    reporte['analisis_detallados'] = {'crecimiento': analisis_crecimiento, 'consistencia': analisis_consistencia, 'momentum': analisis_momentum, 'competencia': analisis_competencia}
    if analisis_momentum.get('momentum') == 'negativo':
        reporte['recomendaciones_prioritarias'].append('Revisar y ajustar estrategia de contenido inmediatamente')
    if analisis_consistencia.get('consistencia_score') == 'baja':
        reporte['recomendaciones_prioritarias'].append('Mejorar consistencia del contenido')
    if analisis_competencia.get('nivel_score') == 'bajo':
        reporte['recomendaciones_prioritarias'].append('Optimizar para alcanzar benchmarks de la industria')
    if analisis_crecimiento.get('tendencia') == 'decreciente':
        reporte['recomendaciones_prioritarias'].append('Analizar causas de decrecimiento y corregir')
    return reporte


def optimizar_post_existente(self, titulo_actual: str, hashtags_actuales: List[str] = None) -> Dict[str, Any]:
    """
    Optimiza un post existente basándose en mejores prácticas y análisis histórico.
    
    Args:
        titulo_actual: Texto actual del post
        hashtags_actuales: Hashtags actuales
        
    Returns:
        Versión optimizada del post con explicaciones
    """
    hashtags_actuales = hashtags_actuales or []
    
    # Analizar post actual
    validacion_actual = {}
    score_actual = 0
    if hasattr(self, 'validar_post_linkedin'):
        try:
            validacion_actual = self.validar_post_linkedin(titulo_actual, hashtags_actuales)
            score_actual = validacion_actual.get('score', 0)
        except:
            pass
    
    # Generar mejoras
    mejoras = {}
    if hasattr(self, 'sugerir_mejoras_post'):
        try:
            mejoras = self.sugerir_mejoras_post(titulo_actual, hashtags_actuales)
        except:
            mejoras = {'mejoras_criticas': [], 'mejoras_importantes': [], 'mejoras_opcionales': []}
    
    # Construir versión optimizada
    titulo_optimizado = titulo_actual
    hashtags_optimizados = hashtags_actuales.copy()
    cambios_aplicados = []
    
    # Aplicar mejoras críticas
    if mejoras.get('mejoras_criticas'):
        for mejora in mejoras['mejoras_criticas']:
            if 'hook' in mejora.get('problema', '').lower():
                # Agregar hook si no existe
                if hasattr(self, '_tiene_hook_efectivo') and not self._tiene_hook_efectivo(titulo_optimizado):
                    hook_sugerido = "El problema que nadie quiere admitir:"
                    titulo_optimizado = f"{hook_sugerido}\n\n{titulo_optimizado}"
                    cambios_aplicados.append("Hook agregado al inicio")
            
            if 'hashtags' in mejora.get('problema', '').lower():
                # Agregar hashtags si faltan
                if len(hashtags_optimizados) < 5:
                    hashtags_faltantes = 5 - len(hashtags_optimizados)
                    hashtags_optimizados.extend([f"#Hashtag{i+1}" for i in range(hashtags_faltantes)])
                    cambios_aplicados.append(f"{hashtags_faltantes} hashtags agregados")
    
    # Aplicar mejoras importantes
    if mejoras.get('mejoras_importantes'):
        for mejora in mejoras['mejoras_importantes']:
            if 'cta' in mejora.get('problema', '').lower():
                if hasattr(self, '_tiene_cta_efectivo') and not self._tiene_cta_efectivo(titulo_optimizado):
                    titulo_optimizado += "\n\n¿Listo para optimizar? Comenta 'SÍ' o envíame un mensaje."
                    cambios_aplicados.append("CTA agregado")
            
            if 'pregunta' in mejora.get('problema', '').lower():
                if '?' not in titulo_optimizado:
                    titulo_optimizado += "\n\n¿Cuál es tu experiencia? Comparte en comentarios 👇"
                    cambios_aplicados.append("Pregunta de engagement agregada")
    
    # Validar versión optimizada
    validacion_optimizada = {}
    score_optimizado = 0
    if hasattr(self, 'validar_post_linkedin'):
        try:
            validacion_optimizada = self.validar_post_linkedin(titulo_optimizado, hashtags_optimizados)
            score_optimizado = validacion_optimizada.get('score', 0)
        except:
            pass
    
    return {
        'version_original': {
            'titulo': titulo_actual,
            'hashtags': hashtags_actuales,
            'score': score_actual,
            'longitud': len(titulo_actual)
        },
        'version_optimizada': {
            'titulo': titulo_optimizado,
            'hashtags': hashtags_optimizados,
            'score': score_optimizado,
            'longitud': len(titulo_optimizado)
        },
        'mejora': {
            'score_antes': score_actual,
            'score_despues': score_optimizado,
            'mejora_puntos': score_optimizado - score_actual,
            'mejora_porcentual': ((score_optimizado - score_actual) / score_actual * 100) if score_actual > 0 else 0
        },
        'cambios_aplicados': cambios_aplicados,
        'recomendaciones_adicionales': mejoras.get('mejoras_opcionales', [])
    }


def predecir_engagement_post(self, titulo: str, hashtags: List[str] = None, 
                             plataforma: str = 'LinkedIn', horario: int = 9, 
                             dia_semana: str = 'Martes') -> Dict[str, Any]:
    """
    Predice el engagement esperado de un post antes de publicarlo.
    
    Args:
        titulo: Texto del post
        hashtags: Lista de hashtags
        plataforma: Plataforma objetivo
        horario: Hora de publicación (0-23)
        dia_semana: Día de la semana
        
    Returns:
        Predicción de engagement con confianza
    """
    hashtags = hashtags or []
    
    # Calcular score de optimización
    score = {}
    if hasattr(self, 'calcular_score_optimizacion'):
        try:
            score = self.calcular_score_optimizacion(titulo, hashtags, plataforma)
        except:
            score = {'porcentaje': 50}
    else:
        score = {'porcentaje': 50}
    
    # Analizar posts históricos similares
    posts_similares = []
    for p in self.publicaciones:
        if p.plataforma.lower() == plataforma.lower():
            palabras_titulo = set(titulo.lower().split())
            palabras_post = set(p.titulo.lower().split())
            similitud = len(palabras_titulo & palabras_post) / max(len(palabras_titulo), 1)
            if similitud > 0.2:  # Al menos 20% de palabras en común
                posts_similares.append(p)
    
    # Calcular engagement esperado basado en score y posts similares
    if posts_similares:
        engagement_base = statistics.mean([p.engagement_rate for p in posts_similares])
    else:
        # Usar promedio general si no hay similares
        posts_plataforma = [p for p in self.publicaciones if p.plataforma.lower() == plataforma.lower()]
        engagement_base = statistics.mean([p.engagement_rate for p in posts_plataforma]) if posts_plataforma else 3.0
    
    # Ajustar según score de optimización
    factor_score = score.get('porcentaje', 50) / 100
    engagement_esperado = engagement_base * (0.7 + 0.6 * factor_score)  # Rango 0.7x a 1.3x
    
    # Ajustar según horario y día
    horarios_optimos = {8, 9, 10, 12, 13, 17, 18}
    dias_optimos = {'Martes', 'Miércoles', 'Jueves'}
    
    factor_horario = 1.15 if horario in horarios_optimos else 0.9
    factor_dia = 1.1 if dia_semana in dias_optimos else 0.95
    
    engagement_ajustado = engagement_esperado * factor_horario * factor_dia
    
    # Calcular confianza
    confianza = min(95, 50 + (len(posts_similares) * 5) + (score.get('porcentaje', 50) * 0.3))
    
    # Clasificación
    if engagement_ajustado >= 6:
        clasificacion = 'Excelente'
        emoji = '🏆'
    elif engagement_ajustado >= 4:
        clasificacion = 'Muy Bueno'
        emoji = '✅'
    elif engagement_ajustado >= 3:
        clasificacion = 'Bueno'
        emoji = '👍'
    else:
        clasificacion = 'Necesita Mejoras'
        emoji = '⚠️'
    
    return {
        'prediccion': {
            'engagement_rate_esperado': engagement_ajustado,
            'engagement_rate_base': engagement_base,
            'confianza': confianza,
            'clasificacion': clasificacion,
            'emoji': emoji
        },
        'factores': {
            'score_optimizacion': score.get('porcentaje', 50),
            'horario_optimo': horario in horarios_optimos,
            'dia_optimo': dia_semana in dias_optimos,
            'posts_similares_analizados': len(posts_similares)
        },
        'recomendaciones': [
            f"Engagement esperado: {engagement_ajustado:.2f}%",
            f"Confianza: {confianza:.1f}%",
            f"Score de optimización: {score.get('porcentaje', 50):.1f}%",
            f"Horario {'óptimo' if horario in horarios_optimos else 'subóptimo'}",
            f"Día {'óptimo' if dia_semana in dias_optimos else 'subóptimo'}"
        ]
    }


def generar_ideas_contenido_linkedin(self, industria: str, num_ideas: int = 5) -> List[Dict[str, Any]]:
    """
    Genera ideas de contenido optimizadas para LinkedIn basadas en análisis histórico.
    
    Args:
        industria: Industria objetivo
        num_ideas: Número de ideas a generar
        
    Returns:
        Lista de ideas de contenido optimizadas
    """
    # Analizar posts exitosos
    posts_exitosos = sorted(self.publicaciones, key=lambda x: x.engagement_rate, reverse=True)[:10]
    
    # Extraer patrones
    tipos_exitosos = Counter([p.tipo_contenido for p in posts_exitosos]).most_common()
    
    ideas = []
    
    # Generar ideas basadas en variaciones exitosas
    variaciones_temas = [
        f"El problema que nadie quiere admitir en {industria}",
        f"Cómo empresas líderes en {industria} están optimizando",
        f"Estadísticas que importan en {industria}",
        f"El futuro de {industria}: tendencias clave",
        f"Casos de éxito en {industria}: lecciones aprendidas"
    ]
    
    for i, tema_base in enumerate(variaciones_temas[:num_ideas], 1):
        # Generar estructura completa
        hook = tema_base
        problema = f"En {industria}, los profesionales enfrentan desafíos constantes..."
        solucion = f"Con las estrategias correctas, puedes transformar..."
        cta = "¿Listo para optimizar? Comenta 'SÍ' o envíame un mensaje."
        pregunta = f"¿Cuál es tu mayor desafío en {industria}? Comparte en comentarios 👇"
        
        titulo_completo = f"{hook}\n\n{problema}\n\n{solucion}\n\n{cta}\n\n{pregunta}"
        
        # Generar hashtags relevantes
        hashtags = [
            f"#{industria}",
            "#Innovación",
            "#Estrategia",
            "#Liderazgo",
            "#TransformaciónDigital",
            "#Productividad",
            "#Éxito"
        ]
        
        # Predecir engagement
        prediccion = {}
        if hasattr(self, 'predecir_engagement_post'):
            try:
                prediccion = self.predecir_engagement_post(titulo_completo, hashtags)
            except:
                pass
        
        # Calcular score
        score = {}
        if hasattr(self, 'calcular_score_optimizacion'):
            try:
                score = self.calcular_score_optimizacion(titulo_completo, hashtags)
            except:
                pass
        
        ideas.append({
            'idea': i,
            'tema': tema_base,
            'titulo_completo': titulo_completo,
            'hashtags_sugeridos': hashtags[:7],
            'tipo_contenido': tipos_exitosos[0][0] if tipos_exitosos else 'X',
            'longitud': len(titulo_completo),
            'prediccion_engagement': prediccion.get('prediccion', {}),
            'score_optimizacion': score,
            'recomendaciones': [
                "Publicar en Martes, Miércoles o Jueves",
                "Horario: 8-10 AM o 12-1 PM",
                "Responde a comentarios en primeras 2 horas",
                "Comparte en tu red personal"
            ]
        })
    
    return ideas


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.1
# ============================================================================

def exportar_reporte_linkedin(self, reporte: Dict[str, Any], output_file: str = None) -> Dict[str, Any]:
    """
    Exporta un reporte específico optimizado para LinkedIn en formato JSON y HTML.
    
    Args:
        reporte: Reporte completo del análisis
        output_file: Archivo de salida (opcional)
        
    Returns:
        Diccionario con rutas de archivos generados
    """
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"reporte_linkedin_{timestamp}"
    
    archivos_generados = {}
    
    # Extraer solo datos relevantes de LinkedIn
    reporte_linkedin = {
        'fecha_analisis': datetime.now().isoformat(),
        'analisis_linkedin': reporte.get('analisis_linkedin', {}),
        'recomendaciones_linkedin': reporte.get('recomendaciones_linkedin', []),
        'resumen_ejecutivo': {
            'total_posts_linkedin': reporte.get('analisis_linkedin', {}).get('total_posts_linkedin', 0),
            'engagement_promedio': reporte.get('analisis_linkedin', {}).get('engagement_promedio_linkedin', 0),
            'mejor_post': reporte.get('analisis_linkedin', {}).get('mejor_post_linkedin', {})
        },
        'metricas_clave': {
            'longitud_optima': reporte.get('analisis_linkedin', {}).get('longitud_optima', {}),
            'hashtags_optimo': reporte.get('analisis_linkedin', {}).get('hashtags_optimo', {}),
            'horarios_optimos': reporte.get('analisis_linkedin', {}).get('horarios_linkedin', {}),
            'formato_optimo': reporte.get('analisis_linkedin', {}).get('formato_analisis', {})
        }
    }
    
    # Exportar JSON
    json_file = f"{output_file}.json"
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(reporte_linkedin, f, indent=2, ensure_ascii=False, default=str)
        archivos_generados['json'] = json_file
    except Exception as e:
        print(f"Error exportando JSON: {e}")
    
    # Exportar HTML específico para LinkedIn
    html_file = f"{output_file}.html"
    try:
        html_content = self._generar_html_linkedin(reporte_linkedin)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        archivos_generados['html'] = html_file
    except Exception as e:
        print(f"Error exportando HTML: {e}")
    
    return {
        'archivos': archivos_generados,
        'reporte': reporte_linkedin
    }


def _generar_html_linkedin(self, reporte: Dict[str, Any]) -> str:
    """Genera HTML específico para reporte de LinkedIn."""
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte LinkedIn - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #0077b5; border-bottom: 3px solid #0077b5; padding-bottom: 10px; }}
        h2 {{ color: #0077b5; margin-top: 30px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #0077b5; border-radius: 4px; }}
        .recomendacion {{ background: #e8f4f8; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .score {{ font-size: 24px; font-weight: bold; color: #0077b5; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #0077b5; color: white; }}
        .badge {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .badge-success {{ background: #28a745; color: white; }}
        .badge-warning {{ background: #ffc107; color: black; }}
        .badge-danger {{ background: #dc3545; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Análisis LinkedIn</h1>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📈 Resumen Ejecutivo</h2>
        <div class="metric">
            <p><strong>Total Posts Analizados:</strong> {reporte.get('resumen_ejecutivo', {}).get('total_posts_linkedin', 0)}</p>
            <p><strong>Engagement Promedio:</strong> <span class="score">{reporte.get('resumen_ejecutivo', {}).get('engagement_promedio', 0):.2f}%</span></p>
        </div>
        
        <h2>💡 Recomendaciones Clave</h2>
    """
    
    recomendaciones = reporte.get('recomendaciones_linkedin', [])
    for rec in recomendaciones:
        prioridad_class = 'badge-danger' if rec.get('prioridad') == 'Alta' else 'badge-warning'
        html += f"""
        <div class="recomendacion">
            <span class="badge {prioridad_class}">{rec.get('prioridad', 'Media')}</span>
            <h3>{rec.get('categoria', 'General')}</h3>
            <p><strong>Recomendación:</strong> {rec.get('recomendacion', '')}</p>
            <p><strong>Razón:</strong> {rec.get('razon', '')}</p>
            <p><strong>Acción:</strong> {rec.get('accion', '')}</p>
        </div>
        """
    
    html += """
    </div>
</body>
</html>
    """
    
    return html


def analizar_benchmark_linkedin(self, benchmarks_industria: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analiza el rendimiento de LinkedIn comparado con benchmarks de la industria.
    
    Args:
        benchmarks_industria: Benchmarks personalizados (opcional)
        
    Returns:
        Análisis comparativo con benchmarks
    """
    # Benchmarks por defecto para LinkedIn B2B
    benchmarks_default = {
        'engagement_rate': {
            'excelente': 6.0,
            'bueno': 4.0,
            'promedio': 3.0,
            'bajo': 2.0
        },
        'longitud_optima': {
            'min': 1000,
            'max': 1500,
            'optimo': 1250
        },
        'hashtags_optimo': {
            'min': 5,
            'max': 7,
            'optimo': 6
        },
        'frecuencia_semanal': {
            'min': 3,
            'max': 5,
            'optimo': 4
        }
    }
    
    benchmarks = benchmarks_industria or benchmarks_default
    
    # Analizar posts de LinkedIn
    analisis_linkedin = {}
    if hasattr(self, 'analizar_linkedin_especifico'):
        try:
            analisis_linkedin = self.analizar_linkedin_especifico()
        except:
            pass
    
    if 'error' in analisis_linkedin:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    engagement_promedio = analisis_linkedin.get('engagement_promedio_linkedin', 0)
    
    # Comparar con benchmarks
    comparacion = {
        'engagement_rate': {
            'actual': engagement_promedio,
            'benchmark_excelente': benchmarks['engagement_rate']['excelente'],
            'benchmark_bueno': benchmarks['engagement_rate']['bueno'],
            'benchmark_promedio': benchmarks['engagement_rate']['promedio'],
            'clasificacion': self._clasificar_benchmark(engagement_promedio, benchmarks['engagement_rate']),
            'porcentaje_del_excelente': (engagement_promedio / benchmarks['engagement_rate']['excelente'] * 100) if benchmarks['engagement_rate']['excelente'] > 0 else 0
        }
    }
    
    # Analizar longitud
    if analisis_linkedin.get('longitud_optima'):
        mejor_longitud = max(analisis_linkedin['longitud_optima'].items(), 
                           key=lambda x: x[1].get('engagement_promedio', 0))
        longitud_promedio = sum([len(p.titulo) for p in self.publicaciones 
                                 if p.plataforma.lower() == 'linkedin']) / max(len([p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']), 1)
        
        comparacion['longitud'] = {
            'actual': longitud_promedio,
            'optima': mejor_longitud[0],
            'benchmark_min': benchmarks['longitud_optima']['min'],
            'benchmark_max': benchmarks['longitud_optima']['max'],
            'dentro_rango': benchmarks['longitud_optima']['min'] <= longitud_promedio <= benchmarks['longitud_optima']['max']
        }
    
    # Analizar hashtags
    if analisis_linkedin.get('hashtags_optimo'):
        mejor_num = max(analisis_linkedin['hashtags_optimo'].items(),
                       key=lambda x: x[1].get('engagement_promedio', 0))
        hashtags_promedio = statistics.mean([len(p.hashtags) for p in self.publicaciones 
                                            if p.plataforma.lower() == 'linkedin'])
        
        comparacion['hashtags'] = {
            'actual': hashtags_promedio,
            'optimo': mejor_num[0],
            'benchmark_min': benchmarks['hashtags_optimo']['min'],
            'benchmark_max': benchmarks['hashtags_optimo']['max'],
            'dentro_rango': benchmarks['hashtags_optimo']['min'] <= hashtags_promedio <= benchmarks['hashtags_optimo']['max']
        }
    
    # Generar recomendaciones basadas en benchmarks
    recomendaciones = []
    
    if comparacion['engagement_rate']['porcentaje_del_excelente'] < 80:
        gap = benchmarks['engagement_rate']['excelente'] - engagement_promedio
        recomendaciones.append({
            'categoria': 'Engagement Rate',
            'problema': f'Engagement {gap:.2f}% por debajo del benchmark excelente',
            'accion': 'Optimiza estructura de posts, horarios y hashtags',
            'prioridad': 'Alta'
        })
    
    return {
        'benchmarks': benchmarks,
        'comparacion': comparacion,
        'recomendaciones': recomendaciones,
        'score_general': self._calcular_score_benchmark(comparacion),
        'clasificacion_general': self._clasificar_score_general(comparacion)
    }


def _clasificar_benchmark(self, valor: float, benchmarks: Dict[str, float]) -> str:
    """Clasifica un valor según benchmarks."""
    if valor >= benchmarks['excelente']:
        return 'Excelente'
    elif valor >= benchmarks['bueno']:
        return 'Bueno'
    elif valor >= benchmarks['promedio']:
        return 'Promedio'
    else:
        return 'Bajo'


def _calcular_score_benchmark(self, comparacion: Dict[str, Any]) -> float:
    """Calcula un score general basado en comparación con benchmarks."""
    score = 0
    max_score = 0
    
    if 'engagement_rate' in comparacion:
        porcentaje = comparacion['engagement_rate']['porcentaje_del_excelente']
        score += porcentaje * 0.5  # 50% del score total
        max_score += 50
    
    if 'longitud' in comparacion:
        if comparacion['longitud'].get('dentro_rango'):
            score += 25
        max_score += 25
    
    if 'hashtags' in comparacion:
        if comparacion['hashtags'].get('dentro_rango'):
            score += 25
        max_score += 25
    
    return (score / max_score * 100) if max_score > 0 else 0


def _clasificar_score_general(self, comparacion: Dict[str, Any]) -> str:
    """Clasifica el score general."""
    score = self._calcular_score_benchmark(comparacion)
    
    if score >= 90:
        return 'Excelente'
    elif score >= 75:
        return 'Muy Bueno'
    elif score >= 60:
        return 'Bueno'
    elif score >= 50:
        return 'Necesita Mejoras'
    else:
        return 'Requiere Optimización Urgente'


def generar_estrategia_linkedin_completa(self, objetivo: str = 'aumentar engagement', 
                                         semanas: int = 4) -> Dict[str, Any]:
    """
    Genera una estrategia completa de LinkedIn basada en análisis histórico.
    
    Args:
        objetivo: Objetivo principal ('aumentar engagement', 'generar leads', 'construir autoridad')
        semanas: Número de semanas a planificar
        
    Returns:
        Estrategia completa con calendario, recomendaciones y métricas objetivo
    """
    # Analizar situación actual
    analisis_linkedin = {}
    if hasattr(self, 'analizar_linkedin_especifico'):
        try:
            analisis_linkedin = self.analizar_linkedin_especifico()
        except:
            pass
    
    # Generar calendario
    calendario = {}
    if hasattr(self, 'generar_calendario_linkedin'):
        try:
            calendario = self.generar_calendario_linkedin(semanas)
        except:
            pass
    
    # Generar ideas de contenido
    ideas = []
    if hasattr(self, 'generar_ideas_contenido_linkedin'):
        try:
            # Intentar detectar industria de posts existentes
            industria = 'Tu Industria'  # Default
            ideas = self.generar_ideas_contenido_linkedin(industria, num_ideas=semanas * 5)
        except:
            pass
    
    # Definir métricas objetivo según objetivo
    metricas_objetivo = {}
    engagement_actual = analisis_linkedin.get('engagement_promedio_linkedin', 3.0)
    
    if objetivo == 'aumentar engagement':
        metricas_objetivo = {
            'engagement_rate_objetivo': min(engagement_actual * 1.5, 6.0),
            'mejora_esperada': '+50%',
            'posts_semanales_objetivo': 4,
            'comentarios_objetivo': 20,
            'shares_objetivo': 10
        }
    elif objetivo == 'generar leads':
        metricas_objetivo = {
            'engagement_rate_objetivo': min(engagement_actual * 1.3, 5.0),
            'mejora_esperada': '+30%',
            'posts_semanales_objetivo': 5,
            'cta_clicks_objetivo': 15,
            'mensajes_directos_objetivo': 5
        }
    elif objetivo == 'construir autoridad':
        metricas_objetivo = {
            'engagement_rate_objetivo': min(engagement_actual * 1.2, 4.5),
            'mejora_esperada': '+20%',
            'posts_semanales_objetivo': 3,
            'compartidos_objetivo': 15,
            'comentarios_calidad_objetivo': 10
        }
    else:
        metricas_objetivo = {
            'engagement_rate_objetivo': engagement_actual * 1.25,
            'mejora_esperada': '+25%',
            'posts_semanales_objetivo': 4
        }
    
    # Generar plan de acción
    plan_accion = []
    
    # Semana 1: Optimización
    plan_accion.append({
        'semana': 1,
        'objetivo': 'Optimizar posts existentes',
        'acciones': [
            'Validar todos los posts antes de publicar',
            'Asegurar estructura Hook + CTA + Pregunta',
            'Optimizar hashtags a 5-7 por post',
            'Publicar en horarios óptimos'
        ],
        'metricas': {
            'posts_publicados': 4,
            'engagement_objetivo': engagement_actual * 1.1
        }
    })
    
    # Semana 2-4: Escalamiento
    for semana in range(2, semanas + 1):
        plan_accion.append({
            'semana': semana,
            'objetivo': f'Escalar y optimizar (Semana {semana})',
            'acciones': [
                'Analizar métricas de semana anterior',
                'Duplicar lo que funciona mejor',
                'Experimentar con nuevos formatos',
                'Responder activamente a comentarios',
                'Compartir en grupos relevantes'
            ],
            'metricas': {
                'posts_publicados': metricas_objetivo.get('posts_semanales_objetivo', 4),
                'engagement_objetivo': engagement_actual * (1 + (semana * 0.1))
            }
        })
    
    return {
        'objetivo': objetivo,
        'situacion_actual': {
            'engagement_promedio': engagement_actual,
            'total_posts': analisis_linkedin.get('total_posts_linkedin', 0),
            'mejor_post': analisis_linkedin.get('mejor_post_linkedin', {})
        },
        'metricas_objetivo': metricas_objetivo,
        'calendario': calendario,
        'ideas_contenido': ideas[:semanas * 5],
        'plan_accion': plan_accion,
        'recomendaciones_estrategicas': [
            'Publica consistentemente 3-5 veces por semana',
            'Responde a todos los comentarios en primeras 2 horas',
            'Varía tipos de contenido para mantener interés',
            'Analiza métricas semanalmente y ajusta estrategia',
            'Construye relaciones antes de pedir algo'
        ],
        'kpis_seguimiento': [
            'Engagement rate promedio',
            'Alcance orgánico',
            'Comentarios por post',
            'Compartidos por post',
            'Mensajes directos generados'
        ]
    }


def analizar_roi_linkedin_detallado(self, costo_hora: float = 50.0, 
                                    valor_lead: float = 100.0) -> Dict[str, Any]:
    """
    Analiza ROI detallado de estrategia de LinkedIn.
    
    Args:
        costo_hora: Costo por hora de trabajo
        valor_lead: Valor promedio de un lead
        
    Returns:
        Análisis detallado de ROI
    """
    # Analizar posts de LinkedIn
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Calcular tiempo invertido (estimado)
    tiempo_por_post = 30  # minutos promedio
    tiempo_total_minutos = len(linkedin_posts) * tiempo_por_post
    tiempo_total_horas = tiempo_total_minutos / 60
    costo_total_tiempo = tiempo_total_horas * costo_hora
    
    # Calcular engagement y alcance
    engagement_promedio = statistics.mean([p.engagement_rate for p in linkedin_posts])
    impresiones_totales = sum([p.impresiones for p in linkedin_posts])
    engagement_total = sum([p.engagement_total for p in linkedin_posts])
    
    # Estimar leads generados (asumiendo 1% de engagement se convierte en lead)
    leads_estimados = int(engagement_total * 0.01)
    valor_leads = leads_estimados * valor_lead
    
    # Calcular ROI
    roi = ((valor_leads - costo_total_tiempo) / costo_total_tiempo * 100) if costo_total_tiempo > 0 else 0
    roi_por_post = roi / len(linkedin_posts) if linkedin_posts else 0
    
    # Calcular costo por engagement
    costo_por_engagement = costo_total_tiempo / engagement_total if engagement_total > 0 else 0
    costo_por_lead = costo_total_tiempo / leads_estimados if leads_estimados > 0 else 0
    
    return {
        'inversion': {
            'tiempo_total_horas': tiempo_total_horas,
            'tiempo_total_minutos': tiempo_total_minutos,
            'costo_total': costo_total_tiempo,
            'costo_por_post': costo_total_tiempo / len(linkedin_posts) if linkedin_posts else 0
        },
        'resultados': {
            'posts_publicados': len(linkedin_posts),
            'impresiones_totales': impresiones_totales,
            'engagement_total': engagement_total,
            'engagement_promedio': engagement_promedio,
            'leads_estimados': leads_estimados
        },
        'roi': {
            'valor_leads': valor_leads,
            'costo_total': costo_total_tiempo,
            'roi_porcentual': roi,
            'roi_por_post': roi_por_post,
            'costo_por_engagement': costo_por_engagement,
            'costo_por_lead': costo_por_lead,
            'breakeven_posts': int(costo_total_tiempo / (valor_leads / len(linkedin_posts))) if valor_leads > 0 else 0
        },
        'recomendaciones': [
            f"ROI actual: {roi:.1f}%",
            f"Costo por lead: ${costo_por_lead:.2f}",
            "Optimiza horarios y estructura para mejorar ROI",
            "Enfócate en contenido que genera más leads",
            "Reduce tiempo de creación con templates"
        ] if roi > 0 else [
            "ROI negativo - optimiza estrategia",
            "Reduce tiempo de creación",
            "Enfócate en contenido de alto engagement",
            "Mejora CTAs para aumentar conversión"
        ]
    }


def generar_dashboard_linkedin(self) -> Dict[str, Any]:
    """
    Genera un dashboard completo con todas las métricas de LinkedIn.
    """
    analisis_linkedin = {}
    if hasattr(self, 'analizar_linkedin_especifico'):
        try:
            analisis_linkedin = self.analizar_linkedin_especifico()
        except:
            pass
    
    if 'error' in analisis_linkedin:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    # Calcular métricas del dashboard
    dashboard = {
        'metricas_principales': {
            'total_posts': len(linkedin_posts),
            'engagement_promedio': analisis_linkedin.get('engagement_promedio_linkedin', 0),
            'alcance_total': sum([p.reach for p in linkedin_posts]),
            'impresiones_totales': sum([p.impresiones for p in linkedin_posts]),
            'engagement_total': sum([p.engagement_total for p in linkedin_posts]),
            'posts_virales': len([p for p in linkedin_posts if p.es_viral])
        },
        'tendencias': {
            'engagement_tendencia': self._calcular_tendencia_engagement(linkedin_posts),
            'crecimiento_semanal': self._calcular_crecimiento_semanal(linkedin_posts),
            'mejor_semana': self._identificar_mejor_semana(linkedin_posts)
        },
        'top_performers': {
            'mejor_post': max(linkedin_posts, key=lambda x: x.engagement_rate) if linkedin_posts else None,
            'top_5_posts': sorted(linkedin_posts, key=lambda x: x.engagement_rate, reverse=True)[:5],
            'posts_mas_compartidos': sorted(linkedin_posts, key=lambda x: x.shares, reverse=True)[:5]
        },
        'optimizacion': {
            'longitud_optima': analisis_linkedin.get('longitud_optima', {}),
            'hashtags_optimo': analisis_linkedin.get('hashtags_optimo', {}),
            'horarios_optimos': analisis_linkedin.get('horarios_linkedin', {}),
            'formato_optimo': analisis_linkedin.get('formato_analisis', {})
        },
        'recomendaciones_prioritarias': []
    }
    
    # Agregar recomendaciones
    if hasattr(self, 'generar_recomendaciones_linkedin'):
        try:
            recomendaciones = self.generar_recomendaciones_linkedin()
            dashboard['recomendaciones_prioritarias'] = [r for r in recomendaciones if r.get('prioridad') == 'Alta']
        except:
            pass
    
    return dashboard


def _calcular_tendencia_engagement(self, posts: List[Publicacion]) -> str:
    """Calcula la tendencia de engagement."""
    if len(posts) < 2:
        return 'insuficiente_datos'
    
    posts_ordenados = sorted(posts, key=lambda x: x.fecha_publicacion)
    mitad = len(posts_ordenados) // 2
    
    primera_mitad = posts_ordenados[:mitad]
    segunda_mitad = posts_ordenados[mitad:]
    
    engagement_primera = statistics.mean([p.engagement_rate for p in primera_mitad])
    engagement_segunda = statistics.mean([p.engagement_rate for p in segunda_mitad])
    
    if engagement_segunda > engagement_primera * 1.1:
        return 'creciendo'
    elif engagement_segunda < engagement_primera * 0.9:
        return 'decreciendo'
    else:
        return 'estable'


def _calcular_crecimiento_semanal(self, posts: List[Publicacion]) -> float:
    """Calcula crecimiento semanal promedio."""
    if len(posts) < 7:
        return 0.0
    
    posts_por_semana = defaultdict(list)
    for p in posts:
        semana = p.fecha_publicacion.isocalendar()[1]
        posts_por_semana[semana].append(p)
    
    if len(posts_por_semana) < 2:
        return 0.0
    
    semanas_ordenadas = sorted(posts_por_semana.keys())
    engagement_semanas = [
        statistics.mean([p.engagement_rate for p in posts_por_semana[semana]])
        for semana in semanas_ordenadas
    ]
    
    if len(engagement_semanas) < 2:
        return 0.0
    
    crecimiento = ((engagement_semanas[-1] - engagement_semanas[0]) / engagement_semanas[0] * 100) if engagement_semanas[0] > 0 else 0
    return crecimiento / len(engagement_semanas) if len(engagement_semanas) > 1 else crecimiento


def _identificar_mejor_semana(self, posts: List[Publicacion]) -> Dict[str, Any]:
    """Identifica la semana con mejor rendimiento."""
    if not posts:
        return {}
    
    posts_por_semana = defaultdict(list)
    for p in posts:
        año, semana, _ = p.fecha_publicacion.isocalendar()
        clave = f"{año}-W{semana}"
        posts_por_semana[clave].append(p)
    
    mejor_semana = None
    mejor_engagement = 0
    
    for semana, posts_semana in posts_por_semana.items():
        engagement_promedio = statistics.mean([p.engagement_rate for p in posts_semana])
        if engagement_promedio > mejor_engagement:
            mejor_engagement = engagement_promedio
            mejor_semana = semana
    
    if mejor_semana:
        return {
            'semana': mejor_semana,
            'engagement_promedio': mejor_engagement,
            'total_posts': len(posts_por_semana[mejor_semana]),
            'posts': posts_por_semana[mejor_semana][:3]  # Top 3 posts
        }
    
    return {}


# Agregar nuevos métodos al AnalizadorEngagement
AnalizadorEngagement.generar_contenido_optimizado = generar_contenido_optimizado
AnalizadorEngagement.analizar_ab_test = analizar_ab_test
AnalizadorEngagement.generar_calendario_linkedin = generar_calendario_linkedin
AnalizadorEngagement.optimizar_post_existente = optimizar_post_existente
AnalizadorEngagement.predecir_engagement_post = predecir_engagement_post
AnalizadorEngagement.generar_ideas_contenido_linkedin = generar_ideas_contenido_linkedin
AnalizadorEngagement.exportar_reporte_linkedin = exportar_reporte_linkedin
AnalizadorEngagement._generar_html_linkedin = _generar_html_linkedin
AnalizadorEngagement.analizar_benchmark_linkedin = analizar_benchmark_linkedin
AnalizadorEngagement._clasificar_benchmark = _clasificar_benchmark
AnalizadorEngagement._calcular_score_benchmark = _calcular_score_benchmark
AnalizadorEngagement._clasificar_score_general = _clasificar_score_general
AnalizadorEngagement.generar_estrategia_linkedin_completa = generar_estrategia_linkedin_completa
AnalizadorEngagement.analizar_roi_linkedin_detallado = analizar_roi_linkedin_detallado
AnalizadorEngagement.generar_dashboard_linkedin = generar_dashboard_linkedin
AnalizadorEngagement._calcular_tendencia_engagement = _calcular_tendencia_engagement
AnalizadorEngagement._calcular_crecimiento_semanal = _calcular_crecimiento_semanal
AnalizadorEngagement._identificar_mejor_semana = _identificar_mejor_semana
AnalizadorEngagement.generar_plan_accion_mejora = generar_plan_accion_mejora
AnalizadorEngagement.analizar_retencion_audiencia = analizar_retencion_audiencia
AnalizadorEngagement.optimizar_distribucion_tipos = optimizar_distribucion_tipos
AnalizadorEngagement.analizar_eficacia_cta = analizar_eficacia_cta
AnalizadorEngagement.generar_benchmark_personalizado = generar_benchmark_personalizado
AnalizadorEngagement.analizar_contenido_evergreen_vs_trending = analizar_contenido_evergreen_vs_trending
AnalizadorEngagement.analizar_patrones_cross_platform = analizar_patrones_cross_platform
AnalizadorEngagement.predecir_potencial_viralidad = predecir_potencial_viralidad
AnalizadorEngagement.analizar_engagement_por_longitud_contenido = analizar_engagement_por_longitud_contenido
AnalizadorEngagement.generar_roadmap_contenido = generar_roadmap_contenido
AnalizadorEngagement.analizar_competidores_especificos = analizar_competidores_especificos
AnalizadorEngagement.analizar_palabras_clave_trending = analizar_palabras_clave_trending
AnalizadorEngagement.analizar_engagement_por_formato = analizar_engagement_por_formato
AnalizadorEngagement.generar_ideas_contenido_inteligentes = generar_ideas_contenido_inteligentes
AnalizadorEngagement.analizar_eficiencia_por_recurso = analizar_eficiencia_por_recurso
AnalizadorEngagement.analizar_engagement_por_temporada = analizar_engagement_por_temporada
AnalizadorEngagement.analizar_engagement_por_evento_especial = analizar_engagement_por_evento_especial
AnalizadorEngagement.analizar_engagement_por_dispositivo = analizar_engagement_por_dispositivo
AnalizadorEngagement.analizar_engagement_por_fuente_trafico = analizar_engagement_por_fuente_trafico
AnalizadorEngagement.analizar_engagement_por_colaboracion = analizar_engagement_por_colaboracion
AnalizadorEngagement.analizar_engagement_por_campana = analizar_engagement_por_campana
AnalizadorEngagement.analizar_engagement_por_tipo_interaccion = analizar_engagement_por_tipo_interaccion
AnalizadorEngagement.analizar_engagement_por_duracion_video = analizar_engagement_por_duracion_video
AnalizadorEngagement.analizar_engagement_por_frecuencia_publicacion_detallado = analizar_engagement_por_frecuencia_publicacion_detallado
AnalizadorEngagement.analizar_engagement_por_hora_detallado = analizar_engagement_por_hora_detallado
AnalizadorEngagement.analizar_engagement_por_dia_mes = analizar_engagement_por_dia_mes
AnalizadorEngagement.analizar_engagement_por_mes_ano = analizar_engagement_por_mes_ano
AnalizadorEngagement.analizar_engagement_por_ubicacion = analizar_engagement_por_ubicacion
AnalizadorEngagement.analizar_engagement_por_demografia = analizar_engagement_por_demografia
AnalizadorEngagement.analizar_engagement_por_calidad_contenido = analizar_engagement_por_calidad_contenido
AnalizadorEngagement.analizar_engagement_por_tipo_media = analizar_engagement_por_tipo_media
AnalizadorEngagement.generar_analisis_completo_temporal = generar_analisis_completo_temporal
AnalizadorEngagement.analizar_engagement_por_emocion = analizar_engagement_por_emocion
AnalizadorEngagement.analizar_engagement_por_tema = analizar_engagement_por_tema
AnalizadorEngagement.analizar_engagement_por_autor = analizar_engagement_por_autor
AnalizadorEngagement.analizar_engagement_por_idioma = analizar_engagement_por_idioma
AnalizadorEngagement.analizar_engagement_por_estilo_contenido = analizar_engagement_por_estilo_contenido
AnalizadorEngagement.generar_dashboard_completo = generar_dashboard_completo
AnalizadorEngagement.analizar_engagement_por_longitud_texto = analizar_engagement_por_longitud_texto
AnalizadorEngagement.analizar_engagement_por_palabras_clave = analizar_engagement_por_palabras_clave
AnalizadorEngagement.analizar_engagement_por_hashtag_count = analizar_engagement_por_hashtag_count
AnalizadorEngagement.analizar_engagement_por_mentions = analizar_engagement_por_mentions
AnalizadorEngagement.analizar_engagement_por_cta = analizar_engagement_por_cta
AnalizadorEngagement.generar_analisis_completo_contenido = generar_analisis_completo_contenido


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.3
# ============================================================================

def analizar_audiencia_avanzado(self) -> Dict[str, Any]:
    """
    Análisis avanzado de audiencia basado en engagement y comportamiento.
    
    Returns:
        Análisis detallado de audiencia
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Analizar comportamiento de audiencia
    posts_con_comentarios = [p for p in linkedin_posts if p.comentarios > 0]
    posts_con_shares = [p for p in linkedin_posts if p.shares > 0]
    posts_con_likes = [p for p in linkedin_posts if p.likes > 0]
    
    # Calcular tasas de participación
    tasa_comentarios = len(posts_con_comentarios) / len(linkedin_posts) * 100 if linkedin_posts else 0
    tasa_shares = len(posts_con_shares) / len(linkedin_posts) * 100 if linkedin_posts else 0
    tasa_likes = len(posts_con_likes) / len(linkedin_posts) * 100 if linkedin_posts else 0
    
    # Analizar tipos de contenido que generan más engagement
    tipos_engagement = defaultdict(list)
    for p in linkedin_posts:
        tipos_engagement[p.tipo_contenido].append(p.engagement_rate)
    
    mejor_tipo = max(tipos_engagement.items(), 
                    key=lambda x: statistics.mean(x[1])) if tipos_engagement else None
    
    # Analizar horarios de mayor participación
    horarios_comentarios = Counter([p.fecha_publicacion.hour for p in posts_con_comentarios])
    mejor_horario_comentarios = horarios_comentarios.most_common(1)[0][0] if horarios_comentarios else None
    
    return {
        'metricas_participacion': {
            'tasa_comentarios': tasa_comentarios,
            'tasa_shares': tasa_shares,
            'tasa_likes': tasa_likes,
            'promedio_comentarios_por_post': statistics.mean([p.comentarios for p in linkedin_posts]),
            'promedio_shares_por_post': statistics.mean([p.shares for p in linkedin_posts]),
            'promedio_likes_por_post': statistics.mean([p.likes for p in linkedin_posts])
        },
        'comportamiento_audiencia': {
            'tipo_contenido_preferido': mejor_tipo[0] if mejor_tipo else None,
            'engagement_tipo_preferido': statistics.mean(mejor_tipo[1]) if mejor_tipo else 0,
            'mejor_horario_comentarios': mejor_horario_comentarios,
            'posts_mas_comentados': sorted(linkedin_posts, key=lambda x: x.comentarios, reverse=True)[:5],
            'posts_mas_compartidos': sorted(linkedin_posts, key=lambda x: x.shares, reverse=True)[:5]
        },
        'insights_audiencia': [
            f"La audiencia prefiere contenido tipo {mejor_tipo[0]}" if mejor_tipo else "No hay suficiente datos",
            f"Mejor horario para comentarios: {mejor_horario_comentarios}:00" if mejor_horario_comentarios else "No hay suficiente datos",
            f"{tasa_comentarios:.1f}% de posts generan comentarios",
            f"{tasa_shares:.1f}% de posts son compartidos"
        ],
        'recomendaciones': [
            f"Crear más contenido tipo {mejor_tipo[0]}" if mejor_tipo else "Diversificar tipos de contenido",
            f"Publicar alrededor de las {mejor_horario_comentarios}:00 para más comentarios" if mejor_horario_comentarios else "Experimentar con diferentes horarios",
            "Incluir preguntas para aumentar comentarios",
            "Crear contenido compartible con insights valiosos"
        ]
    }


def repurposing_contenido(self, post_id: str = None, titulo: str = None) -> Dict[str, Any]:
    """
    Genera variaciones de contenido para repurposing en diferentes formatos.
    
    Args:
        post_id: ID del post a repurposing (opcional)
        titulo: Título del post (opcional, si no se proporciona post_id)
        
    Returns:
        Variaciones de contenido para diferentes formatos
    """
    # Obtener post original
    if post_id:
        post_original = next((p for p in self.publicaciones if p.id == post_id), None)
        if not post_original:
            return {'error': f'Post con ID {post_id} no encontrado'}
        titulo_original = post_original.titulo
        hashtags_originales = post_original.hashtags
    elif titulo:
        titulo_original = titulo
        hashtags_originales = []
    else:
        return {'error': 'Debe proporcionar post_id o titulo'}
    
    # Generar variaciones
    variaciones = {
        'carousel': {
            'formato': 'Carousel de LinkedIn',
            'estructura': [
                f"Slide 1: Hook - {titulo_original[:100]}",
                "Slide 2-4: Puntos clave del contenido",
                "Slide 5: CTA y pregunta",
                "Slide 6: Información de contacto"
            ],
            'recomendaciones': [
                "Usar imágenes o gráficos por slide",
                "Mantener texto conciso (máx 50 palabras por slide)",
                "Incluir estadísticas visuales",
                "Terminar con CTA claro"
            ]
        },
        'video_script': {
            'formato': 'Script para Video',
            'estructura': [
                "Hook (0-5 seg): Pregunta o estadística impactante",
                "Problema (5-15 seg): Contexto del problema",
                "Solución (15-45 seg): Solución principal",
                "CTA (45-60 seg): Llamado a la acción",
                "Cierre (60 seg): Invitación a comentar"
            ],
            'script': f"""
[Hook - 5 segundos]
{titulo_original[:100]}

[Desarrollo - 45 segundos]
Desarrolla los puntos clave del contenido original de manera conversacional.

[CTA - 10 segundos]
¿Te ha pasado esto? Comenta abajo o envíame un mensaje.

[Cierre]
No olvides seguir para más contenido sobre este tema.
            """,
            'recomendaciones': [
                "Mantener duración entre 60-90 segundos",
                "Usar subtítulos para mejor accesibilidad",
                "Incluir elementos visuales",
                "Grabar en formato vertical (9:16)"
            ]
        },
        'articulo_linkedin': {
            'formato': 'Artículo de LinkedIn',
            'estructura': [
                "Título impactante",
                "Introducción (2-3 párrafos)",
                "Desarrollo con subtítulos",
                "Conclusión",
                "CTA final"
            ],
            'contenido_expandido': f"""
# {titulo_original}

## Introducción
[Expandir el contenido original con más contexto y profundidad]

## Puntos Clave
[Desarrollar cada punto del contenido original]

## Conclusión
[Resumir y reforzar el mensaje principal]

## Próximos Pasos
[CTA y llamada a la acción]
            """,
            'recomendaciones': [
                "Expandir a 1000-2000 palabras",
                "Incluir subtítulos para mejor lectura",
                "Agregar ejemplos y casos de estudio",
                "Incluir imágenes o gráficos"
            ]
        },
        'newsletter': {
            'formato': 'Newsletter',
            'estructura': [
                "Asunto del email",
                "Saludo personalizado",
                "Resumen ejecutivo",
                "Contenido principal",
                "CTA",
                "Cierre"
            ],
            'plantilla': f"""
Asunto: {titulo_original[:50]}

Hola [Nombre],

{titulo_original}

[Desarrollo del contenido]

¿Te interesa saber más? [CTA]

Saludos,
[Tu nombre]
            """,
            'recomendaciones': [
                "Personalizar saludo",
                "Mantener formato scannable",
                "Incluir enlaces relevantes",
                "Agregar valor adicional exclusivo"
            ]
        },
        'thread_twitter': {
            'formato': 'Thread de Twitter/X',
            'estructura': [
                "Tweet 1: Hook y contexto",
                "Tweets 2-5: Puntos clave",
                "Tweet final: CTA"
            ],
            'thread': [
                f"1/ {titulo_original[:200]}",
                "2/ [Punto clave 1]",
                "3/ [Punto clave 2]",
                "4/ [Punto clave 3]",
                f"5/ {titulo_original[:150]} ¿Qué opinas? RT si te parece útil 👇"
            ],
            'recomendaciones': [
                "Mantener cada tweet bajo 280 caracteres",
                "Usar numeración (1/5, 2/5, etc.)",
                "Incluir emojis estratégicamente",
                "Terminar con pregunta o CTA"
            ]
        }
    }
    
    return {
        'post_original': {
            'titulo': titulo_original[:100],
            'hashtags': hashtags_originales
        },
        'variaciones': variaciones,
        'recomendaciones_generales': [
            "Adapta el contenido al formato específico",
            "Mantén el mensaje central consistente",
            "Optimiza para cada plataforma",
            "Mide el rendimiento de cada variación"
        ]
    }


def analizar_conversion_cta(self) -> Dict[str, Any]:
    """
    Analiza la efectividad de los CTAs en los posts.
    
    Returns:
        Análisis de conversión de CTAs
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Detectar CTAs en posts
    cta_patterns = [
        'comenta', 'comparte', 'envía', 'descarga', 'visita', 'suscríbete',
        'regístrate', 'contacta', 'mensaje', 'dm', 'link', 'click',
        'sí', 'no', 'cuéntame', 'dime', 'opina'
    ]
    
    posts_con_cta = []
    posts_sin_cta = []
    
    for post in linkedin_posts:
        tiene_cta = any(pattern in post.titulo.lower() for pattern in cta_patterns)
        if tiene_cta:
            posts_con_cta.append(post)
        else:
            posts_sin_cta.append(post)
    
    # Calcular métricas
    engagement_con_cta = statistics.mean([p.engagement_rate for p in posts_con_cta]) if posts_con_cta else 0
    engagement_sin_cta = statistics.mean([p.engagement_rate for p in posts_sin_cta]) if posts_sin_cta else 0
    
    # Analizar tipos de CTA más efectivos
    cta_tipos = defaultdict(list)
    for post in posts_con_cta:
        for pattern in cta_patterns:
            if pattern in post.titulo.lower():
                cta_tipos[pattern].append(post.engagement_rate)
                break
    
    mejor_cta = max(cta_tipos.items(), 
                   key=lambda x: statistics.mean(x[1])) if cta_tipos else None
    
    # Calcular tasa de conversión estimada
    conversion_rate_con_cta = statistics.mean([(p.comentarios + p.shares) / max(p.impresiones, 1) * 100 
                                               for p in posts_con_cta]) if posts_con_cta else 0
    conversion_rate_sin_cta = statistics.mean([(p.comentarios + p.shares) / max(p.impresiones, 1) * 100 
                                              for p in posts_sin_cta]) if posts_sin_cta else 0
    
    return {
        'analisis_cta': {
            'posts_con_cta': len(posts_con_cta),
            'posts_sin_cta': len(posts_sin_cta),
            'porcentaje_con_cta': len(posts_con_cta) / len(linkedin_posts) * 100,
            'engagement_con_cta': engagement_con_cta,
            'engagement_sin_cta': engagement_sin_cta,
            'diferencia_engagement': engagement_con_cta - engagement_sin_cta,
            'mejora_por_cta': ((engagement_con_cta - engagement_sin_cta) / engagement_sin_cta * 100) if engagement_sin_cta > 0 else 0
        },
        'tipos_cta': {
            'mejor_cta': mejor_cta[0] if mejor_cta else None,
            'engagement_mejor_cta': statistics.mean(mejor_cta[1]) if mejor_cta else 0,
            'distribucion_ctas': {k: len(v) for k, v in cta_tipos.items()}
        },
        'conversion': {
            'tasa_conversion_con_cta': conversion_rate_con_cta,
            'tasa_conversion_sin_cta': conversion_rate_sin_cta,
            'mejora_conversion': conversion_rate_con_cta - conversion_rate_sin_cta
        },
        'recomendaciones': [
            f"{'Usar' if engagement_con_cta > engagement_sin_cta else 'Mejorar'} CTAs - {'mejoran' if engagement_con_cta > engagement_sin_cta else 'no mejoran'} engagement",
            f"Usar CTA tipo '{mejor_cta[0]}'" if mejor_cta else "Experimentar con diferentes tipos de CTA",
            "Incluir CTAs específicos y accionables",
            "Colocar CTA cerca del final del post",
            "Variar tipos de CTA para evitar monotonía"
        ]
    }


def generar_reportes_ejecutivos(self, periodo: str = 'mensual') -> Dict[str, Any]:
    """
    Genera reportes ejecutivos optimizados para stakeholders.
    
    Args:
        periodo: Período del reporte ('semanal', 'mensual', 'trimestral')
        
    Returns:
        Reporte ejecutivo completo
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Filtrar por período
    fecha_limite = datetime.now()
    if periodo == 'semanal':
        fecha_limite -= timedelta(weeks=1)
    elif periodo == 'mensual':
        fecha_limite -= timedelta(days=30)
    elif periodo == 'trimestral':
        fecha_limite -= timedelta(days=90)
    
    posts_periodo = [p for p in linkedin_posts if p.fecha_publicacion >= fecha_limite]
    
    if not posts_periodo:
        return {'error': f'No hay posts en el período {periodo} seleccionado'}
    
    # Calcular métricas clave
    total_posts = len(posts_periodo)
    engagement_promedio = statistics.mean([p.engagement_rate for p in posts_periodo])
    alcance_total = sum([p.reach for p in posts_periodo])
    impresiones_totales = sum([p.impresiones for p in posts_periodo])
    engagement_total = sum([p.engagement_total for p in posts_periodo])
    
    # Comparar con período anterior
    posts_anteriores = [p for p in linkedin_posts if p.fecha_publicacion < fecha_limite]
    engagement_anterior = statistics.mean([p.engagement_rate for p in posts_anteriores]) if posts_anteriores else engagement_promedio
    
    crecimiento = ((engagement_promedio - engagement_anterior) / engagement_anterior * 100) if engagement_anterior > 0 else 0
    
    # Identificar top performers
    top_posts = sorted(posts_periodo, key=lambda x: x.engagement_rate, reverse=True)[:3]
    
    # Análisis de tendencias
    tendencia = 'creciendo' if crecimiento > 5 else 'decreciendo' if crecimiento < -5 else 'estable'
    
    return {
        'periodo': periodo,
        'fecha_reporte': datetime.now().isoformat(),
        'resumen_ejecutivo': {
            'total_posts': total_posts,
            'engagement_promedio': engagement_promedio,
            'alcance_total': alcance_total,
            'impresiones_totales': impresiones_totales,
            'engagement_total': engagement_total,
            'crecimiento': crecimiento,
            'tendencia': tendencia
        },
        'metricas_clave': {
            'engagement_rate': {
                'actual': engagement_promedio,
                'anterior': engagement_anterior,
                'cambio': crecimiento,
                'tendencia': tendencia
            },
            'alcance_promedio': alcance_total / total_posts if total_posts > 0 else 0,
            'impresiones_promedio': impresiones_totales / total_posts if total_posts > 0 else 0,
            'engagement_por_post': engagement_total / total_posts if total_posts > 0 else 0
        },
        'top_performers': [
            {
                'titulo': p.titulo[:100],
                'engagement_rate': p.engagement_rate,
                'alcance': p.reach,
                'fecha': p.fecha_publicacion.strftime('%Y-%m-%d')
            }
            for p in top_posts
        ],
        'insights_clave': [
            f"Engagement {'creció' if crecimiento > 0 else 'decreció'} {abs(crecimiento):.1f}% vs período anterior",
            f"Top post alcanzó {top_posts[0].engagement_rate:.2f}% engagement" if top_posts else "No hay posts destacados",
            f"Promedio de {engagement_total / total_posts:.0f} interacciones por post" if total_posts > 0 else "No hay datos"
        ],
        'recomendaciones_ejecutivas': [
            f"{'Mantener' if tendencia == 'creciendo' else 'Revisar'} estrategia actual",
            f"Replicar elementos de top performers",
            f"{'Aumentar' if total_posts < 10 else 'Mantener'} frecuencia de publicación",
            "Continuar monitoreo de métricas clave"
        ]
    }


def analizar_colaboraciones(self, posts_colaboracion: List[Publicacion] = None) -> Dict[str, Any]:
    """
    Analiza el impacto de colaboraciones e influencers en el engagement.
    
    Args:
        posts_colaboracion: Lista de posts que son colaboraciones (opcional)
        
    Returns:
        Análisis de impacto de colaboraciones
    """
    # Detectar posts de colaboración (por keywords o tags)
    if not posts_colaboracion:
        keywords_colaboracion = ['colaboración', 'con', 'junto a', 'invitado', 'guest', 'partnership']
        posts_colaboracion = [p for p in self.publicaciones 
                            if any(keyword in p.titulo.lower() for keyword in keywords_colaboracion)]
    
    if not posts_colaboracion:
        return {'error': 'No se encontraron posts de colaboración'}
    
    # Comparar con posts regulares
    posts_regulares = [p for p in self.publicaciones if p not in posts_colaboracion]
    
    engagement_colaboracion = statistics.mean([p.engagement_rate for p in posts_colaboracion])
    engagement_regular = statistics.mean([p.engagement_rate for p in posts_regulares]) if posts_regulares else 0
    
    diferencia = engagement_colaboracion - engagement_regular
    mejora_porcentual = ((engagement_colaboracion - engagement_regular) / engagement_regular * 100) if engagement_regular > 0 else 0
    
    return {
        'analisis_colaboraciones': {
            'total_colaboraciones': len(posts_colaboracion),
            'engagement_colaboracion': engagement_colaboracion,
            'engagement_regular': engagement_regular,
            'diferencia': diferencia,
            'mejora_porcentual': mejora_porcentual,
            'es_efectivo': engagement_colaboracion > engagement_regular
        },
        'top_colaboraciones': sorted(posts_colaboracion, 
                                    key=lambda x: x.engagement_rate, 
                                    reverse=True)[:5],
        'recomendaciones': [
            f"{'Continuar' if engagement_colaboracion > engagement_regular else 'Revisar'} estrategia de colaboraciones",
            "Identificar colaboradores de mayor impacto",
            "Diversificar tipos de colaboraciones",
            "Medir ROI de cada colaboración"
        ] if posts_colaboracion else []
    }


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.4
# ============================================================================

def analizar_hashtags_avanzado(self) -> Dict[str, Any]:
    """
    Análisis avanzado de hashtags con recomendaciones estratégicas.
    
    Returns:
        Análisis completo de hashtags
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Analizar todos los hashtags
    todos_hashtags = []
    hashtags_por_post = []
    
    for post in linkedin_posts:
        hashtags_post = post.hashtags
        hashtags_por_post.append(len(hashtags_post))
        todos_hashtags.extend(hashtags_post)
    
    # Contar frecuencia y engagement por hashtag
    hashtags_engagement = defaultdict(list)
    hashtags_frecuencia = Counter(todos_hashtags)
    
    for post in linkedin_posts:
        for hashtag in post.hashtags:
            hashtags_engagement[hashtag].append(post.engagement_rate)
    
    # Calcular engagement promedio por hashtag
    hashtags_stats = {}
    for hashtag, engagement_rates in hashtags_engagement.items():
        hashtags_stats[hashtag] = {
            'frecuencia': hashtags_frecuencia[hashtag],
            'engagement_promedio': statistics.mean(engagement_rates),
            'engagement_max': max(engagement_rates),
            'engagement_min': min(engagement_rates)
        }
    
    # Identificar mejores hashtags
    mejores_hashtags = sorted(hashtags_stats.items(), 
                              key=lambda x: x[1]['engagement_promedio'], 
                              reverse=True)[:10]
    
    # Analizar combinaciones de hashtags
    combinaciones_efectivas = defaultdict(list)
    for post in linkedin_posts:
        if len(post.hashtags) >= 2:
            # Generar pares de hashtags
            for i, h1 in enumerate(post.hashtags):
                for h2 in post.hashtags[i+1:]:
                    combinacion = tuple(sorted([h1, h2]))
                    combinaciones_efectivas[combinacion].append(post.engagement_rate)
    
    mejores_combinaciones = sorted(
        [(combo, statistics.mean(engagements)) for combo, engagements in combinaciones_efectivas.items() 
         if len(engagements) >= 2],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # Analizar número óptimo de hashtags
    num_hashtags_engagement = defaultdict(list)
    for post in linkedin_posts:
        num_hashtags_engagement[len(post.hashtags)].append(post.engagement_rate)
    
    mejor_num_hashtags = max(num_hashtags_engagement.items(),
                            key=lambda x: statistics.mean(x[1])) if num_hashtags_engagement else None
    
    return {
        'estadisticas_generales': {
            'total_hashtags_unicos': len(hashtags_stats),
            'hashtags_totales_usados': len(todos_hashtags),
            'promedio_hashtags_por_post': statistics.mean(hashtags_por_post) if hashtags_por_post else 0,
            'mejor_numero_hashtags': mejor_num_hashtags[0] if mejor_num_hashtags else None,
            'engagement_mejor_numero': statistics.mean(mejor_num_hashtags[1]) if mejor_num_hashtags else 0
        },
        'top_hashtags': [
            {
                'hashtag': h[0],
                'frecuencia': h[1]['frecuencia'],
                'engagement_promedio': h[1]['engagement_promedio'],
                'engagement_max': h[1]['engagement_max']
            }
            for h in mejores_hashtags
        ],
        'combinaciones_efectivas': [
            {
                'hashtags': list(combo),
                'engagement_promedio': engagement
            }
            for combo, engagement in mejores_combinaciones
        ],
        'recomendaciones': [
            f"Usar {mejor_num_hashtags[0]} hashtags por post" if mejor_num_hashtags else "Experimentar con número de hashtags",
            f"Incluir hashtags top: {', '.join([h[0] for h in mejores_hashtags[:5]])}",
            "Combinar hashtags de alta performance",
            "Balancear hashtags específicos y generales",
            "Evitar hashtags sobreusados sin valor"
        ]
    }


def programar_contenido_optimizado(self, fecha_inicio: datetime = None, 
                                   semanas: int = 4) -> Dict[str, Any]:
    """
    Genera un calendario de programación optimizado basado en análisis histórico.
    
    Args:
        fecha_inicio: Fecha de inicio (default: hoy)
        semanas: Número de semanas a programar
        
    Returns:
        Calendario optimizado con recomendaciones
    """
    if not fecha_inicio:
        fecha_inicio = datetime.now()
    
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    # Analizar mejores horarios y días
    horarios_optimos = Counter([p.fecha_publicacion.hour for p in linkedin_posts])
    dias_optimos = Counter([p.fecha_publicacion.strftime('%A') for p in linkedin_posts])
    
    mejor_horario = horarios_optimos.most_common(1)[0][0] if horarios_optimos else 9
    mejores_dias = [dia[0] for dia in dias_optimos.most_common(3)]
    
    # Generar calendario
    calendario = []
    fecha_actual = fecha_inicio
    
    # Mapear días de la semana
    dias_semana_map = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    for semana in range(semanas):
        semana_calendario = {
            'semana': semana + 1,
            'fecha_inicio': fecha_actual.strftime('%Y-%m-%d'),
            'posts': []
        }
        
        # Programar posts para mejores días
        dias_programar = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for dia_nombre in dias_programar:
            # Encontrar próximo día de la semana
            dias_hasta = (dias_programar.index(dia_nombre) - fecha_actual.weekday()) % 7
            if dias_hasta == 0 and fecha_actual.weekday() not in [5, 6]:
                fecha_post = fecha_actual
            else:
                fecha_post = fecha_actual + timedelta(days=dias_hasta)
            
            # Ajustar horario según día
            if dia_nombre in ['Tuesday', 'Wednesday', 'Thursday']:
                horario = mejor_horario
            else:
                horario = mejor_horario + 1  # Horario alternativo
            
            semana_calendario['posts'].append({
                'dia': dias_semana_map.get(dia_nombre, dia_nombre),
                'fecha': fecha_post.strftime('%Y-%m-%d'),
                'horario': f"{horario:02d}:00",
                'prioridad': 'Alta' if dia_nombre in ['Tuesday', 'Wednesday', 'Thursday'] else 'Media',
                'recomendaciones': [
                    f"Publicar a las {horario:02d}:00",
                    "Incluir Hook + CTA + Pregunta",
                    "Usar 5-7 hashtags relevantes",
                    "Responder comentarios en primeras 2 horas"
                ]
            })
            
            fecha_actual = fecha_post + timedelta(days=1)
        
        calendario.append(semana_calendario)
    
    return {
        'calendario': calendario,
        'total_posts_programados': semanas * 5,
        'configuracion': {
            'mejor_horario': mejor_horario,
            'mejores_dias': mejores_dias,
            'frecuencia_semanal': 5
        },
        'recomendaciones_generales': [
            f"Publicar principalmente en {', '.join(mejores_dias)}",
            f"Horario óptimo: {mejor_horario}:00",
            "Mantener consistencia en publicación",
            "Variar tipos de contenido",
            "Monitorear y ajustar según resultados"
        ]
    }


def analizar_contenido_viral(self, umbral_viral: float = 5.0) -> Dict[str, Any]:
    """
    Análisis profundo de contenido viral y factores que lo hacen viral.
    
    Args:
        umbral_viral: Engagement rate mínimo para considerar viral (default: 5.0%)
        
    Returns:
        Análisis completo de contenido viral
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Identificar posts virales
    posts_virales = [p for p in linkedin_posts if p.engagement_rate >= umbral_viral]
    posts_no_virales = [p for p in linkedin_posts if p.engagement_rate < umbral_viral]
    
    if not posts_virales:
        return {
            'error': f'No hay posts virales (engagement >= {umbral_viral}%)',
            'sugerencia': 'Reducir umbral_viral o mejorar estrategia de contenido'
        }
    
    # Analizar características de posts virales
    caracteristicas_virales = {
        'longitud_promedio': statistics.mean([len(p.titulo) for p in posts_virales]),
        'hashtags_promedio': statistics.mean([len(p.hashtags) for p in posts_virales]),
        'tipos_contenido': Counter([p.tipo_contenido for p in posts_virales]),
        'horarios': Counter([p.fecha_publicacion.hour for p in posts_virales]),
        'dias_semana': Counter([p.fecha_publicacion.strftime('%A') for p in posts_virales]),
        'palabras_clave': Counter([palabra for p in posts_virales 
                                  for palabra in p.titulo.lower().split() 
                                  if len(palabra) > 4])
    }
    
    # Comparar con posts no virales
    caracteristicas_no_virales = {
        'longitud_promedio': statistics.mean([len(p.titulo) for p in posts_no_virales]) if posts_no_virales else 0,
        'hashtags_promedio': statistics.mean([len(p.hashtags) for p in posts_no_virales]) if posts_no_virales else 0
    }
    
    # Identificar factores clave
    factores_clave = []
    
    if caracteristicas_virales['longitud_promedio'] > caracteristicas_no_virales['longitud_promedio']:
        factores_clave.append({
            'factor': 'Longitud',
            'impacto': 'Alto',
            'descripcion': f"Posts virales son {caracteristicas_virales['longitud_promedio'] - caracteristicas_no_virales['longitud_promedio']:.0f} caracteres más largos"
        })
    
    mejor_tipo_viral = caracteristicas_virales['tipos_contenido'].most_common(1)[0][0] if caracteristicas_virales['tipos_contenido'] else None
    if mejor_tipo_viral:
        factores_clave.append({
            'factor': 'Tipo de Contenido',
            'impacto': 'Alto',
            'descripcion': f"Tipo '{mejor_tipo_viral}' aparece en {caracteristicas_virales['tipos_contenido'][mejor_tipo_viral]} posts virales"
        })
    
    mejor_horario_viral = caracteristicas_virales['horarios'].most_common(1)[0][0] if caracteristicas_virales['horarios'] else None
    if mejor_horario_viral:
        factores_clave.append({
            'factor': 'Horario',
            'impacto': 'Medio',
            'descripcion': f"Horario {mejor_horario_viral}:00 aparece en {caracteristicas_virales['horarios'][mejor_horario_viral]} posts virales"
        })
    
    return {
        'resumen': {
            'total_posts_virales': len(posts_virales),
            'total_posts_no_virales': len(posts_no_virales),
            'porcentaje_viral': len(posts_virales) / len(linkedin_posts) * 100,
            'engagement_promedio_viral': statistics.mean([p.engagement_rate for p in posts_virales]),
            'engagement_promedio_no_viral': statistics.mean([p.engagement_rate for p in posts_no_virales]) if posts_no_virales else 0
        },
        'caracteristicas_virales': caracteristicas_virales,
        'factores_clave': factores_clave,
        'top_posts_virales': sorted(posts_virales, 
                                    key=lambda x: x.engagement_rate, 
                                    reverse=True)[:5],
        'recomendaciones': [
            f"Crear más contenido tipo '{mejor_tipo_viral}'" if mejor_tipo_viral else "Diversificar tipos",
            f"Publicar alrededor de las {mejor_horario_viral}:00" if mejor_horario_viral else "Experimentar horarios",
            f"Usar longitud promedio de {caracteristicas_virales['longitud_promedio']:.0f} caracteres",
            "Incluir palabras clave identificadas",
            "Replicar estructura de posts virales"
        ]
    }


def generar_recomendaciones_personalizadas(self, industria: str = None, 
                                          objetivo: str = 'engagement') -> Dict[str, Any]:
    """
    Genera recomendaciones personalizadas basadas en industria y objetivo.
    
    Args:
        industria: Industria objetivo (opcional)
        objetivo: Objetivo principal ('engagement', 'leads', 'autoridad', 'ventas')
        
    Returns:
        Recomendaciones personalizadas
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Analizar situación actual
    engagement_promedio = statistics.mean([p.engagement_rate for p in linkedin_posts])
    
    # Recomendaciones por objetivo
    recomendaciones_objetivo = {
        'engagement': [
            "Incluir preguntas al final de cada post",
            "Usar hooks impactantes en primeras 125 caracteres",
            "Publicar en horarios de mayor actividad (8-10 AM, 12-1 PM, 5-6 PM)",
            "Responder a todos los comentarios en primeras 2 horas",
            "Crear contenido que invite a compartir experiencias"
        ],
        'leads': [
            "Incluir CTAs claros y específicos",
            "Ofrecer valor antes de pedir algo",
            "Usar mensajes directos estratégicamente",
            "Crear contenido que resuelva problemas específicos",
            "Incluir enlaces a recursos descargables"
        ],
        'autoridad': [
            "Compartir insights únicos y valiosos",
            "Publicar casos de estudio y resultados",
            "Establecer consistencia en publicación",
            "Participar activamente en comentarios",
            "Crear contenido educativo de alta calidad"
        ],
        'ventas': [
            "Contar historias de éxito de clientes",
            "Mostrar resultados y ROI",
            "Incluir testimonios y casos de uso",
            "Crear contenido que demuestre expertise",
            "Usar CTAs orientados a conversación"
        ]
    }
    
    # Recomendaciones por industria (si se proporciona)
    recomendaciones_industria = {}
    if industria:
        recomendaciones_industria = {
            'tecnologia': [
                "Compartir tendencias tecnológicas",
                "Mostrar casos de uso innovadores",
                "Usar hashtags como #TechInnovation, #DigitalTransformation"
            ],
            'marketing': [
                "Compartir estrategias probadas",
                "Mostrar resultados de campañas",
                "Usar hashtags como #MarketingDigital, #GrowthHacking"
            ],
            'ventas': [
                "Compartir técnicas de cierre",
                "Mostrar historias de éxito",
                "Usar hashtags como #SalesTips, #BusinessDevelopment"
            ]
        }
    
    # Generar recomendaciones específicas basadas en análisis
    analisis_linkedin = {}
    if hasattr(self, 'analizar_linkedin_especifico'):
        try:
            analisis_linkedin = self.analizar_linkedin_especifico()
        except:
            pass
    
    recomendaciones_especificas = []
    
    if analisis_linkedin.get('longitud_optima'):
        mejor_longitud = max(analisis_linkedin['longitud_optima'].items(),
                           key=lambda x: x[1].get('engagement_promedio', 0))
        recomendaciones_especificas.append(
            f"Usar longitud de {mejor_longitud[0]} caracteres para máximo engagement"
        )
    
    if analisis_linkedin.get('hashtags_optimo'):
        mejor_num = max(analisis_linkedin['hashtags_optimo'].items(),
                       key=lambda x: x[1].get('engagement_promedio', 0))
        recomendaciones_especificas.append(
            f"Usar {mejor_num[0]} hashtags por post"
        )
    
    return {
        'objetivo': objetivo,
        'industria': industria,
        'situacion_actual': {
            'engagement_promedio': engagement_promedio,
            'total_posts': len(linkedin_posts)
        },
        'recomendaciones_objetivo': recomendaciones_objetivo.get(objetivo, []),
        'recomendaciones_industria': recomendaciones_industria.get(industria.lower(), []),
        'recomendaciones_especificas': recomendaciones_especificas,
        'plan_accion': [
            "Implementar recomendaciones prioritarias esta semana",
            "Medir impacto de cambios",
            "Ajustar estrategia según resultados",
            "Mantener consistencia en implementación"
        ]
    }


def exportar_calendario_ical(self, calendario: Dict[str, Any], 
                            output_file: str = 'calendario_linkedin.ics') -> str:
    """
    Exporta calendario a formato iCal para importar en Google Calendar, Outlook, etc.
    
    Args:
        calendario: Calendario generado por programar_contenido_optimizado
        output_file: Nombre del archivo de salida
        
    Returns:
        Ruta del archivo generado
    """
    ical_content = "BEGIN:VCALENDAR\n"
    ical_content += "VERSION:2.0\n"
    ical_content += "PRODID:-//LinkedIn Content Scheduler//EN\n"
    ical_content += "CALSCALE:GREGORIAN\n"
    ical_content += "METHOD:PUBLISH\n"
    
    # Agregar eventos
    for semana in calendario.get('calendario', []):
        for post in semana.get('posts', []):
            fecha_str = post.get('fecha')
            horario_str = post.get('horario', '09:00')
            
            if fecha_str:
                fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
                hora, minuto = map(int, horario_str.split(':'))
                fecha_dt = fecha_dt.replace(hour=hora, minute=minuto)
                
                fecha_inicio = fecha_dt.strftime('%Y%m%dT%H%M%S')
                fecha_fin = (fecha_dt + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')
                
                ical_content += "BEGIN:VEVENT\n"
                ical_content += f"DTSTART:{fecha_inicio}\n"
                ical_content += f"DTEND:{fecha_fin}\n"
                ical_content += f"SUMMARY:Publicar en LinkedIn - {post.get('dia', '')}\n"
                ical_content += f"DESCRIPTION:Horario: {horario_str}\\nPrioridad: {post.get('prioridad', 'Media')}\\n"
                ical_content += "\\n".join(post.get('recomendaciones', [])) + "\n"
                ical_content += "END:VEVENT\n"
    
    ical_content += "END:VCALENDAR\n"
    
    # Guardar archivo
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ical_content)
        return output_file
    except Exception as e:
        return f"Error al exportar: {e}"


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.5
# ============================================================================

def analizar_tendencias_contenido(self, dias: int = 30) -> Dict[str, Any]:
    """
    Analiza tendencias de contenido en el tiempo para identificar patrones.
    
    Args:
        dias: Número de días hacia atrás para analizar
        
    Returns:
        Análisis de tendencias temporales
    """
    fecha_limite = datetime.now() - timedelta(days=dias)
    posts_recientes = [p for p in self.publicaciones 
                      if p.fecha_publicacion >= fecha_limite and p.plataforma.lower() == 'linkedin']
    
    if not posts_recientes:
        return {'error': f'No hay posts en los últimos {dias} días'}
    
    # Analizar tendencias por semana
    posts_por_semana = defaultdict(list)
    for p in posts_recientes:
        año, semana, _ = p.fecha_publicacion.isocalendar()
        clave = f"{año}-W{semana:02d}"
        posts_por_semana[clave].append(p)
    
    tendencias_semanales = []
    for semana in sorted(posts_por_semana.keys()):
        posts_semana = posts_por_semana[semana]
        tendencias_semanales.append({
            'semana': semana,
            'total_posts': len(posts_semana),
            'engagement_promedio': statistics.mean([p.engagement_rate for p in posts_semana]),
            'tipos_contenido': Counter([p.tipo_contenido for p in posts_semana])
        })
    
    # Calcular tendencia general
    if len(tendencias_semanales) >= 2:
        primera_semana = tendencias_semanales[0]['engagement_promedio']
        ultima_semana = tendencias_semanales[-1]['engagement_promedio']
        cambio = ((ultima_semana - primera_semana) / primera_semana * 100) if primera_semana > 0 else 0
        direccion = 'creciendo' if cambio > 5 else 'decreciendo' if cambio < -5 else 'estable'
    else:
        cambio = 0
        direccion = 'insuficiente_datos'
    
    # Identificar temas emergentes
    palabras_recientes = Counter([palabra for p in posts_recientes[-10:] 
                                  for palabra in p.titulo.lower().split() 
                                  if len(palabra) > 4])
    palabras_antiguas = Counter([palabra for p in posts_recientes[:-10] 
                                 for palabra in p.titulo.lower().split() 
                                 if len(palabra) > 4])
    
    temas_emergentes = set(palabras_recientes.keys()) - set(palabras_antiguas.keys())
    
    return {
        'periodo_analizado': f'Últimos {dias} días',
        'tendencias_semanales': tendencias_semanales,
        'tendencia_general': {
            'direccion': direccion,
            'cambio_porcentual': cambio,
            'primera_semana': tendencias_semanales[0]['engagement_promedio'] if tendencias_semanales else 0,
            'ultima_semana': tendencias_semanales[-1]['engagement_promedio'] if tendencias_semanales else 0
        },
        'temas_emergentes': list(temas_emergentes)[:10],
        'recomendaciones': [
            f"Tendencia: {direccion} ({cambio:+.1f}%)",
            "Aumentar frecuencia si tendencia es creciente",
            "Revisar estrategia si tendencia es decreciente",
            f"Explorar temas emergentes: {', '.join(list(temas_emergentes)[:3])}" if temas_emergentes else "No hay temas emergentes identificados"
        ]
    }


def crear_ab_test_completo(self, variacion_a: Dict[str, Any], 
                           variacion_b: Dict[str, Any],
                           duracion_dias: int = 7) -> Dict[str, Any]:
    """
    Crea un plan completo de A/B testing con métricas y recomendaciones.
    
    Args:
        variacion_a: Variación A con título, hashtags, horario, etc.
        variacion_b: Variación B
        duracion_dias: Duración del test en días
        
    Returns:
        Plan completo de A/B testing
    """
    # Validar variaciones
    validacion_a = {}
    validacion_b = {}
    score_a = {}
    score_b = {}
    
    if hasattr(self, 'validar_post_linkedin'):
        try:
            validacion_a = self.validar_post_linkedin(variacion_a.get('titulo', ''), variacion_a.get('hashtags', []))
            validacion_b = self.validar_post_linkedin(variacion_b.get('titulo', ''), variacion_b.get('hashtags', []))
        except:
            pass
    
    if hasattr(self, 'calcular_score_optimizacion'):
        try:
            score_a = self.calcular_score_optimizacion(variacion_a.get('titulo', ''), variacion_a.get('hashtags', []))
            score_b = self.calcular_score_optimizacion(variacion_b.get('titulo', ''), variacion_b.get('hashtags', []))
        except:
            pass
    
    # Predecir engagement
    prediccion_a = {}
    prediccion_b = {}
    if hasattr(self, 'predecir_engagement_post'):
        try:
            prediccion_a = self.predecir_engagement_post(
                variacion_a.get('titulo', ''),
                variacion_a.get('hashtags', []),
                horario=variacion_a.get('horario', 9),
                dia_semana=variacion_a.get('dia_semana', 'Martes')
            )
            prediccion_b = self.predecir_engagement_post(
                variacion_b.get('titulo', ''),
                variacion_b.get('hashtags', []),
                horario=variacion_b.get('horario', 9),
                dia_semana=variacion_b.get('dia_semana', 'Martes')
            )
        except:
            pass
    
    # Determinar variación recomendada
    engagement_a = prediccion_a.get('prediccion', {}).get('engagement_rate_esperado', 0)
    engagement_b = prediccion_b.get('prediccion', {}).get('engagement_rate_esperado', 0)
    
    variacion_recomendada = 'A' if engagement_a > engagement_b else 'B'
    diferencia = abs(engagement_a - engagement_b)
    
    return {
        'plan_test': {
            'duracion_dias': duracion_dias,
            'variacion_a': {
                'titulo': variacion_a.get('titulo', '')[:100],
                'hashtags': variacion_a.get('hashtags', []),
                'horario': variacion_a.get('horario', 9),
                'dia_semana': variacion_a.get('dia_semana', 'Martes'),
                'validacion': validacion_a,
                'score': score_a,
                'prediccion': prediccion_a
            },
            'variacion_b': {
                'titulo': variacion_b.get('titulo', '')[:100],
                'hashtags': variacion_b.get('hashtags', []),
                'horario': variacion_b.get('horario', 9),
                'dia_semana': variacion_b.get('dia_semana', 'Martes'),
                'validacion': validacion_b,
                'score': score_b,
                'prediccion': prediccion_b
            }
        },
        'prediccion_pre_test': {
            'variacion_recomendada': variacion_recomendada,
            'diferencia_esperada': diferencia,
            'confianza_a': prediccion_a.get('prediccion', {}).get('confianza', 0),
            'confianza_b': prediccion_b.get('prediccion', {}).get('confianza', 0)
        },
        'metricas_seguimiento': [
            'Engagement rate',
            'Alcance',
            'Impresiones',
            'Comentarios',
            'Compartidos',
            'Likes',
            'Clicks en perfil',
            'Mensajes directos'
        ],
        'criterios_exito': {
            'diferencia_minima': 0.5,  # 0.5% de diferencia mínima
            'confianza_minima': 80,  # 80% de confianza
            'muestra_minima': 1000  # Mínimo 1000 impresiones por variación
        },
        'recomendaciones': [
            f"Publicar variación {variacion_recomendada} primero (mayor engagement esperado)",
            f"Monitorear métricas durante {duracion_dias} días",
            "Publicar ambas variaciones en horarios similares",
            "Mantener otros factores constantes",
            "Analizar resultados después de {duracion_dias} días"
        ]
    }


def analizar_roi_completo(self, costo_creacion: float = 25.0, 
                         costo_publicacion: float = 0.0,
                         valor_lead: float = 100.0,
                         tasa_conversion: float = 0.01) -> Dict[str, Any]:
    """
    Análisis completo de ROI incluyendo todos los costos y beneficios.
    
    Args:
        costo_creacion: Costo por hora de creación de contenido
        costo_publicacion: Costo por publicación (si hay)
        valor_lead: Valor promedio de un lead
        tasa_conversion: Tasa de conversión de engagement a lead (1% por defecto)
        
    Returns:
        Análisis completo de ROI
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Calcular costos
    tiempo_creacion_minutos = 30  # minutos promedio por post
    tiempo_total_horas = (len(linkedin_posts) * tiempo_creacion_minutos) / 60
    costo_total_creacion = tiempo_total_horas * costo_creacion
    costo_total_publicacion = len(linkedin_posts) * costo_publicacion
    costo_total = costo_total_creacion + costo_total_publicacion
    
    # Calcular beneficios
    engagement_total = sum([p.engagement_total for p in linkedin_posts])
    impresiones_totales = sum([p.impresiones for p in linkedin_posts])
    leads_estimados = int(engagement_total * tasa_conversion)
    valor_total_leads = leads_estimados * valor_lead
    
    # Calcular ROI
    roi_porcentual = ((valor_total_leads - costo_total) / costo_total * 100) if costo_total > 0 else 0
    roi_por_post = (valor_total_leads - costo_total) / len(linkedin_posts) if linkedin_posts else 0
    
    # Calcular métricas de eficiencia
    costo_por_engagement = costo_total / engagement_total if engagement_total > 0 else 0
    costo_por_lead = costo_total / leads_estimados if leads_estimados > 0 else 0
    costo_por_impresion = costo_total / impresiones_totales if impresiones_totales > 0 else 0
    
    # Identificar posts más rentables
    posts_rentabilidad = []
    for post in linkedin_posts:
        costo_post = (tiempo_creacion_minutos / 60 * costo_creacion) + costo_publicacion
        leads_post = int(post.engagement_total * tasa_conversion)
        valor_post = leads_post * valor_lead
        roi_post = ((valor_post - costo_post) / costo_post * 100) if costo_post > 0 else 0
        
        posts_rentabilidad.append({
            'post_id': post.id,
            'titulo': post.titulo[:100],
            'costo': costo_post,
            'valor_generado': valor_post,
            'roi': roi_post,
            'leads': leads_post
        })
    
    posts_mas_rentables = sorted(posts_rentabilidad, key=lambda x: x['roi'], reverse=True)[:5]
    
    return {
        'costos': {
            'creacion': {
                'tiempo_total_horas': tiempo_total_horas,
                'costo_total': costo_total_creacion,
                'costo_por_post': costo_total_creacion / len(linkedin_posts) if linkedin_posts else 0
            },
            'publicacion': {
                'costo_total': costo_total_publicacion,
                'costo_por_post': costo_publicacion
            },
            'total': costo_total
        },
        'beneficios': {
            'engagement_total': engagement_total,
            'impresiones_totales': impresiones_totales,
            'leads_estimados': leads_estimados,
            'valor_total_leads': valor_total_leads
        },
        'roi': {
            'roi_porcentual': roi_porcentual,
            'roi_por_post': roi_por_post,
            'retorno_total': valor_total_leads - costo_total,
            'breakeven_posts': int(costo_total / (valor_total_leads / len(linkedin_posts))) if valor_total_leads > 0 else 0
        },
        'metricas_eficiencia': {
            'costo_por_engagement': costo_por_engagement,
            'costo_por_lead': costo_por_lead,
            'costo_por_impresion': costo_por_impresion,
            'valor_por_engagement': valor_total_leads / engagement_total if engagement_total > 0 else 0
        },
        'posts_mas_rentables': posts_mas_rentables,
        'recomendaciones': [
            f"ROI actual: {roi_porcentual:.1f}%",
            f"Costo por lead: ${costo_por_lead:.2f}",
            "Optimizar posts de menor ROI",
            "Replicar estructura de posts más rentables",
            "Reducir tiempo de creación para mejorar ROI"
        ] if roi_porcentual > 0 else [
            "ROI negativo - revisar estrategia urgentemente",
            "Reducir costos de creación",
            "Mejorar tasa de conversión",
            "Enfocarse en contenido de alto engagement"
        ]
    }


def generar_estrategia_completa_anual(self, objetivo_principal: str = 'crecimiento') -> Dict[str, Any]:
    """
    Genera una estrategia completa anual de LinkedIn con objetivos y KPIs.
    
    Args:
        objetivo_principal: Objetivo principal ('crecimiento', 'leads', 'autoridad', 'ventas')
        
    Returns:
        Estrategia anual completa
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Analizar situación actual
    engagement_actual = statistics.mean([p.engagement_rate for p in linkedin_posts])
    frecuencia_actual = len(linkedin_posts) / 30  # Posts por mes (asumiendo último mes)
    
    # Definir objetivos según objetivo principal
    objetivos_anuales = {
        'crecimiento': {
            'engagement_objetivo': min(engagement_actual * 1.5, 6.0),
            'frecuencia_objetivo': min(frecuencia_actual * 1.2, 5),
            'posts_anuales': 240,  # 5 posts/semana * 48 semanas
            'seguidores_objetivo': '+25%',
            'alcance_objetivo': '+30%'
        },
        'leads': {
            'engagement_objetivo': min(engagement_actual * 1.3, 5.0),
            'frecuencia_objetivo': min(frecuencia_actual * 1.1, 5),
            'posts_anuales': 200,
            'leads_objetivo': '+50%',
            'conversion_objetivo': '+20%'
        },
        'autoridad': {
            'engagement_objetivo': min(engagement_actual * 1.2, 4.5),
            'frecuencia_objetivo': min(frecuencia_actual * 1.0, 3),
            'posts_anuales': 150,
            'compartidos_objetivo': '+40%',
            'menciones_objetivo': '+30%'
        },
        'ventas': {
            'engagement_objetivo': min(engagement_actual * 1.4, 5.5),
            'frecuencia_objetivo': min(frecuencia_actual * 1.15, 4),
            'posts_anuales': 180,
            'conversaciones_objetivo': '+60%',
            'ventas_objetivo': '+35%'
        }
    }
    
    objetivos = objetivos_anuales.get(objetivo_principal, objetivos_anuales['crecimiento'])
    
    # Generar plan trimestral
    plan_trimestral = []
    for trimestre in range(1, 5):
        plan_trimestral.append({
            'trimestre': trimestre,
            'objetivo': f"Q{trimestre} - {'Establecimiento' if trimestre == 1 else 'Crecimiento' if trimestre == 2 else 'Optimización' if trimestre == 3 else 'Escalamiento'}",
            'posts_objetivo': objetivos['posts_anuales'] // 4,
            'engagement_objetivo': engagement_actual * (1 + (trimestre * 0.1)),
            'acciones_clave': [
                "Optimizar contenido según análisis Q anterior",
                "Experimentar con nuevos formatos",
                "Aumentar frecuencia gradualmente",
                "Medir y ajustar estrategia"
            ]
        })
    
    # KPIs de seguimiento
    kpis = {
        'mensuales': [
            'Engagement rate promedio',
            'Alcance total',
            'Posts publicados',
            'Comentarios totales',
            'Compartidos totales',
            'Mensajes directos',
            'Clicks en perfil'
        ],
        'trimestrales': [
            'Crecimiento de engagement',
            'ROI de contenido',
            'Leads generados',
            'Crecimiento de seguidores',
            'Alcance promedio por post'
        ],
        'anuales': [
            'Objetivo de engagement alcanzado',
            'Total de leads generados',
            'ROI total de estrategia',
            'Crecimiento de audiencia',
            'Posts virales creados'
        ]
    }
    
    return {
        'objetivo_principal': objetivo_principal,
        'situacion_actual': {
            'engagement_promedio': engagement_actual,
            'frecuencia_mensual': frecuencia_actual,
            'total_posts_analizados': len(linkedin_posts)
        },
        'objetivos_anuales': objetivos,
        'plan_trimestral': plan_trimestral,
        'kpis': kpis,
        'estrategia_contenido': {
            'tipos_recomendados': ['Educativo', 'Caso de Éxito', 'Pregunta', 'Estadística'],
            'frecuencia_semanal': objetivos['frecuencia_objetivo'],
            'horarios_optimos': ['8-10 AM', '12-1 PM', '5-6 PM'],
            'dias_optimos': ['Martes', 'Miércoles', 'Jueves']
        },
        'recomendaciones_estrategicas': [
            f"Enfocarse en objetivo de {objetivo_principal}",
            f"Publicar {objetivos['frecuencia_objetivo']:.0f} veces por semana",
            "Mantener consistencia durante todo el año",
            "Revisar y ajustar estrategia trimestralmente",
            "Medir progreso contra objetivos mensualmente"
        ]
    }


# Agregar nuevos métodos al AnalizadorEngagement
AnalizadorEngagement.analizar_audiencia_avanzado = analizar_audiencia_avanzado
AnalizadorEngagement.repurposing_contenido = repurposing_contenido
AnalizadorEngagement.analizar_conversion_cta = analizar_conversion_cta
AnalizadorEngagement.generar_reportes_ejecutivos = generar_reportes_ejecutivos
AnalizadorEngagement.analizar_colaboraciones = analizar_colaboraciones
AnalizadorEngagement.analizar_hashtags_avanzado = analizar_hashtags_avanzado
AnalizadorEngagement.programar_contenido_optimizado = programar_contenido_optimizado
AnalizadorEngagement.analizar_contenido_viral = analizar_contenido_viral
AnalizadorEngagement.generar_recomendaciones_personalizadas = generar_recomendaciones_personalizadas
AnalizadorEngagement.exportar_calendario_ical = exportar_calendario_ical
AnalizadorEngagement.analizar_tendencias_contenido = analizar_tendencias_contenido
AnalizadorEngagement.crear_ab_test_completo = crear_ab_test_completo
AnalizadorEngagement.analizar_roi_completo = analizar_roi_completo
AnalizadorEngagement.generar_estrategia_completa_anual = generar_estrategia_completa_anual


# ============================================================================
# FUNCIONALIDADES AVANZADAS ADICIONALES v4.6
# ============================================================================

def analizar_competidores_especificos(self, competidores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Análisis profundo de competidores específicos con comparación detallada.
    
    Args:
        competidores: Lista de diccionarios con datos de competidores
        
    Returns:
        Análisis competitivo completo
    """
    if not competidores:
        return {'error': 'No se proporcionaron datos de competidores'}
    
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts propios de LinkedIn para comparar'}
    
    # Analizar métricas propias
    engagement_propio = statistics.mean([p.engagement_rate for p in linkedin_posts])
    frecuencia_propia = len(linkedin_posts) / 30  # Posts por mes
    
    # Analizar cada competidor
    analisis_competidores = []
    for i, competidor in enumerate(competidores, 1):
        nombre = competidor.get('nombre', f'Competidor {i}')
        posts_competidor = competidor.get('posts', [])
        
        if not posts_competidor:
            continue
        
        engagement_competidor = statistics.mean([p.get('engagement_rate', 0) for p in posts_competidor])
        frecuencia_competidor = len(posts_competidor) / 30
        
        # Analizar tipos de contenido
        tipos_contenido = Counter([p.get('tipo_contenido', 'X') for p in posts_competidor])
        mejor_tipo = tipos_contenido.most_common(1)[0][0] if tipos_contenido else None
        
        # Analizar hashtags
        hashtags_competidor = Counter([h for p in posts_competidor 
                                      for h in p.get('hashtags', [])])
        
        analisis_competidores.append({
            'nombre': nombre,
            'engagement_promedio': engagement_competidor,
            'frecuencia_mensual': frecuencia_competidor,
            'total_posts': len(posts_competidor),
            'mejor_tipo_contenido': mejor_tipo,
            'top_hashtags': hashtags_competidor.most_common(10),
            'ventaja_sobre_ti': {
                'engagement': engagement_competidor - engagement_propio,
                'frecuencia': frecuencia_competidor - frecuencia_propia
            }
        })
    
    # Identificar mejor competidor
    mejor_competidor = max(analisis_competidores, 
                          key=lambda x: x['engagement_promedio']) if analisis_competidores else None
    
    # Generar recomendaciones competitivas
    recomendaciones = []
    if mejor_competidor:
        if mejor_competidor['engagement_promedio'] > engagement_propio:
            gap = mejor_competidor['engagement_promedio'] - engagement_propio
            recomendaciones.append({
                'prioridad': 'Alta',
                'recomendacion': f"{mejor_competidor['nombre']} tiene {gap:.2f}% más engagement",
                'accion': f"Analizar estructura y contenido de {mejor_competidor['nombre']}"
            })
        
        if mejor_competidor['mejor_tipo_contenido']:
            recomendaciones.append({
                'prioridad': 'Media',
                'recomendacion': f"Competidor usa tipo '{mejor_competidor['mejor_tipo_contenido']}' frecuentemente",
                'accion': f"Experimentar con más contenido tipo '{mejor_competidor['mejor_tipo_contenido']}'"
            })
    
    return {
        'tu_rendimiento': {
            'engagement_promedio': engagement_propio,
            'frecuencia_mensual': frecuencia_propia,
            'total_posts': len(linkedin_posts)
        },
        'analisis_competidores': analisis_competidores,
        'mejor_competidor': mejor_competidor,
        'ranking': sorted(analisis_competidores, 
                         key=lambda x: x['engagement_promedio'], 
                         reverse=True),
        'recomendaciones_competitivas': recomendaciones,
        'oportunidades': [
            f"Mejorar engagement para competir con {mejor_competidor['nombre']}" if mejor_competidor else "No hay competidores para comparar",
            "Analizar hashtags exitosos de competidores",
            "Adaptar tipos de contenido que funcionan",
            "Aumentar frecuencia si es necesario"
        ]
    }


def generar_contenido_evergreen(self, temas: List[str], num_posts: int = 10) -> List[Dict[str, Any]]:
    """
    Genera ideas de contenido evergreen que mantienen relevancia a largo plazo.
    
    Args:
        temas: Lista de temas principales
        num_posts: Número de posts a generar
        
    Returns:
        Lista de ideas de contenido evergreen
    """
    plantillas_evergreen = [
        {
            'tipo': 'Guía Definitiva',
            'estructura': 'Cómo [Acción] en [Tema]: Guía Completa',
            'longitud': 1500,
            'hashtags': ['#Guía', '#Aprendizaje', '#Educación']
        },
        {
            'tipo': 'Lista de Mejores Prácticas',
            'estructura': 'Top [Número] Mejores Prácticas para [Tema]',
            'longitud': 1200,
            'hashtags': ['#MejoresPrácticas', '#Tips', '#Consejos']
        },
        {
            'tipo': 'Comparación',
            'estructura': '[Opción A] vs [Opción B]: ¿Cuál Elegir?',
            'longitud': 1300,
            'hashtags': ['#Comparación', '#Análisis', '#Decisión']
        },
        {
            'tipo': 'Preguntas Frecuentes',
            'estructura': 'Preguntas Frecuentes sobre [Tema] Respondidas',
            'longitud': 1400,
            'hashtags': ['#FAQ', '#Preguntas', '#Respuestas']
        },
        {
            'tipo': 'Mitos y Realidades',
            'estructura': 'Mitos y Realidades sobre [Tema]',
            'longitud': 1250,
            'hashtags': ['#Mitos', '#Verdad', '#Clarificación']
        }
    ]
    
    ideas = []
    temas_rotados = temas * ((num_posts // len(temas)) + 1)
    
    for i in range(num_posts):
        tema = temas_rotados[i]
        plantilla = plantillas_evergreen[i % len(plantillas_evergreen)]
        
        titulo = plantilla['estructura'].replace('[Tema]', tema)
        if '[Acción]' in titulo:
            acciones = ['Empezar', 'Optimizar', 'Mejorar', 'Dominar', 'Aprender']
            titulo = titulo.replace('[Acción]', acciones[i % len(acciones)])
        if '[Número]' in titulo:
            titulo = titulo.replace('[Número]', str(random.randint(5, 10)))
        if '[Opción A]' in titulo:
            opciones = [('Opción A', 'Opción B'), ('Método 1', 'Método 2'), ('Enfoque X', 'Enfoque Y')]
            opcion = opciones[i % len(opciones)]
            titulo = titulo.replace('[Opción A]', opcion[0]).replace('[Opción B]', opcion[1])
        
        # Generar contenido completo
        contenido = f"{titulo}\n\n"
        contenido += f"En {tema}, hay varios aspectos importantes a considerar...\n\n"
        contenido += "1. [Punto clave 1]\n"
        contenido += "2. [Punto clave 2]\n"
        contenido += "3. [Punto clave 3]\n\n"
        contenido += "¿Qué opinas sobre esto? Comparte tu experiencia en comentarios 👇"
        
        ideas.append({
            'idea': i + 1,
            'tipo': plantilla['tipo'],
            'titulo': titulo,
            'contenido': contenido,
            'longitud': len(contenido),
            'hashtags': plantilla['hashtags'] + [f"#{tema.replace(' ', '')}"],
            'es_evergreen': True,
            'recomendaciones': [
                "Actualizar periódicamente con datos recientes",
                "Compartir múltiples veces durante el año",
                "Incluir ejemplos actuales",
                "Mantener relevancia con tendencias"
            ]
        })
    
    return ideas


def analizar_patrones_temporales_avanzado(self) -> Dict[str, Any]:
    """
    Análisis avanzado de patrones temporales con predicciones.
    
    Returns:
        Análisis completo de patrones temporales
    """
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    
    if not linkedin_posts:
        return {'error': 'No hay posts de LinkedIn para analizar'}
    
    # Analizar por mes
    posts_por_mes = defaultdict(list)
    for p in linkedin_posts:
        clave = p.fecha_publicacion.strftime('%Y-%m')
        posts_por_mes[clave].append(p)
    
    tendencias_mensuales = []
    for mes in sorted(posts_por_mes.keys()):
        posts_mes = posts_por_mes[mes]
        tendencias_mensuales.append({
            'mes': mes,
            'total_posts': len(posts_mes),
            'engagement_promedio': statistics.mean([p.engagement_rate for p in posts_mes]),
            'alcance_total': sum([p.reach for p in posts_mes])
        })
    
    # Analizar por día de la semana
    engagement_por_dia = defaultdict(list)
    for p in linkedin_posts:
        dia = p.fecha_publicacion.strftime('%A')
        engagement_por_dia[dia].append(p.engagement_rate)
    
    mejor_dia = max(engagement_por_dia.items(),
                   key=lambda x: statistics.mean(x[1])) if engagement_por_dia else None
    
    # Analizar por hora
    engagement_por_hora = defaultdict(list)
    for p in linkedin_posts:
        hora = p.fecha_publicacion.hour
        engagement_por_hora[hora].append(p.engagement_rate)
    
    mejor_hora = max(engagement_por_hora.items(),
                    key=lambda x: statistics.mean(x[1])) if engagement_por_hora else None
    
    # Predecir próximo mes (simple extrapolación)
    prediccion_proximo_mes = {}
    if len(tendencias_mensuales) >= 2:
        ultimos_meses = tendencias_mensuales[-3:]
        engagement_tendencia = statistics.mean([m['engagement_promedio'] for m in ultimos_meses])
        frecuencia_tendencia = statistics.mean([m['total_posts'] for m in ultimos_meses])
        
        prediccion_proximo_mes = {
            'engagement_esperado': engagement_tendencia,
            'posts_esperados': int(frecuencia_tendencia),
            'confianza': min(85, 50 + len(tendencias_mensuales) * 5)
        }
    
    return {
        'tendencias_mensuales': tendencias_mensuales,
        'patrones_semanales': {
            'mejor_dia': mejor_dia[0] if mejor_dia else None,
            'engagement_mejor_dia': statistics.mean(mejor_dia[1]) if mejor_dia else 0,
            'distribucion_por_dia': {dia: statistics.mean(engagements) 
                                    for dia, engagements in engagement_por_dia.items()}
        },
        'patrones_horarios': {
            'mejor_hora': mejor_hora[0] if mejor_hora else None,
            'engagement_mejor_hora': statistics.mean(mejor_hora[1]) if mejor_hora else 0,
            'horarios_optimos': sorted(engagement_por_hora.items(),
                                     key=lambda x: statistics.mean(x[1]),
                                     reverse=True)[:5]
        },
        'prediccion_proximo_mes': prediccion_proximo_mes,
        'recomendaciones': [
            f"Publicar principalmente los {mejor_dia[0]}" if mejor_dia else "Experimentar con diferentes días",
            f"Horario óptimo: {mejor_hora[0]}:00" if mejor_hora else "Experimentar con horarios",
            "Mantener consistencia en mejores días y horarios",
            "Ajustar según predicción del próximo mes"
        ]
    }


def crear_sistema_automatizacion(self, reglas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Crea un sistema de automatización basado en reglas definidas.
    
    Args:
        reglas: Lista de reglas de automatización
        
    Returns:
        Sistema de automatización configurado
    """
    sistema = {
        'reglas': reglas,
        'acciones_automaticas': [],
        'alertas_configuradas': []
    }
    
    for regla in reglas:
        tipo = regla.get('tipo')
        condicion = regla.get('condicion')
        accion = regla.get('accion')
        
        if tipo == 'alerta_engagement':
            umbral = condicion.get('umbral', 2.0)
            sistema['alertas_configuradas'].append({
                'tipo': 'Alerta de Engagement',
                'condicion': f"Engagement < {umbral}%",
                'accion': accion
            })
        
        elif tipo == 'optimizacion_automatica':
            sistema['acciones_automaticas'].append({
                'tipo': 'Optimización Automática',
                'condicion': condicion.get('descripcion', ''),
                'accion': accion
            })
        
        elif tipo == 'programacion_automatica':
            sistema['acciones_automaticas'].append({
                'tipo': 'Programación Automática',
                'condicion': condicion.get('descripcion', ''),
                'accion': accion
            })
    
    return {
        'sistema': sistema,
        'total_reglas': len(reglas),
        'estado': 'Configurado',
        'recomendaciones': [
            "Revisar reglas periódicamente",
            "Ajustar umbrales según resultados",
            "Monitorear acciones automáticas",
            "Validar antes de implementar cambios automáticos"
        ]
    }


def generar_benchmark_personalizado(self, industria: str, tamaño_empresa: str = 'mediana') -> Dict[str, Any]:
    """
    Genera benchmarks personalizados según industria y tamaño de empresa.
    
    Args:
        industria: Industria objetivo
        tamaño_empresa: Tamaño de empresa ('pequeña', 'mediana', 'grande')
        
    Returns:
        Benchmarks personalizados
    """
    # Benchmarks por industria y tamaño
    benchmarks_base = {
        'tecnologia': {
            'pequeña': {'engagement': 3.5, 'frecuencia': 3, 'alcance': 5000},
            'mediana': {'engagement': 4.0, 'frecuencia': 4, 'alcance': 15000},
            'grande': {'engagement': 4.5, 'frecuencia': 5, 'alcance': 50000}
        },
        'marketing': {
            'pequeña': {'engagement': 4.0, 'frecuencia': 3, 'alcance': 4000},
            'mediana': {'engagement': 4.5, 'frecuencia': 4, 'alcance': 12000},
            'grande': {'engagement': 5.0, 'frecuencia': 5, 'alcance': 40000}
        },
        'ventas': {
            'pequeña': {'engagement': 3.0, 'frecuencia': 2, 'alcance': 3000},
            'mediana': {'engagement': 3.5, 'frecuencia': 3, 'alcance': 10000},
            'grande': {'engagement': 4.0, 'frecuencia': 4, 'alcance': 30000}
        }
    }
    
    benchmark_industria = benchmarks_base.get(industria.lower(), benchmarks_base['tecnologia'])
    benchmark = benchmark_industria.get(tamaño_empresa.lower(), benchmark_industria['mediana'])
    
    # Comparar con rendimiento actual
    linkedin_posts = [p for p in self.publicaciones if p.plataforma.lower() == 'linkedin']
    engagement_actual = statistics.mean([p.engagement_rate for p in linkedin_posts]) if linkedin_posts else 0
    frecuencia_actual = len(linkedin_posts) / 30 if linkedin_posts else 0
    
    gap_engagement = benchmark['engagement'] - engagement_actual
    gap_frecuencia = benchmark['frecuencia'] - frecuencia_actual
    
    return {
        'benchmark': benchmark,
        'tu_rendimiento': {
            'engagement': engagement_actual,
            'frecuencia': frecuencia_actual
        },
        'comparacion': {
            'gap_engagement': gap_engagement,
            'gap_frecuencia': gap_frecuencia,
            'porcentaje_del_benchmark': (engagement_actual / benchmark['engagement'] * 100) if benchmark['engagement'] > 0 else 0
        },
        'clasificacion': {
            'engagement': 'Excelente' if engagement_actual >= benchmark['engagement'] * 1.1 
                         else 'Bueno' if engagement_actual >= benchmark['engagement'] 
                         else 'Necesita Mejora',
            'frecuencia': 'Óptima' if frecuencia_actual >= benchmark['frecuencia'] 
                         else 'Subóptima'
        },
        'recomendaciones': [
            f"{'Mantener' if gap_engagement <= 0 else 'Mejorar'} engagement para alcanzar benchmark",
            f"{'Mantener' if gap_frecuencia <= 0 else 'Aumentar'} frecuencia de publicación",
            f"Objetivo: {benchmark['engagement']}% engagement",
            f"Objetivo: {benchmark['frecuencia']} posts por semana"
        ]
    }


# Agregar nuevos métodos al AnalizadorEngagement
AnalizadorEngagement.analizar_competidores_especificos = analizar_competidores_especificos
AnalizadorEngagement.generar_contenido_evergreen = generar_contenido_evergreen
AnalizadorEngagement.analizar_patrones_temporales_avanzado = analizar_patrones_temporales_avanzado
AnalizadorEngagement.crear_sistema_automatizacion = crear_sistema_automatizacion
AnalizadorEngagement.generar_benchmark_personalizado = generar_benchmark_personalizado




def calcular_score_predictivo_contenido(self, titulo: str, tipo_contenido: str, plataforma: str, hashtags: List[str] = None, horario: int = None) -> Dict[str, Any]:
    """Calcula un score predictivo para contenido antes de publicarlo"""
    score_total = 0
    factores = {}
    recomendaciones = []
    
    # Factor 1: Longitud del título
    longitud = len(titulo)
    if plataforma.lower() == 'linkedin':
        score_longitud = 20 if 1000 <= longitud <= 1500 else (15 if 500 <= longitud < 1000 or 1500 < longitud <= 2000 else 10)
    elif plataforma.lower() == 'twitter':
        score_longitud = 20 if 50 <= longitud <= 200 else (15 if 200 < longitud <= 280 else 10)
    else:
        score_longitud = 20 if 100 <= longitud <= 300 else 15
    
    factores['longitud'] = score_longitud
    score_total += score_longitud
    
    # Factor 2: Hook efectivo
    tiene_hook = any([
        '?' in titulo[:125],
        any(palabra in titulo[:125].lower() for palabra in ['cómo', 'por qué', 'qué', 'cuándo', 'dónde']),
        any(char in titulo[:125] for char in ['!', '...']),
        any(palabra in titulo[:125].lower() for palabra in ['descubre', 'aprende', 'revela', 'secretos'])
    ])
    
    score_hook = 25 if tiene_hook else 5
    if not tiene_hook:
        recomendaciones.append('Agrega un hook en las primeras 125 caracteres')
    factores['hook'] = score_hook
    score_total += score_hook
    
    # Factor 3: CTA
    ctas = ['comenta', 'comparte', 'envía', 'descubre', 'aprende', 'descarga', 'suscríbete', 'síguenos', 'visita']
    tiene_cta = any(cta in titulo.lower() for cta in ctas)
    score_cta = 20 if tiene_cta else 5
    if not tiene_cta:
        recomendaciones.append('Agrega un CTA claro')
    factores['cta'] = score_cta
    score_total += score_cta
    
    # Factor 4: Hashtags
    if hashtags:
        num_hashtags = len(hashtags)
        if plataforma.lower() == 'linkedin':
            score_hashtags = 15 if 5 <= num_hashtags <= 7 else (10 if 3 <= num_hashtags < 5 or 7 < num_hashtags <= 10 else 5)
        elif plataforma.lower() == 'instagram':
            score_hashtags = 15 if 5 <= num_hashtags <= 10 else (12 if 10 < num_hashtags <= 20 else 8)
        else:
            score_hashtags = 15 if 3 <= num_hashtags <= 5 else 10
    else:
        score_hashtags = 0
        recomendaciones.append('Agrega hashtags relevantes')
    factores['hashtags'] = score_hashtags
    score_total += score_hashtags
    
    # Factor 5: Tipo de contenido histórico
    analisis_tipo = self.analizar_por_tipo()
    if tipo_contenido in analisis_tipo:
        engagement_promedio = analisis_tipo[tipo_contenido]['engagement_score_promedio']
        mejor_engagement = max([d['engagement_score_promedio'] for d in analisis_tipo.values()])
        score_tipo = 20 if engagement_promedio >= mejor_engagement * 0.9 else (15 if engagement_promedio >= mejor_engagement * 0.7 else 10)
    else:
        score_tipo = 10
    factores['tipo_contenido'] = score_tipo
    score_total += score_tipo
    
    # Clasificación
    if score_total >= 90:
        nivel, probabilidad_viral = 'Excelente', 'Alta'
    elif score_total >= 75:
        nivel, probabilidad_viral = 'Muy Bueno', 'Media-Alta'
    elif score_total >= 60:
        nivel, probabilidad_viral = 'Bueno', 'Media'
    elif score_total >= 45:
        nivel, probabilidad_viral = 'Regular', 'Baja-Media'
    else:
        nivel, probabilidad_viral = 'Necesita Mejora', 'Baja'
    
    return {
        'score_total': score_total,
        'nivel': nivel,
        'probabilidad_viral': probabilidad_viral,
        'factores': factores,
        'recomendaciones': recomendaciones,
        'mejoras_sugeridas': recomendaciones[:3] if recomendaciones else []
    }


def generar_ideas_contenido_automaticas(self, cantidad: int = 10) -> List[Dict[str, Any]]:
    """Genera ideas de contenido automáticas basadas en análisis de datos"""
    ideas = []
    publicaciones_ordenadas = sorted(self.publicaciones, key=lambda p: p.engagement_score, reverse=True)
    top_publicaciones = publicaciones_ordenadas[:5]
    palabras_clave = self.analizar_palabras_clave_titulos()
    top_palabras = [p['palabra'] for p in palabras_clave[:10]]
    mejor_tipo = self.identificar_mejor_tipo()
    
    for i in range(cantidad):
        if i < len(top_publicaciones):
            pub_exitosa = top_publicaciones[i]
            ideas.append({
                'tipo': 'Variación de contenido exitoso',
                'idea': f"Crear variación de: '{pub_exitosa.titulo[:50]}...'",
                'formato': pub_exitosa.tipo_contenido,
                'plataforma': pub_exitosa.plataforma,
                'hashtags_sugeridos': pub_exitosa.hashtags[:5],
                'razon': f"Basado en publicación con engagement score de {pub_exitosa.engagement_score:.1f}",
                'potencial_engagement': 'Alto'
            })
        
        if i < len(top_palabras) and len(top_palabras) >= 2:
            palabra1 = top_palabras[i % len(top_palabras)]
            palabra2 = top_palabras[(i + 1) % len(top_palabras)]
            ideas.append({
                'tipo': 'Combinación de palabras clave',
                'idea': f"Contenido sobre '{palabra1}' y '{palabra2}'",
                'formato': mejor_tipo['tipo'],
                'plataforma': 'Multiplataforma',
                'hashtags_sugeridos': [f'#{palabra1}', f'#{palabra2}'] + [h['hashtag'] for h in self.analizar_hashtags_efectivos(top_n=3)],
                'razon': 'Combinación de palabras clave con alto engagement histórico',
                'potencial_engagement': 'Medio-Alto'
            })
    
    return ideas[:cantidad]


def analizar_conversion_y_negocio(self, valor_por_clic: float = 0.50, valor_por_conversion: float = 10.0) -> Dict[str, Any]:
    """Analiza métricas de conversión y valor de negocio del contenido"""
    if len(self.publicaciones) == 0:
        return {'error': 'No hay publicaciones para analizar'}
    
    analisis_conversion = {'metricas_por_publicacion': [], 'metricas_totales': {}, 'publicaciones_con_alto_valor': []}
    
    for pub in self.publicaciones:
        clics_estimados = int(pub.engagement_total * 0.1)
        valor_clics = clics_estimados * valor_por_clic
        conversiones_estimadas = int(clics_estimados * 0.02)
        valor_conversiones = conversiones_estimadas * valor_por_conversion
        valor_total_estimado = valor_clics + valor_conversiones
        roi = (valor_total_estimado / 50.0 * 100) if valor_total_estimado > 0 else 0
        
        analisis_conversion['metricas_por_publicacion'].append({
            'id': pub.id,
            'titulo': pub.titulo[:50],
            'engagement_total': pub.engagement_total,
            'clics_estimados': clics_estimados,
            'conversiones_estimadas': conversiones_estimadas,
            'valor_clics': valor_clics,
            'valor_conversiones': valor_conversiones,
            'valor_total': valor_total_estimado,
            'roi': roi
        })
    
    total_clics = sum(m['clics_estimados'] for m in analisis_conversion['metricas_por_publicacion'])
    total_conversiones = sum(m['conversiones_estimadas'] for m in analisis_conversion['metricas_por_publicacion'])
    
    analisis_conversion['metricas_totales'] = {
        'total_publicaciones': len(self.publicaciones),
        'total_clics_estimados': total_clics,
        'total_conversiones_estimadas': total_conversiones,
        'tasa_conversion_promedio': (total_conversiones / total_clics * 100) if total_clics > 0 else 0,
        'valor_total_negocio': sum(m['valor_clics'] + m['valor_conversiones'] for m in analisis_conversion['metricas_por_publicacion'])
    }
    
    analisis_conversion['publicaciones_con_alto_valor'] = sorted(analisis_conversion['metricas_por_publicacion'], key=lambda x: x['valor_total'], reverse=True)[:5]
    
    return analisis_conversion


# Agregar métodos al AnalizadorEngagement
AnalizadorEngagement.calcular_score_predictivo_contenido = calcular_score_predictivo_contenido
AnalizadorEngagement.generar_ideas_contenido_automaticas = generar_ideas_contenido_automaticas
AnalizadorEngagement.analizar_conversion_y_negocio = analizar_conversion_y_negocio




def analizar_competencia_avanzado(self, datos_competencia: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Análisis avanzado de competencia comparando métricas"""
    if not datos_competencia:
        datos_competencia = []
        for i in range(5):
            datos_competencia.append({
                'nombre': f'Competidor {i+1}',
                'engagement_rate_promedio': random.uniform(2.0, 8.0),
                'frecuencia_publicacion': random.randint(3, 10),
                'tipos_contenido': ['X', 'Y', 'Z'],
                'mejor_plataforma': random.choice(['LinkedIn', 'Twitter', 'Instagram'])
            })
    
    analisis_propio = {
        'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in self.publicaciones]) if self.publicaciones else 0,
        'frecuencia_publicacion': len(self.publicaciones) / 30 if self.publicaciones else 0,
        'tipos_contenido': list(set([p.tipo_contenido for p in self.publicaciones])),
        'mejor_plataforma': max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else 'N/A'
    }
    
    comparacion = {'posicion_ranking': 0, 'ventajas': [], 'desventajas': [], 'oportunidades': [], 'benchmarking': {}}
    
    engagement_competencia = [c['engagement_rate_promedio'] for c in datos_competencia]
    engagement_competencia.append(analisis_propio['engagement_rate_promedio'])
    ranking = sorted(enumerate(engagement_competencia), key=lambda x: x[1], reverse=True)
    
    for pos, (idx, rate) in enumerate(ranking):
        if idx == len(datos_competencia):
            comparacion['posicion_ranking'] = pos + 1
            break
    
    mejor_competidor = max(datos_competencia, key=lambda x: x['engagement_rate_promedio'])
    
    if analisis_propio['engagement_rate_promedio'] > mejor_competidor['engagement_rate_promedio']:
        comparacion['ventajas'].append(f"Tienes mejor engagement rate ({analisis_propio['engagement_rate_promedio']:.2f}% vs {mejor_competidor['engagement_rate_promedio']:.2f}%)")
    else:
        diferencia = mejor_competidor['engagement_rate_promedio'] - analisis_propio['engagement_rate_promedio']
        comparacion['desventajas'].append(f"El mejor competidor tiene {diferencia:.2f}% más de engagement rate")
        comparacion['oportunidades'].append(f"Mejorar estrategia para alcanzar el {mejor_competidor['engagement_rate_promedio']:.2f}% del mejor competidor")
    
    comparacion['benchmarking'] = {
        'engagement_rate_promedio_mercado': statistics.mean([c['engagement_rate_promedio'] for c in datos_competencia]),
        'engagement_rate_propio': analisis_propio['engagement_rate_promedio'],
        'diferencia_vs_mercado': analisis_propio['engagement_rate_promedio'] - statistics.mean([c['engagement_rate_promedio'] for c in datos_competencia]),
        'frecuencia_promedio_mercado': statistics.mean([c['frecuencia_publicacion'] for c in datos_competencia]),
        'frecuencia_propia': analisis_propio['frecuencia_publicacion']
    }
    
    return {'analisis_propio': analisis_propio, 'comparacion': comparacion, 'competidores': datos_competencia}


def generar_calendario_contenido_automatico(self, semanas: int = 4) -> Dict[str, Any]:
    """Genera un calendario de contenido automático optimizado"""
    calendario = {'semanas': semanas, 'publicaciones_programadas': [], 'resumen': {}}
    
    mejor_tipo = self.identificar_mejor_tipo()
    horarios = self.analizar_horarios_optimos()
    dias = self.analizar_dias_semana()
    frecuencia_optima = self.optimizar_frecuencia_publicacion()
    
    mejor_horario = max(horarios.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if horarios else '09-12'
    mejor_dia = max(dias.items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if dias else 'Monday'
    dias_entre_publicaciones = frecuencia_optima.get('frecuencia_optima_recomendada', 2)
    
    ideas = self.generar_ideas_contenido_automaticas(cantidad=semanas * 7)
    
    fecha_inicio = datetime.now()
    dia_semana_map = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    mejor_dia_num = dia_semana_map.get(mejor_dia, 0)
    indice_idea = 0
    
    for semana in range(semanas):
        for dia in range(7):
            fecha_publicacion = fecha_inicio + timedelta(days=dia + (semana * 7))
            
            if fecha_publicacion.weekday() == mejor_dia_num and indice_idea < len(ideas):
                idea = ideas[indice_idea]
                hora_publicacion = int(mejor_horario.split('-')[0])
                
                calendario['publicaciones_programadas'].append({
                    'fecha': fecha_publicacion.date().isoformat(),
                    'dia_semana': fecha_publicacion.strftime('%A'),
                    'hora': f"{hora_publicacion:02d}:00",
                    'tipo_contenido': idea['formato'],
                    'idea': idea['idea'],
                    'plataforma': idea['plataforma'],
                    'hashtags_sugeridos': idea['hashtags_sugeridos'],
                    'potencial_engagement': idea['potencial_engagement']
                })
                indice_idea += 1
    
    calendario['resumen'] = {
        'total_publicaciones': len(calendario['publicaciones_programadas']),
        'publicaciones_por_semana': len(calendario['publicaciones_programadas']) / semanas,
        'mejor_dia': mejor_dia,
        'mejor_horario': mejor_horario,
        'tipo_contenido_principal': mejor_tipo['tipo']
    }
    
    return calendario


def analizar_tendencias_mercado(self, palabras_clave: List[str] = None) -> Dict[str, Any]:
    """Analiza tendencias de mercado basándose en palabras clave y contenido"""
    if not palabras_clave:
        palabras_clave = [p['palabra'] for p in self.analizar_palabras_clave_titulos()[:10]]
    
    tendencias = {
        'palabras_clave_analizadas': palabras_clave,
        'tendencias_por_palabra': [],
        'recomendaciones': []
    }
    
    for palabra in palabras_clave:
        publicaciones_con_palabra = [p for p in self.publicaciones if palabra.lower() in p.titulo.lower()]
        
        if publicaciones_con_palabra:
            engagement_promedio = statistics.mean([p.engagement_score for p in publicaciones_con_palabra])
            frecuencia = len(publicaciones_con_palabra)
            
            # Analizar tendencia temporal
            fechas = sorted([p.fecha_publicacion for p in publicaciones_con_palabra])
            if len(fechas) >= 2:
                primera_mitad = [p for p in publicaciones_con_palabra if p.fecha_publicacion <= fechas[len(fechas)//2]]
                segunda_mitad = [p for p in publicaciones_con_palabra if p.fecha_publicacion > fechas[len(fechas)//2]]
                
                engagement_primera = statistics.mean([p.engagement_score for p in primera_mitad]) if primera_mitad else 0
                engagement_segunda = statistics.mean([p.engagement_score for p in segunda_mitad]) if segunda_mitad else 0
                
                cambio = engagement_segunda - engagement_primera
                tendencia = 'creciendo' if cambio > 0 else 'decreciendo' if cambio < 0 else 'estable'
            else:
                tendencia = 'estable'
                cambio = 0
            
            tendencias['tendencias_por_palabra'].append({
                'palabra': palabra,
                'frecuencia': frecuencia,
                'engagement_promedio': engagement_promedio,
                'tendencia': tendencia,
                'cambio_engagement': cambio,
                'recomendacion': 'Aumentar uso' if tendencia == 'creciendo' else 'Mantener uso' if tendencia == 'estable' else 'Reducir uso'
            })
    
    # Ordenar por engagement promedio
    tendencias['tendencias_por_palabra'].sort(key=lambda x: x['engagement_promedio'], reverse=True)
    
    # Generar recomendaciones generales
    palabras_creciendo = [t for t in tendencias['tendencias_por_palabra'] if t['tendencia'] == 'creciendo']
    if palabras_creciendo:
        mejor_palabra = palabras_creciendo[0]
        tendencias['recomendaciones'].append(f"Incrementar uso de '{mejor_palabra['palabra']}' - tendencia creciente con {mejor_palabra['engagement_promedio']:.1f} engagement promedio")
    
    return tendencias


def optimizar_hashtags_por_plataforma(self) -> Dict[str, Any]:
    """Optimiza hashtags específicamente para cada plataforma"""
    optimizacion = {}
    
    analisis_plataformas = self.analizar_por_plataforma()
    hashtags_por_plataforma = self.analizar_hashtags_por_plataforma()
    
    for plataforma in analisis_plataformas.keys():
        hashtags_plataforma = hashtags_por_plataforma.get(plataforma, [])
        
        # Recomendaciones específicas por plataforma
        if plataforma.lower() == 'linkedin':
            hashtags_optimos = [h for h in hashtags_plataforma if h['veces_usado'] >= 2][:7]
            recomendacion = 'LinkedIn: Usa 5-7 hashtags profesionales y específicos'
        elif plataforma.lower() == 'instagram':
            hashtags_optimos = [h for h in hashtags_plataforma if h['veces_usado'] >= 1][:10]
            recomendacion = 'Instagram: Usa 5-10 hashtags, mezcla populares y nicho'
        elif plataforma.lower() == 'twitter':
            hashtags_optimos = [h for h in hashtags_plataforma if h['veces_usado'] >= 2][:3]
            recomendacion = 'Twitter: Usa 1-3 hashtags relevantes y trending'
        else:
            hashtags_optimos = [h for h in hashtags_plataforma if h['veces_usado'] >= 1][:5]
            recomendacion = f'{plataforma}: Usa 3-5 hashtags relevantes'
        
        optimizacion[plataforma] = {
            'hashtags_recomendados': [h['hashtag'] for h in hashtags_optimos],
            'hashtags_con_mejor_engagement': sorted(hashtags_plataforma, key=lambda x: x['engagement_score_promedio'], reverse=True)[:5],
            'recomendacion': recomendacion,
            'cantidad_optima': len(hashtags_optimos)
        }
    
    return optimizacion


def generar_reporte_ejecutivo_completo(self) -> Dict[str, Any]:
    """Genera un reporte ejecutivo completo con todos los análisis"""
    reporte = {
        'fecha_generacion': datetime.now().isoformat(),
        'resumen_ejecutivo': {},
        'metricas_clave': {},
        'recomendaciones_prioritarias': [],
        'analisis_detallados': {}
    }
    
    # Resumen ejecutivo
    mejor_tipo = self.identificar_mejor_tipo()
    reporte['resumen_ejecutivo'] = {
        'mejor_tipo_contenido': mejor_tipo['datos']['nombre'],
        'engagement_rate_promedio': mejor_tipo['datos']['engagement_rate_promedio'],
        'total_publicaciones': len(self.publicaciones),
        'periodo_analizado': 'Últimos 30 días'
    }
    
    # Métricas clave
    reporte['metricas_clave'] = {
        'engagement_total': sum(p.engagement_total for p in self.publicaciones),
        'engagement_rate_promedio': statistics.mean([p.engagement_rate for p in self.publicaciones]) if self.publicaciones else 0,
        'publicaciones_virales': sum(1 for p in self.publicaciones if p.es_viral),
        'mejor_plataforma': max(self.analizar_por_plataforma().items(), key=lambda x: x[1]['engagement_score_promedio'])[0] if self.analizar_por_plataforma() else 'N/A'
    }
    
    # Recomendaciones prioritarias
    gaps = self.analizar_gaps_contenido()
    if gaps.get('oportunidades'):
        reporte['recomendaciones_prioritarias'].extend([o['descripcion'] for o in gaps['oportunidades'][:3]])
    
    frecuencia = self.optimizar_frecuencia_publicacion()
    if frecuencia.get('recomendacion'):
        reporte['recomendaciones_prioritarias'].append(frecuencia['recomendacion'])
    
    # Análisis detallados
    reporte['analisis_detallados'] = {
        'por_tipo': self.analizar_por_tipo(),
        'por_plataforma': self.analizar_por_plataforma(),
        'horarios_optimos': self.analizar_horarios_optimos(),
        'hashtags_efectivos': self.analizar_hashtags_efectivos(top_n=10),
        'tendencias': self.analizar_tendencias_temporales(),
        'gaps': gaps,
        'roi': self.calcular_retorno_inversion_contenido() if hasattr(self, 'calcular_retorno_inversion_contenido') else {}
    }
    
    return reporte


# Agregar métodos al AnalizadorEngagement
AnalizadorEngagement.analizar_competencia_avanzado = analizar_competencia_avanzado
AnalizadorEngagement.generar_calendario_contenido_automatico = generar_calendario_contenido_automatico
AnalizadorEngagement.analizar_tendencias_mercado = analizar_tendencias_mercado
AnalizadorEngagement.optimizar_hashtags_por_plataforma = optimizar_hashtags_por_plataforma
AnalizadorEngagement.generar_reporte_ejecutivo_completo = generar_reporte_ejecutivo_completo


if __name__ == '__main__':
    main()
