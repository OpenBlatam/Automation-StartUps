import { NextResponse } from 'next/server';
import { fetchSummary } from '@/lib/kpi';

export async function GET() {
	try {
		const data = await fetchSummary();
		return NextResponse.json(data, { headers: { 'Cache-Control': 'public, max-age=15, stale-while-revalidate=30' } });
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}
