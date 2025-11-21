#!/bin/bash
# Check Terraform version compatibility
# Verifies Terraform version matches requirements
#
# Usage: ./check-terraform-version.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Checking Terraform Version Compatibility"
echo ""

# Get required version
REQUIRED_VERSION=$(grep "required_version" "$TERRAFORM_DIR"/*.tf "$TERRAFORM_DIR"/azure/*.tf 2>/dev/null | \
    grep -o '">=[0-9]\+\.[0-9]\+' | sed 's/^">=//' | head -1 || echo "1.6.0")

# Get current version
if command -v terraform &> /dev/null; then
    CURRENT_VERSION=$(terraform version -json 2>/dev/null | jq -r '.terraform_version' || \
        terraform version | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
    
    echo "Required version: >= $REQUIRED_VERSION"
    echo "Current version: $CURRENT_VERSION"
    echo ""
    
    # Simple version comparison
    REQUIRED_MAJOR=$(echo "$REQUIRED_VERSION" | cut -d. -f1)
    REQUIRED_MINOR=$(echo "$REQUIRED_VERSION" | cut -d. -f2)
    CURRENT_MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1)
    CURRENT_MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f2)
    
    if [ "$CURRENT_MAJOR" -gt "$REQUIRED_MAJOR" ] || \
       ([ "$CURRENT_MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$CURRENT_MINOR" -ge "$REQUIRED_MINOR" ]); then
        echo -e "${GREEN}✅ Terraform version is compatible${NC}"
        exit 0
    else
        echo -e "${RED}✗ Terraform version is too old${NC}"
        echo "Please upgrade Terraform to >= $REQUIRED_VERSION"
        exit 1
    fi
else
    echo -e "${RED}✗ Terraform is not installed${NC}"
    echo "Install Terraform: https://www.terraform.io/downloads"
    exit 1
fi

