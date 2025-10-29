#!/usr/bin/env python3
"""
Script para crear datos de ejemplo en el sistema de inventario
"""

from app import create_app, db
from models import Product, Supplier, Customer, InventoryRecord, SalesRecord
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Crea datos de ejemplo para el sistema"""
    
    app = create_app()
    
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        
        print("Creando proveedores de ejemplo...")
        
        # Crear proveedores
        suppliers = [
            Supplier(
                name="Proveedor ABC",
                contact_person="Juan Pérez",
                email="juan@proveedorabc.com",
                phone="+1-555-0101",
                address="123 Main St, Ciudad",
                lead_time_days=5
            ),
            Supplier(
                name="Distribuidora XYZ",
                contact_person="María García",
                email="maria@distribuidoraxyz.com",
                phone="+1-555-0102",
                address="456 Oak Ave, Ciudad",
                lead_time_days=7
            ),
            Supplier(
                name="Suministros Global",
                contact_person="Carlos López",
                email="carlos@suministrosglobal.com",
                phone="+1-555-0103",
                address="789 Pine Rd, Ciudad",
                lead_time_days=10
            )
        ]
        
        for supplier in suppliers:
            db.session.add(supplier)
        
        db.session.commit()
        
        print("Creando productos de ejemplo...")
        
        # Crear productos
        products = [
            Product(
                name="Laptop Dell Inspiron 15",
                sku="DELL-INS15-001",
                description="Laptop Dell Inspiron 15 pulgadas, Intel i5, 8GB RAM, 256GB SSD",
                category="Electrónicos",
                unit_price=899.99,
                cost_price=650.00,
                min_stock_level=5,
                max_stock_level=50,
                reorder_point=10,
                supplier_id=1
            ),
            Product(
                name="Mouse Inalámbrico Logitech",
                sku="LOG-MOUSE-001",
                description="Mouse inalámbrico Logitech con receptor USB",
                category="Accesorios",
                unit_price=29.99,
                cost_price=15.00,
                min_stock_level=20,
                max_stock_level=200,
                reorder_point=30,
                supplier_id=1
            ),
            Product(
                name="Teclado Mecánico RGB",
                sku="KEYB-MECH-001",
                description="Teclado mecánico con retroiluminación RGB",
                category="Accesorios",
                unit_price=149.99,
                cost_price=80.00,
                min_stock_level=10,
                max_stock_level=100,
                reorder_point=15,
                supplier_id=2
            ),
            Product(
                name="Monitor Samsung 24 pulgadas",
                sku="SAMS-MON24-001",
                description="Monitor Samsung 24 pulgadas Full HD",
                category="Monitores",
                unit_price=199.99,
                cost_price=120.00,
                min_stock_level=8,
                max_stock_level=80,
                reorder_point=12,
                supplier_id=2
            ),
            Product(
                name="Cable HDMI 2 metros",
                sku="CABLE-HDMI-001",
                description="Cable HDMI de alta velocidad 2 metros",
                category="Cables",
                unit_price=12.99,
                cost_price=5.00,
                min_stock_level=50,
                max_stock_level=500,
                reorder_point=75,
                supplier_id=3
            ),
            Product(
                name="Disco Duro Externo 1TB",
                sku="HD-EXT1TB-001",
                description="Disco duro externo USB 3.0 1TB",
                category="Almacenamiento",
                unit_price=79.99,
                cost_price=45.00,
                min_stock_level=15,
                max_stock_level=150,
                reorder_point=25,
                supplier_id=3
            ),
            Product(
                name="Webcam HD 1080p",
                sku="WEBCAM-HD-001",
                description="Webcam HD 1080p con micrófono integrado",
                category="Accesorios",
                unit_price=89.99,
                cost_price=50.00,
                min_stock_level=12,
                max_stock_level=120,
                reorder_point=20,
                supplier_id=1
            ),
            Product(
                name="Auriculares Gaming",
                sku="AUDIO-GAME-001",
                description="Auriculares gaming con micrófono y RGB",
                category="Audio",
                unit_price=129.99,
                cost_price=70.00,
                min_stock_level=8,
                max_stock_level=80,
                reorder_point=12,
                supplier_id=2
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        
        print("Creando clientes de ejemplo...")
        
        # Crear clientes
        customers = [
            Customer(
                name="Empresa Tecnológica SA",
                email="compras@empresatecnologica.com",
                phone="+1-555-0201",
                address="100 Business Ave, Ciudad"
            ),
            Customer(
                name="Tienda de Electrónicos",
                email="ventas@tiendaelectronicos.com",
                phone="+1-555-0202",
                address="200 Commerce St, Ciudad"
            ),
            Customer(
                name="Cliente Individual",
                email="cliente@email.com",
                phone="+1-555-0203",
                address="300 Residential Rd, Ciudad"
            )
        ]
        
        for customer in customers:
            db.session.add(customer)
        
        db.session.commit()
        
        print("Creando movimientos de inventario iniciales...")
        
        # Crear movimientos de inventario iniciales
        for product in products:
            # Entrada inicial de inventario
            initial_stock = random.randint(product.max_stock_level // 2, product.max_stock_level)
            
            inventory_record = InventoryRecord(
                product_id=product.id,
                quantity=initial_stock,
                movement_type='in',
                reference='INITIAL-STOCK',
                notes='Stock inicial del sistema'
            )
            
            db.session.add(inventory_record)
        
        db.session.commit()
        
        print("Creando ventas históricas...")
        
        # Crear ventas históricas (últimos 90 días)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        for i in range(200):  # 200 ventas aleatorias
            # Fecha aleatoria en los últimos 90 días
            random_days = random.randint(0, 90)
            sale_date = start_date + timedelta(days=random_days)
            
            # Producto aleatorio
            product = random.choice(products)
            
            # Cantidad aleatoria (1-5 unidades)
            quantity = random.randint(1, 5)
            
            # Precio del producto
            unit_price = product.unit_price
            
            # Crear registro de venta
            sale_record = SalesRecord(
                product_id=product.id,
                quantity_sold=quantity,
                sale_date=sale_date,
                unit_price=unit_price,
                total_amount=quantity * unit_price,
                customer_id=random.choice(customers).id
            )
            
            db.session.add(sale_record)
            
            # Crear movimiento de salida de inventario
            inventory_record = InventoryRecord(
                product_id=product.id,
                quantity=quantity,
                movement_type='out',
                reference=f'SALE-{sale_record.id}',
                notes='Venta registrada'
            )
            
            db.session.add(inventory_record)
        
        db.session.commit()
        
        print("✅ Datos de ejemplo creados exitosamente!")
        print(f"   - {len(suppliers)} proveedores")
        print(f"   - {len(products)} productos")
        print(f"   - {len(customers)} clientes")
        print(f"   - 200 ventas históricas")
        print(f"   - Movimientos de inventario iniciales")
        print("")
        print("🚀 El sistema está listo para usar!")
        print("   Accede a http://localhost:5000 para ver el dashboard")

if __name__ == "__main__":
    create_sample_data()



