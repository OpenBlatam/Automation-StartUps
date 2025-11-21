# ============================================================================
# VPC Module - Networking Infrastructure
# ============================================================================

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"

  name = coalesce(var.cluster_name, "${local.name_prefix}-vpc")
  cidr = var.vpc_cidr

  azs             = slice(local.azs, 0, max(length(var.private_subnets), length(var.public_subnets)))
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  # NAT Gateway configuration
  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC Flow Logs (for network monitoring)
  enable_flow_log                      = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_iam_role  = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_log_group = var.enable_vpc_flow_logs

  # Tags
  tags = merge(
    local.tags,
    {
      Name = "${local.name_prefix}-vpc"
    }
  )

  # Subnet tags for Kubernetes (EKS requirement)
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/${coalesce(var.cluster_name, local.name_prefix)}" = "owned"
  }

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/${coalesce(var.cluster_name, local.name_prefix)}" = "owned"
  }
}

# ============================================================================
# EKS Cluster Module - Kubernetes Infrastructure
# ============================================================================

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.8"

  cluster_name    = coalesce(var.cluster_name, local.name_prefix)
  cluster_version = local.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = concat(module.vpc.private_subnets, module.vpc.public_subnets)

  # Cluster logging
  cluster_enabled_log_types = local.enable_cluster_logging ? [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ] : []

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    for name, config in var.eks_node_groups : name => {
      min_size     = config.min_size
      max_size     = config.max_size
      desired_size = config.desired_size

      instance_types = config.instance_types
      capacity_type  = config.capacity_type
      disk_size      = config.disk_size

      labels = merge(
        {
          Environment = var.environment
          ManagedBy   = "terraform"
        },
        config.labels
      )

      taints = config.taints

      # Encryption
      block_device_mappings = local.enable_encryption ? {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = config.disk_size
            volume_type           = "gp3"
            iops                  = 3000
            throughput            = 150
            encrypted             = true
            kms_key_id            = var.kms_key_id
            delete_on_termination = true
          }
        }
      } : {}

      tags = merge(
        local.tags,
        {
          Name = "${coalesce(var.cluster_name, local.name_prefix)}-${name}"
        }
      )
    }
  }

  # IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  tags = local.tags
}

# ============================================================================
# S3 Data Lake - Storage Infrastructure
# ============================================================================

resource "aws_s3_bucket" "datalake" {
  bucket = coalesce(var.datalake_bucket, "${local.name_prefix}-datalake")

  tags = merge(
    local.tags,
    {
      Name        = "${local.name_prefix}-datalake"
      Description = "Data Lake storage bucket"
    }
  )
}

# Versioning
resource "aws_s3_bucket_versioning" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "datalake" {
  count  = local.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.datalake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_id != null ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = var.kms_key_id != null
  }
}

# Public access block (security best practice)
resource "aws_s3_bucket_public_access_block" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    filter {}

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    expiration {
      expired_object_delete_marker = true
    }
  }

  # Intelligent-Tiering for cost optimization (optional)
  rule {
    id     = "intelligent-tiering"
    status = var.environment == "prod" ? "Enabled" : "Disabled"

    filter {}

    transition {
      days          = 0
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

# ============================================================================
# Kubernetes Provider Configuration
# ============================================================================

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name
    ]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.eks.cluster_name
      ]
    }
  }
}
