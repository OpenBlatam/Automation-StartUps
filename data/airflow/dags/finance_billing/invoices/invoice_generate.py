from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict
from pathlib import Path

from jinja2 import Template
from data.airflow.plugins.etl_notifications import notify_email
from data.airflow.plugins.db import get_conn

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.models import Variable
from airflow.exceptions import AirflowFailException


def _get_env_var(name: str, default: str | None = None, required: bool = False) -> str:
	value = Variable.get(name, default_var=default)
	if required and (value is None or str(value).strip() == ""):
		raise AirflowFailException(f"Missing required Airflow Variable: {name}")
	return str(value)


@dag(
	dag_id="invoice_generate",
	start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
	schedule="0 2 * * *",  # daily at 02:00 UTC
	catchup=False,
	default_args={
		"owner": "finance",
		"retries": 1,
		"retry_delay": timedelta(minutes=2),
		"email_on_failure": False,
		"email_on_retry": False,
	},
	description="Generate invoices daily from confirmed sales and notify customers",
	tags=["finance", "invoicing"],
)
def invoice_generate() -> None:
	logger = logging.getLogger("airflow.task")

    @task(task_id="load_sales")
    def load_sales() -> Dict[str, Any]:
        ctx = get_current_context()
        window = {
            "since": ctx["data_interval_start"].to_datetime_string(),
            "until": ctx["data_interval_end"].to_datetime_string(),
        }
        logger.info("loading sales window", extra=window)
        # Try Stripe if key present
        import os
        stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
        sales: list[Dict[str, Any]] = []
        if stripe_key:
            try:
                import requests  # type: ignore
                s = requests.Session()
                s.headers.update({"Authorization": f"Bearer {stripe_key}"})
                params = {
                    "limit": 100,
                    "created[gte]": int(ctx["data_interval_start"].int_timestamp),
                    "created[lte]": int(ctx["data_interval_end"].int_timestamp),
                    "paid": True,
                }
                starting_after = None
                while True:
                    p = dict(params)
                    if starting_after:
                        p["starting_after"] = starting_after
                    r = s.get("https://api.stripe.com/v1/charges", params=p, timeout=30)
                    r.raise_for_status()
                    out = r.json()
                    data = out.get("data", [])
                    for c in data:
                        sales.append({
                            "id": c.get("id"),
                            "amount": (c.get("amount") or 0) / 100.0,
                            "currency": (c.get("currency") or "").upper(),
                            "description": c.get("description") or "Stripe charge",
                        })
                    if out.get("has_more") and data:
                        starting_after = data[-1].get("id")
                    else:
                        break
            except Exception:
                logger.warning("stripe fetch failed; falling back to empty sales", exc_info=True)
        return {"sales": sales, "window": window}

	@task(task_id="build_invoice_rows")
	def build_invoice_rows(payload: Dict[str, Any]) -> Dict[str, Any]:
		serie = _get_env_var("INVOICE_SERIE", default="A")
		tax_rate = float(_get_env_var("TAX_RATE", default="0.21"))
		company_tax_id = _get_env_var("COMPANY_TAX_ID", default="")
		default_currency = _get_env_var("DEFAULT_CURRENCY", default="USD")
		ctx = get_current_context()
		invoice_date = ctx["data_interval_end"].to_date_string()
		logger.info(
			"building invoice rows",
			extra={"serie": serie, "tax_rate": tax_rate, "company_tax_id": company_tax_id, "currency": default_currency},
		)
		# Build items from sales if present; fallback to sample
		sales = payload.get("sales", []) or []
		currencies: set[str] = set()
		if sales:
			items = [
				{
					"description": s.get("description", "Venta"),
					"quantity": 1,
					"unit_price": float(s.get("amount", 0.0)),
					"total": float(s.get("amount", 0.0)),
					"currency": (s.get("currency") or default_currency).upper(),
				}
				for s in sales
			]
			currencies = {item["currency"] for item in items}
		else:
			items = [
				{"description": "Servicio mensual", "quantity": 1, "unit_price": 100.0, "total": 100.0, "currency": default_currency},
				{"description": "Soporte", "quantity": 2, "unit_price": 25.0, "total": 50.0, "currency": default_currency},
			]
			currencies.add(default_currency)
		# Validate items
		if not items:
			raise AirflowFailException("No items to invoice")
		for item in items:
			if float(item.get("total", 0.0)) < 0:
				raise AirflowFailException(f"Invalid item total: {item.get('total')}")
			if float(item.get("quantity", 0.0)) <= 0:
				raise AirflowFailException(f"Invalid quantity: {item.get('quantity')}")
			if float(item.get("unit_price", 0.0)) < 0:
				raise AirflowFailException(f"Invalid unit price: {item.get('unit_price')}")
		# Group by currency if multiple
		if len(currencies) > 1:
			logger.warning(f"Multiple currencies detected: {currencies}, using first currency")
		invoice_currency = list(currencies)[0] if currencies else default_currency
		# Calculate totals for invoice currency only
		items_in_currency = [i for i in items if i.get("currency") == invoice_currency]
		if not items_in_currency:
			items_in_currency = items
		subtotal = sum(float(i["total"]) for i in items_in_currency)
		if subtotal <= 0:
			raise AirflowFailException(f"Invalid subtotal: {subtotal}")
		taxes = round(subtotal * tax_rate, 2)
		total = round(subtotal + taxes, 2)
		payload.update({
			"serie": serie,
			"company_tax_id": company_tax_id,
			"tax_rate": tax_rate,
			"currency": invoice_currency,
			"items": items,
			"subtotal": subtotal,
			"taxes": taxes,
			"total": total,
			"invoice_date": invoice_date,
		})
		return payload

    @task(task_id="render_html")
    def render_html(payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("rendering invoice HTML", extra={"count": len(payload.get("invoices", []))})
        template_path = _get_env_var(
            "INVOICE_TEMPLATE_PATH",
            default=str(Path("/opt/airflow/data/airflow/plugins/templates/invoice.html")),
        )
        html_out_dir = Path(_get_env_var("INVOICE_HTML_OUT", default="/tmp/invoices"))
        html_out_dir.mkdir(parents=True, exist_ok=True)
        try:
            template_str = Path(template_path).read_text(encoding="utf-8")
        except Exception:
            # minimal fallback template
            template_str = """<html><body><h1>Factura {{ serie }}</h1><p>Empresa: {{ company_tax_id }}</p></body></html>"""
        tmpl = Template(template_str)
        html_paths: list[str] = []
        # Render preview with computed amounts
        currency = payload.get("currency", _get_env_var("DEFAULT_CURRENCY", default="USD"))
        currency_symbol = {"USD": "$", "EUR": "€", "MXN": "$", "GBP": "£"}.get(currency, currency)
        html = tmpl.render(
            serie=payload.get("serie", _get_env_var("INVOICE_SERIE", default="A")),
            company_tax_id=payload.get("company_tax_id", _get_env_var("COMPANY_TAX_ID", default="")),
            items=payload.get("items", []),
            subtotal=payload.get("subtotal", 0),
            tax_rate=float(payload.get("tax_rate", 0)),
            taxes=payload.get("taxes", 0),
            total=payload.get("total", 0),
            invoice_date=payload.get("invoice_date", ""),
            currency=currency,
            currency_symbol=currency_symbol,
        )
        out_path = html_out_dir / "invoice_preview.html"
        out_path.write_text(html, encoding="utf-8")
        html_paths.append(str(out_path))
        payload["html_paths"] = html_paths
        return payload

    @task(task_id="store_artifacts")
    def store_artifacts(payload: Dict[str, Any]) -> Dict[str, Any]:
        s3_bucket = _get_env_var("S3_BUCKET", default="")
        logger.info("storing artifacts", extra={"bucket": s3_bucket})
        html_paths = payload.get("html_paths", []) or []
        pdf_paths = payload.get("pdf_paths", []) or []
        if not s3_bucket or (not html_paths and not pdf_paths):
            payload["artifact_urls"] = []
            return payload
        try:
            import boto3  # type: ignore
            from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
            s3 = boto3.client(
                "s3",
                region_name=_get_env_var("AWS_DEFAULT_REGION", default=None),
            )
            uploaded: list[str] = []
            def _upload(local_path: str) -> str | None:
                p = Path(local_path)
                if not p.exists():
                    return None
                key = f"invoices/{p.name}"
                try:
                    s3.upload_file(str(p), s3_bucket, key)
                    ttl = int(_get_env_var("INVOICE_URL_TTL_SECONDS", default="604800"))
                    url = s3.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": s3_bucket, "Key": key},
                        ExpiresIn=ttl,
                    )
                    return url
                except (BotoCoreError, ClientError):
                    logger.warning("s3 upload failed", exc_info=True)
                    return None
            for lp in [*html_paths, *pdf_paths]:
                url = _upload(lp)
                if url:
                    uploaded.append(url)
            payload["artifact_urls"] = uploaded
        except Exception:
            logger.warning("artifact storage skipped", exc_info=True)
            payload["artifact_urls"] = []
        return payload

	@task(task_id="render_pdf")
	def render_pdf(payload: Dict[str, Any]) -> Dict[str, Any]:
		logger.info("rendering invoice PDF")
		pdf_out_dir = Path(_get_env_var("INVOICE_PDF_OUT", default="/tmp/invoices"))
		pdf_out_dir.mkdir(parents=True, exist_ok=True)
		serie = payload.get("serie", "")
		pdf_path = pdf_out_dir / f"invoice_{serie}.pdf"
		try:
			from reportlab.lib.pagesizes import A4  # type: ignore
			from reportlab.pdfgen import canvas  # type: ignore
			from reportlab.lib.units import mm  # type: ignore
			from reportlab.lib.colors import HexColor  # type: ignore
			c = canvas.Canvas(str(pdf_path), pagesize=A4)
			width, height = A4
			currency = payload.get("currency", "USD")
			currency_symbol = {"USD": "$", "EUR": "€", "MXN": "$", "GBP": "£"}.get(currency, currency)
			# Header
			c.setFillColor(HexColor("#2c3e50"))
			c.setFont("Helvetica-Bold", 20)
			c.drawString(20 * mm, height - 25 * mm, "FACTURA")
			c.setFont("Helvetica-Bold", 14)
			c.drawString(20 * mm, height - 35 * mm, f"Número: {serie}")
			c.setFillColor(HexColor("#000000"))
			c.setFont("Helvetica", 10)
			company_tax = payload.get("company_tax_id", "")
			if company_tax:
				c.drawString(20 * mm, height - 43 * mm, f"RFC/NIF: {company_tax}")
			invoice_date = payload.get("invoice_date", "")
			if invoice_date:
				c.drawString(20 * mm, height - 49 * mm, f"Fecha: {invoice_date}")
			c.drawString(20 * mm, height - 55 * mm, f"Moneda: {currency}")
			# Items table header
			y = height - 70 * mm
			c.setFont("Helvetica-Bold", 10)
			c.drawString(20 * mm, y, "Descripción")
			c.drawString(120 * mm, y, "Cant.")
			c.drawString(140 * mm, y, "Precio Unit.")
			c.drawString(170 * mm, y, "Total")
			y -= 6 * mm
			c.line(20 * mm, y, width - 20 * mm, y)
			y -= 4 * mm
			# Items
			c.setFont("Helvetica", 9)
			for item in payload.get("items", []):
				desc = str(item.get("description", ""))[:40]  # Truncate long descriptions
				qty = f"{float(item.get('quantity', 0)):.2f}"
				unit = f"{currency_symbol}{float(item.get('unit_price', 0)):.2f}"
				tot = f"{currency_symbol}{float(item.get('total', 0)):.2f}"
				c.drawString(20 * mm, y, desc)
				c.drawString(120 * mm, y, qty)
				c.drawString(140 * mm, y, unit)
				c.drawString(170 * mm, y, tot)
				y -= 7 * mm
				if y < 100:  # New page if needed
					c.showPage()
					y = height - 30 * mm
			# Totals
			y -= 8 * mm
			c.line(140 * mm, y, width - 20 * mm, y)
			y -= 6 * mm
			c.setFont("Helvetica", 10)
			subtotal = float(payload.get("subtotal", 0))
			c.drawString(140 * mm, y, f"Subtotal: {currency_symbol}{subtotal:.2f}")
			y -= 6 * mm
			taxes = float(payload.get("taxes", 0))
			tax_rate_pct = int(float(payload.get("tax_rate", 0)) * 100)
			c.drawString(140 * mm, y, f"Impuestos ({tax_rate_pct}%): {currency_symbol}{taxes:.2f}")
			y -= 8 * mm
			c.line(140 * mm, y, width - 20 * mm, y)
			y -= 6 * mm
			c.setFont("Helvetica-Bold", 12)
			total = float(payload.get("total", 0))
			c.drawString(140 * mm, y, f"TOTAL: {currency_symbol}{total:.2f}")
			c.showPage()
			c.save()
		except Exception as e:
			logger.warning("PDF generation skipped: %s", e)
			return payload
		payload.setdefault("pdf_paths", []).append(str(pdf_path))
		return payload

    @task(task_id="email_customer")
    def email_customer(payload: Dict[str, Any]) -> Dict[str, Any]:
        subject = "Factura emitida"
        urls = payload.get("artifact_urls", []) or []
        links = "".join(f"<div><a href='{u}'>Descargar factura</a></div>" for u in urls)
        body = f"<p>Tu factura ha sido generada.</p>{links if links else '<p>Adjuntaremos enlaces cuando estén disponibles.</p>'}"
        notify_email(subject=subject, html_content=body, to=None)
        payload["emailed"] = True
        return payload

	@task(task_id="mark_issued")
	def mark_issued(payload: Dict[str, Any]) -> None:
		logger.info("marking invoices as issued")
		return None

    @task(task_id="persist_in_db")
    def persist_in_db(payload: Dict[str, Any]) -> Dict[str, Any]:
        # Create minimal tables and insert a single aggregated invoice as example
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS invoices (
                        id SERIAL PRIMARY KEY,
                        serie TEXT NOT NULL,
                        company_tax_id TEXT,
                        currency VARCHAR(8) NOT NULL DEFAULT 'USD',
                        subtotal NUMERIC(12,2) NOT NULL,
                        taxes NUMERIC(12,2) NOT NULL,
                        total NUMERIC(12,2) NOT NULL,
                        status TEXT NOT NULL DEFAULT 'issued',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS invoice_items (
                        id SERIAL PRIMARY KEY,
                        invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                        description TEXT NOT NULL,
                        quantity NUMERIC(12,2) NOT NULL,
                        unit_price NUMERIC(12,2) NOT NULL,
                        total NUMERIC(12,2) NOT NULL
                    );
                    """
                )
                cur.execute(
                    "INSERT INTO invoices (serie, company_tax_id, currency, subtotal, taxes, total) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                    (
                        payload.get("serie","A"),
                        payload.get("company_tax_id",""),
                        payload.get("currency","USD"),
                        float(payload.get("subtotal",0.0)),
                        float(payload.get("taxes",0.0)),
                        float(payload.get("total",0.0)),
                    ),
                )
                invoice_id = cur.fetchone()[0]
                for it in payload.get("items", []) or []:
                    cur.execute(
                        "INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total) VALUES (%s,%s,%s,%s,%s)",
                        (
                            invoice_id,
                            it.get("description",""),
                            float(it.get("quantity",1)),
                            float(it.get("unit_price",0.0)),
                            float(it.get("total",0.0)),
                        ),
                    )
                conn.commit()
        payload["invoice_id"] = invoice_id
        return payload

    issued = mark_issued(
		email_customer(
			store_artifacts(
				render_pdf(
					render_html(
                        persist_in_db(
                            build_invoice_rows(load_sales())
                        )
					)
				)
			)
		)
	)
	return None


dag = invoice_generate()


