"""
Marketing Brain Marketing Analytics Optimizer
Motor avanzado de optimización de marketing analytics
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

class MarketingAnalyticsOptimizer:
    def __init__(self):
        self.analytics_data = {}
        self.performance_analysis = {}
        self.kpi_analysis = {}
        self.trend_analysis = {}
        self.analytics_models = {}
        self.optimization_strategies = {}
        self.analytics_insights = {}
        
    def load_analytics_data(self, analytics_data):
        """Cargar datos de marketing analytics"""
        if isinstance(analytics_data, str):
            if analytics_data.endswith('.csv'):
                self.analytics_data = pd.read_csv(analytics_data)
            elif analytics_data.endswith('.json'):
                with open(analytics_data, 'r') as f:
                    data = json.load(f)
                self.analytics_data = pd.DataFrame(data)
        else:
            self.analytics_data = pd.DataFrame(analytics_data)
        
        print(f"✅ Datos de marketing analytics cargados: {len(self.analytics_data)} registros")
        return True
    
    def analyze_marketing_performance(self):
        """Analizar performance de marketing"""
        if self.analytics_data.empty:
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
        
        performance_results = {
            'channel_performance': channel_performance,
            'campaign_performance': campaign_performance,
            'segment_performance': segment_performance,
            'content_performance': content_performance,
            'timing_performance': timing_performance,
            'overall_metrics': self._calculate_overall_metrics()
        }
        
        self.performance_analysis = performance_results
        return performance_results
    
    def _analyze_channel_performance(self):
        """Analizar performance por canal"""
        channel_analysis = {}
        
        if 'channel' in self.analytics_data.columns:
            channel_performance = self.analytics_data.groupby('channel').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            channel_performance['ctr'] = (channel_performance['clicks'] / channel_performance['impressions']) * 100
            channel_performance['conversion_rate'] = (channel_performance['conversions'] / channel_performance['clicks']) * 100
            channel_performance['roi'] = (channel_performance['revenue'] - channel_performance['cost']) / channel_performance['cost']
            channel_performance['cpm'] = (channel_performance['cost'] / channel_performance['impressions']) * 1000
            channel_performance['cpc'] = channel_performance['cost'] / channel_performance['clicks']
            channel_performance['cpa'] = channel_performance['cost'] / channel_performance['conversions']
            channel_performance['roas'] = channel_performance['revenue'] / channel_performance['cost']
            
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
            
            # ROAS (15% del score)
            roas = channel['roas']
            if roas > 4:
                efficiency_score += 15
            elif roas > 3:
                efficiency_score += 12
            elif roas > 2:
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
                'roas': roas,
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
        
        if 'campaign_id' in self.analytics_data.columns:
            campaign_performance = self.analytics_data.groupby('campaign_id').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            campaign_performance['ctr'] = (campaign_performance['clicks'] / campaign_performance['impressions']) * 100
            campaign_performance['conversion_rate'] = (campaign_performance['conversions'] / campaign_performance['clicks']) * 100
            campaign_performance['roi'] = (campaign_performance['revenue'] - campaign_performance['cost']) / campaign_performance['cost']
            campaign_performance['cpm'] = (campaign_performance['cost'] / campaign_performance['impressions']) * 1000
            campaign_performance['cpc'] = campaign_performance['cost'] / campaign_performance['clicks']
            campaign_performance['cpa'] = campaign_performance['cost'] / campaign_performance['conversions']
            campaign_performance['roas'] = campaign_performance['revenue'] / campaign_performance['cost']
            
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
            
            # ROAS (15% del score)
            roas = campaign['roas']
            if roas > 4:
                efficiency_score += 15
            elif roas > 3:
                efficiency_score += 12
            elif roas > 2:
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
                'roas': roas,
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
        
        if 'audience_segment' in self.analytics_data.columns:
            segment_performance = self.analytics_data.groupby('audience_segment').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            segment_performance['ctr'] = (segment_performance['clicks'] / segment_performance['impressions']) * 100
            segment_performance['conversion_rate'] = (segment_performance['conversions'] / segment_performance['clicks']) * 100
            segment_performance['roi'] = (segment_performance['revenue'] - segment_performance['cost']) / segment_performance['cost']
            segment_performance['cpm'] = (segment_performance['cost'] / segment_performance['impressions']) * 1000
            segment_performance['cpc'] = segment_performance['cost'] / segment_performance['clicks']
            segment_performance['cpa'] = segment_performance['cost'] / segment_performance['conversions']
            segment_performance['roas'] = segment_performance['revenue'] / segment_performance['cost']
            
            segment_analysis = {
                'segment_performance': segment_performance.to_dict('records')
            }
        
        return segment_analysis
    
    def _analyze_content_performance(self):
        """Analizar performance por contenido"""
        content_analysis = {}
        
        if 'content_type' in self.analytics_data.columns:
            content_performance = self.analytics_data.groupby('content_type').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum',
                'reach': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            content_performance['ctr'] = (content_performance['clicks'] / content_performance['impressions']) * 100
            content_performance['conversion_rate'] = (content_performance['conversions'] / content_performance['clicks']) * 100
            content_performance['roi'] = (content_performance['revenue'] - content_performance['cost']) / content_performance['cost']
            content_performance['cpm'] = (content_performance['cost'] / content_performance['impressions']) * 1000
            content_performance['cpc'] = content_performance['cost'] / content_performance['clicks']
            content_performance['cpa'] = content_performance['cost'] / content_performance['conversions']
            content_performance['roas'] = content_performance['revenue'] / content_performance['cost']
            
            content_analysis = {
                'content_performance': content_performance.to_dict('records')
            }
        
        return content_analysis
    
    def _analyze_timing_performance(self):
        """Analizar performance por timing"""
        timing_analysis = {}
        
        if 'date' in self.analytics_data.columns:
            # Análisis de performance por día de la semana
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            self.analytics_data['day_of_week'] = self.analytics_data['date'].dt.day_name()
            
            daily_performance = self.analytics_data.groupby('day_of_week').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            daily_performance['ctr'] = (daily_performance['clicks'] / daily_performance['impressions']) * 100
            daily_performance['conversion_rate'] = (daily_performance['conversions'] / daily_performance['clicks']) * 100
            daily_performance['roi'] = (daily_performance['revenue'] - daily_performance['cost']) / daily_performance['cost']
            daily_performance['roas'] = daily_performance['revenue'] / daily_performance['cost']
            
            # Análisis de performance por hora del día
            self.analytics_data['hour'] = self.analytics_data['date'].dt.hour
            
            hourly_performance = self.analytics_data.groupby('hour').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de performance
            hourly_performance['ctr'] = (hourly_performance['clicks'] / hourly_performance['impressions']) * 100
            hourly_performance['conversion_rate'] = (hourly_performance['conversions'] / hourly_performance['clicks']) * 100
            hourly_performance['roi'] = (hourly_performance['revenue'] - hourly_performance['cost']) / hourly_performance['cost']
            hourly_performance['roas'] = hourly_performance['revenue'] / hourly_performance['cost']
            
            timing_analysis = {
                'daily_performance': daily_performance.to_dict('records'),
                'hourly_performance': hourly_performance.to_dict('records'),
                'best_day': daily_performance.loc[daily_performance['ctr'].idxmax(), 'day_of_week'],
                'best_hour': hourly_performance.loc[hourly_performance['ctr'].idxmax(), 'hour']
            }
        
        return timing_analysis
    
    def _calculate_overall_metrics(self):
        """Calcular métricas generales"""
        overall_metrics = {}
        
        if not self.analytics_data.empty:
            overall_metrics = {
                'total_impressions': self.analytics_data['impressions'].sum() if 'impressions' in self.analytics_data.columns else 0,
                'total_clicks': self.analytics_data['clicks'].sum() if 'clicks' in self.analytics_data.columns else 0,
                'total_conversions': self.analytics_data['conversions'].sum() if 'conversions' in self.analytics_data.columns else 0,
                'total_revenue': self.analytics_data['revenue'].sum() if 'revenue' in self.analytics_data.columns else 0,
                'total_cost': self.analytics_data['cost'].sum() if 'cost' in self.analytics_data.columns else 0,
                'overall_ctr': (self.analytics_data['clicks'].sum() / self.analytics_data['impressions'].sum()) * 100 if 'clicks' in self.analytics_data.columns and 'impressions' in self.analytics_data.columns else 0,
                'overall_conversion_rate': (self.analytics_data['conversions'].sum() / self.analytics_data['clicks'].sum()) * 100 if 'conversions' in self.analytics_data.columns and 'clicks' in self.analytics_data.columns else 0,
                'overall_roi': (self.analytics_data['revenue'].sum() - self.analytics_data['cost'].sum()) / self.analytics_data['cost'].sum() if 'revenue' in self.analytics_data.columns and 'cost' in self.analytics_data.columns else 0,
                'overall_roas': self.analytics_data['revenue'].sum() / self.analytics_data['cost'].sum() if 'revenue' in self.analytics_data.columns and 'cost' in self.analytics_data.columns else 0
            }
        
        return overall_metrics
    
    def analyze_kpi_performance(self):
        """Analizar performance de KPIs"""
        if self.analytics_data.empty:
            return None
        
        # Análisis de KPIs
        kpi_analysis = {}
        
        # Análisis de KPIs por período
        kpi_trends = self._analyze_kpi_trends()
        kpi_analysis['kpi_trends'] = kpi_trends
        
        # Análisis de KPIs por objetivo
        kpi_goals = self._analyze_kpi_goals()
        kpi_analysis['kpi_goals'] = kpi_goals
        
        # Análisis de KPIs por benchmark
        kpi_benchmarks = self._analyze_kpi_benchmarks()
        kpi_analysis['kpi_benchmarks'] = kpi_benchmarks
        
        # Análisis de KPIs por alerta
        kpi_alerts = self._analyze_kpi_alerts()
        kpi_analysis['kpi_alerts'] = kpi_alerts
        
        self.kpi_analysis = kpi_analysis
        return kpi_analysis
    
    def _analyze_kpi_trends(self):
        """Analizar tendencias de KPIs"""
        kpi_trends = {}
        
        if 'date' in self.analytics_data.columns:
            # Análisis de tendencias por día
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            daily_kpis = self.analytics_data.groupby('date').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de KPIs
            daily_kpis['ctr'] = (daily_kpis['clicks'] / daily_kpis['impressions']) * 100
            daily_kpis['conversion_rate'] = (daily_kpis['conversions'] / daily_kpis['clicks']) * 100
            daily_kpis['roi'] = (daily_kpis['revenue'] - daily_kpis['cost']) / daily_kpis['cost']
            daily_kpis['roas'] = daily_kpis['revenue'] / daily_kpis['cost']
            
            # Análisis de tendencias por semana
            self.analytics_data['week'] = self.analytics_data['date'].dt.to_period('W')
            weekly_kpis = self.analytics_data.groupby('week').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de KPIs
            weekly_kpis['ctr'] = (weekly_kpis['clicks'] / weekly_kpis['impressions']) * 100
            weekly_kpis['conversion_rate'] = (weekly_kpis['conversions'] / weekly_kpis['clicks']) * 100
            weekly_kpis['roi'] = (weekly_kpis['revenue'] - weekly_kpis['cost']) / weekly_kpis['cost']
            weekly_kpis['roas'] = weekly_kpis['revenue'] / weekly_kpis['cost']
            
            kpi_trends = {
                'daily_kpis': daily_kpis.to_dict('records'),
                'weekly_kpis': weekly_kpis.to_dict('records')
            }
        
        return kpi_trends
    
    def _analyze_kpi_goals(self):
        """Analizar KPIs vs objetivos"""
        kpi_goals = {}
        
        # Definir objetivos de KPIs
        kpi_targets = {
            'ctr': 2.5,
            'conversion_rate': 3.0,
            'roi': 2.0,
            'roas': 3.0
        }
        
        # Calcular métricas actuales
        current_metrics = self._calculate_overall_metrics()
        
        # Comparar con objetivos
        goal_analysis = {}
        for kpi, target in kpi_targets.items():
            current_value = current_metrics.get(f'overall_{kpi}', 0)
            performance_vs_goal = (current_value / target) * 100 if target > 0 else 0
            
            goal_analysis[kpi] = {
                'current_value': current_value,
                'target_value': target,
                'performance_vs_goal': performance_vs_goal,
                'status': 'above_goal' if performance_vs_goal >= 100 else 'below_goal'
            }
        
        kpi_goals = {
            'goal_analysis': goal_analysis,
            'overall_goal_performance': np.mean([goal_analysis[kpi]['performance_vs_goal'] for kpi in goal_analysis.keys()])
        }
        
        return kpi_goals
    
    def _analyze_kpi_benchmarks(self):
        """Analizar KPIs vs benchmarks de industria"""
        kpi_benchmarks = {}
        
        # Definir benchmarks de industria
        industry_benchmarks = {
            'ctr': 2.0,
            'conversion_rate': 2.5,
            'roi': 1.5,
            'roas': 2.5
        }
        
        # Calcular métricas actuales
        current_metrics = self._calculate_overall_metrics()
        
        # Comparar con benchmarks
        benchmark_analysis = {}
        for kpi, benchmark in industry_benchmarks.items():
            current_value = current_metrics.get(f'overall_{kpi}', 0)
            performance_vs_benchmark = (current_value / benchmark) * 100 if benchmark > 0 else 0
            
            benchmark_analysis[kpi] = {
                'current_value': current_value,
                'benchmark_value': benchmark,
                'performance_vs_benchmark': performance_vs_benchmark,
                'status': 'above_benchmark' if performance_vs_benchmark >= 100 else 'below_benchmark'
            }
        
        kpi_benchmarks = {
            'benchmark_analysis': benchmark_analysis,
            'overall_benchmark_performance': np.mean([benchmark_analysis[kpi]['performance_vs_benchmark'] for kpi in benchmark_analysis.keys()])
        }
        
        return kpi_benchmarks
    
    def _analyze_kpi_alerts(self):
        """Analizar alertas de KPIs"""
        kpi_alerts = {}
        
        # Definir umbrales de alerta
        alert_thresholds = {
            'ctr': {'min': 1.0, 'max': 5.0},
            'conversion_rate': {'min': 1.5, 'max': 8.0},
            'roi': {'min': 1.0, 'max': 5.0},
            'roas': {'min': 2.0, 'max': 8.0}
        }
        
        # Calcular métricas actuales
        current_metrics = self._calculate_overall_metrics()
        
        # Verificar alertas
        alerts = []
        for kpi, thresholds in alert_thresholds.items():
            current_value = current_metrics.get(f'overall_{kpi}', 0)
            
            if current_value < thresholds['min']:
                alerts.append({
                    'kpi': kpi,
                    'type': 'low_performance',
                    'current_value': current_value,
                    'threshold': thresholds['min'],
                    'message': f'{kpi.upper()} está por debajo del umbral mínimo'
                })
            elif current_value > thresholds['max']:
                alerts.append({
                    'kpi': kpi,
                    'type': 'high_performance',
                    'current_value': current_value,
                    'threshold': thresholds['max'],
                    'message': f'{kpi.upper()} está por encima del umbral máximo'
                })
        
        kpi_alerts = {
            'alerts': alerts,
            'alert_count': len(alerts),
            'critical_alerts': [alert for alert in alerts if alert['type'] == 'low_performance']
        }
        
        return kpi_alerts
    
    def analyze_marketing_trends(self):
        """Analizar tendencias de marketing"""
        if self.analytics_data.empty:
            return None
        
        # Análisis de tendencias
        trend_analysis = {}
        
        # Análisis de tendencias temporales
        temporal_trends = self._analyze_temporal_trends()
        trend_analysis['temporal_trends'] = temporal_trends
        
        # Análisis de tendencias por canal
        channel_trends = self._analyze_channel_trends()
        trend_analysis['channel_trends'] = channel_trends
        
        # Análisis de tendencias por segmento
        segment_trends = self._analyze_segment_trends()
        trend_analysis['segment_trends'] = segment_trends
        
        # Análisis de tendencias por contenido
        content_trends = self._analyze_content_trends()
        trend_analysis['content_trends'] = content_trends
        
        self.trend_analysis = trend_analysis
        return trend_analysis
    
    def _analyze_temporal_trends(self):
        """Analizar tendencias temporales"""
        temporal_trends = {}
        
        if 'date' in self.analytics_data.columns:
            # Análisis de tendencias por mes
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            self.analytics_data['month'] = self.analytics_data['date'].dt.to_period('M')
            
            monthly_trends = self.analytics_data.groupby('month').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de tendencias
            monthly_trends['ctr'] = (monthly_trends['clicks'] / monthly_trends['impressions']) * 100
            monthly_trends['conversion_rate'] = (monthly_trends['conversions'] / monthly_trends['clicks']) * 100
            monthly_trends['roi'] = (monthly_trends['revenue'] - monthly_trends['cost']) / monthly_trends['cost']
            monthly_trends['roas'] = monthly_trends['revenue'] / monthly_trends['cost']
            
            # Análisis de tendencias por trimestre
            self.analytics_data['quarter'] = self.analytics_data['date'].dt.to_period('Q')
            quarterly_trends = self.analytics_data.groupby('quarter').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de tendencias
            quarterly_trends['ctr'] = (quarterly_trends['clicks'] / quarterly_trends['impressions']) * 100
            quarterly_trends['conversion_rate'] = (quarterly_trends['conversions'] / quarterly_trends['clicks']) * 100
            quarterly_trends['roi'] = (quarterly_trends['revenue'] - quarterly_trends['cost']) / quarterly_trends['cost']
            quarterly_trends['roas'] = quarterly_trends['revenue'] / quarterly_trends['cost']
            
            temporal_trends = {
                'monthly_trends': monthly_trends.to_dict('records'),
                'quarterly_trends': quarterly_trends.to_dict('records')
            }
        
        return temporal_trends
    
    def _analyze_channel_trends(self):
        """Analizar tendencias por canal"""
        channel_trends = {}
        
        if 'channel' in self.analytics_data.columns and 'date' in self.analytics_data.columns:
            # Análisis de tendencias por canal y mes
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            self.analytics_data['month'] = self.analytics_data['date'].dt.to_period('M')
            
            channel_monthly_trends = self.analytics_data.groupby(['month', 'channel']).agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de tendencias
            channel_monthly_trends['ctr'] = (channel_monthly_trends['clicks'] / channel_monthly_trends['impressions']) * 100
            channel_monthly_trends['conversion_rate'] = (channel_monthly_trends['conversions'] / channel_monthly_trends['clicks']) * 100
            channel_monthly_trends['roi'] = (channel_monthly_trends['revenue'] - channel_monthly_trends['cost']) / channel_monthly_trends['cost']
            channel_monthly_trends['roas'] = channel_monthly_trends['revenue'] / channel_monthly_trends['cost']
            
            channel_trends = {
                'channel_monthly_trends': channel_monthly_trends.to_dict('records')
            }
        
        return channel_trends
    
    def _analyze_segment_trends(self):
        """Analizar tendencias por segmento"""
        segment_trends = {}
        
        if 'audience_segment' in self.analytics_data.columns and 'date' in self.analytics_data.columns:
            # Análisis de tendencias por segmento y mes
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            self.analytics_data['month'] = self.analytics_data['date'].dt.to_period('M')
            
            segment_monthly_trends = self.analytics_data.groupby(['month', 'audience_segment']).agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de tendencias
            segment_monthly_trends['ctr'] = (segment_monthly_trends['clicks'] / segment_monthly_trends['impressions']) * 100
            segment_monthly_trends['conversion_rate'] = (segment_monthly_trends['conversions'] / segment_monthly_trends['clicks']) * 100
            segment_monthly_trends['roi'] = (segment_monthly_trends['revenue'] - segment_monthly_trends['cost']) / segment_monthly_trends['cost']
            segment_monthly_trends['roas'] = segment_monthly_trends['revenue'] / segment_monthly_trends['cost']
            
            segment_trends = {
                'segment_monthly_trends': segment_monthly_trends.to_dict('records')
            }
        
        return segment_trends
    
    def _analyze_content_trends(self):
        """Analizar tendencias por contenido"""
        content_trends = {}
        
        if 'content_type' in self.analytics_data.columns and 'date' in self.analytics_data.columns:
            # Análisis de tendencias por tipo de contenido y mes
            self.analytics_data['date'] = pd.to_datetime(self.analytics_data['date'])
            self.analytics_data['month'] = self.analytics_data['date'].dt.to_period('M')
            
            content_monthly_trends = self.analytics_data.groupby(['month', 'content_type']).agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue': 'sum',
                'cost': 'sum'
            }).reset_index()
            
            # Calcular métricas de tendencias
            content_monthly_trends['ctr'] = (content_monthly_trends['clicks'] / content_monthly_trends['impressions']) * 100
            content_monthly_trends['conversion_rate'] = (content_monthly_trends['conversions'] / content_monthly_trends['clicks']) * 100
            content_monthly_trends['roi'] = (content_monthly_trends['revenue'] - content_monthly_trends['cost']) / content_monthly_trends['cost']
            content_monthly_trends['roas'] = content_monthly_trends['revenue'] / content_monthly_trends['cost']
            
            content_trends = {
                'content_monthly_trends': content_monthly_trends.to_dict('records')
            }
        
        return content_trends
    
    def build_analytics_prediction_model(self, target_variable='conversion_rate'):
        """Construir modelo de predicción de analytics"""
        if target_variable not in self.analytics_data.columns:
            raise ValueError(f"Variable objetivo '{target_variable}' no encontrada")
        
        # Preparar datos
        feature_columns = [col for col in self.analytics_data.columns if col != target_variable and col not in ['date', 'campaign_id']]
        X = self.analytics_data[feature_columns]
        y = self.analytics_data[target_variable]
        
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
        self.analytics_models['analytics_predictor'] = {
            'model': model,
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'metrics': model_metrics
        }
        
        return model_metrics
    
    def generate_analytics_strategies(self):
        """Generar estrategias de marketing analytics"""
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
        
        # Estrategias basadas en análisis de KPIs
        if self.kpi_analysis:
            kpi_goals = self.kpi_analysis.get('kpi_goals', {})
            goal_analysis = kpi_goals.get('goal_analysis', {})
            
            # Identificar KPIs por debajo del objetivo
            below_goal_kpis = [kpi for kpi, data in goal_analysis.items() if data['status'] == 'below_goal']
            if below_goal_kpis:
                strategies.append({
                    'strategy_type': 'Improve Underperforming KPIs',
                    'description': f'Mejorar KPIs por debajo del objetivo: {", ".join(below_goal_kpis)}',
                    'priority': 'high',
                    'expected_impact': 'high'
                })
        
        # Estrategias basadas en análisis de tendencias
        if self.trend_analysis:
            temporal_trends = self.trend_analysis.get('temporal_trends', {})
            monthly_trends = temporal_trends.get('monthly_trends', [])
            
            if monthly_trends:
                # Analizar tendencias de CTR
                ctr_trends = [trend['ctr'] for trend in monthly_trends]
                if len(ctr_trends) >= 2:
                    ctr_trend_direction = 'increasing' if ctr_trends[-1] > ctr_trends[-2] else 'decreasing'
                    strategies.append({
                        'strategy_type': 'CTR Trend Optimization',
                        'description': f'CTR está {ctr_trend_direction}, optimizar estrategias de CTR',
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
                    'priority': 'low',
                    'expected_impact': 'low'
                })
        
        self.optimization_strategies = strategies
        return strategies
    
    def generate_analytics_insights(self):
        """Generar insights de marketing analytics"""
        insights = []
        
        # Insights de performance
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
        
        # Insights de KPIs
        if self.kpi_analysis:
            kpi_goals = self.kpi_analysis.get('kpi_goals', {})
            overall_goal_performance = kpi_goals.get('overall_goal_performance', 0)
            
            if overall_goal_performance < 80:
                insights.append({
                    'category': 'KPI Performance',
                    'insight': f'Performance general vs objetivos: {overall_goal_performance:.1f}%',
                    'recommendation': 'Mejorar performance para alcanzar objetivos',
                    'priority': 'high'
                })
            
            kpi_alerts = self.kpi_analysis.get('kpi_alerts', {})
            critical_alerts = kpi_alerts.get('critical_alerts', [])
            
            if critical_alerts:
                insights.append({
                    'category': 'KPI Alerts',
                    'insight': f'{len(critical_alerts)} alertas críticas de KPIs',
                    'recommendation': 'Revisar y corregir KPIs críticos',
                    'priority': 'high'
                })
        
        # Insights de tendencias
        if self.trend_analysis:
            temporal_trends = self.trend_analysis.get('temporal_trends', {})
            monthly_trends = temporal_trends.get('monthly_trends', [])
            
            if monthly_trends:
                # Analizar tendencia de revenue
                revenue_trends = [trend['revenue'] for trend in monthly_trends]
                if len(revenue_trends) >= 2:
                    revenue_trend_direction = 'increasing' if revenue_trends[-1] > revenue_trends[-2] else 'decreasing'
                    insights.append({
                        'category': 'Revenue Trends',
                        'insight': f'Revenue está {revenue_trend_direction}',
                        'recommendation': f'{"Mantener" if revenue_trend_direction == "increasing" else "Revisar"} estrategias de revenue',
                        'priority': 'medium'
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
        
        self.analytics_insights = insights
        return insights
    
    def create_analytics_dashboard(self):
        """Crear dashboard de marketing analytics"""
        if not self.analytics_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Channel Performance', 'KPI Trends',
                          'Performance by Segment', 'Timing Analysis'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
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
        
        # Gráfico de tendencias de KPIs
        if self.kpi_analysis:
            kpi_trends = self.kpi_analysis.get('kpi_trends', {})
            daily_kpis = kpi_trends.get('daily_kpis', [])
            
            if daily_kpis:
                dates = [kpi['date'] for kpi in daily_kpis]
                ctrs = [kpi['ctr'] for kpi in daily_kpis]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=ctrs, mode='lines+markers', name='Daily CTR'),
                    row=1, col=2
                )
        
        # Gráfico de performance por segmento
        if self.performance_analysis:
            segment_performance = self.performance_analysis.get('segment_performance', {})
            segment_performance_data = segment_performance.get('segment_performance', [])
            
            if segment_performance_data:
                segments = [segment['audience_segment'] for segment in segment_performance_data]
                conversion_rates = [segment['conversion_rate'] for segment in segment_performance_data]
                
                fig.add_trace(
                    go.Bar(x=segments, y=conversion_rates, name='Segment Conversion Rate'),
                    row=2, col=1
                )
        
        # Gráfico de análisis de timing
        if self.performance_analysis:
            timing_performance = self.performance_analysis.get('timing_performance', {})
            hourly_performance = timing_performance.get('hourly_performance', [])
            
            if hourly_performance:
                hours = [data['hour'] for data in hourly_performance]
                ctrs = [data['ctr'] for data in hourly_performance]
                
                fig.add_trace(
                    go.Scatter(x=hours, y=ctrs, mode='lines+markers', name='Hourly CTR'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Marketing Analytics",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_analytics_analysis(self, filename='marketing_analytics_analysis.json'):
        """Exportar análisis de marketing analytics"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'performance_analysis': self.performance_analysis,
            'kpi_analysis': self.kpi_analysis,
            'trend_analysis': self.trend_analysis,
            'analytics_models': {k: {'metrics': v['metrics']} for k, v in self.analytics_models.items()},
            'optimization_strategies': self.optimization_strategies,
            'analytics_insights': self.analytics_insights,
            'summary': {
                'total_campaigns': len(self.analytics_data['campaign_id'].unique()) if 'campaign_id' in self.analytics_data.columns else 0,
                'total_channels': len(self.analytics_data['channel'].unique()) if 'channel' in self.analytics_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de marketing analytics exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del optimizador de marketing analytics
    analytics_optimizer = MarketingAnalyticsOptimizer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'campaign_id': np.random.randint(1, 50, 1000),
        'channel': np.random.choice(['Email', 'Social Media', 'Paid Search', 'Display', 'Direct'], 1000),
        'audience_segment': np.random.choice(['New', 'Active', 'Inactive', 'VIP'], 1000),
        'content_type': np.random.choice(['Text', 'Image', 'Video', 'Interactive'], 1000),
        'impressions': np.random.poisson(10000, 1000),
        'clicks': np.random.poisson(200, 1000),
        'conversions': np.random.poisson(10, 1000),
        'revenue': np.random.normal(500, 100, 1000),
        'cost': np.random.normal(100, 20, 1000),
        'reach': np.random.poisson(5000, 1000),
        'ctr': np.random.uniform(1, 5, 1000),
        'conversion_rate': np.random.uniform(2, 8, 1000),
        'roi': np.random.uniform(1, 4, 1000),
        'roas': np.random.uniform(2, 6, 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Cargar datos de marketing analytics
    print("📊 Cargando datos de marketing analytics...")
    analytics_optimizer.load_analytics_data(sample_data)
    
    # Analizar performance de marketing
    print("📈 Analizando performance de marketing...")
    performance_analysis = analytics_optimizer.analyze_marketing_performance()
    
    # Analizar performance de KPIs
    print("🎯 Analizando performance de KPIs...")
    kpi_analysis = analytics_optimizer.analyze_kpi_performance()
    
    # Analizar tendencias de marketing
    print("📊 Analizando tendencias de marketing...")
    trend_analysis = analytics_optimizer.analyze_marketing_trends()
    
    # Construir modelo de predicción de analytics
    print("🔮 Construyendo modelo de predicción de analytics...")
    analytics_model = analytics_optimizer.build_analytics_prediction_model()
    
    # Generar estrategias de marketing analytics
    print("🎯 Generando estrategias de marketing analytics...")
    analytics_strategies = analytics_optimizer.generate_analytics_strategies()
    
    # Generar insights de marketing analytics
    print("💡 Generando insights de marketing analytics...")
    analytics_insights = analytics_optimizer.generate_analytics_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de marketing analytics...")
    dashboard = analytics_optimizer.create_analytics_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de marketing analytics...")
    export_data = analytics_optimizer.export_analytics_analysis()
    
    print("✅ Sistema de optimización de marketing analytics completado!")






