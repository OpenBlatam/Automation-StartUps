# Configuración de Entornos

Esta carpeta contiene los archivos de configuración específicos para cada entorno de la plataforma (desarrollo, staging y producción).

## Archivos

```
environments/
├── dev.yaml      # Configuración de desarrollo
├── stg.yaml      # Configuración de staging
└── prod.yaml     # Configuración de producción
```

## Estructura de Configuración

Cada archivo `{env}.yaml` define variables de entorno y parámetros específicos:

### Parámetros Comunes

- **Dominios**: URLs base para servicios (Ingress, APIs)
- **Issuer OIDC**: Configuración de autenticación (OAuth2/OpenID Connect)
- **Bucket/Storage**: Nombres de buckets S3/ADLS por entorno
- **Issuer ACME**: Certificados TLS (Let's Encrypt)
- **Variables de aplicación**: Secrets, conexiones a servicios externos

### Ejemplo de Estructura

```yaml
# environments/dev.yaml
domain:
  base: dev.example.com
  
oauth:
  issuerUrl: https://dev-auth.example.com
  
storage:
  bucket: biz-datalake-dev
  
certificates:
  acmeIssuer: letsencrypt-staging  # Usar staging en dev para evitar rate limits
```

## Uso

### Con Kustomize

Los overlays de Kubernetes (`kubernetes/overlays/{dev,stg,prod}/`) utilizan estas configuraciones para ajustar:

- Hosts de Ingress
- Certificados (`cert-manager.io/cluster-issuer`)
- Labels y annotations por entorno
- Variables de entorno en Deployments

Ejemplo:

```bash
# Aplicar configuración de desarrollo
kubectl apply -k kubernetes/overlays/dev

# Aplicar configuración de producción
kubectl apply -k kubernetes/overlays/prod
```

### Con Helmfile

Helmfile puede referenciar estos archivos para parametrizar charts:

```yaml
# helmfile.yaml
environments:
  - dev: environments/dev.yaml
  - stg: environments/stg.yaml
  - prod: environments/prod.yaml
```

### Con Terraform

Terraform puede leer estos archivos para configurar recursos cloud:

```hcl
# infra/terraform/variables.tf
locals {
  env_config = yamldecode(file("../../environments/${var.environment}.yaml"))
}
```

## Diferencias entre Entornos

### Desarrollo (dev)

- **Dominios**: `*.dev.example.com`
- **Recursos**: Mínimos (1-2 nodos)
- **Certificados**: Let's Encrypt Staging (sin rate limits)
- **Backups**: Menos frecuentes o deshabilitados
- **Debug**: Logging detallado, traces habilitados

### Staging (stg)

- **Dominios**: `*.stg.example.com`
- **Recursos**: Similares a producción pero menores
- **Certificados**: Let's Encrypt Production
- **Backups**: Programados pero no críticos
- **Debug**: Balance entre información y rendimiento

### Producción (prod)

- **Dominios**: `*.example.com` o `*.prod.example.com`
- **Recursos**: Máximos según carga esperada
- **Certificados**: Let's Encrypt Production con alta disponibilidad
- **Backups**: Frecuentes y validados
- **Debug**: Logging estructurado, solo errores/warnings críticos

## Validación

Antes de aplicar cambios, valida la configuración:

```bash
# Validar YAML
yamllint environments/dev.yaml

# Validar con Kustomize
kubectl kustomize kubernetes/overlays/dev --dry-run=client

# Validar con Helmfile
helmfile --environment dev lint
```

## Seguridad

⚠️ **Importante**: Estos archivos NO deben contener secrets reales:

- Usa **External Secrets Operator** para inyectar secrets
- Referencia secrets mediante variables de entorno
- Considera usar **SOPS** o **Sealed Secrets** si necesitas versionar secrets

Ejemplo seguro:

```yaml
# environments/dev.yaml
secrets:
  database:
    secretName: db-credentials  # Referencia a Secret de K8s
    # NO incluir passwords aquí
```

## Migración entre Entornos

Para promover cambios entre entornos:

1. **Desarrollo**: Pruebas iniciales
2. **Staging**: Validación completa
3. **Producción**: Despliegue después de aprobación

Usa CI/CD para automatizar la promoción:

```yaml
# .github/workflows/deploy.yaml
- name: Deploy to Staging
  run: |
    helmfile --environment stg apply
    
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: |
    helmfile --environment prod apply
```

## Variables Dinámicas

Puedes usar variables de entorno o comandos para valores dinámicos:

```yaml
# Usando env vars
domain:
  base: ${ENV_DOMAIN:-dev.example.com}

# En scripts
export ENV=dev
kubectl apply -k kubernetes/overlays/${ENV}
```

## Referencias

- [Kustomize Documentation](https://kustomize.io/)
- [Helmfile Environments](https://helmfile.readthedocs.io/en/latest/#environments)
- [Kubernetes ConfigMaps and Secrets](https://kubernetes.io/docs/concepts/configuration/)


