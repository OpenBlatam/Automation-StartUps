# Quick Start - Sistema de Procesamiento de Documentos

## 🚀 Instalación Rápida

### 1. Instalar Dependencias del Sistema

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    python3-pip

# macOS
brew install tesseract tesseract-lang poppler
```

### 2. Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

```bash
# Crear base de datos
createdb document_processing

# Ejecutar schemas
psql -U postgres -d document_processing -f ../db/document_processing_schema.sql
psql -U postgres -d document_processing -f ../db/document_versioning_schema.sql
psql -U postgres -d document_processing -f ../db/document_collaboration_schema.sql
```

### 4. Procesar Tu Primer Documento

```python
from data.integrations.document_processor import DocumentProcessor

# Configuración básica
config = {
    "ocr": {
        "provider": "tesseract",
        "language": "spa+eng"
    },
    "archive": {
        "base_path": "./archives",
        "structure": "by_type"
    },
    "cache": {
        "enabled": True,
        "cache_dir": "./.cache"
    }
}

# Crear procesador
processor = DocumentProcessor(config)

# Procesar documento
processed = processor.process_document(
    file_path="mi_factura.pdf",
    filename="factura_001.pdf",
    archive=True
)

# Ver resultados
print(f"Tipo: {processed.document_type}")
print(f"Confianza: {processed.classification_confidence:.2%}")
print(f"Campos extraídos: {processed.extracted_fields}")
```

## 📋 Ejemplos Comunes

### Procesar Factura
```python
processed = processor.process_document("factura.pdf")

if processed.document_type == "invoice":
    print(f"Número: {processed.extracted_fields.get('invoice_number')}")
    print(f"Total: {processed.extracted_fields.get('total')}")
    print(f"Cliente: {processed.extracted_fields.get('customer_name')}")
```

### Validar Documento
```python
from data.integrations.document_validator import DocumentValidator

validator = DocumentValidator()
validation = validator.validate_document(
    processed.document_id,
    processed.document_type,
    processed.extracted_fields
)

if validation.overall_valid:
    print("✅ Documento válido")
else:
    print(f"❌ Errores: {validation.warnings}")
```

### Buscar Documentos
```python
from data.integrations.document_search import DocumentSearcher

searcher = DocumentSearcher()
results = searcher.search_by_field(
    "invoice_number",
    "001",
    documents
)

for result in results:
    print(f"Encontrado: {result.document_id}")
```

### Exportar Resultados
```python
from data.integrations.document_export import DocumentExporter

exporter = DocumentExporter()
exporter.export_to_excel([processed.to_dict()], "resultados.xlsx")
exporter.export_to_html_dashboard([processed.to_dict()], "dashboard.html")
```

## 🔧 Configuración Avanzada

### Usar Google Vision API
```python
config = {
    "ocr": {
        "provider": "google_vision",
        "api_key": "TU_API_KEY",
        "project_id": "tu-project-id"
    }
}
```

### Habilitar Cache
```python
config = {
    "cache": {
        "enabled": True,
        "cache_dir": "./.cache",
        "ttl": 86400  # 24 horas
    }
}
```

### Configurar Archivado
```python
config = {
    "archive": {
        "base_path": "/data/documents/archive",
        "structure": "by_type_and_date"  # by_type, by_date, by_type_and_date, flat
    }
}
```

## 🌐 API REST

### Iniciar Servidor
```bash
export DATABASE_URL=postgresql://user:pass@localhost/db
export OCR_PROVIDER=tesseract
export PORT=5000

python -m data.integrations.document_api_rest
```

### Procesar vía API
```bash
curl -X POST http://localhost:5000/api/v1/process \
  -F "file=@factura.pdf" \
  -F "archive=true" \
  -F "validate=true"
```

## 📊 Dashboard

```python
from data.integrations.document_dashboard import DashboardGenerator
from data.integrations.document_analytics import DocumentAnalytics

analytics = DocumentAnalytics(db_conn)
dashboard = DashboardGenerator()

dashboard.generate_dashboard(
    analytics_data=analytics.get_performance_report(),
    monitoring_data=monitor.get_health_status(),
    output_path="dashboard.html"
)
```

## 🎯 Casos de Uso Comunes

### 1. Procesar Facturas Automáticamente
```python
# Procesar lote
files = ["factura1.pdf", "factura2.pdf", "factura3.pdf"]
processed = processor.process_batch(files, archive=True)

# Exportar a Excel
exporter.export_to_excel(processed, "facturas_procesadas.xlsx")
```

### 2. Validar y Notificar
```python
validation = validator.validate_document(...)

if not validation.overall_valid:
    notifier.notify_validation_errors(
        document_id,
        validation.warnings,
        ["admin@example.com"]
    )
```

### 3. Buscar y Comparar
```python
# Buscar facturas similares
similar = comparator.find_similar_documents(
    query_document,
    document_list,
    min_similarity=0.8
)

# Detectar duplicados
duplicates = comparator.find_duplicates(documents, threshold=0.95)
```

## 🆘 Troubleshooting

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

### Error: No se puede conectar a BD
```bash
# Verificar conexión
psql -U usuario -d document_processing -c "SELECT 1"

# Verificar variables de entorno
echo $DATABASE_URL
```

## 📚 Documentación Completa

- [Guía Principal](README_DOCUMENT_PROCESSING.md)
- [Mejoras Avanzadas](README_IMPROVEMENTS.md)
- [Índice Completo](INDEX_COMPLETE.md)

## ✅ Checklist de Instalación

- [ ] Dependencias del sistema instaladas
- [ ] Dependencias Python instaladas
- [ ] Base de datos configurada
- [ ] Schemas ejecutados
- [ ] Primer documento procesado exitosamente
- [ ] API REST funcionando (opcional)
- [ ] Dashboard generado (opcional)

**¡Sistema listo para usar!** 🎉

