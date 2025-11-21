"use client";

import { useState } from 'react';

type FilterConfig = {
	dateRange: { start: string; end: string };
	country?: string;
	source?: string;
	priority?: string;
};

export default function AdvancedFilters({ onFilterChange }: { onFilterChange: (filters: FilterConfig) => void }) {
	const [filters, setFilters] = useState<FilterConfig>({
		dateRange: {
			start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
			end: new Date().toISOString().split('T')[0],
		},
	});

	const handleChange = (key: keyof FilterConfig, value: any) => {
		const newFilters = { ...filters, [key]: value };
		setFilters(newFilters);
		onFilterChange(newFilters);
	};

	const handleReset = () => {
		const resetFilters: FilterConfig = {
			dateRange: {
				start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
				end: new Date().toISOString().split('T')[0],
			},
		};
		setFilters(resetFilters);
		onFilterChange(resetFilters);
	};

	return (
		<div style={{
			border: '1px solid #e5e7eb',
			borderRadius: 8,
			padding: 16,
			backgroundColor: '#f9fafb',
			marginBottom: 24,
		}}>
			<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
				<h4 style={{ margin: 0, fontSize: 16 }}>🔍 Filtros Avanzados</h4>
				<button
					onClick={handleReset}
					style={{
						padding: '6px 12px',
						backgroundColor: 'transparent',
						color: '#6b7280',
						border: '1px solid #d1d5db',
						borderRadius: 4,
						cursor: 'pointer',
						fontSize: 12,
					}}
				>
					Limpiar
				</button>
			</div>
			<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
				<div>
					<label style={{ display: 'block', marginBottom: 4, fontSize: 12, fontWeight: 500 }}>Fecha Inicio:</label>
					<input
						type="date"
						value={filters.dateRange.start}
						onChange={(e) => handleChange('dateRange', { ...filters.dateRange, start: e.target.value })}
						style={{
							width: '100%',
							padding: '6px 8px',
							border: '1px solid #d1d5db',
							borderRadius: 4,
							fontSize: 13,
						}}
					/>
				</div>
				<div>
					<label style={{ display: 'block', marginBottom: 4, fontSize: 12, fontWeight: 500 }}>Fecha Fin:</label>
					<input
						type="date"
						value={filters.dateRange.end}
						onChange={(e) => handleChange('dateRange', { ...filters.dateRange, end: e.target.value })}
						style={{
							width: '100%',
							padding: '6px 8px',
							border: '1px solid #d1d5db',
							borderRadius: 4,
							fontSize: 13,
						}}
					/>
				</div>
				<div>
					<label style={{ display: 'block', marginBottom: 4, fontSize: 12, fontWeight: 500 }}>País:</label>
					<input
						type="text"
						placeholder="Filtrar por país"
						value={filters.country || ''}
						onChange={(e) => handleChange('country', e.target.value || undefined)}
						style={{
							width: '100%',
							padding: '6px 8px',
							border: '1px solid #d1d5db',
							borderRadius: 4,
							fontSize: 13,
						}}
					/>
				</div>
				<div>
					<label style={{ display: 'block', marginBottom: 4, fontSize: 12, fontWeight: 500 }}>Fuente:</label>
					<input
						type="text"
						placeholder="Filtrar por fuente"
						value={filters.source || ''}
						onChange={(e) => handleChange('source', e.target.value || undefined)}
						style={{
							width: '100%',
							padding: '6px 8px',
							border: '1px solid #d1d5db',
							borderRadius: 4,
							fontSize: 13,
						}}
					/>
				</div>
				<div>
					<label style={{ display: 'block', marginBottom: 4, fontSize: 12, fontWeight: 500 }}>Prioridad:</label>
					<select
						value={filters.priority || ''}
						onChange={(e) => handleChange('priority', e.target.value || undefined)}
						style={{
							width: '100%',
							padding: '6px 8px',
							border: '1px solid #d1d5db',
							borderRadius: 4,
							fontSize: 13,
						}}
					>
						<option value="">Todas</option>
						<option value="high">Alta</option>
						<option value="medium">Media</option>
						<option value="low">Baja</option>
					</select>
				</div>
			</div>
		</div>
	);
}

