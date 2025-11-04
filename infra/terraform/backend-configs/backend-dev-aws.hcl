# ============================================================================
# AWS Backend Configuration - Development Environment
# ============================================================================
#
# This file contains backend configuration for the development environment
# on AWS using S3 for state storage and DynamoDB for state locking.
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-dev-aws.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh aws dev
#
# ============================================================================

bucket         = "tf-state-biz-automation-dev"
key            = "dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "tf-state-locks"
encrypt        = true

# Optional: Use customer-managed KMS key for enhanced security (recommended for production)
# Uncomment and set your KMS key ARN:
# kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"

# Optional: Enable server-side encryption with AWS-managed keys (default if kms_key_id not set)
# Uses SSE-S3 encryption by default

# Note: The S3 bucket and DynamoDB table must be created before using this backend.
# Use the bootstrap script to create them:
#   ./scripts/bootstrap-backend-aws.sh dev us-east-1
