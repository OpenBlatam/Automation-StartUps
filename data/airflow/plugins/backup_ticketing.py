"""
Integración con Sistemas de Ticketing.

Proporciona integración con:
- Jira
- ServiceNow
- GitHub Issues
- Custom webhooks
"""
import logging
import os
import json
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TicketPriority(Enum):
    """Prioridades de tickets."""
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"


@dataclass
class Ticket:
    """Ticket en sistema de ticketing."""
    title: str
    description: str
    priority: TicketPriority
    labels: Optional[List[str]] = None
    assignee: Optional[str] = None


class JiraIntegration:
    """Integración con Jira."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None
    ):
        """
        Inicializa integración con Jira.
        
        Args:
            url: URL de Jira (ej: https://company.atlassian.net)
            email: Email de usuario
            api_token: API token de Jira
        """
        self.url = url or os.getenv("JIRA_URL")
        self.email = email or os.getenv("JIRA_EMAIL")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "BACKUP")
    
    def create_ticket(self, ticket: Ticket) -> Optional[str]:
        """
        Crea ticket en Jira.
        
        Args:
            ticket: Ticket a crear
        
        Returns:
            Key del ticket creado (ej: BACKUP-123)
        """
        if not all([self.url, self.email, self.api_token]):
            logger.warning("Jira credentials not configured")
            return None
        
        try:
            # Mapear prioridad
            priority_map = {
                TicketPriority.LOWEST: "Lowest",
                TicketPriority.LOW: "Low",
                TicketPriority.MEDIUM: "Medium",
                TicketPriority.HIGH: "High",
                TicketPriority.HIGHEST: "Highest"
            }
            
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": ticket.title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": ticket.description}]
                            }
                        ]
                    },
                    "issuetype": {"name": "Task"},
                    "priority": {"name": priority_map.get(ticket.priority, "Medium")}
                }
            }
            
            if ticket.labels:
                payload["fields"]["labels"] = ticket.labels
            
            if ticket.assignee:
                payload["fields"]["assignee"] = {"accountId": ticket.assignee}
            
            response = requests.post(
                f"{self.url}/rest/api/3/issue",
                json=payload,
                auth=(self.email, self.api_token),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            ticket_key = response.json()["key"]
            logger.info(f"Jira ticket created: {ticket_key}")
            return ticket_key
            
        except Exception as e:
            logger.error(f"Failed to create Jira ticket: {e}")
            return None


class ServiceNowIntegration:
    """Integración con ServiceNow."""
    
    def __init__(
        self,
        instance_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Inicializa integración con ServiceNow.
        
        Args:
            instance_url: URL de instancia ServiceNow
            username: Usuario
            password: Contraseña
        """
        self.instance_url = instance_url or os.getenv("SERVICENOW_INSTANCE_URL")
        self.username = username or os.getenv("SERVICENOW_USERNAME")
        self.password = password or os.getenv("SERVICENOW_PASSWORD")
    
    def create_incident(self, ticket: Ticket) -> Optional[str]:
        """
        Crea incidente en ServiceNow.
        
        Args:
            ticket: Ticket a crear
        
        Returns:
            Número de incidente
        """
        if not all([self.instance_url, self.username, self.password]):
            logger.warning("ServiceNow credentials not configured")
            return None
        
        try:
            # Mapear prioridad
            priority_map = {
                TicketPriority.LOWEST: "5",
                TicketPriority.LOW: "4",
                TicketPriority.MEDIUM: "3",
                TicketPriority.HIGH: "2",
                TicketPriority.HIGHEST: "1"
            }
            
            payload = {
                "short_description": ticket.title,
                "description": ticket.description,
                "priority": priority_map.get(ticket.priority, "3"),
                "category": "Backup",
                "subcategory": "System Backup"
            }
            
            response = requests.post(
                f"{self.instance_url}/api/now/table/incident",
                json=payload,
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            incident_number = response.json()["result"]["number"]
            logger.info(f"ServiceNow incident created: {incident_number}")
            return incident_number
            
        except Exception as e:
            logger.error(f"Failed to create ServiceNow incident: {e}")
            return None


class GitHubIssuesIntegration:
    """Integración con GitHub Issues."""
    
    def __init__(
        self,
        repo: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Inicializa integración con GitHub.
        
        Args:
            repo: Repositorio (owner/repo)
            token: GitHub personal access token
        """
        self.repo = repo or os.getenv("GITHUB_REPO")
        self.token = token or os.getenv("GITHUB_TOKEN")
    
    def create_issue(self, ticket: Ticket) -> Optional[int]:
        """
        Crea issue en GitHub.
        
        Args:
            ticket: Ticket a crear
        
        Returns:
            Número de issue
        """
        if not all([self.repo, self.token]):
            logger.warning("GitHub credentials not configured")
            return None
        
        try:
            # Mapear prioridad a labels
            label_map = {
                TicketPriority.LOWEST: "priority:lowest",
                TicketPriority.LOW: "priority:low",
                TicketPriority.MEDIUM: "priority:medium",
                TicketPriority.HIGH: "priority:high",
                TicketPriority.HIGHEST: "priority:critical"
            }
            
            labels = ["backup"] + [label_map.get(ticket.priority, "priority:medium")]
            if ticket.labels:
                labels.extend(ticket.labels)
            
            payload = {
                "title": ticket.title,
                "body": ticket.description,
                "labels": labels
            }
            
            if ticket.assignee:
                payload["assignees"] = [ticket.assignee]
            
            response = requests.post(
                f"https://api.github.com/repos/{self.repo}/issues",
                json=payload,
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )
            response.raise_for_status()
            
            issue_number = response.json()["number"]
            logger.info(f"GitHub issue created: #{issue_number}")
            return issue_number
            
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {e}")
            return None


class TicketingManager:
    """Gestor de tickets multi-plataforma."""
    
    def __init__(self):
        """Inicializa gestor de tickets."""
        self.integrations = {}
        
        # Jira
        if os.getenv("JIRA_URL"):
            self.integrations['jira'] = JiraIntegration()
        
        # ServiceNow
        if os.getenv("SERVICENOW_INSTANCE_URL"):
            self.integrations['servicenow'] = ServiceNowIntegration()
        
        # GitHub
        if os.getenv("GITHUB_REPO"):
            self.integrations['github'] = GitHubIssuesIntegration()
    
    def create_backup_failure_ticket(
        self,
        backup_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Optional[str]]:
        """
        Crea ticket por fallo de backup.
        
        Args:
            backup_id: ID del backup que falló
            error: Error que ocurrió
            details: Detalles adicionales
            platforms: Plataformas donde crear ticket (None = todas)
        """
        ticket = Ticket(
            title=f"Backup Failure: {backup_id}",
            description=f"""
Backup {backup_id} failed with error: {error}

Details:
{json.dumps(details or {}, indent=2)}

Action Required: Investigate and fix backup issue.
            """.strip(),
            priority=TicketPriority.HIGH,
            labels=["backup", "failure", "urgent"]
        )
        
        results = {}
        platforms_to_use = platforms or list(self.integrations.keys())
        
        for platform in platforms_to_use:
            if platform not in self.integrations:
                continue
            
            try:
                if platform == 'jira':
                    ticket_key = self.integrations[platform].create_ticket(ticket)
                    results[platform] = ticket_key
                elif platform == 'servicenow':
                    incident_number = self.integrations[platform].create_incident(ticket)
                    results[platform] = incident_number
                elif platform == 'github':
                    issue_number = self.integrations[platform].create_issue(ticket)
                    results[platform] = f"#{issue_number}" if issue_number else None
            except Exception as e:
                logger.error(f"Failed to create ticket in {platform}: {e}")
                results[platform] = None
        
        return results

