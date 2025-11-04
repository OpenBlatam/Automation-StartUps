#!/bin/bash
# Find unused variables in Terraform configuration
# Helps identify variables that can be removed
#
# Usage: ./find-unused-variables.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "🔍 Finding Unused Variables"
echo ""

# Find all variable declarations
VARIABLES=$(grep -h "^variable " *.tf 2>/dev/null | sed 's/variable "\([^"]*\)".*/\1/' || echo "")

if [ -z "$VARIABLES" ]; then
    echo "No variables found."
    exit 0
fi

UNUSED=()
USED_COUNT=0

echo "Checking variables..."
for var in $VARIABLES; do
    # Check if variable is used (excluding its own declaration)
    USAGE=$(grep -r "var\.$var" *.tf 2>/dev/null | grep -v "^variable " | wc -l | tr -d ' ')
    
    if [ "$USAGE" -eq 0 ]; then
        UNUSED+=("$var")
        echo "  ✗ $var - UNUSED"
    else
        echo "  ✓ $var - Used $USAGE time(s)"
        USED_COUNT=$((USED_COUNT + 1))
    fi
done

echo ""
echo "═══════════════════════════════════════"
echo "Summary:"
echo "  Used variables: $USED_COUNT"
echo "  Unused variables: ${#UNUSED[@]}"
echo ""

if [ ${#UNUSED[@]} -gt 0 ]; then
    echo "Unused variables (can be removed):"
    for var in "${UNUSED[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "⚠️  Note: Variables might be used in:"
    echo "  - tfvars files"
    echo "  - Environment variables (TF_VAR_*)"
    echo "  - Module calls"
    echo "  Review carefully before removing!"
else
    echo "✅ All variables are used!"
fi

