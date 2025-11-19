from datetime import datetime, timedelta
import os
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from plugins.db import get_conn

HUBSPOT_TOKEN = os.environ.get("HUBSPOT_TOKEN", "")

FIELDS = ["email","firstname","lastname","phone","utm_source","utm_campaign","lifecyclestage"]


def fetch_contacts(**context):
	offset = None
	all_contacts = []
	headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
	while True:
		payload = {"limit": 100, "properties": FIELDS}
		if offset:
			payload["after"] = offset
		r = requests.post("https://api.hubapi.com/crm/v3/objects/contacts/search", headers=headers, json=payload, timeout=30)
		r.raise_for_status()
		out = r.json()
		all_contacts.extend(out.get("results", []))
		offset = out.get("paging", {}).get("next", {}).get("after")
		if not offset:
			break
	context['ti'].xcom_push(key="contacts", value=all_contacts)


def upsert(**context):
	contacts = context['ti'].xcom_pull(key="contacts") or []
	with get_conn() as conn:
		with conn.cursor() as cur:
			for c in contacts:
				props = c.get("properties", {})
				email = props.get("email")
				if not email:
					continue
				cur.execute(
					"""
					INSERT INTO leads (ext_id, source, first_name, last_name, email, phone, score, priority, utm_source, utm_campaign, created_at, updated_at)
					VALUES (%s,'hubspot',%s,%s,%s,%s,COALESCE(score,0),'',%s,%s,NOW(),NOW())
					ON CONFLICT (ext_id) DO UPDATE SET
						first_name=EXCLUDED.first_name,
						last_name=EXCLUDED.last_name,
						email=EXCLUDED.email,
						phone=EXCLUDED.phone,
						utm_source=EXCLUDED.utm_source,
						utm_campaign=EXCLUDED.utm_campaign,
						updated_at=NOW()
					""",
					(
						c.get("id"),
						props.get("firstname"),
						props.get("lastname"),
						email,
						props.get("phone"),
						props.get("utm_source"),
						props.get("utm_campaign"),
					),
				)
			conn.commit()


default_args = {"owner": "data-eng", "retries": 1, "retry_delay": timedelta(minutes=10)}

with DAG(
	"leads_sync_hubspot",
	start_date=datetime(2024, 1, 1),
	schedule_interval="@daily",
	catchup=False,
	default_args=default_args,
) as dag:

	fetch = PythonOperator(task_id="fetch_contacts", python_callable=fetch_contacts)
	up = PythonOperator(task_id="upsert", python_callable=upsert)

	fetch >> up
