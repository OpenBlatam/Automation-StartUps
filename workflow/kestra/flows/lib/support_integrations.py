"""
Integraciones con Sistemas Externos Populares.

Soporta:
- Zendesk
- Freshdesk
- Intercom
- Salesforce Service Cloud
- Jira Service Management
"""
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class IntegrationConfig:
    """Configuración de integración."""
    system: str  # zendesk, freshdesk, intercom, salesforce, jira
    api_url: str
    api_key: str
    api_secret: Optional[str] = None
    enabled: bool = True


class SupportIntegrations:
    """Gestor de integraciones con sistemas externos."""
    
    def __init__(self, integrations: List[IntegrationConfig]):
        """
        Inicializa el gestor de integraciones.
        
        Args:
            integrations: Lista de configuraciones de integraciones
        """
        self.integrations = {i.system: i for i in integrations if i.enabled}
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
    
    def sync_to_zendesk(
        self,
        ticket_data: Dict[str, Any],
        config: IntegrationConfig
    ) -> Optional[str]:
        """Sincroniza ticket a Zendesk."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Crear ticket en Zendesk
            url = f"{config.api_url}/api/v2/tickets.json"
            auth = (f"{config.api_key}/token", config.api_secret or "")
            
            payload = {
                "ticket": {
                    "subject": ticket_data.get("subject", "Support Ticket"),
                    "comment": {
                        "body": ticket_data.get("description", "")
                    },
                    "priority": ticket_data.get("priority", "normal"),
                    "type": "question",
                    "requester": {
                        "email": ticket_data.get("customer_email", ""),
                        "name": ticket_data.get("customer_name", "")
                    },
                    "tags": ticket_data.get("tags", [])
                }
            }
            
            response = self.session.post(
                url,
                json=payload,
                auth=auth,
                timeout=10
            )
            response.raise_for_status()
            
            zendesk_ticket = response.json().get("ticket", {})
            zendesk_id = str(zendesk_ticket.get("id"))
            
            logger.info(f"Ticket synced to Zendesk: {zendesk_id}")
            return zendesk_id
            
        except Exception as e:
            logger.error(f"Error syncing to Zendesk: {e}")
            return None
    
    def sync_to_freshdesk(
        self,
        ticket_data: Dict[str, Any],
        config: IntegrationConfig
    ) -> Optional[str]:
        """Sincroniza ticket a Freshdesk."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"{config.api_url}/api/v2/tickets"
            auth = (config.api_key, "X")
            
            payload = {
                "email": ticket_data.get("customer_email", ""),
                "subject": ticket_data.get("subject", "Support Ticket"),
                "description": ticket_data.get("description", ""),
                "priority": self._map_priority_to_freshdesk(ticket_data.get("priority", "medium")),
                "status": 2,  # Open
                "tags": ticket_data.get("tags", [])
            }
            
            response = self.session.post(
                url,
                json=payload,
                auth=auth,
                timeout=10
            )
            response.raise_for_status()
            
            freshdesk_ticket = response.json()
            freshdesk_id = str(freshdesk_ticket.get("id"))
            
            logger.info(f"Ticket synced to Freshdesk: {freshdesk_id}")
            return freshdesk_id
            
        except Exception as e:
            logger.error(f"Error syncing to Freshdesk: {e}")
            return None
    
    def sync_to_intercom(
        self,
        ticket_data: Dict[str, Any],
        config: IntegrationConfig
    ) -> Optional[str]:
        """Sincroniza ticket a Intercom."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"{config.api_url}/conversations"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": {
                    "type": "user",
                    "email": ticket_data.get("customer_email", "")
                },
                "body": ticket_data.get("description", ""),
                "subject": ticket_data.get("subject", "Support Request")
            }
            
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            conversation = response.json()
            intercom_id = conversation.get("id")
            
            logger.info(f"Ticket synced to Intercom: {intercom_id}")
            return str(intercom_id) if intercom_id else None
            
        except Exception as e:
            logger.error(f"Error syncing to Intercom: {e}")
            return None
    
    def sync_to_salesforce(
        self,
        ticket_data: Dict[str, Any],
        config: IntegrationConfig
    ) -> Optional[str]:
        """Sincroniza ticket a Salesforce Service Cloud."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Primero obtener access token (OAuth2)
            token_url = f"{config.api_url}/services/oauth2/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": config.api_key,
                "client_secret": config.api_secret
            }
            
            token_response = self.session.post(token_url, data=token_data, timeout=10)
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")
            
            if not access_token:
                return None
            
            # Crear caso en Salesforce
            case_url = f"{config.api_url}/services/data/v57.0/sobjects/Case"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "Subject": ticket_data.get("subject", "Support Case"),
                "Description": ticket_data.get("description", ""),
                "Priority": self._map_priority_to_salesforce(ticket_data.get("priority", "Medium")),
                "Status": "New",
                "Origin": "Web"
            }
            
            response = self.session.post(
                case_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            case = response.json()
            salesforce_id = case.get("id")
            
            logger.info(f"Ticket synced to Salesforce: {salesforce_id}")
            return salesforce_id
            
        except Exception as e:
            logger.error(f"Error syncing to Salesforce: {e}")
            return None
    
    def sync_to_jira(
        self,
        ticket_data: Dict[str, Any],
        config: IntegrationConfig
    ) -> Optional[str]:
        """Sincroniza ticket a Jira Service Management."""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            url = f"{config.api_url}/rest/api/3/issue"
            auth = (config.api_key, config.api_secret or "")
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "fields": {
                    "project": {
                        "key": "SUP"  # Configurar según tu proyecto
                    },
                    "summary": ticket_data.get("subject", "Support Request"),
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{
                                "type": "text",
                                "text": ticket_data.get("description", "")
                            }]
                        }]
                    },
                    "issuetype": {
                        "name": "Task"
                    },
                    "priority": {
                        "name": self._map_priority_to_jira(ticket_data.get("priority", "Medium"))
                    }
                }
            }
            
            response = self.session.post(
                url,
                json=payload,
                auth=auth,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            issue = response.json()
            jira_key = issue.get("key")
            
            logger.info(f"Ticket synced to Jira: {jira_key}")
            return jira_key
            
        except Exception as e:
            logger.error(f"Error syncing to Jira: {e}")
            return None
    
    def sync_ticket(
        self,
        ticket_data: Dict[str, Any],
        systems: Optional[List[str]] = None
    ) -> Dict[str, Optional[str]]:
        """
        Sincroniza ticket a todos los sistemas configurados.
        
        Args:
            ticket_data: Datos del ticket
            systems: Lista de sistemas a sincronizar (None = todos)
            
        Returns:
            Dict con IDs de tickets en sistemas externos
        """
        results = {}
        systems_to_sync = systems or list(self.integrations.keys())
        
        for system in systems_to_sync:
            if system not in self.integrations:
                continue
            
            config = self.integrations[system]
            
            try:
                if system == "zendesk":
                    results["zendesk"] = self.sync_to_zendesk(ticket_data, config)
                elif system == "freshdesk":
                    results["freshdesk"] = self.sync_to_freshdesk(ticket_data, config)
                elif system == "intercom":
                    results["intercom"] = self.sync_to_intercom(ticket_data, config)
                elif system == "salesforce":
                    results["salesforce"] = self.sync_to_salesforce(ticket_data, config)
                elif system == "jira":
                    results["jira"] = self.sync_to_jira(ticket_data, config)
            except Exception as e:
                logger.error(f"Error syncing to {system}: {e}")
                results[system] = None
        
        return results
    
    def _map_priority_to_freshdesk(self, priority: str) -> int:
        """Mapea prioridad a valores de Freshdesk."""
        mapping = {
            "critical": 4,  # Urgent
            "urgent": 3,    # High
            "high": 2,      # Medium
            "medium": 1,    # Low
            "low": 1        # Low
        }
        return mapping.get(priority, 1)
    
    def _map_priority_to_salesforce(self, priority: str) -> str:
        """Mapea prioridad a valores de Salesforce."""
        mapping = {
            "critical": "High",
            "urgent": "High",
            "high": "Medium",
            "medium": "Medium",
            "low": "Low"
        }
        return mapping.get(priority, "Medium")
    
    def _map_priority_to_jira(self, priority: str) -> str:
        """Mapea prioridad a valores de Jira."""
        mapping = {
            "critical": "Highest",
            "urgent": "High",
            "high": "High",
            "medium": "Medium",
            "low": "Lowest"
        }
        return mapping.get(priority, "Medium")

