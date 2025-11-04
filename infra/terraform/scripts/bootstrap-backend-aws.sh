#!/bin/bash
# Bootstrap script to create AWS backend resources for Terraform state
# This script creates the S3 bucket and DynamoDB table required for remote state management
#
# Usage: ./bootstrap-backend-aws.sh [environment] [region]
# Example: ./bootstrap-backend-aws.sh dev us-east-1

set -e

ENVIRONMENT="${1:-dev}"
REGION="${2:-us-east-1}"
BUCKET_NAME="tf-state-biz-automation"
DYNAMODB_TABLE="tf-state-locks"

# Production uses separate bucket
if [ "$ENVIRONMENT" = "prod" ]; then
    BUCKET_NAME="tf-state-biz-automation-prod"
    DYNAMODB_TABLE="tf-state-locks-prod"
fi

echo "Bootstrapping Terraform backend for environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "S3 Bucket: $BUCKET_NAME"
echo "DynamoDB Table: $DYNAMODB_TABLE"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    exit 1
fi

# Create S3 bucket for state storage
echo "Creating S3 bucket: $BUCKET_NAME"
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "Bucket $BUCKET_NAME already exists, skipping creation"
else
    # Create bucket with versioning and encryption
    if [ "$REGION" = "us-east-1" ]; then
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"
    fi
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Enable encryption (SSE-S3)
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }'
    
    # Block public access
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration \
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
    
    echo "S3 bucket created successfully"
fi

# Create DynamoDB table for state locking
echo "Creating DynamoDB table: $DYNAMODB_TABLE"
if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" --region "$REGION" 2>/dev/null; then
    echo "DynamoDB table $DYNAMODB_TABLE already exists, skipping creation"
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION" \
        --tags Key=Environment,Value="$ENVIRONMENT" Key=Purpose,Value=TerraformStateLock
    
    echo "Waiting for table to be active..."
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$REGION"
    echo "DynamoDB table created successfully"
fi

echo ""
echo "✅ Backend bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Update backend-configs/backend-${ENVIRONMENT}-aws.hcl with your configuration"
echo "2. Initialize Terraform:"
echo "   cd infra/terraform"
echo "   terraform init -backend-config=backend-configs/backend-${ENVIRONMENT}-aws.hcl"
echo ""
echo "For KMS encryption (recommended for production):"
echo "   aws kms create-key --description 'Terraform State Encryption' --region $REGION"
echo "   Then add the KMS key ARN to your backend configuration"



