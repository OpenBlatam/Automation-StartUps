#!/bin/bash
# Initialize Terraform with remote backend configuration
#
# Usage: ./init-backend.sh [provider] [environment]
# Example: ./init-backend.sh aws dev
# Example: ./init-backend.sh azure prod

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_CONFIG_DIR="$TERRAFORM_DIR/backend-configs"

if [ ! -d "$BACKEND_CONFIG_DIR" ]; then
    echo "Error: Backend config directory not found: $BACKEND_CONFIG_DIR"
    exit 1
fi

BACKEND_CONFIG_FILE="$BACKEND_CONFIG_DIR/backend-${ENVIRONMENT}-${PROVIDER}.hcl"

if [ ! -f "$BACKEND_CONFIG_FILE" ]; then
    echo "Error: Backend config file not found: $BACKEND_CONFIG_FILE"
    echo "Available configs:"
    ls -1 "$BACKEND_CONFIG_DIR"/backend-*.hcl 2>/dev/null || echo "  None found"
    exit 1
fi

echo "Initializing Terraform with remote backend"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo "Backend config: $BACKEND_CONFIG_FILE"
echo ""

cd "$TERRAFORM_DIR"

# For Azure, also navigate to azure subdirectory if it exists
if [ "$PROVIDER" = "azure" ] && [ -d "$TERRAFORM_DIR/azure" ]; then
    echo "Using Azure-specific Terraform configuration"
    cd "$TERRAFORM_DIR/azure"
fi

# Initialize Terraform with backend configuration
terraform init \
    -backend-config="$BACKEND_CONFIG_FILE" \
    -upgrade

echo ""
echo "✅ Terraform initialized successfully with remote backend!"
echo ""
echo "Next steps:"
echo "  terraform plan"
echo "  terraform apply"



