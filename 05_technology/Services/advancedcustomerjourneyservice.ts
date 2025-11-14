import { EventEmitter } from 'events';
import { CustomerFeedback } from './customerFeedbackService';

export interface CustomerJourney {
  id: string;
  customerId: string;
  customerEmail: string;
  customerName?: string;
  journeyName: string;
  stage: 'awareness' | 'consideration' | 'purchase' | 'onboarding' | 'adoption' | 'retention' | 'advocacy' | 'churn';
  touchpoints: CustomerTouchpoint[];
  timeline: JourneyEvent[];
  metrics: JourneyMetrics;
  insights: JourneyInsight[];
  recommendations: JourneyRecommendation[];
  status: 'active' | 'completed' | 'paused' | 'churned';
  createdAt: Date;
  updatedAt: Date;
  lastActivityAt: Date;
}

export interface CustomerTouchpoint {
  id: string;
  type: 'email' | 'website' | 'social_media' | 'support' | 'sales' | 'marketing' | 'product' | 'feedback';
  channel: string;
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  engagement: number; // 0-100
  timestamp: Date;
  metadata: Record<string, any>;
}

export interface JourneyEvent {
  id: string;
  type: 'touchpoint' | 'milestone' | 'conversion' | 'churn_risk' | 'advocacy' | 'feedback';
  title: string;
  description: string;
  timestamp: Date;
  value?: number;
  metadata: Record<string, any>;
}

export interface JourneyMetrics {
  totalTouchpoints: number;
  averageEngagement: number;
  timeInStage: number; // days
  conversionRate: number;
  churnRisk: number; // 0-100
  advocacyScore: number; // 0-100
  satisfactionScore: number; // 0-100
  lastActivityDays: number;
  stageProgression: StageProgression[];
}

export interface StageProgression {
  stage: string;
  enteredAt: Date;
  exitedAt?: Date;
  duration: number; // days
  touchpoints: number;
  engagement: number;
}

export interface JourneyInsight {
  id: string;
  type: 'pattern' | 'anomaly' | 'opportunity' | 'risk' | 'trend';
  title: string;
  description: string;
  confidence: number; // 0-100
  impact: 'low' | 'medium' | 'high' | 'critical';
  actionable: boolean;
  recommendations: string[];
  generatedAt: Date;
}

export interface JourneyRecommendation {
  id: string;
  type: 'engagement' | 'conversion' | 'retention' | 'upsell' | 'advocacy';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  effort: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  actions: string[];
  expectedOutcome: string;
  generatedAt: Date;
}

export interface JourneyTemplate {
  id: string;
  name: string;
  description: string;
  industry: string;
  stages: JourneyStageTemplate[];
  touchpoints: TouchpointTemplate[];
  metrics: string[];
  insights: string[];
  created: Date;
  updated: Date;
}

export interface JourneyStageTemplate {
  stage: string;
  name: string;
  description: string;
  duration: number; // expected days
  touchpoints: string[];
  metrics: string[];
  exitCriteria: string[];
}

export interface TouchpointTemplate {
  type: string;
  name: string;
  description: string;
  channel: string;
  frequency: 'once' | 'daily' | 'weekly' | 'monthly';
  content: string;
  expectedEngagement: number;
}

export class AdvancedCustomerJourneyService extends EventEmitter {
  private journeys: Map<string, CustomerJourney> = new Map();
  private templates: Map<string, JourneyTemplate> = new Map();
  private isAnalyzing: boolean = false;
  private analysisQueue: string[] = [];
  private analysisInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultTemplates();
    this.startAnalysis();
  }

  private initializeDefaultTemplates(): void {
    // Template para SaaS B2B
    const saasB2BTemplate: JourneyTemplate = {
      id: 'saas_b2b_template',
      name: 'SaaS B2B Customer Journey',
      description: 'Complete customer journey for B2B SaaS companies',
      industry: 'SaaS',
      stages: [
        {
          stage: 'awareness',
          name: 'Awareness',
          description: 'Customer becomes aware of the problem and solution',
          duration: 30,
          touchpoints: ['content_marketing', 'social_media', 'webinar'],
          metrics: ['website_visits', 'content_engagement', 'social_shares'],
          exitCriteria: ['content_download', 'demo_request', 'trial_signup']
        },
        {
          stage: 'consideration',
          name: 'Consideration',
          description: 'Customer evaluates different solutions',
          duration: 45,
          touchpoints: ['demo', 'case_study', 'sales_call'],
          metrics: ['demo_attendance', 'case_study_views', 'sales_meetings'],
          exitCriteria: ['trial_start', 'pilot_program', 'proposal_request']
        },
        {
          stage: 'purchase',
          name: 'Purchase',
          description: 'Customer makes the purchase decision',
          duration: 14,
          touchpoints: ['sales_call', 'proposal', 'contract'],
          metrics: ['proposal_views', 'contract_signed', 'payment_received'],
          exitCriteria: ['contract_signed', 'payment_received']
        },
        {
          stage: 'onboarding',
          name: 'Onboarding',
          description: 'Customer gets started with the product',
          duration: 30,
          touchpoints: ['welcome_email', 'setup_call', 'training'],
          metrics: ['setup_completion', 'feature_adoption', 'support_tickets'],
          exitCriteria: ['first_value', 'feature_adoption', 'team_training']
        },
        {
          stage: 'adoption',
          name: 'Adoption',
          description: 'Customer adopts and uses the product regularly',
          duration: 90,
          touchpoints: ['product_usage', 'support', 'check_in'],
          metrics: ['usage_frequency', 'feature_usage', 'satisfaction'],
          exitCriteria: ['regular_usage', 'feature_adoption', 'team_growth']
        },
        {
          stage: 'retention',
          name: 'Retention',
          description: 'Customer continues using and renews',
          duration: 365,
          touchpoints: ['renewal', 'upsell', 'success_review'],
          metrics: ['renewal_rate', 'upsell_rate', 'satisfaction'],
          exitCriteria: ['renewal', 'upsell', 'advocacy']
        },
        {
          stage: 'advocacy',
          name: 'Advocacy',
          description: 'Customer becomes an advocate and refers others',
          duration: 180,
          touchpoints: ['referral', 'testimonial', 'case_study'],
          metrics: ['referrals', 'testimonials', 'case_studies'],
          exitCriteria: ['referral_made', 'testimonial_given']
        }
      ],
      touchpoints: [
        {
          type: 'email',
          name: 'Welcome Email',
          description: 'Welcome email after signup',
          channel: 'email',
          frequency: 'once',
          content: 'Welcome to our platform!',
          expectedEngagement: 80
        },
        {
          type: 'webinar',
          name: 'Product Demo',
          description: 'Live product demonstration',
          channel: 'webinar',
          frequency: 'weekly',
          content: 'Live demo of key features',
          expectedEngagement: 70
        },
        {
          type: 'support',
          name: 'Setup Call',
          description: 'One-on-one setup assistance',
          channel: 'phone',
          frequency: 'once',
          content: 'Personalized setup guidance',
          expectedEngagement: 90
        }
      ],
      metrics: [
        'website_visits',
        'content_engagement',
        'demo_attendance',
        'trial_signup',
        'contract_signed',
        'setup_completion',
        'feature_adoption',
        'usage_frequency',
        'satisfaction_score',
        'renewal_rate',
        'referrals'
      ],
      insights: [
        'engagement_patterns',
        'conversion_barriers',
        'churn_indicators',
        'advocacy_opportunities',
        'upsell_potential'
      ],
      created: new Date(),
      updated: new Date()
    };

    this.templates.set(saasB2BTemplate.id, saasB2BTemplate);
  }

  private startAnalysis(): void {
    this.analysisInterval = setInterval(() => {
      this.processAnalysisQueue();
    }, 30000); // Cada 30 segundos
  }

  stopAnalysis(): void {
    if (this.analysisInterval) {
      clearInterval(this.analysisInterval);
      this.analysisInterval = null;
    }
  }

  private async processAnalysisQueue(): Promise<void> {
    if (this.isAnalyzing || this.analysisQueue.length === 0) return;

    this.isAnalyzing = true;
    const journeyId = this.analysisQueue.shift();

    try {
      await this.analyzeJourney(journeyId!);
    } catch (error) {
      console.error('Error analyzing journey:', error);
    } finally {
      this.isAnalyzing = false;
    }
  }

  private async analyzeJourney(journeyId: string): Promise<void> {
    const journey = this.journeys.get(journeyId);
    if (!journey) return;

    // Analizar patrones de engagement
    const engagementPatterns = this.analyzeEngagementPatterns(journey);
    
    // Detectar anomalías
    const anomalies = this.detectAnomalies(journey);
    
    // Identificar oportunidades
    const opportunities = this.identifyOpportunities(journey);
    
    // Evaluar riesgo de churn
    const churnRisk = this.evaluateChurnRisk(journey);
    
    // Generar insights
    const insights = this.generateInsights(journey, engagementPatterns, anomalies, opportunities, churnRisk);
    
    // Generar recomendaciones
    const recommendations = this.generateRecommendations(journey, insights);
    
    // Actualizar journey
    journey.insights = insights;
    journey.recommendations = recommendations;
    journey.metrics.churnRisk = churnRisk;
    journey.updatedAt = new Date();
    
    this.journeys.set(journeyId, journey);
    this.emit('journey_analyzed', journey);
  }

  private analyzeEngagementPatterns(journey: CustomerJourney): any {
    const touchpoints = journey.touchpoints;
    const patterns = {
      averageEngagement: 0,
      engagementTrend: 'stable',
      preferredChannels: [],
      optimalTiming: [],
      contentPreferences: []
    };

    if (touchpoints.length === 0) return patterns;

    // Calcular engagement promedio
    patterns.averageEngagement = touchpoints.reduce((sum, tp) => sum + tp.engagement, 0) / touchpoints.length;

    // Analizar tendencia de engagement
    const recentTouchpoints = touchpoints.slice(-5);
    const olderTouchpoints = touchpoints.slice(-10, -5);
    
    if (recentTouchpoints.length > 0 && olderTouchpoints.length > 0) {
      const recentAvg = recentTouchpoints.reduce((sum, tp) => sum + tp.engagement, 0) / recentTouchpoints.length;
      const olderAvg = olderTouchpoints.reduce((sum, tp) => sum + tp.engagement, 0) / olderTouchpoints.length;
      
      if (recentAvg > olderAvg * 1.1) patterns.engagementTrend = 'increasing';
      else if (recentAvg < olderAvg * 0.9) patterns.engagementTrend = 'decreasing';
    }

    // Identificar canales preferidos
    const channelEngagement = touchpoints.reduce((acc, tp) => {
      acc[tp.channel] = (acc[tp.channel] || 0) + tp.engagement;
      return acc;
    }, {} as Record<string, number>);
    
    patterns.preferredChannels = Object.entries(channelEngagement)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([channel]) => channel);

    return patterns;
  }

  private detectAnomalies(journey: CustomerJourney): any[] {
    const anomalies = [];
    const touchpoints = journey.touchpoints;

    // Detectar caída en engagement
    if (touchpoints.length >= 3) {
      const recent = touchpoints.slice(-3);
      const avgRecent = recent.reduce((sum, tp) => sum + tp.engagement, 0) / recent.length;
      const avgOverall = touchpoints.reduce((sum, tp) => sum + tp.engagement, 0) / touchpoints.length;
      
      if (avgRecent < avgOverall * 0.5) {
        anomalies.push({
          type: 'engagement_drop',
          severity: 'high',
          description: 'Significant drop in engagement detected',
          value: avgRecent,
          threshold: avgOverall * 0.5
        });
      }
    }

    // Detectar inactividad prolongada
    const lastActivity = journey.lastActivityAt;
    const daysSinceActivity = (Date.now() - lastActivity.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceActivity > 30) {
      anomalies.push({
        type: 'inactivity',
        severity: 'medium',
        description: 'Customer has been inactive for extended period',
        value: daysSinceActivity,
        threshold: 30
      });
    }

    // Detectar feedback negativo
    const negativeFeedback = touchpoints.filter(tp => tp.sentiment === 'negative');
    if (negativeFeedback.length > 2) {
      anomalies.push({
        type: 'negative_feedback',
        severity: 'high',
        description: 'Multiple negative feedback instances detected',
        value: negativeFeedback.length,
        threshold: 2
      });
    }

    return anomalies;
  }

  private identifyOpportunities(journey: CustomerJourney): any[] {
    const opportunities = [];
    const touchpoints = journey.touchpoints;

    // Oportunidad de upsell
    if (journey.stage === 'adoption' && journey.metrics.satisfactionScore > 80) {
      opportunities.push({
        type: 'upsell',
        priority: 'medium',
        description: 'High satisfaction customer ready for upsell',
        confidence: 0.8
      });
    }

    // Oportunidad de advocacy
    if (journey.stage === 'retention' && journey.metrics.advocacyScore > 70) {
      opportunities.push({
        type: 'advocacy',
        priority: 'high',
        description: 'Customer ready to become advocate',
        confidence: 0.9
      });
    }

    // Oportunidad de re-engagement
    if (journey.metrics.lastActivityDays > 14 && journey.metrics.lastActivityDays < 30) {
      opportunities.push({
        type: 're_engagement',
        priority: 'high',
        description: 'Customer showing signs of disengagement',
        confidence: 0.7
      });
    }

    return opportunities;
  }

  private evaluateChurnRisk(journey: CustomerJourney): number {
    let riskScore = 0;
    const touchpoints = journey.touchpoints;

    // Factores de riesgo
    if (journey.metrics.lastActivityDays > 30) riskScore += 30;
    if (journey.metrics.satisfactionScore < 60) riskScore += 25;
    if (touchpoints.filter(tp => tp.sentiment === 'negative').length > 1) riskScore += 20;
    if (journey.metrics.averageEngagement < 40) riskScore += 15;
    if (journey.stage === 'churn') riskScore += 50;

    // Factores de retención
    if (journey.metrics.satisfactionScore > 80) riskScore -= 20;
    if (journey.metrics.advocacyScore > 70) riskScore -= 15;
    if (touchpoints.filter(tp => tp.sentiment === 'positive').length > 3) riskScore -= 10;

    return Math.max(0, Math.min(100, riskScore));
  }

  private generateInsights(journey: CustomerJourney, patterns: any, anomalies: any[], opportunities: any[], churnRisk: number): JourneyInsight[] {
    const insights: JourneyInsight[] = [];

    // Insight de engagement
    if (patterns.engagementTrend === 'increasing') {
      insights.push({
        id: `insight_${Date.now()}_1`,
        type: 'pattern',
        title: 'Increasing Engagement Trend',
        description: 'Customer engagement is showing positive trend',
        confidence: 85,
        impact: 'medium',
        actionable: true,
        recommendations: ['Continue current engagement strategy', 'Identify successful touchpoints'],
        generatedAt: new Date()
      });
    }

    // Insight de anomalías
    anomalies.forEach(anomaly => {
      insights.push({
        id: `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'anomaly',
        title: `${anomaly.type.replace('_', ' ').toUpperCase()}`,
        description: anomaly.description,
        confidence: 90,
        impact: anomaly.severity === 'high' ? 'high' : 'medium',
        actionable: true,
        recommendations: this.getAnomalyRecommendations(anomaly),
        generatedAt: new Date()
      });
    });

    // Insight de oportunidades
    opportunities.forEach(opportunity => {
      insights.push({
        id: `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'opportunity',
        title: `${opportunity.type.replace('_', ' ').toUpperCase()} Opportunity`,
        description: opportunity.description,
        confidence: Math.round(opportunity.confidence * 100),
        impact: opportunity.priority === 'high' ? 'high' : 'medium',
        actionable: true,
        recommendations: this.getOpportunityRecommendations(opportunity),
        generatedAt: new Date()
      });
    });

    // Insight de riesgo de churn
    if (churnRisk > 70) {
      insights.push({
        id: `insight_${Date.now()}_churn`,
        type: 'risk',
        title: 'High Churn Risk',
        description: `Customer shows high churn risk (${churnRisk}%)`,
        confidence: 95,
        impact: 'critical',
        actionable: true,
        recommendations: ['Immediate intervention required', 'Personal outreach needed', 'Review satisfaction issues'],
        generatedAt: new Date()
      });
    }

    return insights;
  }

  private generateRecommendations(journey: CustomerJourney, insights: JourneyInsight[]): JourneyRecommendation[] {
    const recommendations: JourneyRecommendation[] = [];

    // Recomendaciones basadas en insights
    insights.forEach(insight => {
      if (insight.actionable) {
        insight.recommendations.forEach(rec => {
          recommendations.push({
            id: `rec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: this.getRecommendationType(insight.type),
            title: rec,
            description: `Actionable recommendation based on ${insight.type} insight`,
            priority: insight.impact === 'critical' ? 'urgent' : insight.impact === 'high' ? 'high' : 'medium',
            effort: 'medium',
            impact: insight.impact,
            actions: [rec],
            expectedOutcome: this.getExpectedOutcome(insight.type),
            generatedAt: new Date()
          });
        });
      }
    });

    // Recomendaciones basadas en etapa del journey
    const stageRecommendations = this.getStageRecommendations(journey.stage);
    recommendations.push(...stageRecommendations);

    return recommendations;
  }

  private getAnomalyRecommendations(anomaly: any): string[] {
    switch (anomaly.type) {
      case 'engagement_drop':
        return ['Investigate recent touchpoints', 'Send re-engagement campaign', 'Schedule personal outreach'];
      case 'inactivity':
        return ['Send re-engagement email', 'Offer special promotion', 'Schedule check-in call'];
      case 'negative_feedback':
        return ['Address feedback immediately', 'Schedule satisfaction call', 'Review product issues'];
      default:
        return ['Investigate further', 'Monitor closely'];
    }
  }

  private getOpportunityRecommendations(opportunity: any): string[] {
    switch (opportunity.type) {
      case 'upsell':
        return ['Present upsell options', 'Schedule sales call', 'Offer premium features'];
      case 'advocacy':
        return ['Request testimonial', 'Ask for referral', 'Invite to case study'];
      case 're_engagement':
        return ['Send personalized content', 'Offer exclusive access', 'Schedule demo call'];
      default:
        return ['Follow up on opportunity', 'Monitor progress'];
    }
  }

  private getRecommendationType(insightType: string): 'engagement' | 'conversion' | 'retention' | 'upsell' | 'advocacy' {
    switch (insightType) {
      case 'pattern': return 'engagement';
      case 'anomaly': return 'retention';
      case 'opportunity': return 'upsell';
      case 'risk': return 'retention';
      case 'trend': return 'engagement';
      default: return 'engagement';
    }
  }

  private getExpectedOutcome(insightType: string): string {
    switch (insightType) {
      case 'pattern': return 'Improved engagement and satisfaction';
      case 'anomaly': return 'Issue resolution and customer retention';
      case 'opportunity': return 'Increased revenue and growth';
      case 'risk': return 'Risk mitigation and retention';
      case 'trend': return 'Optimized customer experience';
      default: return 'Improved customer relationship';
    }
  }

  private getStageRecommendations(stage: string): JourneyRecommendation[] {
    const recommendations: JourneyRecommendation[] = [];

    switch (stage) {
      case 'awareness':
        recommendations.push({
          id: `stage_rec_${Date.now()}_1`,
          type: 'engagement',
          title: 'Increase Content Engagement',
          description: 'Provide valuable content to build awareness',
          priority: 'medium',
          effort: 'low',
          impact: 'medium',
          actions: ['Create educational content', 'Share industry insights', 'Host webinars'],
          expectedOutcome: 'Increased brand awareness and engagement',
          generatedAt: new Date()
        });
        break;
      case 'consideration':
        recommendations.push({
          id: `stage_rec_${Date.now()}_2`,
          type: 'conversion',
          title: 'Schedule Product Demo',
          description: 'Show product value through demonstration',
          priority: 'high',
          effort: 'medium',
          impact: 'high',
          actions: ['Schedule demo call', 'Prepare customized demo', 'Follow up after demo'],
          expectedOutcome: 'Increased conversion to trial/purchase',
          generatedAt: new Date()
        });
        break;
      case 'onboarding':
        recommendations.push({
          id: `stage_rec_${Date.now()}_3`,
          type: 'engagement',
          title: 'Provide Setup Support',
          description: 'Ensure smooth onboarding experience',
          priority: 'high',
          effort: 'medium',
          impact: 'high',
          actions: ['Schedule setup call', 'Provide training materials', 'Assign success manager'],
          expectedOutcome: 'Faster time to value and higher satisfaction',
          generatedAt: new Date()
        });
        break;
    }

    return recommendations;
  }

  // Crear journey
  createJourney(customerId: string, customerEmail: string, journeyName: string, templateId?: string): string {
    const journeyId = `journey_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const journey: CustomerJourney = {
      id: journeyId,
      customerId,
      customerEmail,
      journeyName,
      stage: 'awareness',
      touchpoints: [],
      timeline: [],
      metrics: {
        totalTouchpoints: 0,
        averageEngagement: 0,
        timeInStage: 0,
        conversionRate: 0,
        churnRisk: 0,
        advocacyScore: 0,
        satisfactionScore: 0,
        lastActivityDays: 0,
        stageProgression: []
      },
      insights: [],
      recommendations: [],
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date(),
      lastActivityAt: new Date()
    };

    this.journeys.set(journeyId, journey);
    this.emit('journey_created', journey);
    return journeyId;
  }

  // Agregar touchpoint
  addTouchpoint(journeyId: string, touchpoint: Omit<CustomerTouchpoint, 'id' | 'timestamp'>): void {
    const journey = this.journeys.get(journeyId);
    if (!journey) return;

    const newTouchpoint: CustomerTouchpoint = {
      ...touchpoint,
      id: `touchpoint_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };

    journey.touchpoints.push(newTouchpoint);
    journey.lastActivityAt = new Date();
    journey.updatedAt = new Date();

    // Actualizar métricas
    this.updateJourneyMetrics(journey);

    this.journeys.set(journeyId, journey);
    this.emit('touchpoint_added', { journeyId, touchpoint: newTouchpoint });

    // Agregar a cola de análisis
    if (!this.analysisQueue.includes(journeyId)) {
      this.analysisQueue.push(journeyId);
    }
  }

  private updateJourneyMetrics(journey: CustomerJourney): void {
    const touchpoints = journey.touchpoints;
    
    journey.metrics.totalTouchpoints = touchpoints.length;
    journey.metrics.averageEngagement = touchpoints.length > 0 
      ? touchpoints.reduce((sum, tp) => sum + tp.engagement, 0) / touchpoints.length 
      : 0;
    
    // Calcular días desde última actividad
    const now = new Date();
    journey.metrics.lastActivityDays = Math.floor((now.getTime() - journey.lastActivityAt.getTime()) / (1000 * 60 * 60 * 24));
    
    // Calcular satisfacción basada en sentimientos
    const positiveTouchpoints = touchpoints.filter(tp => tp.sentiment === 'positive').length;
    const totalTouchpoints = touchpoints.length;
    journey.metrics.satisfactionScore = totalTouchpoints > 0 ? (positiveTouchpoints / totalTouchpoints) * 100 : 0;
  }

  // Obtener journeys
  getJourneys(limit?: number): CustomerJourney[] {
    const journeys = Array.from(this.journeys.values())
      .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
    
    return limit ? journeys.slice(0, limit) : journeys;
  }

  // Obtener journey específico
  getJourney(journeyId: string): CustomerJourney | undefined {
    return this.journeys.get(journeyId);
  }

  // Obtener templates
  getTemplates(): JourneyTemplate[] {
    return Array.from(this.templates.values());
  }

  // Obtener estadísticas
  getStats(): {
    totalJourneys: number;
    activeJourneys: number;
    completedJourneys: number;
    churnedJourneys: number;
    averageChurnRisk: number;
    averageSatisfaction: number;
    totalInsights: number;
    totalRecommendations: number;
  } {
    const journeys = Array.from(this.journeys.values());
    
    const totalJourneys = journeys.length;
    const activeJourneys = journeys.filter(j => j.status === 'active').length;
    const completedJourneys = journeys.filter(j => j.status === 'completed').length;
    const churnedJourneys = journeys.filter(j => j.status === 'churned').length;
    
    const averageChurnRisk = journeys.length > 0 
      ? journeys.reduce((sum, j) => sum + j.metrics.churnRisk, 0) / journeys.length 
      : 0;
    
    const averageSatisfaction = journeys.length > 0 
      ? journeys.reduce((sum, j) => sum + j.metrics.satisfactionScore, 0) / journeys.length 
      : 0;
    
    const totalInsights = journeys.reduce((sum, j) => sum + j.insights.length, 0);
    const totalRecommendations = journeys.reduce((sum, j) => sum + j.recommendations.length, 0);
    
    return {
      totalJourneys,
      activeJourneys,
      completedJourneys,
      churnedJourneys,
      averageChurnRisk,
      averageSatisfaction,
      totalInsights,
      totalRecommendations
    };
  }
}

export const advancedCustomerJourneyService = new AdvancedCustomerJourneyService();






