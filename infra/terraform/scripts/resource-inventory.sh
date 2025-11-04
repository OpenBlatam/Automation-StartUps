#!/bin/bash
# Generate resource inventory from Terraform state
# Creates a comprehensive inventory of all managed resources
#
# Usage: ./resource-inventory.sh [provider] [format]
# Format: json, yaml, csv, table
# Example: ./resource-inventory.sh aws json

set -e

PROVIDER="${1:-aws}"
FORMAT="${2:-table}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

echo "📋 Terraform Resource Inventory"
echo "Provider: $PROVIDER"
echo "Format: $FORMAT"
echo ""

# Get state resources
STATE_JSON=$(terraform state pull 2>/dev/null || echo "{}")

if [ "$STATE_JSON" = "{}" ]; then
    echo "No state found. Run 'terraform apply' first."
    exit 1
fi

case "$FORMAT" in
    json)
        echo "$STATE_JSON" | jq '{
            total_resources: ([.resources[]?] | length),
            resources: [.resources[]? | {
                address: .address,
                type: .type,
                provider: .provider,
                mode: .mode
            }]
        }'
        ;;
    
    yaml)
        echo "$STATE_JSON" | jq -r '
            "total_resources: " + ([.resources[]?] | length | tostring),
            "resources:",
            (.resources[]? | 
                "- address: " + .address,
                "  type: " + .type,
                "  provider: " + .provider,
                "  mode: " + .mode
            )
        '
        ;;
    
    csv)
        echo "address,type,provider,mode"
        echo "$STATE_JSON" | jq -r '.resources[]? | "\(.address),\(.type),\(.provider),\(.mode)"'
        ;;
    
    table|*)
        echo "Resource Address | Type | Provider | Mode"
        echo "─────────────────────────────────────────────────────────────────"
        echo "$STATE_JSON" | jq -r '.resources[]? | "\(.address) | \(.type) | \(.provider) | \(.mode)"' | column -t -s '|'
        
        TOTAL=$(echo "$STATE_JSON" | jq '[.resources[]?] | length' || echo "0")
        echo ""
        echo "Total resources: $TOTAL"
        ;;
esac

