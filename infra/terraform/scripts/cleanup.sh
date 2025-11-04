#!/bin/bash
# Cleanup script for Terraform workspace
# Removes temporary files and caches (safe to run)
#
# Usage: ./cleanup.sh [options]
# Options:
#   --all      Remove all temporary files including .terraform
#   --cache    Remove only cache files
#   --state    Remove local state backups

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

CLEAN_ALL=false
CLEAN_CACHE=false
CLEAN_STATE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --cache)
            CLEAN_CACHE=true
            shift
            ;;
        --state)
            CLEAN_STATE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--all|--cache|--state]"
            exit 1
            ;;
    esac
done

# If no options specified, clean cache by default
if [ "$CLEAN_ALL" = false ] && [ "$CLEAN_CACHE" = false ] && [ "$CLEAN_STATE" = false ]; then
    CLEAN_CACHE=true
fi

cd "$TERRAFORM_DIR"

echo "🧹 Terraform Workspace Cleanup"
echo ""

FILES_REMOVED=0
SPACE_FREED=0

# Clean cache files
if [ "$CLEAN_CACHE" = true ] || [ "$CLEAN_ALL" = true ]; then
    echo "📦 Cleaning cache files..."
    
    # .terraform directory (but keep it if using remote backend)
    if [ -d ".terraform" ] && [ "$CLEAN_ALL" = true ]; then
        SIZE=$(du -sm .terraform 2>/dev/null | cut -f1 || echo "0")
        rm -rf .terraform
        echo "  ✓ Removed .terraform/ ($SIZE MB)"
        FILES_REMOVED=$((FILES_REMOVED + 1))
        SPACE_FREED=$((SPACE_FREED + SIZE))
    fi
    
    # Terraform lock file (safe to remove, will be regenerated)
    if [ -f ".terraform.lock.hcl" ] && [ "$CLEAN_ALL" = true ]; then
        rm -f .terraform.lock.hcl
        echo "  ✓ Removed .terraform.lock.hcl"
        FILES_REMOVED=$((FILES_REMOVED + 1))
    fi
    
    # Crash logs
    if ls crash.log* 2>/dev/null; then
        rm -f crash.log*
        echo "  ✓ Removed crash logs"
        FILES_REMOVED=$((FILES_REMOVED + 1))
    fi
fi

# Clean state backups
if [ "$CLEAN_STATE" = true ] || [ "$CLEAN_ALL" = true ]; then
    echo ""
    echo "💾 Cleaning state backups..."
    
    # Local state backups
    if ls terraform.tfstate.backup* 2>/dev/null; then
        COUNT=$(ls terraform.tfstate.backup* 2>/dev/null | wc -l)
        SIZE=$(du -sm terraform.tfstate.backup* 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
        rm -f terraform.tfstate.backup*
        echo "  ✓ Removed $COUNT state backup file(s) ($SIZE MB)"
        FILES_REMOVED=$((FILES_REMOVED + COUNT))
        SPACE_FREED=$((SPACE_FREED + SIZE))
    fi
    
    # Old state files (but keep current)
    if [ -f "terraform.tfstate.old" ]; then
        rm -f terraform.tfstate.old
        echo "  ✓ Removed terraform.tfstate.old"
        FILES_REMOVED=$((FILES_REMOVED + 1))
    fi
fi

# Clean plan files
echo ""
echo "📋 Cleaning plan files..."
if ls *.tfplan 2>/dev/null; then
    COUNT=$(ls *.tfplan 2>/dev/null | wc -l)
    rm -f *.tfplan *.tfplan.json
    echo "  ✓ Removed $COUNT plan file(s)"
    FILES_REMOVED=$((FILES_REMOVED + COUNT))
fi

# Clean output files
if ls terraform-output*.json 2>/dev/null; then
    COUNT=$(ls terraform-output*.json 2>/dev/null | wc -l)
    rm -f terraform-output*.json
    echo "  ✓ Removed $COUNT output file(s)"
    FILES_REMOVED=$((FILES_REMOVED + COUNT))
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
if [ $FILES_REMOVED -eq 0 ]; then
    echo "✓ No files to clean"
else
    echo "✓ Cleanup complete!"
    echo "  Files removed: $FILES_REMOVED"
    if [ $SPACE_FREED -gt 0 ]; then
        echo "  Space freed: $SPACE_FREED MB"
    fi
fi

echo ""
echo "⚠️  Note: This script does NOT remove:"
echo "  - terraform.tfstate (current state)"
echo "  - *.tf files (configuration files)"
echo "  - .tfvars files (variable files)"
echo ""
echo "To reinitialize after cleanup:"
echo "  terraform init"



