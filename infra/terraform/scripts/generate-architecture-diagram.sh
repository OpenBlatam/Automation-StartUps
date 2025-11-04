#!/bin/bash
# Generate architecture diagram from Terraform
# Creates a DOT file for Graphviz visualization
#
# Usage: ./generate-architecture-diagram.sh [output_file]
# Example: ./generate-architecture-diagram.sh architecture.dot

set -e

OUTPUT_FILE="${1:-architecture.dot}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

echo "📊 Generating Architecture Diagram"
echo "Output: $OUTPUT_FILE"
echo ""

# Use Terraform graph command
if terraform graph > "$OUTPUT_FILE" 2>/dev/null; then
    echo "✅ Diagram generated: $OUTPUT_FILE"
    echo ""
    echo "To visualize:"
    echo "  # SVG (recommended)"
    echo "  dot -Tsvg $OUTPUT_FILE > architecture.svg"
    echo ""
    echo "  # PNG"
    echo "  dot -Tpng $OUTPUT_FILE > architecture.png"
    echo ""
    echo "  # PDF"
    echo "  dot -Tpdf $OUTPUT_FILE > architecture.pdf"
    echo ""
    echo "Requirements:"
    echo "  Install Graphviz: brew install graphviz (macOS) or apt-get install graphviz (Linux)"
else
    echo "Error: Could not generate diagram"
    echo "Run 'terraform init' first if needed"
    exit 1
fi

