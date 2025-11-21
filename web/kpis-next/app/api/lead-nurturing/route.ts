import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

export const maxDuration = 60;

/**
 * GET /api/lead-nurturing
 * Obtiene métricas de lead nurturing en tiempo real
 * Query params:
 *   - period: 'today' | 'week' | 'month' | 'all' (default: 'week')
 *   - metric: 'summary' | 'sequences' | 'engagement' | 'cohorts' (default: 'summary')
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || 'week';
    const metric = searchParams.get('metric') || 'summary';

    let query = '';
    let params: any[] = [];

    switch (metric) {
      case 'summary':
        // Resumen general
        const daysMap: Record<string, number> = {
          today: 1,
          week: 7,
          month: 30,
          all: 365
        };
        const days = daysMap[period] || 7;

        query = `
          SELECT 
            COUNT(DISTINCT s.id) as total_sequences,
            COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
            COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'active') as active,
            COUNT(DISTINCT e.id) as total_emails_sent,
            COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as emails_opened,
            COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as emails_replied,
            ROUND(
              COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END)::NUMERIC / 
              NULLIF(COUNT(DISTINCT s.id), 0) * 100, 
              2
            ) as conversion_rate,
            ROUND(
              COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END)::NUMERIC / 
              NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
              2
            ) as open_rate,
            ROUND(
              COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END)::NUMERIC / 
              NULLIF(COUNT(DISTINCT e.id), 0) * 100, 
              2
            ) as reply_rate,
            AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days_to_qualify
          FROM lead_nurturing_sequences s
          LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
          WHERE s.started_at >= CURRENT_DATE - INTERVAL '${days} days'
        `;
        break;

      case 'sequences':
        // Secuencias activas
        query = `
          SELECT 
            s.id,
            l.email,
            l.first_name,
            s.current_step,
            s.total_steps,
            s.status,
            s.next_send_at,
            s.completion_rate,
            s.qualified_at
          FROM lead_nurturing_sequences s
          JOIN leads l ON s.lead_ext_id = l.ext_id
          WHERE s.status = 'active'
          ORDER BY s.next_send_at ASC
          LIMIT 50
        `;
        break;

      case 'engagement':
        // Engagement agregado
        query = `
          SELECT 
            es.sequence_id,
            l.email,
            es.total_emails_sent,
            es.total_emails_opened,
            es.total_emails_replied,
            es.open_rate,
            es.reply_rate,
            es.engagement_score
          FROM lead_nurturing_engagement_summary es
          JOIN lead_nurturing_sequences s ON es.sequence_id = s.id
          JOIN leads l ON es.lead_ext_id = l.ext_id
          WHERE s.status IN ('active', 'qualified')
          ORDER BY es.engagement_score DESC
          LIMIT 50
        `;
        break;

      case 'cohorts':
        // Análisis de cohorts
        const cohortDays = period === 'all' ? 90 : period === 'month' ? 30 : 7;
        query = `
          SELECT 
            DATE_TRUNC('week', s.started_at) as cohort_week,
            COUNT(DISTINCT s.id) as total_sequences,
            COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
            ROUND(
              COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END)::NUMERIC / 
              NULLIF(COUNT(DISTINCT s.id), 0) * 100, 
              2
            ) as conversion_rate
          FROM lead_nurturing_sequences s
          WHERE s.started_at >= CURRENT_DATE - INTERVAL '${cohortDays} days'
          GROUP BY DATE_TRUNC('week', s.started_at)
          ORDER BY cohort_week DESC
        `;
        break;

      default:
        return NextResponse.json(
          { error: 'Invalid metric parameter' },
          { status: 400 }
        );
    }

    const result = await db.query(query, params);
    
    return NextResponse.json({
      metric,
      period,
      data: result.rows,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('Error fetching lead nurturing metrics:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch metrics' },
      { status: 500 }
    );
  }
}

