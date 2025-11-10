"""
API REST para Gestión de Leads
================================

API completa para gestionar leads, consultar pipeline, y actualizar estados.
"""
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, List
import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

logger = logging.getLogger(__name__)

app = Flask(__name__)


class LeadAPI:
    """API REST para gestión de leads"""
    
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
    
    def get_leads(
        self,
        limit: int = 50,
        offset: int = 0,
        stage: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: Optional[str] = None,
        min_score: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene lista de leads con filtros"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        p.id,
                        p.lead_ext_id,
                        p.email,
                        p.first_name,
                        p.last_name,
                        p.phone,
                        p.score,
                        p.priority,
                        p.stage,
                        p.assigned_to,
                        p.estimated_value,
                        p.probability_pct,
                        p.qualified_at,
                        p.next_followup_at,
                        p.created_at,
                        p.updated_at,
                        p.metadata
                    FROM sales_pipeline p
                    WHERE 1=1
                """
                params = []
                
                if stage:
                    query += " AND p.stage = %s"
                    params.append(stage)
                
                if assigned_to:
                    query += " AND p.assigned_to = %s"
                    params.append(assigned_to)
                
                if priority:
                    query += " AND p.priority = %s"
                    params.append(priority)
                
                if min_score:
                    query += " AND p.score >= %s"
                    params.append(min_score)
                
                query += " ORDER BY p.priority DESC, p.score DESC, p.qualified_at DESC"
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
    
    def get_lead_by_id(self, lead_ext_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un lead por ID"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        p.id,
                        p.lead_ext_id,
                        p.email,
                        p.first_name,
                        p.last_name,
                        p.phone,
                        p.score,
                        p.priority,
                        p.stage,
                        p.assigned_to,
                        p.estimated_value,
                        p.probability_pct,
                        p.qualified_at,
                        p.first_contact_at,
                        p.last_contact_at,
                        p.next_followup_at,
                        p.notes,
                        p.metadata,
                        p.created_at,
                        p.updated_at
                    FROM sales_pipeline p
                    WHERE p.lead_ext_id = %s
                """, (lead_ext_id,))
                
                result = cur.fetchone()
                return dict(result) if result else None
    
    def update_lead_stage(
        self,
        lead_ext_id: str,
        stage: str,
        notes: Optional[str] = None
    ) -> bool:
        """Actualiza el stage de un lead"""
        valid_stages = [
            "qualified", "contacted", "meeting_scheduled",
            "proposal_sent", "negotiating", "closed_won", "closed_lost"
        ]
        
        if stage not in valid_stages:
            raise ValueError(f"Stage inválido. Debe ser uno de: {', '.join(valid_stages)}")
        
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                update_fields = ["stage = %s", "updated_at = NOW()"]
                params = [stage]
                
                if notes:
                    update_fields.append("notes = COALESCE(notes || '\n' || %s, %s)")
                    params.extend([notes, notes])
                
                # Actualizar timestamps según stage
                if stage == "contacted" and notes:
                    update_fields.append("first_contact_at = COALESCE(first_contact_at, NOW())")
                    update_fields.append("last_contact_at = NOW()")
                
                cur.execute(f"""
                    UPDATE sales_pipeline
                    SET {', '.join(update_fields)}
                    WHERE lead_ext_id = %s
                """, params + [lead_ext_id])
                
                conn.commit()
                return cur.rowcount > 0
    
    def assign_lead(self, lead_ext_id: str, assigned_to: str) -> bool:
        """Asigna un lead a un vendedor"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sales_pipeline
                    SET assigned_to = %s,
                        updated_at = NOW()
                    WHERE lead_ext_id = %s
                """, (assigned_to, lead_ext_id))
                
                conn.commit()
                return cur.rowcount > 0
    
    def get_lead_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del pipeline"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE stage = 'qualified') AS qualified_count,
                        COUNT(*) FILTER (WHERE stage = 'contacted') AS contacted_count,
                        COUNT(*) FILTER (WHERE stage = 'meeting_scheduled') AS meeting_scheduled_count,
                        COUNT(*) FILTER (WHERE stage = 'proposal_sent') AS proposal_sent_count,
                        COUNT(*) FILTER (WHERE stage = 'negotiating') AS negotiating_count,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS closed_won_count,
                        COUNT(*) FILTER (WHERE stage = 'closed_lost') AS closed_lost_count,
                        COUNT(*) FILTER (WHERE assigned_to IS NULL) AS unassigned_count,
                        AVG(score) AS avg_score,
                        SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_lost')) AS total_pipeline_value
                    FROM sales_pipeline
                    WHERE stage NOT IN ('closed_won', 'closed_lost')
                """)
                
                result = cur.fetchone()
                return dict(result) if result else {}


# Inicializar API
api = LeadAPI()


@app.route('/api/leads', methods=['GET'])
def get_leads_endpoint():
    """Endpoint para obtener leads"""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        stage = request.args.get('stage')
        assigned_to = request.args.get('assigned_to')
        priority = request.args.get('priority')
        min_score = int(request.args.get('min_score')) if request.args.get('min_score') else None
        
        leads = api.get_leads(
            limit=limit,
            offset=offset,
            stage=stage,
            assigned_to=assigned_to,
            priority=priority,
            min_score=min_score
        )
        
        return jsonify({
            "success": True,
            "count": len(leads),
            "leads": leads
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo leads: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/leads/<lead_ext_id>', methods=['GET'])
def get_lead_endpoint(lead_ext_id: str):
    """Endpoint para obtener un lead específico"""
    try:
        lead = api.get_lead_by_id(lead_ext_id)
        
        if not lead:
            return jsonify({"error": "Lead no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "lead": lead
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo lead: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/leads/<lead_ext_id>/stage', methods=['PUT'])
def update_stage_endpoint(lead_ext_id: str):
    """Endpoint para actualizar stage de un lead"""
    try:
        data = request.get_json() or {}
        stage = data.get('stage')
        notes = data.get('notes')
        
        if not stage:
            return jsonify({"error": "stage es requerido"}), 400
        
        success = api.update_lead_stage(lead_ext_id, stage, notes)
        
        if not success:
            return jsonify({"error": "Lead no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "message": "Stage actualizado correctamente"
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando stage: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/leads/<lead_ext_id>/assign', methods=['PUT'])
def assign_lead_endpoint(lead_ext_id: str):
    """Endpoint para asignar un lead"""
    try:
        data = request.get_json() or {}
        assigned_to = data.get('assigned_to')
        
        if not assigned_to:
            return jsonify({"error": "assigned_to es requerido"}), 400
        
        success = api.assign_lead(lead_ext_id, assigned_to)
        
        if not success:
            return jsonify({"error": "Lead no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "message": "Lead asignado correctamente"
        }), 200
        
    except Exception as e:
        logger.error(f"Error asignando lead: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/leads/statistics', methods=['GET'])
def get_statistics_endpoint():
    """Endpoint para obtener estadísticas del pipeline"""
    try:
        stats = api.get_lead_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_endpoint():
    """Health check endpoint"""
    try:
        # Test connection
        with api.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv("API_PORT", 5001))
    debug = os.getenv("API_DEBUG", "false").lower() == "true"
    
    logger.info(f"Iniciando API en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

