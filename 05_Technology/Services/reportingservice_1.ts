import { EventEmitter } from 'events';
import { CustomerFeedback } from './customerFeedbackService';
import { AdvancedAnalytics } from './advancedAnalyticsService';
import { aiInsightsService } from './aiInsightsService';
import { automationService } from './automationService';
import { integrationService } from './integrationService';

export interface ReportConfig {
  id: string;
  name: string;
  description: string;
  type: 'dashboard' | 'analytics' | 'insights' | 'automation' | 'integration' | 'custom';
  enabled: boolean;
  schedule?: {
    frequency: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'quarterly';
    time?: string; // HH:MM format
    dayOfWeek?: number; // 0-6 for weekly
    dayOfMonth?: number; // 1-31 for monthly
  };
  filters: ReportFilter[];
  metrics: string[];
  visualizations: ReportVisualization[];
  recipients: ReportRecipient[];
  format: 'pdf' | 'excel' | 'csv' | 'json' | 'html';
  template?: string;
  created: Date;
  updated: Date;
  lastGenerated?: Date;
  generationCount: number;
}

export interface ReportFilter {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'in' | 'not_in' | 'between' | 'date_range';
  value: any;
  logicalOperator?: 'AND' | 'OR';
}

export interface ReportVisualization {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'gauge' | 'trend' | 'heatmap' | 'pie' | 'bar' | 'line' | 'scatter';
  title: string;
  data: any;
  config: Record<string, any>;
  position: { x: number; y: number; width: number; height: number };
}

export interface ReportRecipient {
  type: 'email' | 'slack' | 'webhook' | 'file';
  address: string;
  name?: string;
  enabled: boolean;
}

export interface ReportGeneration {
  id: string;
  reportId: string;
  reportName: string;
  status: 'pending' | 'generating' | 'completed' | 'failed' | 'cancelled';
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  filePath?: string;
  fileSize?: number;
  recipients: ReportRecipient[];
  recipientsNotified: number;
  recipientsFailed: number;
  error?: string;
  metadata: Record<string, any>;
}

export interface ReportData {
  summary: {
    totalRecords: number;
    timeRange: { start: Date; end: Date };
    generatedAt: Date;
    generatedBy: string;
  };
  metrics: Record<string, any>;
  visualizations: ReportVisualization[];
  insights: string[];
  recommendations: string[];
  rawData?: any[];
}

export class ReportingService extends EventEmitter {
  private reports: Map<string, ReportConfig> = new Map();
  private generations: Map<string, ReportGeneration> = new Map();
  private isGenerating: boolean = false;
  private generationQueue: any[] = [];
  private generationInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultReports();
    this.startGenerationScheduler();
  }

  // Inicializar reportes por defecto
  private initializeDefaultReports(): void {
    // Reporte de feedback diario
    const dailyFeedbackReport: ReportConfig = {
      id: 'daily_feedback_report',
      name: 'Daily Feedback Summary',
      description: 'Daily summary of customer feedback and insights',
      type: 'analytics',
      enabled: true,
      schedule: {
        frequency: 'daily',
        time: '08:00'
      },
      filters: [
        {
          field: 'processedAt',
          operator: 'date_range',
          value: { start: 'yesterday', end: 'today' }
        }
      ],
      metrics: [
        'total_feedback',
        'sentiment_distribution',
        'urgency_distribution',
        'regional_breakdown',
        'source_breakdown',
        'trends'
      ],
      visualizations: [
        {
          id: 'sentiment_chart',
          type: 'pie',
          title: 'Sentiment Distribution',
          data: {},
          config: { colors: ['#28a745', '#ffc107', '#dc3545'] },
          position: { x: 0, y: 0, width: 6, height: 4 }
        },
        {
          id: 'trends_chart',
          type: 'line',
          title: 'Sentiment Trends',
          data: {},
          config: { showLegend: true, smooth: true },
          position: { x: 6, y: 0, width: 6, height: 4 }
        }
      ],
      recipients: [
        {
          type: 'email',
          address: 'team@company.com',
          name: 'Feedback Team',
          enabled: true
        }
      ],
      format: 'pdf',
      created: new Date(),
      updated: new Date(),
      generationCount: 0
    };

    // Reporte de insights semanal
    const weeklyInsightsReport: ReportConfig = {
      id: 'weekly_insights_report',
      name: 'Weekly AI Insights',
      description: 'Weekly report of AI-generated insights and recommendations',
      type: 'insights',
      enabled: true,
      schedule: {
        frequency: 'weekly',
        dayOfWeek: 1, // Monday
        time: '09:00'
      },
      filters: [
        {
          field: 'timestamp',
          operator: 'date_range',
          value: { start: '7_days_ago', end: 'today' }
        }
      ],
      metrics: [
        'total_insights',
        'insight_types',
        'trends_detected',
        'anomalies_found',
        'opportunities_identified',
        'recommendations_generated'
      ],
      visualizations: [
        {
          id: 'insights_overview',
          type: 'metric',
          title: 'Insights Overview',
          data: {},
          config: { showTrend: true },
          position: { x: 0, y: 0, width: 4, height: 2 }
        },
        {
          id: 'trends_heatmap',
          type: 'heatmap',
          title: 'Trends Heatmap',
          data: {},
          config: { colorScheme: 'blues' },
          position: { x: 4, y: 0, width: 8, height: 4 }
        }
      ],
      recipients: [
        {
          type: 'email',
          address: 'analytics@company.com',
          name: 'Analytics Team',
          enabled: true
        },
        {
          type: 'slack',
          address: '#analytics',
          name: 'Analytics Channel',
          enabled: true
        }
      ],
      format: 'html',
      created: new Date(),
      updated: new Date(),
      generationCount: 0
    };

    // Reporte de automatización mensual
    const monthlyAutomationReport: ReportConfig = {
      id: 'monthly_automation_report',
      name: 'Monthly Automation Report',
      description: 'Monthly report of automation performance and effectiveness',
      type: 'automation',
      enabled: true,
      schedule: {
        frequency: 'monthly',
        dayOfMonth: 1,
        time: '10:00'
      },
      filters: [
        {
          field: 'startedAt',
          operator: 'date_range',
          value: { start: '30_days_ago', end: 'today' }
        }
      ],
      metrics: [
        'total_executions',
        'success_rate',
        'average_execution_time',
        'rule_performance',
        'error_analysis',
        'recommendations'
      ],
      visualizations: [
        {
          id: 'execution_trends',
          type: 'line',
          title: 'Execution Trends',
          data: {},
          config: { showLegend: true, stacked: false },
          position: { x: 0, y: 0, width: 12, height: 4 }
        },
        {
          id: 'rule_performance',
          type: 'bar',
          title: 'Rule Performance',
          data: {},
          config: { horizontal: true },
          position: { x: 0, y: 4, width: 12, height: 4 }
        }
      ],
      recipients: [
        {
          type: 'email',
          address: 'automation@company.com',
          name: 'Automation Team',
          enabled: true
        }
      ],
      format: 'excel',
      created: new Date(),
      updated: new Date(),
      generationCount: 0
    };

    this.reports.set(dailyFeedbackReport.id, dailyFeedbackReport);
    this.reports.set(weeklyInsightsReport.id, weeklyInsightsReport);
    this.reports.set(monthlyAutomationReport.id, monthlyAutomationReport);
  }

  // Iniciar programador de generación
  private startGenerationScheduler(): void {
    this.generationInterval = setInterval(() => {
      this.checkScheduledReports();
    }, 60000); // Cada minuto
  }

  // Detener programador de generación
  stopGenerationScheduler(): void {
    if (this.generationInterval) {
      clearInterval(this.generationInterval);
      this.generationInterval = null;
    }
  }

  // Verificar reportes programados
  private async checkScheduledReports(): Promise<void> {
    const now = new Date();
    const enabledReports = Array.from(this.reports.values())
      .filter(report => report.enabled && report.schedule);

    for (const report of enabledReports) {
      if (this.shouldGenerateReport(report, now)) {
        this.generationQueue.push({
          reportId: report.id,
          triggeredBy: 'schedule'
        });
      }
    }

    // Procesar cola de generación
    if (this.generationQueue.length > 0 && !this.isGenerating) {
      this.processGenerationQueue();
    }
  }

  // Verificar si debe generar reporte
  private shouldGenerateReport(report: ReportConfig, now: Date): boolean {
    if (!report.schedule) return false;

    const { frequency, time, dayOfWeek, dayOfMonth } = report.schedule;
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentDay = now.getDay();
    const currentDate = now.getDate();

    // Verificar hora
    if (time) {
      const [scheduleHour, scheduleMinute] = time.split(':').map(Number);
      if (currentHour !== scheduleHour || currentMinute !== scheduleMinute) {
        return false;
      }
    }

    // Verificar frecuencia
    switch (frequency) {
      case 'hourly':
        return true;
      case 'daily':
        return true;
      case 'weekly':
        return dayOfWeek !== undefined && currentDay === dayOfWeek;
      case 'monthly':
        return dayOfMonth !== undefined && currentDate === dayOfMonth;
      case 'quarterly':
        return dayOfMonth !== undefined && currentDate === dayOfMonth && 
               [0, 3, 6, 9].includes(now.getMonth());
      default:
        return false;
    }
  }

  // Procesar cola de generación
  private async processGenerationQueue(): Promise<void> {
    if (this.isGenerating || this.generationQueue.length === 0) return;

    this.isGenerating = true;
    const item = this.generationQueue.shift();

    try {
      await this.generateReport(item.reportId, item.triggeredBy);
    } catch (error) {
      console.error('Error processing report generation:', error);
    } finally {
      this.isGenerating = false;
    }
  }

  // Generar reporte
  async generateReport(reportId: string, triggeredBy: string = 'manual'): Promise<string> {
    const report = this.reports.get(reportId);
    if (!report) {
      throw new Error(`Report ${reportId} not found`);
    }

    const generation: ReportGeneration = {
      id: `gen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      reportId,
      reportName: report.name,
      status: 'generating',
      startedAt: new Date(),
      recipients: report.recipients.filter(r => r.enabled),
      recipientsNotified: 0,
      recipientsFailed: 0,
      metadata: { triggeredBy }
    };

    this.generations.set(generation.id, generation);
    this.emit('generation_started', generation);

    try {
      // Recopilar datos del reporte
      const reportData = await this.collectReportData(report);
      
      // Generar archivo del reporte
      const filePath = await this.generateReportFile(report, reportData);
      
      // Notificar a los destinatarios
      await this.notifyRecipients(generation, filePath);
      
      generation.status = 'completed';
      generation.completedAt = new Date();
      generation.duration = generation.completedAt.getTime() - generation.startedAt.getTime();
      generation.filePath = filePath;
      generation.fileSize = 1024; // Simular tamaño del archivo
      
      report.generationCount++;
      report.lastGenerated = new Date();

      this.emit('generation_completed', generation);
      return generation.id;
    } catch (error) {
      generation.status = 'failed';
      generation.error = error.message;
      generation.completedAt = new Date();
      generation.duration = generation.completedAt.getTime() - generation.startedAt.getTime();

      this.emit('generation_failed', generation);
      throw error;
    }
  }

  // Recopilar datos del reporte
  private async collectReportData(report: ReportConfig): Promise<ReportData> {
    const now = new Date();
    const timeRange = this.calculateTimeRange(report.filters);
    
    // Simular recopilación de datos
    const summary = {
      totalRecords: Math.floor(Math.random() * 1000) + 100,
      timeRange,
      generatedAt: now,
      generatedBy: 'system'
    };

    const metrics: Record<string, any> = {};
    for (const metric of report.metrics) {
      metrics[metric] = this.generateMetricData(metric);
    }

    const visualizations = report.visualizations.map(viz => ({
      ...viz,
      data: this.generateVisualizationData(viz.type)
    }));

    const insights = [
      'Customer satisfaction has improved by 15% this period',
      'Negative feedback decreased by 8% compared to last period',
      'New trends detected in customer communication preferences'
    ];

    const recommendations = [
      'Continue current customer engagement strategies',
      'Focus on addressing remaining negative feedback',
      'Implement new communication channels based on trends'
    ];

    return {
      summary,
      metrics,
      visualizations,
      insights,
      recommendations
    };
  }

  // Calcular rango de tiempo
  private calculateTimeRange(filters: ReportFilter[]): { start: Date; end: Date } {
    const now = new Date();
    const end = new Date(now);
    const start = new Date(now);
    
    // Buscar filtro de rango de fechas
    const dateFilter = filters.find(f => f.operator === 'date_range');
    if (dateFilter && dateFilter.value) {
      const { start: startValue, end: endValue } = dateFilter.value;
      
      if (startValue === 'yesterday') {
        start.setDate(start.getDate() - 1);
        start.setHours(0, 0, 0, 0);
        end.setDate(end.getDate() - 1);
        end.setHours(23, 59, 59, 999);
      } else if (startValue === '7_days_ago') {
        start.setDate(start.getDate() - 7);
      } else if (startValue === '30_days_ago') {
        start.setDate(start.getDate() - 30);
      }
    } else {
      // Por defecto, últimos 7 días
      start.setDate(start.getDate() - 7);
    }
    
    return { start, end };
  }

  // Generar datos de métrica
  private generateMetricData(metric: string): any {
    switch (metric) {
      case 'total_feedback':
        return Math.floor(Math.random() * 1000) + 100;
      case 'sentiment_distribution':
        return {
          positive: Math.floor(Math.random() * 60) + 30,
          neutral: Math.floor(Math.random() * 30) + 10,
          negative: Math.floor(Math.random() * 20) + 5
        };
      case 'urgency_distribution':
        return {
          low: Math.floor(Math.random() * 50) + 20,
          medium: Math.floor(Math.random() * 30) + 15,
          high: Math.floor(Math.random() * 15) + 5,
          critical: Math.floor(Math.random() * 5) + 1
        };
      case 'regional_breakdown':
        return {
          MX: Math.floor(Math.random() * 200) + 50,
          AR: Math.floor(Math.random() * 150) + 30,
          BR: Math.floor(Math.random() * 300) + 100,
          CO: Math.floor(Math.random() * 100) + 20
        };
      case 'source_breakdown':
        return {
          survey: Math.floor(Math.random() * 200) + 50,
          review: Math.floor(Math.random() * 150) + 30,
          social_media: Math.floor(Math.random() * 100) + 20,
          email: Math.floor(Math.random() * 80) + 10
        };
      default:
        return Math.floor(Math.random() * 100);
    }
  }

  // Generar datos de visualización
  private generateVisualizationData(type: string): any {
    switch (type) {
      case 'pie':
        return [
          { name: 'Positive', value: Math.floor(Math.random() * 60) + 30 },
          { name: 'Neutral', value: Math.floor(Math.random() * 30) + 10 },
          { name: 'Negative', value: Math.floor(Math.random() * 20) + 5 }
        ];
      case 'line':
        return Array.from({ length: 7 }, (_, i) => ({
          date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          value: Math.floor(Math.random() * 100) + 50
        }));
      case 'bar':
        return [
          { name: 'Rule 1', value: Math.floor(Math.random() * 100) + 50 },
          { name: 'Rule 2', value: Math.floor(Math.random() * 100) + 30 },
          { name: 'Rule 3', value: Math.floor(Math.random() * 100) + 20 }
        ];
      case 'metric':
        return {
          value: Math.floor(Math.random() * 1000) + 100,
          change: (Math.random() - 0.5) * 20,
          trend: Math.random() > 0.5 ? 'up' : 'down'
        };
      default:
        return [];
    }
  }

  // Generar archivo del reporte
  private async generateReportFile(report: ReportConfig, data: ReportData): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${report.name.replace(/\s+/g, '_')}_${timestamp}.${report.format}`;
    const filePath = `/tmp/reports/${filename}`;
    
    // Simular generación de archivo
    console.log(`Generating ${report.format} report: ${filename}`);
    
    // Simular delay de generación
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return filePath;
  }

  // Notificar destinatarios
  private async notifyRecipients(generation: ReportGeneration, filePath: string): Promise<void> {
    for (const recipient of generation.recipients) {
      try {
        await this.sendNotification(recipient, generation, filePath);
        generation.recipientsNotified++;
      } catch (error) {
        console.error(`Error notifying recipient ${recipient.address}:`, error);
        generation.recipientsFailed++;
      }
    }
  }

  // Enviar notificación
  private async sendNotification(recipient: ReportRecipient, generation: ReportGeneration, filePath: string): Promise<void> {
    switch (recipient.type) {
      case 'email':
        console.log(`Sending email to ${recipient.address} with report ${filePath}`);
        break;
      case 'slack':
        console.log(`Sending Slack message to ${recipient.address} with report ${filePath}`);
        break;
      case 'webhook':
        console.log(`Sending webhook to ${recipient.address} with report ${filePath}`);
        break;
      case 'file':
        console.log(`Saving report to ${recipient.address}`);
        break;
    }
  }

  // Crear reporte
  createReport(report: Omit<ReportConfig, 'id' | 'created' | 'updated' | 'generationCount'>): string {
    const id = `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newReport: ReportConfig = {
      ...report,
      id,
      created: new Date(),
      updated: new Date(),
      generationCount: 0
    };

    this.reports.set(id, newReport);
    this.emit('report_created', newReport);
    return id;
  }

  // Actualizar reporte
  updateReport(id: string, updates: Partial<ReportConfig>): boolean {
    const report = this.reports.get(id);
    if (!report) return false;

    const updatedReport = {
      ...report,
      ...updates,
      id,
      updated: new Date()
    };

    this.reports.set(id, updatedReport);
    this.emit('report_updated', updatedReport);
    return true;
  }

  // Eliminar reporte
  deleteReport(id: string): boolean {
    const report = this.reports.get(id);
    if (!report) return false;

    this.reports.delete(id);
    this.emit('report_deleted', report);
    return true;
  }

  // Obtener reportes
  getReports(): ReportConfig[] {
    return Array.from(this.reports.values());
  }

  // Obtener reporte específico
  getReport(id: string): ReportConfig | undefined {
    return this.reports.get(id);
  }

  // Obtener generaciones
  getGenerations(limit?: number): ReportGeneration[] {
    const generations = Array.from(this.generations.values())
      .sort((a, b) => b.startedAt.getTime() - a.startedAt.getTime());
    
    return limit ? generations.slice(0, limit) : generations;
  }

  // Obtener estadísticas
  getStats(): {
    totalReports: number;
    enabledReports: number;
    totalGenerations: number;
    successfulGenerations: number;
    failedGenerations: number;
    averageGenerationTime: number;
    recentGenerations: ReportGeneration[];
  } {
    const reports = Array.from(this.reports.values());
    const generations = Array.from(this.generations.values());
    
    const totalGenerations = generations.length;
    const successfulGenerations = generations.filter(g => g.status === 'completed').length;
    const failedGenerations = generations.filter(g => g.status === 'failed').length;
    
    const averageGenerationTime = generations.length > 0 
      ? generations.reduce((sum, g) => sum + (g.duration || 0), 0) / generations.length
      : 0;
    
    return {
      totalReports: reports.length,
      enabledReports: reports.filter(r => r.enabled).length,
      totalGenerations,
      successfulGenerations,
      failedGenerations,
      averageGenerationTime,
      recentGenerations: generations.slice(0, 10)
    };
  }
}

export const reportingService = new ReportingService();

