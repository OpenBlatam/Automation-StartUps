# Local values for consistent naming and tagging
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
  tags = local.environment_tags[var.environment]

  # Naming conventions
  name_prefix = "${var.project_name}-${var.environment}"
  name_suffix = "${var.project_name}-${var.environment}-${random_id.suffix.hex}"

  # Cluster configuration
  cluster_version = var.kubernetes_version != null ? var.kubernetes_version : "1.29"

  # Availability zones
  azs = length(var.availability_zones) > 0 ? var.availability_zones : [
    "${var.aws_region}a",
    "${var.aws_region}b",
    "${var.aws_region}c"
  ]

  # Subnet configuration validation
  private_subnet_count = length(var.private_subnets)
  public_subnet_count  = length(var.public_subnets)

  # Enable features based on environment
  enable_cluster_logging   = var.environment != "dev"
  enable_cluster_monitoring = true
  enable_encryption         = var.environment == "prod" || var.enable_encryption
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
  keepers = {
    environment = var.environment
    project     = var.project_name
  }
}



