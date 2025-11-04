# Terraform Infrastructure as Code

Sistema completo de gestión de infraestructura con Terraform, implementando mejores prácticas de la industria.

## 🚀 Inicio Rápido

```bash
# Wizard interactivo (recomendado para primera vez)
make tf-quick-start

# O manualmente:
make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1
make tf-init-backend PROVIDER=aws ENV=dev
terraform plan
terraform apply
```

📖 **[Ver Guía de Inicio Rápido →](./QUICK_START.md)**

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [INDEX.md](./INDEX.md) | 📑 Índice completo de documentación |
| [QUICK_START.md](./QUICK_START.md) | ⭐ Guía de inicio rápido |
| [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md) | Gestión de estado completa |
| [BEST_PRACTICES.md](./BEST_PRACTICES.md) | Mejores prácticas |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Solución de problemas |
| [IMPROVEMENTS.md](./IMPROVEMENTS.md) | Resumen de mejoras |

## ✨ Características

### 🔐 Gestión de Estado
- ✅ Backends remotos (S3/Azure Blob)
- ✅ Bloqueo de estado automático
- ✅ Cifrado habilitado
- ✅ Backups automáticos
- ✅ Separación por entorno

### 🛠️ Automatización
- ✅ 14 scripts de utilidad
- ✅ Wizard de inicio rápido
- ✅ Validación pre-aplicación
- ✅ Health checks
- ✅ Detección de drift

### 🔒 Seguridad
- ✅ Validación de configuración
- ✅ Detección de secrets
- ✅ Checks de seguridad
- ✅ Protección por entorno

### 📊 Operaciones
- ✅ Estimación de costos
- ✅ Exportación de outputs
- ✅ Gestión de estado
- ✅ Limpieza automática

## 📋 Comandos Principales

### Setup
```bash
make tf-backend-bootstrap-aws ENV=dev REGION=us-east-1
make tf-init-backend PROVIDER=aws ENV=dev
make tf-quick-start  # Wizard interactivo
```

### Validación
```bash
make tf-validate-config
make tf-pre-apply-check ENV=dev
make tf-health-check PROVIDER=aws ENV=dev
```

### Estado
```bash
make tf-state-list
make tf-backup-state PROVIDER=aws ENV=dev
make tf-drift-detection PROVIDER=aws ENV=dev
```

### Utilidades
```bash
make tf-export-outputs FORMAT=json
make tf-cost-estimate PROVIDER=aws
make tf-cleanup --cache
```

Ver todos los comandos: `make help | grep tf-`

## 📁 Estructura

```
infra/terraform/
├── 📚 Documentación completa
├── ⚙️ Configuración Terraform
├── 🔐 Backend configs (dev/stg/prod)
├── 🛠️ Scripts de utilidad (14 scripts)
├── 📝 Ejemplos y templates
└── ☁️ Configuración Azure
```

## 🌟 Soporte Multi-Cloud

### AWS
- EKS (Kubernetes)
- VPC Networking
- S3 Data Lake
- IAM y seguridad

### Azure
- AKS (Kubernetes)
- Virtual Network
- ADLS Gen2
- Azure RBAC

## 🎯 Mejores Prácticas Implementadas

- ✅ Estado remoto con cifrado
- ✅ Separación por entorno
- ✅ Validación continua
- ✅ Health checks
- ✅ Backups automáticos
- ✅ Documentación completa

📖 **[Ver Mejores Prácticas Completas →](./BEST_PRACTICES.md)**

## 🆘 Soporte

### Problemas Comunes
📖 **[Troubleshooting Guide →](./TROUBLESHOOTING.md)**

### Health Check
```bash
make tf-health-check PROVIDER=aws ENV=dev
```

### Validación
```bash
make tf-validate-config
```

## 📖 Recursos

- [Documentación Completa](./INDEX.md)
- [Inicio Rápido](./QUICK_START.md)
- [Gestión de Estado](./STATE_MANAGEMENT.md)
- [Mejores Prácticas](./BEST_PRACTICES.md)
- [Scripts](./scripts/README.md)

## 🔗 Enlaces Útiles

- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws)
- [Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm)

## 📊 Estadísticas

- **14 Scripts** de utilidad
- **9 Guías** de documentación
- **18+ Targets** Makefile
- **100% Cobertura** de mejores prácticas

---

**¿Primera vez?** Empieza aquí: [QUICK_START.md](./QUICK_START.md) ⭐
