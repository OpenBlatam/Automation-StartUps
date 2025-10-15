"""
Marketing Brain Marketing Automation Optimizer
Motor avanzado de optimización de marketing automation
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

class MarketingAutomationOptimizer:
    def __init__(self):
        self.automation_data = {}
        self.workflow_analysis = {}
        self.trigger_analysis = {}
        self.performance_analysis = {}
        self.automation_models = {}
        self.optimization_strategies = {}
        self.automation_insights = {}
        
    def load_automation_data(self, automation_data):
        """Cargar datos de marketing automation"""
        if isinstance(automation_data, str):
            if automation_data.endswith('.csv'):
                self.automation_data = pd.read_csv(automation_data)
            elif automation_data.endswith('.json'):
                with open(automation_data, 'r') as f:
                    data = json.load(f)
                self.automation_data = pd.DataFrame(data)
        else:
            self.automation_data = pd.DataFrame(automation_data)
        
        print(f"✅ Datos de marketing automation cargados: {len(self.automation_data)} registros")
        return True
    
    def analyze_automation_workflows(self):
        """Analizar workflows de automation"""
        if self.automation_data.empty:
            return None
        
        # Análisis de workflows por performance
        workflow_analysis = self.automation_data.groupby('workflow_id').agg({
            'triggered': 'sum',
            'completed': 'sum',
            'converted': 'sum',
            'revenue': 'sum',
            'cost': 'sum',
            'duration_hours': 'mean'
        }).reset_index()
        
        # Calcular métricas de performance
        workflow_analysis['completion_rate'] = (workflow_analysis['completed'] / workflow_analysis['triggered']) * 100
        workflow_analysis['conversion_rate'] = (workflow_analysis['converted'] / workflow_analysis['completed']) * 100
        workflow_analysis['roi'] = (workflow_analysis['revenue'] - workflow_analysis['cost']) / workflow_analysis['cost']
        workflow_analysis['revenue_per_trigger'] = workflow_analysis['revenue'] / workflow_analysis['triggered']
        workflow_analysis['cost_per_trigger'] = workflow_analysis['cost'] / workflow_analysis['triggered']
        
        # Análisis de eficiencia
        efficiency_analysis = self._analyze_workflow_efficiency(workflow_analysis)
        
        # Análisis de tendencias
        trend_analysis = self._analyze_workflow_trends()
        
        # Análisis de tipos de workflow
        type_analysis = self._analyze_workflow_types()
        
        workflow_results = {
            'workflow_analysis': workflow_analysis.to_dict('records'),
            'efficiency_analysis': efficiency_analysis,
            'trend_analysis': trend_analysis,
            'type_analysis': type_analysis,
            'total_triggered': workflow_analysis['triggered'].sum(),
            'total_revenue': workflow_analysis['revenue'].sum(),
            'overall_completion_rate': (workflow_analysis['completed'].sum() / workflow_analysis['triggered'].sum()) * 100,
            'overall_conversion_rate': (workflow_analysis['converted'].sum() / workflow_analysis['completed'].sum()) * 100
        }
        
        self.workflow_analysis = workflow_results
        return workflow_results
    
    def _analyze_workflow_efficiency(self, workflow_analysis):
        """Analizar eficiencia de workflows"""
        efficiency_metrics = {}
        
        for _, workflow in workflow_analysis.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Completion rate (30% del score)
            completion_rate = workflow['completion_rate']
            if completion_rate > 80:
                efficiency_score += 30
            elif completion_rate > 70:
                efficiency_score += 25
            elif completion_rate > 60:
                efficiency_score += 20
            else:
                efficiency_score += 10
            
            # Conversion rate (25% del score)
            conversion_rate = workflow['conversion_rate']
            if conversion_rate > 15:
                efficiency_score += 25
            elif conversion_rate > 10:
                efficiency_score += 20
            elif conversion_rate > 5:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
            # ROI (20% del score)
            roi = workflow['roi']
            if roi > 3:
                efficiency_score += 20
            elif roi > 2:
                efficiency_score += 15
            elif roi > 1:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # Duration (15% del score)
            duration = workflow['duration_hours']
            if duration < 24:
                efficiency_score += 15
            elif duration < 48:
                efficiency_score += 10
            elif duration < 72:
                efficiency_score += 5
            
            # Volume (10% del score)
            triggered = workflow['triggered']
            if triggered > 1000:
                efficiency_score += 10
            elif triggered > 500:
                efficiency_score += 7
            elif triggered > 100:
                efficiency_score += 5
            
            efficiency_metrics[workflow['workflow_id']] = {
                'efficiency_score': efficiency_score,
                'completion_rate': completion_rate,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'duration_hours': duration,
                'triggered_count': triggered
            }
        
        # Clasificar workflows por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for workflow_id, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(workflow_id)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(workflow_id)
            else:
                efficiency_categories['low_efficiency'].append(workflow_id)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_workflow_trends(self):
        """Analizar tendencias de workflows"""
        trend_analysis = {}
        
        if 'trigger_date' in self.automation_data.columns:
            # Análisis de tendencias temporales
            self.automation_data['trigger_date'] = pd.to_datetime(self.automation_data['trigger_date'])
            self.automation_data['month'] = self.automation_data['trigger_date'].dt.to_period('M')
            
            # Tendencias mensuales
            monthly_trends = self.automation_data.groupby('month').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas mensuales
            monthly_trends['completion_rate'] = (monthly_trends['completed'] / monthly_trends['triggered']) * 100
            monthly_trends['conversion_rate'] = (monthly_trends['converted'] / monthly_trends['completed']) * 100
            
            trend_analysis['monthly_trends'] = monthly_trends.to_dict('records')
            
            # Análisis de tendencias por tipo de workflow
            if 'workflow_type' in self.automation_data.columns:
                type_trends = self.automation_data.groupby(['month', 'workflow_type']).agg({
                    'completion_rate': 'mean',
                    'conversion_rate': 'mean',
                    'revenue': 'sum'
                }).reset_index()
                
                trend_analysis['type_trends'] = type_trends.to_dict('records')
        
        return trend_analysis
    
    def _analyze_workflow_types(self):
        """Analizar tipos de workflows"""
        type_analysis = {}
        
        if 'workflow_type' in self.automation_data.columns:
            # Análisis por tipo de workflow
            type_performance = self.automation_data.groupby('workflow_type').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'duration_hours': 'mean'
            }).reset_index()
            
            # Calcular métricas por tipo
            type_performance['completion_rate'] = (type_performance['completed'] / type_performance['triggered']) * 100
            type_performance['conversion_rate'] = (type_performance['converted'] / type_performance['completed']) * 100
            type_performance['roi'] = (type_performance['revenue'] - type_performance['cost']) / type_performance['cost']
            type_performance['revenue_per_trigger'] = type_performance['revenue'] / type_performance['triggered']
            
            type_analysis['type_performance'] = type_performance.to_dict('records')
        
        return type_analysis
    
    def analyze_automation_triggers(self):
        """Analizar triggers de automation"""
        if self.automation_data.empty:
            return None
        
        # Análisis de triggers
        trigger_analysis = {}
        
        # Análisis por tipo de trigger
        if 'trigger_type' in self.automation_data.columns:
            trigger_type_analysis = self.automation_data.groupby('trigger_type').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            trigger_type_analysis['completion_rate'] = (trigger_type_analysis['completed'] / trigger_type_analysis['triggered']) * 100
            trigger_type_analysis['conversion_rate'] = (trigger_type_analysis['converted'] / trigger_type_analysis['completed']) * 100
            trigger_type_analysis['revenue_per_trigger'] = trigger_type_analysis['revenue'] / trigger_type_analysis['triggered']
            
            trigger_analysis['trigger_type_analysis'] = trigger_type_analysis.to_dict('records')
        
        # Análisis por fuente de trigger
        if 'trigger_source' in self.automation_data.columns:
            source_analysis = self.automation_data.groupby('trigger_source').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            source_analysis['completion_rate'] = (source_analysis['completed'] / source_analysis['triggered']) * 100
            source_analysis['conversion_rate'] = (source_analysis['converted'] / source_analysis['completed']) * 100
            source_analysis['revenue_per_trigger'] = source_analysis['revenue'] / source_analysis['triggered']
            
            trigger_analysis['source_analysis'] = source_analysis.to_dict('records')
        
        # Análisis de timing de triggers
        timing_analysis = self._analyze_trigger_timing()
        trigger_analysis['timing_analysis'] = timing_analysis
        
        # Análisis de frecuencia de triggers
        frequency_analysis = self._analyze_trigger_frequency()
        trigger_analysis['frequency_analysis'] = frequency_analysis
        
        self.trigger_analysis = trigger_analysis
        return trigger_analysis
    
    def _analyze_trigger_timing(self):
        """Analizar timing de triggers"""
        timing_analysis = {}
        
        if 'trigger_date' in self.automation_data.columns:
            # Análisis de timing por día de la semana
            self.automation_data['trigger_date'] = pd.to_datetime(self.automation_data['trigger_date'])
            self.automation_data['day_of_week'] = self.automation_data['trigger_date'].dt.day_name()
            
            daily_timing = self.automation_data.groupby('day_of_week').agg({
                'completion_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            # Análisis de timing por hora del día
            self.automation_data['hour'] = self.automation_data['trigger_date'].dt.hour
            
            hourly_timing = self.automation_data.groupby('hour').agg({
                'completion_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            timing_analysis = {
                'daily_timing': daily_timing.to_dict('records'),
                'hourly_timing': hourly_timing.to_dict('records'),
                'best_day': daily_timing.loc[daily_timing['completion_rate'].idxmax(), 'day_of_week'],
                'best_hour': hourly_timing.loc[hourly_timing['completion_rate'].idxmax(), 'hour']
            }
        
        return timing_analysis
    
    def _analyze_trigger_frequency(self):
        """Analizar frecuencia de triggers"""
        frequency_analysis = {}
        
        if 'trigger_date' in self.automation_data.columns and 'workflow_id' in self.automation_data.columns:
            # Análisis de frecuencia por workflow
            workflow_frequency = self.automation_data.groupby('workflow_id').agg({
                'triggered': 'count',
                'trigger_date': ['min', 'max']
            }).reset_index()
            
            # Calcular frecuencia diaria
            workflow_frequency['duration_days'] = (workflow_frequency[('trigger_date', 'max')] - workflow_frequency[('trigger_date', 'min')]).dt.days
            workflow_frequency['frequency_per_day'] = workflow_frequency[('triggered', 'count')] / workflow_frequency['duration_days']
            
            frequency_analysis = {
                'workflow_frequency': workflow_frequency.to_dict('records'),
                'avg_frequency_per_day': workflow_frequency['frequency_per_day'].mean(),
                'most_frequent_workflow': workflow_frequency.loc[workflow_frequency['frequency_per_day'].idxmax(), 'workflow_id']
            }
        
        return frequency_analysis
    
    def analyze_automation_performance(self):
        """Analizar performance de automation"""
        if self.automation_data.empty:
            return None
        
        # Análisis de performance
        performance_analysis = {}
        
        # Análisis de performance por segmento
        if 'audience_segment' in self.automation_data.columns:
            segment_performance = self.automation_data.groupby('audience_segment').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            segment_performance['completion_rate'] = (segment_performance['completed'] / segment_performance['triggered']) * 100
            segment_performance['conversion_rate'] = (segment_performance['converted'] / segment_performance['completed']) * 100
            segment_performance['roi'] = (segment_performance['revenue'] - segment_performance['cost']) / segment_performance['cost']
            segment_performance['revenue_per_trigger'] = segment_performance['revenue'] / segment_performance['triggered']
            
            performance_analysis['segment_performance'] = segment_performance.to_dict('records')
        
        # Análisis de performance por canal
        if 'channel' in self.automation_data.columns:
            channel_performance = self.automation_data.groupby('channel').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_performance['completion_rate'] = (channel_performance['completed'] / channel_performance['triggered']) * 100
            channel_performance['conversion_rate'] = (channel_performance['converted'] / channel_performance['completed']) * 100
            channel_performance['roi'] = (channel_performance['revenue'] - channel_performance['cost']) / channel_performance['cost']
            channel_performance['revenue_per_trigger'] = channel_performance['revenue'] / channel_performance['triggered']
            
            performance_analysis['channel_performance'] = channel_performance.to_dict('records')
        
        # Análisis de performance por contenido
        if 'content_type' in self.automation_data.columns:
            content_performance = self.automation_data.groupby('content_type').agg({
                'triggered': 'sum',
                'completed': 'sum',
                'converted': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            content_performance['completion_rate'] = (content_performance['completed'] / content_performance['triggered']) * 100
            content_performance['conversion_rate'] = (content_performance['converted'] / content_performance['completed']) * 100
            content_performance['roi'] = (content_performance['revenue'] - content_performance['cost']) / content_performance['cost']
            content_performance['revenue_per_trigger'] = content_performance['revenue'] / content_performance['triggered']
            
            performance_analysis['content_performance'] = content_performance.to_dict('records')
        
        # Análisis de performance por timing
        if 'trigger_date' in self.automation_data.columns:
            timing_performance = self._analyze_performance_timing()
            performance_analysis['timing_performance'] = timing_performance
        
        self.performance_analysis = performance_analysis
        return performance_analysis
    
    def _analyze_performance_timing(self):
        """Analizar performance por timing"""
        timing_performance = {}
        
        if 'trigger_date' in self.automation_data.columns:
            # Análisis de performance por día de la semana
            self.automation_data['trigger_date'] = pd.to_datetime(self.automation_data['trigger_date'])
            self.automation_data['day_of_week'] = self.automation_data['trigger_date'].dt.day_name()
            
            daily_performance = self.automation_data.groupby('day_of_week').agg({
                'completion_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Análisis de performance por hora del día
            self.automation_data['hour'] = self.automation_data['trigger_date'].dt.hour
            
            hourly_performance = self.automation_data.groupby('hour').agg({
                'completion_rate': 'mean',
                'conversion_rate': 'mean',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            timing_performance = {
                'daily_performance': daily_performance.to_dict('records'),
                'hourly_performance': hourly_performance.to_dict('records'),
                'best_performance_day': daily_performance.loc[daily_performance['completion_rate'].idxmax(), 'day_of_week'],
                'best_performance_hour': hourly_performance.loc[hourly_performance['completion_rate'].idxmax(), 'hour']
            }
        
        return timing_performance
    
    def build_automation_prediction_model(self, target_variable='completion_rate'):
        """Construir modelo de predicción de automation"""
        if target_variable not in self.automation_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.automation_data.columns if col != target_variable and col not in ['trigger_date', 'workflow_id']]
        X = self.automation_data[feature_columns]
        y = self.automation_data[target_variable]
        
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
        self.automation_models['automation_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_automation_strategies(self):
        """Generar estrategias de marketing automation"""
        strategies = []
        
        # Estrategias basadas en análisis de workflows
        if self.workflow_analysis:
            efficiency_analysis = self.workflow_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            # Estrategias para workflows de alta eficiencia
            high_efficiency_workflows = efficiency_categories.get('high_efficiency', [])
            if high_efficiency_workflows:
                strategies.append({
                    'strategy_type': 'Scale High Efficiency Workflows',
                    'description': f'Escalar workflows de alta eficiencia: {len(high_efficiency_workflows)} workflows',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias para workflows de baja eficiencia
            low_efficiency_workflows = efficiency_categories.get('low_efficiency', [])
            if low_efficiency_workflows:
                strategies.append({
                    'strategy_type': 'Optimize Low Efficiency Workflows',
                    'description': f'Optimizar workflows de baja eficiencia: {len(low_efficiency_workflows)} workflows',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de triggers
        if self.trigger_analysis:
            trigger_type_analysis = self.trigger_analysis.get('trigger_type_analysis', [])
            
            if trigger_type_analysis:
                # Identificar tipo de trigger más efectivo
                best_trigger_type = max(trigger_type_analysis, key=lambda x: x['completion_rate'])
                strategies.append({
                    'strategy_type': 'Trigger Optimization',
                    'description': f'Aumentar triggers de tipo: {best_trigger_type["trigger_type"]}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
            
            # Estrategias basadas en timing
            timing_analysis = self.trigger_analysis.get('timing_analysis', {})
            if timing_analysis:
                best_day = timing_analysis.get('best_day')
                best_hour = timing_analysis.get('best_hour')
                
                if best_day and best_hour:
                    strategies.append({
                        'strategy_type': 'Timing Optimization',
                        'description': f'Programar triggers en {best_day} a las {best_hour}:00 para máximo engagement',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
        
        # Estrategias basadas en análisis de performance
        if self.performance_analysis:
            segment_performance = self.performance_analysis.get('segment_performance', [])
            
            if segment_performance:
                # Identificar segmento con mejor performance
                best_segment = max(segment_performance, key=lambda x: x['completion_rate'])
                strategies.append({
                    'strategy_type': 'Segment Optimization',
                    'description': f'Enfocar en segmento: {best_segment["audience_segment"]} para máximo performance',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias basadas en canales
            channel_performance = self.performance_analysis.get('channel_performance', [])
            if channel_performance:
                best_channel = max(channel_performance, key=lambda x: x['completion_rate'])
                strategies.append({
                    'strategy_type': 'Channel Optimization',
                    'description': f'Focalizar en canal: {best_channel["channel"]} para máximo performance',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en contenido
        if self.performance_analysis:
            content_performance = self.performance_analysis.get('content_performance', [])
            if content_performance:
                best_content = max(content_performance, key=lambda x: x['completion_rate'])
                strategies.append({
                    'strategy_type': 'Content Optimization',
                    'description': f'Aumentar contenido de tipo: {best_content["content_type"]}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_automation_insights(self):
        """Generar insights de marketing automation"""
        insights = []
        
        # Insights de workflows
        if self.workflow_analysis:
            overall_completion_rate = self.workflow_analysis.get('overall_completion_rate', 0)
            
            if overall_completion_rate < 70:
                insights.append({
                    'category': 'Workflow Performance',
                    'insight': f'Completion rate general bajo: {overall_completion_rate:.1f}%',
                    'recommendation': 'Mejorar completion rate en todos los workflows',
                    'priority': 'high'
                })
            
            overall_conversion_rate = self.workflow_analysis.get('overall_conversion_rate', 0)
            if overall_conversion_rate < 10:
                insights.append({
                    'category': 'Workflow Performance',
                    'insight': f'Conversion rate general bajo: {overall_conversion_rate:.1f}%',
                    'recommendation': 'Mejorar conversion rate en todos los workflows',
                    'priority': 'high'
                })
        
        # Insights de triggers
        if self.trigger_analysis:
            trigger_type_analysis = self.trigger_analysis.get('trigger_type_analysis', [])
            
            if trigger_type_analysis:
                # Identificar tipo de trigger con mejor performance
                best_trigger = max(trigger_type_analysis, key=lambda x: x['completion_rate'])
                insights.append({
                    'category': 'Trigger Performance',
                    'insight': f'Mejor tipo de trigger: {best_trigger["trigger_type"]} con {best_trigger["completion_rate"]:.1f}% completion rate',
                    'recommendation': 'Aumentar uso de este tipo de trigger',
                    'priority': 'medium'
                })
        
        # Insights de performance
        if self.performance_analysis:
            segment_performance = self.performance_analysis.get('segment_performance', [])
            
            if segment_performance:
                # Identificar segmento con mejor performance
                best_segment = max(segment_performance, key=lambda x: x['completion_rate'])
                insights.append({
                    'category': 'Segment Performance',
                    'insight': f'Mejor segmento: {best_segment["audience_segment"]} con {best_segment["completion_rate"]:.1f}% completion rate',
                    'recommendation': 'Enfocar en este segmento para máximo performance',
                    'priority': 'high'
                })
        
        # Insights de timing
        if self.trigger_analysis:
            timing_analysis = self.trigger_analysis.get('timing_analysis', {})
            best_day = timing_analysis.get('best_day')
            best_hour = timing_analysis.get('best_hour')
            
            if best_day and best_hour:
                insights.append({
                    'category': 'Trigger Timing',
                    'insight': f'Mejor momento para triggers: {best_day} a las {best_hour}:00',
                    'recommendation': 'Optimizar horarios de triggers',
                    'priority': 'low'
                })
        
        # Insights de eficiencia
        if self.workflow_analysis:
            efficiency_analysis = self.workflow_analysis.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            low_efficiency_count = len(efficiency_categories.get('low_efficiency', []))
            if low_efficiency_count > 0:
                insights.append({
                    'category': 'Workflow Efficiency',
                    'insight': f'{low_efficiency_count} workflows con baja eficiencia',
                    'recommendation': 'Optimizar workflows de baja eficiencia',
                    'priority': 'medium'
                })
        
        self.automation_insights = insights
        return insights
    
    def create_automation_dashboard(self):
        """Crear dashboard de marketing automation"""
        if not self.automation_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Workflow Performance', 'Trigger Analysis',
                          'Performance by Segment', 'Timing Analysis'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Gráfico de performance de workflows
        if self.workflow_analysis:
            workflow_analysis = self.workflow_analysis.get('workflow_analysis', [])
            if workflow_analysis:
                workflows = [workflow['workflow_id'] for workflow in workflow_analysis]
                completion_rates = [workflow['completion_rate'] for workflow in workflow_analysis]
                
                fig.add_trace(
                    go.Bar(x=workflows, y=completion_rates, name='Workflow Completion Rate'),
                    row=1, col=1
                )
        
        # Gráfico de análisis de triggers
        if self.trigger_analysis:
            trigger_type_analysis = self.trigger_analysis.get('trigger_type_analysis', [])
            if trigger_type_analysis:
                trigger_types = [trigger['trigger_type'] for trigger in trigger_type_analysis]
                triggered_counts = [trigger['triggered'] for trigger in trigger_type_analysis]
                
                fig.add_trace(
                    go.Pie(labels=trigger_types, values=triggered_counts, name='Trigger Types'),
                    row=1, col=2
                )
        
        # Gráfico de performance por segmento
        if self.performance_analysis:
            segment_performance = self.performance_analysis.get('segment_performance', [])
            if segment_performance:
                segments = [segment['audience_segment'] for segment in segment_performance]
                completion_rates = [segment['completion_rate'] for segment in segment_performance]
                
                fig.add_trace(
                    go.Bar(x=segments, y=completion_rates, name='Segment Completion Rate'),
                    row=2, col=1
                )
        
        # Gráfico de análisis de timing
        if self.trigger_analysis:
            timing_analysis = self.trigger_analysis.get('timing_analysis', {})
            hourly_timing = timing_analysis.get('hourly_timing', [])
            
            if hourly_timing:
                hours = [data['hour'] for data in hourly_timing]
                completion_rates = [data['completion_rate'] for data in hourly_timing]
                
                fig.add_trace(
                    go.Scatter(x=hours, y=completion_rates, mode='lines+markers', name='Hourly Completion Rate'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Marketing Automation",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_automation_analysis(self, filename='marketing_automation_analysis.json'):
        """Exportar análisis de marketing automation"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'workflow_analysis': self.workflow_analysis,
            'trigger_analysis': self.trigger_analysis,
            'performance_analysis': self.performance_analysis,
            'automation_models': {k: {'metrics': v['metrics']} for k, v in self.automation_models.items()},
            'optimization_strategies': self.optimization_strategies,
            'automation_insights': self.automation_insights,
            'summary': {
                'total_workflows': len(self.automation_data['workflow_id'].unique()) if 'workflow_id' in self.automation_data.columns else 0,
                'total_triggered': self.automation_data['triggered'].sum() if 'triggered' in self.automation_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de marketing automation exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de marketing automation
    automation_optimizer = MarketingAutomationOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'workflow_id': np.random.randint(1, 20, 1000),
        'triggered': np.random.poisson(100, 1000),
        'completed': np.random.poisson(80, 1000),
        'converted': np.random.poisson(15, 1000),
        'revenue': np.random.normal(500, 100, 1000),
        'cost': np.random.normal(50, 10, 1000),
        'duration_hours': np.random.uniform(1, 72, 1000),
        'completion_rate': np.random.uniform(60, 90, 1000),
        'conversion_rate': np.random.uniform(5, 25, 1000),
        'workflow_type': np.random.choice(['Welcome', 'Nurture', 'Re-engagement', 'Upsell'], 1000),
        'trigger_type': np.random.choice(['Email Open', 'Website Visit', 'Purchase', 'Form Submit'], 1000),
        'trigger_source': np.random.choice(['Website', 'Email', 'Social Media', 'Mobile App'], 1000),
        'audience_segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'channel': np.random.choice(['Email', 'SMS', 'Push', 'In-App'], 1000),
        'content_type': np.random.choice(['Text', 'Image', 'Video', 'Interactive'], 1000),
        'trigger_date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de marketing automation
    print("📊 Cargando datos de marketing automation...")
    automation_optimizer.load_automation_data(sample_data)
    
    # Analizar workflows de automation
    print("🔄 Analizando workflows de automation...")
    workflow_analysis = automation_optimizer.analyze_automation_workflows()
    
    # Analizar triggers de automation
    print("⚡ Analizando triggers de automation...")
    trigger_analysis = automation_optimizer.analyze_automation_triggers()
    
    # Analizar performance de automation
    print("📈 Analizando performance de automation...")
    performance_analysis = automation_optimizer.analyze_automation_performance()
    
    # Construir modelo de predicción de automation
    print("🔮 Construyendo modelo de predicción de automation...")
    automation_model = automation_optimizer.build_automation_prediction_model()
    
    # Generar estrategias de marketing automation
    print("🎯 Generando estrategias de marketing automation...")
    automation_strategies = automation_optimizer.generate_automation_strategies()
    
    # Generar insights de marketing automation
    print("💡 Generando insights de marketing automation...")
    automation_insights = automation_optimizer.generate_automation_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de marketing automation...")
    dashboard = automation_optimizer.create_automation_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de marketing automation...")
    export_data = automation_optimizer.export_automation_analysis()
    
    print("✅ Sistema de optimización de marketing automation completado!")




