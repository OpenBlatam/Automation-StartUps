"""
Integraciones Avanzadas para el Chatbot
- Salesforce CRM
- Zapier
- WhatsApp Business API
- Email (SendGrid)
- Intercom
- Dialogflow
Versión: 2.0.0
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SalesforceIntegration:
    """Integración con Salesforce CRM"""
    
    def __init__(self, instance_url: str, client_id: str, client_secret: str, 
                 username: str, password: str):
        self.instance_url = instance_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Salesforce usando OAuth2"""
        try:
            auth_url = f"{self.instance_url}/services/oauth2/token"
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }
            
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            logger.info("Autenticación con Salesforce exitosa")
        except Exception as e:
            logger.error(f"Error autenticando con Salesforce: {e}")
            raise
    
    def create_lead(self, lead_data: Dict) -> str:
        """Crea un lead en Salesforce"""
        try:
            url = f"{self.instance_url}/services/data/v57.0/sobjects/Lead/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=lead_data, headers=headers)
            response.raise_for_status()
            lead_id = response.json()["id"]
            logger.info(f"Lead creado en Salesforce: {lead_id}")
            return lead_id
        except Exception as e:
            logger.error(f"Error creando lead en Salesforce: {e}")
            raise
    
    def create_case(self, case_data: Dict) -> str:
        """Crea un caso (ticket) en Salesforce"""
        try:
            url = f"{self.instance_url}/services/data/v57.0/sobjects/Case/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=case_data, headers=headers)
            response.raise_for_status()
            case_id = response.json()["id"]
            logger.info(f"Caso creado en Salesforce: {case_id}")
            return case_id
        except Exception as e:
            logger.error(f"Error creando caso en Salesforce: {e}")
            raise
    
    def update_contact(self, contact_id: str, update_data: Dict) -> bool:
        """Actualiza un contacto en Salesforce"""
        try:
            url = f"{self.instance_url}/services/data/v57.0/sobjects/Contact/{contact_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.patch(url, json=update_data, headers=headers)
            response.raise_for_status()
            logger.info(f"Contacto actualizado en Salesforce: {contact_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando contacto en Salesforce: {e}")
            return False


class ZapierIntegration:
    """Integración con Zapier mediante webhooks"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def trigger_webhook(self, event_type: str, data: Dict) -> bool:
        """Dispara un webhook de Zapier"""
        try:
            payload = {
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook Zapier disparado: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Error disparando webhook Zapier: {e}")
            return False
    
    def send_chatbot_event(self, event_data: Dict) -> bool:
        """Envía evento del chatbot a Zapier"""
        return self.trigger_webhook("chatbot_interaction", event_data)
    
    def send_ticket_created(self, ticket_data: Dict) -> bool:
        """Notifica creación de ticket a Zapier"""
        return self.trigger_webhook("ticket_created", ticket_data)
    
    def send_satisfaction_feedback(self, feedback_data: Dict) -> bool:
        """Envía feedback de satisfacción a Zapier"""
        return self.trigger_webhook("satisfaction_feedback", feedback_data)


class WhatsAppIntegration:
    """Integración con WhatsApp Business API"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_message(self, to: str, message: str) -> bool:
        """Envía un mensaje por WhatsApp"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Mensaje WhatsApp enviado a {to}")
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje WhatsApp: {e}")
            return False
    
    def send_template(self, to: str, template_name: str, parameters: list) -> bool:
        """Envía un template de WhatsApp"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "es"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": param}
                                for param in parameters
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Template WhatsApp enviado a {to}")
            return True
        except Exception as e:
            logger.error(f"Error enviando template WhatsApp: {e}")
            return False


class EmailIntegration:
    """Integración con SendGrid para envío de emails"""
    
    def __init__(self, api_key: str, from_email: str, from_name: str = "Chatbot"):
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        self.base_url = "https://api.sendgrid.com/v3"
    
    def send_email(self, to: str, subject: str, html_content: str, 
                   text_content: str = None) -> bool:
        """Envía un email"""
        try:
            url = f"{self.base_url}/mail/send"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "personalizations": [{
                    "to": [{"email": to}]
                }],
                "from": {
                    "email": self.from_email,
                    "name": self.from_name
                },
                "subject": subject,
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            if text_content:
                payload["content"].append({
                    "type": "text/plain",
                    "value": text_content
                })
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Email enviado a {to}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def send_ticket_notification(self, to: str, ticket_id: str, 
                                ticket_data: Dict) -> bool:
        """Envía notificación de ticket creado"""
        subject = f"Ticket #{ticket_id} - {ticket_data.get('subject', 'Nueva consulta')}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Tu ticket ha sido creado</h2>
            <p><strong>Número de ticket:</strong> {ticket_id}</p>
            <p><strong>Prioridad:</strong> {ticket_data.get('priority', 'Media')}</p>
            <p><strong>Mensaje:</strong> {ticket_data.get('message', '')}</p>
            <p>Un agente se pondrá en contacto contigo pronto.</p>
            <p>Saludos,<br>Equipo de Soporte</p>
        </body>
        </html>
        """
        
        return self.send_email(to, subject, html_content)


class IntercomIntegration:
    """Integración con Intercom"""
    
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = "https://api.intercom.io"
    
    def create_conversation(self, user_id: str, message: str) -> str:
        """Crea una conversación en Intercom"""
        try:
            url = f"{self.base_url}/conversations"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Intercom-Version": "2.10"
            }
            
            payload = {
                "from": {
                    "type": "user",
                    "id": user_id
                },
                "body": message
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            conversation_id = response.json()["id"]
            logger.info(f"Conversación creada en Intercom: {conversation_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Error creando conversación en Intercom: {e}")
            raise


# Clase principal de integraciones
class IntegrationManager:
    """Gestiona todas las integraciones del chatbot"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.salesforce = None
        self.zapier = None
        self.whatsapp = None
        self.email = None
        self.intercom = None
        
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Inicializa las integraciones según configuración"""
        integrations = self.config.get("integrations", {})
        
        # Salesforce
        if integrations.get("crm", {}).get("enabled", False):
            sf_config = integrations["crm"]
            try:
                self.salesforce = SalesforceIntegration(
                    instance_url=sf_config.get("instance_url", ""),
                    client_id=sf_config.get("client_id", ""),
                    client_secret=sf_config.get("client_secret", ""),
                    username=sf_config.get("username", ""),
                    password=sf_config.get("password", "")
                )
                logger.info("Integración Salesforce inicializada")
            except Exception as e:
                logger.warning(f"No se pudo inicializar Salesforce: {e}")
        
        # Zapier
        if integrations.get("zapier", {}).get("enabled", False):
            zapier_config = integrations["zapier"]
            self.zapier = ZapierIntegration(
                webhook_url=zapier_config.get("webhook_url", "")
            )
            logger.info("Integración Zapier inicializada")
        
        # WhatsApp
        if integrations.get("whatsapp", {}).get("enabled", False):
            wa_config = integrations["whatsapp"]
            self.whatsapp = WhatsAppIntegration(
                phone_number_id=wa_config.get("phone_number_id", ""),
                access_token=wa_config.get("api_key", "")
            )
            logger.info("Integración WhatsApp inicializada")
        
        # Email
        if integrations.get("email", {}).get("enabled", False):
            email_config = integrations["email"]
            self.email = EmailIntegration(
                api_key=email_config.get("api_key", ""),
                from_email=email_config.get("from_email", ""),
                from_name=email_config.get("from_name", "Chatbot")
            )
            logger.info("Integración Email inicializada")
        
        # Intercom
        if integrations.get("intercom", {}).get("enabled", False):
            ic_config = integrations["intercom"]
            self.intercom = IntercomIntegration(
                app_id=ic_config.get("app_id", ""),
                api_key=ic_config.get("api_key", "")
            )
            logger.info("Integración Intercom inicializada")
    
    def sync_ticket_to_crm(self, ticket_id: str, ticket_data: Dict) -> bool:
        """Sincroniza ticket con CRM"""
        if self.salesforce:
            try:
                case_data = {
                    "Subject": ticket_data.get("message", "")[:255],
                    "Description": ticket_data.get("message", ""),
                    "Priority": ticket_data.get("priority", "Medium"),
                    "Status": "New",
                    "Origin": "Chatbot"
                }
                self.salesforce.create_case(case_data)
            return True
        except Exception as e:
                logger.error(f"Error sincronizando ticket con CRM: {e}")
            return False

    def notify_zapier(self, event_type: str, data: Dict) -> bool:
        """Notifica evento a Zapier"""
        if self.zapier:
            return self.zapier.trigger_webhook(event_type, data)
        return False
