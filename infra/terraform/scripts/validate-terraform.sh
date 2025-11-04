#!/bin/bash
# Pre-apply validation script for Terraform configurations
# Validates syntax, format, backend configuration, and security checks
#
# Usage: ./validate-terraform.sh [directory]
# Example: ./validate-terraform.sh
# Example: ./validate-terraform.sh azure

set -e

TERRAFORM_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation results
ERRORS=0
WARNINGS=0

echo "🔍 Validating Terraform configuration..."
echo "Directory: $TERRAFORM_DIR"
echo ""

cd "$BASE_DIR/$TERRAFORM_DIR"

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}✗ Error: Terraform is not installed${NC}"
    exit 1
fi

# 1. Format check
echo "📝 Checking code format..."
if terraform fmt -check -recursive > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Code is properly formatted${NC}"
else
    echo -e "${YELLOW}⚠ Code formatting issues found${NC}"
    echo "Run 'terraform fmt -recursive' to fix"
    WARNINGS=$((WARNINGS + 1))
fi

# 2. Initialize Terraform (required for validation)
echo ""
echo "🔧 Initializing Terraform..."
if terraform init -backend=false > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Terraform initialized${NC}"
else
    echo -e "${RED}✗ Failed to initialize Terraform${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Validate syntax
echo ""
echo "✅ Validating syntax..."
if terraform validate > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Syntax validation passed${NC}"
else
    echo -e "${RED}✗ Syntax validation failed${NC}"
    terraform validate
    ERRORS=$((ERRORS + 1))
fi

# 4. Check for sensitive data
echo ""
echo "🔒 Checking for sensitive data in code..."
SENSITIVE_PATTERNS=(
    "password"
    "secret"
    "api_key"
    "access_key"
    "private_key"
    "token"
)

FOUND_SENSITIVE=false
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if grep -r -i "$pattern" *.tf 2>/dev/null | grep -v "variable\|sensitive\|#\|description" > /dev/null; then
        echo -e "${YELLOW}⚠ Potential sensitive data found: $pattern${NC}"
        FOUND_SENSITIVE=true
        WARNINGS=$((WARNINGS + 1))
    fi
done

if [ "$FOUND_SENSITIVE" = false ]; then
    echo -e "${GREEN}✓ No hardcoded sensitive data detected${NC}"
fi

# 5. Check for required variables
echo ""
echo "📋 Checking required variables..."
REQUIRED_VARS=("environment" "project_name")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "variable \"$var\"" *.tf 2>/dev/null; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ Required variables defined${NC}"
else
    echo -e "${YELLOW}⚠ Missing required variables: ${MISSING_VARS[*]}${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 6. Check backend configuration
echo ""
echo "🔐 Checking backend configuration..."
if [ -d "../backend-configs" ]; then
    BACKEND_CONFIGS=$(ls ../backend-configs/*.hcl 2>/dev/null | wc -l)
    if [ "$BACKEND_CONFIGS" -gt 0 ]; then
        echo -e "${GREEN}✓ Backend configuration files found ($BACKEND_CONFIGS)${NC}"
    else
        echo -e "${YELLOW}⚠ No backend configuration files found${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠ Backend configs directory not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 7. Check for provider versions
echo ""
echo "📦 Checking provider versions..."
if grep -q "required_providers" *.tf 2>/dev/null; then
    echo -e "${GREEN}✓ Provider versions specified${NC}"
else
    echo -e "${YELLOW}⚠ Provider versions not specified${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# 8. Security checks (if checkov/tflint available)
if command -v checkov &> /dev/null; then
    echo ""
    echo "🛡️  Running security checks (checkov)..."
    if checkov -d . --framework terraform --quiet 2>/dev/null; then
        echo -e "${GREEN}✓ Security checks passed${NC}"
    else
        echo -e "${YELLOW}⚠ Security issues detected (run checkov -d . for details)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Validation passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    exit 1
fi



