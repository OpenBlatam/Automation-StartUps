#!/bin/bash
# Health check script for platform services
# Usage: ./scripts/health-check.sh [service]
# Services: db, api, airflow, kafka, kestra, all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# Default values
KPIS_PG_HOST="${KPIS_PG_HOST:-localhost}"
KPIS_PG_PORT="${KPIS_PG_PORT:-5432}"
KPIS_PG_DB="${KPIS_PG_DB:-analytics}"
KPIS_PG_USER="${KPIS_PG_USER:-analytics}"
KPIS_PG_PASSWORD="${KPIS_PG_PASSWORD:-}"

API_URL="${API_URL:-http://localhost:3000}"
AIRFLOW_URL="${AIRFLOW_URL:-http://localhost:8080}"
KAFKA_BROKER="${KAFKA_BROKER:-localhost:9092}"
KESTRA_URL="${KESTRA_URL:-http://localhost:8080}"

check_db() {
    echo -n "Checking PostgreSQL... "
    if PGPASSWORD="$KPIS_PG_PASSWORD" psql -h "$KPIS_PG_HOST" -p "$KPIS_PG_PORT" -U "$KPIS_PG_USER" -d "$KPIS_PG_DB" -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        
        # Additional checks
        echo -n "  → Checking tables... "
        if PGPASSWORD="$KPIS_PG_PASSWORD" psql -h "$KPIS_PG_HOST" -p "$KPIS_PG_PORT" -U "$KPIS_PG_USER" -d "$KPIS_PG_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('payments', 'leads')" | grep -q "2"; then
            echo -e "${GREEN}✓ OK${NC}"
        else
            echo -e "${YELLOW}⚠ Missing tables${NC}"
        fi
        
        echo -n "  → Checking materialized views... "
        MV_COUNT=$(PGPASSWORD="$KPIS_PG_PASSWORD" psql -h "$KPIS_PG_HOST" -p "$KPIS_PG_PORT" -U "$KPIS_PG_USER" -d "$KPIS_PG_DB" -t -c "SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'public'" | tr -d ' ')
        if [ "$MV_COUNT" -gt 0 ]; then
            echo -e "${GREEN}✓ OK (${MV_COUNT} views)${NC}"
        else
            echo -e "${YELLOW}⚠ No materialized views found${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

check_api() {
    echo -n "Checking API... "
    if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/healthz" 2>/dev/null); then
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
            
            # Check status endpoint
            echo -n "  → Checking /api/status... "
            if STATUS=$(curl -s "$API_URL/api/status" 2>/dev/null); then
                STATUS_HEALTHY=$(echo "$STATUS" | grep -o '"status":"healthy"' || echo "")
                if [ -n "$STATUS_HEALTHY" ]; then
                    echo -e "${GREEN}✓ OK${NC}"
                else
                    echo -e "${YELLOW}⚠ Degraded${NC}"
                fi
            fi
            return 0
        else
            echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ FAILED (Connection refused)${NC}"
        return 1
    fi
}

check_airflow() {
    echo -n "Checking Airflow... "
    if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$AIRFLOW_URL/health" 2>/dev/null); then
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        else
            echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Not reachable${NC}"
        return 1
    fi
}

check_kafka() {
    echo -n "Checking Kafka... "
    if command -v kafka-topics.sh > /dev/null 2>&1; then
        if kafka-topics.sh --bootstrap-server "$KAFKA_BROKER" --list > /dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        else
            echo -e "${RED}✗ FAILED${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ kafka-topics.sh not found${NC}"
        return 1
    fi
}

check_kestra() {
    echo -n "Checking Kestra... "
    if HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$KESTRA_URL/api/v1/health" 2>/dev/null); then
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
            return 0
        else
            echo -e "${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Not reachable${NC}"
        return 1
    fi
}

main() {
    SERVICE="${1:-all}"
    FAILED=0
    
    case "$SERVICE" in
        db)
            check_db || FAILED=1
            ;;
        api)
            check_api || FAILED=1
            ;;
        airflow)
            check_airflow || FAILED=1
            ;;
        kafka)
            check_kafka || FAILED=1
            ;;
        kestra)
            check_kestra || FAILED=1
            ;;
        all)
            check_db || FAILED=1
            check_api || FAILED=1
            check_airflow || FAILED=1
            check_kafka || FAILED=1
            check_kestra || FAILED=1
            ;;
        *)
            echo "Unknown service: $SERVICE"
            echo "Usage: $0 [db|api|airflow|kafka|kestra|all]"
            exit 1
            ;;
    esac
    
    echo ""
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All checks passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some checks failed!${NC}"
        exit 1
    fi
}

main "$@"

