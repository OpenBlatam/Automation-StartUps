from __future__ import annotations

import os
import logging
from typing import Optional, Sequence, List
from urllib import request

try:
	from airflow.utils.email import send_email
except Exception:  # pragma: no cover
	send_email = None  # type: ignore


def _is_enabled(flag_env: str, default: bool = True) -> bool:
	val = os.getenv(flag_env)
	if val is None:
		return default
	val_lower = val.strip().lower()
	return val_lower in {"1", "true", "yes", "y", "on"}


def notify_slack(text: str, webhook_env: str = "SLACK_WEBHOOK_URL", timeout_s: int = 5) -> None:
	if not _is_enabled("ENABLE_SLACK", default=True):
		return
	webhook = os.getenv(webhook_env)
	if not webhook:
		return
	try:
		payload = ("{" + f"\"text\": \"{text}\"" + "}").encode("utf-8")
		req = request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
		request.urlopen(req, timeout=timeout_s).read()
	except Exception:
		# best-effort; do not raise
		logging.getLogger("airflow.task").debug("slack notification failed", exc_info=True)


def _parse_default_recipients() -> Optional[List[str]]:
	emails = os.getenv("ALERT_EMAILS")
	if not emails:
		return None
	recips = [addr.strip() for addr in emails.split(",") if addr.strip()]
	return recips or None


def notify_email(subject: str, html_content: str, to: Optional[Sequence[str]] = None) -> None:
	if not _is_enabled("ENABLE_EMAIL", default=False):
		return
	if to is None:
		to = _parse_default_recipients()
	if send_email is None or not to:
		return
	try:
		send_email(to=to, subject=subject, html_content=html_content)
	except Exception:
		logging.getLogger("airflow.task").debug("email notification failed", exc_info=True)
