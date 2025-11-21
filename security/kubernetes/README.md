# Kubernetes Security - RBAC y Resource Management

Esta carpeta contiene configuraciones de seguridad de Kubernetes incluyendo RBAC (Role-Based Access Control) y gestión de recursos (LimitRanges, ResourceQuotas).

## Estructura

```
kubernetes/
├── rbac-baseline.yaml        # Roles y RoleBindings base
└── limitranges-quotas.yaml   # LimitRanges y ResourceQuotas
```

## Componentes

### RBAC (Role-Based Access Control)

**Archivo**: `rbac-baseline.yaml`

Define roles y permisos para usuarios y Service Accounts.

**Roles incluidos**:
- **platform-viewer**: Permisos de solo lectura
- **platform-editor**: Permisos de lectura/escritura (sin eliminar)
- **platform-admin**: Permisos completos en namespace

**Aplicar**:

```bash
kubectl apply -f security/kubernetes/rbac-baseline.yaml

# Verificar
kubectl get roles,rolebindings -A
```

**Ejemplo de uso**:

```yaml
# Crear ServiceAccount con permisos limitados
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kpis-api-sa
  namespace: integration
---
# Asignar rol de viewer
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kpis-api-viewer
  namespace: integration
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: platform-viewer
subjects:
- kind: ServiceAccount
  name: kpis-api-sa
  namespace: integration
```

### LimitRanges y ResourceQuotas

**Archivo**: `limitranges-quotas.yaml`

Define límites de recursos por namespace:
- **LimitRanges**: Límites por pod/container
- **ResourceQuotas**: Límites totales por namespace

**Aplicar**:

```bash
kubectl apply -f security/kubernetes/limitranges-quotas.yaml

# Verificar
kubectl get limitranges,resourcequotas -A
```

## RBAC Detallado

### Roles Disponibles

#### platform-viewer

Permisos de solo lectura:

```yaml
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
```

#### platform-editor

Permisos de lectura/escritura:

```yaml
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
# Nota: NO incluye "delete"
```

#### platform-admin

Permisos completos:

```yaml
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
```

### ClusterRoles

Para permisos a nivel de cluster:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
- apiGroups: [""]
  resources: ["nodes", "persistentvolumes"]
  verbs: ["get", "list", "watch"]
```

## LimitRanges

### Configuración Típica

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: data
spec:
  limits:
  # Por container
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    max:
      cpu: "2"
      memory: "2Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container
  # Por pod
  - max:
      cpu: "4"
      memory: "4Gi"
    type: Pod
```

### Efectos

1. **Sin requests/limits**: Se aplican `default` y `defaultRequest`
2. **Con requests/limits**: Debe estar dentro de `min` y `max`
3. **Validación**: Kubernetes rechaza pods que violan límites

## ResourceQuotas

### Configuración Típica

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
  namespace: data
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "50"
    services: "20"
```

### Límites Comunes

- **CPU/Memory**: Total de requests y limits
- **PVCs**: Número de PersistentVolumeClaims
- **Pods**: Número máximo de pods
- **Services**: Número máximo de servicios
- **ConfigMaps/Secrets**: Límites de objetos

## Verificación

### Ver Permisos de Usuario

```bash
# Ver permisos de un usuario
kubectl auth can-i get pods --as=user:john.doe -n data

# Ver todos los permisos
kubectl auth can-i --list --as=user:john.doe -n data

# Ver permisos de ServiceAccount
kubectl auth can-i get pods \
  --as=system:serviceaccount:integration:kpis-api-sa \
  -n integration
```

### Ver Roles y Bindings

```bash
# Ver roles en namespace
kubectl get roles -n <namespace>

# Ver role bindings
kubectl get rolebindings -n <namespace>

# Ver detalles
kubectl describe role <name> -n <namespace>
kubectl describe rolebinding <name> -n <namespace>
```

### Ver LimitRanges y Quotas

```bash
# Ver LimitRanges
kubectl get limitranges -n <namespace>

# Ver ResourceQuotas
kubectl get resourcequotas -n <namespace>

# Ver uso actual vs límites
kubectl describe resourcequota <name> -n <namespace>
```

## Troubleshooting

### Usuario no puede crear recursos

```bash
# Verificar permisos
kubectl auth can-i create deployments --as=user:<user> -n <namespace>

# Ver roles asignados
kubectl get rolebindings -n <namespace> -o wide

# Verificar que el usuario está en el binding correcto
kubectl describe rolebinding <name> -n <namespace>
```

### Pod rechazado por recursos

```bash
# Ver mensaje de error
kubectl describe pod <name> -n <namespace> | grep -A 5 Events

# Verificar LimitRange
kubectl describe limitrange -n <namespace>

# Verificar ResourceQuota
kubectl describe resourcequota -n <namespace>
```

### Namespace sin recursos disponibles

```bash
# Ver uso actual
kubectl describe resourcequota -n <namespace>

# Ver recursos solicitados por pods
kubectl top pods -n <namespace>

# Liberar recursos eliminando pods no usados
kubectl get pods -n <namespace> --field-selector=status.phase!=Running
```

## Mejores Prácticas

### RBAC

1. **Principio de menor privilegio**: Mínimos permisos necesarios
2. **Usar roles predefinidos**: Evitar roles personalizados cuando sea posible
3. **Revisar permisos regularmente**: Auditar y eliminar permisos innecesarios
4. **Documentar excepciones**: Mantener registro de por qué se otorgaron permisos especiales
5. **Service Accounts dedicados**: Un SA por aplicación, no compartir

### Resource Management

1. **Definir límites siempre**: Nunca dejar recursos sin límites
2. **Requests = Limits inicialmente**: Para evitar overcommit
3. **Revisar quotas regularmente**: Ajustar según uso real
4. **Monitorear uso**: Alertar cuando se acerca a límites
5. **Documentar decisiones**: Por qué se eligieron ciertos límites

## Integración con Gatekeeper

Estas políticas se complementan con Gatekeeper (ver `security/policies/README.md`):
- **RBAC**: Controla quién puede hacer qué
- **Gatekeeper**: Asegura que los recursos cumplen políticas
- **LimitRanges/Quotas**: Controla uso de recursos

## Referencias

- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)

