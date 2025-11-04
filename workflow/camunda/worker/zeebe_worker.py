from __future__ import annotations

import json
import os
import time
import logging
import signal
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Optional imports: the worker is a stub; install zeebe/grpc client in runtime
try:
    from pyzeebe import ZeebeClient, ZeebeWorker
except Exception:  # pragma: no cover
    ZeebeClient = None  # type: ignore
    ZeebeWorker = None  # type: ignore

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("zeebe-worker")

# Health check state
worker_healthy = True
worker_shutdown = False


def env(name: str, default: str = "") -> str:
    """Get environment variable with default value."""
    return os.getenv(name, default)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global worker_shutdown
    logger.info(f"Received signal {signum}, initiating graceful shutdown")
    worker_shutdown = True


def trigger_airflow_dag(dag_id: str, conf: Dict[str, Any], max_retries: int = 3) -> str:
    """Trigger Airflow DAG with retry logic."""
    base = env("AIRFLOW_BASE_URL")
    token = env("AIRFLOW_TOKEN")
    
    if not base:
        raise ValueError("AIRFLOW_BASE_URL environment variable is required")
    
    url = f"{base}/api/v1/dags/{dag_id}/dagRuns"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {"conf": conf}
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Triggering Airflow DAG (attempt {attempt + 1}/{max_retries})",
                extra={"dag_id": dag_id, "attempt": attempt + 1},
            )
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            dag_run_id = data.get("dag_run_id", "")
            logger.info(
                "Airflow DAG triggered successfully",
                extra={"dag_id": dag_id, "dag_run_id": dag_run_id},
            )
            return dag_run_id
        except requests.exceptions.RequestException as e:
            last_exception = e
            logger.warning(
                f"Failed to trigger Airflow DAG (attempt {attempt + 1}/{max_retries})",
                extra={"dag_id": dag_id, "error": str(e), "attempt": attempt + 1},
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error("Failed to trigger Airflow DAG after all retries", extra={"dag_id": dag_id, "error": str(last_exception)})
    raise last_exception


def health_check() -> Dict[str, Any]:
    """Perform health check of worker dependencies."""
    global worker_healthy
    
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }
    
    # Check Zeebe connection
    zeebe_addr = env("ZEEBE_ADDRESS")
    if not zeebe_addr:
        health["checks"]["zeebe"] = {"status": "unhealthy", "error": "ZEEBE_ADDRESS not configured"}
        health["status"] = "unhealthy"
    else:
        health["checks"]["zeebe"] = {"status": "healthy", "address": zeebe_addr}
    
    # Check Airflow connection
    airflow_base = env("AIRFLOW_BASE_URL")
    if not airflow_base:
        health["checks"]["airflow"] = {"status": "warning", "message": "AIRFLOW_BASE_URL not configured"}
    else:
        try:
            # Simple connectivity check
            resp = requests.get(f"{airflow_base}/health", timeout=5)
            if resp.status_code == 200:
                health["checks"]["airflow"] = {"status": "healthy", "url": airflow_base}
            else:
                health["checks"]["airflow"] = {"status": "unhealthy", "status_code": resp.status_code}
                health["status"] = "unhealthy"
        except Exception as e:
            health["checks"]["airflow"] = {"status": "unhealthy", "error": str(e)}
            health["status"] = "unhealthy"
    
    worker_healthy = health["status"] == "healthy"
    return health


def main() -> None:
    """Main worker function."""
    global worker_shutdown
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    zeebe_addr = env("ZEEBE_ADDRESS")
    dag_id = env("ONBOARDING_DAG_ID", "employee_onboarding")
    
    if not zeebe_addr:
        logger.error("ZEEBE_ADDRESS environment variable is required")
        sys.exit(1)
    
    if not ZeebeWorker:
        logger.error("pyzeebe not installed; install it with: pip install pyzeebe")
        sys.exit(1)
    
    # Perform initial health check
    logger.info("Performing initial health check")
    initial_health = health_check()
    logger.info("Health check result", extra={"health": initial_health})
    
    if not initial_health["status"] == "healthy":
        logger.warning("Health check failed, but continuing anyway", extra={"health": initial_health})
    
    worker = ZeebeWorker(zeebe_address=zeebe_addr)

    @worker.task(task_type="create-accounts")
    def handle_create_accounts(job_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create-accounts job type by triggering Airflow DAG."""
        employee_email = job_vars.get("employee_email", "unknown")
        logger.info("job create-accounts received", extra={"employee_email": employee_email, "vars_keys": list(job_vars.keys())})
        
        try:
            # Trigger the whole Airflow DAG once; subsequent steps are handled inside the DAG
            dag_run_id = trigger_airflow_dag(dag_id, conf=job_vars)
            logger.info(
                "Airflow DAG triggered successfully",
                extra={"employee_email": employee_email, "dag_run_id": dag_run_id},
            )
            return {"airflow_dag_run_id": dag_run_id, "status": "triggered"}
        except Exception as e:
            logger.error(
                "Failed to trigger Airflow DAG",
                extra={"employee_email": employee_email, "error": str(e)},
            )
            raise

    @worker.task(task_type="assign-onboarding-tasks")
    def handle_assign_tasks(job_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Acknowledge assign-onboarding-tasks job (handled by Airflow DAG)."""
        employee_email = job_vars.get("employee_email", "unknown")
        logger.info("job assign-onboarding-tasks acknowledged", extra={"employee_email": employee_email})
        return {"ack": True, "status": "acknowledged"}

    @worker.task(task_type="send-onboarding-docs")
    def handle_send_docs(job_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Acknowledge send-onboarding-docs job (handled by Airflow DAG)."""
        employee_email = job_vars.get("employee_email", "unknown")
        logger.info("job send-onboarding-docs acknowledged", extra={"employee_email": employee_email})
        return {"ack": True, "status": "acknowledged"}

    @worker.task(task_type="track-progress")
    def handle_track_progress(job_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Acknowledge track-progress job (handled by Airflow DAG)."""
        employee_email = job_vars.get("employee_email", "unknown")
        logger.info("job track-progress acknowledged", extra={"employee_email": employee_email})
        return {"ack": True, "status": "acknowledged"}

    logger.info(
        "Starting Zeebe worker",
        extra={
            "zeebe_address": zeebe_addr,
            "dag_id": dag_id,
            "airflow_base_url": env("AIRFLOW_BASE_URL"),
        },
    )
    
    try:
        # Start worker in a loop to allow graceful shutdown
        while not worker_shutdown:
            try:
                worker.work()
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down")
                break
            except Exception as e:
                logger.error("Worker error", extra={"error": str(e)})
                if not worker_shutdown:
                    time.sleep(5)  # Brief pause before retrying
    except Exception as e:
        logger.error("Fatal worker error", extra={"error": str(e)})
        raise
    finally:
        logger.info("Zeebe worker shutting down")


if __name__ == "__main__":
    main()



