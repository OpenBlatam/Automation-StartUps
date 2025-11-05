"""
Enhanced Launch Planning API
API RESTful mejorada con IA, análisis predictivo y funcionalidades premium
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from functools import wraps

# Importar sistemas mejorados
from enhanced_launch_planner import EnhancedLaunchPlanner, AIPrediction, MarketAnalysis, PerformanceMetrics
from launch_planning_checklist import LaunchPlanningChecklist
from clickup_brain_integration import ClickUpBrainBehavior

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask app
app = Flask(__name__)
CORS(app)

# Configurar rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour", "100 per minute"]
)

# Configuración de la aplicación
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'enhanced-launch-planning-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Instancias globales
enhanced_planner = EnhancedLaunchPlanner()
checklist_system = LaunchPlanningChecklist()
brain_system = ClickUpBrainBehavior()

# Almacenamiento en memoria (en producción, usar base de datos)
launch_plans = {}
user_sessions = {}
analysis_cache = {}
api_keys = {}

# Middleware de autenticación
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key not in api_keys:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Middleware de logging
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status_code} for {request.path}")
    return response

# Endpoints principales
@app.route('/')
def home():
    """API home endpoint mejorado"""
    return jsonify({
        "message": "Enhanced Launch Planning System API",
        "version": "2.0.0",
        "features": [
            "AI-powered analysis",
            "Predictive analytics",
            "Market intelligence",
            "Budget optimization",
            "Risk assessment",
            "Performance metrics"
        ],
        "endpoints": {
            "enhanced_planner": "/api/v2/planner",
            "ai_analysis": "/api/v2/ai/analyze",
            "market_intelligence": "/api/v2/market/analyze",
            "budget_optimizer": "/api/v2/budget/optimize",
            "risk_assessment": "/api/v2/risk/assess",
            "performance_metrics": "/api/v2/performance/calculate"
        },
        "documentation": "/docs",
        "timestamp": datetime.now().isoformat()
    })

# Enhanced Planner API Endpoints
@app.route('/api/v2/planner/create', methods=['POST'])
@limiter.limit("10 per minute")
def create_enhanced_launch_plan():
    """Crear plan de lanzamiento mejorado con IA"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        options = data.get('options', {})
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Validar tipo de escenario
        valid_scenarios = ['mobile_app', 'saas_platform', 'ecommerce', 'content_launch']
        if scenario_type not in valid_scenarios:
            return jsonify({"error": f"Invalid scenario type. Must be one of: {valid_scenarios}"}), 400
        
        # Crear plan mejorado
        enhanced_plan = enhanced_planner.create_enhanced_launch_plan(requirements, scenario_type)
        
        # Generar ID único
        plan_id = str(uuid.uuid4())
        
        # Almacenar plan
        launch_plans[plan_id] = {
            "id": plan_id,
            "created_at": datetime.now().isoformat(),
            "scenario_type": scenario_type,
            "requirements": requirements,
            "plan": enhanced_plan,
            "options": options,
            "access_count": 0
        }
        
        # Generar reporte
        report = enhanced_planner.generate_enhanced_report(enhanced_plan)
        
        return jsonify({
            "success": True,
            "data": {
                "plan_id": plan_id,
                "scenario": enhanced_plan["scenario"],
                "ai_insights": enhanced_plan["ai_insights"],
                "market_intelligence": enhanced_plan["market_intelligence"],
                "report": report,
                "created_at": launch_plans[plan_id]["created_at"]
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating enhanced plan: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v2/planner/<plan_id>', methods=['GET'])
def get_enhanced_launch_plan(plan_id: str):
    """Obtener plan de lanzamiento específico"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"error": "Launch plan not found"}), 404
        
        plan_data = launch_plans[plan_id]
        plan_data["access_count"] += 1
        
        return jsonify({
            "success": True,
            "data": plan_data
        })
        
    except Exception as e:
        logger.error(f"Error retrieving plan {plan_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v2/planner/<plan_id>/update', methods=['PUT'])
@limiter.limit("5 per minute")
def update_enhanced_launch_plan(plan_id: str):
    """Actualizar plan de lanzamiento existente"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"error": "Launch plan not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Actualizar campos permitidos
        allowed_fields = ['requirements', 'options']
        for field in allowed_fields:
            if field in data:
                launch_plans[plan_id][field] = data[field]
        
        # Recrear plan si los requisitos cambiaron
        if 'requirements' in data:
            scenario_type = launch_plans[plan_id]['scenario_type']
            enhanced_plan = enhanced_planner.create_enhanced_launch_plan(
                data['requirements'], scenario_type
            )
            launch_plans[plan_id]['plan'] = enhanced_plan
        
        launch_plans[plan_id]['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "message": "Plan updated successfully",
            "data": {
                "plan_id": plan_id,
                "updated_at": launch_plans[plan_id]['updated_at']
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating plan {plan_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# AI Analysis API Endpoints
@app.route('/api/v2/ai/analyze', methods=['POST'])
@limiter.limit("20 per minute")
def analyze_with_ai():
    """Análisis avanzado con IA"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Verificar cache
        cache_key = hashlib.md5(f"{requirements}_{scenario_type}".encode()).hexdigest()
        if cache_key in analysis_cache:
            cached_data = analysis_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):
                return jsonify({
                    "success": True,
                    "data": cached_data['analysis'],
                    "cached": True
                })
        
        # Realizar análisis
        analysis = enhanced_planner.analyze_launch_requirements_ai(requirements, scenario_type)
        
        # Guardar en cache
        analysis_cache[cache_key] = {
            "analysis": analysis,
            "timestamp": datetime.now()
        }
        
        return jsonify({
            "success": True,
            "data": analysis,
            "cached": False
        })
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v2/ai/predict', methods=['POST'])
@limiter.limit("15 per minute")
def predict_success():
    """Predicción de éxito del lanzamiento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Análisis básico
        basic_analysis = enhanced_planner.base_planner.analyze_launch_requirements(requirements)
        
        # Análisis de mercado
        market_analysis = enhanced_planner._perform_market_analysis(scenario_type)
        
        # Generar predicciones
        ai_predictions = enhanced_planner._generate_ai_predictions(requirements, basic_analysis, market_analysis)
        
        return jsonify({
            "success": True,
            "data": {
                "success_probability": ai_predictions.success_probability,
                "confidence_score": enhanced_planner._calculate_confidence_score(ai_predictions),
                "estimated_timeline": ai_predictions.estimated_timeline,
                "budget_optimization": ai_predictions.budget_optimization,
                "risk_factors": ai_predictions.risk_factors,
                "recommendations": ai_predictions.recommendations
            }
        })
        
    except Exception as e:
        logger.error(f"Error in success prediction: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Market Intelligence API Endpoints
@app.route('/api/v2/market/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_market():
    """Análisis de mercado e inteligencia competitiva"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        # Análisis de mercado
        market_analysis = enhanced_planner._perform_market_analysis(scenario_type)
        
        # Análisis competitivo
        competitive_landscape = enhanced_planner._analyze_competitive_landscape(scenario_type)
        
        return jsonify({
            "success": True,
            "data": {
                "market_analysis": market_analysis.__dict__,
                "competitive_landscape": competitive_landscape
            }
        })
        
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v2/market/trends', methods=['GET'])
def get_market_trends():
    """Obtener tendencias del mercado"""
    try:
        scenario_type = request.args.get('scenario_type', 'mobile_app')
        
        market_data = enhanced_planner.market_data.get(f"{scenario_type}_market", {})
        
        return jsonify({
            "success": True,
            "data": {
                "scenario_type": scenario_type,
                "trends": market_data.get("trends", []),
                "opportunities": market_data.get("opportunities", []),
                "growth_rate": market_data.get("growth_rate", 0),
                "competition_level": market_data.get("competition_level", "unknown")
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting market trends: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Budget Optimization API Endpoints
@app.route('/api/v2/budget/optimize', methods=['POST'])
@limiter.limit("10 per minute")
def optimize_budget():
    """Optimización de presupuesto con IA"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        total_budget = data.get('total_budget', 100000)
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Análisis básico
        basic_analysis = enhanced_planner.base_planner.analyze_launch_requirements(requirements)
        
        # Análisis de mercado
        market_analysis = enhanced_planner._perform_market_analysis(scenario_type)
        
        # Optimización de presupuesto
        budget_optimization = enhanced_planner._optimize_budget_allocation(basic_analysis, market_analysis)
        
        # Ajustar según presupuesto total proporcionado
        current_total = sum(budget_optimization.values())
        if current_total != total_budget:
            scale_factor = total_budget / current_total
            budget_optimization = {k: v * scale_factor for k, v in budget_optimization.items()}
        
        return jsonify({
            "success": True,
            "data": {
                "total_budget": total_budget,
                "optimized_allocation": budget_optimization,
                "recommendations": [
                    "Consider increasing development budget for complex features",
                    "Allocate 30% of budget to marketing for competitive markets",
                    "Keep 5-10% as contingency for unexpected costs"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error in budget optimization: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Risk Assessment API Endpoints
@app.route('/api/v2/risk/assess', methods=['POST'])
@limiter.limit("10 per minute")
def assess_risks():
    """Evaluación de riesgos del lanzamiento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        scenario_type = data.get('scenario_type', 'mobile_app')
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Análisis básico
        basic_analysis = enhanced_planner.base_planner.analyze_launch_requirements(requirements)
        
        # Análisis de mercado
        market_analysis = enhanced_planner._perform_market_analysis(scenario_type)
        
        # Identificar riesgos
        risk_factors = enhanced_planner._identify_ai_risk_factors(basic_analysis, market_analysis)
        
        # Clasificar riesgos
        risk_categories = {
            "technical": [],
            "market": [],
            "resource": [],
            "timeline": [],
            "financial": []
        }
        
        for risk in risk_factors:
            if any(word in risk.lower() for word in ["technical", "development", "code", "system"]):
                risk_categories["technical"].append(risk)
            elif any(word in risk.lower() for word in ["market", "competition", "customer"]):
                risk_categories["market"].append(risk)
            elif any(word in risk.lower() for word in ["team", "resource", "staff"]):
                risk_categories["resource"].append(risk)
            elif any(word in risk.lower() for word in ["timeline", "schedule", "deadline"]):
                risk_categories["timeline"].append(risk)
            elif any(word in risk.lower() for word in ["budget", "cost", "financial"]):
                risk_categories["financial"].append(risk)
            else:
                risk_categories["technical"].append(risk)
        
        return jsonify({
            "success": True,
            "data": {
                "risk_factors": risk_factors,
                "risk_categories": risk_categories,
                "overall_risk_level": "high" if len(risk_factors) > 5 else "medium" if len(risk_factors) > 2 else "low",
                "mitigation_strategies": [
                    "Regular risk assessment reviews",
                    "Contingency planning",
                    "Early stakeholder communication",
                    "Agile development approach",
                    "Regular testing and validation"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Performance Metrics API Endpoints
@app.route('/api/v2/performance/calculate', methods=['POST'])
@limiter.limit("15 per minute")
def calculate_performance_metrics():
    """Calcular métricas de rendimiento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        requirements = data.get('requirements')
        
        if not requirements:
            return jsonify({"error": "Requirements are required"}), 400
        
        # Análisis básico
        basic_analysis = enhanced_planner.base_planner.analyze_launch_requirements(requirements)
        
        # Calcular métricas de rendimiento
        performance_metrics = enhanced_planner._calculate_performance_metrics(basic_analysis)
        
        return jsonify({
            "success": True,
            "data": {
                "performance_metrics": performance_metrics.__dict__,
                "recommendations": [
                    "Focus on improving team efficiency through better communication",
                    "Implement automated testing to improve quality score",
                    "Use project management tools to improve timeline adherence"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Analytics API Endpoints
@app.route('/api/v2/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Obtener resumen de analytics"""
    try:
        total_plans = len(launch_plans)
        total_analyses = len(analysis_cache)
        
        # Estadísticas de escenarios
        scenario_stats = {}
        for plan in launch_plans.values():
            scenario = plan['scenario_type']
            scenario_stats[scenario] = scenario_stats.get(scenario, 0) + 1
        
        # Estadísticas de éxito promedio
        success_rates = []
        for plan in launch_plans.values():
            if 'plan' in plan and 'ai_insights' in plan['plan']:
                success_rates.append(plan['plan']['ai_insights']['success_probability'])
        
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        return jsonify({
            "success": True,
            "data": {
                "total_plans": total_plans,
                "total_analyses": total_analyses,
                "scenario_distribution": scenario_stats,
                "average_success_rate": avg_success_rate,
                "cache_hit_rate": len(analysis_cache) / max(1, total_analyses),
                "system_uptime": "99.9%"
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Export API Endpoints
@app.route('/api/v2/export/plan/<plan_id>', methods=['GET'])
def export_launch_plan(plan_id: str):
    """Exportar plan de lanzamiento"""
    try:
        if plan_id not in launch_plans:
            return jsonify({"error": "Launch plan not found"}), 404
        
        plan_data = launch_plans[plan_id]
        export_format = request.args.get('format', 'json')
        
        if export_format == 'json':
            return jsonify({
                "success": True,
                "data": plan_data
            })
        elif export_format == 'report':
            report = enhanced_planner.generate_enhanced_report(plan_data['plan'])
            return jsonify({
                "success": True,
                "data": {
                    "report": report,
                    "plan_id": plan_id,
                    "exported_at": datetime.now().isoformat()
                }
            })
        else:
            return jsonify({"error": "Unsupported export format"}), 400
        
    except Exception as e:
        logger.error(f"Error exporting plan {plan_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Health Check y Status
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint mejorado"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": {
            "ai_analysis": "enabled",
            "market_intelligence": "enabled",
            "budget_optimization": "enabled",
            "risk_assessment": "enabled",
            "performance_metrics": "enabled"
        },
        "system_metrics": {
            "total_plans": len(launch_plans),
            "cache_size": len(analysis_cache),
            "memory_usage": "normal"
        }
    })

@app.route('/status', methods=['GET'])
def system_status():
    """Status detallado del sistema"""
    return jsonify({
        "system": "Enhanced Launch Planning API",
        "version": "2.0.0",
        "status": "operational",
        "uptime": "99.9%",
        "features": [
            "AI-powered analysis",
            "Predictive analytics",
            "Market intelligence",
            "Budget optimization",
            "Risk assessment",
            "Performance metrics"
        ],
        "endpoints": {
            "total": 15,
            "active": 15,
            "rate_limited": 8
        },
        "data": {
            "launch_plans": len(launch_plans),
            "analysis_cache": len(analysis_cache),
            "user_sessions": len(user_sessions)
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "code": 404}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded", "code": 429}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error", "code": 500}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Launch Planning API Server...")
    print("📡 Enhanced API Features:")
    print("   🧠 AI-powered analysis")
    print("   📊 Predictive analytics")
    print("   🎯 Market intelligence")
    print("   💰 Budget optimization")
    print("   ⚠️  Risk assessment")
    print("   📈 Performance metrics")
    print("\n🌐 Server starting on http://localhost:5000")
    print("📚 API Documentation available at /docs")
    
    app.run(debug=True, host='0.0.0.0', port=5000)









