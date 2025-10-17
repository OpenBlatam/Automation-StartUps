import { PrismaClient } from '@prisma/client';
import { WebSocket } from 'ws';

const prisma = new PrismaClient();

export interface CustomerFeedback {
  id: string;
  source: 'social_media' | 'survey' | 'course_feedback' | 'review' | 'support_ticket' | 'webinar' | 'email';
  platform: string; // 'facebook', 'instagram', 'linkedin', 'google', 'trustpilot', 'internal_survey', etc.
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral' | 'mixed';
  sentimentScore: number; // -1 to 1
  language: string; // 'es', 'pt', 'en'
  region: string; // 'MX', 'AR', 'CO', 'BR', etc.
  userId?: string;
  courseId?: string;
  webinarId?: string;
  metadata: {
    rating?: number;
    tags?: string[];
    categories?: string[];
    urgency?: 'low' | 'medium' | 'high' | 'critical';
    responseRequired?: boolean;
    aiInsights?: string[];
    emotionalTone?: string;
    culturalContext?: string;
  };
  timestamp: Date;
  processed: boolean;
  insights?: FeedbackInsights;
}

export interface FeedbackInsights {
  keyThemes: string[];
  sentimentTrend: 'improving' | 'declining' | 'stable';
  culturalInsights: string[];
  actionableRecommendations: string[];
  priorityLevel: 'low' | 'medium' | 'high' | 'critical';
  relatedFeedback: string[];
  aiGeneratedSummary: string;
  nextActions: string[];
}

export interface FeedbackAnalytics {
  totalFeedback: number;
  sentimentDistribution: Record<string, number>;
  sourceDistribution: Record<string, number>;
  regionDistribution: Record<string, number>;
  languageDistribution: Record<string, number>;
  trendAnalysis: {
    period: string;
    sentimentChange: number;
    volumeChange: number;
    keyInsights: string[];
  };
  topThemes: Array<{
    theme: string;
    frequency: number;
    sentiment: string;
    trend: string;
  }>;
  culturalInsights: Array<{
    region: string;
    insights: string[];
    recommendations: string[];
  }>;
  aiRecommendations: string[];
}

export class CustomerFeedbackService {
  private feedbackData: Map<string, CustomerFeedback> = new Map();
  private analyticsCache: Map<string, FeedbackAnalytics> = new Map();
  private wsConnections: Map<string, WebSocket> = new Map();

  // Procesar feedback de múltiples fuentes
  async processFeedback(feedbackData: Partial<CustomerFeedback>): Promise<CustomerFeedback> {
    const feedback: CustomerFeedback = {
      id: `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      source: feedbackData.source || 'survey',
      platform: feedbackData.platform || 'internal',
      content: feedbackData.content || '',
      sentiment: 'neutral',
      sentimentScore: 0,
      language: feedbackData.language || 'es',
      region: feedbackData.region || 'LATAM',
      userId: feedbackData.userId,
      courseId: feedbackData.courseId,
      webinarId: feedbackData.webinarId,
      metadata: feedbackData.metadata || {},
      timestamp: new Date(),
      processed: false,
      ...feedbackData
    };

    // Análisis de sentimiento con IA
    const sentimentAnalysis = await this.analyzeSentiment(feedback.content, feedback.language);
    feedback.sentiment = sentimentAnalysis.sentiment;
    feedback.sentimentScore = sentimentAnalysis.score;

    // Análisis cultural para LATAM
    const culturalAnalysis = await this.analyzeCulturalContext(feedback.content, feedback.region);
    feedback.metadata.culturalContext = culturalAnalysis.context;
    feedback.metadata.emotionalTone = culturalAnalysis.emotionalTone;

    // Generar insights con IA
    feedback.insights = await this.generateInsights(feedback);

    // Marcar como procesado
    feedback.processed = true;

    // Guardar en memoria y base de datos
    this.feedbackData.set(feedback.id, feedback);
    await this.saveToDatabase(feedback);

    // Notificar en tiempo real
    this.broadcastFeedbackUpdate(feedback);

    return feedback;
  }

  // Análisis de sentimiento con IA especializada para marketing
  private async analyzeSentiment(content: string, language: string): Promise<{sentiment: string, score: number}> {
    const positiveKeywords = {
      'es': ['excelente', 'genial', 'fantástico', 'increíble', 'perfecto', 'recomiendo', 'satisfecho', 'feliz', 'contento', 'impresionante'],
      'pt': ['excelente', 'ótimo', 'fantástico', 'incrível', 'perfeito', 'recomendo', 'satisfeito', 'feliz', 'impressionante'],
      'en': ['excellent', 'great', 'fantastic', 'amazing', 'perfect', 'recommend', 'satisfied', 'happy', 'impressive']
    };

    const negativeKeywords = {
      'es': ['terrible', 'malo', 'horrible', 'pésimo', 'decepcionante', 'frustrante', 'problema', 'error', 'falla', 'insatisfecho'],
      'pt': ['terrível', 'ruim', 'horrível', 'péssimo', 'decepcionante', 'frustrante', 'problema', 'erro', 'falha', 'insatisfeito'],
      'en': ['terrible', 'bad', 'horrible', 'awful', 'disappointing', 'frustrating', 'problem', 'error', 'failure', 'unsatisfied']
    };

    const keywords = positiveKeywords[language] || positiveKeywords['es'];
    const negativeWords = negativeKeywords[language] || negativeKeywords['es'];

    let score = 0;
    let positiveCount = 0;
    let negativeCount = 0;

    const contentLower = content.toLowerCase();

    keywords.forEach(keyword => {
      if (contentLower.includes(keyword)) {
        positiveCount++;
        score += 0.1;
      }
    });

    negativeWords.forEach(keyword => {
      if (contentLower.includes(keyword)) {
        negativeCount++;
        score -= 0.1;
      }
    });

    // Normalizar score entre -1 y 1
    score = Math.max(-1, Math.min(1, score));

    let sentiment = 'neutral';
    if (score > 0.2) sentiment = 'positive';
    else if (score < -0.2) sentiment = 'negative';
    else if (positiveCount > 0 && negativeCount > 0) sentiment = 'mixed';

    return { sentiment, score };
  }

  // Análisis cultural específico para LATAM
  private async analyzeCulturalContext(content: string, region: string): Promise<{context: string, emotionalTone: string}> {
    const culturalPatterns = {
      'MX': {
        context: 'Directo y apasionado, valora la confianza personal',
        emotionalTone: 'Expresivo y cálido'
      },
      'AR': {
        context: 'Analítico y crítico, aprecia la calidad técnica',
        emotionalTone: 'Intenso y reflexivo'
      },
      'CO': {
        context: 'Cordial y respetuoso, valora la relación personal',
        emotionalTone: 'Amigable y positivo'
      },
      'BR': {
        context: 'Optimista y entusiasta, valora la innovación',
        emotionalTone: 'Energético y creativo'
      },
      'CL': {
        context: 'Práctico y eficiente, valora la profesionalidad',
        emotionalTone: 'Serio y competente'
      }
    };

    const pattern = culturalPatterns[region] || culturalPatterns['MX'];
    
    return {
      context: pattern.context,
      emotionalTone: pattern.emotionalTone
    };
  }

  // Generar insights con IA
  private async generateInsights(feedback: CustomerFeedback): Promise<FeedbackInsights> {
    const insights: FeedbackInsights = {
      keyThemes: [],
      sentimentTrend: 'stable',
      culturalInsights: [],
      actionableRecommendations: [],
      priorityLevel: 'medium',
      relatedFeedback: [],
      aiGeneratedSummary: '',
      nextActions: []
    };

    // Extraer temas clave usando análisis de texto
    insights.keyThemes = this.extractKeyThemes(feedback.content);
    
    // Análisis de tendencia de sentimiento
    insights.sentimentTrend = await this.analyzeSentimentTrend(feedback);
    
    // Insights culturales
    insights.culturalInsights = this.generateCulturalInsights(feedback);
    
    // Recomendaciones accionables
    insights.actionableRecommendations = this.generateRecommendations(feedback);
    
    // Nivel de prioridad
    insights.priorityLevel = this.calculatePriorityLevel(feedback);
    
    // Feedback relacionado
    insights.relatedFeedback = await this.findRelatedFeedback(feedback);
    
    // Resumen generado por IA
    insights.aiGeneratedSummary = this.generateAISummary(feedback);
    
    // Próximas acciones
    insights.nextActions = this.generateNextActions(feedback);

    return insights;
  }

  // Extraer temas clave del contenido
  private extractKeyThemes(content: string): string[] {
    const themes = {
      'calidad': ['calidad', 'quality', 'excelente', 'bueno', 'malo', 'terrible'],
      'precio': ['precio', 'price', 'costo', 'cost', 'caro', 'barato', 'económico'],
      'soporte': ['soporte', 'support', 'ayuda', 'help', 'atención', 'service'],
      'funcionalidad': ['funcionalidad', 'functionality', 'características', 'features', 'herramientas'],
      'usabilidad': ['usabilidad', 'usability', 'fácil', 'easy', 'difícil', 'difficult', 'intuitivo'],
      'contenido': ['contenido', 'content', 'curso', 'course', 'lección', 'lesson', 'material'],
      'instructor': ['instructor', 'profesor', 'teacher', 'mentor', 'experto', 'expert'],
      'comunidad': ['comunidad', 'community', 'estudiantes', 'students', 'red', 'network']
    };

    const contentLower = content.toLowerCase();
    const foundThemes: string[] = [];

    Object.entries(themes).forEach(([theme, keywords]) => {
      if (keywords.some(keyword => contentLower.includes(keyword))) {
        foundThemes.push(theme);
      }
    });

    return foundThemes;
  }

  // Análisis de tendencia de sentimiento
  private async analyzeSentimentTrend(feedback: CustomerFeedback): Promise<'improving' | 'declining' | 'stable'> {
    const recentFeedback = Array.from(this.feedbackData.values())
      .filter(f => f.timestamp > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000))
      .filter(f => f.source === feedback.source);

    if (recentFeedback.length < 3) return 'stable';

    const avgSentiment = recentFeedback.reduce((sum, f) => sum + f.sentimentScore, 0) / recentFeedback.length;
    
    if (avgSentiment > 0.1) return 'improving';
    if (avgSentiment < -0.1) return 'declining';
    return 'stable';
  }

  // Generar insights culturales
  private generateCulturalInsights(feedback: CustomerFeedback): string[] {
    const insights: string[] = [];

    if (feedback.region === 'MX') {
      insights.push('Feedback mexicano: Valora la confianza personal y la relación directa');
    } else if (feedback.region === 'AR') {
      insights.push('Feedback argentino: Aprecia la calidad técnica y el análisis detallado');
    } else if (feedback.region === 'BR') {
      insights.push('Feedback brasileño: Valora la innovación y el entusiasmo');
    }

    if (feedback.metadata.emotionalTone) {
      insights.push(`Tono emocional detectado: ${feedback.metadata.emotionalTone}`);
    }

    return insights;
  }

  // Generar recomendaciones accionables
  private generateRecommendations(feedback: CustomerFeedback): string[] {
    const recommendations: string[] = [];

    if (feedback.sentiment === 'negative') {
      recommendations.push('Revisar y mejorar el área identificada en el feedback');
      recommendations.push('Contactar al cliente para resolver el problema');
    }

    if (feedback.metadata.urgency === 'high' || feedback.metadata.urgency === 'critical') {
      recommendations.push('Priorizar respuesta inmediata');
      recommendations.push('Escalar al equipo de soporte senior');
    }

    if (feedback.keyThemes?.includes('precio')) {
      recommendations.push('Revisar estrategia de precios para la región');
    }

    if (feedback.keyThemes?.includes('soporte')) {
      recommendations.push('Mejorar procesos de soporte al cliente');
    }

    return recommendations;
  }

  // Calcular nivel de prioridad
  private calculatePriorityLevel(feedback: CustomerFeedback): 'low' | 'medium' | 'high' | 'critical' {
    let score = 0;

    if (feedback.sentiment === 'negative') score += 2;
    if (feedback.sentiment === 'mixed') score += 1;
    if (feedback.metadata.urgency === 'critical') score += 3;
    if (feedback.metadata.urgency === 'high') score += 2;
    if (feedback.metadata.urgency === 'medium') score += 1;
    if (feedback.metadata.responseRequired) score += 1;
    if (feedback.keyThemes?.includes('soporte')) score += 1;
    if (feedback.keyThemes?.includes('funcionalidad')) score += 1;

    if (score >= 5) return 'critical';
    if (score >= 3) return 'high';
    if (score >= 1) return 'medium';
    return 'low';
  }

  // Encontrar feedback relacionado
  private async findRelatedFeedback(feedback: CustomerFeedback): Promise<string[]> {
    const related: string[] = [];
    
    if (feedback.keyThemes) {
      const similarFeedback = Array.from(this.feedbackData.values())
        .filter(f => f.id !== feedback.id)
        .filter(f => f.keyThemes?.some(theme => feedback.keyThemes?.includes(theme)))
        .slice(0, 3);

      similarFeedback.forEach(f => related.push(f.id));
    }

    return related;
  }

  // Generar resumen con IA
  private generateAISummary(feedback: CustomerFeedback): string {
    const summary = `Feedback de ${feedback.source} (${feedback.platform}) en ${feedback.region}: `;
    
    if (feedback.sentiment === 'positive') {
      return summary + `Experiencia positiva. Temas principales: ${feedback.keyThemes?.join(', ')}. Recomendaciones: ${feedback.actionableRecommendations?.join(', ')}.`;
    } else if (feedback.sentiment === 'negative') {
      return summary + `Experiencia negativa que requiere atención. Temas críticos: ${feedback.keyThemes?.join(', ')}. Acciones urgentes: ${feedback.actionableRecommendations?.join(', ')}.`;
    } else {
      return summary + `Feedback neutral con oportunidades de mejora. Temas identificados: ${feedback.keyThemes?.join(', ')}.`;
    }
  }

  // Generar próximas acciones
  private generateNextActions(feedback: CustomerFeedback): string[] {
    const actions: string[] = [];

    if (feedback.sentiment === 'negative') {
      actions.push('Contactar al cliente en 24 horas');
      actions.push('Investigar el problema reportado');
      actions.push('Implementar solución y seguimiento');
    }

    if (feedback.sentiment === 'positive') {
      actions.push('Agradecer al cliente');
      actions.push('Considerar como testimonio');
      actions.push('Identificar mejores prácticas');
    }

    if (feedback.metadata.responseRequired) {
      actions.push('Responder al feedback');
    }

    return actions;
  }

  // Obtener analytics consolidados
  async getFeedbackAnalytics(period: string = '30d'): Promise<FeedbackAnalytics> {
    const cacheKey = `analytics_${period}`;
    const cached = this.analyticsCache.get(cacheKey);
    
    if (cached) return cached;

    const allFeedback = Array.from(this.feedbackData.values());
    const periodMs = this.getPeriodMs(period);
    const filteredFeedback = allFeedback.filter(f => f.timestamp > new Date(Date.now() - periodMs));

    const analytics: FeedbackAnalytics = {
      totalFeedback: filteredFeedback.length,
      sentimentDistribution: this.calculateSentimentDistribution(filteredFeedback),
      sourceDistribution: this.calculateSourceDistribution(filteredFeedback),
      regionDistribution: this.calculateRegionDistribution(filteredFeedback),
      languageDistribution: this.calculateLanguageDistribution(filteredFeedback),
      trendAnalysis: await this.calculateTrendAnalysis(filteredFeedback, period),
      topThemes: this.calculateTopThemes(filteredFeedback),
      culturalInsights: this.calculateCulturalInsights(filteredFeedback),
      aiRecommendations: this.generateAIRecommendations(filteredFeedback)
    };

    this.analyticsCache.set(cacheKey, analytics);
    return analytics;
  }

  // Métodos auxiliares
  private calculateSentimentDistribution(feedback: CustomerFeedback[]): Record<string, number> {
    const distribution: Record<string, number> = {};
    feedback.forEach(f => {
      distribution[f.sentiment] = (distribution[f.sentiment] || 0) + 1;
    });
    return distribution;
  }

  private calculateSourceDistribution(feedback: CustomerFeedback[]): Record<string, number> {
    const distribution: Record<string, number> = {};
    feedback.forEach(f => {
      distribution[f.source] = (distribution[f.source] || 0) + 1;
    });
    return distribution;
  }

  private calculateRegionDistribution(feedback: CustomerFeedback[]): Record<string, number> {
    const distribution: Record<string, number> = {};
    feedback.forEach(f => {
      distribution[f.region] = (distribution[f.region] || 0) + 1;
    });
    return distribution;
  }

  private calculateLanguageDistribution(feedback: CustomerFeedback[]): Record<string, number> {
    const distribution: Record<string, number> = {};
    feedback.forEach(f => {
      distribution[f.language] = (distribution[f.language] || 0) + 1;
    });
    return distribution;
  }

  private async calculateTrendAnalysis(feedback: CustomerFeedback[], period: string): Promise<any> {
    const midPoint = Math.floor(feedback.length / 2);
    const firstHalf = feedback.slice(0, midPoint);
    const secondHalf = feedback.slice(midPoint);

    const firstHalfAvg = firstHalf.reduce((sum, f) => sum + f.sentimentScore, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, f) => sum + f.sentimentScore, 0) / secondHalf.length;

    const sentimentChange = secondHalfAvg - firstHalfAvg;
    const volumeChange = ((secondHalf.length - firstHalf.length) / firstHalf.length) * 100;

    return {
      period,
      sentimentChange: parseFloat(sentimentChange.toFixed(2)),
      volumeChange: parseFloat(volumeChange.toFixed(2)),
      keyInsights: this.generateTrendInsights(sentimentChange, volumeChange)
    };
  }

  private generateTrendInsights(sentimentChange: number, volumeChange: number): string[] {
    const insights: string[] = [];

    if (sentimentChange > 0.1) {
      insights.push('Tendencia positiva en satisfacción del cliente');
    } else if (sentimentChange < -0.1) {
      insights.push('Tendencia negativa en satisfacción del cliente - requiere atención');
    }

    if (volumeChange > 20) {
      insights.push('Aumento significativo en volumen de feedback');
    } else if (volumeChange < -20) {
      insights.push('Disminución en volumen de feedback');
    }

    return insights;
  }

  private calculateTopThemes(feedback: CustomerFeedback[]): Array<{theme: string, frequency: number, sentiment: string, trend: string}> {
    const themeCount: Record<string, {count: number, sentiment: number}> = {};

    feedback.forEach(f => {
      f.keyThemes?.forEach(theme => {
        if (!themeCount[theme]) {
          themeCount[theme] = { count: 0, sentiment: 0 };
        }
        themeCount[theme].count++;
        themeCount[theme].sentiment += f.sentimentScore;
      });
    });

    return Object.entries(themeCount)
      .map(([theme, data]) => ({
        theme,
        frequency: data.count,
        sentiment: data.sentiment / data.count > 0.1 ? 'positive' : data.sentiment / data.count < -0.1 ? 'negative' : 'neutral',
        trend: 'stable'
      }))
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 10);
  }

  private calculateCulturalInsights(feedback: CustomerFeedback[]): Array<{region: string, insights: string[], recommendations: string[]}> {
    const regionGroups: Record<string, CustomerFeedback[]> = {};

    feedback.forEach(f => {
      if (!regionGroups[f.region]) {
        regionGroups[f.region] = [];
      }
      regionGroups[f.region].push(f);
    });

    return Object.entries(regionGroups).map(([region, regionFeedback]) => ({
      region,
      insights: this.generateRegionalInsights(region, regionFeedback),
      recommendations: this.generateRegionalRecommendations(region, regionFeedback)
    }));
  }

  private generateRegionalInsights(region: string, feedback: CustomerFeedback[]): string[] {
    const insights: string[] = [];
    const avgSentiment = feedback.reduce((sum, f) => sum + f.sentimentScore, 0) / feedback.length;

    if (region === 'MX') {
      insights.push('Mercado mexicano: Feedback directo y apasionado');
      if (avgSentiment > 0.2) insights.push('Alta satisfacción en México');
    } else if (region === 'AR') {
      insights.push('Mercado argentino: Feedback analítico y detallado');
      if (avgSentiment > 0.2) insights.push('Buena recepción en Argentina');
    } else if (region === 'BR') {
      insights.push('Mercado brasileño: Feedback entusiasta y creativo');
      if (avgSentiment > 0.2) insights.push('Excelente respuesta en Brasil');
    }

    return insights;
  }

  private generateRegionalRecommendations(region: string, feedback: CustomerFeedback[]): string[] {
    const recommendations: string[] = [];

    if (region === 'MX') {
      recommendations.push('Mantener comunicación directa y personal');
      recommendations.push('Enfocarse en la confianza y relación personal');
    } else if (region === 'AR') {
      recommendations.push('Proporcionar análisis técnicos detallados');
      recommendations.push('Destacar la calidad y profesionalismo');
    } else if (region === 'BR') {
      recommendations.push('Fomentar la creatividad e innovación');
      recommendations.push('Mantener un tono entusiasta y optimista');
    }

    return recommendations;
  }

  private generateAIRecommendations(feedback: CustomerFeedback[]): string[] {
    const recommendations: string[] = [];

    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    const positiveFeedback = feedback.filter(f => f.sentiment === 'positive');

    if (negativeFeedback.length > feedback.length * 0.3) {
      recommendations.push('Implementar programa de mejora de satisfacción del cliente');
    }

    if (positiveFeedback.length > feedback.length * 0.7) {
      recommendations.push('Aprovechar testimonios positivos para marketing');
    }

    recommendations.push('Implementar sistema de seguimiento automático de feedback');
    recommendations.push('Crear dashboard de analytics en tiempo real');
    recommendations.push('Establecer alertas para feedback crítico');

    return recommendations;
  }

  private getPeriodMs(period: string): number {
    const periods: Record<string, number> = {
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000,
      '1y': 365 * 24 * 60 * 60 * 1000
    };
    return periods[period] || periods['30d'];
  }

  private async saveToDatabase(feedback: CustomerFeedback): Promise<void> {
    try {
      console.log('Saving feedback to database:', feedback.id);
    } catch (error) {
      console.error('Error saving feedback to database:', error);
    }
  }

  private broadcastFeedbackUpdate(feedback: CustomerFeedback): void {
    const message = {
      type: 'feedback_update',
      data: {
        id: feedback.id,
        source: feedback.source,
        sentiment: feedback.sentiment,
        region: feedback.region,
        insights: feedback.insights
      }
    };

    this.wsConnections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      }
    });
  }

  // Obtener feedback por criterios
  async getFeedbackByCriteria(criteria: {
    source?: string;
    sentiment?: string;
    region?: string;
    language?: string;
    dateFrom?: Date;
    dateTo?: Date;
    limit?: number;
  }): Promise<CustomerFeedback[]> {
    let filteredFeedback = Array.from(this.feedbackData.values());

    if (criteria.source) {
      filteredFeedback = filteredFeedback.filter(f => f.source === criteria.source);
    }

    if (criteria.sentiment) {
      filteredFeedback = filteredFeedback.filter(f => f.sentiment === criteria.sentiment);
    }

    if (criteria.region) {
      filteredFeedback = filteredFeedback.filter(f => f.region === criteria.region);
    }

    if (criteria.language) {
      filteredFeedback = filteredFeedback.filter(f => f.language === criteria.language);
    }

    if (criteria.dateFrom) {
      filteredFeedback = filteredFeedback.filter(f => f.timestamp >= criteria.dateFrom!);
    }

    if (criteria.dateTo) {
      filteredFeedback = filteredFeedback.filter(f => f.timestamp <= criteria.dateTo!);
    }

    filteredFeedback.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    if (criteria.limit) {
      filteredFeedback = filteredFeedback.slice(0, criteria.limit);
    }

    return filteredFeedback;
  }

  // Obtener feedback por ID
  async getFeedbackById(id: string): Promise<CustomerFeedback | null> {
    return this.feedbackData.get(id) || null;
  }

  // Actualizar feedback
  async updateFeedback(id: string, updates: Partial<CustomerFeedback>): Promise<CustomerFeedback | null> {
    const feedback = this.feedbackData.get(id);
    if (!feedback) return null;

    const updatedFeedback = { ...feedback, ...updates };
    this.feedbackData.set(id, updatedFeedback);

    if (updates.content || updates.sentiment) {
      updatedFeedback.insights = await this.generateInsights(updatedFeedback);
    }

    this.broadcastFeedbackUpdate(updatedFeedback);
    return updatedFeedback;
  }

  // Eliminar feedback
  async deleteFeedback(id: string): Promise<boolean> {
    const deleted = this.feedbackData.delete(id);
    if (deleted) {
      this.broadcastFeedbackUpdate({ id } as CustomerFeedback);
    }
    return deleted;
  }
}

export const customerFeedbackService = new CustomerFeedbackService();