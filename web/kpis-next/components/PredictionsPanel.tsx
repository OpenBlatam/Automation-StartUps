"use client";

import { useEffect, useState } from 'react';

type Prediction = {
  metric: string;
  current: number;
  predicted: number;
  confidence: number;
  timeframe: string;
  explanation: string;
};

export default function PredictionsPanel() {
	const [predictions, setPredictions] = useState<Prediction[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [timeframe, setTimeframe] = useState('7 days');

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const loadPredictions = async () => {
		setLoading(true);
		setError(null);
		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/predictions` : '/api/kpi/predictions';
			const response = await fetch(`${url}?timeframe=${timeframe}`, { cache: 'no-store' });
			if (!response.ok) throw new Error('Failed to load predictions');
			const data = await response.json();
			setPredictions(data.predictions || []);
		} catch (e: any) {
			setError(e.message || 'Error loading predictions');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadPredictions();
	}, [timeframe, baseUrl]);

	if (error) {
		return <div style={{ color: '#b91c1c', padding: 20 }}>Error: {error}</div>;
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
				<h3 style={{ margin: 0 }}>🔮 Predicciones</h3>
				<select
					value={timeframe}
					onChange={(e) => setTimeframe(e.target.value)}
					style={{
						padding: '6px 12px',
						border: '1px solid #d1d5db',
						borderRadius: 4,
						fontSize: 13,
					}}
				>
					<option value="3 days">3 días</option>
					<option value="7 days">7 días</option>
					<option value="14 days">14 días</option>
					<option value="30 days">30 días</option>
				</select>
			</div>

			{loading && predictions.length === 0 ? (
				<div style={{ padding: 20, textAlign: 'center' }}>Generando predicciones...</div>
			) : predictions.length === 0 ? (
				<div style={{ padding: 20, textAlign: 'center', color: '#6b7280' }}>No hay predicciones disponibles</div>
			) : (
				<div style={{ display: 'grid', gap: 16 }}>
					{predictions.map((pred, idx) => (
						<div
							key={idx}
							style={{
								border: '1px solid #e5e7eb',
								borderRadius: 6,
								padding: 16,
								backgroundColor: '#f9fafb',
							}}
						>
							<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
								<div style={{ flex: 1 }}>
									<div style={{ fontWeight: 'bold', marginBottom: 4, fontSize: 16 }}>{pred.metric}</div>
									<div style={{ fontSize: 13, color: '#6b7280', marginBottom: 8 }}>{pred.explanation}</div>
								</div>
								<div style={{
									padding: '4px 8px',
									backgroundColor: pred.confidence > 0.7 ? '#10b981' : pred.confidence > 0.5 ? '#f59e0b' : '#ef4444',
									color: 'white',
									borderRadius: 4,
									fontSize: 11,
									fontWeight: 'bold',
								}}>
									{(pred.confidence * 100).toFixed(0)}% confianza
								</div>
							</div>
							<div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
								<div>
									<div style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>Valor Actual</div>
									<div style={{ fontSize: 18, fontWeight: 'bold' }}>${pred.current.toFixed(2)}</div>
								</div>
								<div>
									<div style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>Predicción ({pred.timeframe})</div>
									<div style={{ fontSize: 18, fontWeight: 'bold', color: '#2563eb' }}>${pred.predicted.toFixed(2)}</div>
								</div>
								<div>
									<div style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>Cambio Esperado</div>
									<div style={{
										fontSize: 18,
										fontWeight: 'bold',
										color: pred.predicted > pred.current ? '#10b981' : '#ef4444',
									}}>
										{pred.predicted > pred.current ? '+' : ''}
										{((pred.predicted - pred.current) / pred.current * 100).toFixed(1)}%
									</div>
								</div>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}

