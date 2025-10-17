#!/usr/bin/env python3
"""
ClickUp Brain REST API
=====================

REST API for ClickUp Brain Tool Selection System with endpoints for
analysis, monitoring, and integration with external systems.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import time

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global instances
simple_system = SimpleClickUpBrainSystem()
enhanced_system = EnhancedClickUpBrainSystem()
realtime_system = ClickUpBrainRealtimeSystem()

# API Configuration
API_VERSION = "v1"
BASE_URL = f"/api/{API_VERSION}"

@app.route('/')
def home():
    """API home endpoint."""
    return jsonify({
        "name": "ClickUp Brain Tool Selection API",
        "version": API_VERSION,
        "description": "REST API for team efficiency analysis and tool recommendations",
        "endpoints": {
            "analysis": f"{BASE_URL}/analysis",
            "monitoring": f"{BASE_URL}/monitoring",
            "recommendations": f"{BASE_URL}/recommendations",
            "health": f"{BASE_URL}/health"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route(f'{BASE_URL}/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": API_VERSION,
        "systems": {
            "simple_analysis": "available",
            "ai_enhanced": "available",
            "realtime_monitoring": "available"
        }
    })

# Analysis Endpoints
@app.route(f'{BASE_URL}/analysis/basic', methods=['POST'])
def basic_analysis():
    """Perform basic analysis of a directory."""
    try:
        data = request.get_json()
        
        if not data or 'directory_path' not in data:
            return jsonify({
                "error": "Missing required field: directory_path"
            }), 400
        
        directory_path = data['directory_path']
        
        # Validate directory exists
        if not Path(directory_path).exists():
            return jsonify({
                "error": f"Directory not found: {directory_path}"
            }), 404
        
        # Perform analysis
        results = simple_system.scan_directory(directory_path)
        
        if "error" in results:
            return jsonify({
                "error": results["error"]
            }), 500
        
        return jsonify({
            "success": True,
            "analysis_type": "basic",
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/analysis/ai-enhanced', methods=['POST'])
def ai_enhanced_analysis():
    """Perform AI-enhanced analysis of a directory."""
    try:
        data = request.get_json()
        
        if not data or 'directory_path' not in data:
            return jsonify({
                "error": "Missing required field: directory_path"
            }), 400
        
        directory_path = data['directory_path']
        team_size = data.get('team_size', 10)
        
        # Validate directory exists
        if not Path(directory_path).exists():
            return jsonify({
                "error": f"Directory not found: {directory_path}"
            }), 404
        
        # Perform AI-enhanced analysis
        results = enhanced_system.analyze_with_ai(directory_path, team_size)
        
        if "error" in results:
            return jsonify({
                "error": results["error"]
            }), 500
        
        return jsonify({
            "success": True,
            "analysis_type": "ai_enhanced",
            "team_size": team_size,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"AI analysis failed: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/analysis/report', methods=['POST'])
def generate_report():
    """Generate analysis report."""
    try:
        data = request.get_json()
        
        if not data or 'analysis_results' not in data:
            return jsonify({
                "error": "Missing required field: analysis_results"
            }), 400
        
        analysis_results = data['analysis_results']
        report_type = data.get('report_type', 'basic')
        
        # Generate report
        if report_type == 'ai_enhanced':
            report = enhanced_system.generate_ai_report(analysis_results)
        else:
            report = simple_system.generate_report(analysis_results)
        
        return jsonify({
            "success": True,
            "report_type": report_type,
            "report": report,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Report generation failed: {str(e)}"
        }), 500

# Monitoring Endpoints
@app.route(f'{BASE_URL}/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start real-time monitoring."""
    try:
        data = request.get_json()
        
        if not data or 'directory_path' not in data:
            return jsonify({
                "error": "Missing required field: directory_path"
            }), 400
        
        directory_path = data['directory_path']
        team_size = data.get('team_size', 10)
        check_interval = data.get('check_interval', 300)  # 5 minutes default
        
        # Validate directory exists
        if not Path(directory_path).exists():
            return jsonify({
                "error": f"Directory not found: {directory_path}"
            }), 404
        
        # Start monitoring
        monitor = realtime_system.start_monitoring(directory_path, team_size, check_interval)
        
        return jsonify({
            "success": True,
            "message": "Real-time monitoring started",
            "directory_path": directory_path,
            "team_size": team_size,
            "check_interval": check_interval,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to start monitoring: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop real-time monitoring."""
    try:
        realtime_system.stop_monitoring()
        
        return jsonify({
            "success": True,
            "message": "Real-time monitoring stopped",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to stop monitoring: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/monitoring/status')
def monitoring_status():
    """Get monitoring status."""
    try:
        status = realtime_system.get_status()
        
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get monitoring status: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/monitoring/export', methods=['POST'])
def export_monitoring_data():
    """Export monitoring data."""
    try:
        data = request.get_json()
        output_file = data.get('output_file', f'monitoring_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        realtime_system.export_data(output_file)
        
        return jsonify({
            "success": True,
            "message": "Monitoring data exported",
            "output_file": output_file,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to export monitoring data: {str(e)}"
        }), 500

# Recommendations Endpoints
@app.route(f'{BASE_URL}/recommendations/tools', methods=['POST'])
def get_tool_recommendations():
    """Get AI-powered tool recommendations."""
    try:
        data = request.get_json()
        
        if not data or 'tool_usage' not in data:
            return jsonify({
                "error": "Missing required field: tool_usage"
            }), 400
        
        tool_usage = data['tool_usage']
        category_analysis = data.get('category_analysis', {})
        team_size = data.get('team_size', 10)
        
        # Generate AI recommendations
        ai_analyzer = enhanced_system.ai_analyzer
        recommendations = ai_analyzer.generate_ai_recommendations(
            tool_usage, category_analysis, team_size
        )
        
        # Convert to JSON-serializable format
        recommendations_data = []
        for rec in recommendations:
            recommendations_data.append({
                "tool_name": rec.tool_name,
                "category": rec.category,
                "confidence_score": rec.confidence_score,
                "efficiency_impact": rec.efficiency_impact,
                "implementation_difficulty": rec.implementation_difficulty,
                "cost_benefit_ratio": rec.cost_benefit_ratio,
                "team_size_optimal": rec.team_size_optimal,
                "integration_complexity": rec.integration_complexity,
                "learning_curve": rec.learning_curve,
                "roi_timeline": rec.roi_timeline,
                "alternative_tools": rec.alternative_tools,
                "success_probability": rec.success_probability
            })
        
        return jsonify({
            "success": True,
            "recommendations": recommendations_data,
            "team_size": team_size,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate recommendations: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/recommendations/clickup', methods=['POST'])
def get_clickup_recommendations():
    """Get ClickUp-specific recommendations."""
    try:
        data = request.get_json()
        
        if not data or 'tool_usage' not in data:
            return jsonify({
                "error": "Missing required field: tool_usage"
            }), 400
        
        tool_usage = data['tool_usage']
        team_size = data.get('team_size', 10)
        
        # Generate ClickUp recommendations
        clickup_recommendations = []
        
        # Check if ClickUp is already used
        if "ClickUp" not in tool_usage:
            clickup_recommendations.append({
                "type": "adoption",
                "title": "Consider ClickUp Adoption",
                "description": "ClickUp can consolidate your project management needs",
                "efficiency_boost": 40.0,
                "implementation_difficulty": "Medium",
                "roi_timeline": "2-3 months"
            })
        
        # Integration opportunities
        integration_opportunities = []
        clickup_integrations = ["Slack", "GitHub", "Figma", "Google Workspace", "Zoom"]
        
        for tool in tool_usage.keys():
            if tool in clickup_integrations:
                integration_opportunities.append({
                    "tool": tool,
                    "integration_type": "native",
                    "benefit": f"Seamless integration between {tool} and ClickUp"
                })
        
        # Feature recommendations
        feature_recommendations = []
        if team_size > 20:
            feature_recommendations.append("ClickUp Enterprise features for large team management")
        if any(cat in ["Development", "Design"] for cat in data.get('categories', [])):
            feature_recommendations.append("ClickUp's Gantt charts and timeline views")
        
        return jsonify({
            "success": True,
            "clickup_recommendations": clickup_recommendations,
            "integration_opportunities": integration_opportunities,
            "feature_recommendations": feature_recommendations,
            "team_size": team_size,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate ClickUp recommendations: {str(e)}"
        }), 500

# Utility Endpoints
@app.route(f'{BASE_URL}/tools/search')
def search_tools():
    """Search for tools in the database."""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        if not query and not category:
            return jsonify({
                "error": "Missing search query or category"
            }), 400
        
        # Search tools
        if query:
            results = simple_system.software_db.search_tools(query)
        else:
            # Filter by category
            results = [
                tool for tool in simple_system.software_db.tools.values()
                if tool['category'] == category
            ]
        
        return jsonify({
            "success": True,
            "query": query,
            "category": category,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Search failed: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/tools/<tool_name>')
def get_tool_details(tool_name):
    """Get detailed information about a specific tool."""
    try:
        tool = simple_system.software_db.get_tool_by_name(tool_name)
        
        if not tool:
            return jsonify({
                "error": f"Tool not found: {tool_name}"
            }), 404
        
        return jsonify({
            "success": True,
            "tool": tool,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get tool details: {str(e)}"
        }), 500

@app.route(f'{BASE_URL}/categories')
def get_categories():
    """Get all available tool categories."""
    try:
        categories = list(set(tool['category'] for tool in simple_system.software_db.tools.values()))
        
        return jsonify({
            "success": True,
            "categories": categories,
            "count": len(categories),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get categories: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Background tasks
def cleanup_old_files():
    """Clean up old analysis files."""
    while True:
        try:
            # Clean up files older than 7 days
            cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)
            
            for file_path in Path('.').glob('*_analysis_*.json'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
            
            for file_path in Path('.').glob('*_report_*.md'):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
            
            time.sleep(3600)  # Run every hour
            
        except Exception as e:
            print(f"Cleanup error: {e}")
            time.sleep(3600)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("🚀 Starting ClickUp Brain API Server")
    print("=" * 50)
    print(f"API Version: {API_VERSION}")
    print(f"Base URL: {BASE_URL}")
    print("Available endpoints:")
    print(f"  GET  / - API information")
    print(f"  GET  {BASE_URL}/health - Health check")
    print(f"  POST {BASE_URL}/analysis/basic - Basic analysis")
    print(f"  POST {BASE_URL}/analysis/ai-enhanced - AI-enhanced analysis")
    print(f"  POST {BASE_URL}/analysis/report - Generate report")
    print(f"  POST {BASE_URL}/monitoring/start - Start monitoring")
    print(f"  POST {BASE_URL}/monitoring/stop - Stop monitoring")
    print(f"  GET  {BASE_URL}/monitoring/status - Monitoring status")
    print(f"  POST {BASE_URL}/monitoring/export - Export monitoring data")
    print(f"  POST {BASE_URL}/recommendations/tools - Get tool recommendations")
    print(f"  POST {BASE_URL}/recommendations/clickup - Get ClickUp recommendations")
    print(f"  GET  {BASE_URL}/tools/search - Search tools")
    print(f"  GET  {BASE_URL}/tools/<name> - Get tool details")
    print(f"  GET  {BASE_URL}/categories - Get categories")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)