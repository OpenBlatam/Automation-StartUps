# Archivo temporal con constantes y helpers para stripe_product_to_quickbooks_item.py
# Estas deben agregarse al archivo principal

# Constantes de configuración
MIN_PRICE = 0.0
MAX_BATCH_SIZE = int(os.environ.get("QB_MAX_BATCH_SIZE", "1000"))
PROGRESS_REPORT_INTERVAL = int(os.environ.get("QB_PROGRESS_REPORT_INTERVAL", "10"))
RETRY_JITTER_MAX = float(os.environ.get("QB_RETRY_JITTER_MAX", "1.0"))
DEFAULT_BATCH_WORKERS = int(os.environ.get("QB_DEFAULT_BATCH_WORKERS", "5"))
DEFAULT_BATCH_DELAY = float(os.environ.get("QB_DEFAULT_BATCH_DELAY", "0.1"))
QUICKBOOKS_RATE_LIMIT_DELAY = float(os.environ.get("QB_RATE_LIMIT_DELAY", "0.1"))
CB_FAILURE_THRESHOLD = int(os.environ.get("QB_CB_FAILURE_THRESHOLD", "5"))
MEMORY_MONITORING_ENABLED = os.environ.get("QB_MEMORY_MONITORING_ENABLED", "true").lower() == "true"
MEMORY_CLEANUP_THRESHOLD_MB = float(os.environ.get("QB_MEMORY_CLEANUP_THRESHOLD_MB", "500.0"))
USE_ADAPTIVE_DELAY = os.environ.get("QB_USE_ADAPTIVE_DELAY", "true").lower() == "true"

