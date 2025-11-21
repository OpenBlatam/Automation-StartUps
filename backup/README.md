# Backups y Recuperación

Esta carpeta contiene las configuraciones para el sistema de backup y recuperación de desastres (DR) de la plataforma.

## Componentes

### Velero

[Velero](https://velero.io/) es la herramienta principal para realizar backups de recursos de Kubernetes y volúmenes persistentes.

**Ubicación**: `backup/velero/`

**Archivos**:
- `values.yaml`: Configuración de Helm para el chart de Velero

**Características**:
- Backups de recursos de Kubernetes (Deployments, Services, ConfigMaps, Secrets, etc.)
- Snapshots de volúmenes persistentes
- Soporte multi-cloud (AWS S3, Azure Blob Storage)
- Programación de backups automáticos
- Restauración completa o selectiva

## Configuración

### AWS

La configuración por defecto está orientada a AWS:

```yaml
configuration:
  backupStorageLocation:
    - name: default
      provider: aws
      bucket: biz-datalake-backups
      config:
        region: us-east-1
```

### Azure

Para usar Azure, descomente y configure la sección Azure en `values.yaml`:

```yaml
configuration:
  backupStorageLocation:
    - name: default
      provider: azure
      bucket: velero
      config:
        resourceGroup: rg-biz-automation-dev
        storageAccount: stbizautodev
        subscriptionId: YOUR_SUBSCRIPTION_ID
```

## Instalación

Velero se instala automáticamente mediante Helmfile (ver `helmfile.yaml` en la raíz):

```bash
helmfile apply
```

O manualmente:

```bash
helm install velero vmware-tanzu/velero \
  --namespace backup \
  --create-namespace \
  -f backup/velero/values.yaml
```

## Uso

### Crear un backup manual

```bash
# Backup de un namespace completo
velero backup create backup-namespace-data --include-namespaces data

# Backup de recursos específicos
velero backup create backup-kpis-api \
  --include-namespaces integration \
  --include-resources deployments,services,configmaps
```

### Programar backups automáticos

```bash
# Backup diario a las 2 AM
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces default,data,integration
```

### Restaurar desde un backup

```bash
# Listar backups disponibles
velero backup get

# Restaurar un backup completo
velero restore create restore-from-backup --from-backup backup-namespace-data

# Restaurar recursos específicos
velero restore create restore-selective \
  --from-backup backup-kpis-api \
  --include-resources deployments
```

### Verificar estado

```bash
# Ver backups
velero backup get

# Ver detalles de un backup
velero backup describe backup-namespace-data

# Ver restauraciones
velero restore get
```

## Credenciales

Las credenciales de cloud deben configurarse mediante:

1. **External Secrets Operator**: Ver `security/secrets/` para ejemplos
2. **Secret de Kubernetes**: Configurar en `credentials.secretContents` de `values.yaml`
3. **IAM Roles/Service Principals**: Para AWS (IRSA) o Azure (Workload Identity)

## Mejores Prácticas

1. **Frecuencia**: Realiza backups diarios de namespaces críticos
2. **Retención**: Configura políticas de retención según SLA (30-90 días)
3. **Validación**: Prueba restauraciones periódicamente
4. **Monitoreo**: Integra alertas de Velero en Prometheus
5. **Encriptación**: Habilita encriptación en el bucket/blob storage
6. **Separación de entornos**: Usa buckets separados por entorno (dev/stg/prod)

## Troubleshooting

```bash
# Ver logs de Velero
kubectl logs -n backup deployment/velero

# Verificar conectividad al storage
velero backup-location get

# Verificar plugins
velero plugin get
```

## Referencias

- [Documentación oficial de Velero](https://velero.io/docs/)
- [Velero Helm Chart](https://github.com/vmware-tanzu/helm-charts/tree/main/charts/velero)


