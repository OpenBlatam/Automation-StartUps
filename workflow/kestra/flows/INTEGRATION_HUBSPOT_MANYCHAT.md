# Integración HubSpot → ManyChat

Guía completa para configurar e integrar la automatización que envía mensajes a ManyChat cuando se crea un lead en HubSpot con interés en un producto.

## 📋 Descripción

Esta automatización detecta cuando se crea un nuevo lead en HubSpot con la propiedad `interés_producto` = 'X' y envía automáticamente un mensaje personalizado al usuario en ManyChat usando su `manychat_user_id`.

**Mensaje enviado**: "Hola {nombre}, gracias por tu interés en {producto}. ¿Te gustaría agendar una demo?"

## 🏗️ Arquitectura

```
HubSpot → Webhook → Kestra Flow → ManyChat API → Usuario
```

## 📦 Componentes Requeridos

1. **Kestra**: Orquestador de workflows (ya desplegado)
2. **External Secrets**: Para gestionar API keys de forma segura
3. **Ingress**: Para exponer webhooks de Kestra
4. **HubSpot**: CRM con contactos y propiedades configuradas
5. **ManyChat**: Plataforma de mensajería con usuarios

## 🔧 Configuración del Stack

### 1. Secrets (External Secrets)

Los secrets se sincronizan automáticamente desde AWS Secrets Manager usando External Secrets Operator.

**Archivo**: `security/secrets/externalsecrets-hubspot-db.yaml`

**Secrets requeridos en AWS Secrets Manager**:

```bash
# ManyChat API Key
aws secretsmanager create-secret \
  --name messaging/manychat/api_key \
  --secret-string "YOUR_MANYCHAT_API_KEY"

# HubSpot Token (si no existe ya)
aws secretsmanager create-secret \
  --name crm/hubspot/token \
  --secret-string "YOUR_HUBSPOT_TOKEN"
```

**Aplicar External Secrets**:

```bash
kubectl apply -f security/secrets/externalsecrets-hubspot-db.yaml

# Verificar sincronización
kubectl get externalsecret -n workflows
kubectl describe externalsecret manychat-api-key -n workflows
kubectl get secret manychat-api-key -n workflows
```

### 2. Ingress (Exponer Webhooks)

**Archivo**: `kubernetes/ingress/kestra-ingress.yaml`

**Aplicar Ingress**:

```bash
kubectl apply -f kubernetes/ingress/kestra-ingress.yaml

# Verificar
kubectl get ingress -n workflows
```

**URL del Webhook**: 
```
https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_to_manychat/hubspot
```

**Nota**: Reemplaza `kestra.example.com` con tu dominio real.

### 3. Cargar Flow en Kestra

**Archivo**: `workflow/kestra/flows/hubspot_to_manychat.yaml`

**Opciones**:

**Opción A: Desde UI de Kestra**:
1. Acceder a Kestra UI: `kubectl port-forward -n workflows service/kestra 8080:8080`
2. Navegar a Flows → Create
3. Paste el contenido YAML del flow
4. Guardar

**Opción B: Desde API**:
```bash
KESTRA_URL="http://kestra.workflows.svc.cluster.local:8080"
curl -X POST "${KESTRA_URL}/api/v1/flows" \
  -H "Content-Type: application/yaml" \
  -u admin:admin \
  --data-binary @workflow/kestra/flows/hubspot_to_manychat.yaml
```

**Opción C: Desde kubectl (si Kestra soporta ConfigMaps)**:
```bash
kubectl create configmap hubspot-to-manychat-flow \
  --from-file=hubspot_to_manychat.yaml=workflow/kestra/flows/hubspot_to_manychat.yaml \
  -n workflows
```

### 4. Configurar Variables en Kestra

Las variables deben configurarse en Kestra. Pueden venir de:
- External Secrets (recomendado)
- Variables de entorno en el Deployment
- Inputs manuales por ejecución

**Opción A: Usar External Secrets (Recomendado)**:

Crear un init container o script que lea los secrets y los exponga como variables de entorno:

```yaml
# Ejemplo de cómo inyectar secrets en variables de Kestra
env:
  - name: MANYCHAT_API_KEY
    valueFrom:
      secretKeyRef:
        name: manychat-api-key
        key: MANYCHAT_API_KEY
  - name: HUBSPOT_TOKEN
    valueFrom:
      secretKeyRef:
        name: hubspot-token
        key: HUBSPOT_TOKEN
```

**Opción B: Variables en Namespace de Kestra**:

Desde la UI de Kestra:
1. Ir a Namespaces → workflows → Variables
2. Crear variables:
   - `manychat_api_key`: Valor del secret
   - `hubspot_token`: Valor del secret (si se necesita para fetch adicional)

**Opción C: Inputs por ejecución**:

Si se usa la API de Kestra para trigger manual, pasar inputs:

```json
{
  "inputs": {
    "manychat_api_key": "xxx",
    "manychat_page_id": "optional"
  }
}
```

## 🔗 Configuración en HubSpot

### 1. Crear Propiedades Personalizadas

Asegúrate de que los contactos tengan estas propiedades:

1. **`interés_producto`**:
   - Tipo: Texto de línea única
   - Campo visible para formularios: No (opcional)
   - Descripción: Producto de interés del lead

2. **`manychat_user_id`**:
   - Tipo: Texto de línea única
   - Campo visible para formularios: No
   - Descripción: ID del usuario en ManyChat

**Cómo crear**:
1. HubSpot → Settings → Properties → Contact properties
2. Crear nueva propiedad
3. Configurar tipo y nombre

### 2. Configurar Webhook en HubSpot

1. **Ir a Settings → Integrations → Workflows → Webhooks**

2. **Crear nuevo webhook**:
   - URL: `https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_to_manychat/hubspot`
   - Método: POST
   - Formato: JSON

3. **Eventos a suscribir**:
   - `contact.creation`: Cuando se crea un nuevo contacto
   - `contact.propertyChange`: Cuando cambia una propiedad (opcional, filtrar por `interés_producto`)

4. **Configurar filtros** (opcional):
   - Si solo quieres cuando `interés_producto` tiene valor:
     - Trigger cuando: `interés_producto` is not empty

5. **Verificar firma** (opcional pero recomendado):
   - Habilitar "Verify signature"
   - Copiar el secret generado
   - Configurar en External Secrets como `crm/hubspot/webhook_secret`

### 3. Prueba del Webhook

**Crear contacto de prueba**:
1. Crear nuevo contacto en HubSpot
2. Asignar `interés_producto` = "Producto X"
3. Asignar `manychat_user_id` = "123456789"
4. Guardar contacto

**Verificar ejecución en Kestra**:
```bash
# Ver logs del pod de Kestra
kubectl logs -n workflows deployment/kestra -f | grep hubspot

# Ver ejecuciones desde UI
# Ir a Executions → Buscar flow "hubspot_to_manychat"
```

## 📊 Monitoreo

### Métricas de Prometheus

Kestra expone métricas automáticamente. Ver: `observability/servicemonitors/kestra.yaml`

**Ver métricas**:
```bash
kubectl port-forward -n workflows service/kestra 8080:8080
curl http://localhost:8080/metrics | grep hubspot_to_manychat
```

### Logs Estructurados

Los logs del flow incluyen información detallada:
- Contact ID
- ManyChat User ID
- Estado de envío
- Errores (si los hay)

**Ver logs**:
```bash
# Desde Kestra UI
# Executions → Seleccionar ejecución → Ver logs de cada task

# Desde kubectl
kubectl logs -n workflows deployment/kestra | \
  grep -A 10 "hubspot_to_manychat"
```

### Alertas (Opcional)

Configurar alertas en Prometheus/Grafana para:
- Fallos de envío a ManyChat
- Webhooks de HubSpot no procesados
- Tasa de error > 5%

## 🔍 Troubleshooting

### Webhook no se dispara

1. **Verificar URL del webhook en HubSpot**:
   - Debe ser la URL correcta de Kestra
   - Verificar que el Ingress esté funcionando

2. **Verificar conectividad**:
   ```bash
   curl -X POST https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_to_manychat/hubspot \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

3. **Ver logs de HubSpot**:
   - HubSpot → Settings → Integrations → Webhooks → Ver logs de webhook

### Mensaje no se envía a ManyChat

1. **Verificar ManyChat API Key**:
   ```bash
   kubectl get secret manychat-api-key -n workflows -o jsonpath='{.data.MANYCHAT_API_KEY}' | base64 -d
   ```

2. **Verificar manychat_user_id**:
   - El contacto debe tener `manychat_user_id` válido
   - El ID debe existir en ManyChat

3. **Probar API de ManyChat directamente**:
   ```bash
   curl -X POST https://api.manychat.com/fb/sending/sendContent \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "subscriber_id": "USER_ID",
       "data": {
         "messages": [{
           "type": "text",
           "text": "Test message"
         }]
       }
     }'
   ```

### Error: "interés_producto not set"

- Verificar que el contacto tenga la propiedad `interés_producto` con valor
- Verificar que el webhook de HubSpot incluya las propiedades en el payload
- Si las propiedades no vienen en el webhook, el flow intentará obtenerlas desde HubSpot API (requiere `hubspot_token`)

### Error: "manychat_user_id not set"

- Verificar que el contacto tenga `manychat_user_id` configurado
- El `manychat_user_id` debe ser un ID válido de ManyChat

## 📝 Ejemplo de Payload

### Webhook de HubSpot (contact.creation)

```json
{
  "subscriptionType": "contact.creation",
  "objectId": 12345,
  "properties": {
    "firstname": "Juan",
    "lastname": "Pérez",
    "interés_producto": "Producto X",
    "manychat_user_id": "67890"
  }
}
```

### Respuesta del Flow

**Éxito**:
```json
{
  "status": "success",
  "contacto_id": "12345",
  "manychat_user_id": "67890",
  "nombre": "Juan Pérez",
  "producto": "Producto X",
  "message_sent": "Hola Juan Pérez, gracias por tu interés en Producto X. ¿Te gustaría agendar una demo?",
  "manychat_response": {
    "status": "success"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Omisión** (sin interés_producto):
```json
{
  "status": "skipped",
  "reason": "interes_producto_not_set",
  "contacto_id": "12345",
  "message": "No se envió mensaje porque interes_producto_not_set"
}
```

## 🚀 Deployment Checklist

- [ ] Secrets creados en AWS Secrets Manager
- [ ] External Secrets aplicados y sincronizados
- [ ] Ingress creado y funcionando
- [ ] Flow cargado en Kestra
- [ ] Variables configuradas en Kestra
- [ ] Propiedades creadas en HubSpot
- [ ] Webhook configurado en HubSpot
- [ ] Prueba end-to-end exitosa
- [ ] Monitoreo configurado
- [ ] Documentación actualizada

## 📚 Referencias

- [Kestra Documentation](https://kestra.io/docs/)
- [HubSpot Webhooks API](https://developers.hubspot.com/docs/api/webhooks)
- [ManyChat API Documentation](https://manychat.github.io/dynamic_block_docs/)
- [External Secrets Operator](https://external-secrets.io/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)



