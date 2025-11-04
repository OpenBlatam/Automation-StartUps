# ============================================================================
# Azure Backend Configuration - Production Environment
# ============================================================================
#
# This file contains backend configuration for the production environment
# on Azure using Blob Storage for state storage.
#
# ⚠️  PRODUCTION ENVIRONMENT - USE WITH CAUTION
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-prod-azure.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh azure prod
#
# ============================================================================

resource_group_name  = "rg-tfstate-prod"
storage_account_name = "sttfstateprod"  # Must be globally unique, lowercase, alphanumeric
container_name       = "tfstate"
key                  = "prod/terraform.tfstate"

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

# Production Best Practices:
# 1. Use a dedicated storage account for production (separate from dev/stg)
# 2. Enable soft delete and blob versioning on storage account
# 3. Use Azure Key Vault for secrets management
# 4. Enable diagnostic logs and monitoring
# 5. Restrict RBAC access to storage account
# 6. Use Private Endpoints for storage account access (if network isolation required)

# Note: The storage account and container must be created before using this backend.
# Use the bootstrap script to create them:
#   ./scripts/bootstrap-backend-azure.sh prod eastus
