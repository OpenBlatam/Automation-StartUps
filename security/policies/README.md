# Políticas de Seguridad - OPA Gatekeeper

Esta carpeta contiene las políticas de seguridad implementadas con OPA Gatekeeper para hacer cumplir políticas de admisión en Kubernetes.

## Descripción

OPA Gatekeeper es un framework de políticas de admisión basado en Open Policy Agent (OPA) que permite definir y hacer cumplir políticas de seguridad y gobernanza en Kubernetes.

## Estructura

```
policies/
└── gatekeeper/
    ├── constraints.yaml     # ConstraintTemplates y Constraints
    ├── limits.yaml          # Política: Requerir requests/limits
    ├── cost-center.yaml     # Política: Requerir etiqueta cost-center
    └── no-latest.yaml       # Política: Prohibir imágenes con tag 'latest'
```

## Políticas Disponibles

### 1. Requerir Requests/Limits

**Archivo**: `gatekeeper/limits.yaml`

**Función**: Asegura que todos los pods tengan requests y limits de CPU/memoria definidos.

**Beneficios**:
- Mejor planificación de recursos
- Prevención de contention de recursos
- Mejor autoscaling

**Aplicar**:

```bash
kubectl apply -f security/policies/gatekeeper/limits.yaml
```

**Verificar violaciones**:

```bash
kubectl get k8srequiredresources -A
kubectl describe k8srequiredresources require-resources -A
```

### 2. Requerir Etiqueta cost-center

**Archivo**: `gatekeeper/cost-center.yaml`

**Función**: Requiere que todos los recursos tengan la etiqueta `cost-center` para tracking de costos.

**Aplicar**:

```bash
kubectl apply -f security/policies/gatekeeper/cost-center.yaml
```

**Ejemplo de recurso válido**:

```yaml
metadata:
  labels:
    cost-center: "engineering"
```

### 3. Prohibir Tag 'latest' en Imágenes

**Archivo**: `gatekeeper/no-latest.yaml`

**Función**: Bloquea despliegues que usan imágenes con tag `latest` (mala práctica).

**Razón**: El tag `latest` es mutable y puede causar problemas de reproducibilidad.

**Aplicar**:

```bash
kubectl apply -f security/policies/gatekeeper/no-latest.yaml
```

**Ejemplo bloqueado**:

```yaml
# ❌ Esto será rechazado
image: nginx:latest

# ✅ Esto es aceptado
image: nginx:1.23.0
```

### 4. Registros Permitidos

**Archivo**: `gatekeeper/constraints.yaml`

**Función**: Define qué registros de contenedores están permitidos.

**Configuración**:

```yaml
parameters:
  repos:
    - "123456789012.dkr.ecr.us-east-1.amazonaws.com/"
    - "mycorp.azurecr.io/"
    - "gcr.io/my-project/"
```

**Aplicar**:

```bash
kubectl apply -f security/policies/gatekeeper/constraints.yaml
```

## Instalación de Gatekeeper

### Con Helmfile

Gatekeeper puede estar configurado en `helmfile.yaml`:

```bash
helmfile apply
```

### Manualmente

```bash
# Instalar Gatekeeper
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm install gatekeeper gatekeeper/gatekeeper \
  --namespace gatekeeper-system \
  --create-namespace

# Aplicar políticas
kubectl apply -f security/policies/gatekeeper/
```

## Verificación

### Ver todas las políticas

```bash
# Ver ConstraintTemplates (definiciones)
kubectl get constrainttemplates

# Ver Constraints (instancias de políticas)
kubectl get constraints -A

# Ver detalles de una constraint
kubectl describe k8srequiredresources require-resources -A
```

### Ver violaciones

```bash
# Ver violaciones de una constraint
kubectl get k8srequiredresources require-resources -A -o json | \
  jq '.status.violations'

# Ver todas las violaciones
kubectl get constraints -A -o json | \
  jq '.items[] | select(.status.violations | length > 0)'
```

### Auditar recursos existentes

```bash
# Gatekeeper audit automáticamente recursos existentes
# Ver resultados del audit
kubectl logs -n gatekeeper-system deployment/gatekeeper-audit
```

## Crear Políticas Personalizadas

### 1. Crear ConstraintTemplate

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredannotations
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredAnnotations
      validation:
        openAPIV3Schema:
          type: object
          properties:
            annotations:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredannotations
        violation[{"msg": msg}] {
          required := input.parameters.annotations[_]
          not input.review.object.metadata.annotations[required]
          msg := sprintf("Missing required annotation: %v", [required])
        }
```

### 2. Crear Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredAnnotations
metadata:
  name: require-owner-annotation
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod", "Deployment"]
  parameters:
    annotations:
      - "owner"
      - "team"
```

### 3. Aplicar

```bash
kubectl apply -f my-constraint-template.yaml
kubectl apply -f my-constraint.yaml
```

## Excepciones

Para recursos que necesitan excepción temporal:

```yaml
apiVersion: config.gatekeeper.sh/v1alpha1
kind: Config
metadata:
  name: config
  namespace: gatekeeper-system
spec:
  match:
    - excludedNamespaces: ["kube-system", "gatekeeper-system"]
    - processes: ["*"]
  validation:
    traces:
      - user: "system:serviceaccount:namespace:serviceaccount"
        kind:
          group: "*"
          version: "*"
          kind: "*"
        exemptNamespaces: ["exempt-namespace"]
```

## Monitoreo

### Métricas de Prometheus

Gatekeeper expone métricas:

```bash
# Ver métricas
kubectl port-forward -n gatekeeper-system service/gatekeeper-controller-manager-metrics-service 8888:8888
curl http://localhost:8888/metrics

# Métricas clave:
# - gatekeeper_constraints
# - gatekeeper_violations
# - gatekeeper_audit_duration_seconds
```

### ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: gatekeeper
  namespace: gatekeeper-system
spec:
  selector:
    matchLabels:
      control-plane: controller-manager
  endpoints:
    - port: http-metrics
      interval: 30s
```

## Troubleshooting

### Política no se aplica

```bash
# Verificar que Gatekeeper está corriendo
kubectl get pods -n gatekeeper-system

# Ver logs
kubectl logs -n gatekeeper-system deployment/gatekeeper-controller-manager

# Verificar que el ConstraintTemplate está instalado
kubectl get constrainttemplate
```

### Recurso rechazado incorrectamente

```bash
# Ver mensaje de rechazo detallado
kubectl get events --field-selector reason=FailedCreate -A

# Ver logs de admission
kubectl logs -n gatekeeper-system deployment/gatekeeper-audit | grep <resource-name>
```

### Política demasiado restrictiva

1. Temporalmente deshabilitar la constraint
2. Auditar impacto
3. Ajustar política o crear excepción
4. Re-habilitar

## Mejores Prácticas

1. **Empezar con políticas básicas**: Limits y cost-center primero
2. **Auditar antes de enforce**: Usar `dry-run` o `warn` mode inicialmente
3. **Documentar excepciones**: Mantener lista de recursos exentos y razones
4. **Monitorear violaciones**: Configurar alertas para violaciones frecuentes
5. **Revisar políticas regularmente**: Asegurar que siguen siendo relevantes
6. **Usar namespaces para testing**: Probar políticas en dev antes de producción

## Referencias

- [Gatekeeper Documentation](https://open-policy-agent.github.io/gatekeeper/)
- [OPA Rego Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [Gatekeeper Library](https://github.com/open-policy-agent/gatekeeper-library)

