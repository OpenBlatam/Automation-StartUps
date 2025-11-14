"""
Dashboard Interactivo para Predicción de Demanda de Transporte
Autor: Sistema de IA Avanzado
Fecha: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="🚛 Predicción de Demanda de Transporte",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TransportDemandDashboard:
    """
    Dashboard interactivo para análisis y predicción de demanda de transporte
    """
    
    def __init__(self):
        """
        Inicializar el dashboard
        """
        self.data = None
        self.analysis_results = {}
        self.predictions = {}
        
    def load_sample_data(self):
        """
        Cargar datos de ejemplo para el dashboard
        """
        # Generar datos de ejemplo
        start_date = datetime.now() - timedelta(days=730)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='D')
        
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
        demand = np.maximum(demand, 0)
        
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
        
        return self.data
    
    def create_main_dashboard(self):
        """
        Crear el dashboard principal
        """
        # Título principal
        st.title("🚛 Sistema de Predicción de Demanda de Transporte")
        st.markdown("---")
        
        # Sidebar
        self.create_sidebar()
        
        # Cargar datos si no están disponibles
        if self.data is None:
            self.load_sample_data()
        
        # Métricas principales
        self.create_metrics_section()
        
        # Gráficos principales
        self.create_main_charts()
        
        # Análisis de estacionalidad
        self.create_seasonality_analysis()
        
        # Predicciones
        self.create_predictions_section()
        
        # Análisis de correlaciones
        self.create_correlation_analysis()
        
        # Alertas y recomendaciones
        self.create_alerts_section()
    
    def create_sidebar(self):
        """
        Crear sidebar con controles
        """
        st.sidebar.title("🎛️ Controles del Dashboard")
        
        # Selector de período
        st.sidebar.subheader("📅 Período de Análisis")
        period_options = {
            "Últimos 30 días": 30,
            "Últimos 90 días": 90,
            "Últimos 6 meses": 180,
            "Último año": 365,
            "Todo el período": 0
        }
        
        selected_period = st.sidebar.selectbox(
            "Seleccionar período:",
            list(period_options.keys())
        )
        
        # Horizonte de predicción
        st.sidebar.subheader("🔮 Predicciones")
        forecast_horizon = st.sidebar.slider(
            "Horizonte de predicción (días):",
            min_value=7,
            max_value=90,
            value=30,
            step=7
        )
        
        # Configuración de alertas
        st.sidebar.subheader("⚠️ Alertas")
        alert_threshold = st.sidebar.slider(
            "Umbral de alerta (%):",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        # Guardar configuración
        self.config = {
            'period': period_options[selected_period],
            'forecast_horizon': forecast_horizon,
            'alert_threshold': alert_threshold
        }
    
    def create_metrics_section(self):
        """
        Crear sección de métricas principales
        """
        st.subheader("📊 Métricas Principales")
        
        # Filtrar datos según período seleccionado
        if self.config['period'] > 0:
            filtered_data = self.data.tail(self.config['period'])
        else:
            filtered_data = self.data
        
        # Calcular métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_demand = filtered_data['demanda_transporte'].mean()
            st.metric(
                label="📈 Demanda Promedio",
                value=f"{avg_demand:,.0f}",
                delta=f"{avg_demand - self.data['demanda_transporte'].mean():.0f}"
            )
        
        with col2:
            max_demand = filtered_data['demanda_transporte'].max()
            st.metric(
                label="🔝 Demanda Máxima",
                value=f"{max_demand:,.0f}",
                delta=f"{max_demand - self.data['demanda_transporte'].max():.0f}"
            )
        
        with col3:
            volatility = filtered_data['demanda_transporte'].std()
            st.metric(
                label="📊 Volatilidad",
                value=f"{volatility:.0f}",
                delta=f"{volatility - self.data['demanda_transporte'].std():.0f}"
            )
        
        with col4:
            trend = filtered_data['demanda_transporte'].diff().mean()
            st.metric(
                label="📈 Tendencia Diaria",
                value=f"{trend:.1f}",
                delta=f"{trend:.1f}"
            )
    
    def create_main_charts(self):
        """
        Crear gráficos principales
        """
        st.subheader("📈 Análisis Temporal")
        
        # Filtrar datos
        if self.config['period'] > 0:
            filtered_data = self.data.tail(self.config['period'])
        else:
            filtered_data = self.data
        
        # Gráfico de serie temporal
        fig = go.Figure()
        
        # Línea principal de demanda
        fig.add_trace(go.Scatter(
            x=filtered_data['fecha'],
            y=filtered_data['demanda_transporte'],
            mode='lines',
            name='Demanda de Transporte',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Demanda:</b> %{y:,.0f}<extra></extra>'
        ))
        
        # Línea de tendencia
        z = np.polyfit(range(len(filtered_data)), filtered_data['demanda_transporte'], 1)
        trend_line = np.polyval(z, range(len(filtered_data)))
        
        fig.add_trace(go.Scatter(
            x=filtered_data['fecha'],
            y=trend_line,
            mode='lines',
            name='Tendencia',
            line=dict(color='red', dash='dash', width=2),
            hovertemplate='<b>Tendencia:</b> %{y:,.0f}<extra></extra>'
        ))
        
        # Configurar layout
        fig.update_layout(
            title="Demanda de Transporte - Serie Temporal",
            xaxis_title="Fecha",
            yaxis_title="Demanda",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de componentes
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de demanda
            fig_dist = px.histogram(
                filtered_data,
                x='demanda_transporte',
                nbins=30,
                title="Distribución de Demanda",
                labels={'demanda_transporte': 'Demanda', 'count': 'Frecuencia'}
            )
            fig_dist.update_layout(height=300)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Boxplot por mes
            fig_box = px.box(
                filtered_data,
                x='mes',
                y='demanda_transporte',
                title="Distribución Mensual",
                labels={'mes': 'Mes', 'demanda_transporte': 'Demanda'}
            )
            fig_box.update_layout(height=300)
            st.plotly_chart(fig_box, use_container_width=True)
    
    def create_seasonality_analysis(self):
        """
        Crear análisis de estacionalidad
        """
        st.subheader("🔄 Análisis de Estacionalidad")
        
        # Patrón mensual
        monthly_pattern = self.data.groupby('mes')['demanda_transporte'].agg(['mean', 'std']).reset_index()
        
        fig_monthly = go.Figure()
        
        fig_monthly.add_trace(go.Bar(
            x=monthly_pattern['mes'],
            y=monthly_pattern['mean'],
            name='Demanda Promedio',
            error_y=dict(type='data', array=monthly_pattern['std']),
            hovertemplate='<b>Mes:</b> %{x}<br><b>Demanda Promedio:</b> %{y:,.0f}<extra></extra>'
        ))
        
        fig_monthly.update_layout(
            title="Patrón Estacional Mensual",
            xaxis_title="Mes",
            yaxis_title="Demanda Promedio",
            height=400
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Patrón semanal
        col1, col2 = st.columns(2)
        
        with col1:
            weekly_pattern = self.data.groupby('dia_semana')['demanda_transporte'].mean().reset_index()
            day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            weekly_pattern['dia_nombre'] = [day_names[i] for i in weekly_pattern['dia_semana']]
            
            fig_weekly = px.bar(
                weekly_pattern,
                x='dia_nombre',
                y='demanda_transporte',
                title="Patrón Semanal",
                labels={'dia_nombre': 'Día de la Semana', 'demanda_transporte': 'Demanda Promedio'}
            )
            fig_weekly.update_layout(height=300)
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        with col2:
            # Heatmap de estacionalidad
            seasonal_matrix = self.data.groupby(['mes', 'dia_semana'])['demanda_transporte'].mean().unstack()
            
            fig_heatmap = px.imshow(
                seasonal_matrix.values,
                labels=dict(x="Día de la Semana", y="Mes", color="Demanda"),
                x=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                y=list(range(1, 13)),
                title="Heatmap de Estacionalidad",
                color_continuous_scale='YlOrRd'
            )
            fig_heatmap.update_layout(height=300)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    def create_predictions_section(self):
        """
        Crear sección de predicciones
        """
        st.subheader("🔮 Predicciones de Demanda")
        
        # Generar predicciones simples
        horizon = self.config['forecast_horizon']
        last_date = self.data['fecha'].max()
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=horizon, freq='D')
        
        # Predicción basada en tendencia y estacionalidad
        last_demand = self.data['demanda_transporte'].iloc[-1]
        trend = self.data['demanda_transporte'].diff().mean()
        seasonal_factor = np.sin(2 * np.pi * future_dates.dayofyear / 365.25) * 50
        
        base_prediction = last_demand + np.arange(1, horizon + 1) * trend + seasonal_factor
        
        # Crear DataFrame de predicciones
        predictions_df = pd.DataFrame({
            'fecha': future_dates,
            'prediccion': base_prediction,
            'intervalo_inf': base_prediction * 0.9,
            'intervalo_sup': base_prediction * 1.1
        })
        
        # Gráfico de predicciones
        fig_pred = go.Figure()
        
        # Datos históricos (últimos 90 días)
        historical_data = self.data.tail(90)
        
        fig_pred.add_trace(go.Scatter(
            x=historical_data['fecha'],
            y=historical_data['demanda_transporte'],
            mode='lines',
            name='Datos Históricos',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Demanda:</b> %{y:,.0f}<extra></extra>'
        ))
        
        # Predicciones
        fig_pred.add_trace(go.Scatter(
            x=predictions_df['fecha'],
            y=predictions_df['prediccion'],
            mode='lines',
            name='Predicción',
            line=dict(color='red', width=2),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Predicción:</b> %{y:,.0f}<extra></extra>'
        ))
        
        # Intervalo de confianza
        fig_pred.add_trace(go.Scatter(
            x=predictions_df['fecha'],
            y=predictions_df['intervalo_sup'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_pred.add_trace(go.Scatter(
            x=predictions_df['fecha'],
            y=predictions_df['intervalo_inf'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.2)',
            name='Intervalo de Confianza',
            hoverinfo='skip'
        ))
        
        fig_pred.update_layout(
            title=f"Predicciones de Demanda ({horizon} días)",
            xaxis_title="Fecha",
            yaxis_title="Demanda",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_pred, use_container_width=True)
        
        # Métricas de predicción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_prediction = predictions_df['prediccion'].mean()
            st.metric(
                label="📊 Demanda Promedio Predicha",
                value=f"{avg_prediction:,.0f}"
            )
        
        with col2:
            max_prediction = predictions_df['prediccion'].max()
            st.metric(
                label="🔝 Demanda Máxima Predicha",
                value=f"{max_prediction:,.0f}"
            )
        
        with col3:
            growth_rate = ((predictions_df['prediccion'].iloc[-1] - predictions_df['prediccion'].iloc[0]) / 
                         predictions_df['prediccion'].iloc[0]) * 100
            st.metric(
                label="📈 Tasa de Crecimiento",
                value=f"{growth_rate:.1f}%"
            )
    
    def create_correlation_analysis(self):
        """
        Crear análisis de correlaciones
        """
        st.subheader("🔗 Análisis de Correlaciones")
        
        # Seleccionar variables numéricas
        numeric_vars = ['demanda_transporte', 'temperatura', 'precio_combustible']
        corr_data = self.data[numeric_vars].corr()
        
        # Heatmap de correlaciones
        fig_corr = px.imshow(
            corr_data.values,
            labels=dict(x="Variable", y="Variable", color="Correlación"),
            x=numeric_vars,
            y=numeric_vars,
            title="Matriz de Correlaciones",
            color_continuous_scale='RdBu',
            color_continuous_midpoint=0
        )
        
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Gráficos de dispersión
        col1, col2 = st.columns(2)
        
        with col1:
            fig_scatter1 = px.scatter(
                self.data,
                x='temperatura',
                y='demanda_transporte',
                title="Demanda vs Temperatura",
                labels={'temperatura': 'Temperatura (°C)', 'demanda_transporte': 'Demanda'},
                trendline="ols"
            )
            fig_scatter1.update_layout(height=300)
            st.plotly_chart(fig_scatter1, use_container_width=True)
        
        with col2:
            fig_scatter2 = px.scatter(
                self.data,
                x='precio_combustible',
                y='demanda_transporte',
                title="Demanda vs Precio Combustible",
                labels={'precio_combustible': 'Precio Combustible', 'demanda_transporte': 'Demanda'},
                trendline="ols"
            )
            fig_scatter2.update_layout(height=300)
            st.plotly_chart(fig_scatter2, use_container_width=True)
    
    def create_alerts_section(self):
        """
        Crear sección de alertas y recomendaciones
        """
        st.subheader("⚠️ Alertas y Recomendaciones")
        
        # Calcular alertas
        current_demand = self.data['demanda_transporte'].iloc[-1]
        avg_demand = self.data['demanda_transporte'].mean()
        threshold = self.config['alert_threshold']
        
        alerts = []
        
        # Alerta de demanda alta
        if current_demand > avg_demand * (1 + threshold/100):
            alerts.append({
                'type': 'warning',
                'title': '🚨 Demanda Alta Detectada',
                'message': f'La demanda actual ({current_demand:,.0f}) está {threshold}% por encima del promedio',
                'recommendation': 'Considerar aumentar la capacidad de transporte'
            })
        
        # Alerta de demanda baja
        elif current_demand < avg_demand * (1 - threshold/100):
            alerts.append({
                'type': 'info',
                'title': '📉 Demanda Baja Detectada',
                'message': f'La demanda actual ({current_demand:,.0f}) está {threshold}% por debajo del promedio',
                'recommendation': 'Considerar optimizar costos operativos'
            })
        
        # Alerta de volatilidad
        volatility = self.data['demanda_transporte'].tail(30).std()
        avg_volatility = self.data['demanda_transporte'].std()
        
        if volatility > avg_volatility * 1.5:
            alerts.append({
                'type': 'warning',
                'title': '📊 Alta Volatilidad',
                'message': f'La volatilidad reciente ({volatility:.0f}) es 50% mayor que el promedio histórico',
                'recommendation': 'Revisar estrategias de gestión de demanda'
            })
        
        # Mostrar alertas
        if alerts:
            for alert in alerts:
                if alert['type'] == 'warning':
                    st.warning(f"**{alert['title']}**\n\n{alert['message']}\n\n💡 **Recomendación:** {alert['recommendation']}")
                else:
                    st.info(f"**{alert['title']}**\n\n{alert['message']}\n\n💡 **Recomendación:** {alert['recommendation']}")
        else:
            st.success("✅ No se detectaron alertas críticas. El sistema está funcionando dentro de parámetros normales.")
        
        # Recomendaciones generales
        st.subheader("💡 Recomendaciones Generales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📈 Optimización de Capacidad:**
            - Monitorear patrones estacionales
            - Ajustar flota según demanda prevista
            - Implementar sistemas de reserva dinámica
            """)
        
        with col2:
            st.markdown("""
            **💰 Gestión de Costos:**
            - Optimizar rutas según demanda
            - Implementar precios dinámicos
            - Reducir costos operativos en períodos de baja demanda
            """)

def main():
    """
    Función principal para ejecutar el dashboard
    """
    # Crear instancia del dashboard
    dashboard = TransportDemandDashboard()
    
    # Ejecutar dashboard
    dashboard.create_main_dashboard()

if __name__ == "__main__":
    main()



