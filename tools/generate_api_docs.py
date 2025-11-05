#!/usr/bin/env python3
"""
Genera documentación de API para integraciones
Crea ejemplos de uso para diferentes servicios (LinkedIn, Google Analytics, etc.)
"""
import sys
from pathlib import Path
from datetime import datetime

def generate_linkedin_api_example():
    """Ejemplo de integración con LinkedIn Campaign Manager API"""
    return """```python
#!/usr/bin/env python3
\"\"\"
Ejemplo de integración con LinkedIn Campaign Manager API
Requiere: pip install requests python-dotenv
\"\"\"
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales (guardar en .env)
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
ACCOUNT_ID = os.getenv('LINKEDIN_ACCOUNT_ID')

def get_campaign_performance(campaign_id):
    \"\"\"Obtiene métricas de performance de una campaña\"\"\"
    url = f"https://api.linkedin.com/v2/adAnalyticsV2"
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    params = {
        'q': 'analytics',
        'pivot': 'CAMPAIGN',
        'timeGranularity': 'DAILY',
        'dateRange.start.day': 1,
        'dateRange.start.month': 1,
        'dateRange.start.year': 2024,
        'campaigns[0]': f'urn:li:sponsoredCampaign:{campaign_id}',
        'fields': 'impressions,clicks,ctr,spend,conversions'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def sync_creative_to_linkedin(creative_data):
    \"\"\"Sincroniza un creative con LinkedIn\"\"\"
    url = f"https://api.linkedin.com/v2/adDirectSponsoredContents"
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'account': f'urn:li:sponsoredAccount:{ACCOUNT_ID}',
        'creative': {
            'variables': {
                'image': creative_data.get('image_url'),
                'title': creative_data.get('headline'),
                'description': creative_data.get('description')
            }
        },
        'campaign': creative_data.get('campaign_urn')
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Uso
if __name__ == '__main__':
    # Obtener performance
    performance = get_campaign_performance('123456789')
    if performance:
        print("Métricas:", performance)
    
    # Sincronizar creative
    creative = {
        'image_url': 'https://example.com/image.jpg',
        'headline': 'Test Creative',
        'description': 'Description here',
        'campaign_urn': 'urn:li:sponsoredCampaign:123456789'
    }
    result = sync_creative_to_linkedin(creative)
    if result:
        print("Creative sincronizado:", result)
```"""

def generate_ga4_api_example():
    """Ejemplo de integración con Google Analytics 4 API"""
    return """```python
#!/usr/bin/env python3
\"\"\"
Ejemplo de integración con Google Analytics 4 Data API
Requiere: pip install google-analytics-data
\"\"\"
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric
)
import os

# Configurar credenciales
# 1. Crear service account en Google Cloud Console
# 2. Descargar JSON key file
# 3. Añadir a GA4 como Viewer

PROPERTY_ID = os.getenv('GA4_PROPERTY_ID')
CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def get_utm_performance(start_date, end_date):
    \"\"\"Obtiene performance por UTM parameters\"\"\"
    client = BetaAnalyticsDataClient.from_service_account_json(CREDENTIALS_PATH)
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
            Dimension(name="sessionCampaignName"),
            Dimension(name="sessionDefaultChannelGroup")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="conversions"),
            Metric(name="totalRevenue")
        ]
    )
    
    response = client.run_report(request)
    
    results = []
    for row in response.rows:
        results.append({
            'source': row.dimension_values[0].value,
            'medium': row.dimension_values[1].value,
            'campaign': row.dimension_values[2].value,
            'channel': row.dimension_values[3].value,
            'sessions': row.metric_values[0].value,
            'users': row.metric_values[1].value,
            'conversions': row.metric_values[2].value,
            'revenue': row.metric_values[3].value
        })
    
    return results

def get_creative_performance(utm_content_pattern):
    \"\"\"Filtra performance por utm_content (creative)\"\"\"
    client = BetaAnalyticsDataClient.from_service_account_json(CREDENTIALS_PATH)
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimensions=[
            Dimension(name="eventName"),
            Dimension(name="pagePath")
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers")
        ],
        dimension_filter={
            'filter': {
                'field_name': 'pagePath',
                'string_filter': {
                    'match_type': 'CONTAINS',
                    'value': f'utm_content={utm_content_pattern}'
                }
            }
        }
    )
    
    response = client.run_report(request)
    return [row for row in response.rows]

# Uso
if __name__ == '__main__':
    # Performance por UTMs últimos 30 días
    performance = get_utm_performance('30daysAgo', 'today')
    for result in performance:
        print(f"{result['campaign']}: {result['sessions']} sesiones, {result['conversions']} conversiones")
    
    # Performance específico de creative
    creative_perf = get_creative_performance('metrics_cta_demo')
    print(f"Eventos del creative: {len(creative_perf)}")
```"""

def generate_webhook_example():
    """Ejemplo de webhook para recibir datos de LinkedIn"""
    return """```python
#!/usr/bin/env python3
\"\"\"
Webhook para recibir eventos de LinkedIn Campaign Manager
Ejemplo usando Flask
Requiere: pip install flask requests
\"\"\"
from flask import Flask, request, jsonify
import requests
import csv
from pathlib import Path

app = Flask(__name__)

# CSV Master path
CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'

def update_creative_performance(utm_content, metrics):
    \"\"\"Actualiza métricas de un creative en CSV\"\"\"
    # Leer CSV
    rows = []
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    # Actualizar fila correspondiente
    for row in rows:
        if row.get('utm_content') == utm_content:
            row['impressions'] = metrics.get('impressions', '')
            row['clicks'] = metrics.get('clicks', '')
            row['ctr'] = metrics.get('ctr', '')
            row['spend'] = metrics.get('spend', '')
            row['conversions'] = metrics.get('conversions', '')
            break
    
    # Guardar CSV
    with open(CSV_MASTER, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

@app.route('/webhook/linkedin', methods=['POST'])
def linkedin_webhook():
    \"\"\"Endpoint para recibir eventos de LinkedIn\"\"\"
    data = request.json
    
    # Validar webhook signature (en producción)
    # signature = request.headers.get('X-LinkedIn-Signature')
    # verify_signature(signature, request.data)
    
    event_type = data.get('event_type')
    
    if event_type == 'AD_PERFORMANCE_UPDATE':
        # Extraer métricas
        creative_id = data.get('creative_id')
        metrics = {
            'impressions': data.get('impressions'),
            'clicks': data.get('clicks'),
            'ctr': data.get('ctr'),
            'spend': data.get('spend'),
            'conversions': data.get('conversions')
        }
        
        # Buscar utm_content por creative_id o campaign_id
        utm_content = data.get('utm_content')  # O mapear desde creative_id
        
        if utm_content:
            update_creative_performance(utm_content, metrics)
            return jsonify({'status': 'success'}), 200
    
    return jsonify({'status': 'ignored'}), 200

@app.route('/webhook/health', methods=['GET'])
def health_check():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # En producción, usar gunicorn o similar
    app.run(host='0.0.0.0', port=5000, debug=True)
```"""

def generate_api_docs():
    """Genera documentación completa de APIs"""
    doc = f"""# 📡 Documentación de APIs para Integración

Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 Tabla de Contenidos

1. [LinkedIn Campaign Manager API](#linkedin-campaign-manager-api)
2. [Google Analytics 4 API](#google-analytics-4-api)
3. [Webhooks](#webhooks)
4. [CRM APIs](#crm-apis)
5. [Configuración](#configuración)

---

## 🔗 LinkedIn Campaign Manager API

### Autenticación

LinkedIn usa OAuth 2.0. Pasos:

1. Crear aplicación en [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Obtener `CLIENT_ID` y `CLIENT_SECRET`
3. Solicitar permisos: `r_ads`, `rw_ads`
4. Obtener `ACCESS_TOKEN` (refresh token para producción)

### Ejemplo de Uso

{generate_linkedin_api_example()}

### Endpoints Principales

- **GET** `/v2/adAnalyticsV2` - Métricas de campañas
- **POST** `/v2/adDirectSponsoredContents` - Crear/sincronizar creative
- **GET** `/v2/adCreativesV2` - Listar creativos
- **PUT** `/v2/adCreativesV2/{id}` - Actualizar creative

### Rate Limits

- 100 requests/minuto por aplicación
- 500 requests/día (development)
- 10,000 requests/día (production, aprobación requerida)

---

## 📊 Google Analytics 4 API

### Autenticación

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar Google Analytics Data API
3. Crear Service Account
4. Descargar JSON key file
5. Añadir service account a GA4 property como Viewer

### Ejemplo de Uso

{generate_ga4_api_example()}

### Dimensiones Útiles para Tracking

- `sessionSource` - utm_source
- `sessionMedium` - utm_medium
- `sessionCampaignName` - utm_campaign
- `eventName` - Eventos personalizados
- `pagePath` - Para filtrar por UTMs en URL

### Métricas Principales

- `sessions` - Sesiones
- `totalUsers` - Usuarios únicos
- `conversions` - Conversiones
- `totalRevenue` - Ingresos
- `bounceRate` - Tasa de rebote

---

## 🔔 Webhooks

### Configuración

1. Exponer endpoint público (usar ngrok para desarrollo)
2. Registrar URL en LinkedIn Campaign Manager
3. Validar signature en producción

### Ejemplo de Implementación

{generate_webhook_example()}

### Eventos Disponibles

- `AD_PERFORMANCE_UPDATE` - Actualización de métricas
- `CAMPAIGN_STATUS_CHANGE` - Cambio de estado de campaña
- `CREATIVE_APPROVED` - Creative aprobado
- `CREATIVE_REJECTED` - Creative rechazado

---

## 🏢 CRM APIs

Ver documentación detallada en:
- [`TOOLS_CRM_COMPARISON.md`](../TOOLS_CRM_COMPARISON.md) - Sección "API Examples"

CRMs soportados:
- HubSpot
- Pipedrive
- ActiveCampaign
- Close
- Zoho

---

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# LinkedIn
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_ACCOUNT_ID=your_account_id

# Google Analytics
GA4_PROPERTY_ID=your_property_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# CRM
HUBSPOT_API_KEY=your_api_key
PIPEDRIVE_API_TOKEN=your_api_token
```

### Instalación de Dependencias

```bash
pip install requests python-dotenv google-analytics-data flask
```

---

## 📚 Recursos Adicionales

- [LinkedIn Marketing API Docs](https://docs.microsoft.com/en-us/linkedin/marketing/)
- [GA4 Data API Docs](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Webhook Security Best Practices](https://developer.github.com/webhooks/securing/)

---

**Nota:** Esta documentación se genera automáticamente. Para actualizar ejemplos, edita `tools/generate_api_docs.py`.
"""
    
    return doc

def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    docs_dir = root_dir / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    output_path = docs_dir / 'API_INTEGRATION_GUIDE.md'
    
    doc_content = generate_api_docs()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("=" * 80)
    print("📡 Generador de Documentación de APIs")
    print("=" * 80)
    print()
    print(f"✅ Documentación generada: {output_path}")
    print()
    print("📋 Incluye:")
    print("   • Ejemplos de LinkedIn Campaign Manager API")
    print("   • Ejemplos de Google Analytics 4 API")
    print("   • Ejemplos de Webhooks")
    print("   • Guía de configuración")
    print()

if __name__ == '__main__':
    main()

