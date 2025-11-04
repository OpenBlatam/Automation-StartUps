#!/bin/bash
# Validate Terraform outputs
# Checks that outputs are properly configured and accessible
#
# Usage: ./validate-outputs.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/outputs.tf" ]; then
    cd azure
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "📤 Validating Terraform Outputs"
echo ""

# Check if outputs.tf exists
if [ ! -f "outputs.tf" ]; then
    echo -e "${YELLOW}⚠ No outputs.tf found${NC}"
    exit 0
fi

OUTPUTS_DEFINED=$(grep -c "^output " outputs.tf 2>/dev/null || echo "0")
echo "Outputs defined: $OUTPUTS_DEFINED"

if [ "$OUTPUTS_DEFINED" -eq 0 ]; then
    echo "No outputs defined."
    exit 0
fi

# Try to get actual outputs
echo ""
echo "Checking accessible outputs..."
OUTPUTS_AVAILABLE=$(terraform output -json 2>/dev/null | jq 'length' || echo "0")

if [ "$OUTPUTS_AVAILABLE" -gt 0 ]; then
    echo -e "${GREEN}✓ $OUTPUTS_AVAILABLE outputs available${NC}"
    echo ""
    echo "Available outputs:"
    terraform output -json 2>/dev/null | jq -r 'keys[]' | while read output; do
        echo "  - $output"
    done
else
    echo -e "${YELLOW}⚠ Outputs defined but not available${NC}"
    echo "  Run 'terraform apply' to create outputs"
fi

# Check for missing descriptions
echo ""
echo "Checking output documentation..."
OUTPUTS_NO_DESC=$(grep "^output " outputs.tf 2>/dev/null | while read line; do
    OUTPUT_NAME=$(echo "$line" | sed 's/output "\([^"]*\)".*/\1/')
    if ! grep -A 10 "^output \"$OUTPUT_NAME\"" outputs.tf | grep -q "description"; then
        echo "$OUTPUT_NAME"
    fi
done | wc -l)

if [ "$OUTPUTS_NO_DESC" -gt 0 ]; then
    echo -e "${YELLOW}⚠ $OUTPUTS_NO_DESC outputs missing descriptions${NC}"
    echo "  Add description to each output for better documentation"
else
    echo -e "${GREEN}✓ All outputs have descriptions${NC}"
fi

echo ""
echo "✅ Output validation complete"

