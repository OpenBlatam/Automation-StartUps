#!/bin/bash
# Cost estimation script for Terraform infrastructure
# Provides rough cost estimates based on resource types
#
# Usage: ./cost-estimate.sh [provider]
# Example: ./cost-estimate.sh aws

set -e

PROVIDER="${1:-aws}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

echo "💰 Terraform Cost Estimation"
echo "Provider: $PROVIDER"
echo ""
echo "⚠️  Note: This is a rough estimate. Actual costs may vary."
echo ""

# Get resource list
RESOURCES=$(terraform state list 2>/dev/null || echo "")

if [ -z "$RESOURCES" ]; then
    echo "No resources found in state. Run 'terraform apply' first."
    exit 0
fi

TOTAL_MONTHLY=0

if [ "$PROVIDER" = "aws" ]; then
    echo "AWS Resource Estimates:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count resources
    EKS_COUNT=$(echo "$RESOURCES" | grep -c "module.eks\|aws_eks" || echo "0")
    EC2_COUNT=$(echo "$RESOURCES" | grep -c "aws_instance\|aws_launch_template" || echo "0")
    S3_COUNT=$(echo "$RESOURCES" | grep -c "aws_s3_bucket" || echo "0")
    NAT_COUNT=$(echo "$RESOURCES" | grep -c "aws_nat_gateway" || echo "0")
    VPC_COUNT=$(echo "$RESOURCES" | grep -c "module.vpc\|aws_vpc" || echo "0")
    
    # Cost estimates (USD/month, approximate)
    if [ "$EKS_COUNT" -gt 0 ]; then
        EKS_COST=$((EKS_COUNT * 72))  # ~$72/month per EKS cluster
        echo "  EKS Cluster(s):        $EKS_COUNT × \$72 = \$$((EKS_COUNT * 72))"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + EKS_COST))
    fi
    
    if [ "$EC2_COUNT" -gt 0 ]; then
        # Estimate based on instance types (rough average)
        EC2_COST=$((EC2_COUNT * 50))  # ~$50/month per instance (varies by type)
        echo "  EC2 Instance(s):        $EC2_COUNT × ~\$50 = ~\$$((EC2_COUNT * 50))"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + EC2_COST))
    fi
    
    if [ "$NAT_COUNT" -gt 0 ]; then
        NAT_COST=$((NAT_COUNT * 32))  # ~$32/month per NAT Gateway
        echo "  NAT Gateway(s):         $NAT_COUNT × \$32 = \$$((NAT_COUNT * 32))"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + NAT_COST))
    fi
    
    if [ "$S3_COUNT" -gt 0 ]; then
        S3_COST=$((S3_COUNT * 1))  # ~$1/month base + storage
        echo "  S3 Bucket(s):           $S3_COUNT × ~\$1+ = ~\$$S3_COST+"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + S3_COST))
    fi

elif [ "$PROVIDER" = "azure" ]; then
    echo "Azure Resource Estimates:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Count resources
    AKS_COUNT=$(echo "$RESOURCES" | grep -c "azurerm_kubernetes_cluster" || echo "0")
    VM_COUNT=$(echo "$RESOURCES" | grep -c "azurerm_virtual_machine\|azurerm_linux_virtual_machine" || echo "0")
    STORAGE_COUNT=$(echo "$RESOURCES" | grep -c "azurerm_storage_account" || echo "0")
    ACR_COUNT=$(echo "$RESOURCES" | grep -c "azurerm_container_registry" || echo "0")
    
    # Cost estimates (USD/month, approximate)
    if [ "$AKS_COUNT" -gt 0 ]; then
        AKS_COST=$((AKS_COUNT * 73))  # ~$73/month per AKS cluster
        echo "  AKS Cluster(s):         $AKS_COUNT × \$73 = \$$((AKS_COUNT * 73))"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + AKS_COST))
    fi
    
    if [ "$VM_COUNT" -gt 0 ]; then
        VM_COST=$((VM_COUNT * 50))  # Varies significantly by VM size
        echo "  Virtual Machine(s):     $VM_COUNT × ~\$50 = ~\$$((VM_COUNT * 50))"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + VM_COST))
    fi
    
    if [ "$STORAGE_COUNT" -gt 0 ]; then
        STORAGE_COST=$((STORAGE_COUNT * 5))  # Base cost + storage
        echo "  Storage Account(s):     $STORAGE_COUNT × ~\$5+ = ~\$$STORAGE_COST+"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + STORAGE_COST))
    fi
    
    if [ "$ACR_COUNT" -gt 0 ]; then
        ACR_COST=$((ACR_COUNT * 5))  # Basic tier
        echo "  Container Registry:    $ACR_COUNT × ~\$5 = ~\$$ACR_COST"
        TOTAL_MONTHLY=$((TOTAL_MONTHLY + ACR_COST))
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Estimated Monthly Cost: ~\$$TOTAL_MONTHLY USD"
echo ""
echo "⚠️  Disclaimer:"
echo "  - Estimates are approximate and may vary significantly"
echo "  - Actual costs depend on usage, region, and instance types"
echo "  - Storage and data transfer costs not fully included"
echo "  - Check your cloud provider's pricing calculator for accurate estimates"
echo ""
echo "📊 For accurate costs, use:"
if [ "$PROVIDER" = "aws" ]; then
    echo "  https://calculator.aws.amazon.com/"
else
    echo "  https://azure.microsoft.com/pricing/calculator/"
fi


