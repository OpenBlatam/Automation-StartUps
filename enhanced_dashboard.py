"""
Enhanced Launch Planning Dashboard
Dashboard web mejorado con IA, análisis predictivo y visualizaciones avanzadas
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Importar sistemas mejorados
from enhanced_launch_planner import EnhancedLaunchPlanner, AIPrediction, MarketAnalysis, PerformanceMetrics
from launch_planning_checklist import LaunchPlanningChecklist
from clickup_brain_integration import ClickUpBrainBehavior

# Configuración de la página
st.set_page_config(
    page_title="Enhanced Launch Planning System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .success-metric {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .warning-metric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .info-metric {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .ai-insight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem 0;
    }
    
    .recommendation-card {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    .risk-card {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializar variables de sesión"""
    if 'enhanced_planner' not in st.session_state:
        st.session_state.enhanced_planner = EnhancedLaunchPlanner()
    
    if 'checklist' not in st.session_state:
        st.session_state.checklist = LaunchPlanningChecklist()
        st.session_state.checklist.load_default_template()
    
    if 'brain' not in st.session_state:
        st.session_state.brain = ClickUpBrainBehavior()
    
    if 'enhanced_plan' not in st.session_state:
        st.session_state.enhanced_plan = None
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

def display_enhanced_header():
    """Mostrar header mejorado"""
    st.markdown('<h1 class="main-header">🚀 Enhanced Launch Planning System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.3rem; color: #666; font-weight: 500;">
            Sistema de planificación de lanzamientos con IA avanzada, análisis predictivo y optimización inteligente
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
            <span style="color: #1f77b4; font-weight: bold;">🧠 IA Avanzada</span>
            <span style="color: #ff7f0e; font-weight: bold;">📊 Análisis Predictivo</span>
            <span style="color: #2ca02c; font-weight: bold;">🎯 Optimización Inteligente</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_ai_insights_overview():
    """Mostrar resumen de insights de IA"""
    if st.session_state.enhanced_plan:
        ai_insights = st.session_state.enhanced_plan["ai_insights"]
        
        st.subheader("🧠 AI Insights & Predictions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            success_prob = ai_insights['success_probability']
            color = "success" if success_prob > 0.7 else "warning" if success_prob > 0.5 else "danger"
            st.markdown(f"""
            <div class="metric-card {color}-metric">
                <h3 style="margin: 0; font-size: 2rem;">{success_prob:.1%}</h3>
                <p style="margin: 0; opacity: 0.9;">Probabilidad de Éxito</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            confidence = ai_insights['confidence_score']
            st.markdown(f"""
            <div class="metric-card info-metric">
                <h3 style="margin: 0; font-size: 2rem;">{confidence:.1%}</h3>
                <p style="margin: 0; opacity: 0.9;">Confianza del Modelo</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            timeline = ai_insights['optimized_timeline']
            st.markdown(f"""
            <div class="metric-card info-metric">
                <h3 style="margin: 0; font-size: 1.5rem;">{timeline}</h3>
                <p style="margin: 0; opacity: 0.9;">Timeline Optimizado</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_budget = sum(ai_insights['budget_optimization'].values())
            st.markdown(f"""
            <div class="metric-card info-metric">
                <h3 style="margin: 0; font-size: 1.5rem;">${total_budget:,.0f}</h3>
                <p style="margin: 0; opacity: 0.9;">Presupuesto Total</p>
            </div>
            """, unsafe_allow_html=True)

def display_performance_metrics():
    """Mostrar métricas de rendimiento"""
    if st.session_state.enhanced_plan:
        performance = st.session_state.enhanced_plan["ai_insights"]["performance_metrics"]
        
        st.subheader("📈 Performance Metrics")
        
        # Crear gráfico de radar para métricas de rendimiento
        categories = ['Velocidad', 'Calidad', 'Eficiencia', 'Recursos', 'Timeline']
        values = [
            performance['velocity'],
            performance['quality_score'],
            performance['team_efficiency'],
            performance['resource_utilization'],
            performance['timeline_adherence']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Rendimiento Actual',
            line_color='rgb(31, 119, 180)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Métricas de Rendimiento del Proyecto",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar métricas individuales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics_data = [
            ("Velocidad", performance['velocity'], "🚀"),
            ("Calidad", performance['quality_score'], "⭐"),
            ("Eficiencia", performance['team_efficiency'], "👥"),
            ("Recursos", performance['resource_utilization'], "💰"),
            ("Timeline", performance['timeline_adherence'], "⏱️")
        ]
        
        for i, (name, value, icon) in enumerate(metrics_data):
            with [col1, col2, col3, col4, col5][i]:
                st.metric(
                    label=f"{icon} {name}",
                    value=f"{value:.1%}",
                    delta=None
                )

def display_budget_optimization():
    """Mostrar optimización de presupuesto"""
    if st.session_state.enhanced_plan:
        budget_data = st.session_state.enhanced_plan["ai_insights"]["budget_optimization"]
        
        st.subheader("💰 Budget Optimization")
        
        # Crear gráfico de dona para distribución del presupuesto
        fig = px.pie(
            values=list(budget_data.values()),
            names=list(budget_data.keys()),
            title="Distribución Optimizada del Presupuesto",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar detalles del presupuesto
        budget_df = pd.DataFrame([
            {"Category": category.title(), "Amount": amount, "Percentage": (amount/sum(budget_data.values()))*100}
            for category, amount in budget_data.items()
        ])
        
        st.dataframe(
            budget_df,
            use_container_width=True,
            hide_index=True
        )

def display_market_analysis():
    """Mostrar análisis de mercado"""
    if st.session_state.enhanced_plan:
        market_data = st.session_state.enhanced_plan["market_intelligence"]["market_analysis"]
        
        st.subheader("📊 Market Intelligence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Información del mercado
            st.markdown("### Market Overview")
            st.info(f"**Market Size**: ${market_data['market_size']:,.0f}")
            st.info(f"**Competition Level**: {market_data['competition_level'].title()}")
            st.info(f"**Market Timing**: {market_data['market_timing']}")
            
            # Audiencia objetivo
            st.markdown("### Target Audience")
            audience = market_data['target_audience']
            st.write(f"**Primary**: {audience['primary']}")
            st.write(f"**Secondary**: {audience['secondary']}")
            st.write(f"**Geographic**: {audience['geographic']}")
            st.write(f"**Behavior**: {audience['behavior']}")
        
        with col2:
            # Tendencias del mercado
            st.markdown("### Market Trends")
            for trend in market_data['market_trends']:
                st.markdown(f"• {trend}")
            
            # Oportunidades
            st.markdown("### Opportunities")
            for opportunity in market_data['opportunities']:
                st.markdown(f"• {opportunity}")
            
            # Amenazas
            st.markdown("### Threats")
            for threat in market_data['threats']:
                st.markdown(f"• {threat}")

def display_smart_recommendations():
    """Mostrar recomendaciones inteligentes"""
    if st.session_state.enhanced_plan:
        recommendations = st.session_state.enhanced_plan["ai_insights"]["smart_recommendations"]
        
        st.subheader("🎯 Smart Recommendations")
        
        # Agrupar recomendaciones por categoría
        categories = {
            "Strategy": [],
            "Technical": [],
            "Marketing": [],
            "Risk Management": [],
            "Team": []
        }
        
        # Clasificar recomendaciones (simplificado)
        for rec in recommendations:
            if any(word in rec.lower() for word in ["strategy", "market", "business"]):
                categories["Strategy"].append(rec)
            elif any(word in rec.lower() for word in ["technical", "development", "code", "system"]):
                categories["Technical"].append(rec)
            elif any(word in rec.lower() for word in ["marketing", "brand", "promotion", "campaign"]):
                categories["Marketing"].append(rec)
            elif any(word in rec.lower() for word in ["risk", "security", "backup", "contingency"]):
                categories["Risk Management"].append(rec)
            elif any(word in rec.lower() for word in ["team", "hire", "staff", "developer"]):
                categories["Team"].append(rec)
            else:
                categories["Strategy"].append(rec)
        
        # Mostrar recomendaciones por categoría
        for category, recs in categories.items():
            if recs:
                with st.expander(f"📋 {category} ({len(recs)} recommendations)"):
                    for i, rec in enumerate(recs, 1):
                        st.markdown(f"""
                        <div class="recommendation-card">
                            <strong>{i}.</strong> {rec}
                        </div>
                        """, unsafe_allow_html=True)

def display_risk_assessment():
    """Mostrar evaluación de riesgos"""
    if st.session_state.enhanced_plan:
        risks = st.session_state.enhanced_plan["enhanced_analysis"]["ai_predictions"].risk_factors
        
        st.subheader("⚠️ Risk Assessment")
        
        # Clasificar riesgos por severidad
        high_risks = []
        medium_risks = []
        low_risks = []
        
        for risk in risks:
            if any(word in risk.lower() for word in ["high", "critical", "major", "severe"]):
                high_risks.append(risk)
            elif any(word in risk.lower() for word in ["medium", "moderate", "potential"]):
                medium_risks.append(risk)
            else:
                low_risks.append(risk)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔴 High Risk")
            for risk in high_risks:
                st.markdown(f"""
                <div class="risk-card" style="border-left-color: #dc3545;">
                    {risk}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🟡 Medium Risk")
            for risk in medium_risks:
                st.markdown(f"""
                <div class="risk-card" style="border-left-color: #ffc107;">
                    {risk}
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("### 🟢 Low Risk")
            for risk in low_risks:
                st.markdown(f"""
                <div class="risk-card" style="border-left-color: #28a745;">
                    {risk}
                </div>
                """, unsafe_allow_html=True)

def display_enhanced_planner_interface():
    """Mostrar interfaz del planificador mejorado"""
    st.subheader("🎯 Enhanced Launch Planner")
    
    # Selección de escenario
    scenario_type = st.selectbox(
        "Select Launch Scenario",
        ["mobile_app", "saas_platform", "ecommerce", "content_launch"],
        format_func=lambda x: {
            "mobile_app": "📱 Mobile App Launch",
            "saas_platform": "☁️ SaaS Platform Launch", 
            "ecommerce": "🛒 E-commerce Launch",
            "content_launch": "📝 Content/Media Launch"
        }[x]
    )
    
    # Input de requisitos mejorado
    st.markdown("### 📝 Launch Requirements")
    requirements = st.text_area(
        "Describe your launch requirements in detail:",
        placeholder="""Example: Launch a SaaS platform for project management with AI features.
Target: 10,000 paying customers in first year.
Budget: $200,000 for development and marketing.
Need 8 developers, 2 designers, 1 AI specialist.
Must integrate with Slack, Microsoft Teams, and payment systems.
Launch deadline: Q3 2024.
Priority: High for security, scalability, and user experience.""",
        height=150,
        help="Be as specific as possible for better AI analysis and predictions."
    )
    
    # Opciones avanzadas
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_market_analysis = st.checkbox("Include Market Analysis", value=True)
            include_risk_assessment = st.checkbox("Include Risk Assessment", value=True)
        
        with col2:
            include_budget_optimization = st.checkbox("Include Budget Optimization", value=True)
            include_performance_metrics = st.checkbox("Include Performance Metrics", value=True)
    
    # Botón para crear plan
    if st.button("🚀 Create Enhanced Launch Plan", type="primary", use_container_width=True):
        if requirements:
            with st.spinner("🧠 Analyzing requirements with advanced AI..."):
                try:
                    # Crear plan mejorado
                    enhanced_plan = st.session_state.enhanced_planner.create_enhanced_launch_plan(
                        requirements, scenario_type
                    )
                    st.session_state.enhanced_plan = enhanced_plan
                    
                    # Agregar a historial
                    st.session_state.analysis_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "scenario": scenario_type,
                        "requirements": requirements[:100] + "...",
                        "success_probability": enhanced_plan["ai_insights"]["success_probability"]
                    })
                    
                    st.success("✅ Enhanced launch plan created successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creating plan: {str(e)}")
        else:
            st.warning("⚠️ Please enter launch requirements first.")

def display_analysis_history():
    """Mostrar historial de análisis"""
    if st.session_state.analysis_history:
        st.subheader("📚 Analysis History")
        
        history_df = pd.DataFrame(st.session_state.analysis_history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df = history_df.sort_values('timestamp', ascending=False)
        
        # Mostrar tabla
        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Gráfico de probabilidad de éxito a lo largo del tiempo
        if len(history_df) > 1:
            fig = px.line(
                history_df,
                x='timestamp',
                y='success_probability',
                title='Success Probability Over Time',
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Success Probability",
                yaxis=dict(tickformat='.1%')
            )
            st.plotly_chart(fig, use_container_width=True)

def display_sidebar():
    """Mostrar sidebar de navegación"""
    st.sidebar.title("🚀 Navigation")
    
    page = st.sidebar.selectbox(
        "Select Page",
        [
            "🏠 Dashboard Overview",
            "🎯 Enhanced Planner",
            "📊 AI Insights",
            "💰 Budget Analysis",
            "📈 Performance Metrics",
            "📊 Market Intelligence",
            "🎯 Smart Recommendations",
            "⚠️ Risk Assessment",
            "📚 Analysis History"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.sidebar.button("📥 Export Plan"):
        if st.session_state.enhanced_plan:
            plan_json = json.dumps(st.session_state.enhanced_plan, indent=2, default=str)
            st.sidebar.download_button(
                label="Download Enhanced Plan",
                data=plan_json,
                file_name=f"enhanced_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.sidebar.warning("No plan available")
    
    st.sidebar.markdown("---")
    
    # System info
    st.sidebar.subheader("ℹ️ System Info")
    st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.session_state.enhanced_plan:
        ai_insights = st.session_state.enhanced_plan["ai_insights"]
        st.sidebar.metric("Success Probability", f"{ai_insights['success_probability']:.1%}")
        st.sidebar.metric("Confidence Score", f"{ai_insights['confidence_score']:.1%}")
    
    return page

def main():
    """Aplicación principal del dashboard mejorado"""
    initialize_session_state()
    display_enhanced_header()
    
    # Navegación sidebar
    page = display_sidebar()
    
    # Contenido principal basado en la página seleccionada
    if page == "🏠 Dashboard Overview":
        if st.session_state.enhanced_plan:
            display_ai_insights_overview()
            st.markdown("---")
            display_performance_metrics()
            st.markdown("---")
            display_budget_optimization()
        else:
            st.info("👆 Please create an enhanced launch plan first using the Enhanced Planner page.")
    
    elif page == "🎯 Enhanced Planner":
        display_enhanced_planner_interface()
    
    elif page == "📊 AI Insights":
        if st.session_state.enhanced_plan:
            display_ai_insights_overview()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "💰 Budget Analysis":
        if st.session_state.enhanced_plan:
            display_budget_optimization()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "📈 Performance Metrics":
        if st.session_state.enhanced_plan:
            display_performance_metrics()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "📊 Market Intelligence":
        if st.session_state.enhanced_plan:
            display_market_analysis()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "🎯 Smart Recommendations":
        if st.session_state.enhanced_plan:
            display_smart_recommendations()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "⚠️ Risk Assessment":
        if st.session_state.enhanced_plan:
            display_risk_assessment()
        else:
            st.info("Please create an enhanced launch plan first.")
    
    elif page == "📚 Analysis History":
        display_analysis_history()

if __name__ == "__main__":
    main()








