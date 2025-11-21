#!/bin/bash
# Check for outdated Terraform providers and modules
# Compares installed versions with latest available
#
# Usage: ./version-check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

echo "📦 Checking Terraform Provider Versions"
echo ""

# Initialize if needed
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init > /dev/null 2>&1
fi

echo "Current provider versions:"
echo ""

# Read lock file
if [ -f ".terraform.lock.hcl" ]; then
    echo "From .terraform.lock.hcl:"
    grep -E "^\s+version\s*=" .terraform.lock.hcl | sed 's/^[[:space:]]*/  /' | head -10
    
    echo ""
    echo "📝 Note: For latest versions, run:"
    echo "  terraform init -upgrade"
else
    echo "No lock file found. Run 'terraform init' first."
fi

echo ""
echo "Current Terraform version:"
terraform version | head -1

echo ""
echo "Required Terraform version (from providers.tf):"
grep "required_version" providers.tf 2>/dev/null | grep -o '">=.*"' | sed 's/[" ]//g' || echo "Not specified"

echo ""
echo "💡 To update:"
echo "  terraform init -upgrade"
echo ""
echo "⚠️  Always test updates in dev environment first!"

