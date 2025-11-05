#!/usr/bin/env python3
"""
Script de inicialización de base de datos
Crea las tablas necesarias y opcionalmente carga datos de ejemplo
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db, create_app
from datetime import datetime

def init_database(create_sample_data=False):
    """Inicializa la base de datos creando todas las tablas"""
    print("=" * 60)
    print("Inicializando Base de Datos del Sistema de Inventario")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Importar modelos para que SQLAlchemy los reconozca
            from models import (
                Product, InventoryRecord, Alert, SalesRecord,
                ReorderRecommendation, Supplier, Customer, KPIMetric
            )
            
            print("\n📊 Creando tablas de la base de datos...")
            
            # Crear todas las tablas
            db.create_all()
            
            print("✅ Tablas creadas exitosamente")
            print(f"   Base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Crear datos de ejemplo si se solicita
            if create_sample_data:
                print("\n🎯 Creando datos de ejemplo...")
                create_sample_data_func(app)
                print("✅ Datos de ejemplo creados")
            
            print("\n" + "=" * 60)
            print("✨ Inicialización completada exitosamente")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante la inicialización: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_sample_data_func(app):
    """Crea datos de ejemplo para testing"""
    from models import Supplier, Customer, Product, InventoryRecord
    
    with app.app_context():
        # Crear proveedores
        suppliers = [
            Supplier(
                name="Proveedor Principal S.A.",
                contact_person="Juan García",
                email="contacto@proveedor-principal.com",
                phone="+52 55 1234 5678",
                lead_time_days=7,
                is_active=True
            ),
            Supplier(
                name="Suministros Industriales Ltd.",
                contact_person="María López",
                email="ventas@suministros-industriales.com",
                phone="+52 55 9876 5432",
                lead_time_days=5,
                is_active=True
            )
        ]
        
        for supplier in suppliers:
            existing = Supplier.query.filter_by(name=supplier.name).first()
            if not existing:
                db.session.add(supplier)
        
        db.session.commit()
        print("   ✓ Proveedores creados")
        
        # Crear clientes
        customers = [
            Customer(
                name="Cliente Corporativo",
                email="compras@cliente-corp.com",
                phone="+52 55 1111 2222",
                company="Corporativo S.A."
            ),
            Customer(
                name="Tienda Mayorista",
                email="pedidos@tienda-mayorista.com",
                phone="+52 55 3333 4444",
                company="Mayorista Express"
            )
        ]
        
        for customer in customers:
            existing = Customer.query.filter_by(email=customer.email).first()
            if not existing:
                db.session.add(customer)
        
        db.session.commit()
        print("   ✓ Clientes creados")
        
        # Crear productos
        supplier1 = Supplier.query.filter_by(name=suppliers[0].name).first()
        supplier2 = Supplier.query.filter_by(name=suppliers[1].name).first()
        
        products = [
            Product(
                name="Producto Estándar A",
                sku="PROD-A-001",
                description="Producto de línea estándar, alta rotación",
                category="Electrónica",
                unit_price=150.00,
                cost_price=100.00,
                min_stock_level=50,
                max_stock_level=500,
                reorder_point=100,
                supplier_id=supplier1.id if supplier1 else None
            ),
            Product(
                name="Producto Premium B",
                sku="PROD-B-002",
                description="Producto premium, alta calidad",
                category="Electrónica",
                unit_price=350.00,
                cost_price=250.00,
                min_stock_level=20,
                max_stock_level=200,
                reorder_point=50,
                supplier_id=supplier2.id if supplier2 else None
            ),
            Product(
                name="Producto Básico C",
                sku="PROD-C-003",
                description="Producto básico, bajo costo",
                category="Suministros",
                unit_price=25.00,
                cost_price=15.00,
                min_stock_level=100,
                max_stock_level=1000,
                reorder_point=200,
                supplier_id=supplier1.id if supplier1 else None
            )
        ]
        
        for product in products:
            existing = Product.query.filter_by(sku=product.sku).first()
            if not existing:
                db.session.add(product)
        
        db.session.commit()
        print("   ✓ Productos creados")
        
        # Crear movimientos de inventario iniciales
        product1 = Product.query.filter_by(sku="PROD-A-001").first()
        product2 = Product.query.filter_by(sku="PROD-B-002").first()
        product3 = Product.query.filter_by(sku="PROD-C-003").first()
        
        movements = []
        
        if product1:
            movements.append(InventoryRecord(
                product_id=product1.id,
                quantity=150,
                movement_type='in',
                reference='INICIAL-001',
                notes='Inventario inicial'
            ))
        
        if product2:
            movements.append(InventoryRecord(
                product_id=product2.id,
                quantity=75,
                movement_type='in',
                reference='INICIAL-002',
                notes='Inventario inicial'
            ))
        
        if product3:
            movements.append(InventoryRecord(
                product_id=product3.id,
                quantity=300,
                movement_type='in',
                reference='INICIAL-003',
                notes='Inventario inicial'
            ))
        
        for movement in movements:
            db.session.add(movement)
        
        db.session.commit()
        print("   ✓ Movimientos de inventario creados")
        
        print(f"\n   Resumen:")
        print(f"   - Proveedores: {Supplier.query.count()}")
        print(f"   - Clientes: {Customer.query.count()}")
        print(f"   - Productos: {Product.query.count()}")
        print(f"   - Movimientos: {InventoryRecord.query.count()}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicializa la base de datos del sistema de inventario')
    parser.add_argument('--sample-data', action='store_true', 
                       help='Crear datos de ejemplo después de crear las tablas')
    
    args = parser.parse_args()
    
    success = init_database(create_sample_data=args.sample_data)
    sys.exit(0 if success else 1)




