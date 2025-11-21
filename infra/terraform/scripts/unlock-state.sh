#!/bin/bash
# Unlock Terraform state
# Removes maintenance lock
#
# Usage: ./unlock-state.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK_FILE="$TERRAFORM_DIR/.terraform.lock"

cd "$TERRAFORM_DIR"

if [ ! -f "$LOCK_FILE" ]; then
    echo "✅ State is not locked"
    exit 0
fi

echo "🔓 Unlocking Terraform State"
echo ""
echo "Current lock:"
cat "$LOCK_FILE"
echo ""

read -p "Are you sure you want to unlock? (yes/no): " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    rm -f "$LOCK_FILE"
    echo "✅ State unlocked successfully"
    echo ""
    echo "Terraform operations can now proceed."
else
    echo "Unlock cancelled."
    exit 0
fi


