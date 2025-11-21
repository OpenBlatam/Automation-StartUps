#!/bin/bash
# Generate dependency graph for Terraform resources
# Shows resource dependencies and relationships
#
# Usage: ./dependency-graph.sh [output_format]
# Format: dot, json, list
# Example: ./dependency-graph.sh dot > graph.dot

set -e

FORMAT="${1:-list}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

echo "📊 Terraform Dependency Graph" >&2
echo "Format: $FORMAT" >&2
echo "" >&2

# Generate graph
GRAPH_OUTPUT=$(terraform graph 2>/dev/null || echo "")

if [ -z "$GRAPH_OUTPUT" ]; then
    echo "Error: Could not generate graph. Is Terraform initialized?" >&2
    exit 1
fi

case "$FORMAT" in
    dot)
        echo "$GRAPH_OUTPUT"
        echo "" >&2
        echo "To visualize:" >&2
        echo "  terraform graph | dot -Tsvg > graph.svg" >&2
        echo "  terraform graph | dot -Tpng > graph.png" >&2
        ;;
    
    json)
        # Convert DOT to a simple JSON structure
        echo "$GRAPH_OUTPUT" | grep -E "^\s*[a-zA-Z]" | sed 's/\[label=.*\]//' | \
        awk '{
            if ($0 ~ /->/) {
                gsub(/[";]/, "", $1)
                gsub(/[";]/, "", $3)
                print "{ \"from\": \"" $1 "\", \"to\": \"" $3 "\" }"
            }
        }' | jq -s '.'
        ;;
    
    list|*)
        echo "Resource Dependencies:" >&2
        echo "$GRAPH_OUTPUT" | grep -E "->" | sed 's/\[label=.*\]//' | \
        sed 's/"//g' | sed 's/->/depends on/' | while read line; do
            if [ -n "$line" ]; then
                echo "  $line"
            fi
        done
        echo "" >&2
        echo "Total dependencies found" >&2
        ;;
esac

