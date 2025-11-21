#!/bin/bash
# Compare two Terraform plans
# Shows differences between plan files
#
# Usage: ./compare-plans.sh plan1.tfplan plan2.tfplan

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

PLAN1="$1"
PLAN2="$2"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$PLAN1" ] || [ -z "$PLAN2" ]; then
    echo "Usage: ./compare-plans.sh <plan1.tfplan> <plan2.tfplan>"
    exit 1
fi

if [ ! -f "$PLAN1" ]; then
    echo "Error: Plan file not found: $PLAN1"
    exit 1
fi

if [ ! -f "$PLAN2" ]; then
    echo "Error: Plan file not found: $PLAN2"
    exit 1
fi

echo "🔍 Comparing Terraform Plans"
echo "Plan 1: $PLAN1"
echo "Plan 2: $PLAN2"
echo ""

# Show plan summaries
echo "=== Plan 1 Summary ==="
terraform show -json "$PLAN1" 2>/dev/null | jq -r '.resource_changes | length' | xargs echo "Resources: "
echo ""

echo "=== Plan 2 Summary ==="
terraform show -json "$PLAN2" 2>/dev/null | jq -r '.resource_changes | length' | xargs echo "Resources: "
echo ""

# Compare resources
echo "=== Resource Changes Comparison ==="
RES1=$(terraform show -json "$PLAN1" 2>/dev/null | jq -r '.resource_changes[] | "\(.address) \(.change.actions | join(","))"')
RES2=$(terraform show -json "$PLAN2" 2>/dev/null | jq -r '.resource_changes[] | "\(.address) \(.change.actions | join(","))"')

echo ""
echo "Resources only in Plan 1:"
echo "$RES1" | while read -r line; do
    RES_ADDR=$(echo "$line" | cut -d' ' -f1)
    if ! echo "$RES2" | grep -q "^$RES_ADDR"; then
        echo -e "${YELLOW}  - $RES_ADDR${NC}"
    fi
done

echo ""
echo "Resources only in Plan 2:"
echo "$RES2" | while read -r line; do
    RES_ADDR=$(echo "$line" | cut -d' ' -f1)
    if ! echo "$RES1" | grep -q "^$RES_ADDR"; then
        echo -e "${YELLOW}  + $RES_ADDR${NC}"
    fi
done

echo ""
echo "✅ Comparison complete"

