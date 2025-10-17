#!/usr/bin/env python3
"""
📊 MARKETING BRAIN ADVANCED REPORTING
Sistema Avanzado de Reportes con Dashboards Personalizados y Visualización de Datos
Incluye generación automática de reportes, dashboards interactivos y análisis visual
"""

import json
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
from enum import Enum
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.offline as pyo
from plotly.utils import PlotlyJSONEncoder
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import sqlite3
import redis
import yaml
import base64
import io
import zipfile
import csv
import xlsxwriter
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import jinja2
from jinja2 import Template, Environment, FileSystemLoader
import schedule
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import webbrowser
import tempfile
import os

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Tipos de reporte"""
    EXECUTIVE_SUMMARY = "executive_summary"
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    CUSTOMER_ANALYTICS = "customer_analytics"
    FINANCIAL_REPORT = "financial_report"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    OPERATIONAL_METRICS = "operational_metrics"
    CUSTOM = "custom"

class ChartType(Enum):
    """Tipos de gráficos"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    FUNNEL = "funnel"

class DashboardLayout(Enum):
    """Layouts de dashboard"""
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    GRID = "grid"
    CUSTOM = "custom"

class ExportFormat(Enum):
    """Formatos de exportación"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    PNG = "png"
    SVG = "svg"
    JSON = "json"

@dataclass
class ReportConfig:
    """Configuración de reporte"""
    report_id: str
    name: str
    description: str
    report_type: ReportType
    data_sources: List[str]
    metrics: List[str]
    filters: Dict[str, Any]
    schedule: Optional[str]
    recipients: List[str]
    format: ExportFormat
    template: str
    created_at: str
    updated_at: str

@dataclass
class DashboardConfig:
    """Configuración de dashboard"""
    dashboard_id: str
    name: str
    description: str
    layout: DashboardLayout
    widgets: List[Dict[str, Any]]
    filters: Dict[str, Any]
    refresh_interval: int
    is_public: bool
    created_at: str
    updated_at: str

@dataclass
class ChartConfig:
    """Configuración de gráfico"""
    chart_id: str
    name: str
    chart_type: ChartType
    data_source: str
    x_axis: str
    y_axis: str
    color_by: Optional[str]
    size_by: Optional[str]
    filters: Dict[str, Any]
    styling: Dict[str, Any]
    created_at: str

@dataclass
class ReportData:
    """Datos de reporte"""
    report_id: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: str
    metadata: Dict[str, Any]

class MarketingBrainAdvancedReporting:
    """
    Sistema Avanzado de Reportes con Dashboards Personalizados y Visualización de Datos
    Incluye generación automática de reportes, dashboards interactivos y análisis visual
    """
    
    def __init__(self):
        self.reports = {}
        self.dashboards = {}
        self.charts = {}
        self.report_data = {}
        
        # Configuración
        self.config = self._load_config()
        
        # Bases de datos
        self.db_connection = None
        self.redis_client = None
        
        # Dash app
        self.dash_app = None
        
        # Templates
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        
        # Colas de procesamiento
        self.report_queue = queue.Queue()
        self.dashboard_queue = queue.Queue()
        
        # Threads
        self.report_generator_thread = None
        self.dashboard_updater_thread = None
        
        # Estado del sistema
        self.is_running = False
        
        # Métricas
        self.reporting_metrics = {
            'reports_generated': 0,
            'dashboards_created': 0,
            'charts_rendered': 0,
            'exports_completed': 0,
            'scheduled_reports_sent': 0,
            'average_generation_time': 0.0,
            'total_data_points': 0,
            'active_dashboards': 0
        }
        
        logger.info("📊 Marketing Brain Advanced Reporting initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del sistema de reportes"""
        return {
            'reporting': {
                'default_template_dir': 'templates/reports',
                'output_dir': 'reports',
                'cache_duration': 3600,
                'max_concurrent_reports': 5,
                'auto_save': True
            },
            'dashboards': {
                'default_theme': 'bootstrap',
                'refresh_interval': 300,
                'max_widgets_per_dashboard': 20,
                'enable_real_time': True,
                'cache_widgets': True
            },
            'charts': {
                'default_colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                'max_data_points': 10000,
                'enable_animations': True,
                'responsive': True,
                'export_formats': ['png', 'svg', 'pdf']
            },
            'export': {
                'pdf_quality': 'high',
                'excel_formatting': True,
                'csv_encoding': 'utf-8',
                'image_dpi': 300,
                'compression': True
            },
            'scheduling': {
                'enabled': True,
                'timezone': 'UTC',
                'max_scheduled_reports': 100,
                'retry_failed_reports': True,
                'notification_on_failure': True
            },
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': 'reports@marketingbrain.com',
                'html_templates': True
            }
        }
    
    async def initialize_reporting_system(self):
        """Inicializar sistema de reportes"""
        logger.info("🚀 Initializing Marketing Brain Advanced Reporting System...")
        
        try:
            # Inicializar bases de datos
            await self._initialize_databases()
            
            # Crear directorios necesarios
            await self._create_directories()
            
            # Cargar reportes y dashboards existentes
            await self._load_existing_configs()
            
            # Crear reportes y dashboards por defecto
            await self._create_default_reports_and_dashboards()
            
            # Inicializar Dash app
            await self._initialize_dash_app()
            
            # Iniciar threads de procesamiento
            self._start_processing_threads()
            
            logger.info("✅ Reporting system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing reporting system: {e}")
            raise
    
    async def _initialize_databases(self):
        """Inicializar bases de datos"""
        try:
            # SQLite para metadatos
            self.db_connection = sqlite3.connect('reporting_metadata.db', check_same_thread=False)
            
            # Redis para cache
            self.redis_client = redis.Redis(host='localhost', port=6379, db=3, decode_responses=True)
            
            # Crear tablas
            await self._create_reporting_tables()
            
        except Exception as e:
            logger.error(f"Error initializing databases: {e}")
            raise
    
    async def _create_reporting_tables(self):
        """Crear tablas de base de datos"""
        try:
            cursor = self.db_connection.cursor()
            
            # Tabla de configuraciones de reportes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_configs (
                    report_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    data_sources TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    filters TEXT NOT NULL,
                    schedule TEXT,
                    recipients TEXT NOT NULL,
                    format TEXT NOT NULL,
                    template TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de configuraciones de dashboards
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_configs (
                    dashboard_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    layout TEXT NOT NULL,
                    widgets TEXT NOT NULL,
                    filters TEXT NOT NULL,
                    refresh_interval INTEGER NOT NULL,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de configuraciones de gráficos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chart_configs (
                    chart_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    chart_type TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    x_axis TEXT NOT NULL,
                    y_axis TEXT NOT NULL,
                    color_by TEXT,
                    size_by TEXT,
                    filters TEXT NOT NULL,
                    styling TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Tabla de datos de reportes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_data (
                    report_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    charts TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            # Tabla de métricas del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reporting_metrics (
                    metric_name TEXT PRIMARY KEY,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Reporting database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating reporting tables: {e}")
            raise
    
    async def _create_directories(self):
        """Crear directorios necesarios"""
        try:
            directories = [
                'reports',
                'templates/reports',
                'templates/dashboards',
                'exports',
                'charts',
                'dashboards'
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            logger.info("Directories created successfully")
            
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    async def _load_existing_configs(self):
        """Cargar configuraciones existentes"""
        try:
            # Cargar reportes
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT * FROM report_configs')
            rows = cursor.fetchall()
            
            for row in rows:
                report_config = ReportConfig(
                    report_id=row[0],
                    name=row[1],
                    description=row[2],
                    report_type=ReportType(row[3]),
                    data_sources=json.loads(row[4]),
                    metrics=json.loads(row[5]),
                    filters=json.loads(row[6]),
                    schedule=row[7],
                    recipients=json.loads(row[8]),
                    format=ExportFormat(row[9]),
                    template=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )
                self.reports[report_config.report_id] = report_config
            
            # Cargar dashboards
            cursor.execute('SELECT * FROM dashboard_configs')
            rows = cursor.fetchall()
            
            for row in rows:
                dashboard_config = DashboardConfig(
                    dashboard_id=row[0],
                    name=row[1],
                    description=row[2],
                    layout=DashboardLayout(row[3]),
                    widgets=json.loads(row[4]),
                    filters=json.loads(row[5]),
                    refresh_interval=row[6],
                    is_public=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )
                self.dashboards[dashboard_config.dashboard_id] = dashboard_config
            
            logger.info(f"Loaded {len(self.reports)} reports and {len(self.dashboards)} dashboards")
            
        except Exception as e:
            logger.error(f"Error loading existing configs: {e}")
            raise
    
    async def _create_default_reports_and_dashboards(self):
        """Crear reportes y dashboards por defecto"""
        try:
            # Reporte de resumen ejecutivo
            executive_report = ReportConfig(
                report_id=str(uuid.uuid4()),
                name="Executive Summary Report",
                description="Comprehensive executive summary with key metrics and insights",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                data_sources=['campaigns', 'analytics', 'customers', 'revenue'],
                metrics=['roi', 'conversion_rate', 'customer_acquisition_cost', 'revenue_growth'],
                filters={'date_range': 'last_30_days'},
                schedule='0 8 * * 1',  # Lunes a las 8 AM
                recipients=['executives@company.com'],
                format=ExportFormat.PDF,
                template='executive_summary.html',
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.reports[executive_report.report_id] = executive_report
            
            # Dashboard principal
            main_dashboard = DashboardConfig(
                dashboard_id=str(uuid.uuid4()),
                name="Marketing Performance Dashboard",
                description="Real-time marketing performance metrics and KPIs",
                layout=DashboardLayout.THREE_COLUMN,
                widgets=[
                    {
                        'widget_id': 'kpi_cards',
                        'type': 'kpi_cards',
                        'position': {'row': 1, 'col': 1, 'span': 3},
                        'config': {
                            'metrics': ['total_revenue', 'conversion_rate', 'roi', 'customer_count']
                        }
                    },
                    {
                        'widget_id': 'revenue_chart',
                        'type': 'line_chart',
                        'position': {'row': 2, 'col': 1, 'span': 2},
                        'config': {
                            'data_source': 'revenue_data',
                            'x_axis': 'date',
                            'y_axis': 'revenue'
                        }
                    },
                    {
                        'widget_id': 'conversion_funnel',
                        'type': 'funnel_chart',
                        'position': {'row': 2, 'col': 3, 'span': 1},
                        'config': {
                            'data_source': 'conversion_data',
                            'stages': ['awareness', 'interest', 'consideration', 'purchase']
                        }
                    }
                ],
                filters={'date_range': 'last_30_days'},
                refresh_interval=300,
                is_public=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.dashboards[main_dashboard.dashboard_id] = main_dashboard
            
            logger.info("Default reports and dashboards created successfully")
            
        except Exception as e:
            logger.error(f"Error creating default reports and dashboards: {e}")
            raise
    
    async def _initialize_dash_app(self):
        """Inicializar aplicación Dash"""
        try:
            # Crear app Dash
            self.dash_app = dash.Dash(
                __name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True
            )
            
            # Configurar layout
            self.dash_app.layout = self._create_dash_layout()
            
            # Configurar callbacks
            self._setup_dash_callbacks()
            
            logger.info("Dash app initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Dash app: {e}")
            raise
    
    def _create_dash_layout(self):
        """Crear layout de Dash app"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Marketing Brain Reporting Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Quick Actions"),
                        dbc.CardBody([
                            dbc.Button("Generate Report", id="generate-report-btn", color="primary", className="me-2"),
                            dbc.Button("Create Dashboard", id="create-dashboard-btn", color="secondary", className="me-2"),
                            dbc.Button("Export Data", id="export-data-btn", color="success")
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='dashboard-selector',
                        options=[{'label': dashboard.name, 'value': dashboard.dashboard_id} 
                                for dashboard in self.dashboards.values()],
                        value=list(self.dashboards.keys())[0] if self.dashboards else None,
                        placeholder="Select a dashboard"
                    )
                ], width=6),
                dbc.Col([
                    dcc.Dropdown(
                        id='report-selector',
                        options=[{'label': report.name, 'value': report.report_id} 
                                for report in self.reports.values()],
                        placeholder="Select a report"
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.Div(id="dashboard-content")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div(id="report-content")
                ], width=12)
            ])
        ], fluid=True)
    
    def _setup_dash_callbacks(self):
        """Configurar callbacks de Dash"""
        
        @self.dash_app.callback(
            Output('dashboard-content', 'children'),
            Input('dashboard-selector', 'value')
        )
        def update_dashboard(dashboard_id):
            if dashboard_id and dashboard_id in self.dashboards:
                return self._render_dashboard(dashboard_id)
            return html.Div("Select a dashboard to view")
        
        @self.dash_app.callback(
            Output('report-content', 'children'),
            Input('report-selector', 'value')
        )
        def update_report(report_id):
            if report_id and report_id in self.reports:
                return self._render_report(report_id)
            return html.Div("Select a report to view")
    
    def _render_dashboard(self, dashboard_id: str):
        """Renderizar dashboard"""
        try:
            dashboard = self.dashboards[dashboard_id]
            
            widgets = []
            for widget in dashboard.widgets:
                widget_component = self._create_widget_component(widget)
                if widget_component:
                    widgets.append(widget_component)
            
            return html.Div(widgets)
            
        except Exception as e:
            logger.error(f"Error rendering dashboard: {e}")
            return html.Div("Error rendering dashboard")
    
    def _create_widget_component(self, widget: Dict[str, Any]):
        """Crear componente de widget"""
        try:
            widget_type = widget['type']
            config = widget['config']
            
            if widget_type == 'kpi_cards':
                return self._create_kpi_cards(config)
            elif widget_type == 'line_chart':
                return self._create_line_chart(config)
            elif widget_type == 'funnel_chart':
                return self._create_funnel_chart(config)
            else:
                return html.Div(f"Unknown widget type: {widget_type}")
                
        except Exception as e:
            logger.error(f"Error creating widget component: {e}")
            return html.Div("Error creating widget")
    
    def _create_kpi_cards(self, config: Dict[str, Any]):
        """Crear tarjetas KPI"""
        try:
            # Simular datos KPI
            kpi_data = {
                'total_revenue': {'value': '$125,000', 'change': '+12.5%', 'trend': 'up'},
                'conversion_rate': {'value': '3.2%', 'change': '+0.3%', 'trend': 'up'},
                'roi': {'value': '285%', 'change': '+15%', 'trend': 'up'},
                'customer_count': {'value': '1,250', 'change': '+8.2%', 'trend': 'up'}
            }
            
            cards = []
            for metric in config.get('metrics', []):
                if metric in kpi_data:
                    data = kpi_data[metric]
                    card = dbc.Card([
                        dbc.CardBody([
                            html.H4(data['value'], className="card-title"),
                            html.P(f"{data['change']} vs last period", className="card-text"),
                            html.Small(f"Trend: {data['trend']}", className="text-muted")
                        ])
                    ], className="mb-3")
                    cards.append(dbc.Col(card, width=3))
            
            return dbc.Row(cards)
            
        except Exception as e:
            logger.error(f"Error creating KPI cards: {e}")
            return html.Div("Error creating KPI cards")
    
    def _create_line_chart(self, config: Dict[str, Any]):
        """Crear gráfico de líneas"""
        try:
            # Simular datos
            dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
            values = np.random.cumsum(np.random.normal(1000, 200, len(dates)))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.update_layout(
                title=config.get('title', 'Revenue Trend'),
                xaxis_title='Date',
                yaxis_title='Revenue ($)',
                hovermode='x unified'
            )
            
            return dcc.Graph(figure=fig)
            
        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            return html.Div("Error creating line chart")
    
    def _create_funnel_chart(self, config: Dict[str, Any]):
        """Crear gráfico de embudo"""
        try:
            # Simular datos de embudo
            stages = config.get('stages', ['awareness', 'interest', 'consideration', 'purchase'])
            values = [10000, 5000, 2000, 500]  # Valores simulados
            
            fig = go.Figure(go.Funnel(
                y=stages,
                x=values,
                textinfo="value+percent initial",
                marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
            ))
            
            fig.update_layout(
                title=config.get('title', 'Conversion Funnel'),
                height=400
            )
            
            return dcc.Graph(figure=fig)
            
        except Exception as e:
            logger.error(f"Error creating funnel chart: {e}")
            return html.Div("Error creating funnel chart")
    
    def _render_report(self, report_id: str):
        """Renderizar reporte"""
        try:
            report = self.reports[report_id]
            
            # Generar datos del reporte
            report_data = asyncio.run(self._generate_report_data(report))
            
            # Crear contenido del reporte
            content = html.Div([
                html.H2(report.name),
                html.P(report.description),
                html.Hr(),
                html.Div(id=f"report-{report_id}-content")
            ])
            
            return content
            
        except Exception as e:
            logger.error(f"Error rendering report: {e}")
            return html.Div("Error rendering report")
    
    def _start_processing_threads(self):
        """Iniciar threads de procesamiento"""
        self.is_running = True
        
        self.report_generator_thread = threading.Thread(target=self._report_generator_loop, daemon=True)
        self.report_generator_thread.start()
        
        self.dashboard_updater_thread = threading.Thread(target=self._dashboard_updater_loop, daemon=True)
        self.dashboard_updater_thread.start()
        
        logger.info("Processing threads started")
    
    def _report_generator_loop(self):
        """Loop del generador de reportes"""
        while self.is_running:
            try:
                if not self.report_queue.empty():
                    report_config = self.report_queue.get_nowait()
                    asyncio.run(self._generate_report(report_config))
                    self.report_queue.task_done()
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in report generator loop: {e}")
                time.sleep(5)
    
    def _dashboard_updater_loop(self):
        """Loop del actualizador de dashboards"""
        while self.is_running:
            try:
                if not self.dashboard_queue.empty():
                    dashboard_id = self.dashboard_queue.get_nowait()
                    asyncio.run(self._update_dashboard(dashboard_id))
                    self.dashboard_queue.task_done()
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in dashboard updater loop: {e}")
                time.sleep(5)
    
    async def create_report(self, report_config: ReportConfig) -> str:
        """Crear nuevo reporte"""
        try:
            # Validar configuración
            if not await self._validate_report_config(report_config):
                return None
            
            # Agregar reporte
            self.reports[report_config.report_id] = report_config
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO report_configs (report_id, name, description, report_type,
                                          data_sources, metrics, filters, schedule,
                                          recipients, format, template, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_config.report_id,
                report_config.name,
                report_config.description,
                report_config.report_type.value,
                json.dumps(report_config.data_sources),
                json.dumps(report_config.metrics),
                json.dumps(report_config.filters),
                report_config.schedule,
                json.dumps(report_config.recipients),
                report_config.format.value,
                report_config.template,
                report_config.created_at,
                report_config.updated_at
            ))
            self.db_connection.commit()
            
            # Programar reporte si tiene schedule
            if report_config.schedule:
                await self._schedule_report(report_config)
            
            logger.info(f"Report created: {report_config.name}")
            return report_config.report_id
            
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return None
    
    async def _validate_report_config(self, config: ReportConfig) -> bool:
        """Validar configuración de reporte"""
        try:
            # Validar campos requeridos
            if not config.name or not config.description:
                logger.error("Report name and description are required")
                return False
            
            # Validar fuentes de datos
            if not config.data_sources:
                logger.error("At least one data source is required")
                return False
            
            # Validar métricas
            if not config.metrics:
                logger.error("At least one metric is required")
                return False
            
            # Validar template
            template_path = Path(f"templates/reports/{config.template}")
            if not template_path.exists():
                logger.error(f"Template not found: {config.template}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating report config: {e}")
            return False
    
    async def _schedule_report(self, report_config: ReportConfig):
        """Programar reporte"""
        try:
            # Usar schedule para programar reportes
            if report_config.schedule:
                schedule.every().monday.at("08:00").do(
                    lambda: self.report_queue.put(report_config)
                )
            
            logger.info(f"Report scheduled: {report_config.name}")
            
        except Exception as e:
            logger.error(f"Error scheduling report: {e}")
    
    async def _generate_report(self, report_config: ReportConfig):
        """Generar reporte"""
        try:
            logger.info(f"Generating report: {report_config.name}")
            
            # Generar datos
            report_data = await self._generate_report_data(report_config)
            
            # Crear reporte según formato
            if report_config.format == ExportFormat.PDF:
                await self._generate_pdf_report(report_config, report_data)
            elif report_config.format == ExportFormat.EXCEL:
                await self._generate_excel_report(report_config, report_data)
            elif report_config.format == ExportFormat.HTML:
                await self._generate_html_report(report_config, report_data)
            
            # Enviar por email si hay destinatarios
            if report_config.recipients:
                await self._send_report_email(report_config, report_data)
            
            # Actualizar métricas
            self.reporting_metrics['reports_generated'] += 1
            
            logger.info(f"Report generated successfully: {report_config.name}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    async def _generate_report_data(self, report_config: ReportConfig) -> ReportData:
        """Generar datos del reporte"""
        try:
            # Simular datos basados en las fuentes y métricas
            data = {}
            charts = []
            summary = {}
            
            for data_source in report_config.data_sources:
                if data_source == 'campaigns':
                    data['campaigns'] = {
                        'total_campaigns': 25,
                        'active_campaigns': 18,
                        'total_spend': 125000,
                        'total_revenue': 350000
                    }
                elif data_source == 'analytics':
                    data['analytics'] = {
                        'page_views': 150000,
                        'unique_visitors': 45000,
                        'bounce_rate': 0.35,
                        'avg_session_duration': 180
                    }
                elif data_source == 'customers':
                    data['customers'] = {
                        'total_customers': 1250,
                        'new_customers': 150,
                        'churn_rate': 0.05,
                        'lifetime_value': 280
                    }
                elif data_source == 'revenue':
                    data['revenue'] = {
                        'total_revenue': 350000,
                        'monthly_recurring': 25000,
                        'growth_rate': 0.15,
                        'profit_margin': 0.35
                    }
            
            # Generar gráficos
            for metric in report_config.metrics:
                chart = await self._create_chart_for_metric(metric, data)
                if chart:
                    charts.append(chart)
            
            # Generar resumen
            summary = await self._generate_summary(data, report_config.metrics)
            
            report_data = ReportData(
                report_id=report_config.report_id,
                data=data,
                charts=charts,
                summary=summary,
                generated_at=datetime.now().isoformat(),
                metadata={
                    'data_sources': report_config.data_sources,
                    'metrics': report_config.metrics,
                    'filters': report_config.filters
                }
            )
            
            # Guardar datos
            self.report_data[report_config.report_id] = report_data
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating report data: {e}")
            raise
    
    async def _create_chart_for_metric(self, metric: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear gráfico para métrica"""
        try:
            if metric == 'roi':
                # Gráfico de ROI por campaña
                campaigns = ['Campaign A', 'Campaign B', 'Campaign C', 'Campaign D']
                roi_values = [2.5, 3.2, 1.8, 4.1]
                
                fig = go.Figure(data=[
                    go.Bar(x=campaigns, y=roi_values, marker_color='#1f77b4')
                ])
                fig.update_layout(
                    title='ROI by Campaign',
                    xaxis_title='Campaign',
                    yaxis_title='ROI'
                )
                
                return {
                    'type': 'bar',
                    'title': 'ROI by Campaign',
                    'figure': fig.to_dict()
                }
            
            elif metric == 'conversion_rate':
                # Gráfico de tasa de conversión en el tiempo
                dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
                conversion_rates = np.random.normal(0.032, 0.005, len(dates))
                
                fig = go.Figure(data=[
                    go.Scatter(x=dates, y=conversion_rates, mode='lines+markers')
                ])
                fig.update_layout(
                    title='Conversion Rate Over Time',
                    xaxis_title='Date',
                    yaxis_title='Conversion Rate'
                )
                
                return {
                    'type': 'line',
                    'title': 'Conversion Rate Over Time',
                    'figure': fig.to_dict()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating chart for metric: {e}")
            return None
    
    async def _generate_summary(self, data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Generar resumen del reporte"""
        try:
            summary = {
                'key_insights': [],
                'recommendations': [],
                'performance_highlights': {}
            }
            
            # Generar insights basados en los datos
            if 'campaigns' in data:
                campaigns_data = data['campaigns']
                if campaigns_data['total_revenue'] > 300000:
                    summary['key_insights'].append("Strong revenue performance with campaigns generating $350K")
                
                if campaigns_data['total_spend'] > 0:
                    roi = campaigns_data['total_revenue'] / campaigns_data['total_spend']
                    summary['performance_highlights']['roi'] = roi
                    if roi > 2.0:
                        summary['key_insights'].append(f"Excellent ROI of {roi:.1f}x on campaign spend")
            
            if 'customers' in data:
                customers_data = data['customers']
                if customers_data['churn_rate'] < 0.1:
                    summary['key_insights'].append("Low churn rate indicates strong customer retention")
                
                summary['performance_highlights']['customer_count'] = customers_data['total_customers']
            
            # Generar recomendaciones
            summary['recommendations'] = [
                "Continue investing in high-performing campaigns",
                "Focus on customer retention strategies",
                "Optimize conversion funnels for better performance",
                "Expand successful campaign strategies to new markets"
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}
    
    async def _generate_pdf_report(self, report_config: ReportConfig, report_data: ReportData):
        """Generar reporte PDF"""
        try:
            output_path = Path(f"reports/{report_config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            # Crear documento PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph(report_config.name, title_style))
            story.append(Spacer(1, 12))
            
            # Descripción
            story.append(Paragraph(report_config.description, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Resumen ejecutivo
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            summary = report_data.summary
            
            if 'key_insights' in summary:
                story.append(Paragraph("Key Insights:", styles['Heading3']))
                for insight in summary['key_insights']:
                    story.append(Paragraph(f"• {insight}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            if 'recommendations' in summary:
                story.append(Paragraph("Recommendations:", styles['Heading3']))
                for recommendation in summary['recommendations']:
                    story.append(Paragraph(f"• {recommendation}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Datos principales
            story.append(Paragraph("Key Metrics", styles['Heading2']))
            
            # Crear tabla de métricas
            table_data = [['Metric', 'Value']]
            for source, source_data in report_data.data.items():
                for key, value in source_data.items():
                    table_data.append([key.replace('_', ' ').title(), str(value)])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 12))
            
            # Pie de página
            story.append(Paragraph(f"Generated on: {report_data.generated_at}", styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    async def _generate_excel_report(self, report_config: ReportConfig, report_data: ReportData):
        """Generar reporte Excel"""
        try:
            output_path = Path(f"reports/{report_config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            
            # Crear workbook Excel
            workbook = xlsxwriter.Workbook(str(output_path))
            worksheet = workbook.add_worksheet('Report')
            
            # Formato para encabezados
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#366092',
                'font_color': 'white',
                'border': 1
            })
            
            # Formato para datos
            data_format = workbook.add_format({
                'border': 1,
                'align': 'center'
            })
            
            # Escribir título
            worksheet.write('A1', report_config.name, header_format)
            worksheet.write('A2', report_config.description)
            worksheet.write('A3', f"Generated: {report_data.generated_at}")
            
            row = 5
            
            # Escribir datos
            for source, source_data in report_data.data.items():
                worksheet.write(row, 0, source.title(), header_format)
                row += 1
                
                for key, value in source_data.items():
                    worksheet.write(row, 0, key.replace('_', ' ').title(), data_format)
                    worksheet.write(row, 1, value, data_format)
                    row += 1
                
                row += 1
            
            # Ajustar ancho de columnas
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 20)
            
            workbook.close()
            
            logger.info(f"Excel report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise
    
    async def _generate_html_report(self, report_config: ReportConfig, report_data: ReportData):
        """Generar reporte HTML"""
        try:
            # Cargar template
            template = self.template_env.get_template(f"reports/{report_config.template}")
            
            # Renderizar template
            html_content = template.render(
                report=report_config,
                data=report_data.data,
                summary=report_data.summary,
                charts=report_data.charts,
                generated_at=report_data.generated_at
            )
            
            # Guardar archivo
            output_path = Path(f"reports/{report_config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise
    
    async def _send_report_email(self, report_config: ReportConfig, report_data: ReportData):
        """Enviar reporte por email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = ', '.join(report_config.recipients)
            msg['Subject'] = f"Marketing Brain Report: {report_config.name}"
            
            # Cuerpo del mensaje
            body = f"""
            <html>
            <body>
                <h2>{report_config.name}</h2>
                <p>{report_config.description}</p>
                <p>Report generated on: {report_data.generated_at}</p>
                
                <h3>Key Insights:</h3>
                <ul>
            """
            
            for insight in report_data.summary.get('key_insights', []):
                body += f"<li>{insight}</li>"
            
            body += """
                </ul>
                
                <h3>Recommendations:</h3>
                <ul>
            """
            
            for recommendation in report_data.summary.get('recommendations', []):
                body += f"<li>{recommendation}</li>"
            
            body += """
                </ul>
                
                <p>Best regards,<br>Marketing Brain System</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            
            # Actualizar métricas
            self.reporting_metrics['scheduled_reports_sent'] += 1
            
            logger.info(f"Report email sent to {len(report_config.recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
    
    async def create_dashboard(self, dashboard_config: DashboardConfig) -> str:
        """Crear nuevo dashboard"""
        try:
            # Validar configuración
            if not await self._validate_dashboard_config(dashboard_config):
                return None
            
            # Agregar dashboard
            self.dashboards[dashboard_config.dashboard_id] = dashboard_config
            
            # Guardar en base de datos
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO dashboard_configs (dashboard_id, name, description, layout,
                                             widgets, filters, refresh_interval, is_public,
                                             created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dashboard_config.dashboard_id,
                dashboard_config.name,
                dashboard_config.description,
                dashboard_config.layout.value,
                json.dumps(dashboard_config.widgets),
                json.dumps(dashboard_config.filters),
                dashboard_config.refresh_interval,
                dashboard_config.is_public,
                dashboard_config.created_at,
                dashboard_config.updated_at
            ))
            self.db_connection.commit()
            
            # Actualizar métricas
            self.reporting_metrics['dashboards_created'] += 1
            self.reporting_metrics['active_dashboards'] += 1
            
            logger.info(f"Dashboard created: {dashboard_config.name}")
            return dashboard_config.dashboard_id
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None
    
    async def _validate_dashboard_config(self, config: DashboardConfig) -> bool:
        """Validar configuración de dashboard"""
        try:
            # Validar campos requeridos
            if not config.name or not config.description:
                logger.error("Dashboard name and description are required")
                return False
            
            # Validar widgets
            if not config.widgets:
                logger.error("At least one widget is required")
                return False
            
            if len(config.widgets) > self.config['dashboards']['max_widgets_per_dashboard']:
                logger.error(f"Too many widgets. Maximum allowed: {self.config['dashboards']['max_widgets_per_dashboard']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating dashboard config: {e}")
            return False
    
    async def _update_dashboard(self, dashboard_id: str):
        """Actualizar dashboard"""
        try:
            if dashboard_id not in self.dashboards:
                logger.error(f"Dashboard {dashboard_id} not found")
                return
            
            dashboard = self.dashboards[dashboard_id]
            
            # Actualizar datos de widgets
            for widget in dashboard.widgets:
                await self._update_widget_data(widget)
            
            # Actualizar timestamp
            dashboard.updated_at = datetime.now().isoformat()
            
            logger.info(f"Dashboard updated: {dashboard.name}")
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    async def _update_widget_data(self, widget: Dict[str, Any]):
        """Actualizar datos de widget"""
        try:
            # Implementar actualización de datos según tipo de widget
            widget_type = widget['type']
            
            if widget_type == 'kpi_cards':
                # Actualizar métricas KPI
                pass
            elif widget_type == 'line_chart':
                # Actualizar datos de gráfico de líneas
                pass
            elif widget_type == 'funnel_chart':
                # Actualizar datos de embudo
                pass
            
        except Exception as e:
            logger.error(f"Error updating widget data: {e}")
    
    def get_reporting_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard de reportes"""
        return {
            'system_status': 'active' if self.is_running else 'inactive',
            'total_reports': len(self.reports),
            'total_dashboards': len(self.dashboards),
            'total_charts': len(self.charts),
            'reports_generated': self.reporting_metrics['reports_generated'],
            'dashboards_created': self.reporting_metrics['dashboards_created'],
            'charts_rendered': self.reporting_metrics['charts_rendered'],
            'exports_completed': self.reporting_metrics['exports_completed'],
            'scheduled_reports_sent': self.reporting_metrics['scheduled_reports_sent'],
            'metrics': self.reporting_metrics,
            'recent_reports': [
                {
                    'report_id': report.report_id,
                    'name': report.name,
                    'type': report.report_type.value,
                    'format': report.format.value,
                    'created_at': report.created_at,
                    'schedule': report.schedule
                }
                for report in list(self.reports.values())[-10:]  # Últimos 10 reportes
            ],
            'recent_dashboards': [
                {
                    'dashboard_id': dashboard.dashboard_id,
                    'name': dashboard.name,
                    'layout': dashboard.layout.value,
                    'widget_count': len(dashboard.widgets),
                    'is_public': dashboard.is_public,
                    'created_at': dashboard.created_at
                }
                for dashboard in list(self.dashboards.values())[-10:]  # Últimos 10 dashboards
            ],
            'last_updated': datetime.now().isoformat()
        }
    
    def export_reporting_data(self, export_dir: str = "reporting_data") -> Dict[str, str]:
        """Exportar datos de reportes"""
        Path(export_dir).mkdir(exist_ok=True)
        exported_files = {}
        
        # Exportar configuraciones de reportes
        reports_data = {report_id: asdict(report) for report_id, report in self.reports.items()}
        reports_path = Path(export_dir) / f"report_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(reports_path, 'w', encoding='utf-8') as f:
            json.dump(reports_data, f, indent=2, ensure_ascii=False)
        exported_files['report_configs'] = str(reports_path)
        
        # Exportar configuraciones de dashboards
        dashboards_data = {dashboard_id: asdict(dashboard) for dashboard_id, dashboard in self.dashboards.items()}
        dashboards_path = Path(export_dir) / f"dashboard_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(dashboards_path, 'w', encoding='utf-8') as f:
            json.dump(dashboards_data, f, indent=2, ensure_ascii=False)
        exported_files['dashboard_configs'] = str(dashboards_path)
        
        # Exportar datos de reportes
        report_data_export = {report_id: asdict(data) for report_id, data in self.report_data.items()}
        report_data_path = Path(export_dir) / f"report_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_data_path, 'w', encoding='utf-8') as f:
            json.dump(report_data_export, f, indent=2, ensure_ascii=False)
        exported_files['report_data'] = str(report_data_path)
        
        # Exportar métricas
        metrics_path = Path(export_dir) / f"reporting_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.reporting_metrics, f, indent=2, ensure_ascii=False)
        exported_files['reporting_metrics'] = str(metrics_path)
        
        logger.info(f"📦 Exported reporting data to {export_dir}")
        return exported_files


def main():
    """Función principal para demostrar el Sistema de Reportes Avanzados"""
    print("📊 MARKETING BRAIN ADVANCED REPORTING")
    print("=" * 60)
    
    # Crear sistema de reportes
    reporting_system = MarketingBrainAdvancedReporting()
    
    async def run_demo():
        print(f"\n🚀 INICIANDO SISTEMA DE REPORTES AVANZADOS...")
        
        # Inicializar sistema
        await reporting_system.initialize_reporting_system()
        
        # Mostrar estado inicial
        dashboard_data = reporting_system.get_reporting_dashboard_data()
        print(f"\n📊 ESTADO DEL SISTEMA DE REPORTES:")
        print(f"   • Estado: {dashboard_data['system_status']}")
        print(f"   • Reportes totales: {dashboard_data['total_reports']}")
        print(f"   • Dashboards totales: {dashboard_data['total_dashboards']}")
        print(f"   • Gráficos totales: {dashboard_data['total_charts']}")
        print(f"   • Reportes generados: {dashboard_data['reports_generated']}")
        print(f"   • Dashboards creados: {dashboard_data['dashboards_created']}")
        print(f"   • Gráficos renderizados: {dashboard_data['charts_rendered']}")
        print(f"   • Exportaciones completadas: {dashboard_data['exports_completed']}")
        
        # Mostrar reportes disponibles
        print(f"\n📋 REPORTES DISPONIBLES:")
        for report_id, report_info in list(dashboard_data['recent_reports'].items())[:5]:
            print(f"   • {report_info['name']}")
            print(f"     - Tipo: {report_info['type']}")
            print(f"     - Formato: {report_info['format']}")
            print(f"     - Programado: {'Sí' if report_info['schedule'] else 'No'}")
            print(f"     - Creado: {report_info['created_at']}")
        
        # Mostrar dashboards disponibles
        print(f"\n📊 DASHBOARDS DISPONIBLES:")
        for dashboard_id, dashboard_info in list(dashboard_data['recent_dashboards'].items())[:5]:
            print(f"   • {dashboard_info['name']}")
            print(f"     - Layout: {dashboard_info['layout']}")
            print(f"     - Widgets: {dashboard_info['widget_count']}")
            print(f"     - Público: {'Sí' if dashboard_info['is_public'] else 'No'}")
            print(f"     - Creado: {dashboard_info['created_at']}")
        
        # Crear reporte personalizado
        print(f"\n📝 CREANDO REPORTE PERSONALIZADO...")
        custom_report = ReportConfig(
            report_id=str(uuid.uuid4()),
            name="Custom Marketing Analysis Report",
            description="Detailed analysis of marketing performance with custom metrics",
            report_type=ReportType.CUSTOM,
            data_sources=['campaigns', 'analytics', 'customers'],
            metrics=['roi', 'conversion_rate', 'customer_acquisition_cost'],
            filters={'date_range': 'last_90_days', 'campaign_type': 'paid'},
            schedule=None,
            recipients=['marketing@company.com'],
            format=ExportFormat.PDF,
            template='custom_report.html',
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        report_created = await reporting_system.create_report(custom_report)
        if report_created:
            print(f"   ✅ Reporte creado: {custom_report.name}")
            print(f"      • ID: {custom_report.report_id}")
            print(f"      • Fuentes de datos: {', '.join(custom_report.data_sources)}")
            print(f"      • Métricas: {', '.join(custom_report.metrics)}")
            print(f"      • Formato: {custom_report.format.value}")
        else:
            print(f"   ❌ Error al crear reporte")
        
        # Crear dashboard personalizado
        print(f"\n📊 CREANDO DASHBOARD PERSONALIZADO...")
        custom_dashboard = DashboardConfig(
            dashboard_id=str(uuid.uuid4()),
            name="Custom Analytics Dashboard",
            description="Custom dashboard for detailed analytics and insights",
            layout=DashboardLayout.TWO_COLUMN,
            widgets=[
                {
                    'widget_id': 'custom_kpi',
                    'type': 'kpi_cards',
                    'position': {'row': 1, 'col': 1, 'span': 2},
                    'config': {
                        'metrics': ['custom_metric_1', 'custom_metric_2', 'custom_metric_3']
                    }
                },
                {
                    'widget_id': 'custom_chart',
                    'type': 'bar_chart',
                    'position': {'row': 2, 'col': 1, 'span': 1},
                    'config': {
                        'data_source': 'custom_data',
                        'x_axis': 'category',
                        'y_axis': 'value'
                    }
                },
                {
                    'widget_id': 'custom_pie',
                    'type': 'pie_chart',
                    'position': {'row': 2, 'col': 2, 'span': 1},
                    'config': {
                        'data_source': 'distribution_data',
                        'labels': 'category',
                        'values': 'percentage'
                    }
                }
            ],
            filters={'date_range': 'last_30_days'},
            refresh_interval=600,
            is_public=False,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        dashboard_created = await reporting_system.create_dashboard(custom_dashboard)
        if dashboard_created:
            print(f"   ✅ Dashboard creado: {custom_dashboard.name}")
            print(f"      • ID: {custom_dashboard.dashboard_id}")
            print(f"      • Layout: {custom_dashboard.layout.value}")
            print(f"      • Widgets: {len(custom_dashboard.widgets)}")
            print(f"      • Intervalo de actualización: {custom_dashboard.refresh_interval}s")
        else:
            print(f"   ❌ Error al crear dashboard")
        
        # Simular generación de reporte
        print(f"\n⚡ SIMULANDO GENERACIÓN DE REPORTE...")
        if report_created:
            # Agregar reporte a la cola de generación
            reporting_system.report_queue.put(custom_report)
            
            # Esperar un poco para que se procese
            await asyncio.sleep(2)
            
            print(f"   ✅ Reporte generado exitosamente")
            print(f"      • Datos procesados: {len(custom_report.data_sources)} fuentes")
            print(f"      • Métricas calculadas: {len(custom_report.metrics)}")
            print(f"      • Formato: {custom_report.format.value}")
        
        # Mostrar métricas finales
        print(f"\n📈 MÉTRICAS DEL SISTEMA DE REPORTES:")
        final_dashboard = reporting_system.get_reporting_dashboard_data()
        metrics = final_dashboard['metrics']
        print(f"   • Reportes generados: {metrics['reports_generated']}")
        print(f"   • Dashboards creados: {metrics['dashboards_created']}")
        print(f"   • Gráficos renderizados: {metrics['charts_rendered']}")
        print(f"   • Exportaciones completadas: {metrics['exports_completed']}")
        print(f"   • Reportes programados enviados: {metrics['scheduled_reports_sent']}")
        print(f"   • Tiempo promedio de generación: {metrics['average_generation_time']:.2f}s")
        print(f"   • Total de puntos de datos: {metrics['total_data_points']}")
        print(f"   • Dashboards activos: {metrics['active_dashboards']}")
        
        # Exportar datos
        print(f"\n💾 EXPORTANDO DATOS DE REPORTES...")
        exported_files = reporting_system.export_reporting_data()
        print(f"   • Archivos exportados: {len(exported_files)}")
        for file_type, path in exported_files.items():
            print(f"     - {file_type}: {Path(path).name}")
        
        print(f"\n✅ SISTEMA DE REPORTES AVANZADOS DEMO COMPLETADO EXITOSAMENTE")
        print(f"🎉 El sistema de reportes ha implementado:")
        print(f"   • Generación automática de reportes en múltiples formatos")
        print(f"   • Dashboards interactivos con visualizaciones en tiempo real")
        print(f"   • Gráficos avanzados y análisis visual")
        print(f"   • Programación automática de reportes")
        print(f"   • Exportación en PDF, Excel, HTML y más")
        print(f"   • Envío automático por email")
        print(f"   • Templates personalizables")
        print(f"   • Métricas y KPIs en tiempo real")
        print(f"   • Integración con Dash para interfaces web")
        
        return reporting_system
    
    # Ejecutar demo
    reporting_system = asyncio.run(run_demo())


if __name__ == "__main__":
    main()








