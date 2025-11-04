# Local values for Azure resources
locals {
  # Common tags applied to all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    CreatedAt   = formatdate("YYYY-MM-DD", timestamp())
  }

  # Environment-specific tags
  environment_tags = {
    dev  = merge(local.common_tags, { CostCenter = "Development", Backup = "Daily" })
    stg  = merge(local.common_tags, { CostCenter = "Staging", Backup = "Daily" })
    prod = merge(local.common_tags, { CostCenter = "Production", Backup = "Hourly", Compliance = "Required" })
  }

  # Final tags to use
  tags = merge(local.environment_tags[var.environment], var.additional_tags)

  # Naming conventions (Azure naming requirements)
  name_prefix = "${var.project_name}-${var.environment}"
  name_suffix = "${var.project_name}-${var.environment}-${substr(random_id.suffix.hex, 0, 4)}"

  # Azure-specific naming (must be lowercase, alphanumeric, and hyphens)
  resource_group_name = coalesce(var.resource_group_name, "rg-${lower(replace(local.name_prefix, "_", "-"))}")
  aks_name            = coalesce(var.aks_name, lower("aks-${replace(local.name_prefix, "_", "-")}"))
  vnet_name           = lower("vnet-${replace(local.name_prefix, "_", "-")}")
  storage_account_name = coalesce(
    var.adls_account_name,
    lower(substr("st${replace(local.name_prefix, "-", "")}", 0, 24))
  )
  acr_name = coalesce(
    var.acr_name,
    lower(substr("acr${replace(local.name_prefix, "-", "")}", 0, 50))
  )

  # Enable features based on environment
  enable_aks_logging   = var.environment != "dev"
  enable_storage_encryption = var.environment == "prod" || var.enable_encryption
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
  keepers = {
    environment = var.environment
    project     = var.project_name
    location    = var.location
  }
}



