# Network Policies - Seguridad de Red

Esta carpeta contiene las Network Policies de Kubernetes para controlar el tráfico de red entre pods y namespaces.

## Descripción

Las Network Policies implementan un firewall a nivel de pod, permitiendo o denegando tráfico basado en:
- **Namespace**: Origen/destino del tráfico
- **Labels**: Selectores basados en labels
- **Port**: Puertos y protocolos específicos
- **CIDR**: Rangos de IP externos

## Estructura

```
networkpolicies/
└── baseline.yaml    # Política base: deny-all con excepciones mínimas
```

## Política Base

**Archivo**: `baseline.yaml`

Implementa el principio de **deny-all** con excepciones mínimas:

- ✅ **Permite DNS**: Tráfico a CoreDNS (puerto 53)
- ✅ **Permite Ingress**: Tráfico desde Ingress Controller
- ❌ **Deniega todo lo demás**: Default deny-all

**Aplicar**:

```bash
kubectl apply -f security/networkpolicies/baseline.yaml

# Verificar
kubectl get networkpolicies -A
```

## Arquitectura de Seguridad

### Principio de Menor Privilegio

Por defecto, **todos los pods están aislados**:
- No pueden comunicarse entre sí
- No pueden comunicarse con pods en otros namespaces
- Solo excepciones explícitas son permitidas

### Permitir Tráfico Necesario

Para permitir comunicación, crea Network Policies específicas:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-kpis-api-to-db
  namespace: integration
spec:
  podSelector:
    matchLabels:
      app: kpis-api
  policyTypes:
  - Egress
  egress:
  # Permitir acceso a PostgreSQL
  - to:
    - namespaceSelector:
        matchLabels:
          name: data
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
  # Permitir DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

## Ejemplos por Componente

### Airflow - Acceso a Base de Datos

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: airflow-to-postgres
  namespace: data
spec:
  podSelector:
    matchLabels:
      app: airflow
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
```

### KPIs API - Acceso Externo

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-kpis
  namespace: integration
spec:
  podSelector:
    matchLabels:
      app: kpis-api
  policyTypes:
  - Ingress
  ingress:
  # Permitir desde Ingress Controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3001
```

### Kafka - Comunicación entre Brokers

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kafka-brokers
  namespace: integration
spec:
  podSelector:
    matchLabels:
      strimzi.io/kind: Kafka
      strimzi.io/name: my-cluster-kafka
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Permitir entre brokers
  - from:
    - podSelector:
        matchLabels:
          strimzi.io/kind: Kafka
          strimzi.io/name: my-cluster-kafka
    ports:
    - protocol: TCP
      port: 9092
  # Permitir desde clientes
  - from:
    - namespaceSelector: {}  # Todos los namespaces
    ports:
    - protocol: TCP
      port: 9092
  egress:
  # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

## Verificación

### Ver Network Policies

```bash
# Ver todas las políticas
kubectl get networkpolicies -A

# Ver detalles
kubectl describe networkpolicy <name> -n <namespace>

# Ver políticas en un namespace
kubectl get networkpolicies -n <namespace>
```

### Probar Conectividad

```bash
# Desde un pod probar conexión
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- \
  curl -v http://service.namespace.svc.cluster.local

# Verificar que el tráfico es bloqueado/permite
kubectl logs -n kube-system <network-plugin-pod> | grep <source-pod>
```

### Verificar Selectores

```bash
# Ver pods que coinciden con selector
kubectl get pods -n <namespace> -l app=kpis-api

# Verificar labels de pods
kubectl get pods -n <namespace> --show-labels
```

## Troubleshooting

### Pod no puede conectarse

```bash
# Verificar que existe Network Policy
kubectl get networkpolicy -n <namespace>

# Verificar selectores coinciden
kubectl get pods -n <namespace> --show-labels

# Verificar que la política permite el tráfico
kubectl describe networkpolicy <name> -n <namespace>

# Verificar logs del CNI plugin
kubectl logs -n kube-system -l k8s-app=cilium  # Si usas Cilium
kubectl logs -n kube-system -l app=calico-node  # Si usas Calico
```

### Política no se aplica

```bash
# Verificar que el CNI soporta Network Policies
kubectl get pods -n kube-system | grep -E "cilium|calico|weave"

# Verificar eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Verificar sintaxis YAML
kubectl apply -f <policy-file> --dry-run=client
```

## Mejores Prácticas

1. **Empezar con deny-all**: Política base que bloquea todo
2. **Permitir incrementalmente**: Agregar excepciones según necesidad
3. **Documentar políticas**: Explicar por qué cada política es necesaria
4. **Probar en desarrollo**: Validar políticas en dev antes de producción
5. **Monitorear bloqueos**: Alertar cuando tráfico legítimo es bloqueado
6. **Revisar regularmente**: Eliminar políticas obsoletas

## Compatibilidad

Las Network Policies requieren un CNI que las soporte:
- ✅ **Calico**
- ✅ **Cilium**
- ✅ **Weave Net**
- ✅ **Antrea**
- ❌ **Flannel** (no soporta Network Policies)

Verificar el CNI del cluster:

```bash
kubectl get pods -n kube-system | grep -E "cilium|calico|weave"
```

## Referencias

- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Network Policy Examples](https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/)
- [Cilium Network Policies](https://docs.cilium.io/en/stable/policy/)

