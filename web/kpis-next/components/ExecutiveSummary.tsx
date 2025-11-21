"use client";

import { useEffect, useState } from 'react';

export default function ExecutiveSummary() {
	const [summary, setSummary] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const loadSummary = async () => {
		setLoading(true);
		setError(null);
		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/executive-summary` : '/api/kpi/executive-summary';
			const response = await fetch(url, { cache: 'no-store' });
			if (!response.ok) throw new Error('Failed to load summary');
			const data = await response.json();
			setSummary(data.summary);
		} catch (e: any) {
			setError(e.message || 'Error loading summary');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadSummary();
		const interval = setInterval(loadSummary, 300000); // Every 5 minutes
		return () => clearInterval(interval);
	}, [baseUrl]);

	if (loading && !summary) {
		return <div style={{ padding: 20, textAlign: 'center' }}>Generando resumen ejecutivo...</div>;
	}

	if (error) {
		return <div style={{ color: '#b91c1c', padding: 20 }}>Error: {error}</div>;
	}

	if (!summary) return null;

	return (
		<div style={{
			border: '1px solid #3b82f6',
			borderRadius: 8,
			padding: 20,
			backgroundColor: '#eff6ff',
			borderLeft: '4px solid #3b82f6',
			marginBottom: 24,
		}}>
			<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
				<h3 style={{ margin: 0, color: '#1e40af', fontSize: 18 }}>📋 Resumen Ejecutivo</h3>
				<button
					onClick={loadSummary}
					disabled={loading}
					style={{
						padding: '6px 12px',
						backgroundColor: '#1e40af',
						color: 'white',
						border: 'none',
						borderRadius: 4,
						cursor: loading ? 'not-allowed' : 'pointer',
						fontSize: 12,
						opacity: loading ? 0.6 : 1,
					}}
				>
					{loading ? '⏳' : '🔄'}
				</button>
			</div>
			<div style={{
				color: '#1e3a8a',
				lineHeight: 1.8,
				fontSize: 15,
				whiteSpace: 'pre-wrap',
			}}>
				{summary}
			</div>
		</div>
	);
}

