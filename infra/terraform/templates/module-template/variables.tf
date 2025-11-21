# Module Variables
# Define all input variables for this module

variable "name" {
  description = "Resource name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "Environment must be dev, stg, or prod."
  }
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

