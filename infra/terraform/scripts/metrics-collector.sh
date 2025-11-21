#!/bin/bash
# Collect infrastructure metrics
# Gathers metrics about Terraform infrastructure for monitoring
#
# Usage: ./metrics-collector.sh [output_format]
# Format: json, prometheus
# Example: ./metrics-collector.sh json

set -e

FORMAT="${1:-json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

echo "📊 Collecting Infrastructure Metrics"
echo "Format: $FORMAT"
echo ""

# Get state
STATE_JSON=$(terraform state pull 2>/dev/null || echo "{}")

if [ "$STATE_JSON" = "{}" ]; then
    echo "No state found."
    exit 1
fi

RESOURCE_COUNT=$(echo "$STATE_JSON" | jq '[.resources[]?] | length' || echo "0")
OUTPUT_COUNT=$(terraform output -json 2>/dev/null | jq 'length' || echo "0")

# Check for drift
PLAN_EXIT=$(terraform plan -detailed-exitcode -no-color > /dev/null 2>&1; echo $? || echo "1")
HAS_DRIFT=0
if [ "$PLAN_EXIT" = "2" ]; then
    HAS_DRIFT=1
fi

# Get resource types breakdown
RESOURCE_TYPES=$(echo "$STATE_JSON" | jq -r '[.resources[]? | .type] | group_by(.) | map({type: .[0], count: length})' 2>/dev/null || echo "[]")

case "$FORMAT" in
    json)
        cat <<EOF | jq '.'
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "metrics": {
    "total_resources": $RESOURCE_COUNT,
    "total_outputs": $OUTPUT_COUNT,
    "has_drift": $HAS_DRIFT,
    "resource_types": $RESOURCE_TYPES,
    "state_size_bytes": $(echo "$STATE_JSON" | wc -c | tr -d ' ')
  }
}
EOF
        ;;
    
    prometheus)
        echo "# Terraform Infrastructure Metrics"
        echo "# HELP terraform_resources_total Total number of Terraform resources"
        echo "# TYPE terraform_resources_total gauge"
        echo "terraform_resources_total $RESOURCE_COUNT"
        echo ""
        echo "# HELP terraform_outputs_total Total number of Terraform outputs"
        echo "# TYPE terraform_outputs_total gauge"
        echo "terraform_outputs_total $OUTPUT_COUNT"
        echo ""
        echo "# HELP terraform_drift_state Whether infrastructure has configuration drift (1=yes, 0=no)"
        echo "# TYPE terraform_drift_state gauge"
        echo "terraform_drift_state $HAS_DRIFT"
        echo ""
        echo "# HELP terraform_state_size_bytes Size of Terraform state file in bytes"
        echo "# TYPE terraform_state_size_bytes gauge"
        echo "terraform_state_size_bytes $(echo "$STATE_JSON" | wc -c | tr -d ' ')"
        ;;
    
    *)
        echo "Error: Unknown format '$FORMAT'"
        echo "Supported formats: json, prometheus"
        exit 1
        ;;
esac

