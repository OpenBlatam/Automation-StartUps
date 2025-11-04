# Terraform Quick Start Guide

Esta guía te ayuda a empezar rápidamente con Terraform en este proyecto.

## 🚀 Inicio Rápido (Automático)

Usa el script interactivo para configurar todo:

```bash
cd infra/terraform/scripts
./quick-start.sh
```

O usando Make:

```bash
make tf-quick-start
```

Este script te guiará a través de:
1. Selección de proveedor (AWS/Azure)
2. Selección de entorno (dev/stg/prod)
3. Bootstrap del backend (si es necesario)
4. Inicialización de Terraform
5. Validación

## 📋 Inicio Manual (Paso a Paso)

### Paso 1: Bootstrap Backend (Primera vez)

**AWS:**
```bash
cd infra/terraform/scripts
./bootstrap-backend-aws.sh dev us-east-1
```

**Azure:**
```bash
cd infra/terraform/scripts
./bootstrap-backend-azure.sh dev eastus
```

### Paso 2: Configurar Backend

Edita el archivo de configuración correspondiente:
- AWS: `backend-configs/backend-dev-aws.hcl`
- Azure: `backend-configs/backend-dev-azure.hcl`

Actualiza valores necesarios (subscription_id, tenant_id, etc.)

### Paso 3: Inicializar Terraform

```bash
cd infra/terraform
./scripts/init-backend.sh aws dev
# o
./scripts/init-backend.sh azure dev
```

### Paso 4: Configurar Variables

Copia el archivo de ejemplo:
```bash
cp examples/terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars` con tus valores.

### Paso 5: Validar

```bash
make tf-validate-config
```

### Paso 6: Plan y Apply

```bash
terraform plan
terraform apply
```

## 🎯 Comandos Esenciales

### Gestión de Estado
```bash
# Listar recursos
make tf-state-list

# Ver detalles
make tf-state-show RESOURCE=aws_s3_bucket.datalake

# Refrescar estado
make tf-state-refresh

# Backup estado
make tf-backup-state PROVIDER=aws ENV=dev
```

### Validación y Seguridad
```bash
# Validar configuración
make tf-validate-config

# Pre-apply checks
make tf-pre-apply-check ENV=dev

# Health check
make tf-health-check PROVIDER=aws ENV=dev
```

### Limpieza
```bash
# Limpiar cache
make tf-cleanup --cache

# Limpiar todo (excepto estado actual)
make tf-cleanup --all
```

## 🔧 Configuración por Entorno

### Desarrollo
```bash
# Bootstrap
make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1

# Inicializar
make tf-init-backend PROVIDER=aws ENV=dev

# Aplicar
terraform apply -var-file=terraform.tfvars.dev
```

### Producción
```bash
# Bootstrap (si no existe)
make tf-backend-bootstrap-aws ENV=prod REGION=us-east-1

# Inicializar
make tf-init-backend PROVIDER=aws ENV=prod

# Pre-apply checks (obligatorio)
make tf-pre-apply-check ENV=prod

# Plan detallado
terraform plan -out=tfplan

# Revisar plan
terraform show tfplan

# Aplicar
terraform apply tfplan
```

## 📚 Estructura de Archivos

```
infra/terraform/
├── scripts/              # Scripts de utilidad
│   ├── quick-start.sh    # ⭐ Inicio rápido interactivo
│   ├── bootstrap-*.sh    # Bootstrap de backends
│   ├── init-backend.sh   # Inicialización
│   └── ...
├── backend-configs/      # Configuraciones de backend
├── examples/             # Ejemplos y templates
└── *.tf                 # Configuración Terraform
```

## 🆘 Troubleshooting

### Problema: Backend no configurado

**Solución:**
```bash
# Bootstrap primero
make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1

# Luego inicializa
make tf-init-backend PROVIDER=aws ENV=dev
```

### Problema: Estado bloqueado

**Solución:**
```bash
# Verificar locks
# Si es seguro, desbloquear
terraform force-unlock LOCK_ID
```

### Problema: Credenciales inválidas

**AWS:**
```bash
aws configure
aws sts get-caller-identity
```

**Azure:**
```bash
az login
az account show
```

Para más problemas, consulta: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## ✅ Checklist de Primer Uso

- [ ] Bootstrap backend (primera vez)
- [ ] Configurar archivo backend-config
- [ ] Inicializar Terraform
- [ ] Crear terraform.tfvars desde ejemplo
- [ ] Validar configuración
- [ ] Plan para revisar cambios
- [ ] Aplicar cambios
- [ ] Verificar con health check

## 📖 Documentación Adicional

- [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md) - Gestión de estado completa
- [README_STATE.md](./README_STATE.md) - Inicio rápido de estado
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Solución de problemas
- [scripts/README.md](./scripts/README.md) - Documentación de scripts
- [IMPROVEMENTS.md](./IMPROVEMENTS.md) - Resumen de mejoras

## 🎉 ¡Listo!

Una vez completado el setup, puedes:

```bash
# Ver todos los comandos disponibles
make help | grep tf-

# Trabajar con Terraform normalmente
terraform plan
terraform apply

# Gestionar estado
make tf-state-list
make tf-health-check PROVIDER=aws ENV=dev
```

¡Bienvenido a Terraform! 🚀


