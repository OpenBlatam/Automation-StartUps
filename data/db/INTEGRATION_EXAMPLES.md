# 🔗 Ejemplos de Integración

Ejemplos prácticos de cómo integrar el sistema de ventas con otros sistemas.

## 📧 Integración con Email Service

### Webhook de Email (Simple)

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook/email', methods=['POST'])
def email_webhook():
    data = request.json
    
    # Validar payload
    required_fields = ['from', 'to', 'subject', 'text']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Enviar email usando servicio (SendGrid, Mailgun, etc.)
    # Ejemplo con requests
    email_service_response = requests.post(
        "https://api.emailservice.com/send",
        json={
            "from": data['from'],
            "to": data['to'],
            "subject": data['subject'],
            "text": data['text'],
            "metadata": data.get('metadata', {})
        },
        headers={"Authorization": f"Bearer {EMAIL_API_KEY}"}
    )
    
    return jsonify({"status": "sent", "id": email_service_response.json().get('id')})
```

### Actualizar Engagement desde Email Service

```python
# Webhook para recibir eventos de email (opens, clicks, replies)
@app.route('/webhook/email-events', methods=['POST'])
def email_events():
    event = request.json
    
    # Trigger DAG de Airflow para actualizar engagement
    airflow_response = requests.post(
        f"{AIRFLOW_URL}/api/v1/dags/lead_nurturing_webhook_handler/dagRuns",
        json={
            "conf": {
                "email": event['email'],
                "event_type": event['type'],  # opened, clicked, replied
                "timestamp": event['timestamp']
            }
        },
        auth=("airflow_user", "airflow_password")
    )
    
    return jsonify({"status": "processed"})
```

## 🔔 Integración con Slack

### Notificaciones de Alertas

```python
import requests
from datetime import datetime

def send_slack_alert(webhook_url: str, message: str, severity: str = "info"):
    """Envía alerta a Slack."""
    
    colors = {
        "critical": "#ff0000",
        "warning": "#ffaa00",
        "info": "#36a64f"
    }
    
    payload = {
        "attachments": [
            {
                "color": colors.get(severity, "#36a64f"),
                "title": "Sales System Alert",
                "text": message,
                "footer": "Sales Automation",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)
```

### Comandos de Slack (Slash Commands)

```python
@app.route('/slack/command', methods=['POST'])
def slack_command():
    command = request.form.get('text', '')
    user = request.form.get('user_name')
    
    if command.startswith('pipeline'):
        # Consultar pipeline
        results = query_pipeline_summary()
        return jsonify({
            "response_type": "in_channel",
            "text": f"Pipeline Summary:\n{format_results(results)}"
        })
    
    elif command.startswith('leads'):
        # Consultar leads
        results = query_leads_attention()
        return jsonify({
            "response_type": "in_channel",
            "text": f"Leads Requiring Attention:\n{format_results(results)}"
        })
    
    return jsonify({"text": "Comando no reconocido"})
```

## 🤖 Integración con CRM

### HubSpot Sync (Python)

```python
import requests
from typing import Dict, Any

class HubSpotSync:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
    
    def sync_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sincroniza lead a HubSpot."""
        
        properties = {
            "email": lead_data['email'],
            "firstname": lead_data.get('first_name'),
            "lastname": lead_data.get('last_name'),
            "phone": lead_data.get('phone'),
            "lifecyclestage": self._map_stage(lead_data.get('stage')),
            "lead_score": str(lead_data.get('score', 0)),
            "lead_source": lead_data.get('source'),
        }
        
        # Crear o actualizar contacto
        response = requests.post(
            f"{self.base_url}/crm/v3/objects/contacts",
            json={"properties": properties},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        return response.json()
    
    def _map_stage(self, stage: str) -> str:
        """Mapea stage interno a HubSpot lifecycle stage."""
        mapping = {
            "qualified": "qualified",
            "contacted": "contacted",
            "meeting_scheduled": "meeting_scheduled",
            "proposal_sent": "proposal_sent",
            "negotiating": "negotiating",
            "closed_won": "customer",
            "closed_lost": "closed_lost"
        }
        return mapping.get(stage, "qualified")
```

## 📊 Integración con Dashboard (Grafana)

### Query para Grafana

```json
{
  "datasource": "PostgreSQL",
  "query": "SELECT DATE_TRUNC('day', qualified_at) AS time, COUNT(*) AS value FROM sales_pipeline WHERE qualified_at >= $__timeFrom() AND qualified_at <= $__timeTo() GROUP BY time ORDER BY time",
  "format": "time_series"
}
```

### Panel de Pipeline Value

```sql
-- Para panel de tiempo
SELECT 
    DATE_TRUNC('hour', qualified_at) AS time,
    SUM(estimated_value * probability_pct / 100.0) AS value
FROM sales_pipeline
WHERE stage NOT IN ('closed_won', 'closed_lost')
AND qualified_at >= $__timeFrom()
AND qualified_at <= $__timeTo()
GROUP BY time
ORDER BY time
```

## 🔄 Integración con ManyChat

### Webhook Handler para ManyChat

```python
@app.route('/webhook/manychat', methods=['POST'])
def manychat_webhook():
    data = request.json
    
    # Extraer datos del lead
    lead = {
        'id': data.get('id'),
        'email': data.get('email'),
        'first_name': data.get('first_name'),
        'phone': data.get('phone'),
        'source': 'manychat',
        'events': data.get('events', [])
    }
    
    # Trigger scoring DAG
    airflow_response = requests.post(
        f"{AIRFLOW_URL}/api/v1/dags/lead_scoring_automation/dagRuns",
        json={"conf": {"lead_data": lead}},
        auth=("user", "password")
    )
    
    return jsonify({"status": "processed"})
```

## 📱 Integración con WhatsApp (Twilio)

```python
from twilio.rest import Client

class WhatsAppIntegration:
    def __init__(self, account_sid: str, auth_token: str):
        self.client = Client(account_sid, auth_token)
    
    def send_followup(self, to: str, message: str):
        """Envía mensaje de seguimiento por WhatsApp."""
        
        message = self.client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio WhatsApp number
            to=f'whatsapp:{to}'
        )
        
        return message.sid
```

## 🎯 Integración con Calendario (Google Calendar)

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class CalendarIntegration:
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def schedule_meeting(self, lead_email: str, lead_name: str, datetime_str: str):
        """Programa reunión en calendario."""
        
        event = {
            'summary': f'Reunión con {lead_name}',
            'description': f'Reunión de ventas con {lead_name} ({lead_email})',
            'start': {
                'dateTime': datetime_str,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': (datetime.fromisoformat(datetime_str) + timedelta(hours=1)).isoformat(),
                'timeZone': 'America/New_York',
            },
            'attendees': [
                {'email': lead_email}
            ],
        }
        
        event = self.service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return event.get('id')
```

## 📊 Integración con Analytics (Google Analytics)

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

def track_lead_conversion(lead_id: str, conversion_value: float):
    """Track conversión en Google Analytics."""
    
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{GA_PROPERTY_ID}",
        events=[
            {
                "name": "lead_converted",
                "params": {
                    "lead_id": lead_id,
                    "value": conversion_value
                }
            }
        ]
    )
    
    response = client.run_report(request)
    return response
```

## 🔐 Integración con Secrets Manager (AWS)

```python
import boto3
import json

def get_secrets(secret_name: str) -> dict:
    """Obtiene secrets desde AWS Secrets Manager."""
    
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    
    return secret

# Uso
secrets = get_secrets('sales-automation-secrets')
db_password = secrets['database_password']
crm_api_key = secrets['crm_api_key']
```

## 📝 Ejemplo Completo de Integración

```python
"""
Ejemplo completo de integración end-to-end
"""

import requests
from typing import Dict, Any

class SalesSystemIntegration:
    def __init__(self, config: Dict[str, Any]):
        self.airflow_url = config['airflow_url']
        self.slack_webhook = config['slack_webhook']
        self.email_service = config['email_service']
    
    def process_new_lead(self, lead_data: Dict[str, Any]):
        """Procesa nuevo lead end-to-end."""
        
        # 1. Trigger scoring
        self._trigger_scoring(lead_data)
        
        # 2. Si califica, asignar y crear tareas
        if lead_data.get('score', 0) >= 50:
            self._assign_to_sales_rep(lead_data)
            self._create_followup_tasks(lead_data)
            
            # 3. Notificar en Slack
            self._notify_slack(f"🎯 Nuevo lead calificado: {lead_data['email']}")
        
        # 4. Sincronizar con CRM
        if lead_data.get('score', 0) >= 50:
            self._sync_to_crm(lead_data)
    
    def _trigger_scoring(self, lead_data: Dict[str, Any]):
        """Trigger DAG de scoring."""
        requests.post(
            f"{self.airflow_url}/api/v1/dags/lead_scoring_automation/dagRuns",
            json={"conf": {"lead_data": lead_data}},
            auth=("user", "password")
        )
    
    def _notify_slack(self, message: str):
        """Envía notificación a Slack."""
        requests.post(
            self.slack_webhook,
            json={"text": message}
        )
```

## 📚 Referencias

- [Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)
- [HubSpot API](https://developers.hubspot.com/docs/api/overview)
- [Salesforce API](https://developer.salesforce.com/docs/apis)


