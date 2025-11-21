# ❓ Preguntas Frecuentes (FAQ)

> Respuestas a las preguntas más comunes sobre el uso de la plataforma

## 🚀 Inicio y Configuración

### ¿Cuánto tiempo toma instalar la plataforma completa?

La instalación completa puede tomar entre 30-60 minutos dependiendo de:
- Velocidad de tu conexión a internet
- Tamaño del cluster de Kubernetes
- Configuración de cloud provider

El despliegue inicial de componentes puede tomar 15-20 minutos adicionales.

### ¿Puedo usar esta plataforma localmente?

Sí, puedes usar:
- **minikube** para un cluster local
- **kind** (Kubernetes in Docker)
- **Docker Desktop** con Kubernetes habilitado

Consulta [Instalación](./../01-inicio-rapido/instalacion.md) para más detalles.

### ¿Qué cloud providers son compatibles?

La plataforma es compatible con:
- **AWS** (EKS)
- **Azure** (AKS)
- **GCP** (GKE)
- **OpenShift**
- Clusters on-premise

## 💰 Costos

### ¿Cuánto cuesta ejecutar esta plataforma?

Los costos dependen de:
- Tamaño del cluster de Kubernetes
- Uso de almacenamiento
- Tráfico de red
- Servicios cloud adicionales (S3, RDS, etc.)

Para un setup pequeño (desarrollo):
- ~$50-100/mes en AWS
- ~$40-80/mes en Azure

Para producción:
- ~$500-2000/mes dependiendo del uso

### ¿Hay componentes con licencias comerciales?

La mayoría de componentes son open-source. Algunas integraciones opcionales pueden requerir licencias:
- **UiPath** (si se integra)
- **ServiceNow** (si se integra)
- Algunos plugins premium de n8n

## 🔧 Uso y Funcionalidad

### ¿Qué diferencia hay entre Kestra, n8n y Airflow?

- **Kestra**: Workflows declarativos en YAML, ideal para pipelines de datos y automatizaciones simples
- **n8n**: Workflows visuales sin código, perfecto para integraciones y automatizaciones de negocio
- **Airflow**: Pipelines ETL enterprise-grade con Python, ideal para procesamiento de datos complejo

### ¿Puedo usar múltiples componentes a la vez?

Sí, todos los componentes están diseñados para trabajar juntos. Por ejemplo:
- Kestra puede invocar workflows de n8n
- Airflow puede usar modelos de MLflow
- Todos comparten la misma infraestructura de Kubernetes

### ¿Cómo elijo qué componente usar para mi caso de uso?

Consulta la [Tabla de Decisiones](./../01-inicio-rapido/README.md#-qué-componente-usar) o las [Guías de Componentes](./../02-componentes/).

## 🔐 Seguridad

### ¿Cómo gestiono secretos y contraseñas?

La plataforma usa **External Secrets Operator** para gestionar secretos de forma segura. Los secretos se almacenan en:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

Nunca se almacenan en el código o en repositorios.

### ¿Es seguro para producción?

Sí, la plataforma incluye:
- RBAC (Role-Based Access Control)
- Network Policies
- TLS/SSL por defecto
- Auditoría y logging
- External Secrets

Consulta [Seguridad](./../05-seguridad/) para más detalles.

## 📊 Datos y Almacenamiento

### ¿Dónde se almacenan los datos?

Los datos se almacenan en:
- **PersistentVolumes** en Kubernetes para datos de aplicaciones
- **Data Lake** (S3/ADLS) para datos históricos
- **Bases de datos** (PostgreSQL, MongoDB) para datos estructurados

### ¿Cómo hago backup de mis datos?

La plataforma incluye:
- Backups automáticos de bases de datos
- Snapshots de PersistentVolumes
- Replicación de datos críticos

Consulta [Backups](./../04-operacion/backups.md) para más información.

## 🐛 Problemas y Troubleshooting

### Mi pod está en CrashLoopBackOff, ¿qué hago?

1. Revisa los logs: `kubectl logs <pod-name> -n <namespace> --previous`
2. Verifica la configuración
3. Revisa los secretos y ConfigMaps
4. Consulta [Troubleshooting](./../04-operacion/troubleshooting.md)

### No puedo acceder a los dashboards, ¿por qué?

Verifica:
1. Que los pods estén corriendo: `kubectl get pods -n <namespace>`
2. Que el Ingress esté configurado: `kubectl get ingress -A`
3. Que el DNS apunte correctamente
4. Que los certificados TLS sean válidos

### ¿Cómo veo los logs de mis workflows?

- **Kestra**: UI de Kestra → Executions → Selecciona ejecución
- **n8n**: UI de n8n → Workflow → Ver ejecuciones
- **Airflow**: UI de Airflow → DAGs → Ver logs de tareas

También puedes usar: `kubectl logs <pod-name> -n <namespace>`

## 🔄 Actualizaciones y Mantenimiento

### ¿Cómo actualizo los componentes?

```bash
# Actualizar Helm charts
helm repo update
helm upgrade <release> <chart> -n <namespace>

# O usar Helmfile
helmfile sync
```

### ¿Cómo hago mantenimiento sin downtime?

- Usa **rolling updates** de Kubernetes
- Configura **multiple replicas**
- Usa **readiness probes** apropiadas
- Considera **blue-green deployments** para cambios mayores

## 📈 Escalado y Performance

### ¿Cómo escalo la plataforma?

**Horizontalmente** (más pods):
```bash
kubectl scale deployment <name> --replicas=5 -n <namespace>
```

**Verticalmente** (más recursos):
Edita el deployment y aumenta requests/limits de CPU/RAM

**Cluster**:
Aumenta el tamaño de los nodos o añade más nodos al cluster

### ¿Cómo optimizo el performance?

1. Revisa métricas en Grafana
2. Ajusta requests/limits según uso real
3. Optimiza workflows (paraleliza tareas)
4. Usa cache cuando sea posible
5. Revisa [Escalado](./../04-operacion/escalado.md)

## 🔗 Integraciones

### ¿Puedo integrar con mi CRM/ERP existente?

Sí, la plataforma puede integrarse con:
- Salesforce
- SAP
- Microsoft Dynamics
- Y cualquier sistema con API REST

Usa n8n para integraciones visuales o crea workflows personalizados.

### ¿Cómo integro con servicios cloud?

Consulta [Integraciones Cloud](./../06-integraciones/cloud-services.md) para guías específicas de AWS, Azure y GCP.

## 🎓 Aprendizaje

### ¿Dónde empiezo si soy nuevo?

1. Lee [Inicio Rápido](./../01-inicio-rapido/README.md)
2. Sigue [Primeros Pasos](./../01-inicio-rapido/primeros-pasos.md)
3. Explora [Casos de Uso](./../03-casos-uso/)
4. Consulta [Guías por Rol](./../07-por-rol/)

### ¿Hay ejemplos o templates?

Sí, el proyecto incluye:
- Ejemplos en cada carpeta de componente
- Templates de workflows en `n8n/`
- DAGs de ejemplo en `data/airflow/dags/`
- Scripts de ejemplo en `scripts/`

## 📞 Soporte

### ¿Dónde obtengo más ayuda?

1. Revisa la [Documentación Técnica](../docs/)
2. Consulta [Troubleshooting](./../04-operacion/troubleshooting.md)
3. Revisa los [Ejemplos Prácticos](./../03-casos-uso/)
4. Busca en los issues del repositorio

### ¿Cómo reporto un bug?

1. Recopila información:
   - Versiones de componentes
   - Logs relevantes
   - Pasos para reproducir
2. Crea un issue con toda la información
3. Incluye configuración (sin secretos)

## 🔒 Licencias

### ¿Qué licencias tienen los componentes?

La mayoría son open-source:
- **Kestra**: Apache 2.0
- **Airflow**: Apache 2.0
- **n8n**: Sustainable Use License (gratis para uso personal/comercial)
- **MLflow**: Apache 2.0
- **Grafana**: Apache 2.0

Consulta las licencias individuales de cada componente.

---

**¿No encuentras tu pregunta?** Abre un issue o consulta la documentación completa.









