# ============================================================================
# Azure Backend Configuration - Staging Environment
# ============================================================================
#
# This file contains backend configuration for the staging environment
# on Azure using Blob Storage for state storage.
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-stg-azure.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh azure stg
#
# ============================================================================

resource_group_name  = "rg-tfstate-stg"
storage_account_name = "sttfstatestg"  # Must be globally unique, lowercase, alphanumeric
container_name       = "tfstate"
key                  = "stg/terraform.tfstate"

# Azure authentication - configure one of the following:
#
# Option 1: Using Service Principal (recommended for CI/CD)
# subscription_id = "YOUR_SUBSCRIPTION_ID"
# tenant_id       = "YOUR_TENANT_ID"
# client_id       = "YOUR_CLIENT_ID"
# client_secret   = "YOUR_CLIENT_SECRET"  # Set via environment variable: ARM_CLIENT_SECRET

# Option 2: Using Managed Identity (recommended for Azure-hosted CI/CD)
# No additional configuration needed when running on Azure

# Option 3: Using Azure CLI authentication (for local development)
# Run: az login
# No additional configuration needed

# Note: The storage account and container must be created before using this backend.
# Use the bootstrap script to create them:
#   ./scripts/bootstrap-backend-azure.sh stg eastus
