# Terraform Scripts - Guía Completa

Este directorio contiene todos los scripts de utilidad para trabajar con Terraform.

## 📋 Índice de Scripts

### 🚀 Setup y Bootstrap (4 scripts)

1. **`bootstrap-backend-aws.sh`**
   - Crea S3 bucket y DynamoDB table para backend
   - Habilita versioning y cifrado
   - Configura seguridad apropiada
   ```bash
   ./bootstrap-backend-aws.sh dev us-east-1
   ```

2. **`bootstrap-backend-azure.sh`**
   - Crea Storage Account y Container
   - Habilita soft delete y versioning
   - Configura seguridad
   ```bash
   ./bootstrap-backend-azure.sh dev eastus
   ```

3. **`init-backend.sh`**
   - Inicializa Terraform con backend remoto
   - Detecta automáticamente proveedor y entorno
   ```bash
   ./init-backend.sh aws dev
   ```

4. **`quick-start.sh`**
   - Wizard interactivo completo
   - Guía paso a paso de configuración
   ```bash
   ./quick-start.sh
   ```

### 📦 Gestión de Estado (7 scripts)

5. **`state-management.sh`**
   - Operaciones de estado (list, show, mv, rm, refresh, pull, unlock)
   ```bash
   ./state-management.sh list
   ./state-management.sh show aws_s3_bucket.datalake
   ```

6. **`backup-state.sh`**
   - Backup automático con timestamp
   - Compresión y rotación
   ```bash
   ./backup-state.sh aws dev
   ```

7. **`compare-states.sh`**
   - Compara estado actual vs backup
   - Identifica diferencias
   ```bash
   ./compare-states.sh backups/terraform-state-aws-dev-20240101.backup
   ```

8. **`migrate-backend.sh`**
   - Migra entre backends (local↔remote, remote↔remote)
   - Backup automático
   ```bash
   ./migrate-backend.sh local remote aws dev
   ```

9. **`rollback.sh`**
   - Rollback desde backup
   - Confirmaciones de seguridad
   ```bash
   ./rollback.sh backups/terraform-state-aws-dev-20240101.backup
   ```

10. **`lock-state.sh` / `unlock-state.sh`**
    - Bloqueo manual para mantenimiento
    - Previene applies accidentales
    ```bash
    ./lock-state.sh "Maintenance window"
    ./unlock-state.sh
    ```

### ✅ Validación y Seguridad (5 scripts)

11. **`validate-terraform.sh`**
    - Validación completa (sintaxis, formato, seguridad)
    ```bash
    ./validate-terraform.sh
    ```

12. **`pre-apply-check.sh`**
    - Checks de seguridad pre-aplicación
    - Verifica producción, backend, estado
    ```bash
    ./pre-apply-check.sh prod
    ```

13. **`health-check.sh`**
    - Health check de infraestructura
    - Verifica estado, drift, credenciales
    ```bash
    ./health-check.sh aws dev
    ```

14. **`audit-security.sh`**
    - Auditoría de seguridad
    - Detecta secrets, verifica cifrado, IAM
    ```bash
    ./audit-security.sh
    ```

15. **`drift-detection.sh`**
    - Detecta configuración drift
    - Resumen de cambios
    ```bash
    ./drift-detection.sh aws dev
    ```

### 🔄 Operaciones y Monitoreo (6 scripts)

16. **`monitor-drift.sh`**
    - Monitoreo continuo de drift
    - Ejecución periódica configurable
    ```bash
    ./monitor-drift.sh aws dev 60  # Cada 60 minutos
    ```

17. **`resource-inventory.sh`**
    - Inventario completo de recursos
    - Formatos: json, yaml, csv, table
    ```bash
    ./resource-inventory.sh aws json
    ```

18. **`dependency-graph.sh`**
    - Grafo de dependencias
    - Formatos: dot, json, list
    ```bash
    ./dependency-graph.sh dot > graph.dot
    dot -Tsvg graph.dot > graph.svg
    ```

19. **`export-outputs.sh`**
    - Exporta outputs en múltiples formatos
    - json, yaml, env, tfvars
    ```bash
    ./export-outputs.sh json outputs.json
    ```

20. **`generate-plan-report.sh`**
    - Genera reporte HTML del plan
    - Visualización de cambios
    ```bash
    terraform plan -out=tfplan
    ./generate-plan-report.sh tfplan
    ```

21. **`test-infrastructure.sh`**
    - Tests de infraestructura post-deployment
    - Valida estado, outputs, drift
    ```bash
    ./test-infrastructure.sh aws dev
    ```

### 🛠️ Utilidades Avanzadas (9 scripts)

22. **`cost-estimate.sh`**
    - Estimación de costos aproximados
    - Soporte AWS y Azure
    ```bash
    ./cost-estimate.sh aws
    ```

23. **`cleanup.sh`**
    - Limpieza de workspace
    - Cache, backups, archivos temporales
    ```bash
    ./cleanup.sh --cache
    ./cleanup.sh --all
    ```

24. **`auto-document.sh`**
    - Auto-genera documentación desde código
    - Extrae variables, outputs, recursos
    ```bash
    ./auto-document.sh AUTO_DOC.md
    ```

25. **`check-dependencies.sh`**
    - Verifica todas las dependencias
    - Terraform, AWS/Azure CLI, credenciales
    ```bash
    ./check-dependencies.sh
    ```

26. **`version-check.sh`**
    - Verifica versiones de Terraform y providers
    - Sugiere actualizaciones
    ```bash
    ./version-check.sh
    ```

27. **`summary.sh`**
    - Resumen completo de infraestructura
    - Estado, recursos, outputs, drift
    ```bash
    ./summary.sh aws
    ```

28. **`validate-modules.sh`**
    - Valida módulos de Terraform
    - Checks de estructura y sintaxis
    ```bash
    ./validate-modules.sh modules
    ```

29. **`export-to-terragrunt.sh`**
    - Convierte configuración a Terragrunt
    - Estructura DRY para múltiples entornos
    ```bash
    ./export-to-terragrunt.sh terragrunt-config
    ```

## 🎯 Flujos de Trabajo por Escenario

### Setup Inicial
```bash
./quick-start.sh
# O paso a paso:
./bootstrap-backend-aws.sh dev us-east-1
./init-backend.sh aws dev
```

### Desarrollo Diario
```bash
./check-dependencies.sh
./validate-terraform.sh
./pre-apply-check.sh dev
terraform plan
terraform apply
./test-infrastructure.sh aws dev
```

### Producción
```bash
./lock-state.sh "Deployment"
./backup-state.sh aws prod
./pre-apply-check.sh prod
terraform plan -out=tfplan
./generate-plan-report.sh tfplan
terraform apply tfplan
./health-check.sh aws prod
./unlock-state.sh
```

### Monitoreo
```bash
./summary.sh aws
./drift-detection.sh aws dev
./resource-inventory.sh aws json
./cost-estimate.sh aws
```

### Mantenimiento
```bash
./version-check.sh
./validate-modules.sh modules
./audit-security.sh
./auto-document.sh
```

## 📊 Estadísticas

- **28 Scripts** totales
- **100% Cobertura** de operaciones comunes
- **Integración Makefile** completa
- **Documentación** exhaustiva

## 🔗 Integración con Makefile

Todos los scripts están disponibles vía Makefile:

```bash
make help | grep tf-
```

## 📚 Documentación Adicional

- [INDEX.md](../INDEX.md) - Índice completo
- [QUICK_START.md](../QUICK_START.md) - Inicio rápido
- [BEST_PRACTICES.md](../BEST_PRACTICES.md) - Mejores prácticas

## ✅ Mejores Prácticas

1. **Siempre verificar dependencias:**
   ```bash
   ./check-dependencies.sh
   ```

2. **Validar antes de aplicar:**
   ```bash
   ./validate-terraform.sh
   ./pre-apply-check.sh $ENV
   ```

3. **Backup en producción:**
   ```bash
   ./backup-state.sh aws prod
   ```

4. **Monitorear regularmente:**
   ```bash
   ./summary.sh aws
   ./drift-detection.sh aws dev
   ```

---

**Todos los scripts son ejecutables y están listos para usar.** 🚀
