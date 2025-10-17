"""
Marketing Brain Marketing Attribution Analyzer
Sistema avanzado de análisis de marketing attribution
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

class MarketingAttributionAnalyzer:
    def __init__(self):
        self.attribution_data = {}
        self.attribution_models = {}
        self.touchpoint_analysis = {}
        self.journey_analysis = {}
        self.attribution_insights = {}
        self.optimization_recommendations = {}
        
    def load_attribution_data(self, attribution_data):
        """Cargar datos de marketing attribution"""
        if isinstance(attribution_data, str):
            if attribution_data.endswith('.csv'):
                self.attribution_data = pd.read_csv(attribution_data)
            elif attribution_data.endswith('.json'):
                with open(attribution_data, 'r') as f:
                    data = json.load(f)
                self.attribution_data = pd.DataFrame(data)
        else:
            self.attribution_data = pd.DataFrame(attribution_data)
        
        print(f"✅ Datos de marketing attribution cargados: {len(self.attribution_data)} registros")
        return True
    
    def analyze_attribution_models(self):
        """Analizar modelos de attribution"""
        if self.attribution_data.empty:
            return None
        
        # Análisis de modelos de attribution
        attribution_models = {}
        
        # Modelo de First Click
        first_click_analysis = self._analyze_first_click_attribution()
        attribution_models['first_click'] = first_click_analysis
        
        # Modelo de Last Click
        last_click_analysis = self._analyze_last_click_attribution()
        attribution_models['last_click'] = last_click_analysis
        
        # Modelo de Linear
        linear_analysis = self._analyze_linear_attribution()
        attribution_models['linear'] = linear_analysis
        
        # Modelo de Time Decay
        time_decay_analysis = self._analyze_time_decay_attribution()
        attribution_models['time_decay'] = time_decay_analysis
        
        # Modelo de Position Based
        position_based_analysis = self._analyze_position_based_attribution()
        attribution_models['position_based'] = position_based_analysis
        
        # Modelo de Data Driven
        data_driven_analysis = self._analyze_data_driven_attribution()
        attribution_models['data_driven'] = data_driven_analysis
        
        # Comparación de modelos
        model_comparison = self._compare_attribution_models(attribution_models)
        attribution_models['model_comparison'] = model_comparison
        
        self.attribution_models = attribution_models
        return attribution_models
    
    def _analyze_first_click_attribution(self):
        """Analizar attribution de primer clic"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution de primer clic
        first_click_attribution = {}
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            if touchpoints:
                first_touchpoint = touchpoints[0]
                if first_touchpoint not in first_click_attribution:
                    first_click_attribution[first_touchpoint] = {
                        'conversions': 0,
                        'revenue': 0,
                        'customers': 0
                    }
                
                first_click_attribution[first_touchpoint]['conversions'] += customer['conversion']
                first_click_attribution[first_touchpoint]['revenue'] += customer['revenue']
                first_click_attribution[first_touchpoint]['customers'] += 1
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in first_click_attribution.values())
        total_revenue = sum(data['revenue'] for data in first_click_attribution.values())
        
        for touchpoint, data in first_click_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
            data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
        
        return {
            'attribution_data': first_click_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'first_click'
        }
    
    def _analyze_last_click_attribution(self):
        """Analizar attribution de último clic"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution de último clic
        last_click_attribution = {}
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            if touchpoints:
                last_touchpoint = touchpoints[-1]
                if last_touchpoint not in last_click_attribution:
                    last_click_attribution[last_touchpoint] = {
                        'conversions': 0,
                        'revenue': 0,
                        'customers': 0
                    }
                
                last_click_attribution[last_touchpoint]['conversions'] += customer['conversion']
                last_click_attribution[last_touchpoint]['revenue'] += customer['revenue']
                last_click_attribution[last_touchpoint]['customers'] += 1
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in last_click_attribution.values())
        total_revenue = sum(data['revenue'] for data in last_click_attribution.values())
        
        for touchpoint, data in last_click_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
            data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
        
        return {
            'attribution_data': last_click_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'last_click'
        }
    
    def _analyze_linear_attribution(self):
        """Analizar attribution lineal"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution lineal
        linear_attribution = {}
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            if touchpoints:
                # Distribuir crédito equitativamente entre todos los touchpoints
                credit_per_touchpoint = 1.0 / len(touchpoints)
                
                for touchpoint in touchpoints:
                    if touchpoint not in linear_attribution:
                        linear_attribution[touchpoint] = {
                            'conversions': 0,
                            'revenue': 0,
                            'customers': 0
                        }
                    
                    linear_attribution[touchpoint]['conversions'] += customer['conversion'] * credit_per_touchpoint
                    linear_attribution[touchpoint]['revenue'] += customer['revenue'] * credit_per_touchpoint
                    linear_attribution[touchpoint]['customers'] += 1
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in linear_attribution.values())
        total_revenue = sum(data['revenue'] for data in linear_attribution.values())
        
        for touchpoint, data in linear_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
            data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
        
        return {
            'attribution_data': linear_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'linear'
        }
    
    def _analyze_time_decay_attribution(self):
        """Analizar attribution con decaimiento temporal"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns or 'timestamp' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer con timestamps
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'timestamp': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution con decaimiento temporal
        time_decay_attribution = {}
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            timestamps = customer['timestamp']
            
            if touchpoints and timestamps:
                # Convertir timestamps a datetime
                timestamps = [pd.to_datetime(ts) for ts in timestamps]
                
                # Calcular pesos con decaimiento temporal
                max_timestamp = max(timestamps)
                weights = []
                
                for ts in timestamps:
                    # Calcular días desde el último touchpoint
                    days_diff = (max_timestamp - ts).days
                    # Aplicar decaimiento exponencial (factor de 0.5 por día)
                    weight = 0.5 ** days_diff
                    weights.append(weight)
                
                # Normalizar pesos
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                
                # Distribuir crédito
                for touchpoint, weight in zip(touchpoints, normalized_weights):
                    if touchpoint not in time_decay_attribution:
                        time_decay_attribution[touchpoint] = {
                            'conversions': 0,
                            'revenue': 0,
                            'customers': 0
                        }
                    
                    time_decay_attribution[touchpoint]['conversions'] += customer['conversion'] * weight
                    time_decay_attribution[touchpoint]['revenue'] += customer['revenue'] * weight
                    time_decay_attribution[touchpoint]['customers'] += 1
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in time_decay_attribution.values())
        total_revenue = sum(data['revenue'] for data in time_decay_attribution.values())
        
        for touchpoint, data in time_decay_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
            data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
        
        return {
            'attribution_data': time_decay_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'time_decay'
        }
    
    def _analyze_position_based_attribution(self):
        """Analizar attribution basado en posición"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution basado en posición
        position_based_attribution = {}
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            if touchpoints:
                # Asignar pesos basados en posición
                weights = []
                for i, touchpoint in enumerate(touchpoints):
                    if i == 0:  # Primer touchpoint
                        weight = 0.4
                    elif i == len(touchpoints) - 1:  # Último touchpoint
                        weight = 0.4
                    else:  # Touchpoints intermedios
                        weight = 0.2 / (len(touchpoints) - 2) if len(touchpoints) > 2 else 0.2
                    
                    weights.append(weight)
                
                # Distribuir crédito
                for touchpoint, weight in zip(touchpoints, weights):
                    if touchpoint not in position_based_attribution:
                        position_based_attribution[touchpoint] = {
                            'conversions': 0,
                            'revenue': 0,
                            'customers': 0
                        }
                    
                    position_based_attribution[touchpoint]['conversions'] += customer['conversion'] * weight
                    position_based_attribution[touchpoint]['revenue'] += customer['revenue'] * weight
                    position_based_attribution[touchpoint]['customers'] += 1
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in position_based_attribution.values())
        total_revenue = sum(data['revenue'] for data in position_based_attribution.values())
        
        for touchpoint, data in position_based_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
            data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
        
        return {
            'attribution_data': position_based_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'position_based'
        }
    
    def _analyze_data_driven_attribution(self):
        """Analizar attribution basado en datos"""
        if 'customer_id' not in self.attribution_data.columns or 'touchpoint' not in self.attribution_data.columns:
            return {}
        
        # Crear secuencias de touchpoints por customer
        customer_sequences = self.attribution_data.groupby('customer_id').agg({
            'touchpoint': lambda x: list(x),
            'conversion': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calcular attribution basado en datos usando algoritmo de Shapley
        data_driven_attribution = {}
        
        # Crear matriz de touchpoints únicos
        all_touchpoints = set()
        for _, customer in customer_sequences.iterrows():
            all_touchpoints.update(customer['touchpoint'])
        
        all_touchpoints = list(all_touchpoints)
        
        # Calcular valores de Shapley para cada touchpoint
        for touchpoint in all_touchpoints:
            shapley_value = 0
            
            # Calcular contribución marginal para cada subconjunto
            for subset_size in range(len(all_touchpoints)):
                for subset in self._get_subsets_of_size(all_touchpoints, subset_size):
                    if touchpoint not in subset:
                        # Calcular valor con y sin el touchpoint
                        value_with = self._calculate_subset_value(subset + [touchpoint], customer_sequences)
                        value_without = self._calculate_subset_value(subset, customer_sequences)
                        
                        # Contribución marginal
                        marginal_contribution = value_with - value_without
                        
                        # Peso de Shapley
                        weight = 1.0 / (len(all_touchpoints) * self._binomial_coefficient(len(all_touchpoints) - 1, len(subset)))
                        
                        shapley_value += weight * marginal_contribution
            
            data_driven_attribution[touchpoint] = {
                'conversions': shapley_value,
                'revenue': shapley_value * 100,  # Asumir revenue promedio
                'customers': 1,
                'conversion_share': 0,
                'revenue_share': 0,
                'avg_revenue_per_customer': shapley_value * 100
            }
        
        # Calcular métricas
        total_conversions = sum(data['conversions'] for data in data_driven_attribution.values())
        total_revenue = sum(data['revenue'] for data in data_driven_attribution.values())
        
        for touchpoint, data in data_driven_attribution.items():
            data['conversion_share'] = (data['conversions'] / total_conversions) * 100 if total_conversions > 0 else 0
            data['revenue_share'] = (data['revenue'] / total_revenue) * 100 if total_revenue > 0 else 0
        
        return {
            'attribution_data': data_driven_attribution,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'model_type': 'data_driven'
        }
    
    def _get_subsets_of_size(self, items, size):
        """Obtener subconjuntos de un tamaño específico"""
        if size == 0:
            return [[]]
        if size > len(items):
            return []
        
        subsets = []
        for i in range(len(items)):
            for subset in self._get_subsets_of_size(items[i+1:], size-1):
                subsets.append([items[i]] + subset)
        
        return subsets
    
    def _calculate_subset_value(self, subset, customer_sequences):
        """Calcular valor de un subconjunto de touchpoints"""
        total_value = 0
        
        for _, customer in customer_sequences.iterrows():
            touchpoints = customer['touchpoint']
            if any(tp in subset for tp in touchpoints):
                total_value += customer['conversion']
        
        return total_value
    
    def _binomial_coefficient(self, n, k):
        """Calcular coeficiente binomial"""
        if k > n or k < 0:
            return 0
        if k == 0 or k == n:
            return 1
        
        result = 1
        for i in range(min(k, n - k)):
            result = result * (n - i) // (i + 1)
        
        return result
    
    def _compare_attribution_models(self, attribution_models):
        """Comparar modelos de attribution"""
        comparison = {}
        
        for model_name, model_data in attribution_models.items():
            if model_name != 'model_comparison':
                attribution_data = model_data.get('attribution_data', {})
                
                # Calcular métricas de comparación
                total_touchpoints = len(attribution_data)
                max_conversion_share = max(data.get('conversion_share', 0) for data in attribution_data.values()) if attribution_data else 0
                min_conversion_share = min(data.get('conversion_share', 0) for data in attribution_data.values()) if attribution_data else 0
                conversion_share_variance = np.var([data.get('conversion_share', 0) for data in attribution_data.values()]) if attribution_data else 0
                
                comparison[model_name] = {
                    'total_touchpoints': total_touchpoints,
                    'max_conversion_share': max_conversion_share,
                    'min_conversion_share': min_conversion_share,
                    'conversion_share_variance': conversion_share_variance,
                    'total_conversions': model_data.get('total_conversions', 0),
                    'total_revenue': model_data.get('total_revenue', 0)
                }
        
        return comparison
    
    def analyze_touchpoint_attribution(self):
        """Analizar attribution de touchpoints"""
        if self.attribution_data.empty:
            return None
        
        # Análisis de touchpoints
        touchpoint_analysis = {}
        
        # Análisis de touchpoints por tipo
        if 'touchpoint_type' in self.attribution_data.columns:
            type_analysis = self.attribution_data.groupby('touchpoint_type').agg({
                'conversion': 'sum',
                'revenue': 'sum',
                'customer_id': 'nunique'
            }).reset_index()
            
            type_analysis['conversion_rate'] = (type_analysis['conversion'] / type_analysis['customer_id']) * 100
            type_analysis['avg_revenue_per_customer'] = type_analysis['revenue'] / type_analysis['customer_id']
            
            touchpoint_analysis['type_analysis'] = type_analysis.to_dict('records')
        
        # Análisis de touchpoints por canal
        if 'channel' in self.attribution_data.columns:
            channel_analysis = self.attribution_data.groupby('channel').agg({
                'conversion': 'sum',
                'revenue': 'sum',
                'customer_id': 'nunique'
            }).reset_index()
            
            channel_analysis['conversion_rate'] = (channel_analysis['conversion'] / channel_analysis['customer_id']) * 100
            channel_analysis['avg_revenue_per_customer'] = channel_analysis['revenue'] / channel_analysis['customer_id']
            
            touchpoint_analysis['channel_analysis'] = channel_analysis.to_dict('records')
        
        # Análisis de touchpoints por posición
        position_analysis = self._analyze_touchpoint_positions()
        touchpoint_analysis['position_analysis'] = position_analysis
        
        # Análisis de touchpoints por timing
        timing_analysis = self._analyze_touchpoint_timing()
        touchpoint_analysis['timing_analysis'] = timing_analysis
        
        self.touchpoint_analysis = touchpoint_analysis
        return touchpoint_analysis
    
    def _analyze_touchpoint_positions(self):
        """Analizar posiciones de touchpoints"""
        position_analysis = {}
        
        if 'customer_id' in self.attribution_data.columns and 'touchpoint' in self.attribution_data.columns:
            # Crear secuencias de touchpoints por customer
            customer_sequences = self.attribution_data.groupby('customer_id').agg({
                'touchpoint': lambda x: list(x),
                'conversion': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Análisis por posición
            position_data = {}
            for _, customer in customer_sequences.iterrows():
                touchpoints = customer['touchpoint']
                for i, touchpoint in enumerate(touchpoints):
                    position = i + 1
                    if position not in position_data:
                        position_data[position] = {
                            'touchpoints': [],
                            'conversions': 0,
                            'revenue': 0,
                            'customers': 0
                        }
                    
                    position_data[position]['touchpoints'].append(touchpoint)
                    position_data[position]['conversions'] += customer['conversion']
                    position_data[position]['revenue'] += customer['revenue']
                    position_data[position]['customers'] += 1
            
            # Calcular métricas por posición
            for position, data in position_data.items():
                data['conversion_rate'] = (data['conversions'] / data['customers']) * 100 if data['customers'] > 0 else 0
                data['avg_revenue_per_customer'] = data['revenue'] / data['customers'] if data['customers'] > 0 else 0
                data['touchpoint_frequency'] = len(data['touchpoints'])
                
                # Análisis de touchpoints más comunes en esta posición
                touchpoint_counts = pd.Series(data['touchpoints']).value_counts()
                data['top_touchpoints'] = touchpoint_counts.head(5).to_dict()
            
            position_analysis = position_data
        
        return position_analysis
    
    def _analyze_touchpoint_timing(self):
        """Analizar timing de touchpoints"""
        timing_analysis = {}
        
        if 'timestamp' in self.attribution_data.columns:
            # Análisis de timing por día de la semana
            self.attribution_data['timestamp'] = pd.to_datetime(self.attribution_data['timestamp'])
            self.attribution_data['day_of_week'] = self.attribution_data['timestamp'].dt.day_name()
            
            daily_timing = self.attribution_data.groupby('day_of_week').agg({
                'conversion': 'sum',
                'revenue': 'sum',
                'customer_id': 'nunique'
            }).reset_index()
            
            daily_timing['conversion_rate'] = (daily_timing['conversion'] / daily_timing['customer_id']) * 100
            daily_timing['avg_revenue_per_customer'] = daily_timing['revenue'] / daily_timing['customer_id']
            
            # Análisis de timing por hora del día
            self.attribution_data['hour'] = self.attribution_data['timestamp'].dt.hour
            
            hourly_timing = self.attribution_data.groupby('hour').agg({
                'conversion': 'sum',
                'revenue': 'sum',
                'customer_id': 'nunique'
            }).reset_index()
            
            hourly_timing['conversion_rate'] = (hourly_timing['conversion'] / hourly_timing['customer_id']) * 100
            hourly_timing['avg_revenue_per_customer'] = hourly_timing['revenue'] / hourly_timing['customer_id']
            
            timing_analysis = {
                'daily_timing': daily_timing.to_dict('records'),
                'hourly_timing': hourly_timing.to_dict('records'),
                'best_day': daily_timing.loc[daily_timing['conversion_rate'].idxmax(), 'day_of_week'],
                'best_hour': hourly_timing.loc[hourly_timing['conversion_rate'].idxmax(), 'hour']
            }
        
        return timing_analysis
    
    def analyze_customer_journey_attribution(self):
        """Analizar attribution del customer journey"""
        if self.attribution_data.empty:
            return None
        
        # Análisis del customer journey
        journey_analysis = {}
        
        # Análisis de longitud del journey
        journey_length_analysis = self._analyze_journey_length()
        journey_analysis['journey_length'] = journey_length_analysis
        
        # Análisis de patrones de journey
        journey_patterns_analysis = self._analyze_journey_patterns()
        journey_analysis['journey_patterns'] = journey_patterns_analysis
        
        # Análisis de touchpoints críticos
        critical_touchpoints_analysis = self._analyze_critical_touchpoints()
        journey_analysis['critical_touchpoints'] = critical_touchpoints_analysis
        
        # Análisis de conversión por journey
        conversion_journey_analysis = self._analyze_conversion_journey()
        journey_analysis['conversion_journey'] = conversion_journey_analysis
        
        self.journey_analysis = journey_analysis
        return journey_analysis
    
    def _analyze_journey_length(self):
        """Analizar longitud del journey"""
        journey_length_analysis = {}
        
        if 'customer_id' in self.attribution_data.columns:
            # Calcular longitud del journey por customer
            journey_lengths = self.attribution_data.groupby('customer_id').size()
            
            journey_length_analysis = {
                'avg_journey_length': journey_lengths.mean(),
                'median_journey_length': journey_lengths.median(),
                'max_journey_length': journey_lengths.max(),
                'min_journey_length': journey_lengths.min(),
                'journey_length_distribution': journey_lengths.value_counts().to_dict()
            }
        
        return journey_length_analysis
    
    def _analyze_journey_patterns(self):
        """Analizar patrones de journey"""
        journey_patterns_analysis = {}
        
        if 'customer_id' in self.attribution_data.columns and 'touchpoint' in self.attribution_data.columns:
            # Crear secuencias de touchpoints por customer
            customer_sequences = self.attribution_data.groupby('customer_id').agg({
                'touchpoint': lambda x: list(x),
                'conversion': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Análisis de patrones comunes
            pattern_counts = {}
            for _, customer in customer_sequences.iterrows():
                touchpoints = customer['touchpoint']
                if len(touchpoints) >= 2:
                    # Crear patrones de 2 touchpoints
                    for i in range(len(touchpoints) - 1):
                        pattern = f"{touchpoints[i]} -> {touchpoints[i+1]}"
                        if pattern not in pattern_counts:
                            pattern_counts[pattern] = {
                                'count': 0,
                                'conversions': 0,
                                'revenue': 0
                            }
                        
                        pattern_counts[pattern]['count'] += 1
                        pattern_counts[pattern]['conversions'] += customer['conversion']
                        pattern_counts[pattern]['revenue'] += customer['revenue']
            
            # Ordenar patrones por frecuencia
            top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
            
            journey_patterns_analysis = {
                'top_patterns': top_patterns,
                'total_patterns': len(pattern_counts),
                'pattern_diversity': len(pattern_counts) / len(customer_sequences) if len(customer_sequences) > 0 else 0
            }
        
        return journey_patterns_analysis
    
    def _analyze_critical_touchpoints(self):
        """Analizar touchpoints críticos"""
        critical_touchpoints_analysis = {}
        
        if 'customer_id' in self.attribution_data.columns and 'touchpoint' in self.attribution_data.columns:
            # Crear secuencias de touchpoints por customer
            customer_sequences = self.attribution_data.groupby('customer_id').agg({
                'touchpoint': lambda x: list(x),
                'conversion': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Análisis de touchpoints críticos
            touchpoint_importance = {}
            for _, customer in customer_sequences.iterrows():
                touchpoints = customer['touchpoint']
                if touchpoints:
                    for touchpoint in touchpoints:
                        if touchpoint not in touchpoint_importance:
                            touchpoint_importance[touchpoint] = {
                                'appearances': 0,
                                'conversions': 0,
                                'revenue': 0,
                                'journey_lengths': []
                            }
                        
                        touchpoint_importance[touchpoint]['appearances'] += 1
                        touchpoint_importance[touchpoint]['conversions'] += customer['conversion']
                        touchpoint_importance[touchpoint]['revenue'] += customer['revenue']
                        touchpoint_importance[touchpoint]['journey_lengths'].append(len(touchpoints))
            
            # Calcular métricas de importancia
            for touchpoint, data in touchpoint_importance.items():
                data['conversion_rate'] = (data['conversions'] / data['appearances']) * 100
                data['avg_revenue_per_appearance'] = data['revenue'] / data['appearances']
                data['avg_journey_length'] = np.mean(data['journey_lengths'])
                data['importance_score'] = data['conversion_rate'] * data['avg_revenue_per_appearance']
            
            # Ordenar por importancia
            top_critical_touchpoints = sorted(touchpoint_importance.items(), key=lambda x: x[1]['importance_score'], reverse=True)[:10]
            
            critical_touchpoints_analysis = {
                'top_critical_touchpoints': top_critical_touchpoints,
                'touchpoint_importance': touchpoint_importance
            }
        
        return critical_touchpoints_analysis
    
    def _analyze_conversion_journey(self):
        """Analizar conversión por journey"""
        conversion_journey_analysis = {}
        
        if 'customer_id' in self.attribution_data.columns and 'touchpoint' in self.attribution_data.columns:
            # Crear secuencias de touchpoints por customer
            customer_sequences = self.attribution_data.groupby('customer_id').agg({
                'touchpoint': lambda x: list(x),
                'conversion': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            # Análisis de conversión por longitud de journey
            conversion_by_length = {}
            for _, customer in customer_sequences.iterrows():
                journey_length = len(customer['touchpoint'])
                if journey_length not in conversion_by_length:
                    conversion_by_length[journey_length] = {
                        'total_customers': 0,
                        'conversions': 0,
                        'revenue': 0
                    }
                
                conversion_by_length[journey_length]['total_customers'] += 1
                conversion_by_length[journey_length]['conversions'] += customer['conversion']
                conversion_by_length[journey_length]['revenue'] += customer['revenue']
            
            # Calcular métricas
            for length, data in conversion_by_length.items():
                data['conversion_rate'] = (data['conversions'] / data['total_customers']) * 100
                data['avg_revenue_per_customer'] = data['revenue'] / data['total_customers']
            
            conversion_journey_analysis = {
                'conversion_by_length': conversion_by_length,
                'optimal_journey_length': max(conversion_by_length.items(), key=lambda x: x[1]['conversion_rate'])[0] if conversion_by_length else 0
            }
        
        return conversion_journey_analysis
    
    def generate_attribution_insights(self):
        """Generar insights de attribution"""
        insights = []
        
        # Insights de modelos de attribution
        if self.attribution_models:
            model_comparison = self.attribution_models.get('model_comparison', {})
            
            if model_comparison:
                # Identificar modelo con mayor varianza
                max_variance_model = max(model_comparison.items(), key=lambda x: x[1].get('conversion_share_variance', 0))
                insights.append({
                    'category': 'Attribution Models',
                    'insight': f'Modelo {max_variance_model[0]} tiene la mayor varianza en attribution',
                    'recommendation': 'Considerar usar este modelo para identificar touchpoints más influyentes',
                    'priority': 'medium'
                })
        
        # Insights de touchpoints
        if self.touchpoint_analysis:
            type_analysis = self.touchpoint_analysis.get('type_analysis', [])
            
            if type_analysis:
                # Identificar tipo de touchpoint más efectivo
                best_touchpoint_type = max(type_analysis, key=lambda x: x['conversion_rate'])
                insights.append({
                    'category': 'Touchpoint Performance',
                    'insight': f'Mejor tipo de touchpoint: {best_touchpoint_type["touchpoint_type"]} con {best_touchpoint_type["conversion_rate"]:.1f}% conversion rate',
                    'recommendation': 'Aumentar inversión en este tipo de touchpoint',
                    'priority': 'high'
                })
        
        # Insights de customer journey
        if self.journey_analysis:
            journey_length = self.journey_analysis.get('journey_length', {})
            avg_journey_length = journey_length.get('avg_journey_length', 0)
            
            if avg_journey_length > 5:
                insights.append({
                    'category': 'Customer Journey',
                    'insight': f'Journey promedio largo: {avg_journey_length:.1f} touchpoints',
                    'recommendation': 'Optimizar journey para reducir fricción',
                    'priority': 'medium'
                })
            
            critical_touchpoints = self.journey_analysis.get('critical_touchpoints', {})
            top_critical = critical_touchpoints.get('top_critical_touchpoints', [])
            
            if top_critical:
                insights.append({
                    'category': 'Critical Touchpoints',
                    'insight': f'Touchpoint más crítico: {top_critical[0][0]} con score de {top_critical[0][1]["importance_score"]:.2f}',
                    'recommendation': 'Priorizar este touchpoint en estrategias de marketing',
                    'priority': 'high'
                })
        
        # Insights de timing
        if self.touchpoint_analysis:
            timing_analysis = self.touchpoint_analysis.get('timing_analysis', {})
            best_day = timing_analysis.get('best_day')
            best_hour = timing_analysis.get('best_hour')
            
            if best_day and best_hour:
                insights.append({
                    'category': 'Touchpoint Timing',
                    'insight': f'Mejor momento para touchpoints: {best_day} a las {best_hour}:00',
                    'recommendation': 'Optimizar timing de campañas',
                    'priority': 'low'
                })
        
        self.attribution_insights = insights
        return insights
    
    def create_attribution_dashboard(self):
        """Crear dashboard de marketing attribution"""
        if not self.attribution_data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Attribution Models Comparison', 'Touchpoint Performance',
                          'Customer Journey Length', 'Critical Touchpoints'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # Gráfico de comparación de modelos de attribution
        if self.attribution_models:
            model_comparison = self.attribution_models.get('model_comparison', {})
            if model_comparison:
                models = list(model_comparison.keys())
                conversion_shares = [model_comparison[model]['max_conversion_share'] for model in models]
                
                fig.add_trace(
                    go.Bar(x=models, y=conversion_shares, name='Max Conversion Share by Model'),
                    row=1, col=1
                )
        
        # Gráfico de performance de touchpoints
        if self.touchpoint_analysis:
            type_analysis = self.touchpoint_analysis.get('type_analysis', [])
            if type_analysis:
                touchpoint_types = [tp['touchpoint_type'] for tp in type_analysis]
                conversion_rates = [tp['conversion_rate'] for tp in type_analysis]
                
                fig.add_trace(
                    go.Pie(labels=touchpoint_types, values=conversion_rates, name='Touchpoint Performance'),
                    row=1, col=2
                )
        
        # Gráfico de longitud del customer journey
        if self.journey_analysis:
            journey_length = self.journey_analysis.get('journey_length', {})
            length_distribution = journey_length.get('journey_length_distribution', {})
            
            if length_distribution:
                lengths = list(length_distribution.keys())
                counts = list(length_distribution.values())
                
                fig.add_trace(
                    go.Histogram(x=lengths, y=counts, name='Journey Length Distribution'),
                    row=2, col=1
                )
        
        # Gráfico de touchpoints críticos
        if self.journey_analysis:
            critical_touchpoints = self.journey_analysis.get('critical_touchpoints', {})
            top_critical = critical_touchpoints.get('top_critical_touchpoints', [])
            
            if top_critical:
                touchpoints = [tp[0] for tp in top_critical[:5]]
                importance_scores = [tp[1]['importance_score'] for tp in top_critical[:5]]
                
                fig.add_trace(
                    go.Bar(x=touchpoints, y=importance_scores, name='Critical Touchpoints'),
                    row=2, col=2
                )
        
        fig.update_layout(
            title="Dashboard de Marketing Attribution",
            showlegend=False,
            height=800
        )
        
        return fig
    
    def export_attribution_analysis(self, filename='marketing_attribution_analysis.json'):
        """Exportar análisis de marketing attribution"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'attribution_models': self.attribution_models,
            'touchpoint_analysis': self.touchpoint_analysis,
            'journey_analysis': self.journey_analysis,
            'attribution_insights': self.attribution_insights,
            'summary': {
                'total_customers': len(self.attribution_data['customer_id'].unique()) if 'customer_id' in self.attribution_data.columns else 0,
                'total_touchpoints': len(self.attribution_data['touchpoint'].unique()) if 'touchpoint' in self.attribution_data.columns else 0,
                'analysis_date': datetime.now().isoformat()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Análisis de marketing attribution exportado a {filename}")
        return export_data

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del analizador de marketing attribution
    attribution_analyzer = MarketingAttributionAnalyzer()
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        'customer_id': np.random.randint(1, 500, 2000),
        'touchpoint': np.random.choice(['Email', 'Social Media', 'Website', 'Paid Search', 'Display', 'Direct'], 2000),
        'touchpoint_type': np.random.choice(['Paid', 'Organic', 'Direct', 'Referral'], 2000),
        'channel': np.random.choice(['Digital', 'Email', 'Social', 'Search', 'Display'], 2000),
        'conversion': np.random.choice([0, 1], 2000, p=[0.8, 0.2]),
        'revenue': np.random.normal(100, 50, 2000),
        'timestamp': pd.date_range('2023-01-01', periods=2000, freq='H')
    })
    
    # Cargar datos de marketing attribution
    print("📊 Cargando datos de marketing attribution...")
    attribution_analyzer.load_attribution_data(sample_data)
    
    # Analizar modelos de attribution
    print("🎯 Analizando modelos de attribution...")
    attribution_models = attribution_analyzer.analyze_attribution_models()
    
    # Analizar attribution de touchpoints
    print("📍 Analizando attribution de touchpoints...")
    touchpoint_analysis = attribution_analyzer.analyze_touchpoint_attribution()
    
    # Analizar attribution del customer journey
    print("🛤️ Analizando attribution del customer journey...")
    journey_analysis = attribution_analyzer.analyze_customer_journey_attribution()
    
    # Generar insights de attribution
    print("💡 Generando insights de attribution...")
    attribution_insights = attribution_analyzer.generate_attribution_insights()
    
    # Crear dashboard
    print("📊 Creando dashboard de marketing attribution...")
    dashboard = attribution_analyzer.create_attribution_dashboard()
    
    # Exportar análisis
    print("💾 Exportando análisis de marketing attribution...")
    export_data = attribution_analyzer.export_attribution_analysis()
    
    print("✅ Sistema de análisis de marketing attribution completado!")






