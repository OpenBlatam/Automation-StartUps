from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from plugins.db import get_conn

SQL_REFRESH = [
	"REFRESH MATERIALIZED VIEW CONCURRENTLY mv_revenue_24h_hourly;",
	"REFRESH MATERIALIZED VIEW CONCURRENTLY mv_revenue_7d_daily;",
]


def refresh(**context):
	with get_conn() as conn:
		with conn.cursor() as cur:
			for stmt in SQL_REFRESH:
				cur.execute(stmt)
			conn.commit()


default_args = {"owner": "data-eng", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
	"refresh_kpi_materialized",
	start_date=datetime(2024, 1, 1),
	schedule_interval="*/15 * * * *",
	catchup=False,
	default_args=default_args,
) as dag:

	refresh_task = PythonOperator(task_id="refresh", python_callable=refresh)
