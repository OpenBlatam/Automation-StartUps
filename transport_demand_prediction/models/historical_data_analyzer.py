"""
Modelo de Análisis de Datos Históricos para Predicción de Demanda de Transporte
Autor: Sistema de IA Avanzado
Fecha: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class HistoricalDataAnalyzer:
    """
    Clase para análisis de datos históricos de transporte y demanda
    """
    
    def __init__(self, data_path=None):
        """
        Inicializar el analizador de datos históricos
        
        Args:
            data_path (str): Ruta al archivo de datos históricos
        """
        self.data_path = data_path
        self.data = None
        self.processed_data = None
        self.analysis_results = {}
        
    def load_data(self, data_path=None):
        """
        Cargar datos históricos desde archivo CSV o crear datos de ejemplo
        
        Args:
            data_path (str): Ruta al archivo de datos
        """
        if data_path:
            self.data_path = data_path
            try:
                self.data = pd.read_csv(data_path)
                print(f"✅ Datos cargados desde: {data_path}")
            except FileNotFoundError:
                print(f"⚠️ Archivo no encontrado: {data_path}")
                print("📊 Generando datos de ejemplo...")
                self._generate_sample_data()
        else:
            print("📊 Generando datos de ejemplo...")
            self._generate_sample_data()
            
        print(f"📈 Datos cargados: {len(self.data)} registros")
        return self.data
    
    def _generate_sample_data(self):
        """
        Generar datos de ejemplo para demostración
        """
        # Generar fechas para los últimos 2 años
        start_date = datetime.now() - timedelta(days=730)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
        
        # Crear datos sintéticos con patrones realistas
        np.random.seed(42)
        n_days = len(dates)
        
        # Variables base
        base_demand = 1000
        seasonal_factor = np.sin(2 * np.pi * np.arange(n_days) / 365.25) * 200
        trend_factor = np.arange(n_days) * 0.5
        noise = np.random.normal(0, 50, n_days)
        
        # Factores adicionales
        weekend_factor = np.where(dates.weekday >= 5, -100, 0)
        holiday_factor = np.random.choice([0, -200], n_days, p=[0.95, 0.05])
        
        # Calcular demanda total
        demand = base_demand + seasonal_factor + trend_factor + noise + weekend_factor + holiday_factor
        demand = np.maximum(demand, 0)  # Asegurar valores positivos
        
        # Crear DataFrame
        self.data = pd.DataFrame({
            'fecha': dates,
            'demanda_transporte': demand.astype(int),
            'temperatura': 20 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365.25) + np.random.normal(0, 3, n_days),
            'precio_combustible': 1.5 + 0.3 * np.sin(2 * np.pi * np.arange(n_days) / 365.25) + np.random.normal(0, 0.1, n_days),
            'eventos_especiales': np.random.choice([0, 1], n_days, p=[0.9, 0.1]),
            'dia_semana': dates.weekday,
            'mes': dates.month,
            'año': dates.year,
            'trimestre': dates.quarter
        })
        
        print("✅ Datos de ejemplo generados exitosamente")
    
    def preprocess_data(self):
        """
        Preprocesar datos para análisis
        """
        if self.data is None:
            raise ValueError("❌ No hay datos cargados. Use load_data() primero.")
        
        print("🔄 Preprocesando datos...")
        
        # Crear copia para procesamiento
        self.processed_data = self.data.copy()
        
        # Convertir fecha a datetime si no lo es
        if not pd.api.types.is_datetime64_any_dtype(self.processed_data['fecha']):
            self.processed_data['fecha'] = pd.to_datetime(self.processed_data['fecha'])
        
        # Crear variables adicionales
        self.processed_data['año_mes'] = self.processed_data['fecha'].dt.to_period('M')
        self.processed_data['semana_año'] = self.processed_data['fecha'].dt.isocalendar().week
        self.processed_data['es_fin_semana'] = self.processed_data['dia_semana'].isin([5, 6])
        self.processed_data['es_feriado'] = self.processed_data['eventos_especiales'] == 1
        
        # Calcular métricas derivadas
        self.processed_data['demanda_log'] = np.log1p(self.processed_data['demanda_transporte'])
        self.processed_data['demanda_normalizada'] = (
            self.processed_data['demanda_transporte'] - self.processed_data['demanda_transporte'].mean()
        ) / self.processed_data['demanda_transporte'].std()
        
        print("✅ Datos preprocesados exitosamente")
        return self.processed_data
    
    def analyze_trends(self):
        """
        Analizar tendencias en los datos históricos
        """
        if self.processed_data is None:
            self.preprocess_data()
        
        print("📈 Analizando tendencias...")
        
        # Análisis de tendencia general
        trend_analysis = {}
        
        # Tendencia mensual
        monthly_avg = self.processed_data.groupby('año_mes')['demanda_transporte'].mean()
        trend_analysis['tendencia_mensual'] = {
            'datos': monthly_avg,
            'tendencia': 'creciente' if monthly_avg.iloc[-1] > monthly_avg.iloc[0] else 'decreciente',
            'cambio_porcentual': ((monthly_avg.iloc[-1] - monthly_avg.iloc[0]) / monthly_avg.iloc[0]) * 100
        }
        
        # Tendencia anual
        yearly_avg = self.processed_data.groupby('año')['demanda_transporte'].mean()
        trend_analysis['tendencia_anual'] = {
            'datos': yearly_avg,
            'tendencia': 'creciente' if len(yearly_avg) > 1 and yearly_avg.iloc[-1] > yearly_avg.iloc[0] else 'estable',
            'cambio_porcentual': ((yearly_avg.iloc[-1] - yearly_avg.iloc[0]) / yearly_avg.iloc[0]) * 100 if len(yearly_avg) > 1 else 0
        }
        
        # Análisis de volatilidad
        daily_volatility = self.processed_data['demanda_transporte'].std()
        monthly_volatility = monthly_avg.std()
        
        trend_analysis['volatilidad'] = {
            'diaria': daily_volatility,
            'mensual': monthly_volatility,
            'coeficiente_variacion': daily_volatility / self.processed_data['demanda_transporte'].mean()
        }
        
        self.analysis_results['tendencias'] = trend_analysis
        print("✅ Análisis de tendencias completado")
        return trend_analysis
    
    def analyze_seasonality(self):
        """
        Analizar patrones estacionales
        """
        if self.processed_data is None:
            self.preprocess_data()
        
        print("🔄 Analizando estacionalidad...")
        
        seasonality_analysis = {}
        
        # Estacionalidad mensual
        monthly_pattern = self.processed_data.groupby('mes')['demanda_transporte'].agg(['mean', 'std', 'min', 'max'])
        seasonality_analysis['mensual'] = monthly_pattern
        
        # Estacionalidad por día de la semana
        weekly_pattern = self.processed_data.groupby('dia_semana')['demanda_transporte'].agg(['mean', 'std'])
        seasonality_analysis['semanal'] = weekly_pattern
        
        # Estacionalidad por trimestre
        quarterly_pattern = self.processed_data.groupby('trimestre')['demanda_transporte'].agg(['mean', 'std'])
        seasonality_analysis['trimestral'] = quarterly_pattern
        
        # Identificar meses pico y valle
        monthly_avg = monthly_pattern['mean']
        peak_month = monthly_avg.idxmax()
        valley_month = monthly_avg.idxmin()
        
        seasonality_analysis['patrones'] = {
            'mes_pico': peak_month,
            'mes_valle': valley_month,
            'diferencia_pico_valle': monthly_avg[peak_month] - monthly_avg[valley_month],
            'variacion_estacional': monthly_avg.std() / monthly_avg.mean()
        }
        
        self.analysis_results['estacionalidad'] = seasonality_analysis
        print("✅ Análisis de estacionalidad completado")
        return seasonality_analysis
    
    def analyze_correlations(self):
        """
        Analizar correlaciones entre variables
        """
        if self.processed_data is None:
            self.preprocess_data()
        
        print("🔗 Analizando correlaciones...")
        
        # Seleccionar variables numéricas para correlación
        numeric_vars = ['demanda_transporte', 'temperatura', 'precio_combustible', 
                       'dia_semana', 'mes', 'trimestre']
        
        correlation_matrix = self.processed_data[numeric_vars].corr()
        
        # Encontrar correlaciones significativas
        significant_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:  # Umbral de correlación significativa
                    significant_correlations.append({
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlacion': corr_value,
                        'fuerza': 'fuerte' if abs(corr_value) > 0.7 else 'moderada'
                    })
        
        correlation_analysis = {
            'matriz_correlacion': correlation_matrix,
            'correlaciones_significativas': significant_correlations
        }
        
        self.analysis_results['correlaciones'] = correlation_analysis
        print("✅ Análisis de correlaciones completado")
        return correlation_analysis
    
    def generate_insights(self):
        """
        Generar insights principales del análisis
        """
        if not self.analysis_results:
            print("⚠️ Ejecutando análisis completos primero...")
            self.analyze_trends()
            self.analyze_seasonality()
            self.analyze_correlations()
        
        print("💡 Generando insights...")
        
        insights = []
        
        # Insights de tendencias
        if 'tendencias' in self.analysis_results:
            trend_data = self.analysis_results['tendencias']
            insights.append(f"📈 Tendencia general: {trend_data['tendencia_mensual']['tendencia']}")
            insights.append(f"📊 Cambio porcentual mensual: {trend_data['tendencia_mensual']['cambio_porcentual']:.2f}%")
            insights.append(f"📉 Volatilidad diaria: {trend_data['volatilidad']['diaria']:.2f}")
        
        # Insights de estacionalidad
        if 'estacionalidad' in self.analysis_results:
            season_data = self.analysis_results['estacionalidad']
            patterns = season_data['patrones']
            insights.append(f"🗓️ Mes pico: {patterns['mes_pico']}")
            insights.append(f"🗓️ Mes valle: {patterns['mes_valle']}")
            insights.append(f"📊 Variación estacional: {patterns['variacion_estacional']:.2f}")
        
        # Insights de correlaciones
        if 'correlaciones' in self.analysis_results:
            corr_data = self.analysis_results['correlaciones']
            if corr_data['correlaciones_significativas']:
                strongest_corr = max(corr_data['correlaciones_significativas'], 
                                   key=lambda x: abs(x['correlacion']))
                insights.append(f"🔗 Correlación más fuerte: {strongest_corr['variable1']} vs {strongest_corr['variable2']} ({strongest_corr['correlacion']:.3f})")
        
        self.analysis_results['insights'] = insights
        print("✅ Insights generados exitosamente")
        return insights
    
    def create_visualizations(self, save_path=None):
        """
        Crear visualizaciones de los análisis
        """
        if self.processed_data is None:
            self.preprocess_data()
        
        print("📊 Creando visualizaciones...")
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Serie temporal de demanda
        plt.subplot(3, 3, 1)
        plt.plot(self.processed_data['fecha'], self.processed_data['demanda_transporte'], alpha=0.7)
        plt.title('Demanda de Transporte - Serie Temporal', fontsize=14, fontweight='bold')
        plt.xlabel('Fecha')
        plt.ylabel('Demanda')
        plt.xticks(rotation=45)
        
        # 2. Tendencia mensual
        plt.subplot(3, 3, 2)
        monthly_data = self.processed_data.groupby('año_mes')['demanda_transporte'].mean()
        plt.plot(range(len(monthly_data)), monthly_data.values, marker='o')
        plt.title('Tendencia Mensual', fontsize=14, fontweight='bold')
        plt.xlabel('Período')
        plt.ylabel('Demanda Promedio')
        
        # 3. Patrón estacional mensual
        plt.subplot(3, 3, 3)
        monthly_pattern = self.processed_data.groupby('mes')['demanda_transporte'].mean()
        plt.bar(monthly_pattern.index, monthly_pattern.values)
        plt.title('Patrón Estacional Mensual', fontsize=14, fontweight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Demanda Promedio')
        
        # 4. Patrón semanal
        plt.subplot(3, 3, 4)
        weekly_pattern = self.processed_data.groupby('dia_semana')['demanda_transporte'].mean()
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        plt.bar(days, weekly_pattern.values)
        plt.title('Patrón Semanal', fontsize=14, fontweight='bold')
        plt.xlabel('Día de la Semana')
        plt.ylabel('Demanda Promedio')
        
        # 5. Distribución de demanda
        plt.subplot(3, 3, 5)
        plt.hist(self.processed_data['demanda_transporte'], bins=50, alpha=0.7, edgecolor='black')
        plt.title('Distribución de Demanda', fontsize=14, fontweight='bold')
        plt.xlabel('Demanda')
        plt.ylabel('Frecuencia')
        
        # 6. Correlación con temperatura
        plt.subplot(3, 3, 6)
        plt.scatter(self.processed_data['temperatura'], self.processed_data['demanda_transporte'], alpha=0.5)
        plt.title('Demanda vs Temperatura', fontsize=14, fontweight='bold')
        plt.xlabel('Temperatura')
        plt.ylabel('Demanda')
        
        # 7. Correlación con precio combustible
        plt.subplot(3, 3, 7)
        plt.scatter(self.processed_data['precio_combustible'], self.processed_data['demanda_transporte'], alpha=0.5)
        plt.title('Demanda vs Precio Combustible', fontsize=14, fontweight='bold')
        plt.xlabel('Precio Combustible')
        plt.ylabel('Demanda')
        
        # 8. Boxplot por mes
        plt.subplot(3, 3, 8)
        monthly_data_list = [self.processed_data[self.processed_data['mes'] == i]['demanda_transporte'].values 
                           for i in range(1, 13)]
        plt.boxplot(monthly_data_list, labels=range(1, 13))
        plt.title('Distribución Mensual', fontsize=14, fontweight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Demanda')
        
        # 9. Heatmap de correlaciones
        plt.subplot(3, 3, 9)
        numeric_vars = ['demanda_transporte', 'temperatura', 'precio_combustible', 'dia_semana']
        corr_matrix = self.processed_data[numeric_vars].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Matriz de Correlaciones', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Visualizaciones guardadas en: {save_path}")
        
        plt.show()
        print("✅ Visualizaciones creadas exitosamente")
    
    def export_analysis(self, output_path='analysis_results.json'):
        """
        Exportar resultados del análisis
        """
        import json
        
        # Preparar datos para exportación
        export_data = {
            'metadata': {
                'fecha_analisis': datetime.now().isoformat(),
                'total_registros': len(self.processed_data) if self.processed_data is not None else 0,
                'periodo_inicio': str(self.processed_data['fecha'].min()) if self.processed_data is not None else None,
                'periodo_fin': str(self.processed_data['fecha'].max()) if self.processed_data is not None else None
            },
            'resumen_estadistico': {
                'demanda_promedio': float(self.processed_data['demanda_transporte'].mean()) if self.processed_data is not None else 0,
                'demanda_std': float(self.processed_data['demanda_transporte'].std()) if self.processed_data is not None else 0,
                'demanda_min': float(self.processed_data['demanda_transporte'].min()) if self.processed_data is not None else 0,
                'demanda_max': float(self.processed_data['demanda_transporte'].max()) if self.processed_data is not None else 0
            },
            'insights': self.analysis_results.get('insights', []),
            'tendencias': self.analysis_results.get('tendencias', {}),
            'estacionalidad': self.analysis_results.get('estacionalidad', {}),
            'correlaciones': self.analysis_results.get('correlaciones', {})
        }
        
        # Convertir numpy arrays a listas para JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, pd.Series):
                return obj.tolist()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict()
            return obj
        
        # Limpiar datos para JSON
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            else:
                return convert_numpy(obj)
        
        export_data = clean_for_json(export_data)
        
        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Análisis exportado a: {output_path}")
        return export_data

# Función principal para demostración
def main():
    """
    Función principal para demostrar el uso del analizador
    """
    print("🚀 Iniciando Análisis de Datos Históricos de Transporte")
    print("=" * 60)
    
    # Crear instancia del analizador
    analyzer = HistoricalDataAnalyzer()
    
    # Cargar datos
    analyzer.load_data()
    
    # Preprocesar datos
    analyzer.preprocess_data()
    
    # Realizar análisis completos
    print("\n📊 Realizando análisis completos...")
    analyzer.analyze_trends()
    analyzer.analyze_seasonality()
    analyzer.analyze_correlations()
    analyzer.generate_insights()
    
    # Mostrar insights
    print("\n💡 INSIGHTS PRINCIPALES:")
    print("-" * 40)
    for insight in analyzer.analysis_results.get('insights', []):
        print(f"  {insight}")
    
    # Crear visualizaciones
    print("\n📊 Creando visualizaciones...")
    analyzer.create_visualizations('transport_analysis.png')
    
    # Exportar resultados
    print("\n💾 Exportando resultados...")
    analyzer.export_analysis('historical_analysis_results.json')
    
    print("\n✅ Análisis completado exitosamente!")
    print("=" * 60)

if __name__ == "__main__":
    main()



