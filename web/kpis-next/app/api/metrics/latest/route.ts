import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
  const client = await pool.connect();
  try {
    const { rows } = await client.query(
      `
      SELECT run_label, total_rows, expected_rows, ratio, num_chunks, dry_run, at
      FROM public.etl_improved_metrics
      ORDER BY at DESC
      LIMIT 1;
      `
    );
    if (!rows.length) return NextResponse.json({ data: null });
    return NextResponse.json({ data: rows[0] });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'query_failed' }, { status: 500 });
  } finally {
    client.release();
  }
}




