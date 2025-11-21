# 🤖 Automatización de Optimización de Costos en la Nube

## 📊 Descripción

Este DAG automatiza la optimización de costos en cloud providers (AWS, Azure, GCP), proporcionando:

- ✅ Monitoreo diario de costos por servicio
- ✅ Detección automática de recursos huérfanos
- ✅ Recomendaciones automáticas de optimización
- ✅ Alertas cuando costos exceden umbrales
- ✅ Limpieza automática de recursos no utilizados (opcional)
- ✅ Reportes históricos en base de datos

## 🎯 Impacto Esperado

- **Ahorro**: 20-30% en costos de infraestructura
- **Tiempo ahorrado**: 10-15 horas/mes
- **ROI**: 500-800%

## 📋 Requisitos

### Dependencias Python

```bash
pip install boto3  # Para AWS
pip install azure-identity azure-mgmt-costmanagement azure-mgmt-resource  # Para Azure
```

### Variables de Entorno

Configurar en Airflow Variables o External Secrets:

```bash
# Cloud Provider
CLOUD_PROVIDER=aws  # aws, azure, gcp

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx  # O usar IAM roles
AWS_SECRET_ACCESS_KEY=xxx  # O usar IAM roles

# Azure
AZURE_SUBSCRIPTION_ID=xxx

# Umbrales
COST_ALERT_THRESHOLD_PERCENT=120  # 120% del promedio
DAILY_COST_LIMIT=1000  # Límite diario en USD
ORPHAN_RESOURCE_GRACE_PERIOD_DAYS=7  # Días antes de considerar huérfano
SNAPSHOT_RETENTION_DAYS=30  # Días de retención de snapshots
```

### Permisos AWS Requeridos

Para AWS, el rol/usuario necesita los siguientes permisos:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetDimensionValues",
        "ec2:DescribeVolumes",
        "ec2:DescribeSnapshots",
        "ec2:DescribeAddresses",
        "ec2:DescribeInstances",
        "ec2:DescribeSecurityGroups",
        "ec2:DeleteVolume",
        "ec2:DeleteSnapshot",
        "ec2:ReleaseAddress",
        "s3:ListBuckets",
        "s3:ListObjects",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🚀 Uso

### Ejecución Manual

1. Ir a Airflow UI → DAGs → `cloud_cost_optimization`
2. Click en "Trigger DAG"
3. Configurar parámetros:
   - `dry_run`: `true` (solo detectar, no eliminar)
   - `auto_cleanup`: `false` (no eliminar automáticamente)
   - `alert_threshold_percent`: `120`

### Parámetros del DAG

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `dry_run` | boolean | `true` | Solo detectar, no eliminar recursos |
| `auto_cleanup` | boolean | `false` | Eliminar automáticamente recursos huérfanos |
| `alert_threshold_percent` | integer | `120` | Porcentaje sobre promedio para alertar |

### Schedule

Por defecto, el DAG se ejecuta **diariamente a las 9 AM UTC**.

Para cambiar el schedule, editar:

```python
schedule='0 9 * * *',  # Cambiar según necesidad
```

## 📊 Recursos Detectados

El DAG detecta los siguientes tipos de recursos huérfanos:

1. **Volúmenes EBS no asociados** - Volúmenes disponibles sin instancias
2. **Snapshots antiguos** - Snapshots más antiguos que el período de retención
3. **IPs elásticas no utilizadas** - IPs elásticas sin asociación
4. **Instancias detenidas** - Instancias detenidas por más de 7 días
5. **Buckets S3 vacíos** - Buckets sin objetos
6. **Security Groups no utilizados** - Security groups sin instancias asociadas

## 💡 Recomendaciones Generadas

El DAG genera automáticamente recomendaciones de optimización:

1. **Limpieza de recursos huérfanos** - Eliminar recursos no utilizados
2. **Reserved Instances** - Para cargas estables (ahorro ~30%)
3. **Spot Instances** - Para cargas tolerantes a interrupciones (ahorro ~50%)
4. **Lifecycle Policies S3** - Mover datos antiguos a Glacier (ahorro ~50%)

## 📈 Reportes y Métricas

### Base de Datos

Los resultados se guardan en la tabla `cloud_cost_optimization_reports`:

```sql
SELECT 
    report_date,
    provider,
    average_daily_cost,
    orphan_resources_count,
    orphan_resources_savings,
    total_potential_savings
FROM cloud_cost_optimization_reports
ORDER BY report_date DESC
LIMIT 10;
```

### Métricas de Airflow

El DAG registra las siguientes métricas:

- `cloud_cost.daily_average` - Costo promedio diario
- `cloud_cost.total_7d` - Costo total últimos 7 días
- `cloud_cost.orphan_resources_count` - Número de recursos huérfanos
- `cloud_cost.orphan_resources_savings` - Ahorro potencial de recursos huérfanos

### Alertas

El DAG genera alertas cuando:

- El costo diario promedio excede `DAILY_COST_LIMIT`
- Se detectan recursos huérfanos con alto costo potencial

## 🔧 Configuración Avanzada

### Habilitar Limpieza Automática

⚠️ **ADVERTENCIA**: La limpieza automática elimina recursos permanentemente. Usar con precaución.

1. Configurar `auto_cleanup=true` en parámetros del DAG
2. Asegurarse de que los recursos están correctamente etiquetados
3. Revisar recursos antes de habilitar en producción

### Personalizar Umbrales

Editar variables de entorno o parámetros del DAG:

```python
# En el DAG
COST_ALERT_THRESHOLD_PERCENT = 150  # 150% del promedio
DAILY_COST_LIMIT = 2000  # $2000/día
ORPHAN_RESOURCE_GRACE_PERIOD_DAYS = 14  # 14 días
```

### Agregar Nuevos Tipos de Recursos

Para agregar detección de nuevos tipos de recursos:

1. Agregar nuevo `ResourceType` en el enum
2. Implementar método `_detect_*` en `CloudCostOptimizer`
3. Llamar al método en `detect_orphan_resources()`

## 🐛 Troubleshooting

### Error: "boto3 no disponible"

```bash
pip install boto3
```

### Error: "Access Denied"

Verificar permisos IAM del rol/usuario de Airflow.

### Error: "Cost Explorer solo disponible en us-east-1"

El Cost Explorer de AWS solo funciona en la región `us-east-1`. Esto está configurado automáticamente en el código.

### No se detectan recursos huérfanos

- Verificar que los recursos cumplen los criterios (edad, estado)
- Verificar permisos de lectura
- Revisar logs del DAG para errores específicos

## 📚 Referencias

- [AWS Cost Explorer API](https://docs.aws.amazon.com/cost-management/latest/APIReference/API_GetCostAndUsage.html)
- [Azure Cost Management](https://docs.microsoft.com/en-us/azure/cost-management-billing/)
- [Documentación de Airflow](https://airflow.apache.org/docs/)

## 🔄 Próximos Pasos

1. ✅ Implementar limpieza automática con aprobación
2. ✅ Agregar soporte para GCP
3. ✅ Integrar con sistemas de notificación (Slack, PagerDuty)
4. ✅ Dashboard de Grafana para visualización
5. ✅ Análisis predictivo de costos

---

**Última actualización**: 2025-01-12

