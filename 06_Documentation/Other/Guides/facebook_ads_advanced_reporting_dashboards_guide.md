---
title: "Facebook Ads Advanced Reporting Dashboards Guide"
category: "06_documentation"
tags: ["guide"]
created: "2025-10-29"
path: "06_documentation/Other/Guides/facebook_ads_advanced_reporting_dashboards_guide.md"
---

# Guía de Reportes Avanzados y Dashboards para Facebook Ads
## Sistemas de Reportes Inteligentes y Visualización de Datos

---

## 1. Introducción a los Reportes Avanzados

Esta guía proporciona técnicas avanzadas para crear sistemas de reportes inteligentes y dashboards interactivos para Facebook Ads, incluyendo visualización de datos, reportes automatizados, análisis en tiempo real y sistemas de alertas. Está diseñada para profesionales que buscan obtener insights profundos y tomar decisiones basadas en datos.

### Objetivos de los Reportes Avanzados
- Crear dashboards interactivos y visualizaciones avanzadas
- Automatizar generación de reportes
- Proporcionar análisis en tiempo real
- Facilitar toma de decisiones basada en datos
- Mejorar comunicación de insights

---

## 2. Fundamentos de Reportes Avanzados

### 2.1 Tipos de Reportes

**Reportes Operacionales:**
```
Daily Reports: Reportes diarios de performance
Weekly Reports: Análisis semanal de tendencias
Monthly Reports: Reportes mensuales ejecutivos
Quarterly Reports: Análisis trimestral estratégico
```

**Reportes Analíticos:**
```
Performance Analysis: Análisis de performance detallado
Trend Analysis: Análisis de tendencias temporales
Comparative Analysis: Análisis comparativo
Predictive Analysis: Análisis predictivo
```

**Reportes Ejecutivos:**
```
Executive Summary: Resumen ejecutivo
ROI Analysis: Análisis de ROI
Budget Analysis: Análisis de presupuestos
Strategic Insights: Insights estratégicos
```

### 2.2 Componentes de Dashboards

**Métricas Clave (KPIs):**
```
Primary KPIs: CTR, CPA, ROAS, Conversion Rate
Secondary KPIs: CPM, CPC, Engagement Rate
Tertiary KPIs: Brand Awareness, Customer Satisfaction
```

**Visualizaciones:**
```
Charts: Gráficos de barras, líneas, áreas
Tables: Tablas de datos detallados
Maps: Mapas geográficos
Gauges: Medidores de performance
```

**Filtros y Controles:**
```
Date Range: Rango de fechas
Campaign Filter: Filtro de campañas
Audience Filter: Filtro de audiencias
Metric Filter: Filtro de métricas
```

---

## 3. Dashboards Interactivos

### 3.1 Dashboard Principal con Streamlit

**Dashboard Completo:**
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time

class FacebookAdsDashboard:
    def __init__(self):
        self.data = None
        self.campaigns = None
        self.insights = None
        
    def load_data(self, access_token, ad_account_id):
        """Cargar datos de Facebook Ads API"""
        try:
            # Obtener campañas
            campaigns_url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/campaigns"
            campaigns_params = {
                'access_token': access_token,
                'fields': 'id,name,status,objective,created_time,daily_budget'
            }
            campaigns_response = requests.get(campaigns_url, params=campaigns_params)
            self.campaigns = campaigns_response.json()
            
            # Obtener insights
            insights_url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/insights"
            insights_params = {
                'access_token': access_token,
                'fields': 'campaign_id,campaign_name,impressions,clicks,spend,ctr,cpc,cpm,conversions,cost_per_conversion',
                'time_range': '{"since":"2024-01-01","until":"2024-12-31"}',
                'level': 'campaign'
            }
            insights_response = requests.get(insights_url, params=insights_params)
            self.insights = insights_response.json()
            
            # Convertir a DataFrame
            if self.insights.get('data'):
                self.data = pd.DataFrame(self.insights['data'])
                self.data['date'] = pd.to_datetime(self.data.get('date_start', datetime.now()))
                
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def create_sidebar_filters(self):
        """Crear filtros en la barra lateral"""
        st.sidebar.header("Filters")
        
        # Filtro de fechas
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        # Filtro de campañas
        if self.campaigns and self.campaigns.get('data'):
            campaign_names = [campaign['name'] for campaign in self.campaigns['data']]
            selected_campaigns = st.sidebar.multiselect(
                "Campaigns",
                campaign_names,
                default=campaign_names
            )
        else:
            selected_campaigns = []
        
        # Filtro de objetivos
        objectives = st.sidebar.multiselect(
            "Objectives",
            ["AWARENESS", "CONSIDERATION", "CONVERSIONS"],
            default=["AWARENESS", "CONSIDERATION", "CONVERSIONS"]
        )
        
        return {
            'date_range': date_range,
            'campaigns': selected_campaigns,
            'objectives': objectives
        }
    
    def create_kpi_cards(self, filtered_data):
        """Crear tarjetas de KPIs"""
        if filtered_data.empty:
            return
        
        # Calcular métricas
        total_spend = filtered_data['spend'].sum()
        total_impressions = filtered_data['impressions'].sum()
        total_clicks = filtered_data['clicks'].sum()
        total_conversions = filtered_data['conversions'].sum()
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        
        # Crear columnas para KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Spend",
                f"${total_spend:,.2f}",
                delta=f"${total_spend * 0.05:,.2f}"  # Simular cambio
            )
        
        with col2:
            st.metric(
                "CTR",
                f"{avg_ctr:.2f}%",
                delta=f"{avg_ctr * 0.1:.2f}%"  # Simular cambio
            )
        
        with col3:
            st.metric(
                "CPC",
                f"${avg_cpc:.2f}",
                delta=f"${avg_cpc * 0.05:.2f}"  # Simular cambio
            )
        
        with col4:
            st.metric(
                "CPA",
                f"${avg_cpa:.2f}",
                delta=f"${avg_cpa * 0.1:.2f}"  # Simular cambio
            )
    
    def create_performance_chart(self, filtered_data):
        """Crear gráfico de performance"""
        if filtered_data.empty:
            return
        
        # Agrupar por fecha
        daily_data = filtered_data.groupby('date').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calcular métricas diarias
        daily_data['ctr'] = (daily_data['clicks'] / daily_data['impressions'] * 100).fillna(0)
        daily_data['cpc'] = (daily_data['spend'] / daily_data['clicks']).fillna(0)
        daily_data['cpa'] = (daily_data['spend'] / daily_data['conversions']).fillna(0)
        
        # Crear gráfico
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Spend Over Time', 'CTR Over Time', 'CPC Over Time', 'CPA Over Time'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Gráfico de gasto
        fig.add_trace(
            go.Scatter(x=daily_data['date'], y=daily_data['spend'], name='Spend', line=dict(color='blue')),
            row=1, col=1
        )
        
        # Gráfico de CTR
        fig.add_trace(
            go.Scatter(x=daily_data['date'], y=daily_data['ctr'], name='CTR', line=dict(color='green')),
            row=1, col=2
        )
        
        # Gráfico de CPC
        fig.add_trace(
            go.Scatter(x=daily_data['date'], y=daily_data['cpc'], name='CPC', line=dict(color='red')),
            row=2, col=1
        )
        
        # Gráfico de CPA
        fig.add_trace(
            go.Scatter(x=daily_data['date'], y=daily_data['cpa'], name='CPA', line=dict(color='orange')),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, title_text="Performance Over Time")
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Value")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_campaign_comparison(self, filtered_data):
        """Crear comparación de campañas"""
        if filtered_data.empty:
            return
        
        # Agrupar por campaña
        campaign_data = filtered_data.groupby('campaign_name').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calcular métricas por campaña
        campaign_data['ctr'] = (campaign_data['clicks'] / campaign_data['impressions'] * 100).fillna(0)
        campaign_data['cpc'] = (campaign_data['spend'] / campaign_data['clicks']).fillna(0)
        campaign_data['cpa'] = (campaign_data['spend'] / campaign_data['conversions']).fillna(0)
        
        # Crear gráfico de barras
        fig = px.bar(
            campaign_data,
            x='campaign_name',
            y=['spend', 'impressions', 'clicks', 'conversions'],
            title="Campaign Performance Comparison",
            barmode='group'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Crear tabla de métricas
        st.subheader("Campaign Metrics Table")
        st.dataframe(campaign_data.round(2))
    
    def create_audience_analysis(self, filtered_data):
        """Crear análisis de audiencias"""
        if filtered_data.empty:
            return
        
        # Simular datos de audiencia (en implementación real, obtener de API)
        audience_data = pd.DataFrame([
            {'age_range': '18-24', 'gender': 'Male', 'spend': 1000, 'conversions': 50},
            {'age_range': '25-34', 'gender': 'Male', 'spend': 1500, 'conversions': 75},
            {'age_range': '35-44', 'gender': 'Male', 'spend': 1200, 'conversions': 60},
            {'age_range': '18-24', 'gender': 'Female', 'spend': 800, 'conversions': 40},
            {'age_range': '25-34', 'gender': 'Female', 'spend': 1300, 'conversions': 65},
            {'age_range': '35-44', 'gender': 'Female', 'spend': 1100, 'conversions': 55}
        ])
        
        # Crear gráfico de audiencia por edad
        fig1 = px.bar(
            audience_data.groupby('age_range').agg({'spend': 'sum', 'conversions': 'sum'}).reset_index(),
            x='age_range',
            y=['spend', 'conversions'],
            title="Audience Performance by Age",
            barmode='group'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Crear gráfico de audiencia por género
        fig2 = px.pie(
            audience_data.groupby('gender').agg({'spend': 'sum'}).reset_index(),
            values='spend',
            names='gender',
            title="Spend Distribution by Gender"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    def create_geographic_analysis(self, filtered_data):
        """Crear análisis geográfico"""
        if filtered_data.empty:
            return
        
        # Simular datos geográficos (en implementación real, obtener de API)
        geo_data = pd.DataFrame([
            {'country': 'United States', 'spend': 2000, 'conversions': 100},
            {'country': 'Canada', 'spend': 800, 'conversions': 40},
            {'country': 'United Kingdom', 'spend': 600, 'conversions': 30},
            {'country': 'Australia', 'spend': 400, 'conversions': 20},
            {'country': 'Germany', 'spend': 300, 'conversions': 15}
        ])
        
        # Crear mapa de calor
        fig = px.choropleth(
            geo_data,
            locations='country',
            locationmode='country names',
            color='spend',
            hover_name='country',
            hover_data=['conversions'],
            title="Spend by Country"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_insights_section(self, filtered_data):
        """Crear sección de insights"""
        st.subheader("Key Insights")
        
        if filtered_data.empty:
            st.warning("No data available for insights")
            return
        
        # Calcular insights
        total_spend = filtered_data['spend'].sum()
        total_conversions = filtered_data['conversions'].sum()
        avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0
        
        # Identificar campañas de mejor performance
        campaign_performance = filtered_data.groupby('campaign_name').agg({
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        campaign_performance['cpa'] = campaign_performance['spend'] / campaign_performance['conversions']
        best_campaign = campaign_performance.loc[campaign_performance['cpa'].idxmin()]
        
        # Crear insights
        insights = [
            f"Total spend: ${total_spend:,.2f}",
            f"Total conversions: {total_conversions:,.0f}",
            f"Average CPA: ${avg_cpa:.2f}",
            f"Best performing campaign: {best_campaign['campaign_name']} (CPA: ${best_campaign['cpa']:.2f})"
        ]
        
        for insight in insights:
            st.info(insight)
    
    def run_dashboard(self):
        """Ejecutar dashboard"""
        st.set_page_config(
            page_title="Facebook Ads Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 Facebook Ads Dashboard")
        
        # Configuración de API
        st.sidebar.header("API Configuration")
        access_token = st.sidebar.text_input("Access Token", type="password")
        ad_account_id = st.sidebar.text_input("Ad Account ID")
        
        if st.sidebar.button("Load Data"):
            if access_token and ad_account_id:
                with st.spinner("Loading data..."):
                    if self.load_data(access_token, ad_account_id):
                        st.success("Data loaded successfully!")
                    else:
                        st.error("Failed to load data")
            else:
                st.error("Please enter access token and ad account ID")
        
        if self.data is not None:
            # Crear filtros
            filters = self.create_sidebar_filters()
            
            # Aplicar filtros
            filtered_data = self.data.copy()
            
            if filters['date_range']:
                start_date, end_date = filters['date_range']
                filtered_data = filtered_data[
                    (filtered_data['date'] >= pd.to_datetime(start_date)) &
                    (filtered_data['date'] <= pd.to_datetime(end_date))
                ]
            
            if filters['campaigns']:
                filtered_data = filtered_data[filtered_data['campaign_name'].isin(filters['campaigns'])]
            
            # Crear KPIs
            self.create_kpi_cards(filtered_data)
            
            # Crear gráficos
            st.subheader("Performance Over Time")
            self.create_performance_chart(filtered_data)
            
            st.subheader("Campaign Comparison")
            self.create_campaign_comparison(filtered_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Audience Analysis")
                self.create_audience_analysis(filtered_data)
            
            with col2:
                st.subheader("Geographic Analysis")
                self.create_geographic_analysis(filtered_data)
            
            # Crear insights
            self.create_insights_section(filtered_data)
            
            # Botón de actualización
            if st.button("Refresh Data"):
                st.rerun()

# Uso del dashboard
if __name__ == "__main__":
    dashboard = FacebookAdsDashboard()
    dashboard.run_dashboard()
```

### 3.2 Dashboard con Plotly Dash

**Dashboard Avanzado:**
```python
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

class AdvancedFacebookAdsDashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.data = None
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Configurar layout del dashboard"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Facebook Ads Advanced Dashboard", className="header-title"),
                html.Div([
                    dcc.Input(
                        id="access-token",
                        type="password",
                        placeholder="Access Token",
                        style={"margin-right": "10px"}
                    ),
                    dcc.Input(
                        id="ad-account-id",
                        type="text",
                        placeholder="Ad Account ID",
                        style={"margin-right": "10px"}
                    ),
                    html.Button("Load Data", id="load-data-btn", n_clicks=0)
                ], className="header-controls")
            ], className="header"),
            
            # Filters
            html.Div([
                html.Div([
                    dcc.DatePickerRange(
                        id="date-range",
                        start_date=datetime.now() - timedelta(days=30),
                        end_date=datetime.now()
                    )
                ], className="filter-item"),
                
                html.Div([
                    dcc.Dropdown(
                        id="campaign-filter",
                        placeholder="Select Campaigns",
                        multi=True
                    )
                ], className="filter-item"),
                
                html.Div([
                    dcc.Dropdown(
                        id="objective-filter",
                        options=[
                            {"label": "Awareness", "value": "AWARENESS"},
                            {"label": "Consideration", "value": "CONSIDERATION"},
                            {"label": "Conversions", "value": "CONVERSIONS"}
                        ],
                        placeholder="Select Objectives",
                        multi=True
                    )
                ], className="filter-item")
            ], className="filters"),
            
            # KPI Cards
            html.Div([
                html.Div([
                    html.H3("Total Spend"),
                    html.H2(id="total-spend")
                ], className="kpi-card"),
                
                html.Div([
                    html.H3("CTR"),
                    html.H2(id="avg-ctr")
                ], className="kpi-card"),
                
                html.Div([
                    html.H3("CPC"),
                    html.H2(id="avg-cpc")
                ], className="kpi-card"),
                
                html.Div([
                    html.H3("CPA"),
                    html.H2(id="avg-cpa")
                ], className="kpi-card")
            ], className="kpi-cards"),
            
            # Charts
            html.Div([
                dcc.Graph(id="performance-chart")
            ], className="chart-container"),
            
            html.Div([
                dcc.Graph(id="campaign-comparison")
            ], className="chart-container"),
            
            html.Div([
                html.Div([
                    dcc.Graph(id="audience-analysis")
                ], className="half-width"),
                
                html.Div([
                    dcc.Graph(id="geographic-analysis")
                ], className="half-width")
            ], className="chart-row"),
            
            # Data Table
            html.Div([
                html.H3("Campaign Data"),
                html.Div(id="data-table")
            ], className="table-container")
        ])
    
    def setup_callbacks(self):
        """Configurar callbacks del dashboard"""
        
        @self.app.callback(
            [Output("campaign-filter", "options"),
             Output("campaign-filter", "value")],
            [Input("load-data-btn", "n_clicks")],
            [dash.dependencies.State("access-token", "value"),
             dash.dependencies.State("ad-account-id", "value")]
        )
        def load_campaigns(n_clicks, access_token, ad_account_id):
            if n_clicks > 0 and access_token and ad_account_id:
                try:
                    campaigns_url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/campaigns"
                    campaigns_params = {
                        'access_token': access_token,
                        'fields': 'id,name,status,objective'
                    }
                    campaigns_response = requests.get(campaigns_url, params=campaigns_params)
                    campaigns_data = campaigns_response.json()
                    
                    if campaigns_data.get('data'):
                        options = [{"label": campaign['name'], "value": campaign['name']} 
                                 for campaign in campaigns_data['data']]
                        values = [campaign['name'] for campaign in campaigns_data['data']]
                        return options, values
                    
                except Exception as e:
                    print(f"Error loading campaigns: {e}")
            
            return [], []
        
        @self.app.callback(
            [Output("total-spend", "children"),
             Output("avg-ctr", "children"),
             Output("avg-cpc", "children"),
             Output("avg-cpa", "children")],
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_kpis(start_date, end_date, selected_campaigns, selected_objectives):
            # Simular datos (en implementación real, cargar datos reales)
            data = self.generate_sample_data()
            
            # Aplicar filtros
            filtered_data = self.apply_filters(data, start_date, end_date, selected_campaigns, selected_objectives)
            
            if filtered_data.empty:
                return "$0", "0%", "$0", "$0"
            
            # Calcular métricas
            total_spend = filtered_data['spend'].sum()
            total_impressions = filtered_data['impressions'].sum()
            total_clicks = filtered_data['clicks'].sum()
            total_conversions = filtered_data['conversions'].sum()
            
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            
            return f"${total_spend:,.2f}", f"{avg_ctr:.2f}%", f"${avg_cpc:.2f}", f"${avg_cpa:.2f}"
        
        @self.app.callback(
            Output("performance-chart", "figure"),
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_performance_chart(start_date, end_date, selected_campaigns, selected_objectives):
            data = self.generate_sample_data()
            filtered_data = self.apply_filters(data, start_date, end_date, selected_campaigns, selected_objectives)
            
            if filtered_data.empty:
                return go.Figure()
            
            # Agrupar por fecha
            daily_data = filtered_data.groupby('date').agg({
                'spend': 'sum',
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            # Crear gráfico
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['spend'],
                mode='lines+markers',
                name='Spend',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['clicks'],
                mode='lines+markers',
                name='Clicks',
                line=dict(color='green'),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Performance Over Time",
                xaxis_title="Date",
                yaxis=dict(title="Spend", side="left"),
                yaxis2=dict(title="Clicks", side="right", overlaying="y"),
                hovermode='x unified'
            )
            
            return fig
        
        @self.app.callback(
            Output("campaign-comparison", "figure"),
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_campaign_comparison(start_date, end_date, selected_campaigns, selected_objectives):
            data = self.generate_sample_data()
            filtered_data = self.apply_filters(data, start_date, end_date, selected_campaigns, selected_objectives)
            
            if filtered_data.empty:
                return go.Figure()
            
            # Agrupar por campaña
            campaign_data = filtered_data.groupby('campaign_name').agg({
                'spend': 'sum',
                'conversions': 'sum'
            }).reset_index()
            
            # Crear gráfico de barras
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=campaign_data['campaign_name'],
                y=campaign_data['spend'],
                name='Spend',
                marker_color='blue'
            ))
            
            fig.add_trace(go.Bar(
                x=campaign_data['campaign_name'],
                y=campaign_data['conversions'],
                name='Conversions',
                marker_color='green',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Campaign Comparison",
                xaxis_title="Campaign",
                yaxis=dict(title="Spend", side="left"),
                yaxis2=dict(title="Conversions", side="right", overlaying="y"),
                barmode='group'
            )
            
            return fig
        
        @self.app.callback(
            Output("audience-analysis", "figure"),
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_audience_analysis(start_date, end_date, selected_campaigns, selected_objectives):
            # Simular datos de audiencia
            audience_data = pd.DataFrame([
                {'age_range': '18-24', 'spend': 1000, 'conversions': 50},
                {'age_range': '25-34', 'spend': 1500, 'conversions': 75},
                {'age_range': '35-44', 'spend': 1200, 'conversions': 60},
                {'age_range': '45-54', 'spend': 800, 'conversions': 40}
            ])
            
            fig = px.bar(
                audience_data,
                x='age_range',
                y=['spend', 'conversions'],
                title="Audience Performance by Age",
                barmode='group'
            )
            
            return fig
        
        @self.app.callback(
            Output("geographic-analysis", "figure"),
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_geographic_analysis(start_date, end_date, selected_campaigns, selected_objectives):
            # Simular datos geográficos
            geo_data = pd.DataFrame([
                {'country': 'United States', 'spend': 2000, 'conversions': 100},
                {'country': 'Canada', 'spend': 800, 'conversions': 40},
                {'country': 'United Kingdom', 'spend': 600, 'conversions': 30},
                {'country': 'Australia', 'spend': 400, 'conversions': 20}
            ])
            
            fig = px.pie(
                geo_data,
                values='spend',
                names='country',
                title="Spend Distribution by Country"
            )
            
            return fig
        
        @self.app.callback(
            Output("data-table", "children"),
            [Input("date-range", "start_date"),
             Input("date-range", "end_date"),
             Input("campaign-filter", "value"),
             Input("objective-filter", "value")]
        )
        def update_data_table(start_date, end_date, selected_campaigns, selected_objectives):
            data = self.generate_sample_data()
            filtered_data = self.apply_filters(data, start_date, end_date, selected_campaigns, selected_objectives)
            
            if filtered_data.empty:
                return "No data available"
            
            # Crear tabla
            table = html.Table([
                html.Thead([
                    html.Tr([html.Th(col) for col in filtered_data.columns])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(filtered_data.iloc[i][col]) for col in filtered_data.columns
                    ]) for i in range(len(filtered_data))
                ])
            ])
            
            return table
    
    def generate_sample_data(self):
        """Generar datos de muestra"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        campaigns = ['Campaign A', 'Campaign B', 'Campaign C', 'Campaign D']
        
        data = []
        for date in dates:
            for campaign in campaigns:
                data.append({
                    'date': date,
                    'campaign_name': campaign,
                    'spend': np.random.uniform(100, 1000),
                    'impressions': np.random.uniform(10000, 100000),
                    'clicks': np.random.uniform(100, 1000),
                    'conversions': np.random.uniform(10, 100)
                })
        
        return pd.DataFrame(data)
    
    def apply_filters(self, data, start_date, end_date, selected_campaigns, selected_objectives):
        """Aplicar filtros a los datos"""
        filtered_data = data.copy()
        
        if start_date and end_date:
            filtered_data = filtered_data[
                (filtered_data['date'] >= pd.to_datetime(start_date)) &
                (filtered_data['date'] <= pd.to_datetime(end_date))
            ]
        
        if selected_campaigns:
            filtered_data = filtered_data[filtered_data['campaign_name'].isin(selected_campaigns)]
        
        return filtered_data
    
    def run(self, debug=True, port=8050):
        """Ejecutar dashboard"""
        self.app.run_server(debug=debug, port=port)

# Uso del dashboard
if __name__ == "__main__":
    dashboard = AdvancedFacebookAdsDashboard()
    dashboard.run()
```

---

## 4. Sistemas de Reportes Automatizados

### 4.1 Generador de Reportes Automáticos

**Sistema de Reportes:**
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json
import os
from jinja2 import Template

class AutomatedReportGenerator:
    def __init__(self, access_token, ad_account_id, email_config):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.email_config = email_config
        self.report_templates = self.load_report_templates()
        
    def load_report_templates(self):
        """Cargar plantillas de reportes"""
        return {
            'daily': {
                'subject': 'Daily Facebook Ads Report - {date}',
                'template': 'daily_report_template.html'
            },
            'weekly': {
                'subject': 'Weekly Facebook Ads Report - {week}',
                'template': 'weekly_report_template.html'
            },
            'monthly': {
                'subject': 'Monthly Facebook Ads Report - {month}',
                'template': 'monthly_report_template.html'
            }
        }
    
    def fetch_facebook_data(self, start_date, end_date):
        """Obtener datos de Facebook Ads API"""
        try:
            # Obtener insights
            insights_url = f"https://graph.facebook.com/v18.0/act_{self.ad_account_id}/insights"
            insights_params = {
                'access_token': self.access_token,
                'fields': 'campaign_id,campaign_name,impressions,clicks,spend,ctr,cpc,cpm,conversions,cost_per_conversion',
                'time_range': f'{{"since":"{start_date}","until":"{end_date}"}}',
                'level': 'campaign'
            }
            
            response = requests.get(insights_url, params=insights_params)
            data = response.json()
            
            if data.get('data'):
                return pd.DataFrame(data['data'])
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching Facebook data: {e}")
            return pd.DataFrame()
    
    def calculate_metrics(self, data):
        """Calcular métricas del reporte"""
        if data.empty:
            return {}
        
        # Métricas agregadas
        total_spend = data['spend'].sum()
        total_impressions = data['impressions'].sum()
        total_clicks = data['clicks'].sum()
        total_conversions = data['conversions'].sum()
        
        # Métricas promedio
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        
        # Métricas por campaña
        campaign_metrics = data.groupby('campaign_name').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        campaign_metrics['ctr'] = (campaign_metrics['clicks'] / campaign_metrics['impressions'] * 100).fillna(0)
        campaign_metrics['cpc'] = (campaign_metrics['spend'] / campaign_metrics['clicks']).fillna(0)
        campaign_metrics['cpa'] = (campaign_metrics['spend'] / campaign_metrics['conversions']).fillna(0)
        
        # Identificar mejores y peores campañas
        best_campaign = campaign_metrics.loc[campaign_metrics['cpa'].idxmin()]
        worst_campaign = campaign_metrics.loc[campaign_metrics['cpa'].idxmax()]
        
        return {
            'total_spend': total_spend,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'avg_ctr': avg_ctr,
            'avg_cpc': avg_cpc,
            'avg_cpa': avg_cpa,
            'avg_cpm': avg_cpm,
            'campaign_metrics': campaign_metrics,
            'best_campaign': best_campaign,
            'worst_campaign': worst_campaign
        }
    
    def generate_insights(self, metrics, previous_metrics=None):
        """Generar insights del reporte"""
        insights = []
        
        # Insight de performance general
        if metrics['avg_ctr'] > 2.0:
            insights.append("✅ CTR above industry average (2.0%)")
        else:
            insights.append("⚠️ CTR below industry average (2.0%)")
        
        if metrics['avg_cpa'] < 50:
            insights.append("✅ CPA within acceptable range")
        else:
            insights.append("⚠️ CPA above target threshold")
        
        # Insight de mejores campañas
        insights.append(f"🏆 Best performing campaign: {metrics['best_campaign']['campaign_name']} (CPA: ${metrics['best_campaign']['cpa']:.2f})")
        
        # Insight de peores campañas
        insights.append(f"📉 Campaign needing attention: {metrics['worst_campaign']['campaign_name']} (CPA: ${metrics['worst_campaign']['cpa']:.2f})")
        
        # Comparación con período anterior
        if previous_metrics:
            ctr_change = metrics['avg_ctr'] - previous_metrics['avg_ctr']
            cpa_change = metrics['avg_cpa'] - previous_metrics['avg_cpa']
            
            if ctr_change > 0:
                insights.append(f"📈 CTR improved by {ctr_change:.2f}% vs previous period")
            else:
                insights.append(f"📉 CTR declined by {abs(ctr_change):.2f}% vs previous period")
            
            if cpa_change < 0:
                insights.append(f"📈 CPA improved by ${abs(cpa_change):.2f} vs previous period")
            else:
                insights.append(f"📉 CPA increased by ${cpa_change:.2f} vs previous period")
        
        return insights
    
    def create_html_report(self, report_type, metrics, insights, date_range):
        """Crear reporte HTML"""
        template_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Facebook Ads {report_type.title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #1877f2; color: white; padding: 20px; text-align: center; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric-card {{ background-color: #f0f2f5; padding: 20px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #1877f2; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                .insights {{ background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .campaign-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .campaign-table th, .campaign-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .campaign-table th {{ background-color: #1877f2; color: white; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Facebook Ads {report_type.title()} Report</h1>
                <p>{date_range}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">${metrics['total_spend']:,.2f}</div>
                    <div class="metric-label">Total Spend</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{metrics['avg_ctr']:.2f}%</div>
                    <div class="metric-label">Average CTR</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics['avg_cpc']:.2f}</div>
                    <div class="metric-label">Average CPC</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics['avg_cpa']:.2f}</div>
                    <div class="metric-label">Average CPA</div>
                </div>
            </div>
            
            <div class="insights">
                <h3>Key Insights</h3>
                <ul>
                    {"".join([f"<li>{insight}</li>" for insight in insights])}
                </ul>
            </div>
            
            <h3>Campaign Performance</h3>
            <table class="campaign-table">
                <tr>
                    <th>Campaign</th>
                    <th>Spend</th>
                    <th>Impressions</th>
                    <th>Clicks</th>
                    <th>Conversions</th>
                    <th>CTR</th>
                    <th>CPC</th>
                    <th>CPA</th>
                </tr>
                {"".join([f"""
                <tr>
                    <td>{row['campaign_name']}</td>
                    <td>${row['spend']:,.2f}</td>
                    <td>{row['impressions']:,.0f}</td>
                    <td>{row['clicks']:,.0f}</td>
                    <td>{row['conversions']:,.0f}</td>
                    <td>{row['ctr']:.2f}%</td>
                    <td>${row['cpc']:.2f}</td>
                    <td>${row['cpa']:.2f}</td>
                </tr>
                """ for _, row in metrics['campaign_metrics'].iterrows()])}
            </table>
            
            <div class="footer">
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return template_html
    
    def send_email_report(self, report_type, html_content, date_range):
        """Enviar reporte por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = self.report_templates[report_type]['subject'].format(
                date=date_range,
                week=date_range,
                month=date_range
            )
            
            # Agregar contenido HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def generate_daily_report(self):
        """Generar reporte diario"""
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = yesterday.strftime('%Y-%m-%d')
        
        # Obtener datos
        data = self.fetch_facebook_data(start_date, end_date)
        
        if data.empty:
            print("No data available for daily report")
            return
        
        # Calcular métricas
        metrics = self.calculate_metrics(data)
        
        # Generar insights
        insights = self.generate_insights(metrics)
        
        # Crear reporte HTML
        html_content = self.create_html_report('daily', metrics, insights, start_date)
        
        # Enviar email
        success = self.send_email_report('daily', html_content, start_date)
        
        if success:
            print(f"Daily report sent successfully for {start_date}")
        else:
            print(f"Failed to send daily report for {start_date}")
    
    def generate_weekly_report(self):
        """Generar reporte semanal"""
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Obtener datos
        data = self.fetch_facebook_data(start_date_str, end_date_str)
        
        if data.empty:
            print("No data available for weekly report")
            return
        
        # Calcular métricas
        metrics = self.calculate_metrics(data)
        
        # Generar insights
        insights = self.generate_insights(metrics)
        
        # Crear reporte HTML
        html_content = self.create_html_report('weekly', metrics, insights, f"{start_date_str} to {end_date_str}")
        
        # Enviar email
        success = self.send_email_report('weekly', html_content, f"Week of {start_date_str}")
        
        if success:
            print(f"Weekly report sent successfully for week of {start_date_str}")
        else:
            print(f"Failed to send weekly report for week of {start_date_str}")
    
    def generate_monthly_report(self):
        """Generar reporte mensual"""
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date.replace(day=1)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Obtener datos
        data = self.fetch_facebook_data(start_date_str, end_date_str)
        
        if data.empty:
            print("No data available for monthly report")
            return
        
        # Calcular métricas
        metrics = self.calculate_metrics(data)
        
        # Generar insights
        insights = self.generate_insights(metrics)
        
        # Crear reporte HTML
        html_content = self.create_html_report('monthly', metrics, insights, f"{start_date_str} to {end_date_str}")
        
        # Enviar email
        success = self.send_email_report('monthly', html_content, start_date.strftime('%B %Y'))
        
        if success:
            print(f"Monthly report sent successfully for {start_date.strftime('%B %Y')}")
        else:
            print(f"Failed to send monthly report for {start_date.strftime('%B %Y')}")

# Uso del generador de reportes
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    EMAIL_CONFIG = {
        'from': 'reports@yourcompany.com',
        'to': 'marketing@yourcompany.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    # Crear generador de reportes
    report_generator = AutomatedReportGenerator(ACCESS_TOKEN, AD_ACCOUNT_ID, EMAIL_CONFIG)
    
    # Generar reportes
    report_generator.generate_daily_report()
    report_generator.generate_weekly_report()
    report_generator.generate_monthly_report()
```

---

## 5. Herramientas de Visualización Avanzada

### 5.1 Dashboard con Tableau

**Configuración de Tableau:**
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

class TableauDashboardConnector:
    def __init__(self, access_token, ad_account_id):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.data = None
        
    def fetch_data_for_tableau(self, start_date, end_date):
        """Obtener datos para Tableau"""
        try:
            # Obtener insights
            insights_url = f"https://graph.facebook.com/v18.0/act_{self.ad_account_id}/insights"
            insights_params = {
                'access_token': self.access_token,
                'fields': 'campaign_id,campaign_name,impressions,clicks,spend,ctr,cpc,cpm,conversions,cost_per_conversion,date_start,date_stop',
                'time_range': f'{{"since":"{start_date}","until":"{end_date}"}}',
                'level': 'campaign'
            }
            
            response = requests.get(insights_url, params=insights_params)
            data = response.json()
            
            if data.get('data'):
                df = pd.DataFrame(data['data'])
                
                # Preparar datos para Tableau
                df['date'] = pd.to_datetime(df['date_start'])
                df['spend'] = pd.to_numeric(df['spend'])
                df['impressions'] = pd.to_numeric(df['impressions'])
                df['clicks'] = pd.to_numeric(df['clicks'])
                df['conversions'] = pd.to_numeric(df['conversions'])
                df['ctr'] = pd.to_numeric(df['ctr'])
                df['cpc'] = pd.to_numeric(df['cpc'])
                df['cpm'] = pd.to_numeric(df['cpm'])
                df['cost_per_conversion'] = pd.to_numeric(df['cost_per_conversion'])
                
                # Crear características adicionales
                df['week'] = df['date'].dt.isocalendar().week
                df['month'] = df['date'].dt.month
                df['quarter'] = df['date'].dt.quarter
                df['day_of_week'] = df['date'].dt.day_name()
                df['is_weekend'] = df['date'].dt.weekday >= 5
                
                # Calcular métricas derivadas
                df['roas'] = df['conversions'] * 50 / df['spend']  # Asumiendo valor promedio de conversión
                df['conversion_rate'] = df['conversions'] / df['clicks'] * 100
                df['engagement_rate'] = df['clicks'] / df['impressions'] * 100
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching data for Tableau: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, data, filename):
        """Exportar datos a CSV para Tableau"""
        try:
            data.to_csv(filename, index=False)
            print(f"Data exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def create_tableau_workbook_config(self):
        """Crear configuración de workbook de Tableau"""
        config = {
            'data_source': 'Facebook_Ads_Data.csv',
            'sheets': [
                {
                    'name': 'Performance Overview',
                    'charts': [
                        {'type': 'line', 'x': 'date', 'y': 'spend', 'title': 'Spend Over Time'},
                        {'type': 'bar', 'x': 'campaign_name', 'y': 'conversions', 'title': 'Conversions by Campaign'},
                        {'type': 'scatter', 'x': 'spend', 'y': 'conversions', 'title': 'Spend vs Conversions'}
                    ]
                },
                {
                    'name': 'Campaign Analysis',
                    'charts': [
                        {'type': 'table', 'columns': ['campaign_name', 'spend', 'conversions', 'ctr', 'cpc', 'cpa']},
                        {'type': 'bar', 'x': 'campaign_name', 'y': 'roas', 'title': 'ROAS by Campaign'}
                    ]
                },
                {
                    'name': 'Trend Analysis',
                    'charts': [
                        {'type': 'line', 'x': 'date', 'y': 'ctr', 'title': 'CTR Trend'},
                        {'type': 'line', 'x': 'date', 'y': 'cpc', 'title': 'CPC Trend'},
                        {'type': 'line', 'x': 'date', 'y': 'cpa', 'title': 'CPA Trend'}
                    ]
                }
            ],
            'filters': [
                {'field': 'date', 'type': 'date_range'},
                {'field': 'campaign_name', 'type': 'multi_select'},
                {'field': 'is_weekend', 'type': 'boolean'}
            ],
            'parameters': [
                {'name': 'Target CPA', 'type': 'float', 'default': 50},
                {'name': 'Target CTR', 'type': 'float', 'default': 2.0}
            ]
        }
        
        return config

# Uso del conector de Tableau
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    # Crear conector
    tableau_connector = TableauDashboardConnector(ACCESS_TOKEN, AD_ACCOUNT_ID)
    
    # Obtener datos
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    data = tableau_connector.fetch_data_for_tableau(start_date, end_date)
    
    if not data.empty:
        # Exportar a CSV
        tableau_connector.export_to_csv(data, 'Facebook_Ads_Data.csv')
        
        # Crear configuración
        config = tableau_connector.create_tableau_workbook_config()
        
        # Guardar configuración
        with open('tableau_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("Tableau configuration created successfully")
    else:
        print("No data available for Tableau")
```

---

## Conclusión

Los reportes avanzados y dashboards proporcionan una ventaja competitiva significativa al facilitar la toma de decisiones basada en datos y la comunicación de insights. La implementación exitosa requiere:

**Elementos Clave:**
1. **Dashboards Interactivos**: Visualizaciones avanzadas y controles dinámicos
2. **Reportes Automatizados**: Generación y envío automático de reportes
3. **Análisis en Tiempo Real**: Monitoreo continuo de performance
4. **Visualizaciones Avanzadas**: Gráficos y tablas informativas
5. **Sistemas de Alertas**: Notificaciones automáticas de cambios importantes

**Beneficios:**
- Toma de decisiones basada en datos
- Comunicación efectiva de insights
- Monitoreo continuo de performance
- Automatización de reportes
- Mejora en eficiencia operacional

**Próximos Pasos:**
1. Implementar dashboards interactivos
2. Configurar reportes automatizados
3. Desarrollar visualizaciones avanzadas
4. Establecer sistemas de alertas
5. Optimizar continuamente basándose en feedback

La implementación exitosa de reportes avanzados resultará en un sistema de Facebook Ads altamente informativo, eficiente y orientado a resultados.


