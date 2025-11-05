#!/usr/bin/env python3
"""
ClickUp Brain Mobile Interface
=============================

Mobile-optimized interface for ClickUp Brain system with responsive design
and mobile-specific features for on-the-go access.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_mobility import Mobility
import qrcode
from io import BytesIO
import base64

# Import our systems
from clickup_brain_simple import SimpleClickUpBrainSystem
from clickup_brain_ai_enhanced import EnhancedClickUpBrainSystem
from clickup_brain_realtime_monitor import ClickUpBrainRealtimeSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clickup_brain_mobile_secret'
Mobility(app)

# Global instances
simple_system = SimpleClickUpBrainSystem()
enhanced_system = EnhancedClickUpBrainSystem()
realtime_system = ClickUpBrainRealtimeSystem()

class MobileOptimizer:
    """Mobile-specific optimizations and utilities"""
    
    def __init__(self):
        """Initialize mobile optimizer"""
        self.mobile_features = {
            'quick_scan': True,
            'voice_input': False,  # Placeholder for future voice features
            'offline_mode': False,  # Placeholder for future offline features
            'push_notifications': False,  # Placeholder for future push features
            'gesture_controls': True,
            'touch_optimized': True
        }
    
    def optimize_for_mobile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize data for mobile display"""
        optimized = data.copy()
        
        # Reduce data size for mobile
        if 'tool_usage' in optimized:
            for tool_name, tool_data in optimized['tool_usage'].items():
                # Keep only essential fields for mobile
                optimized['tool_usage'][tool_name] = {
                    'name': tool_data.get('tool_name', tool_name),
                    'category': tool_data.get('category', 'Unknown'),
                    'efficiency_score': tool_data.get('efficiency_score', 0),
                    'cost_per_user': tool_data.get('cost_per_user', 0)
                }
        
        # Limit recommendations for mobile
        if 'ai_recommendations' in optimized:
            optimized['ai_recommendations'] = optimized['ai_recommendations'][:3]
        
        # Simplify alerts for mobile
        if 'alerts' in optimized:
            optimized['alerts'] = optimized['alerts'][:5]
        
        return optimized
    
    def generate_qr_code(self, data: str) -> str:
        """Generate QR code for sharing"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for web display
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None

# Initialize mobile optimizer
mobile_optimizer = MobileOptimizer()

@app.route('/')
def mobile_home():
    """Mobile home page"""
    return render_template('mobile.html')

@app.route('/mobile')
def mobile_dashboard():
    """Mobile dashboard"""
    return render_template('mobile_dashboard.html')

@app.route('/mobile/scan')
def mobile_scan():
    """Mobile quick scan page"""
    return render_template('mobile_scan.html')

@app.route('/mobile/recommendations')
def mobile_recommendations():
    """Mobile recommendations page"""
    return render_template('mobile_recommendations.html')

@app.route('/mobile/monitoring')
def mobile_monitoring():
    """Mobile monitoring page"""
    return render_template('mobile_monitoring.html')

# Mobile API endpoints
@app.route('/api/mobile/quick-scan', methods=['POST'])
def mobile_quick_scan():
    """Quick scan optimized for mobile"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path', '.')
        team_size = data.get('team_size', 10)
        
        # Perform quick analysis
        results = simple_system.scan_directory(directory_path)
        
        if "error" in results:
            return jsonify({'error': results['error']}), 500
        
        # Optimize for mobile
        mobile_results = mobile_optimizer.optimize_for_mobile(results)
        
        # Add mobile-specific data
        mobile_results['mobile_optimized'] = True
        mobile_results['scan_timestamp'] = datetime.now().isoformat()
        mobile_results['quick_summary'] = {
            'tools_found': len(results['tool_usage']),
            'efficiency_score': results['efficiency_score'],
            'categories': len(results['categories']),
            'recommendation': "Consider ClickUp for better project management" if "ClickUp" not in results['tool_usage'] else "Great tool selection!"
        }
        
        return jsonify({
            'success': True,
            'data': mobile_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mobile quick scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/ai-recommendations', methods=['POST'])
def mobile_ai_recommendations():
    """AI recommendations optimized for mobile"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path', '.')
        team_size = data.get('team_size', 10)
        
        # Get AI-enhanced analysis
        results = enhanced_system.analyze_with_ai(directory_path, team_size)
        
        if "error" in results:
            return jsonify({'error': results['error']}), 500
        
        # Optimize for mobile
        mobile_results = mobile_optimizer.optimize_for_mobile(results)
        
        # Add mobile-specific recommendations
        mobile_results['mobile_recommendations'] = []
        for rec in results.get('ai_recommendations', []):
            mobile_rec = {
                'tool_name': rec['tool_name'],
                'category': rec['category'],
                'confidence': f"{rec['confidence_score']:.0%}",
                'impact': f"+{rec['efficiency_impact']:.1f}",
                'difficulty': rec['implementation_difficulty'],
                'priority': 'High' if rec['confidence_score'] > 0.8 else 'Medium' if rec['confidence_score'] > 0.6 else 'Low'
            }
            mobile_results['mobile_recommendations'].append(mobile_rec)
        
        return jsonify({
            'success': True,
            'data': mobile_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mobile AI recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/monitoring/start', methods=['POST'])
def mobile_start_monitoring():
    """Start monitoring optimized for mobile"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path', '.')
        team_size = data.get('team_size', 10)
        check_interval = data.get('check_interval', 600)  # 10 minutes default for mobile
        
        success = realtime_system.start_monitoring(directory_path, team_size, check_interval)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Mobile monitoring started',
                'monitoring_active': True,
                'check_interval': check_interval,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to start monitoring'}), 500
            
    except Exception as e:
        logger.error(f"Error starting mobile monitoring: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/monitoring/status')
def mobile_monitoring_status():
    """Get monitoring status optimized for mobile"""
    try:
        status = realtime_system.get_status()
        
        # Optimize status for mobile
        mobile_status = {
            'is_active': status['is_active'],
            'last_check': status['last_check'],
            'total_checks': status['total_checks'],
            'alerts_count': status['alerts_count'],
            'efficiency_trend': status['efficiency_trend'][-5:] if status['efficiency_trend'] else [],
            'status_text': 'Active' if status['is_active'] else 'Inactive',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(mobile_status)
        
    except Exception as e:
        logger.error(f"Error getting mobile monitoring status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/share', methods=['POST'])
def mobile_share():
    """Share analysis results via QR code"""
    try:
        data = request.get_json()
        analysis_data = data.get('analysis_data', {})
        
        # Create shareable summary
        share_data = {
            'type': 'clickup_brain_analysis',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'tools_found': len(analysis_data.get('tool_usage', {})),
                'efficiency_score': analysis_data.get('efficiency_score', 0),
                'categories': analysis_data.get('categories', []),
                'top_recommendation': analysis_data.get('ai_recommendations', [{}])[0].get('tool_name', 'ClickUp') if analysis_data.get('ai_recommendations') else 'ClickUp'
            }
        }
        
        # Generate QR code
        qr_data = json.dumps(share_data)
        qr_code = mobile_optimizer.generate_qr_code(qr_data)
        
        return jsonify({
            'success': True,
            'qr_code': qr_code,
            'share_data': share_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating share QR code: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/tools/search')
def mobile_tools_search():
    """Search tools optimized for mobile"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        if not query and not category:
            return jsonify({'error': 'Missing search query or category'}), 400
        
        # Search tools
        if query:
            results = simple_system.software_db.search_tools(query)
        else:
            results = simple_system.software_db.get_tools_by_category(category)
        
        # Optimize for mobile
        mobile_results = []
        for tool in results[:10]:  # Limit to 10 results for mobile
            mobile_tool = {
                'name': tool['name'],
                'category': tool['category'],
                'efficiency_score': tool['efficiency_score'],
                'cost_per_user': tool['cost_per_user'],
                'description': tool['description'][:100] + '...' if len(tool['description']) > 100 else tool['description']
            }
            mobile_results.append(mobile_tool)
        
        return jsonify({
            'success': True,
            'results': mobile_results,
            'count': len(mobile_results),
            'query': query,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in mobile tools search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/offline-data')
def mobile_offline_data():
    """Get offline data for mobile app"""
    try:
        # Get essential data for offline use
        offline_data = {
            'tools_database': {},
            'categories': [],
            'recommendations': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # Add essential tools for offline reference
        essential_tools = ['ClickUp', 'Slack', 'GitHub', 'Figma', 'Notion']
        for tool_name in essential_tools:
            tool = simple_system.software_db.get_tool_by_name(tool_name)
            if tool:
                offline_data['tools_database'][tool_name] = {
                    'name': tool['name'],
                    'category': tool['category'],
                    'efficiency_score': tool['efficiency_score'],
                    'description': tool['description']
                }
        
        offline_data['categories'] = list(set(tool['category'] for tool in offline_data['tools_database'].values()))
        
        return jsonify({
            'success': True,
            'offline_data': offline_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting offline data: {e}")
        return jsonify({'error': str(e)}), 500

# Create mobile templates
def create_mobile_templates():
    """Create mobile-optimized HTML templates"""
    template_dir = os.path.join(os.getcwd(), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Mobile home template
    mobile_home_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ClickUp Brain Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        .container { 
            max-width: 100%; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 30px; 
            padding-top: 20px;
        }
        .header h1 { 
            font-size: 2.2em; 
            margin-bottom: 10px; 
            font-weight: 700;
        }
        .header p { 
            font-size: 1.1em; 
            opacity: 0.9; 
        }
        .nav-grid { 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 15px; 
            margin-bottom: 30px; 
        }
        .nav-card { 
            background: white; 
            border-radius: 20px; 
            padding: 25px 20px; 
            text-align: center; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
            transition: all 0.3s ease; 
            text-decoration: none;
            color: #333;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .nav-card:active { 
            transform: scale(0.95); 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .nav-card .icon { 
            font-size: 2.5em; 
            margin-bottom: 10px; 
        }
        .nav-card h3 { 
            font-size: 1.1em; 
            margin-bottom: 5px; 
            font-weight: 600;
        }
        .nav-card p { 
            font-size: 0.9em; 
            color: #666; 
            line-height: 1.4;
        }
        .quick-actions { 
            background: white; 
            border-radius: 20px; 
            padding: 25px; 
            margin-bottom: 20px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .quick-actions h3 { 
            color: #333; 
            margin-bottom: 20px; 
            font-size: 1.3em;
            font-weight: 600;
        }
        .form-group { 
            margin-bottom: 15px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            color: #555; 
            font-weight: 500; 
            font-size: 0.9em;
        }
        .form-group input, .form-group select { 
            width: 100%; 
            padding: 12px 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 12px; 
            font-size: 16px; 
            background: #f8f9fa;
        }
        .form-group input:focus, .form-group select:focus { 
            outline: none; 
            border-color: #667eea; 
            background: white;
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 15px 25px; 
            border-radius: 12px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 600; 
            transition: all 0.3s ease; 
            width: 100%; 
            margin-bottom: 10px;
        }
        .btn:active { 
            transform: scale(0.98); 
        }
        .btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
        }
        .status { 
            padding: 12px 15px; 
            border-radius: 12px; 
            margin-bottom: 15px; 
            font-weight: 500; 
            font-size: 0.9em;
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
        .footer { 
            text-align: center; 
            color: white; 
            margin-top: 30px; 
            padding: 20px; 
            opacity: 0.8;
        }
        .loading { 
            text-align: center; 
            color: #666; 
            font-style: italic; 
            padding: 20px;
        }
        @media (max-width: 480px) {
            .container { padding: 15px; }
            .header h1 { font-size: 1.8em; }
            .nav-card { padding: 20px 15px; min-height: 100px; }
            .nav-card .icon { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 ClickUp Brain</h1>
            <p>Mobile Team Efficiency Platform</p>
        </div>
        
        <div class="nav-grid">
            <a href="/mobile/scan" class="nav-card">
                <div class="icon">📊</div>
                <h3>Quick Scan</h3>
                <p>Analyze your project directory instantly</p>
            </a>
            
            <a href="/mobile/recommendations" class="nav-card">
                <div class="icon">🤖</div>
                <h3>AI Recommendations</h3>
                <p>Get smart tool suggestions</p>
            </a>
            
            <a href="/mobile/monitoring" class="nav-card">
                <div class="icon">📈</div>
                <h3>Live Monitoring</h3>
                <p>Track efficiency in real-time</p>
            </a>
            
            <a href="/mobile/dashboard" class="nav-card">
                <div class="icon">📱</div>
                <h3>Dashboard</h3>
                <p>Complete mobile dashboard</p>
            </a>
        </div>
        
        <div class="quick-actions">
            <h3>🚀 Quick Actions</h3>
            
            <div class="form-group">
                <label>Directory Path:</label>
                <input type="text" id="directoryPath" value="." placeholder="Enter directory path">
            </div>
            
            <div class="form-group">
                <label>Team Size:</label>
                <input type="number" id="teamSize" value="10" min="1" max="1000">
            </div>
            
            <button class="btn" onclick="quickScan()">📊 Quick Scan</button>
            <button class="btn" onclick="getRecommendations()">🤖 Get AI Recommendations</button>
            
            <div id="status"></div>
        </div>
        
        <div class="footer">
            <p>Optimized for mobile devices</p>
            <p>ClickUp Brain v2.0</p>
        </div>
    </div>
    
    <script>
        // Quick scan function
        async function quickScan() {
            const directoryPath = document.getElementById('directoryPath').value;
            const teamSize = parseInt(document.getElementById('teamSize').value);
            
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="status info">Scanning directory...</div>';
            
            try {
                const response = await fetch('/api/mobile/quick-scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        directory_path: directoryPath,
                        team_size: teamSize
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const summary = data.data.quick_summary;
                    statusDiv.innerHTML = `
                        <div class="status success">
                            <strong>Scan Complete!</strong><br>
                            Tools Found: ${summary.tools_found}<br>
                            Efficiency Score: ${summary.efficiency_score.toFixed(1)}/10<br>
                            Categories: ${summary.categories}<br>
                            <em>${summary.recommendation}</em>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = `<div class="status error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
            }
        }
        
        // Get recommendations function
        async function getRecommendations() {
            const directoryPath = document.getElementById('directoryPath').value;
            const teamSize = parseInt(document.getElementById('teamSize').value);
            
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="status info">Getting AI recommendations...</div>';
            
            try {
                const response = await fetch('/api/mobile/ai-recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        directory_path: directoryPath,
                        team_size: teamSize
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const recommendations = data.data.mobile_recommendations;
                    let html = '<div class="status success"><strong>AI Recommendations:</strong><br>';
                    
                    recommendations.forEach(rec => {
                        html += `
                            <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                                <strong>${rec.tool_name}</strong> (${rec.category})<br>
                                Confidence: ${rec.confidence} | Impact: ${rec.impact}<br>
                                Priority: ${rec.priority} | Difficulty: ${rec.difficulty}
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    statusDiv.innerHTML = html;
                } else {
                    statusDiv.innerHTML = `<div class="status error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">Error: ${error.message}</div>`;
            }
        }
        
        // Add touch feedback
        document.addEventListener('touchstart', function(e) {
            if (e.target.classList.contains('nav-card')) {
                e.target.style.transform = 'scale(0.95)';
            }
        });
        
        document.addEventListener('touchend', function(e) {
            if (e.target.classList.contains('nav-card')) {
                e.target.style.transform = 'scale(1)';
            }
        });
    </script>
</body>
</html>
    """
    
    # Mobile dashboard template
    mobile_dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ClickUp Brain Mobile Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 100%; 
            margin: 0 auto; 
            padding: 15px; 
        }
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 20px; 
            padding-top: 10px;
        }
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 5px; 
            font-weight: 700;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 10px; 
            margin-bottom: 20px; 
        }
        .stat-card { 
            background: white; 
            border-radius: 15px; 
            padding: 20px; 
            text-align: center; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
        }
        .stat-card .number { 
            font-size: 2em; 
            font-weight: 700; 
            color: #667eea; 
            margin-bottom: 5px; 
        }
        .stat-card .label { 
            font-size: 0.9em; 
            color: #666; 
        }
        .section { 
            background: white; 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 15px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .section h3 { 
            color: #333; 
            margin-bottom: 15px; 
            font-size: 1.2em;
            font-weight: 600;
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 10px; 
            cursor: pointer; 
            font-size: 14px; 
            font-weight: 600; 
            transition: all 0.3s ease; 
            width: 100%; 
            margin-bottom: 10px;
        }
        .btn:active { 
            transform: scale(0.98); 
        }
        .loading { 
            text-align: center; 
            color: #666; 
            font-style: italic; 
            padding: 20px;
        }
        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <button class="back-btn" onclick="window.location.href='/'">← Back</button>
    
    <div class="container">
        <div class="header">
            <h1>📱 Mobile Dashboard</h1>
            <p>Real-time team efficiency insights</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number" id="toolsCount">-</div>
                <div class="label">Tools Found</div>
            </div>
            <div class="stat-card">
                <div class="number" id="efficiencyScore">-</div>
                <div class="label">Efficiency Score</div>
            </div>
            <div class="stat-card">
                <div class="number" id="categoriesCount">-</div>
                <div class="label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="number" id="alertsCount">-</div>
                <div class="label">Active Alerts</div>
            </div>
        </div>
        
        <div class="section">
            <h3>📊 Quick Analysis</h3>
            <button class="btn" onclick="runQuickAnalysis()">Run Analysis</button>
            <div id="analysisResults"></div>
        </div>
        
        <div class="section">
            <h3>📈 Monitoring Status</h3>
            <button class="btn" onclick="checkMonitoringStatus()">Check Status</button>
            <div id="monitoringStatus"></div>
        </div>
        
        <div class="section">
            <h3>🤖 AI Recommendations</h3>
            <button class="btn" onclick="getAIRecommendations()">Get Recommendations</button>
            <div id="recommendations"></div>
        </div>
    </div>
    
    <script>
        // Run quick analysis
        async function runQuickAnalysis() {
            const resultsDiv = document.getElementById('analysisResults');
            resultsDiv.innerHTML = '<div class="loading">Running analysis...</div>';
            
            try {
                const response = await fetch('/api/mobile/quick-scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        directory_path: '.',
                        team_size: 10
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const summary = data.data.quick_summary;
                    resultsDiv.innerHTML = `
                        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; margin-top: 10px;">
                            <strong>Analysis Complete!</strong><br>
                            Tools: ${summary.tools_found} | Efficiency: ${summary.efficiency_score.toFixed(1)}/10<br>
                            Categories: ${summary.categories}<br>
                            <em>${summary.recommendation}</em>
                        </div>
                    `;
                    
                    // Update stats
                    document.getElementById('toolsCount').textContent = summary.tools_found;
                    document.getElementById('efficiencyScore').textContent = summary.efficiency_score.toFixed(1);
                    document.getElementById('categoriesCount').textContent = summary.categories;
                } else {
                    resultsDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin-top: 10px;">Error: ${data.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin-top: 10px;">Error: ${error.message}</div>`;
            }
        }
        
        // Check monitoring status
        async function checkMonitoringStatus() {
            const statusDiv = document.getElementById('monitoringStatus');
            statusDiv.innerHTML = '<div class="loading">Checking status...</div>';
            
            try {
                const response = await fetch('/api/mobile/monitoring/status');
                const data = await response.json();
                
                if (data.is_active) {
                    statusDiv.innerHTML = `
                        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; margin-top: 10px;">
                            <strong>Monitoring Active</strong><br>
                            Last Check: ${new Date(data.last_check).toLocaleString()}<br>
                            Total Checks: ${data.total_checks}<br>
                            Alerts: ${data.alerts_count}
                        </div>
                    `;
                    document.getElementById('alertsCount').textContent = data.alerts_count;
                } else {
                    statusDiv.innerHTML = `
                        <div style="background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; margin-top: 10px;">
                            <strong>Monitoring Inactive</strong><br>
                            Click "Start Monitoring" to begin real-time tracking
                        </div>
                    `;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin-top: 10px;">Error: ${error.message}</div>`;
            }
        }
        
        // Get AI recommendations
        async function getAIRecommendations() {
            const recDiv = document.getElementById('recommendations');
            recDiv.innerHTML = '<div class="loading">Getting AI recommendations...</div>';
            
            try {
                const response = await fetch('/api/mobile/ai-recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        directory_path: '.',
                        team_size: 10
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const recommendations = data.data.mobile_recommendations;
                    let html = '<div style="margin-top: 10px;">';
                    
                    recommendations.forEach(rec => {
                        html += `
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #667eea;">
                                <strong>${rec.tool_name}</strong> (${rec.category})<br>
                                <small>Confidence: ${rec.confidence} | Impact: ${rec.impact} | Priority: ${rec.priority}</small>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    recDiv.innerHTML = html;
                } else {
                    recDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin-top: 10px;">Error: ${data.error}</div>`;
                }
            } catch (error) {
                recDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 10px; margin-top: 10px;">Error: ${error.message}</div>`;
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            runQuickAnalysis();
            checkMonitoringStatus();
        });
    </script>
</body>
</html>
    """
    
    # Save templates
    with open(os.path.join(template_dir, 'mobile.html'), 'w', encoding='utf-8') as f:
        f.write(mobile_home_html)
    
    with open(os.path.join(template_dir, 'mobile_dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(mobile_dashboard_html)
    
    # Create additional mobile templates
    mobile_scan_html = mobile_home_html.replace('Mobile Team Efficiency Platform', 'Quick Scan').replace('class="header"', 'class="header" style="padding-top: 50px;"')
    mobile_recommendations_html = mobile_home_html.replace('Mobile Team Efficiency Platform', 'AI Recommendations').replace('class="header"', 'class="header" style="padding-top: 50px;"')
    mobile_monitoring_html = mobile_home_html.replace('Mobile Team Efficiency Platform', 'Live Monitoring').replace('class="header"', 'class="header" style="padding-top: 50px;"')
    
    with open(os.path.join(template_dir, 'mobile_scan.html'), 'w', encoding='utf-8') as f:
        f.write(mobile_scan_html)
    
    with open(os.path.join(template_dir, 'mobile_recommendations.html'), 'w', encoding='utf-8') as f:
        f.write(mobile_recommendations_html)
    
    with open(os.path.join(template_dir, 'mobile_monitoring.html'), 'w', encoding='utf-8') as f:
        f.write(mobile_monitoring_html)
    
    logger.info("Mobile templates created successfully")

def main():
    """Main function to run the mobile interface"""
    print("📱 ClickUp Brain Mobile Interface")
    print("=" * 50)
    
    # Create mobile templates
    create_mobile_templates()
    
    print("📱 Mobile Features:")
    print("  • Touch-optimized interface")
    print("  • Quick scan functionality")
    print("  • AI recommendations on mobile")
    print("  • Real-time monitoring")
    print("  • QR code sharing")
    print("  • Offline data support")
    print("  • Responsive design")
    
    print("\n🌐 Starting mobile interface...")
    print("Access the mobile interface at: http://localhost:5002")
    print("Mobile-optimized for smartphones and tablets")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Mobile interface stopped by user")
    except Exception as e:
        print(f"❌ Error running mobile interface: {str(e)}")

if __name__ == "__main__":
    main()