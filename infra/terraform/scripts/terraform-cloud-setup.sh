#!/bin/bash
# Setup Terraform Cloud configuration
# Helps migrate to or configure Terraform Cloud
#
# Usage: ./terraform-cloud-setup.sh [organization] [workspace]
# Example: ./terraform-cloud-setup.sh my-org production

set -e

ORG="${1}"
WORKSPACE="${2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

if [ -z "$ORG" ] || [ -z "$WORKSPACE" ]; then
    echo "Usage: $0 [organization] [workspace]"
    echo ""
    echo "This will create a terraform.tf file with Terraform Cloud configuration"
    echo ""
    echo "Example:"
    echo "  ./terraform-cloud-setup.sh my-org production"
    exit 1
fi

echo "☁️  Setting up Terraform Cloud"
echo "Organization: $ORG"
echo "Workspace: $WORKSPACE"
echo ""

# Check if terraform.tf exists
if [ -f "terraform.tf" ]; then
    echo "⚠️  terraform.tf already exists"
    read -p "Backup and overwrite? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    cp terraform.tf terraform.tf.backup
fi

# Create Terraform Cloud configuration
cat > terraform.tf <<EOF
terraform {
  cloud {
    organization = "$ORG"
    
    workspaces {
      name = "$WORKSPACE"
    }
  }
  
  required_version = ">= 1.6.0"
  
  required_providers {
    # Add your providers here
  }
}
EOF

echo "✅ Terraform Cloud configuration created"
echo ""
echo "Next steps:"
echo "  1. Login to Terraform Cloud:"
echo "     terraform login"
echo ""
echo "  2. Initialize:"
echo "     terraform init"
echo ""
echo "  3. Configure variables in Terraform Cloud UI"
echo "  4. Run plan/apply as usual"
echo ""
echo "⚠️  Note:"
echo "  - Remove any existing backend configs"
echo "  - Configure variables in Terraform Cloud UI"
echo "  - Sensitive variables are automatically secured"

