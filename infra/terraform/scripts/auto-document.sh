#!/bin/bash
# Auto-generate documentation from Terraform code
# Extracts variables, outputs, and resources to create documentation
#
# Usage: ./auto-document.sh [output_file]
# Example: ./auto-document.sh DOCUMENTATION.md

set -e

OUTPUT_FILE="${1:-AUTO_DOCUMENTATION.md}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "📝 Auto-generating Terraform Documentation"
echo "Output: $OUTPUT_FILE"
echo ""

# Start documentation
cat > "$OUTPUT_FILE" <<EOF
# Auto-Generated Terraform Documentation

> ⚠️ This file is auto-generated. Manual edits will be overwritten.
> Generated: $(date)

## 📋 Table of Contents

- [Variables](#variables)
- [Outputs](#outputs)
- [Resources](#resources)
- [Modules](#modules)

## Variables

EOF

# Extract variables
if ls *.tf 2>/dev/null | grep -q variables; then
    echo "Extracting variables..."
    cat >> "$OUTPUT_FILE" <<EOF
### Variable Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
EOF
    
    grep -h "^variable " *.tf 2>/dev/null | while read -r line; do
        VAR_NAME=$(echo "$line" | sed 's/variable "\([^"]*\)".*/\1/')
        
        # Try to get description and type from variable block
        TYPE=$(grep -A 20 "^variable \"$VAR_NAME\"" *.tf 2>/dev/null | grep "type\s*=" | head -1 | sed 's/.*type\s*=\s*//' | sed 's/\s*$//' || echo "unknown")
        DEFAULT=$(grep -A 20 "^variable \"$VAR_NAME\"" *.tf 2>/dev/null | grep "default\s*=" | head -1 | sed 's/.*default\s*=\s*//' | sed 's/\s*$//' || echo "-")
        DESC=$(grep -A 20 "^variable \"$VAR_NAME\"" *.tf 2>/dev/null | grep "description\s*=" | head -1 | sed 's/.*description\s*=\s*"\([^"]*\)".*/\1/' || echo "No description")
        
        echo "| \`$VAR_NAME\` | $TYPE | $DEFAULT | $DESC |" >> "$OUTPUT_FILE"
    done
else
    echo "No variables found." >> "$OUTPUT_FILE"
fi

# Extract outputs
cat >> "$OUTPUT_FILE" <<EOF

## Outputs

EOF

if ls *.tf 2>/dev/null | grep -q outputs; then
    echo "Extracting outputs..."
    cat >> "$OUTPUT_FILE" <<EOF
### Output Reference

| Output | Description | Sensitive |
|--------|-------------|-----------|
EOF
    
    grep -h "^output " *.tf 2>/dev/null | while read -r line; do
        OUT_NAME=$(echo "$line" | sed 's/output "\([^"]*\)".*/\1/')
        DESC=$(grep -A 10 "^output \"$OUT_NAME\"" *.tf 2>/dev/null | grep "description\s*=" | head -1 | sed 's/.*description\s*=\s*"\([^"]*\)".*/\1/' || echo "No description")
        SENSITIVE=$(grep -A 10 "^output \"$OUT_NAME\"" *.tf 2>/dev/null | grep -q "sensitive\s*=\s*true" && echo "Yes" || echo "No")
        
        echo "| \`$OUT_NAME\` | $DESC | $SENSITIVE |" >> "$OUTPUT_FILE"
    done
else
    echo "No outputs found." >> "$OUTPUT_FILE"
fi

# Extract resources
cat >> "$OUTPUT_FILE" <<EOF

## Resources

EOF

echo "Extracting resources..."
RESOURCE_COUNT=$(grep -h "^resource " *.tf 2>/dev/null | wc -l | tr -d ' ')
echo "Found $RESOURCE_COUNT resources" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" <<EOF
### Resource List

| Type | Name | Description |
|------|------|-------------|
EOF

grep -h "^resource " *.tf 2>/dev/null | while read -r line; do
    RES_TYPE=$(echo "$line" | sed 's/resource "\([^"]*\)" "\([^"]*\)".*/\1/')
    RES_NAME=$(echo "$line" | sed 's/resource "\([^"]*\)" "\([^"]*\)".*/\2/')
    echo "| \`$RES_TYPE\` | \`$RES_NAME\` | - |" >> "$OUTPUT_FILE"
done

# Extract modules
if grep -q "^module " *.tf 2>/dev/null; then
    cat >> "$OUTPUT_FILE" <<EOF

## Modules

### Module Usage

| Module | Source | Version |
|--------|--------|---------|
EOF
    
    grep -h "^module " *.tf 2>/dev/null | while read -r line; do
        MOD_NAME=$(echo "$line" | sed 's/module "\([^"]*\)".*/\1/')
        MOD_SOURCE=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "source\s*=" | head -1 | sed 's/.*source\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
        MOD_VERSION=$(grep -A 5 "^module \"$MOD_NAME\"" *.tf 2>/dev/null | grep "version\s*=" | head -1 | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/' || echo "-")
        
        echo "| \`$MOD_NAME\` | $MOD_SOURCE | $MOD_VERSION |" >> "$OUTPUT_FILE"
    done
fi

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*Auto-generated on $(date)*" >> "$OUTPUT_FILE"

echo "✅ Documentation generated: $OUTPUT_FILE"
echo ""
echo "Review and customize as needed."

