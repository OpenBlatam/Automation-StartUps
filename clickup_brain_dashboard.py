#!/usr/bin/env python3
"""
ClickUp Brain Interactive Dashboard
==================================

Interactive web dashboard with real-time visualization and analytics.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
import threading
import time

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clickup_brain_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
simple_system = SimpleClickUpBrainSystem()
enhanced_system = EnhancedClickUpBrainSystem()
realtime_system = ClickUpBrainRealtimeSystem()

# Dashboard data
dashboard_data = {
    'current_analysis': None,
    'monitoring_active': False,
    'efficiency_history': [],
    'tool_usage_history': [],
    'alerts': [],
    'recommendations': []
}

class DashboardManager:
    """Manages dashboard data and real-time updates"""
    
    def __init__(self):
        """Initialize dashboard manager"""
        self.update_thread = None
        self.is_running = False
    
    def start_updates(self):
        """Start real-time updates"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            logger.info("Dashboard updates started")
    
    def stop_updates(self):
        """Stop real-time updates"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("Dashboard updates stopped")
    
    def _update_loop(self):
        """Main update loop for real-time data"""
        while self.is_running:
            try:
                # Update efficiency history
                if realtime_system.is_monitoring:
                    latest_data = realtime_system.get_latest_data()
                    if latest_data:
                        dashboard_data['efficiency_history'].append({
                            'timestamp': latest_data['timestamp'],
                            'efficiency': latest_data['efficiency_score'],
                            'tool_count': len(latest_data['tool_usage'])
                        })
                        
                        # Keep only last 50 data points
                        if len(dashboard_data['efficiency_history']) > 50:
                            dashboard_data['efficiency_history'] = dashboard_data['efficiency_history'][-50:]
                
                # Update alerts
                recent_alerts = realtime_system.get_alerts(5)
                dashboard_data['alerts'] = recent_alerts
                
                # Emit updates to connected clients
                socketio.emit('dashboard_update', {
                    'efficiency_history': dashboard_data['efficiency_history'][-10:],
                    'alerts': recent_alerts,
                    'monitoring_active': realtime_system.is_monitoring
                })
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                time.sleep(30)

# Initialize dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/dashboard/overview')
def get_dashboard_overview():
    """Get dashboard overview data"""
    try:
        overview = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_active': realtime_system.is_monitoring,
            'total_tools': len(simple_system.software_db.tools),
            'categories': list(set(tool['category'] for tool in simple_system.software_db.tools.values())),
            'recent_analysis': dashboard_data['current_analysis'],
            'efficiency_trend': dashboard_data['efficiency_history'][-10:] if dashboard_data['efficiency_history'] else [],
            'recent_alerts': dashboard_data['alerts'][-5:] if dashboard_data['alerts'] else []
        }
        
        return jsonify(overview)
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/analysis', methods=['POST'])
def perform_analysis():
    """Perform analysis and return results"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path', '.')
        team_size = data.get('team_size', 10)
        analysis_type = data.get('analysis_type', 'basic')
        
        if analysis_type == 'ai_enhanced':
            results = enhanced_system.analyze_with_ai(directory_path, team_size)
        else:
            results = simple_system.scan_directory(directory_path)
        
        if "error" in results:
            return jsonify({'error': results['error']}), 500
        
        # Store current analysis
        dashboard_data['current_analysis'] = {
            'timestamp': datetime.now().isoformat(),
            'directory_path': directory_path,
            'team_size': team_size,
            'analysis_type': analysis_type,
            'results': results
        }
        
        return jsonify({
            'success': True,
            'analysis': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error performing analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start real-time monitoring"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path', '.')
        team_size = data.get('team_size', 10)
        check_interval = data.get('check_interval', 300)
        
        success = realtime_system.start_monitoring(directory_path, team_size, check_interval)
        
        if success:
            dashboard_data['monitoring_active'] = True
            dashboard_manager.start_updates()
            
            return jsonify({
                'success': True,
                'message': 'Monitoring started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to start monitoring'}), 500
            
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop real-time monitoring"""
    try:
        success = realtime_system.stop_monitoring()
        
        if success:
            dashboard_data['monitoring_active'] = False
            dashboard_manager.stop_updates()
            
            return jsonify({
                'success': True,
                'message': 'Monitoring stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to stop monitoring'}), 500
            
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/monitoring/status')
def get_monitoring_status():
    """Get monitoring status"""
    try:
        status = realtime_system.get_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/charts/efficiency')
def get_efficiency_chart():
    """Get efficiency trend chart data"""
    try:
        efficiency_data = dashboard_data['efficiency_history']
        
        if not efficiency_data:
            return jsonify({'error': 'No efficiency data available'})
        
        # Create Plotly chart
        timestamps = [item['timestamp'] for item in efficiency_data]
        efficiency_scores = [item['efficiency'] for item in efficiency_data]
        tool_counts = [item['tool_count'] for item in efficiency_data]
        
        # Efficiency trend chart
        efficiency_trace = go.Scatter(
            x=timestamps,
            y=efficiency_scores,
            mode='lines+markers',
            name='Efficiency Score',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        )
        
        # Tool count chart
        tool_trace = go.Scatter(
            x=timestamps,
            y=tool_counts,
            mode='lines+markers',
            name='Tool Count',
            yaxis='y2',
            line=dict(color='#A23B72', width=3),
            marker=dict(size=8)
        )
        
        layout = go.Layout(
            title='Team Efficiency & Tool Usage Trend',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Efficiency Score', side='left'),
            yaxis2=dict(title='Tool Count', side='right', overlaying='y'),
            hovermode='x unified',
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig = go.Figure(data=[efficiency_trace, tool_trace], layout=layout)
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({'chart': chart_json})
        
    except Exception as e:
        logger.error(f"Error creating efficiency chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/charts/tools')
def get_tools_chart():
    """Get tool usage distribution chart"""
    try:
        if not dashboard_data['current_analysis']:
            return jsonify({'error': 'No analysis data available'})
        
        analysis = dashboard_data['current_analysis']['results']
        tool_usage = analysis.get('tool_usage', {})
        
        if not tool_usage:
            return jsonify({'error': 'No tool usage data available'})
        
        # Prepare data for pie chart
        tool_names = list(tool_usage.keys())
        efficiency_scores = [tool['efficiency_score'] for tool in tool_usage.values()]
        
        # Create pie chart
        pie_trace = go.Pie(
            labels=tool_names,
            values=efficiency_scores,
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )
        
        layout = go.Layout(
            title='Tool Usage Distribution',
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig = go.Figure(data=[pie_trace], layout=layout)
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({'chart': chart_json})
        
    except Exception as e:
        logger.error(f"Error creating tools chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/recommendations')
def get_recommendations():
    """Get AI recommendations"""
    try:
        if not dashboard_data['current_analysis']:
            return jsonify({'error': 'No analysis data available'})
        
        analysis = dashboard_data['current_analysis']['results']
        
        if 'ai_recommendations' in analysis:
            recommendations = analysis['ai_recommendations']
        else:
            # Generate basic recommendations
            recommendations = []
            tool_usage = analysis.get('tool_usage', {})
            
            if "ClickUp" not in tool_usage:
                recommendations.append({
                    'tool_name': 'ClickUp',
                    'category': 'Project Management',
                    'confidence_score': 0.9,
                    'efficiency_impact': 3.5,
                    'implementation_difficulty': 'Medium',
                    'success_probability': 0.85
                })
        
        return jsonify({
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/export', methods=['POST'])
def export_dashboard_data():
    """Export dashboard data"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'full')
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'dashboard_data': dashboard_data,
            'monitoring_status': realtime_system.get_status() if realtime_system.is_monitoring else None
        }
        
        if export_type == 'analysis' and dashboard_data['current_analysis']:
            export_data['current_analysis'] = dashboard_data['current_analysis']
        
        filename = f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to ClickUp Brain Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    emit('dashboard_update', {
        'efficiency_history': dashboard_data['efficiency_history'][-10:],
        'alerts': dashboard_data['alerts'][-5:],
        'monitoring_active': realtime_system.is_monitoring,
        'timestamp': datetime.now().isoformat()
    })

# Create templates directory and HTML template
def create_dashboard_template():
    """Create dashboard HTML template"""
    template_dir = os.path.join(os.getcwd(), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClickUp Brain Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 30px; 
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px; 
        }
        .header p { 
            font-size: 1.2em; 
            opacity: 0.9; 
        }
        .dashboard-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            background: white; 
            border-radius: 15px; 
            padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
            transition: transform 0.3s ease; 
        }
        .card:hover { 
            transform: translateY(-5px); 
        }
        .card h3 { 
            color: #333; 
            margin-bottom: 15px; 
            font-size: 1.3em; 
        }
        .form-group { 
            margin-bottom: 15px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            color: #555; 
            font-weight: 500; 
        }
        .form-group input, .form-group select { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #e1e5e9; 
            border-radius: 8px; 
            font-size: 14px; 
        }
        .form-group input:focus, .form-group select:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 14px; 
            font-weight: 500; 
            transition: all 0.3s ease; 
            width: 100%; 
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0,0,0,0.2); 
        }
        .btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
        }
        .status { 
            padding: 10px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            font-weight: 500; 
        }
        .status.success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb; 
        }
        .status.error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb; 
        }
        .status.info { 
            background: #d1ecf1; 
            color: #0c5460; 
            border: 1px solid #bee5eb; 
        }
        .chart-container { 
            height: 400px; 
            margin-top: 20px; 
        }
        .recommendations { 
            max-height: 300px; 
            overflow-y: auto; 
        }
        .recommendation-item { 
            background: #f8f9fa; 
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 8px; 
            border-left: 4px solid #667eea; 
        }
        .recommendation-item h4 { 
            color: #333; 
            margin-bottom: 5px; 
        }
        .recommendation-item p { 
            color: #666; 
            font-size: 14px; 
        }
        .alerts { 
            max-height: 200px; 
            overflow-y: auto; 
        }
        .alert-item { 
            padding: 10px; 
            margin-bottom: 8px; 
            border-radius: 6px; 
            font-size: 14px; 
        }
        .alert-item.info { 
            background: #d1ecf1; 
            color: #0c5460; 
        }
        .alert-item.warning { 
            background: #fff3cd; 
            color: #856404; 
        }
        .alert-item.success { 
            background: #d4edda; 
            color: #155724; 
        }
        .loading { 
            text-align: center; 
            color: #666; 
            font-style: italic; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 ClickUp Brain Dashboard</h1>
            <p>AI-Powered Team Efficiency & Tool Selection Platform</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- Analysis Card -->
            <div class="card">
                <h3>📊 Analysis</h3>
                <div class="form-group">
                    <label>Directory Path:</label>
                    <input type="text" id="directoryPath" value="." placeholder="Enter directory path">
                </div>
                <div class="form-group">
                    <label>Team Size:</label>
                    <input type="number" id="teamSize" value="10" min="1" max="1000">
                </div>
                <div class="form-group">
                    <label>Analysis Type:</label>
                    <select id="analysisType">
                        <option value="basic">Basic Analysis</option>
                        <option value="ai_enhanced">AI-Enhanced Analysis</option>
                    </select>
                </div>
                <button class="btn" onclick="performAnalysis()">Run Analysis</button>
                <div id="analysisStatus"></div>
            </div>
            
            <!-- Monitoring Card -->
            <div class="card">
                <h3>📈 Real-time Monitoring</h3>
                <div class="form-group">
                    <label>Check Interval (seconds):</label>
                    <input type="number" id="checkInterval" value="300" min="30" max="3600">
                </div>
                <button class="btn" id="monitoringBtn" onclick="toggleMonitoring()">Start Monitoring</button>
                <div id="monitoringStatus"></div>
                <div id="monitoringInfo"></div>
            </div>
            
            <!-- Recommendations Card -->
            <div class="card">
                <h3>🤖 AI Recommendations</h3>
                <button class="btn" onclick="loadRecommendations()">Load Recommendations</button>
                <div id="recommendations" class="recommendations"></div>
            </div>
            
            <!-- Alerts Card -->
            <div class="card">
                <h3>🚨 Alerts</h3>
                <div id="alerts" class="alerts">
                    <div class="loading">No alerts available</div>
                </div>
            </div>
        </div>
        
        <!-- Charts Section -->
        <div class="dashboard-grid">
            <div class="card">
                <h3>📈 Efficiency Trend</h3>
                <div id="efficiencyChart" class="chart-container"></div>
            </div>
            
            <div class="card">
                <h3>🛠️ Tool Distribution</h3>
                <div id="toolsChart" class="chart-container"></div>
            </div>
        </div>
        
        <!-- Export Section -->
        <div class="card">
            <h3>📤 Export Data</h3>
            <button class="btn" onclick="exportData('full')">Export Full Data</button>
            <button class="btn" onclick="exportData('analysis')">Export Analysis Only</button>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // Global variables
        let isMonitoring = false;
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
        });
        
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        // Analysis functions
        async function performAnalysis() {
            const directoryPath = document.getElementById('directoryPath').value;
            const teamSize = parseInt(document.getElementById('teamSize').value);
            const analysisType = document.getElementById('analysisType').value;
            
            const statusDiv = document.getElementById('analysisStatus');
            statusDiv.innerHTML = '<div class="status info">Running analysis...</div>';
            
            try {
                const response = await fetch('/api/dashboard/analysis', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        directory_path: directoryPath,
                        team_size: teamSize,
                        analysis_type: analysisType
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML = '<div class="status success">Analysis completed successfully!</div>';
                    loadEfficiencyChart();
                    loadToolsChart();
                } else {
                    statusDiv.innerHTML = `<div class="status error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
            }
        }
        
        // Monitoring functions
        async function toggleMonitoring() {
            const directoryPath = document.getElementById('directoryPath').value;
            const teamSize = parseInt(document.getElementById('teamSize').value);
            const checkInterval = parseInt(document.getElementById('checkInterval').value);
            
            const statusDiv = document.getElementById('monitoringStatus');
            const btn = document.getElementById('monitoringBtn');
            
            if (!isMonitoring) {
                statusDiv.innerHTML = '<div class="status info">Starting monitoring...</div>';
                
                try {
                    const response = await fetch('/api/dashboard/monitoring/start', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            directory_path: directoryPath,
                            team_size: teamSize,
                            check_interval: checkInterval
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        isMonitoring = true;
                        btn.textContent = 'Stop Monitoring';
                        statusDiv.innerHTML = '<div class="status success">Monitoring started successfully!</div>';
                        updateMonitoringInfo();
                    } else {
                        statusDiv.innerHTML = `<div class="status error">Error: ${data.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
                }
            } else {
                try {
                    const response = await fetch('/api/dashboard/monitoring/stop', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        isMonitoring = false;
                        btn.textContent = 'Start Monitoring';
                        statusDiv.innerHTML = '<div class="status success">Monitoring stopped successfully!</div>';
                    } else {
                        statusDiv.innerHTML = `<div class="status error">Error: ${data.error}</div>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
                }
            }
        }
        
        async function updateMonitoringInfo() {
            try {
                const response = await fetch('/api/dashboard/monitoring/status');
                const data = await response.json();
                
                const infoDiv = document.getElementById('monitoringInfo');
                if (data.is_active) {
                    infoDiv.innerHTML = `
                        <div class="status info">
                            <strong>Monitoring Active</strong><br>
                            Directory: ${data.directory_path}<br>
                            Team Size: ${data.team_size}<br>
                            Total Checks: ${data.total_checks}<br>
                            Alerts: ${data.alerts_count}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error updating monitoring info:', error);
            }
        }
        
        // Chart functions
        async function loadEfficiencyChart() {
            try {
                const response = await fetch('/api/dashboard/charts/efficiency');
                const data = await response.json();
                
                if (data.chart) {
                    const chartData = JSON.parse(data.chart);
                    Plotly.newPlot('efficiencyChart', chartData.data, chartData.layout);
                } else {
                    document.getElementById('efficiencyChart').innerHTML = '<div class="loading">No efficiency data available</div>';
                }
            } catch (error) {
                console.error('Error loading efficiency chart:', error);
            }
        }
        
        async function loadToolsChart() {
            try {
                const response = await fetch('/api/dashboard/charts/tools');
                const data = await response.json();
                
                if (data.chart) {
                    const chartData = JSON.parse(data.chart);
                    Plotly.newPlot('toolsChart', chartData.data, chartData.layout);
                } else {
                    document.getElementById('toolsChart').innerHTML = '<div class="loading">No tool data available</div>';
                }
            } catch (error) {
                console.error('Error loading tools chart:', error);
            }
        }
        
        // Recommendations function
        async function loadRecommendations() {
            try {
                const response = await fetch('/api/dashboard/recommendations');
                const data = await response.json();
                
                const recommendationsDiv = document.getElementById('recommendations');
                
                if (data.recommendations && data.recommendations.length > 0) {
                    let html = '';
                    data.recommendations.forEach(rec => {
                        html += `
                            <div class="recommendation-item">
                                <h4>${rec.tool_name}</h4>
                                <p><strong>Category:</strong> ${rec.category}</p>
                                <p><strong>Confidence:</strong> ${(rec.confidence_score * 100).toFixed(1)}%</p>
                                <p><strong>Efficiency Impact:</strong> +${rec.efficiency_impact}</p>
                                <p><strong>Implementation:</strong> ${rec.implementation_difficulty}</p>
                            </div>
                        `;
                    });
                    recommendationsDiv.innerHTML = html;
                } else {
                    recommendationsDiv.innerHTML = '<div class="loading">No recommendations available</div>';
                }
            } catch (error) {
                console.error('Error loading recommendations:', error);
            }
        }
        
        // Export function
        async function exportData(type) {
            try {
                const response = await fetch('/api/dashboard/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ type: type })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(`Data exported successfully to: ${data.filename}`);
                } else {
                    alert(`Export failed: ${data.error}`);
                }
            } catch (error) {
                alert(`Export error: ${error.message}`);
            }
        }
        
        // Dashboard update function
        function updateDashboard(data) {
            // Update alerts
            const alertsDiv = document.getElementById('alerts');
            if (data.alerts && data.alerts.length > 0) {
                let html = '';
                data.alerts.forEach(alert => {
                    html += `<div class="alert-item ${alert.type}">${alert.message}</div>`;
                });
                alertsDiv.innerHTML = html;
            }
            
            // Update monitoring status
            if (data.monitoring_active !== undefined) {
                isMonitoring = data.monitoring_active;
                const btn = document.getElementById('monitoringBtn');
                btn.textContent = isMonitoring ? 'Stop Monitoring' : 'Start Monitoring';
            }
            
            // Update efficiency chart if monitoring is active
            if (data.monitoring_active && data.efficiency_history) {
                loadEfficiencyChart();
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadEfficiencyChart();
            loadToolsChart();
            loadRecommendations();
        });
    </script>
</body>
</html>
    """
    
    template_path = os.path.join(template_dir, 'dashboard.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Dashboard template created at: {template_path}")

def main():
    """Main function to run the dashboard"""
    print("🎛️ ClickUp Brain Interactive Dashboard")
    print("=" * 50)
    
    # Create dashboard template
    create_dashboard_template()
    
    print("📊 Dashboard Features:")
    print("  • Real-time analysis and monitoring")
    print("  • Interactive charts and visualizations")
    print("  • AI-powered recommendations")
    print("  • Live alerts and notifications")
    print("  • Data export capabilities")
    print("  • WebSocket real-time updates")
    
    print("\n🌐 Starting dashboard server...")
    print("Access the dashboard at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Start dashboard manager
        dashboard_manager.start_updates()
        
        # Run the Flask-SocketIO app
        socketio.run(app, host='0.0.0.0', port=5001, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard server stopped by user")
        dashboard_manager.stop_updates()
    except Exception as e:
        print(f"❌ Error running dashboard server: {str(e)}")
        dashboard_manager.stop_updates()

if __name__ == "__main__":
    main()