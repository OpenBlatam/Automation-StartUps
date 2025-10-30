from __future__ import annotations

from datetime import timedelta
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from data.airflow.plugins.etl_notifications import notify_slack


@dag(
    dag_id="post_etl_report",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-eng",
    },
    description="Post-ETL report generator (triggered)",
    tags=["example", "report"],
    dagrun_timeout=timedelta(minutes=15),
)
def post_etl_report() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="summarize")
    def summarize() -> dict:
        ctx = get_current_context()
        conf = ctx.get("dag_run").conf or {}
        source = conf.get("source", "unknown")
        since = conf.get("since")
        until = conf.get("until")
        run_id = conf.get("run_id", ctx.get("run_id"))

        msg = f"Post ETL report for {source} | since={since} until={until} run_id={run_id}"
        logger.info(msg)
        try:
            notify_slack(f":memo: {msg}")
        except Exception as e:  # slack optional
            logger.warning("slack notify skipped: %s", e)
        return {"ok": True, "source": source, "since": since, "until": until, "run_id": run_id}

    summarize()
    return None


dag = post_etl_report()


