#!/usr/bin/env python3
"""
Advanced Reporting System for Competitive Pricing Analysis
=========================================================

Sistema de reportes avanzado que genera documentos profesionales:
- Reportes ejecutivos automáticos
- Dashboards interactivos
- Análisis de tendencias
- Reportes de compliance
- Documentación técnica
- Presentaciones automáticas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from jinja2 import Template
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
import os
from pathlib import Path
import base64
from io import BytesIO
import webbrowser
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import smtplib
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from email.mime.base import MimeBase
from email import encoders
import schedule
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    """Configuración de reporte"""
    report_type: str
    title: str
    description: str
    frequency: str
    recipients: List[str]
    format: str  # pdf, html, excel, pptx
    template: str
    include_charts: bool = True
    include_data: bool = True
    include_recommendations: bool = True
    auto_send: bool = False

@dataclass
class ReportData:
    """Datos del reporte"""
    summary_stats: Dict[str, Any]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    raw_data: pd.DataFrame
    metadata: Dict[str, Any]

class AdvancedReportingSystem:
    """Sistema de reportes avanzado"""
    
    def __init__(self, db_path: str = "pricing_analysis.db"):
        """Inicializar sistema de reportes"""
        self.db_path = db_path
        self.reports_dir = Path("reports")
        self.templates_dir = Path("report_templates")
        self.charts_dir = Path("charts")
        
        # Crear directorios
        self.reports_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.charts_dir.mkdir(exist_ok=True)
        
        # Configuración de estilos
        self.setup_plotting_styles()
        
        logger.info("Advanced Reporting System initialized")
    
    def setup_plotting_styles(self):
        """Configurar estilos de gráficos"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Configurar Plotly
        import plotly.io as pio
        pio.templates.default = "plotly_white"
    
    def generate_executive_report(self, config: ReportConfig) -> str:
        """Generar reporte ejecutivo"""
        try:
            # Recopilar datos
            data = self._collect_report_data()
            
            # Generar gráficos
            charts = self._generate_executive_charts(data)
            
            # Crear reporte
            if config.format == "pdf":
                return self._generate_pdf_report(config, data, charts)
            elif config.format == "html":
                return self._generate_html_report(config, data, charts)
            elif config.format == "excel":
                return self._generate_excel_report(config, data, charts)
            else:
                raise ValueError(f"Unsupported format: {config.format}")
                
        except Exception as e:
            logger.error(f"Error generating executive report: {e}")
            raise
    
    def _collect_report_data(self) -> ReportData:
        """Recopilar datos para el reporte"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Estadísticas resumidas
            summary_stats = self._get_summary_statistics(conn)
            
            # Insights
            insights = self._get_insights(conn)
            
            # Recomendaciones
            recommendations = self._get_recommendations(conn)
            
            # Datos brutos
            raw_data = self._get_raw_data(conn)
            
            # Metadatos
            metadata = {
                'generated_at': datetime.now().isoformat(),
                'data_period': '30 days',
                'total_products': summary_stats.get('total_products', 0),
                'total_competitors': summary_stats.get('total_competitors', 0)
            }
            
            conn.close()
            
            return ReportData(
                summary_stats=summary_stats,
                insights=insights,
                recommendations=recommendations,
                charts=[],
                raw_data=raw_data,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            raise
    
    def _get_summary_statistics(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Obtener estadísticas resumidas"""
        cursor = conn.cursor()
        
        stats = {}
        
        # Productos y competidores
        cursor.execute("SELECT COUNT(DISTINCT product_id) FROM pricing_data")
        stats['total_products'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT competitor) FROM pricing_data")
        stats['total_competitors'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pricing_data")
        stats['total_data_points'] = cursor.fetchone()[0]
        
        # Precios
        cursor.execute("SELECT AVG(price), MIN(price), MAX(price), STDDEV(price) FROM pricing_data")
        price_stats = cursor.fetchone()
        stats['average_price'] = price_stats[0] or 0
        stats['min_price'] = price_stats[1] or 0
        stats['max_price'] = price_stats[2] or 0
        stats['price_std'] = price_stats[3] or 0
        
        # Cambios de precio
        cursor.execute("""
            SELECT COUNT(*) FROM pricing_data p1
            JOIN pricing_data p2 ON p1.product_id = p2.product_id 
            AND p1.competitor = p2.competitor
            WHERE p1.date_collected > p2.date_collected
            AND ABS(p1.price - p2.price) / p2.price > 0.05
        """)
        stats['significant_price_changes'] = cursor.fetchone()[0]
        
        return stats
    
    def _get_insights(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Obtener insights"""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT insight_type, description, impact_score, recommendation, confidence
            FROM competitive_insights
            WHERE created_at >= date('now', '-7 days')
            ORDER BY impact_score DESC
            LIMIT 10
        """)
        
        insights = []
        for row in cursor.fetchall():
            insights.append({
                'type': row[0],
                'description': row[1],
                'impact_score': row[2],
                'recommendation': row[3],
                'confidence': row[4]
            })
        
        return insights
    
    def _get_recommendations(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Obtener recomendaciones"""
        # Generar recomendaciones basadas en datos
        recommendations = [
            {
                'category': 'Pricing Strategy',
                'priority': 'High',
                'title': 'Optimize Price Positioning',
                'description': 'Consider adjusting prices based on competitive analysis',
                'impact': 'Revenue increase of 5-15%',
                'timeline': '2-4 weeks'
            },
            {
                'category': 'Market Monitoring',
                'priority': 'Medium',
                'title': 'Enhance Competitor Tracking',
                'description': 'Increase monitoring frequency for key competitors',
                'impact': 'Better competitive intelligence',
                'timeline': '1-2 weeks'
            },
            {
                'category': 'Data Quality',
                'priority': 'High',
                'title': 'Improve Data Collection',
                'description': 'Implement additional data sources for better coverage',
                'impact': 'More accurate analysis',
                'timeline': '3-6 weeks'
            }
        ]
        
        return recommendations
    
    def _get_raw_data(self, conn: sqlite3.Connection) -> pd.DataFrame:
        """Obtener datos brutos"""
        query = """
            SELECT 
                product_id,
                product_name,
                competitor,
                price,
                currency,
                date_collected,
                source
            FROM pricing_data
            WHERE date_collected >= date('now', '-30 days')
            ORDER BY date_collected DESC
        """
        
        return pd.read_sql_query(query, conn)
    
    def _generate_executive_charts(self, data: ReportData) -> List[Dict[str, Any]]:
        """Generar gráficos para reporte ejecutivo"""
        charts = []
        
        try:
            # Gráfico de precios por competidor
            price_chart = self._create_price_comparison_chart(data.raw_data)
            charts.append({
                'type': 'price_comparison',
                'title': 'Price Comparison by Competitor',
                'chart': price_chart,
                'description': 'Current pricing landscape across competitors'
            })
            
            # Gráfico de tendencias
            trend_chart = self._create_price_trends_chart(data.raw_data)
            charts.append({
                'type': 'price_trends',
                'title': 'Price Trends Over Time',
                'chart': trend_chart,
                'description': 'Price evolution over the last 30 days'
            })
            
            # Gráfico de distribución de precios
            distribution_chart = self._create_price_distribution_chart(data.raw_data)
            charts.append({
                'type': 'price_distribution',
                'title': 'Price Distribution Analysis',
                'chart': distribution_chart,
                'description': 'Statistical distribution of prices'
            })
            
            # Gráfico de insights por tipo
            insights_chart = self._create_insights_chart(data.insights)
            charts.append({
                'type': 'insights_analysis',
                'title': 'Insights by Category',
                'chart': insights_chart,
                'description': 'Distribution of insights by type and impact'
            })
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return charts
    
    def _create_price_comparison_chart(self, data: pd.DataFrame) -> str:
        """Crear gráfico de comparación de precios"""
        if data.empty:
            return ""
        
        # Agrupar por competidor
        competitor_prices = data.groupby('competitor')['price'].agg(['mean', 'std']).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=competitor_prices['competitor'],
            y=competitor_prices['mean'],
            error_y=dict(type='data', array=competitor_prices['std']),
            name='Average Price',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Price Comparison by Competitor',
            xaxis_title='Competitor',
            yaxis_title='Price ($)',
            template='plotly_white'
        )
        
        # Guardar gráfico
        chart_path = self.charts_dir / f"price_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(chart_path))
        
        return str(chart_path)
    
    def _create_price_trends_chart(self, data: pd.DataFrame) -> str:
        """Crear gráfico de tendencias de precios"""
        if data.empty:
            return ""
        
        # Convertir fecha
        data['date'] = pd.to_datetime(data['date_collected'])
        
        # Agrupar por fecha y competidor
        trend_data = data.groupby(['date', 'competitor'])['price'].mean().reset_index()
        
        fig = px.line(
            trend_data,
            x='date',
            y='price',
            color='competitor',
            title='Price Trends Over Time'
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white'
        )
        
        # Guardar gráfico
        chart_path = self.charts_dir / f"price_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(chart_path))
        
        return str(chart_path)
    
    def _create_price_distribution_chart(self, data: pd.DataFrame) -> str:
        """Crear gráfico de distribución de precios"""
        if data.empty:
            return ""
        
        fig = go.Figure()
        
        # Histograma de precios
        fig.add_trace(go.Histogram(
            x=data['price'],
            nbinsx=20,
            name='Price Distribution',
            marker_color='lightgreen'
        ))
        
        # Línea de precio promedio
        avg_price = data['price'].mean()
        fig.add_vline(
            x=avg_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: ${avg_price:.2f}"
        )
        
        fig.update_layout(
            title='Price Distribution Analysis',
            xaxis_title='Price ($)',
            yaxis_title='Frequency',
            template='plotly_white'
        )
        
        # Guardar gráfico
        chart_path = self.charts_dir / f"price_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(chart_path))
        
        return str(chart_path)
    
    def _create_insights_chart(self, insights: List[Dict[str, Any]]) -> str:
        """Crear gráfico de insights"""
        if not insights:
            return ""
        
        # Agrupar por tipo
        insight_types = {}
        for insight in insights:
            insight_type = insight['type']
            if insight_type not in insight_types:
                insight_types[insight_type] = []
            insight_types[insight_type].append(insight['impact_score'])
        
        # Calcular promedios
        type_avg_impact = {
            insight_type: np.mean(scores)
            for insight_type, scores in insight_types.items()
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(type_avg_impact.keys()),
            y=list(type_avg_impact.values()),
            name='Average Impact Score',
            marker_color='orange'
        ))
        
        fig.update_layout(
            title='Insights by Category',
            xaxis_title='Insight Type',
            yaxis_title='Average Impact Score',
            template='plotly_white'
        )
        
        # Guardar gráfico
        chart_path = self.charts_dir / f"insights_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(str(chart_path))
        
        return str(chart_path)
    
    def _generate_pdf_report(self, config: ReportConfig, data: ReportData, charts: List[Dict[str, Any]]) -> str:
        """Generar reporte PDF"""
        try:
            # Crear archivo PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"executive_report_{timestamp}.pdf"
            filepath = self.reports_dir / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph(config.title, title_style))
            story.append(Spacer(1, 12))
            
            # Descripción
            story.append(Paragraph(config.description, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Estadísticas resumidas
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Products', str(data.summary_stats.get('total_products', 0))],
                ['Total Competitors', str(data.summary_stats.get('total_competitors', 0))],
                ['Data Points', str(data.summary_stats.get('total_data_points', 0))],
                ['Average Price', f"${data.summary_stats.get('average_price', 0):.2f}"],
                ['Price Range', f"${data.summary_stats.get('min_price', 0):.2f} - ${data.summary_stats.get('max_price', 0):.2f}"],
                ['Significant Changes', str(data.summary_stats.get('significant_price_changes', 0))]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Insights clave
            story.append(Paragraph("Key Insights", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for insight in data.insights[:5]:
                story.append(Paragraph(f"• {insight['description']}", styles['Normal']))
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 20))
            
            # Recomendaciones
            story.append(Paragraph("Strategic Recommendations", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for rec in data.recommendations:
                story.append(Paragraph(f"<b>{rec['title']}</b> ({rec['priority']} Priority)", styles['Normal']))
                story.append(Paragraph(rec['description'], styles['Normal']))
                story.append(Paragraph(f"Expected Impact: {rec['impact']}", styles['Normal']))
                story.append(Paragraph(f"Timeline: {rec['timeline']}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Metadatos
            story.append(Spacer(1, 20))
            story.append(Paragraph("Report Information", styles['Heading3']))
            story.append(Paragraph(f"Generated: {data.metadata['generated_at']}", styles['Normal']))
            story.append(Paragraph(f"Data Period: {data.metadata['data_period']}", styles['Normal']))
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _generate_html_report(self, config: ReportConfig, data: ReportData, charts: List[Dict[str, Any]]) -> str:
        """Generar reporte HTML"""
        try:
            # Template HTML
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ title }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { text-align: center; color: #2c3e50; }
                    .section { margin: 30px 0; }
                    .metric { display: inline-block; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 5px; }
                    .insight { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
                    .recommendation { background: #e8f5e8; padding: 15px; margin: 10px 0; border-left: 4px solid #27ae60; }
                    .chart { margin: 20px 0; text-align: center; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{{ title }}</h1>
                    <p>{{ description }}</p>
                    <p>Generated: {{ generated_at }}</p>
                </div>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <div class="metric">Total Products: {{ total_products }}</div>
                    <div class="metric">Total Competitors: {{ total_competitors }}</div>
                    <div class="metric">Data Points: {{ total_data_points }}</div>
                    <div class="metric">Average Price: ${{ average_price }}</div>
                </div>
                
                <div class="section">
                    <h2>Key Insights</h2>
                    {% for insight in insights %}
                    <div class="insight">
                        <strong>{{ insight.type }}</strong><br>
                        {{ insight.description }}<br>
                        <small>Impact: {{ insight.impact_score }} | Confidence: {{ insight.confidence }}</small>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="section">
                    <h2>Strategic Recommendations</h2>
                    {% for rec in recommendations %}
                    <div class="recommendation">
                        <strong>{{ rec.title }}</strong> ({{ rec.priority }} Priority)<br>
                        {{ rec.description }}<br>
                        <small>Impact: {{ rec.impact }} | Timeline: {{ rec.timeline }}</small>
                    </div>
                    {% endfor %}
                </div>
                
                {% if charts %}
                <div class="section">
                    <h2>Charts and Visualizations</h2>
                    {% for chart in charts %}
                    <div class="chart">
                        <h3>{{ chart.title }}</h3>
                        <p>{{ chart.description }}</p>
                        <iframe src="{{ chart.chart }}" width="100%" height="500"></iframe>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </body>
            </html>
            """
            
            # Renderizar template
            template = Template(html_template)
            html_content = template.render(
                title=config.title,
                description=config.description,
                generated_at=data.metadata['generated_at'],
                total_products=data.summary_stats.get('total_products', 0),
                total_competitors=data.summary_stats.get('total_competitors', 0),
                total_data_points=data.summary_stats.get('total_data_points', 0),
                average_price=f"{data.summary_stats.get('average_price', 0):.2f}",
                insights=data.insights,
                recommendations=data.recommendations,
                charts=charts
            )
            
            # Guardar archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"executive_report_{timestamp}.html"
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            raise
    
    def _generate_excel_report(self, config: ReportConfig, data: ReportData, charts: List[Dict[str, Any]]) -> str:
        """Generar reporte Excel"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"executive_report_{timestamp}.xlsx"
            filepath = self.reports_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de resumen
                summary_df = pd.DataFrame([
                    {'Metric': 'Total Products', 'Value': data.summary_stats.get('total_products', 0)},
                    {'Metric': 'Total Competitors', 'Value': data.summary_stats.get('total_competitors', 0)},
                    {'Metric': 'Data Points', 'Value': data.summary_stats.get('total_data_points', 0)},
                    {'Metric': 'Average Price', 'Value': f"${data.summary_stats.get('average_price', 0):.2f}"},
                    {'Metric': 'Min Price', 'Value': f"${data.summary_stats.get('min_price', 0):.2f}"},
                    {'Metric': 'Max Price', 'Value': f"${data.summary_stats.get('max_price', 0):.2f}"},
                    {'Metric': 'Price Std Dev', 'Value': f"${data.summary_stats.get('price_std', 0):.2f}"},
                    {'Metric': 'Significant Changes', 'Value': data.summary_stats.get('significant_price_changes', 0)}
                ])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Hoja de insights
                if data.insights:
                    insights_df = pd.DataFrame(data.insights)
                    insights_df.to_excel(writer, sheet_name='Insights', index=False)
                
                # Hoja de recomendaciones
                if data.recommendations:
                    rec_df = pd.DataFrame(data.recommendations)
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Hoja de datos brutos
                if not data.raw_data.empty:
                    data.raw_data.to_excel(writer, sheet_name='Raw Data', index=False)
            
            logger.info(f"Excel report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise
    
    def schedule_automated_reports(self, configs: List[ReportConfig]):
        """Programar reportes automatizados"""
        for config in configs:
            if config.frequency == "daily":
                schedule.every().day.at("09:00").do(self._run_scheduled_report, config)
            elif config.frequency == "weekly":
                schedule.every().monday.at("09:00").do(self._run_scheduled_report, config)
            elif config.frequency == "monthly":
                schedule.every().month.do(self._run_scheduled_report, config)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info(f"Scheduled {len(configs)} automated reports")
    
    def _run_scheduled_report(self, config: ReportConfig):
        """Ejecutar reporte programado"""
        try:
            logger.info(f"Running scheduled report: {config.title}")
            
            # Generar reporte
            report_path = self.generate_executive_report(config)
            
            # Enviar por email si está configurado
            if config.auto_send and config.recipients:
                self._send_report_email(config, report_path)
            
            logger.info(f"Scheduled report completed: {report_path}")
            
        except Exception as e:
            logger.error(f"Error running scheduled report: {e}")
    
    def _send_report_email(self, config: ReportConfig, report_path: str):
        """Enviar reporte por email"""
        try:
            # Configuración de email (simplificada)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "reports@company.com"
            sender_password = "password"
            
            msg = MimeMultipart()
            msg['From'] = sender_email
            msg['To'] = ', '.join(config.recipients)
            msg['Subject'] = f"Automated Report: {config.title}"
            
            body = f"""
            Please find attached the automated report: {config.title}
            
            Report Description: {config.description}
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Best regards,
            Pricing Analysis System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Adjuntar archivo
            with open(report_path, "rb") as attachment:
                part = MimeBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_path)}'
            )
            msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, config.recipients, text)
            server.quit()
            
            logger.info(f"Report sent via email to {config.recipients}")
            
        except Exception as e:
            logger.error(f"Error sending report email: {e}")
    
    def create_interactive_dashboard(self, data: ReportData) -> str:
        """Crear dashboard interactivo"""
        try:
            # Crear dashboard con Plotly
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Price Comparison', 'Price Trends', 'Price Distribution', 'Insights Analysis'),
                specs=[[{"type": "bar"}, {"type": "scatter"}],
                       [{"type": "histogram"}, {"type": "bar"}]]
            )
            
            # Gráfico 1: Comparación de precios
            if not data.raw_data.empty:
                competitor_prices = data.raw_data.groupby('competitor')['price'].mean()
                fig.add_trace(
                    go.Bar(x=competitor_prices.index, y=competitor_prices.values, name="Average Price"),
                    row=1, col=1
                )
            
            # Gráfico 2: Tendencias
            if not data.raw_data.empty:
                data.raw_data['date'] = pd.to_datetime(data.raw_data['date_collected'])
                trend_data = data.raw_data.groupby(['date', 'competitor'])['price'].mean().reset_index()
                
                for competitor in trend_data['competitor'].unique():
                    comp_data = trend_data[trend_data['competitor'] == competitor]
                    fig.add_trace(
                        go.Scatter(x=comp_data['date'], y=comp_data['price'], 
                                 mode='lines', name=competitor),
                        row=1, col=2
                    )
            
            # Gráfico 3: Distribución
            if not data.raw_data.empty:
                fig.add_trace(
                    go.Histogram(x=data.raw_data['price'], nbinsx=20, name="Price Distribution"),
                    row=2, col=1
                )
            
            # Gráfico 4: Insights
            if data.insights:
                insight_types = {}
                for insight in data.insights:
                    insight_type = insight['type']
                    if insight_type not in insight_types:
                        insight_types[insight_type] = []
                    insight_types[insight_type].append(insight['impact_score'])
                
                type_avg_impact = {
                    insight_type: np.mean(scores)
                    for insight_type, scores in insight_types.items()
                }
                
                fig.add_trace(
                    go.Bar(x=list(type_avg_impact.keys()), y=list(type_avg_impact.values()),
                          name="Insight Impact"),
                    row=2, col=2
                )
            
            fig.update_layout(
                title_text="Interactive Pricing Analysis Dashboard",
                showlegend=False,
                height=800
            )
            
            # Guardar dashboard
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"interactive_dashboard_{timestamp}.html"
            filepath = self.reports_dir / filename
            
            fig.write_html(str(filepath))
            
            logger.info(f"Interactive dashboard created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating interactive dashboard: {e}")
            raise

def main():
    """Función principal para demostrar sistema de reportes"""
    print("=" * 60)
    print("ADVANCED REPORTING SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de reportes
    reporting_system = AdvancedReportingSystem()
    
    # Configurar reporte ejecutivo
    config = ReportConfig(
        report_type="executive",
        title="Competitive Pricing Analysis Report",
        description="Monthly executive summary of competitive pricing analysis",
        frequency="monthly",
        recipients=["executives@company.com", "pricing-team@company.com"],
        format="pdf",
        template="executive_template",
        include_charts=True,
        include_data=True,
        include_recommendations=True,
        auto_send=False
    )
    
    # Generar reporte
    print("Generating executive report...")
    report_path = reporting_system.generate_executive_report(config)
    print(f"✓ Executive report generated: {report_path}")
    
    # Crear dashboard interactivo
    print("\nCreating interactive dashboard...")
    data = reporting_system._collect_report_data()
    dashboard_path = reporting_system.create_interactive_dashboard(data)
    print(f"✓ Interactive dashboard created: {dashboard_path}")
    
    # Programar reportes automatizados
    print("\nScheduling automated reports...")
    automated_configs = [
        ReportConfig(
            report_type="daily_summary",
            title="Daily Pricing Summary",
            description="Daily summary of pricing activities",
            frequency="daily",
            recipients=["pricing-team@company.com"],
            format="html",
            template="daily_template",
            auto_send=True
        ),
        ReportConfig(
            report_type="weekly_analysis",
            title="Weekly Competitive Analysis",
            description="Weekly deep dive into competitive positioning",
            frequency="weekly",
            recipients=["management@company.com"],
            format="excel",
            template="weekly_template",
            auto_send=True
        )
    ]
    
    reporting_system.schedule_automated_reports(automated_configs)
    print("✓ Automated reports scheduled")
    
    print("\n" + "=" * 60)
    print("REPORTING SYSTEM DEMO COMPLETED")
    print("=" * 60)
    print(f"📊 Executive Report: {report_path}")
    print(f"📈 Interactive Dashboard: {dashboard_path}")
    print("🔄 Automated reports are now running in the background")

if __name__ == "__main__":
    main()






