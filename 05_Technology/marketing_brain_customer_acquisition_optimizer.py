"""
Marketing Brain Customer Acquisition Optimizer
Motor avanzado de optimización de customer acquisition
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
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class CustomerAcquisitionOptimizer:
    def __init__(self):
        self.acquisition_data = {}
        self.channel_analysis = {}
        self.acquisition_models = {}
        self.cost_optimization = {}
        self.acquisition_funnels = {}
        self.acquisition_insights = {}
        self.optimization_strategies = {}
        
    def load_acquisition_data(self, acquisition_data):
        """Cargar datos de customer acquisition"""
        if isinstance(acquisition_data, str):
            if acquisition_data.endswith('.csv'):
                self.acquisition_data = pd.read_csv(acquisition_data)
            elif acquisition_data.endswith('.json'):
                with open(acquisition_data, 'r') as f:
                    data = json.load(f)
                self.acquisition_data = pd.DataFrame(data)
        else:
            self.acquisition_data = pd.DataFrame(acquisition_data)
        
        print(f"✅ Datos de customer acquisition cargados: {len(self.acquisition_data)} registros")
        return True
    
    def analyze_acquisition_channels(self):
        """Analizar canales de adquisición"""
        if self.acquisition_data.empty:
            return None
        
        # Análisis de canales por performance
        channel_analysis = self.acquisition_data.groupby('acquisition_channel').agg({
            'leads': 'sum',
            'conversions': 'sum',
            'cost': 'sum',
            'revenue': 'sum',
            'customers': 'sum'
        }).reset_index()
        
        # Calcular métricas de performance
        channel_analysis['conversion_rate'] = (channel_analysis['conversions'] / channel_analysis['leads']) * 100
        channel_analysis['cost_per_lead'] = channel_analysis['cost'] / channel_analysis['leads']
        channel_analysis['cost_per_acquisition'] = channel_analysis['cost'] / channel_analysis['customers']
        channel_analysis['roi'] = (channel_analysis['revenue'] - channel_analysis['cost']) / channel_analysis['cost']
        channel_analysis['roas'] = channel_analysis['revenue'] / channel_analysis['cost']
        channel_analysis['lifetime_value'] = channel_analysis['revenue'] / channel_analysis['customers']
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_channel_efficiency(channel_analysis)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_channel_trends()
        
        # Análisis de estacionalidad
        seasonality_analysis = self._analyze_channel_seasonality()
        
        channel_results = {
            'channel_analysis': channel_analysis.to_dict('records'),
            'efficiency_analysis': efficiency_analysis,
            'trend_analysis': trend_analysis,
            'seasonality_analysis': seasonality_analysis,
            'total_leads': channel_analysis['leads'].sum(),
            'total_conversions': channel_analysis['conversions'].sum(),
            'total_cost': channel_analysis['cost'].sum(),
            'overall_conversion_rate': (channel_analysis['conversions'].sum() / channel_analysis['leads'].sum()) * 100
        }
        
        self.channel_analysis = channel_results
        return channel_results
    
    def _analyze_channel_efficiency(self, channel_analysis):
        """Analizar eficiencia de canales"""
        efficiency_metrics = {}
        
        for _, channel in channel_analysis.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Conversion rate (30% del score)
            conversion_rate = channel['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 30
            elif conversion_rate > 3:
                efficiency_score += 20
            elif conversion_rate > 1:
                efficiency_score += 10
            
            # ROI (25% del score)
            roi = channel['roi']
            if roi > 3:
                efficiency_score += 25
            elif roi > 2:
                efficiency_score += 20
            elif roi > 1:
                efficiency_score += 15
            else:
                efficiency_score += 5
            
            # Cost per acquisition (20% del score)
            cpa = channel['cost_per_acquisition']
            if cpa < 50:
                efficiency_score += 20
            elif cpa < 100:
                efficiency_score += 15
            elif cpa < 200:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # Lifetime value (15% del score)
            ltv = channel['lifetime_value']
            if ltv > 1000:
                efficiency_score += 15
            elif ltv > 500:
                efficiency_score += 10
            elif ltv > 200:
                efficiency_score += 5
            
            # Volume (10% del score)
            leads = channel['leads']
            if leads > 1000:
                efficiency_score += 10
            elif leads > 500:
                efficiency_score += 7
            elif leads > 100:
                efficiency_score += 5
            
            efficiency_metrics[channel['acquisition_channel']] = {
                'efficiency_score': efficiency_score,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'cost_per_acquisition': cpa,
                'lifetime_value': ltv,
                'lead_volume': leads
            }
        
        # Clasificar canales por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for channel, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(channel)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(channel)
            else:
                efficiency_categories['low_efficiency'].append(channel)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_channel_trends(self):
        """Analizar tendencias de canales"""
        trend_analysis = {}
        
        if 'date' in self.acquisition_data.columns:
            # Análisis de tendencias temporales
            self.acquisition_data['date'] = pd.to_datetime(self.acquisition_data['date'])
            self.acquisition_data['month'] = self.acquisition_data['date'].dt.to_period('M')
            
            # Tendencias por canal
            for channel in self.acquisition_data['acquisition_channel'].unique():
                channel_data = self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]
                
                monthly_trends = channel_data.groupby('month').agg({
                    'leads': 'sum',
                    'conversions': 'sum',
                    'cost': 'sum',
                    'revenue': 'sum'
                }).reset_index()
                
                if len(monthly_trends) > 1:
                    # Calcular tendencias
                    leads_trend = self._calculate_trend(monthly_trends['leads'].values)
                    conversions_trend = self._calculate_trend(monthly_trends['conversions'].values)
                    cost_trend = self._calculate_trend(monthly_trends['cost'].values)
                    revenue_trend = self._calculate_trend(monthly_trends['revenue'].values)
                    
                    trend_analysis[channel] = {
                        'leads_trend': leads_trend,
                        'conversions_trend': conversions_trend,
                        'cost_trend': cost_trend,
                        'revenue_trend': revenue_trend
                    }
        
        return trend_analysis
    
    def _analyze_channel_seasonality(self):
        """Analizar estacionalidad de canales"""
        seasonality_analysis = {}
        
        if 'date' in self.acquisition_data.columns:
            # Análisis de estacionalidad por mes
            self.acquisition_data['month'] = pd.to_datetime(self.acquisition_data['date']).dt.month
            
            monthly_seasonality = self.acquisition_data.groupby('month').agg({
                'leads': 'mean',
                'conversions': 'mean',
                'cost': 'mean',
                'revenue': 'mean'
            }).reset_index()
            
            # Calcular coeficiente de variación estacional
            seasonal_variance = monthly_seasonality['leads'].std() / monthly_seasonality['leads'].mean()
            
            seasonality_analysis = {
                'monthly_seasonality': monthly_seasonality.to_dict('records'),
                'seasonal_variance': seasonal_variance,
                'seasonality_strength': 'high' if seasonal_variance > 0.3 else 'medium' if seasonal_variance > 0.1 else 'low'
            }
        
        return seasonality_analysis
    
    def _calculate_trend(self, values):
        """Calcular tendencia de una serie de valores"""
        if len(values) < 2:
            return {'direction': 'stable', 'slope': 0, 'strength': 0}
        
        x = np.arange(len(values))
        y = values
        
        # Regresión lineal
        slope = np.polyfit(x, y, 1)[0]
        correlation = np.corrcoef(x, y)[0, 1]
        
        if slope > 0:
            direction = 'increasing'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': abs(correlation)
        }
    
    def build_acquisition_prediction_model(self, target_variable='conversions'):
        """Construir modelo de predicción de adquisición"""
        if target_variable not in self.acquisition_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.acquisition_data.columns if col != target_variable and col not in ['date', 'acquisition_channel']]
        X = self.acquisition_data[feature_columns]
        y = self.acquisition_data[target_variable]
        
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
        self.acquisition_models['acquisition_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def optimize_acquisition_costs(self, total_budget, optimization_goal='conversions'):
        """Optimizar costos de adquisición"""
        if 'acquisition_predictor' not in self.acquisition_models:
            raise ValueError("Modelo de predicción de adquisición no encontrado")
        
        model_info = self.acquisition_models['acquisition_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        label_encoders = model_info['label_encoders']
        scaler = model_info['scaler']
        
        # Obtener canales únicos
        channels = self.acquisition_data['acquisition_channel'].unique()
        n_channels = len(channels)
        
        # Función objetivo
        def objective(x):
            # x es el vector de asignación de presupuesto por canal
            total_conversions = 0
            
            for i, channel in enumerate(channels):
                # Crear fila de datos para predicción
                prediction_data = np.zeros(len(feature_columns))
                
                # Asignar presupuesto
                cost_idx = feature_columns.index('cost')
                prediction_data[cost_idx] = x[i]
                
                # Asignar otras variables basadas en datos históricos
                channel_data = self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]
                if len(channel_data) > 0:
                    avg_data = channel_data.mean()
                    
                    if 'leads' in feature_columns:
                        leads_idx = feature_columns.index('leads')
                        prediction_data[leads_idx] = avg_data.get('leads', 0)
                    
                    if 'revenue' in feature_columns:
                        revenue_idx = feature_columns.index('revenue')
                        prediction_data[revenue_idx] = avg_data.get('revenue', 0)
                
                # Escalar datos
                prediction_data_scaled = scaler.transform([prediction_data])
                
                # Predecir conversiones
                predicted_conversions = model.predict(prediction_data_scaled)[0]
                total_conversions += predicted_conversions
            
            if optimization_goal == 'conversions':
                return -total_conversions  # Maximizar conversiones
            elif optimization_goal == 'roi':
                total_cost = sum(x)
                roi = (total_conversions * 100 - total_cost) / total_cost if total_cost > 0 else 0
                return -roi  # Maximizar ROI
            else:
                return -total_conversions
        
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
                'current_budget': self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]['cost'].sum(),
                'current_percentage': (self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]['cost'].sum() / total_budget) * 100
            }
        
        # Calcular impacto esperado
        expected_conversions = -result.fun
        expected_roi = (expected_conversions * 100 - total_budget) / total_budget
        
        optimization_results = {
            'optimal_allocation': optimal_allocation,
            'expected_conversions': expected_conversions,
            'expected_roi': expected_roi,
            'optimization_goal': optimization_goal,
            'total_budget': total_budget,
            'optimization_status': result.success
        }
        
        self.cost_optimization = optimization_results
        return optimization_results
    
    def analyze_acquisition_funnels(self):
        """Analizar funnels de adquisición"""
        if self.acquisition_data.empty:
            return None
        
        # Crear funnels por canal
        funnel_analysis = {}
        
        for channel in self.acquisition_data['acquisition_channel'].unique():
            channel_data = self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]
            
            # Análisis de funnel
            funnel_data = self._create_acquisition_funnel(channel_data)
            funnel_analysis[channel] = funnel_data
        
        # Análisis de funnel general
        general_funnel = self._create_acquisition_funnel(self.acquisition_data)
        
        # Análisis de drop-off points
        drop_off_analysis = self._analyze_acquisition_drop_off()
        
        acquisition_funnels = {
            'channel_funnels': funnel_analysis,
            'general_funnel': general_funnel,
            'drop_off_analysis': drop_off_analysis
        }
        
        self.acquisition_funnels = acquisition_funnels
        return acquisition_funnels
    
    def _create_acquisition_funnel(self, data):
        """Crear funnel de adquisición"""
        # Análisis de funnel
        funnel_steps = {}
        
        # Paso 1: Leads
        total_leads = data['leads'].sum()
        funnel_steps['leads'] = {
            'count': total_leads,
            'conversion_rate': 100.0
        }
        
        # Paso 2: Qualified Leads
        if 'qualified_leads' in data.columns:
            qualified_leads = data['qualified_leads'].sum()
            funnel_steps['qualified_leads'] = {
                'count': qualified_leads,
                'conversion_rate': (qualified_leads / total_leads) * 100 if total_leads > 0 else 0
            }
        else:
            # Estimar qualified leads como 70% de leads
            qualified_leads = total_leads * 0.7
            funnel_steps['qualified_leads'] = {
                'count': qualified_leads,
                'conversion_rate': 70.0
            }
        
        # Paso 3: Conversions
        total_conversions = data['conversions'].sum()
        funnel_steps['conversions'] = {
            'count': total_conversions,
            'conversion_rate': (total_conversions / total_leads) * 100 if total_leads > 0 else 0
        }
        
        # Paso 4: Customers
        total_customers = data['customers'].sum()
        funnel_steps['customers'] = {
            'count': total_customers,
            'conversion_rate': (total_customers / total_leads) * 100 if total_leads > 0 else 0
        }
        
        return {
            'funnel_steps': funnel_steps,
            'total_leads': total_leads,
            'overall_conversion_rate': (total_customers / total_leads) * 100 if total_leads > 0 else 0
        }
    
    def _analyze_acquisition_drop_off(self):
        """Analizar puntos de abandono en adquisición"""
        drop_off_analysis = {}
        
        # Análisis de drop-off por canal
        for channel in self.acquisition_data['acquisition_channel'].unique():
            channel_data = self.acquisition_data[self.acquisition_data['acquisition_channel'] == channel]
            
            leads = channel_data['leads'].sum()
            conversions = channel_data['conversions'].sum()
            customers = channel_data['customers'].sum()
            
            # Calcular drop-off rates
            lead_to_conversion_drop_off = ((leads - conversions) / leads) * 100 if leads > 0 else 0
            conversion_to_customer_drop_off = ((conversions - customers) / conversions) * 100 if conversions > 0 else 0
            
            drop_off_analysis[channel] = {
                'lead_to_conversion_drop_off': lead_to_conversion_drop_off,
                'conversion_to_customer_drop_off': conversion_to_customer_drop_off,
                'total_drop_off': ((leads - customers) / leads) * 100 if leads > 0 else 0
            }
        
        return drop_off_analysis
    
    def generate_acquisition_strategies(self):
        """Generar estrategias de adquisición"""
        strategies = []
        
        # Estrategias basadas en análisis de canales
        if self.channel_analysis:
            efficiency_analysis = self.channel_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            # Estrategias para canales de alta eficiencia
            high_efficiency_channels = efficiency_categories.get('high_efficiency', [])
            if high_efficiency_channels:
                strategies.append({
                    'strategy_type': 'Scale High Efficiency Channels',
                    'description': f'Escalar canales de alta eficiencia: {", ".join(high_efficiency_channels)}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias para canales de baja eficiencia
            low_efficiency_channels = efficiency_categories.get('low_efficiency', [])
            if low_efficiency_channels:
                strategies.append({
                    'strategy_type': 'Optimize Low Efficiency Channels',
                    'description': f'Optimizar canales de baja eficiencia: {", ".join(low_efficiency_channels)}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de funnels
        if self.acquisition_funnels:
            drop_off_analysis = self.acquisition_funnels.get('drop_off_analysis', {})
            
            # Identificar canales con alto drop-off
            high_drop_off_channels = []
            for channel, data in drop_off_analysis.items():
                if data.get('total_drop_off', 0) > 80:  # Más del 80% de drop-off
                    high_drop_off_channels.append(channel)
            
            if high_drop_off_channels:
                strategies.append({
                    'strategy_type': 'Reduce Drop-off',
                    'description': f'Reducir drop-off en canales: {", ".join(high_drop_off_channels)}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en optimización de costos
        if self.cost_optimization:
            optimization_results = self.cost_optimization
            if optimization_results['optimization_status']:
                expected_roi = optimization_results.get('expected_roi', 0)
                strategies.append({
                    'strategy_type': 'Budget Optimization',
                    'description': f'Implementar optimización de presupuesto para ROI esperado de {expected_roi:.1%}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en tendencias
        if self.channel_analysis:
            trend_analysis = self.channel_analysis.get('trend_analysis', {})
            
            # Identificar canales con tendencias crecientes
            growing_channels = []
            for channel, trends in trend_analysis.items():
                leads_trend = trends.get('leads_trend', {})
                if leads_trend.get('direction') == 'increasing' and leads_trend.get('strength', 0) > 0.5:
                    growing_channels.append(channel)
            
            if growing_channels:
                strategies.append({
                    'strategy_type': 'Capitalize on Growing Channels',
                    'description': f'Aprovechar canales en crecimiento: {", ".join(growing_channels)}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_acquisition_insights(self):
        """Generar insights de adquisición"""
        insights = []
        
        # Insights de canales
        if self.channel_analysis:
            overall_conversion_rate = self.channel_analysis.get('overall_conversion_rate', 0)
            
            if overall_conversion_rate < 2:
                insights.append({
                    'category': 'Conversion Rate',
                    'insight': f'Tasa de conversión general baja: {overall_conversion_rate:.1f}%',
                    'recommendation': 'Mejorar tasa de conversión en todos los canales',
                    'priority': 'high'
                })
            
            efficiency_analysis = self.channel_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            low_efficiency_count = len(efficiency_categories.get('low_efficiency', []))
            if low_efficiency_count > 0:
                insights.append({
                    'category': 'Channel Efficiency',
                    'insight': f'{low_efficiency_count} canales con baja eficiencia',
                    'recommendation': 'Optimizar canales de baja eficiencia',
                    'priority': 'medium'
                })
        
        # Insights de funnels
        if self.acquisition_funnels:
            general_funnel = self.acquisition_funnels.get('general_funnel', {})
            overall_conversion_rate = general_funnel.get('overall_conversion_rate', 0)
            
            if overall_conversion_rate < 5:
                insights.append({
                    'category': 'Funnel Performance',
                    'insight': f'Conversión general del funnel baja: {overall_conversion_rate:.1f}%',
                    'recommendation': 'Optimizar funnel de adquisición',
                    'priority': 'high'
                })
        
        # Insights de optimización
        if self.cost_optimization:
            optimization_results = self.cost_optimization
            if optimization_results['optimization_status']:
                expected_roi = optimization_results.get('expected_roi', 0)
                insights.append({
                    'category': 'Cost Optimization',
                    'insight': f'ROI esperado con optimización: {expected_roi:.1%}',
                    'recommendation': 'Implementar nueva asignación de presupuesto',
                    'priority': 'high'
                })
        
        # Insights de tendencias
        if self.channel_analysis:
            trend_analysis = self.channel_analysis.get('trend_analysis', {})
            
            # Analizar tendencias de costos
            increasing_cost_channels = []
            for channel, trends in trend_analysis.items():
                cost_trend = trends.get('cost_trend', {})
                if cost_trend.get('direction') == 'increasing' and cost_trend.get('strength', 0) > 0.5:
                    increasing_cost_channels.append(channel)
            
            if increasing_cost_channels:
                insights.append({
                    'category': 'Cost Trends',
                    'insight': f'Costos crecientes en canales: {", ".join(increasing_cost_channels)}',
                    'recommendation': 'Revisar estrategia de costos en estos canales',
                    'priority': 'medium'
                })
        
        self.acquisition_insights = insights
        return insights
    
    def create_acquisition_dashboard(self):
        """Crear dashboard de optimización de adquisición"""
        if not self.acquisition_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Performance', 'Acquisition Funnel',
                          'Cost Optimization', 'Channel Trends'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Gráfico de performance de canales
        if self.channel_analysis:
            channel_analysis = self.channel_analysis.get('channel_analysis', [])
            if channel_analysis:
                channels = [channel['acquisition_channel'] for channel in channel_analysis]
                conversion_rates = [channel['conversion_rate'] for channel in channel_analysis]
                
                fig.add_trace(
                    go.Bar(x=channels, y=conversion_rates, name='Channel Conversion Rate'),
                    row=1, col=1
                )
        
        # Gráfico de funnel de adquisición
        if self.acquisition_funnels:
            general_funnel = self.acquisition_funnels.get('general_funnel', {})
            funnel_steps = general_funnel.get('funnel_steps', {})
            
            if funnel_steps:
                steps = list(funnel_steps.keys())
                conversion_rates = [funnel_steps[step]['conversion_rate'] for step in steps]
                
                fig.add_trace(
                    go.Bar(x=steps, y=conversion_rates, name='Acquisition Funnel'),
                    row=1, col=2
                )
        
        # Gráfico de optimización de costos
        if self.cost_optimization:
            cost_opt = self.cost_optimization.get('optimal_allocation', {})
            if cost_opt:
                channels = list(cost_opt.keys())
                allocations = [cost_opt[channel]['allocation_percentage'] for channel in channels]
                
                fig.add_trace(
                    go.Pie(labels=channels, values=allocations, name='Cost Optimization'),
                    row=2, col=1
                )
        
        # Gráfico de tendencias de canales
        if self.channel_analysis:
            trend_analysis = self.channel_analysis.get('trend_analysis', {})
            
            # Simular datos de tendencias
            channels = list(trend_analysis.keys())
            trend_scores = [np.random.uniform(-1, 1) for _ in channels]
            
            fig.add_trace(
                go.Scatter(x=channels, y=trend_scores, mode='markers', name='Channel Trends'),
                row=2, col=2
            )
        
        fig.update_layout(
            title="Dashboard de Optimización de Customer Acquisition",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_acquisition_analysis(self, filename='customer_acquisition_optimization_analysis.json'):
        """Exportar análisis de customer acquisition"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'channel_analysis': self.channel_analysis,
            'acquisition_models': {k: {'metrics': v['metrics']} for k, v in self.acquisition_models.items()},
            'cost_optimization': self.cost_optimization,
            'acquisition_funnels': self.acquisition_funnels,
            'optimization_strategies': self.optimization_strategies,
            'acquisition_insights': self.acquisition_insights,
            'summary': {
                'total_channels': len(self.acquisition_data['acquisition_channel'].unique()) if 'acquisition_channel' in self.acquisition_data.columns else 0,
                'total_leads': self.acquisition_data['leads'].sum() if 'leads' in self.acquisition_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de customer acquisition exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de customer acquisition
    acquisition_optimizer = CustomerAcquisitionOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'acquisition_channel': np.random.choice(['Google Ads', 'Facebook', 'Instagram', 'Email', 'SMS', 'Website'], 1000),
        'leads': np.random.poisson(100, 1000),
        'qualified_leads': np.random.poisson(70, 1000),
        'conversions': np.random.poisson(20, 1000),
        'customers': np.random.poisson(15, 1000),
        'cost': np.random.normal(1000, 200, 1000),
        'revenue': np.random.normal(5000, 1000, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de customer acquisition
    print("📊 Cargando datos de customer acquisition...")
    acquisition_optimizer.load_acquisition_data(sample_data)
    
    # Analizar canales de adquisición
    print("📈 Analizando canales de adquisición...")
    channel_analysis = acquisition_optimizer.analyze_acquisition_channels()
    
    # Construir modelo de predicción de adquisición
    print("🔮 Construyendo modelo de predicción de adquisición...")
    acquisition_model = acquisition_optimizer.build_acquisition_prediction_model()
    
    # Optimizar costos de adquisición
    print("💰 Optimizando costos de adquisición...")
    cost_optimization = acquisition_optimizer.optimize_acquisition_costs(100000, 'conversions')
    
    # Analizar funnels de adquisición
    print("🔄 Analizando funnels de adquisición...")
    acquisition_funnels = acquisition_optimizer.analyze_acquisition_funnels()
    
    # Generar estrategias de adquisición
    print("🎯 Generando estrategias de adquisición...")
    acquisition_strategies = acquisition_optimizer.generate_acquisition_strategies()
    
    # Generar insights de adquisición
    print("💡 Generando insights de adquisición...")
    acquisition_insights = acquisition_optimizer.generate_acquisition_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de customer acquisition...")
    dashboard = acquisition_optimizer.create_acquisition_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de customer acquisition...")
    export_data = acquisition_optimizer.export_acquisition_analysis()
    
    print("✅ Sistema de optimización de customer acquisition completado!")






