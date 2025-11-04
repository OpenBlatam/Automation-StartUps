from __future__ import annotations

from typing import List
import os
import json
from datetime import timedelta

import pendulum
import pandas as pd
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import ShortCircuitOperator


SCHEDULE = os.getenv("OUTREACH_UNSUB_SYNC_SCHEDULE", None)  # e.g. "0 8 * * *" or "@daily"

@dag(
    dag_id="outreach_unsubscribe_sync",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=SCHEDULE,
    catchup=False,
    default_args={
        "owner": "growth",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    doc_md="""
    Sincroniza lista de bajas (unsubscribe) desde CSV y/o API JSON a un CSV local
    que puede ser consumido por `outreach_multichannel` vía `unsubscribe_csv_url`.

    Parámetros:
    - results_dir: directorio donde escribir `unsubscribed.csv`
    - source_csv_url: CSV con columna `email` (fallback: primera columna)
    - source_api_url: endpoint JSON que retorna lista de emails o lista de objetos con `email`
    - api_headers_json: JSON opcional con headers (auth)
    - deduplicate: deduplicar emails (default true)
    """,
    params={
        "results_dir": Param("/tmp/outreach_results", type="string", minLength=1),
        "source_csv_url": Param("", type="string"),
        "source_api_url": Param("", type="string"),
        "api_headers_json": Param("", type="string"),
        "deduplicate": Param(True, type="boolean"),
        # Auto-trigger del DAG principal
        "auto_trigger": Param(False, type="boolean"),
        "outreach_dag_id": Param("outreach_multichannel", type="string", minLength=1),
        "outreach_conf_json": Param("{}", type="string"),
    },
    tags=["outreach", "unsubscribe"],
)
def outreach_unsubscribe_sync() -> None:
    @task(task_id="load_sources")
    def load_sources() -> List[str]:
        from airflow.operators.python import get_current_context

        ctx = get_current_context()
        p = ctx["params"]
        emails: List[str] = []

        # CSV source
        csv_url = str(p.get("source_csv_url", "")).strip()
        if csv_url:
            try:
                df = pd.read_csv(csv_url).fillna("")
                col = "email" if "email" in df.columns else df.columns[0]
                emails.extend(df[col].astype(str).str.strip().str.lower().tolist())
            except Exception:
                pass

        # API source
        api_url = str(p.get("source_api_url", "")).strip()
        if api_url:
            try:
                headers = {"Content-Type": "application/json"}
                extra = str(p.get("api_headers_json", "")).strip()
                if extra:
                    headers.update(json.loads(extra))
                r = requests.get(api_url, headers=headers, timeout=20)
                if r.status_code < 300:
                    data = r.json()
                    if isinstance(data, list):
                        if data and isinstance(data[0], str):
                            emails.extend([str(x).strip().lower() for x in data])
                        elif data and isinstance(data[0], dict):
                            emails.extend([str(x.get("email", "")).strip().lower() for x in data])
                    elif isinstance(data, dict):
                        arr = data.get("emails") or data.get("data") or []
                        if arr and isinstance(arr, list):
                            if arr and isinstance(arr[0], str):
                                emails.extend([str(x).strip().lower() for x in arr])
                            elif arr and isinstance(arr[0], dict):
                                emails.extend([str(x.get("email", "")).strip().lower() for x in arr])
            except Exception:
                pass

        # Cleanup
        emails = [e for e in emails if e]
        if bool(p.get("deduplicate", True)):
            emails = sorted(list(set(emails)))
        return emails

    @task(task_id="write_csv")
    def write_csv(emails: List[str]) -> str:
        from airflow.operators.python import get_current_context

        ctx = get_current_context()
        outdir = str(ctx["params"].get("results_dir", "/tmp/outreach_results"))
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, "unsubscribed.csv")
        try:
            pd.DataFrame({"email": emails}).to_csv(path, index=False)
        except Exception:
            # best effort
            pass
        return path

    emails = load_sources()
    csv_path = write_csv(emails)

    # Auto-trigger opcional del DAG principal con conf que referencia el CSV generado
    def _build_conf(context):  # type: ignore[no-untyped-def]
        p = context["params"]
        try:
            base = json.loads(p.get("outreach_conf_json", "{}"))
        except Exception:
            base = {}
        base["unsubscribe_csv_url"] = csv_path
        return base

    def _should_trigger(**context):  # type: ignore[no-untyped-def]
        return bool(context["params"].get("auto_trigger", False))

    check = ShortCircuitOperator(task_id="check_auto_trigger", python_callable=_should_trigger)
    trigger = TriggerDagRunOperator(
        task_id="trigger_outreach",
        trigger_dag_id="{{ params.outreach_dag_id }}",
        conf=_build_conf,  # callable for runtime conf
        wait_for_completion=False,
    )

    csv_path >> check >> trigger


dag = outreach_unsubscribe_sync()


