# 🔧 Troubleshooting

> Solución de problemas comunes en la plataforma

## 📋 Tabla de Contenidos

- [Problemas de Despliegue](#-problemas-de-despliegue)
- [Problemas con Kubernetes](#-problemas-con-kubernetes)
- [Problemas con Workflows](#-problemas-con-workflows)
- [Problemas con Datos](#-problemas-con-datos)
- [Problemas de Red](#-problemas-de-red)
- [Problemas de Performance](#-problemas-de-performance)
- [Problemas de Seguridad](#-problemas-de-seguridad)

## 🚀 Problemas de Despliegue

### Pods en estado Pending

**Síntoma**: Los pods no inician y quedan en estado `Pending`

**Diagnóstico**:
```bash
kubectl describe pod <pod-name> -n <namespace>
```

**Causas comunes**:
- Recursos insuficientes en el cluster
- Problemas con PersistentVolumeClaims
- NodeSelector/Affinity no coincide

**Solución**:
```bash
# Verificar recursos disponibles
kubectl top nodes

# Verificar PVCs
kubectl get pvc -n <namespace>

# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

### Pods en CrashLoopBackOff

**Síntoma**: Los pods se reinician continuamente

**Diagnóstico**:
```bash
# Ver logs del pod actual
kubectl logs <pod-name> -n <namespace>

# Ver logs del pod anterior (útil si el pod se reinició)
kubectl logs <pod-name> -n <namespace> --previous

# Describir el pod para ver eventos
kubectl describe pod <pod-name> -n <namespace>
```

**Causas comunes**:
- Error en la configuración
- Secretos faltantes
- Problemas con la base de datos
- Variables de entorno incorrectas

**Solución**:
1. Revisa los logs para identificar el error
2. Verifica los secretos: `kubectl get secrets -n <namespace>`
3. Revisa la configuración en `platform.yaml`
4. Verifica las variables de entorno del deployment

### Helmfile no aplica cambios

**Síntoma**: Los cambios en Helmfile no se reflejan

**Solución**:
```bash
# Validar el archivo
helmfile lint

# Ver qué se va a cambiar
helmfile diff

# Forzar actualización
helmfile sync --force

# Si hay problemas, eliminar y recrear
helmfile destroy
helmfile sync
```

## ☸️ Problemas con Kubernetes

### No puedo conectar al cluster

**Síntoma**: `kubectl get nodes` falla

**Diagnóstico**:
```bash
# Verificar configuración
kubectl config current-context
kubectl config view

# Verificar conectividad
kubectl cluster-info
```

**Soluciones**:

**AWS EKS**:
```bash
aws eks update-kubeconfig --name <cluster-name> --region <region>
```

**Azure AKS**:
```bash
az aks get-credentials --resource-group <rg> --name <cluster-name>
```

**GCP GKE**:
```bash
gcloud container clusters get-credentials <cluster-name> --zone <zone>
```

### Namespace no se crea

**Síntoma**: Error al crear namespace

**Solución**:
```bash
# Verificar permisos
kubectl auth can-i create namespaces

# Crear manualmente
kubectl create namespace <namespace-name>

# O usar el Makefile
make k8s-namespaces
```

### Ingress no funciona

**Síntoma**: No puedo acceder a los servicios a través del Ingress

**Diagnóstico**:
```bash
# Verificar Ingress Controller
kubectl get pods -n ingress-nginx

# Verificar Ingress
kubectl get ingress -A
kubectl describe ingress <ingress-name> -n <namespace>

# Verificar servicios
kubectl get svc -n <namespace>
```

**Soluciones**:
1. Verificar que el Ingress Controller esté corriendo
2. Verificar que el servicio tenga el selector correcto
3. Verificar DNS: `nslookup your-domain.com`
4. Verificar certificados TLS: `kubectl get certificates -A`

## 🔄 Problemas con Workflows

### Kestra: Workflow no se ejecuta

**Diagnóstico**:
```bash
# Ver logs del servidor de Kestra
kubectl logs -n kestra kestra-server-0

# Ver ejecuciones fallidas
# En la UI de Kestra, ve a Executions
```

**Causas comunes**:
- Error de sintaxis en el YAML
- Task type no existe
- Permisos insuficientes
- Recursos no disponibles

**Solución**:
1. Valida el YAML del workflow
2. Revisa los logs de ejecución en la UI
3. Verifica que las dependencias estén instaladas

### n8n: Workflow no se activa

**Diagnóstico**:
- Revisa el estado del workflow en la UI
- Verifica los logs: `kubectl logs -n n8n n8n-0`

**Soluciones**:
1. Activa el workflow manualmente desde la UI
2. Verifica que el webhook esté accesible
3. Revisa la configuración de credenciales
4. Verifica que el cron schedule sea válido

### Airflow: DAG no aparece

**Diagnóstico**:
```bash
# Ver logs del scheduler
kubectl logs -n airflow airflow-scheduler-0

# Ver logs del webserver
kubectl logs -n airflow airflow-webserver-0
```

**Causas comunes**:
- Error de sintaxis en el DAG
- DAG en pausa
- Problemas de importación

**Soluciones**:
1. Valida la sintaxis Python del DAG
2. Verifica imports: `python -m py_compile dag.py`
3. Revisa los logs del scheduler
4. Activa el DAG desde la UI

## 💾 Problemas con Datos

### Base de datos no conecta

**Síntoma**: Las aplicaciones no pueden conectar a la base de datos

**Diagnóstico**:
```bash
# Verificar que el servicio de DB esté corriendo
kubectl get pods -n <namespace> | grep postgres

# Probar conexión
kubectl run -it --rm psql-test --image=postgres:15 --restart=Never -- \
  psql -h <db-service> -U <user> -d <database>
```

**Soluciones**:
1. Verificar que el pod de DB esté Running
2. Verificar secretos de conexión
3. Verificar Network Policies
4. Verificar que el servicio tenga el selector correcto

### PersistentVolume no se monta

**Síntoma**: PVC queda en estado Pending

**Diagnóstico**:
```bash
kubectl describe pvc <pvc-name> -n <namespace>
kubectl get storageclass
```

**Soluciones**:
1. Verificar que exista un StorageClass
2. Verificar que haya nodos con storage disponible
3. Crear StorageClass si no existe:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
```

## 🌐 Problemas de Red

### Servicios no se comunican

**Síntoma**: Los pods no pueden comunicarse entre sí

**Diagnóstico**:
```bash
# Verificar Network Policies
kubectl get networkpolicies -A

# Probar conectividad desde un pod
kubectl run -it --rm test-pod --image=busybox --restart=Never -- \
  wget -O- http://<service-name>.<namespace>.svc.cluster.local
```

**Soluciones**:
1. Revisar Network Policies que puedan estar bloqueando
2. Verificar que los servicios estén en el mismo namespace o configurar DNS correctamente
3. Verificar selectores de servicio

### Ingress no enruta correctamente

**Síntoma**: El Ingress no dirige el tráfico al servicio correcto

**Diagnóstico**:
```bash
kubectl describe ingress <ingress-name> -n <namespace>
kubectl get ingress -A -o yaml
```

**Soluciones**:
1. Verificar que el path y el servicio coincidan
2. Verificar anotaciones del Ingress
3. Verificar que el servicio tenga puerto correcto
4. Revisar logs del Ingress Controller

## ⚡ Problemas de Performance

### Pods lentos o con alto uso de CPU/RAM

**Diagnóstico**:
```bash
# Ver uso de recursos
kubectl top pods -A
kubectl top nodes

# Ver límites y requests
kubectl describe pod <pod-name> -n <namespace>
```

**Soluciones**:
1. Ajustar requests y limits en el deployment
2. Escalar horizontalmente: `kubectl scale deployment <name> --replicas=3`
3. Optimizar la aplicación
4. Revisar si hay memory leaks

### Workflows lentos

**Diagnóstico**:
- Revisar métricas en Grafana
- Revisar logs de ejecución
- Verificar recursos asignados

**Soluciones**:
1. Aumentar recursos del worker
2. Optimizar el workflow (paralelizar tareas)
3. Usar cache cuando sea posible
4. Revisar dependencias externas (APIs lentas, etc.)

## 🔒 Problemas de Seguridad

### Error de autenticación

**Síntoma**: No puedo autenticarme en los dashboards

**Soluciones**:
1. Verificar credenciales en los secretos
2. Resetear password (depende del componente)
3. Verificar configuración de OAuth/SSO si está habilitado

### Secretos no se cargan

**Síntoma**: External Secrets no crea los secretos

**Diagnóstico**:
```bash
kubectl get externalsecrets -A
kubectl describe externalsecret <name> -n <namespace>
```

**Soluciones**:
1. Verificar configuración de External Secrets Operator
2. Verificar credenciales del proveedor (AWS Secrets Manager, etc.)
3. Revisar logs del operador: `kubectl logs -n external-secrets external-secrets-0`

## 📞 Obtener Más Ayuda

### Comandos Útiles de Diagnóstico

```bash
# Ver todos los recursos en un namespace
kubectl get all -n <namespace>

# Ver eventos recientes
kubectl get events -A --sort-by='.lastTimestamp' | tail -20

# Ver logs de todos los pods
kubectl logs -n <namespace> --all-containers=true --tail=50

# Describir recurso completo
kubectl describe <resource-type> <name> -n <namespace>

# Ejecutar shell en un pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash
```

### Recursos Adicionales

- [Documentación de Kubernetes](https://kubernetes.io/docs/)
- [Troubleshooting de Helm](https://helm.sh/docs/troubleshooting/)
- [Logs y Debugging](../04-operacion/monitoreo.md)
- [FAQ](../08-referencias/faq.md)

## 🐛 Reportar Problemas

Si encuentras un bug o problema no documentado:

1. Recopila información:
   - Versión de Kubernetes
   - Versión de los componentes
   - Logs relevantes
   - Pasos para reproducir

2. Crea un issue con toda la información

3. Incluye:
   - Comandos ejecutados
   - Output de `kubectl describe`
   - Logs relevantes
   - Configuración (sin secretos)



