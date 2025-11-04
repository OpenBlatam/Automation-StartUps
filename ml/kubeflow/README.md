# Kubeflow en Kubernetes

Ruta recomendada:
- Instalar Kubeflow (KF 1.9+) con manifests/kustomize según proveedor (ver documentación oficial de Kubeflow).
- Integrar con KServe (ya presente en este repo) para servir modelos; use MLflow/registry si desea versionado y tracking.
- Autenticación: integre OIDC (Dex o IdP corporativo) para notebooks/pipelines.
- Almacenamiento: S3/ADLS para datasets y artefactos de entrenamiento.

Notas:
- Este repo ya incluye MLflow y KServe; Kubeflow aporta Pipelines, Notebooks, Katib (AutoML) y mayor gobernanza ML.


