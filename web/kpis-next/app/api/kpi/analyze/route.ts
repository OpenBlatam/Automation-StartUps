import { NextRequest, NextResponse } from 'next/server';
import { analyzeKPIs, generateAutoInsights, LLMProvider } from '@/lib/llm';
import { fetchSummary, fetchRevenue24h } from '@/lib/kpi';

export const runtime = 'nodejs';

/**
 * POST /api/kpi/analyze
 * Analyze KPI data with LLM
 * Body: { data: any, context?: string, provider?: 'openai' | 'deepseek' }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { data, context, provider } = body;

    if (!data) {
      return NextResponse.json(
        { error: 'Data is required' },
        { status: 400 }
      );
    }

    const insight = await analyzeKPIs(data, context, provider as LLMProvider);
    return NextResponse.json({ insight });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to analyze data' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/kpi/analyze
 * Generate automatic insights from current KPIs
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

    const insight = await generateAutoInsights(summary, series, provider);
    return NextResponse.json({
      insight,
      timestamp: new Date().toISOString(),
      summary: {
        revenue_last_hour: summary.revenue_last_hour,
        revenue_24h: summary.revenue_24h,
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to generate insights' },
      { status: 500 }
    );
  }
}


