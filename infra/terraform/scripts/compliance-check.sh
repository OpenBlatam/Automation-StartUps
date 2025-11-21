#!/bin/bash
# Compliance check script
# Validates infrastructure against compliance standards
#
# Usage: ./compliance-check.sh [standard]
# Standards: aws-well-architected, azure-well-architected, basic
# Example: ./compliance-check.sh aws-well-architected

set -e

STANDARD="${1:-basic}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "📋 Compliance Check"
echo "Standard: $STANDARD"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Basic compliance checks
if [ "$STANDARD" = "basic" ] || [ "$STANDARD" = "aws-well-architected" ] || [ "$STANDARD" = "azure-well-architected" ]; then
    echo "🔒 Security Checks:"
    
    # 1. Encryption enabled
    ENCRYPTION_COUNT=$(grep -r -i "encryption\|encrypt" *.tf 2>/dev/null | grep -v "^#" | wc -l || echo "0")
    if [ "$ENCRYPTION_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Encryption configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Encryption not explicitly configured${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 2. Backend remote
    if [ -d ".terraform" ]; then
        BACKEND_TYPE=$(terraform show -json 2>/dev/null | jq -r '.values.backend.type' || echo "local")
        if [ "$BACKEND_TYPE" != "local" ] && [ "$BACKEND_TYPE" != "null" ]; then
            echo -e "  ${GREEN}✓ Remote backend configured${NC}"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
        else
            echo -e "  ${RED}✗ Using local backend (not recommended)${NC}"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
        fi
    fi
    
    # 3. State locking
    if [ "$BACKEND_TYPE" = "s3" ] || [ "$BACKEND_TYPE" = "azurerm" ]; then
        echo -e "  ${GREEN}✓ State locking enabled (via backend)${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    fi
    
    # 4. No hardcoded secrets
    SECRETS_FOUND=$(grep -r -iE "password\s*=\s*[\"'][^\"']+[\"']|secret\s*=\s*[\"'][^\"']+[\"']" *.tf 2>/dev/null | grep -v "variable\|sensitive\|#" | wc -l || echo "0")
    if [ "$SECRETS_FOUND" -eq 0 ]; then
        echo -e "  ${GREEN}✓ No hardcoded secrets${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${RED}✗ Hardcoded secrets found${NC}"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
fi

# AWS Well-Architected Framework checks
if [ "$STANDARD" = "aws-well-architected" ]; then
    echo ""
    echo "🏗️  AWS Well-Architected Framework:"
    
    # Cost optimization
    COST_TAGS=$(grep -r "cost\|CostCenter\|Billing" *.tf 2>/dev/null | wc -l || echo "0")
    if [ "$COST_TAGS" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Cost tracking tags configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Cost tracking tags not found${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Reliability
    BACKUP_CONFIG=$(grep -r -i "backup\|snapshot\|replication" *.tf 2>/dev/null | wc -l || echo "0")
    if [ "$BACKUP_CONFIG" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Backup/replication configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Backup configuration not found${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Performance
    MONITORING=$(grep -r -i "monitoring\|cloudwatch\|metrics" *.tf 2>/dev/null | wc -l || echo "0")
    if [ "$MONITORING" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Monitoring configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Monitoring not configured${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Azure Well-Architected Framework checks
if [ "$STANDARD" = "azure-well-architected" ]; then
    echo ""
    echo "🏗️  Azure Well-Architected Framework:"
    
    # Security
    NETWORK_RULES=$(grep -r -i "network_rule\|nsg\|firewall" *.tf 2>/dev/null | wc -l || echo "0")
    if [ "$NETWORK_RULES" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Network security configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Network security rules not found${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Reliability
    AVAILABILITY=$(grep -r -i "availability\|redundancy\|zones" *.tf 2>/dev/null | wc -l || echo "0")
    if [ "$AVAILABILITY" -gt 0 ]; then
        echo -e "  ${GREEN}✓ Availability zones configured${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠ Availability configuration not found${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "Compliance Check Summary:"
echo "  ✓ Passed: $CHECKS_PASSED"
echo "  ✗ Failed: $CHECKS_FAILED"
echo "  ⚠ Warnings: $WARNINGS"
echo ""

if [ $CHECKS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Compliance check passed!${NC}"
    exit 0
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠ Compliance check completed with warnings${NC}"
    exit 0
else
    echo -e "${RED}✗ Compliance issues found${NC}"
    exit 1
fi

