"""
Marketing Brain Marketing Performance Optimizer
Sistema avanzado de optimización de performance de marketing
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

class MarketingPerformanceOptimizer:
    def __init__(self):
        self.performance_data = {}
        self.performance_analysis = {}
        self.optimization_models = {}
        self.performance_strategies = {}
        self.performance_insights = {}
        self.optimization_results = {}
        
    def load_performance_data(self, performance_data):
        """Cargar datos de performance de marketing"""
        if isinstance(performance_data, str):
            if performance_data.endswith('.csv'):
                self.performance_data = pd.read_csv(performance_data)
            elif performance_data.endswith('.json'):
                with open(performance_data, 'r') as f:
                    data = json.load(f)
                self.performance_data = pd.DataFrame(data)
        else:
            self.performance_data = pd.DataFrame(performance_data)
        
        print(f"✅ Datos de performance de marketing cargados: {len(self.performance_data)} registros")
        return True
    
    def analyze_marketing_performance(self):
        """Analizar performance de marketing"""
        if self.performance_data.empty:
            return None
        
        # Análisis de performance por canal
        channel_performance = self._analyze_channel_performance()
        
        # Análisis de performance por campaña
        campaign_performance = self._analyze_campaign_performance()
        
        # Análisis de performance por segmento
        segment_performance = self._analyze_segment_performance()
        
        # Análisis de performance por contenido
        content_performance = self._analyze_content_performance()
        
        # Análisis de performance por timing
        timing_performance = self._analyze_timing_performance()
        
        # Análisis de performance por dispositivo
        device_performance = self._analyze_device_performance()
        
        # Análisis de performance por ubicación
        location_performance = self._analyze_location_performance()
        
        performance_results = {
            'channel_performance': channel_performance,
            'campaign_performance': campaign_performance,
            'segment_performance': segment_performance,
            'content_performance': content_performance,
            'timing_performance': timing_performance,
            'device_performance': device_performance,
            'location_performance': location_performance,
            'overall_metrics': self._calculate_overall_metrics()
        }
        
        self.performance_analysis = performance_results
        return performance_results
    
    def _analyze_channel_performance(self):
        """Analizar performance por canal"""
        channel_analysis = {}
        
        if 'channel' in self.performance_data.columns:
            channel_performance = self.performance_data.groupby('channel').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_performance['ctr'] = (channel_performance['clicks'] / channel_performance['impressions']) * 100
            channel_performance['conversion_rate'] = (channel_performance['conversions'] / channel_performance['clicks']) * 100
            channel_performance['roi'] = (channel_performance['revenue'] - channel_performance['cost']) / channel_performance['cost']
            channel_performance['roas'] = channel_performance['revenue'] / channel_performance['cost']
            channel_performance['cpm'] = (channel_performance['cost'] / channel_performance['impressions']) * 1000
            channel_performance['cpc'] = channel_performance['cost'] / channel_performance['clicks']
            channel_performance['cpa'] = channel_performance['cost'] / channel_performance['conversions']
            channel_performance['engagement_rate'] = (channel_performance['engagement'] / channel_performance['reach']) * 100
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_channel_efficiency(channel_performance)
            
            channel_analysis = {
                'channel_performance': channel_performance.to_dict('records'),
                'efficiency_analysis': efficiency_analysis
            }
        
        return channel_analysis
    
    def _analyze_channel_efficiency(self, channel_performance):
        """Analizar eficiencia de canales"""
        efficiency_metrics = {}
        
        for _, channel in channel_performance.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # CTR (20% del score)
            ctr = channel['ctr']
            if ctr > 3:
                efficiency_score += 20
            elif ctr > 2:
                efficiency_score += 15
            elif ctr > 1:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # Conversion rate (25% del score)
            conversion_rate = channel['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 25
            elif conversion_rate > 3:
                efficiency_score += 20
            elif conversion_rate > 2:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
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
            
            # Engagement rate (15% del score)
            engagement_rate = channel['engagement_rate']
            if engagement_rate > 5:
                efficiency_score += 15
            elif engagement_rate > 3:
                efficiency_score += 12
            elif engagement_rate > 2:
                efficiency_score += 8
            else:
                efficiency_score += 5
            
            # Volume (10% del score)
            impressions = channel['impressions']
            if impressions > 1000000:
                efficiency_score += 10
            elif impressions > 500000:
                efficiency_score += 7
            elif impressions > 100000:
                efficiency_score += 5
            
            efficiency_metrics[channel['channel']] = {
                'efficiency_score': efficiency_score,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'engagement_rate': engagement_rate,
                'impressions': impressions
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
    
    def _analyze_campaign_performance(self):
        """Analizar performance por campaña"""
        campaign_analysis = {}
        
        if 'campaign_id' in self.performance_data.columns:
            campaign_performance = self.performance_data.groupby('campaign_id').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            campaign_performance['ctr'] = (campaign_performance['clicks'] / campaign_performance['impressions']) * 100
            campaign_performance['conversion_rate'] = (campaign_performance['conversions'] / campaign_performance['clicks']) * 100
            campaign_performance['roi'] = (campaign_performance['revenue'] - campaign_performance['cost']) / campaign_performance['cost']
            campaign_performance['roas'] = campaign_performance['revenue'] / campaign_performance['cost']
            campaign_performance['cpm'] = (campaign_performance['cost'] / campaign_performance['impressions']) * 1000
            campaign_performance['cpc'] = campaign_performance['cost'] / campaign_performance['clicks']
            campaign_performance['cpa'] = campaign_performance['cost'] / campaign_performance['conversions']
            campaign_performance['engagement_rate'] = (campaign_performance['engagement'] / campaign_performance['reach']) * 100
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_campaign_efficiency(campaign_performance)
            
            campaign_analysis = {
                'campaign_performance': campaign_performance.to_dict('records'),
                'efficiency_analysis': efficiency_analysis
            }
        
        return campaign_analysis
    
    def _analyze_campaign_efficiency(self, campaign_performance):
        """Analizar eficiencia de campañas"""
        efficiency_metrics = {}
        
        for _, campaign in campaign_performance.iterrows():
            # Score de eficiencia basado en múltiples métricas
            efficiency_score = 0
            
            # CTR (20% del score)
            ctr = campaign['ctr']
            if ctr > 3:
                efficiency_score += 20
            elif ctr > 2:
                efficiency_score += 15
            elif ctr > 1:
                efficiency_score += 10
            else:
                efficiency_score += 5
            
            # Conversion rate (25% del score)
            conversion_rate = campaign['conversion_rate']
            if conversion_rate > 5:
                efficiency_score += 25
            elif conversion_rate > 3:
                efficiency_score += 20
            elif conversion_rate > 2:
                efficiency_score += 15
            else:
                efficiency_score += 10
            
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
            
            # Engagement rate (15% del score)
            engagement_rate = campaign['engagement_rate']
            if engagement_rate > 5:
                efficiency_score += 15
            elif engagement_rate > 3:
                efficiency_score += 12
            elif engagement_rate > 2:
                efficiency_score += 8
            else:
                efficiency_score += 5
            
            # Volume (10% del score)
            impressions = campaign['impressions']
            if impressions > 1000000:
                efficiency_score += 10
            elif impressions > 500000:
                efficiency_score += 7
            elif impressions > 100000:
                efficiency_score += 5
            
            efficiency_metrics[campaign['campaign_id']] = {
                'efficiency_score': efficiency_score,
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'roi': roi,
                'engagement_rate': engagement_rate,
                'impressions': impressions
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
    
    def _analyze_segment_performance(self):
        """Analizar performance por segmento"""
        segment_analysis = {}
        
        if 'audience_segment' in self.performance_data.columns:
            segment_performance = self.performance_data.groupby('audience_segment').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            segment_performance['ctr'] = (segment_performance['clicks'] / segment_performance['impressions']) * 100
            segment_performance['conversion_rate'] = (segment_performance['conversions'] / segment_performance['clicks']) * 100
            segment_performance['roi'] = (segment_performance['revenue'] - segment_performance['cost']) / segment_performance['cost']
            segment_performance['roas'] = segment_performance['revenue'] / segment_performance['cost']
            segment_performance['cpm'] = (segment_performance['cost'] / segment_performance['impressions']) * 1000
            segment_performance['cpc'] = segment_performance['cost'] / segment_performance['clicks']
            segment_performance['cpa'] = segment_performance['cost'] / segment_performance['conversions']
            segment_performance['engagement_rate'] = (segment_performance['engagement'] / segment_performance['reach']) * 100
            
            segment_analysis = {
                'segment_performance': segment_performance.to_dict('records')
            }
        
        return segment_analysis
    
    def _analyze_content_performance(self):
        """Analizar performance por contenido"""
        content_analysis = {}
        
        if 'content_type' in self.performance_data.columns:
            content_performance = self.performance_data.groupby('content_type').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            content_performance['ctr'] = (content_performance['clicks'] / content_performance['impressions']) * 100
            content_performance['conversion_rate'] = (content_performance['conversions'] / content_performance['clicks']) * 100
            content_performance['roi'] = (content_performance['revenue'] - content_performance['cost']) / content_performance['cost']
            content_performance['roas'] = content_performance['revenue'] / content_performance['cost']
            content_performance['cpm'] = (content_performance['cost'] / content_performance['impressions']) * 1000
            content_performance['cpc'] = content_performance['cost'] / content_performance['clicks']
            content_performance['cpa'] = content_performance['cost'] / content_performance['conversions']
            content_performance['engagement_rate'] = (content_performance['engagement'] / content_performance['reach']) * 100
            
            content_analysis = {
                'content_performance': content_performance.to_dict('records')
            }
        
        return content_analysis
    
    def _analyze_timing_performance(self):
        """Analizar performance por timing"""
        timing_analysis = {}
        
        if 'date' in self.performance_data.columns:
            # Análisis de performance por día de la semana
            self.performance_data['date'] = pd.to_datetime(self.performance_data['date'])
            self.performance_data['day_of_week'] = self.performance_data['date'].dt.day_name()
            
            daily_performance = self.performance_data.groupby('day_of_week').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            daily_performance['ctr'] = (daily_performance['clicks'] / daily_performance['impressions']) * 100
            daily_performance['conversion_rate'] = (daily_performance['conversions'] / daily_performance['clicks']) * 100
            daily_performance['roi'] = (daily_performance['revenue'] - daily_performance['cost']) / daily_performance['cost']
            daily_performance['roas'] = daily_performance['revenue'] / daily_performance['cost']
            daily_performance['engagement_rate'] = (daily_performance['engagement'] / daily_performance['reach']) * 100
            
            # Análisis de performance por hora del día
            self.performance_data['hour'] = self.performance_data['date'].dt.hour
            
            hourly_performance = self.performance_data.groupby('hour').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            hourly_performance['ctr'] = (hourly_performance['clicks'] / hourly_performance['impressions']) * 100
            hourly_performance['conversion_rate'] = (hourly_performance['conversions'] / hourly_performance['clicks']) * 100
            hourly_performance['roi'] = (hourly_performance['revenue'] - hourly_performance['cost']) / hourly_performance['cost']
            hourly_performance['roas'] = hourly_performance['revenue'] / hourly_performance['cost']
            hourly_performance['engagement_rate'] = (hourly_performance['engagement'] / hourly_performance['reach']) * 100
            
            timing_analysis = {
                'daily_performance': daily_performance.to_dict('records'),
                'hourly_performance': hourly_performance.to_dict('records'),
                'best_day': daily_performance.loc[daily_performance['ctr'].idxmax(), 'day_of_week'],
                'best_hour': hourly_performance.loc[hourly_performance['ctr'].idxmax(), 'hour']
            }
        
        return timing_analysis
    
    def _analyze_device_performance(self):
        """Analizar performance por dispositivo"""
        device_analysis = {}
        
        if 'device_type' in self.performance_data.columns:
            device_performance = self.performance_data.groupby('device_type').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            device_performance['ctr'] = (device_performance['clicks'] / device_performance['impressions']) * 100
            device_performance['conversion_rate'] = (device_performance['conversions'] / device_performance['clicks']) * 100
            device_performance['roi'] = (device_performance['revenue'] - device_performance['cost']) / device_performance['cost']
            device_performance['roas'] = device_performance['revenue'] / device_performance['cost']
            device_performance['cpm'] = (device_performance['cost'] / device_performance['impressions']) * 1000
            device_performance['cpc'] = device_performance['cost'] / device_performance['clicks']
            device_performance['cpa'] = device_performance['cost'] / device_performance['conversions']
            device_performance['engagement_rate'] = (device_performance['engagement'] / device_performance['reach']) * 100
            
            device_analysis = {
                'device_performance': device_performance.to_dict('records')
            }
        
        return device_analysis
    
    def _analyze_location_performance(self):
        """Analizar performance por ubicación"""
        location_analysis = {}
        
        if 'location' in self.performance_data.columns:
            location_performance = self.performance_data.groupby('location').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            location_performance['ctr'] = (location_performance['clicks'] / location_performance['impressions']) * 100
            location_performance['conversion_rate'] = (location_performance['conversions'] / location_performance['clicks']) * 100
            location_performance['roi'] = (location_performance['revenue'] - location_performance['cost']) / location_performance['cost']
            location_performance['roas'] = location_performance['revenue'] / location_performance['cost']
            location_performance['cpm'] = (location_performance['cost'] / location_performance['impressions']) * 1000
            location_performance['cpc'] = location_performance['cost'] / location_performance['clicks']
            location_performance['cpa'] = location_performance['cost'] / location_performance['conversions']
            location_performance['engagement_rate'] = (location_performance['engagement'] / location_performance['reach']) * 100
            
            location_analysis = {
                'location_performance': location_performance.to_dict('records')
            }
        
        return location_analysis
    
    def _calculate_overall_metrics(self):
        """Calcular métricas generales"""
        overall_metrics = {}
        
        if not self.performance_data.empty:
            overall_metrics = {
                'total_impressions': self.performance_data['impressions'].sum() if 'impressions' in self.performance_data.columns else 0,
                'total_clicks': self.performance_data['clicks'].sum() if 'clicks' in self.performance_data.columns else 0,
                'total_conversions': self.performance_data['conversions'].sum() if 'conversions' in self.performance_data.columns else 0,
                'total_revenue': self.performance_data['revenue'].sum() if 'revenue' in self.performance_data.columns else 0,
                'total_cost': self.performance_data['cost'].sum() if 'cost' in self.performance_data.columns else 0,
                'total_reach': self.performance_data['reach'].sum() if 'reach' in self.performance_data.columns else 0,
                'total_engagement': self.performance_data['engagement'].sum() if 'engagement' in self.performance_data.columns else 0,
                'overall_ctr': (self.performance_data['clicks'].sum() / self.performance_data['impressions'].sum()) * 100 if 'clicks' in self.performance_data.columns and 'impressions' in self.performance_data.columns else 0,
                'overall_conversion_rate': (self.performance_data['conversions'].sum() / self.performance_data['clicks'].sum()) * 100 if 'conversions' in self.performance_data.columns and 'clicks' in self.performance_data.columns else 0,
                'overall_roi': (self.performance_data['revenue'].sum() - self.performance_data['cost'].sum()) / self.performance_data['cost'].sum() if 'revenue' in self.performance_data.columns and 'cost' in self.performance_data.columns else 0,
                'overall_roas': self.performance_data['revenue'].sum() / self.performance_data['cost'].sum() if 'revenue' in self.performance_data.columns and 'cost' in self.performance_data.columns else 0,
                'overall_engagement_rate': (self.performance_data['engagement'].sum() / self.performance_data['reach'].sum()) * 100 if 'engagement' in self.performance_data.columns and 'reach' in self.performance_data.columns else 0
            }
        
        return overall_metrics
    
    def optimize_performance_parameters(self, optimization_objective='roi'):
        """Optimizar parámetros de performance"""
        if self.performance_data.empty:
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
        elif optimization_objective == 'engagement':
            objective_function = self._engagement_objective_function
        else:
            objective_function = self._roi_objective_function
        
        # Definir restricciones
        constraints = self._define_performance_constraints()
        
        # Definir límites
        bounds = self._define_performance_bounds(optimization_data)
        
        # Punto inicial
        x0 = self._get_initial_performance_parameters(optimization_data)
        
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
        optimization_results = self._process_performance_optimization_results(result, optimization_data)
        
        self.optimization_results = optimization_results
        return optimization_results
    
    def _prepare_optimization_data(self):
        """Preparar datos para optimización"""
        optimization_data = {}
        
        if 'channel' in self.performance_data.columns:
            # Agrupar por canal
            channel_data = self.performance_data.groupby('channel').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum',
                'engagement': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_data['ctr'] = (channel_data['clicks'] / channel_data['impressions']) * 100
            channel_data['conversion_rate'] = (channel_data['conversions'] / channel_data['clicks']) * 100
            channel_data['roi'] = (channel_data['revenue'] - channel_data['cost']) / channel_data['cost']
            channel_data['roas'] = channel_data['revenue'] / channel_data['cost']
            channel_data['engagement_rate'] = (channel_data['engagement'] / channel_data['reach']) * 100
            
            optimization_data = {
                'channels': channel_data['channel'].tolist(),
                'ctr': channel_data['ctr'].tolist(),
                'conversion_rate': channel_data['conversion_rate'].tolist(),
                'roi': channel_data['roi'].tolist(),
                'roas': channel_data['roas'].tolist(),
                'engagement_rate': channel_data['engagement_rate'].tolist(),
                'current_impressions': channel_data['impressions'].tolist()
            }
        
        return optimization_data
    
    def _roi_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar ROI"""
        # Calcular ROI total
        total_roi = 0
        for i, impressions in enumerate(x):
            if impressions > 0:
                roi = optimization_data['roi'][i]
                total_roi += impressions * roi
        
        # Minimizar el negativo para maximizar ROI
        return -total_roi
    
    def _roas_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar ROAS"""
        # Calcular ROAS total
        total_roas = 0
        for i, impressions in enumerate(x):
            if impressions > 0:
                roas = optimization_data['roas'][i]
                total_roas += impressions * roas
        
        # Minimizar el negativo para maximizar ROAS
        return -total_roas
    
    def _conversions_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar conversiones"""
        # Calcular conversiones totales
        total_conversions = 0
        for i, impressions in enumerate(x):
            if impressions > 0:
                ctr = optimization_data['ctr'][i]
                conversion_rate = optimization_data['conversion_rate'][i]
                conversions = impressions * (ctr / 100) * (conversion_rate / 100)
                total_conversions += conversions
        
        # Minimizar el negativo para maximizar conversiones
        return -total_conversions
    
    def _engagement_objective_function(self, x, optimization_data):
        """Función objetivo para maximizar engagement"""
        # Calcular engagement total
        total_engagement = 0
        for i, impressions in enumerate(x):
            if impressions > 0:
                engagement_rate = optimization_data['engagement_rate'][i]
                engagement = impressions * (engagement_rate / 100)
                total_engagement += engagement
        
        # Minimizar el negativo para maximizar engagement
        return -total_engagement
    
    def _define_performance_constraints(self):
        """Definir restricciones de optimización"""
        constraints = []
        
        # Restricción de presupuesto total
        constraints.append({
            'type': 'eq',
            'fun': lambda x: sum(x) - 1000000  # Presupuesto total de 1M impresiones
        })
        
        return constraints
    
    def _define_performance_bounds(self, optimization_data):
        """Definir límites de optimización"""
        bounds = []
        
        for i in range(len(optimization_data['channels'])):
            # Límite mínimo: 0
            # Límite máximo: 2x de las impresiones actuales
            min_impressions = 0
            max_impressions = optimization_data['current_impressions'][i] * 2
            bounds.append((min_impressions, max_impressions))
        
        return bounds
    
    def _get_initial_performance_parameters(self, optimization_data):
        """Obtener parámetros iniciales de performance"""
        # Usar impresiones actuales como punto inicial
        current_impressions = optimization_data['current_impressions']
        
        # Normalizar para que sume el presupuesto total
        total_current = sum(current_impressions)
        if total_current > 0:
            normalized_impressions = [impressions * (1000000 / total_current) for impressions in current_impressions]
        else:
            # Distribución equitativa si no hay datos actuales
            normalized_impressions = [1000000 / len(current_impressions)] * len(current_impressions)
        
        return normalized_impressions
    
    def _process_performance_optimization_results(self, result, optimization_data):
        """Procesar resultados de optimización de performance"""
        optimized_impressions = result.x
        
        # Crear resultados de optimización
        optimization_results = {
            'total_impressions': 1000000,
            'optimization_success': result.success,
            'optimization_message': result.message,
            'optimized_allocation': {},
            'performance_comparison': {},
            'recommendations': []
        }
        
        # Procesar asignación optimizada
        for i, channel in enumerate(optimization_data['channels']):
            current_impressions = optimization_data['current_impressions'][i]
            optimized_impressions_channel = optimized_impressions[i]
            impressions_change = optimized_impressions_channel - current_impressions
            impressions_change_percent = (impressions_change / current_impressions) * 100 if current_impressions > 0 else 0
            
            optimization_results['optimized_allocation'][channel] = {
                'current_impressions': current_impressions,
                'optimized_impressions': optimized_impressions_channel,
                'impressions_change': impressions_change,
                'impressions_change_percent': impressions_change_percent,
                'ctr': optimization_data['ctr'][i],
                'conversion_rate': optimization_data['conversion_rate'][i],
                'roi': optimization_data['roi'][i],
                'roas': optimization_data['roas'][i],
                'engagement_rate': optimization_data['engagement_rate'][i]
            }
        
        # Calcular comparación de performance
        current_total_roi = sum(optimization_data['current_impressions'][i] * optimization_data['roi'][i] for i in range(len(optimization_data['channels'])))
        optimized_total_roi = sum(optimized_impressions[i] * optimization_data['roi'][i] for i in range(len(optimization_data['channels'])))
        
        optimization_results['performance_comparison'] = {
            'current_total_roi': current_total_roi,
            'optimized_total_roi': optimized_total_roi,
            'roi_improvement': optimized_total_roi - current_total_roi,
            'roi_improvement_percent': ((optimized_total_roi - current_total_roi) / current_total_roi) * 100 if current_total_roi > 0 else 0
        }
        
        # Generar recomendaciones
        recommendations = []
        for channel, data in optimization_results['optimized_allocation'].items():
            if data['impressions_change_percent'] > 20:
                recommendations.append({
                    'channel': channel,
                    'action': 'increase_impressions',
                    'current_impressions': data['current_impressions'],
                    'recommended_impressions': data['optimized_impressions'],
                    'reason': f'Alto ROI ({data["roi"]:.2f}) y ROAS ({data["roas"]:.2f})'
                })
            elif data['impressions_change_percent'] < -20:
                recommendations.append({
                    'channel': channel,
                    'action': 'decrease_impressions',
                    'current_impressions': data['current_impressions'],
                    'recommended_impressions': data['optimized_impressions'],
                    'reason': f'Bajo ROI ({data["roi"]:.2f}) y ROAS ({data["roas"]:.2f})'
                })
        
        optimization_results['recommendations'] = recommendations
        
        return optimization_results
    
    def build_performance_prediction_model(self, target_variable='roi'):
        """Construir modelo de predicción de performance"""
        if target_variable not in self.performance_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.performance_data.columns if col != target_variable and col not in ['date', 'campaign_id']]
        X = self.performance_data[feature_columns]
        y = self.performance_data[target_variable]
        
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
        self.optimization_models['performance_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_performance_strategies(self):
        """Generar estrategias de optimización de performance"""
        strategies = []
        
        # Estrategias basadas en análisis de performance
        if self.performance_analysis:
            channel_performance = self.performance_analysis.get('channel_performance', {})
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
        
        # Estrategias basadas en análisis de timing
        if self.performance_analysis:
            timing_performance = self.performance_analysis.get('timing_performance', {})
            best_day = timing_performance.get('best_day')
            best_hour = timing_performance.get('best_hour')
            
            if best_day and best_hour:
                strategies.append({
                    'strategy_type': 'Timing Optimization',
                    'description': f'Optimizar timing: {best_day} a las {best_hour}:00 para máximo performance',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de contenido
        if self.performance_analysis:
            content_performance = self.performance_analysis.get('content_performance', {})
            content_performance_data = content_performance.get('content_performance', [])
            
            if content_performance_data:
                # Identificar tipo de contenido más efectivo
                best_content = max(content_performance_data, key=lambda x: x['ctr'])
                strategies.append({
                    'strategy_type': 'Content Optimization',
                    'description': f'Aumentar contenido de tipo: {best_content["content_type"]}',
                    'priority': 'medium',
                    'expected_impact': 'medium'
                })
        
        # Estrategias basadas en análisis de dispositivo
        if self.performance_analysis:
            device_performance = self.performance_analysis.get('device_performance', {})
            device_performance_data = device_performance.get('device_performance', [])
            
            if device_performance_data:
                # Identificar dispositivo más efectivo
                best_device = max(device_performance_data, key=lambda x: x['ctr'])
                strategies.append({
                    'strategy_type': 'Device Optimization',
                    'description': f'Enfocar en dispositivo: {best_device["device_type"]}',
                    'priority': 'low',
                    'expected_impact': 'low'
                })
        
        # Estrategias basadas en resultados de optimización
        if self.optimization_results:
            recommendations = self.optimization_results.get('recommendations', [])
            
            for recommendation in recommendations:
                if recommendation['action'] == 'increase_impressions':
                    strategies.append({
                        'strategy_type': 'Increase Channel Impressions',
                        'description': f'Aumentar impresiones en {recommendation["channel"]}: {recommendation["reason"]}',
                        'priority': 'medium',
                        'expected_impact': 'medium'
                    })
                elif recommendation['action'] == 'decrease_impressions':
                    strategies.append({
                        'strategy_type': 'Decrease Channel Impressions',
                        'description': f'Reducir impresiones en {recommendation["channel"]}: {recommendation["reason"]}',
                        'priority': 'low',
                        'expected_impact': 'low'
                    })
        
        self.performance_strategies = strategies
        return strategies
    
    def generate_performance_insights(self):
        """Generar insights de optimización de performance"""
        insights = []
        
        # Insights de performance general
        if self.performance_analysis:
            overall_metrics = self.performance_analysis.get('overall_metrics', {})
            overall_ctr = overall_metrics.get('overall_ctr', 0)
            
            if overall_ctr < 2:
                insights.append({
                    'category': 'Performance',
                    'insight': f'CTR general bajo: {overall_ctr:.1f}%',
                    'recommendation': 'Mejorar CTR en todos los canales',
                    'priority': 'high'
                })
            
            overall_conversion_rate = overall_metrics.get('overall_conversion_rate', 0)
            if overall_conversion_rate < 3:
                insights.append({
                    'category': 'Performance',
                    'insight': f'Conversion rate general bajo: {overall_conversion_rate:.1f}%',
                    'recommendation': 'Mejorar conversion rate en todos los canales',
                    'priority': 'high'
                })
        
        # Insights de canales
        if self.performance_analysis:
            channel_performance = self.performance_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                # Identificar canal con mejor performance
                best_channel = max(channel_performance_data, key=lambda x: x['ctr'])
                insights.append({
                    'category': 'Channel Performance',
                    'insight': f'Mejor canal: {best_channel["channel"]} con {best_channel["ctr"]:.1f}% CTR',
                    'recommendation': 'Aumentar inversión en este canal',
                    'priority': 'medium'
                })
        
        # Insights de timing
        if self.performance_analysis:
            timing_performance = self.performance_analysis.get('timing_performance', {})
            best_day = timing_performance.get('best_day')
            best_hour = timing_performance.get('best_hour')
            
            if best_day and best_hour:
                insights.append({
                    'category': 'Timing Performance',
                    'insight': f'Mejor momento para marketing: {best_day} a las {best_hour}:00',
                    'recommendation': 'Optimizar horarios de campañas',
                    'priority': 'low'
                })
        
        # Insights de contenido
        if self.performance_analysis:
            content_performance = self.performance_analysis.get('content_performance', {})
            content_performance_data = content_performance.get('content_performance', [])
            
            if content_performance_data:
                # Identificar tipo de contenido más efectivo
                best_content = max(content_performance_data, key=lambda x: x['ctr'])
                insights.append({
                    'category': 'Content Performance',
                    'insight': f'Mejor tipo de contenido: {best_content["content_type"]} con {best_content["ctr"]:.1f}% CTR',
                    'recommendation': 'Aumentar producción de este tipo de contenido',
                    'priority': 'medium'
                })
        
        # Insights de dispositivo
        if self.performance_analysis:
            device_performance = self.performance_analysis.get('device_performance', {})
            device_performance_data = device_performance.get('device_performance', [])
            
            if device_performance_data:
                # Identificar dispositivo más efectivo
                best_device = max(device_performance_data, key=lambda x: x['ctr'])
                insights.append({
                    'category': 'Device Performance',
                    'insight': f'Mejor dispositivo: {best_device["device_type"]} con {best_device["ctr"]:.1f}% CTR',
                    'recommendation': 'Optimizar para este dispositivo',
                    'priority': 'low'
                })
        
        # Insights de optimización
        if self.optimization_results:
            performance_comparison = self.optimization_results.get('performance_comparison', {})
            roi_improvement = performance_comparison.get('roi_improvement', 0)
            
            if roi_improvement > 0:
                insights.append({
                    'category': 'Performance Optimization',
                    'insight': f'Optimización puede mejorar ROI en {roi_improvement:.2f}',
                    'recommendation': 'Implementar asignación optimizada de impresiones',
                    'priority': 'high'
                })
        
        self.performance_insights = insights
        return insights
    
    def create_performance_dashboard(self):
        """Crear dashboard de optimización de performance"""
        if not self.performance_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Performance', 'Timing Performance',
                          'Content Performance', 'Optimization Results'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de performance de canales
        if self.performance_analysis:
            channel_performance = self.performance_analysis.get('channel_performance', {})
            channel_performance_data = channel_performance.get('channel_performance', [])
            
            if channel_performance_data:
                channels = [channel['channel'] for channel in channel_performance_data]
                ctrs = [channel['ctr'] for channel in channel_performance_data]
                
                fig.add_trace(
                    go.Bar(x=channels, y=ctrs, name='Channel CTR'),
                    row=1, col=1
                )
        
        # Gráfico de performance de timing
        if self.performance_analysis:
            timing_performance = self.performance_analysis.get('timing_performance', {})
            daily_performance = timing_performance.get('daily_performance', [])
            
            if daily_performance:
                days = [data['day_of_week'] for data in daily_performance]
                ctrs = [data['ctr'] for data in daily_performance]
                
                fig.add_trace(
                    go.Bar(x=days, y=ctrs, name='Daily CTR'),
                    row=1, col=2
                )
        
        # Gráfico de performance de contenido
        if self.performance_analysis:
            content_performance = self.performance_analysis.get('content_performance', {})
            content_performance_data = content_performance.get('content_performance', [])
            
            if content_performance_data:
                content_types = [content['content_type'] for content in content_performance_data]
                ctrs = [content['ctr'] for content in content_performance_data]
                
                fig.add_trace(
                    go.Bar(x=content_types, y=ctrs, name='Content CTR'),
                    row=2, col=1
                )
        
        # Gráfico de resultados de optimización
        if self.optimization_results:
            optimized_allocation = self.optimization_results.get('optimized_allocation', {})
            
            if optimized_allocation:
                channels = list(optimized_allocation.keys())
                impressions_changes = [data['impressions_change_percent'] for data in optimized_allocation.values()]
                
                fig.add_trace(
                    go.Bar(x=channels, y=impressions_changes, name='Impressions Change %'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Optimización de Performance",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_performance_analysis(self, filename='marketing_performance_analysis.json'):
        """Exportar análisis de optimización de performance"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'performance_analysis': self.performance_analysis,
            'optimization_models': {k: {'metrics': v['metrics']} for k, v in self.optimization_models.items()},
            'optimization_results': self.optimization_results,
            'performance_strategies': self.performance_strategies,
            'performance_insights': self.performance_insights,
            'summary': {
                'total_impressions': self.performance_data['impressions'].sum() if 'impressions' in self.performance_data.columns else 0,
                'total_clicks': self.performance_data['clicks'].sum() if 'clicks' in self.performance_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de optimización de performance exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de performance de marketing
    performance_optimizer = MarketingPerformanceOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'channel': np.random.choice(['Email', 'Social Media', 'Paid Search', 'Display', 'Direct'], 1000),
        'campaign_id': np.random.randint(1, 50, 1000),
        'audience_segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'content_type': np.random.choice(['Text', 'Image', 'Video', 'Interactive'], 1000),
        'device_type': np.random.choice(['Desktop', 'Mobile', 'Tablet'], 1000),
        'location': np.random.choice(['US', 'UK', 'CA', 'AU', 'DE'], 1000),
        'impressions': np.random.poisson(10000, 1000),
        'clicks': np.random.poisson(200, 1000),
        'conversions': np.random.poisson(10, 1000),
        'revenue': np.random.normal(500, 100, 1000),
        'cost': np.random.normal(100, 20, 1000),
        'reach': np.random.poisson(5000, 1000),
        'engagement': np.random.poisson(100, 1000),
        'ctr': np.random.uniform(1, 5, 1000),
        'conversion_rate': np.random.uniform(2, 8, 1000),
        'roi': np.random.uniform(1, 4, 1000),
        'roas': np.random.uniform(2, 6, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de performance de marketing
    print("📊 Cargando datos de performance de marketing...")
    performance_optimizer.load_performance_data(sample_data)
    
    # Analizar performance de marketing
    print("📈 Analizando performance de marketing...")
    performance_analysis = performance_optimizer.analyze_marketing_performance()
    
    # Optimizar parámetros de performance
    print("🎯 Optimizando parámetros de performance...")
    optimization_results = performance_optimizer.optimize_performance_parameters(optimization_objective='roi')
    
    # Construir modelo de predicción de performance
    print("🔮 Construyendo modelo de predicción de performance...")
    performance_model = performance_optimizer.build_performance_prediction_model()
    
    # Generar estrategias de optimización de performance
    print("🎯 Generando estrategias de optimización de performance...")
    performance_strategies = performance_optimizer.generate_performance_strategies()
    
    # Generar insights de optimización de performance
    print("💡 Generando insights de optimización de performance...")
    performance_insights = performance_optimizer.generate_performance_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de optimización de performance...")
    dashboard = performance_optimizer.create_performance_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de optimización de performance...")
    export_data = performance_optimizer.export_performance_analysis()
    
    print("✅ Sistema de optimización de performance de marketing completado!")






