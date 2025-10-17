#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Interactivo - Anchor Texts IA Marketing
================================================

Este script genera un dashboard HTML interactivo para visualizar y gestionar
todos los aspectos del sistema de anchor texts.

Funcionalidades:
- Dashboard principal con métricas en tiempo real
- Visualizaciones interactivas
- Gestión de anchor texts
- Análisis de rendimiento
- Exportación de datos
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class DashboardInteractivoAnchorTexts:
    def __init__(self):
        self.palabras_clave_base = [
            "curso IA marketing", "inteligencia artificial marketing", "marketing digital IA",
            "curso marketing automatizado", "IA aplicada marketing", "machine learning marketing"
        ]
        
        # Datos simulados para el dashboard
        self.metricas_globales = {
            'total_anchor_texts': 0,
            'total_impresiones': 0,
            'total_clicks': 0,
            'total_conversiones': 0,
            'ctr_promedio': 0.0,
            'conversion_rate_promedio': 0.0,
            'roi_promedio': 0.0,
            'costo_total': 0.0,
            'ingresos_totales': 0.0
        }
        
        self.anchor_texts_activos = []
        self.campanas_activas = []
        self.tendencias_diarias = []

    def generar_datos_simulados(self):
        """Genera datos simulados para el dashboard"""
        # Generar anchor texts activos
        self.anchor_texts_activos = self._generar_anchor_texts_simulados(50)
        
        # Generar campañas activas
        self.campanas_activas = self._generar_campanas_simuladas(10)
        
        # Generar tendencias diarias (últimos 30 días)
        self.tendencias_diarias = self._generar_tendencias_diarias(30)
        
        # Calcular métricas globales
        self._calcular_metricas_globales()

    def _generar_anchor_texts_simulados(self, cantidad: int) -> List[Dict[str, Any]]:
        """Genera anchor texts simulados con métricas"""
        anchor_texts = []
        
        templates = [
            "Curso {palabra_clave} - {beneficio}",
            "Aprende {palabra_clave} en {tiempo}",
            "Domina {palabra_clave} - {garantia}",
            "Masterclass {palabra_clave} {año}",
            "Certificación {palabra_clave} - {modalidad}",
            "IA Marketing: {enfoque} - {resultado}",
            "Transforma tu negocio con {palabra_clave}",
            "El futuro del marketing: {palabra_clave}",
            "Estrategias {palabra_clave} que funcionan",
            "Guía completa de {palabra_clave}"
        ]
        
        beneficios = ["Resultados garantizados", "Éxito asegurado", "ROI comprobado", "Efectividad probada"]
        tiempos = ["30 días", "6 meses", "1 año", "90 días"]
        garantias = ["100% efectivo", "Sin riesgo", "Satisfacción garantizada", "Resultados comprobados"]
        modalidades = ["Online", "Presencial", "Híbrido", "Intensivo"]
        enfoques = ["Avanzado", "Básico", "Profesional", "Especializado"]
        resultados = ["Multiplica ventas", "Aumenta conversiones", "Optimiza ROI", "Escala tu negocio"]
        
        for i in range(cantidad):
            template = random.choice(templates)
            palabra_clave = random.choice(self.palabras_clave_base)
            
            # Reemplazar placeholders
            anchor_text = template.replace('{palabra_clave}', palabra_clave)
            anchor_text = anchor_text.replace('{beneficio}', random.choice(beneficios))
            anchor_text = anchor_text.replace('{tiempo}', random.choice(tiempos))
            anchor_text = anchor_text.replace('{garantia}', random.choice(garantias))
            anchor_text = anchor_text.replace('{año}', '2024')
            anchor_text = anchor_text.replace('{modalidad}', random.choice(modalidades))
            anchor_text = anchor_text.replace('{enfoque}', random.choice(enfoques))
            anchor_text = anchor_text.replace('{resultado}', random.choice(resultados))
            
            # Generar métricas simuladas
            impresiones = random.randint(1000, 50000)
            ctr = random.uniform(0.02, 0.12)
            clicks = int(impresiones * ctr)
            conversion_rate = random.uniform(0.05, 0.30)
            conversiones = int(clicks * conversion_rate)
            costo_click = random.uniform(0.50, 4.00)
            costo_total = clicks * costo_click
            valor_conversion = random.uniform(50, 500)
            ingresos = conversiones * valor_conversion
            roi = (ingresos - costo_total) / costo_total if costo_total > 0 else 0
            
            anchor_texts.append({
                'id': f"at_{i+1:03d}",
                'texto': anchor_text,
                'palabra_clave': palabra_clave,
                'categoria': random.choice(['comercial', 'informativo', 'navegacional']),
                'estado': random.choice(['activo', 'pausado', 'optimizando']),
                'fecha_creacion': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'metricas': {
                    'impresiones': impresiones,
                    'clicks': clicks,
                    'conversiones': conversiones,
                    'ctr': round(ctr * 100, 2),
                    'conversion_rate': round(conversion_rate * 100, 2),
                    'costo_click': round(costo_click, 2),
                    'costo_total': round(costo_total, 2),
                    'ingresos': round(ingresos, 2),
                    'roi': round(roi, 2)
                }
            })
        
        return anchor_texts

    def _generar_campanas_simuladas(self, cantidad: int) -> List[Dict[str, Any]]:
        """Genera campañas simuladas"""
        campanas = []
        
        nombres_campanas = [
            "Campaña Q1 2024", "Black Friday IA Marketing", "Lanzamiento Curso Premium",
            "Retargeting E-commerce", "Generación Leads B2B", "Conversión E-learning",
            "Upselling Clientes", "Cross-selling Servicios", "Fidelización Usuarios",
            "Expansión Mercado"
        ]
        
        for i in range(cantidad):
            fecha_inicio = datetime.now() - timedelta(days=random.randint(1, 60))
            fecha_fin = fecha_inicio + timedelta(days=random.randint(7, 30))
            
            campanas.append({
                'id': f"campana_{i+1:03d}",
                'nombre': random.choice(nombres_campanas),
                'estado': random.choice(['activa', 'pausada', 'finalizada']),
                'fecha_inicio': fecha_inicio.isoformat(),
                'fecha_fin': fecha_fin.isoformat(),
                'presupuesto': random.randint(1000, 10000),
                'gasto_actual': random.randint(100, 5000),
                'objetivo': random.choice(['conversiones', 'leads', 'ventas', 'awareness']),
                'canal': random.choice(['Google Ads', 'Facebook', 'LinkedIn', 'Email', 'SEO']),
                'metricas': {
                    'impresiones': random.randint(10000, 100000),
                    'clicks': random.randint(500, 5000),
                    'conversiones': random.randint(50, 500),
                    'ctr': round(random.uniform(0.03, 0.10) * 100, 2),
                    'conversion_rate': round(random.uniform(0.08, 0.25) * 100, 2),
                    'costo_total': round(random.uniform(500, 3000), 2),
                    'roi': round(random.uniform(1.5, 4.0), 2)
                }
            })
        
        return campanas

    def _generar_tendencias_diarias(self, dias: int) -> List[Dict[str, Any]]:
        """Genera tendencias diarias simuladas"""
        tendencias = []
        fecha_base = datetime.now() - timedelta(days=dias)
        
        for i in range(dias):
            fecha = fecha_base + timedelta(days=i)
            
            # Simular variaciones diarias
            factor_dia_semana = 1.2 if fecha.weekday() < 5 else 0.8  # Más tráfico en días laborables
            factor_tendencia = 1 + (i * 0.01)  # Tendencia creciente ligera
            
            impresiones = int(random.randint(50000, 100000) * factor_dia_semana * factor_tendencia)
            ctr = random.uniform(0.03, 0.08) * factor_dia_semana
            clicks = int(impresiones * ctr)
            conversion_rate = random.uniform(0.10, 0.20)
            conversiones = int(clicks * conversion_rate)
            
            tendencias.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'impresiones': impresiones,
                'clicks': clicks,
                'conversiones': conversiones,
                'ctr': round(ctr * 100, 2),
                'conversion_rate': round(conversion_rate * 100, 2),
                'costo_total': round(clicks * random.uniform(1.0, 3.0), 2),
                'ingresos': round(conversiones * random.uniform(100, 300), 2)
            })
        
        return tendencias

    def _calcular_metricas_globales(self):
        """Calcula las métricas globales del sistema"""
        total_impresiones = sum(at['metricas']['impresiones'] for at in self.anchor_texts_activos)
        total_clicks = sum(at['metricas']['clicks'] for at in self.anchor_texts_activos)
        total_conversiones = sum(at['metricas']['conversiones'] for at in self.anchor_texts_activos)
        total_costo = sum(at['metricas']['costo_total'] for at in self.anchor_texts_activos)
        total_ingresos = sum(at['metricas']['ingresos'] for at in self.anchor_texts_activos)
        
        self.metricas_globales = {
            'total_anchor_texts': len(self.anchor_texts_activos),
            'total_impresiones': total_impresiones,
            'total_clicks': total_clicks,
            'total_conversiones': total_conversiones,
            'ctr_promedio': round((total_clicks / total_impresiones * 100) if total_impresiones > 0 else 0, 2),
            'conversion_rate_promedio': round((total_conversiones / total_clicks * 100) if total_clicks > 0 else 0, 2),
            'roi_promedio': round((total_ingresos - total_costo) / total_costo if total_costo > 0 else 0, 2),
            'costo_total': round(total_costo, 2),
            'ingresos_totales': round(total_ingresos, 2)
        }

    def generar_dashboard_html(self) -> str:
        """Genera el dashboard HTML interactivo"""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Interactivo - Anchor Texts IA Marketing</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #7f8c8d;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .tables-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .table-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .table-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .status-active {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .status-paused {{
            color: #f39c12;
            font-weight: bold;
        }}
        
        .status-optimizing {{
            color: #3498db;
            font-weight: bold;
        }}
        
        .export-buttons {{
            text-align: center;
            margin-top: 30px;
        }}
        
        .btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            margin: 0 10px;
            transition: transform 0.3s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .filters {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .filter-group {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 15px;
        }}
        
        .filter-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .filter-group select, .filter-group input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid, .tables-grid {{
                grid-template-columns: 1fr;
            }}
            
            .metrics-grid {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Dashboard Interactivo - Anchor Texts IA Marketing</h1>
            <p>Gestión y análisis en tiempo real de tu estrategia de anchor texts</p>
        </div>
        
        <div class="filters">
            <h3 style="margin-bottom: 20px; color: #2c3e50;">🔍 Filtros y Búsqueda</h3>
            <div class="filter-group">
                <label for="categoria-filter">Categoría:</label>
                <select id="categoria-filter">
                    <option value="">Todas</option>
                    <option value="comercial">Comercial</option>
                    <option value="informativo">Informativo</option>
                    <option value="navegacional">Navegacional</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="estado-filter">Estado:</label>
                <select id="estado-filter">
                    <option value="">Todos</option>
                    <option value="activo">Activo</option>
                    <option value="pausado">Pausado</option>
                    <option value="optimizando">Optimizando</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="search-input">Buscar:</label>
                <input type="text" id="search-input" placeholder="Buscar anchor text...">
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['total_anchor_texts']}</div>
                <div class="metric-label">Anchor Texts Activos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['total_impresiones']:,}</div>
                <div class="metric-label">Impresiones Totales</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['total_clicks']:,}</div>
                <div class="metric-label">Clicks Totales</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['total_conversiones']:,}</div>
                <div class="metric-label">Conversiones Totales</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['ctr_promedio']}%</div>
                <div class="metric-label">CTR Promedio</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['conversion_rate_promedio']}%</div>
                <div class="metric-label">Tasa de Conversión</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metricas_globales['roi_promedio']}x</div>
                <div class="metric-label">ROI Promedio</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${self.metricas_globales['ingresos_totales']:,}</div>
                <div class="metric-label">Ingresos Totales</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">📈 Tendencias Diarias (Últimos 30 días)</div>
                <canvas id="tendenciasChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">🎯 Distribución por Categoría</div>
                <canvas id="categoriaChart"></canvas>
            </div>
        </div>
        
        <div class="tables-grid">
            <div class="table-container">
                <div class="table-title">🏆 Top 10 Anchor Texts por CTR</div>
                <table id="top-ctr-table">
                    <thead>
                        <tr>
                            <th>Anchor Text</th>
                            <th>CTR</th>
                            <th>Conversiones</th>
                            <th>ROI</th>
                        </tr>
                    </thead>
                    <tbody id="top-ctr-tbody">
                    </tbody>
                </table>
            </div>
            <div class="table-container">
                <div class="table-title">📊 Campañas Activas</div>
                <table id="campanas-table">
                    <thead>
                        <tr>
                            <th>Campaña</th>
                            <th>Estado</th>
                            <th>CTR</th>
                            <th>Conversiones</th>
                        </tr>
                    </thead>
                    <tbody id="campanas-tbody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="export-buttons">
            <button class="btn" onclick="exportarDatos('json')">📄 Exportar JSON</button>
            <button class="btn" onclick="exportarDatos('csv')">📊 Exportar CSV</button>
            <button class="btn" onclick="exportarDatos('excel')">📈 Exportar Excel</button>
            <button class="btn" onclick="actualizarDashboard()">🔄 Actualizar Datos</button>
        </div>
    </div>

    <script>
        // Datos del dashboard
        const dashboardData = {json.dumps({
            'anchor_texts': self.anchor_texts_activos,
            'campanas': self.campanas_activas,
            'tendencias': self.tendencias_diarias,
            'metricas': self.metricas_globales
        }, ensure_ascii=False, indent=2)};
        
        // Inicializar gráficos
        function inicializarGraficos() {{
            // Gráfico de tendencias
            const tendenciasCtx = document.getElementById('tendenciasChart').getContext('2d');
            new Chart(tendenciasCtx, {{
                type: 'line',
                data: {{
                    labels: dashboardData.tendencias.map(t => t.fecha),
                    datasets: [{{
                        label: 'CTR (%)',
                        data: dashboardData.tendencias.map(t => t.ctr),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }}, {{
                        label: 'Conversiones',
                        data: dashboardData.tendencias.map(t => t.conversiones),
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }}
                }}
            }});
            
            // Gráfico de categorías
            const categoriaCtx = document.getElementById('categoriaChart').getContext('2d');
            const categorias = {{}};
            dashboardData.anchor_texts.forEach(at => {{
                categorias[at.categoria] = (categorias[at.categoria] || 0) + 1;
            }});
            
            new Chart(categoriaCtx, {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(categorias),
                    datasets: [{{
                        data: Object.values(categorias),
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // Actualizar tablas
        function actualizarTablas() {{
            // Top CTR table
            const topCtrTbody = document.getElementById('top-ctr-tbody');
            const topCtr = dashboardData.anchor_texts
                .sort((a, b) => b.metricas.ctr - a.metricas.ctr)
                .slice(0, 10);
            
            topCtrTbody.innerHTML = topCtr.map(at => `
                <tr>
                    <td>${{at.texto}}</td>
                    <td>${{at.metricas.ctr}}%</td>
                    <td>${{at.metricas.conversiones}}</td>
                    <td>${{at.metricas.roi}}x</td>
                </tr>
            `).join('');
            
            // Campañas table
            const campanasTbody = document.getElementById('campanas-tbody');
            campanasTbody.innerHTML = dashboardData.campanas.map(c => `
                <tr>
                    <td>${{c.nombre}}</td>
                    <td><span class="status-${{c.estado}}">${{c.estado}}</span></td>
                    <td>${{c.metricas.ctr}}%</td>
                    <td>${{c.metricas.conversiones}}</td>
                </tr>
            `).join('');
        }}
        
        // Filtros
        function aplicarFiltros() {{
            const categoria = document.getElementById('categoria-filter').value;
            const estado = document.getElementById('estado-filter').value;
            const busqueda = document.getElementById('search-input').value.toLowerCase();
            
            let anchorTextsFiltrados = dashboardData.anchor_texts;
            
            if (categoria) {{
                anchorTextsFiltrados = anchorTextsFiltrados.filter(at => at.categoria === categoria);
            }}
            
            if (estado) {{
                anchorTextsFiltrados = anchorTextsFiltrados.filter(at => at.estado === estado);
            }}
            
            if (busqueda) {{
                anchorTextsFiltrados = anchorTextsFiltrados.filter(at => 
                    at.texto.toLowerCase().includes(busqueda)
                );
            }}
            
            // Actualizar tabla con filtros aplicados
            const topCtrTbody = document.getElementById('top-ctr-tbody');
            const topCtr = anchorTextsFiltrados
                .sort((a, b) => b.metricas.ctr - a.metricas.ctr)
                .slice(0, 10);
            
            topCtrTbody.innerHTML = topCtr.map(at => `
                <tr>
                    <td>${{at.texto}}</td>
                    <td>${{at.metricas.ctr}}%</td>
                    <td>${{at.metricas.conversiones}}</td>
                    <td>${{at.metricas.roi}}x</td>
                </tr>
            `).join('');
        }}
        
        // Exportar datos
        function exportarDatos(formato) {{
            const dataStr = JSON.stringify(dashboardData, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `dashboard_anchor_texts_${{new Date().toISOString().split('T')[0]}}.${{formato}}`;
            link.click();
        }}
        
        // Actualizar dashboard
        function actualizarDashboard() {{
            location.reload();
        }}
        
        // Event listeners
        document.getElementById('categoria-filter').addEventListener('change', aplicarFiltros);
        document.getElementById('estado-filter').addEventListener('change', aplicarFiltros);
        document.getElementById('search-input').addEventListener('input', aplicarFiltros);
        
        // Inicializar dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            inicializarGraficos();
            actualizarTablas();
        }});
    </script>
</body>
</html>
        """
        return html_content

    def guardar_dashboard(self, filename: str = None) -> str:
        """Guarda el dashboard en un archivo HTML"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_anchor_texts_{timestamp}.html"
        
        html_content = self.generar_dashboard_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def main():
    dashboard = DashboardInteractivoAnchorTexts()
    
    print("📊 DASHBOARD INTERACTIVO - ANCHOR TEXTS IA MARKETING")
    print("==================================================\n")
    
    print("🔄 Generando datos simulados...")
    dashboard.generar_datos_simulados()
    
    print("🔄 Creando dashboard interactivo...")
    filename = dashboard.guardar_dashboard()
    
    print(f"\n✅ Dashboard creado exitosamente:")
    print(f"   • Archivo: {filename}")
    print(f"   • Anchor texts: {dashboard.metricas_globales['total_anchor_texts']}")
    print(f"   • Campañas: {len(dashboard.campanas_activas)}")
    print(f"   • Impresiones totales: {dashboard.metricas_globales['total_impresiones']:,}")
    print(f"   • CTR promedio: {dashboard.metricas_globales['ctr_promedio']}%")
    print(f"   • ROI promedio: {dashboard.metricas_globales['roi_promedio']}x")
    
    print(f"\n🎯 CARACTERÍSTICAS DEL DASHBOARD:")
    print("• Métricas en tiempo real")
    print("• Gráficos interactivos")
    print("• Filtros avanzados")
    print("• Tablas de rendimiento")
    print("• Exportación de datos")
    print("• Diseño responsive")
    
    print(f"\n💡 PRÓXIMOS PASOS:")
    print("1. Abre el archivo HTML en tu navegador")
    print("2. Explora las diferentes secciones")
    print("3. Usa los filtros para analizar datos específicos")
    print("4. Exporta los datos que necesites")
    print("5. Actualiza regularmente con datos reales")

if __name__ == "__main__":
    main()




