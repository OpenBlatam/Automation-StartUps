#!/usr/bin/env python3
"""
Script de prueba para el webhook de captura de leads
=====================================================

Ejemplo de uso:
    python scripts/test_lead_webhook.py
"""

import requests
import json
import hmac
import hashlib
import os
import sys

# Configuración
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5000/webhook/lead")
SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "")


def calculate_signature(payload: str, secret: str) -> str:
    """Calcula firma HMAC para el payload"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def send_lead(lead_data: dict, use_signature: bool = True) -> dict:
    """Envía un lead al webhook"""
    payload = json.dumps(lead_data)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Agregar firma si hay secret key
    if use_signature and SECRET_KEY:
        signature = calculate_signature(payload, SECRET_KEY)
        headers["X-Webhook-Signature"] = signature
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            headers=headers,
            data=payload,
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error enviando lead: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Response: {e.response.text}")
            except:
                pass
        raise


def main():
    """Función principal"""
    print("=" * 60)
    print("Test de Webhook de Captura de Leads")
    print("=" * 60)
    print()
    
    # Ejemplo 1: Lead básico
    print("1. Enviando lead básico...")
    lead1 = {
        "email": "test@example.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "phone": "+34612345678",
        "source": "web"
    }
    
    try:
        result1 = send_lead(lead1)
        print(f"✅ Lead enviado: {result1}")
        print(f"   DAG Run ID: {result1.get('dag_run_id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print()
    
    # Ejemplo 2: Lead completo con UTM
    print("2. Enviando lead completo con UTM tracking...")
    lead2 = {
        "email": "cliente@empresa.com",
        "first_name": "María",
        "last_name": "García",
        "phone": "+34687654321",
        "company": "Mi Empresa SL",
        "source": "web",
        "message": "Interesado en conocer más sobre el producto",
        "utm_source": "google",
        "utm_campaign": "summer_2024",
        "utm_medium": "cpc",
        "landing_page": "https://example.com/landing",
        "metadata": {
            "custom_field": "valor_personalizado"
        }
    }
    
    try:
        result2 = send_lead(lead2)
        print(f"✅ Lead enviado: {result2}")
        print(f"   Lead Email: {result2.get('lead_email', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print()
    
    # Ejemplo 3: Lead con full_name (sin first_name/last_name)
    print("3. Enviando lead con full_name...")
    lead3 = {
        "email": "otro@example.com",
        "full_name": "Pedro Sánchez",
        "phone": "+34611111111",
        "source": "referral"
    }
    
    try:
        result3 = send_lead(lead3)
        print(f"✅ Lead enviado: {result3}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print()
    print("=" * 60)
    print("✅ Todos los tests completados exitosamente")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

