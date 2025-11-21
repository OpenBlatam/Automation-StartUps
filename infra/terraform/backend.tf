# ============================================================================
# Remote Backend Configuration
# ============================================================================
#
# This file defines the backend type but NOT the configuration values.
# Backend configuration values are provided via:
#   1. Backend config files in backend-configs/ directory
#   2. Command-line flags during terraform init
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-dev-aws.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh aws dev
#
# ============================================================================

terraform {
  # Backend configuration is provided via backend config files or command line
  # See: infra/terraform/backend-configs/backend-{env}-{provider}.hcl
  # Initialize with: terraform init -backend-config=backend-configs/backend-dev-aws.hcl

  # AWS S3 Backend (default for AWS deployments)
  backend "s3" {
    # Configuration values are provided via:
    #   -backend-config=backend-configs/backend-{env}-aws.hcl
    #   -backend-config="bucket=..." -backend-config="key=..." (command line)
    #
    # Example values (set in backend config file):
    #   bucket         = "tf-state-biz-automation"
    #   key            = "dev/terraform.tfstate"
    #   region         = "us-east-1"
    #   dynamodb_table = "tf-state-locks"
    #   encrypt        = true
    #   kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"  # Optional
  }

  # Alternative backends can be configured by uncommenting and configuring:
  
  # Azure Blob Storage Backend (for Azure deployments)
  # backend "azurerm" {
  #   # Configuration via -backend-config=backend-configs/backend-{env}-azure.hcl
  #   # Example values:
  #   #   resource_group_name  = "rg-tfstate"
  #   #   storage_account_name = "sttfstate"
  #   #   container_name       = "tfstate"
  #   #   key                  = "dev/terraform.tfstate"
  #   #   subscription_id     = "YOUR_SUBSCRIPTION_ID"
  #   #   tenant_id           = "YOUR_TENANT_ID"
  # }

  # GCS Backend (for GCP deployments)
  # backend "gcs" {
  #   # Configuration via -backend-config=backend-configs/backend-{env}-gcp.hcl
  #   # Example values:
  #   #   bucket = "tf-state-biz-automation"
  #   #   prefix = "dev/terraform.tfstate"
  #   #   encryption_key = "projects/PROJECT_ID/locations/LOCATION/keyRings/RING/cryptoKeys/KEY"
  # }
}
