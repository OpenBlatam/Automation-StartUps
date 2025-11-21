"""
Análisis Geográfico Avanzado de Mercado

Análisis detallado por geografía:
- Análisis por países/regiones
- Análisis de mercado local
- Comparación geográfica
- Oportunidades geográficas
- Análisis de expansión geográfica
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeographicMarket:
    """Mercado geográfico."""
    region_id: str
    region_name: str
    region_type: str  # 'country', 'state', 'city', 'region'
    market_size: float
    growth_rate: float
    competition_level: str  # 'high', 'medium', 'low'
    opportunity_score: float  # 0-100
    key_indicators: Dict[str, Any]
    barriers: List[str]
    opportunities: List[str]


class GeographicMarketAnalyzer:
    """Analizador geográfico de mercado."""
    
    def __init__(self):
        """Inicializa el analizador."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_geographic_markets(
        self,
        industry: str,
        regions: List[str],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza mercados geográficos.
        
        Args:
            industry: Industria
            regions: Lista de regiones a analizar
            market_data: Datos de mercado
            
        Returns:
            Análisis geográfico
        """
        logger.info(f"Analyzing geographic markets for {industry}")
        
        geographic_markets = []
        
        for region in regions:
            market = self._analyze_single_region(region, industry, market_data)
            geographic_markets.append(market)
        
        # Comparación geográfica
        comparison = self._compare_regions(geographic_markets)
        
        # Oportunidades geográficas
        opportunities = self._identify_geographic_opportunities(geographic_markets)
        
        return {
            "industry": industry,
            "analysis_date": datetime.utcnow().isoformat(),
            "regions_analyzed": len(regions),
            "geographic_markets": [
                {
                    "region_id": m.region_id,
                    "region_name": m.region_name,
                    "region_type": m.region_type,
                    "market_size": m.market_size,
                    "growth_rate": m.growth_rate,
                    "competition_level": m.competition_level,
                    "opportunity_score": m.opportunity_score,
                    "key_indicators": m.key_indicators,
                    "barriers": m.barriers,
                    "opportunities": m.opportunities
                }
                for m in geographic_markets
            ],
            "geographic_comparison": comparison,
            "geographic_opportunities": opportunities
        }
    
    def _analyze_single_region(
        self,
        region: str,
        industry: str,
        market_data: Dict[str, Any]
    ) -> GeographicMarket:
        """Analiza una región individual."""
        # Simular análisis
        market_size = hash(f"{region}{industry}") % 1000000
        growth_rate = 5.0 + (hash(region) % 15)
        competition_level = ["high", "medium", "low"][hash(region) % 3]
        
        # Calcular opportunity score
        opportunity_score = self._calculate_opportunity_score(
            market_size,
            growth_rate,
            competition_level
        )
        
        key_indicators = {
            "gdp_growth": 2.5 + (hash(region) % 3),
            "population": market_size * 10,
            "tech_adoption": 0.6 + (hash(region) % 40) / 100
        }
        
        barriers = [
            f"Regulatory barriers in {region}",
            f"Language/cultural barriers in {region}"
        ] if competition_level == "high" else []
        
        opportunities = [
            f"Growing market in {region}",
            f"Low competition in {region}",
            f"High growth potential in {region}"
        ] if opportunity_score > 70 else []
        
        return GeographicMarket(
            region_id=f"geo_{region.lower().replace(' ', '_')}",
            region_name=region,
            region_type="country",
            market_size=market_size,
            growth_rate=growth_rate,
            competition_level=competition_level,
            opportunity_score=opportunity_score,
            key_indicators=key_indicators,
            barriers=barriers,
            opportunities=opportunities
        )
    
    def _calculate_opportunity_score(
        self,
        market_size: float,
        growth_rate: float,
        competition_level: str
    ) -> float:
        """Calcula score de oportunidad geográfica."""
        score = 0.0
        
        # Factor 1: Tamaño de mercado (0-40 puntos)
        if market_size > 500000:
            score += 40
        elif market_size > 200000:
            score += 30
        elif market_size > 100000:
            score += 20
        else:
            score += 10
        
        # Factor 2: Tasa de crecimiento (0-35 puntos)
        if growth_rate > 15:
            score += 35
        elif growth_rate > 10:
            score += 25
        elif growth_rate > 5:
            score += 15
        else:
            score += 5
        
        # Factor 3: Competencia (0-25 puntos) - menos competencia = más puntos
        if competition_level == "low":
            score += 25
        elif competition_level == "medium":
            score += 15
        else:
            score += 5
        
        return min(100.0, score)
    
    def _compare_regions(
        self,
        markets: List[GeographicMarket]
    ) -> Dict[str, Any]:
        """Compara regiones."""
        if not markets:
            return {}
        
        best_opportunity = max(markets, key=lambda m: m.opportunity_score)
        fastest_growth = max(markets, key=lambda m: m.growth_rate)
        largest_market = max(markets, key=lambda m: m.market_size)
        
        return {
            "best_opportunity_region": {
                "name": best_opportunity.region_name,
                "score": best_opportunity.opportunity_score
            },
            "fastest_growth_region": {
                "name": fastest_growth.region_name,
                "growth_rate": fastest_growth.growth_rate
            },
            "largest_market_region": {
                "name": largest_market.region_name,
                "size": largest_market.market_size
            }
        }
    
    def _identify_geographic_opportunities(
        self,
        markets: List[GeographicMarket]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades geográficas."""
        opportunities = []
        
        high_opportunity = [m for m in markets if m.opportunity_score > 70]
        
        for market in high_opportunity:
            opportunities.append({
                "region": market.region_name,
                "opportunity_score": market.opportunity_score,
                "market_size": market.market_size,
                "growth_rate": market.growth_rate,
                "recommendation": f"Consider expansion to {market.region_name} - high opportunity score"
            })
        
        return opportunities






