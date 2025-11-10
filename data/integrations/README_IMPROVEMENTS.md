# Mejoras Avanzadas del Sistema de Procesamiento de Documentos

## Nuevas Funcionalidades

### 1. Validación de Campos ✅

Sistema completo de validación y normalización de campos extraídos:

```python
from data.integrations.document_validator import DocumentValidator, ValidationLevel

validator = DocumentValidator(ValidationLevel.MODERATE)

# Validar documento completo
report = validator.validate_document(
    document_id="DOC-123",
    document_type="invoice",
    extracted_fields={
        "invoice_number": "001",
        "date": "01/01/2024",
        "total": "1000.50",
        "customer_email": "cliente@example.com"
    }
)

print(f"Válido: {report.overall_valid}")
print(f"Score: {report.validation_score:.2%}")
print(f"Campos normalizados: {report.fields_validated}")
```

**Características:**
- Validación de números de factura, fechas, montos, emails, teléfonos
- Normalización automática de valores
- Detección de campos requeridos faltantes
- Reportes detallados de validación

### 2. Almacenamiento en la Nube ☁️

Integración con S3 y Google Cloud Storage:

```python
from data.integrations.cloud_storage import create_cloud_storage

# S3
s3 = create_cloud_storage("s3", {
    "bucket_name": "mi-bucket",
    "region": "us-east-1",
    "access_key_id": "...",
    "secret_access_key": "..."
})

# Subir archivo
s3.upload_file(
    local_path="/path/to/document.pdf",
    remote_path="documents/invoice_001.pdf",
    metadata={"document_type": "invoice"}
)

# Generar URL presignada
url = s3.generate_presigned_url("documents/invoice_001.pdf", expiration=timedelta(hours=1))
```

### 3. Templates Personalizables 📝

Define templates personalizados para extracción de campos:

```python
from data.integrations.document_templates import TemplateManager, ExtractionRule

manager = TemplateManager("./templates")

# Crear template personalizado
rules = [
    ExtractionRule(
        field_name="invoice_number",
        pattern=r"FACTURA\s*N[o°]?\s*:?\s*(\d+)",
        required=True
    ),
    ExtractionRule(
        field_name="total",
        pattern=r"TOTAL\s*:?\s*\$?\s*([\d,]+\.?\d*)",
        transform="float",
        required=True
    )
]

template = manager.create_template(
    template_id="custom_invoice",
    name="Factura Personalizada",
    document_type="invoice",
    description="Template para facturas de nuestro proveedor",
    rules=rules
)

# Usar template
extracted = manager.extract_with_template(text, "custom_invoice")
```

### 4. API REST 🚀

API completa para procesamiento remoto:

```bash
# Health check
curl http://localhost:5000/health

# Procesar documento
curl -X POST http://localhost:5000/api/v1/process \
  -F "file=@invoice.pdf" \
  -F "archive=true" \
  -F "validate=true"

# Procesar lote
curl -X POST http://localhost:5000/api/v1/process/batch \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"

# Listar templates
curl http://localhost:5000/api/v1/templates?document_type=invoice

# Crear template
curl -X POST http://localhost:5000/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "custom_template",
    "name": "Mi Template",
    "document_type": "invoice",
    "rules": [...]
  }'

# Validar campos
curl -X POST http://localhost:5000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "invoice",
    "extracted_fields": {...}
  }'
```

### 5. Procesamiento Asíncrono con Colas ⚡

Procesamiento en background usando Redis o PostgreSQL:

```python
from data.integrations.document_queue import create_queue, ProcessingJob

# Crear cola Redis
queue = create_queue("redis", {
    "host": "localhost",
    "port": 6379,
    "queue_name": "documents"
})

# Encolar trabajo
job = ProcessingJob(
    job_id=str(uuid.uuid4()),
    file_path="/path/to/document.pdf",
    filename="invoice.pdf",
    priority=10  # Alta prioridad
)

queue.enqueue(job)

# Worker: procesar trabajos
while True:
    job = queue.dequeue()
    if job:
        # Procesar documento
        processed = processor.process_document(job.file_path)
        
        # Actualizar estado
        queue.update_job_status(
            job.job_id,
            "completed",
            {"document_id": processed.document_id}
        )
```

### 6. Análisis de Calidad 📊

Analiza calidad de documentos procesados:

```python
from data.integrations.document_quality import DocumentQualityAnalyzer

analyzer = DocumentQualityAnalyzer()

report = analyzer.analyze_document_quality(
    document_id="DOC-123",
    image_path="/path/to/document.jpg",
    extracted_text="...",
    ocr_confidence=0.85,
    extracted_fields={...},
    document_type="invoice"
)

print(f"Nivel de calidad: {report.quality_level}")
print(f"Score: {report.metrics.overall_score:.2%}")
print(f"Issues: {report.issues}")
print(f"Recomendaciones: {report.recommendations}")
```

**Métricas analizadas:**
- Resolución y DPI de imagen
- Brillo y contraste
- Nitidez
- Nivel de ruido
- Completitud de texto
- Completitud de campos
- Confianza OCR

## Ejemplo Completo Integrado

```python
from data.integrations.document_processor import DocumentProcessor
from data.integrations.document_validator import DocumentValidator
from data.integrations.cloud_storage import create_cloud_storage
from data.integrations.document_quality import DocumentQualityAnalyzer
from data.integrations.document_queue import create_queue

# Configuración
processor = DocumentProcessor({
    "ocr": {"provider": "tesseract"},
    "archive": {"base_path": "./archives"}
})

validator = DocumentValidator()
s3 = create_cloud_storage("s3", {...})
queue = create_queue("redis", {...})
analyzer = DocumentQualityAnalyzer()

# Procesar documento
processed = processor.process_document("invoice.pdf", archive=True)

# Validar
validation = validator.validate_document(
    processed.document_id,
    processed.document_type,
    processed.extracted_fields
)

# Analizar calidad
quality = analyzer.analyze_document_quality(
    processed.document_id,
    processed.file_path,
    processed.extracted_text,
    processed.ocr_confidence,
    processed.extracted_fields,
    processed.document_type
)

# Subir a S3 si calidad es buena
if quality.quality_level.value in ["excellent", "good"]:
    s3.upload_file(
        processed.archive_path,
        f"documents/{processed.document_id}.pdf"
    )

# Resultado final
result = {
    "document": processed.to_dict(),
    "validation": {
        "is_valid": validation.overall_valid,
        "score": validation.validation_score
    },
    "quality": {
        "level": quality.quality_level.value,
        "score": quality.metrics.overall_score
    }
}
```

## Iniciar API REST

```bash
# Configurar variables de entorno
export OCR_PROVIDER=tesseract
export ARCHIVE_PATH=./archives
export DATABASE_URL=postgresql://user:pass@localhost/db
export PORT=5000

# Ejecutar API
python -m data.integrations.document_api_rest
```

## Integración con Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 5000

# Ejecutar API
CMD ["python", "-m", "data.integrations.document_api_rest"]
```

## Próximas Mejoras

- [ ] Integración con Google Drive y Dropbox
- [ ] Machine Learning para mejor clasificación
- [ ] Dashboard web para visualización
- [ ] Reconocimiento de firmas
- [ ] Comparación de documentos
- [ ] Exportación a formatos adicionales (Excel, XML)

## Mejores Prácticas

1. **Validación**: Siempre valida campos extraídos antes de usar
2. **Calidad**: Analiza calidad antes de archivar documentos importantes
3. **Templates**: Crea templates específicos para tus proveedores
4. **Colas**: Usa procesamiento asíncrono para grandes volúmenes
5. **Almacenamiento**: Sube a la nube solo documentos de calidad aceptable
6. **Monitoreo**: Registra métricas de calidad para mejorar el sistema

