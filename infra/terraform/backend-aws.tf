# Backend configuration for AWS (S3 + DynamoDB)
# This file can be sourced or used as a reference for backend configuration
# 
# Usage:
#   terraform init -backend-config=backend-aws.tf \
#                  -backend-config="key=dev/terraform.tfstate" \
#                  -backend-config="bucket=tf-state-biz-automation"

terraform {
  # Backend configuration can be set via command line or backend config files
  # Command line example:
  # terraform init -backend-config="bucket=tf-state-biz-automation" \
  #                -backend-config="key=dev/terraform.tfstate" \
  #                -backend-config="region=us-east-1" \
  #                -backend-config="dynamodb_table=tf-state-locks" \
  #                -backend-config="encrypt=true"
  
  # Or use a backend config file:
  # backend "s3" {
  #   bucket         = "tf-state-biz-automation"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "tf-state-locks"
  #   encrypt        = true
  #   kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID" # Optional: Custom KMS key
  #   
  #   # Versioning enabled on bucket for state history
  #   # Enable server-side encryption (SSE-S3 or SSE-KMS)
  # }
}

# S3 bucket for Terraform state (should be created separately or via bootstrap)
# This resource should be created FIRST before using remote backend
# Use: infra/terraform/scripts/bootstrap-backend.sh

# DynamoDB table for state locking (should be created separately)
# Use: infra/terraform/scripts/bootstrap-backend.sh



