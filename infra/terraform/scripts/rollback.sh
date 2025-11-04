#!/bin/bash
# Rollback Terraform changes using previous state backup
# Use with extreme caution - rollback can be complex
#
# Usage: ./rollback.sh [backup_file]
# Example: ./rollback.sh backups/terraform-state-aws-dev-20240101.backup

set -e

BACKUP_FILE="${1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

if [ -z "$BACKUP_FILE" ]; then
    echo "⚠️  Rollback Script - Use with EXTREME CAUTION"
    echo ""
    echo "Usage: $0 [backup_file]"
    echo ""
    echo "Available backups:"
    ls -lh "$TERRAFORM_DIR/backups"/*.backup* 2>/dev/null | tail -10 || echo "  No backups found"
    exit 1
fi

cd "$TERRAFORM_DIR"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo -e "${RED}⚠️  ROLLBACK OPERATION${NC}"
echo "This will attempt to restore Terraform state from backup."
echo ""
echo "Backup file: $BACKUP_FILE"
echo ""
echo -e "${YELLOW}WARNINGS:${NC}"
echo "  1. Rollback can be complex and may not work for all changes"
echo "  2. Resources created after backup will be orphaned"
echo "  3. Resources deleted after backup will need to be recreated"
echo "  4. Always backup current state first"
echo ""
read -p "Do you want to continue? (type 'ROLLBACK' to confirm): " CONFIRM

if [ "$CONFIRM" != "ROLLBACK" ]; then
    echo "Rollback cancelled."
    exit 0
fi

# Backup current state first
echo ""
echo "📦 Creating backup of current state..."
CURRENT_BACKUP="backups/terraform-state-rollback-backup-$(date +%Y%m%d_%H%M%S).backup"
mkdir -p backups
terraform state pull > "$CURRENT_BACKUP" 2>/dev/null || {
    echo "Warning: Could not backup current state"
}

# Extract backup state
echo "📥 Extracting backup state..."
TEMP_STATE=$(mktemp)

if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$TEMP_STATE"
else
    cp "$BACKUP_FILE" "$TEMP_STATE"
fi

# Show differences
echo ""
echo "🔍 Analyzing differences..."
CURRENT_STATE=$(mktemp)
terraform state pull > "$CURRENT_STATE" 2>/dev/null || echo "{}" > "$CURRENT_STATE"

CURRENT_RESOURCES=$(jq '[.resources[]? | .address] | length' "$CURRENT_STATE" 2>/dev/null || echo "0")
BACKUP_RESOURCES=$(jq '[.resources[]? | .address] | length' "$TEMP_STATE" 2>/dev/null || echo "0")

echo "Current state resources: $CURRENT_RESOURCES"
echo "Backup state resources: $BACKUP_RESOURCES"
echo ""

read -p "Continue with rollback? (yes/no): " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "yes" ]; then
    echo "Rollback cancelled."
    rm -f "$TEMP_STATE" "$CURRENT_STATE"
    exit 0
fi

# Push backup state
echo ""
echo "🔄 Restoring state..."
if terraform state push "$TEMP_STATE"; then
    echo -e "${GREEN}✅ State restored${NC}"
    echo ""
    echo "⚠️  IMPORTANT: Review the following:"
    echo "  1. Run 'terraform plan' to see what will be recreated/deleted"
    echo "  2. Verify all resources are in expected state"
    echo "  3. Apply changes if rollback created drift"
    echo ""
    echo "Current backup saved at: $CURRENT_BACKUP"
else
    echo -e "${RED}✗ Rollback failed${NC}"
    echo "Manual intervention required."
    echo "Current backup available at: $CURRENT_BACKUP"
    rm -f "$TEMP_STATE" "$CURRENT_STATE"
    exit 1
fi

rm -f "$TEMP_STATE" "$CURRENT_STATE"

echo ""
echo "Next steps:"
echo "  terraform plan"
echo "  terraform refresh"
echo "  # Review carefully before applying"
