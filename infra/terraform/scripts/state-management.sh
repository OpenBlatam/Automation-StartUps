#!/bin/bash
# Terraform State Management Utilities
#
# Usage:
#   ./state-management.sh [command] [options]
#
# Commands:
#   list        - List all resources in state
#   show        - Show details of a specific resource
#   mv          - Move/rename a resource in state
#   rm          - Remove a resource from state
#   refresh     - Refresh state to match real infrastructure
#   pull        - Download current state
#   push        - Upload state
#   unlock      - Force unlock state (use with caution)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

COMMAND="${1:-help}"

case "$COMMAND" in
    list)
        echo "Listing all resources in Terraform state..."
        terraform state list
        ;;
    
    show)
        if [ -z "$2" ]; then
            echo "Error: Resource address required"
            echo "Usage: $0 show <resource_address>"
            echo "Example: $0 show aws_s3_bucket.datalake"
            exit 1
        fi
        echo "Showing resource: $2"
        terraform state show "$2"
        ;;
    
    mv)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Error: Source and destination addresses required"
            echo "Usage: $0 mv <source> <destination>"
            echo "Example: $0 mv aws_s3_bucket.old aws_s3_bucket.new"
            exit 1
        fi
        echo "Moving resource from $2 to $3"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted"
            exit 0
        fi
        terraform state mv "$2" "$3"
        ;;
    
    rm)
        if [ -z "$2" ]; then
            echo "Error: Resource address required"
            echo "Usage: $0 rm <resource_address>"
            echo "Example: $0 rm aws_s3_bucket.old"
            exit 1
        fi
        echo "Removing resource from state: $2"
        echo "⚠️  WARNING: This will remove the resource from Terraform state but NOT delete the actual resource."
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted"
            exit 0
        fi
        terraform state rm "$2"
        ;;
    
    refresh)
        echo "Refreshing Terraform state..."
        terraform refresh
        echo "✅ State refreshed"
        ;;
    
    pull)
        echo "Downloading current state..."
        terraform state pull > "terraform.tfstate.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ State downloaded to terraform.tfstate.backup.*"
        ;;
    
    push)
        echo "⚠️  WARNING: Pushing state can overwrite remote state"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted"
            exit 0
        fi
        terraform state push "$2"
        ;;
    
    unlock)
        if [ -z "$2" ]; then
            echo "Error: Lock ID required"
            echo "Usage: $0 unlock <lock_id>"
            echo "Get lock ID from error message when state is locked"
            exit 1
        fi
        echo "⚠️  WARNING: Force unlocking state. Use only if you're sure no other operations are running."
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted"
            exit 0
        fi
        terraform force-unlock "$2"
        ;;
    
    help|*)
        echo "Terraform State Management Utilities"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  list        List all resources in state"
        echo "  show        Show details of a specific resource"
        echo "  mv          Move/rename a resource in state"
        echo "  rm          Remove a resource from state (doesn't delete resource)"
        echo "  refresh     Refresh state to match real infrastructure"
        echo "  pull        Download current state (creates backup)"
        echo "  push        Upload state (use with caution)"
        echo "  unlock      Force unlock state (use with caution)"
        echo ""
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 show aws_s3_bucket.datalake"
        echo "  $0 mv aws_s3_bucket.old aws_s3_bucket.new"
        echo "  $0 rm aws_s3_bucket.old"
        echo "  $0 refresh"
        echo "  $0 unlock LOCK_ID"
        ;;
esac



