/**
 * API para notificaciones de troubleshooting
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Enviar notificación
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      session_id,
      notification_type,
      recipient,
      subject,
      message,
      metadata = {}
    } = body;

    if (!session_id || !notification_type || !recipient || !message) {
      return NextResponse.json(
        { error: 'session_id, notification_type, recipient, and message are required' },
        { status: 400 }
      );
    }

    // Insertar notificación
    const insertQuery = `
      INSERT INTO support_troubleshooting_notifications (
        session_id,
        notification_type,
        recipient,
        subject,
        message,
        status,
        metadata,
        created_at
      ) VALUES ($1, $2, $3, $4, $5, 'pending', $6, NOW())
      RETURNING *
    `;
    const result = await pool.query(insertQuery, [
      session_id,
      notification_type,
      recipient,
      subject || null,
      message,
      JSON.stringify(metadata)
    ]);

    // Aquí integrarías con el servicio de notificaciones real
    // Por ahora, marcamos como enviada
    const updateQuery = `
      UPDATE support_troubleshooting_notifications
      SET status = 'sent', sent_at = NOW()
      WHERE id = $1
    `;
    await pool.query(updateQuery, [result.rows[0].id]);

    return NextResponse.json({
      success: true,
      notification: result.rows[0],
      message: 'Notification queued successfully'
    });

  } catch (error: any) {
    console.error('Error sending notification:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Obtener notificaciones de una sesión
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

    const query = `
      SELECT * FROM support_troubleshooting_notifications
      WHERE session_id = $1
      ORDER BY created_at DESC
    `;
    const result = await pool.query(query, [sessionId]);

    return NextResponse.json({
      notifications: result.rows
    });

  } catch (error: any) {
    console.error('Error getting notifications:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



