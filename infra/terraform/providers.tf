terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
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
  # See: infra/terraform/backend-configs/backend-{env}-{provider}.hcl
  # Initialize with: terraform init -backend-config=backend-configs/backend-dev-aws.hcl
  #
  # Example AWS S3 backend (uncomment and customize):
  # backend "s3" {
  #   bucket         = "tf-state-biz-automation"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "tf-state-locks"
  #   encrypt        = true
  #   # Optional: KMS encryption
  #   # kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"
  # }
  #
  # Example Azure Blob Storage backend (uncomment and customize):
  # backend "azurerm" {
  #   resource_group_name  = "rg-tfstate"
  #   storage_account_name = "sttfstate"
  #   container_name       = "tfstate"
  #   key                  = "dev/terraform.tfstate"
  #   subscription_id      = "YOUR_SUBSCRIPTION_ID"
  #   tenant_id            = "YOUR_TENANT_ID"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(local.tags, var.additional_tags)
  }
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
  # Set via environment variables: ARM_SUBSCRIPTION_ID, ARM_TENANT_ID, ARM_CLIENT_ID, ARM_CLIENT_SECRET
  #
  # Option 3: Managed Identity (for Azure VMs/App Services)
  # No configuration needed - automatically uses the system-assigned identity
}

# Random provider (for unique suffixes)
# Used in locals.tf


