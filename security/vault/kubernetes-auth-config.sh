#!/bin/bash
# Script de configuración de autenticación Kubernetes para Vault
# Este script configura Vault para autenticar aplicaciones usando Service Accounts de Kubernetes

set -e

# Variables
VAULT_ADDR="${VAULT_ADDR:-http://vault.security.svc.cluster.local:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-root}"  # Cambiar en producción
NAMESPACE="${NAMESPACE:-security}"
KUBERNETES_HOST="${KUBERNETES_HOST:-https://kubernetes.default.svc.cluster.local}"

echo "Configurando autenticación Kubernetes en Vault..."

# Habilitar el auth method de Kubernetes
vault auth enable -path=kubernetes kubernetes

# Obtener el token del Service Account de Vault
SA_TOKEN=$(kubectl get secret -n ${NAMESPACE} -o jsonpath='{.items[?(@.metadata.annotations.kubernetes\.io/service-account\.name=="vault")].data.token}' | base64 -d)

# Obtener el CA del cluster
K8S_CA_CERT=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.certificate-authority-data}' | base64 -d)

# Configurar el auth method
vault write auth/kubernetes/config \
  token_reviewer_jwt="${SA_TOKEN}" \
  kubernetes_host="${KUBERNETES_HOST}" \
  kubernetes_ca_cert="${K8S_CA_CERT}"

echo "Configurando roles de Kubernetes..."

# Rol para External Secrets Operator
vault write auth/kubernetes/role/external-secrets-operator \
  bound_service_account_names=externalsecrets-vault-sa \
  bound_service_account_namespaces=security \
  policies=external-secrets-policy \
  ttl=1h

# Rol para Airflow workers
vault write auth/kubernetes/role/airflow-worker \
  bound_service_account_names=airflow-worker \
  bound_service_account_namespaces=data \
  policies=airflow-policy \
  ttl=24h

# Rol para workflows
vault write auth/kubernetes/role/workflow-service \
  bound_service_account_names=kestra,camunda-worker,flowable \
  bound_service_account_namespaces=workflows \
  policies=workflow-policy \
  ttl=24h

echo "Aplicando políticas..."

# Cargar políticas desde archivos
vault policy write external-secrets-policy - <<EOF
path "secret/data/*" {
  capabilities = ["read"]
}
path "secret/metadata/*" {
  capabilities = ["list", "read"]
}
EOF

vault policy write airflow-policy - <<EOF
path "secret/data/airflow/*" {
  capabilities = ["read"]
}
path "secret/data/crm/*" {
  capabilities = ["read"]
}
path "secret/data/databases/*" {
  capabilities = ["read"]
}
path "secret/data/notifications/*" {
  capabilities = ["read"]
}
EOF

vault policy write workflow-policy - <<EOF
path "secret/data/bpm/*" {
  capabilities = ["read"]
}
path "secret/data/rpa/*" {
  capabilities = ["read"]
}
path "secret/data/messaging/*" {
  capabilities = ["read"]
}
path "secret/data/ai/*" {
  capabilities = ["read"]
}
EOF

echo "Configuración completada!"
echo "Para inicializar Vault en producción, ejecuta: vault operator init"


