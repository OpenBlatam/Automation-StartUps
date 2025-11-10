# 🛡️ Sistema de Backups Automáticos y Seguridad

Sistema completo para proteger tu negocio con backups automáticos, encriptación, sincronización en la nube y alertas de seguridad.

## ✨ Características Principales

- 🔄 **Backups Automáticos** - Sin intervención manual diaria
- 🔒 **Encriptación AES-256** - Protección de datos sensibles
- ☁️ **Sincronización Multi-Nube** - AWS S3, Azure, GCP
- 🚨 **Alertas de Seguridad** - Notificaciones automáticas
- ✅ **Verificación de Integridad** - Checksums SHA-256
- 🧹 **Limpieza Automática** - Retención configurable

## 🚀 Inicio Rápido

### 1. Configurar el Sistema

```bash
cd scripts
./setup_automated_backups.sh
```

### 2. Editar Configuración

Edita `.env.backups` con tus credenciales:

```bash
# Clave de encriptación (generada automáticamente)
export BACKUP_ENCRYPTION_KEY="..."

# Proveedor de nube
export CLOUD_PROVIDER="aws"

# AWS
export AWS_BACKUP_BUCKET="mi-bucket"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

# Bases de datos
export BACKUP_DB_CONNECTIONS="postgresql://user:pass@host:5432/db"

# Archivos críticos
export BACKUP_CRITICAL_PATHS="/etc,/opt/config"
```

### 3. Cargar Variables en Airflow

```bash
source .env.backups
# O agregar a docker-compose.yml / Kubernetes
```

### 4. ¡Listo!

Los DAGs se ejecutarán automáticamente:
- **Backups diarios**: 2 AM UTC
- **Backups incrementales**: Cada 6 horas
- **Monitoreo de seguridad**: Cada 15 minutos

## 📚 Documentación Completa

Ver [docs/BACKUPS_AUTOMATICOS.md](docs/BACKUPS_AUTOMATICOS.md) para documentación completa.

## 🧪 Ejemplos

Ver [scripts/backup_example.py](scripts/backup_example.py) para ejemplos de uso.

## 🔐 Seguridad

**⚠️ IMPORTANTE**: Guarda la clave de encriptación en un lugar seguro. Sin ella, no podrás desencriptar los backups.

Usa:
- ✅ Kubernetes Secrets
- ✅ HashiCorp Vault
- ✅ AWS Secrets Manager
- ✅ Azure Key Vault

**NUNCA**:
- ❌ Commitear en Git
- ❌ Hardcodear en código
- ❌ Almacenar en texto plano

## 📊 Monitoreo

Los backups se monitorean automáticamente y se envían alertas a:
- Slack (si está configurado)
- Email (para alertas críticas)

## 🆘 Soporte

Para problemas:
1. Revisar logs de Airflow
2. Verificar variables de entorno
3. Consultar [docs/BACKUPS_AUTOMATICOS.md](docs/BACKUPS_AUTOMATICOS.md)

