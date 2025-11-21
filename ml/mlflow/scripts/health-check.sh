#!/bin/bash
# MLflow Health Check Script
# Verifica el estado de MLflow y sus dependencias

set -e

NAMESPACE="${MLFLOW_NAMESPACE:-ml}"
MLFLOW_SERVICE="${MLFLOW_SERVICE:-mlflow}"
TIMEOUT="${TIMEOUT:-30}"

echo "🔍 Checking MLflow Health..."
echo "Namespace: $NAMESPACE"
echo "Service: $MLFLOW_SERVICE"
echo "---"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "❌ Namespace '$NAMESPACE' not found"
    exit 1
fi

# Check if MLflow pods are running
echo "📦 Checking pods..."
PODS=$(kubectl get pods -n "$NAMESPACE" -l app=mlflow --field-selector=status.phase=Running -o name 2>/dev/null | wc -l)
if [ "$PODS" -eq 0 ]; then
    echo "❌ No running MLflow pods found"
    kubectl get pods -n "$NAMESPACE" -l app=mlflow
    exit 1
fi
echo "✅ Found $PODS running pod(s)"

# Check service
echo "🌐 Checking service..."
if ! kubectl get service -n "$NAMESPACE" "$MLFLOW_SERVICE" &>/dev/null; then
    echo "❌ Service '$MLFLOW_SERVICE' not found"
    exit 1
fi
echo "✅ Service exists"

# Check health endpoint
echo "💚 Checking health endpoint..."
HEALTH_URL=$(kubectl get service -n "$NAMESPACE" "$MLFLOW_SERVICE" -o jsonpath='{.metadata.annotations.mlflow\.example\.com/health-url}' 2>/dev/null || echo "")
if [ -z "$HEALTH_URL" ]; then
    # Try to port-forward and check
    kubectl port-forward -n "$NAMESPACE" service/$MLFLOW_SERVICE 5000:5000 &
    PF_PID=$!
    sleep 3
    
    if curl -s --max-time "$TIMEOUT" http://localhost:5000/health | grep -q "healthy\|ok"; then
        echo "✅ Health check passed"
        kill $PF_PID 2>/dev/null || true
    else
        echo "❌ Health check failed"
        kill $PF_PID 2>/dev/null || true
        exit 1
    fi
else
    if curl -s --max-time "$TIMEOUT" "$HEALTH_URL/health" | grep -q "healthy\|ok"; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        exit 1
    fi
fi

# Check PostgreSQL connection (if available)
echo "🗄️  Checking PostgreSQL..."
POSTGRES_POD=$(kubectl get pods -n "$NAMESPACE" -l app=postgresql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [ -n "$POSTGRES_POD" ]; then
    if kubectl exec -n "$NAMESPACE" "$POSTGRES_POD" -- pg_isready -U mlflow &>/dev/null; then
        echo "✅ PostgreSQL is ready"
    else
        echo "⚠️  PostgreSQL might not be ready"
    fi
else
    echo "⚠️  PostgreSQL pod not found (might be external)"
fi

# Check S3 access (if AWS credentials are available)
echo "☁️  Checking S3 access..."
if kubectl exec -n "$NAMESPACE" deployment/$MLFLOW_SERVICE -- aws s3 ls s3://biz-datalake-dev/mlflow/ &>/dev/null; then
    echo "✅ S3 access working"
else
    echo "⚠️  S3 access check failed (might be permissions or external config)"
fi

echo "---"
echo "✅ MLflow health check completed successfully!"

