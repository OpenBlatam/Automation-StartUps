#!/bin/bash
# Daily maintenance tasks for Terraform
# Runs routine maintenance checks and cleanup
#
# Usage: ./daily-maintenance.sh [provider] [environment]
# Example: ./daily-maintenance.sh aws dev

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "🔧 Daily Maintenance Tasks"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo "Date: $(date)"
echo ""

# 1. Check state accessibility
echo "1. Checking state accessibility..."
if terraform state list > /dev/null 2>&1; then
    echo "   ✓ State accessible"
else
    echo "   ✗ State not accessible"
    exit 1
fi

# 2. Backup state
echo ""
echo "2. Creating daily backup..."
./backup-state.sh "$PROVIDER" "$ENVIRONMENT" > /dev/null 2>&1 || echo "   ⚠ Backup failed"

# 3. Check for drift
echo ""
echo "3. Checking for drift..."
DRIFT_OUTPUT=$(terraform plan -detailed-exitcode -no-color 2>&1 || true)
if echo "$DRIFT_OUTPUT" | grep -q "No changes"; then
    echo "   ✓ No drift detected"
else
    echo "   ⚠ Drift detected - review with: terraform plan"
fi

# 4. Clean old backups (keep last 30 days)
echo ""
echo "4. Cleaning old backups..."
find backups -name "terraform-state-${PROVIDER}-${ENVIRONMENT}-*.backup*" -mtime +30 -delete 2>/dev/null || true
echo "   ✓ Old backups cleaned"

# 5. Validate configuration
echo ""
echo "5. Validating configuration..."
if terraform validate > /dev/null 2>&1; then
    echo "   ✓ Configuration valid"
else
    echo "   ✗ Validation failed"
fi

# 6. Check for updates
echo ""
echo "6. Checking for provider updates..."
echo "   Run 'terraform init -upgrade' to update providers"

# Summary
echo ""
echo "═══════════════════════════════════════"
echo "✅ Daily maintenance complete"
echo ""
echo "Next: Review any warnings above"

