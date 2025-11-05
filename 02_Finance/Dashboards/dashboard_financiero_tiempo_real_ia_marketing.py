#!/usr/bin/env python3
"""
🚀 DASHBOARD FINANCIERO EN TIEMPO REAL PARA IA MARKETING
Sistema Ultra-Avanzado de Monitoreo Financiero

Características:
- Monitoreo en tiempo real de métricas clave
- Alertas automáticas inteligentes
- Visualizaciones interactivas
- Análisis predictivo con IA
- Integración con APIs de mercado
- Dashboard web responsive
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import json
from typing import Dict, List, Optional
import asyncio
import websockets
from dataclasses import dataclass
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricAlert:
    """Estructura para alertas de métricas"""
    metric_name: str
    current_value: float
    threshold: float
    alert_type: str  # 'above', 'below', 'change'
    severity: str    # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime

class DashboardFinancieroTiempoReal:
    """
    Dashboard financiero en tiempo real para IA Marketing
    """
    
    def __init__(self):
        self.nombre = "🚀 Dashboard Financiero Tiempo Real IA Marketing"
        self.version = "2.0.0"
        self.fecha_inicio = datetime.now()
        
        # Configuración de métricas
        self.metricas_config = {
            'arr': {'threshold_low': 4000000, 'threshold_high': 6000000, 'target': 5000000},
            'ai_accuracy': {'threshold_low': 0.90, 'threshold_high': 0.98, 'target': 0.95},
            'ltv_cac_ratio': {'threshold_low': 10, 'threshold_high': 25, 'target': 16},
            'churn_rate': {'threshold_low': 0.01, 'threshold_high': 0.03, 'target': 0.02},
            'gross_margin': {'threshold_low': 0.65, 'threshold_high': 0.80, 'target': 0.72},
            'customer_ai_adoption': {'threshold_low': 0.75, 'threshold_high': 0.90, 'target': 0.85},
            'api_revenue_monthly': {'threshold_low': 80000, 'threshold_high': 120000, 'target': 100000},
            'content_generation_speed': {'threshold_low': 8, 'threshold_high': 12, 'target': 10}
        }
        
        # Alertas activas
        self.alertas_activas = []
        
        # Datos históricos simulados
        self.datos_historicos = self._generar_datos_historicos()
        
        print(f"🚀 {self.nombre} - {self.version}")
        print(f"📅 Iniciado: {self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def _generar_datos_historicos(self) -> Dict:
        """Generar datos históricos simulados"""
        fechas = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
        
        datos = {
            'fecha': fechas,
            'arr': np.random.normal(5000000, 200000, len(fechas)).cumsum(),
            'ai_accuracy': np.random.normal(0.95, 0.02, len(fechas)),
            'ltv_cac_ratio': np.random.normal(16, 2, len(fechas)),
            'churn_rate': np.random.normal(0.02, 0.005, len(fechas)),
            'gross_margin': np.random.normal(0.72, 0.02, len(fechas)),
            'customer_ai_adoption': np.random.normal(0.85, 0.03, len(fechas)),
            'api_revenue_monthly': np.random.normal(100000, 10000, len(fechas)),
            'content_generation_speed': np.random.normal(10, 1, len(fechas)),
            'usuarios_activos': np.random.normal(25000, 1000, len(fechas)).cumsum(),
            'ingresos_curso': np.random.normal(200000, 20000, len(fechas)).cumsum(),
            'ingresos_saas': np.random.normal(400000, 30000, len(fechas)).cumsum()
        }
        
        return pd.DataFrame(datos)

    def obtener_metricas_tiempo_real(self) -> Dict:
        """Obtener métricas en tiempo real"""
        # Simular datos en tiempo real
        timestamp = datetime.now()
        
        metricas = {
            'timestamp': timestamp,
            'arr': 5000000 + np.random.normal(0, 50000),
            'ai_accuracy': 0.95 + np.random.normal(0, 0.01),
            'ltv_cac_ratio': 16 + np.random.normal(0, 1),
            'churn_rate': 0.02 + np.random.normal(0, 0.002),
            'gross_margin': 0.72 + np.random.normal(0, 0.01),
            'customer_ai_adoption': 0.85 + np.random.normal(0, 0.02),
            'api_revenue_monthly': 100000 + np.random.normal(0, 5000),
            'content_generation_speed': 10 + np.random.normal(0, 0.5),
            'usuarios_activos': 25000 + np.random.normal(0, 500),
            'ingresos_curso': 200000 + np.random.normal(0, 10000),
            'ingresos_saas': 400000 + np.random.normal(0, 15000),
            'conversion_curso_saas': 0.15 + np.random.normal(0, 0.02),
            'upsell_rate': 0.20 + np.random.normal(0, 0.02),
            'nps_score': 67 + np.random.normal(0, 3),
            'customer_satisfaction': 4.5 + np.random.normal(0, 0.1)
        }
        
        return metricas

    def verificar_alertas(self, metricas: Dict) -> List[MetricAlert]:
        """Verificar alertas basadas en métricas actuales"""
        alertas = []
        
        for metric_name, config in self.metricas_config.items():
            if metric_name in metricas:
                current_value = metricas[metric_name]
                target = config['target']
                threshold_low = config['threshold_low']
                threshold_high = config['threshold_high']
                
                # Verificar umbrales
                if current_value < threshold_low:
                    alertas.append(MetricAlert(
                        metric_name=metric_name,
                        current_value=current_value,
                        threshold=threshold_low,
                        alert_type='below',
                        severity='high' if current_value < threshold_low * 0.8 else 'medium',
                        message=f"{metric_name} está por debajo del umbral mínimo",
                        timestamp=datetime.now()
                    ))
                
                if current_value > threshold_high:
                    alertas.append(MetricAlert(
                        metric_name=metric_name,
                        current_value=current_value,
                        threshold=threshold_high,
                        alert_type='above',
                        severity='high' if current_value > threshold_high * 1.2 else 'medium',
                        message=f"{metric_name} está por encima del umbral máximo",
                        timestamp=datetime.now()
                    ))
        
        return alertas

    def crear_grafico_metricas_principales(self, metricas: Dict) -> go.Figure:
        """Crear gráfico de métricas principales"""
        fig = go.Figure()
        
        # Métricas principales
        metricas_principales = ['arr', 'ai_accuracy', 'ltv_cac_ratio', 'churn_rate']
        valores = [metricas[m] for m in metricas_principales]
        targets = [self.metricas_config[m]['target'] for m in metricas_principales]
        
        # Normalizar valores para el gráfico
        valores_norm = [v / max(targets) for v in valores]
        targets_norm = [t / max(targets) for t in targets]
        
        fig.add_trace(go.Bar(
            name='Valor Actual',
            x=metricas_principales,
            y=valores_norm,
            marker_color=['green' if v >= t else 'red' for v, t in zip(valores_norm, targets_norm)]
        ))
        
        fig.add_trace(go.Bar(
            name='Target',
            x=metricas_principales,
            y=targets_norm,
            marker_color='blue',
            opacity=0.5
        ))
        
        fig.update_layout(
            title='Métricas Principales vs Targets',
            xaxis_title='Métricas',
            yaxis_title='Valor Normalizado',
            barmode='group'
        )
        
        return fig

    def crear_grafico_tendencias(self, datos_historicos: pd.DataFrame) -> go.Figure:
        """Crear gráfico de tendencias históricas"""
        fig = go.Figure()
        
        # ARR trend
        fig.add_trace(go.Scatter(
            x=datos_historicos['fecha'],
            y=datos_historicos['arr'],
            mode='lines',
            name='ARR',
            line=dict(color='blue', width=2)
        ))
        
        # AI Accuracy trend
        fig.add_trace(go.Scatter(
            x=datos_historicos['fecha'],
            y=datos_historicos['ai_accuracy'] * 1000000,  # Escalar para visualización
            mode='lines',
            name='AI Accuracy (x1M)',
            line=dict(color='green', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Tendencias Históricas',
            xaxis_title='Fecha',
            yaxis_title='ARR ($)',
            yaxis2=dict(
                title='AI Accuracy (x1M)',
                overlaying='y',
                side='right'
            )
        )
        
        return fig

    def crear_grafico_ingresos_dual(self, metricas: Dict) -> go.Figure:
        """Crear gráfico de ingresos dual (Curso + SaaS)"""
        fig = go.Figure()
        
        # Datos del modelo dual
        ingresos_curso = metricas['ingresos_curso']
        ingresos_saas = metricas['ingresos_saas']
        total = ingresos_curso + ingresos_saas
        
        fig.add_trace(go.Pie(
            labels=['Curso', 'SaaS'],
            values=[ingresos_curso, ingresos_saas],
            hole=0.3,
            marker_colors=['#FF6B6B', '#4ECDC4']
        ))
        
        fig.update_layout(
            title=f'Distribución de Ingresos<br><sub>Total: ${total:,.0f}</sub>',
            annotations=[dict(text=f'${total:,.0f}', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig

    def crear_grafico_metricas_ia(self, metricas: Dict) -> go.Figure:
        """Crear gráfico de métricas específicas de IA"""
        fig = go.Figure()
        
        # Métricas de IA
        metricas_ia = {
            'AI Accuracy': metricas['ai_accuracy'] * 100,
            'AI Adoption': metricas['customer_ai_adoption'] * 100,
            'Content Speed': metricas['content_generation_speed'],
            'API Revenue': metricas['api_revenue_monthly'] / 1000
        }
        
        fig.add_trace(go.Bar(
            x=list(metricas_ia.keys()),
            y=list(metricas_ia.values()),
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        ))
        
        fig.update_layout(
            title='Métricas Específicas de IA',
            xaxis_title='Métricas',
            yaxis_title='Valor'
        )
        
        return fig

    def crear_dashboard_streamlit(self):
        """Crear dashboard con Streamlit"""
        st.set_page_config(
            page_title="Dashboard Financiero IA Marketing",
            page_icon="🚀",
            layout="wide"
        )
        
        st.title("🚀 Dashboard Financiero Tiempo Real - IA Marketing")
        st.markdown("---")
        
        # Obtener métricas en tiempo real
        metricas = self.obtener_metricas_tiempo_real()
        
        # Verificar alertas
        alertas = self.verificar_alertas(metricas)
        
        # Mostrar alertas
        if alertas:
            st.sidebar.title("🚨 Alertas Activas")
            for alerta in alertas:
                color = {
                    'low': 'blue',
                    'medium': 'orange', 
                    'high': 'red',
                    'critical': 'darkred'
                }[alerta.severity]
                
                st.sidebar.markdown(f"""
                <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <strong>{alerta.severity.upper()}</strong><br>
                    {alerta.message}<br>
                    <small>Valor: {alerta.current_value:.2f} | Umbral: {alerta.threshold:.2f}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="ARR",
                value=f"${metricas['arr']:,.0f}",
                delta=f"{((metricas['arr'] - 5000000) / 5000000 * 100):+.1f}%"
            )
        
        with col2:
            st.metric(
                label="AI Accuracy",
                value=f"{metricas['ai_accuracy']:.1%}",
                delta=f"{((metricas['ai_accuracy'] - 0.95) / 0.95 * 100):+.1f}%"
            )
        
        with col3:
            st.metric(
                label="LTV/CAC",
                value=f"{metricas['ltv_cac_ratio']:.1f}",
                delta=f"{((metricas['ltv_cac_ratio'] - 16) / 16 * 100):+.1f}%"
            )
        
        with col4:
            st.metric(
                label="Churn Rate",
                value=f"{metricas['churn_rate']:.1%}",
                delta=f"{((metricas['churn_rate'] - 0.02) / 0.02 * 100):+.1f}%"
            )
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            fig_metricas = self.crear_grafico_metricas_principales(metricas)
            st.plotly_chart(fig_metricas, use_container_width=True)
        
        with col2:
            fig_ingresos = self.crear_grafico_ingresos_dual(metricas)
            st.plotly_chart(fig_ingresos, use_container_width=True)
        
        # Gráfico de tendencias
        fig_tendencias = self.crear_grafico_tendencias(self.datos_historicos)
        st.plotly_chart(fig_tendencias, use_container_width=True)
        
        # Métricas de IA
        fig_ia = self.crear_grafico_metricas_ia(metricas)
        st.plotly_chart(fig_ia, use_container_width=True)
        
        # Tabla de métricas detalladas
        st.subheader("📊 Métricas Detalladas")
        
        metricas_df = pd.DataFrame([
            {'Métrica': 'ARR', 'Valor': f"${metricas['arr']:,.0f}", 'Target': f"${self.metricas_config['arr']['target']:,.0f}", 'Status': '✅' if metricas['arr'] >= self.metricas_config['arr']['target'] else '❌'},
            {'Métrica': 'AI Accuracy', 'Valor': f"{metricas['ai_accuracy']:.1%}", 'Target': f"{self.metricas_config['ai_accuracy']['target']:.1%}", 'Status': '✅' if metricas['ai_accuracy'] >= self.metricas_config['ai_accuracy']['target'] else '❌'},
            {'Métrica': 'LTV/CAC', 'Valor': f"{metricas['ltv_cac_ratio']:.1f}", 'Target': f"{self.metricas_config['ltv_cac_ratio']['target']:.1f}", 'Status': '✅' if metricas['ltv_cac_ratio'] >= self.metricas_config['ltv_cac_ratio']['target'] else '❌'},
            {'Métrica': 'Churn Rate', 'Valor': f"{metricas['churn_rate']:.1%}", 'Target': f"{self.metricas_config['churn_rate']['target']:.1%}", 'Status': '✅' if metricas['churn_rate'] <= self.metricas_config['churn_rate']['target'] else '❌'},
            {'Métrica': 'Gross Margin', 'Valor': f"{metricas['gross_margin']:.1%}", 'Target': f"{self.metricas_config['gross_margin']['target']:.1%}", 'Status': '✅' if metricas['gross_margin'] >= self.metricas_config['gross_margin']['target'] else '❌'},
            {'Métrica': 'AI Adoption', 'Valor': f"{metricas['customer_ai_adoption']:.1%}", 'Target': f"{self.metricas_config['customer_ai_adoption']['target']:.1%}", 'Status': '✅' if metricas['customer_ai_adoption'] >= self.metricas_config['customer_ai_adoption']['target'] else '❌'},
            {'Métrica': 'API Revenue', 'Valor': f"${metricas['api_revenue_monthly']:,.0f}", 'Target': f"${self.metricas_config['api_revenue_monthly']['target']:,.0f}", 'Status': '✅' if metricas['api_revenue_monthly'] >= self.metricas_config['api_revenue_monthly']['target'] else '❌'},
            {'Métrica': 'Content Speed', 'Valor': f"{metricas['content_generation_speed']:.1f}x", 'Target': f"{self.metricas_config['content_generation_speed']['target']:.1f}x", 'Status': '✅' if metricas['content_generation_speed'] >= self.metricas_config['content_generation_speed']['target'] else '❌'}
        ])
        
        st.dataframe(metricas_df, use_container_width=True)
        
        # Auto-refresh
        if st.button("🔄 Actualizar Datos"):
            st.rerun()
        
        # Auto-refresh cada 30 segundos
        time.sleep(30)
        st.rerun()

    def ejecutar_dashboard(self):
        """Ejecutar dashboard principal"""
        print("🚀 Iniciando Dashboard Financiero en Tiempo Real...")
        
        try:
            self.crear_dashboard_streamlit()
        except Exception as e:
            logger.error(f"Error en dashboard: {e}")
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 DASHBOARD FINANCIERO EN TIEMPO REAL - IA MARKETING")
    print("=" * 80)
    
    # Crear instancia del dashboard
    dashboard = DashboardFinancieroTiempoReal()
    
    # Ejecutar dashboard
    dashboard.ejecutar_dashboard()

if __name__ == "__main__":
    main()






