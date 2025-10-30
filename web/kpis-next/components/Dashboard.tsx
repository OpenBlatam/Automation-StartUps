"use client";

import { useEffect, useState } from 'react';

type Summary = {
	revenue_last_hour: number;
	revenue_24h: number;
	leads_by_priority_today: { priority: string; count: number }[];
	payments_recent: any[];
	leads_recent: any[];
};

type Point = { time: string; revenue: number };

function LineChart({ data, width = 600, height = 180 }: { data: Point[]; width?: number; height?: number }) {
	if (!data || data.length === 0) return <div style={{ color: '#888' }}>Sin datos</div>;
	const padding = 24;
	const xs = data.map((_, i) => i);
	const ys = data.map(d => d.revenue);
	const maxY = Math.max(...ys, 1);
	const minY = Math.min(...ys, 0);
	const scaleX = (i: number) => padding + (i / Math.max(xs.length - 1, 1)) * (width - padding * 2);
	const scaleY = (v: number) => height - padding - ((v - minY) / Math.max(maxY - minY, 1)) * (height - padding * 2);
	const d = data.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i)} ${scaleY(p.revenue)}`).join(' ');
	return (
		<svg width={width} height={height} role="img" aria-label="Ingresos 24h">
			<path d={d} fill="none" stroke="#2563eb" strokeWidth={2} />
			<line x1={padding} x2={width - padding} y1={scaleY(minY)} y2={scaleY(minY)} stroke="#eee" />
			<text x={padding} y={16} fill="#555" fontSize={12}>Máx: {maxY.toFixed(2)} | Mín: {minY.toFixed(2)}</text>
		</svg>
	);
}

export default function Dashboard() {
	const [summary, setSummary] = useState<Summary | null>(null);
	const [series, setSeries] = useState<Point[]>([]);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	async function load() {
		try {
			const summaryUrl = baseUrl ? `${baseUrl}/api/kpi/summary` : '/api/kpi/summary';
			const timeseriesUrl = baseUrl ? `${baseUrl}/api/kpi/timeseries` : '/api/kpi/timeseries';
			const [s, t] = await Promise.all([
				fetch(summaryUrl, { cache: 'no-store' }).then(r => r.json()),
				fetch(timeseriesUrl, { cache: 'no-store' }).then(r => r.json())
			]);
			setSummary(s);
			setSeries(t);
			setError(null);
		} catch (e: any) {
			setError(e.message || 'error');
		}
	}

	useEffect(() => {
		load();
		const id = setInterval(load, 10000);
		return () => clearInterval(id);
	}, []);

	return (
		<div>
			{error && <div style={{ color: '#b91c1c', marginBottom: 12 }}>Error: {error}</div>}
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
				<div style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
					<h3>Ingresos (última hora)</h3>
					<div style={{ fontSize: 28 }}>{summary ? `$ ${summary.revenue_last_hour.toFixed(2)}` : '...'}</div>
				</div>
				<div style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
					<h3>Ingresos (24h)</h3>
					<div style={{ fontSize: 28 }}>{summary ? `$ ${summary.revenue_24h.toFixed(2)}` : '...'}</div>
				</div>
				<div style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
					<h3>Leads por prioridad (hoy)</h3>
					<div>
						{summary ? summary.leads_by_priority_today.map((r) => (
							<span key={r.priority} style={{ marginRight: 12 }}>{(r.priority||'unknown')}: {r.count}</span>
						)) : '...'}
					</div>
				</div>
			</div>

			<div style={{ marginTop: 16, border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
				<h3>Ingresos por hora (24h)</h3>
				<LineChart data={series} />
			</div>

			<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>
				<div>
					<h3>Pagos recientes</h3>
					<table style={{ borderCollapse: 'collapse', width: '100%' }}>
						<thead><tr><th>Fecha</th><th>ID</th><th>Monto</th><th>Moneda</th><th>Cliente</th><th>Status</th><th>Método</th></tr></thead>
						<tbody>
							{summary ? summary.payments_recent.map((p: any) => (
								<tr key={p.payment_id}>
									<td>{p.created_at}</td><td>{p.payment_id}</td><td>{p.amount}</td><td>{p.currency}</td><td>{p.customer||''}</td><td>{p.status}</td><td>{p.method||''}</td>
								</tr>
							)) : null}
						</tbody>
					</table>
				</div>
				<div>
					<h3>Leads recientes</h3>
					<table style={{ borderCollapse: 'collapse', width: '100%' }}>
						<thead><tr><th>Fecha</th><th>ID</th><th>Nombre</th><th>Email</th><th>Score</th><th>Prioridad</th></tr></thead>
						<tbody>
							{summary ? summary.leads_recent.map((l: any) => (
								<tr key={l.ext_id}>
									<td>{l.created_at}</td><td>{l.ext_id}</td><td>{`${l.first_name||''} ${l.last_name||''}`}</td><td>{l.email||''}</td><td>{l.score||0}</td><td>{l.priority||''}</td>
								</tr>
							)) : null}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	);
}
