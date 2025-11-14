from datetime import datetime, timedelta
from app import db
import json

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
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Supplier(db.Model):
    """Modelo para proveedores"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    lead_time_days = db.Column(db.Integer, default=7)  # Tiempo de entrega en días
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    products = db.relationship('Product', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class InventoryRecord(db.Model):
    """Registros de inventario"""
    __tablename__ = 'inventory_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'in', 'out', 'adjustment'
    reference = db.Column(db.String(100))  # Número de factura, orden, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InventoryRecord {self.product.name} - {self.quantity}>'

class SalesRecord(db.Model):
    """Registros de ventas para análisis de demanda"""
    __tablename__ = 'sales_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SalesRecord {self.product.name} - {self.quantity_sold}>'

class Customer(db.Model):
    """Modelo para clientes"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    sales_records = db.relationship('SalesRecord', backref='customer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Alert(db.Model):
    """Sistema de alertas"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'low_stock', 'out_of_stock', 'reorder'
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alert {self.alert_type} - {self.product.name}>'

class DemandForecast(db.Model):
    """Previsiones de demanda"""
    __tablename__ = 'demand_forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    predicted_demand = db.Column(db.Float, nullable=False)
    confidence_level = db.Column(db.Float, default=0.8)  # Nivel de confianza 0-1
    method_used = db.Column(db.String(50))  # 'moving_average', 'exponential_smoothing', 'arima'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DemandForecast {self.product.name} - {self.forecast_date}>'

class ReorderRecommendation(db.Model):
    """Recomendaciones de reposición"""
    __tablename__ = 'reorder_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    recommended_quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    urgency = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    estimated_cost = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ReorderRecommendation {self.product.name} - {self.recommended_quantity}>'

class KPIMetric(db.Model):
    """Métricas y KPIs del sistema"""
    __tablename__ = 'kpi_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))
    category = db.Column(db.String(50))  # 'inventory', 'sales', 'financial', 'operational'
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KPIMetric {self.metric_name} - {self.metric_value}>'



