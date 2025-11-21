"""
Ejemplo Completo del Pipeline Ultimate
======================================

Demuestra el uso completo de todas las funcionalidades del sistema.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_processor import DocumentProcessor
from document_optimizer import DocumentOptimizer
from document_validator import DocumentValidator
from document_quality import DocumentQualityAnalyzer
from document_ml import MLDocumentClassifier, DocumentEmbedder
from document_ner import NamedEntityRecognizer
from document_summarization import DocumentSummarizer
from document_sentiment import SentimentAnalyzer
from document_table_extractor import TableExtractor
from document_translation import DocumentTranslator
from document_compression import DocumentCompressor
from document_signature import SignatureDetector
from document_comparison import DocumentComparator
from document_search import DocumentSearcher
from document_anomaly_detection import AnomalyDetector
from document_business_rules import BusinessRulesEngine, BusinessRule, RuleAction
from document_collaboration import CollaborationManager, ReviewStatus
from document_versioning import DocumentVersionManager
from document_audit import AuditLogger, AuditAction
from document_notifications import NotificationService, NotificationChannel
from document_backup import DocumentBackupManager
from document_security import DocumentSecurity
from document_vector_db import create_vector_db
from document_indexing import DocumentIndexer
from document_monitoring import SystemMonitor, AlertLevel
from document_rate_limiter import AdaptiveRateLimiter, RateLimitConfig
from cloud_storage import create_cloud_storage
import psycopg2
import time


def complete_enterprise_pipeline(file_path: str, user_email: str = "user@example.com"):
    """
    Pipeline completo enterprise que integra todas las funcionalidades
    """
    print("=" * 80)
    print("🚀 PIPELINE ULTIMATE ENTERPRISE - PROCESAMIENTO COMPLETO")
    print("=" * 80)
    
    # ============================================
    # 1. CONFIGURACIÓN INICIAL
    # ============================================
    print("\n📋 Paso 1: Configurando componentes...")
    
    # Base de datos
    db_conn = psycopg2.connect("postgresql://user:pass@localhost/db")
    
    # Procesador con cache
    processor_config = {
        "ocr": {"provider": "tesseract", "language": "spa+eng"},
        "archive": {"base_path": "./archives", "structure": "by_type_and_date"},
        "cache": {"enabled": True, "cache_dir": "./.cache", "ttl": 86400}
    }
    processor = DocumentProcessor(processor_config)
    
    # Optimizador
    optimizer = DocumentOptimizer()
    
    # Validador
    validator = DocumentValidator()
    
    # Analizadores
    quality_analyzer = DocumentQualityAnalyzer()
    ml_classifier = MLDocumentClassifier()
    embedder = DocumentEmbedder()
    ner = NamedEntityRecognizer()
    summarizer = DocumentSummarizer()
    sentiment_analyzer = SentimentAnalyzer()
    table_extractor = TableExtractor()
    translator = DocumentTranslator()
    compressor = DocumentCompressor()
    signature_detector = SignatureDetector()
    comparator = DocumentComparator()
    searcher = DocumentSearcher()
    anomaly_detector = AnomalyDetector(db_conn)
    
    # Gestores
    rules_engine = BusinessRulesEngine(db_conn)
    collab_manager = CollaborationManager(db_conn)
    version_manager = DocumentVersionManager(db_conn)
    audit = AuditLogger(db_conn)
    notifier = NotificationService({
        "email_webhook_url": "https://hooks.zapier.com/...",
        "slack_webhook_url": "https://hooks.slack.com/..."
    })
    backup_manager = DocumentBackupManager()
    security = DocumentSecurity()
    
    # Infraestructura
    rate_limiter = AdaptiveRateLimiter(RateLimitConfig(100, 60))
    monitor = SystemMonitor()
    s3 = create_cloud_storage("s3", {
        "bucket_name": "my-documents",
        "region": "us-east-1"
    })
    vector_db = create_vector_db("pinecone", {
        "api_key": "...",
        "index_name": "documents"
    })
    indexer = DocumentIndexer({
        "provider": "elasticsearch",
        "hosts": ["localhost:9200"],
        "index_name": "documents"
    })
    
    # ============================================
    # 2. PROCESAMIENTO
    # ============================================
    print("\n📄 Paso 2: Procesando documento...")
    
    # Rate limiting
    if not rate_limiter.wait_and_acquire():
        print("❌ Rate limit alcanzado")
        return None
    
    start_time = time.time()
    
    # Auditoría: inicio
    audit.log_action(
        document_id="pending",
        action=AuditAction.PROCESS,
        user_email=user_email,
        details={"file_path": file_path}
    )
    
    try:
        # Optimizar imagen
        print("  ⚙️  Optimizando imagen...")
        optimized_path = optimizer.optimize_for_ocr(
            file_path,
            options={
                "enhance_brightness": True,
                "enhance_contrast": True,
                "denoise": True,
                "deskew": True,
                "target_dpi": 300
            }
        )
        
        # Procesar con cache
        print("  🔍 Extrayendo texto y clasificando...")
        processed = processor.process_document(
            optimized_path,
            archive=True,
            use_cache=True
        )
        
        print(f"  ✅ Tipo detectado: {processed.document_type}")
        print(f"  ✅ Confianza: {processed.classification_confidence:.2%}")
        
        # ============================================
        # 3. ANÁLISIS AVANZADO
        # ============================================
        print("\n🧠 Paso 3: Análisis avanzado...")
        
        # ML Classification
        print("  🤖 Clasificación ML...")
        ml_result = ml_classifier.classify_with_ml(processed.extracted_text)
        
        # Generar embedding
        print("  📊 Generando embedding...")
        embedding = embedder.generate_embedding(processed.extracted_text)
        
        # NER
        print("  🏷️  Extrayendo entidades...")
        entities = ner.extract_entities(processed.extracted_text)
        entity_summary = ner.get_entity_summary(entities)
        
        # Análisis de sentimiento
        print("  😊 Analizando sentimiento...")
        sentiment = sentiment_analyzer.analyze_sentiment(processed.extracted_text)
        
        # Generar resumen
        print("  📝 Generando resumen...")
        summary = summarizer.generate_summary(processed.extracted_text, max_sentences=5)
        
        # Extraer tablas
        print("  📊 Extrayendo tablas...")
        tables = table_extractor.extract_tables_from_image(optimized_path)
        
        # Detectar firmas
        print("  ✍️  Detectando firmas...")
        signature_analysis = signature_detector.validate_signature(
            processed.document_id,
            optimized_path
        )
        
        # ============================================
        # 4. VALIDACIÓN Y CALIDAD
        # ============================================
        print("\n✔️  Paso 4: Validación y calidad...")
        
        # Validar
        validation = validator.validate_document(
            processed.document_id,
            processed.document_type,
            processed.extracted_fields
        )
        print(f"  ✅ Validación: {'Válido' if validation.overall_valid else 'Con errores'}")
        print(f"  ✅ Score: {validation.validation_score:.2%}")
        
        # Analizar calidad
        quality = quality_analyzer.analyze_document_quality(
            processed.document_id,
            optimized_path,
            processed.extracted_text,
            processed.ocr_confidence,
            processed.extracted_fields,
            processed.document_type
        )
        print(f"  ✅ Calidad: {quality.quality_level.value}")
        print(f"  ✅ Score: {quality.metrics.overall_score:.2%}")
        
        # Detectar anomalías
        print("  🔍 Detectando anomalías...")
        anomalies = anomaly_detector.detect_anomalies(processed.to_dict())
        if anomalies:
            print(f"  ⚠️  {len(anomalies)} anomalía(s) detectada(s)")
            for anomaly in anomalies:
                print(f"     - {anomaly.anomaly_type.value}: {anomaly.description}")
        
        # ============================================
        # 5. REGLAS DE NEGOCIO
        # ============================================
        print("\n📜 Paso 5: Evaluando reglas de negocio...")
        
        rule_results = rules_engine.evaluate_document(processed.to_dict())
        actions = rules_engine.execute_actions(processed.to_dict(), rule_results)
        print(f"  ✅ {actions['total_rules_matched']} regla(s) aplicada(s)")
        
        # ============================================
        # 6. VERSIONADO Y COLABORACIÓN
        # ============================================
        print("\n📚 Paso 6: Versionado y colaboración...")
        
        # Crear versión
        version = version_manager.create_version(
            processed.document_id,
            processed.to_dict(),
            created_by=user_email
        )
        print(f"  ✅ Versión {version.version} creada")
        
        # Crear revisión si es necesario
        if quality.quality_level.value in ["poor", "unacceptable"]:
            review = collab_manager.create_review(
                processed.document_id,
                reviewer_id="supervisor",
                reviewer_email="supervisor@example.com"
            )
            print(f"  ✅ Revisión creada: {review.review_id}")
        
        # ============================================
        # 7. POST-PROCESAMIENTO
        # ============================================
        print("\n💾 Paso 7: Post-procesamiento...")
        
        # Comprimir si es necesario
        if Path(processed.archive_path).stat().st_size > 5 * 1024 * 1024:
            print("  🗜️  Comprimiendo documento...")
            compressed_path = compressor.compress_pdf(
                processed.archive_path,
                quality="medium"
            )
            processed.archive_path = compressed_path
        
        # Redactar datos sensibles si es necesario
        if processed.document_type == "form":
            print("  🔒 Redactando datos sensibles...")
            redacted_text = security.redact_sensitive_data(processed.extracted_text)
        
        # Subir a S3 si calidad es buena
        if quality.quality_level.value in ["excellent", "good"]:
            print("  ☁️  Subiendo a S3...")
            s3.upload_file(
                processed.archive_path,
                f"documents/{processed.document_id}.pdf",
                metadata={
                    "document_type": processed.document_type,
                    "quality_score": quality.metrics.overall_score
                }
            )
        
        # Indexar para búsqueda
        print("  📇 Indexando para búsqueda...")
        indexer.index_document(processed.to_dict())
        
        # Indexar en vector DB
        if embedding is not None:
            print("  🔍 Indexando en vector DB...")
            vector_db.upsert_document(
                processed.document_id,
                embedding,
                metadata={
                    "document_type": processed.document_type,
                    "quality_score": quality.metrics.overall_score
                }
            )
        
        # Backup
        print("  💾 Creando backup...")
        backup_path = backup_manager.create_backup(
            [processed.to_dict()],
            include_files=True
        )
        
        # ============================================
        # 8. NOTIFICACIONES Y MÉTRICAS
        # ============================================
        print("\n📧 Paso 8: Notificaciones y métricas...")
        
        # Notificar según resultado
        if validation.overall_valid and quality.quality_level.value in ["excellent", "good"]:
            notifier.notify_document_processed(
                processed.to_dict(),
                [user_email],
                NotificationChannel.EMAIL
            )
            print("  ✅ Notificación de éxito enviada")
        else:
            if not validation.overall_valid:
                notifier.notify_validation_errors(
                    processed.document_id,
                    validation.warnings,
                    [user_email]
                )
            if quality.quality_level.value in ["poor", "unacceptable"]:
                notifier.notify_quality_issues(
                    processed.document_id,
                    {"issues": quality.issues},
                    [user_email]
                )
            print("  ⚠️  Notificaciones de advertencia enviadas")
        
        # Registrar métricas
        processing_time = time.time() - start_time
        rate_limiter.record_performance(processing_time, True)
        monitor.record_metric("processing_time", processing_time)
        monitor.record_metric("documents_processed", 1)
        monitor.record_metric("success_rate", 1.0)
        
        # Auditoría: éxito
        audit.log_action(
            document_id=processed.document_id,
            action=AuditAction.PROCESS,
            user_email=user_email,
            result="success",
            details={
                "processing_time": processing_time,
                "document_type": processed.document_type,
                "quality_score": quality.metrics.overall_score,
                "validation_score": validation.validation_score
            }
        )
        
        # ============================================
        # 9. RESULTADO FINAL
        # ============================================
        print("\n" + "=" * 80)
        print("✅ PROCESAMIENTO COMPLETO")
        print("=" * 80)
        
        result = {
            "document": processed.to_dict(),
            "ml_classification": {
                "predicted_type": ml_result.get("predicted_type"),
                "confidence": ml_result.get("confidence")
            },
            "entities": entity_summary,
            "sentiment": {
                "label": sentiment.label.value,
                "score": sentiment.score
            },
            "summary": summary.summary_text,
            "tables_found": len(tables),
            "signatures_found": signature_analysis.signatures_found,
            "validation": {
                "is_valid": validation.overall_valid,
                "score": validation.validation_score
            },
            "quality": {
                "level": quality.quality_level.value,
                "score": quality.metrics.overall_score
            },
            "anomalies": [a.anomaly_type.value for a in anomalies],
            "rule_actions": actions,
            "version": version.version,
            "processing_time": processing_time
        }
        
        print(f"\n📊 Resumen:")
        print(f"   • Tipo: {processed.document_type}")
        print(f"   • Confianza: {processed.classification_confidence:.2%}")
        print(f"   • Calidad: {quality.quality_level.value} ({quality.metrics.overall_score:.2%})")
        print(f"   • Validación: {'✅ Válido' if validation.overall_valid else '❌ Errores'}")
        print(f"   • Entidades: {entity_summary.get('total_entities', 0)}")
        print(f"   • Tablas: {len(tables)}")
        print(f"   • Firmas: {signature_analysis.signatures_found}")
        print(f"   • Anomalías: {len(anomalies)}")
        print(f"   • Tiempo: {processing_time:.2f}s")
        
        return result
    
    except Exception as e:
        # Auditoría: error
        audit.log_action(
            document_id="unknown",
            action=AuditAction.PROCESS,
            user_email=user_email,
            result="error",
            error_message=str(e)
        )
        
        rate_limiter.record_performance(time.time() - start_time, False)
        monitor.create_alert(
            AlertLevel.ERROR,
            f"Error procesando documento: {e}",
            "pipeline"
        )
        
        raise


if __name__ == "__main__":
    # Ejemplo de uso
    result = complete_enterprise_pipeline(
        file_path="example_invoice.pdf",
        user_email="user@example.com"
    )
    
    if result:
        print("\n🎉 ¡Pipeline completado exitosamente!")

