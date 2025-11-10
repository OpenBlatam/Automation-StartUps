"""
Análisis de Tendencias de Mercado

Sistema avanzado para analizar tendencias de mercado y generar insights accionables.
Incluye análisis de:
- Tendencias de búsqueda (Google Trends, Bing)
- Sentimiento en redes sociales
- Análisis de competidores
- Predicciones de mercado
- Análisis de keywords y SEO
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

import httpx
import pandas as pd
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
from pybreaker import CircuitBreaker
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Circuit breaker para APIs externas
market_api_breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

# Cache para resultados de análisis
trends_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hora


@dataclass
class MarketTrend:
    """Estructura para una tendencia de mercado."""
    trend_name: str
    category: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend_direction: str  # 'up', 'down', 'stable'
    confidence: float  # 0-1
    timeframe: str
    source: str
    metadata: Dict[str, Any]


@dataclass
class MarketInsight:
    """Insight accionable sobre el mercado."""
    insight_id: str
    title: str
    description: str
    category: str  # 'opportunity', 'threat', 'trend', 'recommendation'
    priority: str  # 'high', 'medium', 'low'
    actionable_steps: List[str]
    expected_impact: str
    timeframe: str
    confidence_score: float
    supporting_data: Dict[str, Any]
    created_at: datetime


class MarketTrendsAnalyzer:
    """Analizador de tendencias de mercado."""
    
    def __init__(
        self,
        postgres_conn_id: Optional[str] = None,
        google_trends_api_key: Optional[str] = None,
        news_api_key: Optional[str] = None,
        social_api_key: Optional[str] = None
    ):
        """
        Inicializa el analizador de tendencias.
        
        Args:
            postgres_conn_id: Connection ID para PostgreSQL
            google_trends_api_key: API key para Google Trends API
            news_api_key: API key para News API
            social_api_key: API key para APIs de redes sociales
        """
        self.postgres_conn_id = postgres_conn_id
        self.google_trends_api_key = google_trends_api_key or os.getenv("GOOGLE_TRENDS_API_KEY")
        self.news_api_key = news_api_key or os.getenv("NEWS_API_KEY")
        self.social_api_key = social_api_key or os.getenv("SOCIAL_API_KEY")
        
        self.http_client = httpx.Client(timeout=30.0)
        self.trends_history: Dict[str, List[MarketTrend]] = defaultdict(list)
        
    def analyze_industry_trends(
        self,
        industry: str,
        timeframe_months: int = 6,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analiza tendencias de una industria específica.
        
        Args:
            industry: Nombre de la industria
            timeframe_months: Período de análisis en meses
            keywords: Keywords específicos para analizar
            
        Returns:
            Diccionario con análisis completo de tendencias
        """
        cache_key = f"industry_trends_{industry}_{timeframe_months}"
        if cache_key in trends_cache:
            logger.info(f"Using cached trends for {industry}")
            return trends_cache[cache_key]
        
        logger.info(f"Analyzing trends for industry: {industry}")
        
        # Keywords por defecto si no se proporcionan
        if not keywords:
            keywords = self._get_default_keywords(industry)
        
        analysis_results = {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "timeframe_months": timeframe_months,
            "trends": [],
            "insights": [],
            "recommendations": [],
            "risk_factors": [],
            "opportunities": []
        }
        
        # 1. Análisis de búsquedas (Google Trends)
        search_trends = self._analyze_search_trends(industry, keywords, timeframe_months)
        analysis_results["trends"].extend(search_trends)
        
        # 2. Análisis de noticias
        news_trends = self._analyze_news_trends(industry, timeframe_months)
        analysis_results["trends"].extend(news_trends)
        
        # 3. Análisis de sentimiento
        sentiment_analysis = self._analyze_sentiment(industry, keywords, timeframe_months)
        analysis_results["trends"].extend(sentiment_analysis)
        
        # 4. Análisis de competidores
        competitor_analysis = self._analyze_competitors(industry)
        analysis_results["trends"].extend(competitor_analysis)
        
        # 5. Generar insights accionables
        insights = self._generate_actionable_insights(analysis_results["trends"])
        analysis_results["insights"] = insights
        
        # 6. Generar recomendaciones
        recommendations = self._generate_recommendations(analysis_results["trends"], insights)
        analysis_results["recommendations"] = recommendations
        
        # 7. Identificar riesgos y oportunidades
        risks_opportunities = self._identify_risks_opportunities(analysis_results["trends"])
        analysis_results["risk_factors"] = risks_opportunities.get("risks", [])
        analysis_results["opportunities"] = risks_opportunities.get("opportunities", [])
        
        # Cachear resultados
        trends_cache[cache_key] = analysis_results
        
        return analysis_results
    
    def _get_default_keywords(self, industry: str) -> List[str]:
        """Obtiene keywords por defecto para una industria."""
        industry_keywords = {
            "tech": ["technology", "software", "AI", "cloud computing", "digital transformation"],
            "healthcare": ["healthcare", "telemedicine", "health tech", "medical devices"],
            "finance": ["fintech", "blockchain", "cryptocurrency", "digital banking"],
            "retail": ["e-commerce", "online shopping", "retail tech", "omnichannel"],
            "education": ["edtech", "online learning", "e-learning", "education technology"],
            "manufacturing": ["industry 4.0", "smart manufacturing", "IoT", "automation"],
        }
        
        industry_lower = industry.lower()
        for key, keywords in industry_keywords.items():
            if key in industry_lower:
                return keywords
        
        # Keywords genéricos
        return [industry, f"{industry} trends", f"{industry} market"]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @market_api_breaker
    def _analyze_search_trends(
        self,
        industry: str,
        keywords: List[str],
        timeframe_months: int
    ) -> List[MarketTrend]:
        """Analiza tendencias de búsqueda usando Google Trends."""
        trends = []
        
        try:
            # Simulación de análisis de Google Trends
            # En producción, usarías la API real de Google Trends
            for keyword in keywords:
                # Simular datos de tendencia
                current_value = np.random.uniform(50, 100)
                previous_value = np.random.uniform(40, 90)
                change = ((current_value - previous_value) / previous_value) * 100
                
                trend = MarketTrend(
                    trend_name=f"Search Trend: {keyword}",
                    category="search_volume",
                    current_value=current_value,
                    previous_value=previous_value,
                    change_percentage=change,
                    trend_direction="up" if change > 5 else "down" if change < -5 else "stable",
                    confidence=0.85,
                    timeframe=f"{timeframe_months} months",
                    source="google_trends",
                    metadata={"keyword": keyword, "industry": industry}
                )
                trends.append(trend)
                
        except Exception as e:
            logger.error(f"Error analyzing search trends: {e}")
        
        return trends
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @market_api_breaker
    def _analyze_news_trends(
        self,
        industry: str,
        timeframe_months: int
    ) -> List[MarketTrend]:
        """Analiza tendencias basadas en noticias."""
        trends = []
        
        try:
            if not self.news_api_key:
                logger.warning("News API key not configured, skipping news analysis")
                return trends
            
            # En producción, usarías News API o similar
            # Por ahora, simulamos el análisis
            news_volume = np.random.uniform(100, 500)
            sentiment_score = np.random.uniform(-0.5, 0.8)
            
            trend = MarketTrend(
                trend_name=f"News Coverage: {industry}",
                category="news_volume",
                current_value=news_volume,
                previous_value=news_volume * 0.9,
                change_percentage=10.0,
                trend_direction="up" if sentiment_score > 0 else "down",
                confidence=0.75,
                timeframe=f"{timeframe_months} months",
                source="news_api",
                metadata={
                    "industry": industry,
                    "sentiment_score": sentiment_score,
                    "article_count": int(news_volume)
                }
            )
            trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error analyzing news trends: {e}")
        
        return trends
    
    def _analyze_sentiment(
        self,
        industry: str,
        keywords: List[str],
        timeframe_months: int
    ) -> List[MarketTrend]:
        """Analiza sentimiento en redes sociales y medios."""
        trends = []
        
        try:
            # Análisis de sentimiento simulado
            # En producción, usarías APIs de Twitter, Reddit, etc.
            overall_sentiment = np.random.uniform(-0.3, 0.7)
            
            trend = MarketTrend(
                trend_name=f"Social Sentiment: {industry}",
                category="sentiment",
                current_value=overall_sentiment * 100,
                previous_value=(overall_sentiment - 0.1) * 100,
                change_percentage=10.0,
                trend_direction="up" if overall_sentiment > 0 else "down",
                confidence=0.70,
                timeframe=f"{timeframe_months} months",
                source="social_media",
                metadata={
                    "industry": industry,
                    "sentiment_score": overall_sentiment,
                    "keywords_analyzed": keywords
                }
            )
            trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
        
        return trends
    
    def _analyze_competitors(self, industry: str) -> List[MarketTrend]:
        """Analiza actividad y tendencias de competidores."""
        trends = []
        
        try:
            # Análisis de competidores simulado
            competitor_activity = np.random.uniform(60, 100)
            
            trend = MarketTrend(
                trend_name=f"Competitor Activity: {industry}",
                category="competition",
                current_value=competitor_activity,
                previous_value=competitor_activity * 0.95,
                change_percentage=5.0,
                trend_direction="up",
                confidence=0.80,
                timeframe="3 months",
                source="competitor_analysis",
                metadata={
                    "industry": industry,
                    "activity_score": competitor_activity
                }
            )
            trends.append(trend)
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
        
        return trends
    
    def _generate_actionable_insights(
        self,
        trends: List[MarketTrend]
    ) -> List[Dict[str, Any]]:
        """Genera insights accionables basados en las tendencias."""
        insights = []
        
        # Agrupar tendencias por categoría
        trends_by_category = defaultdict(list)
        for trend in trends:
            trends_by_category[trend.category].append(trend)
        
        # Generar insights por categoría
        for category, category_trends in trends_by_category.items():
            avg_change = np.mean([t.change_percentage for t in category_trends])
            avg_confidence = np.mean([t.confidence for t in category_trends])
            
            if abs(avg_change) > 10:  # Cambio significativo
                insight = {
                    "category": category,
                    "trend_direction": "up" if avg_change > 0 else "down",
                    "magnitude": abs(avg_change),
                    "confidence": avg_confidence,
                    "description": self._generate_insight_description(category, avg_change),
                    "actionable_steps": self._generate_actionable_steps(category, avg_change)
                }
                insights.append(insight)
        
        return insights
    
    def _generate_insight_description(self, category: str, change: float) -> str:
        """Genera descripción de insight basada en categoría y cambio."""
        descriptions = {
            "search_volume": f"El volumen de búsqueda ha {'aumentado' if change > 0 else 'disminuido'} un {abs(change):.1f}%",
            "news_volume": f"La cobertura de noticias ha {'aumentado' if change > 0 else 'disminuido'} un {abs(change):.1f}%",
            "sentiment": f"El sentimiento del mercado ha {'mejorado' if change > 0 else 'empeorado'} un {abs(change):.1f}%",
            "competition": f"La actividad de competidores ha {'aumentado' if change > 0 else 'disminuido'} un {abs(change):.1f}%"
        }
        return descriptions.get(category, f"Cambio del {abs(change):.1f}% en {category}")
    
    def _generate_actionable_steps(self, category: str, change: float) -> List[str]:
        """Genera pasos accionables basados en categoría y cambio."""
        if change > 0:
            steps = {
                "search_volume": [
                    "Aumentar inversión en SEO y contenido relacionado",
                    "Crear campañas de marketing dirigidas a estas búsquedas",
                    "Optimizar landing pages para keywords de tendencia"
                ],
                "news_volume": [
                    "Aprovechar el momentum mediático con PR estratégico",
                    "Participar en conversaciones de la industria",
                    "Crear contenido que responda a las noticias actuales"
                ],
                "sentiment": [
                    "Reforzar mensajes positivos en marketing",
                    "Amplificar testimonios y casos de éxito",
                    "Aumentar presencia en canales con sentimiento positivo"
                ],
                "competition": [
                    "Acelerar diferenciación de producto",
                    "Fortalecer propuesta de valor única",
                    "Aumentar inversión en innovación"
                ]
            }
        else:
            steps = {
                "search_volume": [
                    "Diversificar estrategia de marketing",
                    "Explorar nuevos canales y keywords",
                    "Revisar estrategia de contenido"
                ],
                "news_volume": [
                    "Generar contenido propio para mantener visibilidad",
                    "Buscar oportunidades de thought leadership",
                    "Explorar nichos menos saturados"
                ],
                "sentiment": [
                    "Identificar y abordar causas del sentimiento negativo",
                    "Mejorar comunicación y transparencia",
                    "Reforzar relaciones con clientes existentes"
                ],
                "competition": [
                    "Aprovechar menor competencia para ganar market share",
                    "Fortalecer posición en mercado",
                    "Invertir en retención de clientes"
                ]
            }
        
        return steps.get(category, ["Monitorear tendencia", "Ajustar estrategia según evolución"])
    
    def _generate_recommendations(
        self,
        trends: List[MarketTrend],
        insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones estratégicas."""
        recommendations = []
        
        # Analizar patrones en las tendencias
        upward_trends = [t for t in trends if t.trend_direction == "up" and t.change_percentage > 10]
        downward_trends = [t for t in trends if t.trend_direction == "down" and abs(t.change_percentage) > 10]
        
        if len(upward_trends) > len(downward_trends):
            recommendations.append({
                "type": "growth_opportunity",
                "priority": "high",
                "title": "Momentum de Crecimiento Detectado",
                "description": "Múltiples indicadores muestran tendencia positiva",
                "actions": [
                    "Aumentar inversión en áreas de crecimiento",
                    "Escalar operaciones para capitalizar momentum",
                    "Acelerar lanzamiento de productos/servicios relacionados"
                ]
            })
        
        if len(downward_trends) > 2:
            recommendations.append({
                "type": "risk_mitigation",
                "priority": "high",
                "title": "Señales de Riesgo Detectadas",
                "description": "Varias tendencias muestran declive",
                "actions": [
                    "Revisar estrategia actual",
                    "Diversificar fuentes de crecimiento",
                    "Fortalecer fundamentos del negocio"
                ]
            })
        
        return recommendations
    
    def _identify_risks_opportunities(
        self,
        trends: List[MarketTrend]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Identifica riesgos y oportunidades."""
        risks = []
        opportunities = []
        
        for trend in trends:
            if trend.change_percentage > 15 and trend.confidence > 0.7:
                opportunities.append({
                    "title": f"Oportunidad: {trend.trend_name}",
                    "description": f"Tendencia fuerte al alza ({trend.change_percentage:.1f}%)",
                    "category": trend.category,
                    "confidence": trend.confidence,
                    "action": f"Capitalizar tendencia en {trend.category}"
                })
            
            if trend.change_percentage < -15 and trend.confidence > 0.7:
                risks.append({
                    "title": f"Riesgo: {trend.trend_name}",
                    "description": f"Tendencia fuerte a la baja ({abs(trend.change_percentage):.1f}%)",
                    "category": trend.category,
                    "confidence": trend.confidence,
                    "action": f"Mitigar riesgo en {trend.category}"
                })
        
        return {"risks": risks, "opportunities": opportunities}
    
    def save_analysis_to_db(
        self,
        analysis: Dict[str, Any],
        table_name: str = "market_trends_analysis"
    ) -> bool:
        """Guarda análisis en base de datos."""
        if not self.postgres_conn_id:
            logger.warning("PostgreSQL connection not configured, skipping DB save")
            return False
        
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    industry VARCHAR(255),
                    analysis_date TIMESTAMP,
                    analysis_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insertar análisis
            cursor.execute(f"""
                INSERT INTO {table_name} (industry, analysis_date, analysis_data)
                VALUES (%s, %s, %s)
            """, (
                analysis["industry"],
                analysis["analysis_date"],
                json.dumps(analysis)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Analysis saved to database for industry: {analysis['industry']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving analysis to database: {e}")
            return False
    
    def get_historical_trends(
        self,
        industry: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias históricas desde la base de datos."""
        if not self.postgres_conn_id:
            return []
        
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT analysis_data, analysis_date
                FROM market_trends_analysis
                WHERE industry = %s
                AND analysis_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY analysis_date DESC
            """, (industry, days))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "data": row[0],
                    "date": row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1])
                })
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching historical trends: {e}")
            return []






