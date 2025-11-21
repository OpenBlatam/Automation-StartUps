"use client";

import { useEffect, useState } from 'react';

type Recommendation = {
  priority: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  impact: string;
  action: string;
};

export default function RecommendationsPanel() {
	const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

	const loadRecommendations = async () => {
		setLoading(true);
		setError(null);
		try {
			const url = baseUrl ? `${baseUrl}/api/kpi/recommendations` : '/api/kpi/recommendations';
			const response = await fetch(url, { cache: 'no-store' });
			if (!response.ok) throw new Error('Failed to load recommendations');
			const data = await response.json();
			setRecommendations(data.recommendations || []);
		} catch (e: any) {
			setError(e.message || 'Error loading recommendations');
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadRecommendations();
		const interval = setInterval(loadRecommendations, 180000); // Every 3 minutes
		return () => clearInterval(interval);
	}, [baseUrl]);

	const getPriorityColor = (priority: string) => {
		switch (priority) {
			case 'high': return '#dc2626';
			case 'medium': return '#f59e0b';
			case 'low': return '#10b981';
			default: return '#6b7280';
		}
	};

	const getPriorityBg = (priority: string) => {
		switch (priority) {
			case 'high': return '#fef2f2';
			case 'medium': return '#fffbeb';
			case 'low': return '#f0fdf4';
			default: return '#f9fafb';
		}
	};

	if (loading && recommendations.length === 0) {
		return <div style={{ padding: 20, textAlign: 'center' }}>Generando recomendaciones...</div>;
	}

	if (error) {
		return <div style={{ color: '#b91c1c', padding: 20 }}>Error: {error}</div>;
	}

	if (recommendations.length === 0) {
		return null;
	}

	// Group by priority
	const highPriority = recommendations.filter(r => r.priority === 'high');
	const mediumPriority = recommendations.filter(r => r.priority === 'medium');
	const lowPriority = recommendations.filter(r => r.priority === 'low');

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
				<h3 style={{ margin: 0 }}>💡 Recomendaciones Inteligentes</h3>
				<button
					onClick={loadRecommendations}
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

			{[highPriority, mediumPriority, lowPriority].map((group, groupIdx) => {
				if (group.length === 0) return null;
				const priority = group[0].priority;
				return (
					<div key={groupIdx} style={{ marginBottom: groupIdx < 2 ? 20 : 0 }}>
						<h4 style={{
							marginBottom: 12,
							color: getPriorityColor(priority),
							fontSize: 14,
							textTransform: 'uppercase',
							fontWeight: 'bold',
						}}>
							Prioridad {priority === 'high' ? 'Alta' : priority === 'medium' ? 'Media' : 'Baja'}
						</h4>
						<div style={{ display: 'grid', gap: 12 }}>
							{group.map((rec, idx) => (
								<div
									key={idx}
									style={{
										border: `2px solid ${getPriorityColor(rec.priority)}`,
										borderRadius: 6,
										padding: 16,
										backgroundColor: getPriorityBg(rec.priority),
									}}
								>
									<div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 8 }}>
										<div style={{ flex: 1 }}>
											<div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
												<span style={{ 
													padding: '2px 8px',
													backgroundColor: getPriorityColor(rec.priority),
													color: 'white',
													borderRadius: 4,
													fontSize: 11,
													fontWeight: 'bold',
												}}>
													{rec.category}
												</span>
												<span style={{ fontWeight: 'bold', fontSize: 16 }}>{rec.title}</span>
											</div>
											<div style={{ fontSize: 14, color: '#4b5563', marginBottom: 8 }}>
												{rec.description}
											</div>
											<div style={{ fontSize: 13, color: '#6b7280', marginBottom: 4 }}>
												<strong>Impacto esperado:</strong> {rec.impact}
											</div>
											<div style={{
												padding: '8px 12px',
												backgroundColor: '#f3f4f6',
												borderRadius: 4,
												fontSize: 13,
												marginTop: 8,
											}}>
												<strong>Acción recomendada:</strong> {rec.action}
											</div>
										</div>
									</div>
								</div>
							))}
						</div>
					</div>
				);
			})}
		</div>
	);
}
