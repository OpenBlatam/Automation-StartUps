"""
Marketing Brain Brand Analytics
Sistema avanzado de análisis de marca
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class BrandAnalytics:
    def __init__(self):
        self.brand_data = {}
        self.brand_awareness = {}
        self.brand_perception = {}
        self.brand_equity = {}
        self.brand_models = {}
        self.brand_insights = {}
        self.brand_recommendations = {}
        
    def load_brand_data(self, brand_data):
        """Cargar datos de marca"""
        if isinstance(brand_data, str):
            if brand_data.endswith('.csv'):
                self.brand_data = pd.read_csv(brand_data)
            elif brand_data.endswith('.json'):
                with open(brand_data, 'r') as f:
                    data = json.load(f)
                self.brand_data = pd.DataFrame(data)
        else:
            self.brand_data = pd.DataFrame(brand_data)
        
        print(f"✅ Datos de marca cargados: {len(self.brand_data)} registros")
        return True
    
    def analyze_brand_awareness(self):
        """Analizar awareness de marca"""
        if self.brand_data.empty:
            return None
        
        # Análisis de awareness por segmento
        awareness_analysis = {}
        
        if 'brand_awareness' in self.brand_data.columns:
            # Análisis general de awareness
            awareness_scores = self.brand_data['brand_awareness']
            
            awareness_analysis['overall_awareness'] = {
                'avg_awareness': awareness_scores.mean(),
                'awareness_distribution': {
                    'high_awareness': len(awareness_scores[awareness_scores >= 4.0]),
                    'medium_awareness': len(awareness_scores[(awareness_scores >= 2.5) & (awareness_scores < 4.0)]),
                    'low_awareness': len(awareness_scores[awareness_scores < 2.5])
                },
                'awareness_trend': self._calculate_awareness_trend()
            }
        
        # Análisis por segmento demográfico
        if 'demographic_segment' in self.brand_data.columns:
            demographic_awareness = self.brand_data.groupby('demographic_segment')['brand_awareness'].agg(['mean', 'count']).reset_index()
            awareness_analysis['demographic_awareness'] = demographic_awareness.to_dict('records')
        
        # Análisis por región
        if 'region' in self.brand_data.columns:
            regional_awareness = self.brand_data.groupby('region')['brand_awareness'].agg(['mean', 'count']).reset_index()
            awareness_analysis['regional_awareness'] = regional_awareness.to_dict('records')
        
        # Análisis de canales de awareness
        if 'awareness_channel' in self.brand_data.columns:
            channel_awareness = self.brand_data.groupby('awareness_channel')['brand_awareness'].agg(['mean', 'count']).reset_index()
            awareness_analysis['channel_awareness'] = channel_awareness.to_dict('records')
        
        # Análisis de competidores
        if 'competitor_awareness' in self.brand_data.columns:
            competitor_analysis = self._analyze_competitor_awareness()
            awareness_analysis['competitor_awareness'] = competitor_analysis
        
        self.brand_awareness = awareness_analysis
        return awareness_analysis
    
    def _analyze_competitor_awareness(self):
        """Analizar awareness de competidores"""
        competitor_analysis = {}
        
        # Análisis de awareness relativo
        if 'competitor_awareness' in self.brand_data.columns:
            competitor_scores = self.brand_data['competitor_awareness']
            brand_scores = self.brand_data['brand_awareness']
            
            # Calcular awareness relativo
            relative_awareness = brand_scores.mean() - competitor_scores.mean()
            
            competitor_analysis = {
                'relative_awareness': relative_awareness,
                'awareness_gap': abs(relative_awareness),
                'competitive_position': 'leading' if relative_awareness > 0.5 else 'competitive' if relative_awareness > -0.5 else 'lagging'
            }
        
        return competitor_analysis
    
    def _calculate_awareness_trend(self):
        """Calcular tendencia de awareness"""
        if 'date' in self.brand_data.columns and 'brand_awareness' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_awareness = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_awareness'].mean()
            
            if len(monthly_awareness) > 1:
                trend = monthly_awareness.iloc[-1] - monthly_awareness.iloc[0]
                return 'increasing' if trend > 0.1 else 'decreasing' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def analyze_brand_perception(self):
        """Analizar percepción de marca"""
        if self.brand_data.empty:
            return None
        
        # Análisis de atributos de marca
        perception_analysis = {}
        
        # Atributos de marca
        brand_attributes = ['quality', 'value', 'innovation', 'trust', 'reputation', 'customer_service']
        available_attributes = [attr for attr in brand_attributes if attr in self.brand_data.columns]
        
        if available_attributes:
            attribute_scores = {}
            for attribute in available_attributes:
                scores = self.brand_data[attribute]
                attribute_scores[attribute] = {
                    'avg_score': scores.mean(),
                    'score_distribution': {
                        'excellent': len(scores[scores >= 4.5]),
                        'good': len(scores[(scores >= 3.5) & (scores < 4.5)]),
                        'average': len(scores[(scores >= 2.5) & (scores < 3.5)]),
                        'poor': len(scores[(scores >= 1.5) & (scores < 2.5)]),
                        'very_poor': len(scores[scores < 1.5])
                    }
                }
            
            perception_analysis['attribute_scores'] = attribute_scores
            
            # Análisis de fortalezas y debilidades
            strengths_weaknesses = self._analyze_strengths_weaknesses(attribute_scores)
            perception_analysis['strengths_weaknesses'] = strengths_weaknesses
        
        # Análisis de sentimiento
        if 'brand_sentiment' in self.brand_data.columns:
            sentiment_analysis = self._analyze_brand_sentiment()
            perception_analysis['sentiment_analysis'] = sentiment_analysis
        
        # Análisis de asociaciones de marca
        if 'brand_associations' in self.brand_data.columns:
            associations_analysis = self._analyze_brand_associations()
            perception_analysis['associations_analysis'] = associations_analysis
        
        # Análisis de personalidad de marca
        if 'brand_personality' in self.brand_data.columns:
            personality_analysis = self._analyze_brand_personality()
            perception_analysis['personality_analysis'] = personality_analysis
        
        self.brand_perception = perception_analysis
        return perception_analysis
    
    def _analyze_strengths_weaknesses(self, attribute_scores):
        """Analizar fortalezas y debilidades de marca"""
        strengths = []
        weaknesses = []
        
        for attribute, scores in attribute_scores.items():
            avg_score = scores['avg_score']
            
            if avg_score >= 4.0:
                strengths.append({
                    'attribute': attribute,
                    'score': avg_score,
                    'strength_level': 'high'
                })
            elif avg_score <= 2.5:
                weaknesses.append({
                    'attribute': attribute,
                    'score': avg_score,
                    'weakness_level': 'high'
                })
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'strength_count': len(strengths),
            'weakness_count': len(weaknesses)
        }
    
    def _analyze_brand_sentiment(self):
        """Analizar sentimiento de marca"""
        sentiment_analysis = {}
        
        if 'brand_sentiment' in self.brand_data.columns:
            sentiment_scores = self.brand_data['brand_sentiment']
            
            sentiment_analysis = {
                'avg_sentiment': sentiment_scores.mean(),
                'sentiment_distribution': {
                    'very_positive': len(sentiment_scores[sentiment_scores >= 4.5]),
                    'positive': len(sentiment_scores[(sentiment_scores >= 3.5) & (sentiment_scores < 4.5)]),
                    'neutral': len(sentiment_scores[(sentiment_scores >= 2.5) & (sentiment_scores < 3.5)]),
                    'negative': len(sentiment_scores[(sentiment_scores >= 1.5) & (sentiment_scores < 2.5)]),
                    'very_negative': len(sentiment_scores[sentiment_scores < 1.5])
                },
                'sentiment_trend': self._calculate_sentiment_trend()
            }
        
        return sentiment_analysis
    
    def _analyze_brand_associations(self):
        """Analizar asociaciones de marca"""
        associations_analysis = {}
        
        if 'brand_associations' in self.brand_data.columns:
            # Análisis de asociaciones más mencionadas
            associations_frequency = self.brand_data['brand_associations'].value_counts()
            
            associations_analysis = {
                'top_associations': associations_frequency.head(10).to_dict(),
                'association_categories': self._categorize_brand_associations(),
                'unique_associations': len(associations_frequency)
            }
        
        return associations_analysis
    
    def _analyze_brand_personality(self):
        """Analizar personalidad de marca"""
        personality_analysis = {}
        
        if 'brand_personality' in self.brand_data.columns:
            # Análisis de personalidad de marca
            personality_scores = self.brand_data['brand_personality']
            
            personality_analysis = {
                'avg_personality_score': personality_scores.mean(),
                'personality_distribution': {
                    'strong_personality': len(personality_scores[personality_scores >= 4.0]),
                    'moderate_personality': len(personality_scores[(personality_scores >= 2.5) & (personality_scores < 4.0)]),
                    'weak_personality': len(personality_scores[personality_scores < 2.5])
                },
                'personality_trend': self._calculate_personality_trend()
            }
        
        return personality_analysis
    
    def _categorize_brand_associations(self):
        """Categorizar asociaciones de marca"""
        # Categorías predefinidas de asociaciones
        association_categories = {
            'Quality': ['quality', 'premium', 'luxury', 'excellent'],
            'Value': ['value', 'affordable', 'cheap', 'expensive'],
            'Innovation': ['innovation', 'modern', 'advanced', 'cutting-edge'],
            'Trust': ['trust', 'reliable', 'dependable', 'safe'],
            'Emotion': ['fun', 'exciting', 'emotional', 'inspiring']
        }
        
        categorized_associations = {}
        for category, keywords in association_categories.items():
            count = 0
            for association in self.brand_data['brand_associations']:
                if any(keyword in association.lower() for keyword in keywords):
                    count += 1
            categorized_associations[category] = count
        
        return categorized_associations
    
    def _calculate_sentiment_trend(self):
        """Calcular tendencia de sentimiento"""
        if 'date' in self.brand_data.columns and 'brand_sentiment' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_sentiment = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_sentiment'].mean()
            
            if len(monthly_sentiment) > 1:
                trend = monthly_sentiment.iloc[-1] - monthly_sentiment.iloc[0]
                return 'improving' if trend > 0.1 else 'declining' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def _calculate_personality_trend(self):
        """Calcular tendencia de personalidad"""
        if 'date' in self.brand_data.columns and 'brand_personality' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_personality = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_personality'].mean()
            
            if len(monthly_personality) > 1:
                trend = monthly_personality.iloc[-1] - monthly_personality.iloc[0]
                return 'strengthening' if trend > 0.1 else 'weakening' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def analyze_brand_equity(self):
        """Analizar equity de marca"""
        if self.brand_data.empty:
            return None
        
        # Análisis de equity de marca
        equity_analysis = {}
        
        # Calcular métricas de equity
        if 'brand_equity' in self.brand_data.columns:
            equity_scores = self.brand_data['brand_equity']
            
            equity_analysis['overall_equity'] = {
                'avg_equity': equity_scores.mean(),
                'equity_distribution': {
                    'high_equity': len(equity_scores[equity_scores >= 4.0]),
                    'medium_equity': len(equity_scores[(equity_scores >= 2.5) & (equity_scores < 4.0)]),
                    'low_equity': len(equity_scores[equity_scores < 2.5])
                },
                'equity_trend': self._calculate_equity_trend()
            }
        
        # Análisis de componentes de equity
        equity_components = self._analyze_equity_components()
        equity_analysis['equity_components'] = equity_components
        
        # Análisis de valor de marca
        brand_value_analysis = self._analyze_brand_value()
        equity_analysis['brand_value'] = brand_value_analysis
        
        # Análisis de lealtad de marca
        brand_loyalty_analysis = self._analyze_brand_loyalty()
        equity_analysis['brand_loyalty'] = brand_loyalty_analysis
        
        self.brand_equity = equity_analysis
        return equity_analysis
    
    def _analyze_equity_components(self):
        """Analizar componentes de equity"""
        components_analysis = {}
        
        # Componentes de equity
        equity_components = ['brand_awareness', 'brand_perception', 'brand_loyalty', 'brand_associations']
        available_components = [comp for comp in equity_components if comp in self.brand_data.columns]
        
        if available_components:
            component_scores = {}
            for component in available_components:
                scores = self.brand_data[component]
                component_scores[component] = {
                    'avg_score': scores.mean(),
                    'score_std': scores.std(),
                    'score_range': [scores.min(), scores.max()]
                }
            
            components_analysis = {
                'component_scores': component_scores,
                'strongest_component': max(component_scores, key=lambda x: component_scores[x]['avg_score']),
                'weakest_component': min(component_scores, key=lambda x: component_scores[x]['avg_score'])
            }
        
        return components_analysis
    
    def _analyze_brand_value(self):
        """Analizar valor de marca"""
        brand_value_analysis = {}
        
        if 'brand_value' in self.brand_data.columns:
            value_scores = self.brand_data['brand_value']
            
            brand_value_analysis = {
                'avg_value': value_scores.mean(),
                'value_distribution': {
                    'high_value': len(value_scores[value_scores >= 4.0]),
                    'medium_value': len(value_scores[(value_scores >= 2.5) & (value_scores < 4.0)]),
                    'low_value': len(value_scores[value_scores < 2.5])
                },
                'value_trend': self._calculate_value_trend()
            }
        
        return brand_value_analysis
    
    def _analyze_brand_loyalty(self):
        """Analizar lealtad de marca"""
        brand_loyalty_analysis = {}
        
        if 'brand_loyalty' in self.brand_data.columns:
            loyalty_scores = self.brand_data['brand_loyalty']
            
            brand_loyalty_analysis = {
                'avg_loyalty': loyalty_scores.mean(),
                'loyalty_distribution': {
                    'highly_loyal': len(loyalty_scores[loyalty_scores >= 4.5]),
                    'loyal': len(loyalty_scores[(loyalty_scores >= 3.5) & (loyalty_scores < 4.5)]),
                    'moderate': len(loyalty_scores[(loyalty_scores >= 2.5) & (loyalty_scores < 3.5)]),
                    'low_loyalty': len(loyalty_scores[(loyalty_scores >= 1.5) & (loyalty_scores < 2.5)]),
                    'no_loyalty': len(loyalty_scores[loyalty_scores < 1.5])
                },
                'loyalty_trend': self._calculate_loyalty_trend()
            }
        
        return brand_loyalty_analysis
    
    def _calculate_equity_trend(self):
        """Calcular tendencia de equity"""
        if 'date' in self.brand_data.columns and 'brand_equity' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_equity = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_equity'].mean()
            
            if len(monthly_equity) > 1:
                trend = monthly_equity.iloc[-1] - monthly_equity.iloc[0]
                return 'increasing' if trend > 0.1 else 'decreasing' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def _calculate_value_trend(self):
        """Calcular tendencia de valor"""
        if 'date' in self.brand_data.columns and 'brand_value' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_value = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_value'].mean()
            
            if len(monthly_value) > 1:
                trend = monthly_value.iloc[-1] - monthly_value.iloc[0]
                return 'increasing' if trend > 0.1 else 'decreasing' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def _calculate_loyalty_trend(self):
        """Calcular tendencia de lealtad"""
        if 'date' in self.brand_data.columns and 'brand_loyalty' in self.brand_data.columns:
            # Análisis de tendencia temporal
            self.brand_data['date'] = pd.to_datetime(self.brand_data['date'])
            monthly_loyalty = self.brand_data.groupby(self.brand_data['date'].dt.to_period('M'))['brand_loyalty'].mean()
            
            if len(monthly_loyalty) > 1:
                trend = monthly_loyalty.iloc[-1] - monthly_loyalty.iloc[0]
                return 'increasing' if trend > 0.1 else 'decreasing' if trend < -0.1 else 'stable'
        
        return 'stable'
    
    def build_brand_prediction_model(self, target_variable='brand_equity'):
        """Construir modelo de predicción de marca"""
        if target_variable not in self.brand_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.brand_data.columns if col != target_variable and col not in ['date', 'brand_associations']]
        X = self.brand_data[feature_columns]
        y = self.brand_data[target_variable]
        
        # Codificar variables categóricas
        label_encoders = {}
        for column in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column].astype(str))
            label_encoders[column] = le
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar datos
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Entrenar modelo
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        model_metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.brand_models['brand_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_brand_insights(self):
        """Generar insights de marca"""
        insights = []
        
        # Insights de awareness
        if self.brand_awareness:
            overall_awareness = self.brand_awareness.get('overall_awareness', {})
            avg_awareness = overall_awareness.get('avg_awareness', 0)
            
            if avg_awareness < 3.0:
                insights.append({
                    'category': 'Brand Awareness',
                    'insight': f'Awareness promedio bajo: {avg_awareness:.2f}',
                    'recommendation': 'Implementar estrategias para aumentar awareness',
                    'priority': 'high'
                })
            
            awareness_trend = overall_awareness.get('awareness_trend', 'stable')
            if awareness_trend == 'decreasing':
                insights.append({
                    'category': 'Brand Awareness',
                    'insight': 'Tendencia decreciente de awareness',
                    'recommendation': 'Revisar estrategias de awareness',
                    'priority': 'high'
                })
        
        # Insights de percepción
        if self.brand_perception:
            strengths_weaknesses = self.brand_perception.get('strengths_weaknesses', {})
            weaknesses = strengths_weaknesses.get('weaknesses', [])
            
            if weaknesses:
                insights.append({
                    'category': 'Brand Perception',
                    'insight': f'{len(weaknesses)} atributos con puntuación baja',
                    'recommendation': 'Mejorar atributos de marca con puntuación baja',
                    'priority': 'medium'
                })
            
            sentiment_analysis = self.brand_perception.get('sentiment_analysis', {})
            avg_sentiment = sentiment_analysis.get('avg_sentiment', 0)
            
            if avg_sentiment < 3.0:
                insights.append({
                    'category': 'Brand Sentiment',
                    'insight': f'Sentimiento promedio bajo: {avg_sentiment:.2f}',
                    'recommendation': 'Mejorar sentimiento de marca',
                    'priority': 'high'
                })
        
        # Insights de equity
        if self.brand_equity:
            overall_equity = self.brand_equity.get('overall_equity', {})
            avg_equity = overall_equity.get('avg_equity', 0)
            
            if avg_equity < 3.0:
                insights.append({
                    'category': 'Brand Equity',
                    'insight': f'Equity promedio bajo: {avg_equity:.2f}',
                    'recommendation': 'Implementar estrategias para fortalecer equity',
                    'priority': 'high'
                })
            
            equity_components = self.brand_equity.get('equity_components', {})
            weakest_component = equity_components.get('weakest_component', '')
            
            if weakest_component:
                insights.append({
                    'category': 'Brand Equity',
                    'insight': f'Componente más débil: {weakest_component}',
                    'recommendation': f'Fortalecer {weakest_component} para mejorar equity',
                    'priority': 'medium'
                })
        
        # Insights de competidores
        if self.brand_awareness:
            competitor_awareness = self.brand_awareness.get('competitor_awareness', {})
            competitive_position = competitor_awareness.get('competitive_position', '')
            
            if competitive_position == 'lagging':
                insights.append({
                    'category': 'Competitive Position',
                    'insight': 'Posición competitiva rezagada',
                    'recommendation': 'Implementar estrategias para mejorar posición competitiva',
                    'priority': 'high'
                })
        
        self.brand_insights = insights
        return insights
    
    def create_brand_dashboard(self):
        """Crear dashboard de análisis de marca"""
        if not self.brand_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Brand Awareness', 'Brand Perception',
                          'Brand Equity', 'Brand Sentiment'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de awareness de marca
        if self.brand_awareness:
            overall_awareness = self.brand_awareness.get('overall_awareness', {})
            awareness_dist = overall_awareness.get('awareness_distribution', {})
            
            if awareness_dist:
                categories = list(awareness_dist.keys())
                values = list(awareness_dist.values())
                
                fig.add_trace(
                    go.Bar(x=categories, y=values, name='Brand Awareness'),
                    row=1, col=1
                )
        
        # Gráfico de percepción de marca
        if self.brand_perception:
            attribute_scores = self.brand_perception.get('attribute_scores', {})
            
            if attribute_scores:
                attributes = list(attribute_scores.keys())
                scores = [data['avg_score'] for data in attribute_scores.values()]
                
                fig.add_trace(
                    go.Pie(labels=attributes, values=scores, name='Brand Perception'),
                    row=1, col=2
                )
        
        # Gráfico de equity de marca
        if self.brand_equity:
            overall_equity = self.brand_equity.get('overall_equity', {})
            equity_dist = overall_equity.get('equity_distribution', {})
            
            if equity_dist:
                categories = list(equity_dist.keys())
                values = list(equity_dist.values())
                
                fig.add_trace(
                    go.Bar(x=categories, y=values, name='Brand Equity'),
                    row=2, col=1
                )
        
        # Gráfico de sentimiento de marca
        if self.brand_perception:
            sentiment_analysis = self.brand_perception.get('sentiment_analysis', {})
            sentiment_dist = sentiment_analysis.get('sentiment_distribution', {})
            
            if sentiment_dist:
                categories = list(sentiment_dist.keys())
                values = list(sentiment_dist.values())
                
                fig.add_trace(
                    go.Bar(x=categories, y=values, name='Brand Sentiment'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de Marca",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_brand_analysis(self, filename='brand_analytics_analysis.json'):
        """Exportar análisis de marca"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'brand_awareness': self.brand_awareness,
            'brand_perception': self.brand_perception,
            'brand_equity': self.brand_equity,
            'brand_models': {k: {'metrics': v['metrics']} for k, v in self.brand_models.items()},
            'brand_insights': self.brand_insights,
            'summary': {
                'total_responses': len(self.brand_data),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de marca exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de marca
    brand_analytics = BrandAnalytics()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'brand_awareness': np.random.uniform(1, 5, 1000),
        'brand_perception': np.random.uniform(1, 5, 1000),
        'brand_equity': np.random.uniform(1, 5, 1000),
        'brand_sentiment': np.random.uniform(1, 5, 1000),
        'brand_loyalty': np.random.uniform(1, 5, 1000),
        'brand_value': np.random.uniform(1, 5, 1000),
        'brand_personality': np.random.uniform(1, 5, 1000),
        'quality': np.random.uniform(1, 5, 1000),
        'value': np.random.uniform(1, 5, 1000),
        'innovation': np.random.uniform(1, 5, 1000),
        'trust': np.random.uniform(1, 5, 1000),
        'reputation': np.random.uniform(1, 5, 1000),
        'customer_service': np.random.uniform(1, 5, 1000),
        'competitor_awareness': np.random.uniform(1, 5, 1000),
        'demographic_segment': np.random.choice(['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers'], 1000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
        'awareness_channel': np.random.choice(['TV', 'Digital', 'Social Media', 'Print'], 1000),
        'brand_associations': np.random.choice(['Quality', 'Innovation', 'Trust', 'Value'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de marca
    print("📊 Cargando datos de marca...")
    brand_analytics.load_brand_data(sample_data)
    
    # Analizar awareness de marca
    print("👁️ Analizando awareness de marca...")
    brand_awareness = brand_analytics.analyze_brand_awareness()
    
    # Analizar percepción de marca
    print("🧠 Analizando percepción de marca...")
    brand_perception = brand_analytics.analyze_brand_perception()
    
    # Analizar equity de marca
    print("💰 Analizando equity de marca...")
    brand_equity = brand_analytics.analyze_brand_equity()
    
    # Construir modelo de predicción de marca
    print("🔮 Construyendo modelo de predicción de marca...")
    brand_model = brand_analytics.build_brand_prediction_model()
    
    # Generar insights de marca
    print("💡 Generando insights de marca...")
    brand_insights = brand_analytics.generate_brand_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de análisis de marca...")
    dashboard = brand_analytics.create_brand_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de marca...")
    export_data = brand_analytics.export_brand_analysis()
    
    print("✅ Sistema de análisis de marca completado!")






