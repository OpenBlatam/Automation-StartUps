"""
API REST para Procesamiento de Documentos
==========================================

API Flask para procesar documentos remotamente vía HTTP.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

from .document_processor import DocumentProcessor
from .document_validator import DocumentValidator, ValidationLevel
from .document_templates import TemplateManager
from .document_webhooks import WebhookManager
import psycopg2

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilitar CORS para integraciones

# Configuración
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/document_uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Crear directorio de uploads
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Inicializar componentes
processor_config = {
    "ocr": {
        "provider": os.getenv("OCR_PROVIDER", "tesseract"),
        "language": os.getenv("OCR_LANGUAGE", "spa+eng")
    },
    "archive": {
        "base_path": os.getenv("ARCHIVE_PATH", "./archives"),
        "structure": os.getenv("ARCHIVE_STRUCTURE", "by_type_and_date")
    }
}

processor = DocumentProcessor(processor_config)
validator = DocumentValidator(ValidationLevel.MODERATE)
template_manager = TemplateManager(os.getenv("TEMPLATES_DIR", "./templates"))

# Conexión a BD (opcional)
db_connection_string = os.getenv("DATABASE_URL")
db_conn = None
if db_connection_string:
    try:
        db_conn = psycopg2.connect(db_connection_string)
        webhook_manager = WebhookManager(db_conn)
    except Exception as e:
        logger.warning(f"No se pudo conectar a BD: {e}")


def allowed_file(filename: str) -> bool:
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check del servicio"""
    health = processor.health_check()
    return jsonify({
        "status": "healthy" if health['status'] == 'healthy' else "unhealthy",
        "components": health['components']
    }), 200 if health['status'] == 'healthy' else 503


@app.route('/api/v1/process', methods=['POST'])
def process_document():
    """Procesa un documento"""
    try:
        # Verificar archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó archivo"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"Tipo de archivo no permitido. "
                         f"Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Guardar archivo temporal
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        # Opciones de procesamiento
        archive = request.form.get('archive', 'true').lower() == 'true'
        validate = request.form.get('validate', 'false').lower() == 'true'
        template_id = request.form.get('template_id')
        
        try:
            # Procesar documento
            processed = processor.process_document(
                file_path=temp_path,
                filename=filename,
                archive=archive
            )
            
            result = processed.to_dict()
            
            # Validar si se solicita
            if validate:
                validation_report = validator.validate_document(
                    document_id=processed.document_id,
                    document_type=processed.document_type,
                    extracted_fields=processed.extracted_fields
                )
                result['validation'] = {
                    "is_valid": validation_report.overall_valid,
                    "score": validation_report.validation_score,
                    "fields_validated": {
                        k: {
                            "is_valid": v.is_valid,
                            "normalized": v.normalized_value,
                            "errors": v.validation_errors
                        }
                        for k, v in validation_report.fields_validated.items()
                    },
                    "missing_required": validation_report.missing_required_fields,
                    "warnings": validation_report.warnings
                }
            
            # Usar template personalizado si se especifica
            if template_id:
                try:
                    template_extracted = template_manager.extract_with_template(
                        text=processed.extracted_text,
                        template_id=template_id
                    )
                    result['template_extracted_fields'] = template_extracted
                except Exception as e:
                    logger.warning(f"Error usando template: {e}")
            
            # Enviar webhooks si hay BD
            if db_conn and webhook_manager:
                webhook_manager.trigger_webhooks(
                    "document_processed",
                    result,
                    processed.document_type
                )
            
            return jsonify(result), 200
        
        finally:
            # Limpiar archivo temporal
            try:
                os.remove(temp_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Error procesando documento: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/process/batch', methods=['POST'])
def process_batch():
    """Procesa múltiples documentos"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No se proporcionaron archivos"}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "Lista de archivos vacía"}), 400
        
        archive = request.form.get('archive', 'true').lower() == 'true'
        results = []
        
        for file in files:
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(temp_path)
                
                try:
                    processed = processor.process_document(
                        file_path=temp_path,
                        filename=filename,
                        archive=archive
                    )
                    results.append(processed.to_dict())
                except Exception as e:
                    results.append({
                        "filename": filename,
                        "error": str(e)
                    })
                finally:
                    try:
                        os.remove(temp_path)
                    except:
                        pass
        
        return jsonify({
            "total": len(files),
            "processed": len([r for r in results if "error" not in r]),
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Error procesando lote: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/templates', methods=['GET'])
def list_templates():
    """Lista templates disponibles"""
    document_type = request.args.get('document_type')
    
    if document_type:
        templates = template_manager.get_templates_by_type(document_type)
    else:
        templates = list(template_manager.templates.values())
    
    return jsonify({
        "templates": [t.to_dict() for t in templates]
    }), 200


@app.route('/api/v1/templates/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """Obtiene un template específico"""
    template = template_manager.get_template(template_id)
    if not template:
        return jsonify({"error": "Template no encontrado"}), 404
    
    return jsonify(template.to_dict()), 200


@app.route('/api/v1/templates', methods=['POST'])
def create_template():
    """Crea un nuevo template"""
    try:
        data = request.get_json()
        
        rules_data = data.get('rules', [])
        rules = [
            {
                'field_name': r['field_name'],
                'pattern': r['pattern'],
                'required': r.get('required', False),
                'transform': r.get('transform'),
                'default_value': r.get('default_value')
            }
            for r in rules_data
        ]
        
        from .document_templates import ExtractionRule
        extraction_rules = [
            ExtractionRule(
                field_name=r['field_name'],
                pattern=r['pattern'],
                required=r.get('required', False),
                transform=r.get('transform'),
                default_value=r.get('default_value')
            )
            for r in rules_data
        ]
        
        template = template_manager.create_template(
            template_id=data['template_id'],
            name=data['name'],
            document_type=data['document_type'],
            description=data.get('description', ''),
            rules=extraction_rules,
            metadata=data.get('metadata', {})
        )
        
        return jsonify(template.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Error creando template: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400


@app.route('/api/v1/validate', methods=['POST'])
def validate_document():
    """Valida campos de un documento"""
    try:
        data = request.get_json()
        
        validation_report = validator.validate_document(
            document_id=data.get('document_id', 'unknown'),
            document_type=data.get('document_type'),
            extracted_fields=data.get('extracted_fields', {})
        )
        
        return jsonify({
            "is_valid": validation_report.overall_valid,
            "score": validation_report.validation_score,
            "fields_validated": {
                k: {
                    "is_valid": v.is_valid,
                    "normalized": v.normalized_value,
                    "errors": v.validation_errors,
                    "confidence": v.confidence
                }
                for k, v in validation_report.fields_validated.items()
            },
            "missing_required": validation_report.missing_required_fields,
            "warnings": validation_report.warnings
        }), 200
    
    except Exception as e:
        logger.error(f"Error validando: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400


@app.route('/api/v1/webhooks', methods=['GET'])
def list_webhooks():
    """Lista webhooks configurados"""
    if not db_conn:
        return jsonify({"error": "Base de datos no configurada"}), 503
    
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT id, webhook_name, webhook_url, trigger_events, 
                   document_types, enabled
            FROM document_webhooks
            ORDER BY webhook_name
        """)
        
        webhooks = []
        for row in cursor.fetchall():
            webhooks.append({
                "id": row[0],
                "name": row[1],
                "url": row[2],
                "trigger_events": row[3],
                "document_types": row[4],
                "enabled": row[5]
            })
        
        return jsonify({"webhooks": webhooks}), 200
    
    except Exception as e:
        logger.error(f"Error listando webhooks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/webhooks', methods=['POST'])
def register_webhook():
    """Registra un nuevo webhook"""
    if not db_conn:
        return jsonify({"error": "Base de datos no configurada"}), 503
    
    try:
        data = request.get_json()
        
        webhook_manager.register_webhook(
            webhook_name=data['webhook_name'],
            webhook_url=data['webhook_url'],
            trigger_events=data['trigger_events'],
            document_types=data.get('document_types'),
            secret_token=data.get('secret_token'),
            headers=data.get('headers'),
            enabled=data.get('enabled', True)
        )
        
        return jsonify({"message": "Webhook registrado exitosamente"}), 201
    
    except Exception as e:
        logger.error(f"Error registrando webhook: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejecutar servidor
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

