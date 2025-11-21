/**
 * API para obtener analytics y métricas de troubleshooting
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get('days') || '30');

    // Estadísticas generales
    const statsQuery = `
      SELECT * FROM get_troubleshooting_stats(
        NOW() - INTERVAL '${days} days',
        NOW()
      )
    `;
    const statsResult = await pool.query(statsQuery);

    // Distribución de problemas
    const problemDistQuery = `
      SELECT 
        detected_problem_id,
        detected_problem_title,
        COUNT(*) as total_sessions,
        COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
        COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated,
        ROUND(
          COUNT(CASE WHEN status = 'resolved' THEN 1 END)::NUMERIC / 
          COUNT(*)::NUMERIC * 100, 
          2
        ) as resolution_rate
      FROM support_troubleshooting_sessions
      WHERE started_at >= NOW() - INTERVAL '${days} days'
        AND detected_problem_id IS NOT NULL
      GROUP BY detected_problem_id, detected_problem_title
      ORDER BY total_sessions DESC
    `;
    const problemDistResult = await pool.query(problemDistQuery);

    // Pasos más problemáticos
    const failedStepsQuery = `
      SELECT 
        a.step_number,
        a.step_title,
        COUNT(*) as total_attempts,
        COUNT(CASE WHEN a.success = false THEN 1 END) as failed_attempts,
        ROUND(
          COUNT(CASE WHEN a.success = false THEN 1 END)::NUMERIC / 
          COUNT(*)::NUMERIC * 100, 
          2
        ) as failure_rate
      FROM support_troubleshooting_attempts a
      JOIN support_troubleshooting_sessions s ON a.session_id = s.session_id
      WHERE s.started_at >= NOW() - INTERVAL '${days} days'
      GROUP BY a.step_number, a.step_title
      HAVING COUNT(*) >= 3
      ORDER BY failure_rate DESC, failed_attempts DESC
      LIMIT 10
    `;
    const failedStepsResult = await pool.query(failedStepsQuery);

    // Feedback summary
    const feedbackQuery = `
      SELECT 
        COUNT(*) as total_feedback,
        AVG(rating)::NUMERIC(3,2) as average_rating,
        COUNT(CASE WHEN was_helpful = true THEN 1 END) as helpful_count,
        ROUND(
          COUNT(CASE WHEN was_helpful = true THEN 1 END)::NUMERIC / 
          COUNT(*)::NUMERIC * 100, 
          2
        ) as helpful_percentage,
        COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback_count
      FROM support_troubleshooting_feedback
      WHERE collected_at >= NOW() - INTERVAL '${days} days'
    `;
    const feedbackResult = await pool.query(feedbackQuery);

    // Feedback por problema
    const feedbackByProblemQuery = `
      SELECT * FROM get_feedback_by_problem(
        NOW() - INTERVAL '${days} days',
        NOW()
      )
    `;
    const feedbackByProblemResult = await pool.query(feedbackByProblemQuery);

    // Tendencias diarias
    const dailyTrendsQuery = `
      SELECT 
        DATE_TRUNC('day', started_at) as date,
        COUNT(*) as sessions,
        COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
        COUNT(CASE WHEN status = 'escalated' THEN 1 END) as escalated
      FROM support_troubleshooting_sessions
      WHERE started_at >= NOW() - INTERVAL '${days} days'
      GROUP BY DATE_TRUNC('day', started_at)
      ORDER BY date DESC
    `;
    const dailyTrendsResult = await pool.query(dailyTrendsQuery);

    return NextResponse.json({
      period_days: days,
      summary: statsResult.rows[0] || {},
      problem_distribution: problemDistResult.rows,
      common_failed_steps: failedStepsResult.rows,
      feedback_summary: feedbackResult.rows[0] || {},
      feedback_by_problem: feedbackByProblemResult.rows,
      daily_trends: dailyTrendsResult.rows,
      generated_at: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Error getting analytics:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



