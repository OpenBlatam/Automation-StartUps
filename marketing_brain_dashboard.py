#!/usr/bin/env python3
"""
🎯 MARKETING BRAIN DASHBOARD
Dashboard Interactivo para el Advanced Marketing Brain System
Visualización en Tiempo Real de Conceptos y Sugerencias
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import sys

# Agregar el directorio actual al path para importar el sistema
sys.path.append(str(Path(__file__).parent))
from advanced_marketing_brain_system import AdvancedMarketingBrain, MarketingConcept

class MarketingBrainDashboard:
    """Dashboard interactivo para el Advanced Marketing Brain System"""
    
    def __init__(self):
        self.brain = None
        self.concepts = []
        self.suggestions = []
        self.insights = {}
        
    def initialize_brain(self):
        """Inicializar el sistema de IA"""
        try:
            self.brain = AdvancedMarketingBrain()
            return True
        except Exception as e:
            st.error(f"Error al inicializar el sistema: {str(e)}")
            return False
    
    def load_data(self):
        """Cargar datos del sistema"""
        if self.brain:
            self.concepts = self.brain.generate_fresh_concepts(num_concepts=20)
            if self.brain.strategies:
                self.insights = self.brain.analyze_document_insights(self.brain.strategies)
                self.suggestions = self.brain.generate_actionable_marketing_suggestions(
                    self.insights, num_suggestions=15
                )
    
    def render_header(self):
        """Renderizar encabezado del dashboard"""
        st.set_page_config(
            page_title="Marketing Brain Dashboard",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🧠 Advanced Marketing Brain System")
            st.markdown("**Sistema de IA para Generación de Conceptos de Marketing**")
            st.markdown("*Inspirado en ClickUp Brain - Análisis de Documentos y Sugerencias Accionables*")
        
        with col2:
            if st.button("🔄 Regenerar Conceptos", type="primary"):
                self.load_data()
                st.rerun()
        
        with col3:
            if st.button("📊 Actualizar Dashboard"):
                st.rerun()
    
    def render_sidebar(self):
        """Renderizar barra lateral con controles"""
        st.sidebar.header("🎛️ Controles del Sistema")
        
        # Filtros
        st.sidebar.subheader("🔍 Filtros")
        
        # Filtro por tema
        if self.brain and self.brain.themes:
            themes = list(self.brain.themes.keys())
            selected_theme = st.sidebar.selectbox(
                "Tema Principal",
                ["Todos"] + themes,
                index=0
            )
        else:
            selected_theme = "Todos"
        
        # Filtro por probabilidad de éxito
        min_success = st.sidebar.slider(
            "Probabilidad Mínima de Éxito",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            format="%.1f"
        )
        
        # Filtro por complejidad
        complexity_options = ["Todas", "Baja", "Media", "Alta"]
        selected_complexity = st.sidebar.selectbox(
            "Complejidad",
            complexity_options,
            index=0
        )
        
        # Filtro por prioridad
        priority_options = ["Todas", "Baja", "Media", "Alta", "Crítica"]
        selected_priority = st.sidebar.selectbox(
            "Prioridad",
            priority_options,
            index=0
        )
        
        # Configuración de generación
        st.sidebar.subheader("⚙️ Configuración")
        
        num_concepts = st.sidebar.slider(
            "Número de Conceptos",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        target_vertical = st.sidebar.selectbox(
            "Vertical Objetivo",
            ["Todos", "E-commerce", "Fintech", "Healthcare", "Technology", "Fashion", "Education"],
            index=0
        )
        
        return {
            'theme': selected_theme,
            'min_success': min_success,
            'complexity': selected_complexity,
            'priority': selected_priority,
            'num_concepts': num_concepts,
            'target_vertical': target_vertical
        }
    
    def render_system_overview(self):
        """Renderizar resumen del sistema"""
        st.header("📊 Resumen del Sistema")
        
        if not self.brain:
            st.warning("Sistema no inicializado")
            return
        
        summary = self.brain.get_system_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Campañas Analizadas",
                value=summary['total_campaigns_analyzed'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Temas Extraídos",
                value=summary['themes_extracted'],
                delta=None
            )
        
        with col3:
            st.metric(
                label="Campañas de Alto Éxito",
                value=summary['high_success_campaigns'],
                delta=None
            )
        
        with col4:
            st.metric(
                label="Conceptos Generados",
                value=summary['concepts_generated'],
                delta=None
            )
        
        # Gráfico de temas principales
        if summary['top_themes']:
            st.subheader("🎯 Temas Principales")
            
            theme_data = []
            for theme in summary['top_themes']:
                if theme in self.brain.themes:
                    theme_obj = self.brain.themes[theme]
                    theme_data.append({
                        'Tema': theme,
                        'Frecuencia': theme_obj.frequency,
                        'Tasa de Éxito': theme_obj.success_rate,
                        'Score': theme_obj.frequency * theme_obj.success_rate
                    })
            
            if theme_data:
                df_themes = pd.DataFrame(theme_data)
                
                fig = px.bar(
                    df_themes,
                    x='Tema',
                    y='Score',
                    title="Score de Temas (Frecuencia × Tasa de Éxito)",
                    color='Tasa de Éxito',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_concepts_analysis(self, filters):
        """Renderizar análisis de conceptos"""
        st.header("🎨 Análisis de Conceptos Generados")
        
        if not self.concepts:
            st.warning("No hay conceptos generados")
            return
        
        # Aplicar filtros
        filtered_concepts = self._apply_filters(self.concepts, filters)
        
        if not filtered_concepts:
            st.warning("No hay conceptos que coincidan con los filtros")
            return
        
        st.success(f"Mostrando {len(filtered_concepts)} conceptos de {len(self.concepts)} totales")
        
        # Métricas de conceptos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_success = np.mean([c.success_probability for c in filtered_concepts])
            st.metric(
                label="Probabilidad Promedio de Éxito",
                value=f"{avg_success:.1%}",
                delta=None
            )
        
        with col2:
            avg_budget = np.mean([c.estimated_budget['amount'] for c in filtered_concepts])
            st.metric(
                label="Presupuesto Promedio",
                value=f"${avg_budget:,.0f}",
                delta=None
            )
        
        with col3:
            avg_duration = np.mean([c.timeline['duration_weeks'] for c in filtered_concepts])
            st.metric(
                label="Duración Promedio",
                value=f"{avg_duration:.1f} semanas",
                delta=None
            )
        
        with col4:
            high_priority = len([c for c in filtered_concepts if c.priority in ['Alta', 'Crítica']])
            st.metric(
                label="Alta Prioridad",
                value=high_priority,
                delta=None
            )
        
        # Gráficos de análisis
        self._render_concepts_charts(filtered_concepts)
        
        # Tabla de conceptos
        self._render_concepts_table(filtered_concepts)
    
    def _apply_filters(self, concepts, filters):
        """Aplicar filtros a los conceptos"""
        filtered = concepts.copy()
        
        # Filtro por tema
        if filters['theme'] != "Todos":
            filtered = [c for c in filtered if c.category == filters['theme']]
        
        # Filtro por probabilidad de éxito
        filtered = [c for c in filtered if c.success_probability >= filters['min_success']]
        
        # Filtro por complejidad
        if filters['complexity'] != "Todas":
            filtered = [c for c in filtered if c.complexity == filters['complexity']]
        
        # Filtro por prioridad
        if filters['priority'] != "Todas":
            filtered = [c for c in filtered if c.priority == filters['priority']]
        
        # Filtro por vertical
        if filters['target_vertical'] != "Todos":
            filtered = [c for c in filtered if c.vertical == filters['target_vertical']]
        
        return filtered
    
    def _render_concepts_charts(self, concepts):
        """Renderizar gráficos de conceptos"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por tecnología
            tech_counts = {}
            for concept in concepts:
                tech = concept.technology
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
            
            if tech_counts:
                fig_tech = px.pie(
                    values=list(tech_counts.values()),
                    names=list(tech_counts.keys()),
                    title="Distribución por Tecnología"
                )
                st.plotly_chart(fig_tech, use_container_width=True)
        
        with col2:
            # Distribución por canal
            channel_counts = {}
            for concept in concepts:
                channel = concept.channel
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
            
            if channel_counts:
                fig_channel = px.bar(
                    x=list(channel_counts.keys()),
                    y=list(channel_counts.values()),
                    title="Distribución por Canal"
                )
                st.plotly_chart(fig_channel, use_container_width=True)
        
        # Gráfico de probabilidad de éxito vs presupuesto
        st.subheader("📈 Análisis de Probabilidad de Éxito vs Presupuesto")
        
        concept_data = []
        for concept in concepts:
            concept_data.append({
                'Concepto': concept.name,
                'Probabilidad de Éxito': concept.success_probability,
                'Presupuesto': concept.estimated_budget['amount'],
                'Tecnología': concept.technology,
                'Canal': concept.channel,
                'Prioridad': concept.priority
            })
        
        if concept_data:
            df_concepts = pd.DataFrame(concept_data)
            
            fig_scatter = px.scatter(
                df_concepts,
                x='Presupuesto',
                y='Probabilidad de Éxito',
                color='Tecnología',
                size='Presupuesto',
                hover_data=['Concepto', 'Canal', 'Prioridad'],
                title="Probabilidad de Éxito vs Presupuesto por Tecnología"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    def _render_concepts_table(self, concepts):
        """Renderizar tabla de conceptos"""
        st.subheader("📋 Lista de Conceptos")
        
        # Preparar datos para la tabla
        table_data = []
        for concept in concepts:
            table_data.append({
                'ID': concept.concept_id,
                'Nombre': concept.name,
                'Categoría': concept.category,
                'Tecnología': concept.technology,
                'Canal': concept.channel,
                'Vertical': concept.vertical,
                'Prob. Éxito': f"{concept.success_probability:.1%}",
                'Complejidad': concept.complexity,
                'Prioridad': concept.priority,
                'Presupuesto': f"${concept.estimated_budget['amount']:,}",
                'Duración': f"{concept.timeline['duration_weeks']} sem"
            })
        
        if table_data:
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, use_container_width=True)
            
            # Botón de exportación
            if st.button("📥 Exportar Conceptos a CSV"):
                csv = df_table.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"marketing_concepts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    def render_suggestions_analysis(self):
        """Renderizar análisis de sugerencias"""
        st.header("💡 Análisis de Sugerencias Accionables")
        
        if not self.suggestions:
            st.warning("No hay sugerencias generadas")
            return
        
        st.success(f"Mostrando {len(self.suggestions)} sugerencias accionables")
        
        # Métricas de sugerencias
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            high_priority = len([s for s in self.suggestions if s['priority'] == 'Alta'])
            st.metric(
                label="Alta Prioridad",
                value=high_priority,
                delta=None
            )
        
        with col2:
            high_impact = len([s for s in self.suggestions if s['estimated_impact'] == 'Alto'])
            st.metric(
                label="Alto Impacto",
                value=high_impact,
                delta=None
            )
        
        with col3:
            quick_implementation = len([s for s in self.suggestions if '1-2' in s['implementation_time']])
            st.metric(
                label="Implementación Rápida",
                value=quick_implementation,
                delta=None
            )
        
        with col4:
            total_resources = sum([len(s['required_resources']) for s in self.suggestions])
            st.metric(
                label="Total Recursos",
                value=total_resources,
                delta=None
            )
        
        # Gráficos de sugerencias
        self._render_suggestions_charts()
        
        # Tabla de sugerencias
        self._render_suggestions_table()
    
    def _render_suggestions_charts(self):
        """Renderizar gráficos de sugerencias"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por prioridad
            priority_counts = {}
            for suggestion in self.suggestions:
                priority = suggestion['priority']
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if priority_counts:
                fig_priority = px.pie(
                    values=list(priority_counts.values()),
                    names=list(priority_counts.keys()),
                    title="Distribución por Prioridad"
                )
                st.plotly_chart(fig_priority, use_container_width=True)
        
        with col2:
            # Distribución por impacto
            impact_counts = {}
            for suggestion in self.suggestions:
                impact = suggestion['estimated_impact']
                impact_counts[impact] = impact_counts.get(impact, 0) + 1
            
            if impact_counts:
                fig_impact = px.bar(
                    x=list(impact_counts.keys()),
                    y=list(impact_counts.values()),
                    title="Distribución por Impacto Estimado"
                )
                st.plotly_chart(fig_impact, use_container_width=True)
        
        # Gráfico de tiempo de implementación
        st.subheader("⏱️ Análisis de Tiempo de Implementación")
        
        time_data = {}
        for suggestion in self.suggestions:
            time = suggestion['implementation_time']
            time_data[time] = time_data.get(time, 0) + 1
        
        if time_data:
            fig_time = px.bar(
                x=list(time_data.keys()),
                y=list(time_data.values()),
                title="Distribución por Tiempo de Implementación"
            )
            st.plotly_chart(fig_time, use_container_width=True)
    
    def _render_suggestions_table(self):
        """Renderizar tabla de sugerencias"""
        st.subheader("📋 Lista de Sugerencias")
        
        # Preparar datos para la tabla
        table_data = []
        for suggestion in self.suggestions:
            table_data.append({
                'ID': suggestion['id'],
                'Título': suggestion['title'],
                'Tipo': suggestion['action_type'],
                'Prioridad': suggestion['priority'],
                'Impacto': suggestion['estimated_impact'],
                'Tiempo': suggestion['implementation_time'],
                'Recursos': len(suggestion['required_resources']),
                'Métricas': len(suggestion['success_metrics'])
            })
        
        if table_data:
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, use_container_width=True)
            
            # Botón de exportación
            if st.button("📥 Exportar Sugerencias a CSV"):
                csv = df_table.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"marketing_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    def render_insights_analysis(self):
        """Renderizar análisis de insights"""
        st.header("🔍 Análisis de Insights del Documento")
        
        if not self.insights:
            st.warning("No hay insights disponibles")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Temas Clave")
            if self.insights.get('key_themes'):
                for i, theme in enumerate(self.insights['key_themes'][:10], 1):
                    st.write(f"{i}. {theme}")
            else:
                st.write("No se encontraron temas clave")
        
        with col2:
            st.subheader("📈 Temas Trending")
            if self.insights.get('trending_topics'):
                for i, topic in enumerate(self.insights['trending_topics'][:10], 1):
                    st.write(f"{i}. {topic}")
            else:
                st.write("No se encontraron temas trending")
        
        # Sugerencias accionables
        st.subheader("⚡ Sugerencias Accionables")
        if self.insights.get('actionable_suggestions'):
            for i, suggestion in enumerate(self.insights['actionable_suggestions'][:10], 1):
                st.write(f"{i}. {suggestion}")
        else:
            st.write("No se encontraron sugerencias accionables")
        
        # Oportunidades
        st.subheader("🚀 Oportunidades Identificadas")
        if self.insights.get('opportunities'):
            for i, opportunity in enumerate(self.insights['opportunities'][:5], 1):
                st.write(f"{i}. {opportunity}")
        else:
            st.write("No se identificaron oportunidades")
    
    def render_export_section(self):
        """Renderizar sección de exportación"""
        st.header("📤 Exportación de Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 Conceptos de Marketing")
            if self.concepts:
                if st.button("📄 Exportar Conceptos a JSON"):
                    filename = self.brain.export_concepts_to_json(self.concepts)
                    st.success(f"Conceptos exportados a: {filename}")
                
                if st.button("📊 Exportar Conceptos a CSV"):
                    concept_data = []
                    for concept in self.concepts:
                        concept_data.append({
                            'ID': concept.concept_id,
                            'Nombre': concept.name,
                            'Descripción': concept.description,
                            'Categoría': concept.category,
                            'Tecnología': concept.technology,
                            'Canal': concept.channel,
                            'Vertical': concept.vertical,
                            'Objetivo': concept.objective,
                            'Probabilidad de Éxito': concept.success_probability,
                            'Complejidad': concept.complexity,
                            'Prioridad': concept.priority,
                            'Presupuesto': concept.estimated_budget['amount'],
                            'Duración (semanas)': concept.timeline['duration_weeks'],
                            'Tags': ', '.join(concept.tags),
                            'Creado': concept.created_at
                        })
                    
                    df = pd.DataFrame(concept_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"marketing_concepts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("No hay conceptos para exportar")
        
        with col2:
            st.subheader("💡 Sugerencias Accionables")
            if self.suggestions:
                if st.button("📄 Exportar Sugerencias a JSON"):
                    filename = self.brain.export_suggestions_to_json(self.suggestions)
                    st.success(f"Sugerencias exportadas a: {filename}")
                
                if st.button("📊 Exportar Sugerencias a CSV"):
                    suggestion_data = []
                    for suggestion in self.suggestions:
                        suggestion_data.append({
                            'ID': suggestion['id'],
                            'Título': suggestion['title'],
                            'Descripción': suggestion['description'],
                            'Tipo': suggestion['action_type'],
                            'Prioridad': suggestion['priority'],
                            'Impacto': suggestion['estimated_impact'],
                            'Tiempo': suggestion['implementation_time'],
                            'Recursos': ', '.join(suggestion['required_resources']),
                            'Métricas': ', '.join(suggestion['success_metrics']),
                            'Creado': suggestion['created_at']
                        })
                    
                    df = pd.DataFrame(suggestion_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name=f"marketing_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.write("No hay sugerencias para exportar")
    
    def run(self):
        """Ejecutar el dashboard"""
        # Inicializar sistema
        if not self.brain:
            if not self.initialize_brain():
                return
        
        # Renderizar encabezado
        self.render_header()
        
        # Cargar datos si no están cargados
        if not self.concepts:
            with st.spinner("Cargando datos del sistema..."):
                self.load_data()
        
        # Renderizar barra lateral
        filters = self.render_sidebar()
        
        # Crear tabs para diferentes secciones
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Resumen", 
            "🎨 Conceptos", 
            "💡 Sugerencias", 
            "🔍 Insights", 
            "📤 Exportar"
        ])
        
        with tab1:
            self.render_system_overview()
        
        with tab2:
            self.render_concepts_analysis(filters)
        
        with tab3:
            self.render_suggestions_analysis()
        
        with tab4:
            self.render_insights_analysis()
        
        with tab5:
            self.render_export_section()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "🧠 **Advanced Marketing Brain System** - "
            "Sistema de IA para Generación de Conceptos de Marketing | "
            f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


def main():
    """Función principal para ejecutar el dashboard"""
    dashboard = MarketingBrainDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()








