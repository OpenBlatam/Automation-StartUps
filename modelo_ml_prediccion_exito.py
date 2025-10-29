#!/usr/bin/env python3
"""
Modelo de Machine Learning para Predicción de Éxito
Pivote 3: Licensing Technology
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime

class PredictorExito:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.model_performance = None
        
    def generar_datos_sinteticos(self, n_samples=1000):
        """Genera datos sintéticos para entrenamiento"""
        np.random.seed(42)
        
        # Features principales
        data = {
            'growth_rate': np.random.normal(0.25, 0.1, n_samples),
            'churn_rate': np.random.normal(0.05, 0.02, n_samples),
            'cac': np.random.normal(150, 50, n_samples),
            'ltv': np.random.normal(5000, 1000, n_samples),
            'gross_margin': np.random.normal(0.92, 0.03, n_samples),
            'opex_ratio': np.random.normal(0.55, 0.1, n_samples),
            'market_size': np.random.normal(45, 10, n_samples),
            'competition_level': np.random.normal(0.5, 0.2, n_samples),
            'team_size': np.random.normal(20, 10, n_samples),
            'funding_amount': np.random.normal(2, 1, n_samples),
            'time_to_market': np.random.normal(6, 2, n_samples),
            'product_complexity': np.random.normal(0.6, 0.2, n_samples),
            'customer_satisfaction': np.random.normal(0.8, 0.1, n_samples),
            'brand_recognition': np.random.normal(0.3, 0.2, n_samples),
            'partnerships_count': np.random.normal(5, 3, n_samples)
        }
        
        # Target: ROI (función compleja de las features)
        roi = (
            data['growth_rate'] * 1000 +
            (1 - data['churn_rate']) * 2000 +
            data['ltv'] / data['cac'] * 100 +
            data['gross_margin'] * 500 +
            (1 - data['opex_ratio']) * 300 +
            data['market_size'] * 10 +
            (1 - data['competition_level']) * 200 +
            data['team_size'] * 5 +
            data['funding_amount'] * 50 +
            (12 - data['time_to_market']) * 20 +
            (1 - data['product_complexity']) * 100 +
            data['customer_satisfaction'] * 200 +
            data['brand_recognition'] * 150 +
            data['partnerships_count'] * 10 +
            np.random.normal(0, 100, n_samples)  # Ruido
        )
        
        data['roi'] = roi
        
        return pd.DataFrame(data)
    
    def entrenar_modelo(self, data):
        """Entrena el modelo de predicción"""
        # Separar features y target
        X = data.drop('roi', axis=1)
        y = data['roi']
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelo (Random Forest)
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test_scaled)
        
        self.model_performance = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred),
            'cv_score': cross_val_score(self.model, X_train_scaled, y_train, cv=5).mean()
        }
        
        # Feature importance
        self.feature_importance = dict(zip(
            X.columns,
            self.model.feature_importances_
        ))
        
        return self.model_performance
    
    def predecir_roi(self, features):
        """Predice ROI para un conjunto de features"""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Escalar features
        features_scaled = self.scaler.transform([features])
        
        # Predecir
        prediction = self.model.predict(features_scaled)[0]
        
        return prediction
    
    def analizar_escenarios(self):
        """Analiza diferentes escenarios de negocio"""
        print("=" * 80)
        print("MODELO DE MACHINE LEARNING - PREDICCIÓN DE ÉXITO")
        print("=" * 80)
        
        # Generar datos
        data = self.generar_datos_sinteticos()
        
        # Entrenar modelo
        performance = self.entrenar_modelo(data)
        
        print(f"\n📊 PERFORMANCE DEL MODELO")
        print("-" * 40)
        print(f"R² Score:           {performance['r2']:.3f}")
        print(f"RMSE:               {performance['rmse']:.1f}")
        print(f"Cross-validation:   {performance['cv_score']:.3f}")
        
        print(f"\n🔍 FEATURE IMPORTANCE")
        print("-" * 40)
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for feature, importance in sorted_features[:10]:
            print(f"{feature:<20}: {importance:.3f}")
        
        # Analizar escenarios
        print(f"\n🎯 ANÁLISIS DE ESCENARIOS")
        print("-" * 40)
        
        scenarios = {
            'Conservador': {
                'growth_rate': 0.15, 'churn_rate': 0.08, 'cac': 200,
                'ltv': 4000, 'gross_margin': 0.90, 'opex_ratio': 0.60,
                'market_size': 30, 'competition_level': 0.7, 'team_size': 15,
                'funding_amount': 1.5, 'time_to_market': 8, 'product_complexity': 0.7,
                'customer_satisfaction': 0.7, 'brand_recognition': 0.2,
                'partnerships_count': 3
            },
            'Base': {
                'growth_rate': 0.25, 'churn_rate': 0.05, 'cac': 150,
                'ltv': 5000, 'gross_margin': 0.92, 'opex_ratio': 0.55,
                'market_size': 45, 'competition_level': 0.5, 'team_size': 20,
                'funding_amount': 2.0, 'time_to_market': 6, 'product_complexity': 0.6,
                'customer_satisfaction': 0.8, 'brand_recognition': 0.3,
                'partnerships_count': 5
            },
            'Optimista': {
                'growth_rate': 0.35, 'churn_rate': 0.03, 'cac': 120,
                'ltv': 6000, 'gross_margin': 0.95, 'opex_ratio': 0.50,
                'market_size': 60, 'competition_level': 0.3, 'team_size': 30,
                'funding_amount': 3.0, 'time_to_market': 4, 'product_complexity': 0.4,
                'customer_satisfaction': 0.9, 'brand_recognition': 0.5,
                'partnerships_count': 8
            }
        }
        
        predictions = {}
        for scenario_name, features in scenarios.items():
            features_list = list(features.values())
            roi_predicted = self.predecir_roi(features_list)
            predictions[scenario_name] = roi_predicted
            
            print(f"{scenario_name:<12}: ROI {roi_predicted:,.0f}%")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES BASADAS EN ML")
        print("-" * 40)
        
        best_scenario = max(predictions.items(), key=lambda x: x[1])
        print(f"✅ Mejor escenario: {best_scenario[0]} (ROI: {best_scenario[1]:,.0f}%)")
        
        # Análisis de sensibilidad
        print(f"\n🔬 ANÁLISIS DE SENSIBILIDAD")
        print("-" * 40)
        
        base_features = scenarios['Base']
        sensitivity_analysis = {}
        
        for feature, base_value in base_features.items():
            if feature in ['growth_rate', 'churn_rate', 'cac', 'ltv']:
                # Variar ±20%
                features_high = base_features.copy()
                features_high[feature] = base_value * 1.2
                
                features_low = base_features.copy()
                features_low[feature] = base_value * 0.8
                
                roi_high = self.predecir_roi(list(features_high.values()))
                roi_low = self.predecir_roi(list(features_low.values()))
                
                sensitivity = (roi_high - roi_low) / (base_value * 0.4)
                sensitivity_analysis[feature] = sensitivity
        
        # Mostrar sensibilidad
        sorted_sensitivity = sorted(
            sensitivity_analysis.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for feature, sensitivity in sorted_sensitivity[:5]:
            print(f"{feature:<20}: {sensitivity:+.1f}% ROI por 1% cambio")
        
        return predictions, sensitivity_analysis
    
    def guardar_modelo(self, filename='modelo_prediccion_exito.pkl'):
        """Guarda el modelo entrenado"""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance,
            'model_performance': self.model_performance,
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filename)
        print(f"✅ Modelo guardado en {filename}")
    
    def cargar_modelo(self, filename='modelo_prediccion_exito.pkl'):
        """Carga un modelo previamente entrenado"""
        try:
            model_data = joblib.load(filename)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_importance = model_data['feature_importance']
            self.model_performance = model_data['model_performance']
            print(f"✅ Modelo cargado desde {filename}")
        except FileNotFoundError:
            print(f"❌ Archivo {filename} no encontrado")

def main():
    predictor = PredictorExito()
    
    # Analizar escenarios
    predictions, sensitivity = predictor.analizar_escenarios()
    
    # Guardar modelo
    predictor.guardar_modelo()
    
    print("\n" + "=" * 80)
    print("✅ Análisis de Machine Learning completado")
    print("=" * 80)

if __name__ == "__main__":
    main()

