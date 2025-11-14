"""
Herramientas de Análisis y Reportes Avanzados
=============================================

Módulo para análisis estadístico avanzado, reportes automatizados
y herramientas de optimización de inventario.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """Clase para análisis avanzados de inventario"""
    
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
    
    def abc_analysis(self) -> Dict:
        """
        Análisis ABC para clasificar productos por importancia
        A: 80% del valor (productos críticos)
        B: 15% del valor (productos importantes)
        C: 5% del valor (productos menos importantes)
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT p.id, p.name, p.category, p.unit_cost,
                   COALESCE(SUM(i.quantity), 0) as current_stock,
                   (p.unit_cost * COALESCE(SUM(i.quantity), 0)) as inventory_value
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY inventory_value DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {'A': [], 'B': [], 'C': []}
        
        # Calcular porcentajes acumulados
        df['cumulative_value'] = df['inventory_value'].cumsum()
        df['cumulative_percentage'] = (df['cumulative_value'] / df['inventory_value'].sum()) * 100
        
        # Clasificar productos
        df['abc_category'] = 'C'
        df.loc[df['cumulative_percentage'] <= 80, 'abc_category'] = 'A'
        df.loc[(df['cumulative_percentage'] > 80) & (df['cumulative_percentage'] <= 95), 'abc_category'] = 'B'
        
        # Agrupar por categoría
        result = {}
        for category in ['A', 'B', 'C']:
            category_products = df[df['abc_category'] == category]
            result[category] = {
                'products': category_products[['id', 'name', 'category', 'inventory_value']].to_dict('records'),
                'count': len(category_products),
                'total_value': category_products['inventory_value'].sum(),
                'percentage': (category_products['inventory_value'].sum() / df['inventory_value'].sum()) * 100
            }
        
        return result
    
    def demand_forecasting_ml(self, product_id: str, days_ahead: int = 30) -> Dict:
        """
        Predicción de demanda usando Machine Learning
        """
        conn = sqlite3.connect(self.db_path)
        
        # Obtener datos históricos
        query = '''
            SELECT DATE(sale_date) as sale_date, SUM(quantity) as daily_sales
            FROM sales_history
            WHERE product_id = ?
            AND sale_date >= date('now', '-365 days')
            GROUP BY DATE(sale_date)
            ORDER BY sale_date
        '''
        
        df = pd.read_sql_query(query, conn, params=(product_id,))
        conn.close()
        
        if len(df) < 30:  # Necesitamos al menos 30 días de datos
            return {'error': 'Datos insuficientes para predicción ML'}
        
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df = df.set_index('sale_date')
        
        # Crear características para el modelo
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['day_of_month'] = df.index.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Crear características de ventana deslizante
        for window in [7, 14, 30]:
            df[f'sales_ma_{window}'] = df['daily_sales'].rolling(window=window).mean()
            df[f'sales_std_{window}'] = df['daily_sales'].rolling(window=window).std()
        
        # Eliminar filas con NaN
        df = df.dropna()
        
        if len(df) < 20:
            return {'error': 'Datos insuficientes después de limpieza'}
        
        # Preparar datos para entrenamiento
        feature_columns = ['day_of_week', 'month', 'day_of_month', 'is_weekend',
                          'sales_ma_7', 'sales_ma_14', 'sales_ma_30',
                          'sales_std_7', 'sales_std_14', 'sales_std_30']
        
        X = df[feature_columns]
        y = df['daily_sales']
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Predicción futura
        future_dates = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=days_ahead, freq='D')
        future_df = pd.DataFrame(index=future_dates)
        
        # Crear características para fechas futuras
        future_df['day_of_week'] = future_df.index.dayofweek
        future_df['month'] = future_df.index.month
        future_df['day_of_month'] = future_df.index.day
        future_df['is_weekend'] = (future_df['day_of_week'] >= 5).astype(int)
        
        # Usar valores promedio para características de ventana deslizante
        for window in [7, 14, 30]:
            future_df[f'sales_ma_{window}'] = df[f'sales_ma_{window}'].mean()
            future_df[f'sales_std_{window}'] = df[f'sales_std_{window}'].mean()
        
        # Predicción
        future_predictions = model.predict(future_df[feature_columns])
        
        return {
            'predictions': future_predictions.tolist(),
            'dates': future_dates.strftime('%Y-%m-%d').tolist(),
            'model_metrics': {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'r2_score': model.score(X_test, y_test)
            },
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
    
    def inventory_optimization(self) -> Dict:
        """
        Optimización de niveles de inventario usando análisis estadístico
        """
        conn = sqlite3.connect(self.db_path)
        
        # Obtener datos de productos y ventas históricas
        query = '''
            SELECT p.id, p.name, p.category, p.unit_cost, p.lead_time_days,
                   COALESCE(SUM(i.quantity), 0) as current_stock,
                   p.min_stock_level, p.max_stock_level, p.reorder_point
            FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY p.id
        '''
        
        products_df = pd.read_sql_query(query, conn)
        
        recommendations = []
        
        for _, product in products_df.iterrows():
            # Obtener datos históricos de ventas
            sales_query = '''
                SELECT quantity FROM sales_history
                WHERE product_id = ?
                AND sale_date >= date('now', '-90 days')
            '''
            
            sales_df = pd.read_sql_query(sales_query, conn, params=(product['id'],))
            
            if sales_df.empty:
                continue
            
            # Calcular estadísticas de demanda
            demand_mean = sales_df['quantity'].mean()
            demand_std = sales_df['quantity'].std()
            lead_time = product['lead_time_days']
            
            # Calcular niveles óptimos
            # Safety Stock = Z * σ * √(Lead Time)
            # Reorder Point = (Demand Mean * Lead Time) + Safety Stock
            z_score = 1.65  # 95% service level
            safety_stock = z_score * demand_std * np.sqrt(lead_time)
            optimal_reorder_point = int((demand_mean * lead_time) + safety_stock)
            
            # Economic Order Quantity (EOQ)
            # EOQ = √(2 * Annual Demand * Ordering Cost / Holding Cost)
            annual_demand = demand_mean * 365
            ordering_cost = 50  # Costo promedio de orden
            holding_cost_rate = 0.20  # 20% del costo unitario
            holding_cost = product['unit_cost'] * holding_cost_rate
            
            if holding_cost > 0:
                eoq = int(np.sqrt((2 * annual_demand * ordering_cost) / holding_cost))
            else:
                eoq = optimal_reorder_point
            
            # Análisis de recomendaciones
            recommendations.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'category': product['category'],
                'current_stock': product['current_stock'],
                'current_reorder_point': product['reorder_point'],
                'optimal_reorder_point': optimal_reorder_point,
                'safety_stock': int(safety_stock),
                'economic_order_quantity': eoq,
                'demand_mean': demand_mean,
                'demand_std': demand_std,
                'recommendation': self._get_optimization_recommendation(
                    product['current_stock'], optimal_reorder_point, product['max_stock_level']
                )
            })
        
        conn.close()
        
        return {
            'recommendations': recommendations,
            'summary': self._get_optimization_summary(recommendations)
        }
    
    def _get_optimization_recommendation(self, current_stock: int, optimal_rop: int, max_stock: int) -> str:
        """Genera recomendación de optimización"""
        if current_stock <= optimal_rop:
            return "REORDENAR INMEDIATAMENTE - Stock por debajo del punto óptimo"
        elif current_stock >= max_stock:
            return "REDUCIR STOCK - Exceso de inventario detectado"
        elif current_stock <= optimal_rop * 1.2:
            return "MONITOREAR - Stock cercano al punto de reorden"
        else:
            return "NIVEL ADECUADO - Stock dentro de parámetros óptimos"
    
    def _get_optimization_summary(self, recommendations: List[Dict]) -> Dict:
        """Genera resumen de optimización"""
        total_products = len(recommendations)
        reorder_needed = len([r for r in recommendations if "REORDENAR" in r['recommendation']])
        reduce_stock = len([r for r in recommendations if "REDUCIR" in r['recommendation']])
        monitor = len([r for r in recommendations if "MONITOREAR" in r['recommendation']])
        adequate = len([r for r in recommendations if "NIVEL ADECUADO" in r['recommendation']])
        
        return {
            'total_products': total_products,
            'reorder_needed': reorder_needed,
            'reduce_stock': reduce_stock,
            'monitor': monitor,
            'adequate': adequate,
            'optimization_score': (adequate / total_products * 100) if total_products > 0 else 0
        }
    
    def seasonal_analysis(self, product_id: str) -> Dict:
        """
        Análisis estacional de demanda
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT DATE(sale_date) as sale_date, SUM(quantity) as daily_sales
            FROM sales_history
            WHERE product_id = ?
            AND sale_date >= date('now', '-730 days')
            GROUP BY DATE(sale_date)
            ORDER BY sale_date
        '''
        
        df = pd.read_sql_query(query, conn, params=(product_id,))
        conn.close()
        
        if df.empty:
            return {'error': 'No hay datos históricos suficientes'}
        
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df = df.set_index('sale_date')
        
        # Análisis por mes
        monthly_sales = df.resample('M').sum()
        monthly_avg = monthly_sales.groupby(monthly_sales.index.month).mean()
        
        # Análisis por día de la semana
        df['day_of_week'] = df.index.dayofweek
        weekly_avg = df.groupby('day_of_week')['daily_sales'].mean()
        
        # Identificar patrones estacionales
        seasonal_index = monthly_avg / monthly_avg.mean()
        
        # Encontrar meses pico y valle
        peak_month = seasonal_index.idxmax()
        valley_month = seasonal_index.idxmin()
        
        return {
            'monthly_patterns': {
                'averages': monthly_avg.to_dict(),
                'seasonal_index': seasonal_index.to_dict(),
                'peak_month': peak_month,
                'valley_month': valley_month
            },
            'weekly_patterns': weekly_avg.to_dict(),
            'seasonality_strength': seasonal_index.std(),
            'recommendations': self._get_seasonal_recommendations(seasonal_index)
        }
    
    def _get_seasonal_recommendations(self, seasonal_index: pd.Series) -> List[str]:
        """Genera recomendaciones basadas en análisis estacional"""
        recommendations = []
        
        peak_month = seasonal_index.idxmax()
        valley_month = seasonal_index.idxmin()
        
        if seasonal_index.std() > 0.3:  # Alta estacionalidad
            recommendations.append(f"Alta estacionalidad detectada. Mes pico: {peak_month}, mes valle: {valley_month}")
            recommendations.append("Considerar ajustar niveles de inventario según temporada")
            recommendations.append("Planificar promociones especiales en meses de baja demanda")
        else:
            recommendations.append("Demanda relativamente estable a lo largo del año")
            recommendations.append("Mantener niveles de inventario constantes")
        
        return recommendations
    
    def supplier_performance_analysis(self) -> Dict:
        """
        Análisis de rendimiento de proveedores
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT s.*, COUNT(p.id) as product_count,
                   AVG(p.lead_time_days) as avg_lead_time,
                   SUM(i.quantity * p.unit_cost) as total_inventory_value
            FROM suppliers s
            LEFT JOIN products p ON s.id = p.supplier_id
            LEFT JOIN inventory i ON p.id = i.product_id
            GROUP BY s.id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {'error': 'No hay datos de proveedores'}
        
        # Calcular métricas de rendimiento
        df['performance_score'] = (
            df['reliability_score'] * 0.4 +
            df['quality_rating'] * 0.3 +
            (1 - (df['avg_lead_time'] / df['avg_lead_time'].max())) * 0.3
        )
        
        # Clasificar proveedores
        df['performance_category'] = 'C'
        df.loc[df['performance_score'] >= 0.8, 'performance_category'] = 'A'
        df.loc[(df['performance_score'] >= 0.6) & (df['performance_score'] < 0.8), 'performance_category'] = 'B'
        
        return {
            'suppliers': df.to_dict('records'),
            'summary': {
                'total_suppliers': len(df),
                'category_a': len(df[df['performance_category'] == 'A']),
                'category_b': len(df[df['performance_category'] == 'B']),
                'category_c': len(df[df['performance_category'] == 'C']),
                'avg_performance_score': df['performance_score'].mean()
            }
        }
    
    def generate_executive_report(self) -> Dict:
        """
        Genera reporte ejecutivo completo
        """
        # Ejecutar todos los análisis
        abc_analysis = self.abc_analysis()
        optimization = self.inventory_optimization()
        supplier_analysis = self.supplier_performance_analysis()
        
        # Obtener KPIs básicos
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE resolved = FALSE')
        active_alerts = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT SUM(i.quantity * p.unit_cost) as total_value
            FROM inventory i
            JOIN products p ON i.product_id = p.id
        ''')
        total_inventory_value = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'report_date': datetime.now().isoformat(),
            'executive_summary': {
                'total_products': total_products,
                'total_inventory_value': total_inventory_value,
                'active_alerts': active_alerts,
                'optimization_score': optimization['summary']['optimization_score']
            },
            'abc_analysis': abc_analysis,
            'inventory_optimization': optimization,
            'supplier_performance': supplier_analysis,
            'key_recommendations': self._generate_key_recommendations(abc_analysis, optimization, supplier_analysis)
        }
    
    def _generate_key_recommendations(self, abc_analysis: Dict, optimization: Dict, supplier_analysis: Dict) -> List[str]:
        """Genera recomendaciones clave basadas en todos los análisis"""
        recommendations = []
        
        # Recomendaciones basadas en ABC
        if abc_analysis['A']['count'] > 0:
            recommendations.append(f"Enfocar recursos en {abc_analysis['A']['count']} productos críticos (Categoría A)")
        
        # Recomendaciones basadas en optimización
        if optimization['summary']['reorder_needed'] > 0:
            recommendations.append(f"Reordenar inmediatamente {optimization['summary']['reorder_needed']} productos")
        
        if optimization['summary']['reduce_stock'] > 0:
            recommendations.append(f"Reducir stock de {optimization['summary']['reduce_stock']} productos con exceso")
        
        # Recomendaciones basadas en proveedores
        if supplier_analysis['summary']['category_c'] > 0:
            recommendations.append(f"Evaluar {supplier_analysis['summary']['category_c']} proveedores de bajo rendimiento")
        
        return recommendations

# Ejemplo de uso
if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    
    # Generar reporte ejecutivo
    report = analytics.generate_executive_report()
    
    print("=== REPORTE EJECUTIVO DE INVENTARIO ===")
    print(f"Fecha: {report['report_date']}")
    print(f"Total productos: {report['executive_summary']['total_products']}")
    print(f"Valor total inventario: ${report['executive_summary']['total_inventory_value']:,.2f}")
    print(f"Alertas activas: {report['executive_summary']['active_alerts']}")
    print(f"Puntuación de optimización: {report['executive_summary']['optimization_score']:.1f}%")
    
    print("\n=== RECOMENDACIONES CLAVE ===")
    for i, rec in enumerate(report['key_recommendations'], 1):
        print(f"{i}. {rec}")
    
    print("\n=== ANÁLISIS ABC ===")
    for category in ['A', 'B', 'C']:
        data = report['abc_analysis'][category]
        print(f"Categoría {category}: {data['count']} productos ({data['percentage']:.1f}% del valor)")
    
    print("\n=== OPTIMIZACIÓN DE INVENTARIO ===")
    opt_summary = report['inventory_optimization']['summary']
    print(f"Productos que necesitan reorden: {opt_summary['reorder_needed']}")
    print(f"Productos con exceso de stock: {opt_summary['reduce_stock']}")
    print(f"Productos a monitorear: {opt_summary['monitor']}")
    print(f"Productos con nivel adecuado: {opt_summary['adequate']}")



