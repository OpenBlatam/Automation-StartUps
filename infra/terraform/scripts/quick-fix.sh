#!/bin/bash
# Quick fix common Terraform issues
# Automated fixes for frequent problems
#
# Usage: ./quick-fix.sh [issue]
# Issues: format, validate, init, refresh
# Example: ./quick-fix.sh format

set -e

ISSUE="${1:-help}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$TERRAFORM_DIR"

case "$ISSUE" in
    format)
        echo "🔧 Fixing code format..."
        terraform fmt -recursive
        echo -e "${GREEN}✅ Code formatted${NC}"
        ;;
    
    validate)
        echo "🔧 Validating configuration..."
        terraform init -backend=false > /dev/null 2>&1
        if terraform validate; then
            echo -e "${GREEN}✅ Configuration valid${NC}"
        else
            echo "❌ Validation failed. Review errors above."
            exit 1
        fi
        ;;
    
    init)
        echo "🔧 Reinitializing Terraform..."
        rm -rf .terraform .terraform.lock.hcl
        terraform init
        echo -e "${GREEN}✅ Terraform reinitialized${NC}"
        ;;
    
    refresh)
        echo "🔧 Refreshing state..."
        terraform refresh
        echo -e "${GREEN}✅ State refreshed${NC}"
        ;;
    
    clean)
        echo "🔧 Cleaning workspace..."
        rm -rf .terraform crash.log* *.tfplan *.tfplan.json terraform-output*.json
        echo -e "${GREEN}✅ Workspace cleaned${NC}"
        ;;
    
    fix-all)
        echo "🔧 Running all fixes..."
        echo ""
        ./quick-fix.sh format
        ./quick-fix.sh validate
        ./quick-fix.sh refresh
        echo ""
        echo -e "${GREEN}✅ All fixes applied${NC}"
        ;;
    
    help|*)
        echo "Quick Fix Tool"
        echo ""
        echo "Usage: ./quick-fix.sh [issue]"
        echo ""
        echo "Available fixes:"
        echo "  format      - Fix code formatting"
        echo "  validate    - Validate configuration"
        echo "  init        - Reinitialize Terraform"
        echo "  refresh     - Refresh state"
        echo "  clean       - Clean workspace"
        echo "  fix-all     - Run all fixes"
        echo ""
        echo "Examples:"
        echo "  ./quick-fix.sh format"
        echo "  ./quick-fix.sh fix-all"
        ;;
esac

