import { EventEmitter } from 'events';
import { performance } from 'perf_hooks';

export interface PerformanceMetrics {
  endpoint: string;
  method: string;
  responseTime: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage: NodeJS.CpuUsage;
  timestamp: Date;
  statusCode: number;
  requestSize: number;
  responseSize: number;
}

export interface CacheConfig {
  ttl: number; // Time to live in seconds
  maxSize: number; // Maximum number of items
  strategy: 'lru' | 'lfu' | 'fifo';
}

export interface OptimizationRecommendation {
  type: 'database' | 'cache' | 'memory' | 'cpu' | 'network' | 'algorithm';
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  impact: string;
  effort: 'low' | 'medium' | 'high';
  estimatedImprovement: number; // Percentage
}

export interface ResourceUsage {
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  cpu: {
    usage: number;
    loadAverage: number[];
  };
  disk: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    connections: number;
  };
}

export class PerformanceOptimizationService extends EventEmitter {
  private metrics: PerformanceMetrics[] = [];
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();
  private cacheConfig: CacheConfig;
  private resourceUsage: ResourceUsage;
  private optimizationRecommendations: OptimizationRecommendation[] = [];
  private isMonitoring: boolean = false;
  private monitoringInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.cacheConfig = {
      ttl: 300, // 5 minutes
      maxSize: 1000,
      strategy: 'lru'
    };
    this.resourceUsage = this.getCurrentResourceUsage();
    this.startMonitoring();
  }

  // Iniciar monitoreo de rendimiento
  startMonitoring(): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.monitoringInterval = setInterval(() => {
      this.collectResourceUsage();
      this.analyzePerformance();
      this.cleanupCache();
    }, 5000); // Cada 5 segundos
    
    console.log('Performance monitoring started');
  }

  // Detener monitoreo de rendimiento
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
    console.log('Performance monitoring stopped');
  }

  // Registrar métrica de rendimiento
  recordMetric(metric: Omit<PerformanceMetrics, 'timestamp'>): void {
    const fullMetric: PerformanceMetrics = {
      ...metric,
      timestamp: new Date()
    };
    
    this.metrics.push(fullMetric);
    
    // Mantener solo las últimas 1000 métricas
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
    
    // Emitir evento para notificaciones en tiempo real
    this.emit('metric', fullMetric);
    
    // Verificar si hay problemas de rendimiento
    this.checkPerformanceThresholds(fullMetric);
  }

  // Obtener métricas de rendimiento
  getMetrics(filters?: {
    endpoint?: string;
    method?: string;
    timeRange?: { start: Date; end: Date };
    limit?: number;
  }): PerformanceMetrics[] {
    let filteredMetrics = [...this.metrics];
    
    if (filters) {
      if (filters.endpoint) {
        filteredMetrics = filteredMetrics.filter(m => m.endpoint.includes(filters.endpoint!));
      }
      if (filters.method) {
        filteredMetrics = filteredMetrics.filter(m => m.method === filters.method);
      }
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

  // Obtener estadísticas de rendimiento
  getPerformanceStats(): {
    averageResponseTime: number;
    p95ResponseTime: number;
    p99ResponseTime: number;
    totalRequests: number;
    errorRate: number;
    throughput: number; // requests per second
    memoryUsage: {
      average: number;
      peak: number;
      current: number;
    };
    cpuUsage: {
      average: number;
      peak: number;
      current: number;
    };
  } {
    if (this.metrics.length === 0) {
      return {
        averageResponseTime: 0,
        p95ResponseTime: 0,
        p99ResponseTime: 0,
        totalRequests: 0,
        errorRate: 0,
        throughput: 0,
        memoryUsage: { average: 0, peak: 0, current: 0 },
        cpuUsage: { average: 0, peak: 0, current: 0 }
      };
    }
    
    const responseTimes = this.metrics.map(m => m.responseTime).sort((a, b) => a - b);
    const errorCount = this.metrics.filter(m => m.statusCode >= 400).length;
    const totalRequests = this.metrics.length;
    
    const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
    const p95ResponseTime = responseTimes[Math.floor(responseTimes.length * 0.95)];
    const p99ResponseTime = responseTimes[Math.floor(responseTimes.length * 0.99)];
    
    const errorRate = (errorCount / totalRequests) * 100;
    
    // Calcular throughput (requests por segundo)
    const timeRange = this.metrics[this.metrics.length - 1].timestamp.getTime() - this.metrics[0].timestamp.getTime();
    const throughput = totalRequests / (timeRange / 1000);
    
    // Calcular uso de memoria
    const memoryUsages = this.metrics.map(m => m.memoryUsage.heapUsed);
    const averageMemory = memoryUsages.reduce((sum, usage) => sum + usage, 0) / memoryUsages.length;
    const peakMemory = Math.max(...memoryUsages);
    const currentMemory = this.resourceUsage.memory.used;
    
    // Calcular uso de CPU
    const cpuUsages = this.metrics.map(m => m.cpuUsage.user + m.cpuUsage.system);
    const averageCpu = cpuUsages.reduce((sum, usage) => sum + usage, 0) / cpuUsages.length;
    const peakCpu = Math.max(...cpuUsages);
    const currentCpu = this.resourceUsage.cpu.usage;
    
    return {
      averageResponseTime: parseFloat(averageResponseTime.toFixed(2)),
      p95ResponseTime: parseFloat(p95ResponseTime.toFixed(2)),
      p99ResponseTime: parseFloat(p99ResponseTime.toFixed(2)),
      totalRequests,
      errorRate: parseFloat(errorRate.toFixed(2)),
      throughput: parseFloat(throughput.toFixed(2)),
      memoryUsage: {
        average: parseFloat(averageMemory.toFixed(2)),
        peak: parseFloat(peakMemory.toFixed(2)),
        current: parseFloat(currentMemory.toFixed(2))
      },
      cpuUsage: {
        average: parseFloat(averageCpu.toFixed(2)),
        peak: parseFloat(peakCpu.toFixed(2)),
        current: parseFloat(currentCpu.toFixed(2))
      }
    };
  }

  // Sistema de caché inteligente
  setCache(key: string, data: any, ttl?: number): void {
    const cacheTTL = ttl || this.cacheConfig.ttl;
    const timestamp = Date.now();
    
    // Verificar si el caché está lleno
    if (this.cache.size >= this.cacheConfig.maxSize) {
      this.evictCache();
    }
    
    this.cache.set(key, {
      data,
      timestamp,
      ttl: cacheTTL
    });
    
    this.emit('cache_set', { key, size: JSON.stringify(data).length });
  }

  getCache(key: string): any | null {
    const cached = this.cache.get(key);
    
    if (!cached) {
      return null;
    }
    
    // Verificar si el caché ha expirado
    const now = Date.now();
    if (now - cached.timestamp > cached.ttl * 1000) {
      this.cache.delete(key);
      return null;
    }
    
    // Actualizar timestamp para LRU
    if (this.cacheConfig.strategy === 'lru') {
      cached.timestamp = now;
    }
    
    this.emit('cache_hit', { key });
    return cached.data;
  }

  // Invalidar caché
  invalidateCache(pattern?: string): void {
    if (pattern) {
      const regex = new RegExp(pattern);
      for (const key of this.cache.keys()) {
        if (regex.test(key)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
    
    this.emit('cache_invalidated', { pattern });
  }

  // Obtener estadísticas del caché
  getCacheStats(): {
    size: number;
    hitRate: number;
    memoryUsage: number;
    keys: string[];
  } {
    const keys = Array.from(this.cache.keys());
    const memoryUsage = keys.reduce((total, key) => {
      const cached = this.cache.get(key);
      return total + JSON.stringify(cached?.data || {}).length;
    }, 0);
    
    return {
      size: this.cache.size,
      hitRate: 0, // Se calcularía con contadores de hit/miss
      memoryUsage,
      keys
    };
  }

  // Análisis de rendimiento y recomendaciones
  analyzePerformance(): void {
    const stats = this.getPerformanceStats();
    const recommendations: OptimizationRecommendation[] = [];
    
    // Análisis de tiempo de respuesta
    if (stats.averageResponseTime > 1000) {
      recommendations.push({
        type: 'algorithm',
        priority: 'high',
        description: 'Tiempo de respuesta promedio muy alto',
        impact: 'Mejorar la experiencia del usuario',
        effort: 'medium',
        estimatedImprovement: 30
      });
    }
    
    // Análisis de uso de memoria
    if (stats.memoryUsage.current > 500 * 1024 * 1024) { // 500MB
      recommendations.push({
        type: 'memory',
        priority: 'medium',
        description: 'Uso de memoria elevado',
        impact: 'Reducir el uso de memoria y mejorar estabilidad',
        effort: 'high',
        estimatedImprovement: 20
      });
    }
    
    // Análisis de CPU
    if (stats.cpuUsage.current > 80) {
      recommendations.push({
        type: 'cpu',
        priority: 'high',
        description: 'Uso de CPU elevado',
        impact: 'Mejorar la capacidad de procesamiento',
        effort: 'high',
        estimatedImprovement: 25
      });
    }
    
    // Análisis de tasa de error
    if (stats.errorRate > 5) {
      recommendations.push({
        type: 'database',
        priority: 'critical',
        description: 'Tasa de error elevada',
        impact: 'Mejorar la confiabilidad del sistema',
        effort: 'medium',
        estimatedImprovement: 40
      });
    }
    
    // Análisis de throughput
    if (stats.throughput < 10) {
      recommendations.push({
        type: 'network',
        priority: 'medium',
        description: 'Throughput bajo',
        impact: 'Mejorar la capacidad de procesamiento de requests',
        effort: 'medium',
        estimatedImprovement: 35
      });
    }
    
    this.optimizationRecommendations = recommendations;
    this.emit('recommendations_updated', recommendations);
  }

  // Obtener recomendaciones de optimización
  getOptimizationRecommendations(): OptimizationRecommendation[] {
    return [...this.optimizationRecommendations];
  }

  // Obtener uso de recursos actual
  getCurrentResourceUsage(): ResourceUsage {
    const memoryUsage = process.memoryUsage();
    const cpuUsage = process.cpuUsage();
    
    return {
      memory: {
        used: memoryUsage.heapUsed,
        total: memoryUsage.heapTotal,
        percentage: (memoryUsage.heapUsed / memoryUsage.heapTotal) * 100
      },
      cpu: {
        usage: (cpuUsage.user + cpuUsage.system) / 1000000, // Convertir a segundos
        loadAverage: process.platform === 'win32' ? [0, 0, 0] : require('os').loadavg()
      },
      disk: {
        used: 0, // Se calcularía con fs.stat
        total: 0,
        percentage: 0
      },
      network: {
        bytesIn: 0, // Se calcularía con netstat
        bytesOut: 0,
        connections: 0
      }
    };
  }

  // Recopilar uso de recursos
  private collectResourceUsage(): void {
    this.resourceUsage = this.getCurrentResourceUsage();
    this.emit('resource_usage', this.resourceUsage);
  }

  // Verificar umbrales de rendimiento
  private checkPerformanceThresholds(metric: PerformanceMetrics): void {
    const thresholds = {
      responseTime: 2000, // 2 segundos
      memoryUsage: 1000 * 1024 * 1024, // 1GB
      cpuUsage: 90, // 90%
      errorRate: 10 // 10%
    };
    
    if (metric.responseTime > thresholds.responseTime) {
      this.emit('performance_alert', {
        type: 'response_time',
        value: metric.responseTime,
        threshold: thresholds.responseTime,
        endpoint: metric.endpoint
      });
    }
    
    if (metric.memoryUsage.heapUsed > thresholds.memoryUsage) {
      this.emit('performance_alert', {
        type: 'memory_usage',
        value: metric.memoryUsage.heapUsed,
        threshold: thresholds.memoryUsage,
        endpoint: metric.endpoint
      });
    }
    
    if (metric.statusCode >= 400) {
      this.emit('performance_alert', {
        type: 'error_rate',
        value: metric.statusCode,
        threshold: 400,
        endpoint: metric.endpoint
      });
    }
  }

  // Limpiar caché expirado
  private cleanupCache(): void {
    const now = Date.now();
    const expiredKeys: string[] = [];
    
    for (const [key, cached] of this.cache.entries()) {
      if (now - cached.timestamp > cached.ttl * 1000) {
        expiredKeys.push(key);
      }
    }
    
    expiredKeys.forEach(key => this.cache.delete(key));
    
    if (expiredKeys.length > 0) {
      this.emit('cache_cleanup', { expiredKeys: expiredKeys.length });
    }
  }

  // Evictar elementos del caché según la estrategia
  private evictCache(): void {
    const keys = Array.from(this.cache.keys());
    
    switch (this.cacheConfig.strategy) {
      case 'lru':
        // Eliminar el elemento más antiguo
        const oldestKey = keys.reduce((oldest, key) => {
          const current = this.cache.get(key);
          const oldestCached = this.cache.get(oldest);
          return current!.timestamp < oldestCached!.timestamp ? key : oldest;
        });
        this.cache.delete(oldestKey);
        break;
        
      case 'lfu':
        // Eliminar el elemento menos frecuentemente usado
        // Implementación simplificada - eliminar el primero
        this.cache.delete(keys[0]);
        break;
        
      case 'fifo':
        // Eliminar el primer elemento (FIFO)
        this.cache.delete(keys[0]);
        break;
    }
  }

  // Configurar caché
  configureCache(config: Partial<CacheConfig>): void {
    this.cacheConfig = { ...this.cacheConfig, ...config };
    this.emit('cache_configured', this.cacheConfig);
  }

  // Obtener configuración del caché
  getCacheConfig(): CacheConfig {
    return { ...this.cacheConfig };
  }

  // Generar reporte de rendimiento
  generatePerformanceReport(): {
    summary: {
      averageResponseTime: number;
      errorRate: number;
      throughput: number;
      memoryUsage: number;
      cpuUsage: number;
    };
    recommendations: OptimizationRecommendation[];
    cacheStats: any;
    resourceUsage: ResourceUsage;
  } {
    const stats = this.getPerformanceStats();
    const recommendations = this.getOptimizationRecommendations();
    const cacheStats = this.getCacheStats();
    
    return {
      summary: {
        averageResponseTime: stats.averageResponseTime,
        errorRate: stats.errorRate,
        throughput: stats.throughput,
        memoryUsage: stats.memoryUsage.current,
        cpuUsage: stats.cpuUsage.current
      },
      recommendations,
      cacheStats,
      resourceUsage: this.resourceUsage
    };
  }

  // Limpiar métricas antiguas
  cleanupOldMetrics(): void {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    this.metrics = this.metrics.filter(m => m.timestamp > oneHourAgo);
    this.emit('metrics_cleaned', { remaining: this.metrics.length });
  }
}

export const performanceOptimizationService = new PerformanceOptimizationService();

