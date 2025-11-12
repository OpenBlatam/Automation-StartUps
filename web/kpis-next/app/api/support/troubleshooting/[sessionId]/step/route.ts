/**
 * API para completar un paso de troubleshooting
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
    const { success, notes, step_number, step_title } = body;

    if (success === undefined) {
      return NextResponse.json(
        { error: 'success field is required' },
        { status: 400 }
      );
    }

    // Obtener sesión actual
    const sessionQuery = `
      SELECT * FROM support_troubleshooting_sessions
      WHERE session_id = $1
    `;
    const sessionResult = await pool.query(sessionQuery, [sessionId]);

    if (sessionResult.rows.length === 0) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    const session = sessionResult.rows[0];

    // Registrar intento
    const insertAttemptQuery = `
      INSERT INTO support_troubleshooting_attempts (
        session_id,
        step_number,
        step_title,
        success,
        notes
      ) VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    const attemptResult = await pool.query(insertAttemptQuery, [
      sessionId,
      step_number || session.current_step + 1,
      step_title || `Step ${step_number || session.current_step + 1}`,
      success,
      notes || null
    ]);

    // Actualizar sesión
    let newStatus = session.status;
    let newCurrentStep = session.current_step;

    if (success) {
      newCurrentStep = Math.min(newCurrentStep + 1, session.total_steps);
      if (newCurrentStep >= session.total_steps) {
        newStatus = 'resolved';
      } else {
        newStatus = 'in_progress';
      }
    } else {
      // Verificar si debe escalar (más de 2 fallos)
      const failedAttemptsQuery = `
        SELECT COUNT(*) as failed_count
        FROM support_troubleshooting_attempts
        WHERE session_id = $1 AND success = false
      `;
      const failedResult = await pool.query(failedAttemptsQuery, [sessionId]);
      const failedCount = parseInt(failedResult.rows[0].failed_count) || 0;

      if (failedCount >= 2) {
        newStatus = 'needs_escalation';
      }
    }

    const updateSessionQuery = `
      UPDATE support_troubleshooting_sessions
      SET
        status = $1,
        current_step = $2,
        updated_at = NOW()
      WHERE session_id = $3
      RETURNING *
    `;
    const updateResult = await pool.query(updateSessionQuery, [
      newStatus,
      newCurrentStep,
      sessionId
    ]);

    // Determinar siguiente acción
    let nextAction = 'continue';
    let message = success 
      ? 'Paso completado exitosamente. Continuando con el siguiente paso.'
      : 'El paso no se completó exitosamente. Revisa las instrucciones.';

    if (newStatus === 'resolved') {
      nextAction = 'resolved';
      message = '¡Excelente! Has completado todos los pasos. El problema debería estar resuelto.';
    } else if (newStatus === 'needs_escalation') {
      nextAction = 'escalate';
      message = 'Múltiples pasos fallaron. Se recomienda escalar este ticket a un agente humano.';
    }

    return NextResponse.json({
      success: true,
      attempt: attemptResult.rows[0],
      session: updateResult.rows[0],
      next_action: nextAction,
      message: message,
      suggest_escalation: newStatus === 'needs_escalation'
    });

  } catch (error: any) {
    console.error('Error completing troubleshooting step:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



