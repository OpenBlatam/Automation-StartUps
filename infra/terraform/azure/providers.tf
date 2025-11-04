terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # Backend configuration is provided via backend config files or command line
  # This Azure module uses the backend-configs in the parent directory
  # See: ../backend-configs/backend-{env}-azure.hcl
  #
  # Initialize with:
  #   terraform init -backend-config=../backend-configs/backend-dev-azure.hcl
  #
  # Or use the helper script:
  #   ../scripts/init-backend.sh azure dev
  #
  # Example Azure Blob Storage backend (uncomment and customize):
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate"
  #   storage_account_name = "sttfstate"
  #   container_name       = "tfstate"
  #   key                  = "dev/terraform.tfstate"
  #   subscription_id      = "YOUR_SUBSCRIPTION_ID"
  #   tenant_id            = "YOUR_TENANT_ID"
  #   # Encryption is enabled by default on Azure Storage Accounts
  #   # Enable soft delete on storage account for state file recovery
  # }
}

provider "azurerm" {
  features {
    # Prevent accidental deletion of resource groups in production
    resource_group {
      prevent_deletion_if_contains_resources = var.environment == "prod"
    }

    # Enable key vault for secrets management (recommended)
    key_vault {
      purge_soft_delete_on_destroy    = var.environment != "prod"
      recover_soft_deleted_key_vaults = var.environment == "prod"
    }

    # Log analytics for monitoring
    log_analytics_workspace {
      permanently_delete_on_destroy = var.environment != "prod"
    }

    # Storage account features
    storage {
      recover_soft_deleted_accounts = true
      purge_soft_delete_on_destroy  = var.environment != "prod"
    }
  }

  # Authentication options (choose one):
  #
  # Option 1: Azure CLI (default) - Use: az login
  # No additional configuration needed when using Azure CLI authentication
  #
  # Option 2: Service Principal (for CI/CD)
  # Uncomment and set via environment variables or Terraform variables:
  # subscription_id = var.azure_subscription_id
  # tenant_id       = var.azure_tenant_id
  # client_id       = var.azure_client_id
  # client_secret   = var.azure_client_secret
  #
  # Option 3: Managed Identity (for Azure VMs/App Services)
  # No configuration needed - automatically uses the system-assigned identity
  #
  # Environment variables (alternative to variables):
  # ARM_SUBSCRIPTION_ID, ARM_TENANT_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET
}

# Kubernetes provider configuration
# Will be configured after AKS cluster is created
# See: main.tf for provider configuration using AKS cluster credentials

# Helm provider configuration
# Will be configured after AKS cluster is created
# See: main.tf for provider configuration using AKS cluster credentials


