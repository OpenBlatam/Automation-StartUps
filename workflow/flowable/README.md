# Flowable - Business Process Management

Flowable es un motor de procesos de negocio (BPM) open-source que implementa BPMN 2.0 para definir y ejecutar workflows de negocio formales y gobernados.

## Descripción

Flowable proporciona:

- **BPMN 2.0**: Modelado y ejecución de procesos de negocio
- **Case Management**: Gestión de casos y documentos
- **Task Management**: Tareas humanas y automatizadas
- **Decision Tables**: Tablas de decisión (DMN)
- **Auditoría**: Trazabilidad completa de procesos

## Estructura

```
flowable/
└── deployment.yaml    # Deployment de Flowable en Kubernetes
```

## Configuración

El `deployment.yaml` despliega Flowable REST API con:

- **Base de datos**: H2 en memoria (configurable a PostgreSQL/MySQL)
- **Puerto**: 8080
- **Namespace**: `workflows`

### Configuración de Base de Datos

Por defecto usa H2 en memoria. Para producción, configura PostgreSQL:

```yaml
env:
  - name: SPRING_DATASOURCE_DRIVER_CLASS_NAME
    value: org.postgresql.Driver
  - name: SPRING_DATASOURCE_URL
    value: jdbc:postgresql://postgres.workflows.svc.cluster.local:5432/flowable
  - name: SPRING_DATASOURCE_USERNAME
    value: flowable
  - name: SPRING_DATASOURCE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: flowable-db-secret
        key: password
```

## Instalación

```bash
# Aplicar Deployment
kubectl apply -f workflow/flowable/deployment.yaml

# Verificar estado
kubectl get pods -n workflows -l app=flowable

# Port-forward para acceso local
kubectl port-forward -n workflows service/flowable 8080:8080
```

## Uso

### Acceder a la UI

Una vez desplegado:

```bash
# UI de Modeler (diseño de procesos)
http://localhost:8080/flowable-modeler

# UI de Admin (gestión)
http://localhost:8080/flowable-admin

# REST API
http://localhost:8080/flowable-rest/service/
```

**Credenciales por defecto**: `admin` / `test`

### API REST

#### Iniciar un Proceso

```bash
curl -X POST http://localhost:8080/flowable-rest/service/runtime/process-instances \
  -H "Content-Type: application/json" \
  -u admin:test \
  -d '{
    "processDefinitionKey": "businessApproval",
    "variables": [
      {"name": "amount", "value": 5000},
      {"name": "requestor", "value": "john.doe"}
    ]
  }'
```

#### Listar Tareas

```bash
curl http://localhost:8080/flowable-rest/service/runtime/tasks \
  -u admin:test
```

#### Completar una Tarea

```bash
curl -X POST http://localhost:8080/flowable-rest/service/runtime/tasks/{taskId} \
  -H "Content-Type: application/json" \
  -u admin:test \
  -d '{
    "action": "complete",
    "variables": [
      {"name": "approved", "value": true}
    ]
  }'
```

### Desde Kestra

Los flows de Kestra pueden invocar Flowable:

```yaml
# workflow/kestra/flows/bpm_rpa_example.yaml
type: io.kestra.core.tasks.flows.Http
uri: http://flowable.workflows.svc.cluster.local/flowable-rest/service/runtime/process-instances
method: POST
headers:
  Authorization: "Basic ${base64('admin:test')}"
body:
  processDefinitionKey: businessApproval
  variables:
    - name: amount
      value: 5000
```

## Modelado de Procesos

### BPMN 2.0

Flowable soporta elementos BPMN:

- **Start/End Events**: Inicio y fin de proceso
- **Tasks**: Tareas de usuario, servicio, script
- **Gateways**: Decisión, paralelo, inclusivo
- **Events**: Timer, mensaje, señal
- **Sub-processes**: Sub-procesos embebidos

### Ejemplo Básico

1. **Start Event**: Recibe solicitud
2. **User Task**: Aprobación de manager
3. **Gateway**: ¿Aprobado?
4. **Service Task**: Procesar aprobación
5. **End Event**: Finalizar

### Desplegar un Proceso

```bash
# Desde UI: Flowable Modeler → Deploy
# O vía API:
curl -X POST http://localhost:8080/flowable-rest/service/repository/deployments \
  -H "Content-Type: multipart/form-data" \
  -u admin:test \
  -F "file=@process.bpmn20.xml"
```

## Integración con Otros Componentes

### Con Kestra

Kestra puede iniciar procesos de Flowable y esperar completación:

```yaml
# Iniciar proceso
- id: startFlowableProcess
  type: io.kestra.core.tasks.flows.Http
  uri: http://flowable/.../process-instances
  method: POST
  
# Polling para completación
- id: waitForCompletion
  type: io.kestra.core.tasks.flows.Http
  uri: http://flowable/.../runtime/tasks?processInstanceId=${outputs.startFlowableProcess.id}
  method: GET
```

### Con OpenRPA

Flowable puede disparar bots de RPA mediante Service Tasks HTTP que llaman a webhooks de OpenRPA.

### Con Kafka

Integra eventos de Flowable con Kafka usando Spring Cloud Stream o eventos personalizados.

## Base de Datos

### PostgreSQL (Producción)

```yaml
# Configurar PostgreSQL en deployment.yaml
env:
  - name: SPRING_DATASOURCE_URL
    value: jdbc:postgresql://postgres.workflows.svc:5432/flowable
  - name: SPRING_DATASOURCE_USERNAME
    value: flowable
  - name: SPRING_DATASOURCE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: flowable-db
        key: password
```

### Migraciones

Flowable crea automáticamente las tablas al iniciar si `spring.jpa.hibernate.ddl-auto=update`.

Para migraciones controladas, usa Flyway o Liquibase.

## Seguridad

### Autenticación

Configura OAuth2 o LDAP:

```yaml
env:
  - name: FLOWABLE_SECURITY_AUTH_TYPE
    value: oauth2
  - name: FLOWABLE_OAUTH2_CLIENT_ID
    value: flowable-client
  - name: FLOWABLE_OAUTH2_CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: oauth2-secret
        key: client-secret
```

### RBAC

Configura roles y permisos en la UI de Admin.

## Monitoreo

### Métricas

Flowable expone métricas de Spring Boot Actuator:

```bash
# Health check
curl http://localhost:8080/flowable-rest/actuator/health

# Métricas
curl http://localhost:8080/flowable-rest/actuator/metrics
```

### Logs

```bash
# Ver logs
kubectl logs -n workflows deployment/flowable

# Logs estructurados
kubectl logs -n workflows deployment/flowable | jq
```

### Auditoría

Flowable registra automáticamente:
- Inicio y fin de procesos
- Completación de tareas
- Cambios de variables
- Eventos del proceso

Consulta la tabla `ACT_HI_*` en la base de datos.

## Troubleshooting

### Proceso no inicia

```bash
# Verificar definición de proceso
curl http://localhost:8080/flowable-rest/service/repository/process-definitions \
  -u admin:test

# Verificar logs
kubectl logs -n workflows deployment/flowable | grep ERROR
```

### Tarea no aparece

```bash
# Listar tareas asignadas
curl http://localhost:8080/flowable-rest/service/runtime/tasks?assignee=john.doe \
  -u admin:test

# Ver instancias activas
curl http://localhost:8080/flowable-rest/service/runtime/process-instances \
  -u admin:test
```

### Error de conexión a BD

```bash
# Verificar secret
kubectl get secret -n workflows flowable-db

# Verificar conectividad
kubectl exec -n workflows deployment/flowable -- \
  nc -zv postgres.workflows.svc.cluster.local 5432
```

## Referencias

- [Flowable Documentation](https://www.flowable.com/open-source/docs/)
- [BPMN 2.0 Specification](https://www.omg.org/spec/BPMN/2.0/)
- [Flowable REST API](https://www.flowable.com/open-source/docs/rest-api/)


