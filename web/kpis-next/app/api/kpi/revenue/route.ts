import { NextResponse } from 'next/server';
import { fetchRevenue } from '@/lib/kpi';

export async function GET(request: Request) {
	try {
		const { searchParams } = new URL(request.url);
		const period = searchParams.get('period') || 'daily'; // daily, monthly
		const data = await fetchRevenue(period);
		return NextResponse.json(data, {
			headers: { 'Cache-Control': 'public, max-age=300, stale-while-revalidate=600' },
		});
	} catch (e: any) {
		return NextResponse.json({ error: e.message || 'error' }, { status: 500 });
	}
}


