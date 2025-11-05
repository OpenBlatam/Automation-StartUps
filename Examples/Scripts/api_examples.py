"""
Ejemplos de uso de la API del Sistema de Inventario
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def example_create_product():
    """Ejemplo: Crear un producto"""
    product_data = {
        "name": "Producto Ejemplo",
        "sku": "PROD-EX-001",
        "description": "Descripción del producto de ejemplo",
        "category": "Electrónica",
        "unit_price": 150.00,
        "cost_price": 100.00,
        "min_stock_level": 50,
        "max_stock_level": 500,
        "reorder_point": 100
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=product_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def example_get_products():
    """Ejemplo: Obtener todos los productos"""
    response = requests.get(f"{BASE_URL}/products")
    
    print(f"Status: {response.status_code}")
    products = response.json()
    print(f"Productos encontrados: {len(products)}")
    
    for product in products[:5]:  # Mostrar primeros 5
        print(f"  - {product['name']} (SKU: {product['sku']}) - Stock: {product.get('current_stock', 'N/A')}")
    
    return products

def example_record_inventory_movement():
    """Ejemplo: Registrar movimiento de inventario"""
    movement_data = {
        "product_id": 1,
        "quantity": 100,
        "movement_type": "in",
        "reference": "PEDIDO-001",
        "notes": "Entrada de inventario inicial"
    }
    
    response = requests.post(
        f"{BASE_URL}/inventory/movements",
        json=movement_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def example_record_sale():
    """Ejemplo: Registrar una venta"""
    sale_data = {
        "product_id": 1,
        "quantity_sold": 5,
        "unit_price": 150.00,
        "sale_date": "2024-01-15T10:30:00"
    }
    
    response = requests.post(
        f"{BASE_URL}/sales",
        json=sale_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def example_get_alerts():
    """Ejemplo: Obtener alertas activas"""
    response = requests.get(f"{BASE_URL}/alerts")
    
    print(f"Status: {response.status_code}")
    alerts = response.json()
    print(f"Alertas encontradas: {len(alerts)}")
    
    for alert in alerts:
        print(f"  - {alert['message']} (Severidad: {alert['severity']})")
    
    return alerts

def example_get_forecast():
    """Ejemplo: Obtener predicción de demanda"""
    product_id = 1
    days = 30
    
    response = requests.get(
        f"{BASE_URL}/forecasts/{product_id}",
        params={"days": days}
    )
    
    print(f"Status: {response.status_code}")
    forecast = response.json()
    print(f"Predicción para {days} días:")
    print(f"  - Demanda esperada: {forecast.get('predicted_demand', 'N/A')}")
    print(f"  - Algoritmo usado: {forecast.get('algorithm', 'N/A')}")
    
    return forecast

def example_get_replenishment_recommendations():
    """Ejemplo: Obtener recomendaciones de reposición"""
    response = requests.get(f"{BASE_URL}/replenishment/recommendations")
    
    print(f"Status: {response.status_code}")
    recommendations = response.json()
    print(f"Recomendaciones encontradas: {len(recommendations)}")
    
    for rec in recommendations[:5]:
        print(f"  - {rec.get('product_name', 'N/A')}: {rec.get('recommended_quantity', 0)} unidades")
    
    return recommendations

def example_get_kpis():
    """Ejemplo: Obtener KPIs del sistema"""
    response = requests.get(f"{BASE_URL}/kpis")
    
    print(f"Status: {response.status_code}")
    kpis = response.json()
    
    print("KPIs del Sistema:")
    if 'inventory' in kpis:
        print(f"  Inventario:")
        print(f"    - Total de productos: {kpis['inventory'].get('total_products', 'N/A')}")
        print(f"    - Valor total: ${kpis['inventory'].get('total_value', 0):,.2f}")
    
    if 'sales' in kpis:
        print(f"  Ventas:")
        print(f"    - Ingresos totales: ${kpis['sales'].get('total_revenue', 0):,.2f}")
    
    return kpis

if __name__ == '__main__':
    print("=" * 60)
    print("EJEMPLOS DE USO DE LA API")
    print("=" * 60)
    print()
    
    print("Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    print()
    
    # Descomentar las funciones que quieras probar
    # example_create_product()
    # example_get_products()
    # example_record_inventory_movement()
    # example_record_sale()
    # example_get_alerts()
    # example_get_forecast()
    # example_get_replenishment_recommendations()
    # example_get_kpis()
    
    print("\nPara usar estos ejemplos, descomenta las llamadas en el archivo.")

