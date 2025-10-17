import { PrismaClient } from '@prisma/client';
import { customerFeedbackService, CustomerFeedback } from './customerFeedbackService';

const prisma = new PrismaClient();

export interface AdvancedAnalytics {
  emotionalIntelligence: {
    primaryEmotion: string;
    secondaryEmotions: string[];
    emotionalIntensity: number;
    emotionalStability: number;
    empathyLevel: number;
  };
  behavioralPatterns: {
    communicationStyle: string;
    decisionMakingStyle: string;
    riskTolerance: number;
    innovationAdoption: number;
    loyaltyIndicators: string[];
  };
  culturalAnalysis: {
    culturalValues: string[];
    communicationPreferences: string[];
    businessEtiquette: string[];
    decisionMakingFactors: string[];
    relationshipImportance: number;
  };
  predictiveMetrics: {
    churnRisk: number;
    upsellPotential: number;
    advocacyLikelihood: number;
    engagementScore: number;
    satisfactionTrajectory: 'improving' | 'declining' | 'stable';
  };
  actionableRecommendations: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
    priority: 'critical' | 'high' | 'medium' | 'low';
  };
}

export interface RealTimeAlert {
  id: string;
  type: 'sentiment_shift' | 'volume_spike' | 'critical_feedback' | 'trend_emergence' | 'anomaly_detected';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  affectedRegions: string[];
  affectedSources: string[];
  metrics: {
    currentValue: number;
    previousValue: number;
    changePercentage: number;
    threshold: number;
  };
  recommendations: string[];
  timestamp: Date;
  acknowledged: boolean;
  resolved: boolean;
}

export class AdvancedAnalyticsService {
  private analyticsCache: Map<string, AdvancedAnalytics> = new Map();
  private alerts: Map<string, RealTimeAlert> = new Map();
  private patternCache: Map<string, any> = new Map();

  // Procesar feedback con análisis avanzado
  async processAdvancedFeedback(feedback: CustomerFeedback): Promise<AdvancedAnalytics> {
    const cacheKey = `insights_${feedback.id}`;
    const cached = this.analyticsCache.get(cacheKey);
    
    if (cached) return cached;

    const insights: AdvancedAnalytics = {
      emotionalIntelligence: await this.analyzeEmotionalIntelligence(feedback),
      behavioralPatterns: await this.analyzeBehavioralPatterns(feedback),
      culturalAnalysis: await this.analyzeCulturalContext(feedback),
      predictiveMetrics: await this.calculatePredictiveMetrics(feedback),
      actionableRecommendations: await this.generateActionableRecommendations(feedback)
    };

    this.analyticsCache.set(cacheKey, insights);
    return insights;
  }

  // Análisis de inteligencia emocional
  private async analyzeEmotionalIntelligence(feedback: CustomerFeedback): Promise<any> {
    const content = feedback.content.toLowerCase();
    
    // Mapeo de emociones en múltiples idiomas
    const emotionMappings = {
      'joy': {
        'es': ['alegría', 'felicidad', 'contento', 'satisfecho', 'emocionado', 'entusiasmado'],
        'pt': ['alegria', 'felicidade', 'contente', 'satisfeito', 'emocionado', 'entusiasmado'],
        'en': ['joy', 'happiness', 'excited', 'thrilled', 'delighted', 'pleased']
      },
      'anger': {
        'es': ['enojo', 'ira', 'frustración', 'molesto', 'irritado', 'furioso'],
        'pt': ['raiva', 'ira', 'frustração', 'irritado', 'furioso'],
        'en': ['anger', 'frustration', 'annoyed', 'irritated', 'furious', 'mad']
      },
      'fear': {
        'es': ['miedo', 'preocupación', 'ansiedad', 'nervioso', 'inquieto'],
        'pt': ['medo', 'preocupação', 'ansiedade', 'nervoso', 'inquieto'],
        'en': ['fear', 'worry', 'anxiety', 'nervous', 'concerned']
      },
      'sadness': {
        'es': ['tristeza', 'decepción', 'desilusión', 'melancolía'],
        'pt': ['tristeza', 'decepção', 'desilusão', 'melancolia'],
        'en': ['sadness', 'disappointment', 'disillusioned', 'melancholy']
      },
      'surprise': {
        'es': ['sorpresa', 'asombro', 'impresionado', 'sorprendido'],
        'pt': ['surpresa', 'espanto', 'impressionado', 'surpreso'],
        'en': ['surprise', 'amazement', 'impressed', 'surprised']
      },
      'disgust': {
        'es': ['disgusto', 'repugnancia', 'asco', 'desagrado'],
        'pt': ['desgosto', 'repugnância', 'nojo', 'desagrado'],
        'en': ['disgust', 'repugnance', 'revulsion', 'displeasure']
      }
    };

    const language = feedback.language || 'es';
    const emotionScores: Record<string, number> = {};

    Object.entries(emotionMappings).forEach(([emotion, languages]) => {
      const words = languages[language] || languages['es'];
      let score = 0;
      
      words.forEach(word => {
        if (content.includes(word)) {
          score += 1;
        }
      });
      
      emotionScores[emotion] = score;
    });

    const totalEmotions = Object.values(emotionScores).reduce((sum, score) => sum + score, 0);
    const primaryEmotion = Object.entries(emotionScores)
      .sort(([,a], [,b]) => b - a)[0][0];
    
    const secondaryEmotions = Object.entries(emotionScores)
      .filter(([emotion, score]) => emotion !== primaryEmotion && score > 0)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([emotion]) => emotion);

    const emotionalIntensity = Math.min(1, totalEmotions / 10);
    const emotionalStability = this.calculateEmotionalStability(feedback);
    const empathyLevel = this.calculateEmpathyLevel(feedback);

    return {
      primaryEmotion,
      secondaryEmotions,
      emotionalIntensity: parseFloat(emotionalIntensity.toFixed(2)),
      emotionalStability: parseFloat(emotionalStability.toFixed(2)),
      empathyLevel: parseFloat(empathyLevel.toFixed(2))
    };
  }

  // Análisis de patrones de comportamiento
  private async analyzeBehavioralPatterns(feedback: CustomerFeedback): Promise<any> {
    const content = feedback.content.toLowerCase();
    
    // Análisis de estilo de comunicación
    const communicationStyles = {
      'direct': {
        'es': ['directamente', 'claramente', 'sin rodeos', 'francamente'],
        'pt': ['diretamente', 'claramente', 'sem rodeios', 'francamente'],
        'en': ['directly', 'clearly', 'straightforward', 'frankly']
      },
      'diplomatic': {
        'es': ['considerando', 'quizás', 'posiblemente', 'sugiero', 'recomiendo'],
        'pt': ['considerando', 'talvez', 'possivelmente', 'sugiro', 'recomendo'],
        'en': ['considering', 'perhaps', 'possibly', 'suggest', 'recommend']
      },
      'analytical': {
        'es': ['analizando', 'evaluando', 'considerando', 'basándome en', 'según los datos'],
        'pt': ['analisando', 'avaliando', 'considerando', 'baseado em', 'segundo os dados'],
        'en': ['analyzing', 'evaluating', 'considering', 'based on', 'according to data']
      },
      'emotional': {
        'es': ['siento', 'me siento', 'emocionalmente', 'personalmente'],
        'pt': ['sinto', 'me sinto', 'emocionalmente', 'pessoalmente'],
        'en': ['feel', 'I feel', 'emotionally', 'personally']
      }
    };

    const language = feedback.language || 'es';
    let communicationStyle = 'neutral';
    let maxScore = 0;

    Object.entries(communicationStyles).forEach(([style, languages]) => {
      const words = languages[language] || languages['es'];
      let score = 0;
      
      words.forEach(word => {
        if (content.includes(word)) {
          score += 1;
        }
      });
      
      if (score > maxScore) {
        maxScore = score;
        communicationStyle = style;
      }
    });

    // Análisis de tolerancia al riesgo
    const riskIndicators = {
      'conservative': ['seguro', 'estable', 'confiable', 'tradicional'],
      'moderate': ['equilibrado', 'moderado', 'gradual', 'progresivo'],
      'aggressive': ['innovador', 'revolucionario', 'disruptivo', 'avanzado']
    };

    let riskTolerance = 0.5; // Neutral por defecto
    Object.entries(riskIndicators).forEach(([level, words]) => {
      words.forEach(word => {
        if (content.includes(word)) {
          if (level === 'conservative') riskTolerance -= 0.1;
          else if (level === 'aggressive') riskTolerance += 0.1;
        }
      });
    });

    riskTolerance = Math.max(0, Math.min(1, riskTolerance));

    // Análisis de adopción de innovación
    const innovationKeywords = ['nuevo', 'innovador', 'tecnología', 'digital', 'moderno', 'avanzado'];
    const innovationScore = innovationKeywords.filter(word => content.includes(word)).length / innovationKeywords.length;

    // Indicadores de lealtad
    const loyaltyIndicators = [];
    if (content.includes('recomiendo') || content.includes('recomend')) loyaltyIndicators.push('recommendation');
    if (content.includes('volvería') || content.includes('volveria')) loyaltyIndicators.push('repeat_purchase');
    if (content.includes('fiel') || content.includes('leal')) loyaltyIndicators.push('brand_loyalty');
    if (content.includes('referir') || content.includes('referir')) loyaltyIndicators.push('referral');

    return {
      communicationStyle,
      decisionMakingStyle: this.analyzeDecisionMakingStyle(feedback),
      riskTolerance: parseFloat(riskTolerance.toFixed(2)),
      innovationAdoption: parseFloat(innovationScore.toFixed(2)),
      loyaltyIndicators
    };
  }

  // Análisis cultural avanzado
  private async analyzeCulturalContext(feedback: CustomerFeedback): Promise<any> {
    const region = feedback.region || 'LATAM';
    const language = feedback.language || 'es';
    
    const culturalProfiles = {
      'MX': {
        values: ['familia', 'trabajo', 'respeto', 'honor', 'tradición'],
        communication: ['directo', 'cálido', 'personal', 'relacional'],
        business: ['jerárquico', 'formal', 'relaciones personales'],
        decisions: ['consenso', 'relaciones', 'confianza'],
        relationship: 0.9
      },
      'AR': {
        values: ['educación', 'cultura', 'debate', 'análisis', 'calidad'],
        communication: ['analítico', 'crítico', 'directo', 'intelectual'],
        business: ['meritocrático', 'técnico', 'profesional'],
        decisions: ['lógica', 'datos', 'análisis'],
        relationship: 0.7
      },
      'BR': {
        values: ['optimismo', 'creatividad', 'flexibilidad', 'innovación', 'alegría'],
        communication: ['entusiasta', 'creativo', 'colaborativo', 'positivo'],
        business: ['informal', 'innovador', 'colaborativo'],
        decisions: ['intuición', 'relaciones', 'oportunidad'],
        relationship: 0.8
      },
      'CO': {
        values: ['cordialidad', 'respeto', 'educación', 'trabajo', 'familia'],
        communication: ['cordial', 'respetuoso', 'diplomático', 'cuidadoso'],
        business: ['jerárquico', 'formal', 'respetuoso'],
        decisions: ['consenso', 'respeto', 'estabilidad'],
        relationship: 0.85
      }
    };

    const profile = culturalProfiles[region] || culturalProfiles['MX'];
    
    // Análisis de valores culturales en el contenido
    const content = feedback.content.toLowerCase();
    const culturalValues = profile.values.filter(value => content.includes(value));
    
    // Análisis de preferencias de comunicación
    const communicationPreferences = profile.communication.filter(pref => 
      this.analyzeCommunicationPreference(content, pref)
    );

    return {
      culturalValues,
      communicationPreferences,
      businessEtiquette: profile.business,
      decisionMakingFactors: profile.decisions,
      relationshipImportance: profile.relationship
    };
  }

  // Métricas predictivas
  private async calculatePredictiveMetrics(feedback: CustomerFeedback): Promise<any> {
    const churnProbability = this.calculateChurnProbability(feedback);
    const upsellPotential = this.calculateUpsellPotential(feedback);
    const advocacyLikelihood = this.calculateAdvocacyLikelihood(feedback);
    const engagementScore = this.calculateEngagementScore(feedback);
    const satisfactionTrajectory = this.calculateSatisfactionTrajectory(feedback);

    return {
      churnProbability: parseFloat(churnProbability.toFixed(2)),
      upsellPotential: parseFloat(upsellPotential.toFixed(2)),
      advocacyLikelihood: parseFloat(advocacyLikelihood.toFixed(2)),
      engagementScore: parseFloat(engagementScore.toFixed(2)),
      satisfactionTrajectory
    };
  }

  // Generar recomendaciones accionables
  private async generateActionableRecommendations(feedback: CustomerFeedback): Promise<any> {
    const recommendations = {
      immediate: [],
      shortTerm: [],
      longTerm: [],
      priority: 'medium' as 'critical' | 'high' | 'medium' | 'low'
    };

    // Análisis de urgencia
    if (feedback.metadata.urgency === 'critical') {
      recommendations.priority = 'critical';
      recommendations.immediate.push('Contactar al cliente inmediatamente');
      recommendations.immediate.push('Escalar al equipo de soporte senior');
    }

    // Análisis de sentimiento
    if (feedback.sentiment === 'negative') {
      recommendations.shortTerm.push('Implementar plan de recuperación');
      recommendations.shortTerm.push('Ofrecer compensación o descuento');
      recommendations.longTerm.push('Revisar procesos internos');
    } else if (feedback.sentiment === 'positive') {
      recommendations.shortTerm.push('Solicitar testimonio o reseña');
      recommendations.longTerm.push('Considerar para caso de estudio');
    }

    // Análisis regional
    const region = feedback.region || 'LATAM';
    if (region === 'MX') {
      recommendations.longTerm.push('Mantener comunicación personal y directa');
    } else if (region === 'AR') {
      recommendations.longTerm.push('Proporcionar análisis técnicos detallados');
    } else if (region === 'BR') {
      recommendations.longTerm.push('Fomentar creatividad e innovación');
    }

    return recommendations;
  }

  // Métodos auxiliares
  private calculateEmotionalStability(feedback: CustomerFeedback): number {
    const content = feedback.content;
    const emotionalWords = ['siempre', 'nunca', 'todo', 'nada', 'completamente', 'totalmente'];
    const stabilityScore = 1 - (emotionalWords.filter(word => content.toLowerCase().includes(word)).length / emotionalWords.length);
    return Math.max(0, stabilityScore);
  }

  private calculateEmpathyLevel(feedback: CustomerFeedback): number {
    const content = feedback.content.toLowerCase();
    const empathyKeywords = ['entiendo', 'comprendo', 'empático', 'comprensión', 'solidaridad'];
    const empathyScore = empathyKeywords.filter(word => content.includes(word)).length / empathyKeywords.length;
    return Math.min(1, empathyScore * 2);
  }

  private analyzeDecisionMakingStyle(feedback: CustomerFeedback): string {
    const content = feedback.content.toLowerCase();
    
    if (content.includes('datos') || content.includes('estadísticas') || content.includes('análisis')) {
      return 'data_driven';
    } else if (content.includes('intuición') || content.includes('instinto') || content.includes('sentir')) {
      return 'intuitive';
    } else if (content.includes('consenso') || content.includes('equipo') || content.includes('grupo')) {
      return 'collaborative';
    } else {
      return 'individual';
    }
  }

  private analyzeCommunicationPreference(content: string, preference: string): boolean {
    const preferenceKeywords = {
      'directo': ['directamente', 'claramente', 'sin rodeos'],
      'cálido': ['cálido', 'amigable', 'cordial'],
      'personal': ['personal', 'individual', 'específico'],
      'relacional': ['relación', 'conexión', 'vínculo'],
      'analítico': ['análisis', 'evaluación', 'estudio'],
      'crítico': ['crítico', 'evaluación', 'revisión'],
      'entusiasta': ['entusiasmado', 'emocionado', 'excitado'],
      'creativo': ['creativo', 'innovador', 'original'],
      'colaborativo': ['colaboración', 'equipo', 'juntos'],
      'positivo': ['positivo', 'optimista', 'bueno']
    };

    const keywords = preferenceKeywords[preference] || [];
    return keywords.some(keyword => content.includes(keyword));
  }

  private calculateChurnProbability(feedback: CustomerFeedback): number {
    let probability = 0;
    
    if (feedback.sentiment === 'negative') probability += 0.3;
    if (feedback.metadata.urgency === 'high') probability += 0.2;
    if (feedback.metadata.urgency === 'critical') probability += 0.4;
    if (feedback.content.includes('cancelar') || feedback.content.includes('dejar')) probability += 0.3;
    if (feedback.content.includes('competencia') || feedback.content.includes('alternativa')) probability += 0.2;
    
    return Math.min(1, probability);
  }

  private calculateUpsellPotential(feedback: CustomerFeedback): number {
    let potential = 0;
    
    if (feedback.sentiment === 'positive') potential += 0.4;
    if (feedback.content.includes('más') || feedback.content.includes('adicional')) potential += 0.2;
    if (feedback.content.includes('expandir') || feedback.content.includes('crecer')) potential += 0.3;
    if (feedback.content.includes('satisfecho') || feedback.content.includes('contento')) potential += 0.2;
    
    return Math.min(1, potential);
  }

  private calculateAdvocacyLikelihood(feedback: CustomerFeedback): number {
    let likelihood = 0;
    
    if (feedback.sentiment === 'positive') likelihood += 0.3;
    if (feedback.content.includes('recomiendo') || feedback.content.includes('recomend')) likelihood += 0.4;
    if (feedback.content.includes('excelente') || feedback.content.includes('fantástico')) likelihood += 0.3;
    if (feedback.content.includes('referir') || feedback.content.includes('compartir')) likelihood += 0.2;
    
    return Math.min(1, likelihood);
  }

  private calculateEngagementScore(feedback: CustomerFeedback): number {
    let score = 0;
    
    // Longitud del feedback
    if (feedback.content.length > 100) score += 0.2;
    if (feedback.content.length > 500) score += 0.2;
    
    // Detalle en el feedback
    if (feedback.content.includes('porque') || feedback.content.includes('debido a')) score += 0.2;
    if (feedback.content.includes('ejemplo') || feedback.content.includes('específicamente')) score += 0.2;
    
    // Emocionalidad
    if (feedback.sentiment !== 'neutral') score += 0.2;
    
    return Math.min(1, score);
  }

  private calculateSatisfactionTrajectory(feedback: CustomerFeedback): 'improving' | 'declining' | 'stable' {
    if (feedback.sentiment === 'positive') return 'improving';
    if (feedback.sentiment === 'negative') return 'declining';
    return 'stable';
  }

  // Generar alertas en tiempo real
  async generateRealTimeAlerts(feedback: CustomerFeedback): Promise<RealTimeAlert[]> {
    const alerts: RealTimeAlert[] = [];

    // Alerta de cambio de sentimiento
    if (feedback.sentiment === 'negative' && feedback.sentimentScore < -0.5) {
      alerts.push({
        id: `alert_${Date.now()}_sentiment`,
        type: 'sentiment_shift',
        severity: 'high',
        title: 'Cambio de Sentimiento Detectado',
        description: 'Feedback negativo crítico detectado',
        affectedRegions: [feedback.region],
        affectedSources: [feedback.source],
        metrics: {
          currentValue: feedback.sentimentScore,
          previousValue: 0,
          changePercentage: -100,
          threshold: -0.5
        },
        recommendations: ['Contactar al cliente inmediatamente', 'Revisar el problema reportado'],
        timestamp: new Date(),
        acknowledged: false,
        resolved: false
      });
    }

    // Alerta de feedback crítico
    if (feedback.metadata.urgency === 'critical') {
      alerts.push({
        id: `alert_${Date.now()}_critical`,
        type: 'critical_feedback',
        severity: 'critical',
        title: 'Feedback Crítico Requiere Atención',
        description: 'Feedback marcado como crítico necesita respuesta inmediata',
        affectedRegions: [feedback.region],
        affectedSources: [feedback.source],
        metrics: {
          currentValue: 1,
          previousValue: 0,
          changePercentage: 100,
          threshold: 0.8
        },
        recommendations: ['Escalar al equipo senior', 'Contactar al cliente en 1 hora'],
        timestamp: new Date(),
        acknowledged: false,
        resolved: false
      });
    }

    return alerts;
  }

  // Obtener insights consolidados
  async getConsolidatedInsights(period: string = '30d'): Promise<{
    emotionalIntelligence: any;
    behavioralPatterns: any;
    culturalAnalysis: any;
    predictiveMetrics: any;
    recommendations: any;
  }> {
    // Implementar análisis consolidado de todos los feedback del período
    return {
      emotionalIntelligence: {},
      behavioralPatterns: {},
      culturalAnalysis: {},
      predictiveMetrics: {},
      recommendations: {}
    };
  }
}

export const advancedAnalyticsService = new AdvancedAnalyticsService();