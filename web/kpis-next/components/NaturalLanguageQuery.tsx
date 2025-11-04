"use client";

import { useState } from 'react';

export default function NaturalLanguageQuery() {
	const [query, setQuery] = useState('');
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState<any>(null);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!query.trim()) return;

		setLoading(true);
		setError(null);
		setResult(null);

		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/query` : '/api/kpi/query';
			const response = await fetch(url, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ query: query.trim(), execute: true }),
			});

			if (!response.ok) {
				const err = await response.json();
				throw new Error(err.error || 'Failed to execute query');
			}

			const data = await response.json();
			setResult(data);
		} catch (e: any) {
			setError(e.message || 'Error executing query');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ 
			border: '1px solid #eee', 
			borderRadius: 8, 
			padding: 16, 
			marginTop: 16,
			backgroundColor: '#fafafa'
		}}>
			<h3 style={{ marginTop: 0 }}>🔍 Consulta en Lenguaje Natural</h3>
			<form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
				<input
					type="text"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					placeholder="Ej: ¿Cuántos leads recibimos hoy? o ¿Cuál fue el revenue total de la última semana?"
					style={{
						width: '100%',
						padding: '8px 12px',
						border: '1px solid #ddd',
						borderRadius: 4,
						fontSize: 14,
						marginBottom: 8,
					}}
					disabled={loading}
				/>
				<button
					type="submit"
					disabled={loading || !query.trim()}
					style={{
						padding: '8px 16px',
						backgroundColor: '#3b82f6',
						color: 'white',
						border: 'none',
						borderRadius: 4,
						cursor: loading ? 'not-allowed' : 'pointer',
						opacity: loading || !query.trim() ? 0.6 : 1,
					}}
				>
					{loading ? 'Consultando...' : 'Consultar'}
				</button>
			</form>

			{error && (
				<div style={{ 
					color: '#b91c1c', 
					padding: 12, 
					backgroundColor: '#fee2e2', 
					borderRadius: 4,
					marginBottom: 12
				}}>
					Error: {error}
				</div>
			)}

			{result && (
				<div>
					<div style={{ marginBottom: 12 }}>
						<strong>SQL generado:</strong>
						<pre style={{
							backgroundColor: '#f3f4f6',
							padding: 12,
							borderRadius: 4,
							overflow: 'auto',
							fontSize: 12,
							marginTop: 4,
						}}>
							{result.sql}
						</pre>
					</div>
					{result.explanation && (
						<div style={{ marginBottom: 12, color: '#666', fontSize: 14 }}>
							<strong>Explicación:</strong> {result.explanation}
						</div>
					)}
					{result.data && result.data.length > 0 && (
						<div>
							<strong>Resultados ({result.rowCount || result.data.length} filas):</strong>
							<table style={{
								width: '100%',
								borderCollapse: 'collapse',
								marginTop: 8,
								fontSize: 14,
							}}>
								<thead>
									<tr style={{ backgroundColor: '#f5f5f5' }}>
										{Object.keys(result.data[0]).map(key => (
											<th key={key} style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>
												{key}
											</th>
										))}
									</tr>
								</thead>
								<tbody>
									{result.data.slice(0, 20).map((row: any, idx: number) => (
										<tr key={idx}>
											{Object.values(row).map((val: any, i) => (
												<td key={i} style={{ padding: '8px', border: '1px solid #ddd' }}>
													{val === null || val === undefined ? 'null' : String(val)}
												</td>
											))}
										</tr>
									))}
								</tbody>
							</table>
							{result.data.length > 20 && (
								<div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
									Mostrando 20 de {result.data.length} resultados
								</div>
							)}
						</div>
					)}
					{result.data && result.data.length === 0 && (
						<div style={{ color: '#666', padding: 12 }}>
							No se encontraron resultados
						</div>
					)}
				</div>
			)}
		</div>
	);
}


