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
  const [history, setHistory] = useState<LatestMetrics[]>([] as any);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState<number>(20);
  const [start, setStart] = useState<string>('');
  const [end, setEnd] = useState<string>('');
  const [runLabel, setRunLabel] = useState<string>('');
  const [dryRun, setDryRun] = useState<string>(''); // '', 'true', 'false'

  async function load() {
    try {
      const qs = new URLSearchParams();
      qs.set('limit', String(limit));
      if (start) qs.set('start', start);
      if (end) qs.set('end', end);
      if (runLabel) qs.set('run_label', runLabel);
      if (dryRun) qs.set('dry_run', dryRun);
      const [m, a, h] = await Promise.all([
        fetch('/api/metrics/latest', { cache: 'no-store' }).then(r => r.json()),
        fetch('/api/alerts/recent', { cache: 'no-store' }).then(r => r.json()),
        fetch(`/api/metrics/history?${qs.toString()}`, { cache: 'no-store' }).then(r => r.json()),
      ]);
      setLatest(m?.data || null);
      setAlerts(a?.data || []);
      setHistory(h?.data || []);
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

      <section style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
        <h2>Ratio histórico</h2>
        <RatioChart data={(history as any[]).slice().reverse().map((r:any, i:number)=>({ i, t: r.at, v: Number(r.ratio||0) }))} />
      </section>

      <section style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
        <h2>Histórico (últimos)</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6,auto)', gap: 8, alignItems: 'end', marginBottom: 8 }}>
          <label>Limite
            <input type="number" value={limit} min={1} max={500} onChange={(e) => setLimit(Number(e.target.value||20))} style={{ display:'block', width: 100 }} />
          </label>
          <label>Inicio
            <input type="datetime-local" value={start} onChange={(e)=>setStart(e.target.value)} style={{ display:'block' }} />
          </label>
          <label>Fin
            <input type="datetime-local" value={end} onChange={(e)=>setEnd(e.target.value)} style={{ display:'block' }} />
          </label>
          <label>Run label
            <input type="text" value={runLabel} onChange={(e)=>setRunLabel(e.target.value)} style={{ display:'block', width: 180 }} />
          </label>
          <label>Dry-run
            <select value={dryRun} onChange={(e)=>setDryRun(e.target.value)} style={{ display:'block' }}>
              <option value="">(todos)</option>
              <option value="true">true</option>
              <option value="false">false</option>
            </select>
          </label>
          <a href={`${(() => { const p = new URLSearchParams(); p.set('limit', String(limit)); if(start) p.set('start', start); if(end) p.set('end', end); if(runLabel) p.set('run_label', runLabel); if(dryRun) p.set('dry_run', dryRun); p.set('format','csv'); return '/api/metrics/history?'+p.toString(); })()}`} target="_blank" rel="noreferrer">Descargar CSV</a>
        </div>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>Fecha</th><th>Run</th><th>Total</th><th>Esperado</th><th>Ratio</th><th>Chunks</th><th>Dry</th>
            </tr>
          </thead>
          <tbody>
            {history.map((r: any, i: number) => (
              <tr key={i}>
                <td>{r.at}</td>
                <td>{r.run_label}</td>
                <td>{r.total_rows}</td>
                <td>{r.expected_rows}</td>
                <td>{typeof r.ratio === 'number' ? r.ratio.toFixed(3) : ''}</td>
                <td>{r.num_chunks}</td>
                <td>{r.dry_run ? 'Sí' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function RatioChart({ data, width = 700, height = 220 }: { data: { i:number; t:string; v:number }[]; width?: number; height?: number }) {
  if (!data || data.length === 0) return <div style={{ color: '#888' }}>Sin datos</div>;
  const padding = 28;
  const xs = data.map((d) => d.i);
  const ys = data.map((d) => d.v);
  const maxY = Math.max(...ys, 1);
  const minY = Math.min(...ys, 0);
  const scaleX = (i: number) => padding + (i / Math.max(xs.length - 1, 1)) * (width - padding * 2);
  const scaleY = (v: number) => height - padding - ((v - minY) / Math.max(maxY - minY, 1)) * (height - padding * 2);
  const path = data.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i)} ${scaleY(p.v)}`).join(' ');
  const avg = ys.reduce((a,b)=>a+b,0) / ys.length;
  const threshold = 1.0;
  const [hover, setHover] = useState<{ x:number; y:number; label:string } | null>(null as any);
  return (
    <div style={{ position: 'relative', width, height }}>
      <svg width={width} height={height} role="img" aria-label="Ratio histórico">
        <path d={path} fill="none" stroke="#16a34a" strokeWidth={2} />
        {/* average line */}
        <line x1={padding} x2={width - padding} y1={scaleY(avg)} y2={scaleY(avg)} stroke="#94a3b8" strokeDasharray="4 4" />
        <text x={padding} y={scaleY(avg)-6} fill="#475569" fontSize={11}>Promedio {avg.toFixed(3)}</text>
        {/* threshold line */}
        <line x1={padding} x2={width - padding} y1={scaleY(threshold)} y2={scaleY(threshold)} stroke="#ef4444" strokeDasharray="3 3" />
        <text x={width - padding - 120} y={scaleY(threshold)-6} fill="#ef4444" fontSize={11}>Umbral 1.000</text>
        {/* points */}
        {data.map((p, i) => (
          <circle key={i} cx={scaleX(i)} cy={scaleY(p.v)} r={3} fill="#16a34a"
            onMouseEnter={() => setHover({ x: scaleX(i), y: scaleY(p.v), label: `${p.t} • ${p.v.toFixed(3)}` })}
            onMouseLeave={() => setHover(null)}
          />
        ))}
        {/* axis */}
        <line x1={padding} x2={padding} y1={padding} y2={height - padding} stroke="#e5e7eb" />
        <line x1={padding} x2={width - padding} y1={height - padding} y2={height - padding} stroke="#e5e7eb" />
      </svg>
      {hover && (
        <div style={{ position: 'absolute', left: Math.min(Math.max(hover.x + 8, 0), width - 160), top: Math.max(hover.y - 28, 0), background: '#111827', color: '#fff', fontSize: 12, padding: '4px 8px', borderRadius: 6, pointerEvents: 'none' }}>
          {hover.label}
        </div>
      )}
    </div>
  );
}


