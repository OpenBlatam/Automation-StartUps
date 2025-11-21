#!/bin/bash
# Terraform workspace management utility
# Helps manage multiple workspaces/environments
#
# Usage: ./terraform-workspace.sh [command] [workspace]
# Commands:
#   list    - List all workspaces
#   select  - Select a workspace
#   show    - Show current workspace
#   create  - Create new workspace
#   delete  - Delete workspace

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

COMMAND="${1:-help}"
WORKSPACE="${2:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

case "$COMMAND" in
    list)
        echo "📋 Terraform Workspaces:"
        echo ""
        if [ -d ".terraform" ]; then
            terraform workspace list 2>/dev/null || echo "No workspaces configured"
        else
            echo "⚠️  Terraform not initialized. Run 'terraform init' first."
        fi
        ;;
    
    show)
        if [ -d ".terraform" ]; then
            CURRENT=$(terraform workspace show 2>/dev/null || echo "default")
            echo "Current workspace: ${GREEN}$CURRENT${NC}"
        else
            echo "⚠️  Terraform not initialized. Run 'terraform init' first."
        fi
        ;;
    
    select)
        if [ -z "$WORKSPACE" ]; then
            echo "Error: Workspace name required"
            echo "Usage: $0 select <workspace-name>"
            exit 1
        fi
        
        if [ ! -d ".terraform" ]; then
            echo "⚠️  Terraform not initialized. Run 'terraform init' first."
            exit 1
        fi
        
        echo "Switching to workspace: $WORKSPACE"
        terraform workspace select "$WORKSPACE" 2>/dev/null || terraform workspace new "$WORKSPACE"
        echo -e "${GREEN}✓ Switched to workspace: $WORKSPACE${NC}"
        ;;
    
    create)
        if [ -z "$WORKSPACE" ]; then
            echo "Error: Workspace name required"
            echo "Usage: $0 create <workspace-name>"
            exit 1
        fi
        
        if [ ! -d ".terraform" ]; then
            echo "⚠️  Terraform not initialized. Run 'terraform init' first."
            exit 1
        fi
        
        echo "Creating workspace: $WORKSPACE"
        terraform workspace new "$WORKSPACE"
        echo -e "${GREEN}✓ Created workspace: $WORKSPACE${NC}"
        ;;
    
    delete)
        if [ -z "$WORKSPACE" ]; then
            echo "Error: Workspace name required"
            echo "Usage: $0 delete <workspace-name>"
            exit 1
        fi
        
        if [ ! -d ".terraform" ]; then
            echo "⚠️  Terraform not initialized."
            exit 1
        fi
        
        CURRENT=$(terraform workspace show)
        if [ "$CURRENT" = "$WORKSPACE" ]; then
            echo -e "${RED}⚠️  Cannot delete current workspace. Switch to another first.${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}⚠️  WARNING: Deleting workspace '$WORKSPACE'${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            terraform workspace delete "$WORKSPACE"
            echo -e "${GREEN}✓ Deleted workspace: $WORKSPACE${NC}"
        else
            echo "Aborted."
        fi
        ;;
    
    help|*)
        echo "Terraform Workspace Management"
        echo ""
        echo "Usage: $0 [command] [workspace]"
        echo ""
        echo "Commands:"
        echo "  list       List all workspaces"
        echo "  show       Show current workspace"
        echo "  select     Select or create a workspace"
        echo "  create     Create new workspace"
        echo "  delete     Delete workspace (cannot be current)"
        echo ""
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 show"
        echo "  $0 select dev"
        echo "  $0 create staging"
        echo "  $0 delete old-workspace"
        echo ""
        echo "Note: Workspaces provide state isolation but use the same configuration."
        echo "For different environments, prefer separate backend keys."
        ;;
esac

