/**
 * API para Feedback de Tickets de Soporte
 */
import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      ticket_id,
      customer_email,
      satisfaction_score,
      response_time_rating,
      resolution_quality_rating,
      feedback_text,
      positive_aspects,
      improvement_suggestions,
      would_recommend,
      chatbot_was_helpful,
      agent_was_helpful
    } = body;

    // Validaciones
    if (!ticket_id || !customer_email || !satisfaction_score) {
      return NextResponse.json(
        { error: 'ticket_id, customer_email, and satisfaction_score are required' },
        { status: 400 }
      );
    }

    if (satisfaction_score < 1 || satisfaction_score > 5) {
      return NextResponse.json(
        { error: 'satisfaction_score must be between 1 and 5' },
        { status: 400 }
      );
    }

    // Verificar que el ticket existe y pertenece al cliente
    const ticketCheck = await pool.query(
      'SELECT ticket_id, customer_email, status FROM support_tickets WHERE ticket_id = $1',
      [ticket_id]
    );

    if (ticketCheck.rows.length === 0) {
      return NextResponse.json(
        { error: 'Ticket not found' },
        { status: 404 }
      );
    }

    if (ticketCheck.rows[0].customer_email.toLowerCase() !== customer_email.toLowerCase()) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 403 }
      );
    }

    // Insertar o actualizar feedback
    const query = `
      INSERT INTO support_ticket_feedback (
        ticket_id,
        customer_email,
        satisfaction_score,
        response_time_rating,
        resolution_quality_rating,
        feedback_text,
        positive_aspects,
        improvement_suggestions,
        would_recommend,
        chatbot_was_helpful,
        agent_was_helpful,
        submitted_via
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'api')
      ON CONFLICT (ticket_id, customer_email) 
      DO UPDATE SET
        satisfaction_score = EXCLUDED.satisfaction_score,
        response_time_rating = EXCLUDED.response_time_rating,
        resolution_quality_rating = EXCLUDED.resolution_quality_rating,
        feedback_text = EXCLUDED.feedback_text,
        positive_aspects = EXCLUDED.positive_aspects,
        improvement_suggestions = EXCLUDED.improvement_suggestions,
        would_recommend = EXCLUDED.would_recommend,
        chatbot_was_helpful = EXCLUDED.chatbot_was_helpful,
        agent_was_helpful = EXCLUDED.agent_was_helpful,
        submitted_at = NOW()
      RETURNING id, submitted_at
    `;

    const result = await pool.query(query, [
      ticket_id,
      customer_email,
      satisfaction_score,
      response_time_rating || null,
      resolution_quality_rating || null,
      feedback_text || null,
      positive_aspects || null,
      improvement_suggestions || null,
      would_recommend || null,
      chatbot_was_helpful || null,
      agent_was_helpful || null
    ]);

    // Actualizar satisfacción en ticket
    await pool.query(
      `UPDATE support_tickets 
       SET customer_satisfaction_score = $1 
       WHERE ticket_id = $2`,
      [satisfaction_score, ticket_id]
    );

    return NextResponse.json({
      id: result.rows[0].id,
      ticket_id,
      submitted_at: result.rows[0].submitted_at,
      message: 'Feedback submitted successfully'
    }, { status: 201 });
  } catch (error: any) {
    console.error('Error submitting feedback:', error);
    return NextResponse.json(
      { error: 'Error submitting feedback', details: error.message },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const ticket_id = searchParams.get('ticket_id');
    const customer_email = searchParams.get('customer_email');

    if (!ticket_id || !customer_email) {
      return NextResponse.json(
        { error: 'ticket_id and customer_email are required' },
        { status: 400 }
      );
    }

    const result = await pool.query(
      `SELECT * FROM support_ticket_feedback 
       WHERE ticket_id = $1 AND customer_email = $2`,
      [ticket_id, customer_email]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: 'Feedback not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(result.rows[0]);
  } catch (error: any) {
    console.error('Error fetching feedback:', error);
    return NextResponse.json(
      { error: 'Error fetching feedback', details: error.message },
      { status: 500 }
    );
  }
}

