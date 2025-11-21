#!/bin/bash
# Check Terraform and provider dependencies
# Verifies all required tools and versions
#
# Usage: ./check-dependencies.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Checking Terraform Dependencies"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Check Terraform
echo "Checking Terraform..."
if command -v terraform &> /dev/null; then
    TF_VERSION=$(terraform version -json 2>/dev/null | jq -r '.terraform_version' || terraform version | head -1)
    REQUIRED_VERSION="1.6.0"
    
    if terraform version | grep -q "$REQUIRED_VERSION" || terraform version | grep -q "1\.[6-9]\|2\."; then
        echo -e "${GREEN}✓ Terraform installed: $TF_VERSION${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ Terraform version may be outdated${NC}"
        echo "  Installed: $TF_VERSION"
        echo "  Recommended: >= $REQUIRED_VERSION"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗ Terraform not installed${NC}"
    echo "  Install: https://www.terraform.io/downloads"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check jq (for JSON parsing)
echo ""
echo "Checking jq..."
if command -v jq &> /dev/null; then
    JQ_VERSION=$(jq --version)
    echo -e "${GREEN}✓ jq installed: $JQ_VERSION${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ jq not installed (optional but recommended)${NC}"
    echo "  Install: brew install jq (macOS) or apt-get install jq (Linux)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check AWS CLI (if using AWS)
echo ""
echo "Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1)
    echo -e "${GREEN}✓ AWS CLI installed: $AWS_VERSION${NC}"
    
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        echo -e "${GREEN}  ✓ AWS credentials configured (Account: $ACCOUNT)${NC}"
    else
        echo -e "${YELLOW}  ⚠ AWS credentials not configured${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ AWS CLI not installed (required for AWS deployments)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check Azure CLI (if using Azure)
echo ""
echo "Checking Azure CLI..."
if command -v az &> /dev/null; then
    AZ_VERSION=$(az --version | head -1)
    echo -e "${GREEN}✓ Azure CLI installed: $AZ_VERSION${NC}"
    
    if az account show &> /dev/null; then
        SUBSCRIPTION=$(az account show --query name --output tsv 2>/dev/null)
        echo -e "${GREEN}  ✓ Azure credentials configured (Subscription: $SUBSCRIPTION)${NC}"
    else
        echo -e "${YELLOW}  ⚠ Azure not logged in${NC}"
        echo "    Run: az login"
        WARNINGS=$((WARNINGS + 1))
    fi
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ Azure CLI not installed (required for Azure deployments)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check kubectl (optional)
echo ""
echo "Checking kubectl..."
if command -v kubectl &> /dev/null; then
    KUBE_VERSION=$(kubectl version --client --short 2>/dev/null | cut -d' ' -f3)
    echo -e "${GREEN}✓ kubectl installed: $KUBE_VERSION${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ kubectl not installed (optional, for Kubernetes clusters)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check optional tools
echo ""
echo "Checking optional tools..."

if command -v checkov &> /dev/null; then
    CHECKOV_VERSION=$(checkov --version 2>/dev/null | head -1)
    echo -e "${GREEN}✓ checkov installed: $CHECKOV_VERSION${NC}"
else
    echo -e "${YELLOW}  checkov not installed (optional, for security scanning)${NC}"
fi

if command -v infracost &> /dev/null; then
    INFRACOST_VERSION=$(infracost --version 2>/dev/null | head -1)
    echo -e "${GREEN}✓ infracost installed: $INFRACOST_VERSION${NC}"
else
    echo -e "${YELLOW}  infracost not installed (optional, for cost estimation)${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "Dependency Check Summary:"
echo "  ✓ Passed: $CHECKS_PASSED"
echo "  ✗ Failed: $CHECKS_FAILED"
echo "  ⚠ Warnings: $WARNINGS"
echo ""

if [ $CHECKS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All dependencies satisfied!${NC}"
    exit 0
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠ Dependencies check completed with warnings${NC}"
    exit 0
else
    echo -e "${RED}✗ Some required dependencies are missing${NC}"
    exit 1
fi

