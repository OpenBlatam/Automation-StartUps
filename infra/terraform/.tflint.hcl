# TFLint Configuration
# See: https://github.com/terraform-linters/tflint

config {
  # Enable module inspection
  module = true
  
  # Force required providers to have versions
  force = false
  
  # Disable rules that are too opinionated
  disabled_by_default = false
}

# Plugin configuration
plugin "aws" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "azurerm" {
  enabled = true
  version = "0.29.0"
  source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}

# Rule overrides
rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_deprecated_index" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_comment_syntax" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_documented_modules" {
  enabled = true
}

rule "terraform_typed_variables" {
  enabled = true
}

rule "terraform_module_pinned_source" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_required_providers" {
  enabled = true
}

rule "terraform_required_version" {
  enabled = true
}

rule "terraform_standard_module_structure" {
  enabled = true
}

# AWS-specific rules
rule "aws_resource_missing_tags" {
  enabled = false  # We use default_tags in provider
}

rule "aws_instance_previous_type" {
  enabled = true
}

rule "aws_route_not_specified_target" {
  enabled = true
}

rule "aws_route_invalid_route_table" {
  enabled = true
}

rule "aws_s3_bucket_invalid_name" {
  enabled = true
}

# Azure-specific rules
rule "azurerm_resource_missing_tags" {
  enabled = false  # We use tags in locals
}

rule "azurerm_storage_account_invalid_name" {
  enabled = true
}

rule "azurerm_storage_container_invalid_name" {
  enabled = true
}



