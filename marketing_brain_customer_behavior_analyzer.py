"""
Marketing Brain Customer Behavior Analyzer
Sistema avanzado de análisis de comportamiento del cliente
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

class CustomerBehaviorAnalyzer:
    def __init__(self):
        self.customer_data = None
        self.behavior_models = {}
        self.segments = {}
        self.anomalies = []
        self.insights = {}
        
    def load_customer_data(self, data_source):
        """Cargar datos de comportamiento del cliente"""
        try:
            if isinstance(data_source, str):
                if data_source.endswith('.csv'):
                    self.customer_data = pd.read_csv(data_source)
                elif data_source.endswith('.json'):
                    with open(data_source, 'r') as f:
                        data = json.load(f)
                    self.customer_data = pd.DataFrame(data)
            else:
                self.customer_data = pd.DataFrame(data_source)
            
            print(f"✅ Datos cargados: {len(self.customer_data)} registros")
            return True
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False
    
    def analyze_purchase_patterns(self):
        """Analizar patrones de compra"""
        if self.customer_data is None:
            return None
        
        # Análisis de frecuencia de compra
        purchase_frequency = self.customer_data.groupby('customer_id')['purchase_date'].count()
        
        # Análisis de valor de compra
        purchase_value = self.customer_data.groupby('customer_id')['amount'].sum()
        
        # Análisis de estacionalidad
        self.customer_data['month'] = pd.to_datetime(self.customer_data['purchase_date']).dt.month
        seasonal_patterns = self.customer_data.groupby(['customer_id', 'month'])['amount'].sum()
        
        patterns = {
            'frequency_stats': purchase_frequency.describe(),
            'value_stats': purchase_value.describe(),
            'seasonal_patterns': seasonal_patterns,
            'avg_order_value': purchase_value.mean(),
            'purchase_frequency_avg': purchase_frequency.mean()
        }
        
        return patterns
    
    def segment_customers(self, method='kmeans', n_clusters=5):
        """Segmentar clientes basado en comportamiento"""
        if self.customer_data is None:
            return None
        
        # Preparar datos para segmentación
        features = self.customer_data.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count'],
            'purchase_date': 'count'
        }).fillna(0)
        
        features.columns = ['total_spent', 'avg_order_value', 'total_orders', 'purchase_frequency']
        
        # Normalizar datos
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        if method == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42)
            segments = model.fit_predict(features_scaled)
        elif method == 'dbscan':
            model = DBSCAN(eps=0.5, min_samples=5)
            segments = model.fit_predict(features_scaled)
        
        features['segment'] = segments
        
        # Analizar segmentos
        segment_analysis = features.groupby('segment').agg({
            'total_spent': 'mean',
            'avg_order_value': 'mean',
            'total_orders': 'mean',
            'purchase_frequency': 'mean'
        })
        
        self.segments = {
            'model': model,
            'features': features,
            'analysis': segment_analysis,
            'scaler': scaler
        }
        
        return segment_analysis
    
    def detect_anomalies(self):
        """Detectar comportamientos anómalos"""
        if self.customer_data is None:
            return None
        
        # Preparar datos para detección de anomalías
        features = self.customer_data.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'std'],
            'purchase_date': 'count'
        }).fillna(0)
        
        features.columns = ['total_spent', 'avg_order_value', 'spending_std', 'total_orders']
        
        # Detectar anomalías
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(features)
        
        anomalies = features[anomaly_labels == -1]
        
        self.anomalies = anomalies
        
        return {
            'anomaly_count': len(anomalies),
            'anomaly_percentage': len(anomalies) / len(features) * 100,
            'anomalies': anomalies
        }
    
    def analyze_customer_journey(self):
        """Analizar el journey del cliente"""
        if self.customer_data is None:
            return None
        
        # Mapear touchpoints
        touchpoints = self.customer_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'timestamp': lambda x: list(x),
            'conversion': 'sum'
        })
        
        # Analizar conversión por touchpoint
        conversion_by_touchpoint = self.customer_data.groupby('touchpoint')['conversion'].mean()
        
        # Analizar tiempo entre touchpoints
        journey_times = []
        for customer_id, data in touchpoints.iterrows():
            if len(data['timestamp']) > 1:
                times = sorted(data['timestamp'])
                journey_time = (max(times) - min(times)).days
                journey_times.append(journey_time)
        
        journey_analysis = {
            'avg_journey_time': np.mean(journey_times) if journey_times else 0,
            'conversion_by_touchpoint': conversion_by_touchpoint,
            'touchpoint_frequency': self.customer_data['touchpoint'].value_counts(),
            'conversion_rate': self.customer_data['conversion'].mean()
        }
        
        return journey_analysis
    
    def predict_churn(self):
        """Predecir probabilidad de churn"""
        if self.customer_data is None:
            return None
        
        # Calcular métricas de comportamiento
        behavior_metrics = self.customer_data.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count'],
            'purchase_date': ['min', 'max', 'count'],
            'satisfaction_score': 'mean'
        }).fillna(0)
        
        behavior_metrics.columns = [
            'total_spent', 'avg_order_value', 'total_orders',
            'first_purchase', 'last_purchase', 'purchase_frequency',
            'avg_satisfaction'
        ]
        
        # Calcular días desde última compra
        behavior_metrics['days_since_last_purchase'] = (
            datetime.now() - pd.to_datetime(behavior_metrics['last_purchase'])
        ).dt.days
        
        # Calcular score de churn (simplificado)
        behavior_metrics['churn_score'] = (
            behavior_metrics['days_since_last_purchase'] * 0.4 +
            (5 - behavior_metrics['avg_satisfaction']) * 0.3 +
            (behavior_metrics['purchase_frequency'] < 2) * 0.3
        )
        
        # Clasificar riesgo de churn
        behavior_metrics['churn_risk'] = pd.cut(
            behavior_metrics['churn_score'],
            bins=[0, 2, 4, 6, 10],
            labels=['Bajo', 'Medio', 'Alto', 'Crítico']
        )
        
        return behavior_metrics
    
    def generate_insights(self):
        """Generar insights de comportamiento"""
        insights = {}
        
        # Insights de segmentación
        if self.segments:
            insights['segmentation'] = {
                'total_segments': len(self.segments['analysis']),
                'largest_segment': self.segments['analysis']['total_spent'].idxmax(),
                'highest_value_segment': self.segments['analysis']['avg_order_value'].idxmax()
            }
        
        # Insights de anomalías
        if len(self.anomalies) > 0:
            insights['anomalies'] = {
                'count': len(self.anomalies),
                'percentage': len(self.anomalies) / len(self.customer_data) * 100,
                'avg_anomaly_value': self.anomalies['total_spent'].mean()
            }
        
        # Insights de patrones de compra
        patterns = self.analyze_purchase_patterns()
        if patterns:
            insights['purchase_patterns'] = {
                'avg_order_value': patterns['avg_order_value'],
                'purchase_frequency': patterns['purchase_frequency_avg'],
                'seasonal_variation': patterns['seasonal_patterns'].std()
            }
        
        self.insights = insights
        return insights
    
    def create_behavior_dashboard(self):
        """Crear dashboard de comportamiento"""
        if self.customer_data is None:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Segmentación de Clientes', 'Patrones de Compra',
                          'Análisis de Churn', 'Touchpoints del Journey'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Gráfico de segmentación
        if self.segments:
            segment_data = self.segments['analysis']
            fig.add_trace(
                go.Scatter(
                    x=segment_data['total_spent'],
                    y=segment_data['avg_order_value'],
                    mode='markers+text',
                    text=segment_data.index,
                    textposition="top center",
                    name='Segmentos'
                ),
                row=1, col=1
            )
        
        # Gráfico de patrones de compra
        patterns = self.analyze_purchase_patterns()
        if patterns:
            monthly_data = patterns['seasonal_patterns'].groupby('month').mean()
            fig.add_trace(
                go.Bar(x=monthly_data.index, y=monthly_data.values, name='Compras Mensuales'),
                row=1, col=2
            )
        
        # Gráfico de churn
        churn_data = self.predict_churn()
        if churn_data is not None:
            churn_counts = churn_data['churn_risk'].value_counts()
            fig.add_trace(
                go.Bar(x=churn_counts.index, y=churn_counts.values, name='Riesgo de Churn'),
                row=2, col=1
            )
        
        # Gráfico de touchpoints
        journey_data = self.analyze_customer_journey()
        if journey_data:
            touchpoint_data = journey_data['touchpoint_frequency']
            fig.add_trace(
                go.Pie(labels=touchpoint_data.index, values=touchpoint_data.values, name='Touchpoints'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Análisis de Comportamiento del Cliente",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_analysis(self, filename='customer_behavior_analysis.json'):
        """Exportar análisis completo"""
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'insights': self.insights,
            'segments': self.segments['analysis'].to_dict() if self.segments else {},
            'anomalies': self.anomalies.to_dict() if len(self.anomalies) > 0 else {},
            'summary': {
                'total_customers': len(self.customer_data['customer_id'].unique()) if self.customer_data is not None else 0,
                'total_transactions': len(self.customer_data) if self.customer_data is not None else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        print(f"✅ Análisis exportado a {filename}")
        return analysis_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador
    analyzer = CustomerBehaviorAnalyzer()
    
    # Datos de ejemplo
    sample_data = {
        'customer_id': np.random.randint(1, 100, 1000),
        'purchase_date': pd.date_range('2023-01-01', periods=1000, freq='D'),
        'amount': np.random.normal(100, 30, 1000),
        'touchpoint': np.random.choice(['email', 'social', 'website', 'mobile'], 1000),
        'conversion': np.random.choice([0, 1], 1000, p=[0.7, 0.3]),
        'satisfaction_score': np.random.uniform(1, 5, 1000)
    }
    
    # Cargar datos
    analyzer.load_customer_data(sample_data)
    
    # Realizar análisis
    print("🔍 Analizando patrones de compra...")
    patterns = analyzer.analyze_purchase_patterns()
    
    print("👥 Segmentando clientes...")
    segments = analyzer.segment_customers()
    
    print("🚨 Detectando anomalías...")
    anomalies = analyzer.detect_anomalies()
    
    print("🛤️ Analizando customer journey...")
    journey = analyzer.analyze_customer_journey()
    
    print("📊 Prediciendo churn...")
    churn = analyzer.predict_churn()
    
    print("💡 Generando insights...")
    insights = analyzer.generate_insights()
    
    print("📈 Creando dashboard...")
    dashboard = analyzer.create_behavior_dashboard()
    
    print("💾 Exportando análisis...")
    analysis = analyzer.export_analysis()
    
    print("✅ Análisis de comportamiento completado!")




