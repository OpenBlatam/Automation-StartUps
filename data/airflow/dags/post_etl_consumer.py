from __future__ import annotations

from datetime import timedelta
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.operators.python import get_current_context


COMPLETE_DATASET = Dataset("dataset://etl_example/complete")


@dag(
    dag_id="post_etl_consumer",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=[COMPLETE_DATASET],
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 0,
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Post ETL Consumer

    DAG de ejemplo que consume el dataset `dataset://etl_example/complete` y realiza
    una acción placeholder (report/log). Se activa por dataset o puede triggerearse.
    """,
    tags=["example", "dataset"],
)
def post_etl_consumer() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="report", execution_timeout=timedelta(minutes=5))
    def report() -> None:
        ctx = get_current_context()
        dag_run = ctx.get("dag_run")
        conf = getattr(dag_run, "conf", {}) if dag_run else {}
        logger.info(
            "Post ETL report executed",
            extra={
                "source": conf.get("source"),
                "since": conf.get("since"),
                "until": conf.get("until"),
                "upstream_run_id": conf.get("run_id"),
            },
        )

    report()


dag = post_etl_consumer()


