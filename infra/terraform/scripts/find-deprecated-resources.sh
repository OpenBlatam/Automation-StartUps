#!/bin/bash
# Find potentially deprecated or problematic resources
# Checks for resources that might need attention
#
# Usage: ./find-deprecated-resources.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Finding Potentially Deprecated Resources"
echo ""

# Patterns that might indicate deprecated resources
DEPRECATED_PATTERNS=(
    "aws_instance"  # Check if should use launch templates
    "deprecated"
    "deprecation"
    "legacy"
)

FOUND=0

for pattern in "${DEPRECATED_PATTERNS[@]}"; do
    if grep -r -i "$pattern" *.tf 2>/dev/null | grep -v "^#" > /dev/null; then
        echo -e "${YELLOW}⚠ Found: $pattern${NC}"
        grep -r -i "$pattern" *.tf 2>/dev/null | grep -v "^#" | head -3 | sed 's/^/  /'
        FOUND=$((FOUND + 1))
    fi
done

if [ $FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ No obvious deprecated resources found${NC}"
else
    echo ""
    echo "⚠️  Review the above resources for potential updates"
    echo "  - Check provider documentation"
    echo "  - Consider newer resource types"
    echo "  - Review deprecation notices"
fi

