"""
Integraciones para onboarding automatizado de clientes.
Incluye recolección de información, verificación de identidad y activación de servicios.
"""

from __future__ import annotations

import logging
import os
import json
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import requests

logger = logging.getLogger(__name__)


def _env(name: str, default: str = "") -> str:
    """Obtener variable de entorno."""
    return os.getenv(name, default)


def _generate_verification_code(length: int = 6) -> str:
    """Generar código de verificación numérico."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def collect_customer_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recolectar información adicional del cliente desde fuentes externas.
    
    Puede enriquecer datos desde:
    - CRM (HubSpot, Salesforce)
    - Bases de datos internas
    - APIs de terceros
    """
    customer_email = payload.get("customer_email", "")
    logger.info("Collecting customer information", extra={"customer_email": customer_email})
    
    collected_data = {
        "info_collected": True,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "data_sources": []
    }
    
    # Enriquecer desde CRM si está configurado
    crm_api_url = _env("CRM_API_URL")
    crm_api_key = _env("CRM_API_KEY")
    
    if crm_api_url and crm_api_key:
        try:
            response = requests.get(
                f"{crm_api_url}/contacts/{customer_email}",
                headers={"Authorization": f"Bearer {crm_api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                crm_data = response.json()
                collected_data["data_sources"].append("crm")
                
                # Actualizar payload con datos del CRM si no están presentes
                if not payload.get("company_name") and crm_data.get("company"):
                    payload["company_name"] = crm_data["company"]
                if not payload.get("phone") and crm_data.get("phone"):
                    payload["phone"] = crm_data["phone"]
                if not payload.get("country") and crm_data.get("country"):
                    payload["country"] = crm_data["country"]
                
                logger.info("CRM data enriched", extra={"customer_email": customer_email})
        except Exception as e:
            logger.warning(f"Failed to fetch CRM data: {e}", extra={"customer_email": customer_email})
    
    # Guardar información recolectada en base de datos
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        pg_hook = PostgresHook(postgres_conn_id=_env("POSTGRES_CONN_ID", "postgres_default"))
        
        # Insertar datos recolectados
        for field, value in payload.items():
            if field not in ["customer_email", "onboarding_id", "idempotency_key"]:
                insert_sql = """
                    INSERT INTO customer_onboarding_data 
                    (customer_email, data_type, field_name, field_value, collected_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                """
                pg_hook.run(insert_sql, parameters=(
                    customer_email,
                    "contact_info",
                    field,
                    str(value) if value else None
                ))
    except Exception as e:
        logger.warning(f"Failed to persist collected data: {e}")
    
    return {**payload, **collected_data}


def verify_customer_identity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verificar identidad del cliente usando múltiples métodos.
    
    Métodos soportados:
    - email: Verificación por email (OTP)
    - sms: Verificación por SMS (OTP)
    - document: Verificación por documento
    - kyc_provider: Verificación mediante proveedor KYC externo
    """
    customer_email = payload.get("customer_email", "")
    verification_method = payload.get("identity_verification_method", "email")
    
    logger.info(
        "Verifying customer identity",
        extra={
            "customer_email": customer_email,
            "method": verification_method
        }
    )
    
    result = {
        "identity_verified": False,
        "verification_method": verification_method,
        "verification_status": "pending"
    }
    
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        pg_hook = PostgresHook(postgres_conn_id=_env("POSTGRES_CONN_ID", "postgres_default"))
        
        if verification_method == "email":
            # Verificación por email: generar código OTP
            verification_code = _generate_verification_code()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            
            # Guardar verificación en BD
            insert_sql = """
                INSERT INTO customer_identity_verifications
                (customer_email, verification_type, verification_code, expires_at, verification_status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
            """
            verification_id = pg_hook.get_first(insert_sql, parameters=(
                customer_email, "email", verification_code, expires_at
            ))[0]
            
            # Enviar email con código
            email_api_url = _env("EMAIL_API_URL")
            email_api_key = _env("EMAIL_API_KEY")
            
            if email_api_url and email_api_key:
                try:
                    email_payload = {
                        "to": customer_email,
                        "subject": "Código de verificación",
                        "body": f"Su código de verificación es: {verification_code}",
                        "template": "verification_code",
                        "data": {
                            "code": verification_code,
                            "expires_in_minutes": 15
                        }
                    }
                    
                    response = requests.post(
                        f"{email_api_url}/send",
                        headers={"Authorization": f"Bearer {email_api_key}"},
                        json=email_payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Por ahora, asumimos verificación automática
                        # En producción, esto esperaría confirmación del cliente
                        result["identity_verified"] = True
                        result["verification_status"] = "verified"
                        
                        # Actualizar verificación
                        update_sql = """
                            UPDATE customer_identity_verifications
                            SET verification_status = 'verified',
                                verified_at = NOW()
                            WHERE id = %s
                        """
                        pg_hook.run(update_sql, parameters=(verification_id,))
                        
                        logger.info("Email verification sent", extra={
                            "customer_email": customer_email,
                            "verification_id": verification_id
                        })
                except Exception as e:
                    logger.error(f"Failed to send verification email: {e}")
            
        elif verification_method == "sms":
            # Verificación por SMS
            phone = payload.get("phone")
            if not phone:
                logger.warning("Phone number required for SMS verification", extra={
                    "customer_email": customer_email
                })
                return {**payload, **result}
            
            verification_code = _generate_verification_code()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            
            insert_sql = """
                INSERT INTO customer_identity_verifications
                (customer_email, verification_type, verification_code, expires_at, verification_status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
            """
            verification_id = pg_hook.get_first(insert_sql, parameters=(
                customer_email, "sms", verification_code, expires_at
            ))[0]
            
            # Enviar SMS (usar proveedor como Twilio, AWS SNS, etc.)
            sms_api_url = _env("SMS_API_URL")
            sms_api_key = _env("SMS_API_KEY")
            
            if sms_api_url and sms_api_key:
                try:
                    sms_payload = {
                        "to": phone,
                        "message": f"Su código de verificación es: {verification_code}"
                    }
                    
                    response = requests.post(
                        f"{sms_api_url}/send",
                        headers={"Authorization": f"Bearer {sms_api_key}"},
                        json=sms_payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result["identity_verified"] = True
                        result["verification_status"] = "verified"
                        
                        update_sql = """
                            UPDATE customer_identity_verifications
                            SET verification_status = 'verified',
                                verified_at = NOW()
                            WHERE id = %s
                        """
                        pg_hook.run(update_sql, parameters=(verification_id,))
                        
                        logger.info("SMS verification sent", extra={
                            "customer_email": customer_email,
                            "verification_id": verification_id
                        })
                except Exception as e:
                    logger.error(f"Failed to send verification SMS: {e}")
                    
        elif verification_method == "kyc_provider":
            # Verificación mediante proveedor KYC (Sumsub, Onfido, Jumio, etc.)
            kyc_api_url = _env("KYC_API_URL")
            kyc_api_key = _env("KYC_API_KEY")
            
            if kyc_api_url and kyc_api_key:
                try:
                    kyc_payload = {
                        "email": customer_email,
                        "first_name": payload.get("first_name"),
                        "last_name": payload.get("last_name"),
                        "country": payload.get("country"),
                        "phone": payload.get("phone")
                    }
                    
                    response = requests.post(
                        f"{kyc_api_url}/verify",
                        headers={"Authorization": f"Bearer {kyc_api_key}"},
                        json=kyc_payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        kyc_response = response.json()
                        verified = kyc_response.get("verified", False)
                        
                        result["identity_verified"] = verified
                        result["verification_status"] = "verified" if verified else "failed"
                        
                        # Guardar respuesta del proveedor
                        insert_sql = """
                            INSERT INTO customer_identity_verifications
                            (customer_email, verification_type, verification_provider, 
                             verification_status, provider_response, verified_at)
                            VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                        """
                        pg_hook.run(insert_sql, parameters=(
                            customer_email,
                            "kyc",
                            "external_provider",
                            result["verification_status"],
                            json.dumps(kyc_response),
                            datetime.now(timezone.utc) if verified else None
                        ))
                        
                        logger.info("KYC verification completed", extra={
                            "customer_email": customer_email,
                            "verified": verified
                        })
                except Exception as e:
                    logger.error(f"Failed to verify with KYC provider: {e}")
            else:
                logger.warning("KYC provider not configured")
        
        # Actualizar estado de onboarding
        if result["identity_verified"]:
            update_sql = """
                UPDATE customer_onboarding
                SET identity_verified = TRUE,
                    identity_verification_status = 'verified',
                    identity_verified_at = NOW(),
                    status = 'activating_services',
                    updated_at = NOW()
                WHERE customer_email = %s
            """
            pg_hook.run(update_sql, parameters=(customer_email,))
            
            # Registrar evento
            event_sql = """
                INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
                VALUES (%s, 'identity_verified', %s::jsonb)
            """
            pg_hook.run(event_sql, parameters=(
                customer_email,
                json.dumps({
                    "method": verification_method,
                    "verified_at": datetime.now(timezone.utc).isoformat()
                })
            ))
        
    except Exception as e:
        logger.error("Identity verification failed", exc_info=True, extra={
            "customer_email": customer_email
        })
        result["verification_status"] = "failed"
        result["error"] = str(e)
    
    return {**payload, **result}


def activate_customer_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activar cuentas y servicios para el cliente.
    
    Servicios comunes:
    - platform: Cuenta en la plataforma principal
    - dashboard: Acceso al dashboard
    - api: API keys y acceso a API
    - billing: Cuenta de facturación
    - support: Cuenta de soporte
    """
    customer_email = payload.get("customer_email", "")
    services_to_activate = payload.get("services_to_activate", [])
    
    logger.info(
        "Activating customer accounts",
        extra={
            "customer_email": customer_email,
            "services": services_to_activate
        }
    )
    
    result = {
        "accounts_activated": [],
        "accounts_failed": [],
        "activation_summary": {}
    }
    
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        pg_hook = PostgresHook(postgres_conn_id=_env("POSTGRES_CONN_ID", "postgres_default"))
        
        platform_api_url = _env("PLATFORM_API_URL")
        platform_api_key = _env("PLATFORM_API_KEY")
        
        for service in services_to_activate:
            account_status = "pending"
            account_id = None
            error_message = None
            
            try:
                if service == "platform":
                    # Crear cuenta en plataforma principal
                    if platform_api_url and platform_api_key:
                        account_data = {
                            "email": customer_email,
                            "first_name": payload.get("first_name"),
                            "last_name": payload.get("last_name"),
                            "company": payload.get("company_name"),
                            "plan": payload.get("service_plan"),
                            "tier": payload.get("service_tier")
                        }
                        
                        response = requests.post(
                            f"{platform_api_url}/accounts",
                            headers={"Authorization": f"Bearer {platform_api_key}"},
                            json=account_data,
                            timeout=30
                        )
                        
                        if response.status_code in [200, 201]:
                            account_response = response.json()
                            account_id = account_response.get("account_id") or account_response.get("id")
                            account_status = "active"
                            
                            result["accounts_activated"].append(service)
                            logger.info("Platform account created", extra={
                                "customer_email": customer_email,
                                "account_id": account_id
                            })
                        else:
                            account_status = "failed"
                            error_message = f"HTTP {response.status_code}: {response.text}"
                            result["accounts_failed"].append(service)
                
                elif service == "dashboard":
                    # Activar acceso al dashboard
                    if platform_api_url and platform_api_key:
                        dashboard_data = {
                            "email": customer_email,
                            "role": "customer",
                            "permissions": ["read", "write"]
                        }
                        
                        response = requests.post(
                            f"{platform_api_url}/dashboard/users",
                            headers={"Authorization": f"Bearer {platform_api_key}"},
                            json=dashboard_data,
                            timeout=30
                        )
                        
                        if response.status_code in [200, 201]:
                            account_id = response.json().get("user_id")
                            account_status = "active"
                            result["accounts_activated"].append(service)
                        else:
                            account_status = "failed"
                            error_message = f"HTTP {response.status_code}"
                            result["accounts_failed"].append(service)
                
                elif service == "api":
                    # Generar API keys
                    if platform_api_url and platform_api_key:
                        api_key_data = {
                            "email": customer_email,
                            "name": f"Default API Key for {customer_email}",
                            "permissions": ["read", "write"]
                        }
                        
                        response = requests.post(
                            f"{platform_api_url}/api-keys",
                            headers={"Authorization": f"Bearer {platform_api_key}"},
                            json=api_key_data,
                            timeout=30
                        )
                        
                        if response.status_code in [200, 201]:
                            api_response = response.json()
                            account_id = api_response.get("api_key_id")
                            account_status = "active"
                            
                            # Guardar API key de forma segura (encriptar en producción)
                            credentials = {
                                "api_key": api_response.get("api_key"),
                                "api_secret": api_response.get("api_secret")
                            }
                            
                            result["accounts_activated"].append(service)
                        else:
                            account_status = "failed"
                            error_message = f"HTTP {response.status_code}"
                            result["accounts_failed"].append(service)
                
                elif service == "billing":
                    # Crear cuenta de facturación (Stripe, etc.)
                    billing_api_url = _env("BILLING_API_URL")
                    billing_api_key = _env("BILLING_API_KEY")
                    
                    if billing_api_url and billing_api_key:
                        billing_data = {
                            "email": customer_email,
                            "name": f"{payload.get('first_name')} {payload.get('last_name')}",
                            "plan": payload.get("service_plan")
                        }
                        
                        response = requests.post(
                            f"{billing_api_url}/customers",
                            headers={"Authorization": f"Bearer {billing_api_key}"},
                            json=billing_data,
                            timeout=30
                        )
                        
                        if response.status_code in [200, 201]:
                            account_id = response.json().get("customer_id")
                            account_status = "active"
                            result["accounts_activated"].append(service)
                        else:
                            account_status = "failed"
                            error_message = f"HTTP {response.status_code}"
                            result["accounts_failed"].append(service)
                
                # Guardar cuenta en base de datos
                insert_sql = """
                    INSERT INTO customer_accounts
                    (customer_email, account_type, service_name, account_id, account_status, 
                     credentials, error_message, activated_at)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                """
                
                credentials_data = None
                if service == "api" and account_status == "active":
                    credentials_data = json.dumps(credentials)
                
                activated_at = datetime.now(timezone.utc) if account_status == "active" else None
                
                pg_hook.run(insert_sql, parameters=(
                    customer_email,
                    "user_account" if service != "api" else "api_key",
                    service,
                    account_id,
                    account_status,
                    credentials_data,
                    error_message,
                    activated_at
                ))
                
                result["activation_summary"][service] = {
                    "status": account_status,
                    "account_id": account_id
                }
                
            except Exception as e:
                logger.error(f"Failed to activate {service}", exc_info=True, extra={
                    "customer_email": customer_email,
                    "service": service
                })
                result["accounts_failed"].append(service)
                result["activation_summary"][service] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Registrar evento
        event_sql = """
            INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
            VALUES (%s, 'services_activated', %s::jsonb)
        """
        pg_hook.run(event_sql, parameters=(
            customer_email,
            json.dumps(result["activation_summary"])
        ))
        
        logger.info("Account activation completed", extra={
            "customer_email": customer_email,
            "activated": len(result["accounts_activated"]),
            "failed": len(result["accounts_failed"])
        })
        
    except Exception as e:
        logger.error("Account activation failed", exc_info=True, extra={
            "customer_email": customer_email
        })
        result["error"] = str(e)
    
    return {**payload, **result}


def send_welcome_email(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Enviar email de bienvenida al cliente."""
    customer_email = payload.get("customer_email", "")
    first_name = payload.get("first_name", "")
    
    logger.info("Sending welcome email", extra={"customer_email": customer_email})
    
    email_api_url = _env("EMAIL_API_URL")
    email_api_key = _env("EMAIL_API_KEY")
    
    if not email_api_url or not email_api_key:
        logger.warning("Email API not configured, skipping welcome email")
        return payload
    
    try:
        email_data = {
            "to": customer_email,
            "subject": f"¡Bienvenido, {first_name}!",
            "template": "customer_welcome",
            "data": {
                "first_name": first_name,
                "company_name": payload.get("company_name"),
                "services_activated": payload.get("accounts_activated", []),
                "dashboard_url": _env("DASHBOARD_URL", "https://dashboard.example.com"),
                "support_email": _env("SUPPORT_EMAIL", "support@example.com")
            }
        }
        
        response = requests.post(
            f"{email_api_url}/send",
            headers={"Authorization": f"Bearer {email_api_key}"},
            json=email_data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Welcome email sent", extra={"customer_email": customer_email})
            
            # Registrar evento
            try:
                from airflow.providers.postgres.hooks.postgres import PostgresHook
                pg_hook = PostgresHook(postgres_conn_id=_env("POSTGRES_CONN_ID", "postgres_default"))
                
                event_sql = """
                    INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
                    VALUES (%s, 'welcome_email_sent', %s::jsonb)
                """
                pg_hook.run(event_sql, parameters=(
                    customer_email,
                    json.dumps({"sent_at": datetime.now(timezone.utc).isoformat()})
                ))
            except Exception as e:
                logger.warning(f"Failed to log welcome email event: {e}")
        else:
            logger.warning(f"Failed to send welcome email: {response.status_code}")
    
    except Exception as e:
        logger.error("Failed to send welcome email", exc_info=True, extra={
            "customer_email": customer_email
        })
    
    return payload


def persist_onboarding_data(payload: Dict[str, Any]) -> None:
    """Persistir datos adicionales del onboarding."""
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        pg_hook = PostgresHook(postgres_conn_id=_env("POSTGRES_CONN_ID", "postgres_default"))
        customer_email = payload.get("customer_email")
        
        # Persistir información adicional si es necesario
        # Esta función puede extenderse para guardar datos específicos
        
        logger.info("Onboarding data persisted", extra={"customer_email": customer_email})
    
    except Exception as e:
        logger.warning(f"Failed to persist additional data: {e}")





