import { NextResponse } from 'next/server';
import { fetchAging } from '@/lib/kpi';

export async function GET() {
	try {
		const data = await fetchAging();
		return NextResponse.json(data, {
			headers: { 'Cache-Control': 'public, max-age=60, stale-while-revalidate=120' },
		});
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}


