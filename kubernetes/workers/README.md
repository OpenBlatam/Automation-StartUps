# Workers - Auto-escalado

Esta carpeta contiene configuraciones de Horizontal Pod Autoscaler (HPA) para workers que procesan tareas en segundo plano.

## Archivos

- `airflow-worker-hpa.yaml`: Auto-escalado para workers de Airflow (Celery)
- `camunda-worker-hpa.yaml`: Auto-escalado para workers de Camunda

## Aplicar HPA

```bash
# Para workers de Airflow
kubectl apply -f kubernetes/workers/airflow-worker-hpa.yaml

# Para workers de Camunda
kubectl apply -f kubernetes/workers/camunda-worker-hpa.yaml
```

## Verificar Estado

```bash
# Ver todos los HPA
kubectl get hpa -A

# Ver detalles de un HPA específico
kubectl describe hpa airflow-worker-hpa -n data

# Ver métricas actuales
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/namespaces/data/pods"
```

## Notas

- Los HPA requieren el Metrics Server instalado en el cluster
- Para métricas personalizadas (como `celery_queue_length`), se necesita un Adapter de métricas personalizadas (Prometheus Adapter)
- Ajustar `minReplicas`, `maxReplicas` y umbrales según carga esperada

Para más información, ver [docs/ESCALABILIDAD.md](../../docs/ESCALABILIDAD.md).


