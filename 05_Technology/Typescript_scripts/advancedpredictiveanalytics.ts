import express from 'express';
import { advancedPredictiveAnalyticsService } from '../services/advancedPredictiveAnalyticsService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener modelos
router.get('/models', authenticateToken, (req, res) => {
  try {
    const models = advancedPredictiveAnalyticsService.getModels();
    
    res.json({
      success: true,
      data: models,
      count: models.length
    });
  } catch (error) {
    console.error('Error fetching predictive models:', error);
    res.status(500).json({ error: 'Failed to fetch predictive models' });
  }
});

// Obtener modelo específico
router.get('/models/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const models = advancedPredictiveAnalyticsService.getModels();
    const model = models.find(m => m.id === id);
    
    if (!model) {
      return res.status(404).json({ error: 'Predictive model not found' });
    }
    
    res.json({
      success: true,
      data: model
    });
  } catch (error) {
    console.error('Error fetching predictive model:', error);
    res.status(500).json({ error: 'Failed to fetch predictive model' });
  }
});

// Crear predicción
router.post('/predict', authenticateToken, (req, res) => {
  try {
    const { customerId, modelId, features } = req.body;
    
    if (!customerId || !modelId || !features) {
      return res.status(400).json({ 
        error: 'Missing required fields: customerId, modelId, features' 
      });
    }
    
    const predictionId = advancedPredictiveAnalyticsService.createPrediction(
      customerId, 
      modelId, 
      features
    );
    
    res.json({
      success: true,
      data: { predictionId },
      message: 'Prediction created successfully'
    });
  } catch (error) {
    console.error('Error creating prediction:', error);
    res.status(500).json({ error: 'Failed to create prediction' });
  }
});

// Obtener predicciones
router.get('/predictions', authenticateToken, (req, res) => {
  try {
    const { limit = 50, modelId, customerId, type } = req.query;
    
    let predictions = advancedPredictiveAnalyticsService.getPredictions(parseInt(limit as string));
    
    if (modelId) {
      predictions = predictions.filter(p => p.modelId === modelId);
    }
    
    if (customerId) {
      predictions = predictions.filter(p => p.customerId === customerId);
    }
    
    if (type) {
      predictions = predictions.filter(p => p.predictionType === type);
    }
    
    res.json({
      success: true,
      data: predictions,
      count: predictions.length
    });
  } catch (error) {
    console.error('Error fetching predictions:', error);
    res.status(500).json({ error: 'Failed to fetch predictions' });
  }
});

// Obtener predicción específica
router.get('/predictions/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const predictions = advancedPredictiveAnalyticsService.getPredictions();
    const prediction = predictions.find(p => p.id === id);
    
    if (!prediction) {
      return res.status(404).json({ error: 'Prediction not found' });
    }
    
    res.json({
      success: true,
      data: prediction
    });
  } catch (error) {
    console.error('Error fetching prediction:', error);
    res.status(500).json({ error: 'Failed to fetch prediction' });
  }
});

// Obtener alertas
router.get('/alerts', authenticateToken, (req, res) => {
  try {
    const { limit = 50, severity, status, type } = req.query;
    
    let alerts = advancedPredictiveAnalyticsService.getAlerts(parseInt(limit as string));
    
    if (severity) {
      alerts = alerts.filter(a => a.severity === severity);
    }
    
    if (status) {
      alerts = alerts.filter(a => a.status === status);
    }
    
    if (type) {
      alerts = alerts.filter(a => a.type === type);
    }
    
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

// Obtener insights
router.get('/insights', authenticateToken, (req, res) => {
  try {
    const { limit = 50, type, impact } = req.query;
    
    let insights = advancedPredictiveAnalyticsService.getInsights(parseInt(limit as string));
    
    if (type) {
      insights = insights.filter(i => i.type === type);
    }
    
    if (impact) {
      insights = insights.filter(i => i.impact === impact);
    }
    
    res.json({
      success: true,
      data: insights,
      count: insights.length
    });
  } catch (error) {
    console.error('Error fetching insights:', error);
    res.status(500).json({ error: 'Failed to fetch insights' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const dashboard = advancedPredictiveAnalyticsService.getDashboard();
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching predictive analytics dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch predictive analytics dashboard' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedPredictiveAnalyticsService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching predictive analytics stats:', error);
    res.status(500).json({ error: 'Failed to fetch predictive analytics stats' });
  }
});

// Obtener predicciones por tipo
router.get('/predictions/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const predictions = advancedPredictiveAnalyticsService.getPredictions(parseInt(limit as string))
      .filter(p => p.predictionType === type);
    
    res.json({
      success: true,
      data: predictions,
      count: predictions.length
    });
  } catch (error) {
    console.error('Error fetching predictions by type:', error);
    res.status(500).json({ error: 'Failed to fetch predictions by type' });
  }
});

// Obtener predicciones por cliente
router.get('/predictions/customer/:customerId', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const { limit = 20 } = req.query;
    
    const predictions = advancedPredictiveAnalyticsService.getPredictions(parseInt(limit as string))
      .filter(p => p.customerId === customerId);
    
    res.json({
      success: true,
      data: predictions,
      count: predictions.length
    });
  } catch (error) {
    console.error('Error fetching customer predictions:', error);
    res.status(500).json({ error: 'Failed to fetch customer predictions' });
  }
});

// Obtener alertas críticas
router.get('/alerts/critical', authenticateToken, (req, res) => {
  try {
    const { limit = 20 } = req.query;
    
    const alerts = advancedPredictiveAnalyticsService.getAlerts(parseInt(limit as string))
      .filter(a => a.severity === 'critical')
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
    
    res.json({
      success: true,
      data: alerts,
      count: alerts.length
    });
  } catch (error) {
    console.error('Error fetching critical alerts:', error);
    res.status(500).json({ error: 'Failed to fetch critical alerts' });
  }
});

// Obtener alertas por tipo
router.get('/alerts/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const alerts = advancedPredictiveAnalyticsService.getAlerts(parseInt(limit as string))
      .filter(a => a.type === type);
    
    res.json({
      success: true,
      data: alerts,
      count: alerts.length
    });
  } catch (error) {
    console.error('Error fetching alerts by type:', error);
    res.status(500).json({ error: 'Failed to fetch alerts by type' });
  }
});

// Obtener insights por tipo
router.get('/insights/type/:type', authenticateToken, (req, res) => {
  try {
    const { type } = req.params;
    const { limit = 50 } = req.query;
    
    const insights = advancedPredictiveAnalyticsService.getInsights(parseInt(limit as string))
      .filter(i => i.type === type);
    
    res.json({
      success: true,
      data: insights,
      count: insights.length
    });
  } catch (error) {
    console.error('Error fetching insights by type:', error);
    res.status(500).json({ error: 'Failed to fetch insights by type' });
  }
});

// Obtener insights accionables
router.get('/insights/actionable', authenticateToken, (req, res) => {
  try {
    const { limit = 50 } = req.query;
    
    const insights = advancedPredictiveAnalyticsService.getInsights(parseInt(limit as string))
      .filter(i => i.actionable);
    
    res.json({
      success: true,
      data: insights,
      count: insights.length
    });
  } catch (error) {
    console.error('Error fetching actionable insights:', error);
    res.status(500).json({ error: 'Failed to fetch actionable insights' });
  }
});

// Obtener reporte de predicciones
router.get('/predictions/report', authenticateToken, (req, res) => {
  try {
    const { startDate, endDate, modelId, type } = req.query;
    
    let predictions = advancedPredictiveAnalyticsService.getPredictions();
    
    // Filtrar por fecha si se proporciona
    if (startDate) {
      const start = new Date(startDate as string);
      predictions = predictions.filter(p => p.createdAt >= start);
    }
    
    if (endDate) {
      const end = new Date(endDate as string);
      predictions = predictions.filter(p => p.createdAt <= end);
    }
    
    // Filtrar por modelo si se proporciona
    if (modelId) {
      predictions = predictions.filter(p => p.modelId === modelId);
    }
    
    // Filtrar por tipo si se proporciona
    if (type) {
      predictions = predictions.filter(p => p.predictionType === type);
    }
    
    // Generar reporte
    const report = {
      summary: {
        totalPredictions: predictions.length,
        averageConfidence: predictions.length > 0 
          ? predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length 
          : 0,
        averageValue: predictions.length > 0 
          ? predictions.reduce((sum, p) => sum + p.value, 0) / predictions.length 
          : 0
      },
      byType: predictions.reduce((acc, p) => {
        acc[p.predictionType] = (acc[p.predictionType] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byModel: predictions.reduce((acc, p) => {
        acc[p.modelId] = (acc[p.modelId] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      predictions: predictions.slice(0, 100) // Limitar a 100 predicciones
    };
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error fetching predictions report:', error);
    res.status(500).json({ error: 'Failed to fetch predictions report' });
  }
});

// Obtener reporte de alertas
router.get('/alerts/report', authenticateToken, (req, res) => {
  try {
    const { startDate, endDate, severity, type } = req.query;
    
    let alerts = advancedPredictiveAnalyticsService.getAlerts();
    
    // Filtrar por fecha si se proporciona
    if (startDate) {
      const start = new Date(startDate as string);
      alerts = alerts.filter(a => a.createdAt >= start);
    }
    
    if (endDate) {
      const end = new Date(endDate as string);
      alerts = alerts.filter(a => a.createdAt <= end);
    }
    
    // Filtrar por severidad si se proporciona
    if (severity) {
      alerts = alerts.filter(a => a.severity === severity);
    }
    
    // Filtrar por tipo si se proporciona
    if (type) {
      alerts = alerts.filter(a => a.type === type);
    }
    
    // Generar reporte
    const report = {
      summary: {
        totalAlerts: alerts.length,
        criticalAlerts: alerts.filter(a => a.severity === 'critical').length,
        highAlerts: alerts.filter(a => a.severity === 'high').length,
        mediumAlerts: alerts.filter(a => a.severity === 'medium').length,
        lowAlerts: alerts.filter(a => a.severity === 'low').length
      },
      byType: alerts.reduce((acc, a) => {
        acc[a.type] = (acc[a.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      bySeverity: alerts.reduce((acc, a) => {
        acc[a.severity] = (acc[a.severity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byStatus: alerts.reduce((acc, a) => {
        acc[a.status] = (acc[a.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      alerts: alerts.slice(0, 100) // Limitar a 100 alertas
    };
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error fetching alerts report:', error);
    res.status(500).json({ error: 'Failed to fetch alerts report' });
  }
});

// Obtener reporte de insights
router.get('/insights/report', authenticateToken, (req, res) => {
  try {
    const { startDate, endDate, type, impact } = req.query;
    
    let insights = advancedPredictiveAnalyticsService.getInsights();
    
    // Filtrar por fecha si se proporciona
    if (startDate) {
      const start = new Date(startDate as string);
      insights = insights.filter(i => i.generatedAt >= start);
    }
    
    if (endDate) {
      const end = new Date(endDate as string);
      insights = insights.filter(i => i.generatedAt <= end);
    }
    
    // Filtrar por tipo si se proporciona
    if (type) {
      insights = insights.filter(i => i.type === type);
    }
    
    // Filtrar por impacto si se proporciona
    if (impact) {
      insights = insights.filter(i => i.impact === impact);
    }
    
    // Generar reporte
    const report = {
      summary: {
        totalInsights: insights.length,
        actionableInsights: insights.filter(i => i.actionable).length,
        averageConfidence: insights.length > 0 
          ? insights.reduce((sum, i) => sum + i.confidence, 0) / insights.length 
          : 0
      },
      byType: insights.reduce((acc, i) => {
        acc[i.type] = (acc[i.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byImpact: insights.reduce((acc, i) => {
        acc[i.impact] = (acc[i.impact] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      insights: insights.slice(0, 100) // Limitar a 100 insights
    };
    
    res.json({
      success: true,
      data: report
    });
  } catch (error) {
    console.error('Error fetching insights report:', error);
    res.status(500).json({ error: 'Failed to fetch insights report' });
  }
});

export default router;






