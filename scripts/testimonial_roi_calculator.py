#!/usr/bin/env python3
"""
Calculadora de ROI para Testimonios
Calcula el retorno de inversión y valor potencial de publicaciones
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ROICalculation:
    """Cálculo de ROI"""
    estimated_reach: int
    estimated_engagement: int
    estimated_clicks: int
    estimated_conversions: int
    estimated_revenue: float
    cost_per_post: float
    roi_percentage: float
    roi_multiplier: float
    payback_period_days: float


class ROICalculator:
    """Calculadora de ROI para testimonios"""
    
    # Tasas de conversión promedio por plataforma
    CONVERSION_RATES = {
        'linkedin': 0.02,  # 2%
        'instagram': 0.015,  # 1.5%
        'facebook': 0.01,   # 1%
        'twitter': 0.008,   # 0.8%
        'tiktok': 0.012     # 1.2%
    }
    
    # Costo promedio por post (tiempo + recursos)
    COST_PER_POST = {
        'linkedin': 50.0,
        'instagram': 40.0,
        'facebook': 35.0,
        'twitter': 30.0,
        'tiktok': 45.0
    }
    
    # Valor promedio por lead/conversión
    VALUE_PER_CONVERSION = 100.0  # Valor promedio por conversión
    
    def __init__(
        self,
        conversion_rates: Optional[Dict[str, float]] = None,
        cost_per_post: Optional[Dict[str, float]] = None,
        value_per_conversion: float = 100.0
    ):
        """
        Inicializa la calculadora de ROI
        
        Args:
            conversion_rates: Tasas de conversión por plataforma
            cost_per_post: Costo por post por plataforma
            value_per_conversion: Valor promedio por conversión
        """
        if conversion_rates:
            self.CONVERSION_RATES.update(conversion_rates)
        if cost_per_post:
            self.COST_PER_POST.update(cost_per_post)
        self.VALUE_PER_CONVERSION = value_per_conversion
    
    def calculate_roi(
        self,
        predicted_engagement_rate: float,
        estimated_reach: int,
        platform: str,
        cost_override: Optional[float] = None
    ) -> ROICalculation:
        """
        Calcula el ROI de una publicación
        
        Args:
            predicted_engagement_rate: Tasa de engagement predicha (%)
            estimated_reach: Alcance estimado
            platform: Plataforma objetivo
            cost_override: Costo personalizado (opcional)
        
        Returns:
            ROICalculation con todos los cálculos
        """
        # Calcular engagement estimado
        estimated_engagement = int(estimated_reach * (predicted_engagement_rate / 100))
        
        # Calcular clicks estimados (asumiendo que 30% del engagement son clicks)
        click_rate = 0.30
        estimated_clicks = int(estimated_engagement * click_rate)
        
        # Calcular conversiones estimadas
        conversion_rate = self.CONVERSION_RATES.get(platform.lower(), 0.01)
        estimated_conversions = int(estimated_clicks * conversion_rate)
        
        # Calcular ingresos estimados
        estimated_revenue = estimated_conversions * self.VALUE_PER_CONVERSION
        
        # Calcular costo
        cost = cost_override or self.COST_PER_POST.get(platform.lower(), 50.0)
        
        # Calcular ROI
        roi_amount = estimated_revenue - cost
        roi_percentage = (roi_amount / cost * 100) if cost > 0 else 0
        roi_multiplier = estimated_revenue / cost if cost > 0 else 0
        
        # Calcular período de recuperación (días)
        # Asumiendo que el engagement se distribuye en 7 días
        daily_revenue = estimated_revenue / 7
        payback_period_days = cost / daily_revenue if daily_revenue > 0 else 0
        
        return ROICalculation(
            estimated_reach=estimated_reach,
            estimated_engagement=estimated_engagement,
            estimated_clicks=estimated_clicks,
            estimated_conversions=estimated_conversions,
            estimated_revenue=round(estimated_revenue, 2),
            cost_per_post=cost,
            roi_percentage=round(roi_percentage, 2),
            roi_multiplier=round(roi_multiplier, 2),
            payback_period_days=round(payback_period_days, 2)
        )
    
    def calculate_campaign_roi(
        self,
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula el ROI de una campaña completa
        
        Args:
            posts: Lista de publicaciones con predicciones
        
        Returns:
            Dict con ROI agregado de la campaña
        """
        total_cost = 0
        total_revenue = 0
        total_reach = 0
        total_engagement = 0
        total_conversions = 0
        
        platform_breakdown = {}
        
        for post in posts:
            platform = post.get('platform', 'linkedin')
            pred = post.get('engagement_prediction', {})
            engagement_rate = pred.get('predicted_engagement_rate', 0)
            estimated_reach = post.get('estimated_reach', 1000)
            
            roi = self.calculate_roi(
                predicted_engagement_rate=engagement_rate,
                estimated_reach=estimated_reach,
                platform=platform
            )
            
            total_cost += roi.cost_per_post
            total_revenue += roi.estimated_revenue
            total_reach += roi.estimated_reach
            total_engagement += roi.estimated_engagement
            total_conversions += roi.estimated_conversions
            
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    'posts': 0,
                    'cost': 0,
                    'revenue': 0,
                    'roi': 0
                }
            
            platform_breakdown[platform]['posts'] += 1
            platform_breakdown[platform]['cost'] += roi.cost_per_post
            platform_breakdown[platform]['revenue'] += roi.estimated_revenue
            platform_breakdown[platform]['roi'] += roi.roi_amount
        
        campaign_roi_percentage = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        campaign_roi_multiplier = total_revenue / total_cost if total_cost > 0 else 0
        
        return {
            'total_posts': len(posts),
            'total_cost': round(total_cost, 2),
            'total_revenue': round(total_revenue, 2),
            'total_roi': round(total_revenue - total_cost, 2),
            'roi_percentage': round(campaign_roi_percentage, 2),
            'roi_multiplier': round(campaign_roi_multiplier, 2),
            'total_reach': total_reach,
            'total_engagement': total_engagement,
            'total_conversions': total_conversions,
            'average_cost_per_post': round(total_cost / len(posts), 2) if posts else 0,
            'average_revenue_per_post': round(total_revenue / len(posts), 2) if posts else 0,
            'platform_breakdown': {
                platform: {
                    **data,
                    'roi_percentage': round((data['revenue'] - data['cost']) / data['cost'] * 100, 2) if data['cost'] > 0 else 0
                }
                for platform, data in platform_breakdown.items()
            }
        }
    
    def optimize_for_roi(
        self,
        platforms: List[str],
        budget: float,
        target_roi: float = 2.0
    ) -> Dict[str, Any]:
        """
        Optimiza distribución de presupuesto para máximo ROI
        
        Args:
            platforms: Plataformas disponibles
            budget: Presupuesto total
            target_roi: ROI objetivo (múltiplo)
        
        Returns:
            Dict con distribución optimizada
        """
        # Calcular ROI esperado por plataforma
        platform_roi = {}
        for platform in platforms:
            cost = self.COST_PER_POST.get(platform.lower(), 50.0)
            # Estimación conservadora de engagement
            avg_engagement_rate = 3.0
            avg_reach = 2000
            
            roi = self.calculate_roi(
                predicted_engagement_rate=avg_engagement_rate,
                estimated_reach=avg_reach,
                platform=platform
            )
            
            platform_roi[platform] = {
                'cost_per_post': cost,
                'expected_roi_multiplier': roi.roi_multiplier,
                'posts_affordable': int(budget / cost)
            }
        
        # Ordenar por ROI esperado
        sorted_platforms = sorted(
            platform_roi.items(),
            key=lambda x: x[1]['expected_roi_multiplier'],
            reverse=True
        )
        
        # Distribuir presupuesto
        allocation = {}
        remaining_budget = budget
        
        for platform, data in sorted_platforms:
            if remaining_budget <= 0:
                break
            
            cost = data['cost_per_post']
            posts = min(int(remaining_budget / cost), data['posts_affordable'])
            
            if posts > 0:
                allocation[platform] = {
                    'posts': posts,
                    'budget': posts * cost,
                    'expected_roi_multiplier': data['expected_roi_multiplier']
                }
                remaining_budget -= posts * cost
        
        total_allocated = sum(a['budget'] for a in allocation.values())
        total_posts = sum(a['posts'] for a in allocation.values())
        
        return {
            'total_budget': budget,
            'allocated_budget': round(total_allocated, 2),
            'remaining_budget': round(remaining_budget, 2),
            'total_posts': total_posts,
            'allocation': allocation,
            'expected_roi': round(
                sum(a['budget'] * a['expected_roi_multiplier'] for a in allocation.values()),
                2
            )
        }


