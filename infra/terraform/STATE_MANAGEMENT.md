# Terraform State Management Guide

This guide covers best practices for managing Terraform state in this project, including remote backends, state locking, encryption, and environment separation.

## Table of Contents

1. [Overview](#overview)
2. [Backend Configuration](#backend-configuration)
3. [Initial Setup](#initial-setup)
4. [Environment Management](#environment-management)
5. [State Operations](#state-operations)
6. [Security Best Practices](#security-best-practices)
7. [Disaster Recovery](#disaster-recovery)
8. [Troubleshooting](#troubleshooting)

## Overview

Terraform state files track the mapping between your configuration and the real-world resources. For team collaboration and production use, it's critical to:

- **Use remote backends** (S3, Azure Blob) for centralized state management
- **Enable state locking** to prevent concurrent modifications
- **Encrypt state at rest** to protect sensitive data
- **Separate state by environment** (dev/stg/prod) for isolation
- **Version control state history** for recovery and auditing

## Backend Configuration

### AWS Backend (S3 + DynamoDB)

The AWS backend uses:
- **S3 bucket** for state storage with versioning
- **DynamoDB table** for state locking
- **Encryption** enabled (SSE-S3 or SSE-KMS)

Configuration files are located in `backend-configs/backend-{env}-aws.hcl`:

```hcl
bucket         = "tf-state-biz-automation"
key            = "dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "tf-state-locks"
encrypt        = true
```

### Azure Backend (Blob Storage)

The Azure backend uses:
- **Storage Account** with blob container
- **Built-in encryption** (Azure Storage encryption)
- **Soft delete** enabled for state recovery

Configuration files are located in `backend-configs/backend-{env}-azure.hcl`:

```hcl
resource_group_name  = "rg-tfstate"
storage_account_name = "sttfstate"
container_name       = "tfstate"
key                  = "dev/terraform.tfstate"
subscription_id      = "YOUR_SUBSCRIPTION_ID"
tenant_id            = "YOUR_TENANT_ID"
```

## Initial Setup

### Step 1: Bootstrap Backend Resources

Before using remote backends, you need to create the backend infrastructure.

#### AWS

```bash
cd infra/terraform/scripts
chmod +x bootstrap-backend-aws.sh
./bootstrap-backend-aws.sh dev us-east-1
```

This creates:
- S3 bucket with versioning and encryption
- DynamoDB table for state locking
- Proper IAM permissions and security settings

#### Azure

```bash
cd infra/terraform/scripts
chmod +x bootstrap-backend-azure.sh
./bootstrap-backend-azure.sh dev eastus
```

This creates:
- Resource group for Terraform state
- Storage account with encryption
- Blob container for state files
- Soft delete enabled

### Step 2: Configure Backend

Edit the appropriate backend configuration file in `backend-configs/`:

**For AWS**: `backend-configs/backend-dev-aws.hcl`
- Update bucket name if different
- Add KMS key ID for enhanced encryption (optional)

**For Azure**: `backend-configs/backend-dev-azure.hcl`
- Update `subscription_id` with your Azure subscription ID
- Update `tenant_id` with your Azure tenant ID
- Adjust resource names if needed

### Step 3: Initialize Terraform

```bash
cd infra/terraform

# For AWS
./scripts/init-backend.sh aws dev

# For Azure
./scripts/init-backend.sh azure dev
```

Or manually:

```bash
terraform init -backend-config=backend-configs/backend-dev-aws.hcl
```

## Environment Management

### Separate State Files

Each environment (dev/stg/prod) should use separate state files for isolation:

```
dev/terraform.tfstate    # Development environment
stg/terraform.tfstate    # Staging environment
prod/terraform.tfstate   # Production environment
```

### Workspace vs Separate Backends

**Recommended**: Use separate backend keys for each environment rather than Terraform workspaces:

```
✅ Good: backend-configs/backend-dev-aws.hcl → key="dev/terraform.tfstate"
✅ Good: backend-configs/backend-prod-aws.hcl → key="prod/terraform.tfstate"
❌ Avoid: terraform workspace select dev/prod (shared state risk)
```

### Switching Environments

Use the appropriate backend config file when initializing:

```bash
# Development
terraform init -backend-config=backend-configs/backend-dev-aws.hcl

# Staging
terraform init -backend-config=backend-configs/backend-stg-aws.hcl

# Production
terraform init -backend-config=backend-configs/backend-prod-aws.hcl
```

## State Operations

### Common State Commands

Use the state management script for common operations:

```bash
cd infra/terraform
./scripts/state-management.sh [command]
```

**Available commands:**

- `list` - List all resources in state
  ```bash
  ./scripts/state-management.sh list
  ```

- `show` - Show details of a resource
  ```bash
  ./scripts/state-management.sh show aws_s3_bucket.datalake
  ```

- `refresh` - Refresh state to match real infrastructure
  ```bash
  ./scripts/state-management.sh refresh
  ```

- `mv` - Move/rename a resource in state
  ```bash
  ./scripts/state-management.sh mv aws_s3_bucket.old aws_s3_bucket.new
  ```

- `rm` - Remove resource from state (doesn't delete actual resource)
  ```bash
  ./scripts/state-management.sh rm aws_s3_bucket.old
  ```

- `pull` - Download current state as backup
  ```bash
  ./scripts/state-management.sh pull
  ```

- `unlock` - Force unlock state (use with caution)
  ```bash
  ./scripts/state-management.sh unlock LOCK_ID
  ```

### Manual State Operations

```bash
# List resources
terraform state list

# Show resource details
terraform state show aws_s3_bucket.datalake

# Move resource in state
terraform state mv aws_s3_bucket.old aws_s3_bucket.new

# Remove resource from state (resource still exists)
terraform state rm aws_s3_bucket.old

# Refresh state
terraform refresh

# Pull state for backup
terraform state pull > terraform.tfstate.backup

# Force unlock (use with extreme caution)
terraform force-unlock LOCK_ID
```

## Security Best Practices

### 1. Encryption at Rest

**AWS:**
- SSE-S3 encryption is enabled by default
- For production, use SSE-KMS with customer-managed keys:
  ```hcl
  kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"
  ```

**Azure:**
- Encryption is enabled by default on all storage accounts
- Use Azure Key Vault for key management in production

### 2. Access Control

**AWS:**
- Use IAM policies to restrict access to S3 bucket and DynamoDB table
- Implement bucket policies for additional security
- Use least privilege principle

**Azure:**
- Use RBAC (Role-Based Access Control) on storage account
- Prefer Managed Identity for CI/CD pipelines
- Avoid storing access keys in code

### 3. State File Security

- **Never commit state files to git** (should be in `.gitignore`)
- State files may contain sensitive data (passwords, keys, etc.)
- Use remote backends with encryption
- Enable versioning for state recovery

### 4. CI/CD Integration

**For CI/CD pipelines:**

**AWS:**
- Use IAM roles (EC2 instance profile or OIDC for GitHub Actions)
- Avoid using access keys when possible

**Azure:**
- Use Managed Identity or Service Principal
- Store credentials in secure key stores (GitHub Secrets, Azure Key Vault)

Example GitHub Actions workflow:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::ACCOUNT:role/TerraformRole
    aws-region: us-east-1

- name: Terraform Init
  run: |
    cd infra/terraform
    terraform init -backend-config=backend-configs/backend-prod-aws.hcl
```

## Disaster Recovery

### State Backup Strategy

1. **Automatic Versioning:**
   - AWS S3: Versioning enabled on bucket
   - Azure: Soft delete enabled on storage account

2. **Manual Backups:**
   ```bash
   terraform state pull > terraform.tfstate.backup.$(date +%Y%m%d)
   ```

3. **State History:**
   - Review state versions in S3 or Azure portal
   - Restore previous versions if needed

### State Recovery

**If state is corrupted or lost:**

1. Check version history in backend
2. Restore from backup:
   ```bash
   terraform state push terraform.tfstate.backup.20240101
   ```
3. If state is completely lost, you may need to:
   - Import existing resources: `terraform import resource.address resource_id`
   - Or re-create infrastructure (last resort)

### State Consistency

Regularly check for drift:

```bash
terraform plan
terraform refresh
```

If drift is detected:
1. Review changes with `terraform plan`
2. Decide whether to:
   - Import changes: `terraform import`
   - Fix configuration to match reality
   - Apply to fix drift: `terraform apply`

## Troubleshooting

### State Locked

**Error:** `Error: Error acquiring the state lock`

**Solution:**
1. Check if another process is running
2. If process is stuck, find lock ID and unlock:
   ```bash
   terraform force-unlock LOCK_ID
   ```
3. For AWS, check DynamoDB table for active locks
4. For Azure, check blob lease in storage account

### State Not Found

**Error:** `Error: No state file found`

**Solution:**
1. Verify backend configuration
2. Check if state file exists in backend:
   - AWS: Check S3 bucket
   - Azure: Check storage container
3. Verify credentials have read access

### Backend Migration

**Moving from local to remote state:**

```bash
# Initialize with backend (don't apply yet)
terraform init -backend-config=backend-configs/backend-dev-aws.hcl

# Migrate existing state
terraform init -migrate-state
```

**Moving between backends:**

1. Pull current state
2. Configure new backend
3. Initialize with migration

### State Inconsistency

**If state doesn't match reality:**

```bash
# Refresh state
terraform refresh

# Review differences
terraform plan

# Optionally import missing resources
terraform import aws_s3_bucket.example bucket-name
```

## Additional Resources

- [Terraform State Documentation](https://www.terraform.io/docs/state/index.html)
- [Terraform Backend Configuration](https://www.terraform.io/docs/backends/index.html)
- [AWS S3 Backend](https://www.terraform.io/docs/backends/types/s3.html)
- [Azure Backend](https://www.terraform.io/docs/backends/types/azurerm.html)
- [Terraform Cloud](https://www.terraform.io/docs/cloud/index.html) - Alternative managed backend

## Quick Reference

### Bootstrap Backend
```bash
# AWS
./scripts/bootstrap-backend-aws.sh [env] [region]

# Azure
./scripts/bootstrap-backend-azure.sh [env] [location]
```

### Initialize with Backend
```bash
# Using helper script
./scripts/init-backend.sh [provider] [environment]

# Manual
terraform init -backend-config=backend-configs/backend-{env}-{provider}.hcl
```

### State Operations
```bash
./scripts/state-management.sh [command] [args]
```

### Check State
```bash
terraform state list
terraform plan
```



