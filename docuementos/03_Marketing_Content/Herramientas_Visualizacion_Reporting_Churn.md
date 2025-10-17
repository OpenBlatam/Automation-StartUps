# 📊 Herramientas de Visualización y Reporting para Churn

## 🎯 Variante 1: Dashboard Interactivo Avanzado

### **Dashboard con Plotly y Dash**
```python
# dashboard_interactivo_avanzado.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import numpy as np

class DashboardInteractivoAvanzado:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.datos = None
        self.metricas = {}
    
    def crear_dashboard_completo(self):
        """Crea dashboard completo con múltiples secciones"""
        self.app.layout = html.Div([
            # Header con navegación
            html.Div([
                html.H1("📊 Dashboard de Análisis de Churn - Versión Avanzada"),
                dcc.Tabs(id="main-tabs", value="overview", children=[
                    dcc.Tab(label="📈 Resumen General", value="overview"),
                    dcc.Tab(label="🔍 Análisis Detallado", value="detailed"),
                    dcc.Tab(label="🤖 Predicciones IA", value="predictions"),
                    dcc.Tab(label="🌍 Análisis Regional", value="regional"),
                    dcc.Tab(label="📋 Reportes", value="reports")
                ])
            ], className="header"),
            
            # Contenido de pestañas
            html.Div(id="tab-content"),
            
            # Footer con métricas en tiempo real
            html.Div([
                html.Div([
                    html.Span("🔄 Actualizado: "),
                    html.Span(id="last-update")
                ], className="footer-metrics")
            ], className="footer")
        ])
        
        # Configurar callbacks
        self._configurar_callbacks()
        
        return self.app
    
    def _configurar_callbacks(self):
        """Configura callbacks para interactividad"""
        @self.app.callback(
            Output("tab-content", "children"),
            Input("main-tabs", "value")
        )
        def render_tab_content(active_tab):
            if active_tab == "overview":
                return self._crear_pestana_resumen()
            elif active_tab == "detailed":
                return self._crear_pestana_detallado()
            elif active_tab == "predictions":
                return self._crear_pestana_predicciones()
            elif active_tab == "regional":
                return self._crear_pestana_regional()
            elif active_tab == "reports":
                return self._crear_pestana_reportes()
    
    def _crear_pestana_resumen(self):
        """Crea pestaña de resumen general"""
        return html.Div([
            # Métricas principales
            html.Div([
                html.Div([
                    html.H3("Tasa de Churn"),
                    html.H2(id="metric-churn", className="metric-value"),
                    html.P("vs mes anterior", className="metric-change")
                ], className="metric-card"),
                html.Div([
                    html.H3("LTV Promedio"),
                    html.H2(id="metric-ltv", className="metric-value"),
                    html.P("vs mes anterior", className="metric-change")
                ], className="metric-card"),
                html.Div([
                    html.H3("NPS Score"),
                    html.H2(id="metric-nps", className="metric-value"),
                    html.P("vs mes anterior", className="metric-change")
                ], className="metric-card"),
                html.Div([
                    html.H3("Clientes en Riesgo"),
                    html.H2(id="metric-risk", className="metric-value"),
                    html.P("vs mes anterior", className="metric-change")
                ], className="metric-card")
            ], className="metrics-row"),
            
            # Gráficos principales
            html.Div([
                html.Div([
                    dcc.Graph(id="churn-trend-chart")
                ], className="chart-container"),
                html.Div([
                    dcc.Graph(id="retention-cohort-chart")
                ], className="chart-container")
            ], className="charts-row"),
            
            # Alertas y notificaciones
            html.Div([
                html.H3("🚨 Alertas Activas"),
                html.Div(id="alerts-container")
            ], className="alerts-section")
        ])
    
    def _crear_pestana_detallado(self):
        """Crea pestaña de análisis detallado"""
        return html.Div([
            # Filtros avanzados
            html.Div([
                html.Div([
                    html.Label("Período de Análisis:"),
                    dcc.DatePickerRange(
                        id="date-range",
                        start_date="2024-01-01",
                        end_date="2024-12-31"
                    )
                ], className="filter-item"),
                html.Div([
                    html.Label("Segmento:"),
                    dcc.Dropdown(
                        id="segment-filter",
                        options=[
                            {"label": "Todos", "value": "all"},
                            {"label": "Champions", "value": "champions"},
                            {"label": "En Riesgo", "value": "at_risk"},
                            {"label": "Nuevos", "value": "new"}
                        ],
                        value="all"
                    )
                ], className="filter-item"),
                html.Div([
                    html.Label("Región:"),
                    dcc.Dropdown(
                        id="region-filter",
                        options=[
                            {"label": "Todas", "value": "all"},
                            {"label": "México", "value": "mexico"},
                            {"label": "Argentina", "value": "argentina"},
                            {"label": "Colombia", "value": "colombia"}
                        ],
                        value="all"
                    )
                ], className="filter-item")
            ], className="filters-row"),
            
            # Gráficos detallados
            html.Div([
                html.Div([
                    dcc.Graph(id="detailed-churn-analysis")
                ], className="chart-container-large"),
                html.Div([
                    dcc.Graph(id="customer-health-distribution")
                ], className="chart-container-large")
            ], className="charts-row")
        ])
    
    def _crear_pestana_predicciones(self):
        """Crea pestaña de predicciones con IA"""
        return html.Div([
            # Modelo de predicción
            html.Div([
                html.H3("🤖 Predicciones de Churn con IA"),
                html.Div([
                    html.Div([
                        html.Label("Seleccionar Modelo:"),
                        dcc.Dropdown(
                            id="model-selector",
                            options=[
                                {"label": "LSTM", "value": "lstm"},
                                {"label": "Random Forest", "value": "rf"},
                                {"label": "XGBoost", "value": "xgb"},
                                {"label": "Ensemble", "value": "ensemble"}
                            ],
                            value="ensemble"
                        )
                    ], className="model-selector"),
                    html.Div([
                        html.Button("🔄 Actualizar Predicciones", id="update-predictions", className="btn-primary")
                    ], className="update-button")
                ], className="model-controls")
            ], className="prediction-header"),
            
            # Gráficos de predicción
            html.Div([
                html.Div([
                    dcc.Graph(id="prediction-accuracy-chart")
                ], className="chart-container"),
                html.Div([
                    dcc.Graph(id="feature-importance-chart")
                ], className="chart-container")
            ], className="charts-row"),
            
            # Lista de clientes en riesgo
            html.Div([
                html.H3("⚠️ Clientes en Riesgo de Churn"),
                html.Div(id="at-risk-customers-table")
            ], className="risk-customers-section")
        ])
    
    def _crear_pestana_regional(self):
        """Crea pestaña de análisis regional"""
        return html.Div([
            # Mapa de calor regional
            html.Div([
                dcc.Graph(id="regional-heatmap")
            ], className="chart-container-large"),
            
            # Comparación por región
            html.Div([
                html.Div([
                    dcc.Graph(id="regional-comparison")
                ], className="chart-container"),
                html.Div([
                    dcc.Graph(id="cultural-adaptation-metrics")
                ], className="chart-container")
            ], className="charts-row")
        ])
    
    def _crear_pestana_reportes(self):
        """Crea pestaña de reportes"""
        return html.Div([
            # Generador de reportes
            html.Div([
                html.H3("📋 Generador de Reportes"),
                html.Div([
                    html.Div([
                        html.Label("Tipo de Reporte:"),
                        dcc.Dropdown(
                            id="report-type",
                            options=[
                                {"label": "Reporte Ejecutivo", "value": "executive"},
                                {"label": "Reporte Técnico", "value": "technical"},
                                {"label": "Reporte Regional", "value": "regional"},
                                {"label": "Reporte de Predicciones", "value": "predictions"}
                            ],
                            value="executive"
                        )
                    ], className="report-control"),
                    html.Div([
                        html.Label("Formato:"),
                        dcc.RadioItems(
                            id="report-format",
                            options=[
                                {"label": "PDF", "value": "pdf"},
                                {"label": "Excel", "value": "excel"},
                                {"label": "PowerPoint", "value": "pptx"}
                            ],
                            value="pdf"
                        )
                    ], className="report-control"),
                    html.Div([
                        html.Button("📊 Generar Reporte", id="generate-report", className="btn-primary")
                    ], className="generate-button")
                ], className="report-controls")
            ], className="report-generator"),
            
            # Historial de reportes
            html.Div([
                html.H3("📁 Historial de Reportes"),
                html.Div(id="reports-history")
            ], className="reports-history")
        ])
```

## 🎯 Variante 2: Visualizaciones Avanzadas

### **Gráficos Especializados**
```python
# visualizaciones_avanzadas.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np

class VisualizacionesAvanzadas:
    def __init__(self):
        self.colores = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#F18F01',
            'warning': '#C73E1D',
            'info': '#6A994E'
        }
    
    def crear_grafico_churn_trend(self, datos):
        """Crea gráfico de tendencia de churn con múltiples métricas"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Tasa de Churn Mensual', 'Retención por Cohortes', 
                          'LTV por Segmento', 'NPS Trend'),
            specs=[[{"secondary_y": True}, {"type": "heatmap"}],
                   [{"type": "bar"}, {"secondary_y": True}]]
        )
        
        # Gráfico 1: Tasa de churn mensual
        fig.add_trace(
            go.Scatter(
                x=datos['fecha'],
                y=datos['churn_rate'],
                mode='lines+markers',
                name='Churn Rate',
                line=dict(color=self.colores['primary'], width=3)
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Retención por cohortes
        cohort_data = datos['cohort_retention']
        fig.add_trace(
            go.Heatmap(
                z=cohort_data.values,
                x=cohort_data.columns,
                y=cohort_data.index,
                colorscale='RdYlBu_r',
                showscale=True
            ),
            row=1, col=2
        )
        
        # Gráfico 3: LTV por segmento
        segmentos = datos['ltv_by_segment']
        fig.add_trace(
            go.Bar(
                x=list(segmentos.keys()),
                y=list(segmentos.values()),
                marker_color=[self.colores['success'], self.colores['warning'], 
                            self.colores['info'], self.colores['primary']]
            ),
            row=2, col=1
        )
        
        # Gráfico 4: NPS Trend
        fig.add_trace(
            go.Scatter(
                x=datos['fecha'],
                y=datos['nps_score'],
                mode='lines+markers',
                name='NPS Score',
                line=dict(color=self.colores['secondary'], width=3)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Dashboard de Análisis de Churn - Vista Completa",
            showlegend=True,
            height=800,
            template="plotly_white"
        )
        
        return fig
    
    def crear_grafico_prediccion_churn(self, datos_reales, datos_prediccion):
        """Crea gráfico de predicción de churn con intervalos de confianza"""
        fig = go.Figure()
        
        # Datos reales
        fig.add_trace(go.Scatter(
            x=datos_reales['fecha'],
            y=datos_reales['churn_rate'],
            mode='lines+markers',
            name='Churn Real',
            line=dict(color=self.colores['primary'], width=3),
            marker=dict(size=8)
        ))
        
        # Predicción
        fig.add_trace(go.Scatter(
            x=datos_prediccion['fecha'],
            y=datos_prediccion['churn_rate_predicted'],
            mode='lines+markers',
            name='Churn Predicho',
            line=dict(color=self.colores['secondary'], width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        # Intervalo de confianza
        fig.add_trace(go.Scatter(
            x=datos_prediccion['fecha'],
            y=datos_prediccion['upper_bound'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=datos_prediccion['fecha'],
            y=datos_prediccion['lower_bound'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(46, 134, 171, 0.2)',
            name='Intervalo de Confianza',
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title="Predicción de Churn con Intervalos de Confianza",
            xaxis_title="Fecha",
            yaxis_title="Tasa de Churn (%)",
            hovermode='x unified',
            template="plotly_white"
        )
        
        return fig
    
    def crear_grafico_red_clientes(self, datos_red):
        """Crea gráfico de red de clientes"""
        # Crear nodos
        nodes = []
        for cliente in datos_red['clientes']:
            nodes.append({
                'id': cliente['id'],
                'label': cliente['nombre'],
                'size': cliente['influencia'] * 20,
                'color': self._obtener_color_por_tier(cliente['tier']),
                'group': cliente['tier']
            })
        
        # Crear aristas
        edges = []
        for conexion in datos_red['conexiones']:
            edges.append({
                'source': conexion['cliente1'],
                'target': conexion['cliente2'],
                'weight': conexion['peso'],
                'color': self._obtener_color_conexion(conexion['tipo'])
            })
        
        # Crear gráfico de red
        fig = go.Figure()
        
        # Agregar aristas
        for edge in edges:
            fig.add_trace(go.Scatter(
                x=[edge['source'], edge['target']],
                y=[0, 0],  # Simplificado para ejemplo
                mode='lines',
                line=dict(width=edge['weight'], color=edge['color']),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Agregar nodos
        for node in nodes:
            fig.add_trace(go.Scatter(
                x=[node['id']],
                y=[0],
                mode='markers+text',
                marker=dict(
                    size=node['size'],
                    color=node['color'],
                    line=dict(width=2, color='white')
                ),
                text=node['label'],
                textposition="middle center",
                name=node['group']
            ))
        
        fig.update_layout(
            title="Red de Clientes e Influencia",
            showlegend=True,
            template="plotly_white"
        )
        
        return fig
    
    def crear_grafico_sankey_churn(self, datos_flujo):
        """Crea gráfico Sankey para flujo de churn"""
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=datos_flujo['nodos'],
                color=datos_flujo['colores_nodos']
            ),
            link=dict(
                source=datos_flujo['fuentes'],
                target=datos_flujo['destinos'],
                value=datos_flujo['valores'],
                color=datos_flujo['colores_enlaces']
            )
        )])
        
        fig.update_layout(
            title="Flujo de Clientes - Análisis Sankey",
            font_size=10,
            template="plotly_white"
        )
        
        return fig
    
    def _obtener_color_por_tier(self, tier):
        """Obtiene color según tier del cliente"""
        colores_tier = {
            'Champion': self.colores['success'],
            'Loyal': self.colores['info'],
            'Engaged': self.colores['warning'],
            'Satisfied': self.colores['primary']
        }
        return colores_tier.get(tier, self.colores['primary'])
    
    def _obtener_color_conexion(self, tipo):
        """Obtiene color según tipo de conexión"""
        colores_conexion = {
            'referral': self.colores['success'],
            'colaboracion': self.colores['info'],
            'competencia': self.colores['warning']
        }
        return colores_conexion.get(tipo, self.colores['primary'])
```

## 🎯 Variante 3: Reportes Automatizados

### **Generador de Reportes**
```python
# generador_reportes.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
import io

class GeneradorReportes:
    def __init__(self):
        self.estilos = getSampleStyleSheet()
        self.datos = None
    
    def generar_reporte_ejecutivo(self, datos, formato='pdf'):
        """Genera reporte ejecutivo completo"""
        if formato == 'pdf':
            return self._generar_pdf_ejecutivo(datos)
        elif formato == 'excel':
            return self._generar_excel_ejecutivo(datos)
        elif formato == 'pptx':
            return self._generar_pptx_ejecutivo(datos)
    
    def _generar_pdf_ejecutivo(self, datos):
        """Genera reporte ejecutivo en PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Título
        titulo = Paragraph("Reporte Ejecutivo - Análisis de Churn", 
                          self.estilos['Title'])
        story.append(titulo)
        story.append(Spacer(1, 12))
        
        # Resumen ejecutivo
        resumen = Paragraph("Resumen Ejecutivo", self.estilos['Heading1'])
        story.append(resumen)
        
        resumen_texto = f"""
        Este reporte presenta un análisis completo de la retención de clientes 
        basado en datos del período {datos['periodo']}. Se identificaron 
        {datos['clientes_analizados']} clientes con una tasa de churn del 
        {datos['churn_rate']:.1f}% y un LTV promedio de ${datos['ltv_promedio']:,.2f}.
        """
        
        story.append(Paragraph(resumen_texto, self.estilos['Normal']))
        story.append(Spacer(1, 12))
        
        # Métricas principales
        metricas = Paragraph("Métricas Principales", self.estilos['Heading1'])
        story.append(metricas)
        
        # Crear tabla de métricas
        tabla_metricas = [
            ['Métrica', 'Valor Actual', 'Objetivo', 'Variación'],
            ['Tasa de Churn', f"{datos['churn_rate']:.1f}%", "5.0%", f"{datos['variacion_churn']:+.1f}%"],
            ['LTV Promedio', f"${datos['ltv_promedio']:,.2f}", "$15,000", f"{datos['variacion_ltv']:+.1f}%"],
            ['NPS Score', f"{datos['nps_score']:.0f}", "60", f"{datos['variacion_nps']:+.0f}"],
            ['Retención', f"{datos['retencion']:.1f}%", "95.0%", f"{datos['variacion_retencion']:+.1f}%"]
        ]
        
        tabla = Table(tabla_metricas, colWidths=[2, 1.5, 1.5, 1])
        tabla.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#2E86AB'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, 'black')
        ])
        
        story.append(tabla)
        story.append(Spacer(1, 12))
        
        # Recomendaciones
        recomendaciones = Paragraph("Recomendaciones Estratégicas", self.estilos['Heading1'])
        story.append(recomendaciones)
        
        for i, rec in enumerate(datos['recomendaciones'], 1):
            rec_texto = f"{i}. {rec['titulo']}: {rec['descripcion']}"
            story.append(Paragraph(rec_texto, self.estilos['Normal']))
            story.append(Spacer(1, 6))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _generar_excel_ejecutivo(self, datos):
        """Genera reporte ejecutivo en Excel"""
        with pd.ExcelWriter('reporte_ejecutivo.xlsx', engine='openpyxl') as writer:
            # Hoja 1: Resumen
            resumen_df = pd.DataFrame({
                'Métrica': ['Tasa de Churn', 'LTV Promedio', 'NPS Score', 'Retención'],
                'Valor Actual': [f"{datos['churn_rate']:.1f}%", f"${datos['ltv_promedio']:,.2f}", 
                               f"{datos['nps_score']:.0f}", f"{datos['retencion']:.1f}%"],
                'Objetivo': ['5.0%', '$15,000', '60', '95.0%'],
                'Variación': [f"{datos['variacion_churn']:+.1f}%", f"{datos['variacion_ltv']:+.1f}%",
                            f"{datos['variacion_nps']:+.0f}", f"{datos['variacion_retencion']:+.1f}%"]
            })
            resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja 2: Análisis detallado
            analisis_df = pd.DataFrame(datos['analisis_detallado'])
            analisis_df.to_excel(writer, sheet_name='Análisis Detallado', index=False)
            
            # Hoja 3: Recomendaciones
            recomendaciones_df = pd.DataFrame(datos['recomendaciones'])
            recomendaciones_df.to_excel(writer, sheet_name='Recomendaciones', index=False)
    
    def generar_reporte_tecnico(self, datos, formato='pdf'):
        """Genera reporte técnico detallado"""
        if formato == 'pdf':
            return self._generar_pdf_tecnico(datos)
        elif formato == 'excel':
            return self._generar_excel_tecnico(datos)
    
    def _generar_pdf_tecnico(self, datos):
        """Genera reporte técnico en PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Título
        titulo = Paragraph("Reporte Técnico - Análisis de Churn", 
                          self.estilos['Title'])
        story.append(titulo)
        story.append(Spacer(1, 12))
        
        # Metodología
        metodologia = Paragraph("Metodología", self.estilos['Heading1'])
        story.append(metodologia)
        
        metodologia_texto = """
        Este análisis utiliza técnicas avanzadas de machine learning incluyendo:
        - Modelos LSTM para predicción de series temporales
        - Random Forest para clasificación de churn
        - Análisis de sentimientos con NLP
        - Clustering para segmentación de clientes
        - Análisis de redes para identificar influencia
        """
        
        story.append(Paragraph(metodologia_texto, self.estilos['Normal']))
        story.append(Spacer(1, 12))
        
        # Resultados del modelo
        resultados = Paragraph("Resultados del Modelo", self.estilos['Heading1'])
        story.append(resultados)
        
        # Tabla de resultados
        tabla_resultados = [
            ['Modelo', 'Precisión', 'Recall', 'F1-Score', 'AUC'],
            ['LSTM', f"{datos['lstm_accuracy']:.3f}", f"{datos['lstm_recall']:.3f}", 
             f"{datos['lstm_f1']:.3f}", f"{datos['lstm_auc']:.3f}"],
            ['Random Forest', f"{datos['rf_accuracy']:.3f}", f"{datos['rf_recall']:.3f}", 
             f"{datos['rf_f1']:.3f}", f"{datos['rf_auc']:.3f}"],
            ['Ensemble', f"{datos['ensemble_accuracy']:.3f}", f"{datos['ensemble_recall']:.3f}", 
             f"{datos['ensemble_f1']:.3f}", f"{datos['ensemble_auc']:.3f}"]
        ]
        
        tabla = Table(tabla_resultados, colWidths=[1.5, 1, 1, 1, 1])
        tabla.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#2E86AB'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, 'black')
        ])
        
        story.append(tabla)
        story.append(Spacer(1, 12))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
```

## 🎯 Variante 4: Alertas y Notificaciones

### **Sistema de Alertas Inteligentes**
```python
# sistema_alertas_avanzado.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime, timedelta

class SistemaAlertasAvanzado:
    def __init__(self):
        self.reglas_alertas = self._configurar_reglas_alertas()
        self.canales_notificacion = self._configurar_canales()
        self.historial_alertas = []
    
    def _configurar_reglas_alertas(self):
        """Configura reglas de alertas avanzadas"""
        return {
            'churn_critico': {
                'condicion': 'churn_probability > 0.8',
                'prioridad': 'CRÍTICA',
                'accion': 'contacto_inmediato',
                'tiempo_respuesta': '1 hora',
                'escalacion': 'ejecutivo',
                'canales': ['email', 'sms', 'slack', 'phone']
            },
            'churn_alto': {
                'condicion': 'churn_probability > 0.6',
                'prioridad': 'ALTA',
                'accion': 'programa_retencion',
                'tiempo_respuesta': '24 horas',
                'escalacion': 'customer_success',
                'canales': ['email', 'slack']
            },
            'tendencia_negativa': {
                'condicion': 'churn_trend < -0.05',
                'prioridad': 'MEDIA',
                'accion': 'analisis_tendencia',
                'tiempo_respuesta': '48 horas',
                'escalacion': 'analista',
                'canales': ['email']
            },
            'nps_bajo': {
                'condicion': 'nps_score < 6',
                'prioridad': 'MEDIA',
                'accion': 'encuesta_satisfaccion',
                'tiempo_respuesta': '48 horas',
                'escalacion': 'marketing',
                'canales': ['email']
            }
        }
    
    def _configurar_canales(self):
        """Configura canales de notificación"""
        return {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'alerts@company.com',
                'password': 'password'
            },
            'slack': {
                'webhook_url': 'https://hooks.slack.com/services/...',
                'channel': '#churn-alerts'
            },
            'sms': {
                'api_key': 'twilio_api_key',
                'from_number': '+1234567890'
            }
        }
    
    def procesar_alertas_tiempo_real(self, datos_clientes):
        """Procesa alertas en tiempo real"""
        alertas_generadas = []
        
        for cliente in datos_clientes:
            for nombre_regla, regla in self.reglas_alertas.items():
                if self._evaluar_condicion(regla['condicion'], cliente):
                    alerta = self._crear_alerta(cliente, nombre_regla, regla)
                    alertas_generadas.append(alerta)
                    
                    # Enviar notificación inmediata
                    self._enviar_notificacion_inmediata(alerta)
        
        # Procesar alertas en lote
        self._procesar_alertas_lote(alertas_generadas)
        
        return alertas_generadas
    
    def _crear_alerta(self, cliente, nombre_regla, regla):
        """Crea alerta estructurada"""
        alerta = {
            'id': f"{cliente['customer_id']}_{nombre_regla}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'cliente_id': cliente['customer_id'],
            'cliente_nombre': cliente.get('company_name', 'N/A'),
            'regla': nombre_regla,
            'prioridad': regla['prioridad'],
            'accion': regla['accion'],
            'tiempo_respuesta': regla['tiempo_respuesta'],
            'escalacion': regla['escalacion'],
            'canales': regla['canales'],
            'timestamp': datetime.now(),
            'datos_cliente': cliente,
            'estado': 'PENDIENTE'
        }
        
        return alerta
    
    def _enviar_notificacion_inmediata(self, alerta):
        """Envía notificación inmediata por múltiples canales"""
        for canal in alerta['canales']:
            try:
                if canal == 'email':
                    self._enviar_email(alerta)
                elif canal == 'slack':
                    self._enviar_slack(alerta)
                elif canal == 'sms':
                    self._enviar_sms(alerta)
                elif canal == 'phone':
                    self._programar_llamada(alerta)
            except Exception as e:
                print(f"Error enviando notificación por {canal}: {e}")
    
    def _enviar_email(self, alerta):
        """Envía alerta por email"""
        msg = MIMEMultipart()
        msg['From'] = self.canales_notificacion['email']['username']
        msg['To'] = self._obtener_email_destinatario(alerta['escalacion'])
        msg['Subject'] = f"🚨 ALERTA {alerta['prioridad']}: {alerta['regla']}"
        
        cuerpo = f"""
        Cliente: {alerta['cliente_nombre']} ({alerta['cliente_id']})
        Regla: {alerta['regla']}
        Prioridad: {alerta['prioridad']}
        Acción: {alerta['accion']}
        Tiempo de Respuesta: {alerta['tiempo_respuesta']}
        Timestamp: {alerta['timestamp']}
        
        Datos del Cliente:
        - Probabilidad de Churn: {alerta['datos_cliente'].get('churn_probability', 'N/A')}
        - LTV: ${alerta['datos_cliente'].get('ltv', 'N/A'):,.2f}
        - NPS: {alerta['datos_cliente'].get('nps_score', 'N/A')}
        - Última Actividad: {alerta['datos_cliente'].get('last_activity', 'N/A')}
        """
        
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        server = smtplib.SMTP(
            self.canales_notificacion['email']['smtp_server'],
            self.canales_notificacion['email']['smtp_port']
        )
        server.starttls()
        server.login(
            self.canales_notificacion['email']['username'],
            self.canales_notificacion['email']['password']
        )
        server.send_message(msg)
        server.quit()
    
    def _enviar_slack(self, alerta):
        """Envía alerta por Slack"""
        mensaje = {
            "channel": self.canales_notificacion['slack']['channel'],
            "text": f"🚨 ALERTA {alerta['prioridad']}: {alerta['regla']}",
            "attachments": [
                {
                    "color": "danger" if alerta['prioridad'] == 'CRÍTICA' else "warning",
                    "fields": [
                        {"title": "Cliente", "value": alerta['cliente_nombre'], "short": True},
                        {"title": "ID", "value": alerta['cliente_id'], "short": True},
                        {"title": "Prioridad", "value": alerta['prioridad'], "short": True},
                        {"title": "Acción", "value": alerta['accion'], "short": True},
                        {"title": "Tiempo Respuesta", "value": alerta['tiempo_respuesta'], "short": True}
                    ]
                }
            ]
        }
        
        requests.post(
            self.canales_notificacion['slack']['webhook_url'],
            json=mensaje
        )
    
    def _enviar_sms(self, alerta):
        """Envía alerta por SMS"""
        # Implementar con Twilio o similar
        pass
    
    def _programar_llamada(self, alerta):
        """Programa llamada automática"""
        # Implementar con sistema de llamadas automáticas
        pass
    
    def _obtener_email_destinatario(self, escalacion):
        """Obtiene email del destinatario según escalación"""
        emails_escalacion = {
            'ejecutivo': 'ceo@company.com',
            'customer_success': 'cs@company.com',
            'analista': 'analytics@company.com',
            'marketing': 'marketing@company.com'
        }
        return emails_escalacion.get(escalacion, 'alerts@company.com')
```

---

## 🎯 Resumen de Herramientas de Visualización

### **1. Dashboard Interactivo Avanzado**
- Múltiples pestañas especializadas
- Filtros dinámicos
- Gráficos interactivos
- Actualización en tiempo real

### **2. Visualizaciones Especializadas**
- Gráficos de tendencia con múltiples métricas
- Predicciones con intervalos de confianza
- Redes de clientes e influencia
- Diagramas Sankey para flujos

### **3. Reportes Automatizados**
- Reportes ejecutivos en PDF/Excel
- Reportes técnicos detallados
- Generación automática
- Múltiples formatos

### **4. Sistema de Alertas Inteligentes**
- Alertas en tiempo real
- Múltiples canales de notificación
- Escalación automática
- Seguimiento de alertas

---

*Estas herramientas proporcionan capacidades completas de visualización, reporting y alertas para un análisis de churn y retención de nivel empresarial.*
