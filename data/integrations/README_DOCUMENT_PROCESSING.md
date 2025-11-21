# Sistema de Procesamiento de Documentos con OCR

## Descripción

Sistema completo para extraer datos automáticamente de facturas, contratos y formularios usando OCR, clasificar documentos y archivarlos en el lugar correcto. Incluye integración con Zapier y Make.com vía webhooks.

## Características

- ✅ **OCR Multi-proveedor**: Soporta Tesseract, Google Vision, Azure Vision
- ✅ **Clasificación Automática**: Identifica facturas, contratos, formularios, recibos, cotizaciones
- ✅ **Extracción de Campos**: Extrae datos estructurados según el tipo de documento
- ✅ **Archivado Automático**: Organiza documentos por tipo y fecha
- ✅ **Integración Webhooks**: Compatible con Zapier y Make.com
- ✅ **Base de Datos**: Almacena metadatos y campos extraídos
- ✅ **Workflow Automatizado**: Procesamiento programado con Kestra

## Instalación

### Dependencias del Sistema

#### Tesseract OCR (local)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# macOS
brew install tesseract tesseract-lang

# Windows
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

#### Poppler (para PDF)
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

### Dependencias Python

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Configuración del Procesador

```python
from data.integrations.document_processor import DocumentProcessor

config = {
    "ocr": {
        "provider": "tesseract",  # o "google_vision", "azure_vision"
        "language": "spa+eng",
        # Para Google Vision:
        # "api_key": "tu-api-key",
        # "project_id": "tu-project-id",
        # Para Azure Vision:
        # "endpoint": "https://tu-endpoint.cognitiveservices.azure.com/",
        # "api_key": "tu-api-key"
    },
    "classifier": {
        # Configuración del clasificador (opcional)
    },
    "archive": {
        "base_path": "/data/documents/archive",
        "structure": "by_type_and_date"  # by_type, by_date, by_type_and_date, flat
    }
}

processor = DocumentProcessor(config)
```

### 2. Configuración de Base de Datos

Ejecutar el schema SQL:

```bash
psql -U tu_usuario -d tu_base_datos -f data/db/document_processing_schema.sql
```

### 3. Configuración de Webhooks (Zapier/Make)

#### Registrar un webhook en la base de datos:

```python
from data.integrations.document_webhooks import WebhookManager
import psycopg2

db_conn = psycopg2.connect(
    "postgresql://usuario:password@localhost/dbname"
)

webhook_manager = WebhookManager(db_conn)

webhook_manager.register_webhook(
    webhook_name="zapier_documents",
    webhook_url="https://hooks.zapier.com/hooks/catch/...",
    trigger_events=["document_processed", "document_classified"],
    document_types=["invoice", "contract"],  # Opcional: filtrar por tipo
    secret_token="tu-token-secreto",  # Opcional
    enabled=True
)
```

## Uso

### Procesar un Documento Individual

```python
from data.integrations.document_processor import DocumentProcessor

processor = DocumentProcessor(config)

# Procesar un documento
processed = processor.process_document(
    file_path="/path/to/document.pdf",
    filename="factura_001.pdf",
    archive=True
)

print(f"Tipo: {processed.document_type}")
print(f"Confianza: {processed.classification_confidence:.2%}")
print(f"Campos extraídos: {processed.extracted_fields}")
```

### Procesar un Lote de Documentos

```python
file_paths = [
    "/path/to/invoice1.pdf",
    "/path/to/contract1.pdf",
    "/path/to/form1.pdf"
]

processed_docs = processor.process_batch(file_paths, archive=True)

# Exportar resultados
processor.export_results(processed_docs, format="json")
processor.export_results(processed_docs, format="csv")
```

### Usar el Workflow de Kestra

1. **Configurar inputs en Kestra**:
   - `jdbc_url`: URL de conexión a PostgreSQL
   - `jdbc_user`: Usuario de base de datos
   - `jdbc_password`: Contraseña
   - `input_directory`: Directorio con documentos a procesar
   - `archive_directory`: Directorio para archivado
   - `ocr_provider`: Proveedor OCR a usar
   - `webhook_urls`: URLs de webhooks separadas por coma (opcional)

2. **Agregar documentos a procesar**:

```sql
INSERT INTO pending_documents 
(file_path, filename, source, priority)
VALUES 
('/data/documents/invoice.pdf', 'invoice.pdf', 'upload', 10);
```

3. **El workflow se ejecutará automáticamente** cada 6 horas o se puede activar manualmente vía webhook.

## Estructura de Datos

### Documento Procesado

```json
{
  "document_id": "DOC-20240101120000-abc12345",
  "original_filename": "factura_001.pdf",
  "document_type": "invoice",
  "classification_confidence": 0.95,
  "extracted_text": "Texto completo extraído...",
  "ocr_confidence": 0.92,
  "ocr_provider": "tesseract",
  "extracted_fields": {
    "invoice_number": "001",
    "date": "01/01/2024",
    "total": "1000.00",
    "customer_name": "Cliente ABC"
  },
  "archive_path": "/data/documents/archive/invoice/2024/01/DOC-20240101120000-abc12345.pdf",
  "processed_at": "2024-01-01T12:00:00"
}
```

### Eventos de Webhook

#### document_processed
```json
{
  "event": "document_processed",
  "document_id": "DOC-20240101120000-abc12345",
  "document_type": "invoice",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "document": { /* objeto completo del documento */ },
    "extracted_fields": { /* campos extraídos */ },
    "classification": {
      "type": "invoice",
      "confidence": 0.95
    },
    "ocr": {
      "provider": "tesseract",
      "confidence": 0.92,
      "text_length": 1234
    }
  }
}
```

## Tipos de Documentos Soportados

- **Invoice (Factura)**: Extrae número, fecha, total, cliente, items
- **Contract (Contrato)**: Extrae número, fechas, partes, términos
- **Form (Formulario)**: Extrae nombre, email, teléfono, fecha
- **Receipt (Recibo)**: Extrae número, fecha, monto, método de pago
- **Quote (Cotización)**: Extrae número, fecha, válido hasta, total
- **Statement (Estado de Cuenta)**: Extrae número, período, saldo

## Integración con Zapier/Make

### Configurar Zapier

1. Crear un Zap con trigger "Webhooks by Zapier" → "Catch Hook"
2. Copiar la URL del webhook
3. Registrar en la base de datos usando `WebhookManager`
4. Configurar acciones basadas en el tipo de documento

### Ejemplo de Zapier Flow

1. **Trigger**: Webhook recibe `document_processed`
2. **Filter**: Solo facturas (`document_type == "invoice"`)
3. **Action**: Crear registro en Google Sheets con campos extraídos
4. **Action**: Enviar email si el total > $1000

### Configurar Make (Integromat)

Similar a Zapier:
1. Crear un scenario con trigger "Webhooks" → "Custom webhook"
2. Configurar el webhook para recibir eventos
3. Usar filtros y acciones según necesidad

## Consultas SQL Útiles

### Buscar facturas por número
```sql
SELECT * FROM search_documents_by_field('invoice_number', '001', 'invoice');
```

### Estadísticas por tipo
```sql
SELECT * FROM documents_by_type;
```

### Documentos procesados hoy
```sql
SELECT * FROM recent_documents_with_fields 
WHERE processed_at >= CURRENT_DATE;
```

### Webhooks enviados
```sql
SELECT wl.*, w.webhook_name, w.webhook_url
FROM webhook_logs wl
JOIN document_webhooks w ON wl.webhook_id = w.id
WHERE wl.sent_at >= CURRENT_DATE - INTERVAL '1 day'
ORDER BY wl.sent_at DESC;
```

## Troubleshooting

### Error: Tesseract no encontrado
```bash
# Verificar instalación
tesseract --version

# Configurar ruta en Python
config = {
    "ocr": {
        "provider": "tesseract",
        "tesseract_cmd": "/usr/bin/tesseract"  # Ruta completa
    }
}
```

### Error: Google Vision API
- Verificar que las credenciales estén configuradas
- Verificar que la API esté habilitada en Google Cloud Console
- Verificar límites de cuota

### Error: Azure Vision API
- Verificar endpoint y API key
- Verificar región del recurso

## Mejoras Futuras

- [ ] Soporte para AWS Textract
- [ ] Integración con OpenAI Vision para mejor clasificación
- [ ] Machine Learning para mejorar clasificación
- [ ] Validación de campos extraídos
- [ ] Dashboard web para visualización
- [ ] API REST para procesamiento remoto

## Licencia

Ver LICENSE del proyecto principal.

