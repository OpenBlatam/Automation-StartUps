---
title: "Integracion Herramientas Recomendaciones"
category: "integracion_herramientas_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "integracion_herramientas_recomendaciones.md"
---

# 🔗 **INTEGRACIÓN CON HERRAMIENTAS EXISTENTES - SISTEMA DE RECOMENDACIONES**

## **ÍNDICE**
1. [Integración con CRM](#crm)
2. [Integración con E-commerce](#ecommerce)
3. [Integración con Marketing Automation](#marketing)
4. [Integración con Analytics](#analytics)
5. [Integración con Email Marketing](#email)
6. [Integración con Redes Sociales](#social)
7. [Integración con Chatbots](#chatbot)
8. [Integración con Mobile Apps](#mobile)
9. [Integración con ERP](#erp)
10. [Integración con CDP](#cdp)
11. [Casos de Uso Reales](#casos)
12. [Mejores Prácticas](#mejores)
13. [Troubleshooting](#troubleshooting)

---

## **1. INTEGRACIÓN CON CRM** {#crm}

### **Salesforce**
```python
# Ejemplo de integración con Salesforce
import requests
from salesforce_api import Salesforce

class SalesforceRecommendations:
    def __init__(self, username, password, security_token):
        self.sf = Salesforce(username=username, password=password, security_token=security_token)
    
    def get_customer_data(self, customer_id):
        """Obtener datos del cliente desde Salesforce"""
        query = f"SELECT Id, Name, Email, Industry, AnnualRevenue FROM Account WHERE Id = '{customer_id}'"
        result = self.sf.query(query)
        return result['records'][0] if result['records'] else None
    
    def update_recommendations(self, customer_id, recommendations):
        """Actualizar recomendaciones en Salesforce"""
        data = {
            'Recommendation_Score__c': recommendations['score'],
            'Recommended_Products__c': ','.join(recommendations['products']),
            'Last_Recommendation_Update__c': datetime.now().isoformat()
        }
        self.sf.Account.update(customer_id, data)
```

### **HubSpot**
```python
# Ejemplo de integración con HubSpot
from hubspot import HubSpot

class HubSpotRecommendations:
    def __init__(self, access_token):
        self.client = HubSpot(access_token=access_token)
    
    def sync_recommendations(self, contact_id, recommendations):
        """Sincronizar recomendaciones con HubSpot"""
        properties = {
            'recommendation_score': recommendations['score'],
            'recommended_products': ','.join(recommendations['products']),
            'last_recommendation_update': int(time.time() * 1000)
        }
        self.client.contacts.update(contact_id, properties)
```

---

## **2. INTEGRACIÓN CON E-COMMERCE** {#ecommerce}

### **Shopify**
```python
# Ejemplo de integración con Shopify
import shopify

class ShopifyRecommendations:
    def __init__(self, shop_url, access_token):
        shopify.ShopifyResource.set_site(shop_url)
        shopify.ShopifyResource.headers = {'X-Shopify-Access-Token': access_token}
    
    def get_product_data(self, product_id):
        """Obtener datos del producto desde Shopify"""
        product = shopify.Product.find(product_id)
        return {
            'id': product.id,
            'title': product.title,
            'price': product.variants[0].price,
            'tags': product.tags.split(',') if product.tags else [],
            'category': product.product_type
        }
    
    def update_product_recommendations(self, product_id, recommendations):
        """Actualizar recomendaciones del producto"""
        product = shopify.Product.find(product_id)
        product.tags = product.tags + f", recommended_for_{recommendations['category']}"
        product.save()
```

### **WooCommerce**
```python
# Ejemplo de integración con WooCommerce
import requests

class WooCommerceRecommendations:
    def __init__(self, url, consumer_key, consumer_secret):
        self.url = url
        self.auth = (consumer_key, consumer_secret)
    
    def get_order_data(self, order_id):
        """Obtener datos de la orden desde WooCommerce"""
        response = requests.get(f"{self.url}/wp-json/wc/v3/orders/{order_id}", auth=self.auth)
        return response.json()
    
    def update_product_meta(self, product_id, recommendations):
        """Actualizar metadatos del producto con recomendaciones"""
        data = {
            'meta_data': [
                {
                    'key': 'recommendation_score',
                    'value': recommendations['score']
                },
                {
                    'key': 'recommended_products',
                    'value': ','.join(recommendations['products'])
                }
            ]
        }
        requests.put(f"{self.url}/wp-json/wc/v3/products/{product_id}", json=data, auth=self.auth)
```

---

## **3. INTEGRACIÓN CON MARKETING AUTOMATION** {#marketing}

### **Mailchimp**
```python
# Ejemplo de integración con Mailchimp
from mailchimp3 import MailChimp

class MailchimpRecommendations:
    def __init__(self, api_key, username):
        self.client = MailChimp(api_key=api_key, username=username)
    
    def create_recommendation_campaign(self, list_id, recommendations):
        """Crear campaña de email con recomendaciones"""
        campaign_data = {
            'type': 'regular',
            'recipients': {
                'list_id': list_id
            },
            'settings': {
                'subject_line': f"Recomendaciones personalizadas para ti",
                'from_name': "Tu Equipo de Ventas",
                'reply_to': "ventas@tuempresa.com"
            }
        }
        
        campaign = self.client.campaigns.create(campaign_data)
        
        # Agregar contenido con recomendaciones
        content = {
            'html': self.generate_recommendation_html(recommendations)
        }
        self.client.campaigns.content.update(campaign['id'], content)
        
        return campaign
```

### **ActiveCampaign**
```python
# Ejemplo de integración con ActiveCampaign
import requests

class ActiveCampaignRecommendations:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.headers = {'Api-Token': api_key}
    
    def update_contact_tags(self, contact_id, recommendations):
        """Actualizar tags del contacto con recomendaciones"""
        tags = [f"recommended_{product}" for product in recommendations['products']]
        
        for tag in tags:
            tag_data = {'tag': {'tag': tag, 'tagType': 'contact'}}
            requests.post(f"{self.api_url}/api/3/tags", json=tag_data, headers=self.headers)
            
            contact_tag_data = {'contactTag': {'contact': contact_id, 'tag': tag}}
            requests.post(f"{self.api_url}/api/3/contactTags", json=contact_tag_data, headers=self.headers)
```

---

## **4. INTEGRACIÓN CON ANALYTICS** {#analytics}

### **Google Analytics 4**
```python
# Ejemplo de integración con Google Analytics 4
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

class GoogleAnalyticsRecommendations:
    def __init__(self, property_id, credentials_path):
        self.client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        self.property_id = property_id
    
    def track_recommendation_click(self, user_id, recommendation_id, product_id):
        """Rastrear clics en recomendaciones"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[{"name": "customUser:user_id"}],
            metrics=[{"name": "eventCount"}],
            date_ranges=[{"start_date": "2024-01-01", "end_date": "today"}],
            dimension_filter={
                "filter": {
                    "field_name": "customUser:user_id",
                    "string_filter": {"match_type": "EXACT", "value": user_id}
                }
            }
        )
        
        response = self.client.run_report(request)
        return response
```

### **Mixpanel**
```python
# Ejemplo de integración con Mixpanel
from mixpanel import Mixpanel

class MixpanelRecommendations:
    def __init__(self, project_token):
        self.mp = Mixpanel(project_token)
    
    def track_recommendation_event(self, user_id, event_name, properties):
        """Rastrear eventos de recomendaciones"""
        self.mp.track(user_id, event_name, properties)
    
    def get_user_recommendations(self, user_id):
        """Obtener historial de recomendaciones del usuario"""
        events = self.mp.get_events(
            distinct_id=user_id,
            event_names=['recommendation_viewed', 'recommendation_clicked']
        )
        return events
```

---

## **5. INTEGRACIÓN CON EMAIL MARKETING** {#email}

### **SendGrid**
```python
# Ejemplo de integración con SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridRecommendations:
    def __init__(self, api_key):
        self.sg = SendGridAPIClient(api_key)
    
    def send_recommendation_email(self, to_email, recommendations):
        """Enviar email con recomendaciones personalizadas"""
        html_content = self.generate_recommendation_html(recommendations)
        
        message = Mail(
            from_email='ventas@tuempresa.com',
            to_emails=to_email,
            subject='Recomendaciones personalizadas para ti',
            html_content=html_content
        )
        
        response = self.sg.send(message)
        return response
```

### **Constant Contact**
```python
# Ejemplo de integración con Constant Contact
import requests

class ConstantContactRecommendations:
    def __init__(self, api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = "https://api.cc.email/v3"
    
    def create_recommendation_campaign(self, list_id, recommendations):
        """Crear campaña de email con recomendaciones"""
        campaign_data = {
            'name': f"Recomendaciones personalizadas - {datetime.now().strftime('%Y-%m-%d')}",
            'email_campaign_activities': [{
                'format_type': 'HTML',
                'from_name': 'Tu Equipo de Ventas',
                'from_email': 'ventas@tuempresa.com',
                'reply_to_email': 'ventas@tuempresa.com',
                'subject': 'Recomendaciones personalizadas para ti',
                'html_content': self.generate_recommendation_html(recommendations)
            }]
        }
        
        response = requests.post(
            f"{self.base_url}/emails",
            json=campaign_data,
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        return response.json()
```

---

## **6. INTEGRACIÓN CON REDES SOCIALES** {#social}

### **Facebook Marketing API**
```python
# Ejemplo de integración con Facebook Marketing API
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

class FacebookRecommendations:
    def __init__(self, app_id, app_secret, access_token):
        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.api = FacebookAdsApi.get_default_api()
    
    def create_lookalike_audience(self, recommendations_data):
        """Crear audiencia lookalike basada en recomendaciones"""
        ad_account = AdAccount('act_123456789')
        
        audience_data = {
            'name': 'Audiencia Recomendaciones',
            'subtype': 'LOOKALIKE',
            'lookalike_spec': {
                'country': 'US',
                'ratio': 0.01,
                'source': recommendations_data['source_audience_id']
            }
        }
        
        audience = ad_account.create_custom_audience(params=audience_data)
        return audience
```

### **LinkedIn Marketing API**
```python
# Ejemplo de integración con LinkedIn Marketing API
import requests

class LinkedInRecommendations:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
    
    def create_recommendation_campaign(self, recommendations):
        """Crear campaña de LinkedIn con recomendaciones"""
        campaign_data = {
            'name': f"Recomendaciones personalizadas - {datetime.now().strftime('%Y-%m-%d')}",
            'campaignGroup': recommendations['campaign_group_id'],
            'creative': {
                'text': f"Descubre productos recomendados especialmente para ti: {', '.join(recommendations['products'])}"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/adCampaigns",
            json=campaign_data,
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        return response.json()
```

---

## **7. INTEGRACIÓN CON CHATBOTS** {#chatbot}

### **Dialogflow**
```python
# Ejemplo de integración con Dialogflow
from google.cloud import dialogflow

class DialogflowRecommendations:
    def __init__(self, project_id, credentials_path):
        self.project_id = project_id
        self.session_client = dialogflow.SessionsClient.from_service_account_file(credentials_path)
    
    def get_recommendations_intent(self, user_input, session_id):
        """Obtener intención de recomendaciones del usuario"""
        session = self.session_client.session_path(self.project_id, session_id)
        
        text_input = dialogflow.types.TextInput(text=user_input, language_code='es')
        query_input = dialogflow.types.QueryInput(text=text_input)
        
        response = self.session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        
        return response.query_result
    
    def handle_recommendation_request(self, user_input, session_id, recommendations):
        """Manejar solicitud de recomendaciones del usuario"""
        intent = self.get_recommendations_intent(user_input, session_id)
        
        if intent.intent.display_name == 'get_recommendations':
            return f"Basándome en tus preferencias, te recomiendo: {', '.join(recommendations['products'])}"
        else:
            return "¿Te gustaría que te recomiende algunos productos?"
```

### **Microsoft Bot Framework**
```python
# Ejemplo de integración con Microsoft Bot Framework
from botbuilder.core import TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount

class BotFrameworkRecommendations:
    def __init__(self, recommendations_service):
        self.recommendations_service = recommendations_service
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Manejar mensajes del usuario"""
        user_input = turn_context.activity.text
        user_id = turn_context.activity.from_property.id
        
        # Obtener recomendaciones
        recommendations = self.recommendations_service.get_recommendations(user_id)
        
        # Generar respuesta
        if "recomendación" in user_input.lower():
            response = f"Te recomiendo estos productos: {', '.join(recommendations['products'])}"
        else:
            response = "Hola! ¿Te gustaría que te recomiende algunos productos?"
        
        await turn_context.send_activity(MessageFactory.text(response))
```

---

## **8. INTEGRACIÓN CON MOBILE APPS** {#mobile}

### **Firebase**
```python
# Ejemplo de integración con Firebase
import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseRecommendations:
    def __init__(self, credentials_path):
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
    
    def get_user_recommendations(self, user_id):
        """Obtener recomendaciones del usuario desde Firebase"""
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('recommendations', {})
        return {}
    
    def update_user_recommendations(self, user_id, recommendations):
        """Actualizar recomendaciones del usuario en Firebase"""
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.update({
            'recommendations': recommendations,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
```

### **AWS Mobile**
```python
# Ejemplo de integración con AWS Mobile
import boto3

class AWSMobileRecommendations:
    def __init__(self, region_name):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table('user_recommendations')
    
    def get_recommendations(self, user_id):
        """Obtener recomendaciones del usuario desde DynamoDB"""
        response = self.table.get_item(Key={'user_id': user_id})
        return response.get('Item', {}).get('recommendations', {})
    
    def update_recommendations(self, user_id, recommendations):
        """Actualizar recomendaciones del usuario en DynamoDB"""
        self.table.put_item(Item={
            'user_id': user_id,
            'recommendations': recommendations,
            'last_updated': int(time.time())
        })
```

---

## **9. INTEGRACIÓN CON ERP** {#erp}

### **SAP**
```python
# Ejemplo de integración con SAP
import requests

class SAPRecommendations:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = (username, password)
    
    def get_customer_master_data(self, customer_id):
        """Obtener datos maestros del cliente desde SAP"""
        response = requests.get(
            f"{self.base_url}/sap/opu/odata/sap/ZCUSTOMER_SRV/CustomerSet('{customer_id}')",
            auth=self.auth
        )
        return response.json()
    
    def update_recommendations(self, customer_id, recommendations):
        """Actualizar recomendaciones en SAP"""
        data = {
            'RecommendationScore': recommendations['score'],
            'RecommendedProducts': ','.join(recommendations['products']),
            'LastUpdate': datetime.now().isoformat()
        }
        
        response = requests.patch(
            f"{self.base_url}/sap/opu/odata/sap/ZCUSTOMER_SRV/CustomerSet('{customer_id}')",
            json=data,
            auth=self.auth
        )
        return response
```

### **Oracle ERP**
```python
# Ejemplo de integración con Oracle ERP
import cx_Oracle

class OracleERPRecommendations:
    def __init__(self, connection_string):
        self.connection = cx_Oracle.connect(connection_string)
    
    def get_customer_data(self, customer_id):
        """Obtener datos del cliente desde Oracle ERP"""
        cursor = self.connection.cursor()
        query = "SELECT * FROM customers WHERE customer_id = :customer_id"
        cursor.execute(query, customer_id=customer_id)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def update_recommendations(self, customer_id, recommendations):
        """Actualizar recomendaciones en Oracle ERP"""
        cursor = self.connection.cursor()
        query = """
        UPDATE customers 
        SET recommendation_score = :score, 
            recommended_products = :products,
            last_recommendation_update = :update_time
        WHERE customer_id = :customer_id
        """
        cursor.execute(query, 
                      score=recommendations['score'],
                      products=','.join(recommendations['products']),
                      update_time=datetime.now(),
                      customer_id=customer_id)
        self.connection.commit()
        cursor.close()
```

---

## **10. INTEGRACIÓN CON CDP** {#cdp}

### **Segment**
```python
# Ejemplo de integración con Segment
from segment import Client

class SegmentRecommendations:
    def __init__(self, write_key):
        self.client = Client(write_key)
    
    def track_recommendation_event(self, user_id, event_name, properties):
        """Rastrear eventos de recomendaciones en Segment"""
        self.client.track(
            user_id=user_id,
            event=event_name,
            properties=properties
        )
    
    def identify_user(self, user_id, traits):
        """Identificar usuario con características de recomendaciones"""
        self.client.identify(
            user_id=user_id,
            traits=traits
        )
```

### **Adobe Experience Platform**
```python
# Ejemplo de integración con Adobe Experience Platform
import requests

class AdobeExperienceRecommendations:
    def __init__(self, api_key, access_token):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = "https://platform.adobe.io"
    
    def send_recommendation_data(self, user_id, recommendations):
        """Enviar datos de recomendaciones a Adobe Experience Platform"""
        data = {
            'xdm': {
                'identityMap': {
                    'ECID': [{'id': user_id}]
                },
                'recommendations': {
                    'score': recommendations['score'],
                    'products': recommendations['products'],
                    'timestamp': datetime.now().isoformat()
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/data/foundation/ingest/streams",
            json=data,
            headers={
                'Authorization': f'Bearer {self.access_token}',
                'x-api-key': self.api_key
            }
        )
        return response
```

---

## **11. CASOS DE USO REALES** {#casos}

### **Caso 1: E-commerce con Shopify + Mailchimp**
```python
# Flujo completo de integración
class EcommerceRecommendationsFlow:
    def __init__(self):
        self.shopify = ShopifyRecommendations(shop_url, access_token)
        self.mailchimp = MailchimpRecommendations(api_key, username)
        self.recommendations = RecommendationEngine()
    
    def process_new_customer(self, customer_id):
        """Procesar nuevo cliente y enviar recomendaciones"""
        # 1. Obtener datos del cliente desde Shopify
        customer_data = self.shopify.get_customer_data(customer_id)
        
        # 2. Generar recomendaciones
        recommendations = self.recommendations.get_recommendations(customer_data)
        
        # 3. Actualizar producto en Shopify
        self.shopify.update_product_recommendations(customer_id, recommendations)
        
        # 4. Enviar email con Mailchimp
        campaign = self.mailchimp.create_recommendation_campaign(
            customer_data['list_id'], 
            recommendations
        )
        
        return campaign
```

### **Caso 2: SaaS con Salesforce + Slack**
```python
# Flujo de recomendaciones para SaaS
class SaaSRecommendationsFlow:
    def __init__(self):
        self.salesforce = SalesforceRecommendations(username, password, token)
        self.slack = SlackRecommendations(bot_token)
        self.recommendations = RecommendationEngine()
    
    def notify_team_recommendations(self, customer_id):
        """Notificar al equipo sobre nuevas recomendaciones"""
        # 1. Obtener datos del cliente
        customer_data = self.salesforce.get_customer_data(customer_id)
        
        # 2. Generar recomendaciones
        recommendations = self.recommendations.get_recommendations(customer_data)
        
        # 3. Actualizar Salesforce
        self.salesforce.update_recommendations(customer_id, recommendations)
        
        # 4. Notificar en Slack
        message = f"🎯 Nuevas recomendaciones para {customer_data['Name']}: {recommendations['products']}"
        self.slack.send_message("#ventas", message)
```

---

## **12. MEJORES PRÁCTICAS** {#mejores}

### **Sincronización de Datos**
- **Frecuencia**: Sincronizar cada 15-30 minutos
- **Validación**: Verificar integridad de datos antes de sincronizar
- **Rollback**: Mantener capacidad de revertir cambios
- **Logging**: Registrar todas las operaciones de sincronización

### **Manejo de Errores**
- **Retry Logic**: Reintentar operaciones fallidas
- **Circuit Breaker**: Evitar cascadas de fallos
- **Alertas**: Notificar errores críticos inmediatamente
- **Fallback**: Proporcionar alternativas cuando fallan integraciones

### **Seguridad**
- **Autenticación**: Usar OAuth 2.0 cuando sea posible
- **Encriptación**: Encriptar datos sensibles en tránsito
- **Rate Limiting**: Implementar límites de velocidad
- **Auditoría**: Registrar accesos y cambios

### **Monitoreo**
- **Health Checks**: Verificar estado de integraciones
- **Métricas**: Rastrear rendimiento y errores
- **Dashboards**: Visualizar estado en tiempo real
- **Alertas**: Notificar problemas automáticamente

---

## **13. TROUBLESHOOTING** {#troubleshooting}

### **Problemas Comunes**

#### **Error de Autenticación**
```python
# Solución para errores de autenticación
def handle_auth_error(integration):
    try:
        # Reintentar con nuevas credenciales
        integration.refresh_token()
        return True
    except Exception as e:
        # Log error y notificar
        logger.error(f"Auth error: {e}")
        send_alert("Authentication failed", str(e))
        return False
```

#### **Timeout de API**
```python
# Solución para timeouts
def handle_timeout(api_call, max_retries=3):
    for attempt in range(max_retries):
        try:
            return api_call()
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Backoff exponencial
            else:
                raise
```

#### **Datos Inconsistentes**
```python
# Solución para datos inconsistentes
def validate_data(data, schema):
    try:
        jsonschema.validate(data, schema)
        return True
    except jsonschema.ValidationError as e:
        logger.warning(f"Data validation failed: {e}")
        return False
```

---

## **🎯 PRÓXIMOS PASOS**

1. **Identificar Herramientas**: Lista las herramientas que ya usas
2. **Priorizar Integraciones**: Comenzar con las más críticas
3. **Implementar Gradualmente**: Una integración a la vez
4. **Monitorear Resultados**: Rastrear métricas de cada integración
5. **Optimizar Continuamente**: Mejorar basándose en datos

---

## **📞 SOPORTE**

- **Documentación**: [Enlaces a documentación de cada herramienta]
- **Comunidad**: [Foros y grupos de usuarios]
- **Soporte Técnico**: [Contacto para problemas técnicos]
- **Consultoría**: [Servicios de implementación personalizada]

---

**¡Con estas integraciones, tu sistema de recomendaciones estará completamente conectado con todas tus herramientas existentes!** 🚀



