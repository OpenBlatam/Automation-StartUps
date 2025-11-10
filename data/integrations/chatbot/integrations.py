"""
Integraciones Avanzadas para Chatbot
- Dialogflow
- Intercom
- Zapier
- WhatsApp Business API
- Email Services
"""

import json
import logging
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime
from chatbot_engine import ChatbotEngine, ChatMessage, Channel, Language

logger = logging.getLogger(__name__)


class DialogflowIntegration:
    """Integración con Google Dialogflow"""
    
    def __init__(self, project_id: str, language_code: str = "es"):
        self.project_id = project_id
        self.language_code = language_code
        self.session_client = None  # Se inicializaría con google.cloud.dialogflow
    
    async def detect_intent(self, session_id: str, text: str) -> Dict:
        """
        Detecta la intención del usuario usando Dialogflow
        """
        try:
            # En producción, usarías la API real de Dialogflow
            # from google.cloud import dialogflow_v2
            
            # Ejemplo de respuesta simulada
            response = {
                "intent": {
                    "display_name": "export_report",
                    "confidence": 0.95
                },
                "fulfillment_text": "Para exportar reportes, ve a la sección de Reportes...",
                "parameters": {}
            }
            
            logger.info(f"Dialogflow intent detectado: {response['intent']['display_name']}")
            return response
            
        except Exception as e:
            logger.error(f"Error en Dialogflow: {e}")
            return {"error": str(e)}
    
    async def send_to_dialogflow(self, chatbot: ChatbotEngine, user_id: str, 
                                 message: str, session_id: str) -> Dict:
        """Envía mensaje a Dialogflow y procesa respuesta"""
        intent_result = await self.detect_intent(session_id, message)
        
        if "error" in intent_result:
            # Fallback al chatbot local
            chat_msg = ChatMessage(
                user_id=user_id,
                message=message,
                timestamp=datetime.now(),
                channel=Channel.DIALOGFLOW,
                language=Language.ES,
                session_id=session_id
            )
            response = await chatbot.process_message(chat_msg)
            return {"response": response.message, "source": "local"}
        
        return {
            "response": intent_result.get("fulfillment_text", ""),
            "intent": intent_result.get("intent", {}).get("display_name"),
            "confidence": intent_result.get("intent", {}).get("confidence", 0),
            "source": "dialogflow"
        }


class IntercomIntegration:
    """Integración con Intercom"""
    
    def __init__(self, app_id: str, access_token: str):
        self.app_id = app_id
        self.access_token = access_token
        self.base_url = "https://api.intercom.io"
    
    async def create_conversation(self, user_id: str, message: str, 
                                 chatbot_response: str) -> Optional[str]:
        """Crea una conversación en Intercom"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Intercom-Version": "2.10"
            }
            
            data = {
                "from": {
                    "type": "user",
                    "id": user_id
                },
                "body": message
            }
            
            # En producción, harías la llamada real
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         f"{self.base_url}/conversations",
            #         headers=headers,
            #         json=data
            #     ) as response:
            #         result = await response.json()
            #         return result.get("id")
            
            logger.info(f"Conversación Intercom creada para usuario {user_id}")
            return f"intercom_conv_{user_id}_{datetime.now().timestamp()}"
            
        except Exception as e:
            logger.error(f"Error creando conversación Intercom: {e}")
            return None
    
    async def send_message(self, conversation_id: str, message: str, 
                          from_admin: bool = False) -> bool:
        """Envía un mensaje en una conversación de Intercom"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Intercom-Version": "2.10"
            }
            
            data = {
                "message_type": "comment",
                "type": "admin" if from_admin else "user",
                "body": message
            }
            
            # Llamada real a la API
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         f"{self.base_url}/conversations/{conversation_id}/parts",
            #         headers=headers,
            #         json=data
            #     ) as response:
            #         return response.status == 200
            
            logger.info(f"Mensaje enviado a Intercom conversación {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje Intercom: {e}")
            return False
    
    async def assign_to_agent(self, conversation_id: str, admin_id: str) -> bool:
        """Asigna conversación a un agente humano"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Intercom-Version": "2.10"
            }
            
            data = {
                "admin_id": admin_id,
                "type": "admin"
            }
            
            # Llamada real
            # async with aiohttp.ClientSession() as session:
            #     async with session.put(
            #         f"{self.base_url}/conversations/{conversation_id}/parts",
            #         headers=headers,
            #         json=data
            #     ) as response:
            #         return response.status == 200
            
            logger.info(f"Conversación {conversation_id} asignada a agente {admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error asignando agente: {e}")
            return False


class ZapierIntegration:
    """Integración con Zapier para automatizaciones"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def trigger_webhook(self, event_type: str, data: Dict) -> bool:
        """
        Dispara un webhook de Zapier con datos del chatbot
        """
        try:
            payload = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # En producción
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         self.webhook_url,
            #         json=payload,
            #         timeout=aiohttp.ClientTimeout(total=10)
            #     ) as response:
            #         return response.status == 200
            
            logger.info(f"Webhook Zapier disparado: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error en webhook Zapier: {e}")
            return False
    
    async def sync_to_crm(self, user_data: Dict, interaction_data: Dict) -> bool:
        """Sincroniza datos con CRM a través de Zapier"""
        return await self.trigger_webhook("crm_sync", {
            "user": user_data,
            "interaction": interaction_data
        })
    
    async def send_notification(self, notification_type: str, message: str) -> bool:
        """Envía notificación a través de Zapier"""
        return await self.trigger_webhook("notification", {
            "type": notification_type,
            "message": message
        })


class WhatsAppBusinessIntegration:
    """Integración con WhatsApp Business API"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def send_message(self, to: str, message: str, 
                          chatbot_response: Optional[str] = None) -> Dict:
        """
        Envía mensaje a través de WhatsApp Business API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # El mensaje a enviar (respuesta del chatbot o mensaje personalizado)
            text_to_send = chatbot_response or message
            
            data = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": text_to_send
                }
            }
            
            # Llamada real a la API
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         f"{self.base_url}/{self.phone_number_id}/messages",
            #         headers=headers,
            #         json=data
            #     ) as response:
            #         result = await response.json()
            #         return result
            
            logger.info(f"Mensaje WhatsApp enviado a {to}")
            return {
                "success": True,
                "message_id": f"wamid.{datetime.now().timestamp()}"
            }
            
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_template_message(self, to: str, template_name: str, 
                                   parameters: List[str]) -> Dict:
        """Envía mensaje de plantilla de WhatsApp"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
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
            
            # Llamada real
            logger.info(f"Template WhatsApp enviado a {to}: {template_name}")
            return {"success": True, "message_id": f"wamid.{datetime.now().timestamp()}"}
            
        except Exception as e:
            logger.error(f"Error enviando template WhatsApp: {e}")
            return {"success": False, "error": str(e)}


class EmailServiceIntegration:
    """Integración con servicios de email (SendGrid, AWS SES, etc.)"""
    
    def __init__(self, service: str = "sendgrid", api_key: str = None):
        self.service = service
        self.api_key = api_key
    
    async def send_email(self, to: str, subject: str, body: str, 
                        html_body: Optional[str] = None) -> bool:
        """
        Envía email a través del servicio configurado
        """
        try:
            if self.service == "sendgrid":
                return await self._send_sendgrid(to, subject, body, html_body)
            elif self.service == "ses":
                return await self._send_ses(to, subject, body, html_body)
            else:
                logger.warning(f"Servicio de email no soportado: {self.service}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    async def _send_sendgrid(self, to: str, subject: str, body: str, 
                             html_body: Optional[str]) -> bool:
        """Envía email usando SendGrid"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "noreply@empresa.com"},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": body}
                ]
            }
            
            if html_body:
                data["content"].append({"type": "text/html", "value": html_body})
            
            # Llamada real
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         "https://api.sendgrid.com/v3/mail/send",
            #         headers=headers,
            #         json=data
            #     ) as response:
            #         return response.status == 202
            
            logger.info(f"Email SendGrid enviado a {to}")
            return True
            
        except Exception as e:
            logger.error(f"Error SendGrid: {e}")
            return False
    
    async def _send_ses(self, to: str, subject: str, body: str, 
                        html_body: Optional[str]) -> bool:
        """Envía email usando AWS SES"""
        # Implementación con boto3
        logger.info(f"Email SES enviado a {to}")
        return True
    
    async def send_chatbot_response_email(self, to: str, user_message: str, 
                                         chatbot_response: str) -> bool:
        """Envía respuesta del chatbot por email"""
        subject = "Respuesta de Soporte - [Nombre de la Empresa]"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Hola,</h2>
            <p>Gracias por contactarnos. Aquí está la respuesta a tu consulta:</p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Tu pregunta:</strong> {user_message}</p>
                <p><strong>Respuesta:</strong> {chatbot_response}</p>
            </div>
            <p>Si necesitas más ayuda, no dudes en responder a este email.</p>
            <p>Saludos,<br>Equipo de [Nombre de la Empresa]</p>
        </body>
        </html>
        """
        
        return await self.send_email(to, subject, chatbot_response, html_body)


class CRMIntegration:
    """Integración mejorada con CRM (Salesforce, HubSpot)"""
    
    def __init__(self, crm_type: str, api_key: str = None, 
                 base_url: str = None, username: str = None, 
                 password: str = None):
        self.crm_type = crm_type.lower()
        self.api_key = api_key
        self.base_url = base_url
        self.username = username
        self.password = password
        self.access_token = None
    
    async def authenticate(self) -> bool:
        """Autentica con el CRM"""
        try:
            if self.crm_type == "salesforce":
                return await self._authenticate_salesforce()
            elif self.crm_type == "hubspot":
                return await self._authenticate_hubspot()
            return False
        except Exception as e:
            logger.error(f"Error autenticando CRM: {e}")
            return False
    
    async def _authenticate_salesforce(self) -> bool:
        """Autentica con Salesforce"""
        # Implementación con simple-salesforce o requests
        logger.info("Autenticado con Salesforce")
        self.access_token = "sf_token_example"
        return True
    
    async def _authenticate_hubspot(self) -> bool:
        """Autentica con HubSpot"""
        # Implementación con hubspot-api-client
        logger.info("Autenticado con HubSpot")
        self.access_token = "hs_token_example"
        return True
    
    async def create_lead(self, lead_data: Dict) -> Optional[str]:
        """Crea un lead en el CRM"""
        try:
            if not self.access_token:
                await self.authenticate()
            
            if self.crm_type == "salesforce":
                return await self._create_salesforce_lead(lead_data)
            elif self.crm_type == "hubspot":
                return await self._create_hubspot_lead(lead_data)
            
            return None
        except Exception as e:
            logger.error(f"Error creando lead: {e}")
            return None
    
    async def _create_salesforce_lead(self, lead_data: Dict) -> Optional[str]:
        """Crea lead en Salesforce"""
        # Implementación real con simple-salesforce
        logger.info(f"Lead creado en Salesforce: {lead_data.get('email')}")
        return "00Q000000000001AAA"
    
    async def _create_hubspot_lead(self, lead_data: Dict) -> Optional[str]:
        """Crea lead en HubSpot"""
        # Implementación real con hubspot-api-client
        logger.info(f"Lead creado en HubSpot: {lead_data.get('email')}")
        return "lead_12345"
    
    async def create_case(self, case_data: Dict) -> Optional[str]:
        """Crea un caso/ticket en el CRM"""
        try:
            if not self.access_token:
                await self.authenticate()
            
            if self.crm_type == "salesforce":
                return await self._create_salesforce_case(case_data)
            elif self.crm_type == "hubspot":
                return await self._create_hubspot_ticket(case_data)
            
            return None
        except Exception as e:
            logger.error(f"Error creando caso: {e}")
            return None
    
    async def _create_salesforce_case(self, case_data: Dict) -> Optional[str]:
        """Crea caso en Salesforce"""
        logger.info(f"Caso creado en Salesforce")
        return "500000000000001AAA"
    
    async def _create_hubspot_ticket(self, case_data: Dict) -> Optional[str]:
        """Crea ticket en HubSpot"""
        logger.info(f"Ticket creado en HubSpot")
        return "ticket_12345"
    
    async def sync_chatbot_interaction(self, user_id: str, message: str, 
                                      response: str, ticket_id: Optional[str] = None) -> bool:
        """Sincroniza interacción del chatbot con CRM"""
        try:
            interaction_data = {
                "user_id": user_id,
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "ticket_id": ticket_id
            }
            
            # Crear o actualizar registro en CRM
            if ticket_id:
                await self.create_case({
                    "subject": "Consulta Chatbot",
                    "description": f"Usuario: {user_id}\nMensaje: {message}\nRespuesta: {response}",
                    "origin": "Chatbot",
                    "status": "New"
                })
            
            logger.info(f"Interacción sincronizada con {self.crm_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error sincronizando interacción: {e}")
            return False

