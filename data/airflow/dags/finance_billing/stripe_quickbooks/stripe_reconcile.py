from datetime import datetime, timedelta
import os
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from plugins.db import get_conn

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")


def fetch_stripe_charges(**context):
	s = requests.Session()
	s.headers.update({"Authorization": f"Bearer {STRIPE_API_KEY}"})
	params = {
		"limit": 100,
		"created[gte]": int((datetime.utcnow() - timedelta(days=1)).timestamp()),
	}
	all_data = []
	starting_after = None
	while True:
		p = dict(params)
		if starting_after:
			p["starting_after"] = starting_after
		r = s.get("https://api.stripe.com/v1/charges", params=p, timeout=30)
		r.raise_for_status()
		out = r.json()
		data = out.get("data", [])
		all_data.extend(data)
		if out.get("has_more") and data:
			starting_after = data[-1].get("id")
		else:
			break
	context['ti'].xcom_push(key="charges", value=all_data)


def reconcile(**context):
	charges = context['ti'].xcom_pull(key="charges") or []
	missing = []
	with get_conn() as conn:
		with conn.cursor() as cur:
			for c in charges:
				pid = c.get("id")
				amount = (c.get("amount") or 0) / 100.0
				cur.execute("SELECT 1 FROM payments WHERE payment_id = %s", (pid,))
				if not cur.fetchone():
					missing.append({"payment_id": pid, "amount": amount, "currency": c.get("currency", "").upper()})
	context['ti'].xcom_push(key="missing", value=missing)


def report(**context):
	missing = context['ti'].xcom_pull(key="missing") or []
	print(f"Missing payments: {len(missing)}")
	for m in missing[:20]:
		print(m)


default_args = {"owner": "data-eng", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
	"stripe_reconcile",
	start_date=datetime(2024, 1, 1),
	schedule_interval="@hourly",
	catchup=False,
	default_args=default_args,
) as dag:

	fetch = PythonOperator(task_id="fetch_stripe_charges", python_callable=fetch_stripe_charges)
	rec = PythonOperator(task_id="reconcile", python_callable=reconcile)
	rep = PythonOperator(task_id="report", python_callable=report)

	fetch >> rec >> rep
