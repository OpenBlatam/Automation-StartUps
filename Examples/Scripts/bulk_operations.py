"""
Ejemplos de operaciones masivas en el sistema
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def bulk_create_products(products_data: list):
    """Crear múltiples productos de una vez"""
    results = []
    
    for product in products_data:
        response = requests.post(
            f"{BASE_URL}/products",
            json=product,
            headers={"Content-Type": "application/json"}
        )
        results.append({
            'product': product['name'],
            'status': response.status_code,
            'response': response.json()
        })
    
    return results

def bulk_record_movements(movements: list):
    """Registrar múltiples movimientos de inventario"""
    results = []
    
    for movement in movements:
        response = requests.post(
            f"{BASE_URL}/inventory/movements",
            json=movement
        )
        results.append({
            'movement': movement,
            'status': response.status_code,
            'response': response.json()
        })
    
    return results

def generate_sample_data():
    """Genera datos de ejemplo para testing"""
    
    # Productos de ejemplo
    products = [
        {
            "name": f"Producto {i}",
            "sku": f"PROD-{i:03d}",
            "description": f"Descripción del producto {i}",
            "category": "Categoría A" if i % 2 == 0 else "Categoría B",
            "unit_price": 50.0 + (i * 10),
            "cost_price": 30.0 + (i * 5),
            "min_stock_level": 20,
            "max_stock_level": 200,
            "reorder_point": 50
        }
        for i in range(1, 11)  # 10 productos
    ]
    
    # Movimientos de inventario de ejemplo
    movements = [
        {
            "product_id": i,
            "quantity": 100 + (i * 10),
            "movement_type": "in",
            "reference": f"INICIAL-{i:03d}",
            "notes": f"Inventario inicial para producto {i}"
        }
        for i in range(1, 11)
    ]
    
    # Ventas de ejemplo (últimos 30 días)
    sales = []
    for i in range(1, 11):
        for day in range(30):
            sale_date = datetime.now() - timedelta(days=day)
            sales.append({
                "product_id": i,
                "quantity_sold": 1 + (day % 3),
                "unit_price": 50.0 + (i * 10),
                "sale_date": sale_date.isoformat()
            })
    
    return {
        'products': products,
        'movements': movements,
        'sales': sales
    }

if __name__ == '__main__':
    print("=" * 60)
    print("OPERACIONES MASIVAS")
    print("=" * 60)
    print()
    
    print("Este script genera y carga datos de ejemplo masivos")
    print("Útil para pruebas de rendimiento y carga de datos")
    print()
    
    sample_data = generate_sample_data()
    
    print(f"Productos a crear: {len(sample_data['products'])}")
    print(f"Movimientos a registrar: {len(sample_data['movements'])}")
    print(f"Ventas a registrar: {len(sample_data['sales'])}")
    print()
    
    print("Para ejecutar:")
    print("1. Descomenta las líneas correspondientes")
    print("2. Asegúrate de que el servidor esté corriendo")
    print()
    
    # Descomentar para ejecutar
    # bulk_create_products(sample_data['products'])
    # bulk_record_movements(sample_data['movements'])
    # bulk_record_sales(sample_data['sales'])

