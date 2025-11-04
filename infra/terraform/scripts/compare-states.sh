#!/bin/bash
# Compare Terraform states script
# Compares current state with a backup or previous state
#
# Usage: ./compare-states.sh [backup_file]
# Example: ./compare-states.sh backups/terraform-state-aws-dev-20240101.backup

set -e

BACKUP_FILE="${1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 [backup_file]"
    echo ""
    echo "Available backups:"
    ls -lh "$TERRAFORM_DIR/backups"/*.backup* 2>/dev/null || echo "  No backups found"
    exit 1
fi

cd "$TERRAFORM_DIR"

echo "🔍 Comparing Terraform States"
echo "Backup: $BACKUP_FILE"
echo ""

# Get current state
echo "📥 Extracting current state..."
CURRENT_STATE=$(mktemp)
terraform state pull > "$CURRENT_STATE" 2>/dev/null || {
    echo "Error: Could not read current state"
    exit 1
}

# Get backup state
echo "📥 Extracting backup state..."
BACKUP_STATE=$(mktemp)

if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$BACKUP_STATE"
else
    cp "$BACKUP_FILE" "$BACKUP_STATE"
fi

# Compare resources
echo ""
echo "📊 State Comparison:"
echo ""

CURRENT_COUNT=$(jq '[.resources[]?] | length' "$CURRENT_STATE" 2>/dev/null || echo "0")
BACKUP_COUNT=$(jq '[.resources[]?] | length' "$BACKUP_STATE" 2>/dev/null || echo "0")

echo "Current state resources: $CURRENT_COUNT"
echo "Backup state resources: $BACKUP_COUNT"
echo ""

# List resources in each
echo "Current state resources:"
jq -r '.resources[]? | .address' "$CURRENT_STATE" 2>/dev/null | sort || echo "  (could not parse)"

echo ""
echo "Backup state resources:"
jq -r '.resources[]? | .address' "$BACKUP_STATE" 2>/dev/null | sort || echo "  (could not parse)"

# Find differences
echo ""
echo "🔍 Differences:"

# Resources only in current
CURRENT_ONLY=$(comm -23 <(jq -r '.resources[]? | .address' "$CURRENT_STATE" 2>/dev/null | sort) <(jq -r '.resources[]? | .address' "$BACKUP_STATE" 2>/dev/null | sort))
if [ -n "$CURRENT_ONLY" ]; then
    echo ""
    echo "➕ Resources only in current state:"
    echo "$CURRENT_ONLY" | sed 's/^/  /'
fi

# Resources only in backup
BACKUP_ONLY=$(comm -13 <(jq -r '.resources[]? | .address' "$CURRENT_STATE" 2>/dev/null | sort) <(jq -r '.resources[]? | .address' "$BACKUP_STATE" 2>/dev/null | sort))
if [ -n "$BACKUP_ONLY" ]; then
    echo ""
    echo "➖ Resources only in backup:"
    echo "$BACKUP_ONLY" | sed 's/^/  /'
fi

# Cleanup
rm -f "$CURRENT_STATE" "$BACKUP_STATE"

if [ -z "$CURRENT_ONLY" ] && [ -z "$BACKUP_ONLY" ]; then
    echo ""
    echo "✅ States are identical"
fi


