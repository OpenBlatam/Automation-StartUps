/**
 * API REST para Chatbot de Soporte en Tiempo Real
 * 
 * Endpoints:
 * - POST /api/support/chatbot - Procesar mensaje del usuario y obtener respuesta del chatbot
 * - GET /api/support/chatbot/faqs - Obtener FAQs relevantes
 */
import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

interface ChatbotRequest {
  message: string;
  conversation_id?: string;
  customer_email?: string;
  customer_name?: string;
  conversation_history?: ChatMessage[];
}

interface ChatbotResponse {
  response: string;
  confidence: number;
  resolved: boolean;
  faq_matched: boolean;
  faq_article_id?: string;
  intent_detected?: string;
  escalation_needed: boolean;
  escalation_reason?: string;
  conversation_id: string;
  suggested_actions?: string[];
}

/**
 * POST /api/support/chatbot
 * Procesa un mensaje del usuario y retorna respuesta del chatbot
 */
export async function POST(request: NextRequest) {
  try {
    const body: ChatbotRequest = await request.json();
    const { message, conversation_id, customer_email, customer_name, conversation_history = [] } = body;

    if (!message || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'El mensaje es requerido' },
        { status: 400 }
      );
    }

    // Generar conversation_id si no existe
    const convId = conversation_id || `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // 1. Buscar FAQs relevantes
    const faqResults = await searchFAQs(message);

    // 2. Detectar intención y necesidad de escalación
    const intentResult = detectIntent(message);
    const intent = intentResult.intent;
    const requiresImmediateEscalation = intentResult.requiresEscalation;

    // 3. Verificar solicitud explícita de agente humano
    const explicitAgentRequest = /(?:hablar|habla|quiero|necesito|conecta|conectar).*(?:con|a).*(?:agente|humano|persona|soporte|representante)/i.test(message);
    const negativeFeedback = /(?:no|nunca|tampoco|nada).*(?:funciona|ayuda|sirve|resuelve)/i.test(message);

    // 4. Intentar responder con FAQ o LLM
    let response: ChatbotResponse;
    
    if (faqResults.length > 0 && faqResults[0].relevance_score >= 0.7) {
      // Responder con FAQ
      const bestFAQ = faqResults[0];
      response = {
        response: bestFAQ.summary || bestFAQ.content.substring(0, 500),
        confidence: bestFAQ.relevance_score,
        resolved: true,
        faq_matched: true,
        faq_article_id: bestFAQ.article_id,
        intent_detected: intent,
        escalation_needed: false,
        conversation_id: convId,
        suggested_actions: ['¿Te ayudó esta respuesta?', '¿Necesitas algo más?']
      };
    } else {
      // Intentar con LLM si está configurado
      if (process.env.OPENAI_API_KEY) {
        const llmResponse = await callLLM(message, faqResults, conversation_history);
        
        if (llmResponse.confidence >= 0.7) {
          response = {
            response: llmResponse.text,
            confidence: llmResponse.confidence,
            resolved: true,
            faq_matched: faqResults.length > 0,
            faq_article_id: faqResults.length > 0 ? faqResults[0].article_id : undefined,
            intent_detected: intent,
            escalation_needed: false,
            conversation_id: convId,
            suggested_actions: ['¿Te ayudó esta respuesta?', '¿Necesitas algo más?']
          };
        } else {
          // Escalar a humano
          const escalationMessage = requiresImmediateEscalation
            ? 'Entiendo la urgencia de tu consulta. He creado un ticket de alta prioridad y un agente de nuestro equipo se contactará contigo lo antes posible.'
            : 'Entiendo tu consulta. Para darte la mejor asistencia, voy a conectarte con un agente de nuestro equipo que podrá ayudarte mejor. ¿Te parece bien?';
          
          response = {
            response: escalationMessage,
            confidence: llmResponse.confidence,
            resolved: false,
            faq_matched: false,
            intent_detected: intent,
            escalation_needed: true,
            escalation_reason: requiresImmediateEscalation 
              ? 'Escalación inmediata requerida por tipo de consulta'
              : 'Confianza insuficiente en la respuesta automática',
            conversation_id: convId,
            suggested_actions: requiresImmediateEscalation
              ? ['Ver estado del ticket', 'Contactar por teléfono']
              : ['Sí, conectar con agente', 'No, intentar otra pregunta']
          };
        }
      } else {
        // Sin LLM, escalar directamente
        response = {
          response: 'Gracias por tu consulta. Te voy a conectar con un agente de nuestro equipo que podrá ayudarte mejor.',
          confidence: 0.3,
          resolved: false,
          faq_matched: false,
          intent_detected: intent,
          escalation_needed: true,
          escalation_reason: 'No se encontraron FAQs relevantes y LLM no está disponible',
          conversation_id: convId,
          suggested_actions: ['Crear ticket de soporte', 'Ver FAQs']
        };
      }
    }

    // 5. Verificar si necesita escalación inmediata
    if (requiresImmediateEscalation || explicitAgentRequest || negativeFeedback) {
      response.escalation_needed = true;
      response.resolved = false;
      if (requiresImmediateEscalation) {
        response.response = 'Entiendo la urgencia de tu consulta. He creado un ticket de alta prioridad y un agente se contactará contigo inmediatamente.';
        response.escalation_reason = 'Escalación inmediata requerida por tipo de consulta';
      }
    }

    // 6. Si necesita escalación, crear ticket automáticamente
    if (response.escalation_needed && customer_email) {
      const priority = requiresImmediateEscalation || intent === 'security' || intent === 'legal' 
        ? 'urgent' 
        : 'high';
      await createTicketFromChat(message, customer_email, customer_name, intent, convId, priority);
    }

    // 5. Guardar conversación en historial
    await saveConversationHistory(convId, message, response.response, customer_email);

    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Error processing chatbot message:', error);
    return NextResponse.json(
      { 
        error: 'Error procesando mensaje',
        details: error.message,
        response: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo o contacta a soporte directamente.',
        escalation_needed: true,
        conversation_id: `error-${Date.now()}`
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/support/chatbot/faqs
 * Obtiene FAQs relevantes para una consulta
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q');
    const limit = parseInt(searchParams.get('limit') || '5');

    if (!query) {
      return NextResponse.json(
        { error: 'Parámetro "q" es requerido' },
        { status: 400 }
      );
    }

    const faqs = await searchFAQs(query, limit);

    return NextResponse.json({
      faqs: faqs.map(faq => ({
        article_id: faq.article_id,
        title: faq.title,
        summary: faq.summary,
        category: faq.category,
        relevance_score: faq.relevance_score
      }))
    });
  } catch (error: any) {
    console.error('Error fetching FAQs:', error);
    return NextResponse.json(
      { error: 'Error obteniendo FAQs', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * Busca FAQs relevantes en la base de datos
 */
async function searchFAQs(query: string, limit: number = 5) {
  const queryLower = query.toLowerCase().trim();
  const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);

  const sql = `
    SELECT 
      article_id,
      title,
      content,
      summary,
      category,
      tags,
      keywords,
      CASE 
        WHEN LOWER(title) LIKE $1 THEN 0.9
        WHEN EXISTS (
          SELECT 1 FROM unnest(keywords) AS kw
          WHERE LOWER(kw) = ANY($2)
        ) THEN 0.8
        WHEN LOWER(content) LIKE $1 THEN 0.7
        WHEN tags && $3 THEN 0.6
        ELSE 0.5
      END as relevance_score
    FROM support_faq_articles
    WHERE is_active = true
    AND (
      LOWER(content) LIKE $1
      OR LOWER(title) LIKE $1
      OR EXISTS (
        SELECT 1 FROM unnest(keywords) AS kw
        WHERE LOWER(kw) = ANY($2)
      )
      OR tags && $3
    )
    ORDER BY relevance_score DESC, view_count DESC
    LIMIT $4
  `;

  const pattern = `%${queryLower}%`;
  const keywordsArray = queryWords;
  const tagsArray = queryWords;

  const result = await pool.query(sql, [pattern, keywordsArray, tagsArray, limit]);

  return result.rows.map((row: any) => ({
    article_id: row.article_id,
    title: row.title,
    content: row.content,
    summary: row.summary,
    category: row.category,
    relevance_score: parseFloat(row.relevance_score)
  }));
}

/**
 * Detecta la intención del mensaje y determina si requiere escalación inmediata
 */
function detectIntent(message: string): { intent: string; requiresEscalation: boolean } {
  const messageLower = message.toLowerCase();

  // Intenciones que requieren escalación inmediata
  const immediateEscalationKeywords = [
    'hackeado', 'hackeada', 'hacked', 'robo', 'fraude', 'estafa',
    'demanda', 'legal', 'abogado', 'lawyer', 'sueño',
    'cancelar cuenta', 'eliminar cuenta', 'dar de baja permanente',
    'crash', 'caído', 'down', 'no funciona nada', 'sistema caído',
    'emergencia', 'urgente inmediato', 'asap', 'right now'
  ];

  // Verificar si requiere escalación inmediata
  const requiresEscalation = immediateEscalationKeywords.some(kw => 
    messageLower.includes(kw)
  );

  const intents: Record<string, string[]> = {
    billing: ['pago', 'factura', 'cobro', 'tarjeta', 'refund', 'reembolso', 'precio', 'costo', 'billing'],
    technical: ['error', 'no funciona', 'bug', 'problema', 'falla', 'no carga', 'lento', 'crash'],
    account: ['cuenta', 'login', 'contraseña', 'password', 'acceso', 'registro'],
    feature: ['cómo', 'funciona', 'característica', 'feature', 'capacidad', 'usar'],
    cancellation: ['cancelar', 'dar de baja', 'eliminar cuenta', 'cerrar'],
    security: ['seguridad', 'hack', 'robado', 'fraude', 'estafa', 'phishing'],
    legal: ['legal', 'abogado', 'demanda', 'sueño', 'términos'],
    general: ['información', 'ayuda', 'soporte', 'duda', 'hola', 'saludos']
  };

  let detectedIntent = 'general';
  for (const [intent, keywords] of Object.entries(intents)) {
    if (keywords.some(kw => messageLower.includes(kw))) {
      detectedIntent = intent;
      break;
    }
  }

  // Si es intención de seguridad o legal, siempre escalar
  if (detectedIntent === 'security' || detectedIntent === 'legal') {
    return { intent: detectedIntent, requiresEscalation: true };
  }

  return { intent: detectedIntent, requiresEscalation };
}

/**
 * Llama a OpenAI para generar respuesta contextual
 */
async function callLLM(
  message: string,
  faqContext: any[],
  conversationHistory: ChatMessage[]
): Promise<{ text: string; confidence: number }> {
  if (!process.env.OPENAI_API_KEY) {
    return { text: '', confidence: 0 };
  }

  try {
    const messages: any[] = [
      {
        role: 'system',
        content: `Eres un asistente de soporte al cliente experto y útil. 
Tu objetivo es resolver las consultas de los clientes de manera clara, concisa y amigable.
Si tienes información relevante en los artículos de ayuda, úsala para responder.
Si no puedes resolver la consulta con certeza, indica que escalarás a un agente humano.
Responde en el mismo idioma que el usuario.`
      }
    ];

    // Agregar contexto de FAQs si existe
    if (faqContext.length > 0) {
      const faqText = faqContext.slice(0, 3).map((faq, i) => 
        `${i + 1}. ${faq.title}\n${faq.summary || faq.content.substring(0, 200)}`
      ).join('\n\n');
      
      messages.push({
        role: 'system',
        content: `Artículos de ayuda relevantes:\n\n${faqText}`
      });
    }

    // Agregar historial de conversación
    if (conversationHistory.length > 0) {
      messages.push(...conversationHistory.slice(-5));
    }

    // Agregar mensaje del usuario
    messages.push({ role: 'user', content: message });

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
        messages: messages,
        temperature: 0.7,
        max_tokens: 500
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    const assistantMessage = data.choices[0].message.content;

    // Calcular confianza basada en longitud y contenido de la respuesta
    const confidence = assistantMessage && assistantMessage.length > 20 ? 0.8 : 0.5;

    return { text: assistantMessage, confidence };
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    return { text: '', confidence: 0 };
  }
}

/**
 * Crea un ticket automáticamente cuando se necesita escalación
 */
async function createTicketFromChat(
  message: string,
  customer_email: string,
  customer_name: string | undefined,
  intent: string,
  conversation_id: string,
  priority: string = 'medium'
) {
  try {
    const ticket_id = `TKT-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;

    const query = `
      INSERT INTO support_tickets (
        ticket_id,
        source,
        subject,
        description,
        customer_email,
        customer_name,
        category,
        status,
        priority,
        metadata
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'open', 'medium', $8)
      RETURNING ticket_id
    `;

    await pool.query(query, [
      ticket_id,
      'chat',
      `Consulta desde chatbot: ${message.substring(0, 50)}...`,
      message,
      customer_email,
      customer_name || null,
      intent,
      JSON.stringify({ conversation_id, escalated_from_chatbot: true })
    ]);

    // Disparar webhook de Kestra para procesamiento automático
    if (process.env.KESTRA_WEBHOOK_URL) {
      try {
        await fetch(`${process.env.KESTRA_WEBHOOK_URL}/workflows/support_ticket_automation/support-ticket`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ticket_id,
            subject: `Consulta desde chatbot`,
            description: message,
            customer_email,
            customer_name,
            source: 'chat',
            category: intent,
            metadata: { conversation_id, escalated_from_chatbot: true }
          })
        });
      } catch (webhookError) {
        console.error('Error calling Kestra webhook:', webhookError);
      }
    }

    return ticket_id;
  } catch (error) {
    console.error('Error creating ticket from chat:', error);
    throw error;
  }
}

/**
 * Guarda el historial de conversación
 */
async function saveConversationHistory(
  conversation_id: string,
  user_message: string,
  bot_response: string,
  customer_email: string | undefined
) {
  try {
    const query = `
      INSERT INTO support_chatbot_conversations (
        conversation_id,
        user_message,
        bot_response,
        customer_email,
        created_at
      ) VALUES ($1, $2, $3, $4, NOW())
      ON CONFLICT (conversation_id) DO UPDATE SET
        user_message = EXCLUDED.user_message,
        bot_response = EXCLUDED.bot_response,
        updated_at = NOW()
    `;

    await pool.query(query, [conversation_id, user_message, bot_response, customer_email || null]);
  } catch (error) {
    // Si la tabla no existe, solo loguear el error (no crítico)
    console.warn('No se pudo guardar historial de conversación:', error);
  }
}

