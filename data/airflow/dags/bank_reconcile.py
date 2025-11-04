from __future__ import annotations

from datetime import timedelta, date
import logging
from typing import Any, Dict, List
from pathlib import Path

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
from data.airflow.plugins.db import get_conn


def _get_env_var(name: str, default: str | None = None) -> str:
	return str(Variable.get(name, default_var=default))


@dag(
	dag_id="bank_reconcile",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 10 * * *",  # daily at 10:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Reconcile Stripe payouts with bank statements",
	tags=["finance", "reconciliation"],
)
def bank_reconcile() -> None:
	logger = logging.getLogger("airflow.task")

	@task(task_id="fetch_stripe_payouts")
	def fetch_stripe_payouts() -> Dict[str, Any]:
		import os
		import requests  # type: ignore
		stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
		payouts: List[Dict[str, Any]] = []
		if stripe_key:
			try:
				s = requests.Session()
				s.headers.update({"Authorization": f"Bearer {stripe_key}"})
				params = {"limit": 100}
				starting_after = None
				while True:
					p = dict(params)
					if starting_after:
						p["starting_after"] = starting_after
					r = s.get("https://api.stripe.com/v1/payouts", params=p, timeout=30)
					r.raise_for_status()
					out = r.json()
					data = out.get("data", [])
					for p in data:
						if p.get("status") == "paid":
							payouts.append({
								"id": p.get("id"),
								"amount": (p.get("amount") or 0) / 100.0,
								"currency": (p.get("currency") or "").upper(),
								"arrival_date": p.get("arrival_date"),
								"description": p.get("description") or "",
							})
					if out.get("has_more") and data:
						starting_after = data[-1].get("id")
					else:
						break
			except Exception:
				logger.warning("stripe payouts fetch failed", exc_info=True)
		logger.info("fetched stripe payouts", extra={"count": len(payouts)})
		return {"stripe_payouts": payouts}

	@task(task_id="load_bank_statements")
	def load_bank_statements() -> Dict[str, Any]:
		statements_path = _get_env_var("BANK_STATEMENTS_PATH", default="/tmp/bank_statements")
		statements: List[Dict[str, Any]] = []
		try:
			path = Path(statements_path)
			if path.is_file():
				# Simple CSV parser: date,amount,description,reference
				for line in path.read_text(encoding="utf-8").splitlines():
					line = line.strip()
					if not line or line.startswith("#"):
						continue
					parts = line.split(",")
					if len(parts) >= 3:
						try:
							statements.append({
								"date": parts[0].strip(),
								"amount": float(parts[1].strip()),
								"description": parts[2].strip(),
								"reference": parts[3].strip() if len(parts) > 3 else "",
							})
						except (ValueError, IndexError):
							continue
		except Exception:
			logger.warning("bank statements load failed", exc_info=True)
		logger.info("loaded bank statements", extra={"count": len(statements)})
		return {"bank_statements": statements}

	@task(task_id="match_transactions")
	def match_transactions(payouts_payload: Dict[str, Any], statements_payload: Dict[str, Any]) -> Dict[str, Any]:
		payouts = payouts_payload.get("stripe_payouts", []) or []
		statements = statements_payload.get("bank_statements", []) or []
		matched: List[Dict[str, Any]] = []
		unmatched_payouts: List[Dict[str, Any]] = []
		unmatched_statements: List[Dict[str, Any]] = []
		tolerance = float(_get_env_var("RECONCILE_AMOUNT_TOLERANCE", default="0.01"))
		max_date_diff_days = int(_get_env_var("RECONCILE_MAX_DATE_DIFF_DAYS", default="7"))
		used_statements = set()
		for po in payouts:
			found = False
			po_amount = float(po.get("amount", 0.0))
			po_date = po.get("arrival_date")
			po_id = po.get("id", "")
			# Try exact match first
			for idx, st in enumerate(statements):
				if idx in used_statements:
					continue
				st_amount = abs(float(st.get("amount", 0.0)))
				if abs(po_amount - st_amount) <= tolerance:
					st_date = st.get("date", "")
					st_ref = st.get("reference", "")
					if po_date and st_date:
						try:
							from datetime import datetime
							po_dt = datetime.fromtimestamp(int(po_date))
							try:
								st_dt = datetime.strptime(st_date, "%Y-%m-%d")
							except ValueError:
								# Try other date formats
								try:
									st_dt = datetime.strptime(st_date, "%Y/%m/%d")
								except ValueError:
									continue
							days_diff = abs((po_dt.date() - st_dt.date()).days)
							if days_diff <= max_date_diff_days:
								# Check if Stripe ID appears in reference (fuzzy match)
								match_type = "exact"
								if po_id.lower() in st_ref.lower() or st_ref.lower() in po_id.lower():
									match_type = "reference_match"
								matched.append({
									"stripe_payout_id": po_id,
									"stripe_amount": po_amount,
									"bank_amount": st_amount,
									"bank_date": st_date,
									"bank_reference": st_ref,
									"match_type": match_type,
									"date_diff_days": days_diff,
								})
								used_statements.add(idx)
								found = True
								break
						except Exception as e:
							logger.debug(f"date parsing error: {e}")
							continue
			if not found:
				unmatched_payouts.append(po)
		for idx, st in enumerate(statements):
			if idx not in used_statements:
				unmatched_statements.append(st)
		logger.info(
			"matched transactions",
			extra={
				"matched": len(matched),
				"unmatched_payouts": len(unmatched_payouts),
				"unmatched_statements": len(unmatched_statements),
			},
		)
		return {
			"matched": matched,
			"unmatched_payouts": unmatched_payouts,
			"unmatched_statements": unmatched_statements,
		}

	@task(task_id="persist_reconciliations")
	def persist_reconciliations(payload: Dict[str, Any]) -> Dict[str, Any]:
		matched = payload.get("matched", []) or []
		try:
			with get_conn() as conn:
				with conn.cursor() as cur:
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS reconciliations (
							id SERIAL PRIMARY KEY,
							stripe_payout_id TEXT NOT NULL,
							stripe_amount NUMERIC(12,2) NOT NULL,
							bank_amount NUMERIC(12,2) NOT NULL,
							bank_date DATE,
							bank_reference TEXT,
							match_type TEXT NOT NULL,
							date_diff_days INTEGER,
							reconciled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
							UNIQUE(stripe_payout_id)
						)
						"""
					)
					cur.execute(
						"""
						CREATE TABLE IF NOT EXISTS reconciliation_diffs (
							id SERIAL PRIMARY KEY,
							stripe_payout_id TEXT,
							stripe_amount NUMERIC(12,2),
							bank_amount NUMERIC(12,2),
							bank_date DATE,
							bank_reference TEXT,
							diff_type TEXT NOT NULL,
							created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
						)
						"""
					)
					for m in matched:
								cur.execute(
									"""
									INSERT INTO reconciliations 
									(stripe_payout_id, stripe_amount, bank_amount, bank_date, bank_reference, match_type, date_diff_days)
									VALUES (%s,%s,%s,%s,%s,%s,%s)
									ON CONFLICT (stripe_payout_id) DO UPDATE SET
										bank_amount = EXCLUDED.bank_amount,
										bank_date = EXCLUDED.bank_date,
										bank_reference = EXCLUDED.bank_reference,
										match_type = EXCLUDED.match_type,
										date_diff_days = EXCLUDED.date_diff_days,
										reconciled_at = NOW()
									""",
									(
										m.get("stripe_payout_id"),
										float(m.get("stripe_amount", 0.0)),
										float(m.get("bank_amount", 0.0)),
										m.get("bank_date"),
										m.get("bank_reference", ""),
										m.get("match_type", "exact"),
										m.get("date_diff_days"),
									),
								)
					for up in payload.get("unmatched_payouts", []) or []:
						cur.execute(
							"""
							INSERT INTO reconciliation_diffs 
							(stripe_payout_id, stripe_amount, diff_type)
							VALUES (%s,%s,%s)
							""",
							(up.get("id"), float(up.get("amount", 0.0)), "unmatched_payout"),
						)
					for us in payload.get("unmatched_statements", []) or []:
						cur.execute(
							"""
							INSERT INTO reconciliation_diffs 
							(bank_amount, bank_date, bank_reference, diff_type)
							VALUES (%s,%s,%s,%s)
							""",
							(
								float(us.get("amount", 0.0)),
								us.get("date"),
								us.get("reference", ""),
								"unmatched_statement",
							),
						)
					conn.commit()
		except Exception:
			logger.warning("reconciliation persistence failed", exc_info=True)
		return payload

	@task(task_id="report_metrics")
	def report_metrics(payload: Dict[str, Any]) -> None:
		matched_count = len(payload.get("matched", []) or [])
		unmatched_payouts_count = len(payload.get("unmatched_payouts", []) or [])
		unmatched_statements_count = len(payload.get("unmatched_statements", []) or [])
		total = matched_count + unmatched_payouts_count
		match_rate = (matched_count / total * 100) if total > 0 else 0.0
		logger.info(
			"reconciliation metrics",
			extra={
				"matched": matched_count,
				"unmatched_payouts": unmatched_payouts_count,
				"unmatched_statements": unmatched_statements_count,
				"match_rate_pct": round(match_rate, 2),
			},
		)
		if match_rate < 95.0 and total > 0:
			logger.warning(f"Low reconciliation rate: {match_rate:.2f}%")

	payouts = fetch_stripe_payouts()
	statements = load_bank_statements()
	matched = match_transactions(payouts, statements)
	persisted = persist_reconciliations(matched)
	report_metrics(persisted)
	return None


dag = bank_reconcile()

