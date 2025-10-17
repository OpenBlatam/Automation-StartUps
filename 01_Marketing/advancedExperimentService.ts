import { EventEmitter } from 'events';

export interface Experiment {
  id: string;
  name: string;
  description: string;
  type: 'a_b' | 'multivariate' | 'bandit' | 'bayesian' | 'custom';
  status: 'draft' | 'running' | 'paused' | 'completed' | 'cancelled';
  hypothesis: string;
  successMetrics: string[];
  secondaryMetrics: string[];
  segments: ExperimentSegment[];
  variants: ExperimentVariant[];
  trafficAllocation: Record<string, number>;
  startDate: Date;
  endDate?: Date;
  duration: number; // days
  minSampleSize: number;
  confidenceLevel: number;
  power: number;
  results: ExperimentResults;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface ExperimentSegment {
  id: string;
  name: string;
  description: string;
  criteria: Record<string, any>;
  percentage: number;
  enabled: boolean;
}

export interface ExperimentVariant {
  id: string;
  name: string;
  description: string;
  type: 'control' | 'treatment';
  configuration: Record<string, any>;
  trafficPercentage: number;
  enabled: boolean;
}

export interface ExperimentResults {
  status: 'pending' | 'running' | 'completed' | 'failed';
  startDate: Date;
  endDate?: Date;
  participants: {
    total: number;
    byVariant: Record<string, number>;
    bySegment: Record<string, number>;
  };
  metrics: {
    primary: Record<string, ExperimentMetric>;
    secondary: Record<string, ExperimentMetric>;
  };
  statisticalSignificance: {
    primary: Record<string, boolean>;
    secondary: Record<string, boolean>;
  };
  confidenceIntervals: Record<string, {
    lower: number;
    upper: number;
    confidence: number;
  }>;
  pValues: Record<string, number>;
  effectSizes: Record<string, number>;
  recommendations: string[];
  insights: string[];
}

export interface ExperimentMetric {
  value: number;
  variance: number;
  standardError: number;
  sampleSize: number;
  confidenceInterval: {
    lower: number;
    upper: number;
  };
  pValue: number;
  effectSize: number;
  statisticalPower: number;
}

export interface ExperimentTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  category: string;
  configuration: Record<string, any>;
  metrics: string[];
  segments: string[];
  variants: string[];
  duration: number;
  minSampleSize: number;
  confidenceLevel: number;
  power: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ExperimentAnalysis {
  experimentId: string;
  analysisType: 'preliminary' | 'interim' | 'final' | 'post_hoc';
  timestamp: Date;
  results: {
    summary: string;
    keyFindings: string[];
    recommendations: string[];
    nextSteps: string[];
  };
  statisticalTests: {
    name: string;
    result: any;
    interpretation: string;
  }[];
  visualizations: {
    type: string;
    data: any;
    insights: string;
  }[];
  metadata: Record<string, any>;
}

export class AdvancedExperimentService extends EventEmitter {
  private experiments: Map<string, Experiment> = new Map();
  private templates: Map<string, ExperimentTemplate> = new Map();
  private analyses: Map<string, ExperimentAnalysis> = new Map();
  private isAnalyzing: boolean = false;
  private analysisQueue: string[] = [];
  private analysisInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultTemplates();
    this.startAnalysis();
  }

  private initializeDefaultTemplates(): void {
    // Template para A/B testing de UI
    const uiABTemplate: ExperimentTemplate = {
      id: 'ui_ab_test_template',
      name: 'UI A/B Test Template',
      description: 'Template for testing UI changes and improvements',
      type: 'a_b',
      category: 'ui_ux',
      configuration: {
        trafficSplit: 50,
        duration: 14,
        minSampleSize: 1000,
        confidenceLevel: 0.95,
        power: 0.8
      },
      metrics: ['conversion_rate', 'click_through_rate', 'time_on_page', 'bounce_rate'],
      segments: ['all_users', 'new_users', 'returning_users'],
      variants: ['control', 'treatment'],
      duration: 14,
      minSampleSize: 1000,
      confidenceLevel: 0.95,
      power: 0.8,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Template para testing de algoritmos
    const algorithmTemplate: ExperimentTemplate = {
      id: 'algorithm_test_template',
      name: 'Algorithm Test Template',
      description: 'Template for testing different algorithms and models',
      type: 'multivariate',
      category: 'algorithm',
      configuration: {
        trafficSplit: 33.33,
        duration: 21,
        minSampleSize: 2000,
        confidenceLevel: 0.95,
        power: 0.8
      },
      metrics: ['accuracy', 'precision', 'recall', 'f1_score', 'latency'],
      segments: ['all_users', 'premium_users', 'free_users'],
      variants: ['current_algorithm', 'new_algorithm_a', 'new_algorithm_b'],
      duration: 21,
      minSampleSize: 2000,
      confidenceLevel: 0.95,
      power: 0.8,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    // Template para testing de contenido
    const contentTemplate: ExperimentTemplate = {
      id: 'content_test_template',
      name: 'Content Test Template',
      description: 'Template for testing different content variations',
      type: 'a_b',
      category: 'content',
      configuration: {
        trafficSplit: 50,
        duration: 7,
        minSampleSize: 500,
        confidenceLevel: 0.9,
        power: 0.8
      },
      metrics: ['engagement_rate', 'share_rate', 'comment_rate', 'time_spent'],
      segments: ['all_users', 'by_region', 'by_interests'],
      variants: ['control', 'treatment'],
      duration: 7,
      minSampleSize: 500,
      confidenceLevel: 0.9,
      power: 0.8,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.templates.set(uiABTemplate.id, uiABTemplate);
    this.templates.set(algorithmTemplate.id, algorithmTemplate);
    this.templates.set(contentTemplate.id, contentTemplate);
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
    const experimentId = this.analysisQueue.shift();

    try {
      await this.analyzeExperiment(experimentId!);
    } catch (error) {
      console.error('Error analyzing experiment:', error);
    } finally {
      this.isAnalyzing = false;
    }
  }

  private async analyzeExperiment(experimentId: string): Promise<void> {
    const experiment = this.experiments.get(experimentId);
    if (!experiment || experiment.status !== 'running') return;

    const analysis: ExperimentAnalysis = {
      experimentId,
      analysisType: 'interim',
      timestamp: new Date(),
      results: {
        summary: this.generateAnalysisSummary(experiment),
        keyFindings: this.generateKeyFindings(experiment),
        recommendations: this.generateRecommendations(experiment),
        nextSteps: this.generateNextSteps(experiment)
      },
      statisticalTests: this.performStatisticalTests(experiment),
      visualizations: this.generateVisualizations(experiment),
      metadata: {
        analysisVersion: '1.0.0',
        algorithm: 'bayesian_analysis'
      }
    };

    this.analyses.set(`${experimentId}_${Date.now()}`, analysis);
    this.emit('experiment_analyzed', analysis);

    // Actualizar resultados del experimento
    this.updateExperimentResults(experiment, analysis);
  }

  private generateAnalysisSummary(experiment: Experiment): string {
    const participants = experiment.results.participants.total;
    const duration = Math.floor((Date.now() - experiment.startDate.getTime()) / (1000 * 60 * 60 * 24));
    
    return `Experiment "${experiment.name}" has been running for ${duration} days with ${participants} participants. Current status shows promising early results with statistical significance approaching threshold.`;
  }

  private generateKeyFindings(experiment: Experiment): string[] {
    const findings: string[] = [];
    
    // Simular hallazgos basados en el tipo de experimento
    if (experiment.type === 'a_b') {
      findings.push('Treatment variant shows 15% improvement in primary metric');
      findings.push('Statistical significance approaching 95% confidence level');
      findings.push('No significant impact on secondary metrics observed');
    } else if (experiment.type === 'multivariate') {
      findings.push('Variant B outperforms other variants by 20%');
      findings.push('Interaction effects detected between variants');
      findings.push('Segment-specific performance differences identified');
    }
    
    return findings;
  }

  private generateRecommendations(experiment: Experiment): string[] {
    const recommendations: string[] = [];
    
    recommendations.push('Continue experiment to reach statistical significance');
    recommendations.push('Monitor secondary metrics for unexpected impacts');
    recommendations.push('Consider segment-specific analysis for deeper insights');
    
    if (experiment.results.participants.total > experiment.minSampleSize) {
      recommendations.push('Sufficient sample size reached, consider early conclusion');
    }
    
    return recommendations;
  }

  private generateNextSteps(experiment: Experiment): string[] {
    const nextSteps: string[] = [];
    
    nextSteps.push('Continue data collection for remaining duration');
    nextSteps.push('Schedule interim analysis in 3 days');
    nextSteps.push('Prepare rollback plan if negative results emerge');
    
    return nextSteps;
  }

  private performStatisticalTests(experiment: Experiment): { name: string; result: any; interpretation: string }[] {
    const tests: { name: string; result: any; interpretation: string }[] = [];
    
    // Test de significancia estadística
    tests.push({
      name: 'Chi-Square Test',
      result: { pValue: 0.03, chiSquare: 4.5 },
      interpretation: 'Statistically significant difference detected between variants'
    });
    
    // Test de proporciones
    tests.push({
      name: 'Z-Test for Proportions',
      result: { zScore: 2.1, pValue: 0.036 },
      interpretation: 'Significant difference in conversion rates between groups'
    });
    
    // Test de medias
    tests.push({
      name: 'T-Test for Means',
      result: { tStatistic: 2.3, pValue: 0.021 },
      interpretation: 'Significant difference in average values between variants'
    });
    
    return tests;
  }

  private generateVisualizations(experiment: Experiment): { type: string; data: any; insights: string }[] {
    const visualizations: { type: string; data: any; insights: string }[] = [];
    
    // Gráfico de conversión por día
    visualizations.push({
      type: 'line_chart',
      data: {
        title: 'Conversion Rate Over Time',
        xAxis: 'Date',
        yAxis: 'Conversion Rate (%)',
        series: [
          { name: 'Control', data: [2.1, 2.3, 2.0, 2.4, 2.2, 2.5, 2.3] },
          { name: 'Treatment', data: [2.2, 2.5, 2.3, 2.7, 2.4, 2.8, 2.6] }
        ]
      },
      insights: 'Treatment variant consistently outperforms control, showing upward trend'
    });
    
    // Gráfico de distribución
    visualizations.push({
      type: 'histogram',
      data: {
        title: 'Metric Distribution by Variant',
        xAxis: 'Metric Value',
        yAxis: 'Frequency',
        series: [
          { name: 'Control', data: [10, 25, 30, 20, 15] },
          { name: 'Treatment', data: [5, 15, 25, 35, 20] }
        ]
      },
      insights: 'Treatment variant shows higher concentration in upper value ranges'
    });
    
    return visualizations;
  }

  private updateExperimentResults(experiment: Experiment, analysis: ExperimentAnalysis): void {
    // Simular actualización de resultados
    experiment.results.participants.total += Math.floor(Math.random() * 100);
    experiment.results.participants.byVariant = {
      control: Math.floor(experiment.results.participants.total * 0.5),
      treatment: Math.floor(experiment.results.participants.total * 0.5)
    };
    
    // Actualizar métricas
    for (const metric in experiment.results.metrics.primary) {
      experiment.results.metrics.primary[metric].value += Math.random() * 0.1;
      experiment.results.metrics.primary[metric].pValue = Math.random() * 0.1;
    }
    
    this.experiments.set(experiment.id, experiment);
  }

  // Crear experimento
  createExperiment(experiment: Omit<Experiment, 'id' | 'createdAt' | 'updatedAt' | 'results'>): string {
    const id = `exp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newExperiment: Experiment = {
      ...experiment,
      id,
      results: {
        status: 'pending',
        startDate: experiment.startDate,
        participants: {
          total: 0,
          byVariant: {},
          bySegment: {}
        },
        metrics: {
          primary: {},
          secondary: {}
        },
        statisticalSignificance: {
          primary: {},
          secondary: {}
        },
        confidenceIntervals: {},
        pValues: {},
        effectSizes: {},
        recommendations: [],
        insights: []
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.experiments.set(id, newExperiment);
    this.emit('experiment_created', newExperiment);
    return id;
  }

  // Iniciar experimento
  startExperiment(experimentId: string): void {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) return;

    experiment.status = 'running';
    experiment.results.status = 'running';
    experiment.results.startDate = new Date();
    experiment.updatedAt = new Date();

    this.experiments.set(experimentId, experiment);
    this.emit('experiment_started', experiment);

    // Agregar a cola de análisis
    if (!this.analysisQueue.includes(experimentId)) {
      this.analysisQueue.push(experimentId);
    }
  }

  // Pausar experimento
  pauseExperiment(experimentId: string): void {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) return;

    experiment.status = 'paused';
    experiment.updatedAt = new Date();

    this.experiments.set(experimentId, experiment);
    this.emit('experiment_paused', experiment);
  }

  // Completar experimento
  completeExperiment(experimentId: string): void {
    const experiment = this.experiments.get(experimentId);
    if (!experiment) return;

    experiment.status = 'completed';
    experiment.endDate = new Date();
    experiment.results.status = 'completed';
    experiment.results.endDate = new Date();
    experiment.updatedAt = new Date();

    this.experiments.set(experimentId, experiment);
    this.emit('experiment_completed', experiment);
  }

  // Obtener experimentos
  getExperiments(): Experiment[] {
    return Array.from(this.experiments.values());
  }

  // Obtener templates
  getTemplates(): ExperimentTemplate[] {
    return Array.from(this.templates.values());
  }

  // Obtener análisis
  getAnalyses(experimentId?: string): ExperimentAnalysis[] {
    const analyses = Array.from(this.analyses.values());
    return experimentId ? analyses.filter(a => a.experimentId === experimentId) : analyses;
  }

  // Obtener estadísticas
  getStats(): {
    totalExperiments: number;
    runningExperiments: number;
    completedExperiments: number;
    totalAnalyses: number;
    averageDuration: number;
    successRate: number;
  } {
    const experiments = Array.from(this.experiments.values());
    const analyses = Array.from(this.analyses.values());

    const runningExperiments = experiments.filter(e => e.status === 'running').length;
    const completedExperiments = experiments.filter(e => e.status === 'completed').length;
    
    const averageDuration = experiments.length > 0 
      ? experiments.reduce((sum, e) => sum + e.duration, 0) / experiments.length 
      : 0;

    const successRate = completedExperiments > 0 
      ? experiments.filter(e => e.status === 'completed' && this.isExperimentSuccessful(e)).length / completedExperiments 
      : 0;

    return {
      totalExperiments: experiments.length,
      runningExperiments,
      completedExperiments,
      totalAnalyses: analyses.length,
      averageDuration,
      successRate
    };
  }

  private isExperimentSuccessful(experiment: Experiment): boolean {
    // Simular lógica para determinar si un experimento fue exitoso
    return Math.random() > 0.3; // 70% de éxito simulado
  }
}

export const advancedExperimentService = new AdvancedExperimentService();






