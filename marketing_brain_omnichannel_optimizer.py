"""
Marketing Brain Omnichannel Optimizer
Motor avanzado de optimización de canales omnichannel
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class OmnichannelOptimizer:
    def __init__(self):
        self.channel_data = {}
        self.optimization_models = {}
        self.channel_performance = {}
        self.cross_channel_analysis = {}
        self.attribution_models = {}
        self.budget_optimization = {}
        self.omnichannel_insights = {}
        
    def load_channel_data(self, channel_data):
        """Cargar datos de canales"""
        if isinstance(channel_data, str):
            if channel_data.endswith('.csv'):
                self.channel_data = pd.read_csv(channel_data)
            elif channel_data.endswith('.json'):
                with open(channel_data, 'r') as f:
                    data = json.load(f)
                self.channel_data = pd.DataFrame(data)
        else:
            self.channel_data = pd.DataFrame(channel_data)
        
        print(f"✅ Datos de canales cargados: {len(self.channel_data)} registros")
        return True
    
    def analyze_channel_performance(self):
        """Analizar performance de canales"""
        if self.channel_data.empty:
            return None
        
        # Análisis por canal
        channel_analysis = self.channel_data.groupby('channel').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'revenue': 'sum',
            'cost': 'sum',
            'engagement_rate': 'mean',
            'conversion_rate': 'mean',
            'roi': 'mean',
            'roas': 'mean'
        }).round(2)
        
        # Calcular métricas adicionales
        channel_analysis['ctr'] = (channel_analysis['clicks'] / channel_analysis['impressions']) * 100
        channel_analysis['cpc'] = channel_analysis['cost'] / channel_analysis['clicks']
        channel_analysis['cpa'] = channel_analysis['cost'] / channel_analysis['conversions']
        channel_analysis['revenue_per_impression'] = channel_analysis['revenue'] / channel_analysis['impressions']
        
        # Clasificar canales por performance
        channel_analysis['performance_tier'] = pd.cut(
            channel_analysis['roi'],
            bins=[-np.inf, 1, 3, 5, np.inf],
            labels=['Poor', 'Average', 'Good', 'Excellent']
        )
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_channel_efficiency(channel_analysis)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_channel_trends()
        
        performance_results = {
            'channel_analysis': channel_analysis.to_dict('index'),
            'efficiency_analysis': efficiency_analysis,
            'trend_analysis': trend_analysis,
            'total_channels': len(channel_analysis),
            'top_performing_channels': channel_analysis.nlargest(3, 'roi').index.tolist(),
            'underperforming_channels': channel_analysis[channel_analysis['performance_tier'] == 'Poor'].index.tolist()
        }
        
        self.channel_performance = performance_results
        return performance_results
    
    def _analyze_channel_efficiency(self, channel_analysis):
        """Analizar eficiencia de canales"""
        # Calcular score de eficiencia
        efficiency_metrics = ['roi', 'roas', 'conversion_rate', 'engagement_rate']
        efficiency_scores = {}
        
        for channel in channel_analysis.index:
            score = 0
            for metric in efficiency_metrics:
                if metric in channel_analysis.columns:
                    value = channel_analysis.loc[channel, metric]
                    # Normalizar score (0-100)
                    if metric in ['roi', 'roas']:
                        normalized_score = min(100, value * 20)  # ROI/ROAS * 20
                    else:
                        normalized_score = value * 100  # Rates * 100
                    
                    score += normalized_score
            
            efficiency_scores[channel] = score / len(efficiency_metrics)
        
        # Identificar canales más eficientes
        sorted_efficiency = sorted(efficiency_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'efficiency_scores': efficiency_scores,
            'most_efficient_channels': sorted_efficiency[:3],
            'least_efficient_channels': sorted_efficiency[-3:]
        }
    
    def _analyze_channel_trends(self):
        """Analizar tendencias de canales"""
        if 'date' not in self.channel_data.columns:
            return {}
        
        # Análisis temporal
        self.channel_data['date'] = pd.to_datetime(self.channel_data['date'])
        self.channel_data['month'] = self.channel_data['date'].dt.to_period('M')
        
        monthly_trends = self.channel_data.groupby(['channel', 'month']).agg({
            'revenue': 'sum',
            'cost': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calcular crecimiento mensual
        growth_analysis = {}
        for channel in monthly_trends['channel'].unique():
            channel_data = monthly_trends[monthly_trends['channel'] == channel].sort_values('month')
            if len(channel_data) > 1:
                revenue_growth = ((channel_data['revenue'].iloc[-1] - channel_data['revenue'].iloc[0]) / channel_data['revenue'].iloc[0]) * 100
                cost_growth = ((channel_data['cost'].iloc[-1] - channel_data['cost'].iloc[0]) / channel_data['cost'].iloc[0]) * 100
                
                growth_analysis[channel] = {
                    'revenue_growth': revenue_growth,
                    'cost_growth': cost_growth,
                    'efficiency_growth': revenue_growth - cost_growth
                }
        
        return {
            'monthly_trends': monthly_trends.to_dict('records'),
            'growth_analysis': growth_analysis
        }
    
    def analyze_cross_channel_interactions(self):
        """Analizar interacciones entre canales"""
        if 'customer_id' not in self.channel_data.columns:
            return None
        
        # Mapear journey del cliente por canales
        customer_journey = self.channel_data.groupby('customer_id').agg({
            'channel': lambda x: list(x),
            'timestamp': lambda x: list(x),
            'conversions': 'sum',
            'revenue': 'sum'
        })
        
        # Análisis de secuencias de canales
        channel_sequences = {}
        for customer_id, data in customer_journey.iterrows():
            if len(data['channel']) > 1:
                # Crear secuencias de 2 canales
                for i in range(len(data['channel']) - 1):
                    sequence = f"{data['channel'][i]} -> {data['channel'][i+1]}"
                    if sequence not in channel_sequences:
                        channel_sequences[sequence] = {
                            'count': 0,
                            'conversions': 0,
                            'revenue': 0
                        }
                    
                    channel_sequences[sequence]['count'] += 1
                    channel_sequences[sequence]['conversions'] += data['conversions']
                    channel_sequences[sequence]['revenue'] += data['revenue']
        
        # Calcular métricas de secuencias
        for sequence in channel_sequences:
            channel_sequences[sequence]['conversion_rate'] = (
                channel_sequences[sequence]['conversions'] / channel_sequences[sequence]['count']
            )
            channel_sequences[sequence]['revenue_per_interaction'] = (
                channel_sequences[sequence]['revenue'] / channel_sequences[sequence]['count']
            )
        
        # Análisis de canales complementarios
        complementary_channels = self._analyze_complementary_channels(channel_sequences)
        
        # Análisis de canales competitivos
        competitive_channels = self._analyze_competitive_channels(channel_sequences)
        
        cross_channel_results = {
            'channel_sequences': channel_sequences,
            'complementary_channels': complementary_channels,
            'competitive_channels': competitive_channels,
            'total_sequences': len(channel_sequences),
            'most_common_sequences': sorted(channel_sequences.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        }
        
        self.cross_channel_analysis = cross_channel_results
        return cross_channel_results
    
    def _analyze_complementary_channels(self, channel_sequences):
        """Analizar canales complementarios"""
        complementary = {}
        
        for sequence, data in channel_sequences.items():
            if data['conversion_rate'] > 0.1:  # Umbral de conversión
                channels = sequence.split(' -> ')
                if channels[0] not in complementary:
                    complementary[channels[0]] = []
                
                complementary[channels[0]].append({
                    'complementary_channel': channels[1],
                    'conversion_rate': data['conversion_rate'],
                    'revenue_per_interaction': data['revenue_per_interaction']
                })
        
        # Ordenar por performance
        for channel in complementary:
            complementary[channel].sort(key=lambda x: x['conversion_rate'], reverse=True)
        
        return complementary
    
    def _analyze_competitive_channels(self, channel_sequences):
        """Analizar canales competitivos"""
        competitive = {}
        
        # Identificar canales que compiten por la misma audiencia
        channel_performance = {}
        for sequence, data in channel_sequences.items():
            channels = sequence.split(' -> ')
            for channel in channels:
                if channel not in channel_performance:
                    channel_performance[channel] = {
                        'total_interactions': 0,
                        'total_conversions': 0,
                        'total_revenue': 0
                    }
                
                channel_performance[channel]['total_interactions'] += data['count']
                channel_performance[channel]['total_conversions'] += data['conversions']
                channel_performance[channel]['total_revenue'] += data['revenue']
        
        # Calcular métricas de competencia
        for channel in channel_performance:
            performance = channel_performance[channel]
            performance['conversion_rate'] = performance['total_conversions'] / performance['total_interactions']
            performance['revenue_per_interaction'] = performance['total_revenue'] / performance['total_interactions']
        
        # Identificar canales con performance similar (competidores)
        channels = list(channel_performance.keys())
        for i, channel1 in enumerate(channels):
            for channel2 in channels[i+1:]:
                perf1 = channel_performance[channel1]
                perf2 = channel_performance[channel2]
                
                # Si las métricas son similares, son competidores
                if abs(perf1['conversion_rate'] - perf2['conversion_rate']) < 0.05:
                    if channel1 not in competitive:
                        competitive[channel1] = []
                    competitive[channel1].append({
                        'competitive_channel': channel2,
                        'performance_difference': abs(perf1['conversion_rate'] - perf2['conversion_rate'])
                    })
        
        return competitive
    
    def build_attribution_model(self, model_type='shapley'):
        """Construir modelo de atribución"""
        if 'customer_id' not in self.channel_data.columns:
            return None
        
        # Preparar datos para atribución
        customer_data = self.channel_data.groupby('customer_id').agg({
            'channel': lambda x: list(x),
            'conversions': 'sum',
            'revenue': 'sum',
            'cost': 'sum'
        })
        
        if model_type == 'shapley':
            attribution_results = self._calculate_shapley_attribution(customer_data)
        elif model_type == 'linear':
            attribution_results = self._calculate_linear_attribution(customer_data)
        elif model_type == 'time_decay':
            attribution_results = self._calculate_time_decay_attribution(customer_data)
        else:
            attribution_results = self._calculate_first_click_attribution(customer_data)
        
        self.attribution_models[model_type] = attribution_results
        return attribution_results
    
    def _calculate_shapley_attribution(self, customer_data):
        """Calcular atribución de Shapley"""
        # Implementación simplificada de Shapley
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Distribuir crédito equitativamente entre canales
                credit_per_channel = data['revenue'] / len(channels)
                
                for channel in channels:
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit_per_channel
        
        return {
            'model_type': 'shapley',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_linear_attribution(self, customer_data):
        """Calcular atribución lineal"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Distribuir crédito linealmente
                credit_per_channel = data['revenue'] / len(channels)
                
                for channel in channels:
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit_per_channel
        
        return {
            'model_type': 'linear',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_time_decay_attribution(self, customer_data):
        """Calcular atribución con decaimiento temporal"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 1:
                # Aplicar decaimiento temporal (más peso a canales recientes)
                total_weight = sum(range(1, len(channels) + 1))
                
                for i, channel in enumerate(channels):
                    weight = (i + 1) / total_weight
                    credit = data['revenue'] * weight
                    
                    if channel not in channel_contributions:
                        channel_contributions[channel] = 0
                    channel_contributions[channel] += credit
        
        return {
            'model_type': 'time_decay',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def _calculate_first_click_attribution(self, customer_data):
        """Calcular atribución de primer clic"""
        channel_contributions = {}
        
        for customer_id, data in customer_data.iterrows():
            channels = data['channel']
            if len(channels) > 0:
                # Dar todo el crédito al primer canal
                first_channel = channels[0]
                
                if first_channel not in channel_contributions:
                    channel_contributions[first_channel] = 0
                channel_contributions[first_channel] += data['revenue']
        
        return {
            'model_type': 'first_click',
            'channel_contributions': channel_contributions,
            'total_attributed_revenue': sum(channel_contributions.values())
        }
    
    def optimize_budget_allocation(self, total_budget, optimization_goal='roi'):
        """Optimizar asignación de presupuesto"""
        if self.channel_data.empty:
            return None
        
        # Preparar datos para optimización
        channel_metrics = self.channel_data.groupby('channel').agg({
            'cost': 'sum',
            'revenue': 'sum',
            'conversions': 'sum',
            'roi': 'mean',
            'roas': 'mean'
        })
        
        channels = channel_metrics.index.tolist()
        n_channels = len(channels)
        
        # Función objetivo
        def objective(x):
            if optimization_goal == 'roi':
                return -sum(x[i] * channel_metrics.loc[channels[i], 'roi'] for i in range(n_channels))
            elif optimization_goal == 'roas':
                return -sum(x[i] * channel_metrics.loc[channels[i], 'roas'] for i in range(n_channels))
            else:  # revenue
                return -sum(x[i] * channel_metrics.loc[channels[i], 'revenue'] for i in range(n_channels))
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}  # Suma debe ser igual al presupuesto total
        ]
        
        # Límites (cada canal debe recibir al menos 5% y máximo 50%)
        bounds = [(total_budget * 0.05, total_budget * 0.5) for _ in range(n_channels)]
        
        # Punto inicial (distribución uniforme)
        x0 = np.ones(n_channels) * (total_budget / n_channels)
        
        # Optimización
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        # Resultados de optimización
        optimal_allocation = {}
        for i, channel in enumerate(channels):
            optimal_allocation[channel] = {
                'allocated_budget': result.x[i],
                'allocation_percentage': (result.x[i] / total_budget) * 100,
                'current_budget': channel_metrics.loc[channel, 'cost'],
                'current_percentage': (channel_metrics.loc[channel, 'cost'] / total_budget) * 100,
                'expected_roi': channel_metrics.loc[channel, 'roi'],
                'expected_roas': channel_metrics.loc[channel, 'roas']
            }
        
        # Calcular impacto esperado
        expected_impact = {
            'total_roi': sum(optimal_allocation[channel]['allocated_budget'] * optimal_allocation[channel]['expected_roi'] for channel in channels),
            'total_roas': sum(optimal_allocation[channel]['allocated_budget'] * optimal_allocation[channel]['expected_roas'] for channel in channels),
            'optimization_status': result.success
        }
        
        optimization_results = {
            'optimal_allocation': optimal_allocation,
            'expected_impact': expected_impact,
            'optimization_goal': optimization_goal,
            'total_budget': total_budget
        }
        
        self.budget_optimization = optimization_results
        return optimization_results
    
    def generate_omnichannel_insights(self):
        """Generar insights de omnichannel"""
        insights = []
        
        # Insights de performance de canales
        if self.channel_performance:
            performance = self.channel_performance
            underperforming = performance.get('underperforming_channels', [])
            if underperforming:
                insights.append({
                    'category': 'Channel Performance',
                    'insight': f'{len(underperforming)} canales con performance pobre',
                    'recommendation': 'Revisar y optimizar canales subdesempeñados',
                    'priority': 'high'
                })
        
        # Insights de cross-channel
        if self.cross_channel_analysis:
            cross_channel = self.cross_channel_analysis
            complementary = cross_channel.get('complementary_channels', {})
            if complementary:
                insights.append({
                    'category': 'Cross-Channel',
                    'insight': f'{len(complementary)} canales con canales complementarios identificados',
                    'recommendation': 'Aprovechar sinergias entre canales complementarios',
                    'priority': 'medium'
                })
        
        # Insights de atribución
        if self.attribution_models:
            attribution = self.attribution_models
            if 'shapley' in attribution:
                contributions = attribution['shapley']['channel_contributions']
                top_contributor = max(contributions, key=contributions.get)
                insights.append({
                    'category': 'Attribution',
                    'insight': f'{top_contributor} es el mayor contribuidor según modelo Shapley',
                    'recommendation': 'Aumentar inversión en canales de alto impacto',
                    'priority': 'medium'
                })
        
        # Insights de optimización de presupuesto
        if self.budget_optimization:
            budget_opt = self.budget_optimization
            if budget_opt['expected_impact']['optimization_status']:
                insights.append({
                    'category': 'Budget Optimization',
                    'insight': 'Optimización de presupuesto completada exitosamente',
                    'recommendation': 'Implementar nueva asignación de presupuesto',
                    'priority': 'high'
                })
        
        self.omnichannel_insights = insights
        return insights
    
    def create_omnichannel_dashboard(self):
        """Crear dashboard de optimización omnichannel"""
        if not self.channel_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Performance', 'Cross-Channel Analysis',
                          'Attribution Models', 'Budget Optimization'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Gráfico de performance de canales
        if self.channel_performance:
            performance = self.channel_performance.get('channel_analysis', {})
            if performance:
                channels = list(performance.keys())
                roi_values = [performance[channel]['roi'] for channel in channels]
                
                fig.add_trace(
                    go.Bar(x=channels, y=roi_values, name='Channel ROI'),
                    row=1, col=1
                )
        
        # Gráfico de análisis cross-channel
        if self.cross_channel_analysis:
            cross_channel = self.cross_channel_analysis
            sequences = cross_channel.get('most_common_sequences', [])
            if sequences:
                sequence_names = [seq[0] for seq in sequences[:5]]
                sequence_counts = [seq[1]['count'] for seq in sequences[:5]]
                
                fig.add_trace(
                    go.Bar(x=sequence_names, y=sequence_counts, name='Channel Sequences'),
                    row=1, col=2
                )
        
        # Gráfico de modelos de atribución
        if self.attribution_models:
            attribution = self.attribution_models.get('shapley', {})
            if attribution and 'channel_contributions' in attribution:
                contributions = attribution['channel_contributions']
                channels = list(contributions.keys())
                values = list(contributions.values())
                
                fig.add_trace(
                    go.Pie(labels=channels, values=values, name='Channel Attribution'),
                    row=2, col=1
                )
        
        # Gráfico de optimización de presupuesto
        if self.budget_optimization:
            budget_opt = self.budget_optimization.get('optimal_allocation', {})
            if budget_opt:
                channels = list(budget_opt.keys())
                allocations = [budget_opt[channel]['allocation_percentage'] for channel in channels]
                
                fig.add_trace(
                    go.Bar(x=channels, y=allocations, name='Budget Allocation'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización Omnichannel",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_omnichannel_analysis(self, filename='omnichannel_optimization_analysis.json'):
        """Exportar análisis de optimización omnichannel"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'channel_performance': self.channel_performance,
            'cross_channel_analysis': self.cross_channel_analysis,
            'attribution_models': self.attribution_models,
            'budget_optimization': self.budget_optimization,
            'omnichannel_insights': self.omnichannel_insights,
            'summary': {
                'total_channels': len(self.channel_data['channel'].unique()) if 'channel' in self.channel_data.columns else 0,
                'total_interactions': len(self.channel_data),
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis omnichannel exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador omnichannel
    omnichannel_optimizer = OmnichannelOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'channel': np.random.choice(['Google Ads', 'Facebook', 'Instagram', 'Email', 'SMS', 'Website'], 1000),
        'customer_id': np.random.randint(1, 500, 1000),
        'impressions': np.random.poisson(10000, 1000),
        'clicks': np.random.poisson(500, 1000),
        'conversions': np.random.poisson(50, 1000),
        'revenue': np.random.normal(5000, 1000, 1000),
        'cost': np.random.normal(1000, 200, 1000),
        'engagement_rate': np.random.uniform(0.02, 0.08, 1000),
        'conversion_rate': np.random.uniform(0.01, 0.05, 1000),
        'roi': np.random.uniform(1, 5, 1000),
        'roas': np.random.uniform(2, 8, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de canales
    print("📊 Cargando datos de canales...")
    omnichannel_optimizer.load_channel_data(sample_data)
    
    # Analizar performance de canales
    print("📈 Analizando performance de canales...")
    channel_performance = omnichannel_optimizer.analyze_channel_performance()
    
    # Analizar interacciones cross-channel
    print("🔄 Analizando interacciones cross-channel...")
    cross_channel_analysis = omnichannel_optimizer.analyze_cross_channel_interactions()
    
    # Construir modelo de atribución
    print("🎯 Construyendo modelo de atribución...")
    attribution_model = omnichannel_optimizer.build_attribution_model('shapley')
    
    # Optimizar asignación de presupuesto
    print("💰 Optimizando asignación de presupuesto...")
    budget_optimization = omnichannel_optimizer.optimize_budget_allocation(100000, 'roi')
    
    # Generar insights omnichannel
    print("💡 Generando insights omnichannel...")
    omnichannel_insights = omnichannel_optimizer.generate_omnichannel_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard omnichannel...")
    dashboard = omnichannel_optimizer.create_omnichannel_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis omnichannel...")
    export_data = omnichannel_optimizer.export_omnichannel_analysis()
    
    print("✅ Sistema de optimización omnichannel completado!")




