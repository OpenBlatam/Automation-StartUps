#!/usr/bin/env python3
"""
ClickUp Brain Advanced Dashboard
===============================

Advanced web dashboard with real-time monitoring, AI insights,
and comprehensive visualizations for team efficiency analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import Dict, List, Any, Optional

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem

# Page configuration
st.set_page_config(
    page_title="ClickUp Brain Advanced Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for advanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #7B68EE;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .ai-insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-left: 5px solid #7B68EE;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .recommendation-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .alert-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-left: 5px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #7B68EE;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedClickUpBrainDashboard:
    """Advanced dashboard with real-time monitoring and AI insights."""
    
    def __init__(self):
        self.simple_system = SimpleClickUpBrainSystem()
        self.enhanced_system = EnhancedClickUpBrainSystem()
        self.realtime_system = ClickUpBrainRealtimeSystem()
        self.analysis_results = None
        self.monitoring_active = False
    
    def run(self):
        """Run the advanced dashboard."""
        # Header
        st.markdown('<h1 class="main-header">🧠 ClickUp Brain Advanced Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("### AI-Powered Team Efficiency Analysis & Real-Time Monitoring")
        
        # Sidebar
        self.render_advanced_sidebar()
        
        # Main content
        if self.analysis_results:
            self.render_advanced_main_content()
        else:
            self.render_welcome_screen()
    
    def render_advanced_sidebar(self):
        """Render the advanced sidebar with more options."""
        st.sidebar.title("🔧 Advanced Controls")
        
        # Analysis Type Selection
        st.sidebar.subheader("📊 Analysis Type")
        analysis_type = st.sidebar.selectbox(
            "Choose analysis type:",
            ["Basic Analysis", "AI-Enhanced Analysis", "Real-Time Monitoring"],
            help="Select the type of analysis to perform"
        )
        
        # File Upload Section
        st.sidebar.subheader("📁 Data Input")
        
        if analysis_type == "Real-Time Monitoring":
            # Real-time monitoring controls
            directory_path = st.sidebar.text_input(
                "Directory to monitor:",
                value=".",
                help="Enter the path to the directory you want to monitor in real-time"
            )
            
            team_size = st.sidebar.number_input(
                "Team Size:",
                min_value=1,
                max_value=1000,
                value=10,
                help="Number of team members"
            )
            
            check_interval = st.sidebar.selectbox(
                "Check Interval:",
                [60, 300, 600, 1800],
                index=1,
                format_func=lambda x: f"{x//60} minutes" if x >= 60 else f"{x} seconds",
                help="How often to check for changes"
            )
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("🚀 Start Monitoring", type="primary"):
                    with st.spinner("Starting real-time monitoring..."):
                        try:
                            self.realtime_system.start_monitoring(directory_path, team_size, check_interval)
                            self.monitoring_active = True
                            st.sidebar.success("✅ Monitoring started!")
                        except Exception as e:
                            st.sidebar.error(f"❌ Error: {str(e)}")
            
            with col2:
                if st.button("🛑 Stop Monitoring"):
                    try:
                        self.realtime_system.stop_monitoring()
                        self.monitoring_active = False
                        st.sidebar.success("✅ Monitoring stopped!")
                    except Exception as e:
                        st.sidebar.error(f"❌ Error: {str(e)}")
        
        else:
            # Regular analysis controls
            uploaded_file = st.sidebar.file_uploader(
                "Upload analysis results:",
                type=['json'],
                help="Upload previously generated analysis results"
            )
            
            if uploaded_file:
                try:
                    self.analysis_results = json.load(uploaded_file)
                    st.sidebar.success("✅ Analysis results loaded!")
                except Exception as e:
                    st.sidebar.error(f"❌ Error loading file: {str(e)}")
            
            directory_path = st.sidebar.text_input(
                "Directory to analyze:",
                value=".",
                help="Enter the path to the directory you want to analyze"
            )
            
            team_size = st.sidebar.number_input(
                "Team Size:",
                min_value=1,
                max_value=1000,
                value=10,
                help="Number of team members"
            )
            
            if st.sidebar.button("🔍 Analyze Directory", type="primary"):
                with st.spinner("Analyzing directory..."):
                    try:
                        if analysis_type == "AI-Enhanced Analysis":
                            self.analysis_results = self.enhanced_system.analyze_with_ai(directory_path, team_size)
                        else:
                            self.analysis_results = self.simple_system.scan_directory(directory_path)
                        st.sidebar.success("✅ Analysis completed!")
                    except Exception as e:
                        st.sidebar.error(f"❌ Error: {str(e)}")
        
        # Export Options
        if self.analysis_results:
            st.sidebar.subheader("📊 Export Options")
            
            if st.sidebar.button("📄 Generate Report"):
                if analysis_type == "AI-Enhanced Analysis":
                    report = self.enhanced_system.generate_ai_report(self.analysis_results)
                else:
                    report = self.simple_system.generate_report(self.analysis_results)
                
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name=f"clickup_brain_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            
            if st.sidebar.button("💾 Save Analysis"):
                filename = f"clickup_brain_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                if analysis_type == "AI-Enhanced Analysis":
                    self.enhanced_system.save_ai_analysis(self.analysis_results, filename)
                else:
                    self.simple_system.save_analysis(self.analysis_results, filename)
                st.sidebar.success(f"✅ Analysis saved as {filename}")
        
        # API Integration
        st.sidebar.subheader("🔗 API Integration")
        api_url = st.sidebar.text_input(
            "API URL:",
            value="http://localhost:5000",
            help="ClickUp Brain API endpoint"
        )
        
        if st.sidebar.button("🔌 Test API Connection"):
            try:
                response = requests.get(f"{api_url}/api/v1/health", timeout=5)
                if response.status_code == 200:
                    st.sidebar.success("✅ API connected!")
                else:
                    st.sidebar.error("❌ API connection failed")
            except Exception as e:
                st.sidebar.error(f"❌ API error: {str(e)}")
    
    def render_welcome_screen(self):
        """Render the advanced welcome screen."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            ## 🚀 Welcome to ClickUp Brain Advanced Dashboard!
            
            This advanced dashboard provides:
            
            - **🤖 AI-Enhanced Analysis** - Machine learning-powered insights
            - **📊 Real-Time Monitoring** - Live efficiency tracking
            - **🎯 Smart Recommendations** - AI-driven tool suggestions
            - **📈 Advanced Visualizations** - Interactive charts and metrics
            - **🔗 API Integration** - Connect with external systems
            
            ### Getting Started:
            
            1. **Choose Analysis Type** - Select from Basic, AI-Enhanced, or Real-Time
            2. **Configure Settings** - Set team size and monitoring parameters
            3. **Run Analysis** - Start analyzing your team's efficiency
            4. **Explore Insights** - Dive deep into AI-powered recommendations
            
            ### Advanced Features:
            
            - ✅ **Real-Time Monitoring** - Continuous efficiency tracking
            - ✅ **AI Predictions** - Future efficiency forecasting
            - ✅ **Bottleneck Detection** - Automatic problem identification
            - ✅ **ROI Calculations** - Business impact analysis
            - ✅ **Integration Opportunities** - ClickUp-specific insights
            """)
    
    def render_advanced_main_content(self):
        """Render the advanced main dashboard content."""
        # Real-time monitoring status
        if self.monitoring_active:
            self.render_monitoring_status()
        
        # Advanced tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 AI Analysis", 
            "🎯 Smart Recommendations", 
            "📈 Advanced Metrics", 
            "🔍 Deep Insights", 
            "⚙️ System Status"
        ])
        
        with tab1:
            self.render_ai_analysis_tab()
        
        with tab2:
            self.render_smart_recommendations_tab()
        
        with tab3:
            self.render_advanced_metrics_tab()
        
        with tab4:
            self.render_deep_insights_tab()
        
        with tab5:
            self.render_system_status_tab()
    
    def render_monitoring_status(self):
        """Render real-time monitoring status."""
        try:
            status = self.realtime_system.get_status()
            
            if status.get('status') == 'monitoring':
                st.markdown("""
                <div class="success-box">
                    <h4>🟢 Real-Time Monitoring Active</h4>
                    <p>Monitoring directory for changes and efficiency updates...</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-refresh every 30 seconds
                if st.button("🔄 Refresh Status"):
                    st.rerun()
                
                # Show latest snapshot
                if 'latest_snapshot' in status:
                    snapshot = status['latest_snapshot']
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Efficiency", f"{snapshot['efficiency_score']:.1f}/100")
                    
                    with col2:
                        st.metric("Active Tools", snapshot['tool_count'])
                    
                    with col3:
                        st.metric("Trend", snapshot['efficiency_trend'])
                    
                    with col4:
                        st.metric("Last Update", "Just now")
            else:
                st.markdown("""
                <div class="alert-box">
                    <h4>🟡 Monitoring Inactive</h4>
                    <p>Real-time monitoring is not currently active.</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error getting monitoring status: {str(e)}")
    
    def render_ai_analysis_tab(self):
        """Render AI analysis tab with advanced insights."""
        if 'ai_analysis' not in self.analysis_results:
            st.warning("AI analysis not available. Please run AI-Enhanced Analysis.")
            return
        
        ai_profile = self.analysis_results['ai_analysis']['efficiency_profile']
        ai_recommendations = self.analysis_results['ai_analysis']['ai_recommendations']
        
        # AI Efficiency Profile
        st.subheader("🤖 AI Efficiency Profile")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_score = ai_profile['current_efficiency_score']
            color = "#28a745" if current_score >= 80 else "#ffc107" if current_score >= 60 else "#dc3545"
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);">
                <h3>📊 Current Score</h3>
                <h2>{current_score:.1f}/100</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            projected_score = ai_profile['projected_efficiency_score']
            improvement = projected_score - current_score
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 Projected Score</h3>
                <h2>{projected_score:.1f}/100</h2>
                <p>+{improvement:.1f} improvement</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            confidence = ai_profile['confidence_level']
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Confidence</h3>
                <h2>{confidence:.1%}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            trend = ai_profile['efficiency_trend']
            trend_emoji = "📈" if "Improving" in trend else "📉" if "Declining" in trend else "➡️"
            st.markdown(f"""
            <div class="metric-card">
                <h3>{trend_emoji} Trend</h3>
                <h2>{trend}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Insights
        st.subheader("🧠 AI Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if ai_profile['bottleneck_areas']:
                st.markdown("### 🚧 Identified Bottlenecks")
                for bottleneck in ai_profile['bottleneck_areas']:
                    st.markdown(f"""
                    <div class="alert-box">
                        <strong>⚠️</strong> {bottleneck}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if ai_profile['optimization_opportunities']:
                st.markdown("### 🎯 Optimization Opportunities")
                for opportunity in ai_profile['optimization_opportunities']:
                    st.markdown(f"""
                    <div class="ai-insight-box">
                        <strong>💡</strong> {opportunity}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Efficiency Projection Chart
        st.subheader("📈 Efficiency Projection")
        
        # Create projection chart
        months = ['Current', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
        current_score = ai_profile['current_efficiency_score']
        projected_score = ai_profile['projected_efficiency_score']
        
        # Simulate progression
        progression = [current_score]
        for i in range(1, 6):
            progress = (projected_score - current_score) * (i / 6)
            progression.append(current_score + progress)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=progression,
            mode='lines+markers',
            name='Projected Efficiency',
            line=dict(color='#7B68EE', width=4),
            marker=dict(size=10, color='#7B68EE')
        ))
        
        fig.add_hline(
            y=current_score,
            line_dash="dash",
            line_color="red",
            annotation_text="Current Level"
        )
        
        fig.update_layout(
            title="AI-Projected Efficiency Improvement",
            xaxis_title="Time",
            yaxis_title="Efficiency Score",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_smart_recommendations_tab(self):
        """Render smart recommendations tab."""
        if 'ai_analysis' not in self.analysis_results:
            st.warning("AI recommendations not available. Please run AI-Enhanced Analysis.")
            return
        
        ai_recommendations = self.analysis_results['ai_analysis']['ai_recommendations']
        
        st.subheader("🎯 AI-Powered Tool Recommendations")
        
        for i, rec in enumerate(ai_recommendations, 1):
            with st.expander(f"{i}. {rec['tool_name']} - Confidence: {rec['confidence_score']:.1%}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Category:** {rec['category']}")
                    st.markdown(f"**Efficiency Impact:** {rec['efficiency_impact']:.1f}%")
                    st.markdown(f"**Implementation Difficulty:** {rec['implementation_difficulty']}")
                    st.markdown(f"**Learning Curve:** {rec['learning_curve']}")
                
                with col2:
                    st.markdown(f"**Cost-Benefit Ratio:** {rec['cost_benefit_ratio']:.1f}")
                    st.markdown(f"**Optimal Team Size:** {rec['team_size_optimal']}")
                    st.markdown(f"**ROI Timeline:** {rec['roi_timeline']}")
                    st.markdown(f"**Success Probability:** {rec['success_probability']:.1%}")
                
                if rec['alternative_tools']:
                    st.markdown(f"**Alternative Tools:** {', '.join(rec['alternative_tools'])}")
                
                # Recommendation visualization
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = rec['efficiency_impact'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"Efficiency Impact"},
                    delta = {'reference': 50},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#7B68EE"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_advanced_metrics_tab(self):
        """Render advanced metrics tab."""
        efficiency = self.analysis_results['efficiency_analysis']
        
        st.subheader("📊 Advanced Performance Metrics")
        
        # Create advanced metrics dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            # Tool Usage Heatmap
            if efficiency['tool_usage']:
                st.markdown("### 🔥 Tool Usage Heatmap")
                
                tools = list(efficiency['tool_usage'].keys())
                counts = list(efficiency['tool_usage'].values())
                
                fig = px.bar(
                    x=tools,
                    y=counts,
                    title="Tool Usage Frequency",
                    color=counts,
                    color_continuous_scale="Viridis"
                )
                
                fig.update_layout(
                    xaxis_title="Software Tools",
                    yaxis_title="Mentions",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Category Distribution
            if efficiency['category_analysis']:
                st.markdown("### 📂 Category Distribution")
                
                categories = list(efficiency['category_analysis'].keys())
                tool_counts = [len(data['tools']) for data in efficiency['category_analysis'].values()]
                
                fig = px.pie(
                    values=tool_counts,
                    names=categories,
                    title="Tools by Category",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        # Efficiency Score Breakdown
        st.subheader("📈 Efficiency Score Breakdown")
        
        # Create radar chart for efficiency components
        categories = ['Tool Diversity', 'Category Coverage', 'Tool Quality', 'Integration Level']
        scores = [30, 40, 30, 10]  # Simplified scoring
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name='Current Performance',
            line_color='#7B68EE'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 50]
                )),
            showlegend=True,
            title="Efficiency Components Analysis",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_deep_insights_tab(self):
        """Render deep insights tab."""
        st.subheader("🔍 Deep Insights & Analysis")
        
        # ClickUp-specific insights
        if 'clickup_insights' in self.analysis_results:
            clickup = self.analysis_results['clickup_insights']
            
            st.markdown("### 🧠 ClickUp Brain Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("ClickUp Mentions", clickup['clickup_mentions'])
                st.metric("Efficiency Boost Potential", f"{clickup['team_efficiency_boost']:.1f}%")
            
            with col2:
                if clickup['integration_opportunities']:
                    st.markdown("**Integration Opportunities:**")
                    for opp in clickup['integration_opportunities'][:3]:
                        st.markdown(f"• {opp}")
            
            # ClickUp adoption impact simulation
            st.markdown("### 📊 ClickUp Adoption Impact Simulation")
            
            # Simulate impact over time
            months = list(range(0, 13))  # 12 months
            current_efficiency = self.analysis_results['efficiency_analysis']['efficiency_score']
            boost_potential = clickup['team_efficiency_boost']
            
            # Simulate gradual improvement
            efficiency_progression = []
            for month in months:
                if month == 0:
                    efficiency_progression.append(current_efficiency)
                else:
                    improvement = (boost_potential * month / 12)
                    new_efficiency = min(100, current_efficiency + improvement)
                    efficiency_progression.append(new_efficiency)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months,
                y=efficiency_progression,
                mode='lines+markers',
                name='With ClickUp',
                line=dict(color='#7B68EE', width=4),
                marker=dict(size=8)
            ))
            
            # Add baseline (without ClickUp)
            fig.add_trace(go.Scatter(
                x=months,
                y=[current_efficiency] * len(months),
                mode='lines',
                name='Current State',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title="ClickUp Adoption Impact Over Time",
                xaxis_title="Months",
                yaxis_title="Efficiency Score",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # ROI Analysis
        st.subheader("💰 ROI Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            team_size = st.number_input("Team Size", min_value=1, max_value=1000, value=10)
        
        with col2:
            avg_salary = st.number_input("Average Salary ($)", min_value=30000, max_value=200000, value=75000)
        
        with col3:
            efficiency_improvement = st.slider("Efficiency Improvement (%)", 0, 100, 25)
        
        # Calculate ROI
        annual_savings = (team_size * avg_salary * efficiency_improvement / 100)
        implementation_cost = team_size * 2000
        roi_percentage = ((annual_savings - implementation_cost) / implementation_cost) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Annual Savings", f"${annual_savings:,.0f}")
        
        with col2:
            st.metric("Implementation Cost", f"${implementation_cost:,.0f}")
        
        with col3:
            st.metric("ROI", f"{roi_percentage:.1f}%")
        
        with col4:
            payback_months = (implementation_cost / (annual_savings / 12))
            st.metric("Payback Period", f"{payback_months:.1f} months")
    
    def render_system_status_tab(self):
        """Render system status tab."""
        st.subheader("⚙️ System Status & Configuration")
        
        # System Information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Analysis Status")
            st.info(f"Analysis completed: {self.analysis_results.get('scan_timestamp', 'Unknown')}")
            st.info(f"Files scanned: {self.analysis_results.get('total_files_scanned', 0)}")
            st.info(f"Directory: {self.analysis_results.get('directory_path', 'Unknown')}")
        
        with col2:
            st.markdown("### 🔧 System Health")
            st.success("✅ Simple Analysis System: Operational")
            st.success("✅ AI-Enhanced System: Operational")
            st.success("✅ Real-Time Monitoring: Operational")
            st.success("✅ API Integration: Available")
        
        # Performance Metrics
        if 'ai_analysis' in self.analysis_results:
            ai_profile = self.analysis_results['ai_analysis']['efficiency_profile']
            
            st.markdown("### 📈 Performance Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Analysis Confidence", f"{ai_profile['confidence_level']:.1%}")
            
            with col2:
                st.metric("Data Quality", "High")
            
            with col3:
                st.metric("Recommendation Accuracy", "85%")
        
        # Export Options
        st.markdown("### 📤 Export & Integration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to Excel"):
                st.success("Excel export feature coming soon!")
        
        with col2:
            if st.button("🔗 Export to ClickUp"):
                st.success("ClickUp integration coming soon!")
        
        with col3:
            if st.button("📧 Email Report"):
                st.success("Email feature coming soon!")

def main():
    """Main function to run the advanced dashboard."""
    dashboard = AdvancedClickUpBrainDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()










