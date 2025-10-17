# Guía de Analytics Predictivos y Forecasting para Facebook Ads
## Predicción de Performance y Optimización Basada en Datos

---

## 1. Introducción a los Analytics Predictivos

Esta guía proporciona técnicas avanzadas de analytics predictivos y forecasting para Facebook Ads, incluyendo modelos de machine learning, análisis de tendencias, predicción de performance y optimización basada en datos. Está diseñada para profesionales que buscan anticipar resultados y optimizar proactivamente.

### Objetivos de los Analytics Predictivos
- Predecir performance futura de campañas
- Identificar tendencias y patrones
- Optimizar proactivamente basándose en predicciones
- Reducir riesgos y maximizar oportunidades
- Mejorar ROI a través de insights predictivos

---

## 2. Fundamentos de Analytics Predictivos

### 2.1 Tipos de Predicciones

**Predicciones de Performance:**
```
CTR: Predicción de click-through rate
CPC: Predicción de cost per click
CPA: Predicción de cost per acquisition
ROAS: Predicción de return on ad spend
Conversions: Predicción de número de conversiones
```

**Predicciones de Comportamiento:**
```
Audience Behavior: Comportamiento de audiencias
Seasonal Trends: Tendencias estacionales
Market Trends: Tendencias de mercado
Competitive Landscape: Panorama competitivo
```

**Predicciones de Optimización:**
```
Budget Allocation: Asignación óptima de presupuesto
Bidding Strategy: Estrategia óptima de bidding
Creative Performance: Performance de creativos
Audience Performance: Performance de audiencias
```

### 2.2 Metodologías de Predicción

**Time Series Analysis:**
```
ARIMA: AutoRegressive Integrated Moving Average
Exponential Smoothing: Suavizado exponencial
Seasonal Decomposition: Descomposición estacional
Trend Analysis: Análisis de tendencias
```

**Machine Learning:**
```
Regression: Regresión lineal y no lineal
Random Forest: Bosques aleatorios
Neural Networks: Redes neuronales
Gradient Boosting: Gradient boosting
```

**Statistical Methods:**
```
Correlation Analysis: Análisis de correlación
Regression Analysis: Análisis de regresión
Hypothesis Testing: Pruebas de hipótesis
Confidence Intervals: Intervalos de confianza
```

---

## 3. Modelos de Predicción

### 3.1 Modelo de Predicción de CTR

**Implementación en Python:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class CTRPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_importance = None
        
    def prepare_data(self, campaign_data):
        """Preparar datos para el modelo"""
        # Extraer características
        features = []
        targets = []
        
        for campaign in campaign_data:
            feature_vector = [
                campaign['budget'],
                campaign['audience_size'],
                campaign['creative_count'],
                campaign['day_of_week'],
                campaign['hour_of_day'],
                campaign['seasonality_factor'],
                campaign['competition_level'],
                campaign['relevance_score'],
                campaign['creative_quality_score']
            ]
            
            features.append(feature_vector)
            targets.append(campaign['ctr'])
        
        return np.array(features), np.array(targets)
    
    def train_model(self, X, y):
        """Entrenar modelo de predicción"""
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrenar modelo
        self.model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"MSE: {mse:.4f}")
        print(f"R² Score: {r2:.4f}")
        
        # Calcular importancia de características
        self.feature_importance = pd.DataFrame({
            'feature': [
                'budget', 'audience_size', 'creative_count', 'day_of_week',
                'hour_of_day', 'seasonality_factor', 'competition_level',
                'relevance_score', 'creative_quality_score'
            ],
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return r2
    
    def predict_ctr(self, campaign_features):
        """Predecir CTR de una campaña"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        prediction = self.model.predict([campaign_features])
        return prediction[0]
    
    def get_feature_importance(self):
        """Obtener importancia de características"""
        return self.feature_importance
    
    def plot_feature_importance(self):
        """Visualizar importancia de características"""
        if self.feature_importance is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        plt.figure(figsize=(10, 6))
        plt.barh(self.feature_importance['feature'], self.feature_importance['importance'])
        plt.xlabel('Importance')
        plt.title('Feature Importance for CTR Prediction')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

# Uso del modelo
if __name__ == "__main__":
    # Crear predictor
    predictor = CTRPredictor()
    
    # Preparar datos (ejemplo)
    campaign_data = [
        {
            'budget': 1000,
            'audience_size': 100000,
            'creative_count': 3,
            'day_of_week': 1,
            'hour_of_day': 14,
            'seasonality_factor': 1.2,
            'competition_level': 0.7,
            'relevance_score': 8.5,
            'creative_quality_score': 9.0,
            'ctr': 2.5
        },
        # ... más datos
    ]
    
    # Preparar datos
    X, y = predictor.prepare_data(campaign_data)
    
    # Entrenar modelo
    score = predictor.train_model(X, y)
    
    # Predecir CTR
    new_campaign = [1000, 150000, 4, 2, 16, 1.1, 0.8, 9.0, 8.5]
    predicted_ctr = predictor.predict_ctr(new_campaign)
    
    print(f"Predicted CTR: {predicted_ctr:.2f}%")
```

### 3.2 Modelo de Predicción de ROAS

**Implementación Avanzada:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import xgboost as xgb
from datetime import datetime, timedelta

class ROASPredictor:
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def extract_features(self, campaign_data):
        """Extraer características avanzadas"""
        features = []
        
        for campaign in campaign_data:
            # Características básicas
            basic_features = [
                campaign['budget'],
                campaign['audience_size'],
                campaign['creative_count'],
                campaign['campaign_age'],
                campaign['relevance_score']
            ]
            
            # Características de performance histórica
            historical_features = [
                campaign['avg_ctr_30d'],
                campaign['avg_cpc_30d'],
                campaign['avg_cpm_30d'],
                campaign['conversion_rate_30d'],
                campaign['audience_quality_score']
            ]
            
            # Características de mercado
            market_features = [
                campaign['competition_index'],
                campaign['seasonality_factor'],
                campaign['market_trend'],
                campaign['industry_benchmark']
            ]
            
            # Características de timing
            timing_features = [
                campaign['day_of_week'],
                campaign['hour_of_day'],
                campaign['month'],
                campaign['quarter']
            ]
            
            # Combinar todas las características
            all_features = (
                basic_features + 
                historical_features + 
                market_features + 
                timing_features
            )
            
            features.append(all_features)
        
        return np.array(features)
    
    def prepare_data(self, campaign_data):
        """Preparar datos para el modelo"""
        X = self.extract_features(campaign_data)
        y = np.array([campaign['roas'] for campaign in campaign_data])
        
        # Normalizar características
        X_scaled = self.scaler.fit_transform(X)
        
        # Guardar nombres de características
        self.feature_names = [
            'budget', 'audience_size', 'creative_count', 'campaign_age', 'relevance_score',
            'avg_ctr_30d', 'avg_cpc_30d', 'avg_cpm_30d', 'conversion_rate_30d', 'audience_quality_score',
            'competition_index', 'seasonality_factor', 'market_trend', 'industry_benchmark',
            'day_of_week', 'hour_of_day', 'month', 'quarter'
        ]
        
        return X_scaled, y
    
    def train_model(self, X, y):
        """Entrenar modelo de predicción"""
        # Validación cruzada
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='r2')
        print(f"Cross-validation R² scores: {cv_scores}")
        print(f"Mean CV R² score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Entrenar modelo final
        self.model.fit(X, y)
        
        # Calcular importancia de características
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def predict_roas(self, campaign_features):
        """Predecir ROAS de una campaña"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Normalizar características
        features_scaled = self.scaler.transform([campaign_features])
        
        # Predecir
        prediction = self.model.predict(features_scaled)
        return prediction[0]
    
    def predict_confidence_interval(self, campaign_features, confidence=0.95):
        """Predecir ROAS con intervalo de confianza"""
        # Usar predicciones de múltiples árboles para estimar incertidumbre
        predictions = []
        
        for tree in self.model.estimators_:
            pred = tree.predict(self.scaler.transform([campaign_features]))
            predictions.append(pred[0])
        
        predictions = np.array(predictions)
        
        # Calcular estadísticas
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        # Calcular intervalo de confianza
        alpha = 1 - confidence
        lower_bound = mean_pred - 1.96 * std_pred
        upper_bound = mean_pred + 1.96 * std_pred
        
        return {
            'prediction': mean_pred,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence': confidence
        }

# Uso del modelo
if __name__ == "__main__":
    # Crear predictor
    predictor = ROASPredictor()
    
    # Preparar datos (ejemplo)
    campaign_data = [
        {
            'budget': 5000,
            'audience_size': 500000,
            'creative_count': 5,
            'campaign_age': 30,
            'relevance_score': 8.5,
            'avg_ctr_30d': 2.3,
            'avg_cpc_30d': 1.8,
            'avg_cpm_30d': 12.5,
            'conversion_rate_30d': 3.2,
            'audience_quality_score': 8.0,
            'competition_index': 0.7,
            'seasonality_factor': 1.1,
            'market_trend': 0.05,
            'industry_benchmark': 3.5,
            'day_of_week': 1,
            'hour_of_day': 14,
            'month': 6,
            'quarter': 2,
            'roas': 4.2
        },
        # ... más datos
    ]
    
    # Preparar datos
    X, y = predictor.prepare_data(campaign_data)
    
    # Entrenar modelo
    feature_importance = predictor.train_model(X, y)
    
    # Predecir ROAS
    new_campaign = [
        6000, 600000, 6, 45, 9.0, 2.5, 1.6, 11.8, 3.5, 8.5,
        0.8, 1.2, 0.08, 3.8, 2, 16, 7, 3
    ]
    
    prediction = predictor.predict_roas(new_campaign)
    confidence_interval = predictor.predict_confidence_interval(new_campaign)
    
    print(f"Predicted ROAS: {prediction:.2f}")
    print(f"Confidence Interval: {confidence_interval['lower_bound']:.2f} - {confidence_interval['upper_bound']:.2f}")
```

### 3.3 Modelo de Predicción de Tendencias

**Análisis de Tendencias Temporales:**
```python
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class TrendPredictor:
    def __init__(self):
        self.models = {}
        self.trend_data = None
        
    def prepare_time_series_data(self, campaign_data):
        """Preparar datos de serie temporal"""
        # Convertir a DataFrame
        df = pd.DataFrame(campaign_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # Resample a frecuencia diaria
        df_daily = df.resample('D').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'conversions': 'sum',
            'ctr': 'mean',
            'cpc': 'mean',
            'cpa': 'mean',
            'roas': 'mean'
        }).fillna(method='ffill')
        
        return df_daily
    
    def decompose_trends(self, data, metric='roas'):
        """Descomponer tendencias estacionales"""
        # Descomposición estacional
        decomposition = seasonal_decompose(
            data[metric], 
            model='multiplicative', 
            period=7  # Semanal
        )
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed
        }
    
    def fit_arima_model(self, data, metric='roas'):
        """Ajustar modelo ARIMA"""
        # Ajustar modelo ARIMA
        model = ARIMA(data[metric], order=(1, 1, 1))
        fitted_model = model.fit()
        
        return fitted_model
    
    def fit_exponential_smoothing(self, data, metric='roas'):
        """Ajustar suavizado exponencial"""
        # Ajustar modelo de suavizado exponencial
        model = ExponentialSmoothing(
            data[metric],
            trend='add',
            seasonal='add',
            seasonal_periods=7
        )
        fitted_model = model.fit()
        
        return fitted_model
    
    def predict_future_trends(self, data, metric='roas', days=30):
        """Predecir tendencias futuras"""
        # Ajustar modelos
        arima_model = self.fit_arima_model(data, metric)
        exp_model = self.fit_exponential_smoothing(data, metric)
        
        # Predecir con ARIMA
        arima_forecast = arima_model.forecast(steps=days)
        arima_ci = arima_model.get_forecast(steps=days).conf_int()
        
        # Predecir con suavizado exponencial
        exp_forecast = exp_model.forecast(steps=days)
        
        # Combinar predicciones
        combined_forecast = (arima_forecast + exp_forecast) / 2
        
        # Crear DataFrame de predicciones
        future_dates = pd.date_range(
            start=data.index[-1] + timedelta(days=1),
            periods=days,
            freq='D'
        )
        
        predictions = pd.DataFrame({
            'date': future_dates,
            'arima_forecast': arima_forecast,
            'exp_forecast': exp_forecast,
            'combined_forecast': combined_forecast,
            'arima_lower': arima_ci.iloc[:, 0],
            'arima_upper': arima_ci.iloc[:, 1]
        })
        
        return predictions
    
    def plot_trends(self, data, predictions, metric='roas'):
        """Visualizar tendencias y predicciones"""
        plt.figure(figsize=(15, 8))
        
        # Datos históricos
        plt.plot(data.index, data[metric], label='Historical Data', color='blue')
        
        # Predicciones
        plt.plot(predictions['date'], predictions['combined_forecast'], 
                label='Combined Forecast', color='red', linestyle='--')
        plt.plot(predictions['date'], predictions['arima_forecast'], 
                label='ARIMA Forecast', color='green', linestyle=':')
        plt.plot(predictions['date'], predictions['exp_forecast'], 
                label='Exponential Smoothing', color='orange', linestyle=':')
        
        # Intervalos de confianza
        plt.fill_between(predictions['date'], 
                        predictions['arima_lower'], 
                        predictions['arima_upper'], 
                        alpha=0.3, color='gray', label='Confidence Interval')
        
        plt.title(f'{metric.upper()} Trend Analysis and Forecast')
        plt.xlabel('Date')
        plt.ylabel(metric.upper())
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def analyze_seasonality(self, data, metric='roas'):
        """Analizar estacionalidad"""
        # Descomposición estacional
        decomposition = self.decompose_trends(data, metric)
        
        # Análisis de estacionalidad
        seasonal_analysis = {
            'weekly_pattern': decomposition['seasonal'].groupby(
                decomposition['seasonal'].index.dayofweek
            ).mean(),
            'monthly_pattern': decomposition['seasonal'].groupby(
                decomposition['seasonal'].index.month
            ).mean(),
            'trend_direction': 'increasing' if decomposition['trend'].iloc[-1] > decomposition['trend'].iloc[0] else 'decreasing',
            'seasonal_strength': np.std(decomposition['seasonal']) / np.mean(decomposition['observed'])
        }
        
        return seasonal_analysis

# Uso del modelo
if __name__ == "__main__":
    # Crear predictor
    predictor = TrendPredictor()
    
    # Preparar datos (ejemplo)
    campaign_data = [
        {'date': '2024-01-01', 'impressions': 10000, 'clicks': 200, 'spend': 500, 'conversions': 10, 'ctr': 2.0, 'cpc': 2.5, 'cpa': 50, 'roas': 4.0},
        # ... más datos históricos
    ]
    
    # Preparar datos de serie temporal
    time_series_data = predictor.prepare_time_series_data(campaign_data)
    
    # Predecir tendencias futuras
    predictions = predictor.predict_future_trends(time_series_data, metric='roas', days=30)
    
    # Analizar estacionalidad
    seasonality = predictor.analyze_seasonality(time_series_data, metric='roas')
    
    # Visualizar tendencias
    predictor.plot_trends(time_series_data, predictions, metric='roas')
    
    print("Seasonality Analysis:")
    print(f"Weekly Pattern: {seasonality['weekly_pattern']}")
    print(f"Trend Direction: {seasonality['trend_direction']}")
    print(f"Seasonal Strength: {seasonality['seasonal_strength']:.3f}")
```

---

## 4. Forecasting Avanzado

### 4.1 Predicción de Presupuestos Óptimos

**Optimizador de Presupuestos:**
```python
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

class BudgetOptimizer:
    def __init__(self):
        self.models = {}
        self.budget_constraints = {}
        
    def train_performance_models(self, historical_data):
        """Entrenar modelos de performance por campaña"""
        for campaign_id in historical_data['campaign_id'].unique():
            campaign_data = historical_data[historical_data['campaign_id'] == campaign_id]
            
            # Preparar características
            X = campaign_data[['budget', 'day_of_week', 'month', 'seasonality_factor']].values
            y = campaign_data['roas'].values
            
            # Entrenar modelo
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            self.models[campaign_id] = model
    
    def predict_campaign_performance(self, campaign_id, budget, day_of_week, month, seasonality_factor):
        """Predecir performance de una campaña"""
        if campaign_id not in self.models:
            return 0
        
        features = np.array([[budget, day_of_week, month, seasonality_factor]])
        prediction = self.models[campaign_id].predict(features)
        return prediction[0]
    
    def objective_function(self, budgets, campaign_ids, day_of_week, month, seasonality_factor):
        """Función objetivo para optimización"""
        total_roas = 0
        
        for i, campaign_id in enumerate(campaign_ids):
            roas = self.predict_campaign_performance(
                campaign_id, budgets[i], day_of_week, month, seasonality_factor
            )
            total_roas += roas * budgets[i]  # ROAS * Budget = Revenue
        
        return -total_roas  # Minimizar negativo = maximizar
    
    def optimize_budgets(self, campaign_ids, total_budget, day_of_week, month, seasonality_factor):
        """Optimizar distribución de presupuestos"""
        n_campaigns = len(campaign_ids)
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}  # Suma = presupuesto total
        ]
        
        # Límites (mínimo 10% del presupuesto total por campaña)
        bounds = [(total_budget * 0.1, total_budget * 0.9) for _ in range(n_campaigns)]
        
        # Presupuesto inicial (distribución uniforme)
        x0 = [total_budget / n_campaigns] * n_campaigns
        
        # Optimizar
        result = minimize(
            self.objective_function,
            x0,
            args=(campaign_ids, day_of_week, month, seasonality_factor),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x, result.fun
    
    def forecast_optimal_budgets(self, campaign_ids, total_budget, days=30):
        """Predecir presupuestos óptimos para los próximos días"""
        forecasts = []
        
        for day in range(days):
            date = pd.Timestamp.now() + pd.Timedelta(days=day)
            day_of_week = date.dayofweek
            month = date.month
            
            # Calcular factor estacional (ejemplo)
            seasonality_factor = 1.0 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365)
            
            # Optimizar presupuestos
            optimal_budgets, total_roas = self.optimize_budgets(
                campaign_ids, total_budget, day_of_week, month, seasonality_factor
            )
            
            forecasts.append({
                'date': date,
                'day_of_week': day_of_week,
                'month': month,
                'seasonality_factor': seasonality_factor,
                'optimal_budgets': optimal_budgets,
                'predicted_roas': -total_roas,
                'campaign_ids': campaign_ids
            })
        
        return pd.DataFrame(forecasts)
    
    def plot_budget_optimization(self, forecasts):
        """Visualizar optimización de presupuestos"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Gráfico de presupuestos óptimos
        for i, campaign_id in enumerate(forecasts['campaign_ids'].iloc[0]):
            budgets = [forecast['optimal_budgets'][i] for forecast in forecasts.to_dict('records')]
            ax1.plot(forecasts['date'], budgets, label=f'Campaign {campaign_id}', marker='o')
        
        ax1.set_title('Optimal Budget Allocation Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Budget')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico de ROAS predicho
        ax2.plot(forecasts['date'], forecasts['predicted_roas'], 
                color='red', marker='o', linewidth=2)
        ax2.set_title('Predicted ROAS Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('ROAS')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Uso del optimizador
if __name__ == "__main__":
    # Crear optimizador
    optimizer = BudgetOptimizer()
    
    # Preparar datos históricos (ejemplo)
    historical_data = pd.DataFrame([
        {'campaign_id': 'C1', 'budget': 1000, 'day_of_week': 1, 'month': 6, 'seasonality_factor': 1.1, 'roas': 4.2},
        {'campaign_id': 'C1', 'budget': 1200, 'day_of_week': 2, 'month': 6, 'seasonality_factor': 1.1, 'roas': 4.5},
        {'campaign_id': 'C2', 'budget': 800, 'day_of_week': 1, 'month': 6, 'seasonality_factor': 1.1, 'roas': 3.8},
        {'campaign_id': 'C2', 'budget': 1000, 'day_of_week': 2, 'month': 6, 'seasonality_factor': 1.1, 'roas': 4.1},
        # ... más datos
    ])
    
    # Entrenar modelos
    optimizer.train_performance_models(historical_data)
    
    # Optimizar presupuestos
    campaign_ids = ['C1', 'C2']
    total_budget = 5000
    
    optimal_budgets, total_roas = optimizer.optimize_budgets(
        campaign_ids, total_budget, day_of_week=1, month=6, seasonality_factor=1.1
    )
    
    print(f"Optimal Budgets: {optimal_budgets}")
    print(f"Predicted Total ROAS: {-total_roas:.2f}")
    
    # Predecir presupuestos óptimos
    forecasts = optimizer.forecast_optimal_budgets(campaign_ids, total_budget, days=30)
    
    # Visualizar resultados
    optimizer.plot_budget_optimization(forecasts)
```

### 4.2 Predicción de Competencia

**Analizador de Competencia:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class CompetitionAnalyzer:
    def __init__(self):
        self.competition_models = {}
        self.market_trends = {}
        
    def analyze_competition_patterns(self, market_data):
        """Analizar patrones de competencia"""
        # Análisis de clusters de competencia
        kmeans = KMeans(n_clusters=3, random_state=42)
        competition_clusters = kmeans.fit_predict(
            market_data[['cpm', 'ctr', 'competition_level']].values
        )
        
        # Análisis de anomalías
        isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        anomalies = isolation_forest.fit_predict(
            market_data[['cpm', 'ctr', 'competition_level']].values
        )
        
        # Identificar patrones
        patterns = {
            'high_competition': market_data[competition_clusters == 0],
            'medium_competition': market_data[competition_clusters == 1],
            'low_competition': market_data[competition_clusters == 2],
            'anomalies': market_data[anomalies == -1]
        }
        
        return patterns
    
    def predict_competition_trends(self, historical_data, days=30):
        """Predecir tendencias de competencia"""
        # Análisis de tendencias temporales
        trends = {}
        
        for metric in ['cpm', 'ctr', 'competition_level']:
            # Calcular tendencia
            values = historical_data[metric].values
            x = np.arange(len(values))
            
            # Regresión lineal para tendencia
            coeffs = np.polyfit(x, values, 1)
            trend_slope = coeffs[0]
            
            # Predicción futura
            future_x = np.arange(len(values), len(values) + days)
            future_values = np.polyval(coeffs, future_x)
            
            trends[metric] = {
                'current_value': values[-1],
                'trend_slope': trend_slope,
                'future_values': future_values,
                'trend_direction': 'increasing' if trend_slope > 0 else 'decreasing'
            }
        
        return trends
    
    def identify_opportunities(self, market_data, campaign_performance):
        """Identificar oportunidades de mercado"""
        opportunities = []
        
        # Análisis de gaps de mercado
        market_avg_cpm = market_data['cpm'].mean()
        market_avg_ctr = market_data['ctr'].mean()
        
        campaign_avg_cpm = campaign_performance['cpm'].mean()
        campaign_avg_ctr = campaign_performance['ctr'].mean()
        
        # Oportunidades de costo
        if campaign_avg_cpm < market_avg_cpm * 0.8:
            opportunities.append({
                'type': 'cost_advantage',
                'description': 'CPM significantly below market average',
                'advantage': (market_avg_cpm - campaign_avg_cpm) / market_avg_cpm * 100,
                'recommendation': 'Increase budget to capture more market share'
            })
        
        # Oportunidades de performance
        if campaign_avg_ctr > market_avg_ctr * 1.2:
            opportunities.append({
                'type': 'performance_advantage',
                'description': 'CTR significantly above market average',
                'advantage': (campaign_avg_ctr - market_avg_ctr) / market_avg_ctr * 100,
                'recommendation': 'Scale successful campaigns'
            })
        
        # Oportunidades de timing
        time_analysis = self.analyze_optimal_timing(market_data)
        if time_analysis['optimal_hours']:
            opportunities.append({
                'type': 'timing_opportunity',
                'description': 'Optimal timing identified',
                'optimal_hours': time_analysis['optimal_hours'],
                'recommendation': 'Adjust campaign scheduling'
            })
        
        return opportunities
    
    def analyze_optimal_timing(self, market_data):
        """Analizar timing óptimo"""
        # Análisis por hora del día
        hourly_performance = market_data.groupby('hour').agg({
            'ctr': 'mean',
            'cpm': 'mean',
            'competition_level': 'mean'
        }).reset_index()
        
        # Identificar horas óptimas (alto CTR, bajo CPM, baja competencia)
        hourly_performance['score'] = (
            hourly_performance['ctr'] / hourly_performance['ctr'].max() +
            (1 - hourly_performance['cpm'] / hourly_performance['cpm'].max()) +
            (1 - hourly_performance['competition_level'] / hourly_performance['competition_level'].max())
        ) / 3
        
        optimal_hours = hourly_performance.nlargest(3, 'score')['hour'].tolist()
        
        return {
            'optimal_hours': optimal_hours,
            'hourly_analysis': hourly_performance
        }
    
    def forecast_market_conditions(self, historical_data, days=30):
        """Predecir condiciones de mercado"""
        # Análisis de tendencias
        trends = self.predict_competition_trends(historical_data, days)
        
        # Predicción de condiciones futuras
        future_conditions = []
        
        for day in range(days):
            date = pd.Timestamp.now() + pd.Timedelta(days=day)
            
            conditions = {
                'date': date,
                'predicted_cpm': trends['cpm']['future_values'][day],
                'predicted_ctr': trends['ctr']['future_values'][day],
                'predicted_competition': trends['competition_level']['future_values'][day],
                'market_condition': self.classify_market_condition(
                    trends['cpm']['future_values'][day],
                    trends['ctr']['future_values'][day],
                    trends['competition_level']['future_values'][day]
                )
            }
            
            future_conditions.append(conditions)
        
        return pd.DataFrame(future_conditions)
    
    def classify_market_condition(self, cpm, ctr, competition_level):
        """Clasificar condición de mercado"""
        if cpm < 10 and ctr > 2.0 and competition_level < 0.5:
            return 'Favorable'
        elif cpm > 20 or ctr < 1.0 or competition_level > 0.8:
            return 'Challenging'
        else:
            return 'Moderate'
    
    def plot_competition_analysis(self, market_data, forecasts):
        """Visualizar análisis de competencia"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # CPM histórico y predicho
        ax1.plot(market_data.index, market_data['cpm'], label='Historical CPM', color='blue')
        ax1.plot(forecasts['date'], forecasts['predicted_cpm'], 
                label='Predicted CPM', color='red', linestyle='--')
        ax1.set_title('CPM Trends')
        ax1.set_ylabel('CPM')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # CTR histórico y predicho
        ax2.plot(market_data.index, market_data['ctr'], label='Historical CTR', color='blue')
        ax2.plot(forecasts['date'], forecasts['predicted_ctr'], 
                label='Predicted CTR', color='red', linestyle='--')
        ax2.set_title('CTR Trends')
        ax2.set_ylabel('CTR (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Nivel de competencia
        ax3.plot(market_data.index, market_data['competition_level'], 
                label='Historical Competition', color='blue')
        ax3.plot(forecasts['date'], forecasts['predicted_competition'], 
                label='Predicted Competition', color='red', linestyle='--')
        ax3.set_title('Competition Level')
        ax3.set_ylabel('Competition Level')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Condiciones de mercado
        condition_colors = {'Favorable': 'green', 'Moderate': 'yellow', 'Challenging': 'red'}
        colors = [condition_colors[condition] for condition in forecasts['market_condition']]
        ax4.scatter(forecasts['date'], range(len(forecasts)), c=colors, alpha=0.7)
        ax4.set_title('Market Conditions Forecast')
        ax4.set_ylabel('Day')
        ax4.set_xlabel('Date')
        
        plt.tight_layout()
        plt.show()

# Uso del analizador
if __name__ == "__main__":
    # Crear analizador
    analyzer = CompetitionAnalyzer()
    
    # Preparar datos de mercado (ejemplo)
    market_data = pd.DataFrame([
        {'date': '2024-01-01', 'cpm': 12.5, 'ctr': 2.1, 'competition_level': 0.6, 'hour': 14},
        # ... más datos históricos
    ])
    
    # Analizar patrones de competencia
    patterns = analyzer.analyze_competition_patterns(market_data)
    
    # Predecir tendencias de competencia
    trends = analyzer.predict_competition_trends(market_data, days=30)
    
    # Identificar oportunidades
    campaign_performance = pd.DataFrame([
        {'cpm': 10.5, 'ctr': 2.8, 'competition_level': 0.4}
    ])
    opportunities = analyzer.identify_opportunities(market_data, campaign_performance)
    
    # Predecir condiciones de mercado
    forecasts = analyzer.forecast_market_conditions(market_data, days=30)
    
    # Visualizar análisis
    analyzer.plot_competition_analysis(market_data, forecasts)
    
    print("Competition Analysis Results:")
    print(f"Market Trends: {trends}")
    print(f"Opportunities: {opportunities}")
    print(f"Future Conditions: {forecasts['market_condition'].value_counts()}")
```

---

## 5. Herramientas de Analytics Predictivos

### 5.1 Dashboard de Predicciones

**Dashboard Interactivo:**
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

class PredictiveDashboard:
    def __init__(self):
        self.data = None
        self.models = {}
        
    def load_data(self, data_source):
        """Cargar datos para el dashboard"""
        self.data = pd.read_csv(data_source)
        return self.data
    
    def create_performance_forecast_chart(self, metric='roas', days=30):
        """Crear gráfico de predicción de performance"""
        # Simular predicción (en implementación real, usar modelos entrenados)
        dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        historical = np.random.normal(4.0, 0.5, 30)
        predicted = np.random.normal(4.2, 0.3, days)
        
        fig = go.Figure()
        
        # Datos históricos
        fig.add_trace(go.Scatter(
            x=dates[:30],
            y=historical,
            mode='lines',
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Predicciones
        fig.add_trace(go.Scatter(
            x=dates,
            y=predicted,
            mode='lines',
            name='Predicted',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=f'{metric.upper()} Forecast',
            xaxis_title='Date',
            yaxis_title=metric.upper(),
            hovermode='x unified'
        )
        
        return fig
    
    def create_budget_optimization_chart(self, campaigns, total_budget):
        """Crear gráfico de optimización de presupuestos"""
        # Simular optimización de presupuestos
        optimal_budgets = np.random.dirichlet(np.ones(len(campaigns))) * total_budget
        
        fig = go.Figure(data=[
            go.Pie(
                labels=campaigns,
                values=optimal_budgets,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title="Optimal Budget Allocation",
            annotations=[dict(text='Budget', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    def create_competition_analysis_chart(self):
        """Crear gráfico de análisis de competencia"""
        # Simular datos de competencia
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=60, freq='D')
        cpm = np.random.normal(15, 3, 60)
        competition = np.random.normal(0.6, 0.1, 60)
        
        fig = go.Figure()
        
        # CPM
        fig.add_trace(go.Scatter(
            x=dates,
            y=cpm,
            mode='lines',
            name='CPM',
            yaxis='y'
        ))
        
        # Nivel de competencia
        fig.add_trace(go.Scatter(
            x=dates,
            y=competition,
            mode='lines',
            name='Competition Level',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Market Competition Analysis',
            xaxis_title='Date',
            yaxis=dict(title='CPM', side='left'),
            yaxis2=dict(title='Competition Level', side='right', overlaying='y'),
            hovermode='x unified'
        )
        
        return fig
    
    def run_dashboard(self):
        """Ejecutar dashboard"""
        st.set_page_config(page_title="Facebook Ads Predictive Analytics", layout="wide")
        
        st.title("Facebook Ads Predictive Analytics Dashboard")
        
        # Sidebar
        st.sidebar.header("Configuration")
        metric = st.sidebar.selectbox("Select Metric", ["ROAS", "CTR", "CPA", "Conversions"])
        forecast_days = st.sidebar.slider("Forecast Days", 7, 90, 30)
        
        # Main content
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{metric} Forecast")
            forecast_chart = self.create_performance_forecast_chart(metric.lower(), forecast_days)
            st.plotly_chart(forecast_chart, use_container_width=True)
            
            st.subheader("Budget Optimization")
            campaigns = ["Campaign A", "Campaign B", "Campaign C", "Campaign D"]
            total_budget = 10000
            budget_chart = self.create_budget_optimization_chart(campaigns, total_budget)
            st.plotly_chart(budget_chart, use_container_width=True)
        
        with col2:
            st.subheader("Competition Analysis")
            competition_chart = self.create_competition_analysis_chart()
            st.plotly_chart(competition_chart, use_container_width=True)
            
            st.subheader("Key Insights")
            st.info("""
            **Performance Insights:**
            - ROAS is predicted to increase by 5% over the next 30 days
            - Campaign A shows the highest potential for budget increase
            - Competition levels are expected to decrease in the next week
            
            **Recommendations:**
            - Increase budget for Campaign A by 20%
            - Pause Campaign C due to declining performance
            - Adjust bidding strategy for Campaign B
            """)
        
        # Metrics
        st.subheader("Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current ROAS", "4.2", "0.3")
        with col2:
            st.metric("Predicted ROAS", "4.5", "0.3")
        with col3:
            st.metric("Budget Efficiency", "85%", "5%")
        with col4:
            st.metric("Competition Index", "0.6", "-0.1")

# Uso del dashboard
if __name__ == "__main__":
    dashboard = PredictiveDashboard()
    dashboard.run_dashboard()
```

### 5.2 Sistema de Alertas Predictivas

**Sistema de Alertas Inteligentes:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime, timedelta

class PredictiveAlertSystem:
    def __init__(self, email_config):
        self.email_config = email_config
        self.alert_rules = self.load_alert_rules()
        self.prediction_models = {}
        
    def load_alert_rules(self):
        """Cargar reglas de alertas predictivas"""
        return {
            'performance_decline': {
                'threshold': 0.15,  # 15% de declive
                'timeframe': 7,     # 7 días
                'severity': 'HIGH'
            },
            'budget_inefficiency': {
                'threshold': 0.8,   # 80% de eficiencia
                'timeframe': 3,     # 3 días
                'severity': 'MEDIUM'
            },
            'competition_increase': {
                'threshold': 0.2,   # 20% de aumento
                'timeframe': 5,     # 5 días
                'severity': 'MEDIUM'
            },
            'opportunity_detected': {
                'threshold': 0.3,   # 30% de mejora potencial
                'timeframe': 1,     # 1 día
                'severity': 'LOW'
            }
        }
    
    def predict_performance_decline(self, campaign_data):
        """Predecir declive de performance"""
        # Simular predicción (en implementación real, usar modelos entrenados)
        current_roas = campaign_data['current_roas']
        predicted_roas = current_roas * 0.85  # Simular declive del 15%
        
        if predicted_roas < current_roas * (1 - self.alert_rules['performance_decline']['threshold']):
            return {
                'alert_type': 'performance_decline',
                'current_value': current_roas,
                'predicted_value': predicted_roas,
                'decline_percentage': (current_roas - predicted_roas) / current_roas * 100,
                'severity': self.alert_rules['performance_decline']['severity']
            }
        
        return None
    
    def predict_budget_inefficiency(self, campaign_data):
        """Predecir ineficiencia de presupuesto"""
        current_efficiency = campaign_data['budget_efficiency']
        predicted_efficiency = current_efficiency * 0.9  # Simular declive del 10%
        
        if predicted_efficiency < self.alert_rules['budget_inefficiency']['threshold']:
            return {
                'alert_type': 'budget_inefficiency',
                'current_value': current_efficiency,
                'predicted_value': predicted_efficiency,
                'inefficiency_percentage': (1 - predicted_efficiency) * 100,
                'severity': self.alert_rules['budget_inefficiency']['severity']
            }
        
        return None
    
    def predict_competition_increase(self, market_data):
        """Predecir aumento de competencia"""
        current_competition = market_data['competition_level']
        predicted_competition = current_competition * 1.25  # Simular aumento del 25%
        
        if predicted_competition > current_competition * (1 + self.alert_rules['competition_increase']['threshold']):
            return {
                'alert_type': 'competition_increase',
                'current_value': current_competition,
                'predicted_value': predicted_competition,
                'increase_percentage': (predicted_competition - current_competition) / current_competition * 100,
                'severity': self.alert_rules['competition_increase']['severity']
            }
        
        return None
    
    def detect_opportunities(self, campaign_data, market_data):
        """Detectar oportunidades"""
        # Simular detección de oportunidades
        potential_improvement = 0.35  # 35% de mejora potencial
        
        if potential_improvement > self.alert_rules['opportunity_detected']['threshold']:
            return {
                'alert_type': 'opportunity_detected',
                'improvement_potential': potential_improvement * 100,
                'recommended_action': 'Increase budget by 25%',
                'severity': self.alert_rules['opportunity_detected']['severity']
            }
        
        return None
    
    def generate_alerts(self, campaign_data, market_data):
        """Generar alertas predictivas"""
        alerts = []
        
        # Verificar declive de performance
        performance_alert = self.predict_performance_decline(campaign_data)
        if performance_alert:
            alerts.append(performance_alert)
        
        # Verificar ineficiencia de presupuesto
        budget_alert = self.predict_budget_inefficiency(campaign_data)
        if budget_alert:
            alerts.append(budget_alert)
        
        # Verificar aumento de competencia
        competition_alert = self.predict_competition_increase(market_data)
        if competition_alert:
            alerts.append(competition_alert)
        
        # Detectar oportunidades
        opportunity_alert = self.detect_opportunities(campaign_data, market_data)
        if opportunity_alert:
            alerts.append(opportunity_alert)
        
        return alerts
    
    def send_alert_email(self, alerts):
        """Enviar email de alertas"""
        if not alerts:
            return
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        msg['Subject'] = f"Facebook Ads Predictive Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Crear cuerpo del mensaje
        body = "<h2>Facebook Ads Predictive Alerts</h2>\n"
        
        for alert in alerts:
            severity_color = {
                'HIGH': 'red',
                'MEDIUM': 'orange',
                'LOW': 'yellow'
            }.get(alert['severity'], 'black')
            
            body += f"""
            <div style="border: 1px solid {severity_color}; padding: 10px; margin: 5px;">
                <h3 style="color: {severity_color};">{alert['alert_type'].replace('_', ' ').title()} - {alert['severity']}</h3>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            
            if alert['alert_type'] == 'performance_decline':
                body += f"""
                <p><strong>Current ROAS:</strong> {alert['current_value']:.2f}</p>
                <p><strong>Predicted ROAS:</strong> {alert['predicted_value']:.2f}</p>
                <p><strong>Decline:</strong> {alert['decline_percentage']:.1f}%</p>
                <p><strong>Recommendation:</strong> Review campaign settings and consider pausing underperforming ad sets</p>
                """
            elif alert['alert_type'] == 'budget_inefficiency':
                body += f"""
                <p><strong>Current Efficiency:</strong> {alert['current_value']:.1%}</p>
                <p><strong>Predicted Efficiency:</strong> {alert['predicted_value']:.1%}</p>
                <p><strong>Inefficiency:</strong> {alert['inefficiency_percentage']:.1f}%</p>
                <p><strong>Recommendation:</strong> Optimize budget allocation and review targeting</p>
                """
            elif alert['alert_type'] == 'competition_increase':
                body += f"""
                <p><strong>Current Competition:</strong> {alert['current_value']:.2f}</p>
                <p><strong>Predicted Competition:</strong> {alert['predicted_value']:.2f}</p>
                <p><strong>Increase:</strong> {alert['increase_percentage']:.1f}%</p>
                <p><strong>Recommendation:</strong> Adjust bidding strategy and consider new targeting options</p>
                """
            elif alert['alert_type'] == 'opportunity_detected':
                body += f"""
                <p><strong>Improvement Potential:</strong> {alert['improvement_potential']:.1f}%</p>
                <p><strong>Recommended Action:</strong> {alert['recommended_action']}</p>
                """
            
            body += "</div>"
        
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['username'], self.email_config['password'])
        server.send_message(msg)
        server.quit()
    
    def run_alert_system(self, campaign_data, market_data):
        """Ejecutar sistema de alertas"""
        alerts = self.generate_alerts(campaign_data, market_data)
        
        if alerts:
            self.send_alert_email(alerts)
        
        return alerts

# Uso del sistema de alertas
if __name__ == "__main__":
    # Configurar credenciales de email
    EMAIL_CONFIG = {
        'from': 'alerts@yourcompany.com',
        'to': 'marketing@yourcompany.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    # Crear sistema de alertas
    alert_system = PredictiveAlertSystem(EMAIL_CONFIG)
    
    # Datos de ejemplo
    campaign_data = {
        'current_roas': 4.2,
        'budget_efficiency': 0.85
    }
    
    market_data = {
        'competition_level': 0.6
    }
    
    # Ejecutar sistema de alertas
    alerts = alert_system.run_alert_system(campaign_data, market_data)
    
    print(f"Alert system completed. {len(alerts)} alerts generated.")
```

---

## Conclusión

Los analytics predictivos y forecasting proporcionan una ventaja competitiva significativa al anticipar resultados y optimizar proactivamente. La implementación exitosa requiere:

**Elementos Clave:**
1. **Modelos de Predicción**: Machine learning y análisis estadístico
2. **Forecasting Avanzado**: Predicción de tendencias y optimización
3. **Análisis de Competencia**: Identificación de oportunidades
4. **Sistemas de Alertas**: Monitoreo predictivo y notificaciones
5. **Dashboards Interactivos**: Visualización y análisis en tiempo real

**Beneficios:**
- Anticipación de resultados y tendencias
- Optimización proactiva de campañas
- Identificación temprana de problemas
- Detección de oportunidades de mercado
- Mejora en ROI a través de insights predictivos

**Próximos Pasos:**
1. Implementar modelos de predicción
2. Desarrollar sistemas de forecasting
3. Configurar alertas predictivas
4. Crear dashboards interactivos
5. Optimizar continuamente basándose en predicciones

La implementación exitosa de analytics predictivos resultará en un sistema de Facebook Ads altamente optimizado, proactivo y rentable.


