"""
Módulo de Validación Avanzada de Contratos
Incluye validación de contenido, variables y reglas de negocio
"""

from __future__ import annotations

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date

logger = logging.getLogger("airflow.task")


class ContractValidator:
    """Validador avanzado de contratos"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_template(self, template_content: str, template_variables: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida que un template tenga todas las variables requeridas.
        
        Args:
            template_content: Contenido del template
            template_variables: Variables disponibles
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        self.errors = []
        
        # Extraer variables del template
        template_vars = self._extract_template_variables(template_content)
        
        # Verificar que todas las variables estén disponibles
        missing_vars = []
        for var in template_vars:
            if var not in template_variables:
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"Variables faltantes en template: {', '.join(missing_vars)}")
        
        # Verificar variables no usadas (warning)
        unused_vars = [v for v in template_variables.keys() if v not in template_vars]
        if unused_vars:
            self.warnings.append(f"Variables no usadas: {', '.join(unused_vars)}")
        
        return len(self.errors) == 0, self.errors
    
    def validate_contract_data(self, contract_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida datos de un contrato antes de crearlo.
        
        Args:
            contract_data: Datos del contrato
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        self.errors = []
        
        # Validar email
        email = contract_data.get("primary_party_email", "")
        if not self._validate_email(email):
            self.errors.append(f"Email inválido: {email}")
        
        # Validar fechas
        start_date = contract_data.get("start_date")
        if start_date:
            if not self._validate_date(start_date):
                self.errors.append(f"Fecha de inicio inválida: {start_date}")
        
        expiration_days = contract_data.get("expiration_days")
        if expiration_days and expiration_days < 0:
            self.errors.append("expiration_days no puede ser negativo")
        
        # Validar que haya al menos un firmante
        signers = contract_data.get("signers_required", [])
        if not signers:
            self.warnings.append("No hay firmantes configurados")
        
        # Validar firmantes
        signer_emails = []
        for signer in signers:
            signer_email = signer.get("email", "")
            if not self._validate_email(signer_email):
                self.errors.append(f"Email de firmante inválido: {signer_email}")
            if signer_email in signer_emails:
                self.errors.append(f"Firmante duplicado: {signer_email}")
            signer_emails.append(signer_email)
        
        return len(self.errors) == 0, self.errors
    
    def validate_contract_content(self, contract_content: str) -> Tuple[bool, List[str]]:
        """
        Valida el contenido del contrato generado.
        
        Args:
            contract_content: Contenido del contrato
            
        Returns:
            Tuple (is_valid, list_of_warnings)
        """
        self.warnings = []
        
        # Verificar variables no reemplazadas
        unmatched_vars = re.findall(r'\{\{(\w+)\}\}', contract_content)
        if unmatched_vars:
            self.warnings.append(f"Variables no reemplazadas encontradas: {', '.join(set(unmatched_vars))}")
        
        # Verificar longitud mínima
        if len(contract_content.strip()) < 100:
            self.warnings.append("Contenido del contrato muy corto (menos de 100 caracteres)")
        
        # Verificar contenido sospechoso
        suspicious_patterns = [
            (r'TEST|DUMMY|EXAMPLE', "Texto de prueba encontrado"),
            (r'XXXX|XXXXX', "Placeholders no reemplazados"),
        ]
        
        for pattern, message in suspicious_patterns:
            if re.search(pattern, contract_content, re.IGNORECASE):
                self.warnings.append(message)
        
        return True, self.warnings  # No es error crítico, solo warnings
    
    def _extract_template_variables(self, template_content: str) -> List[str]:
        """Extrae variables del template usando regex"""
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, template_content)
        return list(set(matches))
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_date(self, date_str: str) -> bool:
        """Valida formato de fecha YYYY-MM-DD"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class ContractBusinessRulesValidator:
    """Validador de reglas de negocio"""
    
    @staticmethod
    def validate_contract_duration(contract_type: str, duration_days: int) -> Tuple[bool, Optional[str]]:
        """
        Valida que la duración del contrato sea apropiada para su tipo.
        
        Args:
            contract_type: Tipo de contrato
            duration_days: Duración en días
            
        Returns:
            Tuple (is_valid, error_message)
        """
        rules = {
            "employment": (30, 3650),  # 1 mes a 10 años
            "service": (1, 365),  # 1 día a 1 año
            "nda": (365, 3650),  # 1 a 10 años
            "vendor": (30, 1825),  # 1 mes a 5 años
            "client": (30, 1825),  # 1 mes a 5 años
            "lease": (365, 3650),  # 1 a 10 años
        }
        
        if contract_type not in rules:
            return True, None  # Sin regla específica
        
        min_days, max_days = rules[contract_type]
        
        if duration_days < min_days:
            return False, f"Duración mínima para {contract_type} es {min_days} días"
        
        if duration_days > max_days:
            return False, f"Duración máxima para {contract_type} es {max_days} días"
        
        return True, None
    
    @staticmethod
    def validate_signers_order(signers: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Valida que el orden de firmantes sea lógico.
        
        Args:
            signers: Lista de firmantes con 'order' o 'routing_order'
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not signers:
            return False, "Debe haber al menos un firmante"
        
        orders = []
        for signer in signers:
            order = signer.get("order") or signer.get("routing_order")
            if order is None:
                return False, "Todos los firmantes deben tener un orden definido"
            orders.append(order)
        
        # Verificar que los órdenes sean secuenciales empezando desde 1
        expected_orders = list(range(1, len(signers) + 1))
        if sorted(orders) != expected_orders:
            return False, f"Órdenes de firma deben ser secuenciales: {expected_orders}"
        
        return True, None
    
    @staticmethod
    def validate_expiration_date(start_date: date, expiration_date: date) -> Tuple[bool, Optional[str]]:
        """
        Valida que la fecha de expiración sea posterior a la de inicio.
        
        Args:
            start_date: Fecha de inicio
            expiration_date: Fecha de expiración
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if expiration_date <= start_date:
            return False, "La fecha de expiración debe ser posterior a la fecha de inicio"
        
        return True, None


def validate_contract_complete(
    template_content: str,
    contract_variables: Dict[str, Any],
    contract_data: Dict[str, Any]
) -> Tuple[bool, List[str], List[str]]:
    """
    Valida completamente un contrato antes de crearlo.
    
    Args:
        template_content: Contenido del template
        contract_variables: Variables para el template
        contract_data: Datos del contrato
        
    Returns:
        Tuple (is_valid, list_of_errors, list_of_warnings)
    """
    validator = ContractValidator()
    business_validator = ContractBusinessRulesValidator()
    
    errors = []
    warnings = []
    
    # Validar template
    template_valid, template_errors = validator.validate_template(template_content, contract_variables)
    errors.extend(template_errors)
    warnings.extend(validator.warnings)
    
    # Validar datos del contrato
    data_valid, data_errors = validator.validate_contract_data(contract_data)
    errors.extend(data_errors)
    warnings.extend(validator.warnings)
    
    # Validar reglas de negocio
    contract_type = contract_data.get("contract_type", "")
    expiration_days = contract_data.get("expiration_days")
    if expiration_days:
        duration_valid, duration_error = business_validator.validate_contract_duration(
            contract_type, expiration_days
        )
        if not duration_valid:
            errors.append(duration_error)
    
    # Validar orden de firmantes
    signers = contract_data.get("signers_required", [])
    if signers:
        order_valid, order_error = business_validator.validate_signers_order(signers)
        if not order_valid:
            errors.append(order_error)
    
    # Validar fechas
    start_date_str = contract_data.get("start_date")
    expiration_days = contract_data.get("expiration_days")
    if start_date_str and expiration_days:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            expiration_date = start_date + timedelta(days=expiration_days)
            date_valid, date_error = business_validator.validate_expiration_date(
                start_date, expiration_date
            )
            if not date_valid:
                errors.append(date_error)
        except Exception as e:
            errors.append(f"Error validando fechas: {e}")
    
    return len(errors) == 0, errors, warnings

