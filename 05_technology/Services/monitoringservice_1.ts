import { EventEmitter } from 'events';
import { performance } from 'perf_hooks';
import { securityService } from './securityService';
import { performanceOptimizationService } from './performanceOptimizationService';

export interface HealthCheck {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  responseTime: number;
  lastCheck: Date;
  details: Record<string, any>;
  dependencies: string[];
}

export interface Alert {
  id: string;
  type: 'performance' | 'security' | 'availability' | 'error' | 'resource';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  source: string;
  timestamp: Date;
  acknowledged: boolean;
  resolved: boolean;
  metadata: Record<string, any>;
}

export interface SystemMetrics {
  timestamp: Date;
  cpu: {
    usage: number;
    loadAverage: number[];
    cores: number;
  };
  memory: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    connections: number;
    latency: number;
  };
  application: {
    uptime: number;
    requests: number;
    errors: number;
    responseTime: number;
  };
}

export interface DashboardData {
  systemHealth: {
    overall: 'healthy' | 'degraded' | 'unhealthy';
    services: HealthCheck[];
    uptime: number;
    lastIncident: Date | null;
  };
  performance: {
    averageResponseTime: number;
    throughput: number;
    errorRate: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
  };
  security: {
    activeThreats: number;
    blockedIPs: number;
    securityScore: number;
    lastThreat: Date | null;
  };
  resources: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
    networkLatency: number;
  };
  alerts: Alert[];
  trends: {
    responseTime: number[];
    errorRate: number[];
    throughput: number[];
    cpuUsage: number[];
    memoryUsage: number[];
  };
}

export class MonitoringService extends EventEmitter {
  private healthChecks: Map<string, HealthCheck> = new Map();
  private alerts: Alert[] = [];
  private systemMetrics: SystemMetrics[] = [];
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private alertThresholds: Record<string, any> = {};

  constructor() {
    super();
    this.initializeHealthChecks();
    this.initializeAlertThresholds();
    this.startMonitoring();
  }

  // Inicializar verificaciones de salud
  private initializeHealthChecks(): void {
    this.healthChecks.set('database', {
      service: 'database',
      status: 'healthy',
      responseTime: 0,
      lastCheck: new Date(),
      details: {},
      dependencies: []
    });

    this.healthChecks.set('redis', {
      service: 'redis',
      status: 'healthy',
      responseTime: 0,
      lastCheck: new Date(),
      details: {},
      dependencies: []
    });

    this.healthChecks.set('api', {
      service: 'api',
      status: 'healthy',
      responseTime: 0,
      lastCheck: new Date(),
      details: {},
      dependencies: ['database', 'redis']
    });

    this.healthChecks.set('websocket', {
      service: 'websocket',
      status: 'healthy',
      responseTime: 0,
      lastCheck: new Date(),
      details: {},
      dependencies: ['api']
    });
  }

  // Inicializar umbrales de alertas
  private initializeAlertThresholds(): void {
    this.alertThresholds = {
      responseTime: 2000, // 2 segundos
      errorRate: 5, // 5%
      cpuUsage: 80, // 80%
      memoryUsage: 85, // 85%
      diskUsage: 90, // 90%
      securityThreats: 1, // 1 amenaza
      availability: 99.9 // 99.9%
    };
  }

  // Iniciar monitoreo
  startMonitoring(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.collectSystemMetrics();
      this.performHealthChecks();
      this.checkAlertThresholds();
      this.cleanupOldData();
    }, 10000); // Cada 10 segundos

    console.log('System monitoring started');
  }

  // Detener monitoreo
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.log('System monitoring stopped');
  }

  // Recopilar métricas del sistema
  private collectSystemMetrics(): void {
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    const uptime = process.uptime();

    const metrics: SystemMetrics = {
      timestamp: new Date(),
      cpu: {
        usage: this.calculateCpuUsage(cpuUsage),
        loadAverage: process.platform === 'win32' ? [0, 0, 0] : require('os').loadavg(),
        cores: require('os').cpus().length
      },
      memory: {
        used: memoryUsage.heapUsed,
        total: memoryUsage.heapTotal,
        free: memoryUsage.heapTotal - memoryUsage.heapUsed,
        percentage: (memoryUsage.heapUsed / memoryUsage.heapTotal) * 100
      },
      disk: {
        used: 0, // Se calcularía con fs.stat
        total: 0,
        free: 0,
        percentage: 0
      },
      network: {
        bytesIn: 0, // Se calcularía con netstat
        bytesOut: 0,
        connections: 0,
        latency: 0
      },
      application: {
        uptime: uptime,
        requests: this.getRequestCount(),
        errors: this.getErrorCount(),
        responseTime: this.getAverageResponseTime()
      }
    };

    this.systemMetrics.push(metrics);

    // Mantener solo las últimas 1000 métricas
    if (this.systemMetrics.length > 1000) {
      this.systemMetrics = this.systemMetrics.slice(-1000);
    }

    this.emit('metrics_collected', metrics);
  }

  // Realizar verificaciones de salud
  private async performHealthChecks(): Promise<void> {
    for (const [serviceName, healthCheck] of this.healthChecks.entries()) {
      try {
        const startTime = performance.now();
        
        // Simular verificación de salud (en implementación real, verificar servicios reales)
        await this.checkServiceHealth(serviceName);
        
        const responseTime = performance.now() - startTime;
        
        healthCheck.status = 'healthy';
        healthCheck.responseTime = responseTime;
        healthCheck.lastCheck = new Date();
        healthCheck.details = { message: 'Service is healthy' };
        
      } catch (error) {
        healthCheck.status = 'unhealthy';
        healthCheck.responseTime = 0;
        healthCheck.lastCheck = new Date();
        healthCheck.details = { error: error.message };
        
        // Crear alerta
        this.createAlert({
          type: 'availability',
          severity: 'high',
          title: `Service ${serviceName} is unhealthy`,
          description: `Service ${serviceName} failed health check: ${error.message}`,
          source: serviceName,
          metadata: { error: error.message }
        });
      }
    }
  }

  // Verificar salud de un servicio específico
  private async checkServiceHealth(serviceName: string): Promise<void> {
    // Simular verificaciones de salud
    switch (serviceName) {
      case 'database':
        // Verificar conexión a base de datos
        await new Promise(resolve => setTimeout(resolve, 100));
        break;
      case 'redis':
        // Verificar conexión a Redis
        await new Promise(resolve => setTimeout(resolve, 50));
        break;
      case 'api':
        // Verificar endpoints de API
        await new Promise(resolve => setTimeout(resolve, 200));
        break;
      case 'websocket':
        // Verificar conexiones WebSocket
        await new Promise(resolve => setTimeout(resolve, 150));
        break;
      default:
        throw new Error(`Unknown service: ${serviceName}`);
    }
  }

  // Verificar umbrales de alertas
  private checkAlertThresholds(): void {
    const latestMetrics = this.systemMetrics[this.systemMetrics.length - 1];
    if (!latestMetrics) return;

    // Verificar CPU
    if (latestMetrics.cpu.usage > this.alertThresholds.cpuUsage) {
      this.createAlert({
        type: 'resource',
        severity: 'medium',
        title: 'High CPU Usage',
        description: `CPU usage is ${latestMetrics.cpu.usage.toFixed(2)}%, above threshold of ${this.alertThresholds.cpuUsage}%`,
        source: 'system',
        metadata: { cpuUsage: latestMetrics.cpu.usage, threshold: this.alertThresholds.cpuUsage }
      });
    }

    // Verificar memoria
    if (latestMetrics.memory.percentage > this.alertThresholds.memoryUsage) {
      this.createAlert({
        type: 'resource',
        severity: 'high',
        title: 'High Memory Usage',
        description: `Memory usage is ${latestMetrics.memory.percentage.toFixed(2)}%, above threshold of ${this.alertThresholds.memoryUsage}%`,
        source: 'system',
        metadata: { memoryUsage: latestMetrics.memory.percentage, threshold: this.alertThresholds.memoryUsage }
      });
    }

    // Verificar tiempo de respuesta
    if (latestMetrics.application.responseTime > this.alertThresholds.responseTime) {
      this.createAlert({
        type: 'performance',
        severity: 'medium',
        title: 'High Response Time',
        description: `Average response time is ${latestMetrics.application.responseTime.toFixed(2)}ms, above threshold of ${this.alertThresholds.responseTime}ms`,
        source: 'api',
        metadata: { responseTime: latestMetrics.application.responseTime, threshold: this.alertThresholds.responseTime }
      });
    }

    // Verificar tasa de error
    const errorRate = (latestMetrics.application.errors / latestMetrics.application.requests) * 100;
    if (errorRate > this.alertThresholds.errorRate) {
      this.createAlert({
        type: 'error',
        severity: 'high',
        title: 'High Error Rate',
        description: `Error rate is ${errorRate.toFixed(2)}%, above threshold of ${this.alertThresholds.errorRate}%`,
        source: 'api',
        metadata: { errorRate, threshold: this.alertThresholds.errorRate }
      });
    }
  }

  // Crear alerta
  createAlert(alertData: Omit<Alert, 'id' | 'timestamp' | 'acknowledged' | 'resolved'>): void {
    const alert: Alert = {
      ...alertData,
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      acknowledged: false,
      resolved: false
    };

    this.alerts.push(alert);
    this.emit('alert_created', alert);

    // Enviar notificación si es crítica
    if (alert.severity === 'critical') {
      this.emit('critical_alert', alert);
    }
  }

  // Obtener alertas
  getAlerts(filters?: {
    type?: string;
    severity?: string;
    acknowledged?: boolean;
    resolved?: boolean;
    limit?: number;
  }): Alert[] {
    let filteredAlerts = [...this.alerts];

    if (filters) {
      if (filters.type) {
        filteredAlerts = filteredAlerts.filter(a => a.type === filters.type);
      }
      if (filters.severity) {
        filteredAlerts = filteredAlerts.filter(a => a.severity === filters.severity);
      }
      if (filters.acknowledged !== undefined) {
        filteredAlerts = filteredAlerts.filter(a => a.acknowledged === filters.acknowledged);
      }
      if (filters.resolved !== undefined) {
        filteredAlerts = filteredAlerts.filter(a => a.resolved === filters.resolved);
      }
      if (filters.limit) {
        filteredAlerts = filteredAlerts.slice(0, filters.limit);
      }
    }

    return filteredAlerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  // Reconocer alerta
  acknowledgeAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      this.emit('alert_acknowledged', alert);
      return true;
    }
    return false;
  }

  // Resolver alerta
  resolveAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      this.emit('alert_resolved', alert);
      return true;
    }
    return false;
  }

  // Obtener datos del dashboard
  getDashboardData(): DashboardData {
    const latestMetrics = this.systemMetrics[this.systemMetrics.length - 1];
    const performanceStats = performanceOptimizationService.getPerformanceStats();
    const securityStats = securityService.getSecurityStats();
    const healthChecks = Array.from(this.healthChecks.values());
    
    // Calcular salud general del sistema
    const unhealthyServices = healthChecks.filter(h => h.status === 'unhealthy').length;
    const overallHealth = unhealthyServices === 0 ? 'healthy' : 
                         unhealthyServices <= 2 ? 'degraded' : 'unhealthy';
    
    // Obtener tendencias (últimas 24 horas)
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentMetrics = this.systemMetrics.filter(m => m.timestamp > oneDayAgo);
    
    const trends = {
      responseTime: recentMetrics.map(m => m.application.responseTime),
      errorRate: recentMetrics.map(m => (m.application.errors / m.application.requests) * 100),
      throughput: recentMetrics.map(m => m.application.requests / (m.application.uptime / 60)),
      cpuUsage: recentMetrics.map(m => m.cpu.usage),
      memoryUsage: recentMetrics.map(m => m.memory.percentage)
    };
    
    return {
      systemHealth: {
        overall: overallHealth,
        services: healthChecks,
        uptime: latestMetrics?.application.uptime || 0,
        lastIncident: this.alerts.find(a => a.severity === 'critical')?.timestamp || null
      },
      performance: {
        averageResponseTime: performanceStats.averageResponseTime,
        throughput: performanceStats.throughput,
        errorRate: performanceStats.errorRate,
        p95ResponseTime: performanceStats.p95ResponseTime,
        p99ResponseTime: performanceStats.p99ResponseTime
      },
      security: {
        activeThreats: securityStats.totalThreats,
        blockedIPs: securityStats.blockedIPs,
        securityScore: securityService.generateSecurityReport().summary.securityScore,
        lastThreat: securityStats.recentActivity[0]?.timestamp || null
      },
      resources: {
        cpuUsage: latestMetrics?.cpu.usage || 0,
        memoryUsage: latestMetrics?.memory.percentage || 0,
        diskUsage: latestMetrics?.disk.percentage || 0,
        networkLatency: latestMetrics?.network.latency || 0
      },
      alerts: this.getAlerts({ limit: 10 }),
      trends
    };
  }

  // Obtener métricas del sistema
  getSystemMetrics(filters?: {
    timeRange?: { start: Date; end: Date };
    limit?: number;
  }): SystemMetrics[] {
    let filteredMetrics = [...this.systemMetrics];

    if (filters) {
      if (filters.timeRange) {
        filteredMetrics = filteredMetrics.filter(m => 
          m.timestamp >= filters.timeRange!.start && 
          m.timestamp <= filters.timeRange!.end
        );
      }
      if (filters.limit) {
        filteredMetrics = filteredMetrics.slice(-filters.limit);
      }
    }

    return filteredMetrics;
  }

  // Obtener verificaciones de salud
  getHealthChecks(): HealthCheck[] {
    return Array.from(this.healthChecks.values());
  }

  // Obtener estado de un servicio específico
  getServiceHealth(serviceName: string): HealthCheck | null {
    return this.healthChecks.get(serviceName) || null;
  }

  // Métodos auxiliares
  private calculateCpuUsage(cpuUsage: NodeJS.CpuUsage): number {
    const totalUsage = cpuUsage.user + cpuUsage.system;
    return totalUsage / 1000000; // Convertir a segundos
  }

  private getRequestCount(): number {
    // En implementación real, obtener del contador de requests
    return Math.floor(Math.random() * 1000);
  }

  private getErrorCount(): number {
    // En implementación real, obtener del contador de errores
    return Math.floor(Math.random() * 50);
  }

  private getAverageResponseTime(): number {
    // En implementación real, obtener del servicio de rendimiento
    return Math.floor(Math.random() * 500) + 100;
  }

  private cleanupOldData(): void {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    
    // Limpiar métricas antiguas
    this.systemMetrics = this.systemMetrics.filter(m => m.timestamp > oneHourAgo);
    
    // Limpiar alertas resueltas antiguas
    this.alerts = this.alerts.filter(a => !a.resolved || a.timestamp > oneHourAgo);
  }

  // Configurar umbrales de alertas
  setAlertThresholds(thresholds: Record<string, any>): void {
    this.alertThresholds = { ...this.alertThresholds, ...thresholds };
    this.emit('thresholds_updated', this.alertThresholds);
  }

  // Obtener umbrales de alertas
  getAlertThresholds(): Record<string, any> {
    return { ...this.alertThresholds };
  }

  // Generar reporte de monitoreo
  generateMonitoringReport(): {
    summary: {
      overallHealth: string;
      totalAlerts: number;
      criticalAlerts: number;
      uptime: number;
      performanceScore: number;
    };
    healthChecks: HealthCheck[];
    alerts: Alert[];
    recommendations: string[];
  } {
    const dashboardData = this.getDashboardData();
    const criticalAlerts = this.alerts.filter(a => a.severity === 'critical').length;
    
    // Calcular puntuación de rendimiento (0-100)
    let performanceScore = 100;
    performanceScore -= dashboardData.performance.errorRate * 2;
    performanceScore -= Math.max(0, dashboardData.performance.averageResponseTime - 500) / 10;
    performanceScore -= Math.max(0, dashboardData.resources.cpuUsage - 50) / 2;
    performanceScore -= Math.max(0, dashboardData.resources.memoryUsage - 50) / 2;
    performanceScore = Math.max(0, performanceScore);
    
    const recommendations: string[] = [];
    
    if (dashboardData.performance.errorRate > 5) {
      recommendations.push('Investigar y corregir errores de aplicación');
    }
    
    if (dashboardData.performance.averageResponseTime > 1000) {
      recommendations.push('Optimizar consultas de base de datos y algoritmos');
    }
    
    if (dashboardData.resources.cpuUsage > 80) {
      recommendations.push('Considerar escalado horizontal o optimización de CPU');
    }
    
    if (dashboardData.resources.memoryUsage > 85) {
      recommendations.push('Optimizar uso de memoria y considerar escalado');
    }
    
    if (criticalAlerts > 0) {
      recommendations.push('Resolver alertas críticas inmediatamente');
    }
    
    return {
      summary: {
        overallHealth: dashboardData.systemHealth.overall,
        totalAlerts: this.alerts.length,
        criticalAlerts,
        uptime: dashboardData.systemHealth.uptime,
        performanceScore: parseFloat(performanceScore.toFixed(2))
      },
      healthChecks: dashboardData.systemHealth.services,
      alerts: this.getAlerts({ limit: 20 }),
      recommendations
    };
  }
}

export const monitoringService = new MonitoringService();

