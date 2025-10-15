"""
Motor de Visualización Avanzada
Sistema de visualización interactiva con gráficos dinámicos, dashboards y análisis visual
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import seaborn as sns
import bokeh.plotting as bk
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.layouts import column, row
import altair as alt
import streamlit as st

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    CORRELATION = "correlation"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    SANKEY = "sankey"
    CANDLESTICK = "candlestick"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    INDICATOR = "indicator"

class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    REAL_TIME = "real_time"
    CUSTOM = "custom"

@dataclass
class VisualizationConfig:
    chart_id: str
    chart_type: ChartType
    title: str
    data_source: str
    x_column: str
    y_column: str
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    filters: Dict[str, Any] = None
    styling: Dict[str, Any] = None

@dataclass
class DashboardConfig:
    dashboard_id: str
    dashboard_type: DashboardType
    title: str
    description: str
    charts: List[VisualizationConfig]
    layout: Dict[str, Any] = None
    refresh_interval: int = 60
    auto_refresh: bool = True

class AdvancedVisualizationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.charts = {}
        self.dashboards = {}
        self.data_sources = {}
        self.visualization_templates = {}
        self.interactive_features = {}
        
        # Configuración por defecto
        self.default_styling = {
            "color_scheme": "plotly",
            "font_family": "Arial",
            "font_size": 12,
            "background_color": "white",
            "grid_color": "lightgray",
            "title_font_size": 16,
            "axis_font_size": 12
        }
        
    async def create_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> Dict[str, Any]:
        """Crear gráfico avanzado"""
        try:
            chart_result = {
                "chart_id": config.chart_id,
                "chart_type": config.chart_type.value,
                "title": config.title,
                "data_points": len(data),
                "created_at": datetime.now().isoformat()
            }
            
            # Crear gráfico según tipo
            if config.chart_type == ChartType.LINE:
                chart_result["figure"] = await self._create_line_chart(config, data)
            elif config.chart_type == ChartType.BAR:
                chart_result["figure"] = await self._create_bar_chart(config, data)
            elif config.chart_type == ChartType.SCATTER:
                chart_result["figure"] = await self._create_scatter_chart(config, data)
            elif config.chart_type == ChartType.HISTOGRAM:
                chart_result["figure"] = await self._create_histogram_chart(config, data)
            elif config.chart_type == ChartType.BOX:
                chart_result["figure"] = await self._create_box_chart(config, data)
            elif config.chart_type == ChartType.HEATMAP:
                chart_result["figure"] = await self._create_heatmap_chart(config, data)
            elif config.chart_type == ChartType.CORRELATION:
                chart_result["figure"] = await self._create_correlation_chart(config, data)
            elif config.chart_type == ChartType.TREEMAP:
                chart_result["figure"] = await self._create_treemap_chart(config, data)
            elif config.chart_type == ChartType.SUNBURST:
                chart_result["figure"] = await self._create_sunburst_chart(config, data)
            elif config.chart_type == ChartType.SANKEY:
                chart_result["figure"] = await self._create_sankey_chart(config, data)
            elif config.chart_type == ChartType.CANDLESTICK:
                chart_result["figure"] = await self._create_candlestick_chart(config, data)
            elif config.chart_type == ChartType.WATERFALL:
                chart_result["figure"] = await self._create_waterfall_chart(config, data)
            elif config.chart_type == ChartType.FUNNEL:
                chart_result["figure"] = await self._create_funnel_chart(config, data)
            elif config.chart_type == ChartType.GAUGE:
                chart_result["figure"] = await self._create_gauge_chart(config, data)
            elif config.chart_type == ChartType.INDICATOR:
                chart_result["figure"] = await self._create_indicator_chart(config, data)
            
            # Guardar gráfico
            self.charts[config.chart_id] = chart_result
            
            return chart_result
            
        except Exception as e:
            self.logger.error(f"Error creating chart: {e}")
            raise
    
    async def _create_line_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de líneas"""
        try:
            fig = go.Figure()
            
            # Agregar línea principal
            fig.add_trace(go.Scatter(
                x=data[config.x_column],
                y=data[config.y_column],
                mode='lines+markers',
                name=config.y_column,
                line=dict(width=3),
                marker=dict(size=6)
            ))
            
            # Agregar línea de tendencia si hay suficientes puntos
            if len(data) > 10:
                z = np.polyfit(range(len(data)), data[config.y_column], 1)
                p = np.poly1d(z)
                fig.add_trace(go.Scatter(
                    x=data[config.x_column],
                    y=p(range(len(data))),
                    mode='lines',
                    name='Trend',
                    line=dict(dash='dash', color='red')
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_column,
                yaxis_title=config.y_column,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating line chart: {e}")
            raise
    
    async def _create_bar_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de barras"""
        try:
            fig = go.Figure()
            
            # Agrupar datos si hay columna de color
            if config.color_column:
                grouped_data = data.groupby([config.x_column, config.color_column])[config.y_column].sum().reset_index()
                
                for color_value in grouped_data[config.color_column].unique():
                    color_data = grouped_data[grouped_data[config.color_column] == color_value]
                    fig.add_trace(go.Bar(
                        x=color_data[config.x_column],
                        y=color_data[config.y_column],
                        name=str(color_value),
                        text=color_data[config.y_column],
                        textposition='auto'
                    ))
            else:
                fig.add_trace(go.Bar(
                    x=data[config.x_column],
                    y=data[config.y_column],
                    text=data[config.y_column],
                    textposition='auto'
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_column,
                yaxis_title=config.y_column,
                barmode='group' if config.color_column else 'stack',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating bar chart: {e}")
            raise
    
    async def _create_scatter_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de dispersión"""
        try:
            fig = go.Figure()
            
            # Crear gráfico de dispersión
            scatter = go.Scatter(
                x=data[config.x_column],
                y=data[config.y_column],
                mode='markers',
                marker=dict(
                    size=data[config.size_column] if config.size_column else 8,
                    color=data[config.color_column] if config.color_column else 'blue',
                    colorscale='Viridis',
                    showscale=bool(config.color_column),
                    colorbar=dict(title=config.color_column) if config.color_column else None
                ),
                text=data.index,
                hovertemplate=f'<b>{config.x_column}</b>: %{{x}}<br>' +
                             f'<b>{config.y_column}</b>: %{{y}}<br>' +
                             '<extra></extra>'
            )
            
            fig.add_trace(scatter)
            
            # Agregar línea de regresión
            if len(data) > 10:
                z = np.polyfit(data[config.x_column], data[config.y_column], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(data[config.x_column].min(), data[config.x_column].max(), 100)
                y_trend = p(x_trend)
                
                fig.add_trace(go.Scatter(
                    x=x_trend,
                    y=y_trend,
                    mode='lines',
                    name='Regression Line',
                    line=dict(dash='dash', color='red')
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_column,
                yaxis_title=config.y_column,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating scatter chart: {e}")
            raise
    
    async def _create_histogram_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear histograma"""
        try:
            fig = go.Figure()
            
            # Crear histograma
            fig.add_trace(go.Histogram(
                x=data[config.y_column],
                nbinsx=30,
                name=config.y_column,
                opacity=0.7
            ))
            
            # Agregar curva de densidad
            if len(data) > 100:
                from scipy import stats
                kde = stats.gaussian_kde(data[config.y_column])
                x_range = np.linspace(data[config.y_column].min(), data[config.y_column].max(), 100)
                y_kde = kde(x_range)
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_kde * len(data) * (data[config.y_column].max() - data[config.y_column].min()) / 30,
                    mode='lines',
                    name='Density',
                    line=dict(color='red', width=2)
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.y_column,
                yaxis_title='Frequency',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating histogram chart: {e}")
            raise
    
    async def _create_box_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de cajas"""
        try:
            fig = go.Figure()
            
            # Crear gráfico de cajas
            if config.color_column:
                for color_value in data[config.color_column].unique():
                    color_data = data[data[config.color_column] == color_value]
                    fig.add_trace(go.Box(
                        y=color_data[config.y_column],
                        name=str(color_value),
                        boxpoints='outliers'
                    ))
            else:
                fig.add_trace(go.Box(
                    y=data[config.y_column],
                    name=config.y_column,
                    boxpoints='outliers'
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                yaxis_title=config.y_column,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating box chart: {e}")
            raise
    
    async def _create_heatmap_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear mapa de calor"""
        try:
            # Crear matriz de correlación si no se especifica
            if config.x_column == "correlation":
                corr_matrix = data.corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0
                ))
            else:
                # Crear heatmap personalizado
                pivot_data = data.pivot_table(
                    values=config.y_column,
                    index=config.x_column,
                    columns=config.color_column if config.color_column else 'index',
                    aggfunc='mean'
                )
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    colorscale='Viridis'
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating heatmap chart: {e}")
            raise
    
    async def _create_correlation_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de correlación"""
        try:
            # Calcular matriz de correlación
            corr_matrix = data.corr()
            
            # Crear heatmap de correlación
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values,
                texttemplate="%{text:.2f}",
                textfont={"size": 10}
            ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating correlation chart: {e}")
            raise
    
    async def _create_treemap_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de treemap"""
        try:
            # Agrupar datos
            grouped_data = data.groupby(config.x_column)[config.y_column].sum().reset_index()
            
            # Crear treemap
            fig = go.Figure(go.Treemap(
                labels=grouped_data[config.x_column],
                values=grouped_data[config.y_column],
                textinfo="label+value+percent parent"
            ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating treemap chart: {e}")
            raise
    
    async def _create_sunburst_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de sunburst"""
        try:
            # Agrupar datos por múltiples niveles
            if config.color_column:
                grouped_data = data.groupby([config.x_column, config.color_column])[config.y_column].sum().reset_index()
                
                # Crear jerarquía
                ids = []
                labels = []
                parents = []
                values = []
                
                for _, row in grouped_data.iterrows():
                    parent_id = f"parent_{row[config.x_column]}"
                    child_id = f"child_{row[config.x_column]}_{row[config.color_column]}"
                    
                    # Agregar padre si no existe
                    if parent_id not in ids:
                        ids.append(parent_id)
                        labels.append(row[config.x_column])
                        parents.append("")
                        values.append(0)
                    
                    # Agregar hijo
                    ids.append(child_id)
                    labels.append(f"{row[config.color_column]}: {row[config.y_column]}")
                    parents.append(parent_id)
                    values.append(row[config.y_column])
                
                fig = go.Figure(go.Sunburst(
                    ids=ids,
                    labels=labels,
                    parents=parents,
                    values=values
                ))
            else:
                # Sunburst simple
                fig = go.Figure(go.Sunburst(
                    labels=data[config.x_column],
                    values=data[config.y_column]
                ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating sunburst chart: {e}")
            raise
    
    async def _create_sankey_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de Sankey"""
        try:
            # Crear diagrama de Sankey
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=data[config.x_column].unique().tolist()
                ),
                link=dict(
                    source=[0] * len(data),  # Simplificado
                    target=[1] * len(data),
                    value=data[config.y_column].tolist()
                )
            )])
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating sankey chart: {e}")
            raise
    
    async def _create_candlestick_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de velas"""
        try:
            # Crear gráfico de velas
            fig = go.Figure(data=go.Candlestick(
                x=data[config.x_column],
                open=data.get('open', data[config.y_column]),
                high=data.get('high', data[config.y_column] * 1.1),
                low=data.get('low', data[config.y_column] * 0.9),
                close=data[config.y_column]
            ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_column,
                yaxis_title=config.y_column,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating candlestick chart: {e}")
            raise
    
    async def _create_waterfall_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de cascada"""
        try:
            # Crear gráfico de cascada
            fig = go.Figure(go.Waterfall(
                name="Waterfall",
                orientation="v",
                measure=["relative"] * len(data),
                x=data[config.x_column],
                y=data[config.y_column],
                connector={"line": {"color": "rgb(63, 63, 63)"}}
            ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_column,
                yaxis_title=config.y_column,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating waterfall chart: {e}")
            raise
    
    async def _create_funnel_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de embudo"""
        try:
            # Crear gráfico de embudo
            fig = go.Figure(go.Funnel(
                y=data[config.x_column],
                x=data[config.y_column]
            ))
            
            # Configurar layout
            fig.update_layout(
                title=config.title,
                xaxis_title=config.y_column,
                yaxis_title=config.x_column,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating funnel chart: {e}")
            raise
    
    async def _create_gauge_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de medidor"""
        try:
            # Crear gráfico de medidor
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=data[config.y_column].iloc[-1],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': config.title},
                delta={'reference': data[config.y_column].mean()},
                gauge={
                    'axis': {'range': [None, data[config.y_column].max()]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, data[config.y_column].quantile(0.25)], 'color': "lightgray"},
                        {'range': [data[config.y_column].quantile(0.25), data[config.y_column].quantile(0.75)], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': data[config.y_column].quantile(0.9)
                    }
                }
            ))
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating gauge chart: {e}")
            raise
    
    async def _create_indicator_chart(self, config: VisualizationConfig, data: pd.DataFrame) -> go.Figure:
        """Crear gráfico de indicador"""
        try:
            # Crear gráfico de indicador
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=data[config.y_column].iloc[-1],
                delta={"reference": data[config.y_column].iloc[-2] if len(data) > 1 else 0},
                title={"text": config.title}
            ))
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating indicator chart: {e}")
            raise
    
    async def create_dashboard(self, config: DashboardConfig) -> Dict[str, Any]:
        """Crear dashboard avanzado"""
        try:
            dashboard_result = {
                "dashboard_id": config.dashboard_id,
                "dashboard_type": config.dashboard_type.value,
                "title": config.title,
                "description": config.description,
                "charts": [],
                "created_at": datetime.now().isoformat()
            }
            
            # Crear gráficos del dashboard
            for chart_config in config.charts:
                # Simular datos para el gráfico
                data = await self._get_sample_data(chart_config)
                chart_result = await self.create_chart(chart_config, data)
                dashboard_result["charts"].append(chart_result)
            
            # Guardar dashboard
            self.dashboards[config.dashboard_id] = dashboard_result
            
            return dashboard_result
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise
    
    async def _get_sample_data(self, config: VisualizationConfig) -> pd.DataFrame:
        """Obtener datos de muestra para el gráfico"""
        try:
            # Generar datos de muestra
            np.random.seed(42)
            n_samples = 100
            
            data = pd.DataFrame({
                'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
                'price': np.random.normal(100, 20, n_samples),
                'volume': np.random.normal(1000, 200, n_samples),
                'category': np.random.choice(['A', 'B', 'C'], n_samples),
                'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples)
            })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting sample data: {e}")
            raise
    
    async def create_interactive_dashboard(self, config: DashboardConfig) -> str:
        """Crear dashboard interactivo con Dash"""
        try:
            # Crear aplicación Dash
            app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
            
            # Crear layout del dashboard
            layout = dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1(config.title, className="text-center mb-4"),
                        html.P(config.description, className="text-center mb-4")
                    ])
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id=f"chart-{chart_config.chart_id}")
                    ], width=6) for chart_config in config.charts[:2]
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id=f"chart-{chart_config.chart_id}")
                    ], width=6) for chart_config in config.charts[2:4]
                ]),
                
                dcc.Interval(
                    id='interval-component',
                    interval=config.refresh_interval * 1000,
                    n_intervals=0
                )
            ])
            
            app.layout = layout
            
            # Crear callbacks para actualización automática
            @app.callback(
                [Output(f"chart-{chart_config.chart_id}", "figure") for chart_config in config.charts],
                [Input('interval-component', 'n_intervals')]
            )
            def update_charts(n):
                figures = []
                for chart_config in config.charts:
                    data = await self._get_sample_data(chart_config)
                    chart_result = await self.create_chart(chart_config, data)
                    figures.append(chart_result["figure"])
                return figures
            
            # Ejecutar aplicación
            app.run_server(debug=True, port=8050)
            
            return f"Dashboard running at http://localhost:8050"
            
        except Exception as e:
            self.logger.error(f"Error creating interactive dashboard: {e}")
            raise
    
    async def export_chart(self, chart_id: str, format: str = "html") -> str:
        """Exportar gráfico"""
        try:
            if chart_id not in self.charts:
                raise ValueError(f"Chart {chart_id} not found")
            
            chart = self.charts[chart_id]
            figure = chart["figure"]
            
            if format == "html":
                return figure.to_html()
            elif format == "png":
                return figure.to_image(format="png")
            elif format == "pdf":
                return figure.to_image(format="pdf")
            elif format == "svg":
                return figure.to_image(format="svg")
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting chart: {e}")
            raise
    
    async def get_visualization_insights(self) -> Dict[str, Any]:
        """Obtener insights de visualización"""
        insights = {
            "total_charts": len(self.charts),
            "total_dashboards": len(self.dashboards),
            "chart_types_used": {},
            "dashboard_types_used": {},
            "most_used_chart_type": None,
            "average_chart_data_points": 0
        }
        
        if self.charts:
            # Análisis de tipos de gráficos
            chart_types = [chart["chart_type"] for chart in self.charts.values()]
            for chart_type in chart_types:
                insights["chart_types_used"][chart_type] = insights["chart_types_used"].get(chart_type, 0) + 1
            
            insights["most_used_chart_type"] = max(insights["chart_types_used"], key=insights["chart_types_used"].get)
            
            # Promedio de puntos de datos
            data_points = [chart["data_points"] for chart in self.charts.values()]
            insights["average_chart_data_points"] = np.mean(data_points) if data_points else 0
        
        if self.dashboards:
            # Análisis de tipos de dashboards
            dashboard_types = [dashboard["dashboard_type"] for dashboard in self.dashboards.values()]
            for dashboard_type in dashboard_types:
                insights["dashboard_types_used"][dashboard_type] = insights["dashboard_types_used"].get(dashboard_type, 0) + 1
        
        return insights

# Función principal para inicializar el motor
async def initialize_visualization_engine() -> AdvancedVisualizationEngine:
    """Inicializar motor de visualización avanzada"""
    engine = AdvancedVisualizationEngine()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    return engine

if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        engine = await initialize_visualization_engine()
        
        # Crear configuración de gráfico
        chart_config = VisualizationConfig(
            chart_id="price_trend_chart",
            chart_type=ChartType.LINE,
            title="Price Trend Analysis",
            data_source="pricing_data",
            x_column="timestamp",
            y_column="price"
        )
        
        # Crear datos de muestra
        data = await engine._get_sample_data(chart_config)
        
        # Crear gráfico
        chart_result = await engine.create_chart(chart_config, data)
        print("Chart created:", chart_result["chart_id"])
        
        # Crear configuración de dashboard
        dashboard_config = DashboardConfig(
            dashboard_id="executive_dashboard",
            dashboard_type=DashboardType.EXECUTIVE,
            title="Executive Dashboard",
            description="High-level overview of key metrics",
            charts=[chart_config]
        )
        
        # Crear dashboard
        dashboard_result = await engine.create_dashboard(dashboard_config)
        print("Dashboard created:", dashboard_result["dashboard_id"])
        
        # Obtener insights
        insights = await engine.get_visualization_insights()
        print("Visualization Insights:", json.dumps(insights, indent=2, default=str))
    
    asyncio.run(main())



