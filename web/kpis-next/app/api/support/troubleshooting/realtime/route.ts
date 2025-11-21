/**
 * API para métricas en tiempo real
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

export async function GET(request: NextRequest) {
  try {
    // Obtener métricas en tiempo real
    const metricsQuery = `
      SELECT * FROM vw_troubleshooting_realtime_metrics
    `;
    const metricsResult = await pool.query(metricsQuery);

    // Obtener problemas más comunes últimas 24h
    const topProblemsQuery = `
      SELECT 
        detected_problem_id,
        detected_problem_title,
        COUNT(*) as count,
        COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count
      FROM support_troubleshooting_sessions
      WHERE started_at >= NOW() - INTERVAL '24 hours'
        AND detected_problem_id IS NOT NULL
      GROUP BY detected_problem_id, detected_problem_title
      ORDER BY count DESC
      LIMIT 5
    `;
    const topProblemsResult = await pool.query(topProblemsQuery);

    // Obtener sesiones activas recientes
    const activeSessionsQuery = `
      SELECT 
        session_id,
        customer_email,
        detected_problem_title,
        current_step,
        total_steps,
        status,
        started_at
      FROM support_troubleshooting_sessions
      WHERE status IN ('started', 'in_progress')
        AND started_at >= NOW() - INTERVAL '1 hour'
      ORDER BY started_at DESC
      LIMIT 10
    `;
    const activeSessionsResult = await pool.query(activeSessionsQuery);

    return NextResponse.json({
      timestamp: new Date().toISOString(),
      metrics: metricsResult.rows[0] || {},
      top_problems: topProblemsResult.rows,
      active_sessions: activeSessionsResult.rows
    });

  } catch (error: any) {
    console.error('Error getting realtime metrics:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



