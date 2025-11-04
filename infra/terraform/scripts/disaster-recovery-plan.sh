#!/bin/bash
# Generate disaster recovery plan from Terraform state
# Documents recovery procedures based on current infrastructure
#
# Usage: ./disaster-recovery-plan.sh [output_file]
# Example: ./disaster-recovery-plan.sh DR_PLAN.md

set -e

OUTPUT_FILE="${1:-DISASTER_RECOVERY_PLAN.md}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

echo "📋 Generating Disaster Recovery Plan"
echo "Output: $OUTPUT_FILE"
echo ""

# Get state information
STATE_JSON=$(terraform state pull 2>/dev/null || echo "{}")
RESOURCE_COUNT=$(echo "$STATE_JSON" | jq '[.resources[]?] | length' || echo "0")

# Generate DR plan
cat > "$OUTPUT_FILE" <<EOF
# Disaster Recovery Plan

> Auto-generated from Terraform state
> Generated: $(date)

## 📊 Infrastructure Overview

- **Total Resources:** $RESOURCE_COUNT
- **Last Updated:** $(date)
- **State Location:** $(terraform show -json 2>/dev/null | jq -r '.values.backend.type // "local"' || echo "unknown")

## 🚨 Recovery Procedures

### 1. State Recovery

If Terraform state is lost:

\`\`\`bash
# List available backups
ls -lh backups/terraform-state-*.backup*

# Restore from backup
cd infra/terraform/scripts
./rollback.sh backups/terraform-state-YYYYMMDD.backup

# Verify restoration
terraform state list
terraform plan
\`\`\`

### 2. Complete Infrastructure Recovery

If all infrastructure is lost:

\`\`\`bash
# 1. Ensure backend is accessible
cd infra/terraform/scripts
./bootstrap-backend-aws.sh prod us-east-1  # If needed

# 2. Initialize Terraform
./init-backend.sh aws prod

# 3. Import existing resources (if any)
# terraform import aws_s3_bucket.datalake bucket-name

# 4. Or recreate from scratch
terraform plan
terraform apply
\`\`\`

### 3. Partial Recovery

If specific resources are lost:

\`\`\`bash
# 1. Identify missing resources
terraform plan
# Review what will be created

# 2. Apply to recreate
terraform apply -target=resource.address

# 3. Verify
terraform state list
./scripts/health-check.sh aws prod
\`\`\`

## 📦 Critical Resources

### Backend State Storage

**Location:** 
$(terraform show -json 2>/dev/null | jq -r '.values.backend.config.key // "local state"' || echo "unknown")

**Backup Strategy:**
- Automated backups: \`./backup-state.sh\`
- Retention: Last 10 backups
- Location: \`backups/\` directory

### Key Resources to Monitor

\`\`\`
$(terraform state list 2>/dev/null | head -20 || echo "No resources in state")
\`\`\`

## 🔄 Recovery Time Objectives (RTO)

| Scenario | RTO | Procedure |
|----------|-----|-----------|
| State loss | < 1 hour | Restore from backup |
| Complete loss | < 4 hours | Recreate from Terraform |
| Partial loss | < 2 hours | Targeted apply |

## 📞 Emergency Contacts

- **Infrastructure Team:** [Add contact]
- **Cloud Provider Support:** [Add contact]
- **On-call Engineer:** [Add contact]

## ✅ Recovery Checklist

### Pre-Recovery
- [ ] Identify scope of disaster
- [ ] Verify backend accessibility
- [ ] Locate latest backup
- [ ] Notify stakeholders

### During Recovery
- [ ] Restore/verify state
- [ ] Review plan before applying
- [ ] Apply changes carefully
- [ ] Monitor progress

### Post-Recovery
- [ ] Verify all resources
- [ ] Run health checks
- [ ] Update documentation
- [ ] Conduct post-mortem

## 🔗 Related Documentation

- [State Management Guide](../STATE_MANAGEMENT.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [Backup Procedures](../scripts/README.md#gestión-de-estado)

---

**Important:** This plan is auto-generated. Review and customize for your specific needs.

**Last Updated:** $(date)
EOF

echo "✅ Disaster Recovery Plan generated: $OUTPUT_FILE"
echo ""
echo "⚠️  Important: Review and customize this plan for your specific environment!"

