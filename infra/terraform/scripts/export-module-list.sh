#!/bin/bash
# Export list of all modules used
# Useful for dependency tracking and updates
#
# Usage: ./export-module-list.sh [format]
# Format: json, list, markdown
# Example: ./export-module-list.sh json

set -e

FORMAT="${1:-list}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "📦 Exporting Module List"
echo "Format: $FORMAT"
echo ""

MODULES=$(grep -h "^module " *.tf 2>/dev/null || echo "")

if [ -z "$MODULES" ]; then
    echo "No modules found."
    exit 0
fi

case "$FORMAT" in
    json)
        echo "$MODULES" | while read -r line; do
            MOD_NAME=$(echo "$line" | sed 's/module "\([^"]*\)".*/\1/')
            MOD_SOURCE=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "source\s*=" | head -1 | sed 's/.*source\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            MOD_VERSION=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "version\s*=" | head -1 | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            
            echo "{\"name\":\"$MOD_NAME\",\"source\":\"$MOD_SOURCE\",\"version\":\"$MOD_VERSION\"}"
        done | jq -s '.'
        ;;
    
    markdown|md)
        echo "| Module Name | Source | Version |"
        echo "|-------------|--------|---------|"
        echo "$MODULES" | while read -r line; do
            MOD_NAME=$(echo "$line" | sed 's/module "\([^"]*\)".*/\1/')
            MOD_SOURCE=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "source\s*=" | head -1 | sed 's/.*source\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            MOD_VERSION=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "version\s*=" | head -1 | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            
            echo "| $MOD_NAME | $MOD_SOURCE | $MOD_VERSION |"
        done
        ;;
    
    list|*)
        echo "$MODULES" | while read -r line; do
            MOD_NAME=$(echo "$line" | sed 's/module "\([^"]*\)".*/\1/')
            MOD_SOURCE=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "source\s*=" | head -1 | sed 's/.*source\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            MOD_VERSION=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "version\s*=" | head -1 | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
            
            echo "Module: $MOD_NAME"
            echo "  Source: $MOD_SOURCE"
            echo "  Version: $MOD_VERSION"
            echo ""
        done
        ;;
esac

