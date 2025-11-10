# 🏗️ Arquitectura del Sistema

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Documentación completa de la arquitectura de la plataforma de automatización empresarial.

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Arquitectura de Alto Nivel](#-arquitectura-de-alto-nivel)
- [Componentes Principales](#-componentes-principales)
- [Flujo de Datos](#-flujo-de-datos)
- [Patrones Arquitectónicos](#-patrones-arquitectónicos)
- [Seguridad](#-seguridad)
- [Escalabilidad](#-escalabilidad)
- [Observabilidad](#-observabilidad)
- [Decisiones Arquitectónicas](#-decisiones-arquitectónicas)

---

## 🎯 Visión General

La plataforma es un sistema **modular y escalable** diseñado para automatizar procesos empresariales complejos. Está construida sobre Kubernetes y utiliza una arquitectura de microservicios con componentes desacoplados.

### Principios de Diseño

1. **Modularidad**: Componentes independientes y reutilizables
2. **Escalabilidad**: Auto-scaling horizontal y vertical
3. **Resiliencia**: Circuit breakers, retry logic, fallbacks
4. **Observabilidad**: Métricas, logs, traces completos
5. **Seguridad**: Defense in depth, least privilege
6. **Multi-cloud**: Soporte para AWS, Azure, GCP, on-premise

---

## 🏛️ Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Grafana  │  │  Kestra  │  │ Airflow  │  │   Web    │        │
│  │ Dashboard│  │   UI     │  │   UI     │  │  Apps    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE ORQUESTACIÓN                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Kestra   │  │ Flowable │  │ Camunda  │  │ Airflow  │        │
│  │ Workflows│  │   BPM    │  │   BPM    │  │   DAGs   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE SERVICIOS                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  ETL     │  │   ML     │  │   RPA    │  │  APIs    │        │
│  │ Services │  │ Services │  │ Services │  │ Gateway  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE DATOS                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │PostgreSQL│  │  Kafka   │  │   S3/    │  │  Redis   │        │
│  │          │  │          │  │  ADLS    │  │  Cache   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE INFRAESTRUCTURA                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Kubernetes│ │  Prometheus│ │  Loki    │  │  Vault   │        │
│  │   (EKS/   │ │  /Grafana  │ │  Logs    │  │ Secrets  │        │
│  │   AKS)    │ │            │ │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes Principales

### 1. Orquestación y Workflows

#### Kestra
- **Propósito**: Workflows declarativos en YAML
- **Ubicación**: `workflow/kestra/`
- **Características**:
  - Flujos declarativos sin código
  - Integración con múltiples sistemas
  - UI para visualización y ejecución
  - Triggers programados y eventos

#### Flowable / Camunda
- **Propósito**: Procesos de negocio BPMN
- **Ubicación**: `workflow/flowable/`, `workflow/camunda/`
- **Características**:
  - Modelado BPMN 2.0
  - Workers externos para tareas
  - Gestión de aprobaciones multi-nivel
  - Auditoría completa

#### Airflow
- **Propósito**: Pipelines ETL y automatización
- **Ubicación**: `data/airflow/`
- **Características**:
  - DAGs para procesamiento de datos
  - Scheduling avanzado
  - Retry logic y alertas
  - Integración con múltiples fuentes

### 2. Procesamiento de Datos

#### ETL Pipeline
- **Componentes**:
  - Extract: Conexiones a múltiples fuentes
  - Transform: Transformaciones y validaciones
  - Load: Carga a data lake y bases de datos
- **Características**:
  - Procesamiento en lotes
  - Streaming opcional (Kafka)
  - Quality checks automáticos
  - Data lineage tracking

#### Integraciones
- **Ubicación**: `data/integrations/`
- **Soporte**:
  - Databricks
  - Snowflake
  - HubSpot
  - Salesforce
  - APIs REST genéricas

### 3. Machine Learning

#### MLflow
- **Propósito**: Tracking y registro de modelos
- **Ubicación**: `ml/mlflow/`
- **Características**:
  - Experiment tracking
  - Model registry
  - Model versioning
  - Deployment tracking

#### KServe
- **Propósito**: Model serving
- **Ubicación**: `ml/kserve/`
- **Características**:
  - Auto-scaling
  - A/B testing
  - Canary deployments
  - Multi-model serving

#### Kubeflow
- **Propósito**: Plataforma completa de MLOps
- **Ubicación**: `ml/kubeflow/`
- **Características**:
  - Pipeline orchestration
  - Hyperparameter tuning
  - Distributed training
  - Experiment management

### 4. Automatización RPA

#### OpenRPA
- **Propósito**: Automatización de UI/Desktop
- **Ubicación**: `rpa/`
- **Características**:
  - Automatización de aplicaciones desktop
  - Web scraping
  - Automatización de formularios
  - Integración con workflows

### 5. Observabilidad

#### Prometheus
- **Propósito**: Métricas y alertas
- **Ubicación**: `observability/prometheus/`
- **Métricas**:
  - Sistema (CPU, memoria, disco)
  - Aplicación (request rate, latency)
  - Negocio (KPIs, conversiones)

#### Grafana
- **Propósito**: Visualización y dashboards
- **Ubicación**: `observability/grafana/`
- **Dashboards**:
  - Sistema y infraestructura
  - KPIs de negocio
  - Performance de aplicaciones
  - Alertas y SLA

#### Loki
- **Propósito**: Agregación de logs
- **Ubicación**: `observability/loki/`
- **Características**:
  - Log aggregation
  - Log querying
  - Integración con Grafana

### 6. Seguridad

#### Vault
- **Propósito**: Gestión de secretos
- **Ubicación**: `security/vault/`
- **Características**:
  - Secret rotation
  - Dynamic secrets
  - Encryption at rest

#### OPA Gatekeeper
- **Propósito**: Policy enforcement
- **Ubicación**: `security/policies/`
- **Políticas**:
  - Pod security policies
  - Resource quotas
  - Network policies

#### External Secrets
- **Propósito**: Sincronización de secretos
- **Ubicación**: `security/secrets/`
- **Características**:
  - Sincronización desde Vault
  - Auto-refresh
  - Audit trail

---

## 🔄 Flujo de Datos

### Flujo Típico de Procesamiento

```
1. Trigger (Evento/Programado)
   │
   ▼
2. Orquestador (Kestra/Flowable/Airflow)
   │
   ▼
3. Extracción de Datos
   │
   ▼
4. Transformación y Validación
   │
   ▼
5. Carga a Data Lake / Base de Datos
   │
   ▼
6. Análisis y Reportes
   │
   ▼
7. Notificaciones y Alertas
```

### Flujo de Aprobaciones

```
1. Solicitud de Aprobación
   │
   ▼
2. Validación de Reglas de Negocio
   │
   ▼
3. Asignación a Aprobadores
   │
   ▼
4. Notificaciones (Email/Slack)
   │
   ▼
5. Proceso de Aprobación
   │
   ├─► Aprobado → Ejecución
   │
   └─► Rechazado → Notificación y Archivado
```

### Flujo de ML Pipeline

```
1. Data Ingestion
   │
   ▼
2. Feature Engineering
   │
   ▼
3. Model Training
   │
   ▼
4. Model Evaluation
   │
   ├─► Métricas OK → Registro en MLflow
   │
   └─► Métricas Insuficientes → Retraining
   │
   ▼
5. Model Deployment (KServe)
   │
   ▼
6. Monitoring y Drift Detection
```

---

## 🎨 Patrones Arquitectónicos

### 1. Repository Pattern
- **Uso**: Acceso a datos abstraído
- **Ejemplo**: `data/airflow/plugins/approval_cleanup_ops.py`

### 2. Strategy Pattern
- **Uso**: Algoritmos intercambiables
- **Ejemplo**: Múltiples estrategias de ETL

### 3. Observer Pattern
- **Uso**: Notificaciones y eventos
- **Ejemplo**: Sistema de alertas y notificaciones

### 4. Circuit Breaker Pattern
- **Uso**: Protección contra fallos en cascada
- **Ejemplo**: Conexiones a servicios externos

### 5. Factory Pattern
- **Uso**: Creación de objetos complejos
- **Ejemplo**: Creación de workers y conexiones

### 6. Decorator Pattern
- **Uso**: Funcionalidad adicional sin modificar código
- **Ejemplo**: Retry logic, logging, métricas

---

## 🔒 Seguridad

### Capas de Seguridad

1. **Network Layer**
   - Network Policies (Kubernetes)
   - Firewall rules
   - VPN/Private endpoints

2. **Application Layer**
   - RBAC (Role-Based Access Control)
   - OAuth2/OIDC
   - API authentication

3. **Data Layer**
   - Encryption at rest
   - Encryption in transit (TLS)
   - Data masking

4. **Secret Management**
   - Vault para secretos
   - External Secrets Operator
   - Secret rotation

### Compliance

- **Auditoría**: Logs completos de todas las operaciones
- **GDPR**: Data retention policies
- **SOC 2**: Controls documentados
- **HIPAA**: Encryption y access controls

---

## 📈 Escalabilidad

### Horizontal Scaling

- **Kubernetes HPA**: Auto-scaling basado en métricas
- **Workers**: Celery workers para Airflow
- **Kafka**: Particionado para throughput
- **Database**: Read replicas y sharding

### Vertical Scaling

- **Resource Limits**: CPU/Memory configurables
- **Node Groups**: Instancias optimizadas por carga
- **Database**: Instance types escalables

### Performance Optimization

- **Caching**: Redis para datos frecuentes
- **Connection Pooling**: Pools optimizados
- **Batch Processing**: Procesamiento en lotes
- **Indexing**: Índices optimizados en BD

Ver [`docs/ESCALABILIDAD.md`](./ESCALABILIDAD.md) para más detalles.

---

## 👁️ Observabilidad

### Métricas

- **Sistema**: CPU, memoria, disco, red
- **Aplicación**: Request rate, latency, errors
- **Negocio**: KPIs, conversiones, revenue

### Logs

- **Estructurados**: JSON format
- **Niveles**: DEBUG, INFO, WARNING, ERROR
- **Agregación**: Loki para centralización

### Traces

- **Distributed Tracing**: OpenTelemetry
- **Request Flow**: Seguimiento end-to-end
- **Performance**: Latency breakdown

### Alertas

- **Prometheus Alertmanager**: Alertas basadas en métricas
- **Slack/Email**: Notificaciones multi-canal
- **PagerDuty**: Escalamiento para incidentes críticos

Ver [`observability/README.md`](../observability/README.md) para más detalles.

---

## 💡 Decisiones Arquitectónicas

### Por qué Kubernetes?

- **Portabilidad**: Multi-cloud y on-premise
- **Escalabilidad**: Auto-scaling nativo
- **Ecosistema**: Herramientas maduras
- **Comunidad**: Amplio soporte

### Por qué Airflow?

- **Mature**: Ecosistema establecido
- **Flexible**: Soporte para múltiples casos de uso
- **Integración**: Muchos conectores disponibles
- **UI**: Interfaz rica para monitoreo

### Por qué Kestra?

- **Declarativo**: YAML sin código
- **Accesible**: Para usuarios no técnicos
- **Rápido**: Setup rápido para workflows simples
- **Integración**: Fácil integración con otros sistemas

### Por qué PostgreSQL?

- **Relacional**: ACID compliance
- **Extensions**: PostGIS, JSON, etc.
- **Performance**: Optimización avanzada
- **Open Source**: Sin vendor lock-in

---

## 📚 Referencias

- [Documentación de Kubernetes](https://kubernetes.io/docs/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Kestra Documentation](https://kestra.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

