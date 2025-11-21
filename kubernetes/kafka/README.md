# Kafka - Event Streaming Platform

Esta carpeta contiene la configuración de Apache Kafka para event streaming y messaging asíncrono en la plataforma.

## Descripción

Kafka proporciona un sistema distribuido de streaming de eventos que permite:
- **Event Streaming**: Flujo de datos en tiempo real
- **Message Queue**: Colas de mensajes para comunicación asíncrona
- **Event Sourcing**: Almacenamiento de eventos para auditoría
- **Integration Hub**: Integración entre servicios mediante eventos

## Estructura

```
kafka/
├── strimzi-kafka.yaml     # Operador Strimzi para Kafka
├── connect/               # Kafka Connect para integraciones
│   ├── deployment.yaml
│   └── s3-sink.json
└── topics/                # Definición de tópicos
    └── orders.yaml
```

## Componentes

### Strimzi Kafka Operator

Operador de Kubernetes para gestionar clusters de Kafka.

**Archivo**: `strimzi-kafka.yaml`

**Características**:
- Provisioning automático de clusters
- Escalado automático
- Actualizaciones sin downtime
- Gestión de tópicos y usuarios

**Instalación**:

```bash
# Aplicar el operador
kubectl apply -f kubernetes/kafka/strimzi-kafka.yaml

# Verificar instalación
kubectl get pods -n kafka-system

# Verificar que el operador está corriendo
kubectl get deployment strimzi-cluster-operator -n kafka-system
```

### Kafka Connect

Kafka Connect permite integrar Kafka con sistemas externos mediante conectores.

**Archivo**: `connect/deployment.yaml`

**Conectores disponibles**:
- **S3 Sink**: Exporta mensajes de Kafka a S3 (ver `connect/s3-sink.json`)

**Uso**:

```bash
# Desplegar Kafka Connect
kubectl apply -f kubernetes/kafka/connect/deployment.yaml

# Crear conector S3
kubectl apply -f kubernetes/kafka/connect/s3-sink.json

# Listar conectores
kubectl get kafkaconnector -n integration
```

### Tópicos

Los tópicos son categorías/streams de mensajes.

**Ejemplo**: `topics/orders.yaml`

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: orders
  namespace: integration
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000  # 7 días
    segment.ms: 86400000     # 1 día
```

**Crear tópico**:

```bash
kubectl apply -f kubernetes/kafka/topics/orders.yaml

# Verificar
kubectl get kafkatopic -n integration
```

## Uso

### Producir Mensajes

Desde aplicaciones Python:

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka-broker.integration.svc.cluster.local:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('orders', {
    'order_id': '12345',
    'amount': 99.99,
    'timestamp': '2025-01-15T10:00:00Z'
})
```

### Consumir Mensajes

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['kafka-broker.integration.svc.cluster.local:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='order-processor'
)

for message in consumer:
    order = message.value
    process_order(order)
```

### Desde Kestra

```yaml
- id: produce_to_kafka
  type: io.kestra.plugin.kafka.Produce
  broker: kafka-broker.integration.svc:9092
  topic: orders
  key: "{{ outputs.previous.order_id }}"
  value: "{{ outputs.previous.data | json }}"
```

## Integración con Componentes

### Airflow

Los DAGs de Airflow pueden producir/consumir mensajes:

```python
from airflow.providers.apache.kafka.operators.kafka import KafkaProducerOperator

produce_task = KafkaProducerOperator(
    task_id='produce_order_event',
    kafka_config_id='kafka_default',
    topic='orders',
    producer_function='my_producer_function',
)
```

### Integración con Data Lake

Kafka Connect S3 Sink exporta mensajes a S3:

```json
{
  "name": "s3-sink-orders",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "orders",
    "s3.bucket.name": "biz-datalake-dev",
    "s3.region": "us-east-1",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "1000"
  }
}
```

## Tópicos Principales

### `orders`

Eventos de pedidos/órdenes:
- Creación de orden
- Actualización de estado
- Cancelación

### `leads`

Eventos de leads:
- Nuevo lead
- Actualización de lead
- Conversión de lead

### `payments`

Eventos de pagos:
- Pago recibido
- Pago procesado
- Reembolso

### `etl-events`

Eventos de pipelines ETL:
- Inicio de pipeline
- Finalización exitosa
- Error en pipeline

## Monitoreo

### Métricas de Kafka

Strimzi expone métricas de Prometheus:

```bash
# Ver métricas
curl http://kafka-broker.integration.svc:9404/metrics

# Métricas clave:
# - kafka_server_brokertopicmetrics_bytesin_total
# - kafka_server_brokertopicmetrics_bytesout_total
# - kafka_server_brokertopicmetrics_messagesin_total
```

### ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kafka
  namespace: integration
spec:
  selector:
    matchLabels:
      strimzi.io/kind: Kafka
  endpoints:
    - port: tcp-prometheus
      interval: 30s
```

## Seguridad

### TLS/SSL

Habilitar TLS para comunicación encriptada:

```yaml
# En KafkaUser o KafkaCluster
spec:
  authentication:
    type: tls
```

### ACLs (Access Control Lists)

Controlar acceso a tópicos:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaUser
metadata:
  name: order-processor
  namespace: integration
spec:
  authentication:
    type: tls
  authorization:
    type: simple
    acls:
      - resource:
          type: topic
          name: orders
          patternType: literal
        operations:
          - Read
          - Write
```

## Troubleshooting

### Ver estado del cluster

```bash
# Ver pods de Kafka
kubectl get pods -n integration -l strimzi.io/kind=Kafka

# Ver logs
kubectl logs -n integration kafka-broker-0

# Describir cluster
kubectl describe kafka my-cluster -n integration
```

### Verificar tópicos

```bash
# Listar tópicos
kubectl get kafkatopic -n integration

# Ver detalles
kubectl describe kafkatopic orders -n integration
```

### Problemas de conectividad

```bash
# Verificar servicio
kubectl get svc -n integration | grep kafka

# Probar conectividad desde pod
kubectl run -it --rm kafka-client --image=quay.io/strimzi/kafka:latest \
  --restart=Never -- bin/kafka-console-producer.sh \
  --bootstrap-server kafka-broker.integration.svc:9092 \
  --topic test
```

### Ver mensajes

```bash
# Consumir mensajes para debug
kubectl run -it --rm kafka-consumer --image=quay.io/strimzi/kafka:latest \
  --restart=Never -- bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-broker.integration.svc:9092 \
  --topic orders \
  --from-beginning
```

## Mejores Prácticas

1. **Particiones**: Configurar particiones según throughput esperado (3-6 común)
2. **Réplicas**: Mínimo 3 réplicas para alta disponibilidad
3. **Retención**: Configurar retención según necesidades de negocio
4. **Schema Registry**: Usar Schema Registry para validación de schemas (Avro/JSON)
5. **Monitoring**: Configurar alertas para lag de consumidores
6. **Security**: Habilitar TLS y ACLs en producción
7. **Backup**: Considerar replicación a otro cluster para DR

## Referencias

- [Strimzi Documentation](https://strimzi.io/documentation/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Connect](https://kafka.apache.org/documentation/#connect)
- [Confluent S3 Sink Connector](https://docs.confluent.io/kafka-connect-s3-sink/current/)

