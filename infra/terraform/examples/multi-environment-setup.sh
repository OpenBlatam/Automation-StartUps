#!/bin/bash
# Example script for setting up multiple environments
# Demonstrates best practices for multi-environment management
#
# Usage: ./multi-environment-setup.sh [provider]
# Example: ./multi-environment-setup.sh aws

set -e

PROVIDER="${1:-aws}"

echo "🌍 Multi-Environment Setup"
echo "Provider: $PROVIDER"
echo ""
echo "This script demonstrates setting up multiple environments"
echo "following best practices for state management."
echo ""

ENVIRONMENTS=("dev" "stg" "prod")

for ENV in "${ENVIRONMENTS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Setting up environment: $ENV"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 1. Bootstrap backend (if needed)
    echo "1. Bootstrap backend..."
    if [ "$PROVIDER" = "aws" ]; then
        echo "   Run: ./bootstrap-backend-aws.sh $ENV us-east-1"
    else
        echo "   Run: ./bootstrap-backend-azure.sh $ENV eastus"
    fi
    echo ""
    
    # 2. Initialize
    echo "2. Initialize Terraform..."
    echo "   Run: ./init-backend.sh $PROVIDER $ENV"
    echo ""
    
    # 3. Validate
    echo "3. Validate configuration..."
    echo "   Run: terraform validate"
    echo ""
    
    # 4. Plan
    echo "4. Plan changes..."
    echo "   Run: terraform plan -var-file=terraform.tfvars.$ENV"
    echo ""
    
    echo "Environment $ENV setup complete!"
    echo ""
done

echo "✅ Multi-environment setup guide complete!"
echo ""
echo "Best practices:"
echo "  - Use separate backend keys for each environment"
echo "  - Use environment-specific tfvars files"
echo "  - Never share state between environments"
echo "  - Use separate buckets/storage accounts for production"
echo "  - Implement different security policies per environment"

