from __future__ import annotations

import json
import logging
import os
from typing import Dict, Any


logger = logging.getLogger("airflow.task")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def create_idp_and_workspace_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub: create accounts in IdP (e.g., Okta/Entra), email (Google/M365) and core apps.
    Replace with real API calls (HTTP hooks/providers) and proper error handling.
    """
    employee_email = payload["employee_email"]
    full_name = payload.get("full_name", "")
    idp_api = _env("IDP_API_URL")
    workspace = _env("WORKSPACE_API_URL")
    logger.info(
        "create accounts",
        extra={
            "employee_email": employee_email,
            "full_name": full_name,
            "idp_api": bool(idp_api),
            "workspace_api": bool(workspace),
        },
    )
    # TODO: implement providers (airflow.providers.http or vendor-specific providers)
    return {
        "idp_user_id": f"user::{employee_email}",
        "mailbox": f"{employee_email}",
        "workspace_profile": {"url": f"{workspace}/users/{employee_email}" if workspace else ""},
    }


def assign_project_and_it_tasks(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub: create tickets/tasks in tracker (e.g., Jira) and IT checklist.
    """
    jira_url = _env("ISSUE_TRACKER_URL")
    project_key = _env("ISSUE_TRACKER_PROJECT", "ONB")
    logger.info(
        "assign onboarding tasks",
        extra={"jira": bool(jira_url), "project": project_key, "employee_email": payload.get("employee_email")},
    )
    # TODO: use airflow.providers.jira if available
    return {
        "tasks": [
            {"key": f"{project_key}-TEMP", "summary": "Onboarding checklist"},
        ]
    }


def send_welcome_and_docs(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub: send welcome email with links to documentation/handbook and policies.
    """
    docs_base = _env("ONBOARDING_DOCS_BASE_URL", "https://docs.example.com/onboarding")
    email_from = _env("ONBOARDING_EMAIL_FROM", "hr@example.com")
    logger.info(
        "send welcome/docs",
        extra={
            "to": payload.get("employee_email"),
            "from": email_from,
            "docs": docs_base,
        },
    )
    # TODO: wire airflow email operator or external provider
    return {
        "welcome_sent": True,
        "docs": {
            "handbook": f"{docs_base}/handbook",
            "policies": f"{docs_base}/policies",
            "it_setup": f"{docs_base}/it-setup",
        },
    }


def record_progress_and_notify(payload: Dict[str, Any]) -> None:
    """
    Minimal progress tracking: logs a structured line and triggers Slack via env-controlled notifier.
    Extend to persist in a DB or emit metrics.
    """
    progress = {
        "employee_email": payload.get("employee_email"),
        "created_accounts": bool(payload.get("idp_user_id")),
        "tasks_created": bool(payload.get("tasks")),
        "welcome_sent": bool(payload.get("welcome_sent")),
        "manager": payload.get("manager_email"),
    }
    logger.info("onboarding progress", extra={"progress": json.dumps(progress)})


