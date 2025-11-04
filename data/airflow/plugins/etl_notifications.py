from __future__ import annotations

import logging
import os
import json
from typing import Dict, Any, Optional
from urllib.parse import quote

_logger = logging.getLogger(__name__)


def notify_slack(
	message: str,
	extra_context: Optional[Dict[str, Any]] = None,
	webhook_url: Optional[str] = None,
	channel: Optional[str] = None,
	username: str = "Airflow",
	icon_emoji: str = ":robot_face:",
) -> None:
	"""
	Send notification to Slack via webhook.
	
	Args:
		message: Message text to send
		extra_context: Optional dictionary with additional context fields
		webhook_url: Slack webhook URL (defaults to SLACK_WEBHOOK_URL env var)
		channel: Optional channel override (use webhook default if not provided)
		username: Bot username (default: "Airflow")
		icon_emoji: Bot icon emoji (default: ":robot_face:")
		
	Example:
		notify_slack("ETL completed", extra_context={"rows": 1000, "duration_ms": 5000})
	"""
	if not webhook_url:
		webhook_url = os.getenv("SLACK_WEBHOOK_URL")
	
	if not webhook_url:
		_logger.debug("Slack webhook URL not configured, skipping notification")
		return
	
	try:
		import requests
		
		# Build payload
		payload: Dict[str, Any] = {
			"text": message,
			"username": username,
			"icon_emoji": icon_emoji,
		}
		
		# Add context as attachments if provided
		if extra_context:
			fields = []
			for key, value in extra_context.items():
				# Sanitize values to avoid exposing secrets
				if any(secret in key.lower() for secret in ["password", "secret", "token", "key", "api_key"]):
					value = "***REDACTED***"
				fields.append({
					"title": key,
					"value": str(value),
					"short": len(str(value)) < 50,
				})
			
			payload["attachments"] = [{
				"color": "good",
				"fields": fields,
			}]
		
		# Add channel override if provided
		if channel:
			payload["channel"] = channel
		
		# Send request
		response = requests.post(
			webhook_url,
			json=payload,
			timeout=10,
			headers={"Content-Type": "application/json"},
		)
		response.raise_for_status()
		
		_logger.debug("Slack notification sent successfully")
		
	except ImportError:
		_logger.warning("requests library not available, skipping Slack notification")
	except Exception as e:
		_logger.warning("Failed to send Slack notification: %s", e, exc_info=True)


def notify_email(
	to: str | list[str],
	subject: str,
	body: str,
	html: Optional[str] = None,
	smtp_host: Optional[str] = None,
	smtp_port: int = 587,
	smtp_user: Optional[str] = None,
	smtp_password: Optional[str] = None,
) -> None:
	"""
	Send email notification via SMTP.
	
	Args:
		to: Recipient email address(es)
		subject: Email subject
		body: Plain text email body
		html: Optional HTML email body
		smtp_host: SMTP host (defaults to SMTP_HOST env var)
		smtp_port: SMTP port (defaults to 587)
		smtp_user: SMTP username (defaults to SMTP_USER env var)
		smtp_password: SMTP password (defaults to SMTP_PASSWORD env var)
	"""
	if not smtp_host:
		smtp_host = os.getenv("SMTP_HOST")
	
	if not smtp_host:
		_logger.debug("SMTP host not configured, skipping email notification")
		return
	
	try:
		from email.mime.text import MIMEText
		from email.mime.multipart import MIMEMultipart
		import smtplib
		
		msg = MIMEMultipart("alternative")
		msg["Subject"] = subject
		msg["From"] = smtp_user or os.getenv("SMTP_USER", "airflow@example.com")
		
		if isinstance(to, str):
			msg["To"] = to
			to_list = [to]
		else:
			msg["To"] = ", ".join(to)
			to_list = to
		
		# Add plain text part
		part_text = MIMEText(body, "plain")
		msg.attach(part_text)
		
		# Add HTML part if provided
		if html:
			part_html = MIMEText(html, "html")
			msg.attach(part_html)
		
		# Connect and send
		password = smtp_password or os.getenv("SMTP_PASSWORD")
		server = smtplib.SMTP(smtp_host, smtp_port)
		server.starttls()
		if password:
			server.login(smtp_user or "", password)
		server.sendmail(msg["From"], to_list, msg.as_string())
		server.quit()
		
		_logger.debug("Email notification sent successfully")
		
	except ImportError:
		_logger.warning("Email libraries not available, skipping email notification")
	except Exception as e:
		_logger.warning("Failed to send email notification: %s", e, exc_info=True)


def notify_pagerduty(
	summary: str,
	severity: str = "error",
	routing_key: Optional[str] = None,
	source: str = "airflow",
	extra_context: Optional[Dict[str, Any]] = None,
) -> None:
	"""
	Send alert to PagerDuty via Events API v2.
	
	Args:
		summary: Alert summary text
		severity: Severity level (critical, error, warning, info)
		routing_key: PagerDuty routing key (defaults to PAGERDUTY_ROUTING_KEY env var)
		source: Alert source identifier
		extra_context: Optional dictionary with additional context
	"""
	if not routing_key:
		routing_key = os.getenv("PAGERDUTY_ROUTING_KEY")
	
	if not routing_key:
		_logger.debug("PagerDuty routing key not configured, skipping notification")
		return
	
	try:
		import requests
		
		payload = {
			"routing_key": routing_key,
			"event_action": "trigger",
			"payload": {
				"summary": summary,
				"severity": severity,
				"source": source,
				"custom_details": extra_context or {},
			},
		}
		
		response = requests.post(
			"https://events.pagerduty.com/v2/enqueue",
			json=payload,
			timeout=10,
			headers={"Content-Type": "application/json"},
		)
		response.raise_for_status()
		
		_logger.debug("PagerDuty alert sent successfully")
		
	except ImportError:
		_logger.warning("requests library not available, skipping PagerDuty notification")
	except Exception as e:
		_logger.warning("Failed to send PagerDuty alert: %s", e, exc_info=True)
