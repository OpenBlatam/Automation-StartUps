import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
	try {
		const client = await pool.connect();
		try {
			const q = await client.query(`
				SELECT 
					cn.id,
					cn.credit_note_number,
					cn.amount,
					cn.currency,
					cn.reason,
					cn.status,
					cn.created_at,
					i.serie AS invoice_serie
				FROM credit_notes cn
				JOIN invoices i ON cn.invoice_id = i.id
				ORDER BY cn.created_at DESC
				LIMIT 50
			`);
			return NextResponse.json(q.rows, {
				headers: { 'Cache-Control': 'public, max-age=60, stale-while-revalidate=120' },
			});
		} finally {
			client.release();
		}
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}


