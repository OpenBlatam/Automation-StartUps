"""
Ejemplos de Uso del Sistema de Procesamiento de Documentos
===========================================================

Este archivo contiene ejemplos prácticos de cómo usar el sistema
de procesamiento de documentos con OCR y clasificación.
"""

import sys
from pathlib import Path

# Agregar ruta de integraciones al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_processor import DocumentProcessor
from document_classifier import DocumentType
from document_webhooks import WebhookManager, WebhookSender
import psycopg2


def example_1_basic_processing():
    """Ejemplo 1: Procesamiento básico de un documento"""
    print("=" * 60)
    print("Ejemplo 1: Procesamiento Básico")
    print("=" * 60)
    
    # Configuración básica con Tesseract
    config = {
        "ocr": {
            "provider": "tesseract",
            "language": "spa+eng"
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    
    # Procesar un documento
    try:
        processed = processor.process_document(
            file_path="example_invoice.pdf",  # Reemplazar con ruta real
            filename="factura_ejemplo.pdf",
            archive=True
        )
        
        print(f"\n✓ Documento procesado exitosamente!")
        print(f"  ID: {processed.document_id}")
        print(f"  Tipo: {processed.document_type}")
        print(f"  Confianza clasificación: {processed.classification_confidence:.2%}")
        print(f"  Confianza OCR: {processed.ocr_confidence:.2%}")
        print(f"  Campos extraídos: {processed.extracted_fields}")
        print(f"  Archivado en: {processed.archive_path}")
        
    except FileNotFoundError:
        print("⚠️  Archivo no encontrado. Reemplaza 'example_invoice.pdf' con una ruta real.")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_batch_processing():
    """Ejemplo 2: Procesamiento en lote"""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Procesamiento en Lote")
    print("=" * 60)
    
    config = {
        "ocr": {
            "provider": "tesseract",
            "language": "spa+eng"
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type_and_date"
        }
    }
    
    processor = DocumentProcessor(config)
    
    # Lista de documentos a procesar
    documents = [
        "invoice1.pdf",
        "contract1.pdf",
        "form1.pdf"
    ]
    
    # Filtrar solo los que existen
    existing_docs = [d for d in documents if Path(d).exists()]
    
    if not existing_docs:
        print("⚠️  No hay documentos para procesar.")
        print("   Crea algunos archivos PDF de ejemplo o ajusta las rutas.")
        return
    
    print(f"\nProcesando {len(existing_docs)} documentos...")
    
    processed_docs = processor.process_batch(existing_docs, archive=True)
    
    print(f"\n✓ Procesados {len(processed_docs)} documentos")
    
    # Exportar resultados
    json_file = processor.export_results(processed_docs, format="json")
    csv_file = processor.export_results(processed_docs, format="csv")
    
    print(f"  Exportado JSON: {json_file}")
    print(f"  Exportado CSV: {csv_file}")


def example_3_google_vision():
    """Ejemplo 3: Usando Google Cloud Vision API"""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Google Cloud Vision API")
    print("=" * 60)
    
    config = {
        "ocr": {
            "provider": "google_vision",
            "api_key": "TU_API_KEY",  # Reemplazar con tu API key
            "project_id": "tu-project-id"  # Opcional
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    
    # Health check
    health = processor.health_check()
    print(f"Estado del sistema: {health['status']}")
    
    if health['status'] == 'healthy':
        print("✓ Google Vision API está disponible")
    else:
        print("✗ Error de configuración. Verifica tu API key.")


def example_4_azure_vision():
    """Ejemplo 4: Usando Azure Computer Vision"""
    print("\n" + "=" * 60)
    print("Ejemplo 4: Azure Computer Vision")
    print("=" * 60)
    
    config = {
        "ocr": {
            "provider": "azure_vision",
            "endpoint": "https://tu-recurso.cognitiveservices.azure.com/",
            "api_key": "TU_API_KEY"  # Reemplazar con tu API key
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    
    health = processor.health_check()
    print(f"Estado del sistema: {health['status']}")


def example_5_database_integration():
    """Ejemplo 5: Integración con base de datos"""
    print("\n" + "=" * 60)
    print("Ejemplo 5: Integración con Base de Datos")
    print("=" * 60)
    
    # Configurar procesador
    config = {
        "ocr": {
            "provider": "tesseract",
            "language": "spa+eng"
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    
    # Conectar a base de datos
    try:
        db_conn = psycopg2.connect(
            "postgresql://usuario:password@localhost/dbname"  # Ajustar
        )
        
        # Procesar documento
        processed = processor.process_document(
            file_path="example_invoice.pdf",
            archive=True
        )
        
        # Guardar en base de datos
        cursor = db_conn.cursor()
        
        cursor.execute("""
            INSERT INTO processed_documents 
            (document_id, original_filename, file_path, file_hash,
             document_type, classification_confidence, extracted_text,
             ocr_confidence, ocr_provider, archive_path, processed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            processed.document_id,
            processed.original_filename,
            processed.file_path,
            processed.file_hash,
            processed.document_type,
            processed.classification_confidence,
            processed.extracted_text,
            processed.ocr_confidence,
            processed.ocr_provider,
            processed.archive_path,
            processed.processed_at
        ))
        
        # Guardar campos extraídos
        for field_name, field_value in processed.extracted_fields.items():
            cursor.execute("""
                INSERT INTO document_extracted_fields
                (document_id, field_name, field_value)
                VALUES (%s, %s, %s)
            """, (processed.document_id, field_name, str(field_value)))
        
        db_conn.commit()
        print("✓ Documento guardado en base de datos")
        
        db_conn.close()
        
    except psycopg2.OperationalError:
        print("⚠️  No se pudo conectar a la base de datos.")
        print("   Ajusta la cadena de conexión o crea la base de datos.")
    except FileNotFoundError:
        print("⚠️  Archivo no encontrado.")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_webhooks():
    """Ejemplo 6: Integración con webhooks (Zapier/Make)"""
    print("\n" + "=" * 60)
    print("Ejemplo 6: Webhooks para Zapier/Make")
    print("=" * 60)
    
    # Configurar procesador
    config = {
        "ocr": {
            "provider": "tesseract",
            "language": "spa+eng"
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    
    # Procesar documento
    try:
        processed = processor.process_document(
            file_path="example_invoice.pdf",
            archive=True
        )
        
        # Enviar webhook
        webhook_url = "https://hooks.zapier.com/hooks/catch/..."  # URL de Zapier/Make
        sender = WebhookSender()
        
        success = sender.send_document_processed(
            webhook_url=webhook_url,
            document=processed.to_dict(),
            secret_token="tu-token-secreto"  # Opcional
        )
        
        if success:
            print("✓ Webhook enviado exitosamente")
        else:
            print("✗ Error enviando webhook")
            
    except FileNotFoundError:
        print("⚠️  Archivo no encontrado.")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_7_webhook_manager():
    """Ejemplo 7: Usar WebhookManager para múltiples webhooks"""
    print("\n" + "=" * 60)
    print("Ejemplo 7: Gestor de Webhooks")
    print("=" * 60)
    
    try:
        db_conn = psycopg2.connect(
            "postgresql://usuario:password@localhost/dbname"  # Ajustar
        )
        
        webhook_manager = WebhookManager(db_conn)
        
        # Registrar webhook para Zapier
        webhook_manager.register_webhook(
            webhook_name="zapier_invoices",
            webhook_url="https://hooks.zapier.com/hooks/catch/...",
            trigger_events=["document_processed", "document_classified"],
            document_types=["invoice"],  # Solo facturas
            secret_token="tu-token-secreto",
            enabled=True
        )
        
        # Registrar webhook para Make
        webhook_manager.register_webhook(
            webhook_name="make_contracts",
            webhook_url="https://hook.integromat.com/...",
            trigger_events=["document_processed"],
            document_types=["contract"],  # Solo contratos
            enabled=True
        )
        
        print("✓ Webhooks registrados")
        
        # Procesar documento y activar webhooks automáticamente
        # (esto se hace en el workflow de Kestra normalmente)
        
        db_conn.close()
        
    except psycopg2.OperationalError:
        print("⚠️  No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"✗ Error: {e}")


def example_8_health_check():
    """Ejemplo 8: Verificar salud del sistema"""
    print("\n" + "=" * 60)
    print("Ejemplo 8: Health Check del Sistema")
    print("=" * 60)
    
    config = {
        "ocr": {
            "provider": "tesseract",
            "language": "spa+eng"
        },
        "archive": {
            "base_path": "./archives",
            "structure": "by_type"
        }
    }
    
    processor = DocumentProcessor(config)
    health = processor.health_check()
    
    print(f"\nEstado General: {health['status'].upper()}")
    print("\nComponentes:")
    
    for component, status in health['components'].items():
        status_icon = "✓" if status.get('available') else "✗"
        print(f"  {status_icon} {component}: {status.get('status', 'unknown')}")
        if 'error' in status:
            print(f"      Error: {status['error']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EJEMPLOS DE PROCESAMIENTO DE DOCUMENTOS")
    print("=" * 60)
    
    # Ejecutar ejemplos
    example_1_basic_processing()
    # example_2_batch_processing()
    # example_3_google_vision()
    # example_4_azure_vision()
    # example_5_database_integration()
    # example_6_webhooks()
    # example_7_webhook_manager()
    example_8_health_check()
    
    print("\n" + "=" * 60)
    print("FIN DE EJEMPLOS")
    print("=" * 60)

