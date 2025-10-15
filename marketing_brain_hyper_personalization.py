"""
Marketing Brain Hyper Personalization Engine
Sistema de personalización extrema para marketing
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Embedding, LSTM
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class HyperPersonalizationEngine:
    def __init__(self):
        self.customer_profiles = {}
        self.personalization_models = {}
        self.content_recommendations = {}
        self.engagement_predictions = {}
        self.dynamic_pricing = {}
        self.optimization_results = {}
        
    def create_customer_profiles(self, customer_data):
        """Crear perfiles detallados de clientes"""
        profiles = {}
        
        for customer_id, data in customer_data.groupby('customer_id'):
            profile = {
                'demographics': {
                    'age': data['age'].iloc[0] if 'age' in data.columns else None,
                    'gender': data['gender'].iloc[0] if 'gender' in data.columns else None,
                    'location': data['location'].iloc[0] if 'location' in data.columns else None,
                    'income': data['income'].iloc[0] if 'income' in data.columns else None
                },
                'behavioral': {
                    'purchase_history': data['amount'].tolist(),
                    'browsing_patterns': data['page_views'].tolist() if 'page_views' in data.columns else [],
                    'engagement_score': data['engagement_score'].mean() if 'engagement_score' in data.columns else 0,
                    'preferred_categories': data['category'].value_counts().to_dict() if 'category' in data.columns else {}
                },
                'preferences': {
                    'communication_channel': data['preferred_channel'].mode().iloc[0] if 'preferred_channel' in data.columns else 'email',
                    'content_type': data['content_type'].mode().iloc[0] if 'content_type' in data.columns else 'text',
                    'optimal_time': data['optimal_time'].mode().iloc[0] if 'optimal_time' in data.columns else 'morning'
                },
                'predictive': {
                    'lifetime_value': self._calculate_clv(data),
                    'churn_probability': self._calculate_churn_probability(data),
                    'next_purchase_probability': self._calculate_next_purchase_probability(data),
                    'recommended_products': self._get_recommended_products(data)
                }
            }
            profiles[customer_id] = profile
        
        self.customer_profiles = profiles
        return profiles
    
    def _calculate_clv(self, customer_data):
        """Calcular valor de vida del cliente"""
        avg_order_value = customer_data['amount'].mean()
        purchase_frequency = len(customer_data) / 365  # Compras por día
        customer_lifespan = 365  # Días
        return avg_order_value * purchase_frequency * customer_lifespan
    
    def _calculate_churn_probability(self, customer_data):
        """Calcular probabilidad de churn"""
        days_since_last_purchase = (datetime.now() - pd.to_datetime(customer_data['purchase_date'].max())).days
        purchase_frequency = len(customer_data) / 365
        
        # Modelo simplificado de churn
        churn_score = (days_since_last_purchase / 30) * 0.4 + (1 / (purchase_frequency + 1)) * 0.6
        return min(churn_score, 1.0)
    
    def _calculate_next_purchase_probability(self, customer_data):
        """Calcular probabilidad de próxima compra"""
        avg_days_between_purchases = customer_data['purchase_date'].diff().dt.days.mean()
        days_since_last = (datetime.now() - pd.to_datetime(customer_data['purchase_date'].max())).days
        
        if avg_days_between_purchases > 0:
            probability = 1 - (days_since_last / avg_days_between_purchases)
            return max(0, min(probability, 1))
        return 0.5
    
    def _get_recommended_products(self, customer_data):
        """Obtener productos recomendados"""
        if 'category' in customer_data.columns:
            top_categories = customer_data['category'].value_counts().head(3).index.tolist()
            return top_categories
        return []
    
    def build_personalization_models(self, training_data):
        """Construir modelos de personalización"""
        models = {}
        
        # Modelo de recomendación de contenido
        X_content = training_data[['age', 'gender_encoded', 'income', 'engagement_score']]
        y_content = training_data['content_preference']
        
        content_model = RandomForestClassifier(n_estimators=100, random_state=42)
        content_model.fit(X_content, y_content)
        models['content_recommendation'] = content_model
        
        # Modelo de predicción de engagement
        X_engagement = training_data[['time_of_day', 'day_of_week', 'content_type_encoded', 'channel_encoded']]
        y_engagement = training_data['engagement_score']
        
        engagement_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        engagement_model.fit(X_engagement, y_engagement)
        models['engagement_prediction'] = engagement_model
        
        # Modelo de pricing dinámico
        X_pricing = training_data[['customer_segment', 'product_category', 'demand_level', 'competitor_price']]
        y_pricing = training_data['optimal_price']
        
        pricing_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        pricing_model.fit(X_pricing, y_pricing)
        models['dynamic_pricing'] = pricing_model
        
        self.personalization_models = models
        return models
    
    def generate_personalized_content(self, customer_id, content_type='email'):
        """Generar contenido personalizado"""
        if customer_id not in self.customer_profiles:
            return None
        
        profile = self.customer_profiles[customer_id]
        
        # Generar contenido basado en perfil
        content = {
            'subject': self._generate_personalized_subject(profile, content_type),
            'body': self._generate_personalized_body(profile, content_type),
            'cta': self._generate_personalized_cta(profile, content_type),
            'images': self._select_personalized_images(profile, content_type),
            'timing': self._calculate_optimal_timing(profile, content_type)
        }
        
        return content
    
    def _generate_personalized_subject(self, profile, content_type):
        """Generar asunto personalizado"""
        templates = {
            'email': [
                f"¡{profile['demographics']['gender']}, descubre ofertas exclusivas!",
                f"Productos perfectos para ti en {profile['demographics']['location']}",
                f"Basado en tu historial, te recomendamos..."
            ],
            'social': [
                f"¿Sabías que en {profile['demographics']['location']} aman estos productos?",
                f"Para alguien como tú, esto es perfecto",
                f"Tu estilo, nuestros productos"
            ]
        }
        
        return np.random.choice(templates.get(content_type, templates['email']))
    
    def _generate_personalized_body(self, profile, content_type):
        """Generar cuerpo personalizado"""
        body = f"""
        Hola {profile['demographics']['gender']},
        
        Basado en tu historial de compras y preferencias, hemos seleccionado productos especialmente para ti:
        
        """
        
        # Agregar productos recomendados
        if profile['predictive']['recommended_products']:
            body += "Productos recomendados:\n"
            for product in profile['predictive']['recommended_products']:
                body += f"• {product}\n"
        
        # Agregar ofertas personalizadas
        if profile['predictive']['lifetime_value'] > 1000:
            body += "\n¡Como cliente VIP, tienes acceso a ofertas exclusivas!"
        
        return body
    
    def _generate_personalized_cta(self, profile, content_type):
        """Generar call-to-action personalizado"""
        ctas = {
            'high_value': "Descubre tu oferta exclusiva",
            'medium_value': "Explora productos para ti",
            'low_value': "Ver ofertas especiales"
        }
        
        clv = profile['predictive']['lifetime_value']
        if clv > 1000:
            return ctas['high_value']
        elif clv > 500:
            return ctas['medium_value']
        else:
            return ctas['low_value']
    
    def _select_personalized_images(self, profile, content_type):
        """Seleccionar imágenes personalizadas"""
        # Lógica simplificada para selección de imágenes
        image_categories = profile['behavioral']['preferred_categories']
        if image_categories:
            top_category = max(image_categories, key=image_categories.get)
            return [f"images/{top_category}_1.jpg", f"images/{top_category}_2.jpg"]
        return ["images/default_1.jpg", "images/default_2.jpg"]
    
    def _calculate_optimal_timing(self, profile, content_type):
        """Calcular timing óptimo"""
        preferred_time = profile['preferences']['optimal_time']
        timing_map = {
            'morning': '09:00',
            'afternoon': '14:00',
            'evening': '19:00',
            'night': '21:00'
        }
        return timing_map.get(preferred_time, '14:00')
    
    def optimize_campaign_personalization(self, campaign_data):
        """Optimizar personalización de campaña"""
        optimization_results = {}
        
        for campaign_id, data in campaign_data.items():
            # Analizar performance por segmento
            segment_performance = data.groupby('customer_segment').agg({
                'open_rate': 'mean',
                'click_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum'
            })
            
            # Identificar mejores segmentos
            best_segments = segment_performance.nlargest(3, 'conversion_rate')
            
            # Optimizar timing
            timing_analysis = data.groupby('send_time').agg({
                'open_rate': 'mean',
                'click_rate': 'mean'
            })
            optimal_timing = timing_analysis.idxmax()['open_rate']
            
            # Optimizar contenido
            content_analysis = data.groupby('content_type').agg({
                'engagement_score': 'mean',
                'conversion_rate': 'mean'
            })
            optimal_content = content_analysis.idxmax()['engagement_score']
            
            optimization_results[campaign_id] = {
                'best_segments': best_segments.to_dict(),
                'optimal_timing': optimal_timing,
                'optimal_content': optimal_content,
                'recommendations': self._generate_optimization_recommendations(
                    segment_performance, timing_analysis, content_analysis
                )
            }
        
        self.optimization_results = optimization_results
        return optimization_results
    
    def _generate_optimization_recommendations(self, segment_perf, timing_perf, content_perf):
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        # Recomendaciones de segmentación
        if segment_perf['conversion_rate'].std() > 0.1:
            recommendations.append("Considerar segmentación más granular para mejorar conversión")
        
        # Recomendaciones de timing
        if timing_perf['open_rate'].std() > 0.05:
            recommendations.append("Optimizar timing de envío basado en análisis de engagement")
        
        # Recomendaciones de contenido
        if content_perf['engagement_score'].std() > 0.1:
            recommendations.append("Personalizar contenido por tipo de audiencia")
        
        return recommendations
    
    def create_personalization_dashboard(self):
        """Crear dashboard de personalización"""
        if not self.customer_profiles:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribución de CLV', 'Segmentos de Clientes',
                          'Probabilidad de Churn', 'Preferencias de Contenido'),
            specs=[[{"type": "histogram"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de CLV
        clv_values = [profile['predictive']['lifetime_value'] for profile in self.customer_profiles.values()]
        fig.add_trace(
            go.Histogram(x=clv_values, name='CLV Distribution'),
            row=1, col=1
        )
        
        # Gráfico de segmentos
        segments = {}
        for profile in self.customer_profiles.values():
            clv = profile['predictive']['lifetime_value']
            if clv > 1000:
                segment = 'High Value'
            elif clv > 500:
                segment = 'Medium Value'
            else:
                segment = 'Low Value'
            segments[segment] = segments.get(segment, 0) + 1
        
        fig.add_trace(
            go.Pie(labels=list(segments.keys()), values=list(segments.values()), name='Segments'),
            row=1, col=2
        )
        
        # Gráfico de churn
        churn_values = [profile['predictive']['churn_probability'] for profile in self.customer_profiles.values()]
        churn_bins = pd.cut(churn_values, bins=4, labels=['Bajo', 'Medio', 'Alto', 'Crítico'])
        churn_counts = churn_bins.value_counts()
        
        fig.add_trace(
            go.Bar(x=churn_counts.index, y=churn_counts.values, name='Churn Risk'),
            row=2, col=1
        )
        
        # Gráfico de preferencias
        content_prefs = {}
        for profile in self.customer_profiles.values():
            pref = profile['preferences']['content_type']
            content_prefs[pref] = content_prefs.get(pref, 0) + 1
        
        fig.add_trace(
            go.Bar(x=list(content_prefs.keys()), y=list(content_prefs.values()), name='Content Preferences'),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Dashboard de Personalización Hiper-Avanzada",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_personalization_data(self, filename='hyper_personalization_data.json'):
        """Exportar datos de personalización"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'customer_profiles': self.customer_profiles,
            'optimization_results': self.optimization_results,
            'summary': {
                'total_customers': len(self.customer_profiles),
                'avg_clv': np.mean([p['predictive']['lifetime_value'] for p in self.customer_profiles.values()]),
                'avg_churn_probability': np.mean([p['predictive']['churn_probability'] for p in self.customer_profiles.values()])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Datos de personalización exportados a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del motor de personalización
    personalization_engine = HyperPersonalizationEngine()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 100, 1000),
        'age': np.random.randint(18, 65, 1000),
        'gender': np.random.choice(['M', 'F'], 1000),
        'location': np.random.choice(['Madrid', 'Barcelona', 'Valencia'], 1000),
        'income': np.random.normal(30000, 10000, 1000),
        'amount': np.random.normal(100, 30, 1000),
        'category': np.random.choice(['Electronics', 'Fashion', 'Home', 'Sports'], 1000),
        'engagement_score': np.random.uniform(0, 10, 1000),
        'preferred_channel': np.random.choice(['email', 'social', 'sms'], 1000),
        'content_type': np.random.choice(['text', 'video', 'image'], 1000),
        'optimal_time': np.random.choice(['morning', 'afternoon', 'evening'], 1000),
        'purchase_date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Crear perfiles de clientes
    print("👤 Creando perfiles de clientes...")
    profiles = personalization_engine.create_customer_profiles(sample_data)
    
    # Generar contenido personalizado
    print("📝 Generando contenido personalizado...")
    personalized_content = personalization_engine.generate_personalized_content(1, 'email')
    
    # Crear dashboard
    print("📊 Creando dashboard de personalización...")
    dashboard = personalization_engine.create_personalization_dashboard()
    
    # Exportar datos
    print("💾 Exportando datos de personalización...")
    export_data = personalization_engine.export_personalization_data()
    
    print("✅ Sistema de personalización hiper-avanzada completado!")




