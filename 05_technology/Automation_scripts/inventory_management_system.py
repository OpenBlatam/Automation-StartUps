"""
Sistema de Gestión de Inventario y Cadena de Suministro
=====================================================

Este sistema está diseñado para minimizar roturas de stock y exceso de inventario
mediante el uso de algoritmos de predicción, alertas inteligentes y análisis de datos.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Tipos de alertas del sistema"""
    LOW_STOCK = "low_stock"
    HIGH_STOCK = "high_stock"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    SUPPLIER_DELAY = "supplier_delay"
    DEMAND_SPIKE = "demand_spike"
    QUALITY_ISSUE = "quality_issue"

@dataclass
class Product:
    """Modelo de datos para productos"""
    id: str
    name: str
    category: str
    sku: str
    unit_cost: float
    selling_price: float
    supplier_id: str
    lead_time_days: int
    min_stock_level: int
    max_stock_level: int
    reorder_point: int
    reorder_quantity: int
    shelf_life_days: Optional[int] = None
    storage_requirements: Optional[str] = None

@dataclass
class InventoryRecord:
    """Registro de inventario"""
    product_id: str
    quantity: int
    location: str
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    last_updated: datetime = None

@dataclass
class Supplier:
    """Modelo de datos para proveedores"""
    id: str
    name: str
    contact_info: Dict
    reliability_score: float  # 0-1
    average_delivery_time: int
    quality_rating: float  # 0-1
    payment_terms: str
    minimum_order_value: float

@dataclass
class Alert:
    """Modelo de alerta"""
    id: str
    type: AlertType
    product_id: str
    message: str
    severity: str  # low, medium, high, critical
    created_at: datetime
    resolved: bool = False

class InventoryManagementSystem:
    """Sistema principal de gestión de inventario"""
    
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.init_database()
        self.alerts = []
        
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                sku TEXT UNIQUE,
                unit_cost REAL,
                selling_price REAL,
                supplier_id TEXT,
                lead_time_days INTEGER,
                min_stock_level INTEGER,
                max_stock_level INTEGER,
                reorder_point INTEGER,
                reorder_quantity INTEGER,
                shelf_life_days INTEGER,
                storage_requirements TEXT
            )
        ''')
        
        # Tabla de inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                quantity INTEGER,
                location TEXT,
                batch_number TEXT,
                expiry_date TEXT,
                last_updated TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Tabla de proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_info TEXT,
                reliability_score REAL,
                average_delivery_time INTEGER,
                quality_rating REAL,
                payment_terms TEXT,
                minimum_order_value REAL
            )
        ''')
        
        # Tabla de ventas históricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                quantity INTEGER,
                sale_date TEXT,
                customer_id TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Tabla de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                type TEXT,
                product_id TEXT,
                message TEXT,
                severity TEXT,
                created_at TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")
    
    def add_product(self, product: Product):
        """Agrega un nuevo producto al sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO products 
            (id, name, category, sku, unit_cost, selling_price, supplier_id,
             lead_time_days, min_stock_level, max_stock_level, reorder_point,
             reorder_quantity, shelf_life_days, storage_requirements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product.id, product.name, product.category, product.sku,
            product.unit_cost, product.selling_price, product.supplier_id,
            product.lead_time_days, product.min_stock_level, product.max_stock_level,
            product.reorder_point, product.reorder_quantity, product.shelf_life_days,
            product.storage_requirements
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Producto {product.name} agregado al sistema")
    
    def add_supplier(self, supplier: Supplier):
        """Agrega un nuevo proveedor al sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO suppliers 
            (id, name, contact_info, reliability_score, average_delivery_time,
             quality_rating, payment_terms, minimum_order_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            supplier.id, supplier.name, json.dumps(supplier.contact_info),
            supplier.reliability_score, supplier.average_delivery_time,
            supplier.quality_rating, supplier.payment_terms, supplier.minimum_order_value
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Proveedor {supplier.name} agregado al sistema")
    
    def update_inventory(self, product_id: str, quantity_change: int, 
                        location: str = "main_warehouse", batch_number: str = None,
                        expiry_date: datetime = None):
        """Actualiza el inventario de un producto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener cantidad actual
        cursor.execute('SELECT quantity FROM inventory WHERE product_id = ? AND location = ?',
                      (product_id, location))
        result = cursor.fetchone()
        current_quantity = result[0] if result else 0
        
        new_quantity = current_quantity + quantity_change
        
        if new_quantity < 0:
            logger.warning(f"Intento de reducir inventario por debajo de 0 para producto {product_id}")
            new_quantity = 0
        
        # Actualizar o insertar registro
        cursor.execute('''
            INSERT OR REPLACE INTO inventory 
            (product_id, quantity, location, batch_number, expiry_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            product_id, new_quantity, location, batch_number,
            expiry_date.isoformat() if expiry_date else None,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Verificar alertas después de actualizar inventario
        self.check_stock_alerts(product_id)
        logger.info(f"Inventario actualizado para producto {product_id}: {new_quantity} unidades")
    
    def check_stock_alerts(self, product_id: str):
        """Verifica y genera alertas de stock para un producto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener información del producto y stock actual
        cursor.execute('''
            SELECT p.*, COALESCE(SUM(i.quantity), 0) as total_stock
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.id = ?
            GROUP BY p.id
        ''', (product_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        product_data = dict(zip([col[0] for col in cursor.description], result))
        current_stock = product_data['total_stock']
        
        # Verificar stock bajo
        if current_stock <= product_data['reorder_point']:
            self.create_alert(
                AlertType.LOW_STOCK,
                product_id,
                f"Stock bajo para {product_data['name']}: {current_stock} unidades (punto de reorden: {product_data['reorder_point']})",
                "high"
            )
        
        # Verificar stock alto
        if current_stock >= product_data['max_stock_level']:
            self.create_alert(
                AlertType.HIGH_STOCK,
                product_id,
                f"Stock alto para {product_data['name']}: {current_stock} unidades (máximo: {product_data['max_stock_level']})",
                "medium"
            )
        
        conn.close()
    
    def check_expiry_alerts(self):
        """Verifica productos próximos a vencer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Productos que vencen en los próximos 30 días
        thirty_days_from_now = (datetime.now() + timedelta(days=30)).isoformat()
        
        cursor.execute('''
            SELECT i.product_id, i.expiry_date, i.quantity, p.name
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.expiry_date IS NOT NULL 
            AND i.expiry_date <= ?
            AND i.quantity > 0
        ''', (thirty_days_from_now,))
        
        expiring_products = cursor.fetchall()
        
        for product_id, expiry_date, quantity, name in expiring_products:
            expiry_dt = datetime.fromisoformat(expiry_date)
            days_until_expiry = (expiry_dt - datetime.now()).days
            
            if days_until_expiry <= 0:
                self.create_alert(
                    AlertType.EXPIRED,
                    product_id,
                    f"Producto vencido: {name} (venció hace {abs(days_until_expiry)} días)",
                    "critical"
                )
            elif days_until_expiry <= 7:
                self.create_alert(
                    AlertType.EXPIRING_SOON,
                    product_id,
                    f"Producto próximo a vencer: {name} (vence en {days_until_expiry} días)",
                    "high"
                )
        
        conn.close()
    
    def create_alert(self, alert_type: AlertType, product_id: str, message: str, severity: str):
        """Crea una nueva alerta"""
        alert_id = f"{alert_type.value}_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        alert = Alert(
            id=alert_id,
            type=alert_type,
            product_id=product_id,
            message=message,
            severity=severity,
            created_at=datetime.now()
        )
        
        # Guardar en base de datos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (id, type, product_id, message, severity, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert.id, alert.type.value, alert.product_id,
            alert.message, alert.severity, alert.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.alerts.append(alert)
        logger.warning(f"ALERTA [{severity.upper()}]: {message}")
    
    def predict_demand(self, product_id: str, days_ahead: int = 30) -> float:
        """Predice la demanda futura usando datos históricos"""
        conn = sqlite3.connect(self.db_path)
        
        # Obtener datos históricos de ventas
        query = '''
            SELECT DATE(sale_date) as sale_date, SUM(quantity) as daily_sales
            FROM sales_history
            WHERE product_id = ?
            AND sale_date >= date('now', '-90 days')
            GROUP BY DATE(sale_date)
            ORDER BY sale_date
        '''
        
        df = pd.read_sql_query(query, conn, params=(product_id,))
        conn.close()
        
        if df.empty:
            logger.warning(f"No hay datos históricos para producto {product_id}")
            return 0.0
        
        # Método simple de promedio móvil con tendencia
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df = df.set_index('sale_date')
        
        # Calcular promedio móvil de 7 días
        df['ma_7'] = df['daily_sales'].rolling(window=7).mean()
        
        # Calcular tendencia simple
        if len(df) >= 14:
            recent_avg = df['daily_sales'].tail(7).mean()
            older_avg = df['daily_sales'].tail(14).head(7).mean()
            trend = (recent_avg - older_avg) / 7  # tendencia diaria
        else:
            trend = 0
        
        # Predicción con tendencia
        last_ma = df['ma_7'].iloc[-1] if not df['ma_7'].isna().iloc[-1] else df['daily_sales'].mean()
        predicted_daily_demand = last_ma + (trend * days_ahead)
        
        return max(0, predicted_daily_demand * days_ahead)
    
    def calculate_optimal_reorder_point(self, product_id: str) -> int:
        """Calcula el punto de reorden óptimo usando análisis estadístico"""
        conn = sqlite3.connect(self.db_path)
        
        # Obtener datos del producto
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product_data = cursor.fetchone()
        
        if not product_data:
            conn.close()
            return 0
        
        # Obtener datos históricos de ventas
        query = '''
            SELECT quantity FROM sales_history
            WHERE product_id = ?
            AND sale_date >= date('now', '-90 days')
        '''
        
        df = pd.read_sql_query(query, conn, params=(product_id,))
        conn.close()
        
        if df.empty:
            return product_data[9]  # min_stock_level por defecto
        
        # Calcular estadísticas de demanda
        demand_mean = df['quantity'].mean()
        demand_std = df['quantity'].std()
        
        # Obtener tiempo de entrega del proveedor
        lead_time = product_data[7]  # lead_time_days
        
        # Calcular punto de reorden usando fórmula estándar
        # ROP = (Demanda promedio × Tiempo de entrega) + (Z × Desviación estándar × √Tiempo de entrega)
        # Z = 1.65 para 95% de nivel de servicio
        z_score = 1.65
        safety_stock = z_score * demand_std * np.sqrt(lead_time)
        reorder_point = int((demand_mean * lead_time) + safety_stock)
        
        return max(reorder_point, product_data[9])  # No menos que el mínimo establecido
    
    def generate_kpis(self) -> Dict:
        """Genera indicadores clave de rendimiento"""
        conn = sqlite3.connect(self.db_path)
        
        # KPIs de inventario
        cursor = conn.cursor()
        
        # Stock total valorizado
        cursor.execute('''
            SELECT SUM(i.quantity * p.unit_cost) as total_value
            FROM inventory i
            JOIN products p ON i.product_id = p.id
        ''')
        total_inventory_value = cursor.fetchone()[0] or 0
        
        # Productos con stock bajo
        cursor.execute('''
            SELECT COUNT(*)
            FROM (
                SELECT p.id, COALESCE(SUM(i.quantity), 0) as total_stock, p.reorder_point
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                GROUP BY p.id
                HAVING total_stock <= p.reorder_point
            )
        ''')
        low_stock_products = cursor.fetchone()[0]
        
        # Productos con stock alto
        cursor.execute('''
            SELECT COUNT(*)
            FROM (
                SELECT p.id, COALESCE(SUM(i.quantity), 0) as total_stock, p.max_stock_level
                FROM products p
                LEFT JOIN inventory i ON p.id = i.product_id
                GROUP BY p.id
                HAVING total_stock >= p.max_stock_level
            )
        ''')
        high_stock_products = cursor.fetchone()[0]
        
        # Rotación de inventario (últimos 30 días)
        cursor.execute('''
            SELECT SUM(sh.quantity * p.unit_cost) as sales_value
            FROM sales_history sh
            JOIN products p ON sh.product_id = p.id
            WHERE sh.sale_date >= date('now', '-30 days')
        ''')
        monthly_sales_value = cursor.fetchone()[0] or 0
        
        inventory_turnover = monthly_sales_value / total_inventory_value if total_inventory_value > 0 else 0
        
        # Alertas activas
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE resolved = FALSE')
        active_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_inventory_value': total_inventory_value,
            'low_stock_products': low_stock_products,
            'high_stock_products': high_stock_products,
            'inventory_turnover': round(inventory_turnover, 2),
            'active_alerts': active_alerts,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_alerts_summary(self) -> List[Dict]:
        """Obtiene resumen de alertas activas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, p.name as product_name
            FROM alerts a
            JOIN products p ON a.product_id = p.id
            WHERE a.resolved = FALSE
            ORDER BY 
                CASE a.severity 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                a.created_at DESC
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'type': row[1],
                'product_name': row[6],
                'message': row[3],
                'severity': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return alerts
    
    def run_daily_checks(self):
        """Ejecuta verificaciones diarias del sistema"""
        logger.info("Ejecutando verificaciones diarias...")
        
        # Verificar alertas de vencimiento
        self.check_expiry_alerts()
        
        # Verificar stock de todos los productos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM products')
        product_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        for product_id in product_ids:
            self.check_stock_alerts(product_id)
        
        logger.info("Verificaciones diarias completadas")

# Ejemplo de uso del sistema
if __name__ == "__main__":
    # Inicializar sistema
    ims = InventoryManagementSystem()
    
    # Agregar proveedor de ejemplo
    supplier = Supplier(
        id="SUP001",
        name="Proveedor Principal S.A.",
        contact_info={"email": "contacto@proveedor.com", "phone": "+1234567890"},
        reliability_score=0.85,
        average_delivery_time=7,
        quality_rating=0.90,
        payment_terms="30 días",
        minimum_order_value=1000.0
    )
    ims.add_supplier(supplier)
    
    # Agregar productos de ejemplo
    products = [
        Product(
            id="PROD001",
            name="Laptop Dell XPS 13",
            category="Electrónicos",
            sku="DELL-XPS13-001",
            unit_cost=1200.0,
            selling_price=1500.0,
            supplier_id="SUP001",
            lead_time_days=7,
            min_stock_level=5,
            max_stock_level=50,
            reorder_point=10,
            reorder_quantity=20,
            shelf_life_days=None,
            storage_requirements="Ambiente seco, temperatura controlada"
        ),
        Product(
            id="PROD002",
            name="Mouse Inalámbrico Logitech",
            category="Accesorios",
            sku="LOG-MOUSE-001",
            unit_cost=25.0,
            selling_price=35.0,
            supplier_id="SUP001",
            lead_time_days=3,
            min_stock_level=20,
            max_stock_level=200,
            reorder_point=50,
            reorder_quantity=100,
            shelf_life_days=None
        ),
        Product(
            id="PROD003",
            name="Café Premium Colombia",
            category="Alimentos",
            sku="CAFE-COL-001",
            unit_cost=8.0,
            selling_price=12.0,
            supplier_id="SUP001",
            lead_time_days=5,
            min_stock_level=30,
            max_stock_level=300,
            reorder_point=60,
            reorder_quantity=150,
            shelf_life_days=365,
            storage_requirements="Ambiente fresco y seco"
        )
    ]
    
    for product in products:
        ims.add_product(product)
    
    # Simular inventario inicial
    ims.update_inventory("PROD001", 15)  # Stock normal
    ims.update_inventory("PROD002", 8)   # Stock bajo (reorder_point = 50)
    ims.update_inventory("PROD003", 400) # Stock alto (max_stock_level = 300)
    
    # Simular productos próximos a vencer
    expiry_date = datetime.now() + timedelta(days=5)
    ims.update_inventory("PROD003", 50, batch_number="BATCH001", expiry_date=expiry_date)
    
    # Ejecutar verificaciones
    ims.run_daily_checks()
    
    # Mostrar KPIs
    kpis = ims.generate_kpis()
    print("\n=== INDICADORES CLAVE DE RENDIMIENTO ===")
    for key, value in kpis.items():
        print(f"{key}: {value}")
    
    # Mostrar alertas
    alerts = ims.get_alerts_summary()
    print(f"\n=== ALERTAS ACTIVAS ({len(alerts)}) ===")
    for alert in alerts:
        print(f"[{alert['severity'].upper()}] {alert['message']}")
    
    # Ejemplo de predicción de demanda
    predicted_demand = ims.predict_demand("PROD001", 30)
    print(f"\nDemanda predicha para PROD001 en 30 días: {predicted_demand:.2f} unidades")
    
    # Ejemplo de cálculo de punto de reorden óptimo
    optimal_rop = ims.calculate_optimal_reorder_point("PROD001")
    print(f"Punto de reorden óptimo para PROD001: {optimal_rop} unidades")
