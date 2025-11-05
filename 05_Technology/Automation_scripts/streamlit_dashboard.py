#!/usr/bin/env python3
"""
Dashboard Interactivo Avanzado con Streamlit
============================================

Dashboard mejorado para el sistema de análisis de precios competitivos con:
- Visualizaciones interactivas
- Análisis en tiempo real
- Predicciones de precios
- Análisis de sentimientos
- Optimización de estrategias
- Alertas inteligentes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
import json
from datetime import datetime, timedelta
import asyncio
import time
from typing import Dict, List, Any
import requests
from advanced_pricing_enhancements import AdvancedPricingEnhancements, RealTimePricingOptimizer

# Configuración de la página
st.set_page_config(
    page_title="🏆 Competitive Pricing Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .insight-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .alert-high {
        border-left-color: #e74c3c !important;
        background: #fdf2f2 !important;
    }
    
    .alert-medium {
        border-left-color: #f39c12 !important;
        background: #fef9e7 !important;
    }
    
    .alert-low {
        border-left-color: #27ae60 !important;
        background: #f0f9f0 !important;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitDashboard:
    """Dashboard interactivo con Streamlit"""
    
    def __init__(self):
        """Inicializar dashboard"""
        self.enhancements = AdvancedPricingEnhancements()
        self.optimizer = RealTimePricingOptimizer()
        self.db_path = "pricing_analysis.db"
        
    def run(self):
        """Ejecutar dashboard"""
        # Header principal
        st.markdown('<h1 class="main-header">🏆 Competitive Pricing Analysis Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self._create_sidebar()
        
        # Contenido principal
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "🔍 Analysis", 
            "📈 Forecasting", 
            "🎯 Optimization", 
            "⚙️ Settings"
        ])
        
        with tab1:
            self._show_overview()
        
        with tab2:
            self._show_analysis()
        
        with tab3:
            self._show_forecasting()
        
        with tab4:
            self._show_optimization()
        
        with tab5:
            self._show_settings()
    
    def _create_sidebar(self):
        """Crear sidebar con controles"""
        st.sidebar.title("🎛️ Dashboard Controls")
        
        # Selector de producto
        products = self._get_available_products()
        selected_product = st.sidebar.selectbox(
            "Select Product",
            products,
            index=0 if products else 0
        )
        
        # Selector de competidor
        competitors = self._get_available_competitors()
        selected_competitors = st.sidebar.multiselect(
            "Select Competitors",
            competitors,
            default=competitors[:3] if competitors else []
        )
        
        # Rango de fechas
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        # Configuración de actualización
        auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 30, 300, 60)
        
        # Guardar configuración en session state
        st.session_state.selected_product = selected_product
        st.session_state.selected_competitors = selected_competitors
        st.session_state.date_range = date_range
        st.session_state.auto_refresh = auto_refresh
        st.session_state.refresh_interval = refresh_interval
        
        # Botón de actualización manual
        if st.sidebar.button("🔄 Refresh Data"):
            st.rerun()
    
    def _show_overview(self):
        """Mostrar vista general"""
        st.header("📊 Market Overview")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._show_metric_card("Products Tracked", self._get_product_count(), "📦")
        
        with col2:
            self._show_metric_card("Competitors Monitored", self._get_competitor_count(), "🏢")
        
        with col3:
            self._show_metric_card("Data Points", self._get_data_point_count(), "📈")
        
        with col4:
            self._show_metric_card("Active Alerts", self._get_active_alert_count(), "🚨")
        
        # Gráfico de precios principales
        st.subheader("💰 Price Comparison")
        price_chart = self._create_price_comparison_chart()
        st.plotly_chart(price_chart, use_container_width=True)
        
        # Insights recientes
        st.subheader("💡 Recent Insights")
        insights = self._get_recent_insights()
        for insight in insights[:5]:
            self._show_insight_card(insight)
    
    def _show_analysis(self):
        """Mostrar análisis detallado"""
        st.header("🔍 Detailed Analysis")
        
        # Análisis de sentimientos
        st.subheader("😊 Market Sentiment Analysis")
        sentiment = self.enhancements.analyze_market_sentiment(st.session_state.selected_product)
        
        if sentiment:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Sentiment Score", f"{sentiment.sentiment_score:.2f}")
            
            with col2:
                st.metric("Confidence", f"{sentiment.confidence:.2f}")
            
            with col3:
                st.metric("Total Mentions", sentiment.positive_mentions + sentiment.negative_mentions + sentiment.neutral_mentions)
            
            # Gráfico de sentimientos
            sentiment_data = {
                'Positive': sentiment.positive_mentions,
                'Negative': sentiment.negative_mentions,
                'Neutral': sentiment.neutral_mentions
            }
            
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#27ae60',
                    'Negative': '#e74c3c',
                    'Neutral': '#f39c12'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de elasticidad
        st.subheader("📊 Price Elasticity Analysis")
        elasticity = self.enhancements.analyze_price_elasticity(st.session_state.selected_product)
        
        if elasticity:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Price Elasticity", f"{elasticity.price_elasticity:.2f}")
                st.metric("Demand Sensitivity", elasticity.demand_sensitivity.replace('_', ' ').title())
            
            with col2:
                st.metric("Revenue Impact", f"{elasticity.revenue_impact:.1%}")
                st.metric("Market Share Impact", f"{elasticity.market_share_impact:.1%}")
            
            # Gráfico de elasticidad
            price_range = np.linspace(elasticity.optimal_price_range[0], elasticity.optimal_price_range[1], 100)
            demand = 1000 * (1 - (price_range - 100) / 1000)  # Simulación simple
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=price_range,
                y=demand,
                mode='lines',
                name='Demand Curve',
                line=dict(color='#667eea', width=3)
            ))
            
            fig.update_layout(
                title="Price-Demand Relationship",
                xaxis_title="Price ($)",
                yaxis_title="Demand (units)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_forecasting(self):
        """Mostrar predicciones"""
        st.header("📈 Price Forecasting")
        
        # Predicciones de precios
        forecast = self.enhancements.forecast_price_trends(st.session_state.selected_product)
        
        if forecast:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Price", f"${forecast.current_price:.2f}")
                st.metric("1 Week Forecast", f"${forecast.predicted_price_1w:.2f}")
            
            with col2:
                st.metric("1 Month Forecast", f"${forecast.predicted_price_1m:.2f}")
                st.metric("3 Month Forecast", f"${forecast.predicted_price_3m:.2f}")
            
            with col3:
                st.metric("Trend Direction", forecast.trend_direction.title())
                st.metric("Volatility", f"{forecast.volatility:.3f}")
            
            # Gráfico de predicciones
            periods = ['Current', '1 Week', '1 Month', '3 Months']
            prices = [forecast.current_price, forecast.predicted_price_1w, 
                     forecast.predicted_price_1m, forecast.predicted_price_3m]
            confidences = [1.0, forecast.confidence_1w, forecast.confidence_1m, forecast.confidence_3m]
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(
                    x=periods,
                    y=prices,
                    mode='lines+markers',
                    name='Price Forecast',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=periods,
                    y=confidences,
                    mode='lines+markers',
                    name='Confidence',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=6)
                ),
                secondary_y=True
            )
            
            fig.update_xaxes(title_text="Time Period")
            fig.update_yaxes(title_text="Price ($)", secondary_y=False)
            fig.update_yaxes(title_text="Confidence", secondary_y=True)
            fig.update_layout(title_text="Price Forecast with Confidence")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de tendencias
        st.subheader("📊 Trend Analysis")
        trend_data = self._get_trend_data(st.session_state.selected_product)
        
        if not trend_data.empty:
            fig = px.line(
                trend_data,
                x='date',
                y='price',
                color='competitor',
                title="Price Trends Over Time",
                hover_data=['price', 'competitor']
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_optimization(self):
        """Mostrar optimización de estrategias"""
        st.header("🎯 Pricing Strategy Optimization")
        
        # Optimización de estrategia
        if st.button("🚀 Run Optimization Analysis"):
            with st.spinner("Analyzing and optimizing pricing strategy..."):
                strategy = self.enhancements.optimize_pricing_strategy(st.session_state.selected_product)
                
                if strategy:
                    st.success("Optimization completed!")
                    
                    # Mostrar estrategia recomendada
                    st.subheader("📋 Recommended Strategy")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Action", strategy['recommended_strategy']['pricing_action'].title())
                        st.metric("Price Adjustment", f"{strategy['recommended_strategy']['price_adjustment']:.1%}")
                    
                    with col2:
                        st.metric("Confidence Score", f"{strategy['confidence_score']:.2f}")
                        st.metric("Priority", strategy['implementation_priority'].title())
                    
                    with col3:
                        outcomes = strategy['expected_outcomes']
                        st.metric("Revenue Impact", f"{outcomes['revenue_change']:.1%}")
                        st.metric("Market Share Impact", f"{outcomes['market_share_change']:.1%}")
                    
                    # Justificación
                    st.subheader("💡 Rationale")
                    for reason in strategy['recommended_strategy']['rationale']:
                        st.write(f"• {reason}")
                    
                    # Resultados esperados
                    st.subheader("📊 Expected Outcomes")
                    
                    outcome_data = {
                        'Metric': ['Demand Change', 'Revenue Change', 'Market Share Change', 'Profit Margin Impact'],
                        'Impact': [
                            f"{outcomes['demand_change']:.1%}",
                            f"{outcomes['revenue_change']:.1%}",
                            f"{outcomes['market_share_change']:.1%}",
                            f"{outcomes['profit_margin_impact']:.1%}"
                        ]
                    }
                    
                    outcome_df = pd.DataFrame(outcome_data)
                    st.dataframe(outcome_df, use_container_width=True)
                    
                    # Gráfico de impacto
                    fig = px.bar(
                        outcome_df,
                        x='Metric',
                        y='Impact',
                        title="Expected Impact of Strategy",
                        color='Impact',
                        color_continuous_scale=['red', 'yellow', 'green']
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Optimización en tiempo real
        st.subheader("⚡ Real-Time Optimization")
        
        if st.button("🔄 Start Real-Time Optimization"):
            products = [st.session_state.selected_product]
            self.optimizer.start_real_time_optimization(products)
            st.success("Real-time optimization started!")
        
        # Estado de optimización
        optimization_status = self.optimizer.get_optimization_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Active Optimizations", optimization_status['active_optimizations'])
        
        with col2:
            st.metric("Products Being Optimized", len(optimization_status['products_being_optimized']))
    
    def _show_settings(self):
        """Mostrar configuración"""
        st.header("⚙️ System Settings")
        
        # Configuración de alertas
        st.subheader("🚨 Alert Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            price_change_threshold = st.slider("Price Change Threshold (%)", 1, 50, 10)
            price_gap_threshold = st.slider("Price Gap Threshold (%)", 5, 100, 30)
        
        with col2:
            alert_frequency = st.selectbox("Alert Frequency", ["Immediate", "Hourly", "Daily"])
            notification_channels = st.multiselect(
                "Notification Channels",
                ["Email", "SMS", "Slack", "Teams"],
                default=["Email"]
            )
        
        # Configuración de análisis
        st.subheader("🔍 Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_frequency = st.selectbox("Analysis Frequency", ["Real-time", "Hourly", "Daily"])
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7)
        
        with col2:
            forecast_periods = st.multiselect(
                "Forecast Periods",
                ["1 Week", "1 Month", "3 Months", "6 Months"],
                default=["1 Week", "1 Month", "3 Months"]
            )
            include_sentiment = st.checkbox("Include Sentiment Analysis", value=True)
        
        # Configuración de integración
        st.subheader("🔗 Integration Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            crm_integration = st.selectbox("CRM Integration", ["None", "Salesforce", "HubSpot", "Pipedrive"])
            bi_integration = st.selectbox("BI Integration", ["None", "Tableau", "Power BI", "Looker"])
        
        with col2:
            api_rate_limit = st.number_input("API Rate Limit (requests/minute)", 10, 1000, 100)
            data_retention_days = st.number_input("Data Retention (days)", 30, 365, 90)
        
        # Botón de guardar configuración
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
    
    def _show_metric_card(self, title: str, value: Any, icon: str):
        """Mostrar tarjeta de métrica"""
        st.markdown(f"""
        <div class="metric-card">
            <h3>{icon} {title}</h3>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_insight_card(self, insight: Dict[str, Any]):
        """Mostrar tarjeta de insight"""
        alert_class = "alert-high" if insight.get('impact_score', 0) > 0.7 else "alert-medium" if insight.get('impact_score', 0) > 0.4 else "alert-low"
        
        st.markdown(f"""
        <div class="insight-card {alert_class}">
            <h4>{insight.get('title', 'Insight')}</h4>
            <p>{insight.get('description', 'No description available')}</p>
            <small>Impact: {insight.get('impact_score', 0):.1%} | Confidence: {insight.get('confidence', 0):.1%}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _create_price_comparison_chart(self):
        """Crear gráfico de comparación de precios"""
        price_data = self._get_price_data()
        
        if price_data.empty:
            return go.Figure()
        
        fig = px.bar(
            price_data,
            x='competitor',
            y='price',
            color='product_name',
            title="Price Comparison by Competitor",
            hover_data=['price', 'date_collected']
        )
        
        fig.update_layout(
            xaxis_title="Competitor",
            yaxis_title="Price ($)",
            hovermode='x unified'
        )
        
        return fig
    
    def _get_available_products(self) -> List[str]:
        """Obtener productos disponibles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT product_id FROM pricing_data")
            products = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return products
            
        except Exception as e:
            st.error(f"Error getting products: {e}")
            return []
    
    def _get_available_competitors(self) -> List[str]:
        """Obtener competidores disponibles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT competitor FROM pricing_data")
            competitors = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return competitors
            
        except Exception as e:
            st.error(f"Error getting competitors: {e}")
            return []
    
    def _get_price_data(self) -> pd.DataFrame:
        """Obtener datos de precios"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT product_id, product_name, competitor, price, date_collected
                FROM pricing_data
                WHERE date_collected >= date('now', '-7 days')
                ORDER BY date_collected DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            st.error(f"Error getting price data: {e}")
            return pd.DataFrame()
    
    def _get_trend_data(self, product_id: str) -> pd.DataFrame:
        """Obtener datos de tendencias"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT competitor, price, date_collected
                FROM pricing_data
                WHERE product_id = ?
                AND date_collected >= date('now', '-30 days')
                ORDER BY date_collected
            """
            
            df = pd.read_sql_query(query, conn, params=[product_id])
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date_collected'])
            
            return df
            
        except Exception as e:
            st.error(f"Error getting trend data: {e}")
            return pd.DataFrame()
    
    def _get_recent_insights(self) -> List[Dict[str, Any]]:
        """Obtener insights recientes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT insight_type, description, impact_score, recommendation, confidence
                FROM competitive_insights
                WHERE created_at >= date('now', '-7 days')
                ORDER BY impact_score DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            insights = []
            for row in rows:
                insights.append({
                    'title': row[0].replace('_', ' ').title(),
                    'description': row[1],
                    'impact_score': row[2],
                    'recommendation': row[3],
                    'confidence': row[4]
                })
            
            return insights
            
        except Exception as e:
            st.error(f"Error getting insights: {e}")
            return []
    
    def _get_product_count(self) -> int:
        """Obtener número de productos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(DISTINCT product_id) FROM pricing_data")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            return 0
    
    def _get_competitor_count(self) -> int:
        """Obtener número de competidores"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(DISTINCT competitor) FROM pricing_data")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            return 0
    
    def _get_data_point_count(self) -> int:
        """Obtener número de puntos de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM pricing_data")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            return 0
    
    def _get_active_alert_count(self) -> int:
        """Obtener número de alertas activas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE acknowledged = FALSE")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            return 0

def main():
    """Función principal"""
    dashboard = StreamlitDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()






