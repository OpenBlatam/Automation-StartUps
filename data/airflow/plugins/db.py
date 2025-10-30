import os
import psycopg


def get_conn():
	dsn = os.environ.get("KPIS_PG_DSN")
	if not dsn:
		raise RuntimeError("KPIS_PG_DSN not set")
	return psycopg.connect(dsn)
