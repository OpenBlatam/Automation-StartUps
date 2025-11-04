#!/bin/bash
# Drift detection script
# Detects configuration drift between Terraform state and actual infrastructure
#
# Usage: ./drift-detection.sh [provider] [environment]
# Example: ./drift-detection.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔄 Terraform Drift Detection"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

# Run terraform plan to detect drift
echo "📊 Analyzing infrastructure state..."
echo ""

PLAN_OUTPUT=$(terraform plan -detailed-exitcode -no-color 2>&1 || true)
PLAN_EXIT_CODE=$?

case $PLAN_EXIT_CODE in
    0)
        echo -e "${GREEN}✅ No drift detected${NC}"
        echo "Infrastructure matches Terraform configuration."
        exit 0
        ;;
    1)
        echo -e "${RED}✗ Error during plan${NC}"
        echo "$PLAN_OUTPUT"
        exit 1
        ;;
    2)
        echo -e "${YELLOW}⚠ Drift detected!${NC}"
        echo ""
        
        # Extract changes
        CREATES=$(echo "$PLAN_OUTPUT" | grep -c "will be created" || echo "0")
        UPDATES=$(echo "$PLAN_OUTPUT" | grep -c "will be updated\|must be replaced" || echo "0")
        DELETES=$(echo "$PLAN_OUTPUT" | grep -c "will be destroyed" || echo "0")
        
        echo "📈 Change Summary:"
        echo "  Resources to create:  $CREATES"
        echo "  Resources to update:  $UPDATES"
        echo "  Resources to destroy: $DELETES"
        echo ""
        
        # Show details
        if [ "$CREATES" -gt 0 ]; then
            echo -e "${BLUE}➕ Resources to be created:${NC}"
            echo "$PLAN_OUTPUT" | grep "will be created" | head -10 | sed 's/^/  /'
        fi
        
        if [ "$UPDATES" -gt 0 ]; then
            echo -e "${YELLOW}🔄 Resources to be updated:${NC}"
            echo "$PLAN_OUTPUT" | grep -E "will be updated|must be replaced" | head -10 | sed 's/^/  /'
        fi
        
        if [ "$DELETES" -gt 0 ]; then
            echo -e "${RED}➖ Resources to be destroyed:${NC}"
            echo "$PLAN_OUTPUT" | grep "will be destroyed" | head -10 | sed 's/^/  /'
        fi
        
        echo ""
        echo "📋 Full plan details:"
        echo "$PLAN_OUTPUT"
        echo ""
        echo "💡 Recommendations:"
        echo "  1. Review the changes above"
        echo "  2. If changes are expected, run: terraform apply"
        echo "  3. If changes are unexpected, investigate:"
        echo "     - Manual changes to infrastructure"
        echo "     - Changes in provider behavior"
        echo "     - State file issues"
        echo ""
        echo "  4. To refresh state without applying:"
        echo "     terraform refresh"
        
        exit 2
        ;;
    *)
        echo "Unexpected exit code: $PLAN_EXIT_CODE"
        exit 1
        ;;
esac


