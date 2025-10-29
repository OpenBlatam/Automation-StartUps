from datetime import datetime, timedelta
from app import db
from models import Product, SalesRecord, InventoryRecord, Alert
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import json
import os
import pickle
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DeepLearningModel:
    """Modelo de deep learning"""
    name: str
    model_type: str  # 'regression', 'classification', 'anomaly_detection'
    model: object
    scaler: object
    feature_selector: object
    accuracy: float
    trained_at: datetime
    features_used: List[str]

@dataclass
class AIInsight:
    """Insight generado por IA"""
    type: str
    title: str
    description: str
    confidence: float
    impact: str  # 'high', 'medium', 'low'
    recommendations: List[str]
    generated_at: datetime

class AdvancedAIService:
    """Servicio avanzado de Inteligencia Artificial"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.models_dir = 'ai_models'
        self.insights_history = []
        
        # Crear directorio para modelos si no existe
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_advanced_features(self, product_id: int = None, days_back: int = 365) -> pd.DataFrame:
        """Prepara características avanzadas para modelos de IA"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            # Obtener datos de ventas
            if product_id:
                sales_query = SalesRecord.query.filter(
                    SalesRecord.product_id == product_id,
                    SalesRecord.sale_date >= start_date,
                    SalesRecord.sale_date <= end_date
                )
            else:
                sales_query = SalesRecord.query.filter(
                    SalesRecord.sale_date >= start_date,
                    SalesRecord.sale_date <= end_date
                )
            
            sales_data = sales_query.all()
            
            if not sales_data:
                return pd.DataFrame()
            
            # Preparar DataFrame
            data = []
            for sale in sales_data:
                data.append({
                    'date': sale.sale_date,
                    'product_id': sale.product_id,
                    'product_name': sale.product.name,
                    'category': sale.product.category,
                    'quantity_sold': sale.quantity_sold,
                    'unit_price': sale.unit_price,
                    'total_amount': sale.total_amount,
                    'day_of_week': sale.sale_date.weekday(),
                    'day_of_month': sale.sale_date.day,
                    'month': sale.sale_date.month,
                    'quarter': (sale.sale_date.month - 1) // 3 + 1,
                    'year': sale.sale_date.year,
                    'is_weekend': sale.sale_date.weekday() >= 5,
                    'is_month_start': sale.sale_date.day <= 7,
                    'is_month_end': sale.sale_date.day >= 25,
                    'is_holiday_season': sale.sale_date.month in [11, 12],
                    'is_summer': sale.sale_date.month in [6, 7, 8],
                    'is_winter': sale.sale_date.month in [12, 1, 2]
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Características avanzadas
            df = self._add_advanced_time_features(df)
            df = self._add_interaction_features(df)
            df = self._add_statistical_features(df)
            df = self._add_market_features(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f'Error preparando características avanzadas: {str(e)}')
            return pd.DataFrame()
    
    def _add_advanced_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características temporales avanzadas"""
        try:
            # Características cíclicas avanzadas
            df['sin_day_of_year'] = np.sin(2 * np.pi * df['date'].dt.dayofyear / 365.25)
            df['cos_day_of_year'] = np.cos(2 * np.pi * df['date'].dt.dayofyear / 365.25)
            df['sin_week_of_year'] = np.sin(2 * np.pi * df['date'].dt.isocalendar().week / 52)
            df['cos_week_of_year'] = np.cos(2 * np.pi * df['date'].dt.isocalendar().week / 52)
            df['sin_hour'] = np.sin(2 * np.pi * df['date'].dt.hour / 24)
            df['cos_hour'] = np.cos(2 * np.pi * df['date'].dt.hour / 24)
            
            # Patrones temporales
            df['is_payday'] = df['day_of_month'].isin([15, 30, 31])
            df['is_month_end'] = df['date'].dt.is_month_end
            df['is_quarter_end'] = df['date'].dt.is_quarter_end
            df['is_year_end'] = df['date'].dt.is_year_end
            
            # Estacionalidad avanzada
            df['spring'] = df['month'].isin([3, 4, 5])
            df['summer'] = df['month'].isin([6, 7, 8])
            df['autumn'] = df['month'].isin([9, 10, 11])
            df['winter'] = df['month'].isin([12, 1, 2])
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características temporales avanzadas: {str(e)}')
            return df
    
    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características de interacción"""
        try:
            # Interacciones entre variables
            df['price_quantity_interaction'] = df['unit_price'] * df['quantity_sold']
            df['category_price_interaction'] = df['category'].astype('category').cat.codes * df['unit_price']
            df['weekend_price_interaction'] = df['is_weekend'].astype(int) * df['unit_price']
            df['holiday_quantity_interaction'] = df['is_holiday_season'].astype(int) * df['quantity_sold']
            
            # Ratios y proporciones
            df['price_to_avg_price'] = df['unit_price'] / df.groupby('product_id')['unit_price'].transform('mean')
            df['quantity_to_avg_quantity'] = df['quantity_sold'] / df.groupby('product_id')['quantity_sold'].transform('mean')
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características de interacción: {str(e)}')
            return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características estadísticas"""
        try:
            # Estadísticas móviles avanzadas
            for window in [3, 7, 14, 30]:
                df[f'quantity_ma_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).mean().reset_index(0, drop=True)
                
                df[f'quantity_std_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).std().reset_index(0, drop=True)
                
                df[f'quantity_max_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).max().reset_index(0, drop=True)
                
                df[f'quantity_min_{window}'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=window, min_periods=1
                ).min().reset_index(0, drop=True)
            
            # Percentiles
            for percentile in [25, 50, 75, 90]:
                df[f'quantity_p{percentile}_30'] = df.groupby('product_id')['quantity_sold'].rolling(
                    window=30, min_periods=1
                ).quantile(percentile/100).reset_index(0, drop=True)
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características estadísticas: {str(e)}')
            return df
    
    def _add_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade características de mercado"""
        try:
            # Simular características de mercado
            df['market_volatility'] = np.random.normal(0.1, 0.05, len(df))
            df['competitor_price'] = df['unit_price'] * np.random.uniform(0.8, 1.2, len(df))
            df['market_demand'] = np.random.normal(100, 20, len(df))
            df['economic_indicator'] = np.random.normal(0, 1, len(df))
            
            # Características derivadas
            df['price_competitiveness'] = df['unit_price'] / df['competitor_price']
            df['demand_supply_ratio'] = df['market_demand'] / df['quantity_sold']
            
            return df
        except Exception as e:
            self.logger.error(f'Error añadiendo características de mercado: {str(e)}')
            return df
    
    def train_deep_learning_models(self, product_id: int = None) -> Dict:
        """Entrena modelos de deep learning"""
        try:
            # Preparar datos
            df = self.prepare_advanced_features(product_id)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para entrenar'}
            
            # Seleccionar características
            feature_columns = [col for col in df.columns if col not in [
                'date', 'product_id', 'product_name', 'category', 'quantity_sold', 'unit_price', 'total_amount'
            ]]
            
            X = df[feature_columns].fillna(0)
            y_regression = df['quantity_sold']
            y_classification = pd.cut(df['quantity_sold'], bins=3, labels=['low', 'medium', 'high'])
            
            # Dividir datos
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train_reg, y_test_reg = train_test_split(
                X, y_regression, test_size=0.2, random_state=42, shuffle=False
            )
            _, _, y_train_cls, y_test_cls = train_test_split(
                X, y_classification, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Normalizar características
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Selección de características
            feature_selector = SelectKBest(f_regression, k=min(20, len(feature_columns)))
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train_reg)
            X_test_selected = feature_selector.transform(X_test_scaled)
            
            # Entrenar modelos
            models = {}
            
            # 1. Red neuronal para regresión
            try:
                nn_regressor = MLPRegressor(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    alpha=0.001,
                    learning_rate='adaptive',
                    max_iter=1000,
                    random_state=42
                )
                nn_regressor.fit(X_train_selected, y_train_reg)
                y_pred_reg = nn_regressor.predict(X_test_selected)
                
                from sklearn.metrics import r2_score, mean_absolute_error
                r2 = r2_score(y_test_reg, y_pred_reg)
                mae = mean_absolute_error(y_test_reg, y_pred_reg)
                
                models['neural_network_regression'] = DeepLearningModel(
                    name='Neural Network Regression',
                    model_type='regression',
                    model=nn_regressor,
                    scaler=scaler,
                    feature_selector=feature_selector,
                    accuracy=r2,
                    trained_at=datetime.utcnow(),
                    features_used=feature_columns
                )
                
                self.logger.info(f'Modelo de regresión entrenado - R²: {r2:.3f}, MAE: {mae:.3f}')
                
            except Exception as e:
                self.logger.error(f'Error entrenando modelo de regresión: {str(e)}')
            
            # 2. Red neuronal para clasificación
            try:
                nn_classifier = MLPClassifier(
                    hidden_layer_sizes=(100, 50),
                    activation='relu',
                    solver='adam',
                    alpha=0.001,
                    learning_rate='adaptive',
                    max_iter=1000,
                    random_state=42
                )
                nn_classifier.fit(X_train_selected, y_train_cls)
                y_pred_cls = nn_classifier.predict(X_test_selected)
                
                from sklearn.metrics import accuracy_score, classification_report
                accuracy = accuracy_score(y_test_cls, y_pred_cls)
                
                models['neural_network_classification'] = DeepLearningModel(
                    name='Neural Network Classification',
                    model_type='classification',
                    model=nn_classifier,
                    scaler=scaler,
                    feature_selector=feature_selector,
                    accuracy=accuracy,
                    trained_at=datetime.utcnow(),
                    features_used=feature_columns
                )
                
                self.logger.info(f'Modelo de clasificación entrenado - Accuracy: {accuracy:.3f}')
                
            except Exception as e:
                self.logger.error(f'Error entrenando modelo de clasificación: {str(e)}')
            
            # 3. Detección de anomalías
            try:
                isolation_forest = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                isolation_forest.fit(X_train_selected)
                y_pred_anomaly = isolation_forest.predict(X_test_selected)
                
                anomaly_score = np.mean(y_pred_anomaly == -1)
                
                models['anomaly_detection'] = DeepLearningModel(
                    name='Anomaly Detection',
                    model_type='anomaly_detection',
                    model=isolation_forest,
                    scaler=scaler,
                    feature_selector=feature_selector,
                    accuracy=anomaly_score,
                    trained_at=datetime.utcnow(),
                    features_used=feature_columns
                )
                
                self.logger.info(f'Modelo de detección de anomalías entrenado - Anomaly Rate: {anomaly_score:.3f}')
                
            except Exception as e:
                self.logger.error(f'Error entrenando modelo de detección de anomalías: {str(e)}')
            
            # Guardar modelos
            self.models.update(models)
            self._save_models(models)
            
            return {
                'success': True,
                'models_trained': len(models),
                'models': {name: {
                    'accuracy': model.accuracy,
                    'model_type': model.model_type,
                    'trained_at': model.trained_at.isoformat()
                } for name, model in models.items()}
            }
            
        except Exception as e:
            self.logger.error(f'Error entrenando modelos de deep learning: {str(e)}')
            return {'error': str(e)}
    
    def generate_ai_insights(self, product_id: int = None) -> List[AIInsight]:
        """Genera insights usando IA"""
        try:
            insights = []
            
            # Preparar datos
            df = self.prepare_advanced_features(product_id, days_back=90)
            
            if df.empty:
                return insights
            
            # Insight 1: Patrones de demanda
            demand_insight = self._analyze_demand_patterns(df)
            if demand_insight:
                insights.append(demand_insight)
            
            # Insight 2: Anomalías de precio
            price_insight = self._analyze_price_anomalies(df)
            if price_insight:
                insights.append(price_insight)
            
            # Insight 3: Estacionalidad
            seasonality_insight = self._analyze_seasonality(df)
            if seasonality_insight:
                insights.append(seasonality_insight)
            
            # Insight 4: Competitividad
            competitiveness_insight = self._analyze_competitiveness(df)
            if competitiveness_insight:
                insights.append(competitiveness_insight)
            
            # Insight 5: Optimización de inventario
            inventory_insight = self._analyze_inventory_optimization(df)
            if inventory_insight:
                insights.append(inventory_insight)
            
            # Guardar insights
            self.insights_history.extend(insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f'Error generando insights de IA: {str(e)}')
            return []
    
    def _analyze_demand_patterns(self, df: pd.DataFrame) -> Optional[AIInsight]:
        """Analiza patrones de demanda"""
        try:
            if 'quantity_sold' not in df.columns:
                return None
            
            # Calcular tendencias
            df_sorted = df.sort_values('date')
            df_sorted['demand_trend'] = df_sorted['quantity_sold'].rolling(window=7).mean()
            
            # Detectar tendencias
            recent_trend = df_sorted['demand_trend'].tail(7).mean()
            historical_trend = df_sorted['demand_trend'].head(7).mean()
            
            trend_change = (recent_trend - historical_trend) / historical_trend if historical_trend > 0 else 0
            
            if abs(trend_change) > 0.2:  # Cambio significativo
                trend_direction = "creciente" if trend_change > 0 else "decreciente"
                confidence = min(abs(trend_change), 1.0)
                
                recommendations = []
                if trend_change > 0:
                    recommendations.extend([
                        "Considerar aumentar el stock de seguridad",
                        "Evaluar la capacidad de producción",
                        "Monitorear la satisfacción del cliente"
                    ])
                else:
                    recommendations.extend([
                        "Reducir el stock para evitar obsolescencia",
                        "Implementar promociones para estimular demanda",
                        "Analizar causas de la disminución"
                    ])
                
                return AIInsight(
                    type='demand_pattern',
                    title=f'Tendencia de Demanda {trend_direction.title()}',
                    description=f'La demanda muestra una tendencia {trend_direction} del {abs(trend_change)*100:.1f}% en las últimas semanas.',
                    confidence=confidence,
                    impact='high' if abs(trend_change) > 0.5 else 'medium',
                    recommendations=recommendations,
                    generated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error analizando patrones de demanda: {str(e)}')
            return None
    
    def _analyze_price_anomalies(self, df: pd.DataFrame) -> Optional[AIInsight]:
        """Analiza anomalías de precio"""
        try:
            if 'unit_price' not in df.columns:
                return None
            
            # Calcular estadísticas de precio
            price_mean = df['unit_price'].mean()
            price_std = df['unit_price'].std()
            price_threshold = price_mean + 2 * price_std
            
            # Detectar anomalías
            anomalies = df[df['unit_price'] > price_threshold]
            
            if len(anomalies) > 0:
                anomaly_rate = len(anomalies) / len(df)
                
                if anomaly_rate > 0.05:  # Más del 5% son anomalías
                    return AIInsight(
                        type='price_anomaly',
                        title='Anomalías de Precio Detectadas',
                        description=f'Se detectaron {len(anomalies)} anomalías de precio ({anomaly_rate*100:.1f}% de las transacciones).',
                        confidence=min(anomaly_rate * 2, 1.0),
                        impact='high' if anomaly_rate > 0.1 else 'medium',
                        recommendations=[
                            'Revisar la estrategia de precios',
                            'Verificar errores en el sistema de precios',
                            'Analizar la competitividad del mercado',
                            'Considerar ajustes de precios'
                        ],
                        generated_at=datetime.utcnow()
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error analizando anomalías de precio: {str(e)}')
            return None
    
    def _analyze_seasonality(self, df: pd.DataFrame) -> Optional[AIInsight]:
        """Analiza estacionalidad"""
        try:
            if 'month' not in df.columns or 'quantity_sold' not in df.columns:
                return None
            
            # Calcular ventas por mes
            monthly_sales = df.groupby('month')['quantity_sold'].mean()
            
            # Detectar estacionalidad
            max_month = monthly_sales.idxmax()
            min_month = monthly_sales.idxmin()
            seasonality_ratio = monthly_sales.max() / monthly_sales.min()
            
            if seasonality_ratio > 2.0:  # Estacionalidad significativa
                month_names = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }
                
                return AIInsight(
                    type='seasonality',
                    title='Patrón Estacional Detectado',
                    description=f'El producto muestra fuerte estacionalidad. Pico en {month_names[max_month]} y valle en {month_names[min_month]}.',
                    confidence=min((seasonality_ratio - 1) / 3, 1.0),
                    impact='high' if seasonality_ratio > 3.0 else 'medium',
                    recommendations=[
                        f'Ajustar inventario para el pico en {month_names[max_month]}',
                        f'Reducir stock en {month_names[min_month]}',
                        'Implementar promociones en meses de baja demanda',
                        'Planificar compras estacionales'
                    ],
                    generated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error analizando estacionalidad: {str(e)}')
            return None
    
    def _analyze_competitiveness(self, df: pd.DataFrame) -> Optional[AIInsight]:
        """Analiza competitividad"""
        try:
            if 'price_competitiveness' not in df.columns:
                return None
            
            avg_competitiveness = df['price_competitiveness'].mean()
            
            if avg_competitiveness > 1.2:  # Precio 20% más alto que competencia
                return AIInsight(
                    type='competitiveness',
                    title='Precio por Encima de la Competencia',
                    description=f'El precio promedio es {avg_competitiveness:.1f}x el precio de la competencia.',
                    confidence=min((avg_competitiveness - 1) / 2, 1.0),
                    impact='high' if avg_competitiveness > 1.5 else 'medium',
                    recommendations=[
                        'Revisar la estrategia de precios',
                        'Analizar el valor agregado del producto',
                        'Considerar reducciones de precio',
                        'Mejorar la diferenciación del producto'
                    ],
                    generated_at=datetime.utcnow()
                )
            elif avg_competitiveness < 0.8:  # Precio 20% más bajo que competencia
                return AIInsight(
                    type='competitiveness',
                    title='Oportunidad de Aumento de Precio',
                    description=f'El precio promedio es {avg_competitiveness:.1f}x el precio de la competencia.',
                    confidence=min((1 - avg_competitiveness) / 2, 1.0),
                    impact='medium',
                    recommendations=[
                        'Evaluar posibilidad de aumentar precios',
                        'Analizar la elasticidad de la demanda',
                        'Considerar aumentos graduales',
                        'Monitorear el impacto en las ventas'
                    ],
                    generated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error analizando competitividad: {str(e)}')
            return None
    
    def _analyze_inventory_optimization(self, df: pd.DataFrame) -> Optional[AIInsight]:
        """Analiza optimización de inventario"""
        try:
            if 'quantity_sold' not in df.columns:
                return None
            
            # Calcular métricas de inventario
            avg_demand = df['quantity_sold'].mean()
            demand_std = df['quantity_sold'].std()
            cv = demand_std / avg_demand if avg_demand > 0 else 0
            
            # Calcular EOQ simplificado
            # Asumiendo costos de ordenar y mantener
            ordering_cost = 100  # Costo de ordenar
            holding_cost = 0.02  # Costo de mantener por unidad por día
            
            eoq = np.sqrt(2 * avg_demand * ordering_cost / holding_cost)
            
            if cv > 0.5:  # Alta variabilidad
                return AIInsight(
                    type='inventory_optimization',
                    title='Alta Variabilidad en la Demanda',
                    description=f'La demanda muestra alta variabilidad (CV = {cv:.2f}). EOQ recomendado: {eoq:.0f} unidades.',
                    confidence=min(cv, 1.0),
                    impact='high' if cv > 1.0 else 'medium',
                    recommendations=[
                        f'Aumentar stock de seguridad a {avg_demand * 2:.0f} unidades',
                        'Implementar sistema de pronósticos más sofisticado',
                        'Considerar compras más frecuentes',
                        'Monitorear indicadores de demanda'
                    ],
                    generated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f'Error analizando optimización de inventario: {str(e)}')
            return None
    
    def predict_with_ai(self, product_id: int, days_ahead: int = 30) -> Dict:
        """Predice usando modelos de IA"""
        try:
            # Buscar mejor modelo de regresión
            best_model = None
            best_accuracy = 0
            
            for name, model in self.models.items():
                if model.model_type == 'regression' and model.accuracy > best_accuracy:
                    best_model = model
                    best_accuracy = model.accuracy
            
            if not best_model:
                return {'error': 'No hay modelo de regresión entrenado'}
            
            # Preparar datos para predicción
            df = self.prepare_advanced_features(product_id, days_back=30)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para predicción'}
            
            # Obtener características más recientes
            feature_columns = [col for col in df.columns if col not in [
                'date', 'product_id', 'product_name', 'category', 'quantity_sold', 'unit_price', 'total_amount'
            ]]
            
            last_features = df[feature_columns].iloc[-1:].fillna(0)
            
            # Preprocesar características
            features_scaled = best_model.scaler.transform(last_features)
            features_selected = best_model.feature_selector.transform(features_scaled)
            
            # Generar predicciones
            predictions = []
            dates = []
            
            for day in range(1, days_ahead + 1):
                # Crear características para el día futuro
                future_date = datetime.utcnow() + timedelta(days=day)
                
                # Actualizar características temporales
                future_features = features_selected.copy()
                
                # Predecir
                prediction = best_model.model.predict(future_features)[0]
                predictions.append(max(0, prediction))  # No permitir valores negativos
                dates.append(future_date.strftime('%Y-%m-%d'))
            
            return {
                'success': True,
                'product_id': product_id,
                'predictions': predictions,
                'dates': dates,
                'model_used': best_model.name,
                'model_accuracy': best_model.accuracy,
                'total_predicted_demand': sum(predictions),
                'average_daily_demand': sum(predictions) / len(predictions)
            }
            
        except Exception as e:
            self.logger.error(f'Error prediciendo con IA: {str(e)}')
            return {'error': str(e)}
    
    def detect_anomalies(self, product_id: int = None) -> Dict:
        """Detecta anomalías usando IA"""
        try:
            # Buscar modelo de detección de anomalías
            anomaly_model = None
            
            for name, model in self.models.items():
                if model.model_type == 'anomaly_detection':
                    anomaly_model = model
                    break
            
            if not anomaly_model:
                return {'error': 'No hay modelo de detección de anomalías entrenado'}
            
            # Preparar datos
            df = self.prepare_advanced_features(product_id, days_back=30)
            
            if df.empty:
                return {'error': 'No hay datos suficientes para detección de anomalías'}
            
            # Preparar características
            feature_columns = [col for col in df.columns if col not in [
                'date', 'product_id', 'product_name', 'category', 'quantity_sold', 'unit_price', 'total_amount'
            ]]
            
            X = df[feature_columns].fillna(0)
            
            # Preprocesar
            X_scaled = anomaly_model.scaler.transform(X)
            X_selected = anomaly_model.feature_selector.transform(X_scaled)
            
            # Detectar anomalías
            anomaly_scores = anomaly_model.model.decision_function(X_selected)
            anomaly_predictions = anomaly_model.model.predict(X_selected)
            
            # Identificar anomalías
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomalía detectada
                    anomalies.append({
                        'index': i,
                        'date': df.iloc[i]['date'].isoformat(),
                        'anomaly_score': float(score),
                        'quantity_sold': float(df.iloc[i]['quantity_sold']),
                        'unit_price': float(df.iloc[i]['unit_price'])
                    })
            
            return {
                'success': True,
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'model_used': anomaly_model.name,
                'total_records': len(df)
            }
            
        except Exception as e:
            self.logger.error(f'Error detectando anomalías: {str(e)}')
            return {'error': str(e)}
    
    def _save_models(self, models: Dict[str, DeepLearningModel]):
        """Guarda modelos entrenados"""
        try:
            for name, model in models.items():
                model_data = {
                    'name': model.name,
                    'model_type': model.model_type,
                    'accuracy': model.accuracy,
                    'trained_at': model.trained_at.isoformat(),
                    'features_used': model.features_used
                }
                
                # Guardar metadatos
                metadata_path = os.path.join(self.models_dir, f"{name}_metadata.json")
                with open(metadata_path, 'w') as f:
                    json.dump(model_data, f, indent=2)
                
                # Guardar modelo
                model_path = os.path.join(self.models_dir, f"{name}_model.pkl")
                with open(model_path, 'wb') as f:
                    pickle.dump(model.model, f)
                
                # Guardar scaler
                scaler_path = os.path.join(self.models_dir, f"{name}_scaler.pkl")
                with open(scaler_path, 'wb') as f:
                    pickle.dump(model.scaler, f)
                
                # Guardar feature selector
                selector_path = os.path.join(self.models_dir, f"{name}_selector.pkl")
                with open(selector_path, 'wb') as f:
                    pickle.dump(model.feature_selector, f)
                
                self.logger.info(f'Modelo {name} guardado exitosamente')
                
        except Exception as e:
            self.logger.error(f'Error guardando modelos: {str(e)}')
    
    def get_model_performance(self) -> Dict:
        """Obtiene rendimiento de los modelos"""
        try:
            performance = {}
            
            for name, model in self.models.items():
                performance[name] = {
                    'name': model.name,
                    'type': model.model_type,
                    'accuracy': model.accuracy,
                    'trained_at': model.trained_at.isoformat(),
                    'features_count': len(model.features_used)
                }
            
            return {
                'success': True,
                'models': performance,
                'total_models': len(self.models)
            }
            
        except Exception as e:
            self.logger.error(f'Error obteniendo rendimiento de modelos: {str(e)}')
            return {'error': str(e)}
    
    def get_ai_insights_history(self) -> List[Dict]:
        """Obtiene historial de insights de IA"""
        try:
            insights_data = []
            
            for insight in self.insights_history[-50:]:  # Últimos 50 insights
                insights_data.append({
                    'type': insight.type,
                    'title': insight.title,
                    'description': insight.description,
                    'confidence': insight.confidence,
                    'impact': insight.impact,
                    'recommendations': insight.recommendations,
                    'generated_at': insight.generated_at.isoformat()
                })
            
            return insights_data
            
        except Exception as e:
            self.logger.error(f'Error obteniendo historial de insights: {str(e)}')
            return []

# Instancia global del servicio de IA
advanced_ai_service = AdvancedAIService()



