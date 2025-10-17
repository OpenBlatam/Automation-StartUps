"""
Marketing Brain Customer Journey Analyzer
Sistema avanzado de análisis de customer journey
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
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

class CustomerJourneyAnalyzer:
    def __init__(self):
        self.journey_data = {}
        self.touchpoint_analysis = {}
        self.journey_segments = {}
        self.conversion_funnels = {}
        self.journey_models = {}
        self.journey_insights = {}
        self.optimization_recommendations = {}
        
    def load_journey_data(self, journey_data):
        """Cargar datos de customer journey"""
        if isinstance(journey_data, str):
            if journey_data.endswith('.csv'):
                self.journey_data = pd.read_csv(journey_data)
            elif journey_data.endswith('.json'):
                with open(journey_data, 'r') as f:
                    data = json.load(f)
                self.journey_data = pd.DataFrame(data)
        else:
            self.journey_data = pd.DataFrame(journey_data)
        
        print(f"✅ Datos de customer journey cargados: {len(self.journey_data)} registros")
        return True
    
    def analyze_touchpoints(self):
        """Analizar touchpoints del customer journey"""
        if self.journey_data.empty:
            return None
        
        # Análisis de touchpoints por frecuencia
        touchpoint_frequency = self.journey_data['touchpoint'].value_counts()
        
        # Análisis de touchpoints por orden
        touchpoint_order_analysis = self._analyze_touchpoint_order()
        
        # Análisis de touchpoints por canal
        touchpoint_channel_analysis = self._analyze_touchpoint_channels()
        
        # Análisis de touchpoints por tiempo
        touchpoint_timing_analysis = self._analyze_touchpoint_timing()
        
        # Análisis de efectividad de touchpoints
        touchpoint_effectiveness = self._analyze_touchpoint_effectiveness()
        
        touchpoint_results = {
            'touchpoint_frequency': touchpoint_frequency.to_dict(),
            'touchpoint_order_analysis': touchpoint_order_analysis,
            'touchpoint_channel_analysis': touchpoint_channel_analysis,
            'touchpoint_timing_analysis': touchpoint_timing_analysis,
            'touchpoint_effectiveness': touchpoint_effectiveness,
            'total_touchpoints': len(touchpoint_frequency),
            'unique_touchpoints': len(touchpoint_frequency)
        }
        
        self.touchpoint_analysis = touchpoint_results
        return touchpoint_results
    
    def _analyze_touchpoint_order(self):
        """Analizar orden de touchpoints"""
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.journey_data.groupby('customer_id')['touchpoint'].apply(list)
        
        # Análisis de patrones de secuencia
        sequence_patterns = {}
        for customer_id, sequence in customer_sequences.items():
            if len(sequence) > 1:
                # Analizar transiciones
                for i in range(len(sequence) - 1):
                    transition = f"{sequence[i]} -> {sequence[i+1]}"
                    if transition not in sequence_patterns:
                        sequence_patterns[transition] = 0
                    sequence_patterns[transition] += 1
        
        # Identificar patrones más comunes
        common_patterns = sorted(sequence_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'sequence_patterns': sequence_patterns,
            'common_patterns': common_patterns,
            'avg_sequence_length': customer_sequences.apply(len).mean()
        }
    
    def _analyze_touchpoint_channels(self):
        """Analizar touchpoints por canal"""
        if 'channel' not in self.journey_data.columns:
            return {}
        
        # Análisis de touchpoints por canal
        channel_analysis = self.journey_data.groupby('channel').agg({
            'touchpoint': 'count',
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        channel_analysis['conversion_rate'] = (channel_analysis['conversion'] / channel_analysis['touchpoint']) * 100
        channel_analysis['avg_revenue'] = channel_analysis['revenue'] / channel_analysis['touchpoint']
        
        # Análisis de canales más efectivos
        most_effective_channels = channel_analysis.nlargest(5, 'conversion_rate')
        
        return {
            'channel_analysis': channel_analysis.to_dict('records'),
            'most_effective_channels': most_effective_channels.to_dict('records'),
            'channel_diversity': len(channel_analysis)
        }
    
    def _analyze_touchpoint_timing(self):
        """Analizar timing de touchpoints"""
        if 'timestamp' not in self.journey_data.columns:
            return {}
        
        # Convertir timestamp a datetime
        self.journey_data['timestamp'] = pd.to_datetime(self.journey_data['timestamp'])
        
        # Análisis de timing por hora del día
        self.journey_data['hour'] = self.journey_data['timestamp'].dt.hour
        hourly_analysis = self.journey_data.groupby('hour').agg({
            'touchpoint': 'count',
            'conversion': 'sum'
        }).reset_index()
        
        # Análisis de timing por día de la semana
        self.journey_data['day_of_week'] = self.journey_data['timestamp'].dt.day_name()
        daily_analysis = self.journey_data.groupby('day_of_week').agg({
            'touchpoint': 'count',
            'conversion': 'sum'
        }).reset_index()
        
        # Análisis de tiempo entre touchpoints
        time_between_touchpoints = self._analyze_time_between_touchpoints()
        
        return {
            'hourly_analysis': hourly_analysis.to_dict('records'),
            'daily_analysis': daily_analysis.to_dict('records'),
            'time_between_touchpoints': time_between_touchpoints
        }
    
    def _analyze_time_between_touchpoints(self):
        """Analizar tiempo entre touchpoints"""
        time_analysis = {}
        
        for customer_id in self.journey_data['customer_id'].unique():
            customer_data = self.journey_data[self.journey_data['customer_id'] == customer_id].sort_values('timestamp')
            
            if len(customer_data) > 1:
                time_diffs = customer_data['timestamp'].diff().dt.total_seconds() / 3600  # en horas
                time_diffs = time_diffs.dropna()
                
                if len(time_diffs) > 0:
                    time_analysis[customer_id] = {
                        'avg_time_between_touchpoints': time_diffs.mean(),
                        'min_time_between_touchpoints': time_diffs.min(),
                        'max_time_between_touchpoints': time_diffs.max(),
                        'total_touchpoints': len(customer_data)
                    }
        
        # Análisis agregado
        if time_analysis:
            avg_times = [data['avg_time_between_touchpoints'] for data in time_analysis.values()]
            return {
                'overall_avg_time': np.mean(avg_times),
                'overall_min_time': np.min([data['min_time_between_touchpoints'] for data in time_analysis.values()]),
                'overall_max_time': np.max([data['max_time_between_touchpoints'] for data in time_analysis.values()]),
                'customers_analyzed': len(time_analysis)
            }
        
        return {}
    
    def _analyze_touchpoint_effectiveness(self):
        """Analizar efectividad de touchpoints"""
        effectiveness_analysis = {}
        
        for touchpoint in self.journey_data['touchpoint'].unique():
            touchpoint_data = self.journey_data[self.journey_data['touchpoint'] == touchpoint]
            
            # Calcular métricas de efectividad
            total_touchpoints = len(touchpoint_data)
            conversions = touchpoint_data['conversion'].sum() if 'conversion' in touchpoint_data.columns else 0
            revenue = touchpoint_data['revenue'].sum() if 'revenue' in touchpoint_data.columns else 0
            
            conversion_rate = (conversions / total_touchpoints) * 100 if total_touchpoints > 0 else 0
            avg_revenue = revenue / total_touchpoints if total_touchpoints > 0 else 0
            
            # Score de efectividad (combinación de conversión y revenue)
            effectiveness_score = (conversion_rate * 0.6) + (avg_revenue * 0.4)
            
            effectiveness_analysis[touchpoint] = {
                'total_touchpoints': total_touchpoints,
                'conversions': conversions,
                'revenue': revenue,
                'conversion_rate': conversion_rate,
                'avg_revenue': avg_revenue,
                'effectiveness_score': effectiveness_score
            }
        
        # Ordenar por efectividad
        sorted_effectiveness = sorted(effectiveness_analysis.items(), key=lambda x: x[1]['effectiveness_score'], reverse=True)
        
        return {
            'effectiveness_analysis': effectiveness_analysis,
            'top_effective_touchpoints': sorted_effectiveness[:5],
            'bottom_effective_touchpoints': sorted_effectiveness[-5:]
        }
    
    def create_journey_segments(self):
        """Crear segmentos de customer journey"""
        if self.journey_data.empty:
            return None
        
        # Preparar datos para segmentación
        customer_metrics = self.journey_data.groupby('customer_id').agg({
            'touchpoint': 'count',
            'conversion': 'sum',
            'revenue': 'sum',
            'timestamp': ['min', 'max']
        }).reset_index()
        
        # Aplanar columnas
        customer_metrics.columns = ['customer_id', 'touchpoint_count', 'conversions', 'revenue', 'first_touchpoint', 'last_touchpoint']
        
        # Calcular duración del journey
        customer_metrics['journey_duration'] = (customer_metrics['last_touchpoint'] - customer_metrics['first_touchpoint']).dt.days
        
        # Calcular métricas adicionales
        customer_metrics['conversion_rate'] = (customer_metrics['conversions'] / customer_metrics['touchpoint_count']) * 100
        customer_metrics['avg_revenue_per_touchpoint'] = customer_metrics['revenue'] / customer_metrics['touchpoint_count']
        
        # Segmentación usando clustering
        features = ['touchpoint_count', 'conversions', 'revenue', 'journey_duration', 'conversion_rate']
        X = customer_metrics[features].fillna(0)
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Clustering K-means
        kmeans = KMeans(n_clusters=4, random_state=42)
        customer_metrics['journey_segment'] = kmeans.fit_predict(X_scaled)
        
        # Nombrar segmentos
        segment_names = {
            0: 'Quick Converters',
            1: 'Long Journey',
            2: 'High Value',
            3: 'Low Engagement'
        }
        
        customer_metrics['journey_segment_name'] = customer_metrics['journey_segment'].map(segment_names)
        
        # Análisis de segmentos
        segment_analysis = customer_metrics.groupby('journey_segment_name').agg({
            'touchpoint_count': 'mean',
            'conversions': 'mean',
            'revenue': 'mean',
            'journey_duration': 'mean',
            'conversion_rate': 'mean',
            'customer_id': 'count'
        }).round(2)
        
        segment_analysis.columns = [
            'avg_touchpoints', 'avg_conversions', 'avg_revenue',
            'avg_duration', 'avg_conversion_rate', 'customer_count'
        ]
        
        journey_segments = {
            'customer_segments': customer_metrics.to_dict('records'),
            'segment_analysis': segment_analysis.to_dict('index'),
            'segment_characteristics': self._analyze_segment_characteristics(customer_metrics)
        }
        
        self.journey_segments = journey_segments
        return journey_segments
    
    def _analyze_segment_characteristics(self, customer_metrics):
        """Analizar características de segmentos"""
        characteristics = {}
        
        for segment in customer_metrics['journey_segment_name'].unique():
            segment_data = customer_metrics[customer_metrics['journey_segment_name'] == segment]
            
            characteristics[segment] = {
                'avg_touchpoints': segment_data['touchpoint_count'].mean(),
                'avg_conversions': segment_data['conversions'].mean(),
                'avg_revenue': segment_data['revenue'].mean(),
                'avg_duration': segment_data['journey_duration'].mean(),
                'avg_conversion_rate': segment_data['conversion_rate'].mean(),
                'customer_count': len(segment_data),
                'percentage': len(segment_data) / len(customer_metrics) * 100
            }
        
        return characteristics
    
    def analyze_conversion_funnels(self):
        """Analizar funnels de conversión"""
        if self.journey_data.empty:
            return None
        
        # Crear funnels por segmento
        funnel_analysis = {}
        
        for segment in self.journey_data['journey_segment_name'].unique() if 'journey_segment_name' in self.journey_data.columns else ['All']:
            if segment == 'All':
                segment_data = self.journey_data
            else:
                segment_data = self.journey_data[self.journey_data['journey_segment_name'] == segment]
            
            # Análisis de funnel
            funnel_data = self._create_conversion_funnel(segment_data)
            funnel_analysis[segment] = funnel_data
        
        # Análisis de funnel general
        general_funnel = self._create_conversion_funnel(self.journey_data)
        
        # Análisis de drop-off points
        drop_off_analysis = self._analyze_drop_off_points()
        
        conversion_funnels = {
            'segment_funnels': funnel_analysis,
            'general_funnel': general_funnel,
            'drop_off_analysis': drop_off_analysis
        }
        
        self.conversion_funnels = conversion_funnels
        return conversion_funnels
    
    def _create_conversion_funnel(self, data):
        """Crear funnel de conversión"""
        # Ordenar por timestamp
        data_sorted = data.sort_values('timestamp')
        
        # Crear secuencias de touchpoints
        customer_sequences = data_sorted.groupby('customer_id')['touchpoint'].apply(list)
        
        # Análisis de funnel
        funnel_steps = {}
        total_customers = len(customer_sequences)
        
        for step in range(1, 6):  # Analizar hasta 5 pasos
            customers_at_step = 0
            for sequence in customer_sequences:
                if len(sequence) >= step:
                    customers_at_step += 1
            
            conversion_rate = (customers_at_step / total_customers) * 100 if total_customers > 0 else 0
            funnel_steps[f'step_{step}'] = {
                'customers': customers_at_step,
                'conversion_rate': conversion_rate
            }
        
        return {
            'funnel_steps': funnel_steps,
            'total_customers': total_customers,
            'avg_sequence_length': customer_sequences.apply(len).mean()
        }
    
    def _analyze_drop_off_points(self):
        """Analizar puntos de abandono"""
        drop_off_analysis = {}
        
        # Crear secuencias de touchpoints
        customer_sequences = self.journey_data.groupby('customer_id')['touchpoint'].apply(list)
        
        # Analizar abandono por posición
        for position in range(1, 6):
            abandoned_at_position = 0
            total_at_position = 0
            
            for sequence in customer_sequences:
                if len(sequence) >= position:
                    total_at_position += 1
                    if len(sequence) == position:
                        abandoned_at_position += 1
            
            drop_off_rate = (abandoned_at_position / total_at_position) * 100 if total_at_position > 0 else 0
            
            drop_off_analysis[f'position_{position}'] = {
                'abandoned_customers': abandoned_at_position,
                'total_customers': total_at_position,
                'drop_off_rate': drop_off_rate
            }
        
        return drop_off_analysis
    
    def build_journey_prediction_model(self, target_variable='conversion'):
        """Construir modelo de predicción de journey"""
        if target_variable not in self.journey_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.journey_data.columns if col != target_variable and col != 'customer_id' and col != 'timestamp']
        X = self.journey_data[feature_columns]
        y = self.journey_data[target_variable]
        
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
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluar modelo
        y_pred = model.predict(X_test_scaled)
        
        model_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.journey_models['journey_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def predict_journey_outcome(self, customer_data):
        """Predecir resultado del journey"""
        if 'journey_predictor' not in self.journey_models:
            raise ValueError("Modelo de predicción de journey no encontrado")
        
        model_info = self.journey_models['journey_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Preparar datos
        X = customer_data[feature_columns]
        
        # Codificar variables categóricas
        for column in X.select_dtypes(include=['object']).columns:
            if column in label_encoders:
                le = label_encoders[column]
                X[column] = le.transform(X[column].astype(str))
        
        # Escalar datos
        X_scaled = scaler.transform(X)
        
        # Predecir resultado
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)
        
        return {
            'predictions': predictions,
            'probabilities': probabilities,
            'prediction_confidence': np.max(probabilities, axis=1)
        }
    
    def generate_journey_insights(self):
        """Generar insights de customer journey"""
        insights = []
        
        # Insights de touchpoints
        if self.touchpoint_analysis:
            touchpoint_effectiveness = self.touchpoint_analysis.get('touchpoint_effectiveness', {})
            top_touchpoints = touchpoint_effectiveness.get('top_effective_touchpoints', [])
            
            if top_touchpoints:
                insights.append({
                    'category': 'Touchpoint Effectiveness',
                    'insight': f'Top touchpoint efectivo: {top_touchpoints[0][0]}',
                    'recommendation': 'Aumentar inversión en touchpoints más efectivos',
                    'priority': 'high'
                })
        
        # Insights de segmentos
        if self.journey_segments:
            segment_analysis = self.journey_segments.get('segment_analysis', {})
            
            # Analizar segmento de bajo engagement
            low_engagement = segment_analysis.get('Low Engagement', {})
            if low_engagement:
                customer_count = low_engagement.get('customer_count', 0)
                if customer_count > 0:
                    insights.append({
                        'category': 'Journey Segmentation',
                        'insight': f'{customer_count} clientes en segmento de bajo engagement',
                        'recommendation': 'Implementar estrategias de re-engagement',
                        'priority': 'high'
                    })
        
        # Insights de funnels
        if self.conversion_funnels:
            general_funnel = self.conversion_funnels.get('general_funnel', {})
            funnel_steps = general_funnel.get('funnel_steps', {})
            
            if funnel_steps:
                step_1 = funnel_steps.get('step_1', {})
                step_2 = funnel_steps.get('step_2', {})
                
                if step_1 and step_2:
                    drop_off = step_1.get('conversion_rate', 0) - step_2.get('conversion_rate', 0)
                    if drop_off > 20:
                        insights.append({
                            'category': 'Conversion Funnel',
                            'insight': f'Drop-off del {drop_off:.1f}% en el primer paso',
                            'recommendation': 'Optimizar primer touchpoint para reducir abandono',
                            'priority': 'high'
                        })
        
        # Insights de timing
        if self.touchpoint_analysis:
            timing_analysis = self.touchpoint_analysis.get('touchpoint_timing_analysis', {})
            time_between = timing_analysis.get('time_between_touchpoints', {})
            
            if time_between:
                avg_time = time_between.get('overall_avg_time', 0)
                if avg_time > 24:  # Más de 24 horas
                    insights.append({
                        'category': 'Journey Timing',
                        'insight': f'Tiempo promedio entre touchpoints: {avg_time:.1f} horas',
                        'recommendation': 'Implementar follow-up más frecuente',
                        'priority': 'medium'
                    })
        
        self.journey_insights = insights
        return insights
    
    def create_journey_dashboard(self):
        """Crear dashboard de customer journey"""
        if not self.journey_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Touchpoint Effectiveness', 'Journey Segments',
                          'Conversion Funnel', 'Touchpoint Timing'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de efectividad de touchpoints
        if self.touchpoint_analysis:
            touchpoint_effectiveness = self.touchpoint_analysis.get('touchpoint_effectiveness', {})
            effectiveness_analysis = touchpoint_effectiveness.get('effectiveness_analysis', {})
            
            if effectiveness_analysis:
                touchpoints = list(effectiveness_analysis.keys())
                scores = [data['effectiveness_score'] for data in effectiveness_analysis.values()]
                
                fig.add_trace(
                    go.Bar(x=touchpoints, y=scores, name='Touchpoint Effectiveness'),
                    row=1, col=1
                )
        
        # Gráfico de segmentos de journey
        if self.journey_segments:
            segment_analysis = self.journey_segments.get('segment_analysis', {})
            if segment_analysis:
                segments = list(segment_analysis.keys())
                customer_counts = [segment_analysis[segment]['customer_count'] for segment in segments]
                
                fig.add_trace(
                    go.Pie(labels=segments, values=customer_counts, name='Journey Segments'),
                    row=1, col=2
                )
        
        # Gráfico de funnel de conversión
        if self.conversion_funnels:
            general_funnel = self.conversion_funnels.get('general_funnel', {})
            funnel_steps = general_funnel.get('funnel_steps', {})
            
            if funnel_steps:
                steps = list(funnel_steps.keys())
                conversion_rates = [funnel_steps[step]['conversion_rate'] for step in steps]
                
                fig.add_trace(
                    go.Bar(x=steps, y=conversion_rates, name='Conversion Funnel'),
                    row=2, col=1
                )
        
        # Gráfico de timing de touchpoints
        if self.touchpoint_analysis:
            timing_analysis = self.touchpoint_analysis.get('touchpoint_timing_analysis', {})
            hourly_analysis = timing_analysis.get('hourly_analysis', [])
            
            if hourly_analysis:
                hours = [data['hour'] for data in hourly_analysis]
                touchpoint_counts = [data['touchpoint'] for data in hourly_analysis]
                
                fig.add_trace(
                    go.Bar(x=hours, y=touchpoint_counts, name='Touchpoint Timing'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de Customer Journey",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_journey_analysis(self, filename='customer_journey_analysis.json'):
        """Exportar análisis de customer journey"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'touchpoint_analysis': self.touchpoint_analysis,
            'journey_segments': self.journey_segments,
            'conversion_funnels': self.conversion_funnels,
            'journey_models': {k: {'metrics': v['metrics']} for k, v in self.journey_models.items()},
            'journey_insights': self.journey_insights,
            'summary': {
                'total_touchpoints': len(self.journey_data['touchpoint'].unique()) if 'touchpoint' in self.journey_data.columns else 0,
                'total_customers': len(self.journey_data['customer_id'].unique()) if 'customer_id' in self.journey_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de customer journey exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de customer journey
    journey_analyzer = CustomerJourneyAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 500, 2000),
        'touchpoint': np.random.choice(['Website Visit', 'Email Open', 'Social Media', 'Ad Click', 'Product View', 'Add to Cart', 'Purchase'], 2000),
        'channel': np.random.choice(['Digital', 'Email', 'Social', 'Paid Ads', 'Organic'], 2000),
        'conversion': np.random.choice([0, 1], 2000, p=[0.8, 0.2]),
        'revenue': np.random.normal(100, 50, 2000),
        'timestamp': pd.date_range('2023-01-01', periods=2000, freq='H')
    })
    
    # Cargar datos de customer journey
    print("📊 Cargando datos de customer journey...")
    journey_analyzer.load_journey_data(sample_data)
    
    # Analizar touchpoints
    print("🎯 Analizando touchpoints...")
    touchpoint_analysis = journey_analyzer.analyze_touchpoints()
    
    # Crear segmentos de journey
    print("👥 Creando segmentos de journey...")
    journey_segments = journey_analyzer.create_journey_segments()
    
    # Analizar funnels de conversión
    print("🔄 Analizando funnels de conversión...")
    conversion_funnels = journey_analyzer.analyze_conversion_funnels()
    
    # Construir modelo de predicción de journey
    print("🔮 Construyendo modelo de predicción de journey...")
    journey_model = journey_analyzer.build_journey_prediction_model()
    
    # Generar insights de journey
    print("💡 Generando insights de journey...")
    journey_insights = journey_analyzer.generate_journey_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de customer journey...")
    dashboard = journey_analyzer.create_journey_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de customer journey...")
    export_data = journey_analyzer.export_journey_analysis()
    
    print("✅ Sistema de análisis de customer journey completado!")






