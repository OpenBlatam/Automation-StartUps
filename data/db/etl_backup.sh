#!/bin/bash
# ETL Backup Script
# Creates backups of ETL tables and materialized views

set -e

# Configuration
KPIS_PG_DSN="${KPIS_PG_DSN:-postgresql://user:pass@localhost:5432/dbname}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/etl_backup_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Starting ETL backup at $(date)"
echo "Backup file: ${BACKUP_FILE}"

# Backup tables
pg_dump "${KPIS_PG_DSN}" \
  --table=public.etl_improved_events \
  --table=public.etl_improved_audit \
  --table=public.etl_improved_metrics \
  --table=public.etl_improved_alerts \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  > "${BACKUP_FILE}"

# Append materialized views definition (schema only)
echo "" >> "${BACKUP_FILE}"
echo "-- Materialized views (schema only, refresh separately)" >> "${BACKUP_FILE}"
pg_dump "${KPIS_PG_DSN}" \
  --schema-only \
  --table=public.mv_etl_metrics_daily \
  --table=public.mv_etl_alerts_daily \
  --no-owner \
  --no-acl \
  >> "${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_FILE}"
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "Backup completed: ${BACKUP_FILE}"
echo "Size: $(du -h "${BACKUP_FILE}" | cut -f1)"

# Optional: Keep only last N backups (default: 7)
KEEP_BACKUPS="${KEEP_BACKUPS:-7}"
if [ -n "${KEEP_BACKUPS}" ]; then
  echo "Cleaning old backups (keeping last ${KEEP_BACKUPS})..."
  cd "${BACKUP_DIR}"
  ls -t etl_backup_*.sql.gz | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -f
  echo "Cleanup completed"
fi

