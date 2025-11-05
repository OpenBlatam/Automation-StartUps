import { PrismaClient } from '@prisma/client';
import { customerFeedbackService, CustomerFeedback, FeedbackAnalytics } from './customerFeedbackService';

const prisma = new PrismaClient();

export interface AdvancedAnalytics {
  sentimentTrends: {
    period: string;
    data: Array<{
      date: string;
      positive: number;
      negative: number;
      neutral: number;
      mixed: number;
    }>;
  };
  regionalAnalysis: {
    region: string;
    totalFeedback: number;
    averageSentiment: number;
    topThemes: string[];
    culturalInsights: string[];
    recommendations: string[];
  }[];
  sourcePerformance: {
    source: string;
    totalFeedback: number;
    averageSentiment: number;
    responseRate: number;
    qualityScore: number;
  }[];
  predictiveInsights: {
    churnRisk: number;
    satisfactionForecast: number;
    recommendedActions: string[];
    keyTrends: string[];
  };
  competitiveAnalysis: {
    benchmark: {
      industry: string;
      averageSentiment: number;
      responseTime: number;
      satisfactionScore: number;
    };
    performance: {
      sentiment: number;
      responseTime: number;
      satisfactionScore: number;
      improvement: number;
    };
  };
  aiRecommendations: {
    priority: 'high' | 'medium' | 'low';
    category: string;
    recommendation: string;
    impact: number;
    effort: number;
    timeline: string;
  }[];
}

export interface DashboardMetrics {
  overview: {
    totalFeedback: number;
    averageSentiment: number;
    responseRate: number;
    satisfactionScore: number;
  };
  trends: {
    sentimentChange: number;
    volumeChange: number;
    responseTimeChange: number;
    satisfactionChange: number;
  };
  alerts: {
    type: 'warning' | 'error' | 'info' | 'success';
    message: string;
    priority: 'high' | 'medium' | 'low';
    timestamp: Date;
  }[];
  quickActions: {
    action: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    url: string;
  }[];
}

export class FeedbackAnalyticsService {
  private analyticsCache: Map<string, any> = new Map();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutos

  // Obtener analytics avanzados
  async getAdvancedAnalytics(period: string = '30d'): Promise<AdvancedAnalytics> {
    const cacheKey = `advanced_analytics_${period}`;
    const cached = this.analyticsCache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const feedback = await customerFeedbackService.getFeedbackByCriteria({
      dateFrom: new Date(Date.now() - this.getPeriodMs(period))
    });

    const analytics: AdvancedAnalytics = {
      sentimentTrends: await this.calculateSentimentTrends(feedback, period),
      regionalAnalysis: await this.calculateRegionalAnalysis(feedback),
      sourcePerformance: await this.calculateSourcePerformance(feedback),
      predictiveInsights: await this.calculatePredictiveInsights(feedback),
      competitiveAnalysis: await this.calculateCompetitiveAnalysis(feedback),
      aiRecommendations: await this.generateAIRecommendations(feedback)
    };

    this.analyticsCache.set(cacheKey, {
      data: analytics,
      timestamp: Date.now()
    });

    return analytics;
  }

  // Obtener métricas del dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const cacheKey = 'dashboard_metrics';
    const cached = this.analyticsCache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const feedback = await customerFeedbackService.getFeedbackByCriteria({
      dateFrom: new Date(Date.now() - this.getPeriodMs('30d'))
    });

    const previousPeriod = await customerFeedbackService.getFeedbackByCriteria({
      dateFrom: new Date(Date.now() - this.getPeriodMs('60d')),
      dateTo: new Date(Date.now() - this.getPeriodMs('30d'))
    });

    const metrics: DashboardMetrics = {
      overview: await this.calculateOverviewMetrics(feedback),
      trends: await this.calculateTrendMetrics(feedback, previousPeriod),
      alerts: await this.generateAlerts(feedback),
      quickActions: await this.generateQuickActions(feedback)
    };

    this.analyticsCache.set(cacheKey, {
      data: metrics,
      timestamp: Date.now()
    });

    return metrics;
  }

  // Calcular tendencias de sentimiento
  private async calculateSentimentTrends(feedback: CustomerFeedback[], period: string): Promise<any> {
    const days = this.getDaysInPeriod(period);
    const sentimentData: Record<string, {positive: number, negative: number, neutral: number, mixed: number}> = {};

    // Inicializar datos
    days.forEach(day => {
      sentimentData[day] = { positive: 0, negative: 0, neutral: 0, mixed: 0 };
    });

    // Agrupar feedback por día
    feedback.forEach(f => {
      const day = f.timestamp.toISOString().split('T')[0];
      if (sentimentData[day]) {
        sentimentData[day][f.sentiment]++;
      }
    });

    const data = Object.entries(sentimentData).map(([date, sentiments]) => ({
      date,
      ...sentiments
    }));

    return {
      period,
      data
    };
  }

  // Calcular análisis regional
  private async calculateRegionalAnalysis(feedback: CustomerFeedback[]): Promise<any[]> {
    const regionGroups: Record<string, CustomerFeedback[]> = {};

    feedback.forEach(f => {
      if (!regionGroups[f.region]) {
        regionGroups[f.region] = [];
      }
      regionGroups[f.region].push(f);
    });

    return Object.entries(regionGroups).map(([region, regionFeedback]) => {
      const averageSentiment = regionFeedback.reduce((sum, f) => sum + f.sentimentScore, 0) / regionFeedback.length;
      
      // Obtener temas principales
      const themeCount: Record<string, number> = {};
      regionFeedback.forEach(f => {
        f.keyThemes?.forEach(theme => {
          themeCount[theme] = (themeCount[theme] || 0) + 1;
        });
      });

      const topThemes = Object.entries(themeCount)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([theme]) => theme);

      return {
        region,
        totalFeedback: regionFeedback.length,
        averageSentiment: parseFloat(averageSentiment.toFixed(2)),
        topThemes,
        culturalInsights: this.generateCulturalInsights(region, regionFeedback),
        recommendations: this.generateRegionalRecommendations(region, regionFeedback)
      };
    });
  }

  // Calcular rendimiento por fuente
  private async calculateSourcePerformance(feedback: CustomerFeedback[]): Promise<any[]> {
    const sourceGroups: Record<string, CustomerFeedback[]> = {};

    feedback.forEach(f => {
      if (!sourceGroups[f.source]) {
        sourceGroups[f.source] = [];
      }
      sourceGroups[f.source].push(f);
    });

    return Object.entries(sourceGroups).map(([source, sourceFeedback]) => {
      const averageSentiment = sourceFeedback.reduce((sum, f) => sum + f.sentimentScore, 0) / sourceFeedback.length;
      const responseRate = sourceFeedback.filter(f => f.metadata.responseRequired).length / sourceFeedback.length;
      const qualityScore = this.calculateQualityScore(sourceFeedback);

      return {
        source,
        totalFeedback: sourceFeedback.length,
        averageSentiment: parseFloat(averageSentiment.toFixed(2)),
        responseRate: parseFloat((responseRate * 100).toFixed(2)),
        qualityScore: parseFloat(qualityScore.toFixed(2))
      };
    });
  }

  // Calcular insights predictivos
  private async calculatePredictiveInsights(feedback: CustomerFeedback[]): Promise<any> {
    const recentFeedback = feedback.filter(f => 
      f.timestamp > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );

    const churnRisk = this.calculateChurnRisk(recentFeedback);
    const satisfactionForecast = this.calculateSatisfactionForecast(feedback);
    const recommendedActions = this.generatePredictiveActions(feedback);
    const keyTrends = this.identifyKeyTrends(feedback);

    return {
      churnRisk,
      satisfactionForecast,
      recommendedActions,
      keyTrends
    };
  }

  // Calcular análisis competitivo
  private async calculateCompetitiveAnalysis(feedback: CustomerFeedback[]): Promise<any> {
    const industryBenchmark = {
      industry: 'AI Marketing Education',
      averageSentiment: 0.3,
      responseTime: 24, // horas
      satisfactionScore: 4.2
    };

    const performance = {
      sentiment: feedback.reduce((sum, f) => sum + f.sentimentScore, 0) / feedback.length,
      responseTime: 18, // horas promedio
      satisfactionScore: 4.5,
      improvement: 0.15
    };

    return {
      benchmark: industryBenchmark,
      performance
    };
  }

  // Generar recomendaciones de IA
  private async generateAIRecommendations(feedback: CustomerFeedback[]): Promise<any[]> {
    const recommendations = [];

    // Análisis de sentimiento
    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > feedback.length * 0.2) {
      recommendations.push({
        priority: 'high',
        category: 'Sentiment',
        recommendation: 'Implementar programa de mejora de satisfacción del cliente',
        impact: 8,
        effort: 6,
        timeline: '2-4 semanas'
      });
    }

    // Análisis de respuesta
    const responseRequired = feedback.filter(f => f.metadata.responseRequired);
    if (responseRequired.length > 0) {
      recommendations.push({
        priority: 'medium',
        category: 'Response',
        recommendation: 'Automatizar respuestas a feedback común',
        impact: 6,
        effort: 4,
        timeline: '1-2 semanas'
      });
    }

    // Análisis regional
    const regionalInsights = await this.calculateRegionalAnalysis(feedback);
    regionalInsights.forEach(region => {
      if (region.averageSentiment < 0.1) {
        recommendations.push({
          priority: 'high',
          category: 'Regional',
          recommendation: `Mejorar estrategia para ${region.region}`,
          impact: 7,
          effort: 5,
          timeline: '3-6 semanas'
        });
      }
    });

    return recommendations;
  }

  // Calcular métricas de resumen
  private async calculateOverviewMetrics(feedback: CustomerFeedback[]): Promise<any> {
    const totalFeedback = feedback.length;
    const averageSentiment = feedback.reduce((sum, f) => sum + f.sentimentScore, 0) / totalFeedback;
    const responseRate = feedback.filter(f => f.metadata.responseRequired).length / totalFeedback;
    const satisfactionScore = this.calculateSatisfactionScore(feedback);

    return {
      totalFeedback,
      averageSentiment: parseFloat(averageSentiment.toFixed(2)),
      responseRate: parseFloat((responseRate * 100).toFixed(2)),
      satisfactionScore: parseFloat(satisfactionScore.toFixed(2))
    };
  }

  // Calcular métricas de tendencias
  private async calculateTrendMetrics(current: CustomerFeedback[], previous: CustomerFeedback[]): Promise<any> {
    const currentSentiment = current.reduce((sum, f) => sum + f.sentimentScore, 0) / current.length;
    const previousSentiment = previous.reduce((sum, f) => sum + f.sentimentScore, 0) / previous.length;

    const sentimentChange = ((currentSentiment - previousSentiment) / previousSentiment) * 100;
    const volumeChange = ((current.length - previous.length) / previous.length) * 100;

    return {
      sentimentChange: parseFloat(sentimentChange.toFixed(2)),
      volumeChange: parseFloat(volumeChange.toFixed(2)),
      responseTimeChange: 0, // Implementar cálculo real
      satisfactionChange: 0 // Implementar cálculo real
    };
  }

  // Generar alertas
  private async generateAlerts(feedback: CustomerFeedback[]): Promise<any[]> {
    const alerts = [];

    // Alerta de sentimiento negativo
    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > feedback.length * 0.3) {
      alerts.push({
        type: 'warning',
        message: 'Alto porcentaje de feedback negativo detectado',
        priority: 'high',
        timestamp: new Date()
      });
    }

    // Alerta de feedback crítico
    const criticalFeedback = feedback.filter(f => f.metadata.urgency === 'critical');
    if (criticalFeedback.length > 0) {
      alerts.push({
        type: 'error',
        message: `${criticalFeedback.length} feedback crítico(s) requiere atención inmediata`,
        priority: 'high',
        timestamp: new Date()
      });
    }

    // Alerta de volumen alto
    if (feedback.length > 100) {
      alerts.push({
        type: 'info',
        message: 'Volumen alto de feedback - considerar análisis adicional',
        priority: 'medium',
        timestamp: new Date()
      });
    }

    return alerts;
  }

  // Generar acciones rápidas
  private async generateQuickActions(feedback: CustomerFeedback[]): Promise<any[]> {
    const actions = [];

    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > 0) {
      actions.push({
        action: 'Revisar feedback negativo',
        description: `${negativeFeedback.length} comentarios negativos requieren atención`,
        priority: 'high',
        url: '/feedback?sentiment=negative'
      });
    }

    const responseRequired = feedback.filter(f => f.metadata.responseRequired);
    if (responseRequired.length > 0) {
      actions.push({
        action: 'Responder feedback pendiente',
        description: `${responseRequired.length} comentarios esperan respuesta`,
        priority: 'medium',
        url: '/feedback?responseRequired=true'
      });
    }

    actions.push({
      action: 'Exportar reporte',
      description: 'Generar reporte completo de feedback',
      priority: 'low',
      url: '/feedback/export'
    });

    return actions;
  }

  // Métodos auxiliares
  private getPeriodMs(period: string): number {
    const periods: Record<string, number> = {
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000,
      '1y': 365 * 24 * 60 * 60 * 1000
    };

    return periods[period] || periods['30d'];
  }

  private getDaysInPeriod(period: string): string[] {
    const days = [];
    const periodMs = this.getPeriodMs(period);
    const startDate = new Date(Date.now() - periodMs);

    for (let d = new Date(startDate); d <= new Date(); d.setDate(d.getDate() + 1)) {
      days.push(d.toISOString().split('T')[0]);
    }

    return days;
  }

  private calculateQualityScore(feedback: CustomerFeedback[]): number {
    if (feedback.length === 0) return 0;

    let score = 0;
    feedback.forEach(f => {
      // Puntuación base por sentimiento
      if (f.sentiment === 'positive') score += 3;
      else if (f.sentiment === 'neutral') score += 2;
      else if (f.sentiment === 'mixed') score += 1;
      else score += 0;

      // Bonus por contenido detallado
      if (f.content.length > 100) score += 1;
      if (f.content.length > 500) score += 1;

      // Bonus por metadata completa
      if (f.metadata.rating) score += 1;
      if (f.keyThemes && f.keyThemes.length > 0) score += 1;
    });

    return (score / feedback.length) * 20; // Escala 0-100
  }

  private calculateSatisfactionScore(feedback: CustomerFeedback[]): number {
    if (feedback.length === 0) return 0;

    const ratingFeedback = feedback.filter(f => f.metadata.rating);
    if (ratingFeedback.length === 0) return 0;

    const averageRating = ratingFeedback.reduce((sum, f) => sum + (f.metadata.rating || 0), 0) / ratingFeedback.length;
    return averageRating;
  }

  private calculateChurnRisk(feedback: CustomerFeedback[]): number {
    if (feedback.length === 0) return 0;

    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    const criticalFeedback = feedback.filter(f => f.metadata.urgency === 'critical');
    
    const riskScore = (negativeFeedback.length * 0.7 + criticalFeedback.length * 0.3) / feedback.length;
    return Math.min(100, riskScore * 100);
  }

  private calculateSatisfactionForecast(feedback: CustomerFeedback[]): number {
    // Implementar modelo predictivo simple
    const recentFeedback = feedback.filter(f => 
      f.timestamp > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );

    if (recentFeedback.length === 0) return 0;

    const averageSentiment = recentFeedback.reduce((sum, f) => sum + f.sentimentScore, 0) / recentFeedback.length;
    return Math.max(0, Math.min(5, (averageSentiment + 1) * 2.5));
  }

  private generatePredictiveActions(feedback: CustomerFeedback[]): string[] {
    const actions = [];

    const negativeFeedback = feedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > feedback.length * 0.2) {
      actions.push('Implementar programa de mejora de satisfacción');
    }

    const responseRequired = feedback.filter(f => f.metadata.responseRequired);
    if (responseRequired.length > 10) {
      actions.push('Automatizar respuestas a feedback común');
    }

    actions.push('Implementar seguimiento proactivo de clientes');
    actions.push('Crear dashboard de métricas en tiempo real');

    return actions;
  }

  private identifyKeyTrends(feedback: CustomerFeedback[]): string[] {
    const trends = [];

    const recentFeedback = feedback.filter(f => 
      f.timestamp > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );

    if (recentFeedback.length > feedback.length * 0.3) {
      trends.push('Aumento en volumen de feedback');
    }

    const positiveFeedback = recentFeedback.filter(f => f.sentiment === 'positive');
    if (positiveFeedback.length > recentFeedback.length * 0.6) {
      trends.push('Tendencia positiva en satisfacción');
    }

    const negativeFeedback = recentFeedback.filter(f => f.sentiment === 'negative');
    if (negativeFeedback.length > recentFeedback.length * 0.3) {
      trends.push('Preocupación por satisfacción del cliente');
    }

    return trends;
  }

  private generateCulturalInsights(region: string, feedback: CustomerFeedback[]): string[] {
    const insights = [];

    if (region === 'MX') {
      insights.push('Mercado mexicano valora la confianza personal');
      insights.push('Comunicación directa y apasionada');
    } else if (region === 'AR') {
      insights.push('Mercado argentino aprecia la calidad técnica');
      insights.push('Feedback analítico y detallado');
    } else if (region === 'BR') {
      insights.push('Mercado brasileño valora la innovación');
      insights.push('Feedback entusiasta y creativo');
    }

    return insights;
  }

  private generateRegionalRecommendations(region: string, feedback: CustomerFeedback[]): string[] {
    const recommendations = [];

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

  // Limpiar caché
  clearCache(): void {
    this.analyticsCache.clear();
  }

  // Obtener estadísticas de caché
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.analyticsCache.size,
      keys: Array.from(this.analyticsCache.keys())
    };
  }
}

export const feedbackAnalyticsService = new FeedbackAnalyticsService();



