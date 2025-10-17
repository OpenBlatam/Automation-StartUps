#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API REST para Campañas de Marketing con IA
==========================================
API completa para gestionar, analizar y simular campañas de marketing con IA.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import os

# Importar módulos locales
from campaign_comparison_tool import CampaignComparisonTool
from roi_calculator import ROICalculator
from industry_report_generator import IndustryReportGenerator
from scenario_simulator import ScenarioSimulator

app = Flask(__name__)
CORS(app)

# Inicializar herramientas
comparison_tool = CampaignComparisonTool()
roi_calculator = ROICalculator()
industry_generator = IndustryReportGenerator()
scenario_simulator = ScenarioSimulator()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud de la API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Obtener todas las campañas con filtros opcionales"""
    try:
        # Parámetros de filtro
        category = request.args.get('category')
        vertical = request.args.get('vertical')
        technology = request.args.get('technology')
        complexity = request.args.get('complexity')
        priority = request.args.get('priority')
        min_budget = request.args.get('min_budget', type=float)
        max_budget = request.args.get('max_budget', type=float)
        min_roi = request.args.get('min_roi', type=float)
        min_success_prob = request.args.get('min_success_prob', type=float)
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)
        
        # Aplicar filtros
        campaigns = comparison_tool.df.copy()
        
        if category:
            campaigns = campaigns[campaigns['category'] == category]
        if vertical:
            campaigns = campaigns[campaigns['vertical'] == vertical]
        if technology:
            campaigns = campaigns[campaigns['technology'] == technology]
        if complexity:
            campaigns = campaigns[campaigns['complexity'] == complexity]
        if priority:
            campaigns = campaigns[campaigns['priority'] == priority]
        if min_budget:
            campaigns = campaigns[campaigns['budget'].apply(lambda x: x['amount']) >= min_budget]
        if max_budget:
            campaigns = campaigns[campaigns['budget'].apply(lambda x: x['amount']) <= max_budget]
        if min_roi:
            campaigns = campaigns[campaigns['metrics'].apply(lambda x: x['return_on_ad_spend']) >= min_roi]
        if min_success_prob:
            campaigns = campaigns[campaigns['success_probability'] >= min_success_prob]
        
        # Paginación
        total = len(campaigns)
        campaigns = campaigns.iloc[offset:offset + limit]
        
        return jsonify({
            'campaigns': campaigns.to_dict('records'),
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Obtener una campaña específica por ID"""
    try:
        campaign = next((c for c in comparison_tool.campaigns if c['id'] == campaign_id), None)
        if not campaign:
            return jsonify({'error': 'Campaña no encontrada'}), 404
        
        return jsonify(campaign)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/compare', methods=['POST'])
def compare_campaigns():
    """Comparar múltiples campañas"""
    try:
        data = request.get_json()
        campaign_ids = data.get('campaign_ids', [])
        
        if not campaign_ids:
            return jsonify({'error': 'Se requieren IDs de campañas'}), 400
        
        result = comparison_tool.compare_campaigns(campaign_ids)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns/<int:campaign_id>/similar', methods=['GET'])
def get_similar_campaigns(campaign_id):
    """Obtener campañas similares a una dada"""
    try:
        limit = request.args.get('limit', type=int, default=5)
        similar = comparison_tool.find_similar_campaigns(campaign_id, limit)
        
        return jsonify({
            'campaign_id': campaign_id,
            'similar_campaigns': similar
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/roi/simulate', methods=['POST'])
def simulate_roi():
    """Simular ROI para una campaña"""
    try:
        data = request.get_json()
        campaign_id = data.get('campaign_id')
        scenario_params = data.get('scenario_params', {})
        
        if not campaign_id:
            return jsonify({'error': 'Se requiere campaign_id'}), 400
        
        result = roi_calculator.simulate_scenario(campaign_id, scenario_params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/roi/compare-scenarios', methods=['POST'])
def compare_roi_scenarios():
    """Comparar múltiples escenarios de ROI"""
    try:
        data = request.get_json()
        campaign_id = data.get('campaign_id')
        scenarios = data.get('scenarios', [])
        
        if not campaign_id or not scenarios:
            return jsonify({'error': 'Se requieren campaign_id y scenarios'}), 400
        
        result = roi_calculator.compare_scenarios(campaign_id, scenarios)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/industry/<industry>/report', methods=['GET'])
def get_industry_report(industry):
    """Obtener reporte de una industria específica"""
    try:
        result = industry_generator.generate_industry_report(industry)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/industry/reports', methods=['GET'])
def get_all_industry_reports():
    """Obtener reportes de todas las industrias"""
    try:
        reports = industry_generator.generate_all_industry_reports()
        return jsonify(reports)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios/simulate', methods=['POST'])
def simulate_scenario():
    """Simular un escenario de mercado"""
    try:
        data = request.get_json()
        campaign_id = data.get('campaign_id')
        scenario_name = data.get('scenario_name')
        custom_params = data.get('custom_params', {})
        
        if not campaign_id or not scenario_name:
            return jsonify({'error': 'Se requieren campaign_id y scenario_name'}), 400
        
        result = scenario_simulator.simulate_campaign_scenario(campaign_id, scenario_name, custom_params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios/portfolio', methods=['POST'])
def simulate_portfolio_scenario():
    """Simular escenario para un portafolio de campañas"""
    try:
        data = request.get_json()
        campaign_ids = data.get('campaign_ids', [])
        scenario_name = data.get('scenario_name')
        
        if not campaign_ids or not scenario_name:
            return jsonify({'error': 'Se requieren campaign_ids y scenario_name'}), 400
        
        result = scenario_simulator.simulate_portfolio_scenario(campaign_ids, scenario_name)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Obtener resumen analítico general"""
    try:
        df = comparison_tool.df
        
        summary = {
            'total_campaigns': len(df),
            'total_budget': df['budget'].apply(lambda x: x['amount']).sum(),
            'average_budget': df['budget'].apply(lambda x: x['amount']).mean(),
            'average_roi': df['metrics'].apply(lambda x: x['return_on_ad_spend']).mean(),
            'average_success_probability': df['success_probability'].mean(),
            'by_category': df['category'].value_counts().to_dict(),
            'by_vertical': df['vertical'].value_counts().to_dict(),
            'by_technology': df['technology'].value_counts().to_dict(),
            'by_complexity': df['complexity'].value_counts().to_dict(),
            'by_priority': df['priority'].value_counts().to_dict()
        }
        
        return jsonify(summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Obtener recomendaciones personalizadas"""
    try:
        data = request.get_json()
        budget_range = data.get('budget_range')
        complexity = data.get('complexity')
        vertical = data.get('vertical')
        objectives = data.get('objectives', [])
        
        recommendations = comparison_tool.get_recommendations(
            budget_range=budget_range,
            complexity=complexity,
            vertical=vertical,
            objectives=objectives
        )
        
        return jsonify({
            'recommendations': recommendations.to_dict('records'),
            'total': len(recommendations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/campaigns', methods=['GET'])
def export_campaigns():
    """Exportar campañas en formato CSV"""
    try:
        # Aplicar filtros si se proporcionan
        df = comparison_tool.df.copy()
        
        category = request.args.get('category')
        vertical = request.args.get('vertical')
        
        if category:
            df = df[df['category'] == category]
        if vertical:
            df = df[df['vertical'] == vertical]
        
        # Preparar datos para CSV
        csv_data = []
        for _, campaign in df.iterrows():
            csv_data.append({
                'ID': campaign['id'],
                'Nombre': campaign['name'],
                'Categoría': campaign['category'],
                'Tecnología': campaign['technology'],
                'Canal': campaign['channel'],
                'Objetivo': campaign['objective'],
                'Vertical': campaign['vertical'],
                'Presupuesto': campaign['budget']['amount'],
                'Probabilidad_Éxito': campaign['success_probability'],
                'Complejidad': campaign['complexity'],
                'Prioridad': campaign['priority'],
                'ROI': campaign['metrics']['return_on_ad_spend'],
                'Tasa_Conversión': campaign['metrics']['conversion_rate'],
                'CPA': campaign['metrics']['cost_per_acquisition']
            })
        
        return jsonify({
            'data': csv_data,
            'total': len(csv_data),
            'format': 'csv_ready'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Obtener métricas para dashboard"""
    try:
        df = comparison_tool.df
        
        # Métricas generales
        total_campaigns = len(df)
        total_budget = df['budget'].apply(lambda x: x['amount']).sum()
        avg_roi = df['metrics'].apply(lambda x: x['return_on_ad_spend']).mean()
        avg_success = df['success_probability'].mean()
        
        # Distribución por categoría
        category_dist = df['category'].value_counts().to_dict()
        
        # Distribución por complejidad
        complexity_dist = df['complexity'].value_counts().to_dict()
        
        # Top 10 campañas por ROI
        top_roi = df.nlargest(10, 'metrics').apply(lambda x: x['return_on_ad_spend']).to_dict()
        
        # Análisis de presupuesto
        budget_analysis = {
            'under_25k': (df['budget'].apply(lambda x: x['amount']) < 25000).sum(),
            '25k_to_100k': ((df['budget'].apply(lambda x: x['amount']) >= 25000) & 
                           (df['budget'].apply(lambda x: x['amount']) < 100000)).sum(),
            'over_100k': (df['budget'].apply(lambda x: x['amount']) >= 100000).sum()
        }
        
        return jsonify({
            'summary': {
                'total_campaigns': total_campaigns,
                'total_budget': total_budget,
                'average_roi': avg_roi,
                'average_success_probability': avg_success
            },
            'distributions': {
                'by_category': category_dist,
                'by_complexity': complexity_dist,
                'by_budget': budget_analysis
            },
            'top_performers': {
                'by_roi': top_roi
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Manejar errores 404"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores 500"""
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    print("=== API DE CAMPAÑAS DE MARKETING CON IA ===")
    print("Iniciando servidor...")
    print("Endpoints disponibles:")
    print("- GET /api/health - Estado de la API")
    print("- GET /api/campaigns - Listar campañas")
    print("- GET /api/campaigns/<id> - Obtener campaña específica")
    print("- POST /api/campaigns/compare - Comparar campañas")
    print("- GET /api/campaigns/<id>/similar - Campañas similares")
    print("- POST /api/roi/simulate - Simular ROI")
    print("- POST /api/roi/compare-scenarios - Comparar escenarios ROI")
    print("- GET /api/industry/<industry>/report - Reporte de industria")
    print("- GET /api/industry/reports - Todos los reportes")
    print("- POST /api/scenarios/simulate - Simular escenario")
    print("- POST /api/scenarios/portfolio - Simular portafolio")
    print("- GET /api/analytics/summary - Resumen analítico")
    print("- POST /api/recommendations - Recomendaciones")
    print("- GET /api/export/campaigns - Exportar campañas")
    print("- GET /api/dashboard/metrics - Métricas de dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


