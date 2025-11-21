# 🔗 Integraciones - Documentos BLATAM

Guía completa de integraciones con herramientas y plataformas externas.

---

## 📋 Tabla de Contenidos

- [Google Sheets](#google-sheets)
- [CRM Systems](#crm-systems)
- [Email Marketing](#email-marketing)
- [Automatización](#automatización)
- [APIs](#apis)
- [Herramientas de Desarrollo](#herramientas-de-desarrollo)

---

## 📊 Google Sheets

### Configuración Básica

**Objetivo**: Conectar Documentos BLATAM con Google Sheets para dashboards y análisis.

**Pasos**:

1. **Preparar Template CSV**
```bash
# Usar template existente
cp 16_data_analytics/dashboard_template.csv mi_dashboard.csv

# O crear desde cero
cat > mi_dashboard.csv << EOF
Fecha,Métrica,Valor
2025-01-15,Leads,150
2025-01-16,Leads,175
EOF
```

2. **Importar a Google Sheets**
   - Abrir Google Sheets
   - Archivo → Importar → Subir
   - Seleccionar archivo CSV
   - Configurar opciones de importación

3. **Configurar Fórmulas**
```excel
# Ejemplo de fórmulas comunes
=SUM(B2:B100)  # Suma total
=AVERAGE(B2:B100)  # Promedio
=COUNTIF(B2:B100,">100")  # Contar condicional
```

**Recursos**:
- [`README_Sheets_Import.md`](06_documentation/README_Sheets_Import.md)
- Templates: [`16_data_analytics/`](16_data_analytics/)

---

### Dashboards Avanzados

**Templates Disponibles**:

1. **Dashboard Ejecutivo**
   - KPIs principales
   - Tendencias visuales
   - Comparativas

2. **Dashboard de Marketing**
   - Métricas de campañas
   - ROI por canal
   - Conversiones

3. **Dashboard de Ventas**
   - Pipeline
   - Velocidad de ventas
   - Forecast

**Configuración**:
```bash
# Usar script de configuración
python scripts/setup_google_sheets.py \
  --template executive \
  --output mi_dashboard.csv
```

---

## 💼 CRM Systems

### HubSpot

**Integración Básica**:

1. **API Setup**
```python
import requests

HUBSPOT_API_KEY = "tu_api_key"
BASE_URL = "https://api.hubapi.com"

def create_contact(email, firstname, lastname):
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "email": email,
            "firstname": firstname,
            "lastname": lastname
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

2. **Sincronización Automática**
```bash
# Script de sincronización
python scripts/sync_hubspot.py \
  --source leads.csv \
  --action create
```

**Recursos**:
- Templates: [`09_sales/Crm/`](09_sales/Crm/)
- Scripts: [`04_operations/`](04_operations/)

---

### Salesforce

**Integración con REST API**:

```python
import requests

SALESFORCE_INSTANCE = "tu-instance.salesforce.com"
ACCESS_TOKEN = "tu_access_token"

def create_lead(email, company):
    url = f"https://{SALESFORCE_INSTANCE}/services/data/v57.0/sobjects/Lead/"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "Email": email,
        "Company": company,
        "LeadSource": "Web"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

---

## 📧 Email Marketing

### Mailchimp

**Configuración**:

1. **API Key Setup**
```bash
# Agregar a .env
MAILCHIMP_API_KEY=tu_api_key
MAILCHIMP_LIST_ID=tu_list_id
```

2. **Agregar Suscriptores**
```python
import requests
import os

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")
DATACENTER = MAILCHIMP_API_KEY.split("-")[1]

def add_subscriber(email, firstname, lastname):
    url = f"https://{DATACENTER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
    headers = {
        "Authorization": f"Bearer {MAILCHIMP_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email_address": email,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": firstname,
            "LNAME": lastname
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

**Recursos**:
- Templates: [`01_marketing/04_email_marketing/`](01_marketing/04_email_marketing/)
- Secuencias: [`01_marketing/Sequences/`](01_marketing/Sequences/)

---

### SendGrid

**Envío de Emails Transaccionales**:

```python
import sendgrid
from sendgrid.helpers.mail import Mail

SG_API_KEY = "tu_api_key"
sg = sendgrid.SendGridAPIClient(api_key=SG_API_KEY)

def send_email(to_email, subject, content):
    message = Mail(
        from_email="noreply@tudominio.com",
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    response = sg.send(message)
    return response.status_code
```

---

## ⚙️ Automatización

### Zapier

**Zap Básico**: Google Sheets → HubSpot

**Configuración**:

1. **Trigger**: Nueva fila en Google Sheets
2. **Action**: Crear contacto en HubSpot
3. **Mapping**:
   - Email → Email
   - Nombre → First Name
   - Empresa → Company

**Template JSON**:
```json
{
  "zap_name": "Sheets to HubSpot",
  "trigger": {
    "app": "Google Sheets",
    "event": "New Spreadsheet Row"
  },
  "action": {
    "app": "HubSpot",
    "action": "Create Contact",
    "mapping": {
      "email": "{{Email}}",
      "firstname": "{{Nombre}}",
      "company": "{{Empresa}}"
    }
  }
}
```

**Recursos**:
- Blueprints: [`06_documentation/Blueprints_Make_Zapier.md`](06_documentation/Blueprints_Make_Zapier.md)
- Guías: [`06_documentation/`](06_documentation/)

---

### Make (Integromat)

**Escenario**: Automatizar nurturing de leads

**Flujo**:

1. **Trigger**: Nuevo lead en CRM
2. **Filtro**: Lead calificado
3. **Action 1**: Agregar a lista de email
4. **Action 2**: Enviar email de bienvenida
5. **Action 3**: Programar seguimiento

**Configuración**:
```json
{
  "scenario_name": "Lead Nurturing",
  "modules": [
    {
      "type": "trigger",
      "app": "HubSpot",
      "event": "New Contact"
    },
    {
      "type": "filter",
      "condition": "{{Contact.Lead_Score}} > 50"
    },
    {
      "type": "action",
      "app": "Mailchimp",
      "action": "Add Subscriber"
    }
  ]
}
```

---

## 🔌 APIs

### OpenAI API

**Uso para Generación de Contenido**:

```python
import openai

openai.api_key = "tu_api_key"

def generate_content(prompt, max_tokens=500):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].text.strip()
```

**Ejemplo de Uso**:
```python
prompt = "Escribe un post para Instagram sobre marketing con IA"
content = generate_content(prompt)
print(content)
```

**Recursos**:
- Scripts: [`08_ai_artificial_intelligence/`](08_ai_artificial_intelligence/)
- Templates: [`06_documentation/Templates/`](06_documentation/Templates/)

---

### Google Analytics API

**Obtener Métricas**:

```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

def get_analytics_data(property_id, start_date, end_date):
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[{"start_date": start_date, "end_date": end_date}],
        metrics=[{"name": "sessions"}, {"name": "users"}],
        dimensions=[{"name": "date"}]
    )
    
    response = client.run_report(request)
    return response
```

---

## 🛠️ Herramientas de Desarrollo

### GitHub Actions

**CI/CD Automático**:

```yaml
name: Validate Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Validate frontmatter
        run: |
          python 06_documentation/Scripts/frontmatter_validator.py
      
      - name: Check links
        run: |
          python 06_documentation/Scripts/find_broken_links.py
```

---

### Docker

**Containerización**:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Docker Compose**:
```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - API_KEY=${API_KEY}
    ports:
      - "3000:3000"
```

---

## 📱 Redes Sociales

### Instagram API

**Automatización de DMs** (usando herramientas de terceros):

```python
# Nota: Instagram API oficial tiene limitaciones
# Usar herramientas como Instagrapi o APIs de terceros

def send_dm(user_id, message):
    # Implementación según herramienta usada
    pass
```

**Recursos**:
- Templates: [`01_marketing/Sequences/`](01_marketing/Sequences/)
- Scripts: [`01_marketing/Scripts/`](01_marketing/Scripts/)

---

### LinkedIn API

**Obtener Perfil**:

```python
import requests

LINKEDIN_ACCESS_TOKEN = "tu_access_token"

def get_profile():
    url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
```

---

## 🔐 Seguridad

### Variables de Entorno

**Configuración Segura**:

```bash
# .env file (no commitear)
API_KEY=tu_api_key_secreta
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=tu_secret_key
```

**Uso en Código**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
```

---

## 📚 Recursos Adicionales

- [`WORKFLOWS.md`](WORKFLOWS.md) - Flujos de trabajo con integraciones
- [`EXAMPLES.md`](EXAMPLES.md) - Ejemplos de integraciones
- [`BEST_PRACTICES.md`](BEST_PRACTICES.md) - Mejores prácticas de integración

---

## ✅ Checklist de Integración

Antes de integrar:

- [ ] He revisado la documentación de la API
- [ ] He obtenido las credenciales necesarias
- [ ] He configurado variables de entorno
- [ ] He probado la conexión
- [ ] He manejado errores apropiadamente
- [ ] He documentado la integración

---

**¿Necesitas ayuda con una integración específica?**

Abre un issue o consulta la documentación en [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

---

**Última actualización**: 2025-01-XX

