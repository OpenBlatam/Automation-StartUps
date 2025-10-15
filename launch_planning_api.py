"""
Launch Planning API
RESTful API for the Launch Planning System with ClickUp Brain Integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

from launch_planning_checklist import LaunchPlanningChecklist, ChecklistItem, LaunchPhase
from clickup_brain_integration import ClickUpBrainBehavior, ClickUpBrainExtractor
from advanced_launch_planner import AdvancedLaunchPlanner, LaunchMetrics, TeamMember, ResourceRequirement

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global instances
checklist_system = LaunchPlanningChecklist()
brain_system = ClickUpBrainBehavior()
advanced_planner = AdvancedLaunchPlanner()

# In-memory storage for demo (in production, use a database)
launch_plans = {}
user_sessions = {}

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "message": "Launch Planning System API",
        "version": "1.0.0",
        "endpoints": {
            "checklist": "/api/checklist",
            "brain": "/api/brain",
            "planner": "/api/planner",
            "export": "/api/export"
        },
        "timestamp": datetime.now().isoformat()
    })

# Checklist API Endpoints
@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    """Get the default checklist template"""
    try:
        checklist_system.load_default_template()
        all_items = checklist_system.get_all_items()
        
        return jsonify({
            "success": True,
            "data": {
                "phases": [
                    {
                        "name": phase.name,
                        "description": phase.description,
                        "items": [
                            {
                                "id": item.id,
                                "title": item.title,
                                "description": item.description,
                                "category": item.category,
                                "priority": item.priority,
                                "status": item.status,
                                "estimated_duration": item.estimated_duration,
                                "dependencies": item.dependencies,
                                "assignee": item.assignee,
                                "due_date": item.due_date,
                                "tags": item.tags
                            }
                            for item in phase.items
                        ]
                    }
                    for phase in checklist_system.phases
                ],
                "summary": {
                    "total_phases": len(checklist_system.phases),
                    "total_items": len(all_items),
                    "high_priority": len(checklist_system.get_items_by_priority("high")),
                    "completed": len(checklist_system.get_items_by_status("completed"))
                }
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/checklist/item/<item_id>/status', methods=['PUT'])
def update_item_status(item_id: str):
    """Update the status of a checklist item"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({"success": False, "error": "Status is required"}), 400
        
        success = checklist_system.update_item_status(item_id, status)
        
        if success:
            return jsonify({"success": True, "message": f"Item {item_id} status updated to {status}"})
        else:
            return jsonify({"success": False, "error": "Item not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/checklist/item/<item_id>/assign', methods=['PUT'])
def assign_item(item_id: str):
    """Assign a checklist item to a team member"""
    try:
        data = request.get_json()
        assignee = data.get('assignee')
        
        if not assignee:
            return jsonify({"success": False, "error": "Assignee is required"}), 400
        
        success = checklist_system.assign_item(item_id, assignee)
        
        if success:
            return jsonify({"success": True, "message": f"Item {item_id} assigned to {assignee}"})
        else:
            return jsonify({"success": False, "error": "Item not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/checklist/export', methods=['GET'])
def export_checklist():
    """Export checklist to JSON"""
    try:
        checklist_system.load_default_template()
        json_export = checklist_system.export_to_json()
        
        return jsonify({
            "success": True,
            "data": json.loads(json_export),
            "exported_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ClickUp Brain API Endpoints
@app.route('/api/brain/extract', methods=['POST'])
def extract_criteria():
    """Extract criteria from launch requirements"""
    try:
        data = request.get_json()
        requirements = data.get('requirements')
        
        if not requirements:
            return jsonify({"success": False, "error": "Requirements text is required"}), 400
        
        result = brain_system.process_launch_requirements(requirements)
        
        return jsonify({
            "success": True,
            "data": {
                "extracted_criteria": result["extracted_criteria"],
                "parsed_requirements": result["parsed_requirements"],
                "workspace_structure": result["workspace_structure"],
                "import_json": result["import_json"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/brain/workspace', methods=['POST'])
def create_workspace():
    """Create ClickUp workspace structure"""
    try:
        data = request.get_json()
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"success": False, "error": "Requirements text is required"}), 400
        
        # Process with advanced planner
        launch_plan = advanced_planner.create_custom_launch_plan(requirements, scenario_type)
        
        return jsonify({
            "success": True,
            "data": {
                "workspace_structure": launch_plan["clickup_workspace"],
                "import_data": launch_plan["import_data"],
                "analysis": launch_plan["analysis"],
                "metrics": launch_plan["metrics"].__dict__,
                "team": [member.__dict__ for member in launch_plan["team"]],
                "resources": launch_plan["resources"].__dict__
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Advanced Planner API Endpoints
@app.route('/api/planner/scenarios', methods=['GET'])
def get_scenarios():
    """Get available launch scenarios"""
    try:
        scenarios = {
            "mobile_app": advanced_planner.create_launch_scenario("mobile_app"),
            "saas_platform": advanced_planner.create_launch_scenario("saas_platform"),
            "ecommerce": advanced_planner.create_launch_scenario("ecommerce"),
            "content_launch": advanced_planner.create_launch_scenario("content_launch")
        }
        
        return jsonify({
            "success": True,
            "data": scenarios
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/planner/create', methods=['POST'])
def create_launch_plan():
    """Create a comprehensive launch plan"""
    try:
        data = request.get_json()
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"success": False, "error": "Requirements text is required"}), 400
        
        # Create launch plan
        launch_plan = advanced_planner.create_custom_launch_plan(requirements, scenario_type)
        
        # Store in memory (in production, save to database)
        plan_id = str(uuid.uuid4())
        launch_plans[plan_id] = {
            "id": plan_id,
            "created_at": datetime.now().isoformat(),
            "plan": launch_plan
        }
        
        return jsonify({
            "success": True,
            "data": {
                "plan_id": plan_id,
                "scenario": launch_plan["scenario"],
                "analysis": launch_plan["analysis"],
                "metrics": launch_plan["metrics"].__dict__,
                "team": [member.__dict__ for member in launch_plan["team"]],
                "resources": launch_plan["resources"].__dict__,
                "risk_assessment": launch_plan["risk_assessment"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/planner/<plan_id>', methods=['GET'])
def get_launch_plan(plan_id: str):
    """Get a specific launch plan"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"success": False, "error": "Launch plan not found"}), 404
        
        plan_data = launch_plans[plan_id]
        
        return jsonify({
            "success": True,
            "data": plan_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/planner/<plan_id>/report', methods=['GET'])
def get_launch_report(plan_id: str):
    """Generate launch planning report"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"success": False, "error": "Launch plan not found"}), 404
        
        plan_data = launch_plans[plan_id]
        report = advanced_planner.generate_launch_report(plan_data["plan"])
        
        return jsonify({
            "success": True,
            "data": {
                "report": report,
                "generated_at": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Export API Endpoints
@app.route('/api/export/checklist/<format>', methods=['GET'])
def export_checklist_format(format: str):
    """Export checklist in different formats"""
    try:
        checklist_system.load_default_template()
        
        if format == 'json':
            json_export = checklist_system.export_to_json()
            return jsonify(json.loads(json_export))
        
        elif format == 'csv':
            # Convert to CSV format
            all_items = checklist_system.get_all_items()
            csv_data = []
            for item in all_items:
                csv_data.append({
                    "ID": item.id,
                    "Title": item.title,
                    "Description": item.description,
                    "Category": item.category,
                    "Priority": item.priority,
                    "Status": item.status,
                    "Estimated Duration": item.estimated_duration,
                    "Dependencies": ", ".join(item.dependencies),
                    "Assignee": item.assignee or "",
                    "Due Date": item.due_date or "",
                    "Tags": ", ".join(item.tags)
                })
            
            return jsonify({
                "success": True,
                "data": csv_data,
                "format": "csv"
            })
        
        else:
            return jsonify({"success": False, "error": "Unsupported format"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/export/clickup/<plan_id>', methods=['GET'])
def export_clickup_workspace(plan_id: str):
    """Export ClickUp workspace for a specific plan"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"success": False, "error": "Launch plan not found"}), 404
        
        plan_data = launch_plans[plan_id]
        import_data = plan_data["plan"]["import_data"]
        
        return jsonify({
            "success": True,
            "data": json.loads(import_data),
            "exported_at": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Analytics API Endpoints
@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get analytics overview"""
    try:
        checklist_system.load_default_template()
        all_items = checklist_system.get_all_items()
        
        # Calculate analytics
        analytics = {
            "total_items": len(all_items),
            "completed_items": len(checklist_system.get_items_by_status("completed")),
            "in_progress_items": len(checklist_system.get_items_by_status("in_progress")),
            "pending_items": len(checklist_system.get_items_by_status("pending")),
            "high_priority_items": len(checklist_system.get_items_by_priority("high")),
            "medium_priority_items": len(checklist_system.get_items_by_priority("medium")),
            "low_priority_items": len(checklist_system.get_items_by_priority("low")),
            "completion_rate": len(checklist_system.get_items_by_status("completed")) / len(all_items) * 100 if all_items else 0,
            "category_breakdown": {},
            "phase_breakdown": {}
        }
        
        # Category breakdown
        categories = {}
        for item in all_items:
            if item.category not in categories:
                categories[item.category] = 0
            categories[item.category] += 1
        analytics["category_breakdown"] = categories
        
        # Phase breakdown
        for phase in checklist_system.phases:
            analytics["phase_breakdown"][phase.name] = len(phase.items)
        
        return jsonify({
            "success": True,
            "data": analytics
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analytics/plans', methods=['GET'])
def get_plans_analytics():
    """Get analytics for all launch plans"""
    try:
        plans_analytics = {
            "total_plans": len(launch_plans),
            "scenarios": {},
            "complexity_distribution": {},
            "risk_levels": {},
            "recent_plans": []
        }
        
        for plan_id, plan_data in launch_plans.items():
            plan = plan_data["plan"]
            scenario = plan["scenario"]["name"]
            complexity = plan["analysis"]["complexity_score"]
            risk_level = plan["analysis"]["risk_level"]
            
            # Scenario distribution
            if scenario not in plans_analytics["scenarios"]:
                plans_analytics["scenarios"][scenario] = 0
            plans_analytics["scenarios"][scenario] += 1
            
            # Complexity distribution
            if complexity not in plans_analytics["complexity_distribution"]:
                plans_analytics["complexity_distribution"][complexity] = 0
            plans_analytics["complexity_distribution"][complexity] += 1
            
            # Risk level distribution
            if risk_level not in plans_analytics["risk_levels"]:
                plans_analytics["risk_levels"][risk_level] = 0
            plans_analytics["risk_levels"][risk_level] += 1
            
            # Recent plans
            plans_analytics["recent_plans"].append({
                "id": plan_id,
                "scenario": scenario,
                "created_at": plan_data["created_at"],
                "complexity": complexity,
                "risk_level": risk_level
            })
        
        # Sort recent plans by creation date
        plans_analytics["recent_plans"].sort(
            key=lambda x: x["created_at"], 
            reverse=True
        )
        plans_analytics["recent_plans"] = plans_analytics["recent_plans"][:10]  # Last 10
        
        return jsonify({
            "success": True,
            "data": plans_analytics
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Launch Planning API Server...")
    print("📡 API Documentation:")
    print("   GET  /                    - API home")
    print("   GET  /api/checklist       - Get checklist template")
    print("   PUT  /api/checklist/item/<id>/status - Update item status")
    print("   POST /api/brain/extract   - Extract criteria from text")
    print("   POST /api/planner/create  - Create launch plan")
    print("   GET  /api/analytics/overview - Get analytics")
    print("   GET  /health              - Health check")
    print("\n🌐 Server starting on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)








