from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models import Variable

# Notifications and shared callbacks (mirrors etl_example setup)
from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

# Onboarding integration stubs
from data.airflow.plugins.onboarding_integrations import (
    create_idp_and_workspace_accounts,
    assign_project_and_it_tasks,
    send_welcome_and_docs,
    record_progress_and_notify,
)


ONBOARDING_POOL = os.getenv("ONBOARDING_POOL", "etl_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))


def _validate_employee(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = ["employee_email", "full_name", "start_date", "manager_email"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise AirflowFailException(f"Missing required params: {', '.join(missing)}")
    return payload


@dag(
    dag_id="employee_onboarding",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "it-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Employee Onboarding

    Automatiza creación de cuentas, asignación de tareas, envío de documentación y seguimiento.
    Dispara manualmente con parámetros del empleado o desde Camunda vía API.
    """,
    params={
        "employee_email": "",
        "full_name": "",
        "start_date": "",
        "manager_email": "",
        "department": "",
        "role": "",
        "location": "",
        "send_welcome": True,
        "create_issue_tracker_tasks": True,
        "idempotency_key": "",
    },
    description="Automated onboarding orchestration",
    tags=["onboarding", "it", "hr"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=8,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: employee_onboarding DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: employee_onboarding DAG failed"),
)
def employee_onboarding() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="validate_input", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def validate_input() -> Dict[str, Any]:
        ctx = get_current_context()
        params = dict(ctx.get("params", {}))
        logger.info("validating onboarding params", extra={"params": {k: v for k, v in params.items() if k != "idempotency_key"}})
        return _validate_employee(params)

    @task(task_id="idempotency_lock", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def idempotency_lock(payload: Dict[str, Any]) -> Dict[str, Any]:
        ctx = get_current_context()
        dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "employee_onboarding"
        run_id = ctx.get("run_id")
        idem = str(payload.get("idempotency_key") or f"{payload['employee_email']}:{payload.get('start_date','')}")
        lock_key = f"idemp:{dag_id}:{idem}:{run_id}"
        if Variable.get(lock_key, default_var=None):
            logger.warning("idempotency lock hit; skipping run", extra={"key": lock_key})
            raise AirflowFailException("Duplicate onboarding run detected")
        Variable.set(lock_key, "1")
        return payload

    @task(task_id="create_accounts", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def create_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
        result = create_idp_and_workspace_accounts(payload)
        return {**payload, **result}

    @task(task_id="assign_tasks", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def assign_tasks(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not bool(payload.get("create_issue_tracker_tasks", True)):
            return payload
        result = assign_project_and_it_tasks(payload)
        return {**payload, **result}

    @task(task_id="send_docs", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def send_docs(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not bool(payload.get("send_welcome", True)):
            return payload
        result = send_welcome_and_docs(payload)
        return {**payload, **result}

    @task(task_id="track_progress", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=0)
    def track_progress(payload: Dict[str, Any]) -> None:
        record_progress_and_notify(payload)
        return None

    validated = validate_input()
    locked = idempotency_lock(validated)
    accounts = create_accounts(locked)
    tasks = assign_tasks(accounts)
    docs = send_docs(tasks)
    track_progress(docs)
    return None


dag = employee_onboarding()


