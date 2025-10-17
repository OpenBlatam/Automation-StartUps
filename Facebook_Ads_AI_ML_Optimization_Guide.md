# Guía de Optimización con IA y Machine Learning para Facebook Ads
## Inteligencia Artificial y Aprendizaje Automático para Maximizar ROI

---

## 1. Introducción a la Optimización con IA/ML

Esta guía proporciona técnicas avanzadas de optimización de Facebook Ads utilizando Inteligencia Artificial y Machine Learning, incluyendo algoritmos de optimización, modelos predictivos, automatización inteligente y sistemas de aprendizaje continuo. Está diseñada para profesionales que buscan maximizar el ROI a través de la tecnología más avanzada.

### Objetivos de la Optimización con IA/ML
- Automatizar optimización de campañas
- Predecir performance con alta precisión
- Aprender y adaptarse continuamente
- Maximizar ROI a través de algoritmos inteligentes
- Reducir trabajo manual en 90%+

---

## 2. Fundamentos de IA/ML para Facebook Ads

### 2.1 Tipos de Algoritmos de ML

**Algoritmos de Regresión:**
```
Linear Regression: Predicción de métricas continuas
Random Forest: Predicción robusta con múltiples variables
Gradient Boosting: Optimización de performance
Neural Networks: Modelado complejo de relaciones
```

**Algoritmos de Clasificación:**
```
Logistic Regression: Clasificación binaria
Decision Trees: Reglas de decisión interpretables
SVM: Clasificación de alta precisión
Naive Bayes: Clasificación probabilística
```

**Algoritmos de Clustering:**
```
K-Means: Segmentación de audiencias
Hierarchical Clustering: Agrupación jerárquica
DBSCAN: Detección de outliers
Gaussian Mixture: Modelado de distribuciones
```

**Algoritmos de Optimización:**
```
Genetic Algorithms: Optimización evolutiva
Particle Swarm: Optimización de enjambre
Simulated Annealing: Optimización probabilística
Bayesian Optimization: Optimización bayesiana
```

### 2.2 Aplicaciones de IA/ML

**Optimización de Campañas:**
```
Budget Allocation: Asignación óptima de presupuestos
Bidding Strategy: Estrategias de bidding inteligentes
Creative Optimization: Optimización de creativos
Audience Targeting: Targeting inteligente de audiencias
```

**Predicción de Performance:**
```
CTR Prediction: Predicción de click-through rate
CPA Prediction: Predicción de cost per acquisition
ROAS Prediction: Predicción de return on ad spend
Conversion Prediction: Predicción de conversiones
```

**Análisis de Comportamiento:**
```
Audience Segmentation: Segmentación de audiencias
Behavioral Analysis: Análisis de comportamiento
Intent Prediction: Predicción de intención
Lifetime Value: Predicción de valor de vida
```

---

## 3. Modelos de Machine Learning

### 3.1 Modelo de Predicción de CTR

**Implementación Avanzada:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns

class CTRPredictionModel:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'lightgbm': lgb.LGBMRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
        }
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.best_model = None
        self.feature_importance = None
        
    def prepare_features(self, data):
        """Preparar características para el modelo"""
        # Copiar datos
        df = data.copy()
        
        # Codificar variables categóricas
        categorical_features = ['objective', 'placement', 'device_platform', 'age_range', 'gender']
        for feature in categorical_features:
            if feature in df.columns:
                le = LabelEncoder()
                df[feature] = le.fit_transform(df[feature].astype(str))
                self.label_encoders[feature] = le
        
        # Crear características derivadas
        df['budget_per_audience'] = df['budget'] / df['audience_size']
        df['creative_diversity'] = df['creative_count'] / df['audience_size']
        df['competition_ratio'] = df['competition_level'] / df['market_size']
        
        # Características de timing
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Características de estacionalidad
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def select_features(self, df, target='ctr'):
        """Seleccionar características más relevantes"""
        # Características numéricas
        numeric_features = [
            'budget', 'audience_size', 'creative_count', 'relevance_score',
            'competition_level', 'market_size', 'budget_per_audience',
            'creative_diversity', 'competition_ratio', 'hour_sin', 'hour_cos',
            'day_sin', 'day_cos', 'month_sin', 'month_cos'
        ]
        
        # Características categóricas
        categorical_features = ['objective', 'placement', 'device_platform', 'age_range', 'gender']
        
        # Combinar características
        feature_columns = [col for col in numeric_features + categorical_features if col in df.columns]
        
        return feature_columns
    
    def train_models(self, X, y):
        """Entrenar múltiples modelos y seleccionar el mejor"""
        results = {}
        
        for name, model in self.models.items():
            # Validación cruzada
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
            
            # Entrenar modelo
            model.fit(X, y)
            
            # Evaluar modelo
            y_pred = model.predict(X)
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            results[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'mse': mse,
                'r2': r2,
                'mae': mae
            }
            
            print(f"{name}:")
            print(f"  CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            print(f"  R²: {r2:.4f}")
            print(f"  MSE: {mse:.4f}")
            print(f"  MAE: {mae:.4f}")
            print()
        
        # Seleccionar mejor modelo
        best_model_name = max(results.keys(), key=lambda x: results[x]['cv_mean'])
        self.best_model = results[best_model_name]['model']
        
        print(f"Best model: {best_model_name}")
        
        return results
    
    def predict_ctr(self, features):
        """Predecir CTR usando el mejor modelo"""
        if self.best_model is None:
            raise ValueError("No model trained. Call train_models() first.")
        
        # Predecir
        prediction = self.best_model.predict([features])
        return prediction[0]
    
    def get_feature_importance(self, feature_names):
        """Obtener importancia de características"""
        if self.best_model is None:
            raise ValueError("No model trained. Call train_models() first.")
        
        if hasattr(self.best_model, 'feature_importances_'):
            importance = self.best_model.feature_importances_
        elif hasattr(self.best_model, 'coef_'):
            importance = np.abs(self.best_model.coef_)
        else:
            return None
        
        self.feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return self.feature_importance
    
    def plot_feature_importance(self, top_n=15):
        """Visualizar importancia de características"""
        if self.feature_importance is None:
            raise ValueError("No feature importance calculated. Call get_feature_importance() first.")
        
        plt.figure(figsize=(10, 8))
        top_features = self.feature_importance.head(top_n)
        
        sns.barplot(data=top_features, x='importance', y='feature')
        plt.title(f'Top {top_n} Feature Importance for CTR Prediction')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.show()
    
    def optimize_hyperparameters(self, X, y):
        """Optimizar hiperparámetros usando Grid Search"""
        from sklearn.model_selection import GridSearchCV
        
        # Parámetros para Random Forest
        rf_params = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Grid Search
        grid_search = GridSearchCV(
            RandomForestRegressor(random_state=42),
            rf_params,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_

# Uso del modelo
if __name__ == "__main__":
    # Crear modelo
    ctr_model = CTRPredictionModel()
    
    # Preparar datos (ejemplo)
    data = pd.DataFrame([
        {
            'budget': 1000, 'audience_size': 100000, 'creative_count': 3,
            'relevance_score': 8.5, 'competition_level': 0.7, 'market_size': 1000000,
            'objective': 'CONVERSIONS', 'placement': 'FEED', 'device_platform': 'MOBILE',
            'age_range': '25-34', 'gender': 'ALL', 'hour_of_day': 14,
            'day_of_week': 1, 'month': 6, 'ctr': 2.5
        },
        # ... más datos
    ])
    
    # Preparar características
    df = ctr_model.prepare_features(data)
    feature_columns = ctr_model.select_features(df)
    
    X = df[feature_columns].values
    y = df['ctr'].values
    
    # Normalizar características
    X_scaled = ctr_model.scaler.fit_transform(X)
    
    # Entrenar modelos
    results = ctr_model.train_models(X_scaled, y)
    
    # Obtener importancia de características
    feature_importance = ctr_model.get_feature_importance(feature_columns)
    
    # Visualizar importancia
    ctr_model.plot_feature_importance()
    
    # Predecir CTR
    new_features = [1000, 150000, 4, 9.0, 0.8, 1200000, 0.0067, 0.000027, 0.00067, 0.5, 0.866, 0.781, 0.623, 0.5, 0.866, 0.707, 0.707]
    predicted_ctr = ctr_model.predict_ctr(new_features)
    
    print(f"Predicted CTR: {predicted_ctr:.2f}%")
```

### 3.2 Modelo de Optimización de Presupuestos

**Optimizador Inteligente:**
```python
import pandas as pd
import numpy as np
from scipy.optimize import minimize, differential_evolution
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class IntelligentBudgetOptimizer:
    def __init__(self):
        self.performance_models = {}
        self.budget_constraints = {}
        self.optimization_history = []
        
    def train_performance_models(self, historical_data):
        """Entrenar modelos de performance por campaña"""
        for campaign_id in historical_data['campaign_id'].unique():
            campaign_data = historical_data[historical_data['campaign_id'] == campaign_id]
            
            # Preparar características
            feature_columns = [
                'budget', 'day_of_week', 'hour_of_day', 'month',
                'seasonality_factor', 'competition_level', 'audience_size',
                'creative_count', 'relevance_score'
            ]
            
            X = campaign_data[feature_columns].values
            y = campaign_data['roas'].values
            
            # Entrenar modelo
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            model.fit(X, y)
            
            self.performance_models[campaign_id] = {
                'model': model,
                'feature_columns': feature_columns
            }
    
    def predict_campaign_performance(self, campaign_id, budget, context):
        """Predecir performance de una campaña"""
        if campaign_id not in self.performance_models:
            return 0
        
        model_info = self.performance_models[campaign_id]
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        
        # Preparar características
        features = np.array([[
            budget,
            context['day_of_week'],
            context['hour_of_day'],
            context['month'],
            context['seasonality_factor'],
            context['competition_level'],
            context['audience_size'],
            context['creative_count'],
            context['relevance_score']
        ]])
        
        prediction = model.predict(features)
        return prediction[0]
    
    def objective_function(self, budgets, campaign_ids, context):
        """Función objetivo para optimización"""
        total_revenue = 0
        
        for i, campaign_id in enumerate(campaign_ids):
            roas = self.predict_campaign_performance(campaign_id, budgets[i], context)
            revenue = roas * budgets[i]  # ROAS * Budget = Revenue
            total_revenue += revenue
        
        return -total_revenue  # Minimizar negativo = maximizar
    
    def constraint_budget_sum(self, budgets, total_budget):
        """Restricción de suma de presupuestos"""
        return np.sum(budgets) - total_budget
    
    def constraint_min_budget(self, budgets, min_budget_ratio):
        """Restricción de presupuesto mínimo"""
        return budgets - min_budget_ratio * np.sum(budgets)
    
    def optimize_budgets_genetic(self, campaign_ids, total_budget, context):
        """Optimizar presupuestos usando algoritmo genético"""
        n_campaigns = len(campaign_ids)
        
        # Límites de presupuesto
        bounds = [(total_budget * 0.05, total_budget * 0.95) for _ in range(n_campaigns)]
        
        # Función objetivo
        def objective(budgets):
            return self.objective_function(budgets, campaign_ids, context)
        
        # Optimización genética
        result = differential_evolution(
            objective,
            bounds,
            seed=42,
            maxiter=100,
            popsize=15,
            atol=1e-6,
            tol=1e-6
        )
        
        return result.x, result.fun
    
    def optimize_budgets_bayesian(self, campaign_ids, total_budget, context):
        """Optimizar presupuestos usando optimización bayesiana"""
        from skopt import gp_minimize
        from skopt.space import Real
        
        n_campaigns = len(campaign_ids)
        
        # Espacio de búsqueda
        space = [Real(total_budget * 0.05, total_budget * 0.95) for _ in range(n_campaigns)]
        
        # Función objetivo
        def objective(budgets):
            return self.objective_function(budgets, campaign_ids, context)
        
        # Optimización bayesiana
        result = gp_minimize(
            objective,
            space,
            n_calls=100,
            random_state=42
        )
        
        return result.x, result.fun
    
    def optimize_budgets_particle_swarm(self, campaign_ids, total_budget, context):
        """Optimizar presupuestos usando Particle Swarm Optimization"""
        from pyswarm import pso
        
        n_campaigns = len(campaign_ids)
        
        # Límites
        lb = [total_budget * 0.05] * n_campaigns
        ub = [total_budget * 0.95] * n_campaigns
        
        # Función objetivo
        def objective(budgets):
            return self.objective_function(budgets, campaign_ids, context)
        
        # Restricciones
        def constraint(budgets):
            return np.sum(budgets) - total_budget
        
        # Optimización PSO
        xopt, fopt = pso(
            objective,
            lb,
            ub,
            f_ieqcons=constraint,
            swarmsize=100,
            maxiter=100
        )
        
        return xopt, fopt
    
    def compare_optimization_methods(self, campaign_ids, total_budget, context):
        """Comparar diferentes métodos de optimización"""
        methods = {
            'Genetic Algorithm': self.optimize_budgets_genetic,
            'Bayesian Optimization': self.optimize_budgets_bayesian,
            'Particle Swarm': self.optimize_budgets_particle_swarm
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            try:
                optimal_budgets, total_revenue = method_func(campaign_ids, total_budget, context)
                results[method_name] = {
                    'budgets': optimal_budgets,
                    'revenue': -total_revenue,
                    'success': True
                }
            except Exception as e:
                results[method_name] = {
                    'error': str(e),
                    'success': False
                }
        
        return results
    
    def forecast_optimal_budgets(self, campaign_ids, total_budget, days=30):
        """Predecir presupuestos óptimos para los próximos días"""
        forecasts = []
        
        for day in range(days):
            date = pd.Timestamp.now() + pd.Timedelta(days=day)
            
            context = {
                'day_of_week': date.dayofweek,
                'hour_of_day': 14,  # Hora promedio
                'month': date.month,
                'seasonality_factor': 1.0 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365),
                'competition_level': 0.6 + 0.1 * np.sin(2 * np.pi * date.dayofyear / 365),
                'audience_size': 100000,  # Tamaño promedio
                'creative_count': 3,  # Promedio
                'relevance_score': 8.5  # Promedio
            }
            
            # Optimizar presupuestos
            optimal_budgets, total_revenue = self.optimize_budgets_genetic(
                campaign_ids, total_budget, context
            )
            
            forecasts.append({
                'date': date,
                'optimal_budgets': optimal_budgets,
                'predicted_revenue': -total_revenue,
                'context': context
            })
        
        return pd.DataFrame(forecasts)
    
    def plot_optimization_results(self, forecasts):
        """Visualizar resultados de optimización"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Gráfico de presupuestos óptimos
        for i in range(len(forecasts['optimal_budgets'].iloc[0])):
            budgets = [forecast['optimal_budgets'][i] for forecast in forecasts.to_dict('records')]
            ax1.plot(forecasts['date'], budgets, label=f'Campaign {i+1}', marker='o')
        
        ax1.set_title('Optimal Budget Allocation Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Budget')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico de revenue predicho
        ax2.plot(forecasts['date'], forecasts['predicted_revenue'], 
                color='red', marker='o', linewidth=2)
        ax2.set_title('Predicted Revenue Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Revenue')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Uso del optimizador
if __name__ == "__main__":
    # Crear optimizador
    optimizer = IntelligentBudgetOptimizer()
    
    # Preparar datos históricos (ejemplo)
    historical_data = pd.DataFrame([
        {'campaign_id': 'C1', 'budget': 1000, 'day_of_week': 1, 'hour_of_day': 14, 'month': 6, 'seasonality_factor': 1.1, 'competition_level': 0.7, 'audience_size': 100000, 'creative_count': 3, 'relevance_score': 8.5, 'roas': 4.2},
        # ... más datos
    ])
    
    # Entrenar modelos
    optimizer.train_performance_models(historical_data)
    
    # Optimizar presupuestos
    campaign_ids = ['C1', 'C2', 'C3']
    total_budget = 10000
    
    context = {
        'day_of_week': 1,
        'hour_of_day': 14,
        'month': 6,
        'seasonality_factor': 1.1,
        'competition_level': 0.7,
        'audience_size': 100000,
        'creative_count': 3,
        'relevance_score': 8.5
    }
    
    # Comparar métodos de optimización
    results = optimizer.compare_optimization_methods(campaign_ids, total_budget, context)
    
    for method, result in results.items():
        if result['success']:
            print(f"{method}:")
            print(f"  Optimal Budgets: {result['budgets']}")
            print(f"  Predicted Revenue: ${result['revenue']:.2f}")
        else:
            print(f"{method}: Error - {result['error']}")
    
    # Predecir presupuestos óptimos
    forecasts = optimizer.forecast_optimal_budgets(campaign_ids, total_budget, days=30)
    
    # Visualizar resultados
    optimizer.plot_optimization_results(forecasts)
```

### 3.3 Modelo de Segmentación de Audiencias

**Segmentador Inteligente:**
```python
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class IntelligentAudienceSegmenter:
    def __init__(self):
        self.segmenter = None
        self.scaler = StandardScaler()
        self.pca = None
        self.segments = None
        self.segment_profiles = None
        
    def prepare_audience_data(self, audience_data):
        """Preparar datos de audiencia para segmentación"""
        # Copiar datos
        df = audience_data.copy()
        
        # Crear características derivadas
        df['engagement_rate'] = df['clicks'] / df['impressions']
        df['conversion_rate'] = df['conversions'] / df['clicks']
        df['cost_per_engagement'] = df['spend'] / df['clicks']
        df['cost_per_conversion'] = df['spend'] / df['conversions']
        df['audience_efficiency'] = df['conversions'] / df['spend']
        
        # Características de comportamiento
        df['click_frequency'] = df['clicks'] / df['audience_size']
        df['conversion_frequency'] = df['conversions'] / df['audience_size']
        df['spend_frequency'] = df['spend'] / df['audience_size']
        
        # Características de timing
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def select_segmentation_features(self, df):
        """Seleccionar características para segmentación"""
        feature_columns = [
            'engagement_rate', 'conversion_rate', 'cost_per_engagement',
            'cost_per_conversion', 'audience_efficiency', 'click_frequency',
            'conversion_frequency', 'spend_frequency', 'hour_sin', 'hour_cos',
            'day_sin', 'day_cos', 'age_25_34', 'age_35_44', 'age_45_54',
            'gender_male', 'gender_female', 'interests_count', 'behavior_score'
        ]
        
        # Filtrar características disponibles
        available_features = [col for col in feature_columns if col in df.columns]
        
        return available_features
    
    def find_optimal_clusters(self, X, max_clusters=10):
        """Encontrar número óptimo de clusters"""
        inertias = []
        silhouette_scores = []
        calinski_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, cluster_labels))
            calinski_scores.append(calinski_harabasz_score(X, cluster_labels))
        
        # Encontrar número óptimo usando método del codo y silhouette
        optimal_k = np.argmax(silhouette_scores) + 2
        
        return optimal_k, inertias, silhouette_scores, calinski_scores
    
    def segment_audiences(self, audience_data, method='kmeans', n_clusters=None):
        """Segmentar audiencias usando diferentes métodos"""
        # Preparar datos
        df = self.prepare_audience_data(audience_data)
        feature_columns = self.select_segmentation_features(df)
        
        X = df[feature_columns].values
        
        # Normalizar características
        X_scaled = self.scaler.fit_transform(X)
        
        # Reducir dimensionalidad si es necesario
        if X_scaled.shape[1] > 10:
            self.pca = PCA(n_components=10, random_state=42)
            X_scaled = self.pca.fit_transform(X_scaled)
        
        # Encontrar número óptimo de clusters si no se especifica
        if n_clusters is None:
            optimal_k, inertias, silhouette_scores, calinski_scores = self.find_optimal_clusters(X_scaled)
            n_clusters = optimal_k
        
        # Aplicar método de segmentación
        if method == 'kmeans':
            self.segmenter = KMeans(n_clusters=n_clusters, random_state=42)
        elif method == 'dbscan':
            self.segmenter = DBSCAN(eps=0.5, min_samples=5)
        elif method == 'gaussian_mixture':
            self.segmenter = GaussianMixture(n_components=n_clusters, random_state=42)
        elif method == 'hierarchical':
            self.segmenter = AgglomerativeClustering(n_clusters=n_clusters)
        
        # Entrenar segmentador
        if method == 'gaussian_mixture':
            self.segmenter.fit(X_scaled)
            segment_labels = self.segmenter.predict(X_scaled)
        else:
            segment_labels = self.segmenter.fit_predict(X_scaled)
        
        # Agregar segmentos a los datos
        df['segment'] = segment_labels
        
        # Crear perfiles de segmentos
        self.segment_profiles = self.create_segment_profiles(df, feature_columns)
        
        return df, segment_labels
    
    def create_segment_profiles(self, df, feature_columns):
        """Crear perfiles de segmentos"""
        profiles = {}
        
        for segment in df['segment'].unique():
            if segment == -1:  # Skip noise points in DBSCAN
                continue
                
            segment_data = df[df['segment'] == segment]
            
            profile = {
                'size': len(segment_data),
                'percentage': len(segment_data) / len(df) * 100,
                'characteristics': {}
            }
            
            # Calcular características promedio
            for feature in feature_columns:
                profile['characteristics'][feature] = {
                    'mean': segment_data[feature].mean(),
                    'std': segment_data[feature].std(),
                    'median': segment_data[feature].median()
                }
            
            # Calcular métricas de performance
            profile['performance'] = {
                'avg_engagement_rate': segment_data['engagement_rate'].mean(),
                'avg_conversion_rate': segment_data['conversion_rate'].mean(),
                'avg_cost_per_conversion': segment_data['cost_per_conversion'].mean(),
                'avg_audience_efficiency': segment_data['audience_efficiency'].mean()
            }
            
            profiles[segment] = profile
        
        return profiles
    
    def analyze_segment_performance(self, df):
        """Analizar performance de segmentos"""
        segment_analysis = df.groupby('segment').agg({
            'engagement_rate': ['mean', 'std'],
            'conversion_rate': ['mean', 'std'],
            'cost_per_conversion': ['mean', 'std'],
            'audience_efficiency': ['mean', 'std'],
            'spend': ['sum', 'mean'],
            'conversions': ['sum', 'mean']
        }).round(4)
        
        return segment_analysis
    
    def recommend_segment_strategies(self, segment_profiles):
        """Recomendar estrategias por segmento"""
        recommendations = {}
        
        for segment, profile in segment_profiles.items():
            if segment == -1:  # Skip noise points
                continue
                
            performance = profile['performance']
            size = profile['size']
            
            # Clasificar segmento
            if performance['avg_engagement_rate'] > 0.05 and performance['avg_conversion_rate'] > 0.03:
                segment_type = 'High Value'
                strategy = 'Scale and optimize'
                priority = 'High'
            elif performance['avg_engagement_rate'] > 0.03 and performance['avg_conversion_rate'] > 0.02:
                segment_type = 'Medium Value'
                strategy = 'Test and optimize'
                priority = 'Medium'
            elif performance['avg_engagement_rate'] > 0.02:
                segment_type = 'Low Value'
                strategy = 'Pause or optimize'
                priority = 'Low'
            else:
                segment_type = 'Poor Performance'
                strategy = 'Pause or exclude'
                priority = 'Very Low'
            
            recommendations[segment] = {
                'segment_type': segment_type,
                'strategy': strategy,
                'priority': priority,
                'size': size,
                'performance': performance
            }
        
        return recommendations
    
    def plot_segment_analysis(self, df, feature_columns):
        """Visualizar análisis de segmentos"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Gráfico de distribución de segmentos
        segment_counts = df['segment'].value_counts().sort_index()
        axes[0, 0].bar(segment_counts.index, segment_counts.values)
        axes[0, 0].set_title('Segment Distribution')
        axes[0, 0].set_xlabel('Segment')
        axes[0, 0].set_ylabel('Count')
        
        # Gráfico de performance por segmento
        segment_performance = df.groupby('segment').agg({
            'engagement_rate': 'mean',
            'conversion_rate': 'mean'
        })
        
        x = np.arange(len(segment_performance))
        width = 0.35
        
        axes[0, 1].bar(x - width/2, segment_performance['engagement_rate'], width, label='Engagement Rate')
        axes[0, 1].bar(x + width/2, segment_performance['conversion_rate'], width, label='Conversion Rate')
        axes[0, 1].set_title('Performance by Segment')
        axes[0, 1].set_xlabel('Segment')
        axes[0, 1].set_ylabel('Rate')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(segment_performance.index)
        axes[0, 1].legend()
        
        # Gráfico de costo por conversión
        segment_costs = df.groupby('segment')['cost_per_conversion'].mean()
        axes[1, 0].bar(segment_costs.index, segment_costs.values)
        axes[1, 0].set_title('Cost per Conversion by Segment')
        axes[1, 0].set_xlabel('Segment')
        axes[1, 0].set_ylabel('Cost per Conversion')
        
        # Gráfico de eficiencia de audiencia
        segment_efficiency = df.groupby('segment')['audience_efficiency'].mean()
        axes[1, 1].bar(segment_efficiency.index, segment_efficiency.values)
        axes[1, 1].set_title('Audience Efficiency by Segment')
        axes[1, 1].set_xlabel('Segment')
        axes[1, 1].set_ylabel('Audience Efficiency')
        
        plt.tight_layout()
        plt.show()
    
    def plot_segment_characteristics(self, df, feature_columns):
        """Visualizar características de segmentos"""
        # Seleccionar características principales
        main_features = ['engagement_rate', 'conversion_rate', 'cost_per_conversion', 'audience_efficiency']
        available_features = [f for f in main_features if f in feature_columns]
        
        if len(available_features) < 2:
            return
        
        # Crear heatmap de características por segmento
        segment_characteristics = df.groupby('segment')[available_features].mean()
        
        plt.figure(figsize=(10, 6))
        sns.heatmap(segment_characteristics.T, annot=True, cmap='YlOrRd', fmt='.3f')
        plt.title('Segment Characteristics Heatmap')
        plt.xlabel('Segment')
        plt.ylabel('Characteristics')
        plt.tight_layout()
        plt.show()

# Uso del segmentador
if __name__ == "__main__":
    # Crear segmentador
    segmenter = IntelligentAudienceSegmenter()
    
    # Preparar datos de audiencia (ejemplo)
    audience_data = pd.DataFrame([
        {
            'audience_id': 'A1', 'impressions': 10000, 'clicks': 200, 'conversions': 10,
            'spend': 500, 'audience_size': 100000, 'hour_of_day': 14, 'day_of_week': 1,
            'age_25_34': 0.4, 'age_35_44': 0.3, 'age_45_54': 0.2,
            'gender_male': 0.5, 'gender_female': 0.5, 'interests_count': 15, 'behavior_score': 8.5
        },
        # ... más datos
    ])
    
    # Segmentar audiencias
    segmented_data, segment_labels = segmenter.segment_audiences(audience_data, method='kmeans')
    
    # Analizar performance de segmentos
    segment_analysis = segmenter.analyze_segment_performance(segmented_data)
    
    # Recomendar estrategias
    recommendations = segmenter.recommend_segment_strategies(segmenter.segment_profiles)
    
    # Visualizar análisis
    feature_columns = segmenter.select_segmentation_features(segmented_data)
    segmenter.plot_segment_analysis(segmented_data, feature_columns)
    segmenter.plot_segment_characteristics(segmented_data, feature_columns)
    
    print("Segment Analysis Results:")
    print(segment_analysis)
    print("\nSegment Recommendations:")
    for segment, rec in recommendations.items():
        print(f"Segment {segment}: {rec['segment_type']} - {rec['strategy']} (Priority: {rec['priority']})")
```

---

## 4. Sistemas de Aprendizaje Continuo

### 4.1 Sistema de Aprendizaje Adaptativo

**Aprendizaje Continuo:**
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta

class ContinuousLearningSystem:
    def __init__(self, model_path='models/'):
        self.model_path = model_path
        self.models = {}
        self.performance_history = {}
        self.learning_threshold = 0.05  # 5% de mejora mínima
        self.retrain_frequency = 7  # Reentrenar cada 7 días
        
    def load_existing_models(self):
        """Cargar modelos existentes"""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
            return
        
        for filename in os.listdir(self.model_path):
            if filename.endswith('.pkl'):
                model_name = filename[:-4]
                model_path = os.path.join(self.model_path, filename)
                self.models[model_name] = joblib.load(model_path)
    
    def save_models(self):
        """Guardar modelos"""
        for model_name, model in self.models.items():
            model_path = os.path.join(self.model_path, f"{model_name}.pkl")
            joblib.dump(model, model_path)
    
    def evaluate_model_performance(self, model, X_test, y_test):
        """Evaluar performance del modelo"""
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_test)
        
        return {
            'mse': mse,
            'r2': r2,
            'rmse': np.sqrt(mse)
        }
    
    def should_retrain(self, model_name, new_performance):
        """Determinar si el modelo debe ser reentrenado"""
        if model_name not in self.performance_history:
            return True
        
        last_performance = self.performance_history[model_name][-1]
        
        # Reentrenar si la performance ha mejorado significativamente
        if new_performance['r2'] > last_performance['r2'] + self.learning_threshold:
            return True
        
        # Reentrenar si ha pasado suficiente tiempo
        last_retrain = self.performance_history[model_name][-1]['timestamp']
        if (datetime.now() - last_retrain).days >= self.retrain_frequency:
            return True
        
        return False
    
    def retrain_model(self, model_name, new_data):
        """Reentrenar modelo con nuevos datos"""
        # Preparar datos
        X = new_data.drop('target', axis=1)
        y = new_data['target']
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar nuevo modelo
        new_model = RandomForestRegressor(n_estimators=100, random_state=42)
        new_model.fit(X_train, y_train)
        
        # Evaluar performance
        performance = self.evaluate_model_performance(new_model, X_test, y_test)
        
        # Decidir si actualizar el modelo
        if self.should_retrain(model_name, performance):
            self.models[model_name] = new_model
            
            # Actualizar historial de performance
            if model_name not in self.performance_history:
                self.performance_history[model_name] = []
            
            self.performance_history[model_name].append({
                'timestamp': datetime.now(),
                'performance': performance,
                'data_size': len(new_data)
            })
            
            # Guardar modelo
            self.save_models()
            
            return True, performance
        
        return False, performance
    
    def update_model_with_feedback(self, model_name, feedback_data):
        """Actualizar modelo con feedback de performance"""
        if model_name not in self.models:
            return False
        
        # Agregar feedback a los datos existentes
        # (En implementación real, esto vendría de la performance real de las campañas)
        
        # Reentrenar modelo
        success, performance = self.retrain_model(model_name, feedback_data)
        
        return success, performance
    
    def get_model_insights(self, model_name):
        """Obtener insights del modelo"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        insights = {
            'model_type': type(model).__name__,
            'training_date': self.performance_history[model_name][-1]['timestamp'] if model_name in self.performance_history else None,
            'performance_trend': self.get_performance_trend(model_name),
            'feature_importance': self.get_feature_importance(model),
            'data_quality': self.assess_data_quality(model_name)
        }
        
        return insights
    
    def get_performance_trend(self, model_name):
        """Obtener tendencia de performance"""
        if model_name not in self.performance_history:
            return None
        
        history = self.performance_history[model_name]
        if len(history) < 2:
            return 'Insufficient data'
        
        recent_r2 = history[-1]['performance']['r2']
        previous_r2 = history[-2]['performance']['r2']
        
        if recent_r2 > previous_r2 + 0.01:
            return 'Improving'
        elif recent_r2 < previous_r2 - 0.01:
            return 'Declining'
        else:
            return 'Stable'
    
    def get_feature_importance(self, model):
        """Obtener importancia de características"""
        if hasattr(model, 'feature_importances_'):
            return model.feature_importances_.tolist()
        return None
    
    def assess_data_quality(self, model_name):
        """Evaluar calidad de datos"""
        if model_name not in self.performance_history:
            return 'Unknown'
        
        history = self.performance_history[model_name]
        recent_performance = history[-1]['performance']
        
        if recent_performance['r2'] > 0.8:
            return 'Excellent'
        elif recent_performance['r2'] > 0.6:
            return 'Good'
        elif recent_performance['r2'] > 0.4:
            return 'Fair'
        else:
            return 'Poor'
    
    def monitor_model_drift(self, model_name, new_data):
        """Monitorear drift del modelo"""
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        
        # Predecir con datos nuevos
        X_new = new_data.drop('target', axis=1)
        y_new = new_data['target']
        y_pred = model.predict(X_new)
        
        # Calcular métricas de drift
        mse_new = mean_squared_error(y_new, y_pred)
        
        # Comparar con performance histórica
        if model_name in self.performance_history:
            historical_mse = self.performance_history[model_name][-1]['performance']['mse']
            drift_ratio = mse_new / historical_mse
            
            if drift_ratio > 1.5:  # 50% de aumento en MSE
                return {
                    'drift_detected': True,
                    'drift_ratio': drift_ratio,
                    'severity': 'High' if drift_ratio > 2.0 else 'Medium'
                }
        
        return {
            'drift_detected': False,
            'drift_ratio': 1.0,
            'severity': 'None'
        }
    
    def generate_learning_report(self):
        """Generar reporte de aprendizaje"""
        report = {
            'timestamp': datetime.now(),
            'models': {},
            'overall_health': 'Good'
        }
        
        for model_name in self.models.keys():
            insights = self.get_model_insights(model_name)
            report['models'][model_name] = insights
        
        # Evaluar salud general del sistema
        poor_models = sum(1 for model in report['models'].values() 
                         if model and model['data_quality'] == 'Poor')
        
        if poor_models > len(self.models) * 0.5:
            report['overall_health'] = 'Poor'
        elif poor_models > len(self.models) * 0.2:
            report['overall_health'] = 'Fair'
        
        return report

# Uso del sistema de aprendizaje continuo
if __name__ == "__main__":
    # Crear sistema de aprendizaje
    learning_system = ContinuousLearningSystem()
    
    # Cargar modelos existentes
    learning_system.load_existing_models()
    
    # Simular nuevos datos
    new_data = pd.DataFrame([
        {'feature1': 1.0, 'feature2': 2.0, 'feature3': 3.0, 'target': 4.0},
        # ... más datos
    ])
    
    # Actualizar modelo con feedback
    success, performance = learning_system.update_model_with_feedback('ctr_model', new_data)
    
    if success:
        print(f"Model updated successfully. New performance: {performance}")
    else:
        print(f"Model not updated. Current performance: {performance}")
    
    # Monitorear drift
    drift_info = learning_system.monitor_model_drift('ctr_model', new_data)
    if drift_info and drift_info['drift_detected']:
        print(f"Model drift detected: {drift_info['severity']} severity")
    
    # Generar reporte
    report = learning_system.generate_learning_report()
    print(f"Learning system health: {report['overall_health']}")
```

---

## 5. Herramientas de IA/ML

### 5.1 Plataforma de ML End-to-End

**Plataforma Completa:**
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import joblib
import os

class MLPlatform:
    def __init__(self):
        self.models = {}
        self.data = None
        self.predictions = None
        
    def load_data(self, data_source):
        """Cargar datos para la plataforma"""
        if data_source.endswith('.csv'):
            self.data = pd.read_csv(data_source)
        elif data_source.endswith('.json'):
            self.data = pd.read_json(data_source)
        else:
            st.error("Unsupported file format")
            return False
        
        return True
    
    def create_model_selection_interface(self):
        """Crear interfaz de selección de modelos"""
        st.subheader("Model Selection")
        
        model_type = st.selectbox(
            "Select Model Type",
            ["Random Forest", "XGBoost", "LightGBM", "Neural Network"]
        )
        
        if model_type == "Random Forest":
            n_estimators = st.slider("Number of Estimators", 10, 200, 100)
            max_depth = st.slider("Max Depth", 3, 20, 10)
            min_samples_split = st.slider("Min Samples Split", 2, 20, 2)
            
            return {
                'type': 'RandomForestRegressor',
                'params': {
                    'n_estimators': n_estimators,
                    'max_depth': max_depth,
                    'min_samples_split': min_samples_split,
                    'random_state': 42
                }
            }
        
        elif model_type == "XGBoost":
            n_estimators = st.slider("Number of Estimators", 10, 200, 100)
            max_depth = st.slider("Max Depth", 3, 10, 6)
            learning_rate = st.slider("Learning Rate", 0.01, 0.3, 0.1)
            
            return {
                'type': 'XGBRegressor',
                'params': {
                    'n_estimators': n_estimators,
                    'max_depth': max_depth,
                    'learning_rate': learning_rate,
                    'random_state': 42
                }
            }
        
        # Agregar más tipos de modelos...
        
        return None
    
    def create_training_interface(self):
        """Crear interfaz de entrenamiento"""
        st.subheader("Model Training")
        
        if self.data is None:
            st.warning("Please load data first")
            return
        
        # Seleccionar características
        feature_columns = st.multiselect(
            "Select Features",
            self.data.columns.tolist(),
            default=self.data.columns.tolist()[:-1]  # Excluir última columna (target)
        )
        
        # Seleccionar target
        target_column = st.selectbox(
            "Select Target",
            self.data.columns.tolist()
        )
        
        # Configurar modelo
        model_config = self.create_model_selection_interface()
        
        if st.button("Train Model"):
            with st.spinner("Training model..."):
                # Preparar datos
                X = self.data[feature_columns]
                y = self.data[target_column]
                
                # Entrenar modelo
                if model_config['type'] == 'RandomForestRegressor':
                    from sklearn.ensemble import RandomForestRegressor
                    model = RandomForestRegressor(**model_config['params'])
                elif model_config['type'] == 'XGBRegressor':
                    import xgboost as xgb
                    model = xgb.XGBRegressor(**model_config['params'])
                
                model.fit(X, y)
                
                # Guardar modelo
                self.models['current_model'] = model
                
                # Evaluar modelo
                y_pred = model.predict(X)
                mse = np.mean((y - y_pred) ** 2)
                r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
                
                st.success(f"Model trained successfully!")
                st.metric("MSE", f"{mse:.4f}")
                st.metric("R² Score", f"{r2:.4f}")
    
    def create_prediction_interface(self):
        """Crear interfaz de predicción"""
        st.subheader("Make Predictions")
        
        if 'current_model' not in self.models:
            st.warning("Please train a model first")
            return
        
        model = self.models['current_model']
        
        # Crear formulario de entrada
        st.write("Enter feature values:")
        
        # Obtener características del modelo
        feature_names = [f"feature_{i}" for i in range(10)]  # Simplificado
        
        feature_values = {}
        for feature in feature_names:
            feature_values[feature] = st.number_input(f"{feature}", value=0.0)
        
        if st.button("Make Prediction"):
            # Preparar datos de entrada
            input_data = np.array([list(feature_values.values())])
            
            # Hacer predicción
            prediction = model.predict(input_data)
            
            st.success(f"Prediction: {prediction[0]:.4f}")
    
    def create_visualization_interface(self):
        """Crear interfaz de visualización"""
        st.subheader("Data Visualization")
        
        if self.data is None:
            st.warning("Please load data first")
            return
        
        # Gráfico de distribución
        st.write("Data Distribution")
        column = st.selectbox("Select Column", self.data.columns.tolist())
        
        fig = px.histogram(self.data, x=column, title=f"Distribution of {column}")
        st.plotly_chart(fig)
        
        # Gráfico de correlación
        st.write("Correlation Matrix")
        numeric_data = self.data.select_dtypes(include=[np.number])
        corr_matrix = numeric_data.corr()
        
        fig = px.imshow(corr_matrix, title="Correlation Matrix")
        st.plotly_chart(fig)
        
        # Gráfico de scatter
        st.write("Scatter Plot")
        col1, col2 = st.columns(2)
        
        with col1:
            x_column = st.selectbox("X Axis", numeric_data.columns.tolist())
        with col2:
            y_column = st.selectbox("Y Axis", numeric_data.columns.tolist())
        
        fig = px.scatter(self.data, x=x_column, y=y_column, title=f"{x_column} vs {y_column}")
        st.plotly_chart(fig)
    
    def create_model_comparison_interface(self):
        """Crear interfaz de comparación de modelos"""
        st.subheader("Model Comparison")
        
        if len(self.models) < 2:
            st.warning("Please train at least 2 models for comparison")
            return
        
        # Comparar modelos
        model_names = list(self.models.keys())
        selected_models = st.multiselect("Select Models to Compare", model_names)
        
        if len(selected_models) >= 2:
            # Crear gráfico de comparación
            comparison_data = []
            
            for model_name in selected_models:
                model = self.models[model_name]
                # Simular métricas (en implementación real, calcular métricas reales)
                metrics = {
                    'Model': model_name,
                    'MSE': np.random.uniform(0.1, 1.0),
                    'R²': np.random.uniform(0.5, 0.9),
                    'MAE': np.random.uniform(0.1, 0.5)
                }
                comparison_data.append(metrics)
            
            comparison_df = pd.DataFrame(comparison_data)
            
            # Gráfico de barras
            fig = px.bar(comparison_df, x='Model', y=['MSE', 'R²', 'MAE'], 
                        title="Model Performance Comparison", barmode='group')
            st.plotly_chart(fig)
    
    def run_platform(self):
        """Ejecutar plataforma"""
        st.set_page_config(page_title="Facebook Ads ML Platform", layout="wide")
        
        st.title("Facebook Ads Machine Learning Platform")
        
        # Sidebar
        st.sidebar.header("Navigation")
        page = st.sidebar.selectbox("Select Page", [
            "Data Loading", "Model Training", "Predictions", 
            "Visualization", "Model Comparison"
        ])
        
        # Main content
        if page == "Data Loading":
            st.header("Data Loading")
            uploaded_file = st.file_uploader("Upload Data", type=['csv', 'json'])
            
            if uploaded_file is not None:
                if self.load_data(uploaded_file):
                    st.success("Data loaded successfully!")
                    st.write(f"Data shape: {self.data.shape}")
                    st.write("First 5 rows:")
                    st.dataframe(self.data.head())
        
        elif page == "Model Training":
            self.create_training_interface()
        
        elif page == "Predictions":
            self.create_prediction_interface()
        
        elif page == "Visualization":
            self.create_visualization_interface()
        
        elif page == "Model Comparison":
            self.create_model_comparison_interface()

# Uso de la plataforma
if __name__ == "__main__":
    platform = MLPlatform()
    platform.run_platform()
```

---

## Conclusión

La optimización con IA y Machine Learning proporciona una ventaja competitiva significativa al automatizar la optimización, predecir performance y aprender continuamente. La implementación exitosa requiere:

**Elementos Clave:**
1. **Modelos de ML Avanzados**: Algoritmos sofisticados para predicción y optimización
2. **Sistemas de Aprendizaje Continuo**: Adaptación y mejora automática
3. **Plataformas de ML**: Herramientas end-to-end para desarrollo y deployment
4. **Automatización Inteligente**: Optimización automática basada en IA
5. **Monitoreo y Evaluación**: Supervisión continua de performance

**Beneficios:**
- Automatización del 90%+ de tareas de optimización
- Predicción de performance con alta precisión
- Aprendizaje y adaptación continuos
- Maximización de ROI a través de algoritmos inteligentes
- Reducción significativa del trabajo manual

**Próximos Pasos:**
1. Implementar modelos de ML avanzados
2. Desarrollar sistemas de aprendizaje continuo
3. Crear plataformas de ML end-to-end
4. Configurar automatización inteligente
5. Monitorear y optimizar continuamente

La implementación exitosa de IA/ML resultará en un sistema de Facebook Ads altamente automatizado, inteligente y rentable.


