#!/bin/bash
# Pre-apply safety checks for Terraform
# Ensures safe conditions before applying changes
#
# Usage: ./pre-apply-check.sh [environment]
# Example: ./pre-apply-check.sh prod

set -e

ENVIRONMENT="${1:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 Pre-apply Safety Checks"
echo "Environment: $ENVIRONMENT"
echo ""

cd "$TERRAFORM_DIR"

CHECKS_PASSED=0
CHECKS_FAILED=0

# 0. Check for manual lock
LOCK_FILE="../.terraform.lock"
if [ -f "$LOCK_FILE" ]; then
    echo -e "${RED}✗ State is manually locked${NC}"
    echo ""
    cat "$LOCK_FILE"
    echo ""
    echo "State is locked for maintenance. Unlock first:"
    echo "  ../scripts/unlock-state.sh"
    exit 1
fi

# 1. Check if working on production
if [ "$ENVIRONMENT" = "prod" ]; then
    echo -e "${YELLOW}⚠ PRODUCTION ENVIRONMENT DETECTED${NC}"
    read -p "Are you absolutely sure you want to apply to PRODUCTION? (type 'yes' to continue): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# 2. Check for uncommitted changes
echo ""
echo "📝 Checking for uncommitted changes..."
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠ Uncommitted changes detected${NC}"
        git status --short
        read -p "Continue anyway? (y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Aborted."
            exit 1
        fi
    else
        echo -e "${GREEN}✓ No uncommitted changes${NC}"
    fi
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# 3. Verify backend is configured
echo ""
echo "🔐 Verifying backend configuration..."
if terraform init -backend=true -reconfigure > /dev/null 2>&1; then
    BACKEND_TYPE=$(terraform show -json 2>/dev/null | jq -r '.values.backend.type' 2>/dev/null || echo "unknown")
    if [ "$BACKEND_TYPE" != "unknown" ] && [ "$BACKEND_TYPE" != "local" ]; then
        echo -e "${GREEN}✓ Remote backend configured ($BACKEND_TYPE)${NC}"
    else
        echo -e "${YELLOW}⚠ Using local backend (not recommended for production)${NC}"
        if [ "$ENVIRONMENT" = "prod" ]; then
            echo -e "${RED}✗ Production requires remote backend!${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗ Failed to initialize backend${NC}"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 4. Run validation
echo ""
echo "✅ Running Terraform validation..."
if terraform validate > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Configuration is valid${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗ Configuration validation failed${NC}"
    terraform validate
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 5. Check state is unlocked
echo ""
echo "🔓 Checking state lock..."
if terraform plan -out=/dev/null > /dev/null 2>&1; then
    echo -e "${GREEN}✓ State is not locked${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    ERROR_OUT=$(terraform plan -out=/dev/null 2>&1 || true)
    if echo "$ERROR_OUT" | grep -q "locked"; then
        echo -e "${RED}✗ State is locked${NC}"
        echo "If you're sure no other operation is running, use:"
        echo "  terraform force-unlock LOCK_ID"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    else
        echo -e "${YELLOW}⚠ Plan check failed (this may be normal)${NC}"
    fi
fi

# 6. Show plan summary
echo ""
echo "📊 Generating plan summary..."
PLAN_OUTPUT=$(terraform plan -out=/dev/null -no-color 2>&1 || true)
if echo "$PLAN_OUTPUT" | grep -q "No changes"; then
    echo -e "${GREEN}✓ No changes to apply${NC}"
elif echo "$PLAN_OUTPUT" | grep -q "will be created\|will be destroyed\|will be replaced"; then
    CHANGES=$(echo "$PLAN_OUTPUT" | grep -c "will be\|must be replaced" || echo "0")
    echo -e "${YELLOW}⚠ $CHANGES resource change(s) detected${NC}"
    echo ""
    echo "Preview of changes:"
    terraform plan -out=/dev/null -no-color | grep -E "will be|must be" | head -10
    echo ""
    echo "Review the full plan before applying!"
else
    echo -e "${YELLOW}⚠ Could not parse plan output${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "Pre-apply Check Summary:"
echo "  Passed: $CHECKS_PASSED"
echo "  Failed: $CHECKS_FAILED"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All safety checks passed!${NC}"
    echo ""
    echo "You can now safely run:"
    echo "  terraform apply"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review and fix before applying.${NC}"
    exit 1
fi


