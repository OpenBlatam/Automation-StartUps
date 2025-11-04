/**
 * Enhanced LLM Integration with Advanced Features
 * Predictive analysis, anomaly detection, and intelligent recommendations
 */

import { LLMProvider, callLLM } from './llm';

export interface AnomalyDetection {
  metric: string;
  current: number;
  expected: number;
  deviation: number;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
}

export interface Prediction {
  metric: string;
  current: number;
  predicted: number;
  confidence: number;
  timeframe: string;
  explanation: string;
}

export interface Recommendation {
  priority: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  impact: string;
  action: string;
}

/**
 * Detect anomalies in KPI data using LLM
 */
export async function detectAnomalies(
  currentData: any,
  historicalData: any[],
  provider: LLMProvider = 'openai'
): Promise<AnomalyDetection[]> {
  const messages = [
    {
      role: 'system',
      content: `You are an anomaly detection expert for business KPIs.
Analyze the current data against historical patterns and identify anomalies.

For each anomaly, provide:
- metric: name of the metric
- current: current value
- expected: expected value based on historical data
- deviation: percentage deviation
- severity: low, medium, or high
- explanation: brief explanation of the anomaly

Return as JSON array of anomalies.`,
    },
    {
      role: 'user',
      content: `Current data: ${JSON.stringify(currentData, null, 2)}
Historical data: ${JSON.stringify(historicalData.slice(-30), null, 2)}

Identify anomalies and explain them.`,
    },
  ];

  try {
    const response = await callLLM(messages, provider);
    const parsed = JSON.parse(response.content);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    // Fallback to simple detection
    return [];
  }
}

/**
 * Generate predictions for KPIs
 */
export async function generatePredictions(
  currentData: any,
  historicalData: any[],
  timeframe: string = '7 days',
  provider: LLMProvider = 'openai'
): Promise<Prediction[]> {
  const messages = [
    {
      role: 'system',
      content: `You are a predictive analytics expert. Generate forecasts for business KPIs based on historical trends.

For each prediction, provide:
- metric: name of the metric
- current: current value
- predicted: predicted value
- confidence: confidence level (0-1)
- timeframe: prediction timeframe
- explanation: brief rationale

Return as JSON array.`,
    },
    {
      role: 'user',
      content: `Current data: ${JSON.stringify(currentData, null, 2)}
Historical trend: ${JSON.stringify(historicalData.slice(-30), null, 2)}
Predict for: ${timeframe}`,
    },
  ];

  try {
    const response = await callLLM(messages, provider);
    const parsed = JSON.parse(response.content);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    return [];
  }
}

/**
 * Generate actionable recommendations
 */
export async function generateRecommendations(
  kpiData: any,
  anomalies: AnomalyDetection[],
  provider: LLMProvider = 'openai'
): Promise<Recommendation[]> {
  const messages = [
    {
      role: 'system',
      content: `You are a business strategy consultant. Generate actionable recommendations based on KPI data and anomalies.

For each recommendation:
- priority: high, medium, or low
- category: category (e.g., "Revenue", "Operations", "Marketing")
- title: short title
- description: detailed description
- impact: expected impact
- action: specific action to take

Return as JSON array.`,
    },
    {
      role: 'user',
      content: `KPI Data: ${JSON.stringify(kpiData, null, 2)}
Anomalies detected: ${JSON.stringify(anomalies, null, 2)}

Generate actionable recommendations.`,
    },
  ];

  try {
    const response = await callLLM(messages, provider);
    const parsed = JSON.parse(response.content);
    return Array.isArray(parsed) ? parsed : [parsed];
  } catch {
    return [];
  }
}

/**
 * Analyze performance vs targets
 */
export async function analyzePerformanceVsTargets(
  currentData: any,
  targets: any,
  provider: LLMProvider = 'openai'
): Promise<string> {
  const messages = [
    {
      role: 'system',
      content: `You are a performance analyst. Compare current KPIs against targets and provide insights.

Analyze:
- Which metrics are meeting/exceeding targets
- Which metrics are below target
- Overall performance score
- Key areas for improvement`,
    },
    {
      role: 'user',
      content: `Current KPIs: ${JSON.stringify(currentData, null, 2)}
Targets: ${JSON.stringify(targets, null, 2)}

Provide performance analysis.`,
    },
  ];

  const response = await callLLM(messages, provider);
  return response.content;
}

/**
 * Generate executive summary
 */
export async function generateExecutiveSummary(
  kpiData: any,
  provider: LLMProvider = 'openai'
): Promise<string> {
  const messages = [
    {
      role: 'system',
      content: `You are a business intelligence analyst. Generate a concise executive summary (3-4 sentences) highlighting:
- Key achievements
- Areas of concern
- Top priorities
Use executive-friendly language.`,
    },
    {
      role: 'user',
      content: `KPI Data: ${JSON.stringify(kpiData, null, 2)}
Generate executive summary.`,
    },
  ];

  const response = await callLLM(messages, provider);
  return response.content;
}

