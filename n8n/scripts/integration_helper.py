#!/usr/bin/env python3
"""
Helper script para integración de workflows de automatización de clientes
Proporciona funciones útiles para conectar con APIs externas
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

class CustomerAutomationHelper:
    """Helper class para integraciones de automatización"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def trigger_cart_abandonment(self, customer_data: Dict) -> Dict:
        """Activa workflow de carrito abandonado"""
        webhook_url = f"{self.api_base_url}/webhook/cart-abandonment"
        
        payload = {
            "eventType": "cart_abandonment",
            "customerId": customer_data.get("customer_id"),
            "email": customer_data.get("email"),
            "firstName": customer_data.get("first_name"),
            "lastName": customer_data.get("last_name"),
            "cartId": customer_data.get("cart_id"),
            "cartValue": float(customer_data.get("cart_value", 0)),
            "cartItems": [
                {
                    "name": item.get("name"),
                    "price": float(item.get("price", 0)),
                    "quantity": int(item.get("quantity", 1)),
                    "category": item.get("category", "general")
                }
                for item in customer_data.get("cart_items", [])
            ],
            "sessionId": customer_data.get("session_id"),
            "device": customer_data.get("device", "unknown"),
            "browser": customer_data.get("browser", "unknown"),
            "referrer": customer_data.get("referrer", "direct"),
            "utmSource": customer_data.get("utm_source"),
            "utmCampaign": customer_data.get("utm_campaign")
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        return response.json()
    
    def trigger_page_visit(self, customer_data: Dict, page_data: Dict) -> Dict:
        """Activa workflow de visita a página"""
        webhook_url = f"{self.api_base_url}/webhook/page-visit"
        
        payload = {
            "eventType": "page_visit",
            "customerId": customer_data.get("customer_id"),
            "email": customer_data.get("email"),
            "firstName": customer_data.get("first_name"),
            "pageUrl": page_data.get("url"),
            "pageCategory": page_data.get("category", "general"),
            "productName": page_data.get("product_name"),
            "sessionId": page_data.get("session_id"),
            "timeOnPage": page_data.get("time_on_page", 0),
            "pagesViewed": page_data.get("pages_viewed", 1)
        }
        
        response = requests.post(webhook_url, json=payload, headers=self.headers)
        return response.json()
    
    def get_customer_history(self, customer_id: str) -> Dict:
        """Obtiene historial del cliente desde CRM"""
        url = f"{self.api_base_url}/customers/{customer_id}/history"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_customer_preferences(self, customer_id: str) -> Dict:
        """Obtiene preferencias del cliente"""
        url = f"{self.api_base_url}/customers/{customer_id}/preferences"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def track_event(self, event_data: Dict) -> Dict:
        """Registra evento en sistema de tracking"""
        url = f"{self.api_base_url}/tracking"
        response = requests.post(url, json=event_data, headers=self.headers)
        return response.json()
    
    def get_inactive_customers(self, days_inactive: int = 90, limit: int = 100) -> List[Dict]:
        """Obtiene lista de clientes inactivos"""
        url = f"{self.api_base_url}/customers/inactive"
        params = {
            "daysInactive": days_inactive,
            "limit": limit
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json().get("customers", [])
    
    def calculate_conversion_score(self, customer_data: Dict) -> int:
        """Calcula score de conversión (0-100)"""
        score = 50  # Base
        
        cart_value = customer_data.get("cart_value", 0)
        if cart_value > 500:
            score += 30
        elif cart_value > 200:
            score += 25
        elif cart_value > 100:
            score += 20
        elif cart_value > 50:
            score += 10
        
        item_count = len(customer_data.get("cart_items", []))
        if item_count > 5:
            score += 15
        elif item_count > 2:
            score += 10
        
        previous_purchases = customer_data.get("previous_purchases", 0)
        if previous_purchases > 10:
            score += 20
        elif previous_purchases > 0:
            score += 15
        
        time_on_site = customer_data.get("time_on_site", 0)
        if time_on_site > 600:
            score += 15
        elif time_on_site > 300:
            score += 10
        
        pages_viewed = customer_data.get("pages_viewed", 0)
        if pages_viewed > 10:
            score += 10
        elif pages_viewed > 5:
            score += 5
        
        return min(100, max(0, score))
    
    def assign_ab_variant(self, customer_id: str) -> str:
        """Asigna variante A/B consistente basada en customerId"""
        hash_value = int(hashlib.md5(customer_id.encode()).hexdigest(), 16)
        return 'A' if hash_value % 2 == 0 else 'B'
    
    def generate_discount_code(self, customer_segment: str, variant: str) -> str:
        """Genera código de descuento según segmento y variante"""
        discounts = {
            'vip': {'A': 'VIP20', 'B': 'VIP25'},
            'premium': {'A': 'PREMIUM15', 'B': 'PREMIUM18'},
            'high_value': {'A': 'HIGH10', 'B': 'HIGH12'},
            'medium_value': {'A': 'MEDIUM10', 'B': 'MEDIUM12'},
            'low_value': {'A': 'SAVE10', 'B': 'SAVE12'}
        }
        
        segment = customer_segment.lower()
        if segment not in discounts:
            segment = 'low_value'
        
        return discounts[segment].get(variant, 'SAVE10')
    
    def calculate_optimal_timing(self, customer_data: Dict, 
                                 customer_history: Optional[Dict] = None) -> float:
        """Calcula timing óptimo en horas basado en historial"""
        base_delay = 1.0  # 1 hora por defecto
        
        conversion_score = self.calculate_conversion_score(customer_data)
        
        # Ajustar según score
        if conversion_score > 80:
            base_delay = 0.5
        elif conversion_score > 60:
            base_delay = 1.0
        elif conversion_score > 40:
            base_delay = 2.0
        else:
            base_delay = 4.0
        
        # Ajustar según historial si está disponible
        if customer_history:
            best_send_times = customer_history.get("best_send_times", [])
            if best_send_times:
                avg_hour = sum(t.get("hour", 10) for t in best_send_times) / len(best_send_times)
                current_hour = datetime.now().hour
                hours_until_optimal = (avg_hour - current_hour) % 24
                if hours_until_optimal > 0:
                    base_delay = max(base_delay, hours_until_optimal)
        
        return base_delay


def main():
    """Ejemplo de uso"""
    # Configuración
    api_url = os.getenv("API_BASE_URL", "https://api.yourdomain.com")
    api_key = os.getenv("API_KEY", "your_api_key_here")
    
    helper = CustomerAutomationHelper(api_url, api_key)
    
    # Ejemplo: Trigger carrito abandonado
    customer_data = {
        "customer_id": "customer_123",
        "email": "test@example.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "cart_id": "cart_456",
        "cart_value": 150.00,
        "cart_items": [
            {
                "name": "Producto A",
                "price": 75.00,
                "quantity": 2,
                "category": "electronics"
            }
        ],
        "session_id": "session_789",
        "device": "mobile",
        "browser": "chrome"
    }
    
    result = helper.trigger_cart_abandonment(customer_data)
    print(f"Workflow triggered: {result}")
    
    # Ejemplo: Calcular score
    score = helper.calculate_conversion_score(customer_data)
    print(f"Conversion Score: {score}")
    
    # Ejemplo: Asignar variante A/B
    variant = helper.assign_ab_variant(customer_data["customer_id"])
    print(f"AB Variant: {variant}")
    
    # Ejemplo: Generar código de descuento
    discount_code = helper.generate_discount_code("high_value", variant)
    print(f"Discount Code: {discount_code}")


if __name__ == "__main__":
    main()




