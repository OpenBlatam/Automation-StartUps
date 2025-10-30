import { NextResponse } from 'next/server';
import { fetchRevenue24h } from '@/lib/kpi';

export async function GET() {
	try {
		const data = await fetchRevenue24h();
		return NextResponse.json(data, { headers: { 'Cache-Control': 'public, max-age=15, stale-while-revalidate=30' } });
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}
