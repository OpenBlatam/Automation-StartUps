from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from plugins.db import get_conn

SQL_INIT = """
CREATE TABLE IF NOT EXISTS kpi_daily (
	day date PRIMARY KEY,
	revenue numeric(14,2) NOT NULL,
	payments_count int NOT NULL,
	leads_count int NOT NULL,
	conversion_pct numeric(5,2) NOT NULL,
	updated_at timestamp
);
"""

SQL_UPSERT = """
WITH r AS (
	SELECT date_trunc('day', created_at)::date AS day,
		SUM(amount) AS revenue,
		COUNT(*) AS payments_count
	FROM payments
	WHERE created_at >= NOW() - interval '35 days'
	GROUP BY 1
), l AS (
	SELECT date_trunc('day', created_at)::date AS day,
		COUNT(*) AS leads_count
	FROM leads
	WHERE created_at >= NOW() - interval '35 days'
	GROUP BY 1
), joined AS (
	SELECT COALESCE(r.day,l.day) AS day,
		COALESCE(r.revenue,0) AS revenue,
		COALESCE(r.payments_count,0) AS payments_count,
		COALESCE(l.leads_count,0) AS leads_count,
		CASE WHEN COALESCE(l.leads_count,0)=0 THEN 0
			ELSE ROUND(COALESCE(r.payments_count,0)::numeric / NULLIF(l.leads_count,0) * 100, 2)
		END AS conversion_pct
	FROM r FULL OUTER JOIN l ON r.day = l.day
)
INSERT INTO kpi_daily(day, revenue, payments_count, leads_count, conversion_pct, updated_at)
SELECT day, revenue, payments_count, leads_count, conversion_pct, NOW()
FROM joined
ON CONFLICT (day) DO UPDATE SET
	revenue = EXCLUDED.revenue,
	payments_count = EXCLUDED.payments_count,
	leads_count = EXCLUDED.leads_count,
	conversion_pct = EXCLUDED.conversion_pct,
	updated_at = NOW();
"""


def run_agg(**context):
	with get_conn() as conn:
		with conn.cursor() as cur:
			cur.execute(SQL_INIT)
			cur.execute(SQL_UPSERT)
			conn.commit()


default_args = {"owner": "data-eng", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
	"kpi_aggregate_daily",
	start_date=datetime(2024, 1, 1),
	schedule_interval="@daily",
	catchup=False,
	default_args=default_args,
) as dag:

	aggregate = PythonOperator(task_id="aggregate", python_callable=run_agg)
