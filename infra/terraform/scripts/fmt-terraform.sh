#!/bin/bash
# Format Terraform code and check for issues
#
# Usage: ./fmt-terraform.sh [directory]
# Example: ./fmt-terraform.sh
# Example: ./fmt-terraform.sh azure

set -e

TERRAFORM_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$BASE_DIR/$TERRAFORM_DIR"

echo "📝 Formatting Terraform code..."
echo "Directory: $TERRAFORM_DIR"
echo ""

# Format code
if terraform fmt -recursive; then
    echo -e "${GREEN}✓ Code formatted successfully${NC}"
else
    echo -e "${YELLOW}⚠ Some files were reformatted${NC}"
    exit 1
fi

# Check if there are uncommitted changes after formatting
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo ""
        echo -e "${YELLOW}⚠ Files were modified by formatting${NC}"
        echo "Modified files:"
        git status --short
        echo ""
        echo "Please review and commit the changes."
        exit 1
    else
        echo -e "${GREEN}✓ Code is properly formatted${NC}"
    fi
fi



