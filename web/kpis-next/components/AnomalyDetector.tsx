"use client";

import { useEffect, useState } from 'react';

type Anomaly = {
  metric: string;
  current: number;
  expected: number;
  deviation: number;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
};

export default function AnomalyDetector() {
	const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const loadAnomalies = async () => {
		setLoading(true);
		setError(null);
		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/anomalies` : '/api/kpi/anomalies';
			const response = await fetch(url, { cache: 'no-store' });
			if (!response.ok) throw new Error('Failed to load anomalies');
			const data = await response.json();
			setAnomalies(data.anomalies || []);
		} catch (e: any) {
			setError(e.message || 'Error loading anomalies');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadAnomalies();
		const interval = setInterval(loadAnomalies, 120000); // Every 2 minutes
		return () => clearInterval(interval);
	}, [baseUrl]);

	const getSeverityColor = (severity: string) => {
		switch (severity) {
			case 'high': return '#dc2626';
			case 'medium': return '#f59e0b';
			case 'low': return '#10b981';
			default: return '#6b7280';
		}
	};

	const getSeverityBg = (severity: string) => {
		switch (severity) {
			case 'high': return '#fef2f2';
			case 'medium': return '#fffbeb';
			case 'low': return '#f0fdf4';
			default: return '#f9fafb';
		}
	};

	if (loading && anomalies.length === 0) {
		return <div style={{ padding: 20, textAlign: 'center' }}>Analizando anomalías...</div>;
	}

	if (error) {
		return <div style={{ color: '#b91c1c', padding: 20 }}>Error: {error}</div>;
	}

	if (anomalies.length === 0) {
		return (
			<div style={{
				border: '1px solid #10b981',
				borderRadius: 8,
				padding: 16,
				backgroundColor: '#f0fdf4',
				marginBottom: 24,
			}}>
				<div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
					<span style={{ fontSize: 20 }}>✅</span>
					<span style={{ fontWeight: 500 }}>No se detectaron anomalías</span>
				</div>
			</div>
		);
	}

	return (
		<div style={{
			border: '1px solid #e5e7eb',
			borderRadius: 8,
			padding: 20,
			backgroundColor: 'white',
			boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
			marginBottom: 24,
		}}>
			<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
				<h3 style={{ margin: 0 }}>⚠️ Detección de Anomalías</h3>
				<button
					onClick={loadAnomalies}
					disabled={loading}
					style={{
						padding: '6px 12px',
						backgroundColor: '#3b82f6',
						color: 'white',
						border: 'none',
						borderRadius: 4,
						cursor: loading ? 'not-allowed' : 'pointer',
						fontSize: 12,
						opacity: loading ? 0.6 : 1,
					}}
				>
					{loading ? '⏳' : '🔄'} Actualizar
				</button>
			</div>
			<div style={{ display: 'grid', gap: 12 }}>
				{anomalies.map((anomaly, idx) => (
					<div
						key={idx}
						style={{
							border: `2px solid ${getSeverityColor(anomaly.severity)}`,
							borderRadius: 6,
							padding: 16,
							backgroundColor: getSeverityBg(anomaly.severity),
						}}
					>
						<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 8 }}>
							<div>
								<div style={{ fontWeight: 'bold', marginBottom: 4 }}>{anomaly.metric}</div>
								<div style={{ fontSize: 14, color: '#6b7280' }}>{anomaly.explanation}</div>
							</div>
							<span style={{
								padding: '4px 8px',
								backgroundColor: getSeverityColor(anomaly.severity),
								color: 'white',
								borderRadius: 4,
								fontSize: 11,
								fontWeight: 'bold',
								textTransform: 'uppercase',
							}}>
								{anomaly.severity}
							</span>
						</div>
						<div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 12, fontSize: 13 }}>
							<div>
								<div style={{ color: '#6b7280', marginBottom: 2 }}>Actual</div>
								<div style={{ fontWeight: 'bold' }}>{anomaly.current.toFixed(2)}</div>
							</div>
							<div>
								<div style={{ color: '#6b7280', marginBottom: 2 }}>Esperado</div>
								<div style={{ fontWeight: 'bold' }}>{anomaly.expected.toFixed(2)}</div>
							</div>
							<div>
								<div style={{ color: '#6b7280', marginBottom: 2 }}>Desviación</div>
								<div style={{ fontWeight: 'bold', color: getSeverityColor(anomaly.severity) }}>
									{anomaly.deviation > 0 ? '+' : ''}{anomaly.deviation.toFixed(1)}%
								</div>
							</div>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

