from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List

import pendulum
import pandas as pd
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
import re
import random
import time
import os


@dag(
    dag_id="outreach_multichannel",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args={
        "owner": "growth",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Secuencias de outreach multicanal (Email + LinkedIn)

    Orquesta una primera salida por email y crea la tarea/solicitud para LinkedIn
    (mediante webhook externo) para cada lead en un CSV.

    Parámetros (override al disparar el DAG):
    - `leads_csv_url` (str): URL o ruta local al CSV con columnas: email, first_name, last_name, company, linkedin_url (opcional)
    - `email_webhook_url` (str): Webhook que envía emails (p.ej. Zapier/Make/Lemlist/Sendgrid Function)
    - `linkedin_webhook_url` (str): Webhook que crea/conecta tarea en LinkedIn automation (p.ej. PhantomBuster/Make)
    - `email_from` (str): Remitente del email
    - `email_subject_template` (str): Subject con placeholders, p.ej. "{{first_name}}, idea sobre {{company}}"
    - `email_body_template` (str): Cuerpo con placeholders, soporta: first_name, last_name, company
    - `linkedin_delay_days` (int): días a partir de ahora para programar la acción de LinkedIn (por defecto 2)

    Nota: este DAG usa webhooks genéricos para integrarse con tus herramientas de envío.
    """,
    params={
        "leads_csv_url": Param("", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "linkedin_webhook_url": Param("", type="string", minLength=1),
        "email_from": Param("growth@tu-dominio.com", type="string", minLength=3),
        "email_subject_template": Param("{{first_name}}, una idea rápida para {{company}}", type="string", minLength=3),
        "email_body_template": Param(
            (
                "Hola {{first_name}},\n\n"
                "Vi {{company}} y pensé en una mejora concreta. ¿Te interesa que te comparta 2-3 ideas?\n\n"
                "Saludos,\nEquipo Growth"
            ),
            type="string",
            minLength=3,
        ),
        "linkedin_delay_days": Param(2, type="integer", minimum=0, maximum=30),
        "max_parallel_leads": Param(16, type="integer", minimum=1, maximum=1024),
        # Follow-up email
        "followup_delay_days": Param(5, type="integer", minimum=0, maximum=60),
        "email2_subject_template": Param("Re: {{first_name}} x {{company}}", type="string", minLength=3),
        "email2_body_template": Param(
            (
                "Hola {{first_name}},\n\n"
                "Por si se te pasó el anterior, feliz de compartirte las 2-3 ideas.\n\n"
                "¿Te va esta semana?\n"
                "Saludos,\nEquipo Growth"
            ),
            type="string",
            minLength=3,
        ),
        # Operación
        "suppression_csv_url": Param("", type="string"),
        "business_hours_start_utc": Param(8, type="integer", minimum=0, maximum=23),
        "business_hours_end_utc": Param(18, type="integer", minimum=0, maximum=23),
        "business_tz": Param("UTC", type="string", minLength=1),
        # Flags y control de ejecución
        "enable_linkedin": Param(True, type="boolean"),
        "enable_followup": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
        # A/B testing
        "ab_split_percent": Param(0, type="integer", minimum=0, maximum=100),
        "email_subject_template_b": Param("", type="string"),
        "email_body_template_b": Param("", type="string"),
        "email2_subject_template_b": Param("", type="string"),
        "email2_body_template_b": Param("", type="string"),
        # Engagement
        "engagement_check_url": Param("", type="string"),
        "engagement_timeout_seconds": Param(10, type="integer", minimum=1, maximum=120),
        "skip_linkedin_if_opened": Param(True, type="boolean"),
        "skip_followup_if_replied": Param(True, type="boolean"),
        # Notificaciones
        "slack_webhook_url": Param("", type="string"),
    },
    tags=["outreach", "growth", "multichannel"],
)
def outreach_multichannel() -> None:
    @task(task_id="load_leads")
    def load_leads() -> List[Dict[str, Any]]:
        ctx = get_current_context()
        csv_url = str(ctx["params"]["leads_csv_url"]).strip()
        if csv_url.startswith("http://") or csv_url.startswith("https://"):
            df = pd.read_csv(csv_url)
        else:
            df = pd.read_csv(csv_url)

        expected = {"email", "first_name", "last_name", "company"}
        missing = expected - set(map(str, df.columns))
        if missing:
            raise ValueError(f"Faltan columnas obligatorias en el CSV: {sorted(missing)}")

        # Normalización básica + deduplicación por email (case-insensitive)
        df = df.fillna("")
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        email_re = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
        df = df[df["email"].apply(lambda e: bool(email_re.match(e)))]
        df = df.drop_duplicates(subset=["email"], keep="first")

        # Supresión opcional por email
        suppression_url = str(ctx["params"].get("suppression_csv_url", "")).strip()
        if suppression_url:
            sup_df = pd.read_csv(suppression_url).fillna("")
            if "email" in sup_df.columns:
                sup_emails = set(sup_df["email"].astype(str).str.strip().str.lower())
                df = df[~df["email"].isin(sup_emails)]

        leads: List[Dict[str, Any]] = df.to_dict(orient="records")
        return leads

    @task(task_id="send_initial_email", pool="outreach_pool", priority_weight=5)
    def send_initial_email(lead: Dict[str, Any]) -> Dict[str, Any]:
        ctx = get_current_context()
        params = ctx["params"]
        email_webhook_url = str(params["email_webhook_url"]).strip()
        email_from = str(params["email_from"]).strip()
        subject_tpl = str(params["email_subject_template"]).strip()
        body_tpl = str(params["email_body_template"]).strip()
        start_h = int(params.get("business_hours_start_utc", 8))
        end_h = int(params.get("business_hours_end_utc", 18))
        tz_name = str(params.get("business_tz", "UTC")).strip() or "UTC"
        dry_run = bool(params.get("dry_run", False))
        ab_percent = int(params.get("ab_split_percent", 0))
        subj_b = str(params.get("email_subject_template_b", ""))
        body_b = str(params.get("email_body_template_b", ""))

        def render(template: str, data: Dict[str, Any]) -> str:
            # Render muy simple con {{key}}
            out = template
            for k, v in data.items():
                out = out.replace(f"{{{{{k}}}}}", str(v))
            return out

        # Si fuera de horario laboral (en TZ), programar para el siguiente inicio de ventana
        now_utc = pendulum.now("UTC")
        now_tz = now_utc.in_timezone(tz_name)
        if not (start_h <= now_tz.hour <= end_h):
            if now_tz.hour > end_h:
                next_start_tz = now_tz.replace(hour=start_h, minute=0, second=0, microsecond=0).add(days=1)
            else:
                next_start_tz = now_tz.replace(hour=start_h, minute=0, second=0, microsecond=0)
            run_at = next_start_tz.in_timezone("UTC").naive().replace(tzinfo=None)
        else:
            run_at = now_utc.naive().replace(tzinfo=None)

        # Selección A/B determinística por email
        def pick_ab(email: str) -> bool:
            if ab_percent <= 0 or not email or not subj_b or not body_b:
                return False
            h = abs(hash(email)) % 100
            return h < ab_percent

        use_b = pick_ab(str(lead.get("email", "")))
        subject_tpl_final = subj_b if use_b else subject_tpl
        body_tpl_final = body_b if use_b else body_tpl

        payload = {
            "from": email_from,
            "to": lead.get("email"),
            "subject": render(subject_tpl_final, lead),
            "text": render(body_tpl_final, lead),
            "run_at": run_at.isoformat() + "Z",
            "metadata": {
                "channel": "email",
                "lead": {k: lead.get(k, "") for k in ["first_name", "last_name", "company", "email", "linkedin_url"]},
                "sequence_step": "email_1",
                "ab_variant": "B" if use_b else "A",
            },
        }

        headers = {"Content-Type": "application/json"}
        idem_date = datetime.utcnow().strftime("%Y%m%d")
        headers["X-Idempotency-Key"] = f"outreach-email1-{lead.get('email','unknown')}-{idem_date}"

        # Retries/backoff simples (sin dependencias externas)
        last_err = None
        for attempt in range(1, 4):
            try:
                if dry_run:
                    resp = type("R", (), {"status_code": 200})()
                else:
                    resp = requests.post(email_webhook_url, json=payload, headers=headers, timeout=20)
                if resp.status_code < 300:
                    break
                last_err = RuntimeError(f"Email webhook error {resp.status_code}: {resp.text[:300]}")
            except Exception as e:  # noqa: BLE001
                last_err = e
            if attempt < 3:
                # backoff 2s, 4s con jitter
                time.sleep(2 * attempt + random.random())
        else:
            # No exponer PII completa en logs
            masked = {**lead, "email": "***masked***"}
            slack = str(params.get("slack_webhook_url", "") or os.getenv("SLACK_WEBHOOK_URL", "")).strip()
            if slack:
                try:
                    _ = requests.post(slack, json={"text": f":warning: outreach email_1 failed for {masked}"}, timeout=5)
                except Exception:
                    pass
            raise RuntimeError(f"Fallo enviando email tras retries. Lead={masked}") from last_err
        return {"lead": lead, "email_status": "queued"}

    @task(task_id="check_engagement", pool="outreach_pool", priority_weight=4)
    def check_engagement(prev: Dict[str, Any]) -> Dict[str, Any]:
        ctx = get_current_context()
        params = ctx["params"]
        base_url = str(params.get("engagement_check_url", "")).strip()
        timeout_s = int(params.get("engagement_timeout_seconds", 10))
        dry_run = bool(params.get("dry_run", False))

        lead = prev["lead"]
        result = {"opened": False, "replied": False}
        if not base_url:
            return {"lead": lead, "engagement": result}

        try:
            if dry_run:
                return {"lead": lead, "engagement": result}
            url = f"{base_url}?email={requests.utils.quote(lead.get('email',''))}"
            r = requests.get(url, timeout=timeout_s)
            if r.status_code < 300:
                data = {}
                try:
                    data = r.json() or {}
                except Exception:  # noqa: BLE001
                    data = {}
                result = {"opened": bool(data.get("opened", False)), "replied": bool(data.get("replied", False))}
        except Exception:  # noqa: BLE001
            pass
        return {"lead": lead, "engagement": result}

    @task(task_id="enqueue_linkedin_action", pool="outreach_pool", priority_weight=3)
    def enqueue_linkedin_action(prev: Dict[str, Any]) -> None:
        ctx = get_current_context()
        params = ctx["params"]
        linkedin_webhook_url = str(params["linkedin_webhook_url"]).strip()
        delay_days = int(params.get("linkedin_delay_days", 2))
        dry_run = bool(params.get("dry_run", False))
        if not bool(params.get("enable_linkedin", True)):
            return None

        # Si engagement indica opened y se debe omitir, salir
        engagement = prev.get("engagement", {})
        if bool(params.get("skip_linkedin_if_opened", True)) and bool(engagement.get("opened", False)):
            return None

        lead = prev["lead"]
        schedule_at = datetime.utcnow() + timedelta(days=delay_days)
        payload = {
            "action": "linkedin_connect_or_message",
            "run_at": schedule_at.isoformat() + "Z",
            "data": {
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "company": lead.get("company", ""),
                "email": lead.get("email", ""),
                "linkedin_url": lead.get("linkedin_url", ""),
            },
            "metadata": {
                "channel": "linkedin",
                "sequence_step": "linkedin_1",
            },
        }

        headers = {"Content-Type": "application/json"}
        idem_date = datetime.utcnow().strftime("%Y%m%d")
        headers["X-Idempotency-Key"] = f"outreach-linkedin1-{lead.get('email','unknown')}-{idem_date}"

        last_err = None
        for attempt in range(1, 4):
            try:
                if dry_run:
                    resp = type("R", (), {"status_code": 200})()
                else:
                    resp = requests.post(linkedin_webhook_url, json=payload, headers=headers, timeout=20)
                if resp.status_code < 300:
                    break
                last_err = RuntimeError(f"LinkedIn webhook error {resp.status_code}: {resp.text[:300]}")
            except Exception as e:  # noqa: BLE001
                last_err = e
            if attempt < 3:
                import time
                time.sleep(2 * attempt)
        else:
            masked = {**prev["lead"], "email": "***masked***"}
            raise RuntimeError(f"Fallo encolando LinkedIn tras retries. Lead={masked}") from last_err

    @task(task_id="enqueue_followup_email", pool="outreach_pool", priority_weight=4)
    def enqueue_followup_email(prev: Dict[str, Any]) -> None:
        ctx = get_current_context()
        params = ctx["params"]
        email_webhook_url = str(params["email_webhook_url"]).strip()
        email_from = str(params["email_from"]).strip()
        subject_tpl = str(params["email2_subject_template"]).strip()
        body_tpl = str(params["email2_body_template"]).strip()
        delay_days = int(params.get("followup_delay_days", 5))
        dry_run = bool(params.get("dry_run", False))
        if not bool(params.get("enable_followup", True)):
            return None

        # Si engagement indica replied y se debe omitir, salir
        engagement = prev.get("engagement", {})
        if bool(params.get("skip_followup_if_replied", True)) and bool(engagement.get("replied", False)):
            return None

        lead = prev["lead"]

        def render(template: str, data: Dict[str, Any]) -> str:
            out = template
            for k, v in data.items():
                out = out.replace(f"{{{{{k}}}}}", str(v))
            return out

        run_at = (datetime.utcnow() + timedelta(days=delay_days)).isoformat() + "Z"
        payload = {
            "from": email_from,
            "to": lead.get("email"),
            "subject": render(subject_tpl, lead),
            "text": render(body_tpl, lead),
            "run_at": run_at,
            "metadata": {
                "channel": "email",
                "sequence_step": "email_2",
            },
        }

        headers = {"Content-Type": "application/json"}
        idem_date = datetime.utcnow().strftime("%Y%m%d")
        headers["X-Idempotency-Key"] = f"outreach-email2-{lead.get('email','unknown')}-{idem_date}"
        last_err = None
        for attempt in range(1, 4):
            try:
                if dry_run:
                    resp = type("R", (), {"status_code": 200})()
                else:
                    resp = requests.post(email_webhook_url, json=payload, headers=headers, timeout=20)
                if resp.status_code < 300:
                    break
                last_err = RuntimeError(f"Email2 webhook error {resp.status_code}: {resp.text[:300]}")
            except Exception as e:  # noqa: BLE001
                last_err = e
            if attempt < 3:
                import time
                time.sleep(2 * attempt)
        else:
            masked = {"email": "***masked***"}
            raise RuntimeError("Fallo encolando follow-up tras retries.") from last_err

    leads = load_leads()

    # Control de paralelismo por mapeo dinámico + pool
    # El límite real se controla con el pool "outreach_pool" en Airflow UI y el param max_parallel_leads.
    # Nota: max_parallel_leads se usa como hint para chunking futuro; por ahora, delegamos al pool.
    email_results = send_initial_email.expand(lead=leads)
    engagement = check_engagement.expand(prev=email_results)
    enqueue_linkedin_action.expand(prev=engagement)
    enqueue_followup_email.expand(prev=engagement)


dag = outreach_multichannel()


