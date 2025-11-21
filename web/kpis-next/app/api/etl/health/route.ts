import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
  const client = await pool.connect();
  try {
    const checks: Record<string, any> = {};
    let overallHealthy = true;

    // Check 1: DB connectivity
    try {
      await client.query('SELECT 1');
      checks.db_connectivity = { status: 'ok', message: 'Connected' };
    } catch (err: any) {
      checks.db_connectivity = { status: 'error', message: err?.message || 'Connection failed' };
      overallHealthy = false;
    }

    // Check 2: Tables exist
    const requiredTables = [
      'etl_improved_metrics',
      'etl_improved_alerts',
      'etl_improved_audit',
      'etl_improved_events',
    ];
    const tableChecks: Record<string, any> = {};
    for (const table of requiredTables) {
      try {
        const { rows } = await client.query(
          `SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = $1
          )`,
          [table]
        );
        const exists = rows[0]?.exists || false;
        tableChecks[table] = { status: exists ? 'ok' : 'missing', exists };
        if (!exists) overallHealthy = false;
      } catch (err: any) {
        tableChecks[table] = { status: 'error', message: err?.message };
        overallHealthy = false;
      }
    }
    checks.tables = tableChecks;

    // Check 3: Latest successful run
    try {
      const { rows } = await client.query(
        `SELECT at, run_label, ratio, total_rows, expected_rows 
         FROM public.etl_improved_metrics 
         ORDER BY at DESC LIMIT 1`
      );
      if (rows.length > 0) {
        const latest = rows[0];
        const ageMinutes = latest.at
          ? Math.floor((Date.now() - new Date(latest.at).getTime()) / 60000)
          : null;
        checks.latest_run = {
          status: 'ok',
          at: latest.at,
          run_label: latest.run_label,
          ratio: latest.ratio,
          total_rows: latest.total_rows,
          expected_rows: latest.expected_rows,
          age_minutes: ageMinutes,
        };
        // Warn if no run in last 24 hours
        if (ageMinutes && ageMinutes > 1440) {
          checks.latest_run.warning = 'No run in last 24 hours';
        }
      } else {
        checks.latest_run = { status: 'warning', message: 'No runs found' };
      }
    } catch (err: any) {
      checks.latest_run = { status: 'error', message: err?.message };
      overallHealthy = false;
    }

    // Check 4: Materialized views
    try {
      const { rows } = await client.query(
        `SELECT EXISTS (
          SELECT FROM pg_matviews 
          WHERE schemaname = 'public' AND matviewname = 'mv_etl_metrics_daily'
        )`
      );
      const mvsExist = rows[0]?.exists || false;
      checks.materialized_views = {
        status: mvsExist ? 'ok' : 'warning',
        exists: mvsExist,
        message: mvsExist ? 'Views exist' : 'Views not found (run etl_setup.sql)',
      };
    } catch (err: any) {
      checks.materialized_views = { status: 'error', message: err?.message };
    }

    return NextResponse.json({
      healthy: overallHealthy,
      timestamp: new Date().toISOString(),
      checks,
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        healthy: false,
        timestamp: new Date().toISOString(),
        error: err?.message || 'healthcheck_failed',
      },
      { status: 500 }
    );
  } finally {
    client.release();
  }
}


