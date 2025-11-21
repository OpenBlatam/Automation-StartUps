#!/bin/bash
# Generate a detailed Terraform plan report
# Creates an HTML report from terraform plan output
#
# Usage: ./generate-plan-report.sh [plan-file]
# Example: ./generate-plan-report.sh tfplan

set -e

PLAN_FILE="${1:-tfplan}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$TERRAFORM_DIR"

# Handle Azure subdirectory
if [ -d "azure" ] && [ -f "azure/main.tf" ]; then
    cd azure
fi

REPORT_FILE="${PLAN_FILE}.html"

echo "📊 Generating Terraform Plan Report"
echo ""

if [ ! -f "$PLAN_FILE" ]; then
    echo "Plan file not found: $PLAN_FILE"
    echo "Creating plan first..."
    terraform plan -out="$PLAN_FILE"
fi

# Extract plan information
echo "Analyzing plan..."
PLAN_JSON=$(terraform show -json "$PLAN_FILE" 2>/dev/null || echo "{}")

# Count changes
CREATES=$(echo "$PLAN_JSON" | jq '[.resource_changes[]? | select(.change.actions[] == "create")] | length' || echo "0")
UPDATES=$(echo "$PLAN_JSON" | jq '[.resource_changes[]? | select(.change.actions[] == "update")] | length' || echo "0")
DELETES=$(echo "$PLAN_JSON" | jq '[.resource_changes[]? | select(.change.actions[] == "destroy")] | length' || echo "0")
REPLACES=$(echo "$PLAN_JSON" | jq '[.resource_changes[]? | select(.change.actions[] == "replace")] | length' || echo "0")

# Generate HTML report
cat > "$REPORT_FILE" <<EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Terraform Plan Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .card { background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }
        .card.create { border-left-color: #2196F3; }
        .card.update { border-left-color: #FF9800; }
        .card.delete { border-left-color: #F44336; }
        .card.replace { border-left-color: #9C27B0; }
        .card h3 { margin: 0 0 10px 0; color: #333; }
        .card .number { font-size: 32px; font-weight: bold; color: #555; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .create { color: #2196F3; }
        .update { color: #FF9800; }
        .delete { color: #F44336; }
        .replace { color: #9C27B0; }
        .timestamp { color: #666; font-size: 12px; margin-top: 20px; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Terraform Plan Report</h1>
        <p class="timestamp">Generated: $(date)</p>
        
        <div class="summary">
            <div class="card create">
                <h3>Resources to Create</h3>
                <div class="number">$CREATES</div>
            </div>
            <div class="card update">
                <h3>Resources to Update</h3>
                <div class="number">$UPDATES</div>
            </div>
            <div class="card delete">
                <h3>Resources to Delete</h3>
                <div class="number">$DELETES</div>
            </div>
            <div class="card replace">
                <h3>Resources to Replace</h3>
                <div class="number">$REPLACES</div>
            </div>
        </div>
        
        <h2>Resource Changes</h2>
        <table>
            <thead>
                <tr>
                    <th>Resource</th>
                    <th>Action</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
EOF

# Add resource changes to table
echo "$PLAN_JSON" | jq -r '.resource_changes[]? | 
    "                <tr><td>\(.address)</td><td class=\"\(.change.actions[0])\">\(.change.actions | join(", "))</td><td>\(.type)</td></tr>"' >> "$REPORT_FILE"

cat >> "$REPORT_FILE" <<EOF
            </tbody>
        </table>
        
        <h2>Plan Details</h2>
        <pre>$(terraform show -no-color "$PLAN_FILE" | head -100)</pre>
        
        <p class="timestamp">Full plan available in: $PLAN_FILE</p>
    </div>
</body>
</html>
EOF

echo "✅ Report generated: $REPORT_FILE"
echo ""
echo "Open in browser:"
echo "  open $REPORT_FILE"
echo ""
echo "Or view at:"
echo "  file://$(pwd)/$REPORT_FILE"


