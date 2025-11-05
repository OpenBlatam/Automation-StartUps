import express from 'express';
import { feedbackAnalyticsService } from '../services/feedbackAnalyticsService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener analytics avanzados
router.get('/advanced', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics,
      period
    });
  } catch (error) {
    console.error('Error fetching advanced analytics:', error);
    res.status(500).json({ error: 'Failed to fetch advanced analytics' });
  }
});

// Obtener métricas del dashboard
router.get('/dashboard', authenticateToken, async (req, res) => {
  try {
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    res.json({
      success: true,
      data: metrics
    });
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    res.status(500).json({ error: 'Failed to fetch dashboard metrics' });
  }
});

// Obtener tendencias de sentimiento
router.get('/sentiment-trends', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.sentimentTrends,
      period
    });
  } catch (error) {
    console.error('Error fetching sentiment trends:', error);
    res.status(500).json({ error: 'Failed to fetch sentiment trends' });
  }
});

// Obtener análisis regional
router.get('/regional-analysis', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.regionalAnalysis,
      period
    });
  } catch (error) {
    console.error('Error fetching regional analysis:', error);
    res.status(500).json({ error: 'Failed to fetch regional analysis' });
  });
});

// Obtener rendimiento por fuente
router.get('/source-performance', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.sourcePerformance,
      period
    });
  } catch (error) {
    console.error('Error fetching source performance:', error);
    res.status(500).json({ error: 'Failed to fetch source performance' });
  });
});

// Obtener insights predictivos
router.get('/predictive-insights', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.predictiveInsights,
      period
    });
  } catch (error) {
    console.error('Error fetching predictive insights:', error);
    res.status(500).json({ error: 'Failed to fetch predictive insights' });
  });
});

// Obtener análisis competitivo
router.get('/competitive-analysis', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.competitiveAnalysis,
      period
    });
  } catch (error) {
    console.error('Error fetching competitive analysis:', error);
    res.status(500).json({ error: 'Failed to fetch competitive analysis' });
  });
});

// Obtener recomendaciones de IA
router.get('/ai-recommendations', authenticateToken, async (req, res) => {
  try {
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    
    res.json({
      success: true,
      data: analytics.aiRecommendations,
      period
    });
  } catch (error) {
    console.error('Error fetching AI recommendations:', error);
    res.status(500).json({ error: 'Failed to fetch AI recommendations' });
  });
});

// Obtener alertas
router.get('/alerts', authenticateToken, async (req, res) => {
  try {
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    res.json({
      success: true,
      data: metrics.alerts
    });
  } catch (error) {
    console.error('Error fetching alerts:', error);
    res.status(500).json({ error: 'Failed to fetch alerts' });
  }
});

// Obtener acciones rápidas
router.get('/quick-actions', authenticateToken, async (req, res) => {
  try {
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    res.json({
      success: true,
      data: metrics.quickActions
    });
  } catch (error) {
    console.error('Error fetching quick actions:', error);
    res.status(500).json({ error: 'Failed to fetch quick actions' });
  });
});

// Obtener métricas de resumen
router.get('/overview', authenticateToken, async (req, res) => {
  try {
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    res.json({
      success: true,
      data: metrics.overview
    });
  } catch (error) {
    console.error('Error fetching overview metrics:', error);
    res.status(500).json({ error: 'Failed to fetch overview metrics' });
  });
});

// Obtener métricas de tendencias
router.get('/trends', authenticateToken, async (req, res) => {
  try {
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    res.json({
      success: true,
      data: metrics.trends
    });
  } catch (error) {
    console.error('Error fetching trend metrics:', error);
    res.status(500).json({ error: 'Failed to fetch trend metrics' });
  });
});

// Obtener análisis por región específica
router.get('/regional/:region', authenticateToken, async (req, res) => {
  try {
    const { region } = req.params;
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    const regionalData = analytics.regionalAnalysis.find(ra => ra.region === region);
    
    if (!regionalData) {
      return res.status(404).json({ error: 'No data found for this region' });
    }

    res.json({
      success: true,
      data: regionalData,
      region,
      period
    });
  } catch (error) {
    console.error('Error fetching regional data:', error);
    res.status(500).json({ error: 'Failed to fetch regional data' });
  }
});

// Obtener análisis por fuente específica
router.get('/source/:source', authenticateToken, async (req, res) => {
  try {
    const { source } = req.params;
    const { period = '30d' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    const sourceData = analytics.sourcePerformance.find(sp => sp.source === source);
    
    if (!sourceData) {
      return res.status(404).json({ error: 'No data found for this source' });
    }

    res.json({
      success: true,
      data: sourceData,
      source,
      period
    });
  } catch (error) {
    console.error('Error fetching source data:', error);
    res.status(500).json({ error: 'Failed to fetch source data' });
  }
});

// Obtener recomendaciones por prioridad
router.get('/recommendations/:priority', authenticateToken, async (req, res) => {
  try {
    const { priority } = req.params;
    const { period = '30d' } = req.query;
    
    if (!['high', 'medium', 'low'].includes(priority)) {
      return res.status(400).json({ error: 'Invalid priority. Use high, medium, or low' });
    }
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    const filteredRecommendations = analytics.aiRecommendations.filter(
      rec => rec.priority === priority
    );
    
    res.json({
      success: true,
      data: filteredRecommendations,
      priority,
      period
    });
  } catch (error) {
    console.error('Error fetching recommendations by priority:', error);
    res.status(500).json({ error: 'Failed to fetch recommendations by priority' });
  }
});

// Obtener estadísticas de caché
router.get('/cache-stats', authenticateToken, async (req, res) => {
  try {
    const stats = feedbackAnalyticsService.getCacheStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching cache stats:', error);
    res.status(500).json({ error: 'Failed to fetch cache stats' });
  }
});

// Limpiar caché
router.post('/clear-cache', authenticateToken, async (req, res) => {
  try {
    feedbackAnalyticsService.clearCache();
    
    res.json({
      success: true,
      message: 'Cache cleared successfully'
    });
  } catch (error) {
    console.error('Error clearing cache:', error);
    res.status(500).json({ error: 'Failed to clear cache' });
  }
});

// Obtener reporte completo
router.get('/report', authenticateToken, async (req, res) => {
  try {
    const { period = '30d', format = 'json' } = req.query;
    
    const analytics = await feedbackAnalyticsService.getAdvancedAnalytics(period as string);
    const metrics = await feedbackAnalyticsService.getDashboardMetrics();
    
    const report = {
      period,
      generatedAt: new Date(),
      analytics,
      metrics,
      summary: {
        totalInsights: analytics.aiRecommendations.length,
        totalAlerts: metrics.alerts.length,
        totalActions: metrics.quickActions.length,
        cacheStatus: feedbackAnalyticsService.getCacheStats()
      }
    };

    if (format === 'csv') {
      const csv = convertToCSV(report);
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename=feedback_analytics_report.csv');
      res.send(csv);
    } else {
      res.json({
        success: true,
        data: report
      });
    }
  } catch (error) {
    console.error('Error generating report:', error);
    res.status(500).json({ error: 'Failed to generate report' });
  }
});

// Función auxiliar para convertir a CSV
function convertToCSV(data: any): string {
  // Implementar conversión a CSV según necesidades específicas
  const headers = ['Metric', 'Value', 'Period', 'Generated At'];
  const rows = [
    ['Total Insights', data.summary.totalInsights, data.period, data.generatedAt],
    ['Total Alerts', data.summary.totalAlerts, data.period, data.generatedAt],
    ['Total Actions', data.summary.totalActions, data.period, data.generatedAt]
  ];

  return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
}

export default router;
