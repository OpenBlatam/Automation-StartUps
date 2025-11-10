"""
Dashboard API para Leads
========================

API que proporciona endpoints para dashboard y visualización de datos del pipeline.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, List
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

app = Flask(__name__)


class LeadDashboardAPI:
    """API para dashboard de leads"""
    
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Args:
            db_connection_string: String de conexión PostgreSQL
        """
        self.db_conn_str = db_connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/sales_db"
        )
    
    def get_db_connection(self):
        """Obtiene conexión a la base de datos"""
        return psycopg2.connect(self.db_conn_str)
    
    def get_dashboard_summary(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene resumen del dashboard"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Pipeline summary
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE stage = 'qualified') AS qualified,
                        COUNT(*) FILTER (WHERE stage = 'contacted') AS contacted,
                        COUNT(*) FILTER (WHERE stage = 'meeting_scheduled') AS meeting_scheduled,
                        COUNT(*) FILTER (WHERE stage = 'proposal_sent') AS proposal_sent,
                        COUNT(*) FILTER (WHERE stage = 'negotiating') AS negotiating,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS closed_won,
                        COUNT(*) FILTER (WHERE stage = 'closed_lost') AS closed_lost,
                        AVG(score) AS avg_score,
                        SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_lost')) AS pipeline_value,
                        COUNT(*) FILTER (WHERE assigned_to IS NULL) AS unassigned
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                """, (days,))
                
                summary = dict(cur.fetchone())
                
                # Conversion rate
                total = summary.get('qualified', 0) + summary.get('contacted', 0) + summary.get('meeting_scheduled', 0)
                won = summary.get('closed_won', 0)
                summary['conversion_rate'] = round((won / total * 100) if total > 0 else 0, 2)
                
                return summary
    
    def get_funnel_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene datos del funnel"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        stage,
                        COUNT(*) as count,
                        SUM(estimated_value) as value,
                        AVG(score) as avg_score
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY stage
                    ORDER BY 
                        CASE stage
                            WHEN 'qualified' THEN 1
                            WHEN 'contacted' THEN 2
                            WHEN 'meeting_scheduled' THEN 3
                            WHEN 'proposal_sent' THEN 4
                            WHEN 'negotiating' THEN 5
                            WHEN 'closed_won' THEN 6
                            WHEN 'closed_lost' THEN 7
                        END
                """, (days,))
                
                return [dict(row) for row in cur.fetchall()]
    
    def get_recent_leads(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtiene leads recientes"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        lead_ext_id,
                        email,
                        first_name,
                        last_name,
                        score,
                        priority,
                        stage,
                        assigned_to,
                        qualified_at
                    FROM sales_pipeline
                    WHERE stage NOT IN ('closed_won', 'closed_lost')
                    ORDER BY qualified_at DESC
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cur.fetchall()]
    
    def get_top_performers(self, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene top performers"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        assigned_to,
                        COUNT(*) as total_leads,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') as won,
                        ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'closed_won') / COUNT(*), 2) as conversion_rate,
                        SUM(estimated_value) FILTER (WHERE stage = 'closed_won') as total_value
                    FROM sales_pipeline
                    WHERE assigned_to IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY assigned_to
                    ORDER BY won DESC
                    LIMIT 10
                """, (days,))
                
                return [dict(row) for row in cur.fetchall()]
    
    def get_source_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Obtiene performance por fuente"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        source,
                        COUNT(*) as leads,
                        AVG(score) as avg_score,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') as won,
                        ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'closed_won') / COUNT(*), 2) as conversion_rate
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY source
                    ORDER BY leads DESC
                """, (days,))
                
                return [dict(row) for row in cur.fetchall()]


# Inicializar API
dashboard_api = LeadDashboardAPI()


@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Endpoint para resumen del dashboard"""
    try:
        days = int(request.args.get('days', 30))
        summary = dashboard_api.get_dashboard_summary(days)
        
        return jsonify({
            "success": True,
            "summary": summary
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/funnel', methods=['GET'])
def dashboard_funnel():
    """Endpoint para datos del funnel"""
    try:
        days = int(request.args.get('days', 30))
        funnel = dashboard_api.get_funnel_data(days)
        
        return jsonify({
            "success": True,
            "funnel": funnel
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo funnel: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/recent-leads', methods=['GET'])
def dashboard_recent_leads():
    """Endpoint para leads recientes"""
    try:
        limit = int(request.args.get('limit', 20))
        leads = dashboard_api.get_recent_leads(limit)
        
        return jsonify({
            "success": True,
            "leads": leads
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo leads recientes: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/top-performers', methods=['GET'])
def dashboard_top_performers():
    """Endpoint para top performers"""
    try:
        days = int(request.args.get('days', 30))
        performers = dashboard_api.get_top_performers(days)
        
        return jsonify({
            "success": True,
            "performers": performers
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo top performers: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/source-performance', methods=['GET'])
def dashboard_source_performance():
    """Endpoint para performance por fuente"""
    try:
        days = int(request.args.get('days', 30))
        performance = dashboard_api.get_source_performance(days)
        
        return jsonify({
            "success": True,
            "performance": performance
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo performance: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


if __name__ == '__main__':
    port = int(os.getenv("DASHBOARD_API_PORT", 5003))
    debug = os.getenv("DASHBOARD_API_DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando Dashboard API en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

