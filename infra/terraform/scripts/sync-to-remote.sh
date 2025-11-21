#!/bin/bash
# Sync local Terraform configuration to remote backend
# Ensures remote state is up to date with local changes
#
# Usage: ./sync-to-remote.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "🔄 Syncing to Remote Backend"
echo ""

# Check if using remote backend
BACKEND_TYPE=$(terraform show -json 2>/dev/null | jq -r '.values.backend.type' || echo "local")

if [ "$BACKEND_TYPE" = "local" ] || [ "$BACKEND_TYPE" = "null" ]; then
    echo "⚠️  Not using remote backend"
    echo "Initialize with remote backend first:"
    echo "  make tf-init-backend PROVIDER=aws ENV=dev"
    exit 1
fi

echo "Backend type: $BACKEND_TYPE"
echo ""

# Pull remote state
echo "📥 Pulling remote state..."
terraform state pull > /tmp/remote-state.json 2>/dev/null || {
    echo "Error: Could not pull remote state"
    exit 1
}

# Get local state
echo "📥 Getting local state..."
LOCAL_STATE=$(terraform state pull 2>/dev/null || echo "{}")

# Compare serial numbers
REMOTE_SERIAL=$(jq -r '.serial' /tmp/remote-state.json 2>/dev/null || echo "0")
LOCAL_SERIAL=$(echo "$LOCAL_STATE" | jq -r '.serial' 2>/dev/null || echo "0")

echo "Remote serial: $REMOTE_SERIAL"
echo "Local serial: $LOCAL_SERIAL"
echo ""

if [ "$LOCAL_SERIAL" -gt "$REMOTE_SERIAL" ]; then
    echo "Local state is newer. Pushing to remote..."
    terraform state push "$LOCAL_STATE" || {
        echo "Error: Could not push state"
        exit 1
    }
    echo "✅ State synced to remote"
elif [ "$REMOTE_SERIAL" -gt "$LOCAL_SERIAL" ]; then
    echo "Remote state is newer. Pulling from remote..."
    terraform state pull > /tmp/pulled-state.json
    terraform state push /tmp/pulled-state.json || {
        echo "⚠️  State may be out of sync"
    }
    echo "✅ State synced from remote"
else
    echo "✅ States are in sync"
fi

rm -f /tmp/remote-state.json /tmp/pulled-state.json

echo ""
echo "✅ Sync complete"

