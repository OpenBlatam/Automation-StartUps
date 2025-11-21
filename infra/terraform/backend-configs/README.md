# Backend Configuration Files

This directory contains Terraform backend configuration files for different environments and cloud providers.

## 📁 Structure

```
backend-configs/
├── backend-dev-aws.hcl      # Development environment on AWS
├── backend-stg-aws.hcl       # Staging environment on AWS
├── backend-prod-aws.hcl      # Production environment on AWS
├── backend-dev-azure.hcl     # Development environment on Azure
├── backend-stg-azure.hcl     # Staging environment on Azure
└── backend-prod-azure.hcl   # Production environment on Azure
```

## 🚀 Quick Start

### 1. Bootstrap Backend Resources (One-time setup)

Before using remote backends, you need to create the backend infrastructure:

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

### 2. Configure Backend

Edit the appropriate backend configuration file for your environment:

**For AWS**: Update `backend-dev-aws.hcl`:
- Update bucket name if different
- Update DynamoDB table name if different
- Add KMS key ID for enhanced encryption (optional, recommended for prod)

**For Azure**: Update `backend-dev-azure.hcl`:
- Update `resource_group_name` if different
- Update `storage_account_name` (must be globally unique)
- Set `subscription_id` and `tenant_id` (if using Service Principal)

### 3. Initialize Terraform

```bash
cd infra/terraform

# Using helper script (recommended)
./scripts/init-backend.sh aws dev

# Or manually
terraform init -backend-config=backend-configs/backend-dev-aws.hcl
```

## 📋 Environment Selection

Use the appropriate backend config file based on your environment:

```bash
# Development
terraform init -backend-config=backend-configs/backend-dev-aws.hcl
./scripts/init-backend.sh aws dev

# Staging
terraform init -backend-config=backend-configs/backend-stg-aws.hcl
./scripts/init-backend.sh aws stg

# Production
terraform init -backend-config=backend-configs/backend-prod-aws.hcl
./scripts/init-backend.sh aws prod
```

## ⚙️ Configuration Details

### AWS Backend (S3 + DynamoDB)

Each AWS backend config includes:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `bucket` | S3 bucket name for state storage | `tf-state-biz-automation-dev` |
| `key` | State file path | `dev/terraform.tfstate` |
| `region` | AWS region | `us-east-1` |
| `dynamodb_table` | DynamoDB table for state locking | `tf-state-locks` |
| `encrypt` | Enable encryption | `true` |
| `kms_key_id` | Optional KMS key ARN | `arn:aws:kms:...` |

**Features:**
- State locking via DynamoDB (prevents concurrent modifications)
- Encryption at rest (SSE-S3 or SSE-KMS)
- Versioning enabled on S3 bucket
- Access logging (configurable)

### Azure Backend (Blob Storage)

Each Azure backend config includes:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `resource_group_name` | Resource group for state storage | `rg-tfstate-dev` |
| `storage_account_name` | Storage account name (globally unique) | `sttfstatedev` |
| `container_name` | Blob container name | `tfstate` |
| `key` | State file path | `dev/terraform.tfstate` |
| `subscription_id` | Azure subscription ID | (optional, via auth) |
| `tenant_id` | Azure tenant ID | (optional, via auth) |

**Features:**
- Built-in encryption (Azure Storage encryption)
- Soft delete enabled for state recovery
- Versioning support
- Access control via RBAC

## 🔐 Security Best Practices

### AWS

1. **Encryption:**
   - Development/Staging: SSE-S3 (default)
   - Production: SSE-KMS with customer-managed key (recommended)

2. **Access Control:**
   - Use IAM policies to restrict access
   - Implement bucket policies for additional security
   - Use least privilege principle

3. **Production Enhancements:**
   - Enable MFA delete on S3 bucket
   - Use separate DynamoDB table for production
   - Enable CloudTrail for audit logging

### Azure

1. **Encryption:**
   - Enabled by default on all storage accounts
   - Use Azure Key Vault for key management in production

2. **Access Control:**
   - Use RBAC (Role-Based Access Control)
   - Prefer Managed Identity for CI/CD pipelines
   - Avoid storing access keys in code

3. **Production Enhancements:**
   - Use dedicated storage account for production
   - Enable soft delete and blob versioning
   - Use Private Endpoints if network isolation required

## 🔄 Switching Environments

When switching between environments, re-initialize with the appropriate backend config:

```bash
# Switch to staging
terraform init -backend-config=backend-configs/backend-stg-aws.hcl

# Switch to production (use with caution!)
terraform init -backend-config=backend-configs/backend-prod-aws.hcl
```

**Important:** Each environment uses separate state files for isolation. Avoid using Terraform workspaces as they can share state.

## 🛠️ Troubleshooting

### Backend Configuration Not Found

If you see an error about missing backend configuration:

1. Verify the file exists: `ls backend-configs/backend-{env}-{provider}.hcl`
2. Check file permissions
3. Verify the path is correct relative to your working directory

### Authentication Errors

**AWS:**
- Verify AWS credentials are configured: `aws sts get-caller-identity`
- Check IAM permissions for S3 bucket and DynamoDB table access

**Azure:**
- Authenticate with Azure CLI: `az login`
- Or set environment variables for Service Principal:
  - `ARM_SUBSCRIPTION_ID`
  - `ARM_TENANT_ID`
  - `ARM_CLIENT_ID`
  - `ARM_CLIENT_SECRET`

### State Locked

If state is locked:
1. Check if another Terraform process is running
2. For AWS: Check DynamoDB table for active locks
3. For Azure: Check blob lease in storage account
4. If stuck, use `terraform force-unlock LOCK_ID` (with caution)

## 📚 Additional Resources

- [Terraform Backend Configuration](https://www.terraform.io/docs/language/settings/backends/index.html)
- [AWS S3 Backend](https://www.terraform.io/docs/language/settings/backends/s3.html)
- [Azure Backend](https://www.terraform.io/docs/language/settings/backends/azurerm.html)
- [State Management Guide](../STATE_MANAGEMENT.md)

## 🔗 Related Files

- `../backend.tf` - Backend type definition
- `../scripts/init-backend.sh` - Helper script for initialization
- `../scripts/bootstrap-backend-aws.sh` - Bootstrap AWS backend
- `../scripts/bootstrap-backend-azure.sh` - Bootstrap Azure backend
- `../STATE_MANAGEMENT.md` - Comprehensive state management guide
