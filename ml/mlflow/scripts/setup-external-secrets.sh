#!/bin/bash
# Script para configurar External Secrets para MLflow
# Requiere: External Secrets Operator instalado

set -e

NAMESPACE="${MLFLOW_NAMESPACE:-ml}"
SECRET_NAME="${SECRET_NAME:-mlflow-secrets}"

echo "🔐 Setting up External Secrets for MLflow..."
echo "Namespace: $NAMESPACE"
echo "---"

# Check if External Secrets Operator is installed
if ! kubectl get crd externalsecrets.external-secrets.io &>/dev/null; then
    echo "❌ External Secrets Operator not found. Install it first:"
    echo "   helm repo add external-secrets https://charts.external-secrets.io"
    echo "   helm install external-secrets external-secrets/external-secrets"
    exit 1
fi

echo "✅ External Secrets Operator found"

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Example: AWS Secrets Manager
cat <<EOF | kubectl apply -f -
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mlflow-postgres-secret
  namespace: $NAMESPACE
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: mlflow-postgres-secret
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: mlflow/postgres/password
        property: password
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mlflow-s3-secret
  namespace: $NAMESPACE
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: mlflow-s3-secret
    creationPolicy: Owner
  data:
    - secretKey: access-key-id
      remoteRef:
        key: mlflow/s3/access-key
        property: access-key-id
    - secretKey: secret-access-key
      remoteRef:
        key: mlflow/s3/access-key
        property: secret-access-key
EOF

echo "✅ External Secrets created"
echo ""
echo "⚠️  Note: Make sure you have:"
echo "   1. AWS Secrets Manager with keys: mlflow/postgres/password, mlflow/s3/access-key"
echo "   2. SecretStore configured (see security/secrets/externalsecrets-aws.yaml)"
echo "   3. IAM permissions for External Secrets Operator to read from Secrets Manager"
echo ""
echo "Verify secrets:"
echo "   kubectl get externalsecrets -n $NAMESPACE"
echo "   kubectl get secrets -n $NAMESPACE"

