import { NextRequest, NextResponse } from 'next/server';
import { generateReport, LLMProvider } from '@/lib/llm';
import { fetchSummary, fetchRevenue24h, fetchAging, fetchRevenue } from '@/lib/kpi';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * GET /api/kpi/report
 * Generate comprehensive report from KPIs
 * Query params: type (daily|weekly|monthly|custom), provider (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const reportType = (searchParams.get('type') || 'daily') as 'daily' | 'weekly' | 'monthly' | 'custom';
    const provider = (searchParams.get('provider') || 'openai') as LLMProvider;

    // Fetch all KPI data
    const [summary, series, aging, revenue] = await Promise.all([
      fetchSummary(),
      fetchRevenue24h(),
      fetchAging(),
      fetchRevenue(reportType === 'monthly' ? 'monthly' : 'daily'),
    ]);

    const kpiData = {
      summary,
      timeseries_24h: series,
      aging_buckets: aging,
      revenue: revenue,
      report_type: reportType,
      generated_at: new Date().toISOString(),
    };

    const report = await generateReport(kpiData, reportType, provider);
    return NextResponse.json({
      report,
      type: reportType,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to generate report' },
      { status: 500 }
    );
  }
}


