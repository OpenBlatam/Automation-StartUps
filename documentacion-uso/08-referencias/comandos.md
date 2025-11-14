# 📝 Referencia Rápida de Comandos

> Cheat sheet de comandos útiles para la plataforma

## 🚀 Inicio Rápido

```bash
# Verificar conexión a Kubernetes
kubectl get nodes

# Ver todos los pods
kubectl get pods --all-namespaces

# Ver servicios
kubectl get svc --all-namespaces

# Ver ingress
kubectl get ingress --all-namespaces
```

## ☸️ Kubernetes Básico

### Pods

```bash
# Listar pods
kubectl get pods -n <namespace>

# Ver detalles de un pod
kubectl describe pod <pod-name> -n <namespace>

# Ver logs
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --tail=100 -f

# Ejecutar comando en un pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Eliminar pod
kubectl delete pod <pod-name> -n <namespace>
```

### Deployments

```bash
# Listar deployments
kubectl get deployments -n <namespace>

# Escalar deployment
kubectl scale deployment <name> --replicas=3 -n <namespace>

# Ver historial de rollout
kubectl rollout history deployment/<name> -n <namespace>

# Rollback
kubectl rollout undo deployment/<name> -n <namespace>

# Ver estado de rollout
kubectl rollout status deployment/<name> -n <namespace>
```

### Servicios

```bash
# Listar servicios
kubectl get svc -n <namespace>

# Ver detalles
kubectl describe svc <service-name> -n <namespace>

# Port-forward
kubectl port-forward svc/<service-name> 8080:80 -n <namespace>
```

### ConfigMaps y Secrets

```bash
# Listar ConfigMaps
kubectl get configmaps -n <namespace>

# Ver contenido
kubectl get configmap <name> -n <namespace> -o yaml

# Listar Secrets
kubectl get secrets -n <namespace>

# Ver secret (base64)
kubectl get secret <name> -n <namespace> -o yaml

# Decodificar secret
kubectl get secret <name> -n <namespace> -o jsonpath='{.data.password}' | base64 -d
```

### Namespaces

```bash
# Listar namespaces
kubectl get namespaces

# Crear namespace
kubectl create namespace <name>

# Cambiar contexto
kubectl config set-context --current --namespace=<namespace>
```

## 🔧 Terraform

```bash
# Inicializar
terraform init

# Validar
terraform validate

# Plan
terraform plan

# Aplicar
terraform apply

# Aplicar con auto-approve
terraform apply -auto-approve

# Destruir
terraform destroy

# Formatear
terraform fmt

# Ver estado
terraform state list
terraform state show <resource>
```

## 📦 Helm

```bash
# Listar releases
helm list -A

# Instalar chart
helm install <name> <chart> -n <namespace>

# Actualizar
helm upgrade <name> <chart> -n <namespace>

# Desinstalar
helm uninstall <name> -n <namespace>

# Ver valores
helm get values <name> -n <namespace>

# Ver manifiestos generados
helm template <chart> > output.yaml
```

## 🎯 Helmfile

```bash
# Validar
helmfile lint

# Ver diferencias
helmfile diff

# Aplicar
helmfile sync

# Destruir
helmfile destroy

# Listar releases
helmfile list
```

## 🐳 Docker (Desarrollo Local)

```bash
# Construir imagen
docker build -t <image-name> .

# Ejecutar contenedor
docker run -it <image-name>

# Ver logs
docker logs <container-id>

# Listar contenedores
docker ps
docker ps -a

# Limpiar
docker system prune -a
```

## 📊 Monitoreo

```bash
# Ver uso de recursos
kubectl top nodes
kubectl top pods -A

# Ver eventos
kubectl get events -A --sort-by='.lastTimestamp'

# Ver métricas de un pod
kubectl top pod <pod-name> -n <namespace>
```

## 🔍 Debugging

```bash
# Ver todos los recursos en un namespace
kubectl get all -n <namespace>

# Describir recurso completo
kubectl describe <resource-type> <name> -n <namespace>

# Ver logs de todos los contenedores
kubectl logs -n <namespace> --all-containers=true --tail=50

# Ver logs de múltiples pods
kubectl logs -n <namespace> -l app=<label> --tail=50

# Ejecutar shell en pod con imagen específica
kubectl run -it --rm debug --image=busybox --restart=Never -- /bin/sh
```

## 🔐 Seguridad

```bash
# Verificar permisos
kubectl auth can-i <verb> <resource> -n <namespace>

# Ver roles
kubectl get roles -n <namespace>
kubectl get rolebindings -n <namespace>

# Ver Network Policies
kubectl get networkpolicies -A
```

## 📁 Makefile (Comandos del Proyecto)

```bash
# Ver todos los comandos disponibles
make help

# Inicializar Terraform
make tf-init TF_DIR=infra/terraform

# Aplicar Terraform
make tf-apply TF_DIR=infra/terraform

# Crear namespaces
make k8s-namespaces

# Configurar Ingress
make k8s-ingress

# Aplicar Helmfile
make helmfile-apply

# Lint de código
make lint

# Tests
make test
```

## 🌐 Port-Forward (Acceso Local)

```bash
# Grafana
kubectl port-forward -n observability svc/grafana 3000:80

# Kestra
kubectl port-forward -n kestra svc/kestra-server 8080:80

# Airflow
kubectl port-forward -n airflow svc/airflow-webserver 8080:8080

# n8n
kubectl port-forward -n n8n svc/n8n 5678:5678

# MLflow
kubectl port-forward -n mlflow svc/mlflow 5000:5000
```

## 📤 Exportar/Importar

```bash
# Exportar configuración
kubectl get <resource> <name> -n <namespace> -o yaml > export.yaml

# Aplicar desde archivo
kubectl apply -f <file.yaml>

# Exportar todos los recursos de un namespace
kubectl get all -n <namespace> -o yaml > namespace-backup.yaml
```

## 🔄 Utilidades

```bash
# Ver versión de kubectl
kubectl version --client

# Ver contexto actual
kubectl config current-context

# Listar contextos
kubectl config get-contexts

# Cambiar contexto
kubectl config use-context <context-name>

# Ver configuración
kubectl config view
```

## 🎯 Comandos por Componente

### Kestra

```bash
# Ver pods de Kestra
kubectl get pods -n kestra

# Ver logs del servidor
kubectl logs -n kestra kestra-server-0 -f

# Acceder a la API
curl http://kestra.your-domain.com/api/v1/flows
```

### Airflow

```bash
# Ver pods de Airflow
kubectl get pods -n airflow

# Ver logs del scheduler
kubectl logs -n airflow airflow-scheduler-0 -f

# Ver logs del webserver
kubectl logs -n airflow airflow-webserver-0 -f

# Ejecutar comando Airflow CLI
kubectl exec -n airflow airflow-scheduler-0 -- airflow dags list
```

### n8n

```bash
# Ver pods de n8n
kubectl get pods -n n8n

# Ver logs
kubectl logs -n n8n n8n-0 -f

# Backup de workflows
# (Desde la UI: Settings → Import/Export)
```

## 💡 Tips

- Usa `-o wide` para ver más información: `kubectl get pods -o wide`
- Usa `-o yaml` o `-o json` para ver configuración completa
- Usa `--watch` o `-w` para ver cambios en tiempo real
- Usa `-l app=<label>` para filtrar por labels
- Usa `--tail=100` para ver las últimas 100 líneas de logs
- Usa `-f` para seguir logs en tiempo real

## 📚 Más Recursos

- [Kubernetes Cheat Sheet oficial](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Helm Cheat Sheet](https://helm.sh/docs/intro/using_helm/)
- [Terraform Commands](https://www.terraform.io/docs/cli/commands/index.html)



