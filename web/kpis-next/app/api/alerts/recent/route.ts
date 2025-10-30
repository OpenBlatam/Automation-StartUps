import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
  const client = await pool.connect();
  try {
    const { rows } = await client.query(
      `
      SELECT kind, message, run_label, ratio, avg_ratio, threshold_pct, at
      FROM public.etl_improved_alerts
      ORDER BY at DESC
      LIMIT 50;
      `
    );
    return NextResponse.json({ data: rows });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'query_failed' }, { status: 500 });
  } finally {
    client.release();
  }
}


