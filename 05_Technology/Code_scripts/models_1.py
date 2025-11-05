"""
Modelos de base de datos para el Sistema de Control de Inventario Inteligente
"""
from datetime import datetime, timedelta
from app import db
import json

# ==================== MODELOS BASE ====================

class Supplier(db.Model):
    """Modelo para proveedores"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    lead_time_days = db.Column(db.Integer, default=7)  # Tiempo de entrega en días
    payment_terms = db.Column(db.String(50))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    products = db.relationship('Product', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'


class Customer(db.Model):
    """Modelo para clientes"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    sales = db.relationship('SalesRecord', backref='customer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Customer {self.name}>'


class Product(db.Model):
    """Modelo para productos"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    unit_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    min_stock_level = db.Column(db.Integer, default=10)
    max_stock_level = db.Column(db.Integer, default=100)
    reorder_point = db.Column(db.Integer, default=20)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    inventory_records = db.relationship('InventoryRecord', backref='product', lazy='dynamic')
    sales_records = db.relationship('SalesRecord', backref='product', lazy='dynamic')
    alerts = db.relationship('Alert', backref='product', lazy='dynamic')
    reorder_recommendations = db.relationship('ReorderRecommendation', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'


class InventoryRecord(db.Model):
    """Modelo para registros de movimientos de inventario"""
    __tablename__ = 'inventory_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Positivo para entrada, negativo para salida
    movement_type = db.Column(db.String(20), nullable=False)  # 'in', 'out', 'adjustment'
    reference = db.Column(db.String(100))  # Referencia externa (pedido, venta, etc.)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<InventoryRecord {self.movement_type} {self.quantity}>'


class SalesRecord(db.Model):
    """Modelo para registros de ventas"""
    __tablename__ = 'sales_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    quantity_sold = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SalesRecord {self.quantity_sold} units @ ${self.unit_price}>'


class Alert(db.Model):
    """Modelo para alertas del sistema"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'low_stock', 'out_of_stock', 'reorder'
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # 'critical', 'high', 'medium', 'low'
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_type} - {self.severity}>'


class ReorderRecommendation(db.Model):
    """Modelo para recomendaciones de reposición"""
    __tablename__ = 'reorder_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    recommended_quantity = db.Column(db.Integer, nullable=False)
    current_stock = db.Column(db.Integer, nullable=False)
    dynamic_reorder_point = db.Column(db.Integer)
    urgency = db.Column(db.String(20), default='medium')  # 'critical', 'high', 'medium', 'low'
    estimated_cost = db.Column(db.Float)
    reason = db.Column(db.Text)
    is_processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ReorderRecommendation Product {self.product_id}: {self.recommended_quantity} units>'


class KPIMetric(db.Model):
    """Modelo para almacenar métricas KPI históricas"""
    __tablename__ = 'kpi_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_category = db.Column(db.String(50))  # 'inventory', 'sales', 'financial', 'operational'
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))  # 'units', 'currency', 'percentage', 'days'
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    metadata = db.Column(db.Text)  # JSON string con información adicional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KPIMetric {self.metric_name}: {self.value} {self.unit}>'
    
    def get_metadata(self):
        """Obtiene metadata como diccionario"""
        try:
            return json.loads(self.metadata) if self.metadata else {}
        except:
            return {}
    
    def set_metadata(self, data):
        """Establece metadata desde un diccionario"""
        self.metadata = json.dumps(data)

