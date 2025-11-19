from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.models.param import Param
from data.airflow.plugins.etl_notifications import notify_slack
from airflow.operators.python import get_current_context


SOURCE_DATASET = Dataset("dataset://source_ready")


@dag(
    dag_id="source_producer",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="@hourly",
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 0,
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    params={
        "rows": Param(250_000, type="integer", minimum=1, maximum=10_000_000),
    },
    doc_md="""
    ### Source Producer

    DAG de ejemplo que simula la disponibilidad de una fuente y publica el Dataset
    `dataset://source_ready` para disparar el ETL.
    """,
    tags=["example", "dataset"],
    on_success_callback=lambda context: notify_slack(":white_check_mark: source_producer succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: source_producer failed"),
)
def source_producer() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="produce", outlets=[SOURCE_DATASET], execution_timeout=timedelta(minutes=2))
    def produce() -> Dict[str, Any]:
        ctx = get_current_context()
        rows = int(ctx["params"].get("rows", 250_000))
        payload = {"rows": rows, "source": "example"}
        logger.info("source ready", extra={"rows": rows})
        return payload

    @task(task_id="dq_validate", execution_timeout=timedelta(minutes=2))
    def dq_validate(payload: Dict[str, Any]) -> Dict[str, Any]:
        rows = int(payload.get("rows", 0))
        assert rows > 0 and rows <= 10_000_000, "rows fuera de rango"
        return payload

    validated = dq_validate(produce())
    _ = validated  # marcador para linter/flujo


dag = source_producer()


