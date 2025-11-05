import { EventEmitter } from 'events';

export interface PerformanceMetric {
  id: string;
  name: string;
  type: 'response_time' | 'throughput' | 'error_rate' | 'cpu_usage' | 'memory_usage' | 'database_query_time' | 'api_latency';
  value: number;
  unit: string;
  timestamp: Date;
  tags: Record<string, string>;
  metadata: Record<string, any>;
}

export interface PerformanceAlert {
  id: string;
  metricName: string;
  threshold: number;
  currentValue: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  triggeredAt: Date;
  resolvedAt?: Date;
  status: 'active' | 'resolved' | 'acknowledged';
  metadata: Record<string, any>;
}

export interface PerformanceReport {
  id: string;
  name: string;
  period: {
    start: Date;
    end: Date;
  };
  metrics: {
    averageResponseTime: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
    throughput: number;
    errorRate: number;
    uptime: number;
    cpuUsage: number;
    memoryUsage: number;
  };
  trends: {
    responseTime: 'improving' | 'stable' | 'degrading';
    throughput: 'increasing' | 'stable' | 'decreasing';
    errorRate: 'decreasing' | 'stable' | 'increasing';
  };
  recommendations: string[];
  generatedAt: Date;
}

export interface PerformanceOptimization {
  id: string;
  name: string;
  type: 'caching' | 'database' | 'api' | 'memory' | 'cpu' | 'network';
  description: string;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  priority: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  estimatedImprovement: number;
  actualImprovement?: number;
  createdAt: Date;
  completedAt?: Date;
}

export class PerformanceAnalyticsService extends EventEmitter {
  private metrics: Map<string, PerformanceMetric> = new Map();
  private alerts: Map<string, PerformanceAlert> = new Map();
  private reports: Map<string, PerformanceReport> = new Map();
  private optimizations: Map<string, PerformanceOptimization> = new Map();
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.initializeDefaultOptimizations();
    this.startMonitoring();
  }

  private initializeDefaultOptimizations(): void {
    const optimizations: PerformanceOptimization[] = [
      {
        id: 'cache_optimization',
        name: 'Implement Redis Caching',
        type: 'caching',
        description: 'Add Redis caching layer to reduce database load',
        impact: 'high',
        effort: 'medium',
        priority: 1,
        status: 'pending',
        estimatedImprovement: 40,
        createdAt: new Date()
      },
      {
        id: 'database_indexing',
        name: 'Optimize Database Indexes',
        type: 'database',
        description: 'Add missing indexes to improve query performance',
        impact: 'high',
        effort: 'low',
        priority: 2,
        status: 'pending',
        estimatedImprovement: 60,
        createdAt: new Date()
      },
      {
        id: 'api_compression',
        name: 'Enable API Response Compression',
        type: 'api',
        description: 'Enable gzip compression for API responses',
        impact: 'medium',
        effort: 'low',
        priority: 3,
        status: 'pending',
        estimatedImprovement: 30,
        createdAt: new Date()
      },
      {
        id: 'memory_optimization',
        name: 'Optimize Memory Usage',
        type: 'memory',
        description: 'Implement memory pooling and garbage collection optimization',
        impact: 'medium',
        effort: 'high',
        priority: 4,
        status: 'pending',
        estimatedImprovement: 25,
        createdAt: new Date()
      }
    ];

    optimizations.forEach(opt => {
      this.optimizations.set(opt.id, opt);
    });
  }

  private startMonitoring(): void {
    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
      this.checkAlerts();
      this.analyzePerformance();
    }, 5000); // Cada 5 segundos
  }

  stopMonitoring(): void {
    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  private collectMetrics(): void {
    // Simular recolección de métricas del sistema
    const now = new Date();
    
    // Métricas de respuesta de API
    this.recordMetric({
      name: 'api_response_time',
      type: 'response_time',
      value: Math.random() * 200 + 50, // 50-250ms
      unit: 'ms',
      timestamp: now,
      tags: { endpoint: '/api/feedback', method: 'POST' },
      metadata: { version: '1.0.0' }
    });

    // Métricas de throughput
    this.recordMetric({
      name: 'api_throughput',
      type: 'throughput',
      value: Math.random() * 100 + 50, // 50-150 requests/min
      unit: 'requests/min',
      timestamp: now,
      tags: { service: 'feedback' },
      metadata: {}
    });

    // Métricas de CPU
    this.recordMetric({
      name: 'cpu_usage',
      type: 'cpu_usage',
      value: Math.random() * 40 + 20, // 20-60%
      unit: '%',
      timestamp: now,
      tags: { host: 'server-1' },
      metadata: {}
    });

    // Métricas de memoria
    this.recordMetric({
      name: 'memory_usage',
      type: 'memory_usage',
      value: Math.random() * 30 + 40, // 40-70%
      unit: '%',
      timestamp: now,
      tags: { host: 'server-1' },
      metadata: {}
    });

    // Métricas de base de datos
    this.recordMetric({
      name: 'db_query_time',
      type: 'database_query_time',
      value: Math.random() * 100 + 10, // 10-110ms
      unit: 'ms',
      timestamp: now,
      tags: { query: 'SELECT', table: 'feedback' },
      metadata: {}
    });

    // Métricas de error rate
    this.recordMetric({
      name: 'error_rate',
      type: 'error_rate',
      value: Math.random() * 2, // 0-2%
      unit: '%',
      timestamp: now,
      tags: { service: 'api' },
      metadata: {}
    });
  }

  private recordMetric(metricData: Omit<PerformanceMetric, 'id'>): void {
    const metric: PerformanceMetric = {
      ...metricData,
      id: `metric_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    this.metrics.set(metric.id, metric);
    this.emit('metric_recorded', metric);
  }

  private checkAlerts(): void {
    const now = new Date();
    const recentMetrics = this.getRecentMetrics(300000); // Últimos 5 minutos

    // Verificar alertas de tiempo de respuesta
    const responseTimeMetrics = recentMetrics.filter(m => m.name === 'api_response_time');
    if (responseTimeMetrics.length > 0) {
      const avgResponseTime = responseTimeMetrics.reduce((sum, m) => sum + m.value, 0) / responseTimeMetrics.length;
      if (avgResponseTime > 500) { // 500ms threshold
        this.createAlert({
          metricName: 'api_response_time',
          threshold: 500,
          currentValue: avgResponseTime,
          severity: 'high',
          message: `API response time is ${avgResponseTime.toFixed(2)}ms, exceeding threshold of 500ms`,
          metadata: { average: avgResponseTime, count: responseTimeMetrics.length }
        });
      }
    }

    // Verificar alertas de CPU
    const cpuMetrics = recentMetrics.filter(m => m.name === 'cpu_usage');
    if (cpuMetrics.length > 0) {
      const avgCpuUsage = cpuMetrics.reduce((sum, m) => sum + m.value, 0) / cpuMetrics.length;
      if (avgCpuUsage > 80) { // 80% threshold
        this.createAlert({
          metricName: 'cpu_usage',
          threshold: 80,
          currentValue: avgCpuUsage,
          severity: 'critical',
          message: `CPU usage is ${avgCpuUsage.toFixed(2)}%, exceeding threshold of 80%`,
          metadata: { average: avgCpuUsage, count: cpuMetrics.length }
        });
      }
    }

    // Verificar alertas de memoria
    const memoryMetrics = recentMetrics.filter(m => m.name === 'memory_usage');
    if (memoryMetrics.length > 0) {
      const avgMemoryUsage = memoryMetrics.reduce((sum, m) => sum + m.value, 0) / memoryMetrics.length;
      if (avgMemoryUsage > 85) { // 85% threshold
        this.createAlert({
          metricName: 'memory_usage',
          threshold: 85,
          currentValue: avgMemoryUsage,
          severity: 'critical',
          message: `Memory usage is ${avgMemoryUsage.toFixed(2)}%, exceeding threshold of 85%`,
          metadata: { average: avgMemoryUsage, count: memoryMetrics.length }
        });
      }
    }

    // Verificar alertas de error rate
    const errorRateMetrics = recentMetrics.filter(m => m.name === 'error_rate');
    if (errorRateMetrics.length > 0) {
      const avgErrorRate = errorRateMetrics.reduce((sum, m) => sum + m.value, 0) / errorRateMetrics.length;
      if (avgErrorRate > 1) { // 1% threshold
        this.createAlert({
          metricName: 'error_rate',
          threshold: 1,
          currentValue: avgErrorRate,
          severity: 'medium',
          message: `Error rate is ${avgErrorRate.toFixed(2)}%, exceeding threshold of 1%`,
          metadata: { average: avgErrorRate, count: errorRateMetrics.length }
        });
      }
    }
  }

  private createAlert(alertData: Omit<PerformanceAlert, 'id' | 'triggeredAt' | 'status'>): void {
    const alert: PerformanceAlert = {
      ...alertData,
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      triggeredAt: new Date(),
      status: 'active'
    };

    this.alerts.set(alert.id, alert);
    this.emit('alert_triggered', alert);
  }

  private analyzePerformance(): void {
    const recentMetrics = this.getRecentMetrics(3600000); // Última hora
    if (recentMetrics.length === 0) return;

    // Analizar tendencias
    const responseTimeTrend = this.analyzeTrend(recentMetrics.filter(m => m.name === 'api_response_time'));
    const throughputTrend = this.analyzeTrend(recentMetrics.filter(m => m.name === 'api_throughput'));
    const errorRateTrend = this.analyzeTrend(recentMetrics.filter(m => m.name === 'error_rate'));

    // Generar recomendaciones basadas en el análisis
    const recommendations = this.generateRecommendations(responseTimeTrend, throughputTrend, errorRateTrend);
    
    if (recommendations.length > 0) {
      this.emit('recommendations_generated', recommendations);
    }
  }

  private analyzeTrend(metrics: PerformanceMetric[]): 'improving' | 'stable' | 'degrading' {
    if (metrics.length < 2) return 'stable';

    const firstHalf = metrics.slice(0, Math.floor(metrics.length / 2));
    const secondHalf = metrics.slice(Math.floor(metrics.length / 2));

    const firstHalfAvg = firstHalf.reduce((sum, m) => sum + m.value, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, m) => sum + m.value, 0) / secondHalf.length;

    const change = (secondHalfAvg - firstHalfAvg) / firstHalfAvg;

    if (change > 0.1) return 'degrading';
    if (change < -0.1) return 'improving';
    return 'stable';
  }

  private generateRecommendations(responseTrend: string, throughputTrend: string, errorTrend: string): string[] {
    const recommendations: string[] = [];

    if (responseTrend === 'degrading') {
      recommendations.push('Consider implementing caching to improve response times');
      recommendations.push('Review database query optimization');
    }

    if (throughputTrend === 'degrading') {
      recommendations.push('Consider horizontal scaling to handle increased load');
      recommendations.push('Review rate limiting configuration');
    }

    if (errorTrend === 'degrading') {
      recommendations.push('Investigate error patterns and implement better error handling');
      recommendations.push('Review input validation and sanitization');
    }

    return recommendations;
  }

  private getRecentMetrics(timeWindow: number): PerformanceMetric[] {
    const now = Date.now();
    const cutoff = now - timeWindow;

    return Array.from(this.metrics.values())
      .filter(metric => metric.timestamp.getTime() > cutoff);
  }

  // Generar reporte de rendimiento
  generatePerformanceReport(period: { start: Date; end: Date }): PerformanceReport {
    const metrics = Array.from(this.metrics.values())
      .filter(m => m.timestamp >= period.start && m.timestamp <= period.end);

    const responseTimeMetrics = metrics.filter(m => m.name === 'api_response_time');
    const throughputMetrics = metrics.filter(m => m.name === 'api_throughput');
    const errorRateMetrics = metrics.filter(m => m.name === 'error_rate');
    const cpuMetrics = metrics.filter(m => m.name === 'cpu_usage');
    const memoryMetrics = metrics.filter(m => m.name === 'memory_usage');

    const responseTimes = responseTimeMetrics.map(m => m.value);
    const throughputs = throughputMetrics.map(m => m.value);
    const errorRates = errorRateMetrics.map(m => m.value);
    const cpuUsages = cpuMetrics.map(m => m.value);
    const memoryUsages = memoryMetrics.map(m => m.value);

    const report: PerformanceReport = {
      id: `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: `Performance Report ${period.start.toISOString().split('T')[0]} - ${period.end.toISOString().split('T')[0]}`,
      period,
      metrics: {
        averageResponseTime: this.calculateAverage(responseTimes),
        p95ResponseTime: this.calculatePercentile(responseTimes, 95),
        p99ResponseTime: this.calculatePercentile(responseTimes, 99),
        throughput: this.calculateAverage(throughputs),
        errorRate: this.calculateAverage(errorRates),
        uptime: 99.9, // Simular uptime
        cpuUsage: this.calculateAverage(cpuUsages),
        memoryUsage: this.calculateAverage(memoryUsages)
      },
      trends: {
        responseTime: this.analyzeTrend(responseTimeMetrics),
        throughput: this.analyzeTrend(throughputMetrics),
        errorRate: this.analyzeTrend(errorRateMetrics)
      },
      recommendations: this.generateRecommendations(
        this.analyzeTrend(responseTimeMetrics),
        this.analyzeTrend(throughputMetrics),
        this.analyzeTrend(errorRateMetrics)
      ),
      generatedAt: new Date()
    };

    this.reports.set(report.id, report);
    this.emit('report_generated', report);
    return report;
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  private calculatePercentile(values: number[], percentile: number): number {
    if (values.length === 0) return 0;
    const sorted = values.sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }

  // Obtener métricas
  getMetrics(limit?: number): PerformanceMetric[] {
    const metrics = Array.from(this.metrics.values())
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    
    return limit ? metrics.slice(0, limit) : metrics;
  }

  // Obtener alertas
  getAlerts(limit?: number): PerformanceAlert[] {
    const alerts = Array.from(this.alerts.values())
      .sort((a, b) => b.triggeredAt.getTime() - a.triggeredAt.getTime());
    
    return limit ? alerts.slice(0, limit) : alerts;
  }

  // Obtener reportes
  getReports(limit?: number): PerformanceReport[] {
    const reports = Array.from(this.reports.values())
      .sort((a, b) => b.generatedAt.getTime() - a.generatedAt.getTime());
    
    return limit ? reports.slice(0, limit) : reports;
  }

  // Obtener optimizaciones
  getOptimizations(): PerformanceOptimization[] {
    return Array.from(this.optimizations.values());
  }

  // Obtener estadísticas
  getStats(): {
    totalMetrics: number;
    activeAlerts: number;
    totalReports: number;
    pendingOptimizations: number;
    averageResponseTime: number;
    currentCpuUsage: number;
    currentMemoryUsage: number;
  } {
    const metrics = Array.from(this.metrics.values());
    const alerts = Array.from(this.alerts.values());
    const reports = Array.from(this.reports.values());
    const optimizations = Array.from(this.optimizations.values());

    const responseTimeMetrics = metrics.filter(m => m.name === 'api_response_time');
    const cpuMetrics = metrics.filter(m => m.name === 'cpu_usage');
    const memoryMetrics = metrics.filter(m => m.name === 'memory_usage');

    return {
      totalMetrics: metrics.length,
      activeAlerts: alerts.filter(a => a.status === 'active').length,
      totalReports: reports.length,
      pendingOptimizations: optimizations.filter(o => o.status === 'pending').length,
      averageResponseTime: this.calculateAverage(responseTimeMetrics.map(m => m.value)),
      currentCpuUsage: this.calculateAverage(cpuMetrics.map(m => m.value)),
      currentMemoryUsage: this.calculateAverage(memoryMetrics.map(m => m.value))
    };
  }
}

export const performanceAnalyticsService = new PerformanceAnalyticsService();






