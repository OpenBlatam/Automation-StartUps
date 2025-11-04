#!/bin/bash
# Optimize Terraform state file
# Removes unnecessary data and compacts state
#
# Usage: ./optimize-state.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "⚡ Optimizing Terraform State"
echo ""

# Backup current state
echo "📦 Creating backup..."
BACKUP_FILE="backups/terraform-state-optimize-backup-$(date +%Y%m%d_%H%M%S).backup"
mkdir -p backups
terraform state pull > "$BACKUP_FILE" 2>/dev/null || {
    echo "Error: Could not backup state"
    exit 1
}

# Get state size before
STATE_SIZE_BEFORE=$(wc -c < "$BACKUP_FILE" | tr -d ' ')
echo "State size before: $STATE_SIZE_BEFORE bytes"

# Pull state, optimize, push back
echo ""
echo "🔄 Optimizing..."
STATE_JSON=$(terraform state pull)

# Remove unnecessary metadata (keep only essential)
OPTIMIZED_STATE=$(echo "$STATE_JSON" | jq '{
    version: .version,
    terraform_version: .terraform_version,
    serial: .serial,
    lineage: .lineage,
    outputs: .outputs,
    resources: [.resources[]? | {
        mode: .mode,
        type: .type,
        name: .name,
        provider: .provider,
        instances: .instances
    }]
}')

# Save optimized state
OPTIMIZED_FILE=$(mktemp)
echo "$OPTIMIZED_STATE" > "$OPTIMIZED_FILE"

STATE_SIZE_AFTER=$(wc -c < "$OPTIMIZED_FILE" | tr -d ' ')
REDUCTION=$((STATE_SIZE_BEFORE - STATE_SIZE_AFTER))
REDUCTION_PCT=$(echo "scale=1; ($REDUCTION / $STATE_SIZE_BEFORE) * 100" | bc)

echo "State size after: $STATE_SIZE_AFTER bytes"
echo "Reduction: $REDUCTION bytes ($REDUCTION_PCT%)"
echo ""

read -p "Apply optimization? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    terraform state push "$OPTIMIZED_FILE"
    echo ""
    echo "✅ State optimized!"
    echo "Backup saved at: $BACKUP_FILE"
else
    echo "Optimization cancelled."
    rm -f "$OPTIMIZED_FILE"
fi

