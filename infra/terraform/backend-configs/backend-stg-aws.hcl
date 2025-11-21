# ============================================================================
# AWS Backend Configuration - Staging Environment
# ============================================================================
#
# This file contains backend configuration for the staging environment
# on AWS using S3 for state storage and DynamoDB for state locking.
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-stg-aws.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh aws stg
#
# ============================================================================

bucket         = "tf-state-biz-automation-stg"
key            = "stg/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "tf-state-locks"
encrypt        = true

# Optional: Use customer-managed KMS key for enhanced security (recommended)
# Uncomment and set your KMS key ARN:
# kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"

# Note: The S3 bucket and DynamoDB table must be created before using this backend.
# Use the bootstrap script to create them:
#   ./scripts/bootstrap-backend-aws.sh stg us-east-1
