"""
Dashboard Interactivo de Optimización Logística
===============================================

Sistema de visualización avanzado con:
- Mapas interactivos
- Dashboards en tiempo real
- Análisis predictivo visual
- Reportes automatizados
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple
import folium
from folium import plugins
import base64
from io import BytesIO

class DashboardInteractivo:
    """Dashboard interactivo para optimización logística"""
    
    def __init__(self):
        self.datos_rutas = []
        self.metricas_tiempo_real = {}
        self.configuracion = {
            'colores_vehiculos': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            'iconos_vehiculos': ['🚚', '🚛', '🏍️', '🚐', '🚲'],
            'zonas_riesgo': [],
            'clientes_prioritarios': []
        }
    
    def crear_mapa_interactivo(self, rutas: List[Dict], puntos_entrega: List[Dict]) -> folium.Map:
        """Crea mapa interactivo con rutas"""
        
        # Calcular centro del mapa
        lats = [p['latitud'] for p in puntos_entrega]
        lons = [p['longitud'] for p in puntos_entrega]
        centro_lat = sum(lats) / len(lats)
        centro_lon = sum(lons) / len(lons)
        
        # Crear mapa base
        mapa = folium.Map(
            location=[centro_lat, centro_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Agregar puntos de entrega
        for punto in puntos_entrega:
            color = self._obtener_color_prioridad(punto['prioridad'])
            icono = self._obtener_icono_tipo_entrega(punto['tipo_entrega'])
            
            folium.Marker(
                [punto['latitud'], punto['longitud']],
                popup=f"""
                <b>{punto['direccion']}</b><br>
                Tipo: {punto['tipo_entrega']}<br>
                Prioridad: {punto['prioridad']}<br>
                Peso: {punto['peso']} kg<br>
                Volumen: {punto['volumen']} m³<br>
                Horario: {punto['horario_apertura']} - {punto['horario_cierre']}
                """,
                tooltip=f"{icono} {punto['id']}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(mapa)
        
        # Agregar rutas
        for i, ruta in enumerate(rutas):
            color = self.configuracion['colores_vehiculos'][i % len(self.configuracion['colores_vehiculos'])]
            
            # Coordenadas de la ruta
            coordenadas_ruta = []
            for punto_idx in ruta['secuencia_optima']:
                punto = puntos_entrega[punto_idx]
                coordenadas_ruta.append([punto['latitud'], punto['longitud']])
            
            # Dibujar línea de ruta
            folium.PolyLine(
                coordenadas_ruta,
                color=color,
                weight=4,
                opacity=0.8,
                popup=f"Ruta {ruta['vehiculo_id']}"
            ).add_to(mapa)
            
            # Marcar inicio de ruta
            if coordenadas_ruta:
                folium.Marker(
                    coordenadas_ruta[0],
                    popup=f"Inicio Ruta {ruta['vehiculo_id']}",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(mapa)
        
        # Agregar zonas de riesgo
        for zona in self.configuracion['zonas_riesgo']:
            folium.CircleMarker(
                [zona['latitud'], zona['longitud']],
                radius=zona['radio'],
                popup=f"Zona de Riesgo: {zona['descripcion']}",
                color='red',
                fill=True,
                fillOpacity=0.2
            ).add_to(mapa)
        
        return mapa
    
    def crear_dashboard_metricas(self, rutas: List[Dict]) -> Dict:
        """Crea dashboard con métricas clave"""
        
        # Preparar datos
        df_rutas = pd.DataFrame(rutas)
        
        # Métricas generales
        metricas_generales = {
            'total_rutas': len(rutas),
            'total_distancia': df_rutas['distancia_total'].sum(),
            'total_tiempo': df_rutas['tiempo_total'].sum(),
            'total_costo': df_rutas['costo_total'].sum(),
            'total_emisiones': df_rutas['emisiones_co2'].sum(),
            'promedio_satisfaccion': df_rutas['satisfaccion_cliente'].mean(),
            'promedio_riesgo': df_rutas['riesgo_total'].mean()
        }
        
        # Gráficos
        graficos = {}
        
        # Gráfico de costos por vehículo
        fig_costos = px.bar(
            df_rutas, 
            x='vehiculo_id', 
            y='costo_total',
            title='Costo por Vehículo',
            color='vehiculo_id',
            color_discrete_sequence=self.configuracion['colores_vehiculos']
        )
        fig_costos.update_layout(showlegend=False)
        graficos['costos'] = fig_costos
        
        # Gráfico de tiempos
        fig_tiempos = px.bar(
            df_rutas,
            x='vehiculo_id',
            y='tiempo_total',
            title='Tiempo por Vehículo',
            color='vehiculo_id',
            color_discrete_sequence=self.configuracion['colores_vehiculos']
        )
        fig_tiempos.update_layout(showlegend=False)
        graficos['tiempos'] = fig_tiempos
        
        # Gráfico de eficiencia
        fig_eficiencia = px.scatter(
            df_rutas,
            x='distancia_total',
            y='costo_total',
            size='emisiones_co2',
            color='satisfaccion_cliente',
            hover_data=['vehiculo_id', 'tiempo_total'],
            title='Eficiencia: Distancia vs Costo',
            color_continuous_scale='RdYlGn'
        )
        graficos['eficiencia'] = fig_eficiencia
        
        # Gráfico de satisfacción vs riesgo
        fig_riesgo = px.scatter(
            df_rutas,
            x='riesgo_total',
            y='satisfaccion_cliente',
            color='vehiculo_id',
            size='costo_total',
            hover_data=['distancia_total', 'tiempo_total'],
            title='Satisfacción vs Riesgo',
            color_discrete_sequence=self.configuracion['colores_vehiculos']
        )
        graficos['riesgo'] = fig_riesgo
        
        return {
            'metricas': metricas_generales,
            'graficos': graficos,
            'dataframe': df_rutas
        }
    
    def crear_analisis_tendencias(self, datos_historicos: List[Dict]) -> Dict:
        """Crea análisis de tendencias temporales"""
        
        if not datos_historicos:
            return {'error': 'No hay datos históricos disponibles'}
        
        df_historico = pd.DataFrame(datos_historicos)
        df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
        
        # Análisis por día de la semana
        df_historico['dia_semana'] = df_historico['fecha'].dt.day_name()
        
        # Gráfico de tendencias de costo
        fig_tendencias_costo = px.line(
            df_historico,
            x='fecha',
            y='costo_total',
            color='vehiculo_id',
            title='Tendencias de Costo en el Tiempo',
            color_discrete_sequence=self.configuracion['colores_vehiculos']
        )
        
        # Gráfico de distribución por día de la semana
        fig_dia_semana = px.box(
            df_historico,
            x='dia_semana',
            y='costo_total',
            title='Distribución de Costos por Día de la Semana',
            color='dia_semana',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Análisis de correlaciones
        correlaciones = df_historico[['costo_total', 'tiempo_total', 'distancia_total', 
                                    'emisiones_co2', 'satisfaccion_cliente']].corr()
        
        fig_correlaciones = px.imshow(
            correlaciones,
            text_auto=True,
            aspect="auto",
            title='Matriz de Correlaciones',
            color_continuous_scale='RdBu'
        )
        
        return {
            'tendencias_costo': fig_tendencias_costo,
            'dia_semana': fig_dia_semana,
            'correlaciones': fig_correlaciones,
            'estadisticas': df_historico.describe()
        }
    
    def crear_analisis_predictivo(self, datos_historicos: List[Dict]) -> Dict:
        """Crea análisis predictivo"""
        
        if len(datos_historicos) < 30:
            return {'error': 'Se necesitan al menos 30 registros históricos'}
        
        df = pd.DataFrame(datos_historicos)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Preparar datos para predicción
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['mes'] = df['fecha'].dt.month
        df['dia_mes'] = df['fecha'].dt.day
        
        # Predicción de costos (simplificada)
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        # Características para predicción
        X = df[['dia_semana', 'mes', 'dia_mes', 'distancia_total', 'tiempo_total']].values
        y = df['costo_total'].values
        
        # Entrenar modelo
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        modelo = LinearRegression()
        modelo.fit(X_scaled, y)
        
        # Predicciones para los próximos 7 días
        fechas_futuras = pd.date_range(start=df['fecha'].max() + timedelta(days=1), periods=7)
        predicciones = []
        
        for fecha in fechas_futuras:
            # Usar valores promedio para características no conocidas
            X_pred = np.array([[
                fecha.dayofweek,
                fecha.month,
                fecha.day,
                df['distancia_total'].mean(),
                df['tiempo_total'].mean()
            ]])
            
            X_pred_scaled = scaler.transform(X_pred)
            costo_predicho = modelo.predict(X_pred_scaled)[0]
            
            predicciones.append({
                'fecha': fecha,
                'costo_predicho': max(0, costo_predicho),
                'confianza': 0.7  # Confianza simplificada
            })
        
        # Gráfico de predicciones
        df_predicciones = pd.DataFrame(predicciones)
        
        fig_predicciones = go.Figure()
        
        # Datos históricos
        fig_predicciones.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['costo_total'],
            mode='lines',
            name='Datos Históricos',
            line=dict(color='blue')
        ))
        
        # Predicciones
        fig_predicciones.add_trace(go.Scatter(
            x=df_predicciones['fecha'],
            y=df_predicciones['costo_predicho'],
            mode='lines+markers',
            name='Predicciones',
            line=dict(color='red', dash='dash'),
            marker=dict(size=8)
        ))
        
        fig_predicciones.update_layout(
            title='Predicción de Costos - Próximos 7 Días',
            xaxis_title='Fecha',
            yaxis_title='Costo Total (USD)',
            hovermode='x unified'
        )
        
        return {
            'predicciones': predicciones,
            'grafico_predicciones': fig_predicciones,
            'modelo_score': modelo.score(X_scaled, y)
        }
    
    def generar_reporte_pdf(self, datos: Dict) -> bytes:
        """Genera reporte en PDF"""
        
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Reporte de Optimización Logística", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Métricas generales
        story.append(Paragraph("Métricas Generales", styles['Heading2']))
        
        metricas_data = [
            ['Métrica', 'Valor'],
            ['Total Rutas', str(datos['metricas']['total_rutas'])],
            ['Distancia Total', f"{datos['metricas']['total_distancia']:.2f} km"],
            ['Tiempo Total', f"{datatos['metricas']['total_tiempo']:.0f} min"],
            ['Costo Total', f"${datos['metricas']['total_costo']:.2f}"],
            ['Emisiones CO2', f"{datos['metricas']['total_emisiones']:.2f} kg"],
            ['Satisfacción Promedio', f"{datos['metricas']['promedio_satisfaccion']:.2f}"],
            ['Riesgo Promedio', f"{datos['metricas']['promedio_riesgo']:.2f}"]
        ]
        
        tabla_metricas = Table(metricas_data)
        tabla_metricas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tabla_metricas)
        story.append(Spacer(1, 12))
        
        # Recomendaciones
        story.append(Paragraph("Recomendaciones", styles['Heading2']))
        
        recomendaciones = [
            "• Optimizar rutas para reducir costos de combustible",
            "• Implementar vehículos eléctricos para reducir emisiones",
            "• Mejorar comunicación con clientes para aumentar satisfacción",
            "• Monitorear zonas de riesgo en tiempo real",
            "• Analizar patrones de tráfico para optimizar horarios"
        ]
        
        for rec in recomendaciones:
            story.append(Paragraph(rec, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _obtener_color_prioridad(self, prioridad: int) -> str:
        """Obtiene color basado en prioridad"""
        colores = {
            5: 'red',    # Crítica
            4: 'orange', # Alta
            3: 'blue',   # Media
            2: 'green',  # Baja
            1: 'gray'    # Mínima
        }
        return colores.get(prioridad, 'gray')
    
    def _obtener_icono_tipo_entrega(self, tipo_entrega: str) -> str:
        """Obtiene icono basado en tipo de entrega"""
        iconos = {
            'urgente': '⚡',
            'estandar': '📦',
            'programada': '📅',
            'fragil': '⚠️',
            'refrigerada': '❄️'
        }
        return iconos.get(tipo_entrega, '📦')

class AplicacionStreamlit:
    """Aplicación Streamlit para el dashboard"""
    
    def __init__(self):
        self.dashboard = DashboardInteractivo()
    
    def ejecutar(self):
        """Ejecuta la aplicación Streamlit"""
        
        st.set_page_config(
            page_title="Optimización Logística",
            page_icon="🚚",
            layout="wide"
        )
        
        st.title("🚚 Sistema de Optimización Logística Avanzado")
        st.markdown("---")
        
        # Sidebar
        st.sidebar.title("Configuración")
        
        # Selección de vista
        vista = st.sidebar.selectbox(
            "Seleccionar Vista",
            ["Dashboard Principal", "Análisis de Tendencias", "Predicciones", "Reportes"]
        )
        
        if vista == "Dashboard Principal":
            self._mostrar_dashboard_principal()
        elif vista == "Análisis de Tendencias":
            self._mostrar_analisis_tendencias()
        elif vista == "Predicciones":
            self._mostrar_predicciones()
        elif vista == "Reportes":
            self._mostrar_reportes()
    
    def _mostrar_dashboard_principal(self):
        """Muestra el dashboard principal"""
        
        # Datos de ejemplo
        rutas_ejemplo = [
            {
                'vehiculo_id': 'V001',
                'distancia_total': 25.5,
                'tiempo_total': 120,
                'costo_total': 85.0,
                'emisiones_co2': 5.1,
                'satisfaccion_cliente': 0.85,
                'riesgo_total': 0.3,
                'secuencia_optima': [0, 1, 2]
            },
            {
                'vehiculo_id': 'V002',
                'distancia_total': 18.2,
                'tiempo_total': 95,
                'costo_total': 72.0,
                'emisiones_co2': 3.6,
                'satisfaccion_cliente': 0.92,
                'riesgo_total': 0.2,
                'secuencia_optima': [3, 4]
            }
        ]
        
        puntos_ejemplo = [
            {
                'id': 'E001',
                'direccion': 'Av. Arequipa 1234',
                'latitud': -12.0464,
                'longitud': -77.0428,
                'prioridad': 5,
                'tipo_entrega': 'urgente',
                'peso': 2.0,
                'volumen': 0.05,
                'horario_apertura': '09:00',
                'horario_cierre': '18:00'
            },
            {
                'id': 'E002',
                'direccion': 'Jr. Larco 567',
                'latitud': -12.0564,
                'longitud': -77.0328,
                'prioridad': 4,
                'tipo_entrega': 'refrigerada',
                'peso': 5.0,
                'volumen': 0.1,
                'horario_apertura': '08:00',
                'horario_cierre': '20:00'
            },
            {
                'id': 'E003',
                'direccion': 'Av. Javier Prado 890',
                'latitud': -12.0364,
                'longitud': -77.0528,
                'prioridad': 3,
                'tipo_entrega': 'fragil',
                'peso': 8.0,
                'volumen': 0.2,
                'horario_apertura': '10:00',
                'horario_cierre': '17:00'
            },
            {
                'id': 'E004',
                'direccion': 'Calle Las Flores 234',
                'latitud': -12.0664,
                'longitud': -77.0228,
                'prioridad': 5,
                'tipo_entrega': 'urgente',
                'peso': 3.0,
                'volumen': 0.08,
                'horario_apertura': '09:30',
                'horario_cierre': '19:00'
            },
            {
                'id': 'E005',
                'direccion': 'Av. Brasil 456',
                'latitud': -12.0264,
                'longitud': -77.0628,
                'prioridad': 3,
                'tipo_entrega': 'estandar',
                'peso': 6.0,
                'volumen': 0.15,
                'horario_apertura': '08:30',
                'horario_cierre': '18:30'
            }
        ]
        
        # Obtener datos del dashboard
        datos_dashboard = self.dashboard.crear_dashboard_metricas(rutas_ejemplo)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Rutas",
                datos_dashboard['metricas']['total_rutas'],
                delta="+2 vs ayer"
            )
        
        with col2:
            st.metric(
                "Costo Total",
                f"${datos_dashboard['metricas']['total_costo']:.2f}",
                delta="-5.2% vs ayer"
            )
        
        with col3:
            st.metric(
                "Distancia Total",
                f"{datos_dashboard['metricas']['total_distancia']:.1f} km",
                delta="+1.3% vs ayer"
            )
        
        with col4:
            st.metric(
                "Satisfacción",
                f"{datos_dashboard['metricas']['promedio_satisfaccion']:.2f}",
                delta="+0.05 vs ayer"
            )
        
        # Gráficos
        st.subheader("📊 Análisis de Rendimiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(datos_dashboard['graficos']['costos'], use_container_width=True)
        
        with col2:
            st.plotly_chart(datos_dashboard['graficos']['tiempos'], use_container_width=True)
        
        st.plotly_chart(datos_dashboard['graficos']['eficiencia'], use_container_width=True)
        
        # Mapa interactivo
        st.subheader("🗺️ Mapa de Rutas")
        
        # Crear mapa
        mapa = self.dashboard.crear_mapa_interactivo(rutas_ejemplo, puntos_ejemplo)
        
        # Convertir mapa a HTML
        mapa_html = mapa._repr_html_()
        st.components.v1.html(mapa_html, height=500)
    
    def _mostrar_analisis_tendencias(self):
        """Muestra análisis de tendencias"""
        
        st.subheader("📈 Análisis de Tendencias")
        
        # Generar datos históricos de ejemplo
        datos_historicos = []
        fecha_base = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            fecha = fecha_base + timedelta(days=i)
            datos_historicos.append({
                'fecha': fecha,
                'vehiculo_id': f'V00{(i % 2) + 1}',
                'costo_total': 80 + np.random.normal(0, 10),
                'tiempo_total': 120 + np.random.normal(0, 20),
                'distancia_total': 25 + np.random.normal(0, 5),
                'emisiones_co2': 5 + np.random.normal(0, 1),
                'satisfaccion_cliente': 0.8 + np.random.normal(0, 0.1)
            })
        
        # Crear análisis de tendencias
        analisis = self.dashboard.crear_analisis_tendencias(datos_historicos)
        
        if 'error' not in analisis:
            st.plotly_chart(analisis['tendencias_costo'], use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(analisis['dia_semana'], use_container_width=True)
            
            with col2:
                st.plotly_chart(analisis['correlaciones'], use_container_width=True)
            
            # Estadísticas
            st.subheader("📊 Estadísticas Descriptivas")
            st.dataframe(analisis['estadisticas'])
        else:
            st.error(analisis['error'])
    
    def _mostrar_predicciones(self):
        """Muestra análisis predictivo"""
        
        st.subheader("🔮 Predicciones y Análisis Predictivo")
        
        # Generar datos históricos para predicción
        datos_historicos = []
        fecha_base = datetime.now() - timedelta(days=60)
        
        for i in range(60):
            fecha = fecha_base + timedelta(days=i)
            datos_historicos.append({
                'fecha': fecha,
                'vehiculo_id': f'V00{(i % 2) + 1}',
                'costo_total': 80 + np.random.normal(0, 10) + i * 0.1,  # Tendencia creciente
                'tiempo_total': 120 + np.random.normal(0, 20),
                'distancia_total': 25 + np.random.normal(0, 5),
                'emisiones_co2': 5 + np.random.normal(0, 1),
                'satisfaccion_cliente': 0.8 + np.random.normal(0, 0.1)
            })
        
        # Crear análisis predictivo
        predicciones = self.dashboard.crear_analisis_predictivo(datos_historicos)
        
        if 'error' not in predicciones:
            st.plotly_chart(predicciones['grafico_predicciones'], use_container_width=True)
            
            # Tabla de predicciones
            st.subheader("📋 Predicciones Detalladas")
            df_predicciones = pd.DataFrame(predicciones['predicciones'])
            st.dataframe(df_predicciones)
            
            # Métricas del modelo
            st.metric("Precisión del Modelo", f"{predicciones['modelo_score']:.3f}")
        else:
            st.error(predicciones['error'])
    
    def _mostrar_reportes(self):
        """Muestra sección de reportes"""
        
        st.subheader("📄 Generación de Reportes")
        
        # Datos para reporte
        datos_reporte = {
            'metricas': {
                'total_rutas': 2,
                'total_distancia': 43.7,
                'total_tiempo': 215,
                'total_costo': 157.0,
                'total_emisiones': 8.7,
                'promedio_satisfaccion': 0.885,
                'promedio_riesgo': 0.25
            }
        }
        
        # Botón para generar reporte
        if st.button("📊 Generar Reporte PDF"):
            with st.spinner("Generando reporte..."):
                reporte_pdf = self.dashboard.generar_reporte_pdf(datos_reporte)
                
                st.success("✅ Reporte generado exitosamente!")
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Reporte PDF",
                    data=reporte_pdf,
                    file_name=f"reporte_logistica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        # Configuración de reporte
        st.subheader("⚙️ Configuración de Reporte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            incluir_graficos = st.checkbox("Incluir Gráficos", value=True)
            incluir_predicciones = st.checkbox("Incluir Predicciones", value=True)
        
        with col2:
            formato_reporte = st.selectbox("Formato", ["PDF", "Excel", "CSV"])
            nivel_detalle = st.selectbox("Nivel de Detalle", ["Resumen", "Detallado", "Completo"])

def ejemplo_dashboard():
    """Ejemplo de uso del dashboard"""
    
    print("=" * 80)
    print("DASHBOARD INTERACTIVO DE OPTIMIZACIÓN LOGÍSTICA")
    print("=" * 80)
    
    # Crear dashboard
    dashboard = DashboardInteractivo()
    
    # Datos de ejemplo
    rutas_ejemplo = [
        {
            'vehiculo_id': 'V001',
            'distancia_total': 25.5,
            'tiempo_total': 120,
            'costo_total': 85.0,
            'emisiones_co2': 5.1,
            'satisfaccion_cliente': 0.85,
            'riesgo_total': 0.3,
            'secuencia_optima': [0, 1, 2]
        },
        {
            'vehiculo_id': 'V002',
            'distancia_total': 18.2,
            'tiempo_total': 95,
            'costo_total': 72.0,
            'emisiones_co2': 3.6,
            'satisfaccion_cliente': 0.92,
            'riesgo_total': 0.2,
            'secuencia_optima': [3, 4]
        }
    ]
    
    puntos_ejemplo = [
        {
            'id': 'E001',
            'direccion': 'Av. Arequipa 1234',
            'latitud': -12.0464,
            'longitud': -77.0428,
            'prioridad': 5,
            'tipo_entrega': 'urgente',
            'peso': 2.0,
            'volumen': 0.05,
            'horario_apertura': '09:00',
            'horario_cierre': '18:00'
        },
        {
            'id': 'E002',
            'direccion': 'Jr. Larco 567',
            'latitud': -12.0564,
            'longitud': -77.0328,
            'prioridad': 4,
            'tipo_entrega': 'refrigerada',
            'peso': 5.0,
            'volumen': 0.1,
            'horario_apertura': '08:00',
            'horario_cierre': '20:00'
        }
    ]
    
    print("\n📊 Creando dashboard de métricas...")
    datos_dashboard = dashboard.crear_dashboard_metricas(rutas_ejemplo)
    
    print("✅ Dashboard creado exitosamente!")
    print(f"   Total rutas: {datos_dashboard['metricas']['total_rutas']}")
    print(f"   Costo total: ${datos_dashboard['metricas']['total_costo']:.2f}")
    print(f"   Satisfacción promedio: {datos_dashboard['metricas']['promedio_satisfaccion']:.2f}")
    
    print("\n🗺️ Creando mapa interactivo...")
    mapa = dashboard.crear_mapa_interactivo(rutas_ejemplo, puntos_ejemplo)
    print("✅ Mapa interactivo creado!")
    
    print("\n📈 Generando análisis de tendencias...")
    datos_historicos = []
    fecha_base = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        fecha = fecha_base + timedelta(days=i)
        datos_historicos.append({
            'fecha': fecha,
            'vehiculo_id': f'V00{(i % 2) + 1}',
            'costo_total': 80 + np.random.normal(0, 10),
            'tiempo_total': 120 + np.random.normal(0, 20),
            'distancia_total': 25 + np.random.normal(0, 5),
            'emisiones_co2': 5 + np.random.normal(0, 1),
            'satisfaccion_cliente': 0.8 + np.random.normal(0, 0.1)
        })
    
    analisis_tendencias = dashboard.crear_analisis_tendencias(datos_historicos)
    
    if 'error' not in analisis_tendencias:
        print("✅ Análisis de tendencias completado!")
    else:
        print(f"⚠️ {analisis_tendencias['error']}")
    
    print("\n🔮 Generando predicciones...")
    predicciones = dashboard.crear_analisis_predictivo(datos_historicos)
    
    if 'error' not in predicciones:
        print("✅ Predicciones generadas!")
        print(f"   Precisión del modelo: {predicciones['modelo_score']:.3f}")
        print(f"   Predicciones para próximos 7 días: {len(predicciones['predicciones'])}")
    else:
        print(f"⚠️ {predicciones['error']}")
    
    print("\n📄 Generando reporte PDF...")
    datos_reporte = {
        'metricas': datos_dashboard['metricas']
    }
    
    reporte_pdf = dashboard.generar_reporte_pdf(datos_reporte)
    print(f"✅ Reporte PDF generado! Tamaño: {len(reporte_pdf)} bytes")
    
    print("\n" + "=" * 80)
    print("✅ DASHBOARD INTERACTIVO COMPLETADO")
    print("=" * 80)
    
    return {
        'dashboard': dashboard,
        'datos_dashboard': datos_dashboard,
        'mapa': mapa,
        'analisis_tendencias': analisis_tendencias,
        'predicciones': predicciones,
        'reporte_pdf': reporte_pdf
    }

if __name__ == "__main__":
    ejemplo_dashboard()



