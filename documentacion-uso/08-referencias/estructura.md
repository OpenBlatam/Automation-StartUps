# 📁 Estructura del Proyecto

> Mapa completo de la estructura de directorios y archivos del proyecto

## 🗂️ Estructura Principal

```
IA/
├── documentacion-uso/          # 📚 Esta carpeta - Guías de uso
├── docs/                       # Documentación técnica detallada
├── README.md                   # Documentación principal del proyecto
│
├── infra/                      # Infraestructura como código
│   ├── terraform/              # Configuración Terraform
│   ├── helmfile/               # Configuración Helmfile
│   └── kubernetes/             # Manifiestos Kubernetes
│
├── workflow/                   # Workflows y orquestación
│   ├── kestra/                 # Flows de Kestra
│   ├── flowable/               # Procesos BPMN Flowable
│   └── camunda/                # Procesos BPMN Camunda
│
├── data/                       # Procesamiento de datos
│   ├── airflow/                # DAGs de Airflow
│   ├── db/                     # Scripts y schemas de BD
│   └── integrations/           # Integraciones de datos
│
├── n8n/                        # Workflows de n8n
│   ├── *.json                  # Workflows exportados
│   └── *.md                    # Documentación de workflows
│
├── ml/                         # Machine Learning
│   ├── mlflow/                 # Configuración MLflow
│   ├── kubeflow/               # Pipelines Kubeflow
│   └── kserve/                 # Model serving
│
├── rpa/                        # Automatización RPA
│   └── OPENRPA.md              # Documentación OpenRPA
│
├── observability/              # Monitoreo y observabilidad
│   ├── prometheus/             # Configuración Prometheus
│   ├── grafana/                # Dashboards Grafana
│   └── loki/                   # Logging con Loki
│
├── security/                   # Configuración de seguridad
│   ├── rbac/                   # Roles y permisos
│   ├── network-policies/       # Políticas de red
│   └── external-secrets/       # Gestión de secretos
│
├── scripts/                    # Scripts utilitarios
│   ├── setup_*.sh              # Scripts de configuración
│   ├── health_check.py         # Health checks
│   └── *.py                    # Scripts Python varios
│
├── web/                        # Aplicaciones web
│   └── [frontend apps]         # Interfaces de usuario
│
├── customer-journey/           # Mapeo de customer journey
│   └── src/                    # Código fuente
│
├── email_modules/              # Módulos de email
│   └── *.py                    # Generadores de email
│
├── environments/               # Configuración por entorno
│   ├── dev.yaml                # Desarrollo
│   ├── stg.yaml                # Staging
│   └── prod.yaml               # Producción
│
├── kubernetes/                 # Manifiestos K8s adicionales
├── backup/                     # Scripts y config de backups
├── tests/                      # Tests automatizados
├── utils/                      # Utilidades compartidas
│
├── docker-compose.yml          # Docker Compose (desarrollo local)
├── Makefile                    # Comandos Make
├── pyproject.toml              # Configuración Python
├── package.json                # Dependencias Node.js
└── platform.yaml              # Configuración principal
```

## 📚 documentacion-uso/ (Esta Carpeta)

```
documentacion-uso/
├── README.md                   # Índice principal
│
├── 01-inicio-rapido/          # Guías de inicio
│   ├── README.md
│   ├── instalacion.md
│   └── primeros-pasos.md
│
├── 02-componentes/             # Documentación de componentes
│   ├── kestra.md
│   ├── n8n.md
│   ├── airflow.md
│   ├── mlflow.md
│   └── [otros componentes]
│
├── 03-casos-uso/               # Casos de uso prácticos
│   ├── campanas-marketing.md
│   ├── rastreo-pedidos.md
│   └── [otros casos]
│
├── 04-operacion/               # Operación y mantenimiento
│   ├── despliegue.md
│   ├── entornos.md
│   ├── backups.md
│   ├── monitoreo.md
│   ├── escalado.md
│   └── troubleshooting.md
│
├── 05-seguridad/               # Seguridad
│   ├── configuracion.md
│   ├── secretos.md
│   └── [otras guías]
│
├── 06-integraciones/           # Integraciones
│   ├── apis-webhooks.md
│   └── [otras integraciones]
│
├── 07-por-rol/                 # Guías por rol
│   ├── desarrolladores.md
│   ├── devops.md
│   └── [otros roles]
│
└── 08-referencias/             # Referencias rápidas
    ├── comandos.md
    ├── estructura.md          # Este archivo
    ├── variables-entorno.md
    ├── faq.md
    └── glosario.md
```

## 🔍 Componentes Clave

### workflow/
Contiene todos los workflows y procesos de negocio:
- **kestra/**: Workflows declarativos en YAML
- **flowable/**: Procesos BPMN formales
- **camunda/**: BPMN enterprise

### data/
Procesamiento y transformación de datos:
- **airflow/**: Pipelines ETL con DAGs
- **db/**: Schemas y scripts de base de datos
- **integrations/**: Integraciones con fuentes externas

### n8n/
Workflows de automatización visual:
- Archivos `.json` exportados desde n8n
- Documentación de cada workflow

### ml/
Machine Learning y MLOps:
- **mlflow/**: Tracking y gestión de modelos
- **kubeflow/**: Pipelines de ML
- **kserve/**: Servicio de modelos

### infra/
Infraestructura como código:
- **terraform/**: Recursos cloud
- **helmfile/**: Despliegues con Helm
- **kubernetes/**: Manifiestos K8s

## 📝 Archivos Importantes

### Configuración Principal
- `platform.yaml`: Configuración central del proyecto
- `docker-compose.yml`: Setup local con Docker
- `Makefile`: Comandos simplificados
- `pyproject.toml`: Configuración Python
- `package.json`: Dependencias Node.js

### Entornos
- `environments/dev.yaml`: Configuración desarrollo
- `environments/stg.yaml`: Configuración staging
- `environments/prod.yaml`: Configuración producción

### Documentación
- `README.md`: Documentación principal
- `docs/`: Documentación técnica detallada
- `documentacion-uso/`: Guías de uso (esta carpeta)

## 🎯 Dónde Encontrar Cosas

### ¿Dónde están los workflows?
- Kestra: `workflow/kestra/flows/`
- n8n: `n8n/*.json`
- Airflow: `data/airflow/dags/`

### ¿Dónde está la configuración de infraestructura?
- Terraform: `infra/terraform/`
- Helm: `infra/helmfile/`
- Kubernetes: `kubernetes/` y `infra/kubernetes/`

### ¿Dónde están los scripts?
- Scripts Python: `scripts/*.py`
- Scripts Shell: `scripts/*.sh`
- Scripts de setup: `scripts/setup_*.sh`

### ¿Dónde está la documentación?
- Uso: `documentacion-uso/` (esta carpeta)
- Técnica: `docs/`
- Componentes: `[componente]/README.md` o `[componente]/*.md`

## 🔗 Enlaces Útiles

- [README Principal](../README.md)
- [Documentación Técnica](../docs/)
- [Guía de Inicio Rápido](./01-inicio-rapido/README.md)
- [Referencia de Comandos](./comandos.md)

## 📌 Convenciones

### Nombres de Archivos
- Scripts: `snake_case.sh` o `snake_case.py`
- Configuración: `kebab-case.yaml` o `snake_case.yaml`
- Documentación: `UPPER_SNAKE_CASE.md` o `kebab-case.md`

### Estructura de Carpetas
- Componentes principales tienen su propia carpeta
- Cada componente puede tener subcarpetas para organización
- Documentación relacionada está cerca del código

---

**Nota**: Esta estructura puede evolucionar. Consulta el README principal para la versión más actualizada.









