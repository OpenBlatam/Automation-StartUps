# Guía de Automatización Avanzada para Facebook Ads
## Scripts, APIs y Automatización Inteligente

---

## 1. Introducción a la Automatización Avanzada

Esta guía proporciona técnicas avanzadas de automatización para Facebook Ads, incluyendo scripts personalizados, integración con APIs, automatización inteligente y sistemas de monitoreo automatizado. Está diseñada para profesionales que buscan maximizar la eficiencia y reducir el trabajo manual.

### Objetivos de la Automatización Avanzada
- Automatizar tareas repetitivas y complejas
- Integrar sistemas y herramientas
- Implementar monitoreo inteligente
- Optimizar performance automáticamente
- Reducir tiempo de gestión en 80-90%

---

## 2. Fundamentos de Automatización

### 2.1 Tipos de Automatización

**Automatización de Tareas:**
```
Definición: Automatizar tareas específicas y repetitivas
Ejemplos: Pausar campañas de bajo rendimiento, ajustar presupuestos
Beneficio: Reducción de trabajo manual
Complejidad: Baja a Media
```

**Automatización de Procesos:**
```
Definición: Automatizar flujos de trabajo completos
Ejemplos: Creación de campañas, optimización de audiencias
Beneficio: Eficiencia operacional
Complejidad: Media a Alta
```

**Automatización Inteligente:**
```
Definición: Automatización basada en IA y ML
Ejemplos: Predicción de performance, optimización automática
Beneficio: Optimización avanzada
Complejidad: Alta
```

### 2.2 Herramientas de Automatización

**Scripts Personalizados:**
```
Lenguajes: Python, JavaScript, PHP
Plataformas: Facebook Marketing API, Google Apps Script
Ventaja: Control total y personalización
Limitación: Requiere conocimientos técnicos
```

**APIs y Integraciones:**
```
APIs: Facebook Marketing API, Google Ads API
Integraciones: Zapier, IFTTT, Microsoft Power Automate
Ventaja: Conectividad entre sistemas
Limitación: Limitaciones de API
```

**Herramientas de Automatización:**
```
Nativas: Facebook Ads Manager, Google Ads Editor
Terceros: AdEspresso, Optmyzr, WordStream
Ventaja: Facilidad de uso
Limitación: Funcionalidades limitadas
```

---

## 3. Scripts Personalizados

### 3.1 Scripts de Python

**Script de Monitoreo Automático:**
```python
import requests
import json
import time
from datetime import datetime, timedelta

class FacebookAdsMonitor:
    def __init__(self, access_token, ad_account_id):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def get_campaigns(self):
        """Obtener todas las campañas activas"""
        url = f"{self.base_url}/act_{self.ad_account_id}/campaigns"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,objective,created_time',
            'effective_status': 'ACTIVE'
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_campaign_metrics(self, campaign_id, date_range=7):
        """Obtener métricas de campaña"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/{campaign_id}/insights"
        params = {
            'access_token': self.access_token,
            'fields': 'impressions,clicks,spend,ctr,cpc,cpm,conversions',
            'time_range': f"{{'since':'{start_date}','until':'{end_date}'}}",
            'level': 'campaign'
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def check_performance_thresholds(self, campaign_id, min_ctr=1.0, max_cpc=2.0):
        """Verificar umbrales de performance"""
        metrics = self.get_campaign_metrics(campaign_id)
        
        if metrics.get('data'):
            data = metrics['data'][0]
            ctr = float(data.get('ctr', 0))
            cpc = float(data.get('cpc', 0))
            
            if ctr < min_ctr or cpc > max_cpc:
                return {
                    'campaign_id': campaign_id,
                    'ctr': ctr,
                    'cpc': cpc,
                    'action_needed': True,
                    'reason': f"CTR: {ctr}% < {min_ctr}% or CPC: ${cpc} > ${max_cpc}"
                }
        
        return {'action_needed': False}
    
    def pause_underperforming_campaigns(self, min_ctr=1.0, max_cpc=2.0):
        """Pausar campañas de bajo rendimiento"""
        campaigns = self.get_campaigns()
        actions_taken = []
        
        for campaign in campaigns.get('data', []):
            campaign_id = campaign['id']
            performance_check = self.check_performance_thresholds(
                campaign_id, min_ctr, max_cpc
            )
            
            if performance_check['action_needed']:
                # Pausar campaña
                url = f"{self.base_url}/{campaign_id}"
                data = {
                    'status': 'PAUSED',
                    'access_token': self.access_token
                }
                response = requests.post(url, data=data)
                
                if response.status_code == 200:
                    actions_taken.append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign['name'],
                        'action': 'PAUSED',
                        'reason': performance_check['reason']
                    })
        
        return actions_taken

# Uso del script
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    # Crear monitor
    monitor = FacebookAdsMonitor(ACCESS_TOKEN, AD_ACCOUNT_ID)
    
    # Ejecutar monitoreo
    actions = monitor.pause_underperforming_campaigns(
        min_ctr=1.5, 
        max_cpc=3.0
    )
    
    # Reportar acciones
    for action in actions:
        print(f"Campaign {action['campaign_name']} paused: {action['reason']}")
```

**Script de Optimización Automática:**
```python
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

class FacebookAdsOptimizer:
    def __init__(self, access_token, ad_account_id):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def get_ad_sets(self, campaign_id):
        """Obtener ad sets de una campaña"""
        url = f"{self.base_url}/{campaign_id}/adsets"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,daily_budget,bid_strategy,optimization_goal'
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_ad_set_metrics(self, ad_set_id, date_range=7):
        """Obtener métricas de ad set"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/{ad_set_id}/insights"
        params = {
            'access_token': self.access_token,
            'fields': 'impressions,clicks,spend,ctr,cpc,cpm,conversions,cost_per_conversion',
            'time_range': f"{{'since':'{start_date}','until':'{end_date}'}}",
            'level': 'adset'
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def optimize_budgets(self, campaign_id, min_roas=3.0):
        """Optimizar presupuestos basándose en ROAS"""
        ad_sets = self.get_ad_sets(campaign_id)
        optimizations = []
        
        for ad_set in ad_sets.get('data', []):
            ad_set_id = ad_set['id']
            metrics = self.get_ad_set_metrics(ad_set_id)
            
            if metrics.get('data'):
                data = metrics['data'][0]
                spend = float(data.get('spend', 0))
                conversions = float(data.get('conversions', 0))
                
                if conversions > 0:
                    # Calcular ROAS (asumiendo valor promedio de conversión)
                    avg_conversion_value = 50  # Ajustar según tu negocio
                    roas = (conversions * avg_conversion_value) / spend if spend > 0 else 0
                    
                    current_budget = float(ad_set.get('daily_budget', 0))
                    
                    if roas > min_roas * 1.5:  # ROAS muy bueno
                        new_budget = current_budget * 1.2  # Aumentar 20%
                        action = "INCREASE"
                    elif roas > min_roas:  # ROAS bueno
                        new_budget = current_budget * 1.1  # Aumentar 10%
                        action = "INCREASE"
                    elif roas < min_roas * 0.7:  # ROAS malo
                        new_budget = current_budget * 0.8  # Reducir 20%
                        action = "DECREASE"
                    else:
                        continue  # No hacer cambios
                    
                    # Aplicar cambio de presupuesto
                    url = f"{self.base_url}/{ad_set_id}"
                    data = {
                        'daily_budget': int(new_budget),
                        'access_token': self.access_token
                    }
                    response = requests.post(url, data=data)
                    
                    if response.status_code == 200:
                        optimizations.append({
                            'ad_set_id': ad_set_id,
                            'ad_set_name': ad_set['name'],
                            'current_budget': current_budget,
                            'new_budget': new_budget,
                            'roas': roas,
                            'action': action
                        })
        
        return optimizations
    
    def optimize_bidding(self, ad_set_id, target_cpa=25.0):
        """Optimizar bidding basándose en CPA objetivo"""
        metrics = self.get_ad_set_metrics(ad_set_id)
        
        if metrics.get('data'):
            data = metrics['data'][0]
            current_cpa = float(data.get('cost_per_conversion', 0))
            
            if current_cpa > target_cpa * 1.2:  # CPA muy alto
                # Cambiar a bid cap más bajo
                new_bid = target_cpa * 0.8
                bid_strategy = "BID_CAP"
            elif current_cpa < target_cpa * 0.8:  # CPA muy bajo
                # Cambiar a bid cap más alto
                new_bid = target_cpa * 1.2
                bid_strategy = "BID_CAP"
            else:
                return None  # No hacer cambios
            
            # Aplicar cambio de bidding
            url = f"{self.base_url}/{ad_set_id}"
            data = {
                'bid_strategy': bid_strategy,
                'bid_amount': int(new_bid * 100),  # Convertir a centavos
                'access_token': self.access_token
            }
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                return {
                    'ad_set_id': ad_set_id,
                    'current_cpa': current_cpa,
                    'new_bid': new_bid,
                    'bid_strategy': bid_strategy
                }
        
        return None

# Uso del script
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    # Crear optimizador
    optimizer = FacebookAdsOptimizer(ACCESS_TOKEN, AD_ACCOUNT_ID)
    
    # Optimizar presupuestos
    budget_optimizations = optimizer.optimize_budgets("campaign_id", min_roas=3.0)
    
    # Reportar optimizaciones
    for opt in budget_optimizations:
        print(f"Ad Set {opt['ad_set_name']}: {opt['action']} budget from ${opt['current_budget']} to ${opt['new_budget']} (ROAS: {opt['roas']:.2f})")
```

### 3.2 Scripts de JavaScript (Google Apps Script)

**Script de Reportes Automáticos:**
```javascript
function generateFacebookAdsReport() {
  // Configuración
  const ACCESS_TOKEN = 'your_access_token';
  const AD_ACCOUNT_ID = 'your_ad_account_id';
  const SPREADSHEET_ID = 'your_spreadsheet_id';
  
  // Obtener datos de Facebook Ads
  const campaigns = getCampaigns(ACCESS_TOKEN, AD_ACCOUNT_ID);
  const insights = getInsights(ACCESS_TOKEN, AD_ACCOUNT_ID);
  
  // Procesar datos
  const reportData = processData(campaigns, insights);
  
  // Escribir a Google Sheets
  writeToSpreadsheet(SPREADSHEET_ID, reportData);
  
  // Enviar email con reporte
  sendEmailReport(reportData);
}

function getCampaigns(accessToken, adAccountId) {
  const url = `https://graph.facebook.com/v18.0/act_${adAccountId}/campaigns`;
  const params = {
    'access_token': accessToken,
    'fields': 'id,name,status,objective,created_time',
    'effective_status': 'ACTIVE'
  };
  
  const response = UrlFetchApp.fetch(url + '?' + Object.keys(params).map(key => key + '=' + params[key]).join('&'));
  return JSON.parse(response.getContentText());
}

function getInsights(accessToken, adAccountId) {
  const url = `https://graph.facebook.com/v18.0/act_${adAccountId}/insights`;
  const params = {
    'access_token': accessToken,
    'fields': 'campaign_id,campaign_name,impressions,clicks,spend,ctr,cpc,cpm,conversions',
    'time_range': '{"since":"' + getDateRange().start + '","until":"' + getDateRange().end + '"}',
    'level': 'campaign'
  };
  
  const response = UrlFetchApp.fetch(url + '?' + Object.keys(params).map(key => key + '=' + params[key]).join('&'));
  return JSON.parse(response.getContentText());
}

function processData(campaigns, insights) {
  const reportData = [];
  
  insights.data.forEach(insight => {
    const campaign = campaigns.data.find(c => c.id === insight.campaign_id);
    
    reportData.push({
      'Campaign ID': insight.campaign_id,
      'Campaign Name': insight.campaign_name,
      'Status': campaign ? campaign.status : 'Unknown',
      'Objective': campaign ? campaign.objective : 'Unknown',
      'Impressions': insight.impressions,
      'Clicks': insight.clicks,
      'Spend': insight.spend,
      'CTR': insight.ctr,
      'CPC': insight.cpc,
      'CPM': insight.cpm,
      'Conversions': insight.conversions,
      'Date': new Date()
    });
  });
  
  return reportData;
}

function writeToSpreadsheet(spreadsheetId, data) {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getActiveSheet();
  
  // Limpiar datos existentes
  sheet.clear();
  
  // Escribir encabezados
  const headers = Object.keys(data[0]);
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // Escribir datos
  const values = data.map(row => headers.map(header => row[header]));
  sheet.getRange(2, 1, values.length, headers.length).setValues(values);
  
  // Formatear
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  sheet.autoResizeColumns(1, headers.length);
}

function sendEmailReport(data) {
  const emailBody = generateEmailBody(data);
  
  MailApp.sendEmail({
    to: 'your-email@example.com',
    subject: 'Facebook Ads Report - ' + new Date().toLocaleDateString(),
    htmlBody: emailBody
  });
}

function generateEmailBody(data) {
  let html = '<h2>Facebook Ads Performance Report</h2>';
  html += '<p>Date: ' + new Date().toLocaleDateString() + '</p>';
  html += '<table border="1" style="border-collapse: collapse;">';
  html += '<tr><th>Campaign</th><th>Spend</th><th>CTR</th><th>CPC</th><th>Conversions</th></tr>';
  
  data.forEach(row => {
    html += `<tr>
      <td>${row['Campaign Name']}</td>
      <td>$${row['Spend']}</td>
      <td>${row['CTR']}%</td>
      <td>$${row['CPC']}</td>
      <td>${row['Conversions']}</td>
    </tr>`;
  });
  
  html += '</table>';
  return html;
}

function getDateRange() {
  const today = new Date();
  const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  return {
    start: lastWeek.toISOString().split('T')[0],
    end: today.toISOString().split('T')[0]
  };
}
```

---

## 4. Integración con APIs

### 4.1 Facebook Marketing API

**Configuración de API:**
```python
import requests
import json
from datetime import datetime, timedelta

class FacebookMarketingAPI:
    def __init__(self, access_token, ad_account_id):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = requests.Session()
        
    def make_request(self, endpoint, method='GET', data=None, params=None):
        """Realizar petición a la API"""
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        if method == 'GET':
            response = self.session.get(url, params=params)
        elif method == 'POST':
            response = self.session.post(url, data=data, params=params)
        elif method == 'PUT':
            response = self.session.put(url, data=data, params=params)
        elif method == 'DELETE':
            response = self.session.delete(url, params=params)
        
        return response.json()
    
    def create_campaign(self, name, objective, status='PAUSED'):
        """Crear nueva campaña"""
        endpoint = f"act_{self.ad_account_id}/campaigns"
        data = {
            'name': name,
            'objective': objective,
            'status': status
        }
        return self.make_request(endpoint, method='POST', data=data)
    
    def create_ad_set(self, campaign_id, name, daily_budget, targeting, optimization_goal):
        """Crear nuevo ad set"""
        endpoint = f"act_{self.ad_account_id}/adsets"
        data = {
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget,
            'targeting': json.dumps(targeting),
            'optimization_goal': optimization_goal,
            'billing_event': 'IMPRESSIONS',
            'status': 'PAUSED'
        }
        return self.make_request(endpoint, method='POST', data=data)
    
    def create_ad(self, ad_set_id, name, creative_id, status='PAUSED'):
        """Crear nuevo anuncio"""
        endpoint = f"act_{self.ad_account_id}/ads"
        data = {
            'name': name,
            'adset_id': ad_set_id,
            'creative': json.dumps({'creative_id': creative_id}),
            'status': status
        }
        return self.make_request(endpoint, method='POST', data=data)
    
    def get_insights(self, object_id, fields, date_range=7, level='campaign'):
        """Obtener insights de un objeto"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
        
        endpoint = f"{object_id}/insights"
        params = {
            'fields': ','.join(fields),
            'time_range': json.dumps({
                'since': start_date,
                'until': end_date
            }),
            'level': level
        }
        return self.make_request(endpoint, params=params)
    
    def update_object(self, object_id, data):
        """Actualizar objeto"""
        return self.make_request(object_id, method='POST', data=data)
    
    def delete_object(self, object_id):
        """Eliminar objeto"""
        return self.make_request(object_id, method='DELETE')

# Uso de la API
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    # Crear cliente API
    api = FacebookMarketingAPI(ACCESS_TOKEN, AD_ACCOUNT_ID)
    
    # Crear campaña
    campaign = api.create_campaign(
        name="Test Campaign",
        objective="CONVERSIONS"
    )
    
    print(f"Campaign created: {campaign}")
```

### 4.2 Integración con Google Analytics

**Script de Integración GA4:**
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import pandas as pd

class GoogleAnalyticsIntegration:
    def __init__(self, property_id, credentials_path):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
        
    def get_facebook_ads_data(self, start_date, end_date):
        """Obtener datos de Facebook Ads desde GA4"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="campaignName"),
                Dimension(name="source"),
                Dimension(name="medium"),
                Dimension(name="date")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="users"),
                Metric(name="conversions"),
                Metric(name="totalRevenue")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter={
                "filter": {
                    "field_name": "source",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "facebook"
                    }
                }
            }
        )
        
        response = self.client.run_report(request)
        
        # Convertir a DataFrame
        data = []
        for row in response.rows:
            data.append({
                'campaign': row.dimension_values[0].value,
                'source': row.dimension_values[1].value,
                'medium': row.dimension_values[2].value,
                'date': row.dimension_values[3].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'conversions': int(row.metric_values[2].value),
                'revenue': float(row.metric_values[3].value)
            })
        
        return pd.DataFrame(data)
    
    def calculate_roas(self, facebook_data, facebook_spend):
        """Calcular ROAS combinando datos de GA4 y Facebook"""
        # Agrupar datos por campaña
        campaign_data = facebook_data.groupby('campaign').agg({
            'revenue': 'sum',
            'conversions': 'sum',
            'sessions': 'sum'
        }).reset_index()
        
        # Combinar con datos de gasto de Facebook
        campaign_data = campaign_data.merge(
            facebook_spend, 
            left_on='campaign', 
            right_on='campaign_name', 
            how='left'
        )
        
        # Calcular ROAS
        campaign_data['roas'] = campaign_data['revenue'] / campaign_data['spend']
        campaign_data['cpa'] = campaign_data['spend'] / campaign_data['conversions']
        
        return campaign_data

# Uso de la integración
if __name__ == "__main__":
    # Configurar credenciales
    PROPERTY_ID = "your_property_id"
    CREDENTIALS_PATH = "path/to/credentials.json"
    
    # Crear integración
    ga_integration = GoogleAnalyticsIntegration(PROPERTY_ID, CREDENTIALS_PATH)
    
    # Obtener datos
    facebook_data = ga_integration.get_facebook_ads_data("2024-01-01", "2024-01-31")
    
    print("Facebook Ads Data from GA4:")
    print(facebook_data.head())
```

---

## 5. Automatización Inteligente

### 5.1 Sistema de Monitoreo Inteligente

**Sistema de Alertas Inteligentes:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime, timedelta

class IntelligentMonitoringSystem:
    def __init__(self, access_token, ad_account_id, email_config):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.email_config = email_config
        self.alert_rules = self.load_alert_rules()
        
    def load_alert_rules(self):
        """Cargar reglas de alertas"""
        return {
            'ctr_threshold': 1.0,
            'cpc_threshold': 3.0,
            'cpa_threshold': 50.0,
            'roas_threshold': 2.0,
            'spend_threshold': 1000.0,
            'conversion_threshold': 10
        }
    
    def check_performance_alerts(self, campaign_id):
        """Verificar alertas de performance"""
        alerts = []
        
        # Obtener métricas de la campaña
        metrics = self.get_campaign_metrics(campaign_id)
        
        if metrics:
            # Verificar CTR
            if metrics.get('ctr', 0) < self.alert_rules['ctr_threshold']:
                alerts.append({
                    'type': 'LOW_CTR',
                    'message': f"CTR muy bajo: {metrics['ctr']}%",
                    'severity': 'HIGH',
                    'campaign_id': campaign_id
                })
            
            # Verificar CPC
            if metrics.get('cpc', 0) > self.alert_rules['cpc_threshold']:
                alerts.append({
                    'type': 'HIGH_CPC',
                    'message': f"CPC muy alto: ${metrics['cpc']}",
                    'severity': 'MEDIUM',
                    'campaign_id': campaign_id
                })
            
            # Verificar CPA
            if metrics.get('cpa', 0) > self.alert_rules['cpa_threshold']:
                alerts.append({
                    'type': 'HIGH_CPA',
                    'message': f"CPA muy alto: ${metrics['cpa']}",
                    'severity': 'HIGH',
                    'campaign_id': campaign_id
                })
            
            # Verificar ROAS
            if metrics.get('roas', 0) < self.alert_rules['roas_threshold']:
                alerts.append({
                    'type': 'LOW_ROAS',
                    'message': f"ROAS muy bajo: {metrics['roas']}:1",
                    'severity': 'HIGH',
                    'campaign_id': campaign_id
                })
        
        return alerts
    
    def send_alert_email(self, alerts):
        """Enviar email de alertas"""
        if not alerts:
            return
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        msg['Subject'] = f"Facebook Ads Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Crear cuerpo del mensaje
        body = "<h2>Facebook Ads Performance Alerts</h2>\n"
        
        for alert in alerts:
            severity_color = {
                'HIGH': 'red',
                'MEDIUM': 'orange',
                'LOW': 'yellow'
            }.get(alert['severity'], 'black')
            
            body += f"""
            <div style="border: 1px solid {severity_color}; padding: 10px; margin: 5px;">
                <h3 style="color: {severity_color};">{alert['type']} - {alert['severity']}</h3>
                <p><strong>Campaign ID:</strong> {alert['campaign_id']}</p>
                <p><strong>Message:</strong> {alert['message']}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Enviar email
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['username'], self.email_config['password'])
        server.send_message(msg)
        server.quit()
    
    def run_monitoring_cycle(self):
        """Ejecutar ciclo de monitoreo"""
        campaigns = self.get_active_campaigns()
        all_alerts = []
        
        for campaign in campaigns:
            alerts = self.check_performance_alerts(campaign['id'])
            all_alerts.extend(alerts)
        
        if all_alerts:
            self.send_alert_email(all_alerts)
        
        return all_alerts

# Uso del sistema de monitoreo
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    EMAIL_CONFIG = {
        'from': 'alerts@yourcompany.com',
        'to': 'marketing@yourcompany.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'
    }
    
    # Crear sistema de monitoreo
    monitoring = IntelligentMonitoringSystem(ACCESS_TOKEN, AD_ACCOUNT_ID, EMAIL_CONFIG)
    
    # Ejecutar monitoreo
    alerts = monitoring.run_monitoring_cycle()
    
    print(f"Monitoring completed. {len(alerts)} alerts generated.")
```

### 5.2 Sistema de Optimización Automática

**Optimizador Inteligente:**
```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

class IntelligentOptimizer:
    def __init__(self, access_token, ad_account_id):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.model = None
        self.feature_importance = None
        
    def collect_training_data(self, days=30):
        """Recopilar datos de entrenamiento"""
        data = []
        
        # Obtener datos históricos de campañas
        campaigns = self.get_campaigns()
        
        for campaign in campaigns:
            metrics = self.get_campaign_metrics(campaign['id'], days)
            
            if metrics:
                # Obtener características de la campaña
                features = self.extract_features(campaign, metrics)
                data.append(features)
        
        return pd.DataFrame(data)
    
    def extract_features(self, campaign, metrics):
        """Extraer características para el modelo"""
        return {
            'campaign_id': campaign['id'],
            'objective': campaign['objective'],
            'budget': campaign.get('daily_budget', 0),
            'targeting_size': self.get_targeting_size(campaign['id']),
            'creative_count': self.get_creative_count(campaign['id']),
            'day_of_week': datetime.now().weekday(),
            'hour_of_day': datetime.now().hour,
            'impressions': metrics.get('impressions', 0),
            'clicks': metrics.get('clicks', 0),
            'spend': metrics.get('spend', 0),
            'conversions': metrics.get('conversions', 0),
            'ctr': metrics.get('ctr', 0),
            'cpc': metrics.get('cpc', 0),
            'cpm': metrics.get('cpm', 0),
            'cpa': metrics.get('cpa', 0),
            'roas': metrics.get('roas', 0)
        }
    
    def train_model(self, data):
        """Entrenar modelo de predicción"""
        # Preparar características y objetivo
        feature_columns = [
            'objective', 'budget', 'targeting_size', 'creative_count',
            'day_of_week', 'hour_of_day', 'impressions', 'clicks', 'spend'
        ]
        
        X = data[feature_columns]
        y = data['roas']  # Predecir ROAS
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Calcular importancia de características
        self.feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Evaluar modelo
        score = self.model.score(X_test, y_test)
        print(f"Model R² Score: {score:.3f}")
        
        return score
    
    def predict_performance(self, campaign_features):
        """Predecir performance de una campaña"""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        prediction = self.model.predict([campaign_features])
        return prediction[0]
    
    def optimize_campaign(self, campaign_id):
        """Optimizar campaña basándose en predicciones"""
        campaign = self.get_campaign(campaign_id)
        current_features = self.extract_features(campaign, {})
        
        # Predecir performance actual
        current_roas = self.predict_performance([
            current_features['objective'],
            current_features['budget'],
            current_features['targeting_size'],
            current_features['creative_count'],
            current_features['day_of_week'],
            current_features['hour_of_day'],
            current_features['impressions'],
            current_features['clicks'],
            current_features['spend']
        ])
        
        # Probar diferentes configuraciones
        optimizations = []
        
        # Optimizar presupuesto
        for budget_multiplier in [0.8, 1.0, 1.2, 1.5]:
            new_budget = current_features['budget'] * budget_multiplier
            new_features = current_features.copy()
            new_features['budget'] = new_budget
            
            predicted_roas = self.predict_performance([
                new_features['objective'],
                new_features['budget'],
                new_features['targeting_size'],
                new_features['creative_count'],
                new_features['day_of_week'],
                new_features['hour_of_day'],
                new_features['impressions'],
                new_features['clicks'],
                new_features['spend']
            ])
            
            optimizations.append({
                'type': 'budget',
                'value': new_budget,
                'predicted_roas': predicted_roas,
                'improvement': predicted_roas - current_roas
            })
        
        # Encontrar mejor optimización
        best_optimization = max(optimizations, key=lambda x: x['improvement'])
        
        if best_optimization['improvement'] > 0.1:  # Mejora significativa
            # Aplicar optimización
            self.apply_optimization(campaign_id, best_optimization)
            
            return {
                'campaign_id': campaign_id,
                'optimization': best_optimization,
                'applied': True
            }
        
        return {
            'campaign_id': campaign_id,
            'optimization': best_optimization,
            'applied': False,
            'reason': 'Improvement not significant enough'
        }
    
    def apply_optimization(self, campaign_id, optimization):
        """Aplicar optimización a la campaña"""
        if optimization['type'] == 'budget':
            # Actualizar presupuesto
            self.update_campaign_budget(campaign_id, optimization['value'])
        
        # Registrar optimización
        self.log_optimization(campaign_id, optimization)

# Uso del optimizador inteligente
if __name__ == "__main__":
    # Configurar credenciales
    ACCESS_TOKEN = "your_access_token"
    AD_ACCOUNT_ID = "your_ad_account_id"
    
    # Crear optimizador
    optimizer = IntelligentOptimizer(ACCESS_TOKEN, AD_ACCOUNT_ID)
    
    # Recopilar datos de entrenamiento
    training_data = optimizer.collect_training_data(days=30)
    
    # Entrenar modelo
    model_score = optimizer.train_model(training_data)
    
    # Optimizar campaña específica
    optimization_result = optimizer.optimize_campaign("campaign_id")
    
    print(f"Optimization result: {optimization_result}")
```

---

## 6. Herramientas de Automatización

### 6.1 Zapier Integration

**Zapier Workflows:**
```
Workflow 1: Monitoreo de Performance
Trigger: Facebook Ads - New Campaign Performance
Action: Google Sheets - Add Row
Condition: CTR < 1.0 OR CPC > 3.0
Result: Registro automático de campañas de bajo rendimiento

Workflow 2: Alertas de Presupuesto
Trigger: Facebook Ads - Daily Spend
Action: Email - Send Alert
Condition: Spend > $1000
Result: Notificación automática de gasto alto

Workflow 3: Reportes Automáticos
Trigger: Schedule - Daily at 9 AM
Action: Facebook Ads - Get Campaign Data
Action: Google Sheets - Update Report
Result: Reporte diario automático

Workflow 4: Optimización de Presupuestos
Trigger: Facebook Ads - Campaign Performance
Action: Facebook Ads - Update Budget
Condition: ROAS > 4.0
Result: Aumento automático de presupuesto para campañas exitosas
```

### 6.2 Microsoft Power Automate

**Power Automate Flows:**
```
Flow 1: Monitoreo de Campañas
Trigger: Schedule - Every 2 hours
Action: Facebook Ads API - Get Campaign Data
Action: Excel - Update Data
Condition: Performance below threshold
Action: Teams - Send Notification
Result: Monitoreo continuo y notificaciones

Flow 2: Optimización Automática
Trigger: Facebook Ads - Campaign Update
Action: AI Builder - Analyze Performance
Action: Facebook Ads API - Update Campaign
Result: Optimización automática basada en IA

Flow 3: Reportes Ejecutivos
Trigger: Schedule - Weekly on Monday
Action: Facebook Ads API - Get Weekly Data
Action: Power BI - Update Dashboard
Action: Email - Send Executive Report
Result: Reporte ejecutivo semanal automático
```

---

## 7. Mejores Prácticas

### 7.1 Seguridad y Compliance

**Mejores Prácticas de Seguridad:**
```
Credenciales:
- Usar variables de entorno para tokens
- Rotar tokens regularmente
- Implementar autenticación de dos factores
- Monitorear acceso a APIs

Datos:
- Encriptar datos sensibles
- Implementar logging de auditoría
- Cumplir con GDPR y CCPA
- Backup regular de datos

APIs:
- Implementar rate limiting
- Usar HTTPS para todas las comunicaciones
- Validar inputs y outputs
- Monitorear uso de API
```

### 7.2 Monitoreo y Mantenimiento

**Monitoreo de Automatización:**
```
Métricas Clave:
- Tiempo de ejecución de scripts
- Tasa de éxito de automatizaciones
- Errores y excepciones
- Uso de recursos

Alertas:
- Fallos en automatizaciones
- Performance degradada
- Uso excesivo de APIs
- Errores de conectividad

Mantenimiento:
- Actualizaciones regulares de scripts
- Monitoreo de cambios en APIs
- Testing de automatizaciones
- Documentación de cambios
```

### 7.3 Escalabilidad

**Consideraciones de Escalabilidad:**
```
Performance:
- Optimizar consultas a APIs
- Implementar caching
- Usar procesamiento asíncrono
- Monitorear uso de recursos

Recursos:
- Planificar crecimiento de datos
- Implementar load balancing
- Usar servicios en la nube
- Monitorear costos

Mantenimiento:
- Modularizar código
- Implementar testing automatizado
- Documentar procesos
- Capacitar equipos
```

---

## Conclusión

La automatización avanzada de Facebook Ads proporciona una ventaja competitiva significativa al reducir el trabajo manual, mejorar la eficiencia y optimizar el performance. La implementación exitosa requiere:

**Elementos Clave:**
1. **Scripts Personalizados**: Automatización específica para necesidades únicas
2. **Integración con APIs**: Conectividad entre sistemas y herramientas
3. **Automatización Inteligente**: IA y ML para optimización avanzada
4. **Monitoreo Continuo**: Supervisión y alertas automáticas
5. **Seguridad y Compliance**: Protección de datos y cumplimiento

**Beneficios:**
- Reducción del 80-90% en tiempo de gestión
- Optimización automática de performance
- Monitoreo 24/7 de campañas
- Integración entre sistemas
- Escalabilidad y eficiencia

**Próximos Pasos:**
1. Identificar tareas para automatizar
2. Desarrollar scripts personalizados
3. Implementar integraciones con APIs
4. Configurar monitoreo inteligente
5. Optimizar y escalar automatizaciones

La implementación exitosa de automatización avanzada resultará en un sistema de Facebook Ads altamente eficiente, optimizado y escalable.


