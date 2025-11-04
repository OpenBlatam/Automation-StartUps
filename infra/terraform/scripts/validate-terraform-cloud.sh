#!/bin/bash
# Validate configuration for Terraform Cloud/Enterprise
# Checks for compatibility and best practices
#
# Usage: ./validate-terraform-cloud.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "☁️  Terraform Cloud Validation"
echo ""

ISSUES=0
WARNINGS=0
PASSED=0

# Check for remote backend
echo "Checking backend configuration..."
if grep -q "cloud {" *.tf backend*.tf 2>/dev/null; then
    echo -e "${GREEN}✓ Terraform Cloud backend configured${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ No Terraform Cloud backend found${NC}"
    echo "  To use Terraform Cloud, add:"
    echo '  terraform {'
    echo '    cloud {'
    echo '      organization = "your-org"'
    echo '      workspaces {'
    echo '        name = "your-workspace"'
    echo '      }'
    echo '    }'
    echo '  }'
    WARNINGS=$((WARNINGS + 1))
fi

# Check for workspaces
echo ""
echo "Checking workspace usage..."
WORKSPACE_COUNT=$(terraform workspace list 2>/dev/null | wc -l || echo "0")
if [ "$WORKSPACE_COUNT" -gt 1 ]; then
    echo -e "${YELLOW}⚠ Multiple workspaces detected ($WORKSPACE_COUNT)${NC}"
    echo "  Terraform Cloud uses workspace-based isolation"
    echo "  Consider migrating to separate workspaces"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ Workspace usage compatible${NC}"
    PASSED=$((PASSED + 1))
fi

# Check for sensitive variables
echo ""
echo "Checking variable configuration..."
SENSITIVE_VARS=$(grep -h "^variable " *.tf 2>/dev/null | grep "sensitive\s*=\s*true" | wc -l || echo "0")
if [ "$SENSITIVE_VARS" -gt 0 ]; then
    echo -e "${GREEN}✓ Sensitive variables properly marked ($SENSITIVE_VARS)${NC}"
    echo "  These will be stored securely in Terraform Cloud"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ No sensitive variables marked${NC}"
    echo "  Mark sensitive variables for secure storage in Terraform Cloud"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for remote state backend conflicts
echo ""
echo "Checking backend conflicts..."
if grep -q "backend \"s3\"" *.tf backend*.tf 2>/dev/null && grep -q "cloud {" *.tf 2>/dev/null; then
    echo -e "${RED}✗ Conflicting backends (S3 and Cloud)${NC}"
    echo "  Cannot use both S3 backend and Terraform Cloud"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✓ No backend conflicts${NC}"
    PASSED=$((PASSED + 1))
fi

# Check for team collaboration features
echo ""
echo "Checking collaboration features..."
if [ -f ".terraform.lock.hcl" ]; then
    echo -e "${GREEN}✓ Provider lock file present${NC}"
    echo "  Terraform Cloud uses lock files for consistency"
    PASSED=$((PASSED + 1))
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "Validation Summary:"
echo "  ✓ Passed: $PASSED"
echo "  ✗ Issues: $ISSUES"
echo "  ⚠ Warnings: $WARNINGS"
echo ""

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Ready for Terraform Cloud!${NC}"
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo -e "${YELLOW}⚠ Compatible with warnings${NC}"
    exit 0
else
    echo -e "${RED}✗ Issues found - fix before using Terraform Cloud${NC}"
    exit 1
fi
