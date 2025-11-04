"use client";

import { useEffect, useState } from 'react';
import NaturalLanguageQuery from './NaturalLanguageQuery';
import ReportGenerator from './ReportGenerator';
import TrendAnalysis from './TrendAnalysis';
import AdvancedFilters from './AdvancedFilters';
import AnomalyDetector from './AnomalyDetector';
import RecommendationsPanel from './RecommendationsPanel';
import PredictionsPanel from './PredictionsPanel';
import { downloadCSV, downloadExcel } from '@/lib/excel';

type Summary = {
	revenue_last_hour: number;
	revenue_24h: number;
	leads_by_priority_today: { priority: string; count: number }[];
	payments_recent: any[];
	leads_recent: any[];
};

type Point = { time: string; revenue: number };

type AgingBucket = {
	bucket: string;
	invoice_count: number;
	total_amount: number;
};

type RevenuePoint = {
	period: string;
	invoice_count: number;
	revenue: number;
	taxes: number;
	subtotal: number;
};

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
	const [aging, setAging] = useState<AgingBucket[]>([]);
	const [revenue, setRevenue] = useState<RevenuePoint[]>([]);
	const [insight, setInsight] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);
	const [filters, setFilters] = useState<any>({});

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	async function load() {
		try {
			const summaryUrl = baseUrl ? `${baseUrl}/api/kpi/summary` : '/api/kpi/summary';
			const timeseriesUrl = baseUrl ? `${baseUrl}/api/kpi/timeseries` : '/api/kpi/timeseries';
			const agingUrl = baseUrl ? `${baseUrl}/api/kpi/aging` : '/api/kpi/aging';
			const revenueUrl = baseUrl ? `${baseUrl}/api/kpi/revenue?period=daily` : '/api/kpi/revenue?period=daily';
			const [s, t, a, r] = await Promise.all([
				fetch(summaryUrl, { cache: 'no-store' }).then(r => r.json()),
				fetch(timeseriesUrl, { cache: 'no-store' }).then(r => r.json()),
				fetch(agingUrl, { cache: 'no-store' }).then(r => r.json()),
				fetch(revenueUrl, { cache: 'no-store' }).then(r => r.json())
			]);
			setSummary(s);
			setSeries(t);
			setAging(a);
			setRevenue(r);
			setError(null);
		} catch (e: any) {
			setError(e.message || 'error');
		}
	}

	const handleExport = async (format: 'excel' | 'csv', type: string = 'full') => {
		setLoading(true);
		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/export` : '/api/kpi/export';
			const response = await fetch(`${url}?format=${format}&type=${type}`, {
				method: 'GET',
			});
			
			if (!response.ok) throw new Error('Export failed');
			
			const blob = await response.blob();
			const downloadUrl = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = downloadUrl;
			a.download = `kpi-${type}-${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xls' : 'csv'}`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(downloadUrl);
		} catch (e: any) {
			setError(e.message || 'Export failed');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		let interval: any | null = null;
		let es: EventSource | null = null;
		const startPolling = () => {
			load();
			interval = setInterval(load, 10000);
		};
		try {
			const eventsUrl = baseUrl ? `${baseUrl}/api/kpi/events` : '/api/kpi/events';
			es = new EventSource(eventsUrl);
			es.addEventListener('update', (e: MessageEvent) => {
				try {
					const { summary: s, series: t, insight: i } = JSON.parse(e.data as string);
					setSummary(s);
					setSeries(t);
					if (i) setInsight(i);
					setError(null);
				} catch (err: any) {
					setError(err?.message || 'error');
				}
			});
			es.addEventListener('error', () => {
				if (es) {
					es.close();
					es = null;
				}
				if (!interval) startPolling();
			});
		} catch (_) {
			startPolling();
		}

		return () => {
			if (es) es.close();
			if (interval) clearInterval(interval);
		};
	}, [baseUrl]);

	return (
		<div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
			<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
				<h1 style={{ margin: 0, fontSize: 28 }}>📊 Dashboard KPIs en Tiempo Real</h1>
				<div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
					<button
						onClick={() => handleExport('excel', 'full')}
						disabled={loading}
						style={{
							padding: '8px 16px',
							backgroundColor: '#10b981',
							color: 'white',
							border: 'none',
							borderRadius: 6,
							cursor: loading ? 'not-allowed' : 'pointer',
							fontSize: 14,
						}}
					>
						📥 Excel
					</button>
					<button
						onClick={() => handleExport('csv', 'full')}
						disabled={loading}
						style={{
							padding: '8px 16px',
							backgroundColor: '#3b82f6',
							color: 'white',
							border: 'none',
							borderRadius: 6,
							cursor: loading ? 'not-allowed' : 'pointer',
							fontSize: 14,
						}}
					>
						📄 CSV
					</button>
				</div>
			</div>

			{error && (
				<div style={{ 
					color: '#b91c1c', 
					marginBottom: 12, 
					padding: 12,
					backgroundColor: '#fee2e2',
					borderRadius: 8,
					border: '1px solid #fecaca'
				}}>
					Error: {error}
				</div>
			)}

			<AdvancedFilters onFilterChange={setFilters} />

			{insight && (
				<div style={{ 
					border: '1px solid #3b82f6', 
					borderRadius: 8, 
					padding: 16, 
					marginBottom: 16,
					backgroundColor: '#eff6ff',
					borderLeft: '4px solid #3b82f6'
				}}>
					<h3 style={{ marginTop: 0, marginBottom: 8, color: '#1e40af', fontSize: 18 }}>💡 Análisis IA</h3>
					<p style={{ margin: 0, color: '#1e3a8a', lineHeight: 1.6 }}>{insight}</p>
				</div>
			)}

			<TrendAnalysis />

			<AnomalyDetector />

			<RecommendationsPanel />

			<PredictionsPanel />

			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16, marginBottom: 24 }}>
				<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 14, color: '#6b7280' }}>Ingresos (última hora)</h3>
					<div style={{ fontSize: 32, fontWeight: 'bold', color: '#059669' }}>
						{summary ? `$ ${summary.revenue_last_hour.toFixed(2)}` : '...'}
					</div>
				</div>
				<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 14, color: '#6b7280' }}>Ingresos (24h)</h3>
					<div style={{ fontSize: 32, fontWeight: 'bold', color: '#2563eb' }}>
						{summary ? `$ ${summary.revenue_24h.toFixed(2)}` : '...'}
					</div>
				</div>
				<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 8, fontSize: 14, color: '#6b7280' }}>Leads por prioridad (hoy)</h3>
					<div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
						{summary ? summary.leads_by_priority_today.map((r) => (
							<div key={r.priority} style={{ display: 'flex', justifyContent: 'space-between' }}>
								<span style={{ color: '#6b7280' }}>{(r.priority||'unknown')}:</span>
								<span style={{ fontWeight: 'bold' }}>{r.count}</span>
							</div>
						)) : '...'}
					</div>
				</div>
			</div>

			<div style={{ marginBottom: 24, border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
				<h3 style={{ marginTop: 0, marginBottom: 12 }}>Ingresos por hora (24h)</h3>
				<LineChart data={series} width={800} height={200} />
			</div>

			<div style={{ marginBottom: 24 }}>
				<h2 style={{ marginBottom: 16 }}>Finanzas</h2>
				<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 16 }}>
					<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
						<h3 style={{ marginTop: 0, marginBottom: 12 }}>A/R Aging (Cuentas por Cobrar)</h3>
						<table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '14px' }}>
							<thead>
								<tr style={{ backgroundColor: '#f9fafb' }}>
									<th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Bucket</th>
									<th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Facturas</th>
									<th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Monto</th>
								</tr>
							</thead>
							<tbody>
								{aging.length > 0 ? aging.map((b) => (
									<tr key={b.bucket}>
										<td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{b.bucket}</td>
										<td style={{ padding: '10px', textAlign: 'right', borderBottom: '1px solid #f3f4f6' }}>{b.invoice_count}</td>
										<td style={{ 
											padding: '10px', 
											textAlign: 'right', 
											fontWeight: b.bucket === '90+' ? 'bold' : 'normal', 
											color: b.bucket === '90+' ? '#b91c1c' : 'inherit',
											borderBottom: '1px solid #f3f4f6'
										}}>
											${b.total_amount.toFixed(2)}
										</td>
									</tr>
								)) : <tr><td colSpan={3} style={{ padding: '10px', color: '#888', textAlign: 'center' }}>Sin datos</td></tr>}
							</tbody>
						</table>
					</div>
					<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
						<h3 style={{ marginTop: 0, marginBottom: 12 }}>Revenue Diario (Últimos 30 días)</h3>
						{revenue.length > 0 ? (
							<table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '14px' }}>
								<thead>
									<tr style={{ backgroundColor: '#f9fafb' }}>
										<th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Período</th>
										<th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Facturas</th>
										<th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Revenue</th>
									</tr>
								</thead>
								<tbody>
									{revenue.slice(0, 10).map((r) => (
										<tr key={r.period}>
											<td style={{ padding: '10px', borderBottom: '1px solid #f3f4f6' }}>{r.period}</td>
											<td style={{ padding: '10px', textAlign: 'right', borderBottom: '1px solid #f3f4f6' }}>{r.invoice_count}</td>
											<td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold', borderBottom: '1px solid #f3f4f6' }}>
												${r.revenue.toFixed(2)}
											</td>
										</tr>
									))}
								</tbody>
							</table>
						) : <div style={{ color: '#888', padding: '16px', textAlign: 'center' }}>Sin datos</div>}
					</div>
				</div>
			</div>

			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: 16, marginBottom: 24 }}>
				<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 12 }}>Pagos recientes</h3>
					<div style={{ overflowX: 'auto' }}>
						<table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '13px' }}>
							<thead>
								<tr style={{ backgroundColor: '#f9fafb' }}>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Fecha</th>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>ID</th>
									<th style={{ padding: '8px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Monto</th>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Status</th>
								</tr>
							</thead>
							<tbody>
								{summary ? summary.payments_recent.slice(0, 10).map((p: any) => (
									<tr key={p.payment_id}>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{p.created_at}</td>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{p.payment_id}</td>
										<td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #f3f4f6' }}>${p.amount}</td>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{p.status}</td>
									</tr>
								)) : <tr><td colSpan={4} style={{ padding: '10px', color: '#888', textAlign: 'center' }}>Cargando...</td></tr>}
							</tbody>
						</table>
					</div>
				</div>
				<div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 16, backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 12 }}>Leads recientes</h3>
					<div style={{ overflowX: 'auto' }}>
						<table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '13px' }}>
							<thead>
								<tr style={{ backgroundColor: '#f9fafb' }}>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Fecha</th>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Nombre</th>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Email</th>
									<th style={{ padding: '8px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Score</th>
								</tr>
							</thead>
							<tbody>
								{summary ? summary.leads_recent.slice(0, 10).map((l: any) => (
									<tr key={l.ext_id}>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{l.created_at}</td>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{`${l.first_name||''} ${l.last_name||''}`}</td>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{l.email||''}</td>
										<td style={{ padding: '8px', borderBottom: '1px solid #f3f4f6' }}>{l.score||0}</td>
									</tr>
								)) : <tr><td colSpan={4} style={{ padding: '10px', color: '#888', textAlign: 'center' }}>Cargando...</td></tr>}
							</tbody>
						</table>
					</div>
				</div>
			</div>

			<NaturalLanguageQuery />

			<ReportGenerator />
		</div>
	);
}

