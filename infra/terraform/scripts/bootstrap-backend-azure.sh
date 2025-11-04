#!/bin/bash
# Bootstrap script to create Azure backend resources for Terraform state
# This script creates the Storage Account and Container required for remote state management
#
# Usage: ./bootstrap-backend-azure.sh [environment] [location]
# Example: ./bootstrap-backend-azure.sh dev eastus

set -e

ENVIRONMENT="${1:-dev}"
LOCATION="${2:-eastus}"
RESOURCE_GROUP="rg-tfstate"
STORAGE_ACCOUNT="sttfstate"
CONTAINER_NAME="tfstate"

# Production uses separate resources
if [ "$ENVIRONMENT" = "prod" ]; then
    RESOURCE_GROUP="rg-tfstate-prod"
    STORAGE_ACCOUNT="sttfstateprod"
fi

echo "Bootstrapping Terraform backend for environment: $ENVIRONMENT"
echo "Location: $LOCATION"
echo "Resource Group: $RESOURCE_GROUP"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Container: $CONTAINER_NAME"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "Error: Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Subscription ID: $SUBSCRIPTION_ID"

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
if az group show --name "$RESOURCE_GROUP" --output none 2>/dev/null; then
    echo "Resource group $RESOURCE_GROUP already exists, skipping creation"
else
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags Environment="$ENVIRONMENT" Purpose=TerraformState
    echo "Resource group created successfully"
fi

# Create storage account
echo "Creating storage account: $STORAGE_ACCOUNT"
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
    echo "Storage account $STORAGE_ACCOUNT already exists, skipping creation"
else
    # Storage account name must be globally unique and 3-24 characters, lowercase, alphanumeric
    az storage account create \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku Standard_LRS \
        --kind StorageV2 \
        --allow-blob-public-access false \
        --min-tls-version TLS1_2 \
        --tags Environment="$ENVIRONMENT" Purpose=TerraformState
    
    echo "Storage account created successfully"
fi

# Enable soft delete for blob storage (state file recovery)
echo "Enabling soft delete for blob storage"
az storage blob service-properties update \
    --account-name "$STORAGE_ACCOUNT" \
    --enable-delete-retention true \
    --delete-retention-days 30

# Enable versioning
echo "Enabling versioning for blob storage"
az storage blob service-properties update \
    --account-name "$STORAGE_ACCOUNT" \
    --enable-versioning true

# Create container
echo "Creating container: $CONTAINER_NAME"
if az storage container show --name "$CONTAINER_NAME" --account-name "$STORAGE_ACCOUNT" --output none 2>/dev/null; then
    echo "Container $CONTAINER_NAME already exists, skipping creation"
else
    az storage container create \
        --name "$CONTAINER_NAME" \
        --account-name "$STORAGE_ACCOUNT" \
        --public-access off
    echo "Container created successfully"
fi

# Get storage account key (for reference, prefer using managed identity in CI/CD)
STORAGE_KEY=$(az storage account keys list \
    --resource-group "$RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --query "[0].value" -o tsv)

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

echo ""
echo "✅ Backend bootstrap complete!"
echo ""
echo "Storage Account Details:"
echo "  Name: $STORAGE_ACCOUNT"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container: $CONTAINER_NAME"
echo ""
echo "Next steps:"
echo "1. Update backend-configs/backend-${ENVIRONMENT}-azure.hcl:"
echo "   - subscription_id = \"$SUBSCRIPTION_ID\""
echo "   - tenant_id = \"$TENANT_ID\""
echo "2. Initialize Terraform:"
echo "   cd infra/terraform"
echo "   terraform init -backend-config=backend-configs/backend-${ENVIRONMENT}-azure.hcl"
echo ""
echo "Note: For CI/CD, prefer using Managed Identity or Service Principal"
echo "instead of storage account keys for authentication."



