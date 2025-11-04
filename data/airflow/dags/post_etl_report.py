from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")


@dag(
    dag_id="post_etl_report",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "data-eng",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "email_on_failure": False,
        "email_on_retry": False,
    },
    description="Post-ETL report generator (triggered by upstream DAGs)",
    tags=["example", "report", "etl"],
    dagrun_timeout=timedelta(minutes=15),
    doc_md="""
    ### Post ETL Report
    
    Generates summary reports after ETL completion. Triggered by upstream DAGs via TriggerDagRunOperator.
    
    **Conf Parameters** (from trigger):
    - `source` (str): Source DAG ID that triggered this report
    - `since` (str): ISO 8601 start timestamp
    - `until` (str): ISO 8601 end timestamp  
    - `run_id` (str): Upstream DAG run ID
    - `rows` (int, optional): Number of rows processed
    - `chunk_rows` (int, optional): Chunk size used
    
    **Outputs**: Slack notification with summary.
    """,
)
def post_etl_report() -> None:
    @task(task_id="summarize", execution_timeout=timedelta(minutes=5))
    def summarize() -> Dict[str, Any]:
        """Generate summary report from upstream ETL execution."""
        ctx = get_current_context()
        dag_run = ctx.get("dag_run")
        
        if not dag_run:
            raise AirflowFailException("dag_run context not available")
            
        conf = getattr(dag_run, "conf", {}) or {}
        
        # Extract and validate conf parameters
        source = str(conf.get("source", "unknown"))
        since = conf.get("since", "")
        until = conf.get("until", "")
        upstream_run_id = conf.get("run_id", str(ctx.get("run_id", "")))
        rows = conf.get("rows")
        chunk_rows = conf.get("chunk_rows")
        
        # Validate required fields
        if source == "unknown" and not upstream_run_id:
            logger.warning("Missing source and run_id in conf", extra={"conf": conf})
        
        # Build summary
        summary = {
            "ok": True,
            "source": source,
            "since": since,
            "until": until,
            "run_id": upstream_run_id,
        }
        
        if rows is not None:
            summary["rows"] = int(rows)
        if chunk_rows is not None:
            summary["chunk_rows"] = int(chunk_rows)
        
        # Format message
        msg_parts = [
            f":memo: Post ETL report for {source}",
            f"since={since}" if since else "",
            f"until={until}" if until else "",
            f"run_id={upstream_run_id}" if upstream_run_id else "",
        ]
        if rows is not None:
            msg_parts.append(f"rows={rows:,}")
        msg = " | ".join(filter(None, msg_parts))
        
        logger.info("Generating post-ETL report", extra={
            "component": "summarize",
            "source": source,
            "upstream_run_id": upstream_run_id,
            "rows": rows,
        })
        
        # Send notification
        try:
            notify_slack(msg)
            logger.info("Slack notification sent successfully")
            try:
                if Stats:
                    Stats.incr("post_etl_report.notification_sent", 1)
            except Exception:
                pass
        except Exception as e:
            logger.warning("Slack notification failed (non-critical)", extra={"error": str(e)})
            # Don't fail the DAG if Slack fails
        
        try:
            if Stats:
                Stats.incr("post_etl_report.summarize.success", 1)
        except Exception:
            pass
            
        return summary

    summarize()
    return None


dag = post_etl_report()




