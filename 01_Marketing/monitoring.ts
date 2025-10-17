import express from 'express';
import { monitoringService } from '../services/monitoringService';
import { securityService } from '../services/securityService';
import { performanceOptimizationService } from '../services/performanceOptimizationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Dashboard principal de monitoreo
router.get('/dashboard', authenticateToken, (req, res) => {
  try {
    const dashboardData = monitoringService.getDashboardData();
    res.json({
      success: true,
      data: dashboardData,
      message: 'Dashboard data retrieved successfully'
    });
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
});

// Verificaciones de salud del sistema
router.get('/health', (req, res) => {
  try {
    const healthChecks = monitoringService.getHealthChecks();
    const overallHealth = healthChecks.every(h => h.status === 'healthy') ? 'healthy' : 'degraded';
    
    res.json({
      success: true,
      data: {
        overall: overallHealth,
        services: healthChecks,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('Error fetching health checks:', error);
    res.status(500).json({ error: 'Failed to fetch health checks' });
  }
});

// Estado de un servicio específico
router.get('/health/:service', (req, res) => {
  try {
    const { service } = req.params;
    const healthCheck = monitoringService.getServiceHealth(service);
    
    if (!healthCheck) {
      return res.status(404).json({ error: 'Service not found' });
    }
    
    res.json({
      success: true,
      data: healthCheck
    });
  } catch (error) {
    console.error('Error fetching service health:', error);
    res.status(500).json({ error: 'Failed to fetch service health' });
  }
});

// Métricas del sistema
router.get('/metrics', authenticateToken, (req, res) => {
  try {
    const { timeRange, limit } = req.query;
    const filters: any = {};
    
    if (timeRange) {
      const [start, end] = (timeRange as string).split(',');
      filters.timeRange = {
        start: new Date(start),
        end: new Date(end)
      };
    }
    
    if (limit) {
      filters.limit = parseInt(limit as string);
    }
    
    const metrics = monitoringService.getSystemMetrics(filters);
    
    res.json({
      success: true,
      data: metrics,
      count: metrics.length
    });
  } catch (error) {
    console.error('Error fetching system metrics:', error);
    res.status(500).json({ error: 'Failed to fetch system metrics' });
  }
});

// Alertas del sistema
router.get('/alerts', authenticateToken, (req, res) => {
  try {
    const { type, severity, acknowledged, resolved, limit } = req.query;
    const filters: any = {};
    
    if (type) filters.type = type;
    if (severity) filters.severity = severity;
    if (acknowledged !== undefined) filters.acknowledged = acknowledged === 'true';
    if (resolved !== undefined) filters.resolved = resolved === 'true';
    if (limit) filters.limit = parseInt(limit as string);
    
    const alerts = monitoringService.getAlerts(filters);
    
    res.json({
      success: true,
      data: alerts,
      count: alerts.length
    });
  } catch (error) {
    console.error('Error fetching alerts:', error);
    res.status(500).json({ error: 'Failed to fetch alerts' });
  }
});

// Reconocer alerta
router.post('/alerts/:alertId/acknowledge', authenticateToken, (req, res) => {
  try {
    const { alertId } = req.params;
    const acknowledged = monitoringService.acknowledgeAlert(alertId);
    
    if (acknowledged) {
      res.json({
        success: true,
        message: 'Alert acknowledged successfully'
      });
    } else {
      res.status(404).json({ error: 'Alert not found' });
    }
  } catch (error) {
    console.error('Error acknowledging alert:', error);
    res.status(500).json({ error: 'Failed to acknowledge alert' });
  }
});

// Resolver alerta
router.post('/alerts/:alertId/resolve', authenticateToken, (req, res) => {
  try {
    const { alertId } = req.params;
    const resolved = monitoringService.resolveAlert(alertId);
    
    if (resolved) {
      res.json({
        success: true,
        message: 'Alert resolved successfully'
      });
    } else {
      res.status(404).json({ error: 'Alert not found' });
    }
  } catch (error) {
    console.error('Error resolving alert:', error);
    res.status(500).json({ error: 'Failed to resolve alert' });
  }
});

// Estadísticas de rendimiento
router.get('/performance', authenticateToken, (req, res) => {
  try {
    const performanceStats = performanceOptimizationService.getPerformanceStats();
    const cacheStats = performanceOptimizationService.getCacheStats();
    const recommendations = performanceOptimizationService.getOptimizationRecommendations();
    
    res.json({
      success: true,
      data: {
        performance: performanceStats,
        cache: cacheStats,
        recommendations
      }
    });
  } catch (error) {
    console.error('Error fetching performance stats:', error);
    res.status(500).json({ error: 'Failed to fetch performance stats' });
  }
});

// Estadísticas de seguridad
router.get('/security', authenticateToken, (req, res) => {
  try {
    const securityStats = securityService.getSecurityStats();
    const auditLogs = securityService.getAuditLogs({ limit: 50 });
    const threatLogs = securityService.getThreatLogs({ limit: 50 });
    const securityReport = securityService.generateSecurityReport();
    
    res.json({
      success: true,
      data: {
        stats: securityStats,
        auditLogs,
        threatLogs,
        report: securityReport
      }
    });
  } catch (error) {
    console.error('Error fetching security stats:', error);
    res.status(500).json({ error: 'Failed to fetch security stats' });
  }
});

// Configurar umbrales de alertas
router.post('/thresholds', authenticateToken, (req, res) => {
  try {
    const { thresholds } = req.body;
    
    if (!thresholds || typeof thresholds !== 'object') {
      return res.status(400).json({ error: 'Invalid thresholds data' });
    }
    
    monitoringService.setAlertThresholds(thresholds);
    
    res.json({
      success: true,
      message: 'Alert thresholds updated successfully'
    });
  } catch (error) {
    console.error('Error updating alert thresholds:', error);
    res.status(500).json({ error: 'Failed to update alert thresholds' });
  }
});

// Obtener umbrales de alertas
router.get('/thresholds', authenticateToken, (req, res) => {
  try {
    const thresholds = monitoringService.getAlertThresholds();
    
    res.json({
      success: true,
      data: thresholds
    });
  } catch (error) {
    console.error('Error fetching alert thresholds:', error);
    res.status(500).json({ error: 'Failed to fetch alert thresholds' });
  }
});

// Reporte de monitoreo
router.get('/report', authenticateToken, (req, res) => {
  try {
    const monitoringReport = monitoringService.generateMonitoringReport();
    const performanceReport = performanceOptimizationService.generatePerformanceReport();
    const securityReport = securityService.generateSecurityReport();
    
    res.json({
      success: true,
      data: {
        monitoring: monitoringReport,
        performance: performanceReport,
        security: securityReport,
        generatedAt: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('Error generating monitoring report:', error);
    res.status(500).json({ error: 'Failed to generate monitoring report' });
  }
});

// Estadísticas de caché
router.get('/cache', authenticateToken, (req, res) => {
  try {
    const cacheStats = performanceOptimizationService.getCacheStats();
    const cacheConfig = performanceOptimizationService.getCacheConfig();
    
    res.json({
      success: true,
      data: {
        stats: cacheStats,
        config: cacheConfig
      }
    });
  } catch (error) {
    console.error('Error fetching cache stats:', error);
    res.status(500).json({ error: 'Failed to fetch cache stats' });
  }
});

// Configurar caché
router.post('/cache/configure', authenticateToken, (req, res) => {
  try {
    const { config } = req.body;
    
    if (!config || typeof config !== 'object') {
      return res.status(400).json({ error: 'Invalid cache configuration' });
    }
    
    performanceOptimizationService.configureCache(config);
    
    res.json({
      success: true,
      message: 'Cache configuration updated successfully'
    });
  } catch (error) {
    console.error('Error configuring cache:', error);
    res.status(500).json({ error: 'Failed to configure cache' });
  }
});

// Invalidar caché
router.post('/cache/invalidate', authenticateToken, (req, res) => {
  try {
    const { pattern } = req.body;
    
    performanceOptimizationService.invalidateCache(pattern);
    
    res.json({
      success: true,
      message: 'Cache invalidated successfully'
    });
  } catch (error) {
    console.error('Error invalidating cache:', error);
    res.status(500).json({ error: 'Failed to invalidate cache' });
  }
});

// Limpiar datos antiguos
router.post('/cleanup', authenticateToken, (req, res) => {
  try {
    performanceOptimizationService.cleanupOldMetrics();
    
    res.json({
      success: true,
      message: 'Old data cleaned up successfully'
    });
  } catch (error) {
    console.error('Error cleaning up old data:', error);
    res.status(500).json({ error: 'Failed to clean up old data' });
  }
});

// Estado del sistema en tiempo real
router.get('/realtime', authenticateToken, (req, res) => {
  try {
    const dashboardData = monitoringService.getDashboardData();
    const latestMetrics = monitoringService.getSystemMetrics({ limit: 1 })[0];
    
    res.json({
      success: true,
      data: {
        timestamp: new Date().toISOString(),
        systemHealth: dashboardData.systemHealth.overall,
        performance: {
          responseTime: latestMetrics?.application.responseTime || 0,
          throughput: dashboardData.performance.throughput,
          errorRate: dashboardData.performance.errorRate
        },
        resources: {
          cpu: latestMetrics?.cpu.usage || 0,
          memory: latestMetrics?.memory.percentage || 0,
          disk: latestMetrics?.disk.percentage || 0
        },
        alerts: dashboardData.alerts.filter(a => !a.resolved).length,
        uptime: dashboardData.systemHealth.uptime
      }
    });
  } catch (error) {
    console.error('Error fetching real-time status:', error);
    res.status(500).json({ error: 'Failed to fetch real-time status' });
  }
});

// Métricas de tendencias
router.get('/trends', authenticateToken, (req, res) => {
  try {
    const { metric, period = '24h' } = req.query;
    
    const periodMs = period === '1h' ? 60 * 60 * 1000 :
                    period === '24h' ? 24 * 60 * 60 * 1000 :
                    period === '7d' ? 7 * 24 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
    
    const startTime = new Date(Date.now() - periodMs);
    const metrics = monitoringService.getSystemMetrics({
      timeRange: { start: startTime, end: new Date() }
    });
    
    let trendData: any[] = [];
    
    switch (metric) {
      case 'responseTime':
        trendData = metrics.map(m => ({
          timestamp: m.timestamp,
          value: m.application.responseTime
        }));
        break;
      case 'cpu':
        trendData = metrics.map(m => ({
          timestamp: m.timestamp,
          value: m.cpu.usage
        }));
        break;
      case 'memory':
        trendData = metrics.map(m => ({
          timestamp: m.timestamp,
          value: m.memory.percentage
        }));
        break;
      case 'throughput':
        trendData = metrics.map(m => ({
          timestamp: m.timestamp,
          value: m.application.requests / (m.application.uptime / 60)
        }));
        break;
      default:
        return res.status(400).json({ error: 'Invalid metric type' });
    }
    
    res.json({
      success: true,
      data: {
        metric,
        period,
        trends: trendData
      }
    });
  } catch (error) {
    console.error('Error fetching trends:', error);
    res.status(500).json({ error: 'Failed to fetch trends' });
  }
});

export default router;






