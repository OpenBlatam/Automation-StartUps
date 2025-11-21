#!/usr/bin/env python3
"""
Optimizador de Engagement para Publicaciones de Testimonios
Integra análisis de engagement histórico para optimizar publicaciones generadas
"""

import logging
import re
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Intentar importar el analizador de engagement existente
try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    ENGAGEMENT_ANALYZER_AVAILABLE = True
except ImportError:
    ENGAGEMENT_ANALYZER_AVAILABLE = False
    logger.debug("Analizador de engagement completo no disponible")

# Intentar importar analizador de tendencias
try:
    from testimonial_trend_analyzer import TrendAnalyzer
    TREND_ANALYZER_AVAILABLE = True
except ImportError:
    TREND_ANALYZER_AVAILABLE = False
    logger.debug("Analizador de tendencias no disponible")


@dataclass
class EngagementPrediction:
    """Predicción de engagement para una publicación"""
    predicted_score: float  # 0-100
    predicted_engagement_rate: float  # Porcentaje
    confidence: float  # 0-1
    factors: Dict[str, Any]
    recommendations: List[str]
    optimal_posting_time: Optional[str] = None


@dataclass
class ContentOptimization:
    """Optimizaciones sugeridas para el contenido"""
    hashtag_suggestions: List[str]
    length_optimization: Optional[str]
    tone_adjustments: List[str]
    structure_improvements: List[str]
    engagement_boosters: List[str]


class EngagementOptimizer:
    """Optimizador de engagement basado en análisis histórico"""
    
    # Hashtags que históricamente generan más engagement por plataforma
    HIGH_ENGAGEMENT_HASHTAGS = {
        'instagram': [
            '#testimonial', '#successstory', '#clientstory', '#results', '#transformation',
            '#beforeandafter', '#customersuccess', '#realtestimonials', '#proof', '#results',
            '#growth', '#achievement', '#milestone', '#win', '#success'
        ],
        'linkedin': [
            '#testimonial', '#customersuccess', '#clienttestimonial', '#results', '#businessgrowth',
            '#successstory', '#roi', '#transformation', '#achievement', '#businessresults',
            '#customerexperience', '#satisfaction', '#businessimpact', '#growth', '#success'
        ],
        'facebook': [
            '#testimonial', '#success', '#results', '#transformation', '#happycustomer',
            '#reviews', '#proof', '#achievement', '#growth', '#successstory'
        ],
        'twitter': [
            '#testimonial', '#success', '#results', '#growth', '#achievement',
            '#proof', '#transformation', '#roi', '#business', '#win'
        ],
        'tiktok': [
            '#testimonial', '#successstory', '#results', '#transformation', '#proof',
            '#fyp', '#viral', '#success', '#growth', '#achievement'
        ]
    }
    
    # Factores que aumentan engagement
    ENGAGEMENT_BOOSTERS = {
        'numbers': {'weight': 1.5, 'description': 'Incluir números y porcentajes'},
        'emojis': {'weight': 1.2, 'description': 'Usar emojis relevantes'},
        'questions': {'weight': 1.3, 'description': 'Incluir preguntas retóricas'},
        'cta': {'weight': 1.4, 'description': 'Llamada a la acción clara'},
        'storytelling': {'weight': 1.6, 'description': 'Estructura narrativa'},
        'specificity': {'weight': 1.3, 'description': 'Detalles específicos y concretos'}
    }
    
    # Longitudes óptimas por plataforma (caracteres)
    OPTIMAL_LENGTHS = {
        'instagram': {'min': 100, 'max': 300, 'optimal': 200},
        'linkedin': {'min': 150, 'max': 500, 'optimal': 300},
        'facebook': {'min': 100, 'max': 400, 'optimal': 250},
        'twitter': {'min': 50, 'max': 280, 'optimal': 200},
        'tiktok': {'min': 50, 'max': 300, 'optimal': 150}
    }
    
    # Horarios óptimos por plataforma (hora local)
    OPTIMAL_POSTING_TIMES = {
        'instagram': ['09:00-11:00', '13:00-15:00', '18:00-20:00'],
        'linkedin': ['08:00-10:00', '12:00-14:00', '17:00-19:00'],
        'facebook': ['09:00-11:00', '13:00-15:00', '19:00-21:00'],
        'twitter': ['08:00-10:00', '12:00-14:00', '17:00-19:00'],
        'tiktok': ['18:00-22:00', '06:00-09:00']
    }
    
    def __init__(
        self,
        historical_data: Optional[List[Dict[str, Any]]] = None,
        engagement_analyzer: Optional[Any] = None,
        historical_file: Optional[str] = None
    ):
        """
        Inicializa el optimizador
        
        Args:
            historical_data: Datos históricos de publicaciones con engagement
            engagement_analyzer: Instancia de AnalizadorEngagement (opcional)
            historical_file: Archivo JSON con datos históricos (opcional)
        """
        self.historical_data = historical_data or []
        self.engagement_analyzer = engagement_analyzer
        self.historical_file = historical_file
        
        # Cargar datos históricos desde archivo si se proporciona
        if historical_file and not self.historical_data:
            self._load_historical_data(historical_file)
        
        # Integrar con analizador de engagement si está disponible
        if ENGAGEMENT_ANALYZER_AVAILABLE and self.engagement_analyzer:
            self._integrate_engagement_analyzer()
        
        self._analyze_historical_patterns()
        
        # Inicializar analizador de tendencias si está disponible
        if TREND_ANALYZER_AVAILABLE and self.historical_data:
            self.trend_analyzer = TrendAnalyzer(historical_posts=self.historical_data)
        else:
            self.trend_analyzer = None
    
    def _load_historical_data(self, file_path: str):
        """Carga datos históricos desde un archivo JSON"""
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Aceptar diferentes formatos de datos históricos
                    if isinstance(data, list):
                        self.historical_data = data
                    elif isinstance(data, dict) and 'publicaciones' in data:
                        self.historical_data = data['publicaciones']
                    elif isinstance(data, dict) and 'posts' in data:
                        self.historical_data = data['posts']
                    logger.info(f"Datos históricos cargados: {len(self.historical_data)} publicaciones")
        except Exception as e:
            logger.warning(f"Error al cargar datos históricos: {e}")
    
    def _integrate_engagement_analyzer(self):
        """Integra datos del analizador de engagement existente"""
        if not self.engagement_analyzer:
            return
        
        try:
            # Obtener publicaciones del analizador
            if hasattr(self.engagement_analyzer, 'publicaciones'):
                for pub in self.engagement_analyzer.publicaciones:
                    post_data = {
                        'platform': pub.plataforma.lower(),
                        'hashtags': pub.hashtags,
                        'engagement_rate': pub.engagement_rate,
                        'engagement_score': pub.engagement_score,
                        'engagement_total': pub.engagement_total,
                        'likes': pub.likes,
                        'comentarios': pub.comentarios,
                        'shares': pub.shares,
                        'impresiones': pub.impresiones,
                        'fecha_publicacion': pub.fecha_publicacion.isoformat() if isinstance(pub.fecha_publicacion, datetime) else str(pub.fecha_publicacion),
                        'content': getattr(pub, 'titulo', ''),
                        'tipo_contenido': getattr(pub, 'tipo_contenido', 'testimonial')
                    }
                    self.historical_data.append(post_data)
                logger.info(f"Integrados {len(self.engagement_analyzer.publicaciones)} publicaciones del analizador")
        except Exception as e:
            logger.warning(f"Error al integrar analizador de engagement: {e}")
    
    def _analyze_historical_patterns(self):
        """Analiza patrones históricos para mejorar predicciones"""
        if not self.historical_data:
            return
        
        # Analizar hashtags más efectivos
        self.effective_hashtags = {}
        hashtag_engagement = defaultdict(list)
        
        # Analizar patrones por plataforma
        platform_stats = defaultdict(lambda: {
            'total_posts': 0,
            'total_engagement': 0,
            'avg_engagement_rate': 0,
            'best_lengths': [],
            'best_times': []
        })
        
        for post in self.historical_data:
            platform = post.get('platform', 'general').lower()
            hashtags = post.get('hashtags', [])
            engagement_rate = post.get('engagement_rate', 0)
            engagement_score = post.get('engagement_score', 0)
            
            # Estadísticas por plataforma
            platform_stats[platform]['total_posts'] += 1
            platform_stats[platform]['total_engagement'] += engagement_score
            platform_stats[platform]['avg_engagement_rate'] += engagement_rate
            
            # Longitudes óptimas
            content_length = len(post.get('content', ''))
            if engagement_rate > 5.0:  # Solo posts con buen engagement
                platform_stats[platform]['best_lengths'].append(content_length)
            
            # Horarios óptimos
            fecha = post.get('fecha_publicacion')
            if fecha:
                try:
                    if isinstance(fecha, str):
                        fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    else:
                        fecha_dt = fecha
                    hour = fecha_dt.hour
                    if engagement_rate > 5.0:
                        platform_stats[platform]['best_times'].append(hour)
                except:
                    pass
            
            # Hashtags efectivos
            for hashtag in hashtags:
                hashtag_engagement[platform].append({
                    'hashtag': hashtag,
                    'engagement_rate': engagement_rate,
                    'engagement_score': engagement_score
                })
        
        # Calcular hashtags más efectivos por plataforma
        for platform, data in hashtag_engagement.items():
            hashtag_scores = Counter()
            hashtag_rates = defaultdict(list)
            
            for item in data:
                hashtag = item['hashtag']
                hashtag_scores[hashtag] += item['engagement_score']
                hashtag_rates[hashtag].append(item['engagement_rate'])
            
            # Calcular promedio de engagement rate por hashtag
            hashtag_avg_rates = {
                tag: sum(rates) / len(rates)
                for tag, rates in hashtag_rates.items()
            }
            
            # Ordenar por score y rate combinados
            combined_scores = {
                tag: hashtag_scores[tag] * 0.6 + hashtag_avg_rates.get(tag, 0) * 100 * 0.4
                for tag in hashtag_scores
            }
            
            self.effective_hashtags[platform] = [
                tag for tag, _ in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:20]
            ]
        
        # Calcular promedios y óptimos por plataforma
        self.platform_stats = {}
        for platform, stats in platform_stats.items():
            if stats['total_posts'] > 0:
                stats['avg_engagement_rate'] /= stats['total_posts']
                
                # Longitud óptima (mediana de las mejores)
                if stats['best_lengths']:
                    stats['optimal_length'] = int(sum(stats['best_lengths']) / len(stats['best_lengths']))
                else:
                    stats['optimal_length'] = self.OPTIMAL_LENGTHS.get(platform, {}).get('optimal', 200)
                
                # Horario óptimo (moda de las mejores horas)
                if stats['best_times']:
                    hour_counts = Counter(stats['best_times'])
                    stats['optimal_hour'] = hour_counts.most_common(1)[0][0]
                else:
                    stats['optimal_hour'] = 10  # Default
                
                self.platform_stats[platform] = stats
        
        logger.debug(f"Patrones analizados para {len(self.platform_stats)} plataformas")
    
    def predict_engagement(
        self,
        post_content: str,
        hashtags: List[str],
        platform: str,
        has_cta: bool = True,
        has_numbers: bool = False,
        has_emojis: bool = False
    ) -> EngagementPrediction:
        """
        Predice el engagement potencial de una publicación
        
        Args:
            post_content: Contenido de la publicación
            hashtags: Lista de hashtags
            platform: Plataforma objetivo
            has_cta: Si tiene llamada a la acción
            has_numbers: Si contiene números/porcentajes
            has_emojis: Si contiene emojis
        
        Returns:
            EngagementPrediction con predicción y recomendaciones
        """
        base_score = 50.0  # Score base
        
        # Factor de longitud (usar datos históricos si están disponibles)
        length = len(post_content)
        if platform in getattr(self, 'platform_stats', {}) and 'optimal_length' in self.platform_stats[platform]:
            optimal_length = self.platform_stats[platform]['optimal_length']
        else:
            optimal_length = self.OPTIMAL_LENGTHS.get(platform, {}).get('optimal', 200)
        
        length_diff = abs(length - optimal_length)
        length_factor = max(0.7, 1.0 - (length_diff / optimal_length) * 0.3)
        base_score *= length_factor
        
        # Factor de hashtags
        hashtag_count = len(hashtags)
        optimal_hashtag_count = {
            'instagram': 10, 'linkedin': 5, 'facebook': 5,
            'twitter': 3, 'tiktok': 5
        }.get(platform, 5)
        
        if hashtag_count > 0:
            hashtag_factor = min(1.2, 0.8 + (hashtag_count / optimal_hashtag_count) * 0.4)
            base_score *= hashtag_factor
        
        # Verificar calidad de hashtags
        high_quality_hashtags = self.HIGH_ENGAGEMENT_HASHTAGS.get(platform, [])
        matching_hashtags = [h for h in hashtags if h.lower() in [qh.lower() for qh in high_quality_hashtags]]
        if matching_hashtags:
            base_score += len(matching_hashtags) * 2
        
        # Factores de contenido
        if has_numbers:
            base_score *= self.ENGAGEMENT_BOOSTERS['numbers']['weight']
        
        if has_emojis:
            base_score *= self.ENGAGEMENT_BOOSTERS['emojis']['weight']
        
        if has_cta:
            base_score *= self.ENGAGEMENT_BOOSTERS['cta']['weight']
        
        # Detectar storytelling
        if self._has_storytelling_structure(post_content):
            base_score *= self.ENGAGEMENT_BOOSTERS['storytelling']['weight']
        
        # Detectar preguntas
        if '?' in post_content:
            base_score *= self.ENGAGEMENT_BOOSTERS['questions']['weight']
        
        # Normalizar score (0-100)
        predicted_score = min(100, max(0, base_score))
        
        # Calcular engagement rate estimado
        # Engagement rate típico: 1-5% para contenido orgánico
        base_rate = 2.0  # 2% base
        rate_multiplier = predicted_score / 50.0
        predicted_engagement_rate = min(10.0, base_rate * rate_multiplier)
        
        # Calcular confianza basada en datos históricos
        confidence = 0.6  # Base
        if self.historical_data:
            similar_posts = [
                p for p in self.historical_data
                if p.get('platform', '').lower() == platform.lower() and
                abs(len(p.get('content', '')) - length) < 50
            ]
            if similar_posts:
                # Calcular promedio de engagement de posts similares
                avg_similar_engagement = sum(
                    p.get('engagement_rate', 0) for p in similar_posts
                ) / len(similar_posts)
                
                # Ajustar confianza basado en muestra y consistencia
                sample_factor = min(0.2, len(similar_posts) * 0.02)
                consistency_factor = min(0.1, 1.0 - (avg_similar_engagement / 10.0) * 0.1) if avg_similar_engagement > 0 else 0
                confidence = min(0.95, 0.6 + sample_factor + consistency_factor)
                
                # Ajustar predicción basada en promedio histórico
                if avg_similar_engagement > 0:
                    predicted_engagement_rate = (predicted_engagement_rate + avg_similar_engagement) / 2
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            post_content, hashtags, platform, predicted_score
        )
        
        # Determinar horario óptimo (usar datos históricos si están disponibles)
        if self.trend_analyzer:
            optimal_timing = self.trend_analyzer.predict_optimal_posting_time(platform)
            if optimal_timing.get('best_hour') is not None:
                best_hour = optimal_timing['best_hour']
                optimal_posting_time = f"{best_hour:02d}:00-{(best_hour+2)%24:02d}:00"
            elif platform in getattr(self, 'platform_stats', {}) and 'optimal_hour' in self.platform_stats[platform]:
                optimal_hour = self.platform_stats[platform]['optimal_hour']
                optimal_posting_time = f"{optimal_hour:02d}:00-{(optimal_hour+2)%24:02d}:00"
            else:
                optimal_posting_time = self.OPTIMAL_POSTING_TIMES.get(platform, ['09:00-11:00'])[0]
        elif platform in getattr(self, 'platform_stats', {}) and 'optimal_hour' in self.platform_stats[platform]:
            optimal_hour = self.platform_stats[platform]['optimal_hour']
            optimal_posting_time = f"{optimal_hour:02d}:00-{(optimal_hour+2)%24:02d}:00"
        else:
            optimal_posting_time = self.OPTIMAL_POSTING_TIMES.get(platform, ['09:00-11:00'])[0]
        
        return EngagementPrediction(
            predicted_score=round(predicted_score, 1),
            predicted_engagement_rate=round(predicted_engagement_rate, 2),
            confidence=round(confidence, 2),
            factors={
                'length_factor': round(length_factor, 2),
                'hashtag_factor': round(hashtag_factor if hashtag_count > 0 else 1.0, 2),
                'has_numbers': has_numbers,
                'has_emojis': has_emojis,
                'has_cta': has_cta,
                'has_storytelling': self._has_storytelling_structure(post_content),
                'has_questions': '?' in post_content
            },
            recommendations=recommendations,
            optimal_posting_time=optimal_posting_time
        )
    
    def _has_storytelling_structure(self, content: str) -> bool:
        """Detecta si el contenido tiene estructura narrativa"""
        # Buscar indicadores de storytelling
        storytelling_indicators = [
            r'\b(antes|después|entonces|cuando|mientras|finalmente)\b',
            r'\b(logré|conseguí|obtuve|alcanzé|mejoré)\b',
            r'\b(empezó|comenzó|inició)\b',
            r'\b(resultado|consecuencia|efecto)\b'
        ]
        
        matches = sum(1 for pattern in storytelling_indicators if re.search(pattern, content, re.IGNORECASE))
        return matches >= 2
    
    def _generate_recommendations(
        self,
        content: str,
        hashtags: List[str],
        platform: str,
        current_score: float
    ) -> List[str]:
        """Genera recomendaciones para mejorar el engagement"""
        recommendations = []
        
        # Recomendaciones de longitud
        length = len(content)
        optimal = self.OPTIMAL_LENGTHS.get(platform, {}).get('optimal', 200)
        if length < optimal * 0.8:
            recommendations.append(f"Considera expandir el contenido. Longitud actual: {length}, óptima: {optimal}")
        elif length > optimal * 1.2:
            recommendations.append(f"Considera acortar el contenido. Longitud actual: {length}, óptima: {optimal}")
        
        # Recomendaciones de hashtags
        optimal_count = {
            'instagram': 10, 'linkedin': 5, 'facebook': 5,
            'twitter': 3, 'tiktok': 5
        }.get(platform, 5)
        
        if len(hashtags) < optimal_count:
            recommendations.append(f"Agrega más hashtags. Actuales: {len(hashtags)}, óptimos: {optimal_count}")
        
        # Recomendaciones de contenido
        if not re.search(r'\d+%|\d+\s*(veces|meses|años)', content):
            recommendations.append("Agrega números o porcentajes para mayor credibilidad")
        
        if '?' not in content:
            recommendations.append("Considera agregar una pregunta retórica para aumentar engagement")
        
        if not self._has_storytelling_structure(content):
            recommendations.append("Estructura el contenido como una historia para mayor impacto")
        
        # Recomendaciones de hashtags específicos
        high_quality = self.HIGH_ENGAGEMENT_HASHTAGS.get(platform, [])
        missing_hashtags = [h for h in high_quality[:5] if h.lower() not in [tag.lower() for tag in hashtags]]
        if missing_hashtags:
            recommendations.append(f"Considera agregar estos hashtags de alto engagement: {', '.join(missing_hashtags[:3])}")
        
        return recommendations
    
    def optimize_content(
        self,
        post_content: str,
        hashtags: List[str],
        platform: str,
        current_hashtags: Optional[List[str]] = None
    ) -> ContentOptimization:
        """
        Genera optimizaciones específicas para el contenido
        
        Args:
            post_content: Contenido actual
            hashtags: Hashtags actuales
            platform: Plataforma objetivo
            current_hashtags: Hashtags existentes (para evitar duplicados)
        
        Returns:
            ContentOptimization con sugerencias
        """
        # Optimizar hashtags
        optimal_hashtag_count = {
            'instagram': 10, 'linkedin': 5, 'facebook': 5,
            'twitter': 3, 'tiktok': 5
        }.get(platform, 5)
        
        # Combinar hashtags de alto engagement con los existentes
        high_quality_hashtags = self.HIGH_ENGAGEMENT_HASHTAGS.get(platform, [])
        existing_lower = [h.lower() for h in (current_hashtags or hashtags)]
        
        suggested_hashtags = []
        # Agregar hashtags de alto engagement que no estén ya incluidos
        for hq_tag in high_quality_hashtags:
            if hq_tag.lower() not in existing_lower:
                suggested_hashtags.append(hq_tag)
            if len(suggested_hashtags) >= optimal_hashtag_count - len(hashtags):
                break
        
        # Agregar hashtags efectivos históricos si están disponibles
        if platform in getattr(self, 'effective_hashtags', {}):
            for tag in self.effective_hashtags[platform]:
                if tag.lower() not in existing_lower and tag not in suggested_hashtags:
                    suggested_hashtags.append(tag)
                if len(suggested_hashtags) >= optimal_hashtag_count:
                    break
        
        # Optimización de longitud
        length = len(post_content)
        optimal = self.OPTIMAL_LENGTHS.get(platform, {}).get('optimal', 200)
        length_optimization = None
        if length < optimal * 0.8:
            length_optimization = f"Expandir contenido de {length} a ~{optimal} caracteres"
        elif length > optimal * 1.2:
            length_optimization = f"Acortar contenido de {length} a ~{optimal} caracteres"
        
        # Ajustes de tono
        tone_adjustments = []
        if platform == 'linkedin' and '!' in post_content:
            tone_adjustments.append("Reducir exclamaciones para tono más profesional")
        if platform in ['instagram', 'tiktok'] and '!' not in post_content:
            tone_adjustments.append("Considera agregar más entusiasmo con exclamaciones")
        
        # Mejoras de estructura
        structure_improvements = []
        if not self._has_storytelling_structure(post_content):
            structure_improvements.append("Reorganizar como historia: situación inicial → cambio → resultado")
        if '?' not in post_content:
            structure_improvements.append("Agregar pregunta al inicio para captar atención")
        
        # Boosters de engagement
        engagement_boosters = []
        if not re.search(r'\d+', post_content):
            engagement_boosters.append("Agregar números o porcentajes específicos")
        if platform in ['instagram', 'facebook', 'tiktok'] and len(re.findall(r'[😀-🙏🌀-🗿]', post_content)) < 2:
            engagement_boosters.append("Agregar 2-3 emojis relevantes")
        if '?' not in post_content:
            engagement_boosters.append("Incluir pregunta retórica para generar interacción")
        
        return ContentOptimization(
            hashtag_suggestions=suggested_hashtags[:optimal_hashtag_count],
            length_optimization=length_optimization,
            tone_adjustments=tone_adjustments,
            structure_improvements=structure_improvements,
            engagement_boosters=engagement_boosters
        )
    
    def get_optimal_posting_schedule(
        self,
        platform: str,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Obtiene el horario óptimo para publicar
        
        Args:
            platform: Plataforma objetivo
            timezone: Zona horaria
        
        Returns:
            Dict con horarios óptimos y días recomendados
        """
        # Usar análisis de tendencias si está disponible
        if self.trend_analyzer:
            optimal_timing = self.trend_analyzer.predict_optimal_posting_time(platform)
            
            # Construir respuesta con datos del análisis
            optimal_times = []
            if optimal_timing.get('best_hour') is not None:
                best_hour = optimal_timing['best_hour']
                optimal_times.append(f"{best_hour:02d}:00-{(best_hour+2)%24:02d}:00")
            
            optimal_days = []
            if optimal_timing.get('best_day'):
                optimal_days.append(optimal_timing['best_day'])
            
            # Agregar tiempos estándar si no hay datos históricos suficientes
            if not optimal_times:
                optimal_times = self.OPTIMAL_POSTING_TIMES.get(platform, ['09:00-11:00'])
            
            if not optimal_days:
                optimal_days = {
                    'instagram': ['Martes', 'Miércoles', 'Jueves'],
                    'linkedin': ['Martes', 'Miércoles', 'Jueves'],
                    'facebook': ['Jueves', 'Viernes', 'Sábado', 'Domingo'],
                    'twitter': ['Lunes', 'Martes', 'Miércoles', 'Jueves'],
                    'tiktok': ['Martes', 'Miércoles', 'Jueves', 'Viernes']
                }.get(platform, ['Martes', 'Miércoles', 'Jueves'])
            
            return {
                'platform': platform,
                'optimal_times': optimal_times,
                'optimal_days': optimal_days,
                'timezone': timezone,
                'next_best_time': optimal_times[0] if optimal_times else '09:00-11:00',
                'data_driven': True,
                'confidence': optimal_timing.get('confidence', 'medium'),
                'sample_size': optimal_timing.get('sample_size', 0)
            }
        
        # Fallback a valores estándar
        optimal_times = self.OPTIMAL_POSTING_TIMES.get(platform, ['09:00-11:00'])
        
        optimal_days = {
            'instagram': ['Martes', 'Miércoles', 'Jueves'],
            'linkedin': ['Martes', 'Miércoles', 'Jueves'],
            'facebook': ['Jueves', 'Viernes', 'Sábado', 'Domingo'],
            'twitter': ['Lunes', 'Martes', 'Miércoles', 'Jueves'],
            'tiktok': ['Martes', 'Miércoles', 'Jueves', 'Viernes']
        }.get(platform, ['Martes', 'Miércoles', 'Jueves'])
        
        return {
            'platform': platform,
            'optimal_times': optimal_times,
            'optimal_days': optimal_days,
            'timezone': timezone,
            'next_best_time': optimal_times[0] if optimal_times else '09:00-11:00',
            'data_driven': False
        }
    
    def get_trend_insights(self) -> Dict[str, Any]:
        """
        Obtiene insights de tendencias temporales
        
        Returns:
            Dict con insights y recomendaciones basadas en tendencias
        """
        if not self.trend_analyzer:
            return {"error": "Analizador de tendencias no disponible"}
        
        return self.trend_analyzer.generate_insights()

