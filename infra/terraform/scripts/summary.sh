#!/bin/bash
# Comprehensive Terraform summary
# Shows overview of infrastructure, state, and configuration
#
# Usage: ./summary.sh [provider]
# Example: ./summary.sh aws

set -e

PROVIDER="${1:-aws}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Terraform Infrastructure Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Terraform Version
echo "📦 Terraform:"
terraform version | head -1
echo ""

# State Information
echo "📊 State Information:"
if terraform state list > /dev/null 2>&1; then
    RESOURCE_COUNT=$(terraform state list | wc -l | tr -d ' ')
    echo "  Resources in state: $RESOURCE_COUNT"
    
    # Count by type
    echo ""
    echo "  Resources by type:"
    terraform state list | sed 's/\..*$//' | sort | uniq -c | sort -rn | head -10 | \
    while read count type; do
        echo "    $type: $count"
    done
else
    echo "  State not accessible or empty"
fi
echo ""

# Outputs
echo "📤 Outputs:"
OUTPUT_COUNT=$(terraform output -json 2>/dev/null | jq 'length' || echo "0")
echo "  Total outputs: $OUTPUT_COUNT"
if [ "$OUTPUT_COUNT" -gt 0 ]; then
    echo ""
    echo "  Available outputs:"
    terraform output -json 2>/dev/null | jq -r 'keys[]' | head -10 | \
    while read output; do
        echo "    - $output"
    done
fi
echo ""

# Configuration Drift
echo "🔄 Configuration Status:"
PLAN_OUTPUT=$(terraform plan -detailed-exitcode -no-color 2>&1 || true)
if echo "$PLAN_OUTPUT" | grep -q "No changes"; then
    echo -e "  ${GREEN}✓ No drift detected${NC}"
elif echo "$PLAN_OUTPUT" | grep -q "will be"; then
    CREATES=$(echo "$PLAN_OUTPUT" | grep -c "will be created" || echo "0")
    UPDATES=$(echo "$PLAN_OUTPUT" | grep -c "will be updated\|must be replaced" || echo "0")
    DELETES=$(echo "$PLAN_OUTPUT" | grep -c "will be destroyed" || echo "0")
    echo -e "  ${YELLOW}⚠ Drift detected: +$CREATES ~$UPDATES -$DELETES${NC}"
else
    echo "  Could not determine status"
fi
echo ""

# Backend Information
echo "🔐 Backend:"
if [ -d ".terraform" ]; then
    BACKEND_INFO=$(terraform show -json 2>/dev/null | jq -r '.values.backend.type' || echo "unknown")
    if [ "$BACKEND_INFO" != "null" ] && [ "$BACKEND_INFO" != "unknown" ]; then
        echo "  Type: $BACKEND_INFO"
    else
        echo "  Type: Local"
    fi
else
    echo "  Not initialized"
fi
echo ""

# Provider Information
echo "☁️  Provider: $PROVIDER"
if [ "$PROVIDER" = "aws" ]; then
    if aws sts get-caller-identity > /dev/null 2>&1; then
        ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        echo "  Account: $ACCOUNT"
    fi
elif [ "$PROVIDER" = "azure" ]; then
    if az account show > /dev/null 2>&1; then
        SUBSCRIPTION=$(az account show --query name --output tsv 2>/dev/null)
        echo "  Subscription: $SUBSCRIPTION"
    fi
fi
echo ""

# Files
echo "📁 Configuration Files:"
TF_FILES=$(ls *.tf 2>/dev/null | wc -l | tr -d ' ')
echo "  Terraform files: $TF_FILES"
echo ""

# Quick Actions
echo "🚀 Quick Actions:"
echo "  make tf-plan              - Plan changes"
echo "  make tf-apply             - Apply changes"
echo "  make tf-state-list        - List resources"
echo "  make tf-health-check      - Health check"
echo "  make tf-drift-detection   - Check drift"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

