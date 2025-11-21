variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "biz-automation"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev/stg/prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "Environment must be one of: dev, stg, prod."
  }
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
  validation {
    condition = contains([
      "eastus", "eastus2", "westus", "westus2", "westus3",
      "westeurope", "northeurope", "centralus", "southcentralus"
    ], var.location)
    error_message = "Azure location must be a valid Azure region."
  }
}

variable "resource_group_name" {
  description = "Resource group name (will be auto-generated if null)"
  type        = string
  default     = null
}

variable "vnet_cidr" {
  description = "Virtual Network CIDR block"
  type        = string
  default     = "10.30.0.0/16"
  validation {
    condition     = can(cidrhost(var.vnet_cidr, 0))
    error_message = "VNet CIDR must be a valid CIDR block."
  }
}

variable "subnet_cidrs" {
  description = "List of subnet CIDR blocks"
  type        = list(string)
  default     = ["10.30.1.0/24", "10.30.2.0/24"]
  validation {
    condition = alltrue([
      for subnet in var.subnet_cidrs : can(cidrhost(subnet, 0))
    ])
    error_message = "All subnets must be valid CIDR blocks."
  }
}

variable "aks_name" {
  description = "AKS cluster name (will be auto-generated if null)"
  type        = string
  default     = null
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS (defaults to latest stable)"
  type        = string
  default     = null
}

variable "adls_account_name" {
  description = "Storage account name for ADLS Gen2 (will be auto-generated if null, must be unique globally)"
  type        = string
  default     = null
}

variable "datalake_fs_name" {
  description = "Data Lake Gen2 filesystem (container) name"
  type        = string
  default     = "datalake"
}

variable "acr_name" {
  description = "Azure Container Registry name (will be auto-generated if null, must be unique globally)"
  type        = string
  default     = null
}

variable "enable_encryption" {
  description = "Enable encryption for storage accounts and managed disks"
  type        = bool
  default     = true
}

variable "storage_account_tier" {
  description = "Storage account tier (Standard or Premium)"
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Standard", "Premium"], var.storage_account_tier)
    error_message = "Storage account tier must be Standard or Premium."
  }
}

variable "storage_account_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"
  validation {
    condition = contains([
      "LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"
    ], var.storage_account_replication_type)
    error_message = "Storage replication type must be one of: LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS."
  }
}

variable "acr_sku" {
  description = "ACR SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

variable "aks_node_pools" {
  description = "AKS node pools configuration"
  type = map(object({
    node_count    = number
    vm_size       = string
    os_disk_size_gb = optional(number, 50)
    enable_auto_scaling = optional(bool, false)
    min_count     = optional(number)
    max_count     = optional(number)
    node_labels   = optional(map(string), {})
    node_taints   = optional(list(string), [])
  }))
  default = {
    default = {
      node_count      = 2
      vm_size         = "Standard_D4s_v5"
      os_disk_size_gb = 50
      enable_auto_scaling = false
      node_labels     = {}
      node_taints     = []
    }
  }
}

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}


