#!/bin/bash
# Migrate Terraform state from local to remote backend or between backends
#
# Usage: ./migrate-backend.sh [from] [to] [provider] [environment]
# Example: ./migrate-backend.sh local remote aws dev
# Example: ./migrate-backend.sh remote remote azure prod (change backend config)

set -e

FROM="${1:-local}"
TO="${2:-remote}"
PROVIDER="${3:-aws}"
ENVIRONMENT="${4:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_CONFIG_DIR="$TERRAFORM_DIR/backend-configs"

echo "🔄 Terraform State Migration"
echo "From: $FROM"
echo "To: $TO"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "$TERRAFORM_DIR/azure" ]; then
    cd "$TERRAFORM_DIR/azure"
    BACKEND_CONFIG_FILE="../backend-configs/backend-${ENVIRONMENT}-${PROVIDER}.hcl"
else
    BACKEND_CONFIG_FILE="$BACKEND_CONFIG_DIR/backend-${ENVIRONMENT}-${PROVIDER}.hcl"
fi

# Backup current state
echo "📦 Creating backup of current state..."
if [ -f "terraform.tfstate" ]; then
    BACKUP_FILE="terraform.tfstate.backup.$(date +%Y%m%d_%H%M%S)"
    cp terraform.tfstate "$BACKUP_FILE"
    echo "✓ Backup created: $BACKUP_FILE"
fi

# Migration scenarios
case "$FROM-$TO" in
    local-remote)
        echo ""
        echo "Migrating from local to remote backend..."
        
        if [ ! -f "$BACKEND_CONFIG_FILE" ]; then
            echo "Error: Backend config file not found: $BACKEND_CONFIG_FILE"
            echo "Please bootstrap backend first: ./bootstrap-backend-${PROVIDER}.sh"
            exit 1
        fi
        
        # Initialize with backend (will prompt to migrate)
        echo ""
        echo "Initializing with remote backend..."
        terraform init -backend-config="$BACKEND_CONFIG_FILE" -migrate-state
        
        echo ""
        echo "✅ Migration completed!"
        echo "State is now stored in remote backend."
        ;;
    
    remote-remote)
        echo ""
        echo "Migrating between remote backends..."
        echo "⚠️  This will change the backend configuration."
        
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted."
            exit 0
        fi
        
        if [ ! -f "$BACKEND_CONFIG_FILE" ]; then
            echo "Error: New backend config file not found: $BACKEND_CONFIG_FILE"
            exit 1
        fi
        
        # Pull current state
        echo "Downloading current state..."
        terraform state pull > current-state.json
        
        # Reinitialize with new backend
        echo "Reinitializing with new backend..."
        terraform init -backend-config="$BACKEND_CONFIG_FILE" -reconfigure
        
        # Push state to new backend
        echo "Uploading state to new backend..."
        terraform state push current-state.json
        
        # Cleanup
        rm -f current-state.json
        
        echo ""
        echo "✅ Migration completed!"
        ;;
    
    remote-local)
        echo ""
        echo "⚠️  WARNING: Migrating from remote to local backend is not recommended!"
        echo "This should only be done for testing or emergency recovery."
        
        read -p "Are you absolutely sure? (type 'yes' to continue): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted."
            exit 0
        fi
        
        # Pull state from remote
        echo "Downloading state from remote backend..."
        terraform state pull > terraform.tfstate
        
        # Reinitialize with local backend (no backend config)
        echo "Reinitializing with local backend..."
        terraform init -backend=false
        
        echo ""
        echo "✅ Migration completed!"
        echo "⚠️  State is now local. Remember to migrate back to remote for production!"
        ;;
    
    *)
        echo "Error: Invalid migration path: $FROM -> $TO"
        echo "Valid options: local-remote, remote-remote, remote-local"
        exit 1
        ;;
esac

echo ""
echo "Next steps:"
echo "  1. Verify state: terraform state list"
echo "  2. Review plan: terraform plan"
echo "  3. If everything looks good, you can continue with: terraform apply"



