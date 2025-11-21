/**
 * API REST para Tickets de Soporte
 * 
 * Endpoints:
 * - GET /api/support/tickets - Listar tickets
 * - POST /api/support/tickets - Crear ticket
 * - GET /api/support/tickets/[id] - Obtener ticket
 * - PUT /api/support/tickets/[id] - Actualizar ticket
 * - GET /api/support/tickets/stats - Estadísticas
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
    const status = searchParams.get('status');
    const priority = searchParams.get('priority');
    const department = searchParams.get('department');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');

    let query = `
      SELECT 
        ticket_id,
        subject,
        description,
        customer_email,
        customer_name,
        category,
        priority,
        priority_score,
        status,
        assigned_department,
        assigned_agent_name,
        chatbot_resolved,
        created_at,
        updated_at,
        first_response_at,
        resolved_at
      FROM support_tickets
      WHERE 1=1
    `;
    const params: any[] = [];
    let paramCount = 0;

    if (status) {
      paramCount++;
      query += ` AND status = $${paramCount}`;
      params.push(status);
    }

    if (priority) {
      paramCount++;
      query += ` AND priority = $${paramCount}`;
      params.push(priority);
    }

    if (department) {
      paramCount++;
      query += ` AND assigned_department = $${paramCount}`;
      params.push(department);
    }

    query += ` ORDER BY created_at DESC LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
    params.push(limit, offset);

    const result = await pool.query(query, params);

    // Obtener total para paginación
    const countQuery = `
      SELECT COUNT(*) as total
      FROM support_tickets
      WHERE 1=1
      ${status ? `AND status = '${status}'` : ''}
      ${priority ? `AND priority = '${priority}'` : ''}
      ${department ? `AND assigned_department = '${department}'` : ''}
    `;
    const countResult = await pool.query(countQuery);
    const total = parseInt(countResult.rows[0].total);

    return NextResponse.json({
      tickets: result.rows,
      pagination: {
        total,
        limit,
        offset,
        hasMore: offset + limit < total
      }
    });
  } catch (error: any) {
    console.error('Error fetching tickets:', error);
    return NextResponse.json(
      { error: 'Error fetching tickets', details: error.message },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      subject,
      description,
      customer_email,
      customer_name,
      source = 'api',
      category,
      tags = [],
      metadata = {}
    } = body;

    // Validaciones básicas
    if (!description || !customer_email) {
      return NextResponse.json(
        { error: 'description and customer_email are required' },
        { status: 400 }
      );
    }

    // Generar ticket_id
    const ticket_id = `TKT-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;

    // Insertar ticket (el workflow de Kestra calculará prioridad y enrutará)
    const query = `
      INSERT INTO support_tickets (
        ticket_id,
        source,
        subject,
        description,
        customer_email,
        customer_name,
        category,
        tags,
        metadata,
        status,
        priority
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'open', 'medium')
      RETURNING ticket_id, created_at
    `;

    const result = await pool.query(query, [
      ticket_id,
      source,
      subject || null,
      description,
      customer_email,
      customer_name || null,
      category || null,
      tags,
      JSON.stringify(metadata)
    ]);

    // Disparar webhook de Kestra para procesamiento automático
    if (process.env.KESTRA_WEBHOOK_URL) {
      try {
        await fetch(`${process.env.KESTRA_WEBHOOK_URL}/workflows/support_ticket_automation/support-ticket`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ticket_id,
            subject,
            description,
            customer_email,
            customer_name,
            source: 'api',
            category,
            tags,
            metadata
          })
        });
      } catch (webhookError) {
        console.error('Error calling Kestra webhook:', webhookError);
        // No fallar si el webhook falla
      }
    }

    return NextResponse.json({
      ticket_id: result.rows[0].ticket_id,
      created_at: result.rows[0].created_at,
      message: 'Ticket created successfully'
    }, { status: 201 });
  } catch (error: any) {
    console.error('Error creating ticket:', error);
    return NextResponse.json(
      { error: 'Error creating ticket', details: error.message },
      { status: 500 }
    );
  }
}

