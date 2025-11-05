# Snippets de Campos CRM (HubSpot + Salesforce)

## HubSpot (API v3) – Crear propiedades personalizadas

Endpoint: `POST /crm/v3/properties/{objectType}`

Contact properties (objectType = contacts)
```json
{
  "name": "dm_variant",
  "label": "DM Variant",
  "type": "string",
  "fieldType": "select",
  "options": [
    {"label": "v_premium", "value": "v_premium"},
    {"label": "v_principal", "value": "v_principal"},
    {"label": "micro_dm", "value": "micro_dm"},
    {"label": "vip", "value": "vip"}
  ]
}
```
```json
{
  "name": "stack_detected",
  "label": "Stack Detected",
  "type": "string",
  "fieldType": "select",
  "options": [
    {"label": "hubspot", "value": "hubspot"},
    {"label": "ga4", "value": "ga4"},
    {"label": "meta_ads", "value": "meta_ads"},
    {"label": "salesforce", "value": "salesforce"},
    {"label": "otro", "value": "otro"}
  ]
}
```
```json
{
  "name": "objective",
  "label": "Objective",
  "type": "string",
  "fieldType": "select",
  "options": [
    {"label": "respuesta", "value": "respuesta"},
    {"label": "demo", "value": "demo"},
    {"label": "piloto", "value": "piloto"},
    {"label": "recurso", "value": "recurso"},
    {"label": "calendario", "value": "calendario"}
  ]
}
```
```json
{
  "name": "reply_status",
  "label": "Reply Status",
  "type": "string",
  "fieldType": "select",
  "options": [
    {"label": "no_reply", "value": "no_reply"},
    {"label": "replied", "value": "replied"},
    {"label": "booked", "value": "booked"},
    {"label": "declined", "value": "declined"}
  ]
}
```
```json
{
  "name": "cta_used",
  "label": "CTA Used",
  "type": "string",
  "fieldType": "text"
}
```
```json
{
  "name": "next_step_date",
  "label": "Next Step Date",
  "type": "date",
  "fieldType": "date"
}
```

Nota: Para Activities (Engagements API) guarda `utm_*` y `nota` con nomenclatura propuesta.

## Salesforce – sfdx (Custom Fields)

Pre-requisitos: `sfdx` instalado y autenticado; objeto `Lead` o `Contact` según tu proceso.

Campos en Lead (ejemplo)
```bash
sfdx force:cmdt:generate --devname Outreach_Settings --label "Outreach Settings"
```
```bash
sfdx force:source:deploy -m CustomObject:Lead
sfdx force:source:deploy -m CustomObject:Contact
```
```bash
sfdx force:field:create -n DM_Variant__c -l "DM Variant" -t Text -o Lead
sfdx force:field:create -n Stack_Detected__c -l "Stack Detected" -t Text -o Lead
sfdx force:field:create -n Objective__c -l "Objective" -t Picklist -o Lead -v "respuesta;demo;piloto;recurso;calendario"
sfdx force:field:create -n Reply_Status__c -l "Reply Status" -t Picklist -o Lead -v "no_reply;replied;booked;declined"
sfdx force:field:create -n CTA_Used__c -l "CTA Used" -t Text -o Lead
sfdx force:field:create -n Next_Step_Date__c -l "Next Step Date" -t Date -o Lead
```

Validaciones útiles (ejemplo)
```apex
// Bloquear valores fuera de catálogo en Objective__c
// Recomendado crear Validation Rule en vez de Apex trigger
```

Informes básicos sugeridos
- Lead report por `DM_Variant__c` y `Stack_Detected__c`
- Conversión DM→Demo (booked/total replied)
- Tiempo a respuesta: campo de fórmula o reporte con fecha de primera actividad + respuesta

## UTM en CRM
- Guardar `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` en Lead/Contact o Campaign Member
- Relacionar con Campaigns (Salesforce) o Campaigns (HubSpot) para atribución

