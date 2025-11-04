# Seguridad y Gobernanza

- IAM: defina grupos (`platform-ops`, `viewers`) mapeados a RBAC (`security/kubernetes/rbac-baseline.yaml`).
- Políticas: use Gatekeeper/OPA (`security/policies/gatekeeper/constraints.yaml`).
- Secretos: usar AWS Secrets Manager/Azure Key Vault e inyectar con CSI Driver.
- Auditoría: habilite audit logs del cluster y del cloud provider; rote y archive en el data lake.
- CI/CD: firmas de imágenes (Cosign), escaneo (Trivy), políticas de admisión.


