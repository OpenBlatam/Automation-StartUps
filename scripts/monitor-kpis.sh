#!/bin/bash
# KPI monitoring script - fetches and displays real-time KPIs
# Usage: ./scripts/monitor-kpis.sh [--json] [--watch] [--interval SECONDS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

API_URL="${API_URL:-http://localhost:3000}"
JSON_OUTPUT=false
WATCH_MODE=false
INTERVAL=5

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--json] [--watch] [--interval SECONDS]"
            exit 1
            ;;
    esac
done

fetch_kpis() {
    local summary=$(curl -s "$API_URL/api/kpi/summary?currency=USD" 2>/dev/null || echo '{}')
    local timeseries=$(curl -s "$API_URL/api/kpi/timeseries?currency=USD&hours=24" 2>/dev/null || echo '[]')
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo "{\"summary\": $summary, \"timeseries\": $timeseries}"
    else
        display_kpis "$summary" "$timeseries"
    fi
}

display_kpis() {
    local summary="$1"
    local timeseries="$2"
    
    # Extract values using jq if available, otherwise use grep/sed
    if command -v jq > /dev/null 2>&1; then
        local revenue_24h=$(echo "$summary" | jq -r '.revenue_24h // 0')
        local revenue_7d=$(echo "$summary" | jq -r '.revenue_7d // 0')
        local payments_24h=$(echo "$summary" | jq -r '.payments_24h // 0')
        local leads_24h=$(echo "$summary" | jq -r '.leads_24h // 0')
        local conversion_rate=$(echo "$summary" | jq -r '.conversion_rate // 0')
    else
        # Fallback parsing
        local revenue_24h=$(echo "$summary" | grep -o '"revenue_24h":[0-9.]*' | cut -d: -f2 || echo "0")
        local revenue_7d=$(echo "$summary" | grep -o '"revenue_7d":[0-9.]*' | cut -d: -f2 || echo "0")
        local payments_24h=$(echo "$summary" | grep -o '"payments_24h":[0-9]*' | cut -d: -f2 || echo "0")
        local leads_24h=$(echo "$summary" | grep -o '"leads_24h":[0-9]*' | cut -d: -f2 || echo "0")
        local conversion_rate=$(echo "$summary" | grep -o '"conversion_rate":[0-9.]*' | cut -d: -f2 || echo "0")
    fi
    
    clear
    echo "═══════════════════════════════════════════════════════════"
    echo "  📊 KPI Dashboard - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "💰 Revenue"
    echo "   • Last 24h:  \$$(printf "%.2f" "$revenue_24h")"
    echo "   • Last 7d:   \$$(printf "%.2f" "$revenue_7d")"
    echo ""
    echo "📈 Activity"
    echo "   • Payments (24h): $payments_24h"
    echo "   • Leads (24h):    $leads_24h"
    echo "   • Conversion:     $(printf "%.2f%%" "$(echo "$conversion_rate * 100" | bc -l 2>/dev/null || echo "0")")"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    
    if [ "$WATCH_MODE" = false ]; then
        exit 0
    fi
}

main() {
    if [ "$WATCH_MODE" = true ]; then
        while true; do
            fetch_kpis
            sleep "$INTERVAL"
        done
    else
        fetch_kpis
    fi
}

main "$@"
