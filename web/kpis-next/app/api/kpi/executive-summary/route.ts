import { NextRequest, NextResponse } from 'next/server';
import { generateExecutiveSummary, LLMProvider } from '@/lib/llm-enhanced';
import { fetchSummary, fetchRevenue24h, fetchAging, fetchRevenue } from '@/lib/kpi';

export const runtime = 'nodejs';
export const maxDuration = 30;

/**
 * GET /api/kpi/executive-summary
 * Generate executive summary of KPIs
 * Query params: provider (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const provider = (searchParams.get('provider') || 'openai') as LLMProvider;

    const [summary, series, aging, revenue] = await Promise.all([
      fetchSummary(),
      fetchRevenue24h(),
      fetchAging(),
      fetchRevenue('daily'),
    ]);

    const kpiData = {
      summary,
      timeseries_24h: series,
      aging_buckets: aging,
      revenue: revenue,
    };

    const summaryText = await generateExecutiveSummary(kpiData, provider);

    return NextResponse.json({
      summary: summaryText,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to generate executive summary' },
      { status: 500 }
    );
  }
}

