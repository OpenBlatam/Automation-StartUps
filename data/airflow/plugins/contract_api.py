"""
API REST para Gestión de Contratos
Endpoints para crear, consultar y gestionar contratos
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from data.airflow.plugins.contract_integrations import (
    create_contract_from_template,
    send_contract_for_signature,
    check_contract_signature_status,
    get_template,
    get_contract_analytics,
    search_contracts,
    renew_contract,
    create_contract_for_employee_onboarding
)

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def create_contract_api(api_key: str = None) -> Optional[Any]:
    """
    Crea una API REST Flask para gestión de contratos.
    
    Args:
        api_key: API key para autenticación (opcional)
        
    Returns:
        Flask app o None si Flask no está disponible
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask no disponible, no se puede crear API")
        return None
    
    app = Flask(__name__)
    app.api_key = api_key or None
    
    def require_auth():
        """Middleware de autenticación"""
        if not app.api_key:
            return None
        
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided_key != app.api_key:
            return jsonify({"error": "Unauthorized"}), 401
        return None
    
    def check_rate_limit(operation: str = "api"):
        """Middleware de rate limiting"""
        try:
            from data.airflow.plugins.contract_rate_limiter import check_rate_limit
            
            client_ip = request.remote_addr or "unknown"
            is_allowed, rate_info = check_rate_limit(operation, key=client_ip)
            
            if not is_allowed:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "rate_limit": rate_info
                }), 429
            
            return None
        except Exception:
            # Si rate limiting no está disponible, continuar
            return None
    
    @app.route('/api/contracts/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }), 200
    
    @app.route('/api/contracts/gdpr/export/<email>', methods=['GET'])
    def export_gdpr_data(email: str):
        """Exporta datos de un sujeto para solicitud GDPR"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            from data.airflow.plugins.contract_compliance import export_contract_data_for_subject
            
            data = export_contract_data_for_subject(primary_party_email=email)
            return jsonify(data), 200
        except Exception as e:
            logger.error(f"Error exportando datos GDPR: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/<contract_id>/gdpr/check', methods=['GET'])
    def check_gdpr_retention(contract_id: str):
        """Verifica política de retención GDPR de un contrato"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            from data.airflow.plugins.contract_compliance import check_contract_retention_policy
            
            retention_years = int(request.args.get('retention_years', 7))
            result = check_contract_retention_policy(
                contract_id=contract_id,
                retention_years=retention_years
            )
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error verificando retención GDPR: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/templates', methods=['GET'])
    def list_templates():
        """Lista todas las plantillas disponibles"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        rate_error = check_rate_limit("api")
        if rate_error:
            return rate_error
        
        try:
            if not POSTGRES_AVAILABLE:
                return jsonify({"error": "Database not available"}), 500
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            query = """
                SELECT template_id, name, description, contract_type, is_active
                FROM contract_templates
                WHERE is_active = true
                ORDER BY name
            """
            templates = hook.get_records(query)
            
            result = []
            for row in templates:
                result.append({
                    "template_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "contract_type": row[3],
                    "is_active": row[4]
                })
            
            return jsonify({"templates": result}), 200
        except Exception as e:
            logger.error(f"Error listando templates: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/templates/<template_id>', methods=['GET'])
    def get_template_info(template_id: str):
        """Obtiene información de una plantilla"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            template = get_template(template_id)
            if not template:
                return jsonify({"error": "Template not found"}), 404
            
            # No exponer el contenido completo por seguridad
            return jsonify({
                "template_id": template["template_id"],
                "name": template["name"],
                "description": template["description"],
                "contract_type": template["contract_type"],
                "default_expiration_days": template["default_expiration_days"],
                "default_reminder_days": template["default_reminder_days"],
                "requires_legal_review": template["requires_legal_review"],
                "requires_manager_approval": template["requires_manager_approval"],
                "signers_required": template["signers_required"],
                "variables_count": len(template.get("template_variables", {}))
            }), 200
        except Exception as e:
            logger.error(f"Error obteniendo template: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts', methods=['POST'])
    def create_contract():
        """Crea un nuevo contrato"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        rate_error = check_rate_limit("create")
        if rate_error:
            return rate_error
        
        try:
            data = request.get_json()
            
            required_fields = ["template_id", "primary_party_email", "primary_party_name", "contract_variables"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
            
            result = create_contract_from_template(
                template_id=data["template_id"],
                primary_party_email=data["primary_party_email"],
                primary_party_name=data["primary_party_name"],
                contract_variables=data["contract_variables"],
                additional_signers=data.get("additional_signers")
            )
            
            # Enviar para firma si está configurado
            if data.get("auto_send_for_signature", False):
                esignature_provider = data.get("esignature_provider", "docusign")
                send_result = send_contract_for_signature(
                    contract_id=result["contract_id"],
                    esignature_provider=esignature_provider
                )
                result.update(send_result)
            
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Error creando contrato: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/<contract_id>', methods=['GET'])
    def get_contract(contract_id: str):
        """Obtiene información de un contrato"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            if not POSTGRES_AVAILABLE:
                return jsonify({"error": "Database not available"}), 500
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            query = """
                SELECT 
                    contract_id, title, contract_type, status, primary_party_name,
                    primary_party_email, start_date, expiration_date, signed_date,
                    esignature_provider, esignature_url, created_at, updated_at
                FROM contracts
                WHERE contract_id = %s
            """
            contract = hook.get_first(query, parameters=(contract_id,))
            
            if not contract:
                return jsonify({"error": "Contract not found"}), 404
            
            # Obtener firmantes
            signers_query = """
                SELECT signer_email, signer_name, signer_role, signature_status, signer_order
                FROM contract_signers
                WHERE contract_id = %s
                ORDER BY signer_order
            """
            signers = hook.get_records(signers_query, parameters=(contract_id,))
            
            return jsonify({
                "contract_id": contract[0],
                "title": contract[1],
                "contract_type": contract[2],
                "status": contract[3],
                "primary_party_name": contract[4],
                "primary_party_email": contract[5],
                "start_date": contract[6].isoformat() if contract[6] else None,
                "expiration_date": contract[7].isoformat() if contract[7] else None,
                "signed_date": contract[8].isoformat() if contract[8] else None,
                "esignature_provider": contract[9],
                "esignature_url": contract[10],
                "created_at": contract[11].isoformat() if contract[11] else None,
                "updated_at": contract[12].isoformat() if contract[12] else None,
                "signers": [
                    {
                        "email": s[0],
                        "name": s[1],
                        "role": s[2],
                        "status": s[3],
                        "order": s[4]
                    }
                    for s in signers
                ]
            }), 200
        except Exception as e:
            logger.error(f"Error obteniendo contrato: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/<contract_id>/status', methods=['GET'])
    def get_contract_status(contract_id: str):
        """Obtiene el estado actual de firma de un contrato"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            status_result = check_contract_signature_status(contract_id=contract_id)
            return jsonify(status_result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.error(f"Error verificando estado: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/<contract_id>/send', methods=['POST'])
    def send_contract(contract_id: str):
        """Envía un contrato para firma"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        rate_error = check_rate_limit("send")
        if rate_error:
            return rate_error
        
        try:
            data = request.get_json() or {}
            esignature_provider = data.get("esignature_provider", "docusign")
            
            result = send_contract_for_signature(
                contract_id=contract_id,
                esignature_provider=esignature_provider
            )
            
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.error(f"Error enviando contrato: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/<contract_id>/renew', methods=['POST'])
    def renew_contract_endpoint(contract_id: str):
        """Renueva un contrato"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            data = request.get_json() or {}
            result = renew_contract(
                contract_id=contract_id,
                new_start_date=data.get("new_start_date"),
                new_expiration_days=data.get("new_expiration_days")
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.error(f"Error renovando contrato: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/search', methods=['GET'])
    def search_contracts_endpoint():
        """Búsqueda avanzada de contratos"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            search_term = request.args.get('q')
            contract_type = request.args.get('type')
            status = request.args.get('status')
            primary_party_email = request.args.get('email')
            limit = int(request.args.get('limit', 100))
            offset = int(request.args.get('offset', 0))
            
            result = search_contracts(
                search_term=search_term,
                contract_type=contract_type,
                status=status,
                primary_party_email=primary_party_email,
                limit=limit,
                offset=offset
            )
            
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error buscando contratos: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/analytics', methods=['GET'])
    def get_analytics():
        """Obtiene analytics de contratos"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            contract_type = request.args.get('contract_type')
            
            result = get_contract_analytics(
                start_date=start_date,
                end_date=end_date,
                contract_type=contract_type
            )
            
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error obteniendo analytics: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/contracts/onboarding', methods=['POST'])
    def create_onboarding_contract():
        """Crea un contrato para onboarding de empleado"""
        auth_error = require_auth()
        if auth_error:
            return auth_error
        
        try:
            data = request.get_json()
            
            required_fields = ["employee_email", "employee_name", "start_date"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
            
            result = create_contract_for_employee_onboarding(
                employee_email=data["employee_email"],
                employee_name=data["employee_name"],
                start_date=data["start_date"],
                manager_email=data.get("manager_email"),
                department=data.get("department"),
                position=data.get("position"),
                template_id=data.get("template_id", "employment_contract_v1"),
                auto_send_for_signature=data.get("auto_send_for_signature", True),
                esignature_provider=data.get("esignature_provider", "docusign")
            )
            
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error creando contrato de onboarding: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app

