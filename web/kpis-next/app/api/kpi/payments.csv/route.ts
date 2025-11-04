import { NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export async function GET() {
	const client = await pool.connect();
	try {
		const q = await client.query(
			"SELECT created_at, payment_id, amount, currency, customer, status, method FROM payments ORDER BY created_at DESC LIMIT 500"
		);
		const header = ['created_at','payment_id','amount','currency','customer','status','method'];
		const lines = [header.join(',')].concat(q.rows.map(r => header.map(h => {
			const v = r[h];
			if (v === null || v === undefined) return '';
			const s = String(v).replace(/"/g,'""');
			return /[",\n]/.test(s) ? `"${s}"` : s;
		}).join(',')));
		const body = lines.join('\n');
		return new NextResponse(body, { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	} finally {
		client.release();
	}
}


