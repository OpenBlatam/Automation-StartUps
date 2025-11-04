import { NextRequest, NextResponse } from 'next/server';
import { detectAnomalies, LLMProvider } from '@/lib/llm-enhanced';
import { fetchSummary, fetchRevenue24h } from '@/lib/kpi';

export const runtime = 'nodejs';
export const maxDuration = 30;

/**
 * GET /api/kpi/anomalies
 * Detect anomalies in KPI data
 * Query params: provider (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const provider = (searchParams.get('provider') || 'openai') as LLMProvider;

    const [summary, series] = await Promise.all([
      fetchSummary(),
      fetchRevenue24h(),
    ]);

    const currentData = {
      revenue_last_hour: summary.revenue_last_hour,
      revenue_24h: summary.revenue_24h,
      leads_count: summary.leads_by_priority_today.reduce((acc, l) => acc + l.count, 0),
    };

    const anomalies = await detectAnomalies(currentData, series, provider);

    return NextResponse.json({
      anomalies,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to detect anomalies' },
      { status: 500 }
    );
  }
}

