import { EventEmitter } from 'events';
import { CustomerFeedback } from './customerFeedbackService';

export interface CustomerProfile {
  id: string;
  customerId: string;
  email: string;
  name?: string;
  company?: string;
  industry?: string;
  region: string;
  language: string;
  preferences: CustomerPreferences;
  behavior: CustomerBehavior;
  demographics: CustomerDemographics;
  psychographics: CustomerPsychographics;
  engagement: CustomerEngagement;
  journey: CustomerJourneyProfile;
  segments: string[];
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  lastActivityAt: Date;
}

export interface CustomerPreferences {
  communication: {
    preferredChannels: string[];
    frequency: 'low' | 'medium' | 'high';
    timing: string[];
    language: string;
    format: 'text' | 'html' | 'video' | 'audio';
  };
  content: {
    topics: string[];
    formats: string[];
    length: 'short' | 'medium' | 'long';
    complexity: 'basic' | 'intermediate' | 'advanced';
  };
  product: {
    features: string[];
    integrations: string[];
    pricing: 'basic' | 'premium' | 'enterprise';
    support: 'self-service' | 'assisted' | 'dedicated';
  };
  experience: {
    ui: 'simple' | 'detailed' | 'customizable';
    workflow: 'guided' | 'flexible' | 'expert';
    notifications: 'minimal' | 'moderate' | 'comprehensive';
  };
}

export interface CustomerBehavior {
  patterns: {
    loginFrequency: number;
    sessionDuration: number;
    featureUsage: Record<string, number>;
    contentConsumption: Record<string, number>;
    supportInteractions: number;
    feedbackFrequency: number;
  };
  trends: {
    engagementTrend: 'increasing' | 'stable' | 'decreasing';
    usageTrend: 'growing' | 'stable' | 'declining';
    satisfactionTrend: 'improving' | 'stable' | 'declining';
    activityTrend: 'more_active' | 'stable' | 'less_active';
  };
  triggers: {
    positive: string[];
    negative: string[];
    neutral: string[];
  };
  responses: {
    toEmails: number;
    toNotifications: number;
    toSurveys: number;
    toOffers: number;
  };
}

export interface CustomerDemographics {
  age: {
    range: '18-24' | '25-34' | '35-44' | '45-54' | '55-64' | '65+';
    confidence: number;
  };
  gender: {
    value: 'male' | 'female' | 'other' | 'unknown';
    confidence: number;
  };
  location: {
    country: string;
    region: string;
    city: string;
    timezone: string;
  };
  professional: {
    role: string;
    seniority: 'junior' | 'mid' | 'senior' | 'executive';
    department: string;
    companySize: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
    industry: string;
  };
  technical: {
    skillLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    preferredTools: string[];
    deviceTypes: string[];
    browserPreferences: string[];
  };
}

export interface CustomerPsychographics {
  personality: {
    traits: {
      openness: number;
      conscientiousness: number;
      extraversion: number;
      agreeableness: number;
      neuroticism: number;
    };
    type: 'analyst' | 'diplomat' | 'sentinel' | 'explorer';
  };
  values: {
    personal: string[];
    professional: string[];
    cultural: string[];
  };
  motivations: {
    primary: string[];
    secondary: string[];
    drivers: string[];
    barriers: string[];
  };
  communication: {
    style: 'direct' | 'diplomatic' | 'analytical' | 'empathetic';
    tone: 'formal' | 'casual' | 'professional' | 'friendly';
    language: 'technical' | 'business' | 'conversational' | 'academic';
  };
}

export interface CustomerEngagement {
  scores: {
    overall: number;
    content: number;
    product: number;
    support: number;
    community: number;
  };
  metrics: {
    totalInteractions: number;
    averageSessionTime: number;
    featureAdoption: number;
    contentCompletion: number;
    supportSatisfaction: number;
  };
  patterns: {
    peakHours: string[];
    preferredDays: string[];
    seasonalPatterns: Record<string, number>;
    eventResponses: Record<string, number>;
  };
  lifecycle: {
    stage: 'awareness' | 'consideration' | 'trial' | 'adoption' | 'retention' | 'advocacy';
    duration: number;
    progression: string[];
    milestones: string[];
  };
}

export interface CustomerJourneyProfile {
  currentStage: string;
  stageHistory: {
    stage: string;
    enteredAt: Date;
    duration: number;
    touchpoints: number;
    satisfaction: number;
  }[];
  touchpoints: {
    type: string;
    channel: string;
    frequency: number;
    effectiveness: number;
    satisfaction: number;
  }[];
  conversions: {
    type: string;
    date: Date;
    value: number;
    channel: string;
  }[];
  barriers: {
    type: string;
    description: string;
    impact: 'low' | 'medium' | 'high';
    resolution: string;
  }[];
  opportunities: {
    type: string;
    description: string;
    potential: 'low' | 'medium' | 'high';
    action: string;
  }[];
}

export interface PersonalizationRule {
  id: string;
  name: string;
  description: string;
  conditions: PersonalizationCondition[];
  actions: PersonalizationAction[];
  priority: number;
  enabled: boolean;
  targetAudience: {
    segments: string[];
    demographics: Record<string, any>;
    behavior: Record<string, any>;
    psychographics: Record<string, any>;
  };
  performance: {
    impressions: number;
    clicks: number;
    conversions: number;
    satisfaction: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface PersonalizationCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
  weight: number;
}

export interface PersonalizationAction {
  type: 'content' | 'layout' | 'feature' | 'notification' | 'offer' | 'workflow';
  config: Record<string, any>;
  weight: number;
}

export interface PersonalizationResult {
  customerId: string;
  ruleId: string;
  actions: PersonalizationAction[];
  confidence: number;
  reasoning: string[];
  appliedAt: Date;
  expiresAt: Date;
}

export class AdvancedPersonalizationService extends EventEmitter {
  private profiles: Map<string, CustomerProfile> = new Map();
  private rules: Map<string, PersonalizationRule> = new Map();
  private results: Map<string, PersonalizationResult> = new Map();
  private isProcessing: boolean = false;
  private processingQueue: string[] = [];
  private processingInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultRules();
    this.startProcessing();
  }

  private initializeDefaultRules(): void {
    // Regla de personalización para usuarios nuevos
    const newUserRule: PersonalizationRule = {
      id: 'new_user_personalization',
      name: 'New User Onboarding',
      description: 'Personalize experience for new users',
      conditions: [
        {
          field: 'journey.stage',
          operator: 'equals',
          value: 'awareness',
          weight: 1.0
        },
        {
          field: 'behavior.patterns.loginFrequency',
          operator: 'less_than',
          value: 5,
          weight: 0.8
        }
      ],
      actions: [
        {
          type: 'content',
          config: {
            showOnboarding: true,
            highlightFeatures: ['getting_started', 'tutorials', 'help'],
            contentType: 'educational'
          },
          weight: 1.0
        },
        {
          type: 'notification',
          config: {
            type: 'welcome_series',
            frequency: 'daily',
            duration: 7
          },
          weight: 0.9
        }
      ],
      priority: 1,
      enabled: true,
      targetAudience: {
        segments: ['new_users'],
        demographics: {},
        behavior: {},
        psychographics: {}
      },
      performance: {
        impressions: 0,
        clicks: 0,
        conversions: 0,
        satisfaction: 0
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Regla de personalización para usuarios de alto engagement
    const highEngagementRule: PersonalizationRule = {
      id: 'high_engagement_personalization',
      name: 'High Engagement Users',
      description: 'Personalize experience for highly engaged users',
      conditions: [
        {
          field: 'engagement.scores.overall',
          operator: 'greater_than',
          value: 0.8,
          weight: 1.0
        },
        {
          field: 'behavior.patterns.featureUsage',
          operator: 'greater_than',
          value: 0.7,
          weight: 0.9
        }
      ],
      actions: [
        {
          type: 'content',
          config: {
            showAdvancedFeatures: true,
            highlightNewFeatures: true,
            contentType: 'advanced'
          },
          weight: 1.0
        },
        {
          type: 'offer',
          config: {
            type: 'upsell',
            features: ['premium', 'enterprise'],
            discount: 0.1
          },
          weight: 0.8
        }
      ],
      priority: 2,
      enabled: true,
      targetAudience: {
        segments: ['high_engagement'],
        demographics: {},
        behavior: {},
        psychographics: {}
      },
      performance: {
        impressions: 0,
        clicks: 0,
        conversions: 0,
        satisfaction: 0
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Regla de personalización para usuarios en riesgo de churn
    const churnRiskRule: PersonalizationRule = {
      id: 'churn_risk_personalization',
      name: 'Churn Risk Intervention',
      description: 'Personalize experience for users at risk of churning',
      conditions: [
        {
          field: 'engagement.scores.overall',
          operator: 'less_than',
          value: 0.3,
          weight: 1.0
        },
        {
          field: 'behavior.patterns.loginFrequency',
          operator: 'less_than',
          value: 2,
          weight: 0.9
        }
      ],
      actions: [
        {
          type: 'notification',
          config: {
            type: 'retention_campaign',
            frequency: 'daily',
            duration: 14
          },
          weight: 1.0
        },
        {
          type: 'offer',
          config: {
            type: 'retention',
            features: ['support', 'training', 'consultation'],
            discount: 0.2
          },
          weight: 0.9
        }
      ],
      priority: 3,
      enabled: true,
      targetAudience: {
        segments: ['churn_risk'],
        demographics: {},
        behavior: {},
        psychographics: {}
      },
      performance: {
        impressions: 0,
        clicks: 0,
        conversions: 0,
        satisfaction: 0
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.rules.set(newUserRule.id, newUserRule);
    this.rules.set(highEngagementRule.id, highEngagementRule);
    this.rules.set(churnRiskRule.id, churnRiskRule);
  }

  private startProcessing(): void {
    this.processingInterval = setInterval(() => {
      this.processQueue();
    }, 5000); // Cada 5 segundos
  }

  stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
    }
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.processingQueue.length === 0) return;

    this.isProcessing = true;
    const customerId = this.processingQueue.shift();

    try {
      await this.processPersonalization(customerId!);
    } catch (error) {
      console.error('Error processing personalization:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  private async processPersonalization(customerId: string): Promise<void> {
    const profile = this.profiles.get(customerId);
    if (!profile) return;

    const applicableRules = this.getApplicableRules(profile);
    const results: PersonalizationResult[] = [];

    for (const rule of applicableRules) {
      const result = this.applyRule(profile, rule);
      if (result) {
        results.push(result);
        this.results.set(result.customerId, result);
        this.emit('personalization_applied', result);
      }
    }

    // Actualizar perfil con resultados
    profile.updatedAt = new Date();
    this.profiles.set(customerId, profile);
  }

  private getApplicableRules(profile: CustomerProfile): PersonalizationRule[] {
    const applicableRules: PersonalizationRule[] = [];

    for (const rule of this.rules.values()) {
      if (!rule.enabled) continue;

      if (this.evaluateRule(profile, rule)) {
        applicableRules.push(rule);
      }
    }

    return applicableRules.sort((a, b) => b.priority - a.priority);
  }

  private evaluateRule(profile: CustomerProfile, rule: PersonalizationRule): boolean {
    let totalWeight = 0;
    let matchedWeight = 0;

    for (const condition of rule.conditions) {
      totalWeight += condition.weight;
      
      if (this.evaluateCondition(profile, condition)) {
        matchedWeight += condition.weight;
      }
    }

    // Si el peso coincidente es al menos el 70% del peso total, la regla se aplica
    return matchedWeight >= totalWeight * 0.7;
  }

  private evaluateCondition(profile: CustomerProfile, condition: PersonalizationCondition): boolean {
    const value = this.getFieldValue(profile, condition.field);
    
    switch (condition.operator) {
      case 'equals':
        return value === condition.value;
      case 'not_equals':
        return value !== condition.value;
      case 'contains':
        return typeof value === 'string' && value.includes(condition.value);
      case 'greater_than':
        return typeof value === 'number' && value > condition.value;
      case 'less_than':
        return typeof value === 'number' && value < condition.value;
      case 'in':
        return Array.isArray(condition.value) && condition.value.includes(value);
      case 'not_in':
        return Array.isArray(condition.value) && !condition.value.includes(value);
      default:
        return false;
    }
  }

  private getFieldValue(profile: CustomerProfile, field: string): any {
    const parts = field.split('.');
    let value: any = profile;

    for (const part of parts) {
      if (value && typeof value === 'object' && part in value) {
        value = value[part];
      } else {
        return undefined;
      }
    }

    return value;
  }

  private applyRule(profile: CustomerProfile, rule: PersonalizationRule): PersonalizationResult | null {
    const result: PersonalizationResult = {
      customerId: profile.customerId,
      ruleId: rule.id,
      actions: rule.actions,
      confidence: this.calculateConfidence(profile, rule),
      reasoning: this.generateReasoning(profile, rule),
      appliedAt: new Date(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 horas
    };

    // Actualizar métricas de rendimiento de la regla
    rule.performance.impressions++;
    
    return result;
  }

  private calculateConfidence(profile: CustomerProfile, rule: PersonalizationRule): number {
    let totalWeight = 0;
    let matchedWeight = 0;

    for (const condition of rule.conditions) {
      totalWeight += condition.weight;
      
      if (this.evaluateCondition(profile, condition)) {
        matchedWeight += condition.weight;
      }
    }

    return totalWeight > 0 ? matchedWeight / totalWeight : 0;
  }

  private generateReasoning(profile: CustomerProfile, rule: PersonalizationRule): string[] {
    const reasoning: string[] = [];

    for (const condition of rule.conditions) {
      if (this.evaluateCondition(profile, condition)) {
        reasoning.push(`Matched condition: ${condition.field} ${condition.operator} ${condition.value}`);
      }
    }

    return reasoning;
  }

  // Crear perfil de cliente
  createProfile(customerId: string, email: string, initialData: Partial<CustomerProfile> = {}): string {
    const profile: CustomerProfile = {
      id: `profile_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      customerId,
      email,
      name: initialData.name,
      company: initialData.company,
      industry: initialData.industry,
      region: initialData.region || 'MX',
      language: initialData.language || 'es',
      preferences: {
        communication: {
          preferredChannels: ['email'],
          frequency: 'medium',
          timing: ['09:00', '14:00'],
          language: 'es',
          format: 'html'
        },
        content: {
          topics: [],
          formats: ['text', 'video'],
          length: 'medium',
          complexity: 'intermediate'
        },
        product: {
          features: [],
          integrations: [],
          pricing: 'basic',
          support: 'self-service'
        },
        experience: {
          ui: 'simple',
          workflow: 'guided',
          notifications: 'moderate'
        }
      },
      behavior: {
        patterns: {
          loginFrequency: 0,
          sessionDuration: 0,
          featureUsage: {},
          contentConsumption: {},
          supportInteractions: 0,
          feedbackFrequency: 0
        },
        trends: {
          engagementTrend: 'stable',
          usageTrend: 'stable',
          satisfactionTrend: 'stable',
          activityTrend: 'stable'
        },
        triggers: {
          positive: [],
          negative: [],
          neutral: []
        },
        responses: {
          toEmails: 0,
          toNotifications: 0,
          toSurveys: 0,
          toOffers: 0
        }
      },
      demographics: {
        age: {
          range: '25-34',
          confidence: 0.5
        },
        gender: {
          value: 'unknown',
          confidence: 0.5
        },
        location: {
          country: 'MX',
          region: 'MX',
          city: 'Mexico City',
          timezone: 'America/Mexico_City'
        },
        professional: {
          role: 'unknown',
          seniority: 'mid',
          department: 'unknown',
          companySize: 'medium',
          industry: 'unknown'
        },
        technical: {
          skillLevel: 'intermediate',
          preferredTools: [],
          deviceTypes: ['desktop', 'mobile'],
          browserPreferences: ['chrome', 'firefox']
        }
      },
      psychographics: {
        personality: {
          traits: {
            openness: 0.5,
            conscientiousness: 0.5,
            extraversion: 0.5,
            agreeableness: 0.5,
            neuroticism: 0.5
          },
          type: 'analyst'
        },
        values: {
          personal: [],
          professional: [],
          cultural: []
        },
        motivations: {
          primary: [],
          secondary: [],
          drivers: [],
          barriers: []
        },
        communication: {
          style: 'professional',
          tone: 'formal',
          language: 'business'
        }
      },
      engagement: {
        scores: {
          overall: 0.5,
          content: 0.5,
          product: 0.5,
          support: 0.5,
          community: 0.5
        },
        metrics: {
          totalInteractions: 0,
          averageSessionTime: 0,
          featureAdoption: 0,
          contentCompletion: 0,
          supportSatisfaction: 0
        },
        patterns: {
          peakHours: [],
          preferredDays: [],
          seasonalPatterns: {},
          eventResponses: {}
        },
        lifecycle: {
          stage: 'awareness',
          duration: 0,
          progression: [],
          milestones: []
        }
      },
      journey: {
        currentStage: 'awareness',
        stageHistory: [],
        touchpoints: [],
        conversions: [],
        barriers: [],
        opportunities: []
      },
      segments: [],
      tags: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      lastActivityAt: new Date(),
      ...initialData
    };

    this.profiles.set(customerId, profile);
    this.emit('profile_created', profile);

    // Agregar a cola de procesamiento
    if (!this.processingQueue.includes(customerId)) {
      this.processingQueue.push(customerId);
    }

    return profile.id;
  }

  // Actualizar perfil
  updateProfile(customerId: string, updates: Partial<CustomerProfile>): void {
    const profile = this.profiles.get(customerId);
    if (!profile) return;

    Object.assign(profile, updates);
    profile.updatedAt = new Date();
    
    this.profiles.set(customerId, profile);
    this.emit('profile_updated', profile);

    // Agregar a cola de procesamiento
    if (!this.processingQueue.includes(customerId)) {
      this.processingQueue.push(customerId);
    }
  }

  // Obtener perfil
  getProfile(customerId: string): CustomerProfile | undefined {
    return this.profiles.get(customerId);
  }

  // Obtener personalización
  getPersonalization(customerId: string): PersonalizationResult[] {
    const results: PersonalizationResult[] = [];
    
    for (const result of this.results.values()) {
      if (result.customerId === customerId && result.expiresAt > new Date()) {
        results.push(result);
      }
    }
    
    return results.sort((a, b) => b.appliedAt.getTime() - a.appliedAt.getTime());
  }

  // Obtener reglas
  getRules(): PersonalizationRule[] {
    return Array.from(this.rules.values());
  }

  // Crear regla
  createRule(rule: Omit<PersonalizationRule, 'id' | 'createdAt' | 'updatedAt' | 'performance'>): string {
    const id = `rule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newRule: PersonalizationRule = {
      ...rule,
      id,
      createdAt: new Date(),
      updatedAt: new Date(),
      performance: {
        impressions: 0,
        clicks: 0,
        conversions: 0,
        satisfaction: 0
      }
    };

    this.rules.set(id, newRule);
    this.emit('rule_created', newRule);
    return id;
  }

  // Obtener estadísticas
  getStats(): {
    totalProfiles: number;
    totalRules: number;
    totalResults: number;
    averageConfidence: number;
    topPerformingRules: PersonalizationRule[];
  } {
    const profiles = Array.from(this.profiles.values());
    const rules = Array.from(this.rules.values());
    const results = Array.from(this.results.values());

    const averageConfidence = results.length > 0 
      ? results.reduce((sum, r) => sum + r.confidence, 0) / results.length 
      : 0;

    const topPerformingRules = rules
      .sort((a, b) => b.performance.conversions - a.performance.conversions)
      .slice(0, 5);

    return {
      totalProfiles: profiles.length,
      totalRules: rules.length,
      totalResults: results.length,
      averageConfidence,
      topPerformingRules
    };
  }
}

export const advancedPersonalizationService = new AdvancedPersonalizationService();

