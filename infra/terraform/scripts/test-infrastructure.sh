#!/bin/bash
# Test infrastructure after deployment
# Validates that resources are working correctly
#
# Usage: ./test-infrastructure.sh [provider] [environment]
# Example: ./test-infrastructure.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

echo "🧪 Testing Infrastructure"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: State accessibility
echo "Test 1: State accessibility..."
if terraform state list > /dev/null 2>&1; then
    echo -e "${GREEN}✓ State is accessible${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ State is not accessible${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2: Outputs available
echo ""
echo "Test 2: Outputs available..."
OUTPUT_COUNT=$(terraform output -json 2>/dev/null | jq 'length' || echo "0")
if [ "$OUTPUT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Outputs available ($OUTPUT_COUNT outputs)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ No outputs available (infrastructure may not be deployed)${NC}"
fi

# Test 3: No drift
echo ""
echo "Test 3: Configuration drift..."
PLAN_OUTPUT=$(terraform plan -detailed-exitcode -no-color 2>&1 || true)
if echo "$PLAN_OUTPUT" | grep -q "No changes"; then
    echo -e "${GREEN}✓ No drift detected${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ Drift detected (this may be expected)${NC}"
fi

# Test 4: Provider-specific tests
echo ""
echo "Test 4: Provider connectivity..."

if [ "$PROVIDER" = "aws" ]; then
    if aws sts get-caller-identity > /dev/null 2>&1; then
        echo -e "${GREEN}✓ AWS credentials valid${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ AWS credentials invalid${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
elif [ "$PROVIDER" = "azure" ]; then
    if az account show > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Azure credentials valid${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ Azure credentials invalid${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
fi

# Test 5: Resources exist in state
echo ""
echo "Test 5: Resources in state..."
RESOURCE_COUNT=$(terraform state list 2>/dev/null | wc -l | tr -d ' ')
if [ "$RESOURCE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Resources found in state ($RESOURCE_COUNT)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠ No resources in state${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "Test Results:"
echo "  Passed: $TESTS_PASSED"
echo "  Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

