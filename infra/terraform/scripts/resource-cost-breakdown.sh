#!/bin/bash
# Detailed cost breakdown by resource type
# Provides cost estimates per resource type
#
# Usage: ./resource-cost-breakdown.sh [provider]
# Example: ./resource-cost-breakdown.sh aws

set -e

PROVIDER="${1:-aws}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

echo "💰 Resource Cost Breakdown"
echo "Provider: $PROVIDER"
echo ""
echo "⚠️  Note: These are rough estimates. Actual costs vary by usage."
echo ""

# Get resources
STATE_JSON=$(terraform state pull 2>/dev/null || echo "{}")

if [ "$STATE_JSON" = "{}" ]; then
    echo "No state found."
    exit 0
fi

# Cost estimates per resource type (monthly USD, approximate)
declare -A AWS_COSTS
AWS_COSTS[aws_instance]="50"
AWS_COSTS[aws_db_instance]="100"
AWS_COSTS[aws_lb]="20"
AWS_COSTS[aws_nat_gateway]="32"
AWS_COSTS[aws_s3_bucket]="1"
AWS_COSTS[module.eks]="72"
AWS_COSTS[aws_eks_cluster]="72"

declare -A AZURE_COSTS
AZURE_COSTS[azurerm_virtual_machine]="50"
AZURE_COSTS[azurerm_sql_database]="100"
AZURE_COSTS[azurerm_lb]="20"
AZURE_COSTS[azurerm_kubernetes_cluster]="73"
AZURE_COSTS[azurerm_storage_account]="5"
AZURE_COSTS[azurerm_container_registry]="5"

echo "Resource Type | Count | Est. Monthly Cost"
echo "──────────────|───────|──────────────────"

TOTAL_COST=0

if [ "$PROVIDER" = "aws" ]; then
    COSTS=("${!AWS_COSTS[@]}")
elif [ "$PROVIDER" = "azure" ]; then
    COSTS=("${!AZURE_COSTS[@]}")
fi

# Group resources by type
RESOURCE_TYPES=$(echo "$STATE_JSON" | jq -r '[.resources[]? | .type] | group_by(.) | map({type: .[0], count: length})' 2>/dev/null || echo "[]")

echo "$RESOURCE_TYPES" | jq -r '.[] | "\(.type) | \(.count) | \$\(.count * 50)"' | while read line; do
    TYPE=$(echo "$line" | awk -F' | ' '{print $1}')
    COUNT=$(echo "$line" | awk -F' | ' '{print $2}')
    
    if [ "$PROVIDER" = "aws" ] && [ -n "${AWS_COSTS[$TYPE]}" ]; then
        COST_PER_UNIT="${AWS_COSTS[$TYPE]}"
    elif [ "$PROVIDER" = "azure" ] && [ -n "${AZURE_COSTS[$TYPE]}" ]; then
        COST_PER_UNIT="${AZURE_COSTS[$TYPE]}"
    else
        COST_PER_UNIT="50"  # Default estimate
    fi
    
    TOTAL=$(echo "$COUNT * $COST_PER_UNIT" | bc)
    TOTAL_COST=$(echo "$TOTAL_COST + $TOTAL" | bc)
    
    printf "%-30s | %5s | $%8s\n" "$TYPE" "$COUNT" "$TOTAL"
done

echo "──────────────|───────|──────────────────"
echo "Total Estimated Monthly Cost: \$$TOTAL_COST USD"
echo ""
echo "For accurate costs, use your cloud provider's calculator:"
if [ "$PROVIDER" = "aws" ]; then
    echo "  https://calculator.aws.amazon.com/"
else
    echo "  https://azure.microsoft.com/pricing/calculator/"
fi

