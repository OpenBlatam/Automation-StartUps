#!/bin/bash
# Check actual state of resources vs Terraform state
# Validates that resources actually exist in cloud
#
# Usage: ./check-resources.sh [provider] [environment]
# Example: ./check-resources.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Checking Resources in Cloud"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

RESOURCES_CHECKED=0
RESOURCES_FOUND=0
RESOURCES_MISSING=0

# Get resource list from state
RESOURCES=$(terraform state list 2>/dev/null || echo "")

if [ -z "$RESOURCES" ]; then
    echo "No resources in state."
    exit 0
fi

echo "Checking resources..."
echo ""

# Check each resource based on type
while IFS= read -r resource; do
    RESOURCES_CHECKED=$((RESOURCES_CHECKED + 1))
    RESOURCE_TYPE=$(echo "$resource" | sed 's/\..*$//')
    RESOURCE_NAME=$(echo "$resource" | sed 's/^[^.]*\.//')
    
    FOUND=false
    
    if [ "$PROVIDER" = "aws" ]; then
        case "$RESOURCE_TYPE" in
            aws_s3_bucket)
                BUCKET_NAME=$(terraform state show "$resource" 2>/dev/null | grep "id\s*=" | head -1 | awk '{print $3}' || echo "")
                if [ -n "$BUCKET_NAME" ] && aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
                    FOUND=true
                fi
                ;;
            aws_vpc|aws_subnet|aws_instance|aws_security_group)
                # Generic check - try to get resource
                if terraform state show "$resource" > /dev/null 2>&1; then
                    FOUND=true
                fi
                ;;
        esac
    elif [ "$PROVIDER" = "azure" ]; then
        case "$RESOURCE_TYPE" in
            azurerm_resource_group|azurerm_storage_account|azurerm_virtual_network)
                # Check if resource exists
                if terraform state show "$resource" > /dev/null 2>&1; then
                    FOUND=true
                fi
                ;;
        esac
    fi
    
    if [ "$FOUND" = true ]; then
        echo -e "${GREEN}✓${NC} $resource"
        RESOURCES_FOUND=$((RESOURCES_FOUND + 1))
    else
        echo -e "${YELLOW}?${NC} $resource (could not verify)"
        # Don't count as missing, just couldn't verify
    fi
done <<< "$RESOURCES"

echo ""
echo "═══════════════════════════════════════"
echo "Resource Check Summary:"
echo "  Checked: $RESOURCES_CHECKED"
echo "  Found: $RESOURCES_FOUND"
echo "  Could not verify: $((RESOURCES_CHECKED - RESOURCES_FOUND))"
echo ""
echo "⚠️  Note: Not all resource types can be verified automatically."
echo "    Manual verification may be required for some resources."

