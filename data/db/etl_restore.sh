#!/bin/bash
# ETL Restore Script
# Restores ETL tables from backup

set -e

# Configuration
KPIS_PG_DSN="${KPIS_PG_DSN:-postgresql://user:pass@localhost:5432/dbname}"
BACKUP_FILE="${1:-}"

if [ -z "${BACKUP_FILE}" ]; then
  echo "Usage: $0 <backup_file.sql[.gz]>"
  echo "Example: $0 backups/etl_backup_20250115_120000.sql.gz"
  exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Error: Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

echo "Starting ETL restore at $(date)"
echo "Backup file: ${BACKUP_FILE}"
echo "Target database: ${KPIS_PG_DSN}"

# Confirm before proceeding
read -p "This will REPLACE existing data. Continue? (yes/no): " confirm
if [ "${confirm}" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

# Decompress if needed
RESTORE_FILE="${BACKUP_FILE}"
if [[ "${BACKUP_FILE}" == *.gz ]]; then
  echo "Decompressing backup..."
  RESTORE_FILE="${BACKUP_FILE%.gz}"
  gunzip -c "${BACKUP_FILE}" > "${RESTORE_FILE}"
  trap "rm -f ${RESTORE_FILE}" EXIT
fi

# Restore tables
echo "Restoring tables..."
psql "${KPIS_PG_DSN}" < "${RESTORE_FILE}"

# Refresh materialized views if they exist
echo "Refreshing materialized views..."
psql "${KPIS_PG_DSN}" <<EOF
SELECT refresh_etl_mvs();
EOF

echo "Restore completed successfully at $(date)"

