#!/bin/bash
# Export Terraform outputs to various formats
# Useful for CI/CD and integration with other tools
#
# Usage: ./export-outputs.sh [format] [file]
# Formats: json, yaml, env, tfvars
# Example: ./export-outputs.sh json outputs.json

set -e

FORMAT="${1:-json}"
OUTPUT_FILE="${2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/outputs.tf" ]; then
    cd azure
fi

# Check if terraform is initialized
if [ ! -d ".terraform" ]; then
    echo "Error: Terraform not initialized. Run 'terraform init' first."
    exit 1
fi

echo "📤 Exporting Terraform Outputs"
echo "Format: $FORMAT"
echo ""

case "$FORMAT" in
    json)
        OUTPUT=$(terraform output -json 2>/dev/null || echo "{}")
        if [ -n "$OUTPUT_FILE" ]; then
            echo "$OUTPUT" > "$OUTPUT_FILE"
            echo "✓ Exported to: $OUTPUT_FILE"
        else
            echo "$OUTPUT" | jq '.' 2>/dev/null || echo "$OUTPUT"
        fi
        ;;
    
    yaml)
        OUTPUT=$(terraform output -json 2>/dev/null || echo "{}")
        YAML_OUTPUT=$(echo "$OUTPUT" | jq -r 'to_entries | map("\(.key): \(.value.value // .value)") | .[]' 2>/dev/null)
        if [ -n "$OUTPUT_FILE" ]; then
            echo "$YAML_OUTPUT" > "$OUTPUT_FILE"
            echo "✓ Exported to: $OUTPUT_FILE"
        else
            echo "$YAML_OUTPUT"
        fi
        ;;
    
    env)
        OUTPUT=$(terraform output -json 2>/dev/null || echo "{}")
        ENV_OUTPUT=$(echo "$OUTPUT" | jq -r 'to_entries | map("export TF_OUTPUT_\(.key | ascii_upcase)=\(.value.value // .value | @sh)") | .[]' 2>/dev/null)
        if [ -n "$OUTPUT_FILE" ]; then
            echo "$ENV_OUTPUT" > "$OUTPUT_FILE"
            echo "✓ Exported to: $OUTPUT_FILE"
            echo ""
            echo "To use in your shell:"
            echo "  source $OUTPUT_FILE"
        else
            echo "$ENV_OUTPUT"
        fi
        ;;
    
    tfvars)
        OUTPUT=$(terraform output -json 2>/dev/null || echo "{}")
        TFVARS_OUTPUT=$(echo "$OUTPUT" | jq -r 'to_entries | map("\(.key) = \(.value.value // .value | @json)") | .[]' 2>/dev/null)
        if [ -n "$OUTPUT_FILE" ]; then
            echo "# Terraform outputs exported on $(date)" > "$OUTPUT_FILE"
            echo "$TFVARS_OUTPUT" >> "$OUTPUT_FILE"
            echo "✓ Exported to: $OUTPUT_FILE"
        else
            echo "$TFVARS_OUTPUT"
        fi
        ;;
    
    *)
        echo "Error: Unknown format '$FORMAT'"
        echo "Supported formats: json, yaml, env, tfvars"
        exit 1
        ;;
esac

echo ""
echo "✅ Export complete!"


