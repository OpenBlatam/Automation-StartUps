# ============================================================================
# Networking Outputs
# ============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = module.vpc.natgw_ids
}

# ============================================================================
# Kubernetes Outputs
# ============================================================================

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_arn" {
  description = "Amazon Resource Name (ARN) of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
  sensitive   = false
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster OIDC Issuer"
  value       = module.eks.cluster_oidc_issuer_url
}

output "node_groups" {
  description = "Map of EKS managed node groups"
  value = {
    for name, node_group in module.eks.eks_managed_node_groups : name => {
      node_group_arn  = node_group.node_group_arn
      node_group_id   = node_group.node_group_id
      node_group_name = node_group.node_group_name
      status          = node_group.status
      capacity_type   = node_group.capacity_type
      instance_types  = node_group.instance_types
      disk_size       = node_group.disk_size
    }
  }
}

# ============================================================================
# Storage Outputs
# ============================================================================

output "datalake_bucket_name" {
  description = "Name of the S3 Data Lake bucket"
  value       = aws_s3_bucket.datalake.id
}

output "datalake_bucket_arn" {
  description = "ARN of the S3 Data Lake bucket"
  value       = aws_s3_bucket.datalake.arn
}

output "datalake_bucket_domain_name" {
  description = "Domain name of the S3 Data Lake bucket"
  value       = aws_s3_bucket.datalake.bucket_domain_name
}

# ============================================================================
# Common Outputs
# ============================================================================

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "tags" {
  description = "Common tags applied to resources"
  value       = local.tags
}

# ============================================================================
# Connection Information (for kubectl/helm)
# ============================================================================

output "kubeconfig_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region} --alias ${module.eks.cluster_name}"
}

output "kubeconfig_command_file" {
  description = "Command to save kubeconfig to file"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region} --kubeconfig ~/.kube/config-eks-${var.environment}"
}

# ============================================================================
# Quick Reference Outputs
# ============================================================================

output "quick_reference" {
  description = "Quick reference information"
  value = {
    cluster_name       = module.eks.cluster_name
    cluster_endpoint   = module.eks.cluster_endpoint
    vpc_id            = module.vpc.vpc_id
    datalake_bucket   = aws_s3_bucket.datalake.id
    region            = var.aws_region
    environment       = var.environment
  }
}


