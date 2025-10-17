import express from 'express';
import { performanceAnalyticsService } from '../services/performanceAnalyticsService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener métricas de rendimiento
router.get('/metrics', authenticateToken, (req, res) => {
  try {
    const { limit = 100, type, name } = req.query;
    
    let metrics = performanceAnalyticsService.getMetrics(parseInt(limit as string));
    
    if (type) {
      metrics = metrics.filter(metric => metric.type === type);
    }
    
    if (name) {
      metrics = metrics.filter(metric => metric.name === name);
    }
    
    res.json({
      success: true,
      data: metrics,
      count: metrics.length
    });
  } catch (error) {
    console.error('Error fetching performance metrics:', error);
    res.status(500).json({ error: 'Failed to fetch performance metrics' });
  }
});

// Obtener alertas de rendimiento
router.get('/alerts', authenticateToken, (req, res) => {
  try {
    const { limit = 50, status, severity } = req.query;
    
    let alerts = performanceAnalyticsService.getAlerts(parseInt(limit as string));
    
    if (status) {
      alerts = alerts.filter(alert => alert.status === status);
    }
    
    if (severity) {
      alerts = alerts.filter(alert => alert.severity === severity);
    }
    
    res.json({
      success: true,
      data: alerts,
      count: alerts.length
    });
  } catch (error) {
    console.error('Error fetching performance alerts:', error);
    res.status(500).json({ error: 'Failed to fetch performance alerts' });
  }
});

// Obtener reportes de rendimiento
router.get('/reports', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const reports = performanceAnalyticsService.getReports(parseInt(limit as string));
    
    res.json({
      success: true,
      data: reports,
      count: reports.length
    });
  } catch (error) {
    console.error('Error fetching performance reports:', error);
    res.status(500).json({ error: 'Failed to fetch performance reports' });
  }
});

// Generar reporte de rendimiento
router.post('/reports/generate', authenticateToken, (req, res) => {
  try {
    const { start, end } = req.body;
    
    if (!start || !end) {
      return res.status(400).json({ error: 'Start and end dates are required' });
    }
    
    const period = {
      start: new Date(start),
      end: new Date(end)
    };
    
    const report = performanceAnalyticsService.generatePerformanceReport(period);
    
    res.json({
      success: true,
      data: report,
      message: 'Performance report generated successfully'
    });
  } catch (error) {
    console.error('Error generating performance report:', error);
    res.status(500).json({ error: 'Failed to generate performance report' });
  }
});

// Obtener optimizaciones de rendimiento
router.get('/optimizations', authenticateToken, (req, res) => {
  try {
    const { status, type, priority } = req.query;
    
    let optimizations = performanceAnalyticsService.getOptimizations();
    
    if (status) {
      optimizations = optimizations.filter(opt => opt.status === status);
    }
    
    if (type) {
      optimizations = optimizations.filter(opt => opt.type === type);
    }
    
    if (priority) {
      optimizations = optimizations.filter(opt => opt.priority === parseInt(priority as string));
    }
    
    res.json({
      success: true,
      data: optimizations,
      count: optimizations.length
    });
  } catch (error) {
    console.error('Error fetching performance optimizations:', error);
    res.status(500).json({ error: 'Failed to fetch performance optimizations' });
  }
});

// Obtener estadísticas de rendimiento
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = performanceAnalyticsService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching performance stats:', error);
    res.status(500).json({ error: 'Failed to fetch performance stats' });
  }
});

// Obtener dashboard de rendimiento
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = performanceAnalyticsService.getStats();
    const recentAlerts = performanceAnalyticsService.getAlerts(10);
    const recentReports = performanceAnalyticsService.getReports(5);
    const optimizations = performanceAnalyticsService.getOptimizations();
    
    const dashboard = {
      overview: {
        totalMetrics: stats.totalMetrics,
        activeAlerts: stats.activeAlerts,
        totalReports: stats.totalReports,
        pendingOptimizations: stats.pendingOptimizations,
        averageResponseTime: stats.averageResponseTime,
        currentCpuUsage: stats.currentCpuUsage,
        currentMemoryUsage: stats.currentMemoryUsage
      },
      recentAlerts: recentAlerts,
      recentReports: recentReports,
      optimizations: optimizations.map(opt => ({
        id: opt.id,
        name: opt.name,
        type: opt.type,
        status: opt.status,
        impact: opt.impact,
        effort: opt.effort,
        priority: opt.priority,
        estimatedImprovement: opt.estimatedImprovement
      })),
      performance: {
        averageResponseTime: stats.averageResponseTime,
        currentCpuUsage: stats.currentCpuUsage,
        currentMemoryUsage: stats.currentMemoryUsage,
        activeAlerts: stats.activeAlerts,
        pendingOptimizations: stats.pendingOptimizations
      }
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching performance dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch performance dashboard' });
  }
});

// Obtener métricas en tiempo real
router.get('/metrics/realtime', authenticateToken, (req, res) => {
  try {
    const { types } = req.query;
    
    let metrics = performanceAnalyticsService.getMetrics(50);
    
    if (types) {
      const typeList = (types as string).split(',');
      metrics = metrics.filter(metric => typeList.includes(metric.type));
    }
    
    // Agrupar métricas por tipo
    const groupedMetrics = metrics.reduce((acc, metric) => {
      if (!acc[metric.type]) {
        acc[metric.type] = [];
      }
      acc[metric.type].push(metric);
      return acc;
    }, {} as Record<string, any[]>);
    
    // Calcular promedios por tipo
    const realtimeData = Object.entries(groupedMetrics).map(([type, typeMetrics]) => ({
      type,
      currentValue: typeMetrics[0]?.value || 0,
      averageValue: typeMetrics.reduce((sum, m) => sum + m.value, 0) / typeMetrics.length,
      trend: this.calculateTrend(typeMetrics),
      lastUpdated: typeMetrics[0]?.timestamp || new Date()
    }));
    
    res.json({
      success: true,
      data: realtimeData
    });
  } catch (error) {
    console.error('Error fetching realtime metrics:', error);
    res.status(500).json({ error: 'Failed to fetch realtime metrics' });
  }
});

// Calcular tendencia de métricas
private calculateTrend(metrics: any[]): 'improving' | 'stable' | 'degrading' {
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

// Obtener logs de rendimiento
router.get('/logs/performance', authenticateToken, (req, res) => {
  try {
    const { type, severity, limit = 100 } = req.query;
    
    let alerts = performanceAnalyticsService.getAlerts(parseInt(limit as string));
    
    if (type) {
      alerts = alerts.filter(alert => alert.metricName === type);
    }
    
    if (severity) {
      alerts = alerts.filter(alert => alert.severity === severity);
    }
    
    res.json({
      success: true,
      data: alerts,
      count: alerts.length
    });
  } catch (error) {
    console.error('Error fetching performance logs:', error);
    res.status(500).json({ error: 'Failed to fetch performance logs' });
  }
});

// Obtener plantillas de optimización
router.get('/templates/optimization', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'cache_optimization_template',
        name: 'Cache Optimization',
        description: 'Implement caching to improve performance',
        type: 'caching',
        category: 'performance',
        features: ['Redis Caching', 'Memory Optimization', 'Query Caching'],
        impact: 'high',
        effort: 'medium',
        estimatedImprovement: 40
      },
      {
        id: 'database_optimization_template',
        name: 'Database Optimization',
        description: 'Optimize database queries and indexes',
        type: 'database',
        category: 'performance',
        features: ['Index Optimization', 'Query Tuning', 'Connection Pooling'],
        impact: 'high',
        effort: 'low',
        estimatedImprovement: 60
      },
      {
        id: 'api_optimization_template',
        name: 'API Optimization',
        description: 'Optimize API performance and response times',
        type: 'api',
        category: 'performance',
        features: ['Response Compression', 'Pagination', 'Rate Limiting'],
        impact: 'medium',
        effort: 'low',
        estimatedImprovement: 30
      },
      {
        id: 'memory_optimization_template',
        name: 'Memory Optimization',
        description: 'Optimize memory usage and garbage collection',
        type: 'memory',
        category: 'performance',
        features: ['Memory Pooling', 'GC Tuning', 'Memory Leak Detection'],
        impact: 'medium',
        effort: 'high',
        estimatedImprovement: 25
      },
      {
        id: 'network_optimization_template',
        name: 'Network Optimization',
        description: 'Optimize network performance and connectivity',
        type: 'network',
        category: 'performance',
        features: ['CDN Integration', 'Compression', 'Connection Optimization'],
        impact: 'medium',
        effort: 'medium',
        estimatedImprovement: 35
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching optimization templates:', error);
    res.status(500).json({ error: 'Failed to fetch optimization templates' });
  }
});

// Validar configuración de rendimiento
router.post('/validate', authenticateToken, (req, res) => {
  try {
    const { type, thresholds, monitoring } = req.body;
    
    if (!type || !thresholds) {
      return res.status(400).json({ error: 'Type and thresholds are required' });
    }
    
    // Simular validación de configuración
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validaciones específicas por tipo
    switch (type) {
      case 'response_time':
        if (!thresholds.average || thresholds.average <= 0) {
          validation.errors.push('Average response time threshold must be greater than 0');
        }
        if (!thresholds.p95 || thresholds.p95 <= 0) {
          validation.errors.push('P95 response time threshold must be greater than 0');
        }
        break;
      case 'throughput':
        if (!thresholds.minimum || thresholds.minimum <= 0) {
          validation.errors.push('Minimum throughput threshold must be greater than 0');
        }
        break;
      case 'error_rate':
        if (!thresholds.maximum || thresholds.maximum < 0 || thresholds.maximum > 100) {
          validation.errors.push('Maximum error rate threshold must be between 0 and 100');
        }
        break;
      case 'cpu_usage':
        if (!thresholds.warning || thresholds.warning < 0 || thresholds.warning > 100) {
          validation.errors.push('CPU warning threshold must be between 0 and 100');
        }
        if (!thresholds.critical || thresholds.critical < 0 || thresholds.critical > 100) {
          validation.errors.push('CPU critical threshold must be between 0 and 100');
        }
        break;
      case 'memory_usage':
        if (!thresholds.warning || thresholds.warning < 0 || thresholds.warning > 100) {
          validation.errors.push('Memory warning threshold must be between 0 and 100');
        }
        if (!thresholds.critical || thresholds.critical < 0 || thresholds.critical > 100) {
          validation.errors.push('Memory critical threshold must be between 0 and 100');
        }
        break;
      default:
        validation.warnings.push(`Unknown performance type: ${type}`);
    }
    
    // Validar configuración de monitoreo
    if (monitoring) {
      if (!monitoring.interval || monitoring.interval < 1000) {
        validation.warnings.push('Monitoring interval should be at least 1000ms');
      }
      if (!monitoring.retention || monitoring.retention < 24) {
        validation.warnings.push('Data retention should be at least 24 hours');
      }
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating performance configuration:', error);
    res.status(500).json({ error: 'Failed to validate performance configuration' });
  }
});

export default router;






