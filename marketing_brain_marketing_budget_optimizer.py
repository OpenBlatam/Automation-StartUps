"""
Marketing Brain Marketing Budget Optimizer
Sistema avanzado de optimización de presupuesto de marketing
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
from scipy.optimize import minimize
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class MarketingBudgetOptimizer:
    def __init__(self):
        self.budget_data = {}
        self.budget_analysis = {}
        self.optimization_models = {}
        self.budget_strategies = {}
        self.budget_insights = {}
        self.optimization_results = {}
        
    def load_budget_data(self, budget_data):
        """Cargar datos de presupuesto de marketing"""
        if isinstance(budget_data, str):
            if budget_data.endswith('.csv'):
                self.budget_data = pd.read_csv(budget_data)
            elif budget_data.endswith('.json'):
                with open(budget_data, 'r') as f:
                    data = json.load(f)
                self.budget_data = pd.DataFrame(data)
        else:
            self.budget_data = pd.DataFrame(budget_data)
        
        print(f"✅ Datos de presupuesto de marketing cargados: {len(self.budget_data)} registros")
        return True
    
    def analyze_budget_performance(self):
        """Analizar performance del presupuesto"""
        if self.budget_data.empty:
            return None
        
        # Análisis de performance por canal
        channel_performance = self._analyze_channel_budget_performance()
        
        # Análisis de performance por campaña
        campaign_performance = self._analyze_campaign_budget_performance()
        
        # Análisis de performance por período
        period_performance = self._analyze_period_budget_performance()
        
        # Análisis de performance por segmento
        segment_performance = self._analyze_segment_budget_performance()
        
        # Análisis de eficiencia del presupuesto
        budget_efficiency = self._analyze_budget_efficiency()
        
        performance_results = {
            'channel_performance': channel_performance,
            'campaign_performance': campaign_performance,
            'period_performance': period_performance,
            'segment_performance': segment_performance,
            'budget_efficiency': budget_efficiency,
            'overall_metrics': self._calculate_budget_metrics()
        }
        
        self.budget_analysis = performance_results
        return performance_results
    
    def _analyze_channel_budget_performance(self):
        """Analizar performance del presupuesto por canal"""
        channel_analysis = {}
        
        if 'channel' in self.budget_data.columns:
            channel_performance = self.budget_data.groupby('channel').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_performance['budget_utilization'] = (channel_performance['spent'] / channel_performance['budget']) * 100
            channel_performance['roi'] = (channel_performance['revenue'] - channel_performance['spent']) / channel_performance['spent']
            channel_performance['roas'] = channel_performance['revenue'] / channel_performance['spent']
            channel_performance['cpa'] = channel_performance['spent'] / channel_performance['conversions']
            channel_performance['cpm'] = (channel_performance['spent'] / channel_performance['impressions']) * 1000
            channel_performance['cpc'] = channel_performance['spent'] / channel_performance['clicks']
            channel_performance['conversion_rate'] = (channel_performance['conversions'] / channel_performance['clicks']) * 100
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_channel_budget_efficiency(channel_performance)
            
            channel_analysis = {
                'channel_performance': channel_performance.to_dict('records'),
                'efficiency_analysis': efficiency_analysis
            }
        
        return channel_analysis
    
    def _analyze_channel_budget_efficiency(self, channel_performance):
        """Analizar eficiencia del presupuesto por canal"""
        efficiency_metrics = {}
        
        for _, channel in channel_performance.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Budget utilization (20% del score)
            budget_utilization = channel['budget_utilization']
            if budget_utilization > 90:
                efficiency_score += 20
            elif budget_utilization > 80:
                efficiency_score += 15
            elif budget_utilization > 70:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # ROI (30% del score)
            roi = channel['roi']
            if roi > 3:
                efficiency_score += 30
            elif roi > 2:
                efficiency_score += 25
            elif roi > 1:
                efficiency_score += 20
            else:
                efficiency_score += 10
            
            # ROAS (25% del score)
            roas = channel['roas']
            if roas > 4:
                efficiency_score += 25
            elif roas > 3:
                efficiency_score += 20
            elif roas > 2:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
            # Conversion rate (15% del score)
            conversion_rate = channel['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 15
            elif conversion_rate > 3:
                efficiency_score += 12
            elif conversion_rate > 2:
                efficiency_score += 8
            else:
                efficiency_score += 5
            
            # Volume (10% del score)
            spent = channel['spent']
            if spent > 10000:
                efficiency_score += 10
            elif spent > 5000:
                efficiency_score += 7
            elif spent > 1000:
                efficiency_score += 5
            
            efficiency_metrics[channel['channel']] = {
                'efficiency_score': efficiency_score,
                'budget_utilization': budget_utilization,
                'roi': roi,
                'roas': roas,
                'conversion_rate': conversion_rate,
                'spent': spent
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
    
    def _analyze_campaign_budget_performance(self):
        """Analizar performance del presupuesto por campaña"""
        campaign_analysis = {}
        
        if 'campaign_id' in self.budget_data.columns:
            campaign_performance = self.budget_data.groupby('campaign_id').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            campaign_performance['budget_utilization'] = (campaign_performance['spent'] / campaign_performance['budget']) * 100
            campaign_performance['roi'] = (campaign_performance['revenue'] - campaign_performance['spent']) / campaign_performance['spent']
            campaign_performance['roas'] = campaign_performance['revenue'] / campaign_performance['spent']
            campaign_performance['cpa'] = campaign_performance['spent'] / campaign_performance['conversions']
            campaign_performance['cpm'] = (campaign_performance['spent'] / campaign_performance['impressions']) * 1000
            campaign_performance['cpc'] = campaign_performance['spent'] / campaign_performance['clicks']
            campaign_performance['conversion_rate'] = (campaign_performance['conversions'] / campaign_performance['clicks']) * 100
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_campaign_budget_efficiency(campaign_performance)
            
            campaign_analysis = {
                'campaign_performance': campaign_performance.to_dict('records'),
                'efficiency_analysis': efficiency_analysis
            }
        
        return campaign_analysis
    
    def _analyze_campaign_budget_efficiency(self, campaign_performance):
        """Analizar eficiencia del presupuesto por campaña"""
        efficiency_metrics = {}
        
        for _, campaign in campaign_performance.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # Budget utilization (20% del score)
            budget_utilization = campaign['budget_utilization']
            if budget_utilization > 90:
                efficiency_score += 20
            elif budget_utilization > 80:
                efficiency_score += 15
            elif budget_utilization > 70:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # ROI (30% del score)
            roi = campaign['roi']
            if roi > 3:
                efficiency_score += 30
            elif roi > 2:
                efficiency_score += 25
            elif roi > 1:
                efficiency_score += 20
            else:
                efficiency_score += 10
            
            # ROAS (25% del score)
            roas = campaign['roas']
            if roas > 4:
                efficiency_score += 25
            elif roas > 3:
                efficiency_score += 20
            elif roas > 2:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
            # Conversion rate (15% del score)
            conversion_rate = campaign['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 15
            elif conversion_rate > 3:
                efficiency_score += 12
            elif conversion_rate > 2:
                efficiency_score += 8
            else:
                efficiency_score += 5
            
            # Volume (10% del score)
            spent = campaign['spent']
            if spent > 10000:
                efficiency_score += 10
            elif spent > 5000:
                efficiency_score += 7
            elif spent > 1000:
                efficiency_score += 5
            
            efficiency_metrics[campaign['campaign_id']] = {
                'efficiency_score': efficiency_score,
                'budget_utilization': budget_utilization,
                'roi': roi,
                'roas': roas,
                'conversion_rate': conversion_rate,
                'spent': spent
            }
        
        # Clasificar campañas por eficiencia
        efficiency_categories = {
            'high_efficiency': [],
            'medium_efficiency': [],
            'low_efficiency': []
        }
        
        for campaign, metrics in efficiency_metrics.items():
            score = metrics['efficiency_score']
            if score >= 80:
                efficiency_categories['high_efficiency'].append(campaign)
            elif score >= 60:
                efficiency_categories['medium_efficiency'].append(campaign)
            else:
                efficiency_categories['low_efficiency'].append(campaign)
        
        return {
            'efficiency_metrics': efficiency_metrics,
            'efficiency_categories': efficiency_categories
        }
    
    def _analyze_period_budget_performance(self):
        """Analizar performance del presupuesto por período"""
        period_analysis = {}
        
        if 'date' in self.budget_data.columns:
            # Análisis de performance por mes
            self.budget_data['date'] = pd.to_datetime(self.budget_data['date'])
            self.budget_data['month'] = self.budget_data['date'].dt.to_period('M')
            
            monthly_performance = self.budget_data.groupby('month').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            monthly_performance['budget_utilization'] = (monthly_performance['spent'] / monthly_performance['budget']) * 100
            monthly_performance['roi'] = (monthly_performance['revenue'] - monthly_performance['spent']) / monthly_performance['spent']
            monthly_performance['roas'] = monthly_performance['revenue'] / monthly_performance['spent']
            monthly_performance['cpa'] = monthly_performance['spent'] / monthly_performance['conversions']
            monthly_performance['cpm'] = (monthly_performance['spent'] / monthly_performance['impressions']) * 1000
            monthly_performance['cpc'] = monthly_performance['spent'] / monthly_performance['clicks']
            monthly_performance['conversion_rate'] = (monthly_performance['conversions'] / monthly_performance['clicks']) * 100
            
            # Análisis de performance por trimestre
            self.budget_data['quarter'] = self.budget_data['date'].dt.to_period('Q')
            quarterly_performance = self.budget_data.groupby('quarter').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            quarterly_performance['budget_utilization'] = (quarterly_performance['spent'] / quarterly_performance['budget']) * 100
            quarterly_performance['roi'] = (quarterly_performance['revenue'] - quarterly_performance['spent']) / quarterly_performance['spent']
            quarterly_performance['roas'] = quarterly_performance['revenue'] / quarterly_performance['spent']
            quarterly_performance['cpa'] = quarterly_performance['spent'] / quarterly_performance['conversions']
            quarterly_performance['cpm'] = (quarterly_performance['spent'] / quarterly_performance['impressions']) * 1000
            quarterly_performance['cpc'] = quarterly_performance['spent'] / quarterly_performance['clicks']
            quarterly_performance['conversion_rate'] = (quarterly_performance['conversions'] / quarterly_performance['clicks']) * 100
            
            period_analysis = {
                'monthly_performance': monthly_performance.to_dict('records'),
                'quarterly_performance': quarterly_performance.to_dict('records')
            }
        
        return period_analysis
    
    def _analyze_segment_budget_performance(self):
        """Analizar performance del presupuesto por segmento"""
        segment_analysis = {}
        
        if 'audience_segment' in self.budget_data.columns:
            segment_performance = self.budget_data.groupby('audience_segment').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            segment_performance['budget_utilization'] = (segment_performance['spent'] / segment_performance['budget']) * 100
            segment_performance['roi'] = (segment_performance['revenue'] - segment_performance['spent']) / segment_performance['spent']
            segment_performance['roas'] = segment_performance['revenue'] / segment_performance['spent']
            segment_performance['cpa'] = segment_performance['spent'] / segment_performance['conversions']
            segment_performance['cpm'] = (segment_performance['spent'] / segment_performance['impressions']) * 1000
            segment_performance['cpc'] = segment_performance['spent'] / segment_performance['clicks']
            segment_performance['conversion_rate'] = (segment_performance['conversions'] / segment_performance['clicks']) * 100
            
            segment_analysis = {
                'segment_performance': segment_performance.to_dict('records')
            }
        
        return segment_analysis
    
    def _analyze_budget_efficiency(self):
        """Analizar eficiencia del presupuesto"""
        budget_efficiency = {}
        
        if not self.budget_data.empty:
            # Calcular métricas de eficiencia
            total_budget = self.budget_data['budget'].sum()
            total_spent = self.budget_data['spent'].sum()
            total_revenue = self.budget_data['revenue'].sum()
            total_conversions = self.budget_data['conversions'].sum()
            
            budget_efficiency = {
                'total_budget': total_budget,
                'total_spent': total_spent,
                'total_revenue': total_revenue,
                'total_conversions': total_conversions,
                'budget_utilization': (total_spent / total_budget) * 100,
                'overall_roi': (total_revenue - total_spent) / total_spent,
                'overall_roas': total_revenue / total_spent,
                'overall_cpa': total_spent / total_conversions,
                'budget_efficiency_score': self._calculate_budget_efficiency_score()
            }
        
        return budget_efficiency
    
    def _calculate_budget_efficiency_score(self):
        """Calcular score de eficiencia del presupuesto"""
        if self.budget_data.empty:
            return 0
        
        # Calcular métricas base
        total_budget = self.budget_data['budget'].sum()
        total_spent = self.budget_data['spent'].sum()
        total_revenue = self.budget_data['revenue'].sum()
        total_conversions = self.budget_data['conversions'].sum()
        
        # Calcular score de eficiencia
        efficiency_score = 0
        
        # Budget utilization (25% del score)
        budget_utilization = (total_spent / total_budget) * 100
        if budget_utilization > 90:
            efficiency_score += 25
        elif budget_utilization > 80:
            efficiency_score += 20
        elif budget_utilization > 70:
            efficiency_score += 15
        else:
            efficiency_score += 10
        
        # ROI (35% del score)
        roi = (total_revenue - total_spent) / total_spent
        if roi > 3:
            efficiency_score += 35
        elif roi > 2:
            efficiency_score += 30
        elif roi > 1:
            efficiency_score += 25
        else:
            efficiency_score += 15
        
        # ROAS (25% del score)
        roas = total_revenue / total_spent
        if roas > 4:
            efficiency_score += 25
        elif roas > 3:
            efficiency_score += 20
        elif roas > 2:
            efficiency_score += 15
        else:
            efficiency_score += 10
        
        # Volume (15% del score)
        if total_spent > 100000:
            efficiency_score += 15
        elif total_spent > 50000:
            efficiency_score += 12
        elif total_spent > 10000:
            efficiency_score += 8
        else:
            efficiency_score += 5
        
        return efficiency_score
    
    def _calculate_budget_metrics(self):
        """Calcular métricas generales del presupuesto"""
        budget_metrics = {}
        
        if not self.budget_data.empty:
            budget_metrics = {
                'total_budget': self.budget_data['budget'].sum(),
                'total_spent': self.budget_data['spent'].sum(),
                'total_revenue': self.budget_data['revenue'].sum(),
                'total_conversions': self.budget_data['conversions'].sum(),
                'total_impressions': self.budget_data['impressions'].sum(),
                'total_clicks': self.budget_data['clicks'].sum(),
                'overall_budget_utilization': (self.budget_data['spent'].sum() / self.budget_data['budget'].sum()) * 100,
                'overall_roi': (self.budget_data['revenue'].sum() - self.budget_data['spent'].sum()) / self.budget_data['spent'].sum(),
                'overall_roas': self.budget_data['revenue'].sum() / self.budget_data['spent'].sum(),
                'overall_cpa': self.budget_data['spent'].sum() / self.budget_data['conversions'].sum(),
                'overall_cpm': (self.budget_data['spent'].sum() / self.budget_data['impressions'].sum()) * 1000,
                'overall_cpc': self.budget_data['spent'].sum() / self.budget_data['clicks'].sum(),
                'overall_conversion_rate': (self.budget_data['conversions'].sum() / self.budget_data['clicks'].sum()) * 100
            }
        
        return budget_metrics
    
    def optimize_budget_allocation(self, total_budget, optimization_objective='roi'):
        """Optimizar asignación de presupuesto"""
        if self.budget_data.empty:
            return None
        
        # Preparar datos para optimización
        optimization_data = self._prepare_optimization_data()
        
        # Definir función objetivo
        if optimization_objective == 'roi':
            objective_function = self._roi_objective_function
        elif optimization_objective == 'roas':
            objective_function = self._roas_objective_function
        elif optimization_objective == 'conversions':
            objective_function = self._conversions_objective_function
        else:
            objective_function = self._roi_objective_function
        
        # Definir restricciones
        constraints = self._define_optimization_constraints(total_budget)
        
        # Definir límites
        bounds = self._define_optimization_bounds(optimization_data)
        
        # Punto inicial
        x0 = self._get_initial_budget_allocation(optimization_data, total_budget)
        
        # Optimizar
        result = minimize(
            objective_function,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            args=(optimization_data,)
        )
        
        # Procesar resultados
        optimization_results = self._process_optimization_results(result, optimization_data, total_budget)
        
        self.optimization_results = optimization_results
        return optimization_results
    
    def _prepare_optimization_data(self):
        """Preparar datos para optimización"""
        optimization_data = {}
        
        if 'channel' in self.budget_data.columns:
            # Agrupar por canal
            channel_data = self.budget_data.groupby('channel').agg({
                'budget': 'sum',
                'spent': 'sum',
                'revenue': 'sum',
                'conversions': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_data['roi'] = (channel_data['revenue'] - channel_data['spent']) / channel_data['spent']
            channel_data['roas'] = channel_data['revenue'] / channel_data['spent']
            channel_data['conversion_rate'] = (channel_data['conversions'] / channel_data['clicks']) * 100
            channel_data['cpa'] = channel_data['spent'] / channel_data['conversions']
            
            optimization_data = {
                'channels': channel_data['channel'].tolist(),
                'roi': channel_data['roi'].tolist(),
                'roas': channel_data['roas'].tolist(),
                'conversion_rate': channel_data['conversion_rate'].tolist(),
                'cpa': channel_data['cpa'].tolist(),
                'current_spent': channel_data['spent'].tolist()
            }
        
        return optimization_data
    
    def _roi_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar ROI"""
        # Calcular ROI total
        total_roi = 0
        for i, budget in enumerate(x):
            if budget > 0:
                roi = optimization_data['roi'][i]
                total_roi += budget * roi
        
        # Minimizar el negativo para maximizar ROI
        return -total_roi
    
    def _roas_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar ROAS"""
        # Calcular ROAS total
        total_roas = 0
        for i, budget in enumerate(x):
            if budget > 0:
                roas = optimization_data['roas'][i]
                total_roas += budget * roas
        
        # Minimizar el negativo para maximizar ROAS
        return -total_roas
    
    def _conversions_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar conversiones"""
        # Calcular conversiones totales
        total_conversions = 0
        for i, budget in enumerate(x):
            if budget > 0:
                conversion_rate = optimization_data['conversion_rate'][i]
                cpa = optimization_data['cpa'][i]
                conversions = (budget / cpa) * (conversion_rate / 100)
                total_conversions += conversions
        
        # Minimizar el negativo para maximizar conversiones
        return -total_conversions
    
    def _define_optimization_constraints(self, total_budget):
        """Definir restricciones de optimización"""
        constraints = []
        
        # Restricción de presupuesto total
        constraints.append({
            'type': 'eq',
            'fun': lambda x: sum(x) - total_budget
        })
        
        return constraints
    
    def _define_optimization_bounds(self, optimization_data):
        """Definir límites de optimización"""
        bounds = []
        
        for i in range(len(optimization_data['channels'])):
            # Límite mínimo: 0
            # Límite máximo: 2x del presupuesto actual
            min_budget = 0
            max_budget = optimization_data['current_spent'][i] * 2
            bounds.append((min_budget, max_budget))
        
        return bounds
    
    def _get_initial_budget_allocation(self, optimization_data, total_budget):
        """Obtener asignación inicial de presupuesto"""
        # Usar asignación actual como punto inicial
        current_allocation = optimization_data['current_spent']
        
        # Normalizar para que sume el presupuesto total
        total_current = sum(current_allocation)
        if total_current > 0:
            normalized_allocation = [budget * (total_budget / total_current) for budget in current_allocation]
        else:
            # Distribución equitativa si no hay datos actuales
            normalized_allocation = [total_budget / len(current_allocation)] * len(current_allocation)
        
        return normalized_allocation
    
    def _process_optimization_results(self, result, optimization_data, total_budget):
        """Procesar resultados de optimización"""
        optimized_allocation = result.x
        
        # Crear resultados de optimización
        optimization_results = {
            'total_budget': total_budget,
            'optimization_success': result.success,
            'optimization_message': result.message,
            'optimized_allocation': {},
            'performance_comparison': {},
            'recommendations': []
        }
        
        # Procesar asignación optimizada
        for i, channel in enumerate(optimization_data['channels']):
            current_budget = optimization_data['current_spent'][i]
            optimized_budget = optimized_allocation[i]
            budget_change = optimized_budget - current_budget
            budget_change_percent = (budget_change / current_budget) * 100 if current_budget > 0 else 0
            
            optimization_results['optimized_allocation'][channel] = {
                'current_budget': current_budget,
                'optimized_budget': optimized_budget,
                'budget_change': budget_change,
                'budget_change_percent': budget_change_percent,
                'roi': optimization_data['roi'][i],
                'roas': optimization_data['roas'][i],
                'conversion_rate': optimization_data['conversion_rate'][i],
                'cpa': optimization_data['cpa'][i]
            }
        
        # Calcular comparación de performance
        current_total_roi = sum(optimization_data['current_spent'][i] * optimization_data['roi'][i] for i in range(len(optimization_data['channels'])))
        optimized_total_roi = sum(optimized_allocation[i] * optimization_data['roi'][i] for i in range(len(optimization_data['channels'])))
        
        optimization_results['performance_comparison'] = {
            'current_total_roi': current_total_roi,
            'optimized_total_roi': optimized_total_roi,
            'roi_improvement': optimized_total_roi - current_total_roi,
            'roi_improvement_percent': ((optimized_total_roi - current_total_roi) / current_total_roi) * 100 if current_total_roi > 0 else 0
        }
        
        # Generar recomendaciones
        recommendations = []
        for channel, data in optimization_results['optimized_allocation'].items():
            if data['budget_change_percent'] > 20:
                recommendations.append({
                    'channel': channel,
                    'action': 'increase_budget',
                    'current_budget': data['current_budget'],
                    'recommended_budget': data['optimized_budget'],
                    'reason': f'Alto ROI ({data["roi"]:.2f}) y ROAS ({data["roas"]:.2f})'
                })
            elif data['budget_change_percent'] < -20:
                recommendations.append({
                    'channel': channel,
                    'action': 'decrease_budget',
                    'current_budget': data['current_budget'],
                    'recommended_budget': data['optimized_budget'],
                    'reason': f'Bajo ROI ({data["roi"]:.2f}) y ROAS ({data["roas"]:.2f})'
                })
        
        optimization_results['recommendations'] = recommendations
        
        return optimization_results
    
    def build_budget_prediction_model(self, target_variable='roi'):
        """Construir modelo de predicción de presupuesto"""
        if target_variable not in self.budget_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.budget_data.columns if col != target_variable and col not in ['date', 'campaign_id']]
        X = self.budget_data[feature_columns]
        y = self.budget_data[target_variable]
        
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
        self.optimization_models['budget_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_budget_strategies(self):
        """Generar estrategias de optimización de presupuesto"""
        strategies = []
        
        # Estrategias basadas en análisis de performance
        if self.budget_analysis:
            channel_performance = self.budget_analysis.get('channel_performance', {})
            efficiency_analysis = channel_performance.get('efficiency_analysis', {})
            efficiency_categories = efficiency_analysis.get('efficiency_categories', {})
            
            # Estrategias para canales de alta eficiencia
            high_efficiency_channels = efficiency_categories.get('high_efficiency', [])
            if high_efficiency_channels:
                strategies.append({
                    'strategy_type': 'Scale High Efficiency Channels',
                    'description': f'Escalar canales de alta eficiencia: {len(high_efficiency_channels)} canales',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            # Estrategias para canales de baja eficiencia
            low_efficiency_channels = efficiency_categories.get('low_efficiency', [])
            if low_efficiency_channels:
                strategies.append({
                    'strategy_type': 'Optimize Low Efficiency Channels',
                    'description': f'Optimizar canales de baja eficiencia: {len(low_efficiency_channels)} canales',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de eficiencia del presupuesto
        if self.budget_analysis:
            budget_efficiency = self.budget_analysis.get('budget_efficiency', {})
            budget_utilization = budget_efficiency.get('budget_utilization', 0)
            
            if budget_utilization < 80:
                strategies.append({
                    'strategy_type': 'Improve Budget Utilization',
                    'description': f'Mejorar utilización del presupuesto: {budget_utilization:.1f}%',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
            
            overall_roi = budget_efficiency.get('overall_roi', 0)
            if overall_roi < 2:
                strategies.append({
                    'strategy_type': 'Improve Overall ROI',
                    'description': f'Mejorar ROI general: {overall_roi:.2f}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en resultados de optimización
        if self.optimization_results:
            recommendations = self.optimization_results.get('recommendations', [])
            
            for recommendation in recommendations:
                if recommendation['action'] == 'increase_budget':
                    strategies.append({
                        'strategy_type': 'Increase Channel Budget',
                        'description': f'Aumentar presupuesto en {recommendation["channel"]}: {recommendation["reason"]}',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
                elif recommendation['action'] == 'decrease_budget':
                    strategies.append({
                        'strategy_type': 'Decrease Channel Budget',
                        'description': f'Reducir presupuesto en {recommendation["channel"]}: {recommendation["reason"]}',
                        'priority': 'low',
                        'expected_impact': 'low'
                    })
        
        self.budget_strategies = strategies
        return strategies
    
    def generate_budget_insights(self):
        """Generar insights de optimización de presupuesto"""
        insights = []
        
        # Insights de performance del presupuesto
        if self.budget_analysis:
            overall_metrics = self.budget_analysis.get('overall_metrics', {})
            budget_utilization = overall_metrics.get('overall_budget_utilization', 0)
            
            if budget_utilization < 80:
                insights.append({
                    'category': 'Budget Utilization',
                    'insight': f'Utilización del presupuesto baja: {budget_utilization:.1f}%',
                    'recommendation': 'Mejorar utilización del presupuesto',
                    'priority': 'high'
                })
            
            overall_roi = overall_metrics.get('overall_roi', 0)
            if overall_roi < 2:
                insights.append({
                    'category': 'Budget ROI',
                    'insight': f'ROI general bajo: {overall_roi:.2f}',
                    'recommendation': 'Mejorar ROI del presupuesto',
                    'priority': 'high'
                })
        
        # Insights de eficiencia del presupuesto
        if self.budget_analysis:
            budget_efficiency = self.budget_analysis.get('budget_efficiency', {})
            efficiency_score = budget_efficiency.get('budget_efficiency_score', 0)
            
            if efficiency_score < 60:
                insights.append({
                    'category': 'Budget Efficiency',
                    'insight': f'Score de eficiencia del presupuesto bajo: {efficiency_score}',
                    'recommendation': 'Mejorar eficiencia del presupuesto',
                    'priority': 'medium'
                })
        
        # Insights de canales
        if self.budget_analysis:
            channel_performance = self.budget_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                # Identificar canal con mejor ROI
                best_channel = max(channel_performance_data, key=lambda x: x['roi'])
                insights.append({
                    'category': 'Channel Performance',
                    'insight': f'Mejor canal por ROI: {best_channel["channel"]} con {best_channel["roi"]:.2f}',
                    'recommendation': 'Aumentar presupuesto en este canal',
                    'priority': 'medium'
                })
        
        # Insights de optimización
        if self.optimization_results:
            performance_comparison = self.optimization_results.get('performance_comparison', {})
            roi_improvement = performance_comparison.get('roi_improvement', 0)
            
            if roi_improvement > 0:
                insights.append({
                    'category': 'Budget Optimization',
                    'insight': f'Optimización puede mejorar ROI en {roi_improvement:.2f}',
                    'recommendation': 'Implementar asignación optimizada de presupuesto',
                    'priority': 'high'
                })
        
        self.budget_insights = insights
        return insights
    
    def create_budget_dashboard(self):
        """Crear dashboard de optimización de presupuesto"""
        if not self.budget_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Budget Performance', 'Budget Utilization',
                          'ROI by Channel', 'Optimization Results'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de performance del presupuesto por canal
        if self.budget_analysis:
            channel_performance = self.budget_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                channels = [channel['channel'] for channel in channel_performance_data]
                rois = [channel['roi'] for channel in channel_performance_data]
                
                fig.add_trace(
                    go.Bar(x=channels, y=rois, name='Channel ROI'),
                    row=1, col=1
                )
        
        # Gráfico de utilización del presupuesto
        if self.budget_analysis:
            channel_performance = self.budget_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                channels = [channel['channel'] for channel in channel_performance_data]
                utilizations = [channel['budget_utilization'] for channel in channel_performance_data]
                
                fig.add_trace(
                    go.Pie(labels=channels, values=utilizations, name='Budget Utilization'),
                    row=1, col=2
                )
        
        # Gráfico de ROI por canal
        if self.budget_analysis:
            channel_performance = self.budget_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                channels = [channel['channel'] for channel in channel_performance_data]
                rois = [channel['roi'] for channel in channel_performance_data]
                
                fig.add_trace(
                    go.Bar(x=channels, y=rois, name='ROI by Channel'),
                    row=2, col=1
                )
        
        # Gráfico de resultados de optimización
        if self.optimization_results:
            optimized_allocation = self.optimization_results.get('optimized_allocation', {})
            
            if optimized_allocation:
                channels = list(optimized_allocation.keys())
                budget_changes = [data['budget_change_percent'] for data in optimized_allocation.values()]
                
                fig.add_trace(
                    go.Bar(x=channels, y=budget_changes, name='Budget Change %'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización de Presupuesto",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_budget_analysis(self, filename='marketing_budget_analysis.json'):
        """Exportar análisis de optimización de presupuesto"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'budget_analysis': self.budget_analysis,
            'optimization_models': {k: {'metrics': v['metrics']} for k, v in self.optimization_models.items()},
            'optimization_results': self.optimization_results,
            'budget_strategies': self.budget_strategies,
            'budget_insights': self.budget_insights,
            'summary': {
                'total_budget': self.budget_data['budget'].sum() if 'budget' in self.budget_data.columns else 0,
                'total_spent': self.budget_data['spent'].sum() if 'spent' in self.budget_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de optimización de presupuesto exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de presupuesto de marketing
    budget_optimizer = MarketingBudgetOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'channel': np.random.choice(['Email', 'Social Media', 'Paid Search', 'Display', 'Direct'], 1000),
        'campaign_id': np.random.randint(1, 50, 1000),
        'audience_segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'budget': np.random.normal(10000, 2000, 1000),
        'spent': np.random.normal(8000, 1500, 1000),
        'revenue': np.random.normal(12000, 3000, 1000),
        'conversions': np.random.poisson(50, 1000),
        'impressions': np.random.poisson(100000, 1000),
        'clicks': np.random.poisson(2000, 1000),
        'roi': np.random.uniform(1, 4, 1000),
        'roas': np.random.uniform(2, 6, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de presupuesto de marketing
    print("📊 Cargando datos de presupuesto de marketing...")
    budget_optimizer.load_budget_data(sample_data)
    
    # Analizar performance del presupuesto
    print("💰 Analizando performance del presupuesto...")
    budget_analysis = budget_optimizer.analyze_budget_performance()
    
    # Optimizar asignación de presupuesto
    print("🎯 Optimizando asignación de presupuesto...")
    optimization_results = budget_optimizer.optimize_budget_allocation(total_budget=100000, optimization_objective='roi')
    
    # Construir modelo de predicción de presupuesto
    print("🔮 Construyendo modelo de predicción de presupuesto...")
    budget_model = budget_optimizer.build_budget_prediction_model()
    
    # Generar estrategias de optimización de presupuesto
    print("🎯 Generando estrategias de optimización de presupuesto...")
    budget_strategies = budget_optimizer.generate_budget_strategies()
    
    # Generar insights de optimización de presupuesto
    print("💡 Generando insights de optimización de presupuesto...")
    budget_insights = budget_optimizer.generate_budget_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de optimización de presupuesto...")
    dashboard = budget_optimizer.create_budget_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de optimización de presupuesto...")
    export_data = budget_optimizer.export_budget_analysis()
    
    print("✅ Sistema de optimización de presupuesto de marketing completado!")




