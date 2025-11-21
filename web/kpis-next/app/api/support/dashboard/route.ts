/**
 * API de Dashboard para Tickets de Soporte
 * 
 * Proporciona datos agregados para visualización en dashboard
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
    const period = searchParams.get('period') || '24h'; // 24h, 7d, 30d

    let timeFilter = '';
    switch (period) {
      case '24h':
        timeFilter = "created_at >= NOW() - INTERVAL '24 hours'";
        break;
      case '7d':
        timeFilter = "created_at >= NOW() - INTERVAL '7 days'";
        break;
      case '30d':
        timeFilter = "created_at >= NOW() - INTERVAL '30 days'";
        break;
      default:
        timeFilter = "created_at >= NOW() - INTERVAL '24 hours'";
    }

    // Métricas principales
    const mainMetrics = await pool.query(`
      SELECT 
        COUNT(*) as total_tickets,
        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
        COUNT(*) FILTER (WHERE status IN ('open', 'assigned', 'in_progress')) as pending,
        COUNT(*) FILTER (WHERE priority IN ('critical', 'urgent')) as critical_urgent,
        AVG(time_to_first_response_minutes) FILTER (WHERE chatbot_resolved = false) as avg_first_response,
        AVG(time_to_resolution_minutes) FILTER (WHERE status = 'resolved') as avg_resolution
      FROM support_tickets
      WHERE ${timeFilter}
    `);

    // Tendencias (últimas 24 horas por hora)
    const trends = await pool.query(`
      SELECT 
        DATE_TRUNC('hour', created_at) as hour,
        COUNT(*) as ticket_count,
        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved_count
      FROM support_tickets
      WHERE ${timeFilter}
      GROUP BY DATE_TRUNC('hour', created_at)
      ORDER BY hour ASC
    `);

    // Distribución por prioridad (últimas 24h)
    const priorityDistribution = await pool.query(`
      SELECT 
        priority,
        COUNT(*) as count
      FROM support_tickets
      WHERE created_at >= NOW() - INTERVAL '24 hours'
      GROUP BY priority
      ORDER BY 
        CASE priority
          WHEN 'critical' THEN 1
          WHEN 'urgent' THEN 2
          WHEN 'high' THEN 3
          WHEN 'medium' THEN 4
          WHEN 'low' THEN 5
        END
    `);

    // Top categorías
    const topCategories = await pool.query(`
      SELECT 
        category,
        COUNT(*) as count
      FROM support_tickets
      WHERE ${timeFilter}
      AND category IS NOT NULL
      GROUP BY category
      ORDER BY count DESC
      LIMIT 5
    `);

    // Agentes más activos
    const topAgents = await pool.query(`
      SELECT 
        assigned_agent_name,
        COUNT(*) as tickets_handled,
        AVG(time_to_resolution_minutes) as avg_resolution_time,
        AVG(customer_satisfaction_score) as avg_satisfaction
      FROM support_tickets
      WHERE ${timeFilter}
      AND assigned_agent_name IS NOT NULL
      AND status = 'resolved'
      GROUP BY assigned_agent_name
      ORDER BY tickets_handled DESC
      LIMIT 5
    `);

    // Tasa de resolución por chatbot (últimas 24h)
    const chatbotStats = await pool.query(`
      SELECT 
        COUNT(*) FILTER (WHERE chatbot_attempted = true) as attempted,
        COUNT(*) FILTER (WHERE chatbot_resolved = true) as resolved,
        AVG(confidence) FILTER (WHERE chatbot_resolved = true) as avg_confidence
      FROM support_tickets
      WHERE created_at >= NOW() - INTERVAL '24 hours'
      AND chatbot_attempted = true
    `);

    // Feedback reciente
    const recentFeedback = await pool.query(`
      SELECT 
        f.ticket_id,
        f.satisfaction_score,
        f.feedback_text,
        f.submitted_at,
        t.subject,
        t.assigned_agent_name
      FROM support_ticket_feedback f
      INNER JOIN support_tickets t ON f.ticket_id = t.ticket_id
      WHERE f.submitted_at >= NOW() - INTERVAL '7 days'
      ORDER BY f.submitted_at DESC
      LIMIT 10
    `);

    const metrics = mainMetrics.rows[0];
    const chatbot = chatbotStats.rows[0];

    return NextResponse.json({
      period,
      metrics: {
        total_tickets: parseInt(metrics.total_tickets),
        chatbot_resolved: parseInt(metrics.chatbot_resolved),
        pending: parseInt(metrics.pending),
        critical_urgent: parseInt(metrics.critical_urgent),
        avg_first_response_minutes: parseFloat(metrics.avg_first_response) || null,
        avg_resolution_minutes: parseFloat(metrics.avg_resolution) || null,
        chatbot_resolution_rate: chatbot.attempted > 0 
          ? (parseInt(chatbot.resolved) / parseInt(chatbot.attempted) * 100).toFixed(2)
          : 0
      },
      trends: trends.rows.map(row => ({
        hour: row.hour,
        ticket_count: parseInt(row.ticket_count),
        chatbot_resolved_count: parseInt(row.chatbot_resolved_count)
      })),
      priority_distribution: priorityDistribution.rows.map(row => ({
        priority: row.priority,
        count: parseInt(row.count)
      })),
      top_categories: topCategories.rows.map(row => ({
        category: row.category,
        count: parseInt(row.count)
      })),
      top_agents: topAgents.rows.map(row => ({
        agent_name: row.assigned_agent_name,
        tickets_handled: parseInt(row.tickets_handled),
        avg_resolution_minutes: parseFloat(row.avg_resolution_time) || null,
        avg_satisfaction: parseFloat(row.avg_satisfaction) || null
      })),
      recent_feedback: recentFeedback.rows.map(row => ({
        ticket_id: row.ticket_id,
        satisfaction_score: parseInt(row.satisfaction_score),
        feedback_text: row.feedback_text,
        submitted_at: row.submitted_at,
        subject: row.subject,
        agent_name: row.assigned_agent_name
      }))
    });
  } catch (error: any) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Error fetching dashboard data', details: error.message },
      { status: 500 }
    );
  }
}

