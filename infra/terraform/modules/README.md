# Terraform Modules

This directory contains reusable Terraform modules for common infrastructure patterns.

## 📁 Module Structure

```
modules/
├── networking/
│   ├── vpc/
│   └── security-groups/
├── compute/
│   ├── eks/
│   └── ec2/
├── storage/
│   ├── s3/
│   └── ebs/
└── security/
    ├── iam/
    └── kms/
```

## 🔧 Using Modules

### Example: Using the VPC Module

```hcl
module "vpc" {
  source = "./modules/networking/vpc"

  name       = "my-vpc"
  cidr       = "10.0.0.0/16"
  azs        = ["us-east-1a", "us-east-1b"]
  subnets    = ["10.0.1.0/24", "10.0.2.0/24"]
  enable_nat = true

  tags = {
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

## 📦 Available Modules

### Networking

- **vpc**: Complete VPC with subnets, NAT gateways, and internet gateways
- **security-groups**: Pre-configured security groups for common use cases

### Compute

- **eks**: EKS cluster with managed node groups
- **ec2**: EC2 instances with best practices

### Storage

- **s3**: S3 buckets with encryption, versioning, and lifecycle policies
- **ebs**: EBS volumes with encryption

### Security

- **iam**: IAM roles and policies following least privilege
- **kms**: KMS keys for encryption

## 🚀 Creating New Modules

1. Create module directory structure
2. Define variables in `variables.tf`
3. Define resources in `main.tf`
4. Define outputs in `outputs.tf`
5. Add README with usage examples
6. Version the module (semantic versioning)

## 📝 Module Best Practices

1. **Input Variables**: All configurable values should be variables
2. **Outputs**: Expose useful values for other modules/resources
3. **Versioning**: Use version constraints when consuming modules
4. **Documentation**: Include README with examples
5. **Validation**: Add variable validations where appropriate
6. **Tags**: Support tagging for all resources



