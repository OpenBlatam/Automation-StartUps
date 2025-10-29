"""
Dashboard Web para Sistema de Gestión de Inventario
==================================================

Dashboard interactivo con KPIs, gráficos y alertas en tiempo real.
"""

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import json
from inventory_management_system import InventoryManagementSystem, AlertType
from advanced_analytics import AdvancedAnalytics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ims = InventoryManagementSystem()
analytics = AdvancedAnalytics()

# Modelos de base de datos
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    sku = db.Column(db.String(100), unique=True)
    unit_cost = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    supplier_id = db.Column(db.String(50))
    lead_time_days = db.Column(db.Integer)
    min_stock_level = db.Column(db.Integer)
    max_stock_level = db.Column(db.Integer)
    reorder_point = db.Column(db.Integer)
    reorder_quantity = db.Column(db.Integer)
    shelf_life_days = db.Column(db.Integer)
    storage_requirements = db.Column(db.Text)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    location = db.Column(db.String(100))
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='inventory_records')

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.String(100), primary_key=True)
    alert_type = db.Column(db.String(50))
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'))
    message = db.Column(db.Text)
    severity = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    
    product = db.relationship('Product', backref='alerts')

class Sale(db.Model):
    __tablename__ = 'sales_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.String(50))
    total_amount = db.Column(db.Float)
    
    product = db.relationship('Product', backref='sales')

# Rutas principales
@app.route('/')
def dashboard():
    """Página principal del dashboard"""
    # Obtener datos para el dashboard
    total_products = Product.query.count()
    active_alerts = Alert.query.filter_by(resolved=False).count()
    
    # Obtener alertas críticas
    critical_alerts = Alert.query.filter_by(
        resolved=False, 
        severity='critical'
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    # Obtener recomendaciones urgentes (simuladas)
    urgent_recommendations = []
    
    # Obtener ingresos del día
    today = datetime.now().date()
    today_sales = Sale.query.filter(
        db.func.date(Sale.sale_date) == today
    ).all()
    today_revenue = sum(sale.total_amount or 0 for sale in today_sales)
    
    # Obtener recomendaciones pendientes
    pending_recommendations = len(urgent_recommendations)
    
    return render_template('dashboard.html',
                         total_products=total_products,
                         active_alerts=active_alerts,
                         critical_alerts=critical_alerts,
                         urgent_recommendations=urgent_recommendations,
                         today_revenue=today_revenue,
                         pending_recommendations=pending_recommendations,
                         active_alerts_count=active_alerts)

@app.route('/api/kpis')
def get_kpis():
    """API endpoint para obtener KPIs"""
    kpis = ims.generate_kpis()
    return jsonify(kpis)

@app.route('/api/alerts')
def get_alerts():
    """API endpoint para obtener alertas"""
    alerts = ims.get_alerts_summary()
    return jsonify(alerts)

@app.route('/api/inventory-chart')
def get_inventory_chart():
    """Genera gráfico de niveles de inventario"""
    import sqlite3
    
    conn = sqlite3.connect(ims.db_path)
    
    # Obtener datos de inventario por categoría
    query = '''
        SELECT p.category, SUM(i.quantity * p.unit_cost) as total_value
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        GROUP BY p.category
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return jsonify({'data': [], 'layout': {}})
    
    # Crear gráfico de barras
    fig = go.Figure(data=[
        go.Bar(
            x=df['category'],
            y=df['total_value'],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        )
    ])
    
    fig.update_layout(
        title='Valor de Inventario por Categoría',
        xaxis_title='Categoría',
        yaxis_title='Valor Total ($)',
        height=400
    )
    
    return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))

@app.route('/api/stock-levels-chart')
def get_stock_levels_chart():
    """Genera gráfico de niveles de stock"""
    import sqlite3
    
    conn = sqlite3.connect(ims.db_path)
    
    # Obtener datos de niveles de stock
    query = '''
        SELECT p.name, 
               COALESCE(SUM(i.quantity), 0) as current_stock,
               p.min_stock_level,
               p.max_stock_level,
               p.reorder_point
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        GROUP BY p.id
        ORDER BY current_stock DESC
        LIMIT 10
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return jsonify({'data': [], 'layout': {}})
    
    # Crear gráfico de barras horizontales
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['name'],
        x=df['current_stock'],
        name='Stock Actual',
        orientation='h',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        y=df['name'],
        x=df['reorder_point'],
        name='Punto de Reorden',
        orientation='h',
        marker_color='orange'
    ))
    
    fig.add_trace(go.Bar(
        y=df['name'],
        x=df['max_stock_level'],
        name='Stock Máximo',
        orientation='h',
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Niveles de Stock por Producto',
        xaxis_title='Cantidad',
        yaxis_title='Producto',
        height=500,
        barmode='group'
    )
    
    return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))

@app.route('/api/sales-trend-chart')
def get_sales_trend_chart():
    """Genera gráfico de tendencia de ventas"""
    import sqlite3
    
    conn = sqlite3.connect(ims.db_path)
    
    # Obtener datos de ventas de los últimos 30 días
    query = '''
        SELECT DATE(sale_date) as sale_date, SUM(quantity) as daily_sales
        FROM sales_history
        WHERE sale_date >= date('now', '-30 days')
        GROUP BY DATE(sale_date)
        ORDER BY sale_date
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        # Generar datos de ejemplo si no hay ventas históricas
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                             end=datetime.now(), freq='D')
        df = pd.DataFrame({
            'sale_date': dates,
            'daily_sales': [10 + i % 7 for i in range(len(dates))]
        })
    
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    # Crear gráfico de línea
    fig = go.Figure(data=[
        go.Scatter(
            x=df['sale_date'],
            y=df['daily_sales'],
            mode='lines+markers',
            name='Ventas Diarias',
            line=dict(color='#2ca02c', width=3)
        )
    ])
    
    fig.update_layout(
        title='Tendencia de Ventas (Últimos 30 Días)',
        xaxis_title='Fecha',
        yaxis_title='Unidades Vendidas',
        height=400
    )
    
    return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))

@app.route('/api/supplier-performance')
def get_supplier_performance():
    """Obtiene métricas de rendimiento de proveedores"""
    import sqlite3
    
    conn = sqlite3.connect(ims.db_path)
    
    query = '''
        SELECT s.name, s.reliability_score, s.quality_rating, s.average_delivery_time
        FROM suppliers s
        ORDER BY s.reliability_score DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return jsonify(df.to_dict('records'))

@app.route('/api/products')
def get_products():
    """Obtiene lista de productos con información de stock"""
    import sqlite3
    
    conn = sqlite3.connect(ims.db_path)
    
    query = '''
        SELECT p.*, COALESCE(SUM(i.quantity), 0) as current_stock
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        GROUP BY p.id
        ORDER BY p.name
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return jsonify(df.to_dict('records'))

@app.route('/api/update-stock', methods=['POST'])
def update_stock():
    """Actualiza el stock de un producto"""
    data = request.json
    product_id = data.get('product_id')
    quantity_change = data.get('quantity_change')
    location = data.get('location', 'main_warehouse')
    
    try:
        ims.update_inventory(product_id, quantity_change, location)
        return jsonify({'success': True, 'message': 'Stock actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/resolve-alert', methods=['POST'])
def resolve_alert():
    """Marca una alerta como resuelta"""
    data = request.json
    alert_id = data.get('alert_id')
    
    try:
        import sqlite3
        conn = sqlite3.connect(ims.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE alerts SET resolved = TRUE WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Alerta resuelta'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Rutas adicionales para el sistema completo
@app.route('/products')
def products():
    """Página de gestión de productos"""
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/inventory')
def inventory():
    """Página de gestión de inventario"""
    inventory_items = db.session.query(Inventory, Product).join(Product).all()
    return render_template('inventory.html', inventory_items=inventory_items)

@app.route('/suppliers')
def suppliers():
    """Página de gestión de proveedores"""
    suppliers = db.session.execute("SELECT * FROM suppliers").fetchall()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/sales')
def sales():
    """Página de gestión de ventas"""
    sales = Sale.query.order_by(Sale.sale_date.desc()).limit(50).all()
    return render_template('sales.html', sales=sales)

@app.route('/alerts')
def alerts():
    """Página de gestión de alertas"""
    alerts = Alert.query.filter_by(resolved=False).order_by(Alert.created_at.desc()).all()
    return render_template('alerts.html', alerts=alerts)

@app.route('/replenishment')
def replenishment():
    """Página de recomendaciones de reabastecimiento"""
    optimization = analytics.inventory_optimization()
    return render_template('replenishment.html', recommendations=optimization['recommendations'])

@app.route('/reports')
def reports():
    """Página de reportes"""
    abc_analysis = analytics.abc_analysis()
    supplier_analysis = analytics.supplier_performance_analysis()
    return render_template('reports.html', abc_analysis=abc_analysis, supplier_analysis=supplier_analysis)

@app.route('/kpis')
def kpis():
    """Página de KPIs detallados"""
    kpis_data = ims.generate_kpis()
    return render_template('kpis.html', kpis=kpis_data)

# APIs adicionales
@app.route('/api/sales')
def get_sales():
    """API para obtener datos de ventas"""
    sales = Sale.query.filter(
        Sale.sale_date >= datetime.now() - timedelta(days=30)
    ).all()
    
    sales_data = []
    for sale in sales:
        sales_data.append({
            'sale_date': sale.sale_date.isoformat(),
            'total_amount': sale.total_amount or 0,
            'quantity': sale.quantity,
            'product_name': sale.product.name if sale.product else 'N/A'
        })
    
    return jsonify(sales_data)

@app.route('/api/check_alerts', methods=['POST'])
def check_alerts():
    """API para verificar alertas"""
    try:
        ims.run_daily_checks()
        return jsonify({'message': 'Alertas verificadas correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/replenishment/recommendations')
def get_replenishment_recommendations():
    """API para obtener recomendaciones de reabastecimiento"""
    try:
        optimization = analytics.inventory_optimization()
        return jsonify(optimization['recommendations'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Inicializar base de datos
@app.before_first_request
def create_tables():
    """Crear tablas de base de datos"""
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
