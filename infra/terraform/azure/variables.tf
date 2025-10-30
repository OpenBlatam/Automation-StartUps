variable "environment" {
  description = "Environment name (dev/stg/prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "rg-biz-automation-dev"
}

variable "vnet_cidr" {
  description = "VNet CIDR"
  type        = string
  default     = "10.30.0.0/16"
}

variable "subnet_cidrs" {
  description = "Subnets CIDRs"
  type        = list(string)
  default     = ["10.30.1.0/24", "10.30.2.0/24"]
}

variable "aks_name" {
  description = "AKS cluster name"
  type        = string
  default     = "aks-biz-automation-dev"
}

variable "adls_account_name" {
  description = "Storage account name for ADLS Gen2"
  type        = string
  default     = "stbizautodev"
}

variable "datalake_fs_name" {
  description = "Data Lake filesystem (container) name"
  type        = string
  default     = "datalake"
}

variable "acr_name" {
  description = "Azure Container Registry name"
  type        = string
  default     = "acrbizautodev"
}
