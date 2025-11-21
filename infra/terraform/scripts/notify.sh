#!/bin/bash
# Notification script for Terraform operations
# Sends notifications via various channels
#
# Usage: ./notify.sh [channel] [message] [title]
# Channels: slack, email, stdout
# Example: ./notify.sh stdout "Terraform apply completed" "Infrastructure Update"

set -e

CHANNEL="${1:-stdout}"
MESSAGE="${2:-Terraform operation completed}"
TITLE="${3:-Terraform Notification}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
NC='\033[0m'

case "$CHANNEL" in
    stdout)
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}📢 $TITLE${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$MESSAGE"
        echo "Time: $(date)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        ;;
    
    slack)
        if [ -z "$SLACK_WEBHOOK_URL" ]; then
            echo "Error: SLACK_WEBHOOK_URL not set"
            exit 1
        fi
        
        PAYLOAD=$(cat <<EOF | jq -c .
{
  "text": "$TITLE",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "$TITLE"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "$MESSAGE\n*Time:* $(date)"
      }
    }
  ]
}
EOF
)
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$PAYLOAD" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || echo "Failed to send Slack notification"
        
        echo "✅ Notification sent to Slack"
        ;;
    
    email)
        if [ -z "$EMAIL_TO" ]; then
            echo "Error: EMAIL_TO not set"
            exit 1
        fi
        
        if command -v mail &> /dev/null; then
            echo "$MESSAGE" | mail -s "$TITLE" "$EMAIL_TO"
            echo "✅ Email sent to $EMAIL_TO"
        else
            echo "Error: mail command not available"
            exit 1
        fi
        ;;
    
    *)
        echo "Error: Unknown channel '$CHANNEL'"
        echo "Supported channels: stdout, slack, email"
        exit 1
        ;;
esac

