variable "environment" {
  description = "Environment name (dev/stg/prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region when provider=aws"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "Kubernetes cluster name"
  type        = string
  default     = "biz-automation-dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.20.0.0/16"
}

variable "private_subnets" {
  description = "Private subnets"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "public_subnets" {
  description = "Public subnets"
  type        = list(string)
  default     = ["10.20.11.0/24", "10.20.12.0/24"]
}

variable "datalake_bucket" {
  description = "Data Lake bucket/container name"
  type        = string
  default     = "biz-datalake-dev"
}
