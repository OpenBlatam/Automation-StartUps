#!/bin/bash
# Security audit script for Terraform configurations
# Checks for common security issues and misconfigurations
#
# Usage: ./audit-security.sh [directory]
# Example: ./audit-security.sh

set -e

TERRAFORM_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$BASE_DIR/$TERRAFORM_DIR"

echo "🔒 Terraform Security Audit"
echo "Directory: $TERRAFORM_DIR"
echo ""

ISSUES=0
WARNINGS=0
CHECKS_PASSED=0

# 1. Check for hardcoded secrets
echo "🔍 Checking for hardcoded secrets..."
SECRET_PATTERNS=(
    "password\s*=\s*[\"'][^\"']+[\"']"
    "secret\s*=\s*[\"'][^\"']+[\"']"
    "api_key\s*=\s*[\"'][^\"']+[\"']"
    "access_key\s*=\s*[\"'][^\"']+[\"']"
    "private_key\s*=\s*[\"'][^\"']+[\"']"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i -E "$pattern" *.tf 2>/dev/null | grep -v "variable\|sensitive\|#\|description\|example" > /dev/null; then
        echo -e "${RED}✗ Potential hardcoded secret found:${NC}"
        grep -r -i -E "$pattern" *.tf 2>/dev/null | grep -v "variable\|sensitive\|#\|description\|example" | head -3
        ISSUES=$((ISSUES + 1))
    fi
done

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ No hardcoded secrets detected${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# 2. Check for encryption enabled
echo ""
echo "🔐 Checking encryption settings..."

if [ -f "main.tf" ] || [ -f "../main.tf" ]; then
    ENCRYPTION_COUNT=$(grep -r -i "encryption\|encrypt" *.tf 2>/dev/null | grep -v "^#" | wc -l || echo "0")
    if [ "$ENCRYPTION_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Encryption settings found ($ENCRYPTION_COUNT references)${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ No encryption settings detected${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 3. Check for public access restrictions
echo ""
echo "🌐 Checking public access restrictions..."
PUBLIC_ACCESS=$(grep -r -i "public_access\|allow_public\|is_public" *.tf 2>/dev/null | grep -i "true\|enable" | grep -v "^#" | wc -l || echo "0")
if [ "$PUBLIC_ACCESS" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Public access may be enabled (review carefully)${NC}"
    grep -r -i "public_access\|allow_public\|is_public" *.tf 2>/dev/null | grep -i "true\|enable" | grep -v "^#" | head -3
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓ No obvious public access issues${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi

# 4. Check for least privilege IAM
echo ""
echo "👤 Checking IAM configurations..."
IAM_COUNT=$(grep -r -i "iam\|role\|policy" *.tf 2>/dev/null | wc -l || echo "0")
if [ "$IAM_COUNT" -gt 0 ]; then
    # Check for overly permissive policies
    WILDCARD_COUNT=$(grep -r -i "\"\*\"\|\"*\"" *.tf 2>/dev/null | grep -v "^#" | wc -l || echo "0")
    if [ "$WILDCARD_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}⚠ Wildcard permissions detected (review for least privilege)${NC}"
        grep -r -i "\"\*\"\|\"*\"" *.tf 2>/dev/null | grep -v "^#" | head -3
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✓ IAM configurations found, no obvious wildcard issues${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    fi
fi

# 5. Check for backend security
echo ""
echo "🔐 Checking backend security..."
if [ -d "../backend-configs" ]; then
    BACKEND_ENCRYPT=$(grep -r "encrypt\s*=\s*true" ../backend-configs/*.hcl 2>/dev/null | wc -l || echo "0")
    if [ "$BACKEND_ENCRYPT" -gt 0 ]; then
        echo -e "${GREEN}✓ Backend encryption enabled${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ Backend encryption not explicitly set${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# 6. Check for version pinning
echo ""
echo "📌 Checking provider version pinning..."
VERSION_COUNT=$(grep -r "version\s*=" *.tf providers.tf 2>/dev/null | grep -v "^#" | wc -l || echo "0")
if [ "$VERSION_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Provider versions specified ($VERSION_COUNT)${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ Provider versions not pinned${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo -e "${BLUE}Security Audit Summary${NC}"
echo "  Checks Passed: $CHECKS_PASSED"
echo "  Issues Found:  $ISSUES"
echo "  Warnings:      $WARNINGS"
echo ""

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Security audit passed!${NC}"
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo -e "${YELLOW}⚠ Security audit completed with warnings${NC}"
    echo "Review warnings above for potential improvements."
    exit 0
else
    echo -e "${RED}✗ Security issues found!${NC}"
    echo "Please review and fix issues before proceeding."
    exit 1
fi


