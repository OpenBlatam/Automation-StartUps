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

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-southeast-1", "ap-southeast-2"
    ], var.aws_region)
    error_message = "AWS region must be a valid AWS region."
  }
}

variable "cluster_name" {
  description = "Kubernetes cluster name (will be prefixed with project and environment if null)"
  type        = string
  default     = ""
}

variable "kubernetes_version" {
  description = "Kubernetes version for the cluster (defaults to latest stable)"
  type        = string
  default     = null
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.20.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid CIDR block."
  }
}

variable "availability_zones" {
  description = "List of availability zones to use (empty list uses default zones for region)"
  type        = list(string)
  default     = []
}

variable "private_subnets" {
  description = "List of private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
  validation {
    condition = alltrue([
      for subnet in var.private_subnets : can(cidrhost(subnet, 0))
    ])
    error_message = "All private subnets must be valid CIDR blocks."
  }
}

variable "public_subnets" {
  description = "List of public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.20.11.0/24", "10.20.12.0/24"]
  validation {
    condition = alltrue([
      for subnet in var.public_subnets : can(cidrhost(subnet, 0))
    ])
    error_message = "All public subnets must be valid CIDR blocks."
  }
}

variable "datalake_bucket" {
  description = "Data Lake S3 bucket name (will be prefixed with project and environment if null)"
  type        = string
  default     = ""
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single shared NAT Gateway for all private subnets (cost optimization)"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = false
}

variable "enable_encryption" {
  description = "Enable encryption for data at rest (S3, EBS, etc.)"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (if null, AWS managed keys are used)"
  type        = string
  default     = null
  sensitive   = true
}

variable "eks_node_groups" {
  description = "EKS managed node groups configuration"
  type = map(object({
    min_size     = number
    max_size     = number
    desired_size = number
    instance_types = list(string)
    disk_size    = optional(number, 50)
    capacity_type = optional(string, "ON_DEMAND") # ON_DEMAND or SPOT
    labels       = optional(map(string), {})
    taints       = optional(list(object({
      key    = string
      value  = optional(string)
      effect = string
    })), [])
  }))
  default = {
    default = {
      min_size      = 1
      max_size      = 3
      desired_size  = 2
      instance_types = ["m5.large"]
      disk_size     = 50
      capacity_type = "ON_DEMAND"
      labels        = {}
      taints        = []
    }
  }
}

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

