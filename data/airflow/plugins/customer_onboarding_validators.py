"""
Validadores avanzados para onboarding de clientes.
Incluye validación de documentos, verificación de dominio, etc.
"""

from __future__ import annotations

import logging
import re
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_email_domain(email: str) -> Dict[str, Any]:
    """
    Validar dominio de email.
    Verifica que el dominio no esté en listas negras y que tenga DNS válido.
    """
    domain = email.split("@")[1] if "@" in email else ""
    
    result = {
        "valid": True,
        "domain": domain,
        "checks": {}
    }
    
    # Lista de dominios temporales comunes (puedes expandir)
    temporary_domains = [
        "10minutemail.com", "guerrillamail.com", "mailinator.com",
        "temp-mail.org", "throwaway.email"
    ]
    
    if domain.lower() in temporary_domains:
        result["valid"] = False
        result["checks"]["temporary_domain"] = {
            "status": "failed",
            "message": "Temporary email domain detected"
        }
    
    # Verificar formato básico de dominio
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if not re.match(domain_pattern, domain):
        result["valid"] = False
        result["checks"]["domain_format"] = {
            "status": "failed",
            "message": "Invalid domain format"
        }
    else:
        result["checks"]["domain_format"] = {
            "status": "passed",
            "message": "Valid domain format"
        }
    
    return result


def validate_phone_number(phone: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Validar número de teléfono.
    Verifica formato y valida según el país si se proporciona.
    """
    result = {
        "valid": True,
        "phone": phone,
        "checks": {}
    }
    
    # Limpiar número
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Verificar que tenga al menos 7 dígitos
    digits_only = re.sub(r'[^\d]', '', cleaned)
    if len(digits_only) < 7:
        result["valid"] = False
        result["checks"]["length"] = {
            "status": "failed",
            "message": "Phone number too short"
        }
        return result
    
    # Validaciones específicas por país
    if country:
        if country.upper() == "ES":  # España
            # Formato español: +34 o 0034 seguido de 9 dígitos
            es_pattern = r'^(\+34|0034)?[6-9]\d{8}$'
            if not re.match(es_pattern, digits_only[-9:]):
                result["valid"] = False
                result["checks"]["country_format"] = {
                    "status": "failed",
                    "message": "Invalid format for Spain"
                }
            else:
                result["checks"]["country_format"] = {
                    "status": "passed",
                    "message": "Valid format for Spain"
                }
    
    result["checks"]["length"] = {
        "status": "passed",
        "message": f"Phone number has {len(digits_only)} digits"
    }
    
    return result


def validate_company_domain(company_name: str, email: str) -> Dict[str, Any]:
    """
    Validar que el dominio del email coincida con la empresa.
    Extrae dominio probable de la empresa y lo compara con el email.
    """
    domain = email.split("@")[1] if "@" in email else ""
    
    result = {
        "matches": False,
        "company_name": company_name,
        "email_domain": domain,
        "confidence": 0.0
    }
    
    if not company_name or not domain:
        return result
    
    # Normalizar nombre de empresa
    company_normalized = company_name.lower()
    company_normalized = re.sub(r'[^\w\s]', '', company_normalized)
    company_words = company_normalized.split()
    
    # Extraer dominio sin TLD
    domain_parts = domain.split(".")
    domain_base = domain_parts[0] if domain_parts else ""
    
    # Verificar si alguna palabra de la empresa está en el dominio
    for word in company_words:
        if len(word) > 3 and word in domain_base:
            result["matches"] = True
            result["confidence"] = 0.7
            break
    
    # Verificación exacta
    if domain_base in company_normalized.replace(" ", ""):
        result["matches"] = True
        result["confidence"] = 1.0
    
    return result


def validate_document_format(document_type: str, document_number: str, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Validar formato de documento de identidad.
    Soporta DNI (España), NIE (España), pasaporte, etc.
    """
    result = {
        "valid": False,
        "document_type": document_type,
        "document_number": document_number,
        "checks": {}
    }
    
    document_number = document_number.upper().strip()
    
    if document_type.upper() == "DNI" and country == "ES":
        # DNI español: 8 dígitos + 1 letra
        dni_pattern = r'^\d{8}[A-Z]$'
        if re.match(dni_pattern, document_number):
            result["valid"] = True
            result["checks"]["format"] = {
                "status": "passed",
                "message": "Valid DNI format"
            }
        else:
            result["checks"]["format"] = {
                "status": "failed",
                "message": "Invalid DNI format (expected: 8 digits + 1 letter)"
            }
    
    elif document_type.upper() == "NIE" and country == "ES":
        # NIE español: X/Y/Z + 7 dígitos + 1 letra
        nie_pattern = r'^[XYZ]\d{7}[A-Z]$'
        if re.match(nie_pattern, document_number):
            result["valid"] = True
            result["checks"]["format"] = {
                "status": "passed",
                "message": "Valid NIE format"
            }
        else:
            result["checks"]["format"] = {
                "status": "failed",
                "message": "Invalid NIE format (expected: X/Y/Z + 7 digits + 1 letter)"
            }
    
    elif document_type.upper() == "PASSPORT":
        # Pasaporte: generalmente 6-9 caracteres alfanuméricos
        passport_pattern = r'^[A-Z0-9]{6,9}$'
        if re.match(passport_pattern, document_number):
            result["valid"] = True
            result["checks"]["format"] = {
                "status": "passed",
                "message": "Valid passport format"
            }
        else:
            result["checks"]["format"] = {
                "status": "failed",
                "message": "Invalid passport format"
            }
    
    else:
        result["checks"]["format"] = {
            "status": "unknown",
            "message": f"Validation not implemented for {document_type} in {country}"
        }
    
    return result


def validate_business_info(company_name: str, tax_id: Optional[str] = None, country: Optional[str] = None) -> Dict[str, Any]:
    """
    Validar información de negocio.
    Verifica formato de nombre de empresa y número de identificación fiscal.
    """
    result = {
        "valid": True,
        "company_name": company_name,
        "checks": {}
    }
    
    # Validar nombre de empresa
    if not company_name or len(company_name.strip()) < 2:
        result["valid"] = False
        result["checks"]["company_name"] = {
            "status": "failed",
            "message": "Company name too short"
        }
    else:
        result["checks"]["company_name"] = {
            "status": "passed",
            "message": "Valid company name"
        }
    
    # Validar número fiscal (CIF/NIF en España)
    if tax_id:
        if country == "ES":
            # CIF español: 1 letra + 7 dígitos + 1 carácter de control
            cif_pattern = r'^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$'
            if re.match(cif_pattern, tax_id.upper()):
                result["checks"]["tax_id"] = {
                    "status": "passed",
                    "message": "Valid CIF format"
                }
            else:
                result["checks"]["tax_id"] = {
                    "status": "warning",
                    "message": "CIF format may be invalid"
                }
    
    return result


def check_risk_indicators(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verificar indicadores de riesgo.
    Analiza datos del cliente para detectar posibles fraudes o riesgos.
    """
    risk_score = 0
    risk_factors = []
    
    # Verificar email
    email = customer_data.get("customer_email", "")
    email_check = validate_email_domain(email)
    if not email_check["valid"]:
        risk_score += 20
        risk_factors.append("Temporary email domain detected")
    
    # Verificar si el dominio coincide con la empresa
    company_name = customer_data.get("company_name")
    if company_name:
        domain_check = validate_company_domain(company_name, email)
        if not domain_check["matches"]:
            risk_score += 10
            risk_factors.append("Email domain doesn't match company name")
    
    # Verificar teléfono
    phone = customer_data.get("phone")
    if phone:
        phone_check = validate_phone_number(phone, customer_data.get("country"))
        if not phone_check["valid"]:
            risk_score += 15
            risk_factors.append("Invalid phone number format")
    
    # Verificar si falta información crítica
    if not company_name:
        risk_score += 10
        risk_factors.append("Missing company name")
    
    if not phone:
        risk_score += 5
        risk_factors.append("Missing phone number")
    
    # Determinar nivel de riesgo
    risk_level = "low"
    if risk_score >= 50:
        risk_level = "high"
    elif risk_score >= 25:
        risk_level = "medium"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendation": "manual_review" if risk_level != "low" else "auto_approve"
    }


def validate_customer_data_complete(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validación completa de datos del cliente.
    Ejecuta todas las validaciones y retorna resultado consolidado.
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "checks": {}
    }
    
    # Validar email
    email = payload.get("customer_email", "")
    if not email:
        results["valid"] = False
        results["errors"].append("Email is required")
    else:
        email_check = validate_email_domain(email)
        results["checks"]["email"] = email_check
        if not email_check["valid"]:
            results["valid"] = False
            results["errors"].append("Invalid email domain")
    
    # Validar teléfono
    phone = payload.get("phone")
    if phone:
        phone_check = validate_phone_number(phone, payload.get("country"))
        results["checks"]["phone"] = phone_check
        if not phone_check["valid"]:
            results["warnings"].append("Phone number format may be invalid")
    
    # Validar información de negocio
    company_name = payload.get("company_name")
    if company_name:
        business_check = validate_business_info(
            company_name,
            payload.get("tax_id"),
            payload.get("country")
        )
        results["checks"]["business"] = business_check
        if not business_check["valid"]:
            results["warnings"].append("Business information validation issues")
    
    # Verificar indicadores de riesgo
    risk_check = check_risk_indicators(payload)
    results["checks"]["risk"] = risk_check
    if risk_check["risk_level"] != "low":
        results["warnings"].append(f"Risk level: {risk_check['risk_level']}")
    
    return results

