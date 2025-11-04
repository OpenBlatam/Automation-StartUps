/**
 * API de Estadísticas de Tickets de Soporte
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

    // Estadísticas generales
    const generalStats = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
        COUNT(*) FILTER (WHERE status = 'resolved') as manually_resolved,
        COUNT(*) FILTER (WHERE status IN ('open', 'assigned', 'in_progress')) as pending,
        COUNT(*) FILTER (WHERE priority = 'critical') as critical,
        COUNT(*) FILTER (WHERE priority = 'urgent') as urgent,
        AVG(priority_score) as avg_priority_score
      FROM support_tickets
      WHERE ${timeFilter}
    `);

    // Distribución por prioridad
    const priorityDistribution = await pool.query(`
      SELECT 
        priority,
        COUNT(*) as count,
        AVG(time_to_resolution_minutes) as avg_resolution_time
      FROM support_tickets
      WHERE ${timeFilter}
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

    // Distribución por categoría
    const categoryDistribution = await pool.query(`
      SELECT 
        category,
        COUNT(*) as count
      FROM support_tickets
      WHERE ${timeFilter}
      AND category IS NOT NULL
      GROUP BY category
      ORDER BY count DESC
    `);

    // Tiempos de respuesta
    const responseTimes = await pool.query(`
      SELECT 
        AVG(time_to_first_response_minutes) as avg_first_response,
        AVG(time_to_resolution_minutes) as avg_resolution,
        COUNT(*) FILTER (WHERE first_response_at IS NOT NULL) as responded_count
      FROM support_tickets
      WHERE ${timeFilter}
      AND chatbot_resolved = false
    `);

    // Tasa de resolución por chatbot
    const chatbotRate = await pool.query(`
      SELECT 
        COUNT(*) FILTER (WHERE chatbot_attempted = true) as attempted,
        COUNT(*) FILTER (WHERE chatbot_resolved = true) as resolved,
        AVG(confidence) FILTER (WHERE chatbot_resolved = true) as avg_confidence
      FROM support_tickets
      WHERE ${timeFilter}
      AND chatbot_attempted = true
    `);

    // Top agentes
    const topAgents = await pool.query(`
      SELECT 
        assigned_agent_name,
        COUNT(*) as tickets_resolved,
        AVG(time_to_resolution_minutes) as avg_resolution_time
      FROM support_tickets
      WHERE ${timeFilter}
      AND assigned_agent_name IS NOT NULL
      AND status = 'resolved'
      GROUP BY assigned_agent_name
      ORDER BY tickets_resolved DESC
      LIMIT 5
    `);

    const stats = generalStats.rows[0];
    const chatbotStats = chatbotRate.rows[0];

    return NextResponse.json({
      period,
      general: {
        total: parseInt(stats.total),
        chatbot_resolved: parseInt(stats.chatbot_resolved),
        manually_resolved: parseInt(stats.manually_resolved),
        pending: parseInt(stats.pending),
        critical: parseInt(stats.critical),
        urgent: parseInt(stats.urgent),
        avg_priority_score: parseFloat(stats.avg_priority_score) || 0
      },
      chatbot: {
        attempted: parseInt(chatbotStats.attempted) || 0,
        resolved: parseInt(chatbotStats.resolved) || 0,
        resolution_rate: chatbotStats.attempted > 0 
          ? (parseInt(chatbotStats.resolved) / parseInt(chatbotStats.attempted) * 100).toFixed(2)
          : 0,
        avg_confidence: parseFloat(chatbotStats.avg_confidence) || 0
      },
      response_times: {
        avg_first_response_minutes: parseFloat(responseTimes.rows[0].avg_first_response) || null,
        avg_resolution_minutes: parseFloat(responseTimes.rows[0].avg_resolution) || null,
        responded_count: parseInt(responseTimes.rows[0].responded_count) || 0
      },
      priority_distribution: priorityDistribution.rows.map(row => ({
        priority: row.priority,
        count: parseInt(row.count),
        avg_resolution_minutes: parseFloat(row.avg_resolution_time) || null
      })),
      category_distribution: categoryDistribution.rows.map(row => ({
        category: row.category,
        count: parseInt(row.count)
      })),
      top_agents: topAgents.rows.map(row => ({
        agent_name: row.assigned_agent_name,
        tickets_resolved: parseInt(row.tickets_resolved),
        avg_resolution_minutes: parseFloat(row.avg_resolution_time) || null
      }))
    });
  } catch (error: any) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Error fetching stats', details: error.message },
      { status: 500 }
    );
  }
}

