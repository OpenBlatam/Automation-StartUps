import { NextRequest, NextResponse } from 'next/server';
import { pool } from '@/lib/db';

export const maxDuration = 30;

interface QueryParams {
  metric?: string; // 'revenue' | 'leads' | 'conversion_pct' | 'payments_success_rate'
  start_date?: string; // ISO date or 'today' | '7d' | '30d' | '90d'
  end_date?: string;
  country?: string;
  source?: string;
  aggregate?: string; // 'daily' | 'weekly' | 'monthly'
  limit?: string;
}

/**
 * GET /api/kpi/query
 * Advanced KPI query API with filtering and aggregation
 * 
 * Query params:
 * - metric: revenue | leads | conversion_pct | payments_success_rate (default: all)
 * - start_date: ISO date or 'today' | '7d' | '30d' | '90d' (default: '7d')
 * - end_date: ISO date (default: today)
 * - country: filter by country
 * - source: filter by source
 * - aggregate: daily | weekly | monthly (default: daily)
 * - limit: max rows (default: 1000)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const params: QueryParams = {
      metric: searchParams.get('metric') || undefined,
      start_date: searchParams.get('start_date') || '7d',
      end_date: searchParams.get('end_date') || undefined,
      country: searchParams.get('country') || undefined,
      source: searchParams.get('source') || undefined,
      aggregate: searchParams.get('aggregate') || 'daily',
      limit: searchParams.get('limit') || '1000',
    };

    // Parse date ranges
    const endDate = params.end_date 
      ? new Date(params.end_date)
      : new Date();
    
    let startDate: Date;
    if (params.start_date === 'today') {
      startDate = new Date();
      startDate.setHours(0, 0, 0, 0);
    } else if (params.start_date === '7d') {
      startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 7);
    } else if (params.start_date === '30d') {
      startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 30);
    } else if (params.start_date === '90d') {
      startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 90);
    } else {
      startDate = new Date(params.start_date!);
    }

    const client = await pool.connect();
    try {
      let sql: string;
      let queryParams: any[] = [];

      // Determine which view to use
      const useSegment = params.country || params.source;
      const viewName = useSegment ? 'mv_kpi_daily_segment' : 'mv_kpi_daily';

      // Build WHERE clause
      const whereClauses: string[] = ['day >= $1::date', 'day <= $2::date'];
      queryParams.push(startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]);
      
      let paramIndex = 3;
      if (params.country && params.country !== 'All' && params.country !== 'unknown') {
        whereClauses.push(`country = $${paramIndex}`);
        queryParams.push(params.country);
        paramIndex++;
      }
      if (params.source && params.source !== 'All' && params.source !== 'unknown') {
        whereClauses.push(`source = $${paramIndex}`);
        queryParams.push(params.source);
        paramIndex++;
      }

      // Determine aggregation
      let dateTrunc: string;
      if (params.aggregate === 'weekly') {
        dateTrunc = "date_trunc('week', day)";
      } else if (params.aggregate === 'monthly') {
        dateTrunc = "date_trunc('month', day)";
      } else {
        dateTrunc = 'day';
      }

      // Select columns based on metric
      let selectCols: string[];
      if (params.metric === 'revenue') {
        selectCols = ['day', 'SUM(revenue) AS value'];
      } else if (params.metric === 'leads') {
        selectCols = ['day', 'SUM(leads) AS value'];
      } else if (params.metric === 'conversion_pct') {
        selectCols = ['day', 'AVG(conversion_pct) AS value'];
      } else if (params.metric === 'payments_success_rate') {
        selectCols = ['day', 'AVG(payments_success_rate) AS value'];
      } else {
        // All metrics
        selectCols = ['day', 'SUM(leads) AS leads', 'AVG(conversion_pct) AS conversion_pct', 
                      'SUM(revenue) AS revenue', 'SUM(payments_count) AS payments_count',
                      'AVG(payments_success_rate) AS payments_success_rate'];
        if (useSegment) {
          selectCols.push('country', 'source');
        }
      }

      // Build SQL
      if (params.aggregate !== 'daily' || params.metric) {
        // Aggregated query
        const groupByCols = useSegment && params.metric ? ['country', 'source'] : [];
        sql = `
          SELECT ${dateTrunc}::date AS day,
                 ${selectCols.slice(1).join(', ')}
          FROM ${viewName}
          WHERE ${whereClauses.join(' AND ')}
          GROUP BY ${dateTrunc}${groupByCols.length ? ', ' + groupByCols.join(', ') : ''}
          ORDER BY day DESC
          LIMIT $${paramIndex}
        `;
        queryParams.push(parseInt(params.limit || '1000'));
      } else {
        // Simple select
        sql = `
          SELECT ${selectCols.join(', ')}
          ${useSegment ? ', country, source' : ''}
          FROM ${viewName}
          WHERE ${whereClauses.join(' AND ')}
          ORDER BY day DESC
          LIMIT $${paramIndex}
        `;
        queryParams.push(parseInt(params.limit || '1000'));
      }

      const result = await client.query(sql, queryParams);
      
      return NextResponse.json({
        data: result.rows,
        params,
        count: result.rows.length,
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      }, {
        headers: {
          'Cache-Control': 'public, max-age=60, stale-while-revalidate=120',
        },
      });
    } finally {
      client.release();
    }
  } catch (error: any) {
    console.error('KPI query error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to query KPIs' },
      { status: 500 }
    );
  }
}
