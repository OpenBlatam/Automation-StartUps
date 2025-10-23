#!/usr/bin/env python3
"""
Competitive Pricing Analysis API Server
=======================================

Flask-based API server for the competitive pricing analysis system.
Provides REST endpoints for data collection, analysis, and dashboard integration.

Features:
- RESTful API endpoints
- Real-time data collection
- Competitive analysis
- Dashboard data serving
- Export functionality
- Authentication and rate limiting
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import asyncio
from threading import Thread
import yaml
from competitive_pricing_analyzer import CompetitivePricingAnalyzer
import io
import base64
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Global analyzer instance
analyzer = None

def initialize_analyzer():
    """Initialize the competitive pricing analyzer"""
    global analyzer
    try:
        analyzer = CompetitivePricingAnalyzer()
        logger.info("Competitive Pricing Analyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        analyzer = None

@app.route('/')
def index():
    """Serve the main dashboard"""
    try:
        with open('pricing_dashboard.html', 'r', encoding='utf-8') as f:
            dashboard_html = f.read()
        return dashboard_html
    except FileNotFoundError:
        return jsonify({'error': 'Dashboard file not found'}), 404

@app.route('/api/pricing-analysis', methods=['GET'])
@limiter.limit("10 per minute")
def get_pricing_analysis():
    """Get comprehensive pricing analysis data"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        # Get latest pricing data
        pricing_data = analyzer._get_latest_pricing_data()
        
        # Get latest insights
        insights = analyzer._get_latest_insights()
        
        # Generate report
        report = analyzer.generate_pricing_report()
        
        # Convert DataFrame to JSON-serializable format
        pricing_data_json = pricing_data.to_dict('records') if not pricing_data.empty else []
        
        # Convert insights to JSON-serializable format
        insights_json = [
            {
                'insight_type': insight.insight_type,
                'description': insight.description,
                'impact_score': insight.impact_score,
                'recommendation': insight.recommendation,
                'confidence': insight.confidence,
                'supporting_data': insight.supporting_data
            }
            for insight in insights
        ]
        
        response_data = {
            'summary_statistics': report['summary_statistics'],
            'insights': insights_json,
            'pricing_data': pricing_data_json,
            'recommendations': report['recommendations'],
            'data_quality': report['data_quality'],
            'generated_at': report['generated_at']
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_pricing_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collect-data', methods=['POST'])
@limiter.limit("5 per hour")
def collect_data():
    """Trigger data collection from all sources"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        # Run data collection in background
        def run_collection():
            try:
                asyncio.run(analyzer.collect_pricing_data())
                logger.info("Data collection completed successfully")
            except Exception as e:
                logger.error(f"Error in data collection: {e}")
        
        thread = Thread(target=run_collection)
        thread.start()
        
        return jsonify({
            'message': 'Data collection started',
            'status': 'running'
        })
        
    except Exception as e:
        logger.error(f"Error in collect_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per hour")
def run_analysis():
    """Run competitive pricing analysis"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        # Run analysis
        insights = analyzer.analyze_pricing_differences()
        
        return jsonify({
            'message': 'Analysis completed',
            'insights_count': len(insights),
            'insights': [
                {
                    'type': insight.insight_type,
                    'description': insight.description,
                    'impact_score': insight.impact_score,
                    'recommendation': insight.recommendation,
                    'confidence': insight.confidence
                }
                for insight in insights
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in run_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['GET'])
@limiter.limit("5 per hour")
def export_data(format):
    """Export pricing analysis data in various formats"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        if format == 'excel':
            filename = analyzer.export_to_excel()
            return send_file(filename, as_attachment=True, download_name=f"pricing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        elif format == 'json':
            report = analyzer.generate_pricing_report()
            return jsonify(report)
        
        elif format == 'csv':
            pricing_data = analyzer._get_latest_pricing_data()
            if pricing_data.empty:
                return jsonify({'error': 'No data available'}), 404
            
            csv_buffer = io.StringIO()
            pricing_data.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            csv_buffer.close()
            
            response = app.response_class(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=pricing_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
            return response
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f"Error in export_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pricing-data', methods=['GET'])
@limiter.limit("20 per minute")
def get_pricing_data():
    """Get raw pricing data with optional filtering"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        # Get query parameters
        product_id = request.args.get('product_id')
        competitor = request.args.get('competitor')
        days = int(request.args.get('days', 30))
        
        # Build query
        query = '''
            SELECT product_id, product_name, competitor, price, currency, date_collected, source
            FROM pricing_data
            WHERE date_collected >= date('now', '-{} days')
        '''.format(days)
        
        params = []
        if product_id:
            query += ' AND product_id = ?'
            params.append(product_id)
        
        if competitor:
            query += ' AND competitor = ?'
            params.append(competitor)
        
        query += ' ORDER BY date_collected DESC'
        
        # Execute query
        conn = sqlite3.connect(analyzer.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return jsonify(df.to_dict('records'))
        
    except Exception as e:
        logger.error(f"Error in get_pricing_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights', methods=['GET'])
@limiter.limit("20 per minute")
def get_insights():
    """Get competitive insights with optional filtering"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        # Get query parameters
        insight_type = request.args.get('type')
        min_impact = float(request.args.get('min_impact', 0))
        days = int(request.args.get('days', 7))
        
        # Build query
        query = '''
            SELECT insight_type, description, impact_score, recommendation, confidence, supporting_data, created_at
            FROM competitive_insights
            WHERE created_at >= date('now', '-{} days')
            AND impact_score >= ?
        '''.format(days)
        
        params = [min_impact]
        
        if insight_type:
            query += ' AND insight_type = ?'
            params.append(insight_type)
        
        query += ' ORDER BY impact_score DESC, confidence DESC'
        
        # Execute query
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insight = {
                'insight_type': row[0],
                'description': row[1],
                'impact_score': row[2],
                'recommendation': row[3],
                'confidence': row[4],
                'supporting_data': json.loads(row[5]) if row[5] else {},
                'created_at': row[6]
            }
            insights.append(insight)
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Error in get_insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-data', methods=['POST'])
@limiter.limit("10 per hour")
def upload_data():
    """Upload pricing data from CSV or JSON file"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and secure_filename(file.filename):
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            if file_extension == 'csv':
                # Process CSV file
                df = pd.read_csv(file)
                
                # Validate required columns
                required_columns = ['product_id', 'product_name', 'competitor', 'price', 'currency']
                if not all(col in df.columns for col in required_columns):
                    return jsonify({'error': f'Missing required columns: {required_columns}'}), 400
                
                # Convert to PricingData objects
                pricing_data_list = []
                for _, row in df.iterrows():
                    from competitive_pricing_analyzer import PricingData, DataSource
                    pricing_data = PricingData(
                        product_id=row['product_id'],
                        product_name=row['product_name'],
                        competitor=row['competitor'],
                        price=float(row['price']),
                        currency=row['currency'],
                        date_collected=datetime.now(),
                        source=DataSource.CSV_IMPORT,
                        additional_data={'uploaded_file': filename}
                    )
                    pricing_data_list.append(pricing_data)
                
                # Store data
                analyzer._store_pricing_data(pricing_data_list)
                
                return jsonify({
                    'message': f'Successfully uploaded {len(pricing_data_list)} records',
                    'records_count': len(pricing_data_list)
                })
            
            elif file_extension == 'json':
                # Process JSON file
                data = json.load(file)
                
                # Validate and process JSON data
                if isinstance(data, list):
                    pricing_data_list = []
                    for item in data:
                        from competitive_pricing_analyzer import PricingData, DataSource
                        pricing_data = PricingData(
                            product_id=item['product_id'],
                            product_name=item['product_name'],
                            competitor=item['competitor'],
                            price=float(item['price']),
                            currency=item['currency'],
                            date_collected=datetime.now(),
                            source=DataSource.MANUAL_INPUT,
                            additional_data={'uploaded_file': filename}
                        )
                        pricing_data_list.append(pricing_data)
                    
                    # Store data
                    analyzer._store_pricing_data(pricing_data_list)
                    
                    return jsonify({
                        'message': f'Successfully uploaded {len(pricing_data_list)} records',
                        'records_count': len(pricing_data_list)
                    })
                else:
                    return jsonify({'error': 'JSON file must contain an array of pricing data'}), 400
            
            else:
                return jsonify({'error': 'Unsupported file format. Please use CSV or JSON.'}), 400
        
        return jsonify({'error': 'Invalid file'}), 400
        
    except Exception as e:
        logger.error(f"Error in upload_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and health check"""
    try:
        status = {
            'status': 'healthy' if analyzer else 'unhealthy',
            'analyzer_initialized': analyzer is not None,
            'database_path': analyzer.db_path if analyzer else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if analyzer:
            # Check database connectivity
            try:
                conn = sqlite3.connect(analyzer.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM pricing_data')
                data_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM competitive_insights')
                insights_count = cursor.fetchone()[0]
                conn.close()
                
                status.update({
                    'database_connected': True,
                    'pricing_data_count': data_count,
                    'insights_count': insights_count
                })
            except Exception as e:
                status.update({
                    'database_connected': False,
                    'database_error': str(e)
                })
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def manage_config():
    """Get or update system configuration"""
    try:
        if request.method == 'GET':
            if not analyzer:
                return jsonify({'error': 'Analyzer not initialized'}), 500
            
            return jsonify(analyzer.config)
        
        elif request.method == 'POST':
            if not analyzer:
                return jsonify({'error': 'Analyzer not initialized'}), 500
            
            new_config = request.get_json()
            if not new_config:
                return jsonify({'error': 'No configuration provided'}), 400
            
            # Update configuration
            analyzer.config.update(new_config)
            
            # Save configuration to file
            with open('pricing_config.yaml', 'w') as f:
                yaml.dump(analyzer.config, f, default_flow_style=False)
            
            return jsonify({
                'message': 'Configuration updated successfully',
                'config': analyzer.config
            })
        
    except Exception as e:
        logger.error(f"Error in manage_config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/competitors', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def manage_competitors():
    """Get or add competitors"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        if request.method == 'GET':
            return jsonify(analyzer.competitors)
        
        elif request.method == 'POST':
            competitor_data = request.get_json()
            if not competitor_data:
                return jsonify({'error': 'No competitor data provided'}), 400
            
            # Add competitor to configuration
            if 'competitors' not in analyzer.config:
                analyzer.config['competitors'] = []
            
            analyzer.config['competitors'].append(competitor_data)
            analyzer.competitors.append(competitor_data['name'])
            
            # Save configuration
            with open('pricing_config.yaml', 'w') as f:
                yaml.dump(analyzer.config, f, default_flow_style=False)
            
            return jsonify({
                'message': 'Competitor added successfully',
                'competitor': competitor_data
            })
        
    except Exception as e:
        logger.error(f"Error in manage_competitors: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def manage_products():
    """Get or add products"""
    try:
        if not analyzer:
            return jsonify({'error': 'Analyzer not initialized'}), 500
        
        if request.method == 'GET':
            return jsonify(analyzer.products)
        
        elif request.method == 'POST':
            product_data = request.get_json()
            if not product_data:
                return jsonify({'error': 'No product data provided'}), 400
            
            # Add product to configuration
            if 'products' not in analyzer.config:
                analyzer.config['products'] = []
            
            analyzer.config['products'].append(product_data)
            analyzer.products.append(product_data['id'])
            
            # Save configuration
            with open('pricing_config.yaml', 'w') as f:
                yaml.dump(analyzer.config, f, default_flow_style=False)
            
            return jsonify({
                'message': 'Product added successfully',
                'product': product_data
            })
        
    except Exception as e:
        logger.error(f"Error in manage_products: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(404)
def not_found_handler(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found.'
    }), 404

@app.errorhandler(500)
def internal_error_handler(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred.'
    }), 500

def run_scheduled_tasks():
    """Run scheduled tasks for data collection and analysis"""
    import schedule
    import time
    
    def collect_data_task():
        if analyzer:
            try:
                asyncio.run(analyzer.collect_pricing_data())
                logger.info("Scheduled data collection completed")
            except Exception as e:
                logger.error(f"Error in scheduled data collection: {e}")
    
    def analyze_data_task():
        if analyzer:
            try:
                analyzer.analyze_pricing_differences()
                logger.info("Scheduled analysis completed")
            except Exception as e:
                logger.error(f"Error in scheduled analysis: {e}")
    
    # Schedule tasks
    schedule.every().day.at("09:00").do(collect_data_task)
    schedule.every().day.at("17:00").do(analyze_data_task)
    
    # Run scheduler in background
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    """Main function to run the API server"""
    # Initialize analyzer
    initialize_analyzer()
    
    # Start scheduled tasks in background
    scheduler_thread = Thread(target=run_scheduled_tasks, daemon=True)
    scheduler_thread.start()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main()






