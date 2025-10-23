#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Machine Learning para Predicción de Éxito de Campañas
===============================================================
Utiliza algoritmos de ML para predecir la probabilidad de éxito de campañas de marketing con IA.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

class MLSuccessPredictor:
    def __init__(self, campaigns_file='enhanced_1000_ai_marketing_campaigns.json'):
        """Inicializa el predictor de éxito con ML"""
        with open(campaigns_file, 'r', encoding='utf-8') as f:
            self.campaigns = json.load(f)
        
        self.df = pd.DataFrame(self.campaigns)
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Preparar datos para entrenamiento
        self.prepare_training_data()
        
    def prepare_training_data(self):
        """Prepara los datos para entrenamiento de modelos ML"""
        # Crear características (features)
        features = []
        targets = []
        
        for campaign in self.campaigns:
            # Características categóricas
            category = campaign['category']
            technology = campaign['technology']
            channel = campaign['channel']
            vertical = campaign['vertical']
            complexity = campaign['complexity']
            priority = campaign['priority']
            
            # Características numéricas
            budget = campaign['budget']['amount']
            timeline_weeks = campaign['timeline']['duration_weeks']
            
            # Métricas como características
            metrics = campaign['metrics']
            conversion_rate = metrics.get('conversion_rate', 0)
            click_through_rate = metrics.get('click_through_rate', 0)
            engagement_rate = metrics.get('engagement_rate', 0)
            cost_per_acquisition = metrics.get('cost_per_acquisition', 0)
            customer_lifetime_value = metrics.get('customer_lifetime_value', 0)
            
            # Crear vector de características
            feature_vector = [
                self._encode_category(category),
                self._encode_technology(technology),
                self._encode_channel(channel),
                self._encode_vertical(vertical),
                self._encode_complexity(complexity),
                self._encode_priority(priority),
                budget,
                timeline_weeks,
                conversion_rate,
                click_through_rate,
                engagement_rate,
                cost_per_acquisition,
                customer_lifetime_value
            ]
            
            features.append(feature_vector)
            
            # Target: ROI como indicador de éxito
            roi = metrics.get('return_on_ad_spend', 0)
            success_probability = campaign['success_probability']
            
            # Combinar ROI y probabilidad de éxito como target compuesto
            target = (roi * success_probability) / 10  # Normalizar
            targets.append(target)
        
        self.X = np.array(features)
        self.y = np.array(targets)
        
        # Dividir datos en entrenamiento y prueba
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Escalar características
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
    
    def _encode_category(self, category: str) -> int:
        """Codifica categoría a número"""
        if 'category_encoder' not in self.encoders:
            self.encoders['category_encoder'] = LabelEncoder()
            categories = [c['category'] for c in self.campaigns]
            self.encoders['category_encoder'].fit(categories)
        
        return self.encoders['category_encoder'].transform([category])[0]
    
    def _encode_technology(self, technology: str) -> int:
        """Codifica tecnología a número"""
        if 'technology_encoder' not in self.encoders:
            self.encoders['technology_encoder'] = LabelEncoder()
            technologies = [c['technology'] for c in self.campaigns]
            self.encoders['technology_encoder'].fit(technologies)
        
        return self.encoders['technology_encoder'].transform([technology])[0]
    
    def _encode_channel(self, channel: str) -> int:
        """Codifica canal a número"""
        if 'channel_encoder' not in self.encoders:
            self.encoders['channel_encoder'] = LabelEncoder()
            channels = [c['channel'] for c in self.campaigns]
            self.encoders['channel_encoder'].fit(channels)
        
        return self.encoders['channel_encoder'].transform([channel])[0]
    
    def _encode_vertical(self, vertical: str) -> int:
        """Codifica vertical a número"""
        if 'vertical_encoder' not in self.encoders:
            self.encoders['vertical_encoder'] = LabelEncoder()
            verticals = [c['vertical'] for c in self.campaigns]
            self.encoders['vertical_encoder'].fit(verticals)
        
        return self.encoders['vertical_encoder'].transform([vertical])[0]
    
    def _encode_complexity(self, complexity: str) -> int:
        """Codifica complejidad a número"""
        complexity_map = {'Baja': 1, 'Media': 2, 'Alta': 3}
        return complexity_map.get(complexity, 2)
    
    def _encode_priority(self, priority: str) -> int:
        """Codifica prioridad a número"""
        priority_map = {'Baja': 1, 'Media': 2, 'Alta': 3, 'Crítica': 4}
        return priority_map.get(priority, 2)
    
    def train_models(self):
        """Entrena múltiples modelos de ML"""
        models_config = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(alpha=1.0)
        }
        
        results = {}
        
        for name, model in models_config.items():
            print(f"Entrenando modelo: {name}")
            
            # Entrenar modelo
            model.fit(self.X_train_scaled, self.y_train)
            
            # Predecir en conjunto de prueba
            y_pred = model.predict(self.X_test_scaled)
            
            # Calcular métricas
            mse = mean_squared_error(self.y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(self.y_test, y_pred)
            r2 = r2_score(self.y_test, y_pred)
            
            # Validación cruzada
            cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=5)
            
            results[name] = {
                'model': model,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            self.models[name] = model
        
        # Seleccionar mejor modelo
        best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
        self.best_model = results[best_model_name]['model']
        self.best_model_name = best_model_name
        
        print(f"\nMejor modelo: {best_model_name}")
        print(f"R² Score: {results[best_model_name]['r2']:.4f}")
        print(f"RMSE: {results[best_model_name]['rmse']:.4f}")
        
        # Calcular importancia de características
        if hasattr(self.best_model, 'feature_importances_'):
            feature_names = [
                'category', 'technology', 'channel', 'vertical', 'complexity', 'priority',
                'budget', 'timeline_weeks', 'conversion_rate', 'click_through_rate',
                'engagement_rate', 'cost_per_acquisition', 'customer_lifetime_value'
            ]
            
            self.feature_importance = dict(zip(feature_names, self.best_model.feature_importances_))
        
        return results
    
    def predict_success(self, campaign_data: Dict) -> Dict[str, Any]:
        """Predice el éxito de una campaña"""
        # Preparar características de la campaña
        features = [
            self._encode_category(campaign_data['category']),
            self._encode_technology(campaign_data['technology']),
            self._encode_channel(campaign_data['channel']),
            self._encode_vertical(campaign_data['vertical']),
            self._encode_complexity(campaign_data['complexity']),
            self._encode_priority(campaign_data['priority']),
            campaign_data['budget']['amount'],
            campaign_data['timeline']['duration_weeks'],
            campaign_data['metrics'].get('conversion_rate', 0),
            campaign_data['metrics'].get('click_through_rate', 0),
            campaign_data['metrics'].get('engagement_rate', 0),
            campaign_data['metrics'].get('cost_per_acquisition', 0),
            campaign_data['metrics'].get('customer_lifetime_value', 0)
        ]
        
        # Escalar características
        features_scaled = self.scaler.transform([features])
        
        # Predecir con mejor modelo
        prediction = self.best_model.predict(features_scaled)[0]
        
        # Convertir predicción a probabilidad de éxito (0-1)
        success_probability = min(1.0, max(0.0, prediction))
        
        # Calcular confianza basada en la varianza de predicciones de todos los modelos
        predictions = []
        for model in self.models.values():
            pred = model.predict(features_scaled)[0]
            predictions.append(pred)
        
        confidence = 1.0 - (np.std(predictions) / np.mean(predictions)) if np.mean(predictions) > 0 else 0.5
        
        # Generar recomendaciones basadas en la predicción
        recommendations = self._generate_ml_recommendations(campaign_data, success_probability, confidence)
        
        return {
            'predicted_success_probability': success_probability,
            'confidence': confidence,
            'model_used': self.best_model_name,
            'recommendations': recommendations,
            'feature_importance': self.feature_importance,
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _generate_ml_recommendations(self, campaign_data: Dict, success_prob: float, confidence: float) -> List[str]:
        """Genera recomendaciones basadas en la predicción ML"""
        recommendations = []
        
        # Recomendaciones basadas en probabilidad de éxito
        if success_prob >= 0.8:
            recommendations.append("🎯 **Alta probabilidad de éxito**: Esta campaña tiene excelentes perspectivas. Implementar inmediatamente.")
        elif success_prob >= 0.6:
            recommendations.append("✅ **Buena probabilidad de éxito**: La campaña es prometedora. Considerar implementación con monitoreo cuidadoso.")
        elif success_prob >= 0.4:
            recommendations.append("⚠️ **Probabilidad moderada**: Evaluar cuidadosamente antes de implementar. Considerar optimizaciones.")
        else:
            recommendations.append("❌ **Baja probabilidad de éxito**: No recomendado para implementación. Buscar alternativas.")
        
        # Recomendaciones basadas en confianza
        if confidence >= 0.8:
            recommendations.append("🔍 **Alta confianza**: La predicción es muy confiable.")
        elif confidence >= 0.6:
            recommendations.append("📊 **Confianza moderada**: La predicción es razonablemente confiable.")
        else:
            recommendations.append("⚠️ **Baja confianza**: La predicción tiene incertidumbre. Considerar más análisis.")
        
        # Recomendaciones basadas en características específicas
        budget = campaign_data['budget']['amount']
        if budget > 100000 and success_prob < 0.6:
            recommendations.append("💰 **Presupuesto alto con riesgo**: Considerar reducir el presupuesto o dividir en fases.")
        
        complexity = campaign_data['complexity']
        if complexity == 'Alta' and success_prob < 0.7:
            recommendations.append("🔧 **Complejidad alta**: Considerar simplificar la implementación o aumentar el equipo.")
        
        timeline = campaign_data['timeline']['duration_weeks']
        if timeline > 16 and success_prob < 0.6:
            recommendations.append("⏰ **Timeline largo**: Considerar acelerar la implementación o dividir en fases más pequeñas.")
        
        return recommendations
    
    def optimize_campaign(self, campaign_data: Dict) -> Dict[str, Any]:
        """Optimiza una campaña basada en predicciones ML"""
        original_prediction = self.predict_success(campaign_data)
        
        # Probar diferentes optimizaciones
        optimizations = []
        
        # Optimización 1: Reducir presupuesto
        if campaign_data['budget']['amount'] > 25000:
            optimized_campaign = campaign_data.copy()
            optimized_campaign['budget']['amount'] = campaign_data['budget']['amount'] * 0.8
            opt_prediction = self.predict_success(optimized_campaign)
            
            if opt_prediction['predicted_success_probability'] > original_prediction['predicted_success_probability']:
                optimizations.append({
                    'type': 'budget_reduction',
                    'description': 'Reducir presupuesto en 20%',
                    'original_probability': original_prediction['predicted_success_probability'],
                    'optimized_probability': opt_prediction['predicted_success_probability'],
                    'improvement': opt_prediction['predicted_success_probability'] - original_prediction['predicted_success_probability']
                })
        
        # Optimización 2: Reducir complejidad
        if campaign_data['complexity'] == 'Alta':
            optimized_campaign = campaign_data.copy()
            optimized_campaign['complexity'] = 'Media'
            opt_prediction = self.predict_success(optimized_campaign)
            
            if opt_prediction['predicted_success_probability'] > original_prediction['predicted_success_probability']:
                optimizations.append({
                    'type': 'complexity_reduction',
                    'description': 'Reducir complejidad a Media',
                    'original_probability': original_prediction['predicted_success_probability'],
                    'optimized_probability': opt_prediction['predicted_success_probability'],
                    'improvement': opt_prediction['predicted_success_probability'] - original_prediction['predicted_success_probability']
                })
        
        # Optimización 3: Acelerar timeline
        if campaign_data['timeline']['duration_weeks'] > 12:
            optimized_campaign = campaign_data.copy()
            optimized_campaign['timeline']['duration_weeks'] = campaign_data['timeline']['duration_weeks'] * 0.8
            opt_prediction = self.predict_success(optimized_campaign)
            
            if opt_prediction['predicted_success_probability'] > original_prediction['predicted_success_probability']:
                optimizations.append({
                    'type': 'timeline_acceleration',
                    'description': 'Acelerar timeline en 20%',
                    'original_probability': original_prediction['predicted_success_probability'],
                    'optimized_probability': opt_prediction['predicted_success_probability'],
                    'improvement': opt_prediction['predicted_success_probability'] - original_prediction['predicted_success_probability']
                })
        
        # Encontrar mejor optimización
        best_optimization = max(optimizations, key=lambda x: x['improvement']) if optimizations else None
        
        return {
            'original_prediction': original_prediction,
            'optimizations': optimizations,
            'best_optimization': best_optimization,
            'optimization_timestamp': datetime.now().isoformat()
        }
    
    def batch_predict(self, campaign_ids: List[int]) -> Dict[str, Any]:
        """Predice el éxito de múltiples campañas"""
        predictions = []
        
        for campaign_id in campaign_ids:
            campaign = next((c for c in self.campaigns if c['id'] == campaign_id), None)
            if campaign:
                prediction = self.predict_success(campaign)
                prediction['campaign_id'] = campaign_id
                prediction['campaign_name'] = campaign['name']
                predictions.append(prediction)
        
        # Análisis estadístico
        success_probs = [p['predicted_success_probability'] for p in predictions]
        confidences = [p['confidence'] for p in predictions]
        
        return {
            'predictions': predictions,
            'statistics': {
                'total_campaigns': len(predictions),
                'average_success_probability': np.mean(success_probs),
                'std_success_probability': np.std(success_probs),
                'average_confidence': np.mean(confidences),
                'high_success_campaigns': len([p for p in success_probs if p >= 0.8]),
                'low_success_campaigns': len([p for p in success_probs if p < 0.5])
            },
            'recommendations': self._generate_batch_recommendations(predictions)
        }
    
    def _generate_batch_recommendations(self, predictions: List[Dict]) -> List[str]:
        """Genera recomendaciones para un lote de predicciones"""
        recommendations = []
        
        high_success = [p for p in predictions if p['predicted_success_probability'] >= 0.8]
        low_success = [p for p in predictions if p['predicted_success_probability'] < 0.5]
        
        if high_success:
            recommendations.append(f"🚀 **{len(high_success)} campañas de alto éxito**: Priorizar implementación inmediata")
        
        if low_success:
            recommendations.append(f"⚠️ **{len(low_success)} campañas de bajo éxito**: Reconsiderar o optimizar antes de implementar")
        
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        if avg_confidence < 0.6:
            recommendations.append("📊 **Baja confianza general**: Considerar recopilar más datos para mejorar predicciones")
        
        return recommendations

def main():
    """Función principal de demostración"""
    print("=== SISTEMA DE ML PARA PREDICCIÓN DE ÉXITO ===")
    
    # Inicializar predictor
    predictor = MLSuccessPredictor()
    
    # Entrenar modelos
    print("Entrenando modelos de Machine Learning...")
    results = predictor.train_models()
    
    # Mostrar resultados de entrenamiento
    print("\n📊 RESULTADOS DE ENTRENAMIENTO")
    for name, result in results.items():
        print(f"{name}: R² = {result['r2']:.4f}, RMSE = {result['rmse']:.4f}")
    
    # Predecir éxito de campaña individual
    print("\n🔮 PREDICCIÓN DE CAMPAÑA INDIVIDUAL")
    campaign = predictor.campaigns[0]
    prediction = predictor.predict_success(campaign)
    
    print(f"Campaña: {campaign['name']}")
    print(f"Probabilidad de éxito predicha: {prediction['predicted_success_probability']:.2%}")
    print(f"Confianza: {prediction['confidence']:.2%}")
    print(f"Modelo usado: {prediction['model_used']}")
    
    print("\n💡 RECOMENDACIONES ML")
    for recommendation in prediction['recommendations']:
        print(f"• {recommendation}")
    
    # Optimizar campaña
    print("\n🔧 OPTIMIZACIÓN DE CAMPAÑA")
    optimization = predictor.optimize_campaign(campaign)
    
    if optimization['best_optimization']:
        best = optimization['best_optimization']
        print(f"Mejor optimización: {best['description']}")
        print(f"Mejora: {best['improvement']:.2%}")
    else:
        print("No se encontraron optimizaciones recomendadas")
    
    # Predicción por lotes
    print("\n📊 PREDICCIÓN POR LOTES")
    batch_predictions = predictor.batch_predict([1, 2, 3, 4, 5])
    
    stats = batch_predictions['statistics']
    print(f"Total de campañas: {stats['total_campaigns']}")
    print(f"Probabilidad promedio: {stats['average_success_probability']:.2%}")
    print(f"Campañas de alto éxito: {stats['high_success_campaigns']}")
    print(f"Campañas de bajo éxito: {stats['low_success_campaigns']}")
    
    print("\n💡 RECOMENDACIONES DE LOTE")
    for recommendation in batch_predictions['recommendations']:
        print(f"• {recommendation}")

if __name__ == "__main__":
    main()


