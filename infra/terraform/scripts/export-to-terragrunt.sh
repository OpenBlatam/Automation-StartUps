#!/bin/bash
# Convert Terraform configuration to Terragrunt format
# Helps migration to Terragrunt for DRY configurations
#
# Usage: ./export-to-terragrunt.sh [output_dir]
# Example: ./export-to-terragrunt.sh terragrunt-config

set -e

OUTPUT_DIR="${1:-terragrunt-config}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 Converting to Terragrunt Format"
echo "Output directory: $OUTPUT_DIR"
echo ""

cd "$TERRAFORM_DIR"

mkdir -p "$OUTPUT_DIR"

# Create terragrunt.hcl structure
cat > "$OUTPUT_DIR/terragrunt.hcl" <<EOF
# Terragrunt Configuration
# Generated from Terraform config

terraform {
  source = "../../modules/terraform"  # Adjust path as needed
}

# Include common configuration
include {
  path = find_in_parent_folders()
}

# Inputs from terraform.tfvars
inputs = {
  # Add your variables here
  # environment = "dev"
  # project_name = "biz-automation"
}
EOF

# Create common terragrunt.hcl
mkdir -p "$OUTPUT_DIR/common"
cat > "$OUTPUT_DIR/common/terragrunt.hcl" <<EOF
# Common Terragrunt Configuration
# Shared settings for all environments

remote_state {
  backend = "s3"  # or "azurerm"
  
  config = {
    # Backend configuration
    # Will be environment-specific
  }
  
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# Generate providers
generate "provider" {
  path      = "providers.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
EOF
}
EOF

# Create environment-specific configs
for env in dev stg prod; do
    mkdir -p "$OUTPUT_DIR/$env"
    cat > "$OUTPUT_DIR/$env/terragrunt.hcl" <<EOF
# Terragrunt Configuration for $env

include {
  path = find_in_parent_folders("common/terragrunt.hcl")
}

remote_state {
  config = {
    # Backend config for $env
    key = "$env/terraform.tfstate"
  }
}

inputs = {
  environment = "$env"
}
EOF
done

echo "✅ Terragrunt configuration created in: $OUTPUT_DIR"
echo ""
echo "Directory structure:"
echo "  $OUTPUT_DIR/"
echo "    ├── terragrunt.hcl"
echo "    ├── common/"
echo "    │   └── terragrunt.hcl"
echo "    ├── dev/"
echo "    │   └── terragrunt.hcl"
echo "    ├── stg/"
echo "    │   └── terragrunt.hcl"
echo "    └── prod/"
echo "        └── terragrunt.hcl"
echo ""
echo "Next steps:"
echo "  1. Install Terragrunt: brew install terragrunt"
echo "  2. Customize configurations"
echo "  3. Run: terragrunt plan-all"

