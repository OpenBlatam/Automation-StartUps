"""
Launch Planning Dashboard
Web-based interface for the Launch Planning System with ClickUp Brain Integration
"""

import json
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from launch_planning_checklist import LaunchPlanningChecklist
from clickup_brain_integration import ClickUpBrainBehavior
from advanced_launch_planner import AdvancedLaunchPlanner

# Page configuration
st.set_page_config(
    page_title="Launch Planning System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'checklist' not in st.session_state:
        st.session_state.checklist = LaunchPlanningChecklist()
        st.session_state.checklist.load_default_template()
    
    if 'brain' not in st.session_state:
        st.session_state.brain = ClickUpBrainBehavior()
    
    if 'advanced_planner' not in st.session_state:
        st.session_state.advanced_planner = AdvancedLaunchPlanner()
    
    if 'launch_plan' not in st.session_state:
        st.session_state.launch_plan = None

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">🚀 Launch Planning System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Simplify launch planning with ready-to-use checklists and ClickUp Brain integration
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_overview_metrics():
    """Display overview metrics"""
    checklist = st.session_state.checklist
    all_items = checklist.get_all_items()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Phases",
            value=len(checklist.phases),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Items",
            value=len(all_items),
            delta=None
        )
    
    with col3:
        completed = len(checklist.get_items_by_status("completed"))
        st.metric(
            label="Completed",
            value=completed,
            delta=f"{completed/len(all_items)*100:.1f}%" if all_items else "0%"
        )
    
    with col4:
        high_priority = len(checklist.get_items_by_priority("high"))
        st.metric(
            label="High Priority",
            value=high_priority,
            delta=None
        )

def display_phases_overview():
    """Display phases overview"""
    st.subheader("📋 Launch Phases Overview")
    
    checklist = st.session_state.checklist
    phases_data = []
    
    for phase in checklist.phases:
        phases_data.append({
            "Phase": phase.name,
            "Items": len(phase.items),
            "High Priority": len([item for item in phase.items if item.priority == "high"]),
            "Completed": len([item for item in phase.items if item.status == "completed"]),
            "Progress": f"{len([item for item in phase.items if item.status == 'completed'])/len(phase.items)*100:.1f}%" if phase.items else "0%"
        })
    
    df = pd.DataFrame(phases_data)
    st.dataframe(df, use_container_width=True)
    
    # Progress chart
    fig = px.bar(
        df, 
        x="Phase", 
        y="Items",
        color="High Priority",
        title="Items per Phase",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

def display_priority_breakdown():
    """Display priority breakdown"""
    st.subheader("⚡ Priority Breakdown")
    
    checklist = st.session_state.checklist
    all_items = checklist.get_all_items()
    
    priority_counts = {
        "High": len(checklist.get_items_by_priority("high")),
        "Medium": len(checklist.get_items_by_priority("medium")),
        "Low": len(checklist.get_items_by_priority("low"))
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig = px.pie(
            values=list(priority_counts.values()),
            names=list(priority_counts.keys()),
            title="Priority Distribution",
            color_discrete_map={
                "High": "#dc3545",
                "Medium": "#ffc107", 
                "Low": "#28a745"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart
        fig = px.bar(
            x=list(priority_counts.keys()),
            y=list(priority_counts.values()),
            title="Priority Count",
            color=list(priority_counts.keys()),
            color_discrete_map={
                "High": "#dc3545",
                "Medium": "#ffc107",
                "Low": "#28a745"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

def display_category_analysis():
    """Display category analysis"""
    st.subheader("📊 Category Analysis")
    
    checklist = st.session_state.checklist
    all_items = checklist.get_all_items()
    
    categories = {}
    for item in all_items:
        if item.category not in categories:
            categories[item.category] = {"total": 0, "completed": 0, "high_priority": 0}
        categories[item.category]["total"] += 1
        if item.status == "completed":
            categories[item.category]["completed"] += 1
        if item.priority == "high":
            categories[item.category]["high_priority"] += 1
    
    category_data = []
    for category, data in categories.items():
        category_data.append({
            "Category": category,
            "Total Items": data["total"],
            "Completed": data["completed"],
            "High Priority": data["high_priority"],
            "Completion Rate": f"{data['completed']/data['total']*100:.1f}%" if data['total'] > 0 else "0%"
        })
    
    df = pd.DataFrame(category_data)
    st.dataframe(df, use_container_width=True)
    
    # Category chart
    fig = px.bar(
        df,
        x="Category",
        y="Total Items",
        color="High Priority",
        title="Items by Category",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

def display_clickup_brain_interface():
    """Display ClickUp Brain interface"""
    st.subheader("🧠 ClickUp Brain Integration")
    
    st.markdown("""
    Enter your launch requirements in natural language, and the ClickUp Brain will extract criteria 
    and format them into actionable tasks.
    """)
    
    # Text input for requirements
    requirements = st.text_area(
        "Launch Requirements",
        placeholder="""Example: Launch our new mobile app by Q2 2024. 
We need 5 developers and a budget of $50,000.
Priority is high for security audit.
Assign marketing tasks to Sarah.""",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Extract Criteria", type="primary"):
            if requirements:
                with st.spinner("Processing requirements..."):
                    result = st.session_state.brain.process_launch_requirements(requirements)
                    st.session_state.brain_result = result
                
                st.success("Criteria extracted successfully!")
                
                # Display extracted criteria
                st.subheader("📋 Extracted Criteria")
                for criterion in result["extracted_criteria"]:
                    st.info(f"**{criterion['type'].title()}**: {criterion['value']}")
                
                # Display workspace structure
                st.subheader("🏗️ Generated Workspace Structure")
                workspace = result["workspace_structure"]
                st.write(f"**Folders**: {len(workspace['folders'])}")
                st.write(f"**Lists**: {len(workspace['lists'])}")
                
                for folder in workspace["folders"]:
                    with st.expander(f"📁 {folder['name']}"):
                        for list_obj in folder["lists"]:
                            st.write(f"📋 {list_obj['name']} ({len(list_obj['tasks'])} tasks)")
            else:
                st.warning("Please enter launch requirements first.")
    
    with col2:
        if st.button("📥 Download ClickUp Import"):
            if hasattr(st.session_state, 'brain_result'):
                import_data = st.session_state.brain_result["import_json"]
                st.download_button(
                    label="Download JSON",
                    data=import_data,
                    file_name=f"clickup_workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("Please extract criteria first.")

def display_advanced_planner():
    """Display advanced planner interface"""
    st.subheader("🎯 Advanced Launch Planner")
    
    # Scenario selection
    scenario_type = st.selectbox(
        "Select Launch Scenario",
        ["mobile_app", "saas_platform", "ecommerce", "content_launch"],
        format_func=lambda x: {
            "mobile_app": "Mobile App Launch",
            "saas_platform": "SaaS Platform Launch", 
            "ecommerce": "E-commerce Launch",
            "content_launch": "Content/Media Launch"
        }[x]
    )
    
    # Requirements input
    advanced_requirements = st.text_area(
        "Advanced Requirements",
        placeholder="""Example: Launch a SaaS platform for project management.
Target: 10,000 users in first 6 months.
Budget: $150,000 for development and marketing.
Need 6 developers, 2 designers, 1 marketing manager.
Must integrate with Slack, Google Workspace, and payment systems.""",
        height=150
    )
    
    if st.button("🚀 Create Advanced Launch Plan", type="primary"):
        if advanced_requirements:
            with st.spinner("Creating comprehensive launch plan..."):
                launch_plan = st.session_state.advanced_planner.create_custom_launch_plan(
                    advanced_requirements, scenario_type
                )
                st.session_state.launch_plan = launch_plan
            
            st.success("Advanced launch plan created successfully!")
            
            # Display plan summary
            st.subheader("📊 Launch Plan Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Complexity Score",
                    f"{launch_plan['analysis']['complexity_score']}/10",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Risk Level",
                    launch_plan['analysis']['risk_level'].upper(),
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Team Size",
                    f"{launch_plan['resources'].team_size} people",
                    delta=None
                )
            
            # Display detailed information
            with st.expander("📋 Detailed Analysis"):
                st.json(launch_plan['analysis'])
            
            with st.expander("👥 Team Structure"):
                for member in launch_plan['team']:
                    st.write(f"**{member.name}**: {member.role} ({member.availability})")
            
            with st.expander("💰 Resource Requirements"):
                resources = launch_plan['resources']
                st.write(f"**Budget**: ${resources.budget:,.0f}")
                st.write(f"**Tools**: {', '.join(resources.tools)}")
                st.write(f"**External Services**: {', '.join(resources.external_services)}")
            
            with st.expander("⚠️ Risk Assessment"):
                risks = launch_plan['risk_assessment']
                st.write("**Technical Risks:**")
                for risk in risks['technical_risks']:
                    st.write(f"- {risk}")
                st.write("**Mitigation Strategies:**")
                for strategy in risks['mitigation_strategies']:
                    st.write(f"- {strategy}")
            
            # Download options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download Report"):
                    report = st.session_state.advanced_planner.generate_launch_report(launch_plan)
                    st.download_button(
                        label="Download Markdown Report",
                        data=report,
                        file_name=f"launch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            
            with col2:
                if st.button("📊 Download JSON Plan"):
                    plan_json = json.dumps({
                        "launch_plan": {
                            "scenario": launch_plan['scenario'],
                            "analysis": launch_plan['analysis'],
                            "metrics": launch_plan['metrics'].__dict__,
                            "team": [member.__dict__ for member in launch_plan['team']],
                            "resources": launch_plan['resources'].__dict__,
                            "risk_assessment": launch_plan['risk_assessment']
                        }
                    }, indent=2)
                    st.download_button(
                        label="Download JSON Plan",
                        data=plan_json,
                        file_name=f"launch_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col3:
                if st.button("📥 Download ClickUp Workspace"):
                    st.download_button(
                        label="Download ClickUp Import",
                        data=launch_plan['import_data'],
                        file_name=f"clickup_workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.warning("Please enter advanced requirements first.")

def display_sidebar():
    """Display sidebar navigation"""
    st.sidebar.title("🚀 Navigation")
    
    page = st.sidebar.selectbox(
        "Select Page",
        [
            "📊 Dashboard Overview",
            "📋 Checklist Management", 
            "🧠 ClickUp Brain",
            "🎯 Advanced Planner",
            "📈 Analytics & Reports"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.session_state.checklist = LaunchPlanningChecklist()
        st.session_state.checklist.load_default_template()
        st.rerun()
    
    if st.sidebar.button("📥 Export Checklist"):
        json_export = st.session_state.checklist.export_to_json()
        st.sidebar.download_button(
            label="Download Checklist JSON",
            data=json_export,
            file_name=f"checklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    st.sidebar.markdown("---")
    
    # System info
    st.sidebar.subheader("ℹ️ System Info")
    st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return page

def main():
    """Main dashboard application"""
    initialize_session_state()
    display_header()
    
    # Sidebar navigation
    page = display_sidebar()
    
    # Main content based on selected page
    if page == "📊 Dashboard Overview":
        display_overview_metrics()
        st.markdown("---")
        display_phases_overview()
        st.markdown("---")
        display_priority_breakdown()
        st.markdown("---")
        display_category_analysis()
    
    elif page == "📋 Checklist Management":
        st.subheader("📋 Checklist Management")
        st.info("Checklist management features will be implemented here.")
    
    elif page == "🧠 ClickUp Brain":
        display_clickup_brain_interface()
    
    elif page == "🎯 Advanced Planner":
        display_advanced_planner()
    
    elif page == "📈 Analytics & Reports":
        st.subheader("📈 Analytics & Reports")
        st.info("Analytics and reporting features will be implemented here.")

if __name__ == "__main__":
    main()








