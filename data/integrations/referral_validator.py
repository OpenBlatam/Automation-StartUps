"""
Módulo de Validación de Referidos con Detección de Fraude

Este módulo proporciona funciones avanzadas para validar referidos
y detectar patrones de fraude en programas de referidos.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReferralValidator:
    """
    Validador de referidos con detección avanzada de fraude.
    """
    
    def __init__(self, db_hook=None):
        """
        Inicializa el validador.
        
        Args:
            db_hook: Hook de base de datos (PostgresHook de Airflow)
        """
        self.db_hook = db_hook
        self.fraud_patterns = []
    
    def validate_referral(
        self,
        referral_id: str,
        referrer_email: str,
        referred_email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referral_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida un referido y detecta posibles fraudes.
        
        Args:
            referral_id: ID del referido
            referrer_email: Email del referidor
            referred_email: Email del referido
            ip_address: Dirección IP del referido
            user_agent: User agent del navegador
            referral_code: Código de referido usado
        
        Returns:
            Dict con resultado de validación
        """
        validation_result = {
            "is_valid": True,
            "fraud_detected": False,
            "fraud_reasons": [],
            "risk_score": 0.0,
            "warnings": []
        }
        
        # Validación 1: Auto-referido
        if self._is_auto_referral(referrer_email, referred_email):
            validation_result["is_valid"] = False
            validation_result["fraud_detected"] = True
            validation_result["fraud_reasons"].append("Auto-referido: mismo email")
            validation_result["risk_score"] = 10.0
            return validation_result
        
        # Validación 2: Email duplicado (ya existe como lead)
        if self._is_duplicate_email(referred_email, referral_id):
            validation_result["is_valid"] = False
            validation_result["fraud_detected"] = True
            validation_result["fraud_reasons"].append("Email ya existe como lead previo")
            validation_result["risk_score"] = 9.0
            return validation_result
        
        # Validación 3: Múltiples referidos desde misma IP
        if ip_address:
            ip_risk = self._check_ip_risk(ip_address, referral_id)
            if ip_risk["risk_score"] > 7.0:
                validation_result["is_valid"] = False
                validation_result["fraud_detected"] = True
                validation_result["fraud_reasons"].extend(ip_risk["reasons"])
                validation_result["risk_score"] = ip_risk["risk_score"]
                return validation_result
            elif ip_risk["risk_score"] > 5.0:
                validation_result["warnings"].extend(ip_risk["reasons"])
                validation_result["risk_score"] = max(validation_result["risk_score"], ip_risk["risk_score"])
        
        # Validación 4: Patrón de emails sospechosos
        email_risk = self._check_email_pattern(referred_email)
        if email_risk["risk_score"] > 6.0:
            validation_result["warnings"].extend(email_risk["reasons"])
            validation_result["risk_score"] = max(validation_result["risk_score"], email_risk["risk_score"])
        
        # Validación 5: Múltiples referidos del mismo referidor en corto tiempo
        referrer_risk = self._check_referrer_pattern(referrer_email, referral_id)
        if referrer_risk["risk_score"] > 7.0:
            validation_result["is_valid"] = False
            validation_result["fraud_detected"] = True
            validation_result["fraud_reasons"].extend(referrer_risk["reasons"])
            validation_result["risk_score"] = referrer_risk["risk_score"]
            return validation_result
        elif referrer_risk["risk_score"] > 5.0:
            validation_result["warnings"].extend(referrer_risk["reasons"])
            validation_result["risk_score"] = max(validation_result["risk_score"], referrer_risk["risk_score"])
        
        # Validación 6: Código de referido válido
        if referral_code:
            code_valid = self._validate_referral_code(referral_code, referrer_email)
            if not code_valid["is_valid"]:
                validation_result["is_valid"] = False
                validation_result["fraud_detected"] = True
                validation_result["fraud_reasons"].extend(code_valid["reasons"])
                validation_result["risk_score"] = 10.0
                return validation_result
        
        return validation_result
    
    def _is_auto_referral(self, referrer_email: str, referred_email: str) -> bool:
        """Verifica si es un auto-referido."""
        return referrer_email.lower().strip() == referred_email.lower().strip()
    
    def _is_duplicate_email(self, email: str, referral_id: str) -> bool:
        """Verifica si el email ya existe como lead antes del referido."""
        if not self.db_hook:
            return False
        
        try:
            query = """
                SELECT 
                    ol.lead_id,
                    ol.created_at,
                    r.referral_id,
                    r.created_at as referral_created_at
                FROM organic_leads ol
                LEFT JOIN referrals r ON r.referral_id = %s
                WHERE ol.email = %s
                AND ol.created_at < COALESCE(r.created_at, NOW())
                LIMIT 1
            """
            
            result = self.db_hook.get_first(query, parameters=(referral_id, email))
            return result is not None
        except Exception as e:
            logger.error(f"Error verificando email duplicado: {e}")
            return False
    
    def _check_ip_risk(self, ip_address: str, referral_id: str) -> Dict[str, Any]:
        """Verifica riesgo asociado a una IP."""
        if not self.db_hook:
            return {"risk_score": 0.0, "reasons": []}
        
        try:
            # Contar referidos desde misma IP en última hora
            query = """
                SELECT COUNT(*) 
                FROM referrals
                WHERE ip_address = %s
                AND created_at > NOW() - INTERVAL '1 hour'
                AND referral_id != %s
            """
            
            result = self.db_hook.get_first(query, parameters=(ip_address, referral_id))
            count = result[0] if result else 0
            
            risk_score = 0.0
            reasons = []
            
            if count > 10:
                risk_score = 10.0
                reasons.append(f"Múltiples referidos desde misma IP: {count} en última hora")
            elif count > 5:
                risk_score = 7.0
                reasons.append(f"Muchos referidos desde misma IP: {count} en última hora")
            elif count > 3:
                risk_score = 5.0
                reasons.append(f"Varios referidos desde misma IP: {count} en última hora")
            
            return {"risk_score": risk_score, "reasons": reasons}
        except Exception as e:
            logger.error(f"Error verificando IP: {e}")
            return {"risk_score": 0.0, "reasons": []}
    
    def _check_email_pattern(self, email: str) -> Dict[str, Any]:
        """Verifica patrones sospechosos en el email."""
        risk_score = 0.0
        reasons = []
        
        # Email temporal o desechable
        disposable_domains = [
            "tempmail", "10minutemail", "guerrillamail", "mailinator",
            "throwaway", "trashmail", "getnada", "mohmal"
        ]
        
        email_lower = email.lower()
        for domain in disposable_domains:
            if domain in email_lower:
                risk_score = 6.0
                reasons.append("Email desechable detectado")
                break
        
        # Patrón de números secuenciales
        import re
        if re.search(r'\d{4,}', email):
            risk_score = max(risk_score, 4.0)
            reasons.append("Patrón numérico sospechoso en email")
        
        # Email muy corto o muy largo
        if len(email) < 5 or len(email) > 100:
            risk_score = max(risk_score, 3.0)
            reasons.append("Email con longitud sospechosa")
        
        return {"risk_score": risk_score, "reasons": reasons}
    
    def _check_referrer_pattern(self, referrer_email: str, referral_id: str) -> Dict[str, Any]:
        """Verifica patrones sospechosos del referidor."""
        if not self.db_hook:
            return {"risk_score": 0.0, "reasons": []}
        
        try:
            # Contar referidos del mismo referidor en última hora
            query = """
                SELECT COUNT(*) 
                FROM referrals r
                JOIN organic_leads ol ON r.referrer_lead_id = ol.lead_id
                WHERE ol.email = %s
                AND r.created_at > NOW() - INTERVAL '1 hour'
                AND r.referral_id != %s
            """
            
            result = self.db_hook.get_first(query, parameters=(referrer_email, referral_id))
            count = result[0] if result else 0
            
            risk_score = 0.0
            reasons = []
            
            if count > 20:
                risk_score = 10.0
                reasons.append(f"Demasiados referidos en corto tiempo: {count} en última hora")
            elif count > 10:
                risk_score = 8.0
                reasons.append(f"Muchos referidos en corto tiempo: {count} en última hora")
            elif count > 5:
                risk_score = 6.0
                reasons.append(f"Varios referidos en corto tiempo: {count} en última hora")
            
            return {"risk_score": risk_score, "reasons": reasons}
        except Exception as e:
            logger.error(f"Error verificando patrón de referidor: {e}")
            return {"risk_score": 0.0, "reasons": []}
    
    def _validate_referral_code(self, referral_code: str, referrer_email: str) -> Dict[str, Any]:
        """Valida que el código de referido pertenezca al referidor."""
        if not self.db_hook:
            return {"is_valid": True, "reasons": []}
        
        try:
            query = """
                SELECT rp.referral_code, ol.email
                FROM referral_programs rp
                JOIN organic_leads ol ON rp.lead_id = ol.lead_id
                WHERE rp.referral_code = %s
                AND ol.email = %s
                AND rp.status = 'active'
            """
            
            result = self.db_hook.get_first(query, parameters=(referral_code, referrer_email))
            
            if not result:
                return {
                    "is_valid": False,
                    "reasons": ["Código de referido no válido o no pertenece al referidor"]
                }
            
            return {"is_valid": True, "reasons": []}
        except Exception as e:
            logger.error(f"Error validando código: {e}")
            return {"is_valid": True, "reasons": []}  # Por defecto válido si hay error
    
    def batch_validate(self, referrals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valida múltiples referidos en batch.
        
        Args:
            referrals: Lista de dicts con datos de referidos
        
        Returns:
            Lista de resultados de validación
        """
        results = []
        
        for referral in referrals:
            validation = self.validate_referral(
                referral_id=referral.get("referral_id", ""),
                referrer_email=referral.get("referrer_email", ""),
                referred_email=referral.get("referred_email", ""),
                ip_address=referral.get("ip_address"),
                user_agent=referral.get("user_agent"),
                referral_code=referral.get("referral_code")
            )
            
            results.append({
                "referral_id": referral.get("referral_id"),
                **validation
            })
        
        return results


def generate_referral_code(email: str, salt: Optional[str] = None) -> str:
    """
    Genera un código único de referido.
    
    Args:
        email: Email del referidor
        salt: Salt opcional para mayor seguridad
    
    Returns:
        Código de referido único
    """
    import secrets
    import time
    
    if not salt:
        salt = secrets.token_hex(8)
    
    hash_input = f"{email}{salt}{time.time()}"
    hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
    return f"REF-{hash_value.upper()}"


def generate_referral_link(base_url: str, code: str, utm_params: Optional[Dict[str, str]] = None) -> str:
    """
    Genera un enlace de referido con tracking.
    
    Args:
        base_url: URL base del sitio
        code: Código de referido
        utm_params: Parámetros UTM opcionales
    
    Returns:
        Enlace completo de referido
    """
    link = f"{base_url.rstrip('/')}/refer/{code}"
    
    if utm_params:
        params = "&".join([f"{k}={v}" for k, v in utm_params.items()])
        link = f"{link}?{params}"
    
    return link

