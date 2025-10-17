#!/usr/bin/env python3
"""
HR DASHBOARD
============

Dashboard Interactivo de Recursos Humanos
Integrado con el Sistema de Planificación de Lanzamientos

Funcionalidades:
- Visualización de métricas de RRHH
- Seguimiento de capacitación
- Analytics de empleados
- Reportes de cumplimiento
- Predicciones de IA

Autor: Sistema de IA Avanzado
Versión: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
import os

# Agregar el directorio actual al path para importar el sistema de RRHH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hr_ai_training_system import HRAITrainingSystem
except ImportError:
    st.error("No se pudo importar el sistema de RRHH. Asegúrate de que hr_ai_training_system.py esté en el mismo directorio.")
    st.stop()

def initialize_hr_system():
    """Inicializar el sistema de RRHH"""
    if 'hr_system' not in st.session_state:
        st.session_state.hr_system = HRAITrainingSystem()
    return st.session_state.hr_system

def create_summary_cards(analytics):
    """Crear tarjetas de resumen"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Empleados",
            value=analytics['overview']['total_employees'],
            delta=f"+{random.randint(1, 5)} este mes"
        )
    
    with col2:
        st.metric(
            label="Tasa de Finalización",
            value=f"{analytics['training_effectiveness']['average_completion_rate']:.1%}",
            delta=f"+{random.randint(2, 8)}% vs mes anterior"
        )
    
    with col3:
        st.metric(
            label="Satisfacción",
            value=f"{analytics['training_effectiveness']['employee_satisfaction']:.1%}",
            delta=f"+{random.randint(1, 5)}% vs mes anterior"
        )
    
    with col4:
        st.metric(
            label="ROI Capacitación",
            value=f"{analytics['training_effectiveness']['roi_on_training']:.1f}x",
            delta=f"+{random.uniform(0.1, 0.5):.1f}x vs mes anterior"
        )

def create_department_chart(analytics):
    """Crear gráfico de distribución por departamento"""
    dept_data = analytics['department_breakdown']
    
    fig = px.pie(
        values=[dept_data[dept]['employee_count'] for dept in dept_data.keys()],
        names=list(dept_data.keys()),
        title="Distribución de Empleados por Departamento",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_skill_trends_chart():
    """Crear gráfico de tendencias de habilidades"""
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[random.randint(10, 20) for _ in months],
        mode='lines+markers',
        name='AI/ML Skills',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[random.randint(15, 25) for _ in months],
        mode='lines+markers',
        name='Data Analytics',
        line=dict(color='#ff7f0e', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[random.randint(8, 18) for _ in months],
        mode='lines+markers',
        name='Leadership',
        line=dict(color='#2ca02c', width=3)
    ))
    
    fig.update_layout(
        title="Tendencias de Habilidades por Mes",
        xaxis_title="Mes",
        yaxis_title="Número de Empleados",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_performance_distribution_chart(analytics):
    """Crear gráfico de distribución de rendimiento"""
    performance_data = analytics['skill_distribution']
    
    # Simular datos de distribución de rendimiento
    performance_levels = ['Excelente (9-10)', 'Bueno (7-8)', 'Promedio (5-6)', 'Bajo (<5)']
    performance_counts = [random.randint(15, 25), random.randint(30, 40), random.randint(10, 20), random.randint(2, 8)]
    
    fig = px.bar(
        x=performance_levels,
        y=performance_counts,
        title="Distribución de Rendimiento de Empleados",
        color=performance_counts,
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(
        xaxis_title="Nivel de Rendimiento",
        yaxis_title="Número de Empleados",
        height=400,
        showlegend=False
    )
    
    return fig

def create_training_effectiveness_chart(analytics):
    """Crear gráfico de efectividad de capacitación"""
    effectiveness = analytics['training_effectiveness']
    
    metrics = ['Tasa de Finalización', 'Mejora de Habilidades', 'Satisfacción', 'ROI']
    values = [
        effectiveness['average_completion_rate'] * 100,
        effectiveness['skill_improvement_rate'] * 100,
        effectiveness['employee_satisfaction'] * 100,
        effectiveness['roi_on_training'] * 20  # Escalar para visualización
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='Efectividad de Capacitación',
        line_color='rgb(32, 201, 151)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Efectividad de Capacitación",
        height=400
    )
    
    return fig

def display_employee_details(hr_system):
    """Mostrar detalles de empleados"""
    st.subheader("👥 Detalles de Empleados")
    
    # Crear DataFrame de empleados
    employees_data = []
    for emp_id, employee in hr_system.employees.items():
        employees_data.append({
            'ID': employee.id,
            'Nombre': employee.name,
            'Posición': employee.position,
            'Departamento': employee.department,
            'Experiencia (años)': employee.experience_years,
            'Rendimiento': employee.performance_score,
            'Habilidades': ', '.join(employee.skills),
            'Estilo de Aprendizaje': employee.learning_style
        })
    
    df = pd.DataFrame(employees_data)
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        departments = ['Todos'] + list(df['Departamento'].unique())
        selected_dept = st.selectbox("Filtrar por Departamento", departments)
    
    with col2:
        performance_threshold = st.slider("Rendimiento mínimo", 0.0, 10.0, 7.0)
    
    # Aplicar filtros
    filtered_df = df.copy()
    if selected_dept != 'Todos':
        filtered_df = filtered_df[filtered_df['Departamento'] == selected_dept]
    
    filtered_df = filtered_df[filtered_df['Rendimiento'] >= performance_threshold]
    
    # Mostrar tabla
    st.dataframe(filtered_df, use_container_width=True)
    
    # Estadísticas del filtro
    st.write(f"**Empleados mostrados:** {len(filtered_df)} de {len(df)}")

def display_training_modules(hr_system):
    """Mostrar módulos de capacitación"""
    st.subheader("📚 Módulos de Capacitación")
    
    # Crear DataFrame de módulos
    modules_data = []
    for mod_id, module in hr_system.training_modules.items():
        modules_data.append({
            'ID': module.id,
            'Título': module.title,
            'Categoría': module.category,
            'Dificultad': module.difficulty_level,
            'Duración (horas)': module.duration_hours,
            'Tasa de Finalización': f"{module.completion_rate:.1%}",
            'Efectividad': module.effectiveness_score,
            'Habilidades': ', '.join(module.skills_covered)
        })
    
    df = pd.DataFrame(modules_data)
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        categories = ['Todas'] + list(df['Categoría'].unique())
        selected_category = st.selectbox("Filtrar por Categoría", categories)
    
    with col2:
        difficulty_levels = ['Todas'] + list(df['Dificultad'].unique())
        selected_difficulty = st.selectbox("Filtrar por Dificultad", difficulty_levels)
    
    # Aplicar filtros
    filtered_df = df.copy()
    if selected_category != 'Todas':
        filtered_df = filtered_df[filtered_df['Categoría'] == selected_category]
    
    if selected_difficulty != 'Todas':
        filtered_df = filtered_df[filtered_df['Dificultad'] == selected_difficulty]
    
    # Mostrar tabla
    st.dataframe(filtered_df, use_container_width=True)

def display_ai_insights(hr_system):
    """Mostrar insights de IA"""
    st.subheader("🤖 Insights de IA")
    
    # Generar predicciones
    prediction = hr_system.predict_training_needs()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔮 Predicciones de Necesidades de Capacitación**")
        for need in prediction['predicted_needs'][:3]:
            st.write(f"• **{need['skill_category']}**: {need['demand_level']} demanda")
            st.write(f"  - Urgencia: {need['urgency']}")
            st.write(f"  - Empleados afectados: {need['affected_employees']}")
            st.write(f"  - Costo estimado: ${need['estimated_cost']:,}")
            st.write("")
    
    with col2:
        st.write("**📈 Tendencias de Habilidades**")
        st.write("**Habilidades Emergentes:**")
        for skill in prediction['skill_trends']['emerging_skills']:
            st.write(f"• {skill}")
        
        st.write("**Habilidades en Declive:**")
        for skill in prediction['skill_trends']['declining_skills']:
            st.write(f"• {skill}")
        
        st.write(f"**Confianza de IA:** {prediction['ai_confidence']:.1%}")

def display_compliance_status(hr_system):
    """Mostrar estado de cumplimiento"""
    st.subheader("📋 Estado de Cumplimiento")
    
    compliance = hr_system.create_compliance_report()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**✅ Cumplimiento de Capacitación**")
        for training_type, completion_rate in compliance['training_compliance'].items():
            st.write(f"• {training_type.replace('_', ' ').title()}: {completion_rate:.1%}")
        
        st.write("**📜 Estado de Certificaciones**")
        st.write(f"• Certificaciones válidas: {compliance['certification_status']['valid_certifications']}%")
        st.write(f"• Certificaciones expiradas: {compliance['certification_status']['expired_certifications']}")
        st.write(f"• Renovaciones próximas: {compliance['certification_status']['renewal_due_soon']}")
    
    with col2:
        st.write("**🎯 Preparación para Auditoría**")
        for audit_type, score in compliance['audit_readiness'].items():
            st.write(f"• {audit_type.replace('_', ' ').title()}: {score:.1%}")
        
        st.write("**⚠️ Evaluación de Riesgos**")
        st.write(f"• Áreas de alto riesgo: {len(compliance['risk_assessment']['high_risk_areas'])}")
        st.write(f"• Áreas de riesgo medio: {len(compliance['risk_assessment']['medium_risk_areas'])}")
        st.write(f"• Áreas de bajo riesgo: {len(compliance['risk_assessment']['low_risk_areas'])}")

def main():
    """Función principal del dashboard"""
    st.set_page_config(
        page_title="HR AI Dashboard",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal
    st.title("🎓 HR AI Training Dashboard")
    st.markdown("**Sistema de Capacitación de Recursos Humanos con IA**")
    
    # Inicializar sistema
    hr_system = initialize_hr_system()
    
    # Sidebar
    st.sidebar.title("🎛️ Controles")
    
    # Generar analytics
    analytics = hr_system.generate_hr_analytics()
    
    # Navegación
    page = st.sidebar.selectbox(
        "Seleccionar Página",
        ["📊 Dashboard Principal", "👥 Empleados", "📚 Capacitación", "🤖 IA Insights", "📋 Cumplimiento"]
    )
    
    if page == "📊 Dashboard Principal":
        st.header("📊 Dashboard Principal")
        
        # Tarjetas de resumen
        create_summary_cards(analytics)
        
        st.write("")  # Espacio
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_department_chart(analytics)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_performance_distribution_chart(analytics)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Gráficos de tendencias
        col3, col4 = st.columns(2)
        
        with col3:
            fig3 = create_skill_trends_chart()
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            fig4 = create_training_effectiveness_chart(analytics)
            st.plotly_chart(fig4, use_container_width=True)
    
    elif page == "👥 Empleados":
        display_employee_details(hr_system)
    
    elif page == "📚 Capacitación":
        display_training_modules(hr_system)
    
    elif page == "🤖 IA Insights":
        display_ai_insights(hr_system)
    
    elif page == "📋 Cumplimiento":
        display_compliance_status(hr_system)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sistema de IA Avanzado**")
    st.sidebar.markdown("Versión 1.0.0")
    st.sidebar.markdown(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    import random
    main()






