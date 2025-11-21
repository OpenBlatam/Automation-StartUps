#!/bin/bash
# Generate documentation from Terraform configuration
# Extracts variables, outputs, and resources information
#
# Usage: ./generate-docs.sh [output-file]

set -e

OUTPUT_FILE="${1:-TERRAFORM_DOCS.md}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "📚 Generating Terraform documentation..."
echo ""

# Check if terraform-docs is available
if ! command -v terraform-docs &> /dev/null; then
    echo "⚠️  terraform-docs not found. Install with:"
    echo "   brew install terraform-docs  # macOS"
    echo "   # or"
    echo "   go install github.com/terraform-docs/terraform-docs@latest"
    echo ""
    echo "Generating basic documentation without terraform-docs..."
    GENERATE_BASIC=true
else
    GENERATE_BASIC=false
fi

cat > "$OUTPUT_FILE" << 'EOF'
# Terraform Configuration Documentation

This documentation is automatically generated from Terraform configuration files.

**Last Generated:** $(date)

## Overview

This Terraform configuration manages infrastructure for the project, supporting both AWS and Azure deployments.

EOF

# Add generation timestamp
sed -i.bak "s/\$(date)/$(date '+%Y-%m-%d %H:%M:%S')/g" "$OUTPUT_FILE"
rm -f "${OUTPUT_FILE}.bak"

# Generate using terraform-docs if available
if [ "$GENERATE_BASIC" = false ]; then
    echo "Generating detailed documentation..."
    
    # Variables
    echo "" >> "$OUTPUT_FILE"
    echo "## Input Variables" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    terraform-docs markdown table . >> "$OUTPUT_FILE" 2>/dev/null || echo "Could not generate variables documentation" >> "$OUTPUT_FILE"
    
    # Outputs
    echo "" >> "$OUTPUT_FILE"
    echo "## Outputs" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    if [ -f "outputs.tf" ]; then
        grep -E "^output " outputs.tf | sed 's/output "\(.*\)".*/### \1/' >> "$OUTPUT_FILE"
        grep -E "description.*=" outputs.tf | sed 's/.*description.*=.*"\(.*\)".*/- \1/' >> "$OUTPUT_FILE"
    fi
    
    # Resources
    echo "" >> "$OUTPUT_FILE"
    echo "## Resources" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    terraform-docs markdown resources . >> "$OUTPUT_FILE" 2>/dev/null || echo "Could not generate resources documentation" >> "$OUTPUT_FILE"
fi

# Basic documentation without terraform-docs
if [ "$GENERATE_BASIC" = true ]; then
    echo "Generating basic documentation..."
    
    # Variables
    echo "" >> "$OUTPUT_FILE"
    echo "## Input Variables" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    if [ -f "variables.tf" ]; then
        grep -E "^variable " variables.tf | while read -r line; do
            VAR_NAME=$(echo "$line" | sed 's/variable "\(.*\)".*/\1/')
            echo "### \`$VAR_NAME\`" >> "$OUTPUT_FILE"
            # Get description
            grep -A 5 "variable \"$VAR_NAME\"" variables.tf | grep "description" | head -1 | sed 's/.*description.*=.*"\(.*\)".*/  **Description:** \1/' >> "$OUTPUT_FILE"
            # Get type
            grep -A 5 "variable \"$VAR_NAME\"" variables.tf | grep "type" | head -1 | sed 's/.*type.*=.*\(.*\)/  **Type:** \1/' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        done
    fi
    
    # Outputs
    echo "" >> "$OUTPUT_FILE"
    echo "## Outputs" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    if [ -f "outputs.tf" ]; then
        grep -E "^output " outputs.tf | while read -r line; do
            OUT_NAME=$(echo "$line" | sed 's/output "\(.*\)".*/\1/')
            echo "### \`$OUT_NAME\`" >> "$OUTPUT_FILE"
            grep -A 3 "output \"$OUT_NAME\"" outputs.tf | grep "description" | head -1 | sed 's/.*description.*=.*"\(.*\)".*/  **Description:** \1/' >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
        done
    fi
fi

# Add usage examples
cat >> "$OUTPUT_FILE" << 'EOF'

## Usage Examples

### Basic Usage

```bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

### With Backend

```bash
# Initialize with backend
terraform init -backend-config=backend-configs/backend-dev-aws.hcl

# Apply
terraform apply
```

### Using Variables

```bash
# Via command line
terraform apply -var="environment=prod"

# Via file
terraform apply -var-file=terraform.tfvars

# Via environment variables
export TF_VAR_environment=prod
terraform apply
```

## Related Documentation

- [State Management Guide](./STATE_MANAGEMENT.md)
- [Quick Start Guide](./README_STATE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Scripts Documentation](./scripts/README.md)

EOF

echo "✅ Documentation generated: $OUTPUT_FILE"
echo ""
echo "To update this documentation, run:"
echo "  ./scripts/generate-docs.sh"

