/**
 * API REST para el Sistema de Troubleshooting Automatizado
 * 
 * Endpoints:
 * - POST /api/support/troubleshooting/start - Iniciar sesión de troubleshooting
 * - GET /api/support/troubleshooting/:sessionId - Obtener estado de sesión
 * - POST /api/support/troubleshooting/:sessionId/step - Completar paso
 * - POST /api/support/troubleshooting/:sessionId/escalate - Escalar ticket
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Iniciar sesión de troubleshooting
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      problem_description,
      customer_email,
      customer_name,
      ticket_id,
      source = 'web'
    } = body;

    // Validaciones
    if (!problem_description || !customer_email) {
      return NextResponse.json(
        { error: 'problem_description and customer_email are required' },
        { status: 400 }
      );
    }

    // Llamar al workflow de Kestra para iniciar troubleshooting
    const kestraWebhookUrl = process.env.KESTRA_WEBHOOK_URL;
    if (!kestraWebhookUrl) {
      return NextResponse.json(
        { error: 'Kestra webhook URL not configured' },
        { status: 500 }
      );
    }

    const kestraResponse = await fetch(
      `${kestraWebhookUrl}/workflows/workflows/support-troubleshooting-automation/support-troubleshooting`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_description,
          customer_email,
          customer_name,
          ticket_id,
          source
        })
      }
    );

    if (!kestraResponse.ok) {
      const errorText = await kestraResponse.text();
      console.error('Kestra webhook error:', errorText);
      return NextResponse.json(
        { error: 'Failed to start troubleshooting session', details: errorText },
        { status: 500 }
      );
    }

    const kestraResult = await kestraResponse.json();

    // Obtener información de la sesión desde la BD
    const sessionQuery = `
      SELECT * FROM support_troubleshooting_sessions
      WHERE session_id = $1
    `;
    const sessionResult = await pool.query(sessionQuery, [kestraResult.session_id]);

    if (sessionResult.rows.length === 0) {
      return NextResponse.json(
        { error: 'Session not found after creation' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      session_id: kestraResult.session_id,
      ticket_id: ticket_id,
      status: sessionResult.rows[0].status,
      problem_detected: sessionResult.rows[0].detected_problem_title,
      message: kestraResult.message || 'Troubleshooting session started',
      first_step: kestraResult.first_step
    });

  } catch (error: any) {
    console.error('Error starting troubleshooting session:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Obtener estado de sesión
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'session_id is required' },
        { status: 400 }
      );
    }

    // Obtener sesión desde BD
    const sessionQuery = `
      SELECT 
        s.*,
        COUNT(a.id) as total_attempts,
        COUNT(CASE WHEN a.success = true THEN 1 END) as successful_attempts,
        COUNT(CASE WHEN a.success = false THEN 1 END) as failed_attempts
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

    // Obtener intentos recientes
    const attemptsQuery = `
      SELECT * FROM support_troubleshooting_attempts
      WHERE session_id = $1
      ORDER BY attempted_at DESC
      LIMIT 10
    `;
    const attemptsResult = await pool.query(attemptsQuery, [sessionId]);

    return NextResponse.json({
      session: sessionResult.rows[0],
      attempts: attemptsResult.rows,
      summary: {
        total_attempts: parseInt(sessionResult.rows[0].total_attempts) || 0,
        successful_attempts: parseInt(sessionResult.rows[0].successful_attempts) || 0,
        failed_attempts: parseInt(sessionResult.rows[0].failed_attempts) || 0
      }
    });

  } catch (error: any) {
    console.error('Error getting troubleshooting session:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



