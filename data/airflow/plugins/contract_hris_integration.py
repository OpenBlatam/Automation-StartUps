"""
Integración Avanzada con Sistemas HRIS
Obtiene datos automáticos para contratos laborales
"""

from __future__ import annotations

import logging
import os
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("airflow.task")


class HRISIntegration:
    """Integración con sistemas HRIS (Workday, BambooHR, etc.)"""
    
    def __init__(self, hris_type: str = None, api_url: str = None, api_key: str = None):
        """
        Inicializa integración con HRIS.
        
        Args:
            hris_type: Tipo de HRIS ('workday', 'bamboohr', 'bizneo', 'custom')
            api_url: URL base de la API
            api_key: API key o token
        """
        self.hris_type = hris_type or os.getenv("HRIS_TYPE", "").lower()
        self.api_url = api_url or os.getenv("HRIS_API_URL", "")
        self.api_key = api_key or os.getenv("HRIS_API_KEY", "")
    
    def get_employee_data(self, employee_email: str) -> Dict[str, Any]:
        """
        Obtiene datos de empleado desde HRIS.
        
        Args:
            employee_email: Email del empleado
            
        Returns:
            Dict con datos del empleado
        """
        if not self.api_url or not self.api_key:
            logger.warning("HRIS no configurado, retornando datos vacíos")
            return {}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            if self.hris_type == "workday":
                return self._get_workday_employee(employee_email, headers)
            elif self.hris_type == "bamboohr":
                return self._get_bamboohr_employee(employee_email, headers)
            elif self.hris_type == "bizneo":
                return self._get_bizneo_employee(employee_email, headers)
            else:
                # API genérica
                return self._get_generic_employee(employee_email, headers)
        except Exception as e:
            logger.error(f"Error obteniendo datos de HRIS: {e}")
            return {}
    
    def _get_workday_employee(self, employee_email: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Obtiene empleado de Workday"""
        # Workday usa SOAP API, simplificado aquí
        url = f"{self.api_url}/workers"
        params = {"email": employee_email}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Mapear a formato estándar
        return {
            "employee_id": data.get("worker_id"),
            "full_name": data.get("legal_name"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": employee_email,
            "position": data.get("position"),
            "department": data.get("organization"),
            "manager_email": data.get("supervisor_email"),
            "manager_name": data.get("supervisor_name"),
            "location": data.get("location"),
            "start_date": data.get("hire_date"),
            "salary": data.get("base_pay"),
            "employee_type": data.get("worker_type"),
            "source": "workday"
        }
    
    def _get_bamboohr_employee(self, employee_email: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Obtiene empleado de BambooHR"""
        url = f"{self.api_url}/employees"
        params = {"email": employee_email}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "employee_id": data.get("id"),
            "full_name": f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
            "first_name": data.get("firstName"),
            "last_name": data.get("lastName"),
            "email": employee_email,
            "position": data.get("jobTitle"),
            "department": data.get("department"),
            "manager_email": data.get("supervisorEmail"),
            "location": data.get("location"),
            "start_date": data.get("hireDate"),
            "source": "bamboohr"
        }
    
    def _get_bizneo_employee(self, employee_email: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Obtiene empleado de Bizneo HR"""
        url = f"{self.api_url}/employees"
        params = {"email": employee_email}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "employee_id": data.get("employee_id"),
            "full_name": data.get("full_name"),
            "email": employee_email,
            "position": data.get("position"),
            "department": data.get("department"),
            "manager_email": data.get("manager_email"),
            "start_date": data.get("start_date"),
            "source": "bizneo"
        }
    
    def _get_generic_employee(self, employee_email: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Obtiene empleado de API genérica"""
        url = f"{self.api_url}/employees/{employee_email}"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()


def enrich_contract_with_hris_data(
    contract_variables: Dict[str, Any],
    employee_email: str,
    hris_type: str = None
) -> Dict[str, Any]:
    """
    Enriquece variables de contrato con datos de HRIS.
    
    Args:
        contract_variables: Variables actuales del contrato
        employee_email: Email del empleado
        hris_type: Tipo de HRIS (opcional, se detecta automáticamente)
        
    Returns:
        Dict con variables enriquecidas
    """
    hris = HRISIntegration(hris_type=hris_type)
    employee_data = hris.get_employee_data(employee_email)
    
    if not employee_data:
        return contract_variables
    
    # Enriquecer variables
    enriched = contract_variables.copy()
    
    # Mapear campos comunes
    field_mapping = {
        "employee_name": "full_name",
        "employee_email": "email",
        "position": "position",
        "department": "department",
        "manager_email": "manager_email",
        "manager_name": "manager_name",
        "start_date": "start_date",
        "location": "location",
        "salary": "salary"
    }
    
    for contract_key, hris_key in field_mapping.items():
        if contract_key not in enriched and hris_key in employee_data:
            enriched[contract_key] = employee_data[hris_key]
    
    # Agregar metadata
    enriched["hris_source"] = employee_data.get("source", "unknown")
    enriched["hris_employee_id"] = employee_data.get("employee_id")
    
    logger.info(
        f"Datos enriquecidos desde HRIS",
        extra={
            "employee_email": employee_email,
            "hris_source": employee_data.get("source"),
            "fields_added": len([k for k in field_mapping.values() if k in employee_data])
        }
    )
    
    return enriched

