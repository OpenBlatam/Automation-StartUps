#!/bin/bash
# Backup all environments at once
# Useful for scheduled backups across all environments
#
# Usage: ./backup-all-environments.sh [provider]
# Example: ./backup-all-environments.sh aws

set -e

PROVIDER="${1:-aws}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENVIRONMENTS=("dev" "stg" "prod")

echo "💾 Backup All Environments"
echo "Provider: $PROVIDER"
echo ""

cd "$TERRAFORM_DIR"

BACKUP_DIR="$TERRAFORM_DIR/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_LOG="$BACKUP_DIR/backup-all-$TIMESTAMP.log"

SUCCESS=0
FAILED=0

for ENV in "${ENVIRONMENTS[@]}"; do
    echo "Backing up $ENV..."
    
    # Try to backup this environment
    if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
        cd azure
    fi
    
    # Check if environment is initialized
    BACKEND_CONFIG="../backend-configs/backend-${ENV}-${PROVIDER}.hcl"
    if [ ! -f "$BACKEND_CONFIG" ]; then
        echo "  ⚠️  Skipping $ENV (backend config not found)"
        cd "$TERRAFORM_DIR"
        continue
    fi
    
    # Try to initialize and backup
    if terraform init -backend-config="$BACKEND_CONFIG" > /dev/null 2>&1; then
        if terraform state pull > "$BACKUP_DIR/terraform-state-${PROVIDER}-${ENV}-${TIMESTAMP}.backup" 2>/dev/null; then
            echo "  ✅ $ENV backed up"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "  ✗ $ENV backup failed (no state or not accessible)"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "  ⚠️  $ENV not initialized"
    fi
    
    cd "$TERRAFORM_DIR"
done

echo ""
echo "═══════════════════════════════════════"
echo "Backup Summary:"
echo "  ✅ Successful: $SUCCESS"
echo "  ✗ Failed: $FAILED"
echo ""
echo "Backups saved in: $BACKUP_DIR"
echo "Log: $BACKUP_LOG"

