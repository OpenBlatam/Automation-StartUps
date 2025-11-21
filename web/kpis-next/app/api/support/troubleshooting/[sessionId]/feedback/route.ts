/**
 * API para recolectar feedback de sesiones de troubleshooting
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

export async function POST(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId;
    const body = await request.json();
    const { rating, feedback_text, was_helpful } = body;

    // Validaciones
    if (!rating || rating < 1 || rating > 5) {
      return NextResponse.json(
        { error: 'rating is required and must be between 1 and 5' },
        { status: 400 }
      );
    }

    // Obtener información de la sesión
    const sessionQuery = `
      SELECT 
        s.*,
        COUNT(a.id) as total_attempts,
        COUNT(CASE WHEN a.success = true THEN 1 END) as successful_attempts
      FROM support_troubleshooting_sessions s
      LEFT JOIN support_troubleshooting_attempts a ON s.session_id = a.session_id
      WHERE s.session_id = $1
      GROUP BY s.id
    `;
    const sessionResult = await pool.query(sessionQuery, [sessionId]);

    if (sessionResult.rows.length === 0) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    const session = sessionResult.rows[0];

    // Insertar feedback
    const insertFeedbackQuery = `
      INSERT INTO support_troubleshooting_feedback (
        session_id,
        ticket_id,
        customer_email,
        rating,
        feedback_text,
        was_helpful,
        problem_detected_id,
        total_steps,
        completed_steps,
        resolved
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;
    const feedbackResult = await pool.query(insertFeedbackQuery, [
      sessionId,
      session.ticket_id,
      session.customer_email,
      rating,
      feedback_text || null,
      was_helpful !== undefined ? was_helpful : null,
      session.detected_problem_id,
      session.total_steps,
      session.current_step,
      session.status === 'resolved'
    ]);

    return NextResponse.json({
      success: true,
      feedback: feedbackResult.rows[0],
      message: 'Feedback recibido. ¡Gracias por tu opinión!'
    });

  } catch (error: any) {
    console.error('Error collecting feedback:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Obtener feedback de una sesión
export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const sessionId = params.sessionId;

    const feedbackQuery = `
      SELECT * FROM support_troubleshooting_feedback
      WHERE session_id = $1
      ORDER BY collected_at DESC
      LIMIT 1
    `;
    const feedbackResult = await pool.query(feedbackQuery, [sessionId]);

    if (feedbackResult.rows.length === 0) {
      return NextResponse.json(
        { error: 'Feedback not found for this session' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      feedback: feedbackResult.rows[0]
    });

  } catch (error: any) {
    console.error('Error getting feedback:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



