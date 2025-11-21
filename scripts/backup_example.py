#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de backups automáticos.

Este script demuestra cómo usar el sistema de backups programáticamente.
"""
import os
import sys
from pathlib import Path

# Agregar path de plugins
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "airflow" / "plugins"))

from backup_manager import BackupManager, BackupConfig, BackupType
from backup_encryption import BackupEncryption
from backup_notifications import SecurityAlertManager, AlertLevel


def example_database_backup():
    """Ejemplo de backup de base de datos."""
    print("📦 Ejemplo: Backup de Base de Datos")
    print("-" * 50)
    
    # Cargar clave de encriptación
    encryption_key = BackupEncryption.load_key_from_env("BACKUP_ENCRYPTION_KEY")
    
    if not encryption_key:
        print("⚠️  BACKUP_ENCRYPTION_KEY no configurado")
        print("   Generando clave temporal para este ejemplo...")
        encryption = BackupEncryption()
        encryption_key = encryption.key
    else:
        encryption = BackupEncryption(encryption_key)
    
    # Configurar backup
    backup_config = BackupConfig(
        backup_type=BackupType.FULL,
        encrypt=True,
        compress=True,
        verify_integrity=True,
        retention_days=30,
        cloud_sync=False,  # Desactivado para ejemplo
    )
    
    # Crear gestor
    manager = BackupManager(
        backup_dir="/tmp/backups_example",
        encryption_key=encryption_key
    )
    
    # Backup de base de datos
    connection_string = os.getenv(
        "BACKUP_DB_CONNECTION",
        "postgresql://user:pass@localhost:5432/dbname"
    )
    
    print(f"Creando backup de: {connection_string[:30]}...")
    result = manager.backup_database(
        connection_string=connection_string,
        db_type="postgresql",
        config=backup_config
    )
    
    print(f"\n✅ Backup completado:")
    print(f"   ID: {result.backup_id}")
    print(f"   Estado: {result.status.value}")
    print(f"   Tamaño: {result.size_bytes / (1024*1024):.2f} MB")
    print(f"   Duración: {result.duration_seconds:.2f}s")
    
    if result.error:
        print(f"   ❌ Error: {result.error}")
    
    return result


def example_file_backup():
    """Ejemplo de backup de archivos."""
    print("\n📁 Ejemplo: Backup de Archivos")
    print("-" * 50)
    
    # Cargar clave de encriptación
    encryption_key = BackupEncryption.load_key_from_env("BACKUP_ENCRYPTION_KEY")
    
    if not encryption_key:
        encryption = BackupEncryption()
        encryption_key = encryption.key
    else:
        encryption = BackupEncryption(encryption_key)
    
    # Crear gestor
    manager = BackupManager(
        backup_dir="/tmp/backups_example",
        encryption_key=encryption_key
    )
    
    # Backup de archivos
    source_paths = [
        "/etc/passwd",  # Ejemplo (ajustar según tu sistema)
        "/tmp"
    ]
    
    # Filtrar solo paths que existen
    existing_paths = [p for p in source_paths if os.path.exists(p)]
    
    if not existing_paths:
        print("⚠️  No se encontraron paths válidos para backup")
        print("   Ajusta source_paths en el script")
        return None
    
    print(f"Creando backup de: {', '.join(existing_paths)}")
    result = manager.backup_files(
        source_paths=existing_paths,
        config=BackupConfig(encrypt=True, compress=True)
    )
    
    print(f"\n✅ Backup completado:")
    print(f"   ID: {result.backup_id}")
    print(f"   Estado: {result.status.value}")
    print(f"   Tamaño: {result.size_bytes / (1024*1024):.2f} MB")
    
    return result


def example_encryption():
    """Ejemplo de encriptación de datos sensibles."""
    print("\n🔒 Ejemplo: Encriptación de Datos Sensibles")
    print("-" * 50)
    
    # Crear instancia de encriptación
    encryption = BackupEncryption()
    
    # Datos sensibles
    sensitive_data = {
        "email": "user@example.com",
        "phone": "1234567890",
        "credit_card": "4532-1234-5678-9010",
        "ssn": "123-45-6789"
    }
    
    print("Datos originales:")
    for key, value in sensitive_data.items():
        print(f"   {key}: {value}")
    
    # Encriptar
    from backup_encryption import SensitiveDataEncryption
    sensitive_encryption = SensitiveDataEncryption(encryption.key)
    
    encrypted = sensitive_encryption.encrypt_dict(
        sensitive_data,
        sensitive_fields=["email", "phone", "credit_card", "ssn"]
    )
    
    print("\nDatos encriptados:")
    for key, value in encrypted.items():
        if isinstance(value, dict) and value.get('encrypted'):
            print(f"   {key}: [ENCRYPTED]")
        else:
            print(f"   {key}: {value}")
    
    # Desencriptar
    decrypted = sensitive_encryption.decrypt_dict(
        encrypted,
        sensitive_fields=["email", "phone", "credit_card", "ssn"]
    )
    
    print("\nDatos desencriptados:")
    for key, value in decrypted.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Encriptación/desencriptación exitosa")


def example_security_alerts():
    """Ejemplo de alertas de seguridad."""
    print("\n🚨 Ejemplo: Alertas de Seguridad")
    print("-" * 50)
    
    security_manager = SecurityAlertManager()
    
    # Alerta de fallo de backup
    print("Enviando alerta de fallo de backup...")
    security_manager.alert_backup_failure(
        backup_id="backup-123",
        error="Connection timeout",
        details={
            "database": "production_db",
            "timestamp": "2025-01-15T10:30:00Z"
        }
    )
    
    # Alerta de acceso no autorizado
    print("Enviando alerta de acceso no autorizado...")
    security_manager.alert_unauthorized_access(
        resource="database",
        user="suspicious_user",
        ip="192.168.1.100"
    )
    
    # Alerta personalizada
    print("Enviando alerta personalizada...")
    security_manager.send_security_alert(
        title="Suspicious Activity Detected",
        message="Multiple failed login attempts detected",
        level=AlertLevel.WARNING,
        details={
            "attempts": 15,
            "time_window": "5 minutes",
            "source_ip": "192.168.1.100"
        }
    )
    
    print("\n✅ Alertas enviadas (verificar Slack/Email si está configurado)")


def example_cloud_sync():
    """Ejemplo de sincronización con nube (requiere configuración)."""
    print("\n☁️  Ejemplo: Sincronización en Nube")
    print("-" * 50)
    
    # Verificar configuración AWS
    aws_bucket = os.getenv("AWS_BACKUP_BUCKET")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not (aws_bucket and aws_access_key and aws_secret_key):
        print("⚠️  Configuración AWS no encontrada")
        print("   Configura AWS_BACKUP_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        return
    
    from backup_manager import CloudSync
    
    cloud_config = {
        "provider": "aws",
        "config": {
            "bucket": aws_bucket,
            "access_key_id": aws_access_key,
            "secret_access_key": aws_secret_key,
            "region": os.getenv("AWS_REGION", "us-east-1")
        }
    }
    
    cloud_sync = CloudSync("aws", cloud_config["config"])
    
    # Listar backups existentes
    print("Listando backups en nube...")
    backups = cloud_sync.list_backups("backups/")
    
    print(f"   Encontrados {len(backups)} backups")
    for backup in backups[:5]:  # Mostrar primeros 5
        print(f"   - {backup['key']} ({backup['size'] / (1024*1024):.2f} MB)")
    
    print("\n✅ Sincronización configurada correctamente")


def main():
    """Ejecuta todos los ejemplos."""
    print("=" * 60)
    print("🚀 Ejemplos de Sistema de Backups Automáticos")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Backup de base de datos
        example_database_backup()
        
        # Ejemplo 2: Backup de archivos
        example_file_backup()
        
        # Ejemplo 3: Encriptación
        example_encryption()
        
        # Ejemplo 4: Alertas de seguridad
        example_security_alerts()
        
        # Ejemplo 5: Sincronización en nube
        example_cloud_sync()
        
        print("\n" + "=" * 60)
        print("✅ Todos los ejemplos completados")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

