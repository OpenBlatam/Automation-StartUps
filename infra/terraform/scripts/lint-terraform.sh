#!/bin/bash
# Run linters on Terraform code (TFLint, Checkov)
#
# Usage: ./lint-terraform.sh [directory]
# Example: ./lint-terraform.sh
# Example: ./lint-terraform.sh azure

set -e

TERRAFORM_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$BASE_DIR/$TERRAFORM_DIR"

echo "🔍 Linting Terraform code..."
echo "Directory: $TERRAFORM_DIR"
echo ""

ERRORS=0

# 1. TFLint
if command -v tflint &> /dev/null; then
    echo "Running TFLint..."
    if tflint --init && tflint; then
        echo -e "${GREEN}✓ TFLint passed${NC}"
    else
        echo -e "${RED}✗ TFLint found issues${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠ TFLint not installed (skipping)${NC}"
    echo "  Install: https://github.com/terraform-linters/tflint"
fi

echo ""

# 2. Checkov
if command -v checkov &> /dev/null; then
    echo "Running Checkov security scan..."
    if checkov -d . --framework terraform --soft-fail --quiet; then
        echo -e "${GREEN}✓ Checkov passed${NC}"
    else
        echo -e "${YELLOW}⚠ Checkov found issues (see details above)${NC}"
        # Don't count as error in soft-fail mode
    fi
else
    echo -e "${YELLOW}⚠ Checkov not installed (skipping)${NC}"
    echo "  Install: pip install checkov"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Linting completed${NC}"
    exit 0
else
    echo -e "${RED}✗ Linting found $ERRORS issue(s)${NC}"
    exit 1
fi



