# ============================================================================
# AWS Backend Configuration - Production Environment
# ============================================================================
#
# This file contains backend configuration for the production environment
# on AWS using S3 for state storage and DynamoDB for state locking.
#
# ⚠️  PRODUCTION ENVIRONMENT - USE WITH CAUTION
#
# Usage:
#   terraform init -backend-config=backend-configs/backend-prod-aws.hcl
#
# Or use the helper script:
#   ./scripts/init-backend.sh aws prod
#
# ============================================================================

bucket         = "tf-state-biz-automation-prod"
key            = "prod/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "tf-state-locks-prod"
encrypt        = true

# Production: Strongly recommended to use customer-managed KMS key
# Uncomment and set your KMS key ARN:
# kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"

# Production Best Practices:
# 1. Use a dedicated DynamoDB table for production (separate from dev/stg)
# 2. Enable KMS encryption with customer-managed key
# 3. Enable S3 bucket versioning (configured in bootstrap script)
# 4. Enable MFA delete on S3 bucket
# 5. Restrict IAM access to state bucket and DynamoDB table
# 6. Enable CloudTrail for audit logging

# Note: The S3 bucket and DynamoDB table must be created before using this backend.
# Use the bootstrap script to create them:
#   ./scripts/bootstrap-backend-aws.sh prod us-east-1
