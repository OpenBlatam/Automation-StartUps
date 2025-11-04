/**
 * LLM Integration for Real-time Reports
 * Supports OpenAI and DeepSeek APIs for SQL generation and data analysis
 */

const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || '';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';
const DEEPSEEK_BASE_URL = process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1';
const DEFAULT_LLM_PROVIDER = process.env.DEFAULT_LLM_PROVIDER || 'openai';
const DEFAULT_MODEL = process.env.DEFAULT_LLM_MODEL || 'gpt-4o-mini';

export type LLMProvider = 'openai' | 'deepseek';

export interface LLMResponse {
  content: string;
  tokens_used?: number;
  model?: string;
}

export interface SQLQueryResult {
  sql: string;
  explanation: string;
  confidence: number;
}

// Database schema context for LLM
const DB_SCHEMA_CONTEXT = `
-- Database Schema Context
-- Tables available for queries:

-- payments: payment transactions
--   columns: payment_id, created_at, amount, currency, customer, status, method

-- leads: lead information
--   columns: ext_id, created_at, first_name, last_name, email, score, priority, country, source

-- invoices: invoice records
--   columns: invoice_id, created_at, total, taxes, subtotal, due_date, status

-- Materialized Views:
--   mv_revenue_24h_hourly: revenue aggregated by hour for last 24 hours
--     columns: hour, revenue
--   mv_kpi_daily: daily KPIs aggregated (last 120 days)
--     columns: date, leads_count, conversion_rate, revenue, payment_success_rate
--   mv_kpi_timeseries_90d: time series data for last 90 days
--   mv_kpi_daily_segment: KPIs segmented by country/source

-- Common date functions: NOW(), CURRENT_DATE, INTERVAL 'X days'
-- Common aggregations: SUM(), COUNT(), AVG(), MAX(), MIN()
-- Common filters: WHERE, GROUP BY, ORDER BY, LIMIT
`;

/**
 * Call LLM API (OpenAI or DeepSeek)
 */
async function callLLM(
  messages: Array<{ role: string; content: string }>,
  provider: LLMProvider = DEFAULT_LLM_PROVIDER as LLMProvider,
  model?: string
): Promise<LLMResponse> {
  const apiKey = provider === 'deepseek' ? DEEPSEEK_API_KEY : OPENAI_API_KEY;
  const baseUrl = provider === 'deepseek' ? DEEPSEEK_BASE_URL : OPENAI_BASE_URL;
  const selectedModel = model || DEFAULT_MODEL;

  if (!apiKey) {
    throw new Error(`API key not configured for provider: ${provider}`);
  }

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: selectedModel,
      messages,
      temperature: 0.3,
      max_tokens: 2000,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`LLM API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    content: data.choices[0]?.message?.content || '',
    tokens_used: data.usage?.total_tokens,
    model: data.model,
  };
}

/**
 * Convert natural language query to SQL
 */
export async function naturalLanguageToSQL(
  query: string,
  provider: LLMProvider = DEFAULT_LLM_PROVIDER as LLMProvider
): Promise<SQLQueryResult> {
  const messages = [
    {
      role: 'system',
      content: `You are a SQL query generator for a PostgreSQL database. 
Your task is to convert natural language questions into valid PostgreSQL SQL queries.

${DB_SCHEMA_CONTEXT}

Rules:
1. Always generate valid PostgreSQL SQL
2. Use appropriate date functions (NOW(), CURRENT_DATE, INTERVAL)
3. Use materialized views when appropriate for performance
4. Include ORDER BY and LIMIT when fetching lists
5. Return ONLY the SQL query, no explanations in the SQL itself
6. After the SQL, add a brief explanation and confidence score (0-1)

Format your response as JSON:
{
  "sql": "SELECT ...",
  "explanation": "Brief explanation of what the query does",
  "confidence": 0.95
}`,
    },
    {
      role: 'user',
      content: `Convert this question to SQL: ${query}`,
    },
  ];

  try {
    const response = await callLLM(messages, provider);
    // Try to parse as JSON first
    try {
      const parsed = JSON.parse(response.content);
      return {
        sql: parsed.sql || response.content,
        explanation: parsed.explanation || 'Query generated',
        confidence: parsed.confidence || 0.8,
      };
    } catch {
      // If not JSON, extract SQL (might be wrapped in markdown)
      const sqlMatch = response.content.match(/```sql\n([\s\S]*?)\n```/) || 
                       response.content.match(/```\n([\s\S]*?)\n```/) ||
                       /SELECT[\s\S]+?;?/.exec(response.content);
      return {
        sql: sqlMatch ? sqlMatch[1].trim() : response.content.trim(),
        explanation: 'Query extracted from response',
        confidence: 0.7,
      };
    }
  } catch (error: any) {
    throw new Error(`Failed to generate SQL: ${error.message}`);
  }
}

/**
 * Analyze KPI data and generate insights
 */
export async function analyzeKPIs(
  data: any,
  context?: string,
  provider: LLMProvider = DEFAULT_LLM_PROVIDER as LLMProvider
): Promise<string> {
  const messages = [
    {
      role: 'system',
      content: `You are a data analyst specializing in business KPIs. 
Analyze the provided data and generate concise, actionable insights.

Focus on:
- Trends and patterns
- Anomalies or outliers
- Actionable recommendations
- Comparison to benchmarks when available

Be concise (2-3 paragraphs max) and use clear, business-friendly language.`,
    },
    {
      role: 'user',
      content: `${context || 'Analyze this KPI data'}\n\nData:\n${JSON.stringify(data, null, 2)}`,
    },
  ];

  const response = await callLLM(messages, provider);
  return response.content;
}

/**
 * Generate automatic insights from current KPIs
 */
export async function generateAutoInsights(
  summary: any,
  timeseries: any[],
  provider: LLMProvider = DEFAULT_LLM_PROVIDER as LLMProvider
): Promise<string> {
  const messages = [
    {
      role: 'system',
      content: `You are a real-time business intelligence analyst. 
Analyze the current KPI snapshot and generate brief insights (2-3 sentences).

Focus on:
- Current performance vs recent trends
- Notable changes or patterns
- Quick actionable observations

Be very concise and direct.`,
    },
    {
      role: 'user',
      content: `Current KPIs:
- Revenue (last hour): $${summary?.revenue_last_hour || 0}
- Revenue (24h): $${summary?.revenue_24h || 0}
- Leads by priority today: ${JSON.stringify(summary?.leads_by_priority_today || [])}
- Recent payments: ${summary?.payments_recent?.length || 0}
- Recent leads: ${summary?.leads_recent?.length || 0}
- Revenue trend (24h): ${JSON.stringify(timeseries.slice(-6))}

Generate a brief insight about current performance.`,
    },
  ];

  const response = await callLLM(messages, provider);
  return response.content;
}

/**
 * Generate a comprehensive report from KPIs
 */
export async function generateReport(
  kpiData: any,
  reportType: 'daily' | 'weekly' | 'monthly' | 'custom' = 'daily',
  provider: LLMProvider = DEFAULT_LLM_PROVIDER as LLMProvider
): Promise<string> {
  const messages = [
    {
      role: 'system',
      content: `You are a business intelligence report writer.
Generate a comprehensive ${reportType} report based on the provided KPI data.

Structure:
1. Executive Summary (2-3 sentences)
2. Key Metrics Overview
3. Trends and Patterns
4. Anomalies or Concerns
5. Recommendations

Use professional, clear language suitable for business stakeholders.`,
    },
    {
      role: 'user',
      content: `Generate a ${reportType} report from this data:\n\n${JSON.stringify(kpiData, null, 2)}`,
    },
  ];

  const response = await callLLM(messages, provider);
  return response.content;
}


