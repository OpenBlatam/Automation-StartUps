# Backend configuration for Azure (Blob Storage)
# This file can be sourced or used as a reference for backend configuration
# 
# Usage:
#   terraform init -backend-config=backend-azure.tf \
#                  -backend-config="key=dev/terraform.tfstate" \
#                  -backend-config="resource_group_name=rg-tfstate"

terraform {
  # Backend configuration can be set via command line or backend config files
  # Command line example:
  # terraform init -backend-config="resource_group_name=rg-tfstate" \
  #                -backend-config="storage_account_name=sttfstate" \
  #                -backend-config="container_name=tfstate" \
  #                -backend-config="key=dev/terraform.tfstate" \
  #                -backend-config="subscription_id=SUBSCRIPTION_ID"
  
  # Or use a backend config file:
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate"
  #   storage_account_name = "sttfstate"
  #   container_name       = "tfstate"
  #   key                  = "dev/terraform.tfstate"
  #   subscription_id      = "YOUR_SUBSCRIPTION_ID"
  #   tenant_id            = "YOUR_TENANT_ID"
  #   
  #   # Encryption is enabled by default on Azure Storage Accounts
  #   # Enable soft delete for state file recovery
  # }
}

# Storage Account for Terraform state (should be created separately or via bootstrap)
# This resource should be created FIRST before using remote backend
# Use: infra/terraform/scripts/bootstrap-backend.sh



