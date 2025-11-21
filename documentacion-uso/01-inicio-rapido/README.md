# 🚀 Inicio Rápido

> Empieza a usar la plataforma en menos de 15 minutos

## ⚡ Inicio Ultra Rápido (5 minutos)

### Prerrequisitos

Asegúrate de tener instalado:
- `kubectl` (versión 1.24+)
- `helm` (versión 3.13+)
- `terraform` (versión 1.6+)
- `make`
- Acceso a un cluster de Kubernetes (EKS, AKS, GKE, o local con minikube/kind)

### Paso 1: Clonar y Configurar

```bash
# Si aún no tienes el proyecto
git clone <repo-url>
cd IA

# Configurar variables de entorno básicas
cp platform.yaml.example platform.yaml
# Editar platform.yaml con tu configuración
```

### Paso 2: Desplegar Infraestructura Base

```bash
# Inicializar Terraform
make tf-init TF_DIR=infra/terraform

# Aplicar configuración (esto puede tomar 10-15 minutos)
make tf-apply TF_DIR=infra/terraform
```

### Paso 3: Configurar Kubernetes

```bash
# Crear namespaces necesarios
make k8s-namespaces

# Configurar Ingress
make k8s-ingress
```

### Paso 4: Desplegar Componentes

```bash
# Desplegar todos los componentes base con Helmfile
make helmfile-apply
```

### Paso 5: Verificar Despliegue

```bash
# Verificar que los pods estén corriendo
kubectl get pods --all-namespaces

# Acceder a los dashboards (ajusta las URLs según tu configuración)
# Grafana: http://grafana.your-domain.com
# Kestra: http://kestra.your-domain.com
# Airflow: http://airflow.your-domain.com
```

## 📚 Siguientes Pasos

Una vez completado el inicio rápido:

1. **Crea tu primer workflow**: Ve a [Primeros Pasos](./primeros-pasos.md)
2. **Configura tu entorno**: Revisa [Instalación Completa](./instalacion.md)
3. **Explora componentes**: Consulta [Componentes Principales](../02-componentes/)

## 🎯 ¿Qué Componente Usar?

| Necesidad | Componente Recomendado | Guía |
|-----------|------------------------|------|
| Workflow simple | Kestra | [Kestra](../02-componentes/kestra.md) |
| Proceso BPMN formal | Flowable | [Flowable](../02-componentes/flowable.md) |
| Automatización visual | n8n | [n8n](../02-componentes/n8n.md) |
| Pipeline ETL | Airflow | [Airflow](../02-componentes/airflow.md) |
| Automatización UI | OpenRPA | [OpenRPA](../02-componentes/openrpa.md) |
| Machine Learning | MLflow | [MLflow](../02-componentes/mlflow.md) |
| Dashboards | Grafana | [Grafana](../02-componentes/grafana.md) |

## ⚠️ Problemas Comunes

Si encuentras problemas durante el inicio rápido:

- **Error de conexión a Kubernetes**: Verifica `kubectl get nodes`
- **Pods no inician**: Revisa `kubectl describe pod <pod-name>`
- **Problemas con Helmfile**: Ejecuta `helmfile lint` para validar
- **Más ayuda**: Ve a [Troubleshooting](../04-operacion/troubleshooting.md)

## 📖 Documentación Relacionada

- [Instalación Completa](./instalacion.md) - Setup detallado paso a paso
- [Primeros Pasos](./primeros-pasos.md) - Tu primer workflow/automatización
- [Configuración de Entornos](../04-operacion/entornos.md) - Dev, Staging, Prod









