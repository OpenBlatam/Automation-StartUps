#!/bin/bash
# Validate Terraform modules
# Checks modules for common issues and best practices
#
# Usage: ./validate-modules.sh [module_directory]
# Example: ./validate-modules.sh modules/my-module

set -e

MODULE_DIR="${1:-modules}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Validating Terraform Modules"
echo "Directory: $MODULE_DIR"
echo ""

if [ ! -d "$MODULE_DIR" ]; then
    echo "Module directory not found: $MODULE_DIR"
    exit 1
fi

ISSUES=0
WARNINGS=0

# Check each module
for module in "$MODULE_DIR"/*; do
    if [ ! -d "$module" ]; then
        continue
    fi
    
    MODULE_NAME=$(basename "$module")
    echo "Checking module: $MODULE_NAME"
    
    # Check for required files
    if [ ! -f "$module/main.tf" ]; then
        echo -e "${YELLOW}  ⚠ Missing main.tf${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if [ ! -f "$module/variables.tf" ]; then
        echo -e "${YELLOW}  ⚠ Missing variables.tf${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if [ ! -f "$module/outputs.tf" ]; then
        echo -e "${YELLOW}  ⚠ Missing outputs.tf${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if [ ! -f "$module/README.md" ]; then
        echo -e "${YELLOW}  ⚠ Missing README.md${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Validate module syntax
    if cd "$module" && terraform init -backend=false > /dev/null 2>&1; then
        if terraform validate > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Valid${NC}"
        else
            echo -e "${RED}  ✗ Validation failed${NC}"
            terraform validate 2>&1 | head -3
            ISSUES=$((ISSUES + 1))
        fi
    else
        echo -e "${YELLOW}  ⚠ Could not initialize${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    cd "$TERRAFORM_DIR"
    echo ""
done

echo "═══════════════════════════════════════"
echo "Module Validation Summary:"
echo "  Issues: $ISSUES"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All modules valid!${NC}"
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo -e "${YELLOW}⚠ Modules have warnings${NC}"
    exit 0
else
    echo -e "${RED}✗ Some modules have issues${NC}"
    exit 1
fi

