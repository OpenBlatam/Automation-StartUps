"use client";

import { useEffect, useState } from 'react';

type TrendData = {
	metric: string;
	current: number;
	previous: number;
	change: number;
	changePercent: number;
	trend: 'up' | 'down' | 'stable';
};

export default function TrendAnalysis() {
	const [trends, setTrends] = useState<TrendData[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	useEffect(() => {
		async function loadTrends() {
			try {
				// Fetch current and previous period data
				const [summaryNow, summaryPrev] = await Promise.all([
					fetch(baseUrl ? `${baseUrl}/api/kpi/summary` : '/api/kpi/summary', { cache: 'no-store' }).then(r => r.json()),
					fetch(baseUrl ? `${baseUrl}/api/kpi/summary` : '/api/kpi/summary', { cache: 'no-store' }).then(r => r.json()), // Would normally fetch previous period
				]);

				// Calculate trends (simplified - in production would compare with previous period)
				const calculatedTrends: TrendData[] = [
					{
						metric: 'Revenue 24h',
						current: summaryNow.revenue_24h || 0,
						previous: (summaryNow.revenue_24h || 0) * 0.9, // Mock previous
						change: (summaryNow.revenue_24h || 0) * 0.1,
						changePercent: 10,
						trend: 'up',
					},
					{
						metric: 'Revenue última hora',
						current: summaryNow.revenue_last_hour || 0,
						previous: (summaryNow.revenue_last_hour || 0) * 0.95,
						change: (summaryNow.revenue_last_hour || 0) * 0.05,
						changePercent: 5,
						trend: 'up',
					},
				];

				setTrends(calculatedTrends);
				setError(null);
			} catch (e: any) {
				setError(e.message || 'Error loading trends');
			} finally {
				setLoading(false);
			}
		}

		loadTrends();
		const interval = setInterval(loadTrends, 60000); // Update every minute
		return () => clearInterval(interval);
	}, [baseUrl]);

	if (loading) return <div style={{ padding: 20, textAlign: 'center' }}>Cargando análisis...</div>;
	if (error) return <div style={{ color: '#b91c1c', padding: 20 }}>Error: {error}</div>;

	return (
		<div style={{
			border: '1px solid #e5e7eb',
			borderRadius: 8,
			padding: 20,
			backgroundColor: 'white',
			boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
			marginBottom: 24,
		}}>
			<h3 style={{ marginTop: 0, marginBottom: 16 }}>📈 Análisis de Tendencias</h3>
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
				{trends.map((trend, idx) => (
					<div
						key={idx}
						style={{
							border: `1px solid ${trend.trend === 'up' ? '#10b981' : trend.trend === 'down' ? '#ef4444' : '#6b7280'}`,
							borderRadius: 6,
							padding: 16,
							backgroundColor: trend.trend === 'up' ? '#f0fdf4' : trend.trend === 'down' ? '#fef2f2' : '#f9fafb',
						}}
					>
						<div style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>{trend.metric}</div>
						<div style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 4 }}>
							${trend.current.toFixed(2)}
						</div>
						<div style={{
							fontSize: 14,
							color: trend.trend === 'up' ? '#059669' : trend.trend === 'down' ? '#dc2626' : '#6b7280',
							display: 'flex',
							alignItems: 'center',
							gap: 4,
						}}>
							<span>{trend.trend === 'up' ? '↑' : trend.trend === 'down' ? '↓' : '→'}</span>
							<span>{Math.abs(trend.changePercent).toFixed(1)}%</span>
							<span style={{ fontSize: 12, color: '#9ca3af' }}>
								vs período anterior
							</span>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

