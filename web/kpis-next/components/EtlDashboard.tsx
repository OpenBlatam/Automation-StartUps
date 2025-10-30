"use client";

import { useEffect, useState } from 'react';

type LatestMetrics = {
  run_label: string;
  total_rows: number;
  expected_rows: number;
  ratio: number;
  num_chunks: number;
  dry_run: boolean;
  at: string;
} | null;

type Alert = {
  kind: string;
  message: string;
  run_label: string | null;
  ratio: number | null;
  avg_ratio: number | null;
  threshold_pct: number | null;
  at: string;
};

export default function EtlDashboard() {
  const [latest, setLatest] = useState<LatestMetrics>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const [m, a] = await Promise.all([
        fetch('/api/metrics/latest', { cache: 'no-store' }).then(r => r.json()),
        fetch('/api/alerts/recent', { cache: 'no-store' }).then(r => r.json()),
      ]);
      setLatest(m?.data || null);
      setAlerts(a?.data || []);
      setError(null);
    } catch (e: any) {
      setError(e?.message || 'error');
    }
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      {error && <div style={{ color: '#b91c1c' }}>Error: {error}</div>}
      <section style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
        <h2>ETL Latest Metrics</h2>
        {!latest ? (
          <div>Sin datos</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
            <div><div style={{ color: '#666' }}>Run</div><div>{latest.run_label}</div></div>
            <div><div style={{ color: '#666' }}>Total</div><div>{latest.total_rows}</div></div>
            <div><div style={{ color: '#666' }}>Esperado</div><div>{latest.expected_rows}</div></div>
            <div><div style={{ color: '#666' }}>Ratio</div><div>{latest.ratio?.toFixed(3)}</div></div>
            <div><div style={{ color: '#666' }}>Chunks</div><div>{latest.num_chunks}</div></div>
            <div><div style={{ color: '#666' }}>Dry run</div><div>{latest.dry_run ? 'Sí' : 'No'}</div></div>
            <div><div style={{ color: '#666' }}>Fecha</div><div>{latest.at}</div></div>
          </div>
        )}
      </section>

      <section style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
        <h2>Alertas recientes</h2>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>Fecha</th><th>Tipo</th><th>Mensaje</th><th>Run</th><th>Ratio</th><th>Promedio</th><th>Umbral %</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((al, i) => (
              <tr key={i}>
                <td>{al.at}</td>
                <td>{al.kind}</td>
                <td>{al.message}</td>
                <td>{al.run_label || ''}</td>
                <td>{al.ratio ?? ''}</td>
                <td>{al.avg_ratio ?? ''}</td>
                <td>{al.threshold_pct ?? ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}


