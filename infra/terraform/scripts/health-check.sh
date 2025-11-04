#!/bin/bash
# Health check script for Terraform infrastructure
# Verifies that infrastructure is properly configured and accessible
#
# Usage: ./health-check.sh [provider] [environment]
# Example: ./health-check.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🏥 Terraform Infrastructure Health Check"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "$TERRAFORM_DIR/azure" ]; then
    cd "$TERRAFORM_DIR/azure"
fi

CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# 1. Check Terraform is initialized
echo "🔧 Checking Terraform initialization..."
if [ -d ".terraform" ]; then
    echo -e "${GREEN}✓ Terraform initialized${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗ Terraform not initialized${NC}"
    echo "  Run: terraform init"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 2. Check backend configuration
echo ""
echo "🔐 Checking backend configuration..."
if terraform init -backend=true -reconfigure > /dev/null 2>&1; then
    BACKEND_TYPE=$(terraform show -json 2>/dev/null | jq -r '.values.backend.type' 2>/dev/null || echo "local")
    if [ "$BACKEND_TYPE" != "local" ] && [ "$BACKEND_TYPE" != "unknown" ]; then
        echo -e "${GREEN}✓ Remote backend configured ($BACKEND_TYPE)${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ Using local backend${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗ Backend configuration issue${NC}"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 3. Check state accessibility
echo ""
echo "📦 Checking state accessibility..."
if terraform state list > /dev/null 2>&1; then
    STATE_COUNT=$(terraform state list | wc -l)
    echo -e "${GREEN}✓ State accessible ($STATE_COUNT resources)${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗ Cannot access state${NC}"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 4. Check for drift
echo ""
echo "🔄 Checking for infrastructure drift..."
PLAN_OUTPUT=$(terraform plan -no-color 2>&1 || true)
if echo "$PLAN_OUTPUT" | grep -q "No changes"; then
    echo -e "${GREEN}✓ No drift detected${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
elif echo "$PLAN_OUTPUT" | grep -q "will be"; then
    DRIFT_COUNT=$(echo "$PLAN_OUTPUT" | grep -c "will be\|must be" || echo "0")
    echo -e "${YELLOW}⚠ Drift detected ($DRIFT_COUNT changes)${NC}"
    echo "  Run 'terraform plan' to see details"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${YELLOW}⚠ Could not check drift${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 5. Provider-specific checks
echo ""
echo "☁️  Checking provider configuration..."

if [ "$PROVIDER" = "aws" ]; then
    if command -v aws &> /dev/null; then
        if aws sts get-caller-identity > /dev/null 2>&1; then
            ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
            echo -e "${GREEN}✓ AWS credentials valid (Account: $ACCOUNT_ID)${NC}"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
        else
            echo -e "${RED}✗ AWS credentials invalid${NC}"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
        fi
    else
        echo -e "${YELLOW}⚠ AWS CLI not installed${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
elif [ "$PROVIDER" = "azure" ]; then
    if command -v az &> /dev/null; then
        if az account show > /dev/null 2>&1; then
            SUBSCRIPTION=$(az account show --query name --output tsv)
            echo -e "${GREEN}✓ Azure credentials valid (Subscription: $SUBSCRIPTION)${NC}"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
        else
            echo -e "${RED}✗ Azure credentials invalid${NC}"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
        fi
    else
        echo -e "${YELLOW}⚠ Azure CLI not installed${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 6. Check outputs availability
echo ""
echo "📊 Checking outputs..."
OUTPUT_COUNT=$(terraform output -json 2>/dev/null | jq 'length' 2>/dev/null || echo "0")
if [ "$OUTPUT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Outputs available ($OUTPUT_COUNT outputs)${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ No outputs available (infrastructure may not be deployed)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo -e "${BLUE}Health Check Summary${NC}"
echo "  Passed: $CHECKS_PASSED"
echo "  Failed: $CHECKS_FAILED"
echo "  Warnings: $WARNINGS"
echo ""

if [ $CHECKS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All health checks passed!${NC}"
    exit 0
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠ Health checks completed with warnings${NC}"
    exit 0
else
    echo -e "${RED}✗ Health check failed${NC}"
    exit 1
fi



