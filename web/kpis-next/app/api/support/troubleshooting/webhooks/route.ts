/**
 * API para gestionar webhooks de troubleshooting
 */

import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Registrar webhook
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url, events, secret, headers, timeout, retry_attempts } = body;

    if (!url || !events || !Array.isArray(events) || events.length === 0) {
      return NextResponse.json(
        { error: 'url and events (array) are required' },
        { status: 400 }
      );
    }

    // Validar URL
    try {
      new URL(url);
    } catch {
      return NextResponse.json(
        { error: 'Invalid URL format' },
        { status: 400 }
      );
    }

    // Generar webhook_id
    const webhook_id = `wh_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Guardar en BD (asumiendo tabla support_webhooks)
    const insertQuery = `
      INSERT INTO support_webhooks (
        webhook_id,
        url,
        events,
        secret,
        headers,
        timeout,
        retry_attempts,
        enabled,
        created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, true, NOW())
      RETURNING *
    `;
    const result = await pool.query(insertQuery, [
      webhook_id,
      url,
      JSON.stringify(events),
      secret || null,
      JSON.stringify(headers || {}),
      timeout || 10,
      retry_attempts || 3
    ]);

    return NextResponse.json({
      success: true,
      webhook_id: webhook_id,
      webhook: result.rows[0],
      message: 'Webhook registrado exitosamente'
    });

  } catch (error: any) {
    console.error('Error registering webhook:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

// Listar webhooks
export async function GET(request: NextRequest) {
  try {
    const query = `
      SELECT 
        webhook_id,
        url,
        events,
        enabled,
        created_at,
        updated_at
      FROM support_webhooks
      ORDER BY created_at DESC
    `;
    const result = await pool.query(query);

    return NextResponse.json({
      webhooks: result.rows.map(row => ({
        ...row,
        events: typeof row.events === 'string' ? JSON.parse(row.events) : row.events
      }))
    });

  } catch (error: any) {
    console.error('Error listing webhooks:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}



