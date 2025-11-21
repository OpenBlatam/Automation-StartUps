import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

// Prometheus metrics export for ETL
export async function GET() {
  const client = await pool.connect();
  const lines: string[] = [];

  try {
    // Latest metrics as gauges
    const { rows: latest } = await client.query(
      `SELECT total_rows, expected_rows, ratio, num_chunks, dry_run, at 
       FROM public.etl_improved_metrics 
       ORDER BY at DESC LIMIT 1`
    );

    if (latest.length > 0) {
      const m = latest[0];
      const ageSeconds = m.at
        ? Math.floor((Date.now() - new Date(m.at).getTime()) / 1000)
        : 0;

      lines.push(`# HELP etl_latest_total_rows Latest ETL total rows processed`);
      lines.push(`# TYPE etl_latest_total_rows gauge`);
      lines.push(`etl_latest_total_rows ${m.total_rows || 0}`);

      lines.push(`# HELP etl_latest_expected_rows Latest ETL expected rows`);
      lines.push(`# TYPE etl_latest_expected_rows gauge`);
      lines.push(`etl_latest_expected_rows ${m.expected_rows || 0}`);

      lines.push(`# HELP etl_latest_ratio Latest ETL ratio (total/expected)`);
      lines.push(`# TYPE etl_latest_ratio gauge`);
      lines.push(`etl_latest_ratio ${m.ratio || 0}`);

      lines.push(`# HELP etl_latest_num_chunks Latest ETL number of chunks`);
      lines.push(`# TYPE etl_latest_num_chunks gauge`);
      lines.push(`etl_latest_num_chunks ${m.num_chunks || 0}`);

      lines.push(`# HELP etl_latest_run_age_seconds Seconds since last ETL run`);
      lines.push(`# TYPE etl_latest_run_age_seconds gauge`);
      lines.push(`etl_latest_run_age_seconds ${ageSeconds}`);

      lines.push(`# HELP etl_latest_dry_run Whether latest run was dry-run (1=yes, 0=no)`);
      lines.push(`# TYPE etl_latest_dry_run gauge`);
      lines.push(`etl_latest_dry_run ${m.dry_run ? 1 : 0}`);
    }

    // Daily metrics from materialized view
    const { rows: daily } = await client.query(
      `SELECT day, num_runs, total_rows_sum, ratio_avg, low_ratio_count 
       FROM public.mv_etl_metrics_daily 
       ORDER BY day DESC LIMIT 7`
    );

    if (daily.length > 0) {
      lines.push(`# HELP etl_daily_runs Number of ETL runs per day`);
      lines.push(`# TYPE etl_daily_runs gauge`);
      daily.forEach((d: any) => {
        const day = d.day ? new Date(d.day).getTime() / 1000 : 0;
        lines.push(`etl_daily_runs{day="${d.day}"} ${d.num_runs || 0}`);
      });

      lines.push(`# HELP etl_daily_total_rows Total rows processed per day`);
      lines.push(`# TYPE etl_daily_total_rows gauge`);
      daily.forEach((d: any) => {
        lines.push(`etl_daily_total_rows{day="${d.day}"} ${d.total_rows_sum || 0}`);
      });

      lines.push(`# HELP etl_daily_ratio_avg Average ratio per day`);
      lines.push(`# TYPE etl_daily_ratio_avg gauge`);
      daily.forEach((d: any) => {
        lines.push(`etl_daily_ratio_avg{day="${d.day}"} ${d.ratio_avg || 0}`);
      });

      lines.push(`# HELP etl_daily_low_ratio_count Low ratio runs count per day`);
      lines.push(`# TYPE etl_daily_low_ratio_count gauge`);
      daily.forEach((d: any) => {
        lines.push(`etl_daily_low_ratio_count{day="${d.day}"} ${d.low_ratio_count || 0}`);
      });
    }

    // Alert counts by type
    const { rows: alerts } = await client.query(
      `SELECT kind, COUNT(*) as count 
       FROM public.etl_improved_alerts 
       WHERE at >= NOW() - INTERVAL '24 hours'
       GROUP BY kind`
    );

    if (alerts.length > 0) {
      lines.push(`# HELP etl_alerts_24h_count Alert count in last 24h by type`);
      lines.push(`# TYPE etl_alerts_24h_count gauge`);
      alerts.forEach((a: any) => {
        lines.push(`etl_alerts_24h_count{kind="${a.kind}"} ${a.count || 0}`);
      });
    }

    // Overall stats
    const { rows: stats } = await client.query(
      `SELECT 
         COUNT(*) as total_runs,
         COUNT(CASE WHEN ratio < 1.0 THEN 1 END) as low_ratio_runs,
         AVG(ratio) as avg_ratio_all_time
       FROM public.etl_improved_metrics`
    );

    if (stats.length > 0 && stats[0].total_runs) {
      const s = stats[0];
      lines.push(`# HELP etl_total_runs_all_time Total ETL runs since inception`);
      lines.push(`# TYPE etl_total_runs_all_time counter`);
      lines.push(`etl_total_runs_all_time ${s.total_runs || 0}`);

      lines.push(`# HELP etl_low_ratio_runs_all_time Total low ratio runs`);
      lines.push(`# TYPE etl_low_ratio_runs_all_time counter`);
      lines.push(`etl_low_ratio_runs_all_time ${s.low_ratio_runs || 0}`);

      lines.push(`# HELP etl_avg_ratio_all_time Average ratio across all runs`);
      lines.push(`# TYPE etl_avg_ratio_all_time gauge`);
      lines.push(`etl_avg_ratio_all_time ${s.avg_ratio_all_time || 0}`);
    }

    return new NextResponse(lines.join('\n') + '\n', {
      headers: {
        'Content-Type': 'text/plain; version=0.0.4; charset=utf-8',
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err?.message || 'metrics_export_failed' },
      { status: 500 }
    );
  } finally {
    client.release();
  }
}


