"""
Marketing Brain Customer Retention Analyzer
Sistema avanzado de análisis de retención de clientes
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

class CustomerRetentionAnalyzer:
    def __init__(self):
        self.retention_data = {}
        self.cohort_analysis = {}
        self.churn_prediction_models = {}
        self.lifetime_value_analysis = {}
        self.retention_segments = {}
        self.retention_strategies = {}
        self.retention_insights = {}
        
    def load_retention_data(self, retention_data):
        """Cargar datos de retención de clientes"""
        if isinstance(retention_data, str):
            if retention_data.endswith('.csv'):
                self.retention_data = pd.read_csv(retention_data)
            elif retention_data.endswith('.json'):
                with open(retention_data, 'r') as f:
                    data = json.load(f)
                self.retention_data = pd.DataFrame(data)
        else:
            self.retention_data = pd.DataFrame(retention_data)
        
        print(f"✅ Datos de retención cargados: {len(self.retention_data)} registros")
        return True
    
    def analyze_cohort_retention(self, cohort_period='monthly'):
        """Analizar retención por cohortes"""
        if self.retention_data.empty:
            return None
        
        # Preparar datos
        data = self.retention_data.copy()
        data['signup_date'] = pd.to_datetime(data['signup_date'])
        
        # Crear cohortes
        if cohort_period == 'monthly':
            data['cohort'] = data['signup_date'].dt.to_period('M')
        elif cohort_period == 'weekly':
            data['cohort'] = data['signup_date'].dt.to_period('W')
        elif cohort_period == 'quarterly':
            data['cohort'] = data['signup_date'].dt.to_period('Q')
        else:
            data['cohort'] = data['signup_date'].dt.to_period('M')
        
        # Calcular período desde signup
        data['period_number'] = (data['last_activity_date'].dt.to_period(cohort_period[0].upper()) - data['cohort']).apply(attrgetter('n'))
        
        # Crear tabla de cohortes
        cohort_table = data.groupby(['cohort', 'period_number']).agg({
            'customer_id': 'nunique',
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Pivotar tabla
        cohort_pivot = cohort_table.pivot(index='cohort', columns='period_number', values='customer_id')
        
        # Calcular tasas de retención
        cohort_sizes = cohort_pivot.iloc[:, 0]
        retention_rates = cohort_pivot.divide(cohort_sizes, axis=0)
        
        # Análisis de cohortes
        cohort_analysis = {
            'cohort_table': cohort_pivot.to_dict(),
            'retention_rates': retention_rates.to_dict(),
            'cohort_sizes': cohort_sizes.to_dict(),
            'average_retention': retention_rates.mean().to_dict(),
            'retention_trends': self._analyze_retention_trends(retention_rates)
        }
        
        # Análisis de revenue por cohorte
        revenue_cohort = data.groupby(['cohort', 'period_number'])['revenue'].sum().reset_index()
        revenue_pivot = revenue_cohort.pivot(index='cohort', columns='period_number', values='revenue')
        
        cohort_analysis['revenue_by_cohort'] = revenue_pivot.to_dict()
        cohort_analysis['average_revenue_per_period'] = revenue_pivot.mean().to_dict()
        
        # Análisis de lifetime value por cohorte
        cohort_lifetime_value = data.groupby('cohort').agg({
            'revenue': 'sum',
            'customer_id': 'nunique',
            'orders': 'sum'
        }).reset_index()
        
        cohort_lifetime_value['avg_lifetime_value'] = cohort_lifetime_value['revenue'] / cohort_lifetime_value['customer_id']
        cohort_lifetime_value['avg_orders_per_customer'] = cohort_lifetime_value['orders'] / cohort_lifetime_value['customer_id']
        
        cohort_analysis['lifetime_value_by_cohort'] = cohort_lifetime_value.to_dict('records')
        
        self.cohort_analysis = cohort_analysis
        return cohort_analysis
    
    def _analyze_retention_trends(self, retention_rates):
        """Analizar tendencias de retención"""
        trends = {}
        
        # Tendencias por período
        for period in retention_rates.columns:
            period_retention = retention_rates[period].dropna()
            if len(period_retention) > 1:
                trend = self._calculate_trend(period_retention.values)
                trends[f'period_{period}'] = trend
        
        # Tendencias generales
        overall_trend = self._calculate_trend(retention_rates.mean().values)
        trends['overall'] = overall_trend
        
        return trends
    
    def _calculate_trend(self, values):
        """Calcular tendencia de una serie de valores"""
        if len(values) < 2:
            return {'direction': 'stable', 'slope': 0, 'strength': 0}
        
        x = np.arange(len(values))
        y = values
        
        # Regresión lineal
        slope = np.polyfit(x, y, 1)[0]
        correlation = np.corrcoef(x, y)[0, 1]
        
        if slope > 0.01:
            direction = 'increasing'
        elif slope < -0.01:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(correlation)
        }
    
    def build_churn_prediction_model(self, target_variable='churned'):
        """Construir modelo de predicción de churn"""
        if target_variable not in self.retention_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.retention_data.columns if col != target_variable and col != 'customer_id']
        X = self.retention_data[feature_columns]
        y = self.retention_data[target_variable]
        
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
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        model_metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
        
        # Guardar modelo
        self.churn_prediction_models['churn_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def predict_churn_risk(self, customer_data=None):
        """Predecir riesgo de churn"""
        if customer_data is None:
            customer_data = self.retention_data
        
        if 'churn_predictor' not in self.churn_prediction_models:
            raise ValueError("Modelo de predicción de churn no encontrado. Ejecute build_churn_prediction_model() primero.")
        
        model_info = self.churn_prediction_models['churn_predictor']
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
        
        # Predecir probabilidades de churn
        churn_probabilities = model.predict_proba(X_scaled)[:, 1]
        
        # Clasificar riesgo de churn
        churn_risk_categories = []
        for prob in churn_probabilities:
            if prob >= 0.8:
                category = 'High Risk'
            elif prob >= 0.6:
                category = 'Medium Risk'
            elif prob >= 0.4:
                category = 'Low Risk'
            else:
                category = 'Very Low Risk'
            
            churn_risk_categories.append(category)
        
        # Crear DataFrame de resultados
        results = customer_data.copy()
        results['churn_probability'] = churn_probabilities
        results['churn_risk_category'] = churn_risk_categories
        results['prediction_date'] = datetime.now().isoformat()
        
        return results
    
    def analyze_lifetime_value(self):
        """Analizar valor de vida del cliente"""
        if self.retention_data.empty:
            return None
        
        # Calcular métricas de CLV
        clv_metrics = self.retention_data.groupby('customer_id').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'signup_date': 'min',
            'last_activity_date': 'max'
        }).reset_index()
        
        # Calcular duración de vida
        clv_metrics['lifetime_days'] = (clv_metrics['last_activity_date'] - clv_metrics['signup_date']).dt.days
        
        # Calcular métricas adicionales
        clv_metrics['avg_order_value'] = clv_metrics['revenue'] / clv_metrics['orders']
        clv_metrics['purchase_frequency'] = clv_metrics['orders'] / (clv_metrics['lifetime_days'] / 365)
        
        # Análisis de segmentos de CLV
        clv_metrics['clv_segment'] = pd.cut(
            clv_metrics['revenue'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Low', 'Medium', 'High', 'VIP']
        )
        
        # Análisis por segmento
        segment_analysis = clv_metrics.groupby('clv_segment').agg({
            'revenue': ['count', 'mean', 'sum'],
            'orders': 'mean',
            'lifetime_days': 'mean',
            'purchase_frequency': 'mean'
        }).round(2)
        
        segment_analysis.columns = [
            'customer_count', 'avg_clv', 'total_revenue',
            'avg_orders', 'avg_lifetime_days', 'avg_purchase_frequency'
        }
        
        # Análisis de cohortes de CLV
        clv_metrics['signup_month'] = clv_metrics['signup_date'].dt.to_period('M')
        cohort_clv = clv_metrics.groupby('signup_month')['revenue'].agg(['mean', 'median', 'std']).round(2)
        
        # Análisis de retención por CLV
        retention_by_clv = self._analyze_retention_by_clv(clv_metrics)
        
        lifetime_value_analysis = {
            'clv_metrics': clv_metrics.to_dict('records'),
            'segment_analysis': segment_analysis.to_dict('index'),
            'cohort_clv': cohort_clv.to_dict('index'),
            'retention_by_clv': retention_by_clv,
            'overall_metrics': {
                'avg_clv': clv_metrics['revenue'].mean(),
                'median_clv': clv_metrics['revenue'].median(),
                'total_customers': len(clv_metrics),
                'total_revenue': clv_metrics['revenue'].sum()
            }
        }
        
        self.lifetime_value_analysis = lifetime_value_analysis
        return lifetime_value_analysis
    
    def _analyze_retention_by_clv(self, clv_metrics):
        """Analizar retención por segmento de CLV"""
        retention_analysis = {}
        
        for segment in clv_metrics['clv_segment'].unique():
            segment_data = clv_metrics[clv_metrics['clv_segment'] == segment]
            
            # Calcular métricas de retención
            avg_lifetime = segment_data['lifetime_days'].mean()
            avg_orders = segment_data['orders'].mean()
            avg_frequency = segment_data['purchase_frequency'].mean()
            
            retention_analysis[segment] = {
                'avg_lifetime_days': avg_lifetime,
                'avg_orders': avg_orders,
                'avg_purchase_frequency': avg_frequency,
                'customer_count': len(segment_data)
            }
        
        return retention_analysis
    
    def create_retention_segments(self):
        """Crear segmentos de retención"""
        if self.retention_data.empty:
            return None
        
        # Preparar datos
        data = self.retention_data.copy()
        
        # Calcular métricas de retención por cliente
        customer_metrics = data.groupby('customer_id').agg({
            'revenue': 'sum',
            'orders': 'sum',
            'signup_date': 'min',
            'last_activity_date': 'max',
            'churned': 'max'
        }).reset_index()
        
        customer_metrics['lifetime_days'] = (customer_metrics['last_activity_date'] - customer_metrics['signup_date']).dt.days
        customer_metrics['avg_order_value'] = customer_metrics['revenue'] / customer_metrics['orders']
        customer_metrics['purchase_frequency'] = customer_metrics['orders'] / (customer_metrics['lifetime_days'] / 365)
        
        # Crear segmentos usando clustering
        features = ['revenue', 'orders', 'lifetime_days', 'avg_order_value', 'purchase_frequency']
        X = customer_metrics[features].fillna(0)
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Clustering K-means
        kmeans = KMeans(n_clusters=4, random_state=42)
        customer_metrics['retention_segment'] = kmeans.fit_predict(X_scaled)
        
        # Nombrar segmentos
        segment_names = {
            0: 'At Risk',
            1: 'Stable',
            2: 'Loyal',
            3: 'Champions'
        }
        
        customer_metrics['retention_segment_name'] = customer_metrics['retention_segment'].map(segment_names)
        
        # Análisis de segmentos
        segment_analysis = customer_metrics.groupby('retention_segment_name').agg({
            'revenue': ['count', 'mean', 'sum'],
            'orders': 'mean',
            'lifetime_days': 'mean',
            'churned': 'mean'
        }).round(2)
        
        segment_analysis.columns = [
            'customer_count', 'avg_revenue', 'total_revenue',
            'avg_orders', 'avg_lifetime_days', 'churn_rate'
        }
        
        retention_segments = {
            'customer_segments': customer_metrics.to_dict('records'),
            'segment_analysis': segment_analysis.to_dict('index'),
            'segment_characteristics': self._analyze_segment_characteristics(customer_metrics)
        }
        
        self.retention_segments = retention_segments
        return retention_segments
    
    def _analyze_segment_characteristics(self, customer_metrics):
        """Analizar características de segmentos"""
        characteristics = {}
        
        for segment in customer_metrics['retention_segment_name'].unique():
            segment_data = customer_metrics[customer_metrics['retention_segment_name'] == segment]
            
            characteristics[segment] = {
                'avg_revenue': segment_data['revenue'].mean(),
                'avg_orders': segment_data['orders'].mean(),
                'avg_lifetime_days': segment_data['lifetime_days'].mean(),
                'churn_rate': segment_data['churned'].mean(),
                'customer_count': len(segment_data),
                'percentage': len(segment_data) / len(customer_metrics) * 100
            }
        
        return characteristics
    
    def generate_retention_strategies(self):
        """Generar estrategias de retención"""
        strategies = []
        
        # Estrategias basadas en segmentos
        if self.retention_segments:
            segment_analysis = self.retention_segments.get('segment_analysis', {})
            
            for segment, data in segment_analysis.items():
                churn_rate = data.get('churn_rate', 0)
                customer_count = data.get('customer_count', 0)
                
                if segment == 'At Risk' and churn_rate > 0.3:
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Win-back Campaign',
                        'description': 'Implementar campaña de reactivación con ofertas especiales',
                        'priority': 'high',
                        'expected_impact': 'medium'
                    })
                
                elif segment == 'Stable' and churn_rate > 0.1:
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Loyalty Program',
                        'description': 'Crear programa de lealtad para aumentar engagement',
                        'priority': 'medium',
                        'expected_impact': 'high'
                    })
                
                elif segment == 'Loyal':
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Upsell/Cross-sell',
                        'description': 'Ofrecer productos complementarios y upgrades',
                        'priority': 'medium',
                        'expected_impact': 'high'
                    })
                
                elif segment == 'Champions':
                    strategies.append({
                        'segment': segment,
                        'strategy': 'Referral Program',
                        'description': 'Implementar programa de referidos para aprovechar advocacy',
                        'priority': 'low',
                        'expected_impact': 'high'
                    })
        
        # Estrategias basadas en análisis de cohortes
        if self.cohort_analysis:
            avg_retention = self.cohort_analysis.get('average_retention', {})
            if avg_retention:
                # Estrategia para mejorar retención temprana
                early_retention = avg_retention.get('1', 0)  # Retención en período 1
                if early_retention < 0.7:
                    strategies.append({
                        'segment': 'All',
                        'strategy': 'Onboarding Optimization',
                        'description': 'Mejorar proceso de onboarding para aumentar retención temprana',
                        'priority': 'high',
                        'expected_impact': 'high'
                    })
        
        # Estrategias basadas en análisis de CLV
        if self.lifetime_value_analysis:
            overall_metrics = self.lifetime_value_analysis.get('overall_metrics', {})
            avg_clv = overall_metrics.get('avg_clv', 0)
            
            if avg_clv < 500:  # Umbral de CLV bajo
                strategies.append({
                    'segment': 'Low CLV',
                    'strategy': 'Value Enhancement',
                    'description': 'Implementar estrategias para aumentar valor por cliente',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        self.retention_strategies = strategies
        return strategies
    
    def generate_retention_insights(self):
        """Generar insights de retención"""
        insights = []
        
        # Insights de cohortes
        if self.cohort_analysis:
            cohort_analysis = self.cohort_analysis
            avg_retention = cohort_analysis.get('average_retention', {})
            
            if avg_retention:
                # Análisis de retención temprana
                early_retention = avg_retention.get('1', 0)
                if early_retention < 0.7:
                    insights.append({
                        'category': 'Cohort Analysis',
                        'insight': f'Retención temprana baja: {early_retention:.1%}',
                        'recommendation': 'Mejorar onboarding y primera experiencia',
                        'priority': 'high'
                    })
                
                # Análisis de retención a largo plazo
                long_term_retention = avg_retention.get('12', 0)  # Retención a 12 meses
                if long_term_retention < 0.3:
                    insights.append({
                        'category': 'Cohort Analysis',
                        'insight': f'Retención a largo plazo baja: {long_term_retention:.1%}',
                        'recommendation': 'Implementar estrategias de retención a largo plazo',
                        'priority': 'high'
                    })
        
        # Insights de segmentos
        if self.retention_segments:
            segment_analysis = self.retention_segments.get('segment_analysis', {})
            
            at_risk_count = segment_analysis.get('At Risk', {}).get('customer_count', 0)
            total_customers = sum(segment.get('customer_count', 0) for segment in segment_analysis.values())
            
            if at_risk_count > 0 and total_customers > 0:
                at_risk_percentage = at_risk_count / total_customers * 100
                if at_risk_percentage > 20:
                    insights.append({
                        'category': 'Segmentation',
                        'insight': f'{at_risk_percentage:.1f}% de clientes en riesgo',
                        'recommendation': 'Implementar campañas de retención urgentes',
                        'priority': 'high'
                    })
        
        # Insights de CLV
        if self.lifetime_value_analysis:
            overall_metrics = self.lifetime_value_analysis.get('overall_metrics', {})
            avg_clv = overall_metrics.get('avg_clv', 0)
            
            if avg_clv < 500:
                insights.append({
                    'category': 'Lifetime Value',
                    'insight': f'CLV promedio bajo: ${avg_clv:.2f}',
                    'recommendation': 'Implementar estrategias para aumentar valor por cliente',
                    'priority': 'medium'
                })
        
        # Insights de predicción de churn
        if self.churn_prediction_models:
            churn_model = self.churn_prediction_models.get('churn_predictor', {})
            if churn_model:
                metrics = churn_model.get('metrics', {})
                accuracy = metrics.get('accuracy', 0)
                
                if accuracy > 0.8:
                    insights.append({
                        'category': 'Churn Prediction',
                        'insight': f'Modelo de churn con alta precisión: {accuracy:.1%}',
                        'recommendation': 'Usar modelo para identificar clientes en riesgo',
                        'priority': 'medium'
                    })
        
        self.retention_insights = insights
        return insights
    
    def create_retention_dashboard(self):
        """Crear dashboard de análisis de retención"""
        if not self.retention_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cohort Retention', 'CLV Analysis',
                          'Retention Segments', 'Churn Risk Distribution'),
            specs=[[{"type": "heatmap"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de retención por cohortes
        if self.cohort_analysis:
            retention_rates = self.cohort_analysis.get('retention_rates', {})
            if retention_rates:
                # Crear heatmap de retención
                cohorts = list(retention_rates.keys())
                periods = list(set().union(*[list(data.keys()) for data in retention_rates.values()]))
                
                # Preparar datos para heatmap
                heatmap_data = []
                for cohort in cohorts:
                    row = []
                    for period in periods:
                        value = retention_rates[cohort].get(period, 0)
                        row.append(value)
                    heatmap_data.append(row)
                
                fig.add_trace(
                    go.Heatmap(
                        z=heatmap_data,
                        x=periods,
                        y=cohorts,
                        colorscale='RdYlGn',
                        name='Retention Rate'
                    ),
                    row=1, col=1
                )
        
        # Gráfico de análisis de CLV
        if self.lifetime_value_analysis:
            segment_analysis = self.lifetime_value_analysis.get('segment_analysis', {})
            if segment_analysis:
                segments = list(segment_analysis.keys())
                avg_clv = [segment_analysis[segment]['avg_clv'] for segment in segments]
                
                fig.add_trace(
                    go.Bar(x=segments, y=avg_clv, name='Average CLV by Segment'),
                    row=1, col=2
                )
        
        # Gráfico de segmentos de retención
        if self.retention_segments:
            segment_analysis = self.retention_segments.get('segment_analysis', {})
            if segment_analysis:
                segments = list(segment_analysis.keys())
                customer_counts = [segment_analysis[segment]['customer_count'] for segment in segments]
                
                fig.add_trace(
                    go.Pie(labels=segments, values=customer_counts, name='Retention Segments'),
                    row=2, col=1
                )
        
        # Gráfico de distribución de riesgo de churn
        if self.churn_prediction_models:
            # Simular datos de riesgo de churn
            risk_categories = ['Very Low Risk', 'Low Risk', 'Medium Risk', 'High Risk']
            risk_counts = [np.random.randint(100, 300) for _ in risk_categories]
            
            fig.add_trace(
                go.Bar(x=risk_categories, y=risk_counts, name='Churn Risk Distribution'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Análisis de Retención de Clientes",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_retention_analysis(self, filename='customer_retention_analysis.json'):
        """Exportar análisis de retención"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'cohort_analysis': self.cohort_analysis,
            'lifetime_value_analysis': self.lifetime_value_analysis,
            'retention_segments': self.retention_segments,
            'churn_prediction_models': {k: {'metrics': v['metrics']} for k, v in self.churn_prediction_models.items()},
            'retention_strategies': self.retention_strategies,
            'retention_insights': self.retention_insights,
            'summary': {
                'total_customers': len(self.retention_data['customer_id'].unique()) if 'customer_id' in self.retention_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de retención exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de retención
    retention_analyzer = CustomerRetentionAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 1000, 2000),
        'signup_date': pd.date_range('2022-01-01', periods=2000, freq='D'),
        'last_activity_date': pd.date_range('2023-01-01', periods=2000, freq='D'),
        'revenue': np.random.normal(500, 200, 2000),
        'orders': np.random.poisson(5, 2000),
        'churned': np.random.choice([0, 1], 2000, p=[0.7, 0.3]),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 2000),
        'satisfaction_score': np.random.uniform(1, 5, 2000),
        'engagement_score': np.random.uniform(0, 10, 2000)
    })
    
    # Cargar datos de retención
    print("📊 Cargando datos de retención...")
    retention_analyzer.load_retention_data(sample_data)
    
    # Analizar retención por cohortes
    print("📈 Analizando retención por cohortes...")
    cohort_analysis = retention_analyzer.analyze_cohort_retention()
    
    # Construir modelo de predicción de churn
    print("🔮 Construyendo modelo de predicción de churn...")
    churn_model = retention_analyzer.build_churn_prediction_model()
    
    # Predecir riesgo de churn
    print("⚠️ Prediciendo riesgo de churn...")
    churn_predictions = retention_analyzer.predict_churn_risk()
    
    # Analizar valor de vida del cliente
    print("💰 Analizando valor de vida del cliente...")
    clv_analysis = retention_analyzer.analyze_lifetime_value()
    
    # Crear segmentos de retención
    print("👥 Creando segmentos de retención...")
    retention_segments = retention_analyzer.create_retention_segments()
    
    # Generar estrategias de retención
    print("🎯 Generando estrategias de retención...")
    retention_strategies = retention_analyzer.generate_retention_strategies()
    
    # Generar insights de retención
    print("💡 Generando insights de retención...")
    retention_insights = retention_analyzer.generate_retention_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de retención...")
    dashboard = retention_analyzer.create_retention_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de retención...")
    export_data = retention_analyzer.export_retention_analysis()
    
    print("✅ Sistema de análisis de retención de clientes completado!")






