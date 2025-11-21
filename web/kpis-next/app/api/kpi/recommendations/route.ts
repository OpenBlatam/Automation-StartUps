import { NextRequest, NextResponse } from 'next/server';
import { generateRecommendations, detectAnomalies, LLMProvider } from '@/lib/llm-enhanced';
import { fetchSummary, fetchRevenue24h } from '@/lib/kpi';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * GET /api/kpi/recommendations
 * Generate actionable recommendations based on KPIs
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

    // First detect anomalies
    const anomalies = await detectAnomalies(currentData, series, provider);

    // Then generate recommendations based on data and anomalies
    const recommendations = await generateRecommendations(
      { summary, series, anomalies },
      anomalies,
      provider
    );

    return NextResponse.json({
      recommendations,
      anomalies_count: anomalies.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to generate recommendations' },
      { status: 500 }
    );
  }
}

