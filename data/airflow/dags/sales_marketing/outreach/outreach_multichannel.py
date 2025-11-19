"""
Multichannel Outreach Automation DAG

Automates email and LinkedIn outreach sequences with advanced features:
- Multi-channel outreach (email, LinkedIn)
- A/B testing
- Engagement tracking
- VIP segmentation
- Industry personalization
- Multi-language support
- Lead enrichment
- Automatic lead scoring
- Calendar integration (holidays)
- Domain warm-up
- Proactive alerts and monitoring
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import random
import re
import smtplib
import time
from collections import defaultdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import pandas as pd
import pendulum
import requests
from airflow.decorators import dag, task
from airflow.hooks.postgres import PostgresHook
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import workalendar
    _HAS_WORKALENDAR = True
except ImportError:
    _HAS_WORKALENDAR = False
    logger.warning("workalendar not available, calendar features will be limited")

try:
    from openpyxl import Workbook
    _HAS_OPENPYXL = True
except ImportError:
    _HAS_OPENPYXL = False
    logger.warning("openpyxl not available, Excel export will be disabled")

SCHEDULE = os.getenv("OUTREACH_SCHEDULE", None)


@dag(
    dag_id="outreach_multichannel",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=SCHEDULE,
    catchup=False,
    default_args={
        "owner": "growth",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    doc_md=__doc__,
    params={
        # Core parameters
        "leads_csv_url": Param("", type="string", minLength=1),
        "email_webhook_url": Param("", type="string"),
        "linkedin_webhook_url": Param("", type="string"),
        "email_from": Param("growth@example.com", type="string", minLength=3),
        "email_subject_template": Param("", type="string"),
        "email_body_template": Param("", type="string"),
        "linkedin_delay_days": Param(2, type="integer", minimum=0, maximum=30),
        "followup_delay_days": Param(5, type="integer", minimum=1, maximum=30),
        "email2_subject_template": Param("", type="string"),
        "email2_body_template": Param("", type="string"),
        "max_parallel_leads": Param(10, type="integer", minimum=1, maximum=100),
        
        # Validation and filtering
        "suppression_csv_url": Param("", type="string"),
        "unsubscribe_csv_url": Param("", type="string"),
        "unsubscribe_api_url": Param("", type="string"),
        "blocked_domains_csv_url": Param("", type="string"),
        "filter_role_accounts": Param(True, type="boolean"),
        "strict_validation": Param(False, type="boolean"),
        "min_lead_fields": Param(2, type="integer", minimum=1, maximum=10),
        
        # Business hours
        "business_hours_start_utc": Param("09:00", type="string"),
        "business_hours_end_utc": Param("17:00", type="string"),
        "business_tz": Param("UTC", type="string"),
        "exclude_weekends": Param(True, type="boolean"),
        
        # Flags
        "enable_linkedin": Param(True, type="boolean"),
        "enable_followup": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
        
        # Engagement
        "engagement_check_url": Param("", type="string"),
        "engagement_update_api_url": Param("", type="string"),
        "engagement_timeout_seconds": Param(5, type="integer", minimum=1, maximum=30),
        "skip_linkedin_if_opened": Param(True, type="boolean"),
        "skip_followup_if_replied": Param(True, type="boolean"),
        
        # A/B testing
        "ab_split_percent": Param(50, type="integer", minimum=0, maximum=100),
        "email_subject_template_b": Param("", type="string"),
        "email_body_template_b": Param("", type="string"),
        "email2_subject_template_b": Param("", type="string"),
        "email2_body_template_b": Param("", type="string"),
        
        # VIP and personalization
        "vip_emails_csv_url": Param("", type="string"),
        "email_subject_template_vip": Param("", type="string"),
        "email_body_template_vip": Param("", type="string"),
        "email2_subject_template_vip": Param("", type="string"),
        "email2_body_template_vip": Param("", type="string"),
        
        # Industry templates
        "industry_templates_json": Param("{}", type="string"),
        
        # Multi-language
        "auto_detect_language": Param(False, type="boolean"),
        "language_column": Param("", type="string"),
        "multi_language_templates_json": Param("{}", type="string"),
        
        # Rate limiting
        "send_jitter_seconds": Param(2, type="integer", minimum=0, maximum=10),
        "fixed_rate_sleep_seconds": Param(0, type="integer", minimum=0, maximum=5),
        "max_emails_per_minute": Param(20, type="integer", minimum=1, maximum=1000),
        "max_linkedin_per_minute": Param(5, type="integer", minimum=1, maximum=100),
        "max_followup_per_minute": Param(10, type="integer", minimum=1, maximum=500),
        "domain_cooldown_seconds": Param(0, type="integer", minimum=0, maximum=3600),
        "max_domain_emails_per_minute": Param(3, type="integer", minimum=1, maximum=50),
        
        # HTTP settings
        "retry_attempts": Param(3, type="integer", minimum=1, maximum=10),
        "request_timeout_seconds": Param(20, type="integer", minimum=2, maximum=120),
        "email_webhook_headers_json": Param("{}", type="string"),
        "linkedin_webhook_headers_json": Param("{}", type="string"),
        
        # Health checks
        "webhook_healthcheck_enabled": Param(False, type="boolean"),
        "webhook_healthcheck_timeout": Param(5, type="integer", minimum=1, maximum=30),
        
        # Bounce handling
        "auto_suppress_bounces": Param(False, type="boolean"),
        "bounce_api_url": Param("", type="string"),
        
        # Persistence
        "results_dir": Param("/tmp/outreach_results", type="string", minLength=1),
        "metrics_prefix": Param("outreach", type="string", minLength=1),
        "postgres_conn_id": Param("", type="string"),
        "postgres_table": Param("outreach_events", type="string", minLength=1),
        "postgres_summary_table": Param("outreach_summary", type="string", minLength=1),
        
        # Notifications
        "slack_webhook_url": Param("", type="string"),
        "email_notification_to": Param("", type="string"),
        "email_notification_smtp_host": Param("", type="string"),
        "email_notification_smtp_port": Param(587, type="integer", minimum=1, maximum=65535),
        "email_notification_smtp_user": Param("", type="string"),
        "email_notification_smtp_password": Param("", type="string"),
        "email_notification_smtp_use_tls": Param(True, type="boolean"),
        
        # Advanced analytics
        "historical_summary_path": Param("", type="string"),
        "export_prometheus_format": Param(False, type="boolean"),
        "callback_webhook_url": Param("", type="string"),
        "export_executive_report": Param(False, type="boolean"),
        "export_excel": Param(False, type="boolean"),
        "export_dashboard_html": Param(False, type="boolean"),
        "export_formats": Param("csv", type="string"),
        "export_processed_leads": Param(False, type="boolean"),
        
        # CRM integration
        "sync_to_crm": Param(False, type="boolean"),
        "crm_type": Param("hubspot", type="string"),
        "crm_api_key": Param("", type="string"),
        "crm_base_url": Param("", type="string"),
        
        # Template features
        "enable_conditional_templates": Param(False, type="boolean"),
        "enable_template_loops": Param(False, type="boolean"),
        "validate_templates": Param(False, type="boolean"),
        
        # Segmentation
        "segment_by_company_size": Param(False, type="boolean"),
        "segment_by_location": Param(False, type="boolean"),
        
        # Security limits
        "max_leads_limit": Param(0, type="integer", minimum=0, maximum=100000),
        "stop_on_error_rate": Param(0.0, type="number", minimum=0.0, maximum=1.0),
        
        # Cleanup
        "cleanup_old_files_days": Param(0, type="integer", minimum=0, maximum=365),
        
        # NEW: Lead enrichment
        "enable_lead_enrichment": Param(False, type="boolean"),
        "enrichment_api_url": Param("", type="string"),
        "enrichment_api_key": Param("", type="string"),
        "enrichment_timeout_seconds": Param(10, type="integer", minimum=1, maximum=60),
        "enrichment_fields": Param("company_size,job_title,industry,location,social_profiles", type="string"),
        
        # NEW: Automatic lead scoring
        "enable_lead_scoring": Param(False, type="boolean"),
        "scoring_weights_json": Param('{"email_quality": 10, "company_size": 20, "job_title": 15, "industry_fit": 25, "engagement": 30}', type="string"),
        "min_score_to_contact": Param(0, type="integer", minimum=0, maximum=100),
        
        # NEW: Calendar integration
        "enable_calendar_check": Param(False, type="boolean"),
        "calendar_country": Param("US", type="string"),
        "calendar_region": Param("", type="string"),
        "skip_holidays": Param(True, type="boolean"),
        "calendar_api_url": Param("", type="string"),
        
        # NEW: Domain warm-up
        "enable_domain_warmup": Param(False, type="boolean"),
        "warmup_api_url": Param("", type="string"),
        "warmup_daily_limit": Param(50, type="integer", minimum=1, maximum=500),
        "warmup_progress_threshold": Param(50, type="integer", minimum=1, maximum=100),
        
        # NEW: Proactive alerts
        "enable_proactive_alerts": Param(False, type="boolean"),
        "alert_webhook_url": Param("", type="string"),
        "alert_error_threshold": Param(0.1, type="number", minimum=0.0, maximum=1.0),
        "alert_slow_performance_threshold_ms": Param(5000, type="integer", minimum=1000, maximum=60000),
    },
    tags=["outreach", "multichannel", "email", "linkedin"],
)
def outreach_multichannel() -> None:
    """Main DAG for multichannel outreach automation."""
    
    # Helper functions
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    def extract_domain(email: str) -> str:
        """Extract domain from email."""
        return email.split("@")[-1].lower() if "@" in email else ""
    
    def is_role_account(email: str) -> bool:
        """Check if email is a role account."""
        role_prefixes = ["info", "support", "help", "sales", "marketing", "contact", "hello", "admin", "noreply", "no-reply"]
        local = email.split("@")[0].lower() if "@" in email else ""
        return any(local == prefix or local.startswith(prefix + ".") for prefix in role_prefixes)
    
    def render_template_simple(template: str, data: Dict[str, Any]) -> str:
        """Simple template rendering with {{key}} placeholders."""
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value or ""))
            if isinstance(value, dict):
                for subk, subv in value.items():
                    nested = f"{{{{{key}.{subk}}}}}"
                    result = result.replace(nested, str(subv or ""))
        return result
    
    def render_template_advanced(template: str, data: Dict[str, Any], enable_conditionals: bool = False, enable_loops: bool = False) -> str:
        """Advanced template rendering with conditionals and loops."""
        if not enable_conditionals and not enable_loops:
            return render_template_simple(template, data)
        
        # Simple implementation of {% if %} and {% for %}
        result = template
        
        # Handle conditionals {% if var %}...{% endif %}
        if enable_conditionals:
            import re as re_module
            pattern = r"{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}"
            for match in re_module.finditer(pattern, result, re_module.DOTALL):
                var_name = match.group(1)
                content = match.group(2)
                if data.get(var_name):
                    result = result.replace(match.group(0), content)
                else:
                    result = result.replace(match.group(0), "")
        
        # Handle loops {% for item in list_key %}...{% endfor %}
        if enable_loops:
            import re as re_module
            pattern = r"{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}"
            for match in re_module.finditer(pattern, result, re_module.DOTALL):
                item_var = match.group(1)
                list_key = match.group(2)
                content = match.group(3)
                items = data.get(list_key, [])
                if isinstance(items, list):
                    loop_result = ""
                    for item in items:
                        item_data = dict(data)
                        item_data[item_var] = item
                        loop_result += render_template_simple(content, item_data)
                    result = result.replace(match.group(0), loop_result)
        
        # Final simple replacement
        return render_template_simple(result, data)
    
    def load_csv_from_url(url_or_path: str, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load CSV from URL or local path."""
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                df = pd.read_csv(url_or_path)
            else:
                df = pd.read_csv(url_or_path)
            if required_columns:
                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    logger.warning(f"Missing columns in CSV: {missing}")
            return df.fillna("")
        except Exception as e:
            logger.error(f"Error loading CSV from {url_or_path}: {e}")
            return pd.DataFrame()
    
    def load_emails_from_url(url_or_path: str) -> Set[str]:
        """Load email list from CSV or API."""
        emails = set()
        if not url_or_path:
            return emails
        
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                if "api" in url_or_path.lower() or url_or_path.endswith(".json"):
                    # API endpoint
                    ctx = get_current_context()
                    headers = {"Content-Type": "application/json"}
                    r = requests.get(url_or_path, headers=headers, timeout=20)
                    if r.status_code < 300:
                        data = r.json()
                        if isinstance(data, list):
                            if data and isinstance(data[0], str):
                                emails.update(str(x).strip().lower() for x in data)
                            else:
                                emails.update(str(x.get("email", "")).strip().lower() for x in data if isinstance(x, dict))
                        elif isinstance(data, dict):
                            arr = data.get("emails") or data.get("data") or []
                            if arr:
                                if isinstance(arr[0], str):
                                    emails.update(str(x).strip().lower() for x in arr)
                                else:
                                    emails.update(str(x.get("email", "")).strip().lower() for x in arr)
                else:
                    # CSV URL
                    df = pd.read_csv(url_or_path)
                    col = "email" if "email" in df.columns else df.columns[0]
                    emails.update(df[col].astype(str).str.strip().str.lower().dropna().tolist())
            else:
                # Local path
                df = pd.read_csv(url_or_path)
                col = "email" if "email" in df.columns else df.columns[0]
                emails.update(df[col].astype(str).str.strip().str.lower().dropna().tolist())
        except Exception as e:
            logger.error(f"Error loading emails from {url_or_path}: {e}")
        return emails
    
    def is_holiday(date: pendulum.DateTime, country: str = "US", region: str = "") -> bool:
        """Check if date is a holiday using workalendar or API."""
        if not _HAS_WORKALENDAR:
            # Fallback to API if available
            ctx = get_current_context()
            api_url = str(ctx["params"].get("calendar_api_url", "")).strip()
            if api_url:
                try:
                    r = requests.get(f"{api_url}?date={date.format('YYYY-MM-DD')}&country={country}", timeout=5)
                    if r.status_code < 300:
                        data = r.json()
                        return data.get("is_holiday", False)
                except Exception:
                    pass
            return False
        
        try:
            cal = workalendar.get_calendar_class(country)()
            return cal.is_holiday(date.date())
        except Exception:
            return False
    
    def calculate_next_business_time(
        now: pendulum.DateTime,
        start_hour: str,
        end_hour: str,
        tz: str,
        exclude_weekends: bool,
        skip_holidays: bool,
        country: str = "US"
    ) -> pendulum.DateTime:
        """Calculate next valid business time."""
        tz_obj = pendulum.timezone(tz)
        now_tz = now.in_tz(tz_obj)
        
        start = int(start_hour.split(":")[0])
        end = int(end_hour.split(":")[0])
        
        # Check if current time is within business hours
        if start <= now_tz.hour < end:
            if exclude_weekends and now_tz.weekday() >= 5:
                # Weekend, move to next Monday
                days_ahead = 7 - now_tz.weekday()
                next_time = now_tz.add(days=days_ahead).start_of("day").add(hours=start)
            elif skip_holidays and is_holiday(now_tz, country):
                # Holiday, move to next day
                next_time = now_tz.add(days=1).start_of("day").add(hours=start)
            else:
                return now.in_tz("UTC")
        
        # Calculate next business day
        next_time = now_tz.add(days=1).start_of("day").add(hours=start)
        
        while True:
            if exclude_weekends and next_time.weekday() >= 5:
                next_time = next_time.add(days=1)
                continue
            if skip_holidays and is_holiday(next_time, country):
                next_time = next_time.add(days=1)
                continue
            break
        
        return next_time.in_tz("UTC")
    
    def enrich_lead(lead: Dict[str, Any], api_url: str, api_key: str, timeout: int, fields: str) -> Dict[str, Any]:
        """Enrich lead data from external API."""
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            payload = {"email": lead.get("email", "")}
            r = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
            
            if r.status_code < 300:
                data = r.json()
                requested_fields = fields.split(",") if fields else []
                for field in requested_fields:
                    field = field.strip()
                    if field in data:
                        lead[field] = data[field]
                lead["_enriched"] = True
            else:
                lead["_enriched"] = False
        except Exception as e:
            logger.warning(f"Enrichment failed for {lead.get('email', 'unknown')}: {e}")
            lead["_enriched"] = False
        return lead
    
    def score_lead(lead: Dict[str, Any], weights: Dict[str, int]) -> int:
        """Calculate lead score based on various factors."""
        score = 0
        
        # Email quality
        email = lead.get("email", "")
        if is_valid_email(email):
            score += weights.get("email_quality", 10)
        domain = extract_domain(email)
        if domain and "." in domain:
            score += 5
        
        # Company size (if enriched)
        company_size = lead.get("company_size", "")
        if company_size:
            size_lower = str(company_size).lower()
            if "enterprise" in size_lower or "large" in size_lower:
                score += weights.get("company_size", 20)
            elif "medium" in size_lower:
                score += weights.get("company_size", 20) // 2
            else:
                score += weights.get("company_size", 20) // 4
        
        # Job title relevance
        job_title = lead.get("job_title", "")
        if job_title:
            title_lower = str(job_title).lower()
            decision_makers = ["ceo", "cto", "cfo", "founder", "director", "vp", "head", "manager"]
            if any(dm in title_lower for dm in decision_makers):
                score += weights.get("job_title", 15)
            else:
                score += weights.get("job_title", 15) // 3
        
        # Industry fit (if enriched)
        industry = lead.get("industry", "")
        if industry:
            score += weights.get("industry_fit", 25)
        
        # Engagement (if available)
        if lead.get("opened", False):
            score += weights.get("engagement", 30) // 2
        if lead.get("replied", False):
            score += weights.get("engagement", 30)
        
        return min(score, 100)
    
    def check_domain_warmup(domain: str, api_url: str) -> Dict[str, Any]:
        """Check domain warm-up status."""
        try:
            r = requests.get(f"{api_url}?domain={domain}", timeout=10)
            if r.status_code < 300:
                return r.json()
        except Exception:
            pass
        return {"warmed": False, "progress": 0, "daily_limit": 50}
    
    def send_proactive_alert(message: str, webhook_url: str, level: str = "warning"):
        """Send proactive alert to webhook."""
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": level,
                "message": message,
                "dag_id": "outreach_multichannel",
            }
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception:
            pass
    
    # Rate limiting state (in-memory, per-worker)
    _rate_limit_state = {
        "email_per_minute": defaultdict(lambda: {"count": 0, "window_start": time.time()}),
        "domain_per_minute": defaultdict(lambda: {"count": 0, "window_start": time.time()}),
        "linkedin_per_minute": {"count": 0, "window_start": time.time()},
    }
    
    def check_rate_limit(limit_type: str, max_per_minute: int, domain: str = "") -> bool:
        """Check and enforce rate limiting with sliding window."""
        now = time.time()
        window_seconds = 60
        
        if limit_type == "email_global":
            state = _rate_limit_state["email_per_minute"]["global"]
            if now - state["window_start"] >= window_seconds:
                state["count"] = 0
                state["window_start"] = now
            if state["count"] >= max_per_minute:
                wait_time = window_seconds - (now - state["window_start"])
                if wait_time > 0:
                    time.sleep(min(wait_time, 5))  # Cap at 5s per check
                    state["count"] = 0
                    state["window_start"] = time.time()
            state["count"] += 1
            return True
        
        elif limit_type == "email_domain" and domain:
            state = _rate_limit_state["domain_per_minute"][domain]
            if now - state["window_start"] >= window_seconds:
                state["count"] = 0
                state["window_start"] = now
            if state["count"] >= max_per_minute:
                wait_time = window_seconds - (now - state["window_start"])
                if wait_time > 0:
                    time.sleep(min(wait_time, 5))
                    state["count"] = 0
                    state["window_start"] = time.time()
            state["count"] += 1
            return True
        
        elif limit_type == "linkedin":
            state = _rate_limit_state["linkedin_per_minute"]
            if now - state["window_start"] >= window_seconds:
                state["count"] = 0
                state["window_start"] = now
            if state["count"] >= max_per_minute:
                wait_time = window_seconds - (now - state["window_start"])
                if wait_time > 0:
                    time.sleep(min(wait_time, 5))
                    state["count"] = 0
                    state["window_start"] = time.time()
            state["count"] += 1
            return True
        
        return True
    
    def check_webhook_health(webhook_url: str, timeout: int = 5) -> Dict[str, Any]:
        """Check if webhook is healthy and responsive."""
        try:
            start_time = time.time()
            # Try HEAD request first (lightweight)
            try:
                resp = requests.head(webhook_url, timeout=timeout, allow_redirects=True)
                response_time_ms = (time.time() - start_time) * 1000
                
                if resp.status_code < 500:  # 2xx, 3xx, 4xx are OK (4xx might be expected)
                    return {
                        "healthy": True,
                        "status_code": resp.status_code,
                        "response_time_ms": round(response_time_ms, 2),
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": resp.status_code,
                        "response_time_ms": round(response_time_ms, 2),
                        "error": "Server error",
                    }
            except requests.exceptions.Timeout:
                return {
                    "healthy": False,
                    "error": "Timeout",
                    "timeout_ms": timeout * 1000,
                }
            except requests.exceptions.ConnectionError:
                return {
                    "healthy": False,
                    "error": "Connection failed",
                }
            except Exception as e:
                return {
                    "healthy": False,
                    "error": str(e)[:200],
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)[:200],
            }
    
    # Main tasks
    @task(task_id="load_leads")
    def load_leads() -> List[Dict[str, Any]]:
        """Load and validate leads from CSV."""
        ctx = get_current_context()
        params = ctx["params"]
        
        csv_url = str(params.get("leads_csv_url", "")).strip()
        if not csv_url:
            raise ValueError("leads_csv_url is required")
        
        # Load leads
        df = load_csv_from_url(csv_url)
        if df.empty:
            logger.warning("No leads loaded from CSV")
            return []
        
        # Load suppression lists
        suppression = set()
        sup_csv = str(params.get("suppression_csv_url", "")).strip()
        if sup_csv:
            suppression.update(load_emails_from_url(sup_csv))
        
        unsub_csv = str(params.get("unsubscribe_csv_url", "")).strip()
        if unsub_csv:
            suppression.update(load_emails_from_url(unsub_csv))
        
        unsub_api = str(params.get("unsubscribe_api_url", "")).strip()
        if unsub_api:
            suppression.update(load_emails_from_url(unsub_api))
        
        # Load blocked domains
        blocked_domains = set()
        blocked_csv = str(params.get("blocked_domains_csv_url", "")).strip()
        if blocked_csv:
            df_blocked = load_csv_from_url(blocked_csv)
            if not df_blocked.empty:
                col = "domain" if "domain" in df_blocked.columns else df_blocked.columns[0]
                blocked_domains.update(df_blocked[col].astype(str).str.strip().str.lower().dropna().tolist())
        
        # Load VIP emails
        vip_emails = set()
        vip_csv = str(params.get("vip_emails_csv_url", "")).strip()
        if vip_csv:
            vip_emails.update(load_emails_from_url(vip_csv))
        
        # Process leads
        leads = []
        seen_emails = set()
        filter_roles = bool(params.get("filter_role_accounts", True))
        strict_val = bool(params.get("strict_validation", False))
        min_fields = int(params.get("min_lead_fields", 2))
        
        for _, row in df.iterrows():
            email = str(row.get("email", "")).strip().lower()
            if not email or "@" not in email:
                continue
            
            # Deduplication
            if email in seen_emails:
                continue
            seen_emails.add(email)
            
            # Suppression check
            if email in suppression:
                continue
            
            # Blocked domain check
            domain = extract_domain(email)
            if domain in blocked_domains:
                continue
            
            # Role account filter
            if filter_roles and is_role_account(email):
                continue
            
            # Email validation
            if not is_valid_email(email):
                continue
            
            # Strict validation
            if strict_val:
                first_name = str(row.get("first_name", "")).strip()
                last_name = str(row.get("last_name", "")).strip()
                company = str(row.get("company", "")).strip()
                if not first_name or not last_name or not company:
                    continue
            
            # Min fields check
            filled_fields = sum(1 for k in ["first_name", "last_name", "company", "email"] if str(row.get(k, "")).strip())
            if filled_fields < min_fields:
                continue
            
            # Build lead dict
            lead = {
                "email": email,
                "first_name": str(row.get("first_name", "")).strip() or "Valued",
                "last_name": str(row.get("last_name", "")).strip() or "Customer",
                "company": str(row.get("company", "")).strip() or "",
                "linkedin_url": str(row.get("linkedin_url", "")).strip() or "",
                "industry": str(row.get("industry", "")).strip() or "",
                "language": str(row.get(params.get("language_column", "language"), "")).strip() or "",
                "is_vip": email in vip_emails,
                "domain": domain,
            }
            
            # Add all other columns
            for col in df.columns:
                if col not in lead:
                    lead[col] = str(row[col]) if pd.notna(row[col]) else ""
            
            leads.append(lead)
        
        # Apply max leads limit
        max_limit = int(params.get("max_leads_limit", 0))
        if max_limit > 0:
            leads = leads[:max_limit]
        
        # VIP prioritization
        vip_leads = [l for l in leads if l.get("is_vip")]
        regular_leads = [l for l in leads if not l.get("is_vip")]
        leads = vip_leads + regular_leads
        
        logger.info(f"Loaded {len(leads)} leads (VIPs: {len(vip_leads)})")
        
        Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.loaded", len(leads))
        Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.vip", len(vip_leads))
        
        return leads
    
    @task(task_id="enrich_leads")
    def enrich_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich leads with external data."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_lead_enrichment", False)):
            return leads
        
        api_url = str(params.get("enrichment_api_url", "")).strip()
        if not api_url:
            logger.warning("Enrichment enabled but no API URL provided")
            return leads
        
        api_key = str(params.get("enrichment_api_key", "")).strip()
        timeout = int(params.get("enrichment_timeout_seconds", 10))
        fields = str(params.get("enrichment_fields", "company_size,job_title,industry,location,social_profiles"))
        
        enriched_count = 0
        for lead in leads:
            if not lead.get("_enriched"):
                lead = enrich_lead(lead, api_url, api_key, timeout, fields)
                if lead.get("_enriched"):
                    enriched_count += 1
        
        logger.info(f"Enriched {enriched_count} leads")
        Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.enriched", enriched_count)
        
        return leads
    
    @task(task_id="score_leads")
    def score_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate scores for leads."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_lead_scoring", False)):
            return leads
        
        try:
            weights_json = str(params.get("scoring_weights_json", "{}"))
            weights = json.loads(weights_json)
        except Exception:
            weights = {"email_quality": 10, "company_size": 20, "job_title": 15, "industry_fit": 25, "engagement": 30}
        
        min_score = int(params.get("min_score_to_contact", 0))
        
        scored_leads = []
        for lead in leads:
            score = score_lead(lead, weights)
            lead["score"] = score
            if score >= min_score:
                scored_leads.append(lead)
        
        logger.info(f"Scored {len(leads)} leads, {len(scored_leads)} passed minimum score threshold")
        Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.scored", len(leads))
        
        return scored_leads if min_score > 0 else leads
    
    @task(task_id="check_holidays")
    def check_holidays(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out holidays if enabled."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_calendar_check", False)) or not bool(params.get("skip_holidays", True)):
            return leads
        
        country = str(params.get("calendar_country", "US"))
        region = str(params.get("calendar_region", "")).strip()
        
        now = pendulum.now("UTC")
        today = now.date()
        
        if is_holiday(now, country, region):
            logger.warning(f"Today ({today}) is a holiday in {country}, skipping all leads")
            Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.skipped_holiday", len(leads))
            return []
        
        return leads
    
    @task(task_id="check_warmup")
    def check_warmup(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check domain warm-up status and filter leads if needed."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_domain_warmup", False)):
            return leads
        
        api_url = str(params.get("warmup_api_url", "")).strip()
        if not api_url:
            logger.warning("Domain warm-up enabled but no API URL provided")
            return leads
        
        threshold = int(params.get("warmup_progress_threshold", 50))
        daily_limit = int(params.get("warmup_daily_limit", 50))
        
        domain_status = {}
        filtered_leads = []
        domain_counts = defaultdict(int)
        
        for lead in leads:
            domain = lead.get("domain", "")
            if not domain:
                filtered_leads.append(lead)
                continue
            
            if domain not in domain_status:
                status = check_domain_warmup(domain, api_url)
                domain_status[domain] = status
            
            status = domain_status[domain]
            
            if status.get("warmed", False) or status.get("progress", 0) >= threshold:
                if domain_counts[domain] < daily_limit:
                    filtered_leads.append(lead)
                    domain_counts[domain] += 1
            else:
                logger.debug(f"Domain {domain} not warmed (progress: {status.get('progress', 0)}%)")
        
        skipped = len(leads) - len(filtered_leads)
        if skipped > 0:
            logger.info(f"Skipped {skipped} leads due to domain warm-up status")
            Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.leads.skipped_warmup", skipped)
        
        return filtered_leads
    
    @task(task_id="send_initial_email")
    def send_initial_email(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Send initial email to a lead."""
        ctx = get_current_context()
        params = ctx["params"]
        
        dry_run = bool(params.get("dry_run", False))
        webhook_url = str(params.get("email_webhook_url", "")).strip()
        if not webhook_url and not dry_run:
            return {"lead": lead, "status": "skipped", "reason": "no_webhook"}
        
        # Health check (optional)
        healthcheck_enabled = bool(params.get("webhook_healthcheck_enabled", False))
        if healthcheck_enabled and not dry_run:
            health_timeout = int(params.get("webhook_healthcheck_timeout", 5))
            health = check_webhook_health(webhook_url, health_timeout)
            if not health.get("healthy", False):
                logger.warning(f"Webhook health check failed: {health.get('error', 'unknown')}")
                return {"lead": lead, "status": "skipped", "reason": "webhook_unhealthy", "health": health}
        
        # Rate limiting with domain tracking
        max_emails_per_min = int(params.get("max_emails_per_minute", 20))
        max_domain_per_min = int(params.get("max_domain_emails_per_minute", 3))
        
        domain = lead.get("domain", "")
        check_rate_limit("email_global", max_emails_per_min)
        if domain and max_domain_per_min > 0:
            check_rate_limit("email_domain", max_domain_per_min, domain)
        
        # Jitter and fixed sleep
        time.sleep(random.uniform(0, float(params.get("send_jitter_seconds", 2))))
        fixed_sleep = float(params.get("fixed_rate_sleep_seconds", 0))
        if fixed_sleep > 0:
            time.sleep(fixed_sleep)
        
        # Domain cooldown
        domain_cooldown = int(params.get("domain_cooldown_seconds", 0))
        if domain_cooldown > 0 and domain:
            last_sent = _rate_limit_state["domain_per_minute"][domain].get("last_sent", 0)
            if time.time() - last_sent < domain_cooldown:
                wait = domain_cooldown - (time.time() - last_sent)
                time.sleep(min(wait, domain_cooldown))
            _rate_limit_state["domain_per_minute"][domain]["last_sent"] = time.time()
        
        # Determine template variant (A/B or VIP or Industry)
        is_vip = lead.get("is_vip", False)
        industry = lead.get("industry", "")
        language = lead.get("language", "")
        
        # Load industry templates
        industry_templates = {}
        try:
            industry_json = str(params.get("industry_templates_json", "{}"))
            industry_templates = json.loads(industry_json)
        except Exception:
            pass
        
        # Load multi-language templates
        lang_templates = {}
        try:
            lang_json = str(params.get("multi_language_templates_json", "{}"))
            lang_templates = json.loads(lang_json)
        except Exception:
            pass
        
        # Priority: Industry > VIP > Language > A/B > Default
        subject_template = str(params.get("email_subject_template", ""))
        body_template = str(params.get("email_body_template", ""))
        use_b = False  # Default A/B variant
        
        if industry and industry in industry_templates:
            tmpl = industry_templates[industry]
            subject_template = tmpl.get("subject", subject_template)
            body_template = tmpl.get("body", body_template)
        elif is_vip:
            subject_template = str(params.get("email_subject_template_vip", subject_template))
            body_template = str(params.get("email_body_template_vip", body_template))
        elif language and language in lang_templates:
            tmpl = lang_templates[language]
            subject_template = tmpl.get("subject", subject_template)
            body_template = tmpl.get("body", body_template)
        else:
            # A/B testing
            email_hash = int(hashlib.md5(lead["email"].encode()).hexdigest(), 16)
            ab_percent = int(params.get("ab_split_percent", 50))
            use_b = (email_hash % 100) < ab_percent
            
            if use_b:
                subject_template = str(params.get("email_subject_template_b", subject_template))
                body_template = str(params.get("email_body_template_b", body_template))
        
        # Render templates
        enable_conditionals = bool(params.get("enable_conditional_templates", False))
        enable_loops = bool(params.get("enable_template_loops", False))
        
        subject = render_template_advanced(subject_template, lead, enable_conditionals, enable_loops)
        body = render_template_advanced(body_template, lead, enable_conditionals, enable_loops)
        
        # Calculate send time
        now = pendulum.now("UTC")
        start_hour = str(params.get("business_hours_start_utc", "09:00"))
        end_hour = str(params.get("business_hours_end_utc", "17:00"))
        tz = str(params.get("business_tz", "UTC"))
        exclude_weekends = bool(params.get("exclude_weekends", True))
        skip_holidays = bool(params.get("skip_holidays", True)) if params.get("enable_calendar_check") else False
        country = str(params.get("calendar_country", "US"))
        
        run_at = calculate_next_business_time(now, start_hour, end_hour, tz, exclude_weekends, skip_holidays, country)
        
        # Prepare payload
        payload = {
            "from": str(params.get("email_from", "growth@example.com")),
            "to": lead["email"],
            "subject": subject,
            "text": body,
            "html": body,
            "run_at": run_at.isoformat() + "Z",
            "metadata": {
                "channel": "email",
                "sequence_step": "email_1",
                "lead_email": lead["email"][:5] + "***",  # PII-safe
            },
        }
        
        # Idempotency key
        now_str = datetime.utcnow().strftime("%Y%m%d")
        headers = {
            "Content-Type": "application/json",
            "X-Idempotency-Key": f"email1-{lead['email']}-{now_str}",
        }
        
        # Add custom headers
        try:
            custom_headers_json = str(params.get("email_webhook_headers_json", "{}"))
            custom_headers = json.loads(custom_headers_json)
            headers.update(custom_headers)
        except Exception:
            pass
        
        # Send
        if dry_run:
            result = {"lead": lead, "status": "ok", "dry_run": True}
        else:
            try:
                timeout = int(params.get("request_timeout_seconds", 20))
                attempts = int(params.get("retry_attempts", 3))
                last_err = None
                
                for attempt in range(1, attempts + 1):
                    try:
                        resp = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
                        if resp.status_code < 300:
                            result = {"lead": lead, "status": "ok"}
                            break
                        last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    except Exception as e:
                        last_err = str(e)[:200]
                    
                    if attempt < attempts:
                        backoff = 2 ** attempt + random.random()
                        time.sleep(backoff)
                
                if last_err:
                    result = {"lead": lead, "status": "failed", "error": last_err}
            except Exception as e:
                result = {"lead": lead, "status": "failed", "error": str(e)[:200]}
        
        # Persist event
        results_dir = str(params.get("results_dir", "/tmp/outreach_results"))
        os.makedirs(results_dir, exist_ok=True)
        events_path = os.path.join(results_dir, "events.jsonl")
        
        # Store A/B variant in result for later use
        result["ab_variant"] = "B" if use_b else "A"
        result["is_vip"] = is_vip
        
        event = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "step": "email_1",
            "email": lead["email"][:5] + "***",
            "status": result.get("status", "unknown"),
            "ab": "B" if use_b else "A",
            "vip": is_vip,
        }
        
        try:
            with open(events_path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass
        
        Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.email.initial.sent", 1)
        if result.get("status") == "failed":
            Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.email.initial.failed", 1)
            # DLQ
            dlq_path = os.path.join(results_dir, "dlq.jsonl")
            try:
                with open(dlq_path, "a") as f:
                    f.write(json.dumps({"ts": event["ts"], "step": "email_1", "lead": lead, "error": result.get("error", "")}) + "\n")
            except Exception:
                pass
        
        return result
    
    # Continue with remaining tasks... (check_engagement, send_linkedin, enqueue_followup, summarize, etc.)
    # For brevity, I'll add the key remaining tasks
    
    @task(task_id="check_engagement")
    def check_engagement(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Check engagement status for a lead."""
        ctx = get_current_context()
        params = ctx["params"]
        
        check_url = str(params.get("engagement_check_url", "")).strip()
        update_url = str(params.get("engagement_update_api_url", "")).strip()
        
        email = lead.get("email", "")
        lead["opened"] = False
        lead["replied"] = False
        
        # Try update API first (more recent)
        if update_url:
            try:
                r = requests.get(f"{update_url}?email={email}", timeout=int(params.get("engagement_timeout_seconds", 5)))
                if r.status_code < 300:
                    data = r.json()
                    lead["opened"] = bool(data.get("opened", False))
                    lead["replied"] = bool(data.get("replied", False))
                    return lead
            except Exception:
                pass
        
        # Fallback to check URL
        if check_url:
            try:
                r = requests.get(f"{check_url}?email={email}", timeout=int(params.get("engagement_timeout_seconds", 5)))
                if r.status_code < 300:
                    data = r.json()
                    lead["opened"] = bool(data.get("opened", False))
                    lead["replied"] = bool(data.get("replied", False))
            except Exception:
                pass
        
        return lead
    
    @task(task_id="send_linkedin")
    def send_linkedin(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Send LinkedIn action for a lead."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_linkedin", True)):
            return {"lead": lead, "status": "skipped", "reason": "disabled"}
        
        skip_if_opened = bool(params.get("skip_linkedin_if_opened", True))
        if skip_if_opened and lead.get("opened", False):
            return {"lead": lead, "status": "skipped", "reason": "opened"}
        
        dry_run = bool(params.get("dry_run", False))
        webhook_url = str(params.get("linkedin_webhook_url", "")).strip()
        if not webhook_url and not dry_run:
            return {"lead": lead, "status": "skipped", "reason": "no_webhook"}
        
        # Health check
        healthcheck_enabled = bool(params.get("webhook_healthcheck_enabled", False))
        if healthcheck_enabled and not dry_run:
            health_timeout = int(params.get("webhook_healthcheck_timeout", 5))
            health = check_webhook_health(webhook_url, health_timeout)
            if not health.get("healthy", False):
                logger.warning(f"LinkedIn webhook health check failed: {health.get('error', 'unknown')}")
                return {"lead": lead, "status": "skipped", "reason": "webhook_unhealthy", "health": health}
        
        # Rate limiting
        max_linkedin_per_min = int(params.get("max_linkedin_per_minute", 5))
        check_rate_limit("linkedin", max_linkedin_per_min)
        
        delay_days = int(params.get("linkedin_delay_days", 2))
        run_at = pendulum.now("UTC").add(days=delay_days)
        
        payload = {
            "action": "linkedin_connect_or_message",
            "run_at": run_at.isoformat() + "Z",
            "data": {
                "email": lead["email"],
                "linkedin_url": lead.get("linkedin_url", ""),
                "first_name": lead.get("first_name", ""),
                "company": lead.get("company", ""),
            },
            "metadata": {"channel": "linkedin", "sequence_step": "linkedin_1"},
        }
        
        headers = {"Content-Type": "application/json"}
        try:
            custom_headers_json = str(params.get("linkedin_webhook_headers_json", "{}"))
            custom_headers = json.loads(custom_headers_json)
            headers.update(custom_headers)
        except Exception:
            pass
        
        if dry_run:
            return {"lead": lead, "status": "ok", "dry_run": True}
        
        try:
            timeout = int(params.get("request_timeout_seconds", 20))
            resp = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code < 300:
                Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.linkedin.sent", 1)
                return {"lead": lead, "status": "ok"}
            return {"lead": lead, "status": "failed", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"lead": lead, "status": "failed", "error": str(e)[:200]}
    
    @task(task_id="enqueue_followup")
    def enqueue_followup(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Enqueue follow-up email."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("enable_followup", True)):
            return {"lead": lead, "status": "skipped", "reason": "disabled"}
        
        skip_if_replied = bool(params.get("skip_followup_if_replied", True))
        if skip_if_replied and lead.get("replied", False):
            return {"lead": lead, "status": "skipped", "reason": "replied"}
        
        dry_run = bool(params.get("dry_run", False))
        webhook_url = str(params.get("email_webhook_url", "")).strip()
        if not webhook_url and not dry_run:
            return {"lead": lead, "status": "skipped", "reason": "no_webhook"}
        
        delay_days = int(params.get("followup_delay_days", 5))
        run_at = pendulum.now("UTC").add(days=delay_days)
        
        # Template selection (similar to initial email)
        is_vip = lead.get("is_vip", False)
        industry = lead.get("industry", "")
        
        industry_templates = {}
        try:
            industry_json = str(params.get("industry_templates_json", "{}"))
            industry_templates = json.loads(industry_json)
        except Exception:
            pass
        
        subject_template = str(params.get("email2_subject_template", ""))
        body_template = str(params.get("email2_body_template", ""))
        
        if industry and industry in industry_templates:
            tmpl = industry_templates[industry]
            subject_template = tmpl.get("subject2", subject_template)
            body_template = tmpl.get("body2", body_template)
        elif is_vip:
            subject_template = str(params.get("email2_subject_template_vip", subject_template))
            body_template = str(params.get("email2_body_template_vip", body_template))
        else:
            # A/B
            email_hash = int(hashlib.md5(lead["email"].encode()).hexdigest(), 16)
            ab_percent = int(params.get("ab_split_percent", 50))
            use_b = (email_hash % 100) < ab_percent
            if use_b:
                subject_template = str(params.get("email2_subject_template_b", subject_template))
                body_template = str(params.get("email2_body_template_b", body_template))
        
        enable_conditionals = bool(params.get("enable_conditional_templates", False))
        enable_loops = bool(params.get("enable_template_loops", False))
        
        subject = render_template_advanced(subject_template, lead, enable_conditionals, enable_loops)
        body = render_template_advanced(body_template, lead, enable_conditionals, enable_loops)
        
        payload = {
            "from": str(params.get("email_from", "growth@example.com")),
            "to": lead["email"],
            "subject": subject,
            "text": body,
            "html": body,
            "run_at": run_at.isoformat() + "Z",
            "metadata": {"channel": "email", "sequence_step": "email_2"},
        }
        
        headers = {"Content-Type": "application/json"}
        try:
            custom_headers_json = str(params.get("email_webhook_headers_json", "{}"))
            custom_headers = json.loads(custom_headers_json)
            headers.update(custom_headers)
        except Exception:
            pass
        
        if dry_run:
            return {"lead": lead, "status": "ok", "dry_run": True}
        
        try:
            timeout = int(params.get("request_timeout_seconds", 20))
            resp = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code < 300:
                Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.email.followup.sent", 1)
                return {"lead": lead, "status": "ok"}
            return {"lead": lead, "status": "failed", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"lead": lead, "status": "failed", "error": str(e)[:200]}
    
    @task(task_id="summarize")
    def summarize(email_results: List[Dict[str, Any]], linkedin_results: List[Dict[str, Any]], followup_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize outreach results with advanced analytics and exports."""
        ctx = get_current_context()
        params = ctx["params"]
        run_id = ctx["dag_run"].run_id
        
        total = len(email_results)
        sent = sum(1 for r in email_results if r.get("status") == "ok")
        failed = sum(1 for r in email_results if r.get("status") == "failed")
        skipped = total - sent - failed
        
        # Calculate engagement stats (from engagement_checked leads)
        opened_count = 0
        replied_count = 0
        for r in email_results:
            lead = r.get("lead", {})
            if lead.get("opened"):
                opened_count += 1
            if lead.get("replied"):
                replied_count += 1
        
        # A/B stats
        ab_a = sum(1 for r in email_results if r.get("ab_variant") == "A" or (not r.get("ab_variant") and r.get("lead", {}).get("ab") == "A"))
        ab_b = sum(1 for r in email_results if r.get("ab_variant") == "B" or r.get("lead", {}).get("ab") == "B")
        
        # VIP stats
        vip_total = sum(1 for r in email_results if r.get("lead", {}).get("is_vip") or r.get("is_vip"))
        vip_sent = sum(1 for r in email_results if r.get("status") == "ok" and (r.get("lead", {}).get("is_vip") or r.get("is_vip")))
        vip_opened = sum(1 for r in email_results if (r.get("lead", {}).get("is_vip") or r.get("is_vip")) and r.get("lead", {}).get("opened"))
        vip_replied = sum(1 for r in email_results if (r.get("lead", {}).get("is_vip") or r.get("is_vip")) and r.get("lead", {}).get("replied"))
        
        # Domain stats
        domain_stats = defaultdict(lambda: {"sent": 0, "opened": 0, "replied": 0, "failed": 0})
        for r in email_results:
            lead = r.get("lead", {})
            domain = lead.get("domain", "unknown")
            if r.get("status") == "ok":
                domain_stats[domain]["sent"] += 1
            elif r.get("status") == "failed":
                domain_stats[domain]["failed"] += 1
            if lead.get("opened"):
                domain_stats[domain]["opened"] += 1
            if lead.get("replied"):
                domain_stats[domain]["replied"] += 1
        
        # Calculate rates
        open_rate = (opened_count / sent * 100) if sent > 0 else 0
        reply_rate = (replied_count / sent * 100) if sent > 0 else 0
        conversion_rate = (replied_count / total * 100) if total > 0 else 0
        error_rate = (failed / total * 100) if total > 0 else 0
        
        # A/B comparison
        ab_winner = None
        if ab_a > 0 and ab_b > 0:
            ab_a_opened = sum(1 for r in email_results if (r.get("ab_variant") == "A" or r.get("lead", {}).get("ab") == "A") and r.get("lead", {}).get("opened"))
            ab_b_opened = sum(1 for r in email_results if r.get("ab_variant") == "B" or (r.get("lead", {}).get("ab") == "B" and r.get("lead", {}).get("opened")))
            ab_a_rate = (ab_a_opened / ab_a * 100) if ab_a > 0 else 0
            ab_b_rate = (ab_b_opened / ab_b * 100) if ab_b > 0 else 0
            if ab_b_rate > ab_a_rate * 1.05:  # 5% improvement threshold
                ab_winner = "B"
            elif ab_a_rate > ab_b_rate * 1.05:
                ab_winner = "A"
        
        # Aggregate stats
        summary = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_leads": total,
            "emails_sent": sent,
            "emails_failed": failed,
            "emails_skipped": skipped,
            "linkedin_sent": sum(1 for r in linkedin_results if r.get("status") == "ok"),
            "followups_sent": sum(1 for r in followup_results if r.get("status") == "ok"),
            "opened": opened_count,
            "replied": replied_count,
            "open_rate": round(open_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "conversion_rate": round(conversion_rate, 2),
            "error_rate": round(error_rate, 2),
            "ab_variant_a": ab_a,
            "ab_variant_b": ab_b,
            "ab_winner": ab_winner,
            "total_vip": vip_total,
            "vip_sent": vip_sent,
            "opened_vip": vip_opened,
            "replied_vip": vip_replied,
            "domain_stats": dict(domain_stats),
        }
        
        # Persist summary
        results_dir = str(params.get("results_dir", "/tmp/outreach_results"))
        os.makedirs(results_dir, exist_ok=True)
        
        summary_path = os.path.join(results_dir, "summary.jsonl")
        try:
            with open(summary_path, "a") as f:
                f.write(json.dumps(summary) + "\n")
        except Exception:
            pass
        
        # Export domain stats separately
        domain_stats_path = os.path.join(results_dir, f"domain_stats_{run_id}.json")
        try:
            with open(domain_stats_path, "w") as f:
                json.dump(domain_stats, f, indent=2)
        except Exception:
            pass
        
        # Export formats
        export_formats_str = str(params.get("export_formats", "csv")).lower()
        if export_formats_str in ("csv", "all"):
            csv_path = os.path.join(results_dir, f"summary_{run_id}.csv")
            try:
                pd.DataFrame([summary]).to_csv(csv_path, index=False)
            except Exception:
                pass
        
        if export_formats_str in ("json", "all"):
            json_path = os.path.join(results_dir, f"summary_{run_id}.json")
            try:
                with open(json_path, "w") as f:
                    json.dump(summary, f, indent=2)
            except Exception:
                pass
        
        # Export Excel
        if bool(params.get("export_excel", False)) and _HAS_OPENPYXL:
            try:
                excel_path = os.path.join(results_dir, f"summary_{run_id}.xlsx")
                wb = Workbook()
                
                # Summary sheet
                ws_summary = wb.active
                ws_summary.title = "Summary"
                ws_summary.append(["Metric", "Value"])
                for key, value in summary.items():
                    if key != "domain_stats":
                        ws_summary.append([key, value])
                
                # Domain stats sheet
                ws_domains = wb.create_sheet("Domains")
                ws_domains.append(["Domain", "Sent", "Opened", "Replied", "Failed", "Open Rate", "Reply Rate"])
                for domain, stats in sorted(domain_stats.items(), key=lambda x: x[1]["sent"], reverse=True):
                    domain_sent = stats["sent"]
                    domain_opened = stats["opened"]
                    domain_replied = stats["replied"]
                    domain_failed = stats["failed"]
                    domain_open_rate = (domain_opened / domain_sent * 100) if domain_sent > 0 else 0
                    domain_reply_rate = (domain_replied / domain_sent * 100) if domain_sent > 0 else 0
                    ws_domains.append([domain, domain_sent, domain_opened, domain_replied, domain_failed, 
                                      round(domain_open_rate, 2), round(domain_reply_rate, 2)])
                
                wb.save(excel_path)
                logger.info(f"Excel export saved to {excel_path}")
            except Exception as e:
                logger.error(f"Excel export failed: {e}")
        
        # Export Prometheus format
        if bool(params.get("export_prometheus_format", False)):
            try:
                prom_path = os.path.join(results_dir, f"metrics_{run_id}.prom")
                with open(prom_path, "w") as f:
                    prefix = params.get("metrics_prefix", "outreach")
                    f.write(f"# HELP {prefix}_leads_total Total leads processed\n")
                    f.write(f"# TYPE {prefix}_leads_total counter\n")
                    f.write(f'{prefix}_leads_total{{run_id="{run_id}"}} {total}\n')
                    f.write(f"# HELP {prefix}_emails_sent_total Total emails sent\n")
                    f.write(f"# TYPE {prefix}_emails_sent_total counter\n")
                    f.write(f'{prefix}_emails_sent_total{{run_id="{run_id}"}} {sent}\n')
                    f.write(f"# HELP {prefix}_open_rate Open rate percentage\n")
                    f.write(f"# TYPE {prefix}_open_rate gauge\n")
                    f.write(f'{prefix}_open_rate{{run_id="{run_id}"}} {open_rate}\n')
                    f.write(f"# HELP {prefix}_reply_rate Reply rate percentage\n")
                    f.write(f"# TYPE {prefix}_reply_rate gauge\n")
                    f.write(f'{prefix}_reply_rate{{run_id="{run_id}"}} {reply_rate}\n')
            except Exception:
                pass
        
        # Export dashboard HTML
        if bool(params.get("export_dashboard_html", False)):
            try:
                html_path = os.path.join(results_dir, f"dashboard_{run_id}.html")
                
                # Prepare domain data for JS
                top_domains_list = sorted(domain_stats.items(), key=lambda x: x[1]["sent"], reverse=True)[:10]
                top_domains_js = json.dumps([[d[0], d[1]["sent"]] for d in top_domains_list])
                
                ab_winner_text = f"<p><strong>Winner: Variant {ab_winner}</strong></p>" if ab_winner else "<p>No clear winner (threshold not met)</p>"
                
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Outreach Dashboard - {run_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
        canvas {{ max-height: 400px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Outreach Dashboard - {run_id}</h1>
        
        <div class="card">
            <h2>Overview</h2>
            <div class="metric">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Leads</div>
            </div>
            <div class="metric">
                <div class="metric-value">{sent}</div>
                <div class="metric-label">Emails Sent</div>
            </div>
            <div class="metric">
                <div class="metric-value">{opened_count}</div>
                <div class="metric-label">Opened</div>
            </div>
            <div class="metric">
                <div class="metric-value">{replied_count}</div>
                <div class="metric-label">Replied</div>
            </div>
            <div class="metric">
                <div class="metric-value">{round(open_rate, 1)}%</div>
                <div class="metric-label">Open Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{round(reply_rate, 1)}%</div>
                <div class="metric-label">Reply Rate</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Engagement Overview</h2>
            <canvas id="engagementChart"></canvas>
        </div>
        
        <div class="card">
            <h2>A/B Test Results</h2>
            <canvas id="abChart"></canvas>
            {ab_winner_text}
        </div>
        
        <div class="card">
            <h2>Top Domains</h2>
            <canvas id="domainChart"></canvas>
        </div>
    </div>
    
    <script>
        const topDomains = {top_domains_js};
        
        // Engagement chart
        const ctx1 = document.getElementById('engagementChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'doughnut',
            data: {{
                labels: ['Sent', 'Opened', 'Replied'],
                datasets: [{{
                    data: [{sent}, {opened_count}, {replied_count}],
                    backgroundColor: ['#2196F3', '#4CAF50', '#FF9800']
                }}]
            }}
        }});
        
        // A/B test chart
        const ctx2 = document.getElementById('abChart').getContext('2d');
        new Chart(ctx2, {{
            type: 'bar',
            data: {{
                labels: ['Variant A', 'Variant B'],
                datasets: [{{
                    label: 'Sent',
                    data: [{ab_a}, {ab_b}],
                    backgroundColor: '#2196F3'
                }}]
            }}
        }});
        
        // Domain chart (top 10)
        const ctx3 = document.getElementById('domainChart').getContext('2d');
        new Chart(ctx3, {{
            type: 'bar',
            data: {{
                labels: topDomains.map(d => d[0]),
                datasets: [{{
                    label: 'Emails Sent',
                    data: topDomains.map(d => d[1]),
                    backgroundColor: '#2196F3'
                }}]
            }},
            options: {{
                indexAxis: 'y'
            }}
        }});
    </script>
</body>
</html>"""
                with open(html_path, "w") as f:
                    f.write(html_content)
                logger.info(f"Dashboard HTML saved to {html_path}")
            except Exception as e:
                logger.error(f"Dashboard HTML export failed: {e}")
        
        # Export processed leads
        if bool(params.get("export_processed_leads", False)):
            try:
                leads_data = []
                for r in email_results:
                    lead = r.get("lead", {})
                    leads_data.append({
                        "email": lead.get("email", "")[:5] + "***",
                        "first_name": lead.get("first_name", ""),
                        "last_name": lead.get("last_name", ""),
                        "company": lead.get("company", ""),
                        "domain": lead.get("domain", ""),
                        "is_vip": lead.get("is_vip", False),
                        "email_sent": r.get("status") == "ok",
                        "opened": lead.get("opened", False),
                        "replied": lead.get("replied", False),
                        "ab_variant": r.get("ab_variant", lead.get("ab", "A")),
                    })
                leads_df = pd.DataFrame(leads_data)
                leads_path = os.path.join(results_dir, f"processed_leads_{run_id}.csv")
                leads_df.to_csv(leads_path, index=False)
                logger.info(f"Processed leads exported to {leads_path}")
            except Exception as e:
                logger.error(f"Processed leads export failed: {e}")
        
        # Executive report
        if bool(params.get("export_executive_report", False)):
            try:
                report_path = os.path.join(results_dir, f"executive_report_{run_id}.txt")
                with open(report_path, "w") as f:
                    f.write("=" * 60 + "\n")
                    f.write("OUTREACH EXECUTIVE REPORT\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Run ID: {run_id}\n")
                    f.write(f"Timestamp: {summary['timestamp']}\n\n")
                    f.write("SUMMARY\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"Total Leads: {total}\n")
                    f.write(f"Emails Sent: {sent}\n")
                    f.write(f"Opened: {opened_count} ({open_rate:.1f}%)\n")
                    f.write(f"Replied: {replied_count} ({reply_rate:.1f}%)\n")
                    f.write(f"Conversion Rate: {conversion_rate:.1f}%\n")
                    f.write(f"Error Rate: {error_rate:.1f}%\n\n")
                    
                    if ab_winner:
                        f.write(f"A/B TEST\n")
                        f.write("-" * 60 + "\n")
                        f.write(f"Variant A: {ab_a} sent\n")
                        f.write(f"Variant B: {ab_b} sent\n")
                        f.write(f"Winner: Variant {ab_winner}\n\n")
                    
                    if vip_total > 0:
                        f.write(f"VIP SEGMENT\n")
                        f.write("-" * 60 + "\n")
                        f.write(f"Total VIPs: {vip_total}\n")
                        f.write(f"VIP Open Rate: {(vip_opened / vip_sent * 100) if vip_sent > 0 else 0:.1f}%\n")
                        f.write(f"VIP Reply Rate: {(vip_replied / vip_sent * 100) if vip_sent > 0 else 0:.1f}%\n\n")
                    
                    f.write("TOP 10 DOMAINS\n")
                    f.write("-" * 60 + "\n")
                    for domain, stats in sorted(domain_stats.items(), key=lambda x: x[1]["sent"], reverse=True)[:10]:
                        domain_sent = stats["sent"]
                        domain_opened = stats["opened"]
                        domain_replied = stats["replied"]
                        f.write(f"{domain}: {domain_sent} sent, {domain_opened} opened ({domain_opened/domain_sent*100 if domain_sent > 0 else 0:.1f}%), {domain_replied} replied\n")
                logger.info(f"Executive report saved to {report_path}")
            except Exception as e:
                logger.error(f"Executive report failed: {e}")
        
        # Callback webhook
        callback_url = str(params.get("callback_webhook_url", "")).strip()
        if callback_url:
            try:
                payload = {
                    "event": "outreach_completed",
                    "run_id": run_id,
                    "summary": summary,
                    "analytics": {
                        "open_rate": open_rate,
                        "reply_rate": reply_rate,
                        "conversion_rate": conversion_rate,
                        "ab_winner": ab_winner,
                    }
                }
                requests.post(callback_url, json=payload, timeout=10)
            except Exception:
                pass
        
        # Send notifications
        slack_url = str(params.get("slack_webhook_url", os.getenv("SLACK_WEBHOOK_URL", ""))).strip()
        if slack_url:
            try:
                message = f"Outreach completed: {sent}/{total} emails sent | Open: {opened_count} ({open_rate:.1f}%) | Reply: {replied_count} ({reply_rate:.1f}%)"
                if ab_winner:
                    message += f" | A/B Winner: {ab_winner}"
                payload = {"text": message}
                requests.post(slack_url, json=payload, timeout=10)
            except Exception:
                pass
        
        # Email notification
        email_to = str(params.get("email_notification_to", "")).strip()
        if email_to:
            try:
                smtp_host = str(params.get("email_notification_smtp_host", "")).strip()
                smtp_port = int(params.get("email_notification_smtp_port", 587))
                smtp_user = str(params.get("email_notification_smtp_user", "")).strip()
                smtp_pass = str(params.get("email_notification_smtp_password", "")).strip()
                use_tls = bool(params.get("email_notification_smtp_use_tls", True))
                
                if smtp_host and smtp_user:
                    email_body = f"""Outreach Summary

Run ID: {run_id}
Total: {total}
Sent: {sent}
Opened: {opened_count} ({open_rate:.1f}%)
Replied: {replied_count} ({reply_rate:.1f}%)
Conversion Rate: {conversion_rate:.1f}%
Error Rate: {error_rate:.1f}%"""
                    if ab_winner:
                        email_body += f"\nA/B Winner: Variant {ab_winner}"
                    msg = MIMEText(email_body)
                    msg["Subject"] = f"Outreach Summary - {run_id}"
                    msg["From"] = smtp_user
                    msg["To"] = email_to
                    
                    server = smtplib.SMTP(smtp_host, smtp_port)
                    if use_tls:
                        server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                    server.quit()
            except Exception as e:
                logger.warning(f"Email notification failed: {e}")
        
        # Proactive alerts
        if bool(params.get("enable_proactive_alerts", False)):
            alert_url = str(params.get("alert_webhook_url", "")).strip()
            if alert_url:
                error_threshold = float(params.get("alert_error_threshold", 0.1))
                if error_rate > error_threshold:
                    send_proactive_alert(f"High error rate: {error_rate:.1%} (threshold: {error_threshold:.1%})", alert_url, "error")
                
                slow_threshold = int(params.get("alert_slow_performance_threshold_ms", 5000))
                # Performance monitoring could be added here
        
        return summary
    
    @task(task_id="predictive_analytics")
    def predictive_analytics(summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical data and provide predictive insights."""
        ctx = get_current_context()
        params = ctx["params"]
        
        historical_path = str(params.get("historical_summary_path", "")).strip()
        if not historical_path:
            return {"enabled": False}
        
        try:
            # Load historical summaries
            historical_summaries = []
            if os.path.exists(historical_path):
                with open(historical_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                rec = json.loads(line)
                                historical_summaries.append(rec)
                            except Exception:
                                continue
            
            if len(historical_summaries) < 5:
                logger.warning("Not enough historical data for predictive analytics")
                return {"enabled": False, "reason": "insufficient_data"}
            
            # Calculate historical averages
            hist_open_rates = [s.get("open_rate", 0) for s in historical_summaries if s.get("open_rate")]
            hist_reply_rates = [s.get("reply_rate", 0) for s in historical_summaries if s.get("reply_rate")]
            hist_conversion_rates = [s.get("conversion_rate", 0) for s in historical_summaries if s.get("conversion_rate")]
            
            avg_open_rate = sum(hist_open_rates) / len(hist_open_rates) if hist_open_rates else 0
            avg_reply_rate = sum(hist_reply_rates) / len(hist_reply_rates) if hist_reply_rates else 0
            avg_conversion_rate = sum(hist_conversion_rates) / len(hist_conversion_rates) if hist_conversion_rates else 0
            
            current_open_rate = summary.get("open_rate", 0)
            current_reply_rate = summary.get("reply_rate", 0)
            current_conversion_rate = summary.get("conversion_rate", 0)
            
            # Performance vs historical
            performance_vs_historical = {
                "open_rate": {
                    "current": current_open_rate,
                    "historical_avg": round(avg_open_rate, 2),
                    "difference": round(current_open_rate - avg_open_rate, 2),
                    "improvement_pct": round(((current_open_rate - avg_open_rate) / avg_open_rate * 100) if avg_open_rate > 0 else 0, 2),
                },
                "reply_rate": {
                    "current": current_reply_rate,
                    "historical_avg": round(avg_reply_rate, 2),
                    "difference": round(current_reply_rate - avg_reply_rate, 2),
                    "improvement_pct": round(((current_reply_rate - avg_reply_rate) / avg_reply_rate * 100) if avg_reply_rate > 0 else 0, 2),
                },
                "conversion_rate": {
                    "current": current_conversion_rate,
                    "historical_avg": round(avg_conversion_rate, 2),
                    "difference": round(current_conversion_rate - avg_conversion_rate, 2),
                    "improvement_pct": round(((current_conversion_rate - avg_conversion_rate) / avg_conversion_rate * 100) if avg_conversion_rate > 0 else 0, 2),
                },
            }
            
            # Top performing domains from history
            domain_performance = defaultdict(lambda: {"total_sent": 0, "total_opened": 0, "total_replied": 0})
            for s in historical_summaries:
                domain_stats = s.get("domain_stats", {})
                if isinstance(domain_stats, dict):
                    for domain, stats in domain_stats.items():
                        domain_performance[domain]["total_sent"] += stats.get("sent", 0)
                        domain_performance[domain]["total_opened"] += stats.get("opened", 0)
                        domain_performance[domain]["total_replied"] += stats.get("replied", 0)
            
            # Calculate average rates per domain
            top_performing_domains = []
            for domain, perf in domain_performance.items():
                if perf["total_sent"] > 0:
                    avg_domain_open = (perf["total_opened"] / perf["total_sent"] * 100) if perf["total_sent"] > 0 else 0
                    avg_domain_reply = (perf["total_replied"] / perf["total_sent"] * 100) if perf["total_sent"] > 0 else 0
                    top_performing_domains.append({
                        "domain": domain,
                        "total_sent": perf["total_sent"],
                        "avg_open_rate": round(avg_domain_open, 2),
                        "avg_reply_rate": round(avg_domain_reply, 2),
                    })
            
            top_performing_domains.sort(key=lambda x: x["avg_reply_rate"], reverse=True)
            
            analytics = {
                "enabled": True,
                "historical_runs_analyzed": len(historical_summaries),
                "performance_vs_historical": performance_vs_historical,
                "top_performing_domains": top_performing_domains[:10],
                "recommendations": [],
            }
            
            # Generate recommendations
            if current_open_rate < avg_open_rate * 0.9:
                analytics["recommendations"].append("Open rate is below historical average. Consider reviewing subject lines.")
            if current_reply_rate < avg_reply_rate * 0.9:
                analytics["recommendations"].append("Reply rate is below historical average. Consider personalization improvements.")
            if current_open_rate > avg_open_rate * 1.1:
                analytics["recommendations"].append("Open rate is significantly above average. Current approach is working well.")
            
            # Add to summary
            summary["predictive_analytics"] = analytics
            
            # Save analytics
            results_dir = str(params.get("results_dir", "/tmp/outreach_results"))
            analytics_path = os.path.join(results_dir, f"analytics_{ctx['dag_run'].run_id}.json")
            try:
                with open(analytics_path, "w") as f:
                    json.dump(analytics, f, indent=2)
            except Exception:
                pass
            
            return analytics
            
        except Exception as e:
            logger.error(f"Predictive analytics failed: {e}")
            return {"enabled": False, "error": str(e)[:200]}
    
    @task(task_id="sync_to_crm")
    def sync_to_crm(summary: Dict[str, Any], email_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync outreach results to CRM (HubSpot or Salesforce)."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("sync_to_crm", False)):
            return {"enabled": False}
        
        crm_type = str(params.get("crm_type", "hubspot")).lower()
        api_key = str(params.get("crm_api_key", "")).strip()
        base_url = str(params.get("crm_base_url", "")).strip()
        
        if not api_key:
            logger.warning("CRM sync enabled but no API key provided")
            return {"enabled": False, "reason": "no_api_key"}
        
        synced_count = 0
        errors = []
        
        try:
            if crm_type == "hubspot":
                if not base_url:
                    base_url = "https://api.hubapi.com"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                
                for result in email_results[:100]:  # Limit to avoid rate limits
                    lead = result.get("lead", {})
                    if not lead.get("email"):
                        continue
                    
                    try:
                        email = lead.get("email", "")
                        # Create or update contact
                        contact_data = {
                            "properties": {
                                "email": email,
                                "firstname": lead.get("first_name", ""),
                                "lastname": lead.get("last_name", ""),
                                "company": lead.get("company", ""),
                            }
                        }
                        
                        # Add custom properties
                        if result.get("status") == "ok":
                            contact_data["properties"]["outreach_last_sent"] = datetime.utcnow().isoformat()
                            contact_data["properties"]["outreach_status"] = "contacted"
                        if lead.get("opened"):
                            contact_data["properties"]["outreach_opened"] = "yes"
                        if lead.get("replied"):
                            contact_data["properties"]["outreach_replied"] = "yes"
                            contact_data["properties"]["outreach_status"] = "engaged"
                        
                        # HubSpot create or update
                        url = f"{base_url}/crm/v3/objects/contacts"
                        resp = requests.post(url, json=contact_data, headers=headers, timeout=10)
                        
                        if resp.status_code < 300:
                            synced_count += 1
                        else:
                            errors.append(f"{email[:5]}**: HTTP {resp.status_code}")
                        
                    except Exception as e:
                        errors.append(f"{lead.get('email', 'unknown')[:5]}**: {str(e)[:100]}")
            
            elif crm_type == "salesforce":
                if not base_url:
                    base_url = "https://your-instance.salesforce.com"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                
                for result in email_results[:100]:
                    lead = result.get("lead", {})
                    if not lead.get("email"):
                        continue
                    
                    try:
                        email = lead.get("email", "")
                        # Salesforce upsert
                        lead_data = {
                            "Email": email,
                            "FirstName": lead.get("first_name", ""),
                            "LastName": lead.get("last_name", ""),
                            "Company": lead.get("company", ""),
                        }
                        
                        url = f"{base_url}/services/data/v57.0/sobjects/Lead/Email"
                        resp = requests.patch(url, json=lead_data, headers=headers, timeout=10)
                        
                        if resp.status_code < 300:
                            synced_count += 1
                        else:
                            errors.append(f"{email[:5]}**: HTTP {resp.status_code}")
                            
                    except Exception as e:
                        errors.append(f"{lead.get('email', 'unknown')[:5]}**: {str(e)[:100]}")
            
            sync_result = {
                "enabled": True,
                "crm_type": crm_type,
                "synced_count": synced_count,
                "total_attempted": min(len(email_results), 100),
                "errors": errors[:10],  # Limit errors
            }
            
            logger.info(f"Synced {synced_count} leads to {crm_type}")
            Stats.incr(f"{params.get('metrics_prefix', 'outreach')}.crm.synced", synced_count)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"CRM sync failed: {e}")
            return {"enabled": True, "error": str(e)[:200]}
    
    @task(task_id="validate_templates")
    def validate_templates() -> Dict[str, Any]:
        """Pre-flight validation of all email templates."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not bool(params.get("validate_templates", False)):
            return {"enabled": False}
        
        validation_errors = []
        test_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company": "Example Corp",
            "email": "john@example.com",
            "industry": "tech",
            "is_vip": False,
        }
        
        templates_to_check = [
            ("email_subject_template", str(params.get("email_subject_template", ""))),
            ("email_body_template", str(params.get("email_body_template", ""))),
            ("email2_subject_template", str(params.get("email2_subject_template", ""))),
            ("email2_body_template", str(params.get("email2_body_template", ""))),
        ]
        
        # Check VIP templates if provided
        if params.get("email_subject_template_vip"):
            templates_to_check.append(("email_subject_template_vip", str(params.get("email_subject_template_vip", ""))))
        if params.get("email_body_template_vip"):
            templates_to_check.append(("email_body_template_vip", str(params.get("email_body_template_vip", ""))))
        
        # Check A/B templates
        if params.get("email_subject_template_b"):
            templates_to_check.append(("email_subject_template_b", str(params.get("email_subject_template_b", ""))))
        if params.get("email_body_template_b"):
            templates_to_check.append(("email_body_template_b", str(params.get("email_body_template_b", ""))))
        
        enable_conditionals = bool(params.get("enable_conditional_templates", False))
        enable_loops = bool(params.get("enable_template_loops", False))
        
        for template_name, template_content in templates_to_check:
            if not template_content:
                continue
            
            try:
                rendered = render_template_advanced(template_content, test_data, enable_conditionals, enable_loops)
                
                # Check for unrendered placeholders
                if "{{" in rendered:
                    validation_errors.append({
                        "template": template_name,
                        "error": "Unrendered placeholder found",
                        "remaining": [m.group() for m in re.finditer(r"\{\{[^}]+\}\}", rendered)],
                    })
                
                # Check for common issues
                if len(rendered.strip()) == 0:
                    validation_errors.append({
                        "template": template_name,
                        "error": "Template renders to empty string",
                    })
                    
            except Exception as e:
                validation_errors.append({
                    "template": template_name,
                    "error": f"Rendering failed: {str(e)[:200]}",
                })
        
        # Check industry templates
        try:
            industry_json = str(params.get("industry_templates_json", "{}"))
            industry_templates = json.loads(industry_json)
            for industry, tmpls in industry_templates.items():
                for key in ["subject", "body", "subject2", "body2"]:
                    if key in tmpls:
                        try:
                            rendered = render_template_advanced(str(tmpls[key]), test_data, enable_conditionals, enable_loops)
                            if "{{" in rendered:
                                validation_errors.append({
                                    "template": f"industry_templates.{industry}.{key}",
                                    "error": "Unrendered placeholder found",
                                })
                        except Exception as e:
                            validation_errors.append({
                                "template": f"industry_templates.{industry}.{key}",
                                "error": str(e)[:200],
                            })
        except Exception:
            pass
        
        result = {
            "enabled": True,
            "validated_templates": len(templates_to_check),
            "errors": validation_errors,
            "valid": len(validation_errors) == 0,
        }
        
        if validation_errors:
            logger.warning(f"Template validation found {len(validation_errors)} errors")
            for err in validation_errors[:5]:  # Log first 5
                logger.warning(f"  {err['template']}: {err['error']}")
        else:
            logger.info("All templates validated successfully")
        
        return result
    
    @task(task_id="segment_leads")
    def segment_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add segmentation metadata to leads."""
        ctx = get_current_context()
        params = ctx["params"]
        
        segment_by_size = bool(params.get("segment_by_company_size", False))
        segment_by_location = bool(params.get("segment_by_location", False))
        
        if not segment_by_size and not segment_by_location:
            return leads
        
        for lead in leads:
            # Company size segmentation
            if segment_by_size:
                company_size = lead.get("company_size", "")
                if company_size:
                    size_lower = str(company_size).lower()
                    if "enterprise" in size_lower or "large" in size_lower or "500+" in size_lower:
                        lead["segment_size"] = "enterprise"
                    elif "medium" in size_lower or "mid" in size_lower or "50-500" in size_lower:
                        lead["segment_size"] = "medium"
                    elif "small" in size_lower or "startup" in size_lower or "<50" in size_lower:
                        lead["segment_size"] = "small"
                    else:
                        lead["segment_size"] = "unknown"
                else:
                    # Try to infer from company name or other fields
                    company = lead.get("company", "").lower()
                    if any(word in company for word in ["inc", "corp", "llc", "ltd"]):
                        lead["segment_size"] = "medium"  # Default assumption
                    else:
                        lead["segment_size"] = "unknown"
            
            # Location segmentation
            if segment_by_location:
                location = lead.get("location", "")
                country = lead.get("country", "")
                
                # Extract country if location contains it
                if not country and location:
                    location_lower = str(location).lower()
                    # Simple country detection (could be improved)
                    country_codes = {"us": "US", "usa": "US", "united states": "US",
                                   "uk": "UK", "united kingdom": "UK",
                                   "ca": "CA", "canada": "CA",
                                   "au": "AU", "australia": "AU",
                                   "de": "DE", "germany": "DE",
                                   "fr": "FR", "france": "FR",
                                   "es": "ES", "spain": "ES",
                                   "mx": "MX", "mexico": "MX"}
                    for key, code in country_codes.items():
                        if key in location_lower:
                            country = code
                            break
                
                lead["segment_country"] = country or "unknown"
                lead["segment_location"] = location or "unknown"
                
                # Regional segmentation (basic)
                if country in ["US", "CA", "MX"]:
                    lead["segment_region"] = "north_america"
                elif country in ["UK", "DE", "FR", "ES", "IT", "NL"]:
                    lead["segment_region"] = "europe"
                elif country in ["AU", "NZ"]:
                    lead["segment_region"] = "oceania"
                else:
                    lead["segment_region"] = "other"
        
        return leads
    
    @task(task_id="cleanup_old_files")
    def cleanup_old_files() -> Dict[str, Any]:
        """Clean up old result files based on retention policy."""
        ctx = get_current_context()
        params = ctx["params"]
        
        cleanup_days = int(params.get("cleanup_old_files_days", 0))
        if cleanup_days <= 0:
            return {"enabled": False}
        
        results_dir = str(params.get("results_dir", "/tmp/outreach_results"))
        if not os.path.exists(results_dir):
            return {"enabled": True, "cleaned": 0, "reason": "dir_not_exists"}
        
        cutoff_time = time.time() - (cleanup_days * 24 * 60 * 60)
        cleaned_count = 0
        total_size_freed = 0
        
        try:
            for filename in os.listdir(results_dir):
                filepath = os.path.join(results_dir, filename)
                
                if not os.path.isfile(filepath):
                    continue
                
                # Skip active files
                if filename in ["events.jsonl", "summary.jsonl", "dlq.jsonl", "unsubscribed.csv"]:
                    continue
                
                file_mtime = os.path.getmtime(filepath)
                
                if file_mtime < cutoff_time:
                    try:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        cleaned_count += 1
                        total_size_freed += file_size
                    except Exception:
                        pass
            
            # Also truncate large append-only files
            for filename in ["events.jsonl", "summary.jsonl", "dlq.jsonl"]:
                filepath = os.path.join(results_dir, filename)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        try:
                            # Read last 100k lines
                            with open(filepath, "r") as f:
                                lines = f.readlines()
                            if len(lines) > 100000:
                                lines_to_keep = lines[-100000:]
                                with open(filepath, "w") as f:
                                    f.writelines(lines_to_keep)
                                logger.info(f"Truncated {filename} to last 100k lines")
                        except Exception as e:
                            logger.warning(f"Failed to truncate {filename}: {e}")
            
            result = {
                "enabled": True,
                "cleaned": cleaned_count,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            }
            
            logger.info(f"Cleanup: removed {cleaned_count} files, freed {result['size_freed_mb']} MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"enabled": True, "error": str(e)[:200]}
    
    @task(task_id="analyze_time_windows")
    def analyze_time_windows(summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimal time windows for sending emails."""
        ctx = get_current_context()
        params = ctx["params"]
        
        time_window_hours = int(params.get("time_window_analysis_hours", 0))
        if time_window_hours <= 0:
            return {"enabled": False}
        
        results_dir = str(params.get("results_dir", "/tmp/outreach_results"))
        events_path = os.path.join(results_dir, "events.jsonl")
        
        if not os.path.exists(events_path):
            return {"enabled": True, "reason": "no_events_file"}
        
        try:
            # Analyze events by hour
            hourly_stats = defaultdict(lambda: {"sent": 0, "opened": 0, "replied": 0})
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            with open(events_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        event_time_str = event.get("ts", "")
                        if not event_time_str:
                            continue
                        
                        event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                        if event_time < cutoff_time:
                            continue
                        
                        hour = event_time.hour
                        step = event.get("step", "")
                        
                        if step in ["email_1", "email_2"]:
                            hourly_stats[hour]["sent"] += 1
                            # Note: opened/replied would need to be tracked separately
                            # For now, we'll use engagement_checked data if available
                            
                    except Exception:
                        continue
            
            # Calculate rates per hour
            hourly_rates = []
            for hour in range(24):
                stats = hourly_stats[hour]
                if stats["sent"] > 0:
                    hourly_rates.append({
                        "hour": hour,
                        "sent": stats["sent"],
                        "open_rate": (stats["opened"] / stats["sent"] * 100) if stats["opened"] > 0 else 0,
                        "reply_rate": (stats["replied"] / stats["sent"] * 100) if stats["replied"] > 0 else 0,
                    })
            
            # Find best hours
            if hourly_rates:
                hourly_rates.sort(key=lambda x: x.get("reply_rate", 0), reverse=True)
                best_hours = hourly_rates[:3]
                
                analysis = {
                    "enabled": True,
                    "window_hours": time_window_hours,
                    "best_hours": best_hours,
                    "hourly_stats": hourly_stats,
                    "recommendation": f"Best hours for sending: {', '.join(str(h['hour']) for h in best_hours)} UTC",
                }
                
                logger.info(analysis["recommendation"])
                return analysis
            
            return {"enabled": True, "reason": "insufficient_data"}
            
        except Exception as e:
            logger.error(f"Time window analysis failed: {e}")
            return {"enabled": True, "error": str(e)[:200]}
    
    @task(task_id="health_check_webhooks")
    def health_check_webhooks() -> Dict[str, Any]:
        """Pre-flight health check of all webhooks."""
        ctx = get_current_context()
        params = ctx["params"]
        
        healthcheck_enabled = bool(params.get("webhook_healthcheck_enabled", False))
        if not healthcheck_enabled:
            return {"enabled": False}
        
        health_timeout = int(params.get("webhook_healthcheck_timeout", 5))
        results = {}
        
        # Check email webhook
        email_url = str(params.get("email_webhook_url", "")).strip()
        if email_url:
            results["email_webhook"] = check_webhook_health(email_url, health_timeout)
        
        # Check LinkedIn webhook
        linkedin_url = str(params.get("linkedin_webhook_url", "")).strip()
        if linkedin_url:
            results["linkedin_webhook"] = check_webhook_health(linkedin_url, health_timeout)
        
        # Check engagement API
        engagement_url = str(params.get("engagement_check_url", "")).strip()
        if engagement_url:
            results["engagement_api"] = check_webhook_health(engagement_url, health_timeout)
        
        all_healthy = all(r.get("healthy", False) for r in results.values())
        
        if not all_healthy:
            unhealthy = {k: v for k, v in results.items() if not v.get("healthy", False)}
            logger.warning(f"Health check failed for: {list(unhealthy.keys())}")
            for service, health in unhealthy.items():
                logger.warning(f"  {service}: {health.get('error', 'unknown error')}")
        
        return {
            "enabled": True,
            "all_healthy": all_healthy,
            "results": results,
        }
    
    # Task flow
    # Pre-flight validation and health checks
    template_validation = validate_templates()
    webhook_health = health_check_webhooks()
    
    # Load and process leads
    leads = load_leads()
    enriched_leads = enrich_leads(leads)
    scored_leads = score_leads(enriched_leads)
    segmented_leads = segment_leads(scored_leads)
    holiday_filtered = check_holidays(segmented_leads)
    warmup_filtered = check_warmup(holiday_filtered)
    
    # Parallel email sending
    email_results = send_initial_email.expand(lead=warmup_filtered)
    
    # Check engagement (in parallel)
    engagement_checked = check_engagement.expand(lead=warmup_filtered)
    
    # LinkedIn (conditional)
    linkedin_results = send_linkedin.expand(lead=engagement_checked)
    
    # Follow-up (conditional)
    followup_results = enqueue_followup.expand(lead=engagement_checked)
    
    # Summarize
    summary = summarize(email_results, linkedin_results, followup_results)
    
    # Predictive analytics (uses summary)
    analytics = predictive_analytics(summary)
    
    # Time window analysis
    time_analysis = analyze_time_windows(summary)
    
    # CRM sync (uses email_results and summary)
    crm_sync = sync_to_crm(summary, email_results)
    
    # Cleanup old files (run at end)
    cleanup = cleanup_old_files()


dag = outreach_multichannel()

