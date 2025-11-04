#!/bin/bash
# Backup Terraform state script
# Creates timestamped backups of Terraform state for disaster recovery
#
# Usage: ./backup-state.sh [provider] [environment]
# Example: ./backup-state.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$TERRAFORM_DIR/backups"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "💾 Terraform State Backup"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo ""

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "$TERRAFORM_DIR/azure" ]; then
    cd "$TERRAFORM_DIR/azure"
    BACKUP_DIR="../backups"
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/terraform-state-${PROVIDER}-${ENVIRONMENT}-${TIMESTAMP}.backup"
BACKUP_JSON="$BACKUP_DIR/terraform-state-${PROVIDER}-${ENVIRONMENT}-${TIMESTAMP}.json"

# Backup state
echo "📦 Creating state backup..."
if terraform state pull > "$BACKUP_JSON" 2>/dev/null; then
    STATE_SIZE=$(wc -c < "$BACKUP_JSON" | tr -d ' ')
    
    # Also create a compressed backup
    gzip -c "$BACKUP_JSON" > "${BACKUP_FILE}.gz" 2>/dev/null || cp "$BACKUP_JSON" "$BACKUP_FILE"
    
    echo -e "${GREEN}✓ Backup created${NC}"
    echo "  File: $BACKUP_FILE"
    echo "  Size: $STATE_SIZE bytes"
    
    if [ -f "${BACKUP_FILE}.gz" ]; then
        GZ_SIZE=$(wc -c < "${BACKUP_FILE}.gz" | tr -d ' ')
        COMPRESSION=$(echo "scale=1; (1 - $GZ_SIZE / $STATE_SIZE) * 100" | bc)
        echo "  Compressed: ${GZ_SIZE} bytes (${COMPRESSION}% reduction)"
    fi
    
    # Create a symlink to latest
    LATEST="$BACKUP_DIR/terraform-state-${PROVIDER}-${ENVIRONMENT}-latest.json"
    ln -sf "$(basename "$BACKUP_JSON")" "$LATEST" 2>/dev/null || true
    
    # List recent backups
    echo ""
    echo "📋 Recent backups:"
    ls -lh "$BACKUP_DIR"/terraform-state-${PROVIDER}-${ENVIRONMENT}-*.backup* 2>/dev/null | tail -5 || echo "  (none)"
    
    # Clean old backups (keep last 10)
    echo ""
    echo "🧹 Cleaning old backups (keeping last 10)..."
    ls -t "$BACKUP_DIR"/terraform-state-${PROVIDER}-${ENVIRONMENT}-*.backup* 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    
else
    echo "⚠️  Could not create backup (state may not be initialized)"
    exit 1
fi

echo ""
echo "✅ Backup complete!"
