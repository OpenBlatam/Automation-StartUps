# 🎯 Primeros Pasos

> Crea tu primera automatización en menos de 10 minutos

## 🎬 Tu Primer Workflow con Kestra

Kestra es la forma más fácil de empezar. Vamos a crear un workflow simple que ejecuta un script Python.

### Paso 1: Acceder a Kestra

```bash
# Obtener la URL de Kestra
kubectl get ingress -n kestra kestra

# O acceder directamente si tienes port-forward
kubectl port-forward -n kestra svc/kestra-server 8080:8080
# Luego abre http://localhost:8080
```

### Paso 2: Crear tu Primer Flow

Crea un archivo `mi-primer-flow.yaml`:

```yaml
id: mi-primer-flow
namespace: tutorial
description: Mi primer workflow en Kestra

tasks:
  - id: saludar
    type: io.kestra.core.tasks.scripts.Python
    runner: DOCKER
    docker:
      image: python:3.11
    script: |
      print("¡Hola desde Kestra!")
      print(f"Ejecutado el {datetime.now()}")
```

### Paso 3: Subir el Flow

**Opción A: Desde la UI de Kestra**
1. Ve a la interfaz web de Kestra
2. Click en "Flows" → "Create"
3. Pega el contenido del YAML
4. Click en "Save"

**Opción B: Desde la línea de comandos**

```bash
# Usando la API de Kestra
curl -X POST http://kestra.your-domain.com/api/v1/flows \
  -H "Content-Type: application/yaml" \
  --data-binary @mi-primer-flow.yaml
```

### Paso 4: Ejecutar el Flow

Desde la UI:
1. Ve a tu flow
2. Click en "Execute"
3. Observa la ejecución en tiempo real

Desde la línea de comandos:

```bash
curl -X POST http://kestra.your-domain.com/api/v1/executions/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "tutorial",
    "flowId": "mi-primer-flow"
  }'
```

## 🤖 Tu Primera Automatización con n8n

n8n es perfecto para automatizaciones visuales sin código.

### Paso 1: Acceder a n8n

```bash
# Port-forward
kubectl port-forward -n n8n svc/n8n 5678:5678
# Abre http://localhost:5678
```

### Paso 2: Crear un Workflow Simple

Vamos a crear un workflow que:
1. Recibe un webhook
2. Procesa los datos
3. Envía un email

**En la UI de n8n:**

1. Click en "New Workflow"
2. Arrastra un nodo "Webhook" al canvas
3. Click en "Execute Node" para obtener la URL del webhook
4. Arrastra un nodo "Code" para procesar datos
5. Arrastra un nodo "Email" para enviar
6. Conecta los nodos
7. Configura cada nodo según tus necesidades
8. Activa el workflow

### Paso 3: Probar el Workflow

```bash
# Enviar datos al webhook
curl -X POST https://your-n8n.com/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "email": "juan@example.com"
  }'
```

## 📊 Tu Primer Pipeline ETL con Airflow

### Paso 1: Acceder a Airflow

```bash
# Obtener credenciales
kubectl get secret airflow-webserver-secret -n airflow -o jsonpath='{.data.password}' | base64 -d

# Port-forward
kubectl port-forward -n airflow svc/airflow-webserver 8080:8080
# Abre http://localhost:8080
# Usuario: admin
# Password: (el obtenido arriba)
```

### Paso 2: Crear tu Primer DAG

Crea `data/airflow/dags/mi-primer-dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def saludar():
    print("¡Hola desde Airflow!")
    return "Éxito"

default_args = {
    'owner': 'tú',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'mi_primer_dag',
    default_args=default_args,
    description='Mi primer DAG de Airflow',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

tarea_saludar = PythonOperator(
    task_id='saludar',
    python_callable=saludar,
    dag=dag,
)
```

### Paso 3: Verificar el DAG

Airflow detectará automáticamente el DAG. En la UI:
1. Ve a "DAGs"
2. Busca "mi_primer_dag"
3. Actívalo
4. Ejecútalo manualmente

## 🎥 Tu Primera Automatización TikTok

El sistema incluye automatización completa para TikTok.

### Paso 1: Configurar el Sistema

```bash
cd scripts
./setup_tiktok_system.sh
```

### Paso 2: Probar con un Video

```bash
python3 tiktok_cli.py
# Sigue las instrucciones interactivas
```

### Paso 3: Usar el Workflow de n8n

Importa el workflow desde `n8n_workflow_tiktok_auto_edit.json` en n8n.

## 📝 Ejercicios Prácticos

### Ejercicio 1: Workflow con Múltiples Tareas

Crea un workflow en Kestra que:
1. Descarga un archivo
2. Procesa el archivo
3. Sube el resultado a S3
4. Envía una notificación

### Ejercicio 2: Automatización de Email

Crea un workflow en n8n que:
1. Monitorea una carpeta de Google Drive
2. Cuando aparece un nuevo archivo, lo procesa
3. Envía un resumen por email

### Ejercicio 3: Pipeline de Datos

Crea un DAG en Airflow que:
1. Extrae datos de una API
2. Transforma los datos
3. Los carga en una base de datos
4. Genera un reporte

## 🎓 Recursos de Aprendizaje

- [Documentación de Kestra](https://kestra.io/docs)
- [Documentación de n8n](https://docs.n8n.io)
- [Documentación de Airflow](https://airflow.apache.org/docs)
- [Guías de Componentes](../02-componentes/)

## 🆘 ¿Necesitas Ayuda?

- Revisa los [Ejemplos Prácticos](../03-casos-uso/)
- Consulta la [Referencia Rápida](../08-referencias/comandos.md)
- Ve a [Troubleshooting](../04-operacion/troubleshooting.md)

## 🚀 Siguientes Pasos

Ahora que has creado tu primera automatización:

1. Explora [Casos de Uso Avanzados](../03-casos-uso/)
2. Aprende sobre [Componentes Específicos](../02-componentes/)
3. Configura [Monitoreo y Alertas](../04-operacion/monitoreo.md)



