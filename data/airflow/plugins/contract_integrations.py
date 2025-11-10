"""
Módulo de Integración para Gestión Automatizada de Contratos
Incluye integración con DocuSign y PandaDoc para firma electrónica
"""

from __future__ import annotations

import json
import logging
import os
import requests
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta, date
from enum import Enum
from functools import lru_cache

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


class ESignatureProvider(Enum):
    """Proveedores de firma electrónica soportados"""
    DOCUSIGN = "docusign"
    PANDADOC = "pandadoc"
    HELLOSIGN = "hellosign"
    ADOBESIGN = "adobesign"
    MANUAL = "manual"


class DocuSignIntegration:
    """Integración con DocuSign API"""
    
    def __init__(self, api_base_url: str = None, account_id: str = None, 
                 integration_key: str = None, user_id: str = None, 
                 private_key_path: str = None, access_token: str = None):
        """
        Inicializa integración con DocuSign.
        
        Args:
            api_base_url: URL base de la API (default: https://demo.docusign.net para demo)
            account_id: ID de cuenta de DocuSign
            integration_key: Integration Key de la aplicación
            user_id: User ID de DocuSign
            private_key_path: Ruta al archivo de clave privada RSA (para JWT auth)
            access_token: Token de acceso (si ya está disponible)
        """
        self.api_base_url = api_base_url or os.getenv("DOCUSIGN_API_BASE_URL", "https://demo.docusign.net")
        self.account_id = account_id or os.getenv("DOCUSIGN_ACCOUNT_ID", "")
        self.integration_key = integration_key or os.getenv("DOCUSIGN_INTEGRATION_KEY", "")
        self.user_id = user_id or os.getenv("DOCUSIGN_USER_ID", "")
        self.private_key_path = private_key_path or os.getenv("DOCUSIGN_PRIVATE_KEY_PATH", "")
        self.access_token = access_token or os.getenv("DOCUSIGN_ACCESS_TOKEN", "")
        
        if not self.access_token and (self.integration_key and self.user_id and self.private_key_path):
            self.access_token = self._get_access_token_jwt()
    
    def _get_access_token_jwt(self) -> str:
        """Obtiene token de acceso usando JWT (JSON Web Token)"""
        try:
            import jwt
            from cryptography.hazmat.primitives import serialization
            
            # Leer clave privada
            with open(self.private_key_path, 'r') as f:
                private_key = serialization.load_pem_private_key(
                    f.read().encode(),
                    password=None
                )
            
            # Crear JWT
            now = datetime.now(timezone.utc)
            token = jwt.encode({
                'iss': self.integration_key,
                'sub': self.user_id,
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(hours=1)).timestamp()),
                'aud': 'account.docusign.com',
                'scope': 'signature impersonation'
            }, private_key, algorithm='RS256')
            
            # Solicitar token de acceso
            response = requests.post(
                f"{self.api_base_url}/oauth/token",
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': token
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            logger.error(f"Error obteniendo token JWT de DocuSign: {e}")
            raise
    
    def create_envelope(self, document_content: str, document_name: str, 
                       signers: List[Dict[str, Any]], 
                       email_subject: str = "Please sign this document",
                       email_message: str = "Please sign the attached document.",
                       expiration_days: int = 7) -> Dict[str, Any]:
        """
        Crea un sobre (envelope) en DocuSign con documento para firma.
        
        Args:
            document_content: Contenido del documento (base64 o bytes)
            document_name: Nombre del documento
            signers: Lista de firmantes [{"email": "...", "name": "...", "routing_order": 1}]
            email_subject: Asunto del email
            email_message: Mensaje del email
            expiration_days: Días hasta que expire la solicitud de firma
            
        Returns:
            Dict con envelope_id y otros datos
        """
        if not self.access_token:
            raise ValueError("DocuSign access token no disponible")
        
        # Convertir documento a base64 si es necesario
        if isinstance(document_content, str):
            if not document_content.startswith('data:'):
                import base64
                document_content = base64.b64encode(document_content.encode()).decode()
        
        # Construir payload para DocuSign
        signers_payload = []
        for i, signer in enumerate(signers):
            signers_payload.append({
                "email": signer["email"],
                "name": signer["name"],
                "routingOrder": signer.get("routing_order", i + 1),
                "recipientId": str(i + 1),
                "tabs": {
                    "signHereTabs": [{
                        "documentId": "1",
                        "pageNumber": "1",
                        "recipientId": str(i + 1),
                        "xPosition": "100",
                        "yPosition": "100"
                    }]
                }
            })
        
        envelope_definition = {
            "emailSubject": email_subject,
            "emailBlurb": email_message,
            "status": "sent",
            "documents": [{
                "documentBase64": document_content.split(',')[-1] if ',' in document_content else document_content,
                "name": document_name,
                "fileExtension": "pdf",
                "documentId": "1"
            }],
            "recipients": {
                "signers": signers_payload
            },
            "notification": {
                "expirations": {
                    "expireEnabled": "true",
                    "expireAfter": str(expiration_days),
                    "expireWarn": str(expiration_days - 1)
                }
            }
        }
        
        # Enviar a DocuSign
        url = f"{self.api_base_url}/restapi/v2.1/accounts/{self.account_id}/envelopes"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=envelope_definition, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            logger.info(
                f"Envelope creado en DocuSign",
                extra={
                    "envelope_id": result.get("envelopeId"),
                    "status": result.get("status"),
                    "signers_count": len(signers)
                }
            )
            
            return {
                "envelope_id": result.get("envelopeId"),
                "status": result.get("status"),
                "status_date_time": result.get("statusDateTime"),
                "uri": result.get("uri")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creando envelope en DocuSign: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Respuesta de error: {e.response.text}")
            raise
    
    def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un envelope"""
        if not self.access_token:
            raise ValueError("DocuSign access token no disponible")
        
        url = f"{self.api_base_url}/restapi/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo estado de envelope: {e}")
            raise
    
    def get_signed_document(self, envelope_id: str) -> bytes:
        """Descarga el documento firmado"""
        if not self.access_token:
            raise ValueError("DocuSign access token no disponible")
        
        url = f"{self.api_base_url}/restapi/v2.1/accounts/{self.account_id}/envelopes/{envelope_id}/documents/combined"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error descargando documento firmado: {e}")
            raise


class PandaDocIntegration:
    """Integración con PandaDoc API"""
    
    def __init__(self, api_key: str = None, api_base_url: str = None):
        """
        Inicializa integración con PandaDoc.
        
        Args:
            api_key: API Key de PandaDoc
            api_base_url: URL base de la API (default: https://api.pandadoc.com)
        """
        self.api_key = api_key or os.getenv("PANDADOC_API_KEY", "")
        self.api_base_url = api_base_url or os.getenv("PANDADOC_API_BASE_URL", "https://api.pandadoc.com")
        
        if not self.api_key:
            logger.warning("PandaDoc API key no configurada")
    
    def create_document(self, document_name: str, document_content: str,
                       recipients: List[Dict[str, Any]],
                       expiration_days: int = 7) -> Dict[str, Any]:
        """
        Crea un documento en PandaDoc para firma.
        
        Args:
            document_name: Nombre del documento
            document_content: Contenido del documento (base64)
            recipients: Lista de destinatarios [{"email": "...", "first_name": "...", "last_name": "...", "role": "signer"}]
            expiration_days: Días hasta que expire
            
        Returns:
            Dict con document_id y otros datos
        """
        if not self.api_key:
            raise ValueError("PandaDoc API key no disponible")
        
        # Convertir a base64 si es necesario
        if isinstance(document_content, str) and not document_content.startswith('data:'):
            import base64
            document_content = base64.b64encode(document_content.encode()).decode()
        
        payload = {
            "name": document_name,
            "template_uuid": None,
            "recipients": recipients,
            "tokens": [],
            "fields": {},
            "metadata": {},
            "attachments": [],
            "tags": [],
            "images": [],
            "pricing_tables": [],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=expiration_days)).isoformat()
        }
        
        # Crear documento
        url = f"{self.api_base_url}/public/v1/documents"
        headers = {
            "Authorization": f"API-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            document_data = response.json()
            document_id = document_data.get("id")
            
            # Subir contenido del documento
            content_url = f"{self.api_base_url}/public/v1/documents/{document_id}/content"
            files = {
                "file": ("document.pdf", document_content, "application/pdf")
            }
            
            upload_response = requests.post(content_url, files=files, headers={
                "Authorization": f"API-Key {self.api_key}"
            })
            upload_response.raise_for_status()
            
            # Enviar para firma
            send_url = f"{self.api_base_url}/public/v1/documents/{document_id}/send"
            send_response = requests.post(send_url, json={}, headers=headers)
            send_response.raise_for_status()
            
            logger.info(
                f"Documento creado en PandaDoc",
                extra={
                    "document_id": document_id,
                    "recipients_count": len(recipients)
                }
            )
            
            return {
                "document_id": document_id,
                "status": "sent",
                "recipients": recipients
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creando documento en PandaDoc: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Respuesta de error: {e.response.text}")
            raise
    
    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Obtiene el estado de un documento"""
        if not self.api_key:
            raise ValueError("PandaDoc API key no disponible")
        
        url = f"{self.api_base_url}/public/v1/documents/{document_id}"
        headers = {"Authorization": f"API-Key {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo estado de documento: {e}")
            raise
    
    def get_signed_document(self, document_id: str) -> bytes:
        """Descarga el documento firmado"""
        if not self.api_key:
            raise ValueError("PandaDoc API key no disponible")
        
        url = f"{self.api_base_url}/public/v1/documents/{document_id}/download"
        headers = {"Authorization": f"API-Key {self.api_key}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error descargando documento firmado: {e}")
            raise


def get_esignature_client(provider: str) -> Any:
    """
    Obtiene cliente de firma electrónica según el proveedor.
    
    Args:
        provider: 'docusign', 'pandadoc', etc.
        
    Returns:
        Instancia del cliente de integración
    """
    provider_lower = provider.lower()
    
    if provider_lower == ESignatureProvider.DOCUSIGN.value:
        return DocuSignIntegration()
    elif provider_lower == ESignatureProvider.PANDADOC.value:
        return PandaDocIntegration()
    else:
        raise ValueError(f"Proveedor de firma electrónica no soportado: {provider}")


def generate_contract_from_template(template_content: str, variables: Dict[str, Any]) -> str:
    """
    Genera contenido de contrato reemplazando variables en template.
    
    Args:
        template_content: Contenido del template con variables {{variable_name}}
        variables: Dict con valores para las variables
        
    Returns:
        Contenido del contrato con variables reemplazadas
    """
    result = template_content
    
    # Reemplazar variables {{variable_name}}
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    
    return result


def calculate_document_hash(content: bytes) -> str:
    """Calcula hash SHA-256 de un documento para verificación de integridad"""
    return hashlib.sha256(content).hexdigest()


def store_contract_version(contract_id: str, version_number: int, 
                          signed_document: bytes, postgres_conn_id: str = "postgres_default",
                          storage_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Almacena una versión firmada de un contrato.
    
    Args:
        contract_id: ID del contrato
        version_number: Número de versión
        signed_document: Contenido del documento firmado (bytes)
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        storage_config: Configuración de almacenamiento (S3, GCS, etc.)
        
    Returns:
        Dict con información de almacenamiento
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Calcular hash del documento
    document_hash = calculate_document_hash(signed_document)
    
    # Por ahora, almacenar URL local (en producción usar S3/GCS)
    # TODO: Implementar almacenamiento en cloud storage
    storage_url = f"contracts/{contract_id}/version_{version_number}.pdf"
    
    # Insertar en base de datos
    query = """
        INSERT INTO contract_versions (
            contract_id, version_number, version_reason,
            contract_content, signed_document_url, signed_document_hash,
            signed_document_size_bytes, signed_document_format, is_current,
            signed_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (contract_id, version_number) DO UPDATE SET
            signed_document_url = EXCLUDED.signed_document_url,
            signed_document_hash = EXCLUDED.signed_document_hash,
            signed_document_size_bytes = EXCLUDED.signed_document_size_bytes,
            signed_at = EXCLUDED.signed_at,
            is_current = EXCLUDED.is_current
    """
    
    # Obtener contenido del contrato original
    contract_query = "SELECT contract_content FROM contracts WHERE contract_id = %s"
    contract_result = hook.get_first(contract_query, parameters=(contract_id,))
    contract_content = contract_result[0] if contract_result else ""
    
    hook.run(query, parameters=(
        contract_id,
        version_number,
        'initial' if version_number == 1 else 'amendment',
        contract_content,
        storage_url,
        document_hash,
        len(signed_document),
        'pdf',
        True,  # Marcar como versión actual
        datetime.now(timezone.utc)
    ))
    
    # Marcar otras versiones como no actuales
    hook.run(
        "UPDATE contract_versions SET is_current = false WHERE contract_id = %s AND version_number != %s",
        parameters=(contract_id, version_number)
    )
    
    logger.info(
        f"Versión de contrato almacenada",
        extra={
            "contract_id": contract_id,
            "version_number": version_number,
            "document_hash": document_hash,
            "size_bytes": len(signed_document)
        }
    )
    
    return {
        "contract_id": contract_id,
        "version_number": version_number,
        "storage_url": storage_url,
        "document_hash": document_hash,
        "size_bytes": len(signed_document)
    }


# ============================================================================
# Funciones de Gestión de Plantillas
# ============================================================================

@lru_cache(maxsize=100)
def get_template_cached(template_id: str, postgres_conn_id: str = "postgres_default") -> Optional[Dict[str, Any]]:
    """Versión con caché de get_template para mejor rendimiento"""
    return get_template(template_id, postgres_conn_id)


# Intentar usar caché avanzado si está disponible
try:
    from data.airflow.plugins.contract_cache import get_template_cached as get_template_cached_advanced
    # Usar versión avanzada si Redis está disponible
    _template_cache_func = get_template_cached_advanced
except ImportError:
    _template_cache_func = get_template_cached


def get_template(template_id: str, postgres_conn_id: str = "postgres_default") -> Optional[Dict[str, Any]]:
    """
    Obtiene una plantilla de contrato por ID.
    
    Args:
        template_id: ID de la plantilla
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        
    Returns:
        Dict con datos de la plantilla o None si no existe
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT 
            template_id, name, description, contract_type, template_content,
            template_variables, default_expiration_days, default_reminder_days,
            requires_legal_review, requires_manager_approval, signers_required,
            metadata, is_active, created_by, created_at, updated_at
        FROM contract_templates
        WHERE template_id = %s AND is_active = true
    """
    
    result = hook.get_first(query, parameters=(template_id,))
    
    if not result:
        return None
    
    return {
        "template_id": result[0],
        "name": result[1],
        "description": result[2],
        "contract_type": result[3],
        "template_content": result[4],
        "template_variables": result[5] if isinstance(result[5], dict) else json.loads(result[5] or '{}'),
        "default_expiration_days": result[6],
        "default_reminder_days": result[7] if isinstance(result[7], list) else json.loads(result[7] or '[]'),
        "requires_legal_review": result[8],
        "requires_manager_approval": result[9],
        "signers_required": result[10] if isinstance(result[10], list) else json.loads(result[10] or '[]'),
        "metadata": result[11] if isinstance(result[11], dict) else json.loads(result[11] or '{}'),
        "is_active": result[12],
        "created_by": result[13],
        "created_at": result[14],
        "updated_at": result[15]
    }


def create_contract_from_template(
    template_id: str,
    primary_party_email: str,
    primary_party_name: str,
    contract_variables: Dict[str, Any],
    postgres_conn_id: str = "postgres_default",
    additional_signers: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea un contrato a partir de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        primary_party_email: Email de la parte principal
        primary_party_name: Nombre de la parte principal
        contract_variables: Variables para reemplazar en el template
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        additional_signers: Firmantes adicionales [{"email": "...", "name": "...", "role": "..."}]
        
    Returns:
        Dict con información del contrato creado
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Validar datos antes de crear
    try:
        from data.airflow.plugins.contract_validation import validate_contract_complete
        contract_data_for_validation = {
            "primary_party_email": primary_party_email,
            "primary_party_name": primary_party_name,
            "contract_type": None,  # Se obtendrá del template
            "start_date": contract_variables.get("start_date"),
            "expiration_days": contract_variables.get("expiration_days"),
            "signers_required": additional_signers or []
        }
        
        # Obtener plantilla primero para validación completa
        template = get_template(template_id, postgres_conn_id)
        if not template:
            raise ValueError(f"Plantilla no encontrada: {template_id}")
        
        contract_data_for_validation["contract_type"] = template["contract_type"]
        contract_data_for_validation["signers_required"] = template.get("signers_required", []) + (additional_signers or [])
        
        # Validar
        is_valid, errors, warnings = validate_contract_complete(
            template["template_content"],
            contract_variables,
            contract_data_for_validation
        )
        
        if not is_valid:
            error_msg = f"Validación fallida: {', '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if warnings:
            logger.warning(f"Advertencias de validación: {', '.join(warnings)}")
    except ImportError:
        # Si el módulo de validación no está disponible, continuar sin validar
        logger.warning("Módulo de validación no disponible, saltando validación")
        template = get_template(template_id, postgres_conn_id)
        if not template:
            raise ValueError(f"Plantilla no encontrada: {template_id}")
    
    # Generar contenido del contrato
    contract_content = generate_contract_from_template(
        template["template_content"],
        contract_variables
    )
    
    # Generar ID único del contrato
    import uuid
    contract_id = f"CONTRACT-{uuid.uuid4().hex[:12].upper()}"
    
    # Calcular fechas
    start_date = contract_variables.get("start_date")
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    elif not start_date:
        start_date = datetime.now().date()
    
    expiration_days = contract_variables.get("expiration_days") or template["default_expiration_days"]
    expiration_date = start_date + timedelta(days=expiration_days) if expiration_days else None
    
    # Determinar tipo de parte principal
    primary_party_type = contract_variables.get("primary_party_type", "employee")
    
    # Insertar contrato en BD
    insert_query = """
        INSERT INTO contracts (
            contract_id, template_id, contract_type, primary_party_type,
            primary_party_email, primary_party_name, primary_party_id,
            title, description, contract_content, contract_variables,
            start_date, expiration_date, status, requires_legal_review,
            auto_renew, renewal_notice_days, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    
    title = contract_variables.get("title") or f"Contrato {template['name']} - {primary_party_name}"
    description = contract_variables.get("description") or template.get("description", "")
    
    hook.run(insert_query, parameters=(
        contract_id,
        template_id,
        template["contract_type"],
        primary_party_type,
        primary_party_email,
        primary_party_name,
        contract_variables.get("primary_party_id"),
        title,
        description,
        contract_content,
        json.dumps(contract_variables),
        start_date,
        expiration_date,
        "draft",
        template["requires_legal_review"],
        contract_variables.get("auto_renew", False),
        contract_variables.get("renewal_notice_days", 90),
        contract_variables.get("created_by", "system")
    ))
    
    # Crear firmantes
    signers = template.get("signers_required", [])
    if additional_signers:
        signers.extend(additional_signers)
    
    # Agregar parte principal como primer firmante si no está
    primary_in_signers = any(s.get("email") == primary_party_email for s in signers)
    if not primary_in_signers:
        signers.insert(0, {
            "email": primary_party_email,
            "name": primary_party_name,
            "role": primary_party_type
        })
    
    # Insertar firmantes
    signer_order = 1
    for signer in signers:
        signer_insert_query = """
            INSERT INTO contract_signers (
                contract_id, signer_email, signer_name, signer_role, signer_order
            ) VALUES (%s, %s, %s, %s, %s)
        """
        hook.run(signer_insert_query, parameters=(
            contract_id,
            signer["email"],
            signer["name"],
            signer.get("role", "signer"),
            signer_order
        ))
        signer_order += 1
    
    # Registrar evento
    event_query = """
        INSERT INTO contract_events (
            contract_id, event_type, event_description, event_actor_email, event_data
        ) VALUES (%s, %s, %s, %s, %s)
    """
    hook.run(event_query, parameters=(
        contract_id,
        "created",
        f"Contrato creado desde plantilla {template_id}",
        contract_variables.get("created_by", "system"),
        json.dumps({"template_id": template_id, "variables_count": len(contract_variables)})
    ))
    
    logger.info(
        f"Contrato creado desde plantilla",
        extra={
            "contract_id": contract_id,
            "template_id": template_id,
            "primary_party_email": primary_party_email,
            "signers_count": len(signers)
        }
    )
    
    # Enviar notificación
    try:
        from data.airflow.plugins.contract_notifications import send_contract_notification
        send_contract_notification(
            "created",
            contract_id,
            {
                "title": title,
                "contract_type": template["contract_type"],
                "primary_party_name": primary_party_name,
                "status": "draft"
            }
        )
    except Exception as e:
        logger.warning(f"Error enviando notificación de creación: {e}")
    
    return {
        "contract_id": contract_id,
        "template_id": template_id,
        "status": "draft",
        "signers_count": len(signers),
        "expiration_date": expiration_date.isoformat() if expiration_date else None
    }


def send_contract_for_signature(
    contract_id: str,
    esignature_provider: str = "docusign",
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Envía un contrato para firma electrónica.
    
    Args:
        contract_id: ID del contrato
        esignature_provider: Proveedor de firma ('docusign', 'pandadoc')
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        
    Returns:
        Dict con información del envío
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contrato
    contract_query = """
        SELECT contract_id, title, contract_content, esignature_provider,
               primary_party_email, primary_party_name
        FROM contracts
        WHERE contract_id = %s
    """
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    if not contract:
        raise ValueError(f"Contrato no encontrado: {contract_id}")
    
    # Obtener firmantes
    signers_query = """
        SELECT signer_email, signer_name, signer_role, signer_order
        FROM contract_signers
        WHERE contract_id = %s
        ORDER BY signer_order
    """
    signers_rows = hook.get_records(signers_query, parameters=(contract_id,))
    
    signers = []
    for row in signers_rows:
        signers.append({
            "email": row[0],
            "name": row[1],
            "role": row[2],
            "routing_order": row[3]
        })
    
    if not signers:
        raise ValueError(f"No hay firmantes configurados para el contrato: {contract_id}")
    
    # Obtener cliente de firma electrónica con circuit breaker
    try:
        from data.airflow.plugins.contract_circuit_breaker import get_circuit_breaker
        
        circuit_breaker = get_circuit_breaker(esignature_provider)
        esignature_client = circuit_breaker.call(get_esignature_client, esignature_provider)
    except Exception as e:
        logger.warning(f"Circuit breaker no disponible, usando cliente directo: {e}")
        esignature_client = get_esignature_client(esignature_provider)
    
    # Convertir contenido a PDF
    try:
        from data.airflow.plugins.contract_pdf_generator import generate_contract_pdf
        
        # Detectar tipo de contenido
        contract_content = contract[2]  # contract_content
        if contract_content.startswith('<html>') or contract_content.startswith('<!DOCTYPE'):
            content_type = "html"
        elif contract_content.startswith('#') or '**' in contract_content:
            content_type = "markdown"
        else:
            content_type = "text"
        
        # Generar PDF
        pdf_bytes = generate_contract_pdf(
            contract_content=contract_content,
            contract_type=content_type,
            title=contract[1],  # title
            output_format="base64"
        )
        document_content = pdf_bytes
    except ImportError:
        # Fallback: asumir que ya está en formato PDF base64
        logger.warning("PDF generator no disponible, usando contenido directo")
        document_content = contract[2]  # contract_content
    
    # Crear envelope/documento en el servicio
    if esignature_provider.lower() == "docusign":
        result = esignature_client.create_envelope(
            document_content=document_content,
            document_name=contract[1],  # title
            signers=signers,
            email_subject=f"Por favor firma: {contract[1]}",
            email_message=f"Por favor revisa y firma el documento adjunto: {contract[1]}",
            expiration_days=7
        )
        envelope_id = result["envelope_id"]
        document_id = None
    elif esignature_provider.lower() == "pandadoc":
        recipients = [
            {
                "email": s["email"],
                "first_name": s["name"].split()[0] if s["name"] else "",
                "last_name": " ".join(s["name"].split()[1:]) if len(s["name"].split()) > 1 else "",
                "role": s.get("role", "signer")
            }
            for s in signers
        ]
        result = esignature_client.create_document(
            document_name=contract[1],
            document_content=document_content,
            recipients=recipients,
            expiration_days=7
        )
        envelope_id = None
        document_id = result["document_id"]
    else:
        raise ValueError(f"Proveedor no soportado: {esignature_provider}")
    
    # Actualizar contrato en BD
    update_query = """
        UPDATE contracts
        SET esignature_provider = %s,
            esignature_envelope_id = %s,
            esignature_document_id = %s,
            esignature_url = %s,
            status = 'pending_signature',
            updated_at = NOW()
        WHERE contract_id = %s
    """
    
    esignature_url = result.get("url") or f"https://app.{esignature_provider}.com/sign/{envelope_id or document_id}"
    
    hook.run(update_query, parameters=(
        esignature_provider,
        envelope_id,
        document_id,
        esignature_url,
        contract_id
    ))
    
    # Actualizar estado de firmantes
    signer_update_query = """
        UPDATE contract_signers
        SET signature_status = 'sent',
            signature_sent_at = NOW(),
            signature_expires_at = NOW() + INTERVAL '7 days',
            updated_at = NOW()
        WHERE contract_id = %s
    """
    hook.run(signer_update_query, parameters=(contract_id,))
    
    # Registrar evento
    event_query = """
        INSERT INTO contract_events (
            contract_id, event_type, event_description, event_data
        ) VALUES (%s, %s, %s, %s)
    """
    hook.run(event_query, parameters=(
        contract_id,
        "sent_for_signature",
        f"Contrato enviado para firma mediante {esignature_provider}",
        json.dumps({
            "provider": esignature_provider,
            "envelope_id": envelope_id,
            "document_id": document_id,
            "signers_count": len(signers)
        })
    ))
    
    logger.info(
        f"Contrato enviado para firma",
        extra={
            "contract_id": contract_id,
            "provider": esignature_provider,
            "envelope_id": envelope_id,
            "document_id": document_id,
            "signers_count": len(signers)
        }
    )
    
    result = {
        "contract_id": contract_id,
        "provider": esignature_provider,
        "envelope_id": envelope_id,
        "document_id": document_id,
        "esignature_url": esignature_url,
        "status": "pending_signature"
    }
    
    # Enviar notificación
    try:
        from data.airflow.plugins.contract_notifications import send_contract_notification
        send_contract_notification("sent", contract_id, {
            "title": contract[1],
            "provider": esignature_provider,
            "envelope_id": envelope_id,
            "document_id": document_id,
            "esignature_url": esignature_url
        })
    except Exception as e:
        logger.warning(f"Error enviando notificación de envío: {e}")
    
    return result


def check_contract_signature_status(
    contract_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Verifica el estado de firma de un contrato y actualiza la BD.
    
    Args:
        contract_id: ID del contrato
        postgres_conn_id: Connection ID de Airflow para PostgreSQL
        
    Returns:
        Dict con estado actualizado
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contrato
    contract_query = """
        SELECT contract_id, esignature_provider, esignature_envelope_id, 
               esignature_document_id, status
        FROM contracts
        WHERE contract_id = %s
    """
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    if not contract:
        raise ValueError(f"Contrato no encontrado: {contract_id}")
    
    provider = contract[1]
    envelope_id = contract[2]
    document_id = contract[3]
    
    if not provider or provider == "manual":
        # No hay integración, verificar estado manual en BD
        signers_query = """
            SELECT signer_email, signature_status
            FROM contract_signers
            WHERE contract_id = %s
        """
        signers = hook.get_records(signers_query, parameters=(contract_id,))
        
        signed_count = sum(1 for s in signers if s[1] == "signed")
        total_count = len(signers)
        
        status = "fully_signed" if signed_count == total_count else "partially_signed" if signed_count > 0 else "pending_signature"
        
        return {
            "contract_id": contract_id,
            "status": status,
            "signed_count": signed_count,
            "total_signers": total_count
        }
    
    # Obtener cliente y verificar estado con circuit breaker
    try:
        from data.airflow.plugins.contract_circuit_breaker import get_circuit_breaker
        
        circuit_breaker = get_circuit_breaker(provider)
        esignature_client = get_esignature_client(provider)
        
        def get_status():
            if provider.lower() == "docusign" and envelope_id:
                return esignature_client.get_envelope_status(envelope_id)
            elif provider.lower() == "pandadoc" and document_id:
                return esignature_client.get_document_status(document_id)
            return {}
        
        provider_status_data = circuit_breaker.call(get_status)
    except Exception as e:
        logger.warning(f"Circuit breaker no disponible, usando cliente directo: {e}")
        esignature_client = get_esignature_client(provider)
        if provider.lower() == "docusign" and envelope_id:
            provider_status_data = esignature_client.get_envelope_status(envelope_id)
        elif provider.lower() == "pandadoc" and document_id:
            provider_status_data = esignature_client.get_document_status(document_id)
        else:
            provider_status_data = {}
    
    if provider.lower() == "docusign" and envelope_id:
        status_str = provider_status_data.get("status", "unknown")
        
        # Mapear estado de DocuSign
        status_map = {
            "sent": "pending_signature",
            "delivered": "pending_signature",
            "completed": "fully_signed",
            "declined": "cancelled",
            "voided": "cancelled"
        }
        contract_status = status_map.get(status_str.lower(), "pending_signature")
        
    elif provider.lower() == "pandadoc" and document_id:
        status_str = provider_status_data.get("status", "unknown")
        
        # Mapear estado de PandaDoc
        status_map = {
            "draft": "draft",
            "sent": "pending_signature",
            "viewed": "pending_signature",
            "completed": "fully_signed",
            "declined": "cancelled"
        }
        contract_status = status_map.get(status_str.lower(), "pending_signature")
    else:
        return {
            "contract_id": contract_id,
            "status": "unknown",
            "error": "No se pudo obtener estado del servicio"
        }
    
    # Actualizar estado en BD
    update_query = """
        UPDATE contracts
        SET status = %s,
            updated_at = NOW()
        WHERE contract_id = %s
    """
    hook.run(update_query, parameters=(contract_status, contract_id))
    
    # Si está completamente firmado, descargar y almacenar
    if contract_status == "fully_signed":
        try:
            if provider.lower() == "docusign":
                signed_doc = esignature_client.get_signed_document(envelope_id)
            elif provider.lower() == "pandadoc":
                signed_doc = esignature_client.get_signed_document(document_id)
            else:
                signed_doc = None
            
            if signed_doc:
                # Obtener última versión
                version_query = """
                    SELECT COALESCE(MAX(version_number), 0) + 1
                    FROM contract_versions
                    WHERE contract_id = %s
                """
                version_result = hook.get_first(version_query, parameters=(contract_id,))
                next_version = version_result[0] if version_result else 1
                
                # Almacenar versión
                store_contract_version(
                    contract_id=contract_id,
                    version_number=next_version,
                    signed_document=signed_doc,
                    postgres_conn_id=postgres_conn_id
                )
                
                # Actualizar fecha de firma
                hook.run(
                    "UPDATE contracts SET signed_date = NOW() WHERE contract_id = %s",
                    parameters=(contract_id,)
                )
                
                # Actualizar firmantes
                hook.run(
                    """
                    UPDATE contract_signers
                    SET signature_status = 'signed',
                        signature_signed_at = NOW(),
                        updated_at = NOW()
                    WHERE contract_id = %s
                    """,
                    parameters=(contract_id,)
                )
                
                # Registrar evento
                hook.run(
                    """
                    INSERT INTO contract_events (
                        contract_id, event_type, event_description
                    ) VALUES (%s, %s, %s)
                    """,
                    parameters=(contract_id, "signed", "Contrato completamente firmado")
                )
                
                # Enviar notificación
                try:
                    from data.airflow.plugins.contract_notifications import send_contract_notification
                    contract_info_query = "SELECT title, primary_party_name, signed_date FROM contracts WHERE contract_id = %s"
                    contract_info = hook.get_first(contract_info_query, parameters=(contract_id,))
                    if contract_info:
                        send_contract_notification("signed", contract_id, {
                            "title": contract_info[0],
                            "primary_party_name": contract_info[1],
                            "signed_date": contract_info[2].isoformat() if contract_info[2] else None
                        })
                except Exception as e:
                    logger.warning(f"Error enviando notificación de firma: {e}")
        except Exception as e:
            logger.error(f"Error descargando/almacenando documento firmado: {e}")
    
    return {
        "contract_id": contract_id,
        "status": contract_status,
        "provider_status": status_str
    }


# ============================================================================
# Funciones de Integración con Onboarding
# ============================================================================

def create_contract_for_employee_onboarding(
    employee_email: str,
    employee_name: str,
    start_date: str,
    manager_email: str = None,
    department: str = None,
    position: str = None,
    template_id: str = "employment_contract_v1",
    postgres_conn_id: str = "postgres_default",
    auto_send_for_signature: bool = True,
    esignature_provider: str = "docusign"
) -> Dict[str, Any]:
    """
    Crea un contrato laboral automáticamente durante el proceso de onboarding.
    
    Args:
        employee_email: Email del empleado
        employee_name: Nombre completo del empleado
        start_date: Fecha de inicio (YYYY-MM-DD)
        manager_email: Email del manager (opcional)
        department: Departamento (opcional)
        position: Posición/Cargo (opcional)
        template_id: ID de la plantilla de contrato
        postgres_conn_id: Connection ID de Airflow
        auto_send_for_signature: Enviar automáticamente para firma
        esignature_provider: Proveedor de firma electrónica
        
    Returns:
        Dict con información del contrato creado
    """
    # Construir variables del contrato
    contract_variables = {
        "employee_name": employee_name,
        "employee_email": employee_email,
        "start_date": start_date,
        "position": position or "Employee",
        "department": department or "General",
        "primary_party_type": "employee",
        "title": f"Contrato Laboral - {employee_name}",
    }
    
    # Enriquecer con datos de HRIS si está disponible
    try:
        from data.airflow.plugins.contract_hris_integration import enrich_contract_with_hris_data
        contract_variables = enrich_contract_with_hris_data(
            contract_variables,
            employee_email
        )
    except Exception as e:
        logger.debug(f"HRIS enrichment no disponible: {e}")
    
    # Agregar manager si está disponible
    additional_signers = []
    if manager_email:
        contract_variables["manager_email"] = manager_email
        additional_signers.append({
            "email": manager_email,
            "name": f"Manager",  # Se puede obtener del HRIS
            "role": "manager"
        })
    
    # Crear contrato
    result = create_contract_from_template(
        template_id=template_id,
        primary_party_email=employee_email,
        primary_party_name=employee_name,
        contract_variables=contract_variables,
        postgres_conn_id=postgres_conn_id,
        additional_signers=additional_signers if additional_signers else None
    )
    
    contract_id = result["contract_id"]
    
    # Actualizar employee_onboarding con contract_id
    if POSTGRES_AVAILABLE:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        hook.run(
            """
            UPDATE employee_onboarding
            SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('contract_id', %s)
            WHERE employee_email = %s
            """,
            parameters=(contract_id, employee_email)
        )
    
    # Enviar para firma si está configurado
    if auto_send_for_signature:
        try:
            send_result = send_contract_for_signature(
                contract_id=contract_id,
                esignature_provider=esignature_provider,
                postgres_conn_id=postgres_conn_id
            )
            result.update(send_result)
        except Exception as e:
            logger.warning(f"Error enviando contrato para firma durante onboarding: {e}")
            result["signature_error"] = str(e)
    
    logger.info(
        f"Contrato creado para onboarding",
        extra={
            "contract_id": contract_id,
            "employee_email": employee_email,
            "template_id": template_id
        }
    )
    
    return result


def renew_contract(
    contract_id: str,
    new_start_date: str = None,
    new_expiration_days: int = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Renueva un contrato creando una nueva versión.
    
    Args:
        contract_id: ID del contrato a renovar
        new_start_date: Nueva fecha de inicio (opcional, default: fecha de expiración actual)
        new_expiration_days: Días de validez del nuevo contrato (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del contrato renovado
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contrato original
    contract_query = """
        SELECT contract_id, template_id, contract_type, primary_party_email,
               primary_party_name, expiration_date, contract_variables
        FROM contracts
        WHERE contract_id = %s AND status = 'fully_signed'
    """
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    
    if not contract:
        raise ValueError(f"Contrato no encontrado o no está completamente firmado: {contract_id}")
    
    # Calcular nueva fecha de inicio
    if not new_start_date:
        expiration_date = contract[5]
        if expiration_date:
            new_start_date = expiration_date.isoformat()
        else:
            new_start_date = datetime.now().date().isoformat()
    
    # Obtener días de expiración
    if not new_expiration_days:
        template_query = "SELECT default_expiration_days FROM contract_templates WHERE template_id = %s"
        template_result = hook.get_first(template_query, parameters=(contract[1],))
        new_expiration_days = template_result[0] if template_result else 365
    
    # Obtener variables originales
    contract_variables = contract[6]
    if isinstance(contract_variables, str):
        contract_variables = json.loads(contract_variables)
    
    # Actualizar variables con nuevas fechas
    contract_variables["start_date"] = new_start_date
    contract_variables["expiration_days"] = new_expiration_days
    contract_variables["renewal_of"] = contract_id
    
    # Crear nuevo contrato desde la misma plantilla
    import uuid
    new_contract_id = f"CONTRACT-{uuid.uuid4().hex[:12].upper()}"
    
    # Obtener firmantes del contrato original
    signers_query = """
        SELECT signer_email, signer_name, signer_role
        FROM contract_signers
        WHERE contract_id = %s
        ORDER BY signer_order
    """
    signers_rows = hook.get_records(signers_query, parameters=(contract_id,))
    additional_signers = [
        {"email": row[0], "name": row[1], "role": row[2]}
        for row in signers_rows
    ]
    
    # Crear nuevo contrato
    result = create_contract_from_template(
        template_id=contract[1],
        primary_party_email=contract[3],
        primary_party_name=contract[4],
        contract_variables=contract_variables,
        postgres_conn_id=postgres_conn_id,
        additional_signers=additional_signers[1:] if len(additional_signers) > 1 else None
    )
    
    # Marcar contrato original como renovado
    hook.run(
        "UPDATE contracts SET status = 'renewed', updated_at = NOW() WHERE contract_id = %s",
        parameters=(contract_id,)
    )
    
    # Registrar evento
    hook.run(
        """
        INSERT INTO contract_events (
            contract_id, event_type, event_description, event_data
        ) VALUES (%s, %s, %s, %s)
        """,
        parameters=(
            contract_id,
            "renewed",
            f"Contrato renovado. Nuevo contrato: {result['contract_id']}",
            json.dumps({"new_contract_id": result["contract_id"]})
        )
    )
    
    logger.info(
        f"Contrato renovado",
        extra={
            "original_contract_id": contract_id,
            "new_contract_id": result["contract_id"]
        }
    )
    
    return {
        "original_contract_id": contract_id,
        "new_contract_id": result["contract_id"],
        "status": "created",
        "renewal_date": new_start_date
    }


# ============================================================================
# Funciones de Reportes y Analytics
# ============================================================================

def get_contract_analytics(
    start_date: str = None,
    end_date: str = None,
    contract_type: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene analytics y métricas de contratos.
    
    Args:
        start_date: Fecha de inicio para filtrar (YYYY-MM-DD)
        end_date: Fecha de fin para filtrar (YYYY-MM-DD)
        contract_type: Tipo de contrato a filtrar
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con métricas y estadísticas
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Construir query con filtros
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("created_at >= %s")
        params.append(start_date)
    if end_date:
        where_clauses.append("created_at <= %s")
        params.append(end_date)
    if contract_type:
        where_clauses.append("contract_type = %s")
        params.append(contract_type)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Query principal de analytics
    query = f"""
        SELECT 
            COUNT(*) as total_contracts,
            COUNT(CASE WHEN status = 'fully_signed' THEN 1 END) as signed_count,
            COUNT(CASE WHEN status = 'pending_signature' THEN 1 END) as pending_count,
            COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_count,
            AVG(EXTRACT(EPOCH FROM (signed_date - created_at)) / 86400) as avg_days_to_sign,
            COUNT(CASE WHEN expiration_date <= CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as expiring_30_days,
            COUNT(CASE WHEN auto_renew = true THEN 1 END) as auto_renew_count,
            COUNT(DISTINCT contract_type) as contract_types_count
        FROM contracts
        WHERE {where_sql}
    """
    
    result = hook.get_first(query, parameters=tuple(params))
    
    return {
        "total_contracts": result[0] or 0,
        "signed_count": result[1] or 0,
        "pending_count": result[2] or 0,
        "expired_count": result[3] or 0,
        "avg_days_to_sign": float(result[4]) if result[4] else 0.0,
        "expiring_30_days": result[5] or 0,
        "auto_renew_count": result[6] or 0,
        "contract_types_count": result[7] or 0,
        "signing_rate": (result[1] / result[0] * 100) if result[0] > 0 else 0.0
    }


def search_contracts(
    search_term: str = None,
    contract_type: str = None,
    status: str = None,
    primary_party_email: str = None,
    limit: int = 100,
    offset: int = 0,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Búsqueda avanzada de contratos con filtros.
    
    Args:
        search_term: Término de búsqueda (busca en title, description)
        contract_type: Filtrar por tipo de contrato
        status: Filtrar por estado
        primary_party_email: Filtrar por email de la parte principal
        limit: Límite de resultados
        offset: Offset para paginación
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados y metadatos de paginación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    where_clauses = []
    params = []
    
    if search_term:
        where_clauses.append("(title ILIKE %s OR description ILIKE %s)")
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern])
    if contract_type:
        where_clauses.append("contract_type = %s")
        params.append(contract_type)
    if status:
        where_clauses.append("status = %s")
        params.append(status)
    if primary_party_email:
        where_clauses.append("primary_party_email = %s")
        params.append(primary_party_email)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Query de conteo total
    count_query = f"SELECT COUNT(*) FROM contracts WHERE {where_sql}"
    total_count = hook.get_first(count_query, parameters=tuple(params))[0]
    
    # Query de resultados
    results_query = f"""
        SELECT 
            contract_id, title, contract_type, status, primary_party_name,
            primary_party_email, start_date, expiration_date, signed_date,
            created_at
        FROM contracts
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    results = hook.get_records(results_query, parameters=tuple(params))
    
    contracts = []
    for row in results:
        contracts.append({
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "primary_party_name": row[4],
            "primary_party_email": row[5],
            "start_date": row[6].isoformat() if row[6] else None,
            "expiration_date": row[7].isoformat() if row[7] else None,
            "signed_date": row[8].isoformat() if row[8] else None,
            "created_at": row[9].isoformat() if row[9] else None,
        })
    
    return {
        "contracts": contracts,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }

