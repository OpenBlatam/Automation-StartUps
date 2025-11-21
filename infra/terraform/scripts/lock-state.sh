#!/bin/bash
# Lock Terraform state (useful for maintenance windows)
# Prevents accidental applies during critical periods
#
# Usage: ./lock-state.sh [reason]
# Example: ./lock-state.sh "Maintenance window - no deployments"

set -e

REASON="${1:-Manual lock}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK_FILE="$TERRAFORM_DIR/.terraform.lock"

cd "$TERRAFORM_DIR"

echo "🔒 Terraform State Lock"
echo "Reason: $REASON"
echo ""

# Check if already locked
if [ -f "$LOCK_FILE" ]; then
    EXISTING_REASON=$(cat "$LOCK_FILE")
    echo "⚠️  State is already locked!"
    echo "Reason: $EXISTING_REASON"
    echo ""
    read -p "Override existing lock? (yes/no): " OVERRIDE
    if [ "$OVERRIDE" != "yes" ]; then
        echo "Lock not overridden. Exiting."
        exit 1
    fi
fi

# Create lock file
cat > "$LOCK_FILE" <<EOF
Terraform State Locked
Reason: $REASON
Locked by: $(whoami)
Locked at: $(date)
EOF

echo "✅ State locked successfully"
echo ""
echo "Lock details:"
cat "$LOCK_FILE"
echo ""
echo "⚠️  Terraform apply operations will be blocked."
echo ""
echo "To unlock, run:"
echo "  ./unlock-state.sh"
echo "  or"
echo "  rm $LOCK_FILE"


