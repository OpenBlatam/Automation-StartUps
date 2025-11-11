"""
Ejemplo de uso del sistema de upsells complementarios

Este script muestra cómo usar la API de upsells para:
1. Registrar una compra de producto
2. Obtener upsells complementarios sugeridos
3. Agregar un upsell con 1-click add-on
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:5000"

def ejemplo_upsells():
    """Ejemplo completo de uso de upsells"""
    
    print("=" * 70)
    print("EJEMPLO DE USO: SISTEMA DE UPSELLS COMPLEMENTARIOS")
    print("=" * 70)
    
    # 1. Registrar compra del Producto A
    print("\n1. Registrando compra del Producto A...")
    purchase_data = {
        "product_id": "prod_001",
        "customer_id": "customer_123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/purchases",
        json=purchase_data
    )
    
    if response.status_code == 201:
        result = response.json()
        print("✓ Compra registrada exitosamente")
        print(f"  Producto: {result['product_id']}")
        print(f"  Upsells sugeridos: {result['count']}")
        
        # Mostrar upsells sugeridos
        print("\n2. Upsells complementarios sugeridos:")
        print("-" * 70)
        for i, upsell in enumerate(result['upsells'], 1):
            print(f"\n  Upsell {i}:")
            print(f"    Producto: {upsell['upsell_product']['name']}")
            print(f"    Precio bundle: ${upsell['bundle_price']:.0f} MXN")
            print(f"    Precio original: ${upsell['original_price']:.0f} MXN")
            print(f"    Ahorro: ${upsell['savings']:.0f} MXN")
            print(f"    Razón emocional: {upsell['emotional_reason']}")
            print(f"    Mensaje: {upsell['display_message']}")
        
        # 3. Agregar un upsell con 1-click add-on
        if result['upsells']:
            print("\n3. Agregando upsell con 1-click add-on...")
            first_upsell = result['upsells'][0]
            upsell_product_id = first_upsell['upsell_product']['id']
            
            add_upsell_data = {
                "upsell_product_id": upsell_product_id,
                "customer_id": "customer_123"
            }
            
            add_response = requests.post(
                f"{BASE_URL}/api/purchases/{purchase_data['product_id']}/add-upsell",
                json=add_upsell_data
            )
            
            if add_response.status_code == 200:
                add_result = add_response.json()
                print("✓ Upsell agregado exitosamente")
                print(f"  Mensaje: {add_result['message']}")
                print(f"  Producto agregado: {add_result['upsell']['upsell_product']['name']}")
            else:
                print(f"✗ Error al agregar upsell: {add_response.json()}")
    else:
        print(f"✗ Error al registrar compra: {response.json()}")
    
    # 4. Obtener upsells directamente (sin registrar compra)
    print("\n4. Obteniendo upsells directamente para Producto A...")
    response = requests.get(f"{BASE_URL}/api/upsells/prod_001?limit=2")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Se encontraron {result['count']} upsells")
        for upsell in result['upsells']:
            print(f"  - {upsell['display_message']}")
    
    print("\n" + "=" * 70)
    print("EJEMPLO COMPLETADO")
    print("=" * 70)


def ejemplo_respuesta_api():
    """Muestra un ejemplo de respuesta de la API"""
    
    print("\n" + "=" * 70)
    print("EJEMPLO DE RESPUESTA DE LA API")
    print("=" * 70)
    
    ejemplo_respuesta = {
        "success": True,
        "product_id": "prod_001",
        "upsells": [
            {
                "id": "upsell_001",
                "upsell_product": {
                    "id": "prod_002",
                    "name": "Cargador Rápido",
                    "description": "Cargador rápido de alta velocidad",
                    "category": "Accesorios"
                },
                "bundle_price": 199.0,
                "original_price": 399.0,
                "savings": 200.0,
                "emotional_reason": "Clientes que compraron esto también se llevaron el cargador rápido para máxima compatibilidad",
                "display_message": "¡Agrega cargador rápido por solo +$199 MXN (valor $399 MXN)!"
            },
            {
                "id": "upsell_002",
                "upsell_product": {
                    "id": "prod_003",
                    "name": "Funda Protectora",
                    "description": "Funda resistente y elegante",
                    "category": "Accesorios"
                },
                "bundle_price": 249.0,
                "original_price": 299.0,
                "savings": 50.0,
                "emotional_reason": "Clientes que compraron esto también se llevaron la funda protectora para mantener su producto seguro",
                "display_message": "¡Agrega funda protectora por solo +$249 MXN (valor $299 MXN)!"
            }
        ],
        "count": 2
    }
    
    print(json.dumps(ejemplo_respuesta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Mostrar ejemplo de respuesta
    ejemplo_respuesta_api()
    
    # Ejecutar ejemplo (requiere servidor corriendo)
    # ejemplo_upsells()

