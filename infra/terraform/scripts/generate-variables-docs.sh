#!/bin/bash
# Generate variables documentation
# Creates detailed documentation of all variables
#
# Usage: ./generate-variables-docs.sh [output_file]
# Example: ./generate-variables-docs.sh VARIABLES.md

set -e

OUTPUT_FILE="${1:-VARIABLES.md}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/variables.tf" ]; then
    cd azure
fi

echo "📝 Generating Variables Documentation"
echo "Output: $OUTPUT_FILE"
echo ""

cat > "$OUTPUT_FILE" <<EOF
# Terraform Variables Reference

> Auto-generated from Terraform configuration
> Generated: $(date)

## Overview

This document contains all variables defined in the Terraform configuration.

## Variables

| Variable | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
EOF

# Extract variables
grep -h "^variable " *.tf 2>/dev/null | while read -r line; do
    VAR_NAME=$(echo "$line" | sed 's/variable "\([^"]*\)".*/\1/')
    
    # Get variable details
    VAR_BLOCK=$(grep -A 20 "^variable \"$VAR_NAME\"" *.tf 2>/dev/null || echo "")
    
    TYPE=$(echo "$VAR_BLOCK" | grep "type\s*=" | head -1 | sed 's/.*type\s*=\s*//' | sed 's/\s*$//' || echo "unknown")
    DEFAULT=$(echo "$VAR_BLOCK" | grep "default\s*=" | head -1 | sed 's/.*default\s*=\s*//' | sed 's/\s*$//' || echo "-")
    DESC=$(echo "$VAR_BLOCK" | grep "description\s*=" | head -1 | sed 's/.*description\s*=\s*"\([^"]*\)".*/\1/' || echo "No description")
    
    if [ "$DEFAULT" = "-" ]; then
        REQUIRED="Yes"
    else
        REQUIRED="No"
    fi
    
    echo "| \`$VAR_NAME\` | $TYPE | $DEFAULT | $REQUIRED | $DESC |" >> "$OUTPUT_FILE"
done

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*Auto-generated on $(date)*" >> "$OUTPUT_FILE"

echo "✅ Documentation generated: $OUTPUT_FILE"

