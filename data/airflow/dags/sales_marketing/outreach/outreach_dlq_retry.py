from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List

import json
import os
import random
import time

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context


SCHEDULE = os.getenv("OUTREACH_DLQ_RETRY_SCHEDULE", None)  # e.g. "@hourly" or "0 * * * *"

@dag(
    dag_id="outreach_dlq_retry",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=SCHEDULE,
    catchup=False,
    default_args={
        "owner": "growth",
        "retries": 0,
    },
    doc_md="""
    Reintenta eventos fallidos registrados en results_dir/dlq.jsonl por el DAG outreach_multichannel.

    Parámetros:
    - results_dir: directorio donde vive dlq.jsonl (default /tmp/outreach_results)
    - email_webhook_url, linkedin_webhook_url
    - max_retry_items: máximo de elementos a procesar en una ejecución
    - long_backoff_seconds: espera entre intentos por ítem
    - request_timeout_seconds, retry_attempts
    - dry_run: simular
    """,
    params={
        "results_dir": Param("/tmp/outreach_results", type="string", minLength=1),
        "email_webhook_url": Param("", type="string"),
        "linkedin_webhook_url": Param("", type="string"),
        "max_retry_items": Param(200, type="integer", minimum=1, maximum=5000),
        "long_backoff_seconds": Param(30, type="integer", minimum=0, maximum=600),
        "request_timeout_seconds": Param(20, type="integer", minimum=2, maximum=120),
        "retry_attempts": Param(3, type="integer", minimum=1, maximum=10),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["outreach", "dlq", "retry"],
)
def outreach_dlq_retry() -> None:
    @task(task_id="load_dlq")
    def load_dlq() -> List[Dict[str, Any]]:
        ctx = get_current_context()
        outdir = str(ctx["params"].get("results_dir", "/tmp/outreach_results"))
        path = os.path.join(outdir, "dlq.jsonl")
        items: List[Dict[str, Any]] = []
        if not os.path.exists(path):
            return items
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    # Saltar ya reintentados (marcados)
                    if rec.get("retried"):
                        continue
                    items.append(rec)
                except Exception:
                    continue
        max_items = int(ctx["params"].get("max_retry_items", 200))
        return items[:max_items]

    @task(task_id="retry_item")
    def retry_item(item: Dict[str, Any]) -> Dict[str, Any]:
        ctx = get_current_context()
        params = ctx["params"]
        dry_run = bool(params.get("dry_run", False))
        timeout_s = int(params.get("request_timeout_seconds", 20))
        attempts = int(params.get("retry_attempts", 3))
        backoff = int(params.get("long_backoff_seconds", 30))

        step = str(item.get("step", ""))
        email = (item.get("lead") or {}).get("email", "")
        now_str = datetime.utcnow().strftime("%Y%m%d")
        headers = {"Content-Type": "application/json", "X-Idempotency-Key": f"dlq-retry-{step}-{email}-{now_str}"}

        if step == "email_1" or step == "email_2":
            url = str(params.get("email_webhook_url", "")).strip()
            if not url:
                return {"item": item, "status": "skipped", "reason": "missing_email_webhook"}
            payload = {
                "from": "growth@retry.local",
                "to": email,
                "subject": "(Retry)",
                "text": f"Retrying {step}",
                "run_at": datetime.utcnow().isoformat() + "Z",
                "metadata": {"channel": "email", "sequence_step": step},
            }
        elif step == "linkedin_1":
            url = str(params.get("linkedin_webhook_url", "")).strip()
            if not url:
                return {"item": item, "status": "skipped", "reason": "missing_linkedin_webhook"}
            payload = {
                "action": "linkedin_connect_or_message",
                "run_at": datetime.utcnow().isoformat() + "Z",
                "data": {"email": email},
                "metadata": {"channel": "linkedin", "sequence_step": step},
            }
        else:
            return {"item": item, "status": "skipped", "reason": "unknown_step"}

        last_err = None
        for attempt in range(1, attempts + 1):
            try:
                if dry_run:
                    resp = type("R", (), {"status_code": 200})()
                else:
                    resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
                if resp.status_code < 300:
                    return {"item": item, "status": "ok"}
                last_err = RuntimeError(f"HTTP {resp.status_code}: {getattr(resp,'text','')[:300]}")
            except Exception as e:  # noqa: BLE001
                last_err = e
            if attempt < attempts:
                time.sleep(backoff + random.random())
        # Fallo definitivo
        return {"item": item, "status": "failed", "error": str(last_err)[:300]}

    @task(task_id="mark_processed")
    def mark_processed(results: List[Dict[str, Any]]) -> None:
        ctx = get_current_context()
        outdir = str(ctx["params"].get("results_dir", "/tmp/outreach_results"))
        path = os.path.join(outdir, "dlq.jsonl")
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                lines = [l for l in f if l.strip()]
            # Marcamos los elementos procesados con retried=true, dejando historial
            processed = {(r.get("item") or {}).get("ts", "") + (r.get("item") or {}).get("step", "") for r in results if r.get("status") in ("ok", "skipped")}
            new_lines: List[str] = []
            for line in lines:
                try:
                    rec = json.loads(line)
                except Exception:
                    new_lines.append(line)
                    continue
                key = rec.get("ts", "") + rec.get("step", "")
                if key in processed:
                    rec["retried"] = True
                new_lines.append(json.dumps(rec))
            with open(path, "w") as f:
                f.write("\n".join(new_lines) + "\n")
        except Exception:
            # Best-effort
            pass

    items = load_dlq()
    if items:
        results = retry_item.expand(item=items)
        mark_processed(results)


dag = outreach_dlq_retry()


