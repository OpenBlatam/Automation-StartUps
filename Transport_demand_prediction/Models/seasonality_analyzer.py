"""
Modelo Avanzado de Análisis de Estacionalidad para Predicción de Demanda de Transporte
Autor: Sistema de IA Avanzado
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SeasonalityAnalyzer:
    """
    Clase avanzada para análisis de estacionalidad en datos de transporte
    """
    
    def __init__(self, data=None):
        """
        Inicializar el analizador de estacionalidad
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data
        self.seasonal_components = {}
        self.seasonal_patterns = {}
        self.analysis_results = {}
        
    def set_data(self, data):
        """
        Establecer datos para análisis
        
        Args:
            data (pd.DataFrame): DataFrame con datos históricos
        """
        self.data = data.copy()
        print(f"✅ Datos establecidos: {len(self.data)} registros")
        
    def decompose_time_series(self, target_column='demanda_transporte', period=365):
        """
        Descomponer serie temporal en componentes
        
        Args:
            target_column (str): Columna objetivo para análisis
            period (int): Período de estacionalidad (días)
        """
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print(f"🔄 Descomponiendo serie temporal (período: {period} días)...")
        
        # Preparar datos para descomposición
        ts_data = self.data.set_index('fecha')[target_column]
        
        # Realizar descomposición estacional
        decomposition = seasonal_decompose(
            ts_data, 
            model='additive', 
            period=period,
            extrapolate_trend='freq'
        )
        
        # Guardar componentes
        self.seasonal_components = {
            'original': decomposition.observed,
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid
        }
        
        # Calcular métricas de componentes
        seasonal_strength = np.var(decomposition.seasonal) / np.var(decomposition.observed)
        trend_strength = np.var(decomposition.trend) / np.var(decomposition.observed)
        
        self.seasonal_patterns['decomposition_metrics'] = {
            'seasonal_strength': seasonal_strength,
            'trend_strength': trend_strength,
            'residual_strength': 1 - seasonal_strength - trend_strength
        }
        
        print("✅ Descomposición completada")
        return self.seasonal_components
    
    def analyze_seasonal_patterns(self):
        """
        Analizar patrones estacionales detallados
        """
        if not self.seasonal_components:
            self.decompose_time_series()
        
        print("🔍 Analizando patrones estacionales...")
        
        seasonal_data = self.seasonal_components['seasonal']
        
        # Análisis mensual
        monthly_patterns = {}
        for month in range(1, 13):
            month_data = seasonal_data[seasonal_data.index.month == month]
            monthly_patterns[month] = {
                'mean': month_data.mean(),
                'std': month_data.std(),
                'min': month_data.min(),
                'max': month_data.max(),
                'range': month_data.max() - month_data.min()
            }
        
        # Análisis por día de la semana
        weekly_patterns = {}
        for day in range(7):
            day_data = seasonal_data[seasonal_data.index.weekday == day]
            weekly_patterns[day] = {
                'mean': day_data.mean(),
                'std': day_data.std(),
                'min': day_data.min(),
                'max': day_data.max()
            }
        
        # Análisis por trimestre
        quarterly_patterns = {}
        for quarter in range(1, 5):
            quarter_data = seasonal_data[seasonal_data.index.quarter == quarter]
            quarterly_patterns[quarter] = {
                'mean': quarter_data.mean(),
                'std': quarter_data.std(),
                'min': quarter_data.min(),
                'max': quarter_data.max()
            }
        
        # Identificar patrones cíclicos
        cyclic_patterns = self._detect_cyclic_patterns(seasonal_data)
        
        self.seasonal_patterns.update({
            'monthly': monthly_patterns,
            'weekly': weekly_patterns,
            'quarterly': quarterly_patterns,
            'cyclic': cyclic_patterns
        })
        
        print("✅ Análisis de patrones estacionales completado")
        return self.seasonal_patterns
    
    def _detect_cyclic_patterns(self, seasonal_data):
        """
        Detectar patrones cíclicos en los datos estacionales
        """
        # Convertir a array numpy para análisis
        data_array = seasonal_data.dropna().values
        
        # Detectar picos y valles
        peaks, _ = find_peaks(data_array, distance=30)  # Mínimo 30 días entre picos
        valleys, _ = find_peaks(-data_array, distance=30)
        
        # Calcular períodos entre picos
        peak_periods = np.diff(peaks) if len(peaks) > 1 else []
        valley_periods = np.diff(valleys) if len(valleys) > 1 else []
        
        # Análisis de frecuencia usando FFT
        fft = np.fft.fft(data_array)
        freqs = np.fft.fftfreq(len(data_array))
        
        # Encontrar frecuencias dominantes
        dominant_freqs = freqs[np.argsort(np.abs(fft))[-5:]]
        
        cyclic_patterns = {
            'peaks_detected': len(peaks),
            'valleys_detected': len(valleys),
            'avg_peak_period': np.mean(peak_periods) if peak_periods else 0,
            'avg_valley_period': np.mean(valley_periods) if valley_periods else 0,
            'dominant_frequencies': dominant_freqs.tolist(),
            'peak_positions': peaks.tolist(),
            'valley_positions': valleys.tolist()
        }
        
        return cyclic_patterns
    
    def analyze_holiday_effects(self):
        """
        Analizar efectos de días festivos y eventos especiales
        """
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print("🎉 Analizando efectos de días festivos...")
        
        # Análisis de eventos especiales
        normal_days = self.data[self.data['eventos_especiales'] == 0]['demanda_transporte']
        special_days = self.data[self.data['eventos_especiales'] == 1]['demanda_transporte']
        
        if len(special_days) > 0:
            holiday_effect = {
                'normal_days_mean': normal_days.mean(),
                'special_days_mean': special_days.mean(),
                'effect_magnitude': special_days.mean() - normal_days.mean(),
                'effect_percentage': ((special_days.mean() - normal_days.mean()) / normal_days.mean()) * 100,
                'statistical_significance': stats.ttest_ind(normal_days, special_days)[1] < 0.05
            }
        else:
            holiday_effect = {
                'normal_days_mean': normal_days.mean(),
                'special_days_mean': 0,
                'effect_magnitude': 0,
                'effect_percentage': 0,
                'statistical_significance': False
            }
        
        # Análisis de fines de semana
        weekday_demand = self.data[self.data['dia_semana'] < 5]['demanda_transporte']
        weekend_demand = self.data[self.data['dia_semana'] >= 5]['demanda_transporte']
        
        weekend_effect = {
            'weekday_mean': weekday_demand.mean(),
            'weekend_mean': weekend_demand.mean(),
            'weekend_effect': weekend_demand.mean() - weekday_demand.mean(),
            'weekend_percentage': ((weekend_demand.mean() - weekday_demand.mean()) / weekday_demand.mean()) * 100
        }
        
        self.seasonal_patterns['holiday_effects'] = {
            'special_events': holiday_effect,
            'weekend_pattern': weekend_effect
        }
        
        print("✅ Análisis de efectos festivos completado")
        return self.seasonal_patterns['holiday_effects']
    
    def analyze_weather_seasonality(self):
        """
        Analizar estacionalidad relacionada con el clima
        """
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print("🌤️ Analizando estacionalidad climática...")
        
        # Análisis por temperatura
        temp_seasonality = {}
        
        # Dividir en cuartiles de temperatura
        temp_quartiles = pd.qcut(self.data['temperatura'], 4, labels=['Muy Frío', 'Frío', 'Cálido', 'Muy Cálido'])
        
        for quartile in ['Muy Frío', 'Frío', 'Cálido', 'Muy Cálido']:
            quartile_data = self.data[temp_quartiles == quartile]['demanda_transporte']
            temp_seasonality[quartile] = {
                'mean_demand': quartile_data.mean(),
                'std_demand': quartile_data.std(),
                'count': len(quartile_data)
            }
        
        # Análisis de correlación temperatura-demanda por estación
        seasonal_correlations = {}
        for season in range(1, 5):
            season_data = self.data[self.data['trimestre'] == season]
            if len(season_data) > 1:
                corr = season_data['temperatura'].corr(season_data['demanda_transporte'])
                seasonal_correlations[f'Q{season}'] = corr
        
        # Análisis de extremos climáticos
        extreme_cold = self.data[self.data['temperatura'] < self.data['temperatura'].quantile(0.1)]
        extreme_hot = self.data[self.data['temperatura'] > self.data['temperatura'].quantile(0.9)]
        
        weather_extremes = {
            'extreme_cold_demand': extreme_cold['demanda_transporte'].mean() if len(extreme_cold) > 0 else 0,
            'extreme_hot_demand': extreme_hot['demanda_transporte'].mean() if len(extreme_hot) > 0 else 0,
            'normal_weather_demand': self.data[
                (self.data['temperatura'] >= self.data['temperatura'].quantile(0.1)) &
                (self.data['temperatura'] <= self.data['temperatura'].quantile(0.9))
            ]['demanda_transporte'].mean()
        }
        
        self.seasonal_patterns['weather_seasonality'] = {
            'temperature_quartiles': temp_seasonality,
            'seasonal_correlations': seasonal_correlations,
            'weather_extremes': weather_extremes
        }
        
        print("✅ Análisis de estacionalidad climática completado")
        return self.seasonal_patterns['weather_seasonality']
    
    def detect_anomalies(self, method='statistical', threshold=3):
        """
        Detectar anomalías en los patrones estacionales
        
        Args:
            method (str): Método de detección ('statistical', 'isolation_forest')
            threshold (float): Umbral para detección estadística
        """
        if self.data is None:
            raise ValueError("❌ No hay datos establecidos")
        
        print(f"🔍 Detectando anomalías (método: {method})...")
        
        anomalies = {}
        
        if method == 'statistical':
            # Detección estadística usando Z-score
            demand_mean = self.data['demanda_transporte'].mean()
            demand_std = self.data['demanda_transporte'].std()
            
            z_scores = np.abs((self.data['demanda_transporte'] - demand_mean) / demand_std)
            anomaly_mask = z_scores > threshold
            
            anomalies['statistical'] = {
                'anomaly_count': anomaly_mask.sum(),
                'anomaly_percentage': (anomaly_mask.sum() / len(self.data)) * 100,
                'anomaly_dates': self.data[anomaly_mask]['fecha'].tolist(),
                'anomaly_values': self.data[anomaly_mask]['demanda_transporte'].tolist(),
                'threshold_used': threshold
            }
        
        elif method == 'isolation_forest':
            try:
                from sklearn.ensemble import IsolationForest
                
                # Preparar datos para Isolation Forest
                features = ['demanda_transporte', 'temperatura', 'precio_combustible']
                X = self.data[features].fillna(0)
                
                # Entrenar modelo
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(X)
                
                anomaly_mask = anomaly_labels == -1
                
                anomalies['isolation_forest'] = {
                    'anomaly_count': anomaly_mask.sum(),
                    'anomaly_percentage': (anomaly_mask.sum() / len(self.data)) * 100,
                    'anomaly_dates': self.data[anomaly_mask]['fecha'].tolist(),
                    'anomaly_values': self.data[anomaly_mask]['demanda_transporte'].tolist()
                }
            except ImportError:
                print("⚠️ sklearn no disponible, usando método estadístico")
                return self.detect_anomalies(method='statistical', threshold=threshold)
        
        self.seasonal_patterns['anomalies'] = anomalies
        print("✅ Detección de anomalías completada")
        return anomalies
    
    def generate_seasonal_forecast_components(self, forecast_horizon=30):
        """
        Generar componentes estacionales para pronósticos
        
        Args:
            forecast_horizon (int): Horizonte de pronóstico en días
        """
        if not self.seasonal_components:
            self.decompose_time_series()
        
        print(f"🔮 Generando componentes estacionales para pronóstico ({forecast_horizon} días)...")
        
        # Generar fechas futuras
        last_date = self.data['fecha'].max()
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_horizon,
            freq='D'
        )
        
        # Extraer componentes estacionales para fechas futuras
        seasonal_component = self.seasonal_components['seasonal']
        
        # Crear DataFrame para componentes futuros
        future_components = pd.DataFrame({
            'fecha': future_dates,
            'mes': future_dates.month,
            'dia_semana': future_dates.weekday,
            'trimestre': future_dates.quarter
        })
        
        # Calcular componentes estacionales promedio por mes y día
        monthly_seasonal = seasonal_component.groupby(seasonal_component.index.month).mean()
        weekly_seasonal = seasonal_component.groupby(seasonal_component.index.weekday).mean()
        
        # Aplicar componentes a fechas futuras
        future_components['seasonal_component'] = future_components['mes'].map(monthly_seasonal)
        future_components['weekly_component'] = future_components['dia_semana'].map(weekly_seasonal)
        
        # Combinar componentes
        future_components['combined_seasonal'] = (
            future_components['seasonal_component'] + future_components['weekly_component']
        )
        
        self.seasonal_patterns['forecast_components'] = future_components
        
        print("✅ Componentes estacionales para pronóstico generados")
        return future_components
    
    def create_seasonal_visualizations(self, save_path=None):
        """
        Crear visualizaciones específicas de estacionalidad
        """
        if not self.seasonal_patterns:
            self.analyze_seasonal_patterns()
        
        print("📊 Creando visualizaciones de estacionalidad...")
        
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Descomposición estacional
        if self.seasonal_components:
            plt.subplot(4, 4, 1)
            self.seasonal_components['original'].plot(title='Serie Original', alpha=0.7)
            
            plt.subplot(4, 4, 2)
            self.seasonal_components['trend'].plot(title='Tendencia', color='red')
            
            plt.subplot(4, 4, 3)
            self.seasonal_components['seasonal'].plot(title='Componente Estacional', color='green')
            
            plt.subplot(4, 4, 4)
            self.seasonal_components['residual'].plot(title='Residual', color='orange')
        
        # 2. Patrón mensual
        if 'monthly' in self.seasonal_patterns:
            plt.subplot(4, 4, 5)
            monthly_data = self.seasonal_patterns['monthly']
            months = list(monthly_data.keys())
            means = [monthly_data[m]['mean'] for m in months]
            plt.bar(months, means)
            plt.title('Patrón Estacional Mensual')
            plt.xlabel('Mes')
            plt.ylabel('Componente Estacional')
        
        # 3. Patrón semanal
        if 'weekly' in self.seasonal_patterns:
            plt.subplot(4, 4, 6)
            weekly_data = self.seasonal_patterns['weekly']
            days = list(weekly_data.keys())
            means = [weekly_data[d]['mean'] for d in days]
            day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            plt.bar(day_names, means)
            plt.title('Patrón Semanal')
            plt.xlabel('Día de la Semana')
            plt.ylabel('Componente Estacional')
        
        # 4. Efectos de días festivos
        if 'holiday_effects' in self.seasonal_patterns:
            plt.subplot(4, 4, 7)
            holiday_data = self.seasonal_patterns['holiday_effects']
            categories = ['Días Normales', 'Eventos Especiales', 'Días de Semana', 'Fines de Semana']
            values = [
                holiday_data['special_events']['normal_days_mean'],
                holiday_data['special_events']['special_days_mean'],
                holiday_data['weekend_pattern']['weekday_mean'],
                holiday_data['weekend_pattern']['weekend_mean']
            ]
            plt.bar(categories, values)
            plt.title('Efectos de Días Especiales')
            plt.xticks(rotation=45)
            plt.ylabel('Demanda Promedio')
        
        # 5. Estacionalidad climática
        if 'weather_seasonality' in self.seasonal_patterns:
            plt.subplot(4, 4, 8)
            weather_data = self.seasonal_patterns['weather_seasonality']['temperature_quartiles']
            temp_categories = list(weather_data.keys())
            demands = [weather_data[t]['mean_demand'] for t in temp_categories]
            plt.bar(temp_categories, demands)
            plt.title('Demanda por Temperatura')
            plt.xlabel('Categoría de Temperatura')
            plt.ylabel('Demanda Promedio')
            plt.xticks(rotation=45)
        
        # 6. Anomalías detectadas
        if 'anomalies' in self.seasonal_patterns:
            plt.subplot(4, 4, 9)
            anomaly_data = self.seasonal_patterns['anomalies']
            if 'statistical' in anomaly_data:
                plt.scatter(self.data['fecha'], self.data['demanda_transporte'], alpha=0.5, label='Normal')
                anomaly_dates = pd.to_datetime(anomaly_data['statistical']['anomaly_dates'])
                anomaly_values = anomaly_data['statistical']['anomaly_values']
                plt.scatter(anomaly_dates, anomaly_values, color='red', label='Anomalías')
                plt.title('Detección de Anomalías')
                plt.xlabel('Fecha')
                plt.ylabel('Demanda')
                plt.legend()
        
        # 7. Componentes para pronóstico
        if 'forecast_components' in self.seasonal_patterns:
            plt.subplot(4, 4, 10)
            forecast_data = self.seasonal_patterns['forecast_components']
            plt.plot(forecast_data['fecha'], forecast_data['combined_seasonal'])
            plt.title('Componentes Estacionales Futuros')
            plt.xlabel('Fecha')
            plt.ylabel('Componente Estacional')
            plt.xticks(rotation=45)
        
        # 8. Heatmap de estacionalidad
        plt.subplot(4, 4, 11)
        if self.data is not None:
            # Crear matriz de estacionalidad (mes vs día de semana)
            seasonal_matrix = self.data.groupby(['mes', 'dia_semana'])['demanda_transporte'].mean().unstack()
            sns.heatmap(seasonal_matrix, annot=True, fmt='.0f', cmap='YlOrRd')
            plt.title('Heatmap Estacionalidad')
            plt.xlabel('Día de la Semana')
            plt.ylabel('Mes')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Visualizaciones de estacionalidad guardadas en: {save_path}")
        
        plt.show()
        print("✅ Visualizaciones de estacionalidad creadas")
    
    def export_seasonal_analysis(self, output_path='seasonal_analysis.json'):
        """
        Exportar análisis de estacionalidad
        """
        import json
        
        # Preparar datos para exportación
        export_data = {
            'metadata': {
                'fecha_analisis': datetime.now().isoformat(),
                'total_registros': len(self.data) if self.data is not None else 0,
                'metodos_aplicados': list(self.seasonal_patterns.keys())
            },
            'seasonal_patterns': self.seasonal_patterns,
            'decomposition_metrics': self.seasonal_patterns.get('decomposition_metrics', {}),
            'summary': {
                'seasonal_strength': self.seasonal_patterns.get('decomposition_metrics', {}).get('seasonal_strength', 0),
                'trend_strength': self.seasonal_patterns.get('decomposition_metrics', {}).get('trend_strength', 0),
                'anomalies_detected': self.seasonal_patterns.get('anomalies', {}).get('statistical', {}).get('anomaly_count', 0)
            }
        }
        
        # Limpiar datos para JSON
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.ndarray, pd.Series)):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            return obj
        
        export_data = clean_for_json(export_data)
        
        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Análisis de estacionalidad exportado a: {output_path}")
        return export_data

# Función principal para demostración
def main():
    """
    Función principal para demostrar el uso del analizador de estacionalidad
    """
    print("🔄 Iniciando Análisis de Estacionalidad Avanzado")
    print("=" * 60)
    
    # Crear datos de ejemplo
    from historical_data_analyzer import HistoricalDataAnalyzer
    
    # Crear analizador histórico
    historical_analyzer = HistoricalDataAnalyzer()
    historical_analyzer.load_data()
    historical_analyzer.preprocess_data()
    
    # Crear analizador de estacionalidad
    seasonal_analyzer = SeasonalityAnalyzer(historical_analyzer.processed_data)
    
    # Realizar análisis completos
    print("\n🔄 Realizando análisis de estacionalidad...")
    seasonal_analyzer.decompose_time_series()
    seasonal_analyzer.analyze_seasonal_patterns()
    seasonal_analyzer.analyze_holiday_effects()
    seasonal_analyzer.analyze_weather_seasonality()
    seasonal_analyzer.detect_anomalies()
    seasonal_analyzer.generate_seasonal_forecast_components()
    
    # Crear visualizaciones
    print("\n📊 Creando visualizaciones de estacionalidad...")
    seasonal_analyzer.create_seasonal_visualizations('seasonal_analysis.png')
    
    # Exportar resultados
    print("\n💾 Exportando análisis de estacionalidad...")
    seasonal_analyzer.export_seasonal_analysis('seasonal_analysis_results.json')
    
    print("\n✅ Análisis de estacionalidad completado exitosamente!")
    print("=" * 60)

if __name__ == "__main__":
    main()



