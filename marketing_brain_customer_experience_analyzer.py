"""
Marketing Brain Customer Experience Analyzer
Sistema avanzado de análisis de experiencia del cliente (CX)
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

class CustomerExperienceAnalyzer:
    def __init__(self):
        self.cx_data = {}
        self.touchpoint_analysis = {}
        self.journey_mapping = {}
        self.satisfaction_models = {}
        self.nps_analysis = {}
        self.customer_effort_score = {}
        self.cx_insights = {}
        
    def load_cx_data(self, cx_data):
        """Cargar datos de experiencia del cliente"""
        if isinstance(cx_data, str):
            if cx_data.endswith('.csv'):
                self.cx_data = pd.read_csv(cx_data)
            elif cx_data.endswith('.json'):
                with open(cx_data, 'r') as f:
                    data = json.load(f)
                self.cx_data = pd.DataFrame(data)
        else:
            self.cx_data = pd.DataFrame(cx_data)
        
        print(f"✅ Datos de CX cargados: {len(self.cx_data)} registros")
        return True
    
    def analyze_customer_journey(self, customer_id=None):
        """Analizar journey del cliente"""
        if customer_id:
            journey_data = self.cx_data[self.cx_data['customer_id'] == customer_id]
        else:
            journey_data = self.cx_data
        
        # Mapear touchpoints
        touchpoints = journey_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'timestamp': lambda x: list(x),
            'interaction_type': lambda x: list(x),
            'satisfaction_score': lambda x: list(x),
            'effort_score': lambda x: list(x)
        })
        
        # Análisis de journey
        journey_analysis = {}
        
        for customer_id, data in touchpoints.iterrows():
            # Calcular duración del journey
            if len(data['timestamp']) > 1:
                timestamps = sorted(data['timestamp'])
                journey_duration = (max(timestamps) - min(timestamps)).days
            else:
                journey_duration = 0
            
            # Calcular satisfacción promedio
            avg_satisfaction = np.mean(data['satisfaction_score']) if data['satisfaction_score'] else 0
            
            # Calcular esfuerzo promedio
            avg_effort = np.mean(data['effort_score']) if data['effort_score'] else 0
            
            # Identificar touchpoints críticos
            critical_touchpoints = []
            for i, (touchpoint, satisfaction, effort) in enumerate(zip(data['touchpoint'], data['satisfaction_score'], data['effort_score'])):
                if satisfaction < 3 or effort > 7:  # Umbrales de satisfacción y esfuerzo
                    critical_touchpoints.append({
                        'touchpoint': touchpoint,
                        'position': i,
                        'satisfaction': satisfaction,
                        'effort': effort,
                        'criticality': 'high' if satisfaction < 2 or effort > 8 else 'medium'
                    })
            
            # Calcular score de journey
            journey_score = self._calculate_journey_score(avg_satisfaction, avg_effort, journey_duration, len(data['touchpoint']))
            
            journey_analysis[customer_id] = {
                'journey_duration': journey_duration,
                'touchpoint_count': len(data['touchpoint']),
                'avg_satisfaction': avg_satisfaction,
                'avg_effort': avg_effort,
                'critical_touchpoints': critical_touchpoints,
                'journey_score': journey_score,
                'touchpoints': data['touchpoint'],
                'interaction_types': data['interaction_type']
            }
        
        self.journey_mapping = journey_analysis
        return journey_analysis
    
    def _calculate_journey_score(self, satisfaction, effort, duration, touchpoint_count):
        """Calcular score del journey"""
        # Normalizar métricas
        satisfaction_norm = satisfaction / 5.0  # Escala 1-5
        effort_norm = 1 - (effort / 10.0)  # Invertir escala 1-10
        duration_norm = 1 - min(duration / 365.0, 1.0)  # Normalizar duración
        touchpoint_norm = min(touchpoint_count / 10.0, 1.0)  # Normalizar touchpoints
        
        # Score ponderado
        journey_score = (
            satisfaction_norm * 0.4 +
            effort_norm * 0.3 +
            duration_norm * 0.2 +
            touchpoint_norm * 0.1
        ) * 100
        
        return round(journey_score, 2)
    
    def analyze_touchpoint_performance(self):
        """Analizar performance de touchpoints"""
        if self.cx_data.empty:
            return None
        
        # Análisis por touchpoint
        touchpoint_analysis = self.cx_data.groupby('touchpoint').agg({
            'satisfaction_score': ['mean', 'std', 'count'],
            'effort_score': ['mean', 'std'],
            'interaction_duration': 'mean' if 'interaction_duration' in self.cx_data.columns else lambda x: 0,
            'resolution_rate': 'mean' if 'resolution_rate' in self.cx_data.columns else lambda x: 0
        }).round(2)
        
        touchpoint_analysis.columns = [
            'avg_satisfaction', 'satisfaction_std', 'interaction_count',
            'avg_effort', 'effort_std', 'avg_duration', 'resolution_rate'
        ]
        
        # Identificar touchpoints problemáticos
        problematic_touchpoints = touchpoint_analysis[
            (touchpoint_analysis['avg_satisfaction'] < 3.0) |
            (touchpoint_analysis['avg_effort'] > 7.0) |
            (touchpoint_analysis['resolution_rate'] < 0.7)
        ]
        
        # Análisis de correlación entre touchpoints
        touchpoint_correlations = self._analyze_touchpoint_correlations()
        
        # Análisis de secuencias de touchpoints
        touchpoint_sequences = self._analyze_touchpoint_sequences()
        
        analysis_results = {
            'touchpoint_performance': touchpoint_analysis.to_dict('index'),
            'problematic_touchpoints': problematic_touchpoints.to_dict('index'),
            'touchpoint_correlations': touchpoint_correlations,
            'touchpoint_sequences': touchpoint_sequences,
            'total_touchpoints': len(touchpoint_analysis),
            'problematic_count': len(problematic_touchpoints)
        }
        
        self.touchpoint_analysis = analysis_results
        return analysis_results
    
    def _analyze_touchpoint_correlations(self):
        """Analizar correlaciones entre touchpoints"""
        # Crear matriz de touchpoints por cliente
        touchpoint_matrix = self.cx_data.pivot_table(
            index='customer_id',
            columns='touchpoint',
            values='satisfaction_score',
            aggfunc='mean',
            fill_value=0
        )
        
        # Calcular correlaciones
        correlations = touchpoint_matrix.corr()
        
        # Encontrar correlaciones fuertes
        strong_correlations = []
        for i in range(len(correlations.columns)):
            for j in range(i+1, len(correlations.columns)):
                corr_value = correlations.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'touchpoint1': correlations.columns[i],
                        'touchpoint2': correlations.columns[j],
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': correlations.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def _analyze_touchpoint_sequences(self):
        """Analizar secuencias de touchpoints"""
        sequences = {}
        
        for customer_id, data in self.cx_data.groupby('customer_id'):
            touchpoint_sequence = data.sort_values('timestamp')['touchpoint'].tolist()
            
            # Crear secuencias de 2 touchpoints
            for i in range(len(touchpoint_sequence) - 1):
                sequence = f"{touchpoint_sequence[i]} -> {touchpoint_sequence[i+1]}"
                sequences[sequence] = sequences.get(sequence, 0) + 1
        
        # Ordenar por frecuencia
        sorted_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_common_sequences': sorted_sequences[:10],
            'total_sequences': len(sequences)
        }
    
    def analyze_nps(self):
        """Analizar Net Promoter Score (NPS)"""
        if 'nps_score' not in self.cx_data.columns:
            return None
        
        nps_data = self.cx_data['nps_score'].dropna()
        
        # Clasificar promotores, pasivos y detractores
        promoters = len(nps_data[nps_data >= 9])
        passives = len(nps_data[(nps_data >= 7) & (nps_data <= 8)])
        detractors = len(nps_data[nps_data <= 6])
        total_responses = len(nps_data)
        
        # Calcular NPS
        nps_score = ((promoters - detractors) / total_responses) * 100 if total_responses > 0 else 0
        
        # Análisis por segmento
        segment_analysis = {}
        if 'customer_segment' in self.cx_data.columns:
            for segment in self.cx_data['customer_segment'].unique():
                segment_data = self.cx_data[self.cx_data['customer_segment'] == segment]['nps_score'].dropna()
                if len(segment_data) > 0:
                    seg_promoters = len(segment_data[segment_data >= 9])
                    seg_detractors = len(segment_data[segment_data <= 6])
                    seg_nps = ((seg_promoters - seg_detractors) / len(segment_data)) * 100
                    
                    segment_analysis[segment] = {
                        'nps_score': seg_nps,
                        'promoters': seg_promoters,
                        'passives': len(segment_data[(segment_data >= 7) & (segment_data <= 8)]),
                        'detractors': seg_detractors,
                        'total_responses': len(segment_data)
                    }
        
        # Análisis temporal
        temporal_analysis = {}
        if 'timestamp' in self.cx_data.columns:
            self.cx_data['month'] = pd.to_datetime(self.cx_data['timestamp']).dt.to_period('M')
            monthly_nps = self.cx_data.groupby('month')['nps_score'].apply(
                lambda x: ((len(x[x >= 9]) - len(x[x <= 6])) / len(x)) * 100 if len(x) > 0 else 0
            )
            temporal_analysis['monthly_nps'] = monthly_nps.to_dict()
        
        nps_analysis = {
            'overall_nps': nps_score,
            'promoters': promoters,
            'passives': passives,
            'detractors': detractors,
            'total_responses': total_responses,
            'segment_analysis': segment_analysis,
            'temporal_analysis': temporal_analysis,
            'nps_category': self._categorize_nps(nps_score)
        }
        
        self.nps_analysis = nps_analysis
        return nps_analysis
    
    def _categorize_nps(self, nps_score):
        """Categorizar NPS score"""
        if nps_score >= 70:
            return 'Excellent'
        elif nps_score >= 50:
            return 'Good'
        elif nps_score >= 0:
            return 'Average'
        else:
            return 'Poor'
    
    def analyze_customer_effort_score(self):
        """Analizar Customer Effort Score (CES)"""
        if 'effort_score' not in self.cx_data.columns:
            return None
        
        effort_data = self.cx_data['effort_score'].dropna()
        
        # Análisis de distribución
        effort_distribution = {
            'very_low': len(effort_data[effort_data <= 2]),
            'low': len(effort_data[(effort_data > 2) & (effort_data <= 4)]),
            'medium': len(effort_data[(effort_data > 4) & (effort_data <= 6)]),
            'high': len(effort_data[(effort_data > 6) & (effort_data <= 8)]),
            'very_high': len(effort_data[effort_data > 8])
        }
        
        # Score promedio
        avg_effort = effort_data.mean()
        
        # Análisis por touchpoint
        touchpoint_effort = self.cx_data.groupby('touchpoint')['effort_score'].agg(['mean', 'std', 'count']).round(2)
        
        # Identificar touchpoints de alto esfuerzo
        high_effort_touchpoints = touchpoint_effort[touchpoint_effort['mean'] > 7.0]
        
        # Análisis de correlación con satisfacción
        effort_satisfaction_corr = self.cx_data['effort_score'].corr(self.cx_data['satisfaction_score'])
        
        ces_analysis = {
            'avg_effort_score': avg_effort,
            'effort_distribution': effort_distribution,
            'touchpoint_effort': touchpoint_effort.to_dict('index'),
            'high_effort_touchpoints': high_effort_touchpoints.to_dict('index'),
            'effort_satisfaction_correlation': effort_satisfaction_corr,
            'effort_category': self._categorize_effort(avg_effort)
        }
        
        self.customer_effort_score = ces_analysis
        return ces_analysis
    
    def _categorize_effort(self, effort_score):
        """Categorizar effort score"""
        if effort_score <= 3:
            return 'Very Low Effort'
        elif effort_score <= 5:
            return 'Low Effort'
        elif effort_score <= 7:
            return 'Medium Effort'
        else:
            return 'High Effort'
    
    def build_satisfaction_prediction_model(self, target_variable='satisfaction_score'):
        """Construir modelo de predicción de satisfacción"""
        if target_variable not in self.cx_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.cx_data.columns if col != target_variable and col != 'customer_id']
        X = self.cx_data[feature_columns]
        y = self.cx_data[target_variable]
        
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
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.satisfaction_models['satisfaction_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_cx_insights(self):
        """Generar insights de experiencia del cliente"""
        insights = []
        
        # Insights de journey
        if self.journey_mapping:
            avg_journey_score = np.mean([journey['journey_score'] for journey in self.journey_mapping.values()])
            if avg_journey_score < 70:
                insights.append({
                    'category': 'Journey',
                    'insight': f'Journey score promedio bajo: {avg_journey_score:.1f}',
                    'recommendation': 'Optimizar touchpoints críticos y reducir fricción',
                    'priority': 'high'
                })
        
        # Insights de touchpoints
        if self.touchpoint_analysis:
            problematic_count = self.touchpoint_analysis.get('problematic_count', 0)
            total_touchpoints = self.touchpoint_analysis.get('total_touchpoints', 0)
            if problematic_count > 0:
                insights.append({
                    'category': 'Touchpoints',
                    'insight': f'{problematic_count} de {total_touchpoints} touchpoints problemáticos',
                    'recommendation': 'Revisar y mejorar touchpoints con baja satisfacción o alto esfuerzo',
                    'priority': 'high'
                })
        
        # Insights de NPS
        if self.nps_analysis:
            nps_score = self.nps_analysis.get('overall_nps', 0)
            if nps_score < 50:
                insights.append({
                    'category': 'NPS',
                    'insight': f'NPS score bajo: {nps_score:.1f}',
                    'recommendation': 'Implementar estrategias para convertir detractores en promotores',
                    'priority': 'high'
                })
        
        # Insights de esfuerzo
        if self.customer_effort_score:
            avg_effort = self.customer_effort_score.get('avg_effort_score', 0)
            if avg_effort > 6:
                insights.append({
                    'category': 'Effort',
                    'insight': f'Esfuerzo promedio alto: {avg_effort:.1f}',
                    'recommendation': 'Simplificar procesos y reducir fricción en touchpoints',
                    'priority': 'medium'
                })
        
        # Insights de correlaciones
        if self.touchpoint_analysis and 'touchpoint_correlations' in self.touchpoint_analysis:
            strong_correlations = self.touchpoint_analysis['touchpoint_correlations'].get('strong_correlations', [])
            if len(strong_correlations) > 0:
                insights.append({
                    'category': 'Correlations',
                    'insight': f'{len(strong_correlations)} correlaciones fuertes entre touchpoints',
                    'recommendation': 'Optimizar secuencias de touchpoints correlacionados',
                    'priority': 'medium'
                })
        
        self.cx_insights = insights
        return insights
    
    def create_cx_dashboard(self):
        """Crear dashboard de experiencia del cliente"""
        if not self.cx_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Journey Scores', 'NPS Analysis',
                          'Touchpoint Performance', 'Customer Effort Score'),
            specs=[[{"type": "histogram"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de journey scores
        if self.journey_mapping:
            journey_scores = [journey['journey_score'] for journey in self.journey_mapping.values()]
            fig.add_trace(
                go.Histogram(x=journey_scores, name='Journey Scores'),
                row=1, col=1
            )
        
        # Gráfico de NPS
        if self.nps_analysis:
            nps_data = self.nps_analysis
            promoters = nps_data.get('promoters', 0)
            passives = nps_data.get('passives', 0)
            detractors = nps_data.get('detractors', 0)
            
            fig.add_trace(
                go.Pie(
                    labels=['Promoters', 'Passives', 'Detractors'],
                    values=[promoters, passives, detractors],
                    name='NPS Distribution'
                ),
                row=1, col=2
            )
        
        # Gráfico de performance de touchpoints
        if self.touchpoint_analysis:
            touchpoint_perf = self.touchpoint_analysis.get('touchpoint_performance', {})
            if touchpoint_perf:
                touchpoints = list(touchpoint_perf.keys())
                satisfaction_scores = [touchpoint_perf[tp]['avg_satisfaction'] for tp in touchpoints]
                
                fig.add_trace(
                    go.Bar(x=touchpoints, y=satisfaction_scores, name='Touchpoint Satisfaction'),
                    row=2, col=1
                )
        
        # Gráfico de effort score
        if self.customer_effort_score:
            effort_dist = self.customer_effort_score.get('effort_distribution', {})
            if effort_dist:
                effort_categories = list(effort_dist.keys())
                effort_counts = list(effort_dist.values())
                
                fig.add_trace(
                    go.Bar(x=effort_categories, y=effort_counts, name='Effort Distribution'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Análisis de Experiencia del Cliente",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_cx_analysis(self, filename='customer_experience_analysis.json'):
        """Exportar análisis de experiencia del cliente"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'journey_mapping': self.journey_mapping,
            'touchpoint_analysis': self.touchpoint_analysis,
            'nps_analysis': self.nps_analysis,
            'customer_effort_score': self.customer_effort_score,
            'satisfaction_models': {k: {'metrics': v['metrics']} for k, v in self.satisfaction_models.items()},
            'cx_insights': self.cx_insights,
            'summary': {
                'total_customers': len(self.cx_data['customer_id'].unique()) if 'customer_id' in self.cx_data.columns else 0,
                'total_interactions': len(self.cx_data),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de CX exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de CX
    cx_analyzer = CustomerExperienceAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 500, 1000),
        'touchpoint': np.random.choice(['Website', 'Mobile App', 'Call Center', 'Email', 'Chat', 'Store'], 1000),
        'interaction_type': np.random.choice(['Purchase', 'Support', 'Inquiry', 'Complaint', 'Feedback'], 1000),
        'satisfaction_score': np.random.uniform(1, 5, 1000),
        'effort_score': np.random.uniform(1, 10, 1000),
        'nps_score': np.random.randint(0, 11, 1000),
        'interaction_duration': np.random.uniform(1, 30, 1000),
        'resolution_rate': np.random.uniform(0.5, 1.0, 1000),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 1000),
        'timestamp': pd.date_range('2023-01-01', periods=1000, freq='H')
    })
    
    # Cargar datos de CX
    print("📊 Cargando datos de experiencia del cliente...")
    cx_analyzer.load_cx_data(sample_data)
    
    # Analizar journey del cliente
    print("🛤️ Analizando journey del cliente...")
    journey_analysis = cx_analyzer.analyze_customer_journey()
    
    # Analizar performance de touchpoints
    print("📱 Analizando performance de touchpoints...")
    touchpoint_analysis = cx_analyzer.analyze_touchpoint_performance()
    
    # Analizar NPS
    print("⭐ Analizando Net Promoter Score...")
    nps_analysis = cx_analyzer.analyze_nps()
    
    # Analizar Customer Effort Score
    print("💪 Analizando Customer Effort Score...")
    ces_analysis = cx_analyzer.analyze_customer_effort_score()
    
    # Construir modelo de predicción de satisfacción
    print("🔮 Construyendo modelo de predicción de satisfacción...")
    satisfaction_model = cx_analyzer.build_satisfaction_prediction_model()
    
    # Generar insights de CX
    print("💡 Generando insights de experiencia del cliente...")
    cx_insights = cx_analyzer.generate_cx_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de CX...")
    dashboard = cx_analyzer.create_cx_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de CX...")
    export_data = cx_analyzer.export_cx_analysis()
    
    print("✅ Sistema de análisis de experiencia del cliente completado!")






