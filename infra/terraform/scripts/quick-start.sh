#!/bin/bash
# Quick start script for Terraform setup
# Interactive script to bootstrap and initialize Terraform
#
# Usage: ./quick-start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Terraform Quick Start${NC}"
echo "This script will help you set up Terraform for the first time."
echo ""

# 1. Select provider
echo "Select your cloud provider:"
echo "  1) AWS"
echo "  2) Azure"
read -p "Choice [1-2]: " PROVIDER_CHOICE

case $PROVIDER_CHOICE in
    1) PROVIDER="aws";;
    2) PROVIDER="azure";;
    *) echo "Invalid choice"; exit 1;;
esac

# 2. Select environment
echo ""
echo "Select environment:"
echo "  1) Development (dev)"
echo "  2) Staging (stg)"
echo "  3) Production (prod)"
read -p "Choice [1-3]: " ENV_CHOICE

case $ENV_CHOICE in
    1) ENVIRONMENT="dev";;
    2) ENVIRONMENT="stg";;
    3) ENVIRONMENT="prod";;
    *) echo "Invalid choice"; exit 1;;
esac

# 3. Ask about backend
echo ""
echo "Do you need to bootstrap the backend? (recommended for first time)"
read -p "Bootstrap backend? [y/N]: " BOOTSTRAP

if [ "$BOOTSTRAP" = "y" ] || [ "$BOOTSTRAP" = "Y" ]; then
    echo ""
    if [ "$PROVIDER" = "aws" ]; then
        read -p "AWS Region [us-east-1]: " REGION
        REGION=${REGION:-us-east-1}
        echo "Booting backend..."
        ./bootstrap-backend-aws.sh "$ENVIRONMENT" "$REGION"
    else
        read -p "Azure Location [eastus]: " LOCATION
        LOCATION=${LOCATION:-eastus}
        echo "Booting backend..."
        ./bootstrap-backend-azure.sh "$ENVIRONMENT" "$LOCATION"
    fi
fi

# 4. Initialize Terraform
echo ""
echo "Initializing Terraform..."
./init-backend.sh "$PROVIDER" "$ENVIRONMENT"

# 5. Validate
echo ""
echo "Validating configuration..."
cd "$TERRAFORM_DIR"
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

terraform validate

# 6. Summary
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review and customize terraform.tfvars"
echo "  2. Run: terraform plan"
echo "  3. Run: terraform apply"
echo ""
echo "Useful commands:"
echo "  make tf-plan              - Plan changes"
echo "  make tf-apply              - Apply changes"
echo "  make tf-state-list         - List resources"
echo "  make tf-health-check PROVIDER=$PROVIDER ENV=$ENVIRONMENT - Health check"


