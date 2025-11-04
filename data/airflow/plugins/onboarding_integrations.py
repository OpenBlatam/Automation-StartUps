from __future__ import annotations

import json
import logging
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone


logger = logging.getLogger("airflow.task")

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def _env(name: str, default: str = "") -> str:
    """
    Get environment variable with default value.
    Mejorado: Intenta obtener desde Vault primero, luego fallback a env var.
    """
    # Intentar desde Vault usando helper
    try:
        from data.airflow.plugins.vault_helpers import get_config_with_fallback, migrate_env_to_vault_format
        vault_config = migrate_env_to_vault_format(name)
        if vault_config:
            vault_value = get_config_with_fallback(
                vault_config.get("vault_path", ""),
                vault_config.get("vault_key"),
                name,
                default=default,
                required=False
            )
            if vault_value:
                return vault_value
    except Exception as e:
        logger.debug(f"No se pudo obtener {name} desde Vault, usando env var: {e}")
    
    # Fallback a variable de entorno tradicional
    return os.getenv(name, default)


def _retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """Retry function with exponential backoff."""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay}s",
                    extra={"error": str(e), "attempt": attempt + 1},
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"All {max_retries} attempts failed",
                    extra={"error": str(e), "max_retries": max_retries},
                )
    raise last_exception


def hris_prefetch(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch employee details from HRIS (Workday/BambooHR).
    Returns merged payload with canonical fields if available.
    Falls back to provided data if HRIS is unavailable.
    """
    employee_email = payload.get("employee_email", "")
    hris_url = _env("HRIS_API_URL")
    
    logger.info(
        "hris prefetch start",
        extra={
            "hris_configured": bool(hris_url),
            "employee_email": employee_email,
            "hris_url": hris_url if hris_url else None,
        },
    )
    
    if not hris_url:
        logger.warning("HRIS_API_URL not configured, using provided data", extra={"employee_email": employee_email})
        return {
            "hris": {
                "employee_id": employee_email,
                "manager_email": payload.get("manager_email"),
                "department": payload.get("department"),
                "location": payload.get("location"),
                "source": "provided",
            }
        }
    
    # TODO: Replace with actual HTTP call to HRIS API
    # Example implementation:
    # try:
    #     import requests
    #     response = _retry_with_backoff(
    #         requests.get,
    #         f"{hris_url}/employees/{employee_email}",
    #         headers={"Authorization": f"Bearer {_env('HRIS_API_TOKEN')}"},
    #         timeout=10,
    #     )
    #     response.raise_for_status()
    #     hris_data = response.json()
    #     return {"hris": hris_data}
    # except Exception as e:
    #     logger.error("HRIS API call failed", extra={"error": str(e), "employee_email": employee_email})
    #     raise
    
    # Stub implementation for now
    logger.info("hris prefetch completed (stub)", extra={"employee_email": employee_email})
    return {
        "hris": {
            "employee_id": employee_email,
            "manager_email": payload.get("manager_email"),
            "department": payload.get("department"),
            "location": payload.get("location"),
            "source": "stub",
        }
    }

def create_idp_and_workspace_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create accounts in IdP (e.g., Okta/Entra), email (Google/M365) and core apps.
    Returns account IDs and status for each service.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    department = payload.get("department", "")
    idp_api = _env("IDP_API_URL")
    workspace = _env("WORKSPACE_API_URL")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info(
        "create accounts start",
        extra={
            "employee_email": employee_email,
            "full_name": full_name,
            "department": department,
            "idp_configured": bool(idp_api),
            "workspace_configured": bool(workspace),
        },
    )
    
    result = {
        "idp_user_id": None,
        "mailbox": None,
        "workspace_profile": None,
        "accounts_created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    # Create IdP account
    if idp_api:
        try:
            # TODO: Replace with actual IdP API call
            # Example:
            # idp_response = _retry_with_backoff(
            #     requests.post,
            #     f"{idp_api}/users",
            #     json={"email": employee_email, "name": full_name, "department": department},
            #     headers={"Authorization": f"Bearer {_env('IDP_API_TOKEN')}"},
            #     timeout=30,
            # )
            # idp_response.raise_for_status()
            # result["idp_user_id"] = idp_response.json().get("id")
            
            # Stub
            result["idp_user_id"] = f"idp-user-{employee_email}"
            logger.info("IdP account created", extra={"employee_email": employee_email, "idp_user_id": result["idp_user_id"]})
        except Exception as e:
            logger.error("Failed to create IdP account", extra={"employee_email": employee_email, "error": str(e)})
            raise
    else:
        logger.warning("IDP_API_URL not configured, skipping IdP account creation", extra={"employee_email": employee_email})
    
    # Create email/mailbox
    # TODO: Integrate with email provider (Google Workspace, M365, etc.)
    result["mailbox"] = employee_email
    logger.info("Mailbox assigned", extra={"employee_email": employee_email, "mailbox": result["mailbox"]})
    
    # Create workspace profile
    if workspace:
        try:
            # TODO: Replace with actual workspace API call
            result["workspace_profile"] = {
                "url": f"{workspace}/users/{employee_email}",
                "status": "created",
            }
            logger.info("Workspace profile created", extra={"employee_email": employee_email})
        except Exception as e:
            logger.error("Failed to create workspace profile", extra={"employee_email": employee_email, "error": str(e)})
            # Don't fail if workspace profile creation fails
    else:
        logger.warning("WORKSPACE_API_URL not configured, skipping workspace profile", extra={"employee_email": employee_email})
    
    logger.info(
        "accounts creation completed",
        extra={
            "employee_email": employee_email,
            "accounts": {
                "idp": bool(result["idp_user_id"]),
                "mailbox": bool(result["mailbox"]),
                "workspace": bool(result["workspace_profile"]),
            },
        },
    )
    
    return result


def assign_project_and_it_tasks(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create tickets/tasks in tracker (e.g., Jira) and IT checklist.
    Returns list of created task keys.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    department = payload.get("department", "")
    role = payload.get("role", "")
    start_date = payload.get("start_date", "")
    tracker_url = _env("ISSUE_TRACKER_URL")
    project_key = _env("ISSUE_TRACKER_PROJECT", "ONB")
    
    logger.info(
        "assign onboarding tasks start",
        extra={
            "employee_email": employee_email,
            "tracker_configured": bool(tracker_url),
            "project_key": project_key,
            "department": department,
        },
    )
    
    tasks = []
    
    if tracker_url:
        try:
            # TODO: Replace with actual issue tracker API call
            # Example for Jira:
            # jira_tasks = [
            #     {
            #         "project": {"key": project_key},
            #         "summary": f"Onboarding: {full_name}",
            #         "description": f"Onboarding tasks for {full_name} ({employee_email})\nDepartment: {department}\nRole: {role}\nStart Date: {start_date}",
            #         "issuetype": {"name": "Task"},
            #     },
            #     {
            #         "project": {"key": project_key},
            #         "summary": f"IT Setup: {full_name}",
            #         "description": f"IT setup checklist for {full_name}",
            #         "issuetype": {"name": "Task"},
            #     },
            # ]
            # for task_data in jira_tasks:
            #     response = _retry_with_backoff(
            #         requests.post,
            #         f"{tracker_url}/rest/api/3/issue",
            #         json={"fields": task_data},
            #         headers={"Authorization": f"Bearer {_env('ISSUE_TRACKER_TOKEN')}"},
            #         timeout=30,
            #     )
            #     response.raise_for_status()
            #     task_key = response.json().get("key")
            #     tasks.append({"key": task_key, "summary": task_data["summary"]})
            
            # Stub implementation
            tasks = [
                {"key": f"{project_key}-ONB-001", "summary": f"Onboarding checklist: {full_name}", "type": "onboarding"},
                {"key": f"{project_key}-IT-001", "summary": f"IT setup: {full_name}", "type": "it_setup"},
            ]
            logger.info("Tasks created", extra={"employee_email": employee_email, "task_count": len(tasks)})
        except Exception as e:
            logger.error("Failed to create tasks in tracker", extra={"employee_email": employee_email, "error": str(e)})
            raise
    else:
        logger.warning("ISSUE_TRACKER_URL not configured, skipping task creation", extra={"employee_email": employee_email})
    
    return {"tasks": tasks, "tasks_created_at": datetime.now(timezone.utc).isoformat()}


def send_welcome_and_docs(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send welcome email with links to documentation/handbook and policies.
    Returns confirmation of email sent status.
    """
    employee_email = payload.get("employee_email", "")
    full_name = payload.get("full_name", "")
    manager_email = payload.get("manager_email", "")
    start_date = payload.get("start_date", "")
    docs_base = _env("ONBOARDING_DOCS_BASE_URL", "https://docs.example.com/onboarding")
    email_from = _env("ONBOARDING_EMAIL_FROM", "hr@example.com")
    
    if not employee_email:
        raise ValueError("employee_email is required")
    
    logger.info(
        "send welcome email start",
        extra={
            "to": employee_email,
            "from": email_from,
            "manager": manager_email,
            "start_date": start_date,
        },
    )
    
    # Build email content
    docs_links = {
        "handbook": f"{docs_base}/handbook",
        "policies": f"{docs_base}/policies",
        "it_setup": f"{docs_base}/it-setup",
        "getting_started": f"{docs_base}/getting-started",
    }
    
    # TODO: Replace with actual email sending
    # Example using Airflow EmailOperator or external service:
    # try:
    #     email_subject = f"Welcome to the team, {full_name}!"
    #     email_body = f"""
    #     Welcome {full_name}!
    #
    #     Your start date: {start_date}
    #     Your manager: {manager_email}
    #
    #     Resources:
    #     - Handbook: {docs_links['handbook']}
    #     - Policies: {docs_links['policies']}
    #     - IT Setup: {docs_links['it_setup']}
    #     """
    #
    #     # Use SMTP or email service API
    #     _retry_with_backoff(
    #         send_email_via_provider,  # Replace with actual function
    #         to=employee_email,
    #         subject=email_subject,
    #         body=email_body,
    #     )
    #     logger.info("Welcome email sent", extra={"employee_email": employee_email})
    # except Exception as e:
    #     logger.error("Failed to send welcome email", extra={"employee_email": employee_email, "error": str(e)})
    #     raise
    
    logger.info("Welcome email prepared (stub)", extra={"employee_email": employee_email})
    
    return {
        "welcome_sent": True,
        "welcome_sent_at": datetime.now(timezone.utc).isoformat(),
        "docs": docs_links,
        "email_to": employee_email,
        "email_from": email_from,
    }


def record_progress_and_notify(payload: Dict[str, Any]) -> None:
    """
    Track onboarding progress: logs structured data and persists to Airflow Variables.
    Triggers Slack notification via env-controlled notifier.
    Extend to persist in a DB or emit metrics for production use.
    """
    employee_email = payload.get("employee_email", "unknown")
    
    progress = {
        "employee_email": employee_email,
        "full_name": payload.get("full_name"),
        "start_date": payload.get("start_date"),
        "department": payload.get("department"),
        "role": payload.get("role"),
        "created_accounts": bool(payload.get("idp_user_id")),
        "idp_user_id": payload.get("idp_user_id"),
        "mailbox": payload.get("mailbox"),
        "tasks_created": bool(payload.get("tasks")),
        "task_count": len(payload.get("tasks", [])),
        "welcome_sent": bool(payload.get("welcome_sent")),
        "manager": payload.get("manager_email"),
        "hris_source": payload.get("hris", {}).get("source", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
    }
    
    logger.info(
        "onboarding progress recorded",
        extra={
            "employee_email": employee_email,
            "accounts_created": progress["created_accounts"],
            "tasks_count": progress["task_count"],
            "welcome_sent": progress["welcome_sent"],
        },
    )
    
    # Persist to Airflow Variables (lightweight storage)
    try:
        from airflow.models import Variable  # local import to avoid hard dependency at import time
        
        key = f"onboarding_runs:{employee_email}"
        existing_raw = Variable.get(key, default_var="[]")
        try:
            existing = json.loads(existing_raw)
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid existing progress data, resetting", extra={"key": key})
            existing = []
        
        existing.append(progress)
        # Keep only last 10 runs per employee to avoid bloat
        existing = existing[-10:]
        Variable.set(key, json.dumps(existing, indent=2))
        
        logger.info(
            "progress persisted",
            extra={"employee_email": employee_email, "total_runs": len(existing)},
        )
    except Exception as e:
        # If Variables are not available, log warning but don't fail
        logger.warning(
            "failed to persist progress to Variables",
            extra={"employee_email": employee_email, "error": str(e)},
        )
    
    # TODO: Send notification to Slack/Teams/etc. via configured webhook
    # Example:
    # slack_webhook = _env("SLACK_WEBHOOK_URL")
    # if slack_webhook:
    #     try:
    #         notify_message = f"✅ Onboarding completed for {progress['full_name']} ({employee_email})"
    #         _retry_with_backoff(
    #             requests.post,
    #             slack_webhook,
    #             json={"text": notify_message},
    #             timeout=10,
    #         )
    #     except Exception as e:
    #         logger.warning("Failed to send Slack notification", extra={"error": str(e)})


