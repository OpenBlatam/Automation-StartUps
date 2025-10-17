# 🔗 Guía de Integración Avanzada - ClickUp Brain

## Visión General

Esta guía proporciona estrategias avanzadas para integrar ClickUp Brain con ecosistemas empresariales existentes, incluyendo sistemas CRM, ERP, herramientas de colaboración y plataformas de análisis de datos.

## 🏗️ Arquitectura de Integración

### Patrón de Integración Microservicios

```yaml
# integration-architecture.yml
integration_patterns:
  api_gateway:
    description: "Punto de entrada único para todas las integraciones"
    components:
      - "Rate limiting"
      - "Authentication & Authorization"
      - "Request/Response transformation"
      - "Circuit breaker"
      - "Load balancing"
  
  event_driven:
    description: "Integración basada en eventos asíncronos"
    components:
      - "Message queues (RabbitMQ, Apache Kafka)"
      - "Event sourcing"
      - "CQRS pattern"
      - "Saga pattern"
  
  data_synchronization:
    description: "Sincronización bidireccional de datos"
    components:
      - "Change data capture (CDC)"
      - "ETL/ELT pipelines"
      - "Data validation"
      - "Conflict resolution"
  
  real_time_streaming:
    description: "Procesamiento de datos en tiempo real"
    components:
      - "Apache Kafka streams"
      - "Apache Flink"
      - "WebSocket connections"
      - "Server-sent events"
```

## 🔌 Integraciones Empresariales

### Integración con Salesforce

```python
# salesforce_integration.py
import requests
from salesforce_bulk import SalesforceBulk
from salesforce_bulk.util import IteratorBytesIO
import pandas as pd
from typing import List, Dict, Any

class SalesforceIntegration:
    """Integración avanzada con Salesforce."""
    
    def __init__(self, username: str, password: str, security_token: str):
        self.bulk = SalesforceBulk(username, password, security_token)
        self.session = requests.Session()
        self.base_url = "https://your-instance.salesforce.com"
    
    def sync_opportunities_to_salesforce(self, opportunities: List[Dict[str, Any]]):
        """Sincronizar oportunidades estratégicas con Salesforce."""
        
        # Transformar datos de ClickUp Brain a formato Salesforce
        sf_opportunities = []
        for opp in opportunities:
            sf_opp = {
                'Name': opp['title'],
                'Amount': opp.get('estimated_value', 0),
                'StageName': self.map_stage_to_salesforce(opp['status']),
                'CloseDate': opp['expected_close_date'],
                'Probability': opp['success_probability'],
                'Description': opp['description'],
                'Market_Segment__c': opp['market_segment'],
                'Strategic_Priority__c': opp['priority'],
                'ClickUp_Brain_ID__c': opp['id']  # Campo personalizado
            }
            sf_opportunities.append(sf_opp)
        
        # Bulk insert usando Salesforce Bulk API
        job = self.bulk.create_insert_job('Opportunity', contentType='JSON')
        batch = self.bulk.post_batch(job, sf_opportunities)
        self.bulk.wait_for_batch(job, batch)
        
        return self.bulk.get_batch_results(job, batch)
    
    def map_stage_to_salesforce(self, clickup_stage: str) -> str:
        """Mapear etapas de ClickUp Brain a Salesforce."""
        
        stage_mapping = {
            'discovery': 'Prospecting',
            'qualification': 'Qualification',
            'proposal': 'Proposal/Price Quote',
            'negotiation': 'Negotiation/Review',
            'closed_won': 'Closed Won',
            'closed_lost': 'Closed Lost'
        }
        
        return stage_mapping.get(clickup_stage, 'Prospecting')
    
    def sync_contacts_from_salesforce(self):
        """Sincronizar contactos desde Salesforce."""
        
        # Query Salesforce para contactos
        query = """
        SELECT Id, FirstName, LastName, Email, Phone, Title, 
               Account.Name, Account.Industry
        FROM Contact 
        WHERE LastModifiedDate = TODAY
        """
        
        results = self.bulk.query(query)
        
        # Transformar a formato ClickUp Brain
        contacts = []
        for record in results:
            contact = {
                'external_id': record['Id'],
                'first_name': record['FirstName'],
                'last_name': record['LastName'],
                'email': record['Email'],
                'phone': record['Phone'],
                'title': record['Title'],
                'company': record['Account']['Name'],
                'industry': record['Account']['Industry'],
                'source': 'salesforce'
            }
            contacts.append(contact)
        
        return contacts
    
    def create_salesforce_dashboard(self, opportunities_data: List[Dict]):
        """Crear dashboard en Salesforce con datos de ClickUp Brain."""
        
        # Generar métricas
        metrics = self.calculate_opportunity_metrics(opportunities_data)
        
        # Crear reporte en Salesforce
        report_data = {
            'name': 'ClickUp Brain Strategic Opportunities',
            'type': 'Opportunity',
            'format': 'Summary',
            'filters': [
                {
                    'field': 'ClickUp_Brain_ID__c',
                    'operator': 'notEqual',
                    'value': None
                }
            ],
            'groupings': [
                {'field': 'Market_Segment__c'},
                {'field': 'StageName'}
            ],
            'metrics': [
                {'field': 'Amount', 'function': 'sum'},
                {'field': 'Amount', 'function': 'avg'},
                {'field': 'Id', 'function': 'count'}
            ]
        }
        
        return self.create_salesforce_report(report_data)
    
    def implement_bi_directional_sync(self):
        """Implementar sincronización bidireccional."""
        
        # Webhook para cambios en Salesforce
        webhook_config = {
            'url': 'https://clickup-brain.ai/webhooks/salesforce',
            'events': [
                'Opportunity.created',
                'Opportunity.updated',
                'Opportunity.deleted'
            ],
            'authentication': {
                'type': 'oauth2',
                'client_id': 'your_client_id',
                'client_secret': 'your_client_secret'
            }
        }
        
        return self.setup_salesforce_webhook(webhook_config)
```

### Integración con Microsoft Dynamics 365

```python
# dynamics365_integration.py
import requests
from msal import ConfidentialClientApplication
import json
from typing import List, Dict, Any

class Dynamics365Integration:
    """Integración con Microsoft Dynamics 365."""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://your-org.crm.dynamics.com/api/data/v9.1"
        self.access_token = self.get_access_token()
    
    def get_access_token(self) -> str:
        """Obtener token de acceso para Dynamics 365."""
        
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
        
        result = app.acquire_token_for_client(
            scopes=["https://your-org.crm.dynamics.com/.default"]
        )
        
        return result['access_token']
    
    def sync_opportunities_to_dynamics(self, opportunities: List[Dict[str, Any]]):
        """Sincronizar oportunidades con Dynamics 365."""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0'
        }
        
        synced_opportunities = []
        
        for opp in opportunities:
            # Mapear a entidad de Dynamics 365
            dynamics_opp = {
                'name': opp['title'],
                'estimatedvalue': opp.get('estimated_value', 0),
                'closeprobability': opp['success_probability'],
                'estimatedclosedate': opp['expected_close_date'],
                'description': opp['description'],
                'clickup_brain_id': opp['id']
            }
            
            # Crear oportunidad en Dynamics 365
            response = requests.post(
                f"{self.base_url}/opportunities",
                headers=headers,
                json=dynamics_opp
            )
            
            if response.status_code == 201:
                synced_opp = response.json()
                synced_opportunities.append(synced_opp)
        
        return synced_opportunities
    
    def get_dynamics_contacts(self, filter_criteria: Dict = None):
        """Obtener contactos desde Dynamics 365."""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0'
        }
        
        # Construir query
        query = "$select=contactid,firstname,lastname,emailaddress1,telephone1,jobtitle"
        
        if filter_criteria:
            filter_parts = []
            for key, value in filter_criteria.items():
                filter_parts.append(f"{key} eq '{value}'")
            query += f"&$filter={' and '.join(filter_parts)}"
        
        response = requests.get(
            f"{self.base_url}/contacts?{query}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()['value']
        
        return []
    
    def create_dynamics_workflow(self, workflow_config: Dict):
        """Crear workflow en Dynamics 365 para automatización."""
        
        workflow_data = {
            'name': workflow_config['name'],
            'type': 'workflow',
            'category': 'business_process',
            'primaryentity': 'opportunity',
            'trigger': workflow_config['trigger'],
            'steps': workflow_config['steps']
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.base_url}/workflows",
            headers=headers,
            json=workflow_data
        )
        
        return response.json() if response.status_code == 201 else None
```

### Integración con HubSpot

```python
# hubspot_integration.py
import requests
from hubspot import HubSpot
from typing import List, Dict, Any
import json

class HubSpotIntegration:
    """Integración con HubSpot CRM."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.client = HubSpot(access_token=access_token)
        self.base_url = "https://api.hubapi.com"
    
    def sync_deals_to_hubspot(self, opportunities: List[Dict[str, Any]]):
        """Sincronizar oportunidades como deals en HubSpot."""
        
        synced_deals = []
        
        for opp in opportunities:
            # Mapear a formato HubSpot Deal
            deal_data = {
                'properties': {
                    'dealname': opp['title'],
                    'amount': str(opp.get('estimated_value', 0)),
                    'dealstage': self.map_stage_to_hubspot(opp['status']),
                    'closedate': opp['expected_close_date'],
                    'hubspot_owner_id': self.get_owner_id(opp.get('owner_id')),
                    'clickup_brain_id': opp['id'],
                    'market_segment': opp['market_segment'],
                    'strategic_priority': opp['priority']
                }
            }
            
            # Crear deal en HubSpot
            try:
                deal = self.client.deals.create(deal_data)
                synced_deals.append(deal)
            except Exception as e:
                print(f"Error creando deal: {e}")
        
        return synced_deals
    
    def map_stage_to_hubspot(self, clickup_stage: str) -> str:
        """Mapear etapas a pipeline de HubSpot."""
        
        stage_mapping = {
            'discovery': 'appointmentscheduled',
            'qualification': 'qualifiedtobuy',
            'proposal': 'presentationscheduled',
            'negotiation': 'decisionmakerboughtin',
            'closed_won': 'closedwon',
            'closed_lost': 'closedlost'
        }
        
        return stage_mapping.get(clickup_stage, 'appointmentscheduled')
    
    def sync_contacts_from_hubspot(self, properties: List[str] = None):
        """Sincronizar contactos desde HubSpot."""
        
        if not properties:
            properties = [
                'firstname', 'lastname', 'email', 'phone', 
                'jobtitle', 'company', 'industry'
            ]
        
        # Obtener contactos
        contacts = self.client.contacts.get_all(
            properties=properties,
            limit=100
        )
        
        # Transformar a formato ClickUp Brain
        transformed_contacts = []
        for contact in contacts:
            transformed_contact = {
                'external_id': contact['id'],
                'first_name': contact.get('firstname', ''),
                'last_name': contact.get('lastname', ''),
                'email': contact.get('email', ''),
                'phone': contact.get('phone', ''),
                'title': contact.get('jobtitle', ''),
                'company': contact.get('company', ''),
                'industry': contact.get('industry', ''),
                'source': 'hubspot'
            }
            transformed_contacts.append(transformed_contact)
        
        return transformed_contacts
    
    def create_hubspot_automation(self, automation_config: Dict):
        """Crear automatización en HubSpot."""
        
        automation_data = {
            'name': automation_config['name'],
            'type': 'DRIP_DELAY',
            'enabled': True,
            'contactListId': automation_config['contact_list_id'],
            'enrollmentTriggerSettings': {
                'type': 'FORM_SUBMISSION',
                'formId': automation_config['form_id']
            },
            'steps': automation_config['steps']
        }
        
        response = requests.post(
            f"{self.base_url}/automation/v4/automations",
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            },
            json=automation_data
        )
        
        return response.json() if response.status_code == 201 else None
```

## 🔄 Integración con Herramientas de Colaboración

### Integración con Slack

```python
# slack_integration.py
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
from typing import List, Dict, Any

class SlackIntegration:
    """Integración avanzada con Slack."""
    
    def __init__(self, bot_token: str, app_token: str):
        self.client = WebClient(token=bot_token)
        self.app_token = app_token
    
    def send_opportunity_alert(self, opportunity: Dict[str, Any], channel: str):
        """Enviar alerta de nueva oportunidad a Slack."""
        
        # Crear bloque de mensaje rico
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 Nueva Oportunidad Estratégica: {opportunity['title']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Segmento de Mercado:*\n{opportunity['market_segment']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Valor Estimado:*\n${opportunity.get('estimated_value', 0):,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Probabilidad de Éxito:*\n{opportunity['success_probability']}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Prioridad:*\n{opportunity['priority']}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Descripción:*\n{opportunity['description']}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ver en ClickUp Brain"
                        },
                        "url": f"https://clickup-brain.ai/opportunities/{opportunity['id']}",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Asignar a Equipo"
                        },
                        "action_id": "assign_opportunity",
                        "value": opportunity['id']
                    }
                ]
            }
        ]
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text=f"Nueva oportunidad: {opportunity['title']}"
            )
            return response
        except SlackApiError as e:
            print(f"Error enviando mensaje a Slack: {e}")
            return None
    
    def create_slack_dashboard(self, metrics: Dict[str, Any], channel: str):
        """Crear dashboard de métricas en Slack."""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Dashboard ClickUp Brain - Resumen Diario"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Oportunidades Nuevas:*\n{metrics.get('new_opportunities', 0)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Valor Total Pipeline:*\n${metrics.get('total_pipeline_value', 0):,}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Tasa de Conversión:*\n{metrics.get('conversion_rate', 0)}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Oportunidades Ganadas:*\n{metrics.get('won_opportunities', 0)}"
                    }
                ]
            }
        ]
        
        # Agregar gráfico si hay datos
        if metrics.get('trend_data'):
            blocks.append({
                "type": "image",
                "image_url": self.generate_metrics_chart(metrics['trend_data']),
                "alt_text": "Gráfico de tendencias"
            })
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks
            )
            return response
        except SlackApiError as e:
            print(f"Error creando dashboard en Slack: {e}")
            return None
    
    def setup_slack_workflow(self, workflow_config: Dict):
        """Configurar workflow de Slack para automatización."""
        
        workflow_data = {
            "name": workflow_config['name'],
            "steps": [
                {
                    "type": "webhook",
                    "name": "ClickUp Brain Trigger",
                    "inputs": {
                        "url": workflow_config['webhook_url'],
                        "method": "POST"
                    }
                },
                {
                    "type": "send_message",
                    "name": "Send Alert",
                    "inputs": {
                        "channel": workflow_config['channel'],
                        "message": workflow_config['message_template']
                    }
                }
            ]
        }
        
        try:
            response = self.client.workflows_create(workflow_data)
            return response
        except SlackApiError as e:
            print(f"Error creando workflow en Slack: {e}")
            return None
```

### Integración con Microsoft Teams

```python
# teams_integration.py
import requests
import json
from typing import List, Dict, Any

class TeamsIntegration:
    """Integración con Microsoft Teams."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_adaptive_card(self, opportunity: Dict[str, Any]):
        """Enviar tarjeta adaptativa a Teams."""
        
        adaptive_card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"🎯 Nueva Oportunidad Estratégica",
                                "weight": "Bolder",
                                "size": "Large"
                            },
                            {
                                "type": "TextBlock",
                                "text": opportunity['title'],
                                "weight": "Bolder",
                                "size": "Medium"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Segmento de Mercado",
                                        "value": opportunity['market_segment']
                                    },
                                    {
                                        "title": "Valor Estimado",
                                        "value": f"${opportunity.get('estimated_value', 0):,}"
                                    },
                                    {
                                        "title": "Probabilidad de Éxito",
                                        "value": f"{opportunity['success_probability']}%"
                                    },
                                    {
                                        "title": "Prioridad",
                                        "value": opportunity['priority']
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": opportunity['description'],
                                "wrap": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "Ver en ClickUp Brain",
                                "url": f"https://clickup-brain.ai/opportunities/{opportunity['id']}"
                            },
                            {
                                "type": "Action.Submit",
                                "title": "Asignar a Equipo",
                                "data": {
                                    "action": "assign_opportunity",
                                    "opportunity_id": opportunity['id']
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        response = requests.post(
            self.webhook_url,
            headers={'Content-Type': 'application/json'},
            json=adaptive_card
        )
        
        return response.status_code == 200
    
    def create_teams_tab(self, tab_config: Dict):
        """Crear tab personalizado en Teams."""
        
        tab_data = {
            "displayName": tab_config['name'],
            "teamsAppId": tab_config['app_id'],
            "configuration": {
                "entityId": tab_config['entity_id'],
                "contentUrl": tab_config['content_url'],
                "websiteUrl": tab_config['website_url']
            }
        }
        
        # Implementar creación de tab usando Microsoft Graph API
        return self.create_teams_tab_via_graph(tab_data)
    
    def setup_teams_bot(self, bot_config: Dict):
        """Configurar bot de Teams para ClickUp Brain."""
        
        bot_manifest = {
            "manifestVersion": "1.12",
            "version": "1.0.0",
            "id": bot_config['bot_id'],
            "packageName": "com.clickupbrain.teamsbot",
            "developer": {
                "name": "ClickUp Brain",
                "websiteUrl": "https://clickup-brain.ai",
                "privacyUrl": "https://clickup-brain.ai/privacy",
                "termsOfUseUrl": "https://clickup-brain.ai/terms"
            },
            "icons": {
                "color": "color.png",
                "outline": "outline.png"
            },
            "name": {
                "short": "ClickUp Brain Bot",
                "full": "ClickUp Brain Strategic Intelligence Bot"
            },
            "description": {
                "short": "Bot para ClickUp Brain",
                "full": "Bot de ClickUp Brain para gestión de oportunidades estratégicas"
            },
            "accentColor": "#0078D4",
            "bots": [
                {
                    "botId": bot_config['bot_id'],
                    "scopes": ["personal", "team", "groupchat"],
                    "supportsFiles": False,
                    "isNotificationOnly": False
                }
            ],
            "permissions": ["identity", "messageTeamMembers"],
            "validDomains": ["clickup-brain.ai"]
        }
        
        return bot_manifest
```

## 📊 Integración con Herramientas de Análisis

### Integración con Tableau

```python
# tableau_integration.py
import tableauserverclient as TSC
import pandas as pd
from typing import List, Dict, Any

class TableauIntegration:
    """Integración con Tableau para análisis avanzado."""
    
    def __init__(self, server_url: str, username: str, password: str):
        self.server = TSC.Server(server_url)
        self.auth = TSC.TableauAuth(username, password)
        self.server.auth.sign_in(self.auth)
    
    def publish_opportunities_data(self, opportunities: List[Dict[str, Any]]):
        """Publicar datos de oportunidades en Tableau."""
        
        # Convertir a DataFrame
        df = pd.DataFrame(opportunities)
        
        # Preparar datos para Tableau
        tableau_data = df[[
            'id', 'title', 'market_segment', 'estimated_value',
            'success_probability', 'priority', 'status', 'created_at'
        ]].copy()
        
        # Crear datasource
        datasource = TSC.DatasourceItem(
            name="ClickUp Brain Opportunities",
            project_id="your_project_id"
        )
        
        # Publicar datasource
        datasource = self.server.datasources.publish(
            datasource,
            tableau_data.to_csv(index=False),
            TSC.Server.PublishMode.Overwrite
        )
        
        return datasource
    
    def create_strategic_dashboard(self, dashboard_config: Dict):
        """Crear dashboard estratégico en Tableau."""
        
        workbook = TSC.WorkbookItem(
            name=dashboard_config['name'],
            project_id=dashboard_config['project_id']
        )
        
        # Crear workbook con dashboard
        workbook = self.server.workbooks.publish(
            workbook,
            dashboard_config['workbook_file'],
            TSC.Server.PublishMode.Overwrite
        )
        
        return workbook
    
    def setup_data_refresh(self, datasource_id: str, schedule: str):
        """Configurar actualización automática de datos."""
        
        task = TSC.TaskItem(
            name="ClickUp Brain Data Refresh",
            priority=1,
            schedule_item=TSC.ScheduleItem(
                name="Daily Refresh",
                frequency=TSC.ScheduleItem.Frequency.Daily,
                start_time="06:00:00"
            )
        )
        
        # Crear task de actualización
        task = self.server.tasks.create(task)
        
        # Asociar con datasource
        self.server.tasks.run(task.id)
        
        return task
```

### Integración con Power BI

```python
# powerbi_integration.py
from powerbiclient import Report, models
from powerbiclient.authentication import DeviceCodeLoginAuthentication
import pandas as pd
from typing import List, Dict, Any

class PowerBIIntegration:
    """Integración con Microsoft Power BI."""
    
    def __init__(self, client_id: str, workspace_id: str):
        self.client_id = client_id
        self.workspace_id = workspace_id
        self.auth = DeviceCodeLoginAuthentication(client_id=client_id)
    
    def publish_opportunities_dataset(self, opportunities: List[Dict[str, Any]]):
        """Publicar dataset de oportunidades en Power BI."""
        
        # Convertir a DataFrame
        df = pd.DataFrame(opportunities)
        
        # Crear dataset
        dataset = models.Dataset(
            name="ClickUp Brain Opportunities",
            tables=[
                models.Table(
                    name="Opportunities",
                    columns=[
                        models.Column(name="ID", dataType="String"),
                        models.Column(name="Title", dataType="String"),
                        models.Column(name="MarketSegment", dataType="String"),
                        models.Column(name="EstimatedValue", dataType="Decimal"),
                        models.Column(name="SuccessProbability", dataType="Decimal"),
                        models.Column(name="Priority", dataType="String"),
                        models.Column(name="Status", dataType="String"),
                        models.Column(name="CreatedAt", dataType="DateTime")
                    ]
                )
            ]
        )
        
        # Publicar dataset
        dataset = self.client.datasets.post_dataset(dataset)
        
        # Cargar datos
        self.client.datasets.post_rows(
            dataset_id=dataset.id,
            table_name="Opportunities",
            rows=df.to_dict('records')
        )
        
        return dataset
    
    def create_strategic_report(self, report_config: Dict):
        """Crear reporte estratégico en Power BI."""
        
        # Crear reporte
        report = models.Report(
            name=report_config['name'],
            dataset_id=report_config['dataset_id']
        )
        
        report = self.client.reports.post_report(report)
        
        # Configurar visualizaciones
        self.configure_report_visualizations(report.id, report_config['visualizations'])
        
        return report
    
    def configure_report_visualizations(self, report_id: str, visualizations: List[Dict]):
        """Configurar visualizaciones del reporte."""
        
        for viz in visualizations:
            visualization = models.Visualization(
                name=viz['name'],
                type=viz['type'],
                dataset_fields=viz['fields']
            )
            
            self.client.reports.post_visualization(
                report_id=report_id,
                visualization=visualization
            )
    
    def setup_automated_refresh(self, dataset_id: str, schedule: str):
        """Configurar actualización automática."""
        
        refresh_schedule = models.RefreshSchedule(
            enabled=True,
            frequency=schedule,
            times=["06:00:00"]
        )
        
        self.client.datasets.patch_refresh_schedule(
            dataset_id=dataset_id,
            refresh_schedule=refresh_schedule
        )
```

## 🔧 Herramientas de Integración

### API Gateway Personalizado

```python
# api_gateway.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from functools import wraps
import time

app = Flask(__name__)
CORS(app)

class ClickUpBrainAPIGateway:
    """API Gateway personalizado para ClickUp Brain."""
    
    def __init__(self):
        self.services = {
            'salesforce': 'https://api.salesforce.com',
            'hubspot': 'https://api.hubapi.com',
            'dynamics365': 'https://your-org.crm.dynamics.com/api/data/v9.1',
            'slack': 'https://slack.com/api',
            'teams': 'https://graph.microsoft.com/v1.0'
        }
        self.rate_limits = {}
        self.circuit_breakers = {}
    
    def rate_limit(self, max_requests: int = 100, window: int = 3600):
        """Decorator para rate limiting."""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                client_ip = request.remote_addr
                current_time = time.time()
                
                # Verificar rate limit
                if self.check_rate_limit(client_ip, max_requests, window, current_time):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def check_rate_limit(self, client_ip: str, max_requests: int, window: int, current_time: float) -> bool:
        """Verificar si se excedió el rate limit."""
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Limpiar requests antiguos
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < window
        ]
        
        # Verificar límite
        if len(self.rate_limits[client_ip]) >= max_requests:
            return True
        
        # Agregar request actual
        self.rate_limits[client_ip].append(current_time)
        return False
    
    def circuit_breaker(self, service_name: str, failure_threshold: int = 5, timeout: int = 60):
        """Implementar circuit breaker para servicios externos."""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if service_name not in self.circuit_breakers:
                    self.circuit_breakers[service_name] = {
                        'failures': 0,
                        'last_failure': 0,
                        'state': 'closed'  # closed, open, half-open
                    }
                
                breaker = self.circuit_breakers[service_name]
                current_time = time.time()
                
                # Verificar estado del circuit breaker
                if breaker['state'] == 'open':
                    if current_time - breaker['last_failure'] > timeout:
                        breaker['state'] = 'half-open'
                    else:
                        return jsonify({'error': f'Service {service_name} is temporarily unavailable'}), 503
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Reset circuit breaker en caso de éxito
                    if breaker['state'] == 'half-open':
                        breaker['state'] = 'closed'
                        breaker['failures'] = 0
                    
                    return result
                
                except Exception as e:
                    breaker['failures'] += 1
                    breaker['last_failure'] = current_time
                    
                    if breaker['failures'] >= failure_threshold:
                        breaker['state'] = 'open'
                    
                    raise e
            
            return wrapper
        return decorator
    
    @app.route('/api/v1/integrations/salesforce/opportunities', methods=['POST'])
    @rate_limit(max_requests=50, window=3600)
    @circuit_breaker('salesforce')
    def sync_opportunities_to_salesforce():
        """Endpoint para sincronizar oportunidades con Salesforce."""
        
        data = request.get_json()
        opportunities = data.get('opportunities', [])
        
        # Integrar con Salesforce
        sf_integration = SalesforceIntegration(
            username=data['username'],
            password=data['password'],
            security_token=data['security_token']
        )
        
        result = sf_integration.sync_opportunities_to_salesforce(opportunities)
        
        return jsonify({
            'status': 'success',
            'synced_count': len(result),
            'results': result
        })
    
    @app.route('/api/v1/integrations/hubspot/deals', methods=['POST'])
    @rate_limit(max_requests=100, window=3600)
    @circuit_breaker('hubspot')
    def sync_deals_to_hubspot():
        """Endpoint para sincronizar deals con HubSpot."""
        
        data = request.get_json()
        opportunities = data.get('opportunities', [])
        
        # Integrar con HubSpot
        hubspot_integration = HubSpotIntegration(data['access_token'])
        result = hubspot_integration.sync_deals_to_hubspot(opportunities)
        
        return jsonify({
            'status': 'success',
            'synced_count': len(result),
            'results': result
        })
    
    @app.route('/api/v1/integrations/slack/notify', methods=['POST'])
    @rate_limit(max_requests=200, window=3600)
    def send_slack_notification():
        """Endpoint para enviar notificaciones a Slack."""
        
        data = request.get_json()
        
        # Integrar con Slack
        slack_integration = SlackIntegration(
            bot_token=data['bot_token'],
            app_token=data['app_token']
        )
        
        result = slack_integration.send_opportunity_alert(
            opportunity=data['opportunity'],
            channel=data['channel']
        )
        
        return jsonify({
            'status': 'success' if result else 'error',
            'message': 'Notification sent to Slack'
        })
    
    @app.route('/api/v1/integrations/health', methods=['GET'])
    def integration_health():
        """Endpoint para verificar salud de integraciones."""
        
        health_status = {}
        
        for service_name, service_url in self.services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                health_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                health_status[service_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return jsonify({
            'timestamp': time.time(),
            'services': health_status
        })

if __name__ == '__main__':
    gateway = ClickUpBrainAPIGateway()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Configuración de Webhooks

```python
# webhook_manager.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from typing import Dict, Any, Callable

app = Flask(__name__)

class WebhookManager:
    """Gestor de webhooks para integraciones."""
    
    def __init__(self):
        self.webhooks = {}
        self.verification_tokens = {}
    
    def register_webhook(self, service: str, event: str, handler: Callable, secret: str = None):
        """Registrar webhook para un servicio y evento."""
        
        webhook_key = f"{service}:{event}"
        self.webhooks[webhook_key] = {
            'handler': handler,
            'secret': secret
        }
        
        if secret:
            self.verification_tokens[webhook_key] = secret
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verificar firma del webhook."""
        
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, service: str, event: str, payload: Dict[str, Any], signature: str = None):
        """Procesar webhook recibido."""
        
        webhook_key = f"{service}:{event}"
        
        if webhook_key not in self.webhooks:
            return {'error': 'Webhook not registered'}, 404
        
        webhook_config = self.webhooks[webhook_key]
        
        # Verificar firma si existe
        if webhook_config['secret'] and signature:
            if not self.verify_webhook_signature(
                json.dumps(payload), 
                signature, 
                webhook_config['secret']
            ):
                return {'error': 'Invalid signature'}, 401
        
        # Ejecutar handler
        try:
            result = webhook_config['handler'](payload)
            return {'status': 'success', 'result': result}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/webhooks/<service>/<event>', methods=['POST'])
    def handle_webhook(service: str, event: str):
        """Endpoint para manejar webhooks."""
        
        payload = request.get_json()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        return webhook_manager.process_webhook(service, event, payload, signature)

# Ejemplo de uso
webhook_manager = WebhookManager()

def handle_salesforce_opportunity_created(payload: Dict[str, Any]):
    """Handler para cuando se crea una oportunidad en Salesforce."""
    
    # Extraer datos de la oportunidad
    opportunity_data = {
        'external_id': payload['Id'],
        'title': payload['Name'],
        'estimated_value': payload.get('Amount', 0),
        'status': payload['StageName'],
        'source': 'salesforce'
    }
    
    # Sincronizar con ClickUp Brain
    # sync_opportunity_to_clickup_brain(opportunity_data)
    
    return {'message': 'Opportunity synced successfully'}

def handle_hubspot_deal_updated(payload: Dict[str, Any]):
    """Handler para cuando se actualiza un deal en HubSpot."""
    
    # Procesar actualización del deal
    deal_data = {
        'external_id': payload['objectId'],
        'properties': payload['properties']
    }
    
    # Actualizar en ClickUp Brain
    # update_opportunity_in_clickup_brain(deal_data)
    
    return {'message': 'Deal updated successfully'}

# Registrar webhooks
webhook_manager.register_webhook(
    service='salesforce',
    event='opportunity_created',
    handler=handle_salesforce_opportunity_created,
    secret='your_salesforce_webhook_secret'
)

webhook_manager.register_webhook(
    service='hubspot',
    event='deal_updated',
    handler=handle_hubspot_deal_updated,
    secret='your_hubspot_webhook_secret'
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

---

Esta guía de integración avanzada proporciona un framework completo para integrar ClickUp Brain con ecosistemas empresariales existentes, incluyendo CRMs, herramientas de colaboración, plataformas de análisis y sistemas de automatización.


