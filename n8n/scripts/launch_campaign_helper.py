#!/usr/bin/env python3
"""
Launch Campaign Helper
Script para automatizar la campaña de lanzamiento de producto
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class LaunchCampaignHelper:
    """
    Helper para automatizar campaña de lanzamiento de 3 días
    """
    
    def __init__(self, n8n_base_url: str, api_key: str):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def trigger_day_1_teaser(self, product_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara publicación del Día 1 (Teaser)
        
        Args:
            product_config: Configuración del producto
        
        Returns:
            Dict con resultado de la publicación
        """
        webhook_url = f"{self.n8n_base_url}/webhook/launch-campaign"
        
        payload = {
            "campaignDay": 1,
            "campaignType": "teaser",
            "productName": product_config.get("name", "[NOMBRE PRODUCTO]"),
            "productBenefits": product_config.get("benefits", []),
            "problem": product_config.get("problem", "[PROBLEMA ESPECÍFICO]"),
            "pain": product_config.get("pain", "[DOLOR ESPECÍFICO]"),
            "result": product_config.get("result", "[RESULTADO DESEADO]"),
            "area": product_config.get("area", "[ÁREA]"),
            "platforms": product_config.get("platforms", ["instagram", "facebook", "linkedin"]),
            "hashtags": product_config.get("hashtags", []),
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def trigger_day_2_demo(self, product_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara publicación del Día 2 (Demo)
        
        Args:
            product_config: Configuración del producto
        
        Returns:
            Dict con resultado de la publicación
        """
        webhook_url = f"{self.n8n_base_url}/webhook/launch-campaign"
        
        payload = {
            "campaignDay": 2,
            "campaignType": "demo",
            "productName": product_config.get("name", "[NOMBRE PRODUCTO]"),
            "productBenefits": product_config.get("benefits", []),
            "ctaLink": product_config.get("cta_link", "https://yoursite.com/launch"),
            "platforms": product_config.get("platforms", ["instagram", "facebook", "linkedin"]),
            "hashtags": product_config.get("hashtags", []),
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def trigger_day_3_offer(self, product_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara publicación del Día 3 (Oferta)
        
        Args:
            product_config: Configuración del producto
        
        Returns:
            Dict con resultado de la publicación
        """
        webhook_url = f"{self.n8n_base_url}/webhook/launch-campaign"
        
        payload = {
            "campaignDay": 3,
            "campaignType": "offer",
            "productName": product_config.get("name", "[NOMBRE PRODUCTO]"),
            "discountPercentage": product_config.get("discount_percentage", 20),
            "normalPrice": product_config.get("normal_price", 0),
            "specialPrice": product_config.get("special_price", 0),
            "bonuses": product_config.get("bonuses", []),
            "unitsAvailable": product_config.get("units_available", 100),
            "ctaLink": product_config.get("cta_link", "https://yoursite.com/launch"),
            "platforms": product_config.get("platforms", ["instagram", "facebook", "linkedin"]),
            "hashtags": product_config.get("hashtags", []),
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def track_social_engagement(
        self,
        platform: str,
        post_id: str,
        engagement_type: str,
        content: str = "",
        user_id: str = ""
    ) -> Dict[str, Any]:
        """
        Track engagement en redes sociales
        
        Args:
            platform: Plataforma (instagram, facebook, linkedin, etc.)
            post_id: ID del post
            engagement_type: Tipo (like, comment, share, follow, dm)
            content: Contenido del engagement (para comentarios)
            user_id: ID del usuario
        
        Returns:
            Dict con análisis del engagement
        """
        webhook_url = f"{self.n8n_base_url}/webhook/social-engagement"
        
        payload = {
            "platform": platform,
            "postId": post_id,
            "engagementType": engagement_type,
            "content": content,
            "userId": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def track_journey_event(
        self,
        customer_id: str,
        event_type: str,
        page_category: str = "",
        page_url: str = ""
    ) -> Dict[str, Any]:
        """
        Track evento en customer journey
        
        Args:
            customer_id: ID del cliente
            event_type: Tipo de evento
            page_category: Categoría de página
            page_url: URL de la página
        
        Returns:
            Dict con journey map actualizado
        """
        webhook_url = f"{self.n8n_base_url}/webhook/journey-event"
        
        payload = {
            "customerId": customer_id,
            "eventType": event_type,
            "pageCategory": page_category,
            "pageUrl": page_url,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_campaign_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de la campaña
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Dict con métricas de la campaña
        """
        # En producción, esto consultaría una API de analytics
        # Por ahora, retorna estructura de ejemplo
        return {
            "totalReach": 0,
            "totalEngagements": 0,
            "totalLeads": 0,
            "totalConversions": 0,
            "conversionRate": 0.0,
            "roi": 0.0,
            "platforms": {
                "instagram": {"reach": 0, "engagements": 0},
                "facebook": {"reach": 0, "engagements": 0},
                "linkedin": {"reach": 0, "engagements": 0}
            },
            "byDay": {
                "day1": {"reach": 0, "engagements": 0, "leads": 0},
                "day2": {"reach": 0, "engagements": 0, "leads": 0},
                "day3": {"reach": 0, "engagements": 0, "leads": 0, "conversions": 0}
            }
        }


def main():
    """Ejemplo de uso"""
    helper = LaunchCampaignHelper(
        n8n_base_url="https://your-n8n.com",
        api_key="your_api_key"
    )
    
    # Configuración del producto
    product_config = {
        "name": "Mi Nuevo Producto",
        "benefits": [
            "Ahorra 10 horas semanales",
            "Aumenta productividad en 300%",
            "Fácil de usar, sin curva de aprendizaje"
        ],
        "problem": "Gestión de tareas complicada",
        "pain": "Pérdida de tiempo en tareas repetitivas",
        "result": "Automatización completa",
        "area": "productividad",
        "discount_percentage": 25,
        "normal_price": 199,
        "special_price": 149,
        "bonuses": ["Bonus 1", "Bonus 2"],
        "units_available": 50,
        "cta_link": "https://yoursite.com/launch",
        "platforms": ["instagram", "facebook", "linkedin"],
        "hashtags": ["#Productividad", "#Automatización", "#NuevoProducto"]
    }
    
    # Disparar Día 1
    print("Disparando Día 1: Teaser...")
    result = helper.trigger_day_1_teaser(product_config)
    print(f"Resultado: {json.dumps(result, indent=2)}")
    
    # Track engagement
    print("\nTracking engagement...")
    engagement = helper.track_social_engagement(
        platform="instagram",
        post_id="post_123",
        engagement_type="comment",
        content="SÍ, quiero ser de los primeros",
        user_id="user_456"
    )
    print(f"Engagement: {json.dumps(engagement, indent=2)}")


if __name__ == "__main__":
    main()




