#!/bin/bash
# Export detailed resource list with metadata
# Useful for audits and documentation
#
# Usage: ./export-resource-list.sh [format] [file]
# Format: json, csv, markdown
# Example: ./export-resource-list.sh json resources.json

set -e

FORMAT="${1:-json}"
OUTPUT_FILE="${2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

echo "📋 Exporting Resource List"
echo "Format: $FORMAT"
echo ""

# Get state
STATE_JSON=$(terraform state pull 2>/dev/null || echo "{}")

if [ "$STATE_JSON" = "{}" ]; then
    echo "No state found."
    exit 1
fi

case "$FORMAT" in
    json)
        OUTPUT=$(echo "$STATE_JSON" | jq '{
            total_resources: ([.resources[]?] | length),
            resources: [.resources[]? | {
                address: .address,
                type: .type,
                provider: .provider,
                mode: .mode,
                instances: (.instances | length)
            }]
        }')
        
        if [ -n "$OUTPUT_FILE" ]; then
            echo "$OUTPUT" > "$OUTPUT_FILE"
            echo "✅ Exported to: $OUTPUT_FILE"
        else
            echo "$OUTPUT" | jq '.'
        fi
        ;;
    
    csv)
        HEADER="address,type,provider,mode,instances"
        BODY=$(echo "$STATE_JSON" | jq -r '.resources[]? | 
            "\(.address),\(.type),\(.provider),\(.mode),\(.instances | length)"
        ')
        
        if [ -n "$OUTPUT_FILE" ]; then
            echo "$HEADER" > "$OUTPUT_FILE"
            echo "$BODY" >> "$OUTPUT_FILE"
            echo "✅ Exported to: $OUTPUT_FILE"
        else
            echo "$HEADER"
            echo "$BODY"
        fi
        ;;
    
    markdown|md)
        OUTPUT="# Terraform Resources\n\n"
        OUTPUT="${OUTPUT}Total: $(echo "$STATE_JSON" | jq '[.resources[]?] | length')\n\n"
        OUTPUT="${OUTPUT}| Address | Type | Provider | Mode | Instances |\n"
        OUTPUT="${OUTPUT}|---------|------|----------|------|-----------|\n"
        
        BODY=$(echo "$STATE_JSON" | jq -r '.resources[]? | 
            "| \(.address) | \(.type) | \(.provider) | \(.mode) | \(.instances | length) |"
        ')
        
        OUTPUT="${OUTPUT}${BODY}\n"
        
        if [ -n "$OUTPUT_FILE" ]; then
            echo -e "$OUTPUT" > "$OUTPUT_FILE"
            echo "✅ Exported to: $OUTPUT_FILE"
        else
            echo -e "$OUTPUT"
        fi
        ;;
    
    *)
        echo "Error: Unknown format '$FORMAT'"
        echo "Supported formats: json, csv, markdown"
        exit 1
        ;;
esac

