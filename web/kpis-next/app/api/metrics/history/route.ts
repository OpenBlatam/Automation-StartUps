import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const limit = Math.min(Number(url.searchParams.get('limit') || 30), 500);
  const start = url.searchParams.get('start');
  const end = url.searchParams.get('end');
  const runLabel = url.searchParams.get('run_label');
  const dryRun = url.searchParams.get('dry_run');
  const format = (url.searchParams.get('format') || '').toLowerCase();

  const where: string[] = [];
  const params: any[] = [];
  if (start) { params.push(start); where.push(`at >= $${params.length}`); }
  if (end) { params.push(end); where.push(`at <= $${params.length}`); }
  if (runLabel) { params.push(runLabel); where.push(`run_label = $${params.length}`); }
  if (dryRun === 'true' || dryRun === 'false') { params.push(dryRun === 'true'); where.push(`dry_run = $${params.length}`); }
  params.push(limit);

  const client = await pool.connect();
  try {
    const { rows } = await client.query(
      `
      SELECT run_label, total_rows, expected_rows, ratio, num_chunks, dry_run, at
      FROM public.etl_improved_metrics
      ${where.length ? `WHERE ${where.join(' AND ')}` : ''}
      ORDER BY at DESC
      LIMIT $${params.length};
      `,
      params
    );
    if (format === 'csv') {
      const header = ['run_label','total_rows','expected_rows','ratio','num_chunks','dry_run','at'];
      const lines = [header.join(',')].concat(
        rows.map(r => [r.run_label, r.total_rows, r.expected_rows, r.ratio, r.num_chunks, r.dry_run, r.at.toISOString?.() || r.at].join(','))
      );
      return new NextResponse(lines.join('\n'), { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
    }
    return NextResponse.json({ data: rows });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'query_failed' }, { status: 500 });
  } finally {
    client.release();
  }
}


