"use client";

import { useState } from 'react';

export default function ReportGenerator() {
	const [reportType, setReportType] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>('daily');
	const [provider, setProvider] = useState<'openai' | 'deepseek'>('openai');
	const [loading, setLoading] = useState(false);
	const [report, setReport] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const handleGenerate = async () => {
		setLoading(true);
		setError(null);
		setReport(null);

		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/report` : '/api/kpi/report';
			const response = await fetch(`${url}?type=${reportType}&provider=${provider}`, {
				method: 'GET',
			});

			if (!response.ok) {
				const err = await response.json();
				throw new Error(err.error || 'Failed to generate report');
			}

			const data = await response.json();
			setReport(data.report);
		} catch (e: any) {
			setError(e.message || 'Error generating report');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ 
			border: '1px solid #e5e7eb', 
			borderRadius: 8, 
			padding: 20, 
			marginTop: 24,
			backgroundColor: 'white',
			boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
		}}>
			<h3 style={{ marginTop: 0, marginBottom: 16 }}>📄 Generador de Reportes con IA</h3>
			
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 16 }}>
				<div>
					<label style={{ display: 'block', marginBottom: 6, fontSize: 14, fontWeight: 500 }}>Tipo de Reporte:</label>
					<select
						value={reportType}
						onChange={(e) => setReportType(e.target.value as any)}
						style={{
							width: '100%',
							padding: '8px 12px',
							border: '1px solid #d1d5db',
							borderRadius: 6,
							fontSize: 14,
						}}
						disabled={loading}
					>
						<option value="daily">Diario</option>
						<option value="weekly">Semanal</option>
						<option value="monthly">Mensual</option>
						<option value="custom">Personalizado</option>
					</select>
				</div>

				<div>
					<label style={{ display: 'block', marginBottom: 6, fontSize: 14, fontWeight: 500 }}>Proveedor LLM:</label>
					<select
						value={provider}
						onChange={(e) => setProvider(e.target.value as any)}
						style={{
							width: '100%',
							padding: '8px 12px',
							border: '1px solid #d1d5db',
							borderRadius: 6,
							fontSize: 14,
						}}
						disabled={loading}
					>
						<option value="openai">OpenAI</option>
						<option value="deepseek">DeepSeek</option>
					</select>
				</div>

				<div style={{ display: 'flex', alignItems: 'flex-end' }}>
					<button
						onClick={handleGenerate}
						disabled={loading}
						style={{
							padding: '10px 24px',
							backgroundColor: '#3b82f6',
							color: 'white',
							border: 'none',
							borderRadius: 6,
							cursor: loading ? 'not-allowed' : 'pointer',
							opacity: loading ? 0.6 : 1,
							fontSize: 14,
							fontWeight: 500,
							width: '100%',
						}}
					>
						{loading ? '⏳ Generando...' : '🚀 Generar Reporte'}
					</button>
				</div>
			</div>

			{error && (
				<div style={{
					color: '#b91c1c',
					padding: 12,
					backgroundColor: '#fee2e2',
					borderRadius: 6,
					marginBottom: 16,
					border: '1px solid #fecaca',
				}}>
					<strong>Error:</strong> {error}
				</div>
			)}

			{report && (
				<div style={{
					border: '1px solid #3b82f6',
					borderRadius: 8,
					padding: 20,
					backgroundColor: '#eff6ff',
					borderLeft: '4px solid #3b82f6',
				}}>
					<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
						<h4 style={{ margin: 0, color: '#1e40af' }}>Reporte Generado</h4>
						<button
							onClick={() => {
								const blob = new Blob([report], { type: 'text/plain' });
								const url = URL.createObjectURL(blob);
								const a = document.createElement('a');
								a.href = url;
								a.download = `reporte-${reportType}-${new Date().toISOString().split('T')[0]}.txt`;
								a.click();
								URL.revokeObjectURL(url);
							}}
							style={{
								padding: '6px 12px',
								backgroundColor: '#1e40af',
								color: 'white',
								border: 'none',
								borderRadius: 4,
								cursor: 'pointer',
								fontSize: 12,
							}}
						>
							📥 Descargar
						</button>
					</div>
					<div style={{
						whiteSpace: 'pre-wrap',
						lineHeight: 1.8,
						color: '#1e3a8a',
						fontSize: 14,
						maxHeight: '400px',
						overflowY: 'auto',
					}}>
						{report}
					</div>
				</div>
			)}
		</div>
	);
}

