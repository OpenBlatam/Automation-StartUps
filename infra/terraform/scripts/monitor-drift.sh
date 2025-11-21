#!/bin/bash
# Continuous drift monitoring script
# Monitors infrastructure for configuration drift and alerts
#
# Usage: ./monitor-drift.sh [provider] [environment] [interval_minutes]
# Example: ./monitor-drift.sh aws dev 60
# Example: ./monitor-drift.sh aws prod 30  # Run every 30 minutes

set -e

PROVIDER="${1:-aws}"
ENVIRONMENT="${2:-dev}"
INTERVAL="${3:-60}"  # Default: 60 minutes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$TERRAFORM_DIR/backups/drift-monitor.log"

mkdir -p "$TERRAFORM_DIR/backups"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ "$PROVIDER" = "azure" ] && [ -d "azure" ]; then
    cd azure
fi

echo "🔍 Drift Monitoring Started"
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo "Interval: $INTERVAL minutes"
echo "Log: $LOG_FILE"
echo ""

# Create log entry
log_entry() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_entry "Drift monitoring started"

while true; do
    log_entry "Checking for drift..."
    
    # Run drift detection
    PLAN_OUTPUT=$(terraform plan -detailed-exitcode -no-color 2>&1 || true)
    PLAN_EXIT_CODE=$?
    
    case $PLAN_EXIT_CODE in
        0)
            log_entry "✓ No drift detected"
            ;;
        2)
            log_entry "⚠ DRIFT DETECTED!"
            
            # Extract summary
            CREATES=$(echo "$PLAN_OUTPUT" | grep -c "will be created" || echo "0")
            UPDATES=$(echo "$PLAN_OUTPUT" | grep -c "will be updated\|must be replaced" || echo "0")
            DELETES=$(echo "$PLAN_OUTPUT" | grep -c "will be destroyed" || echo "0")
            
            log_entry "Changes: +$CREATES ~$UPDATES -$DELETES"
            
            # Create detailed log
            DRIFT_LOG="$TERRAFORM_DIR/backups/drift-detected-$(date +%Y%m%d_%H%M%S).log"
            echo "$PLAN_OUTPUT" > "$DRIFT_LOG"
            log_entry "Detailed log: $DRIFT_LOG"
            
            # Optional: Send alert (configure as needed)
            # echo "Drift detected in $ENVIRONMENT" | mail -s "Terraform Drift Alert" admin@example.com
            
            ;;
        *)
            log_entry "✗ Error checking drift: $PLAN_OUTPUT"
            ;;
    esac
    
    # Wait for next check
    sleep $((INTERVAL * 60))
done


